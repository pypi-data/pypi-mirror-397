"""
CLI Precondition Checking Module.

This module enforces workflow order in the CLI.

WORKFLOW ORDER (MANDATORY):
1. init/adopt (onboarding)
2. discover (optional)
3. plan
4. preview
5. approve
6. execute

The CLI MUST:
- Refuse execution before approval
- Refuse preview before planning
- Refuse planning before onboarding
- Refuse adoption if already initialized

Error messages MUST:
- Explain what step is missing
- Suggest the correct next command
"""

from dataclasses import dataclass
from typing import Optional, Callable, TypeVar, List
from functools import wraps

from axiom_cli.workflow_state import WorkflowState, WorkflowPhase, load_workflow_state
from axiom_cli.output import print_error, print_info


@dataclass(frozen=True)
class PreconditionError:
    """
    Error raised when a precondition is not met.
    
    Attributes:
        message: Human-readable error message.
        missing_step: The step that needs to be completed.
        suggested_command: The command to run next.
        current_phase: Current workflow phase.
    """
    
    message: str
    missing_step: str
    suggested_command: str
    current_phase: WorkflowPhase
    
    def display(self) -> None:
        """Display the error with helpful guidance."""
        print_error(self.message)
        print_info(f"Current phase: {self.current_phase.value}")
        print_info(f"Missing step: {self.missing_step}")
        print_info(f"Run: {self.suggested_command}")


class PreconditionChecker:
    """
    Checks preconditions for CLI commands.
    
    This class ensures commands are executed in the correct order.
    It does NOT make decisions - it only validates state.
    """
    
    def __init__(self, project_root: str = "."):
        """Initialize the precondition checker.
        
        Args:
            project_root: Path to project root.
        """
        self.project_root = project_root
        self._state: Optional[WorkflowState] = None
    
    @property
    def state(self) -> WorkflowState:
        """Get current workflow state (lazy loaded).
        
        Returns:
            Current workflow state.
        """
        if self._state is None:
            self._state = load_workflow_state(self.project_root)
        return self._state
    
    def refresh(self) -> None:
        """Refresh the workflow state from disk."""
        self._state = None
    
    def check_initialized(self) -> Optional[PreconditionError]:
        """Check if Axiom is initialized.
        
        Returns:
            PreconditionError if not initialized, None otherwise.
        """
        if not self.state.is_initialized():
            return PreconditionError(
                message="Axiom is not initialized in this project.",
                missing_step="Project initialization",
                suggested_command="axiom init  # for new projects\naxiom adopt  # for existing projects",
                current_phase=self.state.phase,
            )
        return None
    
    def check_not_initialized(self) -> Optional[PreconditionError]:
        """Check if Axiom is NOT initialized (for init/adopt).
        
        Returns:
            PreconditionError if already initialized, None otherwise.
        """
        if self.state.is_initialized():
            return PreconditionError(
                message="Axiom is already initialized in this project.",
                missing_step="None - project is already set up",
                suggested_command="axiom status  # to see current state\naxiom plan '<intent>'  # to create a plan",
                current_phase=self.state.phase,
            )
        return None
    
    def check_planned(self) -> Optional[PreconditionError]:
        """Check if a plan exists.
        
        Returns:
            PreconditionError if no plan, None otherwise.
        """
        # First check initialization
        init_error = self.check_initialized()
        if init_error:
            return init_error
        
        if not self.state.is_planned():
            return PreconditionError(
                message="No plan exists. You must create a plan before previewing.",
                missing_step="Planning",
                suggested_command="axiom plan '<your intent here>'",
                current_phase=self.state.phase,
            )
        return None
    
    def check_previewed(self) -> Optional[PreconditionError]:
        """Check if plan has been previewed.
        
        Returns:
            PreconditionError if not previewed, None otherwise.
        """
        # First check planning
        plan_error = self.check_planned()
        if plan_error:
            return plan_error
        
        if not self.state.is_previewed():
            return PreconditionError(
                message="Plan has not been previewed. You must preview before approving.",
                missing_step="Preview",
                suggested_command="axiom preview",
                current_phase=self.state.phase,
            )
        return None
    
    def check_approved(self) -> Optional[PreconditionError]:
        """Check if plan has been approved.
        
        Returns:
            PreconditionError if not approved, None otherwise.
        """
        # First check preview
        preview_error = self.check_previewed()
        if preview_error:
            return preview_error
        
        if not self.state.is_approved():
            return PreconditionError(
                message="Plan has not been approved. Human approval is REQUIRED before execution.",
                missing_step="Human Approval",
                suggested_command="axiom approve",
                current_phase=self.state.phase,
            )
        return None
    
    def check_discovered(self) -> Optional[PreconditionError]:
        """Check if discovery has been run.
        
        Returns:
            PreconditionError if not discovered, None otherwise.
        """
        # First check initialization
        init_error = self.check_initialized()
        if init_error:
            return init_error
        
        # Discovery is optional, so we just check if initialized
        return None
    
    def get_allowed_commands(self) -> List[str]:
        """Get list of commands allowed in current phase.
        
        Returns:
            List of allowed command names.
        """
        phase = self.state.phase
        
        # Always allowed
        allowed = ["status", "docs"]
        
        if phase == WorkflowPhase.UNINITIALIZED:
            allowed.extend(["init", "adopt"])
        elif phase == WorkflowPhase.INITIALIZED:
            allowed.extend(["plan", "discover"])
        elif phase == WorkflowPhase.DISCOVERED:
            allowed.extend(["plan", "discover"])
        elif phase == WorkflowPhase.PLANNED:
            allowed.extend(["preview", "plan"])
        elif phase == WorkflowPhase.PREVIEWED:
            allowed.extend(["approve", "plan"])
        elif phase == WorkflowPhase.APPROVED:
            allowed.extend(["execute", "plan"])
        elif phase == WorkflowPhase.EXECUTED:
            allowed.extend(["plan", "discover"])
        
        return allowed


