"""
Tests for Context-Aware Execution Backend (Phase 10A).

This test suite verifies that the context-aware execution backend:
1. Respects file whitelist constraints
2. Produces diff-only output for EDIT operations
3. Fails on scope expansion
4. Fails on patch size overflow
5. Has no memory between executions
6. Cannot modify Canon artifacts
7. Enforces all hard constraints programmatically

CORE PRINCIPLE:
    Executors may understand context.
    Executors may NOT decide intent.

All tests verify that the executor maintains zero agency, zero authority,
and zero autonomy while still being able to understand local code context.
"""

import pytest
from typing import Dict, Optional, Set
from dataclasses import dataclass, field

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
from axiom_forge.context_aware_backend import (
    ContextAwareExecutionBackend,
    MockContextAwareLLMBackend,
    PromptBuilder,
    ViolationDetector,
    DiffParser,
    DefaultFileLoader,
    validate_no_memory,
    validate_no_retry_logic,
    validate_executor_constraints,
)


# =============================================================================
# FIXTURES
# =============================================================================


@dataclass
class MockFileLoader:
    """Mock file loader for testing."""

    files: Dict[str, str] = field(default_factory=dict)
    access_log: list = field(default_factory=list)

    def load(self, file_path: str) -> Optional[str]:
        """Load file content, tracking access."""
        self.access_log.append(("load", file_path))
        return self.files.get(file_path)

    def exists(self, file_path: str) -> bool:
        """Check if file exists."""
        self.access_log.append(("exists", file_path))
        return file_path in self.files


@pytest.fixture
def mock_file_loader() -> MockFileLoader:
    """Create a mock file loader with test files."""
    return MockFileLoader(
        files={
            "/project/src/main.py": 'def main():\n    print("Hello")\n',
            "/project/src/utils.py": "def helper():\n    return 42\n",
            "/project/tests/test_main.py": "def test_main():\n    assert True\n",
            "/project/README.md": "# Project\n\nA test project.\n",
        }
    )


@pytest.fixture
def valid_edit_diff() -> str:
    """A valid unified diff for testing."""
    return """--- a/project/src/main.py
+++ b/project/src/main.py
@@ -1,2 +1,3 @@
 def main():
-    print("Hello")
+    print("Hello, World!")
+    return 0
"""


@pytest.fixture
def mock_llm_backend(valid_edit_diff: str) -> MockContextAwareLLMBackend:
    """Create a mock LLM backend."""
    return MockContextAwareLLMBackend(
        edit_response=f"```diff\n{valid_edit_diff}```",
        read_response="The main function prints 'Hello' and returns nothing.",
    )


@pytest.fixture
def basic_edit_input() -> ContextAwareExecutionInput:
    """Create a basic EDIT input for testing."""
    return ContextAwareExecutionInput(
        task_id="task-001",
        explicit_instruction="Change the print statement to say 'Hello, World!' and add a return 0",
        allowed_files=frozenset(["/project/src/main.py"]),
        operation_type=OperationType.EDIT,
    )


@pytest.fixture
def basic_read_input() -> ContextAwareExecutionInput:
    """Create a basic READ input for testing."""
    return ContextAwareExecutionInput(
        task_id="task-002",
        explicit_instruction="Describe what the main function does",
        allowed_files=frozenset(["/project/src/main.py"]),
        operation_type=OperationType.READ,
    )


# =============================================================================
# MODEL VALIDATION TESTS
# =============================================================================


