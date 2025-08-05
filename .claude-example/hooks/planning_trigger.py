#!/usr/bin/env python3
"""Detect when planning phase should be triggered"""
import json
import sys
from pathlib import Path
from datetime import datetime

TRIGGER_FILES = [
    "requirements.txt",
    "package.json", 
    "REQUIREMENTS.md",
    "FEATURE_REQUEST.md",
    "ARCHITECTURE.md",
    "USER_STORIES.md"
]

def should_trigger_planning(file_path):
    """Check if file change should trigger planning"""
    file_name = Path(file_path).name
    return any(trigger in file_name.upper() for trigger in 
               [t.upper() for t in TRIGGER_FILES])

def create_planning_trigger(file_path):
    """Create planning trigger notification"""
    trigger_data = {
        "trigger_type": "file_change",
        "file": file_path,
        "timestamp": datetime.now().isoformat(),
        "suggested_agents": [
            "@agent-requirements-analyst",
            "@agent-system-architect[opus]", 
            "@agent-technical-specifications[opus]"
        ],
        "action": "Review changes and update project plan"
    }
    
    trigger_file = Path(".claude/state/PLANNING_TRIGGER.json")
    trigger_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(trigger_file, 'w') as f:
        json.dump(trigger_data, f, indent=2)
    
    # Also create visible notification
    with open("PLANNING_NEEDED.md", 'w') as f:
        f.write(f"""# Planning Phase Triggered

**Trigger**: {file_path} was modified
**Time**: {trigger_data['timestamp']}

## Suggested Actions

1. Run `/technical-feasibility` to assess changes
2. Update `/project-plan` if needed
3. Review with agents: {', '.join(trigger_data['suggested_agents'])}

This file will be automatically removed once planning is complete.
""")
    
    print(f"🎯 Planning phase triggered by {file_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if should_trigger_planning(file_path):
            create_planning_trigger(file_path)