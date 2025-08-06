#!/usr/bin/env python3
"""
Post-command hook - Runs after tool execution.
Triggers planning phase if specific files are modified.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

PLANNING_TRIGGERS = [
    "requirements.txt", "package.json", "REQUIREMENTS.md",
    "FEATURE_REQUEST.md", "ARCHITECTURE.md", "USER_STORIES.md"
]

def main():
    """Main hook function called by Claude Code."""
    try:
        # Read input from Claude Code via stdin
        input_data = json.load(sys.stdin)
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        tool_response = input_data.get("tool_response", {})
        
        # Check if we should trigger planning
        if tool_name in ["Write", "Edit", "MultiEdit"]:
            file_path = tool_input.get("file_path", "")
            file_name = Path(file_path).name.upper()
            
            if any(trigger.upper() in file_name for trigger in PLANNING_TRIGGERS):
                # Create planning notification
                planning_data = {
                    "trigger_type": "file_change",
                    "file": file_path,
                    "timestamp": datetime.now().isoformat(),
                    "suggested_agents": [
                        "@agent-requirements-analyst",
                        "@agent-system-architect",
                        "@agent-technical-specifications"
                    ]
                }
                
                # Save trigger state
                state_dir = Path.home() / ".claude" / "state"
                trigger_file = state_dir / "PLANNING_TRIGGER.json"
                trigger_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(trigger_file, 'w') as f:
                    json.dump(planning_data, f, indent=2)
                
                print(f"[PostToolUse] Planning phase triggered by {file_path}")
                print(f"  Suggested agents: {', '.join(planning_data['suggested_agents'])}")
                
                # Output hook result
                output = {
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": f"Planning phase triggered by {file_path}. Consider running /technical-feasibility"
                    }
                }
                print(json.dumps(output))
        
        return 0
    except Exception as e:
        print(f"Error in post command hook: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())