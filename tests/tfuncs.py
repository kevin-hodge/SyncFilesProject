"""Contains useful functions for testing.

Author: Kevin Hodge
"""

from pathlib import Path
from typing import Any, Callable, List, Optional
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

    def create_rand_fstruct(self, path: str, max_depth: int = 3, max_entries: int = 5) -> None:
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

        num_entries: int = random.randint(0, max_entries)

        for i in range(num_entries):
            if random.randint(0, max_depth-1) > 0:
                directory = Path(path) / f"test_dir_{i}"
                self.create_directory(directory)
                self.create_rand_fstruct(str(directory), max_depth-1, max_entries)
            else:
                file = Path(path) / f"test_file_{i}.txt"
                self.create_file(file)

    def create_directory(self, path: Path) -> None:
        path.mkdir(exist_ok=True)

    def create_file(self, path: Path) -> None:
        path.touch(exist_ok=True)

    def make_rand_mods(self, path: str, parent_name_change: bool = False) -> int:
        """Makes random modifications to a file structure and returns the number of changes.

        10% chance of changing directory name.
        45% change of changing file name.
        45% chance of updating file last modification time.

        Args:
            path (Path): Path to the directory where the random modifications will be made.

        Returns:
            change_count (int): Number of changes made to the file structure.

        """
        change_count: int = 0
        for entry_path in Path(path).iterdir():
            if entry_path.is_dir():
                local_name_change: bool = False
                if random.random() > 0.9:
                    local_name_change = True

                change_count += self.make_rand_mods(str(entry_path), local_name_change or parent_name_change)

                if local_name_change:
                    self.change_dir_name(path, str(entry_path), change_count)
                    change_count += 1
                elif parent_name_change:
                    change_count += 1
            elif Path(entry_path).is_file():
                if random.random() > 0.1:
                    if random.random() > 0.5:
                        self.change_file_name(path, str(entry_path), change_count)
                    else:
                        self.update_last_mod_time(entry_path)
                    change_count += 1
                elif parent_name_change:
                    change_count += 1
            else:
                raise TypeError("make_rand_mods file_dict entry is not a dict or float")
        return change_count

    def change_file_name(self, path: str, old_path: str, change_count: int) -> None:
        new_name = f"Edited_file_{change_count}.txt"
        dest = str(Path(path) / new_name)
        assert shutil.move(old_path, dest) == dest

    def change_dir_name(self, path: str, old_path: str, change_count: int) -> None:
        new_name: str = f"Edited_dir_{change_count}"
        dest: str = str(Path(path) / new_name)
        assert shutil.move(old_path, dest) == dest

    def update_last_mod_time(self, entry_path: Path) -> None:
        entry_path.touch(exist_ok=True)

    def recursive_print_dir(self, path: Path, offset: int = 0) -> None:
        indent: str = 3 * offset * ' '
        for entry in path.iterdir():
            print(f"{indent}{entry.name}")
            if entry.is_dir():
                self.recursive_print_dir(entry, offset + 1)

    def dir_to_list(self, path: str) -> List[str]:
        dir_list: List[str] = []
        for entry in Path(path).iterdir():
            dir_list.append(str(entry))
            if entry.is_dir():
                dir_list.extend(self.dir_to_list(str(entry)))
        return dir_list


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
        tf.create_dir_tempfile()
        handle_error_after_function(func, tf.remove_dir_tempfile, *args, **kwargs)
    return wrapper


def handle_error_after_function(func: Callable[[Any], Any], after_func: Callable[[], None],
                                *args: Any, **kwargs: Any) -> None:
    error: Optional[Exception] = None
    try:
        func(*args, **kwargs)  # type: ignore[call-arg]
    except Exception as oops:
        error = oops
    finally:
        after_func()
    if error is not None:
        raise error


def handle_test_dirs(func) -> Callable[[Any], Any]:
    """Creates and removes test directories even when an exception occurs."""
    tf: TFunctions = TFunctions()

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        tf.create_test_dirs()
        handle_error_after_function(func, tf.remove_test_dirs, *args, **kwargs)
    return wrapper


def handle_last_tempfile(func):
    """Creates and removes last_tempfile even when an exception occurs."""
    tf: TFunctions = TFunctions()

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        tf.create_last_tempfile()
        handle_error_after_function(func, tf.remove_last_tempfile, *args, **kwargs)
    return wrapper
