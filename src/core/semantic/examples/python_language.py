"""
Example Python language implementation using the semantic analysis patterns.

Demonstrates how to implement a language definition and behavior using
the extracted patterns from codanna for Python language support.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
import re

from ..language_registry import LanguageDefinition, LanguageId, register_language
from ..language_behavior import LanguageBehavior, LanguageMetadata
from ..parser_interface import LanguageParser, TreeSitterParser, Import, MethodCall
from ..symbol_extraction import Symbol, SymbolKind, FileId, Range, SymbolCounter, Visibility
from ..resolution import ResolutionScope, InheritanceResolver, GenericResolutionContext, GenericInheritanceResolver
from ..context import ParserContext, ScopeType


class PythonLanguageDefinition(LanguageDefinition):
    """Python language definition for the registry system."""
    
    def id(self) -> LanguageId:
        """Unique identifier for Python language."""
        return LanguageId("python")
    
    def name(self) -> str:
        """Human-readable name."""
        return "Python"
    
    def extensions(self) -> List[str]:
        """File extensions for Python files."""
        return ["py", "pyi", "pyx"]
    
    def create_parser(self, settings: Dict[str, Any]):
        """Create a Python parser instance."""
        return PythonParser()
    
    def create_behavior(self):
        """Create a Python behavior instance."""
        return PythonBehavior()
    
    def default_enabled(self) -> bool:
        """Python is commonly used, so enable by default."""
        return True


class PythonBehavior(LanguageBehavior):
    """Python-specific language behavior implementation."""
    
    def __init__(self):
        """Initialize Python behavior."""
        self._imports: Dict[FileId, List[Import]] = {}
        self._file_modules: Dict[FileId, str] = {}
    
    def format_module_path(self, base_path: str, symbol_name: str) -> str:
        """Format module path using Python dot notation.
        
        Python typically uses file paths as module paths, not including the symbol name.
        """
        return base_path
    
    def parse_visibility(self, signature: str) -> Visibility:
        """Parse visibility from Python signature using naming conventions."""
        # Check for special/dunder methods first
        dunder_methods = ["__init__", "__str__", "__repr__", "__eq__", "__hash__", "__call__"]
        if any(method in signature for method in dunder_methods):
            return Visibility.Public
        
        # Double underscore (not dunder) = private (name mangling)
        if "def __" in signature or "class __" in signature:
            return Visibility.Private
        
        # Single underscore = module-level/protected
        if "def _" in signature or "class _" in signature:
            return Visibility.Module
        
        # Everything else is public in Python
        return Visibility.Public
    
    def module_separator(self) -> str:
        """Python uses dot notation for modules."""
        return "."
    
    def supports_traits(self) -> bool:
        """Python doesn't have traits, it has inheritance and mixins."""
        return False
    
    def supports_inherent_methods(self) -> bool:
        """Python methods are always on classes, not separate."""
        return False
    
    def get_language(self) -> Any:
        """Get tree-sitter language object."""
        try:
            import tree_sitter_python
            return tree_sitter_python.language()
        except ImportError:
            # Return mock object if tree-sitter-python not available
            class MockLanguage:
                def abi_version(self): return 14
                def node_kind_count(self): return 100
                def field_count(self): return 50
                def id_for_node_kind(self, kind, named): return 1 if kind else 0
            return MockLanguage()
    
    def module_path_from_file(self, file_path: Path, project_root: Path) -> Optional[str]:
        """Calculate Python module path from file path."""
        try:
            # Get relative path from project root
            relative_path = file_path.relative_to(project_root)
        except ValueError:
            return None
        
        # Convert path to string
        path_str = str(relative_path)
        
        # Remove common Python source directories if present
        for prefix in ["src/", "lib/", "app/"]:
            if path_str.startswith(prefix):
                path_str = path_str[len(prefix):]
                break
        
        # Remove the .py extension
        for suffix in [".py", ".pyx", ".pyi"]:
            if path_str.endswith(suffix):
                path_str = path_str[:-len(suffix)]
                break
        
        # Handle __init__.py - it represents the package itself
        if path_str.endswith("/__init__"):
            path_str = path_str[:-len("/__init__")]
        
        # Convert path separators to Python module separators
        module_path = path_str.replace("/", ".").replace("\\", ".")
        
        # Handle special cases
        if not module_path or module_path == "__init__":
            return None
        elif module_path in ("__main__", "main"):
            return "__main__"
        else:
            return module_path
    
    def register_file(self, path: Path, file_id: FileId, module_path: str):
        """Register a file with its module path."""
        self._file_modules[file_id] = module_path
    
    def add_import(self, import_stmt: Import):
        """Add an import to tracking."""
        if import_stmt.file_id not in self._imports:
            self._imports[import_stmt.file_id] = []
        self._imports[import_stmt.file_id].append(import_stmt)
    
    def get_imports_for_file(self, file_id: FileId) -> List[Import]:
        """Get imports for a file."""
        return self._imports.get(file_id, [])
    
    def get_module_path_for_file(self, file_id: FileId) -> Optional[str]:
        """Get module path for a file."""
        return self._file_modules.get(file_id)
    
    def import_matches_symbol(self, import_path: str, symbol_module_path: str, 
                            importing_module: Optional[str]) -> bool:
        """Check if import path matches symbol's module path."""
        # Exact match first (performance)
        if import_path == symbol_module_path:
            return True
        
        # Handle Python-specific import patterns
        if importing_module:
            # Handle relative imports starting with dots
            if import_path.startswith('.'):
                resolved = self._resolve_python_relative_import(import_path, importing_module)
                if resolved == symbol_module_path:
                    return True
            
            # Handle absolute imports that might be partial
            if '.' not in import_path:
                # Simple module name, might be imported directly
                if symbol_module_path.endswith(f".{import_path}"):
                    return True
            else:
                # Multi-part import path - check if it's a suffix
                if symbol_module_path.endswith(import_path):
                    return True
        
        return False
    
    def _resolve_python_relative_import(self, import_path: str, from_module: str) -> str:
        """Resolve Python relative imports (., .., etc.)."""
        dots = len(import_path) - len(import_path.lstrip('.'))
        remaining = import_path[dots:]
        
        # Split the current module path
        parts = from_module.split('.')
        
        # Go up 'dots' levels from the current module
        for _ in range(dots):
            if parts:
                parts.pop()
        
        # Add the remaining path if any
        if remaining:
            remaining = remaining.lstrip('.')
            if remaining:
                parts.extend(remaining.split('.'))
        
        return '.'.join(parts)


