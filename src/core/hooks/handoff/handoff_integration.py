#!/usr/bin/env python3
"""
Handoff Integration Layer for V3.6.9 Framework
Integrates handoff protocols with existing orchestration systems
"""

import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable

from .handoff_protocols import (
    HandoffType, HandoffPriority, AgentState, HandoffPackage, 
    HandoffExecutor, MultiAgentHandoffOrchestrator, HandoffPerformanceMonitor
)

# Import existing V3.6.9 components
try:
    from .smart_orchestrator import SmartOrchestrator
    from .context_manager import ContextManager  
    from .chat_manager_v3 import ChatManager
    from .status_line_manager import StatusLineManager
    from .v3_orchestrator import ClaudeCodeV3Orchestrator
except ImportError:
    # Fallback for testing
    SmartOrchestrator = None
    ContextManager = None
    ChatManager = None
    StatusLineManager = None
    ClaudeCodeV3Orchestrator = None

class HandoffIntegrationManager:
    """
    Integrates handoff protocols with existing V3.6.9 framework components
    """
    
    def __init__(self, v3_orchestrator=None):
        # Core handoff system
        self.handoff_executor = HandoffExecutor()
        self.multi_agent_orchestrator = MultiAgentHandoffOrchestrator()
        self.performance_monitor = HandoffPerformanceMonitor()
        
        # V3.6.9 Framework components
        self.v3_orchestrator = v3_orchestrator or self._initialize_v3_orchestrator()
        self.smart_orchestrator = self._initialize_smart_orchestrator()
        self.context_manager = self._initialize_context_manager()
        self.chat_manager = self._initialize_chat_manager()
        self.status_line_manager = self._initialize_status_line_manager()
        
        # Integration state
        self.active_handoffs: Dict[str, Dict[str, Any]] = {}
        self.handoff_history: List[Dict[str, Any]] = []
        self.integration_metrics = {
            "handoffs_triggered_by_context": 0,
            "handoffs_triggered_by_chat": 0,
            "handoffs_triggered_by_orchestrator": 0,
            "successful_integrations": 0,
            "failed_integrations": 0
        }
        
        # Configuration
        self.config = {
            "auto_handoff_enabled": True,
            "context_monitoring_enabled": True,
            "chat_monitoring_enabled": True,
            "performance_monitoring_enabled": True,
            "emergency_escalation_enabled": True
        }
        
        # Start monitoring threads
        self._start_integration_monitoring()
    
    def _initialize_v3_orchestrator(self):
        """Initialize V3 orchestrator if available"""
        if ClaudeCodeV3Orchestrator:
            return ClaudeCodeV3Orchestrator()
        return None
    
    def _initialize_smart_orchestrator(self):
        """Initialize smart orchestrator if available"""
        if SmartOrchestrator:
            return SmartOrchestrator()
        return None
    
    def _initialize_context_manager(self):
        """Initialize context manager if available"""
        if ContextManager:
            return ContextManager()
        return None
    
    def _initialize_chat_manager(self):
        """Initialize chat manager if available"""
        if ChatManager:
            return ChatManager()
        return None
    
    def _initialize_status_line_manager(self):
        """Initialize status line manager if available"""
        if StatusLineManager:
            return StatusLineManager()
        return None
    
    def _start_integration_monitoring(self):
        """Start background monitoring threads for integration triggers"""
        if self.config["context_monitoring_enabled"]:
            context_thread = threading.Thread(target=self._monitor_context_triggers, daemon=True)
            context_thread.start()
        
        if self.config["chat_monitoring_enabled"]:
            chat_thread = threading.Thread(target=self._monitor_chat_triggers, daemon=True)
            chat_thread.start()
        
        if self.config["performance_monitoring_enabled"]:
            performance_thread = threading.Thread(target=self._monitor_performance_triggers, daemon=True)
            performance_thread.start()
    
    def process_integration_request(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for processing integration requests
        """
        result = {
            "processed": True,
            "handoff_triggered": False,
            "handoff_result": None,
            "integration_actions": [],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Determine if handoff is needed based on event
            handoff_assessment = self._assess_handoff_need(event_type, data)
            
            if handoff_assessment["handoff_recommended"]:
                # Create and execute handoff
                handoff_package = self._create_integration_handoff_package(
                    event_type, data, handoff_assessment
                )
                
                # Execute handoff
                handoff_result = self.handoff_executor.execute_handoff(handoff_package)
                
                # Update integration state
                self._update_integration_state(handoff_package, handoff_result)
                
                result["handoff_triggered"] = True
                result["handoff_result"] = handoff_result
                result["integration_actions"].append("handoff_executed")
                
                # Record performance metrics
                self.performance_monitor.record_handoff_metrics(handoff_result)
                
                # Update integration metrics
                self.integration_metrics["successful_integrations"] += 1 if handoff_result.success else 0
                self.integration_metrics["failed_integrations"] += 0 if handoff_result.success else 1
            
            # Process with existing V3.6.9 components
            if self.v3_orchestrator:
                v3_result = self.v3_orchestrator.process_request(event_type, data)
                result["v3_orchestrator_result"] = v3_result
                result["integration_actions"].append("v3_orchestrator_processed")
            
            # Update status line with handoff information
            if self.status_line_manager and result["handoff_triggered"]:
                self._update_status_line_with_handoff(handoff_package, handoff_result)
                result["integration_actions"].append("status_line_updated")
            
        except Exception as e:
            result["processed"] = False
            result["error"] = str(e)
            self.integration_metrics["failed_integrations"] += 1
        
        return result
    
    def _assess_handoff_need(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess whether a handoff is needed based on the event and current state
        """
        assessment = {
            "handoff_recommended": False,
            "handoff_type": None,
            "priority": HandoffPriority.NORMAL,
            "source_agent": None,
            "target_agent": None,
            "reason": None
        }
        
        # Context-based triggers
        if self.context_manager:
            context_health = self.context_manager.get_status()
            if context_health["health"] == "critical":
                assessment.update({
                    "handoff_recommended": True,
                    "handoff_type": HandoffType.EMERGENCY,
                    "priority": HandoffPriority.CRITICAL,
                    "reason": "context_critical"
                })
                self.integration_metrics["handoffs_triggered_by_context"] += 1
        
        # Chat-based triggers
        if self.chat_manager:
            chat_health = self.chat_manager.get_chat_health()
            if chat_health["status"] == "critical":
                assessment.update({
                    "handoff_recommended": True,
                    "handoff_type": HandoffType.PHASE_TRANSITION,
                    "priority": HandoffPriority.HIGH,
                    "reason": "chat_critical"
                })
                self.integration_metrics["handoffs_triggered_by_chat"] += 1
        
        # Event-specific triggers
        if event_type == "agent_failure":
            assessment.update({
                "handoff_recommended": True,
                "handoff_type": HandoffType.EMERGENCY,
                "priority": HandoffPriority.EMERGENCY,
                "source_agent": data.get("failed_agent"),
                "target_agent": data.get("backup_agent", "master-orchestrator"),
                "reason": "agent_failure"
            })
        
        elif event_type == "phase_transition":
            assessment.update({
                "handoff_recommended": True,
                "handoff_type": HandoffType.PHASE_TRANSITION,
                "priority": HandoffPriority.NORMAL,
                "source_agent": data.get("current_agent"),
                "target_agent": data.get("next_agent"),
                "reason": "phase_transition"
            })
        
        elif event_type == "load_balancing":
            assessment.update({
                "handoff_recommended": True,
                "handoff_type": HandoffType.LOAD_BALANCE,
                "priority": HandoffPriority.LOW,
                "reason": "load_balancing"
            })
        
        # Smart orchestrator integration
        if self.smart_orchestrator and not assessment["handoff_recommended"]:
            # Use smart orchestrator to determine if handoff beneficial
            orchestration_result = self.smart_orchestrator.execute_orchestration(
                data.get("user_prompt", ""), data.get("context", {})
            )
            
            if len(orchestration_result.get("selected_agents", [])) > 1:
                assessment.update({
                    "handoff_recommended": True,
                    "handoff_type": HandoffType.COLLABORATIVE,
                    "priority": HandoffPriority.NORMAL,
                    "reason": "multi_agent_workflow"
                })
                self.integration_metrics["handoffs_triggered_by_orchestrator"] += 1
        
        return assessment
    
    def _create_integration_handoff_package(self, event_type: str, data: Dict[str, Any], assessment: Dict[str, Any]) -> HandoffPackage:
        """
        Create handoff package based on integration context
        """
        # Extract state from current context
        current_state = self._extract_current_state(data)
        
        # Determine agents
        source_agent = assessment.get("source_agent") or data.get("current_agent", "unknown")
        target_agent = assessment.get("target_agent") or self._determine_target_agent(event_type, data)
        
        # Create handoff package
        package = HandoffPackage(
            handoff_id=f"integration_{event_type}_{int(time.time())}",
            source_agent=source_agent,
            target_agent=target_agent,
            handoff_type=assessment["handoff_type"],
            priority=assessment["priority"],
            
            state_transfer=current_state,
            
            work_summary=self._generate_work_summary(event_type, data, assessment),
            completed_tasks=data.get("completed_tasks", []),
            pending_tasks=data.get("pending_tasks", []),
            next_actions=data.get("next_actions", []),
            
            conversation_context=self._extract_conversation_context(),
            technical_context=self._extract_technical_context(),
            business_context=self._extract_business_context(),
            
            validation_checkpoints=self._generate_validation_checkpoints(assessment),
            rollback_points=self._generate_rollback_points(current_state),
            success_criteria=self._generate_success_criteria(assessment),
            
            created_at=datetime.now().isoformat(),
            timeout_at=(datetime.now() + timedelta(minutes=30)).isoformat(),
            retry_count=0,
            metadata={
                "integration_source": "v3_framework",
                "event_type": event_type,
                "assessment_reason": assessment["reason"]
            }
        )
        
        return package
    
    def _extract_current_state(self, data: Dict[str, Any]) -> AgentState:
        """Extract current agent state from available data"""
        return AgentState(
            agent_id=data.get("current_agent", "unknown"),
            agent_type=data.get("agent_type", "unknown"),
            current_task=data.get("current_task"),
            progress=data.get("progress", 0.0),
            context=data.get("context", {}),
            active_files=data.get("active_files", []),
            dependencies=data.get("dependencies", []),
            performance_metrics=data.get("performance_metrics", {}),
            error_state=data.get("error_state"),
            memory_snapshot=data.get("memory_snapshot", {}),
            timestamp=datetime.now().isoformat()
        )
    
    def _determine_target_agent(self, event_type: str, data: Dict[str, Any]) -> str:
        """Determine target agent based on event type and context"""
        # Default agent routing based on event type
        event_agent_mapping = {
            "error_recovery": "devops-engineer",
            "phase_transition": "master-orchestrator",
            "load_balancing": "project-manager",
            "user_prompt": "prompt-engineer",
            "technical_issue": "technical-cto"
        }
        
        suggested_agent = event_agent_mapping.get(event_type, "master-orchestrator")
        
        # Use smart orchestrator for better routing if available
        if self.smart_orchestrator:
            orchestration_result = self.smart_orchestrator.execute_orchestration(
                data.get("user_prompt", event_type), data.get("context", {})
            )
            suggested_agents = orchestration_result.get("selected_agents", [])
            if suggested_agents:
                suggested_agent = suggested_agents[0]
        
        return suggested_agent
    
    def _extract_conversation_context(self) -> Dict[str, Any]:
        """Extract conversation context from chat manager"""
        if self.chat_manager:
            return {
                "chat_state": self.chat_manager.get_summary(),
                "health": self.chat_manager.get_chat_health()
            }
        return {}
    
    def _extract_technical_context(self) -> Dict[str, Any]:
        """Extract technical context from various sources"""
        context = {}
        
        if self.status_line_manager:
            status = self.status_line_manager.status
            context["system_status"] = {
                "git": status.get("git", {}),
                "phase": status.get("phase"),
                "performance": status.get("performance", {})
            }
        
        if self.context_manager:
            context["context_state"] = self.context_manager.get_status()
        
        return context
    
    def _extract_business_context(self) -> Dict[str, Any]:
        """Extract business context"""
        # This would integrate with business context systems
        return {
            "current_project": "unknown",
            "business_priority": "normal",
            "stakeholder_requirements": []
        }
    
    def _generate_work_summary(self, event_type: str, data: Dict[str, Any], assessment: Dict[str, Any]) -> str:
        """Generate work summary for handoff"""
        return f"""
        Integration handoff triggered by {event_type}.
        
        Reason: {assessment['reason']}
        Priority: {assessment['priority'].name}
        
        Current Context:
        - Event: {event_type}
        - Assessment: {assessment['reason']}
        - Integration source: V3.6.9 Framework
        
        Handoff initiated to ensure continuity and optimal agent utilization.
        """
    
    def _generate_validation_checkpoints(self, assessment: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate validation checkpoints based on handoff type"""
        checkpoints = [
            {"checkpoint": "agent_availability", "criteria": "Target agent available and responsive"},
            {"checkpoint": "state_transfer", "criteria": "State successfully transferred to target agent"}
        ]
        
        if assessment["handoff_type"] == HandoffType.EMERGENCY:
            checkpoints.append({
                "checkpoint": "emergency_response", 
                "criteria": "Emergency situation addressed within SLA"
            })
        
        return checkpoints
    
    def _generate_rollback_points(self, current_state: AgentState) -> List[Dict[str, Any]]:
        """Generate rollback points for handoff"""
        return [
            {
                "point": "pre_handoff_state",
                "trigger": "Handoff failure",
                "action": "Restore original agent state",
                "state_snapshot": current_state
            }
        ]
    
    def _generate_success_criteria(self, assessment: Dict[str, Any]) -> List[str]:
        """Generate success criteria based on handoff type"""
        criteria = [
            "Target agent activated successfully",
            "State transfer completed without data loss",
            "Workflow continuity maintained"
        ]
        
        if assessment["handoff_type"] == HandoffType.EMERGENCY:
            criteria.append("Emergency situation resolved")
        
        return criteria
    
    def _update_integration_state(self, package: HandoffPackage, result):
        """Update integration state after handoff"""
        handoff_record = {
            "handoff_id": package.handoff_id,
            "timestamp": datetime.now().isoformat(),
            "source_agent": package.source_agent,
            "target_agent": package.target_agent,
            "handoff_type": package.handoff_type.value,
            "success": result.success,
            "continuity_score": result.continuity_score,
            "execution_time_ms": result.performance_metrics.get("total_time_ms", 0)
        }
        
        self.handoff_history.append(handoff_record)
        
        # Keep only recent history (last 100 handoffs)
        if len(self.handoff_history) > 100:
            self.handoff_history = self.handoff_history[-100:]
        
        # Update active handoffs
        if result.success:
            self.active_handoffs[package.handoff_id] = {
                "package": package,
                "result": result,
                "status": "active"
            }
    
    def _update_status_line_with_handoff(self, package: HandoffPackage, result):
        """Update status line with handoff information"""
        if self.status_line_manager:
            # This would update the status line with handoff information
            # Implementation depends on status line manager interface
            pass
    
    def _monitor_context_triggers(self):
        """Monitor context manager for handoff triggers"""
        while True:
            try:
                if self.context_manager:
                    status = self.context_manager.get_status()
                    if status["health"] == "critical":
                        # Trigger emergency handoff
                        self.process_integration_request("context_emergency", {
                            "context_status": status,
                            "trigger_source": "context_monitor"
                        })
                
                time.sleep(10)  # Check every 10 seconds
            except Exception:
                time.sleep(10)
    
    def _monitor_chat_triggers(self):
        """Monitor chat manager for handoff triggers"""
        while True:
            try:
                if self.chat_manager:
                    health = self.chat_manager.get_chat_health()
                    if health["status"] in ["warning", "critical"]:
                        # Trigger handoff suggestion
                        self.process_integration_request("chat_handoff_suggested", {
                            "chat_health": health,
                            "trigger_source": "chat_monitor"
                        })
                
                time.sleep(30)  # Check every 30 seconds
            except Exception:
                time.sleep(30)
    
    def _monitor_performance_triggers(self):
        """Monitor performance metrics for handoff optimization"""
        while True:
            try:
                analysis = self.performance_monitor.get_performance_analysis()
                
                if analysis.get("recommendations"):
                    # Performance-based handoff optimization
                    self.process_integration_request("performance_optimization", {
                        "performance_analysis": analysis,
                        "trigger_source": "performance_monitor"
                    })
                
                time.sleep(60)  # Check every minute
            except Exception:
                time.sleep(60)
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get current integration status"""
        return {
            "timestamp": datetime.now().isoformat(),
            "active_handoffs": len(self.active_handoffs),
            "total_handoffs": len(self.handoff_history),
            "integration_metrics": self.integration_metrics,
            "recent_handoffs": self.handoff_history[-10:],  # Last 10 handoffs
            "performance_analysis": self.performance_monitor.get_performance_analysis(),
            "component_status": {
                "v3_orchestrator": self.v3_orchestrator is not None,
                "smart_orchestrator": self.smart_orchestrator is not None,
                "context_manager": self.context_manager is not None,
                "chat_manager": self.chat_manager is not None,
                "status_line_manager": self.status_line_manager is not None
            }
        }
    
    def execute_manual_handoff(self, source_agent: str, target_agent: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute manual handoff between specified agents"""
        assessment = {
            "handoff_recommended": True,
            "handoff_type": HandoffType.DIRECT,
            "priority": HandoffPriority.NORMAL,
            "source_agent": source_agent,
            "target_agent": target_agent,
            "reason": "manual_request"
        }
        
        return self.process_integration_request("manual_handoff", {
            "current_agent": source_agent,
            "target_agent": target_agent,
            "context": context,
            "manual_trigger": True
        })

# Global integration manager instance
integration_manager = None

def get_integration_manager() -> HandoffIntegrationManager:
    """Get or create integration manager instance"""
    global integration_manager
    if integration_manager is None:
        integration_manager = HandoffIntegrationManager()
    return integration_manager

def process_handoff_integration(event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for handoff integration"""
    manager = get_integration_manager()
    return manager.process_integration_request(event_type, data)

# Export for V3.6.9 framework
__all__ = [
    'HandoffIntegrationManager',
    'get_integration_manager', 
    'process_handoff_integration'
]