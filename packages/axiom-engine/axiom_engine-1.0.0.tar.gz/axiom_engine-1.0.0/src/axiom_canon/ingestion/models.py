"""
Code Summary Artifact Models.

This module defines STRICT, SERIALIZABLE schemas for code ingestion artifacts.
These artifacts represent STRUCTURAL UNDERSTANDING extracted from a codebase.

Each artifact MUST include:
- Stable ID (deterministic, content-addressable)
- Source files / paths
- Deterministic content
- Version hash
- Human-editable notes (optional)

CONSTRAINTS:
- No inference or guessing
- No natural-language interpretation
- No semantic summarization
- Pure structural extraction only
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
import hashlib
import json


# =============================================================================
# Enums
# =============================================================================


class Visibility(str, Enum):
    """Visibility level of a code element."""
    
    PUBLIC = "public"
    PRIVATE = "private"
    PROTECTED = "protected"
    INTERNAL = "internal"


class ModuleType(str, Enum):
    """Type of module."""
    
    PACKAGE = "package"
    MODULE = "module"
    SCRIPT = "script"
    INIT = "init"
    TEST = "test"
    CONFIG = "config"


class DependencyType(str, Enum):
    """Type of dependency relationship."""
    
    IMPORT = "import"
    INHERITANCE = "inheritance"
    COMPOSITION = "composition"
    CONFIGURATION = "configuration"
    RUNTIME = "runtime"


class InvariantType(str, Enum):
    """Type of structural invariant."""
    
    TYPE_CONSTRAINT = "type_constraint"
    INTERFACE_CONTRACT = "interface_contract"
    DEPENDENCY_RULE = "dependency_rule"
    NAMING_CONVENTION = "naming_convention"
    LAYER_BOUNDARY = "layer_boundary"


# =============================================================================
# Supporting Types
# =============================================================================


@dataclass(frozen=True)
class ParameterInfo:
    """
    Information about a function/method parameter.
    
    Frozen dataclass ensures deterministic hashing.
    
    Attributes:
        name: Parameter name.
        type_annotation: Type annotation as string (if present).
        default_value: Default value as string (if present).
        is_required: Whether the parameter is required.
    """
    
    name: str
    type_annotation: Optional[str] = None
    default_value: Optional[str] = None
    is_required: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "type_annotation": self.type_annotation,
            "default_value": self.default_value,
            "is_required": self.is_required,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ParameterInfo":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            type_annotation=data.get("type_annotation"),
            default_value=data.get("default_value"),
            is_required=data.get("is_required", True),
        )


@dataclass(frozen=True)
class FunctionSignature:
    """
    Structural signature of a function.
    
    Captures ONLY the structural aspects:
    - Name
    - Parameters
    - Return type
    - Visibility
    
    Does NOT capture:
    - Implementation details
    - Behavior description
    - Semantic meaning
    
    Attributes:
        name: Function name.
        parameters: List of parameter info.
        return_type: Return type annotation as string (if present).
        visibility: Visibility level.
        is_async: Whether the function is async.
        decorators: List of decorator names.
        line_number: Line number in source file.
    """
    
    name: str
    parameters: tuple  # Tuple[ParameterInfo, ...] for frozen
    return_type: Optional[str] = None
    visibility: Visibility = Visibility.PUBLIC
    is_async: bool = False
    decorators: tuple = ()  # Tuple[str, ...] for frozen
    line_number: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "parameters": [p.to_dict() for p in self.parameters],
            "return_type": self.return_type,
            "visibility": self.visibility.value,
            "is_async": self.is_async,
            "decorators": list(self.decorators),
            "line_number": self.line_number,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FunctionSignature":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            parameters=tuple(
                ParameterInfo.from_dict(p) for p in data.get("parameters", [])
            ),
            return_type=data.get("return_type"),
            visibility=Visibility(data.get("visibility", "public")),
            is_async=data.get("is_async", False),
            decorators=tuple(data.get("decorators", [])),
            line_number=data.get("line_number"),
        )


@dataclass(frozen=True)
class MethodSignature:
    """
    Structural signature of a class method.
    
    Extends FunctionSignature with class-specific information.
    
    Attributes:
        name: Method name.
        parameters: List of parameter info (excluding self/cls).
        return_type: Return type annotation as string.
        visibility: Visibility level.
        is_async: Whether the method is async.
        is_static: Whether it's a static method.
        is_classmethod: Whether it's a class method.
        is_property: Whether it's a property.
        decorators: List of decorator names.
        line_number: Line number in source file.
    """
    
    name: str
    parameters: tuple  # Tuple[ParameterInfo, ...]
    return_type: Optional[str] = None
    visibility: Visibility = Visibility.PUBLIC
    is_async: bool = False
    is_static: bool = False
    is_classmethod: bool = False
    is_property: bool = False
    decorators: tuple = ()
    line_number: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "parameters": [p.to_dict() for p in self.parameters],
            "return_type": self.return_type,
            "visibility": self.visibility.value,
            "is_async": self.is_async,
            "is_static": self.is_static,
            "is_classmethod": self.is_classmethod,
            "is_property": self.is_property,
            "decorators": list(self.decorators),
            "line_number": self.line_number,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MethodSignature":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            parameters=tuple(
                ParameterInfo.from_dict(p) for p in data.get("parameters", [])
            ),
            return_type=data.get("return_type"),
            visibility=Visibility(data.get("visibility", "public")),
            is_async=data.get("is_async", False),
            is_static=data.get("is_static", False),
            is_classmethod=data.get("is_classmethod", False),
            is_property=data.get("is_property", False),
            decorators=tuple(data.get("decorators", [])),
            line_number=data.get("line_number"),
        )


@dataclass(frozen=True)
class ClassSignature:
    """
    Structural signature of a class.
    
    Captures ONLY structural aspects:
    - Name
    - Base classes
    - Methods
    - Class attributes
    
    Does NOT capture:
    - Implementation details
    - Behavior description
    - Semantic meaning
    
    Attributes:
        name: Class name.
        bases: List of base class names.
        methods: List of method signatures.
        class_attributes: List of class attribute names with types.
        visibility: Visibility level.
        decorators: List of decorator names.
        is_abstract: Whether it's an abstract class.
        is_dataclass: Whether it's a dataclass.
        is_protocol: Whether it's a Protocol.
        line_number: Line number in source file.
    """
    
    name: str
    bases: tuple = ()  # Tuple[str, ...]
    methods: tuple = ()  # Tuple[MethodSignature, ...]
    class_attributes: tuple = ()  # Tuple[Tuple[str, Optional[str]], ...]
    visibility: Visibility = Visibility.PUBLIC
    decorators: tuple = ()
    is_abstract: bool = False
    is_dataclass: bool = False
    is_protocol: bool = False
    line_number: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "bases": list(self.bases),
            "methods": [m.to_dict() for m in self.methods],
            "class_attributes": [
                {"name": n, "type": t} for n, t in self.class_attributes
            ],
            "visibility": self.visibility.value,
            "decorators": list(self.decorators),
            "is_abstract": self.is_abstract,
            "is_dataclass": self.is_dataclass,
            "is_protocol": self.is_protocol,
            "line_number": self.line_number,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClassSignature":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            bases=tuple(data.get("bases", [])),
            methods=tuple(
                MethodSignature.from_dict(m) for m in data.get("methods", [])
            ),
            class_attributes=tuple(
                (a["name"], a.get("type"))
                for a in data.get("class_attributes", [])
            ),
            visibility=Visibility(data.get("visibility", "public")),
            decorators=tuple(data.get("decorators", [])),
            is_abstract=data.get("is_abstract", False),
            is_dataclass=data.get("is_dataclass", False),
            is_protocol=data.get("is_protocol", False),
            line_number=data.get("line_number"),
        )


@dataclass(frozen=True)
class ImportInfo:
    """
    Information about an import statement.
    
    Attributes:
        module: The module being imported from.
        names: Names imported (empty for 'import module').
        alias: Alias if using 'as' (for module import).
        is_relative: Whether it's a relative import.
        level: Relative import level (number of dots).
        line_number: Line number in source file.
    """
    
    module: str
    names: tuple = ()  # Tuple[Tuple[str, Optional[str]], ...] - (name, alias)
    alias: Optional[str] = None
    is_relative: bool = False
    level: int = 0
    line_number: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "module": self.module,
            "names": [{"name": n, "alias": a} for n, a in self.names],
            "alias": self.alias,
            "is_relative": self.is_relative,
            "level": self.level,
            "line_number": self.line_number,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ImportInfo":
        """Create from dictionary."""
        return cls(
            module=data["module"],
            names=tuple(
                (n["name"], n.get("alias"))
                for n in data.get("names", [])
            ),
            alias=data.get("alias"),
            is_relative=data.get("is_relative", False),
            level=data.get("level", 0),
            line_number=data.get("line_number"),
        )


@dataclass(frozen=True)
class ExportInfo:
    """
    Information about an exported symbol.
    
    Attributes:
        name: The exported symbol name.
        kind: Kind of symbol (function, class, variable, etc.).
        defined_at: Line number where defined.
    """
    
    name: str
    kind: str  # "function", "class", "variable", "constant"
    defined_at: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "kind": self.kind,
            "defined_at": self.defined_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExportInfo":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            kind=data["kind"],
            defined_at=data.get("defined_at"),
        )


@dataclass(frozen=True)
class EntryPoint:
    """
    Information about an entry point.
    
    Attributes:
        name: Entry point name.
        kind: Kind of entry point (main, cli, wsgi, etc.).
        file_path: Path to the file containing the entry point.
        function_name: Name of the entry function.
        line_number: Line number of entry point.
    """
    
    name: str
    kind: str  # "main", "cli", "wsgi", "asgi", "test", "script"
    file_path: str
    function_name: Optional[str] = None
    line_number: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "kind": self.kind,
            "file_path": self.file_path,
            "function_name": self.function_name,
            "line_number": self.line_number,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EntryPoint":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            kind=data["kind"],
            file_path=data["file_path"],
            function_name=data.get("function_name"),
            line_number=data.get("line_number"),
        )


@dataclass(frozen=True)
class ConfigBoundary:
    """
    Information about a configuration boundary.
    
    Attributes:
        name: Configuration name.
        file_path: Path to the configuration file.
        format: Configuration format (json, yaml, toml, ini, etc.).
        keys: Top-level configuration keys (structure only).
    """
    
    name: str
    file_path: str
    format: str  # "json", "yaml", "toml", "ini", "env", "py"
    keys: tuple = ()  # Top-level keys only
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "file_path": self.file_path,
            "format": self.format,
            "keys": list(self.keys),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConfigBoundary":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            file_path=data["file_path"],
            format=data["format"],
            keys=tuple(data.get("keys", [])),
        )


# =============================================================================
# Hashing Utilities
# =============================================================================


def compute_content_hash(content: Dict[str, Any]) -> str:
    """
    Compute a deterministic SHA-256 hash of content.
    
    Uses sorted JSON serialization for determinism.
    
    Args:
        content: Dictionary to hash.
        
    Returns:
        Hex-encoded SHA-256 hash.
    """
    # Sort keys for determinism
    canonical = json.dumps(content, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def compute_stable_id(kind: str, path: str, name: str) -> str:
    """
    Compute a stable, content-addressable ID.
    
    The ID is deterministic and based on:
    - Artifact kind
    - File path
    - Element name
    
    Args:
        kind: Artifact kind (module, component, api, etc.).
        path: File path.
        name: Element name.
        
    Returns:
        Stable ID string.
    """
    content = f"{kind}:{path}:{name}"
    hash_prefix = hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]
    return f"{kind}_{hash_prefix}"


# =============================================================================
# Core Summary Artifacts
# =============================================================================


@dataclass
class ModuleSummary:
    """
    Summary of a single module/file.
    
    Captures the structural aspects of a Python module:
    - Functions defined
    - Classes defined
    - Imports
    - Exports
    
    This is EXTRACTION, not REASONING.
    
    Attributes:
        id: Stable, deterministic ID.
        path: Relative file path from project root.
        name: Module name (dotted notation).
        module_type: Type of module.
        functions: Functions defined in module.
        classes: Classes defined in module.
        imports: Import statements.
        exports: Exported symbols (from __all__ or public).
        constants: Top-level constants.
        version_hash: SHA-256 of content for change detection.
        source_hash: SHA-256 of source file content.
        human_notes: Optional human-editable notes.
    """
    
    id: str
    path: str
    name: str
    module_type: ModuleType
    functions: List[FunctionSignature] = field(default_factory=list)
    classes: List[ClassSignature] = field(default_factory=list)
    imports: List[ImportInfo] = field(default_factory=list)
    exports: List[ExportInfo] = field(default_factory=list)
    constants: List[tuple] = field(default_factory=list)  # (name, type, value_repr)
    version_hash: str = ""
    source_hash: str = ""
    human_notes: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Compute version hash if not provided."""
        if not self.version_hash:
            self.version_hash = self._compute_version_hash()
    
    def _compute_version_hash(self) -> str:
        """Compute version hash from content."""
        content = {
            "path": self.path,
            "name": self.name,
            "module_type": self.module_type.value,
            "functions": [f.to_dict() for f in self.functions],
            "classes": [c.to_dict() for c in self.classes],
            "imports": [i.to_dict() for i in self.imports],
            "exports": [e.to_dict() for e in self.exports],
            "constants": [{"name": n, "type": t, "value": v} for n, t, v in self.constants],
        }
        return compute_content_hash(content)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "path": self.path,
            "name": self.name,
            "module_type": self.module_type.value,
            "functions": [f.to_dict() for f in self.functions],
            "classes": [c.to_dict() for c in self.classes],
            "imports": [i.to_dict() for i in self.imports],
            "exports": [e.to_dict() for e in self.exports],
            "constants": [
                {"name": n, "type": t, "value": v} for n, t, v in self.constants
            ],
            "version_hash": self.version_hash,
            "source_hash": self.source_hash,
            "human_notes": self.human_notes,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModuleSummary":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            path=data["path"],
            name=data["name"],
            module_type=ModuleType(data["module_type"]),
            functions=[
                FunctionSignature.from_dict(f) for f in data.get("functions", [])
            ],
            classes=[
                ClassSignature.from_dict(c) for c in data.get("classes", [])
            ],
            imports=[
                ImportInfo.from_dict(i) for i in data.get("imports", [])
            ],
            exports=[
                ExportInfo.from_dict(e) for e in data.get("exports", [])
            ],
            constants=[
                (c["name"], c.get("type"), c.get("value"))
                for c in data.get("constants", [])
            ],
            version_hash=data.get("version_hash", ""),
            source_hash=data.get("source_hash", ""),
            human_notes=data.get("human_notes"),
        )


