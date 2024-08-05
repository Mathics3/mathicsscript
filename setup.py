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

from setuptools import setup, find_packages


setup(
    name="mathicsscript",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": [
            "mathicsscript/data/inputrc-no-unicode",
            "mathicsscript/data/inputrc-unicode",
            "mathicsscript/user-settings.m",
            "mathicsscript/autoload/settings.m",
            "mathicsscript/config.asy",
        ]
    },
    entry_points={
        "console_scripts": [
            "mathicsscript = mathicsscript.__main__:main",
            "fake_psviewer.py = mathicsscript.fake_psviewer:main",
        ]
    },
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
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Software Development :: Interpreters",
    ],
    # TODO: could also include long_description, download_url,
)
