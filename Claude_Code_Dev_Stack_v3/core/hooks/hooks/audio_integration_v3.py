#!/usr/bin/env python3
"""
Audio Integration V3 - Cross-Platform Hook Integration
Seamless integration with Claude Code hooks system for phase-aware audio feedback
"""

import os
import sys
import json
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add the audio system to the path
current_dir = Path(__file__).parent
audio_dir = current_dir.parent.parent / "audio"
sys.path.insert(0, str(audio_dir))

try:
    from phase_aware_audio_manager import (
        PhaseAwareAudioManager, 
        DevelopmentPhase, 
        AudioCategory, 
        AudioPriority,
        get_audio_manager
    )
except ImportError:
    # Fallback if audio manager not available
    class MockAudioManager:
        def queue_event(self, *args, **kwargs): pass
        def operation_start(self, *args, **kwargs): pass
        def operation_complete(self, *args, **kwargs): pass
        def error_occurred(self, *args, **kwargs): pass
        def add_agent(self, *args, **kwargs): pass
        def change_phase(self, *args, **kwargs): pass
    
    def get_audio_manager():
        return MockAudioManager()

class AudioHookIntegration:
    """
    Integration layer between Claude Code hooks and the audio system
    """
    
    def __init__(self):
        self.audio_manager = get_audio_manager()
        self.hook_mappings = self._load_hook_mappings()
        self.agent_mappings = self._load_agent_mappings()
        self.operation_mappings = self._load_operation_mappings()
        
        # State tracking
        self.current_session = f"session_{os.getpid()}"
        self.active_operations = set()
        
    def _load_hook_mappings(self) -> Dict[str, Any]:
        """Load mappings between hook events and audio events"""
        return {
            "PreToolUse": {
                "audio_category": AudioCategory.SYSTEM,
                "priority": AudioPriority.LOW,
                "operation_map": {
                    "Task": "agent_delegation",
                    "Write": "file_write",
                    "Edit": "file_edit",
                    "MultiEdit": "multi_file_edit",
                    "Bash": "command_execution",
                    "Read": "file_read",
                    "Glob": "file_search",
                    "Grep": "content_search"
                }
            },
            "PostToolUse": {
                "audio_category": AudioCategory.SUCCESS,
                "priority": AudioPriority.NORMAL,
                "success_sounds": True
            },
            "SessionStart": {
                "audio_category": AudioCategory.SYSTEM,
                "priority": AudioPriority.HIGH,
                "operation": "session_start",
                "phase": DevelopmentPhase.INITIALIZATION
            },
            "Stop": {
                "audio_category": AudioCategory.SYSTEM,
                "priority": AudioPriority.NORMAL,
                "operation": "session_end"
            },
            "UserPromptSubmit": {
                "audio_category": AudioCategory.NOTIFICATION,
                "priority": AudioPriority.LOW,
                "operation": "user_input"
            },
            "Error": {
                "audio_category": AudioCategory.ERROR,
                "priority": AudioPriority.HIGH,
                "operation": "system_error"
            }
        }
    
    def _load_agent_mappings(self) -> Dict[str, str]:
        """Load mappings between tool names and agent types"""
        return {
            # Agent mentions
            "@agent-master-orchestrator": "master_orchestrator",
            "@agent-frontend-architecture": "frontend_architecture",
            "@agent-backend-architecture": "backend_architecture",
            "@agent-database-architecture": "database_architecture",
            "@agent-mobile-architecture": "mobile_architecture",
            "@agent-production-frontend": "production_frontend",
            "@agent-production-backend": "production_backend",
            "@agent-ui-ux-design": "ui_ux_design",
            "@agent-business-analyst": "business_analyst",
            "@agent-financial-analyst": "financial_analyst",
            "@agent-testing-automation": "testing_automation",
            "@agent-performance-optimization": "performance_optimization",
            "@agent-security-specialist": "security_specialist",
            "@agent-devops-specialist": "devops_specialist",
            "@agent-mobile-development": "mobile_development",
            "@agent-api-development": "api_development",
            "@agent-data-pipeline": "data_pipeline",
            "@agent-ml-specialist": "ml_specialist",
            "@agent-documentation": "documentation",
            "@agent-code-review": "code_review",
            "@agent-frontend-mockup": "frontend_mockup",
            
            # Tool-based detection
            "npm": "frontend_development",
            "yarn": "frontend_development",
            "pip": "backend_development",
            "cargo": "rust_development",
            "go": "go_development",
            "docker": "devops",
            "kubectl": "kubernetes",
            "terraform": "infrastructure",
            "git": "version_control",
            "pytest": "testing",
            "jest": "frontend_testing",
            "webpack": "build_tools",
            "vite": "build_tools"
        }
    
    def _load_operation_mappings(self) -> Dict[str, str]:
        """Load mappings between commands and operations"""
        return {
            # File operations
            "mkdir": "directory_creation",
            "touch": "file_creation", 
            "cp": "file_copy",
            "mv": "file_move",
            "rm": "file_delete",
            
            # Git operations
            "git commit": "git_commit",
            "git push": "git_push",
            "git pull": "git_pull",
            "git merge": "git_merge",
            "git checkout": "git_checkout",
            
            # Build operations
            "npm run build": "npm_build",
            "npm install": "npm_install",
            "pip install": "pip_install",
            "make": "make_build",
            "cargo build": "cargo_build",
            
            # Test operations
            "npm test": "npm_test",
            "pytest": "python_test",
            "jest": "javascript_test",
            
            # Server operations
            "npm run dev": "dev_server",
            "python manage.py runserver": "django_server",
            "rails server": "rails_server"
        }
    
    def process_hook_event(self, hook_event: str, tool_name: Optional[str] = None, 
                          command: Optional[str] = None, result: Optional[str] = None) -> bool:
        """Process a hook event and trigger appropriate audio"""
        
        try:
            # Get hook mapping
            hook_config = self.hook_mappings.get(hook_event, {})
            if not hook_config:
                return False
            
            # Determine agent
            agent = self._detect_agent(tool_name, command)
            
            # Determine operation
            operation = self._detect_operation(tool_name, command, hook_config)
            
            # Determine phase
            phase = self._detect_phase(operation, agent)
            
            # Update phase if needed
            if phase and hook_event == "SessionStart":
                self.audio_manager.change_phase(phase)
            
            # Add agent if detected
            if agent:
                self.audio_manager.add_agent(agent)
            
            # Handle specific hook events
            if hook_event == "PreToolUse":
                self._handle_pre_tool_use(tool_name, command, agent, operation)
            elif hook_event == "PostToolUse":
                self._handle_post_tool_use(tool_name, command, result, agent, operation)
            elif hook_event == "SessionStart":
                self._handle_session_start()
            elif hook_event == "Stop":
                self._handle_session_stop()
            elif hook_event == "Error":
                self._handle_error(tool_name, command, result)
            
            return True
            
        except Exception as e:
            # Fail silently to not interfere with main operation
            if os.environ.get("CLAUDE_AUDIO_DEBUG"):
                print(f"Audio integration error: {e}", file=sys.stderr)
            return False
    
    def _detect_agent(self, tool_name: Optional[str], command: Optional[str]) -> Optional[str]:
        """Detect which agent is being used"""
        
        # Check for explicit agent mentions
        if command:
            for mention, agent in self.agent_mappings.items():
                if mention.startswith("@agent-") and mention in command:
                    return agent
        
        # Check tool-based detection
        if tool_name:
            return self.agent_mappings.get(tool_name.lower())
        
        # Check command-based detection
        if command:
            command_lower = command.lower()
            for cmd_pattern, agent in self.agent_mappings.items():
                if not cmd_pattern.startswith("@") and cmd_pattern in command_lower:
                    return agent
        
        return None
    
    def _detect_operation(self, tool_name: Optional[str], command: Optional[str], 
                         hook_config: Dict[str, Any]) -> str:
        """Detect the current operation"""
        
        # Check hook-specific operation mapping
        if tool_name and "operation_map" in hook_config:
            operation = hook_config["operation_map"].get(tool_name)
            if operation:
                return operation
        
        # Check explicit operation in hook config
        if "operation" in hook_config:
            return hook_config["operation"]
        
        # Check command-based detection
        if command:
            for cmd_pattern, operation in self.operation_mappings.items():
                if cmd_pattern in command.lower():
                    return operation
        
        # Default operation
        return tool_name.lower() if tool_name else "unknown"
    
    def _detect_phase(self, operation: str, agent: Optional[str]) -> Optional[DevelopmentPhase]:
        """Detect the current development phase"""
        
        # Phase detection rules
        phase_indicators = {
            DevelopmentPhase.INITIALIZATION: [
                "session_start", "project_creation", "setup"
            ],
            DevelopmentPhase.PLANNING: [
                "agent_delegation", "master_orchestrator", "business_analyst"
            ],
            DevelopmentPhase.ANALYSIS: [
                "content_search", "file_search", "analyzing", "financial_analyst"
            ],
            DevelopmentPhase.DESIGN: [
                "ui_ux_design", "frontend_mockup", "architecture"
            ],
            DevelopmentPhase.IMPLEMENTATION: [
                "file_write", "file_edit", "frontend_development", "backend_development"
            ],
            DevelopmentPhase.TESTING: [
                "npm_test", "python_test", "javascript_test", "testing_automation"
            ],
            DevelopmentPhase.DEBUGGING: [
                "file_edit", "code_review", "error"
            ],
            DevelopmentPhase.INTEGRATION: [
                "git_merge", "git_commit", "devops"
            ],
            DevelopmentPhase.DEPLOYMENT: [
                "git_push", "docker", "kubernetes", "infrastructure"
            ],
            DevelopmentPhase.MONITORING: [
                "performance_optimization", "security_specialist"
            ]
        }
        
        # Check operation-based phase detection
        for phase, indicators in phase_indicators.items():
            if operation in indicators:
                return phase
            if agent and agent in indicators:
                return phase
        
        return None
    
    def _handle_pre_tool_use(self, tool_name: Optional[str], command: Optional[str], 
                           agent: Optional[str], operation: str):
        """Handle PreToolUse event"""
        
        # Track operation start
        self.active_operations.add(operation)
        self.audio_manager.operation_start(operation, agent)
        
        # Queue low-priority notification
        self.audio_manager.queue_event(
            event_id=f"pre_tool_{operation}_{len(self.active_operations)}",
            category=AudioCategory.SYSTEM,
            priority=AudioPriority.LOW,
            agent=agent,
            operation=operation,
            metadata={
                "tool_name": tool_name,
                "command": command[:100] if command else None  # Truncate long commands
            }
        )
    
    def _handle_post_tool_use(self, tool_name: Optional[str], command: Optional[str], 
                            result: Optional[str], agent: Optional[str], operation: str):
        """Handle PostToolUse event"""
        
        # Determine if operation was successful
        success = self._determine_success(result, command)
        
        # Remove from active operations
        self.active_operations.discard(operation)
        
        # Signal operation completion
        self.audio_manager.operation_complete(operation, success, agent)
        
        # Check for milestones
        milestone = self._check_milestones(tool_name, command, result, success)
        if milestone:
            self.audio_manager.milestone_reached(milestone, agent)
    
    def _handle_session_start(self):
        """Handle session start"""
        self.audio_manager.change_phase(DevelopmentPhase.INITIALIZATION)
        self.audio_manager.operation_start("session_start")
        self.audio_manager.operation_complete("session_start", True)
    
    def _handle_session_stop(self):
        """Handle session stop"""
        self.audio_manager.operation_start("session_end")
        self.audio_manager.operation_complete("session_end", True)
    
    def _handle_error(self, tool_name: Optional[str], command: Optional[str], 
                     result: Optional[str]):
        """Handle error event"""
        
        error_type = tool_name or "unknown"
        severity = self._determine_error_severity(result)
        
        self.audio_manager.error_occurred(error_type, severity)
    
    def _determine_success(self, result: Optional[str], command: Optional[str]) -> bool:
        """Determine if an operation was successful"""
        
        if not result:
            return True  # Assume success if no result
        
        result_lower = result.lower()
        
        # Error indicators
        error_indicators = [
            "error", "failed", "exception", "traceback", 
            "command not found", "permission denied", "no such file"
        ]
        
        for indicator in error_indicators:
            if indicator in result_lower:
                return False
        
        # Success indicators
        success_indicators = [
            "success", "completed", "done", "ok", "passed"
        ]
        
        for indicator in success_indicators:
            if indicator in result_lower:
                return True
        
        # Default to success
        return True
    
    def _determine_error_severity(self, result: Optional[str]) -> str:
        """Determine error severity from result"""
        
        if not result:
            return "normal"
        
        result_lower = result.lower()
        
        if any(word in result_lower for word in ["critical", "fatal", "segmentation fault"]):
            return "critical"
        elif any(word in result_lower for word in ["warning", "deprecated"]):
            return "low"
        else:
            return "normal"
    
    def _check_milestones(self, tool_name: Optional[str], command: Optional[str], 
                         result: Optional[str], success: bool) -> Optional[str]:
        """Check if a milestone was reached"""
        
        if not success:
            return None
        
        milestone_patterns = {
            "project_setup": ["npm init", "cargo new", "git init"],
            "dependencies_installed": ["npm install", "pip install", "cargo build"],
            "tests_passing": ["test", "jest", "pytest"],
            "build_successful": ["build", "compile"],
            "deployment_complete": ["deploy", "push", "publish"],
            "git_milestone": ["git push", "git merge"]
        }
        
        if command:
            command_lower = command.lower()
            for milestone, patterns in milestone_patterns.items():
                if any(pattern in command_lower for pattern in patterns):
                    return milestone
        
        return None

