"""
Context-Aware Execution Models for Axiom Forge.

This module defines the data structures for context-aware task execution.
Context-aware executors use local code understanding to apply instructions
precisely, but they have ZERO AGENCY, ZERO AUTHORITY, and ZERO AUTONOMY.

CORE PRINCIPLE:
    Executors may understand context.
    Executors may NOT decide intent.

Any executor that:
    - Expands task scope
    - Introduces new intent
    - Applies "helpful" extra changes
    - Retries or replans
is INVALID.

A Context-Aware Executor is an execution backend that:
    - Receives an explicit, fixed instruction
    - Uses an LLM ONLY to interpret local code context
    - Applies changes strictly within the given scope
    - Produces a deterministic result (usually a diff)
    - Has zero memory, zero learning, zero initiative

This is NOT an agent.
This is NOT a planner.
This is NOT a reviewer.

All models here are serializable and auditable.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any, FrozenSet


# =============================================================================
# ENUMERATIONS
# =============================================================================


class OperationType(str, Enum):
    """
    The type of operation a context-aware executor may perform.

    READ: Extract information from files without modification.
    EDIT: Modify files and produce a diff/patch.
    """

    READ = "read"
    EDIT = "edit"


class ContextAwareExecutionStatus(str, Enum):
    """
    The outcome status of a context-aware execution.

    SUCCEEDED: Instruction was applied successfully within constraints.
    FAILED: Execution failed due to error or constraint violation.
    """

    SUCCEEDED = "succeeded"
    FAILED = "failed"


class ViolationType(str, Enum):
    """
    Categories of constraint violations detected during execution.

    These violations cause immediate execution failure with no partial results.
    """

    # File access violations
    UNAUTHORIZED_FILE_READ = "unauthorized_file_read"
    UNAUTHORIZED_FILE_WRITE = "unauthorized_file_write"

    # Scope violations
    SCOPE_EXPANSION = "scope_expansion"
    NEW_SYMBOL_INTRODUCED = "new_symbol_introduced"
    UNRELATED_CHANGE = "unrelated_change"

    # Output violations
    PATCH_SIZE_OVERFLOW = "patch_size_overflow"
    NON_DIFF_OUTPUT = "non_diff_output"
    INVALID_DIFF_FORMAT = "invalid_diff_format"

    # Instruction violations
    INSTRUCTION_DEVIATION = "instruction_deviation"
    UNSOLICITED_SUGGESTION = "unsolicited_suggestion"
    UNSOLICITED_REFACTOR = "unsolicited_refactor"

    # Token/limit violations
    TOKEN_BUDGET_EXCEEDED = "token_budget_exceeded"
    TIMEOUT = "timeout"

    # LLM response violations
    LLM_REFUSED = "llm_refused"
    LLM_INVALID_RESPONSE = "llm_invalid_response"


# =============================================================================
# FORMATTING RULES
# =============================================================================


@dataclass(frozen=True)
class FormattingRules:
    """
    Optional formatting constraints for generated code.

    These rules are applied ONLY if explicitly provided.
    The executor will not infer or assume formatting preferences.

    Attributes:
        indent_style: "spaces" or "tabs".
        indent_size: Number of spaces per indent level.
        line_ending: Line ending style ("lf", "crlf").
        max_line_length: Maximum line length (0 = no limit).
        trailing_newline: Whether files should end with a newline.
    """

    indent_style: str = "spaces"
    indent_size: int = 4
    line_ending: str = "lf"
    max_line_length: int = 0
    trailing_newline: bool = True

    def __post_init__(self) -> None:
        """Validate formatting rules."""
        if self.indent_style not in ("spaces", "tabs"):
            raise ValueError(f"indent_style must be 'spaces' or 'tabs', got: {self.indent_style}")
        if self.indent_size < 1 or self.indent_size > 16:
            raise ValueError(f"indent_size must be 1-16, got: {self.indent_size}")
        if self.line_ending not in ("lf", "crlf"):
            raise ValueError(f"line_ending must be 'lf' or 'crlf', got: {self.line_ending}")
        if self.max_line_length < 0:
            raise ValueError(f"max_line_length must be >= 0, got: {self.max_line_length}")


# =============================================================================
# EXECUTION INPUT
# =============================================================================


@dataclass(frozen=True)
class ContextAwareExecutionInput:
    """
    The input for a context-aware execution.

    This structure defines EXACTLY what the executor is allowed to do.
    All fields are immutable after creation.

    Attributes:
        task_id: Unique identifier for this execution.
        explicit_instruction: The exact instruction to apply. IMMUTABLE.
        allowed_files: Whitelist of files the executor may access.
        operation_type: READ or EDIT.
        max_patch_size: Maximum allowed patch size in bytes.
        formatting_rules: Optional formatting constraints.
        max_context_tokens: Token budget for LLM context.
        timeout_seconds: Maximum execution time.
        metadata: Additional auditable metadata.

    Invariants:
        - explicit_instruction cannot be empty
        - allowed_files cannot be empty
        - max_patch_size must be positive
        - timeout_seconds must be positive
    """

    task_id: str
    explicit_instruction: str
    allowed_files: FrozenSet[str]
    operation_type: OperationType
    max_patch_size: int = 50_000  # 50KB default
    formatting_rules: Optional[FormattingRules] = None
    max_context_tokens: int = 8000
    timeout_seconds: int = 120
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate input constraints."""
        if not self.task_id:
            raise ValueError("task_id is required")
        if not self.explicit_instruction:
            raise ValueError("explicit_instruction is required and cannot be empty")
        if not self.allowed_files:
            raise ValueError("allowed_files is required and cannot be empty")
        if self.max_patch_size <= 0:
            raise ValueError(f"max_patch_size must be positive, got: {self.max_patch_size}")
        if self.max_context_tokens <= 0:
            raise ValueError(f"max_context_tokens must be positive, got: {self.max_context_tokens}")
        if self.timeout_seconds <= 0:
            raise ValueError(f"timeout_seconds must be positive, got: {self.timeout_seconds}")

    def is_file_allowed(self, file_path: str) -> bool:
        """
        Check if a file path is in the allowed whitelist.

        Args:
            file_path: The file path to check.

        Returns:
            True if the file is allowed, False otherwise.
        """
        return file_path in self.allowed_files

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize to a dictionary for auditing.

        Returns:
            Dictionary representation of the input.
        """
        return {
            "task_id": self.task_id,
            "explicit_instruction": self.explicit_instruction,
            "allowed_files": list(self.allowed_files),
            "operation_type": self.operation_type.value,
            "max_patch_size": self.max_patch_size,
            "formatting_rules": (
                {
                    "indent_style": self.formatting_rules.indent_style,
                    "indent_size": self.formatting_rules.indent_size,
                    "line_ending": self.formatting_rules.line_ending,
                    "max_line_length": self.formatting_rules.max_line_length,
                    "trailing_newline": self.formatting_rules.trailing_newline,
                }
                if self.formatting_rules
                else None
            ),
            "max_context_tokens": self.max_context_tokens,
            "timeout_seconds": self.timeout_seconds,
            "metadata": self.metadata,
        }


# =============================================================================
# VIOLATION RECORD
# =============================================================================


@dataclass(frozen=True)
class Violation:
    """
    A record of a constraint violation during execution.

    Attributes:
        violation_type: The category of violation.
        description: Human-readable description.
        evidence: Specific evidence of the violation.
        file_path: The file involved, if applicable.
    """

    violation_type: ViolationType
    description: str
    evidence: str = ""
    file_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize to a dictionary for auditing.

        Returns:
            Dictionary representation of the violation.
        """
        return {
            "violation_type": self.violation_type.value,
            "description": self.description,
            "evidence": self.evidence,
            "file_path": self.file_path,
        }


