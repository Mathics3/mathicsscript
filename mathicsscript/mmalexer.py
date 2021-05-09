# -*- coding: utf-8 -*-
"""
    Lexer for Mathics. Adapted from pygments.lexers.algebra

    :copyright: Copyright 2006-2021 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import re
from pygments.lexer import RegexLexer, words

import pygments.token as PToken


class MToken:
    """
    Mathics Tokens. Like Pygments Token but for Mathics.

    Class variables contain Mathics tokens like BUILTIN, COMMENT.
    These variables hold corresponding Pygments token-name value.
    """

    BUILTIN = PToken.Name.Function
    COMMENT = PToken.Comment
    GROUP = PToken.Punctuation
    LOCAL_SCOPE = PToken.Name.Variable.Class
    MESSAGE = PToken.Name.Exception
    NAMESPACE = PToken.Namespace
    NUMBER = PToken.Number
    OPERATOR = PToken.Operator
    PATTERN = PToken.Name.Tag
    PUNCTUATION = PToken.Punctuation
    SLOT = PToken.Name.Function
    STRING = PToken.String
    TEXT = PToken.Text
    SYMBOL = PToken.Name.Variable
    UNKNOWN = PToken.Error
    WHITESPACE = PToken.Text.Whitespace


class MathematicaLexer(RegexLexer):
    """
    Lexer for `Mathematica <http://www.wolfram.com/mathematica/>`_ source code.

    .. versionadded:: 2.0
    """

    name = "Mathematica"
    aliases = ["mathematica", "mathics", "mma", "nb"]
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
            (r"(?s)\(\*.*?\*\)", MToken.COMMENT),
            (r"([$a-zA-Z]+[$A-Za-z0-9]*`)", MToken.NAMESPACE),
            (r"([$A-Za-z0-9]*_+[$A-Za-z0-9]*)", MToken.SYMBOL),
            (r"#\d*", MToken.SLOT),
            (r"([$a-zA-Z]+[$a-zA-Z0-9]*)", MToken.SYMBOL),
            (r"-?\d+\.\d*", MToken.NUMBER),
            (r"-?\d*\.\d+", MToken.NUMBER),
            (r"-?\d+", MToken.NUMBER),
            (words(operators), MToken.OPERATOR),
            (words(punctuation), MToken.PUNCTUATION),
            (r'".*?"', MToken.STRING),
            (r"\s+", MToken.WHITESPACE),
        ]
    }
