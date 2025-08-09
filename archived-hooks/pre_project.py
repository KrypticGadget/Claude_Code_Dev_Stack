#!/usr/bin/env python3
"""
Pre-project hook - Runs at session start.
Use this to set up project-specific configurations, validate requirements,
or prepare the development environment.
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
        source = input_data.get("source", "startup")
        
        print(f"[SessionStart] Running pre-project hook (source: {source})...")
        
        project_path = Path.cwd()
        
        print(f"  Session: {session_id}")
        print(f"  Path: {project_path}")
        
        # Create project metadata file
        metadata = {
            'session_id': session_id,
            'started_at': datetime.now().isoformat(),
            'source': source,
            'hook_version': '2.1.0',
            'project_path': str(project_path)
        }
        
        metadata_path = project_path / '.claude-project.json'
        try:
            # Load existing metadata if it exists
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    existing = json.load(f)
                    metadata['created_at'] = existing.get('created_at', metadata['started_at'])
                    metadata['sessions'] = existing.get('sessions', [])
                    metadata['sessions'].append(session_id)
            else:
                metadata['created_at'] = metadata['started_at']
                metadata['sessions'] = [session_id]
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            print(f"  [OK] Updated project metadata")
        except Exception as e:
            print(f"  [WARNING] Could not update metadata file: {e}")
        
        # Check for required files
        required_files = ['.claude/agents', '.claude/commands', '.claude/hooks']
        missing = []
        
        for req_file in required_files:
            full_path = Path.home() / req_file
            if not full_path.exists():
                missing.append(req_file)
        
        if missing:
            print(f"  [WARNING] Missing components: {', '.join(missing)}")
            print("    Run installers to set up missing components")
        else:
            print("  [OK] All Claude Code components installed")
        
        # Output for Claude Code
        output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": f"Project initialized in {project_path}"
            }
        }
        print(json.dumps(output))
        
        print("[COMPLETE] Pre-project hook completed!")
        return 0
    except Exception as e:
        print(f"Error in pre-project hook: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())