# =============================================================================
# EXECUTION RESULT
# =============================================================================


@dataclass(frozen=True)
class ContextAwareExecutionResult:
    """
    The outcome of a context-aware execution.

    This structure contains the result of execution, including any
    produced diff (for EDIT) or summary (for READ).

    Invariants:
        - If status is SUCCEEDED and operation is EDIT, diff must be present.
        - If status is SUCCEEDED and operation is READ, read_summary must be present.
        - If status is FAILED, violations should describe what went wrong.
        - touched_files must be a subset of allowed_files.

    Attributes:
        task_id: The task that was executed.
        status: SUCCEEDED or FAILED.
        diff: The produced patch (for EDIT operations).
        read_summary: The extracted summary (for READ operations).
        touched_files: Files that were read or modified.
        violations: List of constraint violations (if any).
        error_message: Human-readable error message (if failed).
        execution_time_ms: Execution time in milliseconds.
        tokens_used: Number of LLM tokens consumed.
        metadata: Additional auditable metadata.
    """

    task_id: str
    status: ContextAwareExecutionStatus
    diff: Optional[str] = None
    read_summary: Optional[str] = None
    touched_files: FrozenSet[str] = field(default_factory=frozenset)
    violations: tuple = field(default_factory=tuple)  # Tuple[Violation, ...]
    error_message: Optional[str] = None
    execution_time_ms: int = 0
    tokens_used: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate result constraints."""
        if not self.task_id:
            raise ValueError("task_id is required")

    @property
    def succeeded(self) -> bool:
        """Check if execution succeeded."""
        return self.status == ContextAwareExecutionStatus.SUCCEEDED

    @property
    def failed(self) -> bool:
        """Check if execution failed."""
        return self.status == ContextAwareExecutionStatus.FAILED

    @property
    def has_violations(self) -> bool:
        """Check if there are any violations."""
        return len(self.violations) > 0

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize to a dictionary for auditing.

        Returns:
            Dictionary representation of the result.
        """
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "diff": self.diff,
            "read_summary": self.read_summary,
            "touched_files": list(self.touched_files),
            "violations": [v.to_dict() for v in self.violations],
            "error_message": self.error_message,
            "execution_time_ms": self.execution_time_ms,
            "tokens_used": self.tokens_used,
            "metadata": self.metadata,
        }


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================


