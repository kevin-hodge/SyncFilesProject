"""Sync Files Project: config_manager Test

Author: Kevin Hodge
"""

from typing import List, Any, Dict, Tuple
import unittest
import tests.tfuncs as tfuncs
from syncfiles.config_manager import ConfigManager
from syncfiles.file_structure import FileStructure


class ConfigManagerTestCase(unittest.TestCase):
    """Test case for ConfigManager"""
    def __init__(self, *args, **kwargs) -> None:
        self.tf: tfuncs.TFunctions = tfuncs.TFunctions()
        super().__init__(*args, **kwargs)

    @tfuncs.handle_dir_tempfile
    def test_no_config_file(self) -> None:
        """Tests if no config file exists."""
        # Run function and check result
        manager: ConfigManager = ConfigManager()
        buffer: List[str] = manager.read_sync_directories()
        self.assertCountEqual(buffer, [])

    def test_check_nonexistant_dirs(self) -> None:
        # Remove test dirs just in case they exist
        self.tf.remove_test_dirs()

        # Checks if invalid dir is added to result
        manager: ConfigManager = ConfigManager()
        result: List[str] = manager.check_sync_directory(str(self.tf.test_path1), [])
        self.assertCountEqual(result, [])

    @tfuncs.handle_dir_tempfile
    @tfuncs.handle_test_dirs
    def test_check_repeated_dirs(self) -> None:
        # Set up config and directories (so directory is not removed because it does not exist)
        # Run Test
        input: List[str] = [str(self.tf.test_path1)]
        manager: ConfigManager = ConfigManager()
        result: List[str] = manager.check_sync_directory(str(self.tf.test_path1), input)

        # Check Result
        self.assertCountEqual(result, input)

    @tfuncs.handle_dir_tempfile
    @tfuncs.handle_test_dirs
    def test_check_valid_dirs(self) -> None:
        # Set up config and directories (so directory is not removed because it does not exist)
        # Run Test
        input: List[str] = [str(self.tf.test_path1)]
        manager: ConfigManager = ConfigManager()
        result: List[str] = manager.check_sync_directory(str(self.tf.test_path2), input)

        # Check Result
        self.assertCountEqual(result, [str(self.tf.test_path1), str(self.tf.test_path2)])

    @tfuncs.handle_dir_tempfile
    def test_read_not_list(self) -> None:
        # Write invalid contents
        input: str = "JSON contents are not a list"
        tfuncs.write_json(input, str(self.tf.sync_dir_file))
        manager: ConfigManager = ConfigManager()
        result: List[str] = manager.read_sync_directories()

        # Check result
        self.assertCountEqual(result, [])

    @tfuncs.handle_dir_tempfile
    def test_read_nonexistant_dirs(self) -> None:
        self.tf.remove_test_dirs()
        invalid_dirs: List[str] = [str(self.tf.test_path1), str(self.tf.test_path2)]
        tfuncs.write_json(invalid_dirs, str(self.tf.sync_dir_file))
        manager: ConfigManager = ConfigManager()
        result: List[str] = manager.read_sync_directories()

        # Check result
        self.assertCountEqual(result, [])

    @tfuncs.handle_dir_tempfile
    @tfuncs.handle_test_dirs
    def test_read_repeated_dirs(self) -> None:
        # Enter and read repeated directories
        input: List[str] = [str(self.tf.test_path2), str(self.tf.test_path2)]
        tfuncs.write_json(input, str(self.tf.sync_dir_file))
        manager: ConfigManager = ConfigManager()
        result: List[str] = manager.read_sync_directories()

        # Check result
        self.assertCountEqual(result, [str(self.tf.test_path2)])

    @tfuncs.handle_dir_tempfile
    @tfuncs.handle_test_dirs
    def test_read_valid_dirs(self) -> None:
        # Enter and read correct directories
        input: List[str] = [str(self.tf.test_path1), str(self.tf.test_path2)]
        tfuncs.write_json(input, str(self.tf.sync_dir_file))
        user_entry: List[str] = [str(self.tf.test_path1), str(self.tf.test_path2)]
        manager: ConfigManager = ConfigManager()
        buffer: List[str] = manager.read_sync_directories()

        # Check after clean-up so assertion error doesn't prevent clean-up
        self.assertCountEqual(user_entry, buffer)

    @tfuncs.handle_dir_tempfile
    def test_write_valid_dirs(self) -> None:
        # Write to config and check config contents
        input: List[str] = [str(self.tf.test_path1), str(self.tf.test_path2)]
        manager: ConfigManager = ConfigManager()
        assert manager.write_sync_directories(input)
        result: List[str] = tfuncs.get_json_contents(str(self.tf.sync_dir_file))
        self.assertCountEqual(input, result)

    @tfuncs.handle_dir_tempfile
    def test_write_too_few_dirs(self) -> None:
        # Write to config and check config contents
        input: List[str] = [str(self.tf.test_path2)]
        manager: ConfigManager = ConfigManager()
        assert not manager.write_sync_directories(input)
        assert not self.tf.sync_dir_file.exists()

    @tfuncs.handle_dir_tempfile
    def test_write_not_list(self) -> None:
        # Write to config and check config contents
        input: Tuple[str, str] = (str(self.tf.test_path1), str(self.tf.test_path2))
        manager: ConfigManager = ConfigManager()
        with self.assertRaises(AssertionError):
            manager.write_sync_directories(input)  # type: ignore[arg-type]

    @tfuncs.handle_last_tempfile
    def test_no_last_sync(self) -> None:
        # Initialize
        manager: ConfigManager = ConfigManager()

        # Run test
        last_sync_files: Dict[str, Any] = manager.read_last_sync_file()
        self.assertCountEqual(last_sync_files, dict())

    @tfuncs.handle_last_tempfile
    @tfuncs.handle_test_dirs
    def test_read_last_sync(self) -> None:
        # Setup
        tfuncs.create_rand_fstruct(str(self.tf.test_path2))
        fstruct: FileStructure = FileStructure(str(self.tf.test_path2))
        tfuncs.write_json(fstruct.files_to_json(), str(self.tf.last_sync_file))
        last_sync_files: Dict[str, Any]
        manager: ConfigManager = ConfigManager()

        # Run test
        last_sync_files = manager.read_last_sync_file()
        self.assertCountEqual(last_sync_files, fstruct.files_to_json())

    @tfuncs.handle_last_tempfile
    @tfuncs.handle_test_dirs
    def test_write_last_sync(self) -> None:
        test_directory: str = str(self.tf.test_path2)
        tfuncs.create_rand_fstruct(test_directory)
        fstruct: FileStructure = FileStructure(test_directory)
        manager: ConfigManager = ConfigManager()
        manager.write_last_sync_file(fstruct.files_to_json())

        # Run test
        last_sync_files: Dict[str, Any] = tfuncs.get_json_contents(str(self.tf.last_sync_file))
        self.assertCountEqual(last_sync_files, fstruct.files_to_json())


if __name__ == "__main__":
    unittest.main()
