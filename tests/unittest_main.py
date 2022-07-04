"""Runs all test files.

Author: Kevin Hodge
"""

import unittest
from tests.test_config_manager import ConfigManagerTestCase
from tests.test_file_structure import FileStructureTestCase
from tests.test_sync_manager import SyncManagerTestCase


ConfigManagerTestCase()
FileStructureTestCase()
SyncManagerTestCase()


if __name__ == "__main__":
    unittest.main()
