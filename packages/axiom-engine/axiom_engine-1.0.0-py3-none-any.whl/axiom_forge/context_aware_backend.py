"""
Context-Aware Execution Backend for Axiom Forge.

This module implements a context-aware task execution backend that uses
an LLM to understand local code context while strictly following
explicit instructions without agency, authority, or autonomy.

CORE PRINCIPLE:
    Executors may understand context.
    Executors may NOT decide intent.

This backend:
    - Receives an explicit, fixed instruction
    - Uses an LLM ONLY to interpret local code context
    - Applies changes strictly within the given scope
    - Produces a deterministic result (usually a diff)
    - Has zero memory, zero learning, zero initiative

This is NOT an agent.
This is NOT a planner.
This is NOT a reviewer.

LLM Usage Constraints:
    MAY:
        - Parse syntax
        - Understand scope
        - Resolve local symbol references
        - Apply formatting rules
    MAY NOT:
        - Suggest alternative approaches
        - Refactor beyond instruction
        - Fix unrelated issues
        - Add comments or documentation unless explicitly instructed
        - Escalate scope

Hard Constraints (Programmatically Enforced):
    - File access: MUST NOT read files outside whitelist
    - Output: EDIT operations MUST return a diff/patch only
    - Output: READ operations MUST return summaries only
    - Scope: MUST NOT modify unlisted files
    - Scope: MUST NOT introduce new symbols outside scope
    - Patch limits: Enforce max_patch_size
    - Tokens: Enforce strict token budgets
    - Execution: Single-shot only, no retries, no loops, no memory
"""

import time
import re
from dataclasses import dataclass, field
from typing import Protocol, Dict, Optional, List, Set, Callable
from pathlib import Path

from axiom_forge.context_aware_models import (
    ContextAwareExecutionInput,
    ContextAwareExecutionResult,
    ContextAwareExecutionStatus,
    OperationType,
    Violation,
    ViolationType,
    FormattingRules,
    create_failed_result,
    create_edit_result,
    create_read_result,
    CONTEXT_AWARE_EXECUTION_LABEL,
    MAX_PATCH_SIZE_HARD_LIMIT,
    MAX_CONTEXT_TOKENS_HARD_LIMIT,
)


# =============================================================================
# LLM BACKEND PROTOCOL
# =============================================================================


class ContextAwareLLMBackend(Protocol):
    """
    Protocol for LLM backends used by context-aware executors.

    The LLM is used ONLY for local code understanding, not for
    planning, decision-making, or scope expansion.
    """

    def complete(self, prompt: str, max_tokens: int) -> str:
        """
        Get a completion from the LLM.

        Args:
            prompt: The prompt to send to the LLM.
            max_tokens: Maximum tokens in the response.

        Returns:
            The LLM's response text.
        """
        ...


# =============================================================================
# FILE LOADER PROTOCOL
# =============================================================================


class FileLoader(Protocol):
    """
    Protocol for loading file contents.

    This abstraction allows testing without actual file system access.
    """

    def load(self, file_path: str) -> Optional[str]:
        """
        Load the contents of a file.

        Args:
            file_path: Path to the file to load.

        Returns:
            File contents, or None if file doesn't exist.
        """
        ...

    def exists(self, file_path: str) -> bool:
        """
        Check if a file exists.

        Args:
            file_path: Path to check.

        Returns:
            True if file exists, False otherwise.
        """
        ...


# =============================================================================
# DEFAULT FILE LOADER
# =============================================================================


@dataclass
class DefaultFileLoader:
    """
    Default file loader that reads from the file system.

    This loader is intentionally simple and has no caching or
    side effects beyond reading files.
    """

    def load(self, file_path: str) -> Optional[str]:
        """
        Load file contents from the file system.

        Args:
            file_path: Path to the file.

        Returns:
            File contents, or None if file doesn't exist.
        """
        try:
            path = Path(file_path)
            if path.exists() and path.is_file():
                return path.read_text(encoding="utf-8")
            return None
        except (OSError, IOError, UnicodeDecodeError):
            return None

    def exists(self, file_path: str) -> bool:
        """
        Check if file exists.

        Args:
            file_path: Path to check.

        Returns:
            True if exists and is a file.
        """
        try:
            path = Path(file_path)
            return path.exists() and path.is_file()
        except OSError:
            return False


