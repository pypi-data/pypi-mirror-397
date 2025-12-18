"""
LLM Enrichment Runner.

This module implements the LLM-assisted enrichment stage for Canon population.
It provides advisory labeling and compression WITHOUT introducing inference,
authority, or non-determinism.

CORE PRINCIPLE (NON-NEGOTIABLE):
- LLMs may: Label, Compress, Explain, Highlight explicit facts
- LLMs may NOT: Invent facts, Infer behavior, Add dependencies, Modify structure

This phase assists humans. It does not replace them.

Canon truth remains grounded in deterministic extraction + human approval.
"""

import hashlib
import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Protocol

from axiom_canon.ingestion.models import (
    ComponentSummary,
    IngestionResult,
    ModuleSummary,
)
from axiom_canon.ingestion.enrichment_models import (
    EnrichedComponentLabel,
    EnrichedInvariant,
    EnrichmentConfidence,
    EnrichmentIssue,
    EnrichmentIssueType,
    EnrichmentResult,
    InvariantClassification,
    LLM_ENRICHMENT_LABEL,
    MAX_DESCRIPTION_CHARS,
    MAX_INVARIANT_TEXT_CHARS,
    MAX_LABEL_CHARS,
    ReviewDecision,
)


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class EnrichmentConfig:
    """
    Configuration for LLM enrichment.
    
    Attributes:
        max_input_tokens_per_call: Maximum input tokens per LLM call.
        max_output_tokens_per_call: Maximum output tokens per LLM call.
        max_total_input_tokens: Maximum total input tokens for entire run.
        max_components_per_call: Maximum components to process per call.
        min_confidence_to_include: Minimum confidence to include in results.
        skip_low_confidence: Whether to skip LOW confidence enrichments.
        enabled: Whether enrichment is enabled.
        model_name: LLM model to use.
    """
    
    max_input_tokens_per_call: int = 2000
    max_output_tokens_per_call: int = 1000
    max_total_input_tokens: int = 20000
    max_components_per_call: int = 5
    min_confidence_to_include: EnrichmentConfidence = EnrichmentConfidence.LOW
    skip_low_confidence: bool = False
    enabled: bool = True
    model_name: str = "default"


# =============================================================================
# LLM Backend Protocol
# =============================================================================


class EnrichmentLLMBackend(Protocol):
    """
    Protocol for LLM backend used in enrichment.
    
    The backend is responsible for:
    - Making LLM API calls
    - Returning structured JSON responses
    - Tracking token usage
    """
    
    def complete(
        self,
        prompt: str,
        system_prompt: str,
        max_output_tokens: int,
    ) -> tuple[str, int, int]:
        """
        Complete a prompt.
        
        Args:
            prompt: User prompt.
            system_prompt: System prompt.
            max_output_tokens: Maximum output tokens.
            
        Returns:
            Tuple of (response_text, input_tokens, output_tokens).
            
        Raises:
            Exception: If LLM is unavailable.
        """
        ...
    
    def is_available(self) -> bool:
        """Check if backend is available."""
        ...
    
    def model_name(self) -> str:
        """Get model name."""
        ...


# =============================================================================
# Mock Backend for Testing
# =============================================================================


class MockEnrichmentBackend:
    """
    Mock LLM backend for testing.
    
    Returns predetermined responses or generates simple ones.
    """
    
    def __init__(
        self,
        responses: Optional[List[str]] = None,
        available: bool = True,
        model: str = "mock-enrichment-model",
    ) -> None:
        """
        Initialize mock backend.
        
        Args:
            responses: Predetermined responses (cycled through).
            available: Whether backend is available.
            model: Model name to report.
        """
        self._responses = responses or []
        self._response_index = 0
        self._available = available
        self._model = model
        self.call_count = 0
        self.prompts: List[str] = []
    
    def complete(
        self,
        prompt: str,
        system_prompt: str,
        max_output_tokens: int,
    ) -> tuple[str, int, int]:
        """Complete using mock response."""
        if not self._available:
            raise RuntimeError("LLM backend unavailable")
        
        self.call_count += 1
        self.prompts.append(prompt)
        
        if self._responses:
            response = self._responses[self._response_index % len(self._responses)]
            self._response_index += 1
        else:
            response = self._generate_default_response(prompt)
        
        # Estimate tokens (rough)
        input_tokens = len(prompt) // 4
        output_tokens = len(response) // 4
        
        return response, input_tokens, output_tokens
    
    def is_available(self) -> bool:
        """Check availability."""
        return self._available
    
    def model_name(self) -> str:
        """Get model name."""
        return self._model
    
    def _generate_default_response(self, prompt: str) -> str:
        """Generate a default mock response."""
        if "component" in prompt.lower():
            return json.dumps({
                "labels": [
                    {
                        "component_id": "mock_component",
                        "responsibility_label": "Mock Component",
                        "description": "A mock component for testing.",
                        "confidence": "medium",
                        "assumptions": [],
                    }
                ]
            })
        elif "invariant" in prompt.lower():
            return json.dumps({
                "invariants": [
                    {
                        "invariant_text": "This is a mock invariant.",
                        "source_type": "docstring",
                        "source_quote": "Mock quote from docstring.",
                        "classification": "explicit",
                        "confidence": "high",
                    }
                ]
            })
        return json.dumps({"result": "mock"})


