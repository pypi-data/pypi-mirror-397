"""
Strategic Reviewer Interface.

This module defines the protocol for Strategic Reviewers.
A Strategic Reviewer is responsible for evaluating a proposed plan against
strategic goals, constraints, and safety requirements.

Responsibilities:
- Evaluate alignment between TacticalIntent and StrategicIntent.
- Assess risks based on PlanningResult and ValidationResult.
- Verify safety based on DryRunResult.
- Issue a binding StrategicDecision.

Constraints:
- Must NOT modify the plan.
- Must NOT execute the plan.
- Must be deterministic given the same inputs.
"""

from typing import Protocol

from axiom_archon.model import (
    StrategicIntent,
    StrategicContext,
    StrategicDecision
)
from axiom_strata.model import TacticalIntent, PlanningResult
from axiom_strata.validation import PlanningValidationResult
from axiom_strata.dry_run import DryRunResult


class StrategicReviewer(Protocol):
    """
    Protocol for components that authorize or reject plans.
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
        Review a proposed plan and render a decision.
        
        Args:
            strategic_intent: The high-level goal.
            tactical_intent: The specific intent that generated the plan.
            planning_result: The output from the planner (TaskGraph).
            validation_result: The output from the validator.
            dry_run_result: The output from the simulation.
            context: The strategic context (knowledge artifacts).
            
        Returns:
            StrategicDecision: The binding decision (APPROVE/REJECT/etc).
        """
        ...
