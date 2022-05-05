"""Contains the FileStructure class.


Author: Kevin Hodge
"""

from typing import Any, List, Tuple, Optional, Dict
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
        self.files: Dict[str, Any] = dict()
        self.last_update: Dict[str, Any] = dict()
        self.updated: Dict[str, Any] = dict()
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
        self.recursive_print_dict(self.files, offset)

    def print_last_update(self, offset: int = 0) -> None:
        """Prints self.last_update

        Calls recursive_print_list with self.last_update as an argument.

        """
        # print(self.last_update)
        self.recursive_print_dict(self.last_update, offset)

    def recursive_get_directory(self, directory: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Recursive function that gives the structure of all files and folder contained within a directory.

        Args:
            directory (str): Path to the directory.

        Returns:
            file_structure (list): list of one string and one list that contains entries in the directory, directories
            in the directory are represented as lists that also contain a string with the name of directory and another
            list with entries in that directory, pattern continues until no sub-directories are found.

            ex. ["dir_name", ["file1.txt", ["sub_dir_name", ["file2.txt", "file3.txt"]], "file4.txt"]]
            ex. {"dir_name": {"file1.txt", {"sub_dir_name": {"file2.txt", "file3.txt"}}, "file4.txt"}}

        """
        assert isinstance(directory, str)

        dir_name: str = os.path.split(directory)[1]
        dir_time: float = os.stat(directory).st_mtime
        file_structure: Dict[str, Any] = {dir_name: dict()}
        last_updates: Dict[float, Any] = {dir_time: dict()}
        for entry in os.listdir(directory):
            entry_path: str = os.path.join(directory, entry)
            if os.path.isfile(entry_path):
                file_structure[entry] = os.stat(entry_path).st_mtime
                last_updates[os.stat(entry_path).st_mtime] = None
            elif os.path.isdir(entry_path):
                sub_dir: Dict[str, Any]
                sub_updates: Dict[float, Any]
                sub_dir, sub_updates = self.recursive_get_directory(entry_path)
                file_structure[entry] = sub_dir
                last_updates[os.stat(entry).st_mtime] = sub_updates
            else:
                raise ValueError("Directory entry is not a file or directory")
        return file_structure, last_updates

    def recursive_print_dict(self, files_dict: Dict[Any, Any], offset: int = 0) -> None:
        """Prints out dict that matches format of FileStructure.files.

        Args:
            files_dict (dict): List that matches the format of FileStructure.files.
            offset (int): Tracks the depth of the directory and directory vs. file list.

        """
        indent: str = 3 * offset * ' '  # indent made for each directory level
        for entry in files_dict:
            print(f"{indent}{entry}")
            if isinstance(files_dict[entry], dict):
                self.recursive_print_dict(files_dict[entry], offset + 1)

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
        folder_path: str = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
        last_sync_file: str = "last_sync_file.json"
        last_sync_path: str = os.path.join(folder_path, last_sync_file)
        last_sync_files: Dict[str, Any] = dict()
        last_sync_time: float = 0.0
        if os.path.exists(last_sync_path):
            last_sync_data: List[Dict[Any], int] = list()
            with open(last_sync_path, "r") as json_file:
                last_sync_data = json.load(json_file)
                if self.verbose:
                    print("Read last_sync_file.json")
                json_file.close()
            last_sync_files = last_sync_data[0]
            last_sync_time = last_sync_data[1]
        else:
            if self.verbose:
                print("No last_sync_file found.")

        self.updated = dict()  # empty updated of any previous information
        return self.fill_updated(last_sync_files, last_sync_time)

    def fill_updated(self, last_sync_files: Dict[str, Any], last_sync_time: float, depth: int = 0,
                     path: Optional[List[str]] = None, change_found: bool = False) -> bool:
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
        pass

    def update_file_structure(self) -> None:
        pass
