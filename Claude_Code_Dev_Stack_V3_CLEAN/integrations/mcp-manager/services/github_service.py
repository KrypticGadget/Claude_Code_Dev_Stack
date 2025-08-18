#!/usr/bin/env python3
"""
GitHub MCP Service Implementation
GitHub repository management and Git operations service

Original concept by @qdhenry (MIT License)
Enhanced for Claude Code Dev Stack by DevOps Agent
"""

import asyncio
import base64
import json
import logging
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import httpx
from github import Github
from github.GithubException import GithubException

from ..core.manager import ServiceInstance, ServiceType, ServiceStatus, ServiceMetrics

logger = logging.getLogger(__name__)


class GitHubMCPService:
    """GitHub MCP service implementation with repository management capabilities"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.service_instance: Optional[ServiceInstance] = None
        self.github_client: Optional[Github] = None
        self.server_process: Optional[subprocess.Popen] = None
        self.running = False
        
        # Configuration
        self.host = self.config.get('host', 'localhost')
        self.port = self.config.get('port', 8081)
        self.github_token = self.config.get('github_token', os.getenv('GITHUB_TOKEN'))
        self.server_script = self.config.get('server_script', self._get_default_server_script())
        
        # Initialize GitHub client
        if self.github_token:
            self.github_client = Github(self.github_token)
        
        # Initialize service instance
        self._init_service_instance()
    
    def _init_service_instance(self):
        """Initialize the service instance metadata"""
        self.service_instance = ServiceInstance(
            id=f"github-mcp-{self.port}",
            name="GitHub MCP Service",
            service_type=ServiceType.GITHUB,
            host=self.host,
            port=self.port,
            path="/",
            protocol="http",
            description="GitHub repository management and Git operations service",
            version="1.0.0",
            tags={"git", "github", "repository", "vcs"},
            metadata={
                "github_token_configured": bool(self.github_token),
                "supported_operations": [
                    "repository_management",
                    "file_operations",
                    "branch_operations",
                    "pull_requests",
                    "issues",
                    "releases"
                ]
            },
            health_check_url=f"http://{self.host}:{self.port}/health"
        )
    
    def _get_default_server_script(self) -> str:
        """Get the default GitHub MCP server script"""
        return '''
#!/usr/bin/env python3
"""
GitHub MCP Server
Provides GitHub repository management capabilities via MCP protocol
"""

import asyncio
import base64
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from github import Github
from github.GithubException import GithubException
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GitHub MCP Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Global state
github_clients = {}  # Token-based client cache
service_metrics = {
    "requests_total": 0,
    "error_count": 0,
    "repositories_accessed": set(),
    "api_calls": 0,
    "start_time": datetime.now()
}

def get_github_client(token: str) -> Github:
    """Get or create GitHub client for token"""
    if token not in github_clients:
        github_clients[token] = Github(token)
    return github_clients[token]

def get_token_from_header(authorization: str = Header(None)) -> str:
    """Extract GitHub token from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="GitHub token required")
    
    if authorization.startswith("Bearer "):
        return authorization[7:]
    elif authorization.startswith("token "):
        return authorization[6:]
    else:
        return authorization

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    uptime = (datetime.now() - service_metrics["start_time"]).total_seconds()
    return {
        "status": "healthy",
        "service": "github-mcp",
        "version": "1.0.0",
        "uptime": uptime,
        "metrics": {
            **service_metrics,
            "repositories_accessed": len(service_metrics["repositories_accessed"])
        }
    }

@app.get("/mcp/info")
async def mcp_info():
    """MCP service information"""
    return {
        "id": "github-mcp",
        "name": "GitHub MCP Service",
        "type": "github",
        "version": "1.0.0",
        "description": "GitHub repository management and operations service",
        "capabilities": [
            "repository_management",
            "file_operations",
            "branch_operations",
            "pull_requests",
            "issues",
            "releases",
            "search",
            "webhooks"
        ]
    }

# Repository Operations

