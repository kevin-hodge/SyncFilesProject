"""Sync Files Project Test


Author: Kevin Hodge
"""
from typing import List, Any, Dict, Optional, Tuple
from pathlib import Path
import shutil
import json
import unittest
from tests.tfuncs import TFunctions
from syncfiles.config_manager import ConfigManager
from syncfiles.file_structure import FileStructure


class ConfigManagerTestCase(unittest.TestCase):
    """Test case for ConfigManager"""
    def __init__(self, *args, **kwargs) -> None:
        self.tf: TFunctions = TFunctions()
        super().__init__(*args, **kwargs)

    @TFunctions.handle_dir_tempfile
    def test_no_config_file(self) -> None:
        """Tests if no config file exists."""
        # Run function and check result
        manager: ConfigManager = ConfigManager()
        buffer: List[str] = manager.read_sync_directories()
        self.assertCountEqual(buffer, [])

    def test_check_nonexistant_dirs(self) -> None:
        # Deletes invalid directory just in case it exists
        self.tf.remove_test_dirs()

        # Checks if invalid dir is added to result
        manager: ConfigManager = ConfigManager()
        result: List[str] = manager.check_sync_directory(str(self.tf.test_path1), [])
        self.assertCountEqual(result, [])

    @TFunctions.handle_dir_tempfile
    @TFunctions.handle_test_dirs
    def test_check_repeated_dirs(self) -> None:
        # Set up config and directories (so directory is not removed because it does not exist)
        # Run Test
        input: List[str] = [str(self.tf.test_path1)]
        manager: ConfigManager = ConfigManager()
        result: List[str] = manager.check_sync_directory(str(self.tf.test_path1), input)

        # Check Result
        self.assertCountEqual(result, input)

    @TFunctions.handle_dir_tempfile
    @TFunctions.handle_test_dirs
    def test_check_valid_dirs(self) -> None:
        # Set up config and directories (so directory is not removed because it does not exist)
        # Run Test
        input: List[str] = [str(self.tf.test_path1)]
        manager: ConfigManager = ConfigManager()
        result: List[str] = manager.check_sync_directory(str(self.tf.test_path2), input)

        # Check Result
        self.assertCountEqual(result, [str(self.tf.test_path1), str(self.tf.test_path2)])

    @TFunctions.handle_dir_tempfile
    def test_read_not_list(self) -> None:
        # Write invalid contents
        input: str = "JSON contents are not a list"
        self.tf.write_json(input, self.tf.sync_dir_file)
        manager: ConfigManager = ConfigManager()
        result: List[str] = manager.read_sync_directories()

        # Check result
        self.assertCountEqual(result, [])

    @TFunctions.handle_dir_tempfile
    def test_read_nonexistant_dirs(self) -> None:
        # Set up
        self.tf.remove_test_dirs()

        # Checks if invalid dir is returned
        with self.tf.sync_dir_file.open("w") as json_file:
            json.dump([str(self.tf.test_path1), str(self.tf.test_path2)], json_file)
        manager: ConfigManager = ConfigManager()
        result: List[str] = manager.read_sync_directories()

        # Check result
        self.assertCountEqual(result, [])

    @TFunctions.handle_dir_tempfile
    @TFunctions.handle_test_dirs
    def test_read_repeated_dirs(self) -> None:
        # Enter and read repeated directories
        input: List[str] = [str(self.tf.test_path2), str(self.tf.test_path2)]
        self.tf.write_json(input, self.tf.sync_dir_file)
        manager: ConfigManager = ConfigManager()
        result: List[str] = manager.read_sync_directories()

        # Check result
        self.assertCountEqual(result, [str(self.tf.test_path2)])

    @TFunctions.handle_dir_tempfile
    @TFunctions.handle_test_dirs
    def test_read_valid_dirs(self) -> None:
        # Enter and read correct directories
        input: List[str] = [str(self.tf.test_path1), str(self.tf.test_path2)]
        self.tf.write_json(input, self.tf.sync_dir_file)
        user_entry: List[str] = [str(self.tf.test_path1), str(self.tf.test_path2)]
        manager: ConfigManager = ConfigManager()
        buffer: List[str] = manager.read_sync_directories()

        # Check after clean-up so assertion error doesn't prevent clean-up
        self.assertCountEqual(user_entry, buffer)

    @TFunctions.handle_dir_tempfile
    def test_write_valid_dirs(self) -> None:
        # Setup: Move config contents
        # Write to config and check config contents
        input: List[str] = [str(self.tf.test_path1), str(self.tf.test_path2)]
        manager: ConfigManager = ConfigManager()
        assert manager.write_sync_directories(input)
        result: List[str] = self.tf.get_json_contents(self.tf.sync_dir_file)
        self.assertCountEqual(input, result)

    @TFunctions.handle_dir_tempfile
    def test_write_too_few_dirs(self) -> None:
        # Setup: Move config contents
        self.tf.create_dir_tempfile()

        # Write to config and check config contents
        input: List[str] = [str(self.tf.test_path2)]
        manager: ConfigManager = ConfigManager()
        assert not manager.write_sync_directories(input)
        assert not self.tf.sync_dir_file.exists()

    @TFunctions.handle_dir_tempfile
    def test_write_not_list(self) -> None:
        # Write to config and check config contents
        input: Tuple[str, str] = (str(self.tf.test_path1), str(self.tf.test_path2))
        manager: ConfigManager = ConfigManager()
        with self.assertRaises(AssertionError):
            manager.write_sync_directories(input)  # type: ignore[arg-type]

    @TFunctions.handle_last_tempfile
    def test_no_last_sync(self) -> None:
        # Initialize
        last_sync_files: Dict[str, Any]
        last_sync_time: float
        manager: ConfigManager = ConfigManager()

        # Run test
        last_sync_files, last_sync_time = manager.read_last_sync_file()
        self.assertCountEqual(last_sync_files, dict())
        self.assertEqual(last_sync_time, 0.0)

    @TFunctions.handle_last_tempfile
    def test_valid_last_sync(self) -> None:
        # Setup: remove last_sync_file, create file_dict and file_time
        file_dict: Dict[str, Any] = self.tf.create_rand_fstruct(str(self.tf.test_path2))
        file_time: float = 0.0

        # Load data to last_sync_file and initialize
        self.tf.write_json([file_dict, file_time], self.tf.last_sync_file)
        last_sync_files: Dict[str, Any]
        last_sync_time: float
        manager: ConfigManager = ConfigManager()

        # Run test
        last_sync_files, last_sync_time = manager.read_last_sync_file()
        self.assertCountEqual(last_sync_files, file_dict)
        self.assertEqual(last_sync_time, file_time)

        # Teardown
        self.tf.remove_test_dirs()


