"""
Axiom Core Package.

This package contains shared utilities, base classes, and core infrastructure
for the Axiom platform.

Responsibility:
- Logging configuration
- Error handling primitives
- Base configuration management
- Workflow orchestration
- Human decision intake API
"""

from axiom_core.workflow import AxiomWorkflow, WorkflowResult
from axiom_core.human_decision_intake import (
    HumanDecisionIntake,
    HumanDecisionResult,
    ExecutionAuthorizationResult,
    DecisionStatus,
    ApprovalGrammarAction,
    GrammarViolation,
    GrammarViolationType,
    ParsedApproval,
    parse_approval_grammar,
    record_human_decision,
    get_default_intake,
)

__all__ = [
    # Workflow
    "AxiomWorkflow",
    "WorkflowResult",
    # Human Decision Intake
    "HumanDecisionIntake",
    "HumanDecisionResult",
    "ExecutionAuthorizationResult",
    "DecisionStatus",
    "ApprovalGrammarAction",
    "GrammarViolation",
    "GrammarViolationType",
    "ParsedApproval",
    "parse_approval_grammar",
    "record_human_decision",
    "get_default_intake",
]
