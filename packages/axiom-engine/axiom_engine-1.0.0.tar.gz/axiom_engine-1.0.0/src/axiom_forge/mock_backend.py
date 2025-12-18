"""
Mock Execution Backend for Axiom Forge.

This module provides a deterministic mock backend for testing Axiom-Conductor.
It allows simulating various execution scenarios (success, failure, timeouts)
without running actual shell commands.
"""

from typing import Dict, Set, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone

from axiom_conductor.model import (
    TaskExecutionResult,
    TaskExecutionState,
    TaskFailureReason
)
from axiom_forge.backend import TaskExecutionBackend, TaskExecutionInput


@dataclass
class MockExecutionBackend:
    """
    A deterministic mock backend for testing.
    
    Attributes:
        default_success (bool): Whether tasks succeed by default.
        failures (Set[str]): Set of task IDs that should fail.
        custom_results (Dict[str, TaskExecutionResult]): Pre-canned results for specific tasks.
    """
    default_success: bool = True
    failures: Set[str] = field(default_factory=set)
    custom_results: Dict[str, TaskExecutionResult] = field(default_factory=dict)

    def execute_task(self, input_data: TaskExecutionInput) -> TaskExecutionResult:
        """
        Simulate executing a task.
        """
        task_id = input_data.task_id
        timestamp = datetime.now(timezone.utc).isoformat()

        # 1. Check for pre-canned result
        if task_id in self.custom_results:
            result = self.custom_results[task_id]
            # Ensure the result has the correct task_id if not set
            if result.task_id != task_id:
                # We return a copy with the correct ID to avoid mutating the template
                return TaskExecutionResult(
                    task_id=task_id,
                    state=result.state,
                    exit_code=result.exit_code,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    failure_reason=result.failure_reason,
                    error_message=result.error_message,
                    metadata=result.metadata,
                    timestamp=timestamp
                )
            return result

        # 2. Check for configured failure
        if task_id in self.failures:
            return TaskExecutionResult(
                task_id=task_id,
                state=TaskExecutionState.FAILED,
                failure_reason=TaskFailureReason.COMMAND_ERROR,
                error_message=f"Simulated failure for task {task_id}",
                exit_code=1,
                timestamp=timestamp
            )

        # 3. Default behavior
        if self.default_success:
            return TaskExecutionResult(
                task_id=task_id,
                state=TaskExecutionState.SUCCEEDED,
                exit_code=0,
                stdout=f"Simulated success for task {task_id}\nCommand: {input_data.command}",
                timestamp=timestamp
            )
        else:
            return TaskExecutionResult(
                task_id=task_id,
                state=TaskExecutionState.FAILED,
                failure_reason=TaskFailureReason.UNKNOWN,
                error_message="Default simulated failure",
                exit_code=1,
                timestamp=timestamp
            )
