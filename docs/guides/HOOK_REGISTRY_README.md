# Claude Code Hook Registry System V3.6.9

## 🚀 Comprehensive Hook Management System

The Claude Code Hook Registry System V3.6.9 is a sophisticated backend system that provides comprehensive management, execution, and monitoring of all 38 Python hooks in the Claude Code development environment.

### 🎯 Key Features

- **📚 Metadata Storage**: Complete metadata management for all hooks
- **🔄 Trigger Mapping System**: Automated hook execution based on triggers  
- **⚡ Priority Queue System**: Intelligent execution order management
- **🔗 Cross-Hook Dependencies**: Dependency resolution and execution orchestration
- **🌐 LSP-Hook Bridge**: Language Server Protocol integration
- **🔥 Hot-Reload Capabilities**: Real-time hook updates during development
- **📊 Performance Monitoring**: Comprehensive execution metrics and insights
- **🌐 REST API**: Full HTTP API for web interfaces and integrations
- **⚙️ Configuration Management**: Flexible hook configuration system

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Hook Registry System V3.6.9                 │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────┐ │
│  │   Hook Manager  │  │  Hook Registry   │  │  Hook Config    │ │
│  │   (Main Entry)  │◄─►│  (Core System)   │◄─►│  (Settings)     │ │
│  └─────────────────┘  └──────────────────┘  └─────────────────┘ │
│           ▲                      ▲                      ▲       │
│           │                      │                      │       │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────┐ │
│  │   REST API      │  │ Performance      │  │  LSP Bridge     │ │
│  │   (Web Access)  │  │ Monitor          │  │  (Editor Int.)  │ │
│  └─────────────────┘  └──────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────────────────┐
                    │   38 Python Hooks    │
                    │                       │
                    │  • Orchestrators      │
                    │  • Audio Controllers  │
                    │  • Performance Mon.   │
                    │  • Context Managers   │
                    │  • Security Scanners  │
                    │  • And 33 more...     │
                    └───────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- All dependencies from `requirements.txt`

### Installation

1. **Install Dependencies**
   ```bash
   pip install -r core/hooks/requirements.txt
   ```

2. **Start the System**
   ```bash
   python start_hook_system.py --daemon
   ```

3. **Access the API**
   ```
   http://localhost:8888/health
   ```

### Command Line Usage

```bash
# Start as daemon
python start_hook_system.py --daemon

# Check system status
python start_hook_system.py --status-only

# Validate configuration
python start_hook_system.py --validate-only

# Start with custom API settings
python start_hook_system.py --api-host 0.0.0.0 --api-port 9000 --daemon
```

## 📖 Core Components

### 1. Hook Registry (`hook_registry.py`)

The core registry system that manages all hooks:

```python
from core.hooks.hook_registry import get_hook_registry

# Get registry instance
registry = get_hook_registry()

# Execute hook
execution_id = registry.execute_hook(
    hook_name="audio_player",
    trigger="user_prompt", 
    data={"message": "Hello World"}
)

# Check status
status = registry.get_system_status()
```

**Key Features:**
- Automatic hook discovery and registration
- Metadata extraction from Python files
- Priority-based execution queues
- Dependency resolution
- Hot-reload capabilities
- Performance monitoring

### 2. Hook Configuration (`hook_config.py`)

Configuration management system:

```python
from core.hooks.hook_config import get_hook_config_manager

# Get configuration manager
config_manager = get_hook_config_manager()

# List enabled hooks
enabled_hooks = config_manager.get_enabled_hooks()

# Update hook configuration
config_manager.update_hook_config("audio_player", {
    "enabled": True,
    "priority": 2,
    "timeout": 10.0
})
```

**Configuration Options:**
- Enable/disable hooks
- Set execution priorities (1-5)
- Configure timeouts and retries
- Set dependency relationships
- Enable LSP integration

### 3. REST API (`hook_registry_api.py`)

Full HTTP API for web interfaces:

