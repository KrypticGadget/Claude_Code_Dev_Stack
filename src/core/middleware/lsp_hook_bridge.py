#!/usr/bin/env python3
"""
LSP-Hook Bridge - Robust Language Server Protocol Integration
Connects language server daemons to the hook system with real-time analysis,
IntelliSense enhancement, and automated code quality assessment.
"""

import asyncio
import json
import time
import threading
import websocket
import weakref
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Set, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
import concurrent.futures
import socket
import ssl
import subprocess
import logging
import queue
import hashlib
import psutil
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LSPEventType(Enum):
    """LSP event types for hook triggering"""
    DIAGNOSTICS_PUBLISHED = "textDocument/publishDiagnostics"
    COMPLETION_TRIGGERED = "textDocument/completion"
    HOVER_REQUEST = "textDocument/hover"
    DEFINITION_REQUEST = "textDocument/definition"
    DOCUMENT_SYMBOL = "textDocument/documentSymbol"
    WORKSPACE_SYMBOL = "workspace/symbol"
    CODE_ACTION = "textDocument/codeAction"
    REFERENCES = "textDocument/references"
    RENAME = "textDocument/rename"
    FORMATTING = "textDocument/formatting"
    SERVER_INITIALIZE = "initialize"
    SERVER_SHUTDOWN = "shutdown"
    WORKSPACE_CHANGE = "workspace/didChangeWatchedFiles"
    SEMANTIC_TOKENS = "textDocument/semanticTokens/full"


class HookExecutionMode(Enum):
    """Hook execution strategies"""
    SYNCHRONOUS = "sync"
    ASYNCHRONOUS = "async"
    BATCHED = "batched"
    STREAMING = "streaming"


