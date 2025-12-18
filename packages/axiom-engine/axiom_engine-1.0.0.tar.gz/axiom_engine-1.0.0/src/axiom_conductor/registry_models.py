"""
Executor Registry Models for Axiom Conductor.

This module defines the data structures for declaring executor capabilities,
policies, and metadata. These models enable deterministic executor selection
without heuristics, learning, or runtime adaptation.

CORE PRINCIPLES:
    1. Executors do not decide
    2. Executors do not negotiate
    3. Executors do not adapt
    4. Executor selection is deterministic
    5. Executor capabilities are explicit
    6. Policy mismatches fail fast
    7. No automatic fallback or retries

All models are:
    - Declarative
    - Serializable
    - Immutable at runtime
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import FrozenSet, Dict, Any, Optional, List
import uuid


# =============================================================================
# EXECUTOR IDENTIFICATION
# =============================================================================


@dataclass(frozen=True)
class ExecutorId:
    """
    Opaque identifier for an executor.

    This is an immutable value object that uniquely identifies an executor
    within the registry. The value should be human-readable for debugging
    but treated as opaque by the system.

    Attributes:
        value: The unique identifier string.
    """

    value: str

    def __post_init__(self) -> None:
        """Validate the executor ID."""
        if not self.value:
            raise ValueError("ExecutorId value cannot be empty")
        if not self.value.replace("-", "").replace("_", "").isalnum():
            raise ValueError(f"ExecutorId must be alphanumeric with - or _: {self.value}")

    def __str__(self) -> str:
        """Return string representation."""
        return self.value

    @classmethod
    def generate(cls, prefix: str = "executor") -> "ExecutorId":
        """
        Generate a new unique executor ID.

        Args:
            prefix: Prefix for the ID.

        Returns:
            A new ExecutorId.
        """
        return cls(f"{prefix}-{uuid.uuid4().hex[:8]}")


# =============================================================================
# EXECUTOR TYPE
# =============================================================================


class ExecutorType(str, Enum):
    """
    The deployment type of an executor.

    LOCAL: Executor runs on the same machine as Conductor.
    REMOTE: Executor runs on a different machine (future use).
    """

    LOCAL = "local"
    REMOTE = "remote"


# =============================================================================
# EXECUTOR COGNITION LEVEL
# =============================================================================


class ExecutorCognitionLevel(str, Enum):
    """
    The cognition level of an executor.

    LEVEL_0_DUMB: Executor executes commands exactly as given.
        - No context awareness
        - No LLM integration
        - Examples: ShellExecutionBackend, PlaywrightExecutionBackend

    LEVEL_1_CONTEXT_AWARE: Executor can understand local code context.
        - Uses LLM for local interpretation only
        - Zero agency, zero memory, zero learning
        - Example: ContextAwareExecutionBackend
    """

    LEVEL_0_DUMB = "level_0_dumb"
    LEVEL_1_CONTEXT_AWARE = "level_1_context_aware"


# =============================================================================
# BACKEND TYPE
# =============================================================================


class BackendType(str, Enum):
    """
    The type of execution backend.

    SHELL: Command-line execution via subprocess.
    PLAYWRIGHT: Browser automation via Playwright.
    CONTEXT_AWARE: LLM-assisted code execution with strict constraints.
    """

    SHELL = "shell"
    PLAYWRIGHT = "playwright"
    CONTEXT_AWARE = "context_aware"


# =============================================================================
# TASK TYPE
# =============================================================================


class SupportedTaskType(str, Enum):
    """
    Types of tasks an executor can handle.

    EXECUTION: Standard task execution (commands, scripts, etc.)
    DISCOVERY: Code discovery and analysis tasks.
    """

    EXECUTION = "execution"
    DISCOVERY = "discovery"


# =============================================================================
# OPERATION TYPE
# =============================================================================


class AllowedOperation(str, Enum):
    """
    Types of operations allowed for context-aware executors.

    READ: Read and analyze files without modification.
    EDIT: Modify files and produce diffs.
    """

    READ = "read"
    EDIT = "edit"


# =============================================================================
# EXECUTOR CAPABILITIES
# =============================================================================


@dataclass(frozen=True)
class ExecutorCapabilities:
    """
    Declares what an executor can do.

    This is an immutable, explicit declaration of executor capabilities.
    No implicit capabilities are assumed.

    Attributes:
        supported_backends: Set of backend types this executor supports.
        supported_task_types: Set of task types this executor can handle.
        max_parallel_tasks: Maximum concurrent tasks (0 = no limit).
        max_patch_size: Maximum patch size in bytes (context-aware only).
        allowed_operations: Set of allowed operations (context-aware only).
    """

    supported_backends: FrozenSet[BackendType]
    supported_task_types: FrozenSet[SupportedTaskType]
    max_parallel_tasks: int = 1
    max_patch_size: int = 50_000  # 50KB default
    allowed_operations: FrozenSet[AllowedOperation] = field(
        default_factory=lambda: frozenset({AllowedOperation.READ, AllowedOperation.EDIT})
    )

    def __post_init__(self) -> None:
        """Validate capabilities."""
        if not self.supported_backends:
            raise ValueError("supported_backends cannot be empty")
        if not self.supported_task_types:
            raise ValueError("supported_task_types cannot be empty")
        if self.max_parallel_tasks < 0:
            raise ValueError(f"max_parallel_tasks must be >= 0, got: {self.max_parallel_tasks}")
        if self.max_patch_size <= 0:
            raise ValueError(f"max_patch_size must be > 0, got: {self.max_patch_size}")

    def supports_backend(self, backend: BackendType) -> bool:
        """Check if executor supports a backend type."""
        return backend in self.supported_backends

    def supports_task_type(self, task_type: SupportedTaskType) -> bool:
        """Check if executor supports a task type."""
        return task_type in self.supported_task_types

    def supports_operation(self, operation: AllowedOperation) -> bool:
        """Check if executor supports an operation."""
        return operation in self.allowed_operations

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "supported_backends": [b.value for b in self.supported_backends],
            "supported_task_types": [t.value for t in self.supported_task_types],
            "max_parallel_tasks": self.max_parallel_tasks,
            "max_patch_size": self.max_patch_size,
            "allowed_operations": [o.value for o in self.allowed_operations],
        }


# =============================================================================
# EXECUTOR POLICY
# =============================================================================


@dataclass(frozen=True)
class ExecutorPolicy:
    """
    Declares the policy constraints for an executor.

    Policies are immutable rules that govern executor behavior.
    Executors MUST NOT override or relax policies.

    Attributes:
        command_allowlist: Allowed commands for shell executors (empty = allow none).
        domain_allowlist: Allowed domains for Playwright executors (empty = allow none).
        file_access_patterns: Allowed file path patterns for context-aware executors.
        timeout_seconds: Maximum execution timeout.
        max_output_bytes: Maximum output size in bytes.
        max_context_tokens: Maximum context tokens for context-aware executors.
    """

    command_allowlist: FrozenSet[str] = field(default_factory=frozenset)
    domain_allowlist: FrozenSet[str] = field(default_factory=frozenset)
    file_access_patterns: FrozenSet[str] = field(default_factory=frozenset)
    timeout_seconds: int = 300
    max_output_bytes: int = 1024 * 1024  # 1MB
    max_context_tokens: int = 8000

    def __post_init__(self) -> None:
        """Validate policy."""
        if self.timeout_seconds <= 0:
            raise ValueError(f"timeout_seconds must be > 0, got: {self.timeout_seconds}")
        if self.max_output_bytes <= 0:
            raise ValueError(f"max_output_bytes must be > 0, got: {self.max_output_bytes}")
        if self.max_context_tokens <= 0:
            raise ValueError(f"max_context_tokens must be > 0, got: {self.max_context_tokens}")

    def allows_command(self, command: str) -> bool:
        """
        Check if a command is allowed by policy.

        Args:
            command: The base command to check.

        Returns:
            True if command is in allowlist, False otherwise.
        """
        if not self.command_allowlist:
            return False
        base_command = command.split()[0] if command else ""
        return base_command in self.command_allowlist

    def allows_domain(self, domain: str) -> bool:
        """
        Check if a domain is allowed by policy.

        Args:
            domain: The domain to check.

        Returns:
            True if domain is in allowlist, False otherwise.
        """
        if not self.domain_allowlist:
            return False
        return domain in self.domain_allowlist

    def allows_file_access(self, file_path: str) -> bool:
        """
        Check if a file path is allowed by policy.

        Args:
            file_path: The file path to check.

        Returns:
            True if file matches any allowed pattern.
        """
        if not self.file_access_patterns:
            return False
        # Simple prefix matching for now
        for pattern in self.file_access_patterns:
            if file_path.startswith(pattern):
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "command_allowlist": list(self.command_allowlist),
            "domain_allowlist": list(self.domain_allowlist),
            "file_access_patterns": list(self.file_access_patterns),
            "timeout_seconds": self.timeout_seconds,
            "max_output_bytes": self.max_output_bytes,
            "max_context_tokens": self.max_context_tokens,
        }


# =============================================================================
# EXECUTOR DEFINITION
# =============================================================================


@dataclass(frozen=True)
class ExecutorDefinition:
    """
    Complete definition of an executor.

    This is the main data structure that describes an executor's identity,
    type, cognition level, capabilities, and policies.

    All fields are immutable. Definitions cannot be modified at runtime.

    Attributes:
        id: Unique executor identifier.
        name: Human-readable name.
        executor_type: LOCAL or REMOTE.
        cognition_level: LEVEL_0_DUMB or LEVEL_1_CONTEXT_AWARE.
        capabilities: What the executor can do.
        policy: What the executor is allowed to do.
        enabled: Whether the executor is available for use.
        priority: Selection priority (lower = preferred, for stable ordering).
        metadata: Additional human-provided metadata.
    """

    id: ExecutorId
    name: str
    executor_type: ExecutorType
    cognition_level: ExecutorCognitionLevel
    capabilities: ExecutorCapabilities
    policy: ExecutorPolicy
    enabled: bool = True
    priority: int = 100  # Lower = higher priority
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate definition."""
        if not self.name:
            raise ValueError("Executor name cannot be empty")
        if self.priority < 0:
            raise ValueError(f"priority must be >= 0, got: {self.priority}")

        # Validate cognition level matches capabilities
        if self.cognition_level == ExecutorCognitionLevel.LEVEL_1_CONTEXT_AWARE:
            if BackendType.CONTEXT_AWARE not in self.capabilities.supported_backends:
                raise ValueError(
                    "LEVEL_1_CONTEXT_AWARE executor must support CONTEXT_AWARE backend"
                )

    def is_compatible_with_backend(self, backend: BackendType) -> bool:
        """Check if executor is compatible with a backend type."""
        return self.enabled and self.capabilities.supports_backend(backend)

    def is_compatible_with_task_type(self, task_type: SupportedTaskType) -> bool:
        """Check if executor is compatible with a task type."""
        return self.enabled and self.capabilities.supports_task_type(task_type)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "executor_type": self.executor_type.value,
            "cognition_level": self.cognition_level.value,
            "capabilities": self.capabilities.to_dict(),
            "policy": self.policy.to_dict(),
            "enabled": self.enabled,
            "priority": self.priority,
            "metadata": self.metadata,
        }


