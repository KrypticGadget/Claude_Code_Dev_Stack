"""
Statusline Configuration System

Handles loading, validation, and management of statusline configuration
including segment definitions, themes, and runtime settings.
"""

import os
import json
import yaml
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path

from .themes import Theme, DefaultTheme, MinimalTheme, PowerlineTheme


@dataclass
class SegmentConfig:
    """Configuration for individual statusline segments"""
    type: str
    enabled: bool = True
    priority: int = 100
    cache_timeout: float = 1.0
    max_width: Optional[int] = None
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StatuslineConfig:
    """Main statusline configuration"""
    # Display settings
    layout: str = 'left'  # left, right, center, spread, justified
    position: str = 'bottom'  # top, bottom, inline
    separator: str = ' | '
    padding: int = 1
    
    # Update and performance settings
    update_interval: float = 1.0
    cache_timeout: float = 1.0
    max_width: Optional[int] = None
    truncate_mode: str = 'ellipsis'  # ellipsis, fade, cut
    
    # Feature flags
    live_updates: bool = True
    color_support: bool = True
    unicode_support: bool = True
    debug: bool = False
    
    # Segments and theme
    segments: List[SegmentConfig] = field(default_factory=list)
    theme: Theme = field(default_factory=DefaultTheme)
    
    # File paths
    config_file: Optional[str] = None
    log_file: Optional[str] = None


