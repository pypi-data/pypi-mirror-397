"""
LLM-Backed Strategic Reviewer.

This module implements an LLM-assisted strategic reviewer that analyzes
proposed plans and surfaces risks, tradeoffs, and concerns to assist
human decision-making.

CRITICAL DESIGN PRINCIPLES:

1. ADVISORY ONLY
   - The LLM recommends; it does NOT decide
   - The LLM identifies risks; it does NOT approve or reject
   - All output is labeled as advisory

2. NO AUTHORITY
   - Cannot approve plans
   - Cannot reject plans
   - Cannot execute plans
   - Cannot modify Canon or plans
   - Cannot trigger replanning
   - Cannot bypass human approval

3. FALLBACK-SAFE
   - LLM unavailability does NOT block workflow
   - Human decision proceeds without AI input
   - Failures are explicit and structured

4. TOKEN-DISCIPLINED
   - Uses Canon consumption contracts
   - Enforces strict token budgets
   - Never exposes raw source code

All LLM-generated reviews are labeled:
"[AI STRATEGIC REVIEW – NOT A DECISION]"

The human ALWAYS has final authority.
"""

import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol

from axiom_archon.model import (
    StrategicContext,
    StrategicDecision,
    StrategicDecisionType,
    StrategicIntent,
    StrategicIssue,
    StrategicIssueSeverity,
)
from axiom_archon.interface import StrategicReviewer
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
)
from axiom_strata.model import PlanningResult, TacticalIntent
from axiom_strata.validation import PlanningValidationResult
from axiom_strata.dry_run import DryRunResult


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class StrategicReviewConfig:
    """
    Configuration for the LLM Strategic Reviewer.
    
    Attributes:
        enabled: Whether LLM review is enabled.
        max_context_tokens: Maximum tokens for context.
        max_output_tokens: Maximum tokens in LLM response.
        timeout_seconds: Timeout for LLM call.
        require_evidence: Require evidence for all risks.
        min_confidence: Minimum confidence to include risks.
    """
    
    enabled: bool = True
    max_context_tokens: int = 4000
    max_output_tokens: int = 2000
    timeout_seconds: int = 60
    require_evidence: bool = True
    min_confidence: ConfidenceLevel = ConfidenceLevel.LOW
    
    def validate(self) -> List[str]:
        """Validate configuration."""
        errors = []
        
        if self.max_context_tokens <= 0:
            errors.append("max_context_tokens must be positive")
        if self.max_context_tokens > 16000:
            errors.append("max_context_tokens cannot exceed 16000")
        if self.max_output_tokens > 4000:
            errors.append("max_output_tokens cannot exceed 4000")
        if self.timeout_seconds > 300:
            errors.append("timeout_seconds cannot exceed 300")
        
        return errors


# =============================================================================
# LLM Backend Protocol
# =============================================================================


