"""
Tests for LLM Enrichment Stage.

Covers:
- Valid enrichment accepted
- Invalid enrichment rejected
- Over-confident output rejected
- Uncertain enrichment surfaced correctly
- LLM unavailable graceful skip
- Canon unchanged without approval
- Token discipline enforcement
- Human review flow
"""

import json
from typing import Any, Dict, List, Optional

import pytest

from axiom_canon.ingestion.models import (
    ComponentSummary,
    ModuleSummary,
    FunctionSignature,
    ClassSignature,
    ExportInfo,
    IngestionResult,
    ModuleType,
    Visibility,
)
from axiom_canon.ingestion.enrichment_models import (
    EnrichmentConfidence,
    InvariantClassification,
    EnrichmentIssueType,
    ReviewDecision,
    EnrichmentIssue,
    EnrichedComponentLabel,
    EnrichedInvariant,
    EnrichmentResult,
    LLM_ENRICHMENT_LABEL,
    MAX_LABEL_CHARS,
    MAX_DESCRIPTION_CHARS,
    MAX_INVARIANT_TEXT_CHARS,
)
from axiom_canon.ingestion.enrichment import (
    EnrichmentConfig,
    MockEnrichmentBackend,
    LLMEnrichmentRunner,
    validate_enrichment_does_not_modify_structure,
    reject_over_confident_claims,
    apply_review_decision,
    get_approved_enrichments,
    _extract_json_from_response,
    _estimate_tokens,
    _truncate_to_tokens,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_modules() -> List[ModuleSummary]:
    """Create sample modules for testing."""
    return [
        ModuleSummary(
            id="mod_1",
            name="auth_handler",
            path="src/auth/handler.py",
            module_type=ModuleType.MODULE,
            functions=[
                FunctionSignature(
                    name="authenticate",
                    parameters=(),
                    return_type="bool",
                    visibility=Visibility.PUBLIC,
                ),
            ],
            classes=[
                ClassSignature(
                    name="AuthProtocol",
                    methods=(),
                    visibility=Visibility.PUBLIC,
                    is_protocol=True,
                ),
            ],
            exports=[
                ExportInfo(name="authenticate", kind="function"),
                ExportInfo(name="AuthProtocol", kind="class"),
            ],
            human_notes="@invariant All tokens must be time-limited to 1 hour max.",
        ),
        ModuleSummary(
            id="mod_2",
            name="user_model",
            path="src/models/user.py",
            module_type=ModuleType.MODULE,
            functions=[],
            classes=[
                ClassSignature(
                    name="User",
                    methods=(),
                    visibility=Visibility.PUBLIC,
                ),
            ],
            exports=[
                ExportInfo(name="User", kind="class"),
            ],
        ),
    ]


@pytest.fixture
def sample_components(sample_modules: List[ModuleSummary]) -> List[ComponentSummary]:
    """Create sample components for testing."""
    return [
        ComponentSummary(
            id="comp_auth",
            name="auth",
            path="src/auth",
            modules=[sample_modules[0]],
            entry_points=[],
        ),
        ComponentSummary(
            id="comp_models",
            name="models",
            path="src/models",
            modules=[sample_modules[1]],
            entry_points=[],
        ),
    ]


@pytest.fixture
def sample_ingestion_result(
    sample_modules: List[ModuleSummary],
    sample_components: List[ComponentSummary],
) -> IngestionResult:
    """Create sample ingestion result."""
    return IngestionResult(
        project_root="src",
        modules=sample_modules,
        components=sample_components,
        api_exposures=[],
        dependency_edges=[],
        invariants=[],
    )


# =============================================================================
# Mock Backend Tests
# =============================================================================


class TestMockEnrichmentBackend:
    """Tests for MockEnrichmentBackend."""
    
    def test_available_by_default(self) -> None:
        """Backend is available by default."""
        backend = MockEnrichmentBackend()
        assert backend.is_available() is True
    
    def test_unavailable_when_configured(self) -> None:
        """Backend can be configured as unavailable."""
        backend = MockEnrichmentBackend(available=False)
        assert backend.is_available() is False
    
    def test_raises_when_unavailable(self) -> None:
        """Calling complete on unavailable backend raises."""
        backend = MockEnrichmentBackend(available=False)
        with pytest.raises(RuntimeError, match="unavailable"):
            backend.complete("test", "system", 100)
    
    def test_returns_predetermined_responses(self) -> None:
        """Returns predetermined responses in order."""
        responses = ['{"a": 1}', '{"b": 2}']
        backend = MockEnrichmentBackend(responses=responses)
        
        resp1, _, _ = backend.complete("p1", "s", 100)
        resp2, _, _ = backend.complete("p2", "s", 100)
        resp3, _, _ = backend.complete("p3", "s", 100)
        
        assert resp1 == '{"a": 1}'
        assert resp2 == '{"b": 2}'
        assert resp3 == '{"a": 1}'  # Cycles back
    
    def test_tracks_call_count(self) -> None:
        """Tracks number of calls."""
        backend = MockEnrichmentBackend()
        
        assert backend.call_count == 0
        backend.complete("test", "system", 100)
        assert backend.call_count == 1
        backend.complete("test2", "system", 100)
        assert backend.call_count == 2
    
    def test_stores_prompts(self) -> None:
        """Stores prompts for inspection."""
        backend = MockEnrichmentBackend()
        
        backend.complete("prompt 1", "system", 100)
        backend.complete("prompt 2", "system", 100)
        
        assert len(backend.prompts) == 2
        assert backend.prompts[0] == "prompt 1"
        assert backend.prompts[1] == "prompt 2"
    
    def test_model_name(self) -> None:
        """Returns configured model name."""
        backend = MockEnrichmentBackend(model="test-model")
        assert backend.model_name() == "test-model"


# =============================================================================
# JSON Extraction Tests
# =============================================================================


class TestJsonExtraction:
    """Tests for JSON extraction from LLM responses."""
    
    def test_extract_plain_json(self) -> None:
        """Extracts plain JSON."""
        response = '{"labels": [{"id": "test"}]}'
        result = _extract_json_from_response(response)
        assert result == {"labels": [{"id": "test"}]}
    
    def test_extract_json_from_markdown(self) -> None:
        """Extracts JSON from markdown code blocks."""
        response = '''Here is the result:
```json
{"labels": [{"id": "test"}]}
```
'''
        result = _extract_json_from_response(response)
        assert result == {"labels": [{"id": "test"}]}
    
    def test_extract_json_from_plain_code_block(self) -> None:
        """Extracts JSON from plain code blocks."""
        response = '''
```
{"labels": []}
```
'''
        result = _extract_json_from_response(response)
        assert result == {"labels": []}
    
    def test_invalid_json_raises(self) -> None:
        """Invalid JSON raises ValueError."""
        response = "This is not JSON at all"
        with pytest.raises(ValueError, match="No valid JSON"):
            _extract_json_from_response(response)
    
    def test_handles_whitespace(self) -> None:
        """Handles extra whitespace."""
        response = '''

        {"result": true}

'''
        result = _extract_json_from_response(response)
        assert result == {"result": True}


# =============================================================================
# Token Estimation Tests
# =============================================================================


class TestTokenEstimation:
    """Tests for token estimation utilities."""
    
    def test_estimate_tokens(self) -> None:
        """Estimates tokens based on character count."""
        text = "a" * 100
        assert _estimate_tokens(text) == 25  # 100 / 4
    
    def test_truncate_within_limit(self) -> None:
        """Text within limit is unchanged."""
        text = "short text"
        assert _truncate_to_tokens(text, 100) == text
    
    def test_truncate_exceeds_limit(self) -> None:
        """Text exceeding limit is truncated."""
        text = "a" * 100
        result = _truncate_to_tokens(text, 10)  # 10 tokens = 40 chars
        assert len(result) == 40
        assert result.endswith("...")


# =============================================================================
# LLMEnrichmentRunner Tests
# =============================================================================


class TestLLMEnrichmentRunner:
    """Tests for LLMEnrichmentRunner."""
    
    def test_enrichment_disabled(
        self,
        sample_ingestion_result: IngestionResult,
    ) -> None:
        """Returns empty result when enrichment is disabled."""
        backend = MockEnrichmentBackend()
        config = EnrichmentConfig(enabled=False)
        runner = LLMEnrichmentRunner(backend, config)
        
        result = runner.enrich(sample_ingestion_result)
        
        assert not result.has_enrichments
        assert result.has_issues
        assert any(
            i.issue_type == EnrichmentIssueType.LLM_UNAVAILABLE
            for i in result.issues
        )
    
    def test_backend_unavailable(
        self,
        sample_ingestion_result: IngestionResult,
    ) -> None:
        """Handles unavailable backend gracefully."""
        backend = MockEnrichmentBackend(available=False)
        runner = LLMEnrichmentRunner(backend)
        
        result = runner.enrich(sample_ingestion_result)
        
        assert not result.has_enrichments
        assert result.has_issues
        assert any(
            i.issue_type == EnrichmentIssueType.LLM_UNAVAILABLE
            for i in result.issues
        )
    
    def test_valid_component_labels(
        self,
        sample_ingestion_result: IngestionResult,
    ) -> None:
        """Accepts valid component labels."""
        response = json.dumps({
            "labels": [
                {
                    "component_id": "comp_auth",
                    "responsibility_label": "Authentication",
                    "description": "Handles user authentication.",
                    "confidence": "high",
                    "assumptions": [],
                },
                {
                    "component_id": "comp_models",
                    "responsibility_label": "Data Models",
                    "description": "Defines data structures.",
                    "confidence": "medium",
                    "assumptions": ["Based on class names"],
                },
            ]
        })
        
        backend = MockEnrichmentBackend(responses=[response, '{"invariants": []}'])
        runner = LLMEnrichmentRunner(backend)
        
        result = runner.enrich(sample_ingestion_result)
        
        assert len(result.component_labels) == 2
        assert result.component_labels[0].responsibility_label == "Authentication"
        assert result.component_labels[0].confidence == EnrichmentConfidence.HIGH
        assert result.component_labels[1].confidence == EnrichmentConfidence.MEDIUM
    
    def test_unknown_component_rejected(
        self,
        sample_ingestion_result: IngestionResult,
    ) -> None:
        """Labels for unknown components are rejected."""
        response = json.dumps({
            "labels": [
                {
                    "component_id": "unknown_comp",
                    "responsibility_label": "Unknown",
                    "description": "This component does not exist.",
                    "confidence": "high",
                    "assumptions": [],
                },
            ]
        })
        
        backend = MockEnrichmentBackend(responses=[response, '{"invariants": []}'])
        runner = LLMEnrichmentRunner(backend)
        
        result = runner.enrich(sample_ingestion_result)
        
        assert len(result.component_labels) == 0
        assert any(
            i.issue_type == EnrichmentIssueType.UNKNOWN_ARTIFACT
            for i in result.issues
        )
    
    def test_valid_invariants(
        self,
        sample_ingestion_result: IngestionResult,
    ) -> None:
        """Accepts valid invariants."""
        response = json.dumps({
            "invariants": [
                {
                    "invariant_text": "Tokens must be time-limited to 1 hour max.",
                    "source_file": "src/auth/handler.py",
                    "source_type": "docstring",
                    "source_quote": "@invariant All tokens must be time-limited",
                    "classification": "explicit",
                    "confidence": "high",
                },
            ]
        })
        
        backend = MockEnrichmentBackend(responses=['{"labels": []}', response])
        runner = LLMEnrichmentRunner(backend)
        
        result = runner.enrich(sample_ingestion_result)
        
        assert len(result.invariants) == 1
        assert "time-limited" in result.invariants[0].invariant_text
        assert result.invariants[0].classification == InvariantClassification.EXPLICIT
    
    def test_unknown_source_file_rejected(
        self,
        sample_ingestion_result: IngestionResult,
    ) -> None:
        """Invariants with unknown source files are rejected."""
        response = json.dumps({
            "invariants": [
                {
                    "invariant_text": "Made up invariant",
                    "source_file": "nonexistent/file.py",
                    "source_type": "docstring",
                    "source_quote": "",
                    "classification": "uncertain",
                    "confidence": "low",
                },
            ]
        })
        
        backend = MockEnrichmentBackend(responses=['{"labels": []}', response])
        runner = LLMEnrichmentRunner(backend)
        
        result = runner.enrich(sample_ingestion_result)
        
        assert len(result.invariants) == 0
        assert any(
            i.issue_type == EnrichmentIssueType.UNKNOWN_ARTIFACT
            for i in result.issues
        )
    
    def test_parse_error_handling(
        self,
        sample_ingestion_result: IngestionResult,
    ) -> None:
        """Handles parse errors gracefully."""
        backend = MockEnrichmentBackend(responses=["not valid json"])
        runner = LLMEnrichmentRunner(backend)
        
        result = runner.enrich(sample_ingestion_result)
        
        assert any(
            i.issue_type == EnrichmentIssueType.PARSE_ERROR
            for i in result.issues
        )
    
    def test_token_budget_enforced(
        self,
        sample_ingestion_result: IngestionResult,
    ) -> None:
        """Stops when token budget is exceeded."""
        config = EnrichmentConfig(
            max_total_input_tokens=10,  # Very low budget
        )
        
        backend = MockEnrichmentBackend(responses=['{"labels": []}', '{"invariants": []}'])
        runner = LLMEnrichmentRunner(backend, config)
        
        result = runner.enrich(sample_ingestion_result)
        
        # Should have token limit exceeded issue
        assert any(
            i.issue_type == EnrichmentIssueType.TOKEN_LIMIT_EXCEEDED
            for i in result.issues
        )
    
    def test_skip_low_confidence(
        self,
        sample_ingestion_result: IngestionResult,
    ) -> None:
        """Filters out LOW confidence when configured."""
        response = json.dumps({
            "labels": [
                {
                    "component_id": "comp_auth",
                    "responsibility_label": "Auth",
                    "description": "Auth stuff",
                    "confidence": "high",
                    "assumptions": [],
                },
                {
                    "component_id": "comp_models",
                    "responsibility_label": "Models",
                    "description": "Model stuff",
                    "confidence": "low",
                    "assumptions": ["Very uncertain"],
                },
            ]
        })
        
        config = EnrichmentConfig(skip_low_confidence=True)
        backend = MockEnrichmentBackend(responses=[response, '{"invariants": []}'])
        runner = LLMEnrichmentRunner(backend, config)
        
        result = runner.enrich(sample_ingestion_result)
        
        assert len(result.component_labels) == 1
        assert result.component_labels[0].component_id == "comp_auth"
    
    def test_tracks_llm_stats(
        self,
        sample_ingestion_result: IngestionResult,
    ) -> None:
        """Tracks LLM call statistics."""
        backend = MockEnrichmentBackend(responses=['{"labels": []}', '{"invariants": []}'])
        runner = LLMEnrichmentRunner(backend)
        
        result = runner.enrich(sample_ingestion_result)
        
        assert result.total_llm_calls == 2  # Component + Invariant
        assert result.total_input_tokens > 0
        assert result.total_output_tokens > 0
        assert result.llm_model == "mock-enrichment-model"


# =============================================================================
# Validation Tests
# =============================================================================


class TestValidateEnrichmentDoesNotModifyStructure:
    """Tests for structure modification validation."""
    
    def test_valid_enrichment_passes(
        self,
        sample_ingestion_result: IngestionResult,
    ) -> None:
        """Valid enrichment passes validation."""
        enrichment = EnrichmentResult(
            ingestion_version_hash=sample_ingestion_result.version_hash,
            component_labels=[
                EnrichedComponentLabel(
                    component_id="comp_auth",
                    component_path="src/auth",
                    responsibility_label="Auth",
                    description="Authentication.",
                    confidence=EnrichmentConfidence.MEDIUM,
                ),
            ],
            invariants=[
                EnrichedInvariant(
                    invariant_id="inv_1",
                    invariant_text="Test invariant",
                    source_file="src/auth/handler.py",
                    source_line=10,
                    source_type="docstring",
                    source_quote="Test quote",
                    classification=InvariantClassification.EXPLICIT,
                    confidence=EnrichmentConfidence.HIGH,
                ),
            ],
        )
        
        issues = validate_enrichment_does_not_modify_structure(
            sample_ingestion_result,
            enrichment,
        )
        
        assert len(issues) == 0
    
    def test_unknown_component_fails(
        self,
        sample_ingestion_result: IngestionResult,
    ) -> None:
        """Labels for unknown components fail validation."""
        enrichment = EnrichmentResult(
            ingestion_version_hash=sample_ingestion_result.version_hash,
            component_labels=[
                EnrichedComponentLabel(
                    component_id="invented_component",
                    component_path="invented/path",
                    responsibility_label="Invented",
                    description="Made up.",
                    confidence=EnrichmentConfidence.HIGH,
                ),
            ],
        )
        
        issues = validate_enrichment_does_not_modify_structure(
            sample_ingestion_result,
            enrichment,
        )
        
        assert len(issues) == 1
        assert issues[0].issue_type == EnrichmentIssueType.STRUCTURE_MODIFIED
    
    def test_unknown_file_fails(
        self,
        sample_ingestion_result: IngestionResult,
    ) -> None:
        """Invariants for unknown files fail validation."""
        enrichment = EnrichmentResult(
            ingestion_version_hash=sample_ingestion_result.version_hash,
            invariants=[
                EnrichedInvariant(
                    invariant_id="inv_bad",
                    invariant_text="Invented invariant",
                    source_file="invented/file.py",
                    source_line=1,
                    source_type="docstring",
                    source_quote="Made up",
                    classification=InvariantClassification.UNCERTAIN,
                    confidence=EnrichmentConfidence.LOW,
                ),
            ],
        )
        
        issues = validate_enrichment_does_not_modify_structure(
            sample_ingestion_result,
            enrichment,
        )
        
        assert len(issues) == 1
        assert issues[0].issue_type == EnrichmentIssueType.STRUCTURE_MODIFIED


class TestRejectOverConfidentClaims:
    """Tests for over-confident claim rejection."""
    
    def test_high_confidence_with_context_passes(self) -> None:
        """HIGH confidence with source context passes."""
        enrichment = EnrichmentResult(
            ingestion_version_hash="hash",
            component_labels=[
                EnrichedComponentLabel(
                    component_id="comp_1",
                    component_path="src/comp",
                    responsibility_label="Component",
                    description="Does something.",
                    confidence=EnrichmentConfidence.HIGH,
                    source_context=["module1", "module2"],
                ),
            ],
        )
        
        issues = reject_over_confident_claims(enrichment)
        
        assert len(issues) == 0
    
    def test_high_confidence_without_context_fails(self) -> None:
        """HIGH confidence without source context fails."""
        enrichment = EnrichmentResult(
            ingestion_version_hash="hash",
            component_labels=[
                EnrichedComponentLabel(
                    component_id="comp_1",
                    component_path="src/comp",
                    responsibility_label="Component",
                    description="Does something.",
                    confidence=EnrichmentConfidence.HIGH,
                    source_context=[],  # Empty!
                ),
            ],
        )
        
        issues = reject_over_confident_claims(enrichment)
        
        assert len(issues) == 1
        assert issues[0].issue_type == EnrichmentIssueType.VALIDATION_ERROR
    
    def test_explicit_invariant_with_quote_passes(self) -> None:
        """EXPLICIT invariant with source quote passes."""
        enrichment = EnrichmentResult(
            ingestion_version_hash="hash",
            invariants=[
                EnrichedInvariant(
                    invariant_id="inv_1",
                    invariant_text="Must not cache passwords",
                    source_file="src/auth.py",
                    source_line=10,
                    source_type="docstring",
                    source_quote="@invariant Must not cache passwords",
                    classification=InvariantClassification.EXPLICIT,
                    confidence=EnrichmentConfidence.HIGH,
                ),
            ],
        )
        
        issues = reject_over_confident_claims(enrichment)
        
        assert len(issues) == 0
    
    def test_explicit_invariant_without_quote_fails(self) -> None:
        """EXPLICIT invariant without source quote fails."""
        enrichment = EnrichmentResult(
            ingestion_version_hash="hash",
            invariants=[
                EnrichedInvariant(
                    invariant_id="inv_1",
                    invariant_text="Some invariant",
                    source_file="src/auth.py",
                    source_line=10,
                    source_type="docstring",
                    source_quote="",  # Empty!
                    classification=InvariantClassification.EXPLICIT,
                    confidence=EnrichmentConfidence.HIGH,
                ),
            ],
        )
        
        issues = reject_over_confident_claims(enrichment)
        
        assert len(issues) == 1
        assert issues[0].issue_type == EnrichmentIssueType.VALIDATION_ERROR


# =============================================================================
# Human Review Tests
# =============================================================================


class TestHumanReviewFlow:
    """Tests for human review integration."""
    
    def test_apply_approval(self) -> None:
        """Apply approval to component label."""
        enrichment = EnrichmentResult(
            ingestion_version_hash="hash",
            component_labels=[
                EnrichedComponentLabel(
                    component_id="comp_1",
                    component_path="src/comp",
                    responsibility_label="Component",
                    description="Does something.",
                    confidence=EnrichmentConfidence.MEDIUM,
                ),
            ],
        )
        
        result = apply_review_decision(
            enrichment,
            "comp_1",
            ReviewDecision.APPROVED,
            notes="Looks good",
        )
        
        assert result is True
        assert enrichment.component_labels[0].review_decision == ReviewDecision.APPROVED
        assert enrichment.component_labels[0].reviewer_notes == "Looks good"
    
    def test_apply_rejection(self) -> None:
        """Apply rejection to invariant."""
        enrichment = EnrichmentResult(
            ingestion_version_hash="hash",
            invariants=[
                EnrichedInvariant(
                    invariant_id="inv_1",
                    invariant_text="Some invariant",
                    source_file="src/auth.py",
                    source_line=10,
                    source_type="docstring",
                    source_quote="Quote",
                    classification=InvariantClassification.UNCERTAIN,
                    confidence=EnrichmentConfidence.LOW,
                ),
            ],
        )
        
        result = apply_review_decision(
            enrichment,
            "inv_1",
            ReviewDecision.REJECTED,
            notes="This is not actually an invariant",
        )
        
        assert result is True
        assert enrichment.invariants[0].review_decision == ReviewDecision.REJECTED
    
    def test_apply_edit_to_label(self) -> None:
        """Apply edit to component label."""
        enrichment = EnrichmentResult(
            ingestion_version_hash="hash",
            component_labels=[
                EnrichedComponentLabel(
                    component_id="comp_1",
                    component_path="src/comp",
                    responsibility_label="Original Label",
                    description="Original description.",
                    confidence=EnrichmentConfidence.MEDIUM,
                ),
            ],
        )
        
        result = apply_review_decision(
            enrichment,
            "comp_1",
            ReviewDecision.EDITED,
            notes="Fixed description",
            edited_value={
                "responsibility_label": "Better Label",
                "description": "Better description.",
            },
        )
        
        assert result is True
        assert enrichment.component_labels[0].responsibility_label == "Better Label"
        assert enrichment.component_labels[0].description == "Better description."
        assert enrichment.component_labels[0].review_decision == ReviewDecision.EDITED
    
    def test_apply_edit_to_invariant(self) -> None:
        """Apply edit to invariant."""
        enrichment = EnrichmentResult(
            ingestion_version_hash="hash",
            invariants=[
                EnrichedInvariant(
                    invariant_id="inv_1",
                    invariant_text="Original text",
                    source_file="src/auth.py",
                    source_line=10,
                    source_type="docstring",
                    source_quote="Quote",
                    classification=InvariantClassification.UNCERTAIN,
                    confidence=EnrichmentConfidence.LOW,
                ),
            ],
        )
        
        result = apply_review_decision(
            enrichment,
            "inv_1",
            ReviewDecision.EDITED,
            notes="Made it explicit",
            edited_value={
                "invariant_text": "Clear invariant text",
                "classification": "explicit",
            },
        )
        
        assert result is True
        assert enrichment.invariants[0].invariant_text == "Clear invariant text"
        assert enrichment.invariants[0].classification == InvariantClassification.EXPLICIT
    
    def test_unknown_item_returns_false(self) -> None:
        """Returns False for unknown item."""
        enrichment = EnrichmentResult(ingestion_version_hash="hash")
        
        result = apply_review_decision(
            enrichment,
            "nonexistent",
            ReviewDecision.APPROVED,
        )
        
        assert result is False
    
    def test_get_approved_enrichments(self) -> None:
        """Get only approved enrichments."""
        enrichment = EnrichmentResult(
            ingestion_version_hash="hash",
            component_labels=[
                EnrichedComponentLabel(
                    component_id="comp_1",
                    component_path="src/comp1",
                    responsibility_label="Label 1",
                    description="Desc 1",
                    confidence=EnrichmentConfidence.HIGH,
                    review_decision=ReviewDecision.APPROVED,
                ),
                EnrichedComponentLabel(
                    component_id="comp_2",
                    component_path="src/comp2",
                    responsibility_label="Label 2",
                    description="Desc 2",
                    confidence=EnrichmentConfidence.LOW,
                    review_decision=ReviewDecision.REJECTED,
                ),
                EnrichedComponentLabel(
                    component_id="comp_3",
                    component_path="src/comp3",
                    responsibility_label="Label 3",
                    description="Desc 3",
                    confidence=EnrichmentConfidence.MEDIUM,
                    review_decision=ReviewDecision.PENDING,
                ),
            ],
            invariants=[
                EnrichedInvariant(
                    invariant_id="inv_1",
                    invariant_text="Invariant 1",
                    source_file="src/file.py",
                    source_line=1,
                    source_type="docstring",
                    source_quote="Quote 1",
                    classification=InvariantClassification.EXPLICIT,
                    confidence=EnrichmentConfidence.HIGH,
                    review_decision=ReviewDecision.EDITED,
                ),
                EnrichedInvariant(
                    invariant_id="inv_2",
                    invariant_text="Invariant 2",
                    source_file="src/file.py",
                    source_line=2,
                    source_type="comment",
                    source_quote="Quote 2",
                    classification=InvariantClassification.UNCERTAIN,
                    confidence=EnrichmentConfidence.LOW,
                    review_decision=ReviewDecision.PENDING,
                ),
            ],
        )
        
        labels, invariants = get_approved_enrichments(enrichment)
        
        # Only comp_1 is approved
        assert len(labels) == 1
        assert labels[0].component_id == "comp_1"
        
        # Only inv_1 is approved (via EDITED)
        assert len(invariants) == 1
        assert invariants[0].invariant_id == "inv_1"


# =============================================================================
# Enrichment Model Validation Tests
# =============================================================================


class TestEnrichedComponentLabelValidation:
    """Tests for EnrichedComponentLabel validation."""
    
    def test_valid_label(self) -> None:
        """Valid label has no issues."""
        label = EnrichedComponentLabel(
            component_id="comp_1",
            component_path="src/comp",
            responsibility_label="Valid Label",
            description="A valid description.",
            confidence=EnrichmentConfidence.MEDIUM,
        )
        
        issues = label.validate()
        assert len(issues) == 0
    
    def test_label_too_long(self) -> None:
        """Labels exceeding limit fail validation."""
        label = EnrichedComponentLabel(
            component_id="comp_1",
            component_path="src/comp",
            responsibility_label="X" * (MAX_LABEL_CHARS + 1),
            description="Valid description.",
            confidence=EnrichmentConfidence.MEDIUM,
        )
        
        issues = label.validate()
        assert len(issues) == 1
        assert issues[0].issue_type == EnrichmentIssueType.OUTPUT_TOO_VERBOSE
    
    def test_description_too_long(self) -> None:
        """Descriptions exceeding limit fail validation."""
        label = EnrichedComponentLabel(
            component_id="comp_1",
            component_path="src/comp",
            responsibility_label="Valid",
            description="X" * (MAX_DESCRIPTION_CHARS + 1),
            confidence=EnrichmentConfidence.MEDIUM,
        )
        
        issues = label.validate()
        assert len(issues) == 1
        assert issues[0].issue_type == EnrichmentIssueType.OUTPUT_TOO_VERBOSE
    
    def test_unknown_confidence_fails(self) -> None:
        """UNKNOWN confidence fails validation."""
        label = EnrichedComponentLabel(
            component_id="comp_1",
            component_path="src/comp",
            responsibility_label="Valid",
            description="Valid.",
            confidence=EnrichmentConfidence.UNKNOWN,
        )
        
        issues = label.validate()
        assert len(issues) == 1
        assert issues[0].issue_type == EnrichmentIssueType.CONFIDENCE_TOO_LOW


class TestEnrichedInvariantValidation:
    """Tests for EnrichedInvariant validation."""
    
    def test_valid_invariant(self) -> None:
        """Valid invariant has no issues."""
        inv = EnrichedInvariant(
            invariant_id="inv_1",
            invariant_text="Valid invariant text.",
            source_file="src/file.py",
            source_line=10,
            source_type="docstring",
            source_quote="@invariant Valid",
            classification=InvariantClassification.EXPLICIT,
            confidence=EnrichmentConfidence.HIGH,
        )
        
        issues = inv.validate()
        assert len(issues) == 0
    
    def test_invariant_text_too_long(self) -> None:
        """Invariant text exceeding limit fails validation."""
        inv = EnrichedInvariant(
            invariant_id="inv_1",
            invariant_text="X" * (MAX_INVARIANT_TEXT_CHARS + 1),
            source_file="src/file.py",
            source_line=10,
            source_type="docstring",
            source_quote="Quote",
            classification=InvariantClassification.UNCERTAIN,
            confidence=EnrichmentConfidence.LOW,
        )
        
        issues = inv.validate()
        assert len(issues) == 1
        assert issues[0].issue_type == EnrichmentIssueType.OUTPUT_TOO_VERBOSE
    
    def test_explicit_without_quote_fails(self) -> None:
        """EXPLICIT invariant without source quote fails."""
        inv = EnrichedInvariant(
            invariant_id="inv_1",
            invariant_text="Valid text",
            source_file="src/file.py",
            source_line=10,
            source_type="docstring",
            source_quote="",  # Missing!
            classification=InvariantClassification.EXPLICIT,
            confidence=EnrichmentConfidence.HIGH,
        )
        
        issues = inv.validate()
        assert len(issues) == 1
        assert issues[0].issue_type == EnrichmentIssueType.VALIDATION_ERROR
    
    def test_invalid_source_type_fails(self) -> None:
        """Invalid source type fails validation."""
        inv = EnrichedInvariant(
            invariant_id="inv_1",
            invariant_text="Valid text",
            source_file="src/file.py",
            source_line=10,
            source_type="invalid_type",  # Invalid!
            source_quote="Quote",
            classification=InvariantClassification.UNCERTAIN,
            confidence=EnrichmentConfidence.LOW,
        )
        
        issues = inv.validate()
        assert len(issues) == 1
        assert issues[0].issue_type == EnrichmentIssueType.VALIDATION_ERROR


# =============================================================================
# Serialization Tests
# =============================================================================


class TestEnrichmentSerialization:
    """Tests for enrichment serialization."""
    
    def test_component_label_roundtrip(self) -> None:
        """Component label serializes and deserializes correctly."""
        original = EnrichedComponentLabel(
            component_id="comp_1",
            component_path="src/comp",
            responsibility_label="Label",
            description="Description",
            confidence=EnrichmentConfidence.MEDIUM,
            assumptions=["Assumption 1"],
            source_context=["context"],
            review_decision=ReviewDecision.APPROVED,
            reviewer_notes="Approved by reviewer",
        )
        
        data = original.to_dict()
        restored = EnrichedComponentLabel.from_dict(data)
        
        assert restored.component_id == original.component_id
        assert restored.responsibility_label == original.responsibility_label
        assert restored.confidence == original.confidence
        assert restored.review_decision == original.review_decision
        assert restored.reviewer_notes == original.reviewer_notes
    
    def test_invariant_roundtrip(self) -> None:
        """Invariant serializes and deserializes correctly."""
        original = EnrichedInvariant(
            invariant_id="inv_1",
            invariant_text="Invariant text",
            source_file="src/file.py",
            source_line=42,
            source_type="marker",
            source_quote="@invariant text",
            classification=InvariantClassification.EXPLICIT,
            confidence=EnrichmentConfidence.HIGH,
            review_decision=ReviewDecision.EDITED,
            reviewer_notes="Minor edit",
        )
        
        data = original.to_dict()
        restored = EnrichedInvariant.from_dict(data)
        
        assert restored.invariant_id == original.invariant_id
        assert restored.source_line == original.source_line
        assert restored.classification == original.classification
        assert restored.review_decision == original.review_decision
    
    def test_issue_roundtrip(self) -> None:
        """Issue serializes and deserializes correctly."""
        original = EnrichmentIssue(
            issue_type=EnrichmentIssueType.VALIDATION_ERROR,
            message="Test error",
            artifact_id="artifact_1",
            details={"key": "value"},
        )
        
        data = original.to_dict()
        restored = EnrichmentIssue.from_dict(data)
        
        assert restored.issue_type == original.issue_type
        assert restored.message == original.message
        assert restored.artifact_id == original.artifact_id
        assert restored.details == original.details


# =============================================================================
# Integration Tests
# =============================================================================


class TestEnrichmentIntegration:
    """Integration tests for full enrichment flow."""
    
    def test_full_enrichment_flow(
        self,
        sample_ingestion_result: IngestionResult,
    ) -> None:
        """Tests complete enrichment flow from ingestion to approved Canon."""
        # 1. Set up mock backend with realistic responses
        label_response = json.dumps({
            "labels": [
                {
                    "component_id": "comp_auth",
                    "responsibility_label": "Authentication Service",
                    "description": "Handles user authentication and token management.",
                    "confidence": "high",
                    "assumptions": [],
                },
                {
                    "component_id": "comp_models",
                    "responsibility_label": "Data Layer",
                    "description": "Defines core data models.",
                    "confidence": "medium",
                    "assumptions": ["Based on class names only"],
                },
            ]
        })
        
        invariant_response = json.dumps({
            "invariants": [
                {
                    "invariant_text": "Tokens must be time-limited to 1 hour max.",
                    "source_file": "src/auth/handler.py",
                    "source_type": "docstring",
                    "source_quote": "@invariant All tokens must be time-limited to 1 hour max.",
                    "classification": "explicit",
                    "confidence": "high",
                },
            ]
        })
        
        backend = MockEnrichmentBackend(responses=[label_response, invariant_response])
        runner = LLMEnrichmentRunner(backend)
        
        # 2. Run enrichment
        result = runner.enrich(sample_ingestion_result)
        
        # 3. Verify enrichment was produced
        assert result.has_enrichments
        assert len(result.component_labels) == 2
        assert len(result.invariants) == 1
        
        # 4. Verify all are pending review
        for label in result.component_labels:
            assert label.review_decision == ReviewDecision.PENDING
            assert label.llm_label == LLM_ENRICHMENT_LABEL
        
        for inv in result.invariants:
            assert inv.review_decision == ReviewDecision.PENDING
            assert inv.llm_label == LLM_ENRICHMENT_LABEL
        
        # 5. Validate no structure modifications
        structure_issues = validate_enrichment_does_not_modify_structure(
            sample_ingestion_result,
            result,
        )
        assert len(structure_issues) == 0
        
        # 6. Human reviews
        apply_review_decision(result, "comp_auth", ReviewDecision.APPROVED)
        apply_review_decision(result, "comp_models", ReviewDecision.REJECTED, "Too vague")
        apply_review_decision(
            result,
            result.invariants[0].invariant_id,
            ReviewDecision.EDITED,
            edited_value={"invariant_text": "All tokens must expire within 1 hour"},
        )
        
        # 7. Get approved enrichments for Canon
        approved_labels, approved_invariants = get_approved_enrichments(result)
        
        # Only comp_auth approved
        assert len(approved_labels) == 1
        assert approved_labels[0].component_id == "comp_auth"
        
        # Invariant approved via edit
        assert len(approved_invariants) == 1
        assert approved_invariants[0].invariant_text == "All tokens must expire within 1 hour"
    
    def test_graceful_degradation(
        self,
        sample_ingestion_result: IngestionResult,
    ) -> None:
        """Tests that enrichment degrades gracefully on failures."""
        # Backend fails after first call
        class FailingBackend:
            def __init__(self) -> None:
                self.call_count = 0
            
            def complete(self, prompt: str, system_prompt: str, max_output_tokens: int):
                self.call_count += 1
                if self.call_count == 1:
                    return '{"labels": []}', 100, 50
                raise RuntimeError("Backend failed")
            
            def is_available(self) -> bool:
                return True
            
            def model_name(self) -> str:
                return "failing-model"
        
        backend = FailingBackend()
        runner = LLMEnrichmentRunner(backend)  # type: ignore
        
        result = runner.enrich(sample_ingestion_result)
        
        # Should still return a result, just with issues
        assert result is not None
        assert result.has_issues
        assert any(
            i.issue_type == EnrichmentIssueType.LLM_UNAVAILABLE
            for i in result.issues
        )
