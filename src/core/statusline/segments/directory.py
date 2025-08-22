"""
Directory Segment

Displays current working directory with intelligent path truncation
and home directory replacement.
"""

import os
from pathlib import Path
from typing import Dict, Any

from .base import BaseSegment, SegmentData
from ..utils import ColorUtils, truncate_path
from ..themes import Theme


class DirectorySegment(BaseSegment):
    """Segment that displays the current working directory"""
    
    def __init__(self, config: Dict[str, Any], color_utils: ColorUtils, theme: Theme):
        super().__init__(config, color_utils, theme)
        
        # Configuration options
        self.max_depth = config.get('max_depth', 3)
        self.show_home_tilde = config.get('show_home_tilde', True)
        self.show_git_root = config.get('show_git_root', True)
        self.abbreviate_parents = config.get('abbreviate_parents', False)
        self.show_folder_icon = config.get('show_folder_icon', True)
        
        # Path tracking
        self._last_path = None
        self._path_cache = {}
    
    def _collect_data(self) -> SegmentData:
        """Collect current directory information"""
        current_path = os.getcwd()
        
        # Check if path has changed
        if current_path != self._last_path:
            self._last_path = current_path
            self._path_cache.clear()
        
        # Use cached formatted path if available
        if 'formatted_path' in self._path_cache:
            formatted_path = self._path_cache['formatted_path']
        else:
            formatted_path = self._format_path(current_path)
            self._path_cache['formatted_path'] = formatted_path
        
        # Determine status based on path characteristics
        status = self._determine_status(current_path)
        
        # Generate tooltip
        tooltip = f"Current directory: {current_path}"
        if len(current_path) > 50:
            tooltip += f"\nLength: {len(current_path)} characters"
        
        return SegmentData(
            content=formatted_path,
            status=status,
            icon=self._get_directory_icon(current_path),
            tooltip=tooltip,
            clickable=True
        )
    
    def _format_data(self, data: SegmentData) -> str:
        """Format directory data for display"""
        content = data.content
        
        # Add icon if enabled
        if self.show_folder_icon and data.icon:
            content = f"{data.icon} {content}"
        
        return content
    
    def _format_path(self, path: str) -> str:
        """Format path according to configuration"""
        path_obj = Path(path)
        
        # Replace home directory with tilde
        if self.show_home_tilde:
            try:
                home = Path.home()
                if path_obj.is_relative_to(home):
                    relative_path = path_obj.relative_to(home)
                    if str(relative_path) == '.':
                        return '~'
                    else:
                        path = f"~/{relative_path}"
                        path_obj = Path(path)
            except (ValueError, OSError):
                pass
        
        # Handle git repository root
        if self.show_git_root:
            git_root = self._find_git_root(path)
            if git_root and git_root != path:
                try:
                    git_root_obj = Path(git_root)
                    if path_obj.is_relative_to(git_root_obj):
                        relative_to_git = path_obj.relative_to(git_root_obj)
                        git_name = git_root_obj.name
                        if str(relative_to_git) == '.':
                            return f"[{git_name}]"
                        else:
                            return f"[{git_name}]/{relative_to_git}"
                except (ValueError, OSError):
                    pass
        
        # Apply depth limiting
        parts = path_obj.parts
        if len(parts) > self.max_depth:
            if self.abbreviate_parents:
                # Abbreviate parent directories
                abbreviated_parts = []
                for part in parts[:-self.max_depth+1]:
                    if len(part) > 1:
                        abbreviated_parts.append(part[0])
                    else:
                        abbreviated_parts.append(part)
                
                remaining_parts = parts[-self.max_depth+1:]
                path = '/'.join(abbreviated_parts + list(remaining_parts))
            else:
                # Show only last N parts with ellipsis
                kept_parts = parts[-self.max_depth:]
                path = '/'.join(['...'] + list(kept_parts))
        else:
            path = str(path_obj)
        
        return path
    
    def _find_git_root(self, path: str) -> str:
        """Find git repository root directory"""
        current = Path(path)
        
        while current != current.parent:
            if (current / '.git').exists():
                return str(current)
            current = current.parent
        
        return None
    
    def _determine_status(self, path: str) -> str:
        """Determine directory status"""
        path_obj = Path(path)
        
        # Check if it's a special directory
        if path == os.path.expanduser('~'):
            return 'home'
        
        if self._find_git_root(path):
            return 'git_repo'
        
        # Check permissions
        if not os.access(path, os.W_OK):
            return 'readonly'
        
        # Check if it's a project directory (has common project files)
        project_files = [
            'package.json', 'requirements.txt', 'Cargo.toml', 
            'pom.xml', 'build.gradle', 'Makefile', 'CMakeLists.txt',
            'pyproject.toml', 'composer.json', 'go.mod'
        ]
        
        for project_file in project_files:
            if (path_obj / project_file).exists():
                return 'project'
        
        return 'normal'
    
    def _get_directory_icon(self, path: str) -> str:
        """Get appropriate icon for directory"""
        if not self.show_folder_icon:
            return ""
        
        status = self._determine_status(path)
        
        # Check if Unicode is supported by looking at the terminal capabilities
        # For now, use simple ASCII fallbacks on all systems to ensure compatibility
        icon_map = {
            'home': '~',
            'git_repo': '±',
            'project': '*',
            'readonly': '!',
            'normal': '/'
        }
        
        return icon_map.get(status, '/')
    
    def get_current_path(self) -> str:
        """Get the current working directory"""
        return os.getcwd()
    
    def get_path_info(self) -> Dict[str, Any]:
        """Get detailed information about current path"""
        path = self.get_current_path()
        path_obj = Path(path)
        
        try:
            stat = path_obj.stat()
            return {
                'path': path,
                'absolute': path_obj.absolute(),
                'name': path_obj.name,
                'parent': str(path_obj.parent),
                'is_git_repo': self._find_git_root(path) is not None,
                'is_home': path == os.path.expanduser('~'),
                'is_writable': os.access(path, os.W_OK),
                'size': sum(f.stat().st_size for f in path_obj.rglob('*') if f.is_file()),
                'file_count': len(list(path_obj.iterdir())) if path_obj.is_dir() else 0,
                'modified_time': stat.st_mtime,
            }
        except (OSError, PermissionError):
            return {
                'path': path,
                'error': 'Unable to access path information'
            }
    
    def navigate_to(self, path: str) -> bool:
        """
        Navigate to a different directory
        
        Args:
            path: Target directory path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            expanded_path = os.path.expanduser(path)
            abs_path = os.path.abspath(expanded_path)
            
            if os.path.isdir(abs_path):
                os.chdir(abs_path)
                self.clear_cache()  # Force refresh
                return True
            
        except (OSError, PermissionError):
            pass
        
        return False
    
    def get_breadcrumb(self) -> list:
        """Get breadcrumb navigation for current path"""
        path = self.get_current_path()
        path_obj = Path(path)
        
        breadcrumb = []
        current = path_obj
        
        while current != current.parent:
            breadcrumb.append({
                'name': current.name or str(current),
                'path': str(current),
                'is_current': current == path_obj
            })
            current = current.parent
        
        return list(reversed(breadcrumb))
    
    def get_suggestions(self, partial_path: str) -> list:
        """Get directory completion suggestions"""
        try:
            if partial_path.startswith('~'):
                partial_path = os.path.expanduser(partial_path)
            
            if not os.path.isabs(partial_path):
                partial_path = os.path.join(self.get_current_path(), partial_path)
            
            parent_dir = os.path.dirname(partial_path)
            basename = os.path.basename(partial_path)
            
            if not os.path.isdir(parent_dir):
                return []
            
            suggestions = []
            for item in os.listdir(parent_dir):
                if item.startswith(basename) and os.path.isdir(os.path.join(parent_dir, item)):
                    suggestions.append({
                        'name': item,
                        'path': os.path.join(parent_dir, item),
                        'type': 'directory'
                    })
            
            return sorted(suggestions, key=lambda x: x['name'])
            
        except (OSError, PermissionError):
            return []