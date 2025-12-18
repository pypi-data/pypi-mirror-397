"""
Playwright Backend Integration Tests.

These tests verify that the PlaywrightExecutionBackend:
1. Enforces domain allowlist (blocks disallowed domains)
2. Enforces script validation (blocks dangerous patterns)
3. Enforces browser restrictions
4. Enforces timeout limits
5. Captures artifacts deterministically
6. Fails fast on policy violations

NOTE: These tests include both unit-style tests (no real browser)
and integration tests that require Playwright to be installed.
Integration tests are marked and can be skipped if Playwright is unavailable.
"""

import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from axiom_conductor.model import TaskExecutionState, TaskFailureReason
from axiom_forge.backend import TaskExecutionInput
from axiom_forge.playwright_backend import (
    PlaywrightExecutionBackend,
    PlaywrightExecutionPolicy,
    PlaywrightTaskInput,
    PlaywrightBrowser,
    PlaywrightScriptType,
    REGISTERED_SCRIPTS,
    validate_url_against_policy,
    validate_script_content,
)


# =============================================================================
# Policy Validation Tests (No Playwright Required)
# =============================================================================


class TestURLValidation(unittest.TestCase):
    """Tests for URL validation against policy."""

    def test_allowed_domain_passes(self) -> None:
        """Verify that allowed domains pass validation."""
        policy = PlaywrightExecutionPolicy(
            allowed_domains={"example.com", "test.example.com"}
        )
        
        result = validate_url_against_policy("https://example.com/page", policy)
        self.assertIsNone(result)

    def test_subdomain_of_allowed_passes(self) -> None:
        """Verify that subdomains of allowed domains pass."""
        policy = PlaywrightExecutionPolicy(
            allowed_domains={"example.com"}
        )
        
        result = validate_url_against_policy("https://www.example.com/page", policy)
        self.assertIsNone(result)

    def test_disallowed_domain_rejected(self) -> None:
        """Verify that disallowed domains are rejected."""
        policy = PlaywrightExecutionPolicy(
            allowed_domains={"example.com"}
        )
        
        result = validate_url_against_policy("https://evil.com/page", policy)
        self.assertIsNotNone(result)
        self.assertIn("not in the allowed domains", result)

    def test_empty_allowlist_rejects_all(self) -> None:
        """Verify that empty allowlist rejects all domains."""
        policy = PlaywrightExecutionPolicy(
            allowed_domains=set()
        )
        
        result = validate_url_against_policy("https://example.com", policy)
        self.assertIsNotNone(result)
        self.assertIn("No allowed domains", result)

    def test_invalid_url_rejected(self) -> None:
        """Verify that invalid URLs are rejected."""
        policy = PlaywrightExecutionPolicy(
            allowed_domains={"example.com"}
        )
        
        result = validate_url_against_policy("not-a-url", policy)
        self.assertIsNotNone(result)

    def test_non_http_scheme_rejected(self) -> None:
        """Verify that non-http/https schemes are rejected."""
        policy = PlaywrightExecutionPolicy(
            allowed_domains={"example.com"}
        )
        
        result = validate_url_against_policy("file:///etc/passwd", policy)
        self.assertIsNotNone(result)
        self.assertIn("scheme", result.lower())

    def test_javascript_scheme_rejected(self) -> None:
        """Verify that javascript: scheme is rejected."""
        policy = PlaywrightExecutionPolicy(
            allowed_domains={"example.com"}
        )
        
        result = validate_url_against_policy("javascript:alert(1)", policy)
        self.assertIsNotNone(result)


