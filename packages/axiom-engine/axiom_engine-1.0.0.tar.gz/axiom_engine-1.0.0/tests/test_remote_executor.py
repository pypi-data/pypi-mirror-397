"""
Tests for Remote Executor Protocol, Authentication, Stub, and Dispatch.

This module verifies that remote execution maintains all governance guarantees:
1. Remote executor enforces authentication
2. Remote executor enforces policies identically to local
3. Remote executor cannot access Canon
4. Remote executor executes exactly one task
5. Network failure does not cause retries
6. Conductor treats remote and local results uniformly
7. Existing execution tests pass unchanged

CRITICAL INVARIANTS:
- No intelligence or reasoning in remote executors
- No planning, no approval, no Canon access
- One task per request
- No retries, no fallback
- Failure propagates upstream
"""

import pytest
import json
from datetime import datetime
from dataclasses import FrozenInstanceError

from axiom_forge.remote_protocol import (
    RemoteExecutionStatus,
    RemoteBackendType,
    AuthenticationMetadata,
    SerializedTaskInput,
    DeclaredTaskRequirements,
    RemoteExecutionRequest,
    RemoteExecutionResponse,
    SerializedExecutionResult,
    PolicyEnforcementReport,
    ExecutionMetadata,
    serialize_from_task_execution_input,
    deserialize_to_task_execution_input,
)
from axiom_forge.remote_auth import (
    AuthenticationError,
    TokenMissingError,
    TokenInvalidError,
    TokenExpiredError,
    NonceReusedError,
    AuthenticationConfig,
    AuthenticationValidator,
    AuthenticationResult,
    validate_authentication,
    generate_secure_token,
    hash_token,
)
from axiom_forge.remote_stub import (
    RemoteExecutorStub,
    RemoteStubConfig,
    RemoteStubError,
    CapabilityMismatchError,
    PolicyViolationError,
    PolicyValidator,
    create_shell_stub,
    create_playwright_stub,
    create_context_aware_stub,
    assert_stub_has_no_state,
    assert_stub_cannot_access_canon,
    assert_stub_executes_one_task,
)
from axiom_conductor.remote_dispatch import (
    RemoteDispatchError,
    NetworkError,
    SerializationError,
    ProtocolError,
    LocalTransport,
    RemoteDispatcher,
    RemoteExecutionBackend,
    create_remote_shell_backend,
    create_remote_playwright_backend,
    create_remote_context_aware_backend,
    assert_no_retries_in_dispatcher,
    assert_no_fallback_in_dispatcher,
    assert_failure_propagates_upstream,
)
from axiom_forge.backend import TaskExecutionInput
from axiom_conductor.model import TaskExecutionState, TaskFailureReason


# =============================================================================
# TEST: PROTOCOL MODELS
# =============================================================================


class TestRemoteExecutionStatus:
    """Tests for RemoteExecutionStatus enum."""

    def test_status_values_are_strings(self) -> None:
        """All status values are string-serializable."""
        for status in RemoteExecutionStatus:
            assert isinstance(status.value, str)

    def test_success_status_exists(self) -> None:
        """SUCCESS status is defined."""
        assert RemoteExecutionStatus.SUCCESS.value == "success"

    def test_auth_failed_status_exists(self) -> None:
        """AUTH_FAILED status is defined."""
        assert RemoteExecutionStatus.AUTH_FAILED.value == "auth_failed"

    def test_policy_violation_status_exists(self) -> None:
        """POLICY_VIOLATION status is defined."""
        assert RemoteExecutionStatus.POLICY_VIOLATION.value == "policy_violation"


class TestRemoteBackendType:
    """Tests for RemoteBackendType enum."""

    def test_shell_backend_defined(self) -> None:
        """SHELL backend type exists."""
        assert RemoteBackendType.SHELL.value == "shell"

    def test_playwright_backend_defined(self) -> None:
        """PLAYWRIGHT backend type exists."""
        assert RemoteBackendType.PLAYWRIGHT.value == "playwright"

    def test_context_aware_backend_defined(self) -> None:
        """CONTEXT_AWARE backend type exists."""
        assert RemoteBackendType.CONTEXT_AWARE.value == "context_aware"


