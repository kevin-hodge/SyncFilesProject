"""Sync Files Project Main

Ground Rules:
    1. This project will sync a file structure located in two locations on a computer (mac or windows).
    2. The two locations will be defined in a text file (sync_directories_file.txt) in the program's directory.
        - Might change to JSON config file and add prompt to enter file location if files cannot be found.
    3. The file sync will occur when a difference is found between the file_structures.
        - The program should wait 10 seconds between either checking or syncing.
        - The program should check for additions, removals, or updates to each file structure.
        - The program should check for differences between the file structures.
        - The program should copy all updated files from each directory to the other(s).

Difficult Cases:
    1. How to determine if a folder or file name has been changed vs. a folder has been deleted and a new folder added?
        - Just delete the old file or folder and create a new folder or file copied from the
            most recently updated directory
    2. How to handle if a file is deleted in one location, should program delete it in the other location?
        - Yes

Requirements (LR: 18):
    - Req #1: The program shall determine the working directory.
    - Req #15: The program shall store and get sync directories from a config file.
    - Req #16: The program shall ask user for directories if config file does not contain sync directories.
    - Req #17: The program shall update config file with directory provided by user (if it exists).
    - Req #2: The program shall find sync_directories_file.json (json file containing the sync directories).
    - Req #3: The program shall open and read sync_directories_file.json.
    - Req #4: The program shall retrieve the names and file structure of all files and folders in both directories.
    - Req #18: The program shall load last_sync_files and last_sync_time from config file.
    - Req #14: The program shall check if last_update is greater than last_sync_time (if it exists).
    - Req #12: The program shall determine the files and folders that have been updated.
    - TODO Req #13: The program shall copy updated files and folders to the other directory.
    - Req #5: Deleted
    - Req #6: Deleted
    - TODO Req #11: After sync, the program shall store the synchronized FileStructure.files and last sync time in a
        config file.
    - Req #7: The program shall notify the user if either directory cannot be found.
    - Req #8: The program shall be implemented as a finite state machine.
    - Req #9: The program shall be version controlled in a github repository.
    - Req #10: File structures shall be stored in a class "FileStructure".

Author: Kevin Hodge
"""

from syncfiles.config_manager import ConfigManager
from syncfiles.wx_gui import WxGUI
from syncfiles.sync_state_machine import SyncStateMachine
from syncfiles.sync_states import Initial, StateData


def main() -> None:
    config: ConfigManager = ConfigManager()
    gui: WxGUI = WxGUI()
    state_data: StateData = StateData(config, gui, verbose=True)
    initial: Initial = Initial(state_data)
    state_machine: SyncStateMachine = SyncStateMachine()
    state_machine.set_initial_state(initial)
    state_machine.run()


if __name__ == '__main__':
    main()
