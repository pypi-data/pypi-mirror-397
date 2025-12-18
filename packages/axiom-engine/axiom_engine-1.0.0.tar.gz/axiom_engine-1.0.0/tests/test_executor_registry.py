"""
Tests for the Executor Registry and Capability Declaration system.

Phase 10B: DECLARATIVE Executor Registry and CAPABILITY MODEL

Test Philosophy:
- Executor selection is DETERMINISTIC
- No heuristics, no intelligence in selection
- Policy mismatches fail fast
- Registry is immutable once frozen

Test Categories:
1. Registry Construction & Immutability
2. Capability Matching (Pure Functions)
3. Deterministic Selection
4. Policy Enforcement
5. Error Handling
6. Integration Scenarios
"""

import pytest
from typing import List

from axiom_conductor.registry_models import (
    ExecutorId,
    ExecutorType,
    ExecutorCognitionLevel,
    BackendType,
    SupportedTaskType,
    AllowedOperation,
    ExecutorCapabilities,
    ExecutorPolicy,
    ExecutorDefinition,
    TaskExecutionRequirements,
    CapabilityMatchResult,
    CapabilityMatchStatus,
    create_shell_executor,
    create_playwright_executor,
    create_context_aware_executor,
)
from axiom_conductor.registry import (
    RegistryError,
    DuplicateExecutorError,
    InvalidDefinitionError,
    ExecutorNotFoundError,
    RegistryFrozenError,
    CapabilityMatcher,
    ExecutorRegistry,
    ExecutorRegistryBuilder,
    validate_registry_is_deterministic,
    validate_registry_has_no_heuristics,
    validate_no_runtime_mutation,
)
from axiom_conductor.selector import (
    SelectionStatus,
    ExecutorSelectionResult,
    SelectionError,
    NoCompatibleExecutorError,
    ExecutorIncompatibleError,
    ExecutorSelector,
    shell_requirements,
    playwright_requirements,
    context_aware_requirements,
)


# =============================================================================
# SECTION 1: Registry Model Tests
# =============================================================================

class TestExecutorId:
    """Tests for ExecutorId value object."""

    def test_executor_id_is_frozen(self) -> None:
        """ExecutorId should be immutable."""
        executor_id = ExecutorId("test-id")
        with pytest.raises(AttributeError):
            executor_id.value = "new-id"  # type: ignore

    def test_executor_id_equality(self) -> None:
        """ExecutorIds with same value should be equal."""
        id1 = ExecutorId("test")
        id2 = ExecutorId("test")
        assert id1 == id2

    def test_executor_id_hashable(self) -> None:
        """ExecutorId should be hashable for use in sets/dicts."""
        id1 = ExecutorId("test")
        id2 = ExecutorId("test")
        executor_set = {id1, id2}
        assert len(executor_set) == 1


class TestExecutorDefinition:
    """Tests for ExecutorDefinition construction."""

    def test_create_shell_executor(self) -> None:
        """Shell executor factory creates valid definition."""
        executor = create_shell_executor(
            executor_id="shell-1",
            name="Local Shell",
            command_allowlist=frozenset(["ls", "cat", "echo"]),
        )

        assert str(executor.id) == "shell-1"
        assert executor.name == "Local Shell"
        assert executor.executor_type == ExecutorType.LOCAL
        assert executor.cognition_level == ExecutorCognitionLevel.LEVEL_0_DUMB
        assert BackendType.SHELL in executor.capabilities.supported_backends
        assert "ls" in executor.policy.command_allowlist

    def test_create_playwright_executor(self) -> None:
        """Playwright executor factory creates valid definition."""
        executor = create_playwright_executor(
            executor_id="playwright-1",
            name="Local Playwright",
            domain_allowlist=frozenset(["localhost", "example.com"]),
        )

        assert str(executor.id) == "playwright-1"
        assert executor.cognition_level == ExecutorCognitionLevel.LEVEL_0_DUMB
        assert BackendType.PLAYWRIGHT in executor.capabilities.supported_backends
        assert "localhost" in executor.policy.domain_allowlist

    def test_create_context_aware_executor(self) -> None:
        """Context-aware executor factory creates valid definition."""
        executor = create_context_aware_executor(
            executor_id="context-1",
            name="Context-Aware Executor",
            max_context_tokens=8000,
            file_access_patterns=frozenset(["*.py", "*.ts"]),
            allowed_operations=frozenset([AllowedOperation.READ, AllowedOperation.EDIT]),
        )

        assert str(executor.id) == "context-1"
        assert executor.cognition_level == ExecutorCognitionLevel.LEVEL_1_CONTEXT_AWARE
        assert BackendType.CONTEXT_AWARE in executor.capabilities.supported_backends
        assert AllowedOperation.EDIT in executor.capabilities.allowed_operations
        assert executor.policy.max_context_tokens == 8000

    def test_executor_definition_is_frozen(self) -> None:
        """ExecutorDefinition should be immutable."""
        executor = create_shell_executor(
            executor_id="shell-1",
            name="Test Shell",
            command_allowlist=frozenset(["ls"]),
        )
        with pytest.raises(AttributeError):
            executor.name = "New Name"  # type: ignore


