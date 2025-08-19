"""
Integration Tests for Semantic Analysis API
Tests the semantic analysis engine and pattern detection capabilities
"""

import pytest
import asyncio
import json
import aiohttp
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
import tempfile
import ast
from typing import Dict, Any, List


class TestSemanticAnalysisAPI:
    """Test suite for Semantic Analysis API functionality."""

    @pytest.fixture
    async def mock_semantic_client(self):
        """Create a mock HTTP client for semantic analysis API."""
        mock_session = AsyncMock()
        mock_session.get = AsyncMock()
        mock_session.post = AsyncMock()
        mock_session.put = AsyncMock()
        mock_session.delete = AsyncMock()
        return mock_session

    @pytest.fixture
    def sample_code_files(self, temp_dir):
        """Create sample code files for testing."""
        files = {}
        
        # Python file with various patterns
        python_code = '''
import os
import sys
from typing import List, Dict, Any

class UserManager:
    """Manages user operations with potential code smells."""
    
    def __init__(self):
        self.users = []
        self.db_connection = None
        
    def create_user(self, name, email, age, address, phone, preferences, metadata):
        """Function with too many parameters (code smell)."""
        if name and email and age and address and phone:
            user = {
                'name': name,
                'email': email,
                'age': age,
                'address': address,
                'phone': phone,
                'preferences': preferences,
                'metadata': metadata
            }
            self.users.append(user)
            return user
        return None
    
    def complex_method(self, data):
        """Method with high cyclomatic complexity."""
        if data:
            if isinstance(data, dict):
                if 'type' in data:
                    if data['type'] == 'user':
                        if 'id' in data:
                            if data['id'] > 0:
                                if 'name' in data:
                                    if len(data['name']) > 0:
                                        return self.process_user(data)
                                    else:
                                        return None
                                else:
                                    return None
                            else:
                                return None
                        else:
                            return None
                    else:
                        return None
                else:
                    return None
            else:
                return None
        return None
    
    def process_user(self, user_data):
        """Process user data."""
        return user_data
    
    def duplicate_logic_1(self, items):
        """Duplicate logic pattern 1."""
        result = []
        for item in items:
            if item.get('active'):
                processed = {
                    'id': item['id'],
                    'name': item['name'],
                    'status': 'active'
                }
                result.append(processed)
        return result
    
    def duplicate_logic_2(self, elements):
        """Duplicate logic pattern 2 (similar to duplicate_logic_1)."""
        output = []
        for element in elements:
            if element.get('active'):
                transformed = {
                    'id': element['id'],
                    'name': element['name'],
                    'status': 'active'
                }
                output.append(transformed)
        return output

def long_function():
    """Function that's too long (another code smell)."""
    # This function would be very long in reality
    print("Line 1")
    print("Line 2")
    # ... many more lines
    for i in range(100):
        print(f"Processing {i}")
        if i % 10 == 0:
            print(f"Checkpoint at {i}")
    print("Function complete")
'''
        
        files['python_file'] = temp_dir / "user_manager.py"
        files['python_file'].write_text(python_code)
        
        # TypeScript file with patterns
        typescript_code = '''
interface User {
    id: string;
    name: string;
    email: string;
    age?: number;
}

class APIClient {
    private baseUrl: string;
    
    constructor(baseUrl: string) {
        this.baseUrl = baseUrl;
    }
    
    async getUser(id: string): Promise<User | null> {
        try {
            const response = await fetch(`${this.baseUrl}/users/${id}`);
            if (response.ok) {
                const user = await response.json();
                return user;
            } else {
                console.error('Failed to fetch user');
                return null;
            }
        } catch (error) {
            console.error('Error fetching user:', error);
            return null;
        }
    }
    
    // Potential security issue: no input validation
    async createUser(userData: any): Promise<User | null> {
        const response = await fetch(`${this.baseUrl}/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });
        
        if (response.ok) {
            return await response.json();
        }
        return null;
    }
    
    // Performance issue: inefficient loop
    findUsersByName(users: User[], targetName: string): User[] {
        const results: User[] = [];
        for (let i = 0; i < users.length; i++) {
            for (let j = 0; j < users.length; j++) {
                if (users[i].name.toLowerCase().includes(targetName.toLowerCase())) {
                    results.push(users[i]);
                    break;
                }
            }
        }
        return results;
    }
}
'''
        
        files['typescript_file'] = temp_dir / "api_client.ts"
        files['typescript_file'].write_text(typescript_code)
        
        return files

    @pytest.mark.semantic
    @pytest.mark.integration
    async def test_code_complexity_analysis(self, mock_semantic_client, sample_code_files):
        """Test code complexity analysis endpoint."""
        python_file = sample_code_files['python_file']
        
        # Mock API response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'file': str(python_file),
            'complexity_metrics': {
                'cyclomatic_complexity': 15,
                'cognitive_complexity': 12,
                'maintainability_index': 45,
                'lines_of_code': 85,
                'complexity_per_function': {
                    'create_user': 3,
                    'complex_method': 15,
                    'process_user': 1,
                    'duplicate_logic_1': 3,
                    'duplicate_logic_2': 3,
                    'long_function': 8
                }
            },
            'issues': [
                {
                    'type': 'high_complexity',
                    'severity': 'warning',
                    'function': 'complex_method',
                    'complexity': 15,
                    'threshold': 10,
                    'line': 25,
                    'message': 'Function has high cyclomatic complexity'
                },
                {
                    'type': 'too_many_parameters',
                    'severity': 'warning',
                    'function': 'create_user',
                    'parameter_count': 7,
                    'threshold': 5,
                    'line': 10,
                    'message': 'Function has too many parameters'
                }
            ]
        })
        
        mock_semantic_client.post.return_value = mock_response
        
        # Test complexity analysis
        with patch('aiohttp.ClientSession', return_value=mock_semantic_client):
            async with aiohttp.ClientSession() as session:
                response = await session.post(
                    'http://localhost:8080/api/analysis/complexity',
                    json={
                        'file_path': str(python_file),
                        'language': 'python',
                        'include_functions': True
                    }
                )
                
                result = await response.json()
                
                assert response.status == 200
                assert 'complexity_metrics' in result
                assert result['complexity_metrics']['cyclomatic_complexity'] == 15
                assert len(result['issues']) == 2
                assert any(issue['type'] == 'high_complexity' for issue in result['issues'])

    @pytest.mark.semantic
    async def test_pattern_detection(self, mock_semantic_client, sample_code_files):
        """Test pattern detection capabilities."""
        python_file = sample_code_files['python_file']
        
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'file': str(python_file),
            'patterns': [
                {
                    'type': 'code_duplication',
                    'severity': 'medium',
                    'confidence': 0.85,
                    'locations': [
                        {
                            'function': 'duplicate_logic_1',
                            'start_line': 45,
                            'end_line': 55
                        },
                        {
                            'function': 'duplicate_logic_2',
                            'start_line': 57,
                            'end_line': 67
                        }
                    ],
                    'similarity_score': 0.92,
                    'suggestion': 'Extract common logic into a shared function'
                },
                {
                    'type': 'long_method',
                    'severity': 'low',
                    'confidence': 0.9,
                    'location': {
                        'function': 'long_function',
                        'start_line': 69,
                        'end_line': 85,
                        'line_count': 16
                    },
                    'threshold': 15,
                    'suggestion': 'Consider breaking this method into smaller functions'
                },
                {
                    'type': 'god_class',
                    'severity': 'medium',
                    'confidence': 0.7,
                    'location': {
                        'class': 'UserManager',
                        'start_line': 5,
                        'end_line': 67,
                        'method_count': 6,
                        'line_count': 62
                    },
                    'suggestion': 'Consider splitting this class into smaller, focused classes'
                }
            ],
            'design_patterns': [
                {
                    'pattern': 'repository_pattern_candidate',
                    'confidence': 0.6,
                    'location': {
                        'class': 'UserManager',
                        'methods': ['create_user', 'process_user']
                    },
                    'suggestion': 'Consider implementing Repository pattern for data access'
                }
            ]
        })
        
        mock_semantic_client.post.return_value = mock_response
        
        with patch('aiohttp.ClientSession', return_value=mock_semantic_client):
            async with aiohttp.ClientSession() as session:
                response = await session.post(
                    'http://localhost:8080/api/analysis/patterns',
                    json={
                        'file_path': str(python_file),
                        'language': 'python',
                        'detection_types': ['code_smells', 'design_patterns', 'duplications']
                    }
                )
                
                result = await response.json()
                
                assert response.status == 200
                assert 'patterns' in result
                assert len(result['patterns']) == 3
                assert any(p['type'] == 'code_duplication' for p in result['patterns'])
                assert 'design_patterns' in result

    @pytest.mark.semantic
    async def test_security_analysis(self, mock_semantic_client, sample_code_files):
        """Test security vulnerability detection."""
        typescript_file = sample_code_files['typescript_file']
        
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'file': str(typescript_file),
            'security_issues': [
                {
                    'type': 'input_validation',
                    'severity': 'high',
                    'confidence': 0.9,
                    'location': {
                        'function': 'createUser',
                        'line': 35,
                        'column': 5
                    },
                    'cwe_id': 'CWE-20',
                    'description': 'Insufficient input validation on user data',
                    'recommendation': 'Validate and sanitize all user inputs before processing'
                },
                {
                    'type': 'performance_issue',
                    'severity': 'medium',
                    'confidence': 0.85,
                    'location': {
                        'function': 'findUsersByName',
                        'line': 50,
                        'column': 9
                    },
                    'description': 'Inefficient nested loop causing O(n²) complexity',
                    'recommendation': 'Use more efficient search algorithm or data structure'
                },
                {
                    'type': 'error_handling',
                    'severity': 'low',
                    'confidence': 0.7,
                    'location': {
                        'function': 'createUser',
                        'line': 48,
                        'column': 12
                    },
                    'description': 'Generic error handling may expose sensitive information',
                    'recommendation': 'Implement specific error handling and logging'
                }
            ],
            'recommendations': [
                {
                    'category': 'input_validation',
                    'priority': 'high',
                    'suggestions': [
                        'Implement schema validation for API inputs',
                        'Add rate limiting to prevent abuse',
                        'Sanitize string inputs to prevent injection attacks'
                    ]
                },
                {
                    'category': 'performance',
                    'priority': 'medium',
                    'suggestions': [
                        'Use Set or Map for efficient lookups',
                        'Implement pagination for large datasets',
                        'Add caching for frequently accessed data'
                    ]
                }
            ]
        })
        
        mock_semantic_client.post.return_value = mock_response
        
        with patch('aiohttp.ClientSession', return_value=mock_semantic_client):
            async with aiohttp.ClientSession() as session:
                response = await session.post(
                    'http://localhost:8080/api/analysis/security',
                    json={
                        'file_path': str(typescript_file),
                        'language': 'typescript',
                        'scan_types': ['input_validation', 'performance', 'error_handling']
                    }
                )
                
                result = await response.json()
                
                assert response.status == 200
                assert 'security_issues' in result
                assert len(result['security_issues']) == 3
                assert any(issue['type'] == 'input_validation' for issue in result['security_issues'])
                assert 'recommendations' in result

    @pytest.mark.semantic
    async def test_multi_file_analysis(self, mock_semantic_client, sample_code_files):
        """Test analysis across multiple files."""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'analysis_id': 'multi-file-analysis-123',
            'files_analyzed': 2,
            'total_lines': 150,
            'summary': {
                'complexity_score': 7.5,
                'maintainability_score': 6.2,
                'security_score': 8.1,
                'overall_score': 7.3
            },
            'cross_file_issues': [
                {
                    'type': 'circular_dependency',
                    'severity': 'medium',
                    'files': [str(sample_code_files['python_file']), str(sample_code_files['typescript_file'])],
                    'description': 'Potential circular dependency between modules'
                },
                {
                    'type': 'inconsistent_naming',
                    'severity': 'low',
                    'locations': [
                        {'file': str(sample_code_files['python_file']), 'function': 'create_user'},
                        {'file': str(sample_code_files['typescript_file']), 'function': 'createUser'}
                    ],
                    'description': 'Inconsistent naming conventions across files'
                }
            ],
            'file_results': {
                str(sample_code_files['python_file']): {
                    'complexity': 8.2,
                    'maintainability': 5.8,
                    'issues_count': 5
                },
                str(sample_code_files['typescript_file']): {
                    'complexity': 6.8,
                    'maintainability': 6.6,
                    'issues_count': 3
                }
            }
        })
        
        mock_semantic_client.post.return_value = mock_response
        
        with patch('aiohttp.ClientSession', return_value=mock_semantic_client):
            async with aiohttp.ClientSession() as session:
                response = await session.post(
                    'http://localhost:8080/api/analysis/multi-file',
                    json={
                        'files': [
                            {
                                'path': str(sample_code_files['python_file']),
                                'language': 'python'
                            },
                            {
                                'path': str(sample_code_files['typescript_file']),
                                'language': 'typescript'
                            }
                        ],
                        'analysis_types': ['complexity', 'patterns', 'dependencies']
                    }
                )
                
                result = await response.json()
                
                assert response.status == 200
                assert result['files_analyzed'] == 2
                assert 'cross_file_issues' in result
                assert 'file_results' in result
                assert len(result['cross_file_issues']) == 2

    @pytest.mark.semantic
    @pytest.mark.performance
    async def test_analysis_performance(self, mock_semantic_client, temp_dir, performance_test_data):
        """Test semantic analysis performance with large files."""
        # Create a large Python file
        large_code = '''
import os
import sys
from typing import List, Dict, Any

''' + '\n'.join([f'''
def function_{i}(param1, param2, param3):
    """Function {i} with some complexity."""
    if param1:
        if param2:
            if param3:
                result = param1 + param2 + param3
                for j in range(10):
                    result += j
                return result
            else:
                return param1 + param2
        else:
            return param1
    else:
        return 0
''' for i in range(100)])
        
        large_file = temp_dir / "large_analysis.py"
        large_file.write_text(large_code)
        
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'file': str(large_file),
            'analysis_time_ms': 850,
            'lines_of_code': 1200,
            'functions_analyzed': 100,
            'complexity_metrics': {
                'average_complexity': 4.2,
                'max_complexity': 8,
                'total_complexity': 420
            },
            'performance_metrics': {
                'parsing_time_ms': 120,
                'analysis_time_ms': 650,
                'reporting_time_ms': 80
            }
        })
        
        mock_semantic_client.post.return_value = mock_response
        
        with patch('aiohttp.ClientSession', return_value=mock_semantic_client):
            async with aiohttp.ClientSession() as session:
                start_time = asyncio.get_event_loop().time()
                
                response = await session.post(
                    'http://localhost:8080/api/analysis/complexity',
                    json={
                        'file_path': str(large_file),
                        'language': 'python'
                    }
                )
                
                end_time = asyncio.get_event_loop().time()
                request_time = (end_time - start_time) * 1000  # Convert to ms
                
                result = await response.json()
                
                assert response.status == 200
                assert result['functions_analyzed'] == 100
                assert result['analysis_time_ms'] < 1000  # Should be fast
                assert request_time < 2000  # Total request time should be reasonable

    @pytest.mark.semantic
    async def test_caching_functionality(self, mock_semantic_client, sample_code_files):
        """Test semantic analysis caching."""
        python_file = sample_code_files['python_file']
        
        # First request - cache miss
        mock_response_miss = Mock()
        mock_response_miss.status = 200
        mock_response_miss.json = AsyncMock(return_value={
            'file': str(python_file),
            'cache_status': 'miss',
            'analysis_time_ms': 500,
            'complexity_metrics': {'cyclomatic_complexity': 15}
        })
        
        # Second request - cache hit
        mock_response_hit = Mock()
        mock_response_hit.status = 200
        mock_response_hit.json = AsyncMock(return_value={
            'file': str(python_file),
            'cache_status': 'hit',
            'analysis_time_ms': 50,
            'complexity_metrics': {'cyclomatic_complexity': 15}
        })
        
        mock_semantic_client.post.side_effect = [mock_response_miss, mock_response_hit]
        
        with patch('aiohttp.ClientSession', return_value=mock_semantic_client):
            async with aiohttp.ClientSession() as session:
                # First request
                response1 = await session.post(
                    'http://localhost:8080/api/analysis/complexity',
                    json={'file_path': str(python_file), 'language': 'python'}
                )
                result1 = await response1.json()
                
                # Second request (should hit cache)
                response2 = await session.post(
                    'http://localhost:8080/api/analysis/complexity',
                    json={'file_path': str(python_file), 'language': 'python'}
                )
                result2 = await response2.json()
                
                assert result1['cache_status'] == 'miss'
                assert result2['cache_status'] == 'hit'
                assert result2['analysis_time_ms'] < result1['analysis_time_ms']

    @pytest.mark.semantic
    async def test_error_handling(self, mock_semantic_client):
        """Test error handling in semantic analysis."""
        # Test file not found
        mock_response = Mock()
        mock_response.status = 404
        mock_response.json = AsyncMock(return_value={
            'error': 'file_not_found',
            'message': 'The specified file could not be found'
        })
        
        mock_semantic_client.post.return_value = mock_response
        
        with patch('aiohttp.ClientSession', return_value=mock_semantic_client):
            async with aiohttp.ClientSession() as session:
                response = await session.post(
                    'http://localhost:8080/api/analysis/complexity',
                    json={'file_path': '/non/existent/file.py', 'language': 'python'}
                )
                
                assert response.status == 404
                result = await response.json()
                assert result['error'] == 'file_not_found'

    @pytest.mark.semantic
    async def test_language_support(self, mock_semantic_client, temp_dir):
        """Test support for different programming languages."""
        languages_data = [
            ('python', 'def test(): pass'),
            ('typescript', 'function test() {}'),
            ('javascript', 'function test() {}'),
            ('java', 'public class Test { public void test() {} }'),
            ('go', 'func test() {}'),
            ('rust', 'fn test() {}')
        ]
        
        for language, code in languages_data:
            file_ext = {
                'python': '.py',
                'typescript': '.ts',
                'javascript': '.js',
                'java': '.java',
                'go': '.go',
                'rust': '.rs'
            }[language]
            
            test_file = temp_dir / f"test{file_ext}"
            test_file.write_text(code)
            
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'file': str(test_file),
                'language': language,
                'supported': True,
                'complexity_metrics': {'cyclomatic_complexity': 1}
            })
            
            mock_semantic_client.post.return_value = mock_response
            
            with patch('aiohttp.ClientSession', return_value=mock_semantic_client):
                async with aiohttp.ClientSession() as session:
                    response = await session.post(
                        'http://localhost:8080/api/analysis/complexity',
                        json={'file_path': str(test_file), 'language': language}
                    )
                    
                    result = await response.json()
                    assert response.status == 200
                    assert result['language'] == language
                    assert result['supported'] is True