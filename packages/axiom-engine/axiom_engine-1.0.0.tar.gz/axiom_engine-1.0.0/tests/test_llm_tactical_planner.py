"""
Tests for LLM Tactical Planner.

This test module verifies:
1. Valid LLM plans are accepted (after validation)
2. Invalid LLM plans are rejected with PlanningIssues
3. Cyclic graphs are rejected
4. Unknown Canon references are rejected
5. LLM unavailable → rule-based fallback works
6. All LLM-generated plans are labeled correctly

All tests verify that the LLM planner is ADVISORY only.
"""

import pytest
import json
from uuid import uuid4

from axiom_strata.llm_tactical_planner import (
    LLMTacticalPlanner,
    LLMPlanningInput,
    LLMPlanningHints,
    LLMPlanningOutput,
    LLMOutputParser,
    LLMPlanValidator,
    LLMConfidenceLevel,
    LLMUnavailableError,
    MockLLMBackend,
    TaskProposal,
    DependencyProposal,
    PlanningExplanation,
)
from axiom_strata.model import (
    TacticalIntent,
    PlanningContext,
    PlanningIssueType,
)
from axiom_strata.validation import validate_planning_result
from axiom_strata.dry_run import simulate_execution
from axiom_canon.cpkg import CPKG
from axiom_canon.ucir import UCIR
from axiom_canon.bfm import BusinessFlowMap


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def sample_intent() -> TacticalIntent:
    """Create a sample tactical intent."""
    return TacticalIntent(
        id=str(uuid4()),
        description="Run unit tests for the project",
        scope_ids=["src/"],
        constraints=["max_duration: 300s"],
    )


@pytest.fixture
def sample_context() -> PlanningContext:
    """Create a sample planning context."""
    return PlanningContext(
        cpkg=CPKG(nodes={}, edges=[]),
        ucir=UCIR(constraints={}),
        bfm=BusinessFlowMap(nodes={}, transitions=[]),
        project_root="/test/project",
    )


@pytest.fixture
def valid_llm_response() -> str:
    """Create a valid LLM response."""
    return json.dumps({
        "tasks": [
            {
                "id": "task-install",
                "name": "Install Dependencies",
                "description": "Install project dependencies",
                "command": "pip",
                "args": ["install", "-r", "requirements.txt"],
            },
            {
                "id": "task-test",
                "name": "Run Tests",
                "description": "Execute pytest suite",
                "command": "pytest",
                "args": ["tests/", "-v"],
            },
        ],
        "dependencies": [
            {"upstream": "task-install", "downstream": "task-test"},
        ],
        "explanation": {
            "reasoning": "Install dependencies before running tests to ensure all modules are available.",
            "assumptions": ["pytest is the test framework", "requirements.txt exists"],
            "uncertainties": ["Test directory structure may differ"],
        },
        "confidence": "high",
    })


@pytest.fixture
def cyclic_llm_response() -> str:
    """Create an LLM response with cyclic dependencies."""
    return json.dumps({
        "tasks": [
            {"id": "task-a", "name": "Task A", "description": "First task"},
            {"id": "task-b", "name": "Task B", "description": "Second task"},
            {"id": "task-c", "name": "Task C", "description": "Third task"},
        ],
        "dependencies": [
            {"upstream": "task-a", "downstream": "task-b"},
            {"upstream": "task-b", "downstream": "task-c"},
            {"upstream": "task-c", "downstream": "task-a"},  # Creates cycle
        ],
        "explanation": {"reasoning": "Cyclic plan"},
        "confidence": "medium",
    })


@pytest.fixture
def invalid_json_response() -> str:
    """Create an invalid JSON response."""
    return "This is not valid JSON { broken"


@pytest.fixture
def empty_tasks_response() -> str:
    """Create a response with no tasks."""
    return json.dumps({
        "tasks": [],
        "dependencies": [],
        "explanation": {"reasoning": "No tasks needed"},
        "confidence": "low",
    })


@pytest.fixture
def unknown_reference_response() -> str:
    """Create a response referencing unknown tasks."""
    return json.dumps({
        "tasks": [
            {"id": "task-a", "name": "Task A", "description": "A task"},
        ],
        "dependencies": [
            {"upstream": "task-unknown", "downstream": "task-a"},
        ],
        "explanation": {"reasoning": "References unknown task"},
        "confidence": "medium",
    })


