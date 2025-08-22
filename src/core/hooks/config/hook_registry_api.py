#!/usr/bin/env python3
"""
Hook Registry REST API - V3.6.9
Provides comprehensive REST API endpoints for hook registry management
"""

import json
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from functools import wraps
import logging
from pathlib import Path
import threading

# Import hook registry
from .hook_registry import get_hook_registry, HookPriority, HookState, TriggerType, HookRegistryError

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HookRegistryAPI:
    """REST API for Hook Registry System"""
    
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for web interface
        
        # Get registry instance
        self.registry = get_hook_registry()
        
        # API state
        self.api_stats = {
            'requests_total': 0,
            'requests_successful': 0,
            'requests_failed': 0,
            'start_time': datetime.now(),
            'endpoints_accessed': {}
        }
        
        # Setup routes
        self._setup_routes()
        self._setup_error_handlers()
        
        # Thread for running the server
        self.server_thread = None
        self.running = False
    
    def _setup_routes(self):
        """Setup all API routes"""
        
        # Health and status endpoints
        self.app.route('/health', methods=['GET'])(self.health_check)
        self.app.route('/status', methods=['GET'])(self.get_system_status)
        self.app.route('/api/info', methods=['GET'])(self.get_api_info)
        
        # Hook management endpoints
        self.app.route('/api/hooks', methods=['GET'])(self.list_hooks)
        self.app.route('/api/hooks/<hook_name>', methods=['GET'])(self.get_hook)
        self.app.route('/api/hooks/<hook_name>/register', methods=['POST'])(self.register_hook)
        self.app.route('/api/hooks/<hook_name>/activate', methods=['POST'])(self.activate_hook)
        self.app.route('/api/hooks/<hook_name>/deactivate', methods=['POST'])(self.deactivate_hook)
        self.app.route('/api/hooks/<hook_name>/reload', methods=['POST'])(self.reload_hook)
        
        # Hook execution endpoints
        self.app.route('/api/hooks/<hook_name>/execute', methods=['POST'])(self.execute_hook)
        self.app.route('/api/triggers/<trigger>/execute', methods=['POST'])(self.execute_by_trigger)
        
        # Trigger management endpoints
        self.app.route('/api/triggers', methods=['GET'])(self.list_triggers)
        self.app.route('/api/triggers/<trigger>/hooks', methods=['GET'])(self.get_trigger_hooks)
        
        # Performance and monitoring endpoints
        self.app.route('/api/performance/hooks', methods=['GET'])(self.get_performance_stats)
        self.app.route('/api/performance/hooks/<hook_name>', methods=['GET'])(self.get_hook_performance)
        self.app.route('/api/performance/system', methods=['GET'])(self.get_system_performance)
        self.app.route('/api/performance/insights', methods=['GET'])(self.get_performance_insights)
        
        # Dependency management endpoints
        self.app.route('/api/dependencies/validate', methods=['GET'])(self.validate_dependencies)
        self.app.route('/api/dependencies/graph', methods=['GET'])(self.get_dependency_graph)
        
        # LSP integration endpoints
        self.app.route('/api/lsp/hooks', methods=['GET'])(self.list_lsp_hooks)
        self.app.route('/api/lsp/hooks/<hook_name>/activate', methods=['POST'])(self.activate_lsp_hook)
        self.app.route('/api/lsp/hooks/<hook_name>/deactivate', methods=['POST'])(self.deactivate_lsp_hook)
        self.app.route('/api/lsp/capabilities/<hook_name>', methods=['GET'])(self.get_lsp_capabilities)
        
        # Queue and execution management
        self.app.route('/api/queue/status', methods=['GET'])(self.get_queue_status)
        self.app.route('/api/executions/active', methods=['GET'])(self.get_active_executions)
        self.app.route('/api/executions/<execution_id>/status', methods=['GET'])(self.get_execution_status)
        
        # Configuration and settings
        self.app.route('/api/config', methods=['GET'])(self.get_configuration)
        self.app.route('/api/config', methods=['POST'])(self.update_configuration)
        
        # Utility endpoints
        self.app.route('/api/discover', methods=['POST'])(self.discover_hooks)
        self.app.route('/api/validate', methods=['GET'])(self.validate_system)
        self.app.route('/api/optimize', methods=['POST'])(self.optimize_system)
    
    def _setup_error_handlers(self):
        """Setup error handlers"""
        
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({
                'error': 'Not Found',
                'message': 'The requested resource was not found'
            }), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'An internal error occurred'
            }), 500
        
        @self.app.errorhandler(HookRegistryError)
        def hook_registry_error(error):
            return jsonify({
                'error': 'Hook Registry Error',
                'message': str(error)
            }), 400
    
    def _track_request(self, endpoint_name):
        """Decorator to track API requests"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                self.api_stats['requests_total'] += 1
                self.api_stats['endpoints_accessed'][endpoint_name] = (
                    self.api_stats['endpoints_accessed'].get(endpoint_name, 0) + 1
                )
                
                try:
                    result = f(*args, **kwargs)
                    self.api_stats['requests_successful'] += 1
                    return result
                except Exception as e:
                    self.api_stats['requests_failed'] += 1
                    logger.error(f"Error in {endpoint_name}: {str(e)}")
                    raise
            
            return decorated_function
        return decorator
    
    # Health and Status Endpoints
    
    @_track_request
    def health_check(self):
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'registry_initialized': self.registry.initialized,
            'total_hooks': len(self.registry.hooks),
            'active_hooks': len([h for h in self.registry.hooks.values() if h.state == HookState.ACTIVE])
        })
    
    @_track_request
    def get_system_status(self):
        """Get comprehensive system status"""
        status = self.registry.get_system_status()
        status['api_stats'] = self.api_stats
        return jsonify(status)
    
    @_track_request
    def get_api_info(self):
        """Get API information"""
        return jsonify({
            'name': 'Hook Registry API',
            'version': '3.6.9',
            'description': 'Comprehensive REST API for hook registry management',
            'endpoints': {
                'health': '/health',
                'status': '/status',
                'hooks': '/api/hooks',
                'triggers': '/api/triggers',
                'performance': '/api/performance',
                'lsp': '/api/lsp',
                'queue': '/api/queue',
                'config': '/api/config'
            },
            'started_at': self.api_stats['start_time'].isoformat(),
            'uptime_seconds': (datetime.now() - self.api_stats['start_time']).total_seconds()
        })
    
    # Hook Management Endpoints
    
    @_track_request
    def list_hooks(self):
        """List all hooks with optional filtering"""
        # Get filter parameters
        filter_params = {}
        if request.args.get('state'):
            filter_params['state'] = HookState(request.args.get('state'))
        if request.args.get('priority'):
            filter_params['priority'] = HookPriority[request.args.get('priority').upper()]
        if request.args.get('tags'):
            filter_params['tags'] = request.args.get('tags').split(',')
        
        hooks = self.registry.list_hooks(filter_params if filter_params else None)
        
        return jsonify({
            'hooks': hooks,
            'total': len(hooks),
            'filtered': bool(filter_params)
        })
    
    @_track_request
    def get_hook(self, hook_name: str):
        """Get detailed information about a specific hook"""
        metadata = self.registry.get_hook_metadata(hook_name)
        
        if metadata is None:
            return jsonify({'error': f'Hook {hook_name} not found'}), 404
        
        return jsonify(metadata)
    
    @_track_request
    def register_hook(self, hook_name: str):
        """Register a new hook"""
        if not request.json:
            return jsonify({'error': 'JSON payload required'}), 400
        
        try:
            # Extract hook metadata from request
            hook_data = request.json
            hook_data['name'] = hook_name
            
            # Convert enum fields
            if 'priority' in hook_data:
                hook_data['priority'] = HookPriority[hook_data['priority'].upper()]
            if 'state' in hook_data:
                hook_data['state'] = HookState(hook_data['state'])
            
            # Create metadata object
            from .hook_registry import HookMetadata
            metadata = HookMetadata(**hook_data)
            
            success = self.registry.register_hook(metadata)
            
            if success:
                return jsonify({
                    'message': f'Hook {hook_name} registered successfully',
                    'hook': self.registry.get_hook_metadata(hook_name)
                })
            else:
                return jsonify({'error': f'Failed to register hook {hook_name}'}), 400
            
        except Exception as e:
            return jsonify({'error': f'Registration failed: {str(e)}'}), 400
    
    @_track_request
    def activate_hook(self, hook_name: str):
        """Activate a hook"""
        success = self.registry.activate_hook(hook_name)
        
        if success:
            return jsonify({
                'message': f'Hook {hook_name} activated successfully',
                'hook': self.registry.get_hook_metadata(hook_name)
            })
        else:
            return jsonify({'error': f'Failed to activate hook {hook_name}'}), 400
    
    @_track_request
    def deactivate_hook(self, hook_name: str):
        """Deactivate a hook"""
        success = self.registry.deactivate_hook(hook_name)
        
        if success:
            return jsonify({
                'message': f'Hook {hook_name} deactivated successfully',
                'hook': self.registry.get_hook_metadata(hook_name)
            })
        else:
            return jsonify({'error': f'Failed to deactivate hook {hook_name}'}), 400
    
    @_track_request
    def reload_hook(self, hook_name: str):
        """Hot reload a hook"""
        if hook_name not in self.registry.hooks:
            return jsonify({'error': f'Hook {hook_name} not found'}), 404
        
        metadata = self.registry.hooks[hook_name]
        self.registry.hot_reload_hook(metadata.file_path)
        
        return jsonify({
            'message': f'Hook {hook_name} reloaded successfully',
            'hook': self.registry.get_hook_metadata(hook_name)
        })
    
    # Hook Execution Endpoints
    
    @_track_request
    def execute_hook(self, hook_name: str):
        """Execute a specific hook"""
        if not request.json:
            return jsonify({'error': 'JSON payload required'}), 400
        
        try:
            data = request.json
            trigger = data.get('trigger', 'api_request')
            hook_data = data.get('data', {})
            priority = data.get('priority')
            timeout = data.get('timeout', 30.0)
            
            # Convert priority if provided
            if priority:
                priority = HookPriority[priority.upper()]
            
            execution_id = self.registry.execute_hook(
                hook_name, trigger, hook_data, priority, timeout
            )
            
            return jsonify({
                'message': f'Hook {hook_name} execution initiated',
                'execution_id': execution_id,
                'hook_name': hook_name,
                'trigger': trigger
            })
            
        except Exception as e:
            return jsonify({'error': f'Execution failed: {str(e)}'}), 400
    
    @_track_request
    def execute_by_trigger(self, trigger: str):
        """Execute all hooks for a specific trigger"""
        if not request.json:
            return jsonify({'error': 'JSON payload required'}), 400
        
        try:
            data = request.json
            hook_data = data.get('data', {})
            priority = data.get('priority')
            
            # Convert priority if provided
            if priority:
                priority = HookPriority[priority.upper()]
            
            execution_ids = self.registry.execute_by_trigger(trigger, hook_data, priority)
            
            return jsonify({
                'message': f'Executed {len(execution_ids)} hooks for trigger {trigger}',
                'trigger': trigger,
                'execution_ids': execution_ids,
                'hooks_executed': len(execution_ids)
            })
            
        except Exception as e:
            return jsonify({'error': f'Execution failed: {str(e)}'}), 400
    
    # Trigger Management Endpoints
    
    @_track_request
    def list_triggers(self):
        """List all available triggers"""
        triggers = {}
        
        for trigger, hook_names in self.registry.trigger_mappings.items():
            active_hooks = [name for name in hook_names 
                           if name in self.registry.hooks and 
                           self.registry.hooks[name].state == HookState.ACTIVE]
            
            triggers[trigger] = {
                'total_hooks': len(hook_names),
                'active_hooks': len(active_hooks),
                'hook_names': hook_names,
                'active_hook_names': active_hooks
            }
        
        return jsonify({
            'triggers': triggers,
            'total_triggers': len(triggers)
        })
    
    @_track_request
    def get_trigger_hooks(self, trigger: str):
        """Get hooks for a specific trigger"""
        if trigger not in self.registry.trigger_mappings:
            return jsonify({'error': f'Trigger {trigger} not found'}), 404
        
        hook_names = self.registry.trigger_mappings[trigger]
        hooks_details = []
        
        for hook_name in hook_names:
            if hook_name in self.registry.hooks:
                metadata = self.registry.get_hook_metadata(hook_name)
                hooks_details.append(metadata)
        
        return jsonify({
            'trigger': trigger,
            'hooks': hooks_details,
            'total_hooks': len(hooks_details)
        })
    
    # Performance Monitoring Endpoints
    
    @_track_request
    def get_performance_stats(self):
        """Get performance statistics for all hooks"""
        hooks_with_stats = []
        
        for hook_name in self.registry.hooks.keys():
            stats = self.registry.performance_monitor.get_hook_stats(hook_name)
            if stats:
                hooks_with_stats.append({
                    'hook_name': hook_name,
                    'stats': stats
                })
        
        return jsonify({
            'hooks': hooks_with_stats,
            'total_hooks': len(hooks_with_stats)
        })
    
    @_track_request
    def get_hook_performance(self, hook_name: str):
        """Get performance statistics for a specific hook"""
        if hook_name not in self.registry.hooks:
            return jsonify({'error': f'Hook {hook_name} not found'}), 404
        
        stats = self.registry.performance_monitor.get_hook_stats(hook_name)
        
        return jsonify({
            'hook_name': hook_name,
            'stats': stats or {},
            'monitoring_active': self.registry.performance_monitor.monitoring_active
        })
    
    @_track_request
    def get_system_performance(self):
        """Get system-wide performance statistics"""
        stats = self.registry.performance_monitor.get_system_stats()
        
        return jsonify({
            'system_stats': stats,
            'timestamp': datetime.now().isoformat()
        })
    
    @_track_request
    def get_performance_insights(self):
        """Get performance insights and recommendations"""
        insights = self.registry.performance_monitor.get_performance_insights()
        
        return jsonify({
            'insights': insights,
            'total_insights': len(insights),
            'timestamp': datetime.now().isoformat()
        })
    
    # Dependency Management Endpoints
    
    @_track_request
    def validate_dependencies(self):
        """Validate all hook dependencies"""
        issues = self.registry.dependency_resolver.validate_dependencies(self.registry.hooks)
        
        return jsonify({
            'valid': len(issues) == 0,
            'issues': issues,
            'total_issues': len(issues)
        })
    
    @_track_request
    def get_dependency_graph(self):
        """Get the dependency graph"""
        graph = {}
        
        for hook_name, deps in self.registry.dependency_resolver.dependency_graph.items():
            graph[hook_name] = {
                'dependencies': list(deps),
                'provides': []
            }
        
        for provided, providers in self.registry.dependency_resolver.provides_map.items():
            for provider in providers:
                if provider in graph:
                    graph[provider]['provides'].append(provided)
                else:
                    graph[provider] = {'dependencies': [], 'provides': [provided]}
        
        return jsonify({
            'dependency_graph': graph,
            'total_nodes': len(graph)
        })
    
    # LSP Integration Endpoints
    
    @_track_request
    def list_lsp_hooks(self):
        """List hooks with LSP compatibility"""
        lsp_hooks = []
        
        for hook_name, metadata in self.registry.hooks.items():
            if metadata.lsp_compatible:
                lsp_info = {
                    'hook_name': hook_name,
                    'lsp_compatible': True,
                    'active': hook_name in self.registry.lsp_bridge.active_connections,
                    'capabilities': self.registry.lsp_bridge.get_lsp_capabilities(hook_name)
                }
                lsp_hooks.append(lsp_info)
        
        return jsonify({
            'lsp_hooks': lsp_hooks,
            'total_lsp_hooks': len(lsp_hooks)
        })
    
    @_track_request
    def activate_lsp_hook(self, hook_name: str):
        """Activate LSP integration for a hook"""
        if not request.json:
            return jsonify({'error': 'JSON payload required'}), 400
        
        endpoint_config = request.json.get('endpoint_config', {})
        
        # Register endpoint first
        self.registry.lsp_bridge.register_lsp_endpoint(hook_name, endpoint_config)
        
        # Activate LSP
        success = self.registry.lsp_bridge.activate_lsp_hook(hook_name)
        
        if success:
            return jsonify({
                'message': f'LSP activated for hook {hook_name}',
                'hook_name': hook_name,
                'capabilities': self.registry.lsp_bridge.get_lsp_capabilities(hook_name)
            })
        else:
            return jsonify({'error': f'Failed to activate LSP for hook {hook_name}'}), 400
    
    @_track_request
    def deactivate_lsp_hook(self, hook_name: str):
        """Deactivate LSP integration for a hook"""
        success = self.registry.lsp_bridge.deactivate_lsp_hook(hook_name)
        
        if success:
            return jsonify({
                'message': f'LSP deactivated for hook {hook_name}',
                'hook_name': hook_name
            })
        else:
            return jsonify({'error': f'Failed to deactivate LSP for hook {hook_name}'}), 400
    
    @_track_request
    def get_lsp_capabilities(self, hook_name: str):
        """Get LSP capabilities for a hook"""
        capabilities = self.registry.lsp_bridge.get_lsp_capabilities(hook_name)
        
        return jsonify({
            'hook_name': hook_name,
            'capabilities': capabilities,
            'active': hook_name in self.registry.lsp_bridge.active_connections
        })
    
    # Queue and Execution Management Endpoints
    
    @_track_request
    def get_queue_status(self):
        """Get execution queue status"""
        return jsonify({
            'queue_size': self.registry.execution_queue.qsize(),
            'queue_empty': self.registry.execution_queue.empty(),
            'active_executions': len(self.registry.active_executions),
            'timestamp': datetime.now().isoformat()
        })
    
    @_track_request
    def get_active_executions(self):
        """Get currently active executions"""
        active = []
        
        for execution_id, context in self.registry.active_executions.items():
            active.append({
                'execution_id': execution_id,
                'hook_name': context.hook_name,
                'trigger': context.trigger,
                'priority': context.priority.name,
                'started_at': context.timestamp.isoformat(),
                'timeout_seconds': context.timeout_seconds
            })
        
        return jsonify({
            'active_executions': active,
            'total_active': len(active)
        })
    
    @_track_request
    def get_execution_status(self, execution_id: str):
        """Get status of a specific execution"""
        if execution_id in self.registry.active_executions:
            context = self.registry.active_executions[execution_id]
            return jsonify({
                'execution_id': execution_id,
                'status': 'running',
                'hook_name': context.hook_name,
                'trigger': context.trigger,
                'started_at': context.timestamp.isoformat(),
                'running_time_seconds': (datetime.now() - context.timestamp).total_seconds()
            })
        else:
            return jsonify({
                'execution_id': execution_id,
                'status': 'completed_or_not_found'
            })
    
    # Configuration Endpoints
    
    @_track_request
    def get_configuration(self):
        """Get current system configuration"""
        config = {
            'hooks_directory': str(self.registry.hooks_directory),
            'hot_reload_enabled': self.registry.hot_reload_enabled,
            'max_workers': self.registry.executor._max_workers,
            'performance_monitoring': self.registry.performance_monitor.monitoring_active,
            'lsp_bridge_active': len(self.registry.lsp_bridge.active_connections) > 0,
            'cache_file': str(self.registry.metadata_cache_file)
        }
        
        return jsonify({
            'configuration': config,
            'timestamp': datetime.now().isoformat()
        })
    
    @_track_request
    def update_configuration(self):
        """Update system configuration"""
        if not request.json:
            return jsonify({'error': 'JSON payload required'}), 400
        
        config = request.json
        updated = []
        
        # Update hot reload setting
        if 'hot_reload_enabled' in config:
            self.registry.hot_reload_enabled = config['hot_reload_enabled']
            updated.append('hot_reload_enabled')
        
        # Update performance monitoring
        if 'performance_monitoring' in config:
            self.registry.performance_monitor.monitoring_active = config['performance_monitoring']
            updated.append('performance_monitoring')
        
        return jsonify({
            'message': 'Configuration updated',
            'updated_settings': updated,
            'timestamp': datetime.now().isoformat()
        })
    
    # Utility Endpoints
    
    @_track_request
    def discover_hooks(self):
        """Discover new hooks in the hooks directory"""
        initial_count = len(self.registry.hooks)
        self.registry._discover_hooks()
        final_count = len(self.registry.hooks)
        
        return jsonify({
            'message': 'Hook discovery completed',
            'initial_hooks': initial_count,
            'final_hooks': final_count,
            'new_hooks_discovered': final_count - initial_count
        })
    
    @_track_request
    def validate_system(self):
        """Validate entire system health"""
        status = self.registry.get_system_status()
        dependency_issues = self.registry.dependency_resolver.validate_dependencies(self.registry.hooks)
        insights = self.registry.performance_monitor.get_performance_insights()
        
        # Count issues
        total_issues = len(dependency_issues) + len(insights)
        critical_issues = len([i for i in insights if i['type'].endswith('_warning')])
        
        system_health = 'healthy'
        if critical_issues > 0:
            system_health = 'critical'
        elif total_issues > 0:
            system_health = 'warning'
        
        return jsonify({
            'system_health': system_health,
            'total_issues': total_issues,
            'critical_issues': critical_issues,
            'dependency_issues': dependency_issues,
            'performance_insights': insights,
            'system_status': status
        })
    
    @_track_request
    def optimize_system(self):
        """Optimize system performance"""
        if not request.json:
            return jsonify({'error': 'JSON payload required'}), 400
        
        optimization_type = request.json.get('type', 'standard')
        optimizations_applied = []
        
        # Performance optimizations
        if optimization_type in ['standard', 'performance']:
            # Clear old performance data
            for hook_name in self.registry.hooks.keys():
                history = self.registry.performance_monitor.metrics_history[hook_name]
                if len(history) > 100:  # Keep only last 100 records
                    while len(history) > 100:
                        history.popleft()
                    optimizations_applied.append(f'Trimmed performance history for {hook_name}')
        
        # Memory optimizations
        if optimization_type in ['standard', 'memory']:
            # Force garbage collection and cache cleanup
            import gc
            gc.collect()
            optimizations_applied.append('Performed garbage collection')
        
        # Queue optimizations
        if optimization_type in ['standard', 'queue']:
            # Clear completed executions from active list
            completed = []
            for exec_id, context in list(self.registry.active_executions.items()):
                if (datetime.now() - context.timestamp).total_seconds() > context.timeout_seconds:
                    completed.append(exec_id)
            
            for exec_id in completed:
                del self.registry.active_executions[exec_id]
            
            if completed:
                optimizations_applied.append(f'Cleared {len(completed)} timed-out executions')
        
        return jsonify({
            'message': 'System optimization completed',
            'optimization_type': optimization_type,
            'optimizations_applied': optimizations_applied,
            'timestamp': datetime.now().isoformat()
        })
    
    # Server Management
    
    def start(self):
        """Start the API server"""
        if self.running:
            logger.warning("API server is already running")
            return
        
        self.running = True
        logger.info(f"Starting Hook Registry API server on {self.host}:{self.port}")
        
        try:
            self.app.run(
                host=self.host,
                port=self.port,
                debug=False,
                threaded=True,
                use_reloader=False
            )
        except Exception as e:
            logger.error(f"Failed to start API server: {e}")
            self.running = False
            raise
    
    def start_threaded(self):
        """Start the API server in a separate thread"""
        if self.server_thread and self.server_thread.is_alive():
            logger.warning("API server thread is already running")
            return
        
        self.server_thread = threading.Thread(target=self.start, daemon=True)
        self.server_thread.start()
        logger.info("API server started in background thread")
    
    def stop(self):
        """Stop the API server"""
        self.running = False
        logger.info("API server stopped")


# Global API instance
_api_instance = None

def get_hook_registry_api(host='localhost', port=8888) -> HookRegistryAPI:
    """Get or create the global API instance"""
    global _api_instance
    if _api_instance is None:
        _api_instance = HookRegistryAPI(host, port)
    return _api_instance


def start_api_server(host='localhost', port=8888, threaded=True):
    """Start the Hook Registry API server"""
    api = get_hook_registry_api(host, port)
    
    if threaded:
        api.start_threaded()
    else:
        api.start()
    
    return api


if __name__ == '__main__':
    # Start the API server when run directly
    import sys
    
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8888
    
    print(f"Starting Hook Registry API server...")
    print(f"Server will be available at http://{host}:{port}")
    print("Available endpoints:")
    print("  - /health - Health check")
    print("  - /status - System status")
    print("  - /api/hooks - Hook management")
    print("  - /api/triggers - Trigger management")
    print("  - /api/performance - Performance monitoring")
    print("  - /api/lsp - LSP integration")
    print("  - /api/queue - Execution queue")
    print("  - /api/config - Configuration")
    
    start_api_server(host, port, threaded=False)


# Export main classes and functions
__all__ = ['HookRegistryAPI', 'get_hook_registry_api', 'start_api_server']