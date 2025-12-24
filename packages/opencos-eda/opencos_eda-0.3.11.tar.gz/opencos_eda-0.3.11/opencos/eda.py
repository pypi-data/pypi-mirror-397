#!/usr/bin/env python3

'''opencos.eda is an executable script (as `eda <command> ...`)

This is the entrypoint for tool discovery, and running targets from command line or DEPS
markup files
'''

import subprocess
import os
import sys
import re
import signal
import argparse
import shlex
import importlib.util

from pathlib import Path

import opencos
from opencos import util, eda_config, eda_base
from opencos.eda_base import Command, Tool, which_tool, print_eda_usage_line
from opencos.files import safe_shutil_which
from opencos.util import safe_emoji, Colors
from opencos.utils import vsim_helper, vscode_helper
from opencos.utils import status_constants, str_helpers, subprocess_helpers

# Configure util:
util.progname = "EDA"
util.global_log.default_log_enabled = True
util.global_log.default_log_filepath = os.path.join('eda.work', 'eda.log')
util.global_log.default_log_disable_with_args.extend([
    # avoid default log on certain eda commands
    'help', 'waves', 'deps-help', 'targets'
])


# ******************************************************************************
# MAIN

# Set config['command_handler'] entries for (command, Class) so we know which
# eda command (such as, command: eda sim) is handled by which class (such as class: CommandSim)
# These are also overriden depending on the tool, for example --tool verilator sets
# "sim": CommandSimVerilator.
def init_config(
        config: dict,  quiet: bool = False, tool=None, command: str = '',
        run_auto_tool_setup: bool = True
) -> dict:
    '''Sets or clears entries in config (dict) so tools can be re-loaded.'''

    # For key DEFAULT_HANDLERS, we'll update config['command_handler'] with
    # the actual class using importlib (via opencos.util)

    eda_config.update_config_auto_tool_order_for_tool(tool=tool, config=config)

    config['command_handler'] = {}
    for _cmd, str_class in config['DEFAULT_HANDLERS'].items():
        cls = util.import_class_from_string(str_class)
        if not cls:
            util.error(f"config DEFAULT_HANDLERS command={_cmd} {str_class=} could not import")
        else:
            config['command_handler'][_cmd] = cls

    config['auto_tools_found'] = {}
    config['tools_loaded'] = set()
    if run_auto_tool_setup:
        config = auto_tool_setup(config=config, quiet=quiet, tool=tool, command=command)
    return config


def get_all_commands_help_str(config: dict) -> str:
    '''Returns a str of help based on what commands eda supports, from config'''
    all_commands_help = []
    max_command_str_len = max(len(s) for s in config.get('DEFAULT_HANDLERS_HELP', {}).keys())
    for key, value in config.get('DEFAULT_HANDLERS_HELP', {}).items():
        all_commands_help.append(f'    {key:<{max_command_str_len}} - {value.strip()}')
    if all_commands_help:
        all_commands_help = [
            f'Where {Colors.byellow}COMMAND{Colors.normal} is one of:',
            '',
        ] + all_commands_help
    return '\n'.join(all_commands_help)


def usage(tokens: list, config: dict, command: str = "", tool: str = "") -> int:
    '''Returns an int shell return code, given remaining args (tokens list) and eda command.

    config is the config dict. Used to check valid commands in config['command_handler']

    Note that we pass the command (str) if possible, so things like:
     > eda help sim --tool verilator
    Will still return this message. This allows args like --config-yml=<file> to work with
    the help message if command is blank, such as:
     > eda --config-yml=<file> help
    '''

    if command == "":
        util.info('Help:', color=Colors.cyan)
        print()
        print_eda_usage_line()
        print(get_all_commands_help_str(config=config))
        print()
        print(str_helpers.indent_wrap_long_text(
            (
                f'{safe_emoji("❕ ")}where {Colors.byellow}FILES|TARGETS{Colors.normal}'
                ' is one or more source file or DEPS markup file target,'
                ' such as .v, .sv, .vhd[l], .cpp files, or a target key in a'
                f' {Colors.byellow}DEPS.[yml|yaml|toml|json]{Colors.normal}. Note that you can'
                f' prefix source files with {Colors.bcyan}sv@{Colors.normal},'
                f' {Colors.bcyan}v@{Colors.normal}, {Colors.bcyan}vhdl@{Colors.normal},'
                f' or {Colors.bcyan}cpp@{Colors.normal}'
                ' to force use that file as systemverilog, verilog, vhdl, or C++, respectively.'
            ), width=str_helpers.get_terminal_columns(), indent=4
        ))
        print()
        eda_base.print_base_help()
        return 0

    if command in config['command_handler'].keys():
        sco = config['command_handler'][command](config=config) # sub command object
        sco_tool = getattr(sco, '_TOOL', '')
        if tool and tool != sco_tool:
            util.warning(f'{tool=} does not support {command=}')
        sco.help(tokens=tokens)
        return util.exit(0)

    util.info("Valid commands are:")
    for k in sorted(config['command_handler'].keys()):
        util.info(f"   {k:20}")
    return util.error(f"Cannot provide help, don't understand command: '{command}'")


