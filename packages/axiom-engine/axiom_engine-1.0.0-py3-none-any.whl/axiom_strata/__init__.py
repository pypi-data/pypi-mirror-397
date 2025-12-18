"""
Axiom Strata Package (Tactical Layer).

This package implements the Tactical Layer of Axiom.

Responsibility:
- Convert strategic intent into plans
- Decompose work into Task Graphs
- Define validation strategies
- Summarize outcomes upward

Constraints:
- Stateless or short-lived
- Produces structured plans
- Forbidden from executing tasks
- NEVER write files
- NEVER execute tasks directly
- NEVER call Copilot or tools directly
"""

from axiom_strata.model import (
    TacticalIntent,
    PlanningContext,
    PlanningResult,
    PlanningIssue,
    PlanningIssueType
)
from axiom_strata.interface import TacticalPlanner
from axiom_strata.rule_based_planner import RuleBasedTacticalPlanner
from axiom_strata.validation import (
    PlanningValidationResult,
    PlanningValidationIssue,
    validate_planning_result
)
from axiom_strata.dry_run import (
    DryRunResult,
    simulate_execution
)
from axiom_strata.llm_tactical_planner import (
    LLMTacticalPlanner,
    LLMPlanningInput,
    LLMPlanningOutput,
    LLMPlanningHints,
    PlanningExplanation,
    LLMConfidenceLevel,
    LLMBackend,
    MockLLMBackend,
    LLMUnavailableError,
)

__all__ = [
    "TacticalIntent",
    "PlanningContext",
    "PlanningResult",
    "PlanningIssue",
    "PlanningIssueType",
    "TacticalPlanner",
    "RuleBasedTacticalPlanner",
    "PlanningValidationResult",
    "PlanningValidationIssue",
    "validate_planning_result",
    "DryRunResult",
    "simulate_execution",
    # LLM-backed planning (advisory only)
    "LLMTacticalPlanner",
    "LLMPlanningInput",
    "LLMPlanningOutput",
    "LLMPlanningHints",
    "PlanningExplanation",
    "LLMConfidenceLevel",
    "LLMBackend",
    "MockLLMBackend",
    "LLMUnavailableError",
]
