"""Tests sync_states

Author: Kevin Hodge
"""

import unittest
import unittest.mock
from typing import List, Dict, Any
from pathlib import Path
from syncfiles.config_manager import ConfigManager
from syncfiles.sync_state_machine import SyncState, End
from syncfiles.file_system_interface import FSInterface
from syncfiles.file_structure import FileStructure
from syncfiles.sync_exception import SyncException
from syncfiles.sync_states import DataState, Initial, Wait, Check, Sync, Error, Final, StateData
from tests.mock_ui import MockUI
from tests import tfuncs


class SyncStateTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs) -> None:
        self.tf: tfuncs.TFunctions = tfuncs.TFunctions()
        state_data: StateData = StateData(ConfigManager(FSInterface), MockUI(), FSInterface)
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

    def add_to_test_string(self, string: str, end: str = "") -> None:
        self.test_string_output.append(string + end)

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

        state_data: StateData = StateData(ConfigManager(FSInterface), MockUI(), FSInterface)
        test_state: TestState = TestState(state_data)
        test_state.run()
        self.assertTrue(test_state.get_error_raised())
        validation_string: str = "Error in Unknown State, Error ID: Unknown Error\n" + "Error Message: Test"
        error_state: Error = Error(state_data)
        assert error_state.error is not None
        self.assertEqual(error_state.error.get_error_message(), validation_string)

    @tfuncs.handle_dir_tempfile
    @tfuncs.handle_test_dirs
    def test_initial_run_no_sync_dir(self) -> None:
        input: List[str] = [str(self.tf.test_path1), str(self.tf.test_path2)]
        config: ConfigManager = ConfigManager(FSInterface)
        mock_ui: MockUI = MockUI()
        for entry_path in input:
            mock_ui.add_directory(entry_path)
        state_data: StateData = StateData(config, mock_ui, FSInterface, verbose=True)
        initial: Initial = Initial(state_data)
        with unittest.mock.patch('builtins.print', self.add_to_test_string):
            initial.run()
        self.assertCountEqual(initial.get_sync_directories(), input)
        for fstruct in initial.get_fstructs():
            self.assertCountEqual(fstruct.files_to_list(), [])
        self.assertCountEqual(self.get_and_clear_test_string(),
                              ["Initializing...", "Directories to sync:", input[0], input[1]])

    @tfuncs.handle_dir_tempfile
    @tfuncs.handle_test_dirs
    def test_initial_run_nonexistant_user_input(self) -> None:
        input: List[str] = [str(self.tf.test_path1 / "nonexistant"), str(self.tf.test_path1), str(self.tf.test_path2)]
        config: ConfigManager = ConfigManager(FSInterface)
        mock_ui: MockUI = MockUI()
        for entry_path in input:
            mock_ui.add_directory(entry_path)
        state_data: StateData = StateData(config, mock_ui, FSInterface, verbose=True)
        initial: Initial = Initial(state_data)
        with unittest.mock.patch('builtins.print', self.add_to_test_string):
            initial.run()
        self.assertCountEqual(initial.get_sync_directories(), input[1:])
        for fstruct in initial.get_fstructs():
            self.assertCountEqual(fstruct.files_to_list(), [])
        self.assertCountEqual(self.get_and_clear_test_string(),
                              ["Initializing...", "Directories to sync:", input[1], input[2]])

    @tfuncs.handle_dir_tempfile
    @tfuncs.handle_test_dirs
    def test_initial_run_existing_sync_dir(self) -> None:
        input: List[str] = [str(self.tf.test_path1), str(self.tf.test_path2)]
        tfuncs.write_json(input, str(self.tf.sync_dir_file))
        state_data: StateData = StateData(ConfigManager(FSInterface), MockUI(), FSInterface, verbose=True)
        initial: Initial = Initial(state_data)
        with unittest.mock.patch('builtins.print', self.add_to_test_string):
            initial.run()
        self.assertCountEqual(initial.get_sync_directories(), input)
        for fstruct in initial.get_fstructs():
            self.assertCountEqual(fstruct.files_to_list(), [])
        self.assertCountEqual(self.get_and_clear_test_string(),
                              ["Initializing...", "Directories to sync:", input[0], input[1]])

    def test_initial_get_next_error_raised(self) -> None:
        state_data: StateData = StateData(ConfigManager(FSInterface), MockUI(), FSInterface)
        initial: Initial = Initial(state_data)
        initial.set_error_raised()
        self.assertTrue(isinstance(initial.get_next(), Error))

    def test_initial_get_next_exit_request(self) -> None:
        state_data: StateData = StateData(ConfigManager(FSInterface), MockUI(), FSInterface)
        initial: Initial = Initial(state_data)
        initial.set_exit_request()
        self.assertTrue(isinstance(initial.get_next(), Final))

    def test_initial_get_next_no_error_raised(self) -> None:
        state_data: StateData = StateData(ConfigManager(FSInterface), MockUI(), FSInterface)
        initial: Initial = Initial(state_data)
        self.assertTrue(isinstance(initial.get_next(), Check))

    @tfuncs.handle_dir_tempfile
    @tfuncs.handle_test_dirs
    @tfuncs.handle_last_tempfile
    def test_check_run_fstruct_updated(self) -> None:
        config: ConfigManager = ConfigManager(FSInterface)
        test_dir1: str = str(self.tf.test_path1.name)
        test_dir2: str = str(self.tf.test_path2.name)
        fstruct1: FileStructure = FileStructure(str(self.tf.test_path1), FSInterface, verbose=True)
        fstruct2: FileStructure = FileStructure(str(self.tf.test_path2), FSInterface, verbose=True)
        last_sync_files: Dict[str, Any] = fstruct1.files_to_json()
        config.write_last_sync_file(last_sync_files)

        test_file_name: str = "test_file1.txt"
        test_file: str = str(Path(test_dir1) / test_file_name)
        tfuncs.create_file(test_file)

        state_data: StateData = StateData(config, MockUI(), FSInterface, verbose=True)
        check: Check = Check(state_data)
        check.add_fstruct(fstruct1)
        check.add_fstruct(fstruct2)
        with unittest.mock.patch('builtins.print', self.add_to_test_string):
            check.run()
        self.assertTrue(check.get_sync_required())
        validation_strings: List[str] = [
            "Checking...",
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
        config: ConfigManager = ConfigManager(FSInterface)
        test_dir1: str = str(self.tf.test_path1.name)
        test_dir2: str = str(self.tf.test_path2.name)
        test_file_name: str = "test_file1.txt"
        test_file: str = str(Path(test_dir1) / test_file_name)
        tfuncs.create_file(test_file)
        fstruct1: FileStructure = FileStructure(str(self.tf.test_path1), FSInterface, verbose=True)
        fstruct2: FileStructure = FileStructure(str(self.tf.test_path2), FSInterface, verbose=True)
        last_sync_files: Dict[str, Any] = fstruct1.files_to_json()
        config.write_last_sync_file(last_sync_files)

        state_data: StateData = StateData(config, MockUI(), FSInterface, verbose=True)
        check: Check = Check(state_data)
        check.add_fstruct(fstruct1)
        check.add_fstruct(fstruct2)
        with unittest.mock.patch('builtins.print', self.add_to_test_string):
            check.run()
        self.assertFalse(check.get_sync_required())
        validation_strings: List[str] = [
            "Checking...",
            "Directory 1:",
            test_dir1 + "\n   " + str(fstruct1.files),
            "Directory 2:",
            test_dir2 + "\n" + str(fstruct2.files)
        ]
        self.assertCountEqual(self.get_and_clear_test_string(), validation_strings)

    def test_check_get_next_error_raised(self) -> None:
        state_data: StateData = StateData(ConfigManager(FSInterface), MockUI(), FSInterface)
        check: Check = Check(state_data)
        check.set_error_raised()
        self.assertTrue(isinstance(check.get_next(), Error))

    def test_check_get_next_exit_request(self) -> None:
        state_data: StateData = StateData(ConfigManager(FSInterface), MockUI(), FSInterface)
        check: Check = Check(state_data)
        check.set_exit_request()
        self.assertTrue(isinstance(check.get_next(), Final))

    def test_check_get_next_updated(self) -> None:
        state_data: StateData = StateData(ConfigManager(FSInterface), MockUI(), FSInterface)
        check: Check = Check(state_data)
        check.set_sync_required()
        self.assertTrue(isinstance(check.get_next(), Sync))

    def test_check_get_next_not_updated(self) -> None:
        state_data: StateData = StateData(ConfigManager(FSInterface), MockUI(), FSInterface)
        check: Check = Check(state_data)
        self.assertTrue(isinstance(check.get_next(), Wait))

    def test_wait_run_user_requests_exit(self) -> None:
        state_data: StateData = StateData(ConfigManager(FSInterface), MockUI(), FSInterface, verbose=True)
        wait: Wait = Wait(state_data)
        with unittest.mock.patch('builtins.print', self.add_to_test_string):
            wait.run()
        self.assertTrue(wait.get_exit_request())
        self.assertEqual(["Waiting..."], self.get_and_clear_test_string())

    def test_wait_run_user_continues(self) -> None:
        mock_ui: MockUI = MockUI()
        mock_ui.set_exit_request(False)
        state_data: StateData = StateData(ConfigManager(FSInterface), mock_ui, FSInterface, verbose=True)
        wait: Wait = Wait(state_data)
        wait.set_sleep_time(10e-6)
        with unittest.mock.patch('builtins.print', self.add_to_test_string):
            wait.run()
        self.assertFalse(wait.get_exit_request())
        self.assertEqual(["Waiting..."], self.get_and_clear_test_string())

    def test_wait_get_next_error_raised(self) -> None:
        state_data: StateData = StateData(ConfigManager(FSInterface), MockUI(), FSInterface)
        wait: Wait = Wait(state_data)
        wait.set_error_raised()
        self.assertTrue(isinstance(wait.get_next(), Error))

    def test_wait_get_next_exit_request(self) -> None:
        state_data: StateData = StateData(ConfigManager(FSInterface), MockUI(), FSInterface)
        wait: Wait = Wait(state_data)
        wait.set_exit_request()
        self.assertTrue(isinstance(wait.get_next(), Final))

    def test_wait_get_next_default(self) -> None:
        state_data: StateData = StateData(ConfigManager(FSInterface), MockUI(), FSInterface)
        wait: Wait = Wait(state_data)
        self.assertTrue(isinstance(wait.get_next(), Check))

    @tfuncs.handle_dir_tempfile
    @tfuncs.handle_test_dirs
    @tfuncs.handle_last_tempfile
    def test_sync_run_file_in1_notin2(self) -> None:
        test_dir1: str = str(self.tf.test_path1)
        fstruct1: FileStructure = FileStructure(test_dir1, FSInterface)
        test_dir2: str = str(self.tf.test_path2)
        fstruct2: FileStructure = FileStructure(test_dir2, FSInterface)
        fstruct_list: List[FileStructure] = [fstruct1, fstruct2]
        last_sync_dict: Dict[str, Any] = fstruct_list[0].files_to_json()

        test_filename: str = "test_file.txt"
        file_in1_notin2: str = str(self.tf.test_path1 / test_filename)
        tfuncs.create_file(file_in1_notin2)
        for fstruct in fstruct_list:
            fstruct.update_file_structure()
            fstruct.check_file_structure(last_sync_dict)

        state_data: StateData = StateData(ConfigManager(FSInterface), MockUI(), FSInterface, verbose=True)
        sync: Sync = Sync(state_data)
        sync.add_fstruct(fstruct1)
        sync.add_fstruct(fstruct2)
        with unittest.mock.patch('builtins.print', self.add_to_test_string):
            sync.run()

        for fstruct in fstruct_list:
            fstruct.update_file_structure()
        files_in1: List[str] = fstruct_list[0].files_to_list()
        files_in1 = tfuncs.remove_prefixes(files_in1, fstruct_list[0].get_directory_path())
        files_in2: List[str] = fstruct_list[1].files_to_list()
        files_in2 = tfuncs.remove_prefixes(files_in2, fstruct_list[1].get_directory_path())
        self.assertCountEqual(files_in1, files_in2)
        self.assertCountEqual(files_in1, [test_filename])
        self.assertCountEqual(files_in2, [test_filename])
        self.assertEqual(["Syncing..."], self.get_and_clear_test_string())
        self.assertFalse(sync.get_sync_required())

    def test_sync_get_next_error_raised(self) -> None:
        state_data: StateData = StateData(ConfigManager(FSInterface), MockUI(), FSInterface)
        sync: Sync = Sync(state_data)
        sync.set_error_raised()
        self.assertTrue(isinstance(sync.get_next(), Error))

    def test_sync_get_next_default(self) -> None:
        state_data: StateData = StateData(ConfigManager(FSInterface), MockUI(), FSInterface)
        wait: Sync = Sync(state_data)
        self.assertTrue(isinstance(wait.get_next(), Wait))

    def test_error_run(self) -> None:
        sync_error: SyncException = SyncException("Test", "Test State", "Test ID")
        state_data: StateData = StateData(ConfigManager(FSInterface), MockUI(), FSInterface, verbose=True)
        error: Error = Error(state_data)
        error.error = sync_error
        with unittest.mock.patch('builtins.print', self.add_to_test_string):
            error.run()

        validation_strings: List[str] = [
            "Error...",
            "Error in Test State, Error ID: Test ID" + "\n" + "Error Message: Test"
        ]
        self.assertCountEqual(validation_strings, self.get_and_clear_test_string())

    @tfuncs.handle_dir_tempfile
    @tfuncs.handle_test_dirs
    def test_error_sync_dirs_do_not_exist(self) -> None:
        input: List[str] = [str(self.tf.test_path1), str(self.tf.test_path2)]
        tfuncs.write_json(input, str(self.tf.sync_dir_file))
        state_data: StateData = StateData(ConfigManager(FSInterface), MockUI(), FSInterface)
        initial: Initial = Initial(state_data)
        initial.run()

        self.tf.remove_test_dirs()

        assert isinstance(initial.get_next(), Check)
        check: Check = Check(state_data)
        check.run()

        assert isinstance(check.get_next(), Error)
        error: Error = Error(state_data)
        error.run()
        self.assertTrue(isinstance(error.get_next(), Initial))

    def test_final_run(self) -> None:
        state_data: StateData = StateData(ConfigManager(FSInterface), MockUI(), FSInterface, verbose=True)
        final: Final = Final(state_data)
        with unittest.mock.patch('builtins.print', self.add_to_test_string):
            final.run()

        self.assertCountEqual(["Exiting..."], self.get_and_clear_test_string())

    def test_final_get_next(self) -> None:
        state_data: StateData = StateData(ConfigManager(FSInterface), MockUI(), FSInterface)
        final: Final = Final(state_data)
        self.assertTrue(isinstance(final.get_next(), End))