def interactive(config: dict) -> int:
    '''Returns bash/sh return code, entry point for running interactively in CLI if

    args are not present to directly call a command handler, --help, etc
    '''
    rc = 0
    while True:
        try:
            line = input('EDA->')
        except EOFError:
            util.info('End of input reached unexpectedly, exiting')
            return 0
        m = re.match(r'^([^\#]*)\#.*$', line)
        if m:
            line = m.group(1)
        tokens = line.split()
        original_args = tokens.copy()
        # NOTE: interactive will not correctly handle --config-yml arg (from eda_config.py),
        # but we should do a best effor to re-parse args from util.py, such as
        # --quiet, --color, --fancy, --logfile, --debug or --debug-level, etc
        _, tokens = util.process_tokens(tokens)
        rc = process_tokens(
            tokens=tokens, original_args=original_args, config=config, is_interactive=True
        )
    return rc


def auto_tool_setup( # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        warnings: bool = True, config = None, quiet: bool = False, tool: str = '',
        command: str = ''
) -> dict:
    '''Returns an updated config, uses config['auto_tools_order'][0] dict, calls tool_setup(..)

    -- adds items to config['tools_loaded'] set
    -- updates config['command_handler'][command] with a Tool class

    Input arg tool can be in the form (for example):
      tool='verlator', tool='verilator=/path/to/verilator.exe'
      If so, updates config['auto_tools_order'][tool]['exe']
    '''

    tool = eda_config.tool_arg_remove_path_information(tool)

    assert 'auto_tools_order' in config
    assert isinstance(config['auto_tools_order'], list)
    assert isinstance(config['auto_tools_order'][0], dict)

    if command:
        util.info(f'Auto tool setup for command: {Colors.byellow}{command}')

    for name, value in config['auto_tools_order'][0].items():
        if tool and tool != name:
            # if called with tool=(some_name), then only load that tool (which is not
            # this one)
            continue

        if command and command not in value.get('handlers', {}) and \
           command not in config.get('command_has_subcommands', []):
            # Skip tool_setup(..) if the tool handlers can't support command,
            # this is a time-saving feature, but if the comman is multi, tools-multi,
            # sweep, then don't skip this (we don't know what tools we need so load them
            # all.
            # We could figure this out if we went looking for all command(s)
            # multi + sub-command, but that's slightly dangerous if we grab a 'command'
            # from another arg.
            util.debug(f"Skipping tool {name} because it cannot handle {command=}")
            continue

        util.debug(f"Checking for ability to run tool: {name}")
        exe = value.get('exe', str())
        if isinstance(exe, list):
            exe_list = exe
        elif isinstance(exe, str):
            exe_list = [exe] # make it a list
        else:
            util.error(f'eda.py: config["auto_tools_order"][0] for {name=} {value=} has bad type'
                       f'for {exe=}')
            continue

        has_all_py = True
        requires_py_list = value.get('requires_py', [])
        for pkg in requires_py_list:
            spec = importlib.util.find_spec(pkg)
            if not spec:
                has_all_py = False
                util.debug(f"... No, missing pkg {spec}")

        has_all_env = True
        requires_env_list = value.get('requires_env', [])
        for env in requires_env_list:
            if not os.environ.get(env, ''):
                has_all_env = False
                util.debug(f"... No, missing env {env}")

        has_all_exe = True
        has_all_in_exe_path = True
        exe_path = None
        for exe in exe_list:
            assert exe != '', f'{name=} {value=} value missing "exe" {exe=}'
            p = safe_shutil_which(exe)
            if not exe_path:
                exe_path = p # set on first required exe
            if not p:
                has_all_exe = False
                util.debug(f"... No, missing exe {exe}")
            for req in value.get('requires_in_exe_path', []):
                if p and req and str(Path(req)) not in str(Path(p)):
                    has_all_in_exe_path = False
                    util.debug(f"... No, missing path requirement {req}")

        has_vsim_helper = True
        if value.get('requires_vsim_helper', False):
            # This tool name must be in opencos.utils.vsim_helper.TOOL_PATH[name].
            # Special case for vsim being used by a lot of tools.
            vsim_helper.init() # only runs checks once internally
            exe_path = vsim_helper.TOOL_PATH[name]
            has_vsim_helper = bool(exe_path)

        has_vscode_helper = True
        needs_vscode_extensions = value.get('requires_vscode_extension', None)
        if needs_vscode_extensions:
            if not isinstance(needs_vscode_extensions, list):
                util.error(
                    f'eda config issue, tool {name}: requires_vscode_extension must be a list'
                )
            else:
                vscode_helper.init() # only runs checks once internally
                has_vscode_helper = all(
                    x in vscode_helper.EXTENSIONS for x in needs_vscode_extensions
                )

        if has_all_exe:
            requires_cmd_list = value.get('requires_cmd', [])
            for cmd in requires_cmd_list:
                cmd_list = shlex.split(cmd)
                try:
                    proc = subprocess.run(cmd_list, capture_output=True, check=False,
                                          input=b'exit\n\n')
                    if proc.returncode != 0:
                        if not quiet:
                            util.debug(f"For tool {name} missing required command",
                                       f"({proc.returncode=}): {cmd_list=}")
                        has_all_exe = False
                except Exception as e:
                    has_all_exe = False
                    util.debug(f"... No, exception {e} running {cmd_list}")


        if all((has_all_py, has_all_env, has_all_exe, has_all_in_exe_path,
                has_vsim_helper, has_vscode_helper)):
            if exe_path:
                p = exe_path
            else:
                p = safe_shutil_which(exe_list[0])
            config['auto_tools_found'][name] = p # populate key-value pairs w/ first exe in list
            if not quiet:
                util.info(f"Detected {name} ({p})")
            tool_setup(
                tool=name, quiet=True, auto_setup=(not tool), warnings=warnings, config=config
            )
        else:
            util.debug(f'Tool {name} is missing one of: {has_all_py=} {has_all_env=}',
                       f'{has_all_exe=} {has_all_in_exe_path=} {has_vsim_helper=}',
                       f'{has_vscode_helper=}')

    return config