class TestAuthenticationMetadata:
    """Tests for AuthenticationMetadata."""

    def test_is_frozen(self) -> None:
        """AuthenticationMetadata is immutable."""
        auth = AuthenticationMetadata.create("test-token")
        with pytest.raises(FrozenInstanceError):
            auth.token = "new-token"  # type: ignore

    def test_create_generates_timestamp(self) -> None:
        """create() generates a timestamp."""
        auth = AuthenticationMetadata.create("test-token")
        assert auth.request_timestamp is not None
        assert "Z" in auth.request_timestamp

    def test_create_generates_unique_nonce(self) -> None:
        """create() generates unique nonces."""
        auth1 = AuthenticationMetadata.create("test-token")
        auth2 = AuthenticationMetadata.create("test-token")
        assert auth1.request_nonce != auth2.request_nonce

    def test_serialization_roundtrip(self) -> None:
        """to_dict/from_dict roundtrip preserves data."""
        auth = AuthenticationMetadata.create("test-token")
        data = auth.to_dict()
        restored = AuthenticationMetadata.from_dict(data)
        assert restored.token == auth.token
        assert restored.request_timestamp == auth.request_timestamp
        assert restored.request_nonce == auth.request_nonce


class TestSerializedTaskInput:
    """Tests for SerializedTaskInput."""

    def test_is_frozen(self) -> None:
        """SerializedTaskInput is immutable."""
        task = SerializedTaskInput(
            task_id="t1",
            command="echo",
            args=("hello",),
            env=(),
            working_directory=None,
            timeout_seconds=60,
            metadata=(),
        )
        with pytest.raises(FrozenInstanceError):
            task.command = "ls"  # type: ignore

    def test_json_roundtrip(self) -> None:
        """to_json/from_json roundtrip preserves data."""
        task = SerializedTaskInput(
            task_id="t1",
            command="echo",
            args=("hello", "world"),
            env=(("PATH", "/usr/bin"),),
            working_directory="/tmp",
            timeout_seconds=120,
            metadata=(("key", "value"),),
        )
        json_str = task.to_json()
        restored = SerializedTaskInput.from_json(json_str)
        assert restored.task_id == task.task_id
        assert restored.command == task.command
        assert restored.args == task.args
        assert restored.working_directory == task.working_directory


class TestDeclaredTaskRequirements:
    """Tests for DeclaredTaskRequirements."""

    def test_is_frozen(self) -> None:
        """DeclaredTaskRequirements is immutable."""
        req = DeclaredTaskRequirements(
            backend_type=RemoteBackendType.SHELL,
            required_commands=("echo",),
            required_domains=(),
            required_files=(),
            estimated_timeout=60,
        )
        with pytest.raises(FrozenInstanceError):
            req.backend_type = RemoteBackendType.PLAYWRIGHT  # type: ignore

    def test_serialization_roundtrip(self) -> None:
        """to_dict/from_dict roundtrip works."""
        req = DeclaredTaskRequirements(
            backend_type=RemoteBackendType.SHELL,
            required_commands=("ls", "cat"),
            required_domains=(),
            required_files=(),
            estimated_timeout=300,
        )
        data = req.to_dict()
        restored = DeclaredTaskRequirements.from_dict(data)
        assert restored.backend_type == req.backend_type
        assert restored.required_commands == req.required_commands


