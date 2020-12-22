#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import sys
import os
import re
from pathlib import Path

from mathicsscript.termshell import (
    TerminalShell,
    wl_replace_dict_esc,
    wl_replace_pattern,
)

from mathicsscript.format import format_output

from mathics.core.parser import FileLineFeeder
from mathics.core.definitions import Definitions
from mathics.core.expression import Symbol
from mathics.core.evaluation import Evaluation, Output
from mathics.core.expression import from_python
from mathics import version_string, license_string
from mathics import settings

from pygments import highlight
from pygments.lexers import MathematicaLexer

mma_lexer = MathematicaLexer()

from mathicsscript.version import __version__


def replace_wl_to_unicode(wl_input: str) -> str:
    """WL uses some non-unicode character for various things.
    Replace them with the unicode equivalent.
    Two known items are directed arrow and undirected arrow.
    """
    return wl_replace_pattern.sub(
        lambda m: wl_replace_dict_esc[re.escape(m.group(0))], wl_input
    )


def ensure_settings():
    home = Path.home()
    base_config_dir = home / ".config"
    if not base_config_dir.is_dir():
        os.mkdir(str(base_config_dir))
    config_dir = base_config_dir / "mathicsscript"
    if not config_dir.is_dir():
        os.mkdir(str(config_dir))

    settings_file = config_dir / "settings.m"
    if not settings_file.is_file():
        import mathicsscript

        srcfn = Path(mathicsscript.__file__).parent / "settings.m"
        try:
            with open(srcfn, "r") as src:
                buffer = src.readlines()
        except:
            print(f"'{srcfn}' was not found.")
            return ""
        try:
            with open(settings_file, "w") as dst:
                for l in buffer:
                    dst.write(l)
        except:
            print(f" '{settings_file}'  cannot be written.")
            return ""
    return settings_file


def load_settings(shell):
    settings_file = ensure_settings()
    if settings_file == "":
        return
    with open(settings_file, "r") as src:
        feeder = FileLineFeeder(src)
        try:
            while not feeder.empty():
                evaluation = Evaluation(
                    shell.definitions,
                    output=TerminalOutput(shell),
                    catch_interrupt=False,
                    format="text",
                )
                query = evaluation.parse_feeder(feeder)
                if query is None:
                    continue
                evaluation.evaluate(query)
        except (KeyboardInterrupt):
            print("\nKeyboardInterrupt")
    return True


Evaluation.format_output = format_output


class TerminalOutput(Output):
    def max_stored_size(self, settings):
        return None

    def __init__(self, shell):
        self.shell = shell

    def out(self, out):
        return self.shell.out_callback(out)


