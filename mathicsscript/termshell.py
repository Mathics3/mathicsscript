# -*- coding: utf-8 -*-
#   Copyright (C) 2020-2022 Rocky Bernstein <rb@dustyfeet.com>

from columnize import columnize

import locale
import os
import os.path as osp
import pathlib
import sys

from typing import Optional

from mathics_pygments.lexer import MathematicaLexer, MToken

from mathics.core.atoms import String, Symbol
from mathics.core.attributes import attribute_string_to_number
from mathics.core.expression import (
    Expression,
    # strip_context,
    from_python,
)
from mathics.core.rules import Rule
from mathics.core.systemsymbols import SymbolMessageName
from mathics.session import get_settings_value, set_settings_value

from pygments import format, highlight, lex
from pygments.formatters.terminal import TERMINAL_COLORS
from pygments.formatters import Terminal256Formatter
from pygments.styles import get_all_styles
from pygments.util import ClassNotFound

mma_lexer = MathematicaLexer()

ALL_PYGMENTS_STYLES = list(get_all_styles())

color_scheme = TERMINAL_COLORS.copy()
color_scheme[MToken.SYMBOL] = ("yellow", "ansibrightyellow")
color_scheme[MToken.BUILTIN] = ("ansigreen", "ansibrightgreen")
color_scheme[MToken.OPERATOR] = ("magenta", "ansibrightmagenta")
color_scheme[MToken.NUMBER] = ("ansiblue", "ansibrightblue")

from colorama import init as colorama_init

# FIXME: __main__ shouldn't be needed. Fix term_background
from term_background.__main__ import is_dark_background

# Set up mathicsscript configuration directory
CONFIGHOME = os.environ.get("XDG_CONFIG_HOME", osp.expanduser("~/.config"))
CONFIGDIR = osp.join(CONFIGHOME, "mathicsscript")
os.makedirs(CONFIGDIR, exist_ok=True)

try:
    HISTSIZE = int(os.environ.get("MATHICSSCRIPT_HISTSIZE", 50))
except Exception:
    HISTSIZE = 50

HISTFILE = os.environ.get("MATHICS_HISTFILE", osp.join(CONFIGDIR, "history"))
USER_INPUTRC = os.environ.get("MATHICS_INPUTRC", osp.join(CONFIGDIR, "inputrc"))

# Create HISTFILE if it doesn't exist already
if not osp.isfile(HISTFILE):
    pathlib.Path(HISTFILE).touch()

from mathics.core.parser import MathicsLineFeeder

SymbolPygmentsStylesAvailable = Symbol("Settings`PygmentsStylesAvailable")


def is_pygments_style(style: str):
    if style not in ALL_PYGMENTS_STYLES:
        print(f"Pygments style name '{style}' not found.")
        print(f"Style names are:\n{columnize(ALL_PYGMENTS_STYLES)}")
        return False
    return True


class ShellEscapeException(Exception):
    def __init__(self, line):
        self.line = line