class StrategicLLMBackend(Protocol):
    """
    Protocol for LLM backends used in strategic review.
    
    The reviewer does not care how the LLM is called.
    """
    
    def generate(self, prompt: str) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The input prompt.
            
        Returns:
            The LLM's response as a string.
        """
        ...
    
    def is_available(self) -> bool:
        """
        Check if the LLM backend is available.
        
        Returns:
            True if the LLM can be called.
        """
        ...


class LLMUnavailableError(Exception):
    """Raised when the LLM backend cannot be reached."""
    pass


# =============================================================================
# Context Builder
# =============================================================================


@dataclass
class StrategicReviewContext:
    """
    Context prepared for strategic review.
    
    This is a TOKEN-CONTROLLED view of the plan and Canon.
    
    Attributes:
        intent_summary: Summary of the strategic intent.
        plan_summary: Summary of the proposed plan.
        validation_summary: Summary of validation results.
        dry_run_summary: Summary of dry run results.
        canon_summary: Relevant Canon context.
        constraint_summary: Relevant constraints.
        total_token_estimate: Estimated total tokens.
    """
    
    intent_summary: str
    plan_summary: str
    validation_summary: str
    dry_run_summary: str
    canon_summary: str = ""
    constraint_summary: str = ""
    total_token_estimate: int = 0
    
    def to_prompt_section(self) -> str:
        """Convert context to a prompt section."""
        sections = [
            "=== INTENT ===",
            self.intent_summary,
            "",
            "=== PROPOSED PLAN ===",
            self.plan_summary,
            "",
            "=== VALIDATION RESULT ===",
            self.validation_summary,
            "",
            "=== DRY RUN RESULT ===",
            self.dry_run_summary,
        ]
        
        if self.canon_summary:
            sections.extend([
                "",
                "=== RELEVANT CONTEXT ===",
                self.canon_summary,
            ])
        
        if self.constraint_summary:
            sections.extend([
                "",
                "=== CONSTRAINTS ===",
                self.constraint_summary,
            ])
        
        return "\n".join(sections)


class StrategicReviewContextBuilder:
    """
    Builds token-controlled context for strategic review.
    
    Uses Canon consumption contracts and enforces token limits.
    """
    
    def __init__(self, config: StrategicReviewConfig) -> None:
        """
        Initialize the context builder.
        
        Args:
            config: Review configuration.
        """
        self.config = config
    
    def build_context(
        self,
        strategic_intent: StrategicIntent,
        tactical_intent: TacticalIntent,
        planning_result: PlanningResult,
        validation_result: PlanningValidationResult,
        dry_run_result: DryRunResult,
        context: StrategicContext,
    ) -> StrategicReviewContext:
        """
        Build the review context.
        
        Args:
            strategic_intent: High-level goal.
            tactical_intent: Specific intent.
            planning_result: The proposed plan.
            validation_result: Validation outcome.
            dry_run_result: Simulation outcome.
            context: Strategic context with Canon.
            
        Returns:
            Token-controlled context for review.
        """
        # Build intent summary
        intent_summary = self._summarize_intent(strategic_intent, tactical_intent)
        
        # Build plan summary
        plan_summary = self._summarize_plan(planning_result)
        
        # Build validation summary
        validation_summary = self._summarize_validation(validation_result)
        
        # Build dry run summary
        dry_run_summary = self._summarize_dry_run(dry_run_result)
        
        # Build canon summary (token-limited)
        remaining_tokens = self.config.max_context_tokens - (
            self._estimate_tokens(intent_summary) +
            self._estimate_tokens(plan_summary) +
            self._estimate_tokens(validation_summary) +
            self._estimate_tokens(dry_run_summary)
        )
        
        canon_summary = ""
        if remaining_tokens > 500:
            canon_summary = self._summarize_canon(
                context,
                tactical_intent.scope_ids,
                max_tokens=remaining_tokens // 2,
            )
        
        # Build constraint summary
        constraint_summary = ""
        remaining_for_constraints = remaining_tokens - self._estimate_tokens(canon_summary)
        if remaining_for_constraints > 200:
            constraint_summary = self._summarize_constraints(
                context,
                max_tokens=remaining_for_constraints,
            )
        
        total_estimate = sum([
            self._estimate_tokens(intent_summary),
            self._estimate_tokens(plan_summary),
            self._estimate_tokens(validation_summary),
            self._estimate_tokens(dry_run_summary),
            self._estimate_tokens(canon_summary),
            self._estimate_tokens(constraint_summary),
        ])
        
        return StrategicReviewContext(
            intent_summary=intent_summary,
            plan_summary=plan_summary,
            validation_summary=validation_summary,
            dry_run_summary=dry_run_summary,
            canon_summary=canon_summary,
            constraint_summary=constraint_summary,
            total_token_estimate=total_estimate,
        )
    
    def _summarize_intent(
        self,
        strategic: StrategicIntent,
        tactical: TacticalIntent,
    ) -> str:
        """Summarize the intent."""
        lines = [
            f"Strategic Goal: {strategic.description}",
            f"Priority: {strategic.priority}",
            f"Success Criteria: {', '.join(strategic.success_criteria)}",
            f"",
            f"Tactical Intent: {tactical.description}",
            f"Scope: {', '.join(tactical.scope_ids) if tactical.scope_ids else 'Not specified'}",
            f"Constraints: {', '.join(tactical.constraints) if tactical.constraints else 'None'}",
        ]
        return "\n".join(lines)
    
    def _summarize_plan(self, result: PlanningResult) -> str:
        """Summarize the proposed plan."""
        if not result.graph or not result.graph.tasks:
            return "No tasks in plan"
        
        graph = result.graph
        lines = [
            f"Plan ID: {graph.id}",
            f"Total Tasks: {len(graph.tasks)}",
            "",
            "Tasks:",
        ]
        
        # Tasks is a dict, iterate over values
        task_list = list(graph.tasks.values())
        for task in task_list[:10]:  # Limit to first 10 tasks
            lines.append(f"  - {task.id}: {task.name}")
            if task.description:
                lines.append(f"    Description: {task.description[:100]}")
        
        if len(task_list) > 10:
            lines.append(f"  ... and {len(task_list) - 10} more tasks")
        
        # Add dependency summary
        if graph.dependencies:
            lines.append(f"\nDependencies: {len(graph.dependencies)} total")
        
        # Add issues from planning
        if result.issues:
            lines.append(f"\nPlanning Issues: {len(result.issues)}")
            for issue in result.issues[:5]:
                lines.append(f"  - [{issue.severity.value}] {issue.message}")
        
        return "\n".join(lines)
    
    def _summarize_validation(self, result: PlanningValidationResult) -> str:
        """Summarize validation results."""
        lines = [
            f"Valid: {result.is_valid}",
        ]
        
        if result.issues:
            lines.append(f"Issues: {len(result.issues)}")
            for issue in result.issues[:5]:
                lines.append(f"  - {issue.message}")
            if len(result.issues) > 5:
                lines.append(f"  ... and {len(result.issues) - 5} more issues")
        else:
            lines.append("No validation issues")
        
        return "\n".join(lines)
    
    def _summarize_dry_run(self, result: DryRunResult) -> str:
        """Summarize dry run results."""
        lines = [
            f"Success: {result.success}",
            f"Deadlocked: {result.deadlocked}",
            f"Execution Order: {len(result.execution_order)} tasks",
        ]
        
        if result.unreachable_tasks:
            lines.append(f"Unreachable Tasks: {', '.join(result.unreachable_tasks)}")
        
        return "\n".join(lines)
    
    def _summarize_canon(
        self,
        context: StrategicContext,
        scope_ids: List[str],
        max_tokens: int,
    ) -> str:
        """
        Summarize relevant Canon context.
        
        Uses token budget to include only relevant information.
        """
        # This would integrate with LLMConsumptionContract in a real implementation
        # For now, provide basic CPKG/BFM summary
        lines = []
        
        # CPKG summary (minimal)
        if context.cpkg.nodes:
            lines.append(f"Known Nodes: {len(context.cpkg.nodes)}")
            relevant = [
                n for nid, n in context.cpkg.nodes.items()
                if nid in scope_ids or any(s in nid for s in scope_ids)
            ][:5]
            for node in relevant:
                lines.append(f"  - {node.id}: {node.label}")
        
        # BFM summary (minimal)
        if context.bfm.nodes:
            lines.append(f"\nKnown Business Flows: {len(context.bfm.nodes)}")
        
        return "\n".join(lines) if lines else "No relevant Canon context"
    
    def _summarize_constraints(
        self,
        context: StrategicContext,
        max_tokens: int,
    ) -> str:
        """Summarize relevant constraints from UCIR."""
        if not context.ucir.constraints:
            return "No constraints defined"
        
        lines = [f"Active Constraints: {len(context.ucir.constraints)}"]
        
        for constraint in context.ucir.constraints[:5]:
            lines.append(f"  - {constraint.description}")
        
        if len(context.ucir.constraints) > 5:
            lines.append(f"  ... and {len(context.ucir.constraints) - 5} more")
        
        return "\n".join(lines)
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 chars per token)."""
        return len(text) // 4


