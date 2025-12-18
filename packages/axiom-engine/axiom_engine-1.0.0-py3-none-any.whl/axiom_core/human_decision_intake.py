"""
Human Decision Intake API.

This module provides a STRICT intake surface for human decisions submitted
through external channels (Copilot, CLI, API, etc.).

CORE PRINCIPLE:
Copilot is a WITNESS, not an approver.
All validation and authorization happens inside Axiom.

RESPONSIBILITIES:
- Parse strict approval grammar
- Reject invalid or ambiguous input
- Attach timestamp, nonce, source
- Route through HumanDecisionHandler
- Return explicit success or failure

ABSOLUTE RULES:
1. NEVER trust external parsing
2. NEVER infer intent
3. NEVER auto-approve
4. ALWAYS require explicit rationale
5. ALWAYS enforce replay protection
"""

import hashlib
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List, Tuple

from axiom_archon.human_loop import (
    HumanDecision,
    HumanDecisionAction,
    HumanDecisionHandler,
    FinalDecision,
)
from axiom_archon.model import StrategicDecision


# =============================================================================
# Approval Grammar
# =============================================================================

class ApprovalGrammarAction(str, Enum):
    """
    Strict, case-sensitive approval actions.
    
    These are the ONLY valid approval prefixes.
    Free-form text like "yes", "ok", "looks good" is INVALID.
    """
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    OVERRIDE = "OVERRIDE"
    EXECUTE = "EXECUTE"


# Strict regex patterns - case sensitive, exact match required
# Using (.*) to capture even empty rationales, then validate separately
APPROVAL_PATTERN = re.compile(r"^APPROVE:\s*(.*)$", re.DOTALL)
REJECT_PATTERN = re.compile(r"^REJECT:\s*(.*)$", re.DOTALL)
OVERRIDE_PATTERN = re.compile(r"^OVERRIDE:\s*(.*)$", re.DOTALL)
EXECUTE_PATTERN = re.compile(r"^EXECUTE$")

# Invalid patterns - these MUST be rejected
INVALID_APPROVALS = frozenset({
    "yes",
    "ok",
    "okay",
    "sure",
    "looks good",
    "lgtm",
    "approved",
    "approve",  # Must be "APPROVE:" with rationale
    "go ahead",
    "proceed",
    "do it",
    "y",
    "👍",
    "✅",
})


class GrammarViolationType(str, Enum):
    """Types of grammar violations."""
    
    EMPTY_INPUT = "empty_input"
    MISSING_PREFIX = "missing_prefix"
    INVALID_PREFIX = "invalid_prefix"
    MISSING_RATIONALE = "missing_rationale"
    EMPTY_RATIONALE = "empty_rationale"
    INFORMAL_APPROVAL = "informal_approval"
    EXECUTE_WITH_RATIONALE = "execute_with_rationale"
    UNKNOWN_FORMAT = "unknown_format"


@dataclass(frozen=True)
class GrammarViolation:
    """
    A grammar violation that prevents acceptance.
    
    Attributes:
        type: Type of violation.
        message: Human-readable error message.
        suggestion: Suggested correction.
    """
    
    type: GrammarViolationType
    message: str
    suggestion: str


@dataclass(frozen=True)
class ParsedApproval:
    """
    Result of parsing an approval string.
    
    This is an INTERNAL structure. External callers receive HumanDecisionResult.
    
    Attributes:
        action: The parsed action (APPROVE, REJECT, OVERRIDE, EXECUTE).
        rationale: The provided rationale (None for EXECUTE).
        raw_text: Original text for audit.
    """
    
    action: ApprovalGrammarAction
    rationale: Optional[str]
    raw_text: str