# =============================================================================
# TASK REQUIREMENTS
# =============================================================================


@dataclass(frozen=True)
class TaskExecutionRequirements:
    """
    Declares what a task requires from an executor.

    This is matched against ExecutorDefinition to find compatible executors.

    Attributes:
        required_backend: The backend type needed.
        required_task_type: The task type being executed.
        required_cognition_level: Minimum cognition level needed (None = any).
        required_operation: Operation type for context-aware tasks.
        files_to_access: Files the task will access (for policy validation).
        command: Command to execute (for shell policy validation).
        domain: Domain to access (for playwright policy validation).
        estimated_timeout: Estimated execution time in seconds.
        estimated_output_bytes: Estimated output size in bytes.
    """

    required_backend: BackendType
    required_task_type: SupportedTaskType = SupportedTaskType.EXECUTION
    required_cognition_level: Optional[ExecutorCognitionLevel] = None
    required_operation: Optional[AllowedOperation] = None
    files_to_access: FrozenSet[str] = field(default_factory=frozenset)
    command: Optional[str] = None
    domain: Optional[str] = None
    estimated_timeout: int = 60
    estimated_output_bytes: int = 10_000

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "required_backend": self.required_backend.value,
            "required_task_type": self.required_task_type.value,
            "required_cognition_level": (
                self.required_cognition_level.value if self.required_cognition_level else None
            ),
            "required_operation": (
                self.required_operation.value if self.required_operation else None
            ),
            "files_to_access": list(self.files_to_access),
            "command": self.command,
            "domain": self.domain,
            "estimated_timeout": self.estimated_timeout,
            "estimated_output_bytes": self.estimated_output_bytes,
        }


