"""
Tests for the Axiom Onboarding Package.

This module provides comprehensive tests for:
- New Project Onboarding flow
- Existing Project Adoption flow
- First-Run Guardrails
- Configuration management
"""

import json
import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from axiom_onboarding import (
    # New project
    NewProjectOnboarding,
    OnboardingStep,
    OnboardingStepStatus,
    OnboardingState,
    OnboardingResult,
    OnboardingError,
    # Existing project
    ExistingProjectOnboarding,
    AdoptionStep,
    AdoptionStepStatus,
    AdoptionState,
    AdoptionResult,
    AdoptionError,
    # Guardrails
    FirstRunGuard,
    GuardrailViolation,
    GuardrailCheck,
    GuardrailResult,
    GuardrailLevel,
    GuardrailCategory,
    GuardrailOutcome,
    # Configuration
    ExecutorConfiguration,
    ExecutorConfig,
    ExecutorType,
    ExecutorCapability,
    PolicyConfiguration,
    Policy,
    PolicyLevel,
    PolicyAction,
    ConfigurationValidator,
    ConfigurationManager,
    ConfigurationError,
    TokenManager,
    TokenConfig,
    # IDE Templates
    InteractionTemplate,
    InteractionPrompt,
    InteractionType,
    InteractionOwner,
    PromptGenerator,
    CopilotHelper,
    TEMPLATES,
    get_template,
    list_templates,
    get_full_documentation,
    label_ai_advisory,
    label_ai_generated,
    label_human_decision,
)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a sample project structure
        project_dir = Path(tmpdir) / "sample_project"
        project_dir.mkdir()
        
        # Create sample source files
        src_dir = project_dir / "src"
        src_dir.mkdir()
        
        (src_dir / "main.py").write_text('''
"""Main module."""

def main():
    """Entry point."""
    print("Hello, World!")

if __name__ == "__main__":
    main()
''')
        
        (src_dir / "utils.py").write_text('''
"""Utility functions."""

def helper():
    """A helper function."""
    return 42
''')
        
        # Create tests
        tests_dir = project_dir / "tests"
        tests_dir.mkdir()
        
        (tests_dir / "test_main.py").write_text('''
"""Tests for main module."""

def test_sample():
    assert True
''')
        
        # Create README
        (project_dir / "README.md").write_text("# Sample Project")
        
        yield project_dir


