"""
Strategic Data Models.

This module defines the data structures used by the Strategic Layer (Axiom-Archon)
to reason about plans, risks, and alignment.

Responsibilities:
- Define high-level goals (StrategicIntent).
- Define the context for strategic reasoning (StrategicContext).
- Define the outcomes of strategic review (StrategicDecision).
- Define risks and issues (StrategicIssue).

Constraints:
- Pure data models.
- No logic.
- Must reference lower-layer artifacts for evidence.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional

from axiom_canon.cpkg import CPKG
from axiom_canon.ucir import UCIR
from axiom_canon.bfm import BusinessFlowMap as BFM
from axiom_strata.model import TacticalIntent, PlanningResult
from axiom_strata.validation import PlanningValidationResult
from axiom_strata.dry_run import DryRunResult


@dataclass
class StrategicIntent:
    """
    Represents a high-level goal or directive.
    
    Unlike TacticalIntent, which is scoped and specific, StrategicIntent
    captures the "why" and the ultimate success criteria.
    """
    id: str
    description: str
    success_criteria: List[str]
    priority: int = 1  # 1 (High) to 5 (Low)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StrategicContext:
    """
    The context available to a StrategicReviewer.
    
    It aggregates all necessary information to make a GO/NO-GO decision.
    """
    cpkg: CPKG
    ucir: UCIR
    bfm: BFM
    history: List[str] = field(default_factory=list)  # IDs of past decisions


class StrategicDecisionType(str, Enum):
    """
    The verdict of a strategic review.
    """
    APPROVE = "approve"       # Plan is safe and aligned. Proceed to execution.
    REVISE = "revise"         # Plan has issues but is fixable. Send back to Strata.
    REJECT = "reject"         # Plan is fundamentally flawed or dangerous. Stop.
    ESCALATE = "escalate"     # Decision requires human intervention.


class StrategicIssueSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    RISK = "risk"             # Potential future problem
    BLOCKER = "blocker"       # Immediate prevention of approval


@dataclass
class StrategicIssue:
    """
    Represents a risk, uncertainty, or tradeoff identified during review.
    """
    type: str  # e.g., "security_risk", "alignment_gap", "resource_usage"
    message: str
    severity: StrategicIssueSeverity
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StrategicDecision:
    """
    The authoritative output of the Strategic Layer.
    
    This object determines whether the Conductor is allowed to execute the plan.
    """
    decision: StrategicDecisionType
    reason: str
    issues: List[StrategicIssue] = field(default_factory=list)
    
    # If APPROVED, this signature authorizes execution.
    # In a real system, this might be a cryptographic hash of the plan.
    authorization_signature: Optional[str] = None
    
    @property
    def is_approved(self) -> bool:
        return self.decision == StrategicDecisionType.APPROVE
