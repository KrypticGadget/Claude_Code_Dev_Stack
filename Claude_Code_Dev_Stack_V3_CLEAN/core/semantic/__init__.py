"""
Core semantic analysis patterns extracted from codanna tree-sitter implementation.

This module provides Python implementations of the semantic analysis patterns
used in the Rust-based codanna project, enabling tree-sitter based code
intelligence without requiring Rust binaries.

Key Components:
- Language detection and registry patterns
- Tree-sitter parser abstractions  
- Symbol extraction and relationship analysis
- Import resolution and module path handling
- Language-specific behavior patterns

Based on codanna v0.5.1 semantic analysis architecture.
"""

from .language_registry import LanguageRegistry, LanguageDefinition, LanguageId
from .parser_interface import LanguageParser, ParserFactory
from .language_behavior import LanguageBehavior, LanguageMetadata
from .symbol_extraction import Symbol, SymbolKind, SymbolExtractor
from .resolution import ResolutionScope, InheritanceResolver
from .context import ParserContext, ScopeType

__all__ = [
    'LanguageRegistry',
    'LanguageDefinition', 
    'LanguageId',
    'LanguageParser',
    'ParserFactory',
    'LanguageBehavior',
    'LanguageMetadata',
    'Symbol',
    'SymbolKind',
    'SymbolExtractor',
    'ResolutionScope',
    'InheritanceResolver',
    'ParserContext',
    'ScopeType'
]

__version__ = "0.1.0"
__codanna_version__ = "0.5.1"