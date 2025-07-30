# Performance Optimization Prompts

Use these prompts to improve the performance of existing applications and systems.

## Application Performance

### Overall Performance Audit
```
> Use the performance-optimization agent to conduct comprehensive performance audit of [APPLICATION] and create optimization roadmap
```

### Page Load Optimization
```
> Use the performance-optimization agent to reduce page load time for [PAGE/ROUTE] from [CURRENT TIME] to [TARGET TIME]
```

### API Response Time
```
> Use the performance-optimization agent to optimize API endpoints in [SERVICE] to achieve [TARGET LATENCY] p95 response time
```

### Mobile App Performance
```
> Use the performance-optimization agent to improve [iOS/Android] app startup time and reduce memory usage by [PERCENTAGE]
```

## Database Performance

### Query Optimization
```
> Use the database-architecture agent to optimize top [NUMBER] slowest queries in [APPLICATION] database
```

### Index Strategy
```
> Use the database-architecture agent to analyze query patterns and implement optimal indexing strategy for [DATABASE]
```

### Connection Pooling
```
> Use the database-architecture agent to optimize database connection pooling for [APPLICATION] handling [CONCURRENT USERS]
```

### Database Caching
```
> Use the performance-optimization agent to implement caching strategy for [DATABASE] queries reducing load by [PERCENTAGE]
```

## Frontend Optimization

### Bundle Size Reduction
```
> Use the performance-optimization agent to reduce JavaScript bundle size for [APPLICATION] from [CURRENT SIZE] to [TARGET SIZE]
```

### Image Optimization
```
> Use the performance-optimization agent to optimize images in [APPLICATION] with lazy loading, WebP conversion, and responsive sizing
```

### React Performance
```
> Use the production-frontend agent to optimize React components in [APPLICATION] eliminating unnecessary re-renders
```

### CSS Optimization
```
> Use the performance-optimization agent to optimize CSS delivery with critical CSS, tree shaking, and minification
```

## Backend Optimization

### Server Response Time
```
> Use the backend-services agent to optimize [ENDPOINT/SERVICE] server response time using profiling and bottleneck analysis
```

### Memory Usage
```
> Use the performance-optimization agent to reduce memory footprint of [SERVICE] from [CURRENT] to [TARGET] under load
```

### Concurrent Request Handling
```
> Use the backend-services agent to optimize [SERVICE] to handle [REQUEST COUNT] concurrent requests without degradation
```

### Background Job Performance
```
> Use the backend-services agent to optimize background job processing for [JOB TYPE] improving throughput by [PERCENTAGE]
```

## Caching Strategies

### Redis Implementation
```
> Use the performance-optimization agent to implement Redis caching for [DATA TYPE] with appropriate TTL and invalidation
```

### CDN Configuration
```
> Use the devops-engineering agent to implement CDN caching for [ASSET TYPES] reducing origin load by [PERCENTAGE]
```

### Application-Level Caching
```
> Use the backend-services agent to implement application-level caching for [OPERATION TYPE] using [STRATEGY]
```

### Database Query Cache
```
> Use the database-architecture agent to optimize query cache settings for [DATABASE TYPE] workload
```

## Scaling Optimization

### Horizontal Scaling
```
> Use the devops-engineering agent to implement horizontal scaling for [SERVICE] to handle [GROWTH FACTOR]x current load
```

### Load Balancing
```
> Use the devops-engineering agent to optimize load balancer configuration for [APPLICATION] improving distribution efficiency
```

### Auto-Scaling Rules
```
> Use the devops-engineering agent to tune auto-scaling parameters for [SERVICE] based on [METRICS] patterns
```

### Resource Utilization
```
> Use the performance-optimization agent to optimize resource utilization for [APPLICATION] reducing costs by [PERCENTAGE]
```

## Network Optimization

### API Payload Size
```
> Use the backend-services agent to optimize API payloads for [ENDPOINTS] reducing bandwidth usage by [PERCENTAGE]
```

### HTTP/2 Implementation
```
> Use the devops-engineering agent to implement HTTP/2 for [APPLICATION] with multiplexing and server push
```

### WebSocket Optimization
```
> Use the backend-services agent to optimize WebSocket connections for [USE CASE] handling [CONNECTION COUNT]
```

### GraphQL Query Optimization
```
> Use the backend-services agent to optimize GraphQL resolvers preventing N+1 queries and implementing DataLoader
```

## Monitoring & Profiling

### Performance Monitoring
```
> Use the devops-engineering agent to implement APM for [APPLICATION] tracking key performance metrics and bottlenecks
```

### Real User Monitoring
```
> Use the performance-optimization agent to implement RUM for [APPLICATION] tracking actual user experience metrics
```

### Load Testing
```
> Use the performance-optimization agent to conduct load test for [APPLICATION] simulating [USER COUNT] concurrent users
```

### Profiling Analysis
```
> Use the performance-optimization agent to profile [APPLICATION/SERVICE] and identify top performance bottlenecks
```

## Specific Optimizations

### Search Performance
```
> Use the backend-services agent to optimize search functionality in [APPLICATION] from [CURRENT SPEED] to [TARGET SPEED]
```

### Report Generation
```
> Use the backend-services agent to optimize report generation for [REPORT TYPE] reducing time from [CURRENT] to [TARGET]
```

### File Upload/Processing
```
> Use the backend-services agent to optimize file upload and processing for [FILE TYPE] handling [SIZE] files efficiently
```

### Batch Processing
```
> Use the backend-services agent to optimize batch processing job [JOB NAME] to process [VOLUME] records in [TIME]
```

## Variables to Replace:
- `[APPLICATION]` - Your application name
- `[CURRENT TIME]` - Current metric (2s, 500ms)
- `[TARGET TIME]` - Target metric (200ms, 50ms)
- `[PERCENTAGE]` - 30%, 50%, 70%
- `[CONCURRENT USERS]` - 1K, 10K, 100K
- `[DATABASE]` - PostgreSQL, MySQL, MongoDB
- `[SERVICE]` - Specific service name
- `[METRICS]` - CPU, memory, response time