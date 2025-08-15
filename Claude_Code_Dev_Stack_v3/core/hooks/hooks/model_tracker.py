#!/usr/bin/env python3
"""
Ultra-lightweight model tracker - prevents bloat
Only tracks today's count with auto-cleanup
"""
import json
import sys
from datetime import datetime
from pathlib import Path

def main():
    try:
        # Use separate state file, not .claude.json
        state_dir = Path.home() / ".claude" / "state"
        state_dir.mkdir(parents=True, exist_ok=True)
        state_file = state_dir / "daily_count.json"
        
        # Get today's date
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Load existing data
        try:
            with open(state_file) as f:
                data = json.load(f)
        except:
            data = {}
        
        # CRITICAL: Only keep today's data to prevent bloat
        # This automatically cleans up old data
        data = {today: data.get(today, 0) + 1}
        
        # Save minimal data
        with open(state_file, 'w') as f:
            json.dump(data, f)
        
        # Optional lightweight output
        count = data[today]
        if count % 10 == 0:  # Only report every 10 calls
            print(f"[INFO] Daily usage: {count}", file=sys.stderr)
        
    except Exception as e:
        # Silent fail - don't break hook chain
        pass
    
    sys.exit(0)

if __name__ == "__main__":
    main()