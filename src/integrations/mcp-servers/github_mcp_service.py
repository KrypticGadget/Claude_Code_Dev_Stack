#!/usr/bin/env python3
"""
GitHub MCP Service - Enhanced Implementation
Manages the GitHub MCP server lifecycle with advanced features

Features:
- Complete server lifecycle management
- Health monitoring and auto-recovery
- Configuration management
- Docker integration
- Metrics collection
- Service discovery integration
"""

import asyncio
import json
import logging
import os
import subprocess
import signal
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field

import httpx
import psutil
import yaml
from github import Github
from github.GithubException import GithubException

logger = logging.getLogger(__name__)

@dataclass
class ServiceConfig:
    """GitHub MCP Service configuration"""
    # Server configuration
    host: str = "localhost"
    port: int = 8081
    log_level: str = "info"
    
    # GitHub configuration
    github_token: Optional[str] = None
    github_app_id: Optional[str] = None
    github_app_private_key: Optional[str] = None
    github_webhook_secret: Optional[str] = None
    
    # Redis configuration (optional)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    
    # Rate limiting
    rate_limit_requests_per_hour: int = 5000
    rate_limit_search_per_minute: int = 30
    
    # Caching
    cache_ttl_default: int = 300
    cache_ttl_repository: int = 600
    cache_ttl_file_content: int = 1800
    
    # WebSocket configuration
    websocket_heartbeat_interval: int = 30
    websocket_max_connections: int = 100
    
    # Health monitoring
    health_check_interval: int = 30
    health_check_timeout: int = 10
    restart_on_failure: bool = True
    max_restart_attempts: int = 3
    restart_delay: int = 5
    
    # Docker configuration
    docker_enabled: bool = False
    docker_image: str = "github-mcp-server:latest"
    docker_network: str = "mcp-network"
    docker_volumes: List[str] = field(default_factory=list)
    docker_environment: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def from_file(cls, config_path: Path) -> 'ServiceConfig':
        """Load configuration from YAML file"""
        if config_path.exists():
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f) or {}
            
            # Extract GitHub MCP specific config
            github_config = config_data.get('github_mcp', {})
            
            # Merge with environment variables
            github_config.update({
                'github_token': os.getenv('GITHUB_TOKEN', github_config.get('github_token')),
                'github_app_id': os.getenv('GITHUB_APP_ID', github_config.get('github_app_id')),
                'github_app_private_key': os.getenv('GITHUB_APP_PRIVATE_KEY', github_config.get('github_app_private_key')),
                'github_webhook_secret': os.getenv('GITHUB_WEBHOOK_SECRET', github_config.get('github_webhook_secret')),
                'redis_host': os.getenv('REDIS_HOST', github_config.get('redis_host', 'localhost')),
                'redis_port': int(os.getenv('REDIS_PORT', github_config.get('redis_port', 6379))),
                'redis_password': os.getenv('REDIS_PASSWORD', github_config.get('redis_password')),
            })
            
            return cls(**github_config)
        
        # Default configuration with environment variables
        return cls(
            github_token=os.getenv('GITHUB_TOKEN'),
            github_app_id=os.getenv('GITHUB_APP_ID'),
            github_app_private_key=os.getenv('GITHUB_APP_PRIVATE_KEY'),
            github_webhook_secret=os.getenv('GITHUB_WEBHOOK_SECRET'),
            redis_host=os.getenv('REDIS_HOST', 'localhost'),
            redis_port=int(os.getenv('REDIS_PORT', 6379)),
            redis_password=os.getenv('REDIS_PASSWORD'),
        )
    
    def to_environment(self) -> Dict[str, str]:
        """Convert configuration to environment variables"""
        env = {
            'HOST': self.host,
            'PORT': str(self.port),
            'LOG_LEVEL': self.log_level,
            'REDIS_HOST': self.redis_host,
            'REDIS_PORT': str(self.redis_port),
        }
        
        if self.github_token:
            env['GITHUB_TOKEN'] = self.github_token
        if self.github_app_id:
            env['GITHUB_APP_ID'] = self.github_app_id
        if self.github_app_private_key:
            env['GITHUB_APP_PRIVATE_KEY'] = self.github_app_private_key
        if self.github_webhook_secret:
            env['GITHUB_WEBHOOK_SECRET'] = self.github_webhook_secret
        if self.redis_password:
            env['REDIS_PASSWORD'] = self.redis_password
        
        return env

class DockerManager:
    """Docker container management for GitHub MCP service"""
    
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.container_name = f"github-mcp-{config.port}"
        self.container_id: Optional[str] = None
    
    async def start_container(self) -> bool:
        """Start GitHub MCP service in Docker container"""
        try:
            # Build Docker command
            cmd = [
                "docker", "run", "-d",
                "--name", self.container_name,
                "--network", self.config.docker_network,
                "-p", f"{self.config.port}:{self.config.port}",
            ]
            
            # Add environment variables
            env_vars = self.config.to_environment()
            for key, value in env_vars.items():
                cmd.extend(["-e", f"{key}={value}"])
            
            # Add volumes
            for volume in self.config.docker_volumes:
                cmd.extend(["-v", volume])
            
            # Add additional environment variables
            for key, value in self.config.docker_environment.items():
                cmd.extend(["-e", f"{key}={value}"])
            
            # Add image
            cmd.append(self.config.docker_image)
            
            # Run container
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                self.container_id = stdout.decode().strip()
                logger.info(f"Docker container started: {self.container_id[:12]}")
                return True
            else:
                logger.error(f"Failed to start Docker container: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Docker start error: {e}")
            return False
    
    async def stop_container(self) -> bool:
        """Stop Docker container"""
        try:
            if self.container_id or self.container_name:
                identifier = self.container_id or self.container_name
                
                process = await asyncio.create_subprocess_exec(
                    "docker", "stop", identifier,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                await process.communicate()
                
                # Remove container
                process = await asyncio.create_subprocess_exec(
                    "docker", "rm", identifier,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                await process.communicate()
                
                logger.info(f"Docker container stopped and removed: {identifier}")
                self.container_id = None
                return True
                
        except Exception as e:
            logger.error(f"Docker stop error: {e}")
            return False
    
    async def get_container_logs(self, lines: int = 100) -> str:
        """Get container logs"""
        try:
            if self.container_id or self.container_name:
                identifier = self.container_id or self.container_name
                
                process = await asyncio.create_subprocess_exec(
                    "docker", "logs", "--tail", str(lines), identifier,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                return stdout.decode() + stderr.decode()
                
        except Exception as e:
            logger.error(f"Docker logs error: {e}")
            return ""
    
    async def is_container_running(self) -> bool:
        """Check if container is running"""
        try:
            if self.container_id or self.container_name:
                identifier = self.container_id or self.container_name
                
                process = await asyncio.create_subprocess_exec(
                    "docker", "inspect", "-f", "{{.State.Running}}", identifier,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    return stdout.decode().strip().lower() == "true"
                    
        except Exception as e:
            logger.debug(f"Container status check error: {e}")
            
        return False

class GitHubMCPService:
    """Enhanced GitHub MCP service management"""
    
    def __init__(self, config: ServiceConfig = None, config_file: Path = None):
        self.config = config or ServiceConfig.from_file(config_file or Path("github_mcp_config.yml"))
        self.docker_manager = DockerManager(self.config) if self.config.docker_enabled else None
        
        # Service state
        self.server_process: Optional[subprocess.Popen] = None
        self.running = False
        self.restart_attempts = 0
        self.last_restart_time: Optional[datetime] = None
        
        # Health monitoring
        self.health_check_task: Optional[asyncio.Task] = None
        self.last_health_check: Optional[datetime] = None
        self.health_status = "unknown"
        
        # Metrics
        self.metrics = {
            "start_time": None,
            "restart_count": 0,
            "health_checks": 0,
            "failed_health_checks": 0,
            "uptime": 0
        }
        
        # Server script path
        self.server_script = Path(__file__).parent / "github_mcp_server.py"
        if not self.server_script.exists():
            logger.warning(f"Server script not found: {self.server_script}")
    
    async def start(self) -> bool:
        """Start the GitHub MCP service"""
        if self.running:
            logger.warning("GitHub MCP service is already running")
            return True
        
        logger.info(f"Starting GitHub MCP service on {self.config.host}:{self.config.port}")
        
        try:
            if self.config.docker_enabled:
                success = await self._start_docker_service()
            else:
                success = await self._start_local_service()
            
            if success:
                self.running = True
                self.metrics["start_time"] = datetime.now()
                self.restart_attempts = 0
                
                # Start health monitoring
                if self.config.health_check_interval > 0:
                    self.health_check_task = asyncio.create_task(self._health_monitor_loop())
                
                logger.info("GitHub MCP service started successfully")
                return True
            else:
                logger.error("Failed to start GitHub MCP service")
                return False
                
        except Exception as e:
            logger.error(f"Error starting GitHub MCP service: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop the GitHub MCP service"""
        if not self.running:
            logger.warning("GitHub MCP service is not running")
            return True
        
        logger.info("Stopping GitHub MCP service")
        
        try:
            # Stop health monitoring
            if self.health_check_task:
                self.health_check_task.cancel()
                try:
                    await self.health_check_task
                except asyncio.CancelledError:
                    pass
                self.health_check_task = None
            
            # Stop service
            if self.config.docker_enabled:
                success = await self._stop_docker_service()
            else:
                success = await self._stop_local_service()
            
            if success:
                self.running = False
                logger.info("GitHub MCP service stopped successfully")
                return True
            else:
                logger.error("Failed to stop GitHub MCP service gracefully")
                return False
                
        except Exception as e:
            logger.error(f"Error stopping GitHub MCP service: {e}")
            return False
    
    async def restart(self) -> bool:
        """Restart the GitHub MCP service"""
        logger.info("Restarting GitHub MCP service")
        
        self.restart_attempts += 1
        self.metrics["restart_count"] += 1
        self.last_restart_time = datetime.now()
        
        # Stop service
        await self.stop()
        
        # Wait a bit before restarting
        await asyncio.sleep(self.config.restart_delay)
        
        # Start service
        return await self.start()
    
    async def _start_local_service(self) -> bool:
        """Start service as local process"""
        if not self.server_script.exists():
            logger.error(f"Server script not found: {self.server_script}")
            return False
        
        try:
            # Prepare environment
            env = os.environ.copy()
            env.update(self.config.to_environment())
            
            # Start server process
            self.server_process = subprocess.Popen([
                sys.executable, str(self.server_script), str(self.config.port)
            ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            await asyncio.sleep(3)
            
            # Check if process is running
            if self.server_process.poll() is None:
                # Verify server is responding
                return await self._check_server_health()
            else:
                logger.error("Server process exited immediately")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start local service: {e}")
            return False
    
    async def _stop_local_service(self) -> bool:
        """Stop local service process"""
        if not self.server_process:
            return True
        
        try:
            # Send SIGTERM
            self.server_process.terminate()
            
            # Wait for graceful shutdown
            try:
                self.server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                # Force kill if not responding
                logger.warning("Service not responding to SIGTERM, sending SIGKILL")
                self.server_process.kill()
                self.server_process.wait()
            
            self.server_process = None
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop local service: {e}")
            return False
    
    async def _start_docker_service(self) -> bool:
        """Start service in Docker container"""
        if not self.docker_manager:
            return False
        
        success = await self.docker_manager.start_container()
        if success:
            # Wait for container to start
            await asyncio.sleep(5)
            return await self._check_server_health()
        
        return False
    
    async def _stop_docker_service(self) -> bool:
        """Stop Docker container service"""
        if not self.docker_manager:
            return True
        
        return await self.docker_manager.stop_container()
    
    async def _check_server_health(self) -> bool:
        """Check if server is responding to health checks"""
        try:
            async with httpx.AsyncClient(timeout=self.config.health_check_timeout) as client:
                response = await client.get(f"http://{self.config.host}:{self.config.port}/health")
                
                if response.status_code == 200:
                    self.health_status = "healthy"
                    self.last_health_check = datetime.now()
                    return True
                else:
                    self.health_status = f"unhealthy (status: {response.status_code})"
                    return False
                    
        except Exception as e:
            self.health_status = f"unreachable ({e})"
            return False
    
    async def _health_monitor_loop(self):
        """Background health monitoring loop"""
        logger.info("Health monitoring started")
        
        while self.running:
            try:
                self.metrics["health_checks"] += 1
                
                # Check server health
                is_healthy = await self._check_server_health()
                
                if not is_healthy:
                    self.metrics["failed_health_checks"] += 1
                    logger.warning(f"Health check failed: {self.health_status}")
                    
                    # Auto-restart if enabled and within limits
                    if (self.config.restart_on_failure and 
                        self.restart_attempts < self.config.max_restart_attempts):
                        
                        logger.info("Attempting automatic restart due to health check failure")
                        restart_task = asyncio.create_task(self.restart())
                        await restart_task
                
                # Update uptime
                if self.metrics["start_time"]:
                    self.metrics["uptime"] = (datetime.now() - self.metrics["start_time"]).total_seconds()
                
                await asyncio.sleep(self.config.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(self.config.health_check_interval)
        
        logger.info("Health monitoring stopped")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current service status"""
        status = {
            "running": self.running,
            "health_status": self.health_status,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "restart_attempts": self.restart_attempts,
            "last_restart_time": self.last_restart_time.isoformat() if self.last_restart_time else None,
            "config": {
                "host": self.config.host,
                "port": self.config.port,
                "docker_enabled": self.config.docker_enabled,
                "health_check_interval": self.config.health_check_interval,
                "restart_on_failure": self.config.restart_on_failure
            },
            "metrics": self.metrics.copy()
        }
        
        # Add process info for local service
        if self.server_process and not self.config.docker_enabled:
            try:
                process = psutil.Process(self.server_process.pid)
                status["process"] = {
                    "pid": self.server_process.pid,
                    "cpu_percent": process.cpu_percent(),
                    "memory_info": process.memory_info()._asdict(),
                    "create_time": process.create_time()
                }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                status["process"] = {"status": "not_found"}
        
        # Add Docker info if using containers
        if self.config.docker_enabled and self.docker_manager:
            status["docker"] = {
                "container_name": self.docker_manager.container_name,
                "container_id": self.docker_manager.container_id,
                "is_running": await self.docker_manager.is_container_running()
            }
        
        return status
    
    async def get_logs(self, lines: int = 100) -> str:
        """Get service logs"""
        if self.config.docker_enabled and self.docker_manager:
            return await self.docker_manager.get_container_logs(lines)
        elif self.server_process:
            # For local process, we'd need to implement log file reading
            # This is a simplified version
            return "Local process logs not implemented yet"
        else:
            return "Service not running"
    
    async def validate_configuration(self) -> Dict[str, Any]:
        """Validate service configuration"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check GitHub authentication
        if not self.config.github_token and not (self.config.github_app_id and self.config.github_app_private_key):
            validation_result["errors"].append("No GitHub authentication configured (token or app credentials required)")
            validation_result["valid"] = False
        
        # Test GitHub connection if token is provided
        if self.config.github_token:
            try:
                github = Github(self.config.github_token)
                user = github.get_user()
                validation_result["github_user"] = {
                    "login": user.login,
                    "name": user.name,
                    "rate_limit": github.get_rate_limit().core.remaining
                }
            except Exception as e:
                validation_result["errors"].append(f"GitHub token validation failed: {e}")
                validation_result["valid"] = False
        
        # Check port availability
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((self.config.host, self.config.port))
            sock.close()
            if result == 0:
                validation_result["warnings"].append(f"Port {self.config.port} appears to be in use")
        except Exception:
            pass
        
        # Check Docker if enabled
        if self.config.docker_enabled:
            try:
                process = await asyncio.create_subprocess_exec(
                    "docker", "--version",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                if process.returncode != 0:
                    validation_result["errors"].append("Docker not available")
                    validation_result["valid"] = False
                else:
                    validation_result["docker_version"] = stdout.decode().strip()
            except Exception as e:
                validation_result["errors"].append(f"Docker check failed: {e}")
                validation_result["valid"] = False
        
        # Check Redis connection if configured
        if self.config.redis_host and self.config.redis_host != "localhost":
            try:
                import redis
                redis_client = redis.Redis(
                    host=self.config.redis_host,
                    port=self.config.redis_port,
                    password=self.config.redis_password,
                    socket_timeout=5
                )
                redis_client.ping()
                validation_result["redis_connected"] = True
            except Exception as e:
                validation_result["warnings"].append(f"Redis connection failed: {e}")
        
        return validation_result

# Service factory function
def create_github_mcp_service(config_file: Path = None) -> GitHubMCPService:
    """Create GitHub MCP service instance"""
    return GitHubMCPService(config_file=config_file)

# CLI interface
async def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GitHub MCP Service Manager")
    parser.add_argument("action", choices=["start", "stop", "restart", "status", "validate", "logs"])
    parser.add_argument("--config", type=Path, help="Configuration file path")
    parser.add_argument("--port", type=int, default=8081, help="Service port")
    parser.add_argument("--host", default="localhost", help="Service host")
    parser.add_argument("--docker", action="store_true", help="Use Docker")
    parser.add_argument("--lines", type=int, default=100, help="Number of log lines to show")
    
    args = parser.parse_args()
    
    # Create service configuration
    if args.config and args.config.exists():
        config = ServiceConfig.from_file(args.config)
    else:
        config = ServiceConfig(
            host=args.host,
            port=args.port,
            docker_enabled=args.docker
        )
    
    # Create service
    service = GitHubMCPService(config)
    
    # Execute action
    if args.action == "start":
        success = await service.start()
        print(f"Service start: {'SUCCESS' if success else 'FAILED'}")
    
    elif args.action == "stop":
        success = await service.stop()
        print(f"Service stop: {'SUCCESS' if success else 'FAILED'}")
    
    elif args.action == "restart":
        success = await service.restart()
        print(f"Service restart: {'SUCCESS' if success else 'FAILED'}")
    
    elif args.action == "status":
        status = await service.get_status()
        print(json.dumps(status, indent=2, default=str))
    
    elif args.action == "validate":
        validation = await service.validate_configuration()
        print(json.dumps(validation, indent=2, default=str))
        
        if not validation["valid"]:
            sys.exit(1)
    
    elif args.action == "logs":
        logs = await service.get_logs(args.lines)
        print(logs)

if __name__ == "__main__":
    asyncio.run(main())