def parse_approval_grammar(raw_text: str) -> Tuple[Optional[ParsedApproval], Optional[GrammarViolation]]:
    """
    Parse raw text against the strict approval grammar.
    
    This function enforces the approval grammar:
    - APPROVE: <rationale>
    - REJECT: <rationale>
    - OVERRIDE: <rationale>
    - EXECUTE (no rationale)
    
    Args:
        raw_text: The raw input text to parse.
        
    Returns:
        Tuple of (ParsedApproval or None, GrammarViolation or None).
        Exactly one will be non-None.
    """
    if not raw_text:
        return None, GrammarViolation(
            type=GrammarViolationType.EMPTY_INPUT,
            message="Empty input is not a valid approval.",
            suggestion="Use: APPROVE: <your rationale>"
        )
    
    # Strip and normalize
    text = raw_text.strip()
    
    if not text:
        return None, GrammarViolation(
            type=GrammarViolationType.EMPTY_INPUT,
            message="Empty input is not a valid approval.",
            suggestion="Use: APPROVE: <your rationale>"
        )
    
    # Check for invalid informal approvals
    if text.lower() in INVALID_APPROVALS:
        return None, GrammarViolation(
            type=GrammarViolationType.INFORMAL_APPROVAL,
            message=f"'{text}' is not a valid approval. Axiom requires explicit structured approval.",
            suggestion="Use: APPROVE: <your rationale explaining why you approve>"
        )
    
    # Try APPROVE pattern
    match = APPROVAL_PATTERN.match(text)
    if match:
        rationale = match.group(1).strip()
        if not rationale:
            return None, GrammarViolation(
                type=GrammarViolationType.EMPTY_RATIONALE,
                message="APPROVE requires a non-empty rationale.",
                suggestion="Use: APPROVE: <explain why you approve this plan>"
            )
        return ParsedApproval(
            action=ApprovalGrammarAction.APPROVE,
            rationale=rationale,
            raw_text=raw_text,
        ), None
    
    # Try REJECT pattern
    match = REJECT_PATTERN.match(text)
    if match:
        rationale = match.group(1).strip()
        if not rationale:
            return None, GrammarViolation(
                type=GrammarViolationType.EMPTY_RATIONALE,
                message="REJECT requires a non-empty rationale.",
                suggestion="Use: REJECT: <explain why you reject this plan>"
            )
        return ParsedApproval(
            action=ApprovalGrammarAction.REJECT,
            rationale=rationale,
            raw_text=raw_text,
        ), None
    
    # Try OVERRIDE pattern
    match = OVERRIDE_PATTERN.match(text)
    if match:
        rationale = match.group(1).strip()
        if not rationale:
            return None, GrammarViolation(
                type=GrammarViolationType.EMPTY_RATIONALE,
                message="OVERRIDE requires a non-empty rationale.",
                suggestion="Use: OVERRIDE: <explain why you override AI recommendation>"
            )
        return ParsedApproval(
            action=ApprovalGrammarAction.OVERRIDE,
            rationale=rationale,
            raw_text=raw_text,
        ), None
    
    # Try EXECUTE pattern
    match = EXECUTE_PATTERN.match(text)
    if match:
        return ParsedApproval(
            action=ApprovalGrammarAction.EXECUTE,
            rationale=None,
            raw_text=raw_text,
        ), None
    
    # Check if they tried EXECUTE with rationale
    if text.startswith("EXECUTE:"):
        return None, GrammarViolation(
            type=GrammarViolationType.EXECUTE_WITH_RATIONALE,
            message="EXECUTE does not take a rationale. It only confirms execution of an approved plan.",
            suggestion="Use: EXECUTE (with no additional text)"
        )
    
    # Check if they used lowercase variants
    if text.lower().startswith(("approve:", "reject:", "override:", "execute")):
        return None, GrammarViolation(
            type=GrammarViolationType.INVALID_PREFIX,
            message="Approval keywords must be UPPERCASE.",
            suggestion=f"Use: {text.split(':')[0].upper()}: <rationale>"
        )
    
    # Unknown format
    return None, GrammarViolation(
        type=GrammarViolationType.UNKNOWN_FORMAT,
        message=f"'{text[:50]}...' does not match any valid approval format.",
        suggestion="Valid formats:\n  APPROVE: <rationale>\n  REJECT: <rationale>\n  OVERRIDE: <rationale>\n  EXECUTE"
    )


# =============================================================================
# Decision Intake Result
# =============================================================================

class DecisionStatus(str, Enum):
    """Status of a human decision intake."""
    
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PENDING_VERIFICATION = "pending_verification"


