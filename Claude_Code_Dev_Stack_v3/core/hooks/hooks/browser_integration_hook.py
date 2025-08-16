#!/usr/bin/env python3
"""
Claude Code Browser Integration Hook
===================================

Hook for integrating @zainhoda/claude-code-browser with Dev Stack v3.0 hooks system.
Provides seamless integration between browser monitoring and Dev Stack orchestration.

Attribution:
- Original Claude Code Browser by @zainhoda (AGPL-3.0)
- Hook integration by Claude Code Dev Stack v3.0 (AGPL-3.0)
"""

import os
import json
import asyncio
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Import browser adapter
try:
    from ..integrations.browser_adapter import get_browser_adapter, start_browser_integration
    BROWSER_ADAPTER_AVAILABLE = True
except ImportError:
    BROWSER_ADAPTER_AVAILABLE = False
    print("Browser adapter not available - install required dependencies")

# Import Dev Stack components
try:
    from .v3_orchestrator import get_v3_orchestrator
    from .status_line_manager import get_status_line
    from .context_manager import get_context_manager
    from .chat_manager import get_chat_manager
except ImportError:
    # Fallback for standalone testing
    def get_v3_orchestrator():
        return None
    def get_status_line():
        return None
    def get_context_manager():
        return None
    def get_chat_manager():
        return None

