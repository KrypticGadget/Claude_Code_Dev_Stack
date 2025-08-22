#!/usr/bin/env python3
"""
Comprehensive Hook Registry System for V3.6.9
Provides metadata storage, trigger mapping, priority queues, dependency resolution,
LSP bridge interface, hot-reload capabilities, and performance monitoring
"""

import json
import time
import asyncio
import threading
import weakref
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Set, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
import heapq
import re
import inspect
import importlib.util
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class HookPriority(Enum):
    """Hook execution priority levels"""
    CRITICAL = 1      # System critical hooks
    HIGH = 2          # High priority user-facing hooks
    NORMAL = 3        # Standard hooks
    LOW = 4           # Background processing hooks
    MAINTENANCE = 5   # System maintenance hooks


class HookState(Enum):
    """Hook lifecycle states"""
    UNREGISTERED = "unregistered"
    REGISTERED = "registered"
    LOADED = "loaded"
    ACTIVE = "active"
    DISABLED = "disabled"
    ERROR = "error"
    RELOADING = "reloading"


class TriggerType(Enum):
    """Types of trigger events"""
    USER_PROMPT = "user_prompt"
    CLAUDE_RESPONSE = "claude_response"
    AGENT_ACTIVATION = "agent_activation"
    MCP_REQUEST = "mcp_request"
    FILE_CHANGE = "file_change"
    TIME_BASED = "time_based"
    SYSTEM_EVENT = "system_event"
    CUSTOM = "custom"


@dataclass
class HookMetadata:
    """Comprehensive hook metadata"""
    name: str
    file_path: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    priority: HookPriority = HookPriority.NORMAL
    triggers: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    provides: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    lsp_compatible: bool = False
    hot_reload_enabled: bool = True
    state: HookState = HookState.UNREGISTERED
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_executed: Optional[datetime] = None
    execution_count: int = 0
    average_execution_time: float = 0.0
    error_count: int = 0
    success_rate: float = 100.0


@dataclass
class ExecutionContext:
    """Hook execution context"""
    hook_name: str
    trigger: str
    data: Dict[str, Any]
    priority: HookPriority
    timestamp: datetime
    execution_id: str
    dependencies_resolved: bool = False
    timeout_seconds: float = 30.0


@dataclass
class PerformanceMetrics:
    """Performance tracking for hooks"""
    execution_time_ms: float
    memory_usage_mb: float
    cpu_percent: float
    success: bool
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class HookRegistryError(Exception):
    """Hook registry specific exceptions"""
    pass


class HookReloadHandler(FileSystemEventHandler):
    """File system handler for hot-reload capabilities"""
    
    def __init__(self, registry):
        self.registry = weakref.ref(registry)
        self.debounce_delay = 1.0  # seconds
        self.pending_reloads = {}
    
    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith('.py'):
            return
        
        registry = self.registry()
        if registry is None:
            return
        
        # Debounce file changes
        current_time = time.time()
        if event.src_path in self.pending_reloads:
            if current_time - self.pending_reloads[event.src_path] < self.debounce_delay:
                return
        
        self.pending_reloads[event.src_path] = current_time
        
        # Schedule reload
        threading.Timer(self.debounce_delay, 
                       lambda: registry.hot_reload_hook(event.src_path)).start()


class PriorityQueue:
    """Thread-safe priority queue for hook execution"""
    
    def __init__(self):
        self._queue = []
        self._index = 0
        self._lock = threading.RLock()
    
    def put(self, item: ExecutionContext):
        with self._lock:
            heapq.heappush(self._queue, (item.priority.value, self._index, item))
            self._index += 1
    
    def get(self) -> Optional[ExecutionContext]:
        with self._lock:
            if self._queue:
                return heapq.heappop(self._queue)[2]
            return None
    
    def qsize(self) -> int:
        with self._lock:
            return len(self._queue)
    
    def empty(self) -> bool:
        return self.qsize() == 0


