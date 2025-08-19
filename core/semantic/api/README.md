# Semantic Analysis API

A high-performance REST and WebSocket API server for semantic analysis operations. Built with Tree-sitter for robust multi-language support, offering real-time code analysis, pattern matching, and intelligent code discovery.

## 🚀 Features

- **Multi-Language Support**: 16+ programming languages with Tree-sitter integration
- **Real-Time Analysis**: WebSocket support for live code analysis and collaborative features
- **Advanced Search**: Cross-language semantic search with fuzzy matching and similarity detection
- **Pattern Matching**: AST-based pattern detection for code quality, security, and design patterns
- **Intelligent Caching**: Multi-level caching with LRU eviction and performance optimization
- **High Performance**: Optimized for speed with parallel processing and efficient indexing
- **RESTful API**: Comprehensive REST endpoints with OpenAPI documentation
- **Production Ready**: Docker support, monitoring, health checks, and scalability features

## 📋 Supported Languages

- TypeScript/JavaScript
- Python
- Rust
- Go
- Java
- C/C++
- C#
- PHP
- Ruby
- Kotlin
- Swift
- Bash/Shell
- JSON/YAML
- And more...

## 🛠 Installation

### Prerequisites

- Node.js 18+
- npm 8+
- Python 3.8+ (for Tree-sitter bindings)
- C++ compiler (for native modules)

### Local Development

```bash
# Clone the repository
git clone https://github.com/claude-code/semantic-api.git
cd semantic-api

# Install dependencies
npm install

# Build the project
npm run build

# Start development server with hot reload
npm run dev

# Start production server
npm start
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Development mode with hot reload
docker-compose --profile dev up -d

# Production mode with load balancer and monitoring
docker-compose --profile production up -d
```

## 🔧 Configuration

### Environment Variables

```bash
# Server Configuration
NODE_ENV=production
PORT=3001
HOST=0.0.0.0

# Features
ENABLE_WEBSOCKET=true
ENABLE_CACHING=true
ENABLE_RATE_LIMIT=true

# Cache Settings
MAX_CACHE_SIZE=1000
CACHE_TTL=1800000  # 30 minutes

# Rate Limiting
RATE_LIMIT_WINDOW=900000  # 15 minutes
RATE_LIMIT_MAX=1000

# CORS
CORS_ORIGINS=*
```

### Server Configuration

```typescript
import { SemanticAnalysisServer } from './server';

const server = new SemanticAnalysisServer({
  port: 3001,
  host: '0.0.0.0',
  enableWebSocket: true,
  enableCaching: true,
  enableRateLimit: true,
  maxCacheSize: 1000,
  rateLimitWindow: 15 * 60 * 1000, // 15 minutes
  rateLimitMax: 1000,
  corsOrigins: ['*']
});

await server.start();
```

## 📖 API Documentation

### Base URL

```
http://localhost:3001/api/v1
```

### Health Check

```bash
GET /health
```

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "uptime": { "seconds": 3600, "formatted": "1h 0m 0s" },
  "memory": { "rss": "150MB", "heapTotal": "120MB" }
}
```

### Code Analysis

#### Parse Source Code

```bash
POST /analysis/parse
Content-Type: application/json

{
  "code": "function hello(name: string): string { return `Hello, ${name}!`; }",
  "language": "typescript",
  "fileId": "example.ts",
  "includeRelationships": true,
  "includeDocumentation": true
}
```

#### Get AST

```bash
POST /analysis/ast
Content-Type: application/json

{
  "code": "class Example { constructor() {} }",
  "language": "typescript",
  "includePositions": true,
  "includeTypes": false
}
```

#### Complexity Analysis

```bash
POST /analysis/complexity
Content-Type: application/json

{
  "code": "function complex() { /* code */ }",
  "language": "javascript",
  "metrics": ["cyclomatic", "cognitive", "halstead"]
}
```

### Symbol Management

#### List Symbols

```bash
GET /symbols?language=typescript&kind=function&page=1&limit=50
```

#### Get Symbol Details

```bash
GET /symbols/{symbolId}?includeReferences=true&includeContext=true
```

#### Create Symbol

```bash
POST /symbols
Content-Type: application/json

