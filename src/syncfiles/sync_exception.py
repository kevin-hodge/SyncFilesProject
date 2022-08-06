"""Sync Exception

Author: Kevin Hodge
"""

from typing import Optional


class SyncException(Exception):
    def __init__(self, message: Optional[str] = None, prev_state: str = "Unknown State",
                 error_id: str = "Unknown Error") -> None:
        self.__prev_state: str = prev_state
        self.__error_id: str = error_id
        super().__init__(message)

    def get_error_message(self) -> str:
        error_description: str = f"Error in {self.__prev_state}, Error ID: {self.__error_id}"
        error_message: str = f"Error Message: {str(self)}"
        return f"{error_description}\n{error_message}"

    def get_error_id(self) -> str:
        return self.__error_id

    def set_prev_state(self, prev_state: str) -> None:
        self.__prev_state = prev_state