class TestContextAwareExecutionInput:
    """Tests for ContextAwareExecutionInput model validation."""

    def test_valid_input_creation(self):
        """Test creating a valid input."""
        input_data = ContextAwareExecutionInput(
            task_id="task-001",
            explicit_instruction="Add a docstring to the function",
            allowed_files=frozenset(["/path/to/file.py"]),
            operation_type=OperationType.EDIT,
        )
        assert input_data.task_id == "task-001"
        assert input_data.explicit_instruction == "Add a docstring to the function"
        assert "/path/to/file.py" in input_data.allowed_files
        assert input_data.operation_type == OperationType.EDIT

    def test_empty_task_id_rejected(self):
        """Test that empty task_id is rejected."""
        with pytest.raises(ValueError, match="task_id is required"):
            ContextAwareExecutionInput(
                task_id="",
                explicit_instruction="Do something",
                allowed_files=frozenset(["/path/to/file.py"]),
                operation_type=OperationType.EDIT,
            )

    def test_empty_instruction_rejected(self):
        """Test that empty instruction is rejected."""
        with pytest.raises(ValueError, match="explicit_instruction is required"):
            ContextAwareExecutionInput(
                task_id="task-001",
                explicit_instruction="",
                allowed_files=frozenset(["/path/to/file.py"]),
                operation_type=OperationType.EDIT,
            )

    def test_empty_allowed_files_rejected(self):
        """Test that empty allowed_files is rejected."""
        with pytest.raises(ValueError, match="allowed_files is required"):
            ContextAwareExecutionInput(
                task_id="task-001",
                explicit_instruction="Do something",
                allowed_files=frozenset(),
                operation_type=OperationType.EDIT,
            )

    def test_negative_max_patch_size_rejected(self):
        """Test that negative max_patch_size is rejected."""
        with pytest.raises(ValueError, match="max_patch_size must be positive"):
            ContextAwareExecutionInput(
                task_id="task-001",
                explicit_instruction="Do something",
                allowed_files=frozenset(["/path/to/file.py"]),
                operation_type=OperationType.EDIT,
                max_patch_size=-100,
            )

    def test_input_is_immutable(self):
        """Test that input is frozen (immutable)."""
        input_data = ContextAwareExecutionInput(
            task_id="task-001",
            explicit_instruction="Do something",
            allowed_files=frozenset(["/path/to/file.py"]),
            operation_type=OperationType.EDIT,
        )
        with pytest.raises(AttributeError):
            input_data.task_id = "modified"  # type: ignore

    def test_is_file_allowed(self):
        """Test file allowlist checking."""
        input_data = ContextAwareExecutionInput(
            task_id="task-001",
            explicit_instruction="Do something",
            allowed_files=frozenset(["/allowed/file.py", "/allowed/other.py"]),
            operation_type=OperationType.EDIT,
        )
        assert input_data.is_file_allowed("/allowed/file.py")
        assert input_data.is_file_allowed("/allowed/other.py")
        assert not input_data.is_file_allowed("/forbidden/file.py")

    def test_to_dict_serialization(self):
        """Test serialization to dictionary."""
        input_data = ContextAwareExecutionInput(
            task_id="task-001",
            explicit_instruction="Do something",
            allowed_files=frozenset(["/path/to/file.py"]),
            operation_type=OperationType.EDIT,
            max_patch_size=10000,
        )
        d = input_data.to_dict()
        assert d["task_id"] == "task-001"
        assert d["explicit_instruction"] == "Do something"
        assert "/path/to/file.py" in d["allowed_files"]
        assert d["operation_type"] == "edit"
        assert d["max_patch_size"] == 10000


class TestFormattingRules:
    """Tests for FormattingRules model."""

    def test_valid_formatting_rules(self):
        """Test creating valid formatting rules."""
        rules = FormattingRules(
            indent_style="spaces",
            indent_size=4,
            line_ending="lf",
            max_line_length=120,
            trailing_newline=True,
        )
        assert rules.indent_style == "spaces"
        assert rules.indent_size == 4

    def test_invalid_indent_style_rejected(self):
        """Test that invalid indent_style is rejected."""
        with pytest.raises(ValueError, match="indent_style must be"):
            FormattingRules(indent_style="invalid")

    def test_invalid_indent_size_rejected(self):
        """Test that invalid indent_size is rejected."""
        with pytest.raises(ValueError, match="indent_size must be"):
            FormattingRules(indent_size=0)
        with pytest.raises(ValueError, match="indent_size must be"):
            FormattingRules(indent_size=20)

    def test_formatting_rules_immutable(self):
        """Test that formatting rules are frozen."""
        rules = FormattingRules()
        with pytest.raises(AttributeError):
            rules.indent_size = 2  # type: ignore


class TestContextAwareExecutionResult:
    """Tests for ContextAwareExecutionResult model."""

    def test_successful_edit_result(self):
        """Test creating a successful EDIT result."""
        result = create_edit_result(
            task_id="task-001",
            diff="--- a/file.py\n+++ b/file.py\n@@ -1 +1 @@\n-old\n+new",
            touched_files=frozenset(["/path/to/file.py"]),
            execution_time_ms=100,
            tokens_used=500,
        )
        assert result.succeeded
        assert not result.failed
        assert result.diff is not None
        assert result.touched_files

    def test_successful_read_result(self):
        """Test creating a successful READ result."""
        result = create_read_result(
            task_id="task-002",
            read_summary="The function does X, Y, and Z.",
            touched_files=frozenset(["/path/to/file.py"]),
        )
        assert result.succeeded
        assert result.read_summary is not None

    def test_failed_result(self):
        """Test creating a failed result."""
        result = create_failed_result(
            task_id="task-003",
            violations=[
                Violation(
                    violation_type=ViolationType.UNAUTHORIZED_FILE_READ,
                    description="Tried to read forbidden file",
                    file_path="/forbidden/file.py",
                )
            ],
            error_message="Access denied",
        )
        assert result.failed
        assert not result.succeeded
        assert result.has_violations
        assert len(result.violations) == 1

    def test_result_is_immutable(self):
        """Test that result is frozen."""
        result = create_edit_result(
            task_id="task-001",
            diff="some diff",
            touched_files=frozenset(),
        )
        with pytest.raises(AttributeError):
            result.task_id = "modified"  # type: ignore


