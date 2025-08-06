#!/usr/bin/env python3
"""
Post-project hook - Runs after completing a project.
Use this to clean up resources, generate reports, or archive project data.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path


def main():
    """Main hook function called by Claude Code."""
    try:
        # Read input from Claude Code via stdin
        input_data = json.load(sys.stdin)
        session_id = input_data.get("session_id", "")
        
        print("[PostProject] Running post-project hook...")
        
        project_path = Path.cwd()
        
        # Update project metadata with completion time
        metadata_path = project_path / '.claude-project.json'
        try:
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                metadata['completed_at'] = datetime.now().isoformat()
                metadata['status'] = 'completed'
                metadata['session_id'] = session_id
                
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                print(f"  ✓ Updated project metadata")
        except Exception as e:
            print(f"  ⚠ Warning: Could not update metadata: {e}")
        
        # Generate project summary
        print(f"\n📊 Project Summary:")
        print(f"  Path: {project_path}")
        print(f"  Session: {session_id}")
        
        # Count files created/modified
        file_count = sum(len(files) for _, _, files in os.walk(project_path))
        print(f"  Total files: {file_count}")
        
        # Output for Claude Code
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PostProject",
                "additionalContext": f"Project completed with {file_count} files"
            }
        }
        print(json.dumps(output))
        
        print("\n✨ Post-project hook completed!")
        return 0
    except Exception as e:
        print(f"Error in post-project hook: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())