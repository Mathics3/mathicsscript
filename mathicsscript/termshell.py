# -*- coding: utf-8 -*-
#   Copyright (C) 2020 Rocky Bernstein <rb@dustyfeet.com>

import atexit
import os
import os.path as osp
import locale
import pathlib
import sys
import re
from columnize import columnize
from mathics_scanner import replace_unicode_with_wl, named_characters
from mathics.core.expression import Expression, String, Symbol
from mathics.core.expression import strip_context, from_python
from mathics.core.rules import Rule

from pygments import highlight, lex
from mathicsscript.mmalexer import MathematicaLexer

mma_lexer = MathematicaLexer()

from pygments.formatters.terminal import TERMINAL_COLORS
from pygments.formatters import Terminal256Formatter
from pygments.styles import get_all_styles
from pygments.util import ClassNotFound

from pygments.token import (
    # Comment,
    # Generic,
    # Keyword,
    Name,
    Literal,
    Operator,
    # String,
    Token,
)

ALL_PYGMENTS_STYLES = list(get_all_styles())

color_scheme = TERMINAL_COLORS.copy()
color_scheme[Token.Name] = ("yellow", "ansibrightyellow")
color_scheme[Name.Function] = ("ansigreen", "ansibrightgreen")
color_scheme[Operator] = ("magenta", "ansibrightmagenta")
color_scheme[Literal.Number] = ("ansiblue", "ansibrightblue")

from colorama import init as colorama_init

## FIXME: __main__ shouldn't be needed. Fix term_background
from term_background.__main__ import is_dark_background

from readline import (
    parse_and_bind,
    read_history_file,
    read_init_file,
    set_completer,
    set_completer_delims,
    set_history_length,
    write_history_file,
)

# Set up mathicsscript configuration directory
CONFIGHOME = os.environ.get("XDG_CONFIG_HOME", osp.expanduser("~/.config"))
CONFIGDIR = os.path.join(CONFIGHOME, "mathicsscript")
os.makedirs(CONFIGDIR, exist_ok=True)

try:
    HISTSIZE = int(os.environ.get("MATHICSSCRIPT_HISTSIZE"))
except:
    HISTSIZE = 50

HISTFILE = os.path.join(CONFIGDIR, "history")

# Create HISTFILE if it doesn't exist already
if not os.path.isfile(HISTFILE):
    pathlib.Path(HISTFILE).touch()

RL_COMPLETER_DELIMS_WITH_BRACE = " \t\n_~!@#%^&*()-=+{]}|;:'\",<>/?"
RL_COMPLETER_DELIMS = " \t\n_~!@#%^&*()-=+[{]}\\|;:'\",<>/?"


from mathics.core.parser import MathicsLineFeeder


def is_pygments_style(style):
    if style not in ALL_PYGMENTS_STYLES:
        print("Pygments style name '%s' not found." % style)
        print("Style names are:\n%s" % columnize(ALL_PYGMENTS_STYLES))
        return False
    return True


class ShellEscapeException(Exception):
    def __init__(self, line):
        self.line = line


