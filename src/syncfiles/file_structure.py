"""Contains the FileStructure class.

Author: Kevin Hodge
"""

from typing import Any, List, Optional, Dict, Type
# from pathlib import Path
from syncfiles.file_system_interface import DBInterface
from syncfiles.sync_exception import SyncException
from syncfiles.entry import entry, file_entry, dir_entry


class FileStructure:
    """Contains information about a sync directory.

    Attributes:
        directory_path (str): Path to the directory that the FileStructure represents.
        dir_path_list (str): directory_path split into a list of strings. Saves some computation time.
        files (dir_entry): Contains names of all files (strings) and all folders (dict with entries corresponding to the
            files and directories in the directory) in the directory. Folders contained in dicts, contain names of all
            files and folders in those folders, pattern continues until a directory with no folders is found.
        verbose (bool): Indicates if messages will be printed for debugging.
    """
    def __init__(self, directory_path: str, db_interface: Type[DBInterface], verbose: bool = False) -> None:
        self.__directory_path: str = directory_path
        self.db: Type[DBInterface] = db_interface
        self.dir_path_list = self.split_path(self.get_directory_path())
        self.files: dir_entry = self.update_file_structure()
        self.verbose: bool = verbose

    def split_path(self, path: str):
        if "\\" in str(path):
            return str(path).split("\\")
        elif "/" in str(path):
            return str(path).split("/")

    def update_file_structure(self) -> dir_entry:
        """Reads all files and folders below the directory.

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
            file_structure (dir_entry): Same structure as FileStructure.files.
        """
        # if not Path(directory).exists():
        if not self.db(directory).exists():
            raise SyncException("Sync Directory Does Not Exist", error_id="sync_dirs_do_not_exist")

        file_structure: dir_entry = dir_entry()
        # for entry_path in Path(directory).iterdir():
        for entry_path in self.db(directory).iterdir():
            #if Path(entry_path).is_file():
            if entry_path.is_file():
                # last_mod_time: float = Path(entry_path).stat().st_mtime
                last_mod_time: float = entry_path.get_mod_time()
                # file_structure.add_entry(str(entry_path.name), file_entry(last_mod_time))
                file_structure.add_entry(str(entry_path.get_name()), file_entry(last_mod_time))
            # elif Path(entry_path).is_dir():
            elif entry_path.is_dir():
                # file_structure.add_entry(str(entry_path.name), self.get_directory(str(entry_path)))
                file_structure.add_entry(str(entry_path.get_name()), self.get_directory(str(entry_path)))
        return file_structure

    def get_directory_path(self) -> str:
        return self.__directory_path

    def print_file_structure(self, offset: int = 1) -> str:
        return self.db(self.__directory_path).get_name() + "\n" + self.files.__repr__(offset)
        # return Path(self.__directory_path).name + "\n" + self.files.__repr__(offset)

    def check_file_structure(self, last_sync_dict: Dict[str, Any], path: Optional[str] = None,
                             file_dir: Optional[dir_entry] = None) -> int:
        """Checks for updates within the self.files since the last sync.

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
            new_path: str = str(self.db(path) / key)
            # new_path: str = str(Path(path) / key)
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
            if path_list[:index+1] == self.dir_path_list:
                return path_list[index+1:]
        raise ValueError("get_relative_path argument 'path' is not contained in dir_path_list")

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
            file_or_dir_path: Type[DBInterface] = self.db(path) / file_or_dir_name
            # file_or_dir_path: Path = Path(path) / file_or_dir_name
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
