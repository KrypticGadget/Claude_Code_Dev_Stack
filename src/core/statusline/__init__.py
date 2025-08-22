"""
Terminal Statusline Renderer System

A comprehensive Python-based terminal statusline system with customizable segments,
real-time updates, and cross-platform compatibility.
"""

from .renderer import StatuslineRenderer
from .segments import (
    DirectorySegment,
    GitSegment,
    ClaudeSessionSegment,
    SystemInfoSegment,
    AgentStatusSegment,
    NetworkSegment,
    TimeSegment,
    CustomSegment
)
from .config import StatuslineConfig, ConfigManager
from .themes import Theme, DefaultTheme, MinimalTheme, PowerlineTheme
from .utils import TerminalUtils, ColorUtils, GitUtils

__version__ = "1.0.0"
__all__ = [
    "StatuslineRenderer",
    "StatuslineConfig",
    "ConfigManager",
    "DirectorySegment",
    "GitSegment", 
    "ClaudeSessionSegment",
    "SystemInfoSegment",
    "AgentStatusSegment",
    "NetworkSegment",
    "TimeSegment",
    "CustomSegment",
    "Theme",
    "DefaultTheme",
    "MinimalTheme", 
    "PowerlineTheme",
    "TerminalUtils",
    "ColorUtils",
    "GitUtils"
]