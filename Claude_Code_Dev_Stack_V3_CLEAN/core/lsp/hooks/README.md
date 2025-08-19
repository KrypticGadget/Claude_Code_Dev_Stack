# LSP-Hooks Integration V3.0

This directory contains the bidirectional integration system between the LSP daemon and the Python hooks system, enabling real-time communication and intelligent coordination between LSP events and hook responses.

## Architecture Overview

```
┌─────────────────┐    Events    ┌─────────────────┐    JSON/stdin    ┌─────────────────┐
│   LSP Daemon    │─────────────→│  Hook Adapter   │─────────────────→│  Python Hooks   │
│   (TypeScript)  │              │  (TypeScript)   │                  │   (Python)      │
└─────────────────┘              └─────────────────┘                  └─────────────────┘
         ↑                                ↓                                     ↓
         │                        ┌─────────────────┐    Responses     ┌─────────────────┐
         │                        │  Hook Handlers  │←─────────────────│  Hook Responses │
         │                        │  (TypeScript)   │                  │    (JSON)       │
         └────────────────────────└─────────────────┘                  └─────────────────┘
                    Actions/Config Updates
```

## Core Components

### 1. Hook Adapter (`adapter.ts`)
- **Purpose**: Main communication bridge between LSP and hooks
- **Features**:
  - Spawns Python hook processes
  - Manages stdin/stdout communication
  - Handles process lifecycle and timeouts
  - Debounces rapid events
  - Audio notification support

### 2. Event Triggers (`triggers.ts`)
- **Purpose**: Orchestrates LSP events and determines which hooks to trigger
- **Features**:
  - Rule-based event matching
  - Throttling and priority management
  - Parallel hook execution
  - Performance monitoring
  - Success rate tracking

### 3. Hook Handlers (`handlers.ts`)
- **Purpose**: Processes responses from Python hooks and applies them to LSP
- **Features**:
  - Action queue management
  - Configuration updates
  - User notifications
  - LSP command execution
  - Response history tracking

### 4. Configuration Manager (`config.ts`)
- **Purpose**: Centralized configuration for the entire integration
- **Features**:
  - Default configuration templates
  - Runtime configuration updates
  - Hook-specific settings
  - Export/import functionality
  - Validation and error checking

## LSP Events

The system responds to these LSP events:

| Event | Description | Typical Hooks Triggered |
|-------|-------------|-------------------------|
| `diagnostics_received` | Code analysis results | `audio_player_v3`, `quality_gate_hook`, `status_line_manager` |
| `server_started` | LSP server startup | `audio_player_v3`, `status_line_manager`, `smart_orchestrator` |
| `server_stopped` | LSP server shutdown | `audio_player_v3`, `status_line_manager` |
| `hover_received` | Symbol documentation | `status_line_manager` |
| `error_occurred` | LSP system errors | `audio_player_v3`, `smart_orchestrator` |
| `analysis_performance` | Performance metrics | `performance_monitor` |

## Hook Response Types

Python hooks can respond with different types of actions:

### Action Response
```json
{
  "response_type": "action",
  "data": [
    {
      "type": "refresh_diagnostics",
      "target": "/path/to/file.py",
      "priority": 1
    },
    {
      "type": "notify_user",
      "parameters": {
        "message": "Code analysis complete",
        "type": "success",
        "audio": "success.wav"
      }
    }
  ]
}
```

### Data Response
```json
{
  "response_type": "data",
  "data": {
    "status_update": {
      "lsp_quality": "good",
      "last_analysis": "2024-01-15T10:30:00Z"
    },
    "trigger_hooks": ["smart_orchestrator"]
  }
}
```

### Notification Response
```json
{
  "response_type": "notification",
  "data": {
    "message": "Analysis complete - 3 warnings found",
    "type": "warning",
    "audio": "warning.wav",
    "show_user": true,
    "affects_status": true
  }
}
```

### Configuration Response
```json
{
  "response_type": "config",
  "data": {
    "lsp_config": {
      "diagnostics_enabled": true
    },
    "handler_config": {
      "audio_feedback": false
    },
    "restart_required": false
  }
}
```

## Integration Usage

### Basic Setup

```typescript
import { lspHooksIntegration } from './hooks/index.js';

// Initialize the integration system
await lspHooksIntegration.initialize();

// Trigger an LSP event
await lspHooksIntegration.triggerEvent('diagnostics_received', {
  file: '/path/to/file.py',
  error_count: 2,
  warning_count: 5,
  total_count: 7
});

// Listen for user notifications
lspHooksIntegration.on('user_notification', (notification) => {
  console.log(`User notification: ${notification.message}`);
});
```

### Creating a Python Hook

