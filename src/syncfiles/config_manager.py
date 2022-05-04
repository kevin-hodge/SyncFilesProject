"""ConfigManager handles configuration files for the program.


Author: Kevin Hodge
"""

from typing import List
from pathlib import Path
import json


class ConfigManager():
    def __init__(self) -> None:
        self.config_path: Path = Path.cwd()
        self.sync_dir_file: Path = self.config_path / "sync_directories_file.json"
        self.min_dir: int = 2

    def read_sync_directories(self) -> List[str]:
        """Gets directories to be synchronized from config file and/or from user.

        Finds sync_directories_file.json file in working directory, reads entries, and returns list with strings
        containing valid, unique directories.

        Returns:
            buffer (list[str]): Existing, unique directories found in "sync_directories_file.json".

        Requirements:
            - Req #2: The program shall find sync_directories_file.json (json file containing the sync directories).
            - Req #3: The program shall open and read sync_directories_file.json.
            - Req #15: The program shall store and get sync directories from a config file.

        """
        # Read file (with ensures file is closed even if an exception occurs)
        buffer: List[str] = []
        if self.sync_dir_file.exists():
            with self.sync_dir_file.open() as file_to_read:
                buffer = json.load(file_to_read)

        # Ensures buffer is the right datatype
        if not isinstance(buffer, list):
            buffer = []

        # Removes invalid directories. Loops through in reverse order to avoid removing elements that change the
        # indices of all elements after and cause elements to be skipped.
        for entry in buffer[::-1]:
            if not Path(entry).exists():
                buffer.remove(entry)

        return buffer

    def check_sync_directory(self, new_dir: str, existing_dirs: List[str]) -> List[str]:
        """Checks directory provided by user and if valid and unique and adds to buffer if it is.

        Args:
            new_dir (str): _description_
            existing_dirs (List[str]): _description_

        Returns:
            existing_dirs ()
        """
        if new_dir not in existing_dirs and Path(new_dir).exists():
            existing_dirs.append(new_dir)

        return existing_dirs

    def write_sync_directories(self, buffer: List[str]) -> bool:
        """Adds list of directories to sync_dir_file.

        Args:
            buffer (List[Path]): list of paths

        Returns:
            True if file was written, false if it was not.

        Requirements:
            - Req #17: The program shall update config file with directory provided by user (if it exists).
        """
        # Creates and writes or overwrites JSON config file if User inputs new directories to sync
        assert isinstance(buffer, list)

        # Writes str paths to file
        if len(buffer) >= self.min_dir:
            with self.sync_dir_file.open("w") as file_to_write:
                json.dump(buffer, file_to_write)
            return True
        return False

    def read_last_sync_file(self):
        pass
