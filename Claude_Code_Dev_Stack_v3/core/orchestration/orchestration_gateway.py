#!/usr/bin/env python3
"""
Orchestration Gateway - PHASE 7.3
RESTful API gateway for unified orchestration services

Provides HTTP/WebSocket endpoints for managing and interacting with the 
integrated orchestration layer combining v3 and MCP orchestrators.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import traceback
import uuid

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
from pydantic import BaseModel, Field

# Import orchestration components
import sys
sys.path.append(str(Path(__file__).parent))

try:
    from orchestrator_integration import (
        OrchestrationCoordinator, 
        get_orchestration_coordinator,
        start_integrated_orchestration,
        stop_integrated_orchestration
    )
    from mcp_service_orchestrator import ServiceType, OrchestrationStrategy, FailoverPolicy
except ImportError as e:
    logging.warning(f"Import error: {e}")
    # Fallback for testing
    class OrchestrationCoordinator:
        pass
    get_orchestration_coordinator = lambda: None
    start_integrated_orchestration = lambda: None
    stop_integrated_orchestration = lambda: None
    class ServiceType:
        pass
    class OrchestrationStrategy:
        pass
    class FailoverPolicy:
        pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Claude Code Orchestration Gateway",
    description="Unified API gateway for MCP service orchestration and management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Global state
coordinator: Optional[OrchestrationCoordinator] = None
websocket_connections: List[WebSocket] = []
request_logs: List[Dict[str, Any]] = []
MAX_REQUEST_LOGS = 1000

# Pydantic models
class ServiceRequest(BaseModel):
    service_type: str = Field(..., description="Type of service to request")
    context: Dict[str, Any] = Field(default_factory=dict, description="Request context")
    timeout: Optional[int] = Field(30, description="Request timeout in seconds")
    prefer_strategy: Optional[str] = Field(None, description="Preferred load balancing strategy")

class ServiceResponse(BaseModel):
    success: bool
    service: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str
    request_id: str

class OrchestrationEvent(BaseModel):
    event_type: str = Field(..., description="Type of orchestration event")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event data")
    priority: Optional[str] = Field("normal", description="Event priority")

class HealthCheckResponse(BaseModel):
    status: str
    orchestrators: Dict[str, str]
    services: Dict[str, Any]
    timestamp: str

class MetricsResponse(BaseModel):
    integration_metrics: Dict[str, Any]
    service_metrics: Dict[str, Any]
    timestamp: str

# Dependency functions
async def get_coordinator() -> OrchestrationCoordinator:
    """Get the orchestration coordinator"""
    global coordinator
    if coordinator is None:
        coordinator = get_orchestration_coordinator()
        if coordinator and not coordinator.running:
            await coordinator.start()
    return coordinator

def get_auth_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Simple authentication - expand as needed"""
    if credentials is None:
        return "anonymous"
    # Add actual authentication logic here
    return "authenticated_user"

# Utility functions
def log_request(endpoint: str, data: Dict[str, Any], result: Dict[str, Any]):
    """Log API request for monitoring"""
    global request_logs
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "endpoint": endpoint,
        "data": data,
        "result": result,
        "request_id": str(uuid.uuid4())
    }
    
    request_logs.append(log_entry)
    
    # Keep only recent logs
    if len(request_logs) > MAX_REQUEST_LOGS:
        request_logs = request_logs[-MAX_REQUEST_LOGS:]

