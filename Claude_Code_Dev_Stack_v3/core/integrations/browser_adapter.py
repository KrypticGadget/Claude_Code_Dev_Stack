#!/usr/bin/env python3
"""
Claude Code Browser Integration Adapter
======================================

Integrates @zainhoda/claude-code-browser with Claude Code Dev Stack v3.0
while maintaining AGPL-3.0 compliance and proper attribution.

This adapter provides:
- WebSocket endpoints for real-time monitoring
- Custom parsing for Dev Stack commands  
- Integration with hooks and orchestration
- Compliance with AGPL-3.0 license requirements

Attribution:
- Original Claude Code Browser by @zainhoda (AGPL-3.0)
- Integration adapter by Claude Code Dev Stack v3.0 (AGPL-3.0)
"""

import os
import json
import time
import asyncio
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
import sqlite3
import threading
from collections import defaultdict, deque

# WebSocket and HTTP imports
try:
    import websockets
    from websockets.server import WebSocketServerProtocol
    import aiohttp
    from aiohttp import web, WSMsgType
    import aiofiles
except ImportError:
    print("Installing required dependencies...")
    subprocess.run(["pip", "install", "websockets", "aiohttp", "aiofiles"], check=True)
    import websockets
    from websockets.server import WebSocketServerProtocol
    import aiohttp
    from aiohttp import web, WSMsgType
    import aiofiles

# Dev Stack integration
try:
    from ..hooks.hooks.v3_orchestrator import get_v3_orchestrator
    from ..hooks.hooks.status_line_manager import get_status_line
    from ..hooks.hooks.context_manager import get_context_manager
except ImportError:
    # Fallback for standalone testing
    def get_v3_orchestrator():
        return None
    def get_status_line():
        return None
    def get_context_manager():
        return None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BrowserSession:
    """Claude Code Browser session data structure"""
    uuid: str
    filename: str
    mod_time: str
    size: int
    project_name: str
    content_preview: str = ""
    latest_todos: Dict = None
    session_type: str = "claude_code"
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.latest_todos is None:
            self.latest_todos = {}

@dataclass
class BrowserProject:
    """Claude Code Browser project data structure"""
    name: str
    path: str
    mod_time: str
    sessions: List[BrowserSession]
    session_count: int = 0
    total_size: int = 0
    
    def __post_init__(self):
        self.session_count = len(self.sessions)
        self.total_size = sum(session.size for session in self.sessions)

@dataclass
class DevStackCommand:
    """Dev Stack command data structure"""
    command: str
    agent_target: Optional[str]
    parameters: Dict[str, Any]
    timestamp: str
    session_uuid: str
    execution_context: Dict[str, Any]

