"""
Fix cairo for Windows, Python 3.8+
"""

import os
import requests
import sys

cairo_libs_path = "./libs"

def download_file(url, dest):
    response = requests.get(url, timeout=5)
    if response.status_code == 200:
        with open(dest, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded: {dest}")
    else:
        print(f"Failed to download: {url}")

def download_cairo_libs():
    branch_url = "https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/tree/master/"
    directory_url = "gtk-nsis-pack/bin"
    response = requests.get(branch_url + directory_url + "?recursive=1", timeout = 5)
    if response.status_code == 200:
        data = response.json()
        for item in data['payload']['tree']['items']:
            if '.dll' not in item['name']:
                continue
            file_url = branch_url + item['path']
            file_path = os.path.join(cairo_libs_path, item['name'])
            download_file(file_url, file_path)
    else:
        print("Failed to retrieve directory contents.")

def set_dll_search_path():
    # Python 3.8+ no longer searches for DLLs in PATH, so we have to add
    # everything in PATH manually. Note that unlike PATH add_dll_directory
    # has no defined order, so if there are two cairo DLLs in PATH we
    # might get a random one.
    if os.name != "nt" or not hasattr(os, "add_dll_directory"):
        return
    try:
        os.add_dll_directory(cairo_libs_path)
    except OSError:
        pass


if sys.version_info >= (3, 8) and os.name == 'nt' and not os.path.exists(cairo_libs_path):
    os.makedirs(cairo_libs_path)
    download_cairo_libs()
    set_dll_search_path()