@dataclass(frozen=True)
class HumanDecisionResult:
    """
    Result of recording a human decision.
    
    This is the ONLY output from the intake API.
    Copilot and other clients receive this, not internal structures.
    
    Attributes:
        status: Whether the decision was accepted.
        message: Human-readable status message.
        decision_id: Unique ID for this decision (if accepted).
        nonce: Anti-replay nonce (if accepted).
        timestamp: When the decision was recorded.
        source: Where the decision came from.
        violation: Grammar violation details (if rejected).
    """
    
    status: DecisionStatus
    message: str
    decision_id: Optional[str] = None
    nonce: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source: Optional[str] = None
    violation: Optional[GrammarViolation] = None
    
    def to_system_message(self) -> str:
        """Format as a system message for display.
        
        Returns:
            System-labeled message string.
        """
        if self.status == DecisionStatus.ACCEPTED:
            return f"[System State] Decision recorded. ID: {self.decision_id}"
        elif self.status == DecisionStatus.REJECTED:
            return f"[System State] Decision rejected: {self.message}"
        else:
            return f"[System State] Decision pending verification: {self.message}"


# =============================================================================
# Execution Authorization
# =============================================================================

@dataclass(frozen=True)
class ExecutionAuthorizationResult:
    """
    Result of checking execution authorization.
    
    Attributes:
        authorized: Whether execution is authorized.
        message: Human-readable message.
        final_decision_id: ID of the authorizing FinalDecision (if authorized).
        plan_id: ID of the plan to execute (if authorized).
    """
    
    authorized: bool
    message: str
    final_decision_id: Optional[str] = None
    plan_id: Optional[str] = None
    
    def to_system_message(self) -> str:
        """Format as a system message for display.
        
        Returns:
            System-labeled message string.
        """
        if self.authorized:
            return f"[System State] Execution authorized for plan: {self.plan_id}"
        else:
            return f"[System State] Execution denied: {self.message}"


# =============================================================================
# Nonce Registry (Replay Protection)
# =============================================================================

class NonceRegistry:
    """
    Registry for tracking used nonces to prevent replay attacks.
    
    Each decision gets a unique nonce. Nonces cannot be reused.
    """
    
    def __init__(self):
        """Initialize an empty registry."""
        self._used_nonces: set = set()
    
    def generate_nonce(self) -> str:
        """Generate a unique nonce.
        
        Returns:
            A unique nonce string.
        """
        nonce = hashlib.sha256(
            f"{uuid.uuid4()}{datetime.now(timezone.utc).isoformat()}".encode()
        ).hexdigest()[:16]
        return nonce
    
    def register_nonce(self, nonce: str) -> bool:
        """Register a nonce as used.
        
        Args:
            nonce: The nonce to register.
            
        Returns:
            True if registered successfully, False if already used.
        """
        if nonce in self._used_nonces:
            return False
        self._used_nonces.add(nonce)
        return True
    
    def is_used(self, nonce: str) -> bool:
        """Check if a nonce has been used.
        
        Args:
            nonce: The nonce to check.
            
        Returns:
            True if already used, False otherwise.
        """
        return nonce in self._used_nonces


# =============================================================================
# Plan Binding (Approval-Plan Linkage)
# =============================================================================

@dataclass
class PlanBinding:
    """
    Binds an approval to a specific plan version.
    
    If the plan changes, the approval is invalidated.
    
    Attributes:
        plan_id: The plan this approval applies to.
        plan_hash: Hash of the plan at approval time.
        approval_nonce: The nonce from the approval.
        decision_id: ID of the HumanDecision.
    """
    
    plan_id: str
    plan_hash: str
    approval_nonce: str
    decision_id: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def is_valid_for_plan(self, plan_id: str, plan_hash: str) -> bool:
        """Check if this binding is valid for a given plan.
        
        Args:
            plan_id: The plan ID to check.
            plan_hash: The current plan hash.
            
        Returns:
            True if the binding is valid, False otherwise.
        """
        return self.plan_id == plan_id and self.plan_hash == plan_hash


# =============================================================================
# Human Decision Intake Service
# =============================================================================

