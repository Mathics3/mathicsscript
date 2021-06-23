# -*- coding: utf-8 -*-
from .helper import session

from mathicsscript import load_default_settings_files


def test_settings():
    load_default_settings_files(session.definitions)

    assert (
        session.evaluate("Settings`$ShowFullFormInput::usage").to_python()
        != "Settings`$ShowFullFormInput::usage"
    )

    assert type(session.evaluate("Settings`$ShowFullFormInput").to_python()) is bool

    assert (
        session.evaluate("Settings`$PygmentsStyle::usage").to_python()
        != "Settings`$PygmentsStyle::usage"
    )

    assert (
        session.evaluate("Settings`$PygmentsShowTokens::usage").to_python()
        != "Settings`$PygmentsShowTokens::usage"
    )

    assert type(session.evaluate("Settings`$PygmentsShowTokens").to_python()) is bool

    assert (
        session.evaluate("Settings`$UseUnicode::usage").to_python()
        != "Settings`$UseUnicode::usage"
    )

    assert type(session.evaluate("Settings`$UseUnicode").to_python()) is bool

    assert (
        session.evaluate("Settings`MathicsScriptVersion::usage").to_python()
        != "Settings`MathicsScriptVersion::usage"
    )


def test_is_not_notebook():
    # the settings already were loaded
    assert session.evaluate("System`$Notebooks").to_python() == False
