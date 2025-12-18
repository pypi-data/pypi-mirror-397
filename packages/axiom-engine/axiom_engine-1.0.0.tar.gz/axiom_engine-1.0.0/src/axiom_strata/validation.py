"""
Planning Validation Utilities.

This module provides validation logic for PlanningResults produced by TacticalPlanners.
It ensures that the generated TaskGraph is structurally sound, executable, and
compliant with constraints before it is handed off to the Conductor.

Responsibilities:
- Validate structural integrity of the plan.
- Check readiness (executability) of the plan.
- Ensure no critical planning issues were ignored.

Constraints:
- Pure functions.
- No execution.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from axiom_canon.readiness import evaluate_task_graph_readiness, ReadinessStatus
from axiom_strata.model import PlanningResult, PlanningIssue, PlanningIssueType


@dataclass
class PlanningValidationIssue:
    """
    An issue found during validation of a plan.
    """
    message: str
    severity: str  # "error" or "warning"
    context: str  # e.g., "readiness", "structure"


@dataclass
class PlanningValidationResult:
    """
    The result of validating a PlanningResult.
    """
    is_valid: bool
    issues: List[PlanningValidationIssue] = field(default_factory=list)


def validate_planning_result(result: PlanningResult) -> PlanningValidationResult:
    """
    Validates a PlanningResult.
    
    Checks:
    1. Did planning succeed (graph exists)?
    2. Are there any critical planning issues?
    3. Is the generated graph ready for execution (Canon readiness)?
    """
    issues: List[PlanningValidationIssue] = []
    
    # 1. Check if planning produced a graph
    if not result.graph:
        # If no graph, check if we have errors explaining why
        has_errors = any(i.severity == "error" for i in result.issues)
        if has_errors:
            return PlanningValidationResult(is_valid=False, issues=[
                PlanningValidationIssue(
                    message="Planning failed to produce a graph due to errors.",
                    severity="error",
                    context="planning"
                )
            ])
        else:
            return PlanningValidationResult(is_valid=False, issues=[
                PlanningValidationIssue(
                    message="Planning produced no graph and no errors (ambiguous state).",
                    severity="error",
                    context="planning"
                )
            ])

    # 2. Check for critical planning issues in the result itself
    for issue in result.issues:
        if issue.severity == "error":
            issues.append(PlanningValidationIssue(
                message=f"Planner reported error: {issue.message}",
                severity="error",
                context="planner_output"
            ))

    # 3. Check Readiness (Canon)
    # We don't pass CPKG/UCIR here for now as the planner should have already used them,
    # but strictly speaking we should re-verify. For this step, we check structural readiness.
    readiness = evaluate_task_graph_readiness(result.graph)
    
    if readiness.status != ReadinessStatus.READY:
        for issue in readiness.issues:
            issues.append(PlanningValidationIssue(
                message=f"Readiness check failed: {issue.message}",
                severity=issue.severity,
                context="readiness"
            ))

    # Determine validity
    is_valid = not any(i.severity == "error" for i in issues)
    
    return PlanningValidationResult(is_valid=is_valid, issues=issues)
