#!/usr/bin/env python3
"""
Orchestration Package - PHASE 7.3
Unified MCP service orchestration with load balancing, health monitoring, and failover mechanisms.

This package provides:
- MCP Service Orchestrator: Core service management and routing
- Orchestrator Integration: Bridge between v3 and MCP orchestrators
- Orchestration Gateway: RESTful API for external access
- Comprehensive middleware architecture for distributed systems

Usage:
    from core.orchestration import start_orchestration_system, get_orchestration_status
    
    # Start the complete orchestration system
    await start_orchestration_system()
    
    # Get system status
    status = await get_orchestration_status()
    
    # Stop the system
    await stop_orchestration_system()
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, Optional
import sys

# Setup path for imports
sys.path.append(str(Path(__file__).parent))

# Import core components
try:
    from .mcp_service_orchestrator import (
        MCPServiceOrchestrator,
        get_mcp_orchestrator,
        ServiceType,
        OrchestrationStrategy,
        FailoverPolicy,
        ServicePool,
        CircuitBreaker,
        LoadBalancerEngine,
        FailoverManager,
        ServiceHealthMonitor,
        MessageQueue
    )
    
    from .orchestrator_integration import (
        OrchestrationCoordinator,
        get_orchestration_coordinator,
        start_integrated_orchestration,
        stop_integrated_orchestration,
        integrate_orchestrators
    )
    
    from .orchestration_gateway import app as gateway_app
    
except ImportError as e:
    logging.warning(f"Import error in orchestration package: {e}")
    # Create fallback None objects
    MCPServiceOrchestrator = None
    OrchestrationCoordinator = None
    gateway_app = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Package version
__version__ = "1.0.0"

# Global orchestration state
_orchestration_state = {
    "initialized": False,
    "running": False,
    "mcp_orchestrator": None,
    "coordinator": None,
    "gateway_process": None,
    "error": None
}

# Configuration defaults
DEFAULT_CONFIG = {
    "mcp_orchestrator": {
        "config_file": "mcp-orchestrator.yml",
        "health_check_interval": 15,
        "enable_predictive_monitoring": True,
        "enable_circuit_breakers": True
    },
    "integration": {
        "enable_v3_integration": True,
        "sync_status": True,
        "forward_events": True
    },
    "gateway": {
        "host": "0.0.0.0",
        "port": 8000,
        "enable_websockets": True,
        "enable_dashboard": True,
        "enable_auth": False
    },
    "logging": {
        "level": "INFO",
        "enable_file_logging": True,
        "log_file": "orchestration.log"
    }
}


async def initialize_orchestration_system(config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Initialize the complete orchestration system
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        bool: True if initialization successful, False otherwise
    """
    global _orchestration_state
    
    if _orchestration_state["initialized"]:
        logger.warning("Orchestration system already initialized")
        return True
    
    logger.info("Initializing PHASE 7.3 Orchestration System...")
    
    try:
        # Merge configuration
        effective_config = DEFAULT_CONFIG.copy()
        if config:
            effective_config.update(config)
        
        # Configure logging
        log_config = effective_config.get("logging", {})
        if log_config.get("enable_file_logging"):
            log_file = log_config.get("log_file", "orchestration.log")
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            logging.getLogger().addHandler(file_handler)
        
        log_level = getattr(logging, log_config.get("level", "INFO").upper())
        logging.getLogger().setLevel(log_level)
        
        # Initialize MCP Service Orchestrator
        if MCPServiceOrchestrator:
            config_file = effective_config.get("mcp_orchestrator", {}).get("config_file")
            if config_file:
                config_path = Path(config_file)
                if not config_path.is_absolute():
                    config_path = Path(__file__).parent / config_path
            else:
                config_path = None
            
            mcp_orchestrator = MCPServiceOrchestrator(config_path)
            await mcp_orchestrator.initialize()
            _orchestration_state["mcp_orchestrator"] = mcp_orchestrator
            logger.info("MCP Service Orchestrator initialized")
        else:
            logger.warning("MCP Service Orchestrator not available")
        
        # Initialize Integration Coordinator
        if OrchestrationCoordinator and effective_config.get("integration", {}).get("enable_v3_integration"):
            coordinator = get_orchestration_coordinator()
            await coordinator.initialize()
            _orchestration_state["coordinator"] = coordinator
            logger.info("Orchestration Coordinator initialized")
        else:
            logger.warning("Orchestration Coordinator not available or disabled")
        
        _orchestration_state["initialized"] = True
        _orchestration_state["error"] = None
        
        logger.info("PHASE 7.3 Orchestration System initialized successfully")
        return True
        
    except Exception as e:
        error_msg = f"Failed to initialize orchestration system: {e}"
        logger.error(error_msg)
        _orchestration_state["error"] = error_msg
        return False


