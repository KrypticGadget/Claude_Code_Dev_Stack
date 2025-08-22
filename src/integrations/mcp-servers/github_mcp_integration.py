#!/usr/bin/env python3
"""
GitHub MCP Integration
Integration layer for GitHub MCP server with Claude Code ecosystem

Features:
- Service registration with MCP Manager
- WebSocket client for real-time events
- Configuration management
- Health monitoring
- Event broadcasting
- API client wrapper
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field

import httpx
import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException

from github_mcp_service import GitHubMCPService, ServiceConfig

logger = logging.getLogger(__name__)

@dataclass
class WebSocketEvent:
    """WebSocket event structure"""
    type: str
    data: Dict[str, Any]
    timestamp: datetime
    source: str = "github_mcp"

class GitHubMCPClient:
    """Client for interacting with GitHub MCP server"""
    
    def __init__(self, base_url: str, auth_token: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.session = httpx.AsyncClient(timeout=30.0)
        
        # Setup headers
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "GitHub-MCP-Client/2.0.0"
        }
        
        if auth_token:
            self.headers["Authorization"] = f"Bearer {auth_token}"
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.aclose()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check server health"""
        response = await self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get server metrics"""
        response = await self.session.get(f"{self.base_url}/metrics")
        response.raise_for_status()
        return response.json()
    
    async def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository information"""
        response = await self.session.get(
            f"{self.base_url}/repos/{owner}/{repo}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    async def get_file_content(
        self, 
        owner: str, 
        repo: str, 
        path: str, 
        ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get file content from repository"""
        params = {}
        if ref:
            params["ref"] = ref
        
        response = await self.session.get(
            f"{self.base_url}/repos/{owner}/{repo}/contents/{path}",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    async def create_or_update_file(
        self,
        owner: str,
        repo: str,
        path: str,
        content: str,
        message: str,
        branch: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create or update file in repository"""
        data = {
            "content": content,
            "message": message
        }
        if branch:
            data["branch"] = branch
        
        response = await self.session.put(
            f"{self.base_url}/repos/{owner}/{repo}/contents/{path}",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    async def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        head: str,
        base: str,
        body: str = ""
    ) -> Dict[str, Any]:
        """Create a pull request"""
        data = {
            "title": title,
            "head": head,
            "base": base,
            "body": body
        }
        
        response = await self.session.post(
            f"{self.base_url}/repos/{owner}/{repo}/pulls",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    async def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str = "",
        labels: List[str] = None,
        assignee: str = None
    ) -> Dict[str, Any]:
        """Create an issue"""
        data = {
            "title": title,
            "body": body
        }
        if labels:
            data["labels"] = labels
        if assignee:
            data["assignee"] = assignee
        
        response = await self.session.post(
            f"{self.base_url}/repos/{owner}/{repo}/issues",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    async def search_repositories(
        self,
        query: str,
        sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search repositories"""
        params = {"q": query}
        if sort:
            params["sort"] = sort
        
        response = await self.session.get(
            f"{self.base_url}/search/repositories",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    async def search_code(
        self,
        query: str,
        sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search code"""
        params = {"q": query}
        if sort:
            params["sort"] = sort
        
        response = await self.session.get(
            f"{self.base_url}/search/code",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

class GitHubMCPWebSocketClient:
    """WebSocket client for real-time GitHub events"""
    
    def __init__(self, websocket_url: str, user_id: str):
        self.websocket_url = websocket_url
        self.user_id = user_id
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.connected = False
        self.subscribed_events: set = set()
        self.event_handlers: Dict[str, List[Callable]] = {}
        self._running = False
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 5
        self._reconnect_delay = 5
    
    def add_event_handler(self, event_type: str, handler: Callable[[WebSocketEvent], None]):
        """Add event handler for specific event type"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def remove_event_handler(self, event_type: str, handler: Callable):
        """Remove event handler"""
        if event_type in self.event_handlers:
            self.event_handlers[event_type].remove(handler)
    
    async def connect(self):
        """Connect to WebSocket server"""
        try:
            self.websocket = await websockets.connect(f"{self.websocket_url}/{self.user_id}")
            self.connected = True
            self._reconnect_attempts = 0
            logger.info(f"WebSocket connected: {self.user_id}")
            
            # Subscribe to all events by default
            await self.subscribe(["all"])
            
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            self.connected = False
            raise
    
    async def disconnect(self):
        """Disconnect from WebSocket server"""
        self._running = False
        if self.websocket and self.connected:
            await self.websocket.close()
            self.connected = False
            logger.info("WebSocket disconnected")
    
    async def subscribe(self, events: List[str]):
        """Subscribe to specific events"""
        if not self.connected:
            raise RuntimeError("WebSocket not connected")
        
        self.subscribed_events.update(events)
        await self.websocket.send(json.dumps({
            "type": "subscribe",
            "events": events
        }))
    
    async def unsubscribe(self, events: List[str]):
        """Unsubscribe from specific events"""
        if not self.connected:
            raise RuntimeError("WebSocket not connected")
        
        self.subscribed_events.difference_update(events)
        await self.websocket.send(json.dumps({
            "type": "unsubscribe",
            "events": events
        }))
    
    async def start_listening(self):
        """Start listening for WebSocket events"""
        self._running = True
        
        while self._running:
            try:
                if not self.connected:
                    await self._reconnect()
                
                # Listen for messages
                async for message in self.websocket:
                    try:
                        data = json.loads(message)
                        await self._handle_message(data)
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON received: {e}")
                    except Exception as e:
                        logger.error(f"Error handling message: {e}")
                        
            except ConnectionClosed:
                logger.warning("WebSocket connection closed")
                self.connected = False
                if self._running:
                    await self._reconnect()
            except WebSocketException as e:
                logger.error(f"WebSocket error: {e}")
                self.connected = False
                if self._running:
                    await self._reconnect()
            except Exception as e:
                logger.error(f"Unexpected error in WebSocket listener: {e}")
                await asyncio.sleep(1)
    
    async def _reconnect(self):
        """Attempt to reconnect to WebSocket"""
        if self._reconnect_attempts >= self._max_reconnect_attempts:
            logger.error("Max reconnection attempts reached")
            self._running = False
            return
        
        self._reconnect_attempts += 1
        logger.info(f"Attempting to reconnect... (attempt {self._reconnect_attempts})")
        
        await asyncio.sleep(self._reconnect_delay)
        
        try:
            await self.connect()
        except Exception as e:
            logger.error(f"Reconnection attempt failed: {e}")
    
    async def _handle_message(self, data: Dict[str, Any]):
        """Handle incoming WebSocket message"""
        message_type = data.get("type")
        
        if message_type == "connected":
            logger.info("WebSocket connection confirmed")
        elif message_type == "heartbeat":
            # Respond to heartbeat
            await self.websocket.send(json.dumps({"type": "pong"}))
        elif message_type == "subscribed":
            logger.info(f"Subscribed to events: {data.get('events', [])}")
        elif message_type == "unsubscribed":
            logger.info(f"Unsubscribed from events: {data.get('events', [])}")
        else:
            # Handle event
            event = WebSocketEvent(
                type=message_type,
                data=data.get("data", {}),
                timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
                source="github_mcp"
            )
            
            await self._dispatch_event(event)
    
    async def _dispatch_event(self, event: WebSocketEvent):
        """Dispatch event to registered handlers"""
        # Call handlers for specific event type
        if event.type in self.event_handlers:
            for handler in self.event_handlers[event.type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler: {e}")
        
        # Call handlers for "all" events
        if "all" in self.event_handlers:
            for handler in self.event_handlers["all"]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler: {e}")

class GitHubMCPIntegration:
    """Main integration class for GitHub MCP"""
    
    def __init__(
        self,
        config_file: Path = None,
        mcp_manager_url: str = "http://localhost:8000"
    ):
        self.config_file = config_file or Path("github_mcp_config.yml")
        self.mcp_manager_url = mcp_manager_url
        
        # Load configuration
        self.config = ServiceConfig.from_file(self.config_file)
        
        # Initialize service
        self.service = GitHubMCPService(self.config, self.config_file)
        
        # Initialize client components
        self.client: Optional[GitHubMCPClient] = None
        self.websocket_client: Optional[GitHubMCPWebSocketClient] = None
        
        # Service state
        self.registered = False
        self.running = False
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {}
    
    async def start(self) -> bool:
        """Start the GitHub MCP integration"""
        logger.info("Starting GitHub MCP integration...")
        
        try:
            # Start the service
            if not await self.service.start():
                logger.error("Failed to start GitHub MCP service")
                return False
            
            # Wait for service to be ready
            await asyncio.sleep(5)
            
            # Initialize client
            service_url = f"http://{self.config.host}:{self.config.port}"
            self.client = GitHubMCPClient(service_url, self.config.github_token)
            
            # Test connection
            try:
                await self.client.health_check()
                logger.info("GitHub MCP service is healthy")
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                return False
            
            # Initialize WebSocket client
            websocket_url = f"ws://{self.config.host}:{self.config.port}/ws"
            self.websocket_client = GitHubMCPWebSocketClient(websocket_url, "integration_client")
            
            # Setup default event handlers
            self._setup_default_event_handlers()
            
            # Connect WebSocket
            await self.websocket_client.connect()
            
            # Start WebSocket listener
            asyncio.create_task(self.websocket_client.start_listening())
            
            # Register with MCP Manager
            await self._register_with_mcp_manager()
            
            self.running = True
            logger.info("GitHub MCP integration started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start GitHub MCP integration: {e}")
            return False
    
    async def stop(self):
        """Stop the GitHub MCP integration"""
        logger.info("Stopping GitHub MCP integration...")
        
        self.running = False
        
        # Disconnect WebSocket
        if self.websocket_client:
            await self.websocket_client.disconnect()
        
        # Close client
        if self.client:
            await self.client.session.aclose()
        
        # Unregister from MCP Manager
        await self._unregister_from_mcp_manager()
        
        # Stop service
        await self.service.stop()
        
        logger.info("GitHub MCP integration stopped")
    
    def add_event_handler(self, event_type: str, handler: Callable):
        """Add event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        
        if self.websocket_client:
            self.websocket_client.add_event_handler(event_type, handler)
    
    async def _setup_default_event_handlers(self):
        """Setup default event handlers"""
        async def log_event(event: WebSocketEvent):
            logger.info(f"GitHub event: {event.type} - {event.data}")
        
        self.websocket_client.add_event_handler("all", log_event)
    
    async def _register_with_mcp_manager(self):
        """Register service with MCP Manager"""
        try:
            service_info = {
                "id": f"github-mcp-{self.config.port}",
                "name": "GitHub MCP Service",
                "type": "github",
                "host": self.config.host,
                "port": self.config.port,
                "path": "/",
                "protocol": "http",
                "description": "GitHub repository management and operations service",
                "tags": ["git", "github", "repository", "mcp"],
                "metadata": {
                    "version": "2.0.0",
                    "capabilities": [
                        "repository_management",
                        "file_operations",
                        "pull_requests",
                        "issues",
                        "search",
                        "webhooks",
                        "websockets"
                    ]
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.mcp_manager_url}/services/register",
                    json=service_info,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    self.registered = True
                    logger.info("Registered with MCP Manager")
                else:
                    logger.warning(f"Failed to register with MCP Manager: {response.status_code}")
                    
        except Exception as e:
            logger.warning(f"MCP Manager registration failed: {e}")
    
    async def _unregister_from_mcp_manager(self):
        """Unregister service from MCP Manager"""
        if not self.registered:
            return
        
        try:
            service_id = f"github-mcp-{self.config.port}"
            
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.mcp_manager_url}/services/{service_id}",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    logger.info("Unregistered from MCP Manager")
                else:
                    logger.warning(f"Failed to unregister from MCP Manager: {response.status_code}")
                    
        except Exception as e:
            logger.warning(f"MCP Manager unregistration failed: {e}")
        
        self.registered = False
    
    async def get_status(self) -> Dict[str, Any]:
        """Get integration status"""
        service_status = await self.service.get_status()
        
        status = {
            "integration": {
                "running": self.running,
                "registered": self.registered,
                "mcp_manager_url": self.mcp_manager_url
            },
            "service": service_status,
            "client": {
                "connected": self.client is not None,
                "websocket_connected": self.websocket_client.connected if self.websocket_client else False
            }
        }
        
        if self.client:
            try:
                health = await self.client.health_check()
                status["health"] = health
            except Exception as e:
                status["health"] = {"error": str(e)}
        
        return status

# Factory function
def create_github_mcp_integration(
    config_file: Path = None,
    mcp_manager_url: str = "http://localhost:8000"
) -> GitHubMCPIntegration:
    """Create GitHub MCP integration instance"""
    return GitHubMCPIntegration(config_file, mcp_manager_url)

# CLI interface
async def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GitHub MCP Integration")
    parser.add_argument("action", choices=["start", "stop", "status", "test"])
    parser.add_argument("--config", type=Path, help="Configuration file path")
    parser.add_argument("--mcp-manager", default="http://localhost:8000", help="MCP Manager URL")
    
    args = parser.parse_args()
    
    integration = create_github_mcp_integration(args.config, args.mcp_manager)
    
    if args.action == "start":
        success = await integration.start()
        if success:
            print("GitHub MCP integration started successfully")
            # Keep running
            try:
                while integration.running:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\nShutting down...")
                await integration.stop()
        else:
            print("Failed to start GitHub MCP integration")
    
    elif args.action == "stop":
        await integration.stop()
        print("GitHub MCP integration stopped")
    
    elif args.action == "status":
        status = await integration.get_status()
        print(json.dumps(status, indent=2, default=str))
    
    elif args.action == "test":
        # Test integration
        success = await integration.start()
        if success:
            try:
                # Test API calls
                if integration.client:
                    health = await integration.client.health_check()
                    print(f"Health check: {health}")
                    
                    # Test repository access
                    try:
                        repo = await integration.client.get_repository("octocat", "Hello-World")
                        print(f"Repository test: {repo['name']}")
                    except Exception as e:
                        print(f"Repository test failed: {e}")
                
                print("Integration test completed")
            finally:
                await integration.stop()
        else:
            print("Failed to start integration for testing")

if __name__ == "__main__":
    asyncio.run(main())