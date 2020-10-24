# -*- coding: utf-8 -*-

from mathicsscript.term_background import set_default_bg, is_dark_rgb, is_dark_color_fg_bg, is_dark_background
from os import environ

def test_set_default_bg():
    environ["TERM"] = "xterm"
    assert not set_default_bg()
    del environ["TERM"]
    assert set_default_bg()

def test_is_dark_rgb():
    # Test 16-bit values
    for r, g, b, expect in (
            (0, 0, 0, True),
            (16, 16, 16, False),
            (16, 16, 0, False),
            (0, 16, 16, False),
            (0, 8, 10, True),
            (8, 0, 10, True),
            ):
        assert is_dark_rgb(r, g, b) == expect, f"is_dark(r={r}, g={g}, b={b}) should be {expect}"

def test_is_dark_fg_bg():
    environ["LC_DARK_BG"] = "1"
    assert is_dark_color_fg_bg()
    environ["LC_DARK_BG"] = "0"
    assert not is_dark_color_fg_bg()
    del environ["LC_DARK_BG"]
    environ["COLORFGBG"] = "15;0"
    assert is_dark_color_fg_bg()
    environ["COLORFGBG"] = "0;15"
    assert not is_dark_color_fg_bg()

if __name__ == '__main__':
    test_is_dark_rgb()
