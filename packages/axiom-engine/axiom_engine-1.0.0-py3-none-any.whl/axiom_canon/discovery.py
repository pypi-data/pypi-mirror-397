"""
Discovery Models for Governed Documentation.

This module defines models for the GOVERNED DISCOVERY mechanism where:
- Tactical Layer decides WHAT to analyze
- Executors gather EVIDENCE only
- LLMs infer PROVISIONAL meaning
- Humans ratify promotion into Canon
- Documentation becomes a derived, regenerable artifact

CORE PRINCIPLES (ABSOLUTE):
1. Discovery ≠ Truth
2. Inference ≠ Canon
3. Evidence precedes interpretation
4. Human approval is mandatory
5. Executors are read-only
6. LLMs have no authority
7. Canon never auto-mutates

Any violation of these principles is a HARD FAILURE.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import hashlib
import json


# =============================================================================
# Task Type Extension
# =============================================================================


class TaskType(str, Enum):
    """
    Type of task in a TaskGraph.
    
    EXECUTION: Traditional task that can invoke Forge backends.
    DISCOVERY: Read-only analysis task that gathers evidence only.
    """
    
    EXECUTION = "execution"
    DISCOVERY = "discovery"


class DiscoveryTaskType(str, Enum):
    """
    Specific types of discovery tasks.
    
    These define what kind of analysis is being performed.
    """
    
    COMPONENT_ANALYSIS = "component_analysis"     # Analyze a component's purpose
    DEPENDENCY_ANALYSIS = "dependency_analysis"   # Analyze dependency relationships
    INVARIANT_DISCOVERY = "invariant_discovery"   # Find implicit invariants
    PATTERN_RECOGNITION = "pattern_recognition"   # Identify design patterns
    BEHAVIOR_INFERENCE = "behavior_inference"     # Infer behavioral contracts
    DOCUMENTATION_GAP = "documentation_gap"       # Identify missing docs


# =============================================================================
# Discovery Task Models
# =============================================================================


@dataclass
class DiscoveryScope:
    """
    Defines the scope boundaries for a discovery task.
    
    Hard limits on what can be analyzed to prevent runaway LLM usage.
    
    Attributes:
        file_paths: Specific files to analyze (absolute paths).
        max_files: Maximum number of files that can be analyzed.
        max_tokens_per_file: Maximum tokens to read per file.
        max_total_tokens: Maximum total tokens for entire task.
        include_patterns: Glob patterns for files to include.
        exclude_patterns: Glob patterns for files to exclude.
    """
    
    file_paths: List[str] = field(default_factory=list)
    max_files: int = 10
    max_tokens_per_file: int = 2000
    max_total_tokens: int = 10000
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    
    def validate(self) -> List[str]:
        """
        Validate scope constraints.
        
        Returns:
            List of validation errors (empty if valid).
        """
        errors = []
        
        if self.max_files <= 0:
            errors.append("max_files must be positive")
        if self.max_files > 50:
            errors.append("max_files cannot exceed 50")
        if self.max_tokens_per_file <= 0:
            errors.append("max_tokens_per_file must be positive")
        if self.max_tokens_per_file > 10000:
            errors.append("max_tokens_per_file cannot exceed 10000")
        if self.max_total_tokens <= 0:
            errors.append("max_total_tokens must be positive")
        if self.max_total_tokens > 50000:
            errors.append("max_total_tokens cannot exceed 50000")
        
        return errors


@dataclass
class DiscoveryTask:
    """
    A read-only analysis task for gathering evidence.
    
    DISCOVERY tasks:
    - Cannot invoke Forge execution backends
    - Cannot execute shell or Playwright actions
    - Cannot mutate files or Canon
    - Produce DiscoveryResults, not TaskExecutionResults
    
    Attributes:
        id: Unique task identifier.
        name: Human-readable task name.
        description: What this task will analyze.
        task_type: Type of discovery (component, dependency, etc.).
        scope: Scope boundaries for analysis.
        target_artifact_ids: Canon artifact IDs to analyze.
        focus_question: Specific question to answer (if any).
        timeout_seconds: Maximum execution time.
    """
    
    id: str
    name: str
    description: str
    task_type: DiscoveryTaskType
    scope: DiscoveryScope
    target_artifact_ids: List[str] = field(default_factory=list)
    focus_question: Optional[str] = None
    timeout_seconds: int = 60
    
    def validate(self) -> List[str]:
        """
        Validate task configuration.
        
        Returns:
            List of validation errors (empty if valid).
        """
        errors = []
        
        if not self.id:
            errors.append("Task id is required")
        if not self.name:
            errors.append("Task name is required")
        if not self.description:
            errors.append("Task description is required")
        
        # Validate scope
        scope_errors = self.scope.validate()
        errors.extend(scope_errors)
        
        # Timeout limits
        if self.timeout_seconds <= 0:
            errors.append("timeout_seconds must be positive")
        if self.timeout_seconds > 300:
            errors.append("timeout_seconds cannot exceed 300")
        
        return errors


@dataclass
class DiscoveryDependency:
    """
    Dependency between discovery tasks.
    """
    
    upstream_task_id: str
    downstream_task_id: str


@dataclass
class DiscoveryTaskGraph:
    """
    A DAG of discovery tasks.
    
    DISCOVERY TaskGraphs:
    - Contain ONLY discovery tasks
    - Cannot be mixed with EXECUTION tasks
    - Produce DiscoveryResults only
    - Never mutate Canon directly
    
    Attributes:
        id: Unique graph identifier.
        tasks: Mapping of task IDs to DiscoveryTasks.
        dependencies: List of task dependencies.
        intent: Human-readable intent (e.g., "Document auth subsystem").
        metadata: Additional metadata.
    """
    
    id: str
    intent: str
    tasks: Dict[str, DiscoveryTask] = field(default_factory=dict)
    dependencies: List[DiscoveryDependency] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_task(self, task: DiscoveryTask) -> None:
        """Add a discovery task to the graph."""
        self.tasks[task.id] = task
    
    def add_dependency(self, upstream_id: str, downstream_id: str) -> None:
        """Add a dependency between tasks."""
        self.dependencies.append(
            DiscoveryDependency(
                upstream_task_id=upstream_id,
                downstream_task_id=downstream_id,
            )
        )
    
    def validate(self) -> List[str]:
        """
        Validate the discovery graph.
        
        Returns:
            List of validation errors (empty if valid).
        """
        errors = []
        
        if not self.id:
            errors.append("Graph id is required")
        if not self.intent:
            errors.append("Graph intent is required")
        
        # Validate all tasks
        for task_id, task in self.tasks.items():
            task_errors = task.validate()
            for err in task_errors:
                errors.append(f"Task {task_id}: {err}")
        
        # Validate dependencies reference existing tasks
        for dep in self.dependencies:
            if dep.upstream_task_id not in self.tasks:
                errors.append(f"Dependency references unknown task: {dep.upstream_task_id}")
            if dep.downstream_task_id not in self.tasks:
                errors.append(f"Dependency references unknown task: {dep.downstream_task_id}")
        
        # Check for cycles (simple check)
        # TODO: Implement proper topological sort validation
        
        return errors
    
    def get_ready_tasks(self, completed_task_ids: set) -> List[str]:
        """
        Get task IDs ready for execution.
        
        Args:
            completed_task_ids: Set of already completed task IDs.
            
        Returns:
            List of task IDs with all dependencies satisfied.
        """
        # Find tasks with all dependencies completed
        ready = []
        
        for task_id in self.tasks:
            if task_id in completed_task_ids:
                continue
            
            # Check all upstream dependencies
            upstream_complete = True
            for dep in self.dependencies:
                if dep.downstream_task_id == task_id:
                    if dep.upstream_task_id not in completed_task_ids:
                        upstream_complete = False
                        break
            
            if upstream_complete:
                ready.append(task_id)
        
        return ready


# =============================================================================
# Evidence Models
# =============================================================================


@dataclass
class EvidenceExcerpt:
    """
    A quoted excerpt from source code or documentation.
    
    Evidence MUST be quoted exactly from source.
    No paraphrasing, no inference, no interpretation.
    
    Attributes:
        file_path: Absolute path to source file.
        start_line: Starting line number (1-indexed).
        end_line: Ending line number (inclusive).
        content: Exact quoted content.
        symbols: Symbols referenced in excerpt (function names, etc.).
    """
    
    file_path: str
    start_line: int
    end_line: int
    content: str
    symbols: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": self.file_path,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "content": self.content,
            "symbols": self.symbols,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvidenceExcerpt":
        """Create from dictionary."""
        return cls(
            file_path=data["file_path"],
            start_line=data["start_line"],
            end_line=data["end_line"],
            content=data["content"],
            symbols=data.get("symbols", []),
        )


@dataclass
class InferenceEvidence:
    """
    Evidence supporting an inference.
    
    All inferences MUST cite evidence.
    Evidence precedes interpretation.
    
    Attributes:
        excerpts: Quoted excerpts from source.
        referenced_artifacts: Canon artifact IDs referenced.
        observations: Factual observations (not interpretations).
        analysis_context: Context provided to LLM for analysis.
    """
    
    excerpts: List[EvidenceExcerpt] = field(default_factory=list)
    referenced_artifacts: List[str] = field(default_factory=list)
    observations: List[str] = field(default_factory=list)
    analysis_context: str = ""
    
    def has_evidence(self) -> bool:
        """Check if any evidence is present."""
        return (
            len(self.excerpts) > 0 or
            len(self.observations) > 0
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "excerpts": [e.to_dict() for e in self.excerpts],
            "referenced_artifacts": self.referenced_artifacts,
            "observations": self.observations,
            "analysis_context": self.analysis_context,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InferenceEvidence":
        """Create from dictionary."""
        return cls(
            excerpts=[
                EvidenceExcerpt.from_dict(e) for e in data.get("excerpts", [])
            ],
            referenced_artifacts=data.get("referenced_artifacts", []),
            observations=data.get("observations", []),
            analysis_context=data.get("analysis_context", ""),
        )


# =============================================================================
# Inference Models
# =============================================================================


class InferenceConfidence(str, Enum):
    """
    Confidence level of an inference.
    
    Used to indicate how certain the LLM is about the inference.
    """
    
    HIGH = "high"       # Strong evidence, clear meaning
    MEDIUM = "medium"   # Reasonable inference, some uncertainty
    LOW = "low"         # Weak evidence, speculative
    UNKNOWN = "unknown" # Could not determine


class InferenceStatus(str, Enum):
    """
    Status of an inferred annotation.
    
    PROPOSED: Default state, awaiting human review.
    ACCEPTED: Human approved, can be promoted to Canon.
    REJECTED: Human rejected, will not affect Canon.
    """
    
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class InferenceType(str, Enum):
    """
    Type of inference being made.
    """
    
    COMPONENT_PURPOSE = "component_purpose"     # What a component does
    FUNCTION_BEHAVIOR = "function_behavior"     # What a function does
    DEPENDENCY_REASON = "dependency_reason"     # Why a dependency exists
    INVARIANT = "invariant"                     # Implicit invariant
    DESIGN_PATTERN = "design_pattern"           # Design pattern used
    ARCHITECTURAL_DECISION = "arch_decision"    # Architectural choice
    API_CONTRACT = "api_contract"               # API behavioral contract


# Label for all inferred content
INFERENCE_LABEL = "[INFERRED – REQUIRES HUMAN APPROVAL]"


@dataclass
class InferredAnnotation:
    """
    A provisional annotation inferred by LLM analysis.
    
    CRITICAL RULES:
    - All inferred knowledge is PROPOSED by default
    - All inferences must cite evidence
    - Confidence must be explicit
    - Provenance must be tracked
    - InferredAnnotations are NOT Canon truth by default
    
    Attributes:
        id: Unique annotation identifier.
        inference_type: Type of inference.
        content: The inferred content/description.
        evidence: Supporting evidence.
        confidence: Confidence level.
        status: Current status (PROPOSED, ACCEPTED, REJECTED).
        target_artifact_id: Canon artifact this annotates.
        target_artifact_type: Type of Canon artifact.
        provenance: Tracking info (task ID, executor ID, etc.).
        review_notes: Human reviewer notes.
        timestamp: When inference was made.
        inference_label: Marker indicating this is inferred.
    """
    
    id: str
    inference_type: InferenceType
    content: str
    evidence: InferenceEvidence
    confidence: InferenceConfidence
    target_artifact_id: str
    target_artifact_type: str  # "component", "module", "function", etc.
    status: InferenceStatus = InferenceStatus.PROPOSED
    provenance: Dict[str, str] = field(default_factory=dict)
    review_notes: Optional[str] = None
    timestamp: str = ""
    inference_label: str = INFERENCE_LABEL
    
    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def validate(self) -> List[str]:
        """
        Validate the annotation.
        
        Returns:
            List of validation errors (empty if valid).
        """
        errors = []
        
        if not self.id:
            errors.append("Annotation id is required")
        if not self.content:
            errors.append("Annotation content is required")
        if not self.target_artifact_id:
            errors.append("Target artifact id is required")
        
        # Evidence is required
        if not self.evidence.has_evidence():
            errors.append("Evidence is required for all inferences")
        
        # Confidence must not be unknown for proposed annotations
        if self.confidence == InferenceConfidence.UNKNOWN:
            errors.append("Confidence cannot be UNKNOWN")
        
        # Label must be present
        if self.inference_label != INFERENCE_LABEL:
            errors.append("Inference label must be present")
        
        # Provenance must include task_id
        if "task_id" not in self.provenance:
            errors.append("Provenance must include task_id")
        
        return errors
    
    @property
    def is_promotable(self) -> bool:
        """Check if annotation can be promoted to Canon."""
        return self.status == InferenceStatus.ACCEPTED
    
    def compute_hash(self) -> str:
        """Compute content hash for diffing."""
        content = {
            "inference_type": self.inference_type.value,
            "content": self.content,
            "target_artifact_id": self.target_artifact_id,
            "confidence": self.confidence.value,
        }
        return hashlib.sha256(
            json.dumps(content, sort_keys=True).encode()
        ).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "inference_type": self.inference_type.value,
            "content": self.content,
            "evidence": self.evidence.to_dict(),
            "confidence": self.confidence.value,
            "target_artifact_id": self.target_artifact_id,
            "target_artifact_type": self.target_artifact_type,
            "status": self.status.value,
            "provenance": self.provenance,
            "review_notes": self.review_notes,
            "timestamp": self.timestamp,
            "inference_label": self.inference_label,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InferredAnnotation":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            inference_type=InferenceType(data["inference_type"]),
            content=data["content"],
            evidence=InferenceEvidence.from_dict(data["evidence"]),
            confidence=InferenceConfidence(data["confidence"]),
            target_artifact_id=data["target_artifact_id"],
            target_artifact_type=data["target_artifact_type"],
            status=InferenceStatus(data.get("status", "proposed")),
            provenance=data.get("provenance", {}),
            review_notes=data.get("review_notes"),
            timestamp=data.get("timestamp", ""),
            inference_label=data.get("inference_label", INFERENCE_LABEL),
        )


# =============================================================================
# Discovery Result Models
# =============================================================================


@dataclass
class DiscoveryResult:
    """
    Result of a single discovery task.
    
    Contains evidence gathered and inferences proposed.
    This is the output of an LLMAnalysisExecutor.
    
    Attributes:
        task_id: ID of the discovery task.
        success: Whether the task completed successfully.
        evidence: Evidence gathered during analysis.
        annotations: Proposed inferred annotations.
        raw_llm_output: Raw LLM response (for debugging).
        token_usage: Token usage statistics.
        errors: Any errors encountered.
        duration_seconds: Time taken for analysis.
    """
    
    task_id: str
    success: bool
    evidence: InferenceEvidence = field(default_factory=InferenceEvidence)
    annotations: List[InferredAnnotation] = field(default_factory=list)
    raw_llm_output: str = ""
    token_usage: Dict[str, int] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    timestamp: str = ""
    
    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "success": self.success,
            "evidence": self.evidence.to_dict(),
            "annotations": [a.to_dict() for a in self.annotations],
            "raw_llm_output": self.raw_llm_output,
            "token_usage": self.token_usage,
            "errors": self.errors,
            "duration_seconds": self.duration_seconds,
            "timestamp": self.timestamp,
        }


@dataclass
class DiscoveryGraphResult:
    """
    Result of executing an entire discovery graph.
    
    Aggregates all task results and proposed annotations.
    
    Attributes:
        graph_id: ID of the discovery graph.
        task_results: Results for each task.
        all_annotations: All proposed annotations (pending review).
        total_evidence_excerpts: Total evidence gathered.
        total_duration_seconds: Total execution time.
        success_count: Number of successful tasks.
        failure_count: Number of failed tasks.
    """
    
    graph_id: str
    task_results: Dict[str, DiscoveryResult] = field(default_factory=dict)
    all_annotations: List[InferredAnnotation] = field(default_factory=list)
    total_evidence_excerpts: int = 0
    total_duration_seconds: float = 0.0
    success_count: int = 0
    failure_count: int = 0
    timestamp: str = ""
    
    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def add_result(self, result: DiscoveryResult) -> None:
        """Add a task result to the graph result."""
        self.task_results[result.task_id] = result
        
        if result.success:
            self.success_count += 1
        else:
            self.failure_count += 1
        
        self.total_duration_seconds += result.duration_seconds
        self.total_evidence_excerpts += len(result.evidence.excerpts)
        self.all_annotations.extend(result.annotations)
    
    @property
    def pending_review_count(self) -> int:
        """Count annotations pending review."""
        return sum(
            1 for a in self.all_annotations
            if a.status == InferenceStatus.PROPOSED
        )


# =============================================================================
# Review Models
# =============================================================================


@dataclass
class AnnotationReviewDecision:
    """
    Human review decision for an inferred annotation.
    
    Attributes:
        annotation_id: ID of the annotation being reviewed.
        decision: ACCEPT, REJECT, or require EDIT.
        edited_content: Modified content (if edited).
        reviewer_notes: Reviewer's notes.
        reviewer_id: Identifier of the reviewer.
        timestamp: When the decision was made.
    """
    
    annotation_id: str
    decision: InferenceStatus  # ACCEPTED or REJECTED
    edited_content: Optional[str] = None
    reviewer_notes: Optional[str] = None
    reviewer_id: Optional[str] = None
    timestamp: str = ""
    
    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


def apply_review_decision(
    annotation: InferredAnnotation,
    decision: AnnotationReviewDecision,
) -> InferredAnnotation:
    """
    Apply a review decision to an annotation.
    
    Args:
        annotation: The annotation to update.
        decision: The review decision.
        
    Returns:
        Updated annotation.
    """
    annotation.status = decision.decision
    annotation.review_notes = decision.reviewer_notes
    
    if decision.edited_content:
        annotation.content = decision.edited_content
    
    return annotation


def get_promotable_annotations(
    annotations: List[InferredAnnotation],
) -> List[InferredAnnotation]:
    """
    Get annotations that can be promoted to Canon.
    
    Only ACCEPTED annotations can be promoted.
    
    Args:
        annotations: List of annotations to filter.
        
    Returns:
        List of promotable annotations.
    """
    return [a for a in annotations if a.is_promotable]


# =============================================================================
# Validation Functions
# =============================================================================


def validate_discovery_task_is_read_only(task: DiscoveryTask) -> List[str]:
    """
    Validate that a discovery task is truly read-only.
    
    DISCOVERY tasks CANNOT:
    - Invoke Forge execution backends
    - Execute shell or Playwright actions
    - Mutate files or Canon
    
    Args:
        task: The discovery task to validate.
        
    Returns:
        List of validation errors (empty if valid).
    """
    errors = []
    
    # Discovery tasks should not have command fields (that's for execution)
    # This is enforced by the type itself - DiscoveryTask has no command field
    
    # Validate scope is within limits
    scope_errors = task.scope.validate()
    errors.extend(scope_errors)
    
    return errors


def validate_discovery_graph_is_pure(graph: DiscoveryTaskGraph) -> List[str]:
    """
    Validate that a discovery graph contains only discovery tasks.
    
    DISCOVERY graphs:
    - Cannot be mixed with EXECUTION tasks
    - All tasks must be read-only
    
    Args:
        graph: The discovery graph to validate.
        
    Returns:
        List of validation errors (empty if valid).
    """
    errors = []
    
    # Validate graph itself
    graph_errors = graph.validate()
    errors.extend(graph_errors)
    
    # Validate each task is read-only
    for task_id, task in graph.tasks.items():
        task_errors = validate_discovery_task_is_read_only(task)
        for err in task_errors:
            errors.append(f"Task {task_id}: {err}")
    
    return errors


def validate_annotation_has_evidence(annotation: InferredAnnotation) -> bool:
    """
    Validate that an annotation has required evidence.
    
    Args:
        annotation: The annotation to validate.
        
    Returns:
        True if annotation has evidence, False otherwise.
    """
    return annotation.evidence.has_evidence()


def validate_annotation_can_promote(annotation: InferredAnnotation) -> List[str]:
    """
    Validate that an annotation can be promoted to Canon.
    
    Promotion requirements:
    - Status must be ACCEPTED
    - Evidence must be present
    - Confidence must not be UNKNOWN
    
    Args:
        annotation: The annotation to validate.
        
    Returns:
        List of validation errors (empty if promotable).
    """
    errors = []
    
    if annotation.status != InferenceStatus.ACCEPTED:
        errors.append("Only ACCEPTED annotations can be promoted")
    
    if not annotation.evidence.has_evidence():
        errors.append("Evidence is required for promotion")
    
    if annotation.confidence == InferenceConfidence.UNKNOWN:
        errors.append("UNKNOWN confidence cannot be promoted")
    
    return errors
