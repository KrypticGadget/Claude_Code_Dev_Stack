"""
Statusline Themes System

Defines color schemes, styling, and visual presentation for the statusline.
Includes built-in themes and support for custom themes.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ColorScheme:
    """Color definitions for various statusline elements"""
    # Background and foreground
    bg_primary: str = 'black'
    bg_secondary: str = 'gray'
    fg_primary: str = 'white'
    fg_secondary: str = 'lightgray'
    
    # Status colors
    success: str = 'green'
    warning: str = 'yellow'
    error: str = 'red'
    info: str = 'blue'
    
    # Segment-specific colors
    directory: str = 'cyan'
    git_clean: str = 'green'
    git_dirty: str = 'yellow'
    git_conflict: str = 'red'
    claude_active: str = 'magenta'
    claude_idle: str = 'blue'
    system_normal: str = 'green'
    system_warning: str = 'yellow'
    system_critical: str = 'red'
    network_connected: str = 'green'
    network_disconnected: str = 'red'
    time: str = 'white'
    
    # Accent colors
    accent1: str = 'brightblue'
    accent2: str = 'brightmagenta'
    accent3: str = 'brightcyan'


class Theme(ABC):
    """Abstract base class for statusline themes"""
    
    def __init__(self):
        self.name = self.__class__.__name__.lower().replace('theme', '')
        self.colors = self._define_colors()
        self.separator = self._define_separator()
        self.powerline_symbols = self._define_powerline_symbols()
        self.unicode_symbols = self._define_unicode_symbols()
    
    @abstractmethod
    def _define_colors(self) -> ColorScheme:
        """Define the color scheme for this theme"""
        pass
    
    @abstractmethod
    def _define_separator(self) -> str:
        """Define the default separator for this theme"""
        pass
    
    def _define_powerline_symbols(self) -> Dict[str, str]:
        """Define powerline symbols for this theme"""
        return {
            'left_arrow': '',
            'right_arrow': '',
            'left_arrow_thin': '',
            'right_arrow_thin': '',
            'branch': '',
            'lock': '',
            'gear': '',
            'lightning': '⚡',
            'flame': '🔥'
        }
    
    def _define_unicode_symbols(self) -> Dict[str, str]:
        """Define unicode symbols for this theme"""
        return {
            'branch': '⎇',
            'modified': '●',
            'added': '+',
            'deleted': '✖',
            'renamed': '➜',
            'untracked': '?',
            'ahead': '↑',
            'behind': '↓',
            'cpu': '⚙',
            'memory': '🧠',
            'network': '🌐',
            'time': '🕐',
            'agent': '🤖',
            'check': '✓',
            'cross': '✗',
            'warning': '⚠',
            'info': 'ℹ'
        }
    
    def get_segment_style(self, segment_type: str, status: str = 'normal') -> Dict[str, str]:
        """
        Get styling for a specific segment and status
        
        Args:
            segment_type: Type of segment (directory, git, etc.)
            status: Status of segment (normal, warning, error, etc.)
            
        Returns:
            Dictionary with bg, fg, and other style properties
        """
        return {
            'bg': getattr(self.colors, f'{segment_type}', self.colors.bg_primary),
            'fg': self.colors.fg_primary,
            'bold': False,
            'italic': False,
            'underline': False
        }
    
    def format_segment(self, content: str, segment_type: str, status: str = 'normal') -> str:
        """
        Format a segment with theme styling
        
        Args:
            content: The content to format
            segment_type: Type of segment
            status: Status of segment
            
        Returns:
            Formatted string with color codes
        """
        style = self.get_segment_style(segment_type, status)
        return content  # Base implementation, override in specific themes


class DefaultTheme(Theme):
    """Default theme with basic colors and minimal styling"""
    
    def _define_colors(self) -> ColorScheme:
        return ColorScheme()
    
    def _define_separator(self) -> str:
        return ' │ '
    
    def get_segment_style(self, segment_type: str, status: str = 'normal') -> Dict[str, str]:
        color_map = {
            'directory': self.colors.directory,
            'git': self.colors.git_clean if status == 'clean' else 
                   self.colors.git_dirty if status == 'dirty' else self.colors.git_conflict,
            'claude_session': self.colors.claude_active if status == 'active' else self.colors.claude_idle,
            'system_info': self.colors.system_normal if status == 'normal' else
                          self.colors.system_warning if status == 'warning' else self.colors.system_critical,
            'agent_status': self.colors.claude_active,
            'network': self.colors.network_connected if status == 'connected' else self.colors.network_disconnected,
            'time': self.colors.time
        }
        
        return {
            'bg': 'none',
            'fg': color_map.get(segment_type, self.colors.fg_primary),
            'bold': False,
            'italic': False,
            'underline': False
        }


class MinimalTheme(Theme):
    """Minimal theme with reduced visual elements"""
    
    def _define_colors(self) -> ColorScheme:
        colors = ColorScheme()
        colors.fg_primary = 'white'
        colors.fg_secondary = 'gray'
        return colors
    
    def _define_separator(self) -> str:
        return ' | '
    
    def get_segment_style(self, segment_type: str, status: str = 'normal') -> Dict[str, str]:
        # Minimal theme uses only white and gray
        color = self.colors.fg_primary if status != 'inactive' else self.colors.fg_secondary
        
        return {
            'bg': 'none',
            'fg': color,
            'bold': segment_type in ['git', 'claude_session'],
            'italic': False,
            'underline': False
        }


class PowerlineTheme(Theme):
    """Powerline-style theme with arrows and background colors"""
    
    def _define_colors(self) -> ColorScheme:
        colors = ColorScheme()
        # Powerline uses distinct background colors
        colors.bg_primary = 'blue'
        colors.bg_secondary = 'green'
        colors.fg_primary = 'white'
        return colors
    
    def _define_separator(self) -> str:
        return ''  # Powerline uses arrows instead
    
    def get_segment_style(self, segment_type: str, status: str = 'normal') -> Dict[str, str]:
        # Map segment types to colors
        segment_colors = {
            'directory': {'bg': 'blue', 'fg': 'white'},
            'git': {'bg': 'green' if status == 'clean' else 'yellow' if status == 'dirty' else 'red', 'fg': 'black'},
            'claude_session': {'bg': 'magenta', 'fg': 'white'},
            'system_info': {'bg': 'cyan', 'fg': 'black'},
            'agent_status': {'bg': 'brightmagenta', 'fg': 'white'},
            'network': {'bg': 'green' if status == 'connected' else 'red', 'fg': 'white'},
            'time': {'bg': 'gray', 'fg': 'white'}
        }
        
        colors = segment_colors.get(segment_type, {'bg': self.colors.bg_primary, 'fg': self.colors.fg_primary})
        
        return {
            'bg': colors['bg'],
            'fg': colors['fg'],
            'bold': True,
            'italic': False,
            'underline': False
        }
    
    def format_segment(self, content: str, segment_type: str, status: str = 'normal') -> str:
        """Format segment with powerline arrows"""
        style = self.get_segment_style(segment_type, status)
        
        # Add powerline arrows (simplified for cross-platform compatibility)
        if hasattr(self, '_last_bg'):
            left_arrow = f"\033[38;5;{self._last_bg}m{self.powerline_symbols['left_arrow']}\033[0m"
        else:
            left_arrow = ""
        
        formatted_content = f"\033[48;5;{style['bg']};38;5;{style['fg']}m {content} \033[0m"
        
        self._last_bg = style['bg']  # Store for next segment
        
        return left_arrow + formatted_content


class TerminalTheme(Theme):
    """Theme optimized for terminal compatibility"""
    
    def _define_colors(self) -> ColorScheme:
        colors = ColorScheme()
        # Use basic ANSI colors for maximum compatibility
        colors.directory = '36'  # cyan
        colors.git_clean = '32'  # green  
        colors.git_dirty = '33'  # yellow
        colors.git_conflict = '31'  # red
        colors.claude_active = '35'  # magenta
        colors.system_normal = '32'  # green
        colors.time = '37'  # white
        return colors
    
    def _define_separator(self) -> str:
        return ' :: '


class NerdFontTheme(Theme):
    """Theme using Nerd Font icons and symbols"""
    
    def _define_colors(self) -> ColorScheme:
        return ColorScheme()
    
    def _define_separator(self) -> str:
        return '  '
    
    def _define_unicode_symbols(self) -> Dict[str, str]:
        # Nerd Font specific symbols
        return {
            'branch': '',
            'modified': '',
            'added': '',
            'deleted': '',
            'renamed': '',
            'untracked': '',
            'ahead': '',
            'behind': '',
            'cpu': '',
            'memory': '',
            'network': '',
            'time': '',
            'agent': '',
            'check': '',
            'cross': '',
            'warning': '',
            'info': '',
            'folder': '',
            'file': '',
            'home': ''
        }


class CustomTheme(Theme):
    """Custom theme loaded from configuration"""
    
    def __init__(self, theme_config: Dict[str, Any]):
        self.theme_config = theme_config
        super().__init__()
    
    def _define_colors(self) -> ColorScheme:
        colors = ColorScheme()
        
        # Load colors from config
        color_config = self.theme_config.get('colors', {})
        for key, value in color_config.items():
            if hasattr(colors, key):
                setattr(colors, key, value)
        
        return colors
    
    def _define_separator(self) -> str:
        return self.theme_config.get('separator', ' │ ')
    
    def get_segment_style(self, segment_type: str, status: str = 'normal') -> Dict[str, str]:
        # Load segment styles from config
        segments_config = self.theme_config.get('segments', {})
        segment_config = segments_config.get(segment_type, {})
        status_config = segment_config.get(status, segment_config.get('default', {}))
        
        return {
            'bg': status_config.get('bg', 'none'),
            'fg': status_config.get('fg', self.colors.fg_primary),
            'bold': status_config.get('bold', False),
            'italic': status_config.get('italic', False),
            'underline': status_config.get('underline', False)
        }


class ThemeManager:
    """Manages theme loading and switching"""
    
    def __init__(self):
        self.themes = {
            'default': DefaultTheme,
            'minimal': MinimalTheme,
            'powerline': PowerlineTheme,
            'terminal': TerminalTheme,
            'nerdfont': NerdFontTheme
        }
        self.current_theme: Optional[Theme] = None
    
    def register_theme(self, name: str, theme_class: type):
        """Register a new theme"""
        self.themes[name] = theme_class
    
    def get_theme(self, name: str) -> Theme:
        """Get theme instance by name"""
        if name in self.themes:
            return self.themes[name]()
        else:
            raise ValueError(f"Unknown theme: {name}")
    
    def list_themes(self) -> list:
        """List available theme names"""
        return list(self.themes.keys())
    
    def set_theme(self, theme: Theme):
        """Set the current active theme"""
        self.current_theme = theme
    
    def get_current_theme(self) -> Optional[Theme]:
        """Get the current active theme"""
        return self.current_theme
    
    def create_custom_theme(self, config: Dict[str, Any]) -> CustomTheme:
        """Create a custom theme from configuration"""
        return CustomTheme(config)
    
    def export_theme_config(self, theme: Theme) -> Dict[str, Any]:
        """Export theme configuration for saving"""
        config = {
            'name': theme.name,
            'separator': theme.separator,
            'colors': {}
        }
        
        # Export colors
        for attr in dir(theme.colors):
            if not attr.startswith('_'):
                config['colors'][attr] = getattr(theme.colors, attr)
        
        return config