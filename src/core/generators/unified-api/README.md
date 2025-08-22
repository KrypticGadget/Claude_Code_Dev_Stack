# Unified MCP Generator

A unified API layer that seamlessly integrates both Python and Node.js MCP (Model Context Protocol) generators, providing a single interface for OpenAPI to MCP conversion with intelligent generator selection and comprehensive configuration management.

## Features

### 🔧 **Unified Interface**
- Single API for both Python and Node.js MCP generators
- Automatic generator selection based on environment and requirements
- Consistent configuration schema across all generators

### 🎯 **Intelligent Selection**
- Environment-aware generator recommendation
- Project type compatibility checking
- Feature-based generator scoring
- Fallback options and warnings

### 📋 **Comprehensive Configuration**
- JSON/YAML configuration files
- Generator-specific options
- Transport type selection
- Validation and error handling

### 🔄 **Multiple Interfaces**
- Command-line interface with rich output
- Interactive setup wizard
- Programmatic API for integration
- Quick setup templates

### 🛡️ **Robust Validation**
- OpenAPI specification validation
- Configuration schema validation
- Environment requirements checking
- Pre-generation validation hooks

## Installation

```bash
npm install @claude-code/unified-mcp-generator
```

## Quick Start

### Command Line Interface

```bash
# Interactive wizard (recommended for first use)
unified-mcp-generator wizard

# Quick generation with auto-selection
unified-mcp-generator generate -i ./openapi.yaml -o ./my-mcp-server

# Generate with specific options
unified-mcp-generator generate \
  -i ./openapi.yaml \
  -o ./my-mcp-server \
  -g python \
  -p mcp-agent \
  --force
```

### Programmatic API

```typescript
import { generateMCPProject, UnifiedMCPGenerator } from '@claude-code/unified-mcp-generator';

// Quick generation
const result = await generateMCPProject({
  specPath: './openapi.yaml',
  outputDir: './my-mcp-server',
  config: {
    generator: 'auto',
    projectType: 'mcp-server',
    common: {
      name: 'my-api-server',
      transport: 'stdio'
    }
  },
  onProgress: (status) => {
    console.log(`${status.progress}% - ${status.operation}`);
  }
});

// Advanced usage with custom configuration
const generator = await UnifiedMCPGenerator.fromOptions({
  input: './openapi.yaml',
  output: './output',
  config: './config.yaml'
});

const validation = generator.validateConfiguration();
if (validation.valid) {
  const result = await generator.generate();
}
```

## Configuration

### Configuration File (YAML)

```yaml
# unified-mcp.config.yaml
generator: auto  # python | nodejs | auto
projectType: mcp-server  # mcp-server | mcp-agent | mcp-client | full-stack

common:
  name: my-mcp-server
  description: Generated MCP server
  version: 1.0.0
  author:
    name: Your Name
    email: your.email@example.com
  license: MIT
  transport: stdio  # stdio | web | streamable-http | websocket
  port: 3000  # for web transports
  baseUrl: https://api.example.com

python:
  pythonVersion: ">=3.11"
  enhanceDocstrings: true
  enhanceDocstringsOpenAPI: true
  generateAgent: true
  generateEval: true
  generateSystemPrompt: true
  withA2AProxy: false
  fileHeaders:
    copyright: "Copyright 2024"
    license: MIT

nodejs:
  nodeVersion: ">=18.0.0"
  packageManager: npm  # npm | yarn | pnpm
  typescript: true
  eslint: true
  prettier: true
  jest: true

validation:
  validateSpec: true
  validateOutput: false
  strict: false

hooks:
  preGenerate:
    - echo "Starting generation..."
  postGenerate:
    - npm install
  postInstall:
    - npm run build
```

### JSON Configuration

```json
{
  "generator": "auto",
  "projectType": "mcp-server",
  "common": {
    "name": "my-mcp-server",
    "transport": "stdio"
  }
}
```

## CLI Commands

### Generation Commands

```bash
# Main generation command
unified-mcp-generator generate -i <spec> -o <output> [options]

# Interactive wizard
unified-mcp-generator wizard
unified-mcp-generator wizard --quick  # Quick templates

# Initialize configuration
unified-mcp-generator init -g python -p mcp-agent
```

### Validation Commands

```bash
# Validate OpenAPI spec and configuration
unified-mcp-generator validate -i ./openapi.yaml -c ./config.yaml

# Validate configuration only
unified-mcp-generator config validate -c ./config.yaml
```

