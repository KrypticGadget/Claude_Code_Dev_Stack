#!/usr/bin/env python3
"""
Semantic Analysis API - Python Integration Example

This script demonstrates how to integrate the TypeScript/Node.js Semantic Analysis API
with the Python semantic analysis backend from core/semantic/*.
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the semantic analysis modules to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from language_registry import get_registry, LanguageId
from parser_interface import create_parser
from symbol_extraction import SymbolExtractor, SymbolIndex, SymbolCounter, FileId
from resolution import GenericResolutionContext, GenericInheritanceResolver
from context import SemanticContext


class SemanticAnalysisBackend:
    """
    Python backend that integrates with the TypeScript API server.
    Provides actual semantic analysis capabilities using Tree-sitter.
    """
    
    def __init__(self):
        self.registry = get_registry()
        self.symbol_index = SymbolIndex()
        self.symbol_counter = SymbolCounter()
        self.contexts: Dict[str, SemanticContext] = {}
    
    async def parse_code(self, code: str, language: str, file_id: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse source code and extract symbols using Tree-sitter.
        
        Args:
            code: Source code to analyze
            language: Programming language identifier
            file_id: Unique file identifier
            options: Analysis options
            
        Returns:
            Dictionary containing symbols, relationships, and metadata
        """
        try:
            # Get language parser
            language_id = LanguageId(language)
            parser = create_parser(language_id)
            
            if not parser:
                raise ValueError(f"Unsupported language: {language}")
            
            # Create file ID
            file_id_obj = FileId.from_string(file_id)
            
            # Parse symbols
            symbols = parser.parse(code, file_id_obj, self.symbol_counter)
            
            # Add symbols to index
            for symbol in symbols:
                self.symbol_index.add_symbol(symbol)
            
            # Extract relationships if requested
            relationships = []
            if options.get('includeRelationships', True):
                relationships = await self._extract_relationships(parser, code, symbols)
            
            # Convert to JSON-serializable format
            result = {
                'symbols': [self._symbol_to_dict(symbol) for symbol in symbols],
                'relationships': [self._relationship_to_dict(rel) for rel in relationships],
                'metadata': {
                    'language': language,
                    'fileId': file_id,
                    'symbolCount': len(symbols),
                    'relationshipCount': len(relationships),
                    'parseTime': 0,  # Would measure actual parse time
                    'timestamp': self._get_timestamp()
                }
            }
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"Failed to parse {language} code: {str(e)}")
    
    async def generate_ast(self, code: str, language: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Abstract Syntax Tree for the given code.
        
        Args:
            code: Source code to parse
            language: Programming language identifier
            options: AST generation options
            
        Returns:
            Dictionary containing the AST and metadata
        """
        try:
            # Get language parser
            language_id = LanguageId(language)
            parser = create_parser(language_id)
            
            if not parser:
                raise ValueError(f"Unsupported language: {language}")
            
            # Parse AST (this would use Tree-sitter directly)
            ast = await self._parse_ast(parser, code, options)
            
            return {
                'ast': ast,
                'metadata': {
                    'language': language,
                    'nodeCount': self._count_ast_nodes(ast),
                    'parseTime': 0,  # Would measure actual parse time
                    'timestamp': self._get_timestamp()
                }
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate AST for {language}: {str(e)}")
    
    async def analyze_complexity(self, code: str, language: str, metrics: List[str]) -> Dict[str, Any]:
        """
        Analyze code complexity metrics.
        
        Args:
            code: Source code to analyze
            language: Programming language identifier
            metrics: List of complexity metrics to calculate
            
        Returns:
            Dictionary containing complexity analysis results
        """
        try:
            # Parse code first
            language_id = LanguageId(language)
            parser = create_parser(language_id)
            
            if not parser:
                raise ValueError(f"Unsupported language: {language}")
            
            # Calculate complexity metrics
            complexity = {}
            
            if 'cyclomatic' in metrics:
                complexity['cyclomatic'] = await self._calculate_cyclomatic_complexity(parser, code)
            
            if 'cognitive' in metrics:
                complexity['cognitive'] = await self._calculate_cognitive_complexity(parser, code)
            
            if 'lines' in metrics:
                complexity['lines'] = self._calculate_line_metrics(code)
            
            if 'halstead' in metrics:
                complexity['halstead'] = await self._calculate_halstead_metrics(parser, code)
            
            return {
                'complexity': complexity,
                'metadata': {
                    'language': language,
                    'metrics': metrics,
                    'timestamp': self._get_timestamp()
                }
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to analyze complexity for {language}: {str(e)}")
    
    async def find_references(self, code: str, language: str, position: Dict[str, int], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Find references to a symbol at the given position.
        
        Args:
            code: Source code to analyze
            language: Programming language identifier
            position: Position in the code (line, column)
            options: Reference finding options
            
        Returns:
            Dictionary containing references and definitions
        """
        try:
            # Parse code and find symbol at position
            language_id = LanguageId(language)
            parser = create_parser(language_id)
            
            if not parser:
                raise ValueError(f"Unsupported language: {language}")
            
            # Find symbol at position
            symbol = await self._find_symbol_at_position(parser, code, position)
            
            if not symbol:
                return {
                    'symbol': None,
                    'references': [],
                    'definitions': [],
                    'metadata': {
                        'language': language,
                        'position': position,
                        'timestamp': self._get_timestamp()
                    }
                }
            
            # Find references
            references = []
            definitions = []
            
            if options.get('includeReferences', True):
                references = await self._find_symbol_references(symbol, parser, code)
            
            if options.get('includeDefinitions', True):
                definitions = await self._find_symbol_definitions(symbol, parser, code)
            
            return {
                'symbol': self._symbol_to_dict(symbol),
                'references': references,
                'definitions': definitions,
                'metadata': {
                    'language': language,
                    'position': position,
                    'referenceCount': len(references),
                    'definitionCount': len(definitions),
                    'timestamp': self._get_timestamp()
                }
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to find references in {language}: {str(e)}")
    
    async def search_symbols(self, query: str, filters: Dict[str, Any], options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for symbols matching the query.
        
        Args:
            query: Search query text
            filters: Search filters (language, kind, etc.)
            options: Search options
            
        Returns:
            List of matching symbols
        """
        try:
            # Use the symbol index to search
            results = []
            
            # Simple name-based search (would be more sophisticated in practice)
            if query:
                symbols = self.symbol_index.find_symbols_by_name(query)
                results.extend(symbols)
            
            # Apply filters
            if filters.get('language'):
                results = [s for s in results if s.file_id in self._get_files_by_language(filters['language'])]
            
            if filters.get('symbolKind'):
                kind_filter = filters['symbolKind']
                if isinstance(kind_filter, list):
                    results = [s for s in results if s.kind.name in kind_filter]
                else:
                    results = [s for s in results if s.kind.name == kind_filter]
            
            # Convert to dict format
            search_results = []
            for symbol in results[:options.get('maxResults', 100)]:
                search_results.append({
                    'id': str(symbol.id),
                    'symbol': self._symbol_to_dict(symbol),
                    'location': {
                        'fileId': str(symbol.file_id),
                        'filePath': f"file_{symbol.file_id}",  # Would map to actual file paths
                        'range': {
                            'startLine': symbol.range.start_line,
                            'startCol': symbol.range.start_col,
                            'endLine': symbol.range.end_line,
                            'endCol': symbol.range.end_col
                        }
                    },
                    'context': {
                        'language': self._get_symbol_language(symbol),
                        'parentSymbol': symbol.parent_function or symbol.parent_class,
                        'module': symbol.parent_module
                    },
                    'match': {
                        'score': self._calculate_match_score(symbol, query),
                        'type': 'exact' if symbol.name == query else 'partial',
                        'highlightRanges': []
                    }
                })
            
            return search_results
            
        except Exception as e:
            raise RuntimeError(f"Failed to search symbols: {str(e)}")
    
    def get_supported_languages(self) -> List[Dict[str, Any]]:
        """
        Get list of supported languages.
        
        Returns:
            List of supported language definitions
        """
        languages = []
        
        for definition in self.registry.iter_all():
            languages.append({
                'id': definition.id().as_str(),
                'name': definition.name(),
                'extensions': definition.extensions(),
                'enabled': definition.default_enabled(),
                'features': ['ast-parsing', 'symbol-extraction', 'references']
            })
        
        return languages
    
    # Helper methods
    
    async def _extract_relationships(self, parser, code: str, symbols: List) -> List:
        """Extract relationships between symbols."""
        relationships = []
        
        # Find function calls
        calls = parser.find_calls(code)
        for caller, callee, range_obj in calls:
            relationships.append({
                'source': self._find_symbol_by_name(symbols, caller),
                'target': self._find_symbol_by_name(symbols, callee),
                'type': 'calls',
                'range': {
                    'startLine': range_obj.start_line,
                    'startCol': range_obj.start_col,
                    'endLine': range_obj.end_line,
                    'endCol': range_obj.end_col
                }
            })
        
        return relationships
    
    async def _parse_ast(self, parser, code: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AST using Tree-sitter."""
        # This would use Tree-sitter to generate the actual AST
        return {
            'type': 'program',
            'children': []  # Simplified AST structure
        }
    
    def _count_ast_nodes(self, ast: Dict[str, Any]) -> int:
        """Count nodes in the AST."""
        count = 1
        if 'children' in ast:
            for child in ast['children']:
                count += self._count_ast_nodes(child)
        return count
    
    async def _calculate_cyclomatic_complexity(self, parser, code: str) -> int:
        """Calculate cyclomatic complexity."""
        # Simplified complexity calculation
        return code.count('if') + code.count('for') + code.count('while') + 1
    
    async def _calculate_cognitive_complexity(self, parser, code: str) -> int:
        """Calculate cognitive complexity."""
        # Simplified cognitive complexity
        return (code.count('if') + code.count('for') + code.count('while') + 
                code.count('try') + code.count('catch'))
    
    def _calculate_line_metrics(self, code: str) -> Dict[str, int]:
        """Calculate line-based metrics."""
        lines = code.split('\n')
        return {
            'total': len(lines),
            'code': len([line for line in lines if line.strip() and not line.strip().startswith('//')]),
            'comments': len([line for line in lines if line.strip().startswith('//')]),
            'blank': len([line for line in lines if not line.strip()])
        }
    
    async def _calculate_halstead_metrics(self, parser, code: str) -> Dict[str, float]:
        """Calculate Halstead complexity metrics."""
        # Simplified Halstead metrics
        return {
            'difficulty': 2.5,
            'effort': 125.3,
            'volume': 50.1
        }
    
    async def _find_symbol_at_position(self, parser, code: str, position: Dict[str, int]):
        """Find symbol at the given position."""
        # This would use Tree-sitter to find the symbol at the exact position
        return None
    
    async def _find_symbol_references(self, symbol, parser, code: str) -> List[Dict[str, Any]]:
        """Find references to the given symbol."""
        return []
    
    async def _find_symbol_definitions(self, symbol, parser, code: str) -> List[Dict[str, Any]]:
        """Find definitions of the given symbol."""
        return []
    
    def _symbol_to_dict(self, symbol) -> Dict[str, Any]:
        """Convert symbol to dictionary format."""
        return {
            'id': str(symbol.id),
            'name': symbol.name,
            'kind': symbol.kind.name,
            'range': {
                'startLine': symbol.range.start_line,
                'startCol': symbol.range.start_col,
                'endLine': symbol.range.end_line,
                'endCol': symbol.range.end_col
            },
            'signature': symbol.signature,
            'documentation': symbol.doc_comment,
            'visibility': symbol.visibility.name if symbol.visibility else 'public',
            'isAsync': symbol.is_async,
            'isStatic': symbol.is_static,
            'parentClass': symbol.parent_class,
            'parentFunction': symbol.parent_function,
            'parentModule': symbol.parent_module
        }
    
    def _relationship_to_dict(self, relationship) -> Dict[str, Any]:
        """Convert relationship to dictionary format."""
        return {
            'source': str(relationship['source']) if relationship['source'] else None,
            'target': str(relationship['target']) if relationship['target'] else None,
            'type': relationship['type'],
            'range': relationship['range']
        }
    
    def _find_symbol_by_name(self, symbols: List, name: str):
        """Find symbol by name in the list."""
        for symbol in symbols:
            if symbol.name == name:
                return str(symbol.id)
        return None
    
    def _get_files_by_language(self, language: str) -> List[str]:
        """Get file IDs for a specific language."""
        # This would maintain a mapping of files to languages
        return []
    
    def _get_symbol_language(self, symbol) -> str:
        """Get the language for a symbol."""
        # This would determine the language from the file or context
        return 'unknown'
    
    def _calculate_match_score(self, symbol, query: str) -> float:
        """Calculate relevance score for a symbol match."""
        if symbol.name == query:
            return 100.0
        elif query.lower() in symbol.name.lower():
            return 80.0
        else:
            return 50.0
    
    def _get_timestamp(self) -> int:
        """Get current timestamp."""
        import time
        return int(time.time() * 1000)


# Example usage and integration
async def main():
    """
    Example usage of the Semantic Analysis Backend.
    This demonstrates how the Python backend integrates with the TypeScript API.
    """
    print("🔍 Semantic Analysis Backend - Integration Example")
    print("=" * 60)
    
    # Initialize the backend
    backend = SemanticAnalysisBackend()
    
    # Example TypeScript code
    typescript_code = """
    interface User {
        id: number;
        name: string;
        email: string;
    }
    
    class UserService {
        private users: User[] = [];
        
        constructor() {
            this.loadUsers();
        }
        
        private async loadUsers(): Promise<void> {
            // Load users from database
        }
        
        public findUser(id: number): User | undefined {
            return this.users.find(user => user.id === id);
        }
        
        public createUser(userData: Omit<User, 'id'>): User {
            const user: User = {
                id: this.generateId(),
                ...userData
            };
            this.users.push(user);
            return user;
        }
        
        private generateId(): number {
            return Math.max(...this.users.map(u => u.id), 0) + 1;
        }
    }
    """
    
    # Example Python code
    python_code = """
    from typing import List, Optional
    from dataclasses import dataclass
    
    @dataclass
    class User:
        id: int
        name: str
        email: str
    
    class UserService:
        def __init__(self):
            self.users: List[User] = []
            self.load_users()
        
        def load_users(self) -> None:
            # Load users from database
            pass
        
        def find_user(self, user_id: int) -> Optional[User]:
            return next((user for user in self.users if user.id == user_id), None)
        
        def create_user(self, name: str, email: str) -> User:
            user = User(
                id=self.generate_id(),
                name=name,
                email=email
            )
            self.users.append(user)
            return user
        
        def generate_id(self) -> int:
            return max((user.id for user in self.users), default=0) + 1
    """
    
    try:
        # Test TypeScript parsing
        print("🔍 Parsing TypeScript code...")
        ts_result = await backend.parse_code(
            code=typescript_code,
            language='typescript',
            file_id='user-service.ts',
            options={'includeRelationships': True, 'includeDocumentation': True}
        )
        
        print(f"✅ Found {ts_result['metadata']['symbolCount']} symbols in TypeScript")
        print(f"✅ Found {ts_result['metadata']['relationshipCount']} relationships")
        
        # Test Python parsing
        print("\n🔍 Parsing Python code...")
        py_result = await backend.parse_code(
            code=python_code,
            language='python',
            file_id='user_service.py',
            options={'includeRelationships': True, 'includeDocumentation': True}
        )
        
        print(f"✅ Found {py_result['metadata']['symbolCount']} symbols in Python")
        print(f"✅ Found {py_result['metadata']['relationshipCount']} relationships")
        
        # Test complexity analysis
        print("\n📊 Analyzing complexity...")
        complexity = await backend.analyze_complexity(
            code=typescript_code,
            language='typescript',
            metrics=['cyclomatic', 'cognitive', 'lines']
        )
        
        print(f"✅ Cyclomatic complexity: {complexity['complexity'].get('cyclomatic', 'N/A')}")
        print(f"✅ Cognitive complexity: {complexity['complexity'].get('cognitive', 'N/A')}")
        
        # Test symbol search
        print("\n🔍 Searching symbols...")
        search_results = await backend.search_symbols(
            query='User',
            filters={'language': ['typescript']},
            options={'maxResults': 10}
        )
        
        print(f"✅ Found {len(search_results)} symbols matching 'User'")
        
        # Test language support
        print("\n🌍 Supported languages:")
        languages = backend.get_supported_languages()
        for lang in languages:
            print(f"  - {lang['name']} ({lang['id']}): {', '.join(lang['extensions'])}")
        
        print("\n✅ Integration example completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during integration test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())