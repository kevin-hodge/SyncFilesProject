# Define Sync FSM State Behavior
from filestructure_functions import *
from sync_gui import *


class StateMachine:
    """
    Adapted from: https://python-course.eu/applications-python/finite-state-machine.php
    Req #8: The program shall be implemented as a finite state machine.

    """

    def __init__(self):
        self.state_functions = {}  # Functions used in each state of the state machine
        self.initial_state = None
        self.final_states = []

    def new_state(self, state_name, state_function, final_state=0, initial_state=0):
        state_name = state_name.lower()
        self.state_functions[state_name] = state_function
        if final_state != 0:
            self.final_states.append(state_name)
        if initial_state != 0:
            self.initial_state = state_name

    def run(self, state_info):
        try:
            state_function = self.state_functions[self.initial_state]
        except:
            raise ValueError("Must set initial_state")
        if not self.final_states:
            raise ValueError("Must set at least one final_states")

        while True:
            (next_state, state_info) = state_function(state_info)
            if next_state.lower() in self.final_states:
                state_function = self.state_functions[next_state]
                state_function(state_info)
                break
            else:
                state_function = self.state_functions[next_state]


class StateInfo:
    """
    Carries program information from state to state.
    StateInfo Variables
        curr_state: string
            stores name of current state, initialize to initial state

        directories: list(FileStructure)
            stores the file

        err: class Exception
            catches any exceptions, passes message to handler in error state

        err_id: string
            gives exception identifier to help track down bugs

        exit_request: boolean
            unused

        prev_state: string
            stores name of previous state

        sync_gui: SyncGUI
            handles the graphical user interface of the program

        sync_required: boolean
            True if directories need to be sync'd

        to_update: list
            same structure as directories, but has 1 if file/folder needs to be updated and 0 otherwise

        verbose: boolean
            indicates if messages will be printed for debugging
    """

    def __init__(self, verbose=0):
        self.curr_state = "initial"
        self.directories = []
        self.err = []
        self.err_id = []
        self.exit_request = False
        self.prev_state = ""
        self.sync_gui = SyncGUI()
        self.sync_required = False
        self.to_update = []
        self.verbose = verbose

    def get_return_values(self, next_state):
        self.prev_state = self.curr_state
        if self.exit_request:
            self.curr_state = "final"
        else:
            self.curr_state = next_state
        return next_state, self

    def error_handle(self, err, err_id, ):
        self.err = err
        self.err_id = err_id
        return self.get_return_values("error")

    def check_exit_prompt(self):
        response = self.sync_gui.exit_prompt()
        if response == "Exit":
            self.exit_request = "Exit"
        return response

    def get_directory_prompt(self, invalid_dir):
        return self.sync_gui.directory_prompt(invalid_dir)

    def set_sync_directories(self, directories):
        set_sync_directories(directories, verbose=self.verbose)


def initial_state_function(state_info):
    """
    Initializes state_info and retrieves directories to synchronize.
    """
    print("Initializing...")

    # Retrieve directories to sync and initialize FileStructures
    try:
        # TODO Test what happens if "sync_directories_file.txt" is blank
        sync_directories = get_sync_directories(verbose=state_info.verbose)
    except Exception as err:
        return state_info.error_handle(err, "get_sync_directories")
    for dirs in sync_directories:
        state_info.directories.append(FileStructure(dirs, verbose=state_info.verbose))
        if state_info.verbose:
            print("Directories to sync:")
            print(state_info.directories[-1].directory_path)

    next_state = "check"
    return state_info.get_return_values(next_state)


def check_state_function(state_info):
    """
    Retrieves FileStructure information from directories and determines if sync is necessary.
    """
    if state_info.verbose:
        print("Checking...")
    assert len(state_info.directories) > 0

    try:
        for directory in state_info.directories:
            directory.get_file_structure()
            directory.check_file_structure()
            if state_info.verbose:
                print("Directory " + str(state_info.directories.index(directory) + 1) + ":")
                directory.print_file_structure()
                print("Last Updates:")
                directory.print_last_updates()
    except Exception as err:
        return state_info.error_handle(err, "get_file_structure")

    # Determine next state
    state_info.check_exit_prompt()
    state_info.sync_required = True
    next_state = "wait"  # effectively the else condition of the if statement
    if state_info.exit_request:
        next_state = "final"
    elif state_info.sync_required:
        next_state = "sync"
    return state_info.get_return_values(next_state)


def wait_state_function(state_info):
    """
    Waits before checking directories again
    """
    if state_info.verbose:
        print("Waiting...")

    # Wait before checking directory again
    time.sleep(10)

    next_state = "check"
    if state_info.exit_request:
        next_state = "final"
    return state_info.get_return_values(next_state)


def sync_state_function(state_info):
    """
    Synchronizes file directories.
    """
    print("Syncing...")
    assert state_info.sync_required
    # TODO Sync Files according to state_info.to_update

    # Probably do some kind of check here
    next_state = "wait"
    # next_state = "final"
    return state_info.get_return_values(next_state)


def error_state_function(state_info):
    """
    Req #7: The program shall notify the user if either directory cannot be found.
    TODO Needs to notify user through the GUI
    Handles errors that cause transitions from other states.
    """
    next_state = "final"  # default behavior when error is received is to exit
    if state_info.err_id == "get_sync_directories":
        if state_info.verbose:
            print("Couldn't read sync directories config file")
            print("Error Message: " + str(state_info.err))  # Prints error message
    elif state_info.err_id == "get_file_structure":
        invalid_directory = False
        directories = []
        for directory in state_info.directories:
            if not os.path.exists(directory.directory_path):
                invalid_directory = True
                directories.append(state_info.get_directory_prompt(directory.directory_path))
                if state_info.verbose:
                    print("Response: " + str(directories[-1]))
        if invalid_directory:
            state_info.set_sync_directories(directories)
            next_state = "final"
            return state_info.get_return_values(next_state)
        if state_info.verbose:
            print("Couldn't get 1 or more directory file structures")
            print("Error Message: " + str(state_info.err))  # Prints error message

    else:
        if state_info.verbose:
            print("Unknown error occurred")
            print("Previous State: " + state_info.prev_state)
            print("Error Message: " + str(state_info.err))
    return state_info.get_return_values(next_state)


def final_state_function(state_info):
    # Finish Up
    print("Exiting...")
