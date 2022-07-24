"""Tests sync_state_machine

Author: Kevin Hodge
"""

import unittest
from syncfiles.sync_state_machine import SyncStateMachine, SyncState, End


class State1(SyncState):
    def run(self) -> None:
        pass

    def get_next(self) -> SyncState:
        return State2()


class State2(SyncState):
    def run(self) -> None:
        raise ValueError("Pass")

    def get_next(self) -> SyncState:
        return End()


class SyncStateMachineTestCase(unittest.TestCase):
    def test_build_and_run(self) -> None:
        state1: State1 = State1()
        state_machine: SyncStateMachine = SyncStateMachine()
        state_machine.set_initial_state(state1)
        try:
            state_machine.run()
        except ValueError as err:
            assert str(err) == "Pass"

    def test_no_set_initial(self) -> None:
        state_machine: SyncStateMachine = SyncStateMachine()
        state_machine.run()
