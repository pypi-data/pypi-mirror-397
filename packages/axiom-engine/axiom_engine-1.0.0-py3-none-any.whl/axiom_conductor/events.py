"""
Execution Events for Axiom Conductor.

This module defines factory functions for creating structured execution events.
These events provide visibility into the state machine's progress.

Responsibilities:
- Standardize event types and payloads.
- Ensure consistent timestamping (though actual time is injected).

Constraints:
- Pure data creation.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from axiom_conductor.model import ExecutionEvent, TaskExecutionState, TaskFailureReason


def _now() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def task_ready(task_id: str) -> ExecutionEvent:
    return ExecutionEvent(
        event_type="task_ready",
        task_id=task_id,
        timestamp=_now(),
        payload={}
    )


def task_started(task_id: str) -> ExecutionEvent:
    return ExecutionEvent(
        event_type="task_started",
        task_id=task_id,
        timestamp=_now(),
        payload={}
    )


def task_completed(task_id: str, exit_code: int = 0) -> ExecutionEvent:
    return ExecutionEvent(
        event_type="task_completed",
        task_id=task_id,
        timestamp=_now(),
        payload={"exit_code": exit_code}
    )


def task_failed(task_id: str, reason: TaskFailureReason, message: str) -> ExecutionEvent:
    return ExecutionEvent(
        event_type="task_failed",
        task_id=task_id,
        timestamp=_now(),
        payload={"reason": reason, "message": message}
    )


def task_skipped(task_id: str, reason: str) -> ExecutionEvent:
    return ExecutionEvent(
        event_type="task_skipped",
        task_id=task_id,
        timestamp=_now(),
        payload={"reason": reason}
    )


def execution_started(graph_id: str) -> ExecutionEvent:
    return ExecutionEvent(
        event_type="execution_started",
        task_id=None,
        timestamp=_now(),
        payload={"graph_id": graph_id}
    )


def execution_finished(graph_id: str, status: str) -> ExecutionEvent:
    return ExecutionEvent(
        event_type="execution_finished",
        task_id=None,
        timestamp=_now(),
        payload={"graph_id": graph_id, "status": status}
    )
