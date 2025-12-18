"""
Axiom Visualization Module.

This module provides READ-ONLY visualization of Axiom execution artifacts.
It transforms internal data structures into human-readable formats for
display in the IDE or terminal.

CRITICAL DESIGN PRINCIPLE: PRESENTATION ONLY

This module:
- Renders data for human understanding
- Provides no editing, mutation, or interaction capability
- Never hides governance steps or failures
- Always shows complete information

This module does NOT:
- Execute anything
- Modify any state
- Make decisions
- Skip or collapse workflow steps
- Hide risks or failures

Visualization Formats:
- ASCII DAG for TaskGraph (pre-execution preview)
- Timeline view for execution results
- Structured artifact listings
- Dependency tables

UX Principle: Clarity over Convenience
If a visualization could mislead, we refuse to simplify it.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Tuple
from enum import Enum
from datetime import datetime

from axiom_canon.task_graph import TaskGraph, TaskNode, TaskDependency, TaskStatus
from axiom_conductor.model import TaskExecutionResult, TaskExecutionState, ExecutionEvent


# =============================================================================
# TaskGraph Visualization (Preview Mode)
# =============================================================================


@dataclass
class TaskGraphVisualization:
    """
    READ-ONLY visualization of a TaskGraph before execution.
    
    This class renders the planned execution as:
    - ASCII DAG showing dependencies
    - Topological execution order
    - Parallelizable task groups
    
    It provides NO capability to:
    - Reorder tasks
    - Edit dependencies
    - Modify the graph
    """
    
    @staticmethod
    def render_ascii_dag(graph: TaskGraph) -> str:
        """
        Render the TaskGraph as an ASCII DAG.
        
        Args:
            graph: The TaskGraph to visualize.
            
        Returns:
            ASCII string representation of the DAG.
        """
        lines: List[str] = []
        lines.append("=" * 60)
        lines.append("TASK GRAPH PREVIEW (READ-ONLY)")
        lines.append("=" * 60)
        lines.append("")
        
        if not graph.tasks:
            lines.append("  (No tasks in graph)")
            return "\n".join(lines)
        
        # Build dependency map
        downstream_map: Dict[str, List[str]] = {task_id: [] for task_id in graph.tasks}
        upstream_map: Dict[str, List[str]] = {task_id: [] for task_id in graph.tasks}
        
        for dep in graph.dependencies:
            if dep.upstream_task_id in downstream_map:
                downstream_map[dep.upstream_task_id].append(dep.downstream_task_id)
            if dep.downstream_task_id in upstream_map:
                upstream_map[dep.downstream_task_id].append(dep.upstream_task_id)
        
        # Find root tasks (no upstream dependencies)
        root_tasks = [tid for tid, ups in upstream_map.items() if not ups]
        
        # Compute topological levels
        levels = TaskGraphVisualization._compute_levels(graph, upstream_map)
        
        # Group tasks by level
        level_groups: Dict[int, List[str]] = {}
        for task_id, level in levels.items():
            if level not in level_groups:
                level_groups[level] = []
            level_groups[level].append(task_id)
        
        # Render levels
        lines.append("Execution Levels (Parallel within each level):")
        lines.append("-" * 50)
        
        for level in sorted(level_groups.keys()):
            task_ids = level_groups[level]
            parallel_marker = " [PARALLEL]" if len(task_ids) > 1 else ""
            lines.append(f"\nLevel {level}{parallel_marker}:")
            
            for task_id in task_ids:
                task = graph.tasks[task_id]
                deps = upstream_map.get(task_id, [])
                dep_str = f" (depends on: {', '.join(deps)})" if deps else " (root)"
                lines.append(f"  ├── [{task_id}] {task.name}{dep_str}")
                if task.description:
                    lines.append(f"  │   └── {task.description[:50]}...")
        
        lines.append("")
        lines.append("-" * 50)
        lines.append(f"Total Tasks: {len(graph.tasks)}")
        lines.append(f"Parallelizable Levels: {len(level_groups)}")
        lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def render_dependency_table(graph: TaskGraph) -> str:
        """
        Render a table showing task dependencies.
        
        Args:
            graph: The TaskGraph to visualize.
            
        Returns:
            Formatted table string.
        """
        lines: List[str] = []
        lines.append("=" * 70)
        lines.append("TASK DEPENDENCY TABLE (READ-ONLY)")
        lines.append("=" * 70)
        lines.append("")
        
        if not graph.tasks:
            lines.append("  (No tasks in graph)")
            return "\n".join(lines)
        
        # Build upstream map
        upstream_map: Dict[str, List[str]] = {task_id: [] for task_id in graph.tasks}
        for dep in graph.dependencies:
            if dep.downstream_task_id in upstream_map:
                upstream_map[dep.downstream_task_id].append(dep.upstream_task_id)
        
        # Header
        lines.append(f"{'Task ID':<20} {'Task Name':<25} {'Depends On':<25}")
        lines.append("-" * 70)
        
        for task_id, task in graph.tasks.items():
            deps = upstream_map.get(task_id, [])
            dep_str = ", ".join(deps) if deps else "(none - root)"
            name_truncated = task.name[:22] + "..." if len(task.name) > 25 else task.name
            lines.append(f"{task_id:<20} {name_truncated:<25} {dep_str:<25}")
        
        lines.append("")
        return "\n".join(lines)
    
    @staticmethod
    def render_execution_order(graph: TaskGraph) -> str:
        """
        Render the topological execution order.
        
        Args:
            graph: The TaskGraph to visualize.
            
        Returns:
            Ordered list of tasks.
        """
        lines: List[str] = []
        lines.append("=" * 50)
        lines.append("EXECUTION ORDER (TOPOLOGICAL)")
        lines.append("=" * 50)
        lines.append("")
        
        if not graph.tasks:
            lines.append("  (No tasks in graph)")
            return "\n".join(lines)
        
        # Build upstream map
        upstream_map: Dict[str, List[str]] = {task_id: [] for task_id in graph.tasks}
        for dep in graph.dependencies:
            if dep.downstream_task_id in upstream_map:
                upstream_map[dep.downstream_task_id].append(dep.upstream_task_id)
        
        # Compute levels and sort
        levels = TaskGraphVisualization._compute_levels(graph, upstream_map)
        ordered = sorted(graph.tasks.keys(), key=lambda tid: (levels.get(tid, 0), tid))
        
        for idx, task_id in enumerate(ordered, 1):
            task = graph.tasks[task_id]
            lines.append(f"  {idx:3}. [{task_id}] {task.name}")
        
        lines.append("")
        lines.append("Note: Tasks at the same level may execute in parallel.")
        lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def _compute_levels(graph: TaskGraph, upstream_map: Dict[str, List[str]]) -> Dict[str, int]:
        """
        Compute the topological level for each task.
        Level 0 = root tasks (no dependencies).
        """
        levels: Dict[str, int] = {}
        
        def get_level(task_id: str, visited: Set[str]) -> int:
            if task_id in levels:
                return levels[task_id]
            if task_id in visited:
                # Cycle detected - return 0 to avoid infinite recursion
                return 0
            
            visited.add(task_id)
            upstream = upstream_map.get(task_id, [])
            if not upstream:
                levels[task_id] = 0
            else:
                max_parent_level = max(
                    get_level(parent, visited) for parent in upstream
                )
                levels[task_id] = max_parent_level + 1
            
            return levels[task_id]
        
        for task_id in graph.tasks:
            get_level(task_id, set())
        
        return levels


# =============================================================================
# Execution Timeline Visualization (Post-Execution)
# =============================================================================


@dataclass
class ExecutionTimelineVisualization:
    """
    READ-ONLY visualization of execution results as a timeline.
    
    This class renders:
    - Task state transitions
    - Execution duration
    - Failure propagation
    - Root cause analysis
    
    It highlights:
    - FAILED tasks (with error details)
    - SKIPPED tasks (with skip reason)
    - Root cause tasks (first failure in chain)
    """
    
    @staticmethod
    def render_timeline(
        graph: TaskGraph,
        results: Dict[str, TaskExecutionResult],
        events: Optional[List[ExecutionEvent]] = None
    ) -> str:
        """
        Render execution results as a timeline.
        
        Args:
            graph: The executed TaskGraph.
            results: Mapping of task_id to execution result.
            events: Optional list of execution events.
            
        Returns:
            Formatted timeline string.
        """
        lines: List[str] = []
        lines.append("=" * 70)
        lines.append("EXECUTION TIMELINE (POST-EXECUTION REPORT)")
        lines.append("=" * 70)
        lines.append("")
        
        if not results:
            lines.append("  (No execution results available)")
            return "\n".join(lines)
        
        # Categorize results
        succeeded = []
        failed = []
        skipped = []
        
        for task_id, result in results.items():
            if result.state == TaskExecutionState.SUCCEEDED:
                succeeded.append((task_id, result))
            elif result.state == TaskExecutionState.FAILED:
                failed.append((task_id, result))
            elif result.state == TaskExecutionState.SKIPPED:
                skipped.append((task_id, result))
        
        # Summary
        lines.append("SUMMARY:")
        lines.append(f"  ✓ Succeeded: {len(succeeded)}")
        lines.append(f"  ✗ Failed:    {len(failed)}")
        lines.append(f"  ○ Skipped:   {len(skipped)}")
        lines.append(f"  Total:       {len(results)}")
        lines.append("")
        
        # Detailed timeline
        lines.append("-" * 70)
        lines.append("DETAILED TIMELINE:")
        lines.append("-" * 70)
        lines.append("")
        
        # Sort by timestamp if available
        sorted_results = sorted(
            results.items(),
            key=lambda x: x[1].timestamp or ""
        )
        
        for task_id, result in sorted_results:
            state_icon = ExecutionTimelineVisualization._get_state_icon(result.state)
            task_name = graph.tasks[task_id].name if task_id in graph.tasks else task_id
            
            lines.append(f"{state_icon} [{task_id}] {task_name}")
            lines.append(f"    State: {result.state.value}")
            
            if result.timestamp:
                lines.append(f"    Time:  {result.timestamp}")
            
            if result.exit_code is not None:
                lines.append(f"    Exit:  {result.exit_code}")
            
            if result.state == TaskExecutionState.FAILED:
                lines.append(f"    ⚠ FAILURE REASON: {result.failure_reason.value if result.failure_reason else 'unknown'}")
                if result.error_message:
                    lines.append(f"    ⚠ ERROR: {result.error_message}")
            
            lines.append("")
        
        # Root cause analysis for failures
        if failed:
            lines.append("-" * 70)
            lines.append("ROOT CAUSE ANALYSIS:")
            lines.append("-" * 70)
            lines.append("")
            
            # Find root cause (first failure in dependency chain)
            root_causes = ExecutionTimelineVisualization._find_root_causes(
                graph, {tid: r for tid, r in failed}
            )
            
            for task_id in root_causes:
                result = results[task_id]
                lines.append(f"  ⚠ ROOT CAUSE: [{task_id}]")
                if result.error_message:
                    lines.append(f"    Error: {result.error_message}")
                lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def render_state_transitions(events: List[ExecutionEvent]) -> str:
        """
        Render state transitions from execution events.
        
        Args:
            events: List of execution events.
            
        Returns:
            Formatted state transition log.
        """
        lines: List[str] = []
        lines.append("=" * 60)
        lines.append("STATE TRANSITIONS LOG")
        lines.append("=" * 60)
        lines.append("")
        
        if not events:
            lines.append("  (No events recorded)")
            return "\n".join(lines)
        
        for event in events:
            task_id = event.task_id or "(system)"
            lines.append(f"[{event.timestamp}] {event.event_type}")
            lines.append(f"  Task: {task_id}")
            if event.payload:
                for key, value in event.payload.items():
                    lines.append(f"  {key}: {value}")
            lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def _get_state_icon(state: TaskExecutionState) -> str:
        """Get a visual icon for the state."""
        icons = {
            TaskExecutionState.SUCCEEDED: "✓",
            TaskExecutionState.FAILED: "✗",
            TaskExecutionState.SKIPPED: "○",
            TaskExecutionState.RUNNING: "►",
            TaskExecutionState.READY: "◉",
            TaskExecutionState.PENDING: "◌",
        }
        return icons.get(state, "?")
    
    @staticmethod
    def _find_root_causes(
        graph: TaskGraph,
        failed_results: Dict[str, TaskExecutionResult]
    ) -> List[str]:
        """
        Find root cause tasks (failures not caused by upstream failures).
        """
        # Build upstream map
        upstream_map: Dict[str, List[str]] = {task_id: [] for task_id in graph.tasks}
        for dep in graph.dependencies:
            if dep.downstream_task_id in upstream_map:
                upstream_map[dep.downstream_task_id].append(dep.upstream_task_id)
        
        root_causes = []
        failed_ids = set(failed_results.keys())
        
        for task_id in failed_ids:
            # Check if any upstream task also failed
            upstream = upstream_map.get(task_id, [])
            upstream_failed = any(up in failed_ids for up in upstream)
            
            if not upstream_failed:
                # This is a root cause (first failure in its chain)
                root_causes.append(task_id)
        
        return root_causes


# =============================================================================
# Artifact Surfacing
# =============================================================================


@dataclass
class ArtifactVisualization:
    """
    READ-ONLY visualization of execution artifacts.
    
    Surfaces:
    - stdout/stderr (Shell backend)
    - Screenshots, traces, videos (Playwright backend)
    - Artifact paths and sizes
    
    Artifacts are:
    - Shown explicitly with full paths
    - Never auto-opened
    - Never summarized or hidden
    """
    
    @staticmethod
    def render_shell_output(result: TaskExecutionResult) -> str:
        """
        Render shell command output.
        
        Args:
            result: The task execution result.
            
        Returns:
            Formatted output display.
        """
        lines: List[str] = []
        lines.append("=" * 60)
        lines.append(f"SHELL OUTPUT: [{result.task_id}]")
        lines.append("=" * 60)
        lines.append("")
        
        # Exit code
        lines.append(f"Exit Code: {result.exit_code}")
        lines.append(f"State: {result.state.value}")
        lines.append("")
        
        # stdout
        lines.append("-" * 40)
        lines.append("STDOUT:")
        lines.append("-" * 40)
        if result.stdout:
            lines.append(result.stdout)
        else:
            lines.append("  (empty)")
        lines.append("")
        
        # stderr
        lines.append("-" * 40)
        lines.append("STDERR:")
        lines.append("-" * 40)
        if result.stderr:
            lines.append(result.stderr)
        else:
            lines.append("  (empty)")
        lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def render_playwright_artifacts(result: TaskExecutionResult) -> str:
        """
        Render Playwright execution artifacts.
        
        Args:
            result: The task execution result with Playwright metadata.
            
        Returns:
            Formatted artifact listing.
        """
        lines: List[str] = []
        lines.append("=" * 60)
        lines.append(f"PLAYWRIGHT ARTIFACTS: [{result.task_id}]")
        lines.append("=" * 60)
        lines.append("")
        
        lines.append(f"State: {result.state.value}")
        lines.append("")
        
        metadata = result.metadata or {}
        
        # Screenshot
        screenshot_path = metadata.get("screenshot_path")
        if screenshot_path:
            import os
            size = "unknown"
            if os.path.exists(screenshot_path):
                size = f"{os.path.getsize(screenshot_path):,} bytes"
            lines.append("SCREENSHOT:")
            lines.append(f"  Path: {screenshot_path}")
            lines.append(f"  Size: {size}")
            lines.append("  ⚠ Manual action required to view")
            lines.append("")
        
        # Trace
        trace_path = metadata.get("trace_path")
        if trace_path:
            lines.append("TRACE:")
            lines.append(f"  Path: {trace_path}")
            lines.append("  ⚠ Use 'playwright show-trace' to view")
            lines.append("")
        
        # Video
        video_path = metadata.get("video_path")
        if video_path:
            lines.append("VIDEO:")
            lines.append(f"  Path: {video_path}")
            lines.append("  ⚠ Manual action required to view")
            lines.append("")
        
        # Script result data
        if "success" in metadata:
            lines.append("SCRIPT RESULT:")
            for key, value in metadata.items():
                if key not in ("screenshot_path", "trace_path", "video_path"):
                    lines.append(f"  {key}: {value}")
            lines.append("")
        
        if not any([screenshot_path, trace_path, video_path, "success" in metadata]):
            lines.append("  (No artifacts captured)")
            lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def render_artifact_summary(results: Dict[str, TaskExecutionResult]) -> str:
        """
        Render a summary of all artifacts across tasks.
        
        Args:
            results: All task execution results.
            
        Returns:
            Formatted summary.
        """
        lines: List[str] = []
        lines.append("=" * 60)
        lines.append("ARTIFACT SUMMARY")
        lines.append("=" * 60)
        lines.append("")
        
        screenshot_count = 0
        trace_count = 0
        video_count = 0
        tasks_with_output = 0
        
        for task_id, result in results.items():
            if result.stdout or result.stderr:
                tasks_with_output += 1
            
            metadata = result.metadata or {}
            if metadata.get("screenshot_path"):
                screenshot_count += 1
            if metadata.get("trace_path"):
                trace_count += 1
            if metadata.get("video_path"):
                video_count += 1
        
        lines.append(f"Tasks with stdout/stderr: {tasks_with_output}")
        lines.append(f"Screenshots captured:     {screenshot_count}")
        lines.append(f"Traces captured:          {trace_count}")
        lines.append(f"Videos captured:          {video_count}")
        lines.append("")
        lines.append("Note: Artifacts are NOT auto-opened for security.")
        lines.append("      Use file paths above to access manually.")
        lines.append("")
        
        return "\n".join(lines)
