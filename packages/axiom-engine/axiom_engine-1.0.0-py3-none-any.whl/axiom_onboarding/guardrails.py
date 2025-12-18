"""
First-Run UX Guardrails.

This module provides safety guardrails for first-run experiences,
ensuring users cannot accidentally:
- Execute code without approval
- Skip required steps
- Confuse AI recommendations with human authority
- Bypass governance mechanisms

GUARDRAIL PRINCIPLES:
1. EXPLICIT APPROVAL: No action executes without explicit human approval
2. NO STEP SKIPPING: Required steps cannot be skipped
3. AI ≠ HUMAN: AI recommendations are always clearly labeled
4. EXPLAIN BLOCKS: When something is blocked, explain WHY
5. SAFE DEFAULTS: Default to safest option
6. RECOVERABLE: Guardrail violations don't corrupt state

RULES (ABSOLUTE):
- A blocked action is SAFE
- An unblocked action is DANGEROUS
- Guardrails are NEVER bypassed by clever code
- Guardrails are ALWAYS enforced, even in tests
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


# =============================================================================
# Guardrail Types
# =============================================================================


class GuardrailLevel(str, Enum):
    """Severity level of a guardrail check."""
    
    CRITICAL = "critical"  # Must pass, blocks execution
    WARNING = "warning"    # Should pass, warns but allows
    INFO = "info"          # Informational only


class GuardrailCategory(str, Enum):
    """Category of guardrail check."""
    
    APPROVAL = "approval"         # Human approval checks
    SEQUENCING = "sequencing"     # Step order checks
    LABELING = "labeling"         # AI vs Human labeling
    INITIALIZATION = "initialization"  # First-run initialization
    STATE = "state"               # State consistency
    SAFETY = "safety"             # General safety checks


class GuardrailOutcome(str, Enum):
    """Result of a guardrail check."""
    
    PASSED = "passed"        # Check passed
    FAILED = "failed"        # Check failed (action blocked)
    WARNING = "warning"      # Check raised warning (action allowed)
    SKIPPED = "skipped"      # Check not applicable


# =============================================================================
# Guardrail Check Definition
# =============================================================================


@dataclass
class GuardrailCheck:
    """
    Definition of a guardrail check.
    
    Attributes:
        id: Unique identifier for this check.
        name: Human-readable name.
        description: What this check validates.
        category: Category of check.
        level: Severity level.
        check_fn: Function that performs the check.
        block_message: Message shown when check fails.
        explanation: Why this check matters.
        remediation: How to fix a failure.
    """
    
    id: str
    name: str
    description: str
    category: GuardrailCategory
    level: GuardrailLevel
    check_fn: Optional[Callable[..., bool]] = None
    block_message: str = ""
    explanation: str = ""
    remediation: str = ""


@dataclass
class GuardrailResult:
    """
    Result of executing a guardrail check.
    
    Attributes:
        check: The check that was executed.
        outcome: Result of the check.
        message: Human-readable result message.
        timestamp: When the check was performed.
        context: Additional context data.
        blocked_action: Action that was blocked (if any).
    """
    
    check: GuardrailCheck
    outcome: GuardrailOutcome
    message: str
    timestamp: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    blocked_action: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    @property
    def passed(self) -> bool:
        """Whether the check passed."""
        return self.outcome in (GuardrailOutcome.PASSED, GuardrailOutcome.SKIPPED)
    
    @property
    def blocked(self) -> bool:
        """Whether the check blocked an action."""
        return self.outcome == GuardrailOutcome.FAILED


# =============================================================================
# Guardrail Violation
# =============================================================================


class GuardrailViolation(Exception):
    """
    Exception raised when a guardrail is violated.
    
    This exception is special:
    - It MUST be raised, never silently caught
    - It provides complete explanation
    - It provides remediation steps
    - It never corrupts state
    
    Attributes:
        result: The guardrail result that caused the violation.
        action: The action that was attempted.
        explanation: Why the action was blocked.
        remediation: How to properly accomplish the intent.
    """
    
    def __init__(
        self,
        result: GuardrailResult,
        action: str = "",
        explanation: str = "",
        remediation: str = "",
    ) -> None:
        """
        Initialize guardrail violation.
        
        Args:
            result: The failed guardrail result.
            action: What action was attempted.
            explanation: Why it was blocked.
            remediation: How to fix it.
        """
        self.result = result
        self.action = action or result.blocked_action or "Unknown action"
        self.explanation = explanation or result.check.explanation
        self.remediation = remediation or result.check.remediation
        
        message = self._build_message()
        super().__init__(message)
    
    def _build_message(self) -> str:
        """Build comprehensive error message."""
        lines = []
        lines.append("")
        lines.append("╔════════════════════════════════════════════════════════════╗")
        lines.append("║              GUARDRAIL VIOLATION                           ║")
        lines.append("╠════════════════════════════════════════════════════════════╣")
        lines.append("")
        lines.append(f"  Action Blocked: {self.action}")
        lines.append("")
        lines.append(f"  Check: {self.result.check.name}")
        lines.append(f"  Category: {self.result.check.category.value}")
        lines.append(f"  Level: {self.result.check.level.value.upper()}")
        lines.append("")
        lines.append("  Why This Was Blocked:")
        lines.append(f"    {self.explanation}")
        lines.append("")
        lines.append("  How To Fix:")
        lines.append(f"    {self.remediation}")
        lines.append("")
        lines.append("╚════════════════════════════════════════════════════════════╝")
        lines.append("")
        
        return "\n".join(lines)


# =============================================================================
# Standard Guardrail Checks
# =============================================================================


# Human approval check
APPROVAL_REQUIRED = GuardrailCheck(
    id="approval_required",
    name="Human Approval Required",
    description="Verify human has approved the action",
    category=GuardrailCategory.APPROVAL,
    level=GuardrailLevel.CRITICAL,
    block_message="Action requires explicit human approval",
    explanation="Axiom requires human approval before executing actions that modify files, run code, or affect external systems.",
    remediation="Call the approve() method with confirm=True after reviewing the proposed action.",
)

# Step sequencing check
STEP_SEQUENCING = GuardrailCheck(
    id="step_sequencing",
    name="Step Sequencing",
    description="Verify steps are executed in correct order",
    category=GuardrailCategory.SEQUENCING,
    level=GuardrailLevel.CRITICAL,
    block_message="Cannot skip required steps",
    explanation="Axiom enforces a strict step order to ensure safety and correctness. Skipping steps can lead to inconsistent state.",
    remediation="Complete the current step before proceeding to the next one.",
)

# AI label check
AI_LABELED = GuardrailCheck(
    id="ai_labeled",
    name="AI Output Labeled",
    description="Verify AI output is clearly labeled",
    category=GuardrailCategory.LABELING,
    level=GuardrailLevel.CRITICAL,
    block_message="AI output must be clearly labeled",
    explanation="All AI-generated content must be clearly distinguished from human decisions to prevent confusion.",
    remediation="Use the AI_ADVISORY or AI_GENERATED markers when presenting AI content.",
)

# Initialization check
INITIALIZATION_REQUIRED = GuardrailCheck(
    id="initialization_required",
    name="Initialization Required",
    description="Verify system is properly initialized",
    category=GuardrailCategory.INITIALIZATION,
    level=GuardrailLevel.CRITICAL,
    block_message="System must be initialized first",
    explanation="This action requires the system to be properly initialized with Canon artifacts.",
    remediation="Complete the onboarding flow before attempting this action.",
)

# State consistency check
STATE_CONSISTENT = GuardrailCheck(
    id="state_consistent",
    name="State Consistency",
    description="Verify system state is consistent",
    category=GuardrailCategory.STATE,
    level=GuardrailLevel.CRITICAL,
    block_message="System state is inconsistent",
    explanation="The system detected an inconsistent state that could lead to corruption.",
    remediation="Rollback to a known good state and retry.",
)


# =============================================================================
# First-Run Guard
# =============================================================================


class FirstRunGuard:
    """
    First-run experience guardrails.
    
    This class enforces safety guardrails during the first-run experience,
    preventing users from accidentally skipping steps, executing without
    approval, or confusing AI recommendations with human authority.
    
    RULES:
    - All checks are mandatory
    - CRITICAL failures block execution
    - Violations are never silently ignored
    - State is never corrupted by violations
    
    Attributes:
        checks: Registered guardrail checks.
        results: History of check results.
        strict_mode: If True, warnings also block.
    """
    
    def __init__(self, strict_mode: bool = False) -> None:
        """
        Initialize first-run guard.
        
        Args:
            strict_mode: If True, treat warnings as failures.
        """
        self.strict_mode = strict_mode
        self.checks: Dict[str, GuardrailCheck] = {}
        self.results: List[GuardrailResult] = []
        
        # Register standard checks
        self._register_standard_checks()
    
    def _register_standard_checks(self) -> None:
        """Register the standard guardrail checks."""
        standard_checks = [
            APPROVAL_REQUIRED,
            STEP_SEQUENCING,
            AI_LABELED,
            INITIALIZATION_REQUIRED,
            STATE_CONSISTENT,
        ]
        
        for check in standard_checks:
            self.checks[check.id] = check
    
    def register_check(self, check: GuardrailCheck) -> None:
        """
        Register a custom guardrail check.
        
        Args:
            check: The check to register.
        """
        self.checks[check.id] = check
    
    # =========================================================================
    # Check Execution
    # =========================================================================
    
    def require_approval(
        self,
        action: str,
        approved: bool,
        description: str = "",
    ) -> GuardrailResult:
        """
        Require human approval for an action.
        
        Args:
            action: The action being attempted.
            approved: Whether approval was given.
            description: Description of what will happen.
        
        Returns:
            GuardrailResult indicating pass or fail.
        
        Raises:
            GuardrailViolation: If approval was not given.
        """
        check = self.checks["approval_required"]
        
        if approved:
            result = GuardrailResult(
                check=check,
                outcome=GuardrailOutcome.PASSED,
                message=f"Approved: {action}",
                context={"action": action, "description": description},
            )
        else:
            result = GuardrailResult(
                check=check,
                outcome=GuardrailOutcome.FAILED,
                message=f"Not approved: {action}",
                blocked_action=action,
                context={"action": action, "description": description},
            )
        
        self.results.append(result)
        
        if result.blocked:
            raise GuardrailViolation(
                result=result,
                action=action,
                explanation=f"Human approval is required to {action.lower()}. "
                           f"{description}",
                remediation="Review the proposed action and call with approved=True",
            )
        
        return result
    
    def require_step_order(
        self,
        current_step: str,
        required_step: str,
        step_complete: bool,
    ) -> GuardrailResult:
        """
        Require step sequencing.
        
        Args:
            current_step: The step being attempted.
            required_step: The step that must be complete.
            step_complete: Whether required step is complete.
        
        Returns:
            GuardrailResult indicating pass or fail.
        
        Raises:
            GuardrailViolation: If step order is violated.
        """
        check = self.checks["step_sequencing"]
        
        if step_complete:
            result = GuardrailResult(
                check=check,
                outcome=GuardrailOutcome.PASSED,
                message=f"Step order valid: {current_step}",
                context={"current": current_step, "required": required_step},
            )
        else:
            result = GuardrailResult(
                check=check,
                outcome=GuardrailOutcome.FAILED,
                message=f"Cannot proceed to {current_step}: {required_step} not complete",
                blocked_action=current_step,
                context={"current": current_step, "required": required_step},
            )
        
        self.results.append(result)
        
        if result.blocked:
            raise GuardrailViolation(
                result=result,
                action=f"proceed to {current_step}",
                explanation=f"Step '{required_step}' must be completed before '{current_step}'.",
                remediation=f"Complete {required_step} first, then proceed to {current_step}.",
            )
        
        return result
    
    def require_ai_label(
        self,
        content: str,
        is_labeled: bool,
        content_type: str = "output",
    ) -> GuardrailResult:
        """
        Require AI content to be labeled.
        
        Args:
            content: The content being presented.
            is_labeled: Whether it's properly labeled.
            content_type: Type of content (output, recommendation, etc.).
        
        Returns:
            GuardrailResult indicating pass or fail.
        
        Raises:
            GuardrailViolation: If AI content is not labeled.
        """
        check = self.checks["ai_labeled"]
        
        if is_labeled:
            result = GuardrailResult(
                check=check,
                outcome=GuardrailOutcome.PASSED,
                message=f"AI {content_type} properly labeled",
                context={"content_type": content_type},
            )
        else:
            result = GuardrailResult(
                check=check,
                outcome=GuardrailOutcome.FAILED,
                message=f"AI {content_type} not properly labeled",
                blocked_action=f"present unlabeled AI {content_type}",
                context={"content_type": content_type},
            )
        
        self.results.append(result)
        
        if result.blocked:
            raise GuardrailViolation(
                result=result,
                action=f"present AI {content_type}",
                explanation="AI-generated content must be clearly labeled to distinguish "
                           "it from human decisions.",
                remediation="Add AI_ADVISORY or AI_GENERATED markers to the content.",
            )
        
        return result
    
    def require_initialization(
        self,
        action: str,
        initialized: bool,
        missing: List[str] = None,
    ) -> GuardrailResult:
        """
        Require system initialization.
        
        Args:
            action: The action being attempted.
            initialized: Whether system is initialized.
            missing: List of missing components.
        
        Returns:
            GuardrailResult indicating pass or fail.
        
        Raises:
            GuardrailViolation: If system is not initialized.
        """
        check = self.checks["initialization_required"]
        missing = missing or []
        
        if initialized:
            result = GuardrailResult(
                check=check,
                outcome=GuardrailOutcome.PASSED,
                message=f"Initialization verified for: {action}",
                context={"action": action},
            )
        else:
            result = GuardrailResult(
                check=check,
                outcome=GuardrailOutcome.FAILED,
                message=f"Not initialized for: {action}",
                blocked_action=action,
                context={"action": action, "missing": missing},
            )
        
        self.results.append(result)
        
        if result.blocked:
            missing_str = ", ".join(missing) if missing else "Canon artifacts"
            raise GuardrailViolation(
                result=result,
                action=action,
                explanation=f"The system must be initialized before {action.lower()}. "
                           f"Missing: {missing_str}",
                remediation="Complete the onboarding flow to initialize required components.",
            )
        
        return result
    
    def require_state_consistency(
        self,
        action: str,
        consistent: bool,
        inconsistencies: List[str] = None,
    ) -> GuardrailResult:
        """
        Require state consistency.
        
        Args:
            action: The action being attempted.
            consistent: Whether state is consistent.
            inconsistencies: List of inconsistencies found.
        
        Returns:
            GuardrailResult indicating pass or fail.
        
        Raises:
            GuardrailViolation: If state is inconsistent.
        """
        check = self.checks["state_consistent"]
        inconsistencies = inconsistencies or []
        
        if consistent:
            result = GuardrailResult(
                check=check,
                outcome=GuardrailOutcome.PASSED,
                message=f"State consistent for: {action}",
                context={"action": action},
            )
        else:
            result = GuardrailResult(
                check=check,
                outcome=GuardrailOutcome.FAILED,
                message=f"State inconsistent for: {action}",
                blocked_action=action,
                context={"action": action, "inconsistencies": inconsistencies},
            )
        
        self.results.append(result)
        
        if result.blocked:
            issues = ", ".join(inconsistencies) if inconsistencies else "state mismatch"
            raise GuardrailViolation(
                result=result,
                action=action,
                explanation=f"The system state is inconsistent: {issues}",
                remediation="Rollback to a known good state or restart the operation.",
            )
        
        return result
    
    # =========================================================================
    # AI Labeling Helpers
    # =========================================================================
    
    @staticmethod
    def label_ai_advisory(content: str) -> str:
        """
        Label content as AI advisory.
        
        Args:
            content: The AI-generated content.
        
        Returns:
            Properly labeled content.
        """
        return f"""
