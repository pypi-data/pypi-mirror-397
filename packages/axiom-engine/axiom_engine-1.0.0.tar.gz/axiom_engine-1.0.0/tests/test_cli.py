"""
Tests for Axiom CLI.

These tests verify that:
1. CLI commands respect workflow order
2. CLI output matches actual workflow state
3. CLI cannot bypass governance or approval
4. All output is properly labeled
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from axiom_cli.output import (
    OutputLabeler,
    OutputLabel,
    print_ai_advisory,
    print_ai_generated,
    print_human_decision,
    print_system_validation,
)
from axiom_cli.workflow_state import (
    WorkflowState,
    WorkflowPhase,
    load_workflow_state,
    save_workflow_state,
)
from axiom_cli.preconditions import (
    PreconditionChecker,
    PreconditionError,
)
from axiom_cli.main import (
    cli,
    cmd_init,
    cmd_plan,
    cmd_preview,
    cmd_approve,
    cmd_execute,
    cmd_status,
)
from axiom_cli.ide_surface import (
    IDECommand,
    CommandCategory,
    IDE_COMMANDS,
    get_command,
    generate_vscode_commands,
    generate_command_mapping,
)
from axiom_cli.copilot_templates import (
    CopilotTemplate,
    TemplateType,
    TEMPLATES,
    get_template,
    get_copilot_instructions,
    format_advisory_response,
)


# =============================================================================
# Output Labeling Tests
# =============================================================================


class TestOutputLabeling(unittest.TestCase):
    """Tests for output labeling."""
    
    def test_output_labels_exist(self):
        """Verify all required output labels exist."""
        required_labels = [
            OutputLabel.AI_ADVISORY,
            OutputLabel.AI_GENERATED,
            OutputLabel.HUMAN_DECISION,
            OutputLabel.SYSTEM_VALIDATION,
        ]
        for label in required_labels:
            self.assertIsInstance(label.value, str)
    
    def test_labeler_formats_ai_advisory(self):
        """Verify AI advisory messages are labeled."""
        labeler = OutputLabeler(use_color=False)
        result = labeler.ai_advisory("Test message")
        self.assertIn("[AI Advisory]", result)
        self.assertIn("Test message", result)
    
    def test_labeler_formats_ai_generated(self):
        """Verify AI generated messages are labeled."""
        labeler = OutputLabeler(use_color=False)
        result = labeler.ai_generated("Generated code")
        self.assertIn("[AI Generated]", result)
        self.assertIn("Generated code", result)
    
    def test_labeler_formats_human_decision(self):
        """Verify human decision messages are labeled."""
        labeler = OutputLabeler(use_color=False)
        result = labeler.human_decision("Approved")
        self.assertIn("[Human Decision]", result)
        self.assertIn("Approved", result)
    
    def test_labeler_formats_system_validation(self):
        """Verify system validation messages are labeled."""
        labeler = OutputLabeler(use_color=False)
        result = labeler.system_validation("Check passed")
        self.assertIn("[System Validation]", result)
        self.assertIn("Check passed", result)
    
    def test_all_output_functions_produce_labeled_output(self):
        """Verify all print functions produce labeled output."""
        # Capture stdout
        import io
        
        functions = [
            (print_ai_advisory, "[AI Advisory]"),
            (print_ai_generated, "[AI Generated]"),
            (print_human_decision, "[Human Decision]"),
            (print_system_validation, "[System Validation]"),
        ]
        
        for func, expected_label in functions:
            with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                func("test")
                output = mock_stdout.getvalue()
                self.assertIn(expected_label, output)


# =============================================================================
# Workflow State Tests
# =============================================================================


class TestWorkflowState(unittest.TestCase):
    """Tests for workflow state management."""
    
    def test_uninitialized_state(self):
        """Verify uninitialized state is created correctly."""
        state = WorkflowState.uninitialized("/tmp/test")
        self.assertEqual(state.phase, WorkflowPhase.UNINITIALIZED)
        self.assertFalse(state.is_initialized())
    
    def test_state_is_immutable(self):
        """Verify WorkflowState is immutable."""
        state = WorkflowState.uninitialized("/tmp/test")
        with self.assertRaises(AttributeError):
            state.phase = WorkflowPhase.INITIALIZED
    
    def test_state_transitions(self):
        """Verify state transitions work correctly."""
        state = WorkflowState.uninitialized("/tmp/test")
        
        # Transition to initialized
        state = state.with_phase(WorkflowPhase.INITIALIZED)
        self.assertTrue(state.is_initialized())
        
        # Add plan
        state = state.with_plan("plan-123", "test intent")
        self.assertTrue(state.is_planned())
        self.assertEqual(state.current_plan_id, "plan-123")
        
        # Add approval
        state = state.with_approval("sig-456")
        self.assertTrue(state.is_approved())
        self.assertEqual(state.approval_signature, "sig-456")
    
    def test_state_history_tracking(self):
        """Verify state transitions are tracked in history."""
        state = WorkflowState.uninitialized("/tmp/test")
        state = state.with_phase(WorkflowPhase.INITIALIZED)
        state = state.with_plan("plan-123", "test")
        
        self.assertEqual(len(state.history), 2)
    
    def test_state_serialization(self):
        """Verify state can be serialized and deserialized."""
        state = WorkflowState(
            phase=WorkflowPhase.PLANNED,
            project_root="/tmp/test",
            current_plan_id="plan-123",
            current_intent="test intent",
        )
        
        data = state.to_dict()
        restored = WorkflowState.from_dict(data)
        
        self.assertEqual(restored.phase, state.phase)
        self.assertEqual(restored.current_plan_id, state.current_plan_id)
    
    def test_state_persistence(self):
        """Verify state is saved and loaded from disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create .axiom directory
            axiom_dir = Path(tmpdir) / ".axiom"
            axiom_dir.mkdir()
            
            # Save state
            state = WorkflowState(
                phase=WorkflowPhase.INITIALIZED,
                project_root=tmpdir,
            )
            save_workflow_state(state)
            
            # Load state
            loaded = load_workflow_state(tmpdir)
            self.assertEqual(loaded.phase, WorkflowPhase.INITIALIZED)


