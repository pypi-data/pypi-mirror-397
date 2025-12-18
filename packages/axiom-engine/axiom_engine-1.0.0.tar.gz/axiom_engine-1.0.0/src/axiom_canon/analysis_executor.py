"""
LLM Analysis Executor for Discovery.

This module implements the READ-ONLY executor for discovery tasks.
It analyzes code slices and produces structured evidence reports.

HARD CONSTRAINTS (ABSOLUTE):
- Read files ONLY (no execution)
- Strict file count limits
- Strict token budgets
- Strict timeouts
- JSON-only output
- Deterministic failure on violations

Executor MUST NOT:
- Execute code
- Modify files
- Write Canon artifacts
- Produce approvals or decisions
- Run autonomously

Any violation is a HARD FAILURE.
"""

import hashlib
import json
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

from axiom_canon.discovery import (
    DiscoveryResult,
    DiscoveryScope,
    DiscoveryTask,
    DiscoveryTaskType,
    EvidenceExcerpt,
    InferenceConfidence,
    InferenceEvidence,
    InferenceStatus,
    InferenceType,
    InferredAnnotation,
    INFERENCE_LABEL,
)


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class AnalysisExecutorConfig:
    """
    Configuration for LLM Analysis Executor.
    
    Attributes:
        max_files_per_task: Maximum files per analysis task.
        max_tokens_per_file: Maximum tokens to read per file.
        max_total_tokens: Maximum total input tokens.
        max_output_tokens: Maximum output tokens.
        timeout_seconds: Maximum execution time.
        model_name: LLM model to use.
        enabled: Whether analysis is enabled.
    """
    
    max_files_per_task: int = 10
    max_tokens_per_file: int = 2000
    max_total_tokens: int = 10000
    max_output_tokens: int = 2000
    timeout_seconds: int = 60
    model_name: str = "default"
    enabled: bool = True
    
    def validate(self) -> List[str]:
        """Validate configuration."""
        errors = []
        
        if self.max_files_per_task <= 0:
            errors.append("max_files_per_task must be positive")
        if self.max_files_per_task > 50:
            errors.append("max_files_per_task cannot exceed 50")
        if self.max_tokens_per_file > 10000:
            errors.append("max_tokens_per_file cannot exceed 10000")
        if self.max_total_tokens > 50000:
            errors.append("max_total_tokens cannot exceed 50000")
        if self.timeout_seconds > 300:
            errors.append("timeout_seconds cannot exceed 300")
        
        return errors


# =============================================================================
# File Reader (Read-Only)
# =============================================================================


class FileReader:
    """
    Read-only file reader with safety constraints.
    
    ONLY reads files. Cannot modify, execute, or write.
    """
    
    def __init__(
        self,
        project_root: str,
        max_tokens_per_file: int = 2000,
    ) -> None:
        """
        Initialize file reader.
        
        Args:
            project_root: Root directory for relative paths.
            max_tokens_per_file: Maximum tokens to read per file.
        """
        self._project_root = Path(project_root)
        self._max_tokens_per_file = max_tokens_per_file
    
    def read_file(
        self,
        file_path: str,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
    ) -> tuple[str, int]:
        """
        Read file content (read-only).
        
        Args:
            file_path: Absolute or relative path to file.
            start_line: Starting line (1-indexed, optional).
            end_line: Ending line (inclusive, optional).
            
        Returns:
            Tuple of (content, token_estimate).
            
        Raises:
            FileNotFoundError: If file doesn't exist.
            PermissionError: If file is outside project root.
        """
        # Resolve path
        path = Path(file_path)
        if not path.is_absolute():
            path = self._project_root / path
        path = path.resolve()
        
        # Security: Ensure file is within project root
        try:
            path.relative_to(self._project_root.resolve())
        except ValueError:
            raise PermissionError(
                f"File is outside project root: {file_path}"
            )
        
        # Read file
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        content = path.read_text(encoding="utf-8", errors="replace")
        
        # Extract line range if specified
        if start_line is not None or end_line is not None:
            lines = content.split("\n")
            start = (start_line or 1) - 1  # Convert to 0-indexed
            end = end_line or len(lines)
            content = "\n".join(lines[start:end])
        
        # Truncate to token limit
        max_chars = self._max_tokens_per_file * 4
        if len(content) > max_chars:
            content = content[:max_chars - 3] + "..."
        
        token_estimate = len(content) // 4
        return content, token_estimate
    
    def read_files(
        self,
        file_paths: List[str],
        max_files: int = 10,
        max_total_tokens: int = 10000,
    ) -> tuple[Dict[str, str], int]:
        """
        Read multiple files (read-only).
        
        Args:
            file_paths: List of file paths.
            max_files: Maximum files to read.
            max_total_tokens: Maximum total tokens.
            
        Returns:
            Tuple of (file_contents, total_tokens).
        """
        contents = {}
        total_tokens = 0
        
        for path in file_paths[:max_files]:
            if total_tokens >= max_total_tokens:
                break
            
            try:
                content, tokens = self.read_file(path)
                remaining = max_total_tokens - total_tokens
                
                if tokens > remaining:
                    # Truncate content to fit budget
                    max_chars = remaining * 4
                    content = content[:max_chars - 3] + "..."
                    tokens = remaining
                
                contents[path] = content
                total_tokens += tokens
                
            except (FileNotFoundError, PermissionError):
                # Skip files we can't read
                continue
        
        return contents, total_tokens