# =============================================================================
# LLM OUTPUT PARSER TESTS
# =============================================================================


class TestLLMOutputParser:
    """Tests for LLM output parsing."""
    
    def test_parse_valid_json(self, valid_llm_response: str) -> None:
        """Valid JSON should parse successfully."""
        result = LLMOutputParser.parse(valid_llm_response)
        
        assert result.success is True
        assert result.output is not None
        assert len(result.output.tasks) == 2
        assert len(result.output.dependencies) == 1
        assert result.output.confidence == LLMConfidenceLevel.HIGH
    
    def test_parse_extracts_tasks(self, valid_llm_response: str) -> None:
        """Parser should extract all task fields."""
        result = LLMOutputParser.parse(valid_llm_response)
        
        assert result.success is True
        task = result.output.tasks[0]
        assert task.id == "task-install"
        assert task.name == "Install Dependencies"
        assert task.command == "pip"
        assert task.args == ["install", "-r", "requirements.txt"]
    
    def test_parse_extracts_dependencies(self, valid_llm_response: str) -> None:
        """Parser should extract dependencies."""
        result = LLMOutputParser.parse(valid_llm_response)
        
        assert result.success is True
        dep = result.output.dependencies[0]
        assert dep.upstream_id == "task-install"
        assert dep.downstream_id == "task-test"
    
    def test_parse_extracts_explanation(self, valid_llm_response: str) -> None:
        """Parser should extract explanation."""
        result = LLMOutputParser.parse(valid_llm_response)
        
        assert result.success is True
        explanation = result.output.explanation
        assert "Install dependencies" in explanation.reasoning
        assert len(explanation.assumptions) == 2
        assert len(explanation.uncertainties) == 1
    
    def test_parse_invalid_json_fails(self, invalid_json_response: str) -> None:
        """Invalid JSON should fail gracefully."""
        result = LLMOutputParser.parse(invalid_json_response)
        
        assert result.success is False
        assert result.error is not None
        assert "JSON" in result.error
    
    def test_parse_empty_response_fails(self) -> None:
        """Empty response should fail gracefully."""
        result = LLMOutputParser.parse("")
        
        assert result.success is False
        assert result.error is not None
        assert "empty" in result.error.lower()
    
    def test_parse_empty_tasks_fails(self, empty_tasks_response: str) -> None:
        """Response with no tasks should fail."""
        result = LLMOutputParser.parse(empty_tasks_response)
        
        assert result.success is False
        assert result.error is not None
        assert "no valid tasks" in result.error.lower()
    
    def test_parse_markdown_wrapped_json(self) -> None:
        """Parser should handle markdown-wrapped JSON."""
        response = '''Here's the plan:
```json
{
    "tasks": [{"id": "task-1", "name": "Test", "description": "Run tests"}],
    "dependencies": [],
    "explanation": {"reasoning": "Simple test"},
    "confidence": "medium"
}
```
That's the plan.'''
        
        result = LLMOutputParser.parse(response)
        
        assert result.success is True
        assert len(result.output.tasks) == 1
    
    def test_parse_unknown_confidence_defaults(self) -> None:
        """Unknown confidence should default to UNKNOWN."""
        response = json.dumps({
            "tasks": [{"id": "t1", "name": "Task", "description": "Desc"}],
            "dependencies": [],
            "explanation": {"reasoning": "Test"},
            "confidence": "very_high",  # Invalid value
        })
        
        result = LLMOutputParser.parse(response)
        
        assert result.success is True
        assert result.output.confidence == LLMConfidenceLevel.UNKNOWN
        assert len(result.warnings) > 0


# =============================================================================
# LLM PLAN VALIDATOR TESTS
# =============================================================================