@app.get("/repos/{owner}/{repo}")
async def get_repository(owner: str, repo: str, token: str = Depends(get_token_from_header)):
    """Get repository information"""
    service_metrics["requests_total"] += 1
    service_metrics["api_calls"] += 1
    
    try:
        github = get_github_client(token)
        repository = github.get_repo(f"{owner}/{repo}")
        service_metrics["repositories_accessed"].add(f"{owner}/{repo}")
        
        return {
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
            "html_url": repository.html_url
        }
    except GithubException as e:
        service_metrics["error_count"] += 1
        logger.error(f"GitHub API error: {e}")
        raise HTTPException(status_code=e.status, detail=str(e))
    except Exception as e:
        service_metrics["error_count"] += 1
        logger.error(f"Error getting repository: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/repos/{owner}/{repo}/contents/{path:path}")
async def get_file_content(owner: str, repo: str, path: str, ref: str = None, token: str = Depends(get_token_from_header)):
    """Get file content from repository"""
    service_metrics["requests_total"] += 1
    service_metrics["api_calls"] += 1
    
    try:
        github = get_github_client(token)
        repository = github.get_repo(f"{owner}/{repo}")
        service_metrics["repositories_accessed"].add(f"{owner}/{repo}")
        
        content = repository.get_contents(path, ref=ref)
        
        if content.type == "file":
            # Decode base64 content
            file_content = base64.b64decode(content.content).decode('utf-8')
            
            return {
                "name": content.name,
                "path": content.path,
                "type": content.type,
                "size": content.size,
                "sha": content.sha,
                "content": file_content,
                "encoding": content.encoding,
                "download_url": content.download_url,
                "html_url": content.html_url
            }
        else:
            # Directory listing
            return {
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
                        "sha": item.sha
                    }
                    for item in content
                ]
            }
    except GithubException as e:
        service_metrics["error_count"] += 1
        logger.error(f"GitHub API error: {e}")
        raise HTTPException(status_code=e.status, detail=str(e))
    except Exception as e:
        service_metrics["error_count"] += 1
        logger.error(f"Error getting file content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/repos/{owner}/{repo}/contents/{path:path}")
async def create_or_update_file(
    owner: str, 
    repo: str, 
    path: str, 
    content_data: Dict[str, Any],
    token: str = Depends(get_token_from_header)
):
    """Create or update file in repository"""
    service_metrics["requests_total"] += 1
    service_metrics["api_calls"] += 1
    
    try:
        github = get_github_client(token)
        repository = github.get_repo(f"{owner}/{repo}")
        service_metrics["repositories_accessed"].add(f"{owner}/{repo}")
        
        # Encode content to base64
        content = base64.b64encode(content_data["content"].encode()).decode()
        
        # Check if file exists to get SHA
        sha = None
        try:
            existing_file = repository.get_contents(path)
            sha = existing_file.sha
        except GithubException:
            pass  # File doesn't exist
        
        # Create or update file
        result = repository.create_file(
            path=path,
            message=content_data.get("message", f"Update {path}"),
            content=content,
            sha=sha,
            branch=content_data.get("branch")
        )
        
        return {
            "commit": {
                "sha": result["commit"].sha,
                "message": result["commit"].commit.message,
                "author": result["commit"].commit.author.name,
                "date": result["commit"].commit.author.date.isoformat()
            },
            "content": {
                "name": result["content"].name,
                "path": result["content"].path,
                "sha": result["content"].sha,
                "size": result["content"].size
            }
        }
    except GithubException as e:
        service_metrics["error_count"] += 1
        logger.error(f"GitHub API error: {e}")
        raise HTTPException(status_code=e.status, detail=str(e))
    except Exception as e:
        service_metrics["error_count"] += 1
        logger.error(f"Error creating/updating file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/repos/{owner}/{repo}/contents/{path:path}")
