#!/usr/bin/env python3
"""
One-Click Monitoring Installation for Claude Code V3.6.9
Complete monitoring infrastructure setup with a single command
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    """One-click monitoring installation"""
    
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║              Claude Code V3.6.9 - Complete Monitoring Setup                  ║
║                                                                               ║
║  This script will install and configure:                                     ║
║  • Prometheus metrics collection                                             ║
║  • Grafana dashboards and visualization                                      ║
║  • Loki log aggregation                                                      ║
║  • Alertmanager for intelligent alerting                                     ║
║  • Custom metrics collection for Claude Code                                 ║
║                                                                               ║
║  Prerequisites: Docker, Docker Compose, Python 3.8+                         ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    base_dir = Path(__file__).parent
    monitoring_dir = base_dir / 'monitoring'
    
    # Check if monitoring directory exists
    if not monitoring_dir.exists():
        print("❌ Monitoring directory not found. Please ensure you're in the correct directory.")
        sys.exit(1)
    
    # Check prerequisites
    print("🔍 Checking prerequisites...")
    
    required_tools = ['docker', 'docker-compose', 'python']
    missing = []
    
    for tool in required_tools:
        if not shutil.which(tool):
            missing.append(tool)
        else:
            print(f"  ✅ {tool} found")
    
    if missing:
        print(f"❌ Missing required tools: {', '.join(missing)}")
        print("Please install the missing tools and try again.")
        sys.exit(1)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher required")
        sys.exit(1)
    
    print("✅ All prerequisites satisfied")
    
    # Ask for confirmation
    print(f"\n📁 Installation directory: {monitoring_dir}")
    response = input("\n🚀 Ready to install monitoring infrastructure? (y/N): ")
    
    if response.lower() not in ['y', 'yes']:
        print("Installation cancelled.")
        sys.exit(0)
    
    # Run the quick start
    print("\n🔄 Starting installation...")
    
    try:
        quick_start_script = monitoring_dir / 'quick_start.py'
        if quick_start_script.exists():
            # Run quick start
            os.chdir(monitoring_dir)
            result = subprocess.run([sys.executable, 'quick_start.py', 'full'], 
                                  capture_output=False)
            sys.exit(result.returncode)
        else:
            # Fallback to setup script
            setup_script = monitoring_dir / 'setup_monitoring.py'
            if setup_script.exists():
                os.chdir(monitoring_dir)
                result = subprocess.run([sys.executable, 'setup_monitoring.py', 'full'], 
                                      capture_output=False)
                sys.exit(result.returncode)
            else:
                print("❌ Installation scripts not found")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n⚠️  Installation interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Installation error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()