class TestLLMPlanValidator:
    """Tests for LLM plan validation."""
    
    def test_validate_valid_plan(self, sample_context: PlanningContext) -> None:
        """Valid plan should pass validation."""
        output = LLMPlanningOutput(
            tasks=[
                TaskProposal(id="t1", name="Task 1", description="First"),
                TaskProposal(id="t2", name="Task 2", description="Second"),
            ],
            dependencies=[
                DependencyProposal(upstream_id="t1", downstream_id="t2"),
            ],
            explanation=PlanningExplanation(reasoning="Test"),
            confidence=LLMConfidenceLevel.HIGH,
        )
        
        result = LLMPlanValidator.validate(output, sample_context)
        
        assert result.is_valid is True
        assert len(result.issues) == 0
    
    def test_validate_detects_duplicate_ids(self, sample_context: PlanningContext) -> None:
        """Validator should detect duplicate task IDs."""
        output = LLMPlanningOutput(
            tasks=[
                TaskProposal(id="t1", name="Task 1", description="First"),
                TaskProposal(id="t1", name="Task 1 Again", description="Duplicate"),
            ],
            dependencies=[],
            explanation=PlanningExplanation(reasoning="Test"),
            confidence=LLMConfidenceLevel.HIGH,
        )
        
        result = LLMPlanValidator.validate(output, sample_context)
        
        assert result.is_valid is False
        assert any("Duplicate task ID" in i.message for i in result.issues)
    
    def test_validate_detects_unknown_upstream(self, sample_context: PlanningContext) -> None:
        """Validator should detect unknown upstream references."""
        output = LLMPlanningOutput(
            tasks=[
                TaskProposal(id="t1", name="Task 1", description="Only task"),
            ],
            dependencies=[
                DependencyProposal(upstream_id="unknown", downstream_id="t1"),
            ],
            explanation=PlanningExplanation(reasoning="Test"),
            confidence=LLMConfidenceLevel.HIGH,
        )
        
        result = LLMPlanValidator.validate(output, sample_context)
        
        assert result.is_valid is False
        assert any("unknown upstream" in i.message for i in result.issues)
    
    def test_validate_detects_unknown_downstream(self, sample_context: PlanningContext) -> None:
        """Validator should detect unknown downstream references."""
        output = LLMPlanningOutput(
            tasks=[
                TaskProposal(id="t1", name="Task 1", description="Only task"),
            ],
            dependencies=[
                DependencyProposal(upstream_id="t1", downstream_id="unknown"),
            ],
            explanation=PlanningExplanation(reasoning="Test"),
            confidence=LLMConfidenceLevel.HIGH,
        )
        
        result = LLMPlanValidator.validate(output, sample_context)
        
        assert result.is_valid is False
        assert any("unknown downstream" in i.message for i in result.issues)
    
    def test_validate_detects_self_dependency(self, sample_context: PlanningContext) -> None:
        """Validator should detect self-referencing dependencies."""
        output = LLMPlanningOutput(
            tasks=[
                TaskProposal(id="t1", name="Task 1", description="Self-ref"),
            ],
            dependencies=[
                DependencyProposal(upstream_id="t1", downstream_id="t1"),
            ],
            explanation=PlanningExplanation(reasoning="Test"),
            confidence=LLMConfidenceLevel.HIGH,
        )
        
        result = LLMPlanValidator.validate(output, sample_context)
        
        assert result.is_valid is False
        assert any("cannot depend on itself" in i.message for i in result.issues)
    
    def test_validate_detects_cycles(self, sample_context: PlanningContext) -> None:
        """Validator should detect cyclic dependencies."""
        output = LLMPlanningOutput(
            tasks=[
                TaskProposal(id="t1", name="Task 1", description="A"),
                TaskProposal(id="t2", name="Task 2", description="B"),
                TaskProposal(id="t3", name="Task 3", description="C"),
            ],
            dependencies=[
                DependencyProposal(upstream_id="t1", downstream_id="t2"),
                DependencyProposal(upstream_id="t2", downstream_id="t3"),
                DependencyProposal(upstream_id="t3", downstream_id="t1"),  # Cycle
            ],
            explanation=PlanningExplanation(reasoning="Test"),
            confidence=LLMConfidenceLevel.HIGH,
        )
        
        result = LLMPlanValidator.validate(output, sample_context)
        
        assert result.is_valid is False
        assert any("Cyclic dependency" in i.message for i in result.issues)
    
    def test_validate_detects_empty_task_name(self, sample_context: PlanningContext) -> None:
        """Validator should detect empty task names."""
        output = LLMPlanningOutput(
            tasks=[
                TaskProposal(id="t1", name="", description="No name"),
            ],
            dependencies=[],
            explanation=PlanningExplanation(reasoning="Test"),
            confidence=LLMConfidenceLevel.HIGH,
        )
        
        result = LLMPlanValidator.validate(output, sample_context)
        
        assert result.is_valid is False
        assert any("empty name" in i.message for i in result.issues)