# Decorator factory for precondition checks
T = TypeVar("T")


def require_initialized(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator that requires Axiom to be initialized.
    
    Args:
        func: The function to wrap.
        
    Returns:
        Wrapped function that checks initialization.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        project_root = kwargs.get("project_root", ".")
        checker = PreconditionChecker(project_root)
        error = checker.check_initialized()
        if error:
            error.display()
            raise SystemExit(1)
        return func(*args, **kwargs)
    return wrapper


def require_not_initialized(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator that requires Axiom to NOT be initialized.
    
    Args:
        func: The function to wrap.
        
    Returns:
        Wrapped function that checks non-initialization.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        project_root = kwargs.get("project_root", ".")
        checker = PreconditionChecker(project_root)
        error = checker.check_not_initialized()
        if error:
            error.display()
            raise SystemExit(1)
        return func(*args, **kwargs)
    return wrapper


def require_planned(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator that requires a plan to exist.
    
    Args:
        func: The function to wrap.
        
    Returns:
        Wrapped function that checks for plan.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        project_root = kwargs.get("project_root", ".")
        checker = PreconditionChecker(project_root)
        error = checker.check_planned()
        if error:
            error.display()
            raise SystemExit(1)
        return func(*args, **kwargs)
    return wrapper


def require_approved(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator that requires plan to be approved.
    
    Args:
        func: The function to wrap.
        
    Returns:
        Wrapped function that checks approval.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        project_root = kwargs.get("project_root", ".")
        checker = PreconditionChecker(project_root)
        error = checker.check_approved()
        if error:
            error.display()
            raise SystemExit(1)
        return func(*args, **kwargs)
    return wrapper


def require_discovered(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator that requires discovery to have been run.
    
    Args:
        func: The function to wrap.
        
    Returns:
        Wrapped function that checks discovery.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        project_root = kwargs.get("project_root", ".")
        checker = PreconditionChecker(project_root)
        error = checker.check_discovered()
        if error:
            error.display()
            raise SystemExit(1)
        return func(*args, **kwargs)
    return wrapper
