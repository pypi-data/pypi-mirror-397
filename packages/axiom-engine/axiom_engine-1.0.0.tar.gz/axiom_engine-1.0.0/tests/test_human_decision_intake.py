"""
Tests for Human Decision Intake API.

These tests verify that:
1. Approval grammar is strictly enforced
2. Invalid/informal approvals are rejected
3. Nonce replay protection works
4. Plan binding prevents stale approvals
5. Two-step approval → execute is enforced
6. CLI and Copilot paths behave identically
7. AI output remains labeled
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from axiom_core.human_decision_intake import (
    ApprovalGrammarAction,
    DecisionStatus,
    GrammarViolation,
    GrammarViolationType,
    HumanDecisionIntake,
    HumanDecisionResult,
    NonceRegistry,
    ParsedApproval,
    PlanBinding,
    parse_approval_grammar,
)


# =============================================================================
# Grammar Parsing Tests
# =============================================================================


class TestApprovalGrammarParsing:
    """Tests for strict approval grammar parsing."""
    
    def test_valid_approve_with_rationale(self):
        """Valid APPROVE: with rationale is accepted."""
        parsed, violation = parse_approval_grammar("APPROVE: I reviewed the plan and it looks correct")
        
        assert violation is None
        assert parsed is not None
        assert parsed.action == ApprovalGrammarAction.APPROVE
        assert "reviewed" in parsed.rationale
    
    def test_valid_reject_with_rationale(self):
        """Valid REJECT: with rationale is accepted."""
        parsed, violation = parse_approval_grammar("REJECT: This plan modifies production database")
        
        assert violation is None
        assert parsed is not None
        assert parsed.action == ApprovalGrammarAction.REJECT
        assert "production" in parsed.rationale
    
    def test_valid_override_with_rationale(self):
        """Valid OVERRIDE: with rationale is accepted."""
        parsed, violation = parse_approval_grammar("OVERRIDE: AI is too conservative, I accept the risk")
        
        assert violation is None
        assert parsed is not None
        assert parsed.action == ApprovalGrammarAction.OVERRIDE
        assert "risk" in parsed.rationale
    
    def test_valid_execute_no_rationale(self):
        """Valid EXECUTE (no rationale) is accepted."""
        parsed, violation = parse_approval_grammar("EXECUTE")
        
        assert violation is None
        assert parsed is not None
        assert parsed.action == ApprovalGrammarAction.EXECUTE
        assert parsed.rationale is None
    
    def test_multiline_rationale_accepted(self):
        """Multi-line rationale is accepted."""
        text = """APPROVE: I reviewed this plan carefully.
        
It makes the following changes:
- Adds new API endpoint
- Updates database schema