class ClaudeCodeBrowserAdapter:
    """
    Adapter for integrating Claude Code Browser with Dev Stack v3.0
    
    Provides real-time monitoring, WebSocket endpoints, and Dev Stack command parsing
    while maintaining AGPL-3.0 compliance and proper attribution.
    """
    
    def __init__(self, 
                 browser_data_path: Optional[str] = None,
                 websocket_port: int = 8081,
                 http_port: int = 8082):
        # Browser data configuration
        self.browser_data_path = browser_data_path or os.path.expanduser("~/.claude/projects")
        self.websocket_port = websocket_port
        self.http_port = http_port
        
        # Dev Stack integration
        self.v3_orchestrator = get_v3_orchestrator()
        self.status_line = get_status_line()
        self.context_manager = get_context_manager()
        
        # WebSocket connections
        self.websocket_connections: List[WebSocketServerProtocol] = []
        self.connection_registry: Dict[str, Dict] = {}
        
        # Data caching
        self.project_cache: Dict[str, BrowserProject] = {}
        self.session_cache: Dict[str, BrowserSession] = {}
        self.cache_last_updated = datetime.now()
        self.cache_ttl = timedelta(minutes=5)
        
        # Real-time monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.file_watchers: Dict[str, Any] = {}
        
        # Command parsing
        self.command_patterns = {
            "agent_mention": r"@agent-([a-z-]+)",
            "hook_trigger": r"#hook-([a-z-]+)",
            "mcp_command": r"%mcp-([a-z-]+)",
            "orchestration": r"!orchestrate\s+(.+)",
            "status_query": r"\?status\s+(.+)",
            "context_operation": r"@context\s+(\w+)\s*(.*)?"
        }
        
        # Attribution and compliance
        self.attribution_info = {
            "original_project": {
                "name": "Claude Code Browser",
                "author": "@zainhoda",
                "repository": "https://github.com/zainhoda/claude-code-browser",
                "license": "AGPL-3.0",
                "integration_date": datetime.now().isoformat()
            },
            "integration_project": {
                "name": "Claude Code Dev Stack v3.0",
                "integration_type": "adapter_pattern",
                "license": "AGPL-3.0",
                "compliance_verified": True
            }
        }
        
        # Statistics and metrics
        self.metrics = {
            "sessions_processed": 0,
            "commands_parsed": 0,
            "websocket_messages": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "integration_events": 0
        }
        
        # Initialize system
        self._initialize_adapter()
    
    def _initialize_adapter(self):
        """Initialize the browser adapter system"""
        try:
            # Verify browser data path
            Path(self.browser_data_path).mkdir(parents=True, exist_ok=True)
            
            # Initialize cache
            self._refresh_cache()
            
            # Register with Dev Stack orchestrator
            if self.v3_orchestrator:
                self.v3_orchestrator.process_request("integration_registered", {
                    "component": "browser_adapter",
                    "capabilities": ["real_time_monitoring", "command_parsing", "websocket_api"],
                    "attribution": self.attribution_info
                })
            
            # Update status line
            if self.status_line:
                self.status_line.update_status(
                    "browser_adapter",
                    "initialized",
                    {
                        "data_path": self.browser_data_path,
                        "websocket_port": self.websocket_port,
                        "cached_projects": len(self.project_cache)
                    }
                )
            
            logger.info(f"Browser adapter initialized - {len(self.project_cache)} projects cached")
            
        except Exception as e:
            logger.error(f"Failed to initialize browser adapter: {e}")
            raise
    
    def _refresh_cache(self) -> bool:
        """Refresh the project and session cache"""
        try:
            old_cache_size = len(self.project_cache)
            self.project_cache.clear()
            self.session_cache.clear()
            
            # Scan browser data directory
            if not os.path.exists(self.browser_data_path):
                logger.warning(f"Browser data path not found: {self.browser_data_path}")
                return False
            
            projects_loaded = 0
            sessions_loaded = 0
            
            for project_dir in os.listdir(self.browser_data_path):
                project_path = os.path.join(self.browser_data_path, project_dir)
                
                if not os.path.isdir(project_path):
                    continue
                
                # Load project sessions
                project_sessions = []
                
                for session_file in os.listdir(project_path):
                    if not session_file.endswith('.json'):
                        continue
                    
                    session_path = os.path.join(project_path, session_file)
                    session = self._load_session_data(session_path, project_dir)
                    
                    if session:
                        project_sessions.append(session)
                        self.session_cache[session.uuid] = session
                        sessions_loaded += 1
                
                # Create project object
                if project_sessions:
                    project_stat = os.stat(project_path)
                    project = BrowserProject(
                        name=project_dir,
                        path=project_path,
                        mod_time=datetime.fromtimestamp(project_stat.st_mtime).isoformat(),
                        sessions=project_sessions
                    )
                    self.project_cache[project_dir] = project
                    projects_loaded += 1
            
            self.cache_last_updated = datetime.now()
            
            # Update metrics
            self.metrics["cache_hits"] += 1 if old_cache_size > 0 else 0
            self.metrics["cache_misses"] += 1 if old_cache_size == 0 else 0
            
            logger.info(f"Cache refreshed: {projects_loaded} projects, {sessions_loaded} sessions")
            return True
            
        except Exception as e:
            logger.error(f"Failed to refresh cache: {e}")
            return False
    
    def _load_session_data(self, session_path: str, project_name: str) -> Optional[BrowserSession]:
        """Load session data from file"""
        try:
            with open(session_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract session UUID from filename
            session_uuid = os.path.splitext(os.path.basename(session_path))[0]
            
            # Get file stats
            file_stat = os.stat(session_path)
            
            # Parse session content for Dev Stack commands
            content_preview = data.get('content', '')[:500]  # First 500 chars
            dev_stack_commands = self._parse_dev_stack_commands(content_preview, session_uuid)
            
            session = BrowserSession(
                uuid=session_uuid,
                filename=os.path.basename(session_path),
                mod_time=datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                size=file_stat.st_size,
                project_name=project_name,
                content_preview=content_preview,
                latest_todos=data.get('todos', {}),
                session_type="claude_code"
            )
            
            # Add Dev Stack specific tags
            if dev_stack_commands:
                session.tags.extend(['dev_stack_commands', 'orchestration_capable'])
                self.metrics["commands_parsed"] += len(dev_stack_commands)
            
            self.metrics["sessions_processed"] += 1
            return session
            
        except Exception as e:
            logger.error(f"Failed to load session {session_path}: {e}")
            return None
    
    def _parse_dev_stack_commands(self, content: str, session_uuid: str) -> List[DevStackCommand]:
        """Parse Dev Stack commands from session content"""
        import re
        
        commands = []
        
        try:
            # Parse different command types
            for command_type, pattern in self.command_patterns.items():
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                
                for match in matches:
                    command = DevStackCommand(
                        command=match.group(0),
                        agent_target=match.group(1) if match.groups() else None,
                        parameters={"raw_match": match.group(0), "groups": match.groups()},
                        timestamp=datetime.now().isoformat(),
                        session_uuid=session_uuid,
                        execution_context={"command_type": command_type, "session_uuid": session_uuid}
                    )
                    commands.append(command)
            
            # Advanced parsing for orchestration commands
            orchestration_commands = self._parse_orchestration_commands(content, session_uuid)
            commands.extend(orchestration_commands)
            
        except Exception as e:
            logger.error(f"Failed to parse commands from content: {e}")
        
        return commands
    
    def _parse_orchestration_commands(self, content: str, session_uuid: str) -> List[DevStackCommand]:
        """Parse advanced orchestration commands"""
        import re
        
        commands = []
        
        try:
            # Multi-agent orchestration patterns
            multi_agent_pattern = r"@agent-(\w+)\s+(?:and|then|with)\s+@agent-(\w+)"
            matches = re.finditer(multi_agent_pattern, content, re.IGNORECASE)
            
            for match in matches:
                command = DevStackCommand(
                    command=match.group(0),
                    agent_target="orchestrator",
                    parameters={
                        "primary_agent": match.group(1),
                        "secondary_agent": match.group(2),
                        "orchestration_type": "sequential"
                    },
                    timestamp=datetime.now().isoformat(),
                    session_uuid=session_uuid,
                    execution_context={"command_type": "multi_agent_orchestration"}
                )
                commands.append(command)
            
            # Workflow patterns
            workflow_pattern = r"workflow:\s*([^\n]+)"
            matches = re.finditer(workflow_pattern, content, re.IGNORECASE)
            
            for match in matches:
                command = DevStackCommand(
                    command=match.group(0),
                    agent_target="workflow_orchestrator",
                    parameters={"workflow_definition": match.group(1)},
                    timestamp=datetime.now().isoformat(),
                    session_uuid=session_uuid,
                    execution_context={"command_type": "workflow_definition"}
                )
                commands.append(command)
                
        except Exception as e:
            logger.error(f"Failed to parse orchestration commands: {e}")
        
        return commands
    
    async def start_websocket_server(self):
        """Start WebSocket server for real-time updates"""
        async def handle_websocket(websocket, path):
            """Handle WebSocket connection"""
            connection_id = f"ws_{int(time.time() * 1000)}"
            
            try:
                # Register connection
                self.websocket_connections.append(websocket)
                self.connection_registry[connection_id] = {
                    "websocket": websocket,
                    "connected_at": datetime.now().isoformat(),
                    "path": path,
                    "client_info": {}
                }
                
                logger.info(f"WebSocket client connected: {connection_id}")
                
                # Send initial data
                await self._send_initial_data(websocket)
                
                # Handle incoming messages
                async for message in websocket:
                    await self._handle_websocket_message(websocket, message, connection_id)
                    
            except websockets.exceptions.ConnectionClosed:
                logger.info(f"WebSocket client disconnected: {connection_id}")
            except Exception as e:
                logger.error(f"WebSocket error for {connection_id}: {e}")
            finally:
                # Cleanup connection
                if websocket in self.websocket_connections:
                    self.websocket_connections.remove(websocket)
                if connection_id in self.connection_registry:
                    del self.connection_registry[connection_id]
        
        # Start WebSocket server
        logger.info(f"Starting WebSocket server on port {self.websocket_port}")
        server = await websockets.serve(handle_websocket, "localhost", self.websocket_port)
        return server
    
    async def _send_initial_data(self, websocket):
        """Send initial data to WebSocket client"""
        try:
            # Refresh cache if needed
            if datetime.now() - self.cache_last_updated > self.cache_ttl:
                self._refresh_cache()
            
            # Send project list
            projects_data = {
                "type": "projects_update",
                "timestamp": datetime.now().isoformat(),
                "projects": [asdict(project) for project in self.project_cache.values()],
                "total_projects": len(self.project_cache),
                "total_sessions": len(self.session_cache)
            }
            
            await websocket.send(json.dumps(projects_data))
            
            # Send system status
            status_data = {
                "type": "system_status",
                "timestamp": datetime.now().isoformat(),
                "adapter_status": "active",
                "metrics": self.metrics,
                "attribution": self.attribution_info
            }
            
            await websocket.send(json.dumps(status_data))
            
            self.metrics["websocket_messages"] += 2
            
        except Exception as e:
            logger.error(f"Failed to send initial data: {e}")
    
    async def _handle_websocket_message(self, websocket, message, connection_id: str):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            message_type = data.get("type", "unknown")
            
            if message_type == "get_project_sessions":
                await self._handle_get_project_sessions(websocket, data)
            elif message_type == "get_session_content":
                await self._handle_get_session_content(websocket, data)
            elif message_type == "execute_dev_stack_command":
                await self._handle_execute_command(websocket, data)
            elif message_type == "subscribe_to_changes":
                await self._handle_subscribe_changes(websocket, data, connection_id)
            else:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                }))
            
            self.metrics["websocket_messages"] += 1
            
        except json.JSONDecodeError:
            await websocket.send(json.dumps({
                "type": "error",
                "message": "Invalid JSON message"
            }))
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            await websocket.send(json.dumps({
                "type": "error",
                "message": str(e)
            }))
    
    async def _handle_get_project_sessions(self, websocket, data):
        """Handle request for project sessions"""
        project_name = data.get("project_name")
        
        if not project_name or project_name not in self.project_cache:
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"Project not found: {project_name}"
            }))
            return
        
        project = self.project_cache[project_name]
        
        response = {
            "type": "project_sessions",
            "timestamp": datetime.now().isoformat(),
            "project_name": project_name,
            "sessions": [asdict(session) for session in project.sessions],
            "session_count": len(project.sessions)
        }
        
        await websocket.send(json.dumps(response))
    
    async def _handle_get_session_content(self, websocket, data):
        """Handle request for session content"""
        session_uuid = data.get("session_uuid")
        
        if not session_uuid or session_uuid not in self.session_cache:
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"Session not found: {session_uuid}"
            }))
            return
        
        session = self.session_cache[session_uuid]
        
        # Load full content
        session_path = os.path.join(
            self.browser_data_path,
            session.project_name,
            session.filename
        )
        
        try:
            with open(session_path, 'r', encoding='utf-8') as f:
                full_content = json.load(f)
            
            # Parse Dev Stack commands from full content
            dev_stack_commands = self._parse_dev_stack_commands(
                full_content.get('content', ''),
                session_uuid
            )
            
            response = {
                "type": "session_content",
                "timestamp": datetime.now().isoformat(),
                "session": asdict(session),
                "content": full_content,
                "dev_stack_commands": [asdict(cmd) for cmd in dev_stack_commands]
            }
            
            await websocket.send(json.dumps(response))
            
        except Exception as e:
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"Failed to load session content: {e}"
            }))
    
    async def _handle_execute_command(self, websocket, data):
        """Handle Dev Stack command execution"""
        command_data = data.get("command")
        session_uuid = data.get("session_uuid")
        
        if not command_data:
            await websocket.send(json.dumps({
                "type": "error",
                "message": "No command provided"
            }))
            return
        
        try:
            # Create command object
            command = DevStackCommand(
                command=command_data.get("command", ""),
                agent_target=command_data.get("agent_target"),
                parameters=command_data.get("parameters", {}),
                timestamp=datetime.now().isoformat(),
                session_uuid=session_uuid or "",
                execution_context=command_data.get("execution_context", {})
            )
            
            # Execute with Dev Stack orchestrator
            execution_result = await self._execute_dev_stack_command(command)
            
            response = {
                "type": "command_executed",
                "timestamp": datetime.now().isoformat(),
                "command": asdict(command),
                "result": execution_result,
                "success": execution_result.get("success", False)
            }
            
            await websocket.send(json.dumps(response))
            
            # Notify other connections
            await self._broadcast_command_execution(command, execution_result)
            
        except Exception as e:
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"Command execution failed: {e}"
            }))
    
    async def _execute_dev_stack_command(self, command: DevStackCommand) -> Dict:
        """Execute Dev Stack command through orchestrator"""
        try:
            if not self.v3_orchestrator:
                return {
                    "success": False,
                    "error": "Dev Stack orchestrator not available",
                    "message": "Command cannot be executed without orchestrator integration"
                }
            
            # Map command to orchestrator event
            event_type = self._map_command_to_event_type(command)
            event_data = {
                "command": command.command,
                "agent_target": command.agent_target,
                "parameters": command.parameters,
                "session_uuid": command.session_uuid,
                "source": "browser_adapter"
            }
            
            # Execute through orchestrator
            result = self.v3_orchestrator.process_request(event_type, event_data)
            
            # Update metrics
            self.metrics["integration_events"] += 1
            
            return {
                "success": True,
                "orchestrator_result": result,
                "execution_time": result.get("performance_metrics", {}).get("processing_time_ms", 0),
                "components_used": result.get("components_used", [])
            }
            
        except Exception as e:
            logger.error(f"Failed to execute Dev Stack command: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Command execution failed"
            }
    
    def _map_command_to_event_type(self, command: DevStackCommand) -> str:
        """Map command to orchestrator event type"""
        if command.agent_target:
            return "agent_activation"
        elif "orchestrate" in command.command.lower():
            return "orchestration_request"
        elif command.execution_context.get("command_type") == "workflow_definition":
            return "workflow_request"
        else:
            return "user_prompt"
    
    async def _broadcast_command_execution(self, command: DevStackCommand, result: Dict):
        """Broadcast command execution to all connected clients"""
        if not self.websocket_connections:
            return
        
        broadcast_data = {
            "type": "command_broadcast",
            "timestamp": datetime.now().isoformat(),
            "command_summary": {
                "command": command.command,
                "agent_target": command.agent_target,
                "session_uuid": command.session_uuid
            },
            "result_summary": {
                "success": result.get("success", False),
                "components_used": result.get("components_used", [])
            }
        }
        
        # Send to all connections
        disconnected = []
        for websocket in self.websocket_connections:
            try:
                await websocket.send(json.dumps(broadcast_data))
            except websockets.exceptions.ConnectionClosed:
                disconnected.append(websocket)
        
        # Clean up disconnected clients
        for websocket in disconnected:
            if websocket in self.websocket_connections:
                self.websocket_connections.remove(websocket)
    
    def start_real_time_monitoring(self):
        """Start real-time file system monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info("Real-time monitoring started")
    
    def stop_real_time_monitoring(self):
        """Stop real-time file system monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        logger.info("Real-time monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Check for changes in browser data directory
                changes_detected = self._check_for_changes()
                
                if changes_detected:
                    # Refresh cache
                    self._refresh_cache()
                    
                    # Broadcast updates to WebSocket clients
                    asyncio.run(self._broadcast_updates())
                
                # Update status line
                if self.status_line:
                    self.status_line.update_status(
                        "browser_monitor",
                        "active",
                        {
                            "projects": len(self.project_cache),
                            "sessions": len(self.session_cache),
                            "connections": len(self.websocket_connections)
                        }
                    )
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(5)
    
    def _check_for_changes(self) -> bool:
        """Check for changes in browser data directory"""
        try:
            if not os.path.exists(self.browser_data_path):
                return False
            
            current_mod_time = os.path.getmtime(self.browser_data_path)
            last_check_time = self.cache_last_updated.timestamp()
            
            return current_mod_time > last_check_time
            
        except Exception as e:
            logger.error(f"Failed to check for changes: {e}")
            return False
    
    async def _broadcast_updates(self):
        """Broadcast updates to all WebSocket clients"""
        if not self.websocket_connections:
            return
        
        update_data = {
            "type": "data_update",
            "timestamp": datetime.now().isoformat(),
            "projects": [asdict(project) for project in self.project_cache.values()],
            "total_projects": len(self.project_cache),
            "total_sessions": len(self.session_cache)
        }
        
        disconnected = []
        for websocket in self.websocket_connections:
            try:
                await websocket.send(json.dumps(update_data))
            except websockets.exceptions.ConnectionClosed:
                disconnected.append(websocket)
        
        # Clean up disconnected clients
        for websocket in disconnected:
            if websocket in self.websocket_connections:
                self.websocket_connections.remove(websocket)
    
    async def create_http_api_server(self):
        """Create HTTP API server for REST endpoints"""
        app = web.Application()
        
        # CORS middleware
        async def cors_handler(request, handler):
            response = await handler(request)
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            return response
        
        app.middlewares.append(cors_handler)
        
        # API routes
        app.router.add_get('/api/projects', self._api_get_projects)
        app.router.add_get('/api/projects/{project_name}', self._api_get_project)
        app.router.add_get('/api/sessions/{session_uuid}', self._api_get_session)
        app.router.add_get('/api/status', self._api_get_status)
        app.router.add_get('/api/attribution', self._api_get_attribution)
        app.router.add_post('/api/commands/execute', self._api_execute_command)
        app.router.add_get('/api/browser/projects', self._api_browser_proxy_projects)
        app.router.add_get('/api/browser/project/{project_name}', self._api_browser_proxy_project)
        
        return app
    
    async def _api_get_projects(self, request):
        """API endpoint: Get all projects"""
        if datetime.now() - self.cache_last_updated > self.cache_ttl:
            self._refresh_cache()
        
        return web.json_response({
            "projects": [asdict(project) for project in self.project_cache.values()],
            "total_projects": len(self.project_cache),
            "total_sessions": len(self.session_cache),
            "cache_updated": self.cache_last_updated.isoformat()
        })
    
    async def _api_get_project(self, request):
        """API endpoint: Get specific project"""
        project_name = request.match_info['project_name']
        
        if project_name not in self.project_cache:
            return web.json_response(
                {"error": f"Project not found: {project_name}"},
                status=404
            )
        
        project = self.project_cache[project_name]
        return web.json_response(asdict(project))
    
    async def _api_get_session(self, request):
        """API endpoint: Get specific session"""
        session_uuid = request.match_info['session_uuid']
        
        if session_uuid not in self.session_cache:
            return web.json_response(
                {"error": f"Session not found: {session_uuid}"},
                status=404
            )
        
        session = self.session_cache[session_uuid]
        return web.json_response(asdict(session))
    
    async def _api_get_status(self, request):
        """API endpoint: Get adapter status"""
        return web.json_response({
            "status": "active",
            "version": "3.0",
            "metrics": self.metrics,
            "cache_info": {
                "projects": len(self.project_cache),
                "sessions": len(self.session_cache),
                "last_updated": self.cache_last_updated.isoformat()
            },
            "websocket_info": {
                "connections": len(self.websocket_connections),
                "port": self.websocket_port
            },
            "integration_info": {
                "orchestrator_available": self.v3_orchestrator is not None,
                "status_line_available": self.status_line is not None,
                "context_manager_available": self.context_manager is not None
            }
        })
    
    async def _api_get_attribution(self, request):
        """API endpoint: Get attribution information"""
        return web.json_response(self.attribution_info)
    
    async def _api_execute_command(self, request):
        """API endpoint: Execute Dev Stack command"""
        try:
            data = await request.json()
            
            command = DevStackCommand(
                command=data.get("command", ""),
                agent_target=data.get("agent_target"),
                parameters=data.get("parameters", {}),
                timestamp=datetime.now().isoformat(),
                session_uuid=data.get("session_uuid", ""),
                execution_context=data.get("execution_context", {})
            )
            
            result = await self._execute_dev_stack_command(command)
            
            return web.json_response({
                "command": asdict(command),
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            return web.json_response(
                {"error": f"Command execution failed: {e}"},
                status=500
            )
    
    async def _api_browser_proxy_projects(self, request):
        """API endpoint: Proxy to original browser for projects (BWA compatibility)"""
        # This maintains compatibility with the BrowserMonitor component
        projects_data = []
        
        for project in self.project_cache.values():
            projects_data.append({
                "name": project.name,
                "path": project.path,
                "modTime": project.mod_time,
                "sessions": [
                    {
                        "uuid": session.uuid,
                        "filename": session.filename,
                        "modTime": session.mod_time,
                        "size": session.size,
                        "latestTodos": session.latest_todos
                    }
                    for session in project.sessions
                ]
            })
        
        return web.json_response({"projects": projects_data})
    
    async def _api_browser_proxy_project(self, request):
        """API endpoint: Proxy to original browser for specific project"""
        project_name = request.match_info['project_name']
        
        if project_name not in self.project_cache:
            return web.json_response(
                {"error": f"Project not found: {project_name}"},
                status=404
            )
        
        project = self.project_cache[project_name]
        sessions_data = []
        
        for session in project.sessions:
            sessions_data.append({
                "uuid": session.uuid,
                "filename": session.filename,
                "modTime": session.mod_time,
                "size": session.size,
                "latestTodos": session.latest_todos
            })
        
        return web.json_response({"sessions": sessions_data})
    
    def get_integration_status(self) -> Dict:
        """Get comprehensive integration status"""
        return {
            "adapter_status": "active",
            "version": "3.0",
            "attribution": self.attribution_info,
            "cache_info": {
                "projects": len(self.project_cache),
                "sessions": len(self.session_cache),
                "last_updated": self.cache_last_updated.isoformat(),
                "ttl_seconds": self.cache_ttl.total_seconds()
            },
            "websocket_info": {
                "connections": len(self.websocket_connections),
                "port": self.websocket_port,
                "messages_sent": self.metrics["websocket_messages"]
            },
            "monitoring_info": {
                "active": self.monitoring_active,
                "data_path": self.browser_data_path
            },
            "integration_status": {
                "orchestrator": self.v3_orchestrator is not None,
                "status_line": self.status_line is not None,
                "context_manager": self.context_manager is not None
            },
            "metrics": self.metrics,
            "compliance": {
                "license": "AGPL-3.0",
                "attribution_maintained": True,
                "source_available": True
            }
        }


# Global adapter instance
browser_adapter = None

def get_browser_adapter(websocket_port: int = 8081, http_port: int = 8082) -> ClaudeCodeBrowserAdapter:
    """Get or create browser adapter instance"""
    global browser_adapter
    if browser_adapter is None:
        browser_adapter = ClaudeCodeBrowserAdapter(websocket_port=websocket_port, http_port=http_port)
    return browser_adapter

async def start_browser_integration(websocket_port: int = 8081, http_port: int = 8082):
    """Start complete browser integration"""
    adapter = get_browser_adapter(websocket_port, http_port)
    
    # Start real-time monitoring
    adapter.start_real_time_monitoring()
    
    # Start servers
    websocket_server = await adapter.start_websocket_server()
    http_app = await adapter.create_http_api_server()
    
    # Start HTTP server
    runner = web.AppRunner(http_app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', http_port)
    await site.start()
    
    logger.info(f"Browser integration started - WebSocket: {websocket_port}, HTTP: {http_port}")
    
    return adapter, websocket_server, runner

# Export for hook system
__all__ = [
    'ClaudeCodeBrowserAdapter',
    'BrowserSession', 
    'BrowserProject',
    'DevStackCommand',
    'get_browser_adapter',
    'start_browser_integration'
]