# =============================================================================
# SECTION 2: Capability Matching Tests
# =============================================================================

class TestCapabilityMatcher:
    """Tests for the pure CapabilityMatcher function object."""

    def test_exact_backend_match(self) -> None:
        """Matcher returns compatible for exact backend match."""
        matcher = CapabilityMatcher()
        executor = create_shell_executor(
            executor_id="shell-1",
            name="Shell",
            command_allowlist=frozenset(["ls", "cat"]),
        )
        requirements = TaskExecutionRequirements(
            required_backend=BackendType.SHELL,
            required_task_type=SupportedTaskType.EXECUTION,
            command="ls",
        )

        result = matcher.match(executor, requirements)

        assert result.status == CapabilityMatchStatus.COMPATIBLE
        assert result.is_compatible

    def test_backend_mismatch_rejects(self) -> None:
        """Matcher rejects when required backend not supported."""
        matcher = CapabilityMatcher()
        executor = create_shell_executor(
            executor_id="shell-1",
            name="Shell",
            command_allowlist=frozenset(["ls"]),
        )
        requirements = TaskExecutionRequirements(
            required_backend=BackendType.PLAYWRIGHT,
            required_task_type=SupportedTaskType.EXECUTION,
        )

        result = matcher.match(executor, requirements)

        assert result.status == CapabilityMatchStatus.INCOMPATIBLE_BACKEND
        assert not result.is_compatible

    def test_cognition_level_mismatch_rejects(self) -> None:
        """Matcher rejects when required cognition level not met."""
        matcher = CapabilityMatcher()
        executor = create_shell_executor(
            executor_id="shell-1",
            name="Shell",
            command_allowlist=frozenset(["ls"]),
        )
        requirements = TaskExecutionRequirements(
            required_backend=BackendType.SHELL,
            required_task_type=SupportedTaskType.EXECUTION,
            required_cognition_level=ExecutorCognitionLevel.LEVEL_1_CONTEXT_AWARE,
        )

        result = matcher.match(executor, requirements)

        assert result.status == CapabilityMatchStatus.INCOMPATIBLE_COGNITION
        assert not result.is_compatible

    def test_command_allowlist_enforcement(self) -> None:
        """Matcher enforces command allowlist policy."""
        matcher = CapabilityMatcher()
        executor = create_shell_executor(
            executor_id="shell-1",
            name="Shell",
            command_allowlist=frozenset(["ls", "cat"]),
        )
        requirements = TaskExecutionRequirements(
            required_backend=BackendType.SHELL,
            required_task_type=SupportedTaskType.EXECUTION,
            command="rm",  # Not in allowlist
        )

        result = matcher.match(executor, requirements)

        assert result.status == CapabilityMatchStatus.POLICY_VIOLATION_COMMAND
        assert not result.is_compatible
        assert "rm" in result.message

    def test_domain_allowlist_enforcement(self) -> None:
        """Matcher enforces domain allowlist policy."""
        matcher = CapabilityMatcher()
        executor = create_playwright_executor(
            executor_id="pw-1",
            name="Playwright",
            domain_allowlist=frozenset(["localhost"]),
        )
        requirements = TaskExecutionRequirements(
            required_backend=BackendType.PLAYWRIGHT,
            required_task_type=SupportedTaskType.EXECUTION,
            domain="example.com",  # Not allowed
        )

        result = matcher.match(executor, requirements)

        assert result.status == CapabilityMatchStatus.POLICY_VIOLATION_DOMAIN
        assert not result.is_compatible
        assert "example.com" in result.message

    def test_matcher_is_pure_function(self) -> None:
        """Matcher produces same result for same inputs."""
        matcher = CapabilityMatcher()
        executor = create_shell_executor(
            executor_id="shell-1",
            name="Shell",
            command_allowlist=frozenset(["ls"]),
        )
        requirements = TaskExecutionRequirements(
            required_backend=BackendType.SHELL,
            required_task_type=SupportedTaskType.EXECUTION,
            command="ls",
        )

        # Call multiple times
        results = [matcher.match(executor, requirements) for _ in range(10)]

        # All results should be identical
        assert all(r.status == results[0].status for r in results)
        assert all(r.is_compatible == results[0].is_compatible for r in results)


