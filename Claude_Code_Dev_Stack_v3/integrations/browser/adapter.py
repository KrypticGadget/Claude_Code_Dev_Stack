"""
Claude Code Browser Adapter
==========================

Adapter pattern implementation for integrating Claude Code Browser (@zainhoda)
with the Dev Stack v3.0 system while maintaining AGPL-3.0 license compliance.

This adapter wraps the original Go-based browser server and extends it with
Dev Stack specific functionality without modifying the original codebase.
"""

import asyncio
import json
import subprocess
import signal
import os
import sys
from typing import Dict, Any, Optional, List
from pathlib import Path
import requests
import websockets
from dataclasses import dataclass
from attribution import attribution

@dataclass
class BrowserConfig:
    """Configuration for the browser adapter."""
    browser_port: int = 8080
    devstack_port: int = 8081
    go_binary_path: str = "clones/claude-code-browser/main"
    claude_projects_path: str = os.path.expanduser("~/.claude/projects")
    streaming_enabled: bool = True
    websocket_enabled: bool = True

class ClaudeCodeBrowserAdapter:
    """
    Adapter for Claude Code Browser integration.
    
    This class provides a Python interface to the original Go-based browser
    while adding Dev Stack specific extensions through an adapter pattern.
    """
    
    def __init__(self, config: BrowserConfig = None):
        self.config = config or BrowserConfig()
        self.browser_process: Optional[subprocess.Popen] = None
        self.devstack_metrics = {
            "agents": {"active": 0, "total": 28},
            "tasks": {"completed": 0, "total": 0},
            "hooks": {"triggered": 0, "total": 28},
            "audio": {"last_event": None}
        }
        self.connected_clients = set()
        
    async def start_browser_server(self) -> bool:
        """Start the original Claude Code Browser server."""
        try:
            # Build the Go binary if it doesn't exist
            if not os.path.exists(self.config.go_binary_path):
                await self._build_go_binary()
            
            # Start the original browser server
            self.browser_process = subprocess.Popen([
                self.config.go_binary_path,
                "--server",
                "--port", str(self.config.browser_port)
            ], cwd="clones/claude-code-browser")
            
            # Wait for server to be ready
            await self._wait_for_server_ready()
            
            print(f"✅ Claude Code Browser server started on port {self.config.browser_port}")
            print(f"   Original work by @zainhoda (AGPL-3.0)")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start browser server: {e}")
            return False
    
    async def _build_go_binary(self):
        """Build the Go binary for the browser."""
        print("📦 Building Claude Code Browser...")
        
        build_process = subprocess.Popen([
            "go", "build", "-o", "main", "."
        ], cwd="clones/claude-code-browser")
        
        build_process.wait()
        
        if build_process.returncode != 0:
            raise Exception("Failed to build Go binary")
            
        print("✅ Build completed")
    
    async def _wait_for_server_ready(self, timeout: int = 30):
        """Wait for the browser server to be ready."""
        for _ in range(timeout):
            try:
                response = requests.get(f"http://localhost:{self.config.browser_port}/", timeout=1)
                if response.status_code == 200:
                    return
            except:
                pass
            await asyncio.sleep(1)
        
        raise Exception("Browser server failed to start within timeout")
    
    def stop_browser_server(self):
        """Stop the browser server."""
        if self.browser_process:
            self.browser_process.terminate()
            self.browser_process.wait()
            print("🛑 Browser server stopped")
    
    async def get_projects(self) -> List[Dict[str, Any]]:
        """Get projects from the original browser server."""
        try:
            response = requests.get(f"http://localhost:{self.config.browser_port}/api/projects")
            return response.json()
        except Exception as e:
            print(f"❌ Failed to get projects: {e}")
            return []
    
    async def get_project_sessions(self, project_name: str) -> List[Dict[str, Any]]:
        """Get sessions for a specific project."""
        try:
            response = requests.get(f"http://localhost:{self.config.browser_port}/api/project/{project_name}")
            return response.json()
        except Exception as e:
            print(f"❌ Failed to get sessions for {project_name}: {e}")
            return []
    
    async def get_session_data(self, project_name: str, session_uuid: str) -> Dict[str, Any]:
        """Get session data from the original browser."""
        try:
            response = requests.get(f"http://localhost:{self.config.browser_port}/api/session/{project_name}/{session_uuid}")
            return response.json()
        except Exception as e:
            print(f"❌ Failed to get session data: {e}")
            return {}
    
    def update_devstack_metrics(self, metric_type: str, data: Dict[str, Any]):
        """Update Dev Stack specific metrics."""
        if metric_type in self.devstack_metrics:
            self.devstack_metrics[metric_type].update(data)
            
            # Broadcast to connected WebSocket clients
            asyncio.create_task(self._broadcast_metric_update(metric_type, data))
    
    async def _broadcast_metric_update(self, metric_type: str, data: Dict[str, Any]):
        """Broadcast metric updates to connected WebSocket clients."""
        if self.connected_clients:
            message = json.dumps({
                "type": f"{metric_type}-update",
                "payload": data,
                "timestamp": asyncio.get_event_loop().time()
            })
            
            disconnected = set()
            for client in self.connected_clients:
                try:
                    await client.send(message)
                except:
                    disconnected.add(client)
            
            # Remove disconnected clients
            self.connected_clients -= disconnected
    
    async def handle_websocket_connection(self, websocket, path):
        """Handle WebSocket connections for real-time updates."""
        self.connected_clients.add(websocket)
        print(f"🔌 WebSocket client connected ({len(self.connected_clients)} total)")
        
        try:
            # Send current metrics to new client
            await websocket.send(json.dumps({
                "type": "initial-state",
                "payload": self.devstack_metrics
            }))
            
            # Keep connection alive
            async for message in websocket:
                # Handle incoming messages if needed
                pass
                
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.connected_clients.discard(websocket)
            print(f"🔌 WebSocket client disconnected ({len(self.connected_clients)} total)")
    
    def get_attribution_info(self) -> Dict[str, Any]:
        """Get attribution information for the integrated browser."""
        return attribution.get_license_info()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_browser_server()

# Signal handler for graceful shutdown
def signal_handler(sig, frame, adapter: ClaudeCodeBrowserAdapter):
    print("\n🛑 Shutting down Claude Code Browser integration...")
    adapter.stop_browser_server()
    sys.exit(0)

if __name__ == "__main__":
    # Example usage
    async def main():
        adapter = ClaudeCodeBrowserAdapter()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, lambda s, f: signal_handler(s, f, adapter))
        signal.signal(signal.SIGTERM, lambda s, f: signal_handler(s, f, adapter))
        
        if await adapter.start_browser_server():
            print("🚀 Claude Code Browser integration running")
            print(f"   Original: http://localhost:{adapter.config.browser_port}")
            print(f"   Dev Stack: http://localhost:{adapter.config.devstack_port}")
            
            # Keep running
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                pass
        
        adapter.stop_browser_server()
    
    asyncio.run(main())