#!/usr/bin/env python3
"""
Code Linter Hook - V3.0+ Quality Tool
Multi-language linting support with auto-formatting
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class CodeLinter:
    """Multi-language code linting and quality checks"""
    
    def __init__(self):
        self.linters = {
            '.py': {
                'linters': ['flake8', 'mypy', 'pylint'],
                'formatter': 'black',
                'import_sorter': 'isort',
                'security': 'bandit'
            },
            '.js': {
                'linters': ['eslint'],
                'formatter': 'prettier',
                'security': 'eslint-plugin-security'
            },
            '.jsx': {
                'linters': ['eslint'],
                'formatter': 'prettier'
            },
            '.ts': {
                'linters': ['tslint', 'eslint'],
                'formatter': 'prettier'
            },
            '.tsx': {
                'linters': ['tslint', 'eslint'],
                'formatter': 'prettier'
            },
            '.go': {
                'linters': ['golint', 'go vet'],
                'formatter': 'gofmt'
            },
            '.rs': {
                'linters': ['clippy'],
                'formatter': 'rustfmt'
            },
            '.java': {
                'linters': ['checkstyle'],
                'formatter': 'google-java-format'
            },
            '.cpp': {
                'linters': ['cpplint'],
                'formatter': 'clang-format'
            },
            '.c': {
                'linters': ['cpplint'],
                'formatter': 'clang-format'
            },
            '.rb': {
                'linters': ['rubocop'],
                'formatter': 'rubocop'
            },
            '.php': {
                'linters': ['phpcs'],
                'formatter': 'php-cs-fixer'
            }
        }
        
        # Load settings
        self.settings = self.load_settings()
        self.enabled = self.settings.get('v3ExtendedFeatures', {}).get('qualityTools', {}).get('enabled', True)
        self.auto_format = self.settings.get('v3ExtendedFeatures', {}).get('qualityTools', {}).get('autoFormat', True)
        self.lint_on_save = self.settings.get('v3ExtendedFeatures', {}).get('qualityTools', {}).get('lintOnSave', True)
        
        # Audio notifications
        self.audio_events = {
            'linting_started': 'linting_started.wav',
            'linting_complete': 'linting_complete.wav',
            'linting_issues': 'linting_issues.wav',
            'formatting_code': 'formatting_code.wav'
        }
    
    def load_settings(self) -> Dict:
        """Load settings from settings.json"""
        settings_path = Path.home() / '.claude' / 'settings.json'
        if settings_path.exists():
            try:
                with open(settings_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def play_audio(self, event: str):
        """Play audio notification"""
        audio_file = self.audio_events.get(event)
        if audio_file:
            audio_path = Path.home() / '.claude' / 'audio' / audio_file
            if audio_path.exists():
                try:
                    import winsound
                    winsound.PlaySound(str(audio_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
                except:
                    pass
    
    def pre_write_hook(self, file_path: str, content: str) -> Tuple[str, List[str]]:
        """Run before writing file - format code"""
        if not self.enabled or not self.auto_format:
            return content, []
        
        ext = Path(file_path).suffix
        if ext not in self.linters:
            return content, []
        
        self.play_audio('formatting_code')
        
        # Format the content
        formatter = self.linters[ext].get('formatter')
        if formatter:
            formatted_content = self.format_code(content, formatter, ext)
            if formatted_content:
                return formatted_content, ["Code auto-formatted"]
        
        return content, []
    
    def post_write_hook(self, file_path: str) -> Tuple[bool, List[str]]:
        """Run after writing file - lint check"""
        if not self.enabled or not self.lint_on_save:
            return True, []
        
        ext = Path(file_path).suffix
        if ext not in self.linters:
            return True, []
        
        self.play_audio('linting_started')
        
        issues = []
        linter_config = self.linters[ext]
        
        # Run linters
        for linter in linter_config.get('linters', []):
            lint_issues = self.run_linter(file_path, linter)
            issues.extend(lint_issues)
        
        # Run security checks
        if 'security' in linter_config:
            security_issues = self.run_security_check(file_path, linter_config['security'])
            issues.extend(security_issues)
        
        if issues:
            self.play_audio('linting_issues')
            return False, issues
        else:
            self.play_audio('linting_complete')
            return True, ["All quality checks passed"]
    
    def format_code(self, content: str, formatter: str, ext: str) -> Optional[str]:
        """Format code using specified formatter"""
        try:
            # Create temp file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False) as tf:
                tf.write(content)
                temp_path = tf.name
            
            # Run formatter
            if formatter == 'black':
                subprocess.run(['black', '--quiet', temp_path], capture_output=True)
            elif formatter == 'prettier':
                subprocess.run(['prettier', '--write', temp_path], capture_output=True)
            elif formatter == 'gofmt':
                subprocess.run(['gofmt', '-w', temp_path], capture_output=True)
            elif formatter == 'rustfmt':
                subprocess.run(['rustfmt', temp_path], capture_output=True)
            elif formatter == 'clang-format':
                subprocess.run(['clang-format', '-i', temp_path], capture_output=True)
            
            # Read formatted content
            with open(temp_path, 'r') as f:
                formatted = f.read()
            
            # Cleanup
            os.unlink(temp_path)
            return formatted
            
        except Exception as e:
            print(f"Formatting error: {e}")
            return None
    
    def run_linter(self, file_path: str, linter: str) -> List[str]:
        """Run a specific linter on file"""
        issues = []
        try:
            if linter == 'flake8':
                result = subprocess.run(['flake8', file_path], capture_output=True, text=True)
                if result.stdout:
                    issues.extend(result.stdout.strip().split('\n'))
            
            elif linter == 'mypy':
                result = subprocess.run(['mypy', file_path], capture_output=True, text=True)
                if result.stdout:
                    issues.extend(result.stdout.strip().split('\n'))
            
            elif linter == 'eslint':
                result = subprocess.run(['eslint', file_path, '--format', 'compact'], 
                                      capture_output=True, text=True)
                if result.stdout:
                    issues.extend(result.stdout.strip().split('\n'))
            
            elif linter == 'pylint':
                result = subprocess.run(['pylint', file_path, '--output-format=parseable'], 
                                      capture_output=True, text=True)
                if result.stdout:
                    # Filter out score line
                    for line in result.stdout.strip().split('\n'):
                        if not line.startswith('Your code has been rated'):
                            issues.append(line)
                            
        except FileNotFoundError:
            # Linter not installed
            pass
        except Exception as e:
            issues.append(f"Linter error ({linter}): {e}")
        
        return [issue for issue in issues if issue]  # Filter empty lines
    
    def run_security_check(self, file_path: str, scanner: str) -> List[str]:
        """Run security scanner on file"""
        issues = []
        try:
            if scanner == 'bandit':
                result = subprocess.run(['bandit', '-f', 'csv', file_path], 
                                      capture_output=True, text=True)
                if result.stdout:
                    # Parse CSV output
                    lines = result.stdout.strip().split('\n')[1:]  # Skip header
                    for line in lines:
                        if line:
                            issues.append(f"Security: {line}")
                            
        except FileNotFoundError:
            # Scanner not installed
            pass
        except Exception as e:
            issues.append(f"Security scan error: {e}")
        
        return issues
    
    def lint_project(self, project_path: str) -> Dict[str, List[str]]:
        """Lint entire project"""
        all_issues = {}
        
        for ext, config in self.linters.items():
            # Find all files with this extension
            files = list(Path(project_path).rglob(f'*{ext}'))
            
            for file_path in files:
                # Skip node_modules, venv, etc
                if any(part in str(file_path).lower() for part in 
                       ['node_modules', 'venv', '.git', '__pycache__', 'dist', 'build']):
                    continue
                
                success, issues = self.post_write_hook(str(file_path))
                if not success:
                    all_issues[str(file_path)] = issues
        
        return all_issues

def main():
    """Hook entry point"""
    import sys
    
    linter = CodeLinter()
    
    if len(sys.argv) > 2:
        action = sys.argv[1]
        file_path = sys.argv[2]
        
        if action == 'pre-write':
            # Read content from stdin
            content = sys.stdin.read()
            formatted, messages = linter.pre_write_hook(file_path, content)
            print(formatted, end='')
            if messages:
                print(f"# Linter: {'; '.join(messages)}", file=sys.stderr)
        
        elif action == 'post-write':
            success, issues = linter.post_write_hook(file_path)
            if not success:
                print(f"Linting issues found:", file=sys.stderr)
                for issue in issues:
                    print(f"  - {issue}", file=sys.stderr)
                sys.exit(1)
    
    elif len(sys.argv) > 1 and sys.argv[1] == 'project':
        # Lint entire project
        project_path = sys.argv[2] if len(sys.argv) > 2 else '.'
        all_issues = linter.lint_project(project_path)
        
        if all_issues:
            print(f"Found issues in {len(all_issues)} files:")
            for file_path, issues in all_issues.items():
                print(f"\n{file_path}:")
                for issue in issues:
                    print(f"  - {issue}")
            sys.exit(1)
        else:
            print("All files pass quality checks!")

if __name__ == '__main__':
    main()