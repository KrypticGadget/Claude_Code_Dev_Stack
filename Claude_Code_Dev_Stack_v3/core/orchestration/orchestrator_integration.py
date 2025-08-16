#!/usr/bin/env python3
"""
Orchestrator Integration Layer - PHASE 7.3
Seamless integration between MCP Service Orchestrator and v3_orchestrator.py

This module provides the bridge between the existing v3 orchestrator and the new
MCP service orchestrator, ensuring unified operation and coordination.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
import threading
import time

# Import components
import sys
sys.path.append(str(Path(__file__).parent.parent / "hooks" / "hooks"))
sys.path.append(str(Path(__file__).parent))

try:
    from v3_orchestrator import ClaudeCodeV3Orchestrator, get_v3_orchestrator
    from mcp_service_orchestrator import MCPServiceOrchestrator, get_mcp_orchestrator, ServiceType
except ImportError as e:
    logging.warning(f"Import error: {e}")
    # Fallback classes for testing
    class ClaudeCodeV3Orchestrator:
        pass
    class MCPServiceOrchestrator:
        pass
    get_v3_orchestrator = lambda: None
    get_mcp_orchestrator = lambda: None
    class ServiceType:
        pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrchestrationCoordinator:
    """
    Coordinates between v3 orchestrator and MCP service orchestrator
    Provides unified interface and seamless operation
    """
    
    def __init__(self):
        self.v3_orchestrator = None
        self.mcp_orchestrator = None
        self.integration_enabled = False
        self.coordination_thread = None
        self.running = False
        
        # Integration state
        self.integration_state = {
            "v3_orchestrator_active": False,
            "mcp_orchestrator_active": False,
            "coordination_active": False,
            "last_sync": None,
            "sync_count": 0,
            "errors": []
        }
        
        # Event mapping
        self.event_mappings = {
            # v3 -> MCP mappings
            "user_prompt": self._handle_user_prompt,
            "claude_response": self._handle_claude_response,
            "agent_activation": self._handle_agent_activation,
            "mcp_request": self._handle_mcp_request,
            "service_request": self._handle_service_request,
            
            # MCP -> v3 mappings
            "service_health_warning": self._handle_health_warning,
            "service_failover": self._handle_failover,
            "service_recovery": self._handle_recovery,
            "load_balance_update": self._handle_load_balance_update
        }
        
        # Metrics
        self.integration_metrics = {
            "events_processed": 0,
            "events_forwarded": 0,
            "coordination_cycles": 0,
            "errors": 0,
            "last_activity": None
        }
    
    async def initialize(self):
        """Initialize the coordination system"""
        logger.info("Initializing Orchestration Coordinator...")
        
        try:
            # Get orchestrator instances
            self.v3_orchestrator = get_v3_orchestrator()
            self.mcp_orchestrator = get_mcp_orchestrator()
            
            # Initialize MCP orchestrator if not already done
            if self.mcp_orchestrator and not hasattr(self.mcp_orchestrator, 'running'):
                await self.mcp_orchestrator.initialize()
            
            # Check availability
            self.integration_state["v3_orchestrator_active"] = self.v3_orchestrator is not None
            self.integration_state["mcp_orchestrator_active"] = self.mcp_orchestrator is not None
            
            if self.integration_state["v3_orchestrator_active"] and self.integration_state["mcp_orchestrator_active"]:
                await self._setup_integration()
                self.integration_enabled = True
                logger.info("Orchestration Coordinator initialized successfully")
            else:
                logger.warning("One or more orchestrators not available for integration")
                
        except Exception as e:
            logger.error(f"Failed to initialize Orchestration Coordinator: {e}")
            self.integration_state["errors"].append(str(e))
    
    async def start(self):
        """Start the coordination system"""
        if not self.integration_enabled:
            await self.initialize()
        
        if not self.integration_enabled:
            logger.error("Cannot start coordination - integration not enabled")
            return False
        
        self.running = True
        
        # Start MCP orchestrator
        if self.mcp_orchestrator and not getattr(self.mcp_orchestrator, 'running', False):
            await self.mcp_orchestrator.start()
        
        # Start coordination thread
        self.coordination_thread = threading.Thread(target=self._coordination_loop, daemon=True)
        self.coordination_thread.start()
        
        self.integration_state["coordination_active"] = True
        logger.info("Orchestration Coordinator started")
        return True
    
    async def stop(self):
        """Stop the coordination system"""
        self.running = False
        self.integration_state["coordination_active"] = False
        
        if self.coordination_thread:
            self.coordination_thread.join(timeout=5)
        
        # Stop MCP orchestrator
        if self.mcp_orchestrator and getattr(self.mcp_orchestrator, 'running', False):
            await self.mcp_orchestrator.stop()
        
        logger.info("Orchestration Coordinator stopped")
    
    async def _setup_integration(self):
        """Setup integration between orchestrators"""
        try:
            # Enhance v3 orchestrator with MCP capabilities
            await self._enhance_v3_orchestrator()
            
            # Setup event forwarding
            await self._setup_event_forwarding()
            
            # Setup status synchronization
            await self._setup_status_sync()
            
            logger.info("Integration setup completed")
            
        except Exception as e:
            logger.error(f"Integration setup failed: {e}")
            raise
    
    async def _enhance_v3_orchestrator(self):
        """Enhance v3 orchestrator with MCP service capabilities"""
        if not self.v3_orchestrator:
            return
        
        # Store original methods
        original_process_request = self.v3_orchestrator.process_request
        original_get_system_status = self.v3_orchestrator.get_system_status
        
        # Enhanced request processing
        def enhanced_process_request(event_type: str, data: Dict) -> Dict:
            result = original_process_request(event_type, data)
            
            # Add MCP orchestration
            if event_type in self.event_mappings:
                try:
                    mcp_result = asyncio.run(self.event_mappings[event_type](event_type, data))
                    result["mcp_orchestration"] = mcp_result
                    result["components_used"].append("mcp_orchestrator")
                    
                    # Update enhancement tracking
                    if "mcp_enhancement" not in result["enhancements_applied"]:
                        result["enhancements_applied"].append("mcp_enhancement")
                        
                except Exception as e:
                    logger.error(f"MCP orchestration error: {e}")
                    result["mcp_orchestration"] = {"error": str(e)}
            
            return result
        
        # Enhanced system status
        def enhanced_get_system_status() -> Dict:
            status = original_get_system_status()
            
            # Add MCP orchestrator status
            if self.mcp_orchestrator:
                try:
                    mcp_status = self.mcp_orchestrator.get_service_status()
                    status["mcp_orchestrator"] = mcp_status
                    status["component_status"]["mcp_orchestrator"] = {
                        "status": "healthy" if mcp_status.get("orchestrator_status") == "running" else "error",
                        "services": mcp_status.get("total_services", 0),
                        "healthy_services": mcp_status.get("healthy_services", 0),
                        "availability": mcp_status.get("service_availability", "0%")
                    }
                except Exception as e:
                    status["mcp_orchestrator"] = {"error": str(e)}
                    status["component_status"]["mcp_orchestrator"] = {"status": "error"}
            
            # Add integration status
            status["integration"] = {
                "coordinator_active": self.running,
                "integration_enabled": self.integration_enabled,
                "integration_state": self.integration_state,
                "integration_metrics": self.integration_metrics
            }
            
            return status
        
        # Replace methods
        self.v3_orchestrator.process_request = enhanced_process_request
        self.v3_orchestrator.get_system_status = enhanced_get_system_status
        
        # Add MCP orchestrator reference
        self.v3_orchestrator.mcp_orchestrator = self.mcp_orchestrator
        
        logger.info("v3 orchestrator enhanced with MCP capabilities")
    
    async def _setup_event_forwarding(self):
        """Setup bidirectional event forwarding"""
        if not (self.v3_orchestrator and self.mcp_orchestrator):
            return
        
        # Setup MCP message queue subscribers for v3 events
        if hasattr(self.mcp_orchestrator, 'message_queue'):
            self.mcp_orchestrator.message_queue.subscribe(
                "service_health_warning", 
                self._forward_to_v3
            )
            self.mcp_orchestrator.message_queue.subscribe(
                "service_failover", 
                self._forward_to_v3
            )
            self.mcp_orchestrator.message_queue.subscribe(
                "service_recovery", 
                self._forward_to_v3
            )
        
        logger.info("Event forwarding setup completed")
    
    async def _setup_status_sync(self):
        """Setup status synchronization between orchestrators"""
        if not (self.v3_orchestrator and self.mcp_orchestrator):
            return
        
        # Update v3 orchestrator system state
        if hasattr(self.v3_orchestrator, 'system_state'):
            self.v3_orchestrator.system_state["components"]["mcp_orchestrator"] = True
        
        logger.info("Status synchronization setup completed")
    
    def _coordination_loop(self):
        """Background coordination loop"""
        while self.running:
            try:
                # Perform coordination cycle
                asyncio.run(self._coordination_cycle())
                self.integration_metrics["coordination_cycles"] += 1
                
                # Update sync time
                self.integration_state["last_sync"] = datetime.utcnow().isoformat()
                self.integration_state["sync_count"] += 1
                
                time.sleep(5)  # Coordinate every 5 seconds
                
            except Exception as e:
                logger.error(f"Coordination cycle error: {e}")
                self.integration_metrics["errors"] += 1
                self.integration_state["errors"].append(str(e))
                time.sleep(5)
    
    async def _coordination_cycle(self):
        """Single coordination cycle"""
        try:
            # Sync health status
            await self._sync_health_status()
            
            # Sync metrics
            await self._sync_metrics()
            
            # Check for required actions
            await self._check_coordination_actions()
            
        except Exception as e:
            logger.debug(f"Coordination cycle error: {e}")
    
    async def _sync_health_status(self):
        """Synchronize health status between orchestrators"""
        if not (self.v3_orchestrator and self.mcp_orchestrator):
            return
        
        try:
            # Get MCP service health
            mcp_status = self.mcp_orchestrator.get_service_status()
            
            # Update v3 orchestrator status line if available
            if hasattr(self.v3_orchestrator, 'status_line') and self.v3_orchestrator.status_line:
                self.v3_orchestrator.status_line.update_status(
                    "mcp_services",
                    "healthy" if mcp_status.get("healthy_services", 0) > 0 else "warning",
                    {
                        "total_services": mcp_status.get("total_services", 0),
                        "healthy_services": mcp_status.get("healthy_services", 0),
                        "availability": mcp_status.get("service_availability", "0%")
                    }
                )
        
        except Exception as e:
            logger.debug(f"Health sync error: {e}")
    
    async def _sync_metrics(self):
        """Synchronize metrics between orchestrators"""
        try:
            # Update integration metrics
            self.integration_metrics["last_activity"] = datetime.utcnow().isoformat()
            
            # Sync with v3 orchestrator metrics if available
            if hasattr(self.v3_orchestrator, 'metrics'):
                # Add MCP metrics to v3 metrics
                if self.mcp_orchestrator:
                    mcp_metrics = self.mcp_orchestrator.metrics
                    self.v3_orchestrator.metrics["mcp_requests"] = mcp_metrics.total_requests
                    self.v3_orchestrator.metrics["mcp_failovers"] = mcp_metrics.failover_count
                    self.v3_orchestrator.metrics["mcp_availability"] = mcp_metrics.service_availability
        
        except Exception as e:
            logger.debug(f"Metrics sync error: {e}")
    
    async def _check_coordination_actions(self):
        """Check if any coordination actions are needed"""
        try:
            # Check for degraded services
            if self.mcp_orchestrator:
                status = self.mcp_orchestrator.get_service_status()
                availability = float(status.get("service_availability", "0").rstrip("%"))
                
                if availability < 50:  # Less than 50% availability
                    logger.warning(f"Low service availability: {availability}%")
                    
                    # Trigger emergency coordination if v3 orchestrator supports it
                    if hasattr(self.v3_orchestrator, 'chat_manager') and self.v3_orchestrator.chat_manager:
                        # Could trigger emergency handoff or other actions
                        pass
        
        except Exception as e:
            logger.debug(f"Coordination action check error: {e}")
    
    # Event handlers
    
    async def _handle_user_prompt(self, event_type: str, data: Dict) -> Dict:
        """Handle user prompt events"""
        self.integration_metrics["events_processed"] += 1
        
        # Check if prompt requires MCP services
        prompt = data.get("prompt", "")
        
        # Simple heuristics for service type detection
        if any(keyword in prompt.lower() for keyword in ["browser", "web", "page", "screenshot"]):
            service = await self.mcp_orchestrator.route_request(ServiceType.PLAYWRIGHT)
            if service:
                return {
                    "service_routed": True,
                    "service_type": "playwright",
                    "service_url": service.url,
                    "service_id": service.id
                }
        
        elif any(keyword in prompt.lower() for keyword in ["github", "repository", "repo", "code"]):
            service = await self.mcp_orchestrator.route_request(ServiceType.GITHUB)
            if service:
                return {
                    "service_routed": True,
                    "service_type": "github", 
                    "service_url": service.url,
                    "service_id": service.id
                }
        
        elif any(keyword in prompt.lower() for keyword in ["search", "find", "lookup", "web search"]):
            service = await self.mcp_orchestrator.route_request(ServiceType.WEBSEARCH)
            if service:
                return {
                    "service_routed": True,
                    "service_type": "websearch",
                    "service_url": service.url,
                    "service_id": service.id
                }
        
        return {"service_routed": False}
    
    async def _handle_claude_response(self, event_type: str, data: Dict) -> Dict:
        """Handle Claude response events"""
        self.integration_metrics["events_processed"] += 1
        
        # Could analyze response for service usage patterns
        return {"processed": True}
    
    async def _handle_agent_activation(self, event_type: str, data: Dict) -> Dict:
        """Handle agent activation events"""
        self.integration_metrics["events_processed"] += 1
        
        agent_type = data.get("agent_type", "")
        
        # Route to appropriate MCP service based on agent type
        service_mapping = {
            "frontend": ServiceType.PLAYWRIGHT,
            "backend": ServiceType.GITHUB,
            "testing": ServiceType.PLAYWRIGHT,
            "integration": ServiceType.CUSTOM
        }
        
        if agent_type in service_mapping:
            service = await self.mcp_orchestrator.route_request(service_mapping[agent_type])
            if service:
                return {
                    "mcp_service_allocated": True,
                    "service_id": service.id,
                    "service_url": service.url
                }
        
        return {"mcp_service_allocated": False}
    
    async def _handle_mcp_request(self, event_type: str, data: Dict) -> Dict:
        """Handle direct MCP requests"""
        self.integration_metrics["events_processed"] += 1
        
        service_type_str = data.get("service_type", "custom")
        request_context = data.get("context", {})
        
        try:
            service_type = ServiceType(service_type_str)
            service = await self.mcp_orchestrator.route_request(service_type, request_context)
            
            if service:
                return {
                    "success": True,
                    "service": {
                        "id": service.id,
                        "name": service.name,
                        "url": service.url,
                        "type": service.service_type.value
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"No available services for type: {service_type}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _handle_service_request(self, event_type: str, data: Dict) -> Dict:
        """Handle generic service requests"""
        return await self._handle_mcp_request(event_type, data)
    
    async def _handle_health_warning(self, event_type: str, data: Dict) -> Dict:
        """Handle service health warnings"""
        self.integration_metrics["events_processed"] += 1
        
        # Forward to v3 orchestrator status line
        if hasattr(self.v3_orchestrator, 'status_line') and self.v3_orchestrator.status_line:
            self.v3_orchestrator.status_line.update_status(
                "mcp_health_warning",
                "warning",
                data
            )
        
        return {"forwarded": True}
    
    async def _handle_failover(self, event_type: str, data: Dict) -> Dict:
        """Handle service failover events"""
        self.integration_metrics["events_processed"] += 1
        
        # Could trigger emergency measures in v3 orchestrator
        logger.info(f"Service failover detected: {data}")
        
        return {"processed": True}
    
    async def _handle_recovery(self, event_type: str, data: Dict) -> Dict:
        """Handle service recovery events"""
        self.integration_metrics["events_processed"] += 1
        
        # Update v3 orchestrator that service is back online
        if hasattr(self.v3_orchestrator, 'status_line') and self.v3_orchestrator.status_line:
            self.v3_orchestrator.status_line.update_status(
                "mcp_service_recovery",
                "healthy",
                data
            )
        
        return {"processed": True}
    
    async def _handle_load_balance_update(self, event_type: str, data: Dict) -> Dict:
        """Handle load balancing updates"""
        self.integration_metrics["events_processed"] += 1
        return {"processed": True}
    
    async def _forward_to_v3(self, message: Dict[str, Any]):
        """Forward MCP events to v3 orchestrator"""
        try:
            self.integration_metrics["events_forwarded"] += 1
            
            # Process through v3 orchestrator if needed
            if self.v3_orchestrator and hasattr(self.v3_orchestrator, 'process_request'):
                # Convert MCP event to v3 event format
                event_type = message.get("type", "mcp_event")
                self.v3_orchestrator.process_request(event_type, message)
        
        except Exception as e:
            logger.error(f"Failed to forward event to v3: {e}")
    
    # Public API methods
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get comprehensive integration status"""
        return {
            "integration_enabled": self.integration_enabled,
            "coordination_active": self.running,
            "orchestrators": {
                "v3_active": self.integration_state["v3_orchestrator_active"],
                "mcp_active": self.integration_state["mcp_orchestrator_active"]
            },
            "state": self.integration_state,
            "metrics": self.integration_metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def route_service_request(self, service_type_str: str, context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Route a service request through the integrated system"""
        if not self.mcp_orchestrator:
            return None
        
        try:
            service_type = ServiceType(service_type_str)
            service = await self.mcp_orchestrator.route_request(service_type, context or {})
            
            if service:
                return {
                    "id": service.id,
                    "name": service.name,
                    "url": service.url,
                    "type": service.service_type.value,
                    "status": service.status.value
                }
        except Exception as e:
            logger.error(f"Service routing error: {e}")
        
        return None
    
    def get_service_health(self) -> Dict[str, Any]:
        """Get overall service health across both orchestrators"""
        health = {
            "overall_status": "unknown",
            "v3_orchestrator": "unknown",
            "mcp_orchestrator": "unknown",
            "services": {}
        }
        
        # Get v3 status
        if self.v3_orchestrator:
            try:
                v3_status = self.v3_orchestrator.get_system_status()
                health["v3_orchestrator"] = v3_status.get("system_state", {}).get("health", "unknown")
            except:
                health["v3_orchestrator"] = "error"
        
        # Get MCP status
        if self.mcp_orchestrator:
            try:
                mcp_status = self.mcp_orchestrator.get_service_status()
                health["mcp_orchestrator"] = "healthy" if mcp_status.get("healthy_services", 0) > 0 else "degraded"
                health["services"] = mcp_status
            except:
                health["mcp_orchestrator"] = "error"
        
        # Determine overall status
        if health["v3_orchestrator"] == "operational" and health["mcp_orchestrator"] == "healthy":
            health["overall_status"] = "healthy"
        elif "error" in [health["v3_orchestrator"], health["mcp_orchestrator"]]:
            health["overall_status"] = "error"
        else:
            health["overall_status"] = "degraded"
        
        return health


# Global coordinator instance
coordination_instance: Optional[OrchestrationCoordinator] = None

def get_orchestration_coordinator() -> OrchestrationCoordinator:
    """Get or create orchestration coordinator instance"""
    global coordination_instance
    if coordination_instance is None:
        coordination_instance = OrchestrationCoordinator()
    return coordination_instance

async def start_integrated_orchestration():
    """Start the integrated orchestration system"""
    coordinator = get_orchestration_coordinator()
    success = await coordinator.start()
    if success:
        logger.info("Integrated orchestration system started successfully")
    else:
        logger.error("Failed to start integrated orchestration system")
    return success

async def stop_integrated_orchestration():
    """Stop the integrated orchestration system"""
    global coordination_instance
    if coordination_instance:
        await coordination_instance.stop()
        coordination_instance = None

# Convenience function for easy integration
def integrate_orchestrators():
    """Simple function to integrate orchestrators"""
    async def _integrate():
        coordinator = get_orchestration_coordinator()
        await coordinator.initialize()
        return coordinator
    
    return asyncio.run(_integrate())


if __name__ == "__main__":
    async def main():
        """Example usage"""
        coordinator = OrchestrationCoordinator()
        
        try:
            success = await coordinator.start()
            if success:
                print("Integration started successfully")
                
                # Test service routing
                service_info = await coordinator.route_service_request("playwright")
                if service_info:
                    print(f"Routed to service: {service_info}")
                
                # Get status
                status = coordinator.get_integration_status()
                print(f"Integration Status: {json.dumps(status, indent=2)}")
                
                # Keep running for demonstration
                await asyncio.sleep(10)
            else:
                print("Failed to start integration")
        
        finally:
            await coordinator.stop()
    
    asyncio.run(main())