@dataclass
class ComponentSummary:
    """
    Summary of a component (package/directory of modules).
    
    A component is a logical grouping of modules that form a
    cohesive unit (e.g., axiom_canon, axiom_strata).
    
    Attributes:
        id: Stable, deterministic ID.
        path: Relative directory path from project root.
        name: Component name.
        modules: Module summaries within this component.
        subcomponents: Nested component summaries.
        entry_points: Entry points defined in this component.
        config_boundaries: Configuration files in this component.
        version_hash: SHA-256 of content for change detection.
        human_notes: Optional human-editable notes.
    """
    
    id: str
    path: str
    name: str
    modules: List[ModuleSummary] = field(default_factory=list)
    subcomponents: List["ComponentSummary"] = field(default_factory=list)
    entry_points: List[EntryPoint] = field(default_factory=list)
    config_boundaries: List[ConfigBoundary] = field(default_factory=list)
    version_hash: str = ""
    human_notes: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Compute version hash if not provided."""
        if not self.version_hash:
            self.version_hash = self._compute_version_hash()
    
    def _compute_version_hash(self) -> str:
        """Compute version hash from content."""
        content = {
            "path": self.path,
            "name": self.name,
            "modules": [m.version_hash for m in self.modules],
            "subcomponents": [s.version_hash for s in self.subcomponents],
            "entry_points": [e.to_dict() for e in self.entry_points],
            "config_boundaries": [c.to_dict() for c in self.config_boundaries],
        }
        return compute_content_hash(content)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "path": self.path,
            "name": self.name,
            "modules": [m.to_dict() for m in self.modules],
            "subcomponents": [s.to_dict() for s in self.subcomponents],
            "entry_points": [e.to_dict() for e in self.entry_points],
            "config_boundaries": [c.to_dict() for c in self.config_boundaries],
            "version_hash": self.version_hash,
            "human_notes": self.human_notes,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ComponentSummary":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            path=data["path"],
            name=data["name"],
            modules=[ModuleSummary.from_dict(m) for m in data.get("modules", [])],
            subcomponents=[
                ComponentSummary.from_dict(s) for s in data.get("subcomponents", [])
            ],
            entry_points=[
                EntryPoint.from_dict(e) for e in data.get("entry_points", [])
            ],
            config_boundaries=[
                ConfigBoundary.from_dict(c) for c in data.get("config_boundaries", [])
            ],
            version_hash=data.get("version_hash", ""),
            human_notes=data.get("human_notes"),
        )


@dataclass
class APIExposureSummary:
    """
    Summary of public API exposure.
    
    Captures what a module/component exposes to external consumers.
    This is the PUBLIC INTERFACE contract.
    
    Attributes:
        id: Stable, deterministic ID.
        component_path: Path of the component exposing the API.
        exposed_functions: Public function signatures.
        exposed_classes: Public class signatures.
        exposed_constants: Public constants.
        all_exports: Names in __all__ (if defined).
        version_hash: SHA-256 of content for change detection.
        human_notes: Optional human-editable notes.
    """
    
    id: str
    component_path: str
    exposed_functions: List[FunctionSignature] = field(default_factory=list)
    exposed_classes: List[ClassSignature] = field(default_factory=list)
    exposed_constants: List[tuple] = field(default_factory=list)
    all_exports: List[str] = field(default_factory=list)
    version_hash: str = ""
    human_notes: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Compute version hash if not provided."""
        if not self.version_hash:
            self.version_hash = self._compute_version_hash()
    
    def _compute_version_hash(self) -> str:
        """Compute version hash from content."""
        content = {
            "component_path": self.component_path,
            "exposed_functions": [f.to_dict() for f in self.exposed_functions],
            "exposed_classes": [c.to_dict() for c in self.exposed_classes],
            "exposed_constants": [
                {"name": n, "type": t, "value": v}
                for n, t, v in self.exposed_constants
            ],
            "all_exports": sorted(self.all_exports),
        }
        return compute_content_hash(content)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "component_path": self.component_path,
            "exposed_functions": [f.to_dict() for f in self.exposed_functions],
            "exposed_classes": [c.to_dict() for c in self.exposed_classes],
            "exposed_constants": [
                {"name": n, "type": t, "value": v}
                for n, t, v in self.exposed_constants
            ],
            "all_exports": self.all_exports,
            "version_hash": self.version_hash,
            "human_notes": self.human_notes,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "APIExposureSummary":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            component_path=data["component_path"],
            exposed_functions=[
                FunctionSignature.from_dict(f)
                for f in data.get("exposed_functions", [])
            ],
            exposed_classes=[
                ClassSignature.from_dict(c)
                for c in data.get("exposed_classes", [])
            ],
            exposed_constants=[
                (c["name"], c.get("type"), c.get("value"))
                for c in data.get("exposed_constants", [])
            ],
            all_exports=data.get("all_exports", []),
            version_hash=data.get("version_hash", ""),
            human_notes=data.get("human_notes"),
        )


