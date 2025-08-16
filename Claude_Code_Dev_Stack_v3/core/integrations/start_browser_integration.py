#!/usr/bin/env python3
"""
Claude Code Browser Integration Startup Script
==============================================

Start the complete Claude Code Browser integration with Dev Stack v3.0.
This script initializes all components and ensures proper attribution.

Attribution:
- Original Claude Code Browser by @zainhoda (AGPL-3.0)
- Integration by Claude Code Dev Stack v3.0 (AGPL-3.0)
"""

import os
import sys
import asyncio
import logging
import signal
import argparse
from datetime import datetime
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from browser_adapter import start_browser_integration, get_browser_adapter
    ADAPTER_AVAILABLE = True
except ImportError as e:
    print(f"❌ Browser adapter not available: {e}")
    print("📦 Installing required dependencies...")
    
    import subprocess
    subprocess.run([
        sys.executable, "-m", "pip", "install", 
        "websockets", "aiohttp", "aiofiles"
    ], check=True)
    
    try:
        from browser_adapter import start_browser_integration, get_browser_adapter
        ADAPTER_AVAILABLE = True
    except ImportError:
        ADAPTER_AVAILABLE = False
        print("❌ Failed to import browser adapter after installing dependencies")

# Import hook integration
try:
    from ..hooks.hooks.browser_integration_hook import get_browser_integration_hook
    HOOK_AVAILABLE = True
except ImportError:
    HOOK_AVAILABLE = False
    print("⚠️  Browser integration hook not available")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('browser_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BrowserIntegrationStarter:
    """
    Manages the startup and lifecycle of the Claude Code Browser integration
    """
    
    def __init__(self, websocket_port=8081, http_port=8082):
        self.websocket_port = websocket_port
        self.http_port = http_port
        self.adapter = None
        self.hook = None
        self.websocket_server = None
        self.http_runner = None
        self.running = False
        
        # License compliance and attribution
        self.attribution_info = {
            "integration_started": datetime.now().isoformat(),
            "original_project": {
                "name": "Claude Code Browser",
                "author": "@zainhoda",
                "repository": "https://github.com/zainhoda/claude-code-browser",
                "license": "AGPL-3.0",
                "original_work": "Browser monitoring and session management"
            },
            "integration_project": {
                "name": "Claude Code Dev Stack v3.0",
                "integration_components": [
                    "WebSocket real-time updates",
                    "Dev Stack command parsing",
                    "Hook system integration",
                    "PWA frontend integration"
                ],
                "license": "AGPL-3.0",
                "compliance_verified": True
            },
            "legal_notices": {
                "agpl_compliance": "Source code available under AGPL-3.0",
                "attribution_maintained": "Original author @zainhoda properly credited",
                "derivative_work": "Integration adapter is derivative work under AGPL-3.0"
            }
        }
    
    def print_startup_banner(self):
        """Print startup banner with attribution"""
        print("\n" + "="*80)
        print("🚀 Claude Code Browser Integration v3.0")
        print("="*80)
        print("📦 Original Claude Code Browser by @zainhoda (AGPL-3.0)")
        print("🔧 Integration by Claude Code Dev Stack v3.0 (AGPL-3.0)")
        print("📄 License: AGPL-3.0 (Source Available)")
        print("🔗 WebSocket: ws://localhost:{}".format(self.websocket_port))
        print("🌐 HTTP API: http://localhost:{}".format(self.http_port))
        print("="*80)
        
        # Print component status
        print("📊 Component Status:")
        print(f"   ✅ Browser Adapter: {'Available' if ADAPTER_AVAILABLE else '❌ Not Available'}")
        print(f"   ✅ Hook Integration: {'Available' if HOOK_AVAILABLE else '❌ Not Available'}")
        print("="*80)
        
        # Print legal notices
        print("⚖️  Legal Compliance:")
        print("   📋 AGPL-3.0 License: Source code available")
        print("   👤 Attribution: @zainhoda properly credited")
        print("   🔗 Original: https://github.com/zainhoda/claude-code-browser")
        print("   🆕 Integration: Claude Code Dev Stack v3.0")
        print("="*80 + "\n")
    
    def check_dependencies(self):
        """Check if all dependencies are available"""
        issues = []
        
        if not ADAPTER_AVAILABLE:
            issues.append("Browser adapter not available")
        
        if not HOOK_AVAILABLE:
            issues.append("Hook integration not available")
        
        # Check for Claude Code Browser data directory
        browser_data_path = os.path.expanduser("~/.claude/projects")
        if not os.path.exists(browser_data_path):
            issues.append(f"Claude Code Browser data directory not found: {browser_data_path}")
            print(f"💡 To create sample data directory: mkdir -p {browser_data_path}")
        
        return issues
    
    async def start_integration(self):
        """Start the complete browser integration"""
        if not ADAPTER_AVAILABLE:
            logger.error("Cannot start integration - browser adapter not available")
            return False
        
        try:
            # Print startup information
            self.print_startup_banner()
            
            # Check dependencies
            issues = self.check_dependencies()
            if issues:
                logger.warning(f"Dependency issues found: {issues}")
                for issue in issues:
                    print(f"⚠️  {issue}")
            
            # Initialize hook integration
            if HOOK_AVAILABLE:
                self.hook = get_browser_integration_hook()
                logger.info("✅ Browser integration hook initialized")
            
            # Start browser integration
            logger.info("🚀 Starting browser integration servers...")
            self.adapter, self.websocket_server, self.http_runner = await start_browser_integration(
                websocket_port=self.websocket_port,
                http_port=self.http_port
            )
            
            self.running = True
            
            # Log successful startup
            logger.info("✅ Browser integration started successfully")
            logger.info(f"📡 WebSocket server: ws://localhost:{self.websocket_port}")
            logger.info(f"🌐 HTTP API server: http://localhost:{self.http_port}")
            
            # Print integration status
            self.print_integration_status()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start browser integration: {e}")
            return False
    
    def print_integration_status(self):
        """Print current integration status"""
        if self.adapter:
            status = self.adapter.get_integration_status()
            
            print("\n📊 Integration Status:")
            print(f"   🟢 Adapter Status: {status['adapter_status']}")
            print(f"   📁 Projects Cached: {status['cache_info']['projects']}")
            print(f"   📄 Sessions Cached: {status['cache_info']['sessions']}")
            print(f"   🔗 WebSocket Connections: {status['websocket_info']['connections']}")
            print(f"   📈 Commands Parsed: {status['metrics']['commands_parsed']}")
            print(f"   🔄 Integration Events: {status['metrics']['integration_events']}")
            
            if self.hook:
                hook_status = self.hook.get_hook_status()
                print(f"   🎯 Hook Active: {hook_status['is_active']}")
                print(f"   📊 Hook Events: {hook_status['stats']['events_processed']}")
            
            print()
    
    async def shutdown(self):
        """Gracefully shutdown the integration"""
        logger.info("🛑 Shutting down browser integration...")
        
        self.running = False
        
        # Stop monitoring
        if self.adapter:
            self.adapter.stop_real_time_monitoring()
        
        # Close WebSocket server
        if self.websocket_server:
            self.websocket_server.close()
            await self.websocket_server.wait_closed()
        
        # Stop HTTP server
        if self.http_runner:
            await self.http_runner.cleanup()
        
        logger.info("✅ Browser integration shutdown complete")
    
    def handle_signal(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"📡 Received signal {signum}, initiating shutdown...")
        asyncio.create_task(self.shutdown())
    
    async def run_forever(self):
        """Run the integration indefinitely"""
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)
        
        # Start integration
        success = await self.start_integration()
        
        if not success:
            logger.error("❌ Failed to start integration")
            return
        
        # Run until shutdown
        try:
            while self.running:
                await asyncio.sleep(1)
                
                # Periodic status updates
                if hasattr(self, '_last_status_update'):
                    if datetime.now().timestamp() - self._last_status_update > 300:  # Every 5 minutes
                        self.print_integration_status()
                        self._last_status_update = datetime.now().timestamp()
                else:
                    self._last_status_update = datetime.now().timestamp()
                    
        except asyncio.CancelledError:
            logger.info("📡 Integration cancelled")
        except Exception as e:
            logger.error(f"❌ Integration error: {e}")
        finally:
            await self.shutdown()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Start Claude Code Browser Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Attribution:
  Original Claude Code Browser by @zainhoda (AGPL-3.0)
  Integration by Claude Code Dev Stack v3.0 (AGPL-3.0)
  
