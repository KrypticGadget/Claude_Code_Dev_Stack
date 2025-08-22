# LSP-Hook Bridge Middleware

A robust Language Server Protocol integration system that connects language server daemons to the hook system with real-time code analysis, IntelliSense enhancement, and automated code quality assessment.

## Features

### Core Features
- **Real-time Code Analysis Triggers**: Connect LSP events to hook execution for immediate code analysis
- **IntelliSense Enhancement**: Improve autocomplete with hook-based analysis and contextual suggestions  
- **Automated Code Quality Hooks**: Real-time code quality assessment with actionable insights
- **Language Server Integration**: Support for multiple programming languages (Python, TypeScript, JavaScript, Rust, Go, etc.)
- **Performance Optimization**: Minimize latency between LSP and hooks with caching and batching
- **Error Recovery**: Handle LSP disconnections and hook failures with automatic recovery
- **Configuration Management**: Dynamic hook-LSP mapping with hot-reloading capabilities

### Technical Implementation
- **WebSocket/TCP Communication Layer**: Real-time bidirectional communication
- **Protocol Translation**: Seamless translation between LSP and hook system protocols
- **Event Filtering and Routing**: Intelligent message filtering and routing based on configurable rules
- **Caching for Performance**: Multi-layer caching system for optimal performance
- **Health Monitoring**: Comprehensive system health monitoring with automatic recovery
- **Configuration Hot-reloading**: Dynamic configuration updates without system restart

## Architecture

### System Components

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Language Server   │◄──►│   LSP-Hook Bridge    │◄──►│    Hook System      │
│   (Python, TS, etc)│    │                      │    │   (Quality, Audio,  │
└─────────────────────┘    │  - Protocol Trans.   │    │    Formatting)      │
                           │  - Event Filtering   │    └─────────────────────┘
┌─────────────────────┐    │  - Performance Opt.  │    ┌─────────────────────┐
│   WebSocket Gateway │◄──►│  - Error Recovery    │◄──►│  Config Manager     │
│                     │    │  - Health Monitor    │    │                     │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
```

### Component Breakdown

1. **LSP Hook Bridge** (`lsp_hook_bridge.py`)
   - Core LSP-Hook communication bridge
   - Language server connection management
   - Hook execution orchestration
   - Event type mapping and filtering

2. **WebSocket LSP Gateway** (`websocket_lsp_gateway.py`)
   - Real-time WebSocket communication layer
   - Message filtering and routing
   - Performance optimization
   - Client session management

3. **Automated Quality Hooks** (`automated_quality_hooks.py`)
   - Real-time code quality assessment
   - Multi-language quality analyzers
   - Technical debt calculation
   - Quality trend analysis

4. **LSP Config Manager** (`lsp_config_manager.py`)
   - Dynamic configuration management
   - Hot-reload capabilities
   - Health monitoring
   - Error recovery coordination

5. **Integration Orchestrator** (`lsp_integration_orchestrator.py`)
   - Main system orchestrator
   - Component lifecycle management
   - System metrics and monitoring
   - Graceful shutdown handling

## Installation

### Prerequisites

```bash
# Python dependencies
pip install asyncio websockets watchdog psutil pyyaml

# Language servers (install as needed)
pip install python-lsp-server  # Python
npm install -g typescript-language-server  # TypeScript
npm install -g vscode-langservers-extracted  # HTML/CSS/JSON
```

### Setup

1. Clone or copy the middleware directory to your project:
```bash
cp -r core/middleware /path/to/your/project/
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure language servers in the configuration file (auto-generated on first run).

## Usage

### Quick Start

```python
from core.middleware import LSPIntegrationOrchestrator
import asyncio

async def main():
    # Create and start the orchestrator
    orchestrator = LSPIntegrationOrchestrator()
    await orchestrator.run()

if __name__ == "__main__":
    asyncio.run(main())
```

### Manual Quality Assessment

```python
from core.middleware import AutomatedQualityAssessor

# Create quality assessor
assessor = AutomatedQualityAssessor()

# Assess a single file
report = assessor.assess_file("path/to/file.py")
print(f"Quality score: {report.overall_score}")
print(f"Issues found: {len(report.issues)}")

# Get project overview
overview = assessor.get_project_overview("path/to/project")
print(f"Total technical debt: {overview['total_technical_debt_hours']} hours")
```

