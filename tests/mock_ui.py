"""Test interface for sending signals through the GUI.

Author: Kevin Hodge
"""

from typing import List, Optional
from syncfiles.sync_ui import SyncUI


class MockUI(SyncUI):
    def __init__(self, directories: Optional[List[str]] = None) -> None:
        self.__exit_request: bool = True
        self.__request_count: int = 0
        if directories is not None:
            self.__directories: List[str] = directories
        else:
            self.__directories = []
        super().__init__()

    def exit_prompt(self) -> bool:
        return self.__exit_request

    def directory_prompt(self, num_valid_dir: int, min_dir: int = 2) -> str:
        if self.__request_count >= len(self.__directories):
            self.__request_count = 0
        else:
            self.__request_count += 1
        return self.__directories[self.__request_count]

    def get_exit_request(self) -> bool:
        return self.__exit_request

    def set_exit_request(self, exit_request: bool = True) -> None:
        self.__exit_request = exit_request

    def get_directories(self) -> List[str]:
        return self.__directories

    def add_directory(self, directory: str) -> None:
        self.__directories.append(directory)
