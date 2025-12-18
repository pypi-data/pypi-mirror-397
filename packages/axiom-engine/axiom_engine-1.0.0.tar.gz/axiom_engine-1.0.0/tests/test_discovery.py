"""
Tests for Discovery System.

Verifies:
1. DISCOVERY tasks cannot execute code
2. Executors are read-only and sandboxed
3. InferredAnnotations never auto-promote
4. Human rejection blocks Canon updates
5. Evidence is required for all inferences
6. Token and scope limits are enforced
"""

import json
import tempfile
from pathlib import Path
from typing import List

import pytest

# Discovery models - import directly from module to avoid circular imports
from axiom_canon.discovery import (
    AnnotationReviewDecision,
    DiscoveryDependency,
    DiscoveryGraphResult,
    DiscoveryResult,
    DiscoveryScope,
    DiscoveryTask,
    DiscoveryTaskGraph,
    DiscoveryTaskType,
    EvidenceExcerpt,
    INFERENCE_LABEL,
    InferenceConfidence,
    InferenceEvidence,
    InferenceStatus,
    InferenceType,
    InferredAnnotation,
    TaskType,
    apply_review_decision,
    get_promotable_annotations,
    validate_annotation_can_promote,
    validate_annotation_has_evidence,
    validate_discovery_graph_is_pure,
    validate_discovery_task_is_read_only,
)
from axiom_canon.ingestion.models import (
    ComponentSummary,
    ExportInfo,
    IngestionResult,
    ModuleSummary,
    ModuleType,
    Visibility,
)
# Import directly from module file to avoid circular imports through __init__
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from axiom_canon.analysis_executor import (
    AnalysisExecutorConfig,
    FileReader,
    LLMAnalysisExecutor,
    MockAnalysisBackend,
    validate_discovery_result_is_provisional,
    validate_executor_is_read_only,
)
from axiom_strata.discovery_planner import (
    DiscoveryIntent,
    DiscoveryIntentType,
    DiscoveryPlannerConfig,
    RuleBasedDiscoveryPlanner,
    validate_discovery_graph_has_no_execution,
    validate_intent_has_targets,
)
from axiom_canon.documentation import (
    DocumentationGenerator,
    MarkdownRenderer,
    validate_documentation_is_derived,
    validate_documentation_sources,
)
from axiom_canon.ingestion.enrichment_models import (
    EnrichedComponentLabel,
    ReviewDecision,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory with sample files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        
        # Create sample source files
        src_dir = root / "src"
        src_dir.mkdir()
        
        (src_dir / "auth.py").write_text('''"""
Authentication module.

@invariant: Tokens must expire within 1 hour.
"""

class AuthService:
    """Handles user authentication."""
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate a user."""
        # Implementation
        return True
    
    def generate_token(self, user_id: str) -> str:
        """Generate auth token."""
        return "token"
''')
        
        (src_dir / "models.py").write_text('''"""
Data models.
"""

from dataclasses import dataclass

@dataclass
class User:
    """User model."""
    id: str
    username: str
    email: str
''')
        
        (src_dir / "api.py").write_text('''"""
API endpoints.
"""

from auth import AuthService
from models import User

def login(username: str, password: str):
    """Login endpoint."""
    auth = AuthService()
    return auth.authenticate(username, password)
''')
        
        yield root


@pytest.fixture
def sample_modules() -> List[ModuleSummary]:
    """Create sample modules."""
    return [
        ModuleSummary(
            id="mod_auth",
            name="auth",
            path="src/auth.py",
            module_type=ModuleType.MODULE,
            exports=[ExportInfo(name="AuthService", kind="class")],
        ),
        ModuleSummary(
            id="mod_models",
            name="models",
            path="src/models.py",
            module_type=ModuleType.MODULE,
            exports=[ExportInfo(name="User", kind="class")],
        ),
        ModuleSummary(
            id="mod_api",
            name="api",
            path="src/api.py",
            module_type=ModuleType.MODULE,
            exports=[ExportInfo(name="login", kind="function")],
        ),
    ]


@pytest.fixture
def sample_components(sample_modules: List[ModuleSummary]) -> List[ComponentSummary]:
    """Create sample components."""
    return [
        ComponentSummary(
            id="comp_auth",
            name="auth",
            path="src",
            modules=[sample_modules[0]],
        ),
        ComponentSummary(
            id="comp_models",
            name="models",
            path="src",
            modules=[sample_modules[1]],
        ),
        ComponentSummary(
            id="comp_api",
            name="api",
            path="src",
            modules=[sample_modules[2]],
        ),
    ]


@pytest.fixture
def sample_ingestion_result(
    sample_modules: List[ModuleSummary],
    sample_components: List[ComponentSummary],
) -> IngestionResult:
    """Create sample ingestion result."""
    return IngestionResult(
        project_root="src",
        modules=sample_modules,
        components=sample_components,
    )


# =============================================================================
# TaskType and Discovery Task Tests
# =============================================================================


class TestTaskType:
    """Tests for TaskType enum."""
    
    def test_execution_type_exists(self) -> None:
        """EXECUTION type exists."""
        assert TaskType.EXECUTION == "execution"
    
    def test_discovery_type_exists(self) -> None:
        """DISCOVERY type exists."""
        assert TaskType.DISCOVERY == "discovery"


class TestDiscoveryScope:
    """Tests for DiscoveryScope."""
    
    def test_default_scope_is_valid(self) -> None:
        """Default scope passes validation."""
        scope = DiscoveryScope()
        assert scope.validate() == []
    
    def test_max_files_limit(self) -> None:
        """Max files cannot exceed 50."""
        scope = DiscoveryScope(max_files=100)
        errors = scope.validate()
        assert any("max_files cannot exceed 50" in e for e in errors)
    
    def test_max_tokens_limit(self) -> None:
        """Max tokens per file cannot exceed 10000."""
        scope = DiscoveryScope(max_tokens_per_file=20000)
        errors = scope.validate()
        assert any("max_tokens_per_file cannot exceed 10000" in e for e in errors)
    
    def test_total_tokens_limit(self) -> None:
        """Max total tokens cannot exceed 50000."""
        scope = DiscoveryScope(max_total_tokens=100000)
        errors = scope.validate()
        assert any("max_total_tokens cannot exceed 50000" in e for e in errors)


class TestDiscoveryTask:
    """Tests for DiscoveryTask."""
    
    def test_valid_task(self) -> None:
        """Valid task passes validation."""
        task = DiscoveryTask(
            id="task_1",
            name="Analyze auth",
            description="Analyze authentication module",
            task_type=DiscoveryTaskType.COMPONENT_ANALYSIS,
            scope=DiscoveryScope(file_paths=["src/auth.py"]),
        )
        assert task.validate() == []
    
    def test_missing_id_fails(self) -> None:
        """Task without ID fails validation."""
        task = DiscoveryTask(
            id="",
            name="Test",
            description="Test",
            task_type=DiscoveryTaskType.COMPONENT_ANALYSIS,
            scope=DiscoveryScope(),
        )
        errors = task.validate()
        assert any("id is required" in e for e in errors)
    
    def test_timeout_limit(self) -> None:
        """Timeout cannot exceed 300 seconds."""
        task = DiscoveryTask(
            id="task_1",
            name="Test",
            description="Test",
            task_type=DiscoveryTaskType.COMPONENT_ANALYSIS,
            scope=DiscoveryScope(),
            timeout_seconds=600,
        )
        errors = task.validate()
        assert any("timeout_seconds cannot exceed 300" in e for e in errors)
    
    def test_task_has_no_command_field(self) -> None:
        """Discovery tasks have no command field (by design)."""
        task = DiscoveryTask(
            id="task_1",
            name="Test",
            description="Test",
            task_type=DiscoveryTaskType.COMPONENT_ANALYSIS,
            scope=DiscoveryScope(),
        )
        assert not hasattr(task, "command")


class TestDiscoveryTaskGraph:
    """Tests for DiscoveryTaskGraph."""
    
    def test_valid_graph(self) -> None:
        """Valid graph passes validation."""
        graph = DiscoveryTaskGraph(
            id="graph_1",
            intent="Document auth system",
        )
        task = DiscoveryTask(
            id="task_1",
            name="Analyze auth",
            description="Analyze auth module",
            task_type=DiscoveryTaskType.COMPONENT_ANALYSIS,
            scope=DiscoveryScope(file_paths=["src/auth.py"]),
        )
        graph.add_task(task)
        
        assert graph.validate() == []
    
    def test_get_ready_tasks(self) -> None:
        """Ready tasks are correctly identified."""
        graph = DiscoveryTaskGraph(id="graph_1", intent="Test")
        
        task1 = DiscoveryTask(
            id="task_1", name="T1", description="D1",
            task_type=DiscoveryTaskType.COMPONENT_ANALYSIS,
            scope=DiscoveryScope(),
        )
        task2 = DiscoveryTask(
            id="task_2", name="T2", description="D2",
            task_type=DiscoveryTaskType.COMPONENT_ANALYSIS,
            scope=DiscoveryScope(),
        )
        
        graph.add_task(task1)
        graph.add_task(task2)
        graph.add_dependency("task_1", "task_2")
        
        # Initially only task_1 is ready
        ready = graph.get_ready_tasks(set())
        assert "task_1" in ready
        assert "task_2" not in ready
        
        # After task_1 completes, task_2 is ready
        ready = graph.get_ready_tasks({"task_1"})
        assert "task_2" in ready


# =============================================================================
# Evidence and Inference Tests
# =============================================================================


class TestInferenceEvidence:
    """Tests for InferenceEvidence."""
    
    def test_has_evidence_with_excerpts(self) -> None:
        """Evidence with excerpts returns True."""
        evidence = InferenceEvidence(
            excerpts=[
                EvidenceExcerpt(
                    file_path="src/auth.py",
                    start_line=1,
                    end_line=5,
                    content="# Auth code",
                )
            ]
        )
        assert evidence.has_evidence() is True
    
    def test_has_evidence_with_observations(self) -> None:
        """Evidence with observations returns True."""
        evidence = InferenceEvidence(
            observations=["Function takes username parameter"]
        )
        assert evidence.has_evidence() is True
    
    def test_empty_evidence_returns_false(self) -> None:
        """Empty evidence returns False."""
        evidence = InferenceEvidence()
        assert evidence.has_evidence() is False


class TestInferredAnnotation:
    """Tests for InferredAnnotation."""
    
    def test_annotation_starts_proposed(self) -> None:
        """Annotations start in PROPOSED status."""
        annotation = InferredAnnotation(
            id="ann_1",
            inference_type=InferenceType.COMPONENT_PURPOSE,
            content="Test content",
            evidence=InferenceEvidence(observations=["obs"]),
            confidence=InferenceConfidence.MEDIUM,
            target_artifact_id="comp_1",
            target_artifact_type="component",
            provenance={"task_id": "task_1"},
        )
        assert annotation.status == InferenceStatus.PROPOSED
    
    def test_annotation_has_inference_label(self) -> None:
        """Annotations have the inference label."""
        annotation = InferredAnnotation(
            id="ann_1",
            inference_type=InferenceType.COMPONENT_PURPOSE,
            content="Test",
            evidence=InferenceEvidence(observations=["obs"]),
            confidence=InferenceConfidence.MEDIUM,
            target_artifact_id="comp_1",
            target_artifact_type="component",
            provenance={"task_id": "task_1"},
        )
        assert annotation.inference_label == INFERENCE_LABEL
    
    def test_annotation_without_evidence_fails_validation(self) -> None:
        """Annotations without evidence fail validation."""
        annotation = InferredAnnotation(
            id="ann_1",
            inference_type=InferenceType.COMPONENT_PURPOSE,
            content="Test",
            evidence=InferenceEvidence(),  # Empty evidence
            confidence=InferenceConfidence.MEDIUM,
            target_artifact_id="comp_1",
            target_artifact_type="component",
            provenance={"task_id": "task_1"},
        )
        errors = annotation.validate()
        assert any("Evidence is required" in e for e in errors)
    
    def test_unknown_confidence_fails_validation(self) -> None:
        """UNKNOWN confidence fails validation."""
        annotation = InferredAnnotation(
            id="ann_1",
            inference_type=InferenceType.COMPONENT_PURPOSE,
            content="Test",
            evidence=InferenceEvidence(observations=["obs"]),
            confidence=InferenceConfidence.UNKNOWN,
            target_artifact_id="comp_1",
            target_artifact_type="component",
            provenance={"task_id": "task_1"},
        )
        errors = annotation.validate()
        assert any("UNKNOWN" in e for e in errors)
    
    def test_missing_provenance_fails_validation(self) -> None:
        """Missing task_id in provenance fails validation."""
        annotation = InferredAnnotation(
            id="ann_1",
            inference_type=InferenceType.COMPONENT_PURPOSE,
            content="Test",
            evidence=InferenceEvidence(observations=["obs"]),
            confidence=InferenceConfidence.MEDIUM,
            target_artifact_id="comp_1",
            target_artifact_type="component",
            provenance={},  # Missing task_id
        )
        errors = annotation.validate()
        assert any("task_id" in e for e in errors)
    
    def test_only_accepted_is_promotable(self) -> None:
        """Only ACCEPTED annotations are promotable."""
        annotation = InferredAnnotation(
            id="ann_1",
            inference_type=InferenceType.COMPONENT_PURPOSE,
            content="Test",
            evidence=InferenceEvidence(observations=["obs"]),
            confidence=InferenceConfidence.MEDIUM,
            target_artifact_id="comp_1",
            target_artifact_type="component",
            provenance={"task_id": "task_1"},
        )
        
        # PROPOSED is not promotable
        assert annotation.is_promotable is False
        
        # REJECTED is not promotable
        annotation.status = InferenceStatus.REJECTED
        assert annotation.is_promotable is False
        
        # ACCEPTED is promotable
        annotation.status = InferenceStatus.ACCEPTED
        assert annotation.is_promotable is True


# =============================================================================
# Review Flow Tests
# =============================================================================


class TestReviewFlow:
    """Tests for human review flow."""
    
    def test_apply_accept_decision(self) -> None:
        """Accept decision changes status to ACCEPTED."""
        annotation = InferredAnnotation(
            id="ann_1",
            inference_type=InferenceType.COMPONENT_PURPOSE,
            content="Original content",
            evidence=InferenceEvidence(observations=["obs"]),
            confidence=InferenceConfidence.MEDIUM,
            target_artifact_id="comp_1",
            target_artifact_type="component",
            provenance={"task_id": "task_1"},
        )
        
        decision = AnnotationReviewDecision(
            annotation_id="ann_1",
            decision=InferenceStatus.ACCEPTED,
            reviewer_notes="Looks correct",
        )
        
        apply_review_decision(annotation, decision)
        
        assert annotation.status == InferenceStatus.ACCEPTED
        assert annotation.review_notes == "Looks correct"
    
    def test_apply_reject_decision(self) -> None:
        """Reject decision changes status to REJECTED."""
        annotation = InferredAnnotation(
            id="ann_1",
            inference_type=InferenceType.COMPONENT_PURPOSE,
            content="Content",
            evidence=InferenceEvidence(observations=["obs"]),
            confidence=InferenceConfidence.MEDIUM,
            target_artifact_id="comp_1",
            target_artifact_type="component",
            provenance={"task_id": "task_1"},
        )
        
        decision = AnnotationReviewDecision(
            annotation_id="ann_1",
            decision=InferenceStatus.REJECTED,
            reviewer_notes="Incorrect inference",
        )
        
        apply_review_decision(annotation, decision)
        
        assert annotation.status == InferenceStatus.REJECTED
    
    def test_apply_edit_decision(self) -> None:
        """Edit decision updates content and accepts."""
        annotation = InferredAnnotation(
            id="ann_1",
            inference_type=InferenceType.COMPONENT_PURPOSE,
            content="Original content",
            evidence=InferenceEvidence(observations=["obs"]),
            confidence=InferenceConfidence.MEDIUM,
            target_artifact_id="comp_1",
            target_artifact_type="component",
            provenance={"task_id": "task_1"},
        )
        
        decision = AnnotationReviewDecision(
            annotation_id="ann_1",
            decision=InferenceStatus.ACCEPTED,
            edited_content="Edited content",
            reviewer_notes="Fixed wording",
        )
        
        apply_review_decision(annotation, decision)
        
        assert annotation.status == InferenceStatus.ACCEPTED
        assert annotation.content == "Edited content"
    
    def test_get_promotable_annotations(self) -> None:
        """Only accepted annotations are returned."""
        annotations = [
            InferredAnnotation(
                id="ann_1",
                inference_type=InferenceType.COMPONENT_PURPOSE,
                content="Content 1",
                evidence=InferenceEvidence(observations=["obs"]),
                confidence=InferenceConfidence.MEDIUM,
                target_artifact_id="comp_1",
                target_artifact_type="component",
                provenance={"task_id": "task_1"},
                status=InferenceStatus.ACCEPTED,
            ),
            InferredAnnotation(
                id="ann_2",
                inference_type=InferenceType.COMPONENT_PURPOSE,
                content="Content 2",
                evidence=InferenceEvidence(observations=["obs"]),
                confidence=InferenceConfidence.MEDIUM,
                target_artifact_id="comp_2",
                target_artifact_type="component",
                provenance={"task_id": "task_1"},
                status=InferenceStatus.REJECTED,
            ),
            InferredAnnotation(
                id="ann_3",
                inference_type=InferenceType.COMPONENT_PURPOSE,
                content="Content 3",
                evidence=InferenceEvidence(observations=["obs"]),
                confidence=InferenceConfidence.MEDIUM,
                target_artifact_id="comp_3",
                target_artifact_type="component",
                provenance={"task_id": "task_1"},
                status=InferenceStatus.PROPOSED,
            ),
        ]
        
        promotable = get_promotable_annotations(annotations)
        
        assert len(promotable) == 1
        assert promotable[0].id == "ann_1"


# =============================================================================
# File Reader Tests
# =============================================================================


class TestFileReader:
    """Tests for FileReader."""
    
    def test_read_file_within_project(self, temp_project_dir) -> None:
        """Can read files within project root."""
        reader = FileReader(str(temp_project_dir))
        content, tokens = reader.read_file("src/auth.py")
        
        assert "AuthService" in content
        assert tokens > 0
    
    def test_read_file_outside_project_fails(self, temp_project_dir) -> None:
        """Cannot read files outside project root."""
        reader = FileReader(str(temp_project_dir))
        
        with pytest.raises(PermissionError, match="outside project root"):
            reader.read_file("/etc/passwd")
    
    def test_read_nonexistent_file_fails(self, temp_project_dir) -> None:
        """Cannot read nonexistent files."""
        reader = FileReader(str(temp_project_dir))
        
        with pytest.raises(FileNotFoundError):
            reader.read_file("nonexistent.py")
    
    def test_read_file_with_line_range(self, temp_project_dir) -> None:
        """Can read specific line range."""
        reader = FileReader(str(temp_project_dir))
        content, tokens = reader.read_file("src/auth.py", start_line=1, end_line=5)
        
        # Should contain docstring but not full file
        assert "Authentication module" in content
        assert len(content.split("\n")) <= 5
    
    def test_token_limit_truncates(self, temp_project_dir) -> None:
        """Content is truncated to token limit."""
        reader = FileReader(str(temp_project_dir), max_tokens_per_file=10)
        content, tokens = reader.read_file("src/auth.py")
        
        # Should be truncated (10 tokens ~ 40 chars)
        assert len(content) <= 45  # 40 + "..."
        assert content.endswith("...")


# =============================================================================
# LLM Analysis Executor Tests
# =============================================================================


class TestLLMAnalysisExecutor:
    """Tests for LLMAnalysisExecutor."""
    
    def test_executor_is_read_only(self, temp_project_dir) -> None:
        """Executor has no dangerous methods."""
        backend = MockAnalysisBackend()
        executor = LLMAnalysisExecutor(
            backend=backend,
            project_root=str(temp_project_dir),
        )
        
        assert validate_executor_is_read_only(executor)
    
    def test_executor_disabled(self, temp_project_dir) -> None:
        """Disabled executor returns error."""
        backend = MockAnalysisBackend()
        config = AnalysisExecutorConfig(enabled=False)
        executor = LLMAnalysisExecutor(
            backend=backend,
            project_root=str(temp_project_dir),
            config=config,
        )
        
        task = DiscoveryTask(
            id="task_1",
            name="Test",
            description="Test",
            task_type=DiscoveryTaskType.COMPONENT_ANALYSIS,
            scope=DiscoveryScope(file_paths=["src/auth.py"]),
        )
        
        result = executor.execute(task)
        
        assert result.success is False
        assert any("disabled" in e for e in result.errors)
    
    def test_backend_unavailable(self, temp_project_dir) -> None:
        """Unavailable backend returns error."""
        backend = MockAnalysisBackend(available=False)
        executor = LLMAnalysisExecutor(
            backend=backend,
            project_root=str(temp_project_dir),
        )
        
        task = DiscoveryTask(
            id="task_1",
            name="Test",
            description="Test",
            task_type=DiscoveryTaskType.COMPONENT_ANALYSIS,
            scope=DiscoveryScope(file_paths=["src/auth.py"]),
        )
        
        result = executor.execute(task)
        
        assert result.success is False
        assert any("unavailable" in e for e in result.errors)
    
    def test_successful_analysis(self, temp_project_dir) -> None:
        """Successful analysis produces results."""
        response = json.dumps({
            "observations": ["AuthService class found"],
            "inferences": [
                {
                    "type": "component_purpose",
                    "content": "Handles user authentication",
                    "confidence": "high",
                    "evidence_refs": [0],
                }
            ],
            "evidence_excerpts": [
                {
                    "file": "src/auth.py",
                    "start_line": 7,
                    "end_line": 8,
                    "content": "class AuthService:",
                    "symbols": ["AuthService"],
                }
            ],
        })
        
        backend = MockAnalysisBackend(responses=[response])
        executor = LLMAnalysisExecutor(
            backend=backend,
            project_root=str(temp_project_dir),
        )
        
        task = DiscoveryTask(
            id="task_1",
            name="Analyze auth",
            description="Analyze authentication",
            task_type=DiscoveryTaskType.COMPONENT_ANALYSIS,
            scope=DiscoveryScope(file_paths=["src/auth.py"]),
            target_artifact_ids=["comp_auth"],
        )
        
        result = executor.execute(task)
        
        assert result.success is True
        assert len(result.annotations) > 0
        assert result.annotations[0].status == InferenceStatus.PROPOSED
    
    def test_results_are_provisional(self, temp_project_dir) -> None:
        """All annotations in results are provisional."""
        response = json.dumps({
            "observations": ["Test"],
            "inferences": [
                {"type": "component_purpose", "content": "Test", "confidence": "medium", "evidence_refs": []},
                {"type": "invariant", "content": "Test inv", "confidence": "low", "evidence_refs": []},
            ],
            "evidence_excerpts": [],
        })
        
        backend = MockAnalysisBackend(responses=[response])
        executor = LLMAnalysisExecutor(
            backend=backend,
            project_root=str(temp_project_dir),
        )
        
        task = DiscoveryTask(
            id="task_1",
            name="Test",
            description="Test",
            task_type=DiscoveryTaskType.COMPONENT_ANALYSIS,
            scope=DiscoveryScope(file_paths=["src/auth.py"]),
        )
        
        result = executor.execute(task)
        
        assert validate_discovery_result_is_provisional(result)


# =============================================================================
# Discovery Planner Tests
# =============================================================================


class TestDiscoveryPlanner:
    """Tests for Discovery Planner."""
    
    def test_valid_intent(self) -> None:
        """Valid intent passes validation."""
        intent = DiscoveryIntent(
            intent_type=DiscoveryIntentType.DOCUMENT_COMPONENT,
            description="Document the auth system",
            target_components=["comp_auth"],
        )
        
        assert intent.validate() == []
        assert validate_intent_has_targets(intent)
    
    def test_intent_without_targets_fails(self) -> None:
        """Intent without targets fails validation."""
        intent = DiscoveryIntent(
            intent_type=DiscoveryIntentType.DOCUMENT_COMPONENT,
            description="Document something",
        )
        
        errors = intent.validate()
        assert any("target" in e.lower() for e in errors)
    
    def test_planner_generates_discovery_graph(
        self,
        sample_ingestion_result: IngestionResult,
    ) -> None:
        """Planner generates a discovery task graph."""
        planner = RuleBasedDiscoveryPlanner()
        
        intent = DiscoveryIntent(
            intent_type=DiscoveryIntentType.DOCUMENT_COMPONENT,
            description="Document auth",
            target_components=["comp_auth"],
        )
        
        graph = planner.plan(intent, sample_ingestion_result)
        
        assert graph.id is not None
        assert len(graph.tasks) > 0
    
    def test_planner_graph_has_no_execution(
        self,
        sample_ingestion_result: IngestionResult,
    ) -> None:
        """Generated graphs have no execution tasks."""
        planner = RuleBasedDiscoveryPlanner()
        
        intent = DiscoveryIntent(
            intent_type=DiscoveryIntentType.DOCUMENT_SUBSYSTEM,
            description="Document all",
            target_components=["comp_auth", "comp_models", "comp_api"],
        )
        
        graph = planner.plan(intent, sample_ingestion_result)
        
        errors = validate_discovery_graph_has_no_execution(graph)
        assert errors == []
    
    def test_planner_respects_task_limit(
        self,
        sample_ingestion_result: IngestionResult,
    ) -> None:
        """Planner respects max tasks per graph."""
        config = DiscoveryPlannerConfig(max_tasks_per_graph=2)
        planner = RuleBasedDiscoveryPlanner(config=config)
        
        # Many components, but limited tasks
        intent = DiscoveryIntent(
            intent_type=DiscoveryIntentType.DOCUMENT_COMPONENT,
            description="Document all",
            target_components=["comp_auth", "comp_models", "comp_api"],
        )
        
        graph = planner.plan(intent, sample_ingestion_result)
        
        assert len(graph.tasks) <= 2


# =============================================================================
# Documentation Generator Tests
# =============================================================================


class TestDocumentationGenerator:
    """Tests for Documentation Generator."""
    
    def test_generates_documentation(
        self,
        sample_ingestion_result: IngestionResult,
    ) -> None:
        """Generator produces documentation."""
        generator = DocumentationGenerator()
        
        doc = generator.generate(
            ingestion_result=sample_ingestion_result,
            title="Test Docs",
        )
        
        assert doc.title == "Test Docs"
        assert len(doc.component_docs) == 3
    
    def test_documentation_is_derived(
        self,
        sample_ingestion_result: IngestionResult,
    ) -> None:
        """Documentation is marked as derived."""
        generator = DocumentationGenerator()
        
        doc = generator.generate(sample_ingestion_result)
        
        assert validate_documentation_is_derived(doc)
        assert doc.is_regenerable is True
    
    def test_documentation_tracks_source(
        self,
        sample_ingestion_result: IngestionResult,
    ) -> None:
        """Documentation tracks Canon version."""
        generator = DocumentationGenerator()
        
        doc = generator.generate(sample_ingestion_result)
        
        assert validate_documentation_sources(doc, sample_ingestion_result)
    
    def test_markdown_renderer(
        self,
        sample_ingestion_result: IngestionResult,
    ) -> None:
        """Markdown renderer produces output."""
        generator = DocumentationGenerator()
        renderer = MarkdownRenderer()
        
        doc = generator.generate(sample_ingestion_result, title="Test Docs")
        markdown = renderer.render(doc)
        
        assert "# Test Docs" in markdown
        assert "Components" in markdown
        assert "auth" in markdown


# =============================================================================
# Validation Tests
# =============================================================================


class TestValidation:
    """Tests for validation functions."""
    
    def test_validate_discovery_task_is_read_only(self) -> None:
        """Discovery tasks are validated as read-only."""
        task = DiscoveryTask(
            id="task_1",
            name="Test",
            description="Test",
            task_type=DiscoveryTaskType.COMPONENT_ANALYSIS,
            scope=DiscoveryScope(),
        )
        
        errors = validate_discovery_task_is_read_only(task)
        assert errors == []
    
    def test_validate_discovery_graph_is_pure(self) -> None:
        """Discovery graphs are validated as pure."""
        graph = DiscoveryTaskGraph(id="graph_1", intent="Test")
        
        task = DiscoveryTask(
            id="task_1",
            name="Test",
            description="Test",
            task_type=DiscoveryTaskType.COMPONENT_ANALYSIS,
            scope=DiscoveryScope(),
        )
        graph.add_task(task)
        
        errors = validate_discovery_graph_is_pure(graph)
        assert errors == []
    
    def test_validate_annotation_can_promote(self) -> None:
        """Promotion validation catches issues."""
        # Missing acceptance
        annotation = InferredAnnotation(
            id="ann_1",
            inference_type=InferenceType.COMPONENT_PURPOSE,
            content="Test",
            evidence=InferenceEvidence(observations=["obs"]),
            confidence=InferenceConfidence.MEDIUM,
            target_artifact_id="comp_1",
            target_artifact_type="component",
            provenance={"task_id": "task_1"},
        )
        
        errors = validate_annotation_can_promote(annotation)
        assert any("ACCEPTED" in e for e in errors)
        
        # After acceptance
        annotation.status = InferenceStatus.ACCEPTED
        errors = validate_annotation_can_promote(annotation)
        assert errors == []


# =============================================================================
# Integration Tests
# =============================================================================


class TestDiscoveryIntegration:
    """Integration tests for the full discovery flow."""
    
    def test_full_discovery_flow(
        self,
        temp_project_dir,
        sample_ingestion_result: IngestionResult,
    ) -> None:
        """Test complete discovery flow."""
        # 1. Human creates intent
        intent = DiscoveryIntent(
            intent_type=DiscoveryIntentType.DOCUMENT_COMPONENT,
            description="Document the auth module",
            target_components=["comp_auth"],
        )
        
        # 2. Planner generates discovery graph
        planner = RuleBasedDiscoveryPlanner()
        graph = planner.plan(intent, sample_ingestion_result)
        
        assert len(graph.tasks) > 0
        
        # 3. Validate graph is pure discovery (no execution)
        errors = validate_discovery_graph_has_no_execution(graph)
        assert errors == []
        
        # 4. Execute discovery tasks (read-only)
        response = json.dumps({
            "observations": ["Auth module handles authentication"],
            "inferences": [
                {
                    "type": "component_purpose",
                    "content": "Handles user authentication and token generation",
                    "confidence": "high",
                    "evidence_refs": [0],
                }
            ],
            "evidence_excerpts": [
                {
                    "file": "src/auth.py",
                    "start_line": 1,
                    "end_line": 5,
                    "content": '"""Authentication module."""',
                    "symbols": [],
                }
            ],
        })
        
        backend = MockAnalysisBackend(responses=[response])
        executor = LLMAnalysisExecutor(
            backend=backend,
            project_root=str(temp_project_dir),
        )
        
        graph_result = DiscoveryGraphResult(graph_id=graph.id)
        
        for task_id, task in graph.tasks.items():
            result = executor.execute(task)
            graph_result.add_result(result)
        
        # 5. All annotations are PROPOSED (not auto-promoted)
        for annotation in graph_result.all_annotations:
            assert annotation.status == InferenceStatus.PROPOSED
            assert annotation.inference_label == INFERENCE_LABEL
        
        # 6. Human reviews and accepts
        for annotation in graph_result.all_annotations:
            decision = AnnotationReviewDecision(
                annotation_id=annotation.id,
                decision=InferenceStatus.ACCEPTED,
                reviewer_notes="Confirmed correct",
            )
            apply_review_decision(annotation, decision)
        
        # 7. Get promotable annotations
        promotable = get_promotable_annotations(graph_result.all_annotations)
        assert len(promotable) == len(graph_result.all_annotations)
        
        # 8. Generate documentation
        generator = DocumentationGenerator()
        doc = generator.generate(
            ingestion_result=sample_ingestion_result,
            inferred_annotations=promotable,
            title="Auth Module Documentation",
        )
        
        assert doc.is_regenerable
        assert len(doc.component_docs) > 0
    
    def test_rejection_blocks_promotion(self) -> None:
        """Rejected annotations cannot be promoted."""
        annotation = InferredAnnotation(
            id="ann_1",
            inference_type=InferenceType.COMPONENT_PURPOSE,
            content="Wrong inference",
            evidence=InferenceEvidence(observations=["obs"]),
            confidence=InferenceConfidence.HIGH,
            target_artifact_id="comp_1",
            target_artifact_type="component",
            provenance={"task_id": "task_1"},
        )
        
        # Human rejects
        decision = AnnotationReviewDecision(
            annotation_id="ann_1",
            decision=InferenceStatus.REJECTED,
            reviewer_notes="This is incorrect",
        )
        apply_review_decision(annotation, decision)
        
        # Cannot be promoted
        assert annotation.is_promotable is False
        
        errors = validate_annotation_can_promote(annotation)
        assert any("ACCEPTED" in e for e in errors)
    
    def test_auto_promotion_is_impossible(self) -> None:
        """Annotations cannot auto-promote themselves."""
        annotation = InferredAnnotation(
            id="ann_1",
            inference_type=InferenceType.COMPONENT_PURPOSE,
            content="Test",
            evidence=InferenceEvidence(observations=["obs"]),
            confidence=InferenceConfidence.HIGH,
            target_artifact_id="comp_1",
            target_artifact_type="component",
            provenance={"task_id": "task_1"},
        )
        
        # Even with HIGH confidence, still PROPOSED
        assert annotation.status == InferenceStatus.PROPOSED
        assert annotation.is_promotable is False
        
        # There is no auto-accept method
        assert not hasattr(annotation, "auto_accept")
        assert not hasattr(annotation, "auto_promote")
