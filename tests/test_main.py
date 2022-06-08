"""Sync Files Project Test


Author: Kevin Hodge
"""
from typing import List, Any, Dict, Optional, Tuple
import shutil
import json
import unittest
from tests.tfuncs import TFunctions
from syncfiles.config_manager import ConfigManager
from syncfiles.file_structure import FileStructure, dir_entry


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
        manager: ConfigManager = ConfigManager()

        # Run test
        last_sync_files: Dict[str, Any] = manager.read_last_sync_file()
        self.assertCountEqual(last_sync_files, dict())

    @TFunctions.handle_last_tempfile
    @TFunctions.handle_test_dirs
    def test_valid_last_sync(self) -> None:
        # Setup
        file_dict: Dict[str, Any] = self.tf.create_rand_fstruct(str(self.tf.test_path2))
        self.tf.write_json(file_dict, self.tf.last_sync_file)
        last_sync_files: Dict[str, Any]
        manager: ConfigManager = ConfigManager()

        # Run test
        last_sync_files = manager.read_last_sync_file()
        self.assertCountEqual(last_sync_files, file_dict)

    @TFunctions.handle_last_tempfile
    @TFunctions.handle_test_dirs
    def test_write_last_sync(self) -> None:
        # Setup
        file_dict: Dict[str, Any] = self.tf.create_rand_fstruct(str(self.tf.test_path2))
        manager: ConfigManager = ConfigManager()
        manager.write_last_sync_file(file_dict)

        # Run test
        last_sync_files: Dict[str, Any] = self.tf.get_json_contents(self.tf.last_sync_file)
        self.assertCountEqual(last_sync_files, file_dict)


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
            # fstruct.print_file_structure()
            self.assertCountEqual(file_dict, fstruct.files)
        except Exception as oops:
            error = oops
        finally:
            shutil.rmtree(self.tf.test_path1)
        if error is not None:
            raise error

    @TFunctions.handle_last_tempfile
    @TFunctions.handle_test_dirs
    def test_get_updated(self) -> None:
        if self.tf.test_path1.exists():
            shutil.rmtree(self.tf.test_path1)

        self.tf.create_rand_fstruct(str(self.tf.test_path1))
        fstruct: FileStructure = FileStructure(str(self.tf.test_path1))
        last_sync_files: dir_entry = fstruct.get_file_structure()
        # fstruct.print_file_structure()
        checksum: int
        change_dict: Dict[str, Any]
        _, checksum, change_dict = self.tf.make_rand_mods(fstruct.directory_path, fstruct.files)
        print(checksum)
        fstruct.get_file_structure()
        self.tf.recursive_print_dict(change_dict)

        # Run check (Needs to FAIL if something is updated and NOT marked as updated or marked but NOT updated)
        changes_found: int = fstruct.check_file_structure(last_sync_files)
        print(changes_found)
        fstruct.print_file_structure()
        self.assertEqual(changes_found, checksum)

    def test_get_dict_value(self) -> None:
        self.tf.remove_test_dirs()

        error: Optional[Exception] = None
        try:
            self.tf.create_rand_fstruct(str(self.tf.test_path1))
            fstruct: FileStructure = FileStructure(str(self.tf.test_path1))
            fstruct.get_file_structure()
            # fstruct.print_file_structure()
            self.tf.recursive_get_entry(self, fstruct, fstruct.files)
            self.tf.recursive_get_entry(self, fstruct, fstruct.files, updated=True)

            self.assertFalse(fstruct.get_dict_value(str(self.tf.test_path2), fstruct.files))
        except Exception as oops:
            error = oops
        finally:
            if self.tf.test_path1.exists():
                shutil.rmtree(self.tf.test_path1)

        if error is not None:
            raise error

    def test_set_dict_updated(self) -> None:
        self.tf.remove_test_dirs()

        error: Optional[Exception] = None
        try:
            self.tf.create_rand_fstruct(str(self.tf.test_path2))
            fstruct: FileStructure = FileStructure(str(self.tf.test_path2))
            fstruct.get_file_structure()
            # fstruct.print_file_structure()

            # Set values
            self.tf.recursive_set_updated(self, fstruct, fstruct.files)
        except Exception as oops:
            error = oops
        finally:
            if self.tf.test_path2.exists():
                shutil.rmtree(self.tf.test_path2)

        if error is not None:
            raise error

    @TFunctions.handle_last_tempfile
    @TFunctions.handle_test_dirs
    def test_json_conversion(self) -> None:
        # Create fstruct
        self.tf.create_rand_fstruct(str(self.tf.test_path1))
        fstruct: FileStructure = FileStructure(str(self.tf.test_path1))
        before_files: dir_entry = fstruct.get_file_structure()
        before_dict: Dict[str, Any] = fstruct.to_json(before_files)
        self.tf.write_json(before_dict, self.tf.last_tempfile)
        after_dict: Dict[str, Any] = self.tf.get_json_contents(self.tf.last_tempfile)
        self.assertCountEqual(before_dict, after_dict)
        after_files: dir_entry = fstruct.from_json(after_dict)
        self.assertCountEqual(before_files, after_files)


if __name__ == "__main__":
    unittest.main()