### WebSocket Client Example

```python
import asyncio
import websockets
import json

async def connect_to_lsp_gateway():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        # Send LSP request
        request = {
            "type": "lsp_request",
            "method": "textDocument/hover",
            "params": {
                "textDocument": {"uri": "file:///path/to/file.py"},
                "position": {"line": 10, "character": 5}
            }
        }
        await websocket.send(json.dumps(request))
        response = await websocket.recv()
        print(json.loads(response))

asyncio.run(connect_to_lsp_gateway())
```

### Configuration Management

```python
from core.middleware import LSPConfigManager, LanguageServerMapping

# Create config manager
config_manager = LSPConfigManager()

# Add a new language server
rust_server = LanguageServerMapping(
    server_name="rust",
    server_command=["rust-analyzer"],
    file_extensions=[".rs"],
    capabilities={"textDocument": {"publishDiagnostics": True}},
    hook_mappings={
        "textDocument/publishDiagnostics": ["quality_gate_hook", "audio_player_v3"]
    }
)

config_manager.add_language_server(rust_server)
```

## Configuration

### Default Configuration Structure

```yaml
enabled: true
auto_discovery: true
health_check_interval: 30
cache_enabled: true
cache_ttl: 300
websocket_port: 8765
websocket_host: "localhost"
max_concurrent_hooks: 10
log_level: "INFO"
performance_monitoring: true
error_recovery: true

language_servers:
  - server_name: "python"
    server_command: ["pylsp"]
    file_extensions: [".py"]
    capabilities:
      textDocument:
        publishDiagnostics: true
        hover: true
        completion: true
        definition: true
    hook_mappings:
      "textDocument/publishDiagnostics": ["quality_gate_hook", "audio_player_v3"]
      "textDocument/hover": ["context_manager"]
      "textDocument/completion": ["auto_formatter"]
    throttle_config:
      diagnostics_per_second: 5
      completion_per_second: 10

hooks:
  - hook_name: "quality_gate_hook"
    enabled: true
    triggers: ["textDocument/publishDiagnostics"]
    execution_mode: "async"
    timeout_seconds: 30.0
    retry_attempts: 2

global_filters:
  - "throttle_diagnostics"
  - "filter_test_files"
```

### Configuration File Locations

- Main config: `~/.claude/lsp/bridge_config.yaml`
- Cache files: `~/.claude/lsp/`
- Log files: System logs via Python logging

## API Reference

### Core Classes

#### LSPIntegrationOrchestrator

Main orchestrator class for the entire system.

```python
class LSPIntegrationOrchestrator:
    async def initialize() -> bool
    async def run() -> None
    async def shutdown() -> None
    async def trigger_quality_assessment(file_path: str) -> QualityReport
    def get_system_status() -> Dict[str, Any]
```

#### AutomatedQualityAssessor

Automated code quality assessment system.

```python
class AutomatedQualityAssessor:
    def assess_file(file_path: str, content: str = None) -> QualityReport
    def assess_directory(directory_path: str) -> Dict[str, QualityReport]
    def get_quality_trend(file_path: str) -> Dict[str, Any]
    def get_project_overview(project_path: str) -> Dict[str, Any]
```

#### LSPConfigManager

Configuration management with hot-reload support.

```python
class LSPConfigManager:
    def get_current_config() -> BridgeConfiguration
    async def update_config(updates: Dict[str, Any]) -> bool
    def add_language_server(mapping: LanguageServerMapping) -> bool
    def add_hook_config(hook_config: HookConfiguration) -> bool
    def get_health_status() -> Dict[str, Any]
```

#### WebSocketLSPGateway

Real-time WebSocket communication gateway.

```python
class WebSocketLSPGateway:
    async def start() -> None
    async def stop() -> None
    async def broadcast_event(event_type: str, data: Any) -> None
    def add_filter_rule(rule: FilterRule) -> None
    def get_status() -> Dict[str, Any]
```

### Quality Assessment

#### Quality Metrics

- **Complexity**: Cyclomatic complexity and structural complexity
- **Maintainability**: Code maintainability index based on multiple factors
- **Readability**: Code readability score including formatting and comments
- **Documentation**: Documentation coverage and quality
- **Testability**: How easily the code can be tested
- **Style**: Adherence to coding style guidelines
- **Security**: Basic security issue detection
- **Performance**: Performance-related code issues

