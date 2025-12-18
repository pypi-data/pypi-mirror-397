"""
Task Executor Interface.

This module defines the protocol for the Task Executor.
The Executor is responsible for driving the execution of a Task Graph
by advancing the state of tasks in the TaskExecutionContext.

Responsibilities:
- Define the contract for execution.
- Ensure deterministic state progression.

Constraints:
- Interface only. No implementation logic here.
"""

from typing import Protocol, List, Optional
from axiom_conductor.context import TaskExecutionContext
from axiom_conductor.model import ExecutionEvent


class TaskExecutor(Protocol):
    """
    Protocol for a deterministic Task Executor.
    """

    def initialize(self, context: TaskExecutionContext) -> None:
        """
        Prepare the context for execution.
        Identify initial READY tasks.
        """
        ...

    def step(self, context: TaskExecutionContext) -> List[ExecutionEvent]:
        """
        Advance the execution by one step.
        - Check for completed tasks.
        - Update dependencies.
        - Schedule new READY tasks.
        - Return events generated during this step.
        """
        ...

    def run(self, context: TaskExecutionContext) -> None:
        """
        Run the execution loop until completion or failure.
        """
        ...