def tool_setup( # pylint: disable=too-many-branches
        tool: str, config: dict, quiet: bool = False, auto_setup: bool = False,
        warnings: bool = True
):
    ''' Adds items to config["tools_loaded"] (set) and updates config['command_handler'].

    config is potentially updated for entry ['command_handler'][command] with a Tool class.

    Input arg tool can be in the form (for example):
      tool='verlator', tool='verilator=/path/to/verilator.exe'

    '''

    tool = eda_config.tool_arg_remove_path_information(tool)

    if not quiet and not auto_setup:
        util.info(f"Setup for tool: '{tool}'")

    if not tool:
        return

    if tool not in config['auto_tools_order'][0]:
        tools = list(config.get('auto_tools_order', [{}])[0].keys())
        cfg_yaml_fname = config.get('config-yml', None)
        util.warning(f'Unknown tool: {tool}')
        if tools:
            util.info('Known tools:')
            pretty_tools = str_helpers.pretty_list_columns_manual(data=tools)
            for row in pretty_tools:
                if row:
                    util.info(row)
        util.error(f"Don't know how to run tool_setup({tool=}), is not in",
                   f"config['auto_tools_order'] from {cfg_yaml_fname}")
        return

    if tool not in config['auto_tools_found']:
        cfg_yaml_fname = config.get('config-yml', None)
        util.error(f"Don't know how to run tool_setup({tool=}), is not in",
                   f"{config['auto_tools_found']=} from {cfg_yaml_fname}")
        return

    if auto_setup and tool is not None and tool in config['tools_loaded']:
        # Do I realy need to warn if a tool was loaded from auto_tool_setup(),
        # but then I also called it via --tool verilator? Only warn if auto_setup=True:
        if warnings:
            util.warning(f"tool_setup: {auto_setup=} already setup for {tool}?")

    entry = config['auto_tools_order'][0].get(tool, {})
    tool_cmd_handler_dict = entry.get('handlers', {})

    for command, str_class_name in tool_cmd_handler_dict.items():
        current_handler_cls = config['command_handler'].get(command, None)

        if auto_setup and current_handler_cls is not None and issubclass(current_handler_cls, Tool):
            # If we're not in auto_setup, then always override (aka arg --tool=<this tool>)
            # skip, already has a tool associated with it, and we're in auto_setup=True
            continue

        cls = util.import_class_from_string(str_class_name)

        if command in config.get('command_determines_tool', []) + \
           config.get('command_tool_is_optional', []):
            # we don't need to confirm the handler parent is a Tool class.
            pass
        else:
            assert issubclass(cls, Tool), \
                f'{str_class_name=} is does not have Tool class associated with it'

        if not auto_setup or \
           command not in config.get('command_determines_tool', []):
            # If not auto_setup - then someone called this --tool by name on the command line,
            # then update the command handler
            # otherwise, if --tool was not set, and command determines tool, leave it with
            # the default handler.
            util.debug(f'Setting {cls=} for {command=} in config.command_handler')
            config['command_handler'][command] = cls

    config['tools_loaded'].add(tool)


