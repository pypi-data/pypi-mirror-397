"""
Tests for LLM Strategic Reviewer.

Verifies:
1. Reviewer never executes or approves
2. Reviewer output is advisory only
3. Invalid LLM output is safely ignored
4. Human rejection overrides AI recommendation
5. Human approval does not require AI approval
6. Token limits are enforced
7. Canon and plans remain unchanged
"""

import json
import uuid
from typing import Optional

import pytest

from axiom_archon.strategic_review_models import (
    ConfidenceLevel,
    EvidenceReference,
    LLMStrategicReviewResult,
    OverallRiskPosture,
    RiskCategory,
    RiskSeverity,
    STRATEGIC_REVIEW_LABEL,
    StrategicConcern,
    StrategicReviewSummary,
    StrategicRisk,
    StrategicTradeoff,
    create_empty_review,
    create_failed_review,
    validate_review_is_advisory,
    validate_risks_have_evidence,
    validate_confidence_is_stated,
)
from axiom_archon.llm_strategic_reviewer import (
    LLMStrategicReviewer,
    LLMUnavailableError,
    MockStrategicLLMBackend,
    StrategicReviewConfig,
    StrategicReviewContext,
    StrategicReviewContextBuilder,
    StrategicReviewParser,
    build_strategic_review_prompt,
    validate_reviewer_is_advisory,
    validate_reviewer_has_no_authority,
)
from axiom_archon.model import (
    StrategicContext,
    StrategicDecision,
    StrategicDecisionType,
    StrategicIntent,
)
from axiom_archon.human_loop import (
    HumanDecision,
    HumanDecisionAction,
    HumanDecisionHandler,
)
from axiom_canon.cpkg import CPKG
from axiom_canon.ucir import UCIR
from axiom_canon.bfm import BusinessFlowMap as BFM
from axiom_canon.task_graph import TaskGraph, TaskNode, TaskStatus
from axiom_strata.model import TacticalIntent, PlanningResult, PlanningContext
from axiom_strata.validation import PlanningValidationResult
from axiom_strata.dry_run import DryRunResult


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_strategic_intent():
    """Create a sample strategic intent."""
    return StrategicIntent(
        id="intent-1",
        description="Implement new feature",
        success_criteria=["Feature works", "Tests pass"],
        priority=1,
    )


@pytest.fixture
def sample_tactical_intent():
    """Create a sample tactical intent."""
    return TacticalIntent(
        id="tactical-1",
        description="Add authentication endpoint",
        constraints=["Must use OAuth2"],
        scope_ids=["auth-service"],
    )


@pytest.fixture
def sample_task_graph():
    """Create a sample task graph."""
    task1 = TaskNode(
        id="task-1",
        name="Create endpoint",
        description="Create the auth endpoint",
        command="create_file",
        status=TaskStatus.PENDING,
    )
    task2 = TaskNode(
        id="task-2",
        name="Add tests",
        description="Add unit tests",
        command="create_file",
        status=TaskStatus.PENDING,
    )
    graph = TaskGraph(
        id="graph-1",
        tasks={"task-1": task1, "task-2": task2},
        dependencies=[],
    )
    return graph


@pytest.fixture
def sample_planning_result(sample_task_graph):
    """Create a sample planning result."""
    return PlanningResult(
        graph=sample_task_graph,
        issues=[],
    )


@pytest.fixture
def sample_validation_result():
    """Create a valid validation result."""
    return PlanningValidationResult(is_valid=True, issues=[])


@pytest.fixture
def sample_dry_run_result():
    """Create a successful dry run result."""
    return DryRunResult(
        success=True,
        execution_order=["task-1", "task-2"],
        unreachable_tasks=[],
        deadlocked=False,
    )


@pytest.fixture
def sample_strategic_context():
    """Create a sample strategic context."""
    return StrategicContext(
        cpkg=CPKG(),
        ucir=UCIR(),
        bfm=BFM(),
    )


@pytest.fixture
def mock_backend():
    """Create a mock LLM backend."""
    return MockStrategicLLMBackend(available=True)


