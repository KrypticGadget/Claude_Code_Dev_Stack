#!/usr/bin/env python3
"""
GitHub MCP Startup Script
Comprehensive startup script for GitHub MCP server with all features

Features:
- Environment validation
- Configuration loading
- Service management
- Health monitoring
- Graceful shutdown
- Auto-recovery
"""

import asyncio
import json
import logging
import os
import signal
import sys
from pathlib import Path
from typing import Optional

from github_mcp_integration import GitHubMCPIntegration, create_github_mcp_integration
from github_mcp_service import ServiceConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/github_mcp_startup.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

class GitHubMCPStartup:
    """GitHub MCP startup and lifecycle management"""
    
    def __init__(self, config_file: Path = None):
        self.config_file = config_file or Path("github_mcp_config.yml")
        self.integration: Optional[GitHubMCPIntegration] = None
        self.running = False
        self.shutdown_requested = False
        
        # Ensure logs directory exists
        Path("logs").mkdir(exist_ok=True)
    
    def validate_environment(self) -> bool:
        """Validate environment and dependencies"""
        logger.info("Validating environment...")
        
        errors = []
        warnings = []
        
        # Check Python version
        if sys.version_info < (3, 8):
            errors.append(f"Python 3.8+ required, found {sys.version}")
        
        # Check required environment variables
        github_token = os.getenv("GITHUB_TOKEN")
        github_app_id = os.getenv("GITHUB_APP_ID")
        github_app_private_key = os.getenv("GITHUB_APP_PRIVATE_KEY")
        
        if not github_token and not (github_app_id and github_app_private_key):
            errors.append("GitHub authentication not configured. Set GITHUB_TOKEN or GITHUB_APP_ID/GITHUB_APP_PRIVATE_KEY")
        
        # Check configuration file
        if not self.config_file.exists():
            warnings.append(f"Configuration file not found: {self.config_file}")
            logger.info("Will use default configuration with environment variables")
        
        # Check optional dependencies
        try:
            import redis
            redis_host = os.getenv("REDIS_HOST", "localhost")
            redis_port = int(os.getenv("REDIS_PORT", 6379))
            
            # Test Redis connection
            try:
                r = redis.Redis(host=redis_host, port=redis_port, socket_timeout=5)
                r.ping()
                logger.info(f"Redis connection successful: {redis_host}:{redis_port}")
            except Exception as e:
                warnings.append(f"Redis connection failed: {e}")
                logger.warning("Redis not available, will use in-memory cache")
        except ImportError:
            warnings.append("Redis not installed, will use in-memory cache")
        
        # Check Docker availability if needed
        docker_enabled = os.getenv("DOCKER_ENABLED", "false").lower() == "true"
        if docker_enabled:
            try:
                import subprocess
                result = subprocess.run(
                    ["docker", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    logger.info(f"Docker available: {result.stdout.strip()}")
                else:
                    errors.append("Docker not available but DOCKER_ENABLED=true")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                errors.append("Docker not available but DOCKER_ENABLED=true")
        
        # Report validation results
        if warnings:
            for warning in warnings:
                logger.warning(f"VALIDATION WARNING: {warning}")
        
        if errors:
            for error in errors:
                logger.error(f"VALIDATION ERROR: {error}")
            return False
        
        logger.info("Environment validation completed successfully")
        return True
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self.shutdown_requested = True
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        if hasattr(signal, 'SIGHUP'):
            signal.signal(signal.SIGHUP, signal_handler)
    
    async def start_integration(self) -> bool:
        """Start the GitHub MCP integration"""
        try:
            logger.info("Starting GitHub MCP integration...")
            
            # Create integration instance
            mcp_manager_url = os.getenv("MCP_MANAGER_URL", "http://localhost:8000")
            self.integration = create_github_mcp_integration(
                config_file=self.config_file,
                mcp_manager_url=mcp_manager_url
            )
            
            # Start integration
            success = await self.integration.start()
            
            if success:
                self.running = True
                logger.info("GitHub MCP integration started successfully")
                
                # Log initial status
                status = await self.integration.get_status()
                logger.info(f"Integration status: {json.dumps(status, indent=2, default=str)}")
                
                return True
            else:
                logger.error("Failed to start GitHub MCP integration")
                return False
                
        except Exception as e:
            logger.error(f"Error starting integration: {e}")
            return False
    
    async def monitor_health(self):
        """Monitor integration health"""
        logger.info("Starting health monitoring...")
        
        check_interval = 60  # seconds
        failure_count = 0
        max_failures = 3
        
        while self.running and not self.shutdown_requested:
            try:
                await asyncio.sleep(check_interval)
                
                if not self.integration:
                    continue
                
                # Check integration status
                status = await self.integration.get_status()
                
                if status["integration"]["running"]:
                    failure_count = 0
                    logger.debug("Health check passed")
                else:
                    failure_count += 1
                    logger.warning(f"Health check failed ({failure_count}/{max_failures})")
                    
                    if failure_count >= max_failures:
                        logger.error("Multiple health check failures, attempting restart...")
                        await self.restart_integration()
                        failure_count = 0
                
                # Log periodic status
                if hasattr(self, '_last_status_log'):
                    if (asyncio.get_event_loop().time() - self._last_status_log) > 300:  # 5 minutes
                        logger.info(f"Periodic status: {json.dumps(status, default=str)}")
                        self._last_status_log = asyncio.get_event_loop().time()
                else:
                    self._last_status_log = asyncio.get_event_loop().time()
                
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(30)
        
        logger.info("Health monitoring stopped")
    
    async def restart_integration(self) -> bool:
        """Restart the integration"""
        try:
            logger.info("Restarting GitHub MCP integration...")
            
            if self.integration:
                await self.integration.stop()
                await asyncio.sleep(5)
            
            return await self.start_integration()
            
        except Exception as e:
            logger.error(f"Error restarting integration: {e}")
            return False
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Initiating graceful shutdown...")
        
        self.running = False
        
        if self.integration:
            try:
                await self.integration.stop()
                logger.info("Integration stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping integration: {e}")
        
        logger.info("Shutdown completed")
    
    async def run(self) -> int:
        """Main run loop"""
        try:
            # Validate environment
            if not self.validate_environment():
                logger.error("Environment validation failed")
                return 1
            
            # Setup signal handlers
            self.setup_signal_handlers()
            
            # Start integration
            if not await self.start_integration():
                logger.error("Failed to start integration")
                return 1
            
            # Start health monitoring
            health_monitor_task = asyncio.create_task(self.monitor_health())
            
            # Main loop
            logger.info("GitHub MCP integration is running...")
            try:
                while self.running and not self.shutdown_requested:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
            
            # Cancel health monitoring
            health_monitor_task.cancel()
            try:
                await health_monitor_task
            except asyncio.CancelledError:
                pass
            
            # Shutdown
            await self.shutdown()
            
            return 0
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return 1

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GitHub MCP Startup Script")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("github_mcp_config.yml"),
        help="Configuration file path"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate environment and exit"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger("github_mcp_server").setLevel(logging.DEBUG)
        logging.getLogger("github_mcp_service").setLevel(logging.DEBUG)
        logging.getLogger("github_mcp_integration").setLevel(logging.DEBUG)
    
    # Create startup manager
    startup = GitHubMCPStartup(args.config)
    
    # Validation only mode
    if args.validate_only:
        if startup.validate_environment():
            print("✅ Environment validation passed")
            return 0
        else:
            print("❌ Environment validation failed")
            return 1
    
    # Normal startup
    try:
        return asyncio.run(startup.run())
    except KeyboardInterrupt:
        logger.info("Startup interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())