class TestViolation:
    """Tests for Violation model."""

    def test_violation_creation(self):
        """Test creating a violation."""
        v = Violation(
            violation_type=ViolationType.SCOPE_EXPANSION,
            description="Tried to modify additional files",
            evidence="Modified /extra/file.py",
            file_path="/extra/file.py",
        )
        assert v.violation_type == ViolationType.SCOPE_EXPANSION
        assert "additional files" in v.description

    def test_violation_to_dict(self):
        """Test violation serialization."""
        v = Violation(
            violation_type=ViolationType.PATCH_SIZE_OVERFLOW,
            description="Patch too large",
        )
        d = v.to_dict()
        assert d["violation_type"] == "patch_size_overflow"
        assert d["description"] == "Patch too large"


# =============================================================================
# FILE WHITELIST ENFORCEMENT TESTS
# =============================================================================


class TestFileWhitelistEnforcement:
    """Tests verifying that executor cannot access files outside whitelist."""

    def test_executor_only_loads_whitelisted_files(
        self,
        mock_file_loader: MockFileLoader,
        mock_llm_backend: MockContextAwareLLMBackend,
        basic_edit_input: ContextAwareExecutionInput,
    ):
        """Test that executor only loads files in the whitelist."""
        backend = ContextAwareExecutionBackend(
            llm_backend=mock_llm_backend,
            file_loader=mock_file_loader,
        )
        backend.execute(basic_edit_input)

        # Check that only whitelisted files were loaded
        loaded_files = [f for op, f in mock_file_loader.access_log if op == "load"]
        for loaded in loaded_files:
            assert loaded in basic_edit_input.allowed_files

    def test_executor_cannot_read_outside_whitelist(
        self,
        mock_file_loader: MockFileLoader,
    ):
        """Test that executor cannot read files not in whitelist."""
        # Create backend with LLM that tries to reference outside files
        mock_llm = MockContextAwareLLMBackend(
            edit_response="""```diff
--- a/project/src/main.py
+++ b/project/src/main.py
@@ -1 +1 @@
-old
+new
--- a/project/forbidden.py
+++ b/project/forbidden.py
@@ -1 +1 @@
-secret
+exposed
```""",
        )
        backend = ContextAwareExecutionBackend(
            llm_backend=mock_llm,
            file_loader=mock_file_loader,
        )
        input_data = ContextAwareExecutionInput(
            task_id="task-001",
            explicit_instruction="Modify main.py",
            allowed_files=frozenset(["/project/src/main.py"]),
            operation_type=OperationType.EDIT,
        )
        result = backend.execute(input_data)

        # Should fail because diff modifies file outside whitelist
        assert result.failed
        assert result.has_violations
        violation_types = [v.violation_type for v in result.violations]
        assert ViolationType.UNAUTHORIZED_FILE_WRITE in violation_types

    def test_violation_detector_catches_unauthorized_access(self):
        """Test that violation detector catches unauthorized file access."""
        detector = ViolationDetector()
        violations = detector.validate_file_access(
            requested_files={"/allowed/file.py", "/forbidden/file.py"},
            allowed_files={"/allowed/file.py"},
        )
        assert len(violations) == 1
        assert violations[0].violation_type == ViolationType.UNAUTHORIZED_FILE_READ
        assert "/forbidden/file.py" in violations[0].description


# =============================================================================
# DIFF-ONLY OUTPUT TESTS
# =============================================================================


class TestDiffOnlyOutput:
    """Tests verifying that EDIT operations return diff-only output."""

    def test_edit_operation_returns_diff(
        self,
        mock_file_loader: MockFileLoader,
        mock_llm_backend: MockContextAwareLLMBackend,
        basic_edit_input: ContextAwareExecutionInput,
    ):
        """Test that EDIT operation returns a diff."""
        backend = ContextAwareExecutionBackend(
            llm_backend=mock_llm_backend,
            file_loader=mock_file_loader,
        )
        result = backend.execute(basic_edit_input)

        assert result.succeeded
        assert result.diff is not None
        assert "---" in result.diff
        assert "+++" in result.diff

    def test_non_diff_output_fails(
        self,
        mock_file_loader: MockFileLoader,
    ):
        """Test that non-diff output for EDIT fails."""
        mock_llm = MockContextAwareLLMBackend(
            edit_response="Here's the modified code:\n\ndef main():\n    print('Hello')\n",
        )
        backend = ContextAwareExecutionBackend(
            llm_backend=mock_llm,
            file_loader=mock_file_loader,
        )
        input_data = ContextAwareExecutionInput(
            task_id="task-001",
            explicit_instruction="Modify the function",
            allowed_files=frozenset(["/project/src/main.py"]),
            operation_type=OperationType.EDIT,
        )
        result = backend.execute(input_data)

        assert result.failed
        assert result.has_violations
        violation_types = [v.violation_type for v in result.violations]
        assert ViolationType.NON_DIFF_OUTPUT in violation_types

    def test_empty_diff_fails(
        self,
        mock_file_loader: MockFileLoader,
    ):
        """Test that empty diff output fails."""
        mock_llm = MockContextAwareLLMBackend(edit_response="")
        backend = ContextAwareExecutionBackend(
            llm_backend=mock_llm,
            file_loader=mock_file_loader,
        )
        input_data = ContextAwareExecutionInput(
            task_id="task-001",
            explicit_instruction="Modify the function",
            allowed_files=frozenset(["/project/src/main.py"]),
            operation_type=OperationType.EDIT,
        )
        result = backend.execute(input_data)

        assert result.failed

    def test_read_operation_returns_summary_not_diff(
        self,
        mock_file_loader: MockFileLoader,
        mock_llm_backend: MockContextAwareLLMBackend,
        basic_read_input: ContextAwareExecutionInput,
    ):
        """Test that READ operation returns summary, not diff."""
        backend = ContextAwareExecutionBackend(
            llm_backend=mock_llm_backend,
            file_loader=mock_file_loader,
        )
        result = backend.execute(basic_read_input)

        assert result.succeeded
        assert result.read_summary is not None
        assert result.diff is None


