"""Contains FileStructure class and functions interacting with files and directories.


Author: Kevin Hodge
"""

from typing import Any, List, Tuple, Optional, Callable, cast
import os
import time
import functools
import json


def sleep_decorator(func: Callable[..., Any]) -> Callable[..., Any]:
    """Sleep decorator function that currently does nothing.

    Args:
        func (function): Function to be decorated.

    Returns:
        wrapper (function): Decorated function.

    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Do Something
        return func(*args, **kwargs)
        # Do Something

    return cast(Callable[..., Any], wrapper)


@sleep_decorator
def fsm_sleep(seconds: float) -> None:
    """Decorates sleep function from time module.

    Args:
        seconds (int): Time to sleep in seconds.

    """
    time.sleep(seconds)


def get_sync_directories(min_dir: int = 2) -> List[str]:
    """Gets directories to be synchronized from config file and/or from user.

    Requirements:
        - Req #2: The program shall find sync_directories_file.json (json file containing the sync directories).
        - Req #3: The program shall open and read sync_directories_file.json.
        - Req #15: The program shall store and get sync directories from a config file.
        - Req #16: The program shall ask user for directories if config file does not contain sync directories.

    Finds sync_directories_file.json file in parent directory of working directory, reads entries, and returns list
    with strings containing valid, unique directories.

    Function checks for the following and removes directory if any are true:
        - Config File Doesn't exist
        - Sync Directory(s) don't exist
        - Sync Directories are not string instances

    Note:
        Tested only on M1 Mac and Windows 10.

    Args:
        gui (SyncGUI): Graphical User Interface for the program.
        verbose (bool, optional): Indicates if messages will be printed for debugging.

    Returns:
        buffer (list[str]): Existing, unique directories found in "sync_directories_file.json".

    """
    # Find and read sync_directories_file
    file_path: str = os.path.join(os.getcwd(), "sync_directories_file.json")

    # Read file (with ensures file is closed even if an exception occurs)
    buffer: List[str] = list()
    if os.path.exists(file_path):
        with open(file_path, "r") as file_to_read:
            buffer = json.load(file_to_read)
            file_to_read.close()

    # Ensures buffer is the right datatype
    if not type(buffer) == list:
        buffer = []

    # Removes invalid directories from buffer
    for entry in buffer:
        if not os.path.exists(entry) or not isinstance(entry, str):
            buffer.remove(entry)

    return buffer


def set_sync_directory(new_dir: str, existing_dirs: List[str], min_dir: int = 2) -> List[str]:
    """Checks directory provided by user and if valid and unique, adds to sync_directories.

    Requirements:
        - Req #17: The program shall update config file with directory provided by user (if it exists).

    Checks for:
        - Sync Directories are unique
        - Sync Directories exist

    Args:
        new_dir (str): _description_
        existing_dirs (List[str]): _description_

    Returns:
        int: _description_
    """
    unique: bool = True
    if new_dir in existing_dirs:
        unique = False
    if os.path.exists(new_dir) and unique:
        existing_dirs.append(new_dir)

    # Find and read sync_directories_file
    file_path: str = os.path.join(os.getcwd(), "sync_directories_file.json")

    # Creates and writes or overwrites JSON config file if User inputs new directories to sync
    if len(existing_dirs) >= min_dir:
        with open(file_path, "w") as file_to_write:
            json.dump(existing_dirs, file_to_write)
            file_to_write.close()

    return existing_dirs


def recursive_get_directory(directory: str) -> Tuple[List[Any], List[Any]]:
    """Recursive function that gives the structure of all files and folder contained within a directory.

    Args:
        directory (str): Path to the directory.

    Returns:
        file_structure (list): list of one string and one list that contains entries in the directory, directories in
            the directory are represented as lists that also contain a string with the name of directory and another
            list with entries in that directory, pattern continues until no sub-directories are found.

        ex. ["dir_name", ["file1.txt", ["sub_dir_name", ["file2.txt", "file3.txt"]], "file4.txt"]]
        ex. {"dir_name": ["file1.txt", {"sub_dir_name": ["file2.txt", "file3.txt"]}, "file4.txt"]}

    """
    assert isinstance(directory, str)

    file_structure: List[Any] = [os.path.split(directory)[1], list()]  # This should work on most OSes
    last_updates: List[Any] = [os.stat(directory).st_mtime, list()]
    for entry in os.listdir(directory):
        entry_path: str = os.path.join(directory, entry)
        if os.path.isfile(entry_path):
            file_structure[1].append(entry)
            last_updates[1].append(os.stat(entry_path).st_mtime)
        elif os.path.isdir(entry_path):
            sub_dir: List[Any]
            sub_updates: List[Any]
            sub_dir, sub_updates = recursive_get_directory(entry_path)
            file_structure[1].append(sub_dir)
            last_updates[1].append(sub_updates)
        else:
            raise ValueError("Directory entry is not a file or directory")
    return file_structure, last_updates


def recursive_print_list(files_list: List[Any], offset: int = 0) -> None:
    """Prints out list that matches format of FileStructure.files.

    Args:
        files_list (list): List that matches the format of FileStructure.files.
        offset (int): Tracks the depth of the directory and directory vs. file list.

    """
    indent: str = 3 * offset * ' '  # indent made for each directory level
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
    """Contains information about a sync directory.

    Requirements:
        - Req #4: The program shall retrieve the names and file structure of all files and folders in both directories.
        - Req #10: File structures shall be stored in a class "FileStructure".

    Attributes:
        directory_path (str): Contains the path to the directory that the FileStructure represents.
        files (list): Contains the structure of the FileStructure, structure described in recursive_get_directory.
        last_update (list): Same structure as files, contains last modification times of each file in self.files.
        updated (list): Same structure as files, each entry corresponds to an entry in self.files. Contains True if file
            or folder has last_update time greater than last_sync_time or False otherwise (assumes no change to the file
            or folder).
        verbose (bool): Indicates if messages will be printed for debugging.

    """

    def __init__(self, directory_path: str, verbose: bool = False) -> None:
        assert len(directory_path) > 0

        self.directory_path: str = directory_path
        self.files: List[Any] = list()
        self.last_update: List[Any] = list()
        self.updated: List[Any] = list()
        self.verbose: bool = verbose

    def get_file_structure(self) -> List[Any]:
        """Reads all files and folders below the directory.

        Calls recursive_get_directory.

        Returns:
            self.files (list): self.files contains paths to all files (strings) and all folders (list, with two
                elements, name of folder and list containing all entries in directory) in the directory. folders
                contained in files, contain names of all files and folders in those folders, pattern continues until a
                directory with no folders is found.

        """
        self.files, self.last_update = recursive_get_directory(self.directory_path)
        return self.files

    def print_file_structure(self, offset: int = 0) -> None:
        """Prints self.files.

        Calls recursive_print_list with self.files as an argument.

        """
        # print(self.files)
        recursive_print_list(self.files, offset)

    def print_last_update(self, offset: int = 0) -> None:
        """Prints self.last_update

        Calls recursive_print_list with self.last_update as an argument.

        """
        # print(self.last_update)
        recursive_print_list(self.last_update, offset)

    def check_file_structure(self) -> bool:
        """Checks for updates within the self.files since the last sync.

        Requirements:
            - TODO Req #18: The program shall load last_sync_files and last_sync_time from config file.
            - TODO Req #14: The program shall check if last_update is greater than last_sync_time (if it exists).
            - TODO Req #12: The program shall determine the files and folders that have been updated.

        TODOs:
            - TODO: If entry exists in self.files but not in last_sync_files, set entry in self.updated to True
            - TODO: If exists in both last_sync_files and self.files and the entry is a file, compare last_sync_time to
                self.last_update, if greater, set entry in self.updated to True (updated)
            - TODO: All other entries in self.updated should be False (no change, default)

        """
        # Check if last_updates_file exists
        # Retrieve last_sync_files and last_sync_time for each entry in files
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

        self.updated = []  # empty updated of any previous information
        return self.fill_updated(last_sync_files, last_sync_time)

    def fill_updated(self, last_sync_files: List[Any], last_sync_time: float, depth: int = 0,
                     index: Optional[List[Any]] = None, change_found: bool = False) -> bool:
        """Fills self.updated.

        TODOs:
            TODO: Need to track the index of the entry to figure out corresponding entries in other lists.

        Arguments:
            last_sync_files (list): Files list from last sync config file.
            last_sync_time (float): Time in seconds of last update.
            depth (int): Tracks if the entry is a file or folder and depth of the entry.
            change_found (bool): Initializes output value and allows value to be passed through recursive calls.

        Returns:
            change_found (bool): Indicates that at least one file or folder has been updated.

        """
        # if index is None:
        #     index = [0]
        # for entry in file_list:
        #     if depth % 2 == 1: # entry is a file
        #
        #     else: # entry is a directory
        #
        # return change_found

    def update_file_structure(self) -> None:
        pass