class TerminalShellCommon(MathicsLineFeeder):
    def __init__(
        self,
        definitions,
        style: Optional[str],
        want_completion: bool,
        use_unicode: bool,
        prompt: bool,
    ):
        super().__init__("<stdin>")
        self.input_encoding = locale.getpreferredencoding()
        self.lineno = 0
        self.terminal_formatter = None
        self.prompt = prompt

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
        set_settings_value(
            self.definitions, "Settings`$PygmentsShowTokens", from_python(False)
        )
        set_settings_value(
            self.definitions, "Settings`$PygmentsStyle", from_python(style)
        )
        set_settings_value(
            self.definitions, "Settings`$UseUnicode", from_python(use_unicode)
        )
        set_settings_value(
            self.definitions,
            "Settings`PygmentsStylesAvailable",
            from_python(ALL_PYGMENTS_STYLES),
        )
        self.definitions.add_message(
            "Settings`PygmentsStylesAvailable",
            Rule(
                Expression(
                    SymbolMessageName,
                    SymbolPygmentsStylesAvailable,
                    from_python("usage"),
                ),
                from_python(
                    "A list of Pygments style that are valid in Settings`$PygmentsStyle."
                ),
            ),
        )
        self.definitions.set_attribute(
            "Settings`PygmentsStylesAvailable",
            attribute_string_to_number["System`Protected"],
        )
        self.definitions.set_attribute(
            "Settings`PygmentsStylesAvailable",
            attribute_string_to_number["System`Locked"],
        )
        self.definitions.set_attribute(
            "Settings`$UseUnicode", attribute_string_to_number["System`Locked"]
        )

    def change_pygments_style(self, style: str):
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
            # if have_full_readline:
            #     return "{1}In[{2}{0}{3}]:= {4}".format(next_line_number, *self.incolors)
            # else:
            #     return f"In[{next_line_number}]:= "

    def get_out_prompt(self, form: str) -> str:
        """
        Return a formatted "Out" string prefix. ``form`` is either the empty string if the
        default form, or the name of the Form which was used in output preceded by "//"
        """
        line_number = self.get_last_line_number()
        return "{2}Out[{3}{0}{4}]{5}{1}= ".format(line_number, form, *self.outcolors)

    def to_output(self, text: str, form: str) -> str:
        """
        Format an 'Out=' line that it lines after the first one indent properly.
        """
        line_number = self.get_last_line_number()
        newline = "\n" + " " * len(f"Out[{line_number}]{form}= ")
        return newline.join(text.splitlines())

    def out_callback(self, out):
        print(self.to_output(str(out), form=""))

    def read_line(self, prompt):
        if self.using_readline:
            line = self.rl_read_line(prompt)
        else:
            line = input(prompt)
        if line.startswith("!") and self.lineno == 0:
            raise ShellEscapeException(line)
        return line
        # return replace_unicode_with_wl(line)

    def print_result(
        self, result, prompt: bool, output_style="", strict_wl_output=False
    ):
        if result is None:
            # FIXME decide what to do here
            return

        last_eval = result.last_eval

        if last_eval is not None:
            try:
                eval_type = last_eval.get_head_name()
            except Exception:
                print(sys.exc_info()[1])
                return

            out_str = str(result.result)
            use_highlight = True
            if eval_type == "System`String":
                if strict_wl_output:  # exact-wl-compatibility
                    out_str = (
                        format(
                            [(MToken.STRING, out_str.rstrip())], self.terminal_formatter
                        )
                        + "\n"
                    )
                    use_highlight = False
                else:
                    out_str = '"' + out_str.replace('"', r"\"") + '"'
            if eval_type == "System`Graph":
                out_str = "-Graph-"
            elif self.terminal_formatter:  # pygmentize
                show_pygments_tokens = get_settings_value(
                    self.definitions, "Settings`$PygmentsShowTokens"
                )
                pygments_style = get_settings_value(
                    self.definitions, "Settings`$PygmentsStyle"
                )
                if pygments_style != self.pygments_style:
                    if not self.change_pygments_style(pygments_style):
                        set_settings_value(
                            self.definitions,
                            "Settings`$PygmentsStyle",
                            String(self.pygments_style),
                        )

                if show_pygments_tokens:
                    print(list(lex(out_str, mma_lexer)))
                if use_highlight:
                    out_str = highlight(out_str, mma_lexer, self.terminal_formatter)
            form = "" if result.form is None else f"//{result.form}"
            output = self.to_output(out_str, form)
            if output_style == "text" or not prompt:
                print(output)
            else:
                form = "" if result.form is None else f"//{result.form}"
                print(self.get_out_prompt(form) + output + "\n")

    def rl_read_line(self, prompt):
        # Wrap ANSI color sequences in \001 and \002, so readline
        # knows that they're nonprinting.
        prompt = self.ansi_color_re.sub(lambda m: "\001" + m.group(0) + "\002", prompt)

        return input(prompt)

    def reset_lineno(self):
        self.lineno = 0

    def feed(self):
        prompt_str = self.get_in_prompt() if self.prompt else ""
        result = self.read_line(prompt_str) + "\n"
        if result == "\n":
            return ""  # end of input
        self.lineno += 1
        return result

    def empty(self):
        return False
