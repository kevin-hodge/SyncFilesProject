# Define Sync FSM State Behavior
import time
from sync_files_functions import *
"""
State Variables
state_info: list
    0: class Exception, catches any exceptions
    1: string, gives exception identifier to help track down bugs
    2: boolean, exit_command
    3: list, stores class FileStructure 

next_state: string
    gives next state
"""


def initial_state_function(state_info=[]):
    """
    Initializes state_info and retrieves directories to synchronize.
    """
    print("Initializing...")

    # Set-Up Error Handling
    state_info.append(Exception())  # stores exception raised
    state_info.append("")  # stores exception identifier (for debugging)
    state_info.append(False)  # exit request value, initialize to False

    # Retrieve directories to sync and initialize FileStructures
    try:
        sync_directories = get_sync_directories()
    except Exception as err:
        state_info[0] = err
        state_info[1] = "get_sync_directories"
        next_state = "error"
        return next_state, state_info
    directories = []
    for dirs in sync_directories:
        directories.append(FileStructure(dirs))
        #print(directories[-1].directory_path)

    # Add FileStructures to state_info
    state_info.append(directories)

    next_state = "listen"
    return next_state, state_info


def listen_state_function(state_info=[]):
    """
    Retrieves FileStructure information from directories and determines if sync is necessary.
    """
    print("Listening...")
    assert len(state_info) == 4

    # Wait
    time.sleep(10)
    try:
        for directory in state_info[3]:
            directory.get_file_structure()
            print("Directory:")
            directory.print_file_structure(offset=3)
    except Exception as err:
        state_info[0] = err
        state_info[1] = "get_file_structure"
        next_state = "error"
        return next_state, state_info

    # Determine next state (maybe check every hour? possible to check if file has been edited?)
    next_state = "listen"
    state_info[2] = True
    sync_required = True
    if state_info[2]:
        next_state = "final"
    elif sync_required:
        next_state = "sync"
    else:
        next_state = "listen"
    return next_state, state_info


def sync_state_function(state_info=[]):
    """
    Synchronizes file directories.
    """
    assert len(state_info) == 4
    print("Syncing...")
    # TODO Do Something
    next_state = "final"
    return next_state, state_info


def error_state_function(state_info=[]):
    """
    Handles errors that cause transitions from other states.
    """
    if state_info[1] == "get_sync_directories":
        print("Couldn't read sync_directories_file.txt")
        print(state_info[0])  # Prints error message
    elif state_info[1] == "get_file_structure":
        print("Couldn't get file structure")
        print(state_info[0])  # Prints error message
    else:
        print("Unknown error occurred")
    next_state = "final"
    return next_state, state_info


def final_state_function(state_info=[]):
    # TODO Finish Up
    print("Exiting...")