async def start_orchestration_system(config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Start the complete orchestration system
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        bool: True if start successful, False otherwise
    """
    global _orchestration_state
    
    if _orchestration_state["running"]:
        logger.warning("Orchestration system already running")
        return True
    
    # Initialize if not already done
    if not _orchestration_state["initialized"]:
        success = await initialize_orchestration_system(config)
        if not success:
            return False
    
    logger.info("Starting PHASE 7.3 Orchestration System...")
    
    try:
        # Start MCP Service Orchestrator
        mcp_orchestrator = _orchestration_state["mcp_orchestrator"]
        if mcp_orchestrator:
            await mcp_orchestrator.start()
            logger.info("MCP Service Orchestrator started")
        
        # Start Integration Coordinator
        coordinator = _orchestration_state["coordinator"]
        if coordinator:
            await coordinator.start()
            logger.info("Orchestration Coordinator started")
        
        _orchestration_state["running"] = True
        _orchestration_state["error"] = None
        
        logger.info("PHASE 7.3 Orchestration System started successfully")
        return True
        
    except Exception as e:
        error_msg = f"Failed to start orchestration system: {e}"
        logger.error(error_msg)
        _orchestration_state["error"] = error_msg
        return False


async def stop_orchestration_system() -> bool:
    """
    Stop the complete orchestration system
    
    Returns:
        bool: True if stop successful, False otherwise
    """
    global _orchestration_state
    
    if not _orchestration_state["running"]:
        logger.warning("Orchestration system not running")
        return True
    
    logger.info("Stopping PHASE 7.3 Orchestration System...")
    
    try:
        # Stop Integration Coordinator
        coordinator = _orchestration_state["coordinator"]
        if coordinator:
            await coordinator.stop()
            logger.info("Orchestration Coordinator stopped")
        
        # Stop MCP Service Orchestrator
        mcp_orchestrator = _orchestration_state["mcp_orchestrator"]
        if mcp_orchestrator:
            await mcp_orchestrator.stop()
            logger.info("MCP Service Orchestrator stopped")
        
        _orchestration_state["running"] = False
        _orchestration_state["error"] = None
        
        logger.info("PHASE 7.3 Orchestration System stopped successfully")
        return True
        
    except Exception as e:
        error_msg = f"Failed to stop orchestration system: {e}"
        logger.error(error_msg)
        _orchestration_state["error"] = error_msg
        return False


async def restart_orchestration_system(config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Restart the complete orchestration system
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        bool: True if restart successful, False otherwise
    """
    logger.info("Restarting PHASE 7.3 Orchestration System...")
    
    # Stop current system
    await stop_orchestration_system()
    
    # Reset state
    _orchestration_state["initialized"] = False
    
    # Start again
    return await start_orchestration_system(config)


async def get_orchestration_status() -> Dict[str, Any]:
    """
    Get comprehensive orchestration system status
    
    Returns:
        Dict containing system status information
    """
    status = {
        "system": {
            "initialized": _orchestration_state["initialized"],
            "running": _orchestration_state["running"],
            "error": _orchestration_state["error"],
            "version": __version__
        },
        "components": {},
        "services": {},
        "metrics": {}
    }
    
    try:
        # Get MCP Orchestrator status
        mcp_orchestrator = _orchestration_state["mcp_orchestrator"]
        if mcp_orchestrator:
            mcp_status = mcp_orchestrator.get_service_status()
            status["components"]["mcp_orchestrator"] = {
                "running": getattr(mcp_orchestrator, 'running', False),
                "services": mcp_status
            }
            status["services"].update(mcp_status.get("service_pools", {}))
        else:
            status["components"]["mcp_orchestrator"] = {"available": False}
        
        # Get Coordinator status
        coordinator = _orchestration_state["coordinator"]
        if coordinator:
            coord_status = coordinator.get_integration_status()
            status["components"]["coordinator"] = coord_status
            status["metrics"].update(coord_status.get("metrics", {}))
        else:
            status["components"]["coordinator"] = {"available": False}
        
    except Exception as e:
        logger.error(f"Error getting orchestration status: {e}")
        status["system"]["error"] = str(e)
    
    return status


def start_gateway_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    log_level: str = "info"
) -> None:
    """
    Start the orchestration gateway server
    
    Args:
        host: Host to bind to
        port: Port to bind to
        reload: Enable auto-reload
        log_level: Log level
    """
    if not gateway_app:
        logger.error("Gateway app not available")
        return
    
    import uvicorn
    
    logger.info(f"Starting Orchestration Gateway on {host}:{port}")
    
    uvicorn.run(
        "core.orchestration.orchestration_gateway:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level
    )