```bash
# Health check
curl http://localhost:8888/health

# List all hooks
curl http://localhost:8888/api/hooks

# Execute hook
curl -X POST http://localhost:8888/api/hooks/audio_player/execute \
     -H "Content-Type: application/json" \
     -d '{"trigger": "api_call", "data": {"sound": "notification"}}'

# Get performance stats
curl http://localhost:8888/api/performance/system
```

**Available Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System health check |
| `/status` | GET | Comprehensive system status |
| `/api/hooks` | GET | List all hooks |
| `/api/hooks/{name}` | GET | Get specific hook details |
| `/api/hooks/{name}/execute` | POST | Execute specific hook |
| `/api/triggers/{trigger}/execute` | POST | Execute all hooks for trigger |
| `/api/performance/system` | GET | System performance metrics |
| `/api/performance/hooks/{name}` | GET | Hook-specific performance |
| `/api/lsp/hooks` | GET | LSP-compatible hooks |
| `/api/queue/status` | GET | Execution queue status |

### 4. Hook Manager (`hook_manager.py`)

Main integration layer that combines all components:

```python
from core.hooks.hook_manager import get_hook_manager

# Get integrated manager
manager = get_hook_manager(auto_start=True)

# Execute hook with full integration
execution_id = manager.execute_hook(
    hook_name="context_manager",
    trigger="user_prompt",
    data={"prompt": "Create a new React app"}
)

# Get comprehensive system status
status = manager.get_system_status()

# Validate entire system
validation = manager.validate_system()
```

## 🔧 Hook Development

### Creating a New Hook

1. **Create Hook File**
   ```python
   #!/usr/bin/env python3
   """
   My Custom Hook - Does something awesome
   Author: Your Name
   Version: 1.0.0
   """
   
   # @priority: 3
   # @triggers: user_prompt, custom_event
   # @depends: context_manager
   # @provides: custom_service
   # @tags: utility, custom
   # @lsp: true
   
   def process_hook(trigger: str, data: dict) -> dict:
       """Main hook entry point"""
       return {
           "success": True,
           "message": f"Processed {trigger} with data: {data}"
       }
   
   if __name__ == "__main__":
       # Test code
       result = process_hook("test", {"key": "value"})
       print(result)
   ```

2. **Register Hook**
   ```python
   # Hook will be auto-discovered on system startup
   # Or manually register:
   manager.register_hook_file("/path/to/my_custom_hook.py")
   ```

3. **Configure Hook**
   ```yaml
   # In hooks_config.yaml
   hooks:
     my_custom_hook:
       enabled: true
       priority: 3
       timeout: 15.0
       triggers:
         - user_prompt
         - custom_event
   ```

### Hook Metadata

The system automatically extracts metadata from hooks:

**From Docstrings:**
- Description (first line)
- Author, Version
- Tags

**From Comments:**
- `@priority: 1-5` - Execution priority
- `@triggers: list` - Trigger events
- `@depends: list` - Dependencies  
- `@provides: list` - Services provided
- `@tags: list` - Classification tags
- `@lsp: true/false` - LSP compatibility
- `@timeout: seconds` - Execution timeout

**From Code Analysis:**
- Function signatures
- Async capabilities
- Import dependencies
- LSP integration patterns

## 📊 Performance Monitoring

The system provides comprehensive performance monitoring:

### Hook Performance Metrics

- **Execution Time**: Average, min, max execution times
- **Memory Usage**: Memory consumption per execution
- **Success Rate**: Percentage of successful executions
- **Error Tracking**: Detailed error logging and patterns
- **CPU Usage**: CPU utilization during execution

### System Performance

- **Queue Metrics**: Execution queue size and processing rate
- **Resource Usage**: System CPU, memory, disk usage
- **Throughput**: Hooks executed per minute/hour
- **Health Scores**: Overall system health indicators

### Performance Insights

The system automatically generates performance insights:

```json
{
  "insights": [
    {
      "type": "performance_warning",
      "hook_name": "slow_hook",
      "issue": "slow_execution",
      "details": "Average execution time: 8.5s",
      "recommendation": "Consider optimizing hook logic or adding timeout"
    }
  ]
}
```