# =============================================================================
# Prompt Builder
# =============================================================================


def build_strategic_review_prompt(context: StrategicReviewContext) -> str:
    """
    Build the prompt for strategic review.
    
    Args:
        context: The review context.
        
    Returns:
        Formatted prompt string.
    """
    lines = [
        "You are a strategic reviewer for a software engineering platform.",
        "Your role is to analyze proposed plans and identify risks, tradeoffs, and concerns.",
        "",
        "CRITICAL CONSTRAINTS:",
        "- You provide RECOMMENDATIONS, not decisions",
        "- You identify RISKS, you do NOT approve or reject",
        "- All output is ADVISORY and will be reviewed by humans",
        "- Humans have FINAL authority",
        "",
        "Your output will be labeled:",
        f'"{STRATEGIC_REVIEW_LABEL}"',
        "",
        context.to_prompt_section(),
        "",
        "=== YOUR TASK ===",
        "Analyze the proposed plan and provide:",
        "1. Risks: Potential problems with evidence",
        "2. Tradeoffs: Competing concerns and their implications",
        "3. Concerns: Questions humans should consider",
        "4. Summary: Overall assessment",
        "",
        "=== OUTPUT FORMAT ===",
        "Respond with a JSON object:",
        "{",
        '  "risks": [',
        '    {',
        '      "id": "risk-1",',
        '      "category": "safety|security|correctness|performance|architectural|constraint|scope|dependency|reversibility",',
        '      "description": "Description of the risk",',
        '      "severity": "low|medium|high",',
        '      "evidence": [{"source_type": "task|validation|dry_run|canon", "source_id": "...", "excerpt": "..."}],',
        '      "mitigation_hint": "Optional suggestion",',
        '      "confidence": "high|medium|low"',
        '    }',
        '  ],',
        '  "tradeoffs": [',
        '    {',
        '      "id": "tradeoff-1",',
        '      "description": "Description of the tradeoff",',
        '      "impacted_components": ["component-1"],',
        '      "upside": "Positive aspect",',
        '      "downside": "Negative aspect",',
        '      "confidence": "high|medium|low"',
        '    }',
        '  ],',
        '  "concerns": [',
        '    {',
        '      "id": "concern-1",',
        '      "description": "Description of the concern",',
        '      "suggested_questions": ["Question humans should consider"],',
        '      "confidence": "high|medium|low"',
        '    }',
        '  ],',
        '  "summary": {',
        '    "overall_risk_posture": "low|moderate|high|critical",',
        '    "key_recommendations": ["Recommendation 1"],',
        '    "proceed_confidence": "high|medium|low",',
        '    "requires_human_attention": true,',
        '    "attention_areas": ["Area needing attention"]',
        '  },',
        '  "confidence": "high|medium|low"',
        "}",
        "",
        "IMPORTANT:",
        "- Be EXPLICIT about uncertainty",
        "- Do NOT claim certainty you do not have",
        "- Evidence is REQUIRED for risks",
        "- Your output is ADVISORY only",
    ]
    
    return "\n".join(lines)