# =============================================================================
# SCOPE EXPANSION DETECTION TESTS
# =============================================================================


class TestScopeExpansionDetection:
    """Tests verifying that scope expansion is detected and fails."""

    def test_diff_modifying_unlisted_file_fails(
        self,
        mock_file_loader: MockFileLoader,
    ):
        """Test that diff modifying unlisted file fails."""
        mock_llm = MockContextAwareLLMBackend(
            edit_response="""```diff
--- a/project/src/main.py
+++ b/project/src/main.py
@@ -1 +1 @@
-old
+new
--- a/project/src/utils.py
+++ b/project/src/utils.py
@@ -1 +1 @@
-helper
+modified_helper
```""",
        )
        backend = ContextAwareExecutionBackend(
            llm_backend=mock_llm,
            file_loader=mock_file_loader,
        )
        # Only main.py is allowed, not utils.py
        input_data = ContextAwareExecutionInput(
            task_id="task-001",
            explicit_instruction="Modify main.py",
            allowed_files=frozenset(["/project/src/main.py"]),
            operation_type=OperationType.EDIT,
        )
        result = backend.execute(input_data)

        assert result.failed
        violation_types = [v.violation_type for v in result.violations]
        assert ViolationType.UNAUTHORIZED_FILE_WRITE in violation_types

    def test_unsolicited_suggestions_fail(
        self,
        mock_file_loader: MockFileLoader,
    ):
        """Test that unsolicited suggestions are detected and fail."""
        mock_llm = MockContextAwareLLMBackend(
            edit_response="""I would suggest also refactoring the helper function.
Here's the diff:
```diff
--- a/project/src/main.py
+++ b/project/src/main.py
@@ -1 +1 @@
-old
+new
```""",
        )
        backend = ContextAwareExecutionBackend(
            llm_backend=mock_llm,
            file_loader=mock_file_loader,
        )
        input_data = ContextAwareExecutionInput(
            task_id="task-001",
            explicit_instruction="Modify main.py",
            allowed_files=frozenset(["/project/src/main.py"]),
            operation_type=OperationType.EDIT,
        )
        result = backend.execute(input_data)

        assert result.failed
        violation_types = [v.violation_type for v in result.violations]
        assert ViolationType.UNSOLICITED_SUGGESTION in violation_types


# =============================================================================
# PATCH SIZE OVERFLOW TESTS
# =============================================================================


class TestPatchSizeOverflow:
    """Tests verifying patch size limits are enforced."""

    def test_patch_size_overflow_detected(
        self,
        mock_file_loader: MockFileLoader,
    ):
        """Test that oversized patches are detected and fail."""
        # Create a large diff
        large_diff = "--- a/file.py\n+++ b/file.py\n@@ -1 +1 @@\n" + "+x" * 1000
        mock_llm = MockContextAwareLLMBackend(edit_response=f"```diff\n{large_diff}```")
        backend = ContextAwareExecutionBackend(
            llm_backend=mock_llm,
            file_loader=mock_file_loader,
        )
        input_data = ContextAwareExecutionInput(
            task_id="task-001",
            explicit_instruction="Modify the file",
            allowed_files=frozenset(["/project/src/main.py"]),
            operation_type=OperationType.EDIT,
            max_patch_size=100,  # Very small limit
        )
        result = backend.execute(input_data)

        assert result.failed
        violation_types = [v.violation_type for v in result.violations]
        assert ViolationType.PATCH_SIZE_OVERFLOW in violation_types

    def test_max_patch_size_hard_limit_enforced(self):
        """Test that hard limit on patch size is enforced."""
        detector = ViolationDetector()
        violations = detector.validate_input(
            ContextAwareExecutionInput(
                task_id="task-001",
                explicit_instruction="Do something",
                allowed_files=frozenset(["/file.py"]),
                operation_type=OperationType.EDIT,
                max_patch_size=MAX_PATCH_SIZE_HARD_LIMIT + 1,
            )
        )
        assert len(violations) > 0
        assert violations[0].violation_type == ViolationType.PATCH_SIZE_OVERFLOW


# =============================================================================
# NO MEMORY TESTS
# =============================================================================


