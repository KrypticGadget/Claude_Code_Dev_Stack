# Backend Development Workflow Prompts

Use these prompts for specific backend development tasks with the Claude Code Agent System.

## API Design & Development

### RESTful API Design
```
> Use the backend-services agent to design RESTful API for [RESOURCE] with CRUD operations, pagination, filtering, and [AUTH METHOD]
```

### GraphQL Schema
```
> Use the backend-services agent to create GraphQL schema for [DOMAIN] with types, queries, mutations, and subscriptions
```

### API Versioning
```
> Use the backend-services agent to implement API versioning strategy for [SERVICE] with backward compatibility and deprecation plan
```

## Database Design

### Schema Design
```
> Use the database-architecture agent to design database schema for [DOMAIN] with proper normalization, indexes, and relationships
```

### Migration Strategy
```
> Use the database-architecture agent to create migration scripts for [CHANGE TYPE] with rollback procedures and zero-downtime deployment
```

### Query Optimization
```
> Use the database-architecture agent to optimize queries for [USE CASE] improving performance from [CURRENT] to [TARGET] response time
```

## Service Architecture

### Microservice Design
```
> Use the backend-services agent to design microservice for [DOMAIN] with API contracts, data ownership, and communication patterns
```

### Event-Driven Architecture
```
> Use the middleware-specialist agent to implement event-driven architecture using [MESSAGE BROKER] for [USE CASE]
```

### Service Mesh Setup
```
> Use the middleware-specialist agent to configure service mesh for [SERVICES] with load balancing, circuit breakers, and observability
```

## Authentication & Security

### Auth Implementation
```
> Use the security-architecture agent to implement authentication using [METHOD] with session management, token refresh, and MFA
```

### API Security
```
> Use the security-architecture agent to secure API endpoints with rate limiting, CORS, input validation, and [SECURITY STANDARD]
```

### Data Encryption
```
> Use the security-architecture agent to implement data encryption for [DATA TYPE] at rest and in transit with key management
```

## Integration Development

### Third-Party Integration
```
> Use the api-integration-specialist agent to integrate [SERVICE NAME] for [PURPOSE] with error handling and retry logic
```

### Webhook Implementation
```
> Use the api-integration-specialist agent to implement webhook system for [EVENTS] with signature verification and delivery guarantees
```

### Payment Gateway
```
> Use the api-integration-specialist agent to integrate [PAYMENT PROVIDER] with PCI compliance and fraud detection
```

## Performance & Scaling

### Caching Strategy
```
> Use the performance-optimization agent to implement caching for [DATA TYPE] using [CACHE SOLUTION] with invalidation strategy
```

### Load Testing
```
> Use the performance-optimization agent to load test [ENDPOINT/SERVICE] simulating [USER COUNT] concurrent users
```

### Auto-Scaling
```
> Use the devops-engineering agent to configure auto-scaling for [SERVICE] based on [METRICS] with min/max limits
```

## Data Processing

### Batch Processing
```
> Use the backend-services agent to implement batch processing for [JOB TYPE] handling [VOLUME] records with error recovery
```

### Stream Processing
```
> Use the middleware-specialist agent to setup stream processing for [DATA STREAM] using [TOOL] with [THROUGHPUT] events/sec
```

### ETL Pipeline
```
> Use the backend-services agent to create ETL pipeline extracting from [SOURCE], transforming [OPERATIONS], loading to [DESTINATION]
```

## Testing & Quality

### Unit Testing
```
> Use the testing-automation agent to write unit tests for [SERVICE/MODULE] with mocking, edge cases, and [COVERAGE]% coverage
```

### Integration Testing
```
> Use the testing-automation agent to create integration tests for [API/SERVICE] testing all endpoints and error scenarios
```

### Contract Testing
```
> Use the testing-automation agent to implement contract tests between [SERVICE A] and [SERVICE B] ensuring compatibility
```

## Deployment & Operations

### Docker Configuration
```
> Use the devops-engineering agent to containerize [APPLICATION] with multi-stage builds, security scanning, and optimization
```

### Kubernetes Deployment
```
> Use the devops-engineering agent to create Kubernetes manifests for [SERVICE] with configs, secrets, and health checks
```

### Monitoring Setup
```
> Use the devops-engineering agent to implement monitoring for [SERVICE] with metrics, logs, traces, and alerting rules
```

## Common Patterns

### Queue Implementation
```
> Use the middleware-specialist agent to implement message queue for [USE CASE] using [QUEUE SYSTEM] with dead letter handling
```

### Background Jobs
```
> Use the backend-services agent to create background job system for [TASK TYPE] with scheduling, retries, and monitoring
```

### File Upload
```
> Use the backend-services agent to implement file upload for [FILE TYPES] with validation, virus scanning, and [STORAGE]
```

### Search Implementation
```
> Use the backend-services agent to add search functionality using [Elasticsearch/Algolia] for [DATA TYPE] with faceting
```

## Variables to Replace:
- `[RESOURCE]` - User, product, order, etc.
- `[AUTH METHOD]` - JWT, OAuth, API key
- `[DOMAIN]` - Business domain area
- `[MESSAGE BROKER]` - RabbitMQ, Kafka, etc.
- `[SERVICE NAME]` - Stripe, Twilio, etc.
- `[CACHE SOLUTION]` - Redis, Memcached
- `[METRICS]` - CPU, memory, requests
- `[VOLUME]` - 1M, 10M records
- `[STORAGE]` - S3, local, CDN