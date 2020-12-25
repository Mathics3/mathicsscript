# -*- coding: utf-8 -*-
from .helper import session


def test_settings():
    # FIXME: this is a start, but we should do more
    for setting in (
        "Settings`$ShowFullFormInput::usage",
        "Settings`$ShowFullFormInput",
        "Settings`$PygmentsStyle::usage",
        "Settings`$PygmentsShowTokens::usage",
        "Settings`$PygmentsShowTokens",
        "Settings`$UseUnicode::usage",
        "Settings`$UseUnicode",
        "Settings`MathicsScriptVersion::usage",
    ):
        assert session.evaluate(setting), setting
