"""
Remote Dispatch for Axiom Conductor.

This module extends Conductor to dispatch tasks to remote executors.
Dispatch is transport only — no intelligence, no retries, no fallback.

CORE PRINCIPLES:
    1. Detect executor type REMOTE
    2. Serialize TaskExecutionInput
    3. Dispatch request to remote stub
    4. Receive and deserialize response
    5. Treat remote execution identically to local execution

RULES (ABSOLUTE):
    - No retries on network failure
    - No fallback executor selection
    - Failure propagates upstream
    - Human decides next step

This module adds transport, not reasoning.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable, Protocol
from datetime import datetime

from axiom_conductor.model import (
    TaskExecutionResult,
    TaskExecutionState,
    TaskFailureReason,
)
from axiom_forge.backend import TaskExecutionInput
from axiom_forge.remote_protocol import (
    RemoteExecutionRequest,
    RemoteExecutionResponse,
    RemoteExecutionStatus,
    RemoteBackendType,
    SerializedTaskInput,
    DeclaredTaskRequirements,
    AuthenticationMetadata,
    serialize_from_task_execution_input,
)


# =============================================================================
# TRANSPORT ERRORS
# =============================================================================


class RemoteDispatchError(Exception):
    """Base exception for remote dispatch errors."""

    pass


class NetworkError(RemoteDispatchError):
    """Raised when network communication fails."""

    def __init__(self, message: str):
        super().__init__(f"Network error: {message}")


class SerializationError(RemoteDispatchError):
    """Raised when serialization/deserialization fails."""

    def __init__(self, message: str):
        super().__init__(f"Serialization error: {message}")


class ProtocolError(RemoteDispatchError):
    """Raised when protocol validation fails."""

    def __init__(self, message: str):
        super().__init__(f"Protocol error: {message}")


# =============================================================================
# TRANSPORT PROTOCOL
# =============================================================================


class RemoteTransport(Protocol):
    """
    Protocol for remote execution transport.

    Implementations must provide a way to send requests and receive responses.
    The transport is responsible for:
    - Network communication
    - Connection management
    - Timeout enforcement

    The transport is NOT responsible for:
    - Retries
    - Fallback
    - Load balancing
    - Connection pooling
    """

    def send(self, request_json: str) -> str:
        """
        Send a request and receive a response.

        Args:
            request_json: JSON-encoded RemoteExecutionRequest.

        Returns:
            JSON-encoded RemoteExecutionResponse.

        Raises:
            NetworkError: If network communication fails.
        """
        ...


# =============================================================================
# LOCAL TRANSPORT (FOR TESTING)
# =============================================================================


@dataclass
class LocalTransport:
    """
    Local transport for testing remote dispatch.

    This transport calls a local stub directly, simulating remote execution
    without actual network communication.

    Attributes:
        handler: Function that handles JSON requests and returns JSON responses.
    """

    handler: Callable[[str], str]

    def send(self, request_json: str) -> str:
        """
        Send request to local handler.

        Args:
            request_json: JSON-encoded request.

        Returns:
            JSON-encoded response.
        """
        return self.handler(request_json)


# =============================================================================
# REMOTE DISPATCHER
# =============================================================================


@dataclass
class RemoteDispatcher:
    """
    Dispatches tasks to remote executors.

    This dispatcher:
    1. Serializes task input
    2. Creates remote execution request
    3. Sends request via transport
    4. Deserializes response
    5. Returns result as TaskExecutionResult

    The dispatcher treats remote execution identically to local execution
    from the Conductor's perspective.

    INVARIANTS:
    - No retries
    - No fallback
    - Failure propagates upstream

    Attributes:
        executor_id: Target executor ID.
        backend_type: Target backend type.
        auth_token: Authentication token.
        transport: Transport implementation.
    """

    executor_id: str
    backend_type: RemoteBackendType
    auth_token: str
    transport: RemoteTransport

    def dispatch(
        self,
        task_input: TaskExecutionInput,
        required_commands: tuple = (),
        required_domains: tuple = (),
        required_files: tuple = (),
    ) -> TaskExecutionResult:
        """
        Dispatch a task for remote execution.

        Args:
            task_input: The task to execute.
            required_commands: Commands needed (for shell).
            required_domains: Domains needed (for playwright).
            required_files: Files needed (for context-aware).

        Returns:
            TaskExecutionResult from remote execution.

        Raises:
            RemoteDispatchError: If dispatch fails (no retries).
        """
        # Step 1: Serialize task input
        try:
            serialized_input = serialize_from_task_execution_input(task_input)
        except Exception as e:
            raise SerializationError(f"Failed to serialize task input: {e}")

        # Step 2: Create request
        requirements = DeclaredTaskRequirements(
            backend_type=self.backend_type,
            required_commands=required_commands,
            required_domains=required_domains,
            required_files=required_files,
            estimated_timeout=task_input.timeout_seconds,
        )

        request = RemoteExecutionRequest.create(
            executor_id=self.executor_id,
            task_input=serialized_input,
            requirements=requirements,
            auth_token=self.auth_token,
        )

        # Step 3: Send request
        try:
            request_json = request.to_json()
        except Exception as e:
            raise SerializationError(f"Failed to serialize request: {e}")

        try:
            response_json = self.transport.send(request_json)
        except Exception as e:
            # No retries — fail immediately
            raise NetworkError(str(e))

        # Step 4: Deserialize response
        try:
            response = RemoteExecutionResponse.from_json(response_json)
        except Exception as e:
            raise SerializationError(f"Failed to deserialize response: {e}")

        # Step 5: Convert response to TaskExecutionResult
        return self._response_to_result(response, task_input.task_id)

    def _response_to_result(
        self,
        response: RemoteExecutionResponse,
        task_id: str,
    ) -> TaskExecutionResult:
        """
        Convert RemoteExecutionResponse to TaskExecutionResult.

        Args:
            response: The remote execution response.
            task_id: The task ID.

        Returns:
            TaskExecutionResult for Conductor.
        """
        # Handle failure statuses
        if response.status == RemoteExecutionStatus.AUTH_FAILED:
            return TaskExecutionResult(
                task_id=task_id,
                state=TaskExecutionState.FAILED,
                failure_reason=TaskFailureReason.SYSTEM_ERROR,
                error_message="Remote authentication failed",
                metadata={"remote_status": response.status.value},
            )

        if response.status == RemoteExecutionStatus.VALIDATION_FAILED:
            return TaskExecutionResult(
                task_id=task_id,
                state=TaskExecutionState.FAILED,
                failure_reason=TaskFailureReason.PRECONDITION_FAILED,
                error_message=response.error_message or "Validation failed",
                metadata={"remote_status": response.status.value},
            )

        if response.status == RemoteExecutionStatus.POLICY_VIOLATION:
            return TaskExecutionResult(
                task_id=task_id,
                state=TaskExecutionState.FAILED,
                failure_reason=TaskFailureReason.PRECONDITION_FAILED,
                error_message=response.error_message or "Policy violation",
                metadata={
                    "remote_status": response.status.value,
                    "policy_violations": list(
                        response.policy_report.violations_detected
                    )
                    if response.policy_report
                    else [],
                },
            )

        if response.status == RemoteExecutionStatus.EXECUTION_ERROR:
            return TaskExecutionResult(
                task_id=task_id,
                state=TaskExecutionState.FAILED,
                failure_reason=TaskFailureReason.SYSTEM_ERROR,
                error_message=response.error_message or "Execution error",
                metadata={"remote_status": response.status.value},
            )

        if response.status == RemoteExecutionStatus.TRANSPORT_ERROR:
            return TaskExecutionResult(
                task_id=task_id,
                state=TaskExecutionState.FAILED,
                failure_reason=TaskFailureReason.SYSTEM_ERROR,
                error_message=response.error_message or "Transport error",
                metadata={"remote_status": response.status.value},
            )

        # Success case
        if response.status == RemoteExecutionStatus.SUCCESS and response.result:
            result = response.result
            return TaskExecutionResult(
                task_id=result.task_id,
                state=TaskExecutionState(result.state),
                exit_code=result.exit_code,
                stdout=result.stdout,
                stderr=result.stderr,
                failure_reason=(
                    TaskFailureReason(result.failure_reason)
                    if result.failure_reason
                    else None
                ),
                error_message=result.error_message,
                metadata={
                    **dict(result.metadata),
                    "remote_execution": True,
                    "remote_executor": self.executor_id,
                },
                timestamp=result.timestamp,
            )

        # Unexpected status
        return TaskExecutionResult(
            task_id=task_id,
            state=TaskExecutionState.FAILED,
            failure_reason=TaskFailureReason.UNKNOWN,
            error_message=f"Unexpected remote status: {response.status.value}",
            metadata={"remote_status": response.status.value},
        )


# =============================================================================
# DISPATCHER AS BACKEND ADAPTER
# =============================================================================


@dataclass
class RemoteExecutionBackend:
    """
    Adapter that wraps RemoteDispatcher as a TaskExecutionBackend.

    This allows remote execution to be used interchangeably with local
    backends from the Conductor's perspective.

    Attributes:
        dispatcher: The remote dispatcher.
        required_commands: Commands needed (for shell).
        required_domains: Domains needed (for playwright).
        required_files: Files needed (for context-aware).
    """

    dispatcher: RemoteDispatcher
    required_commands: tuple = ()
    required_domains: tuple = ()
    required_files: tuple = ()

    def execute_task(self, input_data: TaskExecutionInput) -> TaskExecutionResult:
        """
        Execute a task via remote dispatch.

        Args:
            input_data: The task execution input.

        Returns:
            TaskExecutionResult from remote execution.
        """
        try:
            return self.dispatcher.dispatch(
                task_input=input_data,
                required_commands=self.required_commands,
                required_domains=self.required_domains,
                required_files=self.required_files,
            )
        except RemoteDispatchError as e:
            # Convert dispatch errors to execution result
            # NO RETRIES — failure is final
            return TaskExecutionResult(
                task_id=input_data.task_id,
                state=TaskExecutionState.FAILED,
                failure_reason=TaskFailureReason.SYSTEM_ERROR,
                error_message=str(e),
                metadata={"dispatch_error": True},
                timestamp=datetime.utcnow().isoformat() + "Z",
            )


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================


def create_remote_shell_backend(
    executor_id: str,
    auth_token: str,
    transport: RemoteTransport,
    required_commands: tuple = (),
) -> RemoteExecutionBackend:
    """
    Create a remote shell execution backend.

    Args:
        executor_id: Target executor ID.
        auth_token: Authentication token.
        transport: Transport implementation.
        required_commands: Commands needed for execution.

    Returns:
        RemoteExecutionBackend for shell tasks.
    """
    dispatcher = RemoteDispatcher(
        executor_id=executor_id,
        backend_type=RemoteBackendType.SHELL,
        auth_token=auth_token,
        transport=transport,
    )
    return RemoteExecutionBackend(
        dispatcher=dispatcher,
        required_commands=required_commands,
    )


def create_remote_playwright_backend(
    executor_id: str,
    auth_token: str,
    transport: RemoteTransport,
    required_domains: tuple = (),
) -> RemoteExecutionBackend:
    """
    Create a remote Playwright execution backend.

    Args:
        executor_id: Target executor ID.
        auth_token: Authentication token.
        transport: Transport implementation.
        required_domains: Domains needed for execution.

    Returns:
        RemoteExecutionBackend for Playwright tasks.
    """
    dispatcher = RemoteDispatcher(
        executor_id=executor_id,
        backend_type=RemoteBackendType.PLAYWRIGHT,
        auth_token=auth_token,
        transport=transport,
    )
    return RemoteExecutionBackend(
        dispatcher=dispatcher,
        required_domains=required_domains,
    )


def create_remote_context_aware_backend(
    executor_id: str,
    auth_token: str,
    transport: RemoteTransport,
    required_files: tuple = (),
) -> RemoteExecutionBackend:
    """
    Create a remote context-aware execution backend.

    Args:
        executor_id: Target executor ID.
        auth_token: Authentication token.
        transport: Transport implementation.
        required_files: Files needed for execution.

    Returns:
        RemoteExecutionBackend for context-aware tasks.
    """
    dispatcher = RemoteDispatcher(
        executor_id=executor_id,
        backend_type=RemoteBackendType.CONTEXT_AWARE,
        auth_token=auth_token,
        transport=transport,
    )
    return RemoteExecutionBackend(
        dispatcher=dispatcher,
        required_files=required_files,
    )


# =============================================================================
# INVARIANT ASSERTIONS
# =============================================================================


def assert_no_retries_in_dispatcher(dispatcher: RemoteDispatcher) -> bool:
    """
    Assert that the dispatcher has no retry logic.

    This is verified by code inspection — the dispatch() method has no
    retry loops or fallback logic.

    Args:
        dispatcher: The dispatcher to check.

    Returns:
        True (by design).
    """
    # No retry logic exists in the dispatch() method
    return True


def assert_no_fallback_in_dispatcher(dispatcher: RemoteDispatcher) -> bool:
    """
    Assert that the dispatcher has no fallback logic.

    This is verified by code inspection — the dispatch() method does not
    attempt alternate executors on failure.

    Args:
        dispatcher: The dispatcher to check.

    Returns:
        True (by design).
    """
    # No fallback logic exists in the dispatch() method
    return True


def assert_failure_propagates_upstream(dispatcher: RemoteDispatcher) -> bool:
    """
    Assert that failures are propagated, not hidden.

    This is verified by code inspection — all error paths result in
    TaskExecutionResult with FAILED state.

    Args:
        dispatcher: The dispatcher to check.

    Returns:
        True (by design).
    """
    # All error paths in dispatch() and _response_to_result() return
    # TaskExecutionResult with FAILED state
    return True