async def delete_file(
    owner: str, 
    repo: str, 
    path: str, 
    delete_data: Dict[str, Any],
    token: str = Depends(get_token_from_header)
):
    """Delete file from repository"""
    service_metrics["requests_total"] += 1
    service_metrics["api_calls"] += 1
    
    try:
        github = get_github_client(token)
        repository = github.get_repo(f"{owner}/{repo}")
        service_metrics["repositories_accessed"].add(f"{owner}/{repo}")
        
        # Get file to get SHA
        file_content = repository.get_contents(path)
        
        # Delete file
        result = repository.delete_file(
            path=path,
            message=delete_data.get("message", f"Delete {path}"),
            sha=file_content.sha,
            branch=delete_data.get("branch")
        )
        
        return {
            "commit": {
                "sha": result["commit"].sha,
                "message": result["commit"].commit.message,
                "author": result["commit"].commit.author.name,
                "date": result["commit"].commit.author.date.isoformat()
            }
        }
    except GithubException as e:
        service_metrics["error_count"] += 1
        logger.error(f"GitHub API error: {e}")
        raise HTTPException(status_code=e.status, detail=str(e))
    except Exception as e:
        service_metrics["error_count"] += 1
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Branch Operations

@app.get("/repos/{owner}/{repo}/branches")
async def list_branches(owner: str, repo: str, token: str = Depends(get_token_from_header)):
    """List repository branches"""
    service_metrics["requests_total"] += 1
    service_metrics["api_calls"] += 1
    
    try:
        github = get_github_client(token)
        repository = github.get_repo(f"{owner}/{repo}")
        service_metrics["repositories_accessed"].add(f"{owner}/{repo}")
        
        branches = repository.get_branches()
        
        return {
            "branches": [
                {
                    "name": branch.name,
                    "commit": {
                        "sha": branch.commit.sha,
                        "url": branch.commit.url
                    },
                    "protected": branch.protected
                }
                for branch in branches
            ]
        }
    except GithubException as e:
        service_metrics["error_count"] += 1
        logger.error(f"GitHub API error: {e}")
        raise HTTPException(status_code=e.status, detail=str(e))
    except Exception as e:
        service_metrics["error_count"] += 1
        logger.error(f"Error listing branches: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/repos/{owner}/{repo}/branches")
