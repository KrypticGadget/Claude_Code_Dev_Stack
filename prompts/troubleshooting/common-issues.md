# Troubleshooting Common Issues

Use these prompts to diagnose and fix common problems in your projects.

## Performance Issues

### Slow API Response
```
> Use the performance-optimization agent to analyze slow API endpoint [ENDPOINT] currently taking [CURRENT TIME] and optimize to under [TARGET TIME]
```

### Database Query Optimization
```
> Use the database-architecture agent to identify and fix slow queries in [APPLICATION] that are causing [SYMPTOM]
```

### Frontend Performance
```
> Use the performance-optimization agent to analyze [PAGE/COMPONENT] load time and reduce from [CURRENT] to [TARGET] seconds
```

### Memory Leaks
```
> Use the performance-optimization agent to identify memory leaks in [APPLICATION PART] causing [ISSUE DESCRIPTION]
```

## Security Issues

### Vulnerability Assessment
```
> Use the security-architecture agent to perform security audit of [APPLICATION/API] and fix identified vulnerabilities
```

### Authentication Problems
```
> Use the security-architecture agent to diagnose authentication issue where [PROBLEM DESCRIPTION] and implement fix
```

### Data Breach Response
```
> Use the security-architecture agent to assess potential data breach in [SYSTEM] and implement immediate remediation
```

## Integration Problems

### API Integration Failures
```
> Use the api-integration-specialist agent to debug failing integration with [SERVICE] showing error [ERROR MESSAGE]
```

### Webhook Issues
```
> Use the api-integration-specialist agent to fix webhook delivery failures to [ENDPOINT] with [ERROR DESCRIPTION]
```

### Data Sync Problems
```
> Use the middleware-specialist agent to resolve data synchronization issues between [SYSTEM A] and [SYSTEM B]
```

## Database Issues

### Connection Pool Exhaustion
```
> Use the database-architecture agent to fix database connection pool exhaustion causing [ERROR] in [APPLICATION]
```

### Deadlock Resolution
```
> Use the database-architecture agent to identify and resolve database deadlocks occurring in [OPERATION]
```

### Replication Lag
```
> Use the database-architecture agent to diagnose and fix replication lag of [DURATION] between master and replica
```

## Deployment Issues

### Failed Deployments
```
> Use the devops-engineering agent to troubleshoot deployment failure to [ENVIRONMENT] with error [ERROR LOG]
```

### Container Crashes
```
> Use the devops-engineering agent to diagnose container crashes in [SERVICE] with exit code [CODE]
```

### CI/CD Pipeline Failures
```
> Use the devops-engineering agent to fix failing CI/CD pipeline at [STAGE] with error [ERROR MESSAGE]
```

## Scaling Issues

### Auto-scaling Problems
```
> Use the devops-engineering agent to fix auto-scaling not triggering for [SERVICE] despite [METRIC] reaching [THRESHOLD]
```

### Load Balancer Issues
```
> Use the devops-engineering agent to diagnose load balancer not distributing traffic evenly to [SERVICE] instances
```

### Resource Exhaustion
```
> Use the performance-optimization agent to address [RESOURCE TYPE] exhaustion in [SERVICE] under [LOAD CONDITION]
```

## Code Quality Issues

### Technical Debt
```
> Use the quality-assurance agent to identify and create plan to address technical debt in [MODULE/SERVICE]
```

### Code Complexity
```
> Use the quality-assurance agent to refactor complex code in [FILE/MODULE] to improve maintainability
```

### Test Coverage
```
> Use the testing-automation agent to improve test coverage for [MODULE] from [CURRENT]% to [TARGET]%
```

## Common Error Patterns

### CORS Issues
```
> Use the backend-services agent to fix CORS errors preventing [FRONTEND] from accessing [API ENDPOINT]
```

### SSL Certificate Problems
```
> Use the security-architecture agent to resolve SSL certificate error [ERROR TYPE] on [DOMAIN]
```

### Environment Variable Issues
```
> Use the integration-setup agent to debug missing or incorrect environment variables causing [APPLICATION] to fail
```

### Dependency Conflicts
```
> Use the integration-setup agent to resolve dependency conflicts between [PACKAGE A] and [PACKAGE B]
```

## Debugging Strategies

### Log Analysis
```
> Use the devops-engineering agent to analyze logs for [SERVICE] to identify root cause of [ISSUE DESCRIPTION]
```

### Distributed Tracing
```
> Use the devops-engineering agent to trace request flow through microservices to identify bottleneck causing [SYMPTOM]
```

### Error Monitoring
```
> Use the devops-engineering agent to setup error monitoring for [APPLICATION] to catch and alert on [ERROR TYPES]
```

## Variables to Replace:
- `[ENDPOINT]` - Specific API endpoint
- `[CURRENT TIME]` - Current response time
- `[TARGET TIME]` - Desired response time
- `[APPLICATION]` - Application name
- `[SYMPTOM]` - What users are experiencing
- `[SERVICE]` - External service name
- `[ERROR MESSAGE]` - Actual error text
- `[SYSTEM A/B]` - System names
- `[ENVIRONMENT]` - dev, staging, prod
- `[METRIC]` - CPU, memory, requests
- `[THRESHOLD]` - Trigger value