@pytest.fixture
def empty_project_dir():
    """Create an empty project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir) / "empty_project"
        project_dir.mkdir()
        yield project_dir


@pytest.fixture
def mock_human_interface():
    """Create a mock human interface for testing."""
    interface = MagicMock()
    interface.confirm.return_value = True
    interface.present.return_value = None
    interface.request_decision.return_value = "approve"
    return interface


# =============================================================================
# New Project Onboarding Tests
# =============================================================================


class TestOnboardingStep:
    """Tests for OnboardingStep enum."""
    
    def test_step_values(self):
        """Test that all expected steps exist."""
        expected_steps = [
            "initialize",
            "bootstrap",
            "configure",
            "discover",
            "enrich",
            "review",
            "promote",
            "document",
            "validate",
            "first_run",
        ]
        
        for step_value in expected_steps:
            step = OnboardingStep(step_value)
            assert step.value == step_value
    
    def test_step_ordering(self):
        """Test that steps have proper ordering."""
        steps = list(OnboardingStep)
        assert steps[0] == OnboardingStep.INITIALIZE
        assert steps[-1] == OnboardingStep.FIRST_RUN


class TestOnboardingState:
    """Tests for OnboardingState."""
    
    def test_initialization(self):
        """Test state initialization."""
        state = OnboardingState(project_path="/test/path")
        
        assert state.project_path == "/test/path"
        assert state.current_step == OnboardingStep.INITIALIZE
        assert len(state.completed_steps) == 0
    
    def test_mark_completed(self):
        """Test marking steps as completed."""
        state = OnboardingState(project_path="/test/path")
        
        state.mark_completed(OnboardingStep.INITIALIZE)
        assert OnboardingStep.INITIALIZE in state.completed_steps
        
        # Should advance to next step
        assert state.current_step == OnboardingStep.BOOTSTRAP


class TestNewProjectOnboarding:
    """Tests for NewProjectOnboarding class."""
    
    def test_initialization(self, empty_project_dir, mock_human_interface):
        """Test onboarding initialization."""
        onboarding = NewProjectOnboarding(
            project_path=str(empty_project_dir),
        )
        
        assert onboarding.state.project_path == str(empty_project_dir)
        assert onboarding.state.current_step == OnboardingStep.INITIALIZE
    
    def test_step_initialize(self, empty_project_dir, mock_human_interface):
        """Test the initialize step."""
        onboarding = NewProjectOnboarding(
            project_path=str(empty_project_dir),
        )
        
        result = onboarding.step_initialize()
        
        assert result.success
        assert result.step == OnboardingStep.INITIALIZE
        assert (empty_project_dir / ".axiom").exists()
        assert (empty_project_dir / ".axiom" / "canon").exists()
    
    def test_step_initialize_already_exists(self, empty_project_dir, mock_human_interface):
        """Test initialize step when .axiom already exists."""
        (empty_project_dir / ".axiom").mkdir()
        
        onboarding = NewProjectOnboarding(
            project_path=str(empty_project_dir),
        )
        
        result = onboarding.step_initialize()
        
        # Should succeed - creates additional structure
        assert result.success
    
    def test_step_sequencing_enforced(self, empty_project_dir, mock_human_interface):
        """Test that step sequencing is enforced."""
        onboarding = NewProjectOnboarding(
            project_path=str(empty_project_dir),
        )
        
        # Try to skip to bootstrap without initialize
        result = onboarding.step_bootstrap()
        
        # Should fail because initialize is not complete
        assert not result.success
    
    def test_full_onboarding_flow(self, empty_project_dir, mock_human_interface):
        """Test the first few steps of the onboarding flow."""
        onboarding = NewProjectOnboarding(
            project_path=str(empty_project_dir),
        )
        
        # Step 1: Initialize
        result = onboarding.step_initialize()
        assert result.success, f"Initialize failed: {result.message}"
        
        # Step 2: Bootstrap Canon
        result = onboarding.step_bootstrap()
        assert result.success, f"Bootstrap failed: {result.message}"


# =============================================================================
# Existing Project Adoption Tests
# =============================================================================


class TestAdoptionStep:
    """Tests for AdoptionStep enum."""
    
    def test_step_values(self):
        """Test that all expected steps exist."""
        expected_steps = [
            "analyze",
            "initialize",
            "extract",
            "enrich",
            "review",
            "promote",
            "integrate",
            "validate",
            "pilot",
        ]
        
        for step_value in expected_steps:
            step = AdoptionStep(step_value)
            assert step.value == step_value


class TestExistingProjectOnboarding:
    """Tests for ExistingProjectOnboarding class."""
    
    def test_initialization(self, temp_project_dir):
        """Test adoption initialization."""
        adoption = ExistingProjectOnboarding(str(temp_project_dir))
        
        assert adoption.state.project_path == str(temp_project_dir)
        assert adoption.state.current_step == AdoptionStep.ANALYZE
    
    def test_invalid_path(self):
        """Test initialization with invalid path."""
        with pytest.raises(AdoptionError):
            ExistingProjectOnboarding("/nonexistent/path")
    
    def test_step_analyze(self, temp_project_dir):
        """Test the analyze step."""
        adoption = ExistingProjectOnboarding(str(temp_project_dir))
        
        result = adoption.step_analyze()
        
        assert result.success
        assert result.step == AdoptionStep.ANALYZE
        assert adoption.state.analysis is not None
        assert adoption.state.analysis.source_files > 0
        assert "Python" in adoption.state.analysis.languages
    
    def test_step_initialize(self, temp_project_dir):
        """Test the initialize step."""
        adoption = ExistingProjectOnboarding(str(temp_project_dir))
        
        # First analyze
        adoption.step_analyze()
        
        # Then initialize
        result = adoption.step_initialize()
        
        assert result.success
        assert (temp_project_dir / ".axiom").exists()
        assert (temp_project_dir / ".axiom" / "config.json").exists()
    
    def test_step_sequencing_enforced(self, temp_project_dir):
        """Test that step sequencing is enforced."""
        adoption = ExistingProjectOnboarding(str(temp_project_dir))
        
        # Try to skip to initialize without analyze
        result = adoption.step_initialize()
        
        # Should fail because analyze is not complete
        assert not result.success
    
    def test_incremental_extraction(self, temp_project_dir):
        """Test incremental extraction."""
        adoption = ExistingProjectOnboarding(str(temp_project_dir))
        
        # Complete prerequisites
        adoption.step_analyze()
        adoption.step_initialize()
        
        # First extraction
        result1 = adoption.step_extract(paths=["src/main.py"])
        assert result1.success
        
        # Second extraction (incremental)
        result2 = adoption.step_extract(paths=["src/utils.py"], incremental=True)
        assert result2.success
    
    def test_progress_display(self, temp_project_dir):
        """Test progress display."""
        adoption = ExistingProjectOnboarding(str(temp_project_dir))
        adoption.step_analyze()
        
        progress = adoption.get_progress()
        
        assert "AXIOM EXISTING PROJECT ADOPTION" in progress
        assert "Analyze Project" in progress or "analyze" in progress.lower()
    
    def test_rollback(self, temp_project_dir):
        """Test rollback functionality."""
        adoption = ExistingProjectOnboarding(str(temp_project_dir))
        
        # Complete some steps
        adoption.step_analyze()
        adoption.step_initialize()
        
        # Verify .axiom exists
        assert (temp_project_dir / ".axiom").exists()
        
        # Rollback
        result = adoption.rollback()
        
        assert result.success
        assert not (temp_project_dir / ".axiom").exists()


# =============================================================================
# First-Run Guardrails Tests
# =============================================================================


class TestFirstRunGuard:
    """Tests for FirstRunGuard class."""
    
    def test_initialization(self):
        """Test guard initialization."""
        guard = FirstRunGuard()
        
        assert len(guard.checks) > 0
        assert "approval_required" in guard.checks
        assert "step_sequencing" in guard.checks
    
    def test_require_approval_passed(self):
        """Test approval check when approved."""
        guard = FirstRunGuard()
        
        result = guard.require_approval(
            action="test action",
            approved=True,
        )
        
        assert result.passed
        assert result.outcome == GuardrailOutcome.PASSED
    
    def test_require_approval_failed(self):
        """Test approval check when not approved."""
        guard = FirstRunGuard()
        
        with pytest.raises(GuardrailViolation) as exc_info:
            guard.require_approval(
                action="test action",
                approved=False,
            )
        
        assert "GUARDRAIL VIOLATION" in str(exc_info.value)
        assert "test action" in str(exc_info.value).lower()
    
    def test_require_step_order_passed(self):
        """Test step order check when valid."""
        guard = FirstRunGuard()
        
        result = guard.require_step_order(
            current_step="extract",
            required_step="initialize",
            step_complete=True,
        )
        
        assert result.passed
    
    def test_require_step_order_failed(self):
        """Test step order check when invalid."""
        guard = FirstRunGuard()
        
        with pytest.raises(GuardrailViolation):
            guard.require_step_order(
                current_step="extract",
                required_step="initialize",
                step_complete=False,
            )
    
    def test_require_ai_label(self):
        """Test AI labeling check."""
        guard = FirstRunGuard()
        
        # Labeled content passes
        result = guard.require_ai_label(
            content="AI generated content",
            is_labeled=True,
        )
        assert result.passed
        
        # Unlabeled content fails
        with pytest.raises(GuardrailViolation):
            guard.require_ai_label(
                content="AI generated content",
                is_labeled=False,
            )
    
    def test_ai_labeling_helpers(self):
        """Test AI labeling helper methods."""
        # Advisory label
        labeled = FirstRunGuard.label_ai_advisory("Test content")
        assert "AI ADVISORY" in labeled
        assert "Human review" in labeled or "REQUIRED" in labeled
        
        # Generated label
        labeled = FirstRunGuard.label_ai_generated("Test content", "testing")
        assert "AI-GENERATED" in labeled
        
        # Human decision label
        labeled = FirstRunGuard.label_human_decision("Test decision", "Admin")
        assert "HUMAN DECISION" in labeled
        assert "Admin" in labeled
    
    def test_get_summary(self):
        """Test guard summary."""
        guard = FirstRunGuard()
        
        # Run some checks
        guard.require_approval("action1", approved=True)
        guard.require_step_order("step2", "step1", step_complete=True)
        
        summary = guard.get_summary()
        
        assert "GUARDRAIL CHECK SUMMARY" in summary
        assert "Passed" in summary


class TestGuardrailViolation:
    """Tests for GuardrailViolation exception."""
    
    def test_violation_message(self):
        """Test violation message formatting."""
        check = GuardrailCheck(
            id="test_check",
            name="Test Check",
            description="A test check",
            category=GuardrailCategory.APPROVAL,
            level=GuardrailLevel.CRITICAL,
            explanation="Test explanation",
            remediation="Test remediation",
        )
        
        result = GuardrailResult(
            check=check,
            outcome=GuardrailOutcome.FAILED,
            message="Test failure",
            blocked_action="test action",
        )
        
        violation = GuardrailViolation(
            result=result,
            action="test action",
            explanation="Custom explanation",
            remediation="Custom remediation",
        )
        
        message = str(violation)
        
        assert "GUARDRAIL VIOLATION" in message
        assert "test action" in message.lower()
        assert "Custom explanation" in message
        assert "Custom remediation" in message


# =============================================================================
# Configuration Tests
# =============================================================================


class TestExecutorConfiguration:
    """Tests for ExecutorConfiguration."""
    
    def test_safe_default(self):
        """Test safe default configuration."""
        config = ExecutorConfiguration.create_safe_default()
        
        assert len(config.executors) > 0
        assert "shell" in config.executors
        
        shell_config = config.executors["shell"]
        assert shell_config.require_approval is True
        assert shell_config.enabled is True
    
    def test_add_executor(self):
        """Test adding an executor."""
        config = ExecutorConfiguration()
        
        exec_config = ExecutorConfig(
            executor_type=ExecutorType.SHELL,
            enabled=True,
            capabilities=[ExecutorCapability.FILE_READ],
        )
        
        config.add_executor("test_shell", exec_config)
        
        assert "test_shell" in config.executors
        assert config.is_enabled("test_shell")
    
    def test_serialization(self):
        """Test configuration serialization."""
        config = ExecutorConfiguration.create_safe_default()
        
        # Serialize
        data = config.to_dict()
        assert "executors" in data
        assert "shell" in data["executors"]
        
        # Deserialize
        restored = ExecutorConfiguration.from_dict(data)
        assert len(restored.executors) == len(config.executors)
        assert restored.default_executor == config.default_executor


class TestPolicyConfiguration:
    """Tests for PolicyConfiguration."""
    
    def test_safe_default(self):
        """Test safe default policy configuration."""
        config = PolicyConfiguration.create_safe_default()
        
        assert config.require_human_approval is True
        assert config.default_action == PolicyAction.REQUIRE_APPROVAL
        assert len(config.policies) > 0
    
    def test_policy_evaluation(self):
        """Test policy evaluation."""
        config = PolicyConfiguration.create_safe_default()
        
        # Evaluate with matching conditions
        action = config.evaluate(
            action="code_change",
            context={"type": "code_change"},
        )
        
        assert action == PolicyAction.REQUIRE_APPROVAL
    
    def test_add_policy(self):
        """Test adding a policy."""
        config = PolicyConfiguration()
        
        policy = Policy(
            id="test_policy",
            name="Test Policy",
            description="A test policy",
            level=PolicyLevel.GLOBAL,
            action=PolicyAction.ALLOW,
        )
        
        config.add_policy(policy)
        
        assert "test_policy" in config.policies
        assert config.get_policy("test_policy") == policy
    
    def test_serialization(self):
        """Test policy serialization."""
        config = PolicyConfiguration.create_safe_default()
        
        data = config.to_dict()
        restored = PolicyConfiguration.from_dict(data)
        
        assert len(restored.policies) == len(config.policies)
        assert restored.default_action == config.default_action


class TestConfigurationValidator:
    """Tests for ConfigurationValidator."""
    
    def test_validate_executor_config(self):
        """Test executor configuration validation."""
        validator = ConfigurationValidator()
        
        # Valid configuration
        config = ExecutorConfiguration.create_safe_default()
        result = validator.validate_executor_config(config)
        
        assert result.valid
        assert len(result.errors) == 0
    
    def test_validate_empty_config(self):
        """Test validation of empty configuration."""
        validator = ConfigurationValidator()
        
        config = ExecutorConfiguration()
        result = validator.validate_executor_config(config)
        
        assert not result.valid
        assert len(result.errors) > 0
    
    def test_validate_dangerous_commands(self):
        """Test validation catches dangerous commands."""
        validator = ConfigurationValidator()
        
        config = ExecutorConfiguration()
        exec_config = ExecutorConfig(
            executor_type=ExecutorType.SHELL,
            allowed_commands=["rm -rf"],  # Dangerous!
        )
        config.add_executor("dangerous_shell", exec_config)
        config.default_executor = "dangerous_shell"
        
        result = validator.validate_executor_config(config)
        
        assert not result.valid
        assert any("dangerous" in e.lower() for e in result.errors)
    
    def test_validate_policy_config(self):
        """Test policy configuration validation."""
        validator = ConfigurationValidator()
        
        config = PolicyConfiguration.create_safe_default()
        result = validator.validate_policy_config(config)
        
        assert result.valid


class TestConfigurationManager:
    """Tests for ConfigurationManager."""
    
    def test_create_defaults(self):
        """Test creating default configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".axiom"
            config_dir.mkdir()
            
            manager = ConfigurationManager(str(config_dir))
            manager.create_defaults()
            
            assert (config_dir / "executors.json").exists()
            assert (config_dir / "policies.json").exists()
    
    def test_load_configuration(self):
        """Test loading configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".axiom"
            config_dir.mkdir()
            
            # Create defaults
            manager = ConfigurationManager(str(config_dir))
            manager.create_defaults()
            
            # Load again
            manager2 = ConfigurationManager(str(config_dir))
            manager2.load()
            
            assert manager2.executor_config is not None
            assert manager2.policy_config is not None
    
    def test_configuration_guide(self):
        """Test configuration guide."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigurationManager(tmpdir)
            
            guide = manager.get_configuration_guide()
            
            assert "CONFIGURATION GUIDE" in guide
            assert "EXECUTOR" in guide
            assert "POLICY" in guide


