"""
LLM Consumption Contract.

This module defines the contract for LLM consumption of Canon summaries.
Explicitly defines:
- Which Canon summaries LLMs may read
- Which fields are exposed
- How summaries are chunked for prompts

LLMs MUST:
- Read summaries, not raw code
- Never bypass Canon

CONSTRAINTS:
- No LLM invocation in this module
- No code execution
- Read-only access to Canon
- Explicit field exposure
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from axiom_canon.ingestion.models import (
    APIExposureSummary,
    ClassSignature,
    ComponentSummary,
    DependencyEdgeSummary,
    FunctionSignature,
    IngestionResult,
    InvariantSummary,
    ModuleSummary,
)


# =============================================================================
# Enums
# =============================================================================


class ChunkingStrategy(str, Enum):
    """Strategy for chunking summaries for LLM prompts."""
    
    BY_MODULE = "by_module"
    BY_COMPONENT = "by_component"
    BY_API = "by_api"
    BY_DEPENDENCY = "by_dependency"
    FLAT = "flat"


class ExposureLevel(str, Enum):
    """Level of detail exposed to LLMs."""
    
    MINIMAL = "minimal"       # IDs and names only
    STANDARD = "standard"     # Names, types, basic structure
    DETAILED = "detailed"     # Full structural information
    FULL = "full"             # Everything except source code


# =============================================================================
# Summary Chunks
# =============================================================================


@dataclass
class SummaryChunk:
    """
    A chunk of summary data prepared for LLM consumption.
    
    Chunks are sized and formatted for efficient LLM context usage.
    
    Attributes:
        chunk_id: Unique identifier for this chunk.
        chunk_type: Type of content (module, component, api, etc.).
        content: The formatted content for LLM consumption.
        source_ids: IDs of source artifacts in this chunk.
        token_estimate: Estimated token count (rough approximation).
        metadata: Additional metadata about the chunk.
    """
    
    chunk_id: str
    chunk_type: str
    content: str
    source_ids: List[str] = field(default_factory=list)
    token_estimate: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "chunk_id": self.chunk_id,
            "chunk_type": self.chunk_type,
            "content": self.content,
            "source_ids": self.source_ids,
            "token_estimate": self.token_estimate,
            "metadata": self.metadata,
        }


# =============================================================================
# LLM Consumption Contract
# =============================================================================


@dataclass
class LLMConsumptionContract:
    """
    Contract defining what Canon data LLMs may access.
    
    This is the BOUNDARY between Canon and LLMs.
    LLMs read through this contract, not directly from Canon.
    
    Attributes:
        exposure_level: Level of detail to expose.
        allowed_fields: Explicit list of allowed fields per artifact type.
        excluded_fields: Explicit list of excluded fields.
        max_chunk_tokens: Maximum estimated tokens per chunk.
        include_human_notes: Whether to include human-editable notes.
    """
    
    exposure_level: ExposureLevel = ExposureLevel.STANDARD
    allowed_fields: Dict[str, List[str]] = field(default_factory=dict)
    excluded_fields: Dict[str, List[str]] = field(default_factory=dict)
    max_chunk_tokens: int = 2000
    include_human_notes: bool = True
    
    def __post_init__(self) -> None:
        """Set default allowed/excluded fields based on exposure level."""
        if not self.allowed_fields:
            self.allowed_fields = self._default_allowed_fields()
        if not self.excluded_fields:
            self.excluded_fields = self._default_excluded_fields()
    
    def _default_allowed_fields(self) -> Dict[str, List[str]]:
        """Get default allowed fields based on exposure level."""
        if self.exposure_level == ExposureLevel.MINIMAL:
            return {
                "module": ["id", "name", "path", "module_type"],
                "component": ["id", "name", "path"],
                "api": ["id", "component_path", "all_exports"],
                "dependency": ["id", "source_path", "target_path"],
                "invariant": ["id", "invariant_type", "description"],
            }
        elif self.exposure_level == ExposureLevel.STANDARD:
            return {
                "module": [
                    "id", "name", "path", "module_type",
                    "functions", "classes", "exports",
                ],
                "component": [
                    "id", "name", "path", "modules", "entry_points",
                ],
                "api": [
                    "id", "component_path", "all_exports",
                    "exposed_functions", "exposed_classes",
                ],
                "dependency": [
                    "id", "source_path", "target_path",
                    "dependency_type", "imported_names",
                ],
                "invariant": [
                    "id", "invariant_type", "description",
                    "source_paths", "is_explicit",
                ],
            }
        elif self.exposure_level == ExposureLevel.DETAILED:
            return {
                "module": [
                    "id", "name", "path", "module_type",
                    "functions", "classes", "imports", "exports", "constants",
                    "human_notes",
                ],
                "component": [
                    "id", "name", "path", "modules", "subcomponents",
                    "entry_points", "config_boundaries", "human_notes",
                ],
                "api": [
                    "id", "component_path", "all_exports",
                    "exposed_functions", "exposed_classes", "exposed_constants",
                    "human_notes",
                ],
                "dependency": [
                    "id", "source_path", "target_path",
                    "dependency_type", "imported_names", "is_direct",
                ],
                "invariant": [
                    "id", "invariant_type", "description",
                    "source_paths", "evidence", "is_explicit", "human_notes",
                ],
            }
        else:  # FULL
            # All fields except source_hash (too technical)
            return {
                "module": [
                    "id", "name", "path", "module_type",
                    "functions", "classes", "imports", "exports", "constants",
                    "version_hash", "human_notes",
                ],
                "component": [
                    "id", "name", "path", "modules", "subcomponents",
                    "entry_points", "config_boundaries", "version_hash", "human_notes",
                ],
                "api": [
                    "id", "component_path", "all_exports",
                    "exposed_functions", "exposed_classes", "exposed_constants",
                    "version_hash", "human_notes",
                ],
                "dependency": [
                    "id", "source_path", "target_path",
                    "dependency_type", "imported_names", "is_direct",
                    "line_numbers", "version_hash",
                ],
                "invariant": [
                    "id", "invariant_type", "description",
                    "source_paths", "evidence", "is_explicit",
                    "version_hash", "human_notes",
                ],
            }
    
    def _default_excluded_fields(self) -> Dict[str, List[str]]:
        """Get default excluded fields."""
        return {
            "module": ["source_hash"],  # Too technical, not useful for LLM
            "component": [],
            "api": [],
            "dependency": [],
            "invariant": [],
        }
    
    def is_field_allowed(self, artifact_type: str, field_name: str) -> bool:
        """
        Check if a field is allowed for LLM consumption.
        
        Args:
            artifact_type: Type of artifact.
            field_name: Name of field.
            
        Returns:
            True if field is allowed.
        """
        # Check exclusions first
        excluded = self.excluded_fields.get(artifact_type, [])
        if field_name in excluded:
            return False
        
        # Check allowed list
        allowed = self.allowed_fields.get(artifact_type, [])
        return field_name in allowed
    
    def filter_artifact(
        self,
        artifact: Any,
        artifact_type: str,
    ) -> Dict[str, Any]:
        """
        Filter an artifact to only allowed fields.
        
        Args:
            artifact: The artifact to filter.
            artifact_type: Type of artifact.
            
        Returns:
            Dictionary with only allowed fields.
        """
        full_dict = artifact.to_dict() if hasattr(artifact, "to_dict") else {}
        
        filtered = {}
        for key, value in full_dict.items():
            if self.is_field_allowed(artifact_type, key):
                # Handle human_notes separately
                if key == "human_notes" and not self.include_human_notes:
                    continue
                filtered[key] = value
        
        return filtered


# =============================================================================
# Formatters
# =============================================================================


def _format_function_signature(func: FunctionSignature) -> str:
    """Format a function signature for LLM consumption."""
    params = ", ".join(
        f"{p.name}: {p.type_annotation or 'Any'}"
        + (f" = {p.default_value}" if p.default_value else "")
        for p in func.parameters
    )
    
    async_prefix = "async " if func.is_async else ""
    return_annotation = f" -> {func.return_type}" if func.return_type else ""
    
    return f"{async_prefix}def {func.name}({params}){return_annotation}"


def _format_class_signature(cls: ClassSignature) -> str:
    """Format a class signature for LLM consumption."""
    bases = ", ".join(cls.bases) if cls.bases else ""
    base_str = f"({bases})" if bases else ""
    
    lines = [f"class {cls.name}{base_str}:"]
    
    # Add method signatures
    for method in cls.methods[:5]:  # Limit to first 5 methods
        method_sig = _format_function_signature(
            FunctionSignature(
                name=method.name,
                parameters=method.parameters,
                return_type=method.return_type,
                visibility=method.visibility,
                is_async=method.is_async,
                decorators=method.decorators,
                line_number=method.line_number,
            )
        )
        lines.append(f"    {method_sig}")
    
    if len(cls.methods) > 5:
        lines.append(f"    # ... and {len(cls.methods) - 5} more methods")
    
    return "\n".join(lines)


def _format_module_summary(
    module: ModuleSummary,
    contract: LLMConsumptionContract,
) -> str:
    """Format a module summary for LLM consumption."""
    lines = [
        f"Module: {module.name}",
        f"  Path: {module.path}",
        f"  Type: {module.module_type.value}",
    ]
    
    # Functions
    if module.functions and contract.is_field_allowed("module", "functions"):
        lines.append("  Functions:")
        for func in module.functions[:10]:
            lines.append(f"    - {_format_function_signature(func)}")
        if len(module.functions) > 10:
            lines.append(f"    # ... and {len(module.functions) - 10} more")
    
    # Classes
    if module.classes and contract.is_field_allowed("module", "classes"):
        lines.append("  Classes:")
        for cls in module.classes[:5]:
            lines.append(f"    - {cls.name}")
            if cls.bases:
                lines.append(f"      Bases: {', '.join(cls.bases)}")
            if cls.methods:
                method_names = [m.name for m in cls.methods[:5]]
                lines.append(f"      Methods: {', '.join(method_names)}")
        if len(module.classes) > 5:
            lines.append(f"    # ... and {len(module.classes) - 5} more classes")
    
    # Exports
    if module.exports and contract.is_field_allowed("module", "exports"):
        export_names = [e.name for e in module.exports[:20]]
        lines.append(f"  Exports: {', '.join(export_names)}")
        if len(module.exports) > 20:
            lines.append(f"    # ... and {len(module.exports) - 20} more")
    
    # Human notes
    if module.human_notes and contract.include_human_notes:
        lines.append(f"  Notes: {module.human_notes}")
    
    return "\n".join(lines)


def _format_api_summary(
    api: APIExposureSummary,
    contract: LLMConsumptionContract,
) -> str:
    """Format an API exposure summary for LLM consumption."""
    lines = [
        f"API: {api.component_path}",
        f"  Exports: {', '.join(api.all_exports[:20])}",
    ]
    
    if len(api.all_exports) > 20:
        lines.append(f"    # ... and {len(api.all_exports) - 20} more")
    
    # Functions
    if api.exposed_functions and contract.is_field_allowed("api", "exposed_functions"):
        lines.append("  Public Functions:")
        for func in api.exposed_functions[:10]:
            lines.append(f"    - {_format_function_signature(func)}")
    
    # Classes
    if api.exposed_classes and contract.is_field_allowed("api", "exposed_classes"):
        lines.append("  Public Classes:")
        for cls in api.exposed_classes[:5]:
            lines.append(f"    - {cls.name}")
    
    return "\n".join(lines)


def _format_dependency_summary(dep: DependencyEdgeSummary) -> str:
    """Format a dependency edge for LLM consumption."""
    names = ", ".join(dep.imported_names[:10]) if dep.imported_names else "*"
    if len(dep.imported_names) > 10:
        names += f", ... ({len(dep.imported_names) - 10} more)"
    
    return f"{dep.source_path} -> {dep.target_path}: [{names}]"


def _format_invariant_summary(inv: InvariantSummary) -> str:
    """Format an invariant for LLM consumption."""
    lines = [
        f"Invariant [{inv.invariant_type.value}]: {inv.description}",
        f"  Sources: {', '.join(inv.source_paths[:5])}",
    ]
    
    if inv.is_explicit:
        lines.append("  (Explicit)")
    
    if inv.human_notes:
        lines.append(f"  Notes: {inv.human_notes}")
    
    return "\n".join(lines)


# =============================================================================
# Token Estimation
# =============================================================================


def _estimate_tokens(text: str) -> int:
    """
    Estimate token count for text.
    
    Uses a simple heuristic (words / 0.75) since we can't
    invoke actual tokenizers without dependencies.
    
    Args:
        text: Text to estimate.
        
    Returns:
        Estimated token count.
    """
    # Simple heuristic: ~1 token per 4 characters on average
    return len(text) // 4


# =============================================================================
# Preparation Function
# =============================================================================


def prepare_for_llm(
    result: IngestionResult,
    contract: Optional[LLMConsumptionContract] = None,
    strategy: ChunkingStrategy = ChunkingStrategy.BY_MODULE,
    focus_paths: Optional[List[str]] = None,
) -> List[SummaryChunk]:
    """
    Prepare ingestion result for LLM consumption.
    
    This is the main entry point for LLM access to Canon summaries.
    Returns structured chunks sized for efficient context usage.
    
    Args:
        result: Ingestion result to prepare.
        contract: Consumption contract (uses default if not provided).
        strategy: How to chunk the data.
        focus_paths: Optional list of paths to focus on (filters output).
        
    Returns:
        List of SummaryChunk ready for LLM prompts.
    """
    if contract is None:
        contract = LLMConsumptionContract()
    
    chunks: List[SummaryChunk] = []
    
    if strategy == ChunkingStrategy.BY_MODULE:
        chunks.extend(_chunk_by_module(result, contract, focus_paths))
    elif strategy == ChunkingStrategy.BY_COMPONENT:
        chunks.extend(_chunk_by_component(result, contract, focus_paths))
    elif strategy == ChunkingStrategy.BY_API:
        chunks.extend(_chunk_by_api(result, contract, focus_paths))
    elif strategy == ChunkingStrategy.BY_DEPENDENCY:
        chunks.extend(_chunk_by_dependency(result, contract, focus_paths))
    elif strategy == ChunkingStrategy.FLAT:
        chunks.extend(_chunk_flat(result, contract, focus_paths))
    
    return chunks


def _chunk_by_module(
    result: IngestionResult,
    contract: LLMConsumptionContract,
    focus_paths: Optional[List[str]],
) -> List[SummaryChunk]:
    """Chunk by individual modules."""
    chunks = []
    
    for module in result.modules:
        # Filter by focus paths if provided
        if focus_paths and not any(
            module.path.startswith(fp) for fp in focus_paths
        ):
            continue
        
        content = _format_module_summary(module, contract)
        token_estimate = _estimate_tokens(content)
        
        chunks.append(
            SummaryChunk(
                chunk_id=f"module:{module.id}",
                chunk_type="module",
                content=content,
                source_ids=[module.id],
                token_estimate=token_estimate,
                metadata={
                    "path": module.path,
                    "name": module.name,
                    "type": module.module_type.value,
                },
            )
        )
    
    return chunks


def _chunk_by_component(
    result: IngestionResult,
    contract: LLMConsumptionContract,
    focus_paths: Optional[List[str]],
) -> List[SummaryChunk]:
    """Chunk by components (packages)."""
    chunks = []
    
    for component in result.components:
        # Filter by focus paths if provided
        if focus_paths and not any(
            component.path.startswith(fp) for fp in focus_paths
        ):
            continue
        
        lines = [
            f"Component: {component.name}",
            f"  Path: {component.path}",
            f"  Modules ({len(component.modules)}):",
        ]
        
        for module in component.modules[:10]:
            lines.append(f"    - {module.name}")
        
        if len(component.modules) > 10:
            lines.append(f"    # ... and {len(component.modules) - 10} more")
        
        if component.entry_points:
            lines.append(f"  Entry Points: {len(component.entry_points)}")
        
        content = "\n".join(lines)
        token_estimate = _estimate_tokens(content)
        
        chunks.append(
            SummaryChunk(
                chunk_id=f"component:{component.id}",
                chunk_type="component",
                content=content,
                source_ids=[component.id] + [m.id for m in component.modules],
                token_estimate=token_estimate,
                metadata={
                    "path": component.path,
                    "name": component.name,
                    "module_count": len(component.modules),
                },
            )
        )
    
    return chunks


def _chunk_by_api(
    result: IngestionResult,
    contract: LLMConsumptionContract,
    focus_paths: Optional[List[str]],
) -> List[SummaryChunk]:
    """Chunk by API exposures."""
    chunks = []
    
    for api in result.api_exposures:
        # Filter by focus paths if provided
        if focus_paths and not any(
            api.component_path.startswith(fp) for fp in focus_paths
        ):
            continue
        
        content = _format_api_summary(api, contract)
        token_estimate = _estimate_tokens(content)
        
        chunks.append(
            SummaryChunk(
                chunk_id=f"api:{api.id}",
                chunk_type="api",
                content=content,
                source_ids=[api.id],
                token_estimate=token_estimate,
                metadata={
                    "component_path": api.component_path,
                    "export_count": len(api.all_exports),
                },
            )
        )
    
    return chunks


def _chunk_by_dependency(
    result: IngestionResult,
    contract: LLMConsumptionContract,
    focus_paths: Optional[List[str]],
) -> List[SummaryChunk]:
    """Chunk by dependency relationships."""
    # Group dependencies by source
    deps_by_source: Dict[str, List[DependencyEdgeSummary]] = {}
    
    for dep in result.dependency_edges:
        if focus_paths and not any(
            dep.source_path.startswith(fp) for fp in focus_paths
        ):
            continue
        
        if dep.source_path not in deps_by_source:
            deps_by_source[dep.source_path] = []
        deps_by_source[dep.source_path].append(dep)
    
    chunks = []
    
    for source_path, deps in sorted(deps_by_source.items()):
        lines = [f"Dependencies for: {source_path}"]
        for dep in deps:
            lines.append(f"  -> {_format_dependency_summary(dep)}")
        
        content = "\n".join(lines)
        token_estimate = _estimate_tokens(content)
        
        chunks.append(
            SummaryChunk(
                chunk_id=f"deps:{source_path}",
                chunk_type="dependency",
                content=content,
                source_ids=[d.id for d in deps],
                token_estimate=token_estimate,
                metadata={
                    "source_path": source_path,
                    "dependency_count": len(deps),
                },
            )
        )
    
    return chunks


def _chunk_flat(
    result: IngestionResult,
    contract: LLMConsumptionContract,
    focus_paths: Optional[List[str]],
) -> List[SummaryChunk]:
    """Create a single flat chunk with overview."""
    lines = [
        "PROJECT SUMMARY",
        "=" * 50,
        f"Root: {result.project_root}",
        f"Components: {len(result.components)}",
        f"Modules: {len(result.modules)}",
        f"APIs: {len(result.api_exposures)}",
        f"Dependencies: {len(result.dependency_edges)}",
        f"Invariants: {len(result.invariants)}",
        "",
        "MODULES:",
    ]
    
    for module in result.modules[:30]:
        if focus_paths and not any(
            module.path.startswith(fp) for fp in focus_paths
        ):
            continue
        lines.append(f"  - {module.name} ({module.module_type.value})")
    
    if len(result.modules) > 30:
        lines.append(f"  # ... and {len(result.modules) - 30} more modules")
    
    lines.extend([
        "",
        "INVARIANTS:",
    ])
    
    for inv in result.invariants:
        lines.append(f"  - {inv.description}")
    
    content = "\n".join(lines)
    token_estimate = _estimate_tokens(content)
    
    return [
        SummaryChunk(
            chunk_id="overview",
            chunk_type="overview",
            content=content,
            source_ids=[m.id for m in result.modules],
            token_estimate=token_estimate,
            metadata={
                "component_count": len(result.components),
                "module_count": len(result.modules),
            },
        )
    ]
