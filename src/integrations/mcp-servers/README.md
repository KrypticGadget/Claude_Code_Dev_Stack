# GitHub MCP Server - Complete API Integration

A comprehensive GitHub integration server implementing the Model Context Protocol (MCP) with advanced features including real-time WebSocket communication, intelligent caching, rate limiting, and complete GitHub API coverage.

## 🚀 Features

### Core GitHub API Integration
- **Repository Management**: Full CRUD operations for repositories, files, and directories
- **Issue Management**: Create, update, comment on issues with full lifecycle support
- **Pull Request Operations**: Complete PR workflow including creation, review, merge, and comments
- **Branch & Tag Management**: Create, delete, and manage repository branches and tags
- **Search Integration**: Comprehensive search across repositories, code, issues, and users
- **Release Management**: Create and manage repository releases
- **Organization Support**: Access organization repositories, members, and settings

### Advanced Features
- **Real-time Events**: WebSocket streaming of repository events and notifications
- **Webhook Handling**: Secure webhook endpoint with signature verification and replay protection
- **Intelligent Caching**: Multi-tier caching with Redis support and intelligent TTL management
- **Rate Limiting**: Respect GitHub API limits with smart queuing and backoff strategies
- **Authentication**: Support for Personal Access Tokens, OAuth, and GitHub Apps
- **Error Recovery**: Automatic retry mechanisms with exponential backoff and circuit breakers
- **Health Monitoring**: Comprehensive health checks and performance metrics
- **Docker Support**: Production-ready containerization with Docker Compose

### Security & Compliance
- **Secure Authentication**: JWT tokens, OAuth flows, and GitHub App integration
- **Request Validation**: Input sanitization and schema validation
- **CORS Support**: Configurable cross-origin resource sharing
- **Audit Logging**: Comprehensive audit trails for all operations
- **Rate Limiting**: Per-user and global rate limiting with Redis backend

## 📋 Requirements

### System Requirements
- Python 3.8+
- 2GB RAM minimum (4GB recommended)
- Network access to GitHub API
- Optional: Redis for enhanced caching and rate limiting
- Optional: Docker for containerized deployment

### Python Dependencies
See `requirements.txt` for complete list. Key dependencies:
- `fastapi>=0.104.1` - Web framework
- `PyGithub>=1.59.1` - GitHub API client
- `websockets>=12.0` - WebSocket support
- `redis>=5.0.1` - Caching backend
- `httpx>=0.25.2` - HTTP client
- `uvicorn>=0.24.0` - ASGI server

## 🛠️ Installation

### Quick Start (Local Development)

1. **Clone and Setup**
   ```bash
   cd integrations/mcp-manager
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   # Copy configuration template
   cp github_mcp_config.yml.example github_mcp_config.yml
   
   # Set GitHub authentication
   export GITHUB_TOKEN="your_github_token_here"
   
   # Optional: Configure Redis
   export REDIS_HOST="localhost"
   export REDIS_PORT="6379"
   ```

3. **Start the Server**
   ```bash
   python start_github_mcp.py
   ```

### Docker Deployment

1. **Build and Start with Docker Compose**
   ```bash
   # Set environment variables
   echo "GITHUB_TOKEN=your_token_here" > .env
   echo "GITHUB_WEBHOOK_SECRET=your_webhook_secret" >> .env
   
   # Start all services
   docker-compose -f docker-compose.github-mcp.yml up -d
   
   # View logs
   docker-compose -f docker-compose.github-mcp.yml logs -f github-mcp
   ```

2. **Production Deployment with Monitoring**
   ```bash
   # Start with monitoring stack
   docker-compose -f docker-compose.github-mcp.yml --profile monitoring up -d
   
   # Access services:
   # - GitHub MCP: http://localhost:8081
   # - Prometheus: http://localhost:9090
   # - Grafana: http://localhost:3000 (admin/admin)
   ```

### Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests including:
- Deployment and Service configurations
- ConfigMaps and Secrets
- Ingress configuration
- HorizontalPodAutoscaler
- ServiceMonitor for Prometheus

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GITHUB_TOKEN` | Personal Access Token | - | Yes* |
| `GITHUB_APP_ID` | GitHub App ID | - | Yes* |
| `GITHUB_APP_PRIVATE_KEY` | GitHub App Private Key | - | Yes* |
| `GITHUB_WEBHOOK_SECRET` | Webhook secret for verification | - | No |
| `HOST` | Server host | localhost | No |
| `PORT` | Server port | 8081 | No |
| `REDIS_HOST` | Redis hostname | localhost | No |
| `REDIS_PORT` | Redis port | 6379 | No |
| `LOG_LEVEL` | Logging level | info | No |

*Either `GITHUB_TOKEN` or both `GITHUB_APP_ID` and `GITHUB_APP_PRIVATE_KEY` required.

### Configuration File

The `github_mcp_config.yml` file provides comprehensive configuration options:

```yaml
github_mcp:
  # Server Configuration
  host: "localhost"
  port: 8081
  log_level: "info"
  
  # Authentication
  github_token: null  # Set via environment
  
  # Rate Limiting
  rate_limit_requests_per_hour: 5000
  rate_limit_search_per_minute: 30
  
  # Caching (seconds)
  cache_ttl_repository: 600
  cache_ttl_file_content: 1800
  
  # Health Monitoring
  health_check_interval: 30
  restart_on_failure: true
  max_restart_attempts: 3
```

## 🔧 Usage

### REST API

#### Authentication
```bash
# Using Personal Access Token
curl -H "Authorization: token YOUR_GITHUB_TOKEN" \
     http://localhost:8081/repos/owner/repo

# Using JWT (after authentication)
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8081/repos/owner/repo
```

#### Repository Operations
```bash
# Get repository information
GET /repos/{owner}/{repo}

# Get file content
GET /repos/{owner}/{repo}/contents/{path}

# Create or update file
PUT /repos/{owner}/{repo}/contents/{path}
Content-Type: application/json
{
  "content": "base64_encoded_content",
  "message": "Commit message",
  "branch": "main"
}

# List branches
GET /repos/{owner}/{repo}/branches

# Create branch
POST /repos/{owner}/{repo}/branches
{
  "name": "new-feature",
  "from_branch": "main"
}
```

#### Pull Requests
```bash
# List pull requests
GET /repos/{owner}/{repo}/pulls?state=open

# Create pull request
POST /repos/{owner}/{repo}/pulls
{
  "title": "New feature",
  "head": "feature-branch",
  "base": "main",
  "body": "Description of changes"
}

# Merge pull request
PUT /repos/{owner}/{repo}/pulls/{number}/merge
{
  "commit_title": "Merge pull request",
  "merge_method": "merge"
}
```

#### Issues
```bash
# List issues
GET /repos/{owner}/{repo}/issues?state=open

# Create issue
POST /repos/{owner}/{repo}/issues
{
  "title": "Bug report",
  "body": "Issue description",
  "labels": ["bug", "high-priority"]
}

# Add comment to issue
POST /repos/{owner}/{repo}/issues/{number}/comments
{
  "body": "Comment text"
}
```

#### Search
```bash
# Search repositories
GET /search/repositories?q=javascript+language:javascript

# Search code
GET /search/code?q=function+repo:owner/repo

# Search issues
GET /search/issues?q=bug+label:critical
```

### WebSocket Integration

#### Connect to WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8081/ws/user123');

ws.onopen = function() {
    console.log('Connected to GitHub MCP WebSocket');
    
    // Subscribe to specific events
    ws.send(JSON.stringify({
        type: 'subscribe',
        events: ['repository_update', 'pr_update', 'issue_update']
    }));
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received event:', data);
    
    switch(data.type) {
        case 'repository_update':
            handleRepositoryUpdate(data.data);
            break;
        case 'pr_update':
            handlePullRequestUpdate(data.data);
            break;
        case 'issue_update':
            handleIssueUpdate(data.data);
            break;
    }
};
```

#### Event Types
- `repository_update` - Repository changes (push, star, fork)
- `pr_update` - Pull request events (opened, closed, merged)
- `issue_update` - Issue events (opened, closed, commented)
- `webhook_received` - Raw webhook events
- `rate_limit_warning` - Rate limit warnings
- `error` - Error notifications

### Webhook Setup