@pytest.fixture
def unavailable_backend():
    """Create an unavailable mock backend."""
    return MockStrategicLLMBackend(available=False)


@pytest.fixture
def reviewer(mock_backend):
    """Create a reviewer with mock backend."""
    return LLMStrategicReviewer(backend=mock_backend)


# =============================================================================
# Strategic Review Models Tests
# =============================================================================


class TestStrategicReviewModels:
    """Tests for strategic review data models."""
    
    def test_strategic_risk_requires_id(self):
        """Risk validation requires ID."""
        risk = StrategicRisk(
            id="",
            category=RiskCategory.SAFETY,
            description="Test risk",
            severity=RiskSeverity.HIGH,
        )
        errors = risk.validate()
        assert "Risk ID is required" in errors
    
    def test_strategic_risk_requires_evidence(self):
        """Risk validation requires evidence."""
        risk = StrategicRisk(
            id="risk-1",
            category=RiskCategory.SAFETY,
            description="Test risk",
            severity=RiskSeverity.HIGH,
            evidence=[],
        )
        errors = risk.validate()
        assert "Risk must have at least one evidence reference" in errors
    
    def test_strategic_risk_valid(self):
        """Valid risk passes validation."""
        risk = StrategicRisk(
            id="risk-1",
            category=RiskCategory.SAFETY,
            description="Test risk",
            severity=RiskSeverity.HIGH,
            evidence=[
                EvidenceReference(
                    source_type="task",
                    source_id="task-1",
                    excerpt="Evidence",
                )
            ],
        )
        errors = risk.validate()
        assert errors == []
    
    def test_tradeoff_requires_upside_or_downside(self):
        """Tradeoff validation requires upside or downside."""
        tradeoff = StrategicTradeoff(
            id="tradeoff-1",
            description="Test tradeoff",
        )
        errors = tradeoff.validate()
        assert "Tradeoff must specify upside or downside" in errors
    
    def test_concern_valid(self):
        """Valid concern passes validation."""
        concern = StrategicConcern(
            id="concern-1",
            description="Test concern",
        )
        errors = concern.validate()
        assert errors == []
    
    def test_review_result_always_has_advisory_label(self):
        """Review result always has advisory label."""
        result = LLMStrategicReviewResult(
            review_id="review-1",
            advisory_label="wrong label",  # Should be corrected
        )
        assert result.advisory_label == STRATEGIC_REVIEW_LABEL
    
    def test_review_result_validation(self):
        """Review result validates all components."""
        risk_without_evidence = StrategicRisk(
            id="risk-1",
            category=RiskCategory.SAFETY,
            description="Test",
            severity=RiskSeverity.HIGH,
            evidence=[],
        )
        result = LLMStrategicReviewResult(
            review_id="review-1",
            risks=[risk_without_evidence],
        )
        errors = result.validate()
        assert any("evidence" in e.lower() for e in errors)


class TestEmptyAndFailedReviews:
    """Tests for empty and failed review factories."""
    
    def test_create_empty_review(self):
        """Empty review is valid and has correct label."""
        review = create_empty_review("review-1", "Test reason")
        assert review.advisory_label == STRATEGIC_REVIEW_LABEL
        assert review.is_valid
        assert len(review.concerns) == 1
        assert "unavailable" in review.concerns[0].description.lower()
    
    def test_create_failed_review(self):
        """Failed review is valid and has correct label."""
        review = create_failed_review("review-1", "Parse error")
        assert review.advisory_label == STRATEGIC_REVIEW_LABEL
        assert review.is_valid
        assert "Parse error" in review.validation_errors


# =============================================================================
# Parser Tests
# =============================================================================