# =============================================================================
# Token Estimation
# =============================================================================


def _estimate_tokens(text: str) -> int:
    """
    Estimate token count for text.
    
    Uses simple heuristic (~1 token per 4 characters).
    
    Args:
        text: Text to estimate.
        
    Returns:
        Estimated token count.
    """
    return len(text) // 4


def _truncate_to_tokens(text: str, max_tokens: int) -> str:
    """
    Truncate text to fit within token limit.
    
    Args:
        text: Text to truncate.
        max_tokens: Maximum tokens.
        
    Returns:
        Truncated text.
    """
    max_chars = max_tokens * 4
    if len(text) <= max_chars:
        return text
    return text[:max_chars - 3] + "..."


# =============================================================================
# Prompt Builders
# =============================================================================


COMPONENT_LABELING_SYSTEM_PROMPT = '''You are a code documentation assistant. Your role is to provide ADVISORY labels for software components.

STRICT RULES:
1. Only use information provided in the input
2. Do NOT invent or infer functionality
3. Do NOT add dependencies or relationships
4. Express uncertainty explicitly
5. Keep labels short (max 50 chars) and descriptions brief (max 200 chars)
6. Output MUST be valid JSON

Confidence levels:
- HIGH: Clear from module names and exports
- MEDIUM: Reasonable guess from context
- LOW: Uncertain, needs human verification

If unsure, say "LOW" confidence and explain assumptions.'''


INVARIANT_EXTRACTION_SYSTEM_PROMPT = '''You are a code documentation assistant. Your role is to extract EXPLICIT invariants from docstrings and comments.

STRICT RULES:
1. Only extract invariants that are EXPLICITLY STATED
2. Do NOT infer invariants from code logic
3. Look for markers like: @invariant, NOTE:, WARNING:, CONSTRAINT:, MUST, MUST NOT
4. Always include the source quote
5. If uncertain whether something is an invariant, mark as UNCERTAIN
6. Output MUST be valid JSON

Source types: docstring, comment, marker, readme

Classification:
- EXPLICIT: Clearly stated as a rule/constraint
- UNCERTAIN: May be an invariant, needs verification'''


def _build_component_labeling_prompt(
    components: List[ComponentSummary],
    config: EnrichmentConfig,
) -> str:
    """
    Build prompt for component labeling.
    
    Args:
        components: Components to label.
        config: Enrichment configuration.
        
    Returns:
        Prompt string.
    """
    lines = [
        "Analyze the following software components and provide responsibility labels.",
        "",
        "For each component, provide:",
        "- component_id: The ID from input",
        "- responsibility_label: Short label (max 50 chars)",
        "- description: Brief description (max 200 chars)",
        "- confidence: HIGH, MEDIUM, or LOW",
        "- assumptions: List of assumptions made (if any)",
        "",
        "Output format (JSON):",
        '{"labels": [{"component_id": "...", "responsibility_label": "...", ...}]}',
        "",
        "COMPONENTS:",
        "",
    ]
    
    for comp in components:
        lines.append(f"Component ID: {comp.id}")
        lines.append(f"  Path: {comp.path}")
        lines.append(f"  Name: {comp.name}")
        
        # List modules (truncated)
        module_names = [m.name for m in comp.modules[:10]]
        if module_names:
            lines.append(f"  Modules: {', '.join(module_names)}")
            if len(comp.modules) > 10:
                lines.append(f"    ... and {len(comp.modules) - 10} more")
        
        # List entry points
        if comp.entry_points:
            ep_names = [e.name for e in comp.entry_points[:5]]
            lines.append(f"  Entry Points: {', '.join(ep_names)}")
        
        lines.append("")
    
    prompt = "\n".join(lines)
    
    # Truncate if too long
    return _truncate_to_tokens(prompt, config.max_input_tokens_per_call)