class TestNoMemory:
    """Tests verifying that executor has no memory between runs."""

    def test_executor_has_no_memory_attributes(self):
        """Test that executor has no memory-related attributes."""
        mock_llm = MockContextAwareLLMBackend()
        backend = ContextAwareExecutionBackend(llm_backend=mock_llm)

        assert validate_no_memory(backend)

    def test_executor_has_no_retry_logic(self):
        """Test that executor has no retry-related attributes."""
        mock_llm = MockContextAwareLLMBackend()
        backend = ContextAwareExecutionBackend(llm_backend=mock_llm)

        assert validate_no_retry_logic(backend)

    def test_executor_passes_all_constraint_validations(self):
        """Test that executor passes all constraint validations."""
        mock_llm = MockContextAwareLLMBackend()
        backend = ContextAwareExecutionBackend(llm_backend=mock_llm)

        violations = validate_executor_constraints(backend)
        assert len(violations) == 0

    def test_multiple_executions_are_independent(
        self,
        mock_file_loader: MockFileLoader,
    ):
        """Test that multiple executions are completely independent."""
        mock_llm = MockContextAwareLLMBackend(
            edit_response="""```diff
--- a/project/src/main.py
+++ b/project/src/main.py
@@ -1 +1 @@
-old
+new
```""",
        )
        backend = ContextAwareExecutionBackend(
            llm_backend=mock_llm,
            file_loader=mock_file_loader,
        )

        # Execute twice
        input1 = ContextAwareExecutionInput(
            task_id="task-001",
            explicit_instruction="First instruction",
            allowed_files=frozenset(["/project/src/main.py"]),
            operation_type=OperationType.EDIT,
        )
        input2 = ContextAwareExecutionInput(
            task_id="task-002",
            explicit_instruction="Second instruction",
            allowed_files=frozenset(["/project/src/main.py"]),
            operation_type=OperationType.EDIT,
        )

        result1 = backend.execute(input1)
        result2 = backend.execute(input2)

        # Both should succeed independently
        assert result1.succeeded
        assert result2.succeeded

        # Verify that the second execution didn't know about the first
        prompts = mock_llm.prompts_received
        assert len(prompts) == 2
        assert "First instruction" in prompts[0]
        assert "Second instruction" in prompts[1]
        # Second prompt should NOT contain first instruction
        assert "First instruction" not in prompts[1]


# =============================================================================
# LLM FAILURE HANDLING TESTS
# =============================================================================


class TestLLMFailureHandling:
    """Tests verifying proper handling of LLM failures."""

    def test_llm_exception_fails_gracefully(
        self,
        mock_file_loader: MockFileLoader,
    ):
        """Test that LLM exception results in graceful failure."""
        mock_llm = MockContextAwareLLMBackend(
            should_fail=True,
            failure_message="API rate limit exceeded",
        )
        backend = ContextAwareExecutionBackend(
            llm_backend=mock_llm,
            file_loader=mock_file_loader,
        )
        input_data = ContextAwareExecutionInput(
            task_id="task-001",
            explicit_instruction="Do something",
            allowed_files=frozenset(["/project/src/main.py"]),
            operation_type=OperationType.EDIT,
        )
        result = backend.execute(input_data)

        assert result.failed
        assert "LLM error" in result.error_message or "API rate limit" in result.error_message

    def test_llm_refusal_fails(
        self,
        mock_file_loader: MockFileLoader,
    ):
        """Test that LLM refusal to apply instruction fails."""
        mock_llm = MockContextAwareLLMBackend(
            edit_response="CANNOT_APPLY: The instruction is ambiguous",
        )
        backend = ContextAwareExecutionBackend(
            llm_backend=mock_llm,
            file_loader=mock_file_loader,
        )
        input_data = ContextAwareExecutionInput(
            task_id="task-001",
            explicit_instruction="Do something",
            allowed_files=frozenset(["/project/src/main.py"]),
            operation_type=OperationType.EDIT,
        )
        result = backend.execute(input_data)

        assert result.failed
        violation_types = [v.violation_type for v in result.violations]
        assert ViolationType.LLM_REFUSED in violation_types


# =============================================================================
# PROMPT BUILDER TESTS
# =============================================================================