class DependencyResolver:
    """Resolves hook dependencies and execution order"""
    
    def __init__(self):
        self.dependency_graph = defaultdict(set)
        self.provides_map = defaultdict(set)
    
    def add_hook(self, metadata: HookMetadata):
        """Add hook to dependency graph"""
        hook_name = metadata.name
        
        # Add dependencies
        for dep in metadata.dependencies:
            self.dependency_graph[hook_name].add(dep)
        
        # Add provides
        for provides in metadata.provides:
            self.provides_map[provides].add(hook_name)
    
    def remove_hook(self, hook_name: str):
        """Remove hook from dependency graph"""
        if hook_name in self.dependency_graph:
            del self.dependency_graph[hook_name]
        
        # Remove from provides
        for provides_set in self.provides_map.values():
            provides_set.discard(hook_name)
    
    def resolve_dependencies(self, hook_name: str, all_hooks: Dict[str, HookMetadata]) -> List[str]:
        """Resolve execution order for a hook and its dependencies"""
        visited = set()
        temp_visited = set()
        result = []
        
        def dfs(current_hook: str):
            if current_hook in temp_visited:
                raise HookRegistryError(f"Circular dependency detected involving {current_hook}")
            
            if current_hook in visited:
                return
            
            temp_visited.add(current_hook)
            
            # Resolve dependencies first
            if current_hook in all_hooks:
                for dep in all_hooks[current_hook].dependencies:
                    # Find hooks that provide this dependency
                    providers = self.provides_map.get(dep, set())
                    for provider in providers:
                        if provider in all_hooks and all_hooks[provider].state == HookState.ACTIVE:
                            dfs(provider)
            
            temp_visited.remove(current_hook)
            visited.add(current_hook)
            result.append(current_hook)
        
        dfs(hook_name)
        return result
    
    def validate_dependencies(self, all_hooks: Dict[str, HookMetadata]) -> List[str]:
        """Validate all hook dependencies"""
        issues = []
        
        for hook_name, metadata in all_hooks.items():
            for dep in metadata.dependencies:
                if dep not in self.provides_map or not self.provides_map[dep]:
                    issues.append(f"Hook '{hook_name}' depends on '{dep}' which is not provided by any active hook")
        
        return issues


class LSPHookBridge:
    """Bridge interface for Language Server Protocol integration"""
    
    def __init__(self, registry):
        self.registry = weakref.ref(registry)
        self.lsp_endpoints = {}
        self.active_connections = {}
    
    def register_lsp_endpoint(self, hook_name: str, endpoint_config: Dict[str, Any]):
        """Register LSP endpoint for a hook"""
        self.lsp_endpoints[hook_name] = {
            'config': endpoint_config,
            'registered_at': datetime.now(),
            'active': False
        }
    
    def activate_lsp_hook(self, hook_name: str) -> bool:
        """Activate LSP integration for a hook"""
        if hook_name not in self.lsp_endpoints:
            return False
        
        registry = self.registry()
        if registry is None or hook_name not in registry.hooks:
            return False
        
        hook_metadata = registry.hooks[hook_name]
        if not hook_metadata.lsp_compatible:
            return False
        
        # Create LSP connection configuration
        connection_config = {
            'hook_name': hook_name,
            'capabilities': self._get_hook_lsp_capabilities(hook_metadata),
            'endpoints': self.lsp_endpoints[hook_name]['config'],
            'activated_at': datetime.now()
        }
        
        self.active_connections[hook_name] = connection_config
        self.lsp_endpoints[hook_name]['active'] = True
        
        return True
    
    def deactivate_lsp_hook(self, hook_name: str) -> bool:
        """Deactivate LSP integration for a hook"""
        if hook_name in self.active_connections:
            del self.active_connections[hook_name]
        
        if hook_name in self.lsp_endpoints:
            self.lsp_endpoints[hook_name]['active'] = False
        
        return True
    
    def get_lsp_capabilities(self, hook_name: str) -> Dict[str, Any]:
        """Get LSP capabilities for a hook"""
        if hook_name not in self.active_connections:
            return {}
        
        return self.active_connections[hook_name]['capabilities']
    
    def _get_hook_lsp_capabilities(self, metadata: HookMetadata) -> Dict[str, Any]:
        """Extract LSP capabilities from hook metadata"""
        capabilities = {
            'textDocumentSync': True,
            'completionProvider': False,
            'hoverProvider': False,
            'definitionProvider': False,
            'codeActionProvider': False
        }
        
        # Analyze hook tags for LSP capabilities
        if 'completion' in metadata.tags:
            capabilities['completionProvider'] = {'triggerCharacters': ['@', '.']}
        
        if 'hover' in metadata.tags:
            capabilities['hoverProvider'] = True
        
        if 'navigation' in metadata.tags:
            capabilities['definitionProvider'] = True
        
        if 'refactor' in metadata.tags:
            capabilities['codeActionProvider'] = True
        
        return capabilities


