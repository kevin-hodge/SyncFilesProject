"""Runs all test files.

Author: Kevin Hodge
"""

import unittest
from tests.test_config_manager import ConfigManagerTestCase
from tests.test_file_structure import FileStructureTestCase
from tests.test_sync_exception import SyncExceptionTestCase
from tests.test_sync_manager import SyncManagerTestCase
from tests.test_sync_state_machine import SyncStateMachineTestCase
from tests.test_sync_states import SyncStateTestCase
from tests.test_wx_gui import WxGUITestCase


ConfigManagerTestCase()
FileStructureTestCase()
SyncExceptionTestCase()
SyncManagerTestCase()
SyncStateMachineTestCase()
SyncStateTestCase()
WxGUITestCase()


if __name__ == "__main__":
    unittest.main()