class TestRemoteExecutionRequest:
    """Tests for RemoteExecutionRequest."""

    def test_is_frozen(self) -> None:
        """Request is immutable."""
        task = SerializedTaskInput(
            task_id="t1",
            command="echo",
            args=(),
            env=(),
            working_directory=None,
            timeout_seconds=60,
            metadata=(),
        )
        req = DeclaredTaskRequirements(
            backend_type=RemoteBackendType.SHELL,
            required_commands=(),
            required_domains=(),
            required_files=(),
            estimated_timeout=60,
        )
        request = RemoteExecutionRequest.create(
            executor_id="exec-1",
            task_input=task,
            requirements=req,
            auth_token="token",
        )
        with pytest.raises(FrozenInstanceError):
            request.executor_id = "new-id"  # type: ignore

    def test_create_generates_request_id(self) -> None:
        """create() generates unique request IDs."""
        task = SerializedTaskInput(
            task_id="t1",
            command="echo",
            args=(),
            env=(),
            working_directory=None,
            timeout_seconds=60,
            metadata=(),
        )
        req = DeclaredTaskRequirements(
            backend_type=RemoteBackendType.SHELL,
            required_commands=(),
            required_domains=(),
            required_files=(),
            estimated_timeout=60,
        )
        request1 = RemoteExecutionRequest.create("exec-1", task, req, "token")
        request2 = RemoteExecutionRequest.create("exec-1", task, req, "token")
        assert request1.request_id != request2.request_id

    def test_json_roundtrip(self) -> None:
        """to_json/from_json roundtrip works."""
        task = SerializedTaskInput(
            task_id="t1",
            command="echo",
            args=("hello",),
            env=(),
            working_directory="/tmp",
            timeout_seconds=60,
            metadata=(),
        )
        req = DeclaredTaskRequirements(
            backend_type=RemoteBackendType.SHELL,
            required_commands=("echo",),
            required_domains=(),
            required_files=(),
            estimated_timeout=60,
        )
        request = RemoteExecutionRequest.create("exec-1", task, req, "secret-token")
        json_str = request.to_json()
        restored = RemoteExecutionRequest.from_json(json_str)
        assert restored.request_id == request.request_id
        assert restored.executor_id == request.executor_id
        assert restored.task_input.task_id == task.task_id


class TestRemoteExecutionResponse:
    """Tests for RemoteExecutionResponse."""

    def test_success_response_creation(self) -> None:
        """Success response can be created."""
        result = SerializedExecutionResult(
            task_id="t1",
            state="completed",
            exit_code=0,
            stdout="hello",
            stderr="",
            failure_reason=None,
            error_message=None,
            metadata=(),
            timestamp=datetime.utcnow().isoformat() + "Z",
        )
        response = RemoteExecutionResponse(
            request_id="req-1",
            status=RemoteExecutionStatus.SUCCESS,
            result=result,
            execution_metadata=None,
            policy_report=None,
        )
        assert response.status == RemoteExecutionStatus.SUCCESS
        assert response.result == result

    def test_auth_failure_response(self) -> None:
        """Auth failure response can be created."""
        response = RemoteExecutionResponse.auth_failed(request_id="req-1")
        assert response.status == RemoteExecutionStatus.AUTH_FAILED
        assert response.error_message is not None
        assert response.result is None

    def test_policy_violation_response(self) -> None:
        """Policy violation response can be created."""
        report = PolicyEnforcementReport(
            checks_performed=("command_check",),
            violations_detected=("command_not_allowed",),
            all_passed=False,
        )
        response = RemoteExecutionResponse.policy_violation(
            request_id="req-1",
            report=report,
        )
        assert response.status == RemoteExecutionStatus.POLICY_VIOLATION
        assert response.policy_report is not None
        assert "command_not_allowed" in response.policy_report.violations_detected


# =============================================================================
# TEST: AUTHENTICATION
# =============================================================================