class ConfigManager:
    """Manages statusline configuration loading and saving"""
    
    DEFAULT_CONFIG_PATHS = [
        os.path.expanduser("~/.config/claude-code/statusline.yml"),
        os.path.expanduser("~/.config/claude-code/statusline.yaml"),
        os.path.expanduser("~/.config/claude-code/statusline.json"),
        os.path.expanduser("~/.claude-code-statusline.yml"),
        os.path.expanduser("~/.claude-code-statusline.yaml"),
        os.path.expanduser("~/.claude-code-statusline.json"),
        "./config/statusline.yml",
        "./config/statusline.yaml", 
        "./config/statusline.json"
    ]
    
    def __init__(self):
        self.theme_registry = {
            'default': DefaultTheme,
            'minimal': MinimalTheme,
            'powerline': PowerlineTheme
        }
    
    def load_config(self, config_path: Optional[str] = None) -> StatuslineConfig:
        """
        Load configuration from file or create default configuration
        
        Args:
            config_path: Optional path to config file. If None, searches default paths.
            
        Returns:
            StatuslineConfig instance
        """
        if config_path:
            config_files = [config_path]
        else:
            config_files = self.DEFAULT_CONFIG_PATHS
        
        for path in config_files:
            if os.path.exists(path):
                try:
                    return self._load_from_file(path)
                except Exception as e:
                    print(f"Warning: Failed to load config from {path}: {e}")
                    continue
        
        # Return default configuration if no file found
        return self._create_default_config()
    
    def _load_from_file(self, file_path: str) -> StatuslineConfig:
        """Load configuration from a specific file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.endswith('.json'):
                data = json.load(f)
            else:
                data = yaml.safe_load(f)
        
        return self._parse_config_data(data, file_path)
    
    def _parse_config_data(self, data: Dict[str, Any], file_path: str) -> StatuslineConfig:
        """Parse configuration data into StatuslineConfig object"""
        config = StatuslineConfig()
        config.config_file = file_path
        
        # Update basic settings
        for key in ['layout', 'position', 'separator', 'padding', 'update_interval',
                   'cache_timeout', 'max_width', 'truncate_mode', 'live_updates',
                   'color_support', 'unicode_support', 'debug', 'log_file']:
            if key in data:
                setattr(config, key, data[key])
        
        # Parse theme
        theme_name = data.get('theme', 'default')
        if isinstance(theme_name, str):
            if theme_name in self.theme_registry:
                config.theme = self.theme_registry[theme_name]()
            else:
                print(f"Warning: Unknown theme '{theme_name}', using default")
                config.theme = DefaultTheme()
        elif isinstance(theme_name, dict):
            # Custom theme definition
            config.theme = self._create_custom_theme(theme_name)
        
        # Parse segments
        segments_data = data.get('segments', [])
        config.segments = []
        
        for segment_data in segments_data:
            segment_config = SegmentConfig(
                type=segment_data['type'],
                enabled=segment_data.get('enabled', True),
                priority=segment_data.get('priority', 100),
                cache_timeout=segment_data.get('cache_timeout', 1.0),
                max_width=segment_data.get('max_width'),
                config=segment_data.get('config', {})
            )
            config.segments.append(segment_config)
        
        # Sort segments by priority
        config.segments.sort(key=lambda x: x.priority)
        
        return config
    
    def _create_custom_theme(self, theme_data: Dict[str, Any]) -> Theme:
        """Create a custom theme from configuration data"""
        from .themes import CustomTheme
        return CustomTheme(theme_data)
    
    def _create_default_config(self) -> StatuslineConfig:
        """Create default configuration with basic segments"""
        config = StatuslineConfig()
        
        # Add default segments
        default_segments = [
            SegmentConfig(type='directory', priority=10),
            SegmentConfig(type='git', priority=20),
            SegmentConfig(type='claude_session', priority=30),
            SegmentConfig(type='system_info', priority=40, config={'show_cpu': True, 'show_memory': True}),
            SegmentConfig(type='time', priority=50)
        ]
        
        config.segments = default_segments
        return config
    
    def save_config(self, config: StatuslineConfig, file_path: Optional[str] = None):
        """
        Save configuration to file
        
        Args:
            config: StatuslineConfig to save
            file_path: Optional file path. If None, uses config.config_file or default path.
        """
        if not file_path:
            file_path = config.config_file or self.DEFAULT_CONFIG_PATHS[0]
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Convert to serializable format
        data = self._config_to_dict(config)
        
        # Save based on file extension
        with open(file_path, 'w', encoding='utf-8') as f:
            if file_path.endswith('.json'):
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    
    def _config_to_dict(self, config: StatuslineConfig) -> Dict[str, Any]:
        """Convert StatuslineConfig to dictionary for serialization"""
        data = {
            'layout': config.layout,
            'position': config.position,
            'separator': config.separator,
            'padding': config.padding,
            'update_interval': config.update_interval,
            'cache_timeout': config.cache_timeout,
            'truncate_mode': config.truncate_mode,
            'live_updates': config.live_updates,
            'color_support': config.color_support,
            'unicode_support': config.unicode_support,
            'debug': config.debug
        }
        
        if config.max_width:
            data['max_width'] = config.max_width
        
        if config.log_file:
            data['log_file'] = config.log_file
        
        # Theme
        if hasattr(config.theme, 'name'):
            data['theme'] = config.theme.name
        else:
            data['theme'] = config.theme.__class__.__name__.lower().replace('theme', '')
        
        # Segments
        data['segments'] = []
        for segment in config.segments:
            segment_data = {
                'type': segment.type,
                'enabled': segment.enabled,
                'priority': segment.priority,
                'cache_timeout': segment.cache_timeout
            }
            
            if segment.max_width:
                segment_data['max_width'] = segment.max_width
            
            if segment.config:
                segment_data['config'] = segment.config
            
            data['segments'].append(segment_data)
        
        return data
    
    def validate_config(self, config: StatuslineConfig) -> List[str]:
        """
        Validate configuration and return list of issues
        
        Args:
            config: Configuration to validate
            
        Returns:
            List of validation error messages
        """
        issues = []
        
        # Validate layout
        valid_layouts = ['left', 'right', 'center', 'spread', 'justified']
        if config.layout not in valid_layouts:
            issues.append(f"Invalid layout '{config.layout}'. Must be one of: {valid_layouts}")
        
        # Validate position
        valid_positions = ['top', 'bottom', 'inline']
        if config.position not in valid_positions:
            issues.append(f"Invalid position '{config.position}'. Must be one of: {valid_positions}")
        
        # Validate truncate mode
        valid_truncate_modes = ['ellipsis', 'fade', 'cut']
        if config.truncate_mode not in valid_truncate_modes:
            issues.append(f"Invalid truncate_mode '{config.truncate_mode}'. Must be one of: {valid_truncate_modes}")
        
        # Validate numeric values
        if config.update_interval <= 0:
            issues.append("update_interval must be positive")
        
        if config.cache_timeout < 0:
            issues.append("cache_timeout must be non-negative")
        
        if config.padding < 0:
            issues.append("padding must be non-negative")
        
        if config.max_width is not None and config.max_width <= 0:
            issues.append("max_width must be positive if specified")
        
        # Validate segments
        segment_types = ['directory', 'git', 'claude_session', 'system_info', 
                        'agent_status', 'network', 'time', 'custom']
        
        for i, segment in enumerate(config.segments):
            if segment.type not in segment_types:
                issues.append(f"Segment {i}: Invalid type '{segment.type}'. Must be one of: {segment_types}")
            
            if segment.cache_timeout < 0:
                issues.append(f"Segment {i}: cache_timeout must be non-negative")
            
            if segment.max_width is not None and segment.max_width <= 0:
                issues.append(f"Segment {i}: max_width must be positive if specified")
        
        return issues
    
    def register_theme(self, name: str, theme_class: type):
        """Register a custom theme class"""
        self.theme_registry[name] = theme_class
    
    def get_example_config(self) -> Dict[str, Any]:
        """Get an example configuration for documentation"""
        return {
            'layout': 'justified',
            'position': 'bottom',
            'separator': ' │ ',
            'padding': 1,
            'update_interval': 1.0,
            'cache_timeout': 1.0,
            'max_width': 120,
            'truncate_mode': 'ellipsis',
            'live_updates': True,
            'color_support': True,
            'unicode_support': True,
            'debug': False,
            'theme': 'powerline',
            'segments': [
                {
                    'type': 'directory',
                    'enabled': True,
                    'priority': 10,
                    'cache_timeout': 1.0,
                    'config': {
                        'max_depth': 3,
                        'show_home_tilde': True
                    }
                },
                {
                    'type': 'git',
                    'enabled': True,
                    'priority': 20,
                    'cache_timeout': 2.0,
                    'config': {
                        'show_branch': True,
                        'show_status': True,
                        'show_ahead_behind': True
                    }
                },
                {
                    'type': 'claude_session',
                    'enabled': True,
                    'priority': 30,
                    'config': {
                        'show_token_usage': True,
                        'show_session_time': True
                    }
                },
                {
                    'type': 'system_info',
                    'enabled': True,
                    'priority': 40,
                    'config': {
                        'show_cpu': True,
                        'show_memory': True,
                        'show_load': False
                    }
                },
                {
                    'type': 'agent_status',
                    'enabled': True,
                    'priority': 35,
                    'config': {
                        'show_active_agents': True,
                        'max_agents_shown': 3
                    }
                },
                {
                    'type': 'network',
                    'enabled': True,
                    'priority': 45,
                    'config': {
                        'show_connectivity': True,
                        'show_tunnel_status': True
                    }
                },
                {
                    'type': 'time',
                    'enabled': True,
                    'priority': 50,
                    'config': {
                        'format': '%H:%M:%S',
                        'show_date': False
                    }
                }
            ]
        }