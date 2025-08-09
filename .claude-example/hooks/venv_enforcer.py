#!/usr/bin/env python3
"""
Virtual Environment Enforcer Hook for Claude Code
Ensures pip commands are run within a virtual environment
"""

import json
import sys
import os
import re
from pathlib import Path

class VenvEnforcer:
    def __init__(self):
        # Check if we're in a virtual environment
        self.in_venv = self.check_venv()
        self.venv_path = os.environ.get('VIRTUAL_ENV', '')
        
    def check_venv(self):
        """Check if running in a virtual environment"""
        # Multiple ways to detect virtual environment
        return (
            hasattr(sys, 'real_prefix') or  # virtualenv
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or  # venv
            os.environ.get('VIRTUAL_ENV') is not None or  # Both
            os.environ.get('CONDA_DEFAULT_ENV') is not None  # Conda
        )
    
    def find_venv_in_project(self):
        """Look for common virtual environment directories"""
        common_venv_names = ['venv', '.venv', 'env', '.env', 'virtualenv']
        cwd = Path.cwd()
        
        for name in common_venv_names:
            venv_path = cwd / name
            if venv_path.exists() and (venv_path / 'Scripts').exists() or (venv_path / 'bin').exists():
                return venv_path
        return None
    
    def check_command(self, command):
        """Check if command is a pip command that should be blocked"""
        if not command:
            return None
            
        command_lower = command.lower()
        
        # Check for pip commands
        pip_patterns = [
            r'\bpip\s+install',
            r'\bpip3\s+install',
            r'\bpython\s+-m\s+pip\s+install',
            r'\bpython3\s+-m\s+pip\s+install',
            r'\bpip\s+uninstall',
            r'\bpip3\s+uninstall',
        ]
        
        # Check if it's a pip command
        is_pip_command = any(re.search(pattern, command_lower) for pattern in pip_patterns)
        
        if not is_pip_command:
            return None
        
        # Allow certain safe pip commands even without venv
        safe_patterns = [
            r'pip\s+--version',
            r'pip\s+list',
            r'pip\s+show',
            r'pip\s+search',
            r'pip\s+help',
            r'pip\s+freeze',
        ]
        
        is_safe = any(re.search(pattern, command_lower) for pattern in safe_patterns)
        if is_safe:
            return None
        
        # Check for explicit global installation flags
        if '--user' in command_lower or '--break-system-packages' in command_lower:
            # User explicitly wants global install
            return None
        
        # If we're in a venv, allow it
        if self.in_venv:
            return None
        
        # Not in venv and trying to pip install - block it
        return self.generate_block_response()
    
    def generate_block_response(self):
        """Generate helpful response when blocking pip command"""
        existing_venv = self.find_venv_in_project()
        
        response = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "action": "block",
                "message": "⚠️ Virtual Environment Required",
                "details": [
                    "Pip installation detected outside of a virtual environment.",
                    "This can cause system-wide Python package conflicts.",
                    "",
                    "To proceed, please activate a virtual environment first:"
                ]
            }
        }
        
        if existing_venv:
            # Found an existing venv
            if os.name == 'nt':  # Windows
                activate_cmd = f"{existing_venv}\\Scripts\\activate"
            else:  # Unix/Mac
                activate_cmd = f"source {existing_venv}/bin/activate"
            
            response["hookSpecificOutput"]["details"].extend([
                f"Found existing venv at: {existing_venv}",
                f"Activate it with: {activate_cmd}",
                "",
                "Or if you really need to install globally, add --user flag"
            ])
        else:
            # No venv found, suggest creating one
            response["hookSpecificOutput"]["details"].extend([
                "No virtual environment found. Create one with:",
                "  python -m venv venv",
                "",
                "Then activate it:",
                "  Windows: venv\\Scripts\\activate",
                "  Mac/Linux: source venv/bin/activate",
                "",
                "Or if you really need to install globally, add --user flag"
            ])
        
        return response

def main():
    """Main hook execution"""
    try:
        input_data = json.load(sys.stdin)
    except:
        # If no input, exit gracefully
        sys.exit(0)
    
    # Only check Bash commands
    if input_data.get("hook_event_name") != "PreToolUse":
        sys.exit(0)
    
    if input_data.get("tool_name") != "Bash":
        sys.exit(0)
    
    command = input_data.get("tool_input", {}).get("command", "")
    
    enforcer = VenvEnforcer()
    block_response = enforcer.check_command(command)
    
    if block_response:
        # Block the command and provide guidance
        print(json.dumps(block_response))
        sys.exit(1)  # Exit with error to block the command
    
    # Allow the command to proceed
    sys.exit(0)

if __name__ == "__main__":
    main()