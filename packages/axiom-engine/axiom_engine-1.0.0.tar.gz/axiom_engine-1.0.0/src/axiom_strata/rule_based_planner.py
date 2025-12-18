"""
Rule-Based Tactical Planner.

This module implements a simple, deterministic planner that converts
well-known intents into TaskGraphs using explicit rules.

Purpose:
- Prove the end-to-end pipeline (Strata -> Conductor -> Forge).
- Provide a baseline for testing.
- Handle common, repetitive tasks without LLM overhead.

Constraints:
- No heuristics.
- No learning.
- Explicit string matching only.
"""

import uuid
from typing import Dict, List, Optional

from axiom_canon.task_graph import TaskGraph, TaskNode, TaskDependency
from axiom_strata.model import (
    TacticalIntent,
    PlanningContext,
    PlanningResult,
    PlanningIssue,
    PlanningIssueType
)
from axiom_strata.interface import TacticalPlanner


class RuleBasedTacticalPlanner:
    """
    A simple planner that maps specific intent descriptions to pre-defined TaskGraphs.
    """

    def plan(self, intent: TacticalIntent, context: PlanningContext) -> PlanningResult:
        """
        Generate a TaskGraph based on the provided intent.
        """
        description = intent.description.lower().strip()
        
        if "run tests" in description:
            return self._plan_run_tests(intent, context)
        elif "lint code" in description:
            return self._plan_lint_code(intent, context)
        elif "format code" in description:
            return self._plan_format_code(intent, context)
        elif "build project" in description:
            return self._plan_build_project(intent, context)
        else:
            return self._create_unsupported_result(intent)

    def _create_graph_id(self) -> str:
        return f"graph-{uuid.uuid4()}"

    def _plan_run_tests(self, intent: TacticalIntent, context: PlanningContext) -> PlanningResult:
        """
        Generates a plan to run tests.
        """
        graph_id = self._create_graph_id()
        
        # Simple plan: 1. Install deps (optional/assumed) -> 2. Run pytest
        # For this rule-based planner, we'll assume environment is ready.
        
        task_test = TaskNode(
            id="task-test",
            name="Run Unit Tests",
            description="Execute pytest suite",
            command="pytest",
            args=["tests/"],  # Assumption: tests are in tests/
            timeout_seconds=300
        )
        
        graph = TaskGraph(
            id=graph_id,
            tasks={task_test.id: task_test},
            dependencies=[],
            metadata={"intent_id": intent.id, "type": "run_tests"}
        )
        
        return PlanningResult(graph=graph)

    def _plan_lint_code(self, intent: TacticalIntent, context: PlanningContext) -> PlanningResult:
        """
        Generates a plan to lint the codebase.
        """
        graph_id = self._create_graph_id()
        
        # Plan: Flake8 -> MyPy (dependent)
        
        task_flake8 = TaskNode(
            id="task-flake8",
            name="Run Flake8",
            description="Lint code with flake8",
            command="flake8",
            args=["src/"],
            timeout_seconds=120
        )
        
        task_mypy = TaskNode(
            id="task-mypy",
            name="Run MyPy",
            description="Type check with mypy",
            command="mypy",
            args=["src/"],
            timeout_seconds=120
        )
        
        # Dependency: Run flake8 first, then mypy (arbitrary choice for demo)
        dep = TaskDependency(upstream_task_id=task_flake8.id, downstream_task_id=task_mypy.id)
        
        graph = TaskGraph(
            id=graph_id,
            tasks={
                task_flake8.id: task_flake8,
                task_mypy.id: task_mypy
            },
            dependencies=[dep],
            metadata={"intent_id": intent.id, "type": "lint_code"}
        )
        
        return PlanningResult(graph=graph)

    def _plan_format_code(self, intent: TacticalIntent, context: PlanningContext) -> PlanningResult:
        """
        Generates a plan to format the codebase.
        """
        graph_id = self._create_graph_id()
        
        task_black = TaskNode(
            id="task-black",
            name="Run Black",
            description="Format code with black",
            command="black",
            args=["src/"],
            timeout_seconds=120
        )
        
        graph = TaskGraph(
            id=graph_id,
            tasks={task_black.id: task_black},
            dependencies=[],
            metadata={"intent_id": intent.id, "type": "format_code"}
        )
        
        return PlanningResult(graph=graph)

    def _plan_build_project(self, intent: TacticalIntent, context: PlanningContext) -> PlanningResult:
        """
        Generates a plan to build the project.
        """
        graph_id = self._create_graph_id()
        
        # Plan: Clean -> Build
        
        task_clean = TaskNode(
            id="task-clean",
            name="Clean Build Artifacts",
            description="Remove dist/ and build/ directories",
            command="rm",
            args=["-rf", "dist/", "build/"],
            timeout_seconds=60
        )
        
        task_build = TaskNode(
            id="task-build",
            name="Build Package",
            description="Build sdist and wheel",
            command="python3",
            args=["-m", "build"],
            timeout_seconds=300
        )
        
        dep = TaskDependency(upstream_task_id=task_clean.id, downstream_task_id=task_build.id)
        
        graph = TaskGraph(
            id=graph_id,
            tasks={
                task_clean.id: task_clean,
                task_build.id: task_build
            },
            dependencies=[dep],
            metadata={"intent_id": intent.id, "type": "build_project"}
        )
        
        return PlanningResult(graph=graph)

    def _create_unsupported_result(self, intent: TacticalIntent) -> PlanningResult:
        """
        Returns a result indicating the intent is not supported.
        """
        issue = PlanningIssue(
            type=PlanningIssueType.UNSUPPORTED_OPERATION,
            message=f"RuleBasedTacticalPlanner does not support intent: '{intent.description}'",
            severity="error",
            context={"intent_id": intent.id}
        )
        return PlanningResult(graph=None, issues=[issue])
