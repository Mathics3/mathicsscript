# -*- coding: utf-8 -*-
#   Copyright (C) 2020 Rocky Bernstein <rb@dustyfeet.com>

import atexit
import os
import os.path as osp
import locale
import pathlib
import sys
import re
from mathics.core.expression import strip_context
from mathics.core.characters import named_characters

from pygments import highlight
from mathicsscript.mmalexer import MathematicaLexer

mma_lexer = MathematicaLexer()

from pygments.formatters.terminal import TERMINAL_COLORS
from pygments.formatters import Terminal256Formatter
from pygments.styles import get_style_by_name
from pygments.util import ClassNotFound

from pygments.token import (
    # Comment,
    # Generic,
    # Keyword,
    Name,
    Literal,
    # Operator,
    # String,
    Token,
)

color_scheme = TERMINAL_COLORS.copy()
color_scheme[Token.Name] = ("yellow", "ansibrightyellow")
color_scheme[Name.Function] = ("ansigreen", "ansibrightgreen")
color_scheme[Name.NameSpace] = ("magenta", "ansibrightmagenta")
color_scheme[Literal.Number] = ("ansiblue", "ansibrightblue")

from colorama import init as colorama_init
from term_background import is_dark_background

from readline import (
    read_history_file,
    read_init_file,
    set_completer,
    set_completer_delims,
    set_history_length,
    write_history_file,
)

try:
    HISTSIZE = int(os.environ.get("MATHICSSCRIPT_HISTSIZE", 50))
except:
    HISTSIZE = 50

HISTFILE = osp.expanduser("~/.mathicsscript_hist")

RL_COMPLETER_DELIMS_WITH_BRACE = " \t\n_~!@#%^&*()-=+{]}|;:'\",<>/?"
RL_COMPLETER_DELIMS = " \t\n_~!@#%^&*()-=+[{]}\\|;:'\",<>/?"


from mathics.core.parser import LineFeeder, FileLineFeeder


class TerminalShell(LineFeeder):
    def __init__(
        self, definitions, style: str, want_readline: bool, want_completion: bool
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

                    inputrc = pathlib.Path(__file__).parent.absolute() / "inputrc"
                    read_init_file(inputrc)
                    # parse_and_bind("tab: complete")
                    self.completion_candidates = []

                # History
                try:
                    read_history_file(HISTFILE)
                except IOError:
                    pass
                except:
                    # PyPy read_history_file fails
                    return
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
            if style is None:
                dark_background = is_dark_background()
                if dark_background:
                    style = "paraiso-dark"
                else:
                    style = "paraiso-light"
            try:
                self.terminal_formatter = Terminal256Formatter(style=style)
            except ClassNotFound:
                print(
                    "Pygments style name '%s' not found; No pygments style set" % style
                )

        self.definitions = definitions

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
            return self.rl_read_line(prompt)
        return input(prompt)

    def print_result(self, result, output_style="", debug_pygments=False):
        if result is not None and result.result is not None:
            out_str = str(result.result)
            if self.terminal_formatter:  # pygmentize
                from pygments import lex

                if debug_pygments:
                    print(list(lex(out_str, mma_lexer)))
                out_str = highlight(out_str, mma_lexer, self.terminal_formatter)
            output = self.to_output(out_str)
            print(self.get_out_prompt(output_style) + output + "\n")

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

        except Exception as e:
            # any exception thrown inside the completer gets silently
            # thrown away otherwise
            print("Unhandled error in readline completion")
        except:
            raise

    def _complete_named_characters(self, prefix, text, state):
        """prefix is the text after \[. Return a list of named character names."""
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
        except Exception as e:
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
