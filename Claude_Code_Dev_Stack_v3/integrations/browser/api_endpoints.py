"""
Dev Stack API Endpoints
=======================

Extended API endpoints for Claude Code Browser integration that provide
Dev Stack specific functionality while maintaining separation from the
original AGPL-3.0 codebase by @zainhoda.
"""

import asyncio
import json
import os
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import aiohttp
from aiohttp import web, WSMsgType
import aiofiles
from attribution import attribution

@dataclass
class AgentStatus:
    """Agent status information."""
    name: str
    active: bool
    last_activity: float
    tasks_completed: int
    status: str = "idle"

@dataclass
class TaskInfo:
    """Task information."""
    id: str
    name: str
    status: str
    progress: float
    started_at: float
    completed_at: Optional[float] = None
    agent: Optional[str] = None

@dataclass
class HookEvent:
    """Hook event information."""
    name: str
    triggered_at: float
    status: str
    payload: Dict[str, Any]

@dataclass
class AudioEvent:
    """Audio event information."""
    file_path: str
    event_type: str
    timestamp: float
    duration: Optional[float] = None

class DevStackAPIServer:
    """
    Extended API server that provides Dev Stack specific endpoints
    while proxying original browser functionality.
    """
    
    def __init__(self, adapter, port: int = 8081):
        self.adapter = adapter
        self.port = port
        self.app = web.Application()
        self.websocket_clients = set()
        
        # Dev Stack data stores
        self.agents: Dict[str, AgentStatus] = {}
        self.tasks: Dict[str, TaskInfo] = {}
        self.hooks: List[HookEvent] = []
        self.audio_events: List[AudioEvent] = []
        
        self._setup_routes()
        self._init_default_agents()
    
    def _setup_routes(self):
        """Setup API routes."""
        # Dev Stack specific endpoints
        self.app.router.add_get('/api/devstack/agents', self.get_agents)
        self.app.router.add_post('/api/devstack/agents/{agent_name}/activate', self.activate_agent)
        self.app.router.add_post('/api/devstack/agents/{agent_name}/deactivate', self.deactivate_agent)
        
        self.app.router.add_get('/api/devstack/tasks', self.get_tasks)
        self.app.router.add_post('/api/devstack/tasks', self.create_task)
        self.app.router.add_put('/api/devstack/tasks/{task_id}', self.update_task)
        
        self.app.router.add_get('/api/devstack/hooks', self.get_hooks)
        self.app.router.add_post('/api/devstack/hooks/trigger', self.trigger_hook)
        
        self.app.router.add_get('/api/devstack/audio', self.get_audio_events)
        self.app.router.add_post('/api/devstack/audio/event', self.log_audio_event)
        
        # WebSocket endpoint for real-time updates
        self.app.router.add_get('/ws', self.websocket_handler)
        
        # Attribution and license endpoint
        self.app.router.add_get('/api/attribution', self.get_attribution)
        
        # Proxy endpoints to original browser (AGPL compliance)
        self.app.router.add_get('/api/browser/{path:.*}', self.proxy_to_browser)
        
        # Health check
        self.app.router.add_get('/health', self.health_check)
    
    def _init_default_agents(self):
        """Initialize default Dev Stack agents."""
        agent_names = [
            "master-orchestrator", "frontend-architecture", "backend-services",
            "api-integration-specialist", "database-architect", "middleware-specialist",
            "technical-specifications", "business-tech-alignment", "technical-documentation",
            "devops-deployment", "security-architecture", "monitoring-observability",
            "performance-optimization", "quality-assurance", "user-experience",
            "product-strategy", "financial-modeling", "go-to-market",
            "legal-compliance", "data-analytics", "ai-ml-specialist",
            "mobile-development", "desktop-development", "game-development",
            "blockchain-development", "iot-development", "edge-computing",
            "cloud-infrastructure"
        ]
        
        current_time = time.time()
        for name in agent_names:
            self.agents[name] = AgentStatus(
                name=name,
                active=False,
                last_activity=current_time,
                tasks_completed=0
            )
    
    async def get_agents(self, request):
        """Get all agent statuses."""
        active_count = sum(1 for agent in self.agents.values() if agent.active)
        
        return web.json_response({
            "agents": [asdict(agent) for agent in self.agents.values()],
            "summary": {
                "active": active_count,
                "total": len(self.agents)
            }
        })
    
    async def activate_agent(self, request):
        """Activate an agent."""
        agent_name = request.match_info['agent_name']
        
        if agent_name in self.agents:
            self.agents[agent_name].active = True
            self.agents[agent_name].last_activity = time.time()
            
            await self._broadcast_update('agent-update', {
                "active": sum(1 for a in self.agents.values() if a.active),
                "total": len(self.agents)
            })
            
            return web.json_response({"status": "activated"})
        
        return web.json_response({"error": "Agent not found"}, status=404)
    
    async def deactivate_agent(self, request):
        """Deactivate an agent."""
        agent_name = request.match_info['agent_name']
        
        if agent_name in self.agents:
            self.agents[agent_name].active = False
            
            await self._broadcast_update('agent-update', {
                "active": sum(1 for a in self.agents.values() if a.active),
                "total": len(self.agents)
            })
            
            return web.json_response({"status": "deactivated"})
        
        return web.json_response({"error": "Agent not found"}, status=404)
    
    async def get_tasks(self, request):
        """Get all tasks."""
        completed_count = sum(1 for task in self.tasks.values() if task.status == "completed")
        
        return web.json_response({
            "tasks": [asdict(task) for task in self.tasks.values()],
            "summary": {
                "completed": completed_count,
                "total": len(self.tasks)
            }
        })
    
    async def create_task(self, request):
        """Create a new task."""
        data = await request.json()
        task_id = f"task_{int(time.time() * 1000)}"
        
        task = TaskInfo(
            id=task_id,
            name=data.get('name', 'Unnamed Task'),
            status='pending',
            progress=0.0,
            started_at=time.time(),
            agent=data.get('agent')
        )
        
        self.tasks[task_id] = task
        
        await self._broadcast_update('task-update', {
            "completed": sum(1 for t in self.tasks.values() if t.status == "completed"),
            "total": len(self.tasks)
        })
        
        return web.json_response(asdict(task))
    
    async def update_task(self, request):
        """Update an existing task."""
        task_id = request.match_info['task_id']
        data = await request.json()
        
        if task_id in self.tasks:
            task = self.tasks[task_id]
            
            if 'status' in data:
                task.status = data['status']
                if data['status'] == 'completed':
                    task.completed_at = time.time()
                    task.progress = 100.0
            
            if 'progress' in data:
                task.progress = data['progress']
            
            await self._broadcast_update('task-update', {
                "completed": sum(1 for t in self.tasks.values() if t.status == "completed"),
                "total": len(self.tasks)
            })
            
            return web.json_response(asdict(task))
        
        return web.json_response({"error": "Task not found"}, status=404)
    
    async def get_hooks(self, request):
        """Get hook events."""
        return web.json_response({
            "hooks": [asdict(hook) for hook in self.hooks[-100:]],  # Last 100 events
            "summary": {
                "triggered": len(self.hooks),
                "total": 28  # Total available hooks
            }
        })
    
    async def trigger_hook(self, request):
        """Trigger a hook event."""
        data = await request.json()
        
        hook_event = HookEvent(
            name=data.get('name', 'unknown'),
            triggered_at=time.time(),
            status='triggered',
            payload=data.get('payload', {})
        )
        
        self.hooks.append(hook_event)
        
        await self._broadcast_update('hook-update', {
            "triggered": len(self.hooks),
            "total": 28
        })
        
        return web.json_response(asdict(hook_event))
    
    async def get_audio_events(self, request):
        """Get audio events."""
        return web.json_response({
            "events": [asdict(event) for event in self.audio_events[-50:]],  # Last 50 events
            "last_event": asdict(self.audio_events[-1]) if self.audio_events else None
        })
    
    async def log_audio_event(self, request):
        """Log an audio event."""
        data = await request.json()
        
        audio_event = AudioEvent(
            file_path=data.get('file_path', ''),
            event_type=data.get('event_type', 'unknown'),
            timestamp=time.time(),
            duration=data.get('duration')
        )
        
        self.audio_events.append(audio_event)
        
        await self._broadcast_update('audio-event', {
            "file": audio_event.file_path,
            "type": audio_event.event_type
        })
        
        return web.json_response(asdict(audio_event))
    
    async def websocket_handler(self, request):
        """Handle WebSocket connections for real-time updates."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.websocket_clients.add(ws)
        print(f"🔌 WebSocket client connected to Dev Stack API ({len(self.websocket_clients)} total)")
        
        try:
            # Send initial state
            await ws.send_str(json.dumps({
                "type": "initial-state",
                "payload": {
                    "agents": {
                        "active": sum(1 for a in self.agents.values() if a.active),
                        "total": len(self.agents)
                    },
                    "tasks": {
                        "completed": sum(1 for t in self.tasks.values() if t.status == "completed"),
                        "total": len(self.tasks)
                    },
                    "hooks": {
                        "triggered": len(self.hooks),
                        "total": 28
                    }
                }
            }))
            
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    # Handle incoming messages if needed
                    pass
                elif msg.type == WSMsgType.ERROR:
                    print(f'WebSocket error: {ws.exception()}')
                    break
                    
        except Exception as e:
            print(f"WebSocket error: {e}")
        finally:
            self.websocket_clients.discard(ws)
            print(f"🔌 WebSocket client disconnected from Dev Stack API ({len(self.websocket_clients)} total)")
        
        return ws
    
    async def get_attribution(self, request):
        """Get attribution and license information."""
        return web.json_response(attribution.get_license_info())
    
    async def proxy_to_browser(self, request):
        """Proxy requests to the original browser server."""
        path = request.match_info['path']
        browser_url = f"http://localhost:{self.adapter.config.browser_port}/api/{path}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(browser_url) as response:
                    data = await response.text()
                    return web.Response(text=data, content_type=response.content_type)
        except Exception as e:
            return web.json_response({"error": f"Proxy error: {str(e)}"}, status=500)
    
    async def health_check(self, request):
        """Health check endpoint."""
        return web.json_response({
            "status": "healthy",
            "timestamp": time.time(),
            "attribution": "Claude Code Browser by @zainhoda (AGPL-3.0)",
            "integration": "Dev Stack v3.0 adapter pattern"
        })
    
    async def _broadcast_update(self, update_type: str, data: Dict[str, Any]):
        """Broadcast updates to all connected WebSocket clients."""
        if self.websocket_clients:
            message = json.dumps({
                "type": update_type,
                "payload": data,
                "timestamp": time.time()
            })
            
            disconnected = set()
            for client in self.websocket_clients:
                try:
                    await client.send_str(message)
                except:
                    disconnected.add(client)
            
            # Remove disconnected clients
            self.websocket_clients -= disconnected
    
    async def start(self):
        """Start the API server."""
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, 'localhost', self.port)
        await site.start()
        
        print(f"🚀 Dev Stack API server started on http://localhost:{self.port}")
        print(f"   Attribution: Claude Code Browser by @zainhoda (AGPL-3.0)")
        print(f"   WebSocket: ws://localhost:{self.port}/ws")
    
    async def stop(self):
        """Stop the API server."""
        await self.app.shutdown()
        await self.app.cleanup()