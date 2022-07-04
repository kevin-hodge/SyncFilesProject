"""Sync Files Project: sync_manager Test

Author: Kevin Hodge
"""

from typing import List, Dict, Any
import unittest
from pathlib import Path
from syncfiles.file_structure import FileStructure
from syncfiles.sync_manager import SyncManager
import tests.tfuncs as tfuncs
from tests.tfuncs import TFunctions


class SyncManagerTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs) -> None:
        self.tf = TFunctions()
        super().__init__(*args, **kwargs)

    @tfuncs.handle_test_dirs
    def test_file_in1_notin2_updated1(self) -> None:
        fstruct_list: List[FileStructure] = self.initialize_test_directories()
        last_sync_dict: Dict[str, Any] = fstruct_list[0].files_to_json()

        test_filename: str = "test_file.txt"
        file_in1_notin2: Path = self.tf.test_path1 / test_filename
        self.tf.create_file(file_in1_notin2)
        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)

        SyncManager(fstruct_list)

        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)
        files_in1: List[str] = fstruct_list[0].files_to_list()
        files_in1 = tfuncs.remove_prefixes(files_in1, fstruct_list[0].directory_path)
        files_in2: List[str] = fstruct_list[1].files_to_list()
        files_in2 = tfuncs.remove_prefixes(files_in2, fstruct_list[1].directory_path)
        self.assertCountEqual(files_in1, files_in2)
        self.assertCountEqual(files_in1, [test_filename])
        self.assertCountEqual(files_in2, [test_filename])

    def initialize_test_directories(self) -> List[FileStructure]:
        test_dir1: str = str(self.tf.test_path1)
        fstruct1: FileStructure = FileStructure(test_dir1)
        test_dir2: str = str(self.tf.test_path2)
        fstruct2: FileStructure = FileStructure(test_dir2)
        return [fstruct1, fstruct2]

    def check_fstructs_for_updates(self, fstruct_list: List[FileStructure],
                                   last_sync_dict: Dict[str, Any]) -> None:
        for fstruct in fstruct_list:
            fstruct.update_file_structure()
            fstruct.check_file_structure(last_sync_dict)

    @tfuncs.handle_test_dirs
    def test_file_in1_notin2_notupdated1(self) -> None:
        file_in1_notin2: Path = self.tf.test_path1 / "test_file.txt"
        self.tf.create_file(file_in1_notin2)

        fstruct_list: List[FileStructure] = self.initialize_test_directories()
        last_sync_dict: Dict[str, Any] = fstruct_list[0].files_to_json()
        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)

        SyncManager(fstruct_list)

        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)
        files_in1: List[str] = fstruct_list[0].files_to_list()
        files_in1 = tfuncs.remove_prefixes(files_in1, fstruct_list[0].directory_path)
        files_in2: List[str] = fstruct_list[1].files_to_list()
        files_in2 = tfuncs.remove_prefixes(files_in2, fstruct_list[1].directory_path)
        self.assertCountEqual(files_in1, files_in2)
        self.assertCountEqual(files_in1, [])
        self.assertCountEqual(files_in2, [])

    @tfuncs.handle_test_dirs
    def test_file_notin1_in2_updated2(self) -> None:
        fstruct_list: List[FileStructure] = self.initialize_test_directories()
        last_sync_dict: Dict[str, Any] = fstruct_list[1].files_to_json()

        test_filename: str = "test_file.txt"
        file_notin1_in2: Path = self.tf.test_path2 / test_filename
        self.tf.create_file(file_notin1_in2)
        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)

        SyncManager(fstruct_list)

        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)
        files_in1: List[str] = fstruct_list[0].files_to_list()
        files_in1 = tfuncs.remove_prefixes(files_in1, fstruct_list[0].directory_path)
        files_in2: List[str] = fstruct_list[1].files_to_list()
        files_in2 = tfuncs.remove_prefixes(files_in2, fstruct_list[1].directory_path)
        self.assertCountEqual(files_in1, files_in2)
        self.assertCountEqual(files_in1, [test_filename])
        self.assertCountEqual(files_in2, [test_filename])

    @tfuncs.handle_test_dirs
    def test_file_notin1_in2_notupdated1(self) -> None:
        file_notin1_in2: Path = self.tf.test_path2 / "test_file.txt"
        self.tf.create_file(file_notin1_in2)

        fstruct_list: List[FileStructure] = self.initialize_test_directories()
        last_sync_dict: Dict[str, Any] = fstruct_list[1].files_to_json()
        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)

        SyncManager(fstruct_list)

        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)
        files_in1: List[str] = fstruct_list[0].files_to_list()
        files_in1 = tfuncs.remove_prefixes(files_in1, fstruct_list[0].directory_path)
        files_in2: List[str] = fstruct_list[1].files_to_list()
        files_in2 = tfuncs.remove_prefixes(files_in2, fstruct_list[1].directory_path)
        self.assertCountEqual(files_in1, files_in2)
        self.assertCountEqual(files_in1, [])
        self.assertCountEqual(files_in2, [])


if __name__ == "__main__":
    unittest.main()