class TestTokenManager:
    """Tests for TokenManager."""
    
    def test_register_token(self):
        """Test token registration."""
        manager = TokenManager()
        
        manager.register_token(
            token_id="test_token",
            token_type="api_key",
            env_variable="TEST_API_KEY",
            service="Test Service",
        )
        
        assert "test_token" in manager.tokens
    
    def test_get_token_from_env(self):
        """Test getting token from environment."""
        manager = TokenManager()
        
        manager.register_token(
            token_id="env_token",
            token_type="api_key",
            env_variable="AXIOM_TEST_TOKEN",
            service="Test",
        )
        
        # Without env var set
        assert manager.get_token("env_token") is None
        
        # With env var set
        os.environ["AXIOM_TEST_TOKEN"] = "secret123"
        try:
            assert manager.get_token("env_token") == "secret123"
            assert manager.validate_token("env_token")
        finally:
            del os.environ["AXIOM_TEST_TOKEN"]
    
    def test_get_missing_tokens(self):
        """Test getting list of missing tokens."""
        manager = TokenManager()
        
        manager.register_token(
            token_id="missing1",
            token_type="api_key",
            env_variable="MISSING_TOKEN_1",
            service="Service1",
        )
        manager.register_token(
            token_id="missing2",
            token_type="api_key",
            env_variable="MISSING_TOKEN_2",
            service="Service2",
        )
        
        missing = manager.get_missing_tokens()
        
        assert "missing1" in missing
        assert "missing2" in missing
    
    def test_token_guide(self):
        """Test token guide generation."""
        manager = TokenManager()
        
        manager.register_token(
            token_id="test",
            token_type="api_key",
            env_variable="TEST_TOKEN",
            service="Test Service",
        )
        
        guide = manager.get_token_guide()
        
        assert "TOKEN CONFIGURATION GUIDE" in guide
        assert "TEST_TOKEN" in guide
        assert "Test Service" in guide


