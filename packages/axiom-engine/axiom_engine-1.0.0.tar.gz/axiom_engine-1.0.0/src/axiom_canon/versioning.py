"""
Versioning Utilities for Axiom Knowledge Artifacts.

This module provides utilities to generate deterministic version identifiers
and manage lightweight metadata for knowledge artifacts.

Why Versioning?
- Traceability: We must know exactly which version of the truth was used.
- Integrity: Hashes ensure that the data has not been tampered with.
- Governance: Human approvals are tied to specific versions.

Responsibilities:
- Generate SHA-256 hashes of deterministic JSON representations.
- Define a separate metadata structure for tracking authorship and approval.

Constraints:
- Metadata is SEPARATE from the artifact content.
- Metadata does not affect the artifact's hash (the hash identifies the content).
- Pure functions only.
"""

import hashlib
from dataclasses import dataclass, field
from typing import Optional, Any

from axiom_canon.serialization import (
    serialize_cpkg,
    serialize_bfm,
    serialize_ucir,
    serialize_task_graph
)
from axiom_canon.cpkg import CPKG
from axiom_canon.bfm import BusinessFlowMap
from axiom_canon.ucir import UCIR
from axiom_canon.task_graph import TaskGraph


@dataclass
class ArtifactMetadata:
    """
    Lightweight metadata for a knowledge artifact version.
    This is NOT part of the canonical artifact itself.
    """
    version_hash: str
    parent_hash: Optional[str] = None
    author: Optional[str] = None
    timestamp_utc: Optional[str] = None  # ISO 8601 string
    change_summary: str = ""
    approved_by: Optional[str] = None
    approval_status: str = "pending"  # pending, approved, rejected


def compute_hash(content: str) -> str:
    """Compute SHA-256 hash of a string."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def get_cpkg_version_hash(cpkg: CPKG) -> str:
    """Get the deterministic hash of a CPKG."""
    serialized = serialize_cpkg(cpkg)
    return compute_hash(serialized)


def get_bfm_version_hash(bfm: BusinessFlowMap) -> str:
    """Get the deterministic hash of a BFM."""
    serialized = serialize_bfm(bfm)
    return compute_hash(serialized)


def get_ucir_version_hash(ucir: UCIR) -> str:
    """Get the deterministic hash of a UCIR."""
    serialized = serialize_ucir(ucir)
    return compute_hash(serialized)


def get_task_graph_version_hash(graph: TaskGraph) -> str:
    """Get the deterministic hash of a TaskGraph."""
    serialized = serialize_task_graph(graph)
    return compute_hash(serialized)
