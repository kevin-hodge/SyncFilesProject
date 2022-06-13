"""Contains the FileStructure class.


Author: Kevin Hodge
"""

from typing import Any, List, Optional, Dict, Union
from pathlib import Path


class entry:
    def __init__(self, mtime: float):
        self.mtime: float = mtime
        self.updated: bool = False

    def set_updated(self) -> None:
        self.updated = True

    def get_updated(self) -> bool:
        return self.updated

    def get_modification_time(self) -> float:
        return self.mtime


class dir_entry(Dict[str, Any]):
    def __init__(self, *args, **kwargs) -> None:
        self.mtime: float = float()
        self.updated: bool = False
        self.dict: Dict[str, entry] = dict()
        super().__init__(*args, **kwargs)

    def add_entry(self, key: str, entry: entry) -> None:
        self.dict[key] = entry

    def get_entry(self, keys: List[str]) -> Optional[entry]:
        if keys[0] in self.dict:
            if len(keys) == 1:
                return self.dict[keys[0]]
            elif len(keys) > 1:
                return self.dict[keys[0]].get_entry(self.dict[keys[0]], keys[1:])
        else:
            return None


class file_entry(entry):
    def __init__(self, mtime: float) -> None:
        super().__init__(mtime)


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

    def print_file_structure(self, offset: int = 1) -> None:
        """Calls recursive_print_list with self.files as an argument."""
        print(Path(self.directory_path).name)
        self.recursive_print_dir(self.files, offset)

    def recursive_print_dir(self, files_dict: dir_entry, offset: int = 0) -> None:
        """Prints out dict that matches format of FileStructure.files.

        Args:
            files_dict (dir_entry): dir_entry that contains a file structure described in
            offset (int): Tracks the depth of the directory and directory vs. file list.

        """
        indent: str = 3 * offset * ' '
        for key in files_dict:
            files_entry: Union[dir_entry, file_entry] = files_dict[key]
            if isinstance(files_entry, dict):
                dir_string: str = f"{indent}{key}: {files_entry.mtime}"
                if files_entry.updated:
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
            path (str, optional): Path to the current directory.

        """
        if path is None:
            path = self.directory_path
        if file_dir is None:
            file_dir = self.files

        last_sync_files: dir_entry = self.from_json(last_sync_dict)
        changes_found: int = 0

        for key in file_dir:
            files_entry: Union[dir_entry, file_entry] = file_dir[key]
            new_path: str = str(Path(path) / key)
            path_list: List[str] = self.get_relative_path(new_path)
            last_sync_entry: Optional[Union[dir_entry, file_entry]] = self.get_entry(last_sync_files, path_list)

            if last_sync_entry is None:
                files_entry.updated = True
                changes_found += 1
            else:
                if isinstance(files_entry, file_entry):
                    last_sync_time: float = last_sync_entry.mtime
                    if files_entry.get_modification_time() > last_sync_time:
                        files_entry.set_updated()
                        changes_found += 1

            if isinstance(files_entry, dict):
                changes_found += self.check_file_structure(last_sync_dict, new_path, files_entry)
        return changes_found

    def get_relative_path(self, path: str) -> list[str]:
        path_list: List[str] = self.split_path(path)
        for index, _ in enumerate(path_list):
            if path_list[:index+1] == self.path_list:
                return path_list[index+1:]

    def get_entry(self, search_dir: dir_entry, keys: List[str]) -> Optional[Union[file_entry, dir_entry]]:
        if keys[0] in search_dir:
            if len(keys) == 1:
                return search_dir[keys[0]]
            elif len(keys) > 1:
                return self.get_entry(search_dir[keys[0]], keys[1:])
        else:
            return None

    def files_to_json(self) -> Dict[str, Any]:
        return self.to_json(self.files)

    def to_json(self, directory: dir_entry) -> Dict[str, Any]:
        file_dict: Dict[str, Any] = dict()
        for entry in directory:
            if isinstance(directory[entry], dir_entry):
                file_dict[entry] = {'mtime': directory[entry].mtime, 'dir': self.to_json(directory[entry])}
                assert type(file_dict[entry]) == dict
            elif isinstance(directory[entry], file_entry):
                file_dict[entry] = float(directory[entry].mtime)
                assert type(file_dict[entry]) == float
            else:
                raise TypeError("dir_entry entry is not a float or dict.")
        return file_dict

    def from_json(self, file_dict: Dict[str, Any]) -> dir_entry:
        entry: dir_entry = dir_entry(dict())
        if 'mtime' in file_dict:
            entry = self.from_json(file_dict['dir'])
            entry.mtime = file_dict['mtime']
        else:
            for key, files_entry in file_dict.items():
                if isinstance(files_entry, dict):
                    entry[key] = self.from_json(files_entry)
                elif isinstance(files_entry, float):
                    entry[key] = file_entry(files_entry)
                else:
                    raise TypeError(f"file_dict entry: {type(files_entry)} is not a float or dict.")
        return entry