# =============================================================================
# Integration Tests
# =============================================================================


class TestOnboardingIntegration:
    """Integration tests for onboarding flows."""
    
    def test_new_project_with_guardrails(self, empty_project_dir, mock_human_interface):
        """Test new project onboarding with guardrails."""
        guard = FirstRunGuard()
        onboarding = NewProjectOnboarding(
            project_path=str(empty_project_dir),
        )
        
        # Initialize (no approval needed for initialization)
        result = onboarding.step_initialize()
        assert result.success
        
        # Bootstrap with step order check
        guard.require_step_order(
            current_step="bootstrap",
            required_step="initialize",
            step_complete=OnboardingStep.INITIALIZE in onboarding.state.completed_steps,
        )
        result = onboarding.step_bootstrap()
        assert result.success
    
    def test_adoption_with_configuration(self, temp_project_dir):
        """Test adoption with configuration management."""
        adoption = ExistingProjectOnboarding(str(temp_project_dir))
        
        # Analyze and initialize
        adoption.step_analyze()
        adoption.step_initialize()
        
        # Load configuration
        axiom_dir = temp_project_dir / ".axiom"
        manager = ConfigurationManager(str(axiom_dir))
        manager.create_defaults()
        
        # Verify configuration exists
        assert (axiom_dir / "executors.json").exists()
        assert (axiom_dir / "policies.json").exists()
        
        # Continue adoption
        adoption.step_extract()
        adoption.skip_enrich()
        
        # Verify state
        assert adoption.state.current_step == AdoptionStep.REVIEW


