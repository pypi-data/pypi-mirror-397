from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict

class NodeType(str, Enum):
    COMPONENT = "component"
    RESPONSIBILITY = "responsibility"
    DEPENDENCY = "dependency"
    CONSTRAINT = "constraint"
    INVARIANT = "invariant"
    DECISION = "decision"
    RISK = "risk"
    BUSINESS_FLOW_NODE = "business_flow_node"

@dataclass
class CPKGNode:
    """
    Represents a single node in the Canonical Project Knowledge Graph.
    
    Rules:
    - Content must be concise (<= 2 sentences).
    - Structured data preferred over prose.
    """
    id: str
    type: NodeType
    content: str
    metadata: Dict[str, str] = field(default_factory=dict)
    
@dataclass
class CPKGEdge:
    """
    Represents a relationship between two CPKG nodes.
    """
    source_id: str
    target_id: str
    relationship: str
    metadata: Dict[str, str] = field(default_factory=dict)

@dataclass
class CPKG:
    """
    The Canonical Project Knowledge Graph (CPKG).
    Primary source of truth for the project.
    """
    nodes: Dict[str, CPKGNode] = field(default_factory=dict)
    edges: List[CPKGEdge] = field(default_factory=list)
    version: str = "0.1.0"
