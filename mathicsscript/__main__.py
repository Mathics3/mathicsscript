#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import sys
import os
import os.path as osp
import subprocess
from pathlib import Path

from mathicsscript.termshell import ShellEscapeException, mma_lexer

from mathicsscript.termshell_gnu import TerminalShellGNUReadline
from mathicsscript.termshell_prompt import TerminalShellPromptToolKit

try:
    __import__("readline")
except ImportError:
    have_readline = False
    readline_choices = ["Prompt", "None"]
else:
    readline_choices = ["GNU", "Prompt", "None"]
    have_readline = True

from mathicsscript.format import format_output

from mathics_scanner import replace_wl_with_plain_text
from mathics.core.parser import MathicsFileLineFeeder
from mathics.core.definitions import autoload_files, Definitions
from mathics.core.expression import Symbol, SymbolTrue, SymbolFalse
from mathics.core.evaluation import Evaluation, Output
from mathics.core.expression import from_python
from mathics import version_string, license_string
from mathics import settings

from pygments import highlight


def get_srcdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


from mathicsscript.version import __version__


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

        srcfn = Path(mathicsscript.__file__).parent / "user-settings.m"
        try:
            with open(srcfn, "r") as src:
                buffer = src.readlines()
        except IOError:
            print(f"'{srcfn}' was not found.")
            return ""
        try:
            with open(settings_file, "w") as dst:
                for c in buffer:
                    dst.write(c)
        except IOError:
            print(f" '{settings_file}'  cannot be written.")
            return ""
    return settings_file


def load_settings(shell):
    autoload_files(shell.definitions, get_srcdir(), "autoload")
    settings_file = ensure_settings()
    if settings_file == "":
        return
    with open(settings_file, "r") as src:
        feeder = MathicsFileLineFeeder(src)
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
    "--readline",
    type=click.Choice(readline_choices, case_sensitive=False),
    default="Prompt",
    show_default=True,
    help="""Readline method. "Prompt" is usually best. None is generally available and have the fewest features.""",
)
@click.option(
    "--completion/--no-completion",
    default=True,
    show_default=True,
    help=(
        "GNU Readline line editing. enable tab completion; "
        "you need a working GNU Readline for this option."
    ),
)
@click.option(
    "--unicode/--no-unicode",
    default=sys.getdefaultencoding() == "utf-8",
    show_default=True,
    help="Accept Unicode operators in input and show unicode in output.",
)
@click.option(
    "--prompt/--no-prompt",
    default=True,
    show_default=True,
    help="Do not prompt In[] or Out[].",
)
@click.option(
    "--pyextensions",
    "-l",
    required=False,
    multiple=True,
    help="directory to load extensions in Python",
)
@click.option(
    "-c",
    "-e",
    "--execute",
    help="evaluate EXPR before processing any input files (may be given "
    "multiple times). Sets --quiet and --no-completion",
    multiple=True,
    required=False,
)
@click.option(
    "--run",
    type=click.Path(readable=True),
    help=(
        "go to interactive shell after evaluating PATH but leave "
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
@click.option(
    "--strict-wl-output/--no-strict-wl-output",
    default=False,
    help=("Most WL-output compatible (at the expense of useability)."),
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
    prompt,
    pyextensions,
    execute,
    run,
    style,
    pygments_tokens,
    strict_wl_output,
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

    readline = "none" if (execute or file and not persist) else readline.lower()
    if readline == "prompt":
        shell = TerminalShellPromptToolKit(
            definitions, style, completion, unicode, prompt
        )
    else:
        want_readline = readline == "gnu"
        shell = TerminalShellGNUReadline(
            definitions, style, want_readline, completion, unicode, prompt
        )

    load_settings(shell)
    if run:
        with open(run, "r") as ifile:
            feeder = MathicsFileLineFeeder(ifile)
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
            evaluation = Evaluation(
                shell.definitions, output=TerminalOutput(shell), format="text"
            )
            shell.terminal_formatter = None
            result = evaluation.parse_evaluate(expr, timeout=settings.TIMEOUT)
            shell.print_result(result, prompt, "text", strict_wl_output)

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
        with open(file, "r") as ifile:
            feeder = MathicsFileLineFeeder(ifile)
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

    if not quiet and prompt:
        print(f"\nMathicscript: {__version__}, {version_string}\n")
        print(license_string + "\n")
        print(f"Quit by evaluating Quit[] or by pressing {quit_command}.\n")
    # If defined, full_form and style overwrite the predefined values.
    definitions.set_ownvalue(
        "Settings`$ShowFullFormInput", SymbolTrue if full_form else SymbolFalse
    )

    definitions.set_ownvalue(
        "Settings`$PygmentsStyle", from_python(shell.pygments_style)
    )
    definitions.set_ownvalue(
        "Settings`$PygmentsShowTokens", from_python(pygments_tokens)
    )
    definitions.set_ownvalue("Settings`MathicsScriptVersion", from_python(__version__))
    definitions.set_attribute("Settings`MathicsScriptVersion", "System`Protected")
    definitions.set_attribute("Settings`MathicsScriptVersion", "System`Locked")
    TeXForm = Symbol("System`TeXForm")

    definitions.set_line_no(0)
    while True:
        try:
            if have_readline and shell.using_readline:
                import readline as GNU_readline

                last_pos = GNU_readline.get_current_history_length()

            full_form = definitions.get_ownvalue(
                "Settings`$ShowFullFormInput"
            ).replace.to_python()
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

            if (
                have_readline
                and shell.using_readline
                and hasattr(GNU_readline, "remove_history_item")
            ):
                current_pos = GNU_readline.get_current_history_length()
                for pos in range(last_pos, current_pos - 1):
                    GNU_readline.remove_history_item(pos)
                wl_input = source_code.rstrip()
                if unicode:
                    wl_input = replace_wl_with_plain_text(wl_input)
                GNU_readline.add_history(wl_input)

            if query is None:
                continue

            if hasattr(query, "head") and query.head == TeXForm:
                output_style = "//TeXForm"
            else:
                output_style = ""

            if full_form:
                print(fmt(query))
            result = evaluation.evaluate(
                query, timeout=settings.TIMEOUT, format="unformatted"
            )
            if result is not None:
                shell.print_result(
                    result, prompt, output_style, strict_wl_output=strict_wl_output
                )

        except ShellEscapeException as e:
            source_code = e.line
            if len(source_code) and source_code[1] == "!":
                try:
                    print(open(source_code[2:], "r").read())
                except:
                    print(str(sys.exc_info()[1]))
            else:
                subprocess.run(source_code[1:], shell=True)

                # Should we test exit code for adding to history?
                GNU_readline.add_history(source_code.rstrip())
                # FIXME add this... when in Mathics core updated
                # shell.defintions.increment_line(1)

        except (KeyboardInterrupt):
            print("\nKeyboardInterrupt")
        except EOFError:
            if prompt:
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
