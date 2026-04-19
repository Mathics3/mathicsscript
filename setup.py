#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Setuptools based setup script for Mathics3 Scanner.

For the easiest installation just type the following command (you'll probably
need root privileges):

    pip install -e .

This will install the library in the default location. For instructions on
how to customize the install procedure read the output of:

    python setup.py --help install
"""

import os
import os.path as osp

from setuptools import setup
from setuptools.command.build_py import build_py as setuptools_build_py


def get_srcdir():
    """Return the directory of the location if this code"""
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


class build_py(setuptools_build_py):
    """
    The "run" method below of class gets invoked when setup.py is run through
    setuptools.

    Here, we just invoke ./admin-tools/make-JSON-tables.sh.
    """

    def run(self):
        """
        If you need to debug this, just extract this method, remove "self" above
        and save it in a standalone Python file without the setuptools_build_py.run(self)
        call below.
        """
        srcdir = get_srcdir()
        cmd = f"bash {osp.join(srcdir, 'admin-tools', 'make-JSON-tables.sh')}"
        print(cmd)
        os.system(cmd)
        setuptools_build_py.run(self)


CMDCLASS = {"build_py": build_py}

setup(
    # Use static files for now.
    # cmdclass=CMDCLASS,  # Set up to run build_py.run()
    # don't pack Mathics3 an in egg because of media files, etc.
    zip_safe=False,
)