async def route_service_request(
    service_type: str,
    context: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    Route a service request through the orchestration system
    
    Args:
        service_type: Type of service to request
        context: Optional request context
        
    Returns:
        Service information if available, None otherwise
    """
    coordinator = _orchestration_state["coordinator"]
    if not coordinator:
        logger.error("Orchestration coordinator not available")
        return None
    
    try:
        return await coordinator.route_service_request(service_type, context or {})
    except Exception as e:
        logger.error(f"Service routing error: {e}")
        return None


def get_service_types() -> list:
    """
    Get available service types
    
    Returns:
        List of available service types
    """
    if ServiceType and hasattr(ServiceType, '__members__'):
        return list(ServiceType.__members__.keys())
    else:
        return ["PLAYWRIGHT", "GITHUB", "WEBSEARCH", "CUSTOM", "CORE", "PROXY", "GATEWAY"]


def get_orchestration_strategies() -> list:
    """
    Get available orchestration strategies
    
    Returns:
        List of available strategies
    """
    if OrchestrationStrategy and hasattr(OrchestrationStrategy, '__members__'):
        return list(OrchestrationStrategy.__members__.keys())
    else:
        return ["ROUND_ROBIN", "LEAST_CONNECTIONS", "FASTEST_RESPONSE", "WEIGHTED_ROUND_ROBIN", "CONSISTENT_HASH", "RESOURCE_AWARE"]


def get_failover_policies() -> list:
    """
    Get available failover policies
    
    Returns:
        List of available failover policies
    """
    if FailoverPolicy and hasattr(FailoverPolicy, '__members__'):
        return list(FailoverPolicy.__members__.keys())
    else:
        return ["IMMEDIATE", "GRACEFUL", "CIRCUIT_BREAKER", "RETRY_WITH_BACKOFF"]


# Convenience functions for common operations
async def quick_start(
    enable_gateway: bool = True,
    gateway_port: int = 8000,
    config: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Quick start function for the entire orchestration system
    
    Args:
        enable_gateway: Whether to start the gateway server
        gateway_port: Port for the gateway server
        config: Optional configuration
        
    Returns:
        bool: True if successful
    """
    # Start orchestration system
    success = await start_orchestration_system(config)
    if not success:
        return False
    
    # Start gateway if requested
    if enable_gateway and gateway_app:
        import threading
        import uvicorn
        
        def run_gateway():
            uvicorn.run(
                "core.orchestration.orchestration_gateway:app",
                host="0.0.0.0",
                port=gateway_port,
                log_level="info"
            )
        
        gateway_thread = threading.Thread(target=run_gateway, daemon=True)
        gateway_thread.start()
        logger.info(f"Gateway started on port {gateway_port}")
    
    return True


# Export all public interfaces
__all__ = [
    # Core classes
    "MCPServiceOrchestrator",
    "OrchestrationCoordinator",
    "ServiceType",
    "OrchestrationStrategy", 
    "FailoverPolicy",
    "ServicePool",
    "CircuitBreaker",
    "LoadBalancerEngine",
    "FailoverManager",
    "ServiceHealthMonitor",
    "MessageQueue",
    
    # Main functions
    "initialize_orchestration_system",
    "start_orchestration_system",
    "stop_orchestration_system",
    "restart_orchestration_system",
    "get_orchestration_status",
    "route_service_request",
    
    # Gateway functions
    "start_gateway_server",
    "gateway_app",
    
    # Utility functions
    "get_service_types",
    "get_orchestration_strategies", 
    "get_failover_policies",
    "quick_start",
    
    # Factory functions
    "get_mcp_orchestrator",
    "get_orchestration_coordinator",
    
    # Legacy compatibility
    "start_integrated_orchestration",
    "stop_integrated_orchestration",
    "integrate_orchestrators",
    
    # Constants
    "__version__",
    "DEFAULT_CONFIG"
]


# Module-level convenience for direct import
if __name__ == "__main__":
    import argparse
    
    async def main():
        parser = argparse.ArgumentParser(description="PHASE 7.3 Orchestration System")
        parser.add_argument("--action", choices=["start", "stop", "restart", "status"], default="start")
        parser.add_argument("--gateway", action="store_true", help="Start gateway server")
        parser.add_argument("--port", type=int, default=8000, help="Gateway port")
        parser.add_argument("--config", help="Configuration file path")
        
        args = parser.parse_args()
        
        # Load config if provided
        config = None
        if args.config:
            import yaml
            with open(args.config, 'r') as f:
                config = yaml.safe_load(f)
        
        if args.action == "start":
            success = await start_orchestration_system(config)
            if success:
                print("Orchestration system started successfully")
                if args.gateway:
                    print(f"Starting gateway on port {args.port}")
                    start_gateway_server(port=args.port)
            else:
                print("Failed to start orchestration system")
        
        elif args.action == "stop":
            success = await stop_orchestration_system()
            if success:
                print("Orchestration system stopped successfully")
            else:
                print("Failed to stop orchestration system")
        
        elif args.action == "restart":
            success = await restart_orchestration_system(config)
            if success:
                print("Orchestration system restarted successfully")
            else:
                print("Failed to restart orchestration system")
        
        elif args.action == "status":
            status = await get_orchestration_status()
            import json
            print(json.dumps(status, indent=2))
    
    asyncio.run(main())