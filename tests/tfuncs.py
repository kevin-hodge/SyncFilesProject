"""Contains useful functions for testing.


Author: Kevin Hodge
"""

from pathlib import Path
from typing import List, Any, Dict, Optional
import json
import shutil
import random
import functools
import unittest
from syncfiles.file_structure import FileStructure


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

    def make_rand_mods(self, path: str, file_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Makes random modifications to a file structure dictionary.

        10% chance of changing directory name.
        5% change of changing file name.
        5% chance of modifying file.

        Args:
            path (Path): _description_
            file_dict (Dict[str, Any]): _description_

        Returns:
            Dict[str, Any]: _description_
        """
        # Iterate through file structure dictionary
        new_file_dict: Dict[str, Any] = dict()
        change_count: int = 0
        for key, value in file_dict.items():
            if isinstance(value, dict):
                dir_name: str = str(Path(path) / key)
                assert Path(dir_name).exists()
                new_file_dict[key] = self.make_rand_mods(dir_name, value)
                if random.random() > 0.9:
                    # Change directory name
                    new_name: str = f"Edited_dir_{change_count}"
                    change_count += 1
                    new_file_dict[new_name] = value
                    dest: str = str(Path(path) / new_name)
                    assert shutil.move(dir_name, dest) == dest
            elif isinstance(value, float):
                file_name: str = str(Path(path) / key)
                assert Path(file_name).exists()
                if random.random() > 0.1:
                    if random.random() > 0.5:
                        # Change file name
                        new_name = f"Edited_file_{change_count}.txt"
                        dest = str(Path(path) / new_name)
                        assert shutil.move(file_name, dest) == dest
                        Path(dest).touch(exist_ok=True)
                        new_file_dict[new_name] = Path(dest).stat().st_mtime
                    else:
                        # Update last modified date
                        assert Path(file_name).exists()
                        Path(file_name).touch(exist_ok=True)
                        new_file_dict[key] = Path(file_name).stat().st_mtime
                    change_count += 1
                else:
                    new_file_dict[key] = value
            else:
                raise TypeError("Directory entry is not a file or directory")
        return new_file_dict

    def recursive_check_entry(self, case: unittest.TestCase, fstruct: FileStructure, file_dict: Dict[str, Any],
                              path: Optional[str] = None, updated: bool = False) -> None:
        """Runs get_dict_value on each entry in a FileStructure and asserts that the value returned equals the value."""
        if path is None:
            path = fstruct.directory_path
        for key, value in file_dict.items():
            new_path = str(Path(path) / key)
            if updated:
                if isinstance(value, dict):
                    self.recursive_check_entry(case, fstruct, value, new_path, updated=True)
                check_val: Any = fstruct.get_dict_value(new_path, fstruct.files, updated=True)
                case.assertEqual(check_val, value.updated)
            else:
                if isinstance(value, dict):
                    self.recursive_check_entry(case, fstruct, value, new_path)
                check_val = fstruct.get_dict_value(new_path, fstruct.files)
                case.assertEqual(check_val, value)

    def write_last_sync(self):
        pass
