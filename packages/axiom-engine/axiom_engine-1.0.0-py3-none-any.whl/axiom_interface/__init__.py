"""
Axiom Interface Package.

This package defines the public interfaces, contracts, and signals
used for communication between Axiom layers.

Responsibility:
- Define Protocol classes
- Define Signal schemas
- Define RPC or message contracts
- Provide READ-ONLY visualization and UX components

Constraints:
- No implementation logic beyond visualization/presentation
- Pure interface definitions
- Visualization is READ-ONLY (no execution, no mutation)
"""

from axiom_interface.visualization import (
    TaskGraphVisualization,
    ExecutionTimelineVisualization,
    ArtifactVisualization,
)
from axiom_interface.decision_display import (
    StrategicDecisionDisplay,
    HumanDecisionDisplay,
    FinalDecisionDisplay,
    DecisionChainDisplay,
    DecisionComparisonDisplay,
)
from axiom_interface.workflow_guide import (
    WorkflowStep,
    StepStatus,
    WorkflowState,
    WorkflowProgressDisplay,
    WorkflowGuard,
    WorkflowSummaryDisplay,
)

__all__ = [
    # TaskGraph Visualization (READ-ONLY)
    "TaskGraphVisualization",
    "ExecutionTimelineVisualization",
    "ArtifactVisualization",
    # Decision Display (READ-ONLY)
    "StrategicDecisionDisplay",
    "HumanDecisionDisplay",
    "FinalDecisionDisplay",
    "DecisionChainDisplay",
    "DecisionComparisonDisplay",
    # Workflow Guide (READ-ONLY enforcement)
    "WorkflowStep",
    "StepStatus",
    "WorkflowState",
    "WorkflowProgressDisplay",
    "WorkflowGuard",
    "WorkflowSummaryDisplay",
]