class PerformanceMonitor:
    """Performance monitoring and metrics collection"""
    
    def __init__(self, max_history=1000):
        self.max_history = max_history
        self.metrics_history = defaultdict(lambda: deque(maxlen=max_history))
        self.aggregate_stats = defaultdict(dict)
        self.monitoring_active = True
        self.lock = threading.RLock()
    
    def record_execution(self, hook_name: str, metrics: PerformanceMetrics):
        """Record execution metrics for a hook"""
        if not self.monitoring_active:
            return
        
        with self.lock:
            self.metrics_history[hook_name].append(metrics)
            self._update_aggregate_stats(hook_name)
    
    def _update_aggregate_stats(self, hook_name: str):
        """Update aggregate statistics for a hook"""
        history = self.metrics_history[hook_name]
        if not history:
            return
        
        recent_metrics = list(history)[-100:]  # Last 100 executions
        
        execution_times = [m.execution_time_ms for m in recent_metrics]
        memory_usage = [m.memory_usage_mb for m in recent_metrics]
        successes = sum(1 for m in recent_metrics if m.success)
        
        self.aggregate_stats[hook_name] = {
            'total_executions': len(history),
            'recent_executions': len(recent_metrics),
            'avg_execution_time_ms': sum(execution_times) / len(execution_times),
            'max_execution_time_ms': max(execution_times),
            'min_execution_time_ms': min(execution_times),
            'avg_memory_usage_mb': sum(memory_usage) / len(memory_usage),
            'max_memory_usage_mb': max(memory_usage),
            'success_rate': (successes / len(recent_metrics)) * 100,
            'last_updated': datetime.now()
        }
    
    def get_hook_stats(self, hook_name: str) -> Dict[str, Any]:
        """Get performance statistics for a hook"""
        with self.lock:
            return self.aggregate_stats.get(hook_name, {})
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system-wide performance statistics"""
        with self.lock:
            total_executions = sum(len(history) for history in self.metrics_history.values())
            
            if total_executions == 0:
                return {'total_executions': 0}
            
            # Aggregate across all hooks
            all_recent_metrics = []
            for history in self.metrics_history.values():
                all_recent_metrics.extend(list(history)[-50:])  # Last 50 from each hook
            
            if not all_recent_metrics:
                return {'total_executions': total_executions}
            
            execution_times = [m.execution_time_ms for m in all_recent_metrics]
            memory_usage = [m.memory_usage_mb for m in all_recent_metrics]
            successes = sum(1 for m in all_recent_metrics if m.success)
            
            return {
                'total_executions': total_executions,
                'active_hooks': len(self.metrics_history),
                'system_avg_execution_time_ms': sum(execution_times) / len(execution_times),
                'system_max_execution_time_ms': max(execution_times),
                'system_avg_memory_usage_mb': sum(memory_usage) / len(memory_usage),
                'system_success_rate': (successes / len(all_recent_metrics)) * 100,
                'monitoring_active': self.monitoring_active,
                'last_updated': datetime.now()
            }
    
    def get_performance_insights(self) -> List[Dict[str, Any]]:
        """Get performance insights and recommendations"""
        insights = []
        
        with self.lock:
            for hook_name, stats in self.aggregate_stats.items():
                if stats['recent_executions'] < 10:
                    continue
                
                # Slow execution detection
                if stats['avg_execution_time_ms'] > 5000:  # 5 seconds
                    insights.append({
                        'type': 'performance_warning',
                        'hook_name': hook_name,
                        'issue': 'slow_execution',
                        'details': f"Average execution time: {stats['avg_execution_time_ms']:.1f}ms",
                        'recommendation': 'Consider optimizing hook logic or adding timeout'
                    })
                
                # High memory usage detection
                if stats['avg_memory_usage_mb'] > 100:  # 100 MB
                    insights.append({
                        'type': 'resource_warning',
                        'hook_name': hook_name,
                        'issue': 'high_memory_usage',
                        'details': f"Average memory usage: {stats['avg_memory_usage_mb']:.1f}MB",
                        'recommendation': 'Review memory allocation and cleanup'
                    })
                
                # Low success rate detection
                if stats['success_rate'] < 90:
                    insights.append({
                        'type': 'reliability_warning',
                        'hook_name': hook_name,
                        'issue': 'low_success_rate',
                        'details': f"Success rate: {stats['success_rate']:.1f}%",
                        'recommendation': 'Review error handling and dependencies'
                    })
        
        return insights


class HookRegistry:
    """Comprehensive hook registry system"""
    
    def __init__(self, hooks_directory: str = None):
        self.hooks_directory = Path(hooks_directory) if hooks_directory else Path(__file__).parent
        self.hooks: Dict[str, HookMetadata] = {}
        self.loaded_hooks: Dict[str, Any] = {}  # Actual hook objects
        self.trigger_mappings: Dict[str, List[str]] = defaultdict(list)
        self.execution_queue = PriorityQueue()
        self.dependency_resolver = DependencyResolver()
        self.lsp_bridge = LSPHookBridge(self)
        self.performance_monitor = PerformanceMonitor()
        
        # Hot reload
        self.hot_reload_enabled = True
        self.file_observer = Observer()
        self.reload_handler = HookReloadHandler(self)
        
        # Execution management
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.execution_lock = threading.RLock()
        self.active_executions: Dict[str, ExecutionContext] = {}
        
        # System state
        self.initialized = False
        self.metadata_cache_file = self.hooks_directory / "hook_registry_cache.json"
        
        # Initialize system
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize the hook registry system"""
        try:
            # Load cached metadata
            self._load_metadata_cache()
            
            # Discover and register hooks
            self._discover_hooks()
            
            # Setup hot reload
            if self.hot_reload_enabled:
                self._setup_hot_reload()
            
            # Build trigger mappings
            self._build_trigger_mappings()
            
            self.initialized = True
            print(f"Hook Registry initialized with {len(self.hooks)} hooks")
            
        except Exception as e:
            print(f"Failed to initialize Hook Registry: {e}")
            raise HookRegistryError(f"Initialization failed: {e}")
    
    def _discover_hooks(self):
        """Discover all Python hooks in the hooks directory"""
        hook_files = list(self.hooks_directory.glob("*.py"))
        
        for hook_file in hook_files:
            if hook_file.name.startswith('__') or hook_file.name == 'hook_registry.py':
                continue
            
            try:
                metadata = self._extract_hook_metadata(hook_file)
                if metadata:
                    self.register_hook(metadata)
            except Exception as e:
                print(f"Failed to discover hook {hook_file.name}: {e}")
    
    def _extract_hook_metadata(self, hook_file: Path) -> Optional[HookMetadata]:
        """Extract metadata from a hook file"""
        try:
            # Read the file
            content = hook_file.read_text(encoding='utf-8')
            
            # Extract docstring
            module_doc = self._extract_module_docstring(content)
            
            # Create basic metadata
            metadata = HookMetadata(
                name=hook_file.stem,
                file_path=str(hook_file),
                description=module_doc.get('description', ''),
                author=module_doc.get('author', ''),
                version=module_doc.get('version', '1.0.0')
            )
            
            # Parse metadata from docstring or comments
            metadata = self._parse_hook_metadata(content, metadata)
            
            # Analyze code for capabilities
            metadata = self._analyze_hook_capabilities(content, metadata)
            
            return metadata
            
        except Exception as e:
            print(f"Failed to extract metadata from {hook_file.name}: {e}")
            return None
    
    def _extract_module_docstring(self, content: str) -> Dict[str, str]:
        """Extract module docstring and parse metadata"""
        result = {'description': '', 'author': '', 'version': '1.0.0'}
        
        # Find module docstring
        match = re.search(r'"""(.*?)"""', content, re.DOTALL)
        if not match:
            match = re.search(r"'''(.*?)'''", content, re.DOTALL)
        
        if match:
            docstring = match.group(1).strip()
            lines = docstring.split('\n')
            
            if lines:
                result['description'] = lines[0].strip()
            
            # Look for author and version in docstring
            for line in lines:
                if line.strip().lower().startswith('author:'):
                    result['author'] = line.split(':', 1)[1].strip()
                elif line.strip().lower().startswith('version:'):
                    result['version'] = line.split(':', 1)[1].strip()
        
        return result
    
    def _parse_hook_metadata(self, content: str, metadata: HookMetadata) -> HookMetadata:
        """Parse metadata from hook content"""
        # Look for metadata comments
        metadata_patterns = {
            'priority': r'#\s*@priority:\s*(\w+)',
            'triggers': r'#\s*@triggers:\s*(.+)',
            'dependencies': r'#\s*@depends:\s*(.+)',
            'provides': r'#\s*@provides:\s*(.+)',
            'tags': r'#\s*@tags:\s*(.+)',
            'lsp_compatible': r'#\s*@lsp:\s*(true|false)',
            'hot_reload': r'#\s*@hot_reload:\s*(true|false)'
        }
        
        for key, pattern in metadata_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                value = matches[0].strip()
                
                if key == 'priority':
                    try:
                        metadata.priority = HookPriority[value.upper()]
                    except KeyError:
                        pass
                elif key in ['triggers', 'dependencies', 'provides', 'tags']:
                    setattr(metadata, key, [item.strip() for item in value.split(',')])
                elif key in ['lsp_compatible', 'hot_reload']:
                    setattr(metadata, key, value.lower() == 'true')
        
        return metadata
    
    def _analyze_hook_capabilities(self, content: str, metadata: HookMetadata) -> HookMetadata:
        """Analyze hook code to determine capabilities"""
        # Check for function patterns
        if 'def process_hook(' in content or 'def main(' in content:
            if 'process_hook' not in metadata.provides:
                metadata.provides.append('hook_processing')
        
        # Check for async patterns
        if 'async def' in content or 'await ' in content:
            metadata.tags.append('async')
        
        # Check for LSP patterns
        lsp_indicators = ['lsp', 'language_server', 'completion', 'hover', 'definition']
        if any(indicator in content.lower() for indicator in lsp_indicators):
            metadata.lsp_compatible = True
            metadata.tags.append('lsp')
        
        # Check for trigger patterns
        trigger_patterns = {
            TriggerType.USER_PROMPT: ['user_prompt', 'user_input', 'prompt'],
            TriggerType.CLAUDE_RESPONSE: ['claude_response', 'ai_response', 'response'],
            TriggerType.AGENT_ACTIVATION: ['agent_activation', 'agent', '@agent'],
            TriggerType.MCP_REQUEST: ['mcp_request', 'mcp', 'service'],
            TriggerType.FILE_CHANGE: ['file_change', 'file_modified', 'watch'],
            TriggerType.SYSTEM_EVENT: ['system_event', 'system', 'event']
        }
        
        for trigger_type, keywords in trigger_patterns.items():
            if any(keyword in content.lower() for keyword in keywords):
                if trigger_type.value not in metadata.triggers:
                    metadata.triggers.append(trigger_type.value)
        
        return metadata
    
    def register_hook(self, metadata: HookMetadata) -> bool:
        """Register a hook with the registry"""
        try:
            # Validate metadata
            if not metadata.name or not metadata.file_path:
                raise HookRegistryError("Hook name and file path are required")
            
            # Check if file exists
            if not Path(metadata.file_path).exists():
                raise HookRegistryError(f"Hook file not found: {metadata.file_path}")
            
            # Update state and timestamps
            metadata.state = HookState.REGISTERED
            metadata.updated_at = datetime.now()
            
            # Register with registry
            self.hooks[metadata.name] = metadata
            
            # Add to dependency resolver
            self.dependency_resolver.add_hook(metadata)
            
            # Update trigger mappings
            for trigger in metadata.triggers:
                if metadata.name not in self.trigger_mappings[trigger]:
                    self.trigger_mappings[trigger].append(metadata.name)
            
            # Save metadata cache
            self._save_metadata_cache()
            
            print(f"Registered hook: {metadata.name}")
            return True
            
        except Exception as e:
            print(f"Failed to register hook {metadata.name}: {e}")
            return False
    
    def load_hook(self, hook_name: str) -> bool:
        """Load a hook into memory"""
        if hook_name not in self.hooks:
            return False
        
        metadata = self.hooks[hook_name]
        
        try:
            # Load the module
            spec = importlib.util.spec_from_file_location(hook_name, metadata.file_path)
            if spec is None or spec.loader is None:
                raise HookRegistryError(f"Cannot load spec for {hook_name}")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Store the loaded module
            self.loaded_hooks[hook_name] = module
            
            # Update metadata
            metadata.state = HookState.LOADED
            metadata.updated_at = datetime.now()
            
            print(f"Loaded hook: {hook_name}")
            return True
            
        except Exception as e:
            metadata.state = HookState.ERROR
            metadata.error_count += 1
            print(f"Failed to load hook {hook_name}: {e}")
            return False
    
    def activate_hook(self, hook_name: str) -> bool:
        """Activate a hook for execution"""
        if hook_name not in self.hooks:
            return False
        
        # Load if not already loaded
        if hook_name not in self.loaded_hooks:
            if not self.load_hook(hook_name):
                return False
        
        metadata = self.hooks[hook_name]
        metadata.state = HookState.ACTIVE
        metadata.updated_at = datetime.now()
        
        print(f"Activated hook: {hook_name}")
        return True
    
    def deactivate_hook(self, hook_name: str) -> bool:
        """Deactivate a hook"""
        if hook_name not in self.hooks:
            return False
        
        metadata = self.hooks[hook_name]
        metadata.state = HookState.DISABLED
        metadata.updated_at = datetime.now()
        
        # Remove from active executions if running
        with self.execution_lock:
            if hook_name in self.active_executions:
                del self.active_executions[hook_name]
        
        print(f"Deactivated hook: {hook_name}")
        return True
    
    def hot_reload_hook(self, file_path: str):
        """Hot reload a hook when its file changes"""
        hook_name = None
        
        # Find the hook by file path
        for name, metadata in self.hooks.items():
            if Path(metadata.file_path).samefile(Path(file_path)):
                hook_name = name
                break
        
        if not hook_name or not self.hooks[hook_name].hot_reload_enabled:
            return
        
        print(f"Hot reloading hook: {hook_name}")
        
        try:
            metadata = self.hooks[hook_name]
            was_active = metadata.state == HookState.ACTIVE
            
            # Set reloading state
            metadata.state = HookState.RELOADING
            
            # Re-extract metadata
            updated_metadata = self._extract_hook_metadata(Path(file_path))
            if updated_metadata:
                # Preserve runtime state
                updated_metadata.execution_count = metadata.execution_count
                updated_metadata.last_executed = metadata.last_executed
                updated_metadata.error_count = metadata.error_count
                updated_metadata.success_rate = metadata.success_rate
                updated_metadata.created_at = metadata.created_at
                updated_metadata.state = HookState.REGISTERED
                
                # Update registry
                self.hooks[hook_name] = updated_metadata
                
                # Remove from loaded hooks to force reload
                if hook_name in self.loaded_hooks:
                    del self.loaded_hooks[hook_name]
                
                # Reactivate if was active
                if was_active:
                    self.activate_hook(hook_name)
                
                # Update dependency resolver
                self.dependency_resolver.remove_hook(hook_name)
                self.dependency_resolver.add_hook(updated_metadata)
                
                # Update trigger mappings
                self._build_trigger_mappings()
                
                print(f"Successfully reloaded hook: {hook_name}")
            
        except Exception as e:
            print(f"Failed to hot reload hook {hook_name}: {e}")
            if hook_name in self.hooks:
                self.hooks[hook_name].state = HookState.ERROR
    
    def execute_hook(self, hook_name: str, trigger: str, data: Dict[str, Any], 
                    priority: HookPriority = None, timeout: float = 30.0) -> str:
        """Execute a hook with the given parameters"""
        if hook_name not in self.hooks or self.hooks[hook_name].state != HookState.ACTIVE:
            raise HookRegistryError(f"Hook {hook_name} is not active")
        
        metadata = self.hooks[hook_name]
        execution_id = f"{hook_name}_{int(time.time() * 1000)}"
        
        # Determine priority
        if priority is None:
            priority = metadata.priority
        
        # Create execution context
        context = ExecutionContext(
            hook_name=hook_name,
            trigger=trigger,
            data=data,
            priority=priority,
            timestamp=datetime.now(),
            execution_id=execution_id,
            timeout_seconds=timeout
        )
        
        # Resolve dependencies
        try:
            dependency_order = self.dependency_resolver.resolve_dependencies(hook_name, self.hooks)
            context.dependencies_resolved = True
        except HookRegistryError as e:
            print(f"Dependency resolution failed for {hook_name}: {e}")
            context.dependencies_resolved = False
        
        # Add to execution queue
        self.execution_queue.put(context)
        
        # Execute immediately if possible
        self._process_execution_queue()
        
        return execution_id
    
    def execute_by_trigger(self, trigger: str, data: Dict[str, Any], 
                          priority: HookPriority = None) -> List[str]:
        """Execute all hooks registered for a trigger"""
        if trigger not in self.trigger_mappings:
            return []
        
        execution_ids = []
        hook_names = self.trigger_mappings[trigger]
        
        for hook_name in hook_names:
            if hook_name in self.hooks and self.hooks[hook_name].state == HookState.ACTIVE:
                try:
                    execution_id = self.execute_hook(hook_name, trigger, data, priority)
                    execution_ids.append(execution_id)
                except Exception as e:
                    print(f"Failed to execute hook {hook_name} for trigger {trigger}: {e}")
        
        return execution_ids
    
    def _process_execution_queue(self):
        """Process the execution queue"""
        while not self.execution_queue.empty():
            context = self.execution_queue.get()
            
            if context is None:
                break
            
            # Submit for execution
            future = self.executor.submit(self._execute_hook_context, context)
            
            # Don't wait for completion to allow parallel execution
    
    def _execute_hook_context(self, context: ExecutionContext) -> Dict[str, Any]:
        """Execute a hook in the given context"""
        hook_name = context.hook_name
        start_time = time.time()
        start_memory = self._get_memory_usage()
        start_cpu = psutil.cpu_percent()
        
        result = {
            'execution_id': context.execution_id,
            'hook_name': hook_name,
            'success': False,
            'result': None,
            'error': None,
            'execution_time_ms': 0,
            'memory_usage_mb': 0,
            'cpu_percent': 0
        }
        
        try:
            with self.execution_lock:
                self.active_executions[context.execution_id] = context
            
            # Get the loaded hook
            if hook_name not in self.loaded_hooks:
                raise HookRegistryError(f"Hook {hook_name} not loaded")
            
            hook_module = self.loaded_hooks[hook_name]
            
            # Find the hook function
            hook_function = None
            if hasattr(hook_module, 'process_hook'):
                hook_function = hook_module.process_hook
            elif hasattr(hook_module, 'main'):
                hook_function = hook_module.main
            else:
                raise HookRegistryError(f"No entry point found in hook {hook_name}")
            
            # Execute with timeout
            if asyncio.iscoroutinefunction(hook_function):
                # Async execution
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result['result'] = loop.run_until_complete(
                        asyncio.wait_for(
                            hook_function(context.trigger, context.data),
                            timeout=context.timeout_seconds
                        )
                    )
                finally:
                    loop.close()
            else:
                # Sync execution
                result['result'] = hook_function(context.trigger, context.data)
            
            result['success'] = True
            
            # Update metadata
            metadata = self.hooks[hook_name]
            metadata.execution_count += 1
            metadata.last_executed = datetime.now()
            metadata.average_execution_time = (
                (metadata.average_execution_time * (metadata.execution_count - 1) + 
                 (time.time() - start_time) * 1000) / metadata.execution_count
            )
            metadata.success_rate = (
                (metadata.success_rate * (metadata.execution_count - 1) + 100) / 
                metadata.execution_count
            )
            
        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            
            # Update error stats
            metadata = self.hooks[hook_name]
            metadata.error_count += 1
            metadata.success_rate = (
                (metadata.success_rate * metadata.execution_count + 0) / 
                (metadata.execution_count + 1)
            )
            
            print(f"Hook execution failed for {hook_name}: {e}")
        
        finally:
            # Calculate metrics
            end_time = time.time()
            end_memory = self._get_memory_usage()
            end_cpu = psutil.cpu_percent()
            
            result['execution_time_ms'] = (end_time - start_time) * 1000
            result['memory_usage_mb'] = max(0, end_memory - start_memory)
            result['cpu_percent'] = max(0, end_cpu - start_cpu)
            
            # Record performance metrics
            metrics = PerformanceMetrics(
                execution_time_ms=result['execution_time_ms'],
                memory_usage_mb=result['memory_usage_mb'],
                cpu_percent=result['cpu_percent'],
                success=result['success'],
                error_message=result.get('error')
            )
            self.performance_monitor.record_execution(hook_name, metrics)
            
            # Remove from active executions
            with self.execution_lock:
                if context.execution_id in self.active_executions:
                    del self.active_executions[context.execution_id]
        
        return result
    
    def get_hook_metadata(self, hook_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific hook"""
        if hook_name not in self.hooks:
            return None
        
        metadata = self.hooks[hook_name]
        result = asdict(metadata)
        
        # Add performance stats
        performance_stats = self.performance_monitor.get_hook_stats(hook_name)
        result['performance_stats'] = performance_stats
        
        # Add LSP info
        if metadata.lsp_compatible:
            result['lsp_capabilities'] = self.lsp_bridge.get_lsp_capabilities(hook_name)
        
        return result
    
    def list_hooks(self, filter_by: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """List all hooks with optional filtering"""
        hooks_list = []
        
        for hook_name, metadata in self.hooks.items():
            hook_dict = asdict(metadata)
            
            # Apply filters
            if filter_by:
                skip = False
                for key, value in filter_by.items():
                    if key in hook_dict:
                        if isinstance(value, list):
                            if not any(v in hook_dict[key] for v in value):
                                skip = True
                                break
                        else:
                            if hook_dict[key] != value:
                                skip = True
                                break
                
                if skip:
                    continue
            
            # Add performance stats
            performance_stats = self.performance_monitor.get_hook_stats(hook_name)
            hook_dict['performance_stats'] = performance_stats
            
            hooks_list.append(hook_dict)
        
        return hooks_list
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        # Get dependency issues
        dependency_issues = self.dependency_resolver.validate_dependencies(self.hooks)
        
        # Get performance insights
        performance_insights = self.performance_monitor.get_performance_insights()
        
        # Get system stats
        system_stats = self.performance_monitor.get_system_stats()
        
        # Count hooks by state
        state_counts = defaultdict(int)
        for metadata in self.hooks.values():
            state_counts[metadata.state.value] += 1
        
        return {
            'timestamp': datetime.now().isoformat(),
            'initialized': self.initialized,
            'total_hooks': len(self.hooks),
            'loaded_hooks': len(self.loaded_hooks),
            'active_executions': len(self.active_executions),
            'hooks_by_state': dict(state_counts),
            'dependency_issues': dependency_issues,
            'performance_insights': performance_insights,
            'system_performance': system_stats,
            'hot_reload_enabled': self.hot_reload_enabled,
            'lsp_endpoints': len(self.lsp_bridge.lsp_endpoints),
            'active_lsp_connections': len(self.lsp_bridge.active_connections),
            'queue_size': self.execution_queue.qsize()
        }
    
    def _setup_hot_reload(self):
        """Setup hot reload file watching"""
        if not self.hot_reload_enabled:
            return
        
        try:
            self.file_observer.schedule(
                self.reload_handler,
                str(self.hooks_directory),
                recursive=False
            )
            self.file_observer.start()
            print("Hot reload monitoring started")
        except Exception as e:
            print(f"Failed to setup hot reload: {e}")
    
    def _build_trigger_mappings(self):
        """Build trigger to hooks mappings"""
        self.trigger_mappings.clear()
        
        for hook_name, metadata in self.hooks.items():
            for trigger in metadata.triggers:
                if hook_name not in self.trigger_mappings[trigger]:
                    self.trigger_mappings[trigger].append(hook_name)
    
    def _load_metadata_cache(self):
        """Load cached hook metadata"""
        if not self.metadata_cache_file.exists():
            return
        
        try:
            with open(self.metadata_cache_file, 'r') as f:
                cache_data = json.load(f)
            
            for hook_data in cache_data.get('hooks', []):
                # Convert datetime strings back to datetime objects
                for date_field in ['created_at', 'updated_at', 'last_executed']:
                    if hook_data.get(date_field):
                        hook_data[date_field] = datetime.fromisoformat(hook_data[date_field])
                
                # Convert enums
                if hook_data.get('priority'):
                    hook_data['priority'] = HookPriority(hook_data['priority'])
                if hook_data.get('state'):
                    hook_data['state'] = HookState(hook_data['state'])
                
                metadata = HookMetadata(**hook_data)
                self.hooks[metadata.name] = metadata
            
            print(f"Loaded {len(self.hooks)} hooks from cache")
            
        except Exception as e:
            print(f"Failed to load metadata cache: {e}")
    
    def _save_metadata_cache(self):
        """Save hook metadata to cache"""
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'hooks': []
            }
            
            for metadata in self.hooks.values():
                hook_data = asdict(metadata)
                
                # Convert datetime objects to strings
                for date_field in ['created_at', 'updated_at', 'last_executed']:
                    if hook_data.get(date_field):
                        hook_data[date_field] = hook_data[date_field].isoformat()
                
                # Convert enums to values
                hook_data['priority'] = metadata.priority.value
                hook_data['state'] = metadata.state.value
                
                cache_data['hooks'].append(hook_data)
            
            with open(self.metadata_cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
        except Exception as e:
            print(f"Failed to save metadata cache: {e}")
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except:
            return 0.0
    
    def __del__(self):
        """Cleanup resources"""
        try:
            if hasattr(self, 'file_observer') and self.file_observer.is_alive():
                self.file_observer.stop()
                self.file_observer.join()
            
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=True)
        except:
            pass


# Global registry instance
_registry_instance = None

def get_hook_registry(hooks_directory: str = None) -> HookRegistry:
    """Get or create the global hook registry instance"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = HookRegistry(hooks_directory)
    return _registry_instance


# Export main classes and functions
__all__ = [
    'HookRegistry',
    'HookMetadata',
    'HookPriority',
    'HookState',
    'TriggerType',
    'ExecutionContext',
    'PerformanceMetrics',
    'HookRegistryError',
    'get_hook_registry'
]