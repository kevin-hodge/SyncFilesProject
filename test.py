"""Sync Files Project Test


Author: Kevin Hodge
"""
import os.path
import json
import unittest
from filestructure_functions import get_sync_directories


def check_sync_dir_contents(expected_input1, expected_input2):
    with


class GetSyncDirectoriesTestCase(unittest.TestCase):
    def no_config_test(self):
        # delete config if it exists
        config_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
        sync_dir_file = 'sync_directories_file.json'
        sync_dir_path = os.path.join(config_path, sync_dir_file)
        if os.path.exists(sync_dir_path):
            os.remove(sync_dir_path)

        # Create test directories


        # Maybe more tests
        # Eventually enter correct directories
        # Run function
        buffer = get_sync_directories()

        # Check that file contains correct information
        expected_dir1 = ""
        expected_dir2 = ""


    def invalid_directory_test(self):
        pass

    def too_few_directories_test(self):
        pass

    def nonunique_directories_test(self):
        pass