class LSPMessageType(Enum):
    """LSP message types"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


@dataclass
class LSPMessage:
    """LSP message structure"""
    id: Optional[Union[str, int]]
    method: str
    params: Dict[str, Any]
    message_type: LSPMessageType
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "lsp"


@dataclass
class HookExecutionContext:
    """Context for hook execution"""
    hook_name: str
    lsp_event: LSPEventType
    message: LSPMessage
    execution_id: str
    mode: HookExecutionMode
    timeout_seconds: float = 30.0
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LanguageServerConfig:
    """Configuration for language server connections"""
    name: str
    command: List[str]
    root_uri: str
    file_extensions: List[str]
    capabilities: Dict[str, Any] = field(default_factory=dict)
    initialization_options: Dict[str, Any] = field(default_factory=dict)
    transport: str = "stdio"  # stdio, tcp, websocket
    port: Optional[int] = None
    host: str = "localhost"
    auto_restart: bool = True
    restart_delay: float = 2.0


@dataclass
class CacheEntry:
    """Cache entry for performance optimization"""
    key: str
    value: Any
    timestamp: datetime
    ttl_seconds: float
    access_count: int = 0
    last_accessed: Optional[datetime] = None


class LSPCacheManager:
    """Performance optimization cache for LSP responses"""
    
    def __init__(self, max_size: int = 1000, default_ttl: float = 300.0):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        
        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        with self._lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            
            # Check if expired
            if datetime.now() > (entry.timestamp + timedelta(seconds=entry.ttl_seconds)):
                del self.cache[key]
                return None
            
            # Update access stats
            entry.access_count += 1
            entry.last_accessed = datetime.now()
            
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Set cached value"""
        with self._lock:
            # Evict if at capacity
            if len(self.cache) >= self.max_size:
                self._evict_lru()
            
            self.cache[key] = CacheEntry(
                key=key,
                value=value,
                timestamp=datetime.now(),
                ttl_seconds=ttl or self.default_ttl,
                last_accessed=datetime.now()
            )
    
    def invalidate(self, pattern: str = None) -> None:
        """Invalidate cache entries"""
        with self._lock:
            if pattern is None:
                self.cache.clear()
                return
            
            # Pattern-based invalidation
            keys_to_remove = [key for key in self.cache.keys() if pattern in key]
            for key in keys_to_remove:
                del self.cache[key]
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry"""
        if not self.cache:
            return
        
        # Find LRU entry
        lru_key = min(
            self.cache.keys(),
            key=lambda k: self.cache[k].last_accessed or datetime.min
        )
        del self.cache[lru_key]
    
    def _cleanup_loop(self) -> None:
        """Background cleanup of expired entries"""
        while True:
            try:
                time.sleep(60)  # Check every minute
                with self._lock:
                    current_time = datetime.now()
                    expired_keys = [
                        key for key, entry in self.cache.items()
                        if current_time > (entry.timestamp + timedelta(seconds=entry.ttl_seconds))
                    ]
                    for key in expired_keys:
                        del self.cache[key]
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")


class LSPTransport(ABC):
    """Abstract base class for LSP transport protocols"""
    
    @abstractmethod
    async def connect(self) -> bool:
        pass
    
    @abstractmethod
    async def send_message(self, message: Dict[str, Any]) -> None:
        pass
    
    @abstractmethod
    async def receive_message(self) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        pass


class StdioTransport(LSPTransport):
    """Standard I/O transport for LSP servers"""
    
    def __init__(self, command: List[str], cwd: Optional[str] = None):
        self.command = command
        self.cwd = cwd
        self.process: Optional[subprocess.Popen] = None
        self._connected = False
    
    async def connect(self) -> bool:
        """Start LSP server process"""
        try:
            self.process = subprocess.Popen(
                self.command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.cwd,
                text=True,
                bufsize=0
            )
            self._connected = True
            logger.info(f"Started LSP server: {' '.join(self.command)}")
            return True
        except Exception as e:
            logger.error(f"Failed to start LSP server: {e}")
            return False
    
    async def send_message(self, message: Dict[str, Any]) -> None:
        """Send JSON-RPC message to server"""
        if not self.process or not self._connected:
            raise RuntimeError("Transport not connected")
        
        content = json.dumps(message, separators=(',', ':'))
        message_str = f"Content-Length: {len(content)}\r\n\r\n{content}"
        
        self.process.stdin.write(message_str)
        self.process.stdin.flush()
    
    async def receive_message(self) -> Optional[Dict[str, Any]]:
        """Receive JSON-RPC message from server"""
        if not self.process or not self._connected:
            return None
        
        try:
            # Read headers
            headers = {}
            while True:
                line = self.process.stdout.readline()
                if not line:
                    return None
                
                line = line.strip()
                if not line:
                    break
                
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip().lower()] = value.strip()
            
            # Read content
            content_length = int(headers.get('content-length', 0))
            if content_length == 0:
                return None
            
            content = self.process.stdout.read(content_length)
            if not content:
                return None
            
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"Error receiving message: {e}")
            return None
    
    async def disconnect(self) -> None:
        """Stop LSP server process"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            self.process = None
        self._connected = False
    
    def is_connected(self) -> bool:
        return self._connected and self.process and self.process.poll() is None


class WebSocketTransport(LSPTransport):
    """WebSocket transport for LSP servers"""
    
    def __init__(self, url: str, ssl_context: Optional[ssl.SSLContext] = None):
        self.url = url
        self.ssl_context = ssl_context
        self.websocket: Optional[websocket.WebSocket] = None
        self._connected = False
    
    async def connect(self) -> bool:
        """Connect to WebSocket LSP server"""
        try:
            self.websocket = websocket.WebSocket(sslopt={"context": self.ssl_context} if self.ssl_context else None)
            self.websocket.connect(self.url)
            self._connected = True
            logger.info(f"Connected to WebSocket LSP server: {self.url}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to WebSocket LSP server: {e}")
            return False
    
    async def send_message(self, message: Dict[str, Any]) -> None:
        """Send JSON-RPC message via WebSocket"""
        if not self.websocket or not self._connected:
            raise RuntimeError("Transport not connected")
        
        content = json.dumps(message, separators=(',', ':'))
        message_str = f"Content-Length: {len(content)}\r\n\r\n{content}"
        self.websocket.send(message_str)
    
    async def receive_message(self) -> Optional[Dict[str, Any]]:
        """Receive JSON-RPC message via WebSocket"""
        if not self.websocket or not self._connected:
            return None
        
        try:
            data = self.websocket.recv()
            if not data:
                return None
            
            # Parse LSP message format
            if '\r\n\r\n' in data:
                headers, content = data.split('\r\n\r\n', 1)
                return json.loads(content)
            else:
                return json.loads(data)
                
        except Exception as e:
            logger.error(f"Error receiving WebSocket message: {e}")
            return None
    
    async def disconnect(self) -> None:
        """Disconnect from WebSocket server"""
        if self.websocket:
            self.websocket.close()
            self.websocket = None
        self._connected = False
    
    def is_connected(self) -> bool:
        return self._connected and self.websocket


