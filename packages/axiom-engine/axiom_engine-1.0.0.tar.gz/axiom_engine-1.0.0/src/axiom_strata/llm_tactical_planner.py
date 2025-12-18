"""
LLM-Backed Tactical Planner.

This module implements an LLM-assisted planner that proposes TaskGraphs
from TacticalIntent. The LLM serves as an ADVISORY component only.

CRITICAL DESIGN PRINCIPLES:

1. ADVISORY ONLY
   - The LLM proposes plans; it does NOT execute them
   - The LLM suggests tasks; it does NOT approve them
   - All output must be validated before use

2. NO AUTHORITY
   - Cannot execute tasks
   - Cannot approve plans
   - Cannot modify Canon artifacts
   - Cannot bypass validation or dry-run

3. FALLBACK-SAFE
   - LLM unavailability does NOT block planning
   - RuleBasedTacticalPlanner is always available as fallback
   - Failures are explicit and structured

4. MACHINE-VALIDATED
   - All LLM output is parsed and validated
   - Invalid output results in PlanningIssues, not exceptions
   - No self-correction or retry loops

All LLM-generated plans are labeled:
"[AI GENERATED PLAN – NOT FINAL]"

The plan MUST still pass:
- validate_planning_result
- simulate_execution
- Archon strategic review
- Human authorization
"""

import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any, Set, Protocol

from axiom_canon.task_graph import TaskGraph, TaskNode, TaskDependency, TaskStatus
from axiom_strata.model import (
    TacticalIntent,
    PlanningContext,
    PlanningResult,
    PlanningIssue,
    PlanningIssueType,
)
from axiom_strata.interface import TacticalPlanner
from axiom_strata.rule_based_planner import RuleBasedTacticalPlanner


# =============================================================================
# LLM Planning Contract - Input/Output Models
# =============================================================================


class LLMConfidenceLevel(str, Enum):
    """
    Qualitative confidence levels for LLM-generated plans.
    
    These are explicitly qualitative to avoid false precision.
    """
    HIGH = "high"           # LLM is confident in the plan
    MEDIUM = "medium"       # LLM has some uncertainty
    LOW = "low"             # LLM is uncertain, human review strongly advised
    UNKNOWN = "unknown"     # LLM did not provide confidence


@dataclass
class LLMPlanningHints:
    """
    Optional hints to guide LLM planning.
    
    These are soft preferences, not hard constraints.
    """
    preferred_tools: List[str] = field(default_factory=list)
    avoid_tools: List[str] = field(default_factory=list)
    max_tasks: Optional[int] = None
    parallel_preference: Optional[str] = None  # "maximize", "minimize", "none"
    additional_context: Optional[str] = None


@dataclass
class LLMPlanningInput:
    """
    The STRICT input contract for LLM planning.
    
    This is what gets sent to the LLM (after formatting).
    """
    intent: TacticalIntent
    context_summary: str  # Summarized Canon context (not raw artifacts)
    hints: LLMPlanningHints = field(default_factory=LLMPlanningHints)
    
    def to_prompt(self) -> str:
        """
        Format the input as a prompt for the LLM.
        
        Returns:
            Formatted prompt string.
        """
        lines = [
            "You are a tactical planner for a software engineering platform.",
            "Your role is to propose a TaskGraph (directed acyclic graph of tasks).",
            "",
            "IMPORTANT CONSTRAINTS:",
            "- You propose plans; you do NOT execute them",
            "- Your output will be validated by humans",
            "- If uncertain, express uncertainty explicitly",
            "- Do NOT include tasks that require human judgment",
            "",
            "=== INTENT ===",
            f"ID: {self.intent.id}",
            f"Description: {self.intent.description}",
        ]
        
        if self.intent.scope_ids:
            lines.append(f"Scope: {', '.join(self.intent.scope_ids)}")
        
        if self.intent.constraints:
            lines.append(f"Constraints: {', '.join(self.intent.constraints)}")
        
        lines.extend([
            "",
            "=== CONTEXT ===",
            self.context_summary,
            "",
        ])
        
        if self.hints.preferred_tools:
            lines.append(f"Preferred tools: {', '.join(self.hints.preferred_tools)}")
        
        if self.hints.avoid_tools:
            lines.append(f"Avoid tools: {', '.join(self.hints.avoid_tools)}")
        
        if self.hints.max_tasks:
            lines.append(f"Max tasks: {self.hints.max_tasks}")
        
        if self.hints.additional_context:
            lines.append(f"Additional context: {self.hints.additional_context}")
        
        lines.extend([
            "",
            "=== OUTPUT FORMAT ===",
            "Respond with a JSON object containing:",
            "{",
            '  "tasks": [',
            '    {"id": "task-1", "name": "...", "description": "...", "command": "...", "args": [...]}',
            "  ],",
            '  "dependencies": [',
            '    {"upstream": "task-1", "downstream": "task-2"}',
            "  ],",
            '  "explanation": {',
            '    "reasoning": "Why these tasks were chosen",',
            '    "assumptions": ["List of assumptions made"],',
            '    "uncertainties": ["List of uncertainties"]',
            "  },",
            '  "confidence": "high|medium|low"',
            "}",
        ])
        
        return "\n".join(lines)


