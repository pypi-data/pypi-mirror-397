"""
CLI Workflow State Module.

This module tracks workflow state for CLI command ordering.

IMPORTANT:
- State is stored in .axiom/workflow_state.json
- State is used ONLY for precondition checking
- CLI does NOT make decisions based on state
- All governance is delegated to existing Axiom classes
"""

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, List


class WorkflowPhase(Enum):
    """Current phase of the Axiom workflow.
    
    Phases must progress in order:
    UNINITIALIZED -> INITIALIZED -> PLANNED -> APPROVED -> EXECUTED
    
    Discovery and adoption are optional parallel tracks.
    """
    
    UNINITIALIZED = "uninitialized"
    INITIALIZED = "initialized"
    DISCOVERED = "discovered"
    PLANNED = "planned"
    PREVIEWED = "previewed"
    APPROVED = "approved"
    EXECUTED = "executed"


@dataclass(frozen=True)
class WorkflowState:
    """
    Immutable workflow state for CLI precondition checking.
    
    This class tracks the current workflow phase and any pending plans.
    It does NOT make decisions - it only reports state.
    
    Attributes:
        phase: Current workflow phase.
        project_root: Absolute path to project root.
        current_plan_id: ID of the current plan (if any).
        current_intent: Current tactical intent (if any).
        approval_signature: Signature from human approval (if approved).
        last_updated: ISO timestamp of last state update.
        history: List of phase transitions with timestamps.
    """
    
    phase: WorkflowPhase
    project_root: str
    current_plan_id: Optional[str] = None
    current_intent: Optional[str] = None
    approval_signature: Optional[str] = None
    last_updated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    history: tuple = field(default_factory=tuple)
    
    def is_initialized(self) -> bool:
        """Check if Axiom is initialized.
        
        Returns:
            True if initialized, False otherwise.
        """
        return self.phase != WorkflowPhase.UNINITIALIZED
    
    def is_planned(self) -> bool:
        """Check if a plan exists.
        
        Returns:
            True if a plan has been created, False otherwise.
        """
        return self.phase in {
            WorkflowPhase.PLANNED,
            WorkflowPhase.PREVIEWED,
            WorkflowPhase.APPROVED,
            WorkflowPhase.EXECUTED,
        }
    
    def is_previewed(self) -> bool:
        """Check if plan has been previewed.
        
        Returns:
            True if previewed, False otherwise.
        """
        return self.phase in {
            WorkflowPhase.PREVIEWED,
            WorkflowPhase.APPROVED,
            WorkflowPhase.EXECUTED,
        }
    
    def is_approved(self) -> bool:
        """Check if plan has been approved.
        
        Returns:
            True if approved, False otherwise.
        """
        return self.phase in {
            WorkflowPhase.APPROVED,
            WorkflowPhase.EXECUTED,
        }
    
    def is_executed(self) -> bool:
        """Check if plan has been executed.
        
        Returns:
            True if executed, False otherwise.
        """
        return self.phase == WorkflowPhase.EXECUTED
    
    def is_discovered(self) -> bool:
        """Check if discovery has been run.
        
        Returns:
            True if discovered, False otherwise.
        """
        return self.phase == WorkflowPhase.DISCOVERED or self.current_plan_id is not None
    
    def with_phase(self, new_phase: WorkflowPhase) -> "WorkflowState":
        """Create a new state with updated phase.
        
        Args:
            new_phase: The new workflow phase.
            
        Returns:
            New WorkflowState with updated phase.
        """
        new_history = list(self.history) + [
            {"from": self.phase.value, "to": new_phase.value, "timestamp": datetime.now(timezone.utc).isoformat()}
        ]
        return WorkflowState(
            phase=new_phase,
            project_root=self.project_root,
            current_plan_id=self.current_plan_id,
            current_intent=self.current_intent,
            approval_signature=self.approval_signature,
            last_updated=datetime.now(timezone.utc).isoformat(),
            history=tuple(new_history),
        )
    
    def with_plan(self, plan_id: str, intent: str) -> "WorkflowState":
        """Create a new state with a plan.
        
        Args:
            plan_id: ID of the new plan.
            intent: The tactical intent.
            
        Returns:
            New WorkflowState with plan.
        """
        new_history = list(self.history) + [
            {"from": self.phase.value, "to": WorkflowPhase.PLANNED.value, "timestamp": datetime.now(timezone.utc).isoformat()}
        ]
        return WorkflowState(
            phase=WorkflowPhase.PLANNED,
            project_root=self.project_root,
            current_plan_id=plan_id,
            current_intent=intent,
            approval_signature=None,
            last_updated=datetime.now(timezone.utc).isoformat(),
            history=tuple(new_history),
        )
    
    def with_approval(self, signature: str) -> "WorkflowState":
        """Create a new state with approval.
        
        Args:
            signature: The approval signature.
            
        Returns:
            New WorkflowState with approval.
        """
        new_history = list(self.history) + [
            {"from": self.phase.value, "to": WorkflowPhase.APPROVED.value, "timestamp": datetime.now(timezone.utc).isoformat()}
        ]
        return WorkflowState(
            phase=WorkflowPhase.APPROVED,
            project_root=self.project_root,
            current_plan_id=self.current_plan_id,
            current_intent=self.current_intent,
            approval_signature=signature,
            last_updated=datetime.now(timezone.utc).isoformat(),
            history=tuple(new_history),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary.
        
        Returns:
            Dictionary representation of state.
        """
        return {
            "phase": self.phase.value,
            "project_root": self.project_root,
            "current_plan_id": self.current_plan_id,
            "current_intent": self.current_intent,
            "approval_signature": self.approval_signature,
            "last_updated": self.last_updated,
            "history": list(self.history),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowState":
        """Create state from dictionary.
        
        Args:
            data: Dictionary representation.
            
        Returns:
            WorkflowState instance.
        """
        return cls(
            phase=WorkflowPhase(data.get("phase", "uninitialized")),
            project_root=data.get("project_root", "."),
            current_plan_id=data.get("current_plan_id"),
            current_intent=data.get("current_intent"),
            approval_signature=data.get("approval_signature"),
            last_updated=data.get("last_updated", datetime.now(timezone.utc).isoformat()),
            history=tuple(data.get("history", [])),
        )
    
    @classmethod
    def uninitialized(cls, project_root: str) -> "WorkflowState":
        """Create an uninitialized state.
        
        Args:
            project_root: Path to project root.
            
        Returns:
            Uninitialized WorkflowState.
        """
        return cls(
            phase=WorkflowPhase.UNINITIALIZED,
            project_root=project_root,
        )


def _get_state_file_path(project_root: str) -> Path:
    """Get the path to the workflow state file.
    
    Args:
        project_root: Path to project root.
        
    Returns:
        Path to workflow_state.json.
    """
    return Path(project_root) / ".axiom" / "workflow_state.json"


def load_workflow_state(project_root: str) -> WorkflowState:
    """Load workflow state from disk.
    
    Args:
        project_root: Path to project root.
        
    Returns:
        Current workflow state, or uninitialized if not found.
    """
    state_file = _get_state_file_path(project_root)
    
    # Check if .axiom directory exists
    axiom_dir = Path(project_root) / ".axiom"
    if not axiom_dir.exists():
        return WorkflowState.uninitialized(project_root)
    
    # Check if state file exists
    if not state_file.exists():
        # Axiom directory exists but no state file - assume initialized
        return WorkflowState(
            phase=WorkflowPhase.INITIALIZED,
            project_root=project_root,
        )
    
    try:
        with open(state_file, "r") as f:
            data = json.load(f)
        return WorkflowState.from_dict(data)
    except (json.JSONDecodeError, IOError):
        # Corrupted state file - treat as uninitialized
        return WorkflowState.uninitialized(project_root)


def save_workflow_state(state: WorkflowState) -> None:
    """Save workflow state to disk.
    
    Args:
        state: The workflow state to save.
    """
    state_file = _get_state_file_path(state.project_root)
    
    # Ensure .axiom directory exists
    state_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(state_file, "w") as f:
        json.dump(state.to_dict(), f, indent=2)
