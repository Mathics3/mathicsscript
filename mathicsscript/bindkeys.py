from prompt_toolkit.key_binding import KeyBindings
import pathlib
import re

bindings = KeyBindings()

bindings.add("escape", "p", "escape")(
    lambda event: event.current_buffer.insert_text("π")
)

# @bindings.add("escape", "p", "escape")
# def _(event):
#     event.current_buffer.insert_text("π")


def read_inputrc(use_unicode: bool) -> None:
    """
    Read GNU Readline style inputrc
    """
    # GNU Readling inputrc $include's paths are relative to itself,
    # so chdir to its directory before reading the file.
    parent_dir = pathlib.Path(__file__).parent.absolute()
    with parent_dir:
        inputrc = "inputrc-unicode" if use_unicode else "inputrc-no-unicode"
        try:
            read_init_file(str(parent_dir / inputrc))
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
        fields = re.split("\s*: ", line)
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


read_inputrc(use_unicode=1)