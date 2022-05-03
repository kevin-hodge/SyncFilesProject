"""Sync Files Project Test


Author: Kevin Hodge
"""
from typing import List, Tuple
from pathlib import Path
import shutil
import json
import unittest
from syncfiles.config_manager import ConfigManager


def get_json_contents(file_path: Path) -> List[str]:
    json_data: List[str]
    with file_path.open() as json_file:
        json_data = json.load(json_file)
    return json_data


class ConfigManagerTestCase(unittest.TestCase):
    """Test case for ConfigManager"""
    def __init__(self, *args, **kwargs) -> None:
        self.sync_dir_file: Path = Path.cwd() / Path("sync_directories_file.json")
        self.tempfile: Path = Path.cwd() / Path("temp_sync_directories_file.json")
        self.test_path1: Path = Path.cwd() / Path("test_dir1")
        self.test_path2: Path = Path.cwd() / Path("test_dir2")
        super().__init__(*args, **kwargs)

    def test_no_config_file(self) -> None:
        """Tests if no config file exists."""
        # Move config file contents and delete config file
        if self.sync_dir_file.exists():
            with self.tempfile.open("w") as json_file:
                json.dump(get_json_contents(self.sync_dir_file), json_file)
            self.sync_dir_file.unlink()

        # Run function and check result
        manager: ConfigManager = ConfigManager()
        buffer: List[str] = manager.read_sync_directories()
        self.assertEqual(buffer, [])

        # Clean up after test
        if self.tempfile.exists():
            with self.sync_dir_file.open("w") as json_file:
                json.dump(get_json_contents(self.tempfile), json_file)
                self.tempfile.unlink()

    def test_check_invalid_dirs(self) -> None:
        # Deletes invalid directory just in case it exists
        if self.test_path1.exists():
            shutil.rmtree(self.test_path1)

        # Checks if invalid dir is added to result
        manager: ConfigManager = ConfigManager()
        result: List[str] = manager.check_sync_directory(str(self.test_path1), [])
        self.assertEqual(result, [])

    def test_valid_directories(self):
        # Move config file contents and delete config file
        if self.sync_dir_file.exists():
            with self.tempfile.open("w") as json_file:
                json.dump(get_json_contents(self.sync_dir_file), json_file)
            self.sync_dir_file.unlink()

        # Create test directories
        if not self.test_path1.exists():
            self.test_path1.mkdir()
        if not self.test_path2.exists():
            self.test_path2.mkdir()

        # Enter correct directories
        with self.sync_dir_file.open("w") as json_file:
            json.dump([str(self.test_path1), str(self.test_path2)], json_file)
        user_entry: Tuple[str, str] = (str(self.test_path1), str(self.test_path2))

        # Run Test
        manager: ConfigManager = ConfigManager()
        buffer: List[str] = manager.read_sync_directories()

        # Clean up after test
        if self.test_path1.exists():
            shutil.rmtree(self.test_path1)
        if self.test_path1.exists():
            shutil.rmtree(self.test_path2)
        if self.tempfile.exists():
            with self.sync_dir_file.open("w") as json_file:
                json.dump(get_json_contents(self.tempfile), json_file)
                self.tempfile.unlink()

        # Check after clean-up so assertion error doesn't prevent clean-up
        self.assertEqual(user_entry, tuple(buffer))


if __name__ == "__main__":
    unittest.main()
