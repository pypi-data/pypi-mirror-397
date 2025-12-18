"""
Strategic Review Models.

This module defines the data models for LLM-backed strategic review.
All models are ADVISORY ONLY - they inform human decisions but never authorize.

CORE PRINCIPLES (ABSOLUTE):
1. Recommendation ≠ Decision
2. Risk analysis ≠ Approval
3. LLM output is advisory only
4. Human authority is final
5. Canon and plans are read-only
6. No autonomy, no retries, no escalation

Any violation of these principles is a HARD FAILURE.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import hashlib


# =============================================================================
# Constants
# =============================================================================


STRATEGIC_REVIEW_LABEL = "[AI STRATEGIC REVIEW – NOT A DECISION]"
"""All strategic review outputs MUST include this label."""


# =============================================================================
# Severity and Confidence Enums
# =============================================================================


class RiskSeverity(str, Enum):
    """
    Severity level for identified risks.
    
    These are QUALITATIVE assessments to avoid false precision.
    """
    
    LOW = "low"           # Minor concern, unlikely to cause issues
    MEDIUM = "medium"     # Moderate concern, should be reviewed
    HIGH = "high"         # Significant concern, requires attention


class ConfidenceLevel(str, Enum):
    """
    Confidence level for strategic assessments.
    
    Explicitly qualitative to prevent over-confidence.
    """
    
    HIGH = "high"         # Strong evidence supports the assessment
    MEDIUM = "medium"     # Some evidence, but uncertainty exists
    LOW = "low"           # Limited evidence, high uncertainty
    UNKNOWN = "unknown"   # Unable to assess confidence


class RiskCategory(str, Enum):
    """
    Categories of strategic risks.
    
    Used to classify risks for human review.
    """
    
    SAFETY = "safety"                   # Could cause harm or data loss
    SECURITY = "security"               # Security vulnerabilities
    CORRECTNESS = "correctness"         # May produce incorrect results
    PERFORMANCE = "performance"         # Performance degradation
    ARCHITECTURAL = "architectural"     # Violates architectural principles
    CONSTRAINT = "constraint"           # Violates user constraints
    SCOPE = "scope"                     # Scope creep or wrong targets
    DEPENDENCY = "dependency"           # Dependency issues
    REVERSIBILITY = "reversibility"     # Hard to undo if wrong
    UNKNOWN = "unknown"                 # Unclassified risk


# =============================================================================
# Evidence Models
# =============================================================================


@dataclass
class EvidenceReference:
    """
    Reference to evidence supporting a risk or concern.
    
    Evidence MUST be cited; unsupported claims are invalid.
    
    Attributes:
        source_type: Type of evidence source.
        source_id: ID of the source artifact.
        excerpt: Relevant excerpt or summary.
        confidence: How confident we are in this evidence.
    """
    
    source_type: str  # "task", "validation", "dry_run", "canon", "constraint"
    source_id: str
    excerpt: str
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source_type": self.source_type,
            "source_id": self.source_id,
            "excerpt": self.excerpt,
            "confidence": self.confidence.value,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvidenceReference":
        """Create from dictionary."""
        return cls(
            source_type=data.get("source_type", "unknown"),
            source_id=data.get("source_id", ""),
            excerpt=data.get("excerpt", ""),
            confidence=ConfidenceLevel(data.get("confidence", "medium")),
        )


# =============================================================================
# Risk, Tradeoff, and Concern Models
# =============================================================================


@dataclass
class StrategicRisk:
    """
    A risk identified during strategic review.
    
    Risks are potential problems that humans should consider.
    They are NOT blocking decisions.
    
    Attributes:
        id: Unique identifier for this risk.
        category: Category of risk.
        description: Human-readable description.
        severity: Severity level (qualitative).
        evidence: References supporting this risk.
        mitigation_hint: Optional suggestion for mitigation.
        confidence: Confidence in this assessment.
    """
    
    id: str
    category: RiskCategory
    description: str
    severity: RiskSeverity
    evidence: List[EvidenceReference] = field(default_factory=list)
    mitigation_hint: Optional[str] = None
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    
    def validate(self) -> List[str]:
        """
        Validate this risk assessment.
        
        Returns:
            List of validation errors (empty if valid).
        """
        errors = []
        
        if not self.id:
            errors.append("Risk ID is required")
        if not self.description:
            errors.append("Risk description is required")
        if not self.evidence:
            errors.append("Risk must have at least one evidence reference")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "category": self.category.value,
            "description": self.description,
            "severity": self.severity.value,
            "evidence": [e.to_dict() for e in self.evidence],
            "mitigation_hint": self.mitigation_hint,
            "confidence": self.confidence.value,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StrategicRisk":
        """Create from dictionary."""
        return cls(
            id=data.get("id", ""),
            category=RiskCategory(data.get("category", "unknown")),
            description=data.get("description", ""),
            severity=RiskSeverity(data.get("severity", "medium")),
            evidence=[
                EvidenceReference.from_dict(e)
                for e in data.get("evidence", [])
            ],
            mitigation_hint=data.get("mitigation_hint"),
            confidence=ConfidenceLevel(data.get("confidence", "medium")),
        )


@dataclass
class StrategicTradeoff:
    """
    A tradeoff identified during strategic review.
    
    Tradeoffs represent competing concerns where one choice
    benefits some aspects while harming others.
    
    Attributes:
        id: Unique identifier.
        description: Human-readable description.
        impacted_components: Components affected by this tradeoff.
        upside: Positive aspects of the current choice.
        downside: Negative aspects of the current choice.
        confidence: Confidence in this assessment.
    """
    
    id: str
    description: str
    impacted_components: List[str] = field(default_factory=list)
    upside: str = ""
    downside: str = ""
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    
    def validate(self) -> List[str]:
        """
        Validate this tradeoff.
        
        Returns:
            List of validation errors (empty if valid).
        """
        errors = []
        
        if not self.id:
            errors.append("Tradeoff ID is required")
        if not self.description:
            errors.append("Tradeoff description is required")
        if not self.upside and not self.downside:
            errors.append("Tradeoff must specify upside or downside")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "impacted_components": self.impacted_components,
            "upside": self.upside,
            "downside": self.downside,
            "confidence": self.confidence.value,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StrategicTradeoff":
        """Create from dictionary."""
        return cls(
            id=data.get("id", ""),
            description=data.get("description", ""),
            impacted_components=data.get("impacted_components", []),
            upside=data.get("upside", ""),
            downside=data.get("downside", ""),
            confidence=ConfidenceLevel(data.get("confidence", "medium")),
        )


@dataclass
class StrategicConcern:
    """
    A concern or question for human consideration.
    
    Concerns are less specific than risks - they represent
    areas where human judgment is needed.
    
    Attributes:
        id: Unique identifier.
        description: Human-readable description.
        suggested_questions: Questions humans should consider.
        confidence: Confidence in this concern being valid.
    """
    
    id: str
    description: str
    suggested_questions: List[str] = field(default_factory=list)
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    
    def validate(self) -> List[str]:
        """
        Validate this concern.
        
        Returns:
            List of validation errors (empty if valid).
        """
        errors = []
        
        if not self.id:
            errors.append("Concern ID is required")
        if not self.description:
            errors.append("Concern description is required")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "suggested_questions": self.suggested_questions,
            "confidence": self.confidence.value,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StrategicConcern":
        """Create from dictionary."""
        return cls(
            id=data.get("id", ""),
            description=data.get("description", ""),
            suggested_questions=data.get("suggested_questions", []),
            confidence=ConfidenceLevel(data.get("confidence", "medium")),
        )


# =============================================================================
# Summary and Result Models
# =============================================================================


class OverallRiskPosture(str, Enum):
    """
    Overall risk posture assessment.
    
    A qualitative summary for human review.
    """
    
    LOW = "low"               # Few or no significant risks
    MODERATE = "moderate"     # Some risks requiring attention
    HIGH = "high"             # Significant risks present
    CRITICAL = "critical"     # Critical risks that demand attention
    UNKNOWN = "unknown"       # Unable to assess


@dataclass
class StrategicReviewSummary:
    """
    Summary of the strategic review.
    
    Provides a high-level overview for quick human review.
    
    Attributes:
        overall_risk_posture: Qualitative risk assessment.
        key_recommendations: Top recommendations for humans.
        proceed_confidence: Confidence that proceeding is safe.
        requires_human_attention: Whether specific attention needed.
        attention_areas: Specific areas needing attention.
    """
    
    overall_risk_posture: OverallRiskPosture
    key_recommendations: List[str] = field(default_factory=list)
    proceed_confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    requires_human_attention: bool = True
    attention_areas: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "overall_risk_posture": self.overall_risk_posture.value,
            "key_recommendations": self.key_recommendations,
            "proceed_confidence": self.proceed_confidence.value,
            "requires_human_attention": self.requires_human_attention,
            "attention_areas": self.attention_areas,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StrategicReviewSummary":
        """Create from dictionary."""
        return cls(
            overall_risk_posture=OverallRiskPosture(
                data.get("overall_risk_posture", "unknown")
            ),
            key_recommendations=data.get("key_recommendations", []),
            proceed_confidence=ConfidenceLevel(
                data.get("proceed_confidence", "medium")
            ),
            requires_human_attention=data.get("requires_human_attention", True),
            attention_areas=data.get("attention_areas", []),
        )


@dataclass
class LLMStrategicReviewResult:
    """
    Complete result from LLM strategic review.
    
    This is ADVISORY ONLY - it informs but never authorizes.
    
    Attributes:
        review_id: Unique identifier for this review.
        advisory_label: MUST be STRATEGIC_REVIEW_LABEL.
        risks: Identified risks.
        tradeoffs: Identified tradeoffs.
        concerns: Identified concerns.
        summary: Review summary.
        confidence: Overall confidence in the review.
        timestamp: When the review was performed.
        is_valid: Whether the review passed validation.
        validation_errors: Errors if invalid.
        raw_response: Raw LLM response (for debugging).
    """
    
    review_id: str
    advisory_label: str = STRATEGIC_REVIEW_LABEL
    risks: List[StrategicRisk] = field(default_factory=list)
    tradeoffs: List[StrategicTradeoff] = field(default_factory=list)
    concerns: List[StrategicConcern] = field(default_factory=list)
    summary: Optional[StrategicReviewSummary] = None
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    timestamp: str = ""
    is_valid: bool = True
    validation_errors: List[str] = field(default_factory=list)
    raw_response: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Set timestamp and validate label."""
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        
        # CRITICAL: Enforce advisory label
        if self.advisory_label != STRATEGIC_REVIEW_LABEL:
            self.advisory_label = STRATEGIC_REVIEW_LABEL
    
    def validate(self) -> List[str]:
        """
        Validate the review result.
        
        Returns:
            List of validation errors (empty if valid).
        """
        errors = []
        
        # Check advisory label
        if self.advisory_label != STRATEGIC_REVIEW_LABEL:
            errors.append("Advisory label must be present and correct")
        
        # Check review ID
        if not self.review_id:
            errors.append("Review ID is required")
        
        # Validate risks
        for risk in self.risks:
            risk_errors = risk.validate()
            errors.extend([f"Risk '{risk.id}': {e}" for e in risk_errors])
        
        # Validate tradeoffs
        for tradeoff in self.tradeoffs:
            tradeoff_errors = tradeoff.validate()
            errors.extend([f"Tradeoff '{tradeoff.id}': {e}" for e in tradeoff_errors])
        
        # Validate concerns
        for concern in self.concerns:
            concern_errors = concern.validate()
            errors.extend([f"Concern '{concern.id}': {e}" for e in concern_errors])
        
        return errors
    
    def has_high_severity_risks(self) -> bool:
        """Check if any HIGH severity risks exist."""
        return any(r.severity == RiskSeverity.HIGH for r in self.risks)
    
    def get_risks_by_severity(self, severity: RiskSeverity) -> List[StrategicRisk]:
        """Get risks filtered by severity."""
        return [r for r in self.risks if r.severity == severity]
    
    def get_risks_by_category(self, category: RiskCategory) -> List[StrategicRisk]:
        """Get risks filtered by category."""
        return [r for r in self.risks if r.category == category]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "review_id": self.review_id,
            "advisory_label": self.advisory_label,
            "risks": [r.to_dict() for r in self.risks],
            "tradeoffs": [t.to_dict() for t in self.tradeoffs],
            "concerns": [c.to_dict() for c in self.concerns],
            "summary": self.summary.to_dict() if self.summary else None,
            "confidence": self.confidence.value,
            "timestamp": self.timestamp,
            "is_valid": self.is_valid,
            "validation_errors": self.validation_errors,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LLMStrategicReviewResult":
        """Create from dictionary."""
        summary_data = data.get("summary")
        return cls(
            review_id=data.get("review_id", ""),
            advisory_label=data.get("advisory_label", STRATEGIC_REVIEW_LABEL),
            risks=[StrategicRisk.from_dict(r) for r in data.get("risks", [])],
            tradeoffs=[
                StrategicTradeoff.from_dict(t) for t in data.get("tradeoffs", [])
            ],
            concerns=[
                StrategicConcern.from_dict(c) for c in data.get("concerns", [])
            ],
            summary=(
                StrategicReviewSummary.from_dict(summary_data)
                if summary_data else None
            ),
            confidence=ConfidenceLevel(data.get("confidence", "medium")),
            timestamp=data.get("timestamp", ""),
            is_valid=data.get("is_valid", True),
            validation_errors=data.get("validation_errors", []),
        )
    
    def compute_hash(self) -> str:
        """
        Compute a hash of the review for tracking.
        
        Returns:
            SHA-256 hash of the review content.
        """
        content = f"{self.review_id}:{len(self.risks)}:{len(self.tradeoffs)}"
        content += f":{self.confidence.value}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


