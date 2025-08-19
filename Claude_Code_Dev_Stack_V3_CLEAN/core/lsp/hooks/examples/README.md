# LSP-Hooks Integration Examples

This directory contains example implementations showing how to create Python hooks that respond to LSP events.

## Available Examples

### 1. `lsp_audio_hook.py`
**Purpose**: Provides intelligent audio feedback for LSP events

**Features**:
- Maps LSP events to specific audio files
- Priority-based notification system
- Context-aware sound selection
- Configurable audio mappings

**Events Handled**:
- `diagnostics_received` → Error/warning/success sounds
- `server_started` → Server startup sound
- `hover_received` → Documentation found sound
- `error_occurred` → Critical error sound

**Usage**:
```bash
python lsp_audio_hook.py
```

### 2. `lsp_quality_orchestrator.py`
**Purpose**: Orchestrates agents based on LSP quality events

**Features**:
- Rule-based agent orchestration
- Quality trend analysis
- Smart agent coordination
- Performance monitoring integration

**Events Handled**:
- `diagnostics_received` → Quality assessment and agent triggering
- `error_occurred` → Error analysis and remediation
- `analysis_performance` → Performance optimization workflows

**Usage**:
```bash
python lsp_quality_orchestrator.py
```

## Running Examples

These examples are designed to be called by the LSP daemon automatically when events occur. However, you can test them manually:

### Manual Testing

1. **Create test input**:
```json
{
  "type": "lsp_event",
  "event": "diagnostics_received",
  "data": {
    "file": "/path/to/test.py",
    "error_count": 2,
    "warning_count": 5,
    "total_count": 7
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "source": "lsp"
}
```

2. **Run the hook**:
```bash
echo '{"type":"lsp_event","event":"diagnostics_received","data":{"error_count":2,"warning_count":5}}' | python lsp_audio_hook.py
```

3. **Expected output** (example):
```json
{
  "hook_name": "lsp_audio_hook",
  "event": "diagnostics_received",
  "response_type": "action",
  "success": true,
  "data": [
    {
      "type": "notify_user",
      "priority": 1,
      "parameters": {
        "message": "2 error(s) found in test.py",
        "type": "error",
        "audio": "lsp_error.wav"
      }
    }
  ]
}
```

## Creating Your Own Hooks

### Basic Template

```python
#!/usr/bin/env python3
import json
import sys
from pathlib import Path

class MyLSPHook:
    def __init__(self):
        self.name = "my_lsp_hook"
    
    def process_lsp_event(self, hook_message):
        event = hook_message.get('event', '')
        data = hook_message.get('data', {})
        
        response = {
            'hook_name': self.name,
            'event': event,
            'response_type': 'data',
            'success': True,
            'timestamp': hook_message.get('timestamp'),
            'data': {}
        }
        
        # Handle your events here
        if event == 'diagnostics_received':
            response['data'] = self.handle_diagnostics(data)
        
        return response
    
    def handle_diagnostics(self, data):
        # Your logic here
        return {'message': 'Diagnostics processed'}

def main():
    try:
        hook_message = json.load(sys.stdin)
    except:
        hook_message = {
            'event': os.environ.get('CLAUDE_LSP_EVENT', ''),
            'data': json.loads(os.environ.get('CLAUDE_LSP_DATA', '{}'))
        }
    
    if not hook_message.get('event'):
        sys.exit(0)
    
    hook = MyLSPHook()
    response = hook.process_lsp_event(hook_message)
    print(json.dumps(response))

if __name__ == "__main__":
    main()
```

### Response Types

Your hooks can return different types of responses:

#### 1. Action Response
Triggers LSP actions like refreshing diagnostics or showing notifications.

```python
return {
    'response_type': 'action',
    'data': [
        {
            'type': 'refresh_diagnostics',
            'target': file_path,
            'priority': 1
        }
    ]
}
```

#### 2. Data Response
Provides data for other hooks or system updates.

```python
return {
    'response_type': 'data',
    'data': {
        'status_update': {'quality': 'good'},
        'trigger_hooks': ['smart_orchestrator']
    }
}
```

#### 3. Notification Response
Shows user notifications with optional audio.

```python
return {
    'response_type': 'notification',
    'data': {
        'message': 'Analysis complete',
        'type': 'success',
        'audio': 'success.wav',
        'show_user': True
    }
}
```

#### 4. Configuration Response
Updates system configuration.

```python
return {
    'response_type': 'config',
    'data': {
        'lsp_config': {'diagnostics_enabled': True},
        'restart_required': False
    }
}
```

### Available LSP Events

Your hooks can respond to these events:

- `diagnostics_received` - Code analysis results
- `server_started` - LSP server startup
- `server_stopped` - LSP server shutdown  
- `hover_received` - Symbol documentation requests
- `error_occurred` - System errors
- `analysis_performance` - Performance metrics
- `daemon_started` - LSP daemon startup
- `daemon_stopping` - LSP daemon shutdown

### Best Practices

1. **Performance**: Keep hook execution fast (< 1 second)
2. **Error Handling**: Always handle exceptions gracefully
3. **Configuration**: Use environment variables for settings
4. **Logging**: Use stderr for debug output
5. **Testing**: Test with various event scenarios

### Testing Framework

Use this helper to test your hooks:

```python
def test_hook(hook_class, event, data):
    """Test helper for LSP hooks"""
    hook_message = {
        'type': 'lsp_event',
        'event': event,
        'data': data,
        'timestamp': '2024-01-15T10:30:00Z',
        'source': 'test'
    }
    
    hook = hook_class()
    response = hook.process_lsp_event(hook_message)
    
    print(f"Event: {event}")
    print(f"Response: {json.dumps(response, indent=2)}")
    return response

# Example usage
test_hook(MyLSPHook, 'diagnostics_received', {
    'file': '/test/file.py',
    'error_count': 1,
    'warning_count': 3
})
```

## Integration with Existing Hooks

These LSP hooks can coordinate with the existing 28 hooks in the system:

### Audio Integration
```python
# Trigger audio from LSP hook
{
    'type': 'notify_user',
    'parameters': {
        'audio': 'custom_sound.wav'
    }
}
```

### Smart Orchestrator Integration
```python
# Trigger agent orchestration
{
    'type': 'trigger_analysis',
    'parameters': {
        'analysis_type': 'smart_orchestration',
        'agents_suggested': ['quality-assurance-lead', 'backend-services']
    }
}
```

### Status Line Integration
```python
# Update status line
{
    'type': 'update_config',
    'parameters': {
        'config_updates': {
            'status': {
                'lsp_status': 'analyzing',
                'quality_score': 85
            }
        }
    }
}
```

## Debugging

### Enable Debug Output
```bash
export CLAUDE_DEBUG=1
```

### Test Event Manually
```bash
export CLAUDE_LSP_EVENT="diagnostics_received"
export CLAUDE_LSP_DATA='{"error_count":2,"file":"/test.py"}'
python your_hook.py
```

### Check Hook Output
The LSP daemon logs all hook responses. Check the daemon log file for output and errors.

### Common Issues

1. **Hook not triggering**: Check if the hook is listed in the trigger rules
2. **No output**: Ensure your hook prints JSON to stdout
3. **Errors**: Check stderr output and daemon logs
4. **Performance**: Keep hook execution under 5 seconds

## Contributing

When adding new examples:

1. Follow the naming convention: `lsp_[purpose]_hook.py`
2. Include comprehensive docstrings
3. Add example usage and test cases
4. Update this README with your example
5. Ensure compatibility with the integration system