@dataclass
class DependencyEdgeSummary:
    """
    Summary of a dependency edge between modules/components.
    
    Captures import relationships and structural dependencies.
    This is OBSERVATION, not inference.
    
    Attributes:
        id: Stable, deterministic ID.
        source_path: Path of the importing module.
        target_path: Path of the imported module.
        dependency_type: Type of dependency.
        imported_names: Specific names imported.
        is_direct: Whether it's a direct import (not transitive).
        line_numbers: Line numbers where imports occur.
        version_hash: SHA-256 of content for change detection.
    """
    
    id: str
    source_path: str
    target_path: str
    dependency_type: DependencyType
    imported_names: List[str] = field(default_factory=list)
    is_direct: bool = True
    line_numbers: List[int] = field(default_factory=list)
    version_hash: str = ""
    
    def __post_init__(self) -> None:
        """Compute version hash if not provided."""
        if not self.version_hash:
            self.version_hash = self._compute_version_hash()
    
    def _compute_version_hash(self) -> str:
        """Compute version hash from content."""
        content = {
            "source_path": self.source_path,
            "target_path": self.target_path,
            "dependency_type": self.dependency_type.value,
            "imported_names": sorted(self.imported_names),
            "is_direct": self.is_direct,
        }
        return compute_content_hash(content)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "source_path": self.source_path,
            "target_path": self.target_path,
            "dependency_type": self.dependency_type.value,
            "imported_names": self.imported_names,
            "is_direct": self.is_direct,
            "line_numbers": self.line_numbers,
            "version_hash": self.version_hash,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DependencyEdgeSummary":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            source_path=data["source_path"],
            target_path=data["target_path"],
            dependency_type=DependencyType(data["dependency_type"]),
            imported_names=data.get("imported_names", []),
            is_direct=data.get("is_direct", True),
            line_numbers=data.get("line_numbers", []),
            version_hash=data.get("version_hash", ""),
        )