{
  "name": "exampleFunction",
  "kind": "function",
  "language": "typescript",
  "fileId": "example.ts",
  "range": { "startLine": 1, "startCol": 0, "endLine": 5, "endCol": 1 },
  "signature": "function exampleFunction(): void",
  "documentation": "Example function",
  "visibility": "public"
}
```

### Semantic Search

#### Search Symbols

```bash
GET /search/symbols?q=function&type=fuzzy&language=typescript&limit=20
```

#### Advanced Search

```bash
POST /search/advanced
Content-Type: application/json

{
  "query": "authentication",
  "filters": {
    "languages": ["typescript", "javascript"],
    "kinds": ["function", "class"],
    "scope": "project"
  },
  "options": {
    "maxResults": 100,
    "crossLanguage": true,
    "includeReferences": true
  }
}
```

#### Cross-Language Search

```bash
GET /search/cross-language?q=hash&languages=python,javascript,rust
```

#### Similarity Search

```bash
GET /search/similar/{symbolId}?threshold=0.7&maxResults=10
```

### Pattern Matching

#### List Patterns

```bash
GET /patterns?type=anti-pattern&category=security&language=javascript
```

#### Find Pattern Matches

```bash
POST /patterns/match
Content-Type: application/json

{
  "code": "const query = 'SELECT * FROM users WHERE id = ' + userId;",
  "patterns": ["sql-injection"],
  "languages": ["javascript"],
  "options": {
    "includeContext": true,
    "includeSuggestions": true,
    "confidenceThreshold": 0.8
  }
}
```

#### Register Custom Pattern

```bash
POST /patterns
Content-Type: application/json

{
  "name": "Custom Security Pattern",
  "description": "Detects unsafe practices",
  "type": "anti-pattern",
  "languages": ["javascript", "typescript"],
  "definition": {
    "query": "(call_expression function: (identifier) @func arguments: (arguments (string) @arg))",
    "constraints": { "unsafeFunctions": ["eval", "exec"] }
  },
  "metadata": {
    "category": "security",
    "severity": "error",
    "tags": ["security", "injection"]
  }
}
```

### Language Support

#### List Supported Languages

```bash
GET /languages?enabled=true&includeMetadata=true
```

#### Get Language Details

```bash
GET /languages/typescript?includeParser=true&includeExamples=true
```

#### Detect Language

```bash
POST /languages/detect
Content-Type: application/json

{
  "code": "def hello(name):\n    return f'Hello, {name}!'",
  "filename": "example.py"
}
```

## 🔌 WebSocket API

### Connection

```javascript
const ws = new WebSocket('ws://localhost:3001/ws');

ws.onopen = () => {
  console.log('Connected to Semantic Analysis API');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};
```

### Real-Time Analysis

```javascript
// Subscribe to file analysis
ws.send(JSON.stringify({
  type: 'subscribe-analysis',
  payload: {
    fileId: 'example.ts',
    language: 'typescript',
    options: {
      realtime: true,
      includeRelationships: true,
      debounceMs: 300
    }
  }
}));

// Send incremental updates
ws.send(JSON.stringify({
  type: 'incremental-update',
  payload: {
    fileId: 'example.ts',
    changes: [
      {
        range: { startLine: 5, startCol: 0, endLine: 5, endCol: 0 },
        text: 'console.log("New line");'
      }
    ],
    language: 'typescript'
  }
}));
```

### Collaborative Features

```javascript
// Join collaboration session
ws.send(JSON.stringify({
  type: 'collaboration-join',
  payload: {
    projectId: 'my-project',
    userId: 'user123'
  }
}));

// Real-time symbol search
ws.send(JSON.stringify({
  type: 'search-symbols',
  payload: {
    query: 'function',
    options: { maxResults: 20 }
  }
}));
```

## 🎯 Use Cases

### Code Intelligence

```typescript
// Find all function definitions
const functions = await searchEngine.searchSymbols({
  text: '',
  filters: { symbolKind: ['function'] },
  options: { includeDefinitions: true }
});

