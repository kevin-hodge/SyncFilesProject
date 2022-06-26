"""Sync Files Project: file_manager Test

Author: Kevin Hodge
"""

from typing import List, Any, Dict
import unittest
import tests.tfuncs as tfuncs
from tests.tfuncs import TFunctions
from syncfiles.file_structure import FileStructure


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
        self.tf.remove_test_dirs()
        test_directory: str = str(self.tf.test_path1)
        self.tf.create_rand_fstruct(test_directory)
        fstruct: FileStructure = FileStructure(test_directory)
        last_sync_files: Dict[str, Any] = fstruct.files_to_json()
        # fstruct.print_file_structure()
        change_list: List[str]
        change_list = self.tf.make_rand_mods(test_directory)
        print(len(change_list))
        # print(change_list)
        fstruct.update_file_structure()

        changes_found: int = fstruct.check_file_structure(last_sync_files)
        print(changes_found)
        fstruct.print_file_structure()
        self.tf.recursive_print_dir(test_directory)
        self.assertEqual(changes_found, len(change_list))
        print(fstruct.get_updated_list())
        print(change_list)
        self.maxDiff = None
        self.assertCountEqual(sorted(fstruct.get_updated_list()), sorted(change_list))

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
