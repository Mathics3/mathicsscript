#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a replacement for a PostScript previewer like gv
which does nothing, but remove any file argument it is
given.

Asymptote run via mathicsscript will create an embeded postscript file out.eps
which should be removed.
"""
import os
import sys


def main():
    if len(sys.argv) > 1:
        eps_file = sys.argv[1]
        if os.path.exists(eps_file):
            os.remove(eps_file)


if __name__ == "__main__":
    main()
