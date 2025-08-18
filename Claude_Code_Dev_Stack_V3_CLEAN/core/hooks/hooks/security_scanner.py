#!/usr/bin/env python3
"""
Security Scanner Hook - V3.0+ Vulnerability Detection
Scans code for security vulnerabilities and compliance issues
"""

import os
import json
import re
import sys
import subprocess
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime

class SecurityScanner:
    """Security vulnerability scanner for multiple languages"""
    
    def __init__(self):
        self.claude_dir = Path.home() / '.claude'
        self.settings = self.load_settings()
        
        # Get security settings
        sec_settings = self.settings.get('v3ExtendedFeatures', {}).get('security', {})
        self.enabled = sec_settings.get('enabled', True)
        self.scan_on_commit = sec_settings.get('scanOnCommit', True)
        self.block_on_high = sec_settings.get('blockOnHigh', True)
        self.scan_dependencies = sec_settings.get('scanDependencies', True)
        
        # Security rules by language
        self.security_rules = {
            'python': {
                'high_risk': [
                    (r'exec\s*\(', 'Code injection via exec()'),
                    (r'eval\s*\(', 'Code injection via eval()'),
                    (r'subprocess\.call\s*\(.*shell\s*=\s*True', 'Shell injection risk'),
                    (r'os\.system\s*\(', 'Command injection via os.system()'),
                    (r'pickle\.loads?\s*\(', 'Insecure deserialization'),
                    (r'input\s*\([^)]*\)', 'Raw input usage (Python 2)'),
                    (r'__import__\s*\(.*\)', 'Dynamic import risk'),
                    (r'compile\s*\(', 'Code compilation risk')
                ],
                'medium_risk': [
                    (r'random\.random\s*\(', 'Weak random number generation'),
                    (r'hashlib\.md5\s*\(', 'Weak hashing algorithm (MD5)'),
                    (r'hashlib\.sha1\s*\(', 'Weak hashing algorithm (SHA1)'),
                    (r'ssl\.PROTOCOL_SSLv[23]', 'Insecure SSL/TLS protocol'),
                    (r'requests\.get\s*\([^)]*verify\s*=\s*False', 'SSL verification disabled'),
                    (r'urllib\.request\.urlopen\s*\([^)]*\)', 'Unvalidated URL request'),
                    (r'tempfile\.mktemp\s*\(', 'Insecure temporary file'),
                    (r'assert\s+', 'Assert statement in production code')
                ],
                'low_risk': [
                    (r'print\s*\([^)]*password', 'Potential password exposure in logs'),
                    (r'print\s*\([^)]*secret', 'Potential secret exposure in logs'),
                    (r'logging\.[^(]*\([^)]*password', 'Password in logs'),
                    (r'TODO.*security', 'Security-related TODO item'),
                    (r'FIXME.*security', 'Security-related FIXME item')
                ]
            },
            'javascript': {
                'high_risk': [
                    (r'eval\s*\(', 'Code injection via eval()'),
                    (r'Function\s*\(.*\)', 'Dynamic function creation'),
                    (r'document\.write\s*\(', 'DOM injection via document.write'),
                    (r'innerHTML\s*=', 'Potential XSS via innerHTML'),
                    (r'outerHTML\s*=', 'Potential XSS via outerHTML'),
                    (r'dangerouslySetInnerHTML', 'React dangerouslySetInnerHTML usage'),
                    (r'localStorage\.setItem\s*\([^)]*password', 'Password in localStorage'),
                    (r'sessionStorage\.setItem\s*\([^)]*password', 'Password in sessionStorage')
                ],
                'medium_risk': [
                    (r'Math\.random\s*\(', 'Weak random number generation'),
                    (r'window\.open\s*\(', 'Popup vulnerability'),
                    (r'location\.href\s*=', 'Potential redirect vulnerability'),
                    (r'document\.cookie', 'Direct cookie manipulation'),
                    (r'postMessage\s*\(', 'Cross-origin messaging risk'),
                    (r'fetch\s*\([^)]*\{[^}]*mode:\s*[\'"]no-cors', 'CORS bypass attempt'),
                    (r'XMLHttpRequest', 'Legacy AJAX usage')
                ],
                'low_risk': [
                    (r'console\.log\s*\([^)]*password', 'Password in console logs'),
                    (r'console\.log\s*\([^)]*secret', 'Secret in console logs'),
                    (r'alert\s*\([^)]*password', 'Password in alert'),
                    (r'// TODO.*security', 'Security-related TODO'),
                    (r'// FIXME.*security', 'Security-related FIXME')
                ]
            },
            'php': {
                'high_risk': [
                    (r'eval\s*\(', 'Code injection via eval()'),
                    (r'exec\s*\(', 'Command execution'),
                    (r'system\s*\(', 'System command execution'),
                    (r'shell_exec\s*\(', 'Shell command execution'),
                    (r'passthru\s*\(', 'Command execution via passthru'),
                    (r'file_get_contents\s*\(\s*[\'"]http', 'Remote file inclusion'),
                    (r'include\s*\(\s*\$', 'Dynamic file inclusion'),
                    (r'require\s*\(\s*\$', 'Dynamic file inclusion'),
                    (r'unserialize\s*\(', 'Insecure deserialization'),
                    (r'\$_GET\[.*\].*echo', 'Potential XSS via GET'),
                    (r'\$_POST\[.*\].*echo', 'Potential XSS via POST')
                ],
                'medium_risk': [
                    (r'md5\s*\(', 'Weak hashing algorithm'),
                    (r'sha1\s*\(', 'Weak hashing algorithm'),
                    (r'mysql_query\s*\(', 'Legacy MySQL function'),
                    (r'curl_setopt.*CURLOPT_SSL_VERIFYPEER.*false', 'SSL verification disabled'),
                    (r'rand\s*\(', 'Weak random number generation'),
                    (r'mt_rand\s*\(', 'Weak random number generation'),
                    (r'extract\s*\(', 'Variable extraction risk')
                ],
                'low_risk': [
                    (r'echo.*password', 'Password in output'),
                    (r'print.*password', 'Password in output'),
                    (r'var_dump.*password', 'Password in debug output'),
                    (r'// TODO.*security', 'Security-related TODO'),
                    (r'// FIXME.*security', 'Security-related FIXME')
                ]
            },
            'java': {
                'high_risk': [
                    (r'Runtime\.getRuntime\(\)\.exec', 'Command execution'),
                    (r'ProcessBuilder.*start', 'Process execution'),
                    (r'ObjectInputStream.*readObject', 'Insecure deserialization'),
                    (r'ScriptEngine.*eval', 'Code injection via script engine'),
                    (r'Class\.forName\s*\(', 'Dynamic class loading'),
                    (r'Method\.invoke\s*\(', 'Reflection-based execution'),
                    (r'System\.setProperty\s*\("java\.security"', 'Security policy manipulation')
                ],
                'medium_risk': [
                    (r'MessageDigest\.getInstance\s*\("MD5"', 'Weak hashing algorithm'),
                    (r'MessageDigest\.getInstance\s*\("SHA1"', 'Weak hashing algorithm'),
                    (r'Random\s*\(', 'Weak random number generation'),
                    (r'TrustManager.*checkServerTrusted', 'Custom trust manager'),
                    (r'HostnameVerifier.*verify', 'Custom hostname verifier'),
                    (r'SSLContext\.getInstance\s*\("SSL"', 'Insecure SSL context')
                ],
                'low_risk': [
                    (r'System\.out\.print.*password', 'Password in output'),
                    (r'Logger.*password', 'Password in logs'),
                    (r'// TODO.*security', 'Security-related TODO'),
                    (r'// FIXME.*security', 'Security-related FIXME')
                ]
            },
            'go': {
                'high_risk': [
                    (r'exec\.Command\s*\(', 'Command execution'),
                    (r'os\.Exec\s*\(', 'Process execution'),
                    (r'unsafe\.Pointer', 'Unsafe memory operations'),
                    (r'reflect\.Call', 'Reflection-based execution'),
                    (r'fmt\.Sprintf.*%s.*\+', 'Format string vulnerability'),
                    (r'sql\.Query\s*\([^?]*\+', 'SQL injection risk')
                ],
                'medium_risk': [
                    (r'math/rand\.', 'Weak random number generation'),
                    (r'crypto/md5', 'Weak hashing algorithm'),
                    (r'crypto/sha1', 'Weak hashing algorithm'),
                    (r'tls\.Config.*InsecureSkipVerify.*true', 'TLS verification disabled'),
                    (r'http\.DefaultTransport', 'Default HTTP transport usage')
                ],
                'low_risk': [
                    (r'fmt\.Print.*password', 'Password in output'),
                    (r'log\.Print.*password', 'Password in logs'),
                    (r'// TODO.*security', 'Security-related TODO'),
                    (r'// FIXME.*security', 'Security-related FIXME')
                ]
            },
            'rust': {
                'high_risk': [
                    (r'unsafe\s*\{', 'Unsafe code block'),
                    (r'std::process::Command', 'Command execution'),
                    (r'std::ptr::', 'Raw pointer usage'),
                    (r'transmute\s*\(', 'Memory transmutation'),
                    (r'from_raw_parts', 'Raw memory access')
                ],
                'medium_risk': [
                    (r'rand::random', 'Standard random (consider crypto rand)'),
                    (r'md5::', 'Weak hashing algorithm'),
                    (r'sha1::', 'Weak hashing algorithm'),
                    (r'unwrap\(\)', 'Panic on error (consider proper error handling)')
                ],
                'low_risk': [
                    (r'println!.*password', 'Password in output'),
                    (r'eprintln!.*password', 'Password in error output'),
                    (r'// TODO.*security', 'Security-related TODO'),
                    (r'// FIXME.*security', 'Security-related FIXME')
                ]
            }
        }
        
        # Common sensitive patterns across all languages
        self.common_patterns = {
            'secrets': [
                (r'[\'"][A-Za-z0-9+/]{40,}[=]{0,2}[\'"]', 'Potential base64 encoded secret'),
                (r'password\s*=\s*[\'"][^\'\"]{8,}[\'"]', 'Hardcoded password'),
                (r'secret\s*=\s*[\'"][^\'\"]{8,}[\'"]', 'Hardcoded secret'),
                (r'api[_-]?key\s*=\s*[\'"][^\'\"]{8,}[\'"]', 'Hardcoded API key'),
                (r'token\s*=\s*[\'"][^\'\"]{20,}[\'"]', 'Hardcoded token'),
                (r'private[_-]?key\s*=', 'Private key reference'),
                (r'-----BEGIN RSA PRIVATE KEY-----', 'RSA private key'),
                (r'-----BEGIN PRIVATE KEY-----', 'Private key'),
                (r'sk_live_[0-9a-zA-Z]{24,}', 'Stripe live secret key'),
                (r'sk_test_[0-9a-zA-Z]{24,}', 'Stripe test secret key'),
                (r'AKIA[0-9A-Z]{16}', 'AWS access key'),
                (r'xox[baprs]-[0-9a-zA-Z]{10,48}', 'Slack token'),
                (r'ghp_[0-9a-zA-Z]{36}', 'GitHub personal access token'),
                (r'glpat-[0-9a-zA-Z_\-]{20}', 'GitLab personal access token')
            ]
        }
        
        # Dependency scanners
        self.dependency_scanners = {
            'npm': ['npm', 'audit', '--json'],
            'pip': ['safety', 'check', '--json'],
            'cargo': ['cargo', 'audit', '--json'],
            'composer': ['composer', 'audit', '--format=json'],
            'bundle': ['bundle', 'audit', '--format=json']
        }
    
    def load_settings(self) -> Dict:
        """Load settings from settings.json"""
        settings_path = self.claude_dir / 'settings.json'
        if settings_path.exists():
            try:
                with open(settings_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def detect_language(self, file_path: Path) -> Optional[str]:
        """Detect programming language from file extension"""
        ext = file_path.suffix.lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'javascript',
            '.tsx': 'javascript',
            '.php': 'php',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.c': 'c',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.h': 'c',
            '.hpp': 'cpp',
            '.rb': 'ruby',
            '.sh': 'shell',
            '.bash': 'shell',
            '.ps1': 'powershell'
        }
        
        return language_map.get(ext)
    
    def scan_file_content(self, file_path: Path) -> List[Dict]:
        """Scan file content for security issues"""
        if not file_path.exists():
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            return []
        
        issues = []
        language = self.detect_language(file_path)
        
        # Scan language-specific patterns
        if language and language in self.security_rules:
            rules = self.security_rules[language]
            
            for severity in ['high_risk', 'medium_risk', 'low_risk']:
                for pattern, description in rules.get(severity, []):
                    matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        issues.append({
                            'file': str(file_path),
                            'line': line_num,
                            'severity': severity.replace('_risk', '').upper(),
                            'type': 'code_vulnerability',
                            'description': description,
                            'pattern': pattern,
                            'snippet': content[max(0, match.start()-20):match.end()+20].strip()
                        })
        
        # Scan common secret patterns
        for pattern, description in self.common_patterns['secrets']:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues.append({
                    'file': str(file_path),
                    'line': line_num,
                    'severity': 'HIGH',
                    'type': 'hardcoded_secret',
                    'description': description,
                    'pattern': pattern,
                    'snippet': content[max(0, match.start()-10):match.end()+10].strip()
                })
        
        return issues
    
    def scan_dependencies(self, directory: str = '.') -> List[Dict]:
        """Scan project dependencies for vulnerabilities"""
        if not self.scan_dependencies:
            return []
        
        directory = Path(directory)
        issues = []
        
        for scanner_name, command in self.dependency_scanners.items():
            # Check if the project uses this package manager
            manifest_files = {
                'npm': ['package.json'],
                'pip': ['requirements.txt', 'setup.py', 'pyproject.toml'],
                'cargo': ['Cargo.toml'],
                'composer': ['composer.json'],
                'bundle': ['Gemfile']
            }
            
            if scanner_name not in manifest_files:
                continue
            
            # Check if manifest exists
            has_manifest = any((directory / f).exists() for f in manifest_files[scanner_name])
            if not has_manifest:
                continue
            
            # Check if scanner is available
            try:
                result = subprocess.run(
                    ['which', command[0]] if os.name != 'nt' else ['where', command[0]],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    continue
            except:
                continue
            
            # Run dependency scan
            try:
                result = subprocess.run(
                    command,
                    cwd=directory,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode != 0 and result.stdout:
                    # Parse scanner-specific output
                    if scanner_name == 'npm':
                        try:
                            audit_data = json.loads(result.stdout)
                            for vuln_id, vuln in audit_data.get('vulnerabilities', {}).items():
                                issues.append({
                                    'file': 'package.json',
                                    'line': 0,
                                    'severity': vuln.get('severity', 'unknown').upper(),
                                    'type': 'dependency_vulnerability',
                                    'description': f"Vulnerable dependency: {vuln.get('name', vuln_id)}",
                                    'details': vuln.get('title', 'No details available')
                                })
                        except json.JSONDecodeError:
                            pass
                    
                    elif scanner_name == 'pip':
                        # Safety output parsing
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
                            if 'vulnerability' in line.lower():
                                issues.append({
                                    'file': 'requirements.txt',
                                    'line': 0,
                                    'severity': 'HIGH',
                                    'type': 'dependency_vulnerability',
                                    'description': 'Python package vulnerability',
                                    'details': line.strip()
                                })
                    
                    # Add generic parsing for other scanners...
                    
            except subprocess.TimeoutExpired:
                issues.append({
                    'file': f'{scanner_name}_scan',
                    'line': 0,
                    'severity': 'LOW',
                    'type': 'scan_timeout',
                    'description': f'{scanner_name} dependency scan timed out'
                })
            except Exception as e:
                issues.append({
                    'file': f'{scanner_name}_scan',
                    'line': 0,
                    'severity': 'LOW',
                    'type': 'scan_error',
                    'description': f'{scanner_name} dependency scan error: {str(e)}'
                })
        
        return issues
    
    def scan_files(self, file_paths: List[str]) -> Dict:
        """Scan multiple files for security issues"""
        all_issues = []
        
        # Play audio notification
        self.play_audio('security_scanning.wav')
        
        for file_path in file_paths:
            try:
                path = Path(file_path)
                if path.exists() and path.is_file():
                    issues = self.scan_file_content(path)
                    all_issues.extend(issues)
            except Exception as e:
                all_issues.append({
                    'file': file_path,
                    'line': 0,
                    'severity': 'LOW',
                    'type': 'scan_error',
                    'description': f'Error scanning file: {str(e)}'
                })
        
        # Categorize issues by severity
        severity_counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for issue in all_issues:
            severity = issue.get('severity', 'LOW')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            'total_issues': len(all_issues),
            'severity_counts': severity_counts,
            'issues': all_issues,
            'files_scanned': len(file_paths),
            'timestamp': datetime.now().isoformat()
        }
    
    def scan_directory(self, directory: str = '.', exclude_dirs: Set[str] = None) -> Dict:
        """Scan entire directory for security issues"""
        directory = Path(directory)
        
        if exclude_dirs is None:
            exclude_dirs = {
                'node_modules', '.git', '__pycache__', 'venv', '.venv',
                'dist', 'build', 'target', '.tox', '.pytest_cache'
            }
        
        # Find all source code files
        source_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.php', '.java', '.go', '.rs', '.rb', '.sh', '.ps1'}
        source_files = []
        
        for ext in source_extensions:
            files = directory.rglob(f"*{ext}")
            # Filter out excluded directories
            filtered_files = [f for f in files if not any(exc in f.parts for exc in exclude_dirs)]
            source_files.extend(str(f) for f in filtered_files)
        
        # Scan files
        file_results = self.scan_files(source_files)
        
        # Scan dependencies
        dep_issues = self.scan_dependencies(str(directory))
        file_results['issues'].extend(dep_issues)
        file_results['total_issues'] += len(dep_issues)
        
        # Update severity counts
        for issue in dep_issues:
            severity = issue.get('severity', 'LOW')
            file_results['severity_counts'][severity] = file_results['severity_counts'].get(severity, 0) + 1
        
        return file_results
    
    def generate_report(self, scan_results: Dict) -> str:
        """Generate security scan report"""
        report_lines = [
            "# Security Scan Report",
            f"Generated: {scan_results.get('timestamp', 'Unknown')}",
            "",
            "## Summary",
            f"- **Total Issues**: {scan_results['total_issues']}",
            f"- **Files Scanned**: {scan_results['files_scanned']}",
            f"- **High Severity**: {scan_results['severity_counts'].get('HIGH', 0)}",
            f"- **Medium Severity**: {scan_results['severity_counts'].get('MEDIUM', 0)}",
            f"- **Low Severity**: {scan_results['severity_counts'].get('LOW', 0)}",
            ""
        ]
        
        if scan_results['total_issues'] == 0:
            report_lines.append("✅ **No security issues found!**")
            return '\n'.join(report_lines)
        
        # Group issues by severity
        issues_by_severity = {}
        for issue in scan_results['issues']:
            severity = issue.get('severity', 'LOW')
            if severity not in issues_by_severity:
                issues_by_severity[severity] = []
            issues_by_severity[severity].append(issue)
        
        # Report by severity
        for severity in ['HIGH', 'MEDIUM', 'LOW']:
            if severity not in issues_by_severity:
                continue
            
            report_lines.extend([
                f"## {severity} Severity Issues",
                ""
            ])
            
            for issue in issues_by_severity[severity]:
                report_lines.extend([
                    f"### {issue['file']}:{issue['line']}",
                    f"**Type**: {issue['type']}",
                    f"**Description**: {issue['description']}",
                    ""
                ])
                
                if 'snippet' in issue:
                    report_lines.extend([
                        "**Code snippet**:",
                        "```",
                        issue['snippet'],
                        "```",
                        ""
                    ])
        
        return '\n'.join(report_lines)
    
    def check_pre_commit(self, staged_files: List[str]) -> Tuple[bool, Dict]:
        """Security check for pre-commit hook"""
        scan_results = self.scan_files(staged_files)
        
        # Determine if commit should be blocked
        high_issues = scan_results['severity_counts'].get('HIGH', 0)
        
        if self.block_on_high and high_issues > 0:
            return False, scan_results
        
        return True, scan_results
    
    def play_audio(self, filename: str):
        """Play audio notification"""
        try:
            audio_path = self.claude_dir / 'audio' / filename
            if audio_path.exists():
                import winsound
                winsound.PlaySound(str(audio_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
        except:
            pass

def main():
    """Hook entry point"""
    scanner = SecurityScanner()
    
    if len(sys.argv) < 2:
        print("Usage: security_scanner.py <action> [args]")
        print("Actions:")
        print("  scan-file <file>     - Scan single file")
        print("  scan-files <files>   - Scan multiple files")
        print("  scan-directory [dir] - Scan entire directory")
        print("  scan-dependencies [dir] - Scan only dependencies")
        print("  pre-commit <files>   - Pre-commit security check")
        print("  report <scan_file>   - Generate report from scan results")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == 'scan-file' and len(sys.argv) > 2:
        file_path = sys.argv[2]
        issues = scanner.scan_file_content(Path(file_path))
        print(json.dumps(issues, indent=2))
        sys.exit(0 if not issues else 1)
    
    elif action == 'scan-files':
        files = sys.argv[2:]
        results = scanner.scan_files(files)
        print(json.dumps(results, indent=2))
        sys.exit(0 if results['severity_counts'].get('HIGH', 0) == 0 else 1)
    
    elif action == 'scan-directory':
        directory = sys.argv[2] if len(sys.argv) > 2 else '.'
        results = scanner.scan_directory(directory)
        print(json.dumps(results, indent=2))
        sys.exit(0 if results['severity_counts'].get('HIGH', 0) == 0 else 1)
    
    elif action == 'scan-dependencies':
        directory = sys.argv[2] if len(sys.argv) > 2 else '.'
        issues = scanner.scan_dependencies(directory)
        print(json.dumps(issues, indent=2))
        sys.exit(0 if not any(i.get('severity') == 'HIGH' for i in issues) else 1)
    
    elif action == 'pre-commit':
        files = sys.argv[2:]
        allowed, results = scanner.check_pre_commit(files)
        print(json.dumps(results, indent=2))
        sys.exit(0 if allowed else 1)
    
    elif action == 'report' and len(sys.argv) > 2:
        scan_file = sys.argv[2]
        try:
            with open(scan_file, 'r') as f:
                results = json.load(f)
            report = scanner.generate_report(results)
            print(report)
        except Exception as e:
            print(f"Error generating report: {e}")
            sys.exit(1)
    
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == '__main__':
    main()