#!/usr/bin/env python3
"""
WebSocket LSP Gateway - Real-time Language Server Communication
Provides WebSocket interface for language server protocol with minimal latency,
event filtering, routing, and performance optimization.
"""

import asyncio
import json
import time
import uuid
import weakref
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Set, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
import websockets
import ssl
import logging
import threading
import concurrent.futures
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    """Message priority levels"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class FilterAction(Enum):
    """Filter actions for message processing"""
    ALLOW = "allow"
    BLOCK = "block"
    THROTTLE = "throttle"
    TRANSFORM = "transform"


@dataclass
class WebSocketMessage:
    """WebSocket message structure"""
    id: str
    type: str
    method: Optional[str]
    params: Dict[str, Any]
    priority: MessagePriority
    timestamp: datetime
    client_id: Optional[str] = None
    response_to: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClientSession:
    """WebSocket client session information"""
    id: str
    websocket: websockets.WebSocketServerProtocol
    connected_at: datetime
    last_activity: datetime
    subscriptions: Set[str] = field(default_factory=set)
    capabilities: Dict[str, Any] = field(default_factory=dict)
    rate_limit_tokens: int = 100
    rate_limit_last_refill: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FilterRule:
    """Message filtering rule"""
    name: str
    pattern: str
    action: FilterAction
    priority: int = 0
    condition: Optional[Callable[[WebSocketMessage], bool]] = None
    transform: Optional[Callable[[WebSocketMessage], WebSocketMessage]] = None
    throttle_limit: int = 10
    throttle_window: float = 60.0
    enabled: bool = True


class MessageRouter:
    """Routes messages between clients and language servers"""
    
    def __init__(self):
        self.routes: Dict[str, List[str]] = defaultdict(list)
        self.route_patterns: Dict[str, Callable[[WebSocketMessage], bool]] = {}
        self.default_route: Optional[str] = None
    
    def add_route(self, pattern: str, destination: str, 
                  condition: Optional[Callable[[WebSocketMessage], bool]] = None) -> None:
        """Add routing rule"""
        self.routes[pattern].append(destination)
        if condition:
            self.route_patterns[pattern] = condition
    
    def route_message(self, message: WebSocketMessage) -> List[str]:
        """Determine destinations for message"""
        destinations = []
        
        # Check pattern-based routes
        for pattern, condition in self.route_patterns.items():
            if condition(message):
                destinations.extend(self.routes[pattern])
        
        # Check simple method-based routes
        if message.method and message.method in self.routes:
            destinations.extend(self.routes[message.method])
        
        # Use default route if no specific routes found
        if not destinations and self.default_route:
            destinations.append(self.default_route)
        
        return list(set(destinations))  # Remove duplicates


class MessageFilter:
    """Filters and transforms messages based on rules"""
    
    def __init__(self):
        self.rules: List[FilterRule] = []
        self.throttle_counters: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._lock = threading.RLock()
    
    def add_rule(self, rule: FilterRule) -> None:
        """Add filtering rule"""
        with self._lock:
            self.rules.append(rule)
            self.rules.sort(key=lambda r: r.priority, reverse=True)
    
    def remove_rule(self, name: str) -> bool:
        """Remove filtering rule by name"""
        with self._lock:
            for i, rule in enumerate(self.rules):
                if rule.name == name:
                    del self.rules[i]
                    return True
            return False
    
    def filter_message(self, message: WebSocketMessage) -> Tuple[FilterAction, Optional[WebSocketMessage]]:
        """Apply filters to message"""
        with self._lock:
            for rule in self.rules:
                if not rule.enabled:
                    continue
                
                # Check if rule applies
                if rule.condition and not rule.condition(message):
                    continue
                
                if rule.pattern and rule.pattern not in (message.method or ""):
                    continue
                
                # Apply rule action
                if rule.action == FilterAction.BLOCK:
                    return FilterAction.BLOCK, None
                
                elif rule.action == FilterAction.THROTTLE:
                    if self._is_throttled(rule, message):
                        return FilterAction.BLOCK, None
                
                elif rule.action == FilterAction.TRANSFORM and rule.transform:
                    message = rule.transform(message)
                
                # Record message for throttling
                if rule.action == FilterAction.THROTTLE:
                    self._record_message(rule, message)
        
        return FilterAction.ALLOW, message
    
    def _is_throttled(self, rule: FilterRule, message: WebSocketMessage) -> bool:
        """Check if message should be throttled"""
        key = f"{rule.name}:{message.method}:{message.client_id}"
        counter = self.throttle_counters[key]
        
        current_time = time.time()
        window_start = current_time - rule.throttle_window
        
        # Remove old entries
        while counter and counter[0] < window_start:
            counter.popleft()
        
        # Check if limit exceeded
        return len(counter) >= rule.throttle_limit
    
    def _record_message(self, rule: FilterRule, message: WebSocketMessage) -> None:
        """Record message for throttling"""
        key = f"{rule.name}:{message.method}:{message.client_id}"
        self.throttle_counters[key].append(time.time())


class PerformanceOptimizer:
    """Optimizes WebSocket performance through various techniques"""
    
    def __init__(self):
        self.message_cache: Dict[str, Tuple[Any, datetime]] = {}
        self.cache_ttl = 60.0  # seconds
        self.compression_enabled = True
        self.batch_size = 10
        self.batch_timeout = 0.1  # seconds
        self.pending_batches: Dict[str, List[WebSocketMessage]] = defaultdict(list)
        self.batch_timers: Dict[str, asyncio.Handle] = {}
        
    async def optimize_message(self, message: WebSocketMessage) -> WebSocketMessage:
        """Apply performance optimizations to message"""
        # Check cache
        cache_key = self._get_cache_key(message)
        if cache_key in self.message_cache:
            cached_data, timestamp = self.message_cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_ttl):
                # Use cached response
                message.params = cached_data
                message.metadata["from_cache"] = True
        
        # Apply compression if enabled
        if self.compression_enabled and len(json.dumps(message.params)) > 1024:
            message.metadata["compressed"] = True
        
        return message
    
    def cache_response(self, request_message: WebSocketMessage, response_data: Any) -> None:
        """Cache response for future use"""
        cache_key = self._get_cache_key(request_message)
        self.message_cache[cache_key] = (response_data, datetime.now())
        
        # Cleanup old cache entries
        current_time = datetime.now()
        expired_keys = [
            key for key, (_, timestamp) in self.message_cache.items()
            if current_time - timestamp > timedelta(seconds=self.cache_ttl)
        ]
        for key in expired_keys:
            del self.message_cache[key]
    
    def _get_cache_key(self, message: WebSocketMessage) -> str:
        """Generate cache key for message"""
        key_data = {
            "method": message.method,
            "params": json.dumps(message.params, sort_keys=True)
        }
        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
    
    async def batch_message(self, client_id: str, message: WebSocketMessage, 
                           send_callback: Callable) -> None:
        """Batch messages for efficient sending"""
        self.pending_batches[client_id].append(message)
        
        # Cancel existing timer
        if client_id in self.batch_timers:
            self.batch_timers[client_id].cancel()
        
        # Set new timer
        loop = asyncio.get_event_loop()
        self.batch_timers[client_id] = loop.call_later(
            self.batch_timeout,
            lambda: asyncio.create_task(self._send_batch(client_id, send_callback))
        )
        
        # Send immediately if batch is full
        if len(self.pending_batches[client_id]) >= self.batch_size:
            if client_id in self.batch_timers:
                self.batch_timers[client_id].cancel()
                del self.batch_timers[client_id]
            await self._send_batch(client_id, send_callback)
    
    async def _send_batch(self, client_id: str, send_callback: Callable) -> None:
        """Send batched messages"""
        if client_id not in self.pending_batches or not self.pending_batches[client_id]:
            return
        
        batch = self.pending_batches[client_id]
        self.pending_batches[client_id] = []
        
        if client_id in self.batch_timers:
            del self.batch_timers[client_id]
        
        # Send batch
        await send_callback(batch)


class WebSocketLSPGateway:
    """Main WebSocket gateway for LSP communication"""
    
    def __init__(self, host: str = "localhost", port: int = 8765, ssl_context: Optional[ssl.SSLContext] = None):
        self.host = host
        self.port = port
        self.ssl_context = ssl_context
        
        # Client management
        self.clients: Dict[str, ClientSession] = {}
        self.client_lock = threading.RLock()
        
        # Message processing
        self.router = MessageRouter()
        self.filter = MessageFilter()
        self.optimizer = PerformanceOptimizer()
        
        # LSP bridge integration
        self.lsp_bridge: Optional[Any] = None
        
        # Server state
        self.server: Optional[websockets.WebSocketServer] = None
        self.running = False
        
        # Performance metrics
        self.metrics = {
            "messages_processed": 0,
            "messages_filtered": 0,
            "messages_cached": 0,
            "clients_connected": 0,
            "errors": 0,
            "start_time": None
        }
        
        # Setup default filters
        self._setup_default_filters()
        
        # Rate limiting
        self.rate_limit_tokens_per_minute = 100
        self.rate_limit_refill_interval = 1.0
        
        # Start rate limit refill task
        self.rate_limit_task: Optional[asyncio.Task] = None
    
    def _setup_default_filters(self) -> None:
        """Setup default message filters"""
        # Throttle diagnostic messages
        self.filter.add_rule(FilterRule(
            name="diagnostics_throttle",
            pattern="textDocument/publishDiagnostics",
            action=FilterAction.THROTTLE,
            throttle_limit=5,
            throttle_window=1.0,
            priority=10
        ))
        
        # Block excessive completion requests
        self.filter.add_rule(FilterRule(
            name="completion_throttle",
            pattern="textDocument/completion",
            action=FilterAction.THROTTLE,
            throttle_limit=10,
            throttle_window=1.0,
            priority=5
        ))
    
    async def start(self) -> None:
        """Start WebSocket server"""
        if self.running:
            return
        
        try:
            logger.info(f"Starting WebSocket LSP Gateway on {self.host}:{self.port}")
            
            # Start server
            self.server = await websockets.serve(
                self._handle_client,
                self.host,
                self.port,
                ssl=self.ssl_context,
                max_size=1024 * 1024,  # 1MB max message size
                max_queue=32,
                compression="deflate"
            )
            
            # Start rate limiting task
            self.rate_limit_task = asyncio.create_task(self._rate_limit_refill())
            
            self.running = True
            self.metrics["start_time"] = datetime.now()
            
            logger.info("WebSocket LSP Gateway started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start WebSocket LSP Gateway: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop WebSocket server"""
        if not self.running:
            return
        
        logger.info("Stopping WebSocket LSP Gateway...")
        
        # Stop rate limiting task
        if self.rate_limit_task:
            self.rate_limit_task.cancel()
            try:
                await self.rate_limit_task
            except asyncio.CancelledError:
                pass
        
        # Close all client connections
        with self.client_lock:
            for client in list(self.clients.values()):
                await client.websocket.close()
            self.clients.clear()
        
        # Stop server
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        self.running = False
        logger.info("WebSocket LSP Gateway stopped")
    
    async def _handle_client(self, websocket: websockets.WebSocketServerProtocol, path: str) -> None:
        """Handle new client connection"""
        client_id = str(uuid.uuid4())
        
        session = ClientSession(
            id=client_id,
            websocket=websocket,
            connected_at=datetime.now(),
            last_activity=datetime.now()
        )
        
        with self.client_lock:
            self.clients[client_id] = session
            self.metrics["clients_connected"] += 1
        
        logger.info(f"Client connected: {client_id}")
        
        try:
            # Send welcome message
            welcome_msg = {
                "type": "welcome",
                "client_id": client_id,
                "server_info": {
                    "version": "1.0.0",
                    "capabilities": ["lsp", "filtering", "routing", "caching"],
                    "timestamp": datetime.now().isoformat()
                }
            }
            await websocket.send(json.dumps(welcome_msg))
            
            # Handle messages
            async for message in websocket:
                await self._process_client_message(client_id, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {client_id}")
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
            self.metrics["errors"] += 1
        finally:
            with self.client_lock:
                if client_id in self.clients:
                    del self.clients[client_id]
    
    async def _process_client_message(self, client_id: str, raw_message: str) -> None:
        """Process message from client"""
        try:
            # Parse message
            data = json.loads(raw_message)
            
            # Create WebSocket message
            message = WebSocketMessage(
                id=data.get("id", str(uuid.uuid4())),
                type=data.get("type", "request"),
                method=data.get("method"),
                params=data.get("params", {}),
                priority=MessagePriority(data.get("priority", 3)),
                timestamp=datetime.now(),
                client_id=client_id
            )
            
            # Update client activity
            with self.client_lock:
                if client_id in self.clients:
                    self.clients[client_id].last_activity = datetime.now()
            
            # Check rate limiting
            if not self._check_rate_limit(client_id):
                await self._send_error(client_id, message.id, "Rate limit exceeded")
                return
            
            # Apply filters
            action, filtered_message = self.filter.filter_message(message)
            if action == FilterAction.BLOCK or filtered_message is None:
                self.metrics["messages_filtered"] += 1
                return
            
            # Apply optimizations
            optimized_message = await self.optimizer.optimize_message(filtered_message)
            
            # Route message
            if optimized_message.type == "lsp_request":
                await self._handle_lsp_request(optimized_message)
            elif optimized_message.type == "subscribe":
                await self._handle_subscription(optimized_message)
            elif optimized_message.type == "unsubscribe":
                await self._handle_unsubscription(optimized_message)
            elif optimized_message.type == "config":
                await self._handle_config(optimized_message)
            else:
                await self._send_error(client_id, message.id, f"Unknown message type: {message.type}")
            
            self.metrics["messages_processed"] += 1
            
        except json.JSONDecodeError:
            await self._send_error(client_id, None, "Invalid JSON")
        except Exception as e:
            logger.error(f"Error processing message from {client_id}: {e}")
            await self._send_error(client_id, None, f"Processing error: {str(e)}")
            self.metrics["errors"] += 1
    
    async def _handle_lsp_request(self, message: WebSocketMessage) -> None:
        """Handle LSP request from client"""
        if not self.lsp_bridge:
            await self._send_error(message.client_id, message.id, "LSP bridge not available")
            return
        
        try:
            # Forward to LSP bridge
            response = await self._forward_to_lsp(message)
            
            # Cache response if appropriate
            if message.method in ["textDocument/hover", "textDocument/definition"]:
                self.optimizer.cache_response(message, response)
                self.metrics["messages_cached"] += 1
            
            # Send response to client
            await self._send_response(message.client_id, message.id, response)
            
        except Exception as e:
            logger.error(f"LSP request error: {e}")
            await self._send_error(message.client_id, message.id, f"LSP error: {str(e)}")
    
    async def _forward_to_lsp(self, message: WebSocketMessage) -> Any:
        """Forward message to LSP bridge"""
        # This would integrate with the LSP bridge
        # For now, return a mock response
        return {
            "result": f"Mock response for {message.method}",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_subscription(self, message: WebSocketMessage) -> None:
        """Handle client subscription to events"""
        client_id = message.client_id
        events = message.params.get("events", [])
        
        with self.client_lock:
            if client_id in self.clients:
                self.clients[client_id].subscriptions.update(events)
        
        await self._send_response(client_id, message.id, {
            "subscribed": events,
            "total_subscriptions": len(self.clients[client_id].subscriptions)
        })
    
    async def _handle_unsubscription(self, message: WebSocketMessage) -> None:
        """Handle client unsubscription from events"""
        client_id = message.client_id
        events = message.params.get("events", [])
        
        with self.client_lock:
            if client_id in self.clients:
                self.clients[client_id].subscriptions.difference_update(events)
        
        await self._send_response(client_id, message.id, {
            "unsubscribed": events,
            "remaining_subscriptions": len(self.clients[client_id].subscriptions)
        })
    
    async def _handle_config(self, message: WebSocketMessage) -> None:
        """Handle configuration update"""
        config_updates = message.params.get("config", {})
        
        # Update client capabilities
        with self.client_lock:
            if message.client_id in self.clients:
                self.clients[message.client_id].capabilities.update(config_updates)
        
        await self._send_response(message.client_id, message.id, {
            "updated": True,
            "config": config_updates
        })
    
    async def _send_response(self, client_id: str, message_id: str, data: Any) -> None:
        """Send response to client"""
        response = {
            "type": "response",
            "id": message_id,
            "result": data,
            "timestamp": datetime.now().isoformat()
        }
        await self._send_to_client(client_id, response)
    
    async def _send_error(self, client_id: str, message_id: Optional[str], error: str) -> None:
        """Send error to client"""
        error_response = {
            "type": "error",
            "id": message_id,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        await self._send_to_client(client_id, error_response)
    
    async def _send_to_client(self, client_id: str, message: Dict[str, Any]) -> None:
        """Send message to specific client"""
        with self.client_lock:
            if client_id not in self.clients:
                return
            
            client = self.clients[client_id]
        
        try:
            await client.websocket.send(json.dumps(message))
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_id} connection closed during send")
            with self.client_lock:
                if client_id in self.clients:
                    del self.clients[client_id]
        except Exception as e:
            logger.error(f"Error sending to client {client_id}: {e}")
    
    async def broadcast_event(self, event_type: str, data: Any) -> None:
        """Broadcast event to subscribed clients"""
        message = {
            "type": "event",
            "event": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        with self.client_lock:
            for client in self.clients.values():
                if event_type in client.subscriptions:
                    asyncio.create_task(self._send_to_client(client.id, message))
    
    def _check_rate_limit(self, client_id: str) -> bool:
        """Check if client is within rate limits"""
        with self.client_lock:
            if client_id not in self.clients:
                return False
            
            client = self.clients[client_id]
            if client.rate_limit_tokens > 0:
                client.rate_limit_tokens -= 1
                return True
            
            return False
    
    async def _rate_limit_refill(self) -> None:
        """Refill rate limit tokens"""
        while self.running:
            try:
                await asyncio.sleep(self.rate_limit_refill_interval)
                
                with self.client_lock:
                    for client in self.clients.values():
                        # Refill tokens (max 100)
                        client.rate_limit_tokens = min(
                            100,
                            client.rate_limit_tokens + (self.rate_limit_tokens_per_minute // 60)
                        )
                        client.rate_limit_last_refill = datetime.now()
                        
            except Exception as e:
                logger.error(f"Rate limit refill error: {e}")
    
    def set_lsp_bridge(self, bridge: Any) -> None:
        """Set LSP bridge reference"""
        self.lsp_bridge = bridge
    
    def get_status(self) -> Dict[str, Any]:
        """Get gateway status"""
        with self.client_lock:
            client_info = {
                client_id: {
                    "connected_at": client.connected_at.isoformat(),
                    "last_activity": client.last_activity.isoformat(),
                    "subscriptions": list(client.subscriptions),
                    "rate_limit_tokens": client.rate_limit_tokens
                }
                for client_id, client in self.clients.items()
            }
        
        uptime = datetime.now() - self.metrics["start_time"] if self.metrics["start_time"] else timedelta(0)
        
        return {
            "running": self.running,
            "host": self.host,
            "port": self.port,
            "ssl_enabled": self.ssl_context is not None,
            "clients": client_info,
            "metrics": {
                **self.metrics,
                "uptime_seconds": uptime.total_seconds(),
                "current_clients": len(self.clients)
            },
            "filter_rules": len(self.filter.rules),
            "cache_size": len(self.optimizer.message_cache)
        }
    
    def add_filter_rule(self, rule: FilterRule) -> None:
        """Add message filter rule"""
        self.filter.add_rule(rule)
    
    def remove_filter_rule(self, name: str) -> bool:
        """Remove filter rule"""
        return self.filter.remove_rule(name)
    
    def add_route(self, pattern: str, destination: str, 
                  condition: Optional[Callable] = None) -> None:
        """Add message route"""
        self.router.add_route(pattern, destination, condition)


# Export main classes
__all__ = [
    'WebSocketLSPGateway',
    'MessageRouter',
    'MessageFilter',
    'FilterRule',
    'FilterAction',
    'MessagePriority',
    'PerformanceOptimizer'
]