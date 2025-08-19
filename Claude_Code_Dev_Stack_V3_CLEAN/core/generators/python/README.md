# Python MCP Generator

This directory contains the Python MCP (Model Control Protocol) generator components extracted from the openapi-mcp-codegen repository.

## Structure

```
core/generators/python/
├── openapi_mcp_codegen/           # Main generator package
│   ├── __init__.py               # Package initialization (empty)
│   ├── __main__.py               # CLI interface
│   ├── mcp_codegen.py           # Main generator logic
│   └── templates/               # Jinja2 templates (24 files)
│       ├── agent/               # Agent-related templates
│       │   ├── a2a_server/      # A2A server templates
│       │   └── ws_proxy/        # WebSocket proxy templates
│       ├── api/                 # API client templates
│       ├── models/              # Data model templates
│       └── tools/               # Tool generation templates
└── pyproject.toml               # Project dependencies and configuration
```

## Key Components

### 1. Main Generator Logic (`mcp_codegen.py`)
- **MCPGenerator class**: Core functionality for generating MCP servers from OpenAPI specs
- **Features**:
  - Jinja2 template rendering
  - OpenAPI specification parsing (YAML/JSON)
  - Python type mapping
  - Code formatting with Ruff
  - LLM-enhanced docstring generation
  - Microservice architecture generation

### 2. CLI Interface (`__main__.py`)
- **Click-based command-line interface**
- **Options**:
  - `--spec-file`: OpenAPI specification file path
  - `--output-dir`: Generated code output directory
  - `--generate-agent`: Create LangGraph React-agent wrapper
  - `--generate-eval`: Generate evaluation modules
  - `--enhance-docstring-with-llm`: LLM-enhanced documentation

### 3. Template System (24 Jinja2 templates)
- **Agent templates**: LangGraph agent wrappers with A2A/WebSocket proxy support
- **API templates**: HTTP client generation
- **Model templates**: Pydantic model generation from OpenAPI schemas
- **Tool templates**: MCP tool function generation
- **Server templates**: MCP server scaffolding

## Dependencies

Key dependencies from `pyproject.toml`:
- **Jinja2**: Template engine
- **Click**: CLI framework
- **PyYAML**: YAML parsing
- **Ruff**: Code formatting
- **LangChain**: LLM integration
- **FastAPI**: Web framework
- **Pydantic**: Data validation
- **HttpX**: HTTP client

## Usage

The generator can be used to create MCP servers from OpenAPI specifications using Jinja2 templates. It supports:

1. **Basic MCP Server Generation**: Core server, models, and tools
2. **Agent Wrapper Generation**: LangGraph agents that use the MCP server
3. **Evaluation System**: Testing and evaluation frameworks
4. **Multiple Protocol Bindings**: A2A and WebSocket proxy support

## Integration Points

This Python generator integrates with:
- **OpenAPI specifications**: Input source for code generation
- **LangChain ecosystem**: For agent and LLM functionality
- **MCP protocol**: For tool and server interfaces
- **FastAPI**: For HTTP API endpoints
- **A2A/WebSocket**: For protocol binding flexibility

## Template Categories

1. **Agent Templates**: React-style agents with tool calling capabilities
2. **API Templates**: HTTP client wrappers for external APIs
3. **Model Templates**: Pydantic models from OpenAPI schemas
4. **Tool Templates**: MCP tool function implementations
5. **Server Templates**: MCP server boilerplate and configuration