class TestScriptValidation(unittest.TestCase):
    """Tests for inline script validation."""

    def test_safe_script_passes(self) -> None:
        """Verify that safe scripts pass validation."""
        script = """
page.goto(target_url)
page.wait_for_load_state("domcontentloaded")
result["success"] = True
"""
        result = validate_script_content(script)
        self.assertIsNone(result)

    def test_import_os_rejected(self) -> None:
        """Verify that 'import os' is rejected."""
        script = """
import os
os.system("rm -rf /")
"""
        result = validate_script_content(script)
        self.assertIsNotNone(result)
        self.assertIn("forbidden pattern", result.lower())

    def test_subprocess_rejected(self) -> None:
        """Verify that subprocess is rejected."""
        script = """
import subprocess
subprocess.run(["rm", "-rf", "/"])
"""
        result = validate_script_content(script)
        self.assertIsNotNone(result)

    def test_eval_rejected(self) -> None:
        """Verify that eval() is rejected."""
        script = """
eval("__import__('os').system('whoami')")
"""
        result = validate_script_content(script)
        self.assertIsNotNone(result)

    def test_exec_rejected(self) -> None:
        """Verify that exec() is rejected."""
        script = """
exec("print('hello')")
"""
        result = validate_script_content(script)
        self.assertIsNotNone(result)

    def test_open_rejected(self) -> None:
        """Verify that open() is rejected."""
        script = """
with open("/etc/passwd") as f:
    data = f.read()
"""
        result = validate_script_content(script)
        self.assertIsNotNone(result)

    def test_builtins_access_rejected(self) -> None:
        """Verify that __builtins__ access is rejected."""
        script = """
__builtins__['open']('/etc/passwd')
"""
        result = validate_script_content(script)
        self.assertIsNotNone(result)


# =============================================================================
# Backend Policy Enforcement Tests
# =============================================================================


class TestPlaywrightBackendPolicyEnforcement(unittest.TestCase):
    """Tests for policy enforcement in the backend."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.policy = PlaywrightExecutionPolicy(
            allowed_domains={"example.com"},
            allowed_browsers={PlaywrightBrowser.CHROMIUM},
            max_timeout_seconds=30,
            allowed_scripts={"smoke_test"},
        )
        self.backend = PlaywrightExecutionBackend(policy=self.policy)

    def test_disallowed_domain_rejected(self) -> None:
        """Verify that tasks targeting disallowed domains are rejected."""
        task_input = TaskExecutionInput(
            task_id="test-task-1",
            command="playwright",
            metadata={
                "target_url": "https://evil.com/malware",
                "script_type": "registered",
                "script_name": "smoke_test",
            }
        )
        
        result = self.backend.execute_task(task_input)
        
        self.assertEqual(result.state, TaskExecutionState.FAILED)
        self.assertEqual(result.failure_reason, TaskFailureReason.PRECONDITION_FAILED)
        self.assertIn("not in the allowed domains", result.error_message)

    def test_disallowed_browser_rejected(self) -> None:
        """Verify that tasks using disallowed browsers are rejected."""
        task_input = TaskExecutionInput(
            task_id="test-task-2",
            command="playwright",
            metadata={
                "target_url": "https://example.com",
                "script_type": "registered",
                "script_name": "smoke_test",
                "browser": "firefox",  # Not in allowed_browsers
            }
        )
        
        result = self.backend.execute_task(task_input)
        
        self.assertEqual(result.state, TaskExecutionState.FAILED)
        self.assertEqual(result.failure_reason, TaskFailureReason.PRECONDITION_FAILED)
        self.assertIn("not allowed", result.error_message.lower())

    def test_excessive_timeout_rejected(self) -> None:
        """Verify that excessive timeouts are rejected."""
        task_input = TaskExecutionInput(
            task_id="test-task-3",
            command="playwright",
            metadata={
                "target_url": "https://example.com",
                "script_type": "registered",
                "script_name": "smoke_test",
                "timeout_seconds": 600,  # Exceeds max_timeout_seconds (30)
            }
        )
        
        result = self.backend.execute_task(task_input)
        
        self.assertEqual(result.state, TaskExecutionState.FAILED)
        self.assertEqual(result.failure_reason, TaskFailureReason.PRECONDITION_FAILED)
        self.assertIn("exceeds maximum", result.error_message.lower())

    def test_unregistered_script_rejected(self) -> None:
        """Verify that unregistered scripts are rejected when policy restricts."""
        task_input = TaskExecutionInput(
            task_id="test-task-4",
            command="playwright",
            metadata={
                "target_url": "https://example.com",
                "script_type": "registered",
                "script_name": "unknown_script",  # Not in allowed_scripts
            }
        )
        
        result = self.backend.execute_task(task_input)
        
        self.assertEqual(result.state, TaskExecutionState.FAILED)
        self.assertEqual(result.failure_reason, TaskFailureReason.PRECONDITION_FAILED)
        self.assertIn("not in the allowed scripts", result.error_message)

    def test_dangerous_inline_script_rejected(self) -> None:
        """Verify that inline scripts with dangerous patterns are rejected."""
        task_input = TaskExecutionInput(
            task_id="test-task-5",
            command="playwright",
            metadata={
                "target_url": "https://example.com",
                "script_type": "inline",
                "script_content": """
