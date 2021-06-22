# -*- coding: utf-8 -*-
from .helper import session

import os.path as osp

from mathics.core.definitions import autoload_files, Definitions

def test_settings():
    for setting in (
        "Settings`$ShowFullFormInput::usage",
        "Settings`$ShowFullFormInput",
        "Settings`$PygmentsStyle::usage",
        "Settings`$PygmentsShowTokens::usage",
        "Settings`$PygmentsShowTokens",
        "Settings`$UseUnicode::usage",
        "Settings`$UseUnicode",
        "Settings`MathicsScriptVersion::usage",
        "System`$Notebooks",
        "System`$Notebooks::usage",
    ):
        assert session.evaluate(setting), setting

def test_is_not_notebook():
    import os.path as osp
    from mathics.core.definitions import autoload_files

    root_dir = osp.realpath(osp.join(
        osp.dirname(osp.abspath(__file__)),
        "..",
        "mathicsscript",
    ))

    autoload_files(session.definitions, root_dir, "autoload")

    assert session.evaluate("System`$Notebooks").to_python() == False