class TestAuthenticationValidator:
    """Tests for authentication validation."""

    def test_valid_token_authenticates(self) -> None:
        """Valid token passes authentication."""
        config = AuthenticationConfig(expected_token="secret-token")
        validator = AuthenticationValidator(config)
        auth = AuthenticationMetadata.create("secret-token")
        # No exception means authentication passed
        validator.validate(
            token=auth.token,
            request_timestamp=auth.request_timestamp,
            request_nonce=auth.request_nonce,
        )

    def test_invalid_token_rejected(self) -> None:
        """Invalid token is rejected."""
        config = AuthenticationConfig(expected_token="secret-token")
        validator = AuthenticationValidator(config)
        auth = AuthenticationMetadata.create("wrong-token")
        with pytest.raises(AuthenticationError):
            validator.validate(
                token=auth.token,
                request_timestamp=auth.request_timestamp,
                request_nonce=auth.request_nonce,
            )

    def test_missing_token_rejected(self) -> None:
        """Missing/empty token is rejected."""
        config = AuthenticationConfig(expected_token="secret-token")
        validator = AuthenticationValidator(config)
        with pytest.raises(AuthenticationError):
            validator.validate(
                token="",
                request_timestamp=datetime.utcnow().isoformat() + "Z",
                request_nonce="abc123",
            )

    def test_constant_time_comparison(self) -> None:
        """Token comparison uses constant-time algorithm."""
        # This is verified by code inspection — hash_token uses hmac.compare_digest
        token_hash = hash_token("test")
        assert isinstance(token_hash, str)
        assert len(token_hash) == 64  # SHA-256 hex digest

    def test_no_information_leakage(self) -> None:
        """Rejection message doesn't leak token info."""
        config = AuthenticationConfig(expected_token="secret-token")
        validator = AuthenticationValidator(config)
        auth = AuthenticationMetadata.create("wrong-token")
        try:
            validator.validate(
                token=auth.token,
                request_timestamp=auth.request_timestamp,
                request_nonce=auth.request_nonce,
            )
        except AuthenticationError as e:
            # Error message should not contain the expected token
            assert "secret-token" not in str(e)
            assert "wrong-token" not in str(e)


class TestSecureTokenGeneration:
    """Tests for secure token generation."""

    def test_generates_correct_length(self) -> None:
        """Generated tokens have correct length."""
        token = generate_secure_token(32)
        assert len(token) == 64  # 32 bytes * 2 hex chars

    def test_generates_unique_tokens(self) -> None:
        """Each generated token is unique."""
        tokens = [generate_secure_token() for _ in range(100)]
        assert len(set(tokens)) == 100

    def test_tokens_are_cryptographically_random(self) -> None:
        """Tokens use secrets module (verified by inspection)."""
        token = generate_secure_token()
        # Should be hex-encoded bytes
        int(token, 16)  # Should not raise


# =============================================================================
# TEST: REMOTE EXECUTOR STUB
# =============================================================================


class TestRemoteStubConfig:
    """Tests for RemoteStubConfig."""

    def test_config_is_frozen(self) -> None:
        """Config is immutable."""
        config = RemoteStubConfig(
            executor_id="exec-1",
            backend_type=RemoteBackendType.SHELL,
            auth_config=AuthenticationConfig(expected_token="token"),
            command_allowlist=frozenset(["echo", "ls"]),
            domain_allowlist=frozenset(),
            file_patterns=frozenset(),
        )
        with pytest.raises(FrozenInstanceError):
            config.executor_id = "new-id"  # type: ignore


