# Master Prompts - Development Workflows (v2.1 4-Stack)

Universal prompts for development tasks using v2.1's slash commands, @agent- mentions, MCPs, and hooks. Replace all bracketed variables with your specific values.

## Frontend Development

### UI/UX Design with Slash Commands
```
/design-system "[APPLICATION_NAME] following [DESIGN_PRINCIPLES] with [ACCESSIBILITY_STANDARD] compliance and supporting [DEVICE_TYPES]"
```
**Routes to**: @agent-ui-ux-designer
**MCPs**: Figma API, Design token generators, Accessibility checkers
**Hooks**: Design consistency validation, accessibility compliance check

### Frontend Architecture
```
@agent-frontend-engineer Design information architecture for [APPLICATION_TYPE] with [PAGE_COUNT] pages, [USER_FLOWS] user flows, and [STATE_MANAGEMENT] state management
```
**MCPs**: Component libraries, State management tools
**Hooks**: Performance budgets, bundle size monitoring

### Component Development
```
/frontend-mockup "[COMPONENT_TYPE] components using [FRAMEWORK] with [STYLING_APPROACH] supporting [BROWSER_TARGETS] and [PERFORMANCE_GOALS]"
```
**Agent collaboration**: @agent-frontend-engineer + @agent-ui-ux-designer
**MCPs**: Framework CLIs, Component generators, Style processors
**Hooks**: Component testing, visual regression checks

### Mobile Development
```
@agent-mobile-engineer Create [PLATFORM] application for [USE_CASE] supporting [FEATURES] with [OFFLINE_CAPABILITY] offline support and [NATIVE_FEATURES] native features
```
**MCPs**: React Native/Flutter CLIs, Device simulators
**Hooks**: Cross-platform compatibility, offline sync validation

## Backend Development

### API Development with Multi-Agent Collaboration
```
/backend-service "[API_TYPE] API for [DOMAIN] supporting [OPERATIONS] with [AUTH_METHOD] authentication and [RATE_LIMITS] rate limiting"
```
**Agent flow**:
1. @agent-backend-engineer creates service structure
2. @agent-database-architect designs data models
3. @agent-api-integration-specialist sets up integrations
4. @agent-security-architect implements auth

**MCPs**: API generators, Database tools, Auth providers
**Hooks**: API contract validation, rate limit testing

### Service Architecture
```
@agent-software-architect + @agent-backend-engineer Implement [ARCHITECTURE_PATTERN] architecture for [SERVICE_NAME] handling [REQUEST_VOLUME] requests with [LATENCY_TARGET] latency
```
**MCPs**: Service mesh tools, Load testing frameworks
**Hooks**: Architecture compliance, performance benchmarking

### Database Design
```
@agent-database-architect Design database schema for [APPLICATION_DOMAIN] supporting [DATA_VOLUME] records with [QUERY_PATTERNS] and [CONSISTENCY_REQUIREMENTS]
```
**MCPs**: Database modeling tools, Migration generators
**Hooks**: Schema validation, query performance analysis

### Integration Development
```
@agent-api-integration-specialist Integrate with [EXTERNAL_SERVICE] API for [PURPOSE] handling [DATA_FLOW] with [ERROR_HANDLING] error handling and [RETRY_STRATEGY]
```
**MCPs**: API testing tools, Mock servers
**Hooks**: Integration health checks, retry mechanism validation

## DevOps & Infrastructure

### CI/CD Pipeline with Automation
```
/setup-cicd "[PROJECT_TYPE] with [STAGES] stages, [TESTING_REQUIREMENTS] testing, and deployment to [ENVIRONMENTS]"
```
**Routes to**: @agent-devops-engineer
**MCPs**: GitHub Actions, GitLab CI, Jenkins API
**Hooks**: Pipeline optimization, deployment validation

### Infrastructure Setup
```
@agent-devops-engineer + @agent-cloud-infrastructure Provision infrastructure for [APPLICATION_NAME] on [CLOUD_PROVIDER] supporting [TRAFFIC_VOLUME] with [AVAILABILITY_TARGET] availability
```
**MCPs**: Terraform, CloudFormation, Pulumi
**Hooks**: Cost optimization, availability monitoring

### Container Orchestration
```
/containerize "[APPLICATION_NAME] with [ORCHESTRATOR] supporting [SCALING_REQUIREMENTS] and [RESOURCE_LIMITS]"
```
**Agent**: @agent-devops-engineer
**MCPs**: Docker API, Kubernetes tools
**Hooks**: Container security scanning, resource optimization

### Monitoring Setup
```
@agent-devops-engineer Implement monitoring for [SYSTEM_NAME] tracking [METRICS] with [ALERTING_RULES] and [RETENTION_PERIOD] retention
```
**MCPs**: Prometheus, Grafana APIs, DataDog
**Hooks**: Alert noise reduction, metric correlation

## Testing Implementation

### Test Strategy with Automation
```
/test-strategy "[APPLICATION_NAME] achieving [COVERAGE_TARGET] coverage with [TEST_TYPES] and [AUTOMATION_LEVEL] automation"
```
**Routes to**: @agent-testing-automation
**MCPs**: Jest, Pytest, Testing frameworks
**Hooks**: Coverage tracking, test flakiness detection

### Test Implementation
```
@agent-testing-automation Implement [TEST_TYPE] tests for [MODULE/FEATURE] covering [SCENARIOS] with [FRAMEWORK] framework
```
**MCPs**: Test runners, Mock generators
**Hooks**: Test execution optimization, parallel testing

### Performance Testing
```
@agent-performance-optimization Create performance tests for [SYSTEM_NAME] simulating [USER_LOAD] users with [USAGE_PATTERNS] and [PERFORMANCE_CRITERIA]
```
**MCPs**: K6, JMeter, Gatling APIs
**Hooks**: Performance regression detection, bottleneck analysis

## Security Implementation

### Security Audit with Compliance
```
/security-audit "[APPLICATION_NAME] for [COMPLIANCE_STANDARD] compliance checking [SECURITY_AREAS] with [THREAT_MODEL]"
```
**Routes to**: @agent-security-architect
**MCPs**: Security scanners, Compliance checkers
**Hooks**: Vulnerability tracking, compliance monitoring

### Authentication System
```
@agent-security-architect Implement [AUTH_TYPE] authentication for [APPLICATION_NAME] supporting [USER_TYPES] with [SECURITY_FEATURES]
```
**MCPs**: Auth0, Okta APIs, Identity providers
**Hooks**: Security policy enforcement, auth flow validation

### Data Protection
```
@agent-security-architect + @agent-database-architect Implement data protection for [DATA_TYPES] using [ENCRYPTION_METHOD] with [COMPLIANCE_REQUIREMENTS]
```
**MCPs**: Encryption libraries, Key management services
**Hooks**: Encryption validation, compliance verification

## Documentation

### Technical Documentation with Auto-Generation
```
/generate-docs "[PROJECT_NAME] including [DOCUMENT_TYPES] for [AUDIENCE_TYPES] with [DETAIL_LEVEL] detail"
```
**Routes to**: @agent-technical-documentation
**MCPs**: Documentation generators, Diagram tools
**Hooks**: Documentation freshness checks, broken link detection

### API Documentation
```
@agent-technical-documentation Document [API_NAME] API with [SPECIFICATION_FORMAT] including [EXAMPLE_TYPES] and [AUTHENTICATION_DETAILS]
```
**MCPs**: OpenAPI generators, Postman collections
**Hooks**: API contract validation, example testing

### User Guides
```
@agent-technical-documentation Create user guide for [APPLICATION_NAME] covering [FEATURES] for [USER_LEVEL] users with [GUIDE_FORMAT]
```
**MCPs**: Documentation platforms, Screenshot tools
**Hooks**: Readability analysis, user feedback integration

## Real-World Workflow Examples

### Complete Feature Development
```
/new-feature "User authentication system with social login"

Triggers workflow:
1. @agent-ui-ux-designer creates login UI mockups
2. @agent-frontend-engineer implements components
3. @agent-backend-engineer creates auth endpoints
4. @agent-database-architect designs user schema
5. @agent-security-architect reviews implementation
6. @agent-testing-automation creates test suite
7. @agent-devops-engineer deploys to staging

MCPs: React/Vue CLI, Auth providers, Database tools
Hooks: Security validation, test coverage, performance checks
```

### API Service Creation
```
/backend-service "Payment processing API with Stripe integration"

Multi-agent collaboration:
- @agent-backend-engineer: Service architecture
- @agent-api-integration-specialist: Stripe integration
- @agent-security-architect: PCI compliance
- @agent-testing-automation: Integration tests
- @agent-technical-documentation: API docs

MCPs: Stripe API, Payment gateways, Security scanners
Hooks: Compliance validation, transaction monitoring
```

### Infrastructure Modernization
```
/modernize-infrastructure "Migrate monolith to microservices on K8s"

Agent orchestra:
- @agent-software-architect: Decomposition strategy
- @agent-backend-engineer: Service extraction
- @agent-devops-engineer: K8s setup
- @agent-cloud-infrastructure: Cloud architecture
- @agent-performance-optimization: Load testing

MCPs: Kubernetes tools, Service mesh, Migration tools
Hooks: Zero-downtime migration, rollback procedures
```

## Variable Reference

- `[APPLICATION_NAME]`: Your application/project name
- `[FRAMEWORK]`: React, Vue, Angular, Next.js, etc.
- `[API_TYPE]`: REST, GraphQL, gRPC, WebSocket
- `[CLOUD_PROVIDER]`: AWS, Azure, GCP, Vercel, Netlify
- `[DATABASE_TYPE]`: PostgreSQL, MongoDB, MySQL, Redis
- `[TEST_TYPE]`: unit, integration, e2e, performance
- `[AUTH_TYPE]`: JWT, OAuth2, SAML, WebAuthn
- `[PERFORMANCE_GOALS]`: <100ms response, 3s page load
- `[SCALING_REQUIREMENTS]`: 10k RPS, auto-scaling to 100 pods
- `[COMPLIANCE_STANDARD]`: GDPR, HIPAA, PCI-DSS, SOC2
- `[USER_TYPES]`: admin, user, guest, developer roles
- `[ENVIRONMENTS]`: dev, staging, production, preview
- `[COVERAGE_TARGET]`: 80%, 90%, 95% test coverage