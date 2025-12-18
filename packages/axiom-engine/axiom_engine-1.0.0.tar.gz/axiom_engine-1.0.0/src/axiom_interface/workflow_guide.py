"""
Axiom Workflow Guide Module.

This module enforces the canonical Axiom workflow visually.
It guides users through the required steps and REFUSES to skip any.

CANONICAL AXIOM WORKFLOW:
1. INTENT     - User provides goal
2. PLAN       - Strata generates TaskGraph
3. VALIDATE   - Strata validates the plan
4. SIMULATE   - Strata dry-runs the plan
5. REVIEW     - Archon reviews strategically
6. APPROVE    - Human makes final decision
7. EXECUTE    - Conductor runs tasks via Forge

CRITICAL DESIGN PRINCIPLE: NO SHORTCUTS

This module:
- Displays the current step clearly
- Shows what has been completed
- Shows what is pending
- REFUSES requests to skip steps
- EXPLAINS why skipping is dangerous

This module does NOT:
- Execute any steps
- Make decisions
- Allow step reordering
- Allow step skipping

UX Principle: Governance is Non-Negotiable
If a user asks to skip a step, we explain why that's impossible.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class WorkflowStep(str, Enum):
    """
    The canonical steps in the Axiom workflow.
    
    These steps MUST be executed in order.
    No step may be skipped.
    """
    INTENT = "intent"
    PLAN = "plan"
    VALIDATE = "validate"
    SIMULATE = "simulate"
    REVIEW = "review"
    APPROVE = "approve"
    EXECUTE = "execute"


class StepStatus(str, Enum):
    """Status of a workflow step."""
    PENDING = "pending"
    CURRENT = "current"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"  # Only for display purposes when blocked


# Step metadata
STEP_DETAILS: Dict[WorkflowStep, Dict[str, str]] = {
    WorkflowStep.INTENT: {
        "name": "Intent Formation",
        "description": "User provides the goal or task to accomplish",
        "owner": "Human",
        "layer": "Input",
    },
    WorkflowStep.PLAN: {
        "name": "Task Planning",
        "description": "Strata generates a TaskGraph from the intent",
        "owner": "AI (Strata)",
        "layer": "Tactical",
    },
    WorkflowStep.VALIDATE: {
        "name": "Plan Validation",
        "description": "Strata validates the plan for consistency and feasibility",
        "owner": "AI (Strata)",
        "layer": "Tactical",
    },
    WorkflowStep.SIMULATE: {
        "name": "Dry Run Simulation",
        "description": "Strata simulates execution to detect deadlocks and issues",
        "owner": "AI (Strata)",
        "layer": "Tactical",
    },
    WorkflowStep.REVIEW: {
        "name": "Strategic Review",
        "description": "Archon reviews the plan for alignment and risks",
        "owner": "AI (Archon)",
        "layer": "Strategic",
    },
    WorkflowStep.APPROVE: {
        "name": "Human Approval",
        "description": "Human reviews AI recommendation and makes final decision",
        "owner": "Human",
        "layer": "Authorization",
    },
    WorkflowStep.EXECUTE: {
        "name": "Task Execution",
        "description": "Conductor executes tasks via Forge backends",
        "owner": "System (Conductor)",
        "layer": "Execution",
    },
}


# =============================================================================
# Workflow State Tracking
# =============================================================================


@dataclass
class WorkflowState:
    """
    Tracks the current state of a workflow execution.
    
    This is a READ-ONLY view of progress through the canonical steps.
    """
    step_statuses: Dict[WorkflowStep, StepStatus] = field(default_factory=dict)
    current_step: Optional[WorkflowStep] = None
    workflow_id: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    def __post_init__(self):
        # Initialize all steps as pending if not set
        for step in WorkflowStep:
            if step not in self.step_statuses:
                self.step_statuses[step] = StepStatus.PENDING


# =============================================================================
# Workflow Progress Visualization
# =============================================================================


class WorkflowProgressDisplay:
    """
    READ-ONLY visualization of workflow progress.
    
    Shows:
    - All steps in the canonical order
    - Current step highlighted
    - Completed steps marked
    - Pending steps shown
    """
    
    @staticmethod
    def render(state: WorkflowState) -> str:
        """
        Render the workflow progress.
        
        Args:
            state: The current workflow state.
            
        Returns:
            Formatted progress display.
        """
        lines: List[str] = []
        
        lines.append("╔" + "═" * 58 + "╗")
        lines.append("║" + " AXIOM WORKFLOW PROGRESS ".center(58) + "║")
        lines.append("╠" + "═" * 58 + "╣")
        lines.append("")
        
        steps = list(WorkflowStep)
        
        for i, step in enumerate(steps):
            status = state.step_statuses.get(step, StepStatus.PENDING)
            details = STEP_DETAILS[step]
            
            # Get status icon
            icon = WorkflowProgressDisplay._get_status_icon(status)
            
            # Current step marker
            marker = "►" if step == state.current_step else " "
            
            # Connection line
            if i < len(steps) - 1:
                connector = "│"
            else:
                connector = " "
            
            lines.append(f"  {marker} {icon} Step {i+1}: {details['name']}")
            lines.append(f"        Owner: {details['owner']}")
            
            if status == StepStatus.CURRENT:
                lines.append(f"        ⟶ IN PROGRESS")
            elif status == StepStatus.FAILED:
                lines.append(f"        ⚠ FAILED - Workflow halted")
            
            if i < len(steps) - 1:
                lines.append(f"        {connector}")
                lines.append(f"        ▼")
            
            lines.append("")
        
        lines.append("╚" + "═" * 58 + "╝")
        lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def render_compact(state: WorkflowState) -> str:
        """
        Render a compact single-line progress indicator.
        
        Args:
            state: The current workflow state.
            
        Returns:
            Compact progress string.
        """
        parts = []
        for step in WorkflowStep:
            status = state.step_statuses.get(step, StepStatus.PENDING)
            icon = WorkflowProgressDisplay._get_status_icon(status)
            
            # Highlight current
            if step == state.current_step:
                parts.append(f"[{icon}{step.value.upper()}]")
            else:
                parts.append(f"{icon}{step.value}")
        
        return " → ".join(parts)
    
    @staticmethod
    def _get_status_icon(status: StepStatus) -> str:
        """Get icon for step status."""
        icons = {
            StepStatus.PENDING: "○",
            StepStatus.CURRENT: "►",
            StepStatus.COMPLETED: "✓",
            StepStatus.FAILED: "✗",
            StepStatus.SKIPPED: "⊘",
        }
        return icons.get(status, "?")


# =============================================================================
# Step Skip Refusal
# =============================================================================


class WorkflowGuard:
    """
    Guards against attempts to skip workflow steps.
    
    When a user attempts to skip a step, this class:
    1. REFUSES the request
    2. EXPLAINS why the step is required
    3. REDIRECTS to the correct step
    """
    
    @staticmethod
    def refuse_skip(
        requested_step: WorkflowStep,
        current_step: WorkflowStep
    ) -> str:
        """
        Generate a refusal message when a user tries to skip steps.
        
        Args:
            requested_step: The step the user wants to jump to.
            current_step: The actual current step.
            
        Returns:
            Explanation of why skipping is not allowed.
        """
        lines: List[str] = []
        
        lines.append("╔" + "═" * 58 + "╗")
        lines.append("║" + " ⛔ STEP SKIP REFUSED ⛔ ".center(58) + "║")
        lines.append("╠" + "═" * 58 + "╣")
        lines.append("")
        
        current_details = STEP_DETAILS[current_step]
        requested_details = STEP_DETAILS[requested_step]
        
        lines.append(f"  You requested: {requested_details['name']}")
        lines.append(f"  Current step:  {current_details['name']}")
        lines.append("")
        
        lines.append("  ⚠ Axiom does not allow skipping workflow steps.")
        lines.append("")
        
        # Explain skipped steps
        steps = list(WorkflowStep)
        current_idx = steps.index(current_step)
        requested_idx = steps.index(requested_step)
        
        if requested_idx > current_idx:
            lines.append("  The following steps would be skipped:")
            for i in range(current_idx, requested_idx):
                step = steps[i]
                details = STEP_DETAILS[step]
                lines.append(f"    • {details['name']}: {details['description']}")
            lines.append("")
        
        # Explain why each step matters
        lines.append("  Why each step is required:")
        lines.append("")
        lines.append("    INTENT   → Without clear intent, planning is directionless")
        lines.append("    PLAN     → Without a plan, execution is undefined")
        lines.append("    VALIDATE → Without validation, plans may be inconsistent")
        lines.append("    SIMULATE → Without simulation, deadlocks go undetected")
        lines.append("    REVIEW   → Without review, risks are not assessed")
        lines.append("    APPROVE  → Without approval, execution is unauthorized")
        lines.append("    EXECUTE  → This is the final step (no skip possible)")
        lines.append("")
        
        lines.append("  ⟶ Please complete the current step first:")
        lines.append(f"    {current_details['name']}")
        lines.append("")
        
        lines.append("╚" + "═" * 58 + "╝")
        lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def explain_step(step: WorkflowStep) -> str:
        """
        Explain what a workflow step does and why it's required.
        
        Args:
            step: The step to explain.
            
        Returns:
            Detailed explanation.
        """
        lines: List[str] = []
        details = STEP_DETAILS[step]
        
        lines.append("=" * 60)
        lines.append(f"WORKFLOW STEP: {details['name'].upper()}")
        lines.append("=" * 60)
        lines.append("")
        
        lines.append(f"  Description: {details['description']}")
        lines.append(f"  Owner:       {details['owner']}")
        lines.append(f"  Layer:       {details['layer']}")
        lines.append("")
        
        # Step-specific details
        explanations = {
            WorkflowStep.INTENT: [
                "This step captures what you want to accomplish.",
                "The intent is used by Strata to generate a plan.",
                "Be specific about goals, scope, and constraints.",
            ],
            WorkflowStep.PLAN: [
                "Strata (Tactical Layer) generates a TaskGraph.",
                "The graph defines tasks and their dependencies.",
                "This step is automatic after intent is provided.",
            ],
            WorkflowStep.VALIDATE: [
                "The plan is checked for internal consistency.",
                "Validation catches missing dependencies and cycles.",
                "A valid plan is required before simulation.",
            ],
            WorkflowStep.SIMULATE: [
                "The plan is dry-run without actual execution.",
                "Simulation detects deadlocks and ordering issues.",
                "This step proves the plan CAN execute.",
            ],
            WorkflowStep.REVIEW: [
                "Archon (Strategic Layer) reviews the plan.",
                "Review assesses alignment, risks, and tradeoffs.",
                "The AI recommendation is generated here.",
            ],
            WorkflowStep.APPROVE: [
                "YOU review the AI's recommendation.",
                "You may APPROVE, REJECT, or OVERRIDE.",
                "This is the ONLY step where human authority is exercised.",
            ],
            WorkflowStep.EXECUTE: [
                "Conductor executes the approved TaskGraph.",
                "Forge backends perform the actual work.",
                "Results and artifacts are captured.",
            ],
        }
        
        lines.append("  Details:")
        for detail in explanations.get(step, []):
            lines.append(f"    • {detail}")
        lines.append("")
        
        return "\n".join(lines)


# =============================================================================
# Workflow Summary
# =============================================================================


class WorkflowSummaryDisplay:
    """
    Provides summary views of workflow state.
    """
    
    @staticmethod
    def render_overview() -> str:
        """
        Render an overview of the entire Axiom workflow.
        
        Returns:
            Workflow overview string.
        """
        lines: List[str] = []
        
        lines.append("╔" + "═" * 58 + "╗")
        lines.append("║" + " AXIOM WORKFLOW OVERVIEW ".center(58) + "║")
        lines.append("╠" + "═" * 58 + "╣")
        lines.append("")
        
        lines.append("  The Axiom workflow enforces governed AI execution.")
        lines.append("")
        lines.append("  Every workflow follows these steps IN ORDER:")
        lines.append("")
        lines.append("    ┌──────────┐")
        lines.append("    │  INTENT  │  ← You provide the goal")
        lines.append("    └────┬─────┘")
        lines.append("         │")
        lines.append("    ┌────▼─────┐")
        lines.append("    │   PLAN   │  ← AI generates TaskGraph")
        lines.append("    └────┬─────┘")
        lines.append("         │")
        lines.append("    ┌────▼─────┐")
        lines.append("    │ VALIDATE │  ← AI validates consistency")
        lines.append("    └────┬─────┘")
        lines.append("         │")
        lines.append("    ┌────▼─────┐")
        lines.append("    │ SIMULATE │  ← AI dry-runs the plan")
        lines.append("    └────┬─────┘")
        lines.append("         │")
        lines.append("    ┌────▼─────┐")
        lines.append("    │  REVIEW  │  ← AI assesses risks")
        lines.append("    └────┬─────┘")
        lines.append("         │")
        lines.append("    ┌────▼─────┐")
        lines.append("    │ APPROVE  │  ← YOU make the decision")
        lines.append("    └────┬─────┘")
        lines.append("         │")
        lines.append("    ┌────▼─────┐")
        lines.append("    │ EXECUTE  │  ← System runs tasks")
        lines.append("    └──────────┘")
        lines.append("")
        lines.append("  Key Principles:")
        lines.append("    • AI recommends, Human decides")
        lines.append("    • No step may be skipped")
        lines.append("    • Execution requires explicit approval")
        lines.append("    • Failures halt the workflow immediately")
        lines.append("")
        
        lines.append("╚" + "═" * 58 + "╝")
        lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def render_current_step_prompt(state: WorkflowState) -> str:
        """
        Render a prompt for the current step.
        
        Args:
            state: The current workflow state.
            
        Returns:
            Step-specific prompt.
        """
        if not state.current_step:
            return "No workflow in progress. Provide an intent to begin."
        
        step = state.current_step
        details = STEP_DETAILS[step]
        
        lines: List[str] = []
        lines.append(f"Current Step: {details['name']}")
        lines.append(f"Description:  {details['description']}")
        lines.append("")
        
        prompts = {
            WorkflowStep.INTENT: "Please describe what you want to accomplish.",
            WorkflowStep.PLAN: "Generating plan from your intent...",
            WorkflowStep.VALIDATE: "Validating the generated plan...",
            WorkflowStep.SIMULATE: "Running dry simulation...",
            WorkflowStep.REVIEW: "Archon is reviewing the plan...",
            WorkflowStep.APPROVE: "Please review the AI recommendation and make your decision: APPROVE, REJECT, or OVERRIDE.",
            WorkflowStep.EXECUTE: "Executing approved tasks...",
        }
        
        lines.append(f"⟶ {prompts.get(step, 'Proceeding...')}")
        lines.append("")
        
        return "\n".join(lines)