class TestPromptBuilder:
    """Tests for prompt construction."""

    def test_edit_prompt_includes_instruction_verbatim(self):
        """Test that edit prompt includes the exact instruction."""
        builder = PromptBuilder()
        instruction = "Add a docstring explaining the function parameters"
        prompt = builder.build_edit_prompt(
            instruction=instruction,
            files_content={"/file.py": "def func(): pass"},
        )

        assert instruction in prompt
        assert "INSTRUCTION (APPLY EXACTLY)" in prompt

    def test_edit_prompt_includes_no_agency_constraints(self):
        """Test that edit prompt explicitly forbids extra changes."""
        builder = PromptBuilder()
        prompt = builder.build_edit_prompt(
            instruction="Do something",
            files_content={"/file.py": "code"},
        )

        assert "Do NOT suggest alternative approaches" in prompt
        assert "Do NOT refactor beyond the instruction" in prompt
        assert "Do NOT fix unrelated issues" in prompt
        assert "MUST be a unified diff ONLY" in prompt

    def test_edit_prompt_includes_context_aware_label(self):
        """Test that prompt includes the context-aware execution label."""
        builder = PromptBuilder()
        prompt = builder.build_edit_prompt(
            instruction="Do something",
            files_content={"/file.py": "code"},
        )

        assert CONTEXT_AWARE_EXECUTION_LABEL in prompt

    def test_read_prompt_includes_instruction_verbatim(self):
        """Test that read prompt includes the exact instruction."""
        builder = PromptBuilder()
        instruction = "List all function names in the file"
        prompt = builder.build_read_prompt(
            instruction=instruction,
            files_content={"/file.py": "def func(): pass"},
        )

        assert instruction in prompt
        assert "INSTRUCTION (EXTRACT EXACTLY)" in prompt

    def test_prompt_includes_all_file_contents(self):
        """Test that prompt includes all file contents."""
        builder = PromptBuilder()
        files = {
            "/file1.py": "content1",
            "/file2.py": "content2",
        }
        prompt = builder.build_edit_prompt(
            instruction="Do something",
            files_content=files,
        )

        assert "content1" in prompt
        assert "content2" in prompt
        assert "FILE: /file1.py" in prompt
        assert "FILE: /file2.py" in prompt

    def test_formatting_rules_included_when_provided(self):
        """Test that formatting rules are included in prompt."""
        builder = PromptBuilder()
        rules = FormattingRules(indent_size=2, indent_style="spaces")
        prompt = builder.build_edit_prompt(
            instruction="Do something",
            files_content={"/file.py": "code"},
            formatting_rules=rules,
        )

        assert "Indent style: spaces" in prompt
        assert "Indent size: 2" in prompt


# =============================================================================
# VIOLATION DETECTOR TESTS
# =============================================================================


class TestViolationDetector:
    """Tests for violation detection."""

    def test_detect_unauthorized_file_read(self):
        """Test detection of unauthorized file read."""
        detector = ViolationDetector()
        violations = detector.validate_file_access(
            requested_files={"/allowed.py", "/forbidden.py"},
            allowed_files={"/allowed.py"},
        )

        assert len(violations) == 1
        assert violations[0].violation_type == ViolationType.UNAUTHORIZED_FILE_READ

    def test_detect_patch_size_overflow(self):
        """Test detection of patch size overflow."""
        detector = ViolationDetector()
        large_diff = "x" * 10000
        violations = detector.validate_diff_output(
            diff=large_diff,
            allowed_files=set(),
            max_patch_size=100,
        )

        # Should detect both overflow and invalid format
        violation_types = [v.violation_type for v in violations]
        assert ViolationType.PATCH_SIZE_OVERFLOW in violation_types

    def test_detect_unsolicited_suggestions(self):
        """Test detection of unsolicited suggestions in response."""
        detector = ViolationDetector()
        violations = detector.validate_llm_response(
            response="I would suggest refactoring this differently. Here's the diff...",
            operation_type=OperationType.EDIT,
        )

        assert len(violations) > 0
        violation_types = [v.violation_type for v in violations]
        assert ViolationType.UNSOLICITED_SUGGESTION in violation_types

    def test_detect_non_diff_output(self):
        """Test detection of non-diff output for EDIT."""
        detector = ViolationDetector()
        violations = detector.validate_llm_response(
            response="Here is the modified code:\n\ndef func():\n    pass",
            operation_type=OperationType.EDIT,
        )

        assert len(violations) > 0
        violation_types = [v.violation_type for v in violations]
        assert ViolationType.NON_DIFF_OUTPUT in violation_types

    def test_detect_files_from_diff(self):
        """Test extracting files from diff."""
        detector = ViolationDetector()
        diff = """--- a/src/main.py
+++ b/src/main.py
@@ -1 +1 @@
-old
+new
--- a/src/utils.py
+++ b/src/utils.py
@@ -1 +1 @@
-old
+new"""
        files = detector._extract_files_from_diff(diff)

        assert "src/main.py" in files
        assert "src/utils.py" in files


# =============================================================================
# DIFF PARSER TESTS
# =============================================================================


class TestDiffParser:
    """Tests for diff parsing."""

    def test_extract_diff_from_code_block(self):
        """Test extracting diff from markdown code block."""
        parser = DiffParser()
        response = """Here's the diff:
```diff
--- a/file.py
+++ b/file.py
@@ -1 +1 @@
-old
+new
```
That's all."""
        diff = parser.extract_diff(response)

        assert "--- a/file.py" in diff
        assert "+new" in diff
        assert "Here's the diff" not in diff
        assert "That's all" not in diff

    def test_extract_diff_without_code_block(self):
        """Test extracting diff without code block markers."""
        parser = DiffParser()
        response = """--- a/file.py
+++ b/file.py
@@ -1 +1 @@
-old
+new"""
        diff = parser.extract_diff(response)

        assert "--- a/file.py" in diff
        assert "+new" in diff


# =============================================================================
# CANON IMMUTABILITY TESTS
# =============================================================================