# =============================================================================
# Precondition Tests
# =============================================================================


class TestPreconditions(unittest.TestCase):
    """Tests for workflow precondition checking."""
    
    def test_check_initialized_fails_when_not_initialized(self):
        """Verify check fails when project is not initialized."""
        with tempfile.TemporaryDirectory() as tmpdir:
            checker = PreconditionChecker(tmpdir)
            error = checker.check_initialized()
            
            self.assertIsNotNone(error)
            self.assertIn("not initialized", error.message)
    
    def test_check_initialized_passes_when_initialized(self):
        """Verify check passes when project is initialized."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create .axiom directory
            axiom_dir = Path(tmpdir) / ".axiom"
            axiom_dir.mkdir()
            
            # Save initialized state
            state = WorkflowState(
                phase=WorkflowPhase.INITIALIZED,
                project_root=tmpdir,
            )
            save_workflow_state(state)
            
            checker = PreconditionChecker(tmpdir)
            error = checker.check_initialized()
            
            self.assertIsNone(error)
    
    def test_check_not_initialized_fails_when_initialized(self):
        """Verify check fails when project is already initialized."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create .axiom directory
            axiom_dir = Path(tmpdir) / ".axiom"
            axiom_dir.mkdir()
            
            # Save initialized state
            state = WorkflowState(
                phase=WorkflowPhase.INITIALIZED,
                project_root=tmpdir,
            )
            save_workflow_state(state)
            
            checker = PreconditionChecker(tmpdir)
            error = checker.check_not_initialized()
            
            self.assertIsNotNone(error)
            self.assertIn("already initialized", error.message)
    
    def test_check_planned_fails_before_planning(self):
        """Verify planning check fails before a plan exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create initialized state
            axiom_dir = Path(tmpdir) / ".axiom"
            axiom_dir.mkdir()
            state = WorkflowState(
                phase=WorkflowPhase.INITIALIZED,
                project_root=tmpdir,
            )
            save_workflow_state(state)
            
            checker = PreconditionChecker(tmpdir)
            error = checker.check_planned()
            
            self.assertIsNotNone(error)
            self.assertIn("No plan", error.message)
    
    def test_check_approved_fails_before_approval(self):
        """Verify approval check fails before human approval."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create planned state
            axiom_dir = Path(tmpdir) / ".axiom"
            axiom_dir.mkdir()
            state = WorkflowState(
                phase=WorkflowPhase.PREVIEWED,
                project_root=tmpdir,
                current_plan_id="plan-123",
                current_intent="test",
            )
            save_workflow_state(state)
            
            checker = PreconditionChecker(tmpdir)
            error = checker.check_approved()
            
            self.assertIsNotNone(error)
            self.assertIn("not been approved", error.message)
    
    def test_error_suggests_correct_command(self):
        """Verify precondition errors suggest the correct next command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            checker = PreconditionChecker(tmpdir)
            error = checker.check_initialized()
            
            self.assertIn("axiom init", error.suggested_command)
    
    def test_allowed_commands_by_phase(self):
        """Verify correct commands are allowed in each phase."""
        with tempfile.TemporaryDirectory() as tmpdir:
            checker = PreconditionChecker(tmpdir)
            
            # Uninitialized - should allow init/adopt
            allowed = checker.get_allowed_commands()
            self.assertIn("init", allowed)
            self.assertIn("adopt", allowed)
            self.assertIn("status", allowed)  # Always allowed
            self.assertNotIn("execute", allowed)


# =============================================================================
# CLI Command Tests
# =============================================================================


class TestCLICommands(unittest.TestCase):
    """Tests for CLI command behavior."""
    
    def test_cli_help_shows_version(self):
        """Verify CLI help includes version."""
        with self.assertRaises(SystemExit):
            cli(["--version"])
    
    def test_cli_no_args_shows_help(self):
        """Verify CLI with no args shows help."""
        result = cli([])
        self.assertEqual(result, 0)
    
    def test_status_command_works_without_init(self):
        """Verify status command works even without initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = cli(["--path", tmpdir, "status"])
            self.assertEqual(result, 0)
    
    def test_execute_requires_approval(self):
        """Verify execute fails without approval."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create previewed state (not approved)
            axiom_dir = Path(tmpdir) / ".axiom"
            axiom_dir.mkdir()
            state = WorkflowState(
                phase=WorkflowPhase.PREVIEWED,
                project_root=tmpdir,
                current_plan_id="plan-123",
                current_intent="test",
            )
            save_workflow_state(state)
            
            result = cli(["--path", tmpdir, "execute"])
            self.assertNotEqual(result, 0)  # Should fail
    
    def test_preview_requires_plan(self):
        """Verify preview fails without a plan."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create initialized state (no plan)
            axiom_dir = Path(tmpdir) / ".axiom"
            axiom_dir.mkdir()
            state = WorkflowState(
                phase=WorkflowPhase.INITIALIZED,
                project_root=tmpdir,
            )
            save_workflow_state(state)
            
            result = cli(["--path", tmpdir, "preview"])
            self.assertNotEqual(result, 0)  # Should fail
    
    def test_approve_requires_rationale(self):
        """Verify approve fails without rationale."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create planned state
            axiom_dir = Path(tmpdir) / ".axiom"
            axiom_dir.mkdir()
            state = WorkflowState(
                phase=WorkflowPhase.PLANNED,
                project_root=tmpdir,
                current_plan_id="plan-123",
                current_intent="test",
            )
            save_workflow_state(state)
            
            # No --rationale provided
            result = cli(["--path", tmpdir, "approve"])
            self.assertNotEqual(result, 0)  # Should fail
    
    def test_approve_requires_confirmation(self):
        """Verify approve fails without --yes flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create planned state
            axiom_dir = Path(tmpdir) / ".axiom"
            axiom_dir.mkdir()
            state = WorkflowState(
                phase=WorkflowPhase.PLANNED,
                project_root=tmpdir,
                current_plan_id="plan-123",
                current_intent="test",
            )
            save_workflow_state(state)
            
            # Rationale provided but no --yes
            result = cli(["--path", tmpdir, "approve", "--rationale", "test"])
            self.assertNotEqual(result, 0)  # Should fail


