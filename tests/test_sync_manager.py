"""Sync Files Project: sync_manager Test

Author: Kevin Hodge
"""

from typing import List, Dict, Any, Tuple
import unittest
import time
from pathlib import Path
from syncfiles.file_system_interface import FSInterface
from syncfiles.file_structure import FileStructure
from syncfiles.sync_manager import SyncManager
import tests.tfuncs as tfuncs


class SyncManagerTestCase(unittest.TestCase):
    delay_sec: float = 10e-6

    def __init__(self, *args, **kwargs) -> None:
        self.tf: tfuncs.TFunctions = tfuncs.TFunctions()
        super().__init__(*args, **kwargs)

    @tfuncs.handle_test_dirs
    def test_file_in1_notin2_updated1(self) -> None:
        fstruct_list: List[FileStructure] = self.initialize_test_directories()
        last_sync_dict: Dict[str, Any] = fstruct_list[0].files_to_json()

        test_filename: str = "test_file.txt"
        file_in1_notin2: str = str(self.tf.test_path1 / test_filename)
        tfuncs.create_file(file_in1_notin2)
        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)

        synchronizer: SyncManager = SyncManager(fstruct_list, FSInterface)
        synchronizer.sync()

        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)
        files_in1, files_in2 = self.get_file_lists_without_prefixes(fstruct_list)
        self.assertCountEqual(files_in1, files_in2)
        self.assertCountEqual(files_in1, [test_filename])
        self.assertCountEqual(files_in2, [test_filename])

    def initialize_test_directories(self) -> List[FileStructure]:
        test_dir1: str = str(self.tf.test_path1)
        fstruct1: FileStructure = FileStructure(test_dir1, FSInterface)
        test_dir2: str = str(self.tf.test_path2)
        fstruct2: FileStructure = FileStructure(test_dir2, FSInterface)
        return [fstruct1, fstruct2]

    def check_fstructs_for_updates(self, fstruct_list: List[FileStructure],
                                   last_sync_dict: Dict[str, Any]) -> None:
        for fstruct in fstruct_list:
            fstruct.update_file_structure()
            fstruct.check_file_structure(last_sync_dict)

    def get_file_lists_without_prefixes(self, fstruct_list: List[FileStructure]) -> Tuple[List[str], List[str]]:
        files_in1: List[str] = fstruct_list[0].files_to_list()
        files_in1 = tfuncs.remove_prefixes(files_in1, fstruct_list[0].get_directory_path())
        files_in2: List[str] = fstruct_list[1].files_to_list()
        files_in2 = tfuncs.remove_prefixes(files_in2, fstruct_list[1].get_directory_path())
        return files_in1, files_in2

    @tfuncs.handle_test_dirs
    def test_file_in1_notin2_notupdated1(self) -> None:
        file_in1_notin2: str = str(self.tf.test_path1 / "test_file.txt")
        tfuncs.create_file(file_in1_notin2)

        fstruct_list: List[FileStructure] = self.initialize_test_directories()
        last_sync_dict: Dict[str, Any] = fstruct_list[0].files_to_json()
        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)

        synchronizer: SyncManager = SyncManager(fstruct_list, FSInterface)
        synchronizer.sync()

        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)
        files_in1, files_in2 = self.get_file_lists_without_prefixes(fstruct_list)
        self.assertCountEqual(files_in1, files_in2)
        self.assertCountEqual(files_in1, [])
        self.assertCountEqual(files_in2, [])

    @tfuncs.handle_test_dirs
    def test_file_notin1_in2_updated2(self) -> None:
        fstruct_list: List[FileStructure] = self.initialize_test_directories()
        last_sync_dict: Dict[str, Any] = fstruct_list[1].files_to_json()

        test_filename: str = "test_file.txt"
        file_notin1_in2: str = str(self.tf.test_path2 / test_filename)
        tfuncs.create_file(file_notin1_in2)
        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)

        synchronizer: SyncManager = SyncManager(fstruct_list, FSInterface)
        synchronizer.sync()

        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)
        files_in1, files_in2 = self.get_file_lists_without_prefixes(fstruct_list)
        self.assertCountEqual(files_in1, files_in2)
        self.assertCountEqual(files_in1, [test_filename])
        self.assertCountEqual(files_in2, [test_filename])

    @tfuncs.handle_test_dirs
    def test_file_notin1_in2_notupdated1(self) -> None:
        file_notin1_in2: str = str(self.tf.test_path2 / "test_file.txt")
        tfuncs.create_file(file_notin1_in2)

        fstruct_list: List[FileStructure] = self.initialize_test_directories()
        last_sync_dict: Dict[str, Any] = fstruct_list[1].files_to_json()
        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)

        synchronizer: SyncManager = SyncManager(fstruct_list, FSInterface)
        synchronizer.sync()

        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)
        files_in1, files_in2 = self.get_file_lists_without_prefixes(fstruct_list)
        self.assertCountEqual(files_in1, files_in2)
        self.assertCountEqual(files_in1, [])
        self.assertCountEqual(files_in2, [])

    @tfuncs.handle_test_dirs
    def test_file_in1_in2_updated1_notupdated2(self) -> None:
        common_file_name: str = "test_file.txt"
        file_in1: str = str(self.tf.test_path1 / common_file_name)
        tfuncs.create_file(file_in1)
        file_in2: str = str(self.tf.test_path2 / common_file_name)
        tfuncs.create_file(file_in2)

        fstruct_list: List[FileStructure] = self.initialize_test_directories()
        last_sync_dict: Dict[str, Any] = fstruct_list[1].files_to_json()

        time.sleep(self.delay_sec)
        with open(file_in1, 'w') as file_to_update:
            file_to_update.write('This file is updated.')

        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)

        synchronizer: SyncManager = SyncManager(fstruct_list, FSInterface)
        synchronizer.sync()

        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)
        files_in1, files_in2 = self.get_file_lists_without_prefixes(fstruct_list)
        self.assertCountEqual(files_in1, files_in2)

        with open(file_in1) as same_as_before_file:
            message: str = same_as_before_file.read()
            self.assertEqual(message, 'This file is updated.')
        with open(file_in2) as updated_file:
            message = updated_file.read()
            self.assertEqual(message, 'This file is updated.')

    @tfuncs.handle_test_dirs
    def test_file_in1_in2_notupdated1_updated2(self) -> None:
        common_file_name: str = "test_file.txt"
        file_in1: str = str(self.tf.test_path1 / common_file_name)
        tfuncs.create_file(file_in1)
        file_in2: str = str(self.tf.test_path2 / common_file_name)
        tfuncs.create_file(file_in2)

        fstruct_list: List[FileStructure] = self.initialize_test_directories()
        last_sync_dict: Dict[str, Any] = fstruct_list[1].files_to_json()

        time.sleep(self.delay_sec)
        with open(file_in2, 'w') as file_to_update:
            file_to_update.write('This file is updated.')

        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)

        synchronizer: SyncManager = SyncManager(fstruct_list, FSInterface)
        synchronizer.sync()

        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)
        files_in1, files_in2 = self.get_file_lists_without_prefixes(fstruct_list)
        self.assertCountEqual(files_in1, files_in2)

        with open(file_in2) as same_as_before_file:
            message: str = same_as_before_file.read()
            self.assertEqual(message, 'This file is updated.')
        with open(file_in1) as updated_file:
            message = updated_file.read()
            self.assertEqual(message, 'This file is updated.')

    @tfuncs.handle_test_dirs
    def test_file_in1_in2_updated1_updated2(self) -> None:
        common_file_name: str = "test_file.txt"
        file_in1: str = str(self.tf.test_path1 / common_file_name)
        tfuncs.create_file(file_in1)
        file_in2: str = str(self.tf.test_path2 / common_file_name)
        tfuncs.create_file(file_in2)

        fstruct_list: List[FileStructure] = self.initialize_test_directories()
        last_sync_dict: Dict[str, Any] = fstruct_list[1].files_to_json()

        time.sleep(self.delay_sec)
        with open(file_in1, 'w') as file_to_update:
            file_to_update.write('This file is updated.')
        with open(file_in2, 'w') as file_to_update:
            file_to_update.write('This file is also updated.')

        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)

        synchronizer: SyncManager = SyncManager(fstruct_list, FSInterface)
        synchronizer.sync()

        # Check each directory contains correct file names with timestamps
        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)
        files_in1, files_in2 = self.get_file_lists_without_prefixes(fstruct_list)
        self.assertCountEqual(files_in1, files_in2)
        self.assertEqual(len(files_in1), 2)
        self.assertEqual(len(files_in2), 2)
        # print(f"files_in1: {files_in1}")
        # print(f"files_in2: {files_in2}")

        # Check contents of files in one directory match contents of same files in other directory
        file_contents: Dict[str, str] = {}
        for file in self.tf.test_path1.iterdir():
            with file.open() as read_file:
                first_file: str = tfuncs.remove_prefix(str(file), str(self.tf.test_path1))
                file_contents[first_file] = read_file.read()
        for file in self.tf.test_path2.iterdir():
            with file.open() as read_file:
                second_file: str = tfuncs.remove_prefix(str(file), str(self.tf.test_path2))
                assert file_contents[second_file] == read_file.read()

    @tfuncs.handle_test_dirs
    def test_file_in1_in2_notupdated1_notupdated2(self) -> None:
        common_file_name: str = "test_file.txt"
        file_in1: str = str(self.tf.test_path1 / common_file_name)
        tfuncs.create_file(file_in1)
        file_in2: str = str(self.tf.test_path2 / common_file_name)
        tfuncs.create_file(file_in2)

        fstruct_list: List[FileStructure] = self.initialize_test_directories()
        last_sync_dict: Dict[str, Any] = fstruct_list[1].files_to_json()

        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)

        synchronizer: SyncManager = SyncManager(fstruct_list, FSInterface)
        synchronizer.sync()

        # Check each directory contains correct file names with timestamps
        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)
        files_in1, files_in2 = self.get_file_lists_without_prefixes(fstruct_list)
        self.assertCountEqual(files_in1, files_in2)
        self.assertEqual(len(files_in1), 1)
        self.assertEqual(len(files_in2), 1)

    @tfuncs.handle_test_dirs
    def test_get_last_sync(self) -> None:
        common_file_name: str = "test_file.txt"
        file_in1: str = str(self.tf.test_path1 / common_file_name)
        tfuncs.create_file(file_in1)
        file_in2: str = str(self.tf.test_path2 / common_file_name)
        tfuncs.create_file(file_in2)

        fstruct_list: List[FileStructure] = self.initialize_test_directories()
        last_sync_dict: Dict[str, Any] = fstruct_list[1].files_to_json()

        time.sleep(self.delay_sec)
        with open(file_in1, 'w') as file_to_update:
            file_to_update.write('This file is updated.')

        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)

        synchronizer: SyncManager = SyncManager(fstruct_list, FSInterface)
        synchronizer.sync()

        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)
        files_in1, files_in2 = self.get_file_lists_without_prefixes(fstruct_list)
        self.assertCountEqual(files_in1, files_in2)

        with open(file_in2) as same_as_before_file:
            message: str = same_as_before_file.read()
            self.assertEqual(message, 'This file is updated.')
        with open(file_in1) as updated_file:
            message = updated_file.read()
            self.assertEqual(message, 'This file is updated.')

        self.assertLessEqual(fstruct_list[0].files_to_json()[files_in1[0]],
                             synchronizer.get_last_sync()[files_in1[0]])
        self.assertLessEqual(fstruct_list[1].files_to_json()[files_in2[0]],
                             synchronizer.get_last_sync()[files_in2[0]])

    @tfuncs.handle_test_dirs
    def test_folder_in1_notin2_updated1(self) -> None:
        fstruct_list: List[FileStructure] = self.initialize_test_directories()
        last_sync_dict: Dict[str, Any] = fstruct_list[0].files_to_json()

        test_folder: str = "test_folder"
        folder_in1_notin2: str = str(self.tf.test_path1 / test_folder)
        tfuncs.create_directory(folder_in1_notin2)
        test_filename: str = "test_file.txt"
        file_in1_notin2: str = str(Path(folder_in1_notin2) / test_filename)
        tfuncs.create_file(file_in1_notin2)
        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)

        synchronizer: SyncManager = SyncManager(fstruct_list, FSInterface)
        synchronizer.sync()

        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)
        files_in1, files_in2 = self.get_file_lists_without_prefixes(fstruct_list)
        self.assertCountEqual(files_in1, files_in2)
        test_paths: List[str] = tfuncs.remove_prefixes([folder_in1_notin2, file_in1_notin2],
                                                       fstruct_list[0].get_directory_path())
        self.assertCountEqual(files_in1, test_paths)
        self.assertCountEqual(files_in2, test_paths)

    @tfuncs.handle_test_dirs
    def test_folder_in1_notin2_notupdated1(self) -> None:
        test_folder: str = "test_folder"
        folder_in1_notin2: str = str(self.tf.test_path1 / test_folder)
        tfuncs.create_directory(folder_in1_notin2)
        test_filename: str = "test_file.txt"
        file_in1_notin2: str = str(Path(folder_in1_notin2) / test_filename)
        tfuncs.create_file(file_in1_notin2)

        fstruct_list: List[FileStructure] = self.initialize_test_directories()
        last_sync_dict: Dict[str, Any] = fstruct_list[0].files_to_json()

        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)

        synchronizer: SyncManager = SyncManager(fstruct_list, FSInterface)
        synchronizer.sync()

        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)
        files_in1, files_in2 = self.get_file_lists_without_prefixes(fstruct_list)
        self.assertCountEqual(files_in1, files_in2)
        self.assertCountEqual(files_in1, [])
        self.assertCountEqual(files_in2, [])

    @tfuncs.handle_test_dirs
    def test_folder_notin1_in2_updated2(self) -> None:
        fstruct_list: List[FileStructure] = self.initialize_test_directories()
        last_sync_dict: Dict[str, Any] = fstruct_list[0].files_to_json()

        test_folder: str = "test_folder"
        folder_notin1_in2: str = str(self.tf.test_path2 / test_folder)
        tfuncs.create_directory(folder_notin1_in2)
        test_filename: str = "test_file.txt"
        file_notin1_in2: str = str(Path(folder_notin1_in2) / test_filename)
        tfuncs.create_file(file_notin1_in2)
        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)

        synchronizer: SyncManager = SyncManager(fstruct_list, FSInterface)
        synchronizer.sync()

        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)
        files_in1, files_in2 = self.get_file_lists_without_prefixes(fstruct_list)
        self.assertCountEqual(files_in1, files_in2)
        test_paths: List[str] = tfuncs.remove_prefixes([folder_notin1_in2, file_notin1_in2],
                                                       fstruct_list[1].get_directory_path())
        self.assertCountEqual(files_in1, test_paths)
        self.assertCountEqual(files_in2, test_paths)

    @tfuncs.handle_test_dirs
    def test_folder_notin1_in2_notupdated2(self) -> None:
        test_folder: str = "test_folder"
        folder_notin1_in2: str = str(self.tf.test_path2 / test_folder)
        tfuncs.create_directory(folder_notin1_in2)
        test_filename: str = "test_file.txt"
        file_notin1_in2: str = str(Path(folder_notin1_in2) / test_filename)
        tfuncs.create_file(file_notin1_in2)

        fstruct_list: List[FileStructure] = self.initialize_test_directories()
        last_sync_dict: Dict[str, Any] = fstruct_list[1].files_to_json()

        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)

        synchronizer: SyncManager = SyncManager(fstruct_list, FSInterface)
        synchronizer.sync()

        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)
        files_in1, files_in2 = self.get_file_lists_without_prefixes(fstruct_list)
        self.assertCountEqual(files_in1, files_in2)
        self.assertCountEqual(files_in1, [])
        self.assertCountEqual(files_in2, [])

    @tfuncs.handle_test_dirs
    def test_folder_in1_in2_notupdated1_notupdated2(self) -> None:
        common_folder_name: str = "test_folder"
        folder_in1: str = str(self.tf.test_path1 / common_folder_name)
        tfuncs.create_directory(folder_in1)
        folder_in2: str = str(self.tf.test_path2 / common_folder_name)
        tfuncs.create_directory(folder_in2)

        fstruct_list: List[FileStructure] = self.initialize_test_directories()
        last_sync_dict: Dict[str, Any] = fstruct_list[1].files_to_json()

        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)

        synchronizer: SyncManager = SyncManager(fstruct_list, FSInterface)
        synchronizer.sync()

        # Check each directory contains correct file names with timestamps
        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)
        files_in1, files_in2 = self.get_file_lists_without_prefixes(fstruct_list)
        self.assertCountEqual(files_in1, files_in2)
        self.assertCountEqual(files_in1, [common_folder_name])
        self.assertCountEqual(files_in2, [common_folder_name])

    @tfuncs.handle_test_dirs
    def test_folder_in1_in2_name_change1(self) -> None:
        common_folder_name: str = "test_folder"
        common_file_name: str = "test_file.txt"
        folder_in1: str = str(self.tf.test_path1 / common_folder_name)
        tfuncs.create_directory(folder_in1)
        file_in1: str = str(Path(folder_in1) / common_file_name)
        tfuncs.create_file(file_in1)
        folder_in2: str = str(self.tf.test_path2 / common_folder_name)
        tfuncs.create_directory(folder_in2)
        file_in2: str = str(Path(folder_in2) / common_file_name)
        tfuncs.create_file(file_in2)

        fstruct_list: List[FileStructure] = self.initialize_test_directories()
        last_sync_dict: Dict[str, Any] = fstruct_list[1].files_to_json()

        time.sleep(self.delay_sec)
        new_folder: str = str(Path(folder_in1).parent / "new_folder")
        Path(folder_in1).rename(new_folder)
        new_file: str = str(Path(new_folder) / common_file_name)

        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)

        synchronizer: SyncManager = SyncManager(fstruct_list, FSInterface)
        synchronizer.sync()

        self.check_fstructs_for_updates(fstruct_list, last_sync_dict)
        files_in1, files_in2 = self.get_file_lists_without_prefixes(fstruct_list)
        new_folder_np, new_file_np = tfuncs.remove_prefixes([new_folder, new_file], str(self.tf.test_path1))
        self.assertCountEqual(files_in1, files_in2)
        self.assertCountEqual(files_in1, [new_folder_np, new_file_np])
        self.assertCountEqual(files_in2, [new_folder_np, new_file_np])


if __name__ == "__main__":
    unittest.main()
