# miscellaneous functions

import os
import platform
import streamlit as st


def make_path(file_path,file):
    system = platform.system()
    if system == 'Windows':
        delimiter = "\\"
    else:
        delimiter = "/"

    split_path = file_path.split(delimiter)
    return delimiter.join(split_path) + delimiter + file


def get_folder_from_path(file_path):
    system = platform.system()
    if system == 'Windows':
        delimiter = "\\"
    else:
        delimiter = "/"

    split_path = file_path.split(delimiter)[:-1]
    return delimiter.join(split_path)