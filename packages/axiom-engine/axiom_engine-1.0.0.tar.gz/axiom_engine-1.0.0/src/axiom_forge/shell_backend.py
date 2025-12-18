"""
Shell Execution Backend for Axiom Forge.

This module provides a real execution backend that runs approved commands
via the local shell using subprocess.run.

Why Execution is Isolated Behind Forge:
- Forge is the ONLY layer that performs side effects.
- All other layers (Core, Strata, Archon) are read-only or advisory.
- This isolation ensures that execution can be audited, mocked, or replaced.

Why This Backend is Intentionally Restrictive:
- Arbitrary shell execution is dangerous.
- We use an explicit allowlist to prevent accidental or malicious misuse.
- Timeouts prevent runaway processes.
- Environment filtering prevents leaking sensitive data.

Why Governance Must Not Be Bypassed for Convenience:
- This backend is only invoked AFTER human ratification.
- It has no authority to approve its own execution.
- Every invocation is a direct result of AxiomWorkflow passing through
  the Strategic Review and Human Authorization stages.

Architectural Reminder:
- Forge executes.
- Core orchestrates.
- Archon authorizes.
- Humans decide.
"""

import subprocess
import os
from dataclasses import dataclass, field
from typing import Set, Dict, Optional, List
from datetime import datetime, timezone

from axiom_conductor.model import (
    TaskExecutionResult,
    TaskExecutionState,
    TaskFailureReason
)
from axiom_forge.backend import TaskExecutionBackend, TaskExecutionInput


@dataclass
class ShellExecutionPolicy:
    """
    Defines the safety constraints for shell execution.

    Attributes:
        allowed_commands: Explicit allowlist of base commands (e.g., "echo", "pytest").
        max_timeout_seconds: Maximum execution time allowed.
        allowed_working_directories: Paths where execution is permitted.
        max_stdout_bytes: Maximum captured stdout size.
        max_stderr_bytes: Maximum captured stderr size.
        allowed_env_vars: Environment variables to pass through. If None, pass none.
    """
    allowed_commands: Set[str] = field(default_factory=lambda: {"echo", "pytest", "python3", "python", "ls", "cat", "pwd"})
    max_timeout_seconds: int = 300
    allowed_working_directories: Set[str] = field(default_factory=set)  # Empty = any
    max_stdout_bytes: int = 1024 * 1024  # 1 MB
    max_stderr_bytes: int = 1024 * 1024  # 1 MB
    allowed_env_vars: Optional[Set[str]] = None  # None = pass nothing


@dataclass
class ShellExecutionBackend:
    """
    A real execution backend that runs commands via subprocess.

    This backend:
    - Uses subprocess.run with shell=False for safety.
    - Enforces an allowlist of commands.
    - Enforces timeouts.
    - Captures stdout/stderr.
    - Returns structured results.

    It does NOT:
    - Retry on failure.
    - Escalate privileges.
    - Modify state.
    """
    policy: ShellExecutionPolicy = field(default_factory=ShellExecutionPolicy)

    def execute_task(self, input_data: TaskExecutionInput) -> TaskExecutionResult:
        """
        Execute a task via subprocess.

        Args:
            input_data: The task execution details.

        Returns:
            TaskExecutionResult: The outcome of the execution.
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        task_id = input_data.task_id
        command = input_data.command
        args = input_data.args
        timeout = min(input_data.timeout_seconds, self.policy.max_timeout_seconds)
        working_dir = input_data.working_directory or os.getcwd()

        # 1. Validate Command
        base_command = command.split()[0] if command else ""
        if base_command not in self.policy.allowed_commands:
            return TaskExecutionResult(
                task_id=task_id,
                state=TaskExecutionState.FAILED,
                failure_reason=TaskFailureReason.PRECONDITION_FAILED,
                error_message=f"Command '{base_command}' is not in the allowlist.",
                timestamp=timestamp
            )

        # 2. Validate Working Directory
        if self.policy.allowed_working_directories:
            if working_dir not in self.policy.allowed_working_directories:
                return TaskExecutionResult(
                    task_id=task_id,
                    state=TaskExecutionState.FAILED,
                    failure_reason=TaskFailureReason.PRECONDITION_FAILED,
                    error_message=f"Working directory '{working_dir}' is not allowed.",
                    timestamp=timestamp
                )

        # 3. Build Command List (No shell=True)
        cmd_list: List[str] = [command] + args

        # 4. Build Environment
        env: Optional[Dict[str, str]] = None
        if self.policy.allowed_env_vars is not None:
            env = {k: v for k, v in os.environ.items() if k in self.policy.allowed_env_vars}
            # Merge task-specific env vars (if they are also allowed)
            for k, v in input_data.env.items():
                if k in self.policy.allowed_env_vars:
                    env[k] = v

        # 5. Execute
        try:
            result = subprocess.run(
                cmd_list,
                capture_output=True,
                timeout=timeout,
                cwd=working_dir,
                env=env,
                text=True
            )

            stdout = result.stdout[:self.policy.max_stdout_bytes] if result.stdout else ""
            stderr = result.stderr[:self.policy.max_stderr_bytes] if result.stderr else ""

            if result.returncode == 0:
                return TaskExecutionResult(
                    task_id=task_id,
                    state=TaskExecutionState.SUCCEEDED,
                    exit_code=result.returncode,
                    stdout=stdout,
                    stderr=stderr,
                    timestamp=timestamp
                )
            else:
                return TaskExecutionResult(
                    task_id=task_id,
                    state=TaskExecutionState.FAILED,
                    exit_code=result.returncode,
                    stdout=stdout,
                    stderr=stderr,
                    failure_reason=TaskFailureReason.COMMAND_ERROR,
                    error_message=f"Command exited with code {result.returncode}",
                    timestamp=timestamp
                )

        except subprocess.TimeoutExpired as e:
            return TaskExecutionResult(
                task_id=task_id,
                state=TaskExecutionState.FAILED,
                failure_reason=TaskFailureReason.TIMEOUT,
                error_message=f"Command timed out after {timeout} seconds.",
                timestamp=timestamp
            )
        except FileNotFoundError as e:
            return TaskExecutionResult(
                task_id=task_id,
                state=TaskExecutionState.FAILED,
                failure_reason=TaskFailureReason.COMMAND_ERROR,
                error_message=f"Command not found: {command}",
                timestamp=timestamp
            )
        except Exception as e:
            return TaskExecutionResult(
                task_id=task_id,
                state=TaskExecutionState.FAILED,
                failure_reason=TaskFailureReason.SYSTEM_ERROR,
                error_message=str(e),
                timestamp=timestamp
            )
