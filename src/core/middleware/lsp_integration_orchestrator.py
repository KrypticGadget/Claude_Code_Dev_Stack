#!/usr/bin/env python3
"""
LSP Integration Orchestrator - Main Entry Point
Orchestrates the complete LSP-Hook bridge system with real-time code analysis,
IntelliSense enhancement, automated quality assessment, and performance optimization.
"""

import asyncio
import json
import time
import threading
import signal
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Set, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
import logging
import traceback

# Import our middleware components
from .lsp_hook_bridge import LSPHookBridge, LanguageServerConfig, LSPEventType
from .websocket_lsp_gateway import WebSocketLSPGateway, FilterRule, FilterAction, MessagePriority
from .automated_quality_hooks import AutomatedQualityAssessor, QualityReport
from .lsp_config_manager import LSPConfigManager, BridgeConfiguration, HealthStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntegrationState(Enum):
    """Integration system states"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    RECOVERING = "recovering"


@dataclass
class SystemMetrics:
    """System performance metrics"""
    uptime_seconds: float
    messages_processed: int
    hooks_executed: int
    quality_assessments: int
    errors_count: int
    average_response_time: float
    memory_usage_mb: float
    cpu_percent: float
    active_connections: int
    cache_hit_rate: float
    timestamp: datetime = field(default_factory=datetime.now)


class LSPIntegrationOrchestrator:
    """Main orchestrator for the LSP-Hook integration system"""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = config_dir
        self.state = IntegrationState.STOPPED
        self.start_time: Optional[datetime] = None
        
        # Core components
        self.config_manager: Optional[LSPConfigManager] = None
        self.lsp_bridge: Optional[LSPHookBridge] = None
        self.websocket_gateway: Optional[WebSocketLSPGateway] = None
        self.quality_assessor: Optional[AutomatedQualityAssessor] = None
        
        # System monitoring
        self.metrics = SystemMetrics(
            uptime_seconds=0,
            messages_processed=0,
            hooks_executed=0,
            quality_assessments=0,
            errors_count=0,
            average_response_time=0.0,
            memory_usage_mb=0.0,
            cpu_percent=0.0,
            active_connections=0,
            cache_hit_rate=0.0
        )
        
        # Event tracking
        self.event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self.error_history: deque = deque(maxlen=100)
        
        # Recovery system
        self.auto_recovery_enabled = True
        self.max_recovery_attempts = 3
        self.recovery_attempts = 0
        self.last_recovery_time: Optional[datetime] = None
        
        # Performance tracking
        self.response_times: deque = deque(maxlen=1000)
        self.processing_stats: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Shutdown handling
        self.shutdown_event = asyncio.Event()
        self._setup_signal_handlers()
        
        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        if hasattr(signal, 'SIGBREAK'):  # Windows
            signal.signal(signal.SIGBREAK, signal_handler)
    
    async def initialize(self) -> bool:
        """Initialize the integration system"""
        try:
            logger.info("Initializing LSP Integration Orchestrator...")
            self.state = IntegrationState.STARTING
            self.start_time = datetime.now()
            
            # Initialize configuration manager
            await self._initialize_config_manager()
            
            # Initialize components based on configuration
            config = self.config_manager.get_current_config()
            
            if config.enabled:
                await self._initialize_lsp_bridge(config)
                await self._initialize_websocket_gateway(config)
                await self._initialize_quality_assessor(config)
                
                # Setup inter-component communication
                await self._setup_component_integration()
                
                # Start background monitoring
                await self._start_background_monitoring()
                
                self.state = IntegrationState.RUNNING
                logger.info("LSP Integration Orchestrator initialized successfully")
                return True
            else:
                logger.info("LSP Integration is disabled in configuration")
                self.state = IntegrationState.STOPPED
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize LSP Integration Orchestrator: {e}")
            logger.error(traceback.format_exc())
            self.state = IntegrationState.ERROR
            self._record_error("initialization", str(e))
            
            if self.auto_recovery_enabled:
                await self._attempt_recovery()
            
            return False
    
    async def _initialize_config_manager(self) -> None:
        """Initialize configuration manager"""
        self.config_manager = LSPConfigManager(self.config_dir)
        
        # Add configuration change callback
        self.config_manager.add_change_callback(self._handle_config_change)
        
        # Start health monitoring
        await self.config_manager.start_health_monitoring()
        
        logger.info("Configuration manager initialized")
    
    async def _initialize_lsp_bridge(self, config: BridgeConfiguration) -> None:
        """Initialize LSP bridge"""
        self.lsp_bridge = LSPHookBridge()
        
        # Configure language servers from config
        for ls_mapping in config.language_servers:
            if ls_mapping.enabled:
                server_config = LanguageServerConfig(
                    name=ls_mapping.server_name,
                    command=ls_mapping.server_command,
                    root_uri=str(Path.cwd()),  # Use current working directory
                    file_extensions=ls_mapping.file_extensions,
                    capabilities=ls_mapping.capabilities,
                    auto_restart=True
                )
                await self.lsp_bridge.add_language_server(server_config)
        
        # Set config manager reference
        self.config_manager.set_lsp_bridge(self.lsp_bridge)
        
        # Start LSP bridge
        await self.lsp_bridge.start()
        
        logger.info("LSP bridge initialized")
    
    async def _initialize_websocket_gateway(self, config: BridgeConfiguration) -> None:
        """Initialize WebSocket gateway"""
        self.websocket_gateway = WebSocketLSPGateway(
            host=config.websocket_host,
            port=config.websocket_port
        )
        
        # Setup default filters
        await self._setup_websocket_filters(config)
        
        # Connect to LSP bridge
        if self.lsp_bridge:
            self.websocket_gateway.set_lsp_bridge(self.lsp_bridge)
        
        # Start WebSocket gateway
        await self.websocket_gateway.start()
        
        logger.info("WebSocket gateway initialized")
    
    async def _setup_websocket_filters(self, config: BridgeConfiguration) -> None:
        """Setup WebSocket message filters"""
        # Add global filters from configuration
        for filter_name in config.global_filters:
            if filter_name == "throttle_diagnostics":
                self.websocket_gateway.add_filter_rule(FilterRule(
                    name="throttle_diagnostics",
                    pattern="textDocument/publishDiagnostics",
                    action=FilterAction.THROTTLE,
                    throttle_limit=5,
                    throttle_window=1.0,
                    priority=10
                ))
            elif filter_name == "filter_test_files":
                def test_file_condition(message):
                    file_uri = message.params.get("uri", "")
                    return "/test/" not in file_uri and "_test" not in file_uri
                
                self.websocket_gateway.add_filter_rule(FilterRule(
                    name="filter_test_files",
                    pattern="",
                    action=FilterAction.BLOCK,
                    condition=test_file_condition,
                    priority=5
                ))
    
    async def _initialize_quality_assessor(self, config: BridgeConfiguration) -> None:
        """Initialize quality assessor"""
        self.quality_assessor = AutomatedQualityAssessor()
        
        logger.info("Quality assessor initialized")
    
    async def _setup_component_integration(self) -> None:
        """Setup integration between components"""
        # Connect LSP events to quality assessment
        if self.lsp_bridge and self.quality_assessor:
            # Add event handlers for LSP events that trigger quality assessment
            await self._setup_quality_assessment_triggers()
        
        # Connect WebSocket events to metrics
        if self.websocket_gateway:
            await self._setup_websocket_metrics()
        
        logger.info("Component integration setup complete")
    
    async def _setup_quality_assessment_triggers(self) -> None:
        """Setup triggers for automated quality assessment"""
        # This would integrate with the LSP bridge to trigger quality assessment
        # on relevant LSP events like diagnostics, file changes, etc.
        pass
    
    async def _setup_websocket_metrics(self) -> None:
        """Setup WebSocket metrics collection"""
        # This would collect metrics from WebSocket gateway
        pass
    
    async def _start_background_monitoring(self) -> None:
        """Start background monitoring tasks"""
        # Metrics collection task
        metrics_task = asyncio.create_task(self._metrics_collection_loop())
        self.background_tasks.append(metrics_task)
        
        # Health monitoring task
        health_task = asyncio.create_task(self._health_monitoring_loop())
        self.background_tasks.append(health_task)
        
        # Performance optimization task
        perf_task = asyncio.create_task(self._performance_optimization_loop())
        self.background_tasks.append(perf_task)
        
        logger.info("Background monitoring started")
    
    async def _metrics_collection_loop(self) -> None:
        """Background metrics collection"""
        while self.state == IntegrationState.RUNNING:
            try:
                await asyncio.sleep(10)  # Collect metrics every 10 seconds
                await self._collect_system_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                self._record_error("metrics_collection", str(e))
    
    async def _health_monitoring_loop(self) -> None:
        """Background health monitoring"""
        while self.state == IntegrationState.RUNNING:
            try:
                await asyncio.sleep(30)  # Health check every 30 seconds
                await self._perform_health_check()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                self._record_error("health_monitoring", str(e))
    
    async def _performance_optimization_loop(self) -> None:
        """Background performance optimization"""
        while self.state == IntegrationState.RUNNING:
            try:
                await asyncio.sleep(60)  # Optimize every minute
                await self._optimize_performance()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Performance optimization error: {e}")
                self._record_error("performance_optimization", str(e))
    
    async def _collect_system_metrics(self) -> None:
        """Collect system metrics"""
        try:
            import psutil
            process = psutil.Process()
            
            # Update metrics
            current_time = datetime.now()
            uptime = (current_time - self.start_time).total_seconds() if self.start_time else 0
            
            self.metrics.uptime_seconds = uptime
            self.metrics.memory_usage_mb = process.memory_info().rss / 1024 / 1024
            self.metrics.cpu_percent = process.cpu_percent()
            self.metrics.timestamp = current_time
            
            # Update response times
            if self.response_times:
                self.metrics.average_response_time = sum(self.response_times) / len(self.response_times)
            
            # Get component-specific metrics
            if self.websocket_gateway:
                gateway_status = self.websocket_gateway.get_status()
                self.metrics.active_connections = gateway_status.get("metrics", {}).get("current_clients", 0)
                self.metrics.messages_processed = gateway_status.get("metrics", {}).get("messages_processed", 0)
            
            if self.lsp_bridge:
                bridge_status = self.lsp_bridge.get_status()
                hook_stats = bridge_status.get("hook_executor_stats", {})
                self.metrics.hooks_executed = hook_stats.get("total_executions", 0)
            
            if self.quality_assessor:
                # Quality assessments would be tracked here
                pass
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    async def _perform_health_check(self) -> None:
        """Perform comprehensive health check"""
        try:
            health_issues = []
            
            # Check config manager health
            if self.config_manager:
                config_health = self.config_manager.get_health_status()
                if config_health.get("overall_status") == "critical":
                    health_issues.append("Configuration manager critical")
            
            # Check LSP bridge health
            if self.lsp_bridge:
                bridge_status = self.lsp_bridge.get_status()
                if not bridge_status.get("running", False):
                    health_issues.append("LSP bridge not running")
            
            # Check WebSocket gateway health
            if self.websocket_gateway:
                gateway_status = self.websocket_gateway.get_status()
                if not gateway_status.get("running", False):
                    health_issues.append("WebSocket gateway not running")
            
            # Trigger recovery if critical issues found
            if health_issues:
                logger.warning(f"Health check found issues: {health_issues}")
                if self.auto_recovery_enabled:
                    await self._attempt_recovery()
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            self._record_error("health_check", str(e))
    
    async def _optimize_performance(self) -> None:
        """Perform performance optimizations"""
        try:
            # Clear old metrics
            cutoff_time = datetime.now() - timedelta(hours=1)
            
            # Clear old response times
            while (self.response_times and 
                   len(self.response_times) > 0 and 
                   self.response_times[0] < cutoff_time.timestamp()):
                self.response_times.popleft()
            
            # Clear old processing stats
            for stat_queue in self.processing_stats.values():
                while stat_queue and stat_queue[0] < cutoff_time.timestamp():
                    stat_queue.popleft()
            
            # Optimize component caches
            if self.lsp_bridge and hasattr(self.lsp_bridge, 'cache_manager'):
                # Cache optimization would go here
                pass
            
            if self.websocket_gateway and hasattr(self.websocket_gateway, 'optimizer'):
                # WebSocket optimization would go here
                pass
            
        except Exception as e:
            logger.error(f"Performance optimization error: {e}")
    
    async def _handle_config_change(self, new_config: BridgeConfiguration) -> None:
        """Handle configuration changes"""
        try:
            logger.info("Configuration change detected, updating components...")
            
            # Update LSP bridge configuration
            if self.lsp_bridge:
                # This would update the bridge with new language server configs
                pass
            
            # Update WebSocket gateway configuration
            if self.websocket_gateway:
                # Update port, host, filters, etc.
                pass
            
            logger.info("Configuration update complete")
            
        except Exception as e:
            logger.error(f"Configuration change handling error: {e}")
            self._record_error("config_change", str(e))
    
    def _record_error(self, component: str, error: str) -> None:
        """Record error for tracking"""
        error_record = {
            "component": component,
            "error": error,
            "timestamp": datetime.now(),
            "state": self.state.value
        }
        self.error_history.append(error_record)
        self.metrics.errors_count += 1
    
    async def _attempt_recovery(self) -> bool:
        """Attempt system recovery"""
        if (self.last_recovery_time and 
            datetime.now() - self.last_recovery_time < timedelta(minutes=5)):
            logger.warning("Recovery attempted too recently, skipping")
            return False
        
        if self.recovery_attempts >= self.max_recovery_attempts:
            logger.error("Maximum recovery attempts reached")
            return False
        
        try:
            logger.info(f"Attempting system recovery (attempt {self.recovery_attempts + 1})")
            self.state = IntegrationState.RECOVERING
            self.last_recovery_time = datetime.now()
            self.recovery_attempts += 1
            
            # Stop all components
            await self._stop_components()
            
            # Wait a moment
            await asyncio.sleep(2)
            
            # Restart components
            config = self.config_manager.get_current_config()
            
            if config.enabled:
                await self._initialize_lsp_bridge(config)
                await self._initialize_websocket_gateway(config)
                await self._initialize_quality_assessor(config)
                await self._setup_component_integration()
                
                self.state = IntegrationState.RUNNING
                logger.info("System recovery successful")
                return True
            else:
                self.state = IntegrationState.STOPPED
                return False
                
        except Exception as e:
            logger.error(f"Recovery attempt failed: {e}")
            self.state = IntegrationState.ERROR
            return False
    
    async def _stop_components(self) -> None:
        """Stop all components"""
        # Stop background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        self.background_tasks.clear()
        
        # Stop components
        if self.websocket_gateway:
            await self.websocket_gateway.stop()
        
        if self.lsp_bridge:
            await self.lsp_bridge.stop()
        
        if self.config_manager:
            await self.config_manager.stop_health_monitoring()
    
    async def trigger_quality_assessment(self, file_path: str) -> Optional[QualityReport]:
        """Manually trigger quality assessment for a file"""
        if not self.quality_assessor:
            logger.warning("Quality assessor not available")
            return None
        
        try:
            start_time = time.time()
            report = self.quality_assessor.assess_file(file_path)
            response_time = time.time() - start_time
            
            self.response_times.append(response_time)
            self.metrics.quality_assessments += 1
            
            logger.info(f"Quality assessment completed for {file_path} in {response_time:.2f}s")
            return report
            
        except Exception as e:
            logger.error(f"Quality assessment failed for {file_path}: {e}")
            self._record_error("quality_assessment", str(e))
            return None
    
    async def get_project_quality_overview(self, project_path: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive project quality overview"""
        if not self.quality_assessor:
            logger.warning("Quality assessor not available")
            return None
        
        try:
            start_time = time.time()
            overview = self.quality_assessor.get_project_overview(project_path)
            response_time = time.time() - start_time
            
            self.response_times.append(response_time)
            
            logger.info(f"Project quality overview generated in {response_time:.2f}s")
            return overview
            
        except Exception as e:
            logger.error(f"Project quality overview failed: {e}")
            self._record_error("project_overview", str(e))
            return None
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            "state": self.state.value,
            "uptime_seconds": self.metrics.uptime_seconds,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "metrics": asdict(self.metrics),
            "recovery_attempts": self.recovery_attempts,
            "last_recovery": self.last_recovery_time.isoformat() if self.last_recovery_time else None,
            "error_count": len(self.error_history),
            "recent_errors": list(self.error_history)[-5:] if self.error_history else [],
            "components": {}
        }
        
        # Add component statuses
        if self.config_manager:
            status["components"]["config_manager"] = self.config_manager.get_health_status()
        
        if self.lsp_bridge:
            status["components"]["lsp_bridge"] = self.lsp_bridge.get_status()
        
        if self.websocket_gateway:
            status["components"]["websocket_gateway"] = self.websocket_gateway.get_status()
        
        if self.quality_assessor:
            status["components"]["quality_assessor"] = {
                "available": True,
                "assessments_cached": len(self.quality_assessor.assessment_history)
            }
        
        return status
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the integration system"""
        if self.state == IntegrationState.STOPPING:
            return
        
        logger.info("Shutting down LSP Integration Orchestrator...")
        self.state = IntegrationState.STOPPING
        
        try:
            # Stop components
            await self._stop_components()
            
            # Shutdown config manager
            if self.config_manager:
                await self.config_manager.shutdown()
            
            self.state = IntegrationState.STOPPED
            logger.info("LSP Integration Orchestrator shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            self.state = IntegrationState.ERROR
        
        finally:
            self.shutdown_event.set()
    
    async def run(self) -> None:
        """Run the integration system"""
        try:
            # Initialize
            if not await self.initialize():
                logger.error("Failed to initialize, exiting")
                return
            
            logger.info("LSP Integration Orchestrator is running")
            
            # Wait for shutdown signal
            await self.shutdown_event.wait()
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            logger.error(traceback.format_exc())
        finally:
            await self.shutdown()


# Main entry point function
async def main():
    """Main entry point for the LSP Integration Orchestrator"""
    orchestrator = LSPIntegrationOrchestrator()
    await orchestrator.run()


if __name__ == "__main__":
    asyncio.run(main())


# Export main classes
__all__ = [
    'LSPIntegrationOrchestrator',
    'IntegrationState',
    'SystemMetrics',
    'main'
]