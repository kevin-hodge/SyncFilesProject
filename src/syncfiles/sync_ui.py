"""Handles the Graphical User Interface for the program.


Author: Kevin Hodge
"""

from abc import ABC, abstractmethod


class SyncUI(ABC):
    """Abstract Class that handles all UI interactions.

    Attributes:
        None

    """
    @abstractmethod
    def exit_prompt(self) -> bool:
        """Ask the user if app should exit and return answer."""

    @abstractmethod
    def directory_prompt(self, num_valid_dir: int, min_dir: int = 2) -> str:
        """Asks user to enter a valid directory

        Args:
            invalid_dir (list): list initialized to [] on each function call.
            min_dir (int): number of directories required.

        """