def _build_invariant_extraction_prompt(
    modules: List[ModuleSummary],
    config: EnrichmentConfig,
) -> str:
    """
    Build prompt for invariant extraction.
    
    Note: We only pass structural info, not raw source code.
    This limits what invariants can be extracted to what's in docstrings.
    
    Args:
        modules: Modules to scan for invariants.
        config: Enrichment configuration.
        
    Returns:
        Prompt string.
    """
    lines = [
        "Analyze the following module summaries and extract EXPLICIT invariants.",
        "",
        "Look for invariants in:",
        "- Module docstrings (captured in human_notes if present)",
        "- Class/function names suggesting constraints",
        "- Export lists suggesting public API contracts",
        "",
        "For each invariant found, provide:",
        "- invariant_text: The invariant statement",
        "- source_file: File path",
        "- source_type: docstring, comment, or marker",
        "- source_quote: Exact quote (if available)",
        "- classification: EXPLICIT or UNCERTAIN",
        "- confidence: HIGH, MEDIUM, or LOW",
        "",
        "Output format (JSON):",
        '{"invariants": [{"invariant_text": "...", ...}]}',
        "",
        "MODULES:",
        "",
    ]
    
    for module in modules:
        lines.append(f"Module: {module.name}")
        lines.append(f"  Path: {module.path}")
        lines.append(f"  Type: {module.module_type.value}")
        
        # Exports suggest API contracts
        if module.exports:
            export_names = [e.name for e in module.exports[:10]]
            lines.append(f"  Exports: {', '.join(export_names)}")
        
        # Human notes may contain docstrings
        if module.human_notes:
            lines.append(f"  Notes: {module.human_notes[:200]}")
        
        # Class names with patterns
        for cls in module.classes[:5]:
            if any(p in cls.name for p in ["Protocol", "Interface", "Abstract", "Base"]):
                lines.append(f"  Interface: {cls.name}")
        
        lines.append("")
    
    prompt = "\n".join(lines)
    
    return _truncate_to_tokens(prompt, config.max_input_tokens_per_call)


# =============================================================================
# Response Parsing
# =============================================================================


def _extract_json_from_response(response: str) -> Dict[str, Any]:
    """
    Extract JSON from LLM response.
    
    Handles markdown code blocks and plain JSON.
    
    Args:
        response: Raw LLM response.
        
    Returns:
        Parsed JSON dictionary.
        
    Raises:
        ValueError: If no valid JSON found.
    """
    # Try to find JSON in markdown code blocks
    json_patterns = [
        r"```json\s*([\s\S]*?)\s*```",
        r"```\s*([\s\S]*?)\s*```",
        r"\{[\s\S]*\}",
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, response)
        for match in matches:
            text = match if isinstance(match, str) else match
            try:
                # Clean up the text
                text = text.strip()
                if text.startswith("{") or text.startswith("["):
                    return json.loads(text)
            except json.JSONDecodeError:
                continue
    
    # Last resort: try the whole response
    try:
        return json.loads(response.strip())
    except json.JSONDecodeError as e:
        raise ValueError(f"No valid JSON found in response: {e}")


