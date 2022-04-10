"""
FileStruture Functions
-----------------------------
Contains the functions for the Sync Files Project.
"""

import os
import time
import functools
import json


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
    last_updates = [os.stat(directory).st_mtime, []]
    for entry in os.listdir(directory):
        entry_path = os.path.join(directory, entry)
        if os.path.isfile(entry_path):
            file_structure[1].append(entry)
            last_updates[1].append(os.stat(entry_path).st_mtime)
        elif os.path.isdir(entry_path):
            sub_dir, sub_updates = recursive_get_directory(entry_path)
            file_structure[1].append(sub_dir)
            last_updates[1].append(sub_updates)
        else:
            return
    return file_structure, last_updates


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


def recursive_print_updates(last_updates, offset=0):
    """
    Prints out directory and files and directories if file_structure matches format given in recursive_get_directory
    :param last_updates:
    :param offset:
    :return file_structure:
    """
    for entry in last_updates:
        if type(entry) == float:
            print(offset * " " + str(entry))
        else:
            recursive_print_updates(entry, offset + 3)


class FileStructure:
    """
    Req #4: The program shall retrieve the names and file structure of all files and folders in both directories.
    Req #10: File structures shall be stored in a class "FileStructure".
    class that contains the file structure of a directory.
    FileStructure Variables
        directory_path: string
            string contains the path to the directory that contains the FileStructure
        files: list
            data structure that contains the structure of the FileStructure, structure described in
            recursive_get_directory
        to_update: list
            same structure as files, contains entries to update

    """

    def __init__(self, directory_path, verbose=False):
        self.directory_path = directory_path
        self.files = list()
        self.last_updates = list()
        self.to_update = list()
        self.verbose = verbose
        pass

    def get_file_structure(self):
        """
        Reads all files and folders below the directory
        :return:
        self.files: list
            self.files contains paths to all files (strings) and all folders (list, with two elements, name of folder '
            and list containing all entries in directory) in the directory. folders contained in files, contain names of
            all files and folders in those folders, pattern continues until a directory with no folders is found.
        """
        self.files, self.last_updates = recursive_get_directory(self.directory_path)
        print(self.last_updates)
        return self.files

    def print_file_structure(self, offset=0):
        """

        :param offset:
        :return:
        """
        recursive_print_directory(self.files, offset)

    def print_last_updates(self, offset=0):
        """

        :param offset:
        :return:
        """
        recursive_print_updates(self.last_updates, offset)

    def check_file_structure(self):
        """
        TODO Req #14: The program check if the most recently updated time matches last sync time (if it exists).
        TODO Req #12: The program shall determine the files and folders that have been most recently updated.

        :return:
        """
        # Check if last_updates_file exists, if not indicate first_sync
        first_sync = True
        last_update_file = "last_update_file.json"
        if os.path.exists(last_update_file):
            first_sync = False
            if self.verbose:
                print("First Sync")

        # TODO: Parse last_updated_file and retrieve last updated time for each entry in files (last_sync)
        last_sync_file_data = []
        if not first_sync:
            with open(last_update_file, "r") as json_file_data:
                last_sync_file_data = json.load(json_file_data)
                if self.verbose:
                    print("Read last_sync_file.json")

        # TODO: Check actual last update times for each entry in files (last_update)


        # TODO: Compare last_sync to last_update and store differences in self.to_update


    def update_file_structure(self):
        """
        # TODO Req #5: The program shall determine the Most_Recently_Updated_Directory and the To_Sync_Directory.
        # TODO Req #6: The program shall copy all files in the Most_Recently_Updated_Directory to the To_Sync_Directory.

        :return:
        """
        pass
