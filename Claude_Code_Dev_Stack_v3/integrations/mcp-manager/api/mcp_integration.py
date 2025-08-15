#!/usr/bin/env python3
"""
MCP Manager Integration API
FastAPI service for integrating with the PWA MCPManager component

Original concept by @qdhenry (MIT License)
Enhanced for Claude Code Dev Stack by DevOps Agent
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.manager import MCPManager, ServiceType, ServiceStatus
from services.playwright_service import create_playwright_service
from services.github_service import create_github_service
from services.websearch_service import create_websearch_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MCP Manager Integration API",
    description="API for managing MCP services and integrating with PWA components",
    version="1.0.0"
)

# Add CORS middleware for PWA integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
mcp_manager: Optional[MCPManager] = None
websocket_connections: List[WebSocket] = []
service_instances = {}

# Pydantic models for API
class ServiceConfig(BaseModel):
    name: str
    type: str
    host: str = "localhost"
    port: int
    path: str = "/"
    protocol: str = "http"
    description: str = ""
    tags: List[str] = []
    metadata: Dict[str, Any] = {}

class ServiceAction(BaseModel):
    action: str  # start, stop, restart
    service_id: Optional[str] = None
    service_name: Optional[str] = None

class MCPConfiguration(BaseModel):
    health_check_interval: int = 30
    load_balancing: Dict[str, Any] = {"default_algorithm": "round_robin"}
    logging: Dict[str, Any] = {"level": "INFO", "file": "mcp-manager.log"}

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize MCP Manager on startup"""
    global mcp_manager
    
    logger.info("Starting MCP Manager Integration API")
    
    # Initialize MCP Manager
    mcp_manager = MCPManager()
    
    # Start the manager
    await mcp_manager.start()
    
    # Register default services
    await setup_default_services()
    
    logger.info("MCP Manager Integration API started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global mcp_manager, service_instances
    
    logger.info("Shutting down MCP Manager Integration API")
    
    # Stop all service instances
    for service in service_instances.values():
        try:
            await service.stop()
        except Exception as e:
            logger.error(f"Error stopping service: {e}")
    
    # Stop MCP Manager
    if mcp_manager:
        await mcp_manager.stop()
    
    logger.info("MCP Manager Integration API shut down")

async def setup_default_services():
    """Setup default MCP services"""
    global mcp_manager, service_instances
    
    default_services = [
        {
            "name": "Playwright MCP",
            "type": "playwright",
            "port": 8080,
            "config": {"headless": True, "browser_type": "chromium"}
        },
        {
            "name": "GitHub MCP", 
            "type": "github",
            "port": 8081,
            "config": {"github_token": os.getenv("GITHUB_TOKEN")}
        },
        {
            "name": "WebSearch MCP",
            "type": "websearch", 
            "port": 8082,
            "config": {"search_engines": ["duckduckgo", "bing"]}
        }
    ]
    
    for service_def in default_services:
        try:
            # Create service instance
            service_config = {
                "host": "localhost",
                "port": service_def["port"],
                **service_def["config"]
            }
            
            if service_def["type"] == "playwright":
                service = create_playwright_service(service_config)
            elif service_def["type"] == "github":
                service = create_github_service(service_config)
            elif service_def["type"] == "websearch":
                service = create_websearch_service(service_config)
            else:
                continue
            
            # Store service instance
            service_instances[service_def["name"]] = service
            
            # Register with MCP Manager
            await mcp_manager.register_external_service({
                "name": service_def["name"],
                "type": service_def["type"],
                "host": "localhost",
                "port": service_def["port"],
                "description": f"{service_def['name']} service"
            })
            
            logger.info(f"Registered service: {service_def['name']}")
            
        except Exception as e:
            logger.error(f"Failed to setup service {service_def['name']}: {e}")

async def broadcast_to_websockets(message: Dict[str, Any]):
    """Broadcast message to all connected WebSocket clients"""
    if not websocket_connections:
        return
    
    message_str = json.dumps(message)
    disconnected = []
    
    for websocket in websocket_connections:
        try:
            await websocket.send_text(message_str)
        except:
            disconnected.append(websocket)
    
    # Remove disconnected clients
    for ws in disconnected:
        websocket_connections.remove(ws)

# Health and status endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global mcp_manager
    
    if not mcp_manager:
        raise HTTPException(status_code=503, detail="MCP Manager not initialized")
    
    status = mcp_manager.get_service_status()
    
    return {
        "status": "healthy",
        "service": "mcp-integration-api",
        "version": "1.0.0",
        "mcp_manager": {
            "running": mcp_manager.running,
            "services": status
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/mcp/status")
async def get_mcp_status():
    """Get overall MCP service status"""
    global mcp_manager
    
    if not mcp_manager:
        raise HTTPException(status_code=503, detail="MCP Manager not initialized")
    
    return mcp_manager.get_service_status()

# Service management endpoints
@app.get("/mcp/services")
async def get_services(service_type: Optional[str] = None, status: Optional[str] = None):
    """Get all registered MCP services"""
    global mcp_manager
    
    if not mcp_manager:
        raise HTTPException(status_code=503, detail="MCP Manager not initialized")
    
    services = mcp_manager.get_all_services()
    
    # Filter by type if specified
    if service_type:
        services = [s for s in services if s.service_type.value == service_type]
    
    # Filter by status if specified
    if status:
        services = [s for s in services if s.status.value == status]
    
    # Convert to dict format for JSON response
    services_data = []
    for service in services:
        services_data.append({
            "id": service.id,
            "name": service.name,
            "type": service.service_type.value,
            "host": service.host,
            "port": service.port,
            "status": service.status.value,
            "version": service.version,
            "description": service.description,
            "url": service.url,
            "is_healthy": service.is_healthy,
            "metrics": {
                "requests_total": service.metrics.requests_total,
                "requests_per_second": service.metrics.requests_per_second,
                "error_count": service.metrics.error_count,
                "response_time_avg": service.metrics.response_time_avg,
                "cpu_usage": service.metrics.cpu_usage,
                "memory_usage": service.metrics.memory_usage,
                "uptime": service.metrics.uptime.total_seconds() if service.metrics.uptime else 0
            },
            "last_seen": service.last_seen.isoformat() if service.last_seen else None,
            "tags": list(service.tags)
        })
    
    return {"services": services_data}

@app.get("/mcp/services/{service_id}")
async def get_service(service_id: str):
    """Get specific service by ID"""
    global mcp_manager
    
    if not mcp_manager:
        raise HTTPException(status_code=503, detail="MCP Manager not initialized")
    
    service = mcp_manager.registry.get_service(service_id)
    
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    return {
        "id": service.id,
        "name": service.name,
        "type": service.service_type.value,
        "host": service.host,
        "port": service.port,
        "status": service.status.value,
        "version": service.version,
        "description": service.description,
        "url": service.url,
        "is_healthy": service.is_healthy,
        "metrics": {
            "requests_total": service.metrics.requests_total,
            "requests_per_second": service.metrics.requests_per_second,
            "error_count": service.metrics.error_count,
            "response_time_avg": service.metrics.response_time_avg,
            "cpu_usage": service.metrics.cpu_usage,
            "memory_usage": service.metrics.memory_usage,
            "uptime": service.metrics.uptime.total_seconds() if service.metrics.uptime else 0
        },
        "last_seen": service.last_seen.isoformat() if service.last_seen else None,
        "tags": list(service.tags),
        "metadata": service.metadata
    }

@app.post("/mcp/services")
async def register_service(service_config: ServiceConfig):
    """Register a new MCP service"""
    global mcp_manager
    
    if not mcp_manager:
        raise HTTPException(status_code=503, detail="MCP Manager not initialized")
    
    try:
        config_dict = {
            "name": service_config.name,
            "type": service_config.type,
            "host": service_config.host,
            "port": service_config.port,
            "path": service_config.path,
            "protocol": service_config.protocol,
            "description": service_config.description,
            "tags": service_config.tags,
            "metadata": service_config.metadata
        }
        
        success = await mcp_manager.register_external_service(config_dict)
        
        if success:
            # Broadcast update to WebSocket clients
            await broadcast_to_websockets({
                "type": "service_registered",
                "service": config_dict,
                "timestamp": datetime.now().isoformat()
            })
            
            return {"status": "success", "message": "Service registered successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to register service")
    
    except Exception as e:
        logger.error(f"Error registering service: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mcp/services/{service_id}/actions")
async def service_action(service_id: str, action: ServiceAction):
    """Perform action on a service (start, stop, restart)"""
    global mcp_manager, service_instances
    
    if not mcp_manager:
        raise HTTPException(status_code=503, detail="MCP Manager not initialized")
    
    service = mcp_manager.registry.get_service(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    try:
        # Find service instance
        service_instance = None
        for name, instance in service_instances.items():
            if instance.get_service_instance().id == service_id:
                service_instance = instance
                break
        
        if not service_instance:
            raise HTTPException(status_code=400, detail="Service instance not found")
        
        if action.action == "start":
            success = await service_instance.start()
        elif action.action == "stop":
            success = await service_instance.stop()
        elif action.action == "restart":
            success = await service_instance.restart()
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        if success:
            # Broadcast update to WebSocket clients
            await broadcast_to_websockets({
                "type": "service_action",
                "service_id": service_id,
                "action": action.action,
                "success": True,
                "timestamp": datetime.now().isoformat()
            })
            
            return {"status": "success", "action": action.action}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to {action.action} service")
    
    except Exception as e:
        logger.error(f"Error performing service action: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/mcp/services/{service_id}")
async def unregister_service(service_id: str):
    """Unregister a service"""
    global mcp_manager, service_instances
    
    if not mcp_manager:
        raise HTTPException(status_code=503, detail="MCP Manager not initialized")
    
    try:
        # Stop service instance if it exists
        for name, instance in list(service_instances.items()):
            if instance.get_service_instance().id == service_id:
                await instance.stop()
                del service_instances[name]
                break
        
        # Unregister from MCP Manager
        success = mcp_manager.registry.unregister_service(service_id)
        
        if success:
            # Broadcast update to WebSocket clients
            await broadcast_to_websockets({
                "type": "service_unregistered",
                "service_id": service_id,
                "timestamp": datetime.now().isoformat()
            })
            
            return {"status": "success", "message": "Service unregistered successfully"}
        else:
            raise HTTPException(status_code=404, detail="Service not found")
    
    except Exception as e:
        logger.error(f"Error unregistering service: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Load balancing endpoint
@app.get("/mcp/load-balance/{service_type}")
async def get_load_balanced_service(service_type: str, algorithm: str = "round_robin"):
    """Get a load-balanced service instance"""
    global mcp_manager
    
    if not mcp_manager:
        raise HTTPException(status_code=503, detail="MCP Manager not initialized")
    
    try:
        service_type_enum = ServiceType(service_type)
        service = mcp_manager.get_service_for_request(service_type_enum, algorithm)
        
        if not service:
            raise HTTPException(status_code=404, detail=f"No healthy {service_type} services available")
        
        return {
            "id": service.id,
            "name": service.name,
            "url": service.url,
            "status": service.status.value,
            "algorithm": algorithm
        }
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid service type")
    except Exception as e:
        logger.error(f"Error getting load-balanced service: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Configuration endpoints
@app.get("/mcp/config")
async def get_configuration():
    """Get current MCP configuration"""
    # This would return actual configuration in a real implementation
    return {
        "health_check_interval": 30,
        "load_balancing": {
            "default_algorithm": "round_robin",
            "health_check_timeout": 10
        },
        "logging": {
            "level": "INFO",
            "file": "mcp-manager.log"
        }
    }

@app.put("/mcp/config")
async def update_configuration(config: MCPConfiguration):
    """Update MCP configuration"""
    global mcp_manager
    
    if not mcp_manager:
        raise HTTPException(status_code=503, detail="MCP Manager not initialized")
    
    try:
        # Update health check interval
        if hasattr(mcp_manager.health_monitor, 'check_interval'):
            mcp_manager.health_monitor.check_interval = config.health_check_interval
        
        # Broadcast configuration update
        await broadcast_to_websockets({
            "type": "config_updated",
            "config": config.dict(),
            "timestamp": datetime.now().isoformat()
        })
        
        return {"status": "success", "message": "Configuration updated"}
    
    except Exception as e:
        logger.error(f"Error updating configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Service discovery endpoints
@app.post("/mcp/discover")
async def discover_services():
    """Trigger service discovery"""
    global mcp_manager
    
    if not mcp_manager:
        raise HTTPException(status_code=503, detail="MCP Manager not initialized")
    
    try:
        await mcp_manager.service_discovery.discover_services()
        
        # Get updated service list
        services = mcp_manager.get_all_services()
        
        # Broadcast discovery update
        await broadcast_to_websockets({
            "type": "services_discovered",
            "count": len(services),
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "status": "success",
            "message": "Service discovery completed",
            "discovered_services": len(services)
        }
    
    except Exception as e:
        logger.error(f"Error during service discovery: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time updates
@app.websocket("/mcp/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time MCP updates"""
    await websocket.accept()
    websocket_connections.append(websocket)
    
    try:
        # Send initial status
        status = mcp_manager.get_service_status() if mcp_manager else {}
        await websocket.send_text(json.dumps({
            "type": "initial_status",
            "status": status,
            "timestamp": datetime.now().isoformat()
        }))
        
        # Keep connection alive
        while True:
            await websocket.receive_text()  # Wait for client messages
    
    except WebSocketDisconnect:
        pass
    finally:
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)

# Utility endpoints
@app.get("/mcp/metrics")
async def get_system_metrics():
    """Get system-level metrics"""
    global mcp_manager, service_instances
    
    if not mcp_manager:
        raise HTTPException(status_code=503, detail="MCP Manager not initialized")
    
    services = mcp_manager.get_all_services()
    
    total_requests = sum(s.metrics.requests_total for s in services)
    total_errors = sum(s.metrics.error_count for s in services)
    avg_response_time = sum(s.metrics.response_time_avg for s in services) / len(services) if services else 0
    
    return {
        "total_services": len(services),
        "running_services": len([s for s in services if s.status == ServiceStatus.RUNNING]),
        "healthy_services": len([s for s in services if s.is_healthy]),
        "total_requests": total_requests,
        "total_errors": total_errors,
        "error_rate": (total_errors / total_requests * 100) if total_requests > 0 else 0,
        "avg_response_time": avg_response_time,
        "service_instances": len(service_instances),
        "websocket_connections": len(websocket_connections),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/mcp/test-connection")
async def test_connection(host: str, port: int):
    """Test connection to a host and port"""
    import socket
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        is_connected = result == 0
        
        return {
            "host": host,
            "port": port,
            "connected": is_connected,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "host": host,
            "port": port,
            "connected": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Main entry point
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Manager Integration API")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--log-level", default="info", help="Log level")
    
    args = parser.parse_args()
    
    uvicorn.run(
        "mcp_integration:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level
    )