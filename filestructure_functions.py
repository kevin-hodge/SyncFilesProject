"""
FileStructure Functions
-----------------------------
Contains functions used by the FileStructure class.
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


def get_sync_directories(gui, verbose=False):
    """
    - Req #2: The program shall find sync_directories_file.json (json file containing the sync directories).
    - Req #3: The program shall open and read sync_directories_file.txt.
    - Req #15: The program shall store and get sync directories from a config file.
    - Req #16: The program shall ask user for directories if config file does not contain sync directories.
    - Req #17: The program shall update config file with directory provided by user (if it exists).
    Finds sync_directories_file.json file in parent directory of working directory, reads entries, and returns list
    with strings containing valid, unique directories.
    Function checks for the following and asks user to provide valid, unique directories if any are true:
    - Config File Doesn't exist
    - Sync Directory(s) don't exist
    - Not enough sync directories (at least 2)
    - Sync Directories are not unique

    :return:
    file_directories: list(string)
        list of file directories found in "sync_directories_file.json"

    Caveat: Tested only on M1 Mac and Windows 10
    """
    # Find and read sync_directories_file
    folder_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))  # get parent directory of current directory
    file_name = "sync_directories_file.json"
    file_path = os.path.join(folder_path, file_name)

    # Read file (with ensures file is closed even if an exception occurs)
    min_directories = 2  # Minimum of 2 directories, otherwise no sync can occur
    buffer = []
    write_config = False
    if os.path.exists(file_path):
        with open(file_path, "r") as file_to_read:
            buffer = json.load(file_to_read)
            file_to_read.close()

    if not type(buffer) == list:
        buffer = []

    for i in range(len(buffer)):
        if not os.path.exists(buffer[i]):
            buffer.pop(i)

    for dir_num in range(min_directories-len(buffer)):
        while True:
            new_dir = gui.directory_prompt(buffer)
            unique = True
            for i in range(len(buffer)):
                if new_dir == buffer[i]:
                    unique = False
            if os.path.exists(new_dir) and unique:
                buffer.append(new_dir)
                print(f"Directory added to sync directories config file: {str(buffer[-1])}")
                break
        write_config = True

    if write_config:
        with open(file_path, "w") as file_to_write:
            json.dump(buffer, file_to_write)
            file_to_write.close()

    # Parse directory paths and return list of directories
    return buffer


def recursive_get_directory(directory):
    """
    Recursive function that gives the structure of all files and folder contained within a directory
    :param directory: string
        path to the directory
    :return file_structure: list
        list of one string and one list that contains entries in the directory, directories in the directory are
        represented as lists that also contain a string with the name of directory and another list with entries in that
        directory, pattern continues until no directories are found
        ex. ["dir_name", ["file1.txt", ["sub_dir_name", ["file2.txt", "file3.txt"]], "file4.txt"]]
        ex. {"dir_name": ["file1.txt", {"sub_dir_name": ["file2.txt", "file3.txt"]}, "file4.txt"]}
    """
    assert type(directory) == str

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


def recursive_print_list(files_list, offset=0):
    """
    Prints out list that matches format of FileStructure.files

    inputs
        files_list: list
            list that matches the format of FileStructure.files

        offset: int
            variable used to track the depth of the directory and directory vs. file list
    """
    indent = 3 * offset * ' '  # indent made for each directory level
    for entry in files_list:
        if isinstance(entry, list):
            if offset % 2 == 1:  # directory list
                print(f"{indent}{entry[0]}")
                recursive_print_list(entry[1], offset + 1)
            else:  # file list
                recursive_print_list(entry, offset + 1)
        else:
            print(f"{indent}{entry}")


class FileStructure:
    """
    Req #4: The program shall retrieve the names and file structure of all files and folders in both directories.
    Req #10: File structures shall be stored in a class "FileStructure".
    class that contains the file structure of a directory.

    :variables:
        directory_path: string
            string contains the path to the directory that contains the FileStructure
        files: list
            data structure that contains the structure of the FileStructure, structure described in
            recursive_get_directory
        last_update: list
            same structure as files, contains last modification times of each file in self.files
        updated: list
            same structure as files, each entry corresponds to an entry in self.files
            contains True if file or folder has last_update time greater than last_sync_time or False otherwise (assumes
            no change to the file or folder)
    """

    def __init__(self, directory_path, verbose=False):
        self.directory_path = directory_path
        self.files = list()
        self.last_update = list()
        self.updated = list()
        self.verbose = verbose
        pass

    def get_file_structure(self):
        """
        Reads all files and folders below the directory
        :return:
        self.files: list
            self.files contains paths to all files (strings) and all folders (list, with two elements, name of folder
            and list containing all entries in directory) in the directory. folders contained in files, contain names of
            all files and folders in those folders, pattern continues until a directory with no folders is found.
        """
        self.files, self.last_update = recursive_get_directory(self.directory_path)
        return self.files

    def print_file_structure(self, offset=0):
        """
        Prints self.files
        """
        # print(self.files)
        recursive_print_list(self.files, offset)

    def print_last_update(self, offset=0):
        """
        Prints self.last_update
        :param:

        """
        # print(self.last_update)
        recursive_print_list(self.last_update, offset)

    def check_file_structure(self):
        """
        TODO Req #18: The program shall load last_sync_files and last_sync_time from config file.
        TODO Req #14: The program shall check if last_update is greater than last_sync_time (if it exists).
        TODO Req #12: The program shall determine the files and folders that have been updated.
        Checks for updates within the self.files since the last sync.
        """
        # Check if last_updates_file exists
        # Parse last_updated_file and retrieve last_sync_time for each entry in files
        folder_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))  # get parent directory of current directory
        last_sync_file = "last_sync_file.json"
        last_sync_path = os.path.join(folder_path, last_sync_file)
        last_sync_files = []
        last_sync_time = 0
        if os.path.exists(last_sync_path):
            last_sync_data = []
            with open(last_sync_path, "r") as json_file:
                last_sync_data = json.load(json_file)
                if self.verbose:
                    print("Read last_sync_file.json")
                json_file.close()
            last_sync_files = last_sync_data[0]
            last_sync_time = last_sync_data[1]
        else:
            if self.verbose:
                print("First Sync")

        # TODO: If entry exists in self.files but not in last_sync_files, set entry in self.updated to True (updated)
        # TODO: If exists in both last_sync_files and self.files and the entry is a file, compare last_sync_time to
        #  self.last_update, if greater, set entry in self.updated to True (updated)
        # TODO: All other entries in self.updated should be False (no change, default)
        self.updated = []  # empty updated of any previous information
        return self.fill_updated(last_sync_files, last_sync_time)

    def fill_updated(self, file_list, last_sync_time, depth=0, index=None, change_found=False):
        """
        TODO: Need to track the index of the entry to figure out corresponding entries in other lists
        Fills self.updated
        inputs
            file_list:

            last_sync_time: float
                time in seconds of last update
            depth: int
                tracks if the entry is a file or folder and depth of entry
            change_found: boolean
                initialize output value and allows value to be passed through recursive calls

        returns
            change_found: boolean
                indicates that at least one file or folder has been updated
        """
        # if index is None:
        #     index = [0]
        # for entry in file_list:
        #     if depth % 2 == 1: # entry is a file
        #
        #     else: # entry is a directory
        #
        # return change_found

    def update_file_structure(self):
        """

        """
        pass

