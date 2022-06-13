"""Contains the StateMachine Class

Author: Kevin Hodge
"""

from typing import Dict, Callable, List, Any, Optional


class StateMachine:
    """Implementation of a finite state machine.

    Adapted from: https://python-course.eu/applications-python/finite-state-machine.php

    Requirements:
        - Req #8: The program shall be implemented as a finite state machine.

    Attributes:
        state_functions (dict): Dictionary of functions representing the states of the state machine.
        initial_state (str): Lowercase name of the initial state.
        final_states (list): Contains the names of all final states.

    """
    def __init__(self):
        self.state_functions: Dict[str, Callable[[Any], Any]] = dict()
        self.initial_state: Optional[int] = None
        self.final_states: List[int] = list()

    def new_state(self, state_name: int, state_function: Callable[[Any], Any],
                  final_state: bool = False, initial_state: bool = False) -> None:
        """Adds new state to state_functions.

        Args:
            state_name (str): Name of the state being added to state_functions.
            state_function (function): Function being added to state_functions.
            final_state (int): Indicates new state is a final state if set to True.
            initial_state (int): Indicates new state is the initial state if set to True.

        """
        self.state_functions[state_name] = state_function
        if final_state != 0:
            self.final_states.append(state_name)
        if initial_state != 0:
            self.initial_state = state_name

    def run(self, state_info: Any) -> None:
        """Runs the StateMachine if one initial state and at least one final state have been specified.

        Args:
            state_info (class): Contains information about the state machine carried from state to state.

        """
        try:
            state_function: Callable[[Any], Any] = self.state_functions[self.initial_state]
        except Exception:
            raise ValueError("Must set initial_state")
        if not self.final_states:
            raise ValueError("Must set at least one final_states")

        while True:
            next_state: int
            next_state, state_info = state_function(state_info)
            if next_state in self.final_states:
                state_function = self.state_functions[next_state]
                state_function(state_info)
                break
            else:
                state_function = self.state_functions[next_state]