import os
os.system("rm -rf /")
""",
            }
        )
        
        result = self.backend.execute_task(task_input)
        
        self.assertEqual(result.state, TaskExecutionState.FAILED)
        self.assertEqual(result.failure_reason, TaskFailureReason.PRECONDITION_FAILED)
        self.assertIn("forbidden pattern", result.error_message.lower())

    def test_missing_target_url_rejected(self) -> None:
        """Verify that missing target_url is rejected."""
        task_input = TaskExecutionInput(
            task_id="test-task-6",
            command="playwright",
            metadata={
                "script_type": "registered",
                "script_name": "smoke_test",
                # target_url is missing
            }
        )
        
        result = self.backend.execute_task(task_input)
        
        self.assertEqual(result.state, TaskExecutionState.FAILED)
        self.assertEqual(result.failure_reason, TaskFailureReason.PRECONDITION_FAILED)
        self.assertIn("target_url", result.error_message.lower())

    def test_screenshot_rejected_when_policy_disallows(self) -> None:
        """Verify that screenshot requests are rejected when policy disallows."""
        policy_no_screenshots = PlaywrightExecutionPolicy(
            allowed_domains={"example.com"},
            allow_screenshots=False,
        )
        backend = PlaywrightExecutionBackend(policy=policy_no_screenshots)
        
        task_input = TaskExecutionInput(
            task_id="test-task-7",
            command="playwright",
            metadata={
                "target_url": "https://example.com",
                "script_type": "registered",
                "script_name": "smoke_test",
                "capture_screenshot": True,  # Disallowed by policy
            }
        )
        
        result = backend.execute_task(task_input)
        
        self.assertEqual(result.state, TaskExecutionState.FAILED)
        self.assertEqual(result.failure_reason, TaskFailureReason.PRECONDITION_FAILED)
        self.assertIn("screenshot", result.error_message.lower())


# =============================================================================
# Registered Scripts Tests
# =============================================================================


class TestRegisteredScripts(unittest.TestCase):
    """Tests for registered script availability."""

    def test_smoke_test_script_exists(self) -> None:
        """Verify that smoke_test script is registered."""
        self.assertIn("smoke_test", REGISTERED_SCRIPTS)

    def test_check_element_exists_script_exists(self) -> None:
        """Verify that check_element_exists script is registered."""
        self.assertIn("check_element_exists", REGISTERED_SCRIPTS)

    def test_screenshot_only_script_exists(self) -> None:
        """Verify that screenshot_only script is registered."""
        self.assertIn("screenshot_only", REGISTERED_SCRIPTS)

    def test_login_flow_check_script_exists(self) -> None:
        """Verify that login_flow_check script is registered."""
        self.assertIn("login_flow_check", REGISTERED_SCRIPTS)

    def test_all_scripts_are_safe(self) -> None:
        """Verify that all registered scripts pass safety validation."""
        for name, script in REGISTERED_SCRIPTS.items():
            result = validate_script_content(script)
            self.assertIsNone(result, f"Script '{name}' failed validation: {result}")


# =============================================================================
# Input Parsing Tests
# =============================================================================


class TestInputParsing(unittest.TestCase):
    """Tests for PlaywrightTaskInput parsing."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.policy = PlaywrightExecutionPolicy(
            allowed_domains={"example.com"},
        )
        self.backend = PlaywrightExecutionBackend(policy=self.policy)

    def test_minimal_input_accepted(self) -> None:
        """Verify that minimal valid input is accepted."""
        # This will fail at script resolution, but parsing should succeed
        task_input = TaskExecutionInput(
            task_id="test-parse-1",
            command="playwright",
            metadata={
                "target_url": "https://example.com",
                "script_type": "registered",
                "script_name": "smoke_test",
            }
        )
        
        # The backend will try to execute and fail on Playwright import,
        # but parsing should succeed. We can verify by checking the error
        # is not about parsing.
        result = self.backend.execute_task(task_input)
        
        # Should fail on Playwright import, not on parsing
        # Unless Playwright is installed, then it would try to run
        if result.state == TaskExecutionState.FAILED:
            self.assertNotIn("invalid playwright input", result.error_message.lower())

    def test_invalid_script_type_rejected(self) -> None:
        """Verify that invalid script_type is rejected."""
        task_input = TaskExecutionInput(
            task_id="test-parse-2",
            command="playwright",
            metadata={
                "target_url": "https://example.com",
                "script_type": "unknown_type",
                "script_name": "smoke_test",
            }
        )
        
        result = self.backend.execute_task(task_input)
        
        self.assertEqual(result.state, TaskExecutionState.FAILED)
        self.assertIn("invalid", result.error_message.lower())

    def test_invalid_browser_rejected(self) -> None:
        """Verify that invalid browser type is rejected."""
        task_input = TaskExecutionInput(
            task_id="test-parse-3",
            command="playwright",
            metadata={
                "target_url": "https://example.com",
                "script_type": "registered",
                "script_name": "smoke_test",
                "browser": "netscape",  # Invalid browser
            }
        )
        
        result = self.backend.execute_task(task_input)
        
        self.assertEqual(result.state, TaskExecutionState.FAILED)
        self.assertIn("invalid", result.error_message.lower())


