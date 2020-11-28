# -*- coding: utf-8 -*-
"""
    Lexer for Mathics. Adapted from pygments.lexers.algebra

    :copyright: Copyright 2006-2020 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from pygments.lexer import RegexLexer, bygroups, words
from pygments.token import (
    Text,
    Comment,
    Operator,
    Keyword,
    Name,
    String,
    Number,
    Punctuation,
)


class MathematicaLexer(RegexLexer):
    """
    Lexer for `Mathematica <http://www.wolfram.com/mathematica/>`_ source code.

    .. versionadded:: 2.0
    """

    name = "Mathematica"
    aliases = ["mathematica", "mma", "nb"]
    filenames = ["*.nb", "*.cdf", "*.nbp", "*.ma"]
    mimetypes = [
        "application/mathematica",
        "application/vnd.wolfram.mathematica",
        "application/vnd.wolfram.mathematica.package",
        "application/vnd.wolfram.cdf",
    ]

    # http://reference.wolfram.com/mathematica/guide/Syntax.html
    operators = (
        ";;",
        "=",
        "=.",
        "!=" "==",
        ":=",
        "->",
        ":>",
        "/.",
        "+",
        "-",
        "*",
        "/",
        "^",
        "&&",
        "||",
        "!",
        "<>",
        "|",
        "/;",
        "?",
        "@",
        "//",
        "/@",
        "@@",
        "@@@",
        "~~",
        "===",
        "&",
        "<",
        ">",
        "<=",
        ">=",
    )

    punctuation = (",", ";", "(", ")", "[", "]", "{", "}")

    def _multi_escape(entries):
        return "(%s)" % ("|".join(re.escape(entry) for entry in entries))

    tokens = {
        "root": [
            (r"(?s)\(\*.*?\*\)", Comment),
            (r"([$a-zA-Z]+[$A-Za-z0-9]*`)", Name.Namespace),
            (r"([$A-Za-z0-9]*_+[$A-Za-z0-9]*)", Name.Variable),
            (r"#\d*", Name.Variable),
            (r"([$a-zA-Z]+[$a-zA-Z0-9]*)", Name),
            (r"-?\d+\.\d*", Number.Float),
            (r"-?\d*\.\d+", Number.Float),
            (r"-?\d+", Number.Integer),
            (words(operators), Operator),
            (words(punctuation), Punctuation),
            (r'".*?"', String),
            (r"\s+", Text.Whitespace),
        ]
    }
