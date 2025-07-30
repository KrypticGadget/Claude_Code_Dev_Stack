# New API Service Project Template

Use these prompts to start various types of API service projects with the Claude Code Agent System.

## RESTful API Service

```
> Use the master-orchestrator agent to begin new project: "RESTful API service for [DOMAIN] handling [OPERATIONS] with [AUTH METHOD] authentication. Expected [REQUESTS/SEC] with [SLA REQUIREMENT]."
```

## GraphQL API

```
> Use the master-orchestrator agent to begin new project: "GraphQL API for [APPLICATION TYPE] with real-time subscriptions, [DATA SOURCES] integration, and efficient query resolution for [USE CASES]."
```

## Microservices Architecture

```
> Use the master-orchestrator agent to begin new project: "Microservices architecture for [SYSTEM TYPE] with [NUMBER] services handling [DOMAINS]. Using [MESSAGE BROKER] for communication and [ORCHESTRATION METHOD]."
```

## Payment Processing API

```
> Use the master-orchestrator agent to begin new project: "Payment processing API supporting [PAYMENT METHODS] with PCI compliance, fraud detection, webhook notifications, and [PROVIDERS] integration."
```

## Data Integration API

```
> Use the master-orchestrator agent to begin new project: "Data integration API connecting [SOURCE SYSTEMS] with [DESTINATION SYSTEMS], handling [DATA VOLUME] with transformation, validation, and error recovery."
```

## Authentication Service

```
> Use the master-orchestrator agent to begin new project: "Authentication and authorization service with [AUTH METHODS], SSO support, MFA, session management, and integration with [IDENTITY PROVIDERS]."
```

## Webhook Service

```
> Use the master-orchestrator agent to begin new project: "Webhook delivery service for [EVENT TYPES] with retry logic, signature verification, event filtering, and delivery guarantees for [VOLUME] events/day."
```

## Real-time API

```
> Use the master-orchestrator agent to begin new project: "Real-time API using [WebSockets/SSE] for [USE CASE] supporting [CONCURRENT CONNECTIONS] with pub/sub, presence, and message history."
```

## Analytics API

```
> Use the master-orchestrator agent to begin new project: "Analytics API for [DATA TYPE] providing real-time and historical insights, custom queries, data export, and visualization endpoints."
```

## File Processing API

```
> Use the master-orchestrator agent to begin new project: "File processing API handling [FILE TYPES] with upload, transformation, storage in [STORAGE SERVICE], and async processing for [FILE SIZE] files."
```

## Variables to Replace:
- `[DOMAIN]` - Business domain (e.g., "e-commerce", "healthcare")
- `[OPERATIONS]` - CRUD operations, specific actions
- `[AUTH METHOD]` - OAuth2, JWT, API keys
- `[REQUESTS/SEC]` - Expected load
- `[SLA REQUIREMENT]` - Uptime percentage
- `[APPLICATION TYPE]` - Web app, mobile app, etc.
- `[DATA SOURCES]` - Databases, external APIs
- `[SYSTEM TYPE]` - E-commerce, banking, etc.
- `[MESSAGE BROKER]` - RabbitMQ, Kafka, etc.
- `[PAYMENT METHODS]` - Cards, ACH, crypto, etc.
- `[EVENT TYPES]` - Order created, user updated, etc.

## API-Specific Enhancements

### Performance Requirements
```
"...with sub-100ms response times, caching strategy, and CDN integration"
```

### Security Requirements
```
"...implementing OAuth 2.0, rate limiting, API key rotation, and request signing"
```

### Documentation
```
"...with OpenAPI 3.0 specification, interactive documentation, and client SDK generation"
```

### Monitoring
```
"...including APM integration, custom metrics, alerting, and SLA monitoring"
```

### Versioning Strategy
```
"...with semantic versioning, deprecation policy, and backward compatibility"
```

## Integration Patterns

### Third-Party Services
```
"...integrated with [Stripe/Twilio/SendGrid/AWS] for [payment/communication/email/infrastructure]"
```

### Database Strategy
```
"...using [PostgreSQL/MongoDB] with read replicas, connection pooling, and query optimization"
```

### Message Queue
```
"...with [RabbitMQ/Kafka/SQS] for async processing and event streaming"
```

### Caching Layer
```
"...implementing Redis caching with cache invalidation and warming strategies"
```

## Deployment Options

### Containerized
```
"...containerized with Docker, Kubernetes orchestration, and auto-scaling policies"
```

### Serverless
```
"...deployed as serverless functions on [AWS Lambda/Google Cloud Functions] with API Gateway"
```

### Multi-Region
```
"...deployed across [REGIONS] with geo-routing and data replication"
```