def _parse_component_labels(
    response_json: Dict[str, Any],
    components: List[ComponentSummary],
    known_ids: set,
) -> tuple[List[EnrichedComponentLabel], List[EnrichmentIssue]]:
    """
    Parse component labels from LLM response.
    
    Args:
        response_json: Parsed JSON response.
        components: Original components for reference.
        known_ids: Set of known component IDs.
        
    Returns:
        Tuple of (labels, issues).
    """
    labels = []
    issues = []
    
    component_map = {c.id: c for c in components}
    
    raw_labels = response_json.get("labels", [])
    
    for raw in raw_labels:
        component_id = raw.get("component_id", "")
        
        # Check for unknown artifact
        if component_id not in known_ids:
            issues.append(
                EnrichmentIssue(
                    issue_type=EnrichmentIssueType.UNKNOWN_ARTIFACT,
                    message=f"Unknown component ID: {component_id}",
                    artifact_id=component_id,
                )
            )
            continue
        
        # Get component path
        comp = component_map.get(component_id)
        component_path = comp.path if comp else ""
        
        # Parse confidence
        conf_str = raw.get("confidence", "unknown").lower()
        try:
            confidence = EnrichmentConfidence(conf_str)
        except ValueError:
            confidence = EnrichmentConfidence.UNKNOWN
        
        # Create label
        label = EnrichedComponentLabel(
            component_id=component_id,
            component_path=component_path,
            responsibility_label=raw.get("responsibility_label", "")[:MAX_LABEL_CHARS],
            description=raw.get("description", "")[:MAX_DESCRIPTION_CHARS],
            confidence=confidence,
            assumptions=raw.get("assumptions", []),
            source_context=[c.name for c in components if c.id == component_id],
        )
        
        # Validate
        validation_issues = label.validate()
        if validation_issues:
            issues.extend(validation_issues)
        else:
            labels.append(label)
    
    return labels, issues


def _parse_invariants(
    response_json: Dict[str, Any],
    modules: List[ModuleSummary],
    known_paths: set,
) -> tuple[List[EnrichedInvariant], List[EnrichmentIssue]]:
    """
    Parse invariants from LLM response.
    
    Args:
        response_json: Parsed JSON response.
        modules: Original modules for reference.
        known_paths: Set of known module paths.
        
    Returns:
        Tuple of (invariants, issues).
    """
    invariants = []
    issues = []
    
    raw_invariants = response_json.get("invariants", [])
    
    for i, raw in enumerate(raw_invariants):
        source_file = raw.get("source_file", "")
        
        # Validate source file if provided
        if source_file and source_file not in known_paths:
            # Try to find a matching module
            matched = False
            for path in known_paths:
                if source_file in path or path in source_file:
                    source_file = path
                    matched = True
                    break
            
            if not matched:
                issues.append(
                    EnrichmentIssue(
                        issue_type=EnrichmentIssueType.UNKNOWN_ARTIFACT,
                        message=f"Unknown source file: {source_file}",
                        details={"raw_source": raw.get("source_file", "")},
                    )
                )
                continue
        
        # Parse classification
        class_str = raw.get("classification", "uncertain").lower()
        try:
            classification = InvariantClassification(class_str)
        except ValueError:
            classification = InvariantClassification.UNCERTAIN
        
        # Parse confidence
        conf_str = raw.get("confidence", "unknown").lower()
        try:
            confidence = EnrichmentConfidence(conf_str)
        except ValueError:
            confidence = EnrichmentConfidence.UNKNOWN
        
        # Generate ID
        invariant_text = raw.get("invariant_text", "")[:MAX_INVARIANT_TEXT_CHARS]
        invariant_id = f"inv_{hashlib.sha256(invariant_text.encode()).hexdigest()[:12]}"
        
        # Create invariant
        inv = EnrichedInvariant(
            invariant_id=invariant_id,
            invariant_text=invariant_text,
            source_file=source_file,
            source_line=raw.get("source_line"),
            source_type=raw.get("source_type", "docstring"),
            source_quote=raw.get("source_quote", "")[:500],
            classification=classification,
            confidence=confidence,
        )
        
        # Validate
        validation_issues = inv.validate()
        if validation_issues:
            issues.extend(validation_issues)
        else:
            invariants.append(inv)
    
    return invariants, issues


# =============================================================================
# LLM Enrichment Runner
# =============================================================================


