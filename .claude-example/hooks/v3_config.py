#!/usr/bin/env python3
"""
Claude Code v3.0 Configuration Management
Centralized configuration for all v3.0 components
"""

import json
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass, asdict

@dataclass
class StatusLineConfig:
    """Status line configuration"""
    update_frequency: int = 100  # milliseconds
    websocket_port: int = 8080
    sqlite_path: str = "~/.claude/v3/status_history.db"
    redis_host: str = "localhost"
    redis_port: int = 6379
    enable_redis: bool = True
    enable_websocket: bool = True
    enable_polling_fallback: bool = True

@dataclass
class ContextManagerConfig:
    """Context manager configuration"""
    retention_policy_days: int = 30
    agent_states_retention_days: int = 7
    project_states_retention_days: int = 90
    snapshots_retention_days: int = 14
    suggest_compact_threshold: float = 0.8
    require_compact_threshold: float = 0.9
    emergency_compact_threshold: float = 0.95
    enable_automatic_optimization: bool = True
    enable_intelligent_handoffs: bool = True

@dataclass  
class ChatManagerConfig:
    """Chat manager configuration"""
    token_suggest_compact: float = 0.8
    token_require_compact: float = 0.9
    token_emergency_handoff: float = 0.95
    conversation_depth_threshold: int = 20
    context_complexity_threshold: float = 0.85
    enable_automatic_handoffs: bool = True
    enable_phase_detection: bool = True
    enable_continuity_monitoring: bool = True

@dataclass
class OrchestratorConfig:
    """Main orchestrator configuration"""
    enable_status_line_integration: bool = True
    enable_context_preservation: bool = True
    enable_intelligent_handoffs: bool = True
    enable_legacy_compatibility: bool = True
    enable_real_time_coordination: bool = True
    coordination_interval_seconds: int = 5
    enable_performance_monitoring: bool = True

@dataclass
class V3Config:
    """Complete v3.0 system configuration"""
    version: str = "3.0"
    status_line: StatusLineConfig = None
    context_manager: ContextManagerConfig = None
    chat_manager: ChatManagerConfig = None
    orchestrator: OrchestratorConfig = None
    
    def __post_init__(self):
        if self.status_line is None:
            self.status_line = StatusLineConfig()
        if self.context_manager is None:
            self.context_manager = ContextManagerConfig()
        if self.chat_manager is None:
            self.chat_manager = ChatManagerConfig()
        if self.orchestrator is None:
            self.orchestrator = OrchestratorConfig()

class V3ConfigManager:
    """Configuration manager for v3.0 system"""
    
    def __init__(self):
        self.config_path = Path.home() / ".claude" / "v3" / "config.json"
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config = self.load_config()
    
    def load_config(self) -> V3Config:
        """Load configuration from file or create default"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                
                # Reconstruct config object
                config = V3Config()
                
                if 'status_line' in config_data:
                    config.status_line = StatusLineConfig(**config_data['status_line'])
                if 'context_manager' in config_data:
                    config.context_manager = ContextManagerConfig(**config_data['context_manager'])
                if 'chat_manager' in config_data:
                    config.chat_manager = ChatManagerConfig(**config_data['chat_manager'])
                if 'orchestrator' in config_data:
                    config.orchestrator = OrchestratorConfig(**config_data['orchestrator'])
                
                return config
                
            except Exception:
                # Fall back to default config if loading fails
                pass
        
        # Create and save default config
        default_config = V3Config()
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config: V3Config = None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        config_data = {
            'version': config.version,
            'status_line': asdict(config.status_line),
            'context_manager': asdict(config.context_manager),
            'chat_manager': asdict(config.chat_manager),
            'orchestrator': asdict(config.orchestrator)
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def get_config(self) -> V3Config:
        """Get current configuration"""
        return self.config
    
    def update_config(self, **kwargs):
        """Update configuration values"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                if isinstance(value, dict):
                    # Update nested config
                    nested_config = getattr(self.config, key)
                    for nested_key, nested_value in value.items():
                        if hasattr(nested_config, nested_key):
                            setattr(nested_config, nested_key, nested_value)
                else:
                    setattr(self.config, key, value)
        
        self.save_config()

# Global config manager instance
config_manager = None

def get_config_manager():
    """Get or create config manager instance"""
    global config_manager
    if config_manager is None:
        config_manager = V3ConfigManager()
    return config_manager

def get_config() -> V3Config:
    """Get current v3.0 configuration"""
    return get_config_manager().get_config()

# Export for other modules
__all__ = [
    'V3Config', 'StatusLineConfig', 'ContextManagerConfig', 
    'ChatManagerConfig', 'OrchestratorConfig', 'V3ConfigManager',
    'get_config_manager', 'get_config'
]