@dataclass
class TaskProposal:
    """
    A proposed task from the LLM.
    """
    id: str
    name: str
    description: str
    command: Optional[str] = None
    args: List[str] = field(default_factory=list)
    timeout_seconds: int = 300


@dataclass
class DependencyProposal:
    """
    A proposed dependency from the LLM.
    """
    upstream_id: str
    downstream_id: str


@dataclass
class PlanningExplanation:
    """
    The LLM's explanation of its reasoning.
    
    This is for human understanding, not execution.
    """
    reasoning: str
    assumptions: List[str] = field(default_factory=list)
    uncertainties: List[str] = field(default_factory=list)


@dataclass
class LLMPlanningOutput:
    """
    The STRICT output contract from LLM planning.
    
    This is what the LLM must produce (after parsing).
    """
    tasks: List[TaskProposal]
    dependencies: List[DependencyProposal]
    explanation: PlanningExplanation
    confidence: LLMConfidenceLevel
    
    # Metadata
    raw_response: Optional[str] = None
    parse_warnings: List[str] = field(default_factory=list)


# =============================================================================
# LLM Backend Protocol
# =============================================================================


class LLMBackend(Protocol):
    """
    Protocol for LLM backends.
    
    The planner does not care how the LLM is called, only that
    it receives a prompt and returns a response.
    """
    
    def generate(self, prompt: str) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The input prompt.
            
        Returns:
            The LLM's response as a string.
            
        Raises:
            LLMUnavailableError: If the LLM cannot be reached.
        """
        ...
    
    def is_available(self) -> bool:
        """
        Check if the LLM backend is available.
        
        Returns:
            True if the LLM can be called.
        """
        ...


class LLMUnavailableError(Exception):
    """Raised when the LLM backend cannot be reached."""
    pass


# =============================================================================
# Output Parser
# =============================================================================


@dataclass
class ParseResult:
    """Result of parsing LLM output."""
    success: bool
    output: Optional[LLMPlanningOutput] = None
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


class LLMOutputParser:
    """
    Parser for LLM planning output.
    
    Converts raw LLM response to structured LLMPlanningOutput.
    All parsing failures result in ParseResult with error, not exceptions.
    """
    
    @staticmethod
    def parse(raw_response: str) -> ParseResult:
        """
        Parse raw LLM response into structured output.
        
        Args:
            raw_response: The raw string from the LLM.
            
        Returns:
            ParseResult with either output or error.
        """
        warnings: List[str] = []
        
        # Handle empty response
        if not raw_response or not raw_response.strip():
            return ParseResult(
                success=False,
                error="LLM returned empty response"
            )
        
        # Extract JSON from response (may be wrapped in markdown)
        json_str = LLMOutputParser._extract_json(raw_response)
        if not json_str:
            return ParseResult(
                success=False,
                error="Could not extract JSON from LLM response"
            )
        
        # Parse JSON
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            return ParseResult(
                success=False,
                error=f"Invalid JSON in LLM response: {e}"
            )
        
        # Validate required fields
        if "tasks" not in data:
            return ParseResult(
                success=False,
                error="LLM response missing 'tasks' field"
            )
        
        # Parse tasks
        tasks: List[TaskProposal] = []
        for i, task_data in enumerate(data.get("tasks", [])):
            task = LLMOutputParser._parse_task(task_data, i)
            if task:
                tasks.append(task)
            else:
                warnings.append(f"Skipped invalid task at index {i}")
        
        if not tasks:
            return ParseResult(
                success=False,
                error="LLM response contains no valid tasks"
            )
        
        # Parse dependencies
        dependencies: List[DependencyProposal] = []
        for dep_data in data.get("dependencies", []):
            dep = LLMOutputParser._parse_dependency(dep_data)
            if dep:
                dependencies.append(dep)
        
        # Parse explanation
        explanation = LLMOutputParser._parse_explanation(
            data.get("explanation", {})
        )
        
        # Parse confidence
        confidence_str = data.get("confidence", "unknown").lower()
        try:
            confidence = LLMConfidenceLevel(confidence_str)
        except ValueError:
            confidence = LLMConfidenceLevel.UNKNOWN
            warnings.append(f"Unknown confidence level: {confidence_str}")
        
        output = LLMPlanningOutput(
            tasks=tasks,
            dependencies=dependencies,
            explanation=explanation,
            confidence=confidence,
            raw_response=raw_response,
            parse_warnings=warnings,
        )
        
        return ParseResult(
            success=True,
            output=output,
            warnings=warnings,
        )
    
    @staticmethod
    def _extract_json(text: str) -> Optional[str]:
        """Extract JSON from text, handling markdown code blocks."""
        text = text.strip()
        
        # Try to find JSON in markdown code block
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end > start:
                return text[start:end].strip()
        
        if "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            if end > start:
                return text[start:end].strip()
        
        # Try to find raw JSON
        if text.startswith("{"):
            return text
        
        # Look for { and } brackets
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            return text[start:end+1]
        
        return None
    
    @staticmethod
    def _parse_task(data: Any, index: int) -> Optional[TaskProposal]:
        """Parse a single task from LLM output."""
        if not isinstance(data, dict):
            return None
        
        task_id = data.get("id") or f"task-{index+1}"
        name = data.get("name")
        description = data.get("description", "")
        
        if not name:
            return None
        
        return TaskProposal(
            id=task_id,
            name=name,
            description=description,
            command=data.get("command"),
            args=data.get("args", []),
            timeout_seconds=data.get("timeout_seconds", 300),
        )
    
    @staticmethod
    def _parse_dependency(data: Any) -> Optional[DependencyProposal]:
        """Parse a single dependency from LLM output."""
        if not isinstance(data, dict):
            return None
        
        upstream = data.get("upstream") or data.get("upstream_id")
        downstream = data.get("downstream") or data.get("downstream_id")
        
        if not upstream or not downstream:
            return None
        
        return DependencyProposal(
            upstream_id=upstream,
            downstream_id=downstream,
        )
    
    @staticmethod
    def _parse_explanation(data: Any) -> PlanningExplanation:
        """Parse explanation from LLM output."""
        if not isinstance(data, dict):
            return PlanningExplanation(
                reasoning="No explanation provided",
                assumptions=[],
                uncertainties=[],
            )
        
        return PlanningExplanation(
            reasoning=data.get("reasoning", "No reasoning provided"),
            assumptions=data.get("assumptions", []),
            uncertainties=data.get("uncertainties", []),
        )


# =============================================================================
# Plan Validation (LLM-Specific)
# =============================================================================


@dataclass
class LLMPlanValidationResult:
    """Result of validating an LLM-generated plan."""
    is_valid: bool
    issues: List[PlanningIssue] = field(default_factory=list)


class LLMPlanValidator:
    """
    Validates LLM-generated plans for structural correctness.
    
    This is a PRE-validation before the plan enters the standard
    validation pipeline. It catches LLM-specific errors.
    """
    
    @staticmethod
    def validate(
        output: LLMPlanningOutput,
        context: PlanningContext,
    ) -> LLMPlanValidationResult:
        """
        Validate an LLM-generated plan.
        
        Checks:
        1. No duplicate task IDs
        2. All dependency references are valid
        3. No cycles in the dependency graph
        4. No empty or ambiguous tasks
        
        Args:
            output: The parsed LLM output.
            context: The planning context.
            
        Returns:
            Validation result with any issues.
        """
        issues: List[PlanningIssue] = []
        
        # Collect task IDs
        task_ids: Set[str] = set()
        for task in output.tasks:
            if task.id in task_ids:
                issues.append(PlanningIssue(
                    type=PlanningIssueType.STRUCTURAL_ERROR,
                    message=f"Duplicate task ID: {task.id}",
                    severity="error",
                ))
            task_ids.add(task.id)
        
        # Validate dependencies reference valid tasks
        for dep in output.dependencies:
            if dep.upstream_id not in task_ids:
                issues.append(PlanningIssue(
                    type=PlanningIssueType.STRUCTURAL_ERROR,
                    message=f"Dependency references unknown upstream task: {dep.upstream_id}",
                    severity="error",
                ))
            if dep.downstream_id not in task_ids:
                issues.append(PlanningIssue(
                    type=PlanningIssueType.STRUCTURAL_ERROR,
                    message=f"Dependency references unknown downstream task: {dep.downstream_id}",
                    severity="error",
                ))
            if dep.upstream_id == dep.downstream_id:
                issues.append(PlanningIssue(
                    type=PlanningIssueType.STRUCTURAL_ERROR,
                    message=f"Task cannot depend on itself: {dep.upstream_id}",
                    severity="error",
                ))
        
        # Check for cycles
        if not issues:  # Only check if no structural errors
            cycle = LLMPlanValidator._detect_cycle(output.tasks, output.dependencies)
            if cycle:
                issues.append(PlanningIssue(
                    type=PlanningIssueType.STRUCTURAL_ERROR,
                    message=f"Cyclic dependency detected: {' -> '.join(cycle)}",
                    severity="error",
                ))
        
        # Check for empty tasks
        for task in output.tasks:
            if not task.name.strip():
                issues.append(PlanningIssue(
                    type=PlanningIssueType.AMBIGUOUS_INTENT,
                    message=f"Task {task.id} has empty name",
                    severity="error",
                ))
        
        is_valid = not any(i.severity == "error" for i in issues)
        
        return LLMPlanValidationResult(is_valid=is_valid, issues=issues)
    
    @staticmethod
    def _detect_cycle(
        tasks: List[TaskProposal],
        dependencies: List[DependencyProposal],
    ) -> Optional[List[str]]:
        """
        Detect cycles in the dependency graph using DFS.
        
        Returns:
            List of task IDs forming the cycle, or None if no cycle.
        """
        # Build adjacency list
        graph: Dict[str, List[str]] = {t.id: [] for t in tasks}
        for dep in dependencies:
            if dep.upstream_id in graph:
                graph[dep.upstream_id].append(dep.downstream_id)
        
        # DFS with color marking
        WHITE, GRAY, BLACK = 0, 1, 2
        color: Dict[str, int] = {t.id: WHITE for t in tasks}
        parent: Dict[str, Optional[str]] = {t.id: None for t in tasks}
        
        def dfs(node: str) -> Optional[List[str]]:
            color[node] = GRAY
            for neighbor in graph.get(node, []):
                if neighbor not in color:
                    continue
                if color[neighbor] == GRAY:
                    # Found cycle, reconstruct
                    cycle = [neighbor]
                    current = node
                    while current != neighbor:
                        cycle.append(current)
                        current = parent.get(current)
                        if current is None:
                            break
                    cycle.append(neighbor)
                    return list(reversed(cycle))
                elif color[neighbor] == WHITE:
                    parent[neighbor] = node
                    result = dfs(neighbor)
                    if result:
                        return result
            color[node] = BLACK
            return None
        
        for task in tasks:
            if color[task.id] == WHITE:
                result = dfs(task.id)
                if result:
                    return result
        
        return None


# =============================================================================
# LLM Tactical Planner
# =============================================================================


class LLMTacticalPlanner:
    """
    LLM-backed Tactical Planner.
    
    This planner uses an LLM to propose TaskGraphs from TacticalIntent.
    It is ADVISORY only — all output must be validated before use.
    
    Key Properties:
    - Implements TacticalPlanner protocol
    - Falls back to RuleBasedTacticalPlanner on failure
    - All output labeled "[AI GENERATED PLAN – NOT FINAL]"
    - No execution, no approval, no Canon modification
    
    Architectural Position:
    - LLM proposes plans
    - Strata validates structure
    - Archon reviews strategy
    - Humans authorize execution
    """
    
    # Label applied to all LLM-generated plans
    AI_GENERATED_LABEL = "[AI GENERATED PLAN – NOT FINAL]"
    
    def __init__(
        self,
        llm_backend: Optional[LLMBackend] = None,
        fallback_planner: Optional[TacticalPlanner] = None,
        enable_llm: bool = True,
    ):
        """
        Initialize the LLM Tactical Planner.
        
        Args:
            llm_backend: The LLM backend to use. If None, LLM is disabled.
            fallback_planner: Fallback planner. Defaults to RuleBasedTacticalPlanner.
            enable_llm: Whether to use LLM. If False, always use fallback.
        """
        self._llm_backend = llm_backend
        self._fallback_planner = fallback_planner or RuleBasedTacticalPlanner()
        self._enable_llm = enable_llm
    
    def plan(
        self,
        intent: TacticalIntent,
        context: PlanningContext,
        hints: Optional[LLMPlanningHints] = None,
    ) -> PlanningResult:
        """
        Generate a TaskGraph based on the provided intent.
        
        This method:
        1. Attempts LLM-based planning if enabled and available
        2. Falls back to rule-based planning on failure
        3. Labels all LLM-generated plans appropriately
        
        Args:
            intent: The description of what needs to be done.
            context: The knowledge artifacts available for planning.
            hints: Optional hints to guide LLM planning.
            
        Returns:
            PlanningResult with the generated plan or issues.
        """
        # Check if LLM should be used
        llm_skip_reason = self._get_llm_skip_reason()
        if llm_skip_reason:
            return self._use_fallback(intent, context, llm_skip_reason)
        
        # Attempt LLM planning
        try:
            result = self._plan_with_llm(intent, context, hints or LLMPlanningHints())
            
            if result.success and result.graph:
                return result
            else:
                # LLM planning failed, try fallback
                return self._use_fallback(
                    intent, context,
                    f"LLM planning failed: {result.issues[0].message if result.issues else 'unknown'}"
                )
        
        except LLMUnavailableError as e:
            return self._use_fallback(intent, context, f"LLM unavailable: {e}")
        
        except Exception as e:
            # Catch-all for unexpected errors — fail safely
            return self._use_fallback(intent, context, f"Unexpected error: {e}")
    
    def _should_use_llm(self) -> bool:
        """Check if LLM should be used."""
        return self._get_llm_skip_reason() is None
    
    def _get_llm_skip_reason(self) -> str | None:
        """
        Get the reason why LLM should not be used, or None if LLM should be used.
        
        Returns:
            A reason string if LLM should be skipped, None otherwise.
        """
        if not self._enable_llm:
            return "LLM disabled"
        if not self._llm_backend:
            return "No LLM backend configured"
        if not self._llm_backend.is_available():
            return "LLM unavailable"
        return None
    
    def _use_fallback(
        self,
        intent: TacticalIntent,
        context: PlanningContext,
        reason: str,
    ) -> PlanningResult:
        """
        Use the fallback planner.
        
        Args:
            intent: The intent to plan.
            context: The planning context.
            reason: Why fallback was used.
            
        Returns:
            PlanningResult from the fallback planner.
        """
        result = self._fallback_planner.plan(intent, context)
        
        # Add info issue about fallback
        result.issues.append(PlanningIssue(
            type=PlanningIssueType.UNSUPPORTED_OPERATION,
            message=f"Used rule-based fallback: {reason}",
            severity="warning",
            context={"fallback_reason": reason},
        ))
        
        return result
    
    def _plan_with_llm(
        self,
        intent: TacticalIntent,
        context: PlanningContext,
        hints: LLMPlanningHints,
    ) -> PlanningResult:
        """
        Attempt to plan using the LLM.
        
        Args:
            intent: The intent to plan.
            context: The planning context.
            hints: Hints to guide planning.
            
        Returns:
            PlanningResult from LLM planning.
        """
        # 1. Build input
        planning_input = LLMPlanningInput(
            intent=intent,
            context_summary=self._summarize_context(context),
            hints=hints,
        )
        
        # 2. Call LLM
        prompt = planning_input.to_prompt()
        raw_response = self._llm_backend.generate(prompt)
        
        # 3. Parse response
        parse_result = LLMOutputParser.parse(raw_response)
        
        if not parse_result.success:
            return PlanningResult(
                graph=None,
                issues=[PlanningIssue(
                    type=PlanningIssueType.STRUCTURAL_ERROR,
                    message=f"Failed to parse LLM response: {parse_result.error}",
                    severity="error",
                    context={"raw_response": raw_response[:500]},
                )],
            )
        
        llm_output = parse_result.output
        
        # 4. Validate LLM output
        validation_result = LLMPlanValidator.validate(llm_output, context)
        
        if not validation_result.is_valid:
            return PlanningResult(
                graph=None,
                issues=validation_result.issues,
            )
        
        # 5. Convert to TaskGraph
        graph = self._convert_to_task_graph(llm_output, intent)
        
        # 6. Build result with explanation
        issues: List[PlanningIssue] = []
        
        # Add warnings from parsing
        for warning in parse_result.warnings:
            issues.append(PlanningIssue(
                type=PlanningIssueType.UNSUPPORTED_OPERATION,
                message=warning,
                severity="warning",
            ))
        
        # Add uncertainties as warnings
        for uncertainty in llm_output.explanation.uncertainties:
            issues.append(PlanningIssue(
                type=PlanningIssueType.AMBIGUOUS_INTENT,
                message=f"LLM uncertainty: {uncertainty}",
                severity="warning",
            ))
        
        # Add low confidence warning
        if llm_output.confidence == LLMConfidenceLevel.LOW:
            issues.append(PlanningIssue(
                type=PlanningIssueType.AMBIGUOUS_INTENT,
                message="LLM reported LOW confidence — careful human review advised",
                severity="warning",
            ))
        
        return PlanningResult(
            graph=graph,
            issues=issues,
        )
    
    def _summarize_context(self, context: PlanningContext) -> str:
        """
        Create a summary of the planning context for the LLM.
        
        This is intentionally brief to avoid overwhelming the LLM
        and to maintain security (no raw artifact dumps).
        
        Args:
            context: The planning context.
            
        Returns:
            Brief summary string.
        """
        lines = [
            f"Project root: {context.project_root}",
        ]
        
        # CPKG summary (minimal)
        if context.cpkg.nodes:
            lines.append(f"CPKG nodes: {len(context.cpkg.nodes)} entries")
            # List a few node types if available
            node_types = set()
            for node in list(context.cpkg.nodes.values())[:10]:
                node_types.add(getattr(node, 'type', 'unknown'))
            if node_types:
                lines.append(f"Node types: {', '.join(node_types)}")
        
        # UCIR summary (minimal)
        if context.ucir.constraints:
            lines.append(f"UCIR constraints: {len(context.ucir.constraints)} defined")
            # List first few constraint IDs
            constraint_ids = list(context.ucir.constraints.keys())[:5]
            if constraint_ids:
                lines.append(f"Sample constraints: {', '.join(constraint_ids)}")
        
        return "\n".join(lines)
    
    def _convert_to_task_graph(
        self,
        output: LLMPlanningOutput,
        intent: TacticalIntent,
    ) -> TaskGraph:
        """
        Convert LLMPlanningOutput to a Canon TaskGraph.
        
        Args:
            output: The validated LLM output.
            intent: The original intent.
            
        Returns:
            A TaskGraph conforming to Canon schema.
        """
        graph_id = f"llm-graph-{uuid.uuid4()}"
        
        # Convert tasks
        tasks: Dict[str, TaskNode] = {}
        for proposal in output.tasks:
            task = TaskNode(
                id=proposal.id,
                name=proposal.name,
                description=proposal.description,
                command=proposal.command,
                args=proposal.args,
                timeout_seconds=proposal.timeout_seconds,
                status=TaskStatus.PENDING,
            )
            tasks[task.id] = task
        
        # Convert dependencies
        dependencies: List[TaskDependency] = []
        for dep in output.dependencies:
            dependencies.append(TaskDependency(
                upstream_task_id=dep.upstream_id,
                downstream_task_id=dep.downstream_id,
            ))
        
        # Build metadata with AI labeling
        metadata = {
            "intent_id": intent.id,
            "source": "llm_tactical_planner",
            "label": self.AI_GENERATED_LABEL,
            "confidence": output.confidence.value,
            "explanation": {
                "reasoning": output.explanation.reasoning,
                "assumptions": output.explanation.assumptions,
                "uncertainties": output.explanation.uncertainties,
            },
        }
        
        return TaskGraph(
            id=graph_id,
            tasks=tasks,
            dependencies=dependencies,
            metadata=metadata,
        )
    
    def get_explanation(self, result: PlanningResult) -> Optional[PlanningExplanation]:
        """
        Extract the LLM's explanation from a planning result.
        
        Args:
            result: The planning result.
            
        Returns:
            The explanation, or None if not available.
        """
        if not result.graph:
            return None
        
        explanation_data = result.graph.metadata.get("explanation")
        if not explanation_data:
            return None
        
        return PlanningExplanation(
            reasoning=explanation_data.get("reasoning", ""),
            assumptions=explanation_data.get("assumptions", []),
            uncertainties=explanation_data.get("uncertainties", []),
        )
    
    def is_llm_generated(self, result: PlanningResult) -> bool:
        """
        Check if a planning result was generated by the LLM.
        
        Args:
            result: The planning result.
            
        Returns:
            True if the plan was LLM-generated.
        """
        if not result.graph:
            return False
        
        return result.graph.metadata.get("source") == "llm_tactical_planner"


# =============================================================================
# Mock LLM Backend (for testing)
# =============================================================================


class MockLLMBackend:
    """
    Mock LLM backend for testing.
    
    Returns pre-configured responses based on input patterns.
    """
    
    def __init__(
        self,
        available: bool = True,
        responses: Optional[Dict[str, str]] = None,
        default_response: Optional[str] = None,
    ):
        """
        Initialize mock backend.
        
        Args:
            available: Whether the backend is available.
            responses: Pattern-to-response mapping.
            default_response: Default response if no pattern matches.
        """
        self._available = available
        self._responses = responses or {}
        self._default_response = default_response
        self._last_prompt: Optional[str] = None
    
    def generate(self, prompt: str) -> str:
        """Generate a mock response."""
        self._last_prompt = prompt
        
        if not self._available:
            raise LLMUnavailableError("Mock LLM is unavailable")
        
        # Check for pattern matches
        for pattern, response in self._responses.items():
            if pattern.lower() in prompt.lower():
                return response
        
        # Return default or empty
        if self._default_response:
            return self._default_response
        
        return ""
    
    def is_available(self) -> bool:
        """Check availability."""
        return self._available
    
    def get_last_prompt(self) -> Optional[str]:
        """Get the last prompt sent to the backend."""
        return self._last_prompt
