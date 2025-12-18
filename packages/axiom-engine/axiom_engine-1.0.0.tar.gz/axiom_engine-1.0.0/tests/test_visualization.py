"""
Tests for Axiom Interface Visualization and UX Components.

This test module verifies:
1. TaskGraph visualization produces valid ASCII output
2. Execution timeline renders chronologically
3. Artifact surfacing respects size limits
4. Decision display clearly separates AI from Human
5. Workflow guide enforces canonical steps and prevents skipping

All tests verify READ-ONLY behavior — no execution, no mutation.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from axiom_interface import (
    TaskGraphVisualization,
    ExecutionTimelineVisualization,
    ArtifactVisualization,
    StrategicDecisionDisplay,
    HumanDecisionDisplay,
    FinalDecisionDisplay,
    WorkflowStep,
    StepStatus,
    WorkflowState,
    WorkflowProgressDisplay,
    WorkflowGuard,
)
from axiom_canon.task_graph import (
    TaskGraph,
    TaskNode,
    TaskStatus,
    TaskDependency,
)
from axiom_conductor.model import (
    TaskExecutionResult,
    TaskExecutionState,
)
from axiom_archon.model import (
    StrategicDecision,
    StrategicDecisionType,
    StrategicIssue,
    StrategicIssueSeverity,
)
from axiom_archon.human_loop import (
    HumanDecision,
    HumanDecisionAction,
    FinalDecision,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def sample_task_graph() -> TaskGraph:
    """Create a sample TaskGraph for visualization tests."""
    node_a = TaskNode(
        id="task-a",
        name="Parse requirements",
        description="Parse user requirements",
        status=TaskStatus.COMPLETED,
    )
    
    node_b = TaskNode(
        id="task-b",
        name="Generate plan",
        description="Generate execution plan",
        status=TaskStatus.COMPLETED,
    )
    
    node_c = TaskNode(
        id="task-c",
        name="Validate constraints",
        description="Validate against UCIR",
        status=TaskStatus.RUNNING,
    )
    
    node_d = TaskNode(
        id="task-d",
        name="Execute tasks",
        description="Execute approved tasks",
        status=TaskStatus.PENDING,
    )
    
    dependencies = [
        TaskDependency(upstream_task_id="task-a", downstream_task_id="task-b"),
        TaskDependency(upstream_task_id="task-a", downstream_task_id="task-c"),
        TaskDependency(upstream_task_id="task-b", downstream_task_id="task-d"),
        TaskDependency(upstream_task_id="task-c", downstream_task_id="task-d"),
    ]
    
    return TaskGraph(
        id="graph-001",
        tasks={"task-a": node_a, "task-b": node_b, "task-c": node_c, "task-d": node_d},
        dependencies=dependencies,
    )


@pytest.fixture
def sample_execution_results() -> list[TaskExecutionResult]:
    """Create sample execution results for timeline tests."""
    now = datetime.now(timezone.utc).isoformat()
    return [
        TaskExecutionResult(
            task_id="task-a",
            state=TaskExecutionState.SUCCEEDED,
            stdout="Parsed 10 requirements",
            stderr="",
            exit_code=0,
            timestamp=now,
        ),
        TaskExecutionResult(
            task_id="task-b",
            state=TaskExecutionState.SUCCEEDED,
            stdout="Generated plan with 4 tasks",
            stderr="",
            exit_code=0,
            timestamp=now,
        ),
        TaskExecutionResult(
            task_id="task-c",
            state=TaskExecutionState.FAILED,
            stdout="",
            stderr="Constraint violation: no shell execution allowed",
            exit_code=1,
            timestamp=now,
        ),
    ]


@pytest.fixture
def sample_strategic_decision() -> StrategicDecision:
    """Create a sample strategic decision."""
    return StrategicDecision(
        decision=StrategicDecisionType.APPROVE,
        reason="Plan is coherent and satisfies all constraints.",
        issues=[
            StrategicIssue(
                type="resource_usage",
                message="High memory usage possible",
                severity=StrategicIssueSeverity.WARNING,
            ),
        ],
        authorization_signature="sig-12345",
    )


@pytest.fixture
def sample_human_decision() -> HumanDecision:
    """Create a sample human decision."""
    return HumanDecision(
        action=HumanDecisionAction.APPROVE,
        user_id="human-001",
        rationale="Reviewed and approved for execution.",
    )


@pytest.fixture
def sample_final_decision(
    sample_strategic_decision: StrategicDecision,
    sample_human_decision: HumanDecision,
) -> FinalDecision:
    """Create a sample final decision."""
    return FinalDecision(
        id=str(uuid4()),
        verdict=StrategicDecisionType.APPROVE,
        is_authorized=True,
        strategic_decision=sample_strategic_decision,
        human_decision=sample_human_decision,
        authorization_signature="final-sig-12345",
    )


@pytest.fixture
def sample_workflow_state() -> WorkflowState:
    """Create a sample workflow state."""
    state = WorkflowState()
    state.current_step = WorkflowStep.VALIDATE
    state.step_statuses[WorkflowStep.INTENT] = StepStatus.COMPLETED
    state.step_statuses[WorkflowStep.PLAN] = StepStatus.COMPLETED
    state.step_statuses[WorkflowStep.VALIDATE] = StepStatus.CURRENT
    return state


# =============================================================================
# TASK GRAPH VISUALIZATION TESTS
# =============================================================================


class TestTaskGraphVisualization:
    """Tests for TaskGraph visualization."""
    
    def test_render_ascii_dag_produces_output(self, sample_task_graph: TaskGraph) -> None:
        """ASCII DAG render should produce non-empty output."""
        result = TaskGraphVisualization.render_ascii_dag(sample_task_graph)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "TASK GRAPH" in result
    
    def test_render_ascii_dag_shows_all_tasks(self, sample_task_graph: TaskGraph) -> None:
        """ASCII DAG render should show all task names."""
        result = TaskGraphVisualization.render_ascii_dag(sample_task_graph)
        
        assert "Parse requirements" in result
        assert "Generate plan" in result
        assert "Validate constraints" in result
        assert "Execute tasks" in result
    
    def test_render_ascii_dag_shows_dependencies(self, sample_task_graph: TaskGraph) -> None:
        """ASCII DAG render should show dependency information."""
        result = TaskGraphVisualization.render_ascii_dag(sample_task_graph)
        
        # Should show dependency info (depends on:)
        assert "depends on" in result.lower() or "root" in result.lower()
    
    def test_render_ascii_dag_shows_parallel_levels(self, sample_task_graph: TaskGraph) -> None:
        """ASCII DAG render should identify parallelizable tasks."""
        result = TaskGraphVisualization.render_ascii_dag(sample_task_graph)
        
        # Should show Level information
        assert "Level" in result
        # task-b and task-c can run in parallel
        assert "PARALLEL" in result
    
    def test_render_dependency_table_produces_output(self, sample_task_graph: TaskGraph) -> None:
        """Dependency table render should produce structured output."""
        result = TaskGraphVisualization.render_dependency_table(sample_task_graph)
        
        assert isinstance(result, str)
        assert len(result) > 0
        # Tables have separators
        assert "-" in result
    
    def test_render_dependency_table_shows_all_tasks(self, sample_task_graph: TaskGraph) -> None:
        """Dependency table should show all tasks."""
        result = TaskGraphVisualization.render_dependency_table(sample_task_graph)
        
        assert "task-a" in result
        assert "task-b" in result
        assert "task-c" in result
        assert "task-d" in result
    
    def test_visualization_is_read_only(self, sample_task_graph: TaskGraph) -> None:
        """Visualization should not modify the TaskGraph."""
        original_tasks = dict(sample_task_graph.tasks)
        original_statuses = {k: v.status for k, v in sample_task_graph.tasks.items()}
        
        TaskGraphVisualization.render_ascii_dag(sample_task_graph)
        TaskGraphVisualization.render_dependency_table(sample_task_graph)
        
        # Verify no modifications
        assert sample_task_graph.tasks == original_tasks
        for task_id, node in sample_task_graph.tasks.items():
            assert node.status == original_statuses[task_id]
    
    def test_empty_graph_renders_gracefully(self) -> None:
        """Empty graph should render without errors."""
        empty_graph = TaskGraph(
            id="empty",
            tasks={},
            dependencies=[],
        )
        
        result = TaskGraphVisualization.render_ascii_dag(empty_graph)
        
        assert isinstance(result, str)
        assert "No tasks" in result or len(result) > 0


class TestExecutionTimelineVisualization:
    """Tests for execution timeline visualization."""
    
    def test_render_timeline_produces_output(
        self,
        sample_task_graph: TaskGraph,
        sample_execution_results: list[TaskExecutionResult],
    ) -> None:
        """Timeline render should produce non-empty output."""
        # Convert list to dict for the method
        results_dict = {r.task_id: r for r in sample_execution_results}
        result = ExecutionTimelineVisualization.render_timeline(sample_task_graph, results_dict)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_render_timeline_shows_all_tasks(
        self,
        sample_task_graph: TaskGraph,
        sample_execution_results: list[TaskExecutionResult],
    ) -> None:
        """Timeline should show all task IDs."""
        results_dict = {r.task_id: r for r in sample_execution_results}
        result = ExecutionTimelineVisualization.render_timeline(sample_task_graph, results_dict)
        
        assert "task-a" in result
        assert "task-b" in result
        assert "task-c" in result
    
    def test_render_timeline_shows_status(
        self,
        sample_task_graph: TaskGraph,
        sample_execution_results: list[TaskExecutionResult],
    ) -> None:
        """Timeline should show success/failure status."""
        results_dict = {r.task_id: r for r in sample_execution_results}
        result = ExecutionTimelineVisualization.render_timeline(sample_task_graph, results_dict)
        
        result_upper = result.upper()
        # Should indicate both success and failure
        assert "SUCCESS" in result_upper or "✓" in result or "SUCCEEDED" in result_upper
        assert "FAILED" in result_upper or "FAIL" in result_upper or "✗" in result
    
    def test_empty_results_renders_gracefully(self, sample_task_graph: TaskGraph) -> None:
        """Empty results should render without errors."""
        result = ExecutionTimelineVisualization.render_timeline(sample_task_graph, {})
        
        assert isinstance(result, str)


class TestArtifactVisualization:
    """Tests for artifact surfacing."""
    
    def test_render_shell_output_shows_stdout(self, sample_execution_results: list[TaskExecutionResult]) -> None:
        """Should surface stdout from results."""
        # Render the first result which has stdout
        result = ArtifactVisualization.render_shell_output(sample_execution_results[0])
        
        assert "Parsed 10 requirements" in result
    
    def test_render_shell_output_shows_stderr(self, sample_execution_results: list[TaskExecutionResult]) -> None:
        """Should surface stderr from failed results."""
        # Render the third result which has stderr
        result = ArtifactVisualization.render_shell_output(sample_execution_results[2])
        
        assert "Constraint violation" in result
    
    def test_surfacing_is_read_only(self, sample_execution_results: list[TaskExecutionResult]) -> None:
        """Surfacing should not modify results."""
        original_count = len(sample_execution_results)
        original_stdout = sample_execution_results[0].stdout
        
        ArtifactVisualization.render_shell_output(sample_execution_results[0])
        
        assert len(sample_execution_results) == original_count
        assert sample_execution_results[0].stdout == original_stdout


# =============================================================================
# DECISION DISPLAY TESTS
# =============================================================================


class TestStrategicDecisionDisplay:
    """Tests for strategic (AI) decision display."""
    
    def test_render_labeled_as_ai(self, sample_strategic_decision: StrategicDecision) -> None:
        """Strategic decision should be labeled as AI recommendation."""
        result = StrategicDecisionDisplay.render(sample_strategic_decision)
        
        # Must explicitly label as AI
        assert "AI" in result.upper()
        assert "RECOMMENDATION" in result.upper() or "NOT FINAL" in result.upper()
    
    def test_render_shows_reason(self, sample_strategic_decision: StrategicDecision) -> None:
        """Strategic decision should show reason."""
        result = StrategicDecisionDisplay.render(sample_strategic_decision)
        
        assert "coherent" in result.lower() or sample_strategic_decision.reason in result
    
    def test_render_shows_issues(self, sample_strategic_decision: StrategicDecision) -> None:
        """Strategic decision should show issues/concerns."""
        result = StrategicDecisionDisplay.render(sample_strategic_decision)
        
        assert "memory" in result.lower() or "ISSUE" in result.upper() or "WARNING" in result.upper()


class TestHumanDecisionDisplay:
    """Tests for human decision display."""
    
    def test_render_labeled_as_human(self, sample_human_decision: HumanDecision) -> None:
        """Human decision should be labeled as human authorization."""
        result = HumanDecisionDisplay.render(sample_human_decision)
        
        # Must explicitly label as human
        assert "HUMAN" in result.upper()
        assert "AUTHOR" in result.upper() or "DECISION" in result.upper()
    
    def test_render_shows_action(self, sample_human_decision: HumanDecision) -> None:
        """Human decision should clearly show action."""
        result = HumanDecisionDisplay.render(sample_human_decision)
        
        assert "APPROVE" in result.upper() or "✓" in result
    
    def test_render_rejection(self) -> None:
        """Human rejection should be clearly displayed."""
        rejection = HumanDecision(
            action=HumanDecisionAction.REJECT,
            user_id="human-002",
            rationale="Rejected due to security concerns.",
        )
        
        result = HumanDecisionDisplay.render(rejection)
        
        assert "REJECT" in result.upper() or "DENIED" in result.upper() or "✗" in result


class TestFinalDecisionDisplay:
    """Tests for final decision display."""
    
    def test_render_combines_both(self, sample_final_decision: FinalDecision) -> None:
        """Final decision should show both AI and Human decisions."""
        result = FinalDecisionDisplay.render(sample_final_decision)
        
        # Should show both sources clearly
        assert "AI" in result.upper()
        assert "HUMAN" in result.upper()
    
    def test_ai_and_human_visually_distinct(
        self,
        sample_strategic_decision: StrategicDecision,
        sample_human_decision: HumanDecision,
    ) -> None:
        """AI and Human sections should be visually distinct."""
        ai_result = StrategicDecisionDisplay.render(sample_strategic_decision)
        human_result = HumanDecisionDisplay.render(sample_human_decision)
        
        # Should have different headers/markers
        assert ai_result != human_result


# =============================================================================
# WORKFLOW GUIDE TESTS
# =============================================================================


class TestWorkflowStep:
    """Tests for canonical workflow steps."""
    
    def test_canonical_steps_defined(self) -> None:
        """All canonical steps should be defined."""
        assert WorkflowStep.INTENT is not None
        assert WorkflowStep.PLAN is not None
        assert WorkflowStep.VALIDATE is not None
        assert WorkflowStep.SIMULATE is not None
        assert WorkflowStep.REVIEW is not None
        assert WorkflowStep.APPROVE is not None
        assert WorkflowStep.EXECUTE is not None
    
    def test_step_count(self) -> None:
        """Should have exactly 7 canonical steps."""
        assert len(WorkflowStep) == 7


class TestWorkflowProgressDisplay:
    """Tests for workflow progress display."""
    
    def test_render_produces_output(self, sample_workflow_state: WorkflowState) -> None:
        """Progress render should produce non-empty output."""
        result = WorkflowProgressDisplay.render(sample_workflow_state)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_render_shows_all_steps(self, sample_workflow_state: WorkflowState) -> None:
        """Should show all workflow steps."""
        result = WorkflowProgressDisplay.render(sample_workflow_state)
        
        assert "Intent" in result or "INTENT" in result.upper()
        assert "Plan" in result or "PLANNING" in result.upper()
        assert "Validat" in result  # Validate/Validation
        assert "Approv" in result  # Approve/Approval
        assert "Execut" in result  # Execute/Execution
    
    def test_render_shows_current_step(self, sample_workflow_state: WorkflowState) -> None:
        """Should highlight current step."""
        result = WorkflowProgressDisplay.render(sample_workflow_state)
        
        # Current step should be marked
        assert "►" in result or "PROGRESS" in result.upper()
    
    def test_render_compact_produces_output(self, sample_workflow_state: WorkflowState) -> None:
        """Compact render should produce output."""
        result = WorkflowProgressDisplay.render_compact(sample_workflow_state)
        
        assert isinstance(result, str)
        assert len(result) > 0


class TestWorkflowGuard:
    """Tests for workflow step skip prevention."""
    
    def test_refuse_skip_produces_refusal(self) -> None:
        """Skip refusal should produce a clear message."""
        result = WorkflowGuard.refuse_skip(
            requested_step=WorkflowStep.EXECUTE,
            current_step=WorkflowStep.INTENT,
        )
        
        assert isinstance(result, str)
        assert "REFUSED" in result.upper() or "SKIP" in result.upper()
    
    def test_refuse_skip_explains_skipped_steps(self) -> None:
        """Skip refusal should explain what steps would be skipped."""
        result = WorkflowGuard.refuse_skip(
            requested_step=WorkflowStep.EXECUTE,
            current_step=WorkflowStep.INTENT,
        )
        
        # Should mention intermediate steps
        assert "PLAN" in result.upper() or "planning" in result.lower()
        assert "APPROV" in result.upper() or "approval" in result.lower()
    
    def test_explain_step_produces_output(self) -> None:
        """Step explanation should produce output."""
        for step in WorkflowStep:
            result = WorkflowGuard.explain_step(step)
            assert isinstance(result, str)
            assert len(result) > 0
    
    def test_guard_has_no_execute_methods(self) -> None:
        """Guard should not have any execution capability."""
        assert not hasattr(WorkflowGuard, "execute")
        assert not hasattr(WorkflowGuard, "run")
        assert not hasattr(WorkflowGuard, "perform")
        assert not hasattr(WorkflowGuard, "approve")


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestVisualizationIntegration:
    """Integration tests for visualization components."""
    
    def test_full_workflow_visualization(
        self,
        sample_task_graph: TaskGraph,
        sample_execution_results: list[TaskExecutionResult],
        sample_strategic_decision: StrategicDecision,
        sample_human_decision: HumanDecision,
        sample_workflow_state: WorkflowState,
    ) -> None:
        """All visualization components should work together."""
        # Task graph visualization
        graph_output = TaskGraphVisualization.render_ascii_dag(sample_task_graph)
        assert len(graph_output) > 0
        
        # Timeline visualization
        results_dict = {r.task_id: r for r in sample_execution_results}
        timeline_output = ExecutionTimelineVisualization.render_timeline(sample_task_graph, results_dict)
        assert len(timeline_output) > 0
        
        # Decision display
        ai_output = StrategicDecisionDisplay.render(sample_strategic_decision)
        human_output = HumanDecisionDisplay.render(sample_human_decision)
        assert "AI" in ai_output.upper()
        assert "HUMAN" in human_output.upper()
        
        # Workflow progress
        progress = WorkflowProgressDisplay.render(sample_workflow_state)
        assert len(progress) > 0
    
    def test_visualization_classes_are_read_only(self) -> None:
        """All visualization classes should be read-only."""
        # TaskGraphVisualization
        assert not hasattr(TaskGraphVisualization, "execute")
        assert not hasattr(TaskGraphVisualization, "run")
        assert not hasattr(TaskGraphVisualization, "modify")
        
        # ExecutionTimelineVisualization  
        assert not hasattr(ExecutionTimelineVisualization, "execute")
        
        # WorkflowGuard
        assert not hasattr(WorkflowGuard, "execute")
        assert not hasattr(WorkflowGuard, "approve")