def process_tokens( # pylint: disable=too-many-branches,too-many-statements,too-many-locals,too-many-return-statements
        tokens: list, original_args: list, config: dict, is_interactive=False
) -> int:
    '''Returns bash/sh style return code int (0 pass, non-zero fail).

    This is the top level token processing function, and entry point (after util and eda_config
    have performed their argparsing). Tokens can come from command line, DEPS target markup file,
    or interactively. We do one pass through all the tokens, triaging them into:
     - those we can execute immediate (help, quit, and global opens like --debug, --color)
        -- some of this has already been performed in main() by util for --color.
    - a command (sim, synth, etc)
    - command arguments (--seed, +define, +incdir, etc) which will be deferred and processed by
      the command. Some are processed here (--tool)
    '''

    deferred_tokens = []
    command = ""
    run_auto_tool_setup = True

    parser = eda_base.get_argparser()
    try:
        parsed, unparsed = parser.parse_known_args(tokens + [''])
        unparsed = list(filter(None, unparsed))
    except argparse.ArgumentError:
        return util.error(f'problem attempting to parse_known_args for {tokens=}')

    config['tool'] = parsed.tool

    # We support a few way of handling quit, exit, or --quit, --exit, -q
    if parsed.quit or parsed.exit or 'exit' in unparsed or 'quit' in unparsed:
        return util.exit(0)
    if parsed.help or 'help' in unparsed:
        if 'help' in unparsed:
            # We'll figure out the command first before applying help, so
            # usage(tokens, config, command) doesn't have a custom argparser guessing.
            unparsed.remove('help')
            parsed.help = True
    if parsed.eda_safe:
        eda_config.update_config_for_eda_safe(config)

    util.debug(f'eda process_tokens: {parsed=} {unparsed=}')

    # Attempt to get the 'command' in the unparsed args before we've even
    # set the command handlers (some commands don't use tools).
    # Note that we only grab the first command, and for multi, tools-multi,
    # or sweep we do NOT get the subcommand.
    for value in unparsed:
        if value in config['DEFAULT_HANDLERS'].keys():
            command = value
            if not parsed.tool and value in config['command_tool_is_optional']:
                # only do this if --tool was not set.
                run_auto_tool_setup = False
            unparsed.remove(value) # remove command (flist, export, targets, etc)
            break

    if not is_interactive:
        # Run init_config() now, we deferred it in main(), but only run it
        # for this tool (or tool=None to figure it out)
        # This will handle any --tool=<name>=/path/to/bin also, so don't have to
        # run tool_setup(..) on its own.
        config = init_config(
            config, tool=parsed.tool, command=command,
            run_auto_tool_setup=run_auto_tool_setup
        )
        if not config:
            util.error(f'eda.py main: problem loading config, {tokens=}')
            return 3

    # Deal with help, now that we have the command (if it was set).
    if parsed.help:
        if not command:
            # if we didn't find the command in config['command_handler'], and
            # since we're entering help anyway (will exit) set command to the
            # first unparsed word looking arg:
            for arg in unparsed:
                if not arg.startswith('-'):
                    command = arg
        return usage(tokens=unparsed, config=config, command=command, tool=parsed.tool)

    deferred_tokens = unparsed
    if not command:
        util.error("'eda' didn't get a command, or command is invalid (run with --help to see",
                   "valid commands)!")
        return 2

    sco = config['command_handler'][command](config=config) # sub command object
    if not parsed.tool:
        # then what was the auto selected tool?
        sco_tool = getattr(sco, '_TOOL', '')
        if sco_tool in config['auto_tools_order'][0] and \
           config['auto_tools_order'][0][sco_tool].get('disable-auto', False):
            util.error(f'Cannot use tool={sco_tool} without arg --tool, it cannot be selected',
                       'automatically')
            return status_constants.EDA_COMMAND_OR_ARGS_ERROR

    util.debug(f'{command=}')
    util.debug(f'{sco.config=}')
    util.debug(f'{type(sco)=}')
    if not parsed.tool and \
       command not in config.get('command_determines_tool', []) and \
       command not in config.get('command_tool_is_optional', []):
        use_tool = which_tool(command, config)
        if use_tool:
            util.info(f"--tool not specified, using default for {command=}: {use_tool}")
        else:
            # Not all commands have a hard requirement on tool (such as 'multi') because we
            # haven't examined sub-commands yet.
            util.info(f'--tool not specified, will attempt to determine tool(s) for {command=}.')
        setattr(sco, 'auto_tool_applied', True)

    rc = check_command_handler_cls(command_obj=sco, command=command, parsed_args=parsed)
    if rc > 0:
        util.debug(f'Return from main process_tokens({tokens=}), {rc=}, {type(sco)=},'
                   f'unparsed={deferred_tokens}')
        return rc

    # Add the original, nothing-parsed args to the Command.config dict.
    sco.config['eda_original_args'] = original_args

    setattr(sco, 'command_name', command) # as a safeguard, 'command' is not always passed to 'sco'
    unparsed = sco.process_tokens(tokens=deferred_tokens, pwd=os.getcwd())

    # query the status from the Command object (0 is pass, > 0 is fail, but we'd prefer to avoid
    # rc=1 because that's the python exception rc)
    rc = getattr(sco, 'status', 2)
    util.debug(f'Return from main process_tokens({tokens=}), {rc=}, {type(sco)=}, {unparsed=}')

    if rc == 0 and not parsed.tool and getattr(sco, 'tool_changed_respawn', False):
        return respawn_new_sub_command_object(
            sco=sco, parsed=parsed, config=config, command=command, tokens=tokens,
            deferred_tokens=deferred_tokens
        )

    return rc