# Global instance
_hook_integration = None

def get_hook_integration() -> AudioHookIntegration:
    """Get the global hook integration instance"""
    global _hook_integration
    if _hook_integration is None:
        _hook_integration = AudioHookIntegration()
    return _hook_integration

def process_hook_stdin():
    """Process hook input from stdin (standard hook format)"""
    try:
        # Read hook data from stdin
        hook_data = json.loads(sys.stdin.read())
        
        hook_event = hook_data.get("hook_event_name", "")
        tool_name = hook_data.get("tool_name")
        command = hook_data.get("command")
        result = hook_data.get("result")
        
        # Get environment variables that might contain additional info
        tool_name = tool_name or os.environ.get("CLAUDE_TOOL_NAME")
        command = command or os.environ.get("CLAUDE_COMMAND")
        
        # Process the hook event
        integration = get_hook_integration()
        success = integration.process_hook_event(hook_event, tool_name, command, result)
        
        if os.environ.get("CLAUDE_AUDIO_DEBUG"):
            print(f"Processed {hook_event} -> {success}", file=sys.stderr)
        
    except Exception as e:
        if os.environ.get("CLAUDE_AUDIO_DEBUG"):
            print(f"Hook processing error: {e}", file=sys.stderr)

def main():
    """Main entry point for hook integration"""
    
    # Check if we're being called as a hook
    if len(sys.argv) > 1:
        hook_event = sys.argv[1]
        tool_name = sys.argv[2] if len(sys.argv) > 2 else None
        command = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else None
        
        integration = get_hook_integration()
        integration.process_hook_event(hook_event, tool_name, command)
    else:
        # Process from stdin (standard hook format)
        process_hook_stdin()

if __name__ == "__main__":
    main()