"""Contains the FileStructure class.

Author: Kevin Hodge
"""

from typing import Any, KeysView, List, Optional, Dict
from pathlib import Path


class entry:
    """Contains info on a file/folder.

    Attributes:
        mod_time (float): last modification time of entry.
        updated (int): described the modification status of entry.
            0: Not modified
            1: Name Changed
            2: Last modified time changed

    """
    def __init__(self):
        self.__updated: bool = False

    def set_updated(self, updated: bool = True) -> None:
        self.__updated = updated

    def get_updated(self) -> int:
        return self.__updated


class file_entry(entry):
    def __init__(self, mod_time: float = -1.0) -> None:
        self.__mod_time: float = mod_time
        super().__init__()

    def set_mod_time(self, mod_time: float) -> None:
        self.__mod_time = mod_time

    def get_mod_time(self) -> float:
        return self.__mod_time


class dir_entry(entry):
    def __init__(self) -> None:
        self.__dict: Dict[str, entry] = dict()
        super().__init__()

    def add_entry(self, key: str, entry: entry) -> None:
        self.__dict[key] = entry

    def get_entry(self, requested_entry: str) -> entry:
        return self.__dict[requested_entry]

    def get_entry_path(self, keys: List[str]) -> Optional[entry]:
        if keys[0] in self.__dict:
            file_or_dir_entry: entry = self.__dict[keys[0]]
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
        return self.__dict.keys()


