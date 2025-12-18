"""
Deterministic Task Executor.

This module implements the scheduling loop for Axiom.
It separates the "when" (scheduling) from the "how" (strategy).

Responsibilities:
- Drive the execution loop.
- Apply state transitions.
- Emit events.
- Delegate actual "work" to an ExecutionStrategy.

Constraints:
- No side effects in the loop itself.
- Deterministic ordering of operations.
- Synchronous execution (for now).
"""

from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone

from axiom_canon.task_graph import TaskNode
from axiom_conductor.context import TaskExecutionContext
from axiom_conductor.model import (
    TaskExecutionState,
    TaskExecutionResult,
    TaskFailureReason,
    ExecutionEvent
)
from axiom_conductor.interface import TaskExecutor
from axiom_conductor import transitions
from axiom_conductor import events
from axiom_forge.backend import TaskExecutionBackend, TaskExecutionInput


class DeterministicTaskExecutor:
    """
    A concrete implementation of TaskExecutor that runs a synchronous,
    deterministic scheduling loop.
    """

    def __init__(self, backend: TaskExecutionBackend):
        self.backend = backend
        self._events: List[ExecutionEvent] = []

    def initialize(self, context: TaskExecutionContext) -> None:
        """
        Prepare context and identify initial ready tasks.
        """
        self._events.append(events.execution_started(context.graph.id))
        
        # Initial transition pass to catch any tasks that start ready (no deps)
        ready_tasks = transitions.update_ready_states(context)
        for tid in ready_tasks:
            self._events.append(events.task_ready(tid))

    def step(self, context: TaskExecutionContext) -> List[ExecutionEvent]:
        """
        Perform one cycle of the execution loop.
        1. Identify READY tasks.
        2. Execute them (via strategy).
        3. Update states.
        4. Update downstream dependencies.
        """
        step_events = []
        
        # 1. Identify READY tasks
        # We scan the context for tasks that are currently READY.
        # transitions.update_ready_states() handles PENDING -> READY.
        # But we also need to pick up tasks that ARE ready.
        
        ready_tasks = [
            tid for tid, state in context.states.items()
            if state == TaskExecutionState.READY
        ]
        
        if not ready_tasks:
            # If no tasks are ready, check if we have any PENDING tasks left.
            # If yes, and nothing is ready, we might be stuck (deadlock or waiting).
            # But transitions.update_ready_states handles skipping blocked tasks.
            # So if we are here, either everything is done, or we are waiting for something external (not possible in this sync model).
            
            # Let's run update_ready_states one more time to be sure we didn't miss transitions
            # triggered by previous steps.
            newly_ready = transitions.update_ready_states(context)
            for tid in newly_ready:
                step_events.append(events.task_ready(tid))
            
            if newly_ready:
                # If we found new work, return events and let the next step handle execution.
                self._events.extend(step_events)
                return step_events
            
            return []

        # 2. Execute READY tasks
        # In a real system, this might be parallel. Here it is sequential and deterministic.
        # We sort by ID to ensure deterministic order of execution.
        ready_tasks.sort()
        
        for task_id in ready_tasks:
            task = context.graph.tasks[task_id]
            
            # Transition to RUNNING
            context.set_state(task_id, TaskExecutionState.RUNNING)
            step_events.append(events.task_started(task_id))
            
            # Prepare input for backend
            input_data = TaskExecutionInput(
                task_id=task.id,
                command=task.command or "",
                args=task.args,
                env=task.env,
                timeout_seconds=task.timeout_seconds,
                metadata=context.graph.metadata
            )

            # Execute via backend
            result = self.backend.execute_task(input_data)
            
            # Update Context
            context.set_result(task_id, result)
            
            # Emit completion event
            if result.state == TaskExecutionState.SUCCEEDED:
                step_events.append(events.task_completed(task_id, result.exit_code or 0))
            else:
                step_events.append(events.task_failed(task_id, result.failure_reason or TaskFailureReason.UNKNOWN, result.error_message or ""))
                
        # 3. Update downstream states
        # Now that some tasks finished, others might become READY or SKIPPED.
        newly_ready = transitions.update_ready_states(context)
        for tid in newly_ready:
            step_events.append(events.task_ready(tid))
            
        # Also check for SKIPPED tasks (transitions.update_ready_states handles this internally,
        # but we might want to emit events for them).
        # We can scan for tasks that transitioned to SKIPPED in this step.
        # Ideally, transitions.update_ready_states would return skipped tasks too.
        # For now, we can just scan context for SKIPPED tasks that don't have a result/event yet?
        # Or better, let's rely on the fact that we only care about events.
        # Let's iterate context to find SKIPPED tasks that we haven't emitted events for?
        # That requires tracking emitted events.
        # Alternatively, we can just trust the loop.
        
        # Optimization: Check for skipped tasks to emit events
        # This is a bit inefficient but safe.
        for tid, state in context.states.items():
            if state == TaskExecutionState.SKIPPED:
                # We need a way to know if we just skipped it.
                # For this simple implementation, we won't emit skipped events here to avoid duplicates
                # without extra tracking. In a full impl, transitions would return changes.
                pass

        self._events.extend(step_events)
        return step_events

    def run(self, context: TaskExecutionContext) -> None:
        """
        Run until completion.
        """
        self.initialize(context)
        
        while True:
            step_events = self.step(context)
            if not step_events:
                # No events generated means no progress made.
                # Check if we are done.
                pending = [t for t, s in context.states.items() if s in (TaskExecutionState.PENDING, TaskExecutionState.READY, TaskExecutionState.RUNNING)]
                if not pending:
                    self._events.append(events.execution_finished(context.graph.id, "success"))
                    break
                else:
                    # We have pending tasks but made no progress. Deadlock or failure propagation incomplete?
                    # In this simple model, if we have pending tasks but step() did nothing,
                    # it means they are blocked by something that didn't resolve.
                    # This shouldn't happen if skip logic is correct.
                    self._events.append(events.execution_finished(context.graph.id, "stalled"))
                    break
