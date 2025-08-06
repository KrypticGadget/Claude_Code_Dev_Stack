#!/usr/bin/env python3
"""
Pre-command hook - Runs before tool execution.
Use this to validate inputs, set up command-specific environment,
or log command usage.
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
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        
        print(f"[PreToolUse] Running pre-command hook for {tool_name}")
        
        # Log tool usage
        log_dir = Path.home() / '.claude' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'tool': tool_name,
            'input': tool_input,
            'cwd': os.getcwd()
        }
        
        log_file = log_dir / 'tool-usage.jsonl'
        try:
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
            print(f"  ✓ Tool usage logged")
        except Exception as e:
            print(f"  ⚠ Warning: Could not log tool usage: {e}")
        
        # Validate certain tools
        if tool_name in ["Write", "Edit", "MultiEdit"]:
            file_path = tool_input.get("file_path", "")
            if file_path:
                # Check if trying to edit system files
                if file_path.startswith("/etc/") or file_path.startswith("/sys/"):
                    output = {
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "permissionDecision": "deny",
                            "permissionDecisionReason": f"Cannot edit system file: {file_path}"
                        }
                    }
                    print(json.dumps(output))
                    return 0
        
        # Allow by default
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "permissionDecisionReason": "Tool usage permitted"
            }
        }
        print(json.dumps(output))
        return 0
    except Exception as e:
        print(f"Error in pre-command hook: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())