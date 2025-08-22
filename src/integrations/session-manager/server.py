"""
Claude Code Session Management Server
====================================

Main server entry point for the comprehensive session management API.
Provides complete session lifecycle management for Claude Code instances.
"""

import asyncio
import signal
import sys
import logging
from pathlib import Path

# Add the parent directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.session_api import SessionAPI


class SessionManagementServer:
    """
    Main server class for Claude Code session management.
    Handles startup, shutdown, and signal handling.
    """
    
    def __init__(self, port: int = 8082, log_level: str = "INFO"):
        self.port = port
        self.log_level = log_level
        self.api = None
        self.running = False
        
        # Setup logging
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
    
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(
                    Path.home() / ".claude" / "logs" / "session_manager.log",
                    mode='a'
                )
            ]
        )
        
        # Create log directory if it doesn't exist
        log_dir = Path.home() / ".claude" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
    
    async def start(self):
        """Start the session management server."""
        try:
            self.logger.info("Starting Claude Code Session Management Server...")
            
            # Create and start the API
            self.api = SessionAPI(port=self.port)
            await self.api.start()
            
            self.running = True
            self.logger.info("Session Management Server started successfully")
            
            # Print startup information
            self._print_startup_info()
            
            # Wait for shutdown signal
            await self._wait_for_shutdown()
            
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            raise
    
    async def stop(self):
        """Stop the session management server."""
        if not self.running:
            return
        
        self.logger.info("Stopping Session Management Server...")
        
        try:
            if self.api:
                await self.api.stop()
            
            self.running = False
            self.logger.info("Session Management Server stopped")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    def _print_startup_info(self):
        """Print startup information to console."""
        print("\n" + "="*60)
        print("🚀 Claude Code Session Management API")
        print("="*60)
        print(f"Server URL:     http://localhost:{self.port}")
        print(f"WebSocket:      ws://localhost:{self.port}/ws/sessions")
        print(f"Health Check:   http://localhost:{self.port}/health")
        print(f"System Status:  http://localhost:{self.port}/api/claude/system-status")
        print("\nAvailable Endpoints:")
        print("  Sessions:")
        print(f"    POST   /api/claude/sessions              - Create new session")
        print(f"    GET    /api/claude/sessions              - List sessions")
        print(f"    GET    /api/claude/sessions/{{id}}        - Get session details")
        print(f"    PUT    /api/claude/sessions/{{id}}        - Update session")
        print(f"    DELETE /api/claude/sessions/{{id}}        - Terminate session")
        print("\n  Session Operations:")
        print(f"    POST   /api/claude/sessions/{{id}}/navigate   - Navigate to path")
        print(f"    POST   /api/claude/sessions/{{id}}/clone      - Clone session")
        print(f"    POST   /api/claude/sessions/{{id}}/export     - Export session")
        print(f"    POST   /api/claude/sessions/import            - Import session")
        print("\n  Agent Management:")
        print(f"    GET    /api/claude/sessions/{{id}}/agents               - Get agents")
        print(f"    POST   /api/claude/sessions/{{id}}/agents/{{name}}/activate   - Activate agent")
        print(f"    POST   /api/claude/sessions/{{id}}/agents/{{name}}/deactivate - Deactivate agent")
        print(f"    POST   /api/claude/sessions/{{id}}/agents/{{name}}/restart    - Restart agent")
        print("\n  Monitoring:")
        print(f"    GET    /api/claude/sessions/{{id}}/metrics     - Get session metrics")
        print(f"    GET    /api/claude/sessions/{{id}}/status      - Get session status")
        print(f"    GET    /api/claude/analytics                   - Get system analytics")
        print("\n  Utilities:")
        print(f"    POST   /api/claude/validate-path              - Validate single path")
        print(f"    POST   /api/claude/validate-paths             - Validate multiple paths")
        print(f"    GET    /api/claude/agent-types                - Get available agent types")
        print("\nPress Ctrl+C to stop the server")
        print("="*60)
    
    async def _wait_for_shutdown(self):
        """Wait for shutdown signals."""
        # Setup signal handlers
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating shutdown...")
            asyncio.create_task(self.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Wait while running
        while self.running:
            await asyncio.sleep(1)


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Claude Code Session Management Server")
    parser.add_argument(
        "--port", 
        type=int, 
        default=8082, 
        help="Port to run the server on (default: 8082)"
    )
    parser.add_argument(
        "--log-level", 
        default="INFO", 
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Log level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Create and start server
    server = SessionManagementServer(
        port=args.port,
        log_level=args.log_level
    )
    
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)
    finally:
        await server.stop()


if __name__ == "__main__":
    # Handle Windows-specific event loop policy
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main())