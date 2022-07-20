"""Sync States

Author: Kevin Hodge
"""

from typing import Optional
from abc import ABC, abstractmethod


class SyncState(ABC):
    next: object
    
    @abstractmethod
    def run(self) -> None:
        raise NotImplementedError

    def get_next(self) -> object:
        return self.next

    def set_next(self, next_state: object) -> None:
        self.next = next_state


class Initial(SyncState):
    def run(self) -> None:
        pass


class Wait(SyncState):
    def run(self) -> None:
        pass
