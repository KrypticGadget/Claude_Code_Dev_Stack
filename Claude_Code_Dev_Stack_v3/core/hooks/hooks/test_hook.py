#!/usr/bin/env python3
"""Test hook to verify hook system is working"""
import json
import sys
import os
from datetime import datetime

def main():
    """Test hook that logs when triggered"""
    try:
        # Create log directory if it doesn't exist
        log_dir = os.path.expanduser("~/.claude/logs")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "test_hook.log")
        
        # Log that hook was triggered
        with open(log_file, "a") as f:
            f.write(f"{datetime.now().isoformat()}: Hook triggered\n")
        
        # Read input from stdin
        input_data = json.load(sys.stdin)
        event = input_data.get("hook_event_name", "unknown")
        tool_name = input_data.get("tool_name", "unknown")
        
        # Log the event details
        with open(log_file, "a") as f:
            f.write(f"  Event: {event}, Tool: {tool_name}\n")
            f.write(f"  Full input: {json.dumps(input_data, indent=2)}\n")
            f.write("-" * 50 + "\n")
        
        # Output to stderr so it shows in debug mode
        print(f"[TEST HOOK] Event: {event}, Tool: {tool_name}", file=sys.stderr)
        
        # Always exit successfully
        sys.exit(0)
        
    except Exception as e:
        # Log any errors
        print(f"[TEST HOOK ERROR] {e}", file=sys.stderr)
        
        # Still exit successfully to not block operations
        sys.exit(0)

if __name__ == "__main__":
    main()