class FileStructure:
    """Contains information about a sync directory.

    Requirements:
        - Req #4: The program shall retrieve the names and file structure of all files and folders in both directories.
        - Req #10: File structures shall be stored in a class "FileStructure".

    Attributes:
        directory_path (str): Path to the directory that the FileStructure represents.
        path_list (str): directory_path split into a list of strings. Saves some computation time.
        files (dir_entry): Contains names of all files (strings) and all folders (dict with entries corresponding to the
            files and directories in the directory) in the directory. Folders contained in dicts, contain names of all
            files and folders in those folders, pattern continues until a directory with no folders is found.
        ex. {"dir_name": {"file1.txt", {"sub_dir_name": {"file2.txt", "file3.txt"}}, "file4.txt"}}
        verbose (bool): Indicates if messages will be printed for debugging.

    """
    def __init__(self, directory_path: str, verbose: bool = False) -> None:
        self.__directory_path: str = directory_path
        self.top_level_dir_path_list = self.split_path(self.get_directory_path())
        self.files: dir_entry = self.update_file_structure()
        self.verbose: bool = verbose

    def split_path(self, path: str):
        if "\\" in str(path):
            return str(path).split("\\")
        elif "/" in str(path):
            return str(path).split("/")

    def update_file_structure(self) -> dir_entry:
        """Reads all files and folders below the directory.

        Calls get_directory.

        Returns:
            self.files (dict): Structure of this dictionary is described in the arguments documentation of
                FileStructure.

        """
        self.files = self.get_directory(self.__directory_path)
        return self.files

    def get_directory(self, directory: str) -> dir_entry:
        """Recursive function that gives the structure of all files and folder contained within a directory.

        Args:
            directory (str): Path to the directory.

        Returns:
            file_structure (Dict[str, Any]): Same structure as FileStructure.files.
                ex. {"dir_name": {"file1.txt", {"sub_dir_name": {"file2.txt", "file3.txt"}}, "file4.txt"}}
            last_updates (Dict[float, Any]): Same structure as FleStructure.last_updates.

        """
        assert Path(directory).exists()

        file_structure: dir_entry = dir_entry()
        for entry in Path(directory).iterdir():
            last_mod_time: float = Path(entry).stat().st_mtime
            if Path(entry).is_file():
                file_structure.add_entry(str(entry.name), file_entry(last_mod_time))
            elif Path(entry).is_dir():
                file_structure.add_entry(str(entry.name), self.get_directory(str(entry)))
        return file_structure

    def get_directory_path(self) -> str:
        return self.__directory_path

    def print_file_structure(self, offset: int = 1) -> None:
        """Calls recursive_print_list with self.files as an argument."""
        print(Path(self.__directory_path).name)
        self.recursive_print_dir(self.files, offset)

    def recursive_print_dir(self, directory: dir_entry, offset: int = 0) -> None:
        """Prints out dict that matches format of self.files.

        Args:
            files_dict (dir_entry): dir_entry that contains a file structure described in
            offset (int): Tracks the depth of the directory and directory vs. file list.

        """
        indent: str = 3 * offset * ' '
        for entry_name in directory.get_keys():
            fstruct_entry: entry = directory.get_entry(entry_name)
            self.print_entry(indent, entry_name, fstruct_entry)
            if isinstance(fstruct_entry, dir_entry):
                self.recursive_print_dir(fstruct_entry, offset + 1)

    def print_entry(self, indent: str, entry_name: str, entry: entry) -> None:
        entry_repr: str = f"{indent}{entry_name}"
        if isinstance(entry, file_entry):
            entry_repr += f": {entry.get_mod_time()}"
        if entry.get_updated() > 0:
            entry_repr += " X"
        print(entry_repr)

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
            path = self.__directory_path
        if file_dir is None:
            file_dir = self.files

        last_sync_files: dir_entry = self.from_json(last_sync_dict)
        changes_found: int = 0

        for key in file_dir.get_keys():
            fstruct_entry: entry = file_dir.get_entry(key)
            new_path: str = str(Path(path) / key)
            path_list: List[str] = self.get_relative_path(new_path)
            last_sync_entry: Optional[entry] = last_sync_files.get_entry_path(path_list)

            if last_sync_entry is None:
                fstruct_entry.set_updated()
                changes_found += 1
            else:
                if isinstance(fstruct_entry, file_entry) and isinstance(last_sync_entry, file_entry):
                    if fstruct_entry.get_mod_time() > last_sync_entry.get_mod_time():
                        fstruct_entry.set_updated()
                        changes_found += 1

            if isinstance(fstruct_entry, dir_entry):
                changes_found += self.check_file_structure(last_sync_dict, new_path, fstruct_entry)
        return changes_found

    def get_relative_path(self, path: str) -> List[str]:
        path_list: List[str] = self.split_path(path)
        for index, _ in enumerate(path_list):
            if path_list[:index+1] == self.top_level_dir_path_list:
                return path_list[index+1:]
        raise ValueError("get_relative_path argument 'path' is not contained in top_level_dir_path_list")

    def files_to_json(self) -> Dict[str, Any]:
        return self.to_json(self.files)

    def to_json(self, directory: dir_entry) -> Dict[str, Any]:
        file_dict: Dict[str, Any] = dict()
        for dir_entry_name in directory.get_keys():
            directory_entry: entry = directory.get_entry(dir_entry_name)
            if isinstance(directory_entry, dir_entry):
                file_dict[dir_entry_name] = {'dir': self.to_json(directory_entry)}
            elif isinstance(directory_entry, file_entry):
                file_dict[dir_entry_name] = directory_entry.get_mod_time()
            else:
                raise TypeError(f"{type(directory_entry)} is not a dir_entry or file_entry.")
        return file_dict

    def files_to_list(self) -> List[str]:
        return self.to_list(self.files)

    def to_list(self, directory: dir_entry, only_updated: bool = False, path: Optional[str] = None) -> List[str]:
        if path is None:
            path = self.__directory_path
        file_list: List[str] = []
        for file_or_dir_name in directory.get_keys():
            file_or_dir_entry: entry = directory.get_entry(file_or_dir_name)
            file_or_dir_path: Path = Path(path) / file_or_dir_name
            file_or_dir_path_string: str = str(file_or_dir_path)
            if only_updated:
                if file_or_dir_entry.get_updated() > 0:
                    file_list.append(file_or_dir_path_string)
            else:
                file_list.append(file_or_dir_path_string)
            if isinstance(file_or_dir_entry, dir_entry):
                directory_entry: dir_entry = file_or_dir_entry
                file_list.extend(self.to_list(directory_entry, only_updated, file_or_dir_path_string))
        return file_list

    def get_updated_list(self) -> List[str]:
        return self.to_list(self.files, only_updated=True)

    def from_json(self, file_dict: Dict[str, Any]) -> dir_entry:
        directory: dir_entry = dir_entry()
        if 'dir' in file_dict:
            directory = self.from_json(file_dict['dir'])
        else:
            for key, fstruct_entry in file_dict.items():
                if isinstance(fstruct_entry, dict):
                    directory.add_entry(key, self.from_json(fstruct_entry))
                elif isinstance(fstruct_entry, float):
                    directory.add_entry(key, file_entry(fstruct_entry))
                else:
                    raise TypeError(f"{type(fstruct_entry)} is not a float or dict.")
        return directory
