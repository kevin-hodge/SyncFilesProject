"""Defines Sync Finite State Machine State Behavior.

Author: Kevin Hodge
"""

from typing import Any, List, Tuple, Optional
# from syncfiles.sync_exception import SyncException
from syncfiles.file_structure import FileStructure
from syncfiles.config_manager import ConfigManager
from syncfiles.sync_ui import SyncUI
import time
from pathlib import Path
from enum import Enum


class State(Enum):
    INITIAL: int = 1
    CHECK: int = 2
    WAIT: int = 3
    SYNC: int = 4
    ERROR: int = 5
    FINAL: int = 6


class StateInfo:
    """Carries program information from state to state.

    Attributes:
        curr_state (str): Stores name of current state, initialize to initial state.
        directories (list[FileStructure]): Stores FileStructures for each sync directory.
        err (Exception): Catches any exceptions, passes message to handler in error state.
        err_id (str): Gives exception identifier to help track down bugs.
        exit_request (bool): Indicates exit has been requested.
        prev_state (str): Stores name of previous state.
        gui (SyncGUI): Reference to graphical user interface of the program.
        sync_required (bool): Indicates that directories need to be synchronized.
        to_update (list[Any]): Same structure as directories, but has 1 if file/folder needs to be updated
        and 0 otherwise.
        verbose (bool, optional): Indicates if messages will be printed for debugging.

    """
    def __init__(self, initial: State, config: ConfigManager, gui: SyncUI, verbose: bool = False) -> None:
        self.curr_state: State = initial
        self.prev_state: State = initial
        self.directories: List[FileStructure] = []
        self.config: ConfigManager = config
        self.gui: SyncUI = gui
        self.err: Exception = Exception()
        self.err_id: str = "Unknown Function"
        self.exit_request: bool = False
        self.sync_required: bool = False
        self.verbose: bool = verbose

    def check_exit_prompt(self) -> bool:
        exit_request: bool = self.gui.exit_prompt()
        if exit_request:
            self.exit_request = True
        return self.exit_request

    def check_sync_required(self, num_changes: int) -> None:
        if num_changes > 0:
            self.sync_required = True

    def initialize_file_structures(self, sync_directories: List[str]) -> None:
        for dir in sync_directories:
            self.add_directory(FileStructure(dir, verbose=self.verbose))
            if self.verbose:
                print("Directories to sync:")
                print(self.directories[-1].get_directory_path())

    def add_directory(self, dir: FileStructure) -> None:
        self.directories.append(dir)

    def get_sync_directories(self) -> List[str]:
        min_directories: int = 2
        sync_directories: List[str] = self.config.read_sync_directories()
        while len(sync_directories) < min_directories:
            new_dir: str = self.get_directory_prompt(len(sync_directories), min_directories)
            sync_directories = self.config.check_sync_directory(new_dir, sync_directories)
        self.config.write_sync_directories(sync_directories)
        return sync_directories

    def get_directory_prompt(self, num_valid_dir: int, min_dir: int) -> str:
        return self.gui.directory_prompt(num_valid_dir, min_dir)

    def handle_error(self, err: Exception, err_id: str) -> Tuple[State, Any]:
        """Handles errors caught from try/except block.

        Args:
            err (Exception): Exception being handled.
            err_id (str): Identifier used to track down errors.

        Returns:
            Return values from get_return_values().

        """
        self.err = err
        self.err_id = err_id
        return self.get_return_values(State.ERROR)

    def get_return_values(self, next_state: Optional[State] = None) -> Tuple[State, Any]:
        """Handles checks and updates prior to each state transition.

        Args:
            next_state (str): Name of the requested next state.

        Returns:
            self.curr_state (str): Name of the actual next state.
            self: Carries program information from state to state.

        """
        self.prev_state = self.curr_state
        if next_state is not None:
            self.curr_state = next_state
        else:
            self.curr_state = self.determine_next_state()
        return self.curr_state, self

    def determine_next_state(self) -> State:
        if self.exit_request:
            return State.FINAL
        elif self.sync_required:
            return State.SYNC
        elif self.curr_state == State.INITIAL:
            return State.CHECK
        elif self.curr_state == State.SYNC:
            return State.WAIT
        elif self.curr_state == State.CHECK:
            return State.WAIT
        elif self.curr_state == State.WAIT:
            return State.CHECK
        elif self.curr_state == State.ERROR:
            return State.FINAL
        else:
            return State.FINAL

    def check_for_changes(self) -> int:
        changes_found: int = 0
        for directory in self.get_directories():
            directory.update_file_structure()
            if self.verbose:
                print(f"Directory {str(self.directories.index(directory) + 1)}:")
                directory.print_file_structure()
            changes: int = directory.check_file_structure(self.config.read_last_sync_file())
            if changes > 0:
                changes_found = changes
        return changes_found

    def get_directories(self) -> List[FileStructure]:
        return self.directories


