#!/usr/bin/env python3
"""
Claude Code v3.0 Master Orchestrator - Enhanced integration layer
Coordinates all v3.0 systems: Status Line, Context Management, Chat Management, and legacy systems
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import threading

# Import v3.0 components
try:
    from .status_line_manager import get_status_line
    from .context_manager import get_context_manager  
    from .chat_manager import get_chat_manager, HandoffTrigger, ConversationPhase
    from .master_orchestrator import UltimateClaudeOrchestrator
except ImportError:
    # Fallback for standalone testing
    def get_status_line():
        return None
    def get_context_manager():
        return None
    def get_chat_manager():
        return None
    class UltimateClaudeOrchestrator:
        pass

class ClaudeCodeV3Orchestrator:
    """
    Master orchestrator for Claude Code v3.0 system
    Integrates all v3.0 components with intelligent coordination
    """
    
    def __init__(self):
        # Initialize v3.0 core systems
        self.status_line = get_status_line()
        self.context_manager = get_context_manager()
        self.chat_manager = get_chat_manager()
        
        # Initialize legacy orchestrator for compatibility
        self.legacy_orchestrator = UltimateClaudeOrchestrator()
        
        # System state
        self.system_state = {
            "version": "3.0",
            "initialized": False,
            "components": {
                "status_line": False,
                "context_manager": False,
                "chat_manager": False,
                "legacy_orchestrator": False
            },
            "health": "initializing"
        }
        
        # Integration configuration
        self.integration_config = {
            "status_line_integration": True,
            "context_preservation": True,
            "intelligent_handoffs": True,
            "legacy_compatibility": True,
            "real_time_coordination": True
        }
        
        # Performance metrics
        self.metrics = {
            "total_requests": 0,
            "successful_handoffs": 0,
            "context_preservations": 0,
            "system_optimizations": 0,
            "error_count": 0
        }
        
        # Background coordination
        self.coordination_thread = None
        self.running = False
        
        # Initialize system
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize all v3.0 systems and verify integration"""
        try:
            # Check component availability
            self.system_state["components"]["status_line"] = self.status_line is not None
            self.system_state["components"]["context_manager"] = self.context_manager is not None
            self.system_state["components"]["chat_manager"] = self.chat_manager is not None
            self.system_state["components"]["legacy_orchestrator"] = self.legacy_orchestrator is not None
            
            # Start coordination
            self.running = True
            self.coordination_thread = threading.Thread(target=self._coordination_loop, daemon=True)
            self.coordination_thread.start()
            
            self.system_state["initialized"] = True
            self.system_state["health"] = "operational"
            
            # Update status line
            if self.status_line:
                self.status_line.update_status(
                    "v3_orchestrator",
                    "active", 
                    {
                        "version": "3.0",
                        "components_active": sum(self.system_state["components"].values()),
                        "health": self.system_state["health"]
                    }
                )
                
        except Exception as e:
            self.system_state["health"] = "error"
            self.system_state["error"] = str(e)
    
    def start(self):
        """Start the v3.0 orchestrator"""
        if not self.running:
            self.running = True
            self.coordination_thread = threading.Thread(target=self._coordination_loop, daemon=True)
            self.coordination_thread.start()
    
    def stop(self):
        """Stop the v3.0 orchestrator"""
        self.running = False
        if self.coordination_thread:
            self.coordination_thread.join(timeout=1)
    
    def process_request(self, event_type: str, data: Dict) -> Dict:
        """
        Main request processing with v3.0 enhancements
        """
        self.metrics["total_requests"] += 1
        start_time = time.time()
        
        result = {
            "processed": True,
            "version": "3.0",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": f"v3_{int(time.time() * 1000)}",
            "components_used": [],
            "enhancements_applied": [],
            "legacy_compatibility": False,
            "performance_metrics": {}
        }
        
        try:
            # 1. Pre-process with status line integration
            if self.status_line and self.integration_config["status_line_integration"]:
                status_insight = self._get_status_insight(event_type, data)
                result["status_insight"] = status_insight
                result["components_used"].append("status_line")
            
            # 2. Chat management integration
            if self.chat_manager and event_type in ['user_prompt', 'claude_response', 'user_message']:
                chat_result = self._process_with_chat_management(event_type, data)
                result["chat_management"] = chat_result
                result["components_used"].append("chat_manager")
                
                # Handle automatic handoffs
                if chat_result.get("handoff_triggered"):
                    result["enhancements_applied"].append("automatic_handoff")
                    self.metrics["successful_handoffs"] += 1
            
            # 3. Context management integration
            if self.context_manager and self.integration_config["context_preservation"]:
                context_result = self._process_with_context_management(event_type, data)
                result["context_management"] = context_result
                result["components_used"].append("context_manager")
                
                if context_result.get("context_preserved"):
                    result["enhancements_applied"].append("context_preservation")
                    self.metrics["context_preservations"] += 1
            
            # 4. Enhanced orchestration logic
            orchestration_result = self._enhanced_orchestration(event_type, data, result)
            result["orchestration"] = orchestration_result
            
            # 5. Legacy compatibility layer
            if self.integration_config["legacy_compatibility"]:
                legacy_result = self._process_with_legacy_orchestrator(event_type, data)
                result["legacy_compatibility"] = True
                result["legacy_result"] = legacy_result
                result["components_used"].append("legacy_orchestrator")
            
            # 6. System optimization
            optimization_result = self._apply_system_optimizations(result)
            if optimization_result["optimizations_applied"]:
                result["enhancements_applied"].append("system_optimization")
                result["optimizations"] = optimization_result
                self.metrics["system_optimizations"] += 1
            
            # 7. Update performance metrics
            processing_time = time.time() - start_time
            result["performance_metrics"] = {
                "processing_time_ms": round(processing_time * 1000, 2),
                "components_used": len(result["components_used"]),
                "enhancements_applied": len(result["enhancements_applied"]),
                "efficiency_score": self._calculate_efficiency_score(result, processing_time)
            }
            
            # 8. Update status line with results
            if self.status_line:
                self.status_line.update_status(
                    "request_processed",
                    "complete",
                    {
                        "request_type": event_type,
                        "processing_time_ms": result["performance_metrics"]["processing_time_ms"],
                        "components_used": result["components_used"],
                        "enhancements_applied": result["enhancements_applied"]
                    }
                )
            
        except Exception as e:
            self.metrics["error_count"] += 1
            result["processed"] = False
            result["error"] = str(e)
            result["error_timestamp"] = datetime.utcnow().isoformat()
            
            # Log error to status line
            if self.status_line:
                self.status_line.update_status(
                    "orchestrator_error",
                    "error",
                    {"error": str(e), "event_type": event_type}
                )
        
        return result
    
    def get_system_status(self) -> Dict:
        """Get comprehensive v3.0 system status"""
        status = {
            "version": "3.0",
            "timestamp": datetime.utcnow().isoformat(),
            "system_state": self.system_state,
            "component_status": {},
            "integration_health": {},
            "performance_metrics": self.metrics,
            "recommendations": []
        }
        
        # Get individual component statuses
        if self.status_line:
            status["component_status"]["status_line"] = self.status_line.get_current_status()
        
        if self.context_manager:
            status["component_status"]["context_manager"] = self.context_manager.get_context_health()
        
        if self.chat_manager:
            status["component_status"]["chat_manager"] = self.chat_manager.check_conversation_health()
        
        # Assess integration health
        status["integration_health"] = self._assess_integration_health()
        
        # Generate recommendations
        status["recommendations"] = self._generate_system_recommendations(status)
        
        return status
    
    def execute_intelligent_workflow(self, workflow_request: Dict) -> Dict:
        """
        Execute intelligent workflow with v3.0 enhancements
        """
        workflow_id = f"wf_v3_{int(time.time() * 1000)}"
        
        result = {
            "workflow_id": workflow_id,
            "status": "initiated",
            "timestamp": datetime.utcnow().isoformat(),
            "phases": [],
            "current_phase": None,
            "agents_orchestrated": [],
            "context_snapshots": [],
            "handoffs_executed": []
        }
        
        try:
            # 1. Parse workflow request
            workflow_analysis = self._analyze_workflow_request(workflow_request)
            result["workflow_analysis"] = workflow_analysis
            
            # 2. Create execution plan with v3.0 intelligence
            execution_plan = self._create_v3_execution_plan(workflow_analysis)
            result["execution_plan"] = execution_plan
            
            # 3. Initialize context snapshot
            if self.context_manager:
                initial_snapshot = self.context_manager.create_context_snapshot()
                result["context_snapshots"].append({
                    "phase": "initialization",
                    "snapshot_id": initial_snapshot.snapshot_id,
                    "timestamp": initial_snapshot.timestamp
                })
            
            # 4. Execute workflow phases
            for phase in execution_plan["phases"]:
                phase_result = self._execute_workflow_phase(phase, workflow_id)
                result["phases"].append(phase_result)
                result["current_phase"] = phase["name"]
                
                # Handle phase transitions
                if phase_result["requires_handoff"]:
                    handoff_result = self._execute_phase_handoff(phase, phase_result)
                    result["handoffs_executed"].append(handoff_result)
                
                # Create phase completion snapshot
                if self.context_manager and phase_result["status"] == "completed":
                    phase_snapshot = self.context_manager.create_context_snapshot()
                    result["context_snapshots"].append({
                        "phase": phase["name"],
                        "snapshot_id": phase_snapshot.snapshot_id,
                        "timestamp": phase_snapshot.timestamp
                    })
            
            result["status"] = "completed"
            result["completion_timestamp"] = datetime.utcnow().isoformat()
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            result["error_timestamp"] = datetime.utcnow().isoformat()
        
        return result
    
    def _get_status_insight(self, event_type: str, data: Dict) -> Dict:
        """Get status-based insights for request processing"""
        if not self.status_line:
            return {}
        
        current_status = self.status_line.get_current_status()
        routing_suggestion = self.status_line.get_intelligent_routing()
        
        return {
            "system_health": current_status.get("system_health", {}),
            "resource_usage": current_status.get("status", {}).get("resources", {}),
            "routing_suggestions": routing_suggestion,
            "optimal_processing": self._determine_optimal_processing(current_status, event_type)
        }
    
    def _process_with_chat_management(self, event_type: str, data: Dict) -> Dict:
        """Process request with chat management integration"""
        if not self.chat_manager:
            return {}
        
        # Map event types to chat manager methods
        if event_type in ['user_prompt', 'user_message']:
            message = data.get('prompt', data.get('message', ''))
            return self.chat_manager.manage_conversation_flow(message, 'user')
        
        elif event_type == 'claude_response':
            response = data.get('response', '')
            return self.chat_manager.manage_conversation_flow(response, 'claude')
        
        else:
            # Check if handoff is beneficial for this event type
            suggestions = self.chat_manager.get_handoff_suggestions()
            return {"handoff_suggestions": suggestions}
    
    def _process_with_context_management(self, event_type: str, data: Dict) -> Dict:
        """Process request with context management integration"""
        if not self.context_manager:
            return {}
        
        # Check context health
        context_health = self.context_manager.get_context_health()
        
        result = {
            "context_health": context_health,
            "context_preserved": False,
            "optimization_applied": False
        }
        
        # Apply optimizations if needed
        if context_health["status"] in ["warning", "critical"]:
            optimization_level = "emergency" if context_health["status"] == "critical" else "standard"
            optimization_result = self.context_manager.optimize_context(optimization_level)
            result["optimization_applied"] = True
            result["optimization_result"] = optimization_result
        
        # Create snapshot for important events
        if event_type in ['user_prompt', 'phase_transition', 'agent_handoff']:
            snapshot = self.context_manager.create_context_snapshot()
            result["context_preserved"] = True
            result["snapshot_id"] = snapshot.snapshot_id
        
        return result
    
    def _enhanced_orchestration(self, event_type: str, data: Dict, current_result: Dict) -> Dict:
        """Apply enhanced orchestration logic"""
        orchestration = {
            "enhanced_routing": False,
            "parallel_optimization": False,
            "intelligent_prioritization": False,
            "resource_optimization": False
        }
        
        # Enhanced agent routing based on current system state
        if self.status_line:
            routing = self.status_line.get_intelligent_routing()
            if routing.get("recommended_agents"):
                orchestration["enhanced_routing"] = True
                orchestration["recommended_agents"] = routing["recommended_agents"]
        
        # Parallel execution opportunities
        if current_result.get("status_insight", {}).get("optimal_processing", {}).get("parallel_capable", False):
            orchestration["parallel_optimization"] = True
            orchestration["parallel_suggestions"] = ["Backend and frontend agents can run in parallel"]
        
        # Intelligent prioritization
        chat_health = current_result.get("chat_management", {}).get("conversation_health", {})
        if chat_health.get("priority") in ["high", "critical"]:
            orchestration["intelligent_prioritization"] = True
            orchestration["priority_level"] = chat_health["priority"]
        
        # Resource optimization
        resource_usage = current_result.get("status_insight", {}).get("resource_usage", {})
        if resource_usage.get("cpu_percent", 0) > 70:
            orchestration["resource_optimization"] = True
            orchestration["optimization_suggestions"] = ["Consider lightweight agents", "Defer non-critical tasks"]
        
        return orchestration
    
    def _process_with_legacy_orchestrator(self, event_type: str, data: Dict) -> Dict:
        """Process with legacy orchestrator for compatibility"""
        try:
            # Map v3.0 event types to legacy event types
            legacy_event_type = self._map_to_legacy_event_type(event_type)
            legacy_data = self._prepare_legacy_data(data)
            
            # Process with legacy orchestrator
            legacy_result = self.legacy_orchestrator.process_hook_event(legacy_event_type, legacy_data)
            
            return {
                "processed": True,
                "legacy_event_type": legacy_event_type,
                "result": legacy_result
            }
            
        except Exception as e:
            return {
                "processed": False,
                "error": str(e)
            }
    
    def _apply_system_optimizations(self, current_result: Dict) -> Dict:
        """Apply system-wide optimizations"""
        optimizations = {
            "optimizations_applied": [],
            "performance_improvements": [],
            "resource_savings": []
        }
        
        # Context optimization
        context_health = current_result.get("context_management", {}).get("context_health", {})
        if context_health.get("status") == "warning":
            optimizations["optimizations_applied"].append("context_optimization")
            optimizations["performance_improvements"].append("Reduced context complexity")
        
        # Chat flow optimization
        chat_health = current_result.get("chat_management", {}).get("conversation_health", {})
        if chat_health.get("action") == "compact_suggested":
            optimizations["optimizations_applied"].append("chat_optimization")
            optimizations["performance_improvements"].append("Optimized conversation flow")
        
        # Resource optimization
        status_insight = current_result.get("status_insight", {})
        if status_insight.get("resource_usage", {}).get("memory_percent", 0) > 80:
            optimizations["optimizations_applied"].append("memory_optimization")
            optimizations["resource_savings"].append("Memory usage optimization")
        
        return optimizations
    
    def _calculate_efficiency_score(self, result: Dict, processing_time: float) -> float:
        """Calculate processing efficiency score"""
        base_score = 100.0
        
        # Penalize long processing times
        if processing_time > 1.0:  # More than 1 second
            base_score -= min(50, (processing_time - 1.0) * 10)
        
        # Reward component usage
        components_used = len(result.get("components_used", []))
        base_score += min(20, components_used * 5)
        
        # Reward enhancements applied
        enhancements = len(result.get("enhancements_applied", []))
        base_score += min(10, enhancements * 3)
        
        return max(0.0, min(100.0, base_score))
    
    def _assess_integration_health(self) -> Dict:
        """Assess health of component integrations"""
        health = {
            "overall_score": 100.0,
            "component_integrations": {},
            "issues": [],
            "recommendations": []
        }
        
        # Check status line integration
        if self.status_line:
            health["component_integrations"]["status_line"] = "healthy"
        else:
            health["overall_score"] -= 25
            health["issues"].append("Status line not available")
            health["recommendations"].append("Initialize status line system")
        
        # Check context manager integration
        if self.context_manager:
            health["component_integrations"]["context_manager"] = "healthy"
        else:
            health["overall_score"] -= 25
            health["issues"].append("Context manager not available")
            health["recommendations"].append("Initialize context management system")
        
        # Check chat manager integration
        if self.chat_manager:
            health["component_integrations"]["chat_manager"] = "healthy"
        else:
            health["overall_score"] -= 25
            health["issues"].append("Chat manager not available")
            health["recommendations"].append("Initialize chat management system")
        
        # Check legacy compatibility
        if self.legacy_orchestrator:
            health["component_integrations"]["legacy_orchestrator"] = "healthy"
        else:
            health["overall_score"] -= 25
            health["issues"].append("Legacy orchestrator not available")
            health["recommendations"].append("Initialize legacy compatibility layer")
        
        return health
    
    def _generate_system_recommendations(self, status: Dict) -> List[str]:
        """Generate system optimization recommendations"""
        recommendations = []
        
        # Performance recommendations
        if self.metrics["error_count"] > 10:
            recommendations.append("High error count detected - review system stability")
        
        if self.metrics["total_requests"] > 0:
            success_rate = (self.metrics["total_requests"] - self.metrics["error_count"]) / self.metrics["total_requests"]
            if success_rate < 0.95:
                recommendations.append("Success rate below 95% - investigate error patterns")
        
        # Component recommendations
        integration_health = status.get("integration_health", {})
        if integration_health.get("overall_score", 100) < 90:
            recommendations.extend(integration_health.get("recommendations", []))
        
        # Resource recommendations
        for component_status in status.get("component_status", {}).values():
            if isinstance(component_status, dict) and component_status.get("status") == "warning":
                recommendations.append("Component health warning detected - review resource usage")
        
        return recommendations
    
    def _coordination_loop(self):
        """Background coordination between v3.0 components"""
        while self.running:
            try:
                # Coordinate status updates
                if self.status_line and self.chat_manager:
                    chat_health = self.chat_manager.check_conversation_health()
                    self.status_line.update_status(
                        "chat_health",
                        chat_health.action,
                        {"priority": chat_health.priority, "token_usage": chat_health.token_usage}
                    )
                
                # Coordinate context management
                if self.context_manager and self.chat_manager:
                    context_health = self.context_manager.get_context_health()
                    if context_health["status"] == "critical":
                        # Trigger emergency handoff
                        handoff_suggestions = self.chat_manager.get_handoff_suggestions()
                        for suggestion in handoff_suggestions:
                            if suggestion.get("urgency") == "high":
                                self.chat_manager.execute_intelligent_handoff(
                                    trigger=HandoffTrigger.EMERGENCY
                                )
                                break
                
                time.sleep(5)  # Coordinate every 5 seconds
                
            except Exception:
                time.sleep(5)  # Continue coordination loop
    
    # Additional helper methods
    def _analyze_workflow_request(self, request: Dict) -> Dict:
        return {"complexity": "medium", "estimated_phases": 3}
    
    def _create_v3_execution_plan(self, analysis: Dict) -> Dict:
        return {"phases": [{"name": "planning", "agents": ["system-architect"]}]}
    
    def _execute_workflow_phase(self, phase: Dict, workflow_id: str) -> Dict:
        return {"status": "completed", "requires_handoff": False}
    
    def _execute_phase_handoff(self, phase: Dict, phase_result: Dict) -> Dict:
        return {"success": True, "continuity_score": 0.9}
    
    def _determine_optimal_processing(self, status: Dict, event_type: str) -> Dict:
        return {"parallel_capable": True, "resource_efficient": True}
    
    def _map_to_legacy_event_type(self, event_type: str) -> str:
        mapping = {
            "user_prompt": "user_prompt",
            "claude_response": "claude_response",
            "agent_activation": "agent_activation",
            "mcp_request": "mcp_request"
        }
        return mapping.get(event_type, "user_prompt")
    
    def _prepare_legacy_data(self, data: Dict) -> Dict:
        # Clean data for legacy compatibility
        return {k: v for k, v in data.items() if isinstance(v, (str, int, float, bool, dict, list))}


# Global instance
v3_orchestrator = None

def get_v3_orchestrator():
    """Get or create v3.0 orchestrator instance"""
    global v3_orchestrator
    if v3_orchestrator is None:
        v3_orchestrator = ClaudeCodeV3Orchestrator()
        v3_orchestrator.start()
    return v3_orchestrator

def process_hook(event_type: str, data: Dict) -> Dict:
    """Main hook entry point for v3.0 system"""
    orchestrator = get_v3_orchestrator()
    return orchestrator.process_request(event_type, data)

# Export for hook system
__all__ = ['process_hook', 'ClaudeCodeV3Orchestrator', 'get_v3_orchestrator']