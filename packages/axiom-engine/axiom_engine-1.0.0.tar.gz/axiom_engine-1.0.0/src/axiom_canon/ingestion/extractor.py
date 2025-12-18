"""
Code Extractor.

This module implements a deterministic, repomix-style code extractor that:
- Walks the repository
- Parses language-specific ASTs (where possible)
- Extracts modules, public APIs, imports, dependencies
- Emits structured artifacts ONLY

CONSTRAINTS (ABSOLUTE):
- The extractor MUST be deterministic
- The extractor MUST be repeatable
- The extractor MUST produce identical output for identical input
- The extractor MUST fail loudly on ambiguity
- NO LLMs
- NO code execution
- NO inference or guessing
- NO natural-language interpretation

This is EXTRACTION, not REASONING.
"""

import ast
import hashlib
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any

from axiom_canon.ingestion.models import (
    APIExposureSummary,
    ClassSignature,
    ComponentSummary,
    ConfigBoundary,
    DependencyEdgeSummary,
    DependencyType,
    EntryPoint,
    ExportInfo,
    FunctionSignature,
    ImportInfo,
    IngestionManifest,
    IngestionResult,
    InvariantSummary,
    InvariantType,
    MethodSignature,
    ModuleSummary,
    ModuleType,
    ParameterInfo,
    Visibility,
    compute_stable_id,
)


# =============================================================================
# Exceptions
# =============================================================================


class ExtractionError(Exception):
    """
    Error during code extraction.
    
    Raised when extraction fails or encounters ambiguity.
    Extraction should FAIL LOUDLY, not guess.
    """
    
    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        line_number: Optional[int] = None,
    ) -> None:
        """
        Initialize extraction error.
        
        Args:
            message: Error description.
            file_path: File where error occurred.
            line_number: Line number where error occurred.
        """
        self.file_path = file_path
        self.line_number = line_number
        location = ""
        if file_path:
            location = f" in {file_path}"
            if line_number:
                location += f":{line_number}"
        super().__init__(f"{message}{location}")


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class ExtractionConfig:
    """
    Configuration for code extraction.
    
    Controls what is extracted and how.
    
    Attributes:
        include_patterns: Glob patterns of files to include.
        exclude_patterns: Glob patterns of files to exclude.
        extract_private: Whether to extract private members.
        extract_docstrings: Whether to extract docstrings (as structure only).
        max_depth: Maximum directory depth to traverse.
        follow_symlinks: Whether to follow symbolic links.
        config_extensions: File extensions to treat as config files.
    """
    
    include_patterns: List[str] = field(
        default_factory=lambda: ["*.py"]
    )
    exclude_patterns: List[str] = field(
        default_factory=lambda: [
            "__pycache__",
            "*.pyc",
            ".git",
            ".venv",
            "venv",
            "node_modules",
            ".tox",
            ".pytest_cache",
            "*.egg-info",
            "build",
            "dist",
        ]
    )
    extract_private: bool = False
    extract_docstrings: bool = False
    max_depth: int = 20
    follow_symlinks: bool = False
    config_extensions: List[str] = field(
        default_factory=lambda: [
            ".json", ".yaml", ".yml", ".toml", ".ini", ".env", ".cfg"
        ]
    )
    
    def should_include_file(self, path: Path, root: Path) -> bool:
        """
        Check if a file should be included in extraction.
        
        Args:
            path: File path to check.
            root: Project root path.
            
        Returns:
            True if file should be included.
        """
        rel_path = str(path.relative_to(root))
        
        # Check exclusions first
        for pattern in self.exclude_patterns:
            if pattern in rel_path:
                return False
        
        # Check inclusions
        for pattern in self.include_patterns:
            if path.match(pattern):
                return True
        
        return False
    
    def should_exclude_dir(self, dirname: str) -> bool:
        """
        Check if a directory should be excluded.
        
        Args:
            dirname: Directory name.
            
        Returns:
            True if directory should be excluded.
        """
        for pattern in self.exclude_patterns:
            if pattern.strip("*") in dirname or dirname == pattern:
                return True
        return False


# =============================================================================
# Abstract Base Extractor
# =============================================================================