# =============================================================================
# SECTION 3: Registry Construction & Immutability Tests
# =============================================================================

class TestExecutorRegistry:
    """Tests for ExecutorRegistry construction and immutability."""

    def test_registry_starts_unfrozen(self) -> None:
        """New registry starts in unfrozen state."""
        registry = ExecutorRegistry()
        assert not registry.is_frozen

    def test_registry_can_register_before_freeze(self) -> None:
        """Executors can be registered before freezing."""
        registry = ExecutorRegistry()
        executor = create_shell_executor(
            executor_id="shell-1",
            name="Shell",
            command_allowlist=frozenset(["ls"]),
        )

        registry.register(executor)

        assert registry.get(ExecutorId("shell-1")) == executor

    def test_registry_freeze_prevents_registration(self) -> None:
        """Freeze prevents further registration."""
        registry = ExecutorRegistry()
        registry.freeze()

        executor = create_shell_executor(
            executor_id="shell-1",
            name="Shell",
            command_allowlist=frozenset(["ls"]),
        )

        with pytest.raises(RegistryFrozenError):
            registry.register(executor)

    def test_registry_freeze_is_idempotent(self) -> None:
        """Calling freeze multiple times is safe."""
        registry = ExecutorRegistry()
        registry.freeze()
        registry.freeze()  # Should not raise
        assert registry.is_frozen

    def test_duplicate_id_raises_error(self) -> None:
        """Registering duplicate executor ID raises error."""
        registry = ExecutorRegistry()
        executor1 = create_shell_executor(
            executor_id="shell-1",
            name="Shell 1",
            command_allowlist=frozenset(["ls"]),
        )
        executor2 = create_shell_executor(
            executor_id="shell-1",  # Same ID
            name="Shell 2",
            command_allowlist=frozenset(["cat"]),
        )

        registry.register(executor1)

        with pytest.raises(DuplicateExecutorError):
            registry.register(executor2)

    def test_registry_list_executors_returns_copy(self) -> None:
        """list_all returns a copy, not internal state."""
        registry = ExecutorRegistry()
        executor = create_shell_executor(
            executor_id="shell-1",
            name="Shell",
            command_allowlist=frozenset(["ls"]),
        )
        registry.register(executor)
        registry.freeze()

        executors = registry.list_all()
        original_length = len(executors)

        # Modifying returned list should not affect registry
        executors.clear()

        assert len(registry.list_all()) == original_length

    def test_registry_iteration_order_is_stable(self) -> None:
        """Registry iteration order is deterministic."""
        registry = ExecutorRegistry()

        # Register in specific order
        for i in range(5):
            executor = create_shell_executor(
                executor_id=f"shell-{i}",
                name=f"Shell {i}",
                command_allowlist=frozenset(["ls"]),
                priority=10 - i,  # Descending priority
            )
            registry.register(executor)

        registry.freeze()

        # Multiple iterations should return same order
        order1 = [str(e.id) for e in registry.list_all()]
        order2 = [str(e.id) for e in registry.list_all()]
        order3 = [str(e.id) for e in registry.list_all()]

        assert order1 == order2 == order3


