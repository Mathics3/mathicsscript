# -*- coding: utf-8 -*-
"""
mathicsscript is a command-line interface to Mathics.

Copyright 2020-2021 The Mathics Team
"""
from mathicsscript.version import __version__


def load_default_settings_files(definitions):
    import os.path as osp
    from mathics.core.definitions import autoload_files

    root_dir = osp.realpath(osp.dirname(__file__))

    autoload_files(definitions, root_dir, "autoload")


__all__ = [__version__, load_default_settings_files]