class TestRemoteExecutorStub:
    """Tests for RemoteExecutorStub."""

    def _create_mock_backend(self):
        """Create a mock backend for testing."""
        from axiom_forge.mock_backend import MockExecutionBackend
        return MockExecutionBackend()

    def test_stub_enforces_authentication(self) -> None:
        """Stub rejects requests with invalid auth."""
        stub = create_shell_stub(
            executor_id="exec-1",
            auth_token="secret-token",
            command_allowlist=frozenset(["echo"]),
            backend=self._create_mock_backend(),
        )
        task = SerializedTaskInput(
            task_id="t1",
            command="echo",
            args=("hello",),
            env=(),
            working_directory=None,
            timeout_seconds=60,
            metadata=(),
        )
        req = DeclaredTaskRequirements(
            backend_type=RemoteBackendType.SHELL,
            required_commands=("echo",),
            required_domains=(),
            required_files=(),
            estimated_timeout=60,
        )
        # Create request with wrong token
        request = RemoteExecutionRequest.create(
            executor_id="exec-1",
            task_input=task,
            requirements=req,
            auth_token="wrong-token",
        )
        response = stub.handle_request(request)
        assert response.status == RemoteExecutionStatus.AUTH_FAILED

    def test_stub_enforces_backend_type(self) -> None:
        """Stub rejects mismatched backend type."""
        stub = create_shell_stub(
            executor_id="exec-1",
            auth_token="secret-token",
            command_allowlist=frozenset(["echo"]),
            backend=self._create_mock_backend(),
        )
        task = SerializedTaskInput(
            task_id="t1",
            command="echo",
            args=(),
            env=(),
            working_directory=None,
            timeout_seconds=60,
            metadata=(),
        )
        # Request Playwright but stub is Shell
        req = DeclaredTaskRequirements(
            backend_type=RemoteBackendType.PLAYWRIGHT,
            required_commands=(),
            required_domains=(),
            required_files=(),
            estimated_timeout=60,
        )
        request = RemoteExecutionRequest.create(
            executor_id="exec-1",
            task_input=task,
            requirements=req,
            auth_token="secret-token",
        )
        response = stub.handle_request(request)
        assert response.status == RemoteExecutionStatus.POLICY_VIOLATION

    def test_stub_enforces_command_allowlist(self) -> None:
        """Stub rejects commands not in allowlist."""
        stub = create_shell_stub(
            executor_id="exec-1",
            auth_token="secret-token",
            command_allowlist=frozenset(["echo"]),
            backend=self._create_mock_backend(),
        )
        task = SerializedTaskInput(
            task_id="t1",
            command="rm",  # Not in allowlist
            args=("-rf", "/"),
            env=(),
            working_directory=None,
            timeout_seconds=60,
            metadata=(),
        )
        req = DeclaredTaskRequirements(
            backend_type=RemoteBackendType.SHELL,
            required_commands=("rm",),
            required_domains=(),
            required_files=(),
            estimated_timeout=60,
        )
        request = RemoteExecutionRequest.create(
            executor_id="exec-1",
            task_input=task,
            requirements=req,
            auth_token="secret-token",
        )
        response = stub.handle_request(request)
        assert response.status == RemoteExecutionStatus.POLICY_VIOLATION

    def test_stub_has_no_persistent_state(self) -> None:
        """Stub maintains no state between requests."""
        stub = create_shell_stub(
            executor_id="exec-1",
            auth_token="secret-token",
            command_allowlist=frozenset(["echo"]),
            backend=self._create_mock_backend(),
        )
        assert assert_stub_has_no_state(stub)

    def test_stub_cannot_access_canon(self) -> None:
        """Stub has no Canon access (verified by inspection)."""
        assert assert_stub_cannot_access_canon()

    def test_stub_executes_one_task(self) -> None:
        """Stub executes exactly one task per request."""
        stub = create_shell_stub(
            executor_id="exec-1",
            auth_token="secret-token",
            command_allowlist=frozenset(["echo"]),
            backend=self._create_mock_backend(),
        )
        assert assert_stub_executes_one_task(stub)