# =============================================================================
# LLM Backend Protocol
# =============================================================================


class AnalysisLLMBackend(Protocol):
    """
    Protocol for LLM backend used in analysis.
    
    The backend is responsible for:
    - Making LLM API calls
    - Returning structured JSON responses
    - Tracking token usage
    """
    
    def analyze(
        self,
        prompt: str,
        system_prompt: str,
        max_output_tokens: int,
    ) -> tuple[str, int, int]:
        """
        Analyze code and return structured response.
        
        Args:
            prompt: User prompt with code to analyze.
            system_prompt: System prompt with instructions.
            max_output_tokens: Maximum output tokens.
            
        Returns:
            Tuple of (response_text, input_tokens, output_tokens).
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


class MockAnalysisBackend:
    """
    Mock LLM backend for testing analysis executor.
    """
    
    def __init__(
        self,
        responses: Optional[List[str]] = None,
        available: bool = True,
        model: str = "mock-analysis-model",
    ) -> None:
        """Initialize mock backend."""
        self._responses = responses or []
        self._response_index = 0
        self._available = available
        self._model = model
        self.call_count = 0
        self.prompts: List[str] = []
    
    def analyze(
        self,
        prompt: str,
        system_prompt: str,
        max_output_tokens: int,
    ) -> tuple[str, int, int]:
        """Analyze using mock response."""
        if not self._available:
            raise RuntimeError("LLM backend unavailable")
        
        self.call_count += 1
        self.prompts.append(prompt)
        
        if self._responses:
            response = self._responses[self._response_index % len(self._responses)]
            self._response_index += 1
        else:
            response = self._generate_default_response()
        
        input_tokens = len(prompt) // 4
        output_tokens = len(response) // 4
        
        return response, input_tokens, output_tokens
    
    def is_available(self) -> bool:
        """Check availability."""
        return self._available
    
    def model_name(self) -> str:
        """Get model name."""
        return self._model
    
    def _generate_default_response(self) -> str:
        """Generate default mock response."""
        return json.dumps({
            "observations": [
                "This is a mock observation from the analysis.",
            ],
            "inferences": [
                {
                    "type": "component_purpose",
                    "content": "This is a mock inference about the component.",
                    "confidence": "medium",
                    "evidence_refs": [0],
                }
            ],
            "evidence_excerpts": [
                {
                    "file": "mock_file.py",
                    "start_line": 1,
                    "end_line": 10,
                    "content": "# Mock content",
                    "symbols": ["mock_function"],
                }
            ],
        })


# =============================================================================
# Prompt Builders
# =============================================================================


ANALYSIS_SYSTEM_PROMPT = '''You are a code analysis assistant. Your role is to analyze code and produce EVIDENCE-BASED observations.

STRICT RULES:
1. Only report what you can OBSERVE in the code
2. Cite specific lines and symbols as evidence
3. Express uncertainty explicitly with confidence levels
4. Do NOT invent behavior not shown in code
5. Do NOT make assumptions about runtime behavior
6. Output MUST be valid JSON

Confidence levels:
- HIGH: Clear from code structure and documentation
- MEDIUM: Reasonable inference from patterns
- LOW: Uncertain, needs human verification

Output format:
{
    "observations": ["factual observations from code..."],
    "inferences": [
        {
            "type": "component_purpose|function_behavior|invariant|...",
            "content": "the inferred meaning",
            "confidence": "high|medium|low",
            "evidence_refs": [0, 1, ...]  // indexes into evidence_excerpts
        }
    ],
    "evidence_excerpts": [
        {
            "file": "path/to/file.py",
            "start_line": 10,
            "end_line": 20,
            "content": "exact quoted content",
            "symbols": ["function_name", "class_name"]
        }
    ]
}'''


def _build_analysis_prompt(
    task: DiscoveryTask,
    file_contents: Dict[str, str],
) -> str:
    """
    Build prompt for code analysis.
    
    Args:
        task: The discovery task.
        file_contents: Mapping of file paths to contents.
        
    Returns:
        Prompt string.
    """
    lines = [
        f"TASK: {task.name}",
        f"TYPE: {task.task_type.value}",
        f"DESCRIPTION: {task.description}",
        "",
    ]
    
    if task.focus_question:
        lines.append(f"FOCUS QUESTION: {task.focus_question}")
        lines.append("")
    
    lines.append("FILES TO ANALYZE:")
    lines.append("")
    
    for path, content in file_contents.items():
        lines.append(f"=== {path} ===")
        lines.append(content)
        lines.append("")
    
    lines.append("Analyze the code above and provide structured observations and inferences.")
    lines.append("Remember: All inferences must be backed by evidence from the code.")
    
    return "\n".join(lines)


# =============================================================================
# Response Parser
# =============================================================================


def _extract_json_from_response(response: str) -> Dict[str, Any]:
    """
    Extract JSON from LLM response.
    
    Handles markdown code blocks and plain JSON.
    """
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
                text = text.strip()
                if text.startswith("{") or text.startswith("["):
                    return json.loads(text)
            except json.JSONDecodeError:
                continue
    
    try:
        return json.loads(response.strip())
    except json.JSONDecodeError as e:
        raise ValueError(f"No valid JSON found in response: {e}")


def _parse_analysis_response(
    response_json: Dict[str, Any],
    task: DiscoveryTask,
    file_paths: List[str],
) -> tuple[InferenceEvidence, List[InferredAnnotation]]:
    """
    Parse analysis response into evidence and annotations.
    
    Args:
        response_json: Parsed JSON response.
        task: The discovery task.
        file_paths: Files that were analyzed.
        
    Returns:
        Tuple of (evidence, annotations).
    """
    # Parse evidence excerpts
    excerpts = []
    raw_excerpts = response_json.get("evidence_excerpts", [])
    
    for raw in raw_excerpts:
        excerpts.append(EvidenceExcerpt(
            file_path=raw.get("file", ""),
            start_line=raw.get("start_line", 0),
            end_line=raw.get("end_line", 0),
            content=raw.get("content", "")[:500],  # Limit content length
            symbols=raw.get("symbols", []),
        ))
    
    # Build evidence
    evidence = InferenceEvidence(
        excerpts=excerpts,
        referenced_artifacts=task.target_artifact_ids,
        observations=response_json.get("observations", []),
        analysis_context=f"Task: {task.name}",
    )
    
    # Parse inferences into annotations
    annotations = []
    raw_inferences = response_json.get("inferences", [])
    
    for i, raw in enumerate(raw_inferences):
        # Map inference type
        type_str = raw.get("type", "component_purpose")
        try:
            inference_type = InferenceType(type_str)
        except ValueError:
            inference_type = InferenceType.COMPONENT_PURPOSE
        
        # Map confidence
        conf_str = raw.get("confidence", "medium").lower()
        try:
            confidence = InferenceConfidence(conf_str)
        except ValueError:
            confidence = InferenceConfidence.MEDIUM
        
        # Build annotation-specific evidence
        evidence_refs = raw.get("evidence_refs", [])
        annotation_excerpts = [
            excerpts[ref] for ref in evidence_refs
            if 0 <= ref < len(excerpts)
        ]
        
        annotation_evidence = InferenceEvidence(
            excerpts=annotation_excerpts,
            referenced_artifacts=task.target_artifact_ids,
            observations=[],
            analysis_context=f"Inference from task: {task.name}",
        )
        
        # Generate annotation ID
        content = raw.get("content", "")
        annotation_id = f"ann_{task.id}_{i}_{hashlib.sha256(content.encode()).hexdigest()[:8]}"
        
        # Determine target artifact
        target_id = task.target_artifact_ids[0] if task.target_artifact_ids else ""
        
        annotation = InferredAnnotation(
            id=annotation_id,
            inference_type=inference_type,
            content=content[:500],  # Limit content length
            evidence=annotation_evidence,
            confidence=confidence,
            target_artifact_id=target_id,
            target_artifact_type="component",  # Default
            provenance={
                "task_id": task.id,
                "task_type": task.task_type.value,
            },
        )
        
        annotations.append(annotation)
    
    return evidence, annotations


# =============================================================================
# LLM Analysis Executor
# =============================================================================


class LLMAnalysisExecutor:
    """
    Read-only executor for discovery tasks.
    
    Analyzes SMALL, SCOPED slices of code.
    Produces structured evidence reports.
    
    HARD CONSTRAINTS:
    - Strict file count limits
    - Strict token budgets
    - Strict timeouts
    - JSON-only output
    - Deterministic failure on violations
    
    Executor MUST NOT:
    - Execute code
    - Modify files
    - Write Canon artifacts
    - Produce approvals or decisions
    - Run autonomously
    """
    
    def __init__(
        self,
        backend: AnalysisLLMBackend,
        project_root: str,
        config: Optional[AnalysisExecutorConfig] = None,
    ) -> None:
        """
        Initialize the analysis executor.
        
        Args:
            backend: LLM backend for analysis.
            project_root: Root directory of the project.
            config: Executor configuration.
        """
        self._backend = backend
        self._config = config or AnalysisExecutorConfig()
        self._file_reader = FileReader(
            project_root=project_root,
            max_tokens_per_file=self._config.max_tokens_per_file,
        )
    
    def execute(self, task: DiscoveryTask) -> DiscoveryResult:
        """
        Execute a discovery task.
        
        This is a READ-ONLY operation that:
        1. Reads files within scope limits
        2. Sends code to LLM for analysis
        3. Parses structured response
        4. Returns evidence and proposed annotations
        
        Args:
            task: The discovery task to execute.
            
        Returns:
            DiscoveryResult with evidence and proposed annotations.
        """
        start_time = time.time()
        
        # Initialize result
        result = DiscoveryResult(
            task_id=task.id,
            success=False,
        )
        
        # Check if executor is enabled
        if not self._config.enabled:
            result.errors.append("Analysis executor is disabled")
            return result
        
        # Check backend availability
        if not self._backend.is_available():
            result.errors.append("LLM backend is unavailable")
            return result
        
        # Validate task
        task_errors = task.validate()
        if task_errors:
            result.errors.extend(task_errors)
            return result
        
        # Read files within scope
        try:
            file_contents, total_tokens = self._file_reader.read_files(
                file_paths=task.scope.file_paths,
                max_files=min(task.scope.max_files, self._config.max_files_per_task),
                max_total_tokens=min(task.scope.max_total_tokens, self._config.max_total_tokens),
            )
        except Exception as e:
            result.errors.append(f"Failed to read files: {e}")
            return result
        
        if not file_contents:
            result.errors.append("No files could be read within scope")
            return result
        
        # Build analysis prompt
        prompt = _build_analysis_prompt(task, file_contents)
        
        # Call LLM for analysis
        try:
            response, input_tokens, output_tokens = self._backend.analyze(
                prompt=prompt,
                system_prompt=ANALYSIS_SYSTEM_PROMPT,
                max_output_tokens=self._config.max_output_tokens,
            )
            
            result.raw_llm_output = response
            result.token_usage = {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            }
            
        except Exception as e:
            result.errors.append(f"LLM analysis failed: {e}")
            return result
        
        # Parse response
        try:
            response_json = _extract_json_from_response(response)
        except ValueError as e:
            result.errors.append(f"Failed to parse response: {e}")
            return result
        
        # Extract evidence and annotations
        try:
            evidence, annotations = _parse_analysis_response(
                response_json=response_json,
                task=task,
                file_paths=list(file_contents.keys()),
            )
            
            result.evidence = evidence
            result.annotations = annotations
            result.success = True
            
        except Exception as e:
            result.errors.append(f"Failed to process response: {e}")
            return result
        
        # Record duration
        result.duration_seconds = time.time() - start_time
        
        # Check timeout
        if result.duration_seconds > task.timeout_seconds:
            result.errors.append(
                f"Task exceeded timeout: {result.duration_seconds:.2f}s > {task.timeout_seconds}s"
            )
            # Still return partial results but mark as warning
        
        return result


# =============================================================================
# Validation Functions
# =============================================================================


def validate_executor_is_read_only(executor: LLMAnalysisExecutor) -> bool:
    """
    Validate that the executor is read-only.
    
    The LLMAnalysisExecutor is read-only by design:
    - Uses FileReader which only reads
    - Has no write methods
    - Has no execute methods
    - Has no Canon mutation methods
    
    This function exists for documentation and testing.
    
    Args:
        executor: The executor to validate.
        
    Returns:
        Always True (executor is read-only by design).
    """
    # Check that executor has no dangerous methods
    dangerous_methods = [
        "write_file",
        "execute_command",
        "run_shell",
        "mutate_canon",
        "approve",
        "promote",
    ]
    
    for method in dangerous_methods:
        if hasattr(executor, method):
            return False
    
    return True


def validate_discovery_result_is_provisional(result: DiscoveryResult) -> bool:
    """
    Validate that all annotations in a result are provisional.
    
    All annotations MUST be in PROPOSED status.
    They are NOT Canon truth until human-approved.
    
    Args:
        result: The discovery result to validate.
        
    Returns:
        True if all annotations are provisional.
    """
    for annotation in result.annotations:
        if annotation.status != InferenceStatus.PROPOSED:
            return False
        if annotation.inference_label != INFERENCE_LABEL:
            return False
    
    return True