class HumanDecisionIntake:
    """
    Main intake service for human decisions.
    
    This service:
    - Parses approval grammar
    - Validates input
    - Attaches metadata (timestamp, nonce, source)
    - Routes to HumanDecisionHandler
    - Returns explicit results
    
    IMPORTANT:
    - This service lives INSIDE Axiom
    - Copilot and other clients call this service
    - Copilot NEVER performs its own validation
    """
    
    def __init__(self, user_id: str = "unknown"):
        """Initialize the intake service.
        
        Args:
            user_id: Default user ID for decisions.
        """
        self._handler = HumanDecisionHandler()
        self._nonce_registry = NonceRegistry()
        self._plan_bindings: dict[str, PlanBinding] = {}
        self._default_user_id = user_id
    
    def record_human_decision(
        self,
        raw_text: str,
        source: str,
        plan_id: Optional[str] = None,
        plan_hash: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> HumanDecisionResult:
        """
        Record a human decision from raw text.
        
        This is the main entry point for external callers.
        
        Args:
            raw_text: The raw approval text (e.g., "APPROVE: I reviewed this")
            source: Source of the decision ("copilot", "cli", "api")
            plan_id: ID of the plan being approved (optional but recommended)
            plan_hash: Hash of the plan (optional but recommended)
            user_id: ID of the user making the decision
            
        Returns:
            HumanDecisionResult indicating success or failure.
        """
        # 1. Parse the grammar
        parsed, violation = parse_approval_grammar(raw_text)
        
        if violation:
            return HumanDecisionResult(
                status=DecisionStatus.REJECTED,
                message=violation.message,
                source=source,
                violation=violation,
            )
        
        # 2. Handle EXECUTE separately (it's not an approval, it's an execution request)
        if parsed.action == ApprovalGrammarAction.EXECUTE:
            return self._handle_execute_request(source, plan_id, plan_hash, user_id)
        
        # 3. Generate nonce and timestamp
        nonce = self._nonce_registry.generate_nonce()
        timestamp = datetime.now(timezone.utc).isoformat()
        decision_id = str(uuid.uuid4())
        
        # 4. Register the nonce
        if not self._nonce_registry.register_nonce(nonce):
            return HumanDecisionResult(
                status=DecisionStatus.REJECTED,
                message="Nonce collision detected. Please try again.",
                source=source,
            )
        
        # 5. Create plan binding if plan info provided
        if plan_id and plan_hash:
            binding = PlanBinding(
                plan_id=plan_id,
                plan_hash=plan_hash,
                approval_nonce=nonce,
                decision_id=decision_id,
            )
            self._plan_bindings[decision_id] = binding
        
        # 6. Map grammar action to HumanDecisionAction
        action_map = {
            ApprovalGrammarAction.APPROVE: HumanDecisionAction.APPROVE,
            ApprovalGrammarAction.REJECT: HumanDecisionAction.REJECT,
            ApprovalGrammarAction.OVERRIDE: HumanDecisionAction.OVERRIDE,
        }
        
        # 7. Create and return result
        return HumanDecisionResult(
            status=DecisionStatus.ACCEPTED,
            message=f"Decision recorded: {parsed.action.value}",
            decision_id=decision_id,
            nonce=nonce,
            timestamp=timestamp,
            source=source,
        )
    
    def _handle_execute_request(
        self,
        source: str,
        plan_id: Optional[str],
        plan_hash: Optional[str],
        user_id: Optional[str],
    ) -> HumanDecisionResult:
        """
        Handle an EXECUTE request.
        
        EXECUTE is only valid if:
        1. A plan has been approved
        2. The plan has not changed since approval
        
        Args:
            source: Source of the request.
            plan_id: ID of the plan to execute.
            plan_hash: Current hash of the plan.
            user_id: ID of the user.
            
        Returns:
            HumanDecisionResult for the execute request.
        """
        # Check if there's an approved plan
        if not plan_id:
            return HumanDecisionResult(
                status=DecisionStatus.REJECTED,
                message="EXECUTE requires a plan ID. No plan context provided.",
                source=source,
                violation=GrammarViolation(
                    type=GrammarViolationType.MISSING_PREFIX,
                    message="No plan ID provided for execution.",
                    suggestion="Ensure a plan is approved before running EXECUTE."
                ),
            )
        
        # Find the binding for this plan
        binding = None
        for b in self._plan_bindings.values():
            if b.plan_id == plan_id:
                binding = b
                break
        
        if not binding:
            return HumanDecisionResult(
                status=DecisionStatus.REJECTED,
                message=f"No approval found for plan '{plan_id}'. Approve first.",
                source=source,
                violation=GrammarViolation(
                    type=GrammarViolationType.MISSING_PREFIX,
                    message="Plan must be approved before execution.",
                    suggestion="Use: APPROVE: <rationale> to approve the plan first."
                ),
            )
        
        # Verify plan hasn't changed
        if plan_hash and not binding.is_valid_for_plan(plan_id, plan_hash):
            return HumanDecisionResult(
                status=DecisionStatus.REJECTED,
                message="Plan has changed since approval. Re-approve required.",
                source=source,
                violation=GrammarViolation(
                    type=GrammarViolationType.UNKNOWN_FORMAT,
                    message="Plan modified after approval.",
                    suggestion="The plan was modified. Use APPROVE: <rationale> to re-approve."
                ),
            )
        
        # Generate execution nonce
        nonce = self._nonce_registry.generate_nonce()
        timestamp = datetime.now(timezone.utc).isoformat()
        execution_id = str(uuid.uuid4())
        
        if not self._nonce_registry.register_nonce(nonce):
            return HumanDecisionResult(
                status=DecisionStatus.REJECTED,
                message="Nonce collision detected. Please try again.",
                source=source,
            )
        
        return HumanDecisionResult(
            status=DecisionStatus.ACCEPTED,
            message="Execution authorized.",
            decision_id=execution_id,
            nonce=nonce,
            timestamp=timestamp,
            source=source,
        )
    
    def create_human_decision(
        self,
        parsed: ParsedApproval,
        user_id: str,
    ) -> HumanDecision:
        """
        Create a HumanDecision from a parsed approval.
        
        This converts the intake-parsed approval into the internal
        HumanDecision structure used by HumanDecisionHandler.
        
        Args:
            parsed: The parsed approval.
            user_id: The user ID.
            
        Returns:
            A HumanDecision for use with HumanDecisionHandler.
        """
        action_map = {
            ApprovalGrammarAction.APPROVE: HumanDecisionAction.APPROVE,
            ApprovalGrammarAction.REJECT: HumanDecisionAction.REJECT,
            ApprovalGrammarAction.OVERRIDE: HumanDecisionAction.OVERRIDE,
        }
        
        return HumanDecision(
            action=action_map[parsed.action],
            user_id=user_id,
            rationale=parsed.rationale,
        )
    
    def resolve_final_decision(
        self,
        raw_text: str,
        strategic_decision: StrategicDecision,
        source: str,
        plan_id: Optional[str] = None,
        plan_hash: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Tuple[Optional[FinalDecision], HumanDecisionResult]:
        """
        Parse human input and resolve to a FinalDecision.
        
        This is a convenience method that combines:
        1. Parsing the approval grammar
        2. Creating a HumanDecision
        3. Resolving with HumanDecisionHandler
        
        Args:
            raw_text: The raw approval text.
            strategic_decision: The AI's strategic decision.
            source: Source of the decision.
            plan_id: ID of the plan.
            plan_hash: Hash of the plan.
            user_id: ID of the user.
            
        Returns:
            Tuple of (FinalDecision or None, HumanDecisionResult).
        """
        # 1. Parse the grammar
        parsed, violation = parse_approval_grammar(raw_text)
        
        if violation:
            result = HumanDecisionResult(
                status=DecisionStatus.REJECTED,
                message=violation.message,
                source=source,
                violation=violation,
            )
            return None, result
        
        # 2. Reject EXECUTE at this stage
        if parsed.action == ApprovalGrammarAction.EXECUTE:
            result = HumanDecisionResult(
                status=DecisionStatus.REJECTED,
                message="EXECUTE is only valid after approval. Use APPROVE: <rationale> first.",
                source=source,
                violation=GrammarViolation(
                    type=GrammarViolationType.INVALID_PREFIX,
                    message="Cannot EXECUTE during approval phase.",
                    suggestion="Use: APPROVE: <rationale> to approve the plan."
                ),
            )
            return None, result
        
        # 3. Create HumanDecision
        effective_user_id = user_id or self._default_user_id
        human_decision = self.create_human_decision(parsed, effective_user_id)
        
        # 4. Resolve with handler
        final_decision = self._handler.resolve(strategic_decision, human_decision)
        
        # 5. Generate nonce and create result
        nonce = self._nonce_registry.generate_nonce()
        self._nonce_registry.register_nonce(nonce)
        
        # 6. Create plan binding if approved
        if final_decision.is_authorized and plan_id and plan_hash:
            binding = PlanBinding(
                plan_id=plan_id,
                plan_hash=plan_hash,
                approval_nonce=nonce,
                decision_id=final_decision.id,
            )
            self._plan_bindings[final_decision.id] = binding
        
        # 7. Build result
        if final_decision.is_authorized:
            result = HumanDecisionResult(
                status=DecisionStatus.ACCEPTED,
                message=f"Plan {final_decision.verdict.value}. Authorization granted.",
                decision_id=final_decision.id,
                nonce=nonce,
                source=source,
            )
        else:
            result = HumanDecisionResult(
                status=DecisionStatus.ACCEPTED,
                message=f"Plan {final_decision.verdict.value}. Authorization denied.",
                decision_id=final_decision.id,
                nonce=nonce,
                source=source,
            )
        
        return final_decision, result
    
    def check_execution_authorization(
        self,
        plan_id: str,
        plan_hash: str,
    ) -> ExecutionAuthorizationResult:
        """
        Check if execution is authorized for a plan.
        
        Args:
            plan_id: The plan ID to check.
            plan_hash: Current hash of the plan.
            
        Returns:
            ExecutionAuthorizationResult indicating authorization status.
        """
        # Find binding for this plan
        binding = None
        for b in self._plan_bindings.values():
            if b.plan_id == plan_id:
                binding = b
                break
        
        if not binding:
            return ExecutionAuthorizationResult(
                authorized=False,
                message="No approval found for this plan.",
            )
        
        if not binding.is_valid_for_plan(plan_id, plan_hash):
            return ExecutionAuthorizationResult(
                authorized=False,
                message="Plan has changed since approval. Re-approval required.",
            )
        
        return ExecutionAuthorizationResult(
            authorized=True,
            message="Execution authorized.",
            final_decision_id=binding.decision_id,
            plan_id=plan_id,
        )
    
    def invalidate_approval(self, plan_id: str) -> bool:
        """
        Invalidate an existing approval for a plan.
        
        This should be called when a plan changes.
        
        Args:
            plan_id: The plan ID to invalidate.
            
        Returns:
            True if an approval was invalidated, False otherwise.
        """
        to_remove = []
        for decision_id, binding in self._plan_bindings.items():
            if binding.plan_id == plan_id:
                to_remove.append(decision_id)
        
        for decision_id in to_remove:
            del self._plan_bindings[decision_id]
        
        return len(to_remove) > 0


# =============================================================================
# Module-level convenience function
# =============================================================================

_default_intake: Optional[HumanDecisionIntake] = None


def get_default_intake() -> HumanDecisionIntake:
    """Get the default intake service instance.
    
    Returns:
        The default HumanDecisionIntake instance.
    """
    global _default_intake
    if _default_intake is None:
        _default_intake = HumanDecisionIntake()
    return _default_intake


def record_human_decision(
    raw_text: str,
    source: str,
    plan_id: Optional[str] = None,
    plan_hash: Optional[str] = None,
    user_id: Optional[str] = None,
) -> HumanDecisionResult:
    """
    Record a human decision from raw text.
    
    Module-level convenience function.
    
    Args:
        raw_text: The raw approval text.
        source: Source of the decision.
        plan_id: ID of the plan being approved.
        plan_hash: Hash of the plan.
        user_id: ID of the user.
        
    Returns:
        HumanDecisionResult indicating success or failure.
    """
    return get_default_intake().record_human_decision(
        raw_text=raw_text,
        source=source,
        plan_id=plan_id,
        plan_hash=plan_hash,
        user_id=user_id,
    )