class FileStructureTestCase(unittest.TestCase):
    """Test case for FileStructure"""
    def __init__(self, *args, **kwargs) -> None:
        self.tf: TFunctions = TFunctions()
        super().__init__(*args, **kwargs)

    def test_init_nonexistant_dir(self) -> None:
        # Delete directory just in case it exists
        if self.tf.test_path1.exists():
            shutil.rmtree(self.tf.test_path1)
        with self.assertRaises(AssertionError):
            FileStructure(str(self.tf.test_path1))  # type: ignore[arg-type]

    def test_get_rand_fstruct(self) -> None:
        if self.tf.test_path1.exists():
            shutil.rmtree(self.tf.test_path1)
        
        error: Optional[Exception] = None
        try:
            # Build, get, and print directory
            file_dict: Dict[str, Any] = self.tf.create_rand_fstruct(str(self.tf.test_path1))
            fstruct: FileStructure = FileStructure(str(self.tf.test_path1))
            fstruct.get_file_structure()
            fstruct.print_file_structure()
            self.assertCountEqual(file_dict, fstruct.files)
        except Exception as oops:
            error = oops
        finally:
            shutil.rmtree(self.tf.test_path1)
        if error is not None:
            raise error

    @TFunctions.handle_last_tempfile
    def test_get_updated(self) -> None:
        if self.tf.test_path1.exists():
            shutil.rmtree(self.tf.test_path1)

        # Set up
        self.tf.create_rand_fstruct(str(self.tf.test_path1))
        fstruct: FileStructure = FileStructure(str(self.tf.test_path1))
        fstruct.get_file_structure()
        self.tf.write_json(fstruct.files, self.tf.last_sync_file)
        file_dict = self.tf.make_rand_mods(fstruct.directory_path, fstruct.files)

        # Run check
        # updated: Dict[str, Any] = fstruct.check_file_structure()

        # Check results

    def test_get_dict_value(self):
        pass


if __name__ == "__main__":
    unittest.main()
