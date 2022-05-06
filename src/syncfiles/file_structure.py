"""Contains the FileStructure class.


Author: Kevin Hodge
"""

from typing import Any, List, Tuple, Optional, Dict
from pathlib import Path


class FileStructure:
    """Contains information about a sync directory.

    Requirements:
        - Req #4: The program shall retrieve the names and file structure of all files and folders in both directories.
        - Req #10: File structures shall be stored in a class "FileStructure".

    Attributes:
        directory_path (str): Contains the path to the directory that the FileStructure represents.
        files (dict): Contains names of all files (strings) and all folders (dict with entries corresponding to the
            files and directories in the directory) in the directory. Folders contained in dicts, contain names of all
            files and folders in those folders, pattern continues until a directory with no folders is found.
        ex. {"dir_name": {"file1.txt", {"sub_dir_name": {"file2.txt", "file3.txt"}}, "file4.txt"}}
        last_update (dict): Same structure as files, contains last modification times of each file in self.files.
        updated (dict): Same structure as files, each entry corresponds to an entry in self.files. Contains True if file
            or folder has last_update time greater than last_sync_time or False otherwise (assumes no change to the file
            or folder).
        verbose (bool): Indicates if messages will be printed for debugging.

    """
    def __init__(self, directory_path: str, verbose: bool = False) -> None:
        assert Path(directory_path).exists()
        self.directory_path: str = directory_path
        self.files: Dict[str, Any] = dict()
        self.last_update: Dict[float, Any] = dict()
        self.updated: Dict[str, Any] = dict()
        self.verbose: bool = verbose

    def get_file_structure(self) -> Dict[str, Any]:
        """Reads all files and folders below the directory.

        Calls recursive_get_directory.

        Returns:
            self.files (dict): Structure of this dictionary is described in the arguments documentation of
                FileStructure.

        """
        self.files, self.last_update = self.recursive_get_directory(self.directory_path)
        return self.files

    def print_file_structure(self, offset: int = 1) -> None:
        """Prints self.files.

        Calls recursive_print_list with self.files as an argument.

        Args:
            offset (int): indicates the depth of the directory and the indention used to print the file/folder.

        """
        print(Path(self.directory_path).name)
        self.recursive_print_dict(self.files, offset)

    def print_last_update(self, offset: int = 1) -> None:
        """Prints self.last_update

        Calls recursive_print_list with self.last_update as an argument.

        """
        print(Path(self.directory_path).stat().st_mtime)
        self.recursive_print_dict(self.last_update, offset)

    def recursive_get_directory(self, directory: str) -> Tuple[Dict[str, Any], Dict[float, Any]]:
        """Recursive function that gives the structure of all files and folder contained within a directory.

        Args:
            directory (str): Path to the directory.

        Returns:
            file_structure (Dict[str, Any]): Same structure as FileStructure.files.
                ex. {"dir_name": {"file1.txt", {"sub_dir_name": {"file2.txt", "file3.txt"}}, "file4.txt"}}
            last_updates (Dict[float, Any]): Same structure as FleStructure.last_updates.

        """
        assert Path(directory).exists()

        file_structure: Dict[str, Any] = dict()
        last_updates: Dict[float, Any] = dict()
        for entry in Path(directory).iterdir():
            if Path(entry).is_file():
                file_structure[entry.name] = Path(entry).stat().st_mtime
                last_updates[Path(entry).stat().st_mtime] = None
            elif Path(entry).is_dir():
                sub_dir: Dict[str, Any]
                sub_updates: Dict[float, Any]
                sub_dir, sub_updates = self.recursive_get_directory(str(entry))
                file_structure[entry.name] = sub_dir
                last_updates[Path(entry).stat().st_mtime] = sub_updates
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
        for entry, value in files_dict.items():
            if isinstance(files_dict[entry], dict):
                print(f"{indent}{entry}")
                self.recursive_print_dict(files_dict[entry], offset + 1)
            else:
                print(f"{indent}{entry}: {value}")

    def check_file_structure(self, last_sync_files: Dict[str, Any], last_sync_time: float,
                             path: Optional[List[str]] = None, change_found: bool = False) -> bool:
        """Checks for updates within the self.files since the last sync and fills self.updated.

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
        # Reset updated just in case
        if path is None:
            self.updated = dict()

        # Check values and mark as updated if necessary

        return change_found

    def get_dict_value(self, path: List[str]):
        pass

    def set_dict_value(self, path: List[str], value: Any):
        pass

    def update_file_structure(self) -> None:
        pass