async def broadcast_to_websockets(message: Dict[str, Any]):
    """Broadcast message to all connected WebSocket clients"""
    if not websocket_connections:
        return
    
    message_str = json.dumps({
        **message,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    disconnected = []
    for websocket in websocket_connections:
        try:
            await websocket.send_text(message_str)
        except:
            disconnected.append(websocket)
    
    # Remove disconnected clients
    for ws in disconnected:
        websocket_connections.remove(ws)

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize the orchestration gateway"""
    global coordinator
    
    logger.info("Starting Orchestration Gateway...")
    
    try:
        # Start integrated orchestration
        success = await start_integrated_orchestration()
        if success:
            coordinator = get_orchestration_coordinator()
            logger.info("Orchestration Gateway started successfully")
        else:
            logger.error("Failed to start integrated orchestration")
    except Exception as e:
        logger.error(f"Startup error: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Orchestration Gateway...")
    
    try:
        await stop_integrated_orchestration()
        logger.info("Orchestration Gateway shut down successfully")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

# Health and status endpoints
@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    coord = await get_coordinator()
    
    if not coord:
        raise HTTPException(status_code=503, detail="Orchestration coordinator not available")
    
    health = coord.get_service_health()
    
    return HealthCheckResponse(
        status=health["overall_status"],
        orchestrators={
            "v3_orchestrator": health["v3_orchestrator"],
            "mcp_orchestrator": health["mcp_orchestrator"]
        },
        services=health.get("services", {}),
        timestamp=datetime.utcnow().isoformat()
    )

@app.get("/status")
async def get_orchestration_status(user: str = Depends(get_auth_user)):
    """Get comprehensive orchestration status"""
    coord = await get_coordinator()
    
    if not coord:
        raise HTTPException(status_code=503, detail="Orchestration coordinator not available")
    
    try:
        integration_status = coord.get_integration_status()
        service_health = coord.get_service_health()
        
        return {
            "integration": integration_status,
            "health": service_health,
            "gateway": {
                "active_websockets": len(websocket_connections),
                "request_logs_count": len(request_logs),
                "last_activity": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics(user: str = Depends(get_auth_user)):
    """Get orchestration metrics"""
    coord = await get_coordinator()
    
    if not coord:
        raise HTTPException(status_code=503, detail="Orchestration coordinator not available")
    
    try:
        integration_status = coord.get_integration_status()
        
        service_metrics = {}
        if coord.mcp_orchestrator:
            service_metrics = coord.mcp_orchestrator.get_load_balancing_stats()
        
        return MetricsResponse(
            integration_metrics=integration_status.get("metrics", {}),
            service_metrics=service_metrics,
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Service orchestration endpoints
@app.post("/services/request", response_model=ServiceResponse)
async def request_service(
    request: ServiceRequest,
    background_tasks: BackgroundTasks,
    user: str = Depends(get_auth_user)
):
    """Request a service from the orchestrated pool"""
    coord = await get_coordinator()
    request_id = str(uuid.uuid4())
    
    if not coord:
        raise HTTPException(status_code=503, detail="Orchestration coordinator not available")
    
    try:
        # Route the service request
        service_info = await coord.route_service_request(
            request.service_type,
            request.context
        )
        
        if service_info:
            result = ServiceResponse(
                success=True,
                service=service_info,
                timestamp=datetime.utcnow().isoformat(),
                request_id=request_id
            )
            
            # Log successful request
            background_tasks.add_task(
                log_request,
                "request_service",
                request.dict(),
                result.dict()
            )
            
            # Broadcast to websockets
            background_tasks.add_task(
                broadcast_to_websockets,
                {
                    "type": "service_requested",
                    "service_type": request.service_type,
                    "service_info": service_info,
                    "user": user
                }
            )
            
            return result
        else:
            error_msg = f"No available services for type: {request.service_type}"
            result = ServiceResponse(
                success=False,
                error=error_msg,
                timestamp=datetime.utcnow().isoformat(),
                request_id=request_id
            )
            
            # Log failed request
            background_tasks.add_task(
                log_request,
                "request_service",
                request.dict(),
                result.dict()
            )
            
            return result
    
    except Exception as e:
        logger.error(f"Service request error: {e}")
        error_result = ServiceResponse(
            success=False,
            error=str(e),
            timestamp=datetime.utcnow().isoformat(),
            request_id=request_id
        )
        
        # Log error
        background_tasks.add_task(
            log_request,
            "request_service",
            request.dict(),
            error_result.dict()
        )
        
        return error_result

@app.get("/services/types")
async def get_service_types(user: str = Depends(get_auth_user)):
    """Get available service types"""
    try:
        # Return available service types
        service_types = []
        if hasattr(ServiceType, '__members__'):
            service_types = list(ServiceType.__members__.keys())
        else:
            # Fallback
            service_types = ["PLAYWRIGHT", "GITHUB", "WEBSEARCH", "CUSTOM", "CORE", "PROXY", "GATEWAY"]
        
        return {
            "service_types": service_types,
            "strategies": ["ROUND_ROBIN", "LEAST_CONNECTIONS", "FASTEST_RESPONSE", "WEIGHTED_ROUND_ROBIN", "CONSISTENT_HASH", "RESOURCE_AWARE"],
            "failover_policies": ["IMMEDIATE", "GRACEFUL", "CIRCUIT_BREAKER", "RETRY_WITH_BACKOFF"]
        }
    except Exception as e:
        logger.error(f"Service types error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/services/pool/{service_type}")
async def get_service_pool_status(
    service_type: str,
    user: str = Depends(get_auth_user)
):
    """Get status of a specific service pool"""
    coord = await get_coordinator()
    
    if not coord or not coord.mcp_orchestrator:
        raise HTTPException(status_code=503, detail="MCP orchestrator not available")
    
    try:
        status = coord.mcp_orchestrator.get_service_status()
        pool_status = status.get("service_pools", {}).get(service_type.lower())
        
        if not pool_status:
            raise HTTPException(status_code=404, detail=f"Service pool not found: {service_type}")
        
        return pool_status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pool status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/services/load-balancing")
async def get_load_balancing_info(user: str = Depends(get_auth_user)):
    """Get load balancing information"""
    coord = await get_coordinator()
    
    if not coord or not coord.mcp_orchestrator:
        raise HTTPException(status_code=503, detail="MCP orchestrator not available")
    
    try:
        return coord.mcp_orchestrator.get_load_balancing_stats()
    except Exception as e:
        logger.error(f"Load balancing info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Event processing endpoints
@app.post("/events/process")
async def process_orchestration_event(
    event: OrchestrationEvent,
    background_tasks: BackgroundTasks,
    user: str = Depends(get_auth_user)
):
    """Process an orchestration event"""
    coord = await get_coordinator()
    
    if not coord:
        raise HTTPException(status_code=503, detail="Orchestration coordinator not available")
    
    try:
        # Process event through coordinator
        if hasattr(coord, 'event_mappings') and event.event_type in coord.event_mappings:
            result = await coord.event_mappings[event.event_type](event.event_type, event.data)
        else:
            result = {"processed": False, "error": f"Unknown event type: {event.event_type}"}
        
        # Broadcast event processing
        background_tasks.add_task(
            broadcast_to_websockets,
            {
                "type": "event_processed",
                "event_type": event.event_type,
                "result": result,
                "user": user
            }
        )
        
        return {
            "success": result.get("processed", True),
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Event processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Configuration endpoints
@app.get("/config")
async def get_configuration(user: str = Depends(get_auth_user)):
    """Get current orchestration configuration"""
    coord = await get_coordinator()
    
    if not coord:
        raise HTTPException(status_code=503, detail="Orchestration coordinator not available")
    
    try:
        config = {
            "integration_enabled": coord.integration_enabled,
            "coordination_active": coord.running,
            "service_pools": {},
            "gateway_config": {
                "max_websocket_connections": 100,
                "max_request_logs": MAX_REQUEST_LOGS,
                "enable_auth": False
            }
        }
        
        # Get service pool configurations
        if coord.mcp_orchestrator and hasattr(coord.mcp_orchestrator, 'service_pools'):
            for service_type, pool in coord.mcp_orchestrator.service_pools.items():
                config["service_pools"][service_type.value] = {
                    "strategy": pool.strategy.value,
                    "failover_policy": pool.failover_policy.value,
                    "health_check_interval": pool.health_check_interval,
                    "max_retries": pool.max_retries,
                    "retry_delay": pool.retry_delay
                }
        
        return config
    
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Monitoring endpoints
@app.get("/logs")
async def get_request_logs(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    user: str = Depends(get_auth_user)
):
    """Get request logs"""
    try:
        total_logs = len(request_logs)
        start_idx = max(0, total_logs - offset - limit)
        end_idx = total_logs - offset
        
        logs = request_logs[start_idx:end_idx]
        logs.reverse()  # Most recent first
        
        return {
            "logs": logs,
            "total": total_logs,
            "offset": offset,
            "limit": limit
        }
    
    except Exception as e:
        logger.error(f"Logs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/logs")
async def clear_request_logs(user: str = Depends(get_auth_user)):
    """Clear request logs"""
    global request_logs
    
    try:
        cleared_count = len(request_logs)
        request_logs = []
        
        return {
            "success": True,
            "cleared_count": cleared_count,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Clear logs error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time orchestration updates"""
    await websocket.accept()
    websocket_connections.append(websocket)
    
    try:
        # Send initial status
        coord = await get_coordinator()
        if coord:
            status = coord.get_integration_status()
            await websocket.send_text(json.dumps({
                "type": "initial_status",
                "status": status,
                "timestamp": datetime.utcnow().isoformat()
            }))
        
        # Keep connection alive and handle client messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle client requests
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                elif message.get("type") == "status_request":
                    if coord:
                        status = coord.get_integration_status()
                        await websocket.send_text(json.dumps({
                            "type": "status_update",
                            "status": status,
                            "timestamp": datetime.utcnow().isoformat()
                        }))
            
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.utcnow().isoformat()
                }))
            except Exception as e:
                logger.error(f"WebSocket message error: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }))
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)

