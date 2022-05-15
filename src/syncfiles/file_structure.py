"""Contains the FileStructure class.


Author: Kevin Hodge
"""

from typing import Any, List, Optional, Dict
from pathlib import Path


class dir_entry(Dict[str, Any]):
    def __init__(self, *args, **kwargs):
        self.mtime: float = float()
        self.updated: bool = False
        super().__init__(*args, **kwargs)


class file_entry(float):
    def __init__(self, *args, **kwargs):
        self.updated: bool = False


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
        self.path_list = self.split_path(self.directory_path)
        self.files: dir_entry = dir_entry(dict())
        # self.files: Dict[str, Any] = dict()
        # self.last_update: Dict[float, Any] = dict()
        # self.updated: Dict[str, Any] = dict()
        self.verbose: bool = verbose

    def get_file_structure(self) -> Dict[str, Any]:
        """Reads all files and folders below the directory.

        Calls recursive_get_directory.

        Returns:
            self.files (dict): Structure of this dictionary is described in the arguments documentation of
                FileStructure.

        """
        self.files = self.recursive_get_directory(self.directory_path)
        return self.files

    def print_file_structure(self, offset: int = 1) -> None:
        """Calls recursive_print_list with self.files as an argument."""
        print(Path(self.directory_path).name)
        self.recursive_print_dict(self.files, offset)

    def recursive_get_directory(self, directory: str) -> dir_entry:
        """Recursive function that gives the structure of all files and folder contained within a directory.

        Args:
            directory (str): Path to the directory.

        Returns:
            file_structure (Dict[str, Any]): Same structure as FileStructure.files.
                ex. {"dir_name": {"file1.txt", {"sub_dir_name": {"file2.txt", "file3.txt"}}, "file4.txt"}}
            last_updates (Dict[float, Any]): Same structure as FleStructure.last_updates.

        """
        assert Path(directory).exists()

        file_structure: dir_entry = dir_entry(dict())
        for entry in Path(directory).iterdir():
            if Path(entry).is_file():
                file_structure[entry.name] = file_entry(Path(entry).stat().st_mtime)
            elif Path(entry).is_dir():
                file_structure[entry.name] = dir_entry(self.recursive_get_directory(str(entry)))
                file_structure[entry.name].mtime = Path(entry).stat().st_mtime
            else:
                raise ValueError("Directory entry is not a file or directory")
        return file_structure

    def recursive_print_dict(self, files_dict: dir_entry, offset: int = 0) -> None:
        """Prints out dict that matches format of FileStructure.files.

        Args:
            files_dict (dict): List that matches the format of FileStructure.files.
            offset (int): Tracks the depth of the directory and directory vs. file list.

        """
        indent: str = 3 * offset * ' '  # indent made for each directory level
        for key, value in files_dict.items():
            if isinstance(files_dict[key], dict):
                print(f"{indent}{key}: {value.mtime}")
                self.recursive_print_dict(files_dict[key], offset + 1)
            else:
                print(f"{indent}{key}: {value}")

    def check_file_structure(self, last_sync_files: Dict[str, Any], path: Optional[str] = None,
                             change_found: bool = False) -> bool:
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

        Args:
            last_sync_files (dict[str, Any]): Same structure as FileStructure.files. Represents the file structure from
                the previous sync.
            last_sync_time (float): REMOVE. Represents time of last sync.
            path (str, optional): Path to the current directory.

        """
        if path is None:
            path = self.directory_path

        # Check values and mark as updated if necessary
        for key, value in self.files.items():
            new_path: str = str(Path(path) / key)
            if isinstance(value, dict):
                # Mark as updated if in self.files, but not in last_sync_files
                if not self.get_dict_value(new_path, self.from_json(last_sync_files)):
                    assert self.set_dict_value(new_path, self.files, value=True, updated=True)
                    change_found = True
                else:
                    assert self.set_dict_value(new_path, self.files, value=False, updated=True)
                # Recursive call
                if self.check_file_structure(last_sync_files, new_path):
                    change_found = True
            elif isinstance(value, float):
                # Check if entry from self.files is in last_sync_files, if not, mark updated
                if self.get_dict_value(new_path, self.from_json(last_sync_files)) is not False:
                    if (self.get_dict_value(new_path, self.files, updated=True) >
                            self.get_dict_value(new_path, self.from_json(last_sync_files), updated=True)):
                        # If file, exists in both, and newer than last sync, mark updated
                        assert self.set_dict_value(new_path, self.files, value=True, updated=True)
                        change_found = True
                    else:
                        # If file, exists in both, and not newer than last sync, mark not updated
                        assert self.set_dict_value(new_path, self.files, value=False, updated=True)
                else:
                    assert self.set_dict_value(new_path, self.files, value=True, updated=True)
                    change_found = True
            else:
                raise TypeError("FileStructure.files value is not a float or dictionary.")
        return change_found

    def split_path(self, path: str):
        if "\\" in str(path):
            return str(path).split("\\")
        elif "/" in str(path):
            return str(path).split("/")

    def get_dict_value(self, path: str, search_dict: dir_entry, keys: Optional[List[str]] = None,
                       updated: bool = False) -> Any:
        if keys is None:
            path_list: List[str] = self.split_path(path)
            for index, entry in enumerate(path_list):
                if path_list[:index+1] == self.path_list:
                    keys = path_list[index+1:]
        if keys is not None:
            if len(keys) == 1:
                if keys[0] in search_dict:
                    if updated:
                        return search_dict[keys[0]].updated
                    else:
                        return search_dict[keys[0]]
                else:
                    return False
            elif len(keys) > 1:
                if updated:
                    return self.get_dict_value(path, search_dict[keys[0]], keys[1:], updated=True)
                else:
                    return self.get_dict_value(path, search_dict[keys[0]], keys[1:])
            else:
                raise ValueError("Keys has no elements.")

    def set_dict_value(self, path: str, search_dict: dir_entry, value: Any, keys: Optional[List[str]] = None,
                       updated: bool = False) -> bool:
        if keys is None:
            path_list: List[str] = self.split_path(path)
            for index, entry in enumerate(path_list):
                if path_list[:index+1] == self.path_list:
                    keys = path_list[index+1:]
        if keys is not None:
            if len(keys) == 1:
                if keys[0] in search_dict:
                    if updated:
                        search_dict[keys[0]].updated = value
                    else:
                        search_dict[keys[0]] = value
                    return True
                    # return search_dict
                else:
                    return False
            elif len(keys) > 1:
                if updated:
                    return self.set_dict_value(path, search_dict[keys[0]], keys[1:], updated=True)
                else:
                    return self.set_dict_value(path, search_dict[keys[0]], keys[1:])
            else:
                raise ValueError("Keys has no elements.")
        else:
            return False

    def update_file_structure(self) -> None:
        pass

    def to_json(self, entry: dir_entry) -> Dict[str, Any]:
        file_dict: Dict[str, Any] = dict()
        for key in entry:
            if isinstance(entry[key], dict):
                file_dict[key] = {'mtime': entry[key].mtime, 'dir': self.to_json(entry[key])}
            elif isinstance(entry[key], float):
                file_dict[key] = float(entry[key])
            else:
                raise TypeError("dir_entry entry is not a float or dict.")
        return file_dict

    def from_json(self, file_dict: Dict[str, Any]) -> dir_entry:
        entry: dir_entry = dir_entry(dict())
        for key, value in file_dict.items():
            if isinstance(value, dict):
                entry[key] = self.from_json(value)
                entry[key].mtime = value['mtime']
            elif isinstance(value, float):
                entry[key] = file_entry(value)
            else:
                raise TypeError("file_dict entry is not a float or dict.")
        return entry