# =============================================================================
# LLM TACTICAL PLANNER TESTS
# =============================================================================


class TestLLMTacticalPlanner:
    """Tests for the LLM Tactical Planner."""
    
    def test_valid_plan_accepted(
        self,
        sample_intent: TacticalIntent,
        sample_context: PlanningContext,
        valid_llm_response: str,
    ) -> None:
        """Valid LLM plan should be accepted."""
        backend = MockLLMBackend(
            available=True,
            default_response=valid_llm_response,
        )
        planner = LLMTacticalPlanner(llm_backend=backend)
        
        result = planner.plan(sample_intent, sample_context)
        
        assert result.success is True
        assert result.graph is not None
        assert len(result.graph.tasks) == 2
    
    def test_plan_labeled_as_ai_generated(
        self,
        sample_intent: TacticalIntent,
        sample_context: PlanningContext,
        valid_llm_response: str,
    ) -> None:
        """LLM-generated plan must be labeled."""
        backend = MockLLMBackend(
            available=True,
            default_response=valid_llm_response,
        )
        planner = LLMTacticalPlanner(llm_backend=backend)
        
        result = planner.plan(sample_intent, sample_context)
        
        assert result.graph is not None
        assert result.graph.metadata.get("label") == LLMTacticalPlanner.AI_GENERATED_LABEL
        assert result.graph.metadata.get("source") == "llm_tactical_planner"
    
    def test_is_llm_generated_detects_correctly(
        self,
        sample_intent: TacticalIntent,
        sample_context: PlanningContext,
        valid_llm_response: str,
    ) -> None:
        """is_llm_generated should correctly identify LLM plans."""
        backend = MockLLMBackend(
            available=True,
            default_response=valid_llm_response,
        )
        planner = LLMTacticalPlanner(llm_backend=backend)
        
        result = planner.plan(sample_intent, sample_context)
        
        assert planner.is_llm_generated(result) is True
    
    def test_explanation_extracted(
        self,
        sample_intent: TacticalIntent,
        sample_context: PlanningContext,
        valid_llm_response: str,
    ) -> None:
        """Explanation should be extractable from result."""
        backend = MockLLMBackend(
            available=True,
            default_response=valid_llm_response,
        )
        planner = LLMTacticalPlanner(llm_backend=backend)
        
        result = planner.plan(sample_intent, sample_context)
        explanation = planner.get_explanation(result)
        
        assert explanation is not None
        assert "Install dependencies" in explanation.reasoning
        assert len(explanation.assumptions) > 0
    
    def test_cyclic_plan_rejected(
        self,
        sample_intent: TacticalIntent,
        sample_context: PlanningContext,
        cyclic_llm_response: str,
    ) -> None:
        """Cyclic LLM plan should be rejected."""
        backend = MockLLMBackend(
            available=True,
            default_response=cyclic_llm_response,
        )
        planner = LLMTacticalPlanner(llm_backend=backend)
        
        result = planner.plan(sample_intent, sample_context)
        
        # Should fallback to rule-based
        assert any("fallback" in i.message.lower() for i in result.issues)
    
    def test_invalid_json_triggers_fallback(
        self,
        sample_intent: TacticalIntent,
        sample_context: PlanningContext,
        invalid_json_response: str,
    ) -> None:
        """Invalid JSON should trigger fallback."""
        backend = MockLLMBackend(
            available=True,
            default_response=invalid_json_response,
        )
        planner = LLMTacticalPlanner(llm_backend=backend)
        
        result = planner.plan(sample_intent, sample_context)
        
        # Should fallback to rule-based
        assert any("fallback" in i.message.lower() for i in result.issues)
    
    def test_unknown_reference_rejected(
        self,
        sample_intent: TacticalIntent,
        sample_context: PlanningContext,
        unknown_reference_response: str,
    ) -> None:
        """Unknown references should be rejected."""
        backend = MockLLMBackend(
            available=True,
            default_response=unknown_reference_response,
        )
        planner = LLMTacticalPlanner(llm_backend=backend)
        
        result = planner.plan(sample_intent, sample_context)
        
        # Should fallback to rule-based
        assert any("fallback" in i.message.lower() for i in result.issues)
    
    def test_llm_unavailable_uses_fallback(
        self,
        sample_intent: TacticalIntent,
        sample_context: PlanningContext,
    ) -> None:
        """LLM unavailability should use fallback."""
        backend = MockLLMBackend(available=False)
        planner = LLMTacticalPlanner(llm_backend=backend)
        
        result = planner.plan(sample_intent, sample_context)
        
        # Should use fallback
        assert any("fallback" in i.message.lower() for i in result.issues)
        assert "unavailable" in str(result.issues).lower()
    
    def test_llm_disabled_uses_fallback(
        self,
        sample_intent: TacticalIntent,
        sample_context: PlanningContext,
    ) -> None:
        """Disabled LLM should use fallback."""
        backend = MockLLMBackend(available=True)
        planner = LLMTacticalPlanner(
            llm_backend=backend,
            enable_llm=False,  # Explicitly disabled
        )
        
        result = planner.plan(sample_intent, sample_context)
        
        # Should use fallback
        assert any("fallback" in i.message.lower() for i in result.issues)
        assert "disabled" in str(result.issues).lower()
    
    def test_no_backend_uses_fallback(
        self,
        sample_intent: TacticalIntent,
        sample_context: PlanningContext,
    ) -> None:
        """No backend configured should use fallback."""
        planner = LLMTacticalPlanner(llm_backend=None)
        
        result = planner.plan(sample_intent, sample_context)
        
        # Should use fallback
        assert any("fallback" in i.message.lower() for i in result.issues)
    
    def test_low_confidence_warning(
        self,
        sample_intent: TacticalIntent,
        sample_context: PlanningContext,
    ) -> None:
        """Low confidence should add warning."""
        low_confidence_response = json.dumps({
            "tasks": [{"id": "t1", "name": "Test", "description": "Test"}],
            "dependencies": [],
            "explanation": {"reasoning": "Uncertain"},
            "confidence": "low",
        })
        backend = MockLLMBackend(
            available=True,
            default_response=low_confidence_response,
        )
        planner = LLMTacticalPlanner(llm_backend=backend)
        
        result = planner.plan(sample_intent, sample_context)
        
        assert result.success is True
        assert any("LOW confidence" in i.message for i in result.issues)
    
    def test_uncertainties_surfaced(
        self,
        sample_intent: TacticalIntent,
        sample_context: PlanningContext,
        valid_llm_response: str,
    ) -> None:
        """LLM uncertainties should be surfaced as warnings."""
        backend = MockLLMBackend(
            available=True,
            default_response=valid_llm_response,
        )
        planner = LLMTacticalPlanner(llm_backend=backend)
        
        result = planner.plan(sample_intent, sample_context)
        
        # The valid response has uncertainties
        assert any("uncertainty" in i.message.lower() for i in result.issues)


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestLLMPlannerIntegration:
    """Integration tests for LLM planner with validation pipeline."""
    
    def test_valid_plan_passes_validation(
        self,
        sample_intent: TacticalIntent,
        sample_context: PlanningContext,
        valid_llm_response: str,
    ) -> None:
        """Valid LLM plan should pass Canon validation."""
        backend = MockLLMBackend(
            available=True,
            default_response=valid_llm_response,
        )
        planner = LLMTacticalPlanner(llm_backend=backend)
        
        result = planner.plan(sample_intent, sample_context)
        
        # Run through standard validation
        validation = validate_planning_result(result)
        
        assert validation.is_valid is True
    
    def test_valid_plan_passes_dry_run(
        self,
        sample_intent: TacticalIntent,
        sample_context: PlanningContext,
        valid_llm_response: str,
    ) -> None:
        """Valid LLM plan should pass dry-run simulation."""
        backend = MockLLMBackend(
            available=True,
            default_response=valid_llm_response,
        )
        planner = LLMTacticalPlanner(llm_backend=backend)
        
        result = planner.plan(sample_intent, sample_context)
        
        # Run through dry-run simulation
        simulation = simulate_execution(result.graph)
        
        assert simulation.success is True
        assert simulation.deadlocked is False
        assert len(simulation.unreachable_tasks) == 0
    
    def test_planner_implements_protocol(self) -> None:
        """LLMTacticalPlanner should implement TacticalPlanner protocol."""
        from axiom_strata.interface import TacticalPlanner
        
        planner = LLMTacticalPlanner()
        
        # Check it has the required method
        assert hasattr(planner, "plan")
        assert callable(planner.plan)


