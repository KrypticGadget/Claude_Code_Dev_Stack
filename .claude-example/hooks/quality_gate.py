#!/usr/bin/env python3
"""Code quality enforcement hook"""
import json
import sys
import re
import os
from pathlib import Path
from datetime import datetime

CLAUDE_DIR = Path(".claude")
CONFIG_FILE = CLAUDE_DIR / "config" / "coding_standards.json"

def load_standards():
    """Load coding standards configuration"""
    if not CONFIG_FILE.exists():
        return {
            "naming": {
                "functions": "snake_case",
                "classes": "PascalCase",
                "constants": "UPPER_SNAKE_CASE"
            },
            "forbidden_patterns": [
                r"console\.log\(",  # No console.log in production
                r"TODO(?!:)",       # TODOs must have descriptions
                r"password\s*=\s*[\"']",  # No hardcoded passwords
            ],
            "required_patterns": {
                "functions": r"def .+\(.*\):\s*\n\s*\"\"\"",  # Docstrings required
            }
        }
    
    with open(CONFIG_FILE) as f:
        return json.load(f)

def check_file_quality(file_path, content):
    """Check file against quality standards"""
    issues = []
    standards = load_standards()
    
    # Check naming conventions
    if file_path.endswith('.py'):
        # Function names
        functions = re.findall(r'def (\w+)\(', content)
        for func in functions:
            if standards["naming"]["functions"] == "snake_case":
                if not re.match(r'^[a-z_][a-z0-9_]*$', func):
                    issues.append(f"Function '{func}' doesn't follow snake_case")
        
        # Class names  
        classes = re.findall(r'class (\w+)[:\(]', content)
        for cls in classes:
            if standards["naming"]["classes"] == "PascalCase":
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', cls):
                    issues.append(f"Class '{cls}' doesn't follow PascalCase")
    
    # Check forbidden patterns
    for i, pattern in enumerate(standards.get("forbidden_patterns", [])):
        matches = re.findall(pattern, content)
        if matches:
            issues.append(f"Forbidden pattern found: {pattern}")
    
    # Check required patterns
    for pattern_type, pattern in standards.get("required_patterns", {}).items():
        if pattern_type == "functions" and file_path.endswith('.py'):
            functions = re.findall(r'def \w+\(.*\):', content)
            for func in functions:
                func_with_next = content[content.find(func):content.find(func)+200]
                if not re.search(pattern, func_with_next):
                    issues.append(f"Function missing required docstring")
    
    return issues

def main():
    """Main quality gate execution"""
    try:
        # Read input from Claude Code via stdin
        input_data = json.load(sys.stdin)
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        
        # Check for dangerous operations on sensitive files
        if tool_name in ["Write", "Edit", "MultiEdit"]:
            file_path = tool_input.get("file_path", "")
            
            # Block sensitive files
            sensitive_patterns = [
                ".env", ".git/", "credentials", "secrets",
                "password", "token", "key", ".ssh/"
            ]
            
            if any(pattern in file_path.lower() for pattern in sensitive_patterns):
                # Block with JSON output
                output = {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": f"Blocked: Attempting to modify sensitive file {file_path}"
                    }
                }
                print(json.dumps(output))
                return 0
            
            # Auto-approve safe files
            safe_extensions = [".md", ".txt", ".json", ".py", ".js", ".ts"]
            if any(file_path.endswith(ext) for ext in safe_extensions):
                # Check quality if it's a code file
                if file_path.endswith(('.py', '.js', '.ts')) and Path(file_path).exists():
                    with open(file_path) as f:
                        content = f.read()
                    
                    issues = check_file_quality(file_path, content)
                    
                    if issues:
                        print(f"[PreToolUse] Quality issues found in {file_path}")
                        for issue in issues:
                            print(f"  - {issue}")
                
                output = {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "allow",
                        "permissionDecisionReason": "Safe file type auto-approved"
                    }
                }
                print(json.dumps(output))
        
        return 0
    except Exception as e:
        print(f"Error in quality gate: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())