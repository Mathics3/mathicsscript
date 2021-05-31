# -*- coding: utf-8 -*-
#   Copyright (C) 2020-2021 Rocky Bernstein <rb@dustyfeet.com>

import atexit
import os
import os.path as osp
import locale
import pathlib
import sys
import re
from mathics_scanner import named_characters
from mathicsscript.termshell import is_pygments_style, TerminalShellCommon
from mathics.core.expression import Expression, Symbol
from mathics.core.expression import strip_context, from_python
from mathics.core.rules import Rule

from pygments.formatters import Terminal256Formatter
from pygments.styles import get_all_styles
from pygments.util import ClassNotFound

ALL_PYGMENTS_STYLES = list(get_all_styles())

from colorama import init as colorama_init

## FIXME: __main__ shouldn't be needed. Fix term_background
from term_background.__main__ import is_dark_background

try:
    from readline import (
        parse_and_bind,
        read_history_file,
        read_init_file,
        set_completer,
        set_completer_delims,
        set_history_length,
        write_history_file,
    )

    have_full_readline = True
except ImportError:
    have_full_readline = False

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


class TerminalShellGNUReadline(TerminalShellCommon):
    def __init__(
        self,
        definitions,
        style: str,
        want_readline: bool,
        want_completion: bool,
        use_unicode: bool,
        prompt: bool,
    ):
        super(TerminalShellGNUReadline, self).__init__(
            definitions, style, want_completion, use_unicode, prompt
        )

        # Try importing readline to enable arrow keys support etc.
        self.using_readline = False
        self.history_length = definitions.get_config_value("$HistoryLength", HISTSIZE)
        if have_full_readline and want_readline:
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
                    inputrc = "inputrc-unicode" if use_unicode else "inputrc-no-unicode"
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

    def get_completion_candidates(self, text: str):

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

    def user_write_history_file(self):
        try:
            set_history_length(self.history_length)
            write_history_file(HISTFILE)
        except:
            pass
