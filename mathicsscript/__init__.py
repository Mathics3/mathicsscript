# -*- coding: utf-8 -*-
"""
mathicsscript is a command-line interface to Mathics.

Copyright 2020-2021, 2024-2025 The Mathics3 Team
"""

import os.path as osp

from mathics.session import autoload_files

from mathicsscript.version import __version__


def load_default_settings_files(definitions):

    root_dir = osp.realpath(osp.dirname(__file__))

    autoload_files(definitions, root_dir, "autoload")


__all__ = ["__version__", "load_default_settings_files"]
