"""Contains FileStructure class and functions interacting with files and directories.


Author: Kevin Hodge
"""

from typing import Any, List, Tuple, Optional
import os
import json


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
        self.files, self.last_update = self.recursive_get_directory(self.directory_path)
        return self.files

    def print_file_structure(self, offset: int = 0) -> None:
        """Prints self.files.

        Calls recursive_print_list with self.files as an argument.

        """
        # print(self.files)
        self.recursive_print_list(self.files, offset)

    def print_last_update(self, offset: int = 0) -> None:
        """Prints self.last_update

        Calls recursive_print_list with self.last_update as an argument.

        """
        # print(self.last_update)
        self.recursive_print_list(self.last_update, offset)

    def recursive_get_directory(self, directory: str) -> Tuple[List[Any], List[Any]]:
        """Recursive function that gives the structure of all files and folder contained within a directory.

        Args:
            directory (str): Path to the directory.

        Returns:
            file_structure (list): list of one string and one list that contains entries in the directory, directories
            in the directory are represented as lists that also contain a string with the name of directory and another
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
                sub_dir, sub_updates = self.recursive_get_directory(entry_path)
                file_structure[1].append(sub_dir)
                last_updates[1].append(sub_updates)
            else:
                raise ValueError("Directory entry is not a file or directory")
        return file_structure, last_updates

    def recursive_print_list(self, files_list: List[Any], offset: int = 0) -> None:
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
                    self.recursive_print_list(entry[1], offset + 1)
                else:  # file list
                    self.recursive_print_list(entry, offset + 1)
            else:
                print(f"{indent}{entry}")

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
