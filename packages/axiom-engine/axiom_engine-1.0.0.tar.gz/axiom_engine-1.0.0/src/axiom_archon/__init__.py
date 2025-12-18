"""
Axiom Archon Package (Strategic Layer).

This package implements the Strategic Layer of Axiom.

Responsibility:
- System-wide coherence
- Logical reasoning
- Stewardship of truth (CPKG, BFM, UCIR)
- Conflict resolution
- Plan authorization (GO/NO-GO)

Constraints:
- Persistent state allowed (Knowledge Artifacts)
- Reads and updates knowledge artifacts
- Performs logical and semantic validation
- Forbidden from writing code or executing tasks directly
"""

from axiom_archon.model import (
    StrategicIntent,
    StrategicContext,
    StrategicDecision,
    StrategicDecisionType,
    StrategicIssue,
    StrategicIssueSeverity
)
from axiom_archon.interface import StrategicReviewer
from axiom_archon.rule_based_reviewer import RuleBasedStrategicReviewer
from axiom_archon.human_loop import (
    HumanDecision,
    HumanDecisionAction,
    FinalDecision,
    HumanDecisionHandler
)

__all__ = [
    "StrategicIntent",
    "StrategicContext",
    "StrategicDecision",
    "StrategicDecisionType",
    "StrategicIssue",
    "StrategicIssueSeverity",
    "StrategicReviewer",
    "RuleBasedStrategicReviewer",
    "HumanDecision",
    "HumanDecisionAction",
    "FinalDecision",
    "HumanDecisionHandler",
]
