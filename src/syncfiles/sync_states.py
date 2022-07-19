"""Sync States

Author: Kevin Hodge
"""

from abc import ABC, abstractmethod


class State(ABC):
    @abstractmethod
    def run(self) -> None:
        raise NotImplementedError


class Initial(State):
    def run(self) -> None:
        pass