```python
#!/usr/bin/env python3
import json
import sys

def process_lsp_event(hook_message):
    event = hook_message.get('event', '')
    data = hook_message.get('data', {})
    
    if event == 'diagnostics_received':
        error_count = data.get('error_count', 0)
        
        if error_count > 0:
            return {
                'response_type': 'action',
                'data': [{
                    'type': 'notify_user',
                    'priority': 1,
                    'parameters': {
                        'message': f'{error_count} errors found!',
                        'type': 'error',
                        'audio': 'error.wav'
                    }
                }]
            }
    
    return {'response_type': 'data', 'data': {}}

def main():
    hook_message = json.load(sys.stdin)
    response = process_lsp_event(hook_message)
    print(json.dumps(response))

if __name__ == "__main__":
    main()
```

## Configuration

### Default Configuration Location
- Configuration file: `~/.claude/lsp_hooks_config.json`
- Default template: `~/.claude/lsp_hooks_defaults.json`

### Example Configuration
```json
{
  "enabled": true,
  "adapter": {
    "debounce_ms": 300,
    "max_diagnostics_per_event": 50,
    "audio_notifications": true,
    "hook_timeout_ms": 5000
  },
  "triggers": {
    "enabled": true,
    "rules": [
      {
        "name": "critical_errors",
        "event": "diagnostics_received",
        "condition": "data.error_count > 0",
        "throttle_ms": 1000,
        "priority": 1,
        "hooks": ["audio_player_v3", "quality_gate_hook"],
        "enabled": true
      }
    ]
  },
  "hooks": {
    "audio_player_v3": {
      "enabled": true,
      "priority": 1,
      "events": ["diagnostics_received", "server_started"]
    }
  }
}
```

## Performance Considerations

### Debouncing
- Events are debounced by default (300ms) to prevent overwhelming hooks
- Configurable per-event debouncing
- Smart throttling based on event type

### Parallel Execution
- Multiple hooks can run simultaneously for the same event
- Priority-based execution ordering
- Timeout management for hanging processes

### Resource Management
- Automatic cleanup of hook processes
- Memory usage monitoring
- Queue size limits to prevent overflow

## Example Integrations

The `examples/` directory contains sample integrations:

### 1. `lsp_audio_hook.py`
- Provides audio feedback for LSP events
- Maps different event types to specific sounds
- Intelligent priority-based notifications

### 2. `lsp_quality_orchestrator.py`
- Orchestrates agents based on code quality events
- Triggers smart agent coordination
- Creates quality improvement workflows

## Debugging

### Enable Debug Mode
```bash
export CLAUDE_DEBUG=1
```

### Check Integration Status
```typescript
const status = lspHooksIntegration.getStatus();
console.log(JSON.stringify(status, null, 2));
```

### Test Integration
```typescript
const testResult = await lspHooksIntegration.testIntegration();
console.log('Test result:', testResult);
```

### View Diagnostic Information
```typescript
const diagnostics = lspHooksIntegration.getDiagnosticInfo();
console.log('Diagnostics:', diagnostics);
```

## Audio Integration

The system supports rich audio feedback:

### Audio Event Mapping
- `lsp_error.wav` - Critical errors
- `lsp_warning.wav` - Warnings
- `lsp_clean.wav` - Clean code
- `lsp_server_start.wav` - Server startup
- `lsp_hover.wav` - Hover information found

### Audio Configuration
```json
{
  "adapter": {
    "audio_notifications": true
  },
  "hooks": {
    "audio_player_v3": {
      "config": {
        "sounds": {
          "error": "lsp_error.wav",
          "warning": "lsp_warning.wav",
          "success": "lsp_success.wav"
        }
      }
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **Hooks not triggering**
   - Check if integration is enabled: `lspHooksIntegration.getStatus()`
   - Verify hook scripts are executable
   - Check debounce settings (may be too aggressive)

2. **Performance issues**
   - Reduce debounce time
   - Limit number of hooks per event
   - Check hook script performance

3. **Audio not playing**
   - Verify audio files exist
   - Check system audio configuration
   - Enable debug mode to see audio attempts

### Log Files
- LSP daemon logs: Check LSP log file path
- Hook execution: Set `CLAUDE_DEBUG=1`
- Configuration issues: Check `~/.claude/lsp_hooks_config.json`

## Future Enhancements

- WebSocket-based communication for real-time updates
- Machine learning-based event prediction
- Advanced hook orchestration patterns
- Integration with external IDEs
- Real-time collaboration features

## Contributing

When adding new hooks or modifying the integration:

1. Update trigger rules in `triggers.ts`
2. Add appropriate event handlers in `handlers.ts`
3. Update configuration schema in `config.ts`
4. Add example hooks in `examples/`
5. Update this documentation

The integration system is designed to be extensible and maintainable, enabling powerful coordination between LSP analysis and the hook ecosystem.