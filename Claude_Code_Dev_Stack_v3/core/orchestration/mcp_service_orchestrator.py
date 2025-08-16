#!/usr/bin/env python3
"""
MCP Service Orchestrator - PHASE 7.3
Unified service management for all MCP servers with load balancing, health monitoring, and failover mechanisms.

Integrates with existing v3_orchestrator.py to provide comprehensive middleware orchestration.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union, Callable
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
import threading
import uuid

import httpx
import psutil
import redis
from pydantic import BaseModel

# Import existing components
import sys
sys.path.append(str(Path(__file__).parent.parent / "hooks" / "hooks"))
try:
    from v3_orchestrator import ClaudeCodeV3Orchestrator, get_v3_orchestrator
except ImportError:
    # Fallback for testing
    ClaudeCodeV3Orchestrator = None
    get_v3_orchestrator = lambda: None

sys.path.append(str(Path(__file__).parent.parent.parent / "integrations" / "mcp-manager"))
try:
    from core.manager import MCPManager, ServiceInstance, ServiceType, ServiceStatus, ServiceMetrics
    from api.mcp_integration import app as mcp_api_app
except ImportError:
    # Fallback definitions
    class ServiceType(str, Enum):
        CORE = "core"
        PLAYWRIGHT = "playwright"
        GITHUB = "github"
        WEBSEARCH = "websearch"
        CUSTOM = "custom"
        PROXY = "proxy"
        GATEWAY = "gateway"
    
    class ServiceStatus(str, Enum):
        STARTING = "starting"
        RUNNING = "running"
        STOPPED = "stopped"
        ERROR = "error"
        UNKNOWN = "unknown"


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrchestrationStrategy(str, Enum):
    """Service orchestration strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    FASTEST_RESPONSE = "fastest_response"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    CONSISTENT_HASH = "consistent_hash"
    RESOURCE_AWARE = "resource_aware"


class FailoverPolicy(str, Enum):
    """Failover handling policies"""
    IMMEDIATE = "immediate"
    GRACEFUL = "graceful"
    CIRCUIT_BREAKER = "circuit_breaker"
    RETRY_WITH_BACKOFF = "retry_with_backoff"


@dataclass
class OrchestrationMetrics:
    """Orchestration performance metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    failover_count: int = 0
    load_balancing_efficiency: float = 0.0
    service_availability: float = 0.0
    circuit_breaker_trips: int = 0


@dataclass
class ServicePool:
    """Pool of services for a specific type"""
    service_type: ServiceType
    instances: List[ServiceInstance] = field(default_factory=list)
    strategy: OrchestrationStrategy = OrchestrationStrategy.ROUND_ROBIN
    failover_policy: FailoverPolicy = FailoverPolicy.GRACEFUL
    weights: Dict[str, float] = field(default_factory=dict)
    circuit_breaker_threshold: float = 0.5
    health_check_interval: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0


class CircuitBreaker:
    """Circuit breaker implementation for service resilience"""
    
    def __init__(self, failure_threshold: float = 0.5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        
    def call_allowed(self) -> bool:
        """Check if calls are allowed through the circuit breaker"""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        else:  # HALF_OPEN
            return True
    
    def record_success(self):
        """Record a successful call"""
        self.success_count += 1
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            self.failure_count = 0
    
    def record_failure(self):
        """Record a failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        total_calls = self.failure_count + self.success_count
        if total_calls > 0 and (self.failure_count / total_calls) >= self.failure_threshold:
            self.state = "OPEN"


