"""
Symbol extraction and analysis patterns from codanna.

Core symbol representation and extraction patterns extracted from codanna's
symbol handling system. Provides Python equivalents for the Rust-based
symbol analysis capabilities.

Based on codanna's Symbol, SymbolKind, and related structures.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union
from enum import Enum, auto
import uuid


class SymbolKind(Enum):
    """Types of symbols that can be extracted from code.
    
    Based on codanna's SymbolKind enum, representing different
    kinds of code elements that can be analyzed.
    """
    Function = auto()
    Method = auto()
    Struct = auto()
    Class = auto()
    Trait = auto()
    Interface = auto()
    Enum = auto()
    Constant = auto()
    Variable = auto()
    TypeAlias = auto()
    Module = auto()
    Package = auto()
    Namespace = auto()
    Constructor = auto()
    Property = auto()
    Field = auto()
    Parameter = auto()
    Import = auto()
    Export = auto()


class Visibility(Enum):
    """Symbol visibility levels.
    
    Based on codanna's visibility system for tracking
    symbol accessibility across module boundaries.
    """
    Public = auto()
    Private = auto()
    Module = auto()  # Package-private or module-level
    Protected = auto()


class ScopeContext(Enum):
    """Scope context for symbols.
    
    Represents the scope in which a symbol is defined,
    affecting its resolution and visibility.
    """
    Global = auto()
    Module = auto()
    Package = auto()
    ClassMember = auto()
    Local = auto()
    Parameter = auto()


@dataclass
class Range:
    """Source code range information.
    
    Represents a location in source code with line/column information.
    Based on codanna's Range structure.
    """
    start_line: int
    start_col: int
    end_line: int
    end_col: int
    
    def __post_init__(self):
        """Validate range values."""
        if self.start_line < 0 or self.start_col < 0:
            raise ValueError("Start position cannot be negative")
        if self.end_line < self.start_line:
            raise ValueError("End line cannot be before start line")
        if self.end_line == self.start_line and self.end_col < self.start_col:
            raise ValueError("End column cannot be before start column on same line")


@dataclass
class FileId:
    """Unique file identifier.
    
    Represents a unique identifier for source files in the system.
    Based on codanna's FileId structure.
    """
    id: Union[int, str, uuid.UUID]
    
    @classmethod
    def from_int(cls, value: int) -> 'FileId':
        """Create FileId from integer."""
        return cls(id=value)
    
    @classmethod
    def from_string(cls, value: str) -> 'FileId':
        """Create FileId from string."""
        return cls(id=value)
    
    @classmethod
    def generate(cls) -> 'FileId':
        """Generate a new unique FileId."""
        return cls(id=uuid.uuid4())
    
    def __str__(self) -> str:
        return str(self.id)
    
    def __hash__(self) -> int:
        return hash(self.id)


@dataclass
class SymbolId:
    """Unique symbol identifier.
    
    Represents a unique identifier for symbols in the system.
    Based on codanna's SymbolId structure.
    """
    id: Union[int, str, uuid.UUID]
    
    @classmethod
    def from_int(cls, value: int) -> 'SymbolId':
        """Create SymbolId from integer."""
        return cls(id=value)
    
    @classmethod
    def from_string(cls, value: str) -> 'SymbolId':
        """Create SymbolId from string."""
        return cls(id=value)
    
    @classmethod
    def generate(cls) -> 'SymbolId':
        """Generate a new unique SymbolId."""
        return cls(id=uuid.uuid4())
    
    def __str__(self) -> str:
        return str(self.id)
    
    def __hash__(self) -> int:
        return hash(self.id)


@dataclass
class Symbol:
    """Core symbol representation.
    
    Based on codanna's Symbol structure, representing a code symbol
    with all its metadata and relationships.
    """
    id: SymbolId
    name: str
    kind: SymbolKind
    file_id: FileId
    range: Range
    
    # Optional metadata
    signature: Optional[str] = None
    doc_comment: Optional[str] = None
    module_path: Optional[str] = None
    visibility: Visibility = Visibility.Public
    scope_context: Optional[ScopeContext] = None
    
    # Parent relationships
    parent_class: Optional[str] = None
    parent_function: Optional[str] = None
    parent_module: Optional[str] = None
    
    # Type information
    type_annotation: Optional[str] = None
    return_type: Optional[str] = None
    parameters: List[str] = field(default_factory=list)
    
    # Additional metadata
    is_async: bool = False
    is_static: bool = False
    is_abstract: bool = False
    is_generic: bool = False
    
    # Custom attributes
    attributes: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def new(cls, symbol_id: SymbolId, name: str, kind: SymbolKind, 
            file_id: FileId, range: Range) -> 'Symbol':
        """Create a new Symbol with required fields.
        
        Convenience constructor matching codanna's Symbol::new pattern.
        """
        return cls(
            id=symbol_id,
            name=name,
            kind=kind,
            file_id=file_id,
            range=range
        )
    
    def is_callable(self) -> bool:
        """Check if this symbol represents a callable entity."""
        return self.kind in (SymbolKind.Function, SymbolKind.Method, SymbolKind.Constructor)
    
    def is_type_definition(self) -> bool:
        """Check if this symbol represents a type definition."""
        return self.kind in (
            SymbolKind.Class, SymbolKind.Struct, SymbolKind.Interface,
            SymbolKind.Trait, SymbolKind.Enum, SymbolKind.TypeAlias
        )
    
    def is_container(self) -> bool:
        """Check if this symbol can contain other symbols."""
        return self.kind in (
            SymbolKind.Class, SymbolKind.Module, SymbolKind.Package,
            SymbolKind.Namespace, SymbolKind.Trait, SymbolKind.Interface
        )


class SymbolCounter:
    """Counter for generating unique symbol IDs.
    
    Based on codanna's SymbolCounter for ensuring unique symbol identification.
    """
    
    def __init__(self, start_id: int = 1):
        self._current_id = start_id
    
    def next_id(self) -> SymbolId:
        """Generate the next unique symbol ID."""
        symbol_id = SymbolId.from_int(self._current_id)
        self._current_id += 1
        return symbol_id
    
    def current(self) -> int:
        """Get current counter value."""
        return self._current_id


@dataclass
class SymbolRelationship:
    """Represents a relationship between symbols.
    
    Based on codanna's relationship tracking for symbol analysis.
    """
    source: SymbolId
    target: SymbolId
    relationship_type: str
    range: Optional[Range] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class RelationshipKind(Enum):
    """Types of relationships between symbols.
    
    Based on codanna's RelationKind for tracking symbol relationships.
    """
    Calls = auto()
    Extends = auto()
    Implements = auto()
    Uses = auto()
    Defines = auto()
    References = auto()
    Contains = auto()
    Imports = auto()
    Exports = auto()


class SymbolExtractor(ABC):
    """Abstract base class for symbol extraction.
    
    Provides the interface for extracting symbols from source code,
    based on codanna's extraction patterns.
    """
    
    @abstractmethod
    def extract_symbols(self, code: str, file_id: FileId) -> List[Symbol]:
        """Extract symbols from source code.
        
        Args:
            code: Source code to analyze
            file_id: Unique identifier for the file
            
        Returns:
            List of extracted symbols
        """
        pass
    
    @abstractmethod
    def extract_relationships(self, code: str, symbols: List[Symbol]) -> List[SymbolRelationship]:
        """Extract relationships between symbols.
        
        Args:
            code: Source code to analyze
            symbols: Previously extracted symbols
            
        Returns:
            List of symbol relationships
        """
        pass
    
    def extract_with_relationships(self, code: str, file_id: FileId) -> tuple[List[Symbol], List[SymbolRelationship]]:
        """Extract both symbols and relationships in one pass.
        
        Convenience method that extracts symbols and then relationships.
        
        Args:
            code: Source code to analyze
            file_id: Unique identifier for the file
            
        Returns:
            Tuple of (symbols, relationships)
        """
        symbols = self.extract_symbols(code, file_id)
        relationships = self.extract_relationships(code, symbols)
        return symbols, relationships


class SymbolIndex:
    """In-memory symbol index for fast lookups.
    
    Provides fast symbol lookup capabilities based on codanna's
    indexing patterns.
    """
    
    def __init__(self):
        self._symbols: Dict[SymbolId, Symbol] = {}
        self._by_name: Dict[str, List[Symbol]] = {}
        self._by_file: Dict[FileId, List[Symbol]] = {}
        self._by_kind: Dict[SymbolKind, List[Symbol]] = {}
        self._relationships: List[SymbolRelationship] = []
    
    def add_symbol(self, symbol: Symbol):
        """Add a symbol to the index."""
        self._symbols[symbol.id] = symbol
        
        # Index by name
        if symbol.name not in self._by_name:
            self._by_name[symbol.name] = []
        self._by_name[symbol.name].append(symbol)
        
        # Index by file
        if symbol.file_id not in self._by_file:
            self._by_file[symbol.file_id] = []
        self._by_file[symbol.file_id].append(symbol)
        
        # Index by kind
        if symbol.kind not in self._by_kind:
            self._by_kind[symbol.kind] = []
        self._by_kind[symbol.kind].append(symbol)
    
    def add_relationship(self, relationship: SymbolRelationship):
        """Add a relationship to the index."""
        self._relationships.append(relationship)
    
    def get_symbol(self, symbol_id: SymbolId) -> Optional[Symbol]:
        """Get symbol by ID."""
        return self._symbols.get(symbol_id)
    
    def find_symbols_by_name(self, name: str) -> List[Symbol]:
        """Find symbols by name."""
        return self._by_name.get(name, []).copy()
    
    def find_symbols_by_file(self, file_id: FileId) -> List[Symbol]:
        """Find symbols in a file."""
        return self._by_file.get(file_id, []).copy()
    
    def find_symbols_by_kind(self, kind: SymbolKind) -> List[Symbol]:
        """Find symbols by kind."""
        return self._by_kind.get(kind, []).copy()
    
    def find_relationships(self, source: Optional[SymbolId] = None, 
                          target: Optional[SymbolId] = None,
                          relationship_type: Optional[str] = None) -> List[SymbolRelationship]:
        """Find relationships matching criteria."""
        results = []
        for rel in self._relationships:
            if source is not None and rel.source != source:
                continue
            if target is not None and rel.target != target:
                continue
            if relationship_type is not None and rel.relationship_type != relationship_type:
                continue
            results.append(rel)
        return results
    
    def get_all_symbols(self) -> List[Symbol]:
        """Get all symbols in the index."""
        return list(self._symbols.values())
    
    def clear(self):
        """Clear all symbols and relationships."""
        self._symbols.clear()
        self._by_name.clear()
        self._by_file.clear()
        self._by_kind.clear()
        self._relationships.clear()
    
    def symbol_count(self) -> int:
        """Get total number of symbols."""
        return len(self._symbols)
    
    def relationship_count(self) -> int:
        """Get total number of relationships."""
        return len(self._relationships)