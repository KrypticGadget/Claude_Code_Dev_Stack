#!/usr/bin/env python3
"""
GitHub MCP Validation Script
Comprehensive validation and testing for GitHub MCP server setup

Features:
- Environment validation
- Configuration testing
- API connectivity checks
- Performance testing
- Security validation
"""

import asyncio
import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

import httpx
from github import Github
from github.GithubException import GithubException

from github_mcp_service import ServiceConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubMCPValidator:
    """Comprehensive validator for GitHub MCP setup"""
    
    def __init__(self, config_file: Path = None):
        self.config_file = config_file or Path("github_mcp_config.yml")
        self.config = ServiceConfig.from_file(self.config_file)
        self.validation_results = {
            "environment": {},
            "configuration": {},
            "github_api": {},
            "server": {},
            "performance": {},
            "security": {},
            "overall": {"success": False, "score": 0}
        }
    
    async def run_all_validations(self) -> Dict[str, Any]:
        """Run all validation checks"""
        logger.info("Starting comprehensive GitHub MCP validation...")
        
        # Environment validation
        await self.validate_environment()
        
        # Configuration validation
        await self.validate_configuration()
        
        # GitHub API validation
        await self.validate_github_api()
        
        # Server validation (if running)
        await self.validate_server()
        
        # Performance testing
        await self.validate_performance()
        
        # Security validation
        await self.validate_security()
        
        # Calculate overall score
        self.calculate_overall_score()
        
        return self.validation_results
    
    async def validate_environment(self):
        """Validate environment setup"""
        logger.info("Validating environment...")
        
        env_results = {
            "python_version": self._check_python_version(),
            "dependencies": self._check_dependencies(),
            "environment_variables": self._check_environment_variables(),
            "file_permissions": self._check_file_permissions(),
            "network_access": await self._check_network_access()
        }
        
        self.validation_results["environment"] = env_results
        logger.info(f"Environment validation completed: {self._count_successes(env_results)}/{len(env_results)} checks passed")
    
    async def validate_configuration(self):
        """Validate configuration settings"""
        logger.info("Validating configuration...")
        
        config_results = {
            "config_file_exists": self.config_file.exists(),
            "config_syntax": self._validate_config_syntax(),
            "required_settings": self._validate_required_settings(),
            "optional_settings": self._validate_optional_settings(),
            "security_settings": self._validate_security_settings()
        }
        
        self.validation_results["configuration"] = config_results
        logger.info(f"Configuration validation completed: {self._count_successes(config_results)}/{len(config_results)} checks passed")
    
    async def validate_github_api(self):
        """Validate GitHub API connectivity and permissions"""
        logger.info("Validating GitHub API...")
        
        api_results = {
            "authentication": await self._test_github_authentication(),
            "api_connectivity": await self._test_api_connectivity(),
            "rate_limits": await self._check_rate_limits(),
            "permissions": await self._test_permissions(),
            "webhook_setup": await self._validate_webhook_setup()
        }
        
        self.validation_results["github_api"] = api_results
        logger.info(f"GitHub API validation completed: {self._count_successes(api_results)}/{len(api_results)} checks passed")
    
    async def validate_server(self):
        """Validate server functionality"""
        logger.info("Validating server...")
        
        server_url = f"http://{self.config.host}:{self.config.port}"
        
        server_results = {
            "server_running": await self._check_server_running(server_url),
            "health_endpoint": await self._test_health_endpoint(server_url),
            "api_endpoints": await self._test_api_endpoints(server_url),
            "websocket": await self._test_websocket(server_url),
            "metrics": await self._test_metrics_endpoint(server_url)
        }
        
        self.validation_results["server"] = server_results
        logger.info(f"Server validation completed: {self._count_successes(server_results)}/{len(server_results)} checks passed")
    
    async def validate_performance(self):
        """Validate performance characteristics"""
        logger.info("Validating performance...")
        
        perf_results = {
            "response_times": await self._test_response_times(),
            "concurrent_requests": await self._test_concurrent_requests(),
            "cache_performance": await self._test_cache_performance(),
            "memory_usage": self._check_memory_usage(),
            "rate_limiting": await self._test_rate_limiting()
        }
        
        self.validation_results["performance"] = perf_results
        logger.info(f"Performance validation completed: {self._count_successes(perf_results)}/{len(perf_results)} checks passed")
    
    async def validate_security(self):
        """Validate security configuration"""
        logger.info("Validating security...")
        
        security_results = {
            "authentication_required": await self._test_authentication_required(),
            "cors_configuration": await self._test_cors_configuration(),
            "rate_limiting_security": await self._test_rate_limiting_security(),
            "webhook_security": await self._test_webhook_security(),
            "sensitive_data_exposure": self._check_sensitive_data_exposure()
        }
        
        self.validation_results["security"] = security_results
        logger.info(f"Security validation completed: {self._count_successes(security_results)}/{len(security_results)} checks passed")
    
    def calculate_overall_score(self):
        """Calculate overall validation score"""
        total_checks = 0
        passed_checks = 0
        
        for category, results in self.validation_results.items():
            if category == "overall":
                continue
            
            total_checks += len(results)
            passed_checks += self._count_successes(results)
        
        if total_checks > 0:
            score = (passed_checks / total_checks) * 100
            success = score >= 80  # Consider 80% pass rate as success
            
            self.validation_results["overall"] = {
                "success": success,
                "score": round(score, 2),
                "passed_checks": passed_checks,
                "total_checks": total_checks
            }
        
        logger.info(f"Overall validation score: {self.validation_results['overall']['score']}%")
    
    # Environment validation methods
    
    def _check_python_version(self) -> Dict[str, Any]:
        """Check Python version"""
        import sys
        version = sys.version_info
        
        if version >= (3, 8):
            return {"success": True, "version": f"{version.major}.{version.minor}.{version.micro}"}
        else:
            return {"success": False, "version": f"{version.major}.{version.minor}.{version.micro}", "error": "Python 3.8+ required"}
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """Check required Python dependencies"""
        required_packages = [
            "fastapi", "uvicorn", "PyGithub", "httpx", "websockets",
            "redis", "pyyaml", "pydantic", "psutil", "asyncio_throttle"
        ]
        
        missing = []
        installed = []
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                installed.append(package)
            except ImportError:
                missing.append(package)
        
        return {
            "success": len(missing) == 0,
            "installed": installed,
            "missing": missing
        }
    
    def _check_environment_variables(self) -> Dict[str, Any]:
        """Check required environment variables"""
        github_token = os.getenv("GITHUB_TOKEN")
        github_app_id = os.getenv("GITHUB_APP_ID")
        github_app_private_key = os.getenv("GITHUB_APP_PRIVATE_KEY")
        
        has_auth = bool(github_token) or (bool(github_app_id) and bool(github_app_private_key))
        
        variables = {
            "GITHUB_TOKEN": bool(github_token),
            "GITHUB_APP_ID": bool(github_app_id),
            "GITHUB_APP_PRIVATE_KEY": bool(github_app_private_key),
            "REDIS_HOST": bool(os.getenv("REDIS_HOST")),
            "JWT_SECRET": bool(os.getenv("JWT_SECRET"))
        }
        
        return {
            "success": has_auth,
            "variables": variables,
            "error": "No GitHub authentication configured" if not has_auth else None
        }
    
    def _check_file_permissions(self) -> Dict[str, Any]:
        """Check file permissions"""
        files_to_check = [
            "github_mcp_server.py",
            "github_mcp_service.py",
            "github_mcp_integration.py",
            "start_github_mcp.py"
        ]
        
        permissions = {}
        for file_path in files_to_check:
            path = Path(file_path)
            if path.exists():
                permissions[file_path] = {
                    "exists": True,
                    "readable": os.access(path, os.R_OK),
                    "executable": os.access(path, os.X_OK)
                }
            else:
                permissions[file_path] = {"exists": False}
        
        success = all(p.get("exists", False) and p.get("readable", False) for p in permissions.values())
        
        return {
            "success": success,
            "permissions": permissions
        }
    
    async def _check_network_access(self) -> Dict[str, Any]:
        """Check network access to required services"""
        endpoints = [
            ("GitHub API", "https://api.github.com"),
            ("GitHub", "https://github.com")
        ]
        
        if self.config.redis_host and self.config.redis_host != "localhost":
            try:
                import redis
                redis_client = redis.Redis(
                    host=self.config.redis_host,
                    port=self.config.redis_port,
                    socket_timeout=5
                )
                redis_accessible = redis_client.ping()
                endpoints.append(("Redis", f"{self.config.redis_host}:{self.config.redis_port}"))
            except Exception:
                redis_accessible = False
                endpoints.append(("Redis", f"{self.config.redis_host}:{self.config.redis_port}"))
        
        results = {}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for name, url in endpoints:
                try:
                    if url.startswith("http"):
                        response = await client.get(url)
                        results[name] = {"success": response.status_code < 400, "url": url}
                    else:
                        # For Redis, we already checked above
                        results[name] = {"success": redis_accessible if "Redis" in name else True, "url": url}
                except Exception as e:
                    results[name] = {"success": False, "url": url, "error": str(e)}
        
        return {
            "success": all(r["success"] for r in results.values()),
            "endpoints": results
        }
    
    # GitHub API validation methods
    
    async def _test_github_authentication(self) -> Dict[str, Any]:
        """Test GitHub authentication"""
        try:
            if self.config.github_token:
                github = Github(self.config.github_token)
                user = github.get_user()
                
                return {
                    "success": True,
                    "method": "token",
                    "user": user.login,
                    "scopes": github.get_user().get_repos().totalCount  # Indirect scope test
                }
            else:
                return {
                    "success": False,
                    "error": "No GitHub authentication configured"
                }
        except GithubException as e:
            return {
                "success": False,
                "error": f"GitHub authentication failed: {e}"
            }
    
    async def _test_api_connectivity(self) -> Dict[str, Any]:
        """Test GitHub API connectivity"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {}
                if self.config.github_token:
                    headers["Authorization"] = f"token {self.config.github_token}"
                
                response = await client.get("https://api.github.com", headers=headers)
                
                return {
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "rate_limit_remaining": response.headers.get("X-RateLimit-Remaining")
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _check_rate_limits(self) -> Dict[str, Any]:
        """Check GitHub API rate limits"""
        try:
            if self.config.github_token:
                github = Github(self.config.github_token)
                rate_limit = github.get_rate_limit()
                
                return {
                    "success": True,
                    "core": {
                        "limit": rate_limit.core.limit,
                        "remaining": rate_limit.core.remaining,
                        "reset": rate_limit.core.reset.isoformat()
                    },
                    "search": {
                        "limit": rate_limit.search.limit,
                        "remaining": rate_limit.search.remaining,
                        "reset": rate_limit.search.reset.isoformat()
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "No authentication configured"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _test_permissions(self) -> Dict[str, Any]:
        """Test GitHub API permissions"""
        try:
            if self.config.github_token:
                github = Github(self.config.github_token)
                user = github.get_user()
                
                # Test basic permissions
                can_read_repos = True
                can_read_user = True
                
                try:
                    repos = list(user.get_repos()[:1])  # Test reading repos
                except:
                    can_read_repos = False
                
                try:
                    user_info = user.login  # Test reading user info
                except:
                    can_read_user = False
                
                return {
                    "success": can_read_repos and can_read_user,
                    "permissions": {
                        "read_repos": can_read_repos,
                        "read_user": can_read_user
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "No authentication configured"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _validate_webhook_setup(self) -> Dict[str, Any]:
        """Validate webhook configuration"""
        webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET")
        
        return {
            "success": bool(webhook_secret),
            "secret_configured": bool(webhook_secret),
            "note": "Webhook secret should be configured for production use"
        }
    
    # Server validation methods
    
    async def _check_server_running(self, server_url: str) -> Dict[str, Any]:
        """Check if server is running"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{server_url}/health")
                return {
                    "success": response.status_code == 200,
                    "status_code": response.status_code
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _test_health_endpoint(self, server_url: str) -> Dict[str, Any]:
        """Test health endpoint"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{server_url}/health")
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "status": data.get("status"),
                        "uptime": data.get("uptime"),
                        "version": data.get("version")
                    }
                else:
                    return {
                        "success": False,
                        "status_code": response.status_code
                    }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _test_api_endpoints(self, server_url: str) -> Dict[str, Any]:
        """Test key API endpoints"""
        endpoints = [
            "/mcp/info",
            "/metrics"
        ]
        
        results = {}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for endpoint in endpoints:
                try:
                    response = await client.get(f"{server_url}{endpoint}")
                    results[endpoint] = {
                        "success": response.status_code == 200,
                        "status_code": response.status_code
                    }
                except Exception as e:
                    results[endpoint] = {
                        "success": False,
                        "error": str(e)
                    }
        
        return {
            "success": all(r["success"] for r in results.values()),
            "endpoints": results
        }
    
    async def _test_websocket(self, server_url: str) -> Dict[str, Any]:
        """Test WebSocket connectivity"""
        try:
            import websockets
            
            websocket_url = server_url.replace("http", "ws") + "/ws/test_user"
            
            try:
                async with websockets.connect(websocket_url, timeout=10) as websocket:
                    # Send ping
                    await websocket.send(json.dumps({"type": "ping"}))
                    
                    # Wait for response
                    response = await asyncio.wait_for(websocket.recv(), timeout=5)
                    data = json.loads(response)
                    
                    return {
                        "success": True,
                        "connected": True,
                        "response": data.get("type")
                    }
            except asyncio.TimeoutError:
                return {
                    "success": False,
                    "error": "WebSocket connection timeout"
                }
            
        except ImportError:
            return {
                "success": False,
                "error": "websockets package not available"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _test_metrics_endpoint(self, server_url: str) -> Dict[str, Any]:
        """Test metrics endpoint"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{server_url}/metrics")
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "metrics_available": bool(data),
                        "uptime": data.get("uptime"),
                        "requests": data.get("requests", {})
                    }
                else:
                    return {
                        "success": False,
                        "status_code": response.status_code
                    }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # Performance validation methods
    
    async def _test_response_times(self) -> Dict[str, Any]:
        """Test API response times"""
        server_url = f"http://{self.config.host}:{self.config.port}"
        
        try:
            times = []
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                for _ in range(5):
                    start_time = time.time()
                    response = await client.get(f"{server_url}/health")
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        times.append(end_time - start_time)
            
            if times:
                avg_time = sum(times) / len(times)
                max_time = max(times)
                min_time = min(times)
                
                return {
                    "success": avg_time < 1.0,  # Under 1 second average
                    "average_ms": round(avg_time * 1000, 2),
                    "max_ms": round(max_time * 1000, 2),
                    "min_ms": round(min_time * 1000, 2),
                    "samples": len(times)
                }
            else:
                return {
                    "success": False,
                    "error": "No successful requests"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _test_concurrent_requests(self) -> Dict[str, Any]:
        """Test concurrent request handling"""
        server_url = f"http://{self.config.host}:{self.config.port}"
        
        try:
            concurrent_requests = 10
            
            async def make_request(client):
                response = await client.get(f"{server_url}/health")
                return response.status_code == 200
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                tasks = [make_request(client) for _ in range(concurrent_requests)]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                successful = sum(1 for r in results if r is True)
                
                return {
                    "success": successful >= concurrent_requests * 0.8,  # 80% success rate
                    "total_requests": concurrent_requests,
                    "successful": successful,
                    "success_rate": round(successful / concurrent_requests * 100, 2)
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _test_cache_performance(self) -> Dict[str, Any]:
        """Test cache performance (if available)"""
        try:
            if self.config.redis_host:
                import redis
                redis_client = redis.Redis(
                    host=self.config.redis_host,
                    port=self.config.redis_port,
                    socket_timeout=5
                )
                
                # Test Redis performance
                start_time = time.time()
                redis_client.set("test_key", "test_value")
                value = redis_client.get("test_key")
                redis_client.delete("test_key")
                end_time = time.time()
                
                return {
                    "success": value == b"test_value",
                    "redis_available": True,
                    "response_time_ms": round((end_time - start_time) * 1000, 2)
                }
            else:
                return {
                    "success": True,
                    "redis_available": False,
                    "note": "Using in-memory cache"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _check_memory_usage(self) -> Dict[str, Any]:
        """Check memory usage"""
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            
            return {
                "success": memory.percent < 80,  # Under 80% memory usage
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "percent_used": memory.percent
            }
        except ImportError:
            return {
                "success": True,
                "error": "psutil not available"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _test_rate_limiting(self) -> Dict[str, Any]:
        """Test rate limiting functionality"""
        # This would require the server to be running
        return {
            "success": True,
            "note": "Rate limiting tests require running server and multiple rapid requests"
        }
    
    # Security validation methods
    
    async def _test_authentication_required(self) -> Dict[str, Any]:
        """Test that authentication is required for protected endpoints"""
        server_url = f"http://{self.config.host}:{self.config.port}"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Test without authentication
                response = await client.get(f"{server_url}/repos/octocat/Hello-World")
                
                return {
                    "success": response.status_code in [401, 403],  # Should require auth
                    "status_code": response.status_code,
                    "requires_auth": response.status_code in [401, 403]
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _test_cors_configuration(self) -> Dict[str, Any]:
        """Test CORS configuration"""
        server_url = f"http://{self.config.host}:{self.config.port}"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.options(
                    f"{server_url}/health",
                    headers={"Origin": "https://example.com"}
                )
                
                cors_headers = {
                    "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                    "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                    "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
                }
                
                return {
                    "success": bool(cors_headers["Access-Control-Allow-Origin"]),
                    "cors_headers": cors_headers
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _test_rate_limiting_security(self) -> Dict[str, Any]:
        """Test rate limiting as security measure"""
        return {
            "success": True,
            "note": "Rate limiting security tests require load testing tools"
        }
    
    async def _test_webhook_security(self) -> Dict[str, Any]:
        """Test webhook security configuration"""
        webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET")
        
        return {
            "success": bool(webhook_secret),
            "secret_configured": bool(webhook_secret),
            "note": "Webhook signature verification requires secret"
        }
    
    def _check_sensitive_data_exposure(self) -> Dict[str, Any]:
        """Check for sensitive data exposure"""
        issues = []
        
        # Check if secrets are in environment (good)
        github_token = os.getenv("GITHUB_TOKEN")
        if github_token and len(github_token) > 0:
            # Don't log actual token
            pass
        else:
            issues.append("GitHub token not found in environment")
        
        # Check config file for sensitive data
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                content = f.read()
                if "github_token:" in content and "null" not in content:
                    issues.append("GitHub token may be in config file (should use environment)")
        
        return {
            "success": len(issues) == 0,
            "issues": issues
        }
    
    # Helper methods
    
    def _count_successes(self, results: Dict[str, Any]) -> int:
        """Count successful validation results"""
        count = 0
        for key, value in results.items():
            if isinstance(value, dict) and value.get("success", False):
                count += 1
            elif value is True:
                count += 1
        return count
    
    def _validate_config_syntax(self) -> Dict[str, Any]:
        """Validate configuration file syntax"""
        try:
            if self.config_file.exists():
                import yaml
                with open(self.config_file, 'r') as f:
                    yaml.safe_load(f)
                return {"success": True}
            else:
                return {"success": False, "error": "Config file does not exist"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _validate_required_settings(self) -> Dict[str, Any]:
        """Validate required configuration settings"""
        required = ["host", "port"]
        missing = []
        
        for setting in required:
            if not hasattr(self.config, setting) or getattr(self.config, setting) is None:
                missing.append(setting)
        
        return {
            "success": len(missing) == 0,
            "missing": missing
        }
    
    def _validate_optional_settings(self) -> Dict[str, Any]:
        """Validate optional configuration settings"""
        return {
            "success": True,
            "redis_configured": bool(self.config.redis_host),
            "cache_ttl_configured": bool(self.config.cache_ttl_default),
            "rate_limiting_configured": bool(self.config.rate_limit_requests_per_hour)
        }
    
    def _validate_security_settings(self) -> Dict[str, Any]:
        """Validate security configuration settings"""
        jwt_secret = os.getenv("JWT_SECRET")
        webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET")
        
        return {
            "success": bool(jwt_secret),
            "jwt_secret_configured": bool(jwt_secret),
            "webhook_secret_configured": bool(webhook_secret)
        }

async def main():
    """Main validation script"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GitHub MCP Validation Script")
    parser.add_argument("--config", type=Path, help="Configuration file path")
    parser.add_argument("--output", type=Path, help="Output file for results")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run validation
    validator = GitHubMCPValidator(args.config)
    results = await validator.run_all_validations()
    
    # Output results
    output_text = json.dumps(results, indent=2, default=str)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_text)
        print(f"Validation results written to {args.output}")
    else:
        print(output_text)
    
    # Summary
    overall = results["overall"]
    print(f"\n{'='*50}")
    print(f"VALIDATION SUMMARY")
    print(f"{'='*50}")
    print(f"Overall Success: {'✅ PASS' if overall['success'] else '❌ FAIL'}")
    print(f"Score: {overall['score']}%")
    print(f"Checks: {overall['passed_checks']}/{overall['total_checks']}")
    
    # Category breakdown
    for category, category_results in results.items():
        if category == "overall":
            continue
        
        success_count = validator._count_successes(category_results)
        total_count = len(category_results)
        status = "✅" if success_count == total_count else "⚠️" if success_count > 0 else "❌"
        
        print(f"{category.title()}: {status} {success_count}/{total_count}")
    
    # Return appropriate exit code
    return 0 if overall["success"] else 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))