class TestStrategicReviewParser:
    """Tests for LLM output parsing."""
    
    def test_parse_empty_response(self):
        """Empty response returns failure."""
        result = StrategicReviewParser.parse("", "review-1")
        assert not result.success
        assert "empty" in result.error.lower()
    
    def test_parse_invalid_json(self):
        """Invalid JSON returns failure."""
        result = StrategicReviewParser.parse("not json", "review-1")
        assert not result.success
        assert "json" in result.error.lower()
    
    def test_parse_valid_response(self):
        """Valid JSON parses successfully."""
        response = json.dumps({
            "risks": [
                {
                    "id": "risk-1",
                    "category": "safety",
                    "description": "Test risk",
                    "severity": "high",
                    "evidence": [{"source_type": "task", "source_id": "t1", "excerpt": "x"}],
                    "confidence": "medium",
                }
            ],
            "tradeoffs": [],
            "concerns": [],
            "summary": {
                "overall_risk_posture": "moderate",
                "key_recommendations": [],
                "proceed_confidence": "medium",
                "requires_human_attention": True,
                "attention_areas": [],
            },
            "confidence": "medium",
        })
        result = StrategicReviewParser.parse(response, "review-1")
        assert result.success
        assert result.result is not None
        assert len(result.result.risks) == 1
    
    def test_parse_json_in_markdown(self):
        """JSON in markdown code block parses successfully."""
        response = """```json
{
    "risks": [],
    "tradeoffs": [],
    "concerns": [],
    "confidence": "low"
}
```"""
        result = StrategicReviewParser.parse(response, "review-1")
        assert result.success
    
    def test_parse_unknown_severity_defaults(self):
        """Unknown severity defaults to MEDIUM."""
        response = json.dumps({
            "risks": [
                {
                    "id": "risk-1",
                    "description": "Test",
                    "severity": "unknown_level",
                    "evidence": [{"source_type": "task", "source_id": "t1", "excerpt": "x"}],
                }
            ],
            "confidence": "medium",
        })
        result = StrategicReviewParser.parse(response, "review-1")
        assert result.success
        assert result.result.risks[0].severity == RiskSeverity.MEDIUM


# =============================================================================
# Context Builder Tests
# =============================================================================


class TestContextBuilder:
    """Tests for context building."""
    
    def test_context_within_token_limit(
        self,
        sample_strategic_intent,
        sample_tactical_intent,
        sample_planning_result,
        sample_validation_result,
        sample_dry_run_result,
        sample_strategic_context,
    ):
        """Built context stays within token limit."""
        config = StrategicReviewConfig(max_context_tokens=4000)
        builder = StrategicReviewContextBuilder(config)
        
        context = builder.build_context(
            sample_strategic_intent,
            sample_tactical_intent,
            sample_planning_result,
            sample_validation_result,
            sample_dry_run_result,
            sample_strategic_context,
        )
        
        assert context.total_token_estimate <= config.max_context_tokens
    
    def test_context_includes_all_sections(
        self,
        sample_strategic_intent,
        sample_tactical_intent,
        sample_planning_result,
        sample_validation_result,
        sample_dry_run_result,
        sample_strategic_context,
    ):
        """Built context includes all required sections."""
        config = StrategicReviewConfig()
        builder = StrategicReviewContextBuilder(config)
        
        context = builder.build_context(
            sample_strategic_intent,
            sample_tactical_intent,
            sample_planning_result,
            sample_validation_result,
            sample_dry_run_result,
            sample_strategic_context,
        )
        
        assert context.intent_summary
        assert context.plan_summary
        assert context.validation_summary
        assert context.dry_run_summary


# =============================================================================
# LLM Strategic Reviewer Tests
# =============================================================================


