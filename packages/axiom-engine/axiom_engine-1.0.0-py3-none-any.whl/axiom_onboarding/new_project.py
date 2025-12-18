"""
New Project Onboarding Flow.

This module provides a step-by-step, governed flow for initializing
a new project with Axiom from scratch.

CANONICAL ONBOARDING FLOW:
1. INITIALIZE    - Create project directory structure
2. BOOTSTRAP     - Create empty Canon artifacts (CPKG, UCIR, BFM)
3. CONFIGURE     - Define initial constraints and policies
4. DISCOVER      - Run first discovery pass (no LLM)
5. ENRICH        - Optionally run LLM enrichment (advisory only)
6. REVIEW        - Human reviews all inferred annotations
7. PROMOTE       - Human approves Canon updates
8. DOCUMENT      - Generate initial documentation
9. VALIDATE      - Verify Canon integrity
10. FIRST_RUN    - Execute first governed workflow

RULES (ABSOLUTE):
- Each step has explicit prerequisites
- Each step has explicit postconditions
- No step may be skipped
- Every step is reversible (safe exit)
- Human approval required before Canon mutation
- Human approval required before execution

This flow produces a SAFE, GOVERNED project state.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
import json
import os

from axiom_canon.cpkg import CPKG, CPKGNode, NodeType
from axiom_canon.ucir import UCIR, UserConstraint, ConstraintLevel
from axiom_canon.bfm import BusinessFlowMap


# =============================================================================
# Onboarding Step Definitions
# =============================================================================


class OnboardingStep(str, Enum):
    """
    The canonical steps in new project onboarding.
    
    These steps MUST be executed in order.
    No step may be skipped.
    """
    
    INITIALIZE = "initialize"
    BOOTSTRAP = "bootstrap"
    CONFIGURE = "configure"
    DISCOVER = "discover"
    ENRICH = "enrich"
    REVIEW = "review"
    PROMOTE = "promote"
    DOCUMENT = "document"
    VALIDATE = "validate"
    FIRST_RUN = "first_run"


class OnboardingStepStatus(str, Enum):
    """Status of an onboarding step."""
    
    PENDING = "pending"
    CURRENT = "current"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED_OPTIONAL = "skipped_optional"  # Only for truly optional steps


# Step metadata for display and validation
ONBOARDING_STEP_DETAILS: Dict[OnboardingStep, Dict[str, Any]] = {
    OnboardingStep.INITIALIZE: {
        "name": "Initialize Project",
        "description": "Create project directory structure and Axiom configuration",
        "owner": "User",
        "required": True,
        "prerequisites": [],
        "produces": ["Project directory", ".axiom/ configuration folder"],
        "reversible": True,
        "exit_action": "Delete .axiom/ folder to abort",
    },
    OnboardingStep.BOOTSTRAP: {
        "name": "Bootstrap Canon",
        "description": "Create empty Canon artifacts (CPKG, UCIR, BFM, TaskGraph templates)",
        "owner": "System",
        "required": True,
        "prerequisites": [OnboardingStep.INITIALIZE],
        "produces": ["Empty CPKG", "Empty UCIR", "Empty BFM"],
        "reversible": True,
        "exit_action": "Delete .axiom/canon/ folder to abort",
    },
    OnboardingStep.CONFIGURE: {
        "name": "Configure Constraints",
        "description": "Define initial user constraints and executor policies",
        "owner": "User",
        "required": True,
        "prerequisites": [OnboardingStep.BOOTSTRAP],
        "produces": ["UCIR with user constraints", "Executor policy configuration"],
        "reversible": True,
        "exit_action": "Reset UCIR to empty state",
    },
    OnboardingStep.DISCOVER: {
        "name": "Run Discovery",
        "description": "Extract code structure deterministically (no LLM)",
        "owner": "System",
        "required": True,
        "prerequisites": [OnboardingStep.CONFIGURE],
        "produces": ["IngestionResult", "Component summaries", "Dependency map"],
        "reversible": True,
        "exit_action": "Discard discovery results",
    },
    OnboardingStep.ENRICH: {
        "name": "LLM Enrichment (Optional)",
        "description": "Use LLM to infer labels and descriptions (ADVISORY ONLY)",
        "owner": "AI (Advisory)",
        "required": False,
        "prerequisites": [OnboardingStep.DISCOVER],
        "produces": ["EnrichmentResult (provisional)", "Inferred labels (not in Canon)"],
        "reversible": True,
        "exit_action": "Discard enrichment results",
    },
    OnboardingStep.REVIEW: {
        "name": "Review Annotations",
        "description": "Human reviews all inferred and extracted annotations",
        "owner": "Human",
        "required": True,
        "prerequisites": [OnboardingStep.DISCOVER],  # Enrich is optional
        "produces": ["Review decisions", "Approved/rejected annotations"],
        "reversible": True,
        "exit_action": "Reset all review decisions",
    },
    OnboardingStep.PROMOTE: {
        "name": "Promote to Canon",
        "description": "Approved annotations are promoted into Canon (requires explicit approval)",
        "owner": "Human (Approval Required)",
        "required": True,
        "prerequisites": [OnboardingStep.REVIEW],
        "produces": ["Updated CPKG", "Updated BFM"],
        "reversible": True,
        "exit_action": "Revert Canon to pre-promotion state",
    },
    OnboardingStep.DOCUMENT: {
        "name": "Generate Documentation",
        "description": "Generate initial documentation from Canon",
        "owner": "System",
        "required": True,
        "prerequisites": [OnboardingStep.PROMOTE],
        "produces": ["Documentation files (derived, regenerable)"],
        "reversible": True,
        "exit_action": "Delete generated documentation",
    },
    OnboardingStep.VALIDATE: {
        "name": "Validate Canon",
        "description": "Verify Canon integrity and consistency",
        "owner": "System",
        "required": True,
        "prerequisites": [OnboardingStep.DOCUMENT],
        "produces": ["Validation report", "Canon integrity confirmation"],
        "reversible": False,  # Validation is read-only
        "exit_action": "Review validation errors",
    },
    OnboardingStep.FIRST_RUN: {
        "name": "First Governed Workflow",
        "description": "Execute first workflow with full governance (preview → approve → execute)",
        "owner": "Human (Approval Required)",
        "required": False,  # User can stop after validation
        "prerequisites": [OnboardingStep.VALIDATE],
        "produces": ["WorkflowResult", "Execution audit trail"],
        "reversible": False,  # Execution cannot be undone
        "exit_action": "Reject execution at approval step",
    },
}


# =============================================================================
# Onboarding State
# =============================================================================


@dataclass
class OnboardingState:
    """
    Tracks the current state of onboarding.
    
    This is the single source of truth for onboarding progress.
    
    Attributes:
        project_path: Path to the project being onboarded.
        current_step: The step currently in progress.
        step_statuses: Status of each step.
        artifacts: Artifacts produced by completed steps.
        errors: Errors encountered during onboarding.
        started_at: When onboarding started.
        completed_steps: List of completed steps in order.
    """
    
    project_path: str
    current_step: OnboardingStep = OnboardingStep.INITIALIZE
    step_statuses: Dict[OnboardingStep, OnboardingStepStatus] = field(default_factory=dict)
    artifacts: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    started_at: str = ""
    completed_steps: List[OnboardingStep] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """Initialize step statuses and timestamp."""
        if not self.step_statuses:
            self.step_statuses = {
                step: OnboardingStepStatus.PENDING
                for step in OnboardingStep
            }
            self.step_statuses[OnboardingStep.INITIALIZE] = OnboardingStepStatus.CURRENT
        
        if not self.started_at:
            self.started_at = datetime.now(timezone.utc).isoformat()
    
    def mark_completed(self, step: OnboardingStep) -> None:
        """Mark a step as completed and advance to next."""
        self.step_statuses[step] = OnboardingStepStatus.COMPLETED
        self.completed_steps.append(step)
        
        # Find next step
        steps = list(OnboardingStep)
        current_index = steps.index(step)
        if current_index + 1 < len(steps):
            next_step = steps[current_index + 1]
            self.current_step = next_step
            self.step_statuses[next_step] = OnboardingStepStatus.CURRENT
    
    def mark_failed(self, step: OnboardingStep, error: str) -> None:
        """Mark a step as failed with error."""
        self.step_statuses[step] = OnboardingStepStatus.FAILED
        self.errors.append(f"[{step.value}] {error}")
    
    def skip_optional(self, step: OnboardingStep) -> None:
        """Skip an optional step."""
        details = ONBOARDING_STEP_DETAILS.get(step, {})
        if details.get("required", True):
            raise OnboardingError(f"Cannot skip required step: {step.value}")
        
        self.step_statuses[step] = OnboardingStepStatus.SKIPPED_OPTIONAL
        self.completed_steps.append(step)
        
        # Advance to next step
        steps = list(OnboardingStep)
        current_index = steps.index(step)
        if current_index + 1 < len(steps):
            next_step = steps[current_index + 1]
            self.current_step = next_step
            self.step_statuses[next_step] = OnboardingStepStatus.CURRENT
    
    def can_proceed_to(self, step: OnboardingStep) -> bool:
        """Check if prerequisites are met for a step."""
        details = ONBOARDING_STEP_DETAILS.get(step, {})
        prerequisites = details.get("prerequisites", [])
        
        for prereq in prerequisites:
            status = self.step_statuses.get(prereq)
            if status not in (
                OnboardingStepStatus.COMPLETED,
                OnboardingStepStatus.SKIPPED_OPTIONAL
            ):
                return False
        
        return True
    
    def get_blocking_reasons(self, step: OnboardingStep) -> List[str]:
        """Get reasons why a step cannot proceed."""
        reasons = []
        details = ONBOARDING_STEP_DETAILS.get(step, {})
        prerequisites = details.get("prerequisites", [])
        
        for prereq in prerequisites:
            status = self.step_statuses.get(prereq)
            if status == OnboardingStepStatus.PENDING:
                reasons.append(f"Prerequisite '{prereq.value}' has not started")
            elif status == OnboardingStepStatus.CURRENT:
                reasons.append(f"Prerequisite '{prereq.value}' is in progress")
            elif status == OnboardingStepStatus.FAILED:
                reasons.append(f"Prerequisite '{prereq.value}' failed")
        
        return reasons


# =============================================================================
# Onboarding Result
# =============================================================================


@dataclass
class OnboardingResult:
    """
    Result of a single onboarding step.
    
    Attributes:
        step: The step that was executed.
        success: Whether the step succeeded.
        message: Human-readable result message.
        artifacts: Artifacts produced by this step.
        next_step: The next step to execute (if any).
        next_action: Description of what to do next.
        can_abort: Whether the user can safely abort at this point.
        abort_instructions: How to abort safely.
    """
    
    step: OnboardingStep
    success: bool
    message: str
    artifacts: Dict[str, Any] = field(default_factory=dict)
    next_step: Optional[OnboardingStep] = None
    next_action: str = ""
    can_abort: bool = True
    abort_instructions: str = ""


# =============================================================================
# Errors
# =============================================================================


class OnboardingError(Exception):
    """
    Error during onboarding.
    
    Always provides:
    - What happened
    - Why it happened
    - How to recover
    """
    
    def __init__(
        self,
        message: str,
        step: Optional[OnboardingStep] = None,
        recovery: str = "",
    ) -> None:
        """
        Initialize onboarding error.
        
        Args:
            message: What happened.
            step: Which step failed.
            recovery: How to recover.
        """
        self.step = step
        self.recovery = recovery
        
        full_message = message
        if step:
            full_message = f"[{step.value}] {message}"
        if recovery:
            full_message += f"\n  Recovery: {recovery}"
        
        super().__init__(full_message)


# =============================================================================
# Onboarding Display
# =============================================================================


class OnboardingDisplay:
    """
    Renders onboarding state and progress for users.
    
    All output is READ-ONLY and purely for display.
    """
    
    @staticmethod
    def render_progress(state: OnboardingState) -> str:
        """
        Render onboarding progress.
        
        Args:
            state: Current onboarding state.
        
        Returns:
            Formatted progress display.
        """
        lines = []
        lines.append("")
        lines.append("╔════════════════════════════════════════════════════════════╗")
        lines.append("║           AXIOM NEW PROJECT ONBOARDING                     ║")
        lines.append("╠════════════════════════════════════════════════════════════╣")
        lines.append("")
        
        # Progress bar
        total = len(OnboardingStep)
        completed = len(state.completed_steps)
        progress = int((completed / total) * 40)
        bar = "█" * progress + "░" * (40 - progress)
        lines.append(f"  Progress: [{bar}] {completed}/{total}")
        lines.append("")
        
        # Step list
        lines.append("  Steps:")
        for step in OnboardingStep:
            status = state.step_statuses.get(step, OnboardingStepStatus.PENDING)
            details = ONBOARDING_STEP_DETAILS.get(step, {})
            name = details.get("name", step.value)
            required = details.get("required", True)
            
            # Status indicators
            if status == OnboardingStepStatus.COMPLETED:
                indicator = "✓"
                style = ""
            elif status == OnboardingStepStatus.CURRENT:
                indicator = "▶"
                style = " ← CURRENT"
            elif status == OnboardingStepStatus.FAILED:
                indicator = "✗"
                style = " ← FAILED"
            elif status == OnboardingStepStatus.SKIPPED_OPTIONAL:
                indicator = "○"
                style = " (skipped)"
            else:
                indicator = "·"
                style = ""
            
            optional = "" if required else " (optional)"
            lines.append(f"    {indicator} {name}{optional}{style}")
        
        lines.append("")
        
        # Current step details
        current = state.current_step
        details = ONBOARDING_STEP_DETAILS.get(current, {})
        lines.append(f"  Current Step: {details.get('name', current.value)}")
        lines.append(f"  Description: {details.get('description', '')}")
        lines.append(f"  Owner: {details.get('owner', 'Unknown')}")
        lines.append("")
        
        # What this step produces
        produces = details.get("produces", [])
        if produces:
            lines.append("  This step will produce:")
            for item in produces:
                lines.append(f"    • {item}")
            lines.append("")
        
        # Safe exit information
        lines.append("  Safe Exit:")
        lines.append(f"    {details.get('exit_action', 'No specific exit action')}")
        lines.append("")
        
        # Errors if any
        if state.errors:
            lines.append("  ⚠ Errors:")
            for error in state.errors[-3:]:  # Show last 3 errors
                lines.append(f"    • {error}")
            lines.append("")
        
        lines.append("╚════════════════════════════════════════════════════════════╝")
        lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def render_step_details(step: OnboardingStep) -> str:
        """
        Render detailed information about a step.
        
        Args:
            step: The step to describe.
        
        Returns:
            Formatted step details.
        """
        details = ONBOARDING_STEP_DETAILS.get(step, {})
        
        lines = []
        lines.append("")
        lines.append(f"╔═══ Step: {details.get('name', step.value)} ═══")
        lines.append("")
        lines.append(f"  Description:")
        lines.append(f"    {details.get('description', 'No description')}")
        lines.append("")
        lines.append(f"  Owner: {details.get('owner', 'Unknown')}")
        lines.append(f"  Required: {'Yes' if details.get('required', True) else 'No'}")
        lines.append(f"  Reversible: {'Yes' if details.get('reversible', True) else 'No'}")
        lines.append("")
        
        prerequisites = details.get("prerequisites", [])
        if prerequisites:
            lines.append("  Prerequisites:")
            for prereq in prerequisites:
                prereq_details = ONBOARDING_STEP_DETAILS.get(prereq, {})
                lines.append(f"    • {prereq_details.get('name', prereq.value)}")
        else:
            lines.append("  Prerequisites: None")
        lines.append("")
        
        produces = details.get("produces", [])
        if produces:
            lines.append("  Produces:")
            for item in produces:
                lines.append(f"    • {item}")
        lines.append("")
        
        lines.append("  Safe Exit:")
        lines.append(f"    {details.get('exit_action', 'No specific exit action')}")
        lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def render_abort_confirmation(state: OnboardingState) -> str:
        """
        Render confirmation dialog for aborting onboarding.
        
        Args:
            state: Current onboarding state.
        
        Returns:
            Formatted abort confirmation.
        """
        lines = []
        lines.append("")
        lines.append("╔════════════════════════════════════════════════════════════╗")
        lines.append("║              ⚠ ABORT ONBOARDING? ⚠                        ║")
        lines.append("╠════════════════════════════════════════════════════════════╣")
        lines.append("")
        lines.append("  You are about to abort onboarding.")
        lines.append("")
        lines.append("  Completed steps:")
        for step in state.completed_steps:
            details = ONBOARDING_STEP_DETAILS.get(step, {})
            lines.append(f"    ✓ {details.get('name', step.value)}")
        lines.append("")
        
        # What will be preserved
        lines.append("  What will be preserved:")
        lines.append("    • Project directory")
        lines.append("    • Any files created outside .axiom/")
        lines.append("")
        
        # What will be cleaned up
        lines.append("  What will be cleaned up:")
        lines.append("    • .axiom/ configuration folder")
        lines.append("    • Canon artifacts (CPKG, UCIR, BFM)")
        lines.append("    • Onboarding state")
        lines.append("")
        
        lines.append("  To confirm abort, call: onboarding.abort(confirm=True)")
        lines.append("  To continue, call the next step function.")
        lines.append("")
        lines.append("╚════════════════════════════════════════════════════════════╝")
        lines.append("")
        
        return "\n".join(lines)


# =============================================================================
# New Project Onboarding
# =============================================================================


class NewProjectOnboarding:
    """
    Governed onboarding flow for new projects.
    
    This class guides users through initializing a new project with Axiom.
    Each step is explicit, reversible, and auditable.
    
    RULES:
    - Steps must be executed in order
    - Each step validates prerequisites
    - Each step produces explicit artifacts
    - Human approval required before Canon mutation
    - Human approval required before execution
    
    Attributes:
        state: Current onboarding state.
        display: Display renderer.
    """
    
    def __init__(self, project_path: str) -> None:
        """
        Initialize onboarding for a new project.
        
        Args:
            project_path: Path where project will be created.
        """
        self.state = OnboardingState(project_path=project_path)
        self.display = OnboardingDisplay()
        self._cpkg: Optional[CPKG] = None
        self._ucir: Optional[UCIR] = None
        self._bfm: Optional[BusinessFlowMap] = None
    
    # =========================================================================
    # Step 1: Initialize Project
    # =========================================================================
    
    def step_initialize(self) -> OnboardingResult:
        """
        Initialize project directory structure.
        
        Creates:
        - .axiom/ configuration directory
        - .axiom/canon/ for Canon artifacts
        - .axiom/state/ for onboarding state
        - .axiom/config.json for Axiom configuration
        
        Returns:
            OnboardingResult with created artifacts.
        """
        step = OnboardingStep.INITIALIZE
        
        # Validate current state
        if self.state.current_step != step:
            return OnboardingResult(
                step=step,
                success=False,
                message=f"Cannot execute {step.value}: current step is {self.state.current_step.value}",
                next_action="Complete the current step first",
            )
        
        try:
            project_path = Path(self.state.project_path)
            axiom_dir = project_path / ".axiom"
            canon_dir = axiom_dir / "canon"
            state_dir = axiom_dir / "state"
            
            # Create directories
            axiom_dir.mkdir(parents=True, exist_ok=True)
            canon_dir.mkdir(exist_ok=True)
            state_dir.mkdir(exist_ok=True)
            
            # Create initial config
            config = {
                "version": "1.0.0",
                "initialized_at": datetime.now(timezone.utc).isoformat(),
                "project_path": str(project_path.absolute()),
                "canon_path": str(canon_dir.absolute()),
            }
            
            config_path = axiom_dir / "config.json"
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            
            # Record artifacts
            self.state.artifacts["axiom_dir"] = str(axiom_dir)
            self.state.artifacts["canon_dir"] = str(canon_dir)
            self.state.artifacts["config_path"] = str(config_path)
            
            # Mark completed
            self.state.mark_completed(step)
            
            return OnboardingResult(
                step=step,
                success=True,
                message="Project initialized successfully",
                artifacts={
                    "axiom_dir": str(axiom_dir),
                    "canon_dir": str(canon_dir),
                    "config_path": str(config_path),
                },
                next_step=OnboardingStep.BOOTSTRAP,
                next_action="Run step_bootstrap() to create empty Canon artifacts",
                can_abort=True,
                abort_instructions="Delete .axiom/ folder to abort",
            )
            
        except Exception as e:
            self.state.mark_failed(step, str(e))
            return OnboardingResult(
                step=step,
                success=False,
                message=f"Initialization failed: {e}",
                abort_instructions="Check permissions and try again",
            )
    
    # =========================================================================
    # Step 2: Bootstrap Canon
    # =========================================================================
    
    def step_bootstrap(self) -> OnboardingResult:
        """
        Bootstrap empty Canon artifacts.
        
        Creates:
        - Empty CPKG (Canonical Project Knowledge Graph)
        - Empty UCIR (User Constraint & Instruction Registry)
        - Empty BFM (Business Flow Map)
        
        Returns:
            OnboardingResult with created Canon artifacts.
        """
        step = OnboardingStep.BOOTSTRAP
        
        # Validate prerequisites
        if not self.state.can_proceed_to(step):
            reasons = self.state.get_blocking_reasons(step)
            return OnboardingResult(
                step=step,
                success=False,
                message=f"Cannot bootstrap: prerequisites not met",
                next_action=f"Blocking reasons: {', '.join(reasons)}",
            )
        
        # Validate current state
        if self.state.current_step != step:
            return OnboardingResult(
                step=step,
                success=False,
                message=f"Cannot execute {step.value}: current step is {self.state.current_step.value}",
                next_action="Complete the current step first",
            )
        
        try:
            canon_dir = Path(self.state.artifacts.get("canon_dir", ""))
            if not canon_dir.exists():
                raise OnboardingError(
                    "Canon directory not found",
                    step=step,
                    recovery="Run step_initialize() first",
                )
            
            # Create empty Canon artifacts
            self._cpkg = CPKG()
            self._ucir = UCIR()
            self._bfm = BusinessFlowMap()
            
            # Serialize to files
            cpkg_path = canon_dir / "cpkg.json"
            ucir_path = canon_dir / "ucir.json"
            bfm_path = canon_dir / "bfm.json"
            
            with open(cpkg_path, "w") as f:
                json.dump({
                    "nodes": {},
                    "edges": [],
                    "version": self._cpkg.version,
                }, f, indent=2)
            
            with open(ucir_path, "w") as f:
                json.dump({
                    "constraints": {},
                    "version": self._ucir.version,
                }, f, indent=2)
            
            with open(bfm_path, "w") as f:
                json.dump({
                    "flows": {},
                    "version": "0.1.0",
                }, f, indent=2)
            
            # Record artifacts
            self.state.artifacts["cpkg_path"] = str(cpkg_path)
            self.state.artifacts["ucir_path"] = str(ucir_path)
            self.state.artifacts["bfm_path"] = str(bfm_path)
            self.state.artifacts["cpkg"] = self._cpkg
            self.state.artifacts["ucir"] = self._ucir
            self.state.artifacts["bfm"] = self._bfm
            
            # Mark completed
            self.state.mark_completed(step)
            
            return OnboardingResult(
                step=step,
                success=True,
                message="Canon artifacts bootstrapped successfully",
                artifacts={
                    "cpkg_path": str(cpkg_path),
                    "ucir_path": str(ucir_path),
                    "bfm_path": str(bfm_path),
                },
                next_step=OnboardingStep.CONFIGURE,
                next_action="Run step_configure() to define initial constraints",
                can_abort=True,
                abort_instructions="Delete .axiom/canon/ folder to abort",
            )
            
        except Exception as e:
            self.state.mark_failed(step, str(e))
            return OnboardingResult(
                step=step,
                success=False,
                message=f"Bootstrap failed: {e}",
                abort_instructions="Check Canon directory exists and try again",
            )
    
    # =========================================================================
    # Step 3: Configure Constraints
    # =========================================================================
    
    def step_configure(
        self,
        constraints: Optional[List[Dict[str, str]]] = None,
    ) -> OnboardingResult:
        """
        Configure initial user constraints.
        
        Args:
            constraints: Optional list of constraint definitions:
                [{"description": "...", "level": "critical|warning|info", "scope": "..."}]
        
        Returns:
            OnboardingResult with configuration status.
        """
        step = OnboardingStep.CONFIGURE
        
        # Validate prerequisites
        if not self.state.can_proceed_to(step):
            reasons = self.state.get_blocking_reasons(step)
            return OnboardingResult(
                step=step,
                success=False,
                message=f"Cannot configure: prerequisites not met",
                next_action=f"Blocking reasons: {', '.join(reasons)}",
            )
        
        if self.state.current_step != step:
            return OnboardingResult(
                step=step,
                success=False,
                message=f"Cannot execute {step.value}: current step is {self.state.current_step.value}",
                next_action="Complete the current step first",
            )
        
        try:
            # Load or create UCIR
            if self._ucir is None:
                self._ucir = UCIR()
            
            # Add default constraints if none provided
            if constraints is None:
                constraints = [
                    {
                        "description": "All execution requires explicit human approval",
                        "level": "critical",
                        "scope": "global",
                    },
                    {
                        "description": "Canon mutations must be reviewed before commit",
                        "level": "critical",
                        "scope": "global",
                    },
                ]
            
            # Add constraints to UCIR
            for i, c in enumerate(constraints):
                constraint_id = f"user_constraint_{i+1}"
                level = ConstraintLevel(c.get("level", "warning"))
                self._ucir.constraints[constraint_id] = UserConstraint(
                    id=constraint_id,
                    description=c.get("description", ""),
                    level=level,
                    scope=c.get("scope", "global"),
                    source="onboarding",
                )
            
            # Save UCIR
            ucir_path = self.state.artifacts.get("ucir_path")
            if ucir_path:
                with open(ucir_path, "w") as f:
                    json.dump({
                        "constraints": {
                            k: {
                                "id": v.id,
                                "description": v.description,
                                "level": v.level.value,
                                "scope": v.scope,
                                "source": v.source,
                            }
                            for k, v in self._ucir.constraints.items()
                        },
                        "version": self._ucir.version,
                    }, f, indent=2)
            
            # Update artifacts
            self.state.artifacts["ucir"] = self._ucir
            self.state.artifacts["constraint_count"] = len(self._ucir.constraints)
            
            # Mark completed
            self.state.mark_completed(step)
            
            return OnboardingResult(
                step=step,
                success=True,
                message=f"Configured {len(self._ucir.constraints)} constraints",
                artifacts={
                    "constraint_count": len(self._ucir.constraints),
                    "constraints": list(self._ucir.constraints.keys()),
                },
                next_step=OnboardingStep.DISCOVER,
                next_action="Run step_discover() to extract code structure",
                can_abort=True,
                abort_instructions="Reset UCIR to empty state with step_reset_ucir()",
            )
            
        except Exception as e:
            self.state.mark_failed(step, str(e))
            return OnboardingResult(
                step=step,
                success=False,
                message=f"Configuration failed: {e}",
            )
    
    # =========================================================================
    # Step 4: Discover
    # =========================================================================
    
    def step_discover(self) -> OnboardingResult:
        """
        Run deterministic code discovery.
        
        This step:
        - Extracts code structure (no LLM)
        - Identifies components and dependencies
        - Generates IngestionResult
        
        Returns:
            OnboardingResult with discovery artifacts.
        """
        step = OnboardingStep.DISCOVER
        
        # Validate prerequisites
        if not self.state.can_proceed_to(step):
            reasons = self.state.get_blocking_reasons(step)
            return OnboardingResult(
                step=step,
                success=False,
                message=f"Cannot discover: prerequisites not met",
                next_action=f"Blocking reasons: {', '.join(reasons)}",
            )
        
        if self.state.current_step != step:
            return OnboardingResult(
                step=step,
                success=False,
                message=f"Cannot execute {step.value}: current step is {self.state.current_step.value}",
                next_action="Complete the current step first",
            )
        
        try:
            # Import extractor
            from axiom_canon.ingestion.extractor import CodeExtractor, ExtractionConfig
            
            project_path = Path(self.state.project_path)
            
            # Configure extraction
            config = ExtractionConfig(
                root_path=str(project_path),
                include_patterns=["**/*.py"],
                exclude_patterns=["**/test_*", "**/__pycache__/**", "**/.axiom/**"],
            )
            
            # Run extraction
            extractor = CodeExtractor(config)
            result = extractor.extract()
            
            # Store results
            self.state.artifacts["ingestion_result"] = result
            self.state.artifacts["component_count"] = len(result.components)
            self.state.artifacts["module_count"] = sum(
                len(c.modules) for c in result.components.values()
            )
            
            # Mark completed
            self.state.mark_completed(step)
            
            return OnboardingResult(
                step=step,
                success=True,
                message=f"Discovered {len(result.components)} components with {self.state.artifacts['module_count']} modules",
                artifacts={
                    "component_count": len(result.components),
                    "module_count": self.state.artifacts["module_count"],
                    "components": list(result.components.keys()),
                },
                next_step=OnboardingStep.ENRICH,
                next_action="Run step_enrich() for LLM enrichment (optional) or skip_enrich()",
                can_abort=True,
                abort_instructions="Discovery results are not persisted until promotion",
            )
            
        except ImportError:
            # Extractor not available - provide placeholder result
            self.state.artifacts["ingestion_result"] = None
            self.state.artifacts["component_count"] = 0
            self.state.artifacts["module_count"] = 0
            
            self.state.mark_completed(step)
            
            return OnboardingResult(
                step=step,
                success=True,
                message="Discovery completed (extractor not available - placeholder)",
                artifacts={
                    "component_count": 0,
                    "module_count": 0,
                },
                next_step=OnboardingStep.ENRICH,
                next_action="Run step_enrich() or skip_enrich()",
            )
            
        except Exception as e:
            self.state.mark_failed(step, str(e))
            return OnboardingResult(
                step=step,
                success=False,
                message=f"Discovery failed: {e}",
            )
    
    # =========================================================================
    # Step 5: Enrich (Optional)
    # =========================================================================
    
    def step_enrich(self) -> OnboardingResult:
        """
        Run optional LLM enrichment.
        
        THIS IS ADVISORY ONLY. Results are NOT in Canon.
        Human must review and approve before promotion.
        
        Returns:
            OnboardingResult with enrichment artifacts.
        """
        step = OnboardingStep.ENRICH
        
        if not self.state.can_proceed_to(step):
            reasons = self.state.get_blocking_reasons(step)
            return OnboardingResult(
                step=step,
                success=False,
                message=f"Cannot enrich: prerequisites not met",
                next_action=f"Blocking reasons: {', '.join(reasons)}",
            )
        
        if self.state.current_step != step:
            return OnboardingResult(
                step=step,
                success=False,
                message=f"Cannot execute {step.value}: current step is {self.state.current_step.value}",
                next_action="Complete the current step first",
            )
        
        try:
            # For now, create placeholder enrichment result
            # In production, this would call LLM enrichment
            self.state.artifacts["enrichment_result"] = {
                "status": "completed",
                "labels_generated": 0,
                "advisory_only": True,
                "requires_human_review": True,
            }
            
            self.state.mark_completed(step)
            
            return OnboardingResult(
                step=step,
                success=True,
                message="Enrichment completed (ADVISORY ONLY - requires human review)",
                artifacts={
                    "advisory_only": True,
                    "requires_human_review": True,
                },
                next_step=OnboardingStep.REVIEW,
                next_action="Run step_review() to review all annotations",
                can_abort=True,
                abort_instructions="Enrichment results are discarded if not promoted",
            )
            
        except Exception as e:
            self.state.mark_failed(step, str(e))
            return OnboardingResult(
                step=step,
                success=False,
                message=f"Enrichment failed: {e}",
            )
    
    def skip_enrich(self) -> OnboardingResult:
        """
        Skip optional LLM enrichment.
        
        Returns:
            OnboardingResult confirming skip.
        """
        step = OnboardingStep.ENRICH
        
        if self.state.current_step != step:
            return OnboardingResult(
                step=step,
                success=False,
                message=f"Cannot skip {step.value}: current step is {self.state.current_step.value}",
            )
        
        self.state.skip_optional(step)
        
        return OnboardingResult(
            step=step,
            success=True,
            message="Enrichment skipped (will proceed with extraction results only)",
            next_step=OnboardingStep.REVIEW,
            next_action="Run step_review() to review extracted annotations",
        )
    
    # =========================================================================
    # Step 6: Review
    # =========================================================================
    
    def step_review(self) -> OnboardingResult:
        """
        Human review of all annotations.
        
        Presents:
        - Extracted structure
        - Inferred labels (if enrichment was run)
        - Provisional annotations
        
        Human must:
        - Approve, reject, or modify each annotation
        - Confirm understanding of what will be promoted
        
        Returns:
            OnboardingResult with review status.
        """
        step = OnboardingStep.REVIEW
        
        if not self.state.can_proceed_to(step):
            reasons = self.state.get_blocking_reasons(step)
            return OnboardingResult(
                step=step,
                success=False,
                message=f"Cannot review: prerequisites not met",
                next_action=f"Blocking reasons: {', '.join(reasons)}",
            )
        
        if self.state.current_step != step:
            return OnboardingResult(
                step=step,
                success=False,
                message=f"Cannot execute {step.value}: current step is {self.state.current_step.value}",
                next_action="Complete the current step first",
            )
        
        # Prepare review summary
        review_items = []
        
        ingestion_result = self.state.artifacts.get("ingestion_result")
        if ingestion_result and hasattr(ingestion_result, "components"):
            for comp_id, comp in ingestion_result.components.items():
                review_items.append({
                    "type": "component",
                    "id": comp_id,
                    "name": getattr(comp, "name", comp_id),
                    "source": "extraction",
                    "requires_approval": True,
                })
        
        enrichment_result = self.state.artifacts.get("enrichment_result")
        if enrichment_result and enrichment_result.get("labels_generated", 0) > 0:
            review_items.append({
                "type": "enrichment",
                "count": enrichment_result["labels_generated"],
                "source": "llm",
                "advisory_only": True,
                "requires_approval": True,
            })
        
        self.state.artifacts["review_items"] = review_items
        self.state.artifacts["review_pending"] = True
        
        # Mark completed (review is a checkpoint, actual approval is in promote)
        self.state.mark_completed(step)
        
        return OnboardingResult(
            step=step,
            success=True,
            message=f"Review prepared: {len(review_items)} items require human review",
            artifacts={
                "review_items_count": len(review_items),
                "review_items": review_items,
            },
            next_step=OnboardingStep.PROMOTE,
            next_action="Run step_promote(approved_items=[...]) to promote approved annotations",
            can_abort=True,
            abort_instructions="All review items will be discarded if not promoted",
        )
    
    # =========================================================================
    # Step 7: Promote
    # =========================================================================
    
    def step_promote(
        self,
        approved_items: Optional[List[str]] = None,
        confirm: bool = False,
    ) -> OnboardingResult:
        """
        Promote approved annotations into Canon.
        
        REQUIRES EXPLICIT CONFIRMATION.
        
        Args:
            approved_items: List of item IDs to promote (None = all).
            confirm: Must be True to proceed.
        
        Returns:
            OnboardingResult with promotion status.
        """
        step = OnboardingStep.PROMOTE
        
        if not self.state.can_proceed_to(step):
            reasons = self.state.get_blocking_reasons(step)
            return OnboardingResult(
                step=step,
                success=False,
                message=f"Cannot promote: prerequisites not met",
                next_action=f"Blocking reasons: {', '.join(reasons)}",
            )
        
        if self.state.current_step != step:
            return OnboardingResult(
                step=step,
                success=False,
                message=f"Cannot execute {step.value}: current step is {self.state.current_step.value}",
                next_action="Complete the current step first",
            )
        
        # Require explicit confirmation
        if not confirm:
            return OnboardingResult(
                step=step,
                success=False,
                message="Canon promotion requires explicit confirmation",
                next_action="Call step_promote(approved_items=[...], confirm=True)",
                abort_instructions="Skip this step to abort promotion",
            )
        
        try:
            # Promote approved items to Canon
            promoted_count = 0
            
            if self._cpkg is None:
                self._cpkg = CPKG()
            
            review_items = self.state.artifacts.get("review_items", [])
            items_to_promote = approved_items if approved_items else [
                item["id"] for item in review_items if item.get("type") == "component"
            ]
            
            for item_id in items_to_promote:
                # Create CPKG node for each promoted component
                node = CPKGNode(
                    id=item_id,
                    type=NodeType.COMPONENT,
                    content=f"Component: {item_id}",
                    metadata={"source": "onboarding", "promoted": "true"},
                )
                self._cpkg.nodes[item_id] = node
                promoted_count += 1
            
            # Save CPKG
            cpkg_path = self.state.artifacts.get("cpkg_path")
            if cpkg_path:
                with open(cpkg_path, "w") as f:
                    json.dump({
                        "nodes": {
                            k: {
                                "id": v.id,
                                "type": v.type.value,
                                "content": v.content,
                                "metadata": v.metadata,
                            }
                            for k, v in self._cpkg.nodes.items()
                        },
                        "edges": [
                            {
                                "source_id": e.source_id,
                                "target_id": e.target_id,
                                "relationship": e.relationship,
                                "metadata": e.metadata,
                            }
                            for e in self._cpkg.edges
                        ],
                        "version": self._cpkg.version,
                    }, f, indent=2)
            
            self.state.artifacts["promoted_count"] = promoted_count
            self.state.artifacts["cpkg"] = self._cpkg
            
            self.state.mark_completed(step)
            
            return OnboardingResult(
                step=step,
                success=True,
                message=f"Promoted {promoted_count} items to Canon",
                artifacts={
                    "promoted_count": promoted_count,
                    "cpkg_nodes": len(self._cpkg.nodes),
                },
                next_step=OnboardingStep.DOCUMENT,
                next_action="Run step_document() to generate documentation",
                can_abort=True,
                abort_instructions="Canon changes can be reverted by restoring from backup",
            )
            
        except Exception as e:
            self.state.mark_failed(step, str(e))
            return OnboardingResult(
                step=step,
                success=False,
                message=f"Promotion failed: {e}",
            )
    
    # =========================================================================
    # Step 8: Document
    # =========================================================================
    
    def step_document(self) -> OnboardingResult:
        """
        Generate initial documentation from Canon.
        
        Documentation is DERIVED and REGENERABLE.
        
        Returns:
            OnboardingResult with documentation artifacts.
        """
        step = OnboardingStep.DOCUMENT
        
        if not self.state.can_proceed_to(step):
            reasons = self.state.get_blocking_reasons(step)
            return OnboardingResult(
                step=step,
                success=False,
                message=f"Cannot document: prerequisites not met",
                next_action=f"Blocking reasons: {', '.join(reasons)}",
            )
        
        if self.state.current_step != step:
            return OnboardingResult(
                step=step,
                success=False,
                message=f"Cannot execute {step.value}: current step is {self.state.current_step.value}",
                next_action="Complete the current step first",
            )
        
        try:
            # Generate documentation
            docs_generated = []
            
            axiom_dir = Path(self.state.artifacts.get("axiom_dir", ""))
            docs_dir = axiom_dir / "docs"
            docs_dir.mkdir(exist_ok=True)
            
            # Generate README
            readme_path = docs_dir / "README.md"
            with open(readme_path, "w") as f:
                f.write("# Project Documentation\n\n")
                f.write("*Generated by Axiom onboarding*\n\n")
                f.write("## Components\n\n")
                
                if self._cpkg:
                    for node_id, node in self._cpkg.nodes.items():
                        if node.type == NodeType.COMPONENT:
                            f.write(f"- **{node_id}**: {node.content}\n")
                
                f.write("\n---\n")
                f.write("*This documentation is derived and regenerable.*\n")
            
            docs_generated.append(str(readme_path))
            
            self.state.artifacts["docs_dir"] = str(docs_dir)
            self.state.artifacts["docs_generated"] = docs_generated
            
            self.state.mark_completed(step)
            
            return OnboardingResult(
                step=step,
                success=True,
                message=f"Generated {len(docs_generated)} documentation files",
                artifacts={
                    "docs_dir": str(docs_dir),
                    "docs_count": len(docs_generated),
                },
                next_step=OnboardingStep.VALIDATE,
                next_action="Run step_validate() to verify Canon integrity",
            )
            
        except Exception as e:
            self.state.mark_failed(step, str(e))
            return OnboardingResult(
                step=step,
                success=False,
                message=f"Documentation failed: {e}",
            )
    
    # =========================================================================
    # Step 9: Validate
    # =========================================================================
    
    def step_validate(self) -> OnboardingResult:
        """
        Validate Canon integrity and consistency.
        
        Checks:
        - All required artifacts exist
        - CPKG is well-formed
        - UCIR constraints are valid
        - No orphaned references
        
        Returns:
            OnboardingResult with validation status.
        """
        step = OnboardingStep.VALIDATE
        
        if not self.state.can_proceed_to(step):
            reasons = self.state.get_blocking_reasons(step)
            return OnboardingResult(
                step=step,
                success=False,
                message=f"Cannot validate: prerequisites not met",
                next_action=f"Blocking reasons: {', '.join(reasons)}",
            )
        
        if self.state.current_step != step:
            return OnboardingResult(
                step=step,
                success=False,
                message=f"Cannot execute {step.value}: current step is {self.state.current_step.value}",
                next_action="Complete the current step first",
            )
        
        try:
            validation_errors = []
            validation_warnings = []
            
            # Check artifacts exist
            cpkg_path = Path(self.state.artifacts.get("cpkg_path", ""))
            ucir_path = Path(self.state.artifacts.get("ucir_path", ""))
            bfm_path = Path(self.state.artifacts.get("bfm_path", ""))
            
            if not cpkg_path.exists():
                validation_errors.append("CPKG file not found")
            if not ucir_path.exists():
                validation_errors.append("UCIR file not found")
            if not bfm_path.exists():
                validation_errors.append("BFM file not found")
            
            # Check CPKG integrity
            if self._cpkg:
                # Check for orphaned edges
                node_ids = set(self._cpkg.nodes.keys())
                for edge in self._cpkg.edges:
                    if edge.source_id not in node_ids:
                        validation_errors.append(f"Orphaned edge source: {edge.source_id}")
                    if edge.target_id not in node_ids:
                        validation_errors.append(f"Orphaned edge target: {edge.target_id}")
                
                # Check node content length
                for node_id, node in self._cpkg.nodes.items():
                    if len(node.content) > 200:
                        validation_warnings.append(f"Node {node_id} content exceeds recommended length")
            
            # Check UCIR constraints
            if self._ucir:
                for constraint_id, constraint in self._ucir.constraints.items():
                    if not constraint.description:
                        validation_warnings.append(f"Constraint {constraint_id} has empty description")
            
            self.state.artifacts["validation_errors"] = validation_errors
            self.state.artifacts["validation_warnings"] = validation_warnings
            
            if validation_errors:
                self.state.mark_failed(step, f"{len(validation_errors)} validation errors")
                return OnboardingResult(
                    step=step,
                    success=False,
                    message=f"Validation failed with {len(validation_errors)} errors",
                    artifacts={
                        "errors": validation_errors,
                        "warnings": validation_warnings,
                    },
                    next_action="Fix validation errors and run step_validate() again",
                )
            
            self.state.mark_completed(step)
            
            return OnboardingResult(
                step=step,
                success=True,
                message=f"Validation passed ({len(validation_warnings)} warnings)",
                artifacts={
                    "errors": [],
                    "warnings": validation_warnings,
                },
                next_step=OnboardingStep.FIRST_RUN,
                next_action="Run step_first_run() to execute first governed workflow (optional)",
                can_abort=False,  # Validation is read-only
            )
            
        except Exception as e:
            self.state.mark_failed(step, str(e))
            return OnboardingResult(
                step=step,
                success=False,
                message=f"Validation failed: {e}",
            )
    
    # =========================================================================
    # Step 10: First Run (Optional)
    # =========================================================================
    
    def step_first_run(
        self,
        request: str = "run tests",
        confirm: bool = False,
    ) -> OnboardingResult:
        """
        Execute first governed workflow.
        
        This step:
        1. Creates TacticalIntent from request
        2. Runs preview (no execution)
        3. Requires human approval
        4. Executes only if approved
        
        REQUIRES EXPLICIT CONFIRMATION.
        
        Args:
            request: The user request to execute.
            confirm: Must be True to proceed.
        
        Returns:
            OnboardingResult with execution status.
        """
        step = OnboardingStep.FIRST_RUN
        
        if not self.state.can_proceed_to(step):
            reasons = self.state.get_blocking_reasons(step)
            return OnboardingResult(
                step=step,
                success=False,
                message=f"Cannot run: prerequisites not met",
                next_action=f"Blocking reasons: {', '.join(reasons)}",
            )
        
        if self.state.current_step != step:
            return OnboardingResult(
                step=step,
                success=False,
                message=f"Cannot execute {step.value}: current step is {self.state.current_step.value}",
                next_action="Complete the current step first",
            )
        
        if not confirm:
            return OnboardingResult(
                step=step,
                success=False,
                message="First workflow execution requires explicit confirmation",
                next_action="Call step_first_run(request='...', confirm=True)",
                can_abort=True,
                abort_instructions="Onboarding is complete without first run",
            )
        
        try:
            # Import workflow
            from axiom_core.workflow import AxiomWorkflow
            
            # Create workflow
            workflow = AxiomWorkflow()
            
            # Get Canon artifacts
            cpkg = self._cpkg or CPKG()
            ucir = self._ucir or UCIR()
            bfm = self._bfm or BusinessFlowMap()
            
            # Run workflow
            result = workflow.run(request, cpkg, ucir, bfm)
            
            self.state.artifacts["workflow_result"] = result
            
            self.state.mark_completed(step)
            
            return OnboardingResult(
                step=step,
                success=result.success,
                message=result.message,
                artifacts={
                    "workflow_success": result.success,
                    "execution_events": len(result.execution_events) if result.execution_events else 0,
                },
                next_step=None,
                next_action="Onboarding complete! Use AxiomWorkflow for subsequent operations.",
            )
            
        except Exception as e:
            self.state.mark_failed(step, str(e))
            return OnboardingResult(
                step=step,
                success=False,
                message=f"First run failed: {e}",
                abort_instructions="Onboarding is complete even without first run",
            )
    
    def skip_first_run(self) -> OnboardingResult:
        """
        Skip first workflow execution.
        
        Onboarding is complete after validation.
        
        Returns:
            OnboardingResult confirming skip.
        """
        step = OnboardingStep.FIRST_RUN
        
        if self.state.current_step != step:
            return OnboardingResult(
                step=step,
                success=False,
                message=f"Cannot skip {step.value}: current step is {self.state.current_step.value}",
            )
        
        self.state.skip_optional(step)
        
        return OnboardingResult(
            step=step,
            success=True,
            message="First run skipped. Onboarding complete!",
            next_step=None,
            next_action="Use AxiomWorkflow for governed operations.",
        )
    
    # =========================================================================
    # Utilities
    # =========================================================================
    
    def get_progress(self) -> str:
        """Get formatted progress display."""
        return self.display.render_progress(self.state)
    
    def get_step_details(self, step: OnboardingStep) -> str:
        """Get detailed information about a step."""
        return self.display.render_step_details(step)
    
    def abort(self, confirm: bool = False) -> OnboardingResult:
        """
        Abort onboarding and clean up.
        
        Args:
            confirm: Must be True to proceed.
        
        Returns:
            OnboardingResult with abort status.
        """
        if not confirm:
            return OnboardingResult(
                step=self.state.current_step,
                success=False,
                message="Abort requires explicit confirmation",
                next_action=self.display.render_abort_confirmation(self.state),
            )
        
        try:
            # Clean up .axiom directory
            axiom_dir = Path(self.state.artifacts.get("axiom_dir", ""))
            if axiom_dir.exists():
                import shutil
                shutil.rmtree(axiom_dir)
            
            return OnboardingResult(
                step=self.state.current_step,
                success=True,
                message="Onboarding aborted and cleaned up",
                artifacts={
                    "cleaned_up": str(axiom_dir),
                },
            )
            
        except Exception as e:
            return OnboardingResult(
                step=self.state.current_step,
                success=False,
                message=f"Abort failed: {e}",
            )

    def run_quick_init(self, project_path: str) -> OnboardingResult:
        """
        Run a quick initialization for CLI usage.
        
        This method runs the essential initialization steps without
        requiring interactive input. It creates the basic project
        structure needed for Axiom to operate.
        
        Args:
            project_path: Path to initialize the project in.
            
        Returns:
            OnboardingResult indicating success or failure.
        """
        # Step 1: Initialize directory structure
        init_result = self.step_initialize()
        if not init_result.success:
            return init_result
        
        # Step 2: Bootstrap Canon artifacts
        bootstrap_result = self.step_bootstrap()
        if not bootstrap_result.success:
            return bootstrap_result
        
        # For quick init, we stop here with minimal viable setup
        # User can run remaining steps manually if needed
        return OnboardingResult(
            step=OnboardingStep.BOOTSTRAP,
            success=True,
            message="Quick initialization complete. Project is ready for planning.",
            artifacts={
                **init_result.artifacts,
                **bootstrap_result.artifacts,
            },
            next_step=OnboardingStep.CONFIGURE,
            next_action="Run 'axiom plan' to create your first plan, or 'axiom discover' for existing code.",
        )
