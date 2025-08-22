"""
Session Management Data Models
=============================

Comprehensive data models for Claude Code session management,
including session state, configuration, and analytics.
"""

import json
import time
import uuid
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from enum import Enum


class SessionStatus(Enum):
    """Session status enumeration."""
    CREATED = "created"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    TERMINATED = "terminated"
    ERROR = "error"


class AgentType(Enum):
    """Agent type enumeration."""
    ORCHESTRATOR = "orchestrator"
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATABASE = "database"
    API = "api"
    MIDDLEWARE = "middleware"
    DEVOPS = "devops"
    SECURITY = "security"
    PERFORMANCE = "performance"
    QUALITY = "quality"
    DOCUMENTATION = "documentation"
    MONITORING = "monitoring"


@dataclass
class PathValidation:
    """Path validation result."""
    path: str
    exists: bool
    readable: bool
    writable: bool
    is_git_repo: bool
    permissions: Dict[str, bool]
    validation_errors: List[str] = field(default_factory=list)


@dataclass
class AgentConfiguration:
    """Agent configuration settings."""
    agent_type: AgentType
    name: str
    enabled: bool = True
    priority: int = 1
    max_memory_mb: int = 512
    timeout_seconds: int = 300
    retry_attempts: int = 3
    custom_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionConfiguration:
    """Session configuration settings."""
    session_id: str
    name: str
    description: str = ""
    working_directory: str = ""
    git_enabled: bool = True
    auto_save: bool = True
    save_interval_seconds: int = 60
    max_memory_mb: int = 2048
    max_agents: int = 10
    agents: List[AgentConfiguration] = field(default_factory=list)
    environment_variables: Dict[str, str] = field(default_factory=dict)
    custom_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionMetrics:
    """Session analytics and metrics."""
    session_id: str
    start_time: float
    end_time: Optional[float] = None
    duration_seconds: float = 0.0
    commands_executed: int = 0
    files_modified: int = 0
    errors_encountered: int = 0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    agent_activations: Dict[str, int] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class SessionContext:
    """Session context and state information."""
    session_id: str
    current_directory: str
    git_branch: Optional[str] = None
    git_commit: Optional[str] = None
    active_agents: List[str] = field(default_factory=list)
    environment_state: Dict[str, Any] = field(default_factory=dict)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    last_activity: float = field(default_factory=time.time)


@dataclass
class SessionSnapshot:
    """Complete session state snapshot for export/import."""
    session_id: str
    timestamp: float
    configuration: SessionConfiguration
    context: SessionContext
    metrics: SessionMetrics
    agent_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    file_system_state: Dict[str, Any] = field(default_factory=dict)
    git_state: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Session:
    """Main session object containing all session data."""
    id: str
    name: str
    status: SessionStatus
    created_at: float
    updated_at: float
    configuration: SessionConfiguration
    context: SessionContext
    metrics: SessionMetrics
    validation: Optional[PathValidation] = None
    error_message: Optional[str] = None
    
    @classmethod
    def create_new(
        cls,
        name: str,
        working_directory: str,
        description: str = "",
        **kwargs
    ) -> 'Session':
        """Create a new session instance."""
        session_id = str(uuid.uuid4())
        current_time = time.time()
        
        configuration = SessionConfiguration(
            session_id=session_id,
            name=name,
            description=description,
            working_directory=working_directory,
            **kwargs
        )
        
        context = SessionContext(
            session_id=session_id,
            current_directory=working_directory
        )
        
        metrics = SessionMetrics(
            session_id=session_id,
            start_time=current_time
        )
        
        return cls(
            id=session_id,
            name=name,
            status=SessionStatus.CREATED,
            created_at=current_time,
            updated_at=current_time,
            configuration=configuration,
            context=context,
            metrics=metrics
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status.value,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'configuration': asdict(self.configuration),
            'context': asdict(self.context),
            'metrics': asdict(self.metrics),
            'validation': asdict(self.validation) if self.validation else None,
            'error_message': self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """Create session from dictionary."""
        config_data = data['configuration']
        agents = [
            AgentConfiguration(**agent) if isinstance(agent, dict) else agent
            for agent in config_data.get('agents', [])
        ]
        config_data['agents'] = agents
        
        return cls(
            id=data['id'],
            name=data['name'],
            status=SessionStatus(data['status']),
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            configuration=SessionConfiguration(**config_data),
            context=SessionContext(**data['context']),
            metrics=SessionMetrics(**data['metrics']),
            validation=PathValidation(**data['validation']) if data['validation'] else None,
            error_message=data.get('error_message')
        )
    
    def update_status(self, status: SessionStatus, error_message: Optional[str] = None):
        """Update session status."""
        self.status = status
        self.updated_at = time.time()
        if error_message:
            self.error_message = error_message
    
    def add_agent(self, agent_config: AgentConfiguration):
        """Add agent to session configuration."""
        self.configuration.agents.append(agent_config)
        self.updated_at = time.time()
    
    def remove_agent(self, agent_name: str):
        """Remove agent from session configuration."""
        self.configuration.agents = [
            agent for agent in self.configuration.agents
            if agent.name != agent_name
        ]
        self.updated_at = time.time()
    
    def navigate_to_path(self, new_path: str) -> bool:
        """Navigate session to new path."""
        if Path(new_path).exists():
            self.context.current_directory = new_path
            self.configuration.working_directory = new_path
            self.updated_at = time.time()
            return True
        return False
    
    def create_snapshot(self) -> SessionSnapshot:
        """Create a complete session snapshot."""
        return SessionSnapshot(
            session_id=self.id,
            timestamp=time.time(),
            configuration=self.configuration,
            context=self.context,
            metrics=self.metrics
        )


@dataclass
class SessionCreateRequest:
    """Request model for creating a new session."""
    name: str
    working_directory: str
    description: str = ""
    git_enabled: bool = True
    auto_save: bool = True
    agents: List[Dict[str, Any]] = field(default_factory=list)
    environment_variables: Dict[str, str] = field(default_factory=dict)
    custom_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionUpdateRequest:
    """Request model for updating session configuration."""
    name: Optional[str] = None
    description: Optional[str] = None
    auto_save: Optional[bool] = None
    save_interval_seconds: Optional[int] = None
    max_memory_mb: Optional[int] = None
    max_agents: Optional[int] = None
    environment_variables: Optional[Dict[str, str]] = None
    custom_settings: Optional[Dict[str, Any]] = None


@dataclass
class SessionNavigateRequest:
    """Request model for navigating session to new path."""
    path: str
    validate_permissions: bool = True
    update_git_state: bool = True


@dataclass
class SessionCloneRequest:
    """Request model for cloning a session."""
    source_session_id: str
    new_name: str
    new_working_directory: Optional[str] = None
    copy_agents: bool = True
    copy_environment: bool = True


@dataclass
class SessionImportRequest:
    """Request model for importing session data."""
    session_data: Dict[str, Any]
    merge_with_existing: bool = False
    update_paths: bool = True


@dataclass
class SessionListFilter:
    """Filter options for listing sessions."""
    status: Optional[SessionStatus] = None
    name_pattern: Optional[str] = None
    created_after: Optional[float] = None
    created_before: Optional[float] = None
    has_agents: Optional[bool] = None
    working_directory_pattern: Optional[str] = None
    limit: int = 100
    offset: int = 0