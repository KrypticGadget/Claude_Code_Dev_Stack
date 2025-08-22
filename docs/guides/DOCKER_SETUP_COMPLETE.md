# Claude Code Dev Stack V3.6.9 - Complete Docker Environment

## 🐳 Complete 11-Service Architecture

This Docker setup provides a comprehensive development environment with 11 optimized services:

### Core Services (4)
1. **PostgreSQL Database** - Optimized for performance with connection pooling
2. **Redis Cache** - Persistent caching with advanced memory management  
3. **Main Application** - Claude Code Dev Stack with agent orchestration
4. **Semantic API** - AI-powered semantic analysis service

### Infrastructure Services (3)
5. **NGROK Tunnel** - External access and webhook handling
6. **Traefik Load Balancer** - Modern reverse proxy with service discovery
7. **Consul Service Discovery** - Dynamic service registration and health checking

### Monitoring Services (2)
8. **Prometheus** - Metrics collection and alerting
9. **Grafana** - Visual monitoring dashboards and analytics

### Development Services (2)
10. **Development Containers** - Tier-specific development environments
11. **Health Check Service** - Comprehensive system monitoring

## 🚀 Quick Start

### 1. Prerequisites
```bash
# Ensure Docker and Docker Compose are installed
docker --version
docker-compose --version
```

### 2. Development Setup
```bash
# Make management script executable
chmod +x docker-manage.sh

# Start development environment
./docker-manage.sh dev-setup
```

### 3. Testing Setup
```bash
# Start testing environment
./docker-manage.sh test-setup
```

### 4. Production Setup
```bash
# Start all production services
./docker-manage.sh start
```

## 📋 Service Overview

### Database Layer
- **PostgreSQL 15**: Production-ready with optimized settings
  - Connection pooling (200 max connections)
  - Performance tuning for SSD storage
  - Automated backup and monitoring
  - Multiple databases for different components

- **Redis 7**: Advanced caching and session management
  - Persistent storage with AOF and RDB
  - Memory optimization (512MB limit)
  - Keyspace notifications for cache invalidation
  - Multi-threading for improved performance

### Application Layer  
- **Claude Dev Stack**: Main application with 28 agents
  - Hot reloading for development
  - Comprehensive health checks
  - Agent orchestration and routing
  - Real-time WebSocket connections

- **Semantic API**: AI-powered code analysis
  - Isolated microservice architecture
  - Caching for performance optimization
  - RESTful API with OpenAPI documentation

### Infrastructure Layer
- **Traefik v3**: Modern load balancer and reverse proxy
  - Automatic service discovery via Consul
  - SSL/TLS termination with Let's Encrypt
  - Rate limiting and security middleware
  - Docker label-based configuration

- **Consul**: Service discovery and configuration management
  - Health checking and service registration
  - Key-value store for configuration
  - Web UI for service visualization
  - Integration with Traefik for dynamic routing

- **NGROK**: Secure tunneling for external access
  - Multiple tunnel endpoints for different services
  - HTTPS termination and custom subdomains
  - Webhook testing and development
  - Real-time tunnel status monitoring

### Monitoring Layer
- **Prometheus**: Metrics collection and alerting
  - Service discovery integration
  - Long-term storage (30 days retention)
  - Custom metrics from all services
  - Alert manager integration ready

- **Grafana**: Visualization and dashboards
  - Pre-configured dashboards for all services
  - Real-time metrics and alerting
  - User authentication and authorization
  - Export/import dashboard configurations

### Development Layer
- **Multi-tier Development Containers**:
  - Frontend development with hot reloading
  - Backend API development with debugging
  - Database development with test data
  - Isolated testing environments

- **Comprehensive Health Monitoring**:
  - Real-time service health checks
  - System resource monitoring
  - Automated alerting and notifications
  - Performance metrics collection

## 🛠 Management Commands

### Core Operations
```bash
# Start all services
./docker-manage.sh start

# Start with specific profile
./docker-manage.sh start dev-tools

# Stop all services
./docker-manage.sh stop

# Restart services
./docker-manage.sh restart

# Show service status
./docker-manage.sh status
```

### Development Operations
```bash
# Setup development environment
./docker-manage.sh dev-setup

# Setup testing environment  
./docker-manage.sh test-setup

# Setup monitoring dashboards
./docker-manage.sh monitoring-setup
```

### Maintenance Operations
```bash
# View logs for all services
./docker-manage.sh logs

# View logs for specific service
./docker-manage.sh logs postgres

# Create backup
./docker-manage.sh backup

# Restore from backup
./docker-manage.sh restore backup-file.tar.gz

# Update all services
./docker-manage.sh update

# Run health check
./docker-manage.sh health-check

# Clean up everything
./docker-manage.sh cleanup
```

## 🌐 Service Endpoints

### Main Application
- **Application**: http://localhost:3000
- **API**: http://localhost:3001  
- **UI/PWA**: http://localhost:5173
- **WebSocket**: ws://localhost:3000

### Infrastructure
- **Traefik Dashboard**: http://localhost:8080
- **Consul UI**: http://localhost:8500
- **NGROK Dashboard**: http://localhost:4040

### Monitoring
- **Grafana**: http://localhost:3030 (admin/admin)
- **Prometheus**: http://localhost:9090