# =============================================================================
# MOCK LLM BACKEND (FOR TESTING)
# =============================================================================


@dataclass
class MockContextAwareLLMBackend:
    """
    A mock LLM backend for testing.

    This backend returns predefined responses based on the operation type.
    It simulates LLM behavior without actual API calls.
    """

    # Predefined responses for testing
    edit_response: str = ""
    read_response: str = ""
    should_fail: bool = False
    failure_message: str = "Mock LLM failure"

    # Tracking for test assertions
    prompts_received: List[str] = field(default_factory=list)
    call_count: int = 0

    def complete(self, prompt: str, max_tokens: int) -> str:
        """
        Return a mock completion.

        Args:
            prompt: The prompt (recorded for testing).
            max_tokens: Ignored in mock.

        Returns:
            Predefined response based on operation type in prompt.
        """
        self.prompts_received.append(prompt)
        self.call_count += 1

        if self.should_fail:
            raise RuntimeError(self.failure_message)

        # Determine operation type from prompt
        if "OPERATION: EDIT" in prompt:
            return self.edit_response
        elif "OPERATION: READ" in prompt:
            return self.read_response
        else:
            return self.edit_response or self.read_response


# =============================================================================
# PROMPT BUILDER
# =============================================================================


# Prompt template for context-aware execution
# This template is designed to:
# 1. Include the exact instruction verbatim
# 2. Explicitly forbid extra changes
# 3. Require diff-only response for edits
# 4. Require summary-only response for reads

EDIT_PROMPT_TEMPLATE = """
{label}

You are a context-aware code executor. Your ONLY task is to apply the
EXACT instruction below to the provided code files. You have NO AGENCY.

=== CRITICAL CONSTRAINTS ===
1. Apply ONLY the exact instruction - nothing more, nothing less.
2. Do NOT suggest alternative approaches.
3. Do NOT refactor beyond the instruction.
4. Do NOT fix unrelated issues.
5. Do NOT add comments or documentation unless explicitly instructed.
6. Do NOT introduce new symbols outside the scope of the instruction.
7. Your response MUST be a unified diff ONLY.
8. If you cannot apply the instruction exactly, respond with: CANNOT_APPLY: <reason>

=== OPERATION: EDIT ===

=== INSTRUCTION (APPLY EXACTLY) ===
{instruction}

=== FILES ===
{files_content}

{formatting_section}

=== RESPONSE FORMAT ===
Respond with ONLY a unified diff. No explanation. No commentary.
Example format:
```diff
--- a/path/to/file.py
+++ b/path/to/file.py
@@ -10,5 +10,7 @@
 existing line
-removed line
+added line
 existing line
```

If the instruction cannot be applied exactly, respond with:
CANNOT_APPLY: <specific reason>

YOUR DIFF:
""".strip()


READ_PROMPT_TEMPLATE = """
{label}

You are a context-aware code reader. Your ONLY task is to extract the
EXACT information requested below from the provided code files. You have NO AGENCY.

=== CRITICAL CONSTRAINTS ===
1. Extract ONLY what is explicitly requested - nothing more.
2. Do NOT suggest improvements.
3. Do NOT analyze beyond the request.
4. Do NOT provide commentary.
5. Your response MUST be a concise summary ONLY.
6. If you cannot extract the requested information, respond with: CANNOT_EXTRACT: <reason>

=== OPERATION: READ ===

=== INSTRUCTION (EXTRACT EXACTLY) ===
{instruction}

=== FILES ===
{files_content}

=== RESPONSE FORMAT ===
Respond with ONLY a concise summary of the requested information.
No explanation. No suggestions. No commentary.

If the information cannot be extracted, respond with:
CANNOT_EXTRACT: <specific reason>

YOUR SUMMARY:
""".strip()


