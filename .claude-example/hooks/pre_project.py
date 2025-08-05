#!/usr/bin/env python3
"""
Pre-project hook - Runs before starting any new project.
Use this to set up project-specific configurations, validate requirements,
or prepare the development environment.
"""

import os
import sys
import json
from datetime import datetime


def main():
    """Main hook function called by Claude."""
    print("🚀 Running pre-project hook...")
    
    # Get project context from environment
    project_name = os.environ.get('CLAUDE_PROJECT_NAME', 'Unknown Project')
    project_path = os.environ.get('CLAUDE_PROJECT_PATH', os.getcwd())
    
    print(f"  Project: {project_name}")
    print(f"  Path: {project_path}")
    
    # Example: Create project metadata file
    metadata = {
        'project_name': project_name,
        'created_at': datetime.now().isoformat(),
        'claude_version': os.environ.get('CLAUDE_VERSION', 'Unknown'),
        'hook_version': '1.0.0'
    }
    
    metadata_path = os.path.join(project_path, '.claude-project.json')
    try:
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"  ✓ Created project metadata at {metadata_path}")
    except Exception as e:
        print(f"  ⚠ Warning: Could not create metadata file: {e}")
    
    # Example: Validate prerequisites
    required_tools = ['git', 'node', 'python']
    missing_tools = []
    
    for tool in required_tools:
        if os.system(f"which {tool} > /dev/null 2>&1") != 0:
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"  ⚠ Warning: Missing tools: {', '.join(missing_tools)}")
        print("    Some features may not work correctly.")
    else:
        print("  ✓ All required tools are installed")
    
    print("✨ Pre-project hook completed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())