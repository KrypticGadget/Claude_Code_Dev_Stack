"""
Claude Code Session Manager
===========================

Comprehensive session management system for Claude Code instances.
Provides session lifecycle, monitoring, and agent coordination.
"""

from .core.session_manager import SessionManager
from .services.path_validator import PathValidator
from .services.agent_initializer import AgentInitializer
from .services.session_monitor import SessionMonitor
from .api.session_api import SessionAPI
from .models.session_models import (
    Session, SessionStatus, SessionConfiguration,
    SessionCreateRequest, SessionUpdateRequest,
    AgentConfiguration, AgentType
)

__version__ = "1.0.0"
__author__ = "Claude Code Agent System"

__all__ = [
    'SessionManager',
    'PathValidator', 
    'AgentInitializer',
    'SessionMonitor',
    'SessionAPI',
    'Session',
    'SessionStatus',
    'SessionConfiguration',
    'SessionCreateRequest',
    'SessionUpdateRequest',
    'AgentConfiguration',
    'AgentType'
]