class TestLLMStrategicReviewer:
    """Tests for the LLM Strategic Reviewer."""
    
    def test_reviewer_has_no_execute_method(self, reviewer):
        """Reviewer cannot execute plans."""
        assert not hasattr(reviewer, "execute")
        assert validate_reviewer_has_no_authority(reviewer)
    
    def test_reviewer_has_no_approve_method(self, reviewer):
        """Reviewer cannot directly approve plans."""
        assert not hasattr(reviewer, "approve")
    
    def test_review_decision_is_advisory(
        self,
        reviewer,
        sample_strategic_intent,
        sample_tactical_intent,
        sample_planning_result,
        sample_validation_result,
        sample_dry_run_result,
        sample_strategic_context,
    ):
        """Review decision is properly labeled as advisory."""
        decision = reviewer.review_plan(
            sample_strategic_intent,
            sample_tactical_intent,
            sample_planning_result,
            sample_validation_result,
            sample_dry_run_result,
            sample_strategic_context,
        )
        
        assert validate_reviewer_is_advisory(decision)
        assert STRATEGIC_REVIEW_LABEL in decision.reason
    
    def test_unavailable_backend_returns_empty_review(
        self,
        unavailable_backend,
        sample_strategic_intent,
        sample_tactical_intent,
        sample_planning_result,
        sample_validation_result,
        sample_dry_run_result,
        sample_strategic_context,
    ):
        """Unavailable backend returns empty review, not failure."""
        reviewer = LLMStrategicReviewer(backend=unavailable_backend)
        
        review = reviewer.get_review_result(
            sample_strategic_intent,
            sample_tactical_intent,
            sample_planning_result,
            sample_validation_result,
            sample_dry_run_result,
            sample_strategic_context,
        )
        
        assert review.is_valid
        assert review.advisory_label == STRATEGIC_REVIEW_LABEL
    
    def test_disabled_reviewer_returns_empty_review(
        self,
        mock_backend,
        sample_strategic_intent,
        sample_tactical_intent,
        sample_planning_result,
        sample_validation_result,
        sample_dry_run_result,
        sample_strategic_context,
    ):
        """Disabled reviewer returns empty review."""
        config = StrategicReviewConfig(enabled=False)
        reviewer = LLMStrategicReviewer(backend=mock_backend, config=config)
        
        review = reviewer.get_review_result(
            sample_strategic_intent,
            sample_tactical_intent,
            sample_planning_result,
            sample_validation_result,
            sample_dry_run_result,
            sample_strategic_context,
        )
        
        assert review.is_valid
        assert "disabled" in review.concerns[0].description.lower()
    
    def test_invalid_llm_output_returns_failed_review(
        self,
        sample_strategic_intent,
        sample_tactical_intent,
        sample_planning_result,
        sample_validation_result,
        sample_dry_run_result,
        sample_strategic_context,
    ):
        """Invalid LLM output returns failed review, not exception."""
        backend = MockStrategicLLMBackend(response="not valid json at all")
        reviewer = LLMStrategicReviewer(backend=backend)
        
        review = reviewer.get_review_result(
            sample_strategic_intent,
            sample_tactical_intent,
            sample_planning_result,
            sample_validation_result,
            sample_dry_run_result,
            sample_strategic_context,
        )
        
        assert review.is_valid  # Still valid structure
        assert review.validation_errors  # But has errors logged
    
    def test_evidence_requirement_filters_risks(
        self,
        sample_strategic_intent,
        sample_tactical_intent,
        sample_planning_result,
        sample_validation_result,
        sample_dry_run_result,
        sample_strategic_context,
    ):
        """Risks without evidence are filtered when required."""
        response = json.dumps({
            "risks": [
                {
                    "id": "risk-with-evidence",
                    "description": "Has evidence",
                    "severity": "high",
                    "evidence": [{"source_type": "task", "source_id": "t1", "excerpt": "x"}],
                },
                {
                    "id": "risk-without-evidence",
                    "description": "No evidence",
                    "severity": "high",
                    "evidence": [],
                },
            ],
            "confidence": "medium",
        })
        backend = MockStrategicLLMBackend(response=response)
        config = StrategicReviewConfig(require_evidence=True)
        reviewer = LLMStrategicReviewer(backend=backend, config=config)
        
        review = reviewer.get_review_result(
            sample_strategic_intent,
            sample_tactical_intent,
            sample_planning_result,
            sample_validation_result,
            sample_dry_run_result,
            sample_strategic_context,
        )
        
        assert len(review.risks) == 1
        assert review.risks[0].id == "risk-with-evidence"


# =============================================================================
# Human Authority Tests
# =============================================================================


