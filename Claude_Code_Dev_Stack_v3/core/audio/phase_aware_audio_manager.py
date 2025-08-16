#!/usr/bin/env python3
"""
Phase-Aware Audio Manager for Claude Code Dev Stack
Intelligent audio feedback system with context-aware notifications and cross-platform compatibility
"""

import os
import sys
import json
import time
import platform
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from contextlib import contextmanager

# Platform-specific imports
if platform.system() == "Windows":
    try:
        import winsound
    except ImportError:
        winsound = None

class DevelopmentPhase(Enum):
    INITIALIZATION = "initialization"
    PLANNING = "planning" 
    ANALYSIS = "analysis"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    DEBUGGING = "debugging"
    INTEGRATION = "integration"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    MAINTENANCE = "maintenance"

class AudioPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class AudioCategory(Enum):
    SYSTEM = "system"
    AGENT = "agent"
    PHASE = "phase"
    ERROR = "error"
    WARNING = "warning"
    SUCCESS = "success"
    NOTIFICATION = "notification"

@dataclass
class AudioEvent:
    event_id: str
    category: AudioCategory
    priority: AudioPriority
    phase: DevelopmentPhase
    agent: Optional[str]
    operation: str
    timestamp: float
    metadata: Dict[str, Any]
    audio_file: Optional[str] = None
    played: bool = False

@dataclass
class PhaseContext:
    current_phase: DevelopmentPhase
    active_agents: List[str]
    current_operation: str
    session_id: str
    platform: str
    user_preferences: Dict[str, Any]
    start_time: float

