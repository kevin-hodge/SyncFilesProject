"""Tests file_structure.py

Author: Kevin Hodge
"""

from typing import List, Any, Dict
import unittest
from pathlib import Path
import time
import tests.tfuncs as tfuncs
from syncfiles.entry import dir_entry, file_entry
from syncfiles.file_system_interface import FSInterface
from syncfiles.sync_exception import SyncException
from syncfiles.file_structure import FileStructure


class FileStructureTestCase(unittest.TestCase):
    """Test case for FileStructure"""
    def __init__(self, *args, **kwargs) -> None:
        self.tf: tfuncs.TFunctions = tfuncs.TFunctions()
        super().__init__(*args, **kwargs)

    @tfuncs.handle_test_dirs
    def test_dir_entry_repr(self) -> None:
        second_level: dir_entry = dir_entry()
        test_file1: file_entry = file_entry()
        test_file1.set_updated()
        second_level.add_entry('test_file1.txt', test_file1)
        second_level.add_entry('test_file2.json', file_entry())
        second_level.add_entry('test_file3.xml', file_entry())
        first_level: dir_entry = dir_entry()
        first_level.add_entry('test_file4.txt', file_entry())
        first_level.add_entry('test_file5.csv', file_entry())
        first_level.add_entry('second_level', second_level)
        validation_string: str = "test_file4.txt: -1.0\n" + "test_file5.csv: -1.0\n" + "second_level\n" + \
            "   test_file1.txt: -1.0 X\n" + "   test_file2.json: -1.0\n" + "   test_file3.xml: -1.0\n"
        assert str(first_level) == validation_string

    @tfuncs.handle_test_dirs
    def test_fstruct_repr(self) -> None:
        second_level: dir_entry = dir_entry()
        test_file1: file_entry = file_entry()
        test_file1.set_updated()
        second_level.add_entry('test_file1.txt', test_file1)
        second_level.add_entry('test_file2.json', file_entry())
        second_level.add_entry('test_file3.xml', file_entry())
        first_level: dir_entry = dir_entry()
        first_level.add_entry('test_file4.txt', file_entry())
        first_level.add_entry('test_file5.csv', file_entry())
        first_level.add_entry('second_level', second_level)
        fstruct: FileStructure = FileStructure(str(tfuncs.TFunctions.test_path1), FSInterface)
        fstruct.files = first_level
        validation_string: str = "test_dir1\n" + "   test_file4.txt: -1.0\n" + "   test_file5.csv: -1.0\n" + \
            "   second_level\n" + "      test_file1.txt: -1.0 X\n" + "      test_file2.json: -1.0\n" + \
            "      test_file3.xml: -1.0\n"
        assert fstruct.print_file_structure() == validation_string

    def test_init_nonexistant_dir(self) -> None:
        test_directory: str = str(self.tf.test_path1)
        self.tf.remove_test_dirs()
        with self.assertRaises(SyncException):
            FileStructure(test_directory, FSInterface)  # type: ignore[arg-type]

    @tfuncs.handle_test_dirs
    def test_get_rand_fstruct(self) -> None:
        test_directory: str = str(self.tf.test_path1)
        self.tf.remove_test_dirs()
        tfuncs.create_rand_fstruct(test_directory)
        fstruct: FileStructure = FileStructure(test_directory, FSInterface)
        self.assertCountEqual(tfuncs.dir_to_list(test_directory), fstruct.files_to_list())

    @tfuncs.handle_test_dirs
    def test_file_modified(self) -> None:
        test_directory: str = str(self.tf.test_path1)
        test_file: str = str(self.tf.test_path1 / "test_file1.txt")
        tfuncs.create_file(test_file)
        fstruct: FileStructure = FileStructure(test_directory, FSInterface)
        last_sync_files: Dict[str, Any] = fstruct.files_to_json()
        time.sleep(10e-6)  # wait before making mods so mod time is later than creation time
        tfuncs.update_last_mod_time(test_file)
        fstruct.update_file_structure()

        changes_found: int = fstruct.check_file_structure(last_sync_files)
        self.assertEqual(changes_found, 1)
        self.assertCountEqual(fstruct.get_updated_list(), [test_file])

    @tfuncs.handle_test_dirs
    def test_file_renamed(self) -> None:
        test_directory: str = str(self.tf.test_path1)
        test_folder_name1: str = "test_folder1"
        test_folder1: str = str(self.tf.test_path1 / test_folder_name1)
        tfuncs.create_directory(test_folder1)
        test_file: str = str(Path(test_folder1) / "test_file1.txt")
        tfuncs.create_file(test_file)
        fstruct: FileStructure = FileStructure(test_directory, FSInterface)
        last_sync_files: Dict[str, Any] = fstruct.files_to_json()
        new_file: str = tfuncs.change_file_name(test_file, 0)
        fstruct.update_file_structure()

        changes_found: int = fstruct.check_file_structure(last_sync_files)
        self.assertEqual(changes_found, 1)
        self.assertCountEqual(fstruct.get_updated_list(), [new_file])

    @tfuncs.handle_test_dirs
    def test_file_added(self) -> None:
        test_directory: str = str(self.tf.test_path1)
        fstruct: FileStructure = FileStructure(test_directory, FSInterface)
        last_sync_files: Dict[str, Any] = fstruct.files_to_json()
        test_file: str = str(Path(test_directory) / "test_file1.txt")
        tfuncs.create_file(test_file)
        fstruct.update_file_structure()

        changes_found: int = fstruct.check_file_structure(last_sync_files)
        self.assertEqual(changes_found, 1)
        self.assertCountEqual(fstruct.get_updated_list(), [test_file])

    @tfuncs.handle_test_dirs
    def test_folder_renamed(self) -> None:
        test_directory: str = str(self.tf.test_path1)
        test_folder: str = str(self.tf.test_path1 / "test_folder1")
        tfuncs.create_directory(test_folder)
        fstruct: FileStructure = FileStructure(test_directory, FSInterface)
        last_sync_files: Dict[str, Any] = fstruct.files_to_json()
        new_folder: str = tfuncs.change_dir_name(test_folder, 0)
        fstruct.update_file_structure()

        changes_found: int = fstruct.check_file_structure(last_sync_files)
        self.assertEqual(changes_found, 1)
        self.assertCountEqual(fstruct.get_updated_list(), [new_folder])

    @tfuncs.handle_test_dirs
    def test_folder_added(self) -> None:
        test_directory: str = str(self.tf.test_path1)
        fstruct: FileStructure = FileStructure(test_directory, FSInterface)
        last_sync_files: Dict[str, Any] = fstruct.files_to_json()
        test_folder: str = str(self.tf.test_path1 / "test_folder1")
        tfuncs.create_directory(test_folder)
        fstruct.update_file_structure()

        changes_found: int = fstruct.check_file_structure(last_sync_files)
        self.assertEqual(changes_found, 1)
        self.assertCountEqual(fstruct.get_updated_list(), [test_folder])

    @tfuncs.handle_test_dirs
    def test_parent_folder_renamed(self) -> None:
        test_directory: str = str(self.tf.test_path1)
        test_folder_name1: str = "test_folder1"
        test_folder1: str = str(self.tf.test_path1 / test_folder_name1)
        tfuncs.create_directory(test_folder1)
        test_folder_name2: str = "test_folder2"
        test_folder2: str = str(Path(test_folder1) / test_folder_name2)
        tfuncs.create_directory(test_folder2)
        test_file_name: str = "test_file1.txt"
        test_file: str = str(Path(test_folder2) / test_file_name)
        tfuncs.create_file(test_file)
        fstruct: FileStructure = FileStructure(test_directory, FSInterface)
        last_sync_files: Dict[str, Any] = fstruct.files_to_json()
        new_folder1: str = tfuncs.change_dir_name(test_folder1, 0)
        new_folder2: str = str(Path(new_folder1) / test_folder_name2)
        new_file: str = str(Path(new_folder2) / test_file_name)
        fstruct.update_file_structure()

        changes_found: int = fstruct.check_file_structure(last_sync_files)
        self.assertEqual(changes_found, 3)
        self.assertCountEqual(sorted(fstruct.get_updated_list()),
                              sorted([new_folder1, new_folder2, new_file]))

    @tfuncs.handle_test_dirs
    def test_no_last_sync_file(self) -> None:
        test_directory: str = str(self.tf.test_path1)
        test_folder_name1: str = "test_folder1"
        test_folder1: str = str(self.tf.test_path1 / test_folder_name1)
        tfuncs.create_directory(test_folder1)
        test_file: str = str(Path(test_folder1) / "test_file1.txt")
        tfuncs.create_file(test_file)
        fstruct: FileStructure = FileStructure(test_directory, FSInterface)
        fstruct.update_file_structure()

        changes_found: int = fstruct.check_file_structure({})
        self.assertEqual(changes_found, 2)
        self.assertCountEqual(fstruct.get_updated_list(), [test_file, test_folder1])

    @tfuncs.handle_test_dirs
    def test_random_updated(self) -> None:
        test_directory: str = str(self.tf.test_path1)
        tfuncs.create_rand_fstruct(test_directory)
        fstruct: FileStructure = FileStructure(test_directory, FSInterface)
        last_sync_files: Dict[str, Any] = fstruct.files_to_json()
        time.sleep(10e-6)  # wait before making mods so mod time is later than creation time
        change_list: List[str] = tfuncs.make_rand_mods(test_directory)
        fstruct.update_file_structure()

        changes_found: int = fstruct.check_file_structure(last_sync_files)
        self.assertCountEqual(sorted(fstruct.get_updated_list()), sorted(change_list))
        self.assertEqual(changes_found, len(change_list))

    @tfuncs.handle_last_tempfile
    @tfuncs.handle_test_dirs
    def test_json_conversion(self) -> None:
        test_directory: str = str(self.tf.test_path1)
        tfuncs.create_rand_fstruct(test_directory)
        fstruct: FileStructure = FileStructure(test_directory, FSInterface)
        before_dict: Dict[str, Any] = fstruct.files_to_json()
        tfuncs.write_json(before_dict, str(self.tf.last_tempfile))
        after_dict: Dict[str, Any] = tfuncs.get_json_contents(str(self.tf.last_tempfile))
        self.assertCountEqual(before_dict, after_dict)
        self.assertCountEqual(after_dict, fstruct.files_to_json())


if __name__ == "__main__":
    unittest.main()
