#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import sys

from tmathics.termshell import TerminalShell

from mathics.core.definitions import Definitions
from mathics.core.evaluation import Evaluation, Output
from mathics import version_string, license_string
from mathics import settings

from pygments import highlight
from pygments.lexers import MathematicaLexer
mma_lexer = MathematicaLexer()

from tmathics.version import VERSION

def format_output(obj, expr, format=None):
    if format is None:
        format = obj.format

    if isinstance(format, dict):
        return dict((k, obj.format_output(expr, f)) for k, f in format.items())

    from mathics.core.expression import Expression, BoxError

    if expr.get_head_name() == "System`MathMLForm":
        format = "xml"
        leaves = expr.get_leaves()
        if len(leaves) == 1:
            expr = leaves[0]
    elif expr.get_head_name() == "System`TeXForm":
        format = "tex"
        leaves = expr.get_leaves()
        if len(leaves) == 1:
            expr = leaves[0]

    if format == 'text':
        result = expr.format(obj, 'System`OutputForm')
    elif format == 'xml':
        result = Expression(
            'StandardForm', expr).format(obj, 'System`MathMLForm')
    elif format == 'tex':
        result = Expression('StandardForm', expr).format(
            obj, 'System`TeXForm')
    else:
        raise ValueError

    try:
        boxes = result.boxes_to_text(evaluation=obj)
    except BoxError:
        boxes = None
        if not hasattr(obj, "seen_box_error"):
            obj.seen_box_error = True
            obj.message('General', 'notboxes',
                         Expression('FullForm', result).evaluate(obj))
    return boxes

Evaluation.format_output = format_output


class TerminalOutput(Output):
    def max_stored_size(self, settings):
        return None

    def __init__(self, shell):
        self.shell = shell

    def out(self, out):
        return self.shell.out_callback(out)


@click.command()
@click.version_option(version=VERSION)
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
    is_flag = True,
    help="go to interactive shell after evaluating FILE or -e",
)
@click.option(
    "--quiet",
    "-q",
    default=False,
    is_flag = True,
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
    "--script", default=True, required=False, help="run a mathics file in script mode"
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
    type=click.Choice(["none", "lightbg", "darkbg", "NoColor"], case_sensitive=False),
    required=False,
)
@click.argument(
    "file",
    nargs=1,
    type=click.Path(readable=True),
    required=False,
)
def main(
    full_form,
    persist,
    quiet,
    readline,
    completion,
    script,
    pyextensions,
    execute,
    initfile,
    style,
    file,
):
    """A command-line interface to Mathics.

    Mathics is a general-purpose computer algebra system
    """

    quit_command = "CTRL-BREAK" if sys.platform == "win32" else "CONTROL-D"

    extension_modules = []
    if pyextensions:
        for ext in pyextensions:
            extension_modules.append(ext)
    else:
        from mathics.settings import default_pymathics_modules

        extension_modules = default_pymathics_modules

    definitions = Definitions(add_builtin=True, extension_modules=extension_modules)
    definitions.set_line_no(0)

    shell = TerminalShell(
        definitions,
        style,
        readline,
        completion,
    )

    if initfile:
        feeder = FileLineFeeder(initfile)
        try:
            while not feeder.empty():
                evaluation = Evaluation(
                    shell.definitions,
                    output=TerminalOutput(shell),
                    catch_interrupt=False,
                    format = "text",
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
            evaluation = Evaluation(shell.definitions,
                                    output=TerminalOutput(shell), format = "text")
            result = evaluation.parse_evaluate(expr, timeout=settings.TIMEOUT)
            shell.print_result(result)

        if not persist:
            return

    if file is not None:
        feeder = FileLineFeeder(file)
        try:
            while not feeder.empty():
                evaluation = Evaluation(
                    shell.definitions,
                    output=TerminalOutput(shell),
                    catch_interrupt=False,
                    format = "text",
                )
                query = evaluation.parse_feeder(feeder)
                if query is None:
                    continue
                evaluation.evaluate(query, timeout=settings.TIMEOUT)
        except (KeyboardInterrupt):
            print("\nKeyboardInterrupt")

        if persist:
            definitions.set_line_no(0)
        else:
            return

    if not quiet:
        print()
        print(version_string + "\n")
        print(license_string + "\n")
        print(f"Quit by pressing {quit_command}\n")

    if style and shell.terminal_formatter:
        fmt = lambda x: highlight(str(query), mma_lexer, shell.terminal_formatter)
    else:
        fmt = lambda x: highlight(str(query), mma_lexer, shell.terminal_formatter)
    while True:
        try:
            evaluation = Evaluation(shell.definitions, output=TerminalOutput(shell))
            query = evaluation.parse_feeder(shell)
            if query is None:
                continue
            if full_form:
                print(fmt(query))
            result = evaluation.evaluate(query, timeout=settings.TIMEOUT)
            if result is not None:
                shell.print_result(result)
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
            shell.reset_lineno()


if __name__ == "__main__":
    main()
