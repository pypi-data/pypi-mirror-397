"""
Tests for Rich Output Module.

These tests verify the rich CLI output formatting while ensuring
no governance constraints are weakened.
"""

import pytest
from axiom_cli.rich_output import (
    StatusIndicator,
    RichOutputFormatter,
    WorkflowStatusView,
    WorkflowStatusFormatter,
    get_rich_formatter,
    get_status_formatter,
    STATUS_SYMBOLS,
    PLAIN_STATUS_SYMBOLS,
)


class TestStatusIndicator:
    """Tests for StatusIndicator enum."""
    
    def test_all_status_indicators_have_symbols(self):
        """Every status indicator must have a unicode symbol."""
        for status in StatusIndicator:
            assert status in STATUS_SYMBOLS, f"Missing symbol for {status}"
    
    def test_all_status_indicators_have_plain_symbols(self):
        """Every status indicator must have a plain text symbol."""
        for status in StatusIndicator:
            assert status in PLAIN_STATUS_SYMBOLS, f"Missing plain symbol for {status}"
    
    def test_blocked_status_exists(self):
        """BLOCKED status must exist for governance visibility."""
        assert StatusIndicator.BLOCKED in StatusIndicator
    
    def test_human_action_required_status_exists(self):
        """HUMAN ACTION REQUIRED status must exist for governance visibility."""
        assert StatusIndicator.HUMAN_ACTION_REQUIRED in StatusIndicator


class TestRichOutputFormatter:
    """Tests for RichOutputFormatter class."""
    
    def test_formatter_initialization_defaults(self):
        """Formatter should initialize with sensible defaults."""
        fmt = RichOutputFormatter()
        # Should not raise
        assert fmt is not None
    
    def test_formatter_with_color_disabled(self):
        """Formatter should work with color disabled."""
        fmt = RichOutputFormatter(use_color=False)
        assert fmt.use_color is False
    
    def test_formatter_with_unicode_disabled(self):
        """Formatter should work with unicode disabled."""
        fmt = RichOutputFormatter(use_unicode=False)
        assert fmt.use_unicode is False
    
    def test_format_status_includes_label(self):
        """Status output must include text label, not just symbols."""
        fmt = RichOutputFormatter(use_color=False, use_unicode=False)
        output = fmt.format_status(StatusIndicator.BLOCKED, "test message")
        
        # Must include the text label
        assert "[BLOCKED]" in output
        assert "test message" in output
    
    def test_format_blocked_is_visually_distinct(self):
        """Blocked status must be clearly marked."""
        fmt = RichOutputFormatter(use_color=False, use_unicode=False)
        output = fmt.format_blocked("Approval required")
        
        assert "BLOCKED" in output
        assert "Approval required" in output
    
    def test_format_human_action_required_is_explicit(self):
        """Human action required must be explicit in output."""
        fmt = RichOutputFormatter(use_color=False, use_unicode=False)
        output = fmt.format_human_action_required("Approval needed")
        
        assert "HUMAN ACTION REQUIRED" in output
        assert "Approval needed" in output
    
    def test_plain_text_fallback_works(self):
        """All formatting must work in plain text mode."""
        fmt = RichOutputFormatter(use_color=False, use_unicode=False)
        
        # Test various format methods
        assert fmt.format_status(StatusIndicator.SUCCESS, "done") != ""
        assert fmt.format_header("Title") != ""
        assert fmt.format_bullet_list(["a", "b"]) != ""
        assert fmt.format_table(["Col"], [["Val"]]) != ""
        assert fmt.format_timeline([(
            "Step",
            StatusIndicator.SUCCESS,
            None,
        )]) != ""
    
    def test_header_formatting(self):
        """Headers should be properly formatted."""
        fmt = RichOutputFormatter(use_color=False, use_unicode=False)
        output = fmt.format_header("TEST HEADER")
        
        assert "TEST HEADER" in output
        # Should have some kind of border/decoration
        assert "=" in output or "-" in output
    
    def test_table_formatting(self):
        """Tables should be properly formatted."""
        fmt = RichOutputFormatter(use_color=False, use_unicode=False)
        output = fmt.format_table(
            ["Name", "Status"],
            [
                ["Plan", "Ready"],
                ["Approval", "Pending"],
            ]
        )
        
        assert "Name" in output
        assert "Status" in output
        assert "Plan" in output
        assert "Ready" in output
    
    def test_timeline_formatting(self):
        """Timeline should be properly formatted."""
        fmt = RichOutputFormatter(use_color=False, use_unicode=False)
        steps = [
            ("Step 1", StatusIndicator.SUCCESS, "2024-01-01"),
            ("Step 2", StatusIndicator.IN_PROGRESS, None),
            ("Step 3", StatusIndicator.NOT_STARTED, None),
        ]
        output = fmt.format_timeline(steps)
        
        assert "Step 1" in output
        assert "Step 2" in output
        assert "Step 3" in output
    
    def test_progress_bar_formatting(self):
        """Progress bar should show percentage."""
        fmt = RichOutputFormatter(use_color=False, use_unicode=False)
        output = fmt.format_progress_bar(50, 100)
        
        assert "50%" in output
    
    def test_box_formatting(self):
        """Box should contain content."""
        fmt = RichOutputFormatter(use_color=False, use_unicode=False)
        output = fmt.format_box("Test content", title="Test Box")
        
        assert "Test content" in output
        assert "Test Box" in output
    
    def test_indentation_works(self):
        """Indentation should affect output."""
        fmt = RichOutputFormatter(use_color=False, use_unicode=False)
        
        output1 = fmt.format_status(StatusIndicator.SUCCESS, "test")
        fmt.indent()
        output2 = fmt.format_status(StatusIndicator.SUCCESS, "test")
        fmt.dedent()
        
        # Indented output should be longer due to spaces
        assert len(output2) > len(output1)
    
    # =========================================================================
    # AI/Human/System Label Preservation Tests
    # =========================================================================
    
    def test_ai_advisory_label_preserved(self):
        """AI Advisory label must be preserved in output."""
        fmt = RichOutputFormatter(use_color=False)
        output = fmt.format_ai_advisory("This is AI advice")
        
        assert "AI Advisory" in output
        assert "This is AI advice" in output
    
    def test_ai_generated_label_preserved(self):
        """AI Generated label must be preserved in output."""
        fmt = RichOutputFormatter(use_color=False)
        output = fmt.format_ai_generated("Generated content")
        
        assert "AI Generated" in output
        assert "Generated content" in output
    
    def test_human_decision_label_preserved(self):
        """Human Decision label must be preserved in output."""
        fmt = RichOutputFormatter(use_color=False)
        output = fmt.format_human_decision("User approved")
        
        assert "Human Decision" in output
        assert "User approved" in output
    
    def test_system_validation_label_preserved(self):
        """System Validation label must be preserved in output."""
        fmt = RichOutputFormatter(use_color=False)
        output = fmt.format_system_validation("All checks passed")
        
        assert "System Validation" in output
        assert "All checks passed" in output