### Information Commands

```bash
# List available generators and capabilities
unified-mcp-generator list

# Show environment analysis
unified-mcp-generator env

# Show configuration
unified-mcp-generator config show -c ./config.yaml
```

### Configuration Management

```bash
# Generate sample configuration
unified-mcp-generator config sample -g python -o ./config.yaml

# Initialize new project
unified-mcp-generator init --generator nodejs --project-type mcp-server
```

## Generator Selection

The unified API automatically selects the best generator based on:

### Environment Analysis
- **Runtime Availability**: Node.js vs Python availability and versions
- **Package Managers**: npm, yarn, pnpm, pip, poetry availability
- **Development Tools**: Git, build tools, etc.

### Project Requirements
- **Project Type**: MCP Agent (Python preferred), MCP Server (both), etc.
- **Transport Type**: WebSocket (Python preferred), StreamableHTTP (Node.js only)
- **Features**: LLM integration, TypeScript support, etc.

### Scoring Algorithm
```
Score = Environment(30) + ProjectType(25) + Transport(15) + Features(20) + Version(10)
```

## Project Types

### MCP Server
Basic MCP server implementation with tools generated from OpenAPI operations.

**Supported by**: Python ✅, Node.js ✅

```bash
unified-mcp-generator generate -i api.yaml -o server -p mcp-server
```

### MCP Agent
AI agent that uses MCP tools, built with LangGraph (Python) or similar frameworks.

**Supported by**: Python ✅ (recommended), Node.js ⚠️ (limited)

```bash
unified-mcp-generator generate -i api.yaml -o agent -p mcp-agent -g python
```

### MCP Client
Client library for connecting to MCP servers.

**Supported by**: Python ✅, Node.js ✅

```bash
unified-mcp-generator generate -i api.yaml -o client -p mcp-client
```

### Full Stack
Complete project with server, client, and documentation.

**Supported by**: Python ✅, Node.js ✅

```bash
unified-mcp-generator generate -i api.yaml -o fullstack -p full-stack
```

## Transport Types

### stdio (Standard I/O)
Default transport for MCP servers, uses stdin/stdout communication.

**Best for**: CLI tools, agent integration, production deployments
**Supported by**: Python ✅, Node.js ✅

### web (HTTP Web Server)
HTTP server with optional web interface for testing.

**Best for**: Development, testing, web integration
**Supported by**: Python ✅, Node.js ✅

### streamable-http (Streaming HTTP)
HTTP server with streaming support for real-time communication.

**Best for**: Real-time applications, streaming data
**Supported by**: Python ⚠️, Node.js ✅

### websocket (WebSocket)
WebSocket-based transport for bidirectional communication.

**Best for**: Real-time bidirectional communication
**Supported by**: Python ✅, Node.js ⚠️

## Environment Requirements

### Python Generator
- **Python**: 3.11+ (recommended), 3.9+ (minimum)
- **Package Manager**: pip, poetry (optional)
- **Additional**: For agents - LangChain, LangGraph dependencies

### Node.js Generator
- **Node.js**: 18.0+ (recommended), 16.0+ (minimum)
- **Package Manager**: npm (required), yarn/pnpm (optional)
- **Additional**: TypeScript support included

### System Requirements
- **Git**: Recommended for version control features
- **Disk Space**: 50MB+ for generated projects
- **Network**: For OpenAPI spec URLs and dependency installation

## Advanced Usage

### Custom Templates

You can create custom templates by extending the base configurations:

```typescript
import { configHelpers } from '@claude-code/unified-mcp-generator';

const customConfig = configHelpers.mergeConfigs(
  configHelpers.createMinimalConfig('python', 'mcp-server'),
  {
    python: {
      enhanceDocstrings: true,
      generateAgent: true
    },
    common: {
      transport: 'web',
      port: 8080
    }
  }
);
```

### Progress Monitoring

```typescript
const result = await generateMCPProject({
  specPath: './api.yaml',
  outputDir: './output',
  onProgress: (status) => {
    console.log(`Phase: ${status.phase}`);
    console.log(`Progress: ${status.progress}%`);
    console.log(`Operation: ${status.operation}`);
    console.log(`Files: ${status.filesProcessed}/${status.totalFiles}`);
  }
});
```

### Error Handling

