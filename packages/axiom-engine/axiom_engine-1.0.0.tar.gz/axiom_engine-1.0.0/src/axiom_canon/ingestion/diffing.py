"""
Ingestion Diffing.

This module provides diffing capabilities for ingestion results.
Enables comparison between ingestion runs and Canon artifacts.

Key features:
- Compute differences between ingestion results
- Support incremental updates
- Enable human review before Canon updates

CONSTRAINTS:
- Diffing is OBSERVATION, not modification
- No auto-write to Canon
- Explicit human review required
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar

from axiom_canon.ingestion.models import (
    APIExposureSummary,
    ComponentSummary,
    DependencyEdgeSummary,
    IngestionResult,
    InvariantSummary,
    ModuleSummary,
)


# =============================================================================
# Enums
# =============================================================================


class ChangeType(str, Enum):
    """Type of change detected."""
    
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"


# =============================================================================
# Change Records
# =============================================================================


T = TypeVar("T")


@dataclass
class ArtifactChange(Generic[T]):
    """
    Record of a change to an artifact.
    
    Attributes:
        artifact_id: Stable ID of the artifact.
        artifact_type: Type of artifact (module, component, etc.).
        change_type: Type of change.
        old_value: Previous value (if modified or removed).
        new_value: New value (if added or modified).
        changed_fields: List of changed field names (if modified).
        old_hash: Previous version hash.
        new_hash: New version hash.
    """
    
    artifact_id: str
    artifact_type: str
    change_type: ChangeType
    old_value: Optional[T] = None
    new_value: Optional[T] = None
    changed_fields: List[str] = field(default_factory=list)
    old_hash: str = ""
    new_hash: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "change_type": self.change_type.value,
            "changed_fields": self.changed_fields,
            "old_hash": self.old_hash,
            "new_hash": self.new_hash,
        }
        
        # Include values if present (as dicts)
        if self.old_value is not None and hasattr(self.old_value, "to_dict"):
            result["old_value"] = self.old_value.to_dict()
        if self.new_value is not None and hasattr(self.new_value, "to_dict"):
            result["new_value"] = self.new_value.to_dict()
        
        return result


# =============================================================================
# Ingestion Diff
# =============================================================================


@dataclass
class IngestionDiff:
    """
    Diff between two ingestion results.
    
    Captures all changes between ingestion runs.
    Used for incremental updates and human review.
    
    Attributes:
        old_timestamp: Timestamp of old ingestion.
        new_timestamp: Timestamp of new ingestion.
        old_hash: Version hash of old result.
        new_hash: Version hash of new result.
        module_changes: Changes to modules.
        component_changes: Changes to components.
        api_changes: Changes to API exposures.
        dependency_changes: Changes to dependency edges.
        invariant_changes: Changes to invariants.
        summary: Human-readable summary of changes.
    """
    
    old_timestamp: str
    new_timestamp: str
    old_hash: str
    new_hash: str
    module_changes: List[ArtifactChange[ModuleSummary]] = field(default_factory=list)
    component_changes: List[ArtifactChange[ComponentSummary]] = field(default_factory=list)
    api_changes: List[ArtifactChange[APIExposureSummary]] = field(default_factory=list)
    dependency_changes: List[ArtifactChange[DependencyEdgeSummary]] = field(default_factory=list)
    invariant_changes: List[ArtifactChange[InvariantSummary]] = field(default_factory=list)
    summary: str = ""
    
    @property
    def has_changes(self) -> bool:
        """Check if there are any changes."""
        return (
            len(self.module_changes) > 0
            or len(self.component_changes) > 0
            or len(self.api_changes) > 0
            or len(self.dependency_changes) > 0
            or len(self.invariant_changes) > 0
        )
    
    @property
    def total_changes(self) -> int:
        """Get total number of changes."""
        return (
            len(self.module_changes)
            + len(self.component_changes)
            + len(self.api_changes)
            + len(self.dependency_changes)
            + len(self.invariant_changes)
        )
    
    def get_changes_by_type(self, change_type: ChangeType) -> List[ArtifactChange]:
        """Get all changes of a specific type."""
        all_changes: List[ArtifactChange] = []
        all_changes.extend(self.module_changes)
        all_changes.extend(self.component_changes)
        all_changes.extend(self.api_changes)
        all_changes.extend(self.dependency_changes)
        all_changes.extend(self.invariant_changes)
        return [c for c in all_changes if c.change_type == change_type]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "old_timestamp": self.old_timestamp,
            "new_timestamp": self.new_timestamp,
            "old_hash": self.old_hash,
            "new_hash": self.new_hash,
            "module_changes": [c.to_dict() for c in self.module_changes],
            "component_changes": [c.to_dict() for c in self.component_changes],
            "api_changes": [c.to_dict() for c in self.api_changes],
            "dependency_changes": [c.to_dict() for c in self.dependency_changes],
            "invariant_changes": [c.to_dict() for c in self.invariant_changes],
            "summary": self.summary,
            "has_changes": self.has_changes,
            "total_changes": self.total_changes,
        }
    
    def render_summary(self) -> str:
        """
        Render a human-readable summary of changes.
        
        Returns:
            Multi-line string summarizing all changes.
        """
        lines = [
            "=" * 60,
            "INGESTION DIFF SUMMARY",
            "=" * 60,
            f"Old: {self.old_timestamp} ({self.old_hash[:12]}...)",
            f"New: {self.new_timestamp} ({self.new_hash[:12]}...)",
            "",
        ]
        
        if not self.has_changes:
            lines.append("No changes detected.")
            return "\n".join(lines)
        
        # Module changes
        if self.module_changes:
            lines.append(f"Module Changes ({len(self.module_changes)}):")
            lines.append("-" * 40)
            for change in self.module_changes:
                symbol = self._change_symbol(change.change_type)
                lines.append(f"  {symbol} {change.artifact_id}")
                if change.changed_fields:
                    lines.append(f"    Changed: {', '.join(change.changed_fields)}")
            lines.append("")
        
        # Component changes
        if self.component_changes:
            lines.append(f"Component Changes ({len(self.component_changes)}):")
            lines.append("-" * 40)
            for change in self.component_changes:
                symbol = self._change_symbol(change.change_type)
                lines.append(f"  {symbol} {change.artifact_id}")
            lines.append("")
        
        # API changes
        if self.api_changes:
            lines.append(f"API Changes ({len(self.api_changes)}):")
            lines.append("-" * 40)
            for change in self.api_changes:
                symbol = self._change_symbol(change.change_type)
                lines.append(f"  {symbol} {change.artifact_id}")
            lines.append("")
        
        # Dependency changes
        if self.dependency_changes:
            lines.append(f"Dependency Changes ({len(self.dependency_changes)}):")
            lines.append("-" * 40)
            for change in self.dependency_changes:
                symbol = self._change_symbol(change.change_type)
                lines.append(f"  {symbol} {change.artifact_id}")
            lines.append("")
        
        # Invariant changes
        if self.invariant_changes:
            lines.append(f"Invariant Changes ({len(self.invariant_changes)}):")
            lines.append("-" * 40)
            for change in self.invariant_changes:
                symbol = self._change_symbol(change.change_type)
                lines.append(f"  {symbol} {change.artifact_id}")
            lines.append("")
        
        # Summary stats
        lines.append("=" * 60)
        added = len(self.get_changes_by_type(ChangeType.ADDED))
        removed = len(self.get_changes_by_type(ChangeType.REMOVED))
        modified = len(self.get_changes_by_type(ChangeType.MODIFIED))
        lines.append(f"Total: {added} added, {removed} removed, {modified} modified")
        
        return "\n".join(lines)
    
    def _change_symbol(self, change_type: ChangeType) -> str:
        """Get symbol for change type."""
        symbols = {
            ChangeType.ADDED: "+",
            ChangeType.REMOVED: "-",
            ChangeType.MODIFIED: "~",
            ChangeType.UNCHANGED: " ",
        }
        return symbols.get(change_type, "?")


# =============================================================================
# Diff Computation
# =============================================================================


def compute_diff(
    old_result: IngestionResult,
    new_result: IngestionResult,
) -> IngestionDiff:
    """
    Compute diff between two ingestion results.
    
    This is a pure, deterministic function.
    Does NOT modify any artifacts.
    
    Args:
        old_result: Previous ingestion result.
        new_result: New ingestion result.
        
    Returns:
        IngestionDiff capturing all changes.
    """
    diff = IngestionDiff(
        old_timestamp=old_result.ingestion_timestamp,
        new_timestamp=new_result.ingestion_timestamp,
        old_hash=old_result.version_hash,
        new_hash=new_result.version_hash,
    )
    
    # If hashes match, no changes
    if old_result.version_hash == new_result.version_hash:
        diff.summary = "No changes detected."
        return diff
    
    # Diff modules
    diff.module_changes = _diff_artifacts(
        old_result.modules,
        new_result.modules,
        "module",
    )
    
    # Diff components
    diff.component_changes = _diff_artifacts(
        old_result.components,
        new_result.components,
        "component",
    )
    
    # Diff API exposures
    diff.api_changes = _diff_artifacts(
        old_result.api_exposures,
        new_result.api_exposures,
        "api",
    )
    
    # Diff dependency edges
    diff.dependency_changes = _diff_artifacts(
        old_result.dependency_edges,
        new_result.dependency_edges,
        "dependency",
    )
    
    # Diff invariants
    diff.invariant_changes = _diff_artifacts(
        old_result.invariants,
        new_result.invariants,
        "invariant",
    )
    
    # Generate summary
    diff.summary = diff.render_summary()
    
    return diff


def _diff_artifacts(
    old_artifacts: List[Any],
    new_artifacts: List[Any],
    artifact_type: str,
) -> List[ArtifactChange]:
    """
    Diff two lists of artifacts.
    
    Args:
        old_artifacts: Previous artifacts.
        new_artifacts: New artifacts.
        artifact_type: Type name for the artifacts.
        
    Returns:
        List of changes.
    """
    changes = []
    
    # Index by ID
    old_by_id = {a.id: a for a in old_artifacts}
    new_by_id = {a.id: a for a in new_artifacts}
    
    all_ids = set(old_by_id.keys()) | set(new_by_id.keys())
    
    for artifact_id in sorted(all_ids):  # Sort for determinism
        old_artifact = old_by_id.get(artifact_id)
        new_artifact = new_by_id.get(artifact_id)
        
        if old_artifact is None and new_artifact is not None:
            # Added
            changes.append(
                ArtifactChange(
                    artifact_id=artifact_id,
                    artifact_type=artifact_type,
                    change_type=ChangeType.ADDED,
                    new_value=new_artifact,
                    new_hash=new_artifact.version_hash,
                )
            )
        elif old_artifact is not None and new_artifact is None:
            # Removed
            changes.append(
                ArtifactChange(
                    artifact_id=artifact_id,
                    artifact_type=artifact_type,
                    change_type=ChangeType.REMOVED,
                    old_value=old_artifact,
                    old_hash=old_artifact.version_hash,
                )
            )
        elif old_artifact is not None and new_artifact is not None:
            # Check for modifications
            if old_artifact.version_hash != new_artifact.version_hash:
                changed_fields = _detect_changed_fields(old_artifact, new_artifact)
                changes.append(
                    ArtifactChange(
                        artifact_id=artifact_id,
                        artifact_type=artifact_type,
                        change_type=ChangeType.MODIFIED,
                        old_value=old_artifact,
                        new_value=new_artifact,
                        changed_fields=changed_fields,
                        old_hash=old_artifact.version_hash,
                        new_hash=new_artifact.version_hash,
                    )
                )
    
    return changes


def _detect_changed_fields(old: Any, new: Any) -> List[str]:
    """
    Detect which fields changed between two artifacts.
    
    Args:
        old: Old artifact.
        new: New artifact.
        
    Returns:
        List of changed field names.
    """
    changed = []
    
    # Get dict representations
    old_dict = old.to_dict() if hasattr(old, "to_dict") else {}
    new_dict = new.to_dict() if hasattr(new, "to_dict") else {}
    
    # Compare fields
    all_keys = set(old_dict.keys()) | set(new_dict.keys())
    
    for key in sorted(all_keys):
        # Skip meta fields
        if key in ("version_hash", "id"):
            continue
        
        old_val = old_dict.get(key)
        new_val = new_dict.get(key)
        
        if old_val != new_val:
            changed.append(key)
    
    return changed


# =============================================================================
# Diff Application
# =============================================================================


@dataclass
class DiffApplicationResult:
    """
    Result of applying a diff.
    
    Note: This does NOT auto-write to Canon.
    It produces artifacts ready for human review.
    
    Attributes:
        proposed_result: The proposed new IngestionResult.
        requires_review: Whether human review is required.
        review_reasons: Reasons why review is required.
    """
    
    proposed_result: IngestionResult
    requires_review: bool = True
    review_reasons: List[str] = field(default_factory=list)


def apply_diff(
    base_result: IngestionResult,
    diff: IngestionDiff,
) -> DiffApplicationResult:
    """
    Apply a diff to produce a new ingestion result.
    
    IMPORTANT: This does NOT auto-write to Canon.
    The result requires explicit human review.
    
    Args:
        base_result: The base ingestion result.
        diff: The diff to apply.
        
    Returns:
        DiffApplicationResult with proposed changes.
    """
    # Start with a copy of base
    new_modules = list(base_result.modules)
    new_components = list(base_result.components)
    new_api_exposures = list(base_result.api_exposures)
    new_dependency_edges = list(base_result.dependency_edges)
    new_invariants = list(base_result.invariants)
    
    review_reasons = []
    
    # Apply module changes
    for change in diff.module_changes:
        if change.change_type == ChangeType.ADDED:
            if change.new_value:
                new_modules.append(change.new_value)
                review_reasons.append(f"New module: {change.artifact_id}")
        elif change.change_type == ChangeType.REMOVED:
            new_modules = [m for m in new_modules if m.id != change.artifact_id]
            review_reasons.append(f"Removed module: {change.artifact_id}")
        elif change.change_type == ChangeType.MODIFIED:
            if change.new_value:
                new_modules = [
                    m if m.id != change.artifact_id else change.new_value
                    for m in new_modules
                ]
                review_reasons.append(
                    f"Modified module: {change.artifact_id} "
                    f"({', '.join(change.changed_fields)})"
                )
    
    # Apply component changes
    for change in diff.component_changes:
        if change.change_type == ChangeType.ADDED:
            if change.new_value:
                new_components.append(change.new_value)
        elif change.change_type == ChangeType.REMOVED:
            new_components = [c for c in new_components if c.id != change.artifact_id]
        elif change.change_type == ChangeType.MODIFIED:
            if change.new_value:
                new_components = [
                    c if c.id != change.artifact_id else change.new_value
                    for c in new_components
                ]
    
    # Apply API changes
    for change in diff.api_changes:
        if change.change_type == ChangeType.ADDED:
            if change.new_value:
                new_api_exposures.append(change.new_value)
                review_reasons.append(f"New API: {change.artifact_id}")
        elif change.change_type == ChangeType.REMOVED:
            new_api_exposures = [
                a for a in new_api_exposures if a.id != change.artifact_id
            ]
            review_reasons.append(f"Removed API: {change.artifact_id}")
        elif change.change_type == ChangeType.MODIFIED:
            if change.new_value:
                new_api_exposures = [
                    a if a.id != change.artifact_id else change.new_value
                    for a in new_api_exposures
                ]
                review_reasons.append(f"Modified API: {change.artifact_id}")
    
    # Apply dependency changes
    for change in diff.dependency_changes:
        if change.change_type == ChangeType.ADDED:
            if change.new_value:
                new_dependency_edges.append(change.new_value)
        elif change.change_type == ChangeType.REMOVED:
            new_dependency_edges = [
                e for e in new_dependency_edges if e.id != change.artifact_id
            ]
        elif change.change_type == ChangeType.MODIFIED:
            if change.new_value:
                new_dependency_edges = [
                    e if e.id != change.artifact_id else change.new_value
                    for e in new_dependency_edges
                ]
    
    # Apply invariant changes
    for change in diff.invariant_changes:
        if change.change_type == ChangeType.ADDED:
            if change.new_value:
                new_invariants.append(change.new_value)
                review_reasons.append(f"New invariant: {change.artifact_id}")
        elif change.change_type == ChangeType.REMOVED:
            new_invariants = [
                i for i in new_invariants if i.id != change.artifact_id
            ]
            review_reasons.append(f"Removed invariant: {change.artifact_id}")
        elif change.change_type == ChangeType.MODIFIED:
            if change.new_value:
                new_invariants = [
                    i if i.id != change.artifact_id else change.new_value
                    for i in new_invariants
                ]
    
    # Build proposed result
    proposed = IngestionResult(
        project_root=base_result.project_root,
        components=new_components,
        modules=new_modules,
        api_exposures=new_api_exposures,
        dependency_edges=new_dependency_edges,
        invariants=new_invariants,
        entry_points=base_result.entry_points,  # Not modified by diff
        config_boundaries=base_result.config_boundaries,  # Not modified by diff
        ingestion_timestamp=diff.new_timestamp,
    )
    
    return DiffApplicationResult(
        proposed_result=proposed,
        requires_review=len(review_reasons) > 0,
        review_reasons=review_reasons,
    )