def respawn_new_sub_command_object(
        sco: Command, parsed: argparse.Namespace, config: dict, command: str,
        tokens: list, deferred_tokens: list
) -> int:
    '''Returns retcode (int). Creates a new Command object, presumably using a different tool,

    due to args changes from DEPS parsing that led to --tool=<different value> vs the automatic
    value if --tool was not originally set. Will run process_tokens(..) on the new sub commmand
    object.
    '''

    use_tool = sco.args.get('tool', '')

    if not use_tool:
        util.error(f'Unable to change tool from {parsed.tool}, internal eda problem.')
        return status_constants.EDA_DEFAULT_ERROR

    util.info(f'Changing {Colors.bcyan}--tool{Colors.normal}{Colors.green} --->',
              f'{Colors.bcyan}{use_tool}{Colors.normal}{Colors.green} for command:',
              f'{Colors.byellow}{command}')

    # Update the command handler(s) with this new tool. We don't really respawn, just
    # try to swap out the sco (Command obj handle)
    entry = config['auto_tools_order'][0].get(use_tool, {})
    tool_cmd_handler_dict = entry.get('handlers', {})

    for _command, str_class_name in tool_cmd_handler_dict.items():
        if _command and command and _command != command:
            # This isn't the command we care about (it's just one of the commands
            # this tool supports, so don't bother loading a handler for it:
            continue

        cls = util.import_class_from_string(str_class_name)
        if _command in config.get('command_determines_tool', []) + \
           config.get('command_tool_is_optional', []):
            # we don't need to confirm the handler parent is a Tool class.
            pass
        else:
            assert issubclass(cls, Tool), \
                f'command {_command} {str_class_name=} does not have Tool class associated with it'

        util.debug(f'Setting {cls=} for command={_command} in config.command_handler')
        config['command_handler'][_command] = cls

    old_sco = sco
    sco = config['command_handler'][command](config=config) # sub command object
    util.debug(f'No longer using handler: {type(old_sco)}; now using: {type(sco)}')
    sco.config['eda_original_args'] = old_sco.config['eda_original_args']
    del old_sco

    rc = check_command_handler_cls(command_obj=sco, command=command, parsed_args=parsed)
    if rc > 0:
        util.debug(f'Return from main process_tokens({tokens=}), {rc=}, {type(sco)=},'
                   f'unparsed={deferred_tokens}')
        return rc

    setattr(sco, 'command_name', command) # as a safeguard, 'command' set in 'sco'
    util.info(f'--tool={use_tool}: running command: {Colors.byellow}eda {command} ',
              ' '.join(deferred_tokens))
    unparsed = sco.process_tokens(tokens=deferred_tokens, pwd=os.getcwd())

    # query the status from the Command object (0 is pass, > 0 is fail, but we'd prefer to
    # avoid rc=1 because that's the python exception rc)
    rc = getattr(sco, 'status', 2)
    util.debug(f'Return from main process_tokens({tokens=}), {rc=}, {type(sco)=}, {unparsed=}')
    return rc


