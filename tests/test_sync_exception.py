"""Tests sync_exception

Author: Kevin Hodge
"""

import unittest
from syncfiles.sync_exception import SyncException


class SyncExceptionTestCase(unittest.TestCase):
    def test_empty_init(self) -> None:
        empty_sync_exception: SyncException = SyncException()
        validation_string: str = "Error in Unknown State, Error ID: Unknown Error" + "\n" + "Error Message: " + "None"
        self.assertEqual(empty_sync_exception.get_error_message(), validation_string)

    def test_get_error_message(self) -> None:
        error: Exception = ValueError("get_relative_path argument 'path' is not contained in dir_path_list")
        prev_state: str = "Sync"
        error_id: str = "get_sync_dirs"
        sync_exception: SyncException = SyncException(str(error), prev_state, error_id)
        validation_string: str = "Error in Sync, Error ID: get_sync_dirs" + "\n" + "Error Message: " + str(error)
        self.assertEqual(sync_exception.get_error_message(), validation_string)
