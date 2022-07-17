# -*- coding: utf-8 -*-
#   Copyright (C) 2021-2022 Rocky Bernstein <rb@dustyfeet.com>

import locale
import os
import os.path as osp
import re
import sys
from typing import Optional

from mathics_pygments.lexer import MathematicaLexer, MToken
from mathicsscript.completion import MathicsCompleter
from mathicsscript.termshell import (
    CONFIGDIR,
    HISTSIZE,
    USER_INPUTRC,
    is_pygments_style,
    ShellEscapeException,
    SymbolPygmentsStylesAvailable,
    TerminalShellCommon,
)
from mathicsscript.version import __version__

from mathics.core.atoms import String
from mathics.core.attributes import attribute_string_to_number
from mathics.core.expression import Expression, from_python
from mathics.core.rules import Rule
from mathics.core.systemsymbols import SymbolMessageName

from mathicsscript.bindkeys import bindings, read_inputrc, read_init_file

from prompt_toolkit import PromptSession, HTML, print_formatted_text
from prompt_toolkit.application.current import get_app
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.history import FileHistory
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles.pygments import style_from_pygments_cls


from pygments import format, highlight, lex
from pygments.styles import get_style_by_name
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

HISTFILE = osp.join(CONFIGDIR, "history-ptk")


class TerminalShellPromptToolKit(TerminalShellCommon):
    def __init__(
        self,
        definitions,
        style: Optional[str],
        want_completion: bool,
        use_unicode: bool,
        prompt: bool,
    ):
        super(TerminalShellCommon, self).__init__("<stdin>")
        self.input_encoding = locale.getpreferredencoding()
        self.lineno = 0
        self.terminal_formatter = None
        self.mma_pygments_lexer = PygmentsLexer(MathematicaLexer)
        self.prompt = prompt

        self.session = PromptSession(history=FileHistory(HISTFILE))

        # Try importing readline to enable arrow keys support etc.
        self.using_readline = False
        self.history_length = definitions.get_config_value("$HistoryLength", HISTSIZE)
        self.using_readline = sys.stdin.isatty() and sys.stdout.isatty()
        self.ansi_color_re = re.compile("\033\\[[0-9;]+m")

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
                sys.stderr.write(
                    f"Pygments style name '{style}' not found; No pygments style set\n"
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

        read_inputrc(read_init_file, use_unicode=use_unicode)
        if osp.isfile(USER_INPUTRC):
            if os.access(USER_INPUTRC, os.R_OK):
                read_init_file(USER_INPUTRC)
            else:
                sys.stderr.write(
                    f"Can't read user inputrc file {USER_INPUTRC}; skipping\n"
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
        self.completer = MathicsCompleter(self.definitions) if want_completion else None

    def bottom_toolbar(self):
        """Adds a mode-line toolbar at the bottom"""
        # TODO: Figure out how allow user-customization
        app = get_app()
        edit_mode = "Vi" if app.editing_mode == EditingMode.VI else "Emacs"

        app.group_autocomplete = True

        if self.definitions.get_ownvalue("Settings`$GroupAutocomplete"):
            app.group_autocomplete = self.definitions.get_ownvalue(
                "Settings`$GroupAutocomplete"
            ).replace.to_python()

        edit_mode = "Vi" if app.editing_mode == EditingMode.VI else "Emacs"
        return HTML(
            f" mathicsscript: {__version__}, Style: {self.pygments_style}, Mode: {edit_mode}, Autobrace: {app.group_autocomplete}"
        )

    def get_in_prompt(self):
        next_line_number = self.get_last_line_number() + 1
        if self.lineno > 0:
            return " " * len(f"In[{next_line_number}]:= ")
        else:
            return HTML(f"<ansired>In[<b>{next_line_number}</b>]:=</ansired> ")

    def get_out_prompt(self):
        line_number = self.get_last_line_number()
        return HTML(f"<ansigreen>Out[<b>{line_number}</b>]:=</ansigreen> ")

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
                if use_highlight:
                    out_str = highlight(out_str, mma_lexer, self.terminal_formatter)
            output = self.to_output(out_str)
            if output_style == "text" or not prompt:
                print(output)
            elif self.session:
                print_formatted_text(self.get_out_prompt(), end="")
                print(output + "\n")
            else:
                print(self.get_out_prompt() + output + "\n")

    def read_line(self, prompt):
        # FIXME set and update inside self.

        style = style_from_pygments_cls(get_style_by_name(self.pygments_style))

        line = self.session.prompt(
            prompt,
            bottom_toolbar=self.bottom_toolbar,
            completer=self.completer,
            key_bindings=bindings,
            lexer=self.mma_pygments_lexer,
            style=style,
        )
        # line = self.rl_read_line(prompt)
        if line.startswith("!") and self.lineno == 0:
            raise ShellEscapeException(line)
        return line
        # return replace_unicode_with_wl(line)