@dataclass
class PromptBuilder:
    """
    Builds prompts for context-aware execution.

    The prompts are designed to:
    1. Include the exact instruction verbatim
    2. Explicitly forbid extra changes
    3. Require diff-only or summary-only responses
    """

    def build_edit_prompt(
        self,
        instruction: str,
        files_content: Dict[str, str],
        formatting_rules: Optional[FormattingRules] = None,
    ) -> str:
        """
        Build a prompt for an EDIT operation.

        Args:
            instruction: The exact instruction to apply.
            files_content: Dictionary of file paths to contents.
            formatting_rules: Optional formatting constraints.

        Returns:
            The formatted prompt string.
        """
        # Build files section
        files_section = self._format_files(files_content)

        # Build formatting section
        formatting_section = ""
        if formatting_rules:
            formatting_section = f"""
=== FORMATTING RULES (APPLY STRICTLY) ===
- Indent style: {formatting_rules.indent_style}
- Indent size: {formatting_rules.indent_size}
- Line ending: {formatting_rules.line_ending}
- Max line length: {formatting_rules.max_line_length or 'none'}
- Trailing newline: {formatting_rules.trailing_newline}
""".strip()

        return EDIT_PROMPT_TEMPLATE.format(
            label=CONTEXT_AWARE_EXECUTION_LABEL,
            instruction=instruction,
            files_content=files_section,
            formatting_section=formatting_section,
        )

    def build_read_prompt(
        self,
        instruction: str,
        files_content: Dict[str, str],
    ) -> str:
        """
        Build a prompt for a READ operation.

        Args:
            instruction: The exact instruction to apply.
            files_content: Dictionary of file paths to contents.

        Returns:
            The formatted prompt string.
        """
        files_section = self._format_files(files_content)

        return READ_PROMPT_TEMPLATE.format(
            label=CONTEXT_AWARE_EXECUTION_LABEL,
            instruction=instruction,
            files_content=files_section,
        )

    def _format_files(self, files_content: Dict[str, str]) -> str:
        """
        Format file contents for inclusion in prompt.

        Args:
            files_content: Dictionary of file paths to contents.

        Returns:
            Formatted string with all file contents.
        """
        sections = []
        for file_path, content in sorted(files_content.items()):
            sections.append(f"--- FILE: {file_path} ---\n{content}\n--- END FILE ---")
        return "\n\n".join(sections)


# =============================================================================
# VIOLATION DETECTOR
# =============================================================================


