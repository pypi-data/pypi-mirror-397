"""
Documentation Generator (Derived Output).

This module generates documentation as a DERIVED VIEW from:
- Canon structural artifacts
- Approved enriched labels
- Accepted inferred annotations

RULES (ABSOLUTE):
- Documentation is REGENERABLE
- Documentation is NEVER authoritative
- Documentation is NEVER written back into Canon

Documentation is a presentation layer, not a source of truth.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from axiom_canon.discovery import (
    InferredAnnotation,
    InferenceStatus,
    InferenceType,
)
from axiom_canon.ingestion.models import (
    ComponentSummary,
    IngestionResult,
    ModuleSummary,
)
from axiom_canon.ingestion.enrichment_models import (
    EnrichedComponentLabel,
    EnrichedInvariant,
    EnrichmentResult,
    ReviewDecision,
)


# =============================================================================
# Documentation Models
# =============================================================================


@dataclass
class ComponentDocumentation:
    """
    Documentation for a single component.
    
    This is a derived view, not authoritative.
    
    Attributes:
        component_id: ID of the component.
        component_name: Name of the component.
        component_path: Path to the component.
        summary: Brief summary (from enriched label if available).
        description: Detailed description (from inferences if available).
        modules: List of module names.
        exports: List of public exports.
        dependencies: List of dependencies.
        invariants: List of invariants.
        generated_at: When documentation was generated.
    """
    
    component_id: str
    component_name: str
    component_path: str
    summary: str = ""
    description: str = ""
    modules: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    invariants: List[str] = field(default_factory=list)
    inferred_content: Dict[str, str] = field(default_factory=dict)
    generated_at: str = ""
    
    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.generated_at:
            self.generated_at = datetime.now(timezone.utc).isoformat()


@dataclass
class ArchitectureOverview:
    """
    High-level architecture overview documentation.
    
    This is a derived view, not authoritative.
    
    Attributes:
        title: Document title.
        summary: High-level summary.
        components: List of component documentation.
        relationships: Description of component relationships.
        patterns: Identified architectural patterns.
        generated_at: When documentation was generated.
    """
    
    title: str
    summary: str = ""
    components: List[ComponentDocumentation] = field(default_factory=list)
    relationships: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    generated_at: str = ""
    
    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.generated_at:
            self.generated_at = datetime.now(timezone.utc).isoformat()


@dataclass
class GeneratedDocumentation:
    """
    Container for all generated documentation.
    
    IMPORTANT: This is DERIVED output.
    It can be regenerated at any time from Canon + approved enrichments.
    
    Attributes:
        title: Main document title.
        architecture_overview: High-level overview.
        component_docs: Per-component documentation.
        source_version_hash: Version hash of Canon used.
        generated_at: When documentation was generated.
        is_regenerable: Always True - documentation can be regenerated.
    """
    
    title: str
    architecture_overview: Optional[ArchitectureOverview] = None
    component_docs: List[ComponentDocumentation] = field(default_factory=list)
    source_version_hash: str = ""
    generated_at: str = ""
    is_regenerable: bool = True  # ALWAYS True
    
    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.generated_at:
            self.generated_at = datetime.now(timezone.utc).isoformat()


# =============================================================================
# Documentation Generator
# =============================================================================


class DocumentationGenerator:
    """
    Generates documentation from Canon and approved enrichments.
    
    This is a DERIVED VIEW generator.
    Documentation is never authoritative.
    Documentation is never written to Canon.
    """
    
    def generate(
        self,
        ingestion_result: IngestionResult,
        enrichment_result: Optional[EnrichmentResult] = None,
        inferred_annotations: Optional[List[InferredAnnotation]] = None,
        title: str = "Project Documentation",
    ) -> GeneratedDocumentation:
        """
        Generate documentation from Canon data.
        
        Args:
            ingestion_result: Canon structural data.
            enrichment_result: Optional enriched labels.
            inferred_annotations: Optional accepted inferences.
            title: Document title.
            
        Returns:
            Generated documentation (derived, regenerable).
        """
        # Filter to only approved enrichments and accepted inferences
        approved_labels = self._get_approved_labels(enrichment_result)
        approved_invariants = self._get_approved_invariants(enrichment_result)
        accepted_inferences = self._get_accepted_inferences(inferred_annotations)
        
        # Generate component docs
        component_docs = []
        for component in ingestion_result.components:
            doc = self._generate_component_doc(
                component=component,
                labels=approved_labels,
                invariants=approved_invariants,
                inferences=accepted_inferences,
            )
            component_docs.append(doc)
        
        # Generate architecture overview
        overview = self._generate_architecture_overview(
            ingestion_result=ingestion_result,
            component_docs=component_docs,
            inferences=accepted_inferences,
        )
        
        return GeneratedDocumentation(
            title=title,
            architecture_overview=overview,
            component_docs=component_docs,
            source_version_hash=ingestion_result.version_hash,
        )
    
    def _get_approved_labels(
        self,
        enrichment_result: Optional[EnrichmentResult],
    ) -> Dict[str, EnrichedComponentLabel]:
        """Get approved enriched labels by component ID."""
        if not enrichment_result:
            return {}
        
        return {
            label.component_id: label
            for label in enrichment_result.component_labels
            if label.review_decision in (ReviewDecision.APPROVED, ReviewDecision.EDITED)
        }
    
    def _get_approved_invariants(
        self,
        enrichment_result: Optional[EnrichmentResult],
    ) -> List[EnrichedInvariant]:
        """Get approved enriched invariants."""
        if not enrichment_result:
            return []
        
        return [
            inv for inv in enrichment_result.invariants
            if inv.review_decision in (ReviewDecision.APPROVED, ReviewDecision.EDITED)
        ]
    
    def _get_accepted_inferences(
        self,
        annotations: Optional[List[InferredAnnotation]],
    ) -> Dict[str, List[InferredAnnotation]]:
        """Get accepted inferences grouped by target artifact."""
        if not annotations:
            return {}
        
        result: Dict[str, List[InferredAnnotation]] = {}
        
        for ann in annotations:
            if ann.status == InferenceStatus.ACCEPTED:
                if ann.target_artifact_id not in result:
                    result[ann.target_artifact_id] = []
                result[ann.target_artifact_id].append(ann)
        
        return result
    
    def _generate_component_doc(
        self,
        component: ComponentSummary,
        labels: Dict[str, EnrichedComponentLabel],
        invariants: List[EnrichedInvariant],
        inferences: Dict[str, List[InferredAnnotation]],
    ) -> ComponentDocumentation:
        """Generate documentation for a single component."""
        doc = ComponentDocumentation(
            component_id=component.id,
            component_name=component.name,
            component_path=component.path,
            modules=[m.name for m in component.modules],
        )
        
        # Add enriched label if available
        if component.id in labels:
            label = labels[component.id]
            doc.summary = label.responsibility_label
            doc.description = label.description
        
        # Collect exports
        for module in component.modules:
            for export in module.exports:
                doc.exports.append(f"{module.name}.{export.name}")
        
        # Collect invariants for this component's files
        component_paths = {m.path for m in component.modules}
        for inv in invariants:
            if inv.source_file in component_paths:
                doc.invariants.append(inv.invariant_text)
        
        # Add accepted inferences
        if component.id in inferences:
            for ann in inferences[component.id]:
                key = ann.inference_type.value
                if key not in doc.inferred_content:
                    doc.inferred_content[key] = ann.content
                else:
                    doc.inferred_content[key] += f"\n{ann.content}"
        
        return doc
    
    def _generate_architecture_overview(
        self,
        ingestion_result: IngestionResult,
        component_docs: List[ComponentDocumentation],
        inferences: Dict[str, List[InferredAnnotation]],
    ) -> ArchitectureOverview:
        """Generate architecture overview."""
        # Build summary from component summaries
        summaries = []
        for doc in component_docs:
            if doc.summary:
                summaries.append(f"- **{doc.component_name}**: {doc.summary}")
        
        summary = "\n".join(summaries) if summaries else "No component summaries available."
        
        # Collect relationships from dependencies
        relationships = []
        for edge in ingestion_result.dependency_edges:
            relationships.append(
                f"{edge.source_module} → {edge.target_module} ({edge.dependency_type.value})"
            )
        
        # Look for architectural pattern inferences
        patterns = []
        for ann_list in inferences.values():
            for ann in ann_list:
                if ann.inference_type == InferenceType.DESIGN_PATTERN:
                    patterns.append(ann.content)
                elif ann.inference_type == InferenceType.ARCHITECTURAL_DECISION:
                    patterns.append(ann.content)
        
        return ArchitectureOverview(
            title="Architecture Overview",
            summary=summary,
            components=component_docs,
            relationships=relationships[:20],  # Limit relationships
            patterns=patterns[:10],  # Limit patterns
        )


# =============================================================================
# Markdown Renderer
# =============================================================================


class MarkdownRenderer:
    """
    Renders documentation as Markdown.
    
    Produces README-style documentation from GeneratedDocumentation.
    """
    
    def render(self, doc: GeneratedDocumentation) -> str:
        """
        Render documentation as Markdown.
        
        Args:
            doc: Generated documentation to render.
            
        Returns:
            Markdown string.
        """
        lines = []
        
        # Title
        lines.append(f"# {doc.title}")
        lines.append("")
        lines.append(f"*Generated: {doc.generated_at}*")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("> **Note**: This documentation is generated and can be regenerated at any time.")
        lines.append("")
        
        # Architecture overview
        if doc.architecture_overview:
            lines.append("## Architecture Overview")
            lines.append("")
            lines.append(doc.architecture_overview.summary)
            lines.append("")
            
            if doc.architecture_overview.patterns:
                lines.append("### Architectural Patterns")
                lines.append("")
                for pattern in doc.architecture_overview.patterns:
                    lines.append(f"- {pattern}")
                lines.append("")
        
        # Components
        lines.append("## Components")
        lines.append("")
        
        for comp_doc in doc.component_docs:
            lines.extend(self._render_component(comp_doc))
        
        return "\n".join(lines)
    
    def _render_component(self, doc: ComponentDocumentation) -> List[str]:
        """Render a single component's documentation."""
        lines = []
        
        lines.append(f"### {doc.component_name}")
        lines.append("")
        lines.append(f"**Path**: `{doc.component_path}`")
        lines.append("")
        
        if doc.summary:
            lines.append(f"**Summary**: {doc.summary}")
            lines.append("")
        
        if doc.description:
            lines.append(doc.description)
            lines.append("")
        
        # Modules
        if doc.modules:
            lines.append("**Modules**:")
            lines.append("")
            for module in doc.modules[:10]:
                lines.append(f"- `{module}`")
            if len(doc.modules) > 10:
                lines.append(f"- ... and {len(doc.modules) - 10} more")
            lines.append("")
        
        # Exports
        if doc.exports:
            lines.append("**Public API**:")
            lines.append("")
            for export in doc.exports[:10]:
                lines.append(f"- `{export}`")
            if len(doc.exports) > 10:
                lines.append(f"- ... and {len(doc.exports) - 10} more")
            lines.append("")
        
        # Invariants
        if doc.invariants:
            lines.append("**Invariants**:")
            lines.append("")
            for inv in doc.invariants:
                lines.append(f"- {inv}")
            lines.append("")
        
        # Inferred content
        if doc.inferred_content:
            lines.append("**Additional Insights** *(from accepted inferences)*:")
            lines.append("")
            for key, content in doc.inferred_content.items():
                lines.append(f"*{key}*: {content}")
                lines.append("")
        
        lines.append("---")
        lines.append("")
        
        return lines


# =============================================================================
# Validation Functions
# =============================================================================


def validate_documentation_is_derived(doc: GeneratedDocumentation) -> bool:
    """
    Validate that documentation is marked as derived.
    
    Documentation MUST:
    - Be regenerable
    - Have a source version hash
    - Never claim to be authoritative
    
    Args:
        doc: The documentation to validate.
        
    Returns:
        True if documentation is properly marked as derived.
    """
    return doc.is_regenerable and bool(doc.source_version_hash)


def validate_documentation_sources(
    doc: GeneratedDocumentation,
    ingestion_result: IngestionResult,
) -> bool:
    """
    Validate that documentation was generated from current Canon.
    
    Args:
        doc: The documentation to validate.
        ingestion_result: Current Canon data.
        
    Returns:
        True if documentation matches current Canon version.
    """
    return doc.source_version_hash == ingestion_result.version_hash
