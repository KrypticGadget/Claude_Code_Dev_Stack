#!/usr/bin/env python3
"""
Quality Gate Hook - Enforce code quality standards and best practices
Runs checks on code changes before they are applied
"""

import sys
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from base_hook import BaseHook


class QualityGate(BaseHook):
    """Enforce quality standards on code changes"""
    
    def __init__(self):
        super().__init__('quality_gate')
        self.load_quality_rules()
    
    def run(self) -> int:
        """Run quality checks on proposed changes"""
        # Read change data from stdin
        change_data = self._read_change_data()
        
        if not change_data:
            self.logger.debug("No changes to validate")
            return 0
        
        # Run quality checks
        results = self._run_quality_checks(change_data)
        
        # Generate report
        report = self._generate_report(results)
        
        # Save results
        self.save_cache('last_quality_check', report)
        
        # Output results
        self.write_stdout(json.dumps(report, indent=2))
        
        # Log summary
        self.logger.info("Quality gate completed", 
                        passed=report['passed'],
                        total_issues=report['total_issues'])
        
        # Return non-zero if quality gate fails (but don't block)
        return 0  # Always return 0 to not block operations
    
    def load_quality_rules(self):
        """Load quality rules from configuration"""
        default_rules = {
            'code_smell_patterns': [
                {'pattern': r'console\.log', 'message': 'Remove console.log statements', 'severity': 'warning'},
                {'pattern': r'debugger;', 'message': 'Remove debugger statements', 'severity': 'error'},
                {'pattern': r'TODO:|FIXME:', 'message': 'Unresolved TODO/FIXME', 'severity': 'info'},
                {'pattern': r'password\s*=\s*["\']', 'message': 'Hardcoded password detected', 'severity': 'error'},
                {'pattern': r'api_key\s*=\s*["\']', 'message': 'Hardcoded API key detected', 'severity': 'error'}
            ],
            'file_size_limits': {
                'max_file_size': 1024 * 1024,  # 1MB
                'max_line_length': 120,
                'max_file_lines': 1000
            },
            'complexity_thresholds': {
                'max_function_length': 50,
                'max_cyclomatic_complexity': 10,
                'max_nesting_depth': 4
            },
            'naming_conventions': {
                'variable_pattern': r'^[a-z][a-zA-Z0-9]*$',
                'function_pattern': r'^[a-z][a-zA-Z0-9]*$',
                'class_pattern': r'^[A-Z][a-zA-Z0-9]*$',
                'constant_pattern': r'^[A-Z][A-Z0-9_]*$'
            }
        }
        
        # Load custom rules from config
        custom_rules = self.config.get('quality_rules', {})
        
        # Merge rules
        self.rules = {**default_rules, **custom_rules}
    
    def _read_change_data(self) -> Dict[str, Any]:
        """Read change data from stdin"""
        input_text = self.read_stdin()
        
        if not input_text:
            return {}
        
        try:
            return json.loads(input_text)
        except json.JSONDecodeError:
            # If not JSON, assume it's file content
            return {
                'type': 'file_content',
                'content': input_text,
                'files': []
            }
    
    def _run_quality_checks(self, change_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Run all quality checks"""
        results = {
            'code_smells': [],
            'size_violations': [],
            'complexity_issues': [],
            'naming_violations': [],
            'security_issues': [],
            'best_practices': [],
            'formatting_issues': []
        }
        
        # Check each file
        for file_info in change_data.get('files', []):
            file_path = Path(file_info.get('path', ''))
            content = file_info.get('content', '')
            
            if not content:
                continue
            
            # Run checks based on file type
            if file_path.suffix in ['.js', '.jsx', '.ts', '.tsx']:
                self._check_javascript_file(file_path, content, results)
            elif file_path.suffix in ['.py']:
                self._check_python_file(file_path, content, results)
            elif file_path.suffix in ['.java']:
                self._check_java_file(file_path, content, results)
            elif file_path.suffix in ['.go']:
                self._check_go_file(file_path, content, results)
            
            # Common checks for all files
            self._check_common_issues(file_path, content, results)
        
        return results
    
    def _check_common_issues(self, file_path: Path, content: str, results: Dict[str, List]):
        """Check for common issues across all file types"""
        lines = content.split('\n')
        
        # Check for code smells
        for i, line in enumerate(lines, 1):
            for rule in self.rules['code_smell_patterns']:
                if re.search(rule['pattern'], line, re.IGNORECASE):
                    results['code_smells'].append({
                        'file': str(file_path),
                        'line': i,
                        'message': rule['message'],
                        'severity': rule['severity'],
                        'code': line.strip()
                    })
        
        # Check file size
        if len(content) > self.rules['file_size_limits']['max_file_size']:
            results['size_violations'].append({
                'file': str(file_path),
                'message': f"File exceeds maximum size ({len(content)} bytes)",
                'severity': 'warning'
            })
        
        # Check line count
        if len(lines) > self.rules['file_size_limits']['max_file_lines']:
            results['size_violations'].append({
                'file': str(file_path),
                'message': f"File has too many lines ({len(lines)})",
                'severity': 'warning'
            })
        
        # Check line length
        for i, line in enumerate(lines, 1):
            if len(line) > self.rules['file_size_limits']['max_line_length']:
                results['size_violations'].append({
                    'file': str(file_path),
                    'line': i,
                    'message': f"Line exceeds maximum length ({len(line)} characters)",
                    'severity': 'info'
                })
        
        # Security checks
        security_patterns = [
            (r'eval\s*\(', 'Unsafe use of eval()'),
            (r'exec\s*\(', 'Unsafe use of exec()'),
            (r'__import__', 'Dynamic import detected'),
            (r'pickle\.loads', 'Unsafe deserialization'),
            (r'subprocess\.call.*shell=True', 'Shell injection risk'),
            (r'os\.system', 'Command injection risk')
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, message in security_patterns:
                if re.search(pattern, line):
                    results['security_issues'].append({
                        'file': str(file_path),
                        'line': i,
                        'message': message,
                        'severity': 'error',
                        'code': line.strip()
                    })
    
    def _check_javascript_file(self, file_path: Path, content: str, results: Dict[str, List]):
        """JavaScript/TypeScript specific checks"""
        lines = content.split('\n')
        
        # Check for common JS issues
        js_patterns = [
            (r'var\s+\w+\s*=', 'Use const/let instead of var', 'warning'),
            (r'==(?!=)', 'Use === instead of ==', 'warning'),
            (r'!=(?!=)', 'Use !== instead of !=', 'warning'),
            (r'function\s*\(\s*\)', 'Use arrow functions for anonymous functions', 'info'),
            (r'new Array\(\)', 'Use array literal [] instead of new Array()', 'info'),
            (r'new Object\(\)', 'Use object literal {} instead of new Object()', 'info')
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, message, severity in js_patterns:
                if re.search(pattern, line):
                    results['best_practices'].append({
                        'file': str(file_path),
                        'line': i,
                        'message': message,
                        'severity': severity,
                        'code': line.strip()
                    })
        
        # Check function complexity
        self._check_function_complexity(content, file_path, results, 'javascript')
    
    def _check_python_file(self, file_path: Path, content: str, results: Dict[str, List]):
        """Python specific checks"""
        lines = content.split('\n')
        
        # Python best practices
        python_patterns = [
            (r'except\s*:', 'Avoid bare except clauses', 'warning'),
            (r'import\s+\*', 'Avoid wildcard imports', 'warning'),
            (r'type\s*\(\s*\w+\s*\)\s*==', 'Use isinstance() instead of type() ==', 'warning'),
            (r'open\s*\([^)]+\)(?!.*\s+as\s+)', 'Use context manager for file operations', 'warning')
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, message, severity in python_patterns:
                if re.search(pattern, line):
                    results['best_practices'].append({
                        'file': str(file_path),
                        'line': i,
                        'message': message,
                        'severity': severity,
                        'code': line.strip()
                    })
        
        # Check PEP 8 compliance (basic)
        self._check_python_naming(content, file_path, results)
    
    def _check_function_complexity(self, content: str, file_path: Path, results: Dict[str, List], language: str):
        """Check function complexity metrics"""
        # Simple complexity analysis
        if language == 'javascript':
            function_pattern = r'function\s+(\w+)|(\w+)\s*=\s*(?:async\s+)?(?:function|\(.*?\)\s*=>)'
        elif language == 'python':
            function_pattern = r'def\s+(\w+)'
        else:
            return
        
        # Find functions and analyze
        for match in re.finditer(function_pattern, content, re.MULTILINE):
            func_name = match.group(1) or match.group(2) if language == 'javascript' else match.group(1)
            func_start = match.start()
            
            # Extract function body (simplified)
            func_body = self._extract_function_body(content[func_start:], language)
            
            # Count lines
            func_lines = len(func_body.split('\n'))
            if func_lines > self.rules['complexity_thresholds']['max_function_length']:
                results['complexity_issues'].append({
                    'file': str(file_path),
                    'function': func_name,
                    'message': f"Function too long ({func_lines} lines)",
                    'severity': 'warning'
                })
            
            # Estimate cyclomatic complexity (simplified)
            complexity = self._estimate_complexity(func_body)
            if complexity > self.rules['complexity_thresholds']['max_cyclomatic_complexity']:
                results['complexity_issues'].append({
                    'file': str(file_path),
                    'function': func_name,
                    'message': f"Function too complex (complexity: {complexity})",
                    'severity': 'warning'
                })
    
    def _extract_function_body(self, content: str, language: str) -> str:
        """Extract function body (simplified implementation)"""
        # This is a simplified extraction - real implementation would need proper parsing
        if language == 'javascript':
            # Find matching braces
            brace_count = 0
            start_pos = content.find('{')
            if start_pos == -1:
                return content[:200]  # Arrow function without braces
            
            for i, char in enumerate(content[start_pos:]):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        return content[start_pos:start_pos + i + 1]
        
        elif language == 'python':
            # Find indented block
            lines = content.split('\n')
            if not lines:
                return ''
            
            # Get indentation of first line after def
            base_indent = len(lines[0]) - len(lines[0].lstrip())
            func_lines = [lines[0]]
            
            for line in lines[1:]:
                if line.strip() and len(line) - len(line.lstrip()) <= base_indent:
                    break
                func_lines.append(line)
            
            return '\n'.join(func_lines)
        
        return content[:500]  # Fallback
    
    def _estimate_complexity(self, code: str) -> int:
        """Estimate cyclomatic complexity (simplified)"""
        # Count decision points
        complexity = 1  # Base complexity
        
        decision_keywords = [
            r'\bif\b', r'\belse\b', r'\belif\b', r'\bwhile\b', r'\bfor\b',
            r'\bcase\b', r'\bcatch\b', r'\bexcept\b', r'\b\?\s*:', r'\b&&\b', r'\b\|\|\b'
        ]
        
        for keyword in decision_keywords:
            complexity += len(re.findall(keyword, code))
        
        return complexity
    
    def _check_python_naming(self, content: str, file_path: Path, results: Dict[str, List]):
        """Check Python naming conventions"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check variable names
            var_match = re.match(r'^\s*(\w+)\s*=', line)
            if var_match:
                var_name = var_match.group(1)
                if var_name.isupper():  # Likely a constant
                    if not re.match(self.rules['naming_conventions']['constant_pattern'], var_name):
                        results['naming_violations'].append({
                            'file': str(file_path),
                            'line': i,
                            'message': f"Constant '{var_name}' doesn't follow naming convention",
                            'severity': 'info'
                        })
                elif not re.match(self.rules['naming_conventions']['variable_pattern'], var_name):
                    results['naming_violations'].append({
                        'file': str(file_path),
                        'line': i,
                        'message': f"Variable '{var_name}' doesn't follow naming convention",
                        'severity': 'info'
                    })
            
            # Check class names
            class_match = re.match(r'^\s*class\s+(\w+)', line)
            if class_match:
                class_name = class_match.group(1)
                if not re.match(self.rules['naming_conventions']['class_pattern'], class_name):
                    results['naming_violations'].append({
                        'file': str(file_path),
                        'line': i,
                        'message': f"Class '{class_name}' doesn't follow naming convention",
                        'severity': 'warning'
                    })
    
    def _check_java_file(self, file_path: Path, content: str, results: Dict[str, List]):
        """Java specific checks"""
        # Placeholder for Java-specific checks
        pass
    
    def _check_go_file(self, file_path: Path, content: str, results: Dict[str, List]):
        """Go specific checks"""
        # Placeholder for Go-specific checks
        pass
    
    def _generate_report(self, results: Dict[str, List]) -> Dict[str, Any]:
        """Generate quality gate report"""
        # Count issues by severity
        severity_counts = {
            'error': 0,
            'warning': 0,
            'info': 0
        }
        
        total_issues = 0
        for category, issues in results.items():
            for issue in issues:
                severity = issue.get('severity', 'info')
                severity_counts[severity] += 1
                total_issues += 1
        
        # Determine if quality gate passes
        passed = severity_counts['error'] == 0
        
        # Create summary
        summary = {
            'passed': passed,
            'total_issues': total_issues,
            'severity_counts': severity_counts,
            'timestamp': datetime.now().isoformat(),
            'project_dir': str(self.env.project_dir)
        }
        
        # Add detailed results
        report = {
            **summary,
            'results': results,
            'recommendations': self._generate_recommendations(results)
        }
        
        return report
    
    def _generate_recommendations(self, results: Dict[str, List]) -> List[str]:
        """Generate recommendations based on results"""
        recommendations = []
        
        if results['security_issues']:
            recommendations.append("🔒 Address security issues immediately")
        
        if results['code_smells']:
            recommendations.append("🧹 Clean up code smells for better maintainability")
        
        if results['complexity_issues']:
            recommendations.append("📊 Refactor complex functions to improve readability")
        
        if results['naming_violations']:
            recommendations.append("📝 Follow naming conventions for consistency")
        
        if not recommendations:
            recommendations.append("✅ Code quality looks good!")
        
        return recommendations


def main():
    """Main entry point"""
    gate = QualityGate()
    return gate.safe_run()


if __name__ == "__main__":
    sys.exit(main())