class TestConfigurationIntegration:
    """Integration tests for configuration."""
    
    def test_full_configuration_workflow(self):
        """Test full configuration workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            
            # Create manager
            manager = ConfigurationManager(str(config_dir))
            
            # Create safe defaults
            manager.create_defaults()
            
            # Reload and validate
            manager2 = ConfigurationManager(str(config_dir))
            manager2.load()
            
            # Validate
            validator = ConfigurationValidator()
            result = validator.validate_all(
                manager2.executor_config,
                manager2.policy_config,
            )
            
            assert result.valid


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_onboarding_nonexistent_path(self, mock_human_interface):
        """Test onboarding with nonexistent path (should create it)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # NewProjectOnboarding allows creating new projects
            onboarding = NewProjectOnboarding(
                project_path=str(Path(tmpdir) / "new_project"),
            )
            # Should work - will create directory on initialize
            assert onboarding.state.project_path is not None
    
    def test_guardrail_strict_mode(self):
        """Test guardrails in strict mode."""
        guard = FirstRunGuard(strict_mode=True)
        
        # Even warnings should be treated more seriously in strict mode
        assert guard.strict_mode is True
    
    def test_configuration_error_message(self):
        """Test configuration error message formatting."""
        error = ConfigurationError(
            message="Test error",
            field="test_field",
            value="invalid",
            reason="Value is not valid",
            fix="Use a valid value",
        )
        
        message = str(error)
        
        assert "CONFIGURATION ERROR" in message
        assert "test_field" in message
        assert "invalid" in message
        assert "Use a valid value" in message
    
    def test_adoption_already_initialized(self, temp_project_dir):
        """Test adoption when .axiom already exists."""
        # Create .axiom directory
        (temp_project_dir / ".axiom").mkdir()
        
        adoption = ExistingProjectOnboarding(str(temp_project_dir))
        adoption.step_analyze()
        
        result = adoption.step_initialize()
        
        # Should handle gracefully
        assert not result.success or "already" in result.message.lower()


