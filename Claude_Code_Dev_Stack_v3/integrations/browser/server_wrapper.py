"""
Extended Server Wrapper
=======================

Main server wrapper that combines the original Claude Code Browser
(@zainhoda, AGPL-3.0) with Dev Stack v3.0 extensions using an adapter
pattern to maintain license compliance and proper attribution.
"""

import asyncio
import signal
import sys
import os
import json
import time
from typing import Optional
from pathlib import Path

from adapter import ClaudeCodeBrowserAdapter, BrowserConfig
from api_endpoints import DevStackAPIServer
from streaming import StreamingManager, StreamingConfig
from attribution import attribution

class ExtendedServer:
    """
    Extended server that wraps the original Claude Code Browser with
    Dev Stack v3.0 functionality while maintaining license compliance.
    """
    
    def __init__(self, 
                 browser_config: Optional[BrowserConfig] = None,
                 streaming_config: Optional[StreamingConfig] = None):
        
        self.browser_config = browser_config or BrowserConfig()
        self.streaming_config = streaming_config or StreamingConfig()
        
        # Core components
        self.browser_adapter = ClaudeCodeBrowserAdapter(self.browser_config)
        self.api_server = DevStackAPIServer(self.browser_adapter, port=self.browser_config.devstack_port)
        self.streaming_manager = StreamingManager(self.streaming_config)
        
        # State
        self.is_running = False
        self.startup_time = None
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    async def start(self):
        """Start the extended server with all components."""
        self.startup_time = time.time()
        
        print("🚀 Starting Claude Code Browser Extended Server")
        print("=" * 60)
        
        # Show attribution
        print(attribution.get_attribution_notice())
        print("=" * 60)
        
        try:
            # Start original browser server
            print("📊 Starting original Claude Code Browser...")
            if not await self.browser_adapter.start_browser_server():
                raise Exception("Failed to start browser server")
            
            # Start Dev Stack API server
            print("🔧 Starting Dev Stack API extensions...")
            await self.api_server.start()
            
            # Start streaming services (optional)
            if self.streaming_config.webrtc_enabled or self.streaming_config.novnc_enabled:
                print("🎥 Starting streaming services...")
                await self.streaming_manager.start_streaming_services()
            
            self.is_running = True
            
            # Show status
            await self._show_startup_status()
            
            # Main server loop
            await self._main_loop()
            
        except Exception as e:
            print(f"❌ Server startup failed: {e}")
            await self.stop()
            raise
    
    async def stop(self):
        """Stop the extended server and all components."""
        if not self.is_running:
            return
        
        print("\n🛑 Shutting down Extended Server...")
        
        self.is_running = False
        
        # Stop streaming services
        if hasattr(self.streaming_manager, 'stop_streaming_services'):
            self.streaming_manager.stop_streaming_services()
        
        # Stop API server
        if hasattr(self.api_server, 'stop'):
            await self.api_server.stop()
        
        # Stop browser adapter
        self.browser_adapter.stop_browser_server()
        
        print("✅ Extended Server stopped")
    
    async def _main_loop(self):
        """Main server loop for handling events and monitoring."""
        try:
            while self.is_running:
                # Update metrics periodically
                await self._update_metrics()
                
                # Health check
                await self._health_check()
                
                # Sleep for a short interval
                await asyncio.sleep(1)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"❌ Main loop error: {e}")
    
    async def _update_metrics(self):
        """Update system metrics."""
        try:
            # Simulate some metrics updates
            current_time = time.time()
            uptime = current_time - self.startup_time if self.startup_time else 0
            
            # Update agent metrics (simulated)
            if hasattr(self.api_server, 'agents'):
                active_agents = sum(1 for agent in self.api_server.agents.values() if agent.active)
                if active_agents != self.browser_adapter.devstack_metrics["agents"]["active"]:
                    self.browser_adapter.update_devstack_metrics("agents", {
                        "active": active_agents,
                        "total": len(self.api_server.agents)
                    })
            
            # Update task metrics
            if hasattr(self.api_server, 'tasks'):
                completed_tasks = sum(1 for task in self.api_server.tasks.values() if task.status == "completed")
                if completed_tasks != self.browser_adapter.devstack_metrics["tasks"]["completed"]:
                    self.browser_adapter.update_devstack_metrics("tasks", {
                        "completed": completed_tasks,
                        "total": len(self.api_server.tasks)
                    })
            
        except Exception as e:
            # Don't let metrics updates crash the server
            pass
    
    async def _health_check(self):
        """Perform health checks on all components."""
        try:
            # Check if browser server is responding
            import aiohttp
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(f"http://localhost:{self.browser_config.browser_port}/health", timeout=1) as response:
                        if response.status != 200:
                            print("⚠️ Browser server health check failed")
                except:
                    print("⚠️ Browser server not responding")
            
        except Exception as e:
            # Health checks shouldn't crash the server
            pass
    
    async def _show_startup_status(self):
        """Show startup status and service URLs."""
        print("\n✅ Extended Server Started Successfully!")
        print("-" * 60)
        print(f"🌐 Original Browser:    http://localhost:{self.browser_config.browser_port}")
        print(f"🔧 Dev Stack API:       http://localhost:{self.browser_config.devstack_port}")
        print(f"🔌 WebSocket:           ws://localhost:{self.browser_config.devstack_port}/ws")
        
        if self.streaming_config.webrtc_enabled:
            print(f"🎥 WebRTC Stream:       ws://localhost:{self.streaming_config.webrtc_port}")
        
        if self.streaming_config.novnc_enabled:
            print(f"🖥️ noVNC Access:        http://localhost:{self.streaming_config.novnc_port}")
        
        print("-" * 60)
        print("📊 Available Endpoints:")
        print("   Original Browser Endpoints (AGPL-3.0 by @zainhoda):")
        print("     GET  /                    - Project index")
        print("     GET  /project/{name}      - Project details")
        print("     GET  /session/{proj}/{id} - Session viewer")
        print("")
        print("   Dev Stack Extensions:")
        print("     GET  /api/devstack/agents - Agent management")
        print("     GET  /api/devstack/tasks  - Task monitoring")
        print("     GET  /api/devstack/hooks  - Hook events")
        print("     GET  /api/devstack/audio  - Audio events")
        print("     GET  /api/attribution     - License info")
        print("     GET  /health              - Health check")
        print("-" * 60)
        print("📋 Integration Status:")
        print(f"   Original Browser: ✅ Running (Port {self.browser_config.browser_port})")
        print(f"   Dev Stack API:    ✅ Running (Port {self.browser_config.devstack_port})")
        print(f"   WebRTC Streaming: {'✅ Enabled' if self.streaming_config.webrtc_enabled else '⚪ Disabled'}")
        print(f"   noVNC Access:     {'✅ Enabled' if self.streaming_config.novnc_enabled else '⚪ Disabled'}")
        print("-" * 60)
        print("⚖️ License Compliance:")
        print("   Original: AGPL-3.0 by @zainhoda")
        print("   Integration: AGPL-3.0 compatible")
        print("   Source: Available in clones/claude-code-browser/")
        print("   Attribution: Maintained and displayed")
        print("-" * 60)
        print("\n🎯 Ready for connections!")
        print("   Press Ctrl+C to stop the server")
        print("")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\n📡 Received signal {signum}")
        asyncio.create_task(self.stop())