I accept these changes."""
        
        parsed, violation = parse_approval_grammar(text)
        
        assert violation is None
        assert parsed is not None
        assert parsed.action == ApprovalGrammarAction.APPROVE
        assert "API endpoint" in parsed.rationale


class TestInvalidApprovals:
    """Tests for rejection of invalid approvals."""
    
    @pytest.mark.parametrize("invalid_text", [
        "yes",
        "Yes",
        "YES",
        "ok",
        "OK",
        "okay",
        "sure",
        "looks good",
        "Looks good",
        "LOOKS GOOD",
        "lgtm",
        "LGTM",
        "approved",
        "Approved",
        "go ahead",
        "proceed",
        "do it",
        "y",
        "👍",
        "✅",
    ])
    def test_informal_approvals_rejected(self, invalid_text):
        """Informal approvals like 'yes', 'ok', 'lgtm' are rejected."""
        parsed, violation = parse_approval_grammar(invalid_text)
        
        assert parsed is None
        assert violation is not None
        assert violation.type == GrammarViolationType.INFORMAL_APPROVAL
    
    def test_lowercase_approve_rejected(self):
        """Lowercase 'approve:' is rejected (must be UPPERCASE)."""
        parsed, violation = parse_approval_grammar("approve: this looks fine")
        
        assert parsed is None
        assert violation is not None
        assert violation.type == GrammarViolationType.INVALID_PREFIX
    
    def test_lowercase_reject_rejected(self):
        """Lowercase 'reject:' is rejected."""
        parsed, violation = parse_approval_grammar("reject: bad idea")
        
        assert parsed is None
        assert violation is not None
        assert violation.type == GrammarViolationType.INVALID_PREFIX
    
    def test_lowercase_execute_rejected(self):
        """Lowercase 'execute' is rejected."""
        parsed, violation = parse_approval_grammar("execute")
        
        assert parsed is None
        assert violation is not None
        assert violation.type == GrammarViolationType.INVALID_PREFIX
    
    def test_approve_without_colon_rejected(self):
        """APPROVE without colon is rejected."""
        parsed, violation = parse_approval_grammar("APPROVE this looks fine")
        
        assert parsed is None
        assert violation is not None
    
    def test_approve_empty_rationale_rejected(self):
        """APPROVE: with empty rationale is rejected."""
        parsed, violation = parse_approval_grammar("APPROVE:   ")
        
        assert parsed is None
        assert violation is not None
        assert violation.type == GrammarViolationType.EMPTY_RATIONALE
    
    def test_reject_empty_rationale_rejected(self):
        """REJECT: with empty rationale is rejected."""
        parsed, violation = parse_approval_grammar("REJECT:")
        
        assert parsed is None
        assert violation is not None
        assert violation.type == GrammarViolationType.EMPTY_RATIONALE
    
    def test_override_empty_rationale_rejected(self):
        """OVERRIDE: with empty rationale is rejected."""
        parsed, violation = parse_approval_grammar("OVERRIDE: ")
        
        assert parsed is None
        assert violation is not None
        assert violation.type == GrammarViolationType.EMPTY_RATIONALE
    
    def test_execute_with_rationale_rejected(self):
        """EXECUTE: with rationale is rejected (EXECUTE takes no rationale)."""
        parsed, violation = parse_approval_grammar("EXECUTE: go ahead")
        
        assert parsed is None
        assert violation is not None
        assert violation.type == GrammarViolationType.EXECUTE_WITH_RATIONALE
    
    def test_empty_input_rejected(self):
        """Empty input is rejected."""
        parsed, violation = parse_approval_grammar("")
        
        assert parsed is None
        assert violation is not None
        assert violation.type == GrammarViolationType.EMPTY_INPUT
    
    def test_whitespace_only_rejected(self):
        """Whitespace-only input is rejected."""
        parsed, violation = parse_approval_grammar("   \n\t  ")
        
        assert parsed is None
        assert violation is not None
        assert violation.type == GrammarViolationType.EMPTY_INPUT
    
    def test_random_text_rejected(self):
        """Random text without valid prefix is rejected."""
        parsed, violation = parse_approval_grammar("I think this plan is good, go ahead")
        
        assert parsed is None
        assert violation is not None
        assert violation.type == GrammarViolationType.UNKNOWN_FORMAT


# =============================================================================
# Nonce Registry Tests
# =============================================================================


class TestNonceRegistry:
    """Tests for nonce replay protection."""
    
    def test_nonce_generation_unique(self):
        """Generated nonces are unique."""
        registry = NonceRegistry()
        nonces = {registry.generate_nonce() for _ in range(100)}
        
        assert len(nonces) == 100  # All unique
    
    def test_nonce_registration_prevents_replay(self):
        """Registered nonce cannot be reused."""
        registry = NonceRegistry()
        nonce = registry.generate_nonce()
        
        # First registration succeeds
        assert registry.register_nonce(nonce) is True
        
        # Second registration fails (replay attempt)
        assert registry.register_nonce(nonce) is False
    
    def test_is_used_reports_correctly(self):
        """is_used() correctly reports nonce status."""
        registry = NonceRegistry()
        nonce = registry.generate_nonce()
        
        assert registry.is_used(nonce) is False
        registry.register_nonce(nonce)
        assert registry.is_used(nonce) is True


# =============================================================================
# Plan Binding Tests
# =============================================================================


class TestPlanBinding:
    """Tests for plan-approval binding."""
    
    def test_binding_valid_for_same_plan(self):
        """Binding is valid for same plan and hash."""
        binding = PlanBinding(
            plan_id="plan-123",
            plan_hash="abc123",
            approval_nonce="nonce-456",
            decision_id="decision-789",
        )
        
        assert binding.is_valid_for_plan("plan-123", "abc123") is True
    
    def test_binding_invalid_for_different_plan(self):
        """Binding is invalid for different plan ID."""
        binding = PlanBinding(
            plan_id="plan-123",
            plan_hash="abc123",
            approval_nonce="nonce-456",
            decision_id="decision-789",
        )
        
        assert binding.is_valid_for_plan("plan-different", "abc123") is False
    
    def test_binding_invalid_for_changed_plan(self):
        """Binding is invalid if plan hash changed."""
        binding = PlanBinding(
            plan_id="plan-123",
            plan_hash="abc123",
            approval_nonce="nonce-456",
            decision_id="decision-789",
        )
        
        # Same plan ID but different hash (plan was modified)
        assert binding.is_valid_for_plan("plan-123", "different-hash") is False


# =============================================================================
# Human Decision Intake Tests
# =============================================================================


class TestHumanDecisionIntake:
    """Tests for the main intake service."""
    
    def test_valid_approval_accepted(self):
        """Valid APPROVE: is accepted."""
        intake = HumanDecisionIntake()
        
        result = intake.record_human_decision(
            raw_text="APPROVE: I reviewed and approve this plan",
            source="copilot",
            plan_id="plan-123",
            plan_hash="hash-abc",
        )
        
        assert result.status == DecisionStatus.ACCEPTED
        assert result.decision_id is not None
        assert result.nonce is not None
        assert result.source == "copilot"
    
    def test_invalid_approval_rejected(self):
        """Invalid approval is rejected with proper violation."""
        intake = HumanDecisionIntake()
        
        result = intake.record_human_decision(
            raw_text="yes",
            source="copilot",
        )
        
        assert result.status == DecisionStatus.REJECTED
        assert result.violation is not None
        assert result.violation.type == GrammarViolationType.INFORMAL_APPROVAL
    
    def test_execute_requires_prior_approval(self):
        """EXECUTE fails without prior approval."""
        intake = HumanDecisionIntake()
        
        result = intake.record_human_decision(
            raw_text="EXECUTE",
            source="copilot",
            plan_id="plan-123",
            plan_hash="hash-abc",
        )
        
        assert result.status == DecisionStatus.REJECTED
        assert "approval" in result.message.lower()
    
    def test_execute_succeeds_after_approval(self):
        """EXECUTE succeeds after approval."""
        intake = HumanDecisionIntake()
        
        # First: approve
        approve_result = intake.record_human_decision(
            raw_text="APPROVE: I reviewed this plan",
            source="copilot",
            plan_id="plan-123",
            plan_hash="hash-abc",
        )
        assert approve_result.status == DecisionStatus.ACCEPTED
        
        # Then: execute
        execute_result = intake.record_human_decision(
            raw_text="EXECUTE",
            source="copilot",
            plan_id="plan-123",
            plan_hash="hash-abc",
        )
        assert execute_result.status == DecisionStatus.ACCEPTED
    
    def test_execute_fails_if_plan_changed(self):
        """EXECUTE fails if plan changed after approval."""
        intake = HumanDecisionIntake()
        
        # Approve with original hash
        intake.record_human_decision(
            raw_text="APPROVE: I reviewed this plan",
            source="copilot",
            plan_id="plan-123",
            plan_hash="hash-abc",
        )
        
        # Execute with different hash (plan was modified)
        result = intake.record_human_decision(
            raw_text="EXECUTE",
            source="copilot",
            plan_id="plan-123",
            plan_hash="hash-DIFFERENT",
        )
        
        assert result.status == DecisionStatus.REJECTED
        assert "changed" in result.message.lower()
    
    def test_source_tracking(self):
        """Source is tracked in result."""
        intake = HumanDecisionIntake()
        
        result = intake.record_human_decision(
            raw_text="APPROVE: test",
            source="cli",
        )
        
        assert result.source == "cli"
    
    def test_timestamp_recorded(self):
        """Timestamp is recorded in result."""
        intake = HumanDecisionIntake()
        
        result = intake.record_human_decision(
            raw_text="APPROVE: test",
            source="api",
        )
        
        assert result.timestamp is not None
        assert "T" in result.timestamp  # ISO format
    
    def test_invalidate_approval_clears_binding(self):
        """invalidate_approval() clears the binding."""
        intake = HumanDecisionIntake()
        
        # Create approval
        intake.record_human_decision(
            raw_text="APPROVE: test",
            source="copilot",
            plan_id="plan-123",
            plan_hash="hash-abc",
        )
        
        # Invalidate it
        result = intake.invalidate_approval("plan-123")
        assert result is True
        
        # EXECUTE should now fail
        execute_result = intake.record_human_decision(
            raw_text="EXECUTE",
            source="copilot",
            plan_id="plan-123",
            plan_hash="hash-abc",
        )
        assert execute_result.status == DecisionStatus.REJECTED


# =============================================================================
# System Message Tests
# =============================================================================


class TestSystemMessages:
    """Tests for system message formatting."""
    
    def test_accepted_message_format(self):
        """Accepted result produces [System State] message."""
        intake = HumanDecisionIntake()
        
        result = intake.record_human_decision(
            raw_text="APPROVE: test rationale",
            source="copilot",
        )
        
        msg = result.to_system_message()
        assert msg.startswith("[System State]")
        assert "Decision recorded" in msg or "recorded" in msg
    
    def test_rejected_message_format(self):
        """Rejected result produces [System State] message."""
        intake = HumanDecisionIntake()
        
        result = intake.record_human_decision(
            raw_text="yes",
            source="copilot",
        )
        
        msg = result.to_system_message()
        assert msg.startswith("[System State]")
        assert "rejected" in msg


# =============================================================================
# CLI/Copilot Parity Tests
# =============================================================================


class TestCLICopilotParity:
    """Tests that CLI and Copilot paths behave identically."""
    
    def test_same_grammar_enforced_for_cli(self):
        """CLI source enforces same grammar as Copilot."""
        intake = HumanDecisionIntake()
        
        # Both should reject informal approval
        cli_result = intake.record_human_decision("yes", source="cli")
        copilot_result = intake.record_human_decision("yes", source="copilot")
        
        assert cli_result.status == copilot_result.status == DecisionStatus.REJECTED
    
    def test_same_grammar_enforced_for_api(self):
        """API source enforces same grammar."""
        intake = HumanDecisionIntake()
        
        # Both should accept valid APPROVE
        cli_result = intake.record_human_decision("APPROVE: test", source="cli")
        api_result = intake.record_human_decision("APPROVE: test", source="api")
        
        assert cli_result.status == api_result.status == DecisionStatus.ACCEPTED
    
    def test_nonce_isolation_between_sources(self):
        """Nonces are unique across sources."""
        intake = HumanDecisionIntake()
        
        cli_result = intake.record_human_decision("APPROVE: test", source="cli")
        copilot_result = intake.record_human_decision("APPROVE: test", source="copilot")
        
        assert cli_result.nonce != copilot_result.nonce


# =============================================================================
# Security Invariant Tests
# =============================================================================


class TestSecurityInvariants:
    """Tests for security invariants."""
    
    def test_copilot_cannot_auto_approve(self):
        """Verify Copilot cannot approve without proper grammar."""
        intake = HumanDecisionIntake()
        
        # Try various Copilot-like responses
        responses = [
            "Approved by Copilot",
            "[Copilot] I approve this",
            "Auto-approved",
            "System: approved",
        ]
        
        for response in responses:
            result = intake.record_human_decision(response, source="copilot")
            assert result.status == DecisionStatus.REJECTED
    
    def test_execution_cannot_bypass_approval(self):
        """Verify execution cannot bypass approval step."""
        intake = HumanDecisionIntake()
        
        # Try to execute without approval
        result = intake.record_human_decision(
            raw_text="EXECUTE",
            source="copilot",
            plan_id="plan-123",
            plan_hash="hash-abc",
        )
        
        assert result.status == DecisionStatus.REJECTED
    
    def test_approval_cannot_be_replayed(self):
        """Verify nonces prevent replay attacks."""
        intake = HumanDecisionIntake()
        
        # Record approval
        result1 = intake.record_human_decision("APPROVE: first", source="copilot")
        nonce1 = result1.nonce
        
        # Nonce should be marked as used
        assert intake._nonce_registry.is_used(nonce1) is True
    
    def test_violation_includes_suggestion(self):
        """Verify violations include helpful suggestions."""
        intake = HumanDecisionIntake()
        
        result = intake.record_human_decision("yes", source="copilot")
        
        assert result.violation is not None
        assert result.violation.suggestion is not None
        assert "APPROVE:" in result.violation.suggestion


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
