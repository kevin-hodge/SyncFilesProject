"""Sync Files Project Test


Author: Kevin Hodge
"""
from typing import List, Any, Dict, Tuple
import unittest
import tests.tfuncs as tfuncs
from tests.tfuncs import TFunctions
from syncfiles.config_manager import ConfigManager
from syncfiles.file_structure import FileStructure


class ConfigManagerTestCase(unittest.TestCase):
    """Test case for ConfigManager"""
    def __init__(self, *args, **kwargs) -> None:
        self.tf: TFunctions = TFunctions()
        super().__init__(*args, **kwargs)

    @tfuncs.handle_dir_tempfile
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
        tfuncs.write_json(input, self.tf.sync_dir_file)
        manager: ConfigManager = ConfigManager()
        result: List[str] = manager.read_sync_directories()

        # Check result
        self.assertCountEqual(result, [])

    @tfuncs.handle_dir_tempfile
    def test_read_nonexistant_dirs(self) -> None:
        self.tf.remove_test_dirs()
        invalid_dirs: List[str] = [str(self.tf.test_path1), str(self.tf.test_path2)]
        tfuncs.write_json(invalid_dirs, self.tf.sync_dir_file)
        manager: ConfigManager = ConfigManager()
        result: List[str] = manager.read_sync_directories()

        # Check result
        self.assertCountEqual(result, [])

    @tfuncs.handle_dir_tempfile
    @tfuncs.handle_test_dirs
    def test_read_repeated_dirs(self) -> None:
        # Enter and read repeated directories
        input: List[str] = [str(self.tf.test_path2), str(self.tf.test_path2)]
        tfuncs.write_json(input, self.tf.sync_dir_file)
        manager: ConfigManager = ConfigManager()
        result: List[str] = manager.read_sync_directories()

        # Check result
        self.assertCountEqual(result, [str(self.tf.test_path2)])

    @tfuncs.handle_dir_tempfile
    @tfuncs.handle_test_dirs
    def test_read_valid_dirs(self) -> None:
        # Enter and read correct directories
        input: List[str] = [str(self.tf.test_path1), str(self.tf.test_path2)]
        tfuncs.write_json(input, self.tf.sync_dir_file)
        user_entry: List[str] = [str(self.tf.test_path1), str(self.tf.test_path2)]
        manager: ConfigManager = ConfigManager()
        buffer: List[str] = manager.read_sync_directories()

        # Check after clean-up so assertion error doesn't prevent clean-up
        self.assertCountEqual(user_entry, buffer)

    @tfuncs.handle_dir_tempfile
    def test_write_valid_dirs(self) -> None:
        # Setup: Move config contents
        # Write to config and check config contents
        input: List[str] = [str(self.tf.test_path1), str(self.tf.test_path2)]
        manager: ConfigManager = ConfigManager()
        assert manager.write_sync_directories(input)
        result: List[str] = tfuncs.get_json_contents(self.tf.sync_dir_file)
        self.assertCountEqual(input, result)

    @tfuncs.handle_dir_tempfile
    def test_write_too_few_dirs(self) -> None:
        # Setup: Move config contents
        self.tf.create_dir_tempfile()

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
    def test_valid_last_sync(self) -> None:
        # Setup
        self.tf.create_rand_fstruct(str(self.tf.test_path2))
        fstruct: FileStructure = FileStructure(str(self.tf.test_path2))
        tfuncs.write_json(fstruct.files_to_json(), self.tf.last_sync_file)
        last_sync_files: Dict[str, Any]
        manager: ConfigManager = ConfigManager()

        # Run test
        last_sync_files = manager.read_last_sync_file()
        self.assertCountEqual(last_sync_files, fstruct.files_to_json())

    @tfuncs.handle_last_tempfile
    @tfuncs.handle_test_dirs
    def test_write_last_sync(self) -> None:
        test_directory: str = str(self.tf.test_path2)
        self.tf.create_rand_fstruct(test_directory)
        fstruct: FileStructure = FileStructure(test_directory)
        manager: ConfigManager = ConfigManager()
        manager.write_last_sync_file(fstruct.files_to_json())

        # Run test
        last_sync_files: Dict[str, Any] = tfuncs.get_json_contents(self.tf.last_sync_file)
        self.assertCountEqual(last_sync_files, fstruct.files_to_json())


class FileStructureTestCase(unittest.TestCase):
    """Test case for FileStructure"""
    def __init__(self, *args, **kwargs) -> None:
        self.tf: TFunctions = TFunctions()
        super().__init__(*args, **kwargs)

    def test_init_nonexistant_dir(self) -> None:
        # Delete directory just in case it exists
        test_directory: str = str(self.tf.test_path1)
        self.tf.remove_test_dirs()
        with self.assertRaises(AssertionError):
            FileStructure(test_directory)  # type: ignore[arg-type]

    @tfuncs.handle_test_dirs
    def test_get_rand_fstruct(self) -> None:
        test_directory: str = str(self.tf.test_path1)
        self.tf.remove_test_dirs()
        self.tf.create_rand_fstruct(test_directory)
        fstruct: FileStructure = FileStructure(test_directory)
        self.assertCountEqual(self.tf.dir_to_list(test_directory), fstruct.files_to_list())

    @tfuncs.handle_last_tempfile
    @tfuncs.handle_test_dirs
    def test_get_updated(self) -> None:
        test_directory: str = str(self.tf.test_path1)
        self.tf.remove_test_dirs()
        self.tf.create_rand_fstruct(test_directory)
        fstruct: FileStructure = FileStructure(test_directory)
        last_sync_files: Dict[str, Any] = fstruct.files_to_json()
        fstruct.print_file_structure()
        num_changes: int
        num_changes = self.tf.make_rand_mods(test_directory)
        print(num_changes)
        fstruct.update_file_structure()

        # Run check (Needs to FAIL if something is updated and NOT marked as updated or marked but NOT updated)
        changes_found: int = fstruct.check_file_structure(last_sync_files)
        print(changes_found)
        fstruct.print_file_structure()
        # self.tf.recursive_print_dir(test_directory)
        self.assertEqual(changes_found, num_changes)

    @tfuncs.handle_last_tempfile
    @tfuncs.handle_test_dirs
    def test_json_conversion(self) -> None:
        test_directory: str = str(self.tf.test_path1)
        self.tf.create_rand_fstruct(test_directory)
        fstruct: FileStructure = FileStructure(test_directory)
        before_dict: Dict[str, Any] = fstruct.files_to_json()
        tfuncs.write_json(before_dict, self.tf.last_tempfile)
        after_dict: Dict[str, Any] = tfuncs.get_json_contents(self.tf.last_tempfile)
        self.assertCountEqual(before_dict, after_dict)
        self.assertCountEqual(after_dict, fstruct.files_to_json())


if __name__ == "__main__":
    unittest.main()
