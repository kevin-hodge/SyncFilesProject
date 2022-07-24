"""Tests sync_states

Author: Kevin Hodge
"""

import unittest
from typing import List
from syncfiles.config_manager import ConfigManager
from syncfiles.sync_state_machine import SyncState
from syncfiles.sync_states import Initial, Wait, Check, Sync, Error, Final, StateData
from tests.mock_ui import MockUI
from tests import tfuncs


class SyncStateTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs) -> None:
        self.tf: tfuncs.TFunctions = tfuncs.TFunctions()
        self.state_data: StateData = StateData(ConfigManager(), MockUI())
        self.states: List[SyncState] = [
            Initial(self.state_data),
            Wait(self.state_data),
            Check(self.state_data),
            Sync(self.state_data),
            Error(self.state_data),
            Final(self.state_data)
        ]
        super().__init__(*args, **kwargs)

    def test_states_init(self) -> None:
        for state in self.states:
            assert isinstance(state, SyncState)

    def test_get_next(self) -> None:
        for state in self.states:
            assert isinstance(state.get_next(), SyncState)

    def test_initial(self) -> None:
        config: ConfigManager = ConfigManager()
        mock_ui: MockUI = MockUI()
        state_data: StateData = StateData(config, mock_ui)
        initial: Initial = Initial(state_data)
        assert isinstance(initial, Initial)
        initial.run()
