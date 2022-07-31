"""Tests sync_states

Author: Kevin Hodge
"""

import unittest
import unittest.mock
from typing import List, Dict, Any
from pathlib import Path
from syncfiles.config_manager import ConfigManager
from syncfiles.sync_state_machine import SyncState
from syncfiles.file_structure import FileStructure
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

        state_data: StateData = StateData(ConfigManager(), MockUI())
        test_state: TestState = TestState(state_data)
        test_state.run()
        self.assertTrue(test_state.get_error_raised())
        self.assertEqual(str(test_state.error), "Test")

    @tfuncs.handle_dir_tempfile
    @tfuncs.handle_test_dirs
    def test_initial_run_no_sync_dir(self) -> None:
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
    def test_initial_run_nonexistant_user_input(self) -> None:
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
    def test_initial_run_existing_sync_dir(self) -> None:
        input: List[str] = [str(self.tf.test_path1), str(self.tf.test_path2)]
        tfuncs.write_json(input, str(self.tf.sync_dir_file))
        state_data: StateData = StateData(ConfigManager(), MockUI(), verbose=True)
        initial: Initial = Initial(state_data)
        with unittest.mock.patch('builtins.print', self.add_to_test_string):
            initial.run()
        self.assertCountEqual(initial.get_sync_directories(), input)
        for fstruct in initial.get_fstructs():
            self.assertCountEqual(fstruct.files_to_list(), [])
        self.assertCountEqual(self.get_and_clear_test_string(), ["Directories to sync:", input[0], input[1]])

    @tfuncs.handle_dir_tempfile
    @tfuncs.handle_test_dirs
    def test_initial_get_next_error_raised(self) -> None:
        state_data: StateData = StateData(ConfigManager(), MockUI(), verbose=True)
        initial: Initial = Initial(state_data)
        initial.set_error_raised()
        self.assertTrue(isinstance(initial.get_next(), Error))

    @tfuncs.handle_dir_tempfile
    @tfuncs.handle_test_dirs
    def test_initial_get_next_exit_request(self) -> None:
        state_data: StateData = StateData(ConfigManager(), MockUI(), verbose=True)
        initial: Initial = Initial(state_data)
        initial.set_exit_request()
        self.assertTrue(isinstance(initial.get_next(), Final))

    @tfuncs.handle_dir_tempfile
    @tfuncs.handle_test_dirs
    def test_initial_get_next_no_error_raised(self) -> None:
        state_data: StateData = StateData(ConfigManager(), MockUI(), verbose=True)
        initial: Initial = Initial(state_data)
        self.assertTrue(isinstance(initial.get_next(), Check))

    @tfuncs.handle_dir_tempfile
    @tfuncs.handle_test_dirs
    @tfuncs.handle_last_tempfile
    def test_check_run_fstruct_updated(self) -> None:
        config: ConfigManager = ConfigManager()
        test_dir1: str = str(self.tf.test_path1.name)
        test_dir2: str = str(self.tf.test_path2.name)
        fstruct1: FileStructure = FileStructure(str(self.tf.test_path1), verbose=True)
        fstruct2: FileStructure = FileStructure(str(self.tf.test_path2), verbose=True)
        last_sync_files: Dict[str, Any] = fstruct1.files_to_json()
        config.write_last_sync_file(last_sync_files)

        test_file_name: str = "test_file1.txt"
        test_file: str = str(Path(test_dir1) / test_file_name)
        tfuncs.create_file(test_file)

        state_data: StateData = StateData(config, MockUI(), verbose=True)
        check: Check = Check(state_data)
        check.add_fstruct(fstruct1)
        check.add_fstruct(fstruct2)
        with unittest.mock.patch('builtins.print', self.add_to_test_string):
            check.run()
        self.assertTrue(check.get_sync_required())
        validation_strings: List[str] = [
            "Directory 1:",
            test_dir1 + "\n   " + str(fstruct1.files),
            "Directory 2:",
            test_dir2 + "\n" + str(fstruct2.files)
        ]
        self.assertCountEqual(self.get_and_clear_test_string(), validation_strings)

    @tfuncs.handle_dir_tempfile
    @tfuncs.handle_test_dirs
    @tfuncs.handle_last_tempfile
    def test_check_run_fstruct_not_updated(self) -> None:
        config: ConfigManager = ConfigManager()
        test_dir1: str = str(self.tf.test_path1.name)
        test_dir2: str = str(self.tf.test_path2.name)
        test_file_name: str = "test_file1.txt"
        test_file: str = str(Path(test_dir1) / test_file_name)
        tfuncs.create_file(test_file)
        fstruct1: FileStructure = FileStructure(str(self.tf.test_path1), verbose=True)
        fstruct2: FileStructure = FileStructure(str(self.tf.test_path2), verbose=True)
        last_sync_files: Dict[str, Any] = fstruct1.files_to_json()
        config.write_last_sync_file(last_sync_files)

        state_data: StateData = StateData(config, MockUI(), verbose=True)
        check: Check = Check(state_data)
        check.add_fstruct(fstruct1)
        check.add_fstruct(fstruct2)
        with unittest.mock.patch('builtins.print', self.add_to_test_string):
            check.run()
        self.assertFalse(check.get_sync_required())
        validation_strings: List[str] = [
            "Directory 1:",
            test_dir1 + "\n   " + str(fstruct1.files),
            "Directory 2:",
            test_dir2 + "\n" + str(fstruct2.files)
        ]
        self.assertCountEqual(self.get_and_clear_test_string(), validation_strings)

    @tfuncs.handle_dir_tempfile
    @tfuncs.handle_test_dirs
    def test_check_get_next_error_raised(self) -> None:
        state_data: StateData = StateData(ConfigManager(), MockUI(), verbose=True)
        check: Check = Check(state_data)
        check.set_error_raised()
        self.assertTrue(isinstance(check.get_next(), Error))

    @tfuncs.handle_dir_tempfile
    @tfuncs.handle_test_dirs
    def test_check_get_next_exit_request(self) -> None:
        state_data: StateData = StateData(ConfigManager(), MockUI(), verbose=True)
        check: Check = Check(state_data)
        check.set_exit_request()
        self.assertTrue(isinstance(check.get_next(), Final))

    @tfuncs.handle_dir_tempfile
    @tfuncs.handle_test_dirs
    def test_check_get_next_not_updated(self) -> None:
        state_data: StateData = StateData(ConfigManager(), MockUI(), verbose=True)
        check: Check = Check(state_data)
        check.set_sync_required()
        self.assertTrue(isinstance(check.get_next(), Sync))
