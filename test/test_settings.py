# -*- coding: utf-8 -*-
from .helper import session

import os.path as osp

from mathics.core.definitions import autoload_files, Definitions

def test_settings():
    import os.path as osp
    from mathics.core.definitions import autoload_files
    import mathicsscript

    root_dir = osp.realpath(
        osp.dirname(mathicsscript.__file__),
    )

    autoload_files(session.definitions, root_dir, "autoload")

    assert session.evaluate("Settings`$ShowFullFormInput::usage").to_python() != "Settings`$ShowFullFormInput::usage"

    assert type(session.evaluate("Settings`$ShowFullFormInput").to_python()) is bool

    assert session.evaluate("Settings`$PygmentsStyle::usage").to_python() != "Settings`$PygmentsStyle::usage"

    assert session.evaluate("Settings`$PygmentsShowTokens::usage").to_python() != "Settings`$PygmentsShowTokens::usage"

    assert type(session.evaluate("Settings`$PygmentsShowTokens").to_python()) is bool

    assert session.evaluate("Settings`$UseUnicode::usage").to_python() != "Settings`$UseUnicode::usage"

    assert type(session.evaluate("Settings`$UseUnicode").to_python()) is bool

    assert session.evaluate("Settings`MathicsScriptVersion::usage").to_python() != "Settings`MathicsScriptVersion::usage"

def test_is_not_notebook():
	# the settings already were loaded
    assert session.evaluate("System`$Notebooks").to_python() == False
