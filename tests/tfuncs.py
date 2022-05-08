"""Contains useful functions for testing.


Author: Kevin Hodge
"""

from pathlib import Path
from typing import List, Any, Dict, Optional
import json
import shutil
import random
import functools


class TFunctions:
    """Contains useful functions that can be used by any test case."""
    def __init__(self):
        self.sync_dir_file: Path = Path.cwd() / Path("sync_directories_file.json")
        self.dir_tempfile: Path = Path.cwd() / Path("temp_sync_directories_file.json")
        self.last_sync_file: Path = Path.cwd() / Path("last_sync_file.json")
        self.last_tempfile: Path = Path.cwd() / Path("temp_last_sync_file.json")
        self.test_path1: Path = Path.cwd() / Path("test_dir1")
        self.test_path2: Path = Path.cwd() / Path("test_dir2")

    def get_json_contents(self, file_path: Path) -> List[str]:
        json_data: List[str]
        with file_path.open() as json_file:
            json_data = json.load(json_file)
        return json_data

    def write_json(self, input: Any, file_path: Path) -> None:
        with file_path.open("w") as json_file:
            json.dump(input, json_file)

    def create_dir_tempfile(self) -> None:
        # Move config file contents and delete config file
        if self.sync_dir_file.exists():
            with self.dir_tempfile.open("w") as json_file:
                json.dump(self.get_json_contents(self.sync_dir_file), json_file)
            self.sync_dir_file.unlink()

    def remove_dir_tempfile(self) -> None:
        # Clean up after test
        if self.dir_tempfile.exists():
            with self.sync_dir_file.open("w") as json_file:
                json.dump(self.get_json_contents(self.dir_tempfile), json_file)
            self.dir_tempfile.unlink()

    def create_last_tempfile(self) -> None:
        # Move config file contents and delete config file
        if self.last_sync_file.exists():
            with self.last_tempfile.open("w") as json_file:
                json.dump(self.get_json_contents(self.last_sync_file), json_file)
            self.last_sync_file.unlink()

    def remove_last_tempfile(self) -> None:
        # Clean up after test
        if self.last_tempfile.exists():
            with self.last_sync_file.open("w") as json_file:
                json.dump(self.get_json_contents(self.last_tempfile), json_file)
            self.last_tempfile.unlink()

    def create_test_dirs(self) -> None:
        # Create test directories
        if not self.test_path1.exists():
            self.test_path1.mkdir()
        if not self.test_path2.exists():
            self.test_path2.mkdir()

    def remove_test_dirs(self) -> None:
        # Clean up after test
        if self.test_path1.exists():
            shutil.rmtree(self.test_path1)
        if self.test_path2.exists():
            shutil.rmtree(self.test_path2)

    def create_rand_fstruct(self, path: str, max_depth: int = 5, max_entries: int = 5) -> Dict[str, Any]:
        if not Path(path).exists():
            Path(path).mkdir(exist_ok=True)

        file_dict: Dict[str, Any] = dict()
        num_entries: int = random.randint(0, max_entries)

        for i in range(num_entries):
            if random.randint(0, max_depth-1) > 0:
                # Create directory (0% chance of making directory at max depth)
                directory = Path(path) / f"test_dir_{i}"
                directory.mkdir(exist_ok=True)
                file_dict[str(directory.name)] = self.create_rand_fstruct(str(directory), max_depth-1, max_entries)
            else:
                # Create file
                file = Path(path) / f"test_file_{i}.txt"
                with file.open("w"):
                    pass
                file_dict[str(file.name)] = file.stat().st_mtime

        return file_dict

    @staticmethod
    def handle_dir_tempfile(func):
        """
        Creates and removes dir_tempfile even when an exception occurs.
        """
        tf: TFunctions = TFunctions()

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            error: Optional[Exception] = None
            tf.create_dir_tempfile()
            try:
                func(*args, **kwargs)
            except Exception as oops:
                error = oops
            finally:
                tf.remove_dir_tempfile()
            if error is not None:
                raise error
        return wrapper

    @staticmethod
    def handle_test_dirs(func):
        """
        Creates and removes test directories even when an exception occurs.
        """
        tf: TFunctions = TFunctions()

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            error: Optional[Exception] = None
            tf.create_test_dirs()
            try:
                func(*args, **kwargs)
            except Exception as oops:
                error = oops
            finally:
                tf.remove_test_dirs()
            if error is not None:
                raise error
        return wrapper

    @staticmethod
    def handle_last_tempfile(func):
        """
        Creates and removes last_tempfile even when an exception occurs.
        """
        tf: TFunctions = TFunctions()

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            error: Optional[Exception] = None
            tf.create_last_tempfile()
            try:
                func(*args, **kwargs)
            except Exception as oops:
                error = oops
            finally:
                tf.create_last_tempfile()
            if error is not None:
                raise error
        return wrapper

    def make_rand_mods(self, path: Path, file_dict: Dict[str, Any]) -> Dict[str, Any]:
        pass

    def write_fstruct(self, path: Path, file_dict: Dict[str, Any]) -> bool:
        pass
