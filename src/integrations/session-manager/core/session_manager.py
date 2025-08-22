"""
Session Manager Core
===================

Core session management functionality including session lifecycle,
state persistence, and coordination with Claude Code agents.
"""

import json
import os
import time
import asyncio
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import logging

import sys
sys.path.append(str(Path(__file__).parent.parent))

from models.session_models import (
    Session, SessionStatus, SessionConfiguration, SessionContext,
    SessionMetrics, SessionSnapshot, PathValidation, AgentConfiguration,
    AgentType, SessionCreateRequest, SessionUpdateRequest,
    SessionNavigateRequest, SessionCloneRequest, SessionImportRequest,
    SessionListFilter
)


class SessionValidationError(Exception):
    """Session validation error."""
    pass


class SessionNotFoundError(Exception):
    """Session not found error."""
    pass


class SessionPermissionError(Exception):
    """Session permission error."""
    pass


class SessionManager:
    """
    Core session manager responsible for session lifecycle,
    persistence, and state management.
    """
    
    def __init__(self, data_directory: str = None):
        self.data_directory = Path(data_directory or Path.home() / ".claude" / "sessions")
        self.data_directory.mkdir(parents=True, exist_ok=True)
        
        self.sessions: Dict[str, Session] = {}
        self.active_sessions: Set[str] = set()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Load existing sessions
        self._load_sessions()
    
    def _load_sessions(self):
        """Load existing sessions from disk."""
        try:
            sessions_file = self.data_directory / "sessions.json"
            if sessions_file.exists():
                with open(sessions_file, 'r') as f:
                    sessions_data = json.load(f)
                
                for session_data in sessions_data.get('sessions', []):
                    try:
                        session = Session.from_dict(session_data)
                        self.sessions[session.id] = session
                        
                        # Mark active sessions
                        if session.status in [SessionStatus.ACTIVE, SessionStatus.INITIALIZING]:
                            self.active_sessions.add(session.id)
                    except Exception as e:
                        self.logger.warning(f"Failed to load session {session_data.get('id')}: {e}")
        except Exception as e:
            self.logger.error(f"Failed to load sessions: {e}")
    
    def _save_sessions(self):
        """Save sessions to disk."""
        try:
            sessions_data = {
                'sessions': [session.to_dict() for session in self.sessions.values()],
                'last_updated': time.time()
            }
            
            sessions_file = self.data_directory / "sessions.json"
            with open(sessions_file, 'w') as f:
                json.dump(sessions_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save sessions: {e}")
            raise
    
    def _validate_path(self, path: str) -> PathValidation:
        """Validate a path for session use."""
        path_obj = Path(path)
        
        validation = PathValidation(
            path=str(path_obj.absolute()),
            exists=path_obj.exists(),
            readable=False,
            writable=False,
            is_git_repo=False,
            permissions={}
        )
        
        try:
            # Check existence and create if needed
            if not validation.exists:
                path_obj.mkdir(parents=True, exist_ok=True)
                validation.exists = True
            
            # Check permissions
            validation.readable = os.access(path_obj, os.R_OK)
            validation.writable = os.access(path_obj, os.W_OK)
            
            validation.permissions = {
                'read': validation.readable,
                'write': validation.writable,
                'execute': os.access(path_obj, os.X_OK)
            }
            
            # Check if git repository
            git_dir = path_obj / ".git"
            validation.is_git_repo = git_dir.exists() and git_dir.is_dir()
            
            # Validation errors
            if not validation.readable:
                validation.validation_errors.append("Path is not readable")
            if not validation.writable:
                validation.validation_errors.append("Path is not writable")
                
        except Exception as e:
            validation.validation_errors.append(f"Path validation error: {str(e)}")
        
        return validation
    
    def _initialize_agents(self, session: Session):
        """Initialize agents for a session."""
        try:
            for agent_config in session.configuration.agents:
                # Agent initialization logic would go here
                # For now, just mark as initialized
                self.logger.info(f"Initialized agent {agent_config.name} for session {session.id}")
                
                # Update metrics
                if agent_config.name not in session.metrics.agent_activations:
                    session.metrics.agent_activations[agent_config.name] = 0
                session.metrics.agent_activations[agent_config.name] += 1
        except Exception as e:
            self.logger.error(f"Failed to initialize agents for session {session.id}: {e}")
            raise
    
    async def create_session(self, request: SessionCreateRequest) -> Session:
        """Create a new session."""
        # Validate path
        path_validation = self._validate_path(request.working_directory)
        if path_validation.validation_errors:
            raise SessionValidationError(f"Path validation failed: {', '.join(path_validation.validation_errors)}")
        
        # Create session
        session = Session.create_new(
            name=request.name,
            working_directory=request.working_directory,
            description=request.description,
            git_enabled=request.git_enabled,
            auto_save=request.auto_save,
            environment_variables=request.environment_variables,
            custom_settings=request.custom_settings
        )
        
        # Add agents
        for agent_data in request.agents:
            agent_config = AgentConfiguration(**agent_data)
            session.add_agent(agent_config)
        
        session.validation = path_validation
        session.update_status(SessionStatus.INITIALIZING)
        
        # Store session
        self.sessions[session.id] = session
        self.active_sessions.add(session.id)
        
        try:
            # Initialize agents
            self._initialize_agents(session)
            
            # Update status to active
            session.update_status(SessionStatus.ACTIVE)
            
            # Save to disk
            self._save_sessions()
            
            self.logger.info(f"Created session {session.id} at {request.working_directory}")
            return session
            
        except Exception as e:
            session.update_status(SessionStatus.ERROR, str(e))
            self.active_sessions.discard(session.id)
            self._save_sessions()
            raise
    
    def get_session(self, session_id: str) -> Session:
        """Get session by ID."""
        if session_id not in self.sessions:
            raise SessionNotFoundError(f"Session {session_id} not found")
        return self.sessions[session_id]
    
    def list_sessions(self, filter_options: Optional[SessionListFilter] = None) -> List[Session]:
        """List sessions with optional filtering."""
        sessions = list(self.sessions.values())
        
        if filter_options:
            # Apply status filter
            if filter_options.status:
                sessions = [s for s in sessions if s.status == filter_options.status]
            
            # Apply name pattern filter
            if filter_options.name_pattern:
                import re
                pattern = re.compile(filter_options.name_pattern, re.IGNORECASE)
                sessions = [s for s in sessions if pattern.search(s.name)]
            
            # Apply date filters
            if filter_options.created_after:
                sessions = [s for s in sessions if s.created_at >= filter_options.created_after]
            if filter_options.created_before:
                sessions = [s for s in sessions if s.created_at <= filter_options.created_before]
            
            # Apply agents filter
            if filter_options.has_agents is not None:
                if filter_options.has_agents:
                    sessions = [s for s in sessions if s.configuration.agents]
                else:
                    sessions = [s for s in sessions if not s.configuration.agents]
            
            # Apply working directory pattern
            if filter_options.working_directory_pattern:
                import re
                pattern = re.compile(filter_options.working_directory_pattern, re.IGNORECASE)
                sessions = [s for s in sessions if pattern.search(s.configuration.working_directory)]
            
            # Apply pagination
            start = filter_options.offset
            end = start + filter_options.limit
            sessions = sessions[start:end]
        
        return sessions
    
    async def navigate_session(self, session_id: str, request: SessionNavigateRequest) -> Session:
        """Navigate session to new path."""
        session = self.get_session(session_id)
        
        if request.validate_permissions:
            path_validation = self._validate_path(request.path)
            if path_validation.validation_errors:
                raise SessionValidationError(f"Navigation failed: {', '.join(path_validation.validation_errors)}")
            session.validation = path_validation
        
        # Update session path
        success = session.navigate_to_path(request.path)
        if not success:
            raise SessionValidationError(f"Failed to navigate to {request.path}")
        
        # Update git state if requested
        if request.update_git_state and session.validation and session.validation.is_git_repo:
            # Update git branch and commit info
            # This would integrate with git commands
            pass
        
        self._save_sessions()
        self.logger.info(f"Session {session_id} navigated to {request.path}")
        return session
    
    async def update_session(self, session_id: str, request: SessionUpdateRequest) -> Session:
        """Update session configuration."""
        session = self.get_session(session_id)
        
        # Update configuration fields
        if request.name is not None:
            session.name = request.name
            session.configuration.name = request.name
        
        if request.description is not None:
            session.configuration.description = request.description
        
        if request.auto_save is not None:
            session.configuration.auto_save = request.auto_save
        
        if request.save_interval_seconds is not None:
            session.configuration.save_interval_seconds = request.save_interval_seconds
        
        if request.max_memory_mb is not None:
            session.configuration.max_memory_mb = request.max_memory_mb
        
        if request.max_agents is not None:
            session.configuration.max_agents = request.max_agents
        
        if request.environment_variables is not None:
            session.configuration.environment_variables.update(request.environment_variables)
        
        if request.custom_settings is not None:
            session.configuration.custom_settings.update(request.custom_settings)
        
        session.updated_at = time.time()
        self._save_sessions()
        
        self.logger.info(f"Updated session {session_id}")
        return session
    
    async def terminate_session(self, session_id: str) -> Session:
        """Terminate a session."""
        session = self.get_session(session_id)
        
        # Update status and metrics
        session.update_status(SessionStatus.TERMINATED)
        session.metrics.end_time = time.time()
        session.metrics.duration_seconds = session.metrics.end_time - session.metrics.start_time
        
        # Remove from active sessions
        self.active_sessions.discard(session_id)
        
        # Save state
        self._save_sessions()
        
        self.logger.info(f"Terminated session {session_id}")
        return session
    
    async def clone_session(self, request: SessionCloneRequest) -> Session:
        """Clone an existing session."""
        source_session = self.get_session(request.source_session_id)
        
        # Create new session configuration
        new_working_dir = request.new_working_directory or source_session.configuration.working_directory
        
        create_request = SessionCreateRequest(
            name=request.new_name,
            working_directory=new_working_dir,
            description=f"Cloned from {source_session.name}",
            git_enabled=source_session.configuration.git_enabled,
            auto_save=source_session.configuration.auto_save
        )
        
        # Copy agents if requested
        if request.copy_agents:
            create_request.agents = [
                {
                    'agent_type': agent.agent_type.value,
                    'name': agent.name,
                    'enabled': agent.enabled,
                    'priority': agent.priority,
                    'max_memory_mb': agent.max_memory_mb,
                    'timeout_seconds': agent.timeout_seconds,
                    'retry_attempts': agent.retry_attempts,
                    'custom_config': agent.custom_config.copy()
                }
                for agent in source_session.configuration.agents
            ]
        
        # Copy environment if requested
        if request.copy_environment:
            create_request.environment_variables = source_session.configuration.environment_variables.copy()
            create_request.custom_settings = source_session.configuration.custom_settings.copy()
        
        # Create the new session
        new_session = await self.create_session(create_request)
        
        self.logger.info(f"Cloned session {request.source_session_id} to {new_session.id}")
        return new_session
    
    def export_session(self, session_id: str) -> SessionSnapshot:
        """Export session data for backup/transfer."""
        session = self.get_session(session_id)
        snapshot = session.create_snapshot()
        
        # Add additional export data
        export_dir = self.data_directory / "exports"
        export_dir.mkdir(exist_ok=True)
        
        export_file = export_dir / f"session_{session_id}_{int(time.time())}.json"
        with open(export_file, 'w') as f:
            json.dump(snapshot.__dict__, f, indent=2, default=str)
        
        self.logger.info(f"Exported session {session_id} to {export_file}")
        return snapshot
    
    async def import_session(self, request: SessionImportRequest) -> Session:
        """Import session data from backup/transfer."""
        session_data = request.session_data
        
        # Create session from imported data
        if 'configuration' in session_data:
            config = session_data['configuration']
            
            create_request = SessionCreateRequest(
                name=config['name'],
                working_directory=config['working_directory'],
                description=config.get('description', 'Imported session'),
                git_enabled=config.get('git_enabled', True),
                auto_save=config.get('auto_save', True),
                agents=config.get('agents', []),
                environment_variables=config.get('environment_variables', {}),
                custom_settings=config.get('custom_settings', {})
            )
            
            # Update paths if requested
            if request.update_paths:
                # This could include path transformation logic
                pass
            
            new_session = await self.create_session(create_request)
            
            # Merge with existing if requested
            if request.merge_with_existing:
                # Merge logic would go here
                pass
            
            self.logger.info(f"Imported session as {new_session.id}")
            return new_session
        else:
            raise SessionValidationError("Invalid session data format")
    
    def get_session_analytics(self) -> Dict[str, Any]:
        """Get session analytics and statistics."""
        total_sessions = len(self.sessions)
        active_sessions = len(self.active_sessions)
        
        status_counts = {}
        for status in SessionStatus:
            status_counts[status.value] = sum(
                1 for session in self.sessions.values()
                if session.status == status
            )
        
        # Calculate average session duration
        completed_sessions = [
            s for s in self.sessions.values()
            if s.status == SessionStatus.TERMINATED and s.metrics.end_time
        ]
        
        avg_duration = 0
        if completed_sessions:
            total_duration = sum(s.metrics.duration_seconds for s in completed_sessions)
            avg_duration = total_duration / len(completed_sessions)
        
        # Most used agents
        agent_usage = {}
        for session in self.sessions.values():
            for agent_name, count in session.metrics.agent_activations.items():
                agent_usage[agent_name] = agent_usage.get(agent_name, 0) + count
        
        return {
            'total_sessions': total_sessions,
            'active_sessions': active_sessions,
            'status_distribution': status_counts,
            'average_duration_seconds': avg_duration,
            'most_used_agents': dict(sorted(agent_usage.items(), key=lambda x: x[1], reverse=True)[:10]),
            'data_directory': str(self.data_directory),
            'last_updated': time.time()
        }
    
    async def cleanup_terminated_sessions(self, older_than_days: int = 30):
        """Cleanup old terminated sessions."""
        cutoff_time = time.time() - (older_than_days * 24 * 3600)
        
        sessions_to_remove = []
        for session_id, session in self.sessions.items():
            if (session.status == SessionStatus.TERMINATED and 
                session.updated_at < cutoff_time):
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.sessions[session_id]
        
        if sessions_to_remove:
            self._save_sessions()
            self.logger.info(f"Cleaned up {len(sessions_to_remove)} old sessions")
        
        return len(sessions_to_remove)