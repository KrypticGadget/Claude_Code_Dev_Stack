"""
Statusline Utilities

Utility classes and functions for terminal operations, color handling,
git operations, and cross-platform compatibility.
"""

import os
import sys
import re
import subprocess
import platform
import shutil
from typing import Optional, Dict, Any, Tuple, List
from pathlib import Path


class TerminalUtils:
    """Utilities for terminal operations and compatibility"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.is_windows = self.platform == 'windows'
        self.is_macos = self.platform == 'darwin'
        self.is_linux = self.platform == 'linux'
        
        # Terminal capabilities
        self._color_support = None
        self._unicode_support = None
        self._width = None
        self._height = None
    
    def supports_color(self) -> bool:
        """Check if terminal supports ANSI colors"""
        if self._color_support is not None:
            return self._color_support
        
        # Check environment variables
        if os.getenv('NO_COLOR'):
            self._color_support = False
            return False
        
        if os.getenv('FORCE_COLOR'):
            self._color_support = True
            return True
        
        # Check if we're in a TTY
        if not sys.stdout.isatty():
            self._color_support = False
            return False
        
        # Check TERM environment variable
        term = os.getenv('TERM', '').lower()
        if 'color' in term or term in ['xterm', 'xterm-256color', 'screen', 'tmux']:
            self._color_support = True
            return True
        
        # Windows-specific checks
        if self.is_windows:
            # Windows Terminal and ConEmu support colors
            if os.getenv('WT_SESSION') or os.getenv('ConEmuANSI'):
                self._color_support = True
                return True
            
            # Try to enable ANSI support on Windows 10+
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
                mode = ctypes.c_ulong()
                kernel32.GetConsoleMode(handle, ctypes.byref(mode))
                kernel32.SetConsoleMode(handle, mode.value | 4)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
                self._color_support = True
                return True
            except:
                pass
        
        self._color_support = False
        return False
    
    def supports_unicode(self) -> bool:
        """Check if terminal supports Unicode characters"""
        if self._unicode_support is not None:
            return self._unicode_support
        
        # Check encoding
        encoding = sys.stdout.encoding or 'ascii'
        if 'utf' in encoding.lower():
            self._unicode_support = True
            return True
        
        # Check locale
        import locale
        try:
            loc = locale.getlocale()
            if loc and any('utf' in str(l).lower() for l in loc if l):
                self._unicode_support = True
                return True
        except:
            pass
        
        self._unicode_support = False
        return False
    
    def get_width(self) -> int:
        """Get terminal width"""
        if self._width is not None:
            return self._width
        
        try:
            # Try shutil.get_terminal_size first
            size = shutil.get_terminal_size()
            self._width = size.columns
            return self._width
        except:
            pass
        
        # Fallback methods
        try:
            if self.is_windows:
                import ctypes
                from ctypes import wintypes
                
                handle = ctypes.windll.kernel32.GetStdHandle(-11)
                csbi = ctypes.create_string_buffer(22)
                res = ctypes.windll.kernel32.GetConsoleScreenBufferInfo(handle, csbi)
                if res:
                    (_, _, _, _, _, left, top, right, bottom, _, _) = struct.unpack("hhhhHhhhhhh", csbi.raw)
                    self._width = right - left + 1
                    return self._width
            else:
                # Unix-like systems
                import fcntl
                import termios
                import struct
                
                s = struct.pack('HHHH', 0, 0, 0, 0)
                x = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, s)
                rows, cols = struct.unpack('HHHH', x)[:2]
                self._width = cols
                return self._width
        except:
            pass
        
        # Final fallback
        self._width = int(os.getenv('COLUMNS', 80))
        return self._width
    
    def get_height(self) -> int:
        """Get terminal height"""
        if self._height is not None:
            return self._height
        
        try:
            size = shutil.get_terminal_size()
            self._height = size.lines
            return self._height
        except:
            self._height = int(os.getenv('LINES', 24))
            return self._height
    
    def clear_line(self):
        """Clear current line"""
        if self.supports_color():
            sys.stdout.write('\033[K')
            sys.stdout.flush()
    
    def move_cursor(self, x: int, y: int):
        """Move cursor to position"""
        if self.supports_color():
            sys.stdout.write(f'\033[{y};{x}H')
            sys.stdout.flush()
    
    def save_cursor(self):
        """Save cursor position"""
        if self.supports_color():
            sys.stdout.write('\033[s')
            sys.stdout.flush()
    
    def restore_cursor(self):
        """Restore cursor position"""
        if self.supports_color():
            sys.stdout.write('\033[u')
            sys.stdout.flush()
    
    def get_shell(self) -> str:
        """Get current shell"""
        shell = os.getenv('SHELL', '')
        if shell:
            return os.path.basename(shell)
        
        if self.is_windows:
            return 'cmd' if 'cmd' in os.getenv('COMSPEC', '') else 'powershell'
        
        return 'bash'  # Default fallback


class ColorUtils:
    """Utilities for terminal color handling"""
    
    ANSI_COLORS = {
        'black': '30',
        'red': '31',
        'green': '32',
        'yellow': '33',
        'blue': '34',
        'magenta': '35',
        'cyan': '36',
        'white': '37',
        'gray': '90',
        'lightgray': '37',
        'brightred': '91',
        'brightgreen': '92',
        'brightyellow': '93',
        'brightblue': '94',
        'brightmagenta': '95',
        'brightcyan': '96',
        'brightwhite': '97'
    }
    
    def __init__(self, color_support: bool = True):
        self.color_support = color_support
        self.ansi_escape_pattern = re.compile(r'\x1b\[[0-9;]*m')
    
    def colorize(self, text: str, color: str, bg_color: Optional[str] = None, 
                bold: bool = False, italic: bool = False, underline: bool = False) -> str:
        """
        Apply color and formatting to text
        
        Args:
            text: Text to colorize
            color: Foreground color name or ANSI code
            bg_color: Background color name or ANSI code
            bold: Apply bold formatting
            italic: Apply italic formatting
            underline: Apply underline formatting
            
        Returns:
            Formatted text with ANSI codes (if color support enabled)
        """
        if not self.color_support:
            return text
        
        codes = []
        
        # Foreground color
        if color in self.ANSI_COLORS:
            codes.append(self.ANSI_COLORS[color])
        elif color.isdigit():
            codes.append(f'38;5;{color}')
        elif color != 'none':
            codes.append('37')  # Default to white
        
        # Background color
        if bg_color:
            if bg_color in self.ANSI_COLORS:
                bg_code = str(int(self.ANSI_COLORS[bg_color]) + 10)
                codes.append(bg_code)
            elif bg_color.isdigit():
                codes.append(f'48;5;{bg_color}')
        
        # Formatting
        if bold:
            codes.append('1')
        if italic:
            codes.append('3')
        if underline:
            codes.append('4')
        
        if codes:
            return f'\033[{";".join(codes)}m{text}\033[0m'
        else:
            return text
    
    def strip_ansi(self, text: str) -> str:
        """Remove ANSI escape sequences from text"""
        return self.ansi_escape_pattern.sub('', text)
    
    def get_display_length(self, text: str) -> int:
        """Get display length of text (ignoring ANSI codes)"""
        return len(self.strip_ansi(text))
    
    def truncate(self, text: str, max_length: int, mode: str = 'ellipsis') -> str:
        """
        Truncate text to maximum length
        
        Args:
            text: Text to truncate
            max_length: Maximum display length
            mode: Truncation mode ('ellipsis', 'fade', 'cut')
            
        Returns:
            Truncated text
        """
        display_text = self.strip_ansi(text)
        
        if len(display_text) <= max_length:
            return text
        
        if mode == 'ellipsis':
            if max_length <= 3:
                return display_text[:max_length]
            return display_text[:max_length-3] + '...'
        elif mode == 'fade':
            # Gradually fade the text (requires color support)
            if self.color_support and max_length > 5:
                visible_part = display_text[:max_length-5]
                fade_part = display_text[max_length-5:max_length]
                return visible_part + self.colorize(fade_part, 'gray')
            else:
                return display_text[:max_length]
        else:  # cut
            return display_text[:max_length]
    
    def gradient_text(self, text: str, start_color: str, end_color: str) -> str:
        """Apply gradient coloring to text (simplified implementation)"""
        if not self.color_support or len(text) <= 1:
            return text
        
        # Simple implementation: alternate between start and end colors
        result = ""
        for i, char in enumerate(text):
            color = start_color if i % 2 == 0 else end_color
            result += self.colorize(char, color)
        
        return result


class GitUtils:
    """Utilities for git repository operations"""
    
    def __init__(self):
        self.git_available = self._check_git_availability()
        self._repo_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timeout = 2.0  # 2 seconds
    
    def _check_git_availability(self) -> bool:
        """Check if git is available in PATH"""
        try:
            subprocess.run(['git', '--version'], 
                         capture_output=True, 
                         check=True, 
                         timeout=5)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def is_git_repo(self, path: Optional[str] = None) -> bool:
        """Check if path is inside a git repository"""
        if not self.git_available:
            return False
        
        try:
            cmd = ['git', 'rev-parse', '--git-dir']
            result = subprocess.run(cmd, 
                                  cwd=path, 
                                  capture_output=True, 
                                  check=True, 
                                  timeout=2)
            return result.returncode == 0
        except:
            return False
    
    def get_repo_info(self, path: Optional[str] = None, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get comprehensive git repository information
        
        Args:
            path: Repository path (current dir if None)
            use_cache: Whether to use cached results
            
        Returns:
            Dictionary with repo information
        """
        if not self.git_available:
            return {}
        
        repo_path = path or os.getcwd()
        
        # Check cache
        if use_cache and repo_path in self._repo_cache:
            cache_entry = self._repo_cache[repo_path]
            if (time.time() - cache_entry['timestamp']) < self._cache_timeout:
                return cache_entry['data']
        
        info = {
            'is_repo': False,
            'branch': None,
            'status': 'unknown',
            'ahead': 0,
            'behind': 0,
            'modified': 0,
            'added': 0,
            'deleted': 0,
            'untracked': 0,
            'stashed': 0
        }
        
        try:
            # Check if it's a repo
            if not self.is_git_repo(repo_path):
                return info
            
            info['is_repo'] = True
            
            # Get current branch
            try:
                result = subprocess.run(['git', 'branch', '--show-current'], 
                                      cwd=repo_path, 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=2)
                if result.returncode == 0:
                    info['branch'] = result.stdout.strip() or 'HEAD'
            except:
                pass
            
            # Get status
            try:
                result = subprocess.run(['git', 'status', '--porcelain'], 
                                      cwd=repo_path, 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=2)
                if result.returncode == 0:
                    status_lines = result.stdout.strip().split('\n')
                    for line in status_lines:
                        if not line:
                            continue
                        
                        status_code = line[:2]
                        if 'M' in status_code:
                            info['modified'] += 1
                        if 'A' in status_code:
                            info['added'] += 1
                        if 'D' in status_code:
                            info['deleted'] += 1
                        if '?' in status_code:
                            info['untracked'] += 1
                    
                    # Determine overall status
                    if info['modified'] or info['added'] or info['deleted'] or info['untracked']:
                        info['status'] = 'dirty'
                    else:
                        info['status'] = 'clean'
            except:
                pass
            
            # Get ahead/behind info
            try:
                result = subprocess.run(['git', 'rev-list', '--count', '--left-right', 'HEAD...@{upstream}'], 
                                      cwd=repo_path, 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=2)
                if result.returncode == 0:
                    counts = result.stdout.strip().split('\t')
                    if len(counts) == 2:
                        info['ahead'] = int(counts[0])
                        info['behind'] = int(counts[1])
            except:
                pass
            
            # Get stash count
            try:
                result = subprocess.run(['git', 'stash', 'list'], 
                                      cwd=repo_path, 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=2)
                if result.returncode == 0:
                    info['stashed'] = len([line for line in result.stdout.strip().split('\n') if line])
            except:
                pass
        
        except Exception:
            pass
        
        # Cache the result
        import time
        self._repo_cache[repo_path] = {
            'data': info,
            'timestamp': time.time()
        }
        
        return info
    
    def get_branch_name(self, path: Optional[str] = None) -> Optional[str]:
        """Get current git branch name"""
        info = self.get_repo_info(path)
        return info.get('branch')
    
    def get_status(self, path: Optional[str] = None) -> str:
        """Get git repository status"""
        info = self.get_repo_info(path)
        return info.get('status', 'unknown')
    
    def clear_cache(self):
        """Clear git information cache"""
        self._repo_cache.clear()


