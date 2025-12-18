"""
Read-Only Query Utilities for Axiom Knowledge Artifacts.

This module provides capability-scoped, read-only access to knowledge artifacts.
It allows higher layers (Strategic, Tactical) to retrieve structured views of
the system truth without mutating data or loading the entire context.

Why Read-Only Queries?
- Context Efficiency: Agents should only load what they need.
- Safety: Prevents accidental mutation during retrieval.
- Intent: Queries express *what* is needed, not *how* to traverse.

Responsibilities:
- Filter nodes and edges by criteria.
- Traverse graph structures to find neighbors/dependencies.
- Aggregate constraints by scope or level.

Constraints:
- Pure functions only.
- NO mutation.
- NO reasoning or inference (return explicit data only).
- NO free-form text generation.
"""

from typing import List, Dict, Set, Optional, Any, Tuple

from axiom_canon.cpkg import CPKG, CPKGNode, CPKGEdge, NodeType
from axiom_canon.bfm import BusinessFlowMap, BusinessFlowTransition, BusinessFlowNode
from axiom_canon.ucir import UCIR, UserConstraint, ConstraintLevel


# --- CPKG Queries ---

def get_nodes_by_type(cpkg: CPKG, node_type: NodeType) -> List[CPKGNode]:
    """
    Retrieve all nodes of a specific type.
    """
    return [node for node in cpkg.nodes.values() if node.type == node_type]


def get_node_by_id(cpkg: CPKG, node_id: str) -> Optional[CPKGNode]:
    """
    Retrieve a single node by ID.
    """
    return cpkg.nodes.get(node_id)


def get_outgoing_edges(cpkg: CPKG, source_id: str, relationship: Optional[str] = None) -> List[CPKGEdge]:
    """
    Get all edges originating from a specific node.
    Optionally filter by relationship type.
    """
    edges = []
    for edge in cpkg.edges:
        if edge.source_id == source_id:
            if relationship is None or edge.relationship == relationship:
                edges.append(edge)
    return edges


def get_incoming_edges(cpkg: CPKG, target_id: str, relationship: Optional[str] = None) -> List[CPKGEdge]:
    """
    Get all edges targeting a specific node.
    Optionally filter by relationship type.
    """
    edges = []
    for edge in cpkg.edges:
        if edge.target_id == target_id:
            if relationship is None or edge.relationship == relationship:
                edges.append(edge)
    return edges


def get_direct_dependencies(cpkg: CPKG, component_id: str) -> List[CPKGNode]:
    """
    Get all nodes that a given component directly depends on.
    Assumes relationship="depends_on".
    """
    edges = get_outgoing_edges(cpkg, component_id, relationship="depends_on")
    dependencies = []
    for edge in edges:
        node = cpkg.nodes.get(edge.target_id)
        if node:
            dependencies.append(node)
    return dependencies


def get_component_responsibilities(cpkg: CPKG, component_id: str) -> List[CPKGNode]:
    """
    Get all responsibility nodes assigned to a component.
    Assumes relationship="has_responsibility" or similar, or directionality
    where Component -> Responsibility.
    """
    # Assuming Component -> (has) -> Responsibility
    edges = get_outgoing_edges(cpkg, component_id)
    responsibilities = []
    for edge in edges:
        node = cpkg.nodes.get(edge.target_id)
        if node and node.type == NodeType.RESPONSIBILITY:
            responsibilities.append(node)
    return responsibilities


def get_invariants_for_node(cpkg: CPKG, node_id: str) -> List[CPKGNode]:
    """
    Get all invariants linked to a specific node.
    """
    # Check both directions: Node -> Invariant or Invariant -> Node
    # Usually Invariant -> (constrains) -> Node, or Node -> (must_satisfy) -> Invariant
    # We'll check for connected nodes of type INVARIANT.
    
    related_nodes = []
    
    # Outgoing
    for edge in get_outgoing_edges(cpkg, node_id):
        node = cpkg.nodes.get(edge.target_id)
        if node and node.type == NodeType.INVARIANT:
            related_nodes.append(node)
            
    # Incoming
    for edge in get_incoming_edges(cpkg, node_id):
        node = cpkg.nodes.get(edge.source_id)
        if node and node.type == NodeType.INVARIANT:
            related_nodes.append(node)
            
    return related_nodes


# --- BFM Queries ---

def get_flow_node(bfm: BusinessFlowMap, node_id: str) -> Optional[BusinessFlowNode]:
    """
    Retrieve a BFM node by ID.
    """
    return bfm.nodes.get(node_id)


def get_next_transitions(bfm: BusinessFlowMap, current_node_id: str) -> List[BusinessFlowTransition]:
    """
    Get all possible transitions from the current flow node.
    """
    return [t for t in bfm.transitions if t.source_id == current_node_id]


def get_previous_transitions(bfm: BusinessFlowMap, current_node_id: str) -> List[BusinessFlowTransition]:
    """
    Get all transitions that lead to the current flow node.
    """
    return [t for t in bfm.transitions if t.target_id == current_node_id]


def get_downstream_nodes(bfm: BusinessFlowMap, node_id: str) -> List[BusinessFlowNode]:
    """
    Get all nodes immediately reachable from the given node.
    """
    transitions = get_next_transitions(bfm, node_id)
    nodes = []
    for t in transitions:
        node = bfm.nodes.get(t.target_id)
        if node:
            nodes.append(node)
    return nodes


# --- UCIR Queries ---

def get_constraints_by_scope(ucir: UCIR, scope: str) -> List[UserConstraint]:
    """
    Get all constraints matching a specific scope (exact match).
    """
    return [c for c in ucir.constraints.values() if c.scope == scope]


def get_constraints_by_level(ucir: UCIR, level: ConstraintLevel) -> List[UserConstraint]:
    """
    Get all constraints of a specific severity level.
    """
    return [c for c in ucir.constraints.values() if c.level == level]


def get_critical_constraints(ucir: UCIR) -> List[UserConstraint]:
    """
    Get all CRITICAL constraints.
    """
    return get_constraints_by_level(ucir, ConstraintLevel.CRITICAL)


def search_constraints(ucir: UCIR, keyword: str) -> List[UserConstraint]:
    """
    Find constraints containing a keyword in their description.
    Case-insensitive.
    """
    kw = keyword.lower()
    return [
        c for c in ucir.constraints.values() 
        if kw in c.description.lower()
    ]