# =============================================================================
# Output Parser
# =============================================================================


@dataclass
class ParseResult:
    """Result of parsing LLM output."""
    success: bool
    result: Optional[LLMStrategicReviewResult] = None
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


class StrategicReviewParser:
    """
    Parser for LLM strategic review output.
    
    Converts raw LLM response to structured LLMStrategicReviewResult.
    All parsing failures result in ParseResult with error, not exceptions.
    """
    
    @staticmethod
    def parse(raw_response: str, review_id: str) -> ParseResult:
        """
        Parse raw LLM response into structured output.
        
        Args:
            raw_response: The raw string from the LLM.
            review_id: ID for the review.
            
        Returns:
            ParseResult with either result or error.
        """
        warnings: List[str] = []
        
        # Handle empty response
        if not raw_response or not raw_response.strip():
            return ParseResult(
                success=False,
                error="LLM returned empty response",
            )
        
        # Extract JSON from response
        json_str = StrategicReviewParser._extract_json(raw_response)
        if not json_str:
            return ParseResult(
                success=False,
                error="Could not extract JSON from LLM response",
            )
        
        # Parse JSON
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            return ParseResult(
                success=False,
                error=f"Invalid JSON in LLM response: {e}",
            )
        
        # Parse risks
        risks: List[StrategicRisk] = []
        for i, risk_data in enumerate(data.get("risks", [])):
            risk = StrategicReviewParser._parse_risk(risk_data, i)
            if risk:
                risks.append(risk)
            else:
                warnings.append(f"Skipped invalid risk at index {i}")
        
        # Parse tradeoffs
        tradeoffs: List[StrategicTradeoff] = []
        for i, tradeoff_data in enumerate(data.get("tradeoffs", [])):
            tradeoff = StrategicReviewParser._parse_tradeoff(tradeoff_data, i)
            if tradeoff:
                tradeoffs.append(tradeoff)
            else:
                warnings.append(f"Skipped invalid tradeoff at index {i}")
        
        # Parse concerns
        concerns: List[StrategicConcern] = []
        for i, concern_data in enumerate(data.get("concerns", [])):
            concern = StrategicReviewParser._parse_concern(concern_data, i)
            if concern:
                concerns.append(concern)
            else:
                warnings.append(f"Skipped invalid concern at index {i}")
        
        # Parse summary
        summary = StrategicReviewParser._parse_summary(data.get("summary", {}))
        
        # Parse confidence
        confidence_str = data.get("confidence", "unknown").lower()
        try:
            confidence = ConfidenceLevel(confidence_str)
        except ValueError:
            confidence = ConfidenceLevel.UNKNOWN
            warnings.append(f"Unknown confidence level: {confidence_str}")
        
        result = LLMStrategicReviewResult(
            review_id=review_id,
            advisory_label=STRATEGIC_REVIEW_LABEL,
            risks=risks,
            tradeoffs=tradeoffs,
            concerns=concerns,
            summary=summary,
            confidence=confidence,
            raw_response=raw_response,
        )
        
        # Validate result
        validation_errors = result.validate()
        if validation_errors:
            result.is_valid = False
            result.validation_errors = validation_errors
        
        return ParseResult(
            success=True,
            result=result,
            warnings=warnings,
        )
    
    @staticmethod
    def _extract_json(text: str) -> Optional[str]:
        """Extract JSON from text, handling markdown code blocks."""
        text = text.strip()
        
        # Try to find JSON in markdown code block
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end > start:
                return text[start:end].strip()
        
        if "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            if end > start:
                return text[start:end].strip()
        
        # Try to find raw JSON
        if text.startswith("{"):
            return text
        
        # Try to find JSON object in text
        start = text.find("{")
        if start >= 0:
            # Find matching closing brace
            depth = 0
            for i, char in enumerate(text[start:], start):
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth == 0:
                        return text[start:i+1]
        
        return None
    
    @staticmethod
    def _parse_risk(data: Dict[str, Any], index: int) -> Optional[StrategicRisk]:
        """Parse a risk from dictionary."""
        if not isinstance(data, dict):
            return None
        
        risk_id = data.get("id", f"risk-{index}")
        description = data.get("description", "")
        if not description:
            return None
        
        # Parse category
        category_str = data.get("category", "unknown").lower()
        try:
            category = RiskCategory(category_str)
        except ValueError:
            category = RiskCategory.UNKNOWN
        
        # Parse severity
        severity_str = data.get("severity", "medium").lower()
        try:
            severity = RiskSeverity(severity_str)
        except ValueError:
            severity = RiskSeverity.MEDIUM
        
        # Parse evidence
        evidence: List[EvidenceReference] = []
        for ev_data in data.get("evidence", []):
            if isinstance(ev_data, dict):
                evidence.append(EvidenceReference(
                    source_type=ev_data.get("source_type", "unknown"),
                    source_id=ev_data.get("source_id", ""),
                    excerpt=ev_data.get("excerpt", ""),
                ))
        
        # Parse confidence
        confidence_str = data.get("confidence", "medium").lower()
        try:
            confidence = ConfidenceLevel(confidence_str)
        except ValueError:
            confidence = ConfidenceLevel.MEDIUM
        
        return StrategicRisk(
            id=risk_id,
            category=category,
            description=description,
            severity=severity,
            evidence=evidence,
            mitigation_hint=data.get("mitigation_hint"),
            confidence=confidence,
        )
    
    @staticmethod
    def _parse_tradeoff(
        data: Dict[str, Any],
        index: int,
    ) -> Optional[StrategicTradeoff]:
        """Parse a tradeoff from dictionary."""
        if not isinstance(data, dict):
            return None
        
        tradeoff_id = data.get("id", f"tradeoff-{index}")
        description = data.get("description", "")
        if not description:
            return None
        
        # Parse confidence
        confidence_str = data.get("confidence", "medium").lower()
        try:
            confidence = ConfidenceLevel(confidence_str)
        except ValueError:
            confidence = ConfidenceLevel.MEDIUM
        
        return StrategicTradeoff(
            id=tradeoff_id,
            description=description,
            impacted_components=data.get("impacted_components", []),
            upside=data.get("upside", ""),
            downside=data.get("downside", ""),
            confidence=confidence,
        )
    
    @staticmethod
    def _parse_concern(
        data: Dict[str, Any],
        index: int,
    ) -> Optional[StrategicConcern]:
        """Parse a concern from dictionary."""
        if not isinstance(data, dict):
            return None
        
        concern_id = data.get("id", f"concern-{index}")
        description = data.get("description", "")
        if not description:
            return None
        
        # Parse confidence
        confidence_str = data.get("confidence", "medium").lower()
        try:
            confidence = ConfidenceLevel(confidence_str)
        except ValueError:
            confidence = ConfidenceLevel.MEDIUM
        
        return StrategicConcern(
            id=concern_id,
            description=description,
            suggested_questions=data.get("suggested_questions", []),
            confidence=confidence,
        )
    
    @staticmethod
    def _parse_summary(data: Dict[str, Any]) -> Optional[StrategicReviewSummary]:
        """Parse summary from dictionary."""
        if not isinstance(data, dict):
            return None
        
        # Parse risk posture
        posture_str = data.get("overall_risk_posture", "unknown").lower()
        try:
            posture = OverallRiskPosture(posture_str)
        except ValueError:
            posture = OverallRiskPosture.UNKNOWN
        
        # Parse confidence
        confidence_str = data.get("proceed_confidence", "medium").lower()
        try:
            confidence = ConfidenceLevel(confidence_str)
        except ValueError:
            confidence = ConfidenceLevel.MEDIUM
        
        return StrategicReviewSummary(
            overall_risk_posture=posture,
            key_recommendations=data.get("key_recommendations", []),
            proceed_confidence=confidence,
            requires_human_attention=data.get("requires_human_attention", True),
            attention_areas=data.get("attention_areas", []),
        )


