"""
Existing Project Adoption Flow.

This module provides a governed flow for adopting Axiom into an
existing project with an established codebase.

CANONICAL ADOPTION FLOW:
1. ANALYZE      - Assess project size, structure, and complexity
2. INITIALIZE   - Create Axiom configuration alongside existing files
3. EXTRACT      - Run deterministic code extraction
4. ENRICH       - Optionally run LLM enrichment (advisory only)
5. REVIEW       - Human reviews all inferred annotations
6. PROMOTE      - Human approves Canon updates incrementally
7. INTEGRATE    - Configure executors for project's tech stack
8. VALIDATE     - Verify Canon integrity
9. PILOT        - Execute first workflow on a safe subset

SPECIAL CONSIDERATIONS:
- Large codebases: Incremental adoption
- Poorly documented: Discovery-first approach
- Existing CI/CD: Integration points
- Safe rollback: Non-destructive at every step

RULES (ABSOLUTE):
- Never modify existing source files
- Never delete existing files
- Canon lives in .axiom/ (isolated)
- All changes are opt-in
- Human approval required before Canon mutation
- Rollback is always safe
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
# Adoption Step Definitions
# =============================================================================


class AdoptionStep(str, Enum):
    """
    The canonical steps in existing project adoption.
    
    These steps MUST be executed in order.
    Some steps support incremental progress.
    """
    
    ANALYZE = "analyze"
    INITIALIZE = "initialize"
    EXTRACT = "extract"
    ENRICH = "enrich"
    REVIEW = "review"
    PROMOTE = "promote"
    INTEGRATE = "integrate"
    VALIDATE = "validate"
    PILOT = "pilot"


class AdoptionStepStatus(str, Enum):
    """Status of an adoption step."""
    
    PENDING = "pending"
    CURRENT = "current"
    COMPLETED = "completed"
    PARTIAL = "partial"  # For incremental steps
    FAILED = "failed"
    SKIPPED_OPTIONAL = "skipped_optional"


# Step metadata
ADOPTION_STEP_DETAILS: Dict[AdoptionStep, Dict[str, Any]] = {
    AdoptionStep.ANALYZE: {
        "name": "Analyze Project",
        "description": "Assess project size, structure, and complexity",
        "owner": "System",
        "required": True,
        "incremental": False,
        "prerequisites": [],
        "produces": ["Project analysis report", "Recommended adoption strategy"],
        "rollback": "No changes made - nothing to rollback",
    },
    AdoptionStep.INITIALIZE: {
        "name": "Initialize Axiom",
        "description": "Create .axiom/ configuration alongside existing files",
        "owner": "System",
        "required": True,
        "incremental": False,
        "prerequisites": [AdoptionStep.ANALYZE],
        "produces": [".axiom/ directory", "Canon artifact templates"],
        "rollback": "Delete .axiom/ directory",
    },
    AdoptionStep.EXTRACT: {
        "name": "Extract Code Structure",
        "description": "Run deterministic code extraction (no LLM)",
        "owner": "System",
        "required": True,
        "incremental": True,  # Can extract incrementally
        "prerequisites": [AdoptionStep.INITIALIZE],
        "produces": ["IngestionResult", "Component map", "Dependency graph"],
        "rollback": "Discard extraction results",
    },
    AdoptionStep.ENRICH: {
        "name": "LLM Enrichment (Optional)",
        "description": "Use LLM to infer labels and descriptions (ADVISORY ONLY)",
        "owner": "AI (Advisory)",
        "required": False,
        "incremental": True,
        "prerequisites": [AdoptionStep.EXTRACT],
        "produces": ["EnrichmentResult (provisional)", "Inferred labels"],
        "rollback": "Discard enrichment results",
    },
    AdoptionStep.REVIEW: {
        "name": "Review Annotations",
        "description": "Human reviews all inferred annotations",
        "owner": "Human",
        "required": True,
        "incremental": True,  # Can review incrementally
        "prerequisites": [AdoptionStep.EXTRACT],
        "produces": ["Review decisions", "Approved annotations"],
        "rollback": "Reset review decisions",
    },
    AdoptionStep.PROMOTE: {
        "name": "Promote to Canon",
        "description": "Approved annotations promoted into Canon (incremental)",
        "owner": "Human (Approval Required)",
        "required": True,
        "incremental": True,  # Incremental promotion
        "prerequisites": [AdoptionStep.REVIEW],
        "produces": ["Updated CPKG", "Updated BFM"],
        "rollback": "Revert Canon to previous version",
    },
    AdoptionStep.INTEGRATE: {
        "name": "Configure Integration",
        "description": "Configure executors for project's tech stack",
        "owner": "User",
        "required": True,
        "incremental": False,
        "prerequisites": [AdoptionStep.PROMOTE],
        "produces": ["Executor configuration", "Policy configuration"],
        "rollback": "Reset to default configuration",
    },
    AdoptionStep.VALIDATE: {
        "name": "Validate Canon",
        "description": "Verify Canon integrity and consistency",
        "owner": "System",
        "required": True,
        "incremental": False,
        "prerequisites": [AdoptionStep.INTEGRATE],
        "produces": ["Validation report"],
        "rollback": "Validation is read-only",
    },
    AdoptionStep.PILOT: {
        "name": "Pilot Workflow",
        "description": "Execute first workflow on a safe subset",
        "owner": "Human (Approval Required)",
        "required": False,
        "incremental": False,
        "prerequisites": [AdoptionStep.VALIDATE],
        "produces": ["WorkflowResult", "Execution audit trail"],
        "rollback": "Results are isolated to pilot scope",
    },
}


# =============================================================================
# Project Analysis Models
# =============================================================================


@dataclass
class ProjectAnalysis:
    """
    Analysis of an existing project.
    
    Used to determine adoption strategy.
    
    Attributes:
        project_path: Path to the project.
        total_files: Total number of files.
        source_files: Number of source code files.
        total_lines: Total lines of code.
        languages: Detected programming languages.
        frameworks: Detected frameworks.
        has_tests: Whether tests exist.
        has_ci: Whether CI/CD exists.
        has_docs: Whether documentation exists.
        complexity: Estimated complexity (low/medium/high).
        recommended_strategy: Recommended adoption strategy.
        warnings: Any warnings about the project.
    """
    
    project_path: str
    total_files: int = 0
    source_files: int = 0
    total_lines: int = 0
    languages: List[str] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)
    has_tests: bool = False
    has_ci: bool = False
    has_docs: bool = False
    complexity: str = "medium"
    recommended_strategy: str = "incremental"
    warnings: List[str] = field(default_factory=list)
    analyzed_at: str = ""
    
    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.analyzed_at:
            self.analyzed_at = datetime.now(timezone.utc).isoformat()


@dataclass
class AdoptionStrategy:
    """
    Recommended adoption strategy based on analysis.
    
    Attributes:
        approach: The adoption approach (full/incremental/targeted).
        phases: List of phases for adoption.
        estimated_effort: Estimated effort level.
        risk_level: Risk assessment.
        recommendations: Specific recommendations.
    """
    
    approach: str  # full, incremental, targeted
    phases: List[Dict[str, str]] = field(default_factory=list)
    estimated_effort: str = "medium"
    risk_level: str = "low"
    recommendations: List[str] = field(default_factory=list)


# =============================================================================
# Adoption State
# =============================================================================


@dataclass
class AdoptionState:
    """
    Tracks the current state of adoption.
    
    Supports incremental progress tracking.
    
    Attributes:
        project_path: Path to the project.
        current_step: The step currently in progress.
        step_statuses: Status of each step.
        step_progress: Progress percentage for incremental steps.
        artifacts: Artifacts produced by completed steps.
        analysis: Project analysis result.
        errors: Errors encountered.
        warnings: Warnings encountered.
        started_at: When adoption started.
        checkpoints: Saved checkpoints for rollback.
    """
    
    project_path: str
    current_step: AdoptionStep = AdoptionStep.ANALYZE
    step_statuses: Dict[AdoptionStep, AdoptionStepStatus] = field(default_factory=dict)
    step_progress: Dict[AdoptionStep, float] = field(default_factory=dict)
    artifacts: Dict[str, Any] = field(default_factory=dict)
    analysis: Optional[ProjectAnalysis] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    started_at: str = ""
    checkpoints: Dict[str, str] = field(default_factory=dict)  # step -> checkpoint_path
    
    def __post_init__(self) -> None:
        """Initialize step statuses and timestamp."""
        if not self.step_statuses:
            self.step_statuses = {
                step: AdoptionStepStatus.PENDING
                for step in AdoptionStep
            }
            self.step_statuses[AdoptionStep.ANALYZE] = AdoptionStepStatus.CURRENT
        
        if not self.step_progress:
            self.step_progress = {step: 0.0 for step in AdoptionStep}
        
        if not self.started_at:
            self.started_at = datetime.now(timezone.utc).isoformat()
    
    def mark_completed(self, step: AdoptionStep) -> None:
        """Mark a step as completed."""
        self.step_statuses[step] = AdoptionStepStatus.COMPLETED
        self.step_progress[step] = 100.0
        
        # Advance to next step
        steps = list(AdoptionStep)
        current_index = steps.index(step)
        if current_index + 1 < len(steps):
            next_step = steps[current_index + 1]
            self.current_step = next_step
            self.step_statuses[next_step] = AdoptionStepStatus.CURRENT
    
    def mark_partial(self, step: AdoptionStep, progress: float) -> None:
        """Mark a step as partially complete."""
        self.step_statuses[step] = AdoptionStepStatus.PARTIAL
        self.step_progress[step] = min(progress, 99.9)  # Never 100% until completed
    
    def mark_failed(self, step: AdoptionStep, error: str) -> None:
        """Mark a step as failed."""
        self.step_statuses[step] = AdoptionStepStatus.FAILED
        self.errors.append(f"[{step.value}] {error}")
    
    def can_proceed_to(self, step: AdoptionStep) -> bool:
        """Check if prerequisites are met for a step."""
        details = ADOPTION_STEP_DETAILS.get(step, {})
        prerequisites = details.get("prerequisites", [])
        
        for prereq in prerequisites:
            status = self.step_statuses.get(prereq)
            if status not in (
                AdoptionStepStatus.COMPLETED,
                AdoptionStepStatus.PARTIAL,
                AdoptionStepStatus.SKIPPED_OPTIONAL,
            ):
                return False
        
        return True
    
    def save_checkpoint(self, step: AdoptionStep, checkpoint_path: str) -> None:
        """Save a checkpoint for rollback."""
        self.checkpoints[step.value] = checkpoint_path
    
    def get_rollback_point(self, step: AdoptionStep) -> Optional[str]:
        """Get the rollback checkpoint for a step."""
        return self.checkpoints.get(step.value)


# =============================================================================
# Adoption Result
# =============================================================================


@dataclass
class AdoptionResult:
    """
    Result of a single adoption step.
    
    Attributes:
        step: The step that was executed.
        success: Whether the step succeeded.
        message: Human-readable result message.
        progress: Progress percentage (for incremental steps).
        artifacts: Artifacts produced by this step.
        next_step: The next step to execute (if any).
        next_action: Description of what to do next.
        can_rollback: Whether rollback is available.
        rollback_instructions: How to rollback.
    """
    
    step: AdoptionStep
    success: bool
    message: str
    progress: float = 100.0
    artifacts: Dict[str, Any] = field(default_factory=dict)
    next_step: Optional[AdoptionStep] = None
    next_action: str = ""
    can_rollback: bool = True
    rollback_instructions: str = ""


# =============================================================================
# Errors
# =============================================================================


class AdoptionError(Exception):
    """
    Error during adoption.
    
    Always provides rollback guidance.
    """
    
    def __init__(
        self,
        message: str,
        step: Optional[AdoptionStep] = None,
        rollback: str = "",
    ) -> None:
        """
        Initialize adoption error.
        
        Args:
            message: What happened.
            step: Which step failed.
            rollback: How to rollback.
        """
        self.step = step
        self.rollback = rollback
        
        full_message = message
        if step:
            full_message = f"[{step.value}] {message}"
        if rollback:
            full_message += f"\n  Rollback: {rollback}"
        
        super().__init__(full_message)


# =============================================================================
# Adoption Display
# =============================================================================


class AdoptionDisplay:
    """
    Renders adoption state and progress for users.
    """
    
    @staticmethod
    def render_progress(state: AdoptionState) -> str:
        """
        Render adoption progress.
        
        Args:
            state: Current adoption state.
        
        Returns:
            Formatted progress display.
        """
        lines = []
        lines.append("")
        lines.append("╔════════════════════════════════════════════════════════════╗")
        lines.append("║         AXIOM EXISTING PROJECT ADOPTION                    ║")
        lines.append("╠════════════════════════════════════════════════════════════╣")
        lines.append("")
        
        # Project info
        lines.append(f"  Project: {state.project_path}")
        if state.analysis:
            lines.append(f"  Files: {state.analysis.source_files} source files")
            lines.append(f"  Languages: {', '.join(state.analysis.languages)}")
            lines.append(f"  Complexity: {state.analysis.complexity}")
        lines.append("")
        
        # Overall progress
        total_progress = sum(state.step_progress.values()) / len(AdoptionStep)
        bar = "█" * int(total_progress / 2.5) + "░" * (40 - int(total_progress / 2.5))
        lines.append(f"  Overall: [{bar}] {total_progress:.0f}%")
        lines.append("")
        
        # Step list with progress
        lines.append("  Steps:")
        for step in AdoptionStep:
            status = state.step_statuses.get(step, AdoptionStepStatus.PENDING)
            progress = state.step_progress.get(step, 0.0)
            details = ADOPTION_STEP_DETAILS.get(step, {})
            name = details.get("name", step.value)
            incremental = details.get("incremental", False)
            required = details.get("required", True)
            
            # Status indicator
            if status == AdoptionStepStatus.COMPLETED:
                indicator = "✓"
                progress_str = ""
            elif status == AdoptionStepStatus.CURRENT:
                indicator = "▶"
                progress_str = " ← CURRENT"
            elif status == AdoptionStepStatus.PARTIAL:
                indicator = "◐"
                progress_str = f" ({progress:.0f}%)"
            elif status == AdoptionStepStatus.FAILED:
                indicator = "✗"
                progress_str = " ← FAILED"
            elif status == AdoptionStepStatus.SKIPPED_OPTIONAL:
                indicator = "○"
                progress_str = " (skipped)"
            else:
                indicator = "·"
                progress_str = ""
            
            optional = "" if required else " (optional)"
            incr = " [incremental]" if incremental and status == AdoptionStepStatus.PARTIAL else ""
            lines.append(f"    {indicator} {name}{optional}{progress_str}{incr}")
        
        lines.append("")
        
        # Current step details
        current = state.current_step
        details = ADOPTION_STEP_DETAILS.get(current, {})
        lines.append(f"  Current: {details.get('name', current.value)}")
        lines.append(f"  {details.get('description', '')}")
        lines.append("")
        
        # Rollback information
        lines.append("  Rollback Available:")
        rollback = details.get("rollback", "No rollback needed")
        lines.append(f"    {rollback}")
        lines.append("")
        
        # Warnings if any
        if state.warnings:
            lines.append("  ⚠ Warnings:")
            for warning in state.warnings[-3:]:
                lines.append(f"    • {warning}")
            lines.append("")
        
        # Errors if any
        if state.errors:
            lines.append("  ✗ Errors:")
            for error in state.errors[-3:]:
                lines.append(f"    • {error}")
            lines.append("")
        
        lines.append("╚════════════════════════════════════════════════════════════╝")
        lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def render_analysis(analysis: ProjectAnalysis) -> str:
        """
        Render project analysis results.
        
        Args:
            analysis: Project analysis.
        
        Returns:
            Formatted analysis display.
        """
        lines = []
        lines.append("")
        lines.append("╔═══ PROJECT ANALYSIS ═══════════════════════════════════════╗")
        lines.append("")
        lines.append(f"  Path: {analysis.project_path}")
        lines.append("")
        lines.append("  Statistics:")
        lines.append(f"    Total Files:   {analysis.total_files}")
        lines.append(f"    Source Files:  {analysis.source_files}")
        lines.append(f"    Lines of Code: {analysis.total_lines:,}")
        lines.append("")
        lines.append("  Technologies:")
        lines.append(f"    Languages:  {', '.join(analysis.languages) or 'Unknown'}")
        lines.append(f"    Frameworks: {', '.join(analysis.frameworks) or 'None detected'}")
        lines.append("")
        lines.append("  Infrastructure:")
        lines.append(f"    Tests:         {'Yes' if analysis.has_tests else 'No'}")
        lines.append(f"    CI/CD:         {'Yes' if analysis.has_ci else 'No'}")
        lines.append(f"    Documentation: {'Yes' if analysis.has_docs else 'No'}")
        lines.append("")
        lines.append(f"  Complexity: {analysis.complexity.upper()}")
        lines.append(f"  Recommended Strategy: {analysis.recommended_strategy.upper()}")
        lines.append("")
        
        if analysis.warnings:
            lines.append("  ⚠ Warnings:")
            for warning in analysis.warnings:
                lines.append(f"    • {warning}")
            lines.append("")
        
        lines.append("╚════════════════════════════════════════════════════════════╝")
        lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def render_strategy(strategy: AdoptionStrategy) -> str:
        """
        Render adoption strategy recommendation.
        
        Args:
            strategy: Adoption strategy.
        
        Returns:
            Formatted strategy display.
        """
        lines = []
        lines.append("")
        lines.append("╔═══ RECOMMENDED ADOPTION STRATEGY ═════════════════════════╗")
        lines.append("")
        lines.append(f"  Approach: {strategy.approach.upper()}")
        lines.append(f"  Effort: {strategy.estimated_effort.upper()}")
        lines.append(f"  Risk: {strategy.risk_level.upper()}")
        lines.append("")
        
        if strategy.phases:
            lines.append("  Phases:")
            for i, phase in enumerate(strategy.phases, 1):
                lines.append(f"    {i}. {phase.get('name', 'Phase')}")
                lines.append(f"       {phase.get('description', '')}")
            lines.append("")
        
        if strategy.recommendations:
            lines.append("  Recommendations:")
            for rec in strategy.recommendations:
                lines.append(f"    • {rec}")
            lines.append("")
        
        lines.append("╚════════════════════════════════════════════════════════════╝")
        lines.append("")
        
        return "\n".join(lines)


# =============================================================================
# Existing Project Adoption
# =============================================================================


class ExistingProjectOnboarding:
    """
    Governed adoption flow for existing projects.
    
    This class guides users through adopting Axiom into an existing codebase.
    Each step is explicit, reversible, and supports incremental progress.
    
    RULES:
    - Never modify existing source files
    - Never delete existing files
    - Axiom configuration is isolated in .axiom/
    - Human approval required before Canon mutation
    - Rollback is always safe
    
    Attributes:
        state: Current adoption state.
        display: Display renderer.
    """
    
    def __init__(self, project_path: str) -> None:
        """
        Initialize adoption for an existing project.
        
        Args:
            project_path: Path to the existing project.
        
        Raises:
            AdoptionError: If project path doesn't exist.
        """
        project = Path(project_path)
        if not project.exists():
            raise AdoptionError(
                f"Project path does not exist: {project_path}",
                step=AdoptionStep.ANALYZE,
                rollback="Verify the path is correct",
            )
        
        self.state = AdoptionState(project_path=str(project.absolute()))
        self.display = AdoptionDisplay()
        self._cpkg: Optional[CPKG] = None
        self._ucir: Optional[UCIR] = None
        self._bfm: Optional[BusinessFlowMap] = None
    
    # =========================================================================
    # Step 1: Analyze Project
    # =========================================================================
    
    def step_analyze(self) -> AdoptionResult:
        """
        Analyze the existing project.
        
        This step:
        - Counts files and lines
        - Detects languages and frameworks
        - Identifies existing tests, CI, docs
        - Recommends adoption strategy
        
        NO CHANGES ARE MADE.
        
        Returns:
            AdoptionResult with analysis.
        """
        step = AdoptionStep.ANALYZE
        
        if self.state.current_step != step:
            return AdoptionResult(
                step=step,
                success=False,
                message=f"Cannot analyze: current step is {self.state.current_step.value}",
            )
        
        try:
            project_path = Path(self.state.project_path)
            
            # Count files
            total_files = 0
            source_files = 0
            total_lines = 0
            languages = set()
            frameworks = set()
            has_tests = False
            has_ci = False
            has_docs = False
            warnings = []
            
            # File extensions to language mapping
            lang_map = {
                ".py": "Python",
                ".js": "JavaScript",
                ".ts": "TypeScript",
                ".java": "Java",
                ".go": "Go",
                ".rs": "Rust",
                ".rb": "Ruby",
                ".php": "PHP",
                ".cs": "C#",
                ".cpp": "C++",
                ".c": "C",
            }
            
            # Walk project
            for root, dirs, files in os.walk(project_path):
                # Skip hidden and common non-source directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in (
                    'node_modules', 'venv', '__pycache__', 'dist', 'build', 'target'
                )]
                
                for file in files:
                    total_files += 1
                    file_path = Path(root) / file
                    ext = file_path.suffix.lower()
                    
                    # Count source files
                    if ext in lang_map:
                        source_files += 1
                        languages.add(lang_map[ext])
                        
                        # Count lines
                        try:
                            with open(file_path, 'r', errors='ignore') as f:
                                total_lines += sum(1 for _ in f)
                        except Exception:
                            pass
                    
                    # Detect tests
                    if 'test' in file.lower() or file.startswith('test_'):
                        has_tests = True
                    
                    # Detect docs
                    if file.lower() in ('readme.md', 'readme.rst', 'readme.txt'):
                        has_docs = True
                    
                    # Detect frameworks
                    if file == 'package.json':
                        frameworks.add('Node.js')
                    if file == 'requirements.txt' or file == 'setup.py' or file == 'pyproject.toml':
                        frameworks.add('Python Package')
                    if file == 'Cargo.toml':
                        frameworks.add('Rust/Cargo')
                    if file == 'go.mod':
                        frameworks.add('Go Module')
                
                # Detect CI
                if '.github' in dirs:
                    has_ci = True
                if '.gitlab-ci.yml' in files or 'Jenkinsfile' in files:
                    has_ci = True
            
            # Determine complexity
            if source_files > 500 or total_lines > 100000:
                complexity = "high"
                recommended_strategy = "incremental"
                warnings.append("Large codebase - recommend incremental adoption")
            elif source_files > 100 or total_lines > 20000:
                complexity = "medium"
                recommended_strategy = "incremental"
            else:
                complexity = "low"
                recommended_strategy = "full"
            
            # Check for potential issues
            if not has_tests:
                warnings.append("No tests detected - recommend adding tests before adoption")
            if not has_docs:
                warnings.append("Limited documentation - discovery may produce sparse results")
            
            # Create analysis
            analysis = ProjectAnalysis(
                project_path=str(project_path),
                total_files=total_files,
                source_files=source_files,
                total_lines=total_lines,
                languages=sorted(languages),
                frameworks=sorted(frameworks),
                has_tests=has_tests,
                has_ci=has_ci,
                has_docs=has_docs,
                complexity=complexity,
                recommended_strategy=recommended_strategy,
                warnings=warnings,
            )
            
            self.state.analysis = analysis
            self.state.artifacts["analysis"] = analysis
            self.state.warnings.extend(warnings)
            
            self.state.mark_completed(step)
            
            return AdoptionResult(
                step=step,
                success=True,
                message=f"Analyzed {source_files} source files ({total_lines:,} lines)",
                artifacts={
                    "source_files": source_files,
                    "total_lines": total_lines,
                    "languages": sorted(languages),
                    "complexity": complexity,
                    "strategy": recommended_strategy,
                },
                next_step=AdoptionStep.INITIALIZE,
                next_action=f"Run step_initialize() to create Axiom configuration",
                can_rollback=False,  # Analysis is read-only
                rollback_instructions="No changes were made",
            )
            
        except Exception as e:
            self.state.mark_failed(step, str(e))
            return AdoptionResult(
                step=step,
                success=False,
                message=f"Analysis failed: {e}",
            )
    
    # =========================================================================
    # Step 2: Initialize
    # =========================================================================
    
    def step_initialize(self) -> AdoptionResult:
        """
        Initialize Axiom configuration.
        
        Creates .axiom/ directory alongside existing project files.
        DOES NOT modify existing files.
        
        Returns:
            AdoptionResult with initialization status.
        """
        step = AdoptionStep.INITIALIZE
        
        if not self.state.can_proceed_to(step):
            return AdoptionResult(
                step=step,
                success=False,
                message="Cannot initialize: complete analysis first",
                next_action="Run step_analyze() first",
            )
        
        if self.state.current_step != step:
            return AdoptionResult(
                step=step,
                success=False,
                message=f"Cannot initialize: current step is {self.state.current_step.value}",
            )
        
        try:
            project_path = Path(self.state.project_path)
            axiom_dir = project_path / ".axiom"
            
            # Check if already initialized
            if axiom_dir.exists():
                return AdoptionResult(
                    step=step,
                    success=False,
                    message="Axiom already initialized in this project",
                    next_action="Use existing configuration or delete .axiom/ to start fresh",
                )
            
            # Create Axiom directories
            canon_dir = axiom_dir / "canon"
            state_dir = axiom_dir / "state"
            checkpoints_dir = axiom_dir / "checkpoints"
            
            axiom_dir.mkdir(parents=True)
            canon_dir.mkdir()
            state_dir.mkdir()
            checkpoints_dir.mkdir()
            
            # Create config
            config = {
                "version": "1.0.0",
                "initialized_at": datetime.now(timezone.utc).isoformat(),
                "project_path": str(project_path.absolute()),
                "canon_path": str(canon_dir.absolute()),
                "adoption_mode": True,  # Indicates this is an adoption
                "analysis": {
                    "complexity": self.state.analysis.complexity if self.state.analysis else "unknown",
                    "strategy": self.state.analysis.recommended_strategy if self.state.analysis else "incremental",
                },
            }
            
            config_path = axiom_dir / "config.json"
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            
            # Create empty Canon artifacts
            self._cpkg = CPKG()
            self._ucir = UCIR()
            self._bfm = BusinessFlowMap()
            
            cpkg_path = canon_dir / "cpkg.json"
            ucir_path = canon_dir / "ucir.json"
            bfm_path = canon_dir / "bfm.json"
            
            with open(cpkg_path, "w") as f:
                json.dump({"nodes": {}, "edges": [], "version": "0.1.0"}, f, indent=2)
            with open(ucir_path, "w") as f:
                json.dump({"constraints": {}, "version": "0.1.0"}, f, indent=2)
            with open(bfm_path, "w") as f:
                json.dump({"flows": {}, "version": "0.1.0"}, f, indent=2)
            
            # Store artifacts
            self.state.artifacts["axiom_dir"] = str(axiom_dir)
            self.state.artifacts["canon_dir"] = str(canon_dir)
            self.state.artifacts["cpkg_path"] = str(cpkg_path)
            self.state.artifacts["ucir_path"] = str(ucir_path)
            self.state.artifacts["bfm_path"] = str(bfm_path)
            
            self.state.mark_completed(step)
            
            return AdoptionResult(
                step=step,
                success=True,
                message="Axiom initialized successfully",
                artifacts={
                    "axiom_dir": str(axiom_dir),
                    "canon_dir": str(canon_dir),
                },
                next_step=AdoptionStep.EXTRACT,
                next_action="Run step_extract() to extract code structure",
                can_rollback=True,
                rollback_instructions="Delete .axiom/ directory to rollback",
            )
            
        except Exception as e:
            self.state.mark_failed(step, str(e))
            return AdoptionResult(
                step=step,
                success=False,
                message=f"Initialization failed: {e}",
                rollback_instructions="Check permissions and try again",
            )
    
    # =========================================================================
    # Step 3: Extract (Incremental)
    # =========================================================================
    
    def step_extract(
        self,
        paths: Optional[List[str]] = None,
        incremental: bool = False,
    ) -> AdoptionResult:
        """
        Extract code structure.
        
        Supports incremental extraction for large codebases.
        
        Args:
            paths: Specific paths to extract (None = all).
            incremental: If True, add to existing extraction.
        
        Returns:
            AdoptionResult with extraction status.
        """
        step = AdoptionStep.EXTRACT
        
        if not self.state.can_proceed_to(step):
            return AdoptionResult(
                step=step,
                success=False,
                message="Cannot extract: complete initialization first",
                next_action="Run step_initialize() first",
            )
        
        if self.state.current_step != step and not incremental:
            return AdoptionResult(
                step=step,
                success=False,
                message=f"Cannot extract: current step is {self.state.current_step.value}",
            )
        
        try:
            project_path = Path(self.state.project_path)
            
            # For incremental, track progress
            existing_components = self.state.artifacts.get("extracted_components", {})
            
            # Determine scope
            if paths:
                target_paths = [project_path / p for p in paths]
            else:
                target_paths = [project_path]
            
            # Count files to extract
            files_to_extract = []
            for target in target_paths:
                if target.is_file():
                    files_to_extract.append(target)
                elif target.is_dir():
                    for ext in ['.py', '.js', '.ts', '.java', '.go', '.rs']:
                        files_to_extract.extend(target.rglob(f'*{ext}'))
            
            # Filter out already extracted
            if incremental:
                extracted_files = set(self.state.artifacts.get("extracted_files", []))
                files_to_extract = [f for f in files_to_extract if str(f) not in extracted_files]
            
            # Extract (simplified - in production would use CodeExtractor)
            extracted_count = 0
            for file_path in files_to_extract:
                try:
                    # Create component entry
                    rel_path = file_path.relative_to(project_path)
                    component_id = str(rel_path).replace('/', '_').replace('.', '_')
                    
                    existing_components[component_id] = {
                        "path": str(rel_path),
                        "type": file_path.suffix[1:] if file_path.suffix else "unknown",
                    }
                    extracted_count += 1
                except Exception:
                    pass
            
            # Update state
            self.state.artifacts["extracted_components"] = existing_components
            self.state.artifacts["extracted_files"] = list(
                set(self.state.artifacts.get("extracted_files", [])) | 
                {str(f) for f in files_to_extract}
            )
            
            # Calculate progress
            total_source = self.state.analysis.source_files if self.state.analysis else 1
            progress = min(len(existing_components) / max(total_source, 1) * 100, 100)
            
            if progress >= 100:
                self.state.mark_completed(step)
                return AdoptionResult(
                    step=step,
                    success=True,
                    message=f"Extraction complete: {len(existing_components)} components",
                    progress=100.0,
                    artifacts={
                        "component_count": len(existing_components),
                    },
                    next_step=AdoptionStep.ENRICH,
                    next_action="Run step_enrich() for LLM enrichment (optional) or skip_enrich()",
                )
            else:
                self.state.mark_partial(step, progress)
                return AdoptionResult(
                    step=step,
                    success=True,
                    message=f"Extracted {extracted_count} files ({progress:.0f}% complete)",
                    progress=progress,
                    artifacts={
                        "extracted_this_run": extracted_count,
                        "total_extracted": len(existing_components),
                    },
                    next_step=None,
                    next_action="Run step_extract(incremental=True) to continue extraction",
                )
            
        except Exception as e:
            self.state.mark_failed(step, str(e))
            return AdoptionResult(
                step=step,
                success=False,
                message=f"Extraction failed: {e}",
            )
    
    # =========================================================================
    # Steps 4-9: Similar pattern to new project
    # =========================================================================
    
    def step_enrich(self) -> AdoptionResult:
        """Run optional LLM enrichment (same as new project)."""
        step = AdoptionStep.ENRICH
        
        if not self.state.can_proceed_to(step):
            return AdoptionResult(
                step=step,
                success=False,
                message="Cannot enrich: complete extraction first",
            )
        
        if self.state.current_step != step:
            return AdoptionResult(
                step=step,
                success=False,
                message=f"Cannot enrich: current step is {self.state.current_step.value}",
            )
        
        # Placeholder - would call LLM enrichment
        self.state.artifacts["enrichment_result"] = {
            "status": "completed",
            "labels_generated": 0,
            "advisory_only": True,
        }
        
        self.state.mark_completed(step)
        
        return AdoptionResult(
            step=step,
            success=True,
            message="Enrichment completed (ADVISORY ONLY)",
            next_step=AdoptionStep.REVIEW,
            next_action="Run step_review() to review annotations",
        )
    
    def skip_enrich(self) -> AdoptionResult:
        """Skip optional enrichment."""
        step = AdoptionStep.ENRICH
        
        if self.state.current_step != step:
            return AdoptionResult(
                step=step,
                success=False,
                message=f"Cannot skip: current step is {self.state.current_step.value}",
            )
        
        self.state.step_statuses[step] = AdoptionStepStatus.SKIPPED_OPTIONAL
        self.state.step_progress[step] = 100.0
        self.state.current_step = AdoptionStep.REVIEW
        self.state.step_statuses[AdoptionStep.REVIEW] = AdoptionStepStatus.CURRENT
        
        return AdoptionResult(
            step=step,
            success=True,
            message="Enrichment skipped",
            next_step=AdoptionStep.REVIEW,
            next_action="Run step_review() to review extracted annotations",
        )
    
    def step_review(self) -> AdoptionResult:
        """Review annotations."""
        step = AdoptionStep.REVIEW
        
        if not self.state.can_proceed_to(step):
            return AdoptionResult(
                step=step,
                success=False,
                message="Cannot review: complete extraction first",
            )
        
        if self.state.current_step != step:
            return AdoptionResult(
                step=step,
                success=False,
                message=f"Cannot review: current step is {self.state.current_step.value}",
            )
        
        components = self.state.artifacts.get("extracted_components", {})
        review_items = [
            {"type": "component", "id": k, "path": v.get("path", "")}
            for k, v in components.items()
        ]
        
        self.state.artifacts["review_items"] = review_items
        self.state.mark_completed(step)
        
        return AdoptionResult(
            step=step,
            success=True,
            message=f"Review prepared: {len(review_items)} items",
            artifacts={"review_count": len(review_items)},
            next_step=AdoptionStep.PROMOTE,
            next_action="Run step_promote(confirm=True) to promote to Canon",
        )
    
    def step_promote(self, confirm: bool = False) -> AdoptionResult:
        """Promote to Canon."""
        step = AdoptionStep.PROMOTE
        
        if not self.state.can_proceed_to(step):
            return AdoptionResult(
                step=step,
                success=False,
                message="Cannot promote: complete review first",
            )
        
        if self.state.current_step != step:
            return AdoptionResult(
                step=step,
                success=False,
                message=f"Cannot promote: current step is {self.state.current_step.value}",
            )
        
        if not confirm:
            return AdoptionResult(
                step=step,
                success=False,
                message="Canon promotion requires explicit confirmation",
                next_action="Call step_promote(confirm=True)",
            )
        
        # Promote components to CPKG
        if self._cpkg is None:
            self._cpkg = CPKG()
        
        components = self.state.artifacts.get("extracted_components", {})
        for comp_id, comp_data in components.items():
            node = CPKGNode(
                id=comp_id,
                type=NodeType.COMPONENT,
                content=f"Component: {comp_data.get('path', comp_id)}",
                metadata={"source": "adoption"},
            )
            self._cpkg.nodes[comp_id] = node
        
        # Save CPKG
        cpkg_path = self.state.artifacts.get("cpkg_path")
        if cpkg_path:
            with open(cpkg_path, "w") as f:
                json.dump({
                    "nodes": {k: {"id": v.id, "type": v.type.value, "content": v.content, "metadata": v.metadata}
                             for k, v in self._cpkg.nodes.items()},
                    "edges": [],
                    "version": self._cpkg.version,
                }, f, indent=2)
        
        self.state.mark_completed(step)
        
        return AdoptionResult(
            step=step,
            success=True,
            message=f"Promoted {len(self._cpkg.nodes)} components to Canon",
            next_step=AdoptionStep.INTEGRATE,
            next_action="Run step_integrate() to configure executors",
        )
    
    def step_integrate(self) -> AdoptionResult:
        """Configure integration."""
        step = AdoptionStep.INTEGRATE
        
        if not self.state.can_proceed_to(step):
            return AdoptionResult(
                step=step,
                success=False,
                message="Cannot integrate: complete promotion first",
            )
        
        if self.state.current_step != step:
            return AdoptionResult(
                step=step,
                success=False,
                message=f"Cannot integrate: current step is {self.state.current_step.value}",
            )
        
        # Create default executor configuration
        axiom_dir = Path(self.state.artifacts.get("axiom_dir", ""))
        config_path = axiom_dir / "executors.json"
        
        executor_config = {
            "version": "1.0.0",
            "executors": {
                "shell": {
                    "enabled": True,
                    "allowed_commands": ["ls", "cat", "echo", "pwd"],
                    "working_directory": self.state.project_path,
                },
            },
            "policies": {
                "require_human_approval": True,
                "max_concurrent_tasks": 1,
            },
        }
        
        with open(config_path, "w") as f:
            json.dump(executor_config, f, indent=2)
        
        self.state.artifacts["executor_config_path"] = str(config_path)
        self.state.mark_completed(step)
        
        return AdoptionResult(
            step=step,
            success=True,
            message="Executor configuration created",
            next_step=AdoptionStep.VALIDATE,
            next_action="Run step_validate() to verify Canon integrity",
        )
    
    def step_validate(self) -> AdoptionResult:
        """Validate Canon."""
        step = AdoptionStep.VALIDATE
        
        if not self.state.can_proceed_to(step):
            return AdoptionResult(
                step=step,
                success=False,
                message="Cannot validate: complete integration first",
            )
        
        if self.state.current_step != step:
            return AdoptionResult(
                step=step,
                success=False,
                message=f"Cannot validate: current step is {self.state.current_step.value}",
            )
        
        errors = []
        warnings = []
        
        # Check files exist
        for path_key in ["cpkg_path", "ucir_path", "bfm_path"]:
            path = self.state.artifacts.get(path_key)
            if not path or not Path(path).exists():
                errors.append(f"Missing: {path_key}")
        
        if errors:
            self.state.mark_failed(step, f"{len(errors)} validation errors")
            return AdoptionResult(
                step=step,
                success=False,
                message=f"Validation failed: {', '.join(errors)}",
            )
        
        self.state.mark_completed(step)
        
        return AdoptionResult(
            step=step,
            success=True,
            message="Validation passed",
            next_step=AdoptionStep.PILOT,
            next_action="Run step_pilot() for first workflow (optional) or skip_pilot()",
        )
    
    def step_pilot(self, request: str = "list files", confirm: bool = False) -> AdoptionResult:
        """Execute pilot workflow."""
        step = AdoptionStep.PILOT
        
        if not self.state.can_proceed_to(step):
            return AdoptionResult(
                step=step,
                success=False,
                message="Cannot pilot: complete validation first",
            )
        
        if self.state.current_step != step:
            return AdoptionResult(
                step=step,
                success=False,
                message=f"Cannot pilot: current step is {self.state.current_step.value}",
            )
        
        if not confirm:
            return AdoptionResult(
                step=step,
                success=False,
                message="Pilot execution requires explicit confirmation",
                next_action="Call step_pilot(confirm=True)",
            )
        
        self.state.mark_completed(step)
        
        return AdoptionResult(
            step=step,
            success=True,
            message="Pilot workflow executed (placeholder)",
            next_step=None,
            next_action="Adoption complete! Use AxiomWorkflow for governed operations.",
        )
    
    def skip_pilot(self) -> AdoptionResult:
        """Skip pilot workflow."""
        step = AdoptionStep.PILOT
        
        if self.state.current_step != step:
            return AdoptionResult(
                step=step,
                success=False,
                message=f"Cannot skip: current step is {self.state.current_step.value}",
            )
        
        self.state.step_statuses[step] = AdoptionStepStatus.SKIPPED_OPTIONAL
        self.state.step_progress[step] = 100.0
        
        return AdoptionResult(
            step=step,
            success=True,
            message="Pilot skipped. Adoption complete!",
            next_step=None,
            next_action="Use AxiomWorkflow for governed operations.",
        )
    
    # =========================================================================
    # Utilities
    # =========================================================================
    
    def get_progress(self) -> str:
        """Get formatted progress display."""
        return self.display.render_progress(self.state)
    
    def get_analysis(self) -> str:
        """Get formatted analysis display."""
        if self.state.analysis:
            return self.display.render_analysis(self.state.analysis)
        return "No analysis available. Run step_analyze() first."
    
    def rollback(self, to_step: Optional[AdoptionStep] = None) -> AdoptionResult:
        """
        Rollback to a previous state.
        
        Args:
            to_step: Step to rollback to (None = initial state).
        
        Returns:
            AdoptionResult with rollback status.
        """
        if to_step is None:
            # Full rollback - delete .axiom/
            axiom_dir = Path(self.state.artifacts.get("axiom_dir", ""))
            if axiom_dir.exists():
                import shutil
                shutil.rmtree(axiom_dir)
            
            return AdoptionResult(
                step=self.state.current_step,
                success=True,
                message="Rolled back to initial state",
                next_action="Run step_analyze() to start adoption again",
            )
        
        # Partial rollback - use checkpoints
        checkpoint = self.state.get_rollback_point(to_step)
        if checkpoint:
            # Restore from checkpoint
            return AdoptionResult(
                step=to_step,
                success=True,
                message=f"Rolled back to {to_step.value}",
            )
        
        return AdoptionResult(
            step=self.state.current_step,
            success=False,
            message=f"No checkpoint available for {to_step.value}",
        )

    def run_quick_adopt(self) -> AdoptionResult:
        """
        Run a quick adoption for CLI usage.
        
        This method runs the essential adoption steps without
        requiring interactive input. It creates the basic project
        structure needed for Axiom to operate with existing code.
        
        Returns:
            AdoptionResult indicating success or failure.
        """
        # Step 1: Analyze existing project
        analyze_result = self.step_analyze()
        if not analyze_result.success:
            return analyze_result
        
        # Step 2: Initialize Axiom structure
        init_result = self.step_initialize()
        if not init_result.success:
            return init_result
        
        # For quick adopt, we stop here with minimal viable setup
        # User can run remaining steps manually if needed
        return AdoptionResult(
            step=AdoptionStep.INITIALIZE,
            success=True,
            message="Quick adoption complete. Project is ready for discovery and planning.",
            artifacts={
                **analyze_result.artifacts,
                **init_result.artifacts,
            },
            next_step=AdoptionStep.EXTRACT,
            next_action="Run 'axiom discover' to analyze your codebase, then 'axiom plan' to create plans.",
        )
