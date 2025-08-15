#!/usr/bin/env python3
"""
MCP Manager - Core service orchestration and management

Original concept by @qdhenry (MIT License)
Enhanced for Claude Code Dev Stack by DevOps Agent

This module provides comprehensive MCP service management with:
- Service discovery and registration
- Load balancing and failover
- Health monitoring and metrics
- Cross-platform service integration
"""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
from urllib.parse import urlparse

import httpx
import psutil
import yaml
from pydantic import BaseModel, Field


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ServiceStatus(str, Enum):
    """Service status enumeration"""
    STARTING = "starting"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    UNKNOWN = "unknown"


class ServiceType(str, Enum):
    """MCP service type enumeration"""
    CORE = "core"
    PLAYWRIGHT = "playwright"
    GITHUB = "github"
    WEBSEARCH = "websearch"
    CUSTOM = "custom"
    PROXY = "proxy"
    GATEWAY = "gateway"


@dataclass
class ServiceMetrics:
    """Service performance metrics"""
    requests_total: int = 0
    requests_per_second: float = 0.0
    error_count: int = 0
    response_time_avg: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    uptime: timedelta = field(default_factory=lambda: timedelta(0))
    last_health_check: Optional[datetime] = None


@dataclass
class ServiceInstance:
    """Individual service instance configuration"""
    id: str
    name: str
    service_type: ServiceType
    host: str
    port: int
    path: str = "/"
    protocol: str = "http"
    status: ServiceStatus = ServiceStatus.UNKNOWN
    version: str = "unknown"
    description: str = ""
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    metrics: ServiceMetrics = field(default_factory=ServiceMetrics)
    last_seen: Optional[datetime] = None
    health_check_url: Optional[str] = None
    startup_command: Optional[str] = None
    
    @property
    def url(self) -> str:
        """Get the full service URL"""
        return f"{self.protocol}://{self.host}:{self.port}{self.path}"
    
    @property
    def is_healthy(self) -> bool:
        """Check if service is considered healthy"""
        if self.status != ServiceStatus.RUNNING:
            return False
        if self.last_seen is None:
            return False
        return (datetime.now() - self.last_seen) < timedelta(minutes=5)


class ServiceRegistry:
    """Service discovery and registration system"""
    
    def __init__(self):
        self.services: Dict[str, ServiceInstance] = {}
        self.service_groups: Dict[ServiceType, Set[str]] = {}
        self.listeners: List[callable] = []
        
    def register_service(self, service: ServiceInstance) -> bool:
        """Register a new service instance"""
        try:
            self.services[service.id] = service
            
            # Add to service group
            if service.service_type not in self.service_groups:
                self.service_groups[service.service_type] = set()
            self.service_groups[service.service_type].add(service.id)
            
            logger.info(f"Registered service: {service.name} ({service.id})")
            self._notify_listeners("service_registered", service)
            return True
            
        except Exception as e:
            logger.error(f"Failed to register service {service.id}: {e}")
            return False
    
    def unregister_service(self, service_id: str) -> bool:
        """Unregister a service instance"""
        try:
            if service_id not in self.services:
                return False
                
            service = self.services[service_id]
            
            # Remove from service group
            if service.service_type in self.service_groups:
                self.service_groups[service.service_type].discard(service_id)
                if not self.service_groups[service.service_type]:
                    del self.service_groups[service.service_type]
            
            del self.services[service_id]
            logger.info(f"Unregistered service: {service.name} ({service_id})")
            self._notify_listeners("service_unregistered", service)
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister service {service_id}: {e}")
            return False
    
    def get_service(self, service_id: str) -> Optional[ServiceInstance]:
        """Get service by ID"""
        return self.services.get(service_id)
    
    def get_services_by_type(self, service_type: ServiceType) -> List[ServiceInstance]:
        """Get all services of a specific type"""
        service_ids = self.service_groups.get(service_type, set())
        return [self.services[sid] for sid in service_ids if sid in self.services]
    
    def get_healthy_services(self, service_type: Optional[ServiceType] = None) -> List[ServiceInstance]:
        """Get all healthy services, optionally filtered by type"""
        services = self.services.values()
        if service_type:
            services = self.get_services_by_type(service_type)
        return [s for s in services if s.is_healthy]
    
    def add_listener(self, callback: callable):
        """Add event listener for service changes"""
        self.listeners.append(callback)
    
    def _notify_listeners(self, event: str, service: ServiceInstance):
        """Notify all listeners of service events"""
        for listener in self.listeners:
            try:
                listener(event, service)
            except Exception as e:
                logger.error(f"Listener error: {e}")


