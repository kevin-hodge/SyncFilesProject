"""
FileStruture Functions
-----------------------------
Contains the functions for the Sync Files Project.
"""

import os
import time
import functools


def sleep_decorator(func):
    """
    Decorator function that currently does nothing.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Do Something
        return func(*args, **kwargs)
        # Do Something

    return wrapper


@sleep_decorator
def fsm_sleep(seconds):
    time.sleep(seconds)


def get_sync_directories():
    """
    # Req #2: The program shall find sync_directories_file.txt (text file containing the sync directories).
    # Req #3: The program shall open and read sync_directories_file.txt.
    Finds sync_directories_file.txt file in working directory, reads entries, and returns tuple with string values

    ASSUMES: sync_directories_file structure is directory paths separated by newline characters

    :return:
    file_directories: list(string)
        list of file directories found in "sync_directories_file.txt"

    Caveat: Only tested on macOS, hopefully should work on Windows, but not confirmed yet
    """
    # Find and read sync_directories_file
    folder_path = os.getcwd()  # get working directory
    file_name = "sync_directories_file.txt"  # should store this value somewhere else eventually, what if this changes?
    file_path = os.path.join(folder_path, file_name)

    # Read file (with ensures file is closed even if an exception occurs)
    with open(file_path) as file_to_read:
        buffer = file_to_read.read()

    # Parse directory paths and return list of directories
    return buffer.split("\n")


def recursive_get_directory(directory):
    """
    Recursive function that gives the structure of all files and folder contained within a directory
    :param directory: string
        path to the directory
    :return file_structure: list
        list of one string and one list that contains entries in the directory, directories in the directory are
        represented as lists that also contain a string with the name of directory and another list with entries in that
        directory, pattern continues until no directories are found
        ex. ["dir_name", ["file1.txt", ["sub_dir_name", ["file2.txt", ["sub_sub_dir_name", [...]]], "file3.txt"]]
    """
    assert type(directory) == str

    # file_structure = [directory.split("/")[-1], []]  # This only works on macOS
    file_structure = [os.path.split(directory)[1], []]  # This should work on most OSes
    for entry in os.listdir(directory):
        entry_path = os.path.join(directory, entry)
        if os.path.isfile(entry_path):
            file_structure[1].append(entry)
        elif os.path.isdir(entry_path):
            sub_dir = recursive_get_directory(entry_path)
            file_structure[1].append(sub_dir)
        else:
            return
    return file_structure


def recursive_print_directory(file_structure, offset=0):
    """
    Prints out directory and files and directories if file_structure matches format given in recursive_get_directory
    :param file_structure:
    :param offset:
    :return file_structure:
    """
    for entry in file_structure:
        if type(entry) == str:
            print(offset * " " + entry)
        else:
            recursive_print_directory(entry, offset + 3)


class FileStructure:
    """
    Req #4: The program shall retrieve the names and file structure of all files and folders in both directories.
    Req #10: File structures shall be stored in a class "FileStructure".
    class that contains the file structure of a directory.
    FileStructure Variables
        directory_path

    """

    def __init__(self, directory_path):
        self.directory_path = directory_path
        self.files = list()
        pass

    def get_file_structure(self):
        """
        Reads all files and folders below the directory
        :return:
        self.files: list
            self.files contains paths to all files (strings) and all folders (list, with two elements, ) in the
            directory. folders contained in files, contain names of all files and folders in those folders,
            pattern continues until a directory with no folders is found.
        """
        self.files = recursive_get_directory(self.directory_path)
        return self.files

    def print_file_structure(self, offset=0):
        recursive_print_directory(self.files, offset)

    def update(self):
        """
        # TODO Req #5: The program shall determine the Most_Recently_Updated_Directory and the To_Sync_Directory.
        # TODO Req #6: The program shall copy all files in the Most_Recently_Updated_Directory to the To_Sync_Directory.

        :return:
        """
        pass