#### Supported Languages

- **Python**: Full analysis with AST parsing
- **TypeScript/JavaScript**: Basic analysis with pattern matching
- **Extensible**: Easy to add new language analyzers

## Performance Optimization

### Caching Strategy

1. **L1 Cache**: In-memory application cache (5-minute TTL)
2. **L2 Cache**: Distributed cache for shared data (1-hour TTL)
3. **Response Cache**: LSP response caching for identical requests

### Message Filtering

- **Throttling**: Limit message frequency per client/method
- **Deduplication**: Remove duplicate messages within time windows
- **Priority Queuing**: Process high-priority messages first
- **Batching**: Batch similar messages for efficient processing

### Performance Metrics

The system tracks comprehensive performance metrics:

- Message processing throughput
- Hook execution times
- Memory and CPU usage
- Cache hit rates
- Error rates and recovery times

## Monitoring and Health

### Health Monitoring

- **System Metrics**: Memory, CPU, disk usage
- **Component Health**: LSP bridge, WebSocket gateway, config manager
- **Application Metrics**: Message processing, hook execution, error rates
- **Automatic Recovery**: Restart failed components automatically

### Error Recovery

- **Graceful Degradation**: Continue operation with reduced functionality
- **Component Restart**: Automatic restart of failed components
- **Configuration Reload**: Recover from configuration errors
- **Circuit Breaker**: Prevent cascade failures

## Development

### Running the Demo

```bash
python core/middleware/demo_lsp_bridge.py
```

The demo showcases:
- Configuration management
- Quality assessment on sample code
- System integration capabilities
- Performance metrics collection

### Testing

```bash
# Run quality assessment on your code
python -m core.middleware.automated_quality_hooks /path/to/your/code

# Test WebSocket gateway
python -m core.middleware.websocket_lsp_gateway

# Test configuration management
python -m core.middleware.lsp_config_manager
```

### Extending the System

#### Adding New Language Analyzers

```python
from core.middleware.automated_quality_hooks import QualityAnalyzer

class MyLanguageAnalyzer(QualityAnalyzer):
    @property
    def supported_languages(self) -> List[str]:
        return ["mylang"]
    
    def analyze(self, file_path: str, content: str) -> List[QualityIssue]:
        # Implement your analysis logic
        pass
    
    def get_metrics(self, file_path: str, content: str) -> Dict[QualityMetric, float]:
        # Implement your metrics calculation
        pass

# Register with the assessor
assessor = AutomatedQualityAssessor()
assessor.analyzers["mylang"] = MyLanguageAnalyzer()
```

#### Adding Custom Filters

```python
from core.middleware.websocket_lsp_gateway import FilterRule, FilterAction

def my_custom_filter(message):
    # Custom filtering logic
    return message.method != "ignore_this_method"

gateway.add_filter_rule(FilterRule(
    name="my_custom_filter",
    pattern="",
    action=FilterAction.BLOCK,
    condition=my_custom_filter,
    priority=1
))
```

## Troubleshooting

### Common Issues

1. **Language Server Not Found**
   - Ensure language server is installed and in PATH
   - Check server command in configuration
   - Verify file extensions mapping

2. **WebSocket Connection Failed**
   - Check port availability (default: 8765)
   - Verify firewall settings
   - Check SSL configuration if using HTTPS

3. **High Memory Usage**
   - Adjust cache settings in configuration
   - Enable performance monitoring
   - Check for memory leaks in custom analyzers

4. **Quality Assessment Errors**
   - Verify file permissions
   - Check supported file types
   - Review error logs for specific issues

### Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check system status:

```python
orchestrator = LSPIntegrationOrchestrator()
status = orchestrator.get_system_status()
print(json.dumps(status, indent=2))
```

## Contributing

### Code Style

- Follow PEP 8 for Python code
- Use type hints for all public APIs
- Include docstrings for all classes and methods
- Write comprehensive tests for new features

### Testing

- Unit tests for individual components
- Integration tests for component interaction
- Performance tests for optimization validation
- End-to-end tests for complete workflows

## License

This project is part of the Claude Code Agents system. See the main project license for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review system logs and health status
3. Run the demo script to verify installation
4. Check component-specific documentation