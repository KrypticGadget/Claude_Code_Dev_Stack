#!/usr/bin/env python3
"""
Base Hook Module - Shared utilities for all Claude Code hooks
Provides cross-platform path handling, logging, and common utilities
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import platform
import re


class HookEnvironment:
    """Manages Claude Code environment variables and paths"""
    
    def __init__(self):
        # Core environment variables with fallbacks
        self.claude_home = Path(os.environ.get('CLAUDE_HOME', self._default_claude_home()))
        self.project_dir = Path(os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd()))
        self.python_executable = os.environ.get('CLAUDE_PYTHON', sys.executable)
        
        # Ensure directories exist
        self.logs_dir = self.claude_home / 'logs'
        self.config_dir = self.claude_home / 'config'
        self.cache_dir = self.claude_home / 'cache'
        self.hooks_dir = self.claude_home / 'hooks'
        
        for directory in [self.logs_dir, self.config_dir, self.cache_dir, self.hooks_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _default_claude_home(self) -> str:
        """Get default Claude home directory based on OS"""
        system = platform.system()
        
        if system == 'Windows':
            return os.path.join(os.environ.get('APPDATA', ''), 'Claude')
        elif system == 'Darwin':  # macOS
            return os.path.expanduser('~/Library/Application Support/Claude')
        else:  # Linux/WSL
            return os.path.expanduser('~/.claude')
    
    def normalize_path(self, path: Union[str, Path]) -> Path:
        """Normalize path for cross-platform compatibility"""
        path = Path(path)
        
        # Handle WSL paths
        if self._is_wsl() and str(path).startswith('/mnt/'):
            # Already in WSL format
            return path
        
        # Resolve and normalize
        try:
            return path.resolve()
        except Exception:
            # If resolve fails, just return the path as-is
            return path
    
    def _is_wsl(self) -> bool:
        """Check if running in WSL"""
        try:
            with open('/proc/version', 'r') as f:
                return 'microsoft' in f.read().lower()
        except:
            return False


class HookLogger:
    """Centralized logging for all hooks"""
    
    def __init__(self, hook_name: str, env: HookEnvironment):
        self.hook_name = hook_name
        self.env = env
        
        # Create logger
        self.logger = logging.getLogger(f'claude_hook.{hook_name}')
        self.logger.setLevel(logging.DEBUG)
        
        # File handler with rotation
        log_file = self.env.logs_dir / f'{hook_name}_{datetime.now().strftime("%Y%m%d")}.log'
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler for errors only
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def debug(self, message: str, **kwargs):
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        self.logger.error(message, extra=kwargs)
    
    def exception(self, message: str, **kwargs):
        self.logger.exception(message, extra=kwargs)


class ConfigManager:
    """Manages hook configuration files"""
    
    def __init__(self, env: HookEnvironment):
        self.env = env
        self.global_config_file = self.env.config_dir / 'hooks.json'
        self.project_config_file = self.env.project_dir / '.claude' / 'hooks.json'
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration with project overrides"""
        config = {}
        
        # Load global config
        if self.global_config_file.exists():
            try:
                with open(self.global_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except Exception:
                pass
        
        # Override with project config
        if self.project_config_file.exists():
            try:
                with open(self.project_config_file, 'r', encoding='utf-8') as f:
                    project_config = json.load(f)
                    config.update(project_config)
            except Exception:
                pass
        
        return config
    
    def save_config(self, config: Dict[str, Any], project_level: bool = False):
        """Save configuration"""
        config_file = self.project_config_file if project_level else self.global_config_file
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)