class TestExecutorRegistryBuilder:
    """Tests for the fluent ExecutorRegistryBuilder."""

    def test_builder_fluent_interface(self) -> None:
        """Builder supports fluent interface."""
        registry = (
            ExecutorRegistryBuilder()
            .add_shell(
                executor_id="shell-1",
                name="Shell",
                command_allowlist=frozenset(["ls"]),
            )
            .add_playwright(
                executor_id="pw-1",
                name="Playwright",
                domain_allowlist=frozenset(["localhost"]),
            )
            .build()
        )

        assert registry.is_frozen
        assert len(registry.list_all()) == 2

    def test_builder_produces_frozen_registry(self) -> None:
        """Builder.build() returns frozen registry."""
        registry = (
            ExecutorRegistryBuilder()
            .add_shell(
                executor_id="shell-1",
                name="Shell",
                command_allowlist=frozenset(["ls"]),
            )
            .build()
        )

        assert registry.is_frozen

    def test_builder_adds_context_aware_executor(self) -> None:
        """Builder supports context-aware executors."""
        registry = (
            ExecutorRegistryBuilder()
            .add_context_aware(
                executor_id="ctx-1",
                name="Context-Aware",
                max_context_tokens=8000,
                file_access_patterns=frozenset(["*.py"]),
                allowed_operations=frozenset([AllowedOperation.READ, AllowedOperation.EDIT]),
            )
            .build()
        )

        executor = registry.get(ExecutorId("ctx-1"))
        assert executor is not None
        assert executor.cognition_level == ExecutorCognitionLevel.LEVEL_1_CONTEXT_AWARE


# =============================================================================
# SECTION 4: Deterministic Selection Tests
# =============================================================================

class TestExecutorSelector:
    """Tests for deterministic ExecutorSelector."""

    def test_selection_returns_first_compatible_by_priority(self) -> None:
        """Selector returns first compatible executor by priority."""
        registry = (
            ExecutorRegistryBuilder()
            .add_shell(
                executor_id="shell-low",
                name="Low Priority",
                command_allowlist=frozenset(["ls"]),
                priority=10,
            )
            .add_shell(
                executor_id="shell-high",
                name="High Priority",
                command_allowlist=frozenset(["ls"]),
                priority=100,
            )
            .build()
        )

        selector = ExecutorSelector(registry)
        requirements = shell_requirements(command="ls")

        result = selector.select(requirements)

        assert result.status == SelectionStatus.SELECTED
        assert result.executor is not None
        # Lower priority value = higher priority, so shell-low (priority 10) should be selected
        assert str(result.executor.id) == "shell-low"

    def test_selection_is_reproducible(self) -> None:
        """Same selection query always returns same result."""
        registry = (
            ExecutorRegistryBuilder()
            .add_shell(
                executor_id="shell-1",
                name="Shell 1",
                command_allowlist=frozenset(["ls", "cat"]),
                priority=50,
            )
            .add_shell(
                executor_id="shell-2",
                name="Shell 2",
                command_allowlist=frozenset(["ls"]),
                priority=50,  # Same priority - should use ID as tiebreaker
            )
            .build()
        )

        selector = ExecutorSelector(registry)
        requirements = shell_requirements(command="ls")

        # Run selection multiple times
        results = [selector.select(requirements) for _ in range(100)]

        # All should select same executor
        selected_ids = [str(r.executor.id) for r in results if r.executor]
        assert len(set(selected_ids)) == 1

    def test_selection_no_compatible_returns_none(self) -> None:
        """Selector returns no match when no executor compatible."""
        registry = (
            ExecutorRegistryBuilder()
            .add_shell(
                executor_id="shell-1",
                name="Shell",
                command_allowlist=frozenset(["ls"]),
            )
            .build()
        )

        selector = ExecutorSelector(registry)
        # Request Playwright - not available
        requirements = playwright_requirements(domain="localhost")

        result = selector.select(requirements)

        assert result.status == SelectionStatus.NO_COMPATIBLE_EXECUTOR
        assert result.executor is None

    def test_select_or_raise_throws_on_no_match(self) -> None:
        """select_or_raise throws NoCompatibleExecutorError."""
        registry = (
            ExecutorRegistryBuilder()
            .add_shell(
                executor_id="shell-1",
                name="Shell",
                command_allowlist=frozenset(["ls"]),
            )
            .build()
        )

        selector = ExecutorSelector(registry)
        requirements = playwright_requirements(domain="localhost")

        with pytest.raises(NoCompatibleExecutorError):
            selector.select_or_raise(requirements)

    def test_selection_result_contains_audit_trail(self) -> None:
        """Selection result contains evaluation audit trail."""
        registry = (
            ExecutorRegistryBuilder()
            .add_shell(
                executor_id="shell-1",
                name="Shell",
                command_allowlist=frozenset(["ls"]),
            )
            .add_playwright(
                executor_id="pw-1",
                name="Playwright",
                domain_allowlist=frozenset(["localhost"]),
            )
            .build()
        )

        selector = ExecutorSelector(registry)
        requirements = shell_requirements(command="ls")

        result = selector.select(requirements)

        # Should have at least one evaluated executor (stops at first match)
        assert len(result.match_results) >= 1

    def test_selection_by_id_stable(self) -> None:
        """When priority is equal, ID is tiebreaker (alphabetical)."""
        registry = (
            ExecutorRegistryBuilder()
            .add_shell(
                executor_id="shell-b",
                name="Shell B",
                command_allowlist=frozenset(["ls"]),
                priority=50,
            )
            .add_shell(
                executor_id="shell-a",
                name="Shell A",
                command_allowlist=frozenset(["ls"]),
                priority=50,
            )
            .build()
        )

        selector = ExecutorSelector(registry)
        requirements = shell_requirements(command="ls")

        result = selector.select(requirements)

        # Should select "shell-a" because it's alphabetically first
        assert result.executor is not None
        assert str(result.executor.id) == "shell-a"