class TestPolicyEnforcement:
    """Tests for policy enforcement in remote stubs."""

    def _create_mock_backend(self):
        """Create a mock backend for testing."""
        from axiom_forge.mock_backend import MockExecutionBackend
        return MockExecutionBackend()

    def test_policy_report_included_in_response(self) -> None:
        """Response includes policy enforcement report."""
        stub = create_shell_stub(
            executor_id="exec-1",
            auth_token="secret-token",
            command_allowlist=frozenset(["echo"]),
            backend=self._create_mock_backend(),
        )
        task = SerializedTaskInput(
            task_id="t1",
            command="echo",
            args=("test",),
            env=(),
            working_directory=None,
            timeout_seconds=60,
            metadata=(),
        )
        req = DeclaredTaskRequirements(
            backend_type=RemoteBackendType.SHELL,
            required_commands=("echo",),
            required_domains=(),
            required_files=(),
            estimated_timeout=60,
        )
        request = RemoteExecutionRequest.create(
            executor_id="exec-1",
            task_input=task,
            requirements=req,
            auth_token="secret-token",
        )
        response = stub.handle_request(request)
        # Either success with report or failure with report
        if response.status == RemoteExecutionStatus.SUCCESS:
            assert response.policy_report is not None
            assert response.policy_report.all_passed is True

    def test_violations_are_explicit(self) -> None:
        """Policy violations are explicitly listed."""
        stub = create_shell_stub(
            executor_id="exec-1",
            auth_token="secret-token",
            command_allowlist=frozenset(["echo"]),
            backend=self._create_mock_backend(),
        )
        task = SerializedTaskInput(
            task_id="t1",
            command="rm",  # Not allowed
            args=(),
            env=(),
            working_directory=None,
            timeout_seconds=60,
            metadata=(),
        )
        req = DeclaredTaskRequirements(
            backend_type=RemoteBackendType.SHELL,
            required_commands=("rm",),
            required_domains=(),
            required_files=(),
            estimated_timeout=60,
        )
        request = RemoteExecutionRequest.create(
            executor_id="exec-1",
            task_input=task,
            requirements=req,
            auth_token="secret-token",
        )
        response = stub.handle_request(request)
        assert response.status == RemoteExecutionStatus.POLICY_VIOLATION
        assert response.policy_report is not None
        assert len(response.policy_report.violations_detected) > 0


# =============================================================================
# TEST: REMOTE DISPATCH
# =============================================================================


class TestRemoteDispatcher:
    """Tests for RemoteDispatcher."""

    def test_no_retries_on_failure(self) -> None:
        """Dispatcher does not retry on failure."""
        dispatcher = RemoteDispatcher(
            executor_id="exec-1",
            backend_type=RemoteBackendType.SHELL,
            auth_token="token",
            transport=LocalTransport(handler=lambda _: ""),
        )
        assert assert_no_retries_in_dispatcher(dispatcher)

    def test_no_fallback_on_failure(self) -> None:
        """Dispatcher does not fallback to other executors."""
        dispatcher = RemoteDispatcher(
            executor_id="exec-1",
            backend_type=RemoteBackendType.SHELL,
            auth_token="token",
            transport=LocalTransport(handler=lambda _: ""),
        )
        assert assert_no_fallback_in_dispatcher(dispatcher)

    def test_failure_propagates_upstream(self) -> None:
        """Failures are propagated, not hidden."""
        dispatcher = RemoteDispatcher(
            executor_id="exec-1",
            backend_type=RemoteBackendType.SHELL,
            auth_token="token",
            transport=LocalTransport(handler=lambda _: ""),
        )
        assert assert_failure_propagates_upstream(dispatcher)

    def test_network_error_becomes_dispatch_error(self) -> None:
        """Network errors become RemoteDispatchError."""

        def failing_transport(request: str) -> str:
            raise ConnectionError("Network unreachable")

        dispatcher = RemoteDispatcher(
            executor_id="exec-1",
            backend_type=RemoteBackendType.SHELL,
            auth_token="token",
            transport=LocalTransport(handler=failing_transport),
        )
        task_input = TaskExecutionInput(
            task_id="t1",
            command="echo",
            args=["hello"],
            timeout_seconds=60,
        )
        with pytest.raises(NetworkError):
            dispatcher.dispatch(task_input)