# Dashboard endpoint (simple HTML interface)
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Simple dashboard for monitoring orchestration"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Orchestration Dashboard</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { max-width: 1200px; margin: 0 auto; }
            .status-card { 
                background: #f5f5f5; border: 1px solid #ddd; 
                border-radius: 5px; padding: 15px; margin: 10px 0; 
            }
            .status-healthy { border-left: 5px solid #4CAF50; }
            .status-warning { border-left: 5px solid #FF9800; }
            .status-error { border-left: 5px solid #F44336; }
            .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; }
            .metric { background: white; padding: 10px; border-radius: 3px; text-align: center; }
            .logs { max-height: 400px; overflow-y: auto; background: #f9f9f9; padding: 10px; border-radius: 3px; }
            .log-entry { margin: 5px 0; padding: 5px; background: white; border-radius: 2px; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Claude Code Orchestration Dashboard</h1>
            
            <div id="status" class="status-card">
                <h3>Loading status...</h3>
            </div>
            
            <div class="metrics" id="metrics">
                <!-- Metrics will be loaded here -->
            </div>
            
            <div class="status-card">
                <h3>Recent Activity</h3>
                <div id="logs" class="logs">
                    <!-- Logs will be loaded here -->
                </div>
            </div>
        </div>
        
        <script>
            const ws = new WebSocket(`ws://${window.location.host}/ws`);
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
            };
            
            function updateDashboard(data) {
                if (data.type === 'initial_status' || data.type === 'status_update') {
                    updateStatus(data.status);
                }
            }
            
            function updateStatus(status) {
                const statusDiv = document.getElementById('status');
                const integration = status.integration_enabled;
                const coordination = status.coordination_active;
                
                let statusClass = 'status-healthy';
                let statusText = 'Operational';
                
                if (!integration || !coordination) {
                    statusClass = 'status-warning';
                    statusText = 'Degraded';
                }
                
                statusDiv.className = `status-card ${statusClass}`;
                statusDiv.innerHTML = `
                    <h3>System Status: ${statusText}</h3>
                    <p>Integration Enabled: ${integration}</p>
                    <p>Coordination Active: ${coordination}</p>
                    <p>Last Update: ${status.timestamp}</p>
                `;
                
                // Update metrics
                updateMetrics(status.metrics);
            }
            
            function updateMetrics(metrics) {
                const metricsDiv = document.getElementById('metrics');
                metricsDiv.innerHTML = `
                    <div class="metric">
                        <h4>Events Processed</h4>
                        <p>${metrics.events_processed || 0}</p>
                    </div>
                    <div class="metric">
                        <h4>Events Forwarded</h4>
                        <p>${metrics.events_forwarded || 0}</p>
                    </div>
                    <div class="metric">
                        <h4>Coordination Cycles</h4>
                        <p>${metrics.coordination_cycles || 0}</p>
                    </div>
                    <div class="metric">
                        <h4>Errors</h4>
                        <p>${metrics.errors || 0}</p>
                    </div>
                `;
            }
            
            // Load initial data
            fetch('/status')
                .then(response => response.json())
                .then(data => updateStatus(data.integration))
                .catch(error => console.error('Error loading status:', error));
            
            // Refresh every 30 seconds
            setInterval(() => {
                ws.send(JSON.stringify({type: 'status_request'}));
            }, 30000);
        </script>
    </body>
    </html>
    """
    return html_content

# Utility endpoints
@app.post("/admin/restart")
async def restart_orchestration(
    background_tasks: BackgroundTasks,
    user: str = Depends(get_auth_user)
):
    """Restart the orchestration system"""
    try:
        # Stop current orchestration
        await stop_integrated_orchestration()
        
        # Start again
        success = await start_integrated_orchestration()
        
        if success:
            background_tasks.add_task(
                broadcast_to_websockets,
                {
                    "type": "system_restarted",
                    "user": user
                }
            )
            
            return {
                "success": True,
                "message": "Orchestration system restarted successfully",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to restart orchestration system")
    
    except Exception as e:
        logger.error(f"Restart error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if app.debug else "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Main entry point
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Orchestration Gateway API")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--log-level", default="info", help="Log level")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    if args.debug:
        app.debug = True
        logging.getLogger().setLevel(logging.DEBUG)
    
    uvicorn.run(
        "orchestration_gateway:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level
    )