# =============================================================================
# IDE Surface Tests
# =============================================================================


class TestIDESurface(unittest.TestCase):
    """Tests for IDE command surface."""
    
    def test_all_commands_have_cli_mapping(self):
        """Verify all IDE commands map to CLI commands."""
        for cmd in IDE_COMMANDS:
            self.assertTrue(cmd.cli_command.startswith("axiom"))
    
    def test_commands_have_unique_ids(self):
        """Verify all command IDs are unique."""
        ids = [cmd.id for cmd in IDE_COMMANDS]
        self.assertEqual(len(ids), len(set(ids)))
    
    def test_get_command_returns_correct_command(self):
        """Verify get_command retrieves correct command."""
        cmd = get_command("axiom.init")
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.id, "axiom.init")
    
    def test_vscode_commands_generated_correctly(self):
        """Verify VS Code commands are generated correctly."""
        commands = generate_vscode_commands()
        self.assertIn("commands", commands)
        self.assertGreater(len(commands["commands"]), 0)
    
    def test_command_mapping_is_complete(self):
        """Verify command mapping covers all commands."""
        mapping = generate_command_mapping()
        for cmd in IDE_COMMANDS:
            self.assertIn(cmd.id, mapping)


# =============================================================================
# Copilot Template Tests
# =============================================================================