class MessageQueue:
    """Async message queue for service coordination"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        self.subscribers = {}
        self.running = False
        
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            await asyncio.get_event_loop().run_in_executor(None, self.redis_client.ping)
            logger.info("Connected to Redis message queue")
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory queue: {e}")
            self.redis_client = None
    
    async def publish(self, channel: str, message: Dict[str, Any]):
        """Publish message to channel"""
        message_str = json.dumps({
            **message,
            "timestamp": datetime.utcnow().isoformat(),
            "id": str(uuid.uuid4())
        })
        
        if self.redis_client:
            try:
                await asyncio.get_event_loop().run_in_executor(
                    None, self.redis_client.publish, channel, message_str
                )
            except Exception as e:
                logger.error(f"Failed to publish message: {e}")
        
        # Also notify local subscribers
        if channel in self.subscribers:
            for callback in self.subscribers[channel]:
                try:
                    await callback(json.loads(message_str))
                except Exception as e:
                    logger.error(f"Subscriber error: {e}")
    
    def subscribe(self, channel: str, callback: Callable):
        """Subscribe to channel"""
        if channel not in self.subscribers:
            self.subscribers[channel] = []
        self.subscribers[channel].append(callback)


class ServiceHealthMonitor:
    """Enhanced health monitoring with predictive capabilities"""
    
    def __init__(self, orchestrator: 'MCPServiceOrchestrator'):
        self.orchestrator = orchestrator
        self.monitoring = False
        self.health_history = {}
        self.prediction_window = 300  # 5 minutes
        self.check_interval = 15  # seconds
        
    async def start_monitoring(self):
        """Start comprehensive health monitoring"""
        self.monitoring = True
        logger.info("Enhanced health monitoring started")
        
        while self.monitoring:
            await self._comprehensive_health_check()
            await asyncio.sleep(self.check_interval)
    
    def stop_monitoring(self):
        """Stop health monitoring"""
        self.monitoring = False
    
    async def _comprehensive_health_check(self):
        """Perform comprehensive health checks"""
        tasks = []
        
        for pool in self.orchestrator.service_pools.values():
            for service in pool.instances:
                tasks.append(self._check_service_health(service))
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            await self._analyze_health_trends(results)
    
    async def _check_service_health(self, service: ServiceInstance) -> Dict[str, Any]:
        """Enhanced service health check"""
        health_data = {
            "service_id": service.id,
            "timestamp": datetime.utcnow(),
            "status": "unknown",
            "response_time": None,
            "resource_usage": {},
            "errors": []
        }
        
        try:
            # HTTP health check
            health_url = service.health_check_url or f"{service.url}/health"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                start_time = time.time()
                response = await client.get(health_url)
                response_time = time.time() - start_time
                
                health_data["response_time"] = response_time
                
                if response.status_code == 200:
                    health_data["status"] = "healthy"
                    service.status = ServiceStatus.RUNNING
                    service.last_seen = datetime.now()
                    service.metrics.response_time_avg = response_time
                    
                    # Parse detailed health info
                    try:
                        health_info = response.json()
                        health_data.update(health_info)
                        
                        if "metrics" in health_info:
                            self._update_service_metrics(service, health_info["metrics"])
                    except:
                        pass
                else:
                    health_data["status"] = "unhealthy"
                    health_data["errors"].append(f"HTTP {response.status_code}")
                    service.status = ServiceStatus.ERROR
        
        except Exception as e:
            health_data["status"] = "error"
            health_data["errors"].append(str(e))
            service.status = ServiceStatus.ERROR
        
        # Store health history
        if service.id not in self.health_history:
            self.health_history[service.id] = []
        
        self.health_history[service.id].append(health_data)
        
        # Keep only recent history
        cutoff_time = datetime.utcnow() - timedelta(seconds=self.prediction_window)
        self.health_history[service.id] = [
            h for h in self.health_history[service.id] 
            if h["timestamp"] > cutoff_time
        ]
        
        return health_data
    
    def _update_service_metrics(self, service: ServiceInstance, metrics_data: Dict[str, Any]):
        """Update service metrics from health data"""
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
    
    async def _analyze_health_trends(self, health_results: List[Dict[str, Any]]):
        """Analyze health trends and predict issues"""
        for service_id, history in self.health_history.items():
            if len(history) < 3:
                continue
            
            # Calculate health score trend
            recent_scores = []
            for entry in history[-10:]:  # Last 10 checks
                score = 1.0 if entry["status"] == "healthy" else 0.0
                if entry["response_time"]:
                    # Penalize slow responses
                    score *= max(0.1, 1.0 - (entry["response_time"] / 10.0))
                recent_scores.append(score)
            
            if len(recent_scores) >= 3:
                trend = (recent_scores[-1] - recent_scores[0]) / len(recent_scores)
                avg_score = sum(recent_scores) / len(recent_scores)
                
                # Predict potential issues
                if trend < -0.1 and avg_score < 0.7:
                    await self.orchestrator.message_queue.publish(
                        "service_health_warning",
                        {
                            "service_id": service_id,
                            "trend": trend,
                            "avg_score": avg_score,
                            "prediction": "potential_degradation"
                        }
                    )


class LoadBalancerEngine:
    """Advanced load balancing engine with multiple strategies"""
    
    def __init__(self, orchestrator: 'MCPServiceOrchestrator'):
        self.orchestrator = orchestrator
        self.round_robin_counters = {}
        self.consistent_hash_ring = {}
        
    async def select_service(self, service_type: ServiceType, request_context: Dict[str, Any] = None) -> Optional[ServiceInstance]:
        """Select the best service instance using configured strategy"""
        pool = self.orchestrator.service_pools.get(service_type)
        if not pool:
            logger.warning(f"No service pool found for type: {service_type}")
            return None
        
        healthy_services = [s for s in pool.instances if s.is_healthy and s.status == ServiceStatus.RUNNING]
        
        if not healthy_services:
            logger.warning(f"No healthy services available for type: {service_type}")
            # Try to find any running service as fallback
            running_services = [s for s in pool.instances if s.status == ServiceStatus.RUNNING]
            if running_services:
                logger.info(f"Using degraded service for {service_type}")
                return running_services[0]
            return None
        
        # Apply circuit breaker check
        filtered_services = []
        for service in healthy_services:
            circuit_breaker = self.orchestrator.circuit_breakers.get(service.id)
            if not circuit_breaker or circuit_breaker.call_allowed():
                filtered_services.append(service)
        
        if not filtered_services:
            logger.warning(f"All services for {service_type} are circuit broken")
            return None
        
        # Select based on strategy
        if pool.strategy == OrchestrationStrategy.ROUND_ROBIN:
            return self._round_robin_select(service_type, filtered_services)
        elif pool.strategy == OrchestrationStrategy.LEAST_CONNECTIONS:
            return self._least_connections_select(filtered_services)
        elif pool.strategy == OrchestrationStrategy.FASTEST_RESPONSE:
            return self._fastest_response_select(filtered_services)
        elif pool.strategy == OrchestrationStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_select(service_type, filtered_services, pool.weights)
        elif pool.strategy == OrchestrationStrategy.CONSISTENT_HASH:
            return self._consistent_hash_select(service_type, filtered_services, request_context)
        elif pool.strategy == OrchestrationStrategy.RESOURCE_AWARE:
            return self._resource_aware_select(filtered_services)
        else:
            return self._round_robin_select(service_type, filtered_services)
    
    def _round_robin_select(self, service_type: ServiceType, services: List[ServiceInstance]) -> ServiceInstance:
        """Round-robin selection"""
        if service_type not in self.round_robin_counters:
            self.round_robin_counters[service_type] = 0
        
        index = self.round_robin_counters[service_type] % len(services)
        self.round_robin_counters[service_type] += 1
        return services[index]
    
    def _least_connections_select(self, services: List[ServiceInstance]) -> ServiceInstance:
        """Select service with least connections"""
        return min(services, key=lambda s: s.metrics.requests_total - s.metrics.error_count)
    
    def _fastest_response_select(self, services: List[ServiceInstance]) -> ServiceInstance:
        """Select service with fastest response time"""
        return min(services, key=lambda s: s.metrics.response_time_avg or float('inf'))
    
    def _weighted_round_robin_select(self, service_type: ServiceType, services: List[ServiceInstance], weights: Dict[str, float]) -> ServiceInstance:
        """Weighted round-robin selection"""
        if not weights:
            return self._round_robin_select(service_type, services)
        
        # Build weighted list
        weighted_services = []
        for service in services:
            weight = weights.get(service.id, 1.0)
            weighted_services.extend([service] * int(weight * 10))
        
        if not weighted_services:
            return services[0]
        
        if service_type not in self.round_robin_counters:
            self.round_robin_counters[service_type] = 0
        
        index = self.round_robin_counters[service_type] % len(weighted_services)
        self.round_robin_counters[service_type] += 1
        return weighted_services[index]
    
    def _consistent_hash_select(self, service_type: ServiceType, services: List[ServiceInstance], request_context: Dict[str, Any]) -> ServiceInstance:
        """Consistent hashing selection"""
        if not request_context or "session_id" not in request_context:
            return self._round_robin_select(service_type, services)
        
        session_id = request_context["session_id"]
        hash_value = hash(session_id) % len(services)
        return services[hash_value]
    
    def _resource_aware_select(self, services: List[ServiceInstance]) -> ServiceInstance:
        """Resource-aware selection based on CPU and memory usage"""
        def resource_score(service: ServiceInstance) -> float:
            cpu_score = 1.0 - (service.metrics.cpu_usage / 100.0)
            memory_score = 1.0 - (service.metrics.memory_usage / 100.0)
            response_score = 1.0 / (1.0 + service.metrics.response_time_avg)
            return (cpu_score + memory_score + response_score) / 3.0
        
        return max(services, key=resource_score)


class FailoverManager:
    """Failover and recovery management"""
    
    def __init__(self, orchestrator: 'MCPServiceOrchestrator'):
        self.orchestrator = orchestrator
        self.failover_history = {}
        
    async def handle_service_failure(self, failed_service: ServiceInstance, error: Exception) -> Optional[ServiceInstance]:
        """Handle service failure and attempt failover"""
        logger.warning(f"Service failure detected: {failed_service.name} - {error}")
        
        # Record failure
        circuit_breaker = self.orchestrator.circuit_breakers.get(failed_service.id)
        if circuit_breaker:
            circuit_breaker.record_failure()
        
        # Update metrics
        failed_service.metrics.error_count += 1
        self.orchestrator.metrics.failed_requests += 1
        self.orchestrator.metrics.failover_count += 1
        
        # Get service pool
        pool = None
        for service_pool in self.orchestrator.service_pools.values():
            if failed_service in service_pool.instances:
                pool = service_pool
                break
        
        if not pool:
            return None
        
        # Apply failover policy
        if pool.failover_policy == FailoverPolicy.IMMEDIATE:
            return await self._immediate_failover(pool, failed_service)
        elif pool.failover_policy == FailoverPolicy.GRACEFUL:
            return await self._graceful_failover(pool, failed_service)
        elif pool.failover_policy == FailoverPolicy.CIRCUIT_BREAKER:
            return await self._circuit_breaker_failover(pool, failed_service)
        elif pool.failover_policy == FailoverPolicy.RETRY_WITH_BACKOFF:
            return await self._retry_with_backoff(pool, failed_service)
        else:
            return await self._immediate_failover(pool, failed_service)
    
    async def _immediate_failover(self, pool: ServicePool, failed_service: ServiceInstance) -> Optional[ServiceInstance]:
        """Immediate failover to next available service"""
        healthy_services = [s for s in pool.instances if s.id != failed_service.id and s.is_healthy]
        
        if healthy_services:
            fallback_service = healthy_services[0]
            logger.info(f"Immediate failover from {failed_service.name} to {fallback_service.name}")
            
            await self.orchestrator.message_queue.publish(
                "service_failover",
                {
                    "failed_service": failed_service.id,
                    "fallback_service": fallback_service.id,
                    "policy": "immediate"
                }
            )
            
            return fallback_service
        
        return None
    
    async def _graceful_failover(self, pool: ServicePool, failed_service: ServiceInstance) -> Optional[ServiceInstance]:
        """Graceful failover with connection draining"""
        # Mark service as draining
        failed_service.status = ServiceStatus.ERROR
        
        # Find best alternative
        healthy_services = [s for s in pool.instances if s.id != failed_service.id and s.is_healthy]
        
        if healthy_services:
            # Select best service based on current load
            fallback_service = min(healthy_services, key=lambda s: s.metrics.requests_total)
            
            logger.info(f"Graceful failover from {failed_service.name} to {fallback_service.name}")
            
            await self.orchestrator.message_queue.publish(
                "service_failover",
                {
                    "failed_service": failed_service.id,
                    "fallback_service": fallback_service.id,
                    "policy": "graceful"
                }
            )
            
            return fallback_service
        
        return None
    
    async def _circuit_breaker_failover(self, pool: ServicePool, failed_service: ServiceInstance) -> Optional[ServiceInstance]:
        """Circuit breaker based failover"""
        circuit_breaker = self.orchestrator.circuit_breakers.get(failed_service.id)
        if circuit_breaker and circuit_breaker.state == "OPEN":
            logger.info(f"Circuit breaker OPEN for {failed_service.name}")
            
            # Find alternative services
            healthy_services = [s for s in pool.instances if s.id != failed_service.id and s.is_healthy]
            if healthy_services:
                return healthy_services[0]
        
        return None
    
    async def _retry_with_backoff(self, pool: ServicePool, failed_service: ServiceInstance) -> Optional[ServiceInstance]:
        """Retry with exponential backoff"""
        service_id = failed_service.id
        
        if service_id not in self.failover_history:
            self.failover_history[service_id] = {"retry_count": 0, "last_retry": None}
        
        history = self.failover_history[service_id]
        
        if history["retry_count"] < pool.max_retries:
            delay = pool.retry_delay * (2 ** history["retry_count"])
            logger.info(f"Retrying {failed_service.name} in {delay} seconds (attempt {history['retry_count'] + 1})")
            
            # Schedule retry
            asyncio.create_task(self._schedule_retry(failed_service, delay))
            
            history["retry_count"] += 1
            history["last_retry"] = datetime.utcnow()
            
            # Return alternative for immediate use
            healthy_services = [s for s in pool.instances if s.id != failed_service.id and s.is_healthy]
            if healthy_services:
                return healthy_services[0]
        
        return None
    
    async def _schedule_retry(self, service: ServiceInstance, delay: float):
        """Schedule service retry after delay"""
        await asyncio.sleep(delay)
        
        # Attempt to restore service
        try:
            # Simple health check
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{service.url}/health")
                if response.status_code == 200:
                    service.status = ServiceStatus.RUNNING
                    logger.info(f"Service {service.name} restored after retry")
                    
                    # Reset circuit breaker
                    circuit_breaker = self.orchestrator.circuit_breakers.get(service.id)
                    if circuit_breaker:
                        circuit_breaker.record_success()
                    
                    # Reset retry count
                    if service.id in self.failover_history:
                        self.failover_history[service.id]["retry_count"] = 0
        except Exception as e:
            logger.debug(f"Service {service.name} still unavailable: {e}")


class MCPServiceOrchestrator:
    """Main orchestrator for unified MCP service management"""
    
    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file or Path("mcp-orchestrator.yml")
        self.service_pools: Dict[ServiceType, ServicePool] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.metrics = OrchestrationMetrics()
        
        # Core components
        self.message_queue = MessageQueue()
        self.health_monitor = ServiceHealthMonitor(self)
        self.load_balancer = LoadBalancerEngine(self)
        self.failover_manager = FailoverManager(self)
        
        # Integration with v3 orchestrator
        self.v3_orchestrator = get_v3_orchestrator() if get_v3_orchestrator else None
        self.mcp_manager = None
        
        # Runtime state
        self.running = False
        self.monitoring_task = None
        
        # Threading for background tasks
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    async def initialize(self):
        """Initialize the orchestrator"""
        logger.info("Initializing MCP Service Orchestrator...")
        
        # Connect to message queue
        await self.message_queue.connect()
        
        # Initialize MCP Manager
        try:
            from core.manager import MCPManager
            self.mcp_manager = MCPManager()
            await self.mcp_manager.start()
            logger.info("MCP Manager integrated successfully")
        except Exception as e:
            logger.warning(f"MCP Manager integration failed: {e}")
        
        # Load configuration
        await self._load_configuration()
        
        # Setup message queue subscribers
        self._setup_message_handlers()
        
        # Discover and register services
        await self._discover_services()
        
        logger.info("MCP Service Orchestrator initialized successfully")
    
    async def start(self):
        """Start the orchestrator"""
        if self.running:
            logger.warning("Orchestrator is already running")
            return
        
        await self.initialize()
        self.running = True
        
        # Start health monitoring
        self.monitoring_task = asyncio.create_task(self.health_monitor.start_monitoring())
        
        # Integrate with v3 orchestrator
        if self.v3_orchestrator:
            logger.info("Integrating with v3 orchestrator")
            # Register as a component in v3 orchestrator
            self.v3_orchestrator.system_state["components"]["mcp_orchestrator"] = True
        
        logger.info("MCP Service Orchestrator started successfully")
    
    async def stop(self):
        """Stop the orchestrator"""
        if not self.running:
            return
        
        logger.info("Stopping MCP Service Orchestrator...")
        self.running = False
        
        # Stop health monitoring
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        self.health_monitor.stop_monitoring()
        
        # Stop MCP Manager
        if self.mcp_manager:
            await self.mcp_manager.stop()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("MCP Service Orchestrator stopped")
    
    async def _load_configuration(self):
        """Load orchestrator configuration"""
        if self.config_file.exists():
            try:
                import yaml
                with open(self.config_file, 'r') as f:
                    config = yaml.safe_load(f)
                
                # Load service pools configuration
                pools_config = config.get('service_pools', {})
                for service_type_str, pool_config in pools_config.items():
                    try:
                        service_type = ServiceType(service_type_str)
                        pool = ServicePool(
                            service_type=service_type,
                            strategy=OrchestrationStrategy(pool_config.get('strategy', 'round_robin')),
                            failover_policy=FailoverPolicy(pool_config.get('failover_policy', 'graceful')),
                            weights=pool_config.get('weights', {}),
                            circuit_breaker_threshold=pool_config.get('circuit_breaker_threshold', 0.5),
                            health_check_interval=pool_config.get('health_check_interval', 30),
                            max_retries=pool_config.get('max_retries', 3),
                            retry_delay=pool_config.get('retry_delay', 1.0)
                        )
                        self.service_pools[service_type] = pool
                    except ValueError as e:
                        logger.error(f"Invalid service type or strategy in config: {e}")
                
                # Configure health monitoring
                if 'health_monitoring' in config:
                    health_config = config['health_monitoring']
                    self.health_monitor.check_interval = health_config.get('check_interval', 15)
                    self.health_monitor.prediction_window = health_config.get('prediction_window', 300)
                
                logger.info(f"Configuration loaded from {self.config_file}")
            except Exception as e:
                logger.error(f"Failed to load configuration: {e}")
        else:
            # Create default configuration
            self._create_default_pools()
    
    def _create_default_pools(self):
        """Create default service pools"""
        default_pools = [
            (ServiceType.PLAYWRIGHT, OrchestrationStrategy.ROUND_ROBIN, FailoverPolicy.GRACEFUL),
            (ServiceType.GITHUB, OrchestrationStrategy.LEAST_CONNECTIONS, FailoverPolicy.CIRCUIT_BREAKER),
            (ServiceType.WEBSEARCH, OrchestrationStrategy.FASTEST_RESPONSE, FailoverPolicy.RETRY_WITH_BACKOFF),
            (ServiceType.CUSTOM, OrchestrationStrategy.RESOURCE_AWARE, FailoverPolicy.GRACEFUL)
        ]
        
        for service_type, strategy, failover_policy in default_pools:
            self.service_pools[service_type] = ServicePool(
                service_type=service_type,
                strategy=strategy,
                failover_policy=failover_policy
            )
    
    def _setup_message_handlers(self):
        """Setup message queue event handlers"""
        self.message_queue.subscribe("service_health_warning", self._handle_health_warning)
        self.message_queue.subscribe("service_failover", self._handle_failover_event)
        self.message_queue.subscribe("service_recovery", self._handle_recovery_event)
    
    async def _handle_health_warning(self, message: Dict[str, Any]):
        """Handle service health warnings"""
        service_id = message.get("service_id")
        prediction = message.get("prediction")
        
        logger.warning(f"Health warning for service {service_id}: {prediction}")
        
        # Notify v3 orchestrator if available
        if self.v3_orchestrator and hasattr(self.v3_orchestrator, 'status_line'):
            self.v3_orchestrator.status_line.update_status(
                "mcp_health_warning",
                "warning",
                {
                    "service_id": service_id,
                    "prediction": prediction,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
    
    async def _handle_failover_event(self, message: Dict[str, Any]):
        """Handle failover events"""
        failed_service = message.get("failed_service")
        fallback_service = message.get("fallback_service")
        policy = message.get("policy")
        
        logger.info(f"Failover event: {failed_service} -> {fallback_service} (policy: {policy})")
    
    async def _handle_recovery_event(self, message: Dict[str, Any]):
        """Handle service recovery events"""
        service_id = message.get("service_id")
        logger.info(f"Service recovery: {service_id}")
    
    async def _discover_services(self):
        """Discover and register MCP services"""
        if self.mcp_manager:
            # Get services from MCP Manager
            services = self.mcp_manager.get_all_services()
            
            for service in services:
                await self.register_service(service)
        
        # Additional discovery from configuration
        await self._discover_from_config()
    
    async def _discover_from_config(self):
        """Discover services from configuration files"""
        config_paths = [
            Path("./mcp-services.yml"),
            Path("./config/mcp-services.yml"),
            Path("../config/mcp-services.yml")
        ]
        
        for config_path in config_paths:
            if config_path.exists():
                try:
                    import yaml
                    with open(config_path, 'r') as f:
                        config = yaml.safe_load(f)
                    
                    services_config = config.get('services', [])
                    for service_config in services_config:
                        service = self._create_service_from_config(service_config)
                        if service:
                            await self.register_service(service)
                            
                except Exception as e:
                    logger.error(f"Failed to load services from {config_path}: {e}")
    
    def _create_service_from_config(self, config: Dict[str, Any]) -> Optional[ServiceInstance]:
        """Create service instance from configuration"""
        try:
            from core.manager import ServiceInstance, ServiceType, ServiceMetrics
            
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
    
    async def register_service(self, service: ServiceInstance) -> bool:
        """Register a service instance"""
        try:
            # Add to appropriate pool
            if service.service_type not in self.service_pools:
                self.service_pools[service.service_type] = ServicePool(service_type=service.service_type)
            
            pool = self.service_pools[service.service_type]
            
            # Check if service already exists
            existing_service = next((s for s in pool.instances if s.id == service.id), None)
            if existing_service:
                # Update existing service
                pool.instances.remove(existing_service)
            
            pool.instances.append(service)
            
            # Create circuit breaker
            self.circuit_breakers[service.id] = CircuitBreaker(
                failure_threshold=pool.circuit_breaker_threshold
            )
            
            logger.info(f"Registered service: {service.name} ({service.id}) in pool {service.service_type}")
            
            # Publish registration event
            await self.message_queue.publish(
                "service_registered",
                {
                    "service_id": service.id,
                    "service_name": service.name,
                    "service_type": service.service_type.value,
                    "url": service.url
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to register service {service.id}: {e}")
            return False
    
    async def unregister_service(self, service_id: str) -> bool:
        """Unregister a service instance"""
        try:
            for pool in self.service_pools.values():
                service = next((s for s in pool.instances if s.id == service_id), None)
                if service:
                    pool.instances.remove(service)
                    
                    # Remove circuit breaker
                    if service_id in self.circuit_breakers:
                        del self.circuit_breakers[service_id]
                    
                    logger.info(f"Unregistered service: {service.name} ({service_id})")
                    
                    # Publish unregistration event
                    await self.message_queue.publish(
                        "service_unregistered",
                        {
                            "service_id": service_id,
                            "service_name": service.name
                        }
                    )
                    
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to unregister service {service_id}: {e}")
            return False
    
    async def route_request(self, service_type: ServiceType, request_context: Dict[str, Any] = None) -> Optional[ServiceInstance]:
        """Route request to best available service"""
        start_time = time.time()
        self.metrics.total_requests += 1
        
        try:
            # Select service using load balancer
            selected_service = await self.load_balancer.select_service(service_type, request_context)
            
            if selected_service:
                # Record successful routing
                circuit_breaker = self.circuit_breakers.get(selected_service.id)
                if circuit_breaker:
                    circuit_breaker.record_success()
                
                selected_service.metrics.requests_total += 1
                self.metrics.successful_requests += 1
                
                # Update response time metrics
                response_time = time.time() - start_time
                self.metrics.average_response_time = (
                    (self.metrics.average_response_time * (self.metrics.total_requests - 1) + response_time) /
                    self.metrics.total_requests
                )
                
                logger.debug(f"Routed {service_type} request to {selected_service.name}")
                return selected_service
            else:
                logger.error(f"No available services for {service_type}")
                self.metrics.failed_requests += 1
                return None
                
        except Exception as e:
            logger.error(f"Request routing failed: {e}")
            self.metrics.failed_requests += 1
            return None
    
    async def handle_service_error(self, service: ServiceInstance, error: Exception) -> Optional[ServiceInstance]:
        """Handle service error and attempt failover"""
        return await self.failover_manager.handle_service_failure(service, error)
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive service status"""
        pool_status = {}
        total_services = 0
        healthy_services = 0
        
        for service_type, pool in self.service_pools.items():
            pool_healthy = sum(1 for s in pool.instances if s.is_healthy)
            total_services += len(pool.instances)
            healthy_services += pool_healthy
            
            pool_status[service_type.value] = {
                "total_instances": len(pool.instances),
                "healthy_instances": pool_healthy,
                "strategy": pool.strategy.value,
                "failover_policy": pool.failover_policy.value,
                "instances": [
                    {
                        "id": s.id,
                        "name": s.name,
                        "status": s.status.value,
                        "healthy": s.is_healthy,
                        "url": s.url,
                        "last_seen": s.last_seen.isoformat() if s.last_seen else None
                    }
                    for s in pool.instances
                ]
            }
        
        # Calculate availability
        self.metrics.service_availability = (healthy_services / total_services * 100) if total_services > 0 else 0
        
        return {
            "orchestrator_status": "running" if self.running else "stopped",
            "total_services": total_services,
            "healthy_services": healthy_services,
            "service_availability": f"{self.metrics.service_availability:.1f}%",
            "service_pools": pool_status,
            "metrics": {
                "total_requests": self.metrics.total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "success_rate": f"{(self.metrics.successful_requests / max(1, self.metrics.total_requests) * 100):.1f}%",
                "average_response_time": f"{self.metrics.average_response_time:.3f}s",
                "failover_count": self.metrics.failover_count,
                "circuit_breaker_trips": self.metrics.circuit_breaker_trips
            },
            "circuit_breakers": {
                service_id: {
                    "state": cb.state,
                    "failure_count": cb.failure_count,
                    "success_count": cb.success_count
                }
                for service_id, cb in self.circuit_breakers.items()
            }
        }
    
    def get_load_balancing_stats(self) -> Dict[str, Any]:
        """Get load balancing statistics"""
        stats = {}
        
        for service_type, pool in self.service_pools.items():
            if not pool.instances:
                continue
            
            request_distribution = {}
            total_requests = sum(s.metrics.requests_total for s in pool.instances)
            
            for service in pool.instances:
                if total_requests > 0:
                    percentage = (service.metrics.requests_total / total_requests) * 100
                else:
                    percentage = 0
                
                request_distribution[service.id] = {
                    "name": service.name,
                    "requests": service.metrics.requests_total,
                    "percentage": f"{percentage:.1f}%",
                    "avg_response_time": f"{service.metrics.response_time_avg:.3f}s",
                    "error_count": service.metrics.error_count
                }
            
            stats[service_type.value] = {
                "strategy": pool.strategy.value,
                "total_requests": total_requests,
                "distribution": request_distribution
            }
        
        return stats
    
    # Integration methods for v3 orchestrator
    
    def process_hook_event(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process hook events from v3 orchestrator"""
        if event_type == "mcp_request":
            return asyncio.run(self._handle_mcp_request(data))
        elif event_type == "service_health_check":
            return self._handle_health_check_request(data)
        elif event_type == "load_balance_request":
            return asyncio.run(self._handle_load_balance_request(data))
        else:
            return {"processed": False, "error": f"Unknown event type: {event_type}"}
    
    async def _handle_mcp_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP service requests"""
        service_type_str = data.get("service_type", "custom")
        request_context = data.get("context", {})
        
        try:
            service_type = ServiceType(service_type_str)
            selected_service = await self.route_request(service_type, request_context)
            
            if selected_service:
                return {
                    "processed": True,
                    "service": {
                        "id": selected_service.id,
                        "name": selected_service.name,
                        "url": selected_service.url,
                        "type": selected_service.service_type.value
                    }
                }
            else:
                return {
                    "processed": False,
                    "error": f"No available services for type: {service_type}"
                }
        except ValueError:
            return {
                "processed": False,
                "error": f"Invalid service type: {service_type_str}"
            }
    
    def _handle_health_check_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle health check requests"""
        return self.get_service_status()
    
    async def _handle_load_balance_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle load balancing requests"""
        return self.get_load_balancing_stats()


# Global instance
mcp_orchestrator: Optional[MCPServiceOrchestrator] = None

def get_mcp_orchestrator() -> MCPServiceOrchestrator:
    """Get or create MCP orchestrator instance"""
    global mcp_orchestrator
    if mcp_orchestrator is None:
        mcp_orchestrator = MCPServiceOrchestrator()
    return mcp_orchestrator

async def start_orchestrator():
    """Start the MCP orchestrator"""
    orchestrator = get_mcp_orchestrator()
    await orchestrator.start()
    return orchestrator

async def stop_orchestrator():
    """Stop the MCP orchestrator"""
    global mcp_orchestrator
    if mcp_orchestrator:
        await mcp_orchestrator.stop()

# Integration with v3 orchestrator
def integrate_with_v3_orchestrator():
    """Integrate MCP orchestrator with v3 orchestrator"""
    v3_orch = get_v3_orchestrator()
    if v3_orch:
        mcp_orch = get_mcp_orchestrator()
        
        # Register MCP orchestrator as a processor
        v3_orch.mcp_orchestrator = mcp_orch
        
        # Add MCP request handling
        original_process = v3_orch.process_request
        
        def enhanced_process_request(event_type: str, data: Dict) -> Dict:
            result = original_process(event_type, data)
            
            # Handle MCP-related events
            if event_type in ['mcp_request', 'service_health_check', 'load_balance_request']:
                mcp_result = mcp_orch.process_hook_event(event_type, data)
                result["mcp_orchestration"] = mcp_result
                result["components_used"].append("mcp_orchestrator")
            
            return result
        
        v3_orch.process_request = enhanced_process_request
        logger.info("MCP Orchestrator integrated with v3 orchestrator")


if __name__ == "__main__":
    async def main():
        """Example usage"""
        orchestrator = MCPServiceOrchestrator()
        
        try:
            await orchestrator.start()
            
            # Example service routing
            service = await orchestrator.route_request(
                ServiceType.PLAYWRIGHT,
                {"session_id": "test_session"}
            )
            
            if service:
                print(f"Selected service: {service.name} at {service.url}")
            
            # Get status
            status = orchestrator.get_service_status()
            print(f"Orchestrator Status: {json.dumps(status, indent=2)}")
            
            # Keep running
            await asyncio.sleep(30)
            
        finally:
            await orchestrator.stop()
    
    asyncio.run(main())