class ProcessRunner:
    """Safe process execution with timeout and error handling"""
    
    def __init__(self, logger: HookLogger):
        self.logger = logger
    
    def run(self, command: List[str], cwd: Optional[Path] = None, 
            timeout: int = 30, capture_output: bool = True) -> subprocess.CompletedProcess:
        """Run a command safely"""
        try:
            # Ensure strings in command list
            command = [str(c) for c in command]
            
            # Handle paths with spaces
            if platform.system() == 'Windows':
                # Windows needs special handling for paths with spaces
                command = [f'"{c}"' if ' ' in c and os.path.exists(c) else c for c in command]
            
            self.logger.debug(f"Running command: {' '.join(command)}")
            
            result = subprocess.run(
                command,
                cwd=cwd,
                timeout=timeout,
                capture_output=capture_output,
                text=True,
                shell=(platform.system() == 'Windows')
            )
            
            if result.returncode != 0:
                self.logger.warning(f"Command failed with code {result.returncode}: {result.stderr}")
            
            return result
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timed out after {timeout} seconds")
            raise
        except Exception as e:
            self.logger.exception(f"Error running command: {e}")
            raise


class HookContext:
    """Context information available to all hooks"""
    
    def __init__(self, env: HookEnvironment):
        self.env = env
        self.timestamp = datetime.now()
        self.session_id = os.environ.get('CLAUDE_SESSION_ID', 'unknown')
        self.user = os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))
        self.hook_phase = os.environ.get('CLAUDE_HOOK_PHASE', 'unknown')
        
        # Load additional context from environment
        self.context_data = {}
        for key, value in os.environ.items():
            if key.startswith('CLAUDE_CONTEXT_'):
                self.context_data[key[15:].lower()] = value


class BaseHook:
    """Base class for all hooks"""
    
    def __init__(self, name: str):
        self.name = name
        self.env = HookEnvironment()
        self.logger = HookLogger(name, self.env)
        self.config_manager = ConfigManager(self.env)
        self.process_runner = ProcessRunner(self.logger)
        self.context = HookContext(self.env)
        
        # Load configuration
        self.config = self.config_manager.load_config()
        
        # Log initialization
        self.logger.info(f"Initialized {name} hook", 
                        project_dir=str(self.env.project_dir),
                        claude_home=str(self.env.claude_home))
    
    def run(self) -> int:
        """Main hook execution - override in subclasses"""
        raise NotImplementedError("Subclasses must implement run()")
    
    def safe_run(self) -> int:
        """Safe wrapper for hook execution"""
        try:
            self.logger.info(f"Starting {self.name} hook")
            result = self.run()
            self.logger.info(f"Completed {self.name} hook successfully")
            return result
        except Exception as e:
            self.logger.exception(f"Hook {self.name} failed: {e}")
            # Return 0 to not block Claude Code operations
            return 0
    
    def read_stdin(self) -> str:
        """Read input from stdin if available"""
        if not sys.stdin.isatty():
            return sys.stdin.read()
        return ""
    
    def write_stdout(self, data: str):
        """Write output to stdout"""
        sys.stdout.write(data)
        sys.stdout.flush()
    
    def get_cache_file(self, name: str) -> Path:
        """Get a cache file path"""
        return self.env.cache_dir / f"{self.name}_{name}.json"
    
    def load_cache(self, name: str) -> Optional[Dict[str, Any]]:
        """Load data from cache"""
        cache_file = self.get_cache_file(name)
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load cache {name}: {e}")
        return None
    
    def save_cache(self, name: str, data: Dict[str, Any]):
        """Save data to cache"""
        cache_file = self.get_cache_file(name)
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save cache {name}: {e}")


# Utility functions for hooks
def sanitize_path(path: str) -> str:
    """Sanitize path for safe usage"""
    # Remove potentially dangerous characters
    path = re.sub(r'[<>:"|?*]', '_', path)
    # Handle Unicode properly
    return path.encode('utf-8', 'ignore').decode('utf-8')


def parse_json_safely(text: str) -> Optional[Dict[str, Any]]:
    """Safely parse JSON from text"""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract JSON from text
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
    return None


def format_size(bytes: int) -> str:
    """Format byte size as human readable"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} PB"


if __name__ == "__main__":
    # Test the base hook functionality
    class TestHook(BaseHook):
        def run(self):
            self.logger.info("Test hook running")
            return 0
    
    hook = TestHook("test")
    sys.exit(hook.safe_run())