@click.command()
@click.version_option(version=__version__)
@click.option(
    "--full-form",
    "-f",
    "full_form",
    flag_value="full_form",
    default=False,
    required=False,
    help="Show how input was parsed to FullForm",
)
@click.option(
    "--persist",
    default=False,
    required=False,
    is_flag=True,
    help="go to interactive shell after evaluating FILE or -e",
)
@click.option(
    "--quiet",
    "-q",
    default=False,
    is_flag=True,
    required=False,
    help="don't print message at startup",
)
@click.option(
    "--readline/--no-readline",
    default=True,
    help="GNU Readline line editing. If this is off completion and command history are also turned off",
)
@click.option(
    "--completion/--no-completion",
    default=True,
    help="GNU Readline line editing. enable tab completion",
)
@click.option(
    "--unicode/--no-unicode",
    default=True,
    help="GNU Readline line editing. If this is off completion and command history are also turned off",
)
@click.option(
    "--pyextensions",
    "-l",
    required=False,
    multiple=True,
    help="directory to load extensions in Python",
)
@click.option(
    "-e",
    "--execute",
    help="evaluate EXPR before processing any input files (may be given "
    "multiple times)",
    multiple=True,
    required=False,
)
@click.option(
    "--initfile",
    type=click.Path(readable=True),
    help=(
        "go to interactive shell after evaluating INITFILE but leave "
        "history empty and set $Line to 1"
    ),
)
@click.option(
    "-s",
    "--style",
    metavar="PYGMENTS-STYLE",
    type=str,
    help=("Set pygments style. Use 'None' if you do not want any pygments styling."),
    required=False,
)
@click.option(
    "--pygments-tokens/--no-pygments-tokens",
    default=False,
    help=("Show pygments tokenization of output."),
    required=False,
)
@click.argument("file", nargs=1, type=click.Path(readable=True), required=False)
def main(
    full_form,
    persist,
    quiet,
    readline,
    completion,
    unicode,
    pyextensions,
    execute,
    initfile,
    style,
    pygments_tokens,
    file,
) -> int:
    """A command-line interface to Mathics.

    Mathics is a general-purpose computer algebra system
    """

    exit_rc = 0
    quit_command = "CTRL-BREAK" if sys.platform == "win32" else "CONTROL-D"

    extension_modules = []
    if pyextensions:
        for ext in pyextensions:
            extension_modules.append(ext)

    definitions = Definitions(add_builtin=True)
    definitions.set_line_no(0)
    # Set a default value for $ShowFullFormInput to False.
    # Then, it can be changed by the settings file (in WL)
    # and overwritten by the command line parameter.
    definitions.set_ownvalue(
        "Settings`$ShowFullFormInput", from_python(True if full_form else False)
    )
    definitions.set_ownvalue(
        "Settings`$PygmentsShowTokens", from_python(True if pygments_tokens else False)
    )

    shell = TerminalShell(definitions, style, readline, completion, unicode)
    load_settings(shell)
    if initfile:
        with open(initfile, "r") as ifile:
            feeder = FileLineFeeder(ifile)
            try:
                while not feeder.empty():
                    evaluation = Evaluation(
                        shell.definitions,
                        output=TerminalOutput(shell),
                        catch_interrupt=False,
                        format="text",
                    )
                    query = evaluation.parse_feeder(feeder)
                    if query is None:
                        continue
                    evaluation.evaluate(query, timeout=settings.TIMEOUT)
            except (KeyboardInterrupt):
                print("\nKeyboardInterrupt")

        definitions.set_line_no(0)

    if execute:
        for expr in execute:
            print(shell.get_in_prompt() + expr)
            evaluation = Evaluation(
                shell.definitions, output=TerminalOutput(shell), format="text"
            )
            result = evaluation.parse_evaluate(expr, timeout=settings.TIMEOUT)
            shell.print_result(result)

            # After the next release, we can remove the hasattr test.
            if hasattr(evaluation, "exc_result"):
                if evaluation.exc_result == Symbol("Null"):
                    exit_rc = 0
                elif evaluation.exc_result == Symbol("$Aborted"):
                    exit_rc = -1
                elif evaluation.exc_result == Symbol("Overflow"):
                    exit_rc = -2
                else:
                    exit_rc = -3

        if not persist:
            return exit_rc

    if file is not None:
        feeder = FileLineFeeder(file)
        try:
            while not feeder.empty():
                evaluation = Evaluation(
                    shell.definitions,
                    output=TerminalOutput(shell),
                    catch_interrupt=False,
                    format="text",
                )
                query = evaluation.parse_feeder(feeder)
                if query is None:
                    continue
                evaluation.evaluate(query, timeout=settings.TIMEOUT)
        except (KeyboardInterrupt):
            print("\nKeyboardInterrupt")

        if not persist:
            return exit_rc

    if not quiet:
        print()
        print(version_string + "\n")
        print(license_string + "\n")
        print(f"Quit by pressing {quit_command}\n")

    # If defined, full_form and style overwrite the predefined values.
    if full_form:
        definitions.set_ownvalue("Settings`$ShowFullFormInput", from_python(full_form))

    definitions.set_ownvalue(
        "Settings`$PygmentsStyle", from_python(shell.pygments_style)
    )
    definitions.set_ownvalue(
        "Settings`$PygmentsShowTokens", from_python(pygments_tokens)
    )

    TeXForm = Symbol("System`TeXForm")

    definitions.set_line_no(0)
    while True:
        try:
            if shell.using_readline:
                import readline as GNU_readline

                last_pos = GNU_readline.get_current_history_length()

            full_form = definitions.get_ownvalue(
                "Settings`$ShowFullFormInput"
            ).replace.get_int_value()
            style = definitions.get_ownvalue("Settings`$PygmentsStyle")
            fmt = lambda x: x
            if style:
                style = style.replace.get_string_value()
                if shell.terminal_formatter:
                    fmt = lambda x: highlight(
                        str(query), mma_lexer, shell.terminal_formatter
                    )

            evaluation = Evaluation(shell.definitions, output=TerminalOutput(shell))
            query, source_code = evaluation.parse_feeder_returning_code(shell)
            if shell.using_readline and hasattr(GNU_readline, "remove_history_item"):
                current_pos = GNU_readline.get_current_history_length()
                for pos in range(last_pos, current_pos - 1):
                    GNU_readline.remove_history_item(pos)
                wl_input = replace_wl_to_unicode(source_code.rstrip())
                GNU_readline.add_history(wl_input)

            if query is None:
                continue

            if hasattr(query, "head") and query.head == TeXForm:
                output_style = "//TeXForm"
            else:
                output_style = ""

            if full_form != 0:
                print(fmt(query))
            result = evaluation.evaluate(
                query, timeout=settings.TIMEOUT, format="unformatted"
            )
            if result is not None:
                shell.print_result(result, output_style)
        except (KeyboardInterrupt):
            print("\nKeyboardInterrupt")
        except EOFError:
            print("\n\nGoodbye!\n")
            break
        except SystemExit:
            print("\n\nGoodbye!\n")
            # raise to pass the error code on, e.g. Quit[1]
            raise
        finally:
            # Reset the input line that would be shown in a parse error.
            # This is not to be confused with the number of complete
            # inputs that have been seen, i.e. In[]
            shell.reset_lineno()
    return exit_rc


if __name__ == "__main__":
    sys.exit(main())