# =============================================================================
# IDE Template Tests
# =============================================================================


class TestInteractionTemplate:
    """Tests for InteractionTemplate."""
    
    def test_template_fields(self):
        """Test template has required fields."""
        template = InteractionTemplate(
            id="test",
            name="Test Template",
            interaction_type=InteractionType.DRAFT_INTENT,
            owner=InteractionOwner.USER,
            description="A test template",
        )
        
        assert template.id == "test"
        assert template.name == "Test Template"
        assert template.interaction_type == InteractionType.DRAFT_INTENT
        assert template.owner == InteractionOwner.USER
    
    def test_get_template(self):
        """Test retrieving template by ID."""
        template = get_template("draft_intent")
        
        assert template is not None
        assert template.id == "draft_intent"
        assert template.interaction_type == InteractionType.DRAFT_INTENT
    
    def test_get_template_not_found(self):
        """Test retrieving nonexistent template."""
        template = get_template("nonexistent")
        
        assert template is None
    
    def test_list_templates(self):
        """Test listing all templates."""
        templates = list_templates()
        
        assert len(templates) >= 5  # At least 5 standard templates
        
        # Check standard templates exist
        template_ids = [t.id for t in templates]
        assert "draft_intent" in template_ids
        assert "preview_plan" in template_ids
        assert "request_approval" in template_ids
        assert "execute_plan" in template_ids
        assert "review_result" in template_ids


