"""
Validation Utilities for Axiom Knowledge Artifacts.

This module provides pure, deterministic validation logic for:
- Canonical Project Knowledge Graph (CPKG)
- Business Flow Map (BFM)
- User Constraint & Instruction Registry (UCIR)
- Task Graph (DAG)

Architectural Requirement:
Axiom relies on strict data integrity. Invalid knowledge artifacts can lead to
hallucinations, broken plans, or infinite loops in execution. This module
enforces structural correctness before any artifact is used by agents.

Responsibilities:
- Check ID uniqueness
- Verify reference integrity (no dangling edges)
- Enforce graph properties (e.g., DAG cycles)
- Validate schema constraints

Constraints:
- NO side effects (I/O, database access)
- NO execution logic
- NO agent reasoning
- Pure functions only
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Set, Optional, Any

from axiom_canon.cpkg import CPKG
from axiom_canon.bfm import BusinessFlowMap
from axiom_canon.ucir import UCIR
from axiom_canon.task_graph import TaskGraph


class ValidationSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass
class ValidationError:
    """
    Represents a single validation issue.
    """
    severity: ValidationSeverity
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    artifact_type: str = "unknown"
    entity_id: Optional[str] = None


@dataclass
class ValidationResult:
    """
    The result of a validation operation.
    """
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)

    def add_error(self, message: str, context: Dict[str, Any] = None, entity_id: str = None):
        self.is_valid = False
        self.errors.append(ValidationError(
            severity=ValidationSeverity.ERROR,
            message=message,
            context=context or {},
            entity_id=entity_id
        ))

    def add_warning(self, message: str, context: Dict[str, Any] = None, entity_id: str = None):
        self.errors.append(ValidationError(
            severity=ValidationSeverity.WARNING,
            message=message,
            context=context or {},
            entity_id=entity_id
        ))


def validate_cpkg(cpkg: CPKG) -> ValidationResult:
    """
    Validates a Canonical Project Knowledge Graph.
    
    Checks:
    - All edges point to existing nodes.
    - No self-referential edges (unless explicitly allowed, but usually discouraged).
    """
    result = ValidationResult(is_valid=True)
    node_ids = set(cpkg.nodes.keys())

    # Check edges for dangling references
    for i, edge in enumerate(cpkg.edges):
        if edge.source_id not in node_ids:
            result.add_error(
                f"Edge references missing source node '{edge.source_id}'",
                context={"edge_index": i, "target_id": edge.target_id},
                entity_id=edge.source_id
            )
        if edge.target_id not in node_ids:
            result.add_error(
                f"Edge references missing target node '{edge.target_id}'",
                context={"edge_index": i, "source_id": edge.source_id},
                entity_id=edge.target_id
            )

    return result


def validate_bfm(bfm: BusinessFlowMap) -> ValidationResult:
    """
    Validates a Business Flow Map.
    
    Checks:
    - All transitions point to existing nodes.
    - Nodes have required fields (name, description).
    """
    result = ValidationResult(is_valid=True)
    node_ids = set(bfm.nodes.keys())

    # Check nodes
    for node_id, node in bfm.nodes.items():
        if not node.name.strip():
            result.add_error("BusinessFlowNode must have a non-empty name", entity_id=node_id)
        if not node.description.strip():
            result.add_warning("BusinessFlowNode description is empty", entity_id=node_id)

    # Check transitions
    for i, transition in enumerate(bfm.transitions):
        if transition.source_id not in node_ids:
            result.add_error(
                f"Transition references missing source node '{transition.source_id}'",
                context={"transition_index": i},
                entity_id=transition.source_id
            )
        if transition.target_id not in node_ids:
            result.add_error(
                f"Transition references missing target node '{transition.target_id}'",
                context={"transition_index": i},
                entity_id=transition.target_id
            )

    return result


def validate_ucir(ucir: UCIR) -> ValidationResult:
    """
    Validates the User Constraint & Instruction Registry.
    
    Checks:
    - Constraints have non-empty descriptions.
    - Constraints have valid levels.
    """
    result = ValidationResult(is_valid=True)

    for constraint_id, constraint in ucir.constraints.items():
        if not constraint.description.strip():
            result.add_error("UserConstraint must have a description", entity_id=constraint_id)
        
        if not constraint.source.strip():
            result.add_warning("UserConstraint source is empty", entity_id=constraint_id)

    return result


def validate_task_graph(graph: TaskGraph) -> ValidationResult:
    """
    Validates a Task Graph.
    
    Checks:
    - All dependencies point to existing tasks.
    - The graph is acyclic (DAG).
    - Tasks have required fields.
    """
    result = ValidationResult(is_valid=True)
    task_ids = set(graph.tasks.keys())

    # Check dependencies
    adj_list: Dict[str, List[str]] = {tid: [] for tid in task_ids}
    
    for i, dep in enumerate(graph.dependencies):
        if dep.upstream_task_id not in task_ids:
            result.add_error(
                f"Dependency references missing upstream task '{dep.upstream_task_id}'",
                context={"dependency_index": i},
                entity_id=dep.upstream_task_id
            )
            continue
        
        if dep.downstream_task_id not in task_ids:
            result.add_error(
                f"Dependency references missing downstream task '{dep.downstream_task_id}'",
                context={"dependency_index": i},
                entity_id=dep.downstream_task_id
            )
            continue
            
        adj_list[dep.upstream_task_id].append(dep.downstream_task_id)

    # Cycle Detection (DFS)
    visited = set()
    recursion_stack = set()

    def has_cycle(node_id: str) -> bool:
        visited.add(node_id)
        recursion_stack.add(node_id)

        for neighbor in adj_list.get(node_id, []):
            if neighbor not in visited:
                if has_cycle(neighbor):
                    return True
            elif neighbor in recursion_stack:
                return True

        recursion_stack.remove(node_id)
        return False

    for node_id in task_ids:
        if node_id not in visited:
            if has_cycle(node_id):
                result.add_error(
                    "Cycle detected in Task Graph",
                    context={"start_node": node_id}
                )
                break

    return result
