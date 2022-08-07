"""Contains ConfigManager.

Author: Kevin Hodge
"""

from typing import List, Dict, Any, Type
import json
from syncfiles.file_system_interface import DBInterface


class ConfigManager:
    """Reads and writes configuration files for the program.

    Args:
        config_path (Path): Path to the configuration directory.
        sync_dir_file (Path): Path to sync_directories_file.json. File contains the directories that will be sync'd.
        min_dir (int): Indicates the minimum number of directories required to sync.
        verbose (bool)
    """
    min_dir: int = 2

    def __init__(self, db: Type[DBInterface], verbose: bool = False) -> None:
        self.db: Type[DBInterface] = db
        config_path: DBInterface = self.db.cwd()
        self.sync_dir_file: DBInterface = config_path / "sync_directories_file.json"
        self.last_sync_file: DBInterface = config_path / "last_sync_file.json"
        self.verbose: bool = verbose

    def get_min_dir(self) -> int:
        return self.min_dir

    def read_sync_directories(self) -> List[str]:
        """Gets directories to be synchronized from config file and/or from user.

        Finds sync_directories_file.json file in working directory, reads entries, and returns list with strings
        containing valid, unique directories.

        Returns:
            directories (list[str]): Existing, unique directories found in "sync_directories_file.json".
        """
        buffer: List[str] = []
        if self.sync_dir_file.exists():
            with self.sync_dir_file.open() as file_to_read:
                buffer = json.load(file_to_read)

        if not isinstance(buffer, list):
            buffer = []

        directories: List[str] = []
        for entry in buffer[::-1]:
            buffer.pop()
            if self.db(entry).exists() and entry not in buffer:
                directories.append(entry)

        return directories

    def check_sync_directory(self, new_dir: str, existing_dirs: List[str]) -> List[str]:
        """Checks directory provided by user and if valid and unique and adds to buffer if it is.

        Args:
            new_dir (str): new directory to be added to existing directories.
            existing_dirs (list[str]): existing directories.

        Returns:
            existing_dirs (list[str]): existing directories with new directory added (or not).
        """
        if new_dir not in existing_dirs and self.db(new_dir).exists():
            existing_dirs.append(new_dir)

        return existing_dirs

    def write_sync_directories(self, buffer: List[str]) -> bool:
        """Adds list of directories to sync_dir_file if list contains at least two elements.

        Args:
            buffer (List[Path]): list of paths

        Returns:
            bool: True if file was written, false if it was not.
        """
        assert isinstance(buffer, list)

        if len(buffer) >= self.min_dir:
            with self.sync_dir_file.open("w") as file_to_write:
                json.dump(buffer, file_to_write)
            return True
        return False

    def read_last_sync_file(self) -> Dict[str, Any]:
        last_sync_files: Dict[str, Any] = dict()
        if self.last_sync_file.exists():
            with self.last_sync_file.open() as json_file:
                last_sync_files = json.load(json_file)
                if self.verbose:
                    print("Read last_sync_file.json")
        else:
            if self.verbose:
                print("No last_sync_file found.")
        return last_sync_files

    def write_last_sync_file(self, file_dict: Dict[str, Any]) -> None:
        with self.last_sync_file.open("w") as json_file:
            json.dump(file_dict, json_file)