License Compliance:
  This integration maintains AGPL-3.0 compliance and proper attribution.
  Source code is available and derivative works must also be AGPL-3.0.
        """
    )
    
    parser.add_argument(
        '--websocket-port', 
        type=int, 
        default=8081,
        help='WebSocket server port (default: 8081)'
    )
    
    parser.add_argument(
        '--http-port',
        type=int,
        default=8082, 
        help='HTTP API server port (default: 8082)'
    )
    
    parser.add_argument(
        '--browser-data-path',
        type=str,
        default=None,
        help='Path to Claude Code Browser data (default: ~/.claude/projects)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only check dependencies and exit'
    )
    
    parser.add_argument(
        '--attribution',
        action='store_true',
        help='Show attribution information and exit'
    )
    
    args = parser.parse_args()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Create integration starter
    starter = BrowserIntegrationStarter(
        websocket_port=args.websocket_port,
        http_port=args.http_port
    )
    
    # Handle special commands
    if args.attribution:
        print(json.dumps(starter.attribution_info, indent=2))
        return
    
    if args.check_only:
        starter.print_startup_banner()
        issues = starter.check_dependencies()
        if issues:
            print("❌ Issues found:")
            for issue in issues:
                print(f"   - {issue}")
            sys.exit(1)
        else:
            print("✅ All dependencies satisfied")
            sys.exit(0)
    
    # Set browser data path if provided
    if args.browser_data_path:
        os.environ['BROWSER_DATA_PATH'] = args.browser_data_path
    
    # Run the integration
    try:
        asyncio.run(starter.run_forever())
    except KeyboardInterrupt:
        logger.info("🛑 Integration stopped by user")
    except Exception as e:
        logger.error(f"❌ Integration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()