1. **Configure Webhook in GitHub Repository**
   - Go to Settings → Webhooks
   - Add webhook URL: `https://your-domain.com/webhooks/github`
   - Select events: Push, Pull Request, Issues, etc.
   - Set secret (matches `GITHUB_WEBHOOK_SECRET`)

2. **Webhook Events Supported**
   - `push` - Code pushes
   - `pull_request` - PR lifecycle events
   - `issues` - Issue lifecycle events
   - `issue_comment` - Issue and PR comments
   - `release` - Release events
   - `star` - Repository stars
   - `fork` - Repository forks

### Python Client Integration

```python
from github_mcp_integration import create_github_mcp_integration
import asyncio

async def example_usage():
    # Create integration
    integration = create_github_mcp_integration(
        config_file="github_mcp_config.yml"
    )
    
    # Start integration
    await integration.start()
    
    # Use the client
    client = integration.client
    
    # Get repository info
    repo = await client.get_repository("octocat", "Hello-World")
    print(f"Repository: {repo['name']} - {repo['description']}")
    
    # Search repositories
    results = await client.search_repositories("python machine learning")
    print(f"Found {results['total_count']} repositories")
    
    # Create an issue
    issue = await client.create_issue(
        "owner", "repo",
        title="API Enhancement Request",
        body="We need better error handling",
        labels=["enhancement"]
    )
    print(f"Created issue #{issue['number']}")
    
    # Add event handler
    async def handle_push_event(event):
        print(f"Push to {event.data['repository']}: {event.data['commits']} commits")
    
    integration.add_event_handler("repository_update", handle_push_event)
    
    # Keep running
    while integration.running:
        await asyncio.sleep(1)
```

## 📊 Monitoring & Metrics

### Health Endpoints
- `GET /health` - Service health status
- `GET /metrics` - Prometheus-compatible metrics
- `GET /mcp/info` - MCP service information

### Key Metrics
- Request rates and response times
- GitHub API call counts and rate limits
- Cache hit/miss ratios
- WebSocket connection counts
- Error rates and types
- Repository access patterns

### Logging
Structured logging with configurable levels:
- **DEBUG**: Detailed operation logs
- **INFO**: General service information
- **WARNING**: Non-critical issues
- **ERROR**: Service errors and failures

Log outputs:
- Console (stdout)
- File (`logs/github_mcp.log` with rotation)
- Optional: Fluentd/ELK stack integration

## 🔒 Security

### Authentication Methods
1. **Personal Access Token**
   - Simple token-based authentication
   - Suitable for personal use and development

2. **OAuth App**
   - Full OAuth 2.0 flow implementation
   - User authorization with scopes

3. **GitHub App**
   - Installation-based authentication
   - Organization-wide access
   - Enhanced security and permissions

### Security Features
- JWT token validation
- Request signature verification (webhooks)
- Rate limiting per user/IP
- Input validation and sanitization
- CORS configuration
- Audit logging

### Best Practices
- Use environment variables for secrets
- Rotate tokens regularly
- Implement least privilege access
- Monitor for unusual activity
- Use HTTPS in production

## 🚀 Deployment

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GITHUB_TOKEN="your_token"

# Start development server
python start_github_mcp.py --debug
```

### Production Deployment

#### Docker (Recommended)
```bash
# Production build
docker build -f Dockerfile.github-mcp -t github-mcp:prod .

# Run with docker-compose
docker-compose -f docker-compose.github-mcp.yml up -d
```

#### Systemd Service
```bash
# Copy service file
sudo cp github-mcp.service /etc/systemd/system/

# Enable and start
sudo systemctl enable github-mcp
sudo systemctl start github-mcp
```

#### Kubernetes
```bash
# Apply manifests
kubectl apply -f k8s/

