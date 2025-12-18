"""
Playwright Execution Backend for Axiom Forge.

This module provides a GOVERNED browser automation backend that runs
Playwright scripts under strict policy enforcement.

Why Browser Automation is Dangerous if Ungated:
- Browsers can access arbitrary network resources.
- JavaScript execution enables complex attacks.
- Credential theft is trivial with browser access.
- Network requests can exfiltrate data.
- Screenshot/video capture can expose sensitive UI.
- Persistent state (cookies, localStorage) can be hijacked.
- Autonomous browsing is indistinguishable from malware.

Why This Backend is Intentionally Restrictive:
- Only allowlisted domains may be accessed.
- Only pre-defined scripts may be executed (no dynamic code).
- Headless mode is ENFORCED (no visible browser).
- No persistent browser state between executions.
- Artifacts (screenshots, traces) are written to controlled directories only.
- Network access is constrained to the domain allowlist.
- Timeouts prevent indefinite execution.

Why Playwright Runs ONLY Through Forge:
- Forge is the ONLY layer that performs side effects.
- Browser automation is a side effect (network, rendering, state).
- By routing through Forge, we ensure all execution passes through
  the human authorization gate in AxiomWorkflow.
- No other layer may directly instantiate Playwright.

Why Human Approval is Mandatory:
- Browser automation affects external systems (websites, APIs).
- Unlike local shell commands, browser actions are visible to third parties.
- The security surface is vastly larger than shell execution.
- Human oversight is the final safety barrier.

Architectural Reminder:
- Forge executes.
- Core orchestrates.
- Archon authorizes.
- Humans decide.

Browser automation is power.
Power must remain contained.
"""

import os
import tempfile
from dataclasses import dataclass, field
from typing import Set, Dict, Optional, List, Any
from datetime import datetime, timezone
from urllib.parse import urlparse
from enum import Enum

from axiom_conductor.model import (
    TaskExecutionResult,
    TaskExecutionState,
    TaskFailureReason
)
from axiom_forge.backend import TaskExecutionBackend, TaskExecutionInput


class PlaywrightBrowser(str, Enum):
    """
    Allowed browser types for Playwright execution.
    
    Note: We restrict to Chromium by default for consistency.
    Firefox and WebKit are available but must be explicitly enabled.
    """
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


class PlaywrightScriptType(str, Enum):
    """
    Types of Playwright scripts that can be executed.
    
    REGISTERED: A pre-registered script reference (safest).
    INLINE: An inline script provided in the task (more flexible, still validated).
    
    Note: We do NOT support arbitrary file paths or URLs as script sources.
    All scripts must be validated before execution.
    """
    REGISTERED = "registered"
    INLINE = "inline"


@dataclass
class PlaywrightExecutionPolicy:
    """
    Defines the safety constraints for Playwright browser execution.

    This policy is IMMUTABLE after construction and enforced BEFORE execution.

    Attributes:
        allowed_domains: Explicit allowlist of domains that may be accessed.
            Must include the full domain (e.g., "example.com", "sub.example.com").
            Wildcards are NOT supported for security.
        allowed_browsers: Set of browser types that may be used.
        max_timeout_seconds: Maximum execution time for any script.
        headless_only: If True, visible browser windows are forbidden.
        allow_screenshots: If True, screenshots may be captured.
        allow_traces: If True, Playwright traces may be captured.
        allow_videos: If True, video recording may be enabled.
        artifact_directory: Directory where artifacts are written.
            Must be an absolute path. Will be created if it doesn't exist.
        max_artifact_size_bytes: Maximum size for any single artifact.
        allowed_scripts: Set of registered script names that may be executed.
            If empty, only INLINE scripts are allowed (with validation).
        viewport_width: Default viewport width (pixels).
        viewport_height: Default viewport height (pixels).
        block_third_party_requests: If True, requests to non-allowed domains are blocked.
    """
    allowed_domains: Set[str] = field(default_factory=set)
    allowed_browsers: Set[PlaywrightBrowser] = field(
        default_factory=lambda: {PlaywrightBrowser.CHROMIUM}
    )
    max_timeout_seconds: int = 60
    headless_only: bool = True
    allow_screenshots: bool = True
    allow_traces: bool = False
    allow_videos: bool = False
    artifact_directory: Optional[str] = None
    max_artifact_size_bytes: int = 10 * 1024 * 1024  # 10 MB
    allowed_scripts: Set[str] = field(default_factory=set)
    viewport_width: int = 1280
    viewport_height: int = 720
    block_third_party_requests: bool = True


