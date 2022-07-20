"""Tests sync_states

Author: Kevin Hodge
"""

import unittest
from syncfiles.sync_states import Initial, Wait


class SyncStateTestCase(unittest.TestCase):
    def test_states_init(self) -> None:
        state: Initial = Initial()
        state.set_next(Wait())
        print(state.get_next())
        state = state.get_next()
        state.set_next(Initial())
        state = state.get_next()
        print(state.get_next())
