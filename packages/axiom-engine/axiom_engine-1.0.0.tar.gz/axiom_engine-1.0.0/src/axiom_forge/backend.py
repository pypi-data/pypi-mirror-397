"""
Axiom Forge Backend Interface.

This module defines the interface for execution backends.
Axiom-Conductor (the scheduler) uses this interface to delegate the actual
performance of work to Axiom-Forge (the executor).

Architecture:
- Conductor: Decides WHEN to run a task.
- Forge: Decides HOW to run a task.

This separation allows Axiom to support multiple execution environments
(e.g., local shell, Docker container, remote worker, simulation) without
changing the scheduling logic.
"""

from typing import Protocol, Dict, List, Optional, Any
from dataclasses import dataclass, field

from axiom_conductor.model import TaskExecutionResult


@dataclass
class TaskExecutionInput:
    """
    The input required to execute a single task.
    
    This structure isolates the backend from the full TaskNode definition,
    ensuring that backends only receive what they need to perform the work.
    """
    task_id: str
    command: str
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    working_directory: Optional[str] = None
    timeout_seconds: int = 300
    metadata: Dict[str, Any] = field(default_factory=dict)


class TaskExecutionBackend(Protocol):
    """
    Protocol for task execution backends.
    
    A backend is responsible for:
    1. Accepting a task definition.
    2. Performing the work (or simulating it).
    3. Returning a deterministic result.
    
    A backend MUST NOT:
    - Manage dependencies.
    - Decide execution order.
    - Modify the Task Graph.
    """
    
    def execute_task(self, input_data: TaskExecutionInput) -> TaskExecutionResult:
        """
        Execute a single task and return the result.
        
        Args:
            input_data: The task execution details.
            
        Returns:
            TaskExecutionResult: The outcome of the execution.
        """
        ...
