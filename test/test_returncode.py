import subprocess

import os.path as osp


def get_testdir():
    filename = osp.normcase(osp.dirname(osp.abspath(__file__)))
    return osp.realpath(filename)


def test_returncode():
    assert subprocess.run(["mathicsscript", "-c", "Quit[5]"]).returncode == 5
    assert subprocess.run(["mathicsscript", "-c", "1 + 2'"]).returncode == 0
    assert subprocess.run(["mathicsscript", "-c", "Quit[0]"]).returncode == 0

    gcd_file = osp.join(get_testdir(), "data", "recursive-gcd.m")
    assert subprocess.run(["mathicsscript", "-f", gcd_file]).returncode == 0


if __name__ == "__main__":
    test_returncode()