class TestCanonImmutability:
    """Tests verifying that executor cannot modify Canon artifacts."""

    def test_executor_cannot_modify_cpkg_files(
        self,
        mock_file_loader: MockFileLoader,
    ):
        """Test that executor cannot modify CPKG-related files."""
        # Add Canon files to mock
        mock_file_loader.files["/project/.axiom/cpkg.json"] = '{"version": "1.0"}'
        mock_file_loader.files["/project/src/main.py"] = "def main(): pass"

        mock_llm = MockContextAwareLLMBackend(
            edit_response="""```diff
--- a/project/.axiom/cpkg.json
+++ b/project/.axiom/cpkg.json
@@ -1 +1 @@
-{"version": "1.0"}
+{"version": "2.0", "hacked": true}
```""",
        )
        backend = ContextAwareExecutionBackend(
            llm_backend=mock_llm,
            file_loader=mock_file_loader,
        )
        # Whitelist only includes main.py, not Canon files
        input_data = ContextAwareExecutionInput(
            task_id="task-001",
            explicit_instruction="Modify main.py",
            allowed_files=frozenset(["/project/src/main.py"]),
            operation_type=OperationType.EDIT,
        )
        result = backend.execute(input_data)

        # Should fail because diff modifies file outside whitelist
        assert result.failed
        violation_types = [v.violation_type for v in result.violations]
        assert ViolationType.UNAUTHORIZED_FILE_WRITE in violation_types

    def test_canon_files_never_in_default_whitelist(self):
        """Test that Canon files should never be whitelisted for modification."""
        # This is a policy test - Canon paths should be excluded at the planning level
        canon_paths = [
            "/project/.axiom/cpkg.json",
            "/project/.axiom/bfm.json",
            "/project/.axiom/ucir.json",
            "/project/.axiom/task_graph.json",
        ]

        # Verify that attempting to include Canon paths would require explicit action
        # (The whitelist is set by the tactical layer, not the executor)
        for path in canon_paths:
            input_data = ContextAwareExecutionInput(
                task_id="task-001",
                explicit_instruction="Do something",
                allowed_files=frozenset([path]),
                operation_type=OperationType.EDIT,
            )
            # Input creation succeeds (policy is at planning level, not executor level)
            assert input_data.allowed_files


# =============================================================================
# TOKEN BUDGET TESTS
# =============================================================================


class TestTokenBudget:
    """Tests for token budget enforcement."""

    def test_token_budget_exceeded_fails(
        self,
        mock_file_loader: MockFileLoader,
    ):
        """Test that exceeding token budget fails."""
        # Add a large file
        mock_file_loader.files["/project/large.py"] = "x" * 100000

        mock_llm = MockContextAwareLLMBackend()
        backend = ContextAwareExecutionBackend(
            llm_backend=mock_llm,
            file_loader=mock_file_loader,
        )
        input_data = ContextAwareExecutionInput(
            task_id="task-001",
            explicit_instruction="Analyze the file",
            allowed_files=frozenset(["/project/large.py"]),
            operation_type=OperationType.READ,
            max_context_tokens=100,  # Very small budget
        )
        result = backend.execute(input_data)

        assert result.failed
        violation_types = [v.violation_type for v in result.violations]
        assert ViolationType.TOKEN_BUDGET_EXCEEDED in violation_types

    def test_token_hard_limit_enforced_on_input(self):
        """Test that token hard limit is enforced on input."""
        detector = ViolationDetector()
        violations = detector.validate_input(
            ContextAwareExecutionInput(
                task_id="task-001",
                explicit_instruction="Do something",
                allowed_files=frozenset(["/file.py"]),
                operation_type=OperationType.EDIT,
                max_context_tokens=MAX_CONTEXT_TOKENS_HARD_LIMIT + 1,
            )
        )
        assert len(violations) > 0
        assert violations[0].violation_type == ViolationType.TOKEN_BUDGET_EXCEEDED


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestIntegration:
    """Integration tests for context-aware execution."""

    def test_successful_edit_workflow(
        self,
        mock_file_loader: MockFileLoader,
        valid_edit_diff: str,
    ):
        """Test a successful EDIT workflow end-to-end."""
        mock_llm = MockContextAwareLLMBackend(
            edit_response=f"```diff\n{valid_edit_diff}```",
        )
        backend = ContextAwareExecutionBackend(
            llm_backend=mock_llm,
            file_loader=mock_file_loader,
        )
        input_data = ContextAwareExecutionInput(
            task_id="task-001",
            explicit_instruction="Modify the print statement",
            allowed_files=frozenset(["/project/src/main.py"]),
            operation_type=OperationType.EDIT,
        )
        result = backend.execute(input_data)

        assert result.succeeded
        assert result.diff is not None
        assert result.touched_files
        assert result.execution_time_ms >= 0
        assert result.tokens_used > 0

    def test_successful_read_workflow(
        self,
        mock_file_loader: MockFileLoader,
    ):
        """Test a successful READ workflow end-to-end."""
        mock_llm = MockContextAwareLLMBackend(
            read_response="The main function prints 'Hello' to stdout.",
        )
        backend = ContextAwareExecutionBackend(
            llm_backend=mock_llm,
            file_loader=mock_file_loader,
        )
        input_data = ContextAwareExecutionInput(
            task_id="task-002",
            explicit_instruction="Describe the main function",
            allowed_files=frozenset(["/project/src/main.py"]),
            operation_type=OperationType.READ,
        )
        result = backend.execute(input_data)

        assert result.succeeded
        assert result.read_summary is not None
        assert "main" in result.read_summary.lower() or "prints" in result.read_summary.lower()

    def test_no_files_loadable_fails(
        self,
    ):
        """Test that execution fails if no whitelisted files can be loaded."""
        mock_file_loader = MockFileLoader(files={})  # Empty
        mock_llm = MockContextAwareLLMBackend()
        backend = ContextAwareExecutionBackend(
            llm_backend=mock_llm,
            file_loader=mock_file_loader,
        )
        input_data = ContextAwareExecutionInput(
            task_id="task-001",
            explicit_instruction="Do something",
            allowed_files=frozenset(["/nonexistent/file.py"]),
            operation_type=OperationType.EDIT,
        )
        result = backend.execute(input_data)

        assert result.failed
        assert "No accessible files" in result.error_message


