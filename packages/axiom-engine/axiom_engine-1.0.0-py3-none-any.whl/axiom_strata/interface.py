"""
Tactical Planner Interface.

This module defines the protocol for Tactical Planners.
A Tactical Planner is responsible for converting a TacticalIntent into a TaskGraph.

Responsibilities:
- Decompose intent into discrete tasks.
- Identify dependencies between tasks.
- Ensure the plan respects constraints (UCIR).
- Ensure the plan is grounded in reality (CPKG).

Constraints:
- Must NOT execute tasks.
- Must NOT schedule tasks (Conductor does that).
- Must be deterministic given the same inputs.
"""

from typing import Protocol

from axiom_strata.model import TacticalIntent, PlanningContext, PlanningResult


class TacticalPlanner(Protocol):
    """
    Protocol for components that can generate TaskGraphs from intent.
    """
    
    def plan(self, intent: TacticalIntent, context: PlanningContext) -> PlanningResult:
        """
        Generate a TaskGraph based on the provided intent and context.
        
        Args:
            intent: The description of what needs to be done.
            context: The knowledge artifacts available for planning.
            
        Returns:
            PlanningResult: The generated plan and any issues found.
        """
        ...
