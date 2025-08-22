#!/usr/bin/env python3
"""
Quick Start Script for Claude Code Session Management API
=========================================================

Simple script to start the session management server with default settings.
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from server import SessionManagementServer


async def main():
    """Quick start the session management server."""
    print("🚀 Starting Claude Code Session Management API...")
    print("   Default port: 8082")
    print("   Log level: INFO")
    print("   Press Ctrl+C to stop\n")
    
    # Create server with default settings
    server = SessionManagementServer(port=8082, log_level="INFO")
    
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\n\n👋 Session Management API stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)
    finally:
        await server.stop()


if __name__ == "__main__":
    # Handle Windows event loop policy
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main())