class ServerConfiguration:
    """Server configuration management."""
    
    @staticmethod
    def load_config(config_path: str = None) -> tuple[BrowserConfig, StreamingConfig]:
        """Load configuration from file."""
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                
                browser_config = BrowserConfig(**config_data.get('browser', {}))
                streaming_config = StreamingConfig(**config_data.get('streaming', {}))
                
                return browser_config, streaming_config
                
            except Exception as e:
                print(f"⚠️ Failed to load config from {config_path}: {e}")
        
        # Return default configurations
        return BrowserConfig(), StreamingConfig()
    
    @staticmethod
    def save_default_config(config_path: str = "browser_config.json"):
        """Save default configuration to file."""
        config_data = {
            "browser": {
                "browser_port": 8080,
                "devstack_port": 8081,
                "go_binary_path": "clones/claude-code-browser/main",
                "claude_projects_path": os.path.expanduser("~/.claude/projects"),
                "streaming_enabled": True,
                "websocket_enabled": True
            },
            "streaming": {
                "webrtc_enabled": True,
                "novnc_enabled": False,
                "screen_capture_fps": 30,
                "max_resolution": [1920, 1080],
                "compression_quality": 80,
                "webrtc_port": 8082,
                "novnc_port": 8083
            }
        }
        
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        print(f"✅ Default configuration saved to {config_path}")

async def main():
    """Main entry point for the extended server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Claude Code Browser Extended Server")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--create-config", action="store_true", help="Create default configuration file")
    parser.add_argument("--browser-port", type=int, default=8080, help="Browser server port")
    parser.add_argument("--api-port", type=int, default=8081, help="Dev Stack API port")
    parser.add_argument("--no-streaming", action="store_true", help="Disable streaming services")
    
    args = parser.parse_args()
    
    if args.create_config:
        ServerConfiguration.save_default_config()
        return
    
    # Load configuration
    browser_config, streaming_config = ServerConfiguration.load_config(args.config)
    
    # Override with command line arguments
    if args.browser_port:
        browser_config.browser_port = args.browser_port
    if args.api_port:
        browser_config.devstack_port = args.api_port
    if args.no_streaming:
        streaming_config.webrtc_enabled = False
        streaming_config.novnc_enabled = False
    
    # Create and start server
    server = ExtendedServer(browser_config, streaming_config)
    
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\n👋 Shutdown requested by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
    finally:
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())