"""ConfigManager handles configuration files for the program.


Author: Kevin Hodge
"""

from typing import List, Dict, Any, Tuple
from pathlib import Path
import json


class ConfigManager():
    """_summary_

    Args:
        config_path (Path): Path to the configuration directory.
        sync_dir_file (Path): Path to sync_directories_file.json. File contains the directories that will be sync'd.
        min_dir (int): Indicates the minimum number of directories required to sync.
        verbose (bool)

    """
    def __init__(self, verbose: bool = False) -> None:
        self.config_path: Path = Path.cwd()
        self.sync_dir_file: Path = self.config_path / "sync_directories_file.json"
        self.min_dir: int = 2
        self.verbose: bool = verbose

    def read_sync_directories(self) -> List[str]:
        """Gets directories to be synchronized from config file and/or from user.

        Finds sync_directories_file.json file in working directory, reads entries, and returns list with strings
        containing valid, unique directories.

        Returns:
            directories (list[str]): Existing, unique directories found in "sync_directories_file.json".

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
        directories: List[str] = []
        for _, entry in enumerate(buffer[::-1]):
            buffer.pop()
            if Path(entry).exists() and entry not in buffer:
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

    def read_last_sync_file(self) -> Tuple[Dict[str, Any], float]:
        # Check if last_updates_file exists
        # Retrieve last_sync_files and last_sync_time for each entry in files
        folder_path: Path = Path("..")
        last_sync_path: Path = folder_path / "last_sync_file.json"
        last_sync_files: Dict[str, Any] = dict()
        last_sync_time: float = 0.0
        if last_sync_path.exists():
            last_sync_data: List[Any] = list()
            with open(last_sync_path, "r") as json_file:
                last_sync_data = json.load(json_file)
                if self.verbose:
                    print("Read last_sync_file.json")
                json_file.close()
            assert len(last_sync_data) == 2
            last_sync_files = last_sync_data[0]
            last_sync_time = last_sync_data[1]
        else:
            if self.verbose:
                print("No last_sync_file found.")

        return last_sync_files, last_sync_time