class PhaseAwareAudioManager:
    """
    Intelligent audio manager that provides context-aware notifications
    based on development phase, active agents, and current operations
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.audio_dir = self.base_dir / "audio"
        self.config_dir = self.base_dir / "config"
        self.state_dir = self.base_dir / "state"
        
        # Create directories
        for dir_path in [self.config_dir, self.state_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Platform detection
        self.platform = platform.system()
        
        # Load configurations
        self.config = self._load_configuration()
        self.audio_mapping = self._load_audio_mapping()
        self.phase_config = self._load_phase_configuration()
        
        # Current context
        self.current_context = self._initialize_context()
        
        # Event queue and history
        self.event_queue = []
        self.event_history = []
        self.queue_lock = threading.Lock()
        
        # Background processor
        self.processor_thread = None
        self.running = False
        
        # Audio player cache
        self.audio_players = self._detect_audio_players()
        
        print(f"Phase-Aware Audio Manager initialized for {self.platform}")
        self._start_background_processor()
    
    def _load_configuration(self) -> Dict[str, Any]:
        """Load main audio configuration"""
        config_file = self.config_dir / "audio_manager_config.json"
        
        default_config = {
            "enabled": True,
            "volume": 0.7,
            "max_queue_size": 50,
            "event_timeout_seconds": 300,
            "concurrent_playback": False,
            "phase_transitions": True,
            "agent_notifications": True,
            "error_emphasis": True,
            "success_celebrations": True,
            "debug_mode": False,
            "user_preferences": {
                "notification_frequency": "normal",
                "quiet_hours": {"enabled": False, "start": "22:00", "end": "08:00"},
                "priority_filter": "normal",
                "categories": {
                    "system": True,
                    "agent": True,
                    "phase": True,
                    "error": True,
                    "warning": True,
                    "success": True,
                    "notification": True
                }
            }
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    loaded_config = json.load(f)
                # Merge with defaults
                default_config.update(loaded_config)
            except Exception as e:
                print(f"Error loading config: {e}, using defaults")
        
        return default_config
    
    def _load_audio_mapping(self) -> Dict[str, Any]:
        """Load audio file mappings for different contexts"""
        mapping_file = self.config_dir / "audio_mapping.json"
        
        default_mapping = {
            "phases": {
                "initialization": ["startup.wav", "project_created.wav"],
                "planning": ["phase_planning.wav", "analyzing.wav"],
                "analysis": ["analyzing_code.wav", "processing.wav"],
                "design": ["generating_code.wav", "planning_complete.wav"],
                "implementation": ["phase_implementation.wav", "working.wav"],
                "testing": ["phase_testing.wav", "running_tests.wav"],
                "debugging": ["analyzing.wav", "reviewing_changes.wav"],
                "integration": ["orchestration_started.wav", "parallel_execution.wav"],
                "deployment": ["phase_deployment.wav", "build_successful.wav"],
                "monitoring": ["dashboard_started.wav", "status_update.wav"],
                "maintenance": ["optimizing_performance.wav", "quality_gate_passed.wav"]
            },
            "agents": {
                "master_orchestrator": ["master_orchestrator.wav", "orchestration_started.wav"],
                "frontend": ["frontend_agent.wav", "generating_code.wav"],
                "backend": ["backend_agent.wav", "processing.wav"],
                "database": ["database_agent.wav", "analyzing.wav"],
                "mobile": ["agent_activated.wav", "working.wav"],
                "testing": ["running_tests.wav", "analyzing.wav"],
                "security": ["security_scanning.wav", "analyzing.wav"],
                "performance": ["optimizing_performance.wav", "analyzing.wav"]
            },
            "operations": {
                "file_create": ["touch_operation.wav", "file_operation_complete.wav"],
                "file_edit": ["file_operation_pending.wav", "file_operation_complete.wav"],
                "file_delete": ["delete_operation.wav", "operation_complete.wav"],
                "directory_create": ["mkdir_operation.wav", "operation_complete.wav"],
                "git_commit": ["git_commit.wav", "operation_complete.wav"],
                "git_push": ["git_push.wav", "operation_complete.wav"],
                "build": ["npm_build.wav", "build_successful.wav"],
                "test": ["running_tests.wav", "tests_passed.wav"],
                "deploy": ["phase_deployment.wav", "operation_complete.wav"]
            },
            "events": {
                "success": ["operation_complete.wav", "build_successful.wav", "tests_passed.wav"],
                "error": ["command_failed.wav", "tests_failed.wav", "connection_error.wav"],
                "warning": ["risky_command.wav", "token_warning.wav", "performance_warning.wav"],
                "notification": ["notification_sent.wav", "status_update.wav"],
                "milestone": ["milestone_complete.wav", "phase_complete.wav"],
                "handoff": ["handoff_generated.wav", "context_saved.wav"]
            }
        }
        
        if mapping_file.exists():
            try:
                with open(mapping_file, 'r') as f:
                    loaded_mapping = json.load(f)
                # Merge with defaults
                default_mapping.update(loaded_mapping)
            except Exception as e:
                print(f"Error loading audio mapping: {e}, using defaults")
        
        return default_mapping
    
    def _load_phase_configuration(self) -> Dict[str, Any]:
        """Load phase-specific audio configuration"""
        phase_config_file = self.config_dir / "phase_audio_config.json"
        
        default_phase_config = {
            "phase_transitions": {
                "enabled": True,
                "volume_boost": 0.2,
                "celebratory_sounds": True
            },
            "phase_specific_settings": {
                "initialization": {"frequency": "high", "volume": 0.8},
                "planning": {"frequency": "normal", "volume": 0.6},
                "analysis": {"frequency": "low", "volume": 0.5},
                "design": {"frequency": "normal", "volume": 0.6},
                "implementation": {"frequency": "normal", "volume": 0.5},
                "testing": {"frequency": "high", "volume": 0.7},
                "debugging": {"frequency": "high", "volume": 0.8},
                "integration": {"frequency": "normal", "volume": 0.7},
                "deployment": {"frequency": "high", "volume": 0.9},
                "monitoring": {"frequency": "low", "volume": 0.4},
                "maintenance": {"frequency": "low", "volume": 0.4}
            },
            "agent_integration": {
                "multi_agent_coordination": True,
                "agent_handoff_sounds": True,
                "parallel_execution_audio": True
            }
        }
        
        if phase_config_file.exists():
            try:
                with open(phase_config_file, 'r') as f:
                    loaded_config = json.load(f)
                default_phase_config.update(loaded_config)
            except Exception as e:
                print(f"Error loading phase config: {e}, using defaults")
        
        return default_phase_config
    
    def _initialize_context(self) -> PhaseContext:
        """Initialize the current phase context"""
        return PhaseContext(
            current_phase=DevelopmentPhase.INITIALIZATION,
            active_agents=[],
            current_operation="startup",
            session_id=f"session_{int(time.time())}",
            platform=self.platform,
            user_preferences=self.config.get("user_preferences", {}),
            start_time=time.time()
        )
    
    def _detect_audio_players(self) -> List[str]:
        """Detect available audio players on the current platform"""
        players = []
        
        if self.platform == "Windows":
            if winsound:
                players.append("winsound")
        elif self.platform == "Darwin":
            if self._command_available("afplay"):
                players.append("afplay")
        else:  # Linux
            for player in ["aplay", "paplay", "play", "mpg123"]:
                if self._command_available(player):
                    players.append(player)
        
        return players
    
    def _command_available(self, command: str) -> bool:
        """Check if a command is available"""
        try:
            subprocess.run(["which", command], capture_output=True, timeout=2)
            return True
        except:
            return False
    
    def _start_background_processor(self):
        """Start the background event processor"""
        self.running = True
        self.processor_thread = threading.Thread(target=self._process_events, daemon=True)
        self.processor_thread.start()
    
    def _process_events(self):
        """Background event processor"""
        while self.running:
            try:
                with self.queue_lock:
                    if self.event_queue:
                        event = self.event_queue.pop(0)
                        self._handle_audio_event(event)
                
                time.sleep(0.1)  # Small delay to prevent busy waiting
            except Exception as e:
                if self.config.get("debug_mode"):
                    print(f"Event processor error: {e}")
    
    def _handle_audio_event(self, event: AudioEvent):
        """Handle a single audio event"""
        try:
            if not self._should_play_event(event):
                return
            
            audio_file = self._select_audio_file(event)
            if audio_file:
                self._play_audio_file(audio_file, event)
                event.played = True
                event.audio_file = audio_file
            
            # Add to history
            self.event_history.append(event)
            
            # Cleanup old events
            self._cleanup_old_events()
            
        except Exception as e:
            if self.config.get("debug_mode"):
                print(f"Error handling audio event: {e}")
    
    def _should_play_event(self, event: AudioEvent) -> bool:
        """Determine if an event should play audio"""
        
        # Check if audio is enabled
        if not self.config.get("enabled", True):
            return False
        
        # Check category filter
        categories = self.config.get("user_preferences", {}).get("categories", {})
        if not categories.get(event.category.value, True):
            return False
        
        # Check priority filter
        priority_filter = self.config.get("user_preferences", {}).get("priority_filter", "normal")
        min_priority = {
            "low": AudioPriority.LOW,
            "normal": AudioPriority.NORMAL,
            "high": AudioPriority.HIGH,
            "critical": AudioPriority.CRITICAL
        }.get(priority_filter, AudioPriority.NORMAL)
        
        if event.priority.value < min_priority.value:
            return False
        
        # Check quiet hours
        quiet_hours = self.config.get("user_preferences", {}).get("quiet_hours", {})
        if quiet_hours.get("enabled", False):
            # Implementation would check current time against quiet hours
            pass
        
        # Check frequency limits
        frequency = self.config.get("user_preferences", {}).get("notification_frequency", "normal")
        if frequency == "minimal" and event.priority != AudioPriority.CRITICAL:
            # Only play critical events in minimal mode
            return event.priority == AudioPriority.CRITICAL
        
        return True
    
    def _select_audio_file(self, event: AudioEvent) -> Optional[str]:
        """Select appropriate audio file for the event"""
        
        # Check for phase-specific audio
        phase_audio = self.audio_mapping.get("phases", {}).get(event.phase.value, [])
        
        # Check for agent-specific audio
        agent_audio = []
        if event.agent:
            agent_audio = self.audio_mapping.get("agents", {}).get(event.agent.lower(), [])
        
        # Check for operation-specific audio
        operation_audio = self.audio_mapping.get("operations", {}).get(event.operation, [])
        
        # Check for event category audio
        category_audio = self.audio_mapping.get("events", {}).get(event.category.value, [])
        
        # Priority order: operation -> agent -> phase -> category
        for audio_list in [operation_audio, agent_audio, phase_audio, category_audio]:
            for audio_file in audio_list:
                audio_path = self.audio_dir / audio_file
                if audio_path.exists():
                    return str(audio_path)
        
        return None
    
    def _play_audio_file(self, audio_file: str, event: AudioEvent):
        """Play an audio file"""
        try:
            # Get volume for this phase
            phase_settings = self.phase_config.get("phase_specific_settings", {}).get(event.phase.value, {})
            volume = phase_settings.get("volume", self.config.get("volume", 0.7))
            
            if self.platform == "Windows" and "winsound" in self.audio_players:
                self._play_windows_audio(audio_file, volume)
            elif self.platform == "Darwin" and "afplay" in self.audio_players:
                self._play_macos_audio(audio_file, volume)
            else:
                self._play_linux_audio(audio_file, volume)
                
            if self.config.get("debug_mode"):
                print(f"Played {Path(audio_file).name} for {event.category.value} event")
                
        except Exception as e:
            if self.config.get("debug_mode"):
                print(f"Error playing audio file {audio_file}: {e}")
    
    def _play_windows_audio(self, audio_file: str, volume: float):
        """Play audio on Windows"""
        if winsound:
            # Windows doesn't support volume control via winsound
            winsound.PlaySound(audio_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
    
    def _play_macos_audio(self, audio_file: str, volume: float):
        """Play audio on macOS"""
        subprocess.Popen([
            "afplay", audio_file, "-v", str(volume)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    def _play_linux_audio(self, audio_file: str, volume: float):
        """Play audio on Linux"""
        for player in self.audio_players:
            try:
                if player == "aplay":
                    subprocess.Popen([player, audio_file], 
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                elif player == "paplay":
                    subprocess.Popen([player, "--volume", str(int(volume * 65536)), audio_file],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    subprocess.Popen([player, audio_file],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                break
            except:
                continue
    
    def _cleanup_old_events(self):
        """Cleanup old events from history"""
        timeout = self.config.get("event_timeout_seconds", 300)
        current_time = time.time()
        
        self.event_history = [
            event for event in self.event_history
            if current_time - event.timestamp < timeout
        ]
    
    # Public API Methods
    
    def queue_event(self, 
                   event_id: str,
                   category: AudioCategory,
                   priority: AudioPriority = AudioPriority.NORMAL,
                   agent: Optional[str] = None,
                   operation: str = "unknown",
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """Queue an audio event"""
        
        event = AudioEvent(
            event_id=event_id,
            category=category,
            priority=priority,
            phase=self.current_context.current_phase,
            agent=agent,
            operation=operation,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        
        with self.queue_lock:
            if len(self.event_queue) < self.config.get("max_queue_size", 50):
                self.event_queue.append(event)
            else:
                # Remove oldest low-priority event
                for i, queued_event in enumerate(self.event_queue):
                    if queued_event.priority == AudioPriority.LOW:
                        self.event_queue.pop(i)
                        self.event_queue.append(event)
                        break
        
        return event.event_id
    
    def change_phase(self, new_phase: DevelopmentPhase):
        """Change the current development phase"""
        old_phase = self.current_context.current_phase
        self.current_context.current_phase = new_phase
        
        # Queue phase transition event
        if self.phase_config.get("phase_transitions", {}).get("enabled", True):
            self.queue_event(
                event_id=f"phase_transition_{int(time.time())}",
                category=AudioCategory.PHASE,
                priority=AudioPriority.HIGH,
                operation="phase_transition",
                metadata={
                    "old_phase": old_phase.value,
                    "new_phase": new_phase.value
                }
            )
        
        # Save context
        self._save_context()
    
    def add_agent(self, agent_name: str):
        """Add an active agent"""
        if agent_name not in self.current_context.active_agents:
            self.current_context.active_agents.append(agent_name)
            
            # Queue agent activation event
            self.queue_event(
                event_id=f"agent_activate_{agent_name}_{int(time.time())}",
                category=AudioCategory.AGENT,
                priority=AudioPriority.NORMAL,
                agent=agent_name,
                operation="agent_activate"
            )
    
    def remove_agent(self, agent_name: str):
        """Remove an active agent"""
        if agent_name in self.current_context.active_agents:
            self.current_context.active_agents.remove(agent_name)
            
            # Queue agent deactivation event
            self.queue_event(
                event_id=f"agent_deactivate_{agent_name}_{int(time.time())}",
                category=AudioCategory.AGENT,
                priority=AudioPriority.LOW,
                agent=agent_name,
                operation="agent_deactivate"
            )
    
    def operation_start(self, operation: str, agent: Optional[str] = None):
        """Signal the start of an operation"""
        self.current_context.current_operation = operation
        
        self.queue_event(
            event_id=f"op_start_{operation}_{int(time.time())}",
            category=AudioCategory.SYSTEM,
            priority=AudioPriority.LOW,
            agent=agent,
            operation=f"{operation}_start"
        )
    
    def operation_complete(self, operation: str, success: bool = True, agent: Optional[str] = None):
        """Signal the completion of an operation"""
        category = AudioCategory.SUCCESS if success else AudioCategory.ERROR
        priority = AudioPriority.NORMAL if success else AudioPriority.HIGH
        
        self.queue_event(
            event_id=f"op_complete_{operation}_{int(time.time())}",
            category=category,
            priority=priority,
            agent=agent,
            operation=f"{operation}_complete",
            metadata={"success": success}
        )
    
    def error_occurred(self, error_type: str, severity: str = "normal", agent: Optional[str] = None):
        """Signal an error occurred"""
        priority_map = {
            "low": AudioPriority.LOW,
            "normal": AudioPriority.HIGH,
            "high": AudioPriority.CRITICAL,
            "critical": AudioPriority.CRITICAL
        }
        
        self.queue_event(
            event_id=f"error_{error_type}_{int(time.time())}",
            category=AudioCategory.ERROR,
            priority=priority_map.get(severity, AudioPriority.HIGH),
            agent=agent,
            operation="error",
            metadata={"error_type": error_type, "severity": severity}
        )
    
    def milestone_reached(self, milestone: str, agent: Optional[str] = None):
        """Signal a milestone was reached"""
        self.queue_event(
            event_id=f"milestone_{milestone}_{int(time.time())}",
            category=AudioCategory.SUCCESS,
            priority=AudioPriority.HIGH,
            agent=agent,
            operation="milestone",
            metadata={"milestone": milestone}
        )
    
    def _save_context(self):
        """Save current context to file"""
        try:
            context_file = self.state_dir / "current_context.json"
            with open(context_file, 'w') as f:
                json.dump(asdict(self.current_context), f, indent=2, default=str)
        except Exception as e:
            if self.config.get("debug_mode"):
                print(f"Error saving context: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current manager status"""
        return {
            "enabled": self.config.get("enabled", True),
            "current_phase": self.current_context.current_phase.value,
            "active_agents": self.current_context.active_agents,
            "current_operation": self.current_context.current_operation,
            "queue_size": len(self.event_queue),
            "history_size": len(self.event_history),
            "available_players": self.audio_players,
            "platform": self.platform
        }
    
    def shutdown(self):
        """Shutdown the audio manager"""
        self.running = False
        if self.processor_thread:
            self.processor_thread.join(timeout=2)
        
        # Save final context
        self._save_context()

