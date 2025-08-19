"""
Pytest Configuration and Fixtures for Python Integration Tests
Provides shared fixtures and test utilities for all Python component tests
"""

import pytest
import asyncio
import tempfile
import shutil
import os
from pathlib import Path
from typing import Dict, Any, Generator, AsyncGenerator
import yaml
import json
from unittest.mock import Mock, AsyncMock

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "test_data"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_openapi_spec() -> Dict[str, Any]:
    """Provide a mock OpenAPI specification for testing."""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Test API",
            "version": "1.0.0",
            "description": "Test API for integration testing"
        },
        "servers": [
            {
                "url": "https://api.test.com",
                "description": "Test server"
            }
        ],
        "paths": {
            "/users": {
                "get": {
                    "operationId": "getUsers",
                    "summary": "Get all users",
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/User"}
                                    }
                                }
                            }
                        }
                    }
                },
                "post": {
                    "operationId": "createUser",
                    "summary": "Create a user",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/User"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Created",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/User"}
                                }
                            }
                        }
                    }
                }
            },
            "/users/{id}": {
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"}
                    }
                ],
                "get": {
                    "operationId": "getUserById",
                    "summary": "Get user by ID",
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/User"}
                                }
                            }
                        },
                        "404": {
                            "description": "User not found"
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "required": ["id", "name", "email"],
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "Unique identifier"
                        },
                        "name": {
                            "type": "string",
                            "description": "Full name"
                        },
                        "email": {
                            "type": "string",
                            "format": "email",
                            "description": "Email address"
                        },
                        "age": {
                            "type": "integer",
                            "minimum": 0,
                            "description": "Age in years"
                        },
                        "active": {
                            "type": "boolean",
                            "default": True,
                            "description": "Whether the user is active"
                        }
                    }
                }
            }
        }
    }


@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Provide a mock configuration for MCP generator testing."""
    return {
        "version": "1.0.0",
        "description": "Test MCP server",
        "author": "Test Author",
        "email": "test@example.com",
        "license": "MIT",
        "python_version": "3.13",
        "file_headers": {
            "copyright": "Test Copyright",
            "license": "MIT",
            "message": "Generated for testing"
        },
        "mcp_server_base_package": "mcp",
        "headers": {
            "Authorization": "Bearer test-token"
        }
    }


@pytest.fixture
def sample_spec_file(temp_dir: Path, mock_openapi_spec: Dict[str, Any]) -> Path:
    """Create a temporary OpenAPI spec file for testing."""
    spec_file = temp_dir / "test_api.yaml"
    with open(spec_file, 'w') as f:
        yaml.dump(mock_openapi_spec, f)
    return spec_file


@pytest.fixture
def sample_config_file(temp_dir: Path, mock_config: Dict[str, Any]) -> Path:
    """Create a temporary config file for testing."""
    config_file = temp_dir / "test_config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(mock_config, f)
    return config_file


@pytest.fixture
def mock_llm_factory():
    """Mock the LLM factory for testing."""
    mock_llm = Mock()
    mock_llm.invoke = Mock(return_value=Mock(content="Enhanced docstring content"))
    
    mock_factory = Mock()
    mock_factory.get_llm = Mock(return_value=mock_llm)
    
    return mock_factory


@pytest.fixture
def mock_subprocess():
    """Mock subprocess for testing external command execution."""
    mock = Mock()
    mock.run = Mock(return_value=Mock(returncode=0, stdout="", stderr=""))
    return mock


@pytest.fixture
async def mock_http_client():
    """Mock HTTP client for testing API calls."""
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=Mock(status_code=200, json=lambda: {"status": "ok"}))
    mock_client.post = AsyncMock(return_value=Mock(status_code=201, json=lambda: {"id": "123"}))
    mock_client.put = AsyncMock(return_value=Mock(status_code=200, json=lambda: {"updated": True}))
    mock_client.delete = AsyncMock(return_value=Mock(status_code=204))
    return mock_client


@pytest.fixture
def performance_test_data():
    """Generate performance test data."""
    return {
        "small_dataset": list(range(100)),
        "medium_dataset": list(range(1000)),
        "large_dataset": list(range(10000)),
        "complex_object": {
            "nested": {
                "data": {
                    "values": list(range(100)),
                    "metadata": {
                        "created": "2024-01-01",
                        "tags": ["test", "performance"]
                    }
                }
            }
        }
    }


@pytest.fixture
def mock_file_system(temp_dir: Path):
    """Create a mock file system structure for testing."""
    # Create directory structure
    dirs = [
        temp_dir / "src",
        temp_dir / "tests",
        temp_dir / "docs",
        temp_dir / "src" / "models",
        temp_dir / "src" / "api",
        temp_dir / "src" / "tools"
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Create sample files
    files = {
        temp_dir / "src" / "__init__.py": "",
        temp_dir / "src" / "models" / "__init__.py": "",
        temp_dir / "src" / "api" / "__init__.py": "",
        temp_dir / "src" / "tools" / "__init__.py": "",
        temp_dir / "src" / "main.py": "# Main application file",
        temp_dir / "requirements.txt": "pydantic>=2.0.0\nhttpx>=0.24.0",
        temp_dir / "README.md": "# Test Project"
    }
    
    for file_path, content in files.items():
        file_path.write_text(content)
    
    return temp_dir


# Test utilities
class TestUtils:
    """Utility class for common test operations."""
    
    @staticmethod
    def create_test_file(path: Path, content: str = "") -> Path:
        """Create a test file with given content."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path
    
    @staticmethod
    def assert_file_exists(path: Path) -> None:
        """Assert that a file exists."""
        assert path.exists(), f"File {path} does not exist"
    
    @staticmethod
    def assert_file_contains(path: Path, content: str) -> None:
        """Assert that a file contains specific content."""
        assert path.exists(), f"File {path} does not exist"
        file_content = path.read_text()
        assert content in file_content, f"File {path} does not contain '{content}'"
    
    @staticmethod
    def assert_directory_structure(base_path: Path, expected_structure: list) -> None:
        """Assert that a directory has the expected structure."""
        for expected_path in expected_structure:
            full_path = base_path / expected_path
            assert full_path.exists(), f"Expected path {full_path} does not exist"


@pytest.fixture
def test_utils():
    """Provide test utilities."""
    return TestUtils


# Pytest plugins and hooks
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "api: API tests")
    config.addinivalue_line("markers", "mcp: MCP generator tests")
    config.addinivalue_line("markers", "semantic: Semantic analysis tests")
    config.addinivalue_line("markers", "lsp: LSP component tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "security: Security tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add markers based on test file names
        if "test_mcp" in item.nodeid:
            item.add_marker(pytest.mark.mcp)
        if "test_semantic" in item.nodeid:
            item.add_marker(pytest.mark.semantic)
        if "test_lsp" in item.nodeid:
            item.add_marker(pytest.mark.lsp)
        if "test_performance" in item.nodeid:
            item.add_marker(pytest.mark.performance)
        if "test_api" in item.nodeid:
            item.add_marker(pytest.mark.api)
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        if "e2e" in item.nodeid:
            item.add_marker(pytest.mark.e2e)
        if "slow" in item.nodeid:
            item.add_marker(pytest.mark.slow)