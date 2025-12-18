"""
State Transition Logic for Axiom Conductor.

This module implements the deterministic rules for advancing task states.

Rules:
- A task is READY if all its upstream dependencies are SUCCEEDED.
- A task is SKIPPED if any upstream dependency is FAILED or SKIPPED.
- A task transitions from READY to RUNNING when picked up by the executor.
- A task transitions from RUNNING to SUCCEEDED or FAILED based on execution result.

Constraints:
- Pure functions.
- No side effects.
- Operates on TaskExecutionContext.
"""

from typing import List, Set
from axiom_conductor.context import TaskExecutionContext
from axiom_conductor.model import TaskExecutionState


def get_upstream_dependencies(context: TaskExecutionContext, task_id: str) -> List[str]:
    """
    Get IDs of all tasks that the given task depends on.
    """
    deps = []
    for dep in context.graph.dependencies:
        if dep.downstream_task_id == task_id:
            deps.append(dep.upstream_task_id)
    return deps


def get_downstream_dependents(context: TaskExecutionContext, task_id: str) -> List[str]:
    """
    Get IDs of all tasks that depend on the given task.
    """
    deps = []
    for dep in context.graph.dependencies:
        if dep.upstream_task_id == task_id:
            deps.append(dep.downstream_task_id)
    return deps


def is_task_ready(context: TaskExecutionContext, task_id: str) -> bool:
    """
    Check if a task is ready to run (all dependencies SUCCEEDED).
    """
    # If already executed or running, not ready (it's beyond ready)
    current_state = context.get_state(task_id)
    if current_state != TaskExecutionState.PENDING:
        return False

    upstream_ids = get_upstream_dependencies(context, task_id)
    for uid in upstream_ids:
        if context.get_state(uid) != TaskExecutionState.SUCCEEDED:
            return False
    
    return True


def should_skip_task(context: TaskExecutionContext, task_id: str) -> bool:
    """
    Check if a task should be skipped (any dependency FAILED or SKIPPED).
    """
    current_state = context.get_state(task_id)
    if current_state != TaskExecutionState.PENDING:
        return False

    upstream_ids = get_upstream_dependencies(context, task_id)
    for uid in upstream_ids:
        state = context.get_state(uid)
        if state in (TaskExecutionState.FAILED, TaskExecutionState.SKIPPED):
            return True
            
    return False


def update_ready_states(context: TaskExecutionContext) -> List[str]:
    """
    Scan PENDING tasks and transition them to READY or SKIPPED based on dependencies.
    Returns a list of task IDs that transitioned to READY.
    """
    ready_tasks = []
    
    # We iterate over all tasks. In a large graph, we might optimize this,
    # but for now, correctness is key.
    # We only care about PENDING tasks.
    pending_tasks = [
        tid for tid, state in context.states.items() 
        if state == TaskExecutionState.PENDING
    ]
    
    for task_id in pending_tasks:
        if should_skip_task(context, task_id):
            context.set_state(task_id, TaskExecutionState.SKIPPED)
            # If we skip a task, we might need to propagate that skip immediately
            # or wait for the next cycle. For simplicity, we let the next cycle handle downstream.
        elif is_task_ready(context, task_id):
            context.set_state(task_id, TaskExecutionState.READY)
            ready_tasks.append(task_id)
            
    return ready_tasks
