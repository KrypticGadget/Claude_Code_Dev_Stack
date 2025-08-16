#!/usr/bin/env python3
"""
Setup script for Claude Code Quality System V3.0+
Configures the enhanced quality system with adjustable strictness levels
"""

import json
import sys
import subprocess
from pathlib import Path

def setup_quality_system():
    """Setup the complete quality system"""
    print("[SETUP] Setting up Claude Code Quality System V3.0+")
    print("=" * 60)
    
    # 1. Configure default settings
    print("[CONFIG] Configuring default quality settings...")
    quality_config_path = Path(__file__).parent / 'quality_config.py'
    
    # Set to 'suggestion' level by default (non-blocking)
    result = subprocess.run([
        sys.executable, str(quality_config_path), 'strictness', 'suggestion'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("[OK] Default strictness level set to 'suggestion' (non-blocking)")
    else:
        print("[WARN] Warning: Could not set default strictness level")
    
    # 2. Enable auto-formatting
    subprocess.run([
        sys.executable, str(quality_config_path), 'autoformat', 'on'
    ], capture_output=True)
    print("[OK] Auto-formatting enabled")
    
    # 3. Enable audio notifications
    subprocess.run([
        sys.executable, str(quality_config_path), 'audio', 'on'
    ], capture_output=True)
    print("[OK] Audio notifications enabled")
    
    # 4. Show current configuration
    print("\n[INFO] Current Configuration:")
    subprocess.run([
        sys.executable, str(quality_config_path), 'show'
    ])
    
    print("\n[SUCCESS] Quality System Setup Complete!")
    print("=" * 60)
    print("Key Features:")
    print("  [OK] Configurable strictness levels (suggestion/warning/strict)")
    print("  [OK] Non-blocking warnings by default")
    print("  [OK] Audio feedback for quality events")
    print("  [OK] Auto-formatting on save")
    print("  [OK] Git hooks with smart blocking")
    
    print("\n[COMMANDS] Quick Commands:")
    print("  # Change strictness level:")
    print("  python quality_config.py strictness warning")
    print("  ")
    print("  # View current settings:")
    print("  python quality_config.py show")
    print("  ")
    print("  # Test the system:")
    print("  python test_quality_system.py")
    
    print("\n[WORKFLOW] Recommended Workflow:")
    print("  1. Development: Use 'suggestion' level (shows issues, allows commits)")
    print("  2. Team review: Use 'warning' level (blocks only on errors)")
    print("  3. Production: Use 'strict' level (blocks on any issue)")
    
    return True

def check_dependencies():
    """Check if required dependencies are available"""
    print("[CHECK] Checking dependencies...")
    
    dependencies = {
        'flake8': 'Python linting',
        'black': 'Python formatting',
        'mypy': 'Python type checking (optional)',
        'eslint': 'JavaScript linting (optional)',
        'prettier': 'JavaScript formatting (optional)'
    }
    
    available = []
    missing = []
    
    for dep, description in dependencies.items():
        try:
            result = subprocess.run([dep, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                available.append(f"[OK] {dep} - {description}")
            else:
                missing.append(f"[MISSING] {dep} - {description}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            missing.append(f"[MISSING] {dep} - {description}")
    
    print("\nAvailable tools:")
    for tool in available:
        print(f"  {tool}")
    
    if missing:
        print("\nMissing tools (optional):")
        for tool in missing:
            print(f"  {tool}")
        
        print("\n[INFO] To install missing Python tools:")
        print("  pip install flake8 black mypy")
        print("\n[INFO] To install missing Node.js tools:")
        print("  npm install -g eslint prettier")
    
    return len(available) > 0

def main():
    """Main setup function"""
    print("[SETUP] Claude Code Quality System Setup")
    print("This will configure the enhanced quality system with adjustable strictness.")
    
    # Check dependencies
    if not check_dependencies():
        print("\n[WARN] Warning: No linting tools found. Basic functionality will be limited.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            sys.exit(1)
    
    # Setup the system
    if setup_quality_system():
        print("\n[SUCCESS] Setup completed successfully!")
        print("The quality system is now configured with non-blocking warnings.")
        print("Commits will show quality issues but won't be blocked unless configured otherwise.")
    else:
        print("\n[ERROR] Setup failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()