# -*- coding: utf-8 -*-
# Copyright (C) 2021-2022 Rocky Bernstein <rb@dustyfeet.com>
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from typing import Callable
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.filters import Condition
import pathlib
import re

from mathicsscript.settings import definitions
from mathics.session import get_settings_value


@Condition
def autocomplete_on():
    return get_settings_value(definitions, "Settings`$GroupAutocomplete")


bindings = KeyBindings()

# bindings.add("escape", "p", "escape")(
#     lambda event: event.current_buffer.insert_text(" ")
# )


@bindings.add("{", filter=autocomplete_on)
def curly_left(event):
    b = event.cli.current_buffer
    b.insert_text("{")
    b.insert_text("}", move_cursor=False)


@bindings.add("}", filter=autocomplete_on)
def curly_right(event):
    b = event.cli.current_buffer
    char = b.document.current_char
    if char == "}":
        b.cursor_right()
    else:
        b.insert_text("}")


@bindings.add("(", filter=autocomplete_on)
def paren_left(event):
    b = event.cli.current_buffer
    b.insert_text("(")
    b.insert_text(")", move_cursor=False)


@bindings.add(")", filter=autocomplete_on)
def paren_right(event):
    b = event.cli.current_buffer
    char = b.document.current_char
    if char == ")":
        b.cursor_right()
    else:
        b.insert_text(")")


@bindings.add("[", filter=autocomplete_on)
def bracket_left(event):
    b = event.cli.current_buffer
    b.insert_text("[")
    b.insert_text("]", move_cursor=False)


@bindings.add("]", filter=autocomplete_on)
def bracket_right(event):
    b = event.cli.current_buffer
    char = b.document.current_char
    if char == "]":
        b.cursor_right()
    else:
        b.insert_text("]")


@bindings.add("'", filter=autocomplete_on)
def single_quotation(event):
    b = event.cli.current_buffer
    char = b.document.current_char
    if char == "'":
        b.cursor_right()
    else:
        b.insert_text("'")
        b.insert_text("'", move_cursor=False)


@bindings.add('"', filter=autocomplete_on)
def double_quotation(event):
    b = event.cli.current_buffer
    char = b.document.current_char
    if char == '"':
        b.cursor_right()
    else:
        b.insert_text('"')
        b.insert_text('"', move_cursor=False)


# Add an additional key binding for toggling this flag.
@bindings.add("f4")
def _editor_toggle(event):
    """Toggle between Emacs and Vi mode."""
    app = event.app

    if app.editing_mode == EditingMode.VI:
        app.editing_mode = EditingMode.EMACS
    else:
        app.editing_mode = EditingMode.VI


# Add an additional key binding for toggling this flag.
@bindings.add("f3")
def _group_autocomplete_toggle(event):
    """Complete braces."""
    app = event.app

    if not hasattr(app, "group_autocomplete"):
        app.group_autocomplete = False
    app.group_autocomplete = not app.group_autocomplete


def read_inputrc(read_init_file_fn: Callable, use_unicode: bool) -> None:
    """
    Read GNU Readline style inputrc
    """
    # GNU Readling inputrc $include's paths are relative to itself,
    # so chdir to its directory before reading the file.
    parent_dir = pathlib.Path(__file__).parent.absolute()
    with parent_dir:
        inputrc = "inputrc-unicode" if use_unicode else "inputrc-no-unicode"
        try:
            read_init_file_fn(str(parent_dir / "data" / inputrc))
        except:
            pass


def read_init_file(path: str):
    def check_quoted(s: str):
        return s[0:1] == '"' and s[-1:] == '"'

    def add_binding(alias_expand, replacement: str):
        def self_insert(event):
            event.current_buffer.insert_text(replacement)

        bindings.add(*alias_expand)(self_insert)

    for line_no, line in enumerate(open(path, "r").readlines()):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        fields = re.split(r"\s*: ", line)
        if len(fields) != 2:
            print(f"{line_no+1}: expecting 2 fields, got {len(fields)} in:\n{line}")
            continue
        alias, replacement = fields
        if not check_quoted(alias):
            print(f"{line_no+1}: expecting alias to be quoted, got {alias} in:\n{line}")
        alias = alias[1:-1]
        if not check_quoted(replacement):
            print(
                f"{line_no+1}: expecting replacement to be quoted, got {replacement} in:\n{line}"
            )
            continue
        replacement = replacement[1:-1]
        alias_expand = [
            c if c != "\x1b" else "escape" for c in list(alias.replace(r"\e", "\x1b"))
        ]
        add_binding(alias_expand, replacement)
    pass
