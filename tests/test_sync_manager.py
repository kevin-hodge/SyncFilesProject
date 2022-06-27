"""Sync Files Project: sync_manager Test

Author: Kevin Hodge
"""

import unittest
from typing import List
import tests.tfuncs as tfuncs
from tests.tfuncs import TFunctions
from syncfiles.sync_manager import SyncManager
from syncfiles.file_structure import FileStructure


class SyncManagerTestCase(unittest.TestCase):
    """Test case for ConfigManager"""
    def __init__(self, *args, **kwargs) -> None:
        self.tf: TFunctions = TFunctions()
        super().__init__(*args, **kwargs)

    @tfuncs.handle_test_dirs
    def test_no_updates(self):
        test_dir1: str = str(self.tf.test_path1)
        self.tf.create_rand_fstruct(test_dir1)
        test_fstruct1: FileStructure = FileStructure(test_dir1)

        test_dir2: str = str(self.tf.test_path2)
        test_fstruct2: FileStructure = FileStructure(test_dir2)

        fstruct_list: List[FileStructure] = [test_fstruct1, test_fstruct2]
        SyncManager(fstruct_list)

    @tfuncs.handle_test_dirs
    def test_new_file(self):
        # test_dir1: str = str(self.tf.test_path1)
        # test_dir2: str = str(self.tf.test_path2)
        pass


if __name__ == "__main__":
    unittest.main()
