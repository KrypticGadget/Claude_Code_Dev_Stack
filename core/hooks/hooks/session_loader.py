#!/usr/bin/env python3
"""
Ultra-lightweight session loader - prevents bloat
Just acknowledges session start without loading massive context
"""
import sys
from datetime import datetime
from pathlib import Path

def main():
    try:
        # Check if we have a previous session timestamp
        state_file = Path.home() / ".claude" / "state" / "session_timestamp.json"
        
        if state_file.exists():
            # Just acknowledge - don't load any heavy data
            print("[OK] Session ready (minimal mode)", file=sys.stderr)
        else:
            print("[OK] New session started", file=sys.stderr)
        
        # Optional: Print lightweight info
        print("[INFO] Model tracking disabled for performance", file=sys.stderr)
        print("[INFO] Context persistence minimal", file=sys.stderr)
        
    except Exception as e:
        # Silent fail - don't break hook chain
        print(f"[WARN] Session load skipped: {e}", file=sys.stderr)
    
    sys.exit(0)

if __name__ == "__main__":
    main()