# Context manager for easy usage
@contextmanager
def audio_context(manager: PhaseAwareAudioManager, 
                 phase: DevelopmentPhase, 
                 operation: str,
                 agent: Optional[str] = None):
    """Context manager for audio operations"""
    try:
        old_phase = manager.current_context.current_phase
        manager.change_phase(phase)
        manager.operation_start(operation, agent)
        yield manager
    finally:
        manager.operation_complete(operation, True, agent)
        if old_phase != phase:
            manager.change_phase(old_phase)

# Global instance
_global_manager = None

def get_audio_manager() -> PhaseAwareAudioManager:
    """Get the global audio manager instance"""
    global _global_manager
    if _global_manager is None:
        _global_manager = PhaseAwareAudioManager()
    return _global_manager

# Convenience functions
def play_system_sound(operation: str, success: bool = True):
    """Play a system sound"""
    manager = get_audio_manager()
    if success:
        manager.operation_complete(operation, True)
    else:
        manager.error_occurred(operation)

def play_agent_sound(agent: str, operation: str):
    """Play an agent-specific sound"""
    manager = get_audio_manager()
    manager.add_agent(agent)
    manager.operation_start(operation, agent)

def play_phase_sound(phase: DevelopmentPhase):
    """Play a phase transition sound"""
    manager = get_audio_manager()
    manager.change_phase(phase)

if __name__ == "__main__":
    # Example usage
    manager = PhaseAwareAudioManager()
    
    # Simulate development workflow
    manager.change_phase(DevelopmentPhase.PLANNING)
    manager.add_agent("master_orchestrator")
    manager.operation_start("project_analysis", "master_orchestrator")
    
    time.sleep(1)
    
    manager.operation_complete("project_analysis", True, "master_orchestrator")
    manager.milestone_reached("requirements_complete")
    
    time.sleep(2)
    
    manager.change_phase(DevelopmentPhase.IMPLEMENTATION)
    manager.add_agent("frontend_agent")
    manager.operation_start("component_creation", "frontend_agent")
    
    time.sleep(1)
    
    manager.operation_complete("component_creation", True, "frontend_agent")
    
    print(json.dumps(manager.get_status(), indent=2))
    
    manager.shutdown()