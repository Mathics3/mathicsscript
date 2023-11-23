# -*- coding: utf-8 -*-
"""
Fix cairo for Windows
"""

import os
import platform
import subprocess
from ctypes.util import find_library
from importlib.util import find_spec

import requests
from tqdm import tqdm

default_GTK_path = "C:\\Program Files\\GTK3-Runtime Win64\\bin"

mathicsscript_path = find_spec("mathicsscript").submodule_search_locations[0]

if platform.architecture()[0] == "64bit":
    release_url = "https://api.github.com/repos/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases/latest"
else:
    release_url = "https://api.github.com/repos/miegir/GTK-for-Windows-Runtime-Environment-Installer-32/releases/latest"

fix_cairo_long_intro = f"""
We noticed that you are using mathicsscript on Windows. Due to a well known bug in the dependency
package cairocffi for mathicsscript on Windows, mathicsscript is not working properly right now.
We will now try to fix it, or you can visit https://github.com/Mathics3/mathicsscript/issues/76
to fix it yourself.

Specifically, cairocffi needs libcairo-2.dll and some other dll files to work properly on Windows.
To get these libraries, we will download the latest GTK+ for Windows Runtime Environment Installer
from {release_url}
and install it for you. After installation, whenever you run mathicsscript, the GTK+ for Windows 
dll libraries will be automatically loaded to make mathicsscript run properly.

IMPORTANT: Remember to check the "Set up PATH environment variable to include GTK+" option!

Please note that now the GTK+ for Windows dll libraries will only be loaded when mathicsscript is
imported. If you want to load them when importing cairocffi, see 
https://github.com/Mathics3/mathicsscript/issues/76.

Do you want us to install GTK+ for Windows Runtime Environment for you? [Y/n] (default: Y)
"""


def download_file(url, dest, name=None):
    response = requests.get(url, stream=True, timeout=5)
    total_size = int(response.headers.get("content-length", 0))
    if response.status_code == 200:
        with open(dest, "wb") as file:
            with tqdm(
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                desc=f"Downloading {name}",
            ) as pbar:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
                        file.flush()
                        pbar.update(len(chunk))
                        pbar.refresh()
    else:
        print(f"Failed to download: {url}")


def download_GTK_installer():
    response = requests.get(release_url, timeout=5)
    if response.status_code == 200:
        name = response.json()["assets"][0]["name"]
        file_url = response.json()["assets"][0]["browser_download_url"]
        file_path = os.path.join(mathicsscript_path, name)
        download_file(file_url, file_path, name)
        print("Done.")
        return file_path
    else:
        print("Failed to retrieve directory contents.")


def set_dll_search_path():
    """
    Python 3.8+ no longer searches for DLLs in PATH, so we have to add
    everything in PATH manually. Note that unlike PATH add_dll_directory
    has no defined order, so if there are two cairo DLLs in PATH we
    might get a random one.
    """
    if not hasattr(os, "add_dll_directory"):
        return
    for path in os.environ.get("PATH", "").split(os.pathsep):
        try:
            os.add_dll_directory(path)
        except OSError:
            pass


def fix_cairo():
    set_dll_search_path()
    if find_library("libcairo-2"):
        return
    else:
        choice = input(fix_cairo_long_intro).lower()
        if choice == "y" or choice == "":
            GTK_installer = os.path.join(
                mathicsscript_path, "gtk3-runtime-3.24.31-2022-01-04-ts-win64.exe"
            )
            # download_GTK_installer()
            GTK_install_cmd = os.path.join(mathicsscript_path, "install_GTK.cmd")
            with open(os.path.join(mathicsscript_path, "install_GTK.cmd"), "w") as file:
                file.write(f'"{GTK_installer}"')
            subprocess.run(
                GTK_install_cmd
            )  # Allow users to run installer as administrators
            os.remove(GTK_install_cmd)
            set_dll_search_path()
            if os.path.exists(default_GTK_path):
                os.environ["PATH"] += os.pathsep + default_GTK_path
            if find_library("libcairo-2"):
                print("Successfully fixed cairocffi for mathicsscript.")
            else:
                print(
                    "Please restart the current terminal to make the changes take effect."
                )