class BrowserIntegrationHook:
    """
    Hook for integrating Claude Code Browser with Dev Stack v3.0
    
    Provides:
    - Automatic browser monitoring activation
    - Real-time session updates
    - Command parsing and execution
    - Integration with Dev Stack orchestration
    """
    
    def __init__(self):
        self.hook_name = "browser_integration"
        self.hook_version = "3.0"
        self.is_active = False
        
        # Integration components
        self.browser_adapter = None
        self.v3_orchestrator = get_v3_orchestrator()
        self.status_line = get_status_line()
        self.context_manager = get_context_manager()
        self.chat_manager = get_chat_manager()
        
        # Configuration
        self.config = {
            "auto_start": True,
            "websocket_port": 8081,
            "http_port": 8082,
            "monitor_sessions": True,
            "parse_commands": True,
            "real_time_updates": True,
            "integration_enabled": BROWSER_ADAPTER_AVAILABLE
        }
        
        # Event handlers
        self.event_handlers = {
            "user_prompt": self._handle_user_prompt,
            "claude_response": self._handle_claude_response,
            "session_started": self._handle_session_started,
            "session_ended": self._handle_session_ended,
            "agent_activation": self._handle_agent_activation,
            "orchestration_request": self._handle_orchestration_request,
            "context_update": self._handle_context_update,
            "browser_command_detected": self._handle_browser_command
        }
        
        # Statistics
        self.stats = {
            "events_processed": 0,
            "commands_parsed": 0,
            "browser_sessions_monitored": 0,
            "integration_events": 0,
            "errors": 0
        }
        
        # Background tasks
        self.background_tasks = []
        self.task_loop = None
        
        # Initialize if auto-start enabled
        if self.config["auto_start"] and BROWSER_ADAPTER_AVAILABLE:
            self._initialize_integration()
    
    def _initialize_integration(self):
        """Initialize browser integration"""
        try:
            if not BROWSER_ADAPTER_AVAILABLE:
                print("Browser adapter not available - skipping initialization")
                return False
            
            # Get browser adapter
            self.browser_adapter = get_browser_adapter(
                websocket_port=self.config["websocket_port"],
                http_port=self.config["http_port"]
            )
            
            # Start background integration
            self._start_background_tasks()
            
            # Update status
            if self.status_line:
                self.status_line.update_status(
                    "browser_integration",
                    "initialized",
                    {
                        "adapter_available": True,
                        "websocket_port": self.config["websocket_port"],
                        "http_port": self.config["http_port"]
                    }
                )
            
            self.is_active = True
            print(f"Browser integration initialized - WebSocket: {self.config['websocket_port']}, HTTP: {self.config['http_port']}")
            return True
            
        except Exception as e:
            print(f"Failed to initialize browser integration: {e}")
            self.stats["errors"] += 1
            return False
    
    def _start_background_tasks(self):
        """Start background integration tasks"""
        if not self.browser_adapter:
            return
        
        # Start monitoring task
        monitoring_task = threading.Thread(target=self._monitoring_task, daemon=True)
        monitoring_task.start()
        self.background_tasks.append(monitoring_task)
        
        # Start WebSocket/HTTP servers in background
        server_task = threading.Thread(target=self._start_servers, daemon=True)
        server_task.start()
        self.background_tasks.append(server_task)
    
    def _start_servers(self):
        """Start WebSocket and HTTP servers"""
        try:
            # Create event loop for async operations
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.task_loop = loop
            
            # Start browser integration servers
            loop.run_until_complete(
                start_browser_integration(
                    websocket_port=self.config["websocket_port"],
                    http_port=self.config["http_port"]
                )
            )
            
        except Exception as e:
            print(f"Failed to start browser integration servers: {e}")
            self.stats["errors"] += 1
    
    def _monitoring_task(self):
        """Background monitoring task"""
        while self.is_active:
            try:
                if self.browser_adapter:
                    # Get integration status
                    status = self.browser_adapter.get_integration_status()
                    
                    # Update statistics
                    self.stats["browser_sessions_monitored"] = status["cache_info"]["sessions"]
                    
                    # Update status line
                    if self.status_line:
                        self.status_line.update_status(
                            "browser_monitor",
                            "active",
                            {
                                "projects": status["cache_info"]["projects"],
                                "sessions": status["cache_info"]["sessions"],
                                "websocket_connections": status["websocket_info"]["connections"]
                            }
                        )
                
                # Sleep for monitoring interval
                threading.Event().wait(10)  # Monitor every 10 seconds
                
            except Exception as e:
                print(f"Monitoring task error: {e}")
                self.stats["errors"] += 1
                threading.Event().wait(10)
    
    def process_hook_event(self, event_type: str, event_data: Dict) -> Dict:
        """Process hook event with browser integration"""
        self.stats["events_processed"] += 1
        
        result = {
            "hook_name": self.hook_name,
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "processed": False,
            "browser_integration": False,
            "enhancements": []
        }
        
        try:
            # Check if handler exists for event type
            if event_type in self.event_handlers:
                handler_result = self.event_handlers[event_type](event_data)
                result.update(handler_result)
                result["processed"] = True
            
            # Parse browser commands if content available
            if self.config["parse_commands"] and self._has_content(event_data):
                command_parsing_result = self._parse_browser_commands(event_data)
                if command_parsing_result["commands_found"]:
                    result["browser_commands"] = command_parsing_result
                    result["enhancements"].append("command_parsing")
                    self.stats["commands_parsed"] += command_parsing_result["command_count"]
            
            # Check for browser integration opportunities
            integration_result = self._check_integration_opportunities(event_type, event_data)
            if integration_result["integration_possible"]:
                result["integration_opportunities"] = integration_result
                result["enhancements"].append("integration_opportunities")
            
            # Update browser session context if available
            if self.browser_adapter and self.config["monitor_sessions"]:
                session_update_result = self._update_browser_session_context(event_data)
                if session_update_result["context_updated"]:
                    result["browser_session_context"] = session_update_result
                    result["enhancements"].append("session_context")
                    result["browser_integration"] = True
            
            # Trigger real-time updates if configured
            if self.config["real_time_updates"] and result["browser_integration"]:
                self._trigger_real_time_update(event_type, event_data, result)
                result["enhancements"].append("real_time_updates")
            
        except Exception as e:
            result["error"] = str(e)
            result["error_timestamp"] = datetime.now().isoformat()
            self.stats["errors"] += 1
        
        return result
    
    def _handle_user_prompt(self, event_data: Dict) -> Dict:
        """Handle user prompt events"""
        prompt = event_data.get("prompt", "")
        
        result = {
            "handler": "user_prompt",
            "browser_relevant": False,
            "parsed_commands": []
        }
        
        # Check for browser-specific commands
        browser_commands = [
            "@browser", "browser:", "claude-code-browser",
            "session:", "project:", "monitor:"
        ]
        
        for cmd in browser_commands:
            if cmd.lower() in prompt.lower():
                result["browser_relevant"] = True
                result["detected_command"] = cmd
                break
        
        # Parse specific browser commands
        if result["browser_relevant"] and self.browser_adapter:
            parsed = self._parse_browser_specific_commands(prompt)
            result["parsed_commands"] = parsed
            
            # Execute browser commands if found
            if parsed:
                execution_results = []
                for command in parsed:
                    exec_result = self._execute_browser_command(command)
                    execution_results.append(exec_result)
                result["execution_results"] = execution_results
        
        return result
    
    def _handle_claude_response(self, event_data: Dict) -> Dict:
        """Handle Claude response events"""
        response = event_data.get("response", "")
        
        result = {
            "handler": "claude_response",
            "monitoring_triggered": False,
            "session_updated": False
        }
        
        # Check if response contains project/session references
        if self.browser_adapter:
            session_refs = self._extract_session_references(response)
            if session_refs:
                result["session_references"] = session_refs
                result["monitoring_triggered"] = True
                
                # Update browser session context
                for session_ref in session_refs:
                    update_result = self._update_session_with_response(session_ref, response)
                    if update_result:
                        result["session_updated"] = True
        
        return result
    
    def _handle_session_started(self, event_data: Dict) -> Dict:
        """Handle session started events"""
        session_id = event_data.get("session_id", "")
        
        result = {
            "handler": "session_started",
            "browser_session_created": False,
            "monitoring_enabled": False
        }
        
        if self.browser_adapter and session_id:
            # Create browser session entry
            browser_session_result = self._create_browser_session_entry(session_id, event_data)
            result["browser_session_created"] = browser_session_result["created"]
            
            # Enable monitoring for this session
            monitoring_result = self._enable_session_monitoring(session_id)
            result["monitoring_enabled"] = monitoring_result["enabled"]
            
            self.stats["browser_sessions_monitored"] += 1
        
        return result
    
    def _handle_session_ended(self, event_data: Dict) -> Dict:
        """Handle session ended events"""
        session_id = event_data.get("session_id", "")
        
        result = {
            "handler": "session_ended",
            "browser_session_finalized": False,
            "monitoring_disabled": False
        }
        
        if self.browser_adapter and session_id:
            # Finalize browser session
            finalize_result = self._finalize_browser_session(session_id, event_data)
            result["browser_session_finalized"] = finalize_result["finalized"]
            
            # Disable monitoring
            monitoring_result = self._disable_session_monitoring(session_id)
            result["monitoring_disabled"] = monitoring_result["disabled"]
        
        return result
    
    def _handle_agent_activation(self, event_data: Dict) -> Dict:
        """Handle agent activation events"""
        agent_name = event_data.get("agent_name", "")
        
        result = {
            "handler": "agent_activation",
            "browser_integration_suggested": False,
            "monitoring_enhanced": False
        }
        
        # Check if agent benefits from browser integration
        browser_beneficial_agents = [
            "api-integration-specialist",
            "frontend-architecture", 
            "backend-services",
            "technical-documentation",
            "master-orchestrator"
        ]
        
        if agent_name in browser_beneficial_agents:
            result["browser_integration_suggested"] = True
            result["suggested_integrations"] = self._suggest_browser_integrations(agent_name)
            
            # Enhance monitoring for this agent
            if self.browser_adapter:
                enhance_result = self._enhance_monitoring_for_agent(agent_name)
                result["monitoring_enhanced"] = enhance_result["enhanced"]
        
        return result
    
    def _handle_orchestration_request(self, event_data: Dict) -> Dict:
        """Handle orchestration request events"""
        request_type = event_data.get("request_type", "")
        
        result = {
            "handler": "orchestration_request",
            "browser_data_available": False,
            "integration_recommendations": []
        }
        
        if self.browser_adapter:
            # Check if browser data can enhance orchestration
            browser_status = self.browser_adapter.get_integration_status()
            
            if browser_status["cache_info"]["sessions"] > 0:
                result["browser_data_available"] = True
                result["available_sessions"] = browser_status["cache_info"]["sessions"]
                result["available_projects"] = browser_status["cache_info"]["projects"]
                
                # Generate integration recommendations
                recommendations = self._generate_orchestration_recommendations(
                    request_type, browser_status
                )
                result["integration_recommendations"] = recommendations
        
        return result
    
    def _handle_context_update(self, event_data: Dict) -> Dict:
        """Handle context update events"""
        context_type = event_data.get("context_type", "")
        
        result = {
            "handler": "context_update",
            "browser_context_sync": False,
            "session_context_updated": False
        }
        
        if self.browser_adapter and self.context_manager:
            # Sync browser context with context manager
            sync_result = self._sync_browser_context_with_manager()
            result["browser_context_sync"] = sync_result["synced"]
            
            # Update session context
            session_update_result = self._update_session_context_from_manager()
            result["session_context_updated"] = session_update_result["updated"]
        
        return result
    
    def _handle_browser_command(self, event_data: Dict) -> Dict:
        """Handle browser-specific command events"""
        command = event_data.get("command", "")
        
        result = {
            "handler": "browser_command",
            "command_executed": False,
            "integration_triggered": False
        }
        
        if self.browser_adapter:
            # Execute browser command
            execution_result = self._execute_browser_command(command)
            result["command_executed"] = execution_result["executed"]
            result["execution_details"] = execution_result
            
            # Trigger integration events
            if execution_result["executed"]:
                integration_result = self._trigger_integration_events(command, execution_result)
                result["integration_triggered"] = integration_result["triggered"]
                self.stats["integration_events"] += 1
        
        return result
    
    def _has_content(self, event_data: Dict) -> bool:
        """Check if event data has content to parse"""
        content_fields = ["prompt", "response", "message", "content", "text"]
        return any(event_data.get(field) for field in content_fields)
    
    def _parse_browser_commands(self, event_data: Dict) -> Dict:
        """Parse browser commands from event content"""
        import re
        
        # Get content from various possible fields
        content = (
            event_data.get("prompt", "") +
            event_data.get("response", "") +
            event_data.get("message", "") +
            event_data.get("content", "")
        )
        
        result = {
            "commands_found": False,
            "command_count": 0,
            "parsed_commands": []
        }
        
        # Browser command patterns
        patterns = {
            "session_reference": r"session:([a-f0-9-]+)",
            "project_reference": r"project:([a-zA-Z0-9_-]+)",
            "browser_query": r"@browser\s+(.+)",
            "monitor_command": r"monitor:(\w+)",
            "integration_command": r"integrate:(.+)"
        }
        
        for pattern_name, pattern in patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                result["parsed_commands"].append({
                    "type": pattern_name,
                    "match": match.group(0),
                    "parameters": match.groups()
                })
                result["command_count"] += 1
        
        result["commands_found"] = result["command_count"] > 0
        return result
    
    def _check_integration_opportunities(self, event_type: str, event_data: Dict) -> Dict:
        """Check for browser integration opportunities"""
        result = {
            "integration_possible": False,
            "opportunities": []
        }
        
        # Integration opportunity patterns
        opportunities = []
        
        # Session-based opportunities
        if "session" in str(event_data).lower():
            opportunities.append({
                "type": "session_integration",
                "description": "Session data available for browser integration",
                "benefit": "Enhanced monitoring and command parsing"
            })
        
        # Agent-based opportunities
        if event_type == "agent_activation":
            opportunities.append({
                "type": "agent_browser_integration",
                "description": "Agent activation can benefit from browser monitoring",
                "benefit": "Real-time agent performance tracking"
            })
        
        # Orchestration opportunities
        if "orchestrate" in str(event_data).lower():
            opportunities.append({
                "type": "orchestration_integration",
                "description": "Orchestration requests can leverage browser data",
                "benefit": "Historical session data for better orchestration"
            })
        
        if opportunities:
            result["integration_possible"] = True
            result["opportunities"] = opportunities
        
        return result
    
    def _update_browser_session_context(self, event_data: Dict) -> Dict:
        """Update browser session context"""
        result = {
            "context_updated": False,
            "sessions_affected": 0
        }
        
        if not self.browser_adapter:
            return result
        
        try:
            # Get current browser sessions
            status = self.browser_adapter.get_integration_status()
            
            if status["cache_info"]["sessions"] > 0:
                # Update context for active sessions
                # This would integrate with actual session updates
                result["context_updated"] = True
                result["sessions_affected"] = status["cache_info"]["sessions"]
                result["update_timestamp"] = datetime.now().isoformat()
        
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _trigger_real_time_update(self, event_type: str, event_data: Dict, result: Dict):
        """Trigger real-time updates to browser clients"""
        if not self.browser_adapter:
            return
        
        try:
            # Create update message
            update_message = {
                "type": "hook_event_update",
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "hook_result": result,
                "integration_info": {
                    "enhancements": result.get("enhancements", []),
                    "browser_integration": result.get("browser_integration", False)
                }
            }
            
            # Send to WebSocket clients (this would need async handling)
            # For now, we'll queue it for the background task
            if hasattr(self, 'pending_updates'):
                self.pending_updates.append(update_message)
            else:
                self.pending_updates = [update_message]
        
        except Exception as e:
            print(f"Failed to trigger real-time update: {e}")
    
    # Additional helper methods for browser-specific operations
    def _parse_browser_specific_commands(self, prompt: str) -> List[Dict]:
        """Parse browser-specific commands from prompt"""
        # Implement specific browser command parsing
        return []
    
    def _execute_browser_command(self, command: str) -> Dict:
        """Execute browser command"""
        return {"executed": False, "message": "Command execution not implemented"}
    
    def _extract_session_references(self, response: str) -> List[str]:
        """Extract session references from response"""
        import re
        pattern = r"session[:\s]+([a-f0-9-]+)"
        matches = re.findall(pattern, response, re.IGNORECASE)
        return matches
    
    def _update_session_with_response(self, session_ref: str, response: str) -> bool:
        """Update session with response data"""
        return False
    
    def _create_browser_session_entry(self, session_id: str, event_data: Dict) -> Dict:
        """Create browser session entry"""
        return {"created": False}
    
    def _enable_session_monitoring(self, session_id: str) -> Dict:
        """Enable monitoring for session"""
        return {"enabled": False}
    
    def _finalize_browser_session(self, session_id: str, event_data: Dict) -> Dict:
        """Finalize browser session"""
        return {"finalized": False}
    
    def _disable_session_monitoring(self, session_id: str) -> Dict:
        """Disable session monitoring"""
        return {"disabled": False}
    
    def _suggest_browser_integrations(self, agent_name: str) -> List[str]:
        """Suggest browser integrations for agent"""
        suggestions = {
            "api-integration-specialist": ["API testing sessions", "Integration monitoring"],
            "frontend-architecture": ["UI component sessions", "Design system tracking"],
            "backend-services": ["Service architecture sessions", "Performance monitoring"],
            "technical-documentation": ["Documentation sessions", "Knowledge tracking"],
            "master-orchestrator": ["Orchestration sessions", "Multi-agent coordination"]
        }
        return suggestions.get(agent_name, [])
    
    def _enhance_monitoring_for_agent(self, agent_name: str) -> Dict:
        """Enhance monitoring for specific agent"""
        return {"enhanced": False}
    
    def _generate_orchestration_recommendations(self, request_type: str, browser_status: Dict) -> List[str]:
        """Generate orchestration recommendations based on browser data"""
        recommendations = []
        
        if browser_status["cache_info"]["sessions"] > 10:
            recommendations.append("Consider session history for better orchestration")
        
        if browser_status["websocket_info"]["connections"] > 0:
            recommendations.append("Real-time monitoring available for orchestration feedback")
        
        return recommendations
    
    def _sync_browser_context_with_manager(self) -> Dict:
        """Sync browser context with context manager"""
        return {"synced": False}
    
    def _update_session_context_from_manager(self) -> Dict:
        """Update session context from context manager"""
        return {"updated": False}
    
    def _trigger_integration_events(self, command: str, execution_result: Dict) -> Dict:
        """Trigger integration events"""
        return {"triggered": False}
    
    def get_hook_status(self) -> Dict:
        """Get comprehensive hook status"""
        return {
            "hook_name": self.hook_name,
            "version": self.hook_version,
            "is_active": self.is_active,
            "adapter_available": BROWSER_ADAPTER_AVAILABLE,
            "adapter_initialized": self.browser_adapter is not None,
            "config": self.config,
            "stats": self.stats,
            "background_tasks": len(self.background_tasks),
            "integration_status": {
                "orchestrator": self.v3_orchestrator is not None,
                "status_line": self.status_line is not None,
                "context_manager": self.context_manager is not None,
                "chat_manager": self.chat_manager is not None
            },
            "attribution": {
                "original_project": "Claude Code Browser by @zainhoda (AGPL-3.0)",
                "integration": "Claude Code Dev Stack v3.0 (AGPL-3.0)",
                "compliance": "Maintained"
            }
        }


# Global hook instance
browser_integration_hook = None

def get_browser_integration_hook() -> BrowserIntegrationHook:
    """Get or create browser integration hook instance"""
    global browser_integration_hook
    if browser_integration_hook is None:
        browser_integration_hook = BrowserIntegrationHook()
    return browser_integration_hook

def process_hook(event_type: str, event_data: Dict) -> Dict:
    """Main hook entry point"""
    hook = get_browser_integration_hook()
    return hook.process_hook_event(event_type, event_data)

# Export for hook system
__all__ = [
    'BrowserIntegrationHook',
    'get_browser_integration_hook', 
    'process_hook'
]