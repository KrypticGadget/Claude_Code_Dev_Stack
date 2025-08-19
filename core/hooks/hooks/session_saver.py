#!/usr/bin/env python3
"""
Ultra-lightweight session saver - prevents .claude.json bloat
Only saves minimal timestamp to prevent performance issues
"""
import json
import sys
from datetime import datetime
from pathlib import Path

def main():
    try:
        # Create state directory if needed
        state_dir = Path.home() / ".claude" / "state"
        state_dir.mkdir(parents=True, exist_ok=True)
        
        # Only save a timestamp - nothing else to prevent bloat
        state = {
            "last_saved": datetime.now().isoformat(),
            "version": "minimal_v1",
            "size_bytes": 100  # This file will always be tiny
        }
        
        # Write to separate state file, NOT .claude.json
        state_file = state_dir / "session_timestamp.json"
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        # Success message
        print("[OK] Session timestamp saved (minimal)", file=sys.stderr)
        
    except Exception as e:
        # Silent fail - don't break hook chain
        print(f"[WARN] Session save skipped: {e}", file=sys.stderr)
    
    sys.exit(0)

if __name__ == "__main__":
    main()