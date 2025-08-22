"""
Git Segment

Displays git repository information including branch, status, and sync status.
"""

import os
from typing import Dict, Any, Optional

from .base import BaseSegment, SegmentData
from ..utils import ColorUtils, GitUtils
from ..themes import Theme


class GitSegment(BaseSegment):
    """Segment that displays git repository information"""
    
    def __init__(self, config: Dict[str, Any], color_utils: ColorUtils, theme: Theme):
        super().__init__(config, color_utils, theme)
        
        # Configuration options
        self.show_branch = config.get('show_branch', True)
        self.show_status = config.get('show_status', True)
        self.show_ahead_behind = config.get('show_ahead_behind', True)
        self.show_stash_count = config.get('show_stash_count', True)
        self.branch_max_length = config.get('branch_max_length', 20)
        self.compact_status = config.get('compact_status', False)
        self.show_icons = config.get('show_icons', True)
        
        # Git utilities
        self.git_utils = GitUtils()
        
        # Status tracking
        self._last_repo_path = None
    
    def _collect_data(self) -> SegmentData:
        """Collect git repository information"""
        if not self.git_utils.git_available:
            return SegmentData(
                content="",
                status="disabled",
                tooltip="Git not available"
            )
        
        current_path = os.getcwd()
        
        # Get git repository info
        repo_info = self.git_utils.get_repo_info(current_path, use_cache=True)
        
        if not repo_info.get('is_repo', False):
            return SegmentData(
                content="",
                status="not_repo",
                tooltip="Not in a git repository"
            )
        
        # Build content
        content_parts = []
        
        # Branch name
        if self.show_branch:
            branch = repo_info.get('branch', 'HEAD')
            if len(branch) > self.branch_max_length:
                branch = branch[:self.branch_max_length-3] + '...'
            
            branch_icon = self._get_branch_icon()
            if branch_icon and self.show_icons:
                content_parts.append(f"{branch_icon} {branch}")
            else:
                content_parts.append(branch)
        
        # Repository status
        if self.show_status:
            status_text = self._format_status(repo_info)
            if status_text:
                content_parts.append(status_text)
        
        # Ahead/behind tracking
        if self.show_ahead_behind:
            tracking_text = self._format_tracking(repo_info)
            if tracking_text:
                content_parts.append(tracking_text)
        
        # Stash count
        if self.show_stash_count:
            stash_count = repo_info.get('stashed', 0)
            if stash_count > 0:
                stash_icon = self._get_stash_icon()
                stash_text = f"{stash_icon}{stash_count}" if stash_icon else f"stash:{stash_count}"
                content_parts.append(stash_text)
        
        content = ' '.join(content_parts) if content_parts else ""
        
        # Determine overall status
        status = self._determine_status(repo_info)
        
        # Generate tooltip
        tooltip = self._generate_tooltip(repo_info)
        
        return SegmentData(
            content=content,
            status=status,
            icon=self._get_branch_icon(),
            tooltip=tooltip,
            clickable=True
        )
    
    def _format_data(self, data: SegmentData) -> str:
        """Format git data for display"""
        return data.content
    
    def _format_status(self, repo_info: Dict[str, Any]) -> str:
        """Format repository status indicators"""
        if not repo_info:
            return ""
        
        status_parts = []
        
        # File status counts
        modified = repo_info.get('modified', 0)
        added = repo_info.get('added', 0)
        deleted = repo_info.get('deleted', 0)
        untracked = repo_info.get('untracked', 0)
        
        if self.compact_status:
            # Compact format: M3 A1 D2 ?5
            if modified > 0:
                status_parts.append(f"M{modified}")
            if added > 0:
                status_parts.append(f"A{added}")
            if deleted > 0:
                status_parts.append(f"D{deleted}")
            if untracked > 0:
                status_parts.append(f"?{untracked}")
        else:
            # Icon format with symbols
            if modified > 0:
                icon = self._get_modified_icon()
                status_parts.append(f"{icon}{modified}" if icon else f"M{modified}")
            if added > 0:
                icon = self._get_added_icon()
                status_parts.append(f"{icon}{added}" if icon else f"A{added}")
            if deleted > 0:
                icon = self._get_deleted_icon()
                status_parts.append(f"{icon}{deleted}" if icon else f"D{deleted}")
            if untracked > 0:
                icon = self._get_untracked_icon()
                status_parts.append(f"{icon}{untracked}" if icon else f"?{untracked}")
        
        return ' '.join(status_parts)
    
    def _format_tracking(self, repo_info: Dict[str, Any]) -> str:
        """Format ahead/behind tracking information"""
        ahead = repo_info.get('ahead', 0)
        behind = repo_info.get('behind', 0)
        
        tracking_parts = []
        
        if ahead > 0:
            ahead_icon = self._get_ahead_icon()
            tracking_parts.append(f"{ahead_icon}{ahead}" if ahead_icon else f"↑{ahead}")
        
        if behind > 0:
            behind_icon = self._get_behind_icon()
            tracking_parts.append(f"{behind_icon}{behind}" if behind_icon else f"↓{behind}")
        
        return ' '.join(tracking_parts)
    
    def _determine_status(self, repo_info: Dict[str, Any]) -> str:
        """Determine overall git status"""
        if not repo_info.get('is_repo', False):
            return 'not_repo'
        
        # Check for conflicts (simplified check)
        if repo_info.get('status') == 'conflict':
            return 'conflict'
        
        # Check for dirty working tree
        total_changes = (
            repo_info.get('modified', 0) +
            repo_info.get('added', 0) +
            repo_info.get('deleted', 0) +
            repo_info.get('untracked', 0)
        )
        
        if total_changes > 0:
            return 'dirty'
        
        # Check sync status
        ahead = repo_info.get('ahead', 0)
        behind = repo_info.get('behind', 0)
        
        if ahead > 0 or behind > 0:
            return 'sync_needed'
        
        return 'clean'
    
    def _generate_tooltip(self, repo_info: Dict[str, Any]) -> str:
        """Generate detailed tooltip for git segment"""
        if not repo_info.get('is_repo', False):
            return "Not in a git repository"
        
        lines = []
        
        # Branch info
        branch = repo_info.get('branch', 'HEAD')
        lines.append(f"Branch: {branch}")
        
        # Status summary
        status = repo_info.get('status', 'unknown')
        lines.append(f"Status: {status}")
        
        # File changes
        modified = repo_info.get('modified', 0)
        added = repo_info.get('added', 0)
        deleted = repo_info.get('deleted', 0)
        untracked = repo_info.get('untracked', 0)
        
        if modified or added or deleted or untracked:
            changes = []
            if modified: changes.append(f"{modified} modified")
            if added: changes.append(f"{added} added")
            if deleted: changes.append(f"{deleted} deleted")
            if untracked: changes.append(f"{untracked} untracked")
            lines.append(f"Changes: {', '.join(changes)}")
        
        # Tracking info
        ahead = repo_info.get('ahead', 0)
        behind = repo_info.get('behind', 0)
        if ahead or behind:
            tracking = []
            if ahead: tracking.append(f"{ahead} ahead")
            if behind: tracking.append(f"{behind} behind")
            lines.append(f"Tracking: {', '.join(tracking)}")
        
        # Stash info
        stashed = repo_info.get('stashed', 0)
        if stashed > 0:
            lines.append(f"Stashed: {stashed} changes")
        
        return '\n'.join(lines)
    
    def _get_branch_icon(self) -> Optional[str]:
        """Get branch icon from theme"""
        if not self.show_icons:
            return None
        
        if hasattr(self.theme, 'unicode_symbols'):
            return self.theme.unicode_symbols.get('branch', '⎇')
        
        return '⎇'
    
    def _get_modified_icon(self) -> Optional[str]:
        """Get modified files icon"""
        if not self.show_icons:
            return None
        
        if hasattr(self.theme, 'unicode_symbols'):
            return self.theme.unicode_symbols.get('modified', '●')
        
        return '●'
    
    def _get_added_icon(self) -> Optional[str]:
        """Get added files icon"""
        if not self.show_icons:
            return None
        
        if hasattr(self.theme, 'unicode_symbols'):
            return self.theme.unicode_symbols.get('added', '+')
        
        return '+'
    
    def _get_deleted_icon(self) -> Optional[str]:
        """Get deleted files icon"""
        if not self.show_icons:
            return None
        
        if hasattr(self.theme, 'unicode_symbols'):
            return self.theme.unicode_symbols.get('deleted', '✖')
        
        return '✖'
    
    def _get_untracked_icon(self) -> Optional[str]:
        """Get untracked files icon"""
        if not self.show_icons:
            return None
        
        if hasattr(self.theme, 'unicode_symbols'):
            return self.theme.unicode_symbols.get('untracked', '?')
        
        return '?'
    
    def _get_ahead_icon(self) -> Optional[str]:
        """Get ahead commits icon"""
        if not self.show_icons:
            return None
        
        if hasattr(self.theme, 'unicode_symbols'):
            return self.theme.unicode_symbols.get('ahead', '↑')
        
        return '↑'
    
    def _get_behind_icon(self) -> Optional[str]:
        """Get behind commits icon"""
        if not self.show_icons:
            return None
        
        if hasattr(self.theme, 'unicode_symbols'):
            return self.theme.unicode_symbols.get('behind', '↓')
        
        return '↓'
    
    def _get_stash_icon(self) -> Optional[str]:
        """Get stash icon"""
        if not self.show_icons:
            return None
        
        if hasattr(self.theme, 'unicode_symbols'):
            return self.theme.unicode_symbols.get('stash', '📦')
        
        return '📦'
    
    def get_repository_info(self) -> Dict[str, Any]:
        """Get detailed repository information"""
        return self.git_utils.get_repo_info(use_cache=False)
    
    def refresh_git_info(self):
        """Force refresh of git information"""
        self.git_utils.clear_cache()
        self.clear_cache()
    
    def get_branch_list(self) -> list:
        """Get list of available branches"""
        if not self.git_utils.git_available:
            return []
        
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'branch', '-a'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                branches = []
                for line in result.stdout.strip().split('\n'):
                    line = line.strip()
                    if line:
                        # Remove markers like * and remotes/origin/
                        if line.startswith('* '):
                            line = line[2:]
                        if line.startswith('remotes/origin/'):
                            line = line[15:]
                        
                        if line and line not in ['HEAD', 'HEAD ->']:
                            branches.append(line)
                
                return sorted(set(branches))
            
        except Exception:
            pass
        
        return []
    
    def get_commit_summary(self, count: int = 5) -> list:
        """Get recent commit summary"""
        if not self.git_utils.git_available:
            return []
        
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'log', f'-{count}', '--oneline', '--decorate'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                commits = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        commits.append(line)
                return commits
            
        except Exception:
            pass
        
        return []