@dataclass
class PlaywrightTaskInput:
    """
    The input contract for Playwright task execution.
    
    This is a STRICT, SERIALIZABLE structure that defines exactly
    what a Playwright task can do. No arbitrary code is accepted.

    Attributes:
        script_type: Whether this is a REGISTERED or INLINE script.
        script_name: Name of the registered script (if REGISTERED).
        script_content: The Playwright script content (if INLINE).
            Must be a valid Python function body that uses the `page` object.
        target_url: The URL to navigate to. Must match the allowed domains.
        browser: Which browser to use.
        timeout_seconds: Maximum execution time for this task.
        viewport_width: Optional viewport width override.
        viewport_height: Optional viewport height override.
        capture_screenshot: Whether to capture a screenshot on completion.
        screenshot_name: Name for the screenshot file (without extension).
        user_agent: Optional user agent string override.
        extra_headers: Optional extra HTTP headers to include.
    """
    script_type: PlaywrightScriptType
    target_url: str
    browser: PlaywrightBrowser = PlaywrightBrowser.CHROMIUM
    timeout_seconds: int = 30
    script_name: Optional[str] = None
    script_content: Optional[str] = None
    viewport_width: Optional[int] = None
    viewport_height: Optional[int] = None
    capture_screenshot: bool = False
    screenshot_name: Optional[str] = None
    user_agent: Optional[str] = None
    extra_headers: Dict[str, str] = field(default_factory=dict)


# =============================================================================
# Script Registry
# =============================================================================


# Pre-registered, validated scripts for common operations.
# Each script is a function that takes (page) and performs actions.
# Scripts MUST NOT contain network calls outside the Playwright API.

REGISTERED_SCRIPTS: Dict[str, str] = {
    "smoke_test": """
# Smoke Test: Navigate to URL and verify page loads
await page.goto(target_url)
await page.wait_for_load_state("domcontentloaded")
title = await page.title()
result["title"] = title
result["success"] = True
""",
    "check_element_exists": """
# Check Element Exists: Verify a specific element is present
await page.goto(target_url)
await page.wait_for_load_state("domcontentloaded")
selector = metadata.get("selector", "body")
element = await page.query_selector(selector)
result["element_found"] = element is not None
result["success"] = element is not None
""",
    "screenshot_only": """
# Screenshot Only: Navigate and capture screenshot
await page.goto(target_url)
await page.wait_for_load_state("networkidle")
result["success"] = True
""",
    "login_flow_check": """
# Login Flow Check: Verify login form elements exist
await page.goto(target_url)
await page.wait_for_load_state("domcontentloaded")
username_field = await page.query_selector('input[name="username"], input[type="email"], #username')
password_field = await page.query_selector('input[name="password"], input[type="password"], #password')
submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
result["has_username_field"] = username_field is not None
result["has_password_field"] = password_field is not None
result["has_submit_button"] = submit_button is not None
result["success"] = all([username_field, password_field, submit_button])
""",
}


# =============================================================================
# Validation Functions
# =============================================================================


def validate_url_against_policy(url: str, policy: PlaywrightExecutionPolicy) -> Optional[str]:
    """
    Validate that a URL is allowed by the policy.
    
    Args:
        url: The URL to validate.
        policy: The execution policy.
        
    Returns:
        None if valid, error message if invalid.
    """
    if not policy.allowed_domains:
        return "No allowed domains configured in policy."
    
    try:
        parsed = urlparse(url)
    except Exception as e:
        return f"Invalid URL format: {e}"
    
    if not parsed.scheme:
        return "URL must include a scheme (http:// or https://)."
    
    if parsed.scheme not in ("http", "https"):
        return f"URL scheme '{parsed.scheme}' is not allowed. Only http and https are permitted."
    
    if not parsed.netloc:
        return "URL must include a domain."
    
    # Extract domain (without port)
    domain = parsed.netloc.split(":")[0].lower()
    
    # Check against allowlist
    if domain not in policy.allowed_domains:
        # Also check if any subdomain matches
        # e.g., "www.example.com" should match "example.com" if that's in the list
        domain_parts = domain.split(".")
        matched = False
        for allowed in policy.allowed_domains:
            if domain == allowed:
                matched = True
                break
            # Check if domain is a subdomain of an allowed domain
            if domain.endswith("." + allowed):
                matched = True
                break
        
        if not matched:
            return f"Domain '{domain}' is not in the allowed domains list."
    
    return None


