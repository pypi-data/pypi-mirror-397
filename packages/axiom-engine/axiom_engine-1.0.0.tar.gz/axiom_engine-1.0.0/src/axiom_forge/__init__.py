"""
Axiom Forge Package (Execution Layer).

This package implements the Execution Layer of Axiom.

Responsibility:
- Perform work (code generation, refactoring, testing)
- Invoke external tools (Copilot, Playwright, CI)
- Execute assigned tasks

Constraints:
- Stateless
- Minimal context
- NEVER declare success
- NEVER make architectural decisions
- NEVER infer global intent
"""

from axiom_forge.backend import (
    TaskExecutionBackend,
    TaskExecutionInput
)
from axiom_forge.mock_backend import MockExecutionBackend
from axiom_forge.shell_backend import (
    ShellExecutionBackend,
    ShellExecutionPolicy
)
from axiom_forge.playwright_backend import (
    PlaywrightExecutionBackend,
    PlaywrightExecutionPolicy,
    PlaywrightTaskInput,
    PlaywrightBrowser,
    PlaywrightScriptType,
    REGISTERED_SCRIPTS,
)

# Remote execution modules are imported separately to avoid
# triggering circular imports during package initialization.
# Import directly from:
#   axiom_forge.remote_protocol
#   axiom_forge.remote_auth
#   axiom_forge.remote_stub

# Context-aware execution modules are imported separately to avoid
# triggering circular imports during package initialization.
# Import directly from:
#   axiom_forge.context_aware_models
#   axiom_forge.context_aware_backend

__all__ = [
    # Core interfaces
    "TaskExecutionBackend",
    "TaskExecutionInput",
    # Mock backend (testing)
    "MockExecutionBackend",
    # Shell backend
    "ShellExecutionBackend",
    "ShellExecutionPolicy",
    # Playwright backend
    "PlaywrightExecutionBackend",
    "PlaywrightExecutionPolicy",
    "PlaywrightTaskInput",
    "PlaywrightBrowser",
    "PlaywrightScriptType",
    "REGISTERED_SCRIPTS",
]