class LoadBalancer:
    """Load balancing algorithms for MCP services"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self.round_robin_counters: Dict[ServiceType, int] = {}
    
    def get_service_instance(self, service_type: ServiceType, algorithm: str = "round_robin") -> Optional[ServiceInstance]:
        """Get the best service instance using specified algorithm"""
        healthy_services = self.registry.get_healthy_services(service_type)
        
        if not healthy_services:
            logger.warning(f"No healthy services available for type: {service_type}")
            return None
        
        if algorithm == "round_robin":
            return self._round_robin(service_type, healthy_services)
        elif algorithm == "least_connections":
            return self._least_connections(healthy_services)
        elif algorithm == "response_time":
            return self._fastest_response(healthy_services)
        else:
            # Default to round robin
            return self._round_robin(service_type, healthy_services)
    
    def _round_robin(self, service_type: ServiceType, services: List[ServiceInstance]) -> ServiceInstance:
        """Round-robin load balancing"""
        if service_type not in self.round_robin_counters:
            self.round_robin_counters[service_type] = 0
        
        index = self.round_robin_counters[service_type] % len(services)
        self.round_robin_counters[service_type] += 1
        return services[index]
    
    def _least_connections(self, services: List[ServiceInstance]) -> ServiceInstance:
        """Least connections load balancing"""
        # For simplicity, use the service with lowest current requests
        return min(services, key=lambda s: s.metrics.requests_total)
    
    def _fastest_response(self, services: List[ServiceInstance]) -> ServiceInstance:
        """Fastest response time load balancing"""
        return min(services, key=lambda s: s.metrics.response_time_avg or float('inf'))


class HealthMonitor:
    """Health monitoring and metrics collection"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self.monitoring = False
        self.check_interval = 30  # seconds
        
    async def start_monitoring(self):
        """Start health monitoring loop"""
        self.monitoring = True
        logger.info("Health monitoring started")
        
        while self.monitoring:
            await self._check_all_services()
            await asyncio.sleep(self.check_interval)
    
    def stop_monitoring(self):
        """Stop health monitoring"""
        self.monitoring = False
        logger.info("Health monitoring stopped")
    
    async def _check_all_services(self):
        """Check health of all registered services"""
        tasks = []
        for service in self.registry.services.values():
            tasks.append(self._check_service_health(service))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_service_health(self, service: ServiceInstance):
        """Check individual service health"""
        try:
            health_url = service.health_check_url or f"{service.url}/health"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                start_time = time.time()
                response = await client.get(health_url)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    service.status = ServiceStatus.RUNNING
                    service.last_seen = datetime.now()
                    service.metrics.response_time_avg = response_time
                    
                    # Try to parse health data
                    try:
                        health_data = response.json()
                        if "metrics" in health_data:
                            self._update_metrics(service, health_data["metrics"])
                    except:
                        pass
                else:
                    service.status = ServiceStatus.ERROR
                    
        except Exception as e:
            logger.debug(f"Health check failed for {service.name}: {e}")
            service.status = ServiceStatus.ERROR
    
    def _update_metrics(self, service: ServiceInstance, metrics_data: Dict[str, Any]):
        """Update service metrics from health check data"""
        try:
            if "requests_total" in metrics_data:
                service.metrics.requests_total = metrics_data["requests_total"]
            if "error_count" in metrics_data:
                service.metrics.error_count = metrics_data["error_count"]
            if "cpu_usage" in metrics_data:
                service.metrics.cpu_usage = metrics_data["cpu_usage"]
            if "memory_usage" in metrics_data:
                service.metrics.memory_usage = metrics_data["memory_usage"]
        except Exception as e:
            logger.debug(f"Failed to update metrics for {service.name}: {e}")


