"""Runs all test files.

Author: Kevin Hodge
"""

import unittest
from tests.test_config_manager import ConfigManagerTestCase
from tests.test_file_structure import FileStructureTestCase
from tests.test_sync_manager import SyncManagerTestCase
from tests.test_sync_states import SyncStateTestCase
from tests.test_sync_state_machine import SyncStateMachineTestCase


ConfigManagerTestCase()
FileStructureTestCase()
SyncManagerTestCase()
SyncStateTestCase()
SyncStateMachineTestCase()


if __name__ == "__main__":
    unittest.main()
