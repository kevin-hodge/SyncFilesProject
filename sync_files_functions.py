"""
Sync Files Project: Functions
-----------------------------
Contains the functions for the Sync Files Project.
"""

import os
import sys


def get_sync_directories():
    """
    # Req #2: The program shall find sync_directories_file.txt (text file containing the sync directories).
    # Req #3: The program shall open and read sync_directories_file.txt.
    Finds sync_directories_file.txt file in working directory, reads entries, and returns tuple with string values

    ASSUMES: sync_directories_file structure is directory paths separated by newline characters

    :return:
    file_directories: list(string)
        list of file directories found in "sync_directories_file.txt"

    Idea: Currently this only works on MacOS, can I somehow figure out the os and implement both ways?
    """
    # Find and read sync_directories_file
    folder_path = os.getcwd()  # get working directory
    file_name = "sync_directories_file.txt"  # should store this value somewhere else eventually, what if this changes?
    file_path = os.path.join(folder_path, file_name)

    # Read file (with ensures file is closed even if an exception occurs)
    with open(file_path) as file_to_read:
        buffer = file_to_read.read()

    # Parse directory paths and return list of directories
    return buffer.split("\n")


def recursive_get_directory(directory):
    """
    Recursive function that gives the structure of all files and folder contained within a directory
    :param directory: string
        path to the directory
    :return file_structure: list
        list of strings and other lists, lists contain string with name of directory and another list with entries in
        that directory
    """
    file_structure = []
    for entry in os.listdir(directory):
        entry_path = os.path.join(directory,entry)
        if os.path.isfile(entry_path):
            file_structure.append(entry)
        elif os.path.isdir(entry_path):
            sub_dir = [entry, []]
            sub_dir[1] = recursive_get_directory(entry_path)
            file_structure.append(sub_dir)
        else:
            return
    return file_structure


def recursive_print_directory(file_structure, offset=0):
    """

    :param file_structure:
    :param offset:
    :return file_structure:
    """
    for entry in file_structure:
        if type(entry) == str:
            print(offset*" " + entry)
        else:
            print(offset*" " + entry[0])
            print_file_structure(entry[1], offset+3)


class FileStructure:
    """
    Req #4: The program shall retrieve the names and file structure of all files and folders in both directories.
    Req #10: File structures shall be stored in a class "FileStructure".
    class that contains the file structure of a directory.

    :input:

    """

    def __init__(self, directory_path):
        self.directory_path = directory_path
        self.files = list()
        pass

    def get_file_structure(self):
        """
        Reads all files and folders below the directory
        :return:
        self.files: list
            self.files contains paths to all files (strings) and all folders (list, with two elements, ) in the directory.
            folders contained in files, contain names of all files and folders in those folders,
            pattern continues until a directory with no folders is found.
        """
        self.files = recursive_get_directory(self.directory_path)
        return self.files

    def print_file_structure(self, offset=0):
        recursive_print_directory(self.files, offset)

    def update(self):
        """
        # TODO Req #5: The program shall determine the Most_Recently_Updated_Directory and the To_Sync_Directory.
        # TODO Req #6: The program shall copy all files in the Most_Recently_Updated_Directory to the To_Sync_Directory.

        :return:
        """
        pass


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

    def run(self, state_info=[]):
        if not self.initial_state:
            raise InitializationError("Must set initial_state")
        if not self.final_states:
            raise InitializationError("Must set at least one final_states")
        state_function = self.state_functions[self.initial_state]
        while True:
            (next_state, state_info) = state_function(state_info)
            if next_state.lower() in self.final_states:
                state_function = self.state_functions[next_state]
                state_function(state_info)
                break
            else:
                state_function = self.state_functions[next_state]
