"""
Language-specific behavior abstraction patterns from codanna.

Extracted from codanna/src/parsing/language_behavior.rs - provides Python
implementation of the LanguageBehavior trait system for encapsulating
language-specific logic.

Key Features:
- Language-agnostic indexing core
- Language-specific formatting and visibility rules
- Import resolution and module path handling
- Symbol resolution and scoping
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass

from .symbol_extraction import Symbol, SymbolId, FileId, Visibility
from .resolution import ResolutionScope, InheritanceResolver, GenericResolutionContext, GenericInheritanceResolver
from .parser_interface import Import


@dataclass
class LanguageMetadata:
    """Language metadata from tree-sitter."""
    abi_version: int
    node_kind_count: int
    field_count: int
    
    @classmethod
    def from_language(cls, language: Any) -> 'LanguageMetadata':
        """Create metadata from a tree-sitter Language."""
        return cls(
            abi_version=getattr(language, 'abi_version', 14),
            node_kind_count=getattr(language, 'node_kind_count', 0),
            field_count=getattr(language, 'field_count', 0)
        )


class LanguageBehavior(ABC):
    """Trait for language-specific behavior and configuration.
    
    This trait extracts all language-specific logic from the indexer,
    making the system truly language-agnostic. Each language parser
    is paired with a behavior implementation that knows how to:
    - Format module paths according to language conventions
    - Parse visibility from signatures
    - Handle import resolution and scoping rules
    - Validate node types using tree-sitter metadata
    
    Design Principles:
    1. Zero allocation where possible: Methods return static strings or reuse inputs
    2. Language agnostic core: The indexer should never check language types
    3. Extensible: New languages can be added without modifying existing code
    4. Type safe: Use tree-sitter for compile-time validation
    """
    
    @abstractmethod
    def format_module_path(self, base_path: str, symbol_name: str) -> str:
        """Format a module path according to language conventions.
        
        Examples:
        - Rust: "crate::module::submodule"
        - Python: "module.submodule"
        - PHP: "\\Namespace\\Subnamespace"
        
        Args:
            base_path: Base module path
            symbol_name: Symbol name to append
            
        Returns:
            Formatted module path
        """
        pass
    
    @abstractmethod
    def parse_visibility(self, signature: str) -> Visibility:
        """Parse visibility from a symbol's signature.
        
        Examples:
        - Rust: "pub fn foo()" -> Public
        - Python: "def _foo()" -> Module (single underscore)
        - PHP: "private function foo()" -> Private
        
        Args:
            signature: Symbol signature string
            
        Returns:
            Parsed visibility level
        """
        pass
    
    @abstractmethod
    def module_separator(self) -> str:
        """Get the module separator for this language.
        
        Examples:
        - Rust: "::"
        - Python: "."
        - PHP: "\\"
        
        Returns:
            Module separator string
        """
        pass
    
    def supports_traits(self) -> bool:
        """Check if this language supports trait/interface concepts."""
        return False
    
    def supports_inherent_methods(self) -> bool:
        """Check if this language supports inherent methods.
        
        (methods defined directly on types, not through traits)
        """
        return False
    
    @abstractmethod
    def get_language(self) -> Any:
        """Get the tree-sitter Language for metadata access."""
        pass
    
    def validate_node_kind(self, node_kind: str) -> bool:
        """Validate that a node kind exists in this language's grammar.
        
        Uses tree-sitter to check if the node type is valid.
        
        Args:
            node_kind: Node type name to validate
            
        Returns:
            True if valid node kind
        """
        language = self.get_language()
        if hasattr(language, 'id_for_node_kind'):
            return language.id_for_node_kind(node_kind, True) != 0
        return True  # Fallback if not available
    
    def get_abi_version(self) -> int:
        """Get the ABI version of the language grammar."""
        language = self.get_language()
        return getattr(language, 'abi_version', 14)
    
    def configure_symbol(self, symbol: Symbol, module_path: Optional[str] = None):
        """Configure a symbol with language-specific rules.
        
        This is the main entry point for applying language-specific
        configuration to a symbol during indexing.
        
        Args:
            symbol: Symbol to configure
            module_path: Optional module path context
        """
        # Apply module path formatting
        if module_path is not None:
            full_path = self.format_module_path(module_path, symbol.name)
            symbol.module_path = full_path
        
        # Apply visibility parsing
        if symbol.signature is not None:
            symbol.visibility = self.parse_visibility(symbol.signature)
    
    def module_path_from_file(self, file_path: Path, project_root: Path) -> Optional[str]:
        """Calculate the module path from a file path according to language conventions.
        
        This method converts a file system path to a language-specific module path.
        Each language has different conventions for how file paths map to module/namespace paths.
        
        Examples:
        - Rust: "src/foo/bar.rs" → "crate::foo::bar"
        - Python: "src/package/module.py" → "package.module"
        - PHP: "src/Namespace/Class.php" → "\\Namespace\\Class"
        
        Default Implementation:
        Returns None by default. Languages should override this if they have
        specific module path conventions.
        
        Args:
            file_path: Path to the file
            project_root: Root path of the project
            
        Returns:
            Module path string or None
        """
        return None
    
    def resolve_import_path(self, import_path: str, document_index: Any) -> Optional[SymbolId]:
        """Resolve an import path to a symbol ID using language-specific conventions.
        
        This method handles the language-specific logic for resolving import paths
        to actual symbols in the index. Each language has different import semantics
        and path formats.
        
        Examples:
        - Rust: "crate::foo::Bar" → looks for Bar in module crate::foo
        - Python: "package.module.Class" → looks for Class in package.module
        - PHP: "\\App\\Controllers\\UserController" → looks for UserController in \\App\\Controllers
        
        Default Implementation:
        1. Splits the path using the language's module separator
        2. Extracts the symbol name (last segment)
        3. Searches for symbols with that name
        4. Matches against the full module path
        
        Args:
            import_path: Import path to resolve
            document_index: Document index for symbol lookup
            
        Returns:
            Symbol ID if found, None otherwise
        """
        # Split the path using this language's separator
        separator = self.module_separator()
        segments = import_path.split(separator)
        
        if not segments:
            return None
        
        # The symbol name is the last segment
        symbol_name = segments[-1]
        
        # Find symbols with this name
        try:
            candidates = document_index.find_symbols_by_name(symbol_name)
        except:
            return None
        
        # Find the one with matching full module path
        for candidate in candidates:
            if candidate.module_path == import_path:
                return candidate.id
        
        return None
    
    # ========== Resolution Methods ==========
    
    def create_resolution_context(self, file_id: FileId) -> ResolutionScope:
        """Create a language-specific resolution context.
        
        Returns a resolution scope that implements the language's scoping rules.
        Default implementation returns a generic context that works for most languages.
        
        Args:
            file_id: File identifier for context
            
        Returns:
            Resolution scope instance
        """
        return GenericResolutionContext(file_id)
    
    def create_inheritance_resolver(self) -> InheritanceResolver:
        """Create a language-specific inheritance resolver.
        
        Returns an inheritance resolver that handles the language's inheritance model.
        Default implementation returns a generic resolver.
        
        Returns:
            Inheritance resolver instance
        """
        return GenericInheritanceResolver()
    
    def add_import(self, import_stmt: Import):
        """Add an import to the language's import tracking.
        
        Default implementation is a no-op. Languages should override to track imports.
        
        Args:
            import_stmt: Import statement to track
        """
        pass
    
    def register_file(self, path: Path, file_id: FileId, module_path: str):
        """Register a file with its module path.
        
        Default implementation is a no-op. Languages should override to track files.
        
        Args:
            path: File path
            file_id: File identifier
            module_path: Module path for the file
        """
        pass
    
    def resolve_symbol(self, name: str, context: ResolutionScope, document_index: Any) -> Optional[SymbolId]:
        """Resolve a symbol using language-specific resolution rules.
        
        Default implementation delegates to the resolution context.
        
        Args:
            name: Symbol name to resolve
            context: Resolution context
            document_index: Document index for lookup
            
        Returns:
            Symbol ID if resolved, None otherwise
        """
        return context.resolve(name)
    
    def add_trait_impl(self, type_name: str, trait_name: str, file_id: FileId):
        """Add a trait/interface implementation.
        
        Default implementation is a no-op. Languages with traits/interfaces should override.
        
        Args:
            type_name: Type implementing the trait
            trait_name: Trait being implemented
            file_id: File where implementation is defined
        """
        pass
    
    def add_inherent_methods(self, type_name: str, methods: List[str]):
        """Add inherent methods for a type.
        
        Default implementation is a no-op. Languages with inherent methods should override.
        
        Args:
            type_name: Type name
            methods: List of method names
        """
        pass
    
    def add_trait_methods(self, trait_name: str, methods: List[str]):
        """Add methods that a trait/interface defines.
        
        Default implementation is a no-op. Languages with traits/interfaces should override.
        
        Args:
            trait_name: Trait name
            methods: List of method names
        """
        pass
    
    def resolve_method_trait(self, type_name: str, method: str) -> Optional[str]:
        """Resolve which trait/interface provides a method.
        
        Returns the trait/interface name if the method comes from one, None if inherent.
        
        Args:
            type_name: Type name
            method: Method name
            
        Returns:
            Trait name or None
        """
        return None
    
    def format_method_call(self, receiver: str, method: str) -> str:
        """Format a method call for this language.
        
        Default uses the module separator (e.g., Type::method for Rust, Type.method for others)
        
        Args:
            receiver: Receiver type/variable
            method: Method name
            
        Returns:
            Formatted method call
        """
        return f"{receiver}{self.module_separator()}{method}"
    
    def inheritance_relation_name(self) -> str:
        """Get the inheritance relationship name for this language.
        
        Returns "implements" for languages with interfaces, "extends" for inheritance.
        
        Returns:
            Relationship name
        """
        return "implements" if self.supports_traits() else "extends"
    
    def map_relationship(self, language_specific: str) -> str:
        """Map language-specific relationship to generic RelationKind.
        
        Allows languages to define how their concepts map to the generic relationship types.
        
        Args:
            language_specific: Language-specific relationship name
            
        Returns:
            Generic relationship kind
        """
        mapping = {
            "extends": "Extends",
            "implements": "Implements", 
            "inherits": "Extends",
            "uses": "Uses",
            "calls": "Calls",
            "defines": "Defines"
        }
        return mapping.get(language_specific, "References")
    
    # ========== Context Building Methods ==========
    
    def build_resolution_context(self, file_id: FileId, document_index: Any) -> ResolutionScope:
        """Build a complete resolution context for a file.
        
        This is the main entry point for resolution context creation.
        This language-agnostic implementation:
        1. Adds imports tracked by the behavior
        2. Adds resolvable symbols from the current file
        3. Adds visible symbols from other files
        
        Each language controls behavior through its overrides of:
        - get_imports_for_file() - what imports are available
        - resolve_import() - how imports resolve to symbols
        - is_resolvable_symbol() - what symbols can be resolved
        - is_symbol_visible_from_file() - cross-file visibility rules
        
        Args:
            file_id: File identifier
            document_index: Document index for symbol lookup
            
        Returns:
            Complete resolution context
        """
        # Create language-specific resolution context
        context = self.create_resolution_context(file_id)
        
        # 1. Add imported symbols (using behavior's tracked imports)
        imports = self.get_imports_for_file(file_id)
        for import_stmt in imports:
            symbol_id = self.resolve_import(import_stmt, document_index)
            if symbol_id is not None:
                # Use alias if provided, otherwise use the last segment of the path
                name = import_stmt.alias or import_stmt.path.split(self.module_separator())[-1]
                context.add_symbol(name, symbol_id, "Module")
        
        # 2. Add file's module-level symbols
        try:
            file_symbols = document_index.find_symbols_by_file(file_id)
            for symbol in file_symbols:
                if self.is_resolvable_symbol(symbol):
                    context.add_symbol(symbol.name, symbol.id, "Module")
        except:
            pass  # Handle gracefully if index access fails
        
        # 3. Add visible symbols from other files (public/exported symbols)
        try:
            all_symbols = document_index.get_all_symbols(10000)  # Limit for performance
            for symbol in all_symbols:
                # Skip symbols from the current file (already added above)
                if symbol.file_id == file_id:
                    continue
                
                # Check if this symbol is visible from the current file
                if self.is_symbol_visible_from_file(symbol, file_id):
                    context.add_symbol(symbol.name, symbol.id, "Global")
        except:
            pass  # Handle gracefully if index access fails
        
        return context
    
    def is_resolvable_symbol(self, symbol: Symbol) -> bool:
        """Check if a symbol should be resolvable (added to resolution context).
        
        Languages override this to filter which symbols are available for resolution.
        For example, local variables might not be resolvable from other scopes.
        
        Default implementation includes common top-level symbols.
        
        Args:
            symbol: Symbol to check
            
        Returns:
            True if symbol should be resolvable
        """
        from .symbol_extraction import SymbolKind, ScopeContext
        
        # Check scope_context first if available
        if symbol.scope_context is not None:
            if symbol.scope_context in (ScopeContext.Module, ScopeContext.Global, ScopeContext.Package):
                return True
            elif symbol.scope_context in (ScopeContext.Local, ScopeContext.Parameter):
                return False
            elif symbol.scope_context == ScopeContext.ClassMember:
                # Class members might be resolvable depending on visibility
                return symbol.visibility == Visibility.Public
        
        # Fallback to symbol kind for backward compatibility
        resolvable_kinds = {
            SymbolKind.Function, SymbolKind.Method, SymbolKind.Struct,
            SymbolKind.Trait, SymbolKind.Interface, SymbolKind.Class,
            SymbolKind.TypeAlias, SymbolKind.Enum, SymbolKind.Constant
        }
        return symbol.kind in resolvable_kinds
    
    def is_symbol_visible_from_file(self, symbol: Symbol, from_file: FileId) -> bool:
        """Check if a symbol is visible from another file.
        
        Languages implement their visibility rules here.
        For example, Rust checks pub, Python might check __all__, etc.
        
        Default implementation checks basic visibility.
        
        Args:
            symbol: Symbol to check
            from_file: File requesting access
            
        Returns:
            True if symbol is visible from the file
        """
        # Same file: always visible
        if symbol.file_id == from_file:
            return True
        
        # Different file: check visibility
        return symbol.visibility == Visibility.Public
    
    def get_imports_for_file(self, file_id: FileId) -> List[Import]:
        """Get imports for a file.
        
        Returns the list of imports that were registered for this file.
        Languages should track imports when add_import() is called.
        
        Default implementation returns empty (no imports).
        
        Args:
            file_id: File identifier
            
        Returns:
            List of imports for the file
        """
        return []
    
    def resolve_import(self, import_stmt: Import, document_index: Any) -> Optional[SymbolId]:
        """Resolve an import to a symbol ID.
        
        Takes an import and resolves it to an actual symbol in the index.
        Languages implement their specific import resolution logic here.
        
        Default implementation tries basic name matching.
        
        Args:
            import_stmt: Import to resolve
            document_index: Document index for lookup
            
        Returns:
            Symbol ID if resolved, None otherwise
        """
        # Get the importing module path for context
        importing_module = self.get_module_path_for_file(import_stmt.file_id)
        
        # Use enhanced resolution with module context
        return self.resolve_import_path_with_context(
            import_stmt.path,
            importing_module,
            document_index
        )
    
    def import_matches_symbol(self, import_path: str, symbol_module_path: str, 
                            importing_module: Optional[str]) -> bool:
        """Check if an import path matches a symbol's module path.
        
        This allows each language to implement custom matching rules.
        For example, Rust needs to handle relative imports where
        "helpers::func" should match "crate::module::helpers::func"
        when imported from "crate::module".
        
        Default Implementation:
        Exact match only. Languages should override for relative imports.
        
        Args:
            import_path: The import path as written in source
            symbol_module_path: The full module path of the symbol
            importing_module: The module doing the importing (if known)
            
        Returns:
            True if the import matches the symbol
        """
        return import_path == symbol_module_path
    
    def get_module_path_for_file(self, file_id: FileId) -> Optional[str]:
        """Get the module path for a file from behavior state.
        
        Default implementation returns None. Languages with state tracking
        should override to return the module path.
        
        Args:
            file_id: File identifier
            
        Returns:
            Module path or None
        """
        return None
    
    def resolve_import_path_with_context(self, import_path: str, 
                                       importing_module: Optional[str],
                                       document_index: Any) -> Optional[SymbolId]:
        """Enhanced import path resolution with module context.
        
        This is separate from resolve_import_path for backward compatibility.
        The default implementation uses import_matches_symbol for matching.
        
        Args:
            import_path: Import path to resolve
            importing_module: Module doing the importing
            document_index: Document index for lookup
            
        Returns:
            Symbol ID if resolved, None otherwise
        """
        # Split the path using this language's separator
        separator = self.module_separator()
        segments = import_path.split(separator)
        
        if not segments:
            return None
        
        # The symbol name is the last segment
        symbol_name = segments[-1]
        
        # Find symbols with this name (using index for performance)
        try:
            candidates = document_index.find_symbols_by_name(symbol_name)
        except:
            return None
        
        # Find the one with matching module path using language-specific rules
        for candidate in candidates:
            if candidate.module_path is not None:
                if self.import_matches_symbol(import_path, candidate.module_path, importing_module):
                    return candidate.id
        
        return None