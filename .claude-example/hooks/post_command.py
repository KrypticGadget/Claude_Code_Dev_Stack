#!/usr/bin/env python3
"""
Post-command hook - Runs after executing any slash command.
Use this to clean up after commands, process results, or trigger
follow-up actions.
"""

import os
import sys
import json
from datetime import datetime


def main():
    """Main hook function called by Claude."""
    command_name = os.environ.get('CLAUDE_COMMAND_NAME', 'unknown')
    command_result = os.environ.get('CLAUDE_COMMAND_RESULT', 'unknown')
    
    print(f"🎯 Running post-command hook for /{command_name}")
    print(f"  Result: {command_result}")
    
    # Example: Send notification for certain commands
    if command_name in ['production-frontend', 'backend-service'] and command_result == 'success':
        print(f"  🔔 Notification: {command_name} completed successfully!")
        # Here you could send actual notifications (email, Slack, etc.)
    
    # Example: Trigger follow-up actions
    if command_name == 'new-project' and command_result == 'success':
        print("  📋 Suggested next steps:")
        print("    1. Run /requirements to gather detailed requirements")
        print("    2. Run /technical-feasibility to assess the project")
        print("    3. Run /project-plan to create a development timeline")
    
    print(f"✨ Post-command hook completed for /{command_name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())