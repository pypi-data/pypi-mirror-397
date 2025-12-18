from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class BusinessFlowNode:
    """
    Represents a meaningful system state in a business flow.
    """
    id: str
    name: str
    description: str
    expected_outcome: str

@dataclass
class BusinessFlowTransition:
    """
    Represents a validated transition between business flow nodes.
    """
    source_id: str
    target_id: str
    trigger: str
    conditions: List[str] = field(default_factory=list)

@dataclass
class BusinessFlowMap:
    """
    The Business Flow Map (BFM).
    Models end-to-end system and user flows.
    """
    nodes: Dict[str, BusinessFlowNode] = field(default_factory=dict)
    transitions: List[BusinessFlowTransition] = field(default_factory=list)
    version: str = "0.1.0"
