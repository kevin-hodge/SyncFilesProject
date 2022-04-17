"""
SyncFilesProject
----------------
Ground Rules:
This is a simple project that will sync a file structure located in two locations on a computer (mac or windows).
The two locations will be defined in a text file (sync_directories_file.txt) in the program's directory.
    - Might change to JSON config file and add prompt to enter file location if files cannot be found.
The file sync will occur when a difference is found between the file_structures.
    - Should program just start when the computer starts and wait for a time of day to run?
    - Can continuously running program check for edits to one or both file_structures?
    - Possible to check which files have been most recently edited? Yes
        - If so, could just sync the files that have been edited and leave the rest (if last dates of edit/sync match).
Difficult Cases:
    - How to determine if a folder or file name has been changed vs. a folder has been deleted and a new folder added?
        - Does it actually matter? Just delete the old file or folder and create a new folder or file copied from the
        most recently updated directory
    - How to handle if a file is deleted in one location, should program delete it in the other location?
        - Yes


Requirements (LR: 17):
    - Req #1: The program shall determine the working directory.
    - Req #15: The program shall store and get sync directories from a config file.
    - Req #16: The program shall ask user for directories if config file does not contain sync directories.
    - Req #17: The program shall update config file with directory provided by user (if it exists).
    - Req #2: The program shall find sync_directories_file.txt (text file containing the sync directories).
    - Req #3: The program shall open and read sync_directories_file.txt.
    - Req #4: The program shall retrieve the names and file structure of all files and folders in both directories.
    - Req #14: The program shall check if the most recently updated time matches last sync time (if it exists).
    - Req #12: The program shall determine the files and folders that have been most recently updated.
    - TODO Req #13: The program shall copy the most recently updated files and folders to the other directory.
    - Req #5: Deleted
    - Req #6: Deleted
    - TODO Req #11: After sync, the program shall store the synchronized file_structure in a config file.
    - Req #7: The program shall notify the user if either directory cannot be found.
    - Req #8: The program shall be implemented as a finite state machine.
    - Req #9: The program shall be version controlled in a github repository.
    - Req #10: File structures shall be stored in a class "FileStructure".
"""
from sync_fsm import *

if __name__ == '__main__':
    # Only For Debugging
    verbose = 1

    # Initialize StateMachine
    Sync_FSM = StateMachine()
    Sync_StateInfo = StateInfo(verbose)
    Sync_FSM.new_state("initial", initial_state_function, initial_state=1)
    Sync_FSM.new_state("check", check_state_function)
    Sync_FSM.new_state("wait", wait_state_function)
    Sync_FSM.new_state("sync", sync_state_function)
    Sync_FSM.new_state("error", error_state_function)
    Sync_FSM.new_state("final", final_state_function, final_state=1)

    # Start StateMachine
    Sync_FSM.run(Sync_StateInfo)

