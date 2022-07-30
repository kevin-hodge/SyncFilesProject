"""Tests sync_states

Author: Kevin Hodge
"""

import unittest
import unittest.mock
from typing import List
from syncfiles.config_manager import ConfigManager
from syncfiles.sync_state_machine import SyncState
from syncfiles.sync_states import DataState, Initial, Wait, Check, Sync, Error, Final, StateData
from tests.mock_ui import MockUI
from tests import tfuncs


class SyncStateTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs) -> None:
        self.tf: tfuncs.TFunctions = tfuncs.TFunctions()
        state_data: StateData = StateData(ConfigManager(), MockUI())
        self.states: List[SyncState] = [
            Initial(state_data),
            Wait(state_data),
            Check(state_data),
            Sync(state_data),
            Error(state_data),
            Final(state_data)
        ]
        self.test_string_output: List[str] = []
        super().__init__(*args, **kwargs)

    def get_and_clear_test_string(self) -> List[str]:
        temp: List[str] = self.test_string_output[:]
        self.test_string_output = []
        return temp

    def add_to_test_string(self, string: str) -> None:
        self.test_string_output.append(string)

    def test_states_init(self) -> None:
        for state in self.states:
            assert isinstance(state, SyncState)

    def test_get_next(self) -> None:
        for state in self.states:
            assert isinstance(state.get_next(), SyncState)

    def test_error_handling(self) -> None:
        class TestState(DataState):
            def run_commands(self) -> None:
                raise ValueError("Test")

            def get_next(self) -> SyncState:
                pass

        config: ConfigManager = ConfigManager()
        mock_ui: MockUI = MockUI()
        state_data: StateData = StateData(config, mock_ui)
        test_state: TestState = TestState(state_data)
        test_state.run()
        self.assertTrue(test_state.get_error_raised())
        self.assertEqual(str(test_state.error), "Test")

    @tfuncs.handle_dir_tempfile
    @tfuncs.handle_test_dirs
    def test_initial_no_sync_dir(self) -> None:
        input: List[str] = [str(self.tf.test_path1), str(self.tf.test_path2)]
        config: ConfigManager = ConfigManager()
        mock_ui: MockUI = MockUI()
        for entry_path in input:
            mock_ui.add_directory(entry_path)
        state_data: StateData = StateData(config, mock_ui, verbose=True)
        initial: Initial = Initial(state_data)
        with unittest.mock.patch('builtins.print', self.add_to_test_string):
            initial.run()
        self.assertCountEqual(initial.get_sync_directories(), input)
        for fstruct in initial.get_fstructs():
            self.assertCountEqual(fstruct.files_to_list(), [])
        self.assertCountEqual(self.get_and_clear_test_string(), ["Directories to sync:", input[0], input[1]])

    @tfuncs.handle_dir_tempfile
    @tfuncs.handle_test_dirs
    def test_initial_nonexistant_user_input(self) -> None:
        input: List[str] = [str(self.tf.test_path1 / "nonexistant"), str(self.tf.test_path1), str(self.tf.test_path2)]
        config: ConfigManager = ConfigManager()
        mock_ui: MockUI = MockUI()
        for entry_path in input:
            mock_ui.add_directory(entry_path)
        state_data: StateData = StateData(config, mock_ui, verbose=True)
        initial: Initial = Initial(state_data)
        with unittest.mock.patch('builtins.print', self.add_to_test_string):
            initial.run()
        self.assertCountEqual(initial.get_sync_directories(), input[1:])
        for fstruct in initial.get_fstructs():
            self.assertCountEqual(fstruct.files_to_list(), [])
        self.assertCountEqual(self.get_and_clear_test_string(), ["Directories to sync:", input[1], input[2]])

    @tfuncs.handle_dir_tempfile
    @tfuncs.handle_test_dirs
    def test_initial_existing_sync_dir(self) -> None:
        input: List[str] = [str(self.tf.test_path1), str(self.tf.test_path2)]
        tfuncs.write_json(input, str(self.tf.sync_dir_file))
        config: ConfigManager = ConfigManager()
        mock_ui: MockUI = MockUI()
        state_data: StateData = StateData(config, mock_ui, verbose=True)
        initial: Initial = Initial(state_data)
        with unittest.mock.patch('builtins.print', self.add_to_test_string):
            initial.run()
        self.assertCountEqual(initial.get_sync_directories(), input)
        for fstruct in initial.get_fstructs():
            self.assertCountEqual(fstruct.files_to_list(), [])
        self.assertCountEqual(self.get_and_clear_test_string(), ["Directories to sync:", input[0], input[1]])

    @tfuncs.handle_dir_tempfile
    @tfuncs.handle_test_dirs
    def test_initial_error_raised(self) -> None:
        config: ConfigManager = ConfigManager()
        mock_ui: MockUI = MockUI()
        state_data: StateData = StateData(config, mock_ui)
        initial: Initial = Initial(state_data)
        initial.set_error_raised()
        self.assertTrue(isinstance(initial.get_next(), Error))

    @tfuncs.handle_dir_tempfile
    @tfuncs.handle_test_dirs
    def test_initial_exit_request(self) -> None:
        config: ConfigManager = ConfigManager()
        mock_ui: MockUI = MockUI()
        state_data: StateData = StateData(config, mock_ui)
        initial: Initial = Initial(state_data)
        initial.set_exit_request()
        self.assertTrue(isinstance(initial.get_next(), Final))

    @tfuncs.handle_dir_tempfile
    @tfuncs.handle_test_dirs
    def test_initial_no_error_raised(self) -> None:
        config: ConfigManager = ConfigManager()
        mock_ui: MockUI = MockUI()
        state_data: StateData = StateData(config, mock_ui)
        initial: Initial = Initial(state_data)
        self.assertTrue(isinstance(initial.get_next(), Check))