class PythonParser(TreeSitterParser):
    """Python language parser using tree-sitter."""
    
    def __init__(self):
        """Initialize Python parser."""
        try:
            import tree_sitter_python
            language = tree_sitter_python.language()
        except ImportError:
            # Mock language if tree-sitter not available
            language = None
        
        super().__init__(LanguageId("python"), language)
    
    def parse(self, code: str, file_id: FileId, symbol_counter: SymbolCounter) -> List[Symbol]:
        """Parse Python code and extract symbols."""
        if self._parser is None:
            return self._fallback_parse(code, file_id, symbol_counter)
        
        try:
            tree = self._parse_tree(code)
            context = ParserContext()
            symbols = []
            
            self._extract_symbols_from_node(
                tree.root_node, code, file_id, symbols, symbol_counter, context
            )
            
            return symbols
        except Exception:
            return self._fallback_parse(code, file_id, symbol_counter)
    
    def _fallback_parse(self, code: str, file_id: FileId, symbol_counter: SymbolCounter) -> List[Symbol]:
        """Fallback parsing using regex when tree-sitter is not available."""
        symbols = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines):
            # Function definitions
            func_match = re.match(r'^\s*(def|async def)\s+(\w+)\s*\(', line)
            if func_match:
                name = func_match.group(2)
                symbol = Symbol.new(
                    symbol_counter.next_id(),
                    name,
                    SymbolKind.Function,
                    file_id,
                    Range(line_num, 0, line_num, len(line))
                )
                symbol.signature = line.strip()
                symbols.append(symbol)
            
            # Class definitions
            class_match = re.match(r'^\s*class\s+(\w+)', line)
            if class_match:
                name = class_match.group(1)
                symbol = Symbol.new(
                    symbol_counter.next_id(),
                    name,
                    SymbolKind.Class,
                    file_id,
                    Range(line_num, 0, line_num, len(line))
                )
                symbol.signature = line.strip()
                symbols.append(symbol)
        
        return symbols
    
    def _extract_symbols_from_node(self, node, code: str, file_id: FileId, 
                                 symbols: List[Symbol], counter: SymbolCounter,
                                 context: ParserContext):
        """Extract symbols from AST node recursively."""
        if node.type == "function_definition":
            symbol = self._process_function(node, code, file_id, counter, context)
            if symbol:
                symbols.append(symbol)
        elif node.type == "class_definition":
            symbol = self._process_class(node, code, file_id, counter, context)
            if symbol:
                symbols.append(symbol)
        
        # Process children
        for child in node.children:
            self._extract_symbols_from_node(child, code, file_id, symbols, counter, context)
    
    def _process_function(self, node, code: str, file_id: FileId, 
                         counter: SymbolCounter, context: ParserContext) -> Optional[Symbol]:
        """Process a function definition node."""
        name_node = self._find_child_by_type(node, "identifier")
        if not name_node:
            return None
        
        name = self._get_node_text(name_node, code)
        range_obj = self._node_to_range(node)
        symbol_id = counter.next_id()
        
        kind = SymbolKind.Method if context.is_in_class() else SymbolKind.Function
        
        symbol = Symbol.new(symbol_id, name, kind, file_id, range_obj)
        symbol.signature = self._get_node_text(node, code).split('\n')[0]  # First line only
        symbol.scope_context = context.current_scope_context()
        
        return symbol
    
    def _process_class(self, node, code: str, file_id: FileId,
                      counter: SymbolCounter, context: ParserContext) -> Optional[Symbol]:
        """Process a class definition node."""
        name_node = self._find_child_by_type(node, "identifier")
        if not name_node:
            return None
        
        name = self._get_node_text(name_node, code)
        range_obj = self._node_to_range(node)
        symbol_id = counter.next_id()
        
        symbol = Symbol.new(symbol_id, name, SymbolKind.Class, file_id, range_obj)
        symbol.signature = self._get_node_text(node, code).split('\n')[0]  # First line only
        symbol.scope_context = context.current_scope_context()
        
        return symbol
    
    def extract_doc_comment(self, node: Any, code: str) -> Optional[str]:
        """Extract Python docstring."""
        # Look for string literal as first statement in function/class body
        if hasattr(node, 'children'):
            for child in node.children:
                if child.type == "block":
                    for stmt in child.children:
                        if stmt.type == "expression_statement":
                            expr = stmt.children[0] if stmt.children else None
                            if expr and expr.type == "string":
                                text = self._get_node_text(expr, code)
                                # Remove quotes and clean up
                                return text.strip('\'"').strip()
        return None
    
    def find_calls(self, code: str) -> List[Tuple[str, str, Range]]:
        """Find function/method calls in Python code."""
        calls = []
        
        if self._parser is None:
            return self._fallback_find_calls(code)
        
        try:
            tree = self._parse_tree(code)
            self._find_calls_in_node(tree.root_node, code, calls)
        except Exception:
            return self._fallback_find_calls(code)
        
        return calls
    
    def _fallback_find_calls(self, code: str) -> List[Tuple[str, str, Range]]:
        """Fallback call finding using regex."""
        calls = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines):
            # Simple function call pattern
            call_matches = re.finditer(r'(\w+)\.(\w+)\s*\(', line)
            for match in call_matches:
                caller = match.group(1)
                callee = match.group(2)
                range_obj = Range(line_num, match.start(), line_num, match.end())
                calls.append((caller, callee, range_obj))
        
        return calls
    
    def _find_calls_in_node(self, node, code: str, calls: List[Tuple[str, str, Range]]):
        """Find calls in AST node recursively."""
        if node.type == "call":
            # Extract caller and callee information
            function_node = node.children[0] if node.children else None
            if function_node:
                if function_node.type == "attribute":
                    # Method call: obj.method()
                    obj_node = function_node.children[0] if function_node.children else None
                    method_node = function_node.children[-1] if len(function_node.children) > 1 else None
                    
                    if obj_node and method_node:
                        caller = self._get_node_text(obj_node, code)
                        callee = self._get_node_text(method_node, code)
                        range_obj = self._node_to_range(node)
                        calls.append((caller, callee, range_obj))
                elif function_node.type == "identifier":
                    # Function call: func()
                    callee = self._get_node_text(function_node, code)
                    range_obj = self._node_to_range(node)
                    calls.append(("", callee, range_obj))
        
        # Process children
        for child in node.children:
            self._find_calls_in_node(child, code, calls)
    
    def find_implementations(self, code: str) -> List[Tuple[str, str, Range]]:
        """Find class inheritance (implementations) in Python."""
        implementations = []
        
        if self._parser is None:
            return self._fallback_find_implementations(code)
        
        try:
            tree = self._parse_tree(code)
            self._find_implementations_in_node(tree.root_node, code, implementations)
        except Exception:
            return self._fallback_find_implementations(code)
        
        return implementations
    
    def _fallback_find_implementations(self, code: str) -> List[Tuple[str, str, Range]]:
        """Fallback implementation finding using regex."""
        implementations = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines):
            # Class inheritance pattern
            inherit_match = re.match(r'^\s*class\s+(\w+)\s*\(\s*([^)]+)\s*\)', line)
            if inherit_match:
                class_name = inherit_match.group(1)
                base_classes = inherit_match.group(2)
                
                # Split base classes and create implementations
                for base_class in base_classes.split(','):
                    base_class = base_class.strip()
                    if base_class:
                        range_obj = Range(line_num, 0, line_num, len(line))
                        implementations.append((class_name, base_class, range_obj))
        
        return implementations
    
    def _find_implementations_in_node(self, node, code: str, 
                                    implementations: List[Tuple[str, str, Range]]):
        """Find implementations in AST node recursively."""
        if node.type == "class_definition":
            # Find class name
            name_node = self._find_child_by_type(node, "identifier")
            if name_node:
                class_name = self._get_node_text(name_node, code)
                
                # Find argument list (base classes)
                arg_list = self._find_child_by_type(node, "argument_list")
                if arg_list:
                    for arg in arg_list.children:
                        if arg.type == "identifier":
                            base_class = self._get_node_text(arg, code)
                            range_obj = self._node_to_range(node)
                            implementations.append((class_name, base_class, range_obj))
        
        # Process children
        for child in node.children:
            self._find_implementations_in_node(child, code, implementations)
    
    def find_uses(self, code: str) -> List[Tuple[str, str, Range]]:
        """Find type usage in Python code."""
        # Python has limited explicit type usage, mainly in type hints
        uses = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines):
            # Type hints in function parameters and return types
            type_hint_matches = re.finditer(r':\s*([A-Za-z_][A-Za-z0-9_\.]*)', line)
            for match in type_hint_matches:
                type_name = match.group(1)
                range_obj = Range(line_num, match.start(), line_num, match.end())
                uses.append(("", type_name, range_obj))
        
        return uses
    
    def find_defines(self, code: str) -> List[Tuple[str, str, Range]]:
        """Find method definitions in Python classes."""
        defines = []
        
        if self._parser is None:
            return self._fallback_find_defines(code)
        
        try:
            tree = self._parse_tree(code)
            context = ParserContext()
            self._find_defines_in_node(tree.root_node, code, defines, context)
        except Exception:
            return self._fallback_find_defines(code)
        
        return defines
    
    def _fallback_find_defines(self, code: str) -> List[Tuple[str, str, Range]]:
        """Fallback method definition finding."""
        defines = []
        lines = code.split('\n')
        current_class = None
        
        for line_num, line in enumerate(lines):
            # Track current class
            class_match = re.match(r'^\s*class\s+(\w+)', line)
            if class_match:
                current_class = class_match.group(1)
                continue
            
            # Method definition inside class
            if current_class:
                method_match = re.match(r'^\s+(def|async def)\s+(\w+)', line)
                if method_match:
                    method_name = method_match.group(2)
                    range_obj = Range(line_num, 0, line_num, len(line))
                    defines.append((current_class, method_name, range_obj))
        
        return defines
    
    def _find_defines_in_node(self, node, code: str, defines: List[Tuple[str, str, Range]],
                            context: ParserContext):
        """Find method definitions in AST."""
        if node.type == "class_definition":
            name_node = self._find_child_by_type(node, "identifier")
            if name_node:
                class_name = self._get_node_text(name_node, code)
                context.enter_scope(ScopeType.Class, class_name)
                
                # Process class body
                for child in node.children:
                    self._find_defines_in_node(child, code, defines, context)
                
                context.exit_scope()
                return
        
        elif node.type == "function_definition" and context.is_in_class():
            name_node = self._find_child_by_type(node, "identifier")
            if name_node:
                method_name = self._get_node_text(name_node, code)
                class_name = context.get_containing_class()
                if class_name:
                    range_obj = self._node_to_range(node)
                    defines.append((class_name, method_name, range_obj))
        
        # Process children for other node types
        for child in node.children:
            self._find_defines_in_node(child, code, defines, context)
    
    def find_imports(self, code: str, file_id: FileId) -> List[Import]:
        """Find import statements in Python code."""
        imports = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            
            # import module
            import_match = re.match(r'^import\s+([^#]+)', line)
            if import_match:
                modules = import_match.group(1)
                for module in modules.split(','):
                    module = module.strip()
                    if ' as ' in module:
                        path, alias = module.split(' as ', 1)
                        path = path.strip()
                        alias = alias.strip()
                    else:
                        path = module
                        alias = None
                    
                    import_obj = Import(
                        path=path,
                        alias=alias,
                        file_id=file_id,
                        range=Range(line_num, 0, line_num, len(line))
                    )
                    imports.append(import_obj)
            
            # from module import name
            from_import_match = re.match(r'^from\s+([^\s]+)\s+import\s+([^#]+)', line)
            if from_import_match:
                module = from_import_match.group(1)
                names = from_import_match.group(2)
                
                for name in names.split(','):
                    name = name.strip()
                    if name == '*':
                        # Star import
                        import_obj = Import(
                            path=module,
                            alias=None,
                            file_id=file_id,
                            range=Range(line_num, 0, line_num, len(line)),
                            is_glob=True
                        )
                        imports.append(import_obj)
                    else:
                        if ' as ' in name:
                            imported_name, alias = name.split(' as ', 1)
                            imported_name = imported_name.strip()
                            alias = alias.strip()
                        else:
                            imported_name = name
                            alias = None
                        
                        # Construct full path
                        full_path = f"{module}.{imported_name}"
                        
                        import_obj = Import(
                            path=full_path,
                            alias=alias,
                            file_id=file_id,
                            range=Range(line_num, 0, line_num, len(line))
                        )
                        imports.append(import_obj)
        
        return imports


# Register the Python language
def register_python_language():
    """Register Python language with the global registry."""
    definition = PythonLanguageDefinition()
    register_language(definition)


# Auto-register when module is imported
register_python_language()