# =============================================================================
# Empty/Failed Review Factory
# =============================================================================


def create_empty_review(
    review_id: str,
    reason: str = "No AI review available",
) -> LLMStrategicReviewResult:
    """
    Create an empty review result when AI review is unavailable.
    
    The system proceeds to human decision without AI input.
    
    Args:
        review_id: ID for the review.
        reason: Reason why review is empty.
        
    Returns:
        An empty but valid review result.
    """
    return LLMStrategicReviewResult(
        review_id=review_id,
        advisory_label=STRATEGIC_REVIEW_LABEL,
        risks=[],
        tradeoffs=[],
        concerns=[
            StrategicConcern(
                id="no-ai-review",
                description=f"AI strategic review unavailable: {reason}",
                suggested_questions=[
                    "Proceed with manual review of the plan",
                    "Consider risks based on your domain knowledge",
                ],
                confidence=ConfidenceLevel.UNKNOWN,
            )
        ],
        summary=StrategicReviewSummary(
            overall_risk_posture=OverallRiskPosture.UNKNOWN,
            key_recommendations=[
                "AI review unavailable - human judgment required",
            ],
            proceed_confidence=ConfidenceLevel.UNKNOWN,
            requires_human_attention=True,
            attention_areas=["Full manual review required"],
        ),
        confidence=ConfidenceLevel.UNKNOWN,
        is_valid=True,
    )