class LLMEnrichmentRunner:
    """
    Main runner for LLM-assisted enrichment.
    
    Takes deterministic ingestion output and produces advisory enrichments.
    NOTHING is written to Canon until human-approved.
    
    CORE CONSTRAINTS:
    - LLMs never see raw source code
    - Enrichments are advisory only
    - All outputs clearly marked as LLM-generated
    - Validation rejects structure modifications
    - Graceful degradation on failure
    """
    
    def __init__(
        self,
        backend: EnrichmentLLMBackend,
        config: Optional[EnrichmentConfig] = None,
    ) -> None:
        """
        Initialize enrichment runner.
        
        Args:
            backend: LLM backend to use.
            config: Enrichment configuration.
        """
        self._backend = backend
        self._config = config or EnrichmentConfig()
        self._total_input_tokens = 0
        self._total_output_tokens = 0
        self._call_count = 0
    
    def enrich(
        self,
        ingestion_result: IngestionResult,
    ) -> EnrichmentResult:
        """
        Run enrichment on ingestion result.
        
        Args:
            ingestion_result: Deterministic ingestion output.
            
        Returns:
            EnrichmentResult with advisory enrichments awaiting review.
        """
        # Initialize result
        result = EnrichmentResult(
            ingestion_version_hash=ingestion_result.version_hash,
            llm_model=self._backend.model_name() if self._backend.is_available() else "",
        )
        
        # Check if enrichment is enabled
        if not self._config.enabled:
            result.issues.append(
                EnrichmentIssue(
                    issue_type=EnrichmentIssueType.LLM_UNAVAILABLE,
                    message="Enrichment is disabled by configuration",
                )
            )
            return result
        
        # Check backend availability
        if not self._backend.is_available():
            result.issues.append(
                EnrichmentIssue(
                    issue_type=EnrichmentIssueType.LLM_UNAVAILABLE,
                    message="LLM backend is unavailable",
                )
            )
            return result
        
        # Reset counters
        self._total_input_tokens = 0
        self._total_output_tokens = 0
        self._call_count = 0
        
        # Build known artifact sets for validation
        known_component_ids = {c.id for c in ingestion_result.components}
        known_module_paths = {m.path for m in ingestion_result.modules}
        
        # Role A: Component Labeling
        try:
            labels, label_issues = self._enrich_components(
                ingestion_result.components,
                known_component_ids,
            )
            result.component_labels.extend(labels)
            result.issues.extend(label_issues)
        except Exception as e:
            result.issues.append(
                EnrichmentIssue(
                    issue_type=EnrichmentIssueType.LLM_UNAVAILABLE,
                    message=f"Component labeling failed: {e}",
                )
            )
        
        # Role B: Invariant Extraction
        try:
            invariants, inv_issues = self._enrich_invariants(
                ingestion_result.modules,
                known_module_paths,
            )
            result.invariants.extend(invariants)
            result.issues.extend(inv_issues)
        except Exception as e:
            result.issues.append(
                EnrichmentIssue(
                    issue_type=EnrichmentIssueType.LLM_UNAVAILABLE,
                    message=f"Invariant extraction failed: {e}",
                )
            )
        
        # Update stats
        result.total_llm_calls = self._call_count
        result.total_input_tokens = self._total_input_tokens
        result.total_output_tokens = self._total_output_tokens
        result.timestamp = datetime.now(timezone.utc).isoformat()
        
        # Filter by confidence if configured
        if self._config.skip_low_confidence:
            result.component_labels = [
                l for l in result.component_labels
                if l.confidence != EnrichmentConfidence.LOW
            ]
            result.invariants = [
                i for i in result.invariants
                if i.confidence != EnrichmentConfidence.LOW
            ]
        
        return result
    
    def _enrich_components(
        self,
        components: List[ComponentSummary],
        known_ids: set,
    ) -> tuple[List[EnrichedComponentLabel], List[EnrichmentIssue]]:
        """
        Enrich components with responsibility labels.
        
        Args:
            components: Components to label.
            known_ids: Set of known component IDs.
            
        Returns:
            Tuple of (labels, issues).
        """
        all_labels = []
        all_issues = []
        
        # Process in batches
        batch_size = self._config.max_components_per_call
        
        for i in range(0, len(components), batch_size):
            # Check token budget
            if self._total_input_tokens >= self._config.max_total_input_tokens:
                all_issues.append(
                    EnrichmentIssue(
                        issue_type=EnrichmentIssueType.TOKEN_LIMIT_EXCEEDED,
                        message="Total input token budget exceeded",
                        details={
                            "used": self._total_input_tokens,
                            "limit": self._config.max_total_input_tokens,
                        },
                    )
                )
                break
            
            batch = components[i:i + batch_size]
            
            # Build prompt
            prompt = _build_component_labeling_prompt(batch, self._config)
            
            # Call LLM
            try:
                response, input_tokens, output_tokens = self._backend.complete(
                    prompt=prompt,
                    system_prompt=COMPONENT_LABELING_SYSTEM_PROMPT,
                    max_output_tokens=self._config.max_output_tokens_per_call,
                )
                
                self._total_input_tokens += input_tokens
                self._total_output_tokens += output_tokens
                self._call_count += 1
                
            except Exception as e:
                all_issues.append(
                    EnrichmentIssue(
                        issue_type=EnrichmentIssueType.LLM_UNAVAILABLE,
                        message=f"LLM call failed: {e}",
                    )
                )
                continue
            
            # Parse response
            try:
                response_json = _extract_json_from_response(response)
            except ValueError as e:
                all_issues.append(
                    EnrichmentIssue(
                        issue_type=EnrichmentIssueType.PARSE_ERROR,
                        message=str(e),
                        details={"response_preview": response[:200]},
                    )
                )
                continue
            
            # Parse labels
            labels, issues = _parse_component_labels(response_json, batch, known_ids)
            all_labels.extend(labels)
            all_issues.extend(issues)
        
        return all_labels, all_issues
    
    def _enrich_invariants(
        self,
        modules: List[ModuleSummary],
        known_paths: set,
    ) -> tuple[List[EnrichedInvariant], List[EnrichmentIssue]]:
        """
        Extract explicit invariants from modules.
        
        Args:
            modules: Modules to scan.
            known_paths: Set of known module paths.
            
        Returns:
            Tuple of (invariants, issues).
        """
        all_invariants = []
        all_issues = []
        
        # Check token budget
        if self._total_input_tokens >= self._config.max_total_input_tokens:
            all_issues.append(
                EnrichmentIssue(
                    issue_type=EnrichmentIssueType.TOKEN_LIMIT_EXCEEDED,
                    message="Token budget exhausted before invariant extraction",
                )
            )
            return all_invariants, all_issues
        
        # Build prompt
        prompt = _build_invariant_extraction_prompt(modules, self._config)
        
        # Call LLM
        try:
            response, input_tokens, output_tokens = self._backend.complete(
                prompt=prompt,
                system_prompt=INVARIANT_EXTRACTION_SYSTEM_PROMPT,
                max_output_tokens=self._config.max_output_tokens_per_call,
            )
            
            self._total_input_tokens += input_tokens
            self._total_output_tokens += output_tokens
            self._call_count += 1
            
        except Exception as e:
            all_issues.append(
                EnrichmentIssue(
                    issue_type=EnrichmentIssueType.LLM_UNAVAILABLE,
                    message=f"LLM call failed: {e}",
                )
            )
            return all_invariants, all_issues
        
        # Parse response
        try:
            response_json = _extract_json_from_response(response)
        except ValueError as e:
            all_issues.append(
                EnrichmentIssue(
                    issue_type=EnrichmentIssueType.PARSE_ERROR,
                    message=str(e),
                    details={"response_preview": response[:200]},
                )
            )
            return all_invariants, all_issues
        
        # Parse invariants
        invariants, issues = _parse_invariants(response_json, modules, known_paths)
        all_invariants.extend(invariants)
        all_issues.extend(issues)
        
        return all_invariants, all_issues