class TestWorkflowStatusView:
    """Tests for WorkflowStatusView dataclass."""
    
    def test_status_view_creation(self):
        """Status view should be creatable with minimal args."""
        view = WorkflowStatusView(
            phase="initialized",
            project_root="/test/path",
        )
        
        assert view.phase == "initialized"
        assert view.project_root == "/test/path"
        assert view.is_blocked is False
    
    def test_status_view_with_blocking(self):
        """Status view should track blocking state."""
        view = WorkflowStatusView(
            phase="previewed",
            project_root="/test/path",
            is_blocked=True,
            blocking_reasons=["Approval required"],
        )
        
        assert view.is_blocked is True
        assert "Approval required" in view.blocking_reasons


class TestWorkflowStatusFormatter:
    """Tests for WorkflowStatusFormatter class."""
    
    def test_formatter_initialization(self):
        """Formatter should initialize properly."""
        fmt = WorkflowStatusFormatter()
        assert fmt is not None
    
    def test_build_status_view(self):
        """Should build status view from state parameters."""
        fmt = WorkflowStatusFormatter()
        view = fmt.build_status_view(
            phase="initialized",
            project_root="/test",
            allowed_commands=["plan", "status"],
        )
        
        assert view.phase == "initialized"
        assert "plan" in view.next_actions
    
    def test_status_view_includes_blocking_for_uninitialized(self):
        """Uninitialized projects should show blocking."""
        fmt = WorkflowStatusFormatter()
        view = fmt.build_status_view(
            phase="uninitialized",
            project_root="/test",
        )
        
        assert view.is_blocked is True
        assert len(view.blocking_reasons) > 0
    
    def test_status_view_includes_blocking_for_previewed(self):
        """Previewed (pre-approval) should show human action required."""
        fmt = WorkflowStatusFormatter()
        view = fmt.build_status_view(
            phase="previewed",
            project_root="/test",
        )
        
        assert view.is_blocked is True
        # Should mention approval
        assert any("approv" in r.lower() for r in view.blocking_reasons)
    
    def test_format_full_status_includes_all_sections(self):
        """Full status output should include all required sections."""
        fmt = WorkflowStatusFormatter(
            RichOutputFormatter(use_color=False, use_unicode=False)
        )
        view = WorkflowStatusView(
            phase="planned",
            project_root="/test",
            plan_id="plan_123",
            intent="test intent",
            is_blocked=True,
            blocking_reasons=["Preview required"],
            timeline=[
                ("Init", StatusIndicator.SUCCESS, None),
                ("Plan", StatusIndicator.SUCCESS, None),
                ("Preview", StatusIndicator.NOT_STARTED, None),
            ],
            next_actions=["preview", "status"],
        )
        
        output = fmt.format_full_status(view)
        
        # Check all required sections
        assert "Project Information" in output or "Project Root" in output
        assert "plan_123" in output or "Plan" in output
        assert "Timeline" in output
        assert "Blocking" in output or "BLOCKED" in output
        assert "Next" in output or "Actions" in output