// Get function complexity
const complexity = await analyzeComplexity({
  code: functionCode,
  language: 'typescript',
  metrics: ['cyclomatic', 'cognitive']
});
```

### Security Analysis

```typescript
// Detect SQL injection vulnerabilities
const vulnerabilities = await patternMatcher.findMatches({
  patterns: ['sql-injection', 'xss-vulnerability'],
  categories: ['security'],
  options: { includeSuggestions: true }
});
```

### Code Quality

```typescript
// Find code smells and anti-patterns
const codeSmells = await patternMatcher.findMatches({
  patterns: ['long-parameter-list', 'deeply-nested-code'],
  categories: ['code-quality'],
  options: { confidenceThreshold: 0.8 }
});
```

### Cross-Language Analysis

```typescript
// Find similar functions across languages
const similar = await searchEngine.searchCrossLanguage({
  text: 'hash function',
  filters: { language: ['python', 'javascript', 'rust'] },
  options: { crossLanguage: true }
});
```

## 🔍 Monitoring & Analytics

### Health Monitoring

```bash
# Basic health check
curl http://localhost:3001/api/v1/health

# Detailed health with component status
curl http://localhost:3001/api/v1/health/detailed

# Readiness check for load balancers
curl http://localhost:3001/api/v1/health/ready

# Performance metrics
curl http://localhost:3001/api/v1/health/metrics
```

### Analytics Dashboard

Access the monitoring dashboard at:
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090

### Performance Metrics

```bash
# Search analytics
GET /search/analytics?period=day&groupBy=language

# Pattern matching statistics
GET /patterns/stats?groupBy=category&period=week

# Language usage statistics
GET /languages/typescript/stats?period=month&includeUsage=true
```

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch
```

### Integration Tests

```bash
# Test API endpoints
npm run test:integration

# Test WebSocket functionality
npm run test:websocket

# Load testing
npm run test:load
```

### Example Test

```typescript
import request from 'supertest';
import { SemanticAnalysisServer } from '../server';

describe('Analysis API', () => {
  let server: SemanticAnalysisServer;

  beforeAll(async () => {
    server = new SemanticAnalysisServer({ port: 0 });
    await server.start();
  });

  afterAll(async () => {
    await server.stop();
  });

  it('should parse TypeScript code', async () => {
    const response = await request(server.app)
      .post('/api/v1/analysis/parse')
      .send({
        code: 'function hello(): string { return "Hello"; }',
        language: 'typescript'
      })
      .expect(200);

    expect(response.body.result.symbols).toHaveLength(1);
    expect(response.body.result.symbols[0].kind).toBe('function');
  });
});
```

## 🚀 Deployment

### Production Deployment

```bash
# Build production image
docker build -t semantic-api:latest .

# Run with Docker Compose
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Deploy to Kubernetes
kubectl apply -f k8s/
```

### Scaling

```yaml
# docker-compose.yml
services:
  semantic-api:
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
```

### Load Balancing

```nginx
# nginx.conf
upstream semantic_api {
    server semantic-api-1:3001;
    server semantic-api-2:3001;
    server semantic-api-3:3001;
}

server {
    listen 80;
    location / {
        proxy_pass http://semantic_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow TypeScript best practices
- Add tests for new features
- Update documentation
- Follow the existing code style
- Use semantic commit messages

### Adding Language Support

```typescript
// 1. Install Tree-sitter grammar
npm install tree-sitter-newlang

// 2. Create language definition
class NewLanguageDefinition implements LanguageDefinition {
  id(): LanguageId {
    return new LanguageId('newlang');
  }
  
  name(): string {
    return 'New Language';
  }
  
  extensions(): string[] {
    return ['nl', 'newlang'];
  }
  
  createParser(settings: any) {
    return new NewLanguageParser();
  }
}

// 3. Register with the registry
registerLanguage(new NewLanguageDefinition());
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Tree-sitter](https://tree-sitter.github.io/) for robust parsing infrastructure
- [Express.js](https://expressjs.com/) for the web framework
- [WebSocket](https://github.com/websockets/ws) for real-time communication
- The open-source community for language grammars and tools

## 📞 Support

- 📧 Email: support@claude-code.dev
- 🐛 Issues: [GitHub Issues](https://github.com/claude-code/semantic-api/issues)
- 📖 Documentation: [API Docs](https://semantic-api.claude-code.dev/docs)
- 💬 Community: [Discord](https://discord.gg/claude-code)

---

**Built with ❤️ by the Claude Code Dev Stack team**