from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict

class ConstraintLevel(str, Enum):
    CRITICAL = "critical"  # Must never be violated
    WARNING = "warning"    # Should be avoided, but can be overridden with justification
    INFO = "info"          # Informational guideline

@dataclass
class UserConstraint:
    """
    A persistent user-defined constraint.
    """
    id: str
    description: str
    level: ConstraintLevel
    scope: str  # e.g., "global", "frontend", "api"
    source: str # e.g., "user_prompt", "architecture_doc"

@dataclass
class UCIR:
    """
    User Constraint & Instruction Registry (UCIR).
    Stores persistent user-defined constraints.
    """
    constraints: Dict[str, UserConstraint] = field(default_factory=dict)
    version: str = "0.1.0"
