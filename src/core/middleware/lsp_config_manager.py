#!/usr/bin/env python3
"""
LSP Configuration Manager - Dynamic Hook-LSP Mapping
Provides configuration management, hot-reloading, health monitoring,
and automatic recovery for the LSP-Hook bridge system.
"""

import asyncio
import json
import time
import threading
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Set, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
import logging
import weakref
import hashlib
import subprocess
import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigFormat(Enum):
    """Configuration file formats"""
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class LanguageServerMapping:
    """Mapping between language server and hooks"""
    server_name: str
    server_command: List[str]
    file_extensions: List[str]
    capabilities: Dict[str, Any]
    hook_mappings: Dict[str, List[str]]  # LSP method -> hook names
    filters: List[str] = field(default_factory=list)
    throttle_config: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    priority: int = 0


@dataclass
class HookConfiguration:
    """Hook-specific configuration"""
    hook_name: str
    enabled: bool = True
    triggers: List[str] = field(default_factory=list)
    filters: List[str] = field(default_factory=list)
    execution_mode: str = "async"
    timeout_seconds: float = 30.0
    retry_attempts: int = 3
    rate_limit: Optional[int] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BridgeConfiguration:
    """Main bridge configuration"""
    enabled: bool = True
    auto_discovery: bool = True
    health_check_interval: int = 30
    cache_enabled: bool = True
    cache_ttl: int = 300
    websocket_port: int = 8765
    websocket_host: str = "localhost"
    max_concurrent_hooks: int = 10
    log_level: str = "INFO"
    performance_monitoring: bool = True
    error_recovery: bool = True
    language_servers: List[LanguageServerMapping] = field(default_factory=list)
    hooks: List[HookConfiguration] = field(default_factory=list)
    global_filters: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthMetric:
    """Health monitoring metric"""
    name: str
    value: float
    status: HealthStatus
    message: str
    threshold: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)


class ConfigurationValidator:
    """Validates configuration settings"""
    
    def validate_bridge_config(self, config: BridgeConfiguration) -> List[str]:
        """Validate main bridge configuration"""
        errors = []
        
        # Basic validation
        if config.health_check_interval < 1:
            errors.append("health_check_interval must be at least 1 second")
        
        if config.cache_ttl < 10:
            errors.append("cache_ttl must be at least 10 seconds")
        
        if not (1024 <= config.websocket_port <= 65535):
            errors.append("websocket_port must be between 1024 and 65535")
        
        if config.max_concurrent_hooks < 1:
            errors.append("max_concurrent_hooks must be at least 1")
        
        # Validate language server mappings
        server_names = set()
        for ls_mapping in config.language_servers:
            validation_errors = self.validate_language_server_mapping(ls_mapping)
            errors.extend(validation_errors)
            
            if ls_mapping.server_name in server_names:
                errors.append(f"Duplicate language server name: {ls_mapping.server_name}")
            server_names.add(ls_mapping.server_name)
        
        # Validate hook configurations
        hook_names = set()
        for hook_config in config.hooks:
            validation_errors = self.validate_hook_config(hook_config)
            errors.extend(validation_errors)
            
            if hook_config.hook_name in hook_names:
                errors.append(f"Duplicate hook name: {hook_config.hook_name}")
            hook_names.add(hook_config.hook_name)
        
        return errors
    
    def validate_language_server_mapping(self, mapping: LanguageServerMapping) -> List[str]:
        """Validate language server mapping"""
        errors = []
        
        if not mapping.server_name:
            errors.append("Language server name cannot be empty")
        
        if not mapping.server_command:
            errors.append(f"Language server '{mapping.server_name}' must have a command")
        
        if not mapping.file_extensions:
            errors.append(f"Language server '{mapping.server_name}' must specify file extensions")
        
        # Validate file extensions format
        for ext in mapping.file_extensions:
            if not ext.startswith('.'):
                errors.append(f"File extension '{ext}' should start with a dot")
        
        # Validate hook mappings
        for method, hooks in mapping.hook_mappings.items():
            if not method:
                errors.append("LSP method cannot be empty")
            if not hooks:
                errors.append(f"Method '{method}' must map to at least one hook")
        
        return errors
    
    def validate_hook_config(self, config: HookConfiguration) -> List[str]:
        """Validate hook configuration"""
        errors = []
        
        if not config.hook_name:
            errors.append("Hook name cannot be empty")
        
        if config.timeout_seconds <= 0:
            errors.append(f"Hook '{config.hook_name}' timeout must be positive")
        
        if config.retry_attempts < 0:
            errors.append(f"Hook '{config.hook_name}' retry attempts cannot be negative")
        
        if config.rate_limit is not None and config.rate_limit <= 0:
            errors.append(f"Hook '{config.hook_name}' rate limit must be positive")
        
        valid_modes = ["sync", "async", "batched", "streaming"]
        if config.execution_mode not in valid_modes:
            errors.append(f"Hook '{config.hook_name}' execution mode must be one of: {valid_modes}")
        
        return errors


