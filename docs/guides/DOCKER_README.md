# Claude Code Dev Stack V3.0 - Docker Setup Guide

This guide covers the complete Docker setup for Claude Code Dev Stack V3.0, including all services, MCP servers, and monitoring components.

## 🚀 Quick Start

### Prerequisites

- Docker Engine 20.10.0+
- Docker Compose 2.0.0+
- Git
- 8GB+ RAM recommended
- 20GB+ disk space

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/KrypticGadget/Claude_Code_Dev_Stack.git
cd Claude_Code_Dev_Stack

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 2. Start Development Environment

```bash
# Make scripts executable
chmod +x docker-start.sh docker-stop.sh

# Start all services
./docker-start.sh
```

### 3. Access Services

- **Main Application**: http://localhost:3000
- **React UI**: http://localhost:5173
- **Semantic API**: http://localhost:3002
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3030 (admin/admin)

## 📋 Services Overview

### Core Services

| Service | Port | Description |
|---------|------|-------------|
| claude-dev-stack | 3000 | Main application server |
| claude-ui | 5173 | React PWA interface |
| semantic-api | 3002 | Code analysis API |
| nginx | 80/443 | Reverse proxy |

### MCP Servers

| Service | Port | Description |
|---------|------|-------------|
| github-mcp-server | 3333 | GitHub integration |
| code-sandbox-mcp | 3334 | Code execution sandbox |
| playwright-mcp | 3335 | Browser automation |

### Infrastructure Services

| Service | Port | Description |
|---------|------|-------------|
| postgres | 5432 | PostgreSQL database |
| redis | 6379 | Redis cache/sessions |
| prometheus | 9090 | Metrics collection |
| grafana | 3030 | Monitoring dashboards |

## 🔧 Configuration

### Environment Variables

Required variables in `.env`:

```bash
# Database passwords
POSTGRES_PASSWORD=your_secure_password
REDIS_PASSWORD=your_redis_password

# MCP configuration
MCP_GITHUB_TOKEN=your_github_token

# Monitoring
GRAFANA_PASSWORD=your_grafana_password

# Security
JWT_SECRET=your_jwt_secret_here
SESSION_SECRET=your_session_secret_here
```

### MCP Server Configuration

The MCP servers are configured to work with Claude Desktop. Update your Claude configuration:

```json
{
  "mcpServers": {
    "github": {
      "command": "node",
      "args": ["path/to/github-mcp-server/dist/index.js"],
      "env": {
        "GITHUB_TOKEN": "your_token_here"
      }
    },
    "code-sandbox": {
      "command": "node",
      "args": ["path/to/code-sandbox/server.js"]
    },
    "playwright": {
      "command": "node",
      "args": ["path/to/playwright/server.js"]
    }
  }
}
```

## 🐳 Docker Commands

### Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f claude-dev-stack

# Restart a service
docker-compose restart semantic-api

# Stop all services
docker-compose down
```

### Production

```bash
# Start production environment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale services
docker-compose up -d --scale claude-dev-stack=3

# Update services
docker-compose pull && docker-compose up -d
```

### Maintenance

```bash
# Stop and remove everything
./docker-stop.sh --force

# Remove only volumes (data loss!)
./docker-stop.sh --volumes

# Remove built images
./docker-stop.sh --images

# Clean up Docker system
docker system prune -a
```

## 📊 Monitoring

### Prometheus Metrics

Access Prometheus at http://localhost:9090

Key metrics to monitor:
- `claude_requests_total` - Total requests
- `claude_response_time` - Response times
- `claude_agent_executions` - Agent execution count
- `claude_mcp_requests` - MCP server requests

### Grafana Dashboards

Access Grafana at http://localhost:3030 (admin/admin)

Pre-configured dashboards:
- Claude Dev Stack Overview
- MCP Server Performance
- System Resources
- Application Performance

## 🔍 Troubleshooting

### Common Issues

**Port conflicts:**
```bash
# Check port usage
netstat -tulpn | grep :3000

# Stop conflicting services
sudo systemctl stop nginx
```

**Memory issues:**
```bash
# Check Docker memory usage
docker stats

# Increase Docker memory limit in Docker Desktop settings
```

**Permission issues:**
```bash
# Fix permissions
sudo chown -R $USER:$USER .
chmod +x scripts/*.sh
```

### Service Health Checks

```bash
# Check all services
docker-compose ps

# Test individual services
curl http://localhost:3000/health
curl http://localhost:3002/api/v1/health
curl http://localhost:3333/health
```

### Database Issues

```bash
# Reset PostgreSQL
docker-compose stop postgres
docker volume rm claude-dev-stack_postgres_data
docker-compose up -d postgres

# Reset Redis
docker-compose stop redis
docker volume rm claude-dev-stack_redis_data
docker-compose up -d redis
```

## 🔄 Updates and Maintenance

### Updating Services

```bash
# Pull latest images
docker-compose pull

# Rebuild custom images
docker-compose build --no-cache

# Restart with new images
docker-compose up -d
```

### Backup and Restore

```bash
# Backup databases
docker-compose exec postgres pg_dumpall -U claude > backup.sql
docker-compose exec redis redis-cli --rdb dump.rdb

# Restore databases
docker-compose exec -T postgres psql -U claude < backup.sql
docker-compose exec redis redis-cli --rdb dump.rdb
```

### Log Management

```bash
# View log sizes
docker system df

# Clean up logs
docker system prune --volumes

# Configure log rotation
# Edit /etc/docker/daemon.json:
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

## 🚀 Production Deployment

### SSL/TLS Setup

1. Obtain SSL certificates
2. Place certificates in `config/nginx/ssl/`
3. Update nginx configuration
4. Restart nginx service

### Scaling

```bash
# Scale main application
docker-compose up -d --scale claude-dev-stack=3

# Use external load balancer for production
# Configure DNS for claude-code.yourdomain.com
```

### Security Considerations

- Change default passwords
- Use secrets management for sensitive data
- Enable firewall rules
- Regular security updates
- Monitor access logs

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [MCP Server Specification](https://spec.modelcontextprotocol.io/)
- [Claude Code Dev Stack Documentation](./README.md)
- [Troubleshooting Guide](./docs/troubleshooting.md)

## 🆘 Support

For issues and questions:
- GitHub Issues: https://github.com/KrypticGadget/Claude_Code_Dev_Stack/issues
- Discord: https://discord.gg/claude-code
- Email: support@claude-code.dev