def create_failed_result(
    task_id: str,
    violations: List[Violation],
    error_message: str,
    execution_time_ms: int = 0,
    tokens_used: int = 0,
) -> ContextAwareExecutionResult:
    """
    Create a failed execution result.

    Args:
        task_id: The task identifier.
        violations: List of violations that caused failure.
        error_message: Human-readable error message.
        execution_time_ms: Execution time in milliseconds.
        tokens_used: Number of tokens consumed.

    Returns:
        A failed ContextAwareExecutionResult.
    """
    return ContextAwareExecutionResult(
        task_id=task_id,
        status=ContextAwareExecutionStatus.FAILED,
        violations=tuple(violations),
        error_message=error_message,
        execution_time_ms=execution_time_ms,
        tokens_used=tokens_used,
    )


def create_edit_result(
    task_id: str,
    diff: str,
    touched_files: FrozenSet[str],
    execution_time_ms: int = 0,
    tokens_used: int = 0,
) -> ContextAwareExecutionResult:
    """
    Create a successful EDIT execution result.

    Args:
        task_id: The task identifier.
        diff: The produced patch.
        touched_files: Files that were modified.
        execution_time_ms: Execution time in milliseconds.
        tokens_used: Number of tokens consumed.

    Returns:
        A successful ContextAwareExecutionResult for an EDIT operation.
    """
    return ContextAwareExecutionResult(
        task_id=task_id,
        status=ContextAwareExecutionStatus.SUCCEEDED,
        diff=diff,
        touched_files=touched_files,
        execution_time_ms=execution_time_ms,
        tokens_used=tokens_used,
    )


def create_read_result(
    task_id: str,
    read_summary: str,
    touched_files: FrozenSet[str],
    execution_time_ms: int = 0,
    tokens_used: int = 0,
) -> ContextAwareExecutionResult:
    """
    Create a successful READ execution result.

    Args:
        task_id: The task identifier.
        read_summary: The extracted summary.
        touched_files: Files that were read.
        execution_time_ms: Execution time in milliseconds.
        tokens_used: Number of tokens consumed.

    Returns:
        A successful ContextAwareExecutionResult for a READ operation.
    """
    return ContextAwareExecutionResult(
        task_id=task_id,
        status=ContextAwareExecutionStatus.SUCCEEDED,
        read_summary=read_summary,
        touched_files=touched_files,
        execution_time_ms=execution_time_ms,
        tokens_used=tokens_used,
    )


# =============================================================================
# CONSTANTS
# =============================================================================


# Label for all context-aware execution outputs
CONTEXT_AWARE_EXECUTION_LABEL = "[CONTEXT-AWARE EXECUTION – NO AGENCY]"

# Maximum allowed patch size (hard limit)
MAX_PATCH_SIZE_HARD_LIMIT = 500_000  # 500KB

# Maximum allowed context tokens (hard limit)
MAX_CONTEXT_TOKENS_HARD_LIMIT = 32_000