@dataclass
class ViolationDetector:
    """
    Detects constraint violations in execution inputs and outputs.

    This detector is responsible for enforcing all hard constraints
    on context-aware execution.
    """

    def validate_input(
        self,
        input_data: ContextAwareExecutionInput,
    ) -> List[Violation]:
        """
        Validate execution input for constraint violations.

        Args:
            input_data: The execution input to validate.

        Returns:
            List of violations found (empty if valid).
        """
        violations: List[Violation] = []

        # Check hard limits
        if input_data.max_patch_size > MAX_PATCH_SIZE_HARD_LIMIT:
            violations.append(
                Violation(
                    violation_type=ViolationType.PATCH_SIZE_OVERFLOW,
                    description=f"max_patch_size {input_data.max_patch_size} exceeds hard limit {MAX_PATCH_SIZE_HARD_LIMIT}",
                    evidence=str(input_data.max_patch_size),
                )
            )

        if input_data.max_context_tokens > MAX_CONTEXT_TOKENS_HARD_LIMIT:
            violations.append(
                Violation(
                    violation_type=ViolationType.TOKEN_BUDGET_EXCEEDED,
                    description=f"max_context_tokens {input_data.max_context_tokens} exceeds hard limit {MAX_CONTEXT_TOKENS_HARD_LIMIT}",
                    evidence=str(input_data.max_context_tokens),
                )
            )

        return violations

    def validate_file_access(
        self,
        requested_files: Set[str],
        allowed_files: Set[str],
    ) -> List[Violation]:
        """
        Validate that only allowed files are accessed.

        Args:
            requested_files: Files that were accessed.
            allowed_files: Files that are allowed.

        Returns:
            List of violations found.
        """
        violations: List[Violation] = []
        unauthorized = requested_files - allowed_files

        for file_path in unauthorized:
            violations.append(
                Violation(
                    violation_type=ViolationType.UNAUTHORIZED_FILE_READ,
                    description=f"Attempted to access file not in whitelist: {file_path}",
                    file_path=file_path,
                )
            )

        return violations

    def validate_diff_output(
        self,
        diff: str,
        allowed_files: Set[str],
        max_patch_size: int,
    ) -> List[Violation]:
        """
        Validate diff output for constraint violations.

        Args:
            diff: The produced diff.
            allowed_files: Files that are allowed to be modified.
            max_patch_size: Maximum allowed patch size.

        Returns:
            List of violations found.
        """
        violations: List[Violation] = []

        # Check patch size
        if len(diff.encode("utf-8")) > max_patch_size:
            violations.append(
                Violation(
                    violation_type=ViolationType.PATCH_SIZE_OVERFLOW,
                    description=f"Diff size {len(diff.encode('utf-8'))} exceeds max {max_patch_size}",
                    evidence=f"Size: {len(diff.encode('utf-8'))} bytes",
                )
            )

        # Check for modified files not in whitelist
        modified_files = self._extract_files_from_diff(diff)
        # Normalize allowed_files for comparison (strip leading slash, handle relative paths)
        normalized_allowed = set()
        for f in allowed_files:
            normalized_allowed.add(f)
            normalized_allowed.add(f.lstrip("/"))
            if not f.startswith("/"):
                normalized_allowed.add("/" + f)
        
        for file_path in modified_files:
            # Check both with and without leading slash
            if file_path not in normalized_allowed and "/" + file_path not in normalized_allowed:
                violations.append(
                    Violation(
                        violation_type=ViolationType.UNAUTHORIZED_FILE_WRITE,
                        description=f"Diff modifies file not in whitelist: {file_path}",
                        file_path=file_path,
                    )
                )

        # Check for valid diff format
        if diff.strip() and not self._is_valid_diff_format(diff):
            violations.append(
                Violation(
                    violation_type=ViolationType.INVALID_DIFF_FORMAT,
                    description="Output is not in valid unified diff format",
                    evidence=diff[:200] if len(diff) > 200 else diff,
                )
            )

        return violations

    def validate_llm_response(
        self,
        response: str,
        operation_type: OperationType,
    ) -> List[Violation]:
        """
        Validate LLM response for constraint violations.

        Args:
            response: The LLM's response.
            operation_type: The operation type (READ or EDIT).

        Returns:
            List of violations found.
        """
        violations: List[Violation] = []

        # Check for refusal patterns
        if response.strip().startswith("CANNOT_APPLY:") or response.strip().startswith("CANNOT_EXTRACT:"):
            violations.append(
                Violation(
                    violation_type=ViolationType.LLM_REFUSED,
                    description="LLM could not apply the instruction",
                    evidence=response.strip(),
                )
            )
            return violations

        # Check for unsolicited suggestions
        suggestion_patterns = [
            r"(?i)i would suggest",
            r"(?i)you might want to",
            r"(?i)a better approach",
            r"(?i)consider also",
            r"(?i)additionally,?\s+you",
            r"(?i)i also noticed",
            r"(?i)while i was",
            r"(?i)i took the liberty",
        ]
        for pattern in suggestion_patterns:
            if re.search(pattern, response):
                violations.append(
                    Violation(
                        violation_type=ViolationType.UNSOLICITED_SUGGESTION,
                        description="LLM included unsolicited suggestions",
                        evidence=response[:300] if len(response) > 300 else response,
                    )
                )
                break

        # For EDIT operations, check that response is diff-like
        if operation_type == OperationType.EDIT:
            if response.strip() and not self._looks_like_diff(response):
                violations.append(
                    Violation(
                        violation_type=ViolationType.NON_DIFF_OUTPUT,
                        description="EDIT operation did not return diff-only output",
                        evidence=response[:300] if len(response) > 300 else response,
                    )
                )

        return violations

    def _extract_files_from_diff(self, diff: str) -> Set[str]:
        """
        Extract file paths from a unified diff.

        Args:
            diff: The unified diff.

        Returns:
            Set of file paths mentioned in the diff.
        """
        files: Set[str] = set()
        # Match --- a/path/to/file and +++ b/path/to/file patterns
        for line in diff.split("\n"):
            if line.startswith("--- ") or line.startswith("+++ "):
                # Extract path after a/ or b/ prefix
                parts = line.split(None, 1)
                if len(parts) >= 2:
                    path = parts[1]
                    # Remove a/ or b/ prefix if present
                    if path.startswith("a/") or path.startswith("b/"):
                        path = path[2:]
                    # Skip /dev/null
                    if path != "/dev/null":
                        files.add(path)
        return files

    def _is_valid_diff_format(self, diff: str) -> bool:
        """
        Check if text is in valid unified diff format.

        Args:
            diff: The text to check.

        Returns:
            True if valid diff format.
        """
        lines = diff.strip().split("\n")
        has_file_header = False
        has_hunk_header = False

        for line in lines:
            if line.startswith("--- ") or line.startswith("+++ "):
                has_file_header = True
            if line.startswith("@@"):
                has_hunk_header = True

        return has_file_header and has_hunk_header

    def _looks_like_diff(self, text: str) -> bool:
        """
        Check if text looks like it contains a diff.

        More lenient than _is_valid_diff_format.

        Args:
            text: The text to check.

        Returns:
            True if text appears to contain diff content.
        """
        # Check for diff markers
        diff_markers = ["--- ", "+++ ", "@@ ", "```diff"]
        for marker in diff_markers:
            if marker in text:
                return True

        # Check for line-level changes
        lines = text.split("\n")
        has_additions = any(line.startswith("+") and not line.startswith("+++") for line in lines)
        has_deletions = any(line.startswith("-") and not line.startswith("---") for line in lines)

        return has_additions or has_deletions