def check_command_handler_cls(command_obj:object, command:str, parsed_args) -> int:
    '''Returns bash/sh return code, checks that a command handling class has all

    internal CHECK_REQUIRES list items. For example, sim.py has CHECK_REQUIRES=[Tool],
    so if a 'sim' command handler does not also inherit a Tool class, then reports this as an
    error.
    '''
    sco = command_obj
    for cls in getattr(sco, 'CHECK_REQUIRES', []):
        if not isinstance(sco, cls):
            # If someone set --tool verilator for command=synth, then our 'sco' will have defaulted
            # to CommandSynth with no tool attached. If we don't have a tool set, error and return.
            parsed_tool =  getattr(parsed_args, 'tool', '')
            auto_tool_entry = command_obj.config.get(
                'auto_tools_order', [{}])[0].get(parsed_tool, {})
            if parsed_tool and not auto_tool_entry:
                util.warning(
                    f"{command=} for tool '{parsed_tool}' is using handling class '{type(sco)}',",
                    f"but missing requirement {cls}, likely because the tool was not loaded",
                    "(not in PATH) or mis-configured (such as missing a Tool based class)"
                )
                return util.error(
                    f"EDA {command=} for tool '{parsed_tool}' cannot be run because tool",
                    f"'{parsed_tool}' is not known to `eda`. It does not exist in the config:",
                    "see informational message for --config-yml, and check that file's",
                    "auto_tools_order."
                )
            if parsed_tool:
                util.warning(
                    f"{command=} for tool '{parsed_tool}' is using handling class '{type(sco)}',",
                    f"but missing requirement {cls}, likely because the tool was not loaded",
                    "(not in PATH) or mis-configured (such as missing a Tool based class)"
                )
                for k,v in auto_tool_entry.items():
                    if k == 'exe' or k.startswith('requires_cmd'):
                        util.warning(
                            f"tool '{parsed_tool}' has requirements that may not have been met --",
                            f"{k}: {v} (Perhaps not in PATH?)"
                        )
                    if k == 'requires_vsim_helper':
                        if found_tool := vsim_helper.found():
                            util.warning(
                                f"tool '{parsed_tool}' was not found, vsim appears to be for tool",
                                f"'{found_tool}'"
                            )

                return util.error(
                    f"EDA {command=} for tool '{parsed_tool}' is not supported (tool",
                    f"'{parsed_tool}' cannot run {command=}). It is likely that tool",
                    f"'{parsed_tool}' is not in PATH, or was unable to be loaded due to missing",
                    "requirements, or missing information when checking the exe version."
                )

            # No parsed_tool.
            util.warning(
                f"{command=} for default tool (--tool not set) is using handling class",
                f"'{type(sco)}', but missing requirement {cls}, likely because the tool was not",
                "loaded (not in PATH) or mis-configured (such as missing a Tool based class)"
            )
            return util.error(
                f"EDA {command=} for default tool (--tool not set) is not supported (default",
                f"tool cannot run {command=}). It appears that no suitable default tool to run",
                f"{command=} was automatically found, was not in PATH, or was unable to be loaded",
                "due to missing requirements, or missing information when checking the exe version."
            )

    return 0


