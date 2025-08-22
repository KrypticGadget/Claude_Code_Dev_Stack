"""
Parser context and scope tracking patterns from codanna.

Extracted from codanna's context management system - provides Python
implementation of parsing context, scope tracking, and symbol context
management during code analysis.

Based on codanna/src/parsing/context.rs patterns.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Stack
from enum import Enum, auto

from .symbol_extraction import ScopeContext


class ScopeType(Enum):
    """Types of scopes during parsing.
    
    Based on codanna's scope type system for tracking
    different kinds of code scopes during parsing.
    """
    Global = auto()
    Module = auto()
    Function = auto()
    Method = auto()
    Class = auto()
    Interface = auto()
    Trait = auto()
    Enum = auto()
    Struct = auto()
    Namespace = auto()
    Block = auto()
    Loop = auto()
    Conditional = auto()
    TryCatch = auto()
    Lambda = auto()
    
    @classmethod
    def function(cls) -> 'ScopeType':
        """Create function scope type."""
        return cls.Function
    
    @classmethod
    def method(cls) -> 'ScopeType':
        """Create method scope type."""
        return cls.Method
    
    @classmethod
    def class_scope(cls) -> 'ScopeType':
        """Create class scope type."""
        return cls.Class


@dataclass
class ScopeInfo:
    """Information about a scope level.
    
    Tracks metadata about a specific scope during parsing.
    """
    scope_type: ScopeType
    name: Optional[str] = None
    start_line: Optional[int] = None
    start_col: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_function_like(self) -> bool:
        """Check if this scope represents a function-like construct."""
        return self.scope_type in (ScopeType.Function, ScopeType.Method, ScopeType.Lambda)
    
    def is_type_like(self) -> bool:
        """Check if this scope represents a type definition."""
        return self.scope_type in (ScopeType.Class, ScopeType.Interface, ScopeType.Trait, ScopeType.Enum, ScopeType.Struct)
    
    def is_container(self) -> bool:
        """Check if this scope can contain other symbols."""
        return self.scope_type in (
            ScopeType.Module, ScopeType.Class, ScopeType.Interface, 
            ScopeType.Trait, ScopeType.Namespace, ScopeType.Enum
        )


class ParserContext:
    """Parser context for tracking scope and symbol information during parsing.
    
    Based on codanna's ParserContext - manages scope stack, parent tracking,
    and context information during AST traversal and symbol extraction.
    """
    
    def __init__(self):
        """Initialize parser context."""
        self._scope_stack: List[ScopeInfo] = []
        self._current_function: Optional[str] = None
        self._current_class: Optional[str] = None
        self._current_module: Optional[str] = None
        self._symbol_stack: List[str] = []  # Track symbol hierarchy
        self._metadata: Dict[str, Any] = {}
        
        # Start with global scope
        self.enter_scope(ScopeType.Global)
    
    def enter_scope(self, scope_type: ScopeType, name: Optional[str] = None, 
                   start_line: Optional[int] = None, start_col: Optional[int] = None,
                   metadata: Optional[Dict[str, Any]] = None):
        """Enter a new scope.
        
        Args:
            scope_type: Type of scope being entered
            name: Optional name of the scope (function name, class name, etc.)
            start_line: Starting line number
            start_col: Starting column number
            metadata: Optional scope metadata
        """
        scope_info = ScopeInfo(
            scope_type=scope_type,
            name=name,
            start_line=start_line,
            start_col=start_col,
            metadata=metadata or {}
        )
        self._scope_stack.append(scope_info)
        
        # Track in symbol stack if named
        if name:
            self._symbol_stack.append(name)
    
    def exit_scope(self) -> Optional[ScopeInfo]:
        """Exit the current scope.
        
        Returns:
            Information about the exited scope, or None if at global scope
        """
        if len(self._scope_stack) > 1:  # Keep global scope
            scope_info = self._scope_stack.pop()
            
            # Remove from symbol stack if it was named
            if scope_info.name and self._symbol_stack and self._symbol_stack[-1] == scope_info.name:
                self._symbol_stack.pop()
            
            return scope_info
        return None
    
    def current_scope(self) -> ScopeInfo:
        """Get current scope information.
        
        Returns:
            Current scope info (global scope if stack is empty)
        """
        return self._scope_stack[-1] if self._scope_stack else ScopeInfo(ScopeType.Global)
    
    def current_scope_type(self) -> ScopeType:
        """Get current scope type.
        
        Returns:
            Current scope type
        """
        return self.current_scope().scope_type
    
    def scope_depth(self) -> int:
        """Get current scope depth.
        
        Returns:
            Number of nested scopes (1 = global scope only)
        """
        return len(self._scope_stack)
    
    def is_global_scope(self) -> bool:
        """Check if currently at global scope.
        
        Returns:
            True if at global scope
        """
        return len(self._scope_stack) == 1 and self._scope_stack[0].scope_type == ScopeType.Global
    
    def is_module_level(self) -> bool:
        """Check if currently at module level.
        
        Returns:
            True if at module level (global or module scope)
        """
        current = self.current_scope_type()
        return current in (ScopeType.Global, ScopeType.Module)
    
    def is_in_function(self) -> bool:
        """Check if currently inside a function.
        
        Returns:
            True if inside any function-like scope
        """
        for scope in self._scope_stack:
            if scope.is_function_like():
                return True
        return False
    
    def is_in_class(self) -> bool:
        """Check if currently inside a class.
        
        Returns:
            True if inside any type-like scope
        """
        for scope in self._scope_stack:
            if scope.is_type_like():
                return True
        return False
    
    def get_containing_function(self) -> Optional[str]:
        """Get the name of the containing function.
        
        Returns:
            Name of nearest enclosing function, or None
        """
        for scope in reversed(self._scope_stack):
            if scope.is_function_like() and scope.name:
                return scope.name
        return None
    
    def get_containing_class(self) -> Optional[str]:
        """Get the name of the containing class.
        
        Returns:
            Name of nearest enclosing class, or None
        """
        for scope in reversed(self._scope_stack):
            if scope.is_type_like() and scope.name:
                return scope.name
        return None
    
    def get_scope_path(self) -> List[str]:
        """Get the full scope path as a list of names.
        
        Returns:
            List of scope names from global to current
        """
        path = []
        for scope in self._scope_stack:
            if scope.name:
                path.append(scope.name)
        return path
    
    def get_qualified_name(self, separator: str = "::") -> str:
        """Get the fully qualified name using the scope path.
        
        Args:
            separator: Separator to use between scope levels
            
        Returns:
            Qualified name string
        """
        path = self.get_scope_path()
        return separator.join(path) if path else ""
    
    # Parent tracking methods
    
    def current_function(self) -> Optional[str]:
        """Get current function name.
        
        Returns:
            Current function name or None
        """
        return self._current_function
    
    def current_class(self) -> Optional[str]:
        """Get current class name.
        
        Returns:
            Current class name or None
        """
        return self._current_class
    
    def current_module(self) -> Optional[str]:
        """Get current module name.
        
        Returns:
            Current module name or None
        """
        return self._current_module
    
    def set_current_function(self, name: Optional[str]):
        """Set current function name.
        
        Args:
            name: Function name or None to clear
        """
        self._current_function = name
    
    def set_current_class(self, name: Optional[str]):
        """Set current class name.
        
        Args:
            name: Class name or None to clear
        """
        self._current_class = name
    
    def set_current_module(self, name: Optional[str]):
        """Set current module name.
        
        Args:
            name: Module name or None to clear
        """
        self._current_module = name
    
    def current_scope_context(self) -> ScopeContext:
        """Get the current scope context for symbols.
        
        Returns:
            ScopeContext enum value based on current scope
        """
        current = self.current_scope_type()
        
        if current == ScopeType.Global:
            return ScopeContext.Global
        elif current == ScopeType.Module:
            return ScopeContext.Module
        elif current in (ScopeType.Class, ScopeType.Interface, ScopeType.Trait):
            return ScopeContext.ClassMember
        elif current in (ScopeType.Function, ScopeType.Method, ScopeType.Lambda):
            return ScopeContext.Local
        else:
            return ScopeContext.Module  # Default fallback
    
    # Metadata management
    
    def set_metadata(self, key: str, value: Any):
        """Set context metadata.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self._metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get context metadata.
        
        Args:
            key: Metadata key
            default: Default value if key not found
            
        Returns:
            Metadata value or default
        """
        return self._metadata.get(key, default)
    
    def set_scope_metadata(self, key: str, value: Any):
        """Set metadata for the current scope.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        if self._scope_stack:
            self._scope_stack[-1].metadata[key] = value
    
    def get_scope_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata from the current scope.
        
        Args:
            key: Metadata key
            default: Default value if key not found
            
        Returns:
            Metadata value or default
        """
        if self._scope_stack:
            return self._scope_stack[-1].metadata.get(key, default)
        return default
    
    def find_scope_metadata(self, key: str, default: Any = None) -> Any:
        """Find metadata by searching up the scope stack.
        
        Args:
            key: Metadata key
            default: Default value if key not found
            
        Returns:
            First matching metadata value or default
        """
        for scope in reversed(self._scope_stack):
            if key in scope.metadata:
                return scope.metadata[key]
        return default
    
    # Utility methods
    
    def reset(self):
        """Reset context to initial state."""
        self._scope_stack.clear()
        self._current_function = None
        self._current_class = None
        self._current_module = None
        self._symbol_stack.clear()
        self._metadata.clear()
        
        # Start with global scope
        self.enter_scope(ScopeType.Global)
    
    def clone(self) -> 'ParserContext':
        """Create a copy of this context.
        
        Returns:
            New ParserContext with copied state
        """
        new_context = ParserContext()
        new_context._scope_stack = [
            ScopeInfo(
                scope_type=scope.scope_type,
                name=scope.name,
                start_line=scope.start_line,
                start_col=scope.start_col,
                metadata=scope.metadata.copy()
            )
            for scope in self._scope_stack
        ]
        new_context._current_function = self._current_function
        new_context._current_class = self._current_class
        new_context._current_module = self._current_module
        new_context._symbol_stack = self._symbol_stack.copy()
        new_context._metadata = self._metadata.copy()
        
        return new_context
    
    def __repr__(self) -> str:
        """String representation of the context."""
        scope_names = [scope.name or f"({scope.scope_type.name})" for scope in self._scope_stack]
        return f"ParserContext(scopes={' -> '.join(scope_names)})"


class ContextManager:
    """Manages multiple parser contexts for different files or parsing sessions.
    
    Provides utilities for managing contexts across multiple parsing operations.
    """
    
    def __init__(self):
        """Initialize context manager."""
        self._contexts: Dict[str, ParserContext] = {}
        self._current_context_id: Optional[str] = None
    
    def create_context(self, context_id: str) -> ParserContext:
        """Create a new parser context.
        
        Args:
            context_id: Unique identifier for the context
            
        Returns:
            New parser context
        """
        context = ParserContext()
        self._contexts[context_id] = context
        return context
    
    def get_context(self, context_id: str) -> Optional[ParserContext]:
        """Get an existing context.
        
        Args:
            context_id: Context identifier
            
        Returns:
            Parser context or None if not found
        """
        return self._contexts.get(context_id)
    
    def set_current_context(self, context_id: str):
        """Set the current active context.
        
        Args:
            context_id: Context identifier
        """
        if context_id in self._contexts:
            self._current_context_id = context_id
    
    def current_context(self) -> Optional[ParserContext]:
        """Get the current active context.
        
        Returns:
            Current parser context or None
        """
        if self._current_context_id:
            return self._contexts.get(self._current_context_id)
        return None
    
    def remove_context(self, context_id: str):
        """Remove a context.
        
        Args:
            context_id: Context identifier to remove
        """
        if context_id in self._contexts:
            del self._contexts[context_id]
            
        if self._current_context_id == context_id:
            self._current_context_id = None
    
    def clear_all(self):
        """Clear all contexts."""
        self._contexts.clear()
        self._current_context_id = None
    
    def list_contexts(self) -> List[str]:
        """Get list of all context IDs.
        
        Returns:
            List of context identifiers
        """
        return list(self._contexts.keys())