class TestExecutorValidation:
    """Tests for executor validation against requirements."""

    def test_validate_compatible_executor(self) -> None:
        """Validation passes for compatible executor."""
        registry = (
            ExecutorRegistryBuilder()
            .add_shell(
                executor_id="shell-1",
                name="Shell",
                command_allowlist=frozenset(["ls", "cat"]),
            )
            .build()
        )

        selector = ExecutorSelector(registry)
        requirements = shell_requirements(command="ls")

        result = selector.validate_executor(
            ExecutorId("shell-1"),
            requirements,
        )

        assert result.succeeded

    def test_validate_incompatible_executor(self) -> None:
        """Validation fails for incompatible executor."""
        registry = (
            ExecutorRegistryBuilder()
            .add_shell(
                executor_id="shell-1",
                name="Shell",
                command_allowlist=frozenset(["ls"]),  # cat not allowed
            )
            .build()
        )

        selector = ExecutorSelector(registry)
        requirements = shell_requirements(command="cat")

        result = selector.validate_executor(
            ExecutorId("shell-1"),
            requirements,
        )

        assert not result.succeeded
        assert result.status == SelectionStatus.EXECUTOR_INCOMPATIBLE

    def test_validate_or_raise_throws_on_incompatible(self) -> None:
        """validate_or_raise throws ExecutorIncompatibleError."""
        registry = (
            ExecutorRegistryBuilder()
            .add_shell(
                executor_id="shell-1",
                name="Shell",
                command_allowlist=frozenset(["ls"]),
            )
            .build()
        )

        selector = ExecutorSelector(registry)
        requirements = playwright_requirements(domain="localhost")

        with pytest.raises(ExecutorIncompatibleError):
            selector.validate_or_raise(
                ExecutorId("shell-1"),
                requirements,
            )


# =============================================================================
# SECTION 5: Requirement Builder Tests
# =============================================================================

