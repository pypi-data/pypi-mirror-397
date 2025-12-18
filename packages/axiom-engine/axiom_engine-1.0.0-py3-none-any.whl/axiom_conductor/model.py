"""
Execution Data Models for Axiom Conductor.

This module defines the core data structures used to track and manage
the execution of tasks. These structures are distinct from the canonical
TaskGraph schema because they represent *runtime* state, not *planned* state.

Responsibilities:
- Define execution states (PENDING, READY, RUNNING, etc.)
- Define result structures and failure reasons.
- Define execution events/signals.

Constraints:
- Pure data models.
- No logic.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional, List
from datetime import datetime


class TaskExecutionState(str, Enum):
    """
    Represents the runtime state of a task.
    
    States:
    - PENDING: Waiting for dependencies to complete.
    - READY: Dependencies satisfied, eligible for execution.
    - RUNNING: Currently executing.
    - SUCCEEDED: Completed successfully.
    - FAILED: Execution failed.
    - SKIPPED: Not executed (e.g., due to upstream failure).
    """
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskFailureReason(str, Enum):
    """
    Categorizes why a task failed.
    """
    COMMAND_ERROR = "command_error"       # Non-zero exit code
    TIMEOUT = "timeout"                   # Execution exceeded time limit
    DEPENDENCY_FAILED = "dependency_failed" # Upstream task failed
    PRECONDITION_FAILED = "precondition_failed" # Readiness check failed
    SYSTEM_ERROR = "system_error"         # Internal executor error
    UNKNOWN = "unknown"


@dataclass
class TaskExecutionResult:
    """
    The outcome of a single task execution attempt.
    """
    task_id: str
    state: TaskExecutionState
    exit_code: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    failure_reason: Optional[TaskFailureReason] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: Optional[str] = None  # ISO 8601


@dataclass
class ExecutionEvent:
    """
    A structured signal emitted during execution.
    Used for logging, monitoring, and UI updates.
    """
    event_type: str  # e.g., "task_started", "task_completed"
    task_id: Optional[str]
    timestamp: str
    payload: Dict[str, Any] = field(default_factory=dict)
