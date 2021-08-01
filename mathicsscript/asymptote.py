#!/usr/bin/env python3
"""Python module to feed Asymptote with commands
(modified from gnuplot.py)
"""

import os
import os.path as osp

from subprocess import Popen, PIPE

asy_program = os.environ.get("ASY_PROG", "asy")


def get_srcdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


mydir = get_srcdir()
asy_config = os.path.join(mydir, "config.asy")


class Asy(object):
    def __init__(self, show_help=True):
        self.session = Popen(
            [asy_program, f"-config={asy_config}", "-quiet", "-inpipe=0", "-outpipe=2"],
            stdin=PIPE,
        )
        if show_help:
            self.help()

    def send(self, cmd):
        self.session.stdin.write(bytes(cmd + "\n", "utf-8"))
        self.session.stdin.flush()

    def size(self, size: int):
        self.send("size(%d);" % size)

    def draw(self, s: str):
        self.send(f"draw({s});")

    def fill(self, s: str):
        self.send(f"fill({s});")

    def clip(self, s: str):
        self.send(f"clip({s});")

    def label(self, s: str):
        self.send(f"label({s});")

    def shipout(self, s: str):
        self.send(f'shipout("{s}");')

    def erase(self):
        self.send("erase();")

    def help(self):
        print("Asymptote session is open.  Available methods are:")
        print(
            "    help(), size(int), draw(str), fill(str), clip(str), label(str), shipout(str), send(str), erase()"
        )

    def __del__(self):
        # print("closing Asymptote session...")
        # Popen in __init__ can fail (e.g. asymptote is not intalled), so self
        # potentially does not have a sesion attribute and without this check an
        # AttributeError can get logged
        if hasattr(self, "session"):
            self.send("quit")
            self.session.stdin.close()
            self.session.wait()


if __name__ == "__main__":
    g = Asy()
    g.size(200)
    g.draw("unitcircle")
    g.send("draw(unitsquare)")
    g.fill("unitsquare,blue")
    g.clip("unitcircle")
    g.label('"$O$",(0,0),SW')
    input("press ENTER to continue")
    g.erase()
    del g
