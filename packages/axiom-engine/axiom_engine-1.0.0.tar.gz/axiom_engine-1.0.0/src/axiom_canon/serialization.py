"""
Deterministic Serialization for Axiom Knowledge Artifacts.

This module provides utilities to convert knowledge artifacts into
strictly deterministic, sorted JSON representations.

Why Deterministic?
- Hashing: We need stable hashes to identify versions.
- Diffing: Stable ordering reduces noise in text-based diffs.
- Signing: Cryptographic signatures require byte-for-byte stability.

Responsibilities:
- Convert dataclasses to dicts with sorted keys.
- Sort lists of objects by stable criteria.
- Serialize Enums to their values.
- Produce compact or pretty-printed JSON.

Constraints:
- NO timestamps.
- NO non-deterministic fields (e.g., random IDs generated at serialization time).
- Pure functions only.
"""

import json
import dataclasses
from enum import Enum
from typing import Any, Dict, List, Type, TypeVar, Union

from axiom_canon.cpkg import CPKG, CPKGEdge
from axiom_canon.bfm import BusinessFlowMap, BusinessFlowTransition
from axiom_canon.ucir import UCIR
from axiom_canon.task_graph import TaskGraph, TaskDependency

T = TypeVar("T")


def _sort_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively sort dictionary keys."""
    return {k: _sort_value(v) for k, v in sorted(d.items())}


def _sort_value(v: Any) -> Any:
    """Recursively sort values (lists and dicts)."""
    if isinstance(v, dict):
        return _sort_dict(v)
    if isinstance(v, list):
        # We can't easily sort a list of mixed types or dicts without a key.
        # For our specific schemas, lists usually contain objects that can be sorted
        # by specific fields. We handle this in the specific serializers.
        # If it's a list of primitives, we sort it.
        try:
            return sorted([_sort_value(x) for x in v])
        except TypeError:
            # If items are not comparable (e.g. dicts), return as is (processed recursively)
            # The specific serializers should handle sorting of complex object lists.
            return [_sort_value(x) for x in v]
    return v


def _to_dict_deterministic(obj: Any) -> Any:
    """
    Convert a dataclass or object to a dict, handling Enums and recursion,
    but NOT sorting keys yet (that happens at the end).
    """
    if dataclasses.is_dataclass(obj):
        result = {}
        for field in dataclasses.fields(obj):
            value = getattr(obj, field.name)
            result[field.name] = _to_dict_deterministic(value)
        return result
    elif isinstance(obj, Enum):
        return obj.value
    elif isinstance(obj, dict):
        return {k: _to_dict_deterministic(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_to_dict_deterministic(x) for x in obj]
    else:
        return obj


def serialize_cpkg(cpkg: CPKG) -> str:
    """
    Serialize CPKG to a deterministic JSON string.
    Edges are sorted by source_id, then target_id, then relationship.
    """
    data = _to_dict_deterministic(cpkg)
    
    # Sort edges explicitly for stability
    if "edges" in data and isinstance(data["edges"], list):
        data["edges"].sort(key=lambda x: (x.get("source_id", ""), x.get("target_id", ""), x.get("relationship", "")))
    
    # Sort nodes by ID (keys of the dict are already sorted by _sort_dict later, 
    # but if it was a list we'd need to sort. It is a Dict in schema.)
    
    sorted_data = _sort_dict(data)
    return json.dumps(sorted_data, sort_keys=True, separators=(",", ":"))


def serialize_bfm(bfm: BusinessFlowMap) -> str:
    """
    Serialize BFM to a deterministic JSON string.
    Transitions are sorted by source_id, then target_id, then trigger.
    """
    data = _to_dict_deterministic(bfm)
    
    if "transitions" in data and isinstance(data["transitions"], list):
        data["transitions"].sort(key=lambda x: (x.get("source_id", ""), x.get("target_id", ""), x.get("trigger", "")))
        
    sorted_data = _sort_dict(data)
    return json.dumps(sorted_data, sort_keys=True, separators=(",", ":"))


def serialize_ucir(ucir: UCIR) -> str:
    """
    Serialize UCIR to a deterministic JSON string.
    """
    data = _to_dict_deterministic(ucir)
    sorted_data = _sort_dict(data)
    return json.dumps(sorted_data, sort_keys=True, separators=(",", ":"))


def serialize_task_graph(graph: TaskGraph) -> str:
    """
    Serialize TaskGraph to a deterministic JSON string.
    Dependencies are sorted by upstream_task_id, then downstream_task_id.
    """
    data = _to_dict_deterministic(graph)
    
    if "dependencies" in data and isinstance(data["dependencies"], list):
        data["dependencies"].sort(key=lambda x: (x.get("upstream_task_id", ""), x.get("downstream_task_id", "")))
        
    sorted_data = _sort_dict(data)
    return json.dumps(sorted_data, sort_keys=True, separators=(",", ":"))
