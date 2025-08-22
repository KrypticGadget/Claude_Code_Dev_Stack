# Semantic Analysis Patterns from Codanna

This module provides Python implementations of the tree-sitter semantic analysis patterns extracted from the Rust-based [codanna](https://github.com/bartolli/codanna) project (v0.5.1). 

## Overview

Codanna is a sophisticated code intelligence system that uses tree-sitter for parsing and provides language-agnostic semantic analysis. This module extracts the key architectural patterns and provides Python implementations that can be integrated into code intelligence systems without requiring Rust binaries.

## Key Patterns Extracted

### 1. Language Registry System

**Source**: `codanna/src/parsing/registry.rs`

- **Pattern**: Dynamic language discovery and management
- **Implementation**: `language_registry.py`
- **Key Features**:
  - Separation of "available" vs "enabled" languages
  - Runtime configuration control
  - Zero-cost lookups using static identifiers
  - Extensible architecture for new languages

```python
from core.semantic import LanguageRegistry, LanguageDefinition

# Register a language
registry = get_registry()
registry.register(PythonLanguageDefinition())

# Create parser for enabled language
parser = registry.create_parser(LanguageId("python"), settings)
```

### 2. Language-Agnostic Parser Interface

**Source**: `codanna/src/parsing/parser.rs`

- **Pattern**: Common interface for all language parsers
- **Implementation**: `parser_interface.py`
- **Key Features**:
  - Tree-sitter integration patterns
  - Symbol extraction interface
  - Relationship discovery (calls, implementations, uses)
  - Documentation extraction

```python
from core.semantic import LanguageParser, TreeSitterParser

class MyLanguageParser(TreeSitterParser):
    def parse(self, code: str, file_id: FileId, counter) -> List[Symbol]:
        # Implementation using tree-sitter patterns
        pass
```

### 3. Language Behavior System

**Source**: `codanna/src/parsing/language_behavior.rs`

- **Pattern**: Language-specific rules and conventions
- **Implementation**: `language_behavior.py`
- **Key Features**:
  - Module path formatting per language
  - Visibility parsing from signatures
  - Import resolution logic
  - Symbol resolution and scoping

```python
from core.semantic import LanguageBehavior

class PythonBehavior(LanguageBehavior):
    def module_separator(self) -> str:
        return "."
    
    def parse_visibility(self, signature: str) -> Visibility:
        # Python-specific visibility rules
        pass
```

### 4. Symbol Extraction and Analysis

**Source**: `codanna/src/parsing/*` and symbol handling

- **Pattern**: Comprehensive symbol representation
- **Implementation**: `symbol_extraction.py`
- **Key Features**:
  - Rich symbol metadata
  - Relationship tracking
  - Scope context management
  - Fast indexing and lookup

```python
from core.semantic import Symbol, SymbolKind, SymbolIndex

# Create and index symbols
symbol = Symbol.new(symbol_id, "function_name", SymbolKind.Function, file_id, range)
index = SymbolIndex()
index.add_symbol(symbol)

# Fast lookups
matches = index.find_symbols_by_name("function_name")
```

### 5. Resolution and Scoping

**Source**: `codanna/src/parsing/resolution.rs`

- **Pattern**: Language-aware symbol resolution
- **Implementation**: `resolution.py`
- **Key Features**:
  - Scope hierarchy management
  - Import resolution
  - Inheritance tracking
  - Context-aware symbol lookup

```python
from core.semantic import ResolutionScope, InheritanceResolver

# Create resolution context
context = behavior.build_resolution_context(file_id, document_index)
symbol_id = context.resolve("symbol_name")
```

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│                Semantic Analysis                │
├─────────────────────────────────────────────────┤
│  Language Registry │  Parser Interface         │
│  ├─ Language Defs  │  ├─ LanguageParser        │
│  ├─ Extensions     │  ├─ TreeSitterParser      │
│  └─ Factories      │  └─ Method/Call Finding   │
├─────────────────────────────────────────────────┤
│  Language Behavior │  Symbol Extraction        │
│  ├─ Module Paths   │  ├─ Symbol Representation │
│  ├─ Visibility     │  ├─ Relationship Tracking │
│  ├─ Import Rules   │  └─ Fast Indexing         │
│  └─ Resolution     │                           │
├─────────────────────────────────────────────────┤
│  Resolution & Scoping │  Context Management    │
│  ├─ Scope Hierarchy  │  ├─ Parser Context     │
│  ├─ Symbol Lookup    │  ├─ Scope Tracking     │
│  └─ Inheritance      │  └─ Metadata           │
└─────────────────────────────────────────────────┘
```

## Integration Approach

### 1. Without Tree-Sitter (Regex Fallback)

For environments where tree-sitter is not available, the patterns include regex-based fallback implementations:

```python
# Automatic fallback in parser implementations
def parse(self, code: str, file_id: FileId, counter) -> List[Symbol]:
    if self._parser is None:
        return self._fallback_parse(code, file_id, counter)  # Regex-based
    
    try:
        return self._tree_sitter_parse(code, file_id, counter)
    except Exception:
        return self._fallback_parse(code, file_id, counter)
```

### 2. With Tree-Sitter Integration

Full tree-sitter integration provides accurate AST-based analysis:

```python
# Tree-sitter based implementation
class PythonParser(TreeSitterParser):
    def __init__(self):
        import tree_sitter_python
        super().__init__(LanguageId("python"), tree_sitter_python.language())
```

### 3. Hybrid Approach

Combine tree-sitter accuracy with regex fallback for reliability:

```python
# Best of both worlds
analyzer = SemanticAnalyzer()
analyzer.add_file(file_path, content)  # Automatically chooses best method
```

## Usage Examples

### Basic File Analysis

```python
from core.semantic.examples import analyze_python_file

file_path = Path("example.py")
symbols, metadata = analyze_python_file(file_path)

for symbol in symbols:
    print(f"{symbol.kind.name}: {symbol.name} at line {symbol.range.start_line}")
```

### Codebase Analysis

```python
from core.semantic.examples import analyze_codebase

results = analyze_codebase(Path("."), ["*.py"])
print(f"Analyzed {results['files_analyzed']} files")
print(f"Found {results['symbols_found']} symbols")
```

### Custom Language Implementation

```python
from core.semantic import LanguageDefinition, LanguageBehavior, TreeSitterParser

class MyLanguageDefinition(LanguageDefinition):
    def id(self) -> LanguageId:
        return LanguageId("mylang")
    
    def extensions(self) -> List[str]:
        return ["ml", "mylang"]
    
    def create_parser(self, settings):
        return MyLanguageParser()
    
    def create_behavior(self):
        return MyLanguageBehavior()

# Register and use
register_language(MyLanguageDefinition())
```

## Configuration

Languages can be enabled/disabled via configuration:

```python
settings = {
    "languages": {
        "python": {"enabled": True},
        "javascript": {"enabled": False},
        "rust": {"enabled": True}
    }
}

analyzer = SemanticAnalyzer(settings)
```

## Benefits of This Approach

1. **Language Agnostic**: Core indexing logic is completely language-independent
2. **Extensible**: New languages can be added without modifying existing code
3. **Configurable**: Runtime enable/disable of languages via configuration
4. **Fallback Support**: Works even without tree-sitter dependencies
5. **Zero-Cost Abstractions**: Efficient lookups and minimal overhead
6. **Rich Metadata**: Comprehensive symbol information and relationships

## Codanna Source Attribution

This implementation is based on the architectural patterns from codanna v0.5.1:

- **Repository**: https://github.com/bartolli/codanna
- **License**: Apache-2.0
- **Key Patterns Extracted**:
  - Language registry system (`src/parsing/registry.rs`)
  - Parser interface design (`src/parsing/parser.rs`)
  - Language behavior traits (`src/parsing/language_behavior.rs`)
  - Symbol extraction patterns (`src/parsing/`)
  - Resolution mechanisms (`src/parsing/resolution.rs`)

The Python implementations maintain the same architectural principles while providing language-appropriate interfaces and fallback mechanisms for broader compatibility.

## Dependencies

### Required
- Python 3.8+
- dataclasses (built-in for Python 3.7+)
- typing (built-in)
- pathlib (built-in)

### Optional (for full tree-sitter support)
- tree-sitter-python
- tree-sitter-javascript
- tree-sitter-rust
- Other tree-sitter language bindings

### Installation

```bash
# For basic functionality (regex fallback)
pip install # no additional dependencies needed

# For full tree-sitter support
pip install tree-sitter tree-sitter-python tree-sitter-javascript
```

## Development

To extend with new languages:

1. Implement `LanguageDefinition`
2. Implement `LanguageBehavior` 
3. Implement `LanguageParser` (inherit from `TreeSitterParser`)
4. Register with the global registry
5. Add configuration support

See `examples/python_language.py` for a complete reference implementation.