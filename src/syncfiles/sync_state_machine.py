"""Sync State Machine

Author: Kevin Hodge
"""

from abc import ABC, abstractmethod


class SyncState(ABC):
    @abstractmethod
    def run(self) -> None:
        """Executes state behavior."""

    @abstractmethod
    def get_next(self) -> object:
        """Gets next state."""


class End(SyncState):
    def run(self) -> None:
        pass

    def get_next(self) -> SyncState:
        return End()


class SyncStateMachine:
    def __init__(self) -> None:
        self.state: SyncState = End()

    def set_initial_state(self, initial: SyncState) -> None:
        assert isinstance(initial, SyncState)
        self.state = initial

    def run(self) -> None:
        while True:
            self.state.run()
            self.state = self.state.get_next()  # type: ignore[assignment]
            if isinstance(self.state, End):
                break
