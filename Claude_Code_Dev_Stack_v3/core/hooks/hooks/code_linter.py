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
        quality_tools = self.settings.get('v3ExtendedFeatures', {}).get('qualityTools', {})
        self.enabled = quality_tools.get('enabled', True)
        self.auto_format = quality_tools.get('autoFormat', True)
        self.lint_on_save = quality_tools.get('lintOnSave', True)
        
        # New strictness configuration
        self.strictness_level = quality_tools.get('strictness', 'warning')  # 'strict', 'warning', 'suggestion'
        self.block_on_errors = quality_tools.get('blockOnErrors', False)  # Only block on actual errors
        self.block_on_warnings = quality_tools.get('blockOnWarnings', False)  # Block on warnings too
        self.show_suggestions = quality_tools.get('showSuggestions', True)  # Show style suggestions
        
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
        
        # Categorize issues by severity
        categorized_issues = self.categorize_issues(issues)
        
        # Determine if we should block based on strictness settings
        should_block = self.should_block_commit(categorized_issues)
        
        # Format messages based on strictness level
        formatted_messages = self.format_issue_messages(categorized_issues)
        
        if should_block:
            self.play_audio('linting_issues')
            return False, formatted_messages
        else:
            if categorized_issues['errors'] or categorized_issues['warnings'] or categorized_issues['suggestions']:
                self.play_audio('linting_issues')
                return True, formatted_messages  # Allow commit but show issues
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
    
    def categorize_issues(self, issues: List[str]) -> Dict[str, List[str]]:
        """Categorize issues by severity level"""
        categorized = {
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        for issue in issues:
            issue_lower = issue.lower()
            
            # Categorize as error
            if any(keyword in issue_lower for keyword in [
                'syntaxerror', 'nameerror', 'typeerror', 'importerror', 
                'error:', 'critical:', 'security:', 'undefined variable',
                'cannot import', 'fatal'
            ]):
                categorized['errors'].append(issue)
            
            # Categorize as warning
            elif any(keyword in issue_lower for keyword in [
                'warning:', 'warn:', 'deprecated', 'unused', 'unreachable',
                'missing docstring', 'line too long', 'too many arguments',
                'redefined', 'shadowed'
            ]):
                categorized['warnings'].append(issue)
            
            # Everything else as suggestion
            else:
                categorized['suggestions'].append(issue)
        
        return categorized
    
    def should_block_commit(self, categorized_issues: Dict[str, List[str]]) -> bool:
        """Determine if commit should be blocked based on strictness settings"""
        if self.strictness_level == 'strict':
            # Block on any issue
            return bool(categorized_issues['errors'] or categorized_issues['warnings'] or categorized_issues['suggestions'])
        
        elif self.strictness_level == 'warning':
            # Block only on errors, or if specifically configured to block on warnings
            return bool(categorized_issues['errors']) or (self.block_on_warnings and categorized_issues['warnings'])
        
        elif self.strictness_level == 'suggestion':
            # Only block on errors if explicitly configured
            return self.block_on_errors and bool(categorized_issues['errors'])
        
        else:
            # Default: don't block but show issues
            return False
    
    def format_issue_messages(self, categorized_issues: Dict[str, List[str]]) -> List[str]:
        """Format issue messages based on strictness level and settings"""
        messages = []
        
        if categorized_issues['errors']:
            messages.append(f"[ERROR] ERRORS ({len(categorized_issues['errors'])}):")
            for error in categorized_issues['errors'][:5]:  # Limit to first 5
                messages.append(f"  [!] {error}")
        
        if categorized_issues['warnings'] and (self.strictness_level in ['strict', 'warning'] or self.show_suggestions):
            messages.append(f"[WARN] WARNINGS ({len(categorized_issues['warnings'])}):")
            for warning in categorized_issues['warnings'][:5]:  # Limit to first 5
                messages.append(f"  [*] {warning}")
        
        if categorized_issues['suggestions'] and self.show_suggestions and self.strictness_level != 'suggestion':
            messages.append(f"[INFO] SUGGESTIONS ({len(categorized_issues['suggestions'])}):")
            for suggestion in categorized_issues['suggestions'][:3]:  # Limit to first 3
                messages.append(f"  [+] {suggestion}")
        
        # Add summary message
        if messages:
            total_issues = len(categorized_issues['errors']) + len(categorized_issues['warnings']) + len(categorized_issues['suggestions'])
            messages.insert(0, f"Code quality analysis found {total_issues} issues (Strictness: {self.strictness_level})")
        
        return messages
    
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
            # Print issues to stderr for git hooks to process
            if issues:
                for issue in issues:
                    print(issue, file=sys.stderr)
            
            # Exit with appropriate code based on success
            sys.exit(0 if success else 1)
    
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