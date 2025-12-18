"""
Remote Executor Protocol for Axiom Forge.

This module defines the strict request/response protocol for remote execution.
Remote executors are still executors — they add transport, not reasoning.

CORE PRINCIPLES (ABSOLUTE):
    1. Remote executors are NOT agents
    2. No planning, no reasoning, no approval
    3. One task per request
    4. No background workers or queues
    5. No persistent state
    6. All policies enforced locally
    7. Canon and planning layers are inaccessible

PROTOCOL RULES:
    - All fields must be JSON-serializable
    - No partial responses
    - No streaming
    - No batching

Any violation of these principles is a hard failure.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List
import json
import hashlib
import uuid


# =============================================================================
# PROTOCOL STATUS
# =============================================================================


class RemoteExecutionStatus(str, Enum):
    """
    Status of a remote execution request.

    SUCCESS: Execution completed (check result for task outcome).
    AUTH_FAILED: Authentication failed, execution rejected.
    VALIDATION_FAILED: Request validation failed.
    POLICY_VIOLATION: Policy enforcement blocked execution.
    EXECUTION_ERROR: Execution attempted but failed.
    TRANSPORT_ERROR: Network or serialization error.
    """

    SUCCESS = "success"
    AUTH_FAILED = "auth_failed"
    VALIDATION_FAILED = "validation_failed"
    POLICY_VIOLATION = "policy_violation"
    EXECUTION_ERROR = "execution_error"
    TRANSPORT_ERROR = "transport_error"


class RemoteBackendType(str, Enum):
    """
    Backend type declaration for remote execution.

    The remote stub validates this matches its configured capability.
    """

    SHELL = "shell"
    PLAYWRIGHT = "playwright"
    CONTEXT_AWARE = "context_aware"


# =============================================================================
# AUTHENTICATION METADATA
# =============================================================================


@dataclass(frozen=True)
class AuthenticationMetadata:
    """
    Authentication information for a remote execution request.

    Uses static token-based authentication only.
    No OAuth, no sessions, no refresh tokens.

    Attributes:
        token: Static authentication token.
        request_timestamp: ISO 8601 timestamp of request creation.
        request_nonce: Unique nonce to prevent replay attacks.
    """

    token: str
    request_timestamp: str
    request_nonce: str

    def __post_init__(self) -> None:
        """Validate authentication metadata."""
        if not self.token:
            raise ValueError("Authentication token cannot be empty")
        if not self.request_timestamp:
            raise ValueError("Request timestamp cannot be empty")
        if not self.request_nonce:
            raise ValueError("Request nonce cannot be empty")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON transport."""
        return {
            "token": self.token,
            "request_timestamp": self.request_timestamp,
            "request_nonce": self.request_nonce,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuthenticationMetadata":
        """Deserialize from dictionary."""
        return cls(
            token=data["token"],
            request_timestamp=data["request_timestamp"],
            request_nonce=data["request_nonce"],
        )

    @classmethod
    def create(cls, token: str) -> "AuthenticationMetadata":
        """
        Create authentication metadata with current timestamp and unique nonce.

        Args:
            token: The authentication token.

        Returns:
            AuthenticationMetadata with generated timestamp and nonce.
        """
        return cls(
            token=token,
            request_timestamp=datetime.utcnow().isoformat() + "Z",
            request_nonce=uuid.uuid4().hex,
        )


# =============================================================================
# SERIALIZED TASK INPUT
# =============================================================================


@dataclass(frozen=True)
class SerializedTaskInput:
    """
    Serialized representation of TaskExecutionInput for transport.

    All fields are primitive types suitable for JSON serialization.

    Attributes:
        task_id: Unique task identifier.
        command: The command to execute.
        args: Command arguments.
        env: Environment variables (filtered for security).
        working_directory: Execution working directory.
        timeout_seconds: Execution timeout.
        metadata: Additional task metadata.
    """

    task_id: str
    command: str
    args: tuple  # Tuple for immutability, serialized as list
    env: tuple  # Tuple of (key, value) pairs, serialized as dict
    working_directory: Optional[str]
    timeout_seconds: int
    metadata: tuple  # Tuple of (key, value) pairs, serialized as dict

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON transport."""
        return {
            "task_id": self.task_id,
            "command": self.command,
            "args": list(self.args),
            "env": dict(self.env),
            "working_directory": self.working_directory,
            "timeout_seconds": self.timeout_seconds,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SerializedTaskInput":
        """Deserialize from dictionary."""
        return cls(
            task_id=data["task_id"],
            command=data["command"],
            args=tuple(data.get("args", [])),
            env=tuple(data.get("env", {}).items()),
            working_directory=data.get("working_directory"),
            timeout_seconds=data.get("timeout_seconds", 300),
            metadata=tuple(data.get("metadata", {}).items()),
        )

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), sort_keys=True)

    @classmethod
    def from_json(cls, json_str: str) -> "SerializedTaskInput":
        """Deserialize from JSON string."""
        return cls.from_dict(json.loads(json_str))

    def content_hash(self) -> str:
        """
        Compute content hash for integrity verification.

        Returns:
            SHA-256 hash of the serialized content.
        """
        return hashlib.sha256(self.to_json().encode()).hexdigest()


# =============================================================================
# TASK REQUIREMENTS DECLARATION
# =============================================================================


@dataclass(frozen=True)
class DeclaredTaskRequirements:
    """
    Declared requirements for task execution.

    These requirements are validated by the remote stub before execution.
    Any mismatch between declared and actual requirements causes rejection.

    Attributes:
        backend_type: Required backend (shell, playwright, context_aware).
        required_commands: Commands needed (for shell policy validation).
        required_domains: Domains needed (for playwright policy validation).
        required_files: File patterns needed (for context-aware validation).
        estimated_timeout: Expected execution time in seconds.
    """

    backend_type: RemoteBackendType
    required_commands: tuple = ()  # Tuple of command strings
    required_domains: tuple = ()  # Tuple of domain strings
    required_files: tuple = ()  # Tuple of file path patterns
    estimated_timeout: int = 60

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON transport."""
        return {
            "backend_type": self.backend_type.value,
            "required_commands": list(self.required_commands),
            "required_domains": list(self.required_domains),
            "required_files": list(self.required_files),
            "estimated_timeout": self.estimated_timeout,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeclaredTaskRequirements":
        """Deserialize from dictionary."""
        return cls(
            backend_type=RemoteBackendType(data["backend_type"]),
            required_commands=tuple(data.get("required_commands", [])),
            required_domains=tuple(data.get("required_domains", [])),
            required_files=tuple(data.get("required_files", [])),
            estimated_timeout=data.get("estimated_timeout", 60),
        )


# =============================================================================
# REMOTE EXECUTION REQUEST
# =============================================================================


@dataclass(frozen=True)
class RemoteExecutionRequest:
    """
    Request for remote task execution.

    This is the complete, self-contained request sent to a remote executor stub.
    All information needed for execution must be included.

    PROTOCOL RULES:
    - Exactly ONE task per request
    - No batching
    - No streaming
    - All fields JSON-serializable

    Attributes:
        request_id: Unique identifier for this request.
        executor_id: Target executor identifier.
        task_input: Serialized task execution input.
        requirements: Declared task requirements.
        auth: Authentication metadata.
        protocol_version: Protocol version for compatibility checking.
    """

    request_id: str
    executor_id: str
    task_input: SerializedTaskInput
    requirements: DeclaredTaskRequirements
    auth: AuthenticationMetadata
    protocol_version: str = "1.0.0"

    def __post_init__(self) -> None:
        """Validate request structure."""
        if not self.request_id:
            raise ValueError("Request ID cannot be empty")
        if not self.executor_id:
            raise ValueError("Executor ID cannot be empty")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON transport."""
        return {
            "request_id": self.request_id,
            "executor_id": self.executor_id,
            "task_input": self.task_input.to_dict(),
            "requirements": self.requirements.to_dict(),
            "auth": self.auth.to_dict(),
            "protocol_version": self.protocol_version,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RemoteExecutionRequest":
        """Deserialize from dictionary."""
        return cls(
            request_id=data["request_id"],
            executor_id=data["executor_id"],
            task_input=SerializedTaskInput.from_dict(data["task_input"]),
            requirements=DeclaredTaskRequirements.from_dict(data["requirements"]),
            auth=AuthenticationMetadata.from_dict(data["auth"]),
            protocol_version=data.get("protocol_version", "1.0.0"),
        )

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), sort_keys=True)

    @classmethod
    def from_json(cls, json_str: str) -> "RemoteExecutionRequest":
        """Deserialize from JSON string."""
        return cls.from_dict(json.loads(json_str))

    def content_hash(self) -> str:
        """
        Compute content hash for integrity verification.

        Does not include auth token in hash for security.

        Returns:
            SHA-256 hash of request content (excluding auth token).
        """
        hashable = {
            "request_id": self.request_id,
            "executor_id": self.executor_id,
            "task_input": self.task_input.to_dict(),
            "requirements": self.requirements.to_dict(),
            "protocol_version": self.protocol_version,
        }
        return hashlib.sha256(
            json.dumps(hashable, sort_keys=True).encode()
        ).hexdigest()

    @classmethod
    def create(
        cls,
        executor_id: str,
        task_input: SerializedTaskInput,
        requirements: DeclaredTaskRequirements,
        auth_token: str,
    ) -> "RemoteExecutionRequest":
        """
        Create a new remote execution request with generated ID.

        Args:
            executor_id: Target executor identifier.
            task_input: Serialized task input.
            requirements: Task requirements declaration.
            auth_token: Authentication token.

        Returns:
            New RemoteExecutionRequest with unique ID.
        """
        return cls(
            request_id=f"req-{uuid.uuid4().hex}",
            executor_id=executor_id,
            task_input=task_input,
            requirements=requirements,
            auth=AuthenticationMetadata.create(auth_token),
        )


# =============================================================================
# SERIALIZED EXECUTION RESULT
# =============================================================================


@dataclass(frozen=True)
class SerializedExecutionResult:
    """
    Serialized representation of TaskExecutionResult for transport.

    All fields are primitive types suitable for JSON serialization.

    Attributes:
        task_id: Task identifier.
        state: Execution state (succeeded, failed, etc.).
        exit_code: Process exit code (if applicable).
        stdout: Standard output (truncated if over limit).
        stderr: Standard error (truncated if over limit).
        failure_reason: Failure category (if failed).
        error_message: Human-readable error message.
        metadata: Additional result metadata.
        timestamp: ISO 8601 execution timestamp.
    """

    task_id: str
    state: str
    exit_code: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    failure_reason: Optional[str] = None
    error_message: Optional[str] = None
    metadata: tuple = ()  # Tuple of (key, value) pairs
    timestamp: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON transport."""
        return {
            "task_id": self.task_id,
            "state": self.state,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "failure_reason": self.failure_reason,
            "error_message": self.error_message,
            "metadata": dict(self.metadata),
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SerializedExecutionResult":
        """Deserialize from dictionary."""
        return cls(
            task_id=data["task_id"],
            state=data["state"],
            exit_code=data.get("exit_code"),
            stdout=data.get("stdout"),
            stderr=data.get("stderr"),
            failure_reason=data.get("failure_reason"),
            error_message=data.get("error_message"),
            metadata=tuple(data.get("metadata", {}).items()),
            timestamp=data.get("timestamp"),
        )


# =============================================================================
# POLICY ENFORCEMENT REPORT
# =============================================================================


@dataclass(frozen=True)
class PolicyEnforcementReport:
    """
    Report of policy enforcement during remote execution.

    Documents which policies were checked and their outcomes.
    This provides an audit trail for security review.

    Attributes:
        checks_performed: List of policy checks performed.
        violations_detected: List of policy violations (if any).
        all_passed: True if all policy checks passed.
    """

    checks_performed: tuple  # Tuple of check names
    violations_detected: tuple  # Tuple of violation descriptions
    all_passed: bool

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON transport."""
        return {
            "checks_performed": list(self.checks_performed),
            "violations_detected": list(self.violations_detected),
            "all_passed": self.all_passed,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PolicyEnforcementReport":
        """Deserialize from dictionary."""
        return cls(
            checks_performed=tuple(data.get("checks_performed", [])),
            violations_detected=tuple(data.get("violations_detected", [])),
            all_passed=data.get("all_passed", False),
        )

    @classmethod
    def passed(cls, checks: List[str]) -> "PolicyEnforcementReport":
        """Create a report indicating all checks passed."""
        return cls(
            checks_performed=tuple(checks),
            violations_detected=(),
            all_passed=True,
        )

    @classmethod
    def failed(cls, checks: List[str], violations: List[str]) -> "PolicyEnforcementReport":
        """Create a report indicating policy violations."""
        return cls(
            checks_performed=tuple(checks),
            violations_detected=tuple(violations),
            all_passed=False,
        )


# =============================================================================
# EXECUTION METADATA
# =============================================================================


@dataclass(frozen=True)
class ExecutionMetadata:
    """
    Metadata about the execution environment and timing.

    Provides audit information about where and when execution occurred.

    Attributes:
        executor_version: Version of the remote executor stub.
        execution_start: ISO 8601 timestamp of execution start.
        execution_end: ISO 8601 timestamp of execution end.
        execution_duration_ms: Duration in milliseconds.
        executor_host: Hostname of executor (sanitized).
    """

    executor_version: str
    execution_start: str
    execution_end: str
    execution_duration_ms: int
    executor_host: str = "remote"  # Sanitized hostname

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON transport."""
        return {
            "executor_version": self.executor_version,
            "execution_start": self.execution_start,
            "execution_end": self.execution_end,
            "execution_duration_ms": self.execution_duration_ms,
            "executor_host": self.executor_host,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionMetadata":
        """Deserialize from dictionary."""
        return cls(
            executor_version=data["executor_version"],
            execution_start=data["execution_start"],
            execution_end=data["execution_end"],
            execution_duration_ms=data["execution_duration_ms"],
            executor_host=data.get("executor_host", "remote"),
        )


# =============================================================================
# REMOTE EXECUTION RESPONSE
# =============================================================================


@dataclass(frozen=True)
class RemoteExecutionResponse:
    """
    Response from a remote task execution.

    This is the complete response from a remote executor stub.
    Contains execution result, metadata, and policy enforcement report.

    PROTOCOL RULES:
    - Response is complete (no partial responses)
    - Response is final (no updates)
    - All fields JSON-serializable

    Attributes:
        request_id: Matches the request ID.
        status: Overall status of the remote execution.
        result: Serialized execution result (if execution attempted).
        execution_metadata: Timing and environment metadata.
        policy_report: Policy enforcement audit trail.
        error_message: Error details (if status is not SUCCESS).
        protocol_version: Protocol version.
    """

    request_id: str
    status: RemoteExecutionStatus
    result: Optional[SerializedExecutionResult] = None
    execution_metadata: Optional[ExecutionMetadata] = None
    policy_report: Optional[PolicyEnforcementReport] = None
    error_message: Optional[str] = None
    protocol_version: str = "1.0.0"

    def __post_init__(self) -> None:
        """Validate response structure."""
        if not self.request_id:
            raise ValueError("Request ID cannot be empty")

    @property
    def succeeded(self) -> bool:
        """Check if remote execution succeeded."""
        return self.status == RemoteExecutionStatus.SUCCESS

    @property
    def failed(self) -> bool:
        """Check if remote execution failed."""
        return not self.succeeded

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON transport."""
        return {
            "request_id": self.request_id,
            "status": self.status.value,
            "result": self.result.to_dict() if self.result else None,
            "execution_metadata": (
                self.execution_metadata.to_dict() if self.execution_metadata else None
            ),
            "policy_report": (
                self.policy_report.to_dict() if self.policy_report else None
            ),
            "error_message": self.error_message,
            "protocol_version": self.protocol_version,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RemoteExecutionResponse":
        """Deserialize from dictionary."""
        return cls(
            request_id=data["request_id"],
            status=RemoteExecutionStatus(data["status"]),
            result=(
                SerializedExecutionResult.from_dict(data["result"])
                if data.get("result")
                else None
            ),
            execution_metadata=(
                ExecutionMetadata.from_dict(data["execution_metadata"])
                if data.get("execution_metadata")
                else None
            ),
            policy_report=(
                PolicyEnforcementReport.from_dict(data["policy_report"])
                if data.get("policy_report")
                else None
            ),
            error_message=data.get("error_message"),
            protocol_version=data.get("protocol_version", "1.0.0"),
        )

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), sort_keys=True)

    @classmethod
    def from_json(cls, json_str: str) -> "RemoteExecutionResponse":
        """Deserialize from JSON string."""
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def auth_failed(cls, request_id: str) -> "RemoteExecutionResponse":
        """Create an authentication failure response."""
        return cls(
            request_id=request_id,
            status=RemoteExecutionStatus.AUTH_FAILED,
            error_message="Authentication failed",
        )

    @classmethod
    def validation_failed(
        cls, request_id: str, message: str
    ) -> "RemoteExecutionResponse":
        """Create a validation failure response."""
        return cls(
            request_id=request_id,
            status=RemoteExecutionStatus.VALIDATION_FAILED,
            error_message=f"Validation failed: {message}",
        )

    @classmethod
    def policy_violation(
        cls, request_id: str, report: PolicyEnforcementReport
    ) -> "RemoteExecutionResponse":
        """Create a policy violation response."""
        return cls(
            request_id=request_id,
            status=RemoteExecutionStatus.POLICY_VIOLATION,
            policy_report=report,
            error_message=f"Policy violations: {', '.join(report.violations_detected)}",
        )

    @classmethod
    def execution_error(
        cls, request_id: str, message: str
    ) -> "RemoteExecutionResponse":
        """Create an execution error response."""
        return cls(
            request_id=request_id,
            status=RemoteExecutionStatus.EXECUTION_ERROR,
            error_message=f"Execution error: {message}",
        )

    @classmethod
    def transport_error(
        cls, request_id: str, message: str
    ) -> "RemoteExecutionResponse":
        """Create a transport error response."""
        return cls(
            request_id=request_id,
            status=RemoteExecutionStatus.TRANSPORT_ERROR,
            error_message=f"Transport error: {message}",
        )


# =============================================================================
# SERIALIZATION UTILITIES
# =============================================================================


def serialize_task_input(
    task_id: str,
    command: str,
    args: List[str],
    env: Dict[str, str],
    working_directory: Optional[str],
    timeout_seconds: int,
    metadata: Dict[str, Any],
) -> SerializedTaskInput:
    """
    Create a serialized task input from individual components.

    Args:
        task_id: Task identifier.
        command: Command to execute.
        args: Command arguments.
        env: Environment variables.
        working_directory: Working directory.
        timeout_seconds: Timeout.
        metadata: Additional metadata.

    Returns:
        SerializedTaskInput ready for transport.
    """
    return SerializedTaskInput(
        task_id=task_id,
        command=command,
        args=tuple(args),
        env=tuple(env.items()),
        working_directory=working_directory,
        timeout_seconds=timeout_seconds,
        metadata=tuple(metadata.items()),
    )


def deserialize_to_task_execution_input(
    serialized: SerializedTaskInput,
) -> "TaskExecutionInput":
    """
    Convert serialized task input to TaskExecutionInput.

    Args:
        serialized: Serialized task input.

    Returns:
        TaskExecutionInput for execution.
    """
    from axiom_forge.backend import TaskExecutionInput

    return TaskExecutionInput(
        task_id=serialized.task_id,
        command=serialized.command,
        args=list(serialized.args),
        env=dict(serialized.env),
        working_directory=serialized.working_directory,
        timeout_seconds=serialized.timeout_seconds,
        metadata=dict(serialized.metadata),
    )


def serialize_from_task_execution_input(
    input_data: "TaskExecutionInput",
) -> SerializedTaskInput:
    """
    Convert TaskExecutionInput to serialized form.

    Args:
        input_data: Task execution input.

    Returns:
        SerializedTaskInput for transport.
    """
    return SerializedTaskInput(
        task_id=input_data.task_id,
        command=input_data.command,
        args=tuple(input_data.args),
        env=tuple(input_data.env.items()),
        working_directory=input_data.working_directory,
        timeout_seconds=input_data.timeout_seconds,
        metadata=tuple(input_data.metadata.items()),
    )