class TestPromptGenerator:
    """Tests for PromptGenerator."""
    
    def test_generate_intent_prompt(self):
        """Test generating intent prompt."""
        prompt = PromptGenerator.generate_intent_prompt(
            description="Add validation to user form",
            scope_ids=["component_user_form"],
            constraints=["Must not break existing tests"],
        )
        
        assert "DRAFT TACTICAL INTENT" in prompt
        assert "Add validation to user form" in prompt
        assert "component_user_form" in prompt
        assert "Must not break existing tests" in prompt
    
    def test_generate_approval_prompt(self):
        """Test generating approval prompt."""
        prompt = PromptGenerator.generate_approval_prompt(
            intent_description="Add validation",
            task_count=3,
            files_affected=["file1.py", "file2.py"],
            risk_level="low",
        )
        
        assert "APPROVAL REQUIRED" in prompt
        assert "Add validation" in prompt
        assert "3 tasks" in prompt
        assert "file1.py" in prompt
        assert "LOW" in prompt
    
    def test_generate_execution_summary(self):
        """Test generating execution summary."""
        summary = PromptGenerator.generate_execution_summary(
            intent_description="Add validation",
            success=True,
            tasks_completed=3,
            files_changed=["file1.py", "file2.py"],
            errors=[],
        )
        
        assert "SUCCESS" in summary
        assert "Add validation" in summary
        assert "3" in summary
        assert "No errors" in summary


class TestCopilotHelper:
    """Tests for CopilotHelper."""
    
    def test_format_for_copilot(self):
        """Test formatting for Copilot."""
        formatted = CopilotHelper.format_for_copilot("Test prompt")
        
        assert "Axiom Interaction Request" in formatted
        assert "Test prompt" in formatted
        assert "Instructions for Copilot" in formatted
    
    def test_create_intent_stub(self):
        """Test creating intent code stub."""
        stub = CopilotHelper.create_intent_stub("Add validation feature")
        
        assert "TacticalIntent" in stub
        assert "Add validation feature" in stub
        assert "scope_ids" in stub
        assert "constraints" in stub
    
    def test_create_workflow_stub(self):
        """Test creating workflow code stub."""
        stub = CopilotHelper.create_workflow_stub()
        
        assert "AxiomWorkflow" in stub
        assert "ConsoleHumanInterface" in stub
        assert "workflow.run" in stub


class TestAILabeling:
    """Tests for AI labeling utilities."""
    
    def test_label_ai_advisory(self):
        """Test AI advisory labeling."""
        labeled = label_ai_advisory("Test content")
        
        assert "AI ADVISORY" in labeled
        assert "Test content" in labeled
        assert "Human review" in labeled or "REQUIRED" in labeled
    
    def test_label_ai_generated(self):
        """Test AI generated labeling."""
        labeled = label_ai_generated("Test content")
        
        assert "AI-GENERATED" in labeled
        assert "Test content" in labeled
    
    def test_label_human_decision(self):
        """Test human decision labeling."""
        labeled = label_human_decision("Test decision")
        
        assert "HUMAN DECISION" in labeled
        assert "Test decision" in labeled


class TestTemplateDocumentation:
    """Tests for template documentation."""
    
    def test_get_full_documentation(self):
        """Test getting full documentation."""
        docs = get_full_documentation()
        
        assert "AXIOM COPILOT/IDE INTERACTION TEMPLATES" in docs
        assert "PRINCIPLES" in docs
        assert "Draft Tactical Intent" in docs
        assert "Preview Plan" in docs
        assert "Request Human Approval" in docs