# =============================================================================
# DIFF PARSER
# =============================================================================


@dataclass
class DiffParser:
    """
    Parses and validates unified diff output from the LLM.
    """

    def extract_diff(self, response: str) -> str:
        """
        Extract the diff portion from an LLM response.

        Args:
            response: The full LLM response.

        Returns:
            The extracted diff content.
        """
        # Try to extract from code block first
        code_block_match = re.search(r"```diff\n(.*?)```", response, re.DOTALL)
        if code_block_match:
            return code_block_match.group(1).strip()

        # Try generic code block
        generic_block_match = re.search(r"```\n(.*?)```", response, re.DOTALL)
        if generic_block_match:
            content = generic_block_match.group(1).strip()
            # Verify it looks like a diff
            if "---" in content or "+++" in content or "@@" in content:
                return content

        # If no code block, try to find diff directly
        lines = response.split("\n")
        diff_lines = []
        in_diff = False

        for line in lines:
            if line.startswith("--- ") or line.startswith("+++ "):
                in_diff = True
            if in_diff:
                # Stop at clearly non-diff content
                if line.strip() and not any([
                    line.startswith("+"),
                    line.startswith("-"),
                    line.startswith("@"),
                    line.startswith(" "),
                    line.startswith("\\"),  # \ No newline at end
                    line.startswith("diff "),
                    line.startswith("index "),
                    line.strip() == "",
                ]):
                    break
                diff_lines.append(line)

        return "\n".join(diff_lines).strip()


# =============================================================================
# CONTEXT-AWARE EXECUTION BACKEND
# =============================================================================


