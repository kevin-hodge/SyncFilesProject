"""Contains useful functions for testing.


Author: Kevin Hodge
"""

from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple
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

    def create_dir_tempfile(self) -> None:
        """Move sync directories file contents and delete sync directories file."""
        if self.sync_dir_file.exists():
            with self.dir_tempfile.open("w") as json_file:
                json.dump(get_json_contents(self.sync_dir_file), json_file)
            self.sync_dir_file.unlink()

    def remove_dir_tempfile(self) -> None:
        """Restore sync directories file contents and delete directories temporary file."""
        if self.dir_tempfile.exists():
            with self.sync_dir_file.open("w") as json_file:
                json.dump(get_json_contents(self.dir_tempfile), json_file)
            self.dir_tempfile.unlink()

    def create_last_tempfile(self) -> None:
        """Move last sync file contents and delete last sync file."""
        if self.last_sync_file.exists():
            with self.last_tempfile.open("w") as json_file:
                json.dump(get_json_contents(self.last_sync_file), json_file)
            self.last_sync_file.unlink()

    def remove_last_tempfile(self) -> None:
        """Restore last sync file contents and delete last sync temporary file."""
        if self.last_tempfile.exists():
            with self.last_sync_file.open("w") as json_file:
                json.dump(get_json_contents(self.last_tempfile), json_file)
            self.last_tempfile.unlink()

    def create_test_dirs(self) -> None:
        """Create test directories."""
        if not self.test_path1.exists():
            self.test_path1.mkdir()
        if not self.test_path2.exists():
            self.test_path2.mkdir()

    def remove_test_dirs(self) -> None:
        """Deletes test directories."""
        if self.test_path1.exists():
            shutil.rmtree(self.test_path1)
        if self.test_path2.exists():
            shutil.rmtree(self.test_path2)

    def create_rand_fstruct(self, path: str, max_depth: int = 5, max_entries: int = 5) -> Dict[str, Any]:
        """Creates a random file structure at the specified path.

        Args:
            path (str): Path to the directory in which the random file structure will be created.
            max_depth (optional, int): Maximum number of nested directories allowed (0 implies only files are allowed
                in the top directory).
            max_entries (optional, int): Maximum number of files or directories within each directory.

        Returns:
            file_dict (dict[str, Any]): Describes the random file structure (same format as FileStructure.files).
        """
        if not Path(path).exists():
            Path(path).mkdir(exist_ok=True)

        file_dict: Dict[str, Any] = dict()
        num_entries: int = random.randint(0, max_entries)

        for i in range(num_entries):
            if random.randint(0, max_depth-1) > 0:
                directory = Path(path) / f"test_dir_{i}"
                directory.mkdir(exist_ok=True)
                file_dict[str(directory.name)] = self.create_rand_fstruct(str(directory), max_depth-1, max_entries)
            else:
                file = Path(path) / f"test_file_{i}.txt"
                with file.open("w"):
                    pass
                file_dict[str(file.name)] = file.stat().st_mtime
        return file_dict

    def make_rand_mods(self, path: str, file_dict: Dict[str, Any],
                       par_name_change: bool = False) -> Tuple[Dict[str, Any], int, Dict[str, Any]]:
        """Makes random modifications to a file structure, creates a new dictionary that represents the structure, and
        creates a dictionary that contains the elements that have been changed.

        10% chance of changing directory name.
        5% change of changing file name.
        5% chance of modifying file.

        Args:
            path (Path): Path to the directory where the random modifications will be made.
            file_dict (Dict[str, Any]): file dictionary that stores file names, direcotry names, and structure.

        Returns:
            new_file_dict (Dict[str, Any]): _description_
            change_count (int): Number of changes made to the file structure.
            change_dict (Dict[str, Any]): dictionary of changed files and all folders.

        """
        if 'dir' in file_dict:
            return self.make_rand_mods(path, file_dict['dir'], par_name_change)
        new_file_dict: Dict[str, Any] = dict()
        change_dict: Dict[str, Any] = dict()
        change_count: int = 0
        for key, value in file_dict.items():
            if isinstance(value, dict):
                local_name_change: bool = False
                new_name: str = ""

                if random.random() > 0.9:
                    new_name = f"Edited_dir_{change_count}"
                    change_count += 1
                    local_name_change = True
                elif par_name_change:
                    change_count += 1

                dir_name: str = str(Path(path) / key)
                assert Path(dir_name).exists()
                changes: int
                new_file_dict[key], changes, change_dict[key] = \
                    self.make_rand_mods(dir_name, value, local_name_change or par_name_change)
                change_count += changes

                if local_name_change:
                    new_file_dict[new_name] = value
                    change_dict[new_name] = value
                    dest: str = str(Path(path) / new_name)
                    assert shutil.move(dir_name, dest) == dest

            elif isinstance(value, float):
                file_name: str = str(Path(path) / key)
                assert Path(file_name).exists()

                if random.random() > 0.1:
                    if random.random() > 0.5:
                        new_name = f"Edited_file_{change_count}.txt"
                        dest = str(Path(path) / new_name)
                        assert shutil.move(file_name, dest) == dest
                        Path(dest).touch(exist_ok=True)
                        new_file_dict[new_name] = Path(dest).stat().st_mtime
                        change_dict[new_name] = new_file_dict[new_name]
                    else:
                        assert Path(file_name).exists()
                        Path(file_name).touch(exist_ok=True)
                        new_file_dict[key] = Path(file_name).stat().st_mtime
                        change_dict[key] = new_file_dict[key]
                    change_count += 1
                elif par_name_change:
                    change_count += 1
                else:
                    new_file_dict[key] = value
            else:
                raise TypeError("Directory entry is not a file or directory")
        return new_file_dict, change_count, change_dict

    def recursive_print_dict(self, file_dict: Dict[str, Any], offset: int = 0) -> None:
        indent: str = 3 * offset * ' '
        for key, value in file_dict.items():
            if isinstance(value, dict):
                print(f"{indent}{key}")
                self.recursive_print_dict(value, offset + 1)
            else:
                print(f"{indent}{key}")


def get_json_contents(file_path: Path) -> Any:
    """Uses json modules to read json file and return contents."""
    json_data: Any
    with file_path.open() as json_file:
        json_data = json.load(json_file)
    return json_data


def write_json(input: Any, file_path: Path) -> None:
    """Uses json module to write to specified json file."""
    with file_path.open("w") as json_file:
        json.dump(input, json_file)


def handle_dir_tempfile(func):
    """Creates and removes dir_tempfile even when an exception occurs."""
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


def handle_error_after_function(func: Callable[[Any], Any]) -> None:
    pass


def handle_test_dirs(func) -> Callable[[Any], Any]:
    """Creates and removes test directories even when an exception occurs."""
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


def handle_last_tempfile(func):
    """Creates and removes last_tempfile even when an exception occurs."""
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
            tf.remove_last_tempfile()
        if error is not None:
            raise error
    return wrapper