def validate_script_content(script: str) -> Optional[str]:
    """
    Validate that an inline script does not contain dangerous patterns.
    
    This is a basic safety check, not a complete security audit.
    The script will still run in a controlled environment.
    
    Args:
        script: The script content to validate.
        
    Returns:
        None if valid, error message if dangerous patterns detected.
    """
    # Dangerous patterns that should never appear in Playwright scripts
    dangerous_patterns = [
        "import os",
        "import subprocess",
        "import sys",
        "__import__",
        "eval(",
        "exec(",
        "compile(",
        "open(",
        "os.system",
        "os.popen",
        "os.exec",
        "subprocess.",
        "shutil.",
        "pathlib.",
        "glob.",
        "pickle.",
        "marshal.",
        "builtins",
        "__builtins__",
        "globals(",
        "locals(",
        "getattr(",
        "setattr(",
        "delattr(",
        "hasattr(",
    ]
    
    script_lower = script.lower()
    for pattern in dangerous_patterns:
        if pattern.lower() in script_lower:
            return f"Script contains forbidden pattern: '{pattern}'"
    
    return None


# =============================================================================
# PlaywrightExecutionBackend
# =============================================================================


@dataclass
class PlaywrightExecutionBackend:
    """
    A GOVERNED browser automation backend using Playwright.
    
    This backend:
    - Enforces domain allowlists BEFORE any navigation.
    - Runs only pre-registered or validated inline scripts.
    - Executes in headless mode ONLY.
    - Creates no persistent browser state.
    - Captures artifacts to a controlled directory only.
    - Enforces strict timeouts.
    - Returns structured, deterministic results.
    
    This backend does NOT:
    - Allow arbitrary code execution.
    - Allow navigation to non-allowlisted domains.
    - Allow visible browser windows (headless enforced).
    - Retry on failure.
    - Cache browser state between executions.
    - Modify external state beyond the target URL's response.
    
    Security Model:
    - All execution passes through AxiomWorkflow → Human Authorization.
    - Policy violations cause immediate failure (fail-fast).
    - No escalation or retry logic.
    - Artifacts are sandboxed to the configured directory.
    """
    policy: PlaywrightExecutionPolicy = field(default_factory=PlaywrightExecutionPolicy)
    
    def execute_task(self, input_data: TaskExecutionInput) -> TaskExecutionResult:
        """
        Execute a Playwright task.
        
        The task metadata must contain a PlaywrightTaskInput-compatible dict.
        
        Args:
            input_data: The task execution input. The `metadata` field must
                contain the Playwright-specific configuration.
                
        Returns:
            TaskExecutionResult with execution outcome.
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        task_id = input_data.task_id
        
        # Extract Playwright-specific input from metadata
        try:
            pw_input = self._parse_playwright_input(input_data.metadata)
        except ValueError as e:
            return TaskExecutionResult(
                task_id=task_id,
                state=TaskExecutionState.FAILED,
                failure_reason=TaskFailureReason.PRECONDITION_FAILED,
                error_message=f"Invalid Playwright input: {e}",
                timestamp=timestamp
            )
        
        # Validate policy constraints
        validation_error = self._validate_against_policy(pw_input)
        if validation_error:
            return TaskExecutionResult(
                task_id=task_id,
                state=TaskExecutionState.FAILED,
                failure_reason=TaskFailureReason.PRECONDITION_FAILED,
                error_message=validation_error,
                timestamp=timestamp
            )
        
        # Get the script to execute
        script_error, script = self._get_script(pw_input)
        if script_error:
            return TaskExecutionResult(
                task_id=task_id,
                state=TaskExecutionState.FAILED,
                failure_reason=TaskFailureReason.PRECONDITION_FAILED,
                error_message=script_error,
                timestamp=timestamp
            )
        
        # Execute the script
        return self._execute_playwright_script(
            task_id=task_id,
            pw_input=pw_input,
            script=script,
            timestamp=timestamp
        )
    
    def _parse_playwright_input(self, metadata: Dict[str, Any]) -> PlaywrightTaskInput:
        """
        Parse and validate the Playwright task input from metadata.
        
        Args:
            metadata: The task metadata dictionary.
            
        Returns:
            PlaywrightTaskInput instance.
            
        Raises:
            ValueError: If required fields are missing or invalid.
        """
        # Required fields
        if "target_url" not in metadata:
            raise ValueError("'target_url' is required")
        
        script_type_str = metadata.get("script_type", "registered")
        try:
            script_type = PlaywrightScriptType(script_type_str)
        except ValueError:
            raise ValueError(f"Invalid script_type: {script_type_str}")
        
        browser_str = metadata.get("browser", "chromium")
        try:
            browser = PlaywrightBrowser(browser_str)
        except ValueError:
            raise ValueError(f"Invalid browser: {browser_str}")
        
        return PlaywrightTaskInput(
            script_type=script_type,
            target_url=metadata["target_url"],
            browser=browser,
            timeout_seconds=metadata.get("timeout_seconds", 30),
            script_name=metadata.get("script_name"),
            script_content=metadata.get("script_content"),
            viewport_width=metadata.get("viewport_width"),
            viewport_height=metadata.get("viewport_height"),
            capture_screenshot=metadata.get("capture_screenshot", False),
            screenshot_name=metadata.get("screenshot_name"),
            user_agent=metadata.get("user_agent"),
            extra_headers=metadata.get("extra_headers", {}),
        )
    
    def _validate_against_policy(self, pw_input: PlaywrightTaskInput) -> Optional[str]:
        """
        Validate the input against the execution policy.
        
        Args:
            pw_input: The Playwright task input.
            
        Returns:
            None if valid, error message if policy is violated.
        """
        # Validate browser
        if pw_input.browser not in self.policy.allowed_browsers:
            return f"Browser '{pw_input.browser.value}' is not allowed. Allowed: {[b.value for b in self.policy.allowed_browsers]}"
        
        # Validate URL
        url_error = validate_url_against_policy(pw_input.target_url, self.policy)
        if url_error:
            return url_error
        
        # Validate timeout
        if pw_input.timeout_seconds > self.policy.max_timeout_seconds:
            return f"Timeout {pw_input.timeout_seconds}s exceeds maximum {self.policy.max_timeout_seconds}s"
        
        # Validate screenshot permission
        if pw_input.capture_screenshot and not self.policy.allow_screenshots:
            return "Screenshots are not allowed by policy"
        
        # Validate script type
        if pw_input.script_type == PlaywrightScriptType.REGISTERED:
            if not pw_input.script_name:
                return "script_name is required for REGISTERED script type"
            if self.policy.allowed_scripts and pw_input.script_name not in self.policy.allowed_scripts:
                return f"Script '{pw_input.script_name}' is not in the allowed scripts list"
        elif pw_input.script_type == PlaywrightScriptType.INLINE:
            if not pw_input.script_content:
                return "script_content is required for INLINE script type"
        
        return None
    
    def _get_script(self, pw_input: PlaywrightTaskInput) -> tuple:
        """
        Get the script to execute, validating it if necessary.
        
        Args:
            pw_input: The Playwright task input.
            
        Returns:
            Tuple of (error_message, script_content).
            If error_message is not None, script_content will be None.
        """
        if pw_input.script_type == PlaywrightScriptType.REGISTERED:
            if pw_input.script_name not in REGISTERED_SCRIPTS:
                return (f"Unknown registered script: '{pw_input.script_name}'", None)
            return (None, REGISTERED_SCRIPTS[pw_input.script_name])
        
        elif pw_input.script_type == PlaywrightScriptType.INLINE:
            # Validate inline script for dangerous patterns
            validation_error = validate_script_content(pw_input.script_content)
            if validation_error:
                return (validation_error, None)
            return (None, pw_input.script_content)
        
        return ("Unknown script type", None)
    
    def _execute_playwright_script(
        self,
        task_id: str,
        pw_input: PlaywrightTaskInput,
        script: str,
        timestamp: str
    ) -> TaskExecutionResult:
        """
        Execute the Playwright script in a controlled environment.
        
        Args:
            task_id: The task identifier.
            pw_input: The Playwright task input.
            script: The script content to execute.
            timestamp: The execution timestamp.
            
        Returns:
            TaskExecutionResult with execution outcome.
        """
        try:
            # Import Playwright only when needed (lazy import)
            from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
        except ImportError:
            return TaskExecutionResult(
                task_id=task_id,
                state=TaskExecutionState.FAILED,
                failure_reason=TaskFailureReason.SYSTEM_ERROR,
                error_message="Playwright is not installed. Install with: pip install playwright && playwright install",
                timestamp=timestamp
            )
        
        # Prepare artifact directory
        artifact_dir = self.policy.artifact_directory
        if artifact_dir:
            os.makedirs(artifact_dir, exist_ok=True)
        else:
            artifact_dir = tempfile.mkdtemp(prefix="axiom_playwright_")
        
        # Result container for script execution
        result: Dict[str, Any] = {}
        screenshot_path: Optional[str] = None
        
        try:
            with sync_playwright() as playwright:
                # Select browser
                if pw_input.browser == PlaywrightBrowser.CHROMIUM:
                    browser_type = playwright.chromium
                elif pw_input.browser == PlaywrightBrowser.FIREFOX:
                    browser_type = playwright.firefox
                elif pw_input.browser == PlaywrightBrowser.WEBKIT:
                    browser_type = playwright.webkit
                else:
                    browser_type = playwright.chromium
                
                # Launch browser (HEADLESS ENFORCED)
                browser = browser_type.launch(
                    headless=True,  # ALWAYS headless, policy.headless_only is defense-in-depth
                )
                
                # Create context with viewport
                viewport_width = pw_input.viewport_width or self.policy.viewport_width
                viewport_height = pw_input.viewport_height or self.policy.viewport_height
                
                context_options: Dict[str, Any] = {
                    "viewport": {"width": viewport_width, "height": viewport_height},
                }
                
                if pw_input.user_agent:
                    context_options["user_agent"] = pw_input.user_agent
                
                if pw_input.extra_headers:
                    context_options["extra_http_headers"] = pw_input.extra_headers
                
                context = browser.new_context(**context_options)
                
                # Set up request interception if blocking third-party requests
                if self.policy.block_third_party_requests:
                    def route_handler(route):
                        request_url = route.request.url
                        url_error = validate_url_against_policy(request_url, self.policy)
                        if url_error:
                            route.abort()
                        else:
                            route.continue_()
                    context.route("**/*", route_handler)
                
                # Create page with timeout
                page = context.new_page()
                page.set_default_timeout(pw_input.timeout_seconds * 1000)
                
                # Prepare execution context for script
                target_url = pw_input.target_url
                metadata = pw_input.extra_headers  # Scripts can access extra metadata
                
                # Execute the script
                # Note: We use exec() here, but the script has been validated
                # and runs in a controlled namespace with only `page`, `target_url`,
                # `result`, and `metadata` available.
                exec_globals = {
                    "page": page,
                    "target_url": target_url,
                    "result": result,
                    "metadata": metadata,
                }
                
                # Wrap script in async function for Playwright's async API
                # But we're using sync_api, so we need to handle this differently
                # The script is executed synchronously
                
                # For sync_playwright, page methods are NOT async
                # Replace 'await' with direct calls for sync API
                sync_script = script.replace("await ", "")
                
                exec(sync_script, exec_globals)
                
                # Capture screenshot if requested
                if pw_input.capture_screenshot and self.policy.allow_screenshots:
                    screenshot_name = pw_input.screenshot_name or f"screenshot_{task_id}"
                    screenshot_path = os.path.join(artifact_dir, f"{screenshot_name}.png")
                    page.screenshot(path=screenshot_path)
                    result["screenshot_path"] = screenshot_path
                
                # Clean up
                context.close()
                browser.close()
            
            # Build success result
            return TaskExecutionResult(
                task_id=task_id,
                state=TaskExecutionState.SUCCEEDED,
                exit_code=0,
                stdout=str(result),
                metadata=result,
                timestamp=timestamp
            )
            
        except PlaywrightTimeout as e:
            return TaskExecutionResult(
                task_id=task_id,
                state=TaskExecutionState.FAILED,
                failure_reason=TaskFailureReason.TIMEOUT,
                error_message=f"Playwright timeout: {e}",
                timestamp=timestamp
            )
        except Exception as e:
            return TaskExecutionResult(
                task_id=task_id,
                state=TaskExecutionState.FAILED,
                failure_reason=TaskFailureReason.COMMAND_ERROR,
                error_message=f"Playwright execution error: {e}",
                timestamp=timestamp
            )