def create_failed_review(
    review_id: str,
    error: str,
    raw_response: Optional[str] = None,
) -> LLMStrategicReviewResult:
    """
    Create a failed review result when AI review fails.
    
    The system proceeds to human decision without AI input.
    
    Args:
        review_id: ID for the review.
        error: Error message describing the failure.
        raw_response: Raw LLM response if available.
        
    Returns:
        A failed but valid review result.
    """
    return LLMStrategicReviewResult(
        review_id=review_id,
        advisory_label=STRATEGIC_REVIEW_LABEL,
        risks=[],
        tradeoffs=[],
        concerns=[
            StrategicConcern(
                id="review-failed",
                description=f"AI strategic review failed: {error}",
                suggested_questions=[
                    "Review the plan manually",
                    "Consider whether to retry or proceed without AI input",
                ],
                confidence=ConfidenceLevel.UNKNOWN,
            )
        ],
        summary=StrategicReviewSummary(
            overall_risk_posture=OverallRiskPosture.UNKNOWN,
            key_recommendations=[
                "AI review failed - proceed with human judgment",
            ],
            proceed_confidence=ConfidenceLevel.UNKNOWN,
            requires_human_attention=True,
            attention_areas=["Full manual review required due to AI failure"],
        ),
        confidence=ConfidenceLevel.UNKNOWN,
        is_valid=True,
        validation_errors=[error],
        raw_response=raw_response,
    )


# =============================================================================
# Validation Functions
# =============================================================================


def validate_review_is_advisory(result: LLMStrategicReviewResult) -> bool:
    """
    Validate that the review is properly labeled as advisory.
    
    Args:
        result: The review result to validate.
        
    Returns:
        True if properly labeled as advisory.
    """
    return result.advisory_label == STRATEGIC_REVIEW_LABEL


def validate_risks_have_evidence(result: LLMStrategicReviewResult) -> List[str]:
    """
    Validate that all risks have evidence.
    
    Args:
        result: The review result to validate.
        
    Returns:
        List of risks missing evidence.
    """
    missing = []
    for risk in result.risks:
        if not risk.evidence:
            missing.append(risk.id)
    return missing


def validate_confidence_is_stated(result: LLMStrategicReviewResult) -> bool:
    """
    Validate that confidence level is explicitly stated.
    
    Args:
        result: The review result to validate.
        
    Returns:
        True if confidence is not UNKNOWN.
    """
    return result.confidence != ConfidenceLevel.UNKNOWN