╔═══ AI ADVISORY ══════════════════════════════════════════════╗
║  This is an AI-generated recommendation.                      ║
║  Human review and approval is REQUIRED before action.         ║
╠══════════════════════════════════════════════════════════════╣

{content}

╠══════════════════════════════════════════════════════════════╣
║  ⚠  DO NOT EXECUTE without human review and approval.        ║
╚══════════════════════════════════════════════════════════════╝
"""
    
    @staticmethod
    def label_ai_generated(content: str, purpose: str = "") -> str:
        """
        Label content as AI generated.
        
        Args:
            content: The AI-generated content.
            purpose: What the content is for.
        
        Returns:
            Properly labeled content.
        """
        purpose_line = f"  Purpose: {purpose}" if purpose else ""
        return f"""
┌─── AI-GENERATED ────────────────────────────────────────────┐
│  This content was generated by AI.                           │
│  It is NOT a human decision.{purpose_line}                            │
├──────────────────────────────────────────────────────────────┤

{content}

└──────────────────────────────────────────────────────────────┘
"""
    
    @staticmethod
    def label_human_decision(content: str, decision_by: str = "User") -> str:
        """
        Label content as human decision.
        
        Args:
            content: The human decision.
            decision_by: Who made the decision.
        
        Returns:
            Properly labeled content.
        """
        return f"""
