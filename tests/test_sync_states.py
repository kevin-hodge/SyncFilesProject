"""Tests sync_states.py

Author: Kevin Hodge
"""

import unittest
from syncfiles.sync_states import State, Initial


class SyncStatesTestCase(unittest.TestCase):
    def test_intial_valid(self) -> None:
        state: Initial = Initial()
        assert isinstance(state, State)