class TestHumanAuthority:
    """Tests that human authority is always final."""
    
    def test_human_rejection_overrides_ai_approval(
        self,
        reviewer,
        sample_strategic_intent,
        sample_tactical_intent,
        sample_planning_result,
        sample_validation_result,
        sample_dry_run_result,
        sample_strategic_context,
    ):
        """Human rejection overrides any AI recommendation."""
        # Get AI decision
        ai_decision = reviewer.review_plan(
            sample_strategic_intent,
            sample_tactical_intent,
            sample_planning_result,
            sample_validation_result,
            sample_dry_run_result,
            sample_strategic_context,
        )
        
        # Human rejects
        human_decision = HumanDecision(
            action=HumanDecisionAction.REJECT,
            user_id="test-user",
            rationale="I don't trust this",
        )
        
        handler = HumanDecisionHandler()
        final = handler.resolve(ai_decision, human_decision)
        
        assert not final.is_authorized
        assert final.verdict == StrategicDecisionType.REJECT
    
    def test_human_can_approve_without_ai(self):
        """Human can approve even if AI is unavailable."""
        # Create a decision with AI unavailable
        ai_decision = StrategicDecision(
            decision=StrategicDecisionType.APPROVE,
            reason="Rule-based approval",
        )
        
        human_decision = HumanDecision(
            action=HumanDecisionAction.APPROVE,
            user_id="test-user",
        )
        
        handler = HumanDecisionHandler()
        final = handler.resolve(ai_decision, human_decision)
        
        assert final.is_authorized
    
    def test_human_override_requires_rationale(self):
        """Human override requires rationale."""
        ai_decision = StrategicDecision(
            decision=StrategicDecisionType.REJECT,
            reason="AI says no",
        )
        
        # Override without rationale
        human_decision = HumanDecision(
            action=HumanDecisionAction.OVERRIDE,
            user_id="test-user",
            rationale=None,  # Missing rationale
        )
        
        handler = HumanDecisionHandler()
        final = handler.resolve(ai_decision, human_decision)
        
        # Without rationale, override should fail
        assert not final.is_authorized
    
    def test_human_override_with_rationale_succeeds(self):
        """Human override with rationale succeeds."""
        ai_decision = StrategicDecision(
            decision=StrategicDecisionType.REJECT,
            reason="AI says no",
        )
        
        # Override with rationale
        human_decision = HumanDecision(
            action=HumanDecisionAction.OVERRIDE,
            user_id="test-user",
            rationale="I know better in this case",
        )
        
        handler = HumanDecisionHandler()
        final = handler.resolve(ai_decision, human_decision)
        
        assert final.is_authorized


# =============================================================================
# Token Limit Tests
# =============================================================================


class TestTokenLimits:
    """Tests for token budget enforcement."""
    
    def test_config_validates_token_limits(self):
        """Config validates token limits."""
        config = StrategicReviewConfig(max_context_tokens=100000)
        errors = config.validate()
        assert any("cannot exceed" in e for e in errors)
    
    def test_config_validates_timeout(self):
        """Config validates timeout."""
        config = StrategicReviewConfig(timeout_seconds=1000)
        errors = config.validate()
        assert any("timeout" in e.lower() for e in errors)


# =============================================================================
# Canon Immutability Tests
# =============================================================================


class TestCanonImmutability:
    """Tests that Canon is never modified."""
    
    def test_review_does_not_modify_cpkg(
        self,
        reviewer,
        sample_strategic_intent,
        sample_tactical_intent,
        sample_planning_result,
        sample_validation_result,
        sample_dry_run_result,
    ):
        """Review does not modify CPKG."""
        cpkg = CPKG()
        original_nodes = len(cpkg.nodes)
        
        context = StrategicContext(cpkg=cpkg, ucir=UCIR(), bfm=BFM())
        
        reviewer.review_plan(
            sample_strategic_intent,
            sample_tactical_intent,
            sample_planning_result,
            sample_validation_result,
            sample_dry_run_result,
            context,
        )
        
        assert len(cpkg.nodes) == original_nodes
    
    def test_review_does_not_modify_plan(
        self,
        reviewer,
        sample_strategic_intent,
        sample_tactical_intent,
        sample_planning_result,
        sample_validation_result,
        sample_dry_run_result,
        sample_strategic_context,
    ):
        """Review does not modify the plan."""
        original_task_count = len(sample_planning_result.graph.tasks)
        
        reviewer.review_plan(
            sample_strategic_intent,
            sample_tactical_intent,
            sample_planning_result,
            sample_validation_result,
            sample_dry_run_result,
            sample_strategic_context,
        )
        
        assert len(sample_planning_result.graph.tasks) == original_task_count


