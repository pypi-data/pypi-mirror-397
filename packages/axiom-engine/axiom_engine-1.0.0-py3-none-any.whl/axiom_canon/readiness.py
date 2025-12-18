"""
Task Graph Readiness Evaluation Utilities.

This module determines whether a Task Graph is safe and complete enough
to be handed to the Task Executor.

Readiness vs Validation:
- Validation checks structural integrity (DAG properties, schema types).
- Readiness checks semantic executability (dependencies exist, constraints met, context valid).

Responsibilities:
- Verify all tasks have executable commands or are valid placeholders.
- Check alignment with UCIR constraints.
- Verify that referenced artifacts (in metadata) exist in the CPKG.
- Ensure no "blocked" or "invalid" states exist before execution.

Constraints:
- Pure functions only.
- NO execution.
- NO auto-fixing.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any

from axiom_canon.task_graph import TaskGraph, TaskNode
from axiom_canon.cpkg import CPKG
from axiom_canon.ucir import UCIR, ConstraintLevel
from axiom_canon.validation import validate_task_graph


class ReadinessStatus(str, Enum):
    READY = "ready"
    BLOCKED = "blocked"
    INVALID = "invalid"


@dataclass
class ReadinessIssue:
    """
    Represents a specific reason why a graph is not ready.
    """
    message: str
    severity: str  # "error" (blocks execution) or "warning" (advisory)
    task_id: Optional[str] = None
    constraint_id: Optional[str] = None


@dataclass
class TaskReadinessResult:
    """
    The result of a readiness evaluation.
    """
    status: ReadinessStatus
    issues: List[ReadinessIssue] = field(default_factory=list)
    
    @property
    def is_executable(self) -> bool:
        return self.status == ReadinessStatus.READY


def evaluate_task_graph_readiness(
    graph: TaskGraph,
    cpkg: Optional[CPKG] = None,
    ucir: Optional[UCIR] = None
) -> TaskReadinessResult:
    """
    Evaluates if a Task Graph is ready for execution.
    
    Checks:
    1. Structural Validation (via validation.py)
    2. Task Completeness (commands exist)
    3. Context Validity (referenced components exist in CPKG)
    4. Constraint Compliance (UCIR)
    """
    issues: List[ReadinessIssue] = []
    
    # 1. Structural Validation
    validation_result = validate_task_graph(graph)
    if not validation_result.is_valid:
        for error in validation_result.errors:
            issues.append(ReadinessIssue(
                message=f"Structural validation failed: {error.message}",
                severity="error",
                task_id=error.entity_id
            ))
        return TaskReadinessResult(status=ReadinessStatus.INVALID, issues=issues)

    # 2. Task Completeness
    for task_id, task in graph.tasks.items():
        # A task must have a command unless it's purely structural (which we might allow, 
        # but usually a task without a command does nothing).
        # For now, we'll warn if command is missing, or error if strict.
        # Let's assume tasks MUST have a command to be executable.
        if not task.command:
            issues.append(ReadinessIssue(
                message="Task has no executable command",
                severity="error",
                task_id=task_id
            ))
            
        # Check for empty args if command expects them? (Hard to know without logic)
        # We can check if env vars are strings.
        for k, v in task.env.items():
            if not isinstance(v, str):
                 issues.append(ReadinessIssue(
                    message=f"Environment variable {k} is not a string",
                    severity="error",
                    task_id=task_id
                ))

    # 3. Context Validity (CPKG)
    if cpkg:
        # Check if graph metadata references a valid component
        related_component = graph.metadata.get("related_component_id")
        if related_component:
            if related_component not in cpkg.nodes:
                issues.append(ReadinessIssue(
                    message=f"Graph references unknown component '{related_component}'",
                    severity="error"
                ))
        
        # If tasks reference components in their env/metadata (convention), check them.
        # Example convention: env["AXIOM_COMPONENT_ID"]
        for task_id, task in graph.tasks.items():
            comp_ref = task.env.get("AXIOM_COMPONENT_ID")
            if comp_ref and comp_ref not in cpkg.nodes:
                 issues.append(ReadinessIssue(
                    message=f"Task references unknown component '{comp_ref}' in env",
                    severity="error",
                    task_id=task_id
                ))

    # 4. Constraint Compliance (UCIR)
    if ucir:
        # Check for global critical constraints that might block ALL execution
        # This is a heuristic: if there's a critical constraint saying "NO_EXECUTION", we block.
        # In reality, we'd need semantic matching, but here we can check for explicit flags
        # or just ensure we acknowledge them.
        
        # For this implementation, we will check if any task violates a "blocked" keyword
        # in a critical constraint (simple keyword matching as a placeholder for semantic checks).
        
        critical_constraints = [c for c in ucir.constraints.values() if c.level == ConstraintLevel.CRITICAL]
        
        for constraint in critical_constraints:
            # Heuristic: If a constraint explicitly mentions a task ID (unlikely but possible)
            # or if we had a way to link tasks to constraints.
            # For now, we'll just pass, as we can't semantically validate "Does this bash command violate constraint X?"
            # without an LLM or complex logic.
            pass

    # Determine Status
    has_errors = any(i.severity == "error" for i in issues)
    status = ReadinessStatus.INVALID if has_errors else ReadinessStatus.READY
    
    # If there are warnings but no errors, it's READY (but maybe with caveats)
    # If there are blocking issues (like missing dependencies handled in validation), it's INVALID.
    # We could use BLOCKED if it's valid but waiting on external factors, but here we check static readiness.
    
    return TaskReadinessResult(status=status, issues=issues)
