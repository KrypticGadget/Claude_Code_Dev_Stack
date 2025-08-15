#!/usr/bin/env python3
"""
Claude Code Browser Integration Startup Script
==============================================

Starts the complete Claude Code Browser integration with Dev Stack v3.0,
maintaining AGPL-3.0 license compliance and proper attribution to @zainhoda.

Usage:
    python start_integration.py [options]
    
Options:
    --browser-port PORT     Browser server port (default: 8080)
    --api-port PORT        Dev Stack API port (default: 8081)
    --no-streaming         Disable streaming services
    --config FILE          Configuration file
    --create-config        Create default configuration
    --check-deps           Check dependencies
    --verbose              Verbose logging
    --help                 Show this help
"""

import argparse
import asyncio
import sys
import os
import json
import subprocess
import shutil
from pathlib import Path

# Add the integration directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server_wrapper import ExtendedServer, ServerConfiguration
from adapter import BrowserConfig
from streaming import StreamingConfig
from attribution import attribution

class IntegrationLauncher:
    """Manages the startup and configuration of the browser integration."""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.claude_browser_path = self.base_path.parent.parent / "clones" / "claude-code-browser"
        
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are available."""
        print("🔍 Checking dependencies...")
        
        # Check Python dependencies
        missing_deps = []
        required_deps = [
            'aiohttp', 'aiofiles', 'websockets', 'requests', 
            'Pillow', 'numpy', 'opencv-python'
        ]
        
        for dep in required_deps:
            try:
                __import__(dep.replace('-', '_'))
                print(f"  ✅ {dep}")
            except ImportError:
                missing_deps.append(dep)
                print(f"  ❌ {dep}")
        
        # Check Go installation
        try:
            result = subprocess.run(['go', 'version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✅ Go: {result.stdout.strip()}")
            else:
                print("  ❌ Go: Not found")
                missing_deps.append('go')
        except FileNotFoundError:
            print("  ❌ Go: Not found")
            missing_deps.append('go')
        
        # Check Claude Code Browser source
        if self.claude_browser_path.exists():
            print(f"  ✅ Claude Code Browser source: {self.claude_browser_path}")
        else:
            print(f"  ❌ Claude Code Browser source not found: {self.claude_browser_path}")
            missing_deps.append('claude-code-browser-source')
        
        # Check Claude projects directory
        claude_projects = Path.home() / ".claude" / "projects"
        if claude_projects.exists():
            print(f"  ✅ Claude projects directory: {claude_projects}")
        else:
            print(f"  ⚠️ Claude projects directory not found: {claude_projects}")
            print("     This is normal if you haven't used Claude Code yet")
        
        if missing_deps:
            print(f"\n❌ Missing dependencies: {', '.join(missing_deps)}")
            print("\nTo install Python dependencies:")
            print(f"  pip install -r {self.base_path}/requirements.txt")
            print("\nTo install Go:")
            print("  Visit: https://golang.org/dl/")
            return False
        
        print("\n✅ All dependencies satisfied!")
        return True
    
    def install_dependencies(self):
        """Install Python dependencies."""
        print("📦 Installing Python dependencies...")
        
        requirements_file = self.base_path / "requirements.txt"
        if requirements_file.exists():
            try:
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
                ], check=True)
                print("✅ Dependencies installed successfully!")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install dependencies: {e}")
                return False
        else:
            print(f"❌ Requirements file not found: {requirements_file}")
            return False
        
        return True
    
    def show_attribution(self):
        """Display attribution information."""
        print("⚖️ License & Attribution Information")
        print("=" * 60)
        print(attribution.get_attribution_notice())
        print("=" * 60)
    
    def create_startup_scripts(self):
        """Create convenient startup scripts."""
        
        # Windows batch script
        bat_script = self.base_path / "start.bat"
        with open(bat_script, 'w') as f:
            f.write(f"""@echo off
REM Claude Code Browser Integration Launcher (Windows)
REM Original work by @zainhoda (AGPL-3.0)

cd /d "{self.base_path}"
python start_integration.py %*
pause
""")
        
        # Unix shell script
        sh_script = self.base_path / "start.sh"
        with open(sh_script, 'w') as f:
            f.write(f"""#!/bin/bash
# Claude Code Browser Integration Launcher (Unix)
# Original work by @zainhoda (AGPL-3.0)

cd "{self.base_path}"
python3 start_integration.py "$@"
""")
        
        # Make shell script executable
        os.chmod(sh_script, 0o755)
        
        print(f"✅ Startup scripts created:")
        print(f"   Windows: {bat_script}")
        print(f"   Unix:    {sh_script}")

async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Claude Code Browser Integration for Dev Stack v3.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_integration.py                    # Start with defaults
  python start_integration.py --browser-port 9000  # Custom browser port
  python start_integration.py --no-streaming     # Disable streaming
  python start_integration.py --check-deps       # Check dependencies
  python start_integration.py --create-config    # Create config file
  
Attribution:
  Original Claude Code Browser by @zainhoda (AGPL-3.0)
  Integration adapter for Dev Stack v3.0
  Source: https://github.com/zainhoda/claude-code-browser
        """
    )
    
    parser.add_argument('--browser-port', type=int, default=8080,
                       help='Browser server port (default: 8080)')
    parser.add_argument('--api-port', type=int, default=8081,
                       help='Dev Stack API port (default: 8081)')
    parser.add_argument('--no-streaming', action='store_true',
                       help='Disable streaming services')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--create-config', action='store_true',
                       help='Create default configuration file')
    parser.add_argument('--check-deps', action='store_true',
                       help='Check dependencies and exit')
    parser.add_argument('--install-deps', action='store_true',
                       help='Install Python dependencies')
    parser.add_argument('--create-scripts', action='store_true',
                       help='Create startup scripts')
    parser.add_argument('--verbose', action='store_true',
                       help='Verbose logging')
    
    args = parser.parse_args()
    
    launcher = IntegrationLauncher()
    
    # Show attribution
    launcher.show_attribution()
    
    # Handle special commands
    if args.check_deps:
        success = launcher.check_dependencies()
        sys.exit(0 if success else 1)
    
    if args.install_deps:
        success = launcher.install_dependencies()
        sys.exit(0 if success else 1)
    
    if args.create_scripts:
        launcher.create_startup_scripts()
        sys.exit(0)
    
    if args.create_config:
        ServerConfiguration.save_default_config()
        sys.exit(0)
    
    # Check dependencies before starting
    if not launcher.check_dependencies():
        print("\n❌ Dependency check failed. Run with --install-deps to install Python packages.")
        sys.exit(1)
    
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
    
    # Create and start the extended server
    server = ExtendedServer(browser_config, streaming_config)
    
    print("\n🚀 Starting Claude Code Browser Integration...")
    print(f"   Original work by @zainhoda (AGPL-3.0)")
    print(f"   Extended for Dev Stack v3.0")
    
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\n👋 Shutdown requested by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
    finally:
        await server.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)