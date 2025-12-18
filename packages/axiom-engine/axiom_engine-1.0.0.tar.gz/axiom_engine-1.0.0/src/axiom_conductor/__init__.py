"""
Axiom Conductor Package (Task Executor).

This package implements the deterministic control plane for Axiom.

Responsibility:
- Execute Task Graphs (DAGs)
- Manage parallelism, retries, and failures
- Emit structured execution signals
- Enforce execution order
- Manage Executor Registry (deterministic, immutable)
- Select executors based on explicit capability matching

Constraints:
- NO LLM CALLS
- NO architectural reasoning
- NO task decomposition
- NO code generation
- NO heuristics in executor selection
- NO runtime registry mutation

This component must remain boring and predictable.
"""

from axiom_conductor.model import (
    TaskExecutionState,
    TaskExecutionResult,
    TaskFailureReason,
    ExecutionEvent
)
from axiom_conductor.context import TaskExecutionContext
from axiom_conductor.interface import TaskExecutor
from axiom_conductor.executor import DeterministicTaskExecutor

# Registry models - declarative executor definitions
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

# Registry - immutable executor registry
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

# Selector - deterministic executor selection
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

# Remote dispatch is imported separately to avoid circular imports.
# Import directly from:
#   axiom_conductor.remote_dispatch

__all__ = [
    # Existing exports
    "TaskExecutionState",
    "TaskExecutionResult",
    "TaskFailureReason",
    "ExecutionEvent",
    "TaskExecutionContext",
    "TaskExecutor",
    "DeterministicTaskExecutor",
    # Registry models
    "ExecutorId",
    "ExecutorType",
    "ExecutorCognitionLevel",
    "BackendType",
    "SupportedTaskType",
    "AllowedOperation",
    "ExecutorCapabilities",
    "ExecutorPolicy",
    "ExecutorDefinition",
    "TaskExecutionRequirements",
    "CapabilityMatchResult",
    "CapabilityMatchStatus",
    "create_shell_executor",
    "create_playwright_executor",
    "create_context_aware_executor",
    # Registry
    "RegistryError",
    "DuplicateExecutorError",
    "InvalidDefinitionError",
    "ExecutorNotFoundError",
    "RegistryFrozenError",
    "CapabilityMatcher",
    "ExecutorRegistry",
    "ExecutorRegistryBuilder",
    "validate_registry_is_deterministic",
    "validate_registry_has_no_heuristics",
    "validate_no_runtime_mutation",
    # Selector
    "SelectionStatus",
    "ExecutorSelectionResult",
    "SelectionError",
    "NoCompatibleExecutorError",
    "ExecutorIncompatibleError",
    "ExecutorSelector",
    "shell_requirements",
    "playwright_requirements",
    "context_aware_requirements",
]