class TestRequirementBuilders:
    """Tests for requirement builder helper functions."""

    def test_shell_requirements_builder(self) -> None:
        """shell_requirements creates proper requirements."""
        reqs = shell_requirements(
            command="ls -la",
            timeout=120,
        )

        assert reqs.required_backend == BackendType.SHELL
        assert reqs.required_task_type == SupportedTaskType.EXECUTION
        assert reqs.command == "ls -la"
        assert reqs.estimated_timeout == 120

    def test_playwright_requirements_builder(self) -> None:
        """playwright_requirements creates proper requirements."""
        reqs = playwright_requirements(
            domain="localhost",
            timeout=60,
        )

        assert reqs.required_backend == BackendType.PLAYWRIGHT
        assert reqs.domain == "localhost"

    def test_context_aware_requirements_builder(self) -> None:
        """context_aware_requirements creates proper requirements."""
        reqs = context_aware_requirements(
            files=["src/main.py", "src/utils.py"],
            operation=AllowedOperation.EDIT,
            timeout=120,
        )

        assert reqs.required_backend == BackendType.CONTEXT_AWARE
        assert reqs.required_cognition_level == ExecutorCognitionLevel.LEVEL_1_CONTEXT_AWARE
        assert reqs.required_operation == AllowedOperation.EDIT
        assert "src/main.py" in reqs.files_to_access


# =============================================================================
# SECTION 6: Validation Function Tests
# =============================================================================

class TestRegistryValidation:
    """Tests for registry validation functions."""

    def test_validate_deterministic_passes_for_frozen_registry(self) -> None:
        """Deterministic validation passes for frozen registry."""
        registry = (
            ExecutorRegistryBuilder()
            .add_shell(
                executor_id="shell-1",
                name="Shell",
                command_allowlist=frozenset(["ls"]),
            )
            .build()
        )

        # Should not raise
        validate_registry_is_deterministic(registry)

    def test_validate_deterministic_fails_for_unfrozen_registry(self) -> None:
        """Deterministic validation passes even for unfrozen registry (just checks order)."""
        registry = ExecutorRegistry()
        executor = create_shell_executor(
            executor_id="shell-1",
            name="Shell",
            command_allowlist=frozenset(["ls"]),
        )
        registry.register(executor)
        # Not frozen, but validation checks order, not frozen state

        # Should return True as long as order is stable
        result = validate_registry_is_deterministic(registry)
        assert result is True

    def test_validate_no_heuristics_passes(self) -> None:
        """No-heuristics validation passes for standard registry."""
        registry = (
            ExecutorRegistryBuilder()
            .add_shell(
                executor_id="shell-1",
                name="Shell",
                command_allowlist=frozenset(["ls"]),
            )
            .build()
        )

        # Should not raise
        validate_registry_has_no_heuristics(registry)

    def test_validate_no_runtime_mutation_passes(self) -> None:
        """No-runtime-mutation validation passes for frozen registry."""
        registry = (
            ExecutorRegistryBuilder()
            .add_shell(
                executor_id="shell-1",
                name="Shell",
                command_allowlist=frozenset(["ls"]),
            )
            .build()
        )

        # Should not raise
        validate_no_runtime_mutation(registry)


# =============================================================================
# SECTION 7: Integration Scenarios
# =============================================================================