class TestCopilotTemplates(unittest.TestCase):
    """Tests for Copilot interaction templates."""
    
    def test_all_templates_have_warnings(self):
        """Verify all templates include warnings about AI limitations."""
        for template_id, template in TEMPLATES.items():
            self.assertGreater(len(template.warnings), 0)
    
    def test_templates_include_ai_labels(self):
        """Verify templates mention AI labeling."""
        instructions = get_copilot_instructions()
        self.assertIn("[AI Advisory]", instructions)
        self.assertIn("[AI Generated]", instructions)
    
    def test_copilot_instructions_forbid_execution(self):
        """Verify Copilot instructions forbid autonomous execution."""
        instructions = get_copilot_instructions()
        self.assertIn("NEVER execute", instructions)
        self.assertIn("NEVER approve", instructions)
    
    def test_template_rendering(self):
        """Verify templates can be rendered with values."""
        template = get_template("intent_draft")
        self.assertIsNotNone(template)
        
        result = template.render(goal="add authentication")
        self.assertIn("add authentication", result["user"])
    
    def test_advisory_response_formatting(self):
        """Verify advisory responses are labeled."""
        response = format_advisory_response("This is advice")
        self.assertIn("[AI Advisory]", response)


# =============================================================================
# Security Invariant Tests
# =============================================================================