## 🔗 LSP Integration

Language Server Protocol integration for editor support:

### Enable LSP for Hook

```python
# In hook file
# @lsp: true
# @tags: completion, hover

def get_lsp_capabilities():
    return {
        "completionProvider": {"triggerCharacters": ["@", "."]},
        "hoverProvider": True,
        "definitionProvider": True
    }
```

### Activate LSP Bridge

```bash
curl -X POST http://localhost:8888/api/lsp/hooks/my_hook/activate \
     -H "Content-Type: application/json" \
     -d '{"endpoint_config": {"port": 9001}}'
```

## 🔥 Hot Reload

Automatic hot reloading during development:

### Enable Hot Reload

```python
# In hook file
# @hot_reload: true

# Or in configuration
hooks:
  my_hook:
    hot_reload: true
```

### Manual Reload

```bash
# Via API
curl -X POST http://localhost:8888/api/hooks/my_hook/reload

# Via CLI
python -m core.hooks.hook_manager reload --hook my_hook
```

## ⚡ Trigger System

Flexible trigger-based execution:

### Built-in Triggers

- `user_prompt` - User input/prompts
- `claude_response` - Claude AI responses  
- `agent_activation` - Agent system events
- `mcp_request` - MCP service requests
- `file_change` - File system changes
- `system_event` - System-level events
- `time_based` - Scheduled executions
- `custom` - Custom application triggers

### Execute by Trigger

```python
# Execute all hooks for a trigger
execution_ids = manager.execute_by_trigger(
    trigger="user_prompt",
    data={"prompt": "Create a new app", "user_id": "123"}
)
```

### Custom Triggers

```python
# Register custom trigger
manager.execute_by_trigger(
    trigger="my_custom_trigger",
    data={"custom_data": "value"}
)
```

## 🔗 Dependency Management

Sophisticated dependency resolution:

### Define Dependencies

```python
# In hook file
# @depends: context_manager, audio_system
# @provides: enhanced_orchestration

# Or in configuration
hooks:
  my_hook:
    dependencies:
      - context_manager
      - audio_system
    provides:
      - enhanced_orchestration
```

### Dependency Resolution

The system automatically:
- Resolves execution order
- Validates dependencies
- Detects circular dependencies
- Manages parallel execution

### Validation

```python
# Check dependency health
validation = manager.validate_system()
dependency_issues = validation['registry_validation']['dependency_issues']
```

## 🎛️ Configuration System

Flexible YAML-based configuration:

### System Configuration

```yaml
# hooks_config.yaml
system:
  max_concurrent_executions: 10
  default_timeout: 30.0
  hot_reload_enabled: true
  performance_monitoring: true
  lsp_bridge_enabled: true
  auto_discovery: true

hooks:
  audio_player:
    enabled: true
    priority: 2
    timeout: 5.0
    retry_count: 3
    max_concurrent: 1
    hot_reload: true
    lsp_enabled: false
    custom_config:
      volume: 0.8
      default_sound: "notification.wav"
```

### Environment-Based Config

```bash
# Development
export HOOK_ENV=development
export HOOK_LOG_LEVEL=DEBUG

# Production  
export HOOK_ENV=production
export HOOK_LOG_LEVEL=INFO
export HOOK_API_HOST=0.0.0.0
```

## 📈 Monitoring & Observability

### Health Checks

```bash
# Basic health check
curl http://localhost:8888/health

# Detailed system status
curl http://localhost:8888/status
```

### Metrics Collection

The system collects:
- Execution metrics per hook
- System resource usage
- Error rates and patterns
- Queue performance
- API request statistics

### Alerting

Configure alerts for:
- High error rates (>10%)
- Slow executions (>30s)
- High memory usage (>80%)
- Queue backups (>50 pending)
- System health issues

## 🔒 Security Features

### Input Validation

- JSON schema validation
- Parameter sanitization
- SQL injection prevention
- XSS protection

### Access Control

