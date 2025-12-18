"""
Enrichment Models for LLM-Assisted Canon Population.

This module defines schemas for LLM enrichment artifacts.
These artifacts represent ADVISORY labeling, not ground truth.

CORE PRINCIPLE (NON-NEGOTIABLE):
LLMs may: Label, Compress, Explain, Highlight explicit facts
LLMs may NOT: Invent facts, Infer behavior, Add dependencies, Modify structure

All enrichment artifacts MUST:
- Be clearly marked as LLM-generated
- Include confidence indicators
- Be reviewable independently

Canon truth remains grounded in deterministic extraction + human approval.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


# =============================================================================
# Constants
# =============================================================================


# Label indicating LLM-generated content (must appear in all enrichments)
LLM_ENRICHMENT_LABEL = "[LLM ENRICHMENT – ADVISORY ONLY]"

# Maximum allowed description length (tokens ~ chars/4)
MAX_DESCRIPTION_CHARS = 200
MAX_LABEL_CHARS = 50
MAX_INVARIANT_TEXT_CHARS = 500


# =============================================================================
# Enums
# =============================================================================


class EnrichmentConfidence(str, Enum):
    """Confidence level of LLM enrichment."""
    
    HIGH = "high"       # Strong evidence in artifacts
    MEDIUM = "medium"   # Reasonable inference from context
    LOW = "low"         # Uncertain, needs human review
    UNKNOWN = "unknown" # Could not determine


class InvariantClassification(str, Enum):
    """Classification of extracted invariants."""
    
    EXPLICIT = "explicit"     # Clearly stated in docstring/comment
    UNCERTAIN = "uncertain"   # May be an invariant, needs verification


class EnrichmentIssueType(str, Enum):
    """Types of issues during enrichment."""
    
    PARSE_ERROR = "parse_error"             # Failed to parse LLM response
    VALIDATION_ERROR = "validation_error"   # Response failed validation
    CONFIDENCE_TOO_LOW = "confidence_too_low"
    UNKNOWN_ARTIFACT = "unknown_artifact"   # References non-existent artifact
    STRUCTURE_MODIFIED = "structure_modified"  # Attempted to modify structure
    TOKEN_LIMIT_EXCEEDED = "token_limit_exceeded"
    LLM_UNAVAILABLE = "llm_unavailable"
    HUMAN_REJECTED = "human_rejected"
    OUTPUT_TOO_VERBOSE = "output_too_verbose"


class ReviewDecision(str, Enum):
    """Human review decision for enrichment."""
    
    PENDING = "pending"     # Not yet reviewed
    APPROVED = "approved"   # Accepted as-is
    EDITED = "edited"       # Accepted with modifications
    REJECTED = "rejected"   # Rejected entirely


# =============================================================================
# Enrichment Issue
# =============================================================================


@dataclass
class EnrichmentIssue:
    """
    Issue encountered during enrichment.
    
    Captures errors, validation failures, and rejection reasons.
    
    Attributes:
        issue_type: Type of issue encountered.
        message: Human-readable description.
        artifact_id: ID of affected artifact (if applicable).
        details: Additional context.
    """
    
    issue_type: EnrichmentIssueType
    message: str
    artifact_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "issue_type": self.issue_type.value,
            "message": self.message,
            "artifact_id": self.artifact_id,
            "details": self.details,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnrichmentIssue":
        """Create from dictionary."""
        return cls(
            issue_type=EnrichmentIssueType(data["issue_type"]),
            message=data["message"],
            artifact_id=data.get("artifact_id"),
            details=data.get("details", {}),
        )


# =============================================================================
# Role A: Component Labeling
# =============================================================================


@dataclass
class EnrichedComponentLabel:
    """
    LLM-generated component label and description.
    
    Purpose: Speed up human understanding by compressing large structures
    into meaningful groupings.
    
    This is ADVISORY ONLY. Does not modify structure.
    
    Attributes:
        component_id: ID of the component being labeled.
        component_path: Path of the component.
        responsibility_label: Short label (max 50 chars).
        description: 1-2 sentence description (max 200 chars).
        confidence: Confidence level.
        assumptions: Explicit assumptions made (if any).
        source_context: What artifacts informed this label.
        llm_label: Marker indicating LLM-generated.
        timestamp: When enrichment was generated.
        review_decision: Human review status.
        reviewer_notes: Human reviewer notes.
    """
    
    component_id: str
    component_path: str
    responsibility_label: str
    description: str
    confidence: EnrichmentConfidence
    assumptions: List[str] = field(default_factory=list)
    source_context: List[str] = field(default_factory=list)
    llm_label: str = LLM_ENRICHMENT_LABEL
    timestamp: str = ""
    review_decision: ReviewDecision = ReviewDecision.PENDING
    reviewer_notes: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def validate(self) -> List[EnrichmentIssue]:
        """
        Validate the enrichment.
        
        Returns:
            List of validation issues (empty if valid).
        """
        issues = []
        
        # Check label length
        if len(self.responsibility_label) > MAX_LABEL_CHARS:
            issues.append(
                EnrichmentIssue(
                    issue_type=EnrichmentIssueType.OUTPUT_TOO_VERBOSE,
                    message=f"Label exceeds {MAX_LABEL_CHARS} chars",
                    artifact_id=self.component_id,
                    details={"actual_length": len(self.responsibility_label)},
                )
            )
        
        # Check description length
        if len(self.description) > MAX_DESCRIPTION_CHARS:
            issues.append(
                EnrichmentIssue(
                    issue_type=EnrichmentIssueType.OUTPUT_TOO_VERBOSE,
                    message=f"Description exceeds {MAX_DESCRIPTION_CHARS} chars",
                    artifact_id=self.component_id,
                    details={"actual_length": len(self.description)},
                )
            )
        
        # Check LLM label is present
        if self.llm_label != LLM_ENRICHMENT_LABEL:
            issues.append(
                EnrichmentIssue(
                    issue_type=EnrichmentIssueType.VALIDATION_ERROR,
                    message="Missing or incorrect LLM enrichment label",
                    artifact_id=self.component_id,
                )
            )
        
        # Confidence must be specified
        if self.confidence == EnrichmentConfidence.UNKNOWN:
            issues.append(
                EnrichmentIssue(
                    issue_type=EnrichmentIssueType.CONFIDENCE_TOO_LOW,
                    message="Confidence level is UNKNOWN",
                    artifact_id=self.component_id,
                )
            )
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "component_id": self.component_id,
            "component_path": self.component_path,
            "responsibility_label": self.responsibility_label,
            "description": self.description,
            "confidence": self.confidence.value,
            "assumptions": self.assumptions,
            "source_context": self.source_context,
            "llm_label": self.llm_label,
            "timestamp": self.timestamp,
            "review_decision": self.review_decision.value,
            "reviewer_notes": self.reviewer_notes,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnrichedComponentLabel":
        """Create from dictionary."""
        return cls(
            component_id=data["component_id"],
            component_path=data["component_path"],
            responsibility_label=data["responsibility_label"],
            description=data["description"],
            confidence=EnrichmentConfidence(data["confidence"]),
            assumptions=data.get("assumptions", []),
            source_context=data.get("source_context", []),
            llm_label=data.get("llm_label", LLM_ENRICHMENT_LABEL),
            timestamp=data.get("timestamp", ""),
            review_decision=ReviewDecision(data.get("review_decision", "pending")),
            reviewer_notes=data.get("reviewer_notes"),
        )


# =============================================================================
# Role B: Explicit Invariant Extraction
# =============================================================================


@dataclass
class EnrichedInvariant:
    """
    LLM-extracted invariant from explicit sources.
    
    Purpose: Surface important rules already stated in code or docs
    to reduce human scanning effort.
    
    Allowed Sources:
    - Docstrings
    - Comments with markers (@invariant, NOTE:, WARNING:)
    - README fragments (if included)
    
    FORBIDDEN: Inferring invariants from logic.
    
    Attributes:
        invariant_id: Unique identifier.
        invariant_text: The extracted invariant text.
        source_file: File where invariant was found.
        source_line: Line number (if known).
        source_type: Type of source (docstring, comment, etc.).
        source_quote: Exact quote from source.
        classification: EXPLICIT or UNCERTAIN.
        confidence: Confidence level.
        llm_label: Marker indicating LLM-generated.
        timestamp: When enrichment was generated.
        review_decision: Human review status.
        reviewer_notes: Human reviewer notes.
    """
    
    invariant_id: str
    invariant_text: str
    source_file: str
    source_line: Optional[int]
    source_type: str  # "docstring", "comment", "readme", "marker"
    source_quote: str
    classification: InvariantClassification
    confidence: EnrichmentConfidence
    llm_label: str = LLM_ENRICHMENT_LABEL
    timestamp: str = ""
    review_decision: ReviewDecision = ReviewDecision.PENDING
    reviewer_notes: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def validate(self) -> List[EnrichmentIssue]:
        """
        Validate the enrichment.
        
        Returns:
            List of validation issues (empty if valid).
        """
        issues = []
        
        # Check invariant text length
        if len(self.invariant_text) > MAX_INVARIANT_TEXT_CHARS:
            issues.append(
                EnrichmentIssue(
                    issue_type=EnrichmentIssueType.OUTPUT_TOO_VERBOSE,
                    message=f"Invariant text exceeds {MAX_INVARIANT_TEXT_CHARS} chars",
                    artifact_id=self.invariant_id,
                    details={"actual_length": len(self.invariant_text)},
                )
            )
        
        # Source quote must be present for explicit invariants
        if self.classification == InvariantClassification.EXPLICIT and not self.source_quote:
            issues.append(
                EnrichmentIssue(
                    issue_type=EnrichmentIssueType.VALIDATION_ERROR,
                    message="EXPLICIT invariant must have source quote",
                    artifact_id=self.invariant_id,
                )
            )
        
        # Check LLM label is present
        if self.llm_label != LLM_ENRICHMENT_LABEL:
            issues.append(
                EnrichmentIssue(
                    issue_type=EnrichmentIssueType.VALIDATION_ERROR,
                    message="Missing or incorrect LLM enrichment label",
                    artifact_id=self.invariant_id,
                )
            )
        
        # Valid source types
        valid_source_types = {"docstring", "comment", "readme", "marker"}
        if self.source_type not in valid_source_types:
            issues.append(
                EnrichmentIssue(
                    issue_type=EnrichmentIssueType.VALIDATION_ERROR,
                    message=f"Invalid source_type: {self.source_type}",
                    artifact_id=self.invariant_id,
                    details={"valid_types": list(valid_source_types)},
                )
            )
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "invariant_id": self.invariant_id,
            "invariant_text": self.invariant_text,
            "source_file": self.source_file,
            "source_line": self.source_line,
            "source_type": self.source_type,
            "source_quote": self.source_quote,
            "classification": self.classification.value,
            "confidence": self.confidence.value,
            "llm_label": self.llm_label,
            "timestamp": self.timestamp,
            "review_decision": self.review_decision.value,
            "reviewer_notes": self.reviewer_notes,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnrichedInvariant":
        """Create from dictionary."""
        return cls(
            invariant_id=data["invariant_id"],
            invariant_text=data["invariant_text"],
            source_file=data["source_file"],
            source_line=data.get("source_line"),
            source_type=data["source_type"],
            source_quote=data["source_quote"],
            classification=InvariantClassification(data["classification"]),
            confidence=EnrichmentConfidence(data["confidence"]),
            llm_label=data.get("llm_label", LLM_ENRICHMENT_LABEL),
            timestamp=data.get("timestamp", ""),
            review_decision=ReviewDecision(data.get("review_decision", "pending")),
            reviewer_notes=data.get("reviewer_notes"),
        )


# =============================================================================
# Enrichment Result
# =============================================================================


@dataclass
class EnrichmentResult:
    """
    Result of LLM enrichment processing.
    
    Contains all enrichment artifacts awaiting human review.
    NOTHING is written to Canon until approved.
    
    Attributes:
        ingestion_version_hash: Hash of ingestion result being enriched.
        component_labels: Enriched component labels.
        invariants: Enriched invariants.
        issues: Issues encountered during enrichment.
        llm_model: LLM model used for enrichment.
        timestamp: When enrichment was performed.
        total_llm_calls: Number of LLM API calls made.
        total_input_tokens: Estimated input tokens used.
        total_output_tokens: Estimated output tokens used.
    """
    
    ingestion_version_hash: str
    component_labels: List[EnrichedComponentLabel] = field(default_factory=list)
    invariants: List[EnrichedInvariant] = field(default_factory=list)
    issues: List[EnrichmentIssue] = field(default_factory=list)
    llm_model: str = ""
    timestamp: str = ""
    total_llm_calls: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    
    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    @property
    def has_enrichments(self) -> bool:
        """Check if any enrichments were produced."""
        return len(self.component_labels) > 0 or len(self.invariants) > 0
    
    @property
    def has_issues(self) -> bool:
        """Check if any issues were encountered."""
        return len(self.issues) > 0
    
    @property
    def pending_review_count(self) -> int:
        """Count of enrichments pending review."""
        count = sum(
            1 for label in self.component_labels
            if label.review_decision == ReviewDecision.PENDING
        )
        count += sum(
            1 for inv in self.invariants
            if inv.review_decision == ReviewDecision.PENDING
        )
        return count
    
    @property
    def approved_count(self) -> int:
        """Count of approved enrichments."""
        count = sum(
            1 for label in self.component_labels
            if label.review_decision in (ReviewDecision.APPROVED, ReviewDecision.EDITED)
        )
        count += sum(
            1 for inv in self.invariants
            if inv.review_decision in (ReviewDecision.APPROVED, ReviewDecision.EDITED)
        )
        return count
    
    def get_by_confidence(
        self,
        confidence: EnrichmentConfidence,
    ) -> tuple[List[EnrichedComponentLabel], List[EnrichedInvariant]]:
        """
        Get enrichments by confidence level.
        
        Args:
            confidence: Confidence level to filter by.
            
        Returns:
            Tuple of (component_labels, invariants) matching confidence.
        """
        labels = [l for l in self.component_labels if l.confidence == confidence]
        invs = [i for i in self.invariants if i.confidence == confidence]
        return labels, invs
    
    def validate_all(self) -> List[EnrichmentIssue]:
        """
        Validate all enrichments.
        
        Returns:
            List of all validation issues.
        """
        all_issues = []
        
        for label in self.component_labels:
            all_issues.extend(label.validate())
        
        for inv in self.invariants:
            all_issues.extend(inv.validate())
        
        return all_issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "ingestion_version_hash": self.ingestion_version_hash,
            "component_labels": [l.to_dict() for l in self.component_labels],
            "invariants": [i.to_dict() for i in self.invariants],
            "issues": [i.to_dict() for i in self.issues],
            "llm_model": self.llm_model,
            "timestamp": self.timestamp,
            "total_llm_calls": self.total_llm_calls,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnrichmentResult":
        """Create from dictionary."""
        return cls(
            ingestion_version_hash=data["ingestion_version_hash"],
            component_labels=[
                EnrichedComponentLabel.from_dict(l)
                for l in data.get("component_labels", [])
            ],
            invariants=[
                EnrichedInvariant.from_dict(i)
                for i in data.get("invariants", [])
            ],
            issues=[
                EnrichmentIssue.from_dict(i)
                for i in data.get("issues", [])
            ],
            llm_model=data.get("llm_model", ""),
            timestamp=data.get("timestamp", ""),
            total_llm_calls=data.get("total_llm_calls", 0),
            total_input_tokens=data.get("total_input_tokens", 0),
            total_output_tokens=data.get("total_output_tokens", 0),
        )


# =============================================================================
# Review Support
# =============================================================================


@dataclass
class EnrichmentReviewItem:
    """
    A single item for human review.
    
    Provides context for reviewer to make decision.
    
    Attributes:
        item_id: ID of the enrichment item.
        item_type: Type (component_label or invariant).
        enrichment: The enrichment data.
        source_artifact_summary: Summary of source artifact.
        existing_canon_value: Current Canon value (if any).
        diff_preview: Preview of what would change.
    """
    
    item_id: str
    item_type: str  # "component_label" or "invariant"
    enrichment: Dict[str, Any]
    source_artifact_summary: str
    existing_canon_value: Optional[str] = None
    diff_preview: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "item_id": self.item_id,
            "item_type": self.item_type,
            "enrichment": self.enrichment,
            "source_artifact_summary": self.source_artifact_summary,
            "existing_canon_value": self.existing_canon_value,
            "diff_preview": self.diff_preview,
        }


def prepare_for_review(result: EnrichmentResult) -> List[EnrichmentReviewItem]:
    """
    Prepare enrichment result for human review.
    
    Args:
        result: Enrichment result to prepare.
        
    Returns:
        List of review items.
    """
    items = []
    
    for label in result.component_labels:
        if label.review_decision == ReviewDecision.PENDING:
            items.append(
                EnrichmentReviewItem(
                    item_id=label.component_id,
                    item_type="component_label",
                    enrichment=label.to_dict(),
                    source_artifact_summary=f"Component: {label.component_path}",
                    diff_preview=_format_label_diff(label),
                )
            )
    
    for inv in result.invariants:
        if inv.review_decision == ReviewDecision.PENDING:
            items.append(
                EnrichmentReviewItem(
                    item_id=inv.invariant_id,
                    item_type="invariant",
                    enrichment=inv.to_dict(),
                    source_artifact_summary=f"Source: {inv.source_file}:{inv.source_line or '?'}",
                    diff_preview=_format_invariant_diff(inv),
                )
            )
    
    return items


def _format_label_diff(label: EnrichedComponentLabel) -> str:
    """Format a component label as a diff preview."""
    lines = [
        f"{LLM_ENRICHMENT_LABEL}",
        f"Component: {label.component_path}",
        f"+ Label: {label.responsibility_label}",
        f"+ Description: {label.description}",
        f"  Confidence: {label.confidence.value.upper()}",
    ]
    
    if label.assumptions:
        lines.append(f"  Assumptions: {', '.join(label.assumptions)}")
    
    return "\n".join(lines)


def _format_invariant_diff(inv: EnrichedInvariant) -> str:
    """Format an invariant as a diff preview."""
    lines = [
        f"{LLM_ENRICHMENT_LABEL}",
        f"Source: {inv.source_file}:{inv.source_line or '?'}",
        f"+ Invariant: {inv.invariant_text}",
        f"  Classification: {inv.classification.value.upper()}",
        f"  Confidence: {inv.confidence.value.upper()}",
        f'  Quote: "{inv.source_quote[:100]}..."' if len(inv.source_quote) > 100 else f'  Quote: "{inv.source_quote}"',
    ]
    
    return "\n".join(lines)
