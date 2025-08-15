#!/usr/bin/env python3
"""
Dependency Checker Hook - V3.0+ Package Management
Manages and validates project dependencies across multiple languages
"""

import os
import json
import subprocess
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional

class DependencyChecker:
    """Check and manage project dependencies"""
    
    def __init__(self):
        self.claude_dir = Path.home() / '.claude'
        self.settings = self.load_settings()
        
        # Get dependency settings
        dep_settings = self.settings.get('v3ExtendedFeatures', {}).get('dependencyManagement', {})
        self.auto_install = dep_settings.get('autoInstall', True)
        self.check_security = dep_settings.get('checkSecurity', True)
        self.update_lockfiles = dep_settings.get('updateLockfiles', False)
        self.check_outdated = dep_settings.get('checkOutdated', True)
        
        # Package managers and their configurations
        self.package_managers = {
            'npm': {
                'name': 'Node.js (npm)',
                'manifest_files': ['package.json'],
                'lockfiles': ['package-lock.json', 'yarn.lock'],
                'install_cmd': ['npm', 'install'],
                'check_cmd': ['npm', 'audit'],
                'outdated_cmd': ['npm', 'outdated'],
                'security_cmd': ['npm', 'audit', '--audit-level', 'moderate'],
                'patterns': {
                    'import': [
                        r"import\s+.*\s+from\s+['\"]([^'\"]+)['\"]",
                        r"require\s*\(\s*['\"]([^'\"]+)['\"]"
                    ]
                }
            },
            'pip': {
                'name': 'Python (pip)',
                'manifest_files': ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile'],
                'lockfiles': ['requirements-lock.txt', 'Pipfile.lock'],
                'install_cmd': ['pip', 'install', '-r', 'requirements.txt'],
                'check_cmd': ['pip', 'check'],
                'outdated_cmd': ['pip', 'list', '--outdated'],
                'security_cmd': ['safety', 'check'],
                'patterns': {
                    'import': [
                        r"^import\s+(\w+)",
                        r"^from\s+(\w+)",
                        r"__import__\s*\(\s*['\"]([^'\"]+)['\"]"
                    ]
                }
            },
            'cargo': {
                'name': 'Rust (Cargo)',
                'manifest_files': ['Cargo.toml'],
                'lockfiles': ['Cargo.lock'],
                'install_cmd': ['cargo', 'build'],
                'check_cmd': ['cargo', 'check'],
                'outdated_cmd': ['cargo', 'outdated'],
                'security_cmd': ['cargo', 'audit'],
                'patterns': {
                    'use': [r"use\s+([^:;]+)"]
                }
            },
            'go': {
                'name': 'Go Modules',
                'manifest_files': ['go.mod'],
                'lockfiles': ['go.sum'],
                'install_cmd': ['go', 'mod', 'download'],
                'check_cmd': ['go', 'mod', 'verify'],
                'outdated_cmd': ['go', 'list', '-u', '-m', 'all'],
                'security_cmd': ['govulncheck', './...'],
                'patterns': {
                    'import': [r"import\s+[\"']([^\"']+)[\"']"]
                }
            },
            'composer': {
                'name': 'PHP (Composer)',
                'manifest_files': ['composer.json'],
                'lockfiles': ['composer.lock'],
                'install_cmd': ['composer', 'install'],
                'check_cmd': ['composer', 'validate'],
                'outdated_cmd': ['composer', 'outdated'],
                'security_cmd': ['composer', 'audit'],
                'patterns': {
                    'use': [r"use\s+([^;]+);"]
                }
            },
            'bundle': {
                'name': 'Ruby (Bundler)',
                'manifest_files': ['Gemfile'],
                'lockfiles': ['Gemfile.lock'],
                'install_cmd': ['bundle', 'install'],
                'check_cmd': ['bundle', 'check'],
                'outdated_cmd': ['bundle', 'outdated'],
                'security_cmd': ['bundle', 'audit'],
                'patterns': {
                    'require': [r"require\s+['\"]([^'\"]+)['\"]"]
                }
            },
            'maven': {
                'name': 'Java (Maven)',
                'manifest_files': ['pom.xml'],
                'lockfiles': [],
                'install_cmd': ['mvn', 'install'],
                'check_cmd': ['mvn', 'validate'],
                'outdated_cmd': ['mvn', 'versions:display-dependency-updates'],
                'security_cmd': ['mvn', 'org.owasp:dependency-check-maven:check'],
                'patterns': {
                    'import': [r"import\s+([^;]+);"]
                }
            },
            'gradle': {
                'name': 'Java (Gradle)',
                'manifest_files': ['build.gradle', 'build.gradle.kts'],
                'lockfiles': [],
                'install_cmd': ['gradle', 'build'],
                'check_cmd': ['gradle', 'check'],
                'outdated_cmd': ['gradle', 'dependencyUpdates'],
                'security_cmd': ['gradle', 'dependencyCheckAnalyze'],
                'patterns': {
                    'import': [r"import\s+([^;]+);"]
                }
            }
        }
        
        # Cache for detected dependencies
        self.dependency_cache = {}
    
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
    
    def detect_project_types(self, directory: str = '.') -> List[str]:
        """Detect which package managers are used in project"""
        directory = Path(directory)
        detected = []
        
        for manager_name, config in self.package_managers.items():
            for manifest_file in config['manifest_files']:
                if (directory / manifest_file).exists():
                    detected.append(manager_name)
                    break
        
        return detected
    
    def check_command_available(self, command: str) -> bool:
        """Check if a command is available in PATH"""
        try:
            result = subprocess.run(
                ['which', command] if os.name != 'nt' else ['where', command],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def scan_imports(self, file_path: str) -> Set[str]:
        """Scan file for imported modules/packages"""
        imports = set()
        file_path = Path(file_path)
        
        if not file_path.exists():
            return imports
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Determine file type and appropriate patterns
            ext = file_path.suffix.lower()
            patterns = []
            
            if ext in ['.py']:
                patterns = self.package_managers['pip']['patterns']['import']
            elif ext in ['.js', '.jsx', '.ts', '.tsx']:
                patterns = self.package_managers['npm']['patterns']['import']
            elif ext in ['.rs']:
                patterns = self.package_managers['cargo']['patterns']['use']
            elif ext in ['.go']:
                patterns = self.package_managers['go']['patterns']['import']
            elif ext in ['.php']:
                patterns = self.package_managers['composer']['patterns']['use']
            elif ext in ['.rb']:
                patterns = self.package_managers['bundle']['patterns']['require']
            elif ext in ['.java']:
                patterns = self.package_managers['maven']['patterns']['import']
            
            # Extract imports using patterns
            for pattern in patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                for match in matches:
                    # Clean up the import name
                    import_name = match.strip().split('.')[0].split('/')[0]
                    if import_name and not import_name.startswith('.'):
                        imports.add(import_name)
                        
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
        
        return imports
    
    def analyze_dependencies(self, directory: str = '.') -> Dict:
        """Analyze project dependencies"""
        directory = Path(directory)
        project_types = self.detect_project_types(directory)
        
        analysis = {
            'project_types': project_types,
            'managers': {},
            'missing_dependencies': [],
            'security_issues': [],
            'outdated_packages': [],
            'recommendations': []
        }
        
        # Play audio notification
        self.play_audio('dependency_installing.wav')
        
        for manager in project_types:
            config = self.package_managers[manager]
            manager_info = {
                'name': config['name'],
                'manifest_found': False,
                'lockfile_found': False,
                'installed': False,
                'status': 'unknown'
            }
            
            # Check manifest files
            for manifest in config['manifest_files']:
                if (directory / manifest).exists():
                    manager_info['manifest_found'] = True
                    break
            
            # Check lockfiles
            for lockfile in config['lockfiles']:
                if (directory / lockfile).exists():
                    manager_info['lockfile_found'] = True
                    break
            
            # Check if package manager is available
            main_command = config['install_cmd'][0]
            if self.check_command_available(main_command):
                manager_info['installed'] = True
                
                # Run basic check
                try:
                    result = subprocess.run(
                        config['check_cmd'],
                        cwd=directory,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    manager_info['status'] = 'ok' if result.returncode == 0 else 'issues'
                    if result.returncode != 0 and result.stderr:
                        manager_info['error'] = result.stderr.strip()
                except subprocess.TimeoutExpired:
                    manager_info['status'] = 'timeout'
                except Exception as e:
                    manager_info['status'] = 'error'
                    manager_info['error'] = str(e)
            else:
                analysis['recommendations'].append(f"Install {config['name']} package manager")
            
            analysis['managers'][manager] = manager_info
        
        return analysis
    
    def check_security_vulnerabilities(self, directory: str = '.') -> Dict:
        """Check for security vulnerabilities in dependencies"""
        directory = Path(directory)
        project_types = self.detect_project_types(directory)
        
        vulnerabilities = {
            'found': False,
            'issues': [],
            'scans_run': 0,
            'scans_failed': 0
        }
        
        for manager in project_types:
            config = self.package_managers[manager]
            
            if not self.check_command_available(config['security_cmd'][0]):
                continue
            
            vulnerabilities['scans_run'] += 1
            
            try:
                result = subprocess.run(
                    config['security_cmd'],
                    cwd=directory,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode != 0:
                    vulnerabilities['found'] = True
                    
                    # Parse vulnerabilities based on manager
                    if manager == 'npm':
                        try:
                            audit_data = json.loads(result.stdout)
                            for vuln in audit_data.get('vulnerabilities', {}).values():
                                vulnerabilities['issues'].append({
                                    'manager': manager,
                                    'package': vuln.get('name', 'unknown'),
                                    'severity': vuln.get('severity', 'unknown'),
                                    'title': vuln.get('title', 'Security issue')
                                })
                        except:
                            vulnerabilities['issues'].append({
                                'manager': manager,
                                'package': 'multiple',
                                'severity': 'unknown',
                                'title': 'Security vulnerabilities found'
                            })
                    else:
                        # Generic parsing
                        if result.stdout:
                            vulnerabilities['issues'].append({
                                'manager': manager,
                                'package': 'multiple',
                                'severity': 'unknown',
                                'title': f"{config['name']} security issues found"
                            })
                
            except subprocess.TimeoutExpired:
                vulnerabilities['scans_failed'] += 1
            except Exception as e:
                vulnerabilities['scans_failed'] += 1
        
        return vulnerabilities
    
    def auto_install_dependencies(self, directory: str = '.') -> Dict:
        """Automatically install missing dependencies"""
        if not self.auto_install:
            return {'success': False, 'message': 'Auto-install disabled'}
        
        directory = Path(directory)
        project_types = self.detect_project_types(directory)
        
        results = {
            'installed': [],
            'failed': [],
            'skipped': []
        }
        
        # Play audio notification
        self.play_audio('dependency_installing.wav')
        
        for manager in project_types:
            config = self.package_managers[manager]
            
            if not self.check_command_available(config['install_cmd'][0]):
                results['skipped'].append(f"{config['name']}: Command not available")
                continue
            
            try:
                print(f"Installing {config['name']} dependencies...")
                result = subprocess.run(
                    config['install_cmd'],
                    cwd=directory,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode == 0:
                    results['installed'].append(config['name'])
                else:
                    results['failed'].append(f"{config['name']}: {result.stderr.strip()}")
                
            except subprocess.TimeoutExpired:
                results['failed'].append(f"{config['name']}: Installation timeout")
            except Exception as e:
                results['failed'].append(f"{config['name']}: {str(e)}")
        
        # Play result audio
        if results['failed']:
            self.play_audio('dependency_missing.wav')
        else:
            self.play_audio('dependency_installing.wav')
        
        return results
    
    def check_outdated_packages(self, directory: str = '.') -> Dict:
        """Check for outdated packages"""
        directory = Path(directory)
        project_types = self.detect_project_types(directory)
        
        outdated = {
            'packages': [],
            'total_checks': 0,
            'managers_checked': 0
        }
        
        for manager in project_types:
            config = self.package_managers[manager]
            
            if not self.check_command_available(config['outdated_cmd'][0]):
                continue
            
            outdated['total_checks'] += 1
            
            try:
                result = subprocess.run(
                    config['outdated_cmd'],
                    cwd=directory,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                outdated['managers_checked'] += 1
                
                if result.stdout:
                    # Parse outdated packages (simplified)
                    lines = result.stdout.strip().split('\n')
                    for line in lines[1:]:  # Skip header
                        if line.strip():
                            parts = line.split()
                            if len(parts) >= 2:
                                outdated['packages'].append({
                                    'manager': manager,
                                    'name': parts[0],
                                    'current': parts[1] if len(parts) > 1 else 'unknown',
                                    'latest': parts[2] if len(parts) > 2 else 'unknown'
                                })
                
            except subprocess.TimeoutExpired:
                pass
            except Exception:
                pass
        
        return outdated
    
    def generate_report(self, directory: str = '.') -> Dict:
        """Generate comprehensive dependency report"""
        analysis = self.analyze_dependencies(directory)
        security = self.check_security_vulnerabilities(directory)
        outdated = self.check_outdated_packages(directory)
        
        report = {
            'timestamp': sys.version,  # Simple timestamp
            'directory': str(Path(directory).absolute()),
            'analysis': analysis,
            'security': security,
            'outdated': outdated,
            'summary': {
                'total_managers': len(analysis['project_types']),
                'security_issues': len(security['issues']),
                'outdated_packages': len(outdated['packages']),
                'recommendations': len(analysis['recommendations'])
            }
        }
        
        return report
    
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
    checker = DependencyChecker()
    
    if len(sys.argv) < 2:
        print("Usage: dependency_checker.py <action> [args]")
        print("Actions:")
        print("  analyze [dir]    - Analyze project dependencies")
        print("  install [dir]    - Auto-install dependencies")
        print("  security [dir]   - Check security vulnerabilities")
        print("  outdated [dir]   - Check for outdated packages")
        print("  report [dir]     - Generate full report")
        print("  scan-file <file> - Scan file for imports")
        sys.exit(1)
    
    action = sys.argv[1]
    directory = sys.argv[2] if len(sys.argv) > 2 else '.'
    
    if action == 'analyze':
        analysis = checker.analyze_dependencies(directory)
        print(json.dumps(analysis, indent=2))
    
    elif action == 'install':
        results = checker.auto_install_dependencies(directory)
        print(json.dumps(results, indent=2))
        sys.exit(0 if not results.get('failed') else 1)
    
    elif action == 'security':
        vulnerabilities = checker.check_security_vulnerabilities(directory)
        print(json.dumps(vulnerabilities, indent=2))
        sys.exit(0 if not vulnerabilities['found'] else 1)
    
    elif action == 'outdated':
        outdated = checker.check_outdated_packages(directory)
        print(json.dumps(outdated, indent=2))
    
    elif action == 'report':
        report = checker.generate_report(directory)
        print(json.dumps(report, indent=2))
    
    elif action == 'scan-file' and len(sys.argv) > 2:
        file_path = sys.argv[2]
        imports = checker.scan_imports(file_path)
        print(json.dumps(list(imports), indent=2))
    
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == '__main__':
    main()