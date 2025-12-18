"""
Human-in-the-Loop Authorization.

This module defines the structures and interfaces for human ratification
of strategic decisions. It ensures that no AI decision is final without
explicit human consent or pre-authorized policy.

Responsibilities:
- Define HumanDecision structures.
- Merge StrategicDecision (AI) and HumanDecision (Human) into FinalDecision.
- Enforce override rules.

Constraints:
- No execution.
- No persistence.
- Deterministic logic.
"""

import hashlib
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime, timezone

from axiom_archon.model import StrategicDecision, StrategicDecisionType


class HumanDecisionAction(str, Enum):
    """
    The explicit action taken by the human operator.
    """
    APPROVE = "approve"       # Ratify the AI's decision (if AI approved).
    REJECT = "reject"         # Block execution regardless of AI decision.
    OVERRIDE = "override"     # Force execution despite AI rejection (requires rationale).


@dataclass
class HumanDecision:
    """
    Represents the input from a human operator.
    """
    action: HumanDecisionAction
    user_id: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    rationale: Optional[str] = None
    
    # If overriding, the user must explicitly acknowledge the risk.
    override_target: Optional[StrategicDecisionType] = None


@dataclass
class FinalDecision:
    """
    The final, binding decision that authorizes or blocks execution.
    Result of merging StrategicDecision and HumanDecision.
    """
    id: str
    verdict: StrategicDecisionType
    is_authorized: bool
    strategic_decision: StrategicDecision
    human_decision: HumanDecision
    authorization_signature: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class HumanDecisionHandler:
    """
    Logic for reconciling AI recommendations with Human authority.
    """
    
    def resolve(self, ai_decision: StrategicDecision, human_decision: HumanDecision) -> FinalDecision:
        """
        Produces a FinalDecision based on AI and Human inputs.
        
        Rules:
        1. Human REJECT -> REJECT (Always blocks).
        2. Human OVERRIDE -> APPROVE (If rationale provided).
        3. Human APPROVE + AI APPROVE -> APPROVE.
        4. Human APPROVE + AI REJECT -> REJECT (Cannot simple-approve a rejection).
        """
        decision_id = str(uuid.uuid4())
        
        # Case 1: Human explicitly rejects
        if human_decision.action == HumanDecisionAction.REJECT:
            return FinalDecision(
                id=decision_id,
                verdict=StrategicDecisionType.REJECT,
                is_authorized=False,
                strategic_decision=ai_decision,
                human_decision=human_decision
            )
            
        # Case 2: Human overrides
        if human_decision.action == HumanDecisionAction.OVERRIDE:
            if not human_decision.rationale:
                # Invalid override attempt (missing rationale)
                # We default to REJECT for safety
                return FinalDecision(
                    id=decision_id,
                    verdict=StrategicDecisionType.REJECT,
                    is_authorized=False,
                    strategic_decision=ai_decision,
                    human_decision=human_decision
                )
            
            # Generate a human-authorized signature
            sig = self._generate_signature(ai_decision, human_decision)
            return FinalDecision(
                id=decision_id,
                verdict=StrategicDecisionType.APPROVE,
                is_authorized=True,
                strategic_decision=ai_decision,
                human_decision=human_decision,
                authorization_signature=sig
            )
            
        # Case 3: Human approves
        if human_decision.action == HumanDecisionAction.APPROVE:
            if ai_decision.decision == StrategicDecisionType.APPROVE:
                # Happy path: AI and Human agree
                return FinalDecision(
                    id=decision_id,
                    verdict=StrategicDecisionType.APPROVE,
                    is_authorized=True,
                    strategic_decision=ai_decision,
                    human_decision=human_decision,
                    authorization_signature=ai_decision.authorization_signature
                )
            else:
                # Safety Fallback: AI Rejected, Human tried to simple-approve.
                # This is treated as a REJECT because an Override was required.
                return FinalDecision(
                    id=decision_id,
                    verdict=StrategicDecisionType.REJECT,
                    is_authorized=False,
                    strategic_decision=ai_decision,
                    human_decision=human_decision
                )
        
        # Default Fallback (Should be unreachable with valid Enums)
        return FinalDecision(
            id=decision_id,
            verdict=StrategicDecisionType.REJECT,
            is_authorized=False,
            strategic_decision=ai_decision,
            human_decision=human_decision
        )

    def _generate_signature(self, ai: StrategicDecision, human: HumanDecision) -> str:
        """
        Generates a cryptographic signature for the final decision.
        """
        payload = f"{ai.decision.value}:{human.action.value}:{human.user_id}:{human.timestamp}"
        return hashlib.sha256(payload.encode()).hexdigest()