class CodeExtractor(ABC):
    """
    Abstract base class for code extractors.
    
    Defines the interface for language-specific extractors.
    All extractors MUST be deterministic.
    """
    
    @abstractmethod
    def extract_module(
        self,
        file_path: Path,
        source_content: str,
        project_root: Path,
    ) -> ModuleSummary:
        """
        Extract module summary from source file.
        
        Args:
            file_path: Path to source file.
            source_content: File content as string.
            project_root: Project root path.
            
        Returns:
            ModuleSummary with extracted information.
            
        Raises:
            ExtractionError: If extraction fails.
        """
        pass
    
    @abstractmethod
    def can_handle(self, file_path: Path) -> bool:
        """
        Check if this extractor can handle the file.
        
        Args:
            file_path: Path to check.
            
        Returns:
            True if this extractor can handle the file.
        """
        pass


# =============================================================================
# Python AST Extractor
# =============================================================================


class PythonASTExtractor(CodeExtractor):
    """
    Python AST-based code extractor.
    
    Uses Python's built-in AST module for deterministic extraction.
    Does NOT execute any code.
    
    Extracts:
    - Functions and their signatures
    - Classes and their methods
    - Imports
    - Top-level constants
    - Entry points (if __name__ == "__main__")
    """
    
    def __init__(self, config: Optional[ExtractionConfig] = None) -> None:
        """
        Initialize Python AST extractor.
        
        Args:
            config: Extraction configuration.
        """
        self._config = config or ExtractionConfig()
    
    def can_handle(self, file_path: Path) -> bool:
        """Check if this extractor can handle Python files."""
        return file_path.suffix == ".py"
    
    def extract_module(
        self,
        file_path: Path,
        source_content: str,
        project_root: Path,
    ) -> ModuleSummary:
        """
        Extract module summary from Python source.
        
        Args:
            file_path: Path to Python file.
            source_content: File content.
            project_root: Project root path.
            
        Returns:
            ModuleSummary with extracted information.
            
        Raises:
            ExtractionError: If parsing fails.
        """
        rel_path = str(file_path.relative_to(project_root))
        
        # Parse the AST
        try:
            tree = ast.parse(source_content, filename=str(file_path))
        except SyntaxError as e:
            raise ExtractionError(
                f"Syntax error: {e.msg}",
                file_path=rel_path,
                line_number=e.lineno,
            )
        
        # Determine module name and type
        module_name = self._path_to_module_name(file_path, project_root)
        module_type = self._determine_module_type(file_path, tree)
        
        # Extract components
        functions = self._extract_functions(tree, rel_path)
        classes = self._extract_classes(tree, rel_path)
        imports = self._extract_imports(tree)
        exports = self._extract_exports(tree)
        constants = self._extract_constants(tree)
        
        # Compute stable ID
        stable_id = compute_stable_id("module", rel_path, module_name)
        
        # Compute source hash
        source_hash = hashlib.sha256(source_content.encode("utf-8")).hexdigest()
        
        return ModuleSummary(
            id=stable_id,
            path=rel_path,
            name=module_name,
            module_type=module_type,
            functions=functions,
            classes=classes,
            imports=imports,
            exports=exports,
            constants=constants,
            source_hash=source_hash,
        )
    
    def _path_to_module_name(self, file_path: Path, project_root: Path) -> str:
        """
        Convert file path to Python module name.
        
        Args:
            file_path: Path to Python file.
            project_root: Project root path.
            
        Returns:
            Dotted module name.
        """
        rel_path = file_path.relative_to(project_root)
        parts = list(rel_path.parts)
        
        # Remove .py extension from last part
        if parts[-1].endswith(".py"):
            parts[-1] = parts[-1][:-3]
        
        # Handle __init__.py
        if parts[-1] == "__init__":
            parts = parts[:-1]
        
        return ".".join(parts) if parts else "__main__"
    
    def _determine_module_type(self, file_path: Path, tree: ast.Module) -> ModuleType:
        """
        Determine the type of module.
        
        Args:
            file_path: Path to file.
            tree: Parsed AST.
            
        Returns:
            ModuleType enum value.
        """
        filename = file_path.name
        
        if filename == "__init__.py":
            return ModuleType.INIT
        
        if filename.startswith("test_") or filename.endswith("_test.py"):
            return ModuleType.TEST
        
        if "config" in filename.lower() or "settings" in filename.lower():
            return ModuleType.CONFIG
        
        # Check for if __name__ == "__main__" to identify scripts
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                if self._is_main_check(node):
                    return ModuleType.SCRIPT
        
        return ModuleType.MODULE
    
    def _is_main_check(self, node: ast.If) -> bool:
        """Check if an If node is 'if __name__ == "__main__"'."""
        test = node.test
        if isinstance(test, ast.Compare):
            if len(test.ops) == 1 and isinstance(test.ops[0], ast.Eq):
                left = test.left
                comparators = test.comparators
                if (
                    isinstance(left, ast.Name)
                    and left.id == "__name__"
                    and len(comparators) == 1
                    and isinstance(comparators[0], ast.Constant)
                    and comparators[0].value == "__main__"
                ):
                    return True
        return False
    
    def _extract_functions(
        self,
        tree: ast.Module,
        file_path: str,
    ) -> List[FunctionSignature]:
        """
        Extract top-level function signatures.
        
        Args:
            tree: Parsed AST.
            file_path: File path for error reporting.
            
        Returns:
            List of function signatures.
        """
        functions = []
        
        for node in tree.body:
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                func = self._extract_function_signature(node)
                if self._should_include(func.name):
                    functions.append(func)
        
        # Sort for determinism
        functions.sort(key=lambda f: (f.line_number or 0, f.name))
        return functions
    
    def _extract_function_signature(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> FunctionSignature:
        """
        Extract signature from a function definition.
        
        Args:
            node: AST function definition node.
            
        Returns:
            FunctionSignature.
        """
        # Extract parameters
        parameters = self._extract_parameters(node.args)
        
        # Extract return type
        return_type = None
        if node.returns:
            return_type = self._annotation_to_string(node.returns)
        
        # Determine visibility
        visibility = self._determine_visibility(node.name)
        
        # Extract decorators
        decorators = tuple(self._decorator_to_string(d) for d in node.decorator_list)
        
        return FunctionSignature(
            name=node.name,
            parameters=tuple(parameters),
            return_type=return_type,
            visibility=visibility,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            decorators=decorators,
            line_number=node.lineno,
        )
    
    def _extract_parameters(self, args: ast.arguments) -> List[ParameterInfo]:
        """
        Extract parameter information from function arguments.
        
        Args:
            args: AST arguments node.
            
        Returns:
            List of ParameterInfo.
        """
        parameters = []
        
        # Calculate default offset
        num_defaults = len(args.defaults)
        num_args = len(args.args)
        default_offset = num_args - num_defaults
        
        for i, arg in enumerate(args.args):
            # Skip 'self' and 'cls'
            if arg.arg in ("self", "cls"):
                continue
            
            type_annotation = None
            if arg.annotation:
                type_annotation = self._annotation_to_string(arg.annotation)
            
            default_value = None
            is_required = True
            if i >= default_offset:
                default_idx = i - default_offset
                if default_idx < len(args.defaults):
                    default_value = self._value_to_string(args.defaults[default_idx])
                    is_required = False
            
            parameters.append(
                ParameterInfo(
                    name=arg.arg,
                    type_annotation=type_annotation,
                    default_value=default_value,
                    is_required=is_required,
                )
            )
        
        # Handle *args
        if args.vararg:
            type_annotation = None
            if args.vararg.annotation:
                type_annotation = self._annotation_to_string(args.vararg.annotation)
            parameters.append(
                ParameterInfo(
                    name=f"*{args.vararg.arg}",
                    type_annotation=type_annotation,
                    is_required=False,
                )
            )
        
        # Handle keyword-only args
        for i, arg in enumerate(args.kwonlyargs):
            type_annotation = None
            if arg.annotation:
                type_annotation = self._annotation_to_string(arg.annotation)
            
            default_value = None
            is_required = True
            if i < len(args.kw_defaults) and args.kw_defaults[i] is not None:
                default_value = self._value_to_string(args.kw_defaults[i])
                is_required = False
            
            parameters.append(
                ParameterInfo(
                    name=arg.arg,
                    type_annotation=type_annotation,
                    default_value=default_value,
                    is_required=is_required,
                )
            )
        
        # Handle **kwargs
        if args.kwarg:
            type_annotation = None
            if args.kwarg.annotation:
                type_annotation = self._annotation_to_string(args.kwarg.annotation)
            parameters.append(
                ParameterInfo(
                    name=f"**{args.kwarg.arg}",
                    type_annotation=type_annotation,
                    is_required=False,
                )
            )
        
        return parameters
    
    def _extract_classes(
        self,
        tree: ast.Module,
        file_path: str,
    ) -> List[ClassSignature]:
        """
        Extract class signatures from module.
        
        Args:
            tree: Parsed AST.
            file_path: File path for error reporting.
            
        Returns:
            List of class signatures.
        """
        classes = []
        
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                cls = self._extract_class_signature(node)
                if self._should_include(cls.name):
                    classes.append(cls)
        
        # Sort for determinism
        classes.sort(key=lambda c: (c.line_number or 0, c.name))
        return classes
    
    def _extract_class_signature(self, node: ast.ClassDef) -> ClassSignature:
        """
        Extract signature from a class definition.
        
        Args:
            node: AST class definition node.
            
        Returns:
            ClassSignature.
        """
        # Extract base classes
        bases = tuple(self._annotation_to_string(base) for base in node.bases)
        
        # Extract methods
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                method = self._extract_method_signature(item)
                if self._should_include(method.name):
                    methods.append(method)
        
        # Sort methods for determinism
        methods.sort(key=lambda m: (m.line_number or 0, m.name))
        
        # Extract class attributes
        class_attributes = []
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                attr_name = item.target.id
                attr_type = self._annotation_to_string(item.annotation) if item.annotation else None
                class_attributes.append((attr_name, attr_type))
        
        # Sort attributes for determinism
        class_attributes.sort(key=lambda a: a[0])
        
        # Determine visibility
        visibility = self._determine_visibility(node.name)
        
        # Extract decorators
        decorators = tuple(self._decorator_to_string(d) for d in node.decorator_list)
        
        # Check for special class types
        is_abstract = any("abstract" in str(d).lower() for d in decorators)
        is_dataclass = any("dataclass" in str(d).lower() for d in decorators)
        is_protocol = "Protocol" in bases
        
        return ClassSignature(
            name=node.name,
            bases=bases,
            methods=tuple(methods),
            class_attributes=tuple(class_attributes),
            visibility=visibility,
            decorators=decorators,
            is_abstract=is_abstract,
            is_dataclass=is_dataclass,
            is_protocol=is_protocol,
            line_number=node.lineno,
        )
    
    def _extract_method_signature(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> MethodSignature:
        """
        Extract signature from a method definition.
        
        Args:
            node: AST function definition node.
            
        Returns:
            MethodSignature.
        """
        # Extract parameters (excluding self/cls)
        parameters = self._extract_parameters(node.args)
        
        # Extract return type
        return_type = None
        if node.returns:
            return_type = self._annotation_to_string(node.returns)
        
        # Determine visibility
        visibility = self._determine_visibility(node.name)
        
        # Extract decorators
        decorators = tuple(self._decorator_to_string(d) for d in node.decorator_list)
        
        # Check decorator types
        is_static = any("staticmethod" in str(d) for d in decorators)
        is_classmethod = any("classmethod" in str(d) for d in decorators)
        is_property = any("property" in str(d) for d in decorators)
        
        return MethodSignature(
            name=node.name,
            parameters=tuple(parameters),
            return_type=return_type,
            visibility=visibility,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            is_static=is_static,
            is_classmethod=is_classmethod,
            is_property=is_property,
            decorators=decorators,
            line_number=node.lineno,
        )
    
    def _extract_imports(self, tree: ast.Module) -> List[ImportInfo]:
        """
        Extract import statements from module.
        
        Args:
            tree: Parsed AST.
            
        Returns:
            List of ImportInfo.
        """
        imports = []
        
        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(
                        ImportInfo(
                            module=alias.name,
                            alias=alias.asname,
                            line_number=node.lineno,
                        )
                    )
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                names = tuple(
                    (alias.name, alias.asname) for alias in node.names
                )
                imports.append(
                    ImportInfo(
                        module=module,
                        names=names,
                        is_relative=node.level > 0,
                        level=node.level,
                        line_number=node.lineno,
                    )
                )
        
        # Sort for determinism
        imports.sort(key=lambda i: (i.line_number or 0, i.module))
        return imports
    
    def _extract_exports(self, tree: ast.Module) -> List[ExportInfo]:
        """
        Extract exported symbols from module.
        
        Looks for __all__ definition and public symbols.
        
        Args:
            tree: Parsed AST.
            
        Returns:
            List of ExportInfo.
        """
        exports = []
        all_names: Optional[List[str]] = None
        
        # Look for __all__ definition
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(node.value, ast.List):
                            all_names = []
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                    all_names.append(elt.value)
        
        # If __all__ is defined, use it
        if all_names is not None:
            for name in all_names:
                # Find where this name is defined
                defined_at = self._find_definition(tree, name)
                kind = self._determine_symbol_kind(tree, name)
                exports.append(
                    ExportInfo(name=name, kind=kind, defined_at=defined_at)
                )
        else:
            # Otherwise, collect all public symbols
            for node in tree.body:
                if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                    if not node.name.startswith("_"):
                        exports.append(
                            ExportInfo(
                                name=node.name,
                                kind="function",
                                defined_at=node.lineno,
                            )
                        )
                elif isinstance(node, ast.ClassDef):
                    if not node.name.startswith("_"):
                        exports.append(
                            ExportInfo(
                                name=node.name,
                                kind="class",
                                defined_at=node.lineno,
                            )
                        )
        
        # Sort for determinism
        exports.sort(key=lambda e: e.name)
        return exports
    
    def _extract_constants(self, tree: ast.Module) -> List[Tuple[str, Optional[str], Optional[str]]]:
        """
        Extract top-level constants from module.
        
        Args:
            tree: Parsed AST.
            
        Returns:
            List of (name, type, value_repr) tuples.
        """
        constants = []
        
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name = target.id
                        # Only include UPPER_CASE constants or annotated assignments
                        if name.isupper() or name.startswith("_") is False:
                            if name.isupper():  # Convention for constants
                                value_repr = self._value_to_string(node.value)
                                constants.append((name, None, value_repr))
            
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name):
                    name = node.target.id
                    type_annotation = self._annotation_to_string(node.annotation)
                    value_repr = None
                    if node.value:
                        value_repr = self._value_to_string(node.value)
                    # Only include if it looks like a constant
                    if name.isupper():
                        constants.append((name, type_annotation, value_repr))
        
        # Sort for determinism
        constants.sort(key=lambda c: c[0])
        return constants
    
    def _find_definition(self, tree: ast.Module, name: str) -> Optional[int]:
        """Find the line number where a name is defined."""
        for node in tree.body:
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                if node.name == name:
                    return node.lineno
            elif isinstance(node, ast.ClassDef):
                if node.name == name:
                    return node.lineno
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == name:
                        return node.lineno
        return None
    
    def _determine_symbol_kind(self, tree: ast.Module, name: str) -> str:
        """Determine the kind of a symbol."""
        for node in tree.body:
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                if node.name == name:
                    return "function"
            elif isinstance(node, ast.ClassDef):
                if node.name == name:
                    return "class"
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == name:
                        if name.isupper():
                            return "constant"
                        return "variable"
        return "unknown"
    
    def _determine_visibility(self, name: str) -> Visibility:
        """Determine visibility from naming convention."""
        if name.startswith("__") and not name.endswith("__"):
            return Visibility.PRIVATE
        elif name.startswith("_"):
            return Visibility.PROTECTED
        return Visibility.PUBLIC
    
    def _should_include(self, name: str) -> bool:
        """Check if a name should be included based on config."""
        if self._config.extract_private:
            return True
        return not name.startswith("_") or name.startswith("__") and name.endswith("__")
    
    def _annotation_to_string(self, node: ast.expr) -> str:
        """Convert an AST annotation to string representation."""
        return ast.unparse(node)
    
    def _value_to_string(self, node: ast.expr) -> str:
        """Convert an AST value to string representation."""
        try:
            return ast.unparse(node)
        except Exception:
            return "<complex>"
    
    def _decorator_to_string(self, node: ast.expr) -> str:
        """Convert a decorator to string representation."""
        return ast.unparse(node)


# =============================================================================
# Main Extractor Orchestrator
# =============================================================================


class RepositoryExtractor:
    """
    Main orchestrator for repository extraction.
    
    Coordinates multiple language-specific extractors to produce
    a complete ingestion result.
    
    CONSTRAINTS:
    - Deterministic: same input always produces same output
    - No execution: only parses, never runs code
    - No inference: only extracts observable structure
    """
    
    def __init__(
        self,
        config: Optional[ExtractionConfig] = None,
        extractors: Optional[List[CodeExtractor]] = None,
    ) -> None:
        """
        Initialize repository extractor.
        
        Args:
            config: Extraction configuration.
            extractors: List of language-specific extractors.
        """
        self._config = config or ExtractionConfig()
        self._extractors = extractors or [PythonASTExtractor(self._config)]
    
    def extract(
        self,
        project_root: Path,
        manifest: Optional[IngestionManifest] = None,
        incremental: bool = False,
    ) -> IngestionResult:
        """
        Extract structural information from repository.
        
        Args:
            project_root: Root path of the project.
            manifest: Previous ingestion manifest for incremental updates.
            incremental: Whether to perform incremental extraction.
            
        Returns:
            IngestionResult with all extracted artifacts.
            
        Raises:
            ExtractionError: If extraction fails.
        """
        project_root = project_root.resolve()
        
        if not project_root.exists():
            raise ExtractionError(f"Project root does not exist: {project_root}")
        
        if not project_root.is_dir():
            raise ExtractionError(f"Project root is not a directory: {project_root}")
        
        # Collect all files to process
        files_to_process = self._collect_files(project_root, manifest, incremental)
        
        # Extract modules
        modules: List[ModuleSummary] = []
        file_hashes: Dict[str, str] = {}
        
        for file_path in sorted(files_to_process):  # Sort for determinism
            rel_path = str(file_path.relative_to(project_root))
            
            # Read file content
            try:
                content = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                # Skip binary files
                continue
            
            # Compute file hash
            file_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
            file_hashes[rel_path] = file_hash
            
            # Find appropriate extractor
            for extractor in self._extractors:
                if extractor.can_handle(file_path):
                    module = extractor.extract_module(file_path, content, project_root)
                    modules.append(module)
                    break
        
        # Build component hierarchy
        components = self._build_component_hierarchy(modules, project_root)
        
        # Extract API exposures
        api_exposures = self._extract_api_exposures(modules, project_root)
        
        # Extract dependency edges
        dependency_edges = self._extract_dependency_edges(modules, project_root)
        
        # Extract entry points
        entry_points = self._extract_entry_points(modules)
        
        # Collect config boundaries
        config_boundaries = self._collect_config_boundaries(project_root)
        
        # Extract structural invariants
        invariants = self._extract_invariants(modules, dependency_edges)
        
        # Build result
        timestamp = datetime.now(timezone.utc).isoformat()
        
        return IngestionResult(
            project_root=str(project_root),
            components=components,
            modules=modules,
            api_exposures=api_exposures,
            dependency_edges=dependency_edges,
            invariants=invariants,
            entry_points=entry_points,
            config_boundaries=config_boundaries,
            ingestion_timestamp=timestamp,
        )
    
    def _collect_files(
        self,
        project_root: Path,
        manifest: Optional[IngestionManifest],
        incremental: bool,
    ) -> List[Path]:
        """
        Collect files to process.
        
        Args:
            project_root: Root path of the project.
            manifest: Previous ingestion manifest.
            incremental: Whether to only collect changed files.
            
        Returns:
            List of file paths to process.
        """
        files = []
        
        for root, dirs, filenames in os.walk(
            project_root,
            followlinks=self._config.follow_symlinks,
        ):
            # Filter directories
            dirs[:] = [
                d for d in dirs
                if not self._config.should_exclude_dir(d)
            ]
            
            # Check depth
            rel_root = Path(root).relative_to(project_root)
            if len(rel_root.parts) > self._config.max_depth:
                continue
            
            for filename in filenames:
                file_path = Path(root) / filename
                
                if self._config.should_include_file(file_path, project_root):
                    files.append(file_path)
        
        # If incremental, filter to changed files only
        if incremental and manifest:
            new_hashes = {}
            for file_path in files:
                content = file_path.read_text(encoding="utf-8")
                file_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
                rel_path = str(file_path.relative_to(project_root))
                new_hashes[rel_path] = file_hash
            
            changed = manifest.get_changed_files(new_hashes)
            files = [f for f in files if str(f.relative_to(project_root)) in changed]
        
        return files
    
    def _build_component_hierarchy(
        self,
        modules: List[ModuleSummary],
        project_root: Path,
    ) -> List[ComponentSummary]:
        """
        Build component hierarchy from modules.
        
        Args:
            modules: List of extracted modules.
            project_root: Project root path.
            
        Returns:
            List of top-level component summaries.
        """
        # Group modules by parent directory
        components_by_path: Dict[str, List[ModuleSummary]] = {}
        
        for module in modules:
            parent_path = str(Path(module.path).parent)
            if parent_path not in components_by_path:
                components_by_path[parent_path] = []
            components_by_path[parent_path].append(module)
        
        # Build component summaries
        components = []
        for path, path_modules in sorted(components_by_path.items()):
            component_name = Path(path).name if path != "." else project_root.name
            stable_id = compute_stable_id("component", path, component_name)
            
            components.append(
                ComponentSummary(
                    id=stable_id,
                    path=path,
                    name=component_name,
                    modules=sorted(path_modules, key=lambda m: m.path),
                )
            )
        
        # Sort for determinism
        components.sort(key=lambda c: c.path)
        return components
    
    def _extract_api_exposures(
        self,
        modules: List[ModuleSummary],
        project_root: Path,
    ) -> List[APIExposureSummary]:
        """
        Extract API exposure summaries from modules.
        
        Args:
            modules: List of extracted modules.
            project_root: Project root path.
            
        Returns:
            List of API exposure summaries.
        """
        exposures = []
        
        for module in modules:
            # Only create API exposure for init files (package APIs)
            if module.module_type == ModuleType.INIT:
                stable_id = compute_stable_id("api", module.path, module.name)
                
                # Get exported functions and classes
                export_names = {e.name for e in module.exports}
                exposed_functions = [
                    f for f in module.functions
                    if f.name in export_names or f.visibility == Visibility.PUBLIC
                ]
                exposed_classes = [
                    c for c in module.classes
                    if c.name in export_names or c.visibility == Visibility.PUBLIC
                ]
                exposed_constants = [
                    c for c in module.constants
                    if c[0] in export_names
                ]
                
                exposures.append(
                    APIExposureSummary(
                        id=stable_id,
                        component_path=str(Path(module.path).parent),
                        exposed_functions=exposed_functions,
                        exposed_classes=exposed_classes,
                        exposed_constants=exposed_constants,
                        all_exports=[e.name for e in module.exports],
                    )
                )
        
        # Sort for determinism
        exposures.sort(key=lambda e: e.component_path)
        return exposures
    
    def _extract_dependency_edges(
        self,
        modules: List[ModuleSummary],
        project_root: Path,
    ) -> List[DependencyEdgeSummary]:
        """
        Extract dependency edges from module imports.
        
        Args:
            modules: List of extracted modules.
            project_root: Project root path.
            
        Returns:
            List of dependency edge summaries.
        """
        edges = []
        module_paths = {m.name: m.path for m in modules}
        
        for module in modules:
            for imp in module.imports:
                # Try to resolve import to a local module
                target_path: Optional[str] = None
                
                if imp.is_relative:
                    # Resolve relative import
                    base_path = Path(module.path).parent
                    for _ in range(imp.level - 1):
                        base_path = base_path.parent
                    if imp.module:
                        target_name = ".".join(base_path.parts) + "." + imp.module
                    else:
                        target_name = ".".join(base_path.parts)
                    target_path = module_paths.get(target_name)
                else:
                    # Check if it's a local module
                    target_path = module_paths.get(imp.module)
                    # Also check partial matches (e.g., 'axiom_canon' matches 'axiom_canon.models')
                    if not target_path:
                        for name, path in module_paths.items():
                            if name.startswith(imp.module + ".") or name == imp.module:
                                target_path = path
                                break
                
                if target_path:
                    stable_id = compute_stable_id(
                        "dependency",
                        module.path,
                        f"{module.path}->{target_path}",
                    )
                    
                    imported_names = [n for n, _ in imp.names] if imp.names else []
                    
                    edges.append(
                        DependencyEdgeSummary(
                            id=stable_id,
                            source_path=module.path,
                            target_path=target_path,
                            dependency_type=DependencyType.IMPORT,
                            imported_names=imported_names,
                            line_numbers=[imp.line_number] if imp.line_number else [],
                        )
                    )
        
        # Sort for determinism
        edges.sort(key=lambda e: (e.source_path, e.target_path))
        return edges
    
    def _extract_entry_points(
        self,
        modules: List[ModuleSummary],
    ) -> List[EntryPoint]:
        """
        Extract entry points from modules.
        
        Args:
            modules: List of extracted modules.
            
        Returns:
            List of entry points.
        """
        entry_points = []
        
        for module in modules:
            if module.module_type == ModuleType.SCRIPT:
                entry_points.append(
                    EntryPoint(
                        name=module.name,
                        kind="script",
                        file_path=module.path,
                        function_name="__main__",
                    )
                )
        
        # Sort for determinism
        entry_points.sort(key=lambda e: e.name)
        return entry_points
    
    def _collect_config_boundaries(
        self,
        project_root: Path,
    ) -> List[ConfigBoundary]:
        """
        Collect configuration file boundaries.
        
        Args:
            project_root: Project root path.
            
        Returns:
            List of config boundaries.
        """
        boundaries = []
        
        for ext in self._config.config_extensions:
            for config_file in project_root.rglob(f"*{ext}"):
                # Skip files in excluded directories
                rel_path = config_file.relative_to(project_root)
                skip = False
                for part in rel_path.parts:
                    if self._config.should_exclude_dir(part):
                        skip = True
                        break
                
                if skip:
                    continue
                
                # Determine format
                format_map = {
                    ".json": "json",
                    ".yaml": "yaml",
                    ".yml": "yaml",
                    ".toml": "toml",
                    ".ini": "ini",
                    ".cfg": "ini",
                    ".env": "env",
                }
                config_format = format_map.get(config_file.suffix, "unknown")
                
                boundaries.append(
                    ConfigBoundary(
                        name=config_file.name,
                        file_path=str(rel_path),
                        format=config_format,
                        # Note: we don't parse keys to avoid execution/inference
                    )
                )
        
        # Sort for determinism
        boundaries.sort(key=lambda b: b.file_path)
        return boundaries
    
    def _extract_invariants(
        self,
        modules: List[ModuleSummary],
        edges: List[DependencyEdgeSummary],
    ) -> List[InvariantSummary]:
        """
        Extract observable structural invariants.
        
        Only extracts EXPLICIT invariants:
        - Protocol definitions
        - Abstract base classes
        - Type annotations
        
        Does NOT infer or guess.
        
        Args:
            modules: List of extracted modules.
            edges: List of dependency edges.
            
        Returns:
            List of invariant summaries.
        """
        invariants = []
        
        for module in modules:
            for cls in module.classes:
                # Detect Protocol/ABC invariants
                if cls.is_protocol or cls.is_abstract:
                    stable_id = compute_stable_id(
                        "invariant",
                        module.path,
                        f"interface:{cls.name}",
                    )
                    
                    invariants.append(
                        InvariantSummary(
                            id=stable_id,
                            invariant_type=InvariantType.INTERFACE_CONTRACT,
                            description=f"{'Protocol' if cls.is_protocol else 'ABC'}: {cls.name}",
                            source_paths=[module.path],
                            evidence={
                                "class_name": cls.name,
                                "methods": [m.name for m in cls.methods],
                                "is_protocol": cls.is_protocol,
                                "is_abstract": cls.is_abstract,
                            },
                            is_explicit=True,
                        )
                    )
        
        # Sort for determinism
        invariants.sort(key=lambda i: i.id)
        return invariants
