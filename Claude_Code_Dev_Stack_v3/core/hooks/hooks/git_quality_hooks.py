#!/usr/bin/env python3
"""
Git Quality Hooks - V3.0+ Pre-commit Validation
Ensures code quality before commits with automated checks
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class GitQualityHooks:
    """Git hooks for code quality enforcement"""
    
    def __init__(self):
        self.claude_dir = Path.home() / '.claude'
        self.settings = self.load_settings()
        
        # Get git hook settings
        git_settings = self.settings.get('v3ExtendedFeatures', {}).get('gitHooks', {})
        self.enabled = git_settings.get('enabled', True)
        self.pre_commit_checks = git_settings.get('preCommitChecks', [
            'lint', 'format', 'test', 'security'
        ])
        self.block_on_failure = git_settings.get('blockOnFailure', True)
        self.auto_fix = git_settings.get('autoFix', True)
        
        # Check types configuration
        self.checks = {
            'lint': {
                'name': 'Code Linting',
                'command': 'code_linter.py',
                'required': True,
                'auto_fixable': True
            },
            'format': {
                'name': 'Code Formatting',
                'command': 'auto_formatter.py',
                'required': True,
                'auto_fixable': True
            },
            'test': {
                'name': 'Unit Tests',
                'command': None,  # Detected based on project
                'required': False,
                'auto_fixable': False
            },
            'security': {
                'name': 'Security Scan',
                'command': 'security_scanner.py',
                'required': False,
                'auto_fixable': False
            },
            'dependencies': {
                'name': 'Dependency Check',
                'command': 'dependency_checker.py',
                'required': False,
                'auto_fixable': True
            },
            'documentation': {
                'name': 'Documentation Check',
                'command': 'auto_documentation.py',
                'required': False,
                'auto_fixable': True
            }
        }
        
        # Git configuration
        self.git_dir = self.find_git_dir()
        self.hooks_dir = self.git_dir / 'hooks' if self.git_dir else None
    
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
    
    def find_git_dir(self) -> Optional[Path]:
        """Find .git directory"""
        current = Path.cwd()
        while current != current.parent:
            git_dir = current / '.git'
            if git_dir.exists():
                return git_dir
            current = current.parent
        return None
    
    def get_staged_files(self) -> List[str]:
        """Get list of staged files"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return [f for f in result.stdout.strip().split('\n') if f]
        except:
            pass
        return []
    
    def get_changed_files(self) -> List[str]:
        """Get list of all changed files"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return [f for f in result.stdout.strip().split('\n') if f]
        except:
            pass
        return []
    
    def run_lint_check(self, files: List[str]) -> Tuple[bool, List[str]]:
        """Run linting on files"""
        messages = []
        success = True
        
        linter_path = self.claude_dir / 'hooks' / 'code_linter.py'
        if not linter_path.exists():
            return True, ["Linter not found, skipping"]
        
        for file_path in files:
            # Skip non-code files
            if Path(file_path).suffix in ['.md', '.txt', '.json', '.yml', '.yaml']:
                continue
            
            try:
                result = subprocess.run(
                    [sys.executable, str(linter_path), 'file', file_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    success = False
                    messages.append(f"Linting issues in {file_path}")
                    if result.stdout:
                        messages.extend(f"  {line}" for line in result.stdout.strip().split('\n'))
                    
            except subprocess.TimeoutExpired:
                messages.append(f"Linting timeout for {file_path}")
            except Exception as e:
                messages.append(f"Linting error for {file_path}: {str(e)}")
        
        return success, messages
    
    def run_format_check(self, files: List[str]) -> Tuple[bool, List[str]]:
        """Check if files are properly formatted"""
        messages = []
        success = True
        
        formatter_path = self.claude_dir / 'hooks' / 'auto_formatter.py'
        if not formatter_path.exists():
            return True, ["Formatter not found, skipping"]
        
        for file_path in files:
            try:
                result = subprocess.run(
                    [sys.executable, str(formatter_path), 'check', file_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    if self.auto_fix:
                        # Try to auto-format
                        fix_result = subprocess.run(
                            [sys.executable, str(formatter_path), 'format', file_path],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        if fix_result.returncode == 0:
                            messages.append(f"Auto-formatted {file_path}")
                            # Re-stage the file
                            subprocess.run(['git', 'add', file_path])
                        else:
                            success = False
                            messages.append(f"Formatting required for {file_path}")
                    else:
                        success = False
                        messages.append(f"Formatting required for {file_path}")
                    
            except subprocess.TimeoutExpired:
                messages.append(f"Format check timeout for {file_path}")
            except Exception as e:
                messages.append(f"Format check error for {file_path}: {str(e)}")
        
        return success, messages
    
    def run_test_check(self) -> Tuple[bool, List[str]]:
        """Run project tests"""
        messages = []
        
        # Detect test framework
        test_commands = []
        
        if Path('package.json').exists():
            # Node.js project
            test_commands.append(['npm', 'test'])
        
        if Path('requirements.txt').exists() or Path('setup.py').exists():
            # Python project
            if Path('pytest.ini').exists() or Path('setup.cfg').exists():
                test_commands.append(['pytest'])
            elif Path('manage.py').exists():
                test_commands.append(['python', 'manage.py', 'test'])
            else:
                test_commands.append(['python', '-m', 'unittest', 'discover'])
        
        if Path('Cargo.toml').exists():
            # Rust project
            test_commands.append(['cargo', 'test'])
        
        if Path('go.mod').exists():
            # Go project
            test_commands.append(['go', 'test', './...'])
        
        if not test_commands:
            return True, ["No test framework detected, skipping"]
        
        success = True
        for command in test_commands:
            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode != 0:
                    success = False
                    messages.append(f"Tests failed: {' '.join(command)}")
                    if result.stdout:
                        messages.extend(result.stdout.strip().split('\n')[:10])  # First 10 lines
                else:
                    messages.append(f"Tests passed: {' '.join(command)}")
                    
            except subprocess.TimeoutExpired:
                messages.append(f"Test timeout: {' '.join(command)}")
            except FileNotFoundError:
                messages.append(f"Test command not found: {command[0]}")
            except Exception as e:
                messages.append(f"Test error: {str(e)}")
        
        return success, messages
    
    def run_security_check(self, files: List[str]) -> Tuple[bool, List[str]]:
        """Run security scanning"""
        messages = []
        
        scanner_path = self.claude_dir / 'hooks' / 'security_scanner.py'
        if not scanner_path.exists():
            return True, ["Security scanner not found, skipping"]
        
        try:
            result = subprocess.run(
                [sys.executable, str(scanner_path), 'scan-files'] + files,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                messages.append("Security issues detected:")
                if result.stdout:
                    issues = json.loads(result.stdout)
                    for issue in issues.get('issues', [])[:5]:  # First 5 issues
                        messages.append(f"  - {issue}")
                return False, messages
            else:
                messages.append("Security scan passed")
                return True, messages
                
        except subprocess.TimeoutExpired:
            messages.append("Security scan timeout")
        except Exception as e:
            messages.append(f"Security scan error: {str(e)}")
        
        return True, messages
    
    def run_pre_commit_checks(self) -> Tuple[bool, Dict[str, any]]:
        """Run all pre-commit checks"""
        if not self.enabled:
            return True, {'message': 'Git hooks disabled'}
        
        staged_files = self.get_staged_files()
        if not staged_files:
            return True, {'message': 'No staged files'}
        
        results = {
            'total_checks': 0,
            'passed': 0,
            'failed': 0,
            'checks': {}
        }
        
        overall_success = True
        
        # Play audio notification
        self.play_audio('git_commit.wav')
        
        for check_name in self.pre_commit_checks:
            if check_name not in self.checks:
                continue
            
            check_config = self.checks[check_name]
            results['total_checks'] += 1
            
            print(f"Running {check_config['name']}...")
            
            # Run appropriate check
            if check_name == 'lint':
                success, messages = self.run_lint_check(staged_files)
            elif check_name == 'format':
                success, messages = self.run_format_check(staged_files)
            elif check_name == 'test':
                success, messages = self.run_test_check()
            elif check_name == 'security':
                success, messages = self.run_security_check(staged_files)
            else:
                success = True
                messages = [f"Check {check_name} not implemented"]
            
            results['checks'][check_name] = {
                'name': check_config['name'],
                'success': success,
                'messages': messages
            }
            
            if success:
                results['passed'] += 1
                print(f"  [OK] {check_config['name']} passed")
            else:
                results['failed'] += 1
                print(f"  [FAIL] {check_config['name']} failed")
                for msg in messages[:5]:  # Show first 5 messages
                    print(f"    {msg}")
                
                if check_config.get('required', False) and self.block_on_failure:
                    overall_success = False
        
        # Play result audio
        if overall_success:
            self.play_audio('quality_gate_passed.wav')
        else:
            self.play_audio('tests_failed.wav')
        
        return overall_success, results
    
    def install_hooks(self) -> bool:
        """Install git hooks"""
        if not self.hooks_dir:
            print("Not in a git repository")
            return False
        
        # Create pre-commit hook
        pre_commit_hook = self.hooks_dir / 'pre-commit'
        
        hook_content = f"""#!/usr/bin/env python3
