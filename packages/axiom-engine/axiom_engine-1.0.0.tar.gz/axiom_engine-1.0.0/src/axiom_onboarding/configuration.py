"""
Operator & Infrastructure Configuration.

This module provides configuration utilities for:
- Executor Registry setup
- Policy configuration
- Authentication token management
- Environment configuration

CONFIGURATION PRINCIPLES:
1. EXPLICIT: All configuration is explicit, never inferred
2. VALIDATED: All configuration is validated before use
3. VERSIONED: Configuration changes are trackable
4. SECURE: Secrets are never stored in plain text
5. DOCUMENTED: Every option is self-documenting

RULES (ABSOLUTE):
- Configuration errors fail fast
- Invalid configuration never reaches execution
- Default configuration is always safe (restrictive)
- Secrets must be encrypted or use environment variables
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set
import json
import os


# =============================================================================
# Configuration Errors
# =============================================================================


class ConfigurationError(Exception):
    """
    Error in configuration.
    
    Provides detailed information about what's wrong and how to fix it.
    
    Attributes:
        field: The field that has an error.
        value: The invalid value.
        reason: Why it's invalid.
        fix: How to fix it.
    """
    
    def __init__(
        self,
        message: str,
        field: str = "",
        value: Any = None,
        reason: str = "",
        fix: str = "",
    ) -> None:
        """
        Initialize configuration error.
        
        Args:
            message: Error message.
            field: Field with error.
            value: Invalid value.
            reason: Why it's invalid.
            fix: How to fix it.
        """
        self.field = field
        self.value = value
        self.reason = reason
        self.fix = fix
        
        full_message = self._build_message(message)
        super().__init__(full_message)
    
    def _build_message(self, message: str) -> str:
        """Build detailed error message."""
        lines = []
        lines.append("")
        lines.append("╔═══ CONFIGURATION ERROR ═══════════════════════════════════════╗")
        lines.append("")
        lines.append(f"  {message}")
        lines.append("")
        
        if self.field:
            lines.append(f"  Field: {self.field}")
        if self.value is not None:
            value_str = str(self.value)
            if len(value_str) > 50:
                value_str = value_str[:50] + "..."
            lines.append(f"  Value: {value_str}")
        if self.reason:
            lines.append(f"  Reason: {self.reason}")
        
        lines.append("")
        
        if self.fix:
            lines.append("  How to Fix:")
            lines.append(f"    {self.fix}")
            lines.append("")
        
        lines.append("╚════════════════════════════════════════════════════════════════╝")
        lines.append("")
        
        return "\n".join(lines)


# =============================================================================
# Executor Configuration
# =============================================================================


class ExecutorType(str, Enum):
    """Type of executor."""
    
    SHELL = "shell"
    PLAYWRIGHT = "playwright"
    COPILOT = "copilot"
    REMOTE = "remote"
    MOCK = "mock"


class ExecutorCapability(str, Enum):
    """Capabilities an executor can have."""
    
    CODE_GENERATION = "code_generation"
    FILE_WRITE = "file_write"
    FILE_READ = "file_read"
    SHELL_COMMAND = "shell_command"
    BROWSER_CONTROL = "browser_control"
    API_CALL = "api_call"


@dataclass
class ExecutorConfig:
    """
    Configuration for a single executor.
    
    Attributes:
        executor_type: Type of executor.
        enabled: Whether this executor is enabled.
        capabilities: Capabilities this executor has.
        allowed_commands: For shell, list of allowed commands.
        blocked_commands: For shell, list of blocked commands.
        working_directory: Working directory for execution.
        timeout_seconds: Timeout for operations.
        require_approval: Whether human approval is required.
        metadata: Additional executor-specific configuration.
    """
    
    executor_type: ExecutorType
    enabled: bool = True
    capabilities: List[ExecutorCapability] = field(default_factory=list)
    allowed_commands: List[str] = field(default_factory=list)
    blocked_commands: List[str] = field(default_factory=lambda: [
        "rm -rf", "sudo", "mkfs", "dd", "chmod 777",
        "curl | sh", "wget | sh", "eval",
    ])
    working_directory: str = ""
    timeout_seconds: int = 300
    require_approval: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutorConfiguration:
    """
    Complete executor configuration.
    
    Attributes:
        executors: Configured executors by name.
        default_executor: Name of default executor.
        version: Configuration version.
        created_at: When configuration was created.
        modified_at: When last modified.
    """
    
    executors: Dict[str, ExecutorConfig] = field(default_factory=dict)
    default_executor: str = "shell"
    version: str = "1.0.0"
    created_at: str = ""
    modified_at: str = ""
    
    def __post_init__(self) -> None:
        """Set timestamps if not provided."""
        now = datetime.now(timezone.utc).isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.modified_at:
            self.modified_at = now
    
    def add_executor(
        self,
        name: str,
        config: ExecutorConfig,
    ) -> None:
        """
        Add an executor configuration.
        
        Args:
            name: Name for this executor.
            config: Executor configuration.
        """
        self.executors[name] = config
        self.modified_at = datetime.now(timezone.utc).isoformat()
    
    def get_executor(self, name: str) -> Optional[ExecutorConfig]:
        """
        Get executor configuration by name.
        
        Args:
            name: Executor name.
        
        Returns:
            ExecutorConfig or None.
        """
        return self.executors.get(name)
    
    def is_enabled(self, name: str) -> bool:
        """Check if an executor is enabled."""
        config = self.executors.get(name)
        return config is not None and config.enabled
    
    @classmethod
    def create_safe_default(cls) -> "ExecutorConfiguration":
        """
        Create a safe default configuration.
        
        Returns restrictive defaults suitable for first run.
        
        Returns:
            Safe default ExecutorConfiguration.
        """
        config = cls()
        
        # Add safe shell executor
        shell_config = ExecutorConfig(
            executor_type=ExecutorType.SHELL,
            enabled=True,
            capabilities=[
                ExecutorCapability.FILE_READ,
            ],
            allowed_commands=[
                "ls", "cat", "head", "tail", "grep", "find",
                "pwd", "echo", "date", "wc",
            ],
            require_approval=True,
            timeout_seconds=60,
        )
        config.add_executor("shell", shell_config)
        
        # Add mock executor (for testing)
        mock_config = ExecutorConfig(
            executor_type=ExecutorType.MOCK,
            enabled=True,
            capabilities=[],
            require_approval=False,
        )
        config.add_executor("mock", mock_config)
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "version": self.version,
            "default_executor": self.default_executor,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "executors": {
                name: {
                    "executor_type": config.executor_type.value,
                    "enabled": config.enabled,
                    "capabilities": [c.value for c in config.capabilities],
                    "allowed_commands": config.allowed_commands,
                    "blocked_commands": config.blocked_commands,
                    "working_directory": config.working_directory,
                    "timeout_seconds": config.timeout_seconds,
                    "require_approval": config.require_approval,
                    "metadata": config.metadata,
                }
                for name, config in self.executors.items()
            },
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutorConfiguration":
        """Create from dictionary."""
        config = cls(
            version=data.get("version", "1.0.0"),
            default_executor=data.get("default_executor", "shell"),
            created_at=data.get("created_at", ""),
            modified_at=data.get("modified_at", ""),
        )
        
        for name, exec_data in data.get("executors", {}).items():
            exec_config = ExecutorConfig(
                executor_type=ExecutorType(exec_data.get("executor_type", "shell")),
                enabled=exec_data.get("enabled", True),
                capabilities=[
                    ExecutorCapability(c)
                    for c in exec_data.get("capabilities", [])
                ],
                allowed_commands=exec_data.get("allowed_commands", []),
                blocked_commands=exec_data.get("blocked_commands", []),
                working_directory=exec_data.get("working_directory", ""),
                timeout_seconds=exec_data.get("timeout_seconds", 300),
                require_approval=exec_data.get("require_approval", True),
                metadata=exec_data.get("metadata", {}),
            )
            config.executors[name] = exec_config
        
        return config


# =============================================================================
# Policy Configuration
# =============================================================================


class PolicyLevel(str, Enum):
    """Level at which a policy applies."""
    
    GLOBAL = "global"      # Applies to everything
    EXECUTOR = "executor"  # Applies to specific executor
    TASK = "task"          # Applies to specific task type


class PolicyAction(str, Enum):
    """Action a policy takes."""
    
    ALLOW = "allow"        # Allow the action
    DENY = "deny"          # Deny the action
    REQUIRE_APPROVAL = "require_approval"  # Require human approval
    WARN = "warn"          # Warn but allow
    LOG = "log"            # Log only


@dataclass
class Policy:
    """
    A single policy rule.
    
    Attributes:
        id: Unique identifier.
        name: Human-readable name.
        description: What this policy does.
        level: Level at which it applies.
        action: Action to take.
        conditions: Conditions that trigger this policy.
        enabled: Whether policy is active.
    """
    
    id: str
    name: str
    description: str
    level: PolicyLevel
    action: PolicyAction
    conditions: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


@dataclass
class PolicyConfiguration:
    """
    Complete policy configuration.
    
    Attributes:
        policies: Defined policies.
        default_action: Default action when no policy matches.
        require_human_approval: Global approval requirement.
        max_concurrent_tasks: Maximum concurrent tasks.
        version: Configuration version.
    """
    
    policies: Dict[str, Policy] = field(default_factory=dict)
    default_action: PolicyAction = PolicyAction.REQUIRE_APPROVAL
    require_human_approval: bool = True
    max_concurrent_tasks: int = 1
    version: str = "1.0.0"
    
    def add_policy(self, policy: Policy) -> None:
        """Add a policy."""
        self.policies[policy.id] = policy
    
    def get_policy(self, policy_id: str) -> Optional[Policy]:
        """Get a policy by ID."""
        return self.policies.get(policy_id)
    
    def evaluate(
        self,
        action: str,
        context: Dict[str, Any] = None,
    ) -> PolicyAction:
        """
        Evaluate policies for an action.
        
        Args:
            action: The action to evaluate.
            context: Additional context.
        
        Returns:
            The action to take.
        """
        context = context or {}
        
        # Check each policy
        for policy in self.policies.values():
            if not policy.enabled:
                continue
            
            # Simple condition matching
            matches = True
            for key, value in policy.conditions.items():
                if context.get(key) != value:
                    matches = False
                    break
            
            if matches:
                return policy.action
        
        return self.default_action
    
    @classmethod
    def create_safe_default(cls) -> "PolicyConfiguration":
        """
        Create safe default policy configuration.
        
        Returns:
            Restrictive default PolicyConfiguration.
        """
        config = cls(
            default_action=PolicyAction.REQUIRE_APPROVAL,
            require_human_approval=True,
            max_concurrent_tasks=1,
        )
        
        # Add default policies
        config.add_policy(Policy(
            id="block_destructive",
            name="Block Destructive Operations",
            description="Deny operations that could destroy data",
            level=PolicyLevel.GLOBAL,
            action=PolicyAction.DENY,
            conditions={"destructive": True},
        ))
        
        config.add_policy(Policy(
            id="require_code_review",
            name="Require Code Review",
            description="Require approval for code changes",
            level=PolicyLevel.TASK,
            action=PolicyAction.REQUIRE_APPROVAL,
            conditions={"type": "code_change"},
        ))
        
        config.add_policy(Policy(
            id="log_read_operations",
            name="Log Read Operations",
            description="Log but allow read operations",
            level=PolicyLevel.GLOBAL,
            action=PolicyAction.LOG,
            conditions={"type": "read"},
        ))
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "default_action": self.default_action.value,
            "require_human_approval": self.require_human_approval,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "policies": {
                pid: {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "level": p.level.value,
                    "action": p.action.value,
                    "conditions": p.conditions,
                    "enabled": p.enabled,
                }
                for pid, p in self.policies.items()
            },
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PolicyConfiguration":
        """Create from dictionary."""
        config = cls(
            default_action=PolicyAction(data.get("default_action", "require_approval")),
            require_human_approval=data.get("require_human_approval", True),
            max_concurrent_tasks=data.get("max_concurrent_tasks", 1),
            version=data.get("version", "1.0.0"),
        )
        
        for pid, pdata in data.get("policies", {}).items():
            policy = Policy(
                id=pdata.get("id", pid),
                name=pdata.get("name", ""),
                description=pdata.get("description", ""),
                level=PolicyLevel(pdata.get("level", "global")),
                action=PolicyAction(pdata.get("action", "require_approval")),
                conditions=pdata.get("conditions", {}),
                enabled=pdata.get("enabled", True),
            )
            config.policies[pid] = policy
        
        return config


# =============================================================================
# Configuration Validator
# =============================================================================


@dataclass
class ValidationResult:
    """Result of configuration validation."""
    
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def add_error(self, error: str) -> None:
        """Add an error."""
        self.errors.append(error)
        self.valid = False
    
    def add_warning(self, warning: str) -> None:
        """Add a warning."""
        self.warnings.append(warning)


class ConfigurationValidator:
    """
    Validates configuration before use.
    
    Ensures configuration is valid, safe, and complete.
    """
    
    def __init__(self) -> None:
        """Initialize validator."""
        self._validators: List[Callable[[Any], ValidationResult]] = []
    
    def validate_executor_config(
        self,
        config: ExecutorConfiguration,
    ) -> ValidationResult:
        """
        Validate executor configuration.
        
        Args:
            config: Configuration to validate.
        
        Returns:
            ValidationResult.
        """
        result = ValidationResult(valid=True)
        
        # Check for at least one executor
        if not config.executors:
            result.add_error("No executors configured")
        
        # Check default executor exists
        if config.default_executor not in config.executors:
            result.add_error(
                f"Default executor '{config.default_executor}' not configured"
            )
        
        # Check each executor
        for name, exec_config in config.executors.items():
            # Validate shell executor
            if exec_config.executor_type == ExecutorType.SHELL:
                if not exec_config.require_approval:
                    result.add_warning(
                        f"Shell executor '{name}' does not require approval"
                    )
                
                # Check for dangerous allowed commands
                dangerous = {"rm -rf", "sudo", "mkfs", "dd"}
                allowed_set = set(exec_config.allowed_commands)
                dangerous_allowed = allowed_set & dangerous
                if dangerous_allowed:
                    result.add_error(
                        f"Executor '{name}' allows dangerous commands: "
                        f"{dangerous_allowed}"
                    )
            
            # Validate timeout
            if exec_config.timeout_seconds <= 0:
                result.add_error(
                    f"Executor '{name}' has invalid timeout: "
                    f"{exec_config.timeout_seconds}"
                )
            elif exec_config.timeout_seconds > 3600:
                result.add_warning(
                    f"Executor '{name}' has very long timeout: "
                    f"{exec_config.timeout_seconds}s"
                )
        
        return result
    
    def validate_policy_config(
        self,
        config: PolicyConfiguration,
    ) -> ValidationResult:
        """
        Validate policy configuration.
        
        Args:
            config: Configuration to validate.
        
        Returns:
            ValidationResult.
        """
        result = ValidationResult(valid=True)
        
        # Check for reasonable defaults
        if config.default_action == PolicyAction.ALLOW:
            result.add_warning(
                "Default policy action is ALLOW - consider REQUIRE_APPROVAL"
            )
        
        if not config.require_human_approval:
            result.add_warning(
                "Human approval is not globally required"
            )
        
        # Check concurrent tasks
        if config.max_concurrent_tasks > 10:
            result.add_warning(
                f"High concurrent task limit: {config.max_concurrent_tasks}"
            )
        
        # Check for policy conflicts
        deny_all = any(
            p.action == PolicyAction.DENY and not p.conditions
            for p in config.policies.values()
            if p.enabled
        )
        if deny_all:
            result.add_error("Policy denies all actions (no conditions)")
        
        return result
    
    def validate_all(
        self,
        executor_config: ExecutorConfiguration,
        policy_config: PolicyConfiguration,
    ) -> ValidationResult:
        """
        Validate all configuration.
        
        Args:
            executor_config: Executor configuration.
            policy_config: Policy configuration.
        
        Returns:
            Combined ValidationResult.
        """
        result = ValidationResult(valid=True)
        
        # Validate executors
        exec_result = self.validate_executor_config(executor_config)
        result.errors.extend(exec_result.errors)
        result.warnings.extend(exec_result.warnings)
        if not exec_result.valid:
            result.valid = False
        
        # Validate policies
        policy_result = self.validate_policy_config(policy_config)
        result.errors.extend(policy_result.errors)
        result.warnings.extend(policy_result.warnings)
        if not policy_result.valid:
            result.valid = False
        
        return result


# =============================================================================
# Configuration Manager
# =============================================================================


class ConfigurationManager:
    """
    Manages configuration loading, saving, and validation.
    
    Attributes:
        config_dir: Directory for configuration files.
        executor_config: Executor configuration.
        policy_config: Policy configuration.
    """
    
    def __init__(self, config_dir: str) -> None:
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Directory for configuration files.
        """
        self.config_dir = Path(config_dir)
        self.executor_config: Optional[ExecutorConfiguration] = None
        self.policy_config: Optional[PolicyConfiguration] = None
        self._validator = ConfigurationValidator()
    
    def load(self) -> None:
        """
        Load configuration from files.
        
        Raises:
            ConfigurationError: If configuration is invalid.
        """
        executor_path = self.config_dir / "executors.json"
        policy_path = self.config_dir / "policies.json"
        
        # Load executor config
        if executor_path.exists():
            with open(executor_path) as f:
                data = json.load(f)
                self.executor_config = ExecutorConfiguration.from_dict(data)
        else:
            self.executor_config = ExecutorConfiguration.create_safe_default()
        
        # Load policy config
        if policy_path.exists():
            with open(policy_path) as f:
                data = json.load(f)
                self.policy_config = PolicyConfiguration.from_dict(data)
        else:
            self.policy_config = PolicyConfiguration.create_safe_default()
        
        # Validate
        result = self._validator.validate_all(
            self.executor_config,
            self.policy_config,
        )
        
        if not result.valid:
            raise ConfigurationError(
                message="Configuration validation failed",
                reason="; ".join(result.errors),
                fix="Fix the configuration errors and try again",
            )
    
    def save(self) -> None:
        """Save configuration to files."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Save executor config
        if self.executor_config:
            executor_path = self.config_dir / "executors.json"
            with open(executor_path, "w") as f:
                json.dump(self.executor_config.to_dict(), f, indent=2)
        
        # Save policy config
        if self.policy_config:
            policy_path = self.config_dir / "policies.json"
            with open(policy_path, "w") as f:
                json.dump(self.policy_config.to_dict(), f, indent=2)
    
    def create_defaults(self) -> None:
        """Create default configuration files."""
        self.executor_config = ExecutorConfiguration.create_safe_default()
        self.policy_config = PolicyConfiguration.create_safe_default()
        self.save()
    
    def get_configuration_guide(self) -> str:
        """
        Get a guide for configuring Axiom.
        
        Returns:
            Formatted configuration guide.
        """
        lines = []
        lines.append("")
        lines.append("╔════════════════════════════════════════════════════════════════╗")
        lines.append("║              AXIOM CONFIGURATION GUIDE                         ║")
        lines.append("╠════════════════════════════════════════════════════════════════╣")
        lines.append("")
        lines.append("  Configuration files are stored in: .axiom/")
        lines.append("")
        lines.append("  1. EXECUTOR CONFIGURATION (.axiom/executors.json)")
        lines.append("     Configure which executors are available and their permissions.")
        lines.append("")
        lines.append("     Available executor types:")
        lines.append("     • shell     - Execute shell commands")
        lines.append("     • playwright - Browser automation")
        lines.append("     • copilot   - AI code generation")
        lines.append("     • remote    - Remote execution")
        lines.append("     • mock      - Testing/simulation")
        lines.append("")
        lines.append("     Key settings:")
        lines.append("     • enabled: true/false")
        lines.append("     • allowed_commands: list of allowed commands")
        lines.append("     • blocked_commands: list of blocked commands")
        lines.append("     • require_approval: true/false")
        lines.append("     • timeout_seconds: maximum execution time")
        lines.append("")
        lines.append("  2. POLICY CONFIGURATION (.axiom/policies.json)")
        lines.append("     Define policies that control execution behavior.")
        lines.append("")
        lines.append("     Policy actions:")
        lines.append("     • allow            - Allow the action")
        lines.append("     • deny             - Block the action")
        lines.append("     • require_approval - Require human approval")
        lines.append("     • warn             - Warn but allow")
        lines.append("     • log              - Log only")
        lines.append("")
        lines.append("     Key settings:")
        lines.append("     • default_action: action when no policy matches")
        lines.append("     • require_human_approval: global approval requirement")
        lines.append("     • max_concurrent_tasks: parallel execution limit")
        lines.append("")
        lines.append("  RECOMMENDED FIRST-RUN SETTINGS:")
        lines.append("     • require_human_approval: true")
        lines.append("     • default_action: require_approval")
        lines.append("     • max_concurrent_tasks: 1")
        lines.append("     • shell.require_approval: true")
        lines.append("")
        lines.append("  Use ConfigurationManager.create_defaults() to generate")
        lines.append("  safe default configuration files.")
        lines.append("")
        lines.append("╚════════════════════════════════════════════════════════════════╝")
        lines.append("")
        
        return "\n".join(lines)


# =============================================================================
# Token Management
# =============================================================================


@dataclass
class TokenConfig:
    """
    Configuration for an authentication token.
    
    NOTE: Actual token values should come from environment variables
    or a secure secret store. Never store tokens in configuration files.
    
    Attributes:
        token_id: Identifier for this token.
        token_type: Type of token (api_key, oauth, jwt, etc.).
        env_variable: Environment variable containing the token.
        service: Service this token is for.
        expires_at: When the token expires (if known).
        last_rotated: When the token was last rotated.
    """
    
    token_id: str
    token_type: str
    env_variable: str
    service: str
    expires_at: Optional[str] = None
    last_rotated: Optional[str] = None


class TokenManager:
    """
    Manages authentication tokens securely.
    
    RULES:
    - Never store tokens in configuration files
    - Always use environment variables for sensitive values
    - Rotate tokens regularly
    - Validate tokens before use
    """
    
    def __init__(self) -> None:
        """Initialize token manager."""
        self.tokens: Dict[str, TokenConfig] = {}
    
    def register_token(
        self,
        token_id: str,
        token_type: str,
        env_variable: str,
        service: str,
    ) -> None:
        """
        Register a token configuration.
        
        Args:
            token_id: Unique identifier.
            token_type: Type of token.
            env_variable: Environment variable name.
            service: Service this token is for.
        """
        self.tokens[token_id] = TokenConfig(
            token_id=token_id,
            token_type=token_type,
            env_variable=env_variable,
            service=service,
        )
    
    def get_token(self, token_id: str) -> Optional[str]:
        """
        Get a token value from environment.
        
        Args:
            token_id: Token identifier.
        
        Returns:
            Token value or None if not available.
        """
        config = self.tokens.get(token_id)
        if not config:
            return None
        
        return os.environ.get(config.env_variable)
    
    def validate_token(self, token_id: str) -> bool:
        """
        Check if a token is available.
        
        Args:
            token_id: Token identifier.
        
        Returns:
            True if token is available.
        """
        return self.get_token(token_id) is not None
    
    def get_missing_tokens(self) -> List[str]:
        """
        Get list of missing tokens.
        
        Returns:
            List of token IDs that are not available.
        """
        return [
            token_id
            for token_id in self.tokens
            if not self.validate_token(token_id)
        ]
    
    def get_token_guide(self) -> str:
        """
        Get guide for configuring tokens.
        
        Returns:
            Formatted token configuration guide.
        """
        lines = []
        lines.append("")
        lines.append("╔═══ TOKEN CONFIGURATION GUIDE ═════════════════════════════════╗")
        lines.append("")
        lines.append("  Axiom uses environment variables for authentication tokens.")
        lines.append("  Never store tokens in configuration files.")
        lines.append("")
        lines.append("  Required environment variables:")
        lines.append("")
        
        for token_id, config in self.tokens.items():
            status = "✓ Set" if self.validate_token(token_id) else "✗ Missing"
            lines.append(f"  {config.env_variable}")
            lines.append(f"    Service: {config.service}")
            lines.append(f"    Type: {config.token_type}")
            lines.append(f"    Status: {status}")
            lines.append("")
        
        missing = self.get_missing_tokens()
        if missing:
            lines.append("  ⚠ Missing tokens:")
            for token_id in missing:
                config = self.tokens[token_id]
                lines.append(f"    export {config.env_variable}=<your-token>")
            lines.append("")
        
        lines.append("  Token Rotation:")
        lines.append("    • Rotate tokens every 90 days minimum")
        lines.append("    • Update environment variables with new values")
        lines.append("    • Test with validate_token() after rotation")
        lines.append("")
        lines.append("╚════════════════════════════════════════════════════════════════╝")
        lines.append("")
        
        return "\n".join(lines)
