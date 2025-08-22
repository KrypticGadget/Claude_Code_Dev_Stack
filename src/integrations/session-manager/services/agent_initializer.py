"""
Agent Initialization Service
===========================

Service for initializing and configuring Claude Code agents within sessions.
Handles agent lifecycle, configuration, and coordination.
"""

import asyncio
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
import logging

import sys
sys.path.append(str(Path(__file__).parent.parent))

from models.session_models import (
    AgentConfiguration, AgentType, SessionConfiguration, SessionContext
)


class AgentInitializationError(Exception):
    """Agent initialization error."""
    pass


class AgentInitializer:
    """
    Service responsible for initializing and managing Claude Code agents
    within session contexts.
    """
    
    def __init__(self, core_hooks_path: str = None):
        self.logger = logging.getLogger(__name__)
        
        # Path to core hooks directory
        if core_hooks_path:
            self.hooks_path = Path(core_hooks_path)
        else:
            # Default to relative path from this file
            self.hooks_path = Path(__file__).parent.parent.parent.parent / "core" / "hooks"
        
        # Agent definitions and capabilities
        self.agent_definitions = self._load_agent_definitions()
        
        # Active agent processes
        self.active_agents: Dict[str, Dict[str, Any]] = {}
        
        # Agent dependencies
        self.agent_dependencies = self._define_agent_dependencies()
    
    def _load_agent_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Load agent definitions and capabilities."""
        return {
            "master-orchestrator": {
                "type": AgentType.ORCHESTRATOR,
                "description": "Central coordination and task orchestration",
                "hooks": ["master_orchestrator.py", "smart_orchestrator.py"],
                "capabilities": ["task_coordination", "agent_management", "workflow_control"],
                "priority": 1,
                "memory_min": 256,
                "memory_max": 1024
            },
            "frontend-architecture": {
                "type": AgentType.FRONTEND,
                "description": "Frontend architecture and UI/UX design",
                "hooks": ["auto_documentation.py"],
                "capabilities": ["ui_design", "frontend_frameworks", "user_experience"],
                "priority": 2,
                "memory_min": 128,
                "memory_max": 512
            },
            "backend-services": {
                "type": AgentType.BACKEND,
                "description": "Backend services and API development",
                "hooks": ["enhanced_bash_hook.py"],
                "capabilities": ["api_development", "service_architecture", "business_logic"],
                "priority": 2,
                "memory_min": 256,
                "memory_max": 1024
            },
            "database-architect": {
                "type": AgentType.DATABASE,
                "description": "Database design and optimization",
                "hooks": ["dependency_checker.py"],
                "capabilities": ["schema_design", "query_optimization", "data_modeling"],
                "priority": 3,
                "memory_min": 128,
                "memory_max": 512
            },
            "api-integration-specialist": {
                "type": AgentType.API,
                "description": "API integration and external services",
                "hooks": ["hook_registry_api.py"],
                "capabilities": ["api_integration", "external_services", "data_transformation"],
                "priority": 3,
                "memory_min": 128,
                "memory_max": 512
            },
            "middleware-specialist": {
                "type": AgentType.MIDDLEWARE,
                "description": "Middleware and integration layer",
                "hooks": ["context_manager.py"],
                "capabilities": ["middleware_design", "integration_patterns", "message_queuing"],
                "priority": 4,
                "memory_min": 128,
                "memory_max": 512
            },
            "devops-deployment": {
                "type": AgentType.DEVOPS,
                "description": "DevOps and deployment automation",
                "hooks": ["git_quality_hooks.py", "venv_enforcer.py"],
                "capabilities": ["ci_cd", "deployment", "infrastructure", "automation"],
                "priority": 4,
                "memory_min": 256,
                "memory_max": 768
            },
            "security-architecture": {
                "type": AgentType.SECURITY,
                "description": "Security architecture and compliance",
                "hooks": ["security_scanner.py"],
                "capabilities": ["security_design", "vulnerability_scanning", "compliance"],
                "priority": 3,
                "memory_min": 128,
                "memory_max": 512
            },
            "performance-optimization": {
                "type": AgentType.PERFORMANCE,
                "description": "Performance optimization and monitoring",
                "hooks": ["resource_monitor.py"],
                "capabilities": ["performance_tuning", "monitoring", "optimization"],
                "priority": 4,
                "memory_min": 128,
                "memory_max": 512
            },
            "quality-assurance": {
                "type": AgentType.QUALITY,
                "description": "Quality assurance and testing",
                "hooks": ["quality_gate_hook.py", "code_linter.py"],
                "capabilities": ["testing", "quality_gates", "code_review"],
                "priority": 3,
                "memory_min": 128,
                "memory_max": 512
            },
            "technical-documentation": {
                "type": AgentType.DOCUMENTATION,
                "description": "Technical documentation and knowledge management",
                "hooks": ["auto_documentation.py"],
                "capabilities": ["documentation", "knowledge_management", "api_docs"],
                "priority": 5,
                "memory_min": 64,
                "memory_max": 256
            },
            "monitoring-observability": {
                "type": AgentType.MONITORING,
                "description": "Monitoring and observability",
                "hooks": ["status_line_manager.py", "notification_sender.py"],
                "capabilities": ["monitoring", "alerting", "observability", "metrics"],
                "priority": 4,
                "memory_min": 128,
                "memory_max": 512
            }
        }
    
    def _define_agent_dependencies(self) -> Dict[str, List[str]]:
        """Define agent dependencies and initialization order."""
        return {
            "master-orchestrator": [],  # No dependencies
            "backend-services": ["master-orchestrator"],
            "frontend-architecture": ["master-orchestrator"],
            "database-architect": ["backend-services"],
            "api-integration-specialist": ["backend-services"],
            "middleware-specialist": ["backend-services", "api-integration-specialist"],
            "security-architecture": ["backend-services", "api-integration-specialist"],
            "performance-optimization": ["backend-services", "database-architect"],
            "quality-assurance": ["backend-services", "frontend-architecture"],
            "devops-deployment": ["backend-services", "database-architect", "security-architecture"],
            "technical-documentation": ["backend-services", "frontend-architecture"],
            "monitoring-observability": ["backend-services", "performance-optimization"]
        }
    
    async def initialize_agents(
        self,
        session_config: SessionConfiguration,
        session_context: SessionContext
    ) -> Dict[str, Dict[str, Any]]:
        """
        Initialize all agents for a session in proper dependency order.
        
        Args:
            session_config: Session configuration
            session_context: Session context
            
        Returns:
            Dictionary of initialized agent states
        """
        initialized_agents = {}
        
        try:
            # Get initialization order based on dependencies
            init_order = self._get_initialization_order(session_config.agents)
            
            self.logger.info(f"Initializing {len(init_order)} agents for session {session_config.session_id}")
            
            # Initialize agents in dependency order
            for agent_config in init_order:
                try:
                    agent_state = await self._initialize_single_agent(
                        agent_config, session_config, session_context
                    )
                    initialized_agents[agent_config.name] = agent_state
                    
                    # Add delay between initializations to prevent resource conflicts
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    self.logger.error(f"Failed to initialize agent {agent_config.name}: {e}")
                    # Continue with other agents unless it's a critical dependency
                    if agent_config.name == "master-orchestrator":
                        raise AgentInitializationError(f"Critical agent initialization failed: {e}")
            
            self.logger.info(f"Successfully initialized {len(initialized_agents)} agents")
            return initialized_agents
            
        except Exception as e:
            self.logger.error(f"Agent initialization failed: {e}")
            # Cleanup any partially initialized agents
            await self._cleanup_agents(list(initialized_agents.keys()))
            raise
    
    def _get_initialization_order(self, agent_configs: List[AgentConfiguration]) -> List[AgentConfiguration]:
        """Get agent initialization order based on dependencies."""
        # Create lookup maps
        config_by_name = {config.name: config for config in agent_configs}
        
        # Topological sort for dependency resolution
        visited = set()
        temp_visited = set()
        ordered_configs = []
        
        def visit(agent_name: str):
            if agent_name in temp_visited:
                raise AgentInitializationError(f"Circular dependency detected involving {agent_name}")
            
            if agent_name not in visited:
                temp_visited.add(agent_name)
                
                # Visit dependencies first
                dependencies = self.agent_dependencies.get(agent_name, [])
                for dep in dependencies:
                    if dep in config_by_name:  # Only visit if the dependency is configured
                        visit(dep)
                
                temp_visited.remove(agent_name)
                visited.add(agent_name)
                
                # Add to ordered list if config exists
                if agent_name in config_by_name:
                    ordered_configs.append(config_by_name[agent_name])
        
        # Visit all configured agents
        for config in agent_configs:
            if config.name not in visited:
                visit(config.name)
        
        return ordered_configs
    
    async def _initialize_single_agent(
        self,
        agent_config: AgentConfiguration,
        session_config: SessionConfiguration,
        session_context: SessionContext
    ) -> Dict[str, Any]:
        """Initialize a single agent."""
        agent_name = agent_config.name
        self.logger.info(f"Initializing agent: {agent_name}")
        
        # Get agent definition
        agent_def = self.agent_definitions.get(agent_name)
        if not agent_def:
            raise AgentInitializationError(f"Unknown agent type: {agent_name}")
        
        # Validate configuration
        self._validate_agent_config(agent_config, agent_def)
        
        # Prepare agent environment
        agent_env = self._prepare_agent_environment(agent_config, session_config, session_context)
        
        # Initialize agent hooks
        hook_states = await self._initialize_agent_hooks(agent_config, agent_def, agent_env)
        
        # Create agent state
        agent_state = {
            'name': agent_name,
            'type': agent_def['type'].value,
            'status': 'initialized',
            'initialized_at': time.time(),
            'configuration': agent_config.__dict__,
            'definition': agent_def,
            'environment': agent_env,
            'hooks': hook_states,
            'metrics': {
                'initialization_time': time.time(),
                'activations': 0,
                'errors': 0,
                'last_activity': time.time()
            }
        }
        
        # Store in active agents
        self.active_agents[agent_name] = agent_state
        
        self.logger.info(f"Successfully initialized agent: {agent_name}")
        return agent_state
    
    def _validate_agent_config(self, config: AgentConfiguration, definition: Dict[str, Any]):
        """Validate agent configuration against definition."""
        # Check memory requirements
        if config.max_memory_mb < definition['memory_min']:
            raise AgentInitializationError(
                f"Agent {config.name} requires at least {definition['memory_min']}MB memory"
            )
        
        if config.max_memory_mb > definition['memory_max']:
            self.logger.warning(
                f"Agent {config.name} configured with {config.max_memory_mb}MB, "
                f"maximum recommended is {definition['memory_max']}MB"
            )
        
        # Validate timeout settings
        if config.timeout_seconds < 30:
            self.logger.warning(f"Agent {config.name} has very short timeout: {config.timeout_seconds}s")
        
        # Validate retry attempts
        if config.retry_attempts > 10:
            self.logger.warning(f"Agent {config.name} has high retry count: {config.retry_attempts}")
    
    def _prepare_agent_environment(
        self,
        agent_config: AgentConfiguration,
        session_config: SessionConfiguration,
        session_context: SessionContext
    ) -> Dict[str, Any]:
        """Prepare environment variables and settings for agent."""
        env = {
            'CLAUDE_SESSION_ID': session_config.session_id,
            'CLAUDE_WORKING_DIR': session_config.working_directory,
            'CLAUDE_AGENT_NAME': agent_config.name,
            'CLAUDE_AGENT_TYPE': agent_config.agent_type.value,
            'CLAUDE_MEMORY_LIMIT': str(agent_config.max_memory_mb),
            'CLAUDE_TIMEOUT': str(agent_config.timeout_seconds),
            'CLAUDE_RETRY_ATTEMPTS': str(agent_config.retry_attempts),
            'CLAUDE_GIT_ENABLED': str(session_config.git_enabled).lower(),
            'CLAUDE_AUTO_SAVE': str(session_config.auto_save).lower()
        }
        
        # Add session environment variables
        env.update(session_config.environment_variables)
        
        # Add agent-specific custom config
        for key, value in agent_config.custom_config.items():
            env[f'CLAUDE_AGENT_{key.upper()}'] = str(value)
        
        return env
    
    async def _initialize_agent_hooks(
        self,
        agent_config: AgentConfiguration,
        agent_def: Dict[str, Any],
        agent_env: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Initialize hooks for an agent."""
        hook_states = {}
        
        for hook_file in agent_def.get('hooks', []):
            hook_path = self.hooks_path / hook_file
            
            if not hook_path.exists():
                self.logger.warning(f"Hook file not found: {hook_path}")
                continue
            
            try:
                # Initialize hook (this could involve running the hook script)
                hook_state = await self._initialize_hook(hook_path, agent_env)
                hook_states[hook_file] = hook_state
                
            except Exception as e:
                self.logger.error(f"Failed to initialize hook {hook_file}: {e}")
                hook_states[hook_file] = {
                    'status': 'error',
                    'error': str(e),
                    'initialized_at': time.time()
                }
        
        return hook_states
    
    async def _initialize_hook(self, hook_path: Path, env: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize a specific hook."""
        # For now, just validate the hook exists and is executable
        hook_state = {
            'path': str(hook_path),
            'status': 'ready',
            'initialized_at': time.time(),
            'size_bytes': hook_path.stat().st_size,
            'last_modified': hook_path.stat().st_mtime
        }
        
        # Could add more sophisticated hook initialization here
        # such as checking dependencies, validating syntax, etc.
        
        return hook_state
    
    async def activate_agent(self, agent_name: str, session_context: SessionContext) -> bool:
        """Activate an initialized agent."""
        if agent_name not in self.active_agents:
            raise AgentInitializationError(f"Agent {agent_name} not initialized")
        
        agent_state = self.active_agents[agent_name]
        
        try:
            # Update agent state
            agent_state['status'] = 'active'
            agent_state['metrics']['activations'] += 1
            agent_state['metrics']['last_activity'] = time.time()
            
            # Add to session context
            if agent_name not in session_context.active_agents:
                session_context.active_agents.append(agent_name)
            
            self.logger.info(f"Activated agent: {agent_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to activate agent {agent_name}: {e}")
            agent_state['status'] = 'error'
            agent_state['metrics']['errors'] += 1
            return False
    
    async def deactivate_agent(self, agent_name: str, session_context: SessionContext) -> bool:
        """Deactivate an active agent."""
        if agent_name not in self.active_agents:
            return True  # Already not active
        
        agent_state = self.active_agents[agent_name]
        
        try:
            # Update agent state
            agent_state['status'] = 'inactive'
            agent_state['metrics']['last_activity'] = time.time()
            
            # Remove from session context
            if agent_name in session_context.active_agents:
                session_context.active_agents.remove(agent_name)
            
            self.logger.info(f"Deactivated agent: {agent_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to deactivate agent {agent_name}: {e}")
            return False
    
    async def _cleanup_agents(self, agent_names: List[str]):
        """Cleanup agents during error recovery."""
        for agent_name in agent_names:
            try:
                if agent_name in self.active_agents:
                    # Cleanup agent resources
                    del self.active_agents[agent_name]
                    self.logger.info(f"Cleaned up agent: {agent_name}")
            except Exception as e:
                self.logger.error(f"Failed to cleanup agent {agent_name}: {e}")
    
    def get_agent_status(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific agent."""
        return self.active_agents.get(agent_name)
    
    def get_all_agent_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all active agents."""
        return self.active_agents.copy()
    
    def get_available_agents(self) -> Dict[str, Dict[str, Any]]:
        """Get list of all available agent types."""
        return self.agent_definitions.copy()
    
    async def restart_agent(self, agent_name: str, session_config: SessionConfiguration, session_context: SessionContext) -> bool:
        """Restart a failed agent."""
        if agent_name in self.active_agents:
            # Cleanup existing agent
            await self._cleanup_agents([agent_name])
        
        # Find agent configuration
        agent_config = None
        for config in session_config.agents:
            if config.name == agent_name:
                agent_config = config
                break
        
        if not agent_config:
            raise AgentInitializationError(f"Agent configuration not found: {agent_name}")
        
        try:
            # Reinitialize agent
            agent_state = await self._initialize_single_agent(agent_config, session_config, session_context)
            self.logger.info(f"Restarted agent: {agent_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to restart agent {agent_name}: {e}")
            return False