# Check status
kubectl get pods -l app=github-mcp
```

### Load Balancing
For high availability:
- Use multiple instances behind a load balancer
- Configure session affinity for WebSocket connections
- Implement health checks for load balancer
- Consider Redis cluster for shared cache

## 🔧 Development

### Project Structure
```
github-mcp/
├── github_mcp_server.py          # Main server implementation
├── github_mcp_service.py         # Service lifecycle management
├── github_mcp_integration.py     # Integration layer
├── start_github_mcp.py          # Startup script
├── github_mcp_config.yml        # Configuration file
├── requirements.txt             # Python dependencies
├── Dockerfile.github-mcp        # Docker image
├── docker-compose.github-mcp.yml # Docker Compose
├── docker-entrypoint.sh         # Docker entrypoint
└── README.md                    # This file
```

### Adding Features
1. **New API Endpoints**: Add to `github_mcp_server.py`
2. **Event Types**: Extend WebSocket event handling
3. **Authentication**: Modify auth methods in server
4. **Caching**: Extend cache strategies
5. **Monitoring**: Add new metrics collection

### Testing
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest tests/ -v --cov=github_mcp

# Integration tests
python start_github_mcp.py --validate-only
```

### Contributing
1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request

## 📚 API Reference

### Core Endpoints

#### Repository Operations
- `GET /repos/{owner}/{repo}` - Get repository
- `GET /repos/{owner}/{repo}/contents/{path}` - Get file/directory
- `PUT /repos/{owner}/{repo}/contents/{path}` - Create/update file
- `DELETE /repos/{owner}/{repo}/contents/{path}` - Delete file
- `GET /repos/{owner}/{repo}/commits` - List commits
- `POST /repos` - Create repository
- `DELETE /repos/{owner}/{repo}` - Delete repository

#### Branch Management
- `GET /repos/{owner}/{repo}/branches` - List branches
- `GET /repos/{owner}/{repo}/branches/{branch}` - Get branch
- `POST /repos/{owner}/{repo}/branches` - Create branch
- `DELETE /repos/{owner}/{repo}/branches/{branch}` - Delete branch

#### Pull Requests
- `GET /repos/{owner}/{repo}/pulls` - List pull requests
- `GET /repos/{owner}/{repo}/pulls/{number}` - Get pull request
- `POST /repos/{owner}/{repo}/pulls` - Create pull request
- `PATCH /repos/{owner}/{repo}/pulls/{number}` - Update pull request
- `PUT /repos/{owner}/{repo}/pulls/{number}/merge` - Merge pull request

#### Issues
- `GET /repos/{owner}/{repo}/issues` - List issues
- `GET /repos/{owner}/{repo}/issues/{number}` - Get issue
- `POST /repos/{owner}/{repo}/issues` - Create issue
- `PATCH /repos/{owner}/{repo}/issues/{number}` - Update issue

#### Search
- `GET /search/repositories` - Search repositories
- `GET /search/code` - Search code
- `GET /search/issues` - Search issues
- `GET /search/users` - Search users

#### Administration
- `GET /health` - Health check
- `GET /metrics` - Metrics
- `GET /mcp/info` - Service info
- `POST /auth/token` - Authenticate with token
- `POST /webhooks/github` - GitHub webhook endpoint
- `WS /ws/{user_id}` - WebSocket connection

## 🐛 Troubleshooting

### Common Issues

#### Authentication Errors
```
Error: Invalid token
Solution: Verify GITHUB_TOKEN is valid and has required scopes
```

#### Rate Limiting
```
Error: API rate limit exceeded
Solution: Implement request throttling or increase rate limits
```

#### WebSocket Connection Issues
```
Error: WebSocket connection failed
Solution: Check firewall settings and WebSocket proxy configuration
```

#### Cache Issues
```
Warning: Redis connection failed
Solution: Verify Redis is running and accessible
```

### Debug Mode
```bash
# Enable debug logging
python start_github_mcp.py --debug

# Check service status
curl http://localhost:8081/health

# Validate configuration
python start_github_mcp.py --validate-only
```

### Performance Tuning
- Adjust cache TTL values for your use case
- Configure Redis for better performance
- Tune rate limiting parameters
- Monitor resource usage and scale accordingly

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🤝 Support

- **Documentation**: See this README and inline code comments
- **Issues**: Open GitHub issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact maintainers for critical issues

## 🔄 Changelog

### Version 2.0.0
- Complete GitHub API integration
- Real-time WebSocket events
- Advanced caching with Redis
- Docker and Kubernetes support
- Comprehensive monitoring
- Security enhancements

### Version 1.0.0
- Initial release
- Basic GitHub API integration
- Simple authentication
- Basic error handling