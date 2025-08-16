# API Generator Service

A unified OpenAPI to MCP (Model Context Protocol) conversion service that integrates both Python and Node.js generators with a web interface for validation, generation, and deployment.

## Overview

The API Generator Service combines:
- **@cnoe-io/openapi-mcp-codegen** - Python FastAPI-based MCP server generator
- **@harsha-iiiv/openapi-mcp-generator** - Node.js Express-based MCP server generator

## Features

### 🔍 OpenAPI Validation
- Full OpenAPI 3.x specification validation
- Error and warning reporting
- Specification statistics and analysis
- Support for JSON and YAML formats

### 🔄 Dual Generator Support
- **Python Generator**: FastAPI-based servers with automatic documentation
- **Node.js Generator**: Express/TypeScript servers with Swagger UI
- **Unified Interface**: Single web interface for both generators

### 🚀 Deployment & Management
- Automatic MCP server deployment
- Real-time generation status
- Downloadable server packages
- Integration with MCP Manager

### 🎯 Web Interface
- **Upload & Validate**: Drag-and-drop or paste OpenAPI specs
- **Generate MCP**: Choose generators and customize options
- **Deploy Servers**: One-click deployment to local environment

## Quick Start

### 1. Setup
```bash
# Navigate to backend directory
cd apps/backend

# Install dependencies
npm install

# Setup generators (installs Python and Node.js packages)
node setup-api-generator.js
```

### 2. Start Service
```bash
# Start API Generator service
npm start
# or
node start-api-generator.js
```

### 3. Access Web Interface
- Open http://localhost:3000/api-generator in your browser
- The service runs on port 8082 by default

## API Endpoints

### Validation
```http
POST /validate
Content-Type: application/json

{
  "spec": { /* OpenAPI specification */ }
}
```

### Python Generation
```http
POST /generate/python
Content-Type: application/json

{
  "spec": { /* OpenAPI specification */ },
  "options": {
    "serverName": "my-api",
    "generateTests": true,
    "includeDocumentation": true
  }
}
```

### Node.js Generation
```http
POST /generate/nodejs
Content-Type: application/json

{
  "spec": { /* OpenAPI specification */ },
  "options": {
    "serverName": "my-api",
    "generateTests": true,
    "includeDocumentation": true
  }
}
```

### Deployment
```http
POST /deploy
Content-Type: application/json

{
  "generator": "python",
  "mcpServer": { /* MCP server config */ },
  "autoStart": true
}
```

### Health Check
```http
GET /health
```

## Configuration

### Environment Variables
```bash
API_GENERATOR_PORT=8082           # Service port
API_GENERATOR_URL=http://localhost:8082  # Base URL for frontend
```

### Generator Options

#### Python Generator (@cnoe-io/openapi-mcp-codegen)
- **Runtime**: Python 3.7+
- **Framework**: FastAPI
- **Features**: Async support, automatic validation, CORS
- **Output**: Production-ready FastAPI application

#### Node.js Generator (@harsha-iiiv/openapi-mcp-generator)
- **Runtime**: Node.js 16+
- **Framework**: Express + TypeScript
- **Features**: Swagger UI, CORS, type safety
- **Output**: TypeScript Express application

## Directory Structure
```
apps/backend/
├── api-generator.js              # Main service
├── setup-api-generator.js        # Setup script
├── start-api-generator.js        # Launcher
├── api-generator-package.json    # Dependencies
├── temp/                         # Temporary files
├── generated/                    # Generated servers
└── generators/
    ├── python/                   # Python generator config
    └── nodejs/                   # Node.js generator config
```

## Web Interface Usage

### Upload & Validate Tab
1. **Upload File**: Drag and drop OpenAPI JSON/YAML file
2. **Paste Spec**: Copy and paste OpenAPI specification
3. **Validation**: Automatic validation with detailed feedback
4. **Statistics**: View paths, operations, and schemas count

### Generate MCP Tab
1. **Select Generator**: Choose Python, Node.js, or both
2. **Configure Options**: Set server name and features
3. **Generate**: Create MCP servers from OpenAPI spec
4. **Download**: Get generated code as ZIP packages

### Deploy Servers Tab
1. **Review Generated**: See list of generated MCP servers
2. **Deploy**: One-click deployment to local environment
3. **Monitor**: Integration with MCP Manager for status

## Integration with MCP Manager

The API Generator integrates seamlessly with the existing MCP Manager:

1. **Service Discovery**: Generated servers auto-register with MCP Manager
2. **Health Monitoring**: Real-time health checks and metrics
3. **Lifecycle Management**: Start, stop, restart generated servers
4. **Unified Dashboard**: Single interface for all MCP services

## Troubleshooting

### Common Issues

#### Python Generator Not Working
```bash
# Check Python installation
python3 --version

# Install Python generator
pip install openapi-mcp-codegen

# Test installation
openapi-mcp-codegen --version
```

#### Node.js Generator Not Working
```bash
# Check Node.js installation
node --version

# Install Node.js generator
npm install -g @harsha-iiiv/openapi-mcp-generator

# Test installation
npx @harsha-iiiv/openapi-mcp-generator --version
```

#### Service Won't Start
```bash
# Check if port is available
netstat -an | grep 8082

# Start with debug logging
DEBUG=* node api-generator.js

# Check dependencies
npm install
```

### Logs and Debugging

- Service logs: Console output when running
- Generation logs: Temporary files in `temp/` directory
- Deployment logs: Manifest files in `generated/` directory

## Development

### Adding New Generators
1. Create generator configuration in `generators/` directory
2. Implement generation logic in `api-generator.js`
3. Add UI options in `APIGenerator.tsx`
4. Update setup script

### Testing
```bash
# Run tests
npm test

# Test with sample OpenAPI spec
curl -X POST http://localhost:8082/validate \
  -H "Content-Type: application/json" \
  -d @sample-openapi.json
```

## Contributing

The API Generator Service integrates community projects:

- **@cnoe-io/openapi-mcp-codegen**: Python generator
- **@harsha-iiiv/openapi-mcp-generator**: Node.js generator

Please contribute improvements back to the respective projects.

## License

- API Generator Service: AGPL-3.0
- Individual generators: See respective project licenses

## Support

For issues and support:
1. Check troubleshooting section above
2. Review generator project documentation
3. File issues in respective project repositories