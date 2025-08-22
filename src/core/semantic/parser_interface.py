"""
Language parser interface patterns extracted from codanna.

Provides the core abstractions for language-specific parsing using tree-sitter,
based on the patterns from codanna/src/parsing/parser.rs.

Key Components:
- LanguageParser trait equivalent for Python parsers
- ParserFactory for creating parser instances
- Method call and relationship extraction interfaces
- Symbol processing and documentation extraction
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Any, Dict
from dataclasses import dataclass
from enum import Enum

from .symbol_extraction import Symbol, Range, FileId
from .language_registry import LanguageId


@dataclass
class MethodCall:
    """Represents a method call with receiver information.
    
    Based on codanna's MethodCall structure for tracking
    method invocations with enhanced receiver tracking.
    """
    caller: str
    target: str
    range: Range
    receiver_type: Optional[str] = None
    is_static: bool = False
    
    @classmethod
    def from_legacy_format(cls, caller: str, target: str, range: Range) -> 'MethodCall':
        """Create MethodCall from legacy (caller, target, range) format."""
        return cls(caller=caller, target=target, range=range)


@dataclass
class Import:
    """Represents an import statement.
    
    Based on codanna's Import structure for tracking
    import statements and their resolution.
    """
    path: str
    alias: Optional[str]
    file_id: FileId
    range: Range
    is_glob: bool = False


class LanguageParser(ABC):
    """Common interface for all language parsers.
    
    Based on codanna's LanguageParser trait - defines the common interface
    that all language parsers must implement to work with the indexing system.
    """
    
    @abstractmethod
    def parse(self, code: str, file_id: FileId, symbol_counter) -> List[Symbol]:
        """Parse source code and extract symbols.
        
        Args:
            code: Source code to parse
            file_id: Unique identifier for the file
            symbol_counter: Counter for generating unique symbol IDs
            
        Returns:
            List of extracted symbols
        """
        pass
    
    @abstractmethod
    def extract_doc_comment(self, node: Any, code: str) -> Optional[str]:
        """Extract documentation comment for a node.
        
        Each language has its own documentation conventions:
        - Rust: `///` and `/** */`
        - Python: Docstrings (first string literal)
        - JavaScript/TypeScript: JSDoc `/** */`
        
        Args:
            node: Tree-sitter node
            code: Source code
            
        Returns:
            Documentation comment if found
        """
        pass
    
    @abstractmethod
    def find_calls(self, code: str) -> List[Tuple[str, str, Range]]:
        """Find function/method calls in the code.
        
        Returns tuples of (caller_name, callee_name, range).
        Zero-cost: Returns string slices into the source code.
        
        Args:
            code: Source code to analyze
            
        Returns:
            List of (caller, callee, range) tuples
        """
        pass
    
    def find_method_calls(self, code: str) -> List[MethodCall]:
        """Find method calls with rich receiver information.
        
        Default implementation converts from find_calls() for backward compatibility.
        Parsers can override this method to provide enhanced receiver tracking.
        
        Args:
            code: Source code to analyze
            
        Returns:
            List of MethodCall structures with receiver information
        """
        calls = self.find_calls(code)
        return [MethodCall.from_legacy_format(caller, target, range) 
                for caller, target, range in calls]
    
    @abstractmethod
    def find_implementations(self, code: str) -> List[Tuple[str, str, Range]]:
        """Find trait/interface implementations.
        
        Returns tuples of (type_name, trait_name, range).
        Zero-cost: Returns string slices into the source code.
        
        Args:
            code: Source code to analyze
            
        Returns:
            List of (type, trait, range) tuples
        """
        pass
    
    def find_extends(self, code: str) -> List[Tuple[str, str, Range]]:
        """Find inheritance relationships (extends for classes/interfaces).
        
        Returns tuples of (derived_type, base_type, range).
        Zero-cost: Returns string slices into the source code.
        Default implementation returns empty for languages without inheritance.
        
        Args:
            code: Source code to analyze
            
        Returns:
            List of (derived, base, range) tuples
        """
        return []
    
    @abstractmethod
    def find_uses(self, code: str) -> List[Tuple[str, str, Range]]:
        """Find type usage (in fields, parameters, returns).
        
        Returns tuples of (context_name, used_type, range).
        Zero-cost: Returns string slices into the source code.
        
        Args:
            code: Source code to analyze
            
        Returns:
            List of (context, type, range) tuples
        """
        pass
    
    @abstractmethod
    def find_defines(self, code: str) -> List[Tuple[str, str, Range]]:
        """Find method definitions (in traits/interfaces or types).
        
        Returns tuples of (definer_name, method_name, range).
        Zero-cost: Returns string slices into the source code.
        
        Args:
            code: Source code to analyze
            
        Returns:
            List of (definer, method, range) tuples
        """
        pass
    
    @abstractmethod
    def find_imports(self, code: str, file_id: FileId) -> List[Import]:
        """Find import statements in the code.
        
        Returns Import structures with path, alias, and glob information.
        
        Args:
            code: Source code to analyze
            file_id: File identifier for the imports
            
        Returns:
            List of Import structures
        """
        pass
    
    @abstractmethod
    def language(self) -> LanguageId:
        """Get the language this parser handles."""
        pass
    
    def find_variable_types(self, code: str) -> List[Tuple[str, str, Range]]:
        """Extract variable bindings with their types.
        
        Returns tuples of (variable_name, type_name, range).
        Zero-cost: Returns string slices into the source code.
        Default implementation returns empty - languages can override.
        
        Args:
            code: Source code to analyze
            
        Returns:
            List of (variable, type, range) tuples
        """
        return []
    
    def find_inherent_methods(self, code: str) -> List[Tuple[str, str, Range]]:
        """Find inherent methods (methods defined directly on types).
        
        Returns tuples of (type_name, method_name, range).
        This is for methods defined directly on types (not through traits/interfaces).
        Default implementation returns empty - languages can override.
        
        Note: Returns owned strings to support complex type names that need construction
        (e.g., Rust's `Option<String>`, `Vec<T>`, etc.)
        
        Args:
            code: Source code to analyze
            
        Returns:
            List of (type, method, range) tuples
        """
        return []


class ParserFactory(ABC):
    """Trait for creating language parsers.
    
    Based on codanna's ParserFactory trait for creating parser instances.
    """
    
    @abstractmethod
    def create(self) -> LanguageParser:
        """Create a new parser instance.
        
        Returns:
            New parser instance
            
        Raises:
            Exception: If parser creation fails
        """
        pass


class TreeSitterParser(LanguageParser):
    """Base class for tree-sitter based parsers.
    
    Provides common functionality for parsers using tree-sitter,
    extracting common patterns from codanna's language-specific parsers.
    """
    
    def __init__(self, language_id: LanguageId, tree_sitter_language: Any):
        """Initialize with tree-sitter language.
        
        Args:
            language_id: Language identifier
            tree_sitter_language: Tree-sitter language object
        """
        self._language_id = language_id
        self._ts_language = tree_sitter_language
        self._parser = None
        self._init_parser()
    
    def _init_parser(self):
        """Initialize the tree-sitter parser."""
        try:
            import tree_sitter
            self._parser = tree_sitter.Parser()
            self._parser.set_language(self._ts_language)
        except ImportError:
            raise ImportError("tree-sitter-python is required for parsing")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize {self._language_id} parser: {e}")
    
    def language(self) -> LanguageId:
        """Get the language this parser handles."""
        return self._language_id
    
    def _parse_tree(self, code: str):
        """Parse code into tree-sitter AST."""
        if self._parser is None:
            raise RuntimeError("Parser not initialized")
        
        code_bytes = code.encode('utf-8')
        return self._parser.parse(code_bytes)
    
    def _node_to_range(self, node: Any) -> Range:
        """Convert tree-sitter node to Range."""
        return Range(
            start_line=node.start_point[0],
            start_col=node.start_point[1],
            end_line=node.end_point[0],
            end_col=node.end_point[1]
        )
    
    def _get_node_text(self, node: Any, code: str) -> str:
        """Extract text content from a tree-sitter node."""
        start_byte = node.start_byte
        end_byte = node.end_byte
        code_bytes = code.encode('utf-8')
        return code_bytes[start_byte:end_byte].decode('utf-8')
    
    def _find_child_by_type(self, node: Any, node_type: str) -> Optional[Any]:
        """Find first child node of specified type."""
        for child in node.children:
            if child.type == node_type:
                return child
        return None
    
    def _find_children_by_type(self, node: Any, node_type: str) -> List[Any]:
        """Find all child nodes of specified type."""
        return [child for child in node.children if child.type == node_type]


class LanguageParserRegistry:
    """Registry for managing parser factories by language.
    
    Provides a centralized way to register and create parsers
    for different languages.
    """
    
    def __init__(self):
        self._factories: Dict[LanguageId, ParserFactory] = {}
    
    def register_factory(self, language_id: LanguageId, factory: ParserFactory):
        """Register a parser factory for a language.
        
        Args:
            language_id: Language identifier
            factory: Parser factory instance
        """
        self._factories[language_id] = factory
    
    def create_parser(self, language_id: LanguageId) -> Optional[LanguageParser]:
        """Create a parser for the specified language.
        
        Args:
            language_id: Language to create parser for
            
        Returns:
            Parser instance or None if language not supported
        """
        factory = self._factories.get(language_id)
        if factory is None:
            return None
        
        return factory.create()
    
    def get_supported_languages(self) -> List[LanguageId]:
        """Get list of supported language IDs."""
        return list(self._factories.keys())


# Global parser registry instance
_parser_registry = LanguageParserRegistry()


def register_parser_factory(language_id: LanguageId, factory: ParserFactory):
    """Register a parser factory with the global registry."""
    _parser_registry.register_factory(language_id, factory)


def create_parser(language_id: LanguageId) -> Optional[LanguageParser]:
    """Create a parser from the global registry."""
    return _parser_registry.create_parser(language_id)