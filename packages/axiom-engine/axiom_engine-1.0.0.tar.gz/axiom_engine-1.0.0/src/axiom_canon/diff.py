"""
Structural Diffing for Axiom Knowledge Artifacts.

This module provides utilities to compare two versions of an artifact
and produce a structured difference report.

Why Diffing?
- Governance: Humans need to see exactly what changed before approving.
- Validation: We can detect semantic regressions by analyzing diffs.
- Auditing: Every change to the system truth must be trackable.

Responsibilities:
- Detect added, removed, and modified nodes.
- Detect added and removed edges/transitions.
- Report field-level changes for modified nodes.

Constraints:
- Pure functions only.
- No intent inference (just report the data change).
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Generic, List, Optional, Set, TypeVar

from axiom_canon.cpkg import CPKG, CPKGEdge
from axiom_canon.bfm import BusinessFlowMap, BusinessFlowTransition
from axiom_canon.ucir import UCIR
from axiom_canon.task_graph import TaskGraph, TaskDependency
from axiom_canon.serialization import _to_dict_deterministic

T = TypeVar("T")


@dataclass
class FieldChange:
    field_name: str
    old_value: Any
    new_value: Any


@dataclass
class NodeDiff:
    added_ids: List[str] = field(default_factory=list)
    removed_ids: List[str] = field(default_factory=list)
    modified_ids: Dict[str, List[FieldChange]] = field(default_factory=dict)


@dataclass
class EdgeDiff(Generic[T]):
    added: List[T] = field(default_factory=list)
    removed: List[T] = field(default_factory=list)


@dataclass
class ArtifactDiff:
    nodes: NodeDiff = field(default_factory=NodeDiff)
    edges: EdgeDiff = field(default_factory=EdgeDiff)
    has_changes: bool = False


def _diff_dicts(old_dict: Dict[str, Any], new_dict: Dict[str, Any]) -> List[FieldChange]:
    """Compare two dictionaries (representing objects) and return field changes."""
    changes = []
    all_keys = set(old_dict.keys()) | set(new_dict.keys())
    
    for key in all_keys:
        old_val = old_dict.get(key)
        new_val = new_dict.get(key)
        
        # Simple equality check. For nested structures, this might be too coarse,
        # but for our flat schemas, it's usually sufficient.
        if old_val != new_val:
            changes.append(FieldChange(field_name=key, old_value=old_val, new_value=new_val))
            
    return changes


def _diff_nodes(old_nodes: Dict[str, Any], new_nodes: Dict[str, Any]) -> NodeDiff:
    """Generic node diffing logic."""
    old_ids = set(old_nodes.keys())
    new_ids = set(new_nodes.keys())
    
    added = sorted(list(new_ids - old_ids))
    removed = sorted(list(old_ids - new_ids))
    modified = {}
    
    common_ids = old_ids & new_ids
    for nid in common_ids:
        # Convert to dict for comparison to handle dataclasses
        old_obj_dict = _to_dict_deterministic(old_nodes[nid])
        new_obj_dict = _to_dict_deterministic(new_nodes[nid])
        
        changes = _diff_dicts(old_obj_dict, new_obj_dict)
        if changes:
            modified[nid] = changes
            
    return NodeDiff(added_ids=added, removed_ids=removed, modified_ids=modified)


def _diff_lists(old_list: List[Any], new_list: List[Any]) -> EdgeDiff:
    """
    Generic list diffing logic.
    Assumes items are hashable or comparable.
    Since dataclasses aren't always hashable by default (unless frozen),
    we serialize them to tuples of sorted items for set comparison.
    """
    def to_comparable(obj):
        d = _to_dict_deterministic(obj)
        # Convert dict to sorted tuple of items recursively to make it hashable
        return _make_hashable(d)

    old_set = {to_comparable(x) for x in old_list}
    new_set = {to_comparable(x) for x in new_list}
    
    # We need to map back from hashable representation to original object for the report
    # This is a bit expensive but safe.
    
    added_reprs = new_set - old_set
    removed_reprs = old_set - new_set
    
    added_items = [x for x in new_list if to_comparable(x) in added_reprs]
    removed_items = [x for x in old_list if to_comparable(x) in removed_reprs]
    
    return EdgeDiff(added=added_items, removed=removed_items)


def _make_hashable(value: Any) -> Any:
    if isinstance(value, dict):
        return tuple(sorted((k, _make_hashable(v)) for k, v in value.items()))
    if isinstance(value, list):
        return tuple(_make_hashable(v) for v in value)
    return value


def diff_cpkg(old: CPKG, new: CPKG) -> ArtifactDiff:
    node_diff = _diff_nodes(old.nodes, new.nodes)
    edge_diff = _diff_lists(old.edges, new.edges)
    
    has_changes = (
        bool(node_diff.added_ids) or 
        bool(node_diff.removed_ids) or 
        bool(node_diff.modified_ids) or 
        bool(edge_diff.added) or 
        bool(edge_diff.removed)
    )
    
    return ArtifactDiff(nodes=node_diff, edges=edge_diff, has_changes=has_changes)


def diff_bfm(old: BusinessFlowMap, new: BusinessFlowMap) -> ArtifactDiff:
    node_diff = _diff_nodes(old.nodes, new.nodes)
    edge_diff = _diff_lists(old.transitions, new.transitions)
    
    has_changes = (
        bool(node_diff.added_ids) or 
        bool(node_diff.removed_ids) or 
        bool(node_diff.modified_ids) or 
        bool(edge_diff.added) or 
        bool(edge_diff.removed)
    )
    
    return ArtifactDiff(nodes=node_diff, edges=edge_diff, has_changes=has_changes)


def diff_ucir(old: UCIR, new: UCIR) -> ArtifactDiff:
    # UCIR only has nodes (constraints), no edges
    node_diff = _diff_nodes(old.constraints, new.constraints)
    
    has_changes = (
        bool(node_diff.added_ids) or 
        bool(node_diff.removed_ids) or 
        bool(node_diff.modified_ids)
    )
    
    return ArtifactDiff(nodes=node_diff, edges=EdgeDiff(), has_changes=has_changes)


def diff_task_graph(old: TaskGraph, new: TaskGraph) -> ArtifactDiff:
    node_diff = _diff_nodes(old.tasks, new.tasks)
    edge_diff = _diff_lists(old.dependencies, new.dependencies)
    
    has_changes = (
        bool(node_diff.added_ids) or 
        bool(node_diff.removed_ids) or 
        bool(node_diff.modified_ids) or 
        bool(edge_diff.added) or 
        bool(edge_diff.removed)
    )
    
    return ArtifactDiff(nodes=node_diff, edges=edge_diff, has_changes=has_changes)