class SystemUtils:
    """Utilities for system information"""
    
    def __init__(self):
        self.platform = platform.system().lower()
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except ImportError:
            # Fallback without psutil
            try:
                if self.platform == 'linux' or self.platform == 'darwin':
                    result = subprocess.run(['top', '-l', '1', '-n', '0'], 
                                          capture_output=True, 
                                          text=True, 
                                          timeout=2)
                    # Parse top output (simplified)
                    for line in result.stdout.split('\n'):
                        if 'CPU usage' in line or 'CPU:' in line:
                            # Extract percentage (this is a simplified parser)
                            import re
                            matches = re.findall(r'(\d+\.?\d*)%', line)
                            if matches:
                                return float(matches[0])
                
                return 0.0
            except:
                return 0.0
    
    def get_memory_usage(self) -> Tuple[float, float]:
        """
        Get memory usage information
        
        Returns:
            Tuple of (used_percentage, used_gb)
        """
        try:
            import psutil
            memory = psutil.virtual_memory()
            return memory.percent, memory.used / (1024**3)
        except ImportError:
            return 0.0, 0.0
    
    def get_load_average(self) -> Optional[Tuple[float, float, float]]:
        """Get system load average (Unix only)"""
        try:
            if hasattr(os, 'getloadavg'):
                return os.getloadavg()
        except:
            pass
        return None
    
    def get_disk_usage(self, path: str = '.') -> Tuple[float, float]:
        """
        Get disk usage for path
        
        Returns:
            Tuple of (used_percentage, free_gb)
        """
        try:
            import psutil
            usage = psutil.disk_usage(path)
            used_percent = (usage.used / usage.total) * 100
            free_gb = usage.free / (1024**3)
            return used_percent, free_gb
        except ImportError:
            try:
                stat = os.statvfs(path)
                total = stat.f_blocks * stat.f_frsize
                free = stat.f_available * stat.f_frsize
                used_percent = ((total - free) / total) * 100
                free_gb = free / (1024**3)
                return used_percent, free_gb
            except:
                return 0.0, 0.0


