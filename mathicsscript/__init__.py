# -*- coding: utf-8 -*-
"""
mathicsscript is a command-line interface to Mathics.

Copyright 2020-2021 The Mathics Team
"""
from ctypes.util import find_library

from mathicsscript.fixcairo import fix_cairo
from mathicsscript.version import __version__


def load_default_settings_files(definitions):
    import os.path as osp

    from mathics.core.definitions import autoload_files

    root_dir = osp.realpath(osp.dirname(__file__))

    autoload_files(definitions, root_dir, "autoload")


__all__ = ["__version__", "load_default_settings_files"]

if not find_library("libcairo-2"):
    fix_cairo()