# **************************************************************
# **** Interrupt Handler

def signal_handler(sig, frame) -> None: # pylint: disable=unused-argument
    '''Handles Ctrl-C, called by main_cli() if running from command line'''
    util.fancy_stop()
    util.error(f'{safe_emoji("❌ ")}Received Ctrl+C...', start='\nINFO: [EDA] ')
    subprocess_helpers.cleanup_all()
    util.exit(-1)

# **************************************************************
# **** Startup Code


def main(*args):
    ''' Returns return code (int), entry point for calling eda.main(*list) directly in py code'''

    args = list(args)
    if len(args) == 0:
        # If not one passed args, then use sys.argv:
        args = sys.argv[1:]

    original_args = args.copy() # save before any parsing.

    # Set global --debug, --quiet, --color, -f/--iput-file, --envfile
    # early before parsing other args:
    util_parsed, unparsed = util.process_tokens(args)

    util.debug(f"main: file: {os.path.realpath(__file__)}")
    util.debug(f"main: args: {args=}")

    if util_parsed.version:
        # Do not consider parsed.quiet, print the version and exit:
        print(f'eda {opencos.__version__} ({opencos.__pyproject_name__})')
        sys.exit(0)

    if not util.args['quiet']:
        util.info(f'eda: version {opencos.__version__}', color=Colors.bcyan)
        # And show the command that was run (all args):
        util.info(f"main: {Colors.byellow}eda {' '.join(args)}{Colors.normal}{Colors.green};",
                  f"(run from {os.getcwd()})")

    # Handle --config-yml= arg
    config, unparsed = eda_config.get_eda_config(unparsed)

    # Note - we used to call: config = init_config(config=config)
    # However, we now defer calling init_config(..) until eda.process_tokens(..)

    util.info("*** OpenCOS EDA ***", color=Colors.bcyan)

    if len(args) == 0 or (len(args) == 1 and '--debug' in args):
        # special snowflake case if someone called with a singular arg --debug
        # (without --help or exit)
        util.debug("Starting automatic tool setup: init_config()")
        config = init_config(config=config)
        if not config:
            util.error(f'eda.py main: problem loading config, {args=}')
            return 3
        main_ret = interactive(config=config)
    else:
        main_ret =  process_tokens(
            tokens=list(unparsed), original_args=original_args, config=config
        )
    # Stop the util log, needed for pytests that call eda.main directly that otherwise
    # won't close the log file via util's atexist.register(stop_log)
    util.global_log.stop()
    return main_ret

def main_show_autocomplete_instructions() -> None:
    ''' Executable script entry point - eda_show_autocomplete

    from pyproject.toml::project.scripts. Shows instructions on how to enable bash autocomplete
    '''
    source_filepath = opencos.__file__.replace(
        '__init__.py', 'eda_deps_bash_completion.bash'
    )
    if os.path.exists(source_filepath):
        print(
            f"{Colors.yellow}To enable bash autocompletion with"
            f" {Colors.bold}eda{Colors.normal}{Colors.yellow} script (uv not equired):"
        )
        print(f"{Colors.normal}")
        print(f"    source {source_filepath}")
        print("")
        print(f"{Colors.yellow}Feel free to inspect this script prior to sourcing.")
        print(f"{Colors.normal}")
        sys.exit(0)
    else:
        util.error(f"It appears the following file(s) doe not exist: {source_filepath}")
        sys.exit(1)


def main_cli() -> None:
    ''' Executable script entry point - eda

    from pyproject.tom::project.scripts, or from __main__.
    Returns None, will exit with return code.
    '''
    signal.signal(signal.SIGINT, signal_handler)
    util.global_exit_allowed = True
    # Strip eda or eda.py from sys.argv, we know who we are if called from __main__:
    rc = main()
    subprocess_helpers.cleanup_all()
    util.exit(rc)


if __name__ == '__main__':
    main_cli()