# =============================================================================
# CAPABILITY MATCH RESULT
# =============================================================================


class CapabilityMatchStatus(str, Enum):
    """
    Result of matching task requirements to executor capabilities.
    """

    COMPATIBLE = "compatible"
    INCOMPATIBLE_BACKEND = "incompatible_backend"
    INCOMPATIBLE_TASK_TYPE = "incompatible_task_type"
    INCOMPATIBLE_COGNITION = "incompatible_cognition"
    INCOMPATIBLE_OPERATION = "incompatible_operation"
    POLICY_VIOLATION_COMMAND = "policy_violation_command"
    POLICY_VIOLATION_DOMAIN = "policy_violation_domain"
    POLICY_VIOLATION_FILE_ACCESS = "policy_violation_file_access"
    POLICY_VIOLATION_TIMEOUT = "policy_violation_timeout"
    POLICY_VIOLATION_OUTPUT_SIZE = "policy_violation_output_size"
    EXECUTOR_DISABLED = "executor_disabled"


@dataclass(frozen=True)
class CapabilityMatchResult:
    """
    Result of matching task requirements to an executor.

    Attributes:
        executor_id: The executor that was checked.
        status: The match status.
        message: Human-readable explanation.
    """

    executor_id: ExecutorId
    status: CapabilityMatchStatus
    message: str = ""

    @property
    def is_compatible(self) -> bool:
        """Check if the match is compatible."""
        return self.status == CapabilityMatchStatus.COMPATIBLE

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "executor_id": str(self.executor_id),
            "status": self.status.value,
            "message": self.message,
        }


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================


