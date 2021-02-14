#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Setuptools based setup script for Mathics.

For the easiest installation just type the following command (you'll probably
need root privileges):

    pip install -e .

This will install the library in the default location. For instructions on
how to customize the install procedure read the output of:

    python setup.py --help install
"""

import os.path as osp
from setuptools import setup, find_packages


def get_srcdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


srcdir = get_srcdir()


def read(*rnames):
    return open(osp.join(srcdir, *rnames)).read()


import sys
import platform

# Ensure user has the correct Python version
if sys.version_info < (3, 6):
    print("mathicsscript does not support Python %d.%d" % sys.version_info[:2])
    sys.exit(-1)


def get_srcdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


def read(*rnames):
    return open(osp.join(get_srcdir(), *rnames)).read()


# stores __version__ in the current namespace
exec(compile(read("mathicsscript/version.py"), "mathicsscript/version.py", "exec"))

long_description = read("README.rst") + "\n"
exec(read("mathicsscript/version.py"))

is_PyPy = platform.python_implementation() == "PyPy"

setup(
    maintainer="Mathics Group",
    maintainer_email="mathic-devel@googlegroups.com",
    author_email="rb@dustyfeet.com",
    name="mathicsscript",
    version=__version__,  # noqa
    packages=find_packages(),
    include_package_data=True,
    package_data={"": ["inputrc-no-unicode", "inputrc-unicode", "settings/settings.m"]},
    install_requires=[
        "Mathics_Scanner>=1.0.0,<1.1.0",
        "Mathics3 >= 2.0.0,<2.1.0",
        "click",
        "colorama",
        "columnize",
        "networkx",
        "pygments",
        "term-background >= 1.0.1",
    ],
    entry_points={"console_scripts": ["mathicsscript = mathicsscript.__main__:main"]},
    long_description=long_description,
    long_description_content_type="text/x-rst",
    # don't pack Mathics in egg because of media files, etc.
    zip_safe=False,
    # metadata for upload to PyPI
    description="A general-purpose computer algebra system.",
    license="GPL",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Software Development :: Interpreters",
    ],
    # TODO: could also include long_description, download_url,
)
