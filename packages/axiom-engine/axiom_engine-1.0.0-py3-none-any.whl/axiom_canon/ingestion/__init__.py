"""
Axiom Canon Ingestion Pipeline.

This package implements a deterministic, repomix-style code ingestion pipeline
that extracts STRUCTURAL UNDERSTANDING from a codebase and stores it as
CANONICAL ARTIFACTS.

This pipeline replaces "LLM reads the repo" with
"LLM reads stable, human-verified summaries."

CONSTRAINTS (ABSOLUTE):
- No LLMs in ingestion
- No code execution
- No runtime mutation of Canon
- No autonomous updates
- No inference or guessing
- No natural-language interpretation

This phase is EXTRACTION, not REASONING.

Canon is truth.
Ingestion is observation.
LLMs are guests.
"""

from axiom_canon.ingestion.models import (
    # Core summary artifacts
    ModuleSummary,
    ComponentSummary,
    APIExposureSummary,
    DependencyEdgeSummary,
    InvariantSummary,
    # Supporting types
    FunctionSignature,
    ClassSignature,
    MethodSignature,
    ParameterInfo,
    ImportInfo,
    ExportInfo,
    EntryPoint,
    ConfigBoundary,
    # Container types
    IngestionResult,
    IngestionManifest,
    # Enums
    Visibility,
    ModuleType,
    DependencyType,
    InvariantType,
)
from axiom_canon.ingestion.extractor import (
    CodeExtractor,
    PythonASTExtractor,
    ExtractionConfig,
    ExtractionError,
)
from axiom_canon.ingestion.diffing import (
    IngestionDiff,
    ArtifactChange,
    ChangeType,
    compute_diff,
    apply_diff,
)
from axiom_canon.ingestion.consumption import (
    LLMConsumptionContract,
    ChunkingStrategy,
    SummaryChunk,
    prepare_for_llm,
)
from axiom_canon.ingestion.enrichment_models import (
    # Enrichment constants
    LLM_ENRICHMENT_LABEL,
    MAX_DESCRIPTION_CHARS,
    MAX_LABEL_CHARS,
    MAX_INVARIANT_TEXT_CHARS,
    # Enrichment enums
    EnrichmentConfidence,
    InvariantClassification,
    EnrichmentIssueType,
    ReviewDecision,
    # Enrichment artifacts
    EnrichmentIssue,
    EnrichedComponentLabel,
    EnrichedInvariant,
    EnrichmentResult,
)
from axiom_canon.ingestion.enrichment import (
    # Configuration
    EnrichmentConfig,
    # Backend protocol
    EnrichmentLLMBackend,
    MockEnrichmentBackend,
    # Runner
    LLMEnrichmentRunner,
    # Validation
    validate_enrichment_does_not_modify_structure,
    reject_over_confident_claims,
    # Human review
    apply_review_decision,
    get_approved_enrichments,
)

__all__ = [
    # Core summary artifacts
    "ModuleSummary",
    "ComponentSummary",
    "APIExposureSummary",
    "DependencyEdgeSummary",
    "InvariantSummary",
    # Supporting types
    "FunctionSignature",
    "ClassSignature",
    "MethodSignature",
    "ParameterInfo",
    "ImportInfo",
    "ExportInfo",
    "EntryPoint",
    "ConfigBoundary",
    # Container types
    "IngestionResult",
    "IngestionManifest",
    # Enums
    "Visibility",
    "ModuleType",
    "DependencyType",
    "InvariantType",
    # Extractor
    "CodeExtractor",
    "PythonASTExtractor",
    "ExtractionConfig",
    "ExtractionError",
    # Diffing
    "IngestionDiff",
    "ArtifactChange",
    "ChangeType",
    "compute_diff",
    "apply_diff",
    # LLM consumption
    "LLMConsumptionContract",
    "ChunkingStrategy",
    "SummaryChunk",
    "prepare_for_llm",
    # Enrichment constants
    "LLM_ENRICHMENT_LABEL",
    "MAX_DESCRIPTION_CHARS",
    "MAX_LABEL_CHARS",
    "MAX_INVARIANT_TEXT_CHARS",
    # Enrichment enums
    "EnrichmentConfidence",
    "InvariantClassification",
    "EnrichmentIssueType",
    "ReviewDecision",
    # Enrichment artifacts
    "EnrichmentIssue",
    "EnrichedComponentLabel",
    "EnrichedInvariant",
    "EnrichmentResult",
    # Enrichment configuration
    "EnrichmentConfig",
    # Enrichment backend
    "EnrichmentLLMBackend",
    "MockEnrichmentBackend",
    # Enrichment runner
    "LLMEnrichmentRunner",
    # Enrichment validation
    "validate_enrichment_does_not_modify_structure",
    "reject_over_confident_claims",
    # Human review
    "apply_review_decision",
    "get_approved_enrichments",
]