def create_shell_executor(
    executor_id: str,
    name: str,
    command_allowlist: FrozenSet[str],
    priority: int = 100,
    timeout_seconds: int = 300,
) -> ExecutorDefinition:
    """
    Create a shell executor definition.

    Args:
        executor_id: Unique identifier.
        name: Human-readable name.
        command_allowlist: Allowed shell commands.
        priority: Selection priority.
        timeout_seconds: Execution timeout.

    Returns:
        ExecutorDefinition for a shell executor.
    """
    return ExecutorDefinition(
        id=ExecutorId(executor_id),
        name=name,
        executor_type=ExecutorType.LOCAL,
        cognition_level=ExecutorCognitionLevel.LEVEL_0_DUMB,
        capabilities=ExecutorCapabilities(
            supported_backends=frozenset({BackendType.SHELL}),
            supported_task_types=frozenset({SupportedTaskType.EXECUTION}),
        ),
        policy=ExecutorPolicy(
            command_allowlist=command_allowlist,
            timeout_seconds=timeout_seconds,
        ),
        priority=priority,
    )


def create_playwright_executor(
    executor_id: str,
    name: str,
    domain_allowlist: FrozenSet[str],
    priority: int = 100,
    timeout_seconds: int = 300,
) -> ExecutorDefinition:
    """
    Create a Playwright executor definition.

    Args:
        executor_id: Unique identifier.
        name: Human-readable name.
        domain_allowlist: Allowed domains.
        priority: Selection priority.
        timeout_seconds: Execution timeout.

    Returns:
        ExecutorDefinition for a Playwright executor.
    """
    return ExecutorDefinition(
        id=ExecutorId(executor_id),
        name=name,
        executor_type=ExecutorType.LOCAL,
        cognition_level=ExecutorCognitionLevel.LEVEL_0_DUMB,
        capabilities=ExecutorCapabilities(
            supported_backends=frozenset({BackendType.PLAYWRIGHT}),
            supported_task_types=frozenset({SupportedTaskType.EXECUTION, SupportedTaskType.DISCOVERY}),
        ),
        policy=ExecutorPolicy(
            domain_allowlist=domain_allowlist,
            timeout_seconds=timeout_seconds,
        ),
        priority=priority,
    )


def create_context_aware_executor(
    executor_id: str,
    name: str,
    file_access_patterns: FrozenSet[str],
    allowed_operations: FrozenSet[AllowedOperation],
    priority: int = 100,
    max_patch_size: int = 50_000,
    max_context_tokens: int = 8000,
    timeout_seconds: int = 120,
) -> ExecutorDefinition:
    """
    Create a context-aware executor definition.

    Args:
        executor_id: Unique identifier.
        name: Human-readable name.
        file_access_patterns: Allowed file path patterns.
        allowed_operations: Allowed operations (READ/EDIT).
        priority: Selection priority.
        max_patch_size: Maximum patch size in bytes.
        max_context_tokens: Maximum context tokens.
        timeout_seconds: Execution timeout.

    Returns:
        ExecutorDefinition for a context-aware executor.
    """
    return ExecutorDefinition(
        id=ExecutorId(executor_id),
        name=name,
        executor_type=ExecutorType.LOCAL,
        cognition_level=ExecutorCognitionLevel.LEVEL_1_CONTEXT_AWARE,
        capabilities=ExecutorCapabilities(
            supported_backends=frozenset({BackendType.CONTEXT_AWARE}),
            supported_task_types=frozenset({SupportedTaskType.EXECUTION, SupportedTaskType.DISCOVERY}),
            max_patch_size=max_patch_size,
            allowed_operations=allowed_operations,
        ),
        policy=ExecutorPolicy(
            file_access_patterns=file_access_patterns,
            max_context_tokens=max_context_tokens,
            timeout_seconds=timeout_seconds,
        ),
        priority=priority,
    )
