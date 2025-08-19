"""
Integration Tests for MCP Generator
Tests the complete MCP code generation pipeline including templates, file generation, and validation
"""

import pytest
import os
import tempfile
import yaml
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import subprocess

# Import the MCP generator components
import sys
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "core" / "generators" / "python" / "openapi_mcp_codegen"))

from mcp_codegen import MCPGenerator


class TestMCPGenerator:
    """Test suite for MCP Generator functionality."""

    @pytest.mark.mcp
    @pytest.mark.integration
    def test_mcp_generator_initialization(self, temp_dir, sample_spec_file, sample_config_file):
        """Test MCP generator initialization with valid inputs."""
        script_dir = Path(__file__).parent.parent.parent.parent / "core" / "generators" / "python" / "openapi_mcp_codegen"
        
        generator = MCPGenerator(
            script_dir=str(script_dir),
            spec_path=str(sample_spec_file),
            output_dir=str(temp_dir),
            config_path=str(sample_config_file)
        )
        
        assert generator.script_dir == str(script_dir)
        assert generator.spec_path == str(sample_spec_file)
        assert generator.output_dir == str(temp_dir)
        assert generator.spec is not None
        assert generator.config is not None
        assert "test_api" in generator.mcp_name.lower()

    @pytest.mark.mcp
    def test_spec_loading_yaml(self, temp_dir, mock_openapi_spec):
        """Test loading OpenAPI spec from YAML file."""
        spec_file = temp_dir / "test.yaml"
        with open(spec_file, 'w') as f:
            yaml.dump(mock_openapi_spec, f)
        
        script_dir = Path(__file__).parent.parent.parent.parent / "core" / "generators" / "python" / "openapi_mcp_codegen"
        config_file = temp_dir / "config.yaml"
        config_file.write_text("version: 1.0.0")
        
        generator = MCPGenerator(
            script_dir=str(script_dir),
            spec_path=str(spec_file),
            output_dir=str(temp_dir),
            config_path=str(config_file)
        )
        
        assert generator.spec["openapi"] == "3.0.0"
        assert generator.spec["info"]["title"] == "Test API"

    @pytest.mark.mcp
    def test_spec_loading_json(self, temp_dir, mock_openapi_spec):
        """Test loading OpenAPI spec from JSON file."""
        spec_file = temp_dir / "test.json"
        with open(spec_file, 'w') as f:
            json.dump(mock_openapi_spec, f)
        
        script_dir = Path(__file__).parent.parent.parent.parent / "core" / "generators" / "python" / "openapi_mcp_codegen"
        config_file = temp_dir / "config.yaml"
        config_file.write_text("version: 1.0.0")
        
        generator = MCPGenerator(
            script_dir=str(script_dir),
            spec_path=str(spec_file),
            output_dir=str(temp_dir),
            config_path=str(config_file)
        )
        
        assert generator.spec["openapi"] == "3.0.0"
        assert generator.spec["info"]["title"] == "Test API"

    @pytest.mark.mcp
    def test_python_type_mapping(self, temp_dir, sample_spec_file, sample_config_file):
        """Test OpenAPI to Python type mapping."""
        script_dir = Path(__file__).parent.parent.parent.parent / "core" / "generators" / "python" / "openapi_mcp_codegen"
        
        generator = MCPGenerator(
            script_dir=str(script_dir),
            spec_path=str(sample_spec_file),
            output_dir=str(temp_dir),
            config_path=str(sample_config_file)
        )
        
        # Test basic type mappings
        assert generator._get_python_type({"type": "string"}) == "str"
        assert generator._get_python_type({"type": "integer"}) == "int"
        assert generator._get_python_type({"type": "number"}) == "float"
        assert generator._get_python_type({"type": "boolean"}) == "bool"
        assert generator._get_python_type({"type": "object"}) == "Dict[str, Any]"
        
        # Test array types
        array_type = generator._get_python_type({
            "type": "array",
            "items": {"type": "string"}
        })
        assert array_type == "List[str]"
        
        # Test enum types
        enum_type = generator._get_python_type({
            "type": "string",
            "enum": ["active", "inactive", "pending"]
        })
        assert "Literal" in enum_type
        assert "active" in enum_type

    @pytest.mark.mcp
    @patch('subprocess.run')
    def test_ruff_linting(self, mock_subprocess, temp_dir, sample_spec_file, sample_config_file):
        """Test Ruff linting integration."""
        mock_subprocess.return_value = Mock(returncode=0)
        
        script_dir = Path(__file__).parent.parent.parent.parent / "core" / "generators" / "python" / "openapi_mcp_codegen"
        generator = MCPGenerator(
            script_dir=str(script_dir),
            spec_path=str(sample_spec_file),
            output_dir=str(temp_dir),
            config_path=str(sample_config_file)
        )
        
        test_file = temp_dir / "test.py"
        test_file.write_text("print('hello world')")
        
        generator.run_ruff_lint(str(test_file))
        
        # Verify ruff format and check were called
        assert mock_subprocess.call_count == 2
        format_call = mock_subprocess.call_args_list[0]
        check_call = mock_subprocess.call_args_list[1]
        
        assert "ruff" in format_call[0][0]
        assert "format" in format_call[0][0]
        assert "ruff" in check_call[0][0]
        assert "check" in check_call[0][0]

    @pytest.mark.mcp
    def test_file_header_generation(self, temp_dir, sample_spec_file):
        """Test file header generation from config."""
        config_data = {
            "version": "1.0.0",
            "file_headers": {
                "copyright": "Test Copyright 2024",
                "license": "MIT",
                "message": "Generated by test"
            }
        }
        
        config_file = temp_dir / "config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        script_dir = Path(__file__).parent.parent.parent.parent / "core" / "generators" / "python" / "openapi_mcp_codegen"
        generator = MCPGenerator(
            script_dir=str(script_dir),
            spec_path=str(sample_spec_file),
            output_dir=str(temp_dir),
            config_path=str(config_file)
        )
        
        headers = generator.get_file_header_kwargs()
        
        assert headers["file_headers"] is True
        assert headers["file_headers_copyright"] == "Test Copyright 2024"
        assert headers["file_headers_license"] == "MIT"
        assert headers["file_headers_message"] == "Generated by test"

    @pytest.mark.mcp
    @patch('subprocess.run')
    def test_model_generation(self, mock_subprocess, temp_dir, sample_spec_file, sample_config_file):
        """Test model file generation from OpenAPI schemas."""
        mock_subprocess.return_value = Mock(returncode=0)
        
        script_dir = Path(__file__).parent.parent.parent.parent / "core" / "generators" / "python" / "openapi_mcp_codegen"
        generator = MCPGenerator(
            script_dir=str(script_dir),
            spec_path=str(sample_spec_file),
            output_dir=str(temp_dir),
            config_path=str(sample_config_file)
        )
        
        # Mock template rendering
        with patch.object(generator, 'render_template') as mock_render:
            generator.generate_models()
            
            # Verify that model generation was called
            assert mock_render.called
            call_args = mock_render.call_args_list
            
            # Should generate User model
            user_model_call = any("user.py" in str(call) for call in call_args)
            assert user_model_call

    @pytest.mark.mcp
    @patch('subprocess.run')
    def test_api_client_generation(self, mock_subprocess, temp_dir, sample_spec_file, sample_config_file):
        """Test API client generation."""
        mock_subprocess.return_value = Mock(returncode=0)
        
        script_dir = Path(__file__).parent.parent.parent.parent / "core" / "generators" / "python" / "openapi_mcp_codegen"
        generator = MCPGenerator(
            script_dir=str(script_dir),
            spec_path=str(sample_spec_file),
            output_dir=str(temp_dir),
            config_path=str(sample_config_file)
        )
        
        with patch.object(generator, 'render_template') as mock_render:
            generator.generate_api_client()
            
            # Verify API client generation
            assert mock_render.called
            call_args = mock_render.call_args_list
            
            # Should generate client.py
            client_call = any("client.py" in str(call) for call in call_args)
            assert client_call

    @pytest.mark.mcp
    @patch('subprocess.run')
    def test_tool_modules_generation(self, mock_subprocess, temp_dir, sample_spec_file, sample_config_file):
        """Test tool modules generation from OpenAPI paths."""
        mock_subprocess.return_value = Mock(returncode=0)
        
        script_dir = Path(__file__).parent.parent.parent.parent / "core" / "generators" / "python" / "openapi_mcp_codegen"
        generator = MCPGenerator(
            script_dir=str(script_dir),
            spec_path=str(sample_spec_file),
            output_dir=str(temp_dir),
            config_path=str(sample_config_file)
        )
        
        with patch.object(generator, 'render_template') as mock_render:
            generator.generate_tool_modules()
            
            # Verify tool generation
            assert mock_render.called
            call_args = mock_render.call_args_list
            
            # Should generate tools for users endpoint
            users_tool_call = any("users.py" in str(call) for call in call_args)
            assert users_tool_call

    @pytest.mark.mcp
    @patch('subprocess.run')
    def test_server_generation(self, mock_subprocess, temp_dir, sample_spec_file, sample_config_file):
        """Test MCP server generation."""
        mock_subprocess.return_value = Mock(returncode=0)
        
        script_dir = Path(__file__).parent.parent.parent.parent / "core" / "generators" / "python" / "openapi_mcp_codegen"
        generator = MCPGenerator(
            script_dir=str(script_dir),
            spec_path=str(sample_spec_file),
            output_dir=str(temp_dir),
            config_path=str(sample_config_file)
        )
        
        # Generate tools first to populate tools_map
        with patch.object(generator, 'render_template'):
            generator.generate_tool_modules()
        
        with patch.object(generator, 'render_template') as mock_render:
            generator.generate_server()
            
            # Verify server generation
            assert mock_render.called
            call_args = mock_render.call_args_list
            
            # Should generate server.py
            server_call = any("server.py" in str(call) for call in call_args)
            assert server_call

    @pytest.mark.mcp
    @pytest.mark.slow
    @patch('subprocess.run')
    def test_complete_generation_pipeline(self, mock_subprocess, temp_dir, sample_spec_file, sample_config_file):
        """Test complete MCP generation pipeline."""
        mock_subprocess.return_value = Mock(returncode=0)
        
        script_dir = Path(__file__).parent.parent.parent.parent / "core" / "generators" / "python" / "openapi_mcp_codegen"
        generator = MCPGenerator(
            script_dir=str(script_dir),
            spec_path=str(sample_spec_file),
            output_dir=str(temp_dir),
            config_path=str(sample_config_file)
        )
        
        with patch.object(generator, 'render_template') as mock_render:
            generator.generate()
            
            # Verify all components were generated
            assert mock_render.call_count > 0
            
            # Verify key files were generated
            call_args_str = str(mock_render.call_args_list)
            assert "client.py" in call_args_str
            assert "server.py" in call_args_str
            assert "__init__.py" in call_args_str

    @pytest.mark.mcp
    def test_ref_resolution(self, temp_dir, sample_config_file):
        """Test $ref resolution in OpenAPI specs."""
        # Create spec with references
        spec_with_refs = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {
                "/test": {
                    "get": {
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/TestModel"}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "TestModel": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "value": {"type": "integer"}
                        }
                    }
                }
            }
        }
        
        spec_file = temp_dir / "spec_with_refs.yaml"
        with open(spec_file, 'w') as f:
            yaml.dump(spec_with_refs, f)
        
        script_dir = Path(__file__).parent.parent.parent.parent / "core" / "generators" / "python" / "openapi_mcp_codegen"
        generator = MCPGenerator(
            script_dir=str(script_dir),
            spec_path=str(spec_file),
            output_dir=str(temp_dir),
            config_path=str(sample_config_file)
        )
        
        # Test reference resolution
        resolved = generator._resolve_ref("#/components/schemas/TestModel")
        assert resolved["type"] == "object"
        assert "name" in resolved["properties"]

    @pytest.mark.mcp
    @pytest.mark.performance
    def test_large_spec_performance(self, temp_dir, sample_config_file, performance_test_data):
        """Test performance with large OpenAPI specifications."""
        # Create a large spec with many paths and schemas
        large_spec = {
            "openapi": "3.0.0",
            "info": {"title": "Large API", "version": "1.0.0"},
            "paths": {},
            "components": {"schemas": {}}
        }
        
        # Generate 100 paths and schemas
        for i in range(100):
            path_name = f"/resource{i}"
            schema_name = f"Resource{i}"
            
            large_spec["paths"][path_name] = {
                "get": {
                    "operationId": f"getResource{i}",
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": f"#/components/schemas/{schema_name}"}
                                }
                            }
                        }
                    }
                }
            }
            
            large_spec["components"]["schemas"][schema_name] = {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "value": {"type": "integer"}
                }
            }
        
        spec_file = temp_dir / "large_spec.yaml"
        with open(spec_file, 'w') as f:
            yaml.dump(large_spec, f)
        
        script_dir = Path(__file__).parent.parent.parent.parent / "core" / "generators" / "python" / "openapi_mcp_codegen"
        
        # Measure initialization time
        import time
        start_time = time.time()
        
        generator = MCPGenerator(
            script_dir=str(script_dir),
            spec_path=str(spec_file),
            output_dir=str(temp_dir),
            config_path=str(sample_config_file)
        )
        
        initialization_time = time.time() - start_time
        
        # Should initialize within reasonable time (< 5 seconds)
        assert initialization_time < 5.0
        
        # Verify all paths were loaded
        assert len(generator.spec["paths"]) == 100
        assert len(generator.spec["components"]["schemas"]) == 100

    @pytest.mark.mcp
    def test_error_handling_invalid_spec(self, temp_dir, sample_config_file):
        """Test error handling with invalid OpenAPI spec."""
        # Create invalid spec file
        invalid_spec = temp_dir / "invalid_spec.yaml"
        invalid_spec.write_text("invalid: yaml: content: [")
        
        script_dir = Path(__file__).parent.parent.parent.parent / "core" / "generators" / "python" / "openapi_mcp_codegen"
        
        with pytest.raises(Exception):
            MCPGenerator(
                script_dir=str(script_dir),
                spec_path=str(invalid_spec),
                output_dir=str(temp_dir),
                config_path=str(sample_config_file)
            )

    @pytest.mark.mcp
    def test_error_handling_missing_config(self, temp_dir, sample_spec_file):
        """Test error handling with missing config file."""
        script_dir = Path(__file__).parent.parent.parent.parent / "core" / "generators" / "python" / "openapi_mcp_codegen"
        missing_config = temp_dir / "missing_config.yaml"
        
        with pytest.raises(FileNotFoundError):
            MCPGenerator(
                script_dir=str(script_dir),
                spec_path=str(sample_spec_file),
                output_dir=str(temp_dir),
                config_path=str(missing_config)
            )

    @pytest.mark.mcp
    def test_dry_run_mode(self, temp_dir, sample_spec_file, sample_config_file):
        """Test dry run mode functionality."""
        script_dir = Path(__file__).parent.parent.parent.parent / "core" / "generators" / "python" / "openapi_mcp_codegen"
        
        generator = MCPGenerator(
            script_dir=str(script_dir),
            spec_path=str(sample_spec_file),
            output_dir=str(temp_dir),
            config_path=str(sample_config_file),
            dry_run=True
        )
        
        assert generator.dry_run is True
        
        # In dry run mode, files should not be created
        with patch.object(generator, 'render_template') as mock_render:
            # Mock render_template to track calls but not create files
            mock_render.return_value = None
            
            # This should work without actually creating files
            generator.generate_api_client()
            assert mock_render.called