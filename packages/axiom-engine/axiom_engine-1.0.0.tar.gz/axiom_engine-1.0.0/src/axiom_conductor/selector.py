"""
Executor Selector for Axiom Conductor.

This module provides deterministic executor selection based on task
requirements and executor capabilities. Selection is explicit,
reproducible, and has no heuristics or adaptive behavior.

CORE PRINCIPLES:
    1. First compatible executor by stable ordering
    2. No randomness
    3. No load-based decisions
    4. No retries or fallback
    5. If no compatible executor: fail fast

Selection rules are deterministic and auditable.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum

from axiom_conductor.registry_models import (
    ExecutorId,
    ExecutorDefinition,
    TaskExecutionRequirements,
    CapabilityMatchResult,
    CapabilityMatchStatus,
    BackendType,
    SupportedTaskType,
    AllowedOperation,
)
from axiom_conductor.registry import (
    ExecutorRegistry,
    ExecutorNotFoundError,
)


# =============================================================================
# SELECTION ERRORS
# =============================================================================


class SelectionError(Exception):
    """Base exception for selection errors."""

    pass


class NoCompatibleExecutorError(SelectionError):
    """Raised when no compatible executor is found."""

    def __init__(
        self,
        requirements: TaskExecutionRequirements,
        match_results: List[CapabilityMatchResult],
    ):
        self.requirements = requirements
        self.match_results = match_results
        super().__init__(
            f"No compatible executor found for requirements: "
            f"backend={requirements.required_backend.value}, "
            f"task_type={requirements.required_task_type.value}"
        )


class ExecutorIncompatibleError(SelectionError):
    """Raised when a specified executor is incompatible with requirements."""

    def __init__(
        self,
        executor_id: ExecutorId,
        match_result: CapabilityMatchResult,
    ):
        self.executor_id = executor_id
        self.match_result = match_result
        super().__init__(
            f"Executor {executor_id} is incompatible: {match_result.status.value} - {match_result.message}"
        )


# =============================================================================
# SELECTION RESULT
# =============================================================================


class SelectionStatus(str, Enum):
    """Status of executor selection."""

    SELECTED = "selected"
    NO_COMPATIBLE_EXECUTOR = "no_compatible_executor"
    EXECUTOR_INCOMPATIBLE = "executor_incompatible"
    REGISTRY_EMPTY = "registry_empty"


@dataclass(frozen=True)
class ExecutorSelectionResult:
    """
    Result of executor selection.

    Attributes:
        status: The selection status.
        executor: The selected executor (if successful).
        match_results: All capability match results for auditing.
        message: Human-readable message.
    """

    status: SelectionStatus
    executor: Optional[ExecutorDefinition] = None
    match_results: tuple = field(default_factory=tuple)  # Tuple[CapabilityMatchResult, ...]
    message: str = ""

    @property
    def succeeded(self) -> bool:
        """Check if selection succeeded."""
        return self.status == SelectionStatus.SELECTED and self.executor is not None

    @property
    def failed(self) -> bool:
        """Check if selection failed."""
        return not self.succeeded

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "status": self.status.value,
            "executor_id": str(self.executor.id) if self.executor else None,
            "executor_name": self.executor.name if self.executor else None,
            "match_results": [r.to_dict() for r in self.match_results],
            "message": self.message,
        }


# =============================================================================
# EXECUTOR SELECTOR
# =============================================================================


@dataclass
class ExecutorSelector:
    """
    Deterministic executor selector.

    The selector uses a frozen registry to find compatible executors
    for task requirements. Selection is:
    - Deterministic (same inputs → same output)
    - Explicit (no hidden heuristics)
    - Auditable (full match history)
    - Fail-fast (no retries or fallback)

    Attributes:
        registry: The frozen executor registry.
    """

    registry: ExecutorRegistry

    def __post_init__(self) -> None:
        """Validate that registry is frozen."""
        if not self.registry.is_frozen:
            raise ValueError("ExecutorSelector requires a frozen registry")

    def select(
        self,
        requirements: TaskExecutionRequirements,
    ) -> ExecutorSelectionResult:
        """
        Select an executor for task requirements.

        Selection is deterministic:
        - First compatible executor by stable ordering (priority, then ID)
        - No randomness
        - No load-based decisions
        - No retries or fallback

        Args:
            requirements: The task requirements.

        Returns:
            ExecutorSelectionResult with status and selected executor.
        """
        if len(self.registry) == 0:
            return ExecutorSelectionResult(
                status=SelectionStatus.REGISTRY_EMPTY,
                message="No executors registered",
            )

        executor, match_results = self.registry.find_compatible(requirements)

        if executor is not None:
            return ExecutorSelectionResult(
                status=SelectionStatus.SELECTED,
                executor=executor,
                match_results=tuple(match_results),
                message=f"Selected executor: {executor.name} ({executor.id})",
            )
        else:
            return ExecutorSelectionResult(
                status=SelectionStatus.NO_COMPATIBLE_EXECUTOR,
                match_results=tuple(match_results),
                message=self._format_no_match_message(requirements, match_results),
            )

    def select_or_raise(
        self,
        requirements: TaskExecutionRequirements,
    ) -> ExecutorDefinition:
        """
        Select an executor or raise an exception.

        Args:
            requirements: The task requirements.

        Returns:
            The selected executor.

        Raises:
            NoCompatibleExecutorError: If no compatible executor found.
        """
        result = self.select(requirements)

        if result.failed:
            raise NoCompatibleExecutorError(
                requirements=requirements,
                match_results=list(result.match_results),
            )

        assert result.executor is not None
        return result.executor

    def validate_executor(
        self,
        executor_id: ExecutorId,
        requirements: TaskExecutionRequirements,
    ) -> ExecutorSelectionResult:
        """
        Validate that a specific executor is compatible.

        Use this when an executor has already been chosen (e.g., by human)
        and needs to be validated against requirements.

        Args:
            executor_id: The executor to validate.
            requirements: The task requirements.

        Returns:
            ExecutorSelectionResult with validation status.
        """
        try:
            match_result = self.registry.validate_compatibility(executor_id, requirements)
        except ExecutorNotFoundError:
            return ExecutorSelectionResult(
                status=SelectionStatus.NO_COMPATIBLE_EXECUTOR,
                message=f"Executor not found: {executor_id}",
            )

        if match_result.is_compatible:
            executor = self.registry.get(executor_id)
            return ExecutorSelectionResult(
                status=SelectionStatus.SELECTED,
                executor=executor,
                match_results=(match_result,),
                message=f"Executor {executor_id} is compatible",
            )
        else:
            return ExecutorSelectionResult(
                status=SelectionStatus.EXECUTOR_INCOMPATIBLE,
                match_results=(match_result,),
                message=f"Executor {executor_id} is incompatible: {match_result.message}",
            )

    def validate_or_raise(
        self,
        executor_id: ExecutorId,
        requirements: TaskExecutionRequirements,
    ) -> ExecutorDefinition:
        """
        Validate a specific executor or raise an exception.

        Args:
            executor_id: The executor to validate.
            requirements: The task requirements.

        Returns:
            The validated executor.

        Raises:
            ExecutorIncompatibleError: If executor is incompatible.
            ExecutorNotFoundError: If executor not found.
        """
        match_result = self.registry.validate_compatibility(executor_id, requirements)

        if not match_result.is_compatible:
            raise ExecutorIncompatibleError(executor_id, match_result)

        return self.registry.get(executor_id)

    def _format_no_match_message(
        self,
        requirements: TaskExecutionRequirements,
        match_results: List[CapabilityMatchResult],
    ) -> str:
        """Format a detailed message for no match."""
        lines = [
            f"No compatible executor for: backend={requirements.required_backend.value}, "
            f"task_type={requirements.required_task_type.value}",
            "Checked executors:",
        ]
        for result in match_results:
            lines.append(f"  - {result.executor_id}: {result.status.value}")
            if result.message:
                lines.append(f"    {result.message}")
        return "\n".join(lines)


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================


def create_selector(registry: ExecutorRegistry) -> ExecutorSelector:
    """
    Create an executor selector from a registry.

    Args:
        registry: The executor registry (will be frozen if not already).

    Returns:
        ExecutorSelector instance.
    """
    if not registry.is_frozen:
        registry.freeze()
    return ExecutorSelector(registry=registry)


# =============================================================================
# REQUIREMENT BUILDERS
# =============================================================================


def shell_requirements(
    command: str,
    timeout: int = 60,
) -> TaskExecutionRequirements:
    """
    Create requirements for a shell task.

    Args:
        command: The shell command to execute.
        timeout: Estimated timeout in seconds.

    Returns:
        TaskExecutionRequirements for shell execution.
    """
    return TaskExecutionRequirements(
        required_backend=BackendType.SHELL,
        required_task_type=SupportedTaskType.EXECUTION,
        command=command,
        estimated_timeout=timeout,
    )


def playwright_requirements(
    domain: str,
    timeout: int = 60,
) -> TaskExecutionRequirements:
    """
    Create requirements for a Playwright task.

    Args:
        domain: The domain to access.
        timeout: Estimated timeout in seconds.

    Returns:
        TaskExecutionRequirements for Playwright execution.
    """
    return TaskExecutionRequirements(
        required_backend=BackendType.PLAYWRIGHT,
        required_task_type=SupportedTaskType.EXECUTION,
        domain=domain,
        estimated_timeout=timeout,
    )


def context_aware_requirements(
    files: List[str],
    operation: AllowedOperation,
    timeout: int = 120,
) -> TaskExecutionRequirements:
    """
    Create requirements for a context-aware task.

    Args:
        files: Files to access.
        operation: Operation type (READ or EDIT).
        timeout: Estimated timeout in seconds.

    Returns:
        TaskExecutionRequirements for context-aware execution.
    """
    from axiom_conductor.registry_models import ExecutorCognitionLevel

    return TaskExecutionRequirements(
        required_backend=BackendType.CONTEXT_AWARE,
        required_task_type=SupportedTaskType.EXECUTION,
        required_cognition_level=ExecutorCognitionLevel.LEVEL_1_CONTEXT_AWARE,
        required_operation=operation,
        files_to_access=frozenset(files),
        estimated_timeout=timeout,
    )


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================


def validate_selector_is_deterministic(
    selector: ExecutorSelector,
    requirements: TaskExecutionRequirements,
) -> bool:
    """
    Validate that selector produces deterministic results.

    Args:
        selector: The selector to validate.
        requirements: Requirements to test with.

    Returns:
        True if selection is deterministic.
    """
    result1 = selector.select(requirements)
    result2 = selector.select(requirements)

    if result1.executor is None and result2.executor is None:
        return True

    if result1.executor is None or result2.executor is None:
        return False

    return str(result1.executor.id) == str(result2.executor.id)


def validate_selector_has_no_randomness(selector: ExecutorSelector) -> List[str]:
    """
    Validate that selector has no randomness.

    Args:
        selector: The selector to validate.

    Returns:
        List of violations (empty if valid).
    """
    violations = []

    # Check for forbidden attributes
    forbidden_attrs = [
        "random",
        "seed",
        "shuffle",
        "sample",
    ]

    for attr in forbidden_attrs:
        if hasattr(selector, attr):
            violations.append(f"Selector has forbidden random attribute: {attr}")

    return violations