# =============================================================================
# SAFETY INVARIANT TESTS
# =============================================================================


class TestSafetyInvariants:
    """Tests for safety invariants that must always hold."""

    def test_executor_has_no_plan_method(self):
        """Test that executor has no planning capability."""
        mock_llm = MockContextAwareLLMBackend()
        backend = ContextAwareExecutionBackend(llm_backend=mock_llm)

        assert not hasattr(backend, "plan")
        assert not hasattr(backend, "decide")
        assert not hasattr(backend, "choose")

    def test_executor_has_no_suggest_method(self):
        """Test that executor has no suggestion capability."""
        mock_llm = MockContextAwareLLMBackend()
        backend = ContextAwareExecutionBackend(llm_backend=mock_llm)

        assert not hasattr(backend, "suggest")
        assert not hasattr(backend, "improve")
        assert not hasattr(backend, "optimize")

    def test_executor_has_no_auto_fix_method(self):
        """Test that executor has no auto-fix capability."""
        mock_llm = MockContextAwareLLMBackend()
        backend = ContextAwareExecutionBackend(llm_backend=mock_llm)

        assert not hasattr(backend, "auto_fix")
        assert not hasattr(backend, "fix_all")
        assert not hasattr(backend, "refactor_all")

    def test_execution_input_immutability(self):
        """Test that execution input cannot be modified after creation."""
        input_data = ContextAwareExecutionInput(
            task_id="task-001",
            explicit_instruction="Original instruction",
            allowed_files=frozenset(["/file.py"]),
            operation_type=OperationType.EDIT,
        )

        # Instruction cannot be changed
        with pytest.raises(AttributeError):
            input_data.explicit_instruction = "Modified instruction"  # type: ignore

        # Files cannot be changed
        with pytest.raises(AttributeError):
            input_data.allowed_files = frozenset(["/other.py"])  # type: ignore

    def test_context_aware_label_is_present(self):
        """Test that context-aware label constant is defined correctly."""
        assert "NO AGENCY" in CONTEXT_AWARE_EXECUTION_LABEL
        assert "CONTEXT-AWARE" in CONTEXT_AWARE_EXECUTION_LABEL

    def test_single_shot_execution(
        self,
        mock_file_loader: MockFileLoader,
    ):
        """Test that execution is single-shot (LLM called exactly once)."""
        mock_llm = MockContextAwareLLMBackend(
            edit_response="""```diff
--- a/project/src/main.py
+++ b/project/src/main.py
@@ -1 +1 @@
-old
+new
```""",
        )
        backend = ContextAwareExecutionBackend(
            llm_backend=mock_llm,
            file_loader=mock_file_loader,
        )
        input_data = ContextAwareExecutionInput(
            task_id="task-001",
            explicit_instruction="Modify the file",
            allowed_files=frozenset(["/project/src/main.py"]),
            operation_type=OperationType.EDIT,
        )
        backend.execute(input_data)

        # LLM should be called exactly once
        assert mock_llm.call_count == 1

    def test_no_retry_on_failure(
        self,
        mock_file_loader: MockFileLoader,
    ):
        """Test that there are no retries on failure."""
        mock_llm = MockContextAwareLLMBackend(
            should_fail=True,
            failure_message="API error",
        )
        backend = ContextAwareExecutionBackend(
            llm_backend=mock_llm,
            file_loader=mock_file_loader,
        )
        input_data = ContextAwareExecutionInput(
            task_id="task-001",
            explicit_instruction="Do something",
            allowed_files=frozenset(["/project/src/main.py"]),
            operation_type=OperationType.EDIT,
        )
        result = backend.execute(input_data)

        # Should fail immediately without retries
        assert result.failed
        assert mock_llm.call_count == 1  # No retries