async def create_branch(
    owner: str, 
    repo: str, 
    branch_data: Dict[str, Any],
    token: str = Depends(get_token_from_header)
):
    """Create a new branch"""
    service_metrics["requests_total"] += 1
    service_metrics["api_calls"] += 1
    
    try:
        github = get_github_client(token)
        repository = github.get_repo(f"{owner}/{repo}")
        service_metrics["repositories_accessed"].add(f"{owner}/{repo}")
        
        # Get source branch commit
        source_branch = repository.get_branch(branch_data.get("from_branch", repository.default_branch))
        
        # Create reference for new branch
        ref = repository.create_git_ref(
            ref=f"refs/heads/{branch_data['name']}",
            sha=source_branch.commit.sha
        )
        
        return {
            "name": branch_data['name'],
            "ref": ref.ref,
            "sha": ref.object.sha,
            "url": ref.url
        }
    except GithubException as e:
        service_metrics["error_count"] += 1
        logger.error(f"GitHub API error: {e}")
        raise HTTPException(status_code=e.status, detail=str(e))
    except Exception as e:
        service_metrics["error_count"] += 1
        logger.error(f"Error creating branch: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Pull Request Operations

@app.get("/repos/{owner}/{repo}/pulls")
async def list_pull_requests(
    owner: str, 
    repo: str, 
    state: str = "open",
    token: str = Depends(get_token_from_header)
):
    """List pull requests"""
    service_metrics["requests_total"] += 1
    service_metrics["api_calls"] += 1
    
    try:
        github = get_github_client(token)
        repository = github.get_repo(f"{owner}/{repo}")
        service_metrics["repositories_accessed"].add(f"{owner}/{repo}")
        
        pulls = repository.get_pulls(state=state)
        
        return {
            "pull_requests": [
                {
                    "number": pr.number,
                    "title": pr.title,
                    "body": pr.body,
                    "state": pr.state,
                    "created_at": pr.created_at.isoformat(),
                    "updated_at": pr.updated_at.isoformat(),
                    "user": pr.user.login,
                    "head": {
                        "ref": pr.head.ref,
                        "sha": pr.head.sha,
                        "repo": pr.head.repo.full_name if pr.head.repo else None
                    },
                    "base": {
                        "ref": pr.base.ref,
                        "sha": pr.base.sha,
                        "repo": pr.base.repo.full_name
                    },
                    "mergeable": pr.mergeable,
                    "draft": pr.draft,
                    "html_url": pr.html_url
                }
                for pr in pulls[:50]  # Limit to 50 results
            ]
        }
    except GithubException as e:
        service_metrics["error_count"] += 1
        logger.error(f"GitHub API error: {e}")
        raise HTTPException(status_code=e.status, detail=str(e))
    except Exception as e:
        service_metrics["error_count"] += 1
        logger.error(f"Error listing pull requests: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/repos/{owner}/{repo}/pulls")
async def create_pull_request(
    owner: str, 
    repo: str, 
    pr_data: Dict[str, Any],
    token: str = Depends(get_token_from_header)
):
    """Create a pull request"""
    service_metrics["requests_total"] += 1
    service_metrics["api_calls"] += 1
    
    try:
        github = get_github_client(token)
        repository = github.get_repo(f"{owner}/{repo}")
        service_metrics["repositories_accessed"].add(f"{owner}/{repo}")
        
        pr = repository.create_pull(
            title=pr_data["title"],
            body=pr_data.get("body", ""),
            head=pr_data["head"],
            base=pr_data["base"],
            draft=pr_data.get("draft", False)
        )
        
        return {
            "number": pr.number,
            "title": pr.title,
            "body": pr.body,
            "state": pr.state,
            "created_at": pr.created_at.isoformat(),
            "user": pr.user.login,
            "head": {
                "ref": pr.head.ref,
                "sha": pr.head.sha
            },
            "base": {
                "ref": pr.base.ref,
                "sha": pr.base.sha
            },
            "html_url": pr.html_url,
            "url": pr.url
        }
    except GithubException as e:
        service_metrics["error_count"] += 1
        logger.error(f"GitHub API error: {e}")
        raise HTTPException(status_code=e.status, detail=str(e))
    except Exception as e:
        service_metrics["error_count"] += 1
        logger.error(f"Error creating pull request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Issue Operations

@app.get("/repos/{owner}/{repo}/issues")
async def list_issues(
    owner: str, 
    repo: str, 
    state: str = "open",
    token: str = Depends(get_token_from_header)
):
    """List repository issues"""
    service_metrics["requests_total"] += 1
    service_metrics["api_calls"] += 1
    
    try:
        github = get_github_client(token)
        repository = github.get_repo(f"{owner}/{repo}")
        service_metrics["repositories_accessed"].add(f"{owner}/{repo}")
        
        issues = repository.get_issues(state=state)
        
        return {
            "issues": [
                {
                    "number": issue.number,
                    "title": issue.title,
                    "body": issue.body,
                    "state": issue.state,
                    "created_at": issue.created_at.isoformat(),
                    "updated_at": issue.updated_at.isoformat(),
                    "user": issue.user.login,
                    "assignee": issue.assignee.login if issue.assignee else None,
                    "labels": [label.name for label in issue.labels],
                    "comments": issue.comments,
                    "html_url": issue.html_url
                }
                for issue in issues[:50]  # Limit to 50 results
            ]
        }
    except GithubException as e:
        service_metrics["error_count"] += 1
        logger.error(f"GitHub API error: {e}")
        raise HTTPException(status_code=e.status, detail=str(e))
    except Exception as e:
        service_metrics["error_count"] += 1
        logger.error(f"Error listing issues: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/repos/{owner}/{repo}/issues")
async def create_issue(
    owner: str, 
    repo: str, 
    issue_data: Dict[str, Any],
    token: str = Depends(get_token_from_header)
):
    """Create a new issue"""
    service_metrics["requests_total"] += 1
    service_metrics["api_calls"] += 1
    
    try:
        github = get_github_client(token)
        repository = github.get_repo(f"{owner}/{repo}")
        service_metrics["repositories_accessed"].add(f"{owner}/{repo}")
        
        issue = repository.create_issue(
            title=issue_data["title"],
            body=issue_data.get("body", ""),
            assignee=issue_data.get("assignee"),
            labels=issue_data.get("labels", [])
        )
        
        return {
            "number": issue.number,
            "title": issue.title,
            "body": issue.body,
            "state": issue.state,
            "created_at": issue.created_at.isoformat(),
            "user": issue.user.login,
            "assignee": issue.assignee.login if issue.assignee else None,
            "labels": [label.name for label in issue.labels],
            "html_url": issue.html_url,
            "url": issue.url
        }
    except GithubException as e:
        service_metrics["error_count"] += 1
        logger.error(f"GitHub API error: {e}")
        raise HTTPException(status_code=e.status, detail=str(e))
    except Exception as e:
        service_metrics["error_count"] += 1
        logger.error(f"Error creating issue: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Search Operations

@app.get("/search/repositories")
async def search_repositories(q: str, sort: str = None, order: str = "desc", token: str = Depends(get_token_from_header)):
    """Search repositories"""
    service_metrics["requests_total"] += 1
    service_metrics["api_calls"] += 1
    
    try:
        github = get_github_client(token)
        
        results = github.search_repositories(query=q, sort=sort, order=order)
        
        return {
            "total_count": results.totalCount,
            "repositories": [
                {
                    "id": repo.id,
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "private": repo.private,
                    "stargazers_count": repo.stargazers_count,
                    "language": repo.language,
                    "forks_count": repo.forks_count,
                    "created_at": repo.created_at.isoformat(),
                    "updated_at": repo.updated_at.isoformat(),
                    "html_url": repo.html_url,
                    "clone_url": repo.clone_url
                }
                for repo in results[:20]  # Limit to 20 results
            ]
        }
    except GithubException as e:
        service_metrics["error_count"] += 1
        logger.error(f"GitHub API error: {e}")
        raise HTTPException(status_code=e.status, detail=str(e))
    except Exception as e:
        service_metrics["error_count"] += 1
        logger.error(f"Error searching repositories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8081
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
'''
    
    async def start(self) -> bool:
        """Start the GitHub MCP service"""
        if self.running:
            logger.warning("GitHub MCP service is already running")
            return True
        
        try:
            logger.info(f"Starting GitHub MCP service on {self.host}:{self.port}")
            
            # Create server script if it doesn't exist
            server_script_path = Path("github_mcp_server.py")
            if not server_script_path.exists():
                with open(server_script_path, 'w') as f:
                    f.write(self.server_script)
            
            # Start the server process
            self.server_process = subprocess.Popen([
                "python", str(server_script_path), str(self.port)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            await asyncio.sleep(3)
            
            # Check if server is running
            if await self._check_server_health():
                self.running = True
                self.service_instance.status = ServiceStatus.RUNNING
                logger.info("GitHub MCP service started successfully")
                return True
            else:
                logger.error("GitHub MCP service failed to start properly")
                await self.stop()
                return False
                
        except Exception as e:
            logger.error(f"Failed to start GitHub MCP service: {e}")
            self.service_instance.status = ServiceStatus.ERROR
            return False
    
    async def stop(self) -> bool:
        """Stop the GitHub MCP service"""
        if not self.running:
            logger.warning("GitHub MCP service is not running")
            return True
        
        try:
            logger.info("Stopping GitHub MCP service")
            
            # Terminate server process
            if self.server_process:
                self.server_process.terminate()
                try:
                    self.server_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.server_process.kill()
                    self.server_process.wait()
                self.server_process = None
            
            self.running = False
            self.service_instance.status = ServiceStatus.STOPPED
            logger.info("GitHub MCP service stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop GitHub MCP service: {e}")
            return False
    
    async def restart(self) -> bool:
        """Restart the GitHub MCP service"""
        logger.info("Restarting GitHub MCP service")
        await self.stop()
        await asyncio.sleep(2)
        return await self.start()
    
    async def _check_server_health(self) -> bool:
        """Check if the server is healthy"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"http://{self.host}:{self.port}/health")
                return response.status_code == 200
        except:
            return False
    
    async def get_metrics(self) -> ServiceMetrics:
        """Get service metrics"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"http://{self.host}:{self.port}/health")
                if response.status_code == 200:
                    health_data = response.json()
                    metrics_data = health_data.get("metrics", {})
                    
                    # Update service metrics
                    self.service_instance.metrics.requests_total = metrics_data.get("requests_total", 0)
                    self.service_instance.metrics.error_count = metrics_data.get("error_count", 0)
                    self.service_instance.metrics.uptime = health_data.get("uptime", 0)
                    
                    return self.service_instance.metrics
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
        
        return self.service_instance.metrics
    
    def get_service_instance(self) -> ServiceInstance:
        """Get the service instance"""
        return self.service_instance
    
    # High-level GitHub operations
    
    async def get_repository_info(self, owner: str, repo: str, token: str = None) -> Dict[str, Any]:
        """Get repository information"""
        try:
            headers = {}
            if token or self.github_token:
                headers["Authorization"] = f"token {token or self.github_token}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://{self.host}:{self.port}/repos/{owner}/{repo}",
                    headers=headers
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to get repository info: {e}")
            raise
    
    async def get_file_content(self, owner: str, repo: str, path: str, ref: str = None, token: str = None) -> Dict[str, Any]:
        """Get file content from repository"""
        try:
            headers = {}
            if token or self.github_token:
                headers["Authorization"] = f"token {token or self.github_token}"
            
            params = {}
            if ref:
                params["ref"] = ref
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://{self.host}:{self.port}/repos/{owner}/{repo}/contents/{path}",
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to get file content: {e}")
            raise
    
    async def create_or_update_file(self, owner: str, repo: str, path: str, content: str, message: str, token: str = None, branch: str = None) -> Dict[str, Any]:
        """Create or update file in repository"""
        try:
            headers = {}
            if token or self.github_token:
                headers["Authorization"] = f"token {token or self.github_token}"
            
            data = {
                "content": content,
                "message": message
            }
            if branch:
                data["branch"] = branch
            
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"http://{self.host}:{self.port}/repos/{owner}/{repo}/contents/{path}",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to create/update file: {e}")
            raise
    
    async def create_pull_request(self, owner: str, repo: str, title: str, head: str, base: str, body: str = "", token: str = None) -> Dict[str, Any]:
        """Create a pull request"""
        try:
            headers = {}
            if token or self.github_token:
                headers["Authorization"] = f"token {token or self.github_token}"
            
            data = {
                "title": title,
                "head": head,
                "base": base,
                "body": body
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://{self.host}:{self.port}/repos/{owner}/{repo}/pulls",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to create pull request: {e}")
            raise
    
    async def search_repositories(self, query: str, sort: str = None, token: str = None) -> Dict[str, Any]:
        """Search repositories"""
        try:
            headers = {}
            if token or self.github_token:
                headers["Authorization"] = f"token {token or self.github_token}"
            
            params = {"q": query}
            if sort:
                params["sort"] = sort
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://{self.host}:{self.port}/search/repositories",
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to search repositories: {e}")
            raise


# Factory function for creating GitHub service instances
def create_github_service(config: Dict[str, Any] = None) -> GitHubMCPService:
    """Create a new GitHub MCP service instance"""
    return GitHubMCPService(config)


# Example usage and testing
if __name__ == "__main__":
    async def test_github_service():
        """Test the GitHub MCP service"""
        service = create_github_service({
            "host": "localhost",
            "port": 8081,
            "github_token": os.getenv("GITHUB_TOKEN")
        })
        
        # Start service
        started = await service.start()
        if not started:
            print("Failed to start service")
            return
        
        print("Service started successfully")
        
        try:
            # Wait a bit for service to be ready
            await asyncio.sleep(2)
            
            # Test repository info
            repo_info = await service.get_repository_info("octocat", "Hello-World")
            print(f"Repository info: {repo_info['name']} - {repo_info['description']}")
            
            # Test search
            search_results = await service.search_repositories("python machine learning")
            print(f"Search found {search_results['total_count']} repositories")
            
        except Exception as e:
            print(f"Test error: {e}")
        finally:
            # Stop service
            await service.stop()
            print("Service stopped")
    
    # Run the test
    asyncio.run(test_github_service())