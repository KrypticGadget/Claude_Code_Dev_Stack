#!/usr/bin/env python3
"""
Enhanced Bash Hook - V3.0 Intelligent Command Enhancement
Provides context-aware command suggestions and validation
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

class EnhancedBashHook:
    """Enhanced bash command processing with V3 intelligence"""
    
    def __init__(self):
        self.home_dir = Path.home() / ".claude"
        self.dangerous_commands = [
            "rm -rf /", "format", "del /f /s /q C:\\",
            "DROP DATABASE", "DELETE FROM", "TRUNCATE",
            "shutdown", "reboot", "halt", "poweroff"
        ]
        
        self.smart_suggestions = {
            "git": {
                "git add .": "git add . && git commit -m 'Auto-commit'",
                "git push": "git push origin $(git branch --show-current)",
                "git pull": "git pull origin $(git branch --show-current)"
            },
            "npm": {
                "npm install": "npm ci  # Use npm ci for reproducible builds",
                "npm start": "npm run dev  # Consider using dev script",
                "npm test": "npm run test:watch  # Consider watch mode"
            },
            "docker": {
                "docker build .": "docker build -t project:latest .",
                "docker run": "docker run --rm -it",
                "docker ps": "docker ps -a  # Show all containers"
            }
        }
    
    def analyze_command(self, command: str) -> Dict[str, any]:
        """Analyze command for safety and optimization"""
        analysis = {
            "command": command,
            "safe": True,
            "warnings": [],
            "suggestions": [],
            "enhancements": []
        }
        
        # Safety check
        for dangerous in self.dangerous_commands:
            if dangerous in command.lower():
                analysis["safe"] = False
                analysis["warnings"].append(f"Dangerous command detected: {dangerous}")
        
        # Command-specific suggestions
        for tool, suggestions in self.smart_suggestions.items():
            if command.startswith(tool):
                for pattern, suggestion in suggestions.items():
                    if pattern in command:
                        analysis["suggestions"].append(suggestion)
        
        # Context-aware enhancements
        if "git" in command:
            analysis["enhancements"].append("Consider using git hooks for automation")
        
        if "npm" in command or "yarn" in command:
            analysis["enhancements"].append("Ensure using virtual environment")
        
        if "python" in command:
            analysis["enhancements"].append("Consider using ./venv/Scripts/python.exe")
        
        return analysis
    
    def process_command(self, hook_data: Dict) -> Dict:
        """Process bash command with V3 intelligence"""
        command = hook_data.get("tool_input", {}).get("command", "")
        
        if not command:
            return {"status": "no_command"}
        
        analysis = self.analyze_command(command)
        
        result = {
            "original_command": command,
            "analysis": analysis,
            "timestamp": self.get_timestamp()
        }
        
        # Log command for learning
        self.log_command(command, analysis)
        
        return result
    
    def log_command(self, command: str, analysis: Dict):
        """Log command for pattern learning"""
        log_file = self.home_dir / "command_history.jsonl"
        log_entry = {
            "timestamp": self.get_timestamp(),
            "command": command,
            "safe": analysis["safe"],
            "warnings": len(analysis["warnings"]),
            "suggestions": len(analysis["suggestions"])
        }
        
        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except:
            pass
    
    def get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

def main():
    """Main hook execution"""
    try:
        hook_data = json.load(sys.stdin)
    except:
        hook_data = {}
    
    hook = EnhancedBashHook()
    result = hook.process_command(hook_data)
    
    # Output enhancement suggestions if any
    if result.get("analysis", {}).get("suggestions"):
        print("Command suggestions:", file=sys.stderr)
        for suggestion in result["analysis"]["suggestions"]:
            print(f"  • {suggestion}", file=sys.stderr)
    
    sys.exit(0)

if __name__ == "__main__":
    main()