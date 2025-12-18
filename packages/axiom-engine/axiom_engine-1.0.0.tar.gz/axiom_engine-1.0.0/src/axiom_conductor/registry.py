"""
Executor Registry for Axiom Conductor.

This module implements the central registry for executor definitions.
The registry is deterministic, immutable at runtime, and provides
read-only access to executor information for scheduling.

CORE PRINCIPLES:
    1. Deterministic loading and ordering
    2. Reject invalid or conflicting definitions
    3. No scheduling logic
    4. No selection heuristics
    5. No runtime modification
    6. Human-configurable only

The registry MUST NOT:
    - Perform scheduling
    - Perform selection heuristics
    - Modify executor behavior
    - Change at runtime
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Iterator, Tuple, Set, FrozenSet
import json
from pathlib import Path

from axiom_conductor.registry_models import (
    ExecutorId,
    ExecutorDefinition,
    ExecutorType,
    ExecutorCognitionLevel,
    ExecutorCapabilities,
    ExecutorPolicy,
    BackendType,
    SupportedTaskType,
    AllowedOperation,
    TaskExecutionRequirements,
    CapabilityMatchResult,
    CapabilityMatchStatus,
)


# =============================================================================
# REGISTRY ERRORS
# =============================================================================


class RegistryError(Exception):
    """Base exception for registry errors."""

    pass


class DuplicateExecutorError(RegistryError):
    """Raised when an executor ID is already registered."""

    def __init__(self, executor_id: ExecutorId):
        self.executor_id = executor_id
        super().__init__(f"Executor already registered: {executor_id}")


class InvalidDefinitionError(RegistryError):
    """Raised when an executor definition is invalid."""

    def __init__(self, message: str, executor_id: Optional[ExecutorId] = None):
        self.executor_id = executor_id
        super().__init__(message)


class ExecutorNotFoundError(RegistryError):
    """Raised when an executor is not found in the registry."""

    def __init__(self, executor_id: ExecutorId):
        self.executor_id = executor_id
        super().__init__(f"Executor not found: {executor_id}")


class RegistryFrozenError(RegistryError):
    """Raised when attempting to modify a frozen registry."""

    def __init__(self):
        super().__init__("Registry is frozen and cannot be modified")


# =============================================================================
# CAPABILITY MATCHER
# =============================================================================


@dataclass
class CapabilityMatcher:
    """
    Matches task requirements against executor capabilities.

    This is a pure function object with no state or side effects.
    Matching is deterministic and explicit.
    """

    def match(
        self,
        executor: ExecutorDefinition,
        requirements: TaskExecutionRequirements,
    ) -> CapabilityMatchResult:
        """
        Check if an executor matches task requirements.

        Args:
            executor: The executor to check.
            requirements: The task requirements.

        Returns:
            CapabilityMatchResult with status and message.
        """
        # Check if executor is enabled
        if not executor.enabled:
            return CapabilityMatchResult(
                executor_id=executor.id,
                status=CapabilityMatchStatus.EXECUTOR_DISABLED,
                message=f"Executor {executor.id} is disabled",
            )

        # Check backend compatibility
        if not executor.capabilities.supports_backend(requirements.required_backend):
            return CapabilityMatchResult(
                executor_id=executor.id,
                status=CapabilityMatchStatus.INCOMPATIBLE_BACKEND,
                message=f"Executor does not support backend: {requirements.required_backend.value}",
            )

        # Check task type compatibility
        if not executor.capabilities.supports_task_type(requirements.required_task_type):
            return CapabilityMatchResult(
                executor_id=executor.id,
                status=CapabilityMatchStatus.INCOMPATIBLE_TASK_TYPE,
                message=f"Executor does not support task type: {requirements.required_task_type.value}",
            )

        # Check cognition level if required
        if requirements.required_cognition_level is not None:
            if executor.cognition_level != requirements.required_cognition_level:
                return CapabilityMatchResult(
                    executor_id=executor.id,
                    status=CapabilityMatchStatus.INCOMPATIBLE_COGNITION,
                    message=f"Executor cognition level {executor.cognition_level.value} "
                    f"does not match required {requirements.required_cognition_level.value}",
                )

        # Check operation compatibility for context-aware executors
        if requirements.required_operation is not None:
            if not executor.capabilities.supports_operation(requirements.required_operation):
                return CapabilityMatchResult(
                    executor_id=executor.id,
                    status=CapabilityMatchStatus.INCOMPATIBLE_OPERATION,
                    message=f"Executor does not support operation: {requirements.required_operation.value}",
                )

        # Check policy: command allowlist (for shell)
        if requirements.command is not None:
            if not executor.policy.allows_command(requirements.command):
                return CapabilityMatchResult(
                    executor_id=executor.id,
                    status=CapabilityMatchStatus.POLICY_VIOLATION_COMMAND,
                    message=f"Command not in allowlist: {requirements.command}",
                )

        # Check policy: domain allowlist (for playwright)
        if requirements.domain is not None:
            if not executor.policy.allows_domain(requirements.domain):
                return CapabilityMatchResult(
                    executor_id=executor.id,
                    status=CapabilityMatchStatus.POLICY_VIOLATION_DOMAIN,
                    message=f"Domain not in allowlist: {requirements.domain}",
                )

        # Check policy: file access patterns (for context-aware)
        if requirements.files_to_access:
            for file_path in requirements.files_to_access:
                if not executor.policy.allows_file_access(file_path):
                    return CapabilityMatchResult(
                        executor_id=executor.id,
                        status=CapabilityMatchStatus.POLICY_VIOLATION_FILE_ACCESS,
                        message=f"File access not allowed: {file_path}",
                    )

        # Check policy: timeout
        if requirements.estimated_timeout > executor.policy.timeout_seconds:
            return CapabilityMatchResult(
                executor_id=executor.id,
                status=CapabilityMatchStatus.POLICY_VIOLATION_TIMEOUT,
                message=f"Estimated timeout {requirements.estimated_timeout}s exceeds limit {executor.policy.timeout_seconds}s",
            )

        # Check policy: output size
        if requirements.estimated_output_bytes > executor.policy.max_output_bytes:
            return CapabilityMatchResult(
                executor_id=executor.id,
                status=CapabilityMatchStatus.POLICY_VIOLATION_OUTPUT_SIZE,
                message=f"Estimated output {requirements.estimated_output_bytes} bytes exceeds limit {executor.policy.max_output_bytes} bytes",
            )

        # All checks passed
        return CapabilityMatchResult(
            executor_id=executor.id,
            status=CapabilityMatchStatus.COMPATIBLE,
            message="Executor is compatible with task requirements",
        )


# =============================================================================
# EXECUTOR REGISTRY
# =============================================================================


@dataclass
class ExecutorRegistry:
    """
    Central registry for executor definitions.

    The registry is the single source of truth for available executors.
    It is deterministic, immutable once frozen, and provides read-only
    access to executor information.

    Attributes:
        _executors: Internal mapping of executor IDs to definitions.
        _frozen: Whether the registry is frozen (immutable).
        _matcher: Capability matcher for validation.
    """

    _executors: Dict[str, ExecutorDefinition] = field(default_factory=dict)
    _frozen: bool = False
    _matcher: CapabilityMatcher = field(default_factory=CapabilityMatcher)

    # =========================================================================
    # REGISTRATION (BEFORE FREEZE)
    # =========================================================================

    def register(self, executor: ExecutorDefinition) -> None:
        """
        Register an executor definition.

        Args:
            executor: The executor definition to register.

        Raises:
            RegistryFrozenError: If registry is frozen.
            DuplicateExecutorError: If executor ID already exists.
            InvalidDefinitionError: If definition is invalid.
        """
        if self._frozen:
            raise RegistryFrozenError()

        executor_id = str(executor.id)

        if executor_id in self._executors:
            raise DuplicateExecutorError(executor.id)

        # Validate the definition
        self._validate_definition(executor)

        self._executors[executor_id] = executor

    def register_all(self, executors: List[ExecutorDefinition]) -> None:
        """
        Register multiple executor definitions.

        Args:
            executors: List of executor definitions.

        Raises:
            RegistryFrozenError: If registry is frozen.
            DuplicateExecutorError: If any executor ID already exists.
            InvalidDefinitionError: If any definition is invalid.
        """
        for executor in executors:
            self.register(executor)

    def _validate_definition(self, executor: ExecutorDefinition) -> None:
        """
        Validate an executor definition.

        Args:
            executor: The definition to validate.

        Raises:
            InvalidDefinitionError: If definition is invalid.
        """
        # Check for conflicting capabilities
        has_shell = BackendType.SHELL in executor.capabilities.supported_backends
        has_context_aware = BackendType.CONTEXT_AWARE in executor.capabilities.supported_backends

        # Shell executors need command allowlist
        if has_shell and not executor.policy.command_allowlist:
            raise InvalidDefinitionError(
                f"Shell executor {executor.id} requires non-empty command_allowlist",
                executor.id,
            )

        # Context-aware executors need file access patterns
        if has_context_aware and not executor.policy.file_access_patterns:
            raise InvalidDefinitionError(
                f"Context-aware executor {executor.id} requires non-empty file_access_patterns",
                executor.id,
            )

    # =========================================================================
    # FREEZE
    # =========================================================================

    def freeze(self) -> "ExecutorRegistry":
        """
        Freeze the registry, making it immutable.

        After freezing, no new executors can be registered.

        Returns:
            Self for chaining.
        """
        self._frozen = True
        return self

    @property
    def is_frozen(self) -> bool:
        """Check if registry is frozen."""
        return self._frozen

    # =========================================================================
    # READ-ONLY ACCESS
    # =========================================================================

    def get(self, executor_id: ExecutorId) -> ExecutorDefinition:
        """
        Get an executor by ID.

        Args:
            executor_id: The executor ID to look up.

        Returns:
            The executor definition.

        Raises:
            ExecutorNotFoundError: If executor not found.
        """
        key = str(executor_id)
        if key not in self._executors:
            raise ExecutorNotFoundError(executor_id)
        return self._executors[key]

    def get_optional(self, executor_id: ExecutorId) -> Optional[ExecutorDefinition]:
        """
        Get an executor by ID, or None if not found.

        Args:
            executor_id: The executor ID to look up.

        Returns:
            The executor definition or None.
        """
        return self._executors.get(str(executor_id))

    def contains(self, executor_id: ExecutorId) -> bool:
        """Check if an executor is registered."""
        return str(executor_id) in self._executors

    def __len__(self) -> int:
        """Return number of registered executors."""
        return len(self._executors)

    def __iter__(self) -> Iterator[ExecutorDefinition]:
        """Iterate over executor definitions in stable order."""
        # Sort by priority (lower first), then by ID for determinism
        return iter(
            sorted(
                self._executors.values(),
                key=lambda e: (e.priority, str(e.id)),
            )
        )

    def list_all(self) -> List[ExecutorDefinition]:
        """
        Get all executors in stable order.

        Returns:
            List of executor definitions sorted by priority and ID.
        """
        return list(self)

    def list_enabled(self) -> List[ExecutorDefinition]:
        """
        Get all enabled executors in stable order.

        Returns:
            List of enabled executor definitions.
        """
        return [e for e in self if e.enabled]

    def list_by_backend(self, backend: BackendType) -> List[ExecutorDefinition]:
        """
        Get executors that support a specific backend.

        Args:
            backend: The backend type to filter by.

        Returns:
            List of compatible executors in stable order.
        """
        return [
            e for e in self
            if e.capabilities.supports_backend(backend) and e.enabled
        ]

    def list_by_cognition(self, level: ExecutorCognitionLevel) -> List[ExecutorDefinition]:
        """
        Get executors with a specific cognition level.

        Args:
            level: The cognition level to filter by.

        Returns:
            List of matching executors in stable order.
        """
        return [e for e in self if e.cognition_level == level and e.enabled]

    # =========================================================================
    # EXECUTOR SELECTION (DETERMINISTIC)
    # =========================================================================

    def find_compatible(
        self,
        requirements: TaskExecutionRequirements,
    ) -> Tuple[Optional[ExecutorDefinition], List[CapabilityMatchResult]]:
        """
        Find a compatible executor for task requirements.

        Selection is deterministic:
        - First compatible executor by stable ordering (priority, then ID)
        - No randomness
        - No load-based decisions
        - No retries or fallback

        Args:
            requirements: The task requirements.

        Returns:
            Tuple of:
            - The first compatible executor, or None if none found.
            - List of all match results for auditing.
        """
        match_results: List[CapabilityMatchResult] = []

        for executor in self:
            result = self._matcher.match(executor, requirements)
            match_results.append(result)

            if result.is_compatible:
                return (executor, match_results)

        return (None, match_results)

    def validate_compatibility(
        self,
        executor_id: ExecutorId,
        requirements: TaskExecutionRequirements,
    ) -> CapabilityMatchResult:
        """
        Validate that a specific executor is compatible with requirements.

        Args:
            executor_id: The executor to check.
            requirements: The task requirements.

        Returns:
            CapabilityMatchResult with status.

        Raises:
            ExecutorNotFoundError: If executor not found.
        """
        executor = self.get(executor_id)
        return self._matcher.match(executor, requirements)

    # =========================================================================
    # SERIALIZATION
    # =========================================================================

    def to_dict(self) -> Dict:
        """Serialize registry to dictionary."""
        return {
            "executors": [e.to_dict() for e in self],
            "frozen": self._frozen,
        }


# =============================================================================
# REGISTRY BUILDER
# =============================================================================


@dataclass
class ExecutorRegistryBuilder:
    """
    Builder for constructing an ExecutorRegistry.

    Provides a fluent interface for building registries with validation.
    """

    _registry: ExecutorRegistry = field(default_factory=ExecutorRegistry)

    def add(self, executor: ExecutorDefinition) -> "ExecutorRegistryBuilder":
        """
        Add an executor to the registry.

        Args:
            executor: The executor definition.

        Returns:
            Self for chaining.
        """
        self._registry.register(executor)
        return self

    def add_shell(
        self,
        executor_id: str,
        name: str,
        command_allowlist: FrozenSet[str],
        priority: int = 100,
        timeout_seconds: int = 300,
    ) -> "ExecutorRegistryBuilder":
        """
        Add a shell executor.

        Args:
            executor_id: Unique identifier.
            name: Human-readable name.
            command_allowlist: Allowed commands.
            priority: Selection priority.
            timeout_seconds: Timeout limit.

        Returns:
            Self for chaining.
        """
        from axiom_conductor.registry_models import create_shell_executor

        self._registry.register(
            create_shell_executor(
                executor_id=executor_id,
                name=name,
                command_allowlist=command_allowlist,
                priority=priority,
                timeout_seconds=timeout_seconds,
            )
        )
        return self

    def add_playwright(
        self,
        executor_id: str,
        name: str,
        domain_allowlist: FrozenSet[str],
        priority: int = 100,
        timeout_seconds: int = 300,
    ) -> "ExecutorRegistryBuilder":
        """
        Add a Playwright executor.

        Args:
            executor_id: Unique identifier.
            name: Human-readable name.
            domain_allowlist: Allowed domains.
            priority: Selection priority.
            timeout_seconds: Timeout limit.

        Returns:
            Self for chaining.
        """
        from axiom_conductor.registry_models import create_playwright_executor

        self._registry.register(
            create_playwright_executor(
                executor_id=executor_id,
                name=name,
                domain_allowlist=domain_allowlist,
                priority=priority,
                timeout_seconds=timeout_seconds,
            )
        )
        return self

    def add_context_aware(
        self,
        executor_id: str,
        name: str,
        file_access_patterns: FrozenSet[str],
        allowed_operations: FrozenSet[AllowedOperation],
        priority: int = 100,
        max_patch_size: int = 50_000,
        max_context_tokens: int = 8000,
        timeout_seconds: int = 120,
    ) -> "ExecutorRegistryBuilder":
        """
        Add a context-aware executor.

        Args:
            executor_id: Unique identifier.
            name: Human-readable name.
            file_access_patterns: Allowed file patterns.
            allowed_operations: Allowed operations.
            priority: Selection priority.
            max_patch_size: Max patch size.
            max_context_tokens: Max context tokens.
            timeout_seconds: Timeout limit.

        Returns:
            Self for chaining.
        """
        from axiom_conductor.registry_models import create_context_aware_executor

        self._registry.register(
            create_context_aware_executor(
                executor_id=executor_id,
                name=name,
                file_access_patterns=file_access_patterns,
                allowed_operations=allowed_operations,
                priority=priority,
                max_patch_size=max_patch_size,
                max_context_tokens=max_context_tokens,
                timeout_seconds=timeout_seconds,
            )
        )
        return self

    def build(self) -> ExecutorRegistry:
        """
        Build and freeze the registry.

        Returns:
            The frozen ExecutorRegistry.
        """
        return self._registry.freeze()


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================


def validate_registry_is_deterministic(registry: ExecutorRegistry) -> bool:
    """
    Validate that registry iteration is deterministic.

    Args:
        registry: The registry to validate.

    Returns:
        True if iteration order is stable.
    """
    first_pass = [str(e.id) for e in registry]
    second_pass = [str(e.id) for e in registry]
    return first_pass == second_pass


def validate_registry_has_no_heuristics(registry: ExecutorRegistry) -> List[str]:
    """
    Validate that registry has no heuristic-based methods.

    Args:
        registry: The registry to validate.

    Returns:
        List of violations (empty if valid).
    """
    violations = []

    # Check for forbidden method names
    forbidden_methods = [
        "select_best",
        "choose_optimal",
        "balance_load",
        "adaptive_select",
        "learn",
        "train",
        "optimize",
    ]

    for method in forbidden_methods:
        if hasattr(registry, method):
            violations.append(f"Registry has forbidden heuristic method: {method}")

    return violations


def validate_no_runtime_mutation(registry: ExecutorRegistry) -> bool:
    """
    Validate that a frozen registry cannot be mutated.

    Args:
        registry: The registry to validate.

    Returns:
        True if mutation is properly blocked.
    """
    if not registry.is_frozen:
        return False

    try:
        from axiom_conductor.registry_models import create_shell_executor

        registry.register(
            create_shell_executor(
                executor_id="test-mutation",
                name="Test",
                command_allowlist=frozenset({"echo"}),
            )
        )
        return False  # Should have raised
    except RegistryFrozenError:
        return True