class ConfigurationFileWatcher(FileSystemEventHandler):
    """Watches configuration files for changes"""
    
    def __init__(self, config_manager):
        self.config_manager = weakref.ref(config_manager)
        self.debounce_delay = 1.0
        self.pending_changes = {}
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        config_manager = self.config_manager()
        if config_manager is None:
            return
        
        # Check if this is a watched config file
        if event.src_path not in config_manager.watched_files:
            return
        
        # Debounce changes
        current_time = time.time()
        if event.src_path in self.pending_changes:
            if current_time - self.pending_changes[event.src_path] < self.debounce_delay:
                return
        
        self.pending_changes[event.src_path] = current_time
        
        # Schedule reload
        threading.Timer(
            self.debounce_delay,
            lambda: asyncio.create_task(config_manager.reload_config_file(event.src_path))
        ).start()


class HealthMonitor:
    """Monitors system health and performance"""
    
    def __init__(self, config_manager):
        self.config_manager = weakref.ref(config_manager)
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.thresholds = {
            "memory_usage_mb": 500.0,
            "cpu_percent": 80.0,
            "error_rate": 0.1,
            "response_time_ms": 1000.0,
            "disk_usage_percent": 90.0
        }
        self.monitoring_enabled = True
        self._lock = threading.RLock()
    
    def collect_metrics(self) -> List[HealthMetric]:
        """Collect current health metrics"""
        metrics = []
        
        try:
            # System metrics
            process = psutil.Process()
            
            # Memory usage
            memory_mb = process.memory_info().rss / 1024 / 1024
            memory_status = self._get_status("memory_usage_mb", memory_mb)
            metrics.append(HealthMetric(
                name="memory_usage_mb",
                value=memory_mb,
                status=memory_status,
                message=f"Memory usage: {memory_mb:.1f} MB",
                threshold=self.thresholds.get("memory_usage_mb")
            ))
            
            # CPU usage
            cpu_percent = process.cpu_percent()
            cpu_status = self._get_status("cpu_percent", cpu_percent)
            metrics.append(HealthMetric(
                name="cpu_percent",
                value=cpu_percent,
                status=cpu_status,
                message=f"CPU usage: {cpu_percent:.1f}%",
                threshold=self.thresholds.get("cpu_percent")
            ))
            
            # Disk usage
            disk_usage = psutil.disk_usage('/').percent
            disk_status = self._get_status("disk_usage_percent", disk_usage)
            metrics.append(HealthMetric(
                name="disk_usage_percent",
                value=disk_usage,
                status=disk_status,
                message=f"Disk usage: {disk_usage:.1f}%",
                threshold=self.thresholds.get("disk_usage_percent")
            ))
            
            # Application-specific metrics
            config_manager = self.config_manager()
            if config_manager:
                # Configuration health
                config_health = self._check_configuration_health(config_manager)
                metrics.append(config_health)
                
                # LSP bridge health (if available)
                bridge_health = self._check_bridge_health(config_manager)
                if bridge_health:
                    metrics.append(bridge_health)
            
        except Exception as e:
            logger.error(f"Error collecting health metrics: {e}")
            metrics.append(HealthMetric(
                name="metrics_collection",
                value=0.0,
                status=HealthStatus.CRITICAL,
                message=f"Failed to collect metrics: {e}"
            ))
        
        # Store metrics in history
        with self._lock:
            for metric in metrics:
                self.metrics_history[metric.name].append(metric)
        
        return metrics
    
    def _get_status(self, metric_name: str, value: float) -> HealthStatus:
        """Determine status based on threshold"""
        threshold = self.thresholds.get(metric_name)
        if threshold is None:
            return HealthStatus.UNKNOWN
        
        if metric_name in ["memory_usage_mb", "cpu_percent", "disk_usage_percent", "response_time_ms"]:
            # Higher values are worse
            if value >= threshold:
                return HealthStatus.CRITICAL
            elif value >= threshold * 0.8:
                return HealthStatus.WARNING
            else:
                return HealthStatus.HEALTHY
        elif metric_name == "error_rate":
            # Higher error rates are worse
            if value >= threshold:
                return HealthStatus.CRITICAL
            elif value >= threshold * 0.5:
                return HealthStatus.WARNING
            else:
                return HealthStatus.HEALTHY
        
        return HealthStatus.UNKNOWN
    
    def _check_configuration_health(self, config_manager) -> HealthMetric:
        """Check configuration health"""
        try:
            config = config_manager.get_current_config()
            validator = ConfigurationValidator()
            errors = validator.validate_bridge_config(config)
            
            if errors:
                return HealthMetric(
                    name="configuration_health",
                    value=0.0,
                    status=HealthStatus.CRITICAL,
                    message=f"Configuration errors: {len(errors)} issues found"
                )
            else:
                return HealthMetric(
                    name="configuration_health",
                    value=1.0,
                    status=HealthStatus.HEALTHY,
                    message="Configuration is valid"
                )
        except Exception as e:
            return HealthMetric(
                name="configuration_health",
                value=0.0,
                status=HealthStatus.CRITICAL,
                message=f"Configuration check failed: {e}"
            )
    
    def _check_bridge_health(self, config_manager) -> Optional[HealthMetric]:
        """Check LSP bridge health"""
        try:
            if hasattr(config_manager, 'lsp_bridge') and config_manager.lsp_bridge:
                bridge = config_manager.lsp_bridge
                if hasattr(bridge, 'get_status'):
                    status = bridge.get_status()
                    running = status.get('running', False)
                    
                    if running:
                        return HealthMetric(
                            name="lsp_bridge_health",
                            value=1.0,
                            status=HealthStatus.HEALTHY,
                            message="LSP bridge is running"
                        )
                    else:
                        return HealthMetric(
                            name="lsp_bridge_health",
                            value=0.0,
                            status=HealthStatus.CRITICAL,
                            message="LSP bridge is not running"
                        )
        except Exception as e:
            return HealthMetric(
                name="lsp_bridge_health",
                value=0.0,
                status=HealthStatus.CRITICAL,
                message=f"Bridge health check failed: {e}"
            )
        
        return None
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary"""
        with self._lock:
            if not self.metrics_history:
                return {"status": "no_data", "metrics": []}
            
            latest_metrics = {}
            for metric_name, history in self.metrics_history.items():
                if history:
                    latest_metrics[metric_name] = history[-1]
            
            # Determine overall status
            statuses = [metric.status for metric in latest_metrics.values()]
            if HealthStatus.CRITICAL in statuses:
                overall_status = HealthStatus.CRITICAL
            elif HealthStatus.WARNING in statuses:
                overall_status = HealthStatus.WARNING
            elif all(s == HealthStatus.HEALTHY for s in statuses):
                overall_status = HealthStatus.HEALTHY
            else:
                overall_status = HealthStatus.UNKNOWN
            
            return {
                "overall_status": overall_status.value,
                "monitoring_enabled": self.monitoring_enabled,
                "metrics": {name: asdict(metric) for name, metric in latest_metrics.items()},
                "thresholds": self.thresholds,
                "timestamp": datetime.now().isoformat()
            }


class LSPConfigManager:
    """Main configuration management system"""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else Path.home() / ".claude" / "lsp"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.main_config_file = self.config_dir / "bridge_config.yaml"
        self.watched_files: Set[str] = set()
        
        # Current configuration
        self._current_config: Optional[BridgeConfiguration] = None
        self._config_lock = threading.RLock()
        
        # Hot-reload support
        self.file_observer: Optional[Observer] = None
        self.watcher = ConfigurationFileWatcher(self)
        self.hot_reload_enabled = True
        
        # Health monitoring
        self.health_monitor = HealthMonitor(self)
        self.health_monitor_task: Optional[asyncio.Task] = None
        
        # Change callbacks
        self.change_callbacks: List[Callable[[BridgeConfiguration], None]] = []
        
        # Validation
        self.validator = ConfigurationValidator()
        
        # LSP Bridge reference
        self.lsp_bridge: Optional[Any] = None
        
        # Initialize
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize configuration manager"""
        try:
            # Load or create default configuration
            if not self._load_main_config():
                self._create_default_config()
                self._load_main_config()
            
            # Start file watching
            if self.hot_reload_enabled:
                self._start_file_watching()
            
            logger.info("LSP Configuration Manager initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize configuration manager: {e}")
            raise
    
    def _load_main_config(self) -> bool:
        """Load main configuration file"""
        try:
            if not self.main_config_file.exists():
                return False
            
            content = self.main_config_file.read_text(encoding='utf-8')
            config_data = yaml.safe_load(content) if content.strip() else {}
            
            # Convert to dataclass
            config = self._dict_to_bridge_config(config_data)
            
            # Validate configuration
            errors = self.validator.validate_bridge_config(config)
            if errors:
                logger.warning(f"Configuration validation errors: {errors}")
                # Continue with potentially invalid config, but log warnings
            
            with self._config_lock:
                self._current_config = config
            
            # Add to watched files
            self.watched_files.add(str(self.main_config_file))
            
            logger.info(f"Loaded configuration from {self.main_config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return False
    
    def _create_default_config(self) -> None:
        """Create default configuration file"""
        default_config = BridgeConfiguration(
            enabled=True,
            auto_discovery=True,
            health_check_interval=30,
            cache_enabled=True,
            cache_ttl=300,
            websocket_port=8765,
            websocket_host="localhost",
            max_concurrent_hooks=10,
            log_level="INFO",
            performance_monitoring=True,
            error_recovery=True,
            language_servers=[
                LanguageServerMapping(
                    server_name="python",
                    server_command=["pylsp"],
                    file_extensions=[".py"],
                    capabilities={
                        "textDocument": {
                            "publishDiagnostics": True,
                            "hover": True,
                            "completion": True,
                            "definition": True
                        }
                    },
                    hook_mappings={
                        "textDocument/publishDiagnostics": ["quality_gate_hook", "audio_player_v3"],
                        "textDocument/hover": ["context_manager"],
                        "textDocument/completion": ["auto_formatter"],
                        "initialize": ["status_line_manager"]
                    },
                    throttle_config={
                        "diagnostics_per_second": 5,
                        "completion_per_second": 10
                    }
                )
            ],
            hooks=[
                HookConfiguration(
                    hook_name="quality_gate_hook",
                    enabled=True,
                    triggers=["textDocument/publishDiagnostics"],
                    execution_mode="async",
                    timeout_seconds=30.0,
                    retry_attempts=2
                ),
                HookConfiguration(
                    hook_name="audio_player_v3",
                    enabled=True,
                    triggers=["textDocument/publishDiagnostics", "initialize"],
                    execution_mode="async",
                    timeout_seconds=10.0,
                    rate_limit=5
                ),
                HookConfiguration(
                    hook_name="auto_formatter",
                    enabled=True,
                    triggers=["textDocument/completion"],
                    execution_mode="sync",
                    timeout_seconds=15.0
                )
            ],
            global_filters=[
                "throttle_diagnostics",
                "filter_test_files"
            ]
        )
        
        # Save to file
        self._save_config_to_file(default_config, self.main_config_file)
        logger.info(f"Created default configuration at {self.main_config_file}")
    
    def _dict_to_bridge_config(self, data: Dict[str, Any]) -> BridgeConfiguration:
        """Convert dictionary to BridgeConfiguration"""
        # Convert language servers
        language_servers = []
        for ls_data in data.get("language_servers", []):
            ls_mapping = LanguageServerMapping(**ls_data)
            language_servers.append(ls_mapping)
        
        # Convert hooks
        hooks = []
        for hook_data in data.get("hooks", []):
            hook_config = HookConfiguration(**hook_data)
            hooks.append(hook_config)
        
        # Create main config
        config_dict = {k: v for k, v in data.items() 
                      if k not in ["language_servers", "hooks"]}
        config_dict["language_servers"] = language_servers
        config_dict["hooks"] = hooks
        
        return BridgeConfiguration(**config_dict)
    
    def _save_config_to_file(self, config: BridgeConfiguration, file_path: Path) -> None:
        """Save configuration to file"""
        try:
            # Convert to dict for serialization
            config_dict = asdict(config)
            
            # Save as YAML
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            
            logger.info(f"Saved configuration to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise
    
    def _start_file_watching(self) -> None:
        """Start watching configuration files for changes"""
        try:
            self.file_observer = Observer()
            self.file_observer.schedule(
                self.watcher,
                str(self.config_dir),
                recursive=True
            )
            self.file_observer.start()
            logger.info("Configuration file watching started")
        except Exception as e:
            logger.error(f"Failed to start file watching: {e}")
    
    async def reload_config_file(self, file_path: str) -> bool:
        """Reload configuration from file"""
        try:
            logger.info(f"Reloading configuration from {file_path}")
            
            if file_path == str(self.main_config_file):
                if self._load_main_config():
                    await self._notify_config_change()
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to reload configuration from {file_path}: {e}")
            return False
    
    async def _notify_config_change(self) -> None:
        """Notify listeners of configuration changes"""
        config = self.get_current_config()
        
        # Call registered callbacks
        for callback in self.change_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(config)
                else:
                    callback(config)
            except Exception as e:
                logger.error(f"Configuration change callback error: {e}")
        
        # Update LSP bridge if available
        if self.lsp_bridge and hasattr(self.lsp_bridge, 'update_configuration'):
            try:
                await self.lsp_bridge.update_configuration(asdict(config))
            except Exception as e:
                logger.error(f"Failed to update LSP bridge configuration: {e}")
    
    def get_current_config(self) -> BridgeConfiguration:
        """Get current configuration"""
        with self._config_lock:
            if self._current_config is None:
                raise RuntimeError("Configuration not initialized")
            return self._current_config
    
    async def update_config(self, updates: Dict[str, Any]) -> bool:
        """Update configuration with new values"""
        try:
            with self._config_lock:
                current = self.get_current_config()
                
                # Create updated config
                current_dict = asdict(current)
                current_dict.update(updates)
                
                # Convert back to dataclass
                updated_config = self._dict_to_bridge_config(current_dict)
                
                # Validate
                errors = self.validator.validate_bridge_config(updated_config)
                if errors:
                    logger.error(f"Configuration update validation failed: {errors}")
                    return False
                
                # Save to file
                self._save_config_to_file(updated_config, self.main_config_file)
                
                # Update current config
                self._current_config = updated_config
            
            # Notify of changes
            await self._notify_config_change()
            
            logger.info("Configuration updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            return False
    
    def add_language_server(self, mapping: LanguageServerMapping) -> bool:
        """Add or update language server mapping"""
        try:
            config = self.get_current_config()
            
            # Check if server already exists
            for i, existing in enumerate(config.language_servers):
                if existing.server_name == mapping.server_name:
                    config.language_servers[i] = mapping
                    break
            else:
                config.language_servers.append(mapping)
            
            # Validate
            errors = self.validator.validate_language_server_mapping(mapping)
            if errors:
                logger.error(f"Language server mapping validation failed: {errors}")
                return False
            
            # Save
            self._save_config_to_file(config, self.main_config_file)
            
            with self._config_lock:
                self._current_config = config
            
            # Notify
            asyncio.create_task(self._notify_config_change())
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add language server: {e}")
            return False
    
    def remove_language_server(self, server_name: str) -> bool:
        """Remove language server mapping"""
        try:
            config = self.get_current_config()
            
            # Find and remove server
            for i, existing in enumerate(config.language_servers):
                if existing.server_name == server_name:
                    del config.language_servers[i]
                    break
            else:
                logger.warning(f"Language server '{server_name}' not found")
                return False
            
            # Save
            self._save_config_to_file(config, self.main_config_file)
            
            with self._config_lock:
                self._current_config = config
            
            # Notify
            asyncio.create_task(self._notify_config_change())
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove language server: {e}")
            return False
    
    def add_hook_config(self, hook_config: HookConfiguration) -> bool:
        """Add or update hook configuration"""
        try:
            config = self.get_current_config()
            
            # Validate
            errors = self.validator.validate_hook_config(hook_config)
            if errors:
                logger.error(f"Hook configuration validation failed: {errors}")
                return False
            
            # Check if hook already exists
            for i, existing in enumerate(config.hooks):
                if existing.hook_name == hook_config.hook_name:
                    config.hooks[i] = hook_config
                    break
            else:
                config.hooks.append(hook_config)
            
            # Save
            self._save_config_to_file(config, self.main_config_file)
            
            with self._config_lock:
                self._current_config = config
            
            # Notify
            asyncio.create_task(self._notify_config_change())
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add hook configuration: {e}")
            return False
    
    def remove_hook_config(self, hook_name: str) -> bool:
        """Remove hook configuration"""
        try:
            config = self.get_current_config()
            
            # Find and remove hook
            for i, existing in enumerate(config.hooks):
                if existing.hook_name == hook_name:
                    del config.hooks[i]
                    break
            else:
                logger.warning(f"Hook '{hook_name}' not found")
                return False
            
            # Save
            self._save_config_to_file(config, self.main_config_file)
            
            with self._config_lock:
                self._current_config = config
            
            # Notify
            asyncio.create_task(self._notify_config_change())
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove hook configuration: {e}")
            return False
    
    def add_change_callback(self, callback: Callable[[BridgeConfiguration], None]) -> None:
        """Add configuration change callback"""
        self.change_callbacks.append(callback)
    
    def remove_change_callback(self, callback: Callable[[BridgeConfiguration], None]) -> None:
        """Remove configuration change callback"""
        if callback in self.change_callbacks:
            self.change_callbacks.remove(callback)
    
    async def start_health_monitoring(self) -> None:
        """Start health monitoring"""
        if self.health_monitor_task:
            return
        
        config = self.get_current_config()
        if config.health_check_interval > 0:
            self.health_monitor_task = asyncio.create_task(self._health_monitoring_loop())
            logger.info("Health monitoring started")
    
    async def stop_health_monitoring(self) -> None:
        """Stop health monitoring"""
        if self.health_monitor_task:
            self.health_monitor_task.cancel()
            try:
                await self.health_monitor_task
            except asyncio.CancelledError:
                pass
            self.health_monitor_task = None
            logger.info("Health monitoring stopped")
    
    async def _health_monitoring_loop(self) -> None:
        """Health monitoring loop"""
        while True:
            try:
                config = self.get_current_config()
                await asyncio.sleep(config.health_check_interval)
                
                # Collect metrics
                metrics = self.health_monitor.collect_metrics()
                
                # Check for critical issues
                critical_metrics = [m for m in metrics if m.status == HealthStatus.CRITICAL]
                if critical_metrics:
                    logger.warning(f"Critical health issues detected: {[m.name for m in critical_metrics]}")
                    
                    # Trigger error recovery if enabled
                    if config.error_recovery:
                        await self._trigger_error_recovery(critical_metrics)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
    
    async def _trigger_error_recovery(self, critical_metrics: List[HealthMetric]) -> None:
        """Trigger error recovery procedures"""
        logger.info("Triggering error recovery procedures")
        
        for metric in critical_metrics:
            if metric.name == "lsp_bridge_health" and self.lsp_bridge:
                # Try to restart LSP bridge
                try:
                    logger.info("Attempting to restart LSP bridge")
                    await self.lsp_bridge.stop()
                    await asyncio.sleep(2)
                    await self.lsp_bridge.start()
                except Exception as e:
                    logger.error(f"Failed to restart LSP bridge: {e}")
            
            elif metric.name == "memory_usage_mb":
                # Memory cleanup
                try:
                    import gc
                    gc.collect()
                    logger.info("Performed garbage collection")
                except Exception as e:
                    logger.error(f"Failed to perform garbage collection: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        return self.health_monitor.get_health_summary()
    
    def set_lsp_bridge(self, bridge: Any) -> None:
        """Set LSP bridge reference"""
        self.lsp_bridge = bridge
    
    async def shutdown(self) -> None:
        """Shutdown configuration manager"""
        logger.info("Shutting down configuration manager")
        
        # Stop health monitoring
        await self.stop_health_monitoring()
        
        # Stop file watching
        if self.file_observer:
            self.file_observer.stop()
            self.file_observer.join()
        
        logger.info("Configuration manager shutdown complete")


# Export main classes
__all__ = [
    'LSPConfigManager',
    'BridgeConfiguration',
    'LanguageServerMapping',
    'HookConfiguration',
    'HealthMonitor',
    'HealthMetric',
    'HealthStatus',
    'ConfigurationValidator'
]