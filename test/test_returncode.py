import subprocess


def test_returncode():
    assert subprocess.run(["mathicsscript", "-e", "Quit[5]"]).returncode == 5
    assert subprocess.run(["mathicsscript", "-e", "1 + 2'"]).returncode == 0
    assert subprocess.run(["mathicsscript", "-e", "Quit[0]"]).returncode == 0