# =============================================================================
# Validation Functions
# =============================================================================


def validate_enrichment_does_not_modify_structure(
    ingestion_result: IngestionResult,
    enrichment_result: EnrichmentResult,
) -> List[EnrichmentIssue]:
    """
    Validate that enrichment does not modify structure.
    
    CRITICAL: Enrichments must NOT:
    - Add or remove modules
    - Add or remove components
    - Add dependencies
    - Modify exports
    
    Args:
        ingestion_result: Original ingestion result.
        enrichment_result: Enrichment to validate.
        
    Returns:
        List of issues if structure was modified.
    """
    issues = []
    
    # Get known IDs
    known_component_ids = {c.id for c in ingestion_result.components}
    known_module_paths = {m.path for m in ingestion_result.modules}
    
    # Check component labels reference only known components
    for label in enrichment_result.component_labels:
        if label.component_id not in known_component_ids:
            issues.append(
                EnrichmentIssue(
                    issue_type=EnrichmentIssueType.STRUCTURE_MODIFIED,
                    message=f"Label references unknown component: {label.component_id}",
                    artifact_id=label.component_id,
                )
            )
    
    # Check invariants reference only known files
    for inv in enrichment_result.invariants:
        if inv.source_file and inv.source_file not in known_module_paths:
            # Allow partial matches
            matched = any(
                inv.source_file in p or p in inv.source_file
                for p in known_module_paths
            )
            if not matched:
                issues.append(
                    EnrichmentIssue(
                        issue_type=EnrichmentIssueType.STRUCTURE_MODIFIED,
                        message=f"Invariant references unknown file: {inv.source_file}",
                        artifact_id=inv.invariant_id,
                    )
                )
    
    return issues