```typescript
try {
  const result = await generateMCPProject({
    specPath: './api.yaml',
    outputDir: './output'
  });
  
  if (!result.success) {
    console.error('Generation failed:');
    result.errors.forEach(error => {
      console.error(`- ${error.message} (${error.code})`);
    });
  }
  
  if (result.warnings.length > 0) {
    console.warn('Warnings:');
    result.warnings.forEach(warning => {
      console.warn(`- ${warning.message}`);
    });
  }
  
} catch (error) {
  console.error('Fatal error:', error.message);
}
```

### Validation Before Generation

```typescript
import { validateMCPProject } from '@claude-code/unified-mcp-generator';

const validation = await validateMCPProject({
  specPath: './api.yaml',
  config: myConfig,
  strict: true
});

if (!validation.overall.valid) {
  console.error('Validation failed!');
  console.error('Config errors:', validation.configValidation.errors);
  console.error('Spec errors:', validation.specValidation.errors);
} else {
  // Proceed with generation
}
```

## Migration Guide

### From Python Generator

If you're currently using the Python generator directly:

```bash
# Old way
python -m openapi_mcp_codegen --spec-path api.yaml --output-dir output

# New way
unified-mcp-generator generate -i api.yaml -o output -g python
```

### From Node.js Generator

If you're currently using the Node.js generator directly:

```bash
# Old way
openapi-mcp-generator -i api.yaml -o output

# New way
unified-mcp-generator generate -i api.yaml -o output -g nodejs
```

### Configuration Migration

The unified API accepts generator-specific configurations:

```yaml
# For existing Python projects
generator: python
python:
  # Your existing Python generator config
  enhanceDocstrings: true
  generateAgent: true

# For existing Node.js projects  
generator: nodejs
nodejs:
  # Your existing Node.js generator config
  typescript: true
  packageManager: npm
```

## Troubleshooting

### Common Issues

#### Generator Not Found
```
Error: Python generator not found
```
**Solution**: Install Python 3.11+ and pip, or use `--generator nodejs`

#### Permission Denied
```
Error: No write permission in current directory
```
**Solution**: Run with appropriate permissions or change output directory

#### OpenAPI Validation Failed
```
Error: OpenAPI validation failed: Invalid path parameter
```
**Solution**: Fix your OpenAPI specification or use `--skip-validation`

### Environment Issues

Check your environment:
```bash
unified-mcp-generator env
```

Validate your setup:
```bash
unified-mcp-generator list
```

### Debug Mode

Enable verbose output for debugging:
```bash
unified-mcp-generator generate -i api.yaml -o output --verbose
```

### Getting Help

```bash
# General help
unified-mcp-generator --help

# Command-specific help
unified-mcp-generator generate --help
unified-mcp-generator wizard --help
```

## Examples

### Basic MCP Server (Auto-select generator)
```bash
unified-mcp-generator generate \
  -i https://petstore.swagger.io/v2/swagger.json \
  -o ./petstore-mcp
```

### Python MCP Agent with LLM Features
```bash
unified-mcp-generator generate \
  -i ./api.yaml \
  -o ./my-agent \
  -g python \
  -p mcp-agent \
  -c ./agent-config.yaml
```

### Node.js Web Server with TypeScript
```bash
unified-mcp-generator generate \
  -i ./api.yaml \
  -o ./web-server \
  -g nodejs \
  --config '{"common":{"transport":"web","port":8080},"nodejs":{"typescript":true}}'
```

### Interactive Setup
```bash
# Full interactive wizard
unified-mcp-generator wizard

# Quick template selection
unified-mcp-generator wizard --quick
```

## Contributing

This unified API is part of the Claude Code Dev Stack. Contributions are welcome!

### Development Setup

```bash
git clone <repository>
cd unified-api
npm install
npm run build
npm test
```

### Generator Integration

To integrate a new generator:

1. Create an adapter class implementing the `GeneratorAdapter` interface
2. Add generator capabilities to `selector.ts`
3. Update the CLI commands and validation schemas
4. Add tests and documentation

## License

MIT License - see LICENSE file for details.

## Related Projects

- [Python MCP Generator](../python/) - The underlying Python generator
- [Node.js MCP Generator](../nodejs/) - The underlying Node.js generator
- [Claude Code Dev Stack](../../) - The complete development stack

## Support

- 📖 [Documentation](./docs/)
- 🐛 [Issues](https://github.com/claude-code/unified-mcp-generator/issues)
- 💬 [Discussions](https://github.com/claude-code/unified-mcp-generator/discussions)
- 📧 [Support Email](mailto:support@claude-code.dev)