#!/usr/bin/env python3
"""
LSP Audio Hook Example - V3.0 Audio Feedback for LSP Events
Demonstrates how Python hooks can respond to LSP events with audio feedback
"""

import json
import os
import sys
from pathlib import Path

class LSPAudioHook:
    """Example hook that provides audio feedback for LSP events"""
    
    def __init__(self):
        self.home_dir = Path.home() / ".claude"
        self.audio_dir = self.home_dir / "audio"
        
        # LSP-specific audio mappings
        self.lsp_sounds = {
            'diagnostics_received': {
                'error': 'lsp_error.wav',
                'warning': 'lsp_warning.wav',
                'clean': 'lsp_clean.wav'
            },
            'server_started': 'lsp_server_start.wav',
            'server_stopped': 'lsp_server_stop.wav',
            'hover_received': 'lsp_hover.wav',
            'error_occurred': 'lsp_error_critical.wav',
            'analysis_performance': 'lsp_slow_analysis.wav'
        }
    
    def process_lsp_event(self, hook_message):
        """Process LSP event and determine audio response"""
        event = hook_message.get('event', '')
        data = hook_message.get('data', {})
        
        response = {
            'hook_name': 'lsp_audio_hook',
            'event': event,
            'response_type': 'action',
            'success': True,
            'timestamp': hook_message.get('timestamp'),
            'data': []
        }
        
        # Handle different LSP events
        if event == 'diagnostics_received':
            response['data'] = self.handle_diagnostics_event(data)
        elif event == 'server_started':
            response['data'] = self.handle_server_event(data, 'started')
        elif event == 'server_stopped':
            response['data'] = self.handle_server_event(data, 'stopped')
        elif event == 'hover_received':
            response['data'] = self.handle_hover_event(data)
        elif event == 'error_occurred':
            response['data'] = self.handle_error_event(data)
        elif event == 'analysis_performance':
            response['data'] = self.handle_performance_event(data)
        else:
            # Unknown event - no action needed
            response['response_type'] = 'data'
            response['data'] = {'message': f'LSP event received: {event}'}
        
        return response
    
    def handle_diagnostics_event(self, data):
        """Handle diagnostics events with appropriate audio"""
        error_count = data.get('error_count', 0)
        warning_count = data.get('warning_count', 0)
        file_path = data.get('file', 'unknown')
        
        actions = []
        
        if error_count > 0:
            # Critical errors - priority 1
            actions.append({
                'type': 'notify_user',
                'priority': 1,
                'parameters': {
                    'message': f'{error_count} error(s) found in {Path(file_path).name}',
                    'type': 'error',
                    'audio': self.lsp_sounds['diagnostics_received']['error']
                }
            })
            
            # Suggest quality gate intervention
            if error_count > 3:
                actions.append({
                    'type': 'trigger_analysis',
                    'priority': 2,
                    'parameters': {
                        'analysis_type': 'quality_review',
                        'target_files': [file_path],
                        'reason': 'high_error_count'
                    }
                })
        
        elif warning_count > 5:
            # Many warnings - priority 2
            actions.append({
                'type': 'notify_user',
                'priority': 2,
                'parameters': {
                    'message': f'{warning_count} warning(s) in {Path(file_path).name}',
                    'type': 'warning',
                    'audio': self.lsp_sounds['diagnostics_received']['warning']
                }
            })
        
        elif error_count == 0 and warning_count == 0:
            # Clean code - priority 3
            actions.append({
                'type': 'notify_user',
                'priority': 3,
                'parameters': {
                    'message': f'Clean code: {Path(file_path).name}',
                    'type': 'success',
                    'audio': self.lsp_sounds['diagnostics_received']['clean'],
                    'duration': 2000
                }
            })
        
        return actions
    
    def handle_server_event(self, data, event_type):
        """Handle server start/stop events"""
        server_id = data.get('server_id', 'unknown')
        
        return [{
            'type': 'notify_user',
            'priority': 1,
            'parameters': {
                'message': f'LSP server {event_type}: {server_id}',
                'type': 'info',
                'audio': self.lsp_sounds[f'server_{event_type}'],
                'show_user': False  # Just audio, no visual notification
            }
        }]
    
    def handle_hover_event(self, data):
        """Handle hover events"""
        symbol = data.get('symbol', 'unknown')
        result_count = data.get('result_count', 0)
        
        # Only notify for successful hover with documentation
        if result_count > 0 and data.get('has_documentation'):
            return [{
                'type': 'notify_user',
                'priority': 3,
                'parameters': {
                    'message': f'Documentation found for {symbol}',
                    'type': 'info',
                    'audio': self.lsp_sounds['hover_received'],
                    'duration': 1500,
                    'show_user': False
                }
            }]
        
        return []
    
    def handle_error_event(self, data):
        """Handle LSP error events"""
        error_message = data.get('error_message', 'Unknown error')
        
        return [{
            'type': 'notify_user',
            'priority': 1,
            'parameters': {
                'message': f'LSP Error: {error_message[:50]}...',
                'type': 'error',
                'audio': self.lsp_sounds['error_occurred'],
                'duration': 4000
            }
        }]
    
    def handle_performance_event(self, data):
        """Handle performance monitoring events"""
        operation = data.get('operation', 'unknown')
        duration = data.get('duration_ms', 0)
        
        # Only notify for slow operations
        if duration > 3000:  # 3 seconds
            return [{
                'type': 'notify_user',
                'priority': 2,
                'parameters': {
                    'message': f'Slow {operation}: {duration}ms',
                    'type': 'warning',
                    'audio': self.lsp_sounds['analysis_performance'],
                    'duration': 3000
                }
            }]
        
        return []
    
    def get_status_update(self, event, data):
        """Generate status updates for the status line"""
        if event == 'diagnostics_received':
            error_count = data.get('error_count', 0)
            warning_count = data.get('warning_count', 0)
            
            return {
                'lsp_diagnostics': {
                    'errors': error_count,
                    'warnings': warning_count,
                    'last_check': data.get('file', ''),
                    'status': 'clean' if error_count == 0 and warning_count == 0 else 'issues'
                }
            }
        
        return {}

def main():
    """Main hook execution"""
    try:
        # Read hook message from stdin
        hook_message = json.load(sys.stdin)
    except:
        # Fallback to environment variables
        hook_message = {
            'type': 'lsp_event',
            'event': os.environ.get('CLAUDE_LSP_EVENT', ''),
            'data': json.loads(os.environ.get('CLAUDE_LSP_DATA', '{}')),
            'timestamp': '',
            'source': 'lsp'
        }
    
    if not hook_message.get('event'):
        sys.exit(0)
    
    # Process the LSP event
    hook = LSPAudioHook()
    response = hook.process_lsp_event(hook_message)
    
    # Add status update if applicable
    status_update = hook.get_status_update(hook_message['event'], hook_message['data'])
    if status_update:
        response['data'].append({
            'type': 'update_config',
            'priority': 3,
            'parameters': {
                'config_updates': {
                    'status': status_update
                }
            }
        })
    
    # Output response as JSON
    print(json.dumps(response))

if __name__ == "__main__":
    main()