@dataclass
class ContextAwareExecutionBackend:
    """
    A context-aware execution backend that uses an LLM to understand
    local code context while strictly following explicit instructions.

    This backend:
        - Receives an explicit, fixed instruction
        - Uses an LLM ONLY to interpret local code context
        - Applies changes strictly within the given scope
        - Produces a deterministic result (usually a diff)
        - Has zero memory, zero learning, zero initiative

    Hard Constraints (Enforced Programmatically):
        - File access: MUST NOT read files outside whitelist
        - Output: EDIT operations MUST return a diff/patch only
        - Output: READ operations MUST return summaries only
        - Scope: MUST NOT modify unlisted files
        - Scope: MUST NOT introduce new symbols outside scope
        - Patch limits: Enforce max_patch_size
        - Tokens: Enforce strict token budgets
        - Execution: Single-shot only, no retries, no loops, no memory
    """

    llm_backend: ContextAwareLLMBackend
    file_loader: FileLoader = field(default_factory=DefaultFileLoader)
    prompt_builder: PromptBuilder = field(default_factory=PromptBuilder)
    violation_detector: ViolationDetector = field(default_factory=ViolationDetector)
    diff_parser: DiffParser = field(default_factory=DiffParser)

    # NO MEMORY: This backend has no state between executions
    # Each execution is completely independent

    def execute(
        self,
        input_data: ContextAwareExecutionInput,
    ) -> ContextAwareExecutionResult:
        """
        Execute a context-aware task.

        This method:
        1. Validates input constraints
        2. Loads only whitelisted files
        3. Builds a minimal prompt
        4. Invokes the LLM exactly once (single-shot)
        5. Validates the output
        6. Returns a deterministic result

        No retries. No loops. No memory.

        Args:
            input_data: The execution input.

        Returns:
            The execution result.
        """
        start_time = time.time()
        tokens_used = 0

        # Step 1: Validate input constraints
        input_violations = self.violation_detector.validate_input(input_data)
        if input_violations:
            return create_failed_result(
                task_id=input_data.task_id,
                violations=input_violations,
                error_message="Input validation failed",
                execution_time_ms=int((time.time() - start_time) * 1000),
            )

        # Step 2: Load only whitelisted files
        files_content: Dict[str, str] = {}
        touched_files: Set[str] = set()

        for file_path in input_data.allowed_files:
            content = self.file_loader.load(file_path)
            if content is not None:
                files_content[file_path] = content
                touched_files.add(file_path)

        # If no files could be loaded, fail
        if not files_content:
            return create_failed_result(
                task_id=input_data.task_id,
                violations=[
                    Violation(
                        violation_type=ViolationType.LLM_INVALID_RESPONSE,
                        description="No files could be loaded from whitelist",
                    )
                ],
                error_message="No accessible files in whitelist",
                execution_time_ms=int((time.time() - start_time) * 1000),
            )

        # Step 3: Build prompt
        if input_data.operation_type == OperationType.EDIT:
            prompt = self.prompt_builder.build_edit_prompt(
                instruction=input_data.explicit_instruction,
                files_content=files_content,
                formatting_rules=input_data.formatting_rules,
            )
        else:
            prompt = self.prompt_builder.build_read_prompt(
                instruction=input_data.explicit_instruction,
                files_content=files_content,
            )

        # Estimate tokens (rough: ~4 chars per token)
        estimated_tokens = len(prompt) // 4
        if estimated_tokens > input_data.max_context_tokens:
            return create_failed_result(
                task_id=input_data.task_id,
                violations=[
                    Violation(
                        violation_type=ViolationType.TOKEN_BUDGET_EXCEEDED,
                        description=f"Estimated tokens {estimated_tokens} exceeds budget {input_data.max_context_tokens}",
                    )
                ],
                error_message="Token budget exceeded",
                execution_time_ms=int((time.time() - start_time) * 1000),
            )

        # Step 4: Invoke LLM (single-shot, no retries)
        try:
            response = self.llm_backend.complete(
                prompt=prompt,
                max_tokens=input_data.max_context_tokens // 2,  # Reserve half for response
            )
            tokens_used = estimated_tokens + (len(response) // 4)
        except Exception as e:
            return create_failed_result(
                task_id=input_data.task_id,
                violations=[
                    Violation(
                        violation_type=ViolationType.LLM_INVALID_RESPONSE,
                        description=f"LLM invocation failed: {str(e)}",
                    )
                ],
                error_message=f"LLM error: {str(e)}",
                execution_time_ms=int((time.time() - start_time) * 1000),
                tokens_used=tokens_used,
            )

        # Step 5: Validate LLM response
        response_violations = self.violation_detector.validate_llm_response(
            response=response,
            operation_type=input_data.operation_type,
        )
        if response_violations:
            return create_failed_result(
                task_id=input_data.task_id,
                violations=response_violations,
                error_message="LLM response validation failed",
                execution_time_ms=int((time.time() - start_time) * 1000),
                tokens_used=tokens_used,
            )

        # Step 6: Process response based on operation type
        execution_time_ms = int((time.time() - start_time) * 1000)

        if input_data.operation_type == OperationType.EDIT:
            return self._process_edit_response(
                task_id=input_data.task_id,
                response=response,
                allowed_files=set(input_data.allowed_files),
                max_patch_size=input_data.max_patch_size,
                touched_files=touched_files,
                execution_time_ms=execution_time_ms,
                tokens_used=tokens_used,
            )
        else:
            return self._process_read_response(
                task_id=input_data.task_id,
                response=response,
                touched_files=touched_files,
                execution_time_ms=execution_time_ms,
                tokens_used=tokens_used,
            )

    def _process_edit_response(
        self,
        task_id: str,
        response: str,
        allowed_files: Set[str],
        max_patch_size: int,
        touched_files: Set[str],
        execution_time_ms: int,
        tokens_used: int,
    ) -> ContextAwareExecutionResult:
        """
        Process an EDIT operation response.

        Args:
            task_id: The task identifier.
            response: The LLM response.
            allowed_files: Allowed file paths.
            max_patch_size: Maximum patch size.
            touched_files: Files that were loaded.
            execution_time_ms: Execution time.
            tokens_used: Tokens consumed.

        Returns:
            The execution result.
        """
        # Extract diff from response
        diff = self.diff_parser.extract_diff(response)

        if not diff.strip():
            return create_failed_result(
                task_id=task_id,
                violations=[
                    Violation(
                        violation_type=ViolationType.NON_DIFF_OUTPUT,
                        description="EDIT operation produced no diff output",
                        evidence=response[:200] if len(response) > 200 else response,
                    )
                ],
                error_message="No diff produced",
                execution_time_ms=execution_time_ms,
                tokens_used=tokens_used,
            )

        # Validate diff output
        diff_violations = self.violation_detector.validate_diff_output(
            diff=diff,
            allowed_files=allowed_files,
            max_patch_size=max_patch_size,
        )
        if diff_violations:
            return create_failed_result(
                task_id=task_id,
                violations=diff_violations,
                error_message="Diff validation failed",
                execution_time_ms=execution_time_ms,
                tokens_used=tokens_used,
            )

        return create_edit_result(
            task_id=task_id,
            diff=diff,
            touched_files=frozenset(touched_files),
            execution_time_ms=execution_time_ms,
            tokens_used=tokens_used,
        )

    def _process_read_response(
        self,
        task_id: str,
        response: str,
        touched_files: Set[str],
        execution_time_ms: int,
        tokens_used: int,
    ) -> ContextAwareExecutionResult:
        """
        Process a READ operation response.

        Args:
            task_id: The task identifier.
            response: The LLM response.
            touched_files: Files that were loaded.
            execution_time_ms: Execution time.
            tokens_used: Tokens consumed.

        Returns:
            The execution result.
        """
        # For READ operations, the response is the summary
        summary = response.strip()

        if not summary:
            return create_failed_result(
                task_id=task_id,
                violations=[
                    Violation(
                        violation_type=ViolationType.LLM_INVALID_RESPONSE,
                        description="READ operation produced empty summary",
                    )
                ],
                error_message="No summary produced",
                execution_time_ms=execution_time_ms,
                tokens_used=tokens_used,
            )

        return create_read_result(
            task_id=task_id,
            read_summary=summary,
            touched_files=frozenset(touched_files),
            execution_time_ms=execution_time_ms,
            tokens_used=tokens_used,
        )


# =============================================================================
# VALIDATION FUNCTIONS (FOR EXTERNAL USE)
# =============================================================================


def validate_no_memory(backend: ContextAwareExecutionBackend) -> bool:
    """
    Validate that a backend has no persistent memory.

    This function checks that the backend class has no state
    that persists between executions.

    Args:
        backend: The backend to validate.

    Returns:
        True if the backend has no memory mechanisms.
    """
    # Check for memory-related attributes
    forbidden_attrs = [
        "cache",
        "history",
        "memory",
        "state",
        "session",
        "context_store",
        "previous_results",
        "learning",
    ]
    for attr in forbidden_attrs:
        if hasattr(backend, attr):
            return False
    return True


def validate_no_retry_logic(backend: ContextAwareExecutionBackend) -> bool:
    """
    Validate that a backend has no retry logic.

    Args:
        backend: The backend to validate.

    Returns:
        True if the backend has no retry mechanisms.
    """
    # Check for retry-related attributes
    forbidden_attrs = [
        "max_retries",
        "retry_count",
        "retry_delay",
        "retry_on_failure",
    ]
    for attr in forbidden_attrs:
        if hasattr(backend, attr):
            return False
    return True


def validate_executor_constraints(backend: ContextAwareExecutionBackend) -> List[str]:
    """
    Validate all executor constraints.

    Args:
        backend: The backend to validate.

    Returns:
        List of constraint violations (empty if valid).
    """
    violations = []

    if not validate_no_memory(backend):
        violations.append("Executor has forbidden memory mechanisms")

    if not validate_no_retry_logic(backend):
        violations.append("Executor has forbidden retry logic")

    # Check for forbidden methods that would indicate agency
    forbidden_methods = [
        "plan",
        "decide",
        "choose",
        "suggest",
        "improve",
        "optimize",
        "refactor_all",
        "fix_all",
        "auto_fix",
    ]
    for method in forbidden_methods:
        if hasattr(backend, method) and callable(getattr(backend, method)):
            violations.append(f"Executor has forbidden method: {method}")

    return violations