def format_bytes(bytes_value: float) -> str:
    """Format bytes value to human readable string"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            if unit == 'B':
                return f"{int(bytes_value)}{unit}"
            else:
                return f"{bytes_value:.1f}{unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f}PB"


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable string"""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m{secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h{minutes}m"


def truncate_path(path: str, max_length: int) -> str:
    """Truncate filesystem path intelligently"""
    if len(path) <= max_length:
        return path
    
    path_obj = Path(path)
    parts = path_obj.parts
    
    if len(parts) <= 2:
        # Can't truncate much, just cut from end
        return path[:max_length-3] + '...'
    
    # Try to keep first and last parts, truncate middle
    first_part = parts[0]
    last_part = parts[-1]
    
    if len(first_part) + len(last_part) + 5 > max_length:
        # Even first and last are too long
        return path[:max_length-3] + '...'
    
    available = max_length - len(first_part) - len(last_part) - 5  # 5 for separators and ...
    
    # Add middle parts until we run out of space
    middle_parts = []
    for part in parts[1:-1]:
        if len('/'.join(middle_parts)) + len(part) + 1 <= available:
            middle_parts.append(part)
        else:
            break
    
    if middle_parts:
        middle = '/'.join(middle_parts)
        return f"{first_part}/.../{middle}/{last_part}"
    else:
        return f"{first_part}/.../{last_part}"