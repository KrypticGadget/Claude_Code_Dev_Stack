#!/usr/bin/env python3
"""
Post-project hook - Runs after completing a project.
Use this to clean up resources, generate reports, or archive project data.
"""

import os
import sys
import json
from datetime import datetime


def main():
    """Main hook function called by Claude."""
    print("🏁 Running post-project hook...")
    
    project_name = os.environ.get('CLAUDE_PROJECT_NAME', 'Unknown Project')
    project_path = os.environ.get('CLAUDE_PROJECT_PATH', os.getcwd())
    
    # Example: Update project metadata with completion time
    metadata_path = os.path.join(project_path, '.claude-project.json')
    try:
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            metadata['completed_at'] = datetime.now().isoformat()
            metadata['status'] = 'completed'
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"  ✓ Updated project metadata")
    except Exception as e:
        print(f"  ⚠ Warning: Could not update metadata: {e}")
    
    # Example: Generate project summary
    print(f"\n📊 Project Summary:")
    print(f"  Name: {project_name}")
    print(f"  Path: {project_path}")
    
    # Count files created/modified
    file_count = sum(len(files) for _, _, files in os.walk(project_path))
    print(f"  Total files: {file_count}")
    
    print("\n✨ Post-project hook completed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())