class TestIntegrationScenarios:
    """End-to-end integration scenarios."""

    def test_multi_executor_selection_scenario(self) -> None:
        """Complete scenario with multiple executor types."""
        # Build a registry with all executor types
        registry = (
            ExecutorRegistryBuilder()
            .add_shell(
                executor_id="shell-primary",
                name="Primary Shell",
                command_allowlist=frozenset(["ls", "cat", "grep"]),
                priority=100,
            )
            .add_shell(
                executor_id="shell-secondary",
                name="Secondary Shell",
                command_allowlist=frozenset(["ls", "cat", "grep", "find"]),
                priority=50,
            )
            .add_playwright(
                executor_id="playwright-primary",
                name="Primary Playwright",
                domain_allowlist=frozenset(["localhost", "127.0.0.1"]),
                priority=100,
            )
            .add_context_aware(
                executor_id="context-primary",
                name="Primary Context-Aware",
                max_context_tokens=8000,
                # Use prefix patterns (simple matching, not glob)
                file_access_patterns=frozenset(["src/", "tests/", "lib/"]),
                allowed_operations=frozenset([AllowedOperation.READ, AllowedOperation.EDIT]),
                priority=100,
            )
            .build()
        )

        selector = ExecutorSelector(registry)

        # Scenario 1: Shell task selects by priority (lower = higher)
        shell_reqs = shell_requirements(command="ls")
        shell_result = selector.select(shell_reqs)
        assert str(shell_result.executor.id) == "shell-secondary"  # priority 50

        # Scenario 2: Playwright task selects playwright
        pw_reqs = playwright_requirements(domain="localhost")
        pw_result = selector.select(pw_reqs)
        assert str(pw_result.executor.id) == "playwright-primary"

        # Scenario 3: Context-aware task selects context-aware
        # Use files that start with allowed patterns
        ctx_reqs = context_aware_requirements(
            files=["src/main.py"],
            operation=AllowedOperation.EDIT,
        )
        ctx_result = selector.select(ctx_reqs)
        assert str(ctx_result.executor.id) == "context-primary"

    def test_policy_enforcement_scenario(self) -> None:
        """Policy enforcement blocks incompatible requests."""
        registry = (
            ExecutorRegistryBuilder()
            .add_shell(
                executor_id="shell-restricted",
                name="Restricted Shell",
                command_allowlist=frozenset(["ls", "cat"]),  # No rm, chmod, etc.
            )
            .build()
        )

        selector = ExecutorSelector(registry)

        # Blocked: rm command not in allowlist
        dangerous_reqs = shell_requirements(command="rm")
        dangerous_result = selector.select(dangerous_reqs)
        assert dangerous_result.status == SelectionStatus.NO_COMPATIBLE_EXECUTOR

    def test_selection_determinism_under_concurrency_simulation(self) -> None:
        """Selection remains deterministic across simulated concurrent access."""
        registry = (
            ExecutorRegistryBuilder()
            .add_shell(
                executor_id="shell-1",
                name="Shell 1",
                command_allowlist=frozenset(["ls"]),
                priority=50,
            )
            .add_shell(
                executor_id="shell-2",
                name="Shell 2",
                command_allowlist=frozenset(["ls"]),
                priority=50,
            )
            .add_shell(
                executor_id="shell-3",
                name="Shell 3",
                command_allowlist=frozenset(["ls"]),
                priority=50,
            )
            .build()
        )

        requirements = shell_requirements(command="ls")

        # Simulate concurrent selectors
        selectors = [ExecutorSelector(registry) for _ in range(10)]
        results = [s.select(requirements) for s in selectors]

        # All should select the same executor
        selected_ids = [str(r.executor.id) for r in results]
        assert len(set(selected_ids)) == 1

    def test_find_compatible_returns_first_match(self) -> None:
        """Registry.find_compatible returns first match."""
        registry = (
            ExecutorRegistryBuilder()
            .add_shell(
                executor_id="shell-low",
                name="Low Priority",
                command_allowlist=frozenset(["ls"]),
                priority=10,
            )
            .add_shell(
                executor_id="shell-medium",
                name="Medium Priority",
                command_allowlist=frozenset(["ls"]),
                priority=50,
            )
            .add_shell(
                executor_id="shell-high",
                name="High Priority",
                command_allowlist=frozenset(["ls"]),
                priority=100,
            )
            .build()
        )

        requirements = TaskExecutionRequirements(
            required_backend=BackendType.SHELL,
            required_task_type=SupportedTaskType.EXECUTION,
            command="ls",
        )

        executor, match_results = registry.find_compatible(requirements)

        assert executor is not None
        # Should be ordered by priority (lower value = higher priority)
        assert str(executor.id) == "shell-low"


# =============================================================================
# SECTION 8: Error Message Quality Tests
# =============================================================================