# Auto-generated by Claude Code Dev Stack V3.0+

import sys
import subprocess

# Run quality checks
result = subprocess.run(
    [sys.executable, r'{self.claude_dir / "hooks" / "git_quality_hooks.py"}', 'pre-commit'],
    capture_output=False
)

sys.exit(result.returncode)
"""
        
        try:
            with open(pre_commit_hook, 'w') as f:
                f.write(hook_content)
            
            # Make executable on Unix-like systems
            if os.name != 'nt':
                os.chmod(pre_commit_hook, 0o755)
            
            print(f"Installed pre-commit hook at {pre_commit_hook}")
            return True
            
        except Exception as e:
            print(f"Failed to install hook: {e}")
            return False
    
    def uninstall_hooks(self) -> bool:
        """Uninstall git hooks"""
        if not self.hooks_dir:
            print("Not in a git repository")
            return False
        
        pre_commit_hook = self.hooks_dir / 'pre-commit'
        if pre_commit_hook.exists():
            try:
                pre_commit_hook.unlink()
                print("Uninstalled pre-commit hook")
                return True
            except Exception as e:
                print(f"Failed to uninstall hook: {e}")
                return False
        else:
            print("No hooks to uninstall")
            return True
    
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
    hooks = GitQualityHooks()
    
    if len(sys.argv) < 2:
        print("Usage: git_quality_hooks.py <action>")
        print("Actions:")
        print("  install      - Install git hooks")
        print("  uninstall    - Remove git hooks")
        print("  pre-commit   - Run pre-commit checks")
        print("  check        - Check staged files")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == 'install':
        success = hooks.install_hooks()
        sys.exit(0 if success else 1)
    
    elif action == 'uninstall':
        success = hooks.uninstall_hooks()
        sys.exit(0 if success else 1)
    
    elif action == 'pre-commit':
        success, results = hooks.run_pre_commit_checks()
        
        print("\n" + "=" * 60)
        print(f"Pre-commit checks: {'PASSED' if success else 'FAILED'}")
        print(f"Checks run: {results.get('total_checks', 0)}")
        print(f"Passed: {results.get('passed', 0)}")
        print(f"Failed: {results.get('failed', 0)}")
        print("=" * 60)
        
        sys.exit(0 if success else 1)
    
    elif action == 'check':
        staged_files = hooks.get_staged_files()
        if staged_files:
            print(f"Staged files: {len(staged_files)}")
            for f in staged_files:
                print(f"  - {f}")
        else:
            print("No staged files")
        sys.exit(0)
    
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == '__main__':
    main()