class TestCLISecurityInvariants(unittest.TestCase):
    """Tests for CLI security invariants."""
    
    def test_cli_cannot_auto_approve(self):
        """Verify CLI has no auto-approve mechanism."""
        # Check that approve command requires explicit flags
        with tempfile.TemporaryDirectory() as tmpdir:
            axiom_dir = Path(tmpdir) / ".axiom"
            axiom_dir.mkdir()
            state = WorkflowState(
                phase=WorkflowPhase.PLANNED,
                project_root=tmpdir,
                current_plan_id="plan-123",
                current_intent="test",
            )
            save_workflow_state(state)
            
            # Try to approve without any flags
            result = cli(["--path", tmpdir, "approve"])
            self.assertNotEqual(result, 0)
    
    def test_cli_cannot_skip_approval(self):
        """Verify CLI cannot skip approval step."""
        with tempfile.TemporaryDirectory() as tmpdir:
            axiom_dir = Path(tmpdir) / ".axiom"
            axiom_dir.mkdir()
            
            # Create state with plan but no approval
            state = WorkflowState(
                phase=WorkflowPhase.PREVIEWED,
                project_root=tmpdir,
                current_plan_id="plan-123",
                current_intent="test",
            )
            save_workflow_state(state)
            
            # Try to execute without approval
            result = cli(["--path", tmpdir, "execute"])
            self.assertNotEqual(result, 0)
    
    def test_workflow_order_enforced(self):
        """Verify workflow steps must be done in order."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Try to plan without init
            result = cli(["--path", tmpdir, "plan", "test"])
            self.assertNotEqual(result, 0)
    
    def test_cli_does_not_store_persistent_state(self):
        """Verify CLI itself does not maintain state."""
        # The CLI module should not have any module-level mutable state
        import axiom_cli.main as main_module
        
        # Check that there are no module-level mutable containers
        # that could store state across invocations
        for name in dir(main_module):
            obj = getattr(main_module, name)
            if isinstance(obj, (dict, list, set)) and not name.startswith('_'):
                if name not in ['sys', 'os']:  # Ignore standard library
                    self.fail(f"Module has mutable state: {name}")


# =============================================================================
# Integration Tests
# =============================================================================


class TestCLIIntegration(unittest.TestCase):
    """Integration tests for CLI workflow."""
    
    def test_workflow_state_transitions(self):
        """Test workflow state transitions directly (without calling real workflows)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup .axiom directory
            axiom_dir = Path(tmpdir) / ".axiom"
            axiom_dir.mkdir()
            
            # 1. Status before init - should work
            result = cli(["--path", tmpdir, "status"])
            self.assertEqual(result, 0)
            
            # 2. Manually set initialized state (simulating cmd_init success)
            state = WorkflowState(
                phase=WorkflowPhase.INITIALIZED,
                project_root=tmpdir,
            )
            save_workflow_state(state)
            
            # Verify state
            state = load_workflow_state(tmpdir)
            self.assertEqual(state.phase, WorkflowPhase.INITIALIZED)
            
            # 3. Manually set planned state (simulating cmd_plan success)
            state = state.with_plan("plan-123", "test intent")
            save_workflow_state(state)
            
            # Verify state
            state = load_workflow_state(tmpdir)
            self.assertEqual(state.phase, WorkflowPhase.PLANNED)
            self.assertEqual(state.current_intent, "test intent")
            
            # 4. Manually set previewed state (simulating cmd_preview success)
            state = state.with_phase(WorkflowPhase.PREVIEWED)
            save_workflow_state(state)
            
            # Verify state  
            state = load_workflow_state(tmpdir)
            self.assertEqual(state.phase, WorkflowPhase.PREVIEWED)
            
            # 5. Approve (with required flags) - this should work
            result = cli([
                "--path", tmpdir,
                "approve",
                "--rationale", "Reviewed and approved",
                "--yes"
            ])
            self.assertEqual(result, 0)
            
            # Verify state
            state = load_workflow_state(tmpdir)
            self.assertEqual(state.phase, WorkflowPhase.APPROVED)
            self.assertIsNotNone(state.approval_signature)
    
    def test_workflow_order_enforcement_prevents_skipping(self):
        """Test that workflow order is enforced and steps cannot be skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            axiom_dir = Path(tmpdir) / ".axiom"
            axiom_dir.mkdir()
            
            # Set initialized state
            state = WorkflowState(
                phase=WorkflowPhase.INITIALIZED,
                project_root=tmpdir,
            )
            save_workflow_state(state)
            
            # Cannot approve without plan
            result = cli([
                "--path", tmpdir,
                "approve",
                "--rationale", "test",
                "--yes"
            ])
            self.assertNotEqual(result, 0)
            
            # Cannot execute without approval
            result = cli(["--path", tmpdir, "execute"])
            self.assertNotEqual(result, 0)
    
    def test_approval_signature_is_recorded(self):
        """Test that approval signature is properly recorded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            axiom_dir = Path(tmpdir) / ".axiom"
            axiom_dir.mkdir()
            
            # Setup state for approval
            state = WorkflowState(
                phase=WorkflowPhase.PREVIEWED,
                project_root=tmpdir,
                current_plan_id="plan-123",
                current_intent="test intent",
            )
            save_workflow_state(state)
            
            # Approve
            result = cli([
                "--path", tmpdir,
                "approve",
                "--rationale", "I have reviewed and approve this plan",
                "--yes"
            ])
            self.assertEqual(result, 0)
            
            # Check signature was recorded
            state = load_workflow_state(tmpdir)
            self.assertEqual(state.phase, WorkflowPhase.APPROVED)
            self.assertIsNotNone(state.approval_signature)
            # Signature is a hash of plan_id, rationale, timestamp
            self.assertGreater(len(state.approval_signature), 0)
            # Verify the signature is a hex string
            self.assertTrue(all(c in '0123456789abcdef' for c in state.approval_signature))


if __name__ == "__main__":
    unittest.main()
