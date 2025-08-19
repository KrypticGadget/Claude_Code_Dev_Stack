"""
Symbol resolution and scoping patterns from codanna.

Extracted from codanna's resolution system - provides Python implementation
of symbol resolution, inheritance tracking, and scoping mechanisms.

Based on codanna/src/parsing/resolution.rs patterns.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum, auto

from .symbol_extraction import SymbolId, FileId


class ScopeLevel(Enum):
    """Scope priority levels for symbol resolution.
    
    Based on codanna's scope level system for determining
    symbol resolution priority.
    """
    Local = auto()      # Highest priority - local scope
    Function = auto()   # Function parameters and locals
    Class = auto()      # Class/type scope
    Module = auto()     # Module/file scope
    Package = auto()    # Package/namespace scope
    Global = auto()     # Lowest priority - global scope


@dataclass
class ScopeEntry:
    """Entry in a resolution scope.
    
    Represents a symbol available for resolution at a specific scope level.
    """
    name: str
    symbol_id: SymbolId
    scope_level: ScopeLevel


class ResolutionScope(ABC):
    """Abstract interface for symbol resolution contexts.
    
    Based on codanna's ResolutionScope trait for handling
    language-specific symbol resolution rules.
    """
    
    @abstractmethod
    def resolve(self, name: str) -> Optional[SymbolId]:
        """Resolve a symbol name to a symbol ID.
        
        Args:
            name: Symbol name to resolve
            
        Returns:
            Symbol ID if found, None otherwise
        """
        pass
    
    @abstractmethod
    def add_symbol(self, name: str, symbol_id: SymbolId, scope_level: ScopeLevel):
        """Add a symbol to the resolution scope.
        
        Args:
            name: Symbol name
            symbol_id: Symbol identifier
            scope_level: Scope level for priority
        """
        pass
    
    @abstractmethod
    def enter_scope(self, scope_type: str):
        """Enter a new scope level.
        
        Args:
            scope_type: Type of scope being entered
        """
        pass
    
    @abstractmethod
    def exit_scope(self):
        """Exit the current scope level."""
        pass
    
    @abstractmethod
    def current_scope(self) -> str:
        """Get the current scope type.
        
        Returns:
            Current scope type
        """
        pass


class GenericResolutionContext(ResolutionScope):
    """Generic resolution context that works for most languages.
    
    Based on codanna's GenericResolutionContext - provides a
    standard implementation of symbol resolution with scope tracking.
    """
    
    def __init__(self, file_id: FileId):
        """Initialize resolution context for a file.
        
        Args:
            file_id: File identifier for this context
        """
        self.file_id = file_id
        self._symbols: Dict[str, List[ScopeEntry]] = {}
        self._scope_stack: List[str] = ["global"]
        self._local_scopes: List[Dict[str, SymbolId]] = [{}]
    
    def resolve(self, name: str) -> Optional[SymbolId]:
        """Resolve a symbol name to a symbol ID.
        
        Resolution priority (highest to lowest):
        1. Local scope (current function/method)
        2. Function scope (parameters)
        3. Class scope (class members)
        4. Module scope (file-level symbols)
        5. Package scope (imported symbols)
        6. Global scope (public symbols from other files)
        
        Args:
            name: Symbol name to resolve
            
        Returns:
            Symbol ID if found, None otherwise
        """
        # Check local scopes first (highest priority)
        for local_scope in reversed(self._local_scopes):
            if name in local_scope:
                return local_scope[name]
        
        # Check symbol entries by scope priority
        if name in self._symbols:
            entries = self._symbols[name]
            
            # Sort by scope priority (Local has highest priority)
            entries_by_priority = sorted(entries, key=lambda e: e.scope_level.value)
            
            if entries_by_priority:
                return entries_by_priority[0].symbol_id
        
        return None
    
    def add_symbol(self, name: str, symbol_id: SymbolId, scope_level: ScopeLevel):
        """Add a symbol to the resolution scope.
        
        Args:
            name: Symbol name
            symbol_id: Symbol identifier
            scope_level: Scope level for priority
        """
        if isinstance(scope_level, str):
            # Handle string scope levels for backward compatibility
            scope_mapping = {
                "Local": ScopeLevel.Local,
                "Function": ScopeLevel.Function,
                "Class": ScopeLevel.Class,
                "Module": ScopeLevel.Module,
                "Package": ScopeLevel.Package,
                "Global": ScopeLevel.Global
            }
            scope_level = scope_mapping.get(scope_level, ScopeLevel.Global)
        
        if name not in self._symbols:
            self._symbols[name] = []
        
        entry = ScopeEntry(name, symbol_id, scope_level)
        self._symbols[name].append(entry)
    
    def enter_scope(self, scope_type: str):
        """Enter a new scope level.
        
        Args:
            scope_type: Type of scope being entered
        """
        self._scope_stack.append(scope_type)
        self._local_scopes.append({})
    
    def exit_scope(self):
        """Exit the current scope level."""
        if len(self._scope_stack) > 1:
            self._scope_stack.pop()
            self._local_scopes.pop()
    
    def current_scope(self) -> str:
        """Get the current scope type.
        
        Returns:
            Current scope type
        """
        return self._scope_stack[-1] if self._scope_stack else "global"
    
    def add_local_symbol(self, name: str, symbol_id: SymbolId):
        """Add a symbol to the current local scope.
        
        Args:
            name: Symbol name
            symbol_id: Symbol identifier
        """
        if self._local_scopes:
            self._local_scopes[-1][name] = symbol_id
    
    def get_available_symbols(self) -> Set[str]:
        """Get all symbols available in this context.
        
        Returns:
            Set of available symbol names
        """
        symbols = set()
        
        # Add local scope symbols
        for local_scope in self._local_scopes:
            symbols.update(local_scope.keys())
        
        # Add other scope symbols
        symbols.update(self._symbols.keys())
        
        return symbols
    
    def clear(self):
        """Clear all symbols and reset to initial state."""
        self._symbols.clear()
        self._scope_stack = ["global"]
        self._local_scopes = [{}]


class InheritanceResolver(ABC):
    """Abstract interface for handling inheritance relationships.
    
    Based on codanna's InheritanceResolver trait for tracking
    and resolving inheritance hierarchies.
    """
    
    @abstractmethod
    def add_inheritance(self, derived: str, base: str, file_id: FileId):
        """Add an inheritance relationship.
        
        Args:
            derived: Derived type name
            base: Base type name
            file_id: File where relationship is defined
        """
        pass
    
    @abstractmethod
    def get_base_types(self, type_name: str) -> List[str]:
        """Get all base types for a given type.
        
        Args:
            type_name: Type to get bases for
            
        Returns:
            List of base type names
        """
        pass
    
    @abstractmethod
    def get_derived_types(self, type_name: str) -> List[str]:
        """Get all types that derive from a given type.
        
        Args:
            type_name: Base type to get derived types for
            
        Returns:
            List of derived type names
        """
        pass
    
    @abstractmethod
    def is_subtype(self, derived: str, base: str) -> bool:
        """Check if one type is a subtype of another.
        
        Args:
            derived: Potentially derived type
            base: Potentially base type
            
        Returns:
            True if derived is a subtype of base
        """
        pass


@dataclass
class InheritanceRelation:
    """Represents an inheritance relationship."""
    derived: str
    base: str
    file_id: FileId


class GenericInheritanceResolver(InheritanceResolver):
    """Generic inheritance resolver for most languages.
    
    Based on codanna's GenericInheritanceResolver - provides
    standard inheritance tracking and resolution.
    """
    
    def __init__(self):
        """Initialize inheritance resolver."""
        self._inheritance_map: Dict[str, Set[str]] = {}  # derived -> {base1, base2, ...}
        self._reverse_map: Dict[str, Set[str]] = {}      # base -> {derived1, derived2, ...}
        self._all_relations: List[InheritanceRelation] = []
    
    def add_inheritance(self, derived: str, base: str, file_id: FileId):
        """Add an inheritance relationship.
        
        Args:
            derived: Derived type name
            base: Base type name
            file_id: File where relationship is defined
        """
        # Add to forward map
        if derived not in self._inheritance_map:
            self._inheritance_map[derived] = set()
        self._inheritance_map[derived].add(base)
        
        # Add to reverse map
        if base not in self._reverse_map:
            self._reverse_map[base] = set()
        self._reverse_map[base].add(derived)
        
        # Store the relation
        relation = InheritanceRelation(derived, base, file_id)
        self._all_relations.append(relation)
    
    def get_base_types(self, type_name: str) -> List[str]:
        """Get all base types for a given type.
        
        Args:
            type_name: Type to get bases for
            
        Returns:
            List of base type names
        """
        return list(self._inheritance_map.get(type_name, set()))
    
    def get_derived_types(self, type_name: str) -> List[str]:
        """Get all types that derive from a given type.
        
        Args:
            type_name: Base type to get derived types for
            
        Returns:
            List of derived type names
        """
        return list(self._reverse_map.get(type_name, set()))
    
    def is_subtype(self, derived: str, base: str) -> bool:
        """Check if one type is a subtype of another.
        
        Uses breadth-first search to handle multi-level inheritance.
        
        Args:
            derived: Potentially derived type
            base: Potentially base type
            
        Returns:
            True if derived is a subtype of base
        """
        if derived == base:
            return True
        
        visited = set()
        queue = [derived]
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            # Get direct base types
            bases = self._inheritance_map.get(current, set())
            
            if base in bases:
                return True
            
            # Add bases to queue for further exploration
            queue.extend(bases)
        
        return False
    
    def get_inheritance_chain(self, derived: str, base: str) -> Optional[List[str]]:
        """Get the inheritance chain from derived to base type.
        
        Args:
            derived: Starting type
            base: Target base type
            
        Returns:
            List representing the inheritance chain, or None if no path exists
        """
        if derived == base:
            return [derived]
        
        visited = set()
        queue = [(derived, [derived])]
        
        while queue:
            current, path = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            # Get direct base types
            bases = self._inheritance_map.get(current, set())
            
            for base_type in bases:
                new_path = path + [base_type]
                if base_type == base:
                    return new_path
                queue.append((base_type, new_path))
        
        return None
    
    def get_all_supertypes(self, type_name: str) -> Set[str]:
        """Get all supertypes (transitive closure of base types).
        
        Args:
            type_name: Type to get supertypes for
            
        Returns:
            Set of all supertype names
        """
        supertypes = set()
        visited = set()
        queue = [type_name]
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            # Get direct base types
            bases = self._inheritance_map.get(current, set())
            supertypes.update(bases)
            queue.extend(bases)
        
        return supertypes
    
    def get_all_subtypes(self, type_name: str) -> Set[str]:
        """Get all subtypes (transitive closure of derived types).
        
        Args:
            type_name: Type to get subtypes for
            
        Returns:
            Set of all subtype names
        """
        subtypes = set()
        visited = set()
        queue = [type_name]
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            # Get direct derived types
            derived = self._reverse_map.get(current, set())
            subtypes.update(derived)
            queue.extend(derived)
        
        return subtypes
    
    def clear(self):
        """Clear all inheritance relationships."""
        self._inheritance_map.clear()
        self._reverse_map.clear()
        self._all_relations.clear()
    
    def get_relation_count(self) -> int:
        """Get total number of inheritance relationships."""
        return len(self._all_relations)


class ScopeManager:
    """Manages nested scopes for symbol resolution.
    
    Provides utilities for tracking nested scopes during parsing
    and symbol resolution.
    """
    
    def __init__(self):
        """Initialize scope manager."""
        self._scope_stack: List[Dict[str, Any]] = []
        self._global_scope: Dict[str, Any] = {}
    
    def enter_scope(self, scope_data: Optional[Dict[str, Any]] = None):
        """Enter a new scope.
        
        Args:
            scope_data: Optional data for the new scope
        """
        if scope_data is None:
            scope_data = {}
        self._scope_stack.append(scope_data)
    
    def exit_scope(self) -> Optional[Dict[str, Any]]:
        """Exit the current scope.
        
        Returns:
            Data from the exited scope, or None if at global scope
        """
        if self._scope_stack:
            return self._scope_stack.pop()
        return None
    
    def current_scope(self) -> Dict[str, Any]:
        """Get the current scope data.
        
        Returns:
            Current scope data, or global scope if no active scopes
        """
        if self._scope_stack:
            return self._scope_stack[-1]
        return self._global_scope
    
    def scope_depth(self) -> int:
        """Get the current scope depth.
        
        Returns:
            Number of nested scopes (0 = global scope)
        """
        return len(self._scope_stack)
    
    def is_global_scope(self) -> bool:
        """Check if currently at global scope.
        
        Returns:
            True if at global scope
        """
        return len(self._scope_stack) == 0
    
    def set_scope_data(self, key: str, value: Any):
        """Set data in the current scope.
        
        Args:
            key: Data key
            value: Data value
        """
        scope = self.current_scope()
        scope[key] = value
    
    def get_scope_data(self, key: str, default: Any = None) -> Any:
        """Get data from the current scope.
        
        Args:
            key: Data key
            default: Default value if key not found
            
        Returns:
            Data value or default
        """
        scope = self.current_scope()
        return scope.get(key, default)
    
    def find_in_scopes(self, key: str) -> Any:
        """Find data by searching from current scope upward to global.
        
        Args:
            key: Data key to find
            
        Returns:
            First matching value found, or None
        """
        # Search from current scope upward
        for scope in reversed(self._scope_stack):
            if key in scope:
                return scope[key]
        
        # Check global scope
        return self._global_scope.get(key)
    
    def clear(self):
        """Clear all scopes and return to global scope."""
        self._scope_stack.clear()
        self._global_scope.clear()