@dataclass
class InvariantSummary:
    """
    Summary of a structural invariant.
    
    Captures invariants that can be OBSERVED from code structure:
    - Type constraints (from type annotations)
    - Interface contracts (from abstract classes/protocols)
    - Dependency rules (from import patterns)
    - Naming conventions (from naming patterns)
    - Layer boundaries (from package structure)
    
    This is OBSERVATION, not enforcement.
    
    Attributes:
        id: Stable, deterministic ID.
        invariant_type: Type of invariant.
        description: Structural description (not semantic).
        source_paths: Files where invariant is observed.
        evidence: Specific code evidence (line numbers, symbols).
        is_explicit: Whether explicitly declared (e.g., Protocol).
        version_hash: SHA-256 of content for change detection.
        human_notes: Optional human-editable notes.
    """
    
    id: str
    invariant_type: InvariantType
    description: str
    source_paths: List[str] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)
    is_explicit: bool = False
    version_hash: str = ""
    human_notes: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Compute version hash if not provided."""
        if not self.version_hash:
            self.version_hash = self._compute_version_hash()
    
    def _compute_version_hash(self) -> str:
        """Compute version hash from content."""
        content = {
            "invariant_type": self.invariant_type.value,
            "description": self.description,
            "source_paths": sorted(self.source_paths),
            "evidence": self.evidence,
            "is_explicit": self.is_explicit,
        }
        return compute_content_hash(content)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "invariant_type": self.invariant_type.value,
            "description": self.description,
            "source_paths": self.source_paths,
            "evidence": self.evidence,
            "is_explicit": self.is_explicit,
            "version_hash": self.version_hash,
            "human_notes": self.human_notes,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InvariantSummary":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            invariant_type=InvariantType(data["invariant_type"]),
            description=data["description"],
            source_paths=data.get("source_paths", []),
            evidence=data.get("evidence", {}),
            is_explicit=data.get("is_explicit", False),
            version_hash=data.get("version_hash", ""),
            human_notes=data.get("human_notes"),
        )


# =============================================================================
# Container Types
# =============================================================================


@dataclass
class IngestionResult:
    """
    Result of a single ingestion operation.
    
    Contains all extracted artifacts from a codebase.
    This is a SNAPSHOT of structural understanding.
    
    Attributes:
        project_root: Absolute path to project root.
        components: Top-level component summaries.
        modules: All module summaries (flattened).
        api_exposures: API exposure summaries.
        dependency_edges: Dependency edge summaries.
        invariants: Structural invariant summaries.
        entry_points: All entry points found.
        config_boundaries: All configuration files found.
        ingestion_timestamp: ISO 8601 timestamp of ingestion.
        version_hash: Hash of entire ingestion result.
    """
    
    project_root: str
    components: List[ComponentSummary] = field(default_factory=list)
    modules: List[ModuleSummary] = field(default_factory=list)
    api_exposures: List[APIExposureSummary] = field(default_factory=list)
    dependency_edges: List[DependencyEdgeSummary] = field(default_factory=list)
    invariants: List[InvariantSummary] = field(default_factory=list)
    entry_points: List[EntryPoint] = field(default_factory=list)
    config_boundaries: List[ConfigBoundary] = field(default_factory=list)
    ingestion_timestamp: str = ""
    version_hash: str = ""
    
    def __post_init__(self) -> None:
        """Compute version hash if not provided."""
        if not self.version_hash:
            self.version_hash = self._compute_version_hash()
    
    def _compute_version_hash(self) -> str:
        """Compute version hash from all component hashes."""
        content = {
            "project_root": self.project_root,
            "component_hashes": sorted([c.version_hash for c in self.components]),
            "module_hashes": sorted([m.version_hash for m in self.modules]),
            "api_hashes": sorted([a.version_hash for a in self.api_exposures]),
            "edge_hashes": sorted([e.version_hash for e in self.dependency_edges]),
            "invariant_hashes": sorted([i.version_hash for i in self.invariants]),
        }
        return compute_content_hash(content)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "project_root": self.project_root,
            "components": [c.to_dict() for c in self.components],
            "modules": [m.to_dict() for m in self.modules],
            "api_exposures": [a.to_dict() for a in self.api_exposures],
            "dependency_edges": [e.to_dict() for e in self.dependency_edges],
            "invariants": [i.to_dict() for i in self.invariants],
            "entry_points": [e.to_dict() for e in self.entry_points],
            "config_boundaries": [c.to_dict() for c in self.config_boundaries],
            "ingestion_timestamp": self.ingestion_timestamp,
            "version_hash": self.version_hash,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IngestionResult":
        """Create from dictionary."""
        return cls(
            project_root=data["project_root"],
            components=[
                ComponentSummary.from_dict(c) for c in data.get("components", [])
            ],
            modules=[
                ModuleSummary.from_dict(m) for m in data.get("modules", [])
            ],
            api_exposures=[
                APIExposureSummary.from_dict(a) for a in data.get("api_exposures", [])
            ],
            dependency_edges=[
                DependencyEdgeSummary.from_dict(e)
                for e in data.get("dependency_edges", [])
            ],
            invariants=[
                InvariantSummary.from_dict(i) for i in data.get("invariants", [])
            ],
            entry_points=[
                EntryPoint.from_dict(e) for e in data.get("entry_points", [])
            ],
            config_boundaries=[
                ConfigBoundary.from_dict(c)
                for c in data.get("config_boundaries", [])
            ],
            ingestion_timestamp=data.get("ingestion_timestamp", ""),
            version_hash=data.get("version_hash", ""),
        )


@dataclass
class IngestionManifest:
    """
    Manifest tracking ingestion runs.
    
    Enables incremental updates by tracking what has been ingested.
    
    Attributes:
        project_root: Absolute path to project root.
        last_full_ingestion: Timestamp of last full ingestion.
        last_partial_ingestion: Timestamp of last partial ingestion.
        file_hashes: Mapping of file paths to their content hashes.
        version: Manifest format version.
    """
    
    project_root: str
    last_full_ingestion: Optional[str] = None
    last_partial_ingestion: Optional[str] = None
    file_hashes: Dict[str, str] = field(default_factory=dict)
    version: str = "1.0.0"
    
    def get_changed_files(self, new_file_hashes: Dict[str, str]) -> List[str]:
        """
        Get list of files that have changed since last ingestion.
        
        Args:
            new_file_hashes: Current file hashes.
            
        Returns:
            List of changed file paths.
        """
        changed = []
        for path, new_hash in new_file_hashes.items():
            old_hash = self.file_hashes.get(path)
            if old_hash != new_hash:
                changed.append(path)
        return changed
    
    def get_deleted_files(self, new_file_hashes: Dict[str, str]) -> List[str]:
        """
        Get list of files that have been deleted since last ingestion.
        
        Args:
            new_file_hashes: Current file hashes.
            
        Returns:
            List of deleted file paths.
        """
        return [p for p in self.file_hashes if p not in new_file_hashes]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "project_root": self.project_root,
            "last_full_ingestion": self.last_full_ingestion,
            "last_partial_ingestion": self.last_partial_ingestion,
            "file_hashes": self.file_hashes,
            "version": self.version,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IngestionManifest":
        """Create from dictionary."""
        return cls(
            project_root=data["project_root"],
            last_full_ingestion=data.get("last_full_ingestion"),
            last_partial_ingestion=data.get("last_partial_ingestion"),
            file_hashes=data.get("file_hashes", {}),
            version=data.get("version", "1.0.0"),
        )
