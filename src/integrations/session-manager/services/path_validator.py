"""
Path Validation Service
======================

Advanced path validation and permission checking for Claude Code sessions.
Ensures secure and reliable path handling across different operating systems.
"""

import os
import stat
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import platform

import sys
sys.path.append(str(Path(__file__).parent.parent))

from models.session_models import PathValidation


class PathValidator:
    """
    Advanced path validation service with comprehensive permission checking,
    security validation, and cross-platform compatibility.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.system = platform.system()
        
        # Security-sensitive paths to avoid
        self.restricted_paths = self._get_restricted_paths()
    
    def _get_restricted_paths(self) -> List[str]:
        """Get list of restricted system paths."""
        if self.system == "Windows":
            return [
                "C:\\Windows\\System32",
                "C:\\Program Files",
                "C:\\Program Files (x86)",
                "C:\\ProgramData",
                "C:\\Users\\Default",
                "C:\\$Recycle.Bin"
            ]
        elif self.system == "Darwin":  # macOS
            return [
                "/System",
                "/Library/System",
                "/usr/bin",
                "/usr/sbin",
                "/bin",
                "/sbin",
                "/private"
            ]
        else:  # Linux and others
            return [
                "/bin",
                "/sbin",
                "/usr/bin",
                "/usr/sbin",
                "/lib",
                "/lib64",
                "/sys",
                "/proc",
                "/dev",
                "/boot"
            ]
    
    def validate_path(self, path: str, create_if_missing: bool = True) -> PathValidation:
        """
        Comprehensive path validation with security checks.
        
        Args:
            path: Path to validate
            create_if_missing: Whether to create the directory if it doesn't exist
            
        Returns:
            PathValidation object with detailed validation results
        """
        path_obj = Path(path).resolve()
        
        validation = PathValidation(
            path=str(path_obj),
            exists=path_obj.exists(),
            readable=False,
            writable=False,
            is_git_repo=False,
            permissions={}
        )
        
        try:
            # Security checks
            self._check_path_security(path_obj, validation)
            
            # Existence and creation
            if not validation.exists and create_if_missing:
                self._create_directory_safely(path_obj, validation)
            
            # Permission checks
            self._check_permissions(path_obj, validation)
            
            # Git repository detection
            self._check_git_repository(path_obj, validation)
            
            # Advanced filesystem checks
            self._check_filesystem_properties(path_obj, validation)
            
        except Exception as e:
            validation.validation_errors.append(f"Validation error: {str(e)}")
            self.logger.error(f"Path validation failed for {path}: {e}")
        
        return validation
    
    def _check_path_security(self, path_obj: Path, validation: PathValidation):
        """Check path for security issues."""
        path_str = str(path_obj)
        
        # Check against restricted paths
        for restricted in self.restricted_paths:
            if path_str.startswith(restricted):
                validation.validation_errors.append(
                    f"Path is in restricted system directory: {restricted}"
                )
        
        # Check for suspicious patterns
        suspicious_patterns = [
            "..",  # Directory traversal
            "~",   # Home directory shortcuts in unexpected places
        ]
        
        for pattern in suspicious_patterns:
            if pattern in path_str:
                validation.validation_errors.append(
                    f"Suspicious path pattern detected: {pattern}"
                )
        
        # Check path length (Windows has 260 char limit by default)
        if self.system == "Windows" and len(path_str) > 250:
            validation.validation_errors.append(
                "Path too long for Windows filesystem"
            )
        
        # Check for invalid characters
        invalid_chars = self._get_invalid_path_chars()
        for char in invalid_chars:
            if char in path_str:
                validation.validation_errors.append(
                    f"Invalid character in path: {char}"
                )
    
    def _get_invalid_path_chars(self) -> List[str]:
        """Get invalid characters for filesystem paths."""
        if self.system == "Windows":
            return ['<', '>', ':', '"', '|', '?', '*']
        else:
            return ['\0']  # Null character is invalid on Unix-like systems
    
    def _create_directory_safely(self, path_obj: Path, validation: PathValidation):
        """Safely create directory with proper error handling."""
        try:
            path_obj.mkdir(parents=True, exist_ok=True)
            validation.exists = True
            self.logger.info(f"Created directory: {path_obj}")
        except PermissionError:
            validation.validation_errors.append("Insufficient permissions to create directory")
        except OSError as e:
            validation.validation_errors.append(f"Failed to create directory: {str(e)}")
    
    def _check_permissions(self, path_obj: Path, validation: PathValidation):
        """Check detailed file system permissions."""
        if not path_obj.exists():
            return
        
        try:
            # Basic permission checks
            validation.readable = os.access(path_obj, os.R_OK)
            validation.writable = os.access(path_obj, os.W_OK)
            executable = os.access(path_obj, os.X_OK)
            
            validation.permissions = {
                'read': validation.readable,
                'write': validation.writable,
                'execute': executable
            }
            
            # Detailed permission analysis
            if self.system != "Windows":
                self._check_unix_permissions(path_obj, validation)
            else:
                self._check_windows_permissions(path_obj, validation)
            
            # Test actual write capability
            if validation.writable:
                self._test_write_capability(path_obj, validation)
                
        except Exception as e:
            validation.validation_errors.append(f"Permission check failed: {str(e)}")
    
    def _check_unix_permissions(self, path_obj: Path, validation: PathValidation):
        """Check Unix-style permissions in detail."""
        try:
            stat_info = path_obj.stat()
            mode = stat_info.st_mode
            
            # Extract permission bits
            owner_perms = {
                'read': bool(mode & stat.S_IRUSR),
                'write': bool(mode & stat.S_IWUSR),
                'execute': bool(mode & stat.S_IXUSR)
            }
            
            group_perms = {
                'read': bool(mode & stat.S_IRGRP),
                'write': bool(mode & stat.S_IWGRP),
                'execute': bool(mode & stat.S_IXGRP)
            }
            
            other_perms = {
                'read': bool(mode & stat.S_IROTH),
                'write': bool(mode & stat.S_IWOTH),
                'execute': bool(mode & stat.S_IXOTH)
            }
            
            validation.permissions.update({
                'owner': owner_perms,
                'group': group_perms,
                'other': other_perms,
                'octal': oct(stat.S_IMODE(mode))
            })
            
        except Exception as e:
            validation.validation_errors.append(f"Unix permission check failed: {str(e)}")
    
    def _check_windows_permissions(self, path_obj: Path, validation: PathValidation):
        """Check Windows-specific permissions."""
        try:
            # Windows permission checking is more complex
            # This is a simplified version
            validation.permissions.update({
                'is_system_file': bool(path_obj.stat().st_file_attributes & stat.FILE_ATTRIBUTE_SYSTEM) if hasattr(stat, 'FILE_ATTRIBUTE_SYSTEM') else False,
                'is_hidden': bool(path_obj.stat().st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN) if hasattr(stat, 'FILE_ATTRIBUTE_HIDDEN') else False,
                'is_readonly': not validation.writable
            })
            
        except Exception as e:
            validation.validation_errors.append(f"Windows permission check failed: {str(e)}")
    
    def _test_write_capability(self, path_obj: Path, validation: PathValidation):
        """Test actual write capability by creating a test file."""
        try:
            test_file = path_obj / ".claude_write_test"
            
            # Write test
            with open(test_file, 'w') as f:
                f.write("test")
            
            # Read test
            with open(test_file, 'r') as f:
                content = f.read()
            
            # Cleanup
            test_file.unlink()
            
            if content != "test":
                validation.validation_errors.append("Write test failed - content mismatch")
                
        except Exception as e:
            validation.validation_errors.append(f"Write capability test failed: {str(e)}")
            validation.writable = False
    
    def _check_git_repository(self, path_obj: Path, validation: PathValidation):
        """Check if path is or contains a git repository."""
        try:
            # Check for .git directory
            git_dir = path_obj / ".git"
            validation.is_git_repo = git_dir.exists() and git_dir.is_dir()
            
            # Additional git checks
            if validation.is_git_repo:
                validation.permissions['git'] = self._check_git_permissions(path_obj)
            
        except Exception as e:
            validation.validation_errors.append(f"Git check failed: {str(e)}")
    
    def _check_git_permissions(self, path_obj: Path) -> Dict[str, bool]:
        """Check git-specific permissions and status."""
        git_perms = {
            'can_read_config': False,
            'can_write_index': False,
            'is_bare_repo': False,
            'has_remote': False
        }
        
        try:
            # Check git config readability
            git_config = path_obj / ".git" / "config"
            git_perms['can_read_config'] = git_config.exists() and os.access(git_config, os.R_OK)
            
            # Check git index writability
            git_index = path_obj / ".git" / "index"
            git_perms['can_write_index'] = (not git_index.exists()) or os.access(git_index, os.W_OK)
            
            # Check if bare repository
            if git_config.exists():
                try:
                    with open(git_config, 'r') as f:
                        config_content = f.read()
                        git_perms['is_bare_repo'] = 'bare = true' in config_content
                except:
                    pass
            
            # Check for remotes using git command if available
            try:
                result = subprocess.run(
                    ['git', 'remote'],
                    cwd=path_obj,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                git_perms['has_remote'] = bool(result.stdout.strip())
            except:
                pass
                
        except Exception as e:
            self.logger.debug(f"Git permission check failed: {e}")
        
        return git_perms
    
    def _check_filesystem_properties(self, path_obj: Path, validation: PathValidation):
        """Check filesystem-specific properties."""
        try:
            if path_obj.exists():
                stat_info = path_obj.stat()
                
                validation.permissions.update({
                    'filesystem_type': self._get_filesystem_type(path_obj),
                    'device_id': stat_info.st_dev,
                    'inode': getattr(stat_info, 'st_ino', None),
                    'size_bytes': stat_info.st_size if path_obj.is_file() else None,
                    'last_modified': stat_info.st_mtime,
                    'last_accessed': stat_info.st_atime,
                })
                
                # Check available space
                self._check_disk_space(path_obj, validation)
                
        except Exception as e:
            validation.validation_errors.append(f"Filesystem check failed: {str(e)}")
    
    def _get_filesystem_type(self, path_obj: Path) -> Optional[str]:
        """Get filesystem type (platform-specific)."""
        try:
            if self.system == "Windows":
                # Windows filesystem detection
                drive = str(path_obj).split(':')[0] + ':'
                result = subprocess.run(
                    ['fsutil', 'fsinfo', 'volumeinfo', drive],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'File System Name' in line:
                            return line.split(':')[1].strip()
            
            elif self.system in ["Linux", "Darwin"]:
                # Unix filesystem detection
                result = subprocess.run(
                    ['df', '-T', str(path_obj)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        return lines[1].split()[1]
                        
        except Exception:
            pass
        
        return None
    
    def _check_disk_space(self, path_obj: Path, validation: PathValidation):
        """Check available disk space."""
        try:
            if self.system == "Windows":
                import ctypes
                free_bytes = ctypes.c_ulonglong(0)
                total_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    str(path_obj),
                    ctypes.pointer(free_bytes),
                    ctypes.pointer(total_bytes),
                    None
                )
                validation.permissions['disk_space'] = {
                    'free_bytes': free_bytes.value,
                    'total_bytes': total_bytes.value,
                    'free_mb': free_bytes.value / (1024 * 1024),
                    'total_mb': total_bytes.value / (1024 * 1024)
                }
            else:
                # Unix-like systems
                statvfs = os.statvfs(path_obj)
                free_bytes = statvfs.f_frsize * statvfs.f_bavail
                total_bytes = statvfs.f_frsize * statvfs.f_blocks
                
                validation.permissions['disk_space'] = {
                    'free_bytes': free_bytes,
                    'total_bytes': total_bytes,
                    'free_mb': free_bytes / (1024 * 1024),
                    'total_mb': total_bytes / (1024 * 1024)
                }
                
            # Warn if low on space (less than 100MB)
            free_mb = validation.permissions['disk_space']['free_mb']
            if free_mb < 100:
                validation.validation_errors.append(
                    f"Low disk space: {free_mb:.1f}MB available"
                )
                
        except Exception as e:
            validation.validation_errors.append(f"Disk space check failed: {str(e)}")
    
    def validate_multiple_paths(self, paths: List[str]) -> Dict[str, PathValidation]:
        """Validate multiple paths in batch."""
        results = {}
        for path in paths:
            try:
                results[path] = self.validate_path(path)
            except Exception as e:
                # Create error validation result
                error_validation = PathValidation(
                    path=path,
                    exists=False,
                    readable=False,
                    writable=False,
                    is_git_repo=False,
                    permissions={},
                    validation_errors=[f"Validation failed: {str(e)}"]
                )
                results[path] = error_validation
        
        return results
    
    def suggest_alternative_paths(self, failed_path: str) -> List[str]:
        """Suggest alternative paths when validation fails."""
        suggestions = []
        
        try:
            failed_path_obj = Path(failed_path)
            
            # Try parent directories
            parent = failed_path_obj.parent
            while parent != parent.parent:  # Stop at root
                if parent.exists() and os.access(parent, os.W_OK):
                    suggestion = parent / "claude_workspace"
                    suggestions.append(str(suggestion))
                    break
                parent = parent.parent
            
            # Try common workspace locations
            common_locations = []
            
            if self.system == "Windows":
                common_locations = [
                    Path.home() / "Documents" / "Claude_Workspace",
                    Path.home() / "Desktop" / "Claude_Workspace",
                    Path("C:/temp/Claude_Workspace")
                ]
            else:
                common_locations = [
                    Path.home() / "Documents" / "claude_workspace",
                    Path.home() / "workspace",
                    Path("/tmp/claude_workspace")
                ]
            
            for location in common_locations:
                if str(location) not in suggestions:
                    suggestions.append(str(location))
            
        except Exception as e:
            self.logger.error(f"Failed to suggest alternatives for {failed_path}: {e}")
        
        return suggestions[:5]  # Return up to 5 suggestions