### Databases
- **PostgreSQL**: localhost:5432 (claude/claude_dev_db)
- **Redis**: localhost:6379 (password: claude_dev_redis)

### Development Tools
- **Frontend Dev**: http://localhost:5173
- **Backend Dev**: http://localhost:3001
- **API Documentation**: http://localhost:3000/api/docs

## 🔒 Security Configuration

### Authentication
- JWT-based authentication for API access
- Session management with Redis
- RBAC (Role-Based Access Control) implementation
- OAuth integration ready

### Network Security
- Internal Docker network isolation
- Traefik security middleware
- Rate limiting and DDoS protection
- SSL/TLS encryption for external access

### Database Security
- Connection encryption
- User privilege separation
- Query logging and monitoring
- Backup encryption

## 📊 Performance Optimization

### Database Optimization
```sql
-- PostgreSQL optimizations applied:
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
```

### Redis Optimization
```conf
# Redis optimizations applied:
maxmemory 512mb
maxmemory-policy allkeys-lru
io-threads 4
hz 10
activerehashing yes
```

### Application Optimization
- Connection pooling for database access
- Redis caching for frequent queries
- Gzip compression for static assets
- CDN-ready static file serving

## 🧪 Testing Configuration

### Test Databases
- Unit tests: `claude_dev_test`
- Integration tests: `claude_test_integration`  
- E2E tests: `claude_test_e2e`

### Test Profiles
```bash
# Unit tests
./docker-manage.sh start testing
docker-compose run --rm test-env npm run test:unit

# Integration tests
docker-compose run --rm test-env npm run test:integration

# E2E tests  
docker-compose run --rm test-env npm run test:e2e

# Performance tests
docker-compose run --rm test-env npm run test:performance

# Security tests
docker-compose run --rm test-env npm run test:security
```

## 🔧 Configuration Files

### Generated Configuration Files
- `/config/postgres/postgresql.conf` - Database optimization
- `/config/postgres/pg_hba.conf` - Authentication rules
- `/config/postgres/init.sql` - Database initialization
- `/config/redis/redis.conf` - Cache configuration
- `/config/ngrok/ngrok.yml` - Tunnel configuration
- `/config/consul/consul.hcl` - Service discovery
- `/config/traefik/traefik.yml` - Load balancer config
- `/config/traefik/dynamic/services.yml` - Dynamic routing
- `/scripts/healthcheck.sh` - Health monitoring script

### Environment Variables
Configuration is managed through `.env` file:
```bash
# Database
POSTGRES_PASSWORD=secure_password
REDIS_PASSWORD=secure_password

# Monitoring  
GRAFANA_PASSWORD=admin_password

# External Services
NGROK_AUTHTOKEN=your_ngrok_token
MCP_GITHUB_TOKEN=your_github_token

# Security
JWT_SECRET=your_jwt_secret
SESSION_SECRET=your_session_secret
```

## 🚨 Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check what's using ports
   netstat -tulpn | grep :3000
   
   # Stop conflicting services
   sudo systemctl stop apache2 nginx
   ```

2. **Permission Issues**
   ```bash
   # Fix script permissions
   chmod +x docker-manage.sh scripts/healthcheck.sh
   
   # Fix data directory permissions
   sudo chown -R $USER:$USER data/
   ```

3. **Memory Issues**
   ```bash
   # Check available memory
   free -h
   
   # Reduce Redis memory limit in docker-compose.yml
   --maxmemory 256mb
   ```

4. **Service Health Issues**
   ```bash
   # Check service logs
   ./docker-manage.sh logs service-name
   
   # Run health check
   ./docker-manage.sh health-check
   
   # Restart unhealthy services
   docker-compose restart service-name
   ```

### Log Locations
- Application logs: `./logs/`
- Docker logs: `docker-compose logs service-name`
- Health check logs: `./logs/healthcheck.log`
- Database logs: PostgreSQL container logs
- Cache logs: Redis container logs

### Performance Monitoring
```bash
# Monitor resource usage
docker stats

# Check service health
./docker-manage.sh health-check

# View metrics in Grafana
open http://localhost:3030
```

## 🔄 Backup and Recovery

### Automated Backups
```bash
# Create backup
./docker-manage.sh backup

# Schedule daily backups (cron)
0 2 * * * /path/to/docker-manage.sh backup
```

### Disaster Recovery
```bash
# Restore from backup
./docker-manage.sh restore backup-20240120_140000.tar.gz

# Verify restoration
./docker-manage.sh health-check
```

## 📈 Scaling and Production

### Horizontal Scaling
- Multiple application instances behind Traefik
- Database read replicas with PostgreSQL streaming replication
- Redis Cluster for cache scaling
- Consul cluster for high availability

### Production Considerations
- Enable SSL/TLS with proper certificates
- Configure proper backup retention policies
- Set up external monitoring and alerting
- Implement log aggregation and analysis
- Enable security scanning and vulnerability management

---

## 🎯 Next Steps

1. **Start Development**: Run `./docker-manage.sh dev-setup`
2. **Configure NGROK**: Add your NGROK authtoken to `.env`
3. **Set up Monitoring**: Run `./docker-manage.sh monitoring-setup`
4. **Run Tests**: Use `./docker-manage.sh test-setup`
5. **Deploy to Production**: Configure production environment variables

This comprehensive Docker environment provides everything needed for Claude Code Dev Stack development, testing, and deployment! 🚀