class TestGlobalFormatters:
    """Tests for global formatter instances."""
    
    def test_get_rich_formatter_returns_formatter(self):
        """get_rich_formatter should return a RichOutputFormatter."""
        fmt = get_rich_formatter()
        assert isinstance(fmt, RichOutputFormatter)
    
    def test_get_status_formatter_returns_formatter(self):
        """get_status_formatter should return a WorkflowStatusFormatter."""
        fmt = get_status_formatter()
        assert isinstance(fmt, WorkflowStatusFormatter)


class TestGovernancePreservation:
    """
    Tests ensuring rich output does not weaken governance.
    
    These tests verify that:
    1. Output makes blocking states clearly visible
    2. Human action requirements are explicit
    3. AI vs Human labels are preserved
    4. No output implies automatic approval
    """
    
    def test_blocked_state_is_explicit(self):
        """Blocked states must be explicitly labeled."""
        fmt = RichOutputFormatter(use_color=False, use_unicode=False)
        output = fmt.format_blocked("Cannot proceed")
        
        # The word "BLOCKED" must appear
        assert "BLOCKED" in output.upper()
    
    def test_human_action_required_is_explicit(self):
        """Human action requirements must be explicit."""
        fmt = RichOutputFormatter(use_color=False, use_unicode=False)
        output = fmt.format_human_action_required("Approval needed")
        
        # Must mention human action
        assert "HUMAN" in output.upper()
        assert "REQUIRED" in output.upper() or "ACTION" in output.upper()
    
    def test_no_auto_approval_suggestion(self):
        """Output must never suggest automatic approval."""
        fmt = WorkflowStatusFormatter(
            RichOutputFormatter(use_color=False, use_unicode=False)
        )
        view = WorkflowStatusView(
            phase="previewed",
            project_root="/test",
            next_actions=["approve"],
        )
        
        output = fmt.format_full_status(view)
        
        # Should not suggest auto-approval
        assert "auto" not in output.lower() or "automatic" not in output.lower()
        
        # AI advisory should be clear that suggestions are just suggestions
        assert "suggest" in output.lower() or "you decide" in output.lower()
    
    def test_timeline_shows_approval_step(self):
        """Timeline must include approval as a distinct step."""
        fmt = WorkflowStatusFormatter(
            RichOutputFormatter(use_color=False, use_unicode=False)
        )
        view = fmt.build_status_view(
            phase="executed",
            project_root="/test",
        )
        
        # Check timeline includes approval
        step_names = [step[0].lower() for step in view.timeline]
        assert any("approv" in name for name in step_names)
    
    def test_success_output_does_not_imply_completion(self):
        """Success formatting should not imply approval is automatic."""
        fmt = RichOutputFormatter(use_color=False, use_unicode=False)
        output = fmt.format_success("Plan validated")
        
        # Should not mention "approved" or "executing"
        assert "approved" not in output.lower()
        assert "executing" not in output.lower()