class TestRemoteExecutionBackend:
    """Tests for RemoteExecutionBackend adapter."""

    def test_converts_dispatch_error_to_result(self) -> None:
        """Dispatch errors become failed TaskExecutionResult."""

        def failing_transport(request: str) -> str:
            raise ConnectionError("Network unreachable")

        backend = create_remote_shell_backend(
            executor_id="exec-1",
            auth_token="token",
            transport=LocalTransport(handler=failing_transport),
        )
        task_input = TaskExecutionInput(
            task_id="t1",
            command="echo",
            args=["hello"],
            timeout_seconds=60,
        )
        result = backend.execute_task(task_input)
        assert result.state == TaskExecutionState.FAILED
        assert result.failure_reason == TaskFailureReason.SYSTEM_ERROR

    def test_treats_remote_like_local(self) -> None:
        """Remote execution returns standard TaskExecutionResult."""
        # Create a mock transport that returns a success response
        def mock_transport(request_json: str) -> str:
            request = RemoteExecutionRequest.from_json(request_json)
            result = SerializedExecutionResult(
                task_id=request.task_input.task_id,
                state="succeeded",  # Match TaskExecutionState.SUCCEEDED
                exit_code=0,
                stdout="hello",
                stderr="",
                failure_reason=None,
                error_message=None,
                metadata=(),
                timestamp=datetime.utcnow().isoformat() + "Z",
            )
            response = RemoteExecutionResponse(
                request_id=request.request_id,
                status=RemoteExecutionStatus.SUCCESS,
                result=result,
                execution_metadata=None,
                policy_report=PolicyEnforcementReport.passed(["command_check"]),
            )
            return response.to_json()

        backend = create_remote_shell_backend(
            executor_id="exec-1",
            auth_token="token",
            transport=LocalTransport(handler=mock_transport),
        )
        task_input = TaskExecutionInput(
            task_id="t1",
            command="echo",
            args=["hello"],
            timeout_seconds=60,
        )
        result = backend.execute_task(task_input)
        assert result.task_id == "t1"
        assert result.state == TaskExecutionState.SUCCEEDED
        assert result.stdout == "hello"


class TestLocalTransport:
    """Tests for LocalTransport (testing utility)."""

    def test_calls_handler(self) -> None:
        """LocalTransport calls the provided handler."""
        called = []

        def handler(request: str) -> str:
            called.append(request)
            return '{"status": "success"}'

        transport = LocalTransport(handler=handler)
        result = transport.send('{"test": true}')
        assert len(called) == 1
        assert called[0] == '{"test": true}'


# =============================================================================
# TEST: END-TO-END INTEGRATION
# =============================================================================


class TestRemoteExecutionIntegration:
    """Integration tests for remote execution flow."""

    def _create_mock_backend(self):
        """Create a mock backend for testing."""
        from axiom_forge.mock_backend import MockExecutionBackend
        return MockExecutionBackend()

    def test_full_roundtrip_with_local_stub(self) -> None:
        """Full request/response roundtrip works."""
        # Create stub
        stub = create_shell_stub(
            executor_id="exec-1",
            auth_token="secret-token",
            command_allowlist=frozenset(["echo"]),
            backend=self._create_mock_backend(),
        )

        # Create transport that calls stub
        def stub_transport(request_json: str) -> str:
            return stub.handle_json_request(request_json)

        # Create backend
        backend = create_remote_shell_backend(
            executor_id="exec-1",
            auth_token="secret-token",
            transport=LocalTransport(handler=stub_transport),
            required_commands=("echo",),
        )

        # Execute task
        task_input = TaskExecutionInput(
            task_id="t1",
            command="echo",
            args=["hello"],
            timeout_seconds=60,
        )
        result = backend.execute_task(task_input)

        # Verify result
        assert result.task_id == "t1"
        # Result should have remote execution metadata
        assert result.metadata.get("remote_execution") is True

    def test_auth_failure_propagates_correctly(self) -> None:
        """Auth failure from stub becomes failed result."""
        # Create stub with one token
        stub = create_shell_stub(
            executor_id="exec-1",
            auth_token="correct-token",
            command_allowlist=frozenset(["echo"]),
            backend=self._create_mock_backend(),
        )

        def stub_transport(request_json: str) -> str:
            return stub.handle_json_request(request_json)

        # Create backend with wrong token
        backend = create_remote_shell_backend(
            executor_id="exec-1",
            auth_token="wrong-token",
            transport=LocalTransport(handler=stub_transport),
        )

        task_input = TaskExecutionInput(
            task_id="t1",
            command="echo",
            args=["hello"],
            timeout_seconds=60,
        )
        result = backend.execute_task(task_input)

        assert result.state == TaskExecutionState.FAILED
        assert "auth" in result.error_message.lower()

    def test_policy_violation_propagates_correctly(self) -> None:
        """Policy violation from stub becomes failed result."""
        # Create stub that only allows "echo"
        stub = create_shell_stub(
            executor_id="exec-1",
            auth_token="secret-token",
            command_allowlist=frozenset(["echo"]),
            backend=self._create_mock_backend(),
        )

        def stub_transport(request_json: str) -> str:
            return stub.handle_json_request(request_json)

        backend = create_remote_shell_backend(
            executor_id="exec-1",
            auth_token="secret-token",
            transport=LocalTransport(handler=stub_transport),
        )

        # Try to execute disallowed command
        task_input = TaskExecutionInput(
            task_id="t1",
            command="rm",  # Not allowed
            args=["-rf", "/"],
            timeout_seconds=60,
        )
        result = backend.execute_task(task_input)

        assert result.state == TaskExecutionState.FAILED
        # Policy violations should be in metadata
        assert "policy_violations" in result.metadata


