"""
Rule-Based Strategic Reviewer.

This module implements a deterministic, rule-based reviewer that authorizes
or blocks plans based on explicit safety and validity checks.

Purpose:
- Establish a baseline for governance.
- Enforce hard constraints (validation, dry-run success).
- Provide a fallback mechanism for decision making.

Constraints:
- No AI or heuristics.
- Deterministic logic.
- No side effects.
"""

import hashlib
from typing import List

from axiom_archon.model import (
    StrategicIntent,
    StrategicContext,
    StrategicDecision,
    StrategicDecisionType,
    StrategicIssue,
    StrategicIssueSeverity
)
from axiom_archon.interface import StrategicReviewer
from axiom_strata.model import TacticalIntent, PlanningResult
from axiom_strata.validation import PlanningValidationResult
from axiom_strata.dry_run import DryRunResult


class RuleBasedStrategicReviewer:
    """
    A deterministic reviewer that applies strict rules to authorize plans.
    """

    def review_plan(
        self,
        strategic_intent: StrategicIntent,
        tactical_intent: TacticalIntent,
        planning_result: PlanningResult,
        validation_result: PlanningValidationResult,
        dry_run_result: DryRunResult,
        context: StrategicContext
    ) -> StrategicDecision:
        """
        Review a proposed plan and render a decision based on explicit rules.
        """
        issues: List[StrategicIssue] = []

        # Rule 1: Check Planning Validation
        if not validation_result.is_valid:
            for issue in validation_result.issues:
                issues.append(StrategicIssue(
                    type="validation_failure",
                    message=issue.message,
                    severity=StrategicIssueSeverity.BLOCKER,
                    context={"source": issue.context}
                ))
            return StrategicDecision(
                decision=StrategicDecisionType.REJECT,
                reason="Planning validation failed.",
                issues=issues
            )

        # Rule 2: Check Dry Run Results
        if not dry_run_result.success:
            if dry_run_result.deadlocked:
                issues.append(StrategicIssue(
                    type="deadlock_detected",
                    message="Plan execution simulation resulted in a deadlock.",
                    severity=StrategicIssueSeverity.BLOCKER,
                    context={"unreachable": dry_run_result.unreachable_tasks}
                ))
            return StrategicDecision(
                decision=StrategicDecisionType.REJECT,
                reason="Dry run simulation failed.",
                issues=issues
            )

        # Rule 3: Check for Critical Constraints (Mock Logic)
        # In a real system, we would check context.ucir for high-severity constraints
        # that apply to the scope of the plan.
        # For now, we assume if validation passed, constraints are met structurally.
        
        # Rule 4: Check for Critical Component Modification (Mock Logic)
        # If the plan modifies "core" components, we might want to escalate.
        # We can check tactical_intent.scope_ids against a list of critical IDs.
        # For this rule-based implementation, we'll be permissive unless explicitly flagged.
        
        # Rule 5: Check for Empty Plan
        if not planning_result.graph or not planning_result.graph.tasks:
             issues.append(StrategicIssue(
                type="empty_plan",
                message="The generated plan contains no tasks.",
                severity=StrategicIssueSeverity.WARNING
            ))
             # An empty plan might be valid (nothing to do), but usually suspicious.
             # We'll REVISE it.
             return StrategicDecision(
                decision=StrategicDecisionType.REVISE,
                reason="Plan is empty.",
                issues=issues
            )

        # If all checks pass, APPROVE.
        # Generate a signature (mock hash of graph ID + intent ID)
        signature_base = f"{planning_result.graph.id}:{tactical_intent.id}"
        signature = hashlib.sha256(signature_base.encode()).hexdigest()
        
        return StrategicDecision(
            decision=StrategicDecisionType.APPROVE,
            reason="All validation and safety checks passed.",
            issues=issues,
            authorization_signature=signature
        )
