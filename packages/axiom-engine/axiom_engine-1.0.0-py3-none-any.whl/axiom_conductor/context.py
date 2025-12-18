"""
Task Execution Context.

This module defines the runtime context for executing a Task Graph.
It acts as the "state machine" container, tracking the progress of every task.

Responsibilities:
- Hold the authoritative TaskGraph.
- Track the current ExecutionState of every task.
- Store execution results.
- Provide access to readiness information.

Constraints:
- No business logic (state transitions are handled by transitions.py).
- No side effects.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional

from axiom_canon.task_graph import TaskGraph
from axiom_canon.readiness import TaskReadinessResult
from axiom_conductor.model import TaskExecutionState, TaskExecutionResult


@dataclass
class TaskExecutionContext:
    """
    Runtime context for a Task Graph execution.
    """
    graph: TaskGraph
    readiness: TaskReadinessResult
    
    # Runtime state tracking
    # Maps task_id -> current state
    states: Dict[str, TaskExecutionState] = field(default_factory=dict)
    
    # Results storage
    # Maps task_id -> result (if completed)
    results: Dict[str, TaskExecutionResult] = field(default_factory=dict)
    
    def __post_init__(self):
        """
        Initialize states for all tasks in the graph.
        Default to PENDING.
        """
        for task_id in self.graph.tasks:
            if task_id not in self.states:
                self.states[task_id] = TaskExecutionState.PENDING

    def get_state(self, task_id: str) -> TaskExecutionState:
        return self.states.get(task_id, TaskExecutionState.PENDING)

    def set_state(self, task_id: str, state: TaskExecutionState):
        if task_id in self.graph.tasks:
            self.states[task_id] = state

    def set_result(self, task_id: str, result: TaskExecutionResult):
        self.results[task_id] = result
        self.states[task_id] = result.state
