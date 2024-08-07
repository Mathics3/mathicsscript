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
    long_description_content_type="text/x-rst",
    # don't pack Mathics in egg because of media files, etc.
    zip_safe=False,
    # TODO: could also include long_description, download_url,
)
