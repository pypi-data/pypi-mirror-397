"""
Axiom Decision Display Module.

This module provides READ-ONLY visualization of Axiom's decision-making process.
It clearly displays the distinction between:
- AI Recommendation (StrategicDecision)
- Human Authorization (HumanDecision)
- Final Binding Decision (FinalDecision)

CRITICAL DESIGN PRINCIPLE: CLARITY OVER CONVENIENCE

This module:
- Makes it IMPOSSIBLE to confuse recommendation with authorization
- Shows all risks and issues without summarization
- Never hides the human decision step
- Always shows the full decision chain

This module does NOT:
- Make decisions
- Influence decisions
- Skip decision steps
- Collapse multiple decisions into one

UX Principle: Trust Through Transparency
Every decision step must be visible.
Every risk must be surfaced.
Every authorization must be explicit.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from axiom_archon.model import (
    StrategicDecision,
    StrategicDecisionType,
    StrategicIssue,
    StrategicIssueSeverity,
)
from axiom_archon.human_loop import (
    HumanDecision,
    HumanDecisionAction,
    FinalDecision,
)


# =============================================================================
# Decision Display Classes
# =============================================================================


class StrategicDecisionDisplay:
    """
    READ-ONLY visualization of AI Strategic Decisions.
    
    Clearly labels this as an AI RECOMMENDATION, not a final decision.
    Shows all issues with full severity information.
    """
    
    @staticmethod
    def render(decision: StrategicDecision) -> str:
        """
        Render a StrategicDecision for human review.
        
        Args:
            decision: The AI's strategic decision.
            
        Returns:
            Formatted display string.
        """
        lines: List[str] = []
        
        # Header with clear labeling
        lines.append("╔" + "═" * 58 + "╗")
        lines.append("║" + " AI RECOMMENDATION (NOT FINAL)".center(58) + "║")
        lines.append("╠" + "═" * 58 + "╣")
        lines.append("")
        
        # Verdict with icon
        verdict_icon = StrategicDecisionDisplay._get_verdict_icon(decision.decision)
        lines.append(f"  {verdict_icon} AI Verdict: {decision.decision.value.upper()}")
        lines.append("")
        
        # Reason
        lines.append(f"  Reason: {decision.reason}")
        lines.append("")
        
        # Issues (NEVER hidden)
        if decision.issues:
            lines.append("  " + "-" * 50)
            lines.append("  IDENTIFIED ISSUES:")
            lines.append("  " + "-" * 50)
            
            for issue in decision.issues:
                severity_icon = StrategicDecisionDisplay._get_severity_icon(issue.severity)
                lines.append(f"    {severity_icon} [{issue.severity.value.upper()}] {issue.message}")
                if issue.context:
                    for key, val in issue.context.items():
                        lines.append(f"       {key}: {val}")
                lines.append("")
        else:
            lines.append("  Issues: None identified")
            lines.append("")
        
        # Clear footer
        lines.append("╠" + "═" * 58 + "╣")
        lines.append("║" + " ⚠ THIS IS A RECOMMENDATION - HUMAN DECISION REQUIRED ⚠ ".center(58) + "║")
        lines.append("╚" + "═" * 58 + "╝")
        lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def _get_verdict_icon(verdict: StrategicDecisionType) -> str:
        """Get icon for decision type."""
        icons = {
            StrategicDecisionType.APPROVE: "✓",
            StrategicDecisionType.REJECT: "✗",
            StrategicDecisionType.REVISE: "↻",
            StrategicDecisionType.ESCALATE: "⚠",
        }
        return icons.get(verdict, "?")
    
    @staticmethod
    def _get_severity_icon(severity: StrategicIssueSeverity) -> str:
        """Get icon for issue severity."""
        icons = {
            StrategicIssueSeverity.INFO: "ℹ",
            StrategicIssueSeverity.WARNING: "⚠",
            StrategicIssueSeverity.RISK: "⚡",
            StrategicIssueSeverity.BLOCKER: "⛔",
        }
        return icons.get(severity, "?")


class HumanDecisionDisplay:
    """
    READ-ONLY visualization of Human Decisions.
    
    Clearly shows what action the human took and why.
    """
    
    @staticmethod
    def render(decision: HumanDecision) -> str:
        """
        Render a HumanDecision.
        
        Args:
            decision: The human's decision.
            
        Returns:
            Formatted display string.
        """
        lines: List[str] = []
        
        # Header
        lines.append("╔" + "═" * 58 + "╗")
        lines.append("║" + " HUMAN DECISION".center(58) + "║")
        lines.append("╠" + "═" * 58 + "╣")
        lines.append("")
        
        # Action with icon
        action_icon = HumanDecisionDisplay._get_action_icon(decision.action)
        lines.append(f"  {action_icon} Action: {decision.action.value.upper()}")
        lines.append("")
        
        # User
        lines.append(f"  User: {decision.user_id}")
        lines.append(f"  Time: {decision.timestamp}")
        lines.append("")
        
        # Rationale (especially important for OVERRIDE)
        if decision.rationale:
            lines.append("  Rationale:")
            lines.append(f"    {decision.rationale}")
            lines.append("")
        
        # Override target (if applicable)
        if decision.action == HumanDecisionAction.OVERRIDE and decision.override_target:
            lines.append("  ⚠ OVERRIDE:")
            lines.append(f"    Overriding AI verdict: {decision.override_target.value}")
            lines.append("    ⚠ Human has assumed responsibility for this decision")
            lines.append("")
        
        lines.append("╚" + "═" * 58 + "╝")
        lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def _get_action_icon(action: HumanDecisionAction) -> str:
        """Get icon for human action."""
        icons = {
            HumanDecisionAction.APPROVE: "✓",
            HumanDecisionAction.REJECT: "✗",
            HumanDecisionAction.OVERRIDE: "⚡",
        }
        return icons.get(action, "?")


class FinalDecisionDisplay:
    """
    READ-ONLY visualization of Final Decisions.
    
    Shows the binding, authoritative decision that controls execution.
    Makes clear whether execution is authorized.
    """
    
    @staticmethod
    def render(decision: FinalDecision) -> str:
        """
        Render a FinalDecision.
        
        Args:
            decision: The final binding decision.
            
        Returns:
            Formatted display string.
        """
        lines: List[str] = []
        
        # Header with authorization status
        auth_status = "AUTHORIZED" if decision.is_authorized else "NOT AUTHORIZED"
        header_color = "✓" if decision.is_authorized else "✗"
        
        lines.append("╔" + "═" * 58 + "╗")
        lines.append("║" + f" {header_color} FINAL DECISION: {auth_status} ".center(58) + "║")
        lines.append("╠" + "═" * 58 + "╣")
        lines.append("")
        
        # Verdict
        lines.append(f"  Final Verdict: {decision.verdict.value.upper()}")
        lines.append(f"  Is Authorized: {'YES' if decision.is_authorized else 'NO'}")
        lines.append("")
        
        # Decision chain
        lines.append("  Decision Chain:")
        lines.append(f"    1. AI Recommended: {decision.strategic_decision.decision.value}")
        lines.append(f"    2. Human Decided:  {decision.human_decision.action.value}")
        lines.append(f"    3. Final Verdict:  {decision.verdict.value}")
        lines.append("")
        
        # Authorization signature
        if decision.authorization_signature:
            lines.append(f"  Authorization Signature: {decision.authorization_signature[:20]}...")
        lines.append(f"  Decision ID: {decision.id}")
        lines.append(f"  Timestamp: {decision.timestamp}")
        lines.append("")
        
        # Execution status
        if decision.is_authorized:
            lines.append("  ✓ EXECUTION MAY PROCEED")
        else:
            lines.append("  ✗ EXECUTION IS BLOCKED")
        lines.append("")
        
        lines.append("╚" + "═" * 58 + "╝")
        lines.append("")
        
        return "\n".join(lines)


class DecisionChainDisplay:
    """
    READ-ONLY visualization of the complete decision chain.
    
    Shows the full progression from AI recommendation to final authorization.
    Makes the governance flow explicit and auditable.
    """
    
    @staticmethod
    def render(
        strategic: StrategicDecision,
        human: HumanDecision,
        final: FinalDecision
    ) -> str:
        """
        Render the complete decision chain.
        
        Args:
            strategic: The AI's recommendation.
            human: The human's decision.
            final: The final binding decision.
            
        Returns:
            Formatted chain display.
        """
        lines: List[str] = []
        
        lines.append("=" * 60)
        lines.append("COMPLETE DECISION CHAIN (GOVERNANCE AUDIT)")
        lines.append("=" * 60)
        lines.append("")
        
        # Phase 1: AI Recommendation
        lines.append("┌─────────────────────────────────────────────────────────┐")
        lines.append("│ PHASE 1: AI RECOMMENDATION                             │")
        lines.append("├─────────────────────────────────────────────────────────┤")
        ai_icon = StrategicDecisionDisplay._get_verdict_icon(strategic.decision)
        lines.append(f"│  {ai_icon} Verdict: {strategic.decision.value:<42} │")
        reason_truncated = strategic.reason[:40] + "..." if len(strategic.reason) > 40 else strategic.reason
        lines.append(f"│  Reason: {reason_truncated:<46} │")
        lines.append(f"│  Issues: {len(strategic.issues):<47} │")
        lines.append("└─────────────────────────────────────────────────────────┘")
        lines.append("                          │")
        lines.append("                          ▼")
        
        # Phase 2: Human Decision
        lines.append("┌─────────────────────────────────────────────────────────┐")
        lines.append("│ PHASE 2: HUMAN DECISION                                 │")
        lines.append("├─────────────────────────────────────────────────────────┤")
        human_icon = HumanDecisionDisplay._get_action_icon(human.action)
        lines.append(f"│  {human_icon} Action: {human.action.value:<43} │")
        lines.append(f"│  User: {human.user_id:<49} │")
        if human.rationale:
            rat_truncated = human.rationale[:40] + "..." if len(human.rationale) > 40 else human.rationale
            lines.append(f"│  Rationale: {rat_truncated:<43} │")
        lines.append("└─────────────────────────────────────────────────────────┘")
        lines.append("                          │")
        lines.append("                          ▼")
        
        # Phase 3: Final Decision
        auth_marker = "✓ AUTHORIZED" if final.is_authorized else "✗ NOT AUTHORIZED"
        lines.append("┌─────────────────────────────────────────────────────────┐")
        lines.append("│ PHASE 3: FINAL DECISION                                 │")
        lines.append("├─────────────────────────────────────────────────────────┤")
        lines.append(f"│  Status: {auth_marker:<46} │")
        lines.append(f"│  Verdict: {final.verdict.value:<45} │")
        lines.append(f"│  ID: {final.id[:50]:<50} │")
        lines.append("└─────────────────────────────────────────────────────────┘")
        lines.append("")
        
        # Summary
        if final.is_authorized:
            lines.append("✓ Governance check PASSED. Execution may proceed.")
        else:
            lines.append("✗ Governance check FAILED. Execution is blocked.")
        lines.append("")
        
        return "\n".join(lines)


class DecisionComparisonDisplay:
    """
    Side-by-side comparison of AI recommendation vs Human decision.
    
    Highlights where human agreed with or overrode AI.
    """
    
    @staticmethod
    def render(strategic: StrategicDecision, human: HumanDecision) -> str:
        """
        Render a side-by-side comparison.
        
        Args:
            strategic: The AI's recommendation.
            human: The human's decision.
            
        Returns:
            Formatted comparison display.
        """
        lines: List[str] = []
        
        lines.append("=" * 60)
        lines.append("AI vs HUMAN DECISION COMPARISON")
        lines.append("=" * 60)
        lines.append("")
        
        # Determine agreement
        ai_approves = strategic.decision == StrategicDecisionType.APPROVE
        human_approves = human.action == HumanDecisionAction.APPROVE
        human_overrides = human.action == HumanDecisionAction.OVERRIDE
        
        # Left: AI, Right: Human
        lines.append("        AI RECOMMENDATION          │         HUMAN DECISION")
        lines.append("═══════════════════════════════════╪═══════════════════════════════════")
        
        ai_verdict = strategic.decision.value.upper()
        human_verdict = human.action.value.upper()
        
        lines.append(f"  Verdict: {ai_verdict:<22} │   Action: {human_verdict}")
        lines.append(f"  Issues: {len(strategic.issues):<23} │   User: {human.user_id}")
        
        lines.append("═══════════════════════════════════╧═══════════════════════════════════")
        lines.append("")
        
        # Agreement analysis
        if ai_approves and human_approves:
            lines.append("  ✓ AGREEMENT: Both AI and Human approved.")
        elif not ai_approves and not human_approves and not human_overrides:
            lines.append("  ✓ AGREEMENT: Both AI and Human rejected.")
        elif human_overrides:
            lines.append("  ⚠ OVERRIDE: Human overrode AI recommendation.")
            lines.append(f"    AI said: {strategic.decision.value}")
            lines.append(f"    Human chose: OVERRIDE")
            if human.rationale:
                lines.append(f"    Reason: {human.rationale}")
        else:
            lines.append("  ⚠ DISAGREEMENT: Human rejected AI approval.")
            lines.append("    This is a safety-first decision.")
        
        lines.append("")
        
        return "\n".join(lines)
