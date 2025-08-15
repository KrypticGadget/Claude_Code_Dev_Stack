#!/usr/bin/env python3
"""
Quality Gate Hook - V3.0 Automated Quality Assurance
Enforces quality standards and best practices
"""

import json
import os
import sys
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional

class QualityGateHook:
    """Automated quality gate enforcement"""
    
    def __init__(self):
        self.home_dir = Path.home() / ".claude"
        self.quality_standards = {
            "code": {
                "max_function_lines": 50,
                "max_file_lines": 1000,
                "min_test_coverage": 80,
                "max_complexity": 10
            },
            "security": {
                "no_hardcoded_secrets": True,
                "no_sql_injection": True,
                "secure_headers": True
            },
            "performance": {
                "max_bundle_size_mb": 5,
                "max_response_time_ms": 200,
                "min_lighthouse_score": 90
            }
        }
        
        self.file_patterns = {
            "python": [".py"],
            "javascript": [".js", ".ts", ".jsx", ".tsx"],
            "web": [".html", ".css"],
            "config": [".json", ".yaml", ".yml", ".env"],
            "documentation": [".md", ".txt", ".rst"]
        }
    
    def check_file_quality(self, file_path: str) -> Dict:
        """Check quality of a specific file"""
        path = Path(file_path)
        
        if not path.exists():
            return {"status": "file_not_found", "file": file_path}
        
        checks = {
            "file": file_path,
            "size_check": self.check_file_size(path),
            "security_check": self.check_security(path),
            "style_check": self.check_style(path),
            "complexity_check": self.check_complexity(path),
            "overall_score": 0
        }
        
        # Calculate overall score
        passed_checks = sum(1 for check in checks.values() 
                           if isinstance(check, dict) and check.get("passed", False))
        total_checks = len([k for k in checks.keys() if k.endswith("_check")])
        checks["overall_score"] = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        return checks
    
    def check_file_size(self, path: Path) -> Dict:
        """Check if file size is reasonable"""
        try:
            line_count = len(path.read_text().splitlines())
            max_lines = self.quality_standards["code"]["max_file_lines"]
            
            return {
                "check": "file_size",
                "lines": line_count,
                "max_allowed": max_lines,
                "passed": line_count <= max_lines,
                "message": f"File has {line_count} lines (max: {max_lines})"
            }
        except:
            return {"check": "file_size", "passed": False, "message": "Could not read file"}
    
    def check_security(self, path: Path) -> Dict:
        """Check for security issues"""
        try:
            content = path.read_text()
            issues = []
            
            # Check for hardcoded secrets
            secret_patterns = [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']'
            ]
            
            for pattern in secret_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    issues.append(f"Potential hardcoded secret: {pattern}")
            
            # Check for SQL injection patterns
            sql_patterns = [
                r'f".*SELECT.*{.*}"',
                r'".*SELECT.*" \+ ',
                r'execute\(["\'].*\+.*["\']'
            ]
            
            for pattern in sql_patterns:
                if re.search(pattern, content):
                    issues.append(f"Potential SQL injection: {pattern}")
            
            return {
                "check": "security",
                "issues": issues,
                "passed": len(issues) == 0,
                "message": f"Found {len(issues)} security issues"
            }
        except:
            return {"check": "security", "passed": True, "message": "Could not analyze security"}
    
    def check_style(self, path: Path) -> Dict:
        """Check code style"""
        try:
            content = path.read_text()
            issues = []
            
            # Check for basic style issues
            lines = content.splitlines()
            
            for i, line in enumerate(lines, 1):
                # Line too long
                if len(line) > 120:
                    issues.append(f"Line {i}: Too long ({len(line)} chars)")
                
                # Trailing whitespace
                if line.endswith(' ') or line.endswith('\t'):
                    issues.append(f"Line {i}: Trailing whitespace")
            
            # Check for function length (Python)
            if path.suffix == '.py':
                function_lines = self.count_function_lines(content)
                max_function_lines = self.quality_standards["code"]["max_function_lines"]
                
                for func_name, line_count in function_lines.items():
                    if line_count > max_function_lines:
                        issues.append(f"Function '{func_name}': Too long ({line_count} lines)")
            
            return {
                "check": "style",
                "issues": issues[:10],  # Limit to first 10 issues
                "passed": len(issues) == 0,
                "message": f"Found {len(issues)} style issues"
            }
        except:
            return {"check": "style", "passed": True, "message": "Could not analyze style"}
    
    def check_complexity(self, path: Path) -> Dict:
        """Check code complexity"""
        try:
            content = path.read_text()
            
            # Simple complexity check - count nested blocks
            max_nesting = 0
            current_nesting = 0
            
            for line in content.splitlines():
                stripped = line.strip()
                
                # Count opening blocks
                if any(stripped.startswith(kw) for kw in ['if', 'for', 'while', 'try', 'with']):
                    current_nesting += 1
                    max_nesting = max(max_nesting, current_nesting)
                
                # Count closing blocks (simplified)
                if stripped.startswith(('except', 'finally', 'else')) or not stripped:
                    current_nesting = max(0, current_nesting - 1)
            
            max_complexity = self.quality_standards["code"]["max_complexity"]
            
            return {
                "check": "complexity",
                "max_nesting": max_nesting,
                "max_allowed": max_complexity,
                "passed": max_nesting <= max_complexity,
                "message": f"Max nesting depth: {max_nesting} (max: {max_complexity})"
            }
        except:
            return {"check": "complexity", "passed": True, "message": "Could not analyze complexity"}
    
    def count_function_lines(self, content: str) -> Dict[str, int]:
        """Count lines in Python functions"""
        functions = {}
        current_function = None
        function_start = 0
        
        for i, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            
            # Function definition
            if stripped.startswith('def '):
                if current_function:
                    functions[current_function] = i - function_start - 1
                
                current_function = stripped.split('(')[0].replace('def ', '')
                function_start = i
            
            # End of function (next def or class, or end of file)
            elif stripped.startswith(('def ', 'class ')) and current_function:
                functions[current_function] = i - function_start - 1
                current_function = None
        
        # Handle last function
        if current_function:
            functions[current_function] = len(content.splitlines()) - function_start
        
        return functions
    
    def process_file_operation(self, hook_data: Dict) -> Dict:
        """Process file operation through quality gates"""
        tool_name = hook_data.get("tool_name", "")
        file_path = hook_data.get("tool_input", {}).get("file_path", "")
        
        if tool_name not in ["Write", "Edit", "MultiEdit"] or not file_path:
            return {"status": "not_applicable"}
        
        # Run quality checks
        quality_results = self.check_file_quality(file_path)
        
        # Determine if quality gate passed
        gate_passed = quality_results.get("overall_score", 0) >= 70
        
        result = {
            "file": file_path,
            "tool": tool_name,
            "quality_gate_passed": gate_passed,
            "quality_score": quality_results.get("overall_score", 0),
            "checks": quality_results,
            "recommendations": self.generate_recommendations(quality_results)
        }
        
        # Log quality results
        self.log_quality_check(result)
        
        return result
    
    def generate_recommendations(self, quality_results: Dict) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        for check_name, check_result in quality_results.items():
            if check_name.endswith("_check") and isinstance(check_result, dict):
                if not check_result.get("passed", True):
                    if check_name == "size_check":
                        recommendations.append("Consider breaking large file into smaller modules")
                    elif check_name == "security_check":
                        recommendations.append("Review and fix security issues")
                    elif check_name == "style_check":
                        recommendations.append("Run code formatter (black, prettier, etc.)")
                    elif check_name == "complexity_check":
                        recommendations.append("Refactor complex functions into smaller units")
        
        return recommendations
    
    def log_quality_check(self, result: Dict):
        """Log quality check results"""
        log_file = self.home_dir / "quality_history.jsonl"
        log_entry = {
            "timestamp": self.get_timestamp(),
            "file": result["file"],
            "score": result["quality_score"],
            "passed": result["quality_gate_passed"]
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
    
    hook = QualityGateHook()
    result = hook.process_file_operation(hook_data)
    
    # Output quality results if applicable
    if result.get("status") != "not_applicable":
        score = result.get("quality_score", 0)
        passed = result.get("quality_gate_passed", False)
        
        if not passed:
            print(f"Quality Gate: {score:.0f}% (FAILED)", file=sys.stderr)
            for rec in result.get("recommendations", []):
                print(f"  • {rec}", file=sys.stderr)
        elif os.environ.get("CLAUDE_DEBUG"):
            print(f"Quality Gate: {score:.0f}% (PASSED)", file=sys.stderr)
    
    sys.exit(0)

if __name__ == "__main__":
    main()