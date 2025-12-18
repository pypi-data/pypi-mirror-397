"""
Tactical Planning Data Models.

This module defines the data structures used by the Tactical Layer (Axiom-Strata)
to convert intent into executable plans.

Responsibilities:
- Define what needs to be done (TacticalIntent).
- Define the context available for planning (PlanningContext).
- Define the output of the planning process (PlanningResult).
- Define planning errors and issues.

Constraints:
- Pure data models.
- No logic.
- Must reference Canon artifacts (CPKG, UCIR, BFM) for context.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any

from axiom_canon.task_graph import TaskGraph
from axiom_canon.cpkg import CPKG
from axiom_canon.ucir import UCIR
from axiom_canon.bfm import BusinessFlowMap as BFM


@dataclass
class TacticalIntent:
    """
    Represents a scoped request for work to be done.
    
    Unlike a high-level goal, TacticalIntent is specific enough to be
    decomposed into a TaskGraph. It focuses on "what", not "how".
    """
    id: str
    description: str
    
    # The specific CPKG nodes that are the subject of this intent.
    # e.g., "Refactor module X", "Add test to function Y".
    scope_ids: List[str] = field(default_factory=list)
    
    # Specific constraints or requirements for this intent.
    # These might be references to UCIR constraints or ad-hoc requirements.
    constraints: List[str] = field(default_factory=list)
    
    # Additional metadata for the planner.
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlanningContext:
    """
    The context available to a TacticalPlanner.
    
    It provides access to the persistent knowledge artifacts required
    to make informed planning decisions.
    """
    cpkg: CPKG
    ucir: UCIR
    bfm: BFM
    
    # The root directory of the project being modified.
    project_root: str


class PlanningIssueType(str, Enum):
    """
    Categorizes issues encountered during planning.
    """
    AMBIGUOUS_INTENT = "ambiguous_intent"       # Intent is too vague to plan
    CONSTRAINT_CONFLICT = "constraint_conflict" # Intent violates UCIR
    MISSING_DEPENDENCY = "missing_dependency"   # Required CPKG node missing
    UNSUPPORTED_OPERATION = "unsupported_operation" # Planner cannot handle request
    STRUCTURAL_ERROR = "structural_error"       # Generated graph would be invalid


@dataclass
class PlanningIssue:
    """
    Represents a problem encountered during planning.
    """
    type: PlanningIssueType
    message: str
    severity: str  # "error" or "warning"
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlanningResult:
    """
    The output of a planning operation.
    """
    # The generated plan (TaskGraph). None if planning failed completely.
    graph: Optional[TaskGraph]
    
    # Issues encountered during planning.
    issues: List[PlanningIssue] = field(default_factory=list)
    
    @property
    def success(self) -> bool:
        """
        Returns True if a graph was generated and there are no error-level issues.
        """
        has_errors = any(i.severity == "error" for i in self.issues)
        return self.graph is not None and not has_errors
