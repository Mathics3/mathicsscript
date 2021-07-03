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
import re
from setuptools import setup, find_packages


def get_srcdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


srcdir = get_srcdir()

import sys
import platform

# Ensure user has the correct Python version
if sys.version_info < (3, 6):
    print("mathicsscript does not support Python %d.%d" % sys.version_info[:2])
    sys.exit(-1)


def read(*rnames):
    return open(osp.join(get_srcdir(), *rnames)).read()


# stores __version__ in the current namespace
exec(compile(read("mathicsscript/version.py"), "mathicsscript/version.py", "exec"))

long_description = read("README.rst") + "\n"
exec(read("mathicsscript/version.py"))

is_PyPy = platform.python_implementation() == "PyPy"

EXTRAS_REQUIRE = {}
for kind in ("dev", "full"):
    extras_require = []
    requirements_file = f"requirements-{kind}.txt"
    for line in open(requirements_file).read().split("\n"):
        if line and not line.startswith("#"):
            requires = re.sub(r"([^#]+)(\s*#.*$)?", r"\1", line)
            extras_require.append(requires)
    EXTRAS_REQUIRE[kind] = extras_require

setup(
    maintainer="Mathics Group",
    maintainer_email="mathics-devel@googlegroups.com",
    author_email="rb@dustyfeet.com",
    name="mathicsscript",
    version=__version__,  # noqa
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": [
            "mathicsscript/data/inputrc-no-unicode",
            "mathicsscript/data/inputrc-unicode",
            "mathicsscript/user-settings.m",
            "mathicsscript/autoload/*.m",
        ]
    },
    install_requires=[
        "Mathics_Scanner>=1.2.2",
        "Mathics3 >= 3.1.0,<3.2.0",
        "click",
        "colorama",
        "columnize",
        "networkx",
        "prompt_toolkit>=3.0.18",
        "Pygments>=2.9.0",  # Want something late enough that has the "inkpot" style
        # "mathics_pygments @ https://github.com/Mathics3/mathics-pygments/archive/master.zip#egg=mathics_pygments",
        "mathics_pygments>=1.0.2",
        "term-background >= 1.0.1",
    ],
    entry_points={"console_scripts": ["mathicsscript = mathicsscript.__main__:main"]},
    extras_require=EXTRAS_REQUIRE,
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
