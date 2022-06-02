"""Contains the FileStructure class.


Author: Kevin Hodge
"""

from typing import Any, List, Optional, Dict, Union
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
        path_list (str): directory_path split into a list of strings. Saves some computation time.
        files (dir_entry): Contains names of all files (strings) and all folders (dict with entries corresponding to the
            files and directories in the directory) in the directory. Folders contained in dicts, contain names of all
            files and folders in those folders, pattern continues until a directory with no folders is found.
        ex. {"dir_name": {"file1.txt", {"sub_dir_name": {"file2.txt", "file3.txt"}}, "file4.txt"}}
        verbose (bool): Indicates if messages will be printed for debugging.

    """
    def __init__(self, directory_path: str, verbose: bool = False) -> None:
        assert Path(directory_path).exists()
        self.directory_path: str = directory_path
        self.path_list = self.split_path(self.directory_path)
        self.files: dir_entry = dir_entry(dict())
        self.verbose: bool = verbose

    def get_file_structure(self) -> dir_entry:
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
            files_dict (dir_entry): dir_entry that contains a file structure described in
            offset (int): Tracks the depth of the directory and directory vs. file list.

        """
        indent: str = 3 * offset * ' '  # indent made for each directory level
        for key in files_dict:
            value: Union[dir_entry, file_entry] = files_dict[key]
            if isinstance(value, dict):
                dir_string: str = f"{indent}{key}: {value.mtime}"
                if value.updated:
                    dir_string = dir_string + " X"
                print(dir_string)
                self.recursive_print_dict(value, offset + 1)
            else:
                file_string: str = f"{indent}{key}: {value}"
                if value.updated:
                    file_string = file_string + " X"
                print(file_string)

    def check_file_structure(self, last_sync_dict: Dict[str, Any], path: Optional[str] = None,
                             file_dir: Optional[dir_entry] = None) -> int:
        """Checks for updates within the self.files since the last sync and fills self.updated.

        Args:
            last_sync_files (dict[str, Any]): Same structure as FileStructure.files. Represents the file structure from
                the previous sync.
            path (str, optional): Path to the current directory.

        """
        if path is None:
            path = self.directory_path
        if file_dir is None:
            file_dir = self.files

        # Check values and mark as updated if necessary
        last_sync_files: dir_entry = self.from_json(last_sync_dict)
        changes_found: int = 0
        for key in file_dir:
            value: Union[dir_entry, file_entry] = file_dir[key]
            new_path: str = str(Path(path) / key)
            if isinstance(value, dict):
                # Mark as updated if in self.files, but not in last_sync_files
                if self.get_dict_value(new_path, last_sync_files) is not False:
                    value.updated = False
                else:
                    value.updated = True
                    changes_found += 1
                # Recursive call
                changes: int = self.check_file_structure(last_sync_files, new_path, value)
                changes_found += changes
            elif isinstance(value, float):
                # Check if entry from self.files is in last_sync_files, if not, mark updated
                if self.get_dict_value(new_path, last_sync_files) is not False:
                    if (self.get_dict_value(new_path, self.files) > self.get_dict_value(new_path, last_sync_files)):
                        # If file, exists in both, and newer than last sync, mark updated
                        value.updated = True
                        changes_found += 1
                    else:
                        # If file, exists in both, and not newer than last sync, mark not updated
                        value.updated = False
                else:
                    value.updated = True
                    changes_found += 1
            else:
                raise TypeError("FileStructure.files value is not a float or dictionary.")
        return changes_found

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
            if keys[0] in search_dict:
                if len(keys) == 1:
                    if updated:
                        return search_dict[keys[0]].updated
                    else:
                        return search_dict[keys[0]]
                elif len(keys) > 1:
                    if updated:
                        return self.get_dict_value(path, search_dict[keys[0]], keys[1:], updated=True)
                    else:
                        return self.get_dict_value(path, search_dict[keys[0]], keys[1:])
                else:
                    raise ValueError("Keys has no elements.")
            else:
                return False

    def set_dict_updated(self, path: str, search_dict: dir_entry, value: bool,
                         keys: Optional[List[str]] = None) -> bool:
        if keys is None:
            path_list: List[str] = self.split_path(path)
            for index, entry in enumerate(path_list):
                if path_list[:index+1] == self.path_list:
                    keys = path_list[index+1:]
        if keys is not None:
            if len(keys) == 1:
                if keys[0] in search_dict:
                    search_dict[keys[0]].updated = value
                    return True
                else:
                    return False
            elif len(keys) > 1:
                return self.set_dict_updated(path, search_dict[keys[0]], value, keys[1:])
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
        if 'mtime' in file_dict:
            entry = self.from_json(file_dict['dir'])
            entry.mtime = file_dict['mtime']
        else:
            for key, value in file_dict.items():
                if isinstance(value, dict):
                    entry[key] = self.from_json(value)
                elif isinstance(value, float):
                    entry[key] = file_entry(value)
                else:
                    raise TypeError("file_dict entry is not a float or dict.")
        return entry