def initial_state_function(state_info: StateInfo) -> Tuple[State, StateInfo]:
    """Retrieves directories to synchronize and initializes FileStructures.

    Args:
        state_info (StateInfo): Carries program information from state to state.

    Returns:
        state_info.curr_state (str): Name of the actual next state.
        state_info: Carries program information from state to state.

    """
    if state_info.verbose:
        print("Initializing...")

    try:
        sync_directories: List[str] = state_info.get_sync_directories()
        state_info.initialize_file_structures(sync_directories)
    except Exception as e:
        return state_info.handle_error(e, "initialize_file_structures")

    return state_info.get_return_values()


def check_state_function(state_info: StateInfo) -> Tuple[State, StateInfo]:
    """Retrieves FileStructure information from directories and determines if sync is necessary.

    Args:
        state_info (StateInfo): Carries program information from state to state.

    Returns:
        state_info.curr_state (str): Name of the actual next state.
        state_info: Carries program information from state to state.

    """
    assert len(state_info.directories) > 0

    if state_info.verbose:
        print("Checking...")

    try:
        num_changes: int = state_info.check_for_changes()
    except Exception as err:
        return state_info.handle_error(err, "check_for_changes")

    state_info.check_sync_required(num_changes)
    state_info.check_exit_prompt()
    return state_info.get_return_values()


def wait_state_function(state_info: StateInfo) -> Tuple[State, StateInfo]:
    """Waits before checking directories again.

    Args:
        state_info (StateInfo): Carries program information from state to state.

    Returns:
        state_info.curr_state (str): Name of the actual next state.
        state_info: Carries program information from state to state.

    """
    if state_info.verbose:
        print("Waiting...")

    time.sleep(10)

    state_info.check_exit_prompt()
    return state_info.get_return_values()


def sync_state_function(state_info: StateInfo) -> Tuple[State, StateInfo]:
    """Synchronizes directories.

    Args:
        state_info (StateInfo): Carries program information from state to state.

    Returns:
        state_info.curr_state (str): Name of the actual next state.
        state_info: Carries program information from state to state.

    """
    assert state_info.sync_required

    if state_info.verbose:
        print("Syncing...")

    # TODO Sync Files

    state_info.check_exit_prompt()
    return state_info.get_return_values()


def error_state_function(state_info: StateInfo) -> Tuple[State, StateInfo]:
    """Handles errors that cause transitions from other states.

    Requirements:
        Req #7: The program shall notify the user if either directory cannot be found.
        TODO Needs to notify user through the GUI

    Args:
        state_info (StateInfo): Carries program information from state to state.

    Returns:
        state_info.curr_state (str): Name of the actual next state.
        state_info: Carries program information from state to state.

    """
    error_description: str = f"Error in {state_info.prev_state}: {state_info.err_id} raised the following error:"
    error_message: str = f"Error Message: {str(state_info.err)}"
    if state_info.verbose:
        print("Error...")
        print(error_description)
        print(error_message)

    if state_info.err_id == "check_for_changes":
        for directory in state_info.get_directories():
            if not Path(directory.get_directory_path()).exists():
                next_state: State = State.INITIAL
                return state_info.get_return_values(next_state)

    return state_info.get_return_values()


def final_state_function(state_info: StateInfo) -> Tuple[State, StateInfo]:
    """Performs final tasks prior to exiting.

    Args:
        state_info (StateInfo): Carries program information from state to state.

    Returns:
        state_info.curr_state (str): Name of the actual next state.
        state_info: Carries program information from state to state.

    """
    if state_info.verbose:
        print("Exiting...")

    return state_info.get_return_values()