# =============================================================================
# SAFETY INVARIANT TESTS
# =============================================================================


class TestLLMPlannerSafetyInvariants:
    """Tests for safety invariants of the LLM planner."""
    
    def test_planner_has_no_execute_method(self) -> None:
        """LLM planner should not have execute capability."""
        planner = LLMTacticalPlanner()
        
        assert not hasattr(planner, "execute")
        assert not hasattr(planner, "run")
        assert not hasattr(planner, "perform")
    
    def test_planner_has_no_approve_method(self) -> None:
        """LLM planner should not have approval capability."""
        planner = LLMTacticalPlanner()
        
        assert not hasattr(planner, "approve")
        assert not hasattr(planner, "authorize")
        assert not hasattr(planner, "ratify")
    
    def test_planner_has_no_canon_mutation(self) -> None:
        """LLM planner should not modify Canon."""
        planner = LLMTacticalPlanner()
        
        assert not hasattr(planner, "update_cpkg")
        assert not hasattr(planner, "write_canon")
        assert not hasattr(planner, "modify_ucir")
    
    def test_backend_prompt_excludes_secrets(
        self,
        sample_intent: TacticalIntent,
        sample_context: PlanningContext,
        valid_llm_response: str,
    ) -> None:
        """LLM prompt should not contain sensitive data."""
        backend = MockLLMBackend(
            available=True,
            default_response=valid_llm_response,
        )
        planner = LLMTacticalPlanner(llm_backend=backend)
        
        planner.plan(sample_intent, sample_context)
        
        # Check the prompt sent to the backend
        prompt = backend.get_last_prompt()
        assert prompt is not None
        
        # Should not contain sensitive patterns
        sensitive_patterns = [
            "password", "secret", "api_key", "token",
            "AWS_SECRET", "GITHUB_TOKEN",
        ]
        for pattern in sensitive_patterns:
            assert pattern.lower() not in prompt.lower()
    
    def test_label_constant_is_correct(self) -> None:
        """AI generated label should be the correct string."""
        assert LLMTacticalPlanner.AI_GENERATED_LABEL == "[AI GENERATED PLAN – NOT FINAL]"


# =============================================================================
# FALLBACK PLANNER TESTS
# =============================================================================


class TestFallbackBehavior:
    """Tests for fallback behavior."""
    
    def test_fallback_works_for_known_intents(
        self,
        sample_context: PlanningContext,
    ) -> None:
        """Fallback should work for known intents."""
        intent = TacticalIntent(
            id="test-id",
            description="run tests",  # Known to rule-based planner
        )
        
        planner = LLMTacticalPlanner(llm_backend=None)  # No LLM
        result = planner.plan(intent, sample_context)
        
        # Should use fallback successfully
        assert result.graph is not None
        assert "test" in result.graph.tasks.get("task-test", object()).name.lower() or len(result.graph.tasks) > 0
    
    def test_fallback_reports_reason(
        self,
        sample_intent: TacticalIntent,
        sample_context: PlanningContext,
    ) -> None:
        """Fallback should report why it was used."""
        planner = LLMTacticalPlanner(llm_backend=None)
        
        result = planner.plan(sample_intent, sample_context)
        
        # Should have fallback warning
        assert any(
            i.type == PlanningIssueType.UNSUPPORTED_OPERATION and "fallback" in i.message.lower()
            for i in result.issues
        )
