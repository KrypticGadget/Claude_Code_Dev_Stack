"""
Usage patterns and integration examples for the semantic analysis system.

Demonstrates practical usage of the semantic analysis patterns extracted
from codanna, showing how to integrate them into code intelligence systems.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from ..language_registry import get_registry, LanguageId
from ..symbol_extraction import SymbolIndex, SymbolCounter, Symbol, FileId
from ..parser_interface import LanguageParser
from ..language_behavior import LanguageBehavior


class SemanticAnalyzer:
    """Main semantic analyzer using the extracted patterns.
    
    Provides a high-level interface for code analysis using the
    language-agnostic patterns from codanna.
    """
    
    def __init__(self, settings: Optional[Dict[str, Any]] = None):
        """Initialize the semantic analyzer.
        
        Args:
            settings: Configuration settings for languages
        """
        self.settings = settings or {"languages": {"python": {"enabled": True}}}
        self.registry = get_registry()
        self.symbol_index = SymbolIndex()
        self.symbol_counter = SymbolCounter()
        self._parsers: Dict[LanguageId, LanguageParser] = {}
        self._behaviors: Dict[LanguageId, LanguageBehavior] = {}
    
    def add_file(self, file_path: Path, content: str, project_root: Optional[Path] = None) -> Optional[FileId]:
        """Add a file to the analysis.
        
        Args:
            file_path: Path to the source file
            content: File content
            project_root: Optional project root for module path calculation
            
        Returns:
            File ID if successfully analyzed, None otherwise
        """
        # Detect language from file extension
        extension = file_path.suffix.lstrip('.')
        language_def = self.registry.get_by_extension(extension)
        
        if not language_def or not language_def.is_enabled(self.settings):
            return None
        
        language_id = language_def.id()
        
        # Get or create parser and behavior
        parser = self._get_parser(language_id)
        behavior = self._get_behavior(language_id)
        
        if not parser or not behavior:
            return None
        
        # Create file ID
        file_id = FileId.generate()
        
        # Calculate module path if project root provided
        if project_root:
            module_path = behavior.module_path_from_file(file_path, project_root)
            if module_path:
                behavior.register_file(file_path, file_id, module_path)
        
        # Parse symbols
        symbols = parser.parse(content, file_id, self.symbol_counter)
        
        # Configure symbols with language-specific behavior
        for symbol in symbols:
            module_path = behavior.get_module_path_for_file(file_id)
            behavior.configure_symbol(symbol, module_path)
        
        # Add symbols to index
        for symbol in symbols:
            self.symbol_index.add_symbol(symbol)
        
        # Find and process imports
        imports = parser.find_imports(content, file_id)
        for import_stmt in imports:
            behavior.add_import(import_stmt)
        
        # Find and process relationships
        calls = parser.find_calls(content)
        implementations = parser.find_implementations(content)
        uses = parser.find_uses(content)
        defines = parser.find_defines(content)
        
        # Add relationships to index (simplified)
        for caller, callee, range_obj in calls:
            # Could create SymbolRelationship objects here
            pass
        
        return file_id
    
    def _get_parser(self, language_id: LanguageId) -> Optional[LanguageParser]:
        """Get or create parser for language."""
        if language_id not in self._parsers:
            try:
                parser = self.registry.create_parser(language_id, self.settings)
                self._parsers[language_id] = parser
            except Exception:
                return None
        
        return self._parsers.get(language_id)
    
    def _get_behavior(self, language_id: LanguageId) -> Optional[LanguageBehavior]:
        """Get or create behavior for language."""
        if language_id not in self._behaviors:
            try:
                _, behavior = self.registry.create_parser_with_behavior(language_id, self.settings)
                self._behaviors[language_id] = behavior
            except Exception:
                return None
        
        return self._behaviors.get(language_id)
    
    def find_symbols(self, name: str) -> List[Symbol]:
        """Find symbols by name.
        
        Args:
            name: Symbol name to search for
            
        Returns:
            List of matching symbols
        """
        return self.symbol_index.find_symbols_by_name(name)
    
    def find_symbols_in_file(self, file_id: FileId) -> List[Symbol]:
        """Find all symbols in a file.
        
        Args:
            file_id: File identifier
            
        Returns:
            List of symbols in the file
        """
        return self.symbol_index.find_symbols_by_file(file_id)
    
    def get_symbol_count(self) -> int:
        """Get total number of indexed symbols."""
        return self.symbol_index.symbol_count()
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        return list(self.registry.enabled_extensions(self.settings))
    
    def clear(self):
        """Clear all analysis data."""
        self.symbol_index.clear()
        self.symbol_counter = SymbolCounter()
        self._parsers.clear()
        self._behaviors.clear()


def create_semantic_analyzer(settings: Optional[Dict[str, Any]] = None) -> SemanticAnalyzer:
    """Create a semantic analyzer with default configuration.
    
    Args:
        settings: Optional language settings
        
    Returns:
        Configured semantic analyzer
    """
    if settings is None:
        settings = {
            "languages": {
                "python": {"enabled": True}
            }
        }
    
    return SemanticAnalyzer(settings)


def analyze_python_file(file_path: Path, project_root: Optional[Path] = None) -> Tuple[List[Symbol], Dict[str, Any]]:
    """Analyze a Python file and return symbols and metadata.
    
    Args:
        file_path: Path to Python file
        project_root: Optional project root
        
    Returns:
        Tuple of (symbols, metadata)
    """
    analyzer = create_semantic_analyzer()
    
    # Read file content
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return [], {"error": str(e)}
    
    # Analyze file
    file_id = analyzer.add_file(file_path, content, project_root)
    
    if file_id is None:
        return [], {"error": "Failed to analyze file"}
    
    # Get symbols
    symbols = analyzer.find_symbols_in_file(file_id)
    
    # Get metadata
    metadata = {
        "file_id": str(file_id),
        "symbol_count": len(symbols),
        "supported_extensions": analyzer.get_supported_extensions(),
        "total_symbols": analyzer.get_symbol_count()
    }
    
    return symbols, metadata


def setup_language_registry(enable_languages: Optional[List[str]] = None) -> Dict[str, Any]:
    """Setup language registry with specified languages.
    
    Args:
        enable_languages: List of language IDs to enable
        
    Returns:
        Configuration dictionary
    """
    if enable_languages is None:
        enable_languages = ["python"]
    
    settings = {"languages": {}}
    
    # Get registry and configure languages
    registry = get_registry()
    
    for lang_def in registry.iter_all():
        lang_id = lang_def.id().as_str()
        enabled = lang_id in enable_languages
        
        settings["languages"][lang_id] = {
            "enabled": enabled,
            "name": lang_def.name(),
            "extensions": lang_def.extensions()
        }
    
    return settings


def analyze_codebase(root_path: Path, include_patterns: Optional[List[str]] = None) -> Dict[str, Any]:
    """Analyze an entire codebase.
    
    Args:
        root_path: Root directory of the codebase
        include_patterns: Optional file patterns to include
        
    Returns:
        Analysis results dictionary
    """
    if include_patterns is None:
        include_patterns = ["*.py"]
    
    analyzer = create_semantic_analyzer()
    supported_extensions = set(analyzer.get_supported_extensions())
    
    results = {
        "files_analyzed": 0,
        "symbols_found": 0,
        "files_by_type": {},
        "symbol_types": {},
        "errors": []
    }
    
    # Find all matching files
    files_to_analyze = []
    for pattern in include_patterns:
        files_to_analyze.extend(root_path.glob(f"**/{pattern}"))
    
    # Analyze each file
    for file_path in files_to_analyze:
        extension = file_path.suffix.lstrip('.')
        if extension not in supported_extensions:
            continue
        
        try:
            content = file_path.read_text(encoding='utf-8')
            file_id = analyzer.add_file(file_path, content, root_path)
            
            if file_id:
                results["files_analyzed"] += 1
                
                # Track file types
                if extension not in results["files_by_type"]:
                    results["files_by_type"][extension] = 0
                results["files_by_type"][extension] += 1
                
                # Get symbols for this file
                symbols = analyzer.find_symbols_in_file(file_id)
                
                # Track symbol types
                for symbol in symbols:
                    symbol_type = symbol.kind.name
                    if symbol_type not in results["symbol_types"]:
                        results["symbol_types"][symbol_type] = 0
                    results["symbol_types"][symbol_type] += 1
            
        except Exception as e:
            results["errors"].append({
                "file": str(file_path),
                "error": str(e)
            })
    
    results["symbols_found"] = analyzer.get_symbol_count()
    
    return results


def export_symbols_to_json(analyzer: SemanticAnalyzer) -> Dict[str, Any]:
    """Export symbol index to JSON-serializable format.
    
    Args:
        analyzer: Semantic analyzer with indexed symbols
        
    Returns:
        JSON-serializable dictionary of symbols
    """
    symbols_data = []
    
    for symbol in analyzer.symbol_index.get_all_symbols():
        symbol_data = {
            "id": str(symbol.id),
            "name": symbol.name,
            "kind": symbol.kind.name,
            "file_id": str(symbol.file_id),
            "range": {
                "start_line": symbol.range.start_line,
                "start_col": symbol.range.start_col,
                "end_line": symbol.range.end_line,
                "end_col": symbol.range.end_col
            },
            "signature": symbol.signature,
            "doc_comment": symbol.doc_comment,
            "module_path": symbol.module_path,
            "visibility": symbol.visibility.name if symbol.visibility else None,
            "scope_context": symbol.scope_context.name if symbol.scope_context else None
        }
        symbols_data.append(symbol_data)
    
    return {
        "symbols": symbols_data,
        "total_count": len(symbols_data),
        "export_timestamp": "2024-01-01T00:00:00Z"  # Would use actual timestamp
    }


# Example usage patterns
def example_usage():
    """Example usage of the semantic analysis system."""
    
    # 1. Basic file analysis
    file_path = Path("example.py")
    if file_path.exists():
        symbols, metadata = analyze_python_file(file_path)
        print(f"Found {len(symbols)} symbols in {file_path}")
    
    # 2. Codebase analysis
    project_root = Path(".")
    results = analyze_codebase(project_root, ["*.py"])
    print(f"Analyzed {results['files_analyzed']} files")
    print(f"Found {results['symbols_found']} total symbols")
    
    # 3. Custom analyzer with multiple languages
    settings = setup_language_registry(["python"])
    analyzer = create_semantic_analyzer(settings)
    
    # Add files to analyzer
    for py_file in project_root.glob("**/*.py"):
        if py_file.exists():
            content = py_file.read_text(encoding='utf-8')
            file_id = analyzer.add_file(py_file, content, project_root)
            if file_id:
                print(f"Analyzed {py_file}")
    
    # Search for symbols
    main_functions = analyzer.find_symbols("main")
    print(f"Found {len(main_functions)} 'main' symbols")
    
    # Export results
    export_data = export_symbols_to_json(analyzer)
    print(f"Export contains {export_data['total_count']} symbols")


if __name__ == "__main__":
    example_usage()