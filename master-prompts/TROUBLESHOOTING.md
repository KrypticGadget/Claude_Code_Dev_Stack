# Master Prompts - Troubleshooting

Universal prompts for diagnosing and fixing issues. Replace bracketed variables with your specific values.

## Performance Issues

### Performance Diagnosis
```
> Use the performance-optimization agent to diagnose performance issues in [APPLICATION_NAME] where [SYMPTOM_DESCRIPTION] occurs under [CONDITIONS] affecting [METRICS]
```

### Bottleneck Analysis
```
> Use the performance-optimization agent to identify bottlenecks causing [PERFORMANCE_ISSUE] in [SYSTEM_COMPONENT] when [TRIGGER_CONDITION]
```

### Memory Issues
```
> Use the performance-optimization agent to investigate memory issues in [APPLICATION_NAME] showing [MEMORY_PATTERN] during [OPERATIONS]
```

## Bug Investigation

### Bug Diagnosis
```
> Use the quality-assurance agent to investigate bug where [BUG_DESCRIPTION] occurs in [FEATURE/MODULE] under [REPRODUCTION_STEPS]
```

### Root Cause Analysis
```
> Use the quality-assurance agent to perform root cause analysis for [ISSUE_TYPE] affecting [SYSTEM_AREA] with symptoms [SYMPTOM_LIST]
```

### Error Pattern Analysis
```
> Use the quality-assurance agent to analyze error patterns in [LOG_SOURCE] showing [ERROR_TYPES] occurring [FREQUENCY]
```

## Integration Issues

### API Failures
```
> Use the api-integration-specialist agent to troubleshoot API integration with [SERVICE_NAME] failing with [ERROR_TYPE] when [OPERATION]
```

### Data Sync Issues
```
> Use the middleware-specialist agent to diagnose data synchronization issues between [SYSTEM_A] and [SYSTEM_B] showing [INCONSISTENCY_TYPE]
```

### Authentication Problems
```
> Use the security-architecture agent to troubleshoot authentication issues where [AUTH_FAILURE_TYPE] occurs for [USER_TYPE] when [ACTION]
```

## Database Issues

### Query Performance
```
> Use the database-architecture agent to troubleshoot slow queries in [DATABASE_NAME] where [QUERY_TYPE] takes [CURRENT_TIME] instead of expected [EXPECTED_TIME]
```

### Data Integrity
```
> Use the database-architecture agent to investigate data integrity issues in [TABLE/COLLECTION] showing [INTEGRITY_PROBLEM] affecting [RECORD_COUNT] records
```

### Connection Issues
```
> Use the database-architecture agent to diagnose database connection issues showing [CONNECTION_ERROR] under [LOAD_CONDITION]
```

## Deployment Issues

### Deployment Failures
```
> Use the devops-engineering agent to troubleshoot deployment failure to [ENVIRONMENT] showing [ERROR_MESSAGE] during [DEPLOYMENT_STAGE]
```

### Environment Differences
```
> Use the devops-engineering agent to diagnose why [FEATURE/SYSTEM] works in [ENVIRONMENT_A] but fails in [ENVIRONMENT_B]
```

### Container Issues
```
> Use the devops-engineering agent to troubleshoot container issues where [CONTAINER_NAME] shows [PROBLEM_TYPE] with [SYMPTOMS]
```

## Frontend Issues

### UI Rendering
```
> Use the production-frontend agent to fix rendering issues in [COMPONENT/PAGE] on [BROWSER/DEVICE] showing [VISUAL_PROBLEM]
```

### State Management
```
> Use the production-frontend agent to debug state management issues where [STATE_PROBLEM] occurs in [COMPONENT] when [USER_ACTION]
```

### Browser Compatibility
```
> Use the production-frontend agent to fix compatibility issues in [BROWSER_NAME] version [VERSION] affecting [FEATURE]
```

## Security Issues

### Vulnerability Investigation
```
> Use the security-architecture agent to investigate [VULNERABILITY_TYPE] reported in [COMPONENT] with severity [SEVERITY_LEVEL]
```

### Access Control Issues
```
> Use the security-architecture agent to troubleshoot access control where [USER_ROLE] can/cannot [ACTION] on [RESOURCE]
```

### Security Breach Analysis
```
> Use the security-architecture agent to analyze potential security breach showing [INDICATORS] in [SYSTEM_AREA] during [TIME_PERIOD]
```

## Test Failures

### Test Debugging
```
> Use the testing-automation agent to debug failing tests in [TEST_SUITE] where [TEST_COUNT] tests fail with [ERROR_PATTERN]
```

### Flaky Test Resolution
```
> Use the testing-automation agent to fix flaky tests in [TEST_CATEGORY] that fail [FAILURE_RATE] of the time
```

### Coverage Gaps
```
> Use the testing-automation agent to identify why [CODE_AREA] shows [COVERAGE_PERCENTAGE] coverage despite [EXPECTATION]
```

## System Issues

### Service Availability
```
> Use the devops-engineering agent to troubleshoot service unavailability where [SERVICE_NAME] is [STATUS] showing [ERROR_INDICATORS]
```

### Resource Exhaustion
```
> Use the performance-optimization agent to diagnose resource exhaustion where [RESOURCE_TYPE] reaches [LIMIT] during [OPERATION]
```

### Network Issues
```
> Use the devops-engineering agent to troubleshoot network issues between [SERVICE_A] and [SERVICE_B] showing [NETWORK_SYMPTOMS]
```

## Variable Reference

- `[APPLICATION_NAME]`: Your application/system name
- `[SYMPTOM_DESCRIPTION]`: Slow response, high CPU, crashes
- `[CONDITIONS]`: Under load, specific times, user actions
- `[METRICS]`: Response time, CPU usage, memory
- `[BUG_DESCRIPTION]`: Specific bug behavior
- `[REPRODUCTION_STEPS]`: Steps to reproduce issue
- `[ERROR_TYPE]`: 404, 500, timeout, specific error
- `[ENVIRONMENT]`: dev, staging, production
- `[SEVERITY_LEVEL]`: critical, high, medium, low
- `[RESOURCE_TYPE]`: CPU, memory, disk, connections
- `[USER_TYPE]`: admin, regular user, guest
- `[FAILURE_RATE]`: percentage or frequency