class ServiceDiscovery:
    """Automatic service discovery"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
        self.discovery_enabled = True
        
    async def discover_services(self, config_paths: List[Path] = None):
        """Discover services from configuration files and network scanning"""
        if config_paths is None:
            config_paths = [
                Path("./mcp-services.yml"),
                Path("./config/mcp-services.yml"),
                Path("../config/mcp-services.yml")
            ]
        
        # Load from configuration files
        for config_path in config_paths:
            if config_path.exists():
                await self._load_from_config(config_path)
        
        # Network-based discovery
        await self._network_discovery()
    
    async def _load_from_config(self, config_path: Path):
        """Load service definitions from YAML config"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            services_config = config.get('services', [])
            for service_config in services_config:
                service = self._create_service_from_config(service_config)
                if service:
                    self.registry.register_service(service)
                    
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
    
    def _create_service_from_config(self, config: Dict[str, Any]) -> Optional[ServiceInstance]:
        """Create service instance from configuration"""
        try:
            return ServiceInstance(
                id=config.get('id', config['name'].replace(' ', '_').lower()),
                name=config['name'],
                service_type=ServiceType(config.get('type', 'custom')),
                host=config.get('host', 'localhost'),
                port=config['port'],
                path=config.get('path', '/'),
                protocol=config.get('protocol', 'http'),
                description=config.get('description', ''),
                tags=set(config.get('tags', [])),
                metadata=config.get('metadata', {}),
                health_check_url=config.get('health_check_url'),
                startup_command=config.get('startup_command')
            )
        except Exception as e:
            logger.error(f"Failed to create service from config: {e}")
            return None
    
    async def _network_discovery(self):
        """Discover services via network scanning"""
        # Common MCP service ports
        common_ports = [8080, 8081, 8082, 8083, 8084, 8090, 8091, 8092]
        
        for port in common_ports:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"http://localhost:{port}/mcp/info")
                    if response.status_code == 200:
                        service_info = response.json()
                        service = self._create_service_from_discovery(port, service_info)
                        if service:
                            self.registry.register_service(service)
            except:
                continue  # Port not available or not an MCP service
    
    def _create_service_from_discovery(self, port: int, info: Dict[str, Any]) -> Optional[ServiceInstance]:
        """Create service instance from network discovery"""
        try:
            return ServiceInstance(
                id=info.get('id', f"discovered_{port}"),
                name=info.get('name', f"MCP Service {port}"),
                service_type=ServiceType(info.get('type', 'custom')),
                host='localhost',
                port=port,
                path=info.get('path', '/'),
                description=info.get('description', 'Auto-discovered MCP service'),
                version=info.get('version', 'unknown'),
                tags=set(info.get('tags', []))
            )
        except Exception as e:
            logger.error(f"Failed to create service from discovery: {e}")
            return None