class HookExecutor:
    """Manages hook execution with different strategies"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.execution_queue = queue.PriorityQueue()
        self.active_executions: Dict[str, HookExecutionContext] = {}
        self.execution_history: deque = deque(maxlen=1000)
        self._lock = threading.RLock()
        
        # Start execution processor
        self._processor_thread = threading.Thread(target=self._process_executions, daemon=True)
        self._processor_thread.start()
    
    async def execute_hook(self, context: HookExecutionContext) -> Dict[str, Any]:
        """Execute hook with specified strategy"""
        if context.mode == HookExecutionMode.SYNCHRONOUS:
            return await self._execute_sync(context)
        elif context.mode == HookExecutionMode.ASYNCHRONOUS:
            return await self._execute_async(context)
        elif context.mode == HookExecutionMode.BATCHED:
            return await self._execute_batched(context)
        elif context.mode == HookExecutionMode.STREAMING:
            return await self._execute_streaming(context)
        else:
            raise ValueError(f"Unknown execution mode: {context.mode}")
    
    async def _execute_sync(self, context: HookExecutionContext) -> Dict[str, Any]:
        """Execute hook synchronously"""
        start_time = time.time()
        
        try:
            with self._lock:
                self.active_executions[context.execution_id] = context
            
            # Import hook registry for execution
            from core.hooks.hook_registry import get_hook_registry
            registry = get_hook_registry()
            
            # Prepare hook data
            hook_data = {
                'event': context.lsp_event.value,
                'message': asdict(context.message),
                'metadata': context.metadata,
                'timestamp': datetime.now().isoformat()
            }
            
            # Execute hook
            execution_id = registry.execute_hook(
                context.hook_name,
                context.lsp_event.value,
                hook_data,
                timeout=context.timeout_seconds
            )
            
            result = {
                'execution_id': execution_id,
                'context_id': context.execution_id,
                'success': True,
                'execution_time': time.time() - start_time,
                'mode': context.mode.value
            }
            
            # Record execution
            self.execution_history.append({
                'context': context,
                'result': result,
                'timestamp': datetime.now()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Sync hook execution failed: {e}")
            return {
                'execution_id': context.execution_id,
                'success': False,
                'error': str(e),
                'execution_time': time.time() - start_time,
                'mode': context.mode.value
            }
        finally:
            with self._lock:
                if context.execution_id in self.active_executions:
                    del self.active_executions[context.execution_id]
    
    async def _execute_async(self, context: HookExecutionContext) -> Dict[str, Any]:
        """Execute hook asynchronously"""
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(self.executor, self._sync_hook_wrapper, context)
        
        try:
            result = await asyncio.wait_for(future, timeout=context.timeout_seconds)
            return result
        except asyncio.TimeoutError:
            return {
                'execution_id': context.execution_id,
                'success': False,
                'error': 'Timeout',
                'mode': context.mode.value
            }
    
    def _sync_hook_wrapper(self, context: HookExecutionContext) -> Dict[str, Any]:
        """Wrapper for sync execution in thread pool"""
        return asyncio.run(self._execute_sync(context))
    
    async def _execute_batched(self, context: HookExecutionContext) -> Dict[str, Any]:
        """Execute hook in batch mode (queued for later processing)"""
        priority = 1  # Lower number = higher priority
        self.execution_queue.put((priority, time.time(), context))
        
        return {
            'execution_id': context.execution_id,
            'success': True,
            'queued': True,
            'mode': context.mode.value
        }
    
    async def _execute_streaming(self, context: HookExecutionContext) -> Dict[str, Any]:
        """Execute hook in streaming mode (for real-time processing)"""
        # For streaming, we process immediately but with minimal overhead
        return await self._execute_async(context)
    
    def _process_executions(self) -> None:
        """Background processor for batched executions"""
        while True:
            try:
                if not self.execution_queue.empty():
                    _, timestamp, context = self.execution_queue.get(timeout=1)
                    asyncio.run(self._execute_sync(context))
                else:
                    time.sleep(0.1)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Batch execution error: {e}")
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        with self._lock:
            recent_executions = list(self.execution_history)[-100:]
            successful = sum(1 for exec in recent_executions if exec['result']['success'])
            
            return {
                'total_executions': len(self.execution_history),
                'active_executions': len(self.active_executions),
                'queued_executions': self.execution_queue.qsize(),
                'recent_success_rate': (successful / len(recent_executions)) * 100 if recent_executions else 0,
                'executor_threads': self.max_workers
            }


class LanguageServerConnection:
    """Manages connection to a single language server"""
    
    def __init__(self, config: LanguageServerConfig, hook_executor: HookExecutor):
        self.config = config
        self.hook_executor = hook_executor
        self.transport: Optional[LSPTransport] = None
        self.message_id_counter = 0
        self.pending_requests: Dict[Union[str, int], asyncio.Future] = {}
        self.capabilities: Dict[str, Any] = {}
        self.initialized = False
        self.running = False
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        
        # Health monitoring
        self.last_heartbeat = datetime.now()
        self.restart_count = 0
        self.max_restarts = 5
    
    def add_event_handler(self, event_type: str, handler: Callable) -> None:
        """Add event handler for specific LSP events"""
        self.event_handlers[event_type].append(handler)
    
    async def start(self) -> bool:
        """Start language server connection"""
        try:
            # Create transport
            if self.config.transport == "stdio":
                self.transport = StdioTransport(self.config.command, self.config.root_uri)
            elif self.config.transport == "websocket":
                url = f"ws://{self.config.host}:{self.config.port}"
                self.transport = WebSocketTransport(url)
            else:
                raise ValueError(f"Unsupported transport: {self.config.transport}")
            
            # Connect
            if not await self.transport.connect():
                return False
            
            # Initialize
            if not await self._initialize():
                return False
            
            # Start message loop
            self.running = True
            asyncio.create_task(self._message_loop())
            
            logger.info(f"Language server '{self.config.name}' started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start language server '{self.config.name}': {e}")
            return False
    
    async def stop(self) -> None:
        """Stop language server connection"""
        self.running = False
        
        if self.transport and self.transport.is_connected():
            # Send shutdown request
            try:
                await self.send_request("shutdown", {})
                await self.send_notification("exit", {})
            except Exception as e:
                logger.warning(f"Error during shutdown: {e}")
            
            await self.transport.disconnect()
        
        # Cancel pending requests
        for future in self.pending_requests.values():
            if not future.done():
                future.cancel()
        self.pending_requests.clear()
        
        logger.info(f"Language server '{self.config.name}' stopped")
    
    async def send_request(self, method: str, params: Dict[str, Any]) -> Any:
        """Send request and wait for response"""
        if not self.transport or not self.transport.is_connected():
            raise RuntimeError("Language server not connected")
        
        self.message_id_counter += 1
        message_id = self.message_id_counter
        
        message = {
            "jsonrpc": "2.0",
            "id": message_id,
            "method": method,
            "params": params
        }
        
        # Create future for response
        future = asyncio.Future()
        self.pending_requests[message_id] = future
        
        try:
            await self.transport.send_message(message)
            response = await asyncio.wait_for(future, timeout=30.0)
            return response
        finally:
            if message_id in self.pending_requests:
                del self.pending_requests[message_id]
    
    async def send_notification(self, method: str, params: Dict[str, Any]) -> None:
        """Send notification (no response expected)"""
        if not self.transport or not self.transport.is_connected():
            raise RuntimeError("Language server not connected")
        
        message = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
        
        await self.transport.send_message(message)
    
    async def _initialize(self) -> bool:
        """Initialize language server"""
        try:
            # Prepare initialization params
            init_params = {
                "processId": None,
                "rootUri": self.config.root_uri,
                "capabilities": {
                    "textDocument": {
                        "publishDiagnostics": {"relatedInformation": True},
                        "hover": {"contentFormat": ["markdown", "plaintext"]},
                        "completion": {"completionItem": {"snippetSupport": True}},
                        "definition": {"dynamicRegistration": True},
                        "references": {"dynamicRegistration": True},
                        "documentSymbol": {"hierarchicalDocumentSymbolSupport": True},
                        "codeAction": {"dynamicRegistration": True},
                        "rename": {"dynamicRegistration": True},
                        "formatting": {"dynamicRegistration": True}
                    },
                    "workspace": {
                        "symbol": {"dynamicRegistration": True},
                        "didChangeWatchedFiles": {"dynamicRegistration": True}
                    }
                },
                "initializationOptions": self.config.initialization_options
            }
            
            # Send initialize request
            response = await self.send_request("initialize", init_params)
            self.capabilities = response.get("capabilities", {})
            
            # Send initialized notification
            await self.send_notification("initialized", {})
            
            self.initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Language server initialization failed: {e}")
            return False
    
    async def _message_loop(self) -> None:
        """Main message processing loop"""
        while self.running and self.transport and self.transport.is_connected():
            try:
                message = await self.transport.receive_message()
                if message is None:
                    if self.config.auto_restart and self.restart_count < self.max_restarts:
                        logger.warning(f"Language server connection lost, attempting restart...")
                        await self._restart()
                    else:
                        break
                    continue
                
                await self._process_message(message)
                self.last_heartbeat = datetime.now()
                
            except Exception as e:
                logger.error(f"Message loop error: {e}")
                if self.config.auto_restart and self.restart_count < self.max_restarts:
                    await self._restart()
                else:
                    break
    
    async def _process_message(self, message: Dict[str, Any]) -> None:
        """Process incoming LSP message"""
        try:
            # Determine message type
            if "id" in message and "method" in message:
                # Request
                await self._handle_request(message)
            elif "id" in message and "result" in message:
                # Response
                await self._handle_response(message)
            elif "id" in message and "error" in message:
                # Error response
                await self._handle_error_response(message)
            elif "method" in message:
                # Notification
                await self._handle_notification(message)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def _handle_request(self, message: Dict[str, Any]) -> None:
        """Handle incoming request from language server"""
        method = message["method"]
        params = message.get("params", {})
        
        # Process based on method
        if method == "workspace/configuration":
            # Send configuration response
            response = {
                "jsonrpc": "2.0",
                "id": message["id"],
                "result": []
            }
            await self.transport.send_message(response)
    
    async def _handle_response(self, message: Dict[str, Any]) -> None:
        """Handle response to our request"""
        message_id = message["id"]
        if message_id in self.pending_requests:
            future = self.pending_requests[message_id]
            if not future.done():
                future.set_result(message.get("result"))
    
    async def _handle_error_response(self, message: Dict[str, Any]) -> None:
        """Handle error response"""
        message_id = message["id"]
        if message_id in self.pending_requests:
            future = self.pending_requests[message_id]
            if not future.done():
                error = message.get("error", {})
                future.set_exception(Exception(f"LSP Error: {error}"))
    
    async def _handle_notification(self, message: Dict[str, Any]) -> None:
        """Handle notification from language server"""
        method = message["method"]
        params = message.get("params", {})
        
        # Create LSP message object
        lsp_message = LSPMessage(
            id=None,
            method=method,
            params=params,
            message_type=LSPMessageType.NOTIFICATION
        )
        
        # Trigger hooks based on method
        await self._trigger_hooks_for_method(method, lsp_message)
        
        # Call registered event handlers
        if method in self.event_handlers:
            for handler in self.event_handlers[method]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(params)
                    else:
                        handler(params)
                except Exception as e:
                    logger.error(f"Event handler error: {e}")
    
    async def _trigger_hooks_for_method(self, method: str, message: LSPMessage) -> None:
        """Trigger appropriate hooks for LSP method"""
        # Map LSP methods to event types
        method_mapping = {
            "textDocument/publishDiagnostics": LSPEventType.DIAGNOSTICS_PUBLISHED,
            "textDocument/completion": LSPEventType.COMPLETION_TRIGGERED,
            "textDocument/hover": LSPEventType.HOVER_REQUEST,
            "textDocument/definition": LSPEventType.DEFINITION_REQUEST,
            "textDocument/documentSymbol": LSPEventType.DOCUMENT_SYMBOL,
            "workspace/symbol": LSPEventType.WORKSPACE_SYMBOL,
            "textDocument/codeAction": LSPEventType.CODE_ACTION,
            "textDocument/references": LSPEventType.REFERENCES,
            "textDocument/rename": LSPEventType.RENAME,
            "textDocument/formatting": LSPEventType.FORMATTING,
            "workspace/didChangeWatchedFiles": LSPEventType.WORKSPACE_CHANGE,
        }
        
        event_type = method_mapping.get(method)
        if not event_type:
            return
        
        # Import hook registry
        try:
            from core.hooks.hook_registry import get_hook_registry
            registry = get_hook_registry()
            
            # Get hooks that can handle this event
            compatible_hooks = []
            for hook_name, metadata in registry.hooks.items():
                if (metadata.lsp_compatible and 
                    metadata.state.value == "active" and
                    event_type.value in metadata.triggers):
                    compatible_hooks.append(hook_name)
            
            # Execute hooks
            for hook_name in compatible_hooks:
                context = HookExecutionContext(
                    hook_name=hook_name,
                    lsp_event=event_type,
                    message=message,
                    execution_id=f"{hook_name}_{int(time.time() * 1000)}",
                    mode=HookExecutionMode.ASYNCHRONOUS,  # Default to async for LSP events
                    metadata={
                        'language_server': self.config.name,
                        'method': method,
                        'file_extensions': self.config.file_extensions
                    }
                )
                
                # Execute hook asynchronously
                asyncio.create_task(self.hook_executor.execute_hook(context))
                
        except Exception as e:
            logger.error(f"Error triggering hooks for {method}: {e}")
    
    async def _restart(self) -> None:
        """Restart language server connection"""
        self.restart_count += 1
        logger.info(f"Restarting language server '{self.config.name}' (attempt {self.restart_count})")
        
        await self.stop()
        await asyncio.sleep(self.config.restart_delay)
        
        if await self.start():
            self.restart_count = 0  # Reset on successful restart
        else:
            logger.error(f"Failed to restart language server '{self.config.name}'")


class LSPHookBridge:
    """Main LSP-Hook Bridge system"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or str(Path.home() / ".claude" / "lsp_hook_bridge.json")
        self.language_servers: Dict[str, LanguageServerConnection] = {}
        self.hook_executor = HookExecutor(max_workers=6)
        self.cache_manager = LSPCacheManager()
        self.running = False
        
        # Configuration
        self.config = {
            "enabled": True,
            "auto_discovery": True,
            "cache_enabled": True,
            "health_check_interval": 30,
            "default_timeout": 30.0,
            "max_concurrent_hooks": 10,
            "language_servers": []
        }
        
        # Load configuration
        self._load_config()
        
        # Health monitoring
        self.health_monitor_task: Optional[asyncio.Task] = None
    
    def _load_config(self) -> None:
        """Load configuration from file"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                self.config.update(user_config)
                logger.info(f"Configuration loaded from {self.config_path}")
            else:
                self._save_config()
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
    
    def _save_config(self) -> None:
        """Save configuration to file"""
        try:
            config_file = Path(self.config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    async def start(self) -> bool:
        """Start the LSP-Hook bridge system"""
        if self.running:
            return True
        
        try:
            logger.info("Starting LSP-Hook Bridge system...")
            
            if not self.config["enabled"]:
                logger.info("LSP-Hook Bridge is disabled in configuration")
                return False
            
            # Start language servers
            for server_config_dict in self.config["language_servers"]:
                server_config = LanguageServerConfig(**server_config_dict)
                await self.add_language_server(server_config)
            
            # Auto-discover language servers if enabled
            if self.config["auto_discovery"]:
                await self._auto_discover_servers()
            
            # Start health monitoring
            if self.config["health_check_interval"] > 0:
                self.health_monitor_task = asyncio.create_task(self._health_monitor())
            
            self.running = True
            logger.info("LSP-Hook Bridge system started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start LSP-Hook Bridge: {e}")
            return False
    
    async def stop(self) -> None:
        """Stop the LSP-Hook bridge system"""
        if not self.running:
            return
        
        logger.info("Stopping LSP-Hook Bridge system...")
        
        # Stop health monitoring
        if self.health_monitor_task:
            self.health_monitor_task.cancel()
            try:
                await self.health_monitor_task
            except asyncio.CancelledError:
                pass
        
        # Stop all language servers
        for server in self.language_servers.values():
            await server.stop()
        self.language_servers.clear()
        
        self.running = False
        logger.info("LSP-Hook Bridge system stopped")
    
    async def add_language_server(self, config: LanguageServerConfig) -> bool:
        """Add and start a language server"""
        if config.name in self.language_servers:
            logger.warning(f"Language server '{config.name}' already exists")
            return False
        
        try:
            server = LanguageServerConnection(config, self.hook_executor)
            
            # Add standard event handlers
            server.add_event_handler("textDocument/publishDiagnostics", self._handle_diagnostics)
            server.add_event_handler("textDocument/completion", self._handle_completion)
            
            if await server.start():
                self.language_servers[config.name] = server
                logger.info(f"Added language server: {config.name}")
                return True
            else:
                logger.error(f"Failed to start language server: {config.name}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding language server '{config.name}': {e}")
            return False
    
    async def remove_language_server(self, name: str) -> bool:
        """Remove and stop a language server"""
        if name not in self.language_servers:
            return False
        
        server = self.language_servers[name]
        await server.stop()
        del self.language_servers[name]
        
        logger.info(f"Removed language server: {name}")
        return True
    
    async def _auto_discover_servers(self) -> None:
        """Auto-discover common language servers"""
        # Common language server configurations
        common_servers = [
            {
                "name": "python",
                "command": ["pylsp"],
                "file_extensions": [".py"],
                "root_uri": str(Path.cwd()),
                "auto_restart": True
            },
            {
                "name": "typescript",
                "command": ["typescript-language-server", "--stdio"],
                "file_extensions": [".ts", ".tsx", ".js", ".jsx"],
                "root_uri": str(Path.cwd()),
                "auto_restart": True
            },
            {
                "name": "rust",
                "command": ["rust-analyzer"],
                "file_extensions": [".rs"],
                "root_uri": str(Path.cwd()),
                "auto_restart": True
            }
        ]
        
        for server_dict in common_servers:
            # Check if command exists
            try:
                subprocess.run([server_dict["command"][0], "--version"], 
                             capture_output=True, timeout=5)
                
                config = LanguageServerConfig(**server_dict)
                await self.add_language_server(config)
                
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                logger.debug(f"Language server not available: {server_dict['command'][0]}")
    
    async def _handle_diagnostics(self, params: Dict[str, Any]) -> None:
        """Handle diagnostics from language server"""
        uri = params.get("uri", "")
        diagnostics = params.get("diagnostics", [])
        
        # Enhance diagnostics with additional context
        enhanced_data = {
            "uri": uri,
            "diagnostics": diagnostics,
            "error_count": len([d for d in diagnostics if d.get("severity") == 1]),
            "warning_count": len([d for d in diagnostics if d.get("severity") == 2]),
            "info_count": len([d for d in diagnostics if d.get("severity") == 3]),
            "hint_count": len([d for d in diagnostics if d.get("severity") == 4]),
            "total_count": len(diagnostics),
            "timestamp": datetime.now().isoformat()
        }
        
        # Cache diagnostics for performance
        if self.config["cache_enabled"]:
            cache_key = f"diagnostics:{uri}"
            self.cache_manager.set(cache_key, enhanced_data, ttl=300)  # 5 minute TTL
    
    async def _handle_completion(self, params: Dict[str, Any]) -> None:
        """Handle completion requests"""
        position = params.get("position", {})
        uri = params.get("textDocument", {}).get("uri", "")
        
        # Cache completion context for IntelliSense enhancement
        if self.config["cache_enabled"]:
            cache_key = f"completion:{uri}:{position.get('line')}:{position.get('character')}"
            completion_context = {
                "uri": uri,
                "position": position,
                "timestamp": datetime.now().isoformat()
            }
            self.cache_manager.set(cache_key, completion_context, ttl=60)  # 1 minute TTL
    
    async def _health_monitor(self) -> None:
        """Monitor health of language servers"""
        while self.running:
            try:
                await asyncio.sleep(self.config["health_check_interval"])
                
                for name, server in list(self.language_servers.items()):
                    if not server.transport or not server.transport.is_connected():
                        logger.warning(f"Language server '{name}' appears disconnected")
                        
                        # Attempt restart if auto-restart is enabled
                        if server.config.auto_restart:
                            logger.info(f"Attempting to restart language server '{name}'")
                            asyncio.create_task(server._restart())
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        server_status = {}
        for name, server in self.language_servers.items():
            server_status[name] = {
                "connected": server.transport.is_connected() if server.transport else False,
                "initialized": server.initialized,
                "restart_count": server.restart_count,
                "last_heartbeat": server.last_heartbeat.isoformat(),
                "capabilities": len(server.capabilities),
                "file_extensions": server.config.file_extensions
            }
        
        return {
            "running": self.running,
            "config": self.config,
            "language_servers": server_status,
            "hook_executor_stats": self.hook_executor.get_execution_stats(),
            "cache_stats": {
                "size": len(self.cache_manager.cache),
                "max_size": self.cache_manager.max_size
            },
            "system_resources": {
                "memory_usage_mb": psutil.Process().memory_info().rss / 1024 / 1024,
                "cpu_percent": psutil.Process().cpu_percent()
            }
        }
    
    async def trigger_manual_analysis(self, file_path: str, analysis_type: str = "full") -> Dict[str, Any]:
        """Manually trigger analysis for a file"""
        results = {}
        
        for name, server in self.language_servers.items():
            # Check if server handles this file type
            file_ext = Path(file_path).suffix
            if file_ext in server.config.file_extensions:
                try:
                    # Send document symbol request
                    params = {
                        "textDocument": {
                            "uri": f"file://{file_path}"
                        }
                    }
                    
                    if analysis_type in ["full", "symbols"]:
                        symbols = await server.send_request("textDocument/documentSymbol", params)
                        results[f"{name}_symbols"] = symbols
                    
                    if analysis_type in ["full", "diagnostics"]:
                        # Diagnostics are usually sent automatically, but we can request them
                        # by opening the document
                        open_params = {
                            "textDocument": {
                                "uri": f"file://{file_path}",
                                "languageId": name,
                                "version": 1,
                                "text": Path(file_path).read_text()
                            }
                        }
                        await server.send_notification("textDocument/didOpen", open_params)
                        
                except Exception as e:
                    logger.error(f"Manual analysis failed for {name}: {e}")
                    results[f"{name}_error"] = str(e)
        
        return results
    
    async def update_configuration(self, updates: Dict[str, Any]) -> None:
        """Update bridge configuration"""
        self.config.update(updates)
        self._save_config()
        
        # Apply configuration changes
        if "enabled" in updates:
            if updates["enabled"] and not self.running:
                await self.start()
            elif not updates["enabled"] and self.running:
                await self.stop()


# Export main classes
__all__ = [
    'LSPHookBridge',
    'LanguageServerConfig',
    'LSPEventType',
    'HookExecutionMode',
    'HookExecutionContext'
]