# =============================================================================
# Mock Backend for Testing
# =============================================================================


class MockStrategicLLMBackend:
    """
    Mock LLM backend for testing.
    
    Returns configurable responses without calling a real LLM.
    """
    
    def __init__(
        self,
        available: bool = True,
        response: Optional[str] = None,
    ) -> None:
        """
        Initialize mock backend.
        
        Args:
            available: Whether the mock is available.
            response: Response to return (or None for default).
        """
        self._available = available
        self._response = response
    
    def is_available(self) -> bool:
        """Check if available."""
        return self._available
    
    def generate(self, prompt: str) -> str:
        """Generate mock response."""
        if not self._available:
            raise LLMUnavailableError("Mock backend unavailable")
        
        if self._response:
            return self._response
        
        # Return a default valid response
        return json.dumps({
            "risks": [
                {
                    "id": "risk-1",
                    "category": "correctness",
                    "description": "Plan may produce unintended side effects",
                    "severity": "medium",
                    "evidence": [
                        {
                            "source_type": "task",
                            "source_id": "task-1",
                            "excerpt": "Task modifies shared state",
                        }
                    ],
                    "confidence": "medium",
                }
            ],
            "tradeoffs": [
                {
                    "id": "tradeoff-1",
                    "description": "Speed vs thoroughness",
                    "impacted_components": ["component-1"],
                    "upside": "Faster execution",
                    "downside": "Less comprehensive coverage",
                    "confidence": "medium",
                }
            ],
            "concerns": [
                {
                    "id": "concern-1",
                    "description": "Consider impact on downstream systems",
                    "suggested_questions": [
                        "Are dependent systems prepared for this change?",
                    ],
                    "confidence": "medium",
                }
            ],
            "summary": {
                "overall_risk_posture": "moderate",
                "key_recommendations": [
                    "Review task dependencies carefully",
                    "Consider adding rollback capability",
                ],
                "proceed_confidence": "medium",
                "requires_human_attention": True,
                "attention_areas": ["Side effect management"],
            },
            "confidence": "medium",
        })


