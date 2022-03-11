"""
Sync Files Project: Functions
-----------------------------
Contains the functions for the Sync Files Project.
"""


import os
import sys


def get_working_directory():
    """
    Gets the current working directory.
    :return: string
        current working directory
    """
    return os.getcwd()


def get_sync_directories():
    """
    # Req #2: The program shall find sync_directories_file.txt (text file containing the sync directories).
    # Req #3: The program shall open and read sync_directories_file.txt.
    Finds sync_directories_file.txt file in working directory, reads entries, and returns tuple with string values
    :return:
    file_directories: list(string)
        list of file directories found in "sync_directories_file.txt"

    Idea: Currently this only works on MacOS, can I somehow figure out the os and implement both ways?
    """
    # Find and read sync_directories_file
    folder_path = os.getcwd()
    file_name = "sync_directories_file.txt"  # should store this value somewhere else eventually
    file_path = folder_path + "/" + file_name
    with open(file_path) as file_to_read:  # with ensures file is closed even if an exception occurs
        buffer = file_to_read.read()

    # Parse directory paths and return list of directories
    file_directories = [""]
    for letters in buffer:
        if not letters == "\n":
            file_directories[-1] += letters
        else:
            file_directories.append("")
    return file_directories