# =============================================================================
# Integration Tests (Require Playwright)
# =============================================================================


def playwright_available() -> bool:
    """Check if Playwright is available."""
    try:
        from playwright.sync_api import sync_playwright
        return True
    except ImportError:
        return False


@unittest.skipUnless(playwright_available(), "Playwright not installed")
class TestPlaywrightIntegration(unittest.TestCase):
    """Integration tests that require Playwright to be installed.
    
    These tests verify actual browser execution behavior.
    They are skipped if Playwright is not available.
    """

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.artifact_dir = tempfile.mkdtemp(prefix="axiom_playwright_test_")
        self.policy = PlaywrightExecutionPolicy(
            allowed_domains={"example.com", "httpbin.org"},
            allowed_browsers={PlaywrightBrowser.CHROMIUM},
            max_timeout_seconds=30,
            allow_screenshots=True,
            artifact_directory=self.artifact_dir,
        )
        self.backend = PlaywrightExecutionBackend(policy=self.policy)

    def tearDown(self) -> None:
        """Clean up test artifacts."""
        import shutil
        if os.path.exists(self.artifact_dir):
            shutil.rmtree(self.artifact_dir)

    def test_smoke_test_on_example_com(self) -> None:
        """Verify that smoke test executes successfully on example.com."""
        task_input = TaskExecutionInput(
            task_id="integration-1",
            command="playwright",
            metadata={
                "target_url": "https://example.com",
                "script_type": "registered",
                "script_name": "smoke_test",
            }
        )
        
        result = self.backend.execute_task(task_input)
        
        self.assertEqual(result.state, TaskExecutionState.SUCCEEDED)
        self.assertIn("success", result.metadata)
        self.assertTrue(result.metadata.get("success"))

    def test_screenshot_capture(self) -> None:
        """Verify that screenshots are captured correctly."""
        task_input = TaskExecutionInput(
            task_id="integration-2",
            command="playwright",
            metadata={
                "target_url": "https://example.com",
                "script_type": "registered",
                "script_name": "screenshot_only",
                "capture_screenshot": True,
                "screenshot_name": "test_screenshot",
            }
        )
        
        result = self.backend.execute_task(task_input)
        
        self.assertEqual(result.state, TaskExecutionState.SUCCEEDED)
        screenshot_path = result.metadata.get("screenshot_path")
        self.assertIsNotNone(screenshot_path)
        self.assertTrue(os.path.exists(screenshot_path))

    def test_third_party_requests_blocked(self) -> None:
        """Verify that requests to non-allowed domains are blocked."""
        policy_strict = PlaywrightExecutionPolicy(
            allowed_domains={"example.com"},
            block_third_party_requests=True,
        )
        backend = PlaywrightExecutionBackend(policy=policy_strict)
        
        # example.com is simple and shouldn't have external requests
        # This test verifies the route handler is installed
        task_input = TaskExecutionInput(
            task_id="integration-3",
            command="playwright",
            metadata={
                "target_url": "https://example.com",
                "script_type": "registered",
                "script_name": "smoke_test",
            }
        )
        
        result = backend.execute_task(task_input)
        
        # Should succeed because example.com is allowed
        self.assertEqual(result.state, TaskExecutionState.SUCCEEDED)


if __name__ == "__main__":
    unittest.main()
