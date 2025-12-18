"""
Dry Run Simulation.

This module provides utilities to simulate the execution of a TaskGraph
without actually running any tasks. It uses the exact same transition logic
as the Conductor to ensure the simulation is accurate.

Purpose:
- Verify that the graph is not deadlocked.
- Predict the execution order.
- Validate that all tasks are reachable.

Constraints:
- No execution.
- No side effects.
- Deterministic.
"""

from dataclasses import dataclass, field
from typing import List, Set

from axiom_canon.task_graph import TaskGraph
from axiom_canon.readiness import TaskReadinessResult, ReadinessStatus
from axiom_conductor.context import TaskExecutionContext
from axiom_conductor.model import TaskExecutionState, TaskExecutionResult
from axiom_conductor import transitions


@dataclass
class DryRunResult:
    """
    The result of a dry run simulation.
    """
    success: bool
    execution_order: List[str]  # List of task IDs in order of simulated execution
    unreachable_tasks: List[str] # Tasks that never became READY
    deadlocked: bool


def simulate_execution(graph: TaskGraph) -> DryRunResult:
    """
    Simulates the execution of a TaskGraph.
    
    Algorithm:
    1. Initialize Context.
    2. Loop until no progress:
       a. Identify READY tasks.
       b. "Execute" them (mark SUCCEEDED).
       c. Record order.
    3. Check for remaining PENDING tasks.
    """
    # Initialize Context
    # We assume the graph is structurally ready for the purpose of simulation
    readiness = TaskReadinessResult(status=ReadinessStatus.READY)
    context = TaskExecutionContext(graph, readiness)
    
    execution_order: List[str] = []
    executed_set: Set[str] = set()
    
    while True:
        # 1. Update states (PENDING -> READY/SKIPPED)
        ready_tasks = transitions.update_ready_states(context)
        
        # 2. If no tasks became ready, check if we are done
        if not ready_tasks:
            # Check if any tasks are still PENDING or RUNNING (shouldn't be RUNNING in this loop)
            pending = [
                tid for tid, state in context.states.items() 
                if state == TaskExecutionState.PENDING
            ]
            
            if not pending:
                # All done (or skipped)
                return DryRunResult(
                    success=True,
                    execution_order=execution_order,
                    unreachable_tasks=[],
                    deadlocked=False
                )
            else:
                # We have pending tasks but nothing became ready -> Deadlock
                return DryRunResult(
                    success=False,
                    execution_order=execution_order,
                    unreachable_tasks=pending,
                    deadlocked=True
                )
        
        # 3. "Execute" the ready tasks
        # Sort for deterministic simulation order
        ready_tasks.sort()
        
        for task_id in ready_tasks:
            # Mark as RUNNING (transition logic expects this flow usually, though update_ready_states handles PENDING)
            context.set_state(task_id, TaskExecutionState.RUNNING)
            execution_order.append(task_id)
            executed_set.add(task_id)
            
            # Simulate Success
            # We don't need a full result object for transitions to work, 
            # just the state change to SUCCEEDED.
            context.set_state(task_id, TaskExecutionState.SUCCEEDED)
            
            # Note: In a real execution, we'd set a result. 
            # transitions.is_task_ready checks context.get_state(uid) == SUCCEEDED.
            # So setting state is sufficient.