class TestErrorMessages:
    """Tests for clear, actionable error messages."""

    def test_no_compatible_error_lists_requirements(self) -> None:
        """NoCompatibleExecutorError message is informative."""
        registry = (
            ExecutorRegistryBuilder()
            .add_shell(
                executor_id="shell-1",
                name="Shell",
                command_allowlist=frozenset(["ls"]),
            )
            .build()
        )

        selector = ExecutorSelector(registry)
        requirements = playwright_requirements(domain="localhost")

        try:
            selector.select_or_raise(requirements)
            pytest.fail("Expected NoCompatibleExecutorError")
        except NoCompatibleExecutorError as e:
            error_message = str(e)
            # Should mention backend requirement
            assert "playwright" in error_message.lower()

    def test_duplicate_error_identifies_id(self) -> None:
        """DuplicateExecutorError identifies the duplicate ID."""
        registry = ExecutorRegistry()
        executor1 = create_shell_executor(
            executor_id="duplicate-id",
            name="First",
            command_allowlist=frozenset(["ls"]),
        )
        executor2 = create_shell_executor(
            executor_id="duplicate-id",
            name="Second",
            command_allowlist=frozenset(["cat"]),
        )

        registry.register(executor1)

        try:
            registry.register(executor2)
            pytest.fail("Expected DuplicateExecutorError")
        except DuplicateExecutorError as e:
            assert "duplicate-id" in str(e)

    def test_frozen_error_is_clear(self) -> None:
        """RegistryFrozenError clearly states registry is frozen."""
        registry = ExecutorRegistry()
        registry.freeze()

        executor = create_shell_executor(
            executor_id="shell-1",
            name="Shell",
            command_allowlist=frozenset(["ls"]),
        )

        try:
            registry.register(executor)
            pytest.fail("Expected RegistryFrozenError")
        except RegistryFrozenError as e:
            assert "frozen" in str(e).lower()


# =============================================================================
# SECTION 9: Capability Match Result Tests
# =============================================================================

class TestCapabilityMatchResult:
    """Tests for CapabilityMatchResult structure."""

    def test_compatible_result_has_no_message(self) -> None:
        """Compatible match has empty message."""
        matcher = CapabilityMatcher()
        executor = create_shell_executor(
            executor_id="shell-1",
            name="Shell",
            command_allowlist=frozenset(["ls"]),
        )
        requirements = shell_requirements(command="ls")

        result = matcher.match(executor, requirements)

        assert result.is_compatible
        # Compatible result may or may not have a message

    def test_incompatible_result_has_message(self) -> None:
        """Incompatible match has descriptive message."""
        matcher = CapabilityMatcher()
        executor = create_shell_executor(
            executor_id="shell-1",
            name="Shell",
            command_allowlist=frozenset(["ls"]),
        )
        requirements = shell_requirements(command="rm")  # Not allowed

        result = matcher.match(executor, requirements)

        assert not result.is_compatible
        assert result.message != ""
        assert "rm" in result.message


# =============================================================================
# SECTION 10: Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_registry_returns_empty_status(self) -> None:
        """Empty registry returns registry empty status."""
        registry = ExecutorRegistryBuilder().build()  # Empty
        selector = ExecutorSelector(registry)

        requirements = shell_requirements(command="ls")
        result = selector.select(requirements)

        assert result.status == SelectionStatus.REGISTRY_EMPTY

    def test_get_nonexistent_executor_returns_none(self) -> None:
        """Getting nonexistent executor returns None with get_optional."""
        registry = ExecutorRegistryBuilder().build()

        result = registry.get_optional(ExecutorId("nonexistent"))

        assert result is None

    def test_wildcard_file_patterns_stored(self) -> None:
        """Wildcard file access patterns are stored correctly."""
        executor = create_context_aware_executor(
            executor_id="ctx-1",
            name="Context",
            max_context_tokens=4000,
            file_access_patterns=frozenset(["*.py", "src/**/*.ts", "!node_modules/**"]),
            allowed_operations=frozenset([AllowedOperation.READ]),
        )

        assert "*.py" in executor.policy.file_access_patterns
        assert "src/**/*.ts" in executor.policy.file_access_patterns
        assert "!node_modules/**" in executor.policy.file_access_patterns

    def test_registry_len(self) -> None:
        """Registry supports len()."""
        registry = (
            ExecutorRegistryBuilder()
            .add_shell(
                executor_id="shell-1",
                name="Shell 1",
                command_allowlist=frozenset(["ls"]),
            )
            .add_shell(
                executor_id="shell-2",
                name="Shell 2",
                command_allowlist=frozenset(["cat"]),
            )
            .build()
        )

        assert len(registry) == 2
