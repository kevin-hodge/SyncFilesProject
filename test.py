"""Sync Files Project Test


Author: Kevin Hodge
"""
import os.path
import json
import unittest
from filestructure_functions import get_sync_directories
import sync_gui
from pynput.keyboard import Key, Controller
import threading
import time


def get_json_contents(file_path):
    with open(file_path, "r") as json_file:
        json_data = json.load(json_file)
    return json_data


def type_response(typed_response):
    time.sleep(0.1)
    keyboard = Controller()
    for entry in typed_response:
        for key in entry:
            keyboard.press(key)
            keyboard.release(key)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        time.sleep(0.1)


class GetSyncDirectoriesTestCase(unittest.TestCase):
    """Test case for get_sync_directories()"""

    def test_no_config_file(self):
        """Tests if no config file exists."""
        # Move config file contents and delete config file
        config_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
        sync_dir_file = "sync_directories_file.json"
        sync_dir_path = os.path.join(config_path, sync_dir_file)
        tempfile = os.path.join(config_path, "temp_sync_directories_file.json")
        if os.path.exists(sync_dir_path):
            with open(tempfile, "w") as json_file:
                json.dump(get_json_contents(sync_dir_path), json_file)
            os.remove(sync_dir_path)

        # Create test directories
        test_path1 = os.path.join(config_path, "test_dir1")
        test_path2 = os.path.join(config_path, "test_dir2")
        if not os.path.exists(test_path1):
            os.mkdir(test_path1)
        if not os.path.exists(test_path2):
            os.mkdir(test_path2)

        # Maybe more tests
        # Eventually enter correct directories
        user_entry = (test_path1, test_path2)
        keyboard_thread = threading.Thread(target=type_response, args=(user_entry,))
        keyboard_thread.start()

        gui = sync_gui.SyncGUI()
        get_sync_directories(gui)  # wxWidgets doesn't like being run outside the main thread.

        # print("Waiting for keyboard_thread to finish.")
        keyboard_thread.join(timeout=5)

        # Check that file contains correct information
        buffer = get_json_contents(sync_dir_path)
        self.assertEqual(tuple(buffer), user_entry)

        # Clean up after test
        if os.path.exists(test_path1):
            os.rmdir(test_path1)  # only works if folder is empty
        if os.path.exists(test_path2):
            os.rmdir(test_path2)  # only works if folder is empty
        with open(sync_dir_path, "w") as json_file:
            if os.path.exists(tempfile):
                json.dump(get_json_contents(tempfile), json_file)
                os.remove(tempfile)


if __name__ == "__main__":
    unittest.main()