class MCPManager:
    """Main MCP Manager class orchestrating all components"""
    
    def __init__(self, config_file: Optional[Path] = None):
        self.registry = ServiceRegistry()
        self.load_balancer = LoadBalancer(self.registry)
        self.health_monitor = HealthMonitor(self.registry)
        self.service_discovery = ServiceDiscovery(self.registry)
        self.config_file = config_file or Path("mcp-manager.yml")
        self.running = False
        
        # Setup event listeners
        self.registry.add_listener(self._on_service_event)
    
    async def start(self):
        """Start the MCP Manager"""
        if self.running:
            logger.warning("MCP Manager is already running")
            return
        
        logger.info("Starting MCP Manager...")
        self.running = True
        
        # Load configuration
        await self._load_configuration()
        
        # Discover services
        await self.service_discovery.discover_services()
        
        # Start health monitoring
        monitoring_task = asyncio.create_task(self.health_monitor.start_monitoring())
        
        logger.info("MCP Manager started successfully")
        return monitoring_task
    
    async def stop(self):
        """Stop the MCP Manager"""
        if not self.running:
            return
        
        logger.info("Stopping MCP Manager...")
        self.running = False
        self.health_monitor.stop_monitoring()
        logger.info("MCP Manager stopped")
    
    async def _load_configuration(self):
        """Load manager configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = yaml.safe_load(f)
                
                # Configure health monitoring
                if 'health_check_interval' in config:
                    self.health_monitor.check_interval = config['health_check_interval']
                
                logger.info(f"Configuration loaded from {self.config_file}")
            except Exception as e:
                logger.error(f"Failed to load configuration: {e}")
    
    def _on_service_event(self, event: str, service: ServiceInstance):
        """Handle service registry events"""
        logger.info(f"Service event: {event} for {service.name}")
    
    # Public API methods
    
    def get_service_for_request(self, service_type: ServiceType, algorithm: str = "round_robin") -> Optional[ServiceInstance]:
        """Get the best service instance for a request"""
        return self.load_balancer.get_service_instance(service_type, algorithm)
    
    def get_all_services(self) -> List[ServiceInstance]:
        """Get all registered services"""
        return list(self.registry.services.values())
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get overall service status summary"""
        services = self.get_all_services()
        
        status_counts = {}
        for status in ServiceStatus:
            status_counts[status.value] = len([s for s in services if s.status == status])
        
        return {
            "total_services": len(services),
            "status_breakdown": status_counts,
            "healthy_services": len([s for s in services if s.is_healthy]),
            "service_types": list(set(s.service_type.value for s in services))
        }
    
    async def register_external_service(self, service_config: Dict[str, Any]) -> bool:
        """Register an external service manually"""
        try:
            service = ServiceInstance(
                id=service_config.get('id', service_config['name'].replace(' ', '_').lower()),
                name=service_config['name'],
                service_type=ServiceType(service_config.get('type', 'custom')),
                host=service_config.get('host', 'localhost'),
                port=service_config['port'],
                path=service_config.get('path', '/'),
                protocol=service_config.get('protocol', 'http'),
                description=service_config.get('description', ''),
                tags=set(service_config.get('tags', [])),
                metadata=service_config.get('metadata', {})
            )
            
            return self.registry.register_service(service)
        except Exception as e:
            logger.error(f"Failed to register external service: {e}")
            return False


# Example configuration
DEFAULT_MCP_CONFIG = {
    "health_check_interval": 30,
    "services": [
        {
            "name": "Playwright MCP",
            "type": "playwright",
            "host": "localhost",
            "port": 8080,
            "path": "/",
            "description": "Browser automation and testing service",
            "tags": ["automation", "testing", "browser"]
        },
        {
            "name": "GitHub MCP",
            "type": "github",
            "host": "localhost", 
            "port": 8081,
            "path": "/",
            "description": "GitHub repository management service",
            "tags": ["git", "repository", "github"]
        },
        {
            "name": "Web Search MCP",
            "type": "websearch",
            "host": "localhost",
            "port": 8082,
            "path": "/",
            "description": "Web search and scraping service",
            "tags": ["search", "web", "scraping"]
        }
    ]
}


if __name__ == "__main__":
    # Example usage
    async def main():
        manager = MCPManager()
        
        # Start the manager
        monitoring_task = await manager.start()
        
        try:
            # Let it run for a while
            await asyncio.sleep(10)
            
            # Get service status
            status = manager.get_service_status()
            print(f"Service Status: {json.dumps(status, indent=2)}")
            
            # Get a service for a request
            playwright_service = manager.get_service_for_request(ServiceType.PLAYWRIGHT)
            if playwright_service:
                print(f"Selected Playwright service: {playwright_service.url}")
            
        finally:
            await manager.stop()
            if monitoring_task and not monitoring_task.done():
                monitoring_task.cancel()
    
    # Run the example
    asyncio.run(main())