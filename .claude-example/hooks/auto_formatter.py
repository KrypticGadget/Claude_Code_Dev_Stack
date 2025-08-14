#!/usr/bin/env python3
"""
Auto Formatter Hook - V3.0+ Code Formatting
Automatically formats code on save using appropriate formatters
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class AutoFormatter:
    """Automatically format code files using appropriate formatters"""
    
    def __init__(self):
        self.claude_dir = Path.home() / '.claude'
        self.settings = self.load_settings()
        
        # Get formatter settings
        quality_settings = self.settings.get('v3ExtendedFeatures', {}).get('qualityTools', {})
        self.auto_format = quality_settings.get('autoFormat', True)
        self.format_on_save = quality_settings.get('formatOnSave', True)
        self.fix_on_format = quality_settings.get('fixOnFormat', False)
        
        # Formatters configuration
        self.formatters = {
            '.py': {
                'formatters': ['black', 'isort', 'autopep8'],
                'commands': {
                    'black': ['black', '--quiet', '{file}'],
                    'isort': ['isort', '--quiet', '{file}'],
                    'autopep8': ['autopep8', '--in-place', '{file}']
                },
                'check_commands': {
                    'black': ['black', '--check', '{file}'],
                    'isort': ['isort', '--check-only', '{file}']
                }
            },
            '.js': {
                'formatters': ['prettier', 'eslint'],
                'commands': {
                    'prettier': ['prettier', '--write', '{file}'],
                    'eslint': ['eslint', '--fix', '{file}']
                },
                'check_commands': {
                    'prettier': ['prettier', '--check', '{file}'],
                    'eslint': ['eslint', '{file}']
                }
            },
            '.jsx': {
                'formatters': ['prettier', 'eslint'],
                'commands': {
                    'prettier': ['prettier', '--write', '{file}'],
                    'eslint': ['eslint', '--fix', '{file}']
                },
                'check_commands': {
                    'prettier': ['prettier', '--check', '{file}'],
                    'eslint': ['eslint', '{file}']
                }
            },
            '.ts': {
                'formatters': ['prettier', 'tslint'],
                'commands': {
                    'prettier': ['prettier', '--write', '{file}'],
                    'tslint': ['tslint', '--fix', '{file}']
                },
                'check_commands': {
                    'prettier': ['prettier', '--check', '{file}'],
                    'tslint': ['tslint', '{file}']
                }
            },
            '.tsx': {
                'formatters': ['prettier', 'tslint'],
                'commands': {
                    'prettier': ['prettier', '--write', '{file}'],
                    'tslint': ['tslint', '--fix', '{file}']
                },
                'check_commands': {
                    'prettier': ['prettier', '--check', '{file}'],
                    'tslint': ['tslint', '{file}']
                }
            },
            '.go': {
                'formatters': ['gofmt', 'goimports'],
                'commands': {
                    'gofmt': ['gofmt', '-w', '{file}'],
                    'goimports': ['goimports', '-w', '{file}']
                },
                'check_commands': {
                    'gofmt': ['gofmt', '-l', '{file}'],
                    'goimports': ['goimports', '-l', '{file}']
                }
            },
            '.rs': {
                'formatters': ['rustfmt'],
                'commands': {
                    'rustfmt': ['rustfmt', '{file}']
                },
                'check_commands': {
                    'rustfmt': ['rustfmt', '--check', '{file}']
                }
            },
            '.java': {
                'formatters': ['google-java-format'],
                'commands': {
                    'google-java-format': ['google-java-format', '--replace', '{file}']
                },
                'check_commands': {
                    'google-java-format': ['google-java-format', '--dry-run', '{file}']
                }
            },
            '.rb': {
                'formatters': ['rubocop'],
                'commands': {
                    'rubocop': ['rubocop', '--auto-correct', '{file}']
                },
                'check_commands': {
                    'rubocop': ['rubocop', '--format', 'json', '{file}']
                }
            },
            '.php': {
                'formatters': ['php-cs-fixer'],
                'commands': {
                    'php-cs-fixer': ['php-cs-fixer', 'fix', '{file}']
                },
                'check_commands': {
                    'php-cs-fixer': ['php-cs-fixer', 'fix', '--dry-run', '{file}']
                }
            },
            '.cpp': {
                'formatters': ['clang-format'],
                'commands': {
                    'clang-format': ['clang-format', '-i', '{file}']
                },
                'check_commands': {
                    'clang-format': ['clang-format', '--dry-run', '{file}']
                }
            },
            '.c': {
                'formatters': ['clang-format'],
                'commands': {
                    'clang-format': ['clang-format', '-i', '{file}']
                },
                'check_commands': {
                    'clang-format': ['clang-format', '--dry-run', '{file}']
                }
            },
            '.h': {
                'formatters': ['clang-format'],
                'commands': {
                    'clang-format': ['clang-format', '-i', '{file}']
                },
                'check_commands': {
                    'clang-format': ['clang-format', '--dry-run', '{file}']
                }
            },
            '.hpp': {
                'formatters': ['clang-format'],
                'commands': {
                    'clang-format': ['clang-format', '-i', '{file}']
                },
                'check_commands': {
                    'clang-format': ['clang-format', '--dry-run', '{file}']
                }
            },
            '.json': {
                'formatters': ['prettier'],
                'commands': {
                    'prettier': ['prettier', '--write', '{file}']
                },
                'check_commands': {
                    'prettier': ['prettier', '--check', '{file}']
                }
            },
            '.yaml': {
                'formatters': ['prettier'],
                'commands': {
                    'prettier': ['prettier', '--write', '{file}']
                },
                'check_commands': {
                    'prettier': ['prettier', '--check', '{file}']
                }
            },
            '.yml': {
                'formatters': ['prettier'],
                'commands': {
                    'prettier': ['prettier', '--write', '{file}']
                },
                'check_commands': {
                    'prettier': ['prettier', '--check', '{file}']
                }
            },
            '.md': {
                'formatters': ['prettier'],
                'commands': {
                    'prettier': ['prettier', '--write', '--prose-wrap', 'always', '{file}']
                },
                'check_commands': {
                    'prettier': ['prettier', '--check', '{file}']
                }
            },
            '.css': {
                'formatters': ['prettier'],
                'commands': {
                    'prettier': ['prettier', '--write', '{file}']
                },
                'check_commands': {
                    'prettier': ['prettier', '--check', '{file}']
                }
            },
            '.scss': {
                'formatters': ['prettier'],
                'commands': {
                    'prettier': ['prettier', '--write', '{file}']
                },
                'check_commands': {
                    'prettier': ['prettier', '--check', '{file}']
                }
            },
            '.html': {
                'formatters': ['prettier'],
                'commands': {
                    'prettier': ['prettier', '--write', '{file}']
                },
                'check_commands': {
                    'prettier': ['prettier', '--check', '{file}']
                }
            }
        }
        
        # Track formatting stats
        self.stats = {
            'files_formatted': 0,
            'files_checked': 0,
            'formatters_run': 0,
            'errors': 0
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
    
    def check_formatter_installed(self, formatter: str) -> bool:
        """Check if a formatter is installed"""
        try:
            result = subprocess.run(
                ['which', formatter] if os.name != 'nt' else ['where', formatter],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def format_file(self, file_path: str, check_only: bool = False) -> Tuple[bool, List[str]]:
        """Format a single file"""
        file_path = Path(file_path)
        if not file_path.exists():
            return False, [f"File not found: {file_path}"]
        
        ext = file_path.suffix.lower()
        if ext not in self.formatters:
            return True, [f"No formatter configured for {ext} files"]
        
        config = self.formatters[ext]
        results = []
        success = True
        
        for formatter_name in config['formatters']:
            # Check if formatter is installed
            if not self.check_formatter_installed(formatter_name):
                results.append(f"Formatter {formatter_name} not installed")
                continue
            
            # Get appropriate command
            if check_only and formatter_name in config.get('check_commands', {}):
                command = config['check_commands'][formatter_name]
            else:
                command = config['commands'][formatter_name]
            
            # Replace placeholder with actual file path
            command = [arg.replace('{file}', str(file_path)) for arg in command]
            
            try:
                # Run formatter
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                self.stats['formatters_run'] += 1
                
                if result.returncode == 0:
                    if check_only:
                        results.append(f"[OK] {formatter_name}: No changes needed")
                    else:
                        results.append(f"[OK] {formatter_name}: Formatted successfully")
                else:
                    success = False
                    if result.stderr:
                        results.append(f"[WARN] {formatter_name}: {result.stderr.strip()}")
                    elif result.stdout:
                        results.append(f"[WARN] {formatter_name}: {result.stdout.strip()}")
                    else:
                        results.append(f"[WARN] {formatter_name}: Non-zero exit code")
                    
            except subprocess.TimeoutExpired:
                success = False
                results.append(f"[ERROR] {formatter_name}: Timeout")
                self.stats['errors'] += 1
            except Exception as e:
                success = False
                results.append(f"[ERROR] {formatter_name}: {str(e)}")
                self.stats['errors'] += 1
        
        if check_only:
            self.stats['files_checked'] += 1
        else:
            self.stats['files_formatted'] += 1
        
        return success, results
    
    def format_directory(self, directory: str, extensions: List[str] = None, check_only: bool = False) -> Dict:
        """Format all files in a directory"""
        directory = Path(directory)
        if not directory.exists():
            return {'success': False, 'message': f"Directory not found: {directory}"}
        
        # Get all files to format
        files_to_format = []
        if extensions:
            for ext in extensions:
                files_to_format.extend(directory.rglob(f"*{ext}"))
        else:
            # Format all supported extensions
            for ext in self.formatters.keys():
                files_to_format.extend(directory.rglob(f"*{ext}"))
        
        # Exclude common directories
        exclude_dirs = {'node_modules', '.git', '__pycache__', 'venv', '.venv', 'dist', 'build'}
        files_to_format = [f for f in files_to_format 
                          if not any(exc in f.parts for exc in exclude_dirs)]
        
        results = {
            'total_files': len(files_to_format),
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'files': {}
        }
        
        # Trigger audio notification
        self.play_audio('formatting_code.wav')
        
        for file_path in files_to_format:
            success, messages = self.format_file(str(file_path), check_only)
            
            if success and len(messages) == 1 and "No formatter configured" in messages[0]:
                results['skipped'] += 1
            elif success:
                results['successful'] += 1
            else:
                results['failed'] += 1
            
            results['files'][str(file_path)] = {
                'success': success,
                'messages': messages
            }
        
        return results
    
    def format_on_save_hook(self, file_path: str) -> bool:
        """Hook called when a file is saved"""
        if not self.format_on_save:
            return True
        
        success, messages = self.format_file(file_path)
        
        if not success:
            print(f"Formatting issues for {file_path}:")
            for msg in messages:
                print(f"  {msg}")
        
        return success
    
    def play_audio(self, filename: str):
        """Play audio notification"""
        try:
            audio_path = self.claude_dir / 'audio' / filename
            if audio_path.exists():
                import winsound
                winsound.PlaySound(str(audio_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
        except:
            pass
    
    def get_stats(self) -> Dict:
        """Get formatting statistics"""
        return self.stats
    
    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            'files_formatted': 0,
            'files_checked': 0,
            'formatters_run': 0,
            'errors': 0
        }

def main():
    """Hook entry point"""
    formatter = AutoFormatter()
    
    if len(sys.argv) < 2:
        print("Usage: auto_formatter.py <action> [args]")
        print("Actions:")
        print("  format <file>     - Format a single file")
        print("  check <file>      - Check if file needs formatting")
        print("  directory <path>  - Format all files in directory")
        print("  on-save <file>    - Format on save hook")
        print("  stats             - Show formatting statistics")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == 'format' and len(sys.argv) > 2:
        file_path = sys.argv[2]
        success, messages = formatter.format_file(file_path)
        for msg in messages:
            print(msg)
        sys.exit(0 if success else 1)
    
    elif action == 'check' and len(sys.argv) > 2:
        file_path = sys.argv[2]
        success, messages = formatter.format_file(file_path, check_only=True)
        for msg in messages:
            print(msg)
        sys.exit(0 if success else 1)
    
    elif action == 'directory' and len(sys.argv) > 2:
        directory = sys.argv[2]
        results = formatter.format_directory(directory)
        print(json.dumps(results, indent=2))
        sys.exit(0 if results.get('failed', 0) == 0 else 1)
    
    elif action == 'on-save' and len(sys.argv) > 2:
        file_path = sys.argv[2]
        success = formatter.format_on_save_hook(file_path)
        sys.exit(0 if success else 1)
    
    elif action == 'stats':
        print(json.dumps(formatter.get_stats(), indent=2))
        sys.exit(0)
    
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == '__main__':
    main()