- API key authentication (optional)
- Rate limiting per endpoint
- IP whitelisting support
- Audit logging

### Secure Communication

- HTTPS support
- JWT token validation
- Certificate-based auth

## 🐛 Debugging & Troubleshooting

### Debug Mode

```bash
python start_hook_system.py --debug
```

### Log Analysis

```bash
# View system logs
tail -f hook_system.log

# Filter for specific hook
grep "audio_player" hook_system.log
```

### Common Issues

1. **Hook Not Found**
   ```bash
   # Check if hook is registered
   curl http://localhost:8888/api/hooks/my_hook
   ```

2. **Execution Failures**
   ```bash
   # Check performance insights
   curl http://localhost:8888/api/performance/insights
   ```

3. **Dependency Issues**
   ```bash
   # Validate dependencies
   curl http://localhost:8888/api/dependencies/validate
   ```

### Debug Tools

```python
# Manual hook execution with detailed output
from core.hooks.hook_registry import get_hook_registry

registry = get_hook_registry()
result = registry._execute_hook_context(context)
print(result)
```

## 🚀 Advanced Usage

### Batch Operations

```python
# Activate multiple hooks
hooks_to_activate = ["audio_player", "context_manager", "performance_monitor"]
results = {}
for hook_name in hooks_to_activate:
    results[hook_name] = manager.activate_hook(hook_name)
```

### Custom Event Handlers

```python
def on_hook_executed(data):
    print(f"Hook {data['hook_name']} executed with ID {data['execution_id']}")

manager.add_event_handler('hook_executed', on_hook_executed)
```

### Async Hook Execution

```python
import asyncio

async def async_hook_executor():
    # Async execution support built-in
    execution_id = await manager.execute_hook_async("my_async_hook", "trigger", {})
    return execution_id
```

## 📚 API Reference

### Hook Registry API

```python
class HookRegistry:
    def register_hook(self, metadata: HookMetadata) -> bool
    def activate_hook(self, hook_name: str) -> bool  
    def execute_hook(self, hook_name: str, trigger: str, data: Dict) -> str
    def get_hook_metadata(self, hook_name: str) -> Optional[Dict]
    def list_hooks(self, filter_by: Dict = None) -> List[Dict]
    def get_system_status(self) -> Dict
```

### Configuration API

```python
class HookConfigManager:
    def get_hook_config(self, hook_name: str) -> Optional[HookConfig]
    def update_hook_config(self, hook_name: str, updates: Dict) -> bool
    def get_enabled_hooks(self) -> List[str]
    def validate_configurations(self) -> List[str]
```

### Manager API

```python  
class HookManager:
    def execute_hook(self, hook_name: str, trigger: str, data: Dict) -> str
    def get_system_status(self) -> Dict
    def validate_system(self) -> Dict
    def optimize_system(self) -> Dict
    def reload_hook(self, hook_name: str) -> bool
```

## 🤝 Contributing

### Development Setup

1. **Clone and Setup**
   ```bash
   git clone <repository>
   cd Claude_Code_Agents/V3.6.9
   pip install -r core/hooks/requirements.txt
   ```

2. **Run Tests**
   ```bash
   pytest core/hooks/tests/
   ```

3. **Code Quality**
   ```bash
   black core/hooks/
   pylint core/hooks/
   ```

### Adding Features

1. Create feature branch
2. Implement changes
3. Add tests
4. Update documentation
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

For issues and support:

1. Check the troubleshooting section
2. Review system logs
3. Use the built-in validation tools
4. Create an issue with detailed information

## 🔄 Version History

### V3.6.9 (Current)
- Complete hook registry system
- REST API implementation
- Performance monitoring
- LSP bridge integration
- Hot-reload capabilities
- Comprehensive configuration management

### Previous Versions
- V3.0 - Initial hook system
- V2.0 - Basic orchestration
- V1.0 - Core functionality

---

**🎉 The Claude Code Hook Registry System V3.6.9 provides a robust, scalable, and feature-rich platform for managing all aspects of hook-based automation in your development environment.**