# =============================================================================
# Validation Function Tests
# =============================================================================


class TestValidationFunctions:
    """Tests for validation helper functions."""
    
    def test_validate_review_is_advisory(self):
        """Validates review has advisory label."""
        valid_review = LLMStrategicReviewResult(review_id="r1")
        assert validate_review_is_advisory(valid_review)
    
    def test_validate_risks_have_evidence(self):
        """Validates all risks have evidence."""
        review = LLMStrategicReviewResult(
            review_id="r1",
            risks=[
                StrategicRisk(
                    id="risk-1",
                    category=RiskCategory.SAFETY,
                    description="Test",
                    severity=RiskSeverity.HIGH,
                    evidence=[],  # No evidence
                ),
            ],
        )
        missing = validate_risks_have_evidence(review)
        assert "risk-1" in missing
    
    def test_validate_confidence_is_stated(self):
        """Validates confidence is not UNKNOWN."""
        review_with_confidence = LLMStrategicReviewResult(
            review_id="r1",
            confidence=ConfidenceLevel.MEDIUM,
        )
        assert validate_confidence_is_stated(review_with_confidence)
        
        review_without_confidence = LLMStrategicReviewResult(
            review_id="r1",
            confidence=ConfidenceLevel.UNKNOWN,
        )
        assert not validate_confidence_is_stated(review_without_confidence)


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for the complete review flow."""
    
    def test_full_review_flow(
        self,
        reviewer,
        sample_strategic_intent,
        sample_tactical_intent,
        sample_planning_result,
        sample_validation_result,
        sample_dry_run_result,
        sample_strategic_context,
    ):
        """Full review flow from intent to decision."""
        # 1. Get LLM review
        review = reviewer.get_review_result(
            sample_strategic_intent,
            sample_tactical_intent,
            sample_planning_result,
            sample_validation_result,
            sample_dry_run_result,
            sample_strategic_context,
        )
        
        assert review.advisory_label == STRATEGIC_REVIEW_LABEL
        assert review.is_valid
        
        # 2. Get strategic decision
        decision = reviewer.review_plan(
            sample_strategic_intent,
            sample_tactical_intent,
            sample_planning_result,
            sample_validation_result,
            sample_dry_run_result,
            sample_strategic_context,
        )
        
        assert STRATEGIC_REVIEW_LABEL in decision.reason
        
        # 3. Human decides
        human_decision = HumanDecision(
            action=HumanDecisionAction.APPROVE,
            user_id="test-user",
        )
        
        handler = HumanDecisionHandler()
        final = handler.resolve(decision, human_decision)
        
        # Human has final say
        assert final.human_decision.action == HumanDecisionAction.APPROVE
    
    def test_backend_failure_does_not_block(
        self,
        unavailable_backend,
        sample_strategic_intent,
        sample_tactical_intent,
        sample_planning_result,
        sample_validation_result,
        sample_dry_run_result,
        sample_strategic_context,
    ):
        """Backend failure does not block the workflow."""
        reviewer = LLMStrategicReviewer(backend=unavailable_backend)
        
        # Review still completes (with empty result)
        decision = reviewer.review_plan(
            sample_strategic_intent,
            sample_tactical_intent,
            sample_planning_result,
            sample_validation_result,
            sample_dry_run_result,
            sample_strategic_context,
        )
        
        # Decision is still valid (escalate to human)
        assert decision.decision in [
            StrategicDecisionType.ESCALATE,
            StrategicDecisionType.APPROVE,
        ]
        
        # Human can still approve
        human_decision = HumanDecision(
            action=HumanDecisionAction.OVERRIDE,
            user_id="test-user",
            rationale="Proceeding without AI review",
        )
        
        handler = HumanDecisionHandler()
        final = handler.resolve(decision, human_decision)
        
        assert final.is_authorized