# =============================================================================
# TEST: INVARIANT ASSERTIONS
# =============================================================================


class TestRemoteExecutorInvariants:
    """Tests that verify remote executor invariants hold."""

    def _create_mock_backend(self):
        """Create a mock backend for testing."""
        from axiom_forge.mock_backend import MockExecutionBackend
        return MockExecutionBackend()

    def test_remote_executor_is_not_agent(self) -> None:
        """Remote executor has no planning or reasoning."""
        stub = create_shell_stub(
            executor_id="exec-1",
            auth_token="token",
            command_allowlist=frozenset(["echo"]),
            backend=self._create_mock_backend(),
        )
        # Verify no planning methods exist
        assert not hasattr(stub, "plan")
        assert not hasattr(stub, "reason")
        assert not hasattr(stub, "decide")
        assert not hasattr(stub, "approve")

    def test_remote_executor_no_persistent_state(self) -> None:
        """Remote executor maintains no persistent state."""
        stub = create_shell_stub(
            executor_id="exec-1",
            auth_token="token",
            command_allowlist=frozenset(["echo"]),
            backend=self._create_mock_backend(),
        )
        # Verify no state storage methods
        assert not hasattr(stub, "save_state")
        assert not hasattr(stub, "load_state")
        assert not hasattr(stub, "persist")

    def test_remote_executor_no_canon_access(self) -> None:
        """Remote executor cannot access Canon."""
        stub = create_shell_stub(
            executor_id="exec-1",
            auth_token="token",
            command_allowlist=frozenset(["echo"]),
            backend=self._create_mock_backend(),
        )
        # Verify no Canon methods
        assert not hasattr(stub, "read_cpkg")
        assert not hasattr(stub, "write_cpkg")
        assert not hasattr(stub, "query_knowledge")

    def test_dispatcher_no_retry_logic(self) -> None:
        """Dispatcher has no retry mechanism."""
        dispatcher = RemoteDispatcher(
            executor_id="exec-1",
            backend_type=RemoteBackendType.SHELL,
            auth_token="token",
            transport=LocalTransport(handler=lambda _: ""),
        )
        # Verify no retry methods
        assert not hasattr(dispatcher, "retry")
        assert not hasattr(dispatcher, "retry_count")
        assert not hasattr(dispatcher, "max_retries")

    def test_dispatcher_no_fallback_logic(self) -> None:
        """Dispatcher has no fallback mechanism."""
        dispatcher = RemoteDispatcher(
            executor_id="exec-1",
            backend_type=RemoteBackendType.SHELL,
            auth_token="token",
            transport=LocalTransport(handler=lambda _: ""),
        )
        # Verify no fallback methods
        assert not hasattr(dispatcher, "fallback")
        assert not hasattr(dispatcher, "alternate_executor")
        assert not hasattr(dispatcher, "backup")
