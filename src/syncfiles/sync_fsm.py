"""Defines StateMachine and Sync Finite State Machine State Behavior.

Requirements:
    - Req #16: The program shall ask user for directories if config file does not contain sync directories.

Author: Kevin Hodge
"""
from typing import Any, List, Tuple
from syncfiles.file_structure import FileStructure
from syncfiles.config_manager import ConfigManager
from syncfiles.sync_gui import SyncGUI
import time
import os


class StateInfo:
    """Carries program information from state to state.

    Attributes:
        curr_state (str): Stores name of current state, initialize to initial state.
        directories (list[FileStructure]): Stores FileStructures for each sync directory.
        err (Exception): Catches any exceptions, passes message to handler in error state.
        err_id (str): Gives exception identifier to help track down bugs.
        exit_request (bool): Indicates exit has been requested.
        prev_state (str): Stores name of previous state.
        sync_gui (SyncGUI): Reference to graphical user interface of the program.
        sync_required (bool): Indicates that directories need to be synchronized.
        to_update (list[Any]): Same structure as directories, but has 1 if file/folder needs to be updated
        and 0 otherwise.
        verbose (bool, optional): Indicates if messages will be printed for debugging.

    """

    def __init__(self, verbose: bool = False) -> None:
        self.curr_state: str = "initial"
        self.directories: List[FileStructure] = list()
        self.manager: ConfigManager = ConfigManager()
        self.err: Exception = Exception()
        self.err_id: str = str()
        self.exit_request: bool = False
        self.prev_state: str = str()
        self.sync_gui: SyncGUI = SyncGUI()
        self.sync_required: bool = False
        self.to_update: List[Any] = list()
        self.verbose: bool = verbose

    def get_return_values(self, next_state) -> Tuple[str, Any]:
        """Handles checks and updates prior to each state transition.

        Args:
            next_state (str): Name of the requested next state.

        Returns:
            self.curr_state (str): Name of the actual next state.
            self: Carries program information from state to state.

        """
        assert isinstance(next_state, str)

        self.prev_state = self.curr_state
        if self.exit_request:
            self.curr_state = "final"
        else:
            self.curr_state = next_state
        return self.curr_state, self

    def error_handle(self, err: Exception, err_id: str) -> Tuple[str, Any]:
        """Handles errors caught from try/except block.

        Args:
            err (Exception): Exception being handled.
            err_id (str): Identifier used to track down errors.

        Returns:
            Return values from get_return_values().

        """
        assert isinstance(err, Exception)
        assert isinstance(err_id, str)

        self.err = err
        self.err_id = err_id
        return self.get_return_values("error")

    def check_exit_prompt(self) -> str:
        response = self.sync_gui.exit_prompt()
        if response == "Exit":
            self.exit_request = True
        return response

    def get_directory_prompt(self, num_valid_dir: int) -> str:
        return self.sync_gui.directory_prompt(num_valid_dir)


def initial_state_function(state_info: StateInfo) -> Tuple[str, StateInfo]:
    """Retrieves directories to synchronize and initializes FileStructures.

    Args:
        state_info (StateInfo): Carries program information from state to state.

    Returns:
        state_info.curr_state (str): Name of the actual next state.
        state_info: Carries program information from state to state.

    """
    if state_info.verbose:
        print("Initializing...")

    # Retrieve directories to sync and initialize FileStructures
    min_directories: int = 2
    try:
        sync_directories: List[str] = state_info.manager.read_sync_directories()
        while len(sync_directories) < min_directories:
            new_dir: str = state_info.sync_gui.directory_prompt(len(sync_directories), min_directories)
            sync_directories = state_info.manager.check_sync_directory(new_dir, sync_directories)
        state_info.manager.write_sync_directories(sync_directories)
    except Exception as err:
        return state_info.error_handle(err, "get_sync_directories")

    for dir in sync_directories:
        state_info.directories.append(FileStructure(dir, verbose=state_info.verbose))
        if state_info.verbose:
            print("Directories to sync:")
            print(state_info.directories[-1].directory_path)

    next_state: str = "check"
    return state_info.get_return_values(next_state)


def check_state_function(state_info: StateInfo) -> Tuple[str, StateInfo]:
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

    # Retrieves and checks FileStructures
    try:
        for directory in state_info.directories:
            directory.get_file_structure()
            # directory.check_file_structure()
            if state_info.verbose:
                print(f"Directory {str(state_info.directories.index(directory) + 1)}:")
                directory.print_file_structure()
                print("Last Updates:")
                directory.print_last_update()
    except Exception as err:
        return state_info.error_handle(err, "get_file_structure")

    # Determine next state
    state_info.check_exit_prompt()
    state_info.sync_required = True  # TODO: Make this dependent on checking if the FileStructures need to be updated.
    next_state: str = "wait"  # effectively the else condition of the if statement
    if state_info.sync_required:
        next_state = "sync"
    return state_info.get_return_values(next_state)


def wait_state_function(state_info: StateInfo) -> Tuple[str, StateInfo]:
    """Waits before checking directories again.

    Args:
        state_info (StateInfo): Carries program information from state to state.

    Returns:
        state_info.curr_state (str): Name of the actual next state.
        state_info: Carries program information from state to state.

    """
    if state_info.verbose:
        print("Waiting...")

    # Wait before checking directory again
    time.sleep(10)

    next_state: str = "check"
    return state_info.get_return_values(next_state)


def sync_state_function(state_info: StateInfo) -> Tuple[str, StateInfo]:
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

    # TODO Sync Files according to state_info.to_update
    # Probably do some kind of check here
    next_state: str = "wait"
    return state_info.get_return_values(next_state)


def error_state_function(state_info: StateInfo) -> Tuple[str, StateInfo]:
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
    if state_info.verbose:
        print("Error...")

    next_state: str = "final"  # default behavior when error is received is to exit

    if state_info.err_id == "get_sync_directories":
        if state_info.verbose:
            print("Couldn't read sync directories config file")
            print(f"Error Message: {str(state_info.err)}")  # Prints error message

    elif state_info.err_id == "get_file_structure":
        for directory in state_info.directories:
            if not os.path.exists(directory.directory_path):
                next_state = "initial"
                return state_info.get_return_values(next_state)
        if state_info.verbose:
            print("Couldn't get 1 or more directory file structures")
            print(f"Error Message: {str(state_info.err)}")  # Prints error message

    else:
        if state_info.verbose:
            print("Unknown error occurred")
            print(f"Previous State: {state_info.prev_state}")
            print(f"Error Message: {str(state_info.err)}")

    return state_info.get_return_values(next_state)


def final_state_function(state_info: StateInfo) -> Tuple[str, StateInfo]:
    """Performs final tasks prior to exiting.

    Args:
        state_info (StateInfo): Carries program information from state to state.

    Returns:
        state_info.curr_state (str): Name of the actual next state.
        state_info: Carries program information from state to state.

    """
    if state_info.verbose:
        print("Exiting...")

    return state_info.get_return_values(state_info.prev_state)
