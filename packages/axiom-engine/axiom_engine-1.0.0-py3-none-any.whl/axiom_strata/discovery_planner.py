"""
Discovery-Mode Tactical Planner.

This module extends the Tactical Layer with a Discovery mode that:
- Accepts intents for documentation and analysis
- Generates DISCOVERY-ONLY TaskGraphs
- Assigns scoped discovery tasks to executors
- Never schedules EXECUTION tasks in this mode

CORE PRINCIPLE: No heuristics, no autonomy, no execution.

This planner helps humans understand codebases by:
1. Decomposing documentation intents into analysis tasks
2. Scoping tasks to prevent runaway LLM usage
3. Coordinating evidence gathering across components
4. Never making decisions about truth
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import hashlib

from axiom_canon.discovery import (
    DiscoveryDependency,
    DiscoveryScope,
    DiscoveryTask,
    DiscoveryTaskGraph,
    DiscoveryTaskType,
)
from axiom_canon.ingestion.models import (
    ComponentSummary,
    IngestionResult,
    ModuleSummary,
)


# =============================================================================
# Discovery Intent Models
# =============================================================================


class DiscoveryIntentType(str, Enum):
    """
    Type of discovery intent.
    
    These are the high-level goals a human might have.
    """
    
    DOCUMENT_COMPONENT = "document_component"       # Document a component
    DOCUMENT_SUBSYSTEM = "document_subsystem"       # Document multiple components
    EXPLAIN_ARCHITECTURE = "explain_architecture"   # Explain system architecture
    FIND_INVARIANTS = "find_invariants"             # Find implicit invariants
    EXPLAIN_DEPENDENCIES = "explain_dependencies"   # Explain why deps exist
    DOCUMENT_API = "document_api"                   # Document API surface


@dataclass
class DiscoveryIntent:
    """
    A human-specified intent for discovery.
    
    This is what the human wants to understand or document.
    
    Attributes:
        intent_type: Type of discovery intent.
        description: Human-readable description.
        target_components: Component IDs to analyze.
        target_modules: Module IDs to analyze.
        focus_areas: Specific areas of focus.
        scope_limit: Maximum scope for generated tasks.
    """
    
    intent_type: DiscoveryIntentType
    description: str
    target_components: List[str] = field(default_factory=list)
    target_modules: List[str] = field(default_factory=list)
    focus_areas: List[str] = field(default_factory=list)
    scope_limit: Optional[DiscoveryScope] = None
    
    def validate(self) -> List[str]:
        """Validate intent."""
        errors = []
        
        if not self.description:
            errors.append("Intent description is required")
        
        if not self.target_components and not self.target_modules:
            errors.append("At least one target component or module is required")
        
        if self.scope_limit:
            scope_errors = self.scope_limit.validate()
            errors.extend(scope_errors)
        
        return errors


# =============================================================================
# Planning Configuration
# =============================================================================


@dataclass
class DiscoveryPlannerConfig:
    """
    Configuration for discovery planner.
    
    Attributes:
        max_tasks_per_graph: Maximum tasks in a single graph.
        default_max_files: Default max files per task.
        default_max_tokens_per_file: Default max tokens per file.
        default_max_total_tokens: Default max total tokens per task.
        default_timeout_seconds: Default task timeout.
    """
    
    max_tasks_per_graph: int = 20
    default_max_files: int = 5
    default_max_tokens_per_file: int = 1500
    default_max_total_tokens: int = 5000
    default_timeout_seconds: int = 45


# =============================================================================
# Discovery Planner Protocol
# =============================================================================


class DiscoveryPlanner(ABC):
    """
    Abstract base class for discovery planners.
    
    Discovery planners:
    - Accept human intents
    - Generate DISCOVERY-ONLY TaskGraphs
    - Never produce EXECUTION tasks
    """
    
    @abstractmethod
    def plan(
        self,
        intent: DiscoveryIntent,
        ingestion_result: IngestionResult,
    ) -> DiscoveryTaskGraph:
        """
        Generate a discovery task graph from an intent.
        
        Args:
            intent: The human's discovery intent.
            ingestion_result: Current Canon ingestion data.
            
        Returns:
            A discovery task graph.
        """
        ...


# =============================================================================
# Rule-Based Discovery Planner
# =============================================================================


class RuleBasedDiscoveryPlanner(DiscoveryPlanner):
    """
    Rule-based discovery planner.
    
    Uses deterministic rules to decompose intents into tasks.
    No LLM involvement in planning itself.
    """
    
    def __init__(
        self,
        config: Optional[DiscoveryPlannerConfig] = None,
    ) -> None:
        """Initialize planner with configuration."""
        self._config = config or DiscoveryPlannerConfig()
    
    def plan(
        self,
        intent: DiscoveryIntent,
        ingestion_result: IngestionResult,
    ) -> DiscoveryTaskGraph:
        """
        Generate a discovery task graph from an intent.
        
        Args:
            intent: The human's discovery intent.
            ingestion_result: Current Canon ingestion data.
            
        Returns:
            A discovery task graph.
        """
        # Validate intent
        errors = intent.validate()
        if errors:
            raise ValueError(f"Invalid intent: {errors}")
        
        # Generate graph ID
        graph_id = f"discovery_{hashlib.sha256(intent.description.encode()).hexdigest()[:12]}"
        
        # Create graph
        graph = DiscoveryTaskGraph(
            id=graph_id,
            intent=intent.description,
            metadata={
                "intent_type": intent.intent_type.value,
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        
        # Dispatch to appropriate planning method
        if intent.intent_type == DiscoveryIntentType.DOCUMENT_COMPONENT:
            self._plan_component_documentation(graph, intent, ingestion_result)
        elif intent.intent_type == DiscoveryIntentType.DOCUMENT_SUBSYSTEM:
            self._plan_subsystem_documentation(graph, intent, ingestion_result)
        elif intent.intent_type == DiscoveryIntentType.EXPLAIN_ARCHITECTURE:
            self._plan_architecture_explanation(graph, intent, ingestion_result)
        elif intent.intent_type == DiscoveryIntentType.FIND_INVARIANTS:
            self._plan_invariant_discovery(graph, intent, ingestion_result)
        elif intent.intent_type == DiscoveryIntentType.EXPLAIN_DEPENDENCIES:
            self._plan_dependency_explanation(graph, intent, ingestion_result)
        elif intent.intent_type == DiscoveryIntentType.DOCUMENT_API:
            self._plan_api_documentation(graph, intent, ingestion_result)
        else:
            # Default: simple component analysis
            self._plan_component_documentation(graph, intent, ingestion_result)
        
        return graph
    
    def _get_default_scope(self, intent: DiscoveryIntent) -> DiscoveryScope:
        """Get default scope, overridden by intent scope if provided."""
        if intent.scope_limit:
            return intent.scope_limit
        
        return DiscoveryScope(
            max_files=self._config.default_max_files,
            max_tokens_per_file=self._config.default_max_tokens_per_file,
            max_total_tokens=self._config.default_max_total_tokens,
        )
    
    def _get_component_files(
        self,
        component_id: str,
        ingestion_result: IngestionResult,
    ) -> List[str]:
        """Get file paths for a component."""
        for comp in ingestion_result.components:
            if comp.id == component_id:
                return [m.path for m in comp.modules]
        return []
    
    def _get_module_file(
        self,
        module_id: str,
        ingestion_result: IngestionResult,
    ) -> Optional[str]:
        """Get file path for a module."""
        for module in ingestion_result.modules:
            if module.id == module_id:
                return module.path
        return None
    
    def _plan_component_documentation(
        self,
        graph: DiscoveryTaskGraph,
        intent: DiscoveryIntent,
        ingestion_result: IngestionResult,
    ) -> None:
        """Plan tasks for documenting components."""
        task_count = 0
        
        for comp_id in intent.target_components:
            if task_count >= self._config.max_tasks_per_graph:
                break
            
            files = self._get_component_files(comp_id, ingestion_result)
            if not files:
                continue
            
            # Create scope with component's files
            scope = self._get_default_scope(intent)
            scope.file_paths = files[:scope.max_files]
            
            # Create analysis task
            task = DiscoveryTask(
                id=f"doc_comp_{comp_id}_{task_count}",
                name=f"Document component: {comp_id}",
                description=f"Analyze and document the purpose and responsibilities of component {comp_id}",
                task_type=DiscoveryTaskType.COMPONENT_ANALYSIS,
                scope=scope,
                target_artifact_ids=[comp_id],
                focus_question="What is the primary responsibility of this component?",
                timeout_seconds=self._config.default_timeout_seconds,
            )
            
            graph.add_task(task)
            task_count += 1
    
    def _plan_subsystem_documentation(
        self,
        graph: DiscoveryTaskGraph,
        intent: DiscoveryIntent,
        ingestion_result: IngestionResult,
    ) -> None:
        """Plan tasks for documenting a subsystem (multiple components)."""
        # First, plan individual component docs
        self._plan_component_documentation(graph, intent, ingestion_result)
        
        # Then add a synthesis task if multiple components
        if len(intent.target_components) > 1:
            # Collect all files across components (limited)
            all_files = []
            for comp_id in intent.target_components:
                files = self._get_component_files(comp_id, ingestion_result)
                all_files.extend(files[:2])  # Limit per component
            
            scope = self._get_default_scope(intent)
            scope.file_paths = all_files[:scope.max_files]
            
            synthesis_task = DiscoveryTask(
                id=f"synthesize_subsystem_{len(graph.tasks)}",
                name="Synthesize subsystem documentation",
                description="Analyze how the components work together as a subsystem",
                task_type=DiscoveryTaskType.PATTERN_RECOGNITION,
                scope=scope,
                target_artifact_ids=intent.target_components,
                focus_question="How do these components collaborate?",
                timeout_seconds=self._config.default_timeout_seconds,
            )
            
            # Add dependencies: synthesis depends on all component tasks
            for task_id in list(graph.tasks.keys()):
                graph.add_dependency(task_id, synthesis_task.id)
            
            graph.add_task(synthesis_task)
    
    def _plan_architecture_explanation(
        self,
        graph: DiscoveryTaskGraph,
        intent: DiscoveryIntent,
        ingestion_result: IngestionResult,
    ) -> None:
        """Plan tasks for explaining architecture."""
        task_count = 0
        
        # Analyze high-level structure
        if ingestion_result.components:
            # Get entry points and key modules
            entry_files = []
            for comp in ingestion_result.components:
                for ep in comp.entry_points[:1]:  # One entry point per component
                    for module in comp.modules:
                        if ep.module in module.path or ep.module == module.name:
                            entry_files.append(module.path)
                            break
            
            if entry_files:
                scope = self._get_default_scope(intent)
                scope.file_paths = entry_files[:scope.max_files]
                
                arch_task = DiscoveryTask(
                    id=f"arch_overview_{task_count}",
                    name="Analyze system architecture",
                    description="Analyze the high-level architecture and entry points",
                    task_type=DiscoveryTaskType.PATTERN_RECOGNITION,
                    scope=scope,
                    target_artifact_ids=[c.id for c in ingestion_result.components[:5]],
                    focus_question="What is the overall architectural pattern?",
                    timeout_seconds=self._config.default_timeout_seconds,
                )
                
                graph.add_task(arch_task)
                task_count += 1
        
        # Then analyze individual components
        self._plan_component_documentation(graph, intent, ingestion_result)
    
    def _plan_invariant_discovery(
        self,
        graph: DiscoveryTaskGraph,
        intent: DiscoveryIntent,
        ingestion_result: IngestionResult,
    ) -> None:
        """Plan tasks for discovering implicit invariants."""
        task_count = 0
        
        for comp_id in intent.target_components:
            if task_count >= self._config.max_tasks_per_graph:
                break
            
            files = self._get_component_files(comp_id, ingestion_result)
            if not files:
                continue
            
            scope = self._get_default_scope(intent)
            scope.file_paths = files[:scope.max_files]
            
            task = DiscoveryTask(
                id=f"find_inv_{comp_id}_{task_count}",
                name=f"Find invariants in: {comp_id}",
                description=f"Analyze component {comp_id} for implicit invariants and constraints",
                task_type=DiscoveryTaskType.INVARIANT_DISCOVERY,
                scope=scope,
                target_artifact_ids=[comp_id],
                focus_question="What implicit rules or constraints govern this code?",
                timeout_seconds=self._config.default_timeout_seconds,
            )
            
            graph.add_task(task)
            task_count += 1
    
    def _plan_dependency_explanation(
        self,
        graph: DiscoveryTaskGraph,
        intent: DiscoveryIntent,
        ingestion_result: IngestionResult,
    ) -> None:
        """Plan tasks for explaining dependencies."""
        task_count = 0
        
        for comp_id in intent.target_components:
            if task_count >= self._config.max_tasks_per_graph:
                break
            
            files = self._get_component_files(comp_id, ingestion_result)
            if not files:
                continue
            
            scope = self._get_default_scope(intent)
            scope.file_paths = files[:scope.max_files]
            
            task = DiscoveryTask(
                id=f"explain_deps_{comp_id}_{task_count}",
                name=f"Explain dependencies of: {comp_id}",
                description=f"Analyze why component {comp_id} has its dependencies",
                task_type=DiscoveryTaskType.DEPENDENCY_ANALYSIS,
                scope=scope,
                target_artifact_ids=[comp_id],
                focus_question="Why do these dependencies exist?",
                timeout_seconds=self._config.default_timeout_seconds,
            )
            
            graph.add_task(task)
            task_count += 1
    
    def _plan_api_documentation(
        self,
        graph: DiscoveryTaskGraph,
        intent: DiscoveryIntent,
        ingestion_result: IngestionResult,
    ) -> None:
        """Plan tasks for documenting API surface."""
        task_count = 0
        
        for comp_id in intent.target_components:
            if task_count >= self._config.max_tasks_per_graph:
                break
            
            # Find modules with exports
            files_with_exports = []
            for comp in ingestion_result.components:
                if comp.id == comp_id:
                    for module in comp.modules:
                        if module.exports:
                            files_with_exports.append(module.path)
            
            if not files_with_exports:
                continue
            
            scope = self._get_default_scope(intent)
            scope.file_paths = files_with_exports[:scope.max_files]
            
            task = DiscoveryTask(
                id=f"doc_api_{comp_id}_{task_count}",
                name=f"Document API of: {comp_id}",
                description=f"Document the public API surface of component {comp_id}",
                task_type=DiscoveryTaskType.BEHAVIOR_INFERENCE,
                scope=scope,
                target_artifact_ids=[comp_id],
                focus_question="What is the public API contract?",
                timeout_seconds=self._config.default_timeout_seconds,
            )
            
            graph.add_task(task)
            task_count += 1


# =============================================================================
# Validation Functions
# =============================================================================


def validate_discovery_graph_has_no_execution(graph: DiscoveryTaskGraph) -> List[str]:
    """
    Validate that a discovery graph has no execution tasks.
    
    Discovery graphs MUST:
    - Contain ONLY DiscoveryTask objects
    - Have no shell commands
    - Have no file mutations
    
    Args:
        graph: The graph to validate.
        
    Returns:
        List of validation errors (empty if valid).
    """
    errors = []
    
    for task_id, task in graph.tasks.items():
        # Verify task is a DiscoveryTask (by checking type)
        if not isinstance(task, DiscoveryTask):
            errors.append(f"Task {task_id} is not a DiscoveryTask")
        
        # Verify scope limits are reasonable
        task_errors = task.validate()
        for err in task_errors:
            errors.append(f"Task {task_id}: {err}")
    
    return errors


def validate_intent_has_targets(intent: DiscoveryIntent) -> bool:
    """
    Validate that an intent has targets to analyze.
    
    Args:
        intent: The intent to validate.
        
    Returns:
        True if intent has targets.
    """
    return bool(intent.target_components or intent.target_modules)