def reject_over_confident_claims(
    enrichment_result: EnrichmentResult,
) -> List[EnrichmentIssue]:
    """
    Reject enrichments that claim HIGH confidence without evidence.
    
    HIGH confidence should only be used when:
    - Label clearly derived from module names
    - Invariant has explicit source quote
    
    Args:
        enrichment_result: Enrichment to validate.
        
    Returns:
        List of rejection issues.
    """
    issues = []
    
    for label in enrichment_result.component_labels:
        if label.confidence == EnrichmentConfidence.HIGH:
            # HIGH confidence should have source context
            if not label.source_context:
                issues.append(
                    EnrichmentIssue(
                        issue_type=EnrichmentIssueType.VALIDATION_ERROR,
                        message="HIGH confidence label without source context",
                        artifact_id=label.component_id,
                    )
                )
    
    for inv in enrichment_result.invariants:
        if inv.classification == InvariantClassification.EXPLICIT:
            # EXPLICIT invariant must have source quote
            if not inv.source_quote:
                issues.append(
                    EnrichmentIssue(
                        issue_type=EnrichmentIssueType.VALIDATION_ERROR,
                        message="EXPLICIT invariant without source quote",
                        artifact_id=inv.invariant_id,
                    )
                )
    
    return issues


# =============================================================================
# Human Review Application
# =============================================================================


def apply_review_decision(
    enrichment_result: EnrichmentResult,
    item_id: str,
    decision: ReviewDecision,
    notes: Optional[str] = None,
    edited_value: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Apply a human review decision to an enrichment item.
    
    Args:
        enrichment_result: Enrichment result to update.
        item_id: ID of item being reviewed.
        decision: Review decision.
        notes: Optional reviewer notes.
        edited_value: Optional edited values (for EDITED decision).
        
    Returns:
        True if decision was applied, False if item not found.
    """
    # Check component labels
    for label in enrichment_result.component_labels:
        if label.component_id == item_id:
            label.review_decision = decision
            label.reviewer_notes = notes
            
            if decision == ReviewDecision.EDITED and edited_value:
                if "responsibility_label" in edited_value:
                    label.responsibility_label = edited_value["responsibility_label"]
                if "description" in edited_value:
                    label.description = edited_value["description"]
            
            return True
    
    # Check invariants
    for inv in enrichment_result.invariants:
        if inv.invariant_id == item_id:
            inv.review_decision = decision
            inv.reviewer_notes = notes
            
            if decision == ReviewDecision.EDITED and edited_value:
                if "invariant_text" in edited_value:
                    inv.invariant_text = edited_value["invariant_text"]
                if "classification" in edited_value:
                    inv.classification = InvariantClassification(
                        edited_value["classification"]
                    )
            
            return True
    
    return False


def get_approved_enrichments(
    enrichment_result: EnrichmentResult,
) -> tuple[List[EnrichedComponentLabel], List[EnrichedInvariant]]:
    """
    Get only approved enrichments.
    
    Only returns enrichments with APPROVED or EDITED status.
    
    Args:
        enrichment_result: Enrichment result to filter.
        
    Returns:
        Tuple of (approved_labels, approved_invariants).
    """
    approved_labels = [
        label for label in enrichment_result.component_labels
        if label.review_decision in (ReviewDecision.APPROVED, ReviewDecision.EDITED)
    ]
    
    approved_invariants = [
        inv for inv in enrichment_result.invariants
        if inv.review_decision in (ReviewDecision.APPROVED, ReviewDecision.EDITED)
    ]
    
    return approved_labels, approved_invariants
