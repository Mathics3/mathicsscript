import re

from typing import Iterable, NamedTuple

from mathics.core.expression import strip_context
from mathics_scanner import named_characters
from prompt_toolkit.completion import CompleteEvent, Completion, WordCompleter
from prompt_toolkit.document import Document

FIND_MATHICS_WORD_RE = re.compile(r"((?:\[)?[^\s]+)")

# TODO: "kind" could be an enumeration: of "Null", "Symbol", "NamedCharacter"
WordToken = NamedTuple("WordToken", [("text", str), ("kind", str)])


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


class MathicsCompleter(WordCompleter):
    def __init__(self, definitions):
        self.definitions = definitions
        self.completer = WordCompleter([])

        # From WordCompleter, adjusted with default values
        self.ignore_case = True
        self.display_dict = {}
        self.meta_dict = {}
        self.WORD = False
        self.sentence = False
        self.match_middle = False
        self.pattern = None
        self.display_dict = self.completer.display_dict
        self.named_characters = [name + "]" for name in named_characters.keys()]

    def _is_word_before_cursor_complete(
        self, document, text_before_cursor: str
    ) -> bool:
        return text_before_cursor == "" or text_before_cursor[-1:].isspace()

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        # Get word/text before cursor.
        word_before_cursor, kind = self.get_word_before_cursor_with_kind(document)
        if kind == "Symbol":
            words = self.get_word_names()
        elif kind == "NamedCharacter":
            words = self.named_characters
        else:
            # FIXME add ascii operators, and escape symbols
            words = []

        def word_matches(word: str) -> bool:
            """ True when the word before the cursor matches. """

            if self.match_middle:
                return word_before_cursor in word
            else:
                return word.startswith(word_before_cursor)

        for a in words:
            if word_matches(a):
                display = self.display_dict.get(a, a)
                display_meta = self.meta_dict.get(a, "")
                yield Completion(
                    a,
                    -len(word_before_cursor),
                    display=display,
                    display_meta=display_meta,
                )

    def get_word_before_cursor_with_kind(self, document: Document) -> WordToken:
        """
        Get the word before the cursor and clasify it into:

        If we have whitespace before the cursor this returns an empty string.

        :param pattern: (None or compiled regex). When given, use this regex
            pattern.
        """

        text_before_cursor = document.text_before_cursor

        if self._is_word_before_cursor_complete(
            document=document, text_before_cursor=text_before_cursor
        ):
            # Space before the cursor or no text before cursor.
            return WordToken("", "Null")

        start = (
            document.find_start_of_previous_word(
                WORD=False, pattern=FIND_MATHICS_WORD_RE
            )
            or 0
        )

        word_before_cursor = text_before_cursor[len(text_before_cursor) + start :]
        if word_before_cursor.startswith(r"\["):
            return WordToken(word_before_cursor[2:], "NamedCharacter")
        elif word_before_cursor.isnumeric():
            return WordToken(word_before_cursor, "Null")

        return word_before_cursor, "Symbol"

    def get_word_names(self: str):
        names = self.definitions.get_names()
        short_names = [strip_context(m) for m in names]
        return list(names) + short_names