# =============================================================================
# LLM Strategic Reviewer Implementation
# =============================================================================


class LLMStrategicReviewer:
    """
    LLM-backed Strategic Reviewer.
    
    Analyzes proposed plans and provides ADVISORY recommendations.
    Does NOT have authority to approve, reject, or execute plans.
    
    All output is labeled as advisory and subject to human override.
    """
    
    def __init__(
        self,
        backend: StrategicLLMBackend,
        config: Optional[StrategicReviewConfig] = None,
    ) -> None:
        """
        Initialize the reviewer.
        
        Args:
            backend: LLM backend for generating reviews.
            config: Review configuration.
        """
        self.backend = backend
        self.config = config or StrategicReviewConfig()
        self._context_builder = StrategicReviewContextBuilder(self.config)
    
    def review_plan(
        self,
        strategic_intent: StrategicIntent,
        tactical_intent: TacticalIntent,
        planning_result: PlanningResult,
        validation_result: PlanningValidationResult,
        dry_run_result: DryRunResult,
        context: StrategicContext,
    ) -> StrategicDecision:
        """
        Review a proposed plan and produce an ADVISORY decision.
        
        This implements the StrategicReviewer protocol but the decision
        is ALWAYS advisory - human authority is final.
        
        Args:
            strategic_intent: The high-level goal.
            tactical_intent: The specific intent.
            planning_result: The proposed plan.
            validation_result: Validation outcome.
            dry_run_result: Simulation outcome.
            context: Strategic context.
            
        Returns:
            StrategicDecision with advisory recommendation.
        """
        review_id = str(uuid.uuid4())
        
        # If disabled, return empty review
        if not self.config.enabled:
            review = create_empty_review(review_id, "LLM review disabled")
            return self._convert_to_strategic_decision(review)
        
        # Check backend availability
        if not self.backend.is_available():
            review = create_empty_review(review_id, "LLM backend unavailable")
            return self._convert_to_strategic_decision(review)
        
        # Build context
        review_context = self._context_builder.build_context(
            strategic_intent=strategic_intent,
            tactical_intent=tactical_intent,
            planning_result=planning_result,
            validation_result=validation_result,
            dry_run_result=dry_run_result,
            context=context,
        )
        
        # Build prompt
        prompt = build_strategic_review_prompt(review_context)
        
        # Call LLM
        try:
            raw_response = self.backend.generate(prompt)
        except LLMUnavailableError as e:
            review = create_failed_review(review_id, str(e))
            return self._convert_to_strategic_decision(review)
        except Exception as e:
            review = create_failed_review(review_id, f"LLM call failed: {e}")
            return self._convert_to_strategic_decision(review)
        
        # Parse response
        parse_result = StrategicReviewParser.parse(raw_response, review_id)
        
        if not parse_result.success:
            review = create_failed_review(
                review_id,
                parse_result.error or "Unknown parse error",
                raw_response,
            )
            return self._convert_to_strategic_decision(review)
        
        review = parse_result.result
        if not review:
            review = create_failed_review(review_id, "No result from parser")
            return self._convert_to_strategic_decision(review)
        
        # Validate evidence requirement
        if self.config.require_evidence:
            missing_evidence = validate_risks_have_evidence(review)
            if missing_evidence:
                # Remove risks without evidence
                review.risks = [r for r in review.risks if r.id not in missing_evidence]
                review.validation_errors.extend([
                    f"Removed risk '{rid}' due to missing evidence"
                    for rid in missing_evidence
                ])
        
        return self._convert_to_strategic_decision(review)
    
    def get_review_result(
        self,
        strategic_intent: StrategicIntent,
        tactical_intent: TacticalIntent,
        planning_result: PlanningResult,
        validation_result: PlanningValidationResult,
        dry_run_result: DryRunResult,
        context: StrategicContext,
    ) -> LLMStrategicReviewResult:
        """
        Get the full review result (not just StrategicDecision).
        
        Use this when you need the detailed risks, tradeoffs, and concerns.
        
        Args:
            strategic_intent: The high-level goal.
            tactical_intent: The specific intent.
            planning_result: The proposed plan.
            validation_result: Validation outcome.
            dry_run_result: Simulation outcome.
            context: Strategic context.
            
        Returns:
            Full LLMStrategicReviewResult with all details.
        """
        review_id = str(uuid.uuid4())
        
        # If disabled, return empty review
        if not self.config.enabled:
            return create_empty_review(review_id, "LLM review disabled")
        
        # Check backend availability
        if not self.backend.is_available():
            return create_empty_review(review_id, "LLM backend unavailable")
        
        # Build context
        review_context = self._context_builder.build_context(
            strategic_intent=strategic_intent,
            tactical_intent=tactical_intent,
            planning_result=planning_result,
            validation_result=validation_result,
            dry_run_result=dry_run_result,
            context=context,
        )
        
        # Build prompt
        prompt = build_strategic_review_prompt(review_context)
        
        # Call LLM
        try:
            raw_response = self.backend.generate(prompt)
        except LLMUnavailableError as e:
            return create_failed_review(review_id, str(e))
        except Exception as e:
            return create_failed_review(review_id, f"LLM call failed: {e}")
        
        # Parse response
        parse_result = StrategicReviewParser.parse(raw_response, review_id)
        
        if not parse_result.success:
            return create_failed_review(
                review_id,
                parse_result.error or "Unknown parse error",
                raw_response,
            )
        
        review = parse_result.result
        if not review:
            return create_failed_review(review_id, "No result from parser")
        
        # Validate evidence requirement
        if self.config.require_evidence:
            missing_evidence = validate_risks_have_evidence(review)
            if missing_evidence:
                # Remove risks without evidence
                review.risks = [r for r in review.risks if r.id not in missing_evidence]
                review.validation_errors.extend([
                    f"Removed risk '{rid}' due to missing evidence"
                    for rid in missing_evidence
                ])
        
        return review
    
    def _convert_to_strategic_decision(
        self,
        review: LLMStrategicReviewResult,
    ) -> StrategicDecision:
        """
        Convert review result to StrategicDecision.
        
        Maps review findings to decision type:
        - HIGH risks or CRITICAL posture -> ESCALATE (recommend human review)
        - MEDIUM risks or MODERATE posture -> ESCALATE
        - LOW risks or LOW posture -> APPROVE (recommend proceeding)
        - Invalid review -> ESCALATE (human must decide)
        
        Note: This decision is ADVISORY only.
        """
        # Convert risks to StrategicIssues
        issues: List[StrategicIssue] = []
        
        for risk in review.risks:
            severity_map = {
                RiskSeverity.LOW: StrategicIssueSeverity.INFO,
                RiskSeverity.MEDIUM: StrategicIssueSeverity.WARNING,
                RiskSeverity.HIGH: StrategicIssueSeverity.RISK,
            }
            issues.append(StrategicIssue(
                type=risk.category.value,
                message=f"{STRATEGIC_REVIEW_LABEL} {risk.description}",
                severity=severity_map.get(risk.severity, StrategicIssueSeverity.INFO),
                context={
                    "evidence": [e.to_dict() for e in risk.evidence],
                    "confidence": risk.confidence.value,
                }
            ))
        
        for concern in review.concerns:
            issues.append(StrategicIssue(
                type="concern",
                message=f"{STRATEGIC_REVIEW_LABEL} {concern.description}",
                severity=StrategicIssueSeverity.INFO,
                context={
                    "questions": concern.suggested_questions,
                    "confidence": concern.confidence.value,
                }
            ))
        
        # Determine recommendation
        if not review.is_valid or review.confidence == ConfidenceLevel.UNKNOWN:
            # Cannot assess - escalate to human
            return StrategicDecision(
                decision=StrategicDecisionType.ESCALATE,
                reason=f"{STRATEGIC_REVIEW_LABEL} AI review incomplete - human judgment required",
                issues=issues,
            )
        
        if review.has_high_severity_risks():
            return StrategicDecision(
                decision=StrategicDecisionType.ESCALATE,
                reason=f"{STRATEGIC_REVIEW_LABEL} High-severity risks identified - human review recommended",
                issues=issues,
            )
        
        if review.summary:
            if review.summary.overall_risk_posture in [
                OverallRiskPosture.HIGH,
                OverallRiskPosture.CRITICAL,
            ]:
                return StrategicDecision(
                    decision=StrategicDecisionType.ESCALATE,
                    reason=f"{STRATEGIC_REVIEW_LABEL} Elevated risk posture - human review recommended",
                    issues=issues,
                )
            
            if review.summary.overall_risk_posture == OverallRiskPosture.MODERATE:
                return StrategicDecision(
                    decision=StrategicDecisionType.ESCALATE,
                    reason=f"{STRATEGIC_REVIEW_LABEL} Moderate risks identified - human review recommended",
                    issues=issues,
                )
        
        # Low risk - recommend proceeding (but human still decides)
        return StrategicDecision(
            decision=StrategicDecisionType.APPROVE,
            reason=f"{STRATEGIC_REVIEW_LABEL} Low risk assessment - proceeding appears safe",
            issues=issues,
        )


# =============================================================================
# Validation Functions
# =============================================================================


def validate_reviewer_is_advisory(decision: StrategicDecision) -> bool:
    """
    Validate that a decision from LLMStrategicReviewer is properly labeled.
    
    Args:
        decision: The decision to validate.
        
    Returns:
        True if properly labeled as advisory.
    """
    return STRATEGIC_REVIEW_LABEL in decision.reason


def validate_reviewer_has_no_authority(reviewer: LLMStrategicReviewer) -> bool:
    """
    Validate that the reviewer has no execution authority.
    
    This is always True by design - the reviewer cannot execute.
    
    Args:
        reviewer: The reviewer to validate.
        
    Returns:
        True (reviewer has no execution capability).
    """
    # By design, LLMStrategicReviewer has no execute method
    return not hasattr(reviewer, "execute") and not hasattr(reviewer, "approve")