class TerminalShell(MathicsLineFeeder):
    def __init__(
        self,
        definitions,
        style: str,
        want_readline: bool,
        want_completion: bool,
        use_unicode: bool,
    ):
        super(TerminalShell, self).__init__("<stdin>")
        self.input_encoding = locale.getpreferredencoding()
        self.lineno = 0
        self.terminal_formatter = None
        self.history_length = definitions.get_config_value("$HistoryLength", HISTSIZE)

        # Try importing readline to enable arrow keys support etc.
        self.using_readline = False
        try:
            if want_readline:

                self.using_readline = sys.stdin.isatty() and sys.stdout.isatty()
                self.ansi_color_re = re.compile("\033\\[[0-9;]+m")
                if want_completion:
                    set_completer(
                        lambda text, state: self.complete_symbol_name(text, state)
                    )

                    self.named_character_names = set(named_characters.keys())

                    # Make _ a delimiter, but not $ or `
                    # set_completer_delims(RL_COMPLETER_DELIMS)
                    set_completer_delims(RL_COMPLETER_DELIMS_WITH_BRACE)

                    # GNU Readling inputrc $include's paths are relative to itself,
                    # so chdir to its directory before reading the file.
                    parent_dir = pathlib.Path(__file__).parent.absolute()
                    with parent_dir:
                        inputrc = (
                            "inputrc-unicode" if use_unicode else "inputrc-no-unicode"
                        )
                        try:
                            read_init_file(str(parent_dir / inputrc))
                        except:
                            pass

                    parse_and_bind("tab: complete")
                    self.completion_candidates = []

                # History
                try:
                    read_history_file(HISTFILE)
                except IOError:
                    pass
                except:
                    # PyPy read_history_file fails
                    pass
                else:
                    set_history_length(self.history_length)
                    atexit.register(self.user_write_history_file)
                pass

        except ImportError:
            pass

        colorama_init()
        if style == "None":
            self.terminal_formatter = None
            self.incolors = self.outcolors = ["", "", "", ""]
        else:
            # self.incolors = ["\033[34m", "\033[1m", "\033[22m", "\033[39m"]
            self.incolors = ["\033[32m", "\033[1m", "\033[22m", "\033[39m"]
            self.outcolors = ["\033[31m", "\033[1m", "\033[22m", "\033[39m"]
            if style is not None and not is_pygments_style(style):
                style = None

            if style is None:
                dark_background = is_dark_background()
                if dark_background:
                    style = "inkpot"
                else:
                    style = "colorful"
            try:
                self.terminal_formatter = Terminal256Formatter(style=style)
            except ClassNotFound:
                print(
                    "Pygments style name '%s' not found; No pygments style set" % style
                )

        self.pygments_style = style
        self.definitions = definitions
        self.definitions.set_ownvalue(
            "Settings`$PygmentsShowTokens", from_python(False)
        )
        self.definitions.set_ownvalue("Settings`$PygmentsStyle", from_python(style))
        self.definitions.set_ownvalue("Settings`$UseUnicode", from_python(use_unicode))
        self.definitions.set_ownvalue(
            "Settings`PygmentsStylesAvailable", from_python(ALL_PYGMENTS_STYLES)
        )
        self.definitions.add_message(
            "Settings`PygmentsStylesAvailable",
            Rule(
                Expression(
                    "System`MessageName",
                    Symbol("Settings`PygmentsStylesAvailable"),
                    from_python("usage"),
                ),
                from_python(
                    "A list of Pygments style that are valid in Settings`$PygmentsStyle."
                ),
            ),
        )
        self.definitions.set_attribute(
            "Settings`PygmentsStylesAvailable", "System`Protected"
        )
        self.definitions.set_attribute(
            "Settings`PygmentsStylesAvailable", "System`Locked"
        )
        self.definitions.set_attribute("Settings`$UseUnicode", "System`Locked")

    def change_pygments_style(self, style):
        if style == self.pygments_style:
            return False
        if is_pygments_style(style):
            self.terminal_formatter = Terminal256Formatter(style=style)
            self.pygments_style = style
            return True
        else:
            print("Pygments style not changed")
            return False

    def get_last_line_number(self):
        return self.definitions.get_line_no()

    def get_in_prompt(self):
        next_line_number = self.get_last_line_number() + 1
        if self.lineno > 0:
            return " " * len(f"In[{next_line_number}]:= ")
        else:
            return "{1}In[{2}{0}{3}]:= {4}".format(next_line_number, *self.incolors)

    def get_out_prompt(self, output_style=""):
        line_number = self.get_last_line_number()
        return "{2}Out[{3}{0}{4}]{1}= {5}".format(
            line_number, output_style, *self.outcolors
        )

    def to_output(self, text):
        line_number = self.get_last_line_number()
        newline = "\n" + " " * len("Out[{0}]= ".format(line_number))
        return newline.join(text.splitlines())

    def out_callback(self, out):
        print(self.to_output(str(out)))

    def read_line(self, prompt):
        if self.using_readline:
            line = self.rl_read_line(prompt)
        else:
            line = input(prompt)
        if line.startswith("!") and self.lineno == 0:
            raise ShellEscapeException(line)
        return replace_unicode_with_wl(line)

    def print_result(self, result, output_style=""):
        if result is None:
            # FIXME decide what to do here
            return

        last_eval = result.last_eval

        if last_eval is not None:
            try:
                eval_type = last_eval.get_head_name()
            except:
                print(sys.exc_info()[1])
                return

            out_str = str(result.result)
            if eval_type == "System`Graph":
                out_str = "-Graph-"
            elif self.terminal_formatter:  # pygmentize
                show_pygments_tokens = self.definitions.get_ownvalue(
                    "Settings`$PygmentsShowTokens"
                ).replace.to_python()
                pygments_style = self.definitions.get_ownvalue(
                    "Settings`$PygmentsStyle"
                ).replace.get_string_value()
                if pygments_style != self.pygments_style:
                    if not self.change_pygments_style(pygments_style):
                        self.definitions.set_ownvalue(
                            "Settings`$PygmentsStyle", String(self.pygments_style)
                        )

                if show_pygments_tokens:
                    print(list(lex(out_str, mma_lexer)))
                out_str = highlight(out_str, mma_lexer, self.terminal_formatter)
            output = self.to_output(out_str)
            if output_style == "text":
                print(output)
            else:
                print(self.get_out_prompt("") + output + "\n")

    def rl_read_line(self, prompt):
        # Wrap ANSI color sequences in \001 and \002, so readline
        # knows that they're nonprinting.
        prompt = self.ansi_color_re.sub(lambda m: "\001" + m.group(0) + "\002", prompt)

        return input(prompt)

    def complete_symbol_name(self, text, state):
        try:
            match = re.match(r"^(.*\\\[)([A-Z][a-z]*)$", text)
            if match:
                return self._complete_named_characters(
                    match.group(1), match.group(2), state
                )
            return self._complete_symbol_name(text, state)

        except Exception:
            # any exception thrown inside the completer gets silently
            # thrown away otherwise
            print("Unhandled error in readline completion")
        except:
            raise

    def _complete_named_characters(self, prefix, text, state):
        r"""prefix is the text after \[. Return a list of named character names."""
        if state == 0:
            self.completion_candidates = [
                prefix + name + "]"
                for name in self.named_character_names
                if name.startswith(text)
            ]
            # self.completion_candidates = self.get_completion_symbol_candidates(prefix, text)
        try:
            return self.completion_candidates[state]
        except IndexError:
            return None

    def _complete_symbol_name(self, text, state):
        # The readline module calls this function repeatedly,
        # increasing 'state' each time and expecting one string to be
        # returned per call.
        if state == 0:
            self.completion_candidates = self.get_completion_candidates(text)
        try:
            return self.completion_candidates[state]
        except IndexError:
            return None

    def get_completion_candidates(self, text):

        brace_pos = text.rfind("[")
        if brace_pos >= 0:
            suffix = text[brace_pos + 1 :]
            prefix = text[: brace_pos + 1]
        else:
            prefix = ""
            suffix = text
        try:
            matches = self.definitions.get_matching_names(suffix + "*")
        except Exception:
            return []
        if "`" not in text:
            matches = [strip_context(m) for m in matches]
        return [prefix + m for m in matches]

    def reset_lineno(self):
        self.lineno = 0

    def feed(self):
        result = self.read_line(self.get_in_prompt()) + "\n"
        if result == "\n":
            return ""  # end of input
        self.lineno += 1
        return result

    def empty(self):
        return False

    def user_write_history_file(self):
        try:
            set_history_length(self.history_length)
            write_history_file(HISTFILE)
        except:
            pass
