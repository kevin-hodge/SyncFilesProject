"""Tests sync_states

Author: Kevin Hodge
"""

import unittest
from syncfiles.sync_states import Initial, Wait


class SyncStateTestCase(unittest.TestCase):
    def test_states_init(self) -> None:
        Initial()