╔═══ HUMAN DECISION ═══════════════════════════════════════════╗
║  Decision By: {decision_by:<48}║
║  This is an authoritative human decision.                    ║
╠══════════════════════════════════════════════════════════════╣

{content}

╚══════════════════════════════════════════════════════════════╝
"""
    
    # =========================================================================
    # Summary
    # =========================================================================
    
    def get_summary(self) -> str:
        """
        Get summary of all guardrail checks.
        
        Returns:
            Formatted summary of checks.
        """
        lines = []
        lines.append("")
        lines.append("╔═══ GUARDRAIL CHECK SUMMARY ══════════════════════════════════╗")
        lines.append("")
        
        passed = sum(1 for r in self.results if r.outcome == GuardrailOutcome.PASSED)
        failed = sum(1 for r in self.results if r.outcome == GuardrailOutcome.FAILED)
        warnings = sum(1 for r in self.results if r.outcome == GuardrailOutcome.WARNING)
        
        lines.append(f"  Total Checks: {len(self.results)}")
        lines.append(f"  Passed: {passed} ✓")
        lines.append(f"  Failed: {failed} ✗")
        lines.append(f"  Warnings: {warnings} ⚠")
        lines.append("")
        
        if failed > 0:
            lines.append("  ✗ Failed Checks:")
            for result in self.results:
                if result.outcome == GuardrailOutcome.FAILED:
                    lines.append(f"    • {result.check.name}: {result.message}")
            lines.append("")
        
        if warnings > 0:
            lines.append("  ⚠ Warnings:")
            for result in self.results:
                if result.outcome == GuardrailOutcome.WARNING:
                    lines.append(f"    • {result.check.name}: {result.message}")
            lines.append("")
        
        lines.append("╚══════════════════════════════════════════════════════════════╝")
        lines.append("")
        
        return "\n".join(lines)
    
    def clear_results(self) -> None:
        """Clear check history."""
        self.results.clear()


# =============================================================================
# Guardrail Decorators
# =============================================================================


def requires_approval(action_name: str):
    """
    Decorator that requires approval before a function executes.
    
    Args:
        action_name: Name of the action for the approval check.
    
    Returns:
        Decorator function.
    
    Example:
        @requires_approval("execute_task")
        def execute_task(self, task, approved=False):
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Look for 'approved' in kwargs or assume False
            approved = kwargs.get("approved", False)
            
            # Look for a guard instance in self
            self = args[0] if args else None
            guard = getattr(self, "_guard", None) if self else None
            
            if guard is None:
                guard = FirstRunGuard()
            
            # Run approval check (will raise if not approved)
            guard.require_approval(
                action=action_name,
                approved=approved,
            )
            
            return func(*args, **kwargs)
        
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    
    return decorator


def requires_initialization(*required_components: str):
    """
    Decorator that requires initialization before a function executes.
    
    Args:
        required_components: Names of required components.
    
    Returns:
        Decorator function.
    
    Example:
        @requires_initialization("cpkg", "ucir")
        def run_workflow(self):
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            self = args[0] if args else None
            guard = getattr(self, "_guard", None) if self else None
            
            if guard is None:
                guard = FirstRunGuard()
            
            # Check each required component
            missing = []
            for component in required_components:
                if self and not hasattr(self, component):
                    missing.append(component)
                elif self and getattr(self, component, None) is None:
                    missing.append(component)
            
            guard.require_initialization(
                action=func.__name__,
                initialized=len(missing) == 0,
                missing=missing,
            )
            
            return func(*args, **kwargs)
        
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    
    return decorator
