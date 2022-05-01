"""Defines StateMachine and Sync Finite State Machine State Behavior.


Author: Kevin Hodge
"""
from typing import Any, List, Dict, Tuple, Optional, Callable, cast
from syncfiles.file_ops.filestructure_functions import get_sync_directories, FileStructure
from syncfiles.gui.sync_gui import SyncGUI
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

    def get_directory_prompt(self, valid_dir: Optional[List[str]] = None):
        return self.sync_gui.directory_prompt(valid_dir)


class StateMachine:
    """Implementation of a finite state machine.

    Adapted from: https://python-course.eu/applications-python/finite-state-machine.php

    Requirements:
        - Req #8: The program shall be implemented as a finite state machine.

    Attributes:
        state_functions (dict): Dictionary of functions representing the states of the state machine.
        initial_state (str): Lowercase name of the initial state.
        final_states (list): Contains the names of all final states.

    """

    def __init__(self):
        self.state_functions: Dict[str, Callable[[StateInfo], Tuple[str, StateInfo]]] = dict()
        self.initial_state: Optional[str] = None
        self.final_states: List[str] = list()

    def new_state(self, state_name: str, state_function: Callable[[StateInfo], Tuple[str, StateInfo]],
                  final_state: bool = False, initial_state: bool = False) -> None:
        """Adds new state to state_functions.

        Args:
            state_name (str): Name of the state being added to state_functions.
            state_function (function): Function being added to state_functions.
            final_state (int): Indicates new state is a final state if set to True.
            initial_state (int): Indicates new state is the initial state if set to True.

        """
        state_name = state_name.lower()
        self.state_functions[state_name] = state_function
        if final_state != 0:
            self.final_states.append(state_name)
        if initial_state != 0:
            self.initial_state = state_name

    def run(self, state_info: StateInfo) -> None:
        """Runs the StateMachine if one initial state and at least one final state have been specified.

        Args:
            state_info (class): Contains information about the state machine carried from state to state.

        """
        try:
            state_function: Callable[[StateInfo], Tuple[str, StateInfo]] = self.state_functions[
                cast(str, self.initial_state)]
        except Exception:
            raise ValueError("Must set initial_state")
        if not self.final_states:
            raise ValueError("Must set at least one final_states")

        while True:
            next_state: str
            next_state, state_info = state_function(state_info)
            if next_state.lower() in self.final_states:
                state_function = self.state_functions[next_state]
                state_function(state_info)
                break
            else:
                state_function = self.state_functions[next_state]


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
    try:
        sync_directories: List[str] = get_sync_directories(state_info.sync_gui, verbose=state_info.verbose)
    except Exception as err:
        return state_info.error_handle(err, "get_sync_directories")
    for dirs in sync_directories:
        state_info.directories.append(FileStructure(dirs, verbose=state_info.verbose))
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

    #
    try:
        for directory in state_info.directories:
            directory.get_file_structure()
            directory.check_file_structure()
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
