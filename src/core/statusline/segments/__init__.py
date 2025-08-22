"""
Statusline Segments

Modular segments for displaying different types of information in the statusline.
Each segment is responsible for gathering and formatting its own data.
"""

from .base import BaseSegment
from .directory import DirectorySegment
from .git import GitSegment
from .claude_session import ClaudeSessionSegment
from .system_info import SystemInfoSegment
from .agent_status import AgentStatusSegment
from .network import NetworkSegment
from .time import TimeSegment
from .custom import CustomSegment

__all__ = [
    'BaseSegment',
    'DirectorySegment',
    'GitSegment',
    'ClaudeSessionSegment',
    'SystemInfoSegment', 
    'AgentStatusSegment',
    'NetworkSegment',
    'TimeSegment',
    'CustomSegment'
]