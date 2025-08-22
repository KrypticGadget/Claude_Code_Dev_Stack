# Context Preservation System

A robust, enterprise-grade context preservation system for cross-agent context sharing with PostgreSQL backend, Redis caching, and real-time WebSocket support.

## 🚀 Features

### Core Features
- **Cross-Agent Context Sharing**: Store and retrieve context between agent executions
- **Session State Management**: Maintain context across Claude Code sessions
- **Context Versioning**: Track context evolution and enable rollback
- **Memory Management**: Efficient context storage and retrieval
- **Context Compression**: Optimize context size for performance
- **Context Search**: Find relevant context across sessions with full-text search
- **Context Analytics**: Track context usage patterns

### Technical Features
- **PostgreSQL Backend**: Persistent storage with ACID compliance
- **Redis Caching**: High-performance caching for frequently accessed context
- **REST API**: RESTful API for context operations
- **WebSocket Support**: Real-time context updates and notifications
- **Context Encryption**: Secure sensitive data with AES-256-GCM
- **Context Expiration**: Automatic cleanup of expired contexts
- **Batch Operations**: Efficient bulk context operations
- **Health Monitoring**: Comprehensive health checks and metrics

## 📋 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client API    │    │  WebSocket API  │    │  Management     │
│   (REST)        │    │  (Real-time)    │    │  Scripts        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                │
         ┌─────────────────────────────────────────────────────┐
         │              Context API Server                     │
         │  ┌─────────────────┐    ┌─────────────────────────┐ │
         │  │ Context Manager │    │    WebSocket Handler   │ │
         │  └─────────────────┘    └─────────────────────────┘ │
         └─────────────────────────────────────────────────────┘
                                │
         ┌──────────────────────────────────────────────────────┐
         │                  Storage Layer                       │
         │  ┌─────────────────┐    ┌─────────────────────────┐ │
         │  │   PostgreSQL    │    │        Redis            │ │
         │  │   (Primary)     │    │       (Cache)           │ │
         │  └─────────────────┘    └─────────────────────────┘ │
         └──────────────────────────────────────────────────────┘
```

## 🛠️ Installation

### Prerequisites
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (for containerized deployment)

### Quick Start

1. **Install dependencies**:
```bash
cd core/context
npm install
```

2. **Setup environment variables**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Setup database**:
```bash
npm run setup:db
```

4. **Start the system**:
```bash
npm start
```

### Docker Deployment

1. **Start with Docker Compose**:
```bash
docker-compose up -d context-api
```

2. **Or use the management script**:
```bash
node scripts/context/manage-context-system.js setup
```

## 🔧 Configuration

### Environment Variables

```bash
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=claude_dev_stack
POSTGRES_USER=claude
POSTGRES_PASSWORD=your_password

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your_redis_password

# API Configuration
CONTEXT_API_PORT=3100
CONTEXT_API_HOST=0.0.0.0

# Security Configuration
CONTEXT_ENCRYPTION_ENABLED=false
CONTEXT_ENCRYPTION_KEY=your_32_character_secret_key

# Feature Flags
DEBUG=false
LOG_LEVEL=info
```

### Configuration File

The system uses `config/context/context-config.yml` for detailed configuration:

```yaml
# Database settings
database:
  postgresql:
    pool:
      max: 20
      min: 2
  redis:
    cache:
      default_ttl: 3600

# Context management
context:
  storage:
    default_ttl: 86400  # 24 hours
  versioning:
    max_versions: 10
  compression:
    threshold: 1024  # bytes
```

## 📚 API Reference

### REST API Endpoints

#### Store Context
```http
POST /api/context/store
Content-Type: application/json

{
  "key": "agent-conversation-123",
  "data": {
    "messages": [...],
    "state": {...}
  },
  "options": {
    "sessionId": "session-456",
    "agentId": "agent-789",
    "ttl": 86400,
    "encrypt": false,
    "compress": true,
    "tags": ["conversation", "important"]
  }
}
```

#### Retrieve Context
```http
GET /api/context/get/agent-conversation-123
```

#### Update Context
```http
PUT /api/context/update/agent-conversation-123
Content-Type: application/json

{
  "data": {
    "messages": [...],
    "state": {...},
    "updated": true
  },
  "options": {
    "changeType": "append",
    "changedBy": "agent-789"
  }
}
```

#### Delete Context
```http
DELETE /api/context/delete/agent-conversation-123
```

#### Search Contexts
```http
POST /api/context/search
Content-Type: application/json

{
  "query": "conversation about API design",
  "options": {
    "sessionId": "session-456",
    "limit": 20,
    "offset": 0
  }
}
```

#### Get Analytics
```http
GET /api/context/analytics?sessionId=session-456&agentId=agent-789
```

### WebSocket API

Connect to `ws://localhost:3100/context-ws`

#### Subscribe to Context Updates
```json
{
  "type": "subscribe-context",
  "payload": {
    "key": "agent-conversation-123"
  }
}
```

#### Real-time Context Changes
```json
{
  "type": "context-updated",
  "payload": {
    "key": "agent-conversation-123",
    "version": 2,
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

## 💻 Usage Examples

### Client Library Usage

```javascript
const { ContextClient } = require('./context-client');

// Create client
const client = new ContextClient();
await client.initialize();

// Store context
await client.store('my-context', {
  data: 'important information',
  timestamp: Date.now()
}, {
  sessionId: 'session-123',
  agentId: 'agent-456',
  ttl: 3600  // 1 hour
});

// Retrieve context
const context = await client.get('my-context');
console.log(context.data);

// Subscribe to updates
client.subscribe('my-context');
client.on('contextChange', (data) => {
  console.log('Context updated:', data);
});

// Search contexts
const results = await client.search('important information');
console.log(results.results);
```

### Quick Functions

```javascript
const { storeContext, getContext } = require('./context-client');

// Quick store
await storeContext('quick-key', { message: 'Hello World' });

// Quick retrieve
const data = await getContext('quick-key');
```

### Agent Integration Example

```javascript
// In your agent code
const contextClient = require('../core/context/context-client');

class MyAgent {
  async processTask(input) {
    // Load previous context
    const context = await contextClient.getContext(`agent-${this.id}-state`);
    
    // Process with context
    const result = this.processWithContext(input, context?.data);
    
    // Store updated context
    await contextClient.updateContext(`agent-${this.id}-state`, {
      lastInput: input,
      lastResult: result,
      timestamp: Date.now()
    });
    
    return result;
  }
}
```

## 🧪 Testing

### Run Tests
```bash
# Unit tests
npm test

# Integration tests
npm run test:integration

# All tests with coverage
npm run test:coverage
```

### Test Configuration
```javascript
// Jest configuration in package.json
{
  "jest": {
    "testEnvironment": "node",
    "coverageDirectory": "coverage",
    "testMatch": ["**/tests/**/*.test.js"]
  }
}
```

## 📊 Monitoring & Analytics

### Health Check
```bash
curl http://localhost:3100/api/context/health
```

### System Statistics
```bash
curl http://localhost:3100/api/context/analytics
```

### Performance Monitoring
The system exposes Prometheus metrics at `/metrics`:

- `context_operations_total` - Total context operations
- `context_cache_hit_ratio` - Cache hit percentage
- `context_response_time` - Response time histogram
- `context_storage_size` - Storage usage metrics

## 🔒 Security

### Encryption
Enable encryption for sensitive contexts:

```javascript
await client.store('sensitive-key', secretData, {
  encrypt: true
});
```

### Rate Limiting
Built-in rate limiting (1000 requests per 15 minutes per IP).

### Access Control
Configure access control in `context-config.yml`:

```yaml
security:
  rate_limit:
    max_requests: 1000
    window_ms: 900000
```

## 🚀 Performance

### Optimization Features
- **Connection Pooling**: PostgreSQL connection pool (2-20 connections)
- **Redis Caching**: Aggressive caching for hot contexts
- **Compression**: Automatic compression for contexts > 1KB
- **Batch Operations**: Bulk context operations
- **Lazy Loading**: Context data loaded on demand

### Benchmarks
Run performance benchmarks:

```bash
npm run benchmark
```

Typical performance metrics:
- Context store: ~5ms (cached), ~15ms (database)
- Context retrieve: ~2ms (cached), ~10ms (database)
- Context search: ~20ms (full-text search)
- WebSocket latency: ~1ms

## 🔧 Management

### Management Script
Use the comprehensive management script:

```bash
# Complete system setup
node scripts/context/manage-context-system.js setup

# Start services
node scripts/context/manage-context-system.js start

# Check status
node scripts/context/manage-context-system.js status

# Show statistics
node scripts/context/manage-context-system.js stats

# Create backup
node scripts/context/manage-context-system.js backup

# Cleanup expired contexts
node scripts/context/manage-context-system.js cleanup
```

### Database Maintenance
```sql
-- Cleanup expired contexts
SELECT context_system.cleanup_expired_contexts();

-- Archive old versions
SELECT context_system.archive_old_versions(10);

-- Get system statistics
SELECT * FROM context_system.get_context_stats();
```

## 🔄 Backup & Recovery

### Automated Backups
Configure automated backups in `docker-services/context-preservation.yml`:

```yaml
context-backup:
  environment:
    - BACKUP_INTERVAL=6h
    - BACKUP_RETENTION=30d
```

### Manual Backup
```bash
# Create backup
node scripts/context/manage-context-system.js backup

# Restore from backup
node scripts/context/manage-context-system.js restore backup-file.sql
```

### Export/Import
```bash
# Export contexts
node scripts/context/manage-context-system.js export contexts.json

# Import contexts
node scripts/context/manage-context-system.js import contexts.json --overwrite
```

## 🐛 Troubleshooting

### Common Issues

#### Connection Issues
```bash
# Check service status
docker-compose ps

# Check logs
docker-compose logs context-api

# Test connectivity
curl http://localhost:3100/api/context/health
```

#### Database Issues
```bash
# Check PostgreSQL
docker exec postgres pg_isready

# Check schema
docker exec postgres psql -U claude -d claude_dev_stack -c "\dt context_system.*"
```

#### Redis Issues
```bash
# Check Redis
docker exec redis redis-cli ping

# Check memory usage
docker exec redis redis-cli info memory
```

### Debug Mode
Enable debug mode for detailed logging:

```bash
export DEBUG=true
export LOG_LEVEL=debug
```

## 📈 Scaling

### Horizontal Scaling
- Deploy multiple Context API instances behind a load balancer
- Use Redis Cluster for distributed caching
- Configure PostgreSQL read replicas

### Vertical Scaling
- Increase PostgreSQL connection pool size
- Allocate more memory to Redis
- Optimize database queries with proper indexing

### Performance Tuning
```yaml
# context-config.yml
production:
  caching:
    aggressive: true
    preload_hot_contexts: true
    memory_cache_size: "512mb"
  
  performance:
    connection_pooling: true
    query_optimization: true
    index_optimization: true
```

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone [repository-url]
cd core/context

# Install dependencies
npm install

# Run tests
npm test

# Start in development mode
npm run dev
```

### Code Style
- ESLint configuration: `.eslintrc.js`
- Prettier configuration: `package.json`
- Pre-commit hooks with Husky

### Testing Guidelines
- Write unit tests for all new features
- Include integration tests for API endpoints
- Maintain >80% code coverage

## 📄 License

MIT License - see LICENSE file for details.

## 📞 Support

- **Documentation**: [API Documentation](http://localhost:3100/api/context/docs)
- **Health Check**: [System Health](http://localhost:3100/api/context/health)
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

---

**Context Preservation System v1.0.0** - Built with ❤️ for the Claude Code Agent ecosystem.