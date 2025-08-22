# Claude Code Session Management API

A comprehensive session management system for Claude Code path-based instances, providing complete session lifecycle management, real-time monitoring, and agent coordination.

## Overview

The Session Management API provides a robust foundation for managing Claude Code sessions with features including:

- **Complete Session Lifecycle**: Create, configure, navigate, clone, import/export, and terminate sessions
- **Advanced Path Validation**: Cross-platform path validation with security checks and permission verification
- **Agent Management**: Initialize, configure, and coordinate Claude Code agents within sessions
- **Real-time Monitoring**: Performance metrics, resource usage tracking, and session health monitoring
- **RESTful API**: Comprehensive REST endpoints with WebSocket support for real-time updates
- **Session Analytics**: Detailed analytics and reporting on session usage and performance

## Architecture

```
session-manager/
├── api/                    # REST API endpoints
│   ├── session_api.py     # Main API server with all endpoints
│   └── __init__.py
├── core/                   # Core session management
│   ├── session_manager.py # Session lifecycle and persistence
│   └── __init__.py
├── services/              # Supporting services
│   ├── path_validator.py  # Path validation and security
│   ├── agent_initializer.py # Agent management and coordination
│   ├── session_monitor.py # Real-time monitoring and metrics
│   └── __init__.py
├── models/                # Data models and schemas
│   ├── session_models.py  # Session, agent, and request models
│   └── __init__.py
├── examples/              # Usage examples and demos
│   ├── api_client_example.py # Complete API usage demo
│   └── __init__.py
├── server.py              # Main server entry point
├── start_session_api.py   # Quick start script
├── simple_test.py         # Basic functionality test
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Quick Start

### 1. Install Dependencies

```bash
cd integrations/session-manager
pip install -r requirements.txt
```

### 2. Start the Server

```bash
python start_session_api.py
```

The server will start on `http://localhost:8082` by default.

### 3. Verify Installation

```bash
python simple_test.py
```

## API Endpoints

### Session Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/claude/sessions` | Create new session |
| GET | `/api/claude/sessions` | List sessions with filtering |
| GET | `/api/claude/sessions/{id}` | Get session details |
| PUT | `/api/claude/sessions/{id}` | Update session configuration |
| DELETE | `/api/claude/sessions/{id}` | Terminate session |

### Session Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/claude/sessions/{id}/navigate` | Navigate to new path |
| POST | `/api/claude/sessions/{id}/clone` | Clone existing session |
| POST | `/api/claude/sessions/{id}/export` | Export session data |
| POST | `/api/claude/sessions/import` | Import session data |

### Agent Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/claude/sessions/{id}/agents` | Get session agents |
| POST | `/api/claude/sessions/{id}/agents/{name}/activate` | Activate agent |
| POST | `/api/claude/sessions/{id}/agents/{name}/deactivate` | Deactivate agent |
| POST | `/api/claude/sessions/{id}/agents/{name}/restart` | Restart agent |

### Monitoring & Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/claude/sessions/{id}/metrics` | Get session metrics |
| GET | `/api/claude/sessions/{id}/status` | Get session status |
| GET | `/api/claude/analytics` | Get system analytics |

### Utilities

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/claude/validate-path` | Validate single path |
| POST | `/api/claude/validate-paths` | Validate multiple paths |
| GET | `/api/claude/agent-types` | Get available agent types |
| GET | `/api/claude/system-status` | Get system status |
| GET | `/health` | Health check |

### WebSocket

- `ws://localhost:8082/ws/sessions` - Real-time session updates and alerts

## Usage Examples

### Creating a Session

```python
import aiohttp
import asyncio

async def create_session():
    async with aiohttp.ClientSession() as session:
        data = {
            'name': 'My Project Session',
            'working_directory': '/path/to/project',
            'description': 'Development session for my project',
            'agents': [
                {
                    'agent_type': 'BACKEND',
                    'name': 'backend-services',
                    'enabled': True,
                    'priority': 2
                }
            ]
        }
        
        async with session.post('http://localhost:8082/api/claude/sessions', json=data) as resp:
            result = await resp.json()
            if result['success']:
                print(f"Session created: {result['session']['id']}")
                return result['session']['id']

# Run the example
session_id = asyncio.run(create_session())
```

### Navigating a Session

```python
async def navigate_session(session_id, new_path):
    async with aiohttp.ClientSession() as session:
        data = {
            'path': new_path,
            'validate_permissions': True,
            'update_git_state': True
        }
        
        async with session.post(
            f'http://localhost:8082/api/claude/sessions/{session_id}/navigate',
            json=data
        ) as resp:
            result = await resp.json()
            if result['success']:
                print(f"Navigated to: {new_path}")
```

### Monitoring Session Metrics

```python
async def get_session_metrics(session_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f'http://localhost:8082/api/claude/sessions/{session_id}/metrics?hours=1'
        ) as resp:
            result = await resp.json()
            if result['success']:
                summary = result['summary']
                print(f"Session duration: {summary.get('duration_hours', 0):.2f} hours")
                print(f"Data points: {summary.get('total_data_points', 0)}")
```

## Features

### Session Lifecycle Management

- **Creation**: Create sessions with custom configurations and agent setups
- **Navigation**: Safely navigate sessions to new paths with validation
- **Cloning**: Clone existing sessions with agent and environment copying
- **Import/Export**: Backup and restore session configurations
- **Termination**: Clean session shutdown with resource cleanup

### Path Validation & Security

- **Cross-Platform**: Windows, macOS, and Linux support
- **Permission Checking**: Read, write, and execute permission validation
- **Security Scanning**: Restricted path detection and suspicious pattern checking
- **Git Integration**: Automatic git repository detection and status
- **Disk Space**: Available space monitoring and low-space warnings

### Agent Management

- **12 Agent Types**: Backend, Frontend, Database, API, DevOps, Security, etc.
- **Dependency Resolution**: Automatic agent initialization ordering
- **Configuration**: Memory limits, timeouts, retry attempts per agent
- **Lifecycle**: Start, stop, restart, and monitor agent health
- **Coordination**: Inter-agent communication and shared context

### Real-time Monitoring

- **Performance Metrics**: CPU, memory, and disk usage tracking
- **Session Analytics**: Commands executed, files modified, error rates
- **Alert System**: Configurable thresholds with callback support
- **WebSocket Updates**: Real-time status updates and notifications
- **Historical Data**: Metrics history with configurable retention

### API Features

- **RESTful Design**: Standard HTTP methods and status codes
- **JSON Responses**: Consistent response format with error handling
- **CORS Support**: Cross-origin request support
- **WebSocket**: Real-time bidirectional communication
- **Filtering**: Advanced filtering and pagination for session lists
- **Validation**: Request validation with detailed error messages

## Configuration

### Server Configuration

```python
# Default configuration
server = SessionManagementServer(
    port=8082,
    log_level="INFO"
)
```

### Session Configuration

```json
{
    "name": "Session Name",
    "working_directory": "/path/to/workspace",
    "description": "Session description",
    "git_enabled": true,
    "auto_save": true,
    "save_interval_seconds": 60,
    "max_memory_mb": 2048,
    "max_agents": 10,
    "agents": [
        {
            "agent_type": "BACKEND",
            "name": "backend-services", 
            "enabled": true,
            "priority": 2,
            "max_memory_mb": 512,
            "timeout_seconds": 300,
            "retry_attempts": 3
        }
    ],
    "environment_variables": {
        "NODE_ENV": "development"
    }
}
```

### Agent Types

Available agent types with their capabilities:

1. **ORCHESTRATOR** - master-orchestrator, smart-orchestrator
2. **FRONTEND** - frontend-architecture, UI/UX design
3. **BACKEND** - backend-services, API development  
4. **DATABASE** - database-architect, schema design
5. **API** - api-integration-specialist, external services
6. **MIDDLEWARE** - middleware-specialist, integration patterns
7. **DEVOPS** - devops-deployment, CI/CD automation
8. **SECURITY** - security-architecture, vulnerability scanning
9. **PERFORMANCE** - performance-optimization, monitoring
10. **QUALITY** - quality-assurance, testing frameworks
11. **DOCUMENTATION** - technical-documentation, API docs
12. **MONITORING** - monitoring-observability, alerting

## Monitoring & Analytics

### Session Metrics

- **Duration**: Session runtime and activity periods
- **Resource Usage**: CPU, memory, and disk utilization
- **Agent Activity**: Agent activations and performance
- **File Operations**: Files created, modified, and deleted
- **Error Tracking**: Error counts and rates
- **Performance**: Response times and throughput

### System Analytics

- **Session Distribution**: Status breakdown and trends
- **Agent Usage**: Most used agents and activation patterns
- **Performance Baselines**: Anomaly detection and trending
- **Resource Consumption**: System-wide resource tracking
- **Historical Trends**: Long-term usage patterns

### Alerts & Notifications

- **Resource Alerts**: High CPU, memory, or disk usage
- **Performance Alerts**: Slow response times or high error rates
- **System Alerts**: Service failures or connection issues
- **Custom Callbacks**: Programmable alert handling
- **WebSocket Broadcasting**: Real-time alert distribution

## Error Handling & Recovery

### Error Types

- **SessionValidationError**: Path or configuration validation failures
- **SessionNotFoundError**: Session not found or deleted
- **SessionPermissionError**: Insufficient permissions
- **AgentInitializationError**: Agent startup or configuration failures

### Recovery Mechanisms

- **Automatic Retry**: Configurable retry attempts with exponential backoff
- **Graceful Degradation**: Continue with available agents on partial failures
- **Resource Cleanup**: Automatic cleanup on errors or shutdown
- **Session Restoration**: Recover sessions from persisted state
- **Error Logging**: Detailed error logging with context

## Security Considerations

### Path Security

- **Restricted Paths**: Prevents access to system directories
- **Traversal Protection**: Blocks directory traversal attempts  
- **Permission Validation**: Verifies read/write permissions
- **Character Filtering**: Removes invalid filesystem characters

### API Security

- **Input Validation**: Schema validation for all requests
- **CORS Configuration**: Configurable cross-origin policies
- **Rate Limiting**: Built-in protection against abuse
- **Error Sanitization**: Prevents information leakage in errors

### Session Isolation

- **Workspace Isolation**: Each session operates in its own workspace
- **Agent Sandboxing**: Agents are isolated and resource-limited
- **State Separation**: Session states are kept separate
- **Clean Termination**: Proper cleanup on session end

## Performance & Scalability

### Performance Features

- **Async Architecture**: Non-blocking I/O for high concurrency
- **Connection Pooling**: Efficient resource utilization
- **Metrics Optimization**: Efficient monitoring with minimal overhead
- **Memory Management**: Configurable limits and garbage collection

### Scalability Considerations

- **Session Limits**: Configurable maximum concurrent sessions
- **Resource Monitoring**: Real-time resource usage tracking
- **Cleanup Automation**: Automatic cleanup of old sessions
- **Data Retention**: Configurable metrics and log retention

## Development & Testing

### Running Tests

```bash
# Basic functionality test
python simple_test.py

# Full API test (requires server running)
python examples/api_client_example.py
```

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Start in development mode with debug logging
python server.py --log-level DEBUG
```

### Adding New Agent Types

1. Update `AgentType` enum in `models/session_models.py`
2. Add agent definition in `services/agent_initializer.py`
3. Update agent dependencies if needed
4. Add corresponding hook files to core/hooks/

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Port Conflicts**: Change port if 8082 is in use
3. **Permission Errors**: Check filesystem permissions for working directories
4. **Agent Failures**: Check agent configuration and hook availability

### Debug Mode

Start the server with debug logging:

```bash
python server.py --log-level DEBUG
```

### Log Locations

- Server logs: `~/.claude/logs/session_manager.log`
- Session data: `~/.claude/sessions/`
- Metrics archives: `~/.claude/session_metrics/`

## API Response Format

All API responses follow this format:

```json
{
    "success": true,
    "data": {},
    "error": null,
    "timestamp": 1234567890.123
}
```

Error responses:

```json
{
    "success": false,
    "error": "Error description",
    "timestamp": 1234567890.123
}
```

## Contributing

This session management API is part of the Claude Code Agent System. When making changes:

1. Follow the existing code structure and patterns
2. Add tests for new functionality
3. Update documentation for API changes
4. Ensure backward compatibility where possible
5. Test across different platforms (Windows, macOS, Linux)

## License

Part of the Claude Code Agent System - refer to the main project license.

---

**Ready to get started?** Run `python start_session_api.py` and visit `http://localhost:8082/health` to verify the API is running!