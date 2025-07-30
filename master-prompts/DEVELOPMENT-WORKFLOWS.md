# Master Prompts - Development Workflows

Universal prompts for development tasks. Replace all bracketed variables with your specific values.

## Frontend Development

### UI/UX Design
```
> Use the ui-ux-design agent to create design system for [APPLICATION_NAME] following [DESIGN_PRINCIPLES] with [ACCESSIBILITY_STANDARD] compliance and supporting [DEVICE_TYPES]
```

### Frontend Architecture
```
> Use the frontend-architecture agent to design information architecture for [APPLICATION_TYPE] with [PAGE_COUNT] pages, [USER_FLOWS] user flows, and [STATE_MANAGEMENT] state management
```

### Component Development
```
> Use the production-frontend agent to build [COMPONENT_TYPE] components using [FRAMEWORK] with [STYLING_APPROACH] supporting [BROWSER_TARGETS] and [PERFORMANCE_GOALS]
```

### Mobile Development
```
> Use the mobile-development agent to create [PLATFORM] application for [USE_CASE] supporting [FEATURES] with [OFFLINE_CAPABILITY] offline support and [NATIVE_FEATURES] native features
```

## Backend Development

### API Development
```
> Use the backend-services agent to create [API_TYPE] API for [DOMAIN] supporting [OPERATIONS] with [AUTH_METHOD] authentication and [RATE_LIMITS] rate limiting
```

### Service Architecture
```
> Use the backend-services agent to implement [ARCHITECTURE_PATTERN] architecture for [SERVICE_NAME] handling [REQUEST_VOLUME] requests with [LATENCY_TARGET] latency
```

### Database Design
```
> Use the database-architecture agent to design database schema for [APPLICATION_DOMAIN] supporting [DATA_VOLUME] records with [QUERY_PATTERNS] and [CONSISTENCY_REQUIREMENTS]
```

### Integration Development
```
> Use the api-integration-specialist agent to integrate with [EXTERNAL_SERVICE] API for [PURPOSE] handling [DATA_FLOW] with [ERROR_HANDLING] error handling and [RETRY_STRATEGY]
```

## DevOps & Infrastructure

### CI/CD Pipeline
```
> Use the devops-engineering agent to create CI/CD pipeline for [PROJECT_TYPE] with [STAGES] stages, [TESTING_REQUIREMENTS] testing, and deployment to [ENVIRONMENTS]
```

### Infrastructure Setup
```
> Use the devops-engineering agent to provision infrastructure for [APPLICATION_NAME] on [CLOUD_PROVIDER] supporting [TRAFFIC_VOLUME] with [AVAILABILITY_TARGET] availability
```

### Container Orchestration
```
> Use the devops-engineering agent to containerize [APPLICATION_NAME] with [ORCHESTRATOR] supporting [SCALING_REQUIREMENTS] and [RESOURCE_LIMITS]
```

### Monitoring Setup
```
> Use the devops-engineering agent to implement monitoring for [SYSTEM_NAME] tracking [METRICS] with [ALERTING_RULES] and [RETENTION_PERIOD] retention
```

## Testing Implementation

### Test Strategy
```
> Use the testing-automation agent to create test strategy for [APPLICATION_NAME] achieving [COVERAGE_TARGET] coverage with [TEST_TYPES] and [AUTOMATION_LEVEL] automation
```

### Test Implementation
```
> Use the testing-automation agent to implement [TEST_TYPE] tests for [MODULE/FEATURE] covering [SCENARIOS] with [FRAMEWORK] framework
```

### Performance Testing
```
> Use the performance-optimization agent to create performance tests for [SYSTEM_NAME] simulating [USER_LOAD] users with [USAGE_PATTERNS] and [PERFORMANCE_CRITERIA]
```

## Security Implementation

### Security Audit
```
> Use the security-architecture agent to audit [APPLICATION_NAME] for [COMPLIANCE_STANDARD] compliance checking [SECURITY_AREAS] with [THREAT_MODEL]
```

### Authentication System
```
> Use the security-architecture agent to implement [AUTH_TYPE] authentication for [APPLICATION_NAME] supporting [USER_TYPES] with [SECURITY_FEATURES]
```

### Data Protection
```
> Use the security-architecture agent to implement data protection for [DATA_TYPES] using [ENCRYPTION_METHOD] with [COMPLIANCE_REQUIREMENTS]
```

## Documentation

### Technical Documentation
```
> Use the technical-documentation agent to create documentation for [PROJECT_NAME] including [DOCUMENT_TYPES] for [AUDIENCE_TYPES] with [DETAIL_LEVEL] detail
```

### API Documentation
```
> Use the technical-documentation agent to document [API_NAME] API with [SPECIFICATION_FORMAT] including [EXAMPLE_TYPES] and [AUTHENTICATION_DETAILS]
```

### User Guides
```
> Use the usage-guide agent to create user guide for [APPLICATION_NAME] covering [FEATURES] for [USER_LEVEL] users with [GUIDE_FORMAT]
```

## Variable Reference

- `[APPLICATION_NAME]`: Your application/project name
- `[FRAMEWORK]`: React, Vue, Angular, etc.
- `[API_TYPE]`: REST, GraphQL, gRPC
- `[CLOUD_PROVIDER]`: AWS, Azure, GCP
- `[DATABASE_TYPE]`: PostgreSQL, MongoDB, etc.
- `[TEST_TYPE]`: unit, integration, e2e
- `[AUTH_TYPE]`: JWT, OAuth2, SAML
- `[PERFORMANCE_GOALS]`: load time, response time targets
- `[SCALING_REQUIREMENTS]`: horizontal, vertical, auto-scaling
- `[COMPLIANCE_STANDARD]`: GDPR, HIPAA, PCI-DSS
- `[USER_TYPES]`: admin, user, guest roles
- `[ENVIRONMENTS]`: dev, staging, production
- `[COVERAGE_TARGET]`: 80%, 90%, etc.