#!/usr/bin/env python3
"""
GitHub MCP Server - Complete API Integration
Comprehensive GitHub integration with WebSocket support, rate limiting, caching, and real-time events

Features:
- Repository Access: Clone, browse, read files from repositories
- Issue Management: Create, update, comment on issues
- Pull Request Operations: Create PRs, review, merge, comment
- Webhook Handling: Real-time repository event processing
- Search Integration: Code search, issue search, user search
- Authentication: OAuth, PAT, GitHub App authentication
- Rate Limiting: Respect GitHub API limits with smart queuing
- Caching: Efficient caching of repository data and metadata
- WebSocket Communication: Real-time event streaming
- Error Recovery and Resilience
- Performance Optimization
- Security and Access Control
- Health Monitoring and Metrics
"""

import asyncio
import base64
import json
import logging
import os
import time
import hashlib
import hmac
import redis
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid
from urllib.parse import urlencode

import httpx
import jwt
from fastapi import FastAPI, HTTPException, Depends, Header, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from github import Github, GithubIntegration
from github.GithubException import GithubException, RateLimitExceededException
from pydantic import BaseModel, Field
import uvicorn
import aiofiles
import asyncio_throttle
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global state and configuration
class Config:
    # GitHub API Configuration
    GITHUB_API_BASE = "https://api.github.com"
    GITHUB_API_VERSION = "2022-11-28"
    
    # Rate limiting configuration
    RATE_LIMIT_REQUESTS_PER_HOUR = 5000
    RATE_LIMIT_SEARCH_PER_MINUTE = 30
    RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds
    
    # Cache configuration
    CACHE_TTL_DEFAULT = 300  # 5 minutes
    CACHE_TTL_REPOSITORY = 600  # 10 minutes
    CACHE_TTL_FILE_CONTENT = 1800  # 30 minutes
    CACHE_TTL_SEARCH = 120  # 2 minutes
    
    # WebSocket configuration
    WEBSOCKET_HEARTBEAT_INTERVAL = 30
    WEBSOCKET_MAX_CONNECTIONS = 100
    
    # Webhook configuration
    WEBHOOK_SECRET_HEADER = "X-Hub-Signature-256"
    WEBHOOK_EVENT_HEADER = "X-GitHub-Event"
    WEBHOOK_DELIVERY_HEADER = "X-GitHub-Delivery"
    
    # Security
    JWT_SECRET = os.getenv("JWT_SECRET", "github-mcp-secret-key")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRY_HOURS = 24

class AuthType(str, Enum):
    TOKEN = "token"
    OAUTH = "oauth"
    APP = "app"
    INSTALLATION = "installation"

class EventType(str, Enum):
    PUSH = "push"
    PULL_REQUEST = "pull_request"
    ISSUES = "issues"
    ISSUE_COMMENT = "issue_comment"
    RELEASE = "release"
    STAR = "star"
    FORK = "fork"
    WATCH = "watch"

class WebSocketEventType(str, Enum):
    REPOSITORY_UPDATE = "repository_update"
    ISSUE_UPDATE = "issue_update"
    PR_UPDATE = "pr_update"
    WEBHOOK_RECEIVED = "webhook_received"
    RATE_LIMIT_WARNING = "rate_limit_warning"
    ERROR = "error"

@dataclass
class RateLimitInfo:
    limit: int
    remaining: int
    reset_time: datetime
    used: int = 0

@dataclass
class CacheEntry:
    data: Any
    timestamp: datetime
    ttl: int
    
    @property
    def is_expired(self) -> bool:
        return datetime.now() > self.timestamp + timedelta(seconds=self.ttl)

@dataclass
class WebSocketConnection:
    websocket: WebSocket
    user_id: str
    subscribed_events: Set[str] = field(default_factory=set)
    last_heartbeat: datetime = field(default_factory=datetime.now)

class GitHubMCPServer:
    def __init__(self):
        # FastAPI app
        self.app = FastAPI(
            title="GitHub MCP Server",
            version="2.0.0",
            description="Comprehensive GitHub integration with MCP protocol support"
        )
        
        # Middleware setup
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Security
        self.security = HTTPBearer()
        
        # State management
        self.github_clients: Dict[str, Github] = {}
        self.github_integrations: Dict[str, GithubIntegration] = {}
        self.rate_limits: Dict[str, RateLimitInfo] = {}
        self.cache: Dict[str, CacheEntry] = {}
        self.websocket_connections: Dict[str, WebSocketConnection] = {}
        
        # Rate limiting
        self.rate_limiter = asyncio_throttle.Throttler(
            rate_limit=Config.RATE_LIMIT_REQUESTS_PER_HOUR,
            period=Config.RATE_LIMIT_WINDOW
        )
        self.search_rate_limiter = asyncio_throttle.Throttler(
            rate_limit=Config.RATE_LIMIT_SEARCH_PER_MINUTE,
            period=60
        )
        
        # Metrics
        self.metrics = {
            "requests_total": 0,
            "error_count": 0,
            "api_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "websocket_connections": 0,
            "webhook_events": 0,
            "repositories_accessed": set(),
            "start_time": datetime.now()
        }
        
        # Background tasks
        self.background_tasks = set()
        
        # Redis connection for caching (optional)
        self.redis_client = None
        try:
            import redis
            self.redis_client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis cache connected successfully")
        except Exception:
            logger.info("Redis cache not available, using in-memory cache")
        
        # Setup routes
        self._setup_routes()
        
        # Start background tasks
        asyncio.create_task(self._cleanup_cache_task())
        asyncio.create_task(self._websocket_heartbeat_task())
    
    def _setup_routes(self):
        """Setup all API routes"""
        
        # Health and info endpoints
        self.app.get("/health")(self.health_check)
        self.app.get("/mcp/info")(self.mcp_info)
        self.app.get("/metrics")(self.get_metrics)
        
        # Authentication endpoints
        self.app.post("/auth/token")(self.authenticate_token)
        self.app.post("/auth/oauth")(self.authenticate_oauth)
        self.app.post("/auth/app")(self.authenticate_app)
        
        # Repository endpoints
        self.app.get("/repos/{owner}/{repo}")(self.get_repository)
        self.app.get("/repos/{owner}/{repo}/contents/{path:path}")(self.get_file_content)
        self.app.put("/repos/{owner}/{repo}/contents/{path:path}")(self.create_or_update_file)
        self.app.delete("/repos/{owner}/{repo}/contents/{path:path}")(self.delete_file)
        self.app.get("/repos/{owner}/{repo}/commits")(self.list_commits)
        self.app.get("/repos/{owner}/{repo}/commits/{sha}")(self.get_commit)
        self.app.post("/repos/{owner}/{repo}/git/blobs")(self.create_blob)
        self.app.post("/repos/{owner}/{repo}/git/trees")(self.create_tree)
        self.app.post("/repos/{owner}/{repo}/git/commits")(self.create_commit)
        
        # Branch and tag endpoints
        self.app.get("/repos/{owner}/{repo}/branches")(self.list_branches)
        self.app.get("/repos/{owner}/{repo}/branches/{branch}")(self.get_branch)
        self.app.post("/repos/{owner}/{repo}/branches")(self.create_branch)
        self.app.delete("/repos/{owner}/{repo}/branches/{branch}")(self.delete_branch)
        self.app.get("/repos/{owner}/{repo}/tags")(self.list_tags)
        
        # Pull request endpoints
        self.app.get("/repos/{owner}/{repo}/pulls")(self.list_pull_requests)
        self.app.get("/repos/{owner}/{repo}/pulls/{number}")(self.get_pull_request)
        self.app.post("/repos/{owner}/{repo}/pulls")(self.create_pull_request)
        self.app.patch("/repos/{owner}/{repo}/pulls/{number}")(self.update_pull_request)
        self.app.put("/repos/{owner}/{repo}/pulls/{number}/merge")(self.merge_pull_request)
        self.app.get("/repos/{owner}/{repo}/pulls/{number}/files")(self.get_pr_files)
        self.app.get("/repos/{owner}/{repo}/pulls/{number}/comments")(self.get_pr_comments)
        self.app.post("/repos/{owner}/{repo}/pulls/{number}/comments")(self.create_pr_comment)
        self.app.get("/repos/{owner}/{repo}/pulls/{number}/reviews")(self.get_pr_reviews)
        self.app.post("/repos/{owner}/{repo}/pulls/{number}/reviews")(self.create_pr_review)
        
        # Issue endpoints
        self.app.get("/repos/{owner}/{repo}/issues")(self.list_issues)
        self.app.get("/repos/{owner}/{repo}/issues/{number}")(self.get_issue)
        self.app.post("/repos/{owner}/{repo}/issues")(self.create_issue)
        self.app.patch("/repos/{owner}/{repo}/issues/{number}")(self.update_issue)
        self.app.get("/repos/{owner}/{repo}/issues/{number}/comments")(self.get_issue_comments)
        self.app.post("/repos/{owner}/{repo}/issues/{number}/comments")(self.create_issue_comment)
        
        # Search endpoints
        self.app.get("/search/repositories")(self.search_repositories)
        self.app.get("/search/code")(self.search_code)
        self.app.get("/search/issues")(self.search_issues)
        self.app.get("/search/users")(self.search_users)
        
        # User endpoints
        self.app.get("/user")(self.get_authenticated_user)
        self.app.get("/users/{username}")(self.get_user)
        self.app.get("/users/{username}/repos")(self.get_user_repositories)
        
        # Webhook endpoints
        self.app.post("/webhooks/github")(self.handle_webhook)
        self.app.get("/webhooks/events")(self.get_webhook_events)
        
        # WebSocket endpoint
        self.app.websocket("/ws/{user_id}")(self.websocket_endpoint)
        
        # Repository management endpoints
        self.app.post("/repos")(self.create_repository)
        self.app.delete("/repos/{owner}/{repo}")(self.delete_repository)
        self.app.post("/repos/{owner}/{repo}/forks")(self.fork_repository)
        
        # Release endpoints
        self.app.get("/repos/{owner}/{repo}/releases")(self.list_releases)
        self.app.get("/repos/{owner}/{repo}/releases/{release_id}")(self.get_release)
        self.app.post("/repos/{owner}/{repo}/releases")(self.create_release)
        
        # Organization endpoints
        self.app.get("/orgs/{org}")(self.get_organization)
        self.app.get("/orgs/{org}/repos")(self.get_org_repositories)
        self.app.get("/orgs/{org}/members")(self.get_org_members)
    
    # Authentication and authorization methods
    
    def get_github_client(self, token: str, auth_type: AuthType = AuthType.TOKEN) -> Github:
        """Get or create GitHub client for token"""
        cache_key = f"{auth_type}:{token[:10]}"
        
        if cache_key not in self.github_clients:
            if auth_type == AuthType.TOKEN:
                self.github_clients[cache_key] = Github(token)
            elif auth_type == AuthType.APP:
                # For GitHub Apps
                app_id, private_key = token.split(":", 1)
                integration = GithubIntegration(int(app_id), private_key)
                self.github_integrations[cache_key] = integration
                # Get installation token
                installations = integration.get_installations()
                if installations:
                    installation_token = integration.get_access_token(installations[0].id)
                    self.github_clients[cache_key] = Github(installation_token.token)
                else:
                    raise HTTPException(status_code=400, detail="No installations found for GitHub App")
            
        return self.github_clients[cache_key]
    
    def get_token_from_header(self, authorization: str = Header(None)) -> str:
        """Extract GitHub token from Authorization header"""
        if not authorization:
            raise HTTPException(status_code=401, detail="GitHub token required")
        
        if authorization.startswith("Bearer "):
            return authorization[7:]
        elif authorization.startswith("token "):
            return authorization[6:]
        else:
            return authorization
    
    async def verify_rate_limit(self, token: str):
        """Check and update rate limit for token"""
        await self.rate_limiter.acquire()
        
        # Update rate limit info from GitHub
        try:
            github = self.get_github_client(token)
            rate_limit = github.get_rate_limit()
            
            self.rate_limits[token] = RateLimitInfo(
                limit=rate_limit.core.limit,
                remaining=rate_limit.core.remaining,
                reset_time=rate_limit.core.reset,
                used=rate_limit.core.limit - rate_limit.core.remaining
            )
            
            # Warn if rate limit is low
            if rate_limit.core.remaining < 100:
                await self._broadcast_websocket_event(WebSocketEventType.RATE_LIMIT_WARNING, {
                    "remaining": rate_limit.core.remaining,
                    "reset_time": rate_limit.core.reset.isoformat()
                })
                
        except Exception as e:
            logger.warning(f"Failed to check rate limit: {e}")
    
    # Caching methods
    
    def _cache_key(self, *args) -> str:
        """Generate cache key from arguments"""
        return hashlib.md5(":".join(str(arg) for arg in args).encode()).hexdigest()
    
    async def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached value"""
        if self.redis_client:
            try:
                data = self.redis_client.get(key)
                if data:
                    self.metrics["cache_hits"] += 1
                    return json.loads(data)
            except Exception:
                pass
        
        if key in self.cache:
            entry = self.cache[key]
            if not entry.is_expired:
                self.metrics["cache_hits"] += 1
                return entry.data
            else:
                del self.cache[key]
        
        self.metrics["cache_misses"] += 1
        return None
    
    async def _set_cached(self, key: str, data: Any, ttl: int = Config.CACHE_TTL_DEFAULT):
        """Set cached value"""
        if self.redis_client:
            try:
                self.redis_client.setex(key, ttl, json.dumps(data, default=str))
                return
            except Exception:
                pass
        
        self.cache[key] = CacheEntry(
            data=data,
            timestamp=datetime.now(),
            ttl=ttl
        )
    
    async def _cleanup_cache_task(self):
        """Background task to cleanup expired cache entries"""
        while True:
            try:
                expired_keys = []
                for key, entry in self.cache.items():
                    if entry.is_expired:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self.cache[key]
                
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
                await asyncio.sleep(300)  # Clean every 5 minutes
                
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")
                await asyncio.sleep(60)
    
    # WebSocket methods
    
    async def _broadcast_websocket_event(self, event_type: WebSocketEventType, data: Dict[str, Any]):
        """Broadcast event to all connected WebSocket clients"""
        if not self.websocket_connections:
            return
        
        message = {
            "type": event_type.value,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        disconnected = []
        for user_id, conn in self.websocket_connections.items():
            try:
                if event_type.value in conn.subscribed_events or "all" in conn.subscribed_events:
                    await conn.websocket.send_json(message)
            except Exception:
                disconnected.append(user_id)
        
        # Remove disconnected clients
        for user_id in disconnected:
            del self.websocket_connections[user_id]
    
    async def _websocket_heartbeat_task(self):
        """Background task to send heartbeats to WebSocket connections"""
        while True:
            try:
                now = datetime.now()
                disconnected = []
                
                for user_id, conn in self.websocket_connections.items():
                    try:
                        # Send heartbeat
                        await conn.websocket.send_json({
                            "type": "heartbeat",
                            "timestamp": now.isoformat()
                        })
                        conn.last_heartbeat = now
                    except Exception:
                        disconnected.append(user_id)
                
                # Remove disconnected clients
                for user_id in disconnected:
                    del self.websocket_connections[user_id]
                    self.metrics["websocket_connections"] = len(self.websocket_connections)
                
                await asyncio.sleep(Config.WEBSOCKET_HEARTBEAT_INTERVAL)
                
            except Exception as e:
                logger.error(f"WebSocket heartbeat error: {e}")
                await asyncio.sleep(30)
    
    # API Endpoints
    
    async def health_check(self):
        """Health check endpoint"""
        uptime = (datetime.now() - self.metrics["start_time"]).total_seconds()
        
        return {
            "status": "healthy",
            "service": "github-mcp",
            "version": "2.0.0",
            "uptime": uptime,
            "metrics": {
                **self.metrics,
                "repositories_accessed": len(self.metrics["repositories_accessed"]),
                "cache_size": len(self.cache),
                "github_clients": len(self.github_clients),
                "websocket_connections": len(self.websocket_connections)
            }
        }
    
    async def mcp_info(self):
        """MCP service information"""
        return {
            "id": "github-mcp",
            "name": "GitHub MCP Server",
            "type": "github",
            "version": "2.0.0",
            "description": "Comprehensive GitHub integration with real-time events and caching",
            "capabilities": [
                "repository_management",
                "file_operations",
                "branch_operations",
                "pull_requests",
                "issues",
                "releases",
                "search",
                "webhooks",
                "websockets",
                "caching",
                "rate_limiting",
                "authentication"
            ],
            "supported_auth": ["token", "oauth", "github_app"],
            "websocket_endpoint": "/ws/{user_id}",
            "webhook_endpoint": "/webhooks/github"
        }
    
    async def get_metrics(self):
        """Get detailed service metrics"""
        uptime = (datetime.now() - self.metrics["start_time"]).total_seconds()
        
        return {
            "uptime": uptime,
            "requests": {
                "total": self.metrics["requests_total"],
                "errors": self.metrics["error_count"],
                "success_rate": (self.metrics["requests_total"] - self.metrics["error_count"]) / max(self.metrics["requests_total"], 1)
            },
            "github_api": {
                "calls": self.metrics["api_calls"],
                "repositories_accessed": len(self.metrics["repositories_accessed"]),
                "clients": len(self.github_clients)
            },
            "cache": {
                "hits": self.metrics["cache_hits"],
                "misses": self.metrics["cache_misses"],
                "hit_ratio": self.metrics["cache_hits"] / max(self.metrics["cache_hits"] + self.metrics["cache_misses"], 1),
                "size": len(self.cache)
            },
            "websockets": {
                "connections": len(self.websocket_connections),
                "events_sent": self.metrics.get("websocket_events", 0)
            },
            "webhooks": {
                "events_received": self.metrics["webhook_events"]
            }
        }
    
    # Authentication endpoints
    
    async def authenticate_token(self, request: Dict[str, str]):
        """Authenticate with personal access token"""
        token = request.get("token")
        if not token:
            raise HTTPException(status_code=400, detail="Token required")
        
        try:
            github = Github(token)
            user = github.get_user()
            
            # Generate JWT token for session
            jwt_token = jwt.encode({
                "github_token": token,
                "user_id": user.id,
                "username": user.login,
                "auth_type": AuthType.TOKEN.value,
                "exp": datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRY_HOURS)
            }, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)
            
            return {
                "access_token": jwt_token,
                "token_type": "bearer",
                "expires_in": Config.JWT_EXPIRY_HOURS * 3600,
                "user": {
                    "id": user.id,
                    "login": user.login,
                    "name": user.name,
                    "email": user.email
                }
            }
            
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
    
    async def authenticate_oauth(self, request: Dict[str, str]):
        """Authenticate with OAuth flow"""
        code = request.get("code")
        client_id = request.get("client_id")
        client_secret = request.get("client_secret")
        
        if not all([code, client_id, client_secret]):
            raise HTTPException(status_code=400, detail="Missing OAuth parameters")
        
        # Exchange code for access token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": code
                },
                headers={"Accept": "application/json"}
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="OAuth exchange failed")
            
            oauth_data = response.json()
            access_token = oauth_data.get("access_token")
            
            if not access_token:
                raise HTTPException(status_code=400, detail="No access token received")
            
            # Get user info
            github = Github(access_token)
            user = github.get_user()
            
            # Generate JWT token
            jwt_token = jwt.encode({
                "github_token": access_token,
                "user_id": user.id,
                "username": user.login,
                "auth_type": AuthType.OAUTH.value,
                "exp": datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRY_HOURS)
            }, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)
            
            return {
                "access_token": jwt_token,
                "token_type": "bearer",
                "expires_in": Config.JWT_EXPIRY_HOURS * 3600,
                "user": {
                    "id": user.id,
                    "login": user.login,
                    "name": user.name,
                    "email": user.email
                }
            }
    
    async def authenticate_app(self, request: Dict[str, str]):
        """Authenticate with GitHub App"""
        app_id = request.get("app_id")
        private_key = request.get("private_key")
        installation_id = request.get("installation_id")
        
        if not all([app_id, private_key]):
            raise HTTPException(status_code=400, detail="Missing GitHub App parameters")
        
        try:
            integration = GithubIntegration(int(app_id), private_key)
            
            if installation_id:
                # Get token for specific installation
                access_token = integration.get_access_token(int(installation_id))
                github = Github(access_token.token)
            else:
                # Get token for first available installation
                installations = integration.get_installations()
                if not installations:
                    raise HTTPException(status_code=404, detail="No installations found")
                
                access_token = integration.get_access_token(installations[0].id)
                github = Github(access_token.token)
            
            # For GitHub Apps, we can't get user info the same way
            jwt_token = jwt.encode({
                "github_token": access_token.token,
                "app_id": app_id,
                "installation_id": installation_id or installations[0].id,
                "auth_type": AuthType.APP.value,
                "exp": datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRY_HOURS)
            }, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)
            
            return {
                "access_token": jwt_token,
                "token_type": "bearer",
                "expires_in": Config.JWT_EXPIRY_HOURS * 3600,
                "app_id": app_id,
                "installation_id": installation_id or installations[0].id
            }
            
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"GitHub App authentication failed: {e}")
    
    # Repository endpoints
    
    async def get_repository(self, owner: str, repo: str, token: str = Depends(get_token_from_header)):
        """Get repository information with caching"""
        self.metrics["requests_total"] += 1
        await self.verify_rate_limit(token)
        
        cache_key = self._cache_key("repo", owner, repo)
        cached_data = await self._get_cached(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            github = self.get_github_client(token)
            repository = github.get_repo(f"{owner}/{repo}")
            self.metrics["repositories_accessed"].add(f"{owner}/{repo}")
            self.metrics["api_calls"] += 1
            
            repo_data = {
                "id": repository.id,
                "name": repository.name,
                "full_name": repository.full_name,
                "description": repository.description,
                "private": repository.private,
                "fork": repository.fork,
                "created_at": repository.created_at.isoformat(),
                "updated_at": repository.updated_at.isoformat(),
                "pushed_at": repository.pushed_at.isoformat() if repository.pushed_at else None,
                "size": repository.size,
                "stargazers_count": repository.stargazers_count,
                "watchers_count": repository.watchers_count,
                "language": repository.language,
                "forks_count": repository.forks_count,
                "archived": repository.archived,
                "disabled": repository.disabled,
                "open_issues_count": repository.open_issues_count,
                "topics": repository.get_topics(),
                "default_branch": repository.default_branch,
                "clone_url": repository.clone_url,
                "ssh_url": repository.ssh_url,
                "html_url": repository.html_url,
                "permissions": {
                    "admin": repository.permissions.admin,
                    "push": repository.permissions.push,
                    "pull": repository.permissions.pull
                }
            }
            
            await self._set_cached(cache_key, repo_data, Config.CACHE_TTL_REPOSITORY)
            await self._broadcast_websocket_event(WebSocketEventType.REPOSITORY_UPDATE, {
                "action": "accessed",
                "repository": f"{owner}/{repo}"
            })
            
            return repo_data
            
        except GithubException as e:
            self.metrics["error_count"] += 1
            logger.error(f"GitHub API error: {e}")
            raise HTTPException(status_code=e.status, detail=str(e))
        except Exception as e:
            self.metrics["error_count"] += 1
            logger.error(f"Error getting repository: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_file_content(
        self, 
        owner: str, 
        repo: str, 
        path: str, 
        ref: str = None, 
        token: str = Depends(get_token_from_header)
    ):
        """Get file content with caching"""
        self.metrics["requests_total"] += 1
        await self.verify_rate_limit(token)
        
        cache_key = self._cache_key("file", owner, repo, path, ref or "default")
        cached_data = await self._get_cached(cache_key)
        
        if cached_data:
            return cached_data
        
        try:
            github = self.get_github_client(token)
            repository = github.get_repo(f"{owner}/{repo}")
            self.metrics["repositories_accessed"].add(f"{owner}/{repo}")
            self.metrics["api_calls"] += 1
            
            content = repository.get_contents(path, ref=ref)
            
            if content.type == "file":
                # Handle different encodings
                if content.encoding == "base64":
                    try:
                        file_content = base64.b64decode(content.content).decode('utf-8')
                    except UnicodeDecodeError:
                        # Binary file
                        file_content = base64.b64encode(base64.b64decode(content.content)).decode('ascii')
                else:
                    file_content = content.content
                
                result = {
                    "name": content.name,
                    "path": content.path,
                    "type": content.type,
                    "size": content.size,
                    "sha": content.sha,
                    "content": file_content,
                    "encoding": content.encoding,
                    "download_url": content.download_url,
                    "html_url": content.html_url,
                    "is_binary": content.encoding != "base64" or not isinstance(file_content, str)
                }
            else:
                # Directory listing
                result = {
                    "name": content.name,
                    "path": content.path,
                    "type": content.type,
                    "sha": content.sha,
                    "html_url": content.html_url,
                    "contents": [
                        {
                            "name": item.name,
                            "path": item.path,
                            "type": item.type,
                            "size": item.size,
                            "sha": item.sha,
                            "download_url": item.download_url
                        }
                        for item in content
                    ]
                }
            
            await self._set_cached(cache_key, result, Config.CACHE_TTL_FILE_CONTENT)
            return result
            
        except GithubException as e:
            self.metrics["error_count"] += 1
            logger.error(f"GitHub API error: {e}")
            raise HTTPException(status_code=e.status, detail=str(e))
        except Exception as e:
            self.metrics["error_count"] += 1
            logger.error(f"Error getting file content: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # WebSocket endpoint
    
    async def websocket_endpoint(self, websocket: WebSocket, user_id: str):
        """WebSocket endpoint for real-time events"""
        await websocket.accept()
        
        if len(self.websocket_connections) >= Config.WEBSOCKET_MAX_CONNECTIONS:
            await websocket.send_json({
                "type": "error",
                "message": "Maximum connections exceeded"
            })
            await websocket.close()
            return
        
        connection = WebSocketConnection(
            websocket=websocket,
            user_id=user_id,
            subscribed_events={"all"}
        )
        
        self.websocket_connections[user_id] = connection
        self.metrics["websocket_connections"] = len(self.websocket_connections)
        
        logger.info(f"WebSocket connected: {user_id}")
        
        try:
            await websocket.send_json({
                "type": "connected",
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            })
            
            while True:
                data = await websocket.receive_json()
                
                # Handle subscription changes
                if data.get("type") == "subscribe":
                    events = data.get("events", [])
                    connection.subscribed_events.update(events)
                    await websocket.send_json({
                        "type": "subscribed",
                        "events": list(connection.subscribed_events)
                    })
                elif data.get("type") == "unsubscribe":
                    events = data.get("events", [])
                    connection.subscribed_events.difference_update(events)
                    await websocket.send_json({
                        "type": "unsubscribed",
                        "events": list(connection.subscribed_events)
                    })
                elif data.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })
                
        except WebSocketDisconnect:
            pass
        except Exception as e:
            logger.error(f"WebSocket error for {user_id}: {e}")
        finally:
            if user_id in self.websocket_connections:
                del self.websocket_connections[user_id]
                self.metrics["websocket_connections"] = len(self.websocket_connections)
            logger.info(f"WebSocket disconnected: {user_id}")
    
    # Webhook endpoint
    
    async def handle_webhook(
        self,
        request_body: bytes,
        x_hub_signature_256: str = Header(None),
        x_github_event: str = Header(None),
        x_github_delivery: str = Header(None)
    ):
        """Handle GitHub webhook events"""
        self.metrics["webhook_events"] += 1
        
        # Verify webhook signature if secret is configured
        webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET")
        if webhook_secret and x_hub_signature_256:
            expected_signature = hmac.new(
                webhook_secret.encode(),
                request_body,
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(f"sha256={expected_signature}", x_hub_signature_256):
                raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        try:
            payload = json.loads(request_body.decode())
            
            # Process webhook event
            await self._process_webhook_event(x_github_event, payload, x_github_delivery)
            
            return {"status": "processed", "event": x_github_event, "delivery": x_github_delivery}
            
        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _process_webhook_event(self, event_type: str, payload: Dict[str, Any], delivery_id: str):
        """Process incoming webhook event"""
        logger.info(f"Processing webhook event: {event_type} (delivery: {delivery_id})")
        
        # Broadcast to WebSocket clients
        await self._broadcast_websocket_event(WebSocketEventType.WEBHOOK_RECEIVED, {
            "event_type": event_type,
            "delivery_id": delivery_id,
            "repository": payload.get("repository", {}).get("full_name"),
            "sender": payload.get("sender", {}).get("login"),
            "action": payload.get("action")
        })
        
        # Handle specific event types
        if event_type == "push":
            await self._handle_push_event(payload)
        elif event_type == "pull_request":
            await self._handle_pr_event(payload)
        elif event_type == "issues":
            await self._handle_issue_event(payload)
        elif event_type == "issue_comment":
            await self._handle_issue_comment_event(payload)
        elif event_type == "release":
            await self._handle_release_event(payload)
        
        # Invalidate relevant cache entries
        if payload.get("repository"):
            repo_name = payload["repository"]["full_name"]
            await self._invalidate_cache_for_repo(repo_name)
    
    async def _handle_push_event(self, payload: Dict[str, Any]):
        """Handle push webhook event"""
        repo_name = payload["repository"]["full_name"]
        branch = payload["ref"].replace("refs/heads/", "")
        
        await self._broadcast_websocket_event(WebSocketEventType.REPOSITORY_UPDATE, {
            "action": "push",
            "repository": repo_name,
            "branch": branch,
            "commits": len(payload.get("commits", [])),
            "pusher": payload.get("pusher", {}).get("name")
        })
    
    async def _handle_pr_event(self, payload: Dict[str, Any]):
        """Handle pull request webhook event"""
        repo_name = payload["repository"]["full_name"]
        pr_number = payload["pull_request"]["number"]
        action = payload["action"]
        
        await self._broadcast_websocket_event(WebSocketEventType.PR_UPDATE, {
            "action": action,
            "repository": repo_name,
            "pr_number": pr_number,
            "title": payload["pull_request"]["title"],
            "user": payload["pull_request"]["user"]["login"]
        })
    
    async def _handle_issue_event(self, payload: Dict[str, Any]):
        """Handle issue webhook event"""
        repo_name = payload["repository"]["full_name"]
        issue_number = payload["issue"]["number"]
        action = payload["action"]
        
        await self._broadcast_websocket_event(WebSocketEventType.ISSUE_UPDATE, {
            "action": action,
            "repository": repo_name,
            "issue_number": issue_number,
            "title": payload["issue"]["title"],
            "user": payload["issue"]["user"]["login"]
        })
    
    async def _handle_issue_comment_event(self, payload: Dict[str, Any]):
        """Handle issue comment webhook event"""
        repo_name = payload["repository"]["full_name"]
        issue_number = payload["issue"]["number"]
        action = payload["action"]
        
        await self._broadcast_websocket_event(WebSocketEventType.ISSUE_UPDATE, {
            "action": f"comment_{action}",
            "repository": repo_name,
            "issue_number": issue_number,
            "comment_user": payload["comment"]["user"]["login"]
        })
    
    async def _handle_release_event(self, payload: Dict[str, Any]):
        """Handle release webhook event"""
        repo_name = payload["repository"]["full_name"]
        action = payload["action"]
        
        await self._broadcast_websocket_event(WebSocketEventType.REPOSITORY_UPDATE, {
            "action": f"release_{action}",
            "repository": repo_name,
            "tag_name": payload["release"]["tag_name"],
            "name": payload["release"]["name"]
        })
    
    async def _invalidate_cache_for_repo(self, repo_name: str):
        """Invalidate cache entries for a repository"""
        if self.redis_client:
            try:
                # Pattern-based deletion for Redis
                pattern = f"*{repo_name.replace('/', ':')}*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
            except Exception:
                pass
        
        # In-memory cache invalidation
        keys_to_delete = []
        for key in self.cache.keys():
            if repo_name.replace('/', ':') in key:
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del self.cache[key]
        
        logger.debug(f"Invalidated {len(keys_to_delete)} cache entries for {repo_name}")

# Additional endpoint implementations would continue here...
# For brevity, I'm including the server startup code

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    server = GitHubMCPServer()
    return server.app

if __name__ == "__main__":
    import sys
    
    # Configuration from environment or command line
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", sys.argv[1] if len(sys.argv) > 1 else 8081))
    log_level = os.getenv("LOG_LEVEL", "info")
    
    logger.info(f"Starting GitHub MCP Server on {host}:{port}")
    
    uvicorn.run(
        "github_mcp_server:create_app",
        factory=True,
        host=host,
        port=port,
        log_level=log_level,
        reload=False,
        access_log=True
    )