#!/usr/bin/env python3
"""
Comprehensive Hook Manager - V3.6.9
Main entry point that integrates all hook system components:
- Hook Registry (metadata storage and execution)
- Hook Configuration (settings and discovery)
- REST API (web interface)
- Performance Monitoring
- LSP Bridge
- Hot Reload System
"""

import asyncio
import json
import logging
import signal
import sys
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import psutil

# Import all hook system components
from .hook_registry import (
    get_hook_registry, 
    HookRegistry, 
    HookPriority, 
    HookState, 
    TriggerType,
    HookRegistryError
)
from .hook_registry_api import get_hook_registry_api, HookRegistryAPI
from .hook_config import get_hook_config_manager, HookConfigManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HookManager:
    """
    Comprehensive hook management system that integrates all components
    """
    
    def __init__(self, 
                 hooks_directory: str = None,
                 config_file: str = None,
                 api_host: str = 'localhost',
                 api_port: int = 8888,
                 auto_start: bool = True):
        
        # Configuration
        self.hooks_directory = Path(hooks_directory) if hooks_directory else Path(__file__).parent
        self.config_file = config_file
        self.api_host = api_host
        self.api_port = api_port
        
        # Core components
        self.registry: Optional[HookRegistry] = None
        self.config_manager: Optional[HookConfigManager] = None
        self.api_server: Optional[HookRegistryAPI] = None
        
        # State management
        self.initialized = False
        self.running = False
        self.start_time = datetime.now()
        
        # Monitoring
        self.stats = {
            'hooks_executed': 0,
            'api_requests': 0,
            'errors': 0,
            'uptime_seconds': 0,
            'last_heartbeat': datetime.now()
        }
        
        # Background tasks
        self.heartbeat_thread: Optional[threading.Thread] = None
        self.monitor_thread: Optional[threading.Thread] = None
        self.cleanup_thread: Optional[threading.Thread] = None
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {
            'hook_registered': [],
            'hook_activated': [],
            'hook_deactivated': [],
            'hook_executed': [],
            'hook_error': [],
            'system_started': [],
            'system_stopped': []
        }
        
        # Initialize system if requested
        if auto_start:
            self.initialize()
    
    def initialize(self):
        """Initialize the comprehensive hook management system"""
        if self.initialized:
            logger.warning("Hook manager already initialized")
            return
        
        logger.info("Initializing Comprehensive Hook Management System V3.6.9")
        
        try:
            # 1. Initialize configuration manager
            logger.info("Initializing configuration manager...")
            self.config_manager = get_hook_config_manager(
                str(self.hooks_directory), 
                self.config_file
            )
            logger.info(f"Configuration manager initialized with {len(self.config_manager.hook_configs)} hooks")
            
            # 2. Initialize hook registry
            logger.info("Initializing hook registry...")
            self.registry = get_hook_registry(str(self.hooks_directory))
            logger.info(f"Hook registry initialized with {len(self.registry.hooks)} hooks")
            
            # 3. Sync configurations with registry
            self._sync_config_with_registry()
            
            # 4. Initialize API server
            logger.info(f"Initializing API server on {self.api_host}:{self.api_port}...")
            self.api_server = get_hook_registry_api(self.api_host, self.api_port)
            
            # 5. Start background services
            self._start_background_services()
            
            # 6. Setup signal handlers
            self._setup_signal_handlers()
            
            self.initialized = True
            self.running = True
            
            logger.info("Hook Management System fully initialized")
            
            # Trigger system started event
            self._trigger_event('system_started', {'timestamp': datetime.now()})
            
        except Exception as e:
            logger.error(f"Failed to initialize hook management system: {e}")
            raise HookRegistryError(f"Initialization failed: {e}")
    
    def _sync_config_with_registry(self):
        """Sync configuration manager with hook registry"""
        logger.info("Syncing configurations with registry...")
        
        # Register hooks from configuration
        for hook_name, config in self.config_manager.hook_configs.items():
            if hook_name not in self.registry.hooks:
                # Try to register the hook
                file_path = config.custom_config.get('file_path')
                if file_path and Path(file_path).exists():
                    try:
                        # Extract metadata from file
                        metadata = self.registry._extract_hook_metadata(Path(file_path))
                        if metadata:
                            # Update metadata with config values
                            metadata.priority = HookPriority(min(5, max(1, config.priority)))
                            metadata.triggers = config.triggers[:]
                            metadata.dependencies = config.dependencies[:]
                            metadata.provides = config.provides[:]
                            metadata.tags = config.tags[:]
                            metadata.lsp_compatible = config.lsp_enabled
                            metadata.hot_reload_enabled = config.hot_reload
                            
                            # Register the hook
                            if self.registry.register_hook(metadata):
                                logger.info(f"Registered hook from config: {hook_name}")
                                
                                # Activate if enabled in config
                                if config.enabled:
                                    self.registry.activate_hook(hook_name)
                                    logger.info(f"Activated hook: {hook_name}")
                    except Exception as e:
                        logger.error(f"Failed to sync hook {hook_name}: {e}")
        
        # Update configurations with registry data
        for hook_name, metadata in self.registry.hooks.items():
            if hook_name not in self.config_manager.hook_configs:
                # Create config from metadata
                self.config_manager._create_default_hook_config({
                    'name': hook_name,
                    'file_path': metadata.file_path,
                    'description': metadata.description,
                    'version': metadata.version,
                    'author': metadata.author,
                    'triggers': metadata.triggers[:],
                    'dependencies': metadata.dependencies[:],
                    'provides': metadata.provides[:],
                    'tags': metadata.tags[:],
                    'lsp_compatible': metadata.lsp_compatible
                })
                logger.info(f"Created config for hook: {hook_name}")
        
        logger.info("Configuration sync completed")
    
    def _start_background_services(self):
        """Start background monitoring and maintenance services"""
        logger.info("Starting background services...")
        
        # Start API server in background thread
        if self.api_server:
            self.api_server.start_threaded()
            logger.info("API server started in background")
        
        # Start heartbeat service
        self.heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop, 
            daemon=True, 
            name="HookManager-Heartbeat"
        )
        self.heartbeat_thread.start()
        
        # Start monitoring service
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, 
            daemon=True, 
            name="HookManager-Monitor"
        )
        self.monitor_thread.start()
        
        # Start cleanup service
        self.cleanup_thread = threading.Thread(
            target=self._cleanup_loop, 
            daemon=True, 
            name="HookManager-Cleanup"
        )
        self.cleanup_thread.start()
        
        logger.info("Background services started")
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def _heartbeat_loop(self):
        """Background heartbeat loop"""
        while self.running:
            try:
                self.stats['uptime_seconds'] = (datetime.now() - self.start_time).total_seconds()
                self.stats['last_heartbeat'] = datetime.now()
                
                # Update system metrics
                if self.registry:
                    system_stats = self.registry.performance_monitor.get_system_stats()
                    self.stats.update({
                        'total_hooks': len(self.registry.hooks),
                        'active_hooks': len([h for h in self.registry.hooks.values() 
                                           if h.state == HookState.ACTIVE]),
                        'queue_size': self.registry.execution_queue.qsize(),
                        'active_executions': len(self.registry.active_executions)
                    })
                
                time.sleep(30)  # Heartbeat every 30 seconds
                
            except Exception as e:
                logger.error(f"Heartbeat loop error: {e}")
                time.sleep(30)
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.running:
            try:
                # Check system health
                self._check_system_health()
                
                # Check hook performance
                if self.registry:
                    insights = self.registry.performance_monitor.get_performance_insights()
                    for insight in insights:
                        if insight['type'].endswith('_warning'):
                            logger.warning(f"Performance issue in {insight['hook_name']}: {insight['issue']}")
                
                time.sleep(60)  # Monitor every minute
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(60)
    
    def _cleanup_loop(self):
        """Background cleanup loop"""
        while self.running:
            try:
                # Cleanup old performance data
                if self.registry:
                    for hook_name in list(self.registry.performance_monitor.metrics_history.keys()):
                        history = self.registry.performance_monitor.metrics_history[hook_name]
                        # Remove entries older than 24 hours
                        cutoff_time = datetime.now() - timedelta(hours=24)
                        while history and history[0].timestamp < cutoff_time:
                            history.popleft()
                
                # Cleanup stale executions
                if self.registry:
                    current_time = datetime.now()
                    stale_executions = []
                    
                    for exec_id, context in self.registry.active_executions.items():
                        if (current_time - context.timestamp).total_seconds() > context.timeout_seconds * 2:
                            stale_executions.append(exec_id)
                    
                    for exec_id in stale_executions:
                        del self.registry.active_executions[exec_id]
                        logger.warning(f"Cleaned up stale execution: {exec_id}")
                
                time.sleep(300)  # Cleanup every 5 minutes
                
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
                time.sleep(300)
    
    def _check_system_health(self):
        """Check overall system health"""
        try:
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 90:
                logger.warning(f"High CPU usage: {cpu_percent}%")
            
            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                logger.warning(f"High memory usage: {memory.percent}%")
            
            # Check registry health
            if self.registry:
                error_rate = 0
                if self.stats.get('hooks_executed', 0) > 0:
                    error_rate = (self.stats.get('errors', 0) / self.stats['hooks_executed']) * 100
                
                if error_rate > 10:  # More than 10% error rate
                    logger.warning(f"High hook error rate: {error_rate:.1f}%")
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
    
    # Public API Methods
    
    def register_hook_file(self, file_path: str) -> bool:
        """Register a hook from a file path"""
        if not self.registry:
            return False
        
        try:
            metadata = self.registry._extract_hook_metadata(Path(file_path))
            if metadata and self.registry.register_hook(metadata):
                # Update configuration
                if self.config_manager and metadata.name not in self.config_manager.hook_configs:
                    self.config_manager._create_default_hook_config({
                        'name': metadata.name,
                        'file_path': file_path,
                        'description': metadata.description,
                        'version': metadata.version,
                        'author': metadata.author,
                        'triggers': metadata.triggers[:],
                        'dependencies': metadata.dependencies[:],
                        'provides': metadata.provides[:],
                        'tags': metadata.tags[:],
                        'lsp_compatible': metadata.lsp_compatible
                    })
                
                self._trigger_event('hook_registered', {
                    'hook_name': metadata.name,
                    'file_path': file_path
                })
                
                logger.info(f"Successfully registered hook: {metadata.name}")
                return True
            
        except Exception as e:
            logger.error(f"Failed to register hook from {file_path}: {e}")
            self.stats['errors'] += 1
        
        return False
    
    def activate_hook(self, hook_name: str) -> bool:
        """Activate a hook"""
        if not self.registry:
            return False
        
        try:
            if self.registry.activate_hook(hook_name):
                # Update configuration
                if self.config_manager:
                    self.config_manager.update_hook_config(hook_name, {'enabled': True})
                
                self._trigger_event('hook_activated', {'hook_name': hook_name})
                logger.info(f"Successfully activated hook: {hook_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to activate hook {hook_name}: {e}")
            self.stats['errors'] += 1
        
        return False
    
    def deactivate_hook(self, hook_name: str) -> bool:
        """Deactivate a hook"""
        if not self.registry:
            return False
        
        try:
            if self.registry.deactivate_hook(hook_name):
                # Update configuration
                if self.config_manager:
                    self.config_manager.update_hook_config(hook_name, {'enabled': False})
                
                self._trigger_event('hook_deactivated', {'hook_name': hook_name})
                logger.info(f"Successfully deactivated hook: {hook_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to deactivate hook {hook_name}: {e}")
            self.stats['errors'] += 1
        
        return False
    
    def execute_hook(self, hook_name: str, trigger: str, data: Dict[str, Any], 
                    priority: HookPriority = None, timeout: float = 30.0) -> Optional[str]:
        """Execute a specific hook"""
        if not self.registry:
            return None
        
        try:
            execution_id = self.registry.execute_hook(hook_name, trigger, data, priority, timeout)
            self.stats['hooks_executed'] += 1
            
            self._trigger_event('hook_executed', {
                'hook_name': hook_name,
                'trigger': trigger,
                'execution_id': execution_id
            })
            
            logger.info(f"Executed hook {hook_name} with ID: {execution_id}")
            return execution_id
            
        except Exception as e:
            logger.error(f"Failed to execute hook {hook_name}: {e}")
            self.stats['errors'] += 1
            
            self._trigger_event('hook_error', {
                'hook_name': hook_name,
                'error': str(e)
            })
            
        return None
    
    def execute_by_trigger(self, trigger: str, data: Dict[str, Any], 
                          priority: HookPriority = None) -> List[str]:
        """Execute all hooks for a specific trigger"""
        if not self.registry:
            return []
        
        try:
            execution_ids = self.registry.execute_by_trigger(trigger, data, priority)
            self.stats['hooks_executed'] += len(execution_ids)
            
            logger.info(f"Executed {len(execution_ids)} hooks for trigger: {trigger}")
            return execution_ids
            
        except Exception as e:
            logger.error(f"Failed to execute hooks for trigger {trigger}: {e}")
            self.stats['errors'] += 1
            return []
    
    def get_hook_info(self, hook_name: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive information about a hook"""
        if not self.registry or hook_name not in self.registry.hooks:
            return None
        
        info = self.registry.get_hook_metadata(hook_name)
        
        # Add configuration info
        if self.config_manager and hook_name in self.config_manager.hook_configs:
            config = self.config_manager.hook_configs[hook_name]
            info['configuration'] = {
                'enabled': config.enabled,
                'priority': config.priority,
                'timeout': config.timeout,
                'retry_count': config.retry_count,
                'max_concurrent': config.max_concurrent,
                'hot_reload': config.hot_reload,
                'lsp_enabled': config.lsp_enabled,
                'custom_config': config.custom_config
            }
        
        return info
    
    def list_hooks(self, filter_criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """List hooks with optional filtering"""
        if not self.registry:
            return []
        
        hooks = self.registry.list_hooks(filter_criteria)
        
        # Add configuration info to each hook
        for hook in hooks:
            hook_name = hook['name']
            if self.config_manager and hook_name in self.config_manager.hook_configs:
                config = self.config_manager.hook_configs[hook_name]
                hook['configuration'] = {
                    'enabled': config.enabled,
                    'timeout': config.timeout,
                    'retry_count': config.retry_count,
                    'max_concurrent': config.max_concurrent
                }
        
        return hooks
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'initialized': self.initialized,
            'running': self.running,
            'uptime_seconds': self.stats['uptime_seconds'],
            'stats': self.stats.copy()
        }
        
        # Add registry status
        if self.registry:
            registry_status = self.registry.get_system_status()
            status['registry'] = registry_status
        
        # Add configuration status
        if self.config_manager:
            config_stats = self.config_manager.get_statistics()
            status['configuration'] = config_stats
        
        # Add API status
        if self.api_server:
            status['api'] = {
                'host': self.api_host,
                'port': self.api_port,
                'stats': self.api_server.api_stats
            }
        
        return status
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.registry:
            return {}
        
        system_stats = self.registry.performance_monitor.get_system_stats()
        insights = self.registry.performance_monitor.get_performance_insights()
        
        return {
            'system_performance': system_stats,
            'performance_insights': insights,
            'top_performing_hooks': self._get_top_performing_hooks(),
            'problematic_hooks': self._get_problematic_hooks()
        }
    
    def _get_top_performing_hooks(self) -> List[Dict[str, Any]]:
        """Get top performing hooks"""
        if not self.registry:
            return []
        
        hook_stats = []
        for hook_name in self.registry.hooks.keys():
            stats = self.registry.performance_monitor.get_hook_stats(hook_name)
            if stats and stats.get('recent_executions', 0) > 5:
                hook_stats.append({
                    'hook_name': hook_name,
                    'success_rate': stats.get('success_rate', 0),
                    'avg_execution_time': stats.get('avg_execution_time_ms', 0),
                    'executions': stats.get('recent_executions', 0)
                })
        
        # Sort by success rate and execution time
        hook_stats.sort(key=lambda x: (x['success_rate'], -x['avg_execution_time']), reverse=True)
        
        return hook_stats[:10]  # Top 10
    
    def _get_problematic_hooks(self) -> List[Dict[str, Any]]:
        """Get hooks with performance issues"""
        if not self.registry:
            return []
        
        problematic = []
        for hook_name in self.registry.hooks.keys():
            stats = self.registry.performance_monitor.get_hook_stats(hook_name)
            if stats and stats.get('recent_executions', 0) > 5:
                success_rate = stats.get('success_rate', 100)
                avg_time = stats.get('avg_execution_time_ms', 0)
                
                if success_rate < 90 or avg_time > 5000:  # Less than 90% success or >5s avg
                    problematic.append({
                        'hook_name': hook_name,
                        'success_rate': success_rate,
                        'avg_execution_time': avg_time,
                        'issues': []
                    })
                    
                    if success_rate < 90:
                        problematic[-1]['issues'].append('low_success_rate')
                    if avg_time > 5000:
                        problematic[-1]['issues'].append('slow_execution')
        
        return problematic
    
    def reload_hook(self, hook_name: str) -> bool:
        """Hot reload a specific hook"""
        if not self.registry or hook_name not in self.registry.hooks:
            return False
        
        try:
            metadata = self.registry.hooks[hook_name]
            self.registry.hot_reload_hook(metadata.file_path)
            logger.info(f"Successfully reloaded hook: {hook_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to reload hook {hook_name}: {e}")
            self.stats['errors'] += 1
            return False
    
    def reload_all_hooks(self) -> Dict[str, bool]:
        """Hot reload all hooks that support it"""
        if not self.registry:
            return {}
        
        results = {}
        
        for hook_name, metadata in self.registry.hooks.items():
            if metadata.hot_reload_enabled:
                results[hook_name] = self.reload_hook(hook_name)
            else:
                results[hook_name] = False  # Hot reload disabled
        
        successful = sum(1 for success in results.values() if success)
        logger.info(f"Reloaded {successful}/{len(results)} hooks")
        
        return results
    
    def validate_system(self) -> Dict[str, Any]:
        """Validate entire system"""
        validation_results = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'issues': [],
            'warnings': [],
            'registry_validation': {},
            'config_validation': {},
            'performance_validation': {}
        }
        
        # Validate registry
        if self.registry:
            dependency_issues = self.registry.dependency_resolver.validate_dependencies(self.registry.hooks)
            validation_results['registry_validation'] = {
                'dependency_issues': dependency_issues,
                'total_hooks': len(self.registry.hooks),
                'active_hooks': len([h for h in self.registry.hooks.values() if h.state == HookState.ACTIVE])
            }
            
            if dependency_issues:
                validation_results['issues'].extend(dependency_issues)
        
        # Validate configuration
        if self.config_manager:
            config_issues = self.config_manager.validate_configurations()
            validation_results['config_validation'] = {
                'config_issues': config_issues,
                'total_configs': len(self.config_manager.hook_configs)
            }
            
            if config_issues:
                validation_results['issues'].extend(config_issues)
        
        # Validate performance
        if self.registry:
            performance_insights = self.registry.performance_monitor.get_performance_insights()
            validation_results['performance_validation'] = {
                'performance_insights': performance_insights
            }
            
            for insight in performance_insights:
                if insight['type'].endswith('_warning'):
                    validation_results['warnings'].append(
                        f"{insight['hook_name']}: {insight['issue']} - {insight['recommendation']}"
                    )
        
        # Determine overall status
        if validation_results['issues']:
            validation_results['overall_status'] = 'error'
        elif validation_results['warnings']:
            validation_results['overall_status'] = 'warning'
        
        return validation_results
    
    def optimize_system(self) -> Dict[str, Any]:
        """Optimize system performance"""
        optimization_results = {
            'timestamp': datetime.now().isoformat(),
            'optimizations_applied': [],
            'performance_improvement': {}
        }
        
        try:
            # Clear old performance data
            if self.registry:
                for hook_name in list(self.registry.performance_monitor.metrics_history.keys()):
                    history = self.registry.performance_monitor.metrics_history[hook_name]
                    original_size = len(history)
                    
                    # Keep only last 100 entries per hook
                    while len(history) > 100:
                        history.popleft()
                    
                    if len(history) < original_size:
                        optimization_results['optimizations_applied'].append(
                            f"Trimmed performance history for {hook_name}: {original_size} -> {len(history)}"
                        )
            
            # Clean up stale executions
            if self.registry:
                stale_count = 0
                current_time = datetime.now()
                
                for exec_id in list(self.registry.active_executions.keys()):
                    context = self.registry.active_executions[exec_id]
                    if (current_time - context.timestamp).total_seconds() > context.timeout_seconds * 2:
                        del self.registry.active_executions[exec_id]
                        stale_count += 1
                
                if stale_count > 0:
                    optimization_results['optimizations_applied'].append(
                        f"Cleaned up {stale_count} stale executions"
                    )
            
            # Force garbage collection
            import gc
            collected = gc.collect()
            if collected > 0:
                optimization_results['optimizations_applied'].append(
                    f"Garbage collection freed {collected} objects"
                )
            
            logger.info(f"System optimization completed with {len(optimization_results['optimizations_applied'])} optimizations")
            
        except Exception as e:
            logger.error(f"System optimization failed: {e}")
            optimization_results['error'] = str(e)
        
        return optimization_results
    
    # Event System
    
    def add_event_handler(self, event_type: str, handler: Callable):
        """Add an event handler"""
        if event_type in self.event_handlers:
            self.event_handlers[event_type].append(handler)
        else:
            self.event_handlers[event_type] = [handler]
    
    def remove_event_handler(self, event_type: str, handler: Callable):
        """Remove an event handler"""
        if event_type in self.event_handlers and handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)
    
    def _trigger_event(self, event_type: str, data: Dict[str, Any]):
        """Trigger an event and call all handlers"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    logger.error(f"Event handler error for {event_type}: {e}")
    
    # Lifecycle Management
    
    def start(self):
        """Start the hook management system"""
        if not self.initialized:
            self.initialize()
        
        if self.running:
            logger.warning("Hook management system is already running")
            return
        
        self.running = True
        logger.info("Hook Management System started successfully")
    
    def stop(self):
        """Stop the hook management system"""
        if not self.running:
            logger.warning("Hook management system is not running")
            return
        
        logger.info("Stopping Hook Management System...")
        
        self.running = False
        
        # Stop API server
        if self.api_server:
            self.api_server.stop()
        
        # Stop background threads (they are daemon threads, so they'll stop automatically)
        
        # Clean shutdown of registry
        if self.registry:
            self.registry.executor.shutdown(wait=True, timeout=10)
        
        # Trigger system stopped event
        self._trigger_event('system_stopped', {'timestamp': datetime.now()})
        
        logger.info("Hook Management System stopped successfully")
    
    def restart(self):
        """Restart the hook management system"""
        logger.info("Restarting Hook Management System...")
        self.stop()
        time.sleep(2)  # Brief pause
        self.start()
    
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()


# Global hook manager instance
_hook_manager_instance = None

def get_hook_manager(hooks_directory: str = None,
                    config_file: str = None,
                    api_host: str = 'localhost',
                    api_port: int = 8888,
                    auto_start: bool = True) -> HookManager:
    """Get or create the global hook manager instance"""
    global _hook_manager_instance
    if _hook_manager_instance is None:
        _hook_manager_instance = HookManager(
            hooks_directory=hooks_directory,
            config_file=config_file,
            api_host=api_host,
            api_port=api_port,
            auto_start=auto_start
        )
    return _hook_manager_instance


# Command-line interface
def main():
    """Command-line interface for hook management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive Hook Management System V3.6.9")
    parser.add_argument('--hooks-dir', help='Directory containing hooks')
    parser.add_argument('--config-file', help='Configuration file path')
    parser.add_argument('--api-host', default='localhost', help='API server host')
    parser.add_argument('--api-port', type=int, default=8888, help='API server port')
    parser.add_argument('--no-api', action='store_true', help='Disable API server')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start the hook management system')
    start_parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    
    # Status command
    subparsers.add_parser('status', help='Show system status')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List hooks')
    list_parser.add_argument('--active-only', action='store_true', help='Show only active hooks')
    
    # Execute command
    execute_parser = subparsers.add_parser('execute', help='Execute hook')
    execute_parser.add_argument('hook_name', help='Hook to execute')
    execute_parser.add_argument('--trigger', default='cli', help='Trigger name')
    execute_parser.add_argument('--data', help='JSON data to pass to hook')
    
    # Validate command
    subparsers.add_parser('validate', help='Validate system')
    
    # Optimize command
    subparsers.add_parser('optimize', help='Optimize system performance')
    
    # Reload command
    reload_parser = subparsers.add_parser('reload', help='Reload hooks')
    reload_parser.add_argument('--hook', help='Specific hook to reload')
    reload_parser.add_argument('--all', action='store_true', help='Reload all hooks')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Create hook manager
    hook_manager = get_hook_manager(
        hooks_directory=args.hooks_dir,
        config_file=args.config_file,
        api_host=args.api_host,
        api_port=args.api_port if not args.no_api else None,
        auto_start=False
    )
    
    try:
        if args.command == 'start':
            hook_manager.start()
            
            if args.daemon:
                print(f"Hook Management System started as daemon")
                print(f"API available at http://{args.api_host}:{args.api_port}")
                print("Press Ctrl+C to stop")
                
                try:
                    while hook_manager.running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\nReceived interrupt, stopping...")
                    hook_manager.stop()
            else:
                print("Hook Management System started")
        
        elif args.command == 'status':
            if not hook_manager.initialized:
                hook_manager.initialize()
            
            status = hook_manager.get_system_status()
            print(json.dumps(status, indent=2, default=str))
        
        elif args.command == 'list':
            if not hook_manager.initialized:
                hook_manager.initialize()
            
            filter_criteria = {'state': HookState.ACTIVE} if args.active_only else None
            hooks = hook_manager.list_hooks(filter_criteria)
            
            print(f"Found {len(hooks)} hooks:")
            for hook in hooks:
                status = "✓" if hook.get('state') == 'active' else "○"
                print(f"  {status} {hook['name']} - {hook.get('description', 'No description')}")
        
        elif args.command == 'execute':
            if not hook_manager.initialized:
                hook_manager.initialize()
            
            data = {}
            if args.data:
                data = json.loads(args.data)
            
            execution_id = hook_manager.execute_hook(args.hook_name, args.trigger, data)
            if execution_id:
                print(f"Hook executed successfully. Execution ID: {execution_id}")
            else:
                print(f"Failed to execute hook: {args.hook_name}")
        
        elif args.command == 'validate':
            if not hook_manager.initialized:
                hook_manager.initialize()
            
            validation = hook_manager.validate_system()
            
            print(f"System Status: {validation['overall_status']}")
            if validation['issues']:
                print("Issues:")
                for issue in validation['issues']:
                    print(f"  ❌ {issue}")
            if validation['warnings']:
                print("Warnings:")
                for warning in validation['warnings']:
                    print(f"  ⚠️  {warning}")
            
            if not validation['issues'] and not validation['warnings']:
                print("✅ System is healthy")
        
        elif args.command == 'optimize':
            if not hook_manager.initialized:
                hook_manager.initialize()
            
            results = hook_manager.optimize_system()
            
            if results['optimizations_applied']:
                print("Optimizations applied:")
                for opt in results['optimizations_applied']:
                    print(f"  ✅ {opt}")
            else:
                print("No optimizations needed")
        
        elif args.command == 'reload':
            if not hook_manager.initialized:
                hook_manager.initialize()
            
            if args.hook:
                success = hook_manager.reload_hook(args.hook)
                print(f"Hook {args.hook} {'reloaded successfully' if success else 'failed to reload'}")
            elif args.all:
                results = hook_manager.reload_all_hooks()
                successful = sum(1 for success in results.values() if success)
                print(f"Reloaded {successful}/{len(results)} hooks")
            else:
                print("Specify --hook <name> or --all")
    
    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)
    
    finally:
        if hook_manager.running:
            hook_manager.stop()


if __name__ == '__main__':
    main()


# Export main classes and functions
__all__ = ['HookManager', 'get_hook_manager']