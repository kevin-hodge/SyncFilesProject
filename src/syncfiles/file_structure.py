"""Contains the FileStructure class.

Author: Kevin Hodge
"""

from typing import Any, KeysView, List, Optional, Dict, Union
from pathlib import Path


class entry:
    def __init__(self, mtime: float = -1.0):
        self.mtime: float = mtime
        self.updated: bool = False

    def set_updated(self) -> None:
        self.updated = True

    def get_updated(self) -> bool:
        return self.updated

    def set_mod_time(self, mtime: float) -> None:
        self.mtime = mtime

    def get_mod_time(self) -> float:
        return self.mtime


class file_entry(entry):
    def __init__(self, mtime: float = -1.0) -> None:
        super().__init__(mtime)


class dir_entry(entry):
    def __init__(self, mtime: float = -1.0) -> None:
        self.dict: Dict[str, entry] = dict()
        super().__init__(mtime)

    def add_entry(self, key: str, entry: entry) -> None:
        self.dict[key] = entry

    def get_entry(self, requested_entry: str) -> entry:
        return self.dict[requested_entry]

    def get_entry_path(self, keys: List[str]) -> Optional[entry]:
        if keys[0] in self.dict:
            file_or_dir_entry: entry = self.dict[keys[0]]
            if len(keys) == 1:
                return file_or_dir_entry
            elif len(keys) > 1 and isinstance(file_or_dir_entry, dir_entry):
                directory: dir_entry = file_or_dir_entry
                return directory.get_entry_path(keys[1:])
            else:
                raise KeyError("get_entry_path argument keys was not valid")
        else:
            return None

    def get_keys(self) -> KeysView[str]:
        return self.dict.keys()


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
        self.top_level_dir_path_list = self.split_path(self.directory_path)
        self.files: dir_entry = self.get_file_structure()
        self.verbose: bool = verbose

    def split_path(self, path: str):
        if "\\" in str(path):
            return str(path).split("\\")
        elif "/" in str(path):
            return str(path).split("/")

    def get_file_structure(self) -> dir_entry:
        """Reads all files and folders below the directory.

        Calls recursive_get_directory.

        Returns:
            self.files (dict): Structure of this dictionary is described in the arguments documentation of
                FileStructure.

        """
        self.files = self.recursive_get_directory(self.directory_path)
        return self.files

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

        file_structure: dir_entry = dir_entry(Path(directory).stat().st_mtime)
        for entry in Path(directory).iterdir():
            last_mod_time: float = Path(entry).stat().st_mtime
            if Path(entry).is_file():
                file_structure.add_entry(entry.name, file_entry(last_mod_time))
            elif Path(entry).is_dir():
                file_structure.add_entry(entry.name, self.recursive_get_directory(str(entry)))
            else:
                raise ValueError("Directory entry is not a file or directory")
        return file_structure

    def print_file_structure(self, offset: int = 1) -> None:
        """Calls recursive_print_list with self.files as an argument."""
        print(Path(self.directory_path).name)
        self.recursive_print_dir(self.files, offset)

    def recursive_print_dir(self, directory: dir_entry, offset: int = 0) -> None:
        """Prints out dict that matches format of FileStructure.files.

        Args:
            files_dict (dir_entry): dir_entry that contains a file structure described in
            offset (int): Tracks the depth of the directory and directory vs. file list.

        """
        indent: str = 3 * offset * ' '
        for key in directory.get_keys():
            files_entry: entry = directory.get_entry(key)
            if isinstance(files_entry, dir_entry):
                dir_string: str = f"{indent}{key}: {files_entry.mtime}"
                if files_entry.get_updated():
                    dir_string = dir_string + " X"
                print(dir_string)
                self.recursive_print_dir(files_entry, offset + 1)
            else:
                file_string: str = f"{indent}{key}: {files_entry.mtime}"
                if files_entry.get_updated():
                    file_string = file_string + " X"
                print(file_string)

    def check_file_structure(self, last_sync_dict: Dict[str, Any], path: Optional[str] = None,
                             file_dir: Optional[dir_entry] = None) -> int:
        """Checks for updates within the self.files since the last sync.
        - marks updated field for each entry
        - counts number of changes

        Args:
            last_sync_files (dict[str, Any]): Same structure as FileStructure.files. Represents the file structure from
                the previous sync.
            path (str, optional): Path to the directory directory.

        """
        if path is None:
            path = self.directory_path
        if file_dir is None:
            file_dir = self.files

        last_sync_files: dir_entry = self.from_json(last_sync_dict)
        changes_found: int = 0

        for key in file_dir.get_keys():
            files_entry: entry = file_dir.get_entry(key)
            new_path: str = str(Path(path) / key)
            path_list: List[str] = self.get_relative_path(new_path)
            last_sync_entry: Optional[entry] = last_sync_files.get_entry_path(path_list)

            if last_sync_entry is None:
                files_entry.set_updated()
                changes_found += 1
            else:
                if isinstance(files_entry, file_entry):
                    last_sync_time: float = last_sync_entry.get_mod_time()
                    if files_entry.get_mod_time() > last_sync_time:
                        files_entry.set_updated()
                        changes_found += 1

            if isinstance(files_entry, dir_entry):
                changes_found += self.check_file_structure(last_sync_dict, new_path, files_entry)
        return changes_found

    def get_relative_path(self, path: str) -> List[str]:
        path_list: List[str] = self.split_path(path)
        for index, _ in enumerate(path_list):
            if path_list[:index+1] == self.top_level_dir_path_list:
                return path_list[index+1:]
        raise ValueError("get_relative_path argument 'path' is not contained in top_level_dir_path_list")

    def get_entry(self, keys: List[str]) -> Optional[entry]:
        return self.files.get_entry_path(keys)

    def files_to_json(self) -> Dict[str, Any]:
        return self.to_json(self.files)

    def to_json(self, directory: dir_entry) -> Dict[str, Any]:
        file_dict: Dict[str, Any] = dict()
        for dir_entry_name in directory.get_keys():
            file_dict[dir_entry_name] = self.convert_dir_entry_to_dict_entry(dir_entry_name, directory)
        return file_dict

    def convert_dir_entry_to_dict_entry(self, dir_entry_name: str,
                                        directory: dir_entry) -> Union[Dict[str, Any], float]:
        directory_entry: entry = directory.get_entry(dir_entry_name)
        if isinstance(directory_entry, dir_entry):
            return {'mtime': directory_entry.get_mod_time(),
                    'dir': self.to_json(directory_entry)}
        elif isinstance(directory_entry, file_entry):
            return directory_entry.get_mod_time()
        else:
            raise TypeError(f"{type(directory_entry)} is not a dir_entry or file_entry.")

    def from_json(self, file_dict: Dict[str, Any]) -> dir_entry:
        directory: dir_entry = dir_entry()
        if 'mtime' in file_dict:
            directory = self.from_json(file_dict['dir'])
            directory.set_mod_time(file_dict['mtime'])
        else:
            for key, files_entry in file_dict.items():
                if isinstance(files_entry, dict):
                    directory.add_entry(key, self.from_json(files_entry))
                elif isinstance(files_entry, float):
                    directory.add_entry(key, file_entry(files_entry))
                else:
                    raise TypeError(f"{type(files_entry)} is not a float or dict.")
        return directory
