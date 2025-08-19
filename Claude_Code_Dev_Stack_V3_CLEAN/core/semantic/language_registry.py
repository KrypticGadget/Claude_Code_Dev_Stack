"""
Language registry system for dynamic language discovery and management.

Extracted from codanna/src/parsing/registry.rs - provides Python implementation
of the language registry pattern for managing available and enabled languages.

Key Features:
- Auto-discovery of available language parsers
- Runtime enable/disable control via configuration
- Zero-cost lookups using static identifiers
- Extensible architecture for adding new languages
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Iterator, Tuple, Any
from enum import Enum
import threading


class LanguageId:
    """Type-safe language identifier using static strings for zero-cost comparisons."""
    
    def __init__(self, id_str: str):
        """Create a new LanguageId from a string identifier.
        
        Args:
            id_str: Static string identifier (e.g., 'rust', 'python')
        """
        self._id = id_str
    
    def as_str(self) -> str:
        """Get the string identifier."""
        return self._id
    
    def __str__(self) -> str:
        return self._id
    
    def __repr__(self) -> str:
        return f"LanguageId('{self._id}')"
    
    def __eq__(self, other) -> bool:
        if isinstance(other, LanguageId):
            return self._id == other._id
        return False
    
    def __hash__(self) -> int:
        return hash(self._id)


class RegistryError(Exception):
    """Registry errors with actionable suggestions."""
    pass


class LanguageNotFoundError(RegistryError):
    """Language not found in registry."""
    
    def __init__(self, language_id: LanguageId):
        super().__init__(
            f"Language '{language_id}' not found in registry\n"
            f"Suggestion: Check available languages or ensure the language module is imported"
        )


class LanguageDisabledError(RegistryError):
    """Language is available but disabled."""
    
    def __init__(self, language_id: LanguageId):
        super().__init__(
            f"Language '{language_id}' is available but disabled\n"
            f"Suggestion: Enable it in configuration by setting languages.{language_id}.enabled = true"
        )


class ExtensionNotMappedError(RegistryError):
    """No language found for file extension."""
    
    def __init__(self, extension: str):
        super().__init__(
            f"No language found for extension '.{extension}'\n"
            f"Suggestion: Check if the file type is supported or add a language mapping"
        )


class ParserCreationError(RegistryError):
    """Failed to create parser for language."""
    
    def __init__(self, language_id: LanguageId, reason: str):
        super().__init__(
            f"Failed to create parser for language '{language_id}': {reason}\n"
            f"Suggestion: Check the language configuration"
        )


class LanguageDefinition(ABC):
    """Trait for language modules to implement.
    
    Each language provides a static definition that the registry
    uses for discovery and instantiation.
    """
    
    @abstractmethod
    def id(self) -> LanguageId:
        """Unique identifier for this language (e.g., 'rust', 'python')."""
        pass
    
    @abstractmethod
    def name(self) -> str:
        """Human-readable name (e.g., 'Rust', 'Python')."""
        pass
    
    @abstractmethod
    def extensions(self) -> List[str]:
        """File extensions this language handles (without dot prefix)."""
        pass
    
    @abstractmethod
    def create_parser(self, settings: Dict[str, Any]):
        """Create a parser instance for this language."""
        pass
    
    @abstractmethod
    def create_behavior(self):
        """Create a behavior instance for this language."""
        pass
    
    def default_enabled(self) -> bool:
        """Default enabled state for configuration generation."""
        return False
    
    def is_enabled(self, settings: Dict[str, Any]) -> bool:
        """Check if this language is enabled in settings."""
        languages_config = settings.get('languages', {})
        language_config = languages_config.get(self.id().as_str(), {})
        return language_config.get('enabled', False)


@dataclass
class LanguageMetadata:
    """Language metadata from tree-sitter."""
    abi_version: int
    node_kind_count: int
    field_count: int
    
    @classmethod
    def from_language(cls, language) -> 'LanguageMetadata':
        """Create metadata from a tree-sitter Language."""
        # Placeholder implementation - would integrate with actual tree-sitter
        return cls(
            abi_version=getattr(language, 'abi_version', 14),
            node_kind_count=getattr(language, 'node_kind_count', 0),
            field_count=getattr(language, 'field_count', 0)
        )


class LanguageRegistry:
    """Language registry that manages available and enabled languages.
    
    The registry maintains two views:
    - All available languages (imported/registered)
    - Currently enabled languages (from configuration)
    
    This separation allows runtime control via configuration.
    """
    
    def __init__(self):
        self._definitions: Dict[LanguageId, LanguageDefinition] = {}
        self._extension_map: Dict[str, LanguageId] = {}
        self._lock = threading.RLock()
    
    def register(self, definition: LanguageDefinition) -> None:
        """Register a language definition.
        
        This is called during initialization to register all
        available languages. Whether they're enabled is determined
        by configuration at runtime.
        """
        with self._lock:
            language_id = definition.id()
            
            # Register the definition
            self._definitions[language_id] = definition
            
            # Update extension mappings
            for ext in definition.extensions():
                self._extension_map[ext] = language_id
    
    def get(self, language_id: LanguageId) -> Optional[LanguageDefinition]:
        """Get a language definition by ID.
        
        Returns None if the language is not available (not registered).
        Use is_enabled() to check if it's active in configuration.
        """
        with self._lock:
            return self._definitions.get(language_id)
    
    def get_by_extension(self, extension: str) -> Optional[LanguageDefinition]:
        """Get a language by file extension.
        
        Returns the language definition if a mapping exists.
        The language may still be disabled in configuration.
        """
        # Remove leading dot if present
        ext = extension.lstrip('.')
        
        with self._lock:
            language_id = self._extension_map.get(ext)
            if language_id:
                return self.get(language_id)
            return None
    
    def iter_all(self) -> Iterator[LanguageDefinition]:
        """Iterate over all available languages.
        
        This includes disabled languages. Filter by is_enabled()
        to get only active languages.
        """
        with self._lock:
            # Create a list to avoid holding the lock during iteration
            definitions = list(self._definitions.values())
        
        yield from definitions
    
    def iter_enabled(self, settings: Dict[str, Any]) -> Iterator[LanguageDefinition]:
        """Iterate over enabled languages only.
        
        Filters available languages by checking configuration.
        """
        for definition in self.iter_all():
            if definition.is_enabled(settings):
                yield definition
    
    def enabled_extensions(self, settings: Dict[str, Any]) -> Iterator[str]:
        """Get all supported extensions from enabled languages.
        
        Returns extensions only from languages enabled in configuration.
        """
        for definition in self.iter_enabled(settings):
            yield from definition.extensions()
    
    def is_available(self, language_id: LanguageId) -> bool:
        """Check if a language is available (registered)."""
        with self._lock:
            return language_id in self._definitions
    
    def is_enabled(self, language_id: LanguageId, settings: Dict[str, Any]) -> bool:
        """Check if a language is enabled in configuration.
        
        Returns False if language is not available or disabled.
        """
        definition = self.get(language_id)
        if definition is None:
            return False
        return definition.is_enabled(settings)
    
    def create_parser(self, language_id: LanguageId, settings: Dict[str, Any]):
        """Create a parser for a language.
        
        Checks both availability and configuration before creation.
        Returns appropriate error with suggestions.
        """
        definition = self.get(language_id)
        if definition is None:
            raise LanguageNotFoundError(language_id)
        
        if not definition.is_enabled(settings):
            raise LanguageDisabledError(language_id)
        
        try:
            return definition.create_parser(settings)
        except Exception as e:
            raise ParserCreationError(language_id, str(e))
    
    def create_parser_with_behavior(self, language_id: LanguageId, settings: Dict[str, Any]) -> Tuple[Any, Any]:
        """Create a parser and behavior pair.
        
        Convenience method for getting both parser and behavior.
        """
        definition = self.get(language_id)
        if definition is None:
            raise LanguageNotFoundError(language_id)
        
        if not definition.is_enabled(settings):
            raise LanguageDisabledError(language_id)
        
        try:
            parser = definition.create_parser(settings)
            behavior = definition.create_behavior()
            return parser, behavior
        except Exception as e:
            raise ParserCreationError(language_id, str(e))


# Global registry instance with lazy initialization
_global_registry: Optional[LanguageRegistry] = None
_registry_lock = threading.Lock()


def get_registry() -> LanguageRegistry:
    """Get the global registry instance.
    
    Provides access to the singleton registry instance with lazy initialization.
    """
    global _global_registry
    
    if _global_registry is None:
        with _registry_lock:
            if _global_registry is None:
                _global_registry = LanguageRegistry()
                _initialize_registry(_global_registry)
    
    return _global_registry


def _initialize_registry(registry: LanguageRegistry) -> None:
    """Initialize the registry with all available languages.
    
    This is called once during first registry access.
    Each language module should register itself here.
    """
    # Languages will register themselves here when their modules are imported
    # This happens during first access or explicit imports
    pass


# Convenience functions for common operations
def register_language(definition: LanguageDefinition) -> None:
    """Register a language definition with the global registry."""
    get_registry().register(definition)


def get_language_for_extension(extension: str) -> Optional[LanguageDefinition]:
    """Get a language definition for a file extension."""
    return get_registry().get_by_extension(extension)


def get_enabled_languages(settings: Dict[str, Any]) -> List[LanguageDefinition]:
    """Get all enabled language definitions."""
    return list(get_registry().iter_enabled(settings))