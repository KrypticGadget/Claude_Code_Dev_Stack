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
    # Get file being edited from environment or args
    file_path = sys.argv[1] if len(sys.argv) > 1 else os.getenv("EDITING_FILE", "")
    
    if not file_path or not Path(file_path).exists():
        print("⚠️  No file to check")
        return 0
    
    with open(file_path) as f:
        content = f.read()
    
    issues = check_file_quality(file_path, content)
    
    if issues:
        print(f"❌ Quality gate failed for {file_path}:")
        for issue in issues:
            print(f"  - {issue}")
        
        # Create quality report
        report = {
            "file": file_path,
            "timestamp": datetime.now().isoformat(),
            "issues": issues
        }
        
        report_file = CLAUDE_DIR / "state" / "quality_report.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return 1
    else:
        print(f"✅ Quality gate passed for {file_path}")
        return 0

if __name__ == "__main__":
    sys.exit(main())