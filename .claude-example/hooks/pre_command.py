#!/usr/bin/env python3
"""
Pre-command hook - Runs before executing any slash command.
Use this to validate inputs, set up command-specific environment,
or log command usage.
"""

import os
import sys
import json
from datetime import datetime


def main():
    """Main hook function called by Claude."""
    command_name = os.environ.get('CLAUDE_COMMAND_NAME', 'unknown')
    command_args = os.environ.get('CLAUDE_COMMAND_ARGS', '')
    
    print(f"⚡ Running pre-command hook for /{command_name}")
    
    # Example: Log command usage
    log_dir = os.path.expanduser('~/.claude/logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'command': command_name,
        'args': command_args,
        'cwd': os.getcwd()
    }
    
    log_file = os.path.join(log_dir, 'command-usage.jsonl')
    try:
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        print(f"  ✓ Command logged to {log_file}")
    except Exception as e:
        print(f"  ⚠ Warning: Could not log command: {e}")
    
    # Example: Validate command prerequisites
    if command_name == 'new-project' and not os.environ.get('CLAUDE_API_KEY'):
        print("  ⚠ Warning: CLAUDE_API_KEY not set")
        print("    Some features may require API access")
    
    print(f"✅ Pre-command hook completed for /{command_name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())