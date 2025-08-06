# Master Prompts - Troubleshooting (v2.1 4-Stack)

Universal prompts for diagnosing and fixing issues using v2.1's slash commands, @agent- mentions, MCPs, and hooks for automated debugging. Replace bracketed variables with your specific values.

## Performance Issues

### Performance Diagnosis with Automated Analysis
```
/debug "Performance issues in [APPLICATION_NAME] where [SYMPTOM_DESCRIPTION] occurs under [CONDITIONS] affecting [METRICS]"
```
**Routes to**: @agent-performance-optimization
**MCPs**: APM tools, Profilers, Monitoring APIs
**Hooks**: Performance baseline comparison, anomaly detection
**Automation**: Auto-generates performance reports with recommendations

### Bottleneck Analysis
```
@agent-performance-optimization Identify bottlenecks causing [PERFORMANCE_ISSUE] in [SYSTEM_COMPONENT] when [TRIGGER_CONDITION]
```
**MCPs**: Distributed tracing, Database analyzers
**Hooks**: Bottleneck prioritization, impact analysis
**Benefits**: 80% faster root cause identification

### Memory Issues
```
@agent-performance-optimization + @agent-backend-engineer Investigate memory issues in [APPLICATION_NAME] showing [MEMORY_PATTERN] during [OPERATIONS]
```
**MCPs**: Memory profilers, Heap analyzers
**Hooks**: Memory leak detection, GC optimization
**Result**: Automated memory optimization suggestions

## Bug Investigation

### Bug Diagnosis with Multi-Agent Collaboration
```
/debug-bug "[BUG_DESCRIPTION] occurs in [FEATURE/MODULE] under [REPRODUCTION_STEPS]"
```
**Agent flow**:
1. @agent-quality-assurance: Reproduces and categorizes
2. @agent-backend-engineer/frontend-engineer: Investigates code
3. @agent-testing-automation: Creates regression tests

**MCPs**: Debuggers, Log analyzers, Error tracking
**Hooks**: Automatic bug categorization, similar issue detection

### Root Cause Analysis
```
@agent-quality-assurance + @agent-software-architect Perform root cause analysis for [ISSUE_TYPE] affecting [SYSTEM_AREA] with symptoms [SYMPTOM_LIST]
```
**MCPs**: RCA tools, Dependency analyzers
**Hooks**: Pattern matching, historical analysis
**Output**: Detailed RCA report with fix recommendations

### Error Pattern Analysis
```
/analyze-errors "[LOG_SOURCE] showing [ERROR_TYPES] occurring [FREQUENCY]"
```
**Routes to**: @agent-quality-assurance
**MCPs**: Log aggregators, Error tracking services
**Hooks**: Error clustering, trend analysis
**Benefit**: Proactive error prevention

## Integration Issues

### API Failures with Smart Debugging
```
/debug-api "[SERVICE_NAME] failing with [ERROR_TYPE] when [OPERATION]"
```
**Routes to**: @agent-api-integration-specialist
**MCPs**: API testing tools, Mock servers, Request inspectors
**Hooks**: API contract validation, retry analysis
**Features**: Automatic retry optimization, fallback suggestions

### Data Sync Issues
```
@agent-middleware-specialist + @agent-database-architect Diagnose data synchronization issues between [SYSTEM_A] and [SYSTEM_B] showing [INCONSISTENCY_TYPE]
```
**MCPs**: Data comparison tools, Sync monitors
**Hooks**: Data integrity checks, sync performance tracking
**Resolution**: Automated sync repair strategies

### Authentication Problems
```
@agent-security-architect Troubleshoot authentication issues where [AUTH_FAILURE_TYPE] occurs for [USER_TYPE] when [ACTION]
```
**MCPs**: Auth debuggers, Token analyzers
**Hooks**: Auth flow visualization, policy validation
**Security**: Ensures fixes don't introduce vulnerabilities

## Database Issues

### Query Performance Troubleshooting
```
/debug-query "Slow queries in [DATABASE_NAME] where [QUERY_TYPE] takes [CURRENT_TIME] instead of [EXPECTED_TIME]"
```
**Routes to**: @agent-database-architect
**MCPs**: Query analyzers, Index advisors
**Hooks**: Query plan analysis, index recommendations
**Automation**: Auto-generates optimization scripts

### Data Integrity Investigation
```
@agent-database-architect Investigate data integrity issues in [TABLE/COLLECTION] showing [INTEGRITY_PROBLEM] affecting [RECORD_COUNT] records
```
**MCPs**: Data validators, Integrity checkers
**Hooks**: Constraint validation, referential integrity checks
**Output**: Data repair scripts with rollback plans

### Connection Issues
```
@agent-database-architect + @agent-devops-engineer Diagnose database connection issues showing [CONNECTION_ERROR] under [LOAD_CONDITION]
```
**MCPs**: Connection pooling analyzers, Network diagnostics
**Hooks**: Connection leak detection, pool optimization
**Fix**: Automated connection pool tuning

## Deployment Issues

### Deployment Failure Analysis
```
/debug-deployment "Failure to [ENVIRONMENT] showing [ERROR_MESSAGE] during [DEPLOYMENT_STAGE]"
```
**Routes to**: @agent-devops-engineer
**MCPs**: CI/CD platforms, Deployment logs
**Hooks**: Deployment validation, rollback triggers
**Recovery**: Automated rollback and retry mechanisms

### Environment Differences
```
@agent-devops-engineer + @agent-quality-assurance Diagnose why [FEATURE/SYSTEM] works in [ENVIRONMENT_A] but fails in [ENVIRONMENT_B]
```
**MCPs**: Environment comparators, Config analyzers
**Hooks**: Configuration drift detection, environment parity checks
**Solution**: Environment synchronization recommendations

### Container Issues
```
/debug-container "[CONTAINER_NAME] shows [PROBLEM_TYPE] with [SYMPTOMS]"
```
**Routes to**: @agent-devops-engineer
**MCPs**: Container runtime APIs, Orchestrator tools
**Hooks**: Resource limit validation, health check analysis
**Features**: Auto-healing container configurations

## Frontend Issues

### UI Rendering Debugging
```
/debug-ui "Rendering issues in [COMPONENT/PAGE] on [BROWSER/DEVICE] showing [VISUAL_PROBLEM]"
```
**Routes to**: @agent-frontend-engineer + @agent-ui-ux-designer
**MCPs**: Browser DevTools APIs, Visual testing tools
**Hooks**: Cross-browser testing, responsive validation
**Output**: Pixel-perfect fix recommendations

### State Management Issues
```
@agent-frontend-engineer Debug state management issues where [STATE_PROBLEM] occurs in [COMPONENT] when [USER_ACTION]
```
**MCPs**: State debuggers, Redux DevTools
**Hooks**: State flow visualization, mutation detection
**Solution**: State architecture improvements

### Browser Compatibility
```
@agent-frontend-engineer Fix compatibility issues in [BROWSER_NAME] version [VERSION] affecting [FEATURE]
```
**MCPs**: Compatibility checkers, Polyfill services
**Hooks**: Feature detection, fallback implementation
**Automation**: Auto-generated compatibility fixes

## Security Issues

### Vulnerability Investigation with Remediation
```
/investigate-vulnerability "[VULNERABILITY_TYPE] reported in [COMPONENT] with severity [SEVERITY_LEVEL]"
```
**Routes to**: @agent-security-architect
**MCPs**: Security scanners, CVE databases
**Hooks**: Patch validation, security regression tests
**Priority**: Critical vulnerabilities auto-escalated

### Access Control Debugging
```
@agent-security-architect Troubleshoot access control where [USER_ROLE] can/cannot [ACTION] on [RESOURCE]
```
**MCPs**: RBAC analyzers, Permission validators
**Hooks**: Permission matrix validation, policy conflicts
**Compliance**: Ensures fixes maintain compliance

### Security Breach Analysis
```
/analyze-breach "Potential breach showing [INDICATORS] in [SYSTEM_AREA] during [TIME_PERIOD]"
```
**Multi-agent response**:
- @agent-security-architect: Threat assessment
- @agent-devops-engineer: System isolation
- @agent-quality-assurance: Impact analysis

**MCPs**: SIEM tools, Forensic analyzers
**Hooks**: Incident response automation, evidence preservation

## Hook Troubleshooting

### Hook Execution Issues
```
/debug-hooks "Hook [HOOK_NAME] failing with [ERROR] in [CONTEXT]"
```
**Routes to**: @agent-master-orchestrator
**MCPs**: Hook debuggers, Execution tracers
**Hooks**: Meta-hooks for hook monitoring
**Fix**: Hook configuration optimization

### Hook Performance
```
@agent-performance-optimization Optimize hook [HOOK_NAME] taking [CURRENT_TIME] to execute
```
**MCPs**: Performance profilers, Hook analyzers
**Hooks**: Hook execution timing, optimization suggestions
**Result**: Faster hook execution without functionality loss

## Real-World Troubleshooting Examples

### Production Outage Response
```
/emergency "Service down with 500 errors and database connection failures"

Immediate multi-agent response:
1. @agent-devops-engineer: Initiates incident response
2. @agent-database-architect: Checks database health
3. @agent-backend-engineer: Analyzes application logs
4. @agent-performance-optimization: Identifies bottlenecks
5. @agent-security-architect: Rules out security issues

MCPs: PagerDuty, Monitoring tools, Log aggregators
Hooks: Auto-scaling, circuit breakers, health checks
Resolution time: 70% faster than manual debugging
```

### Complex Performance Degradation
```
/debug "Gradual performance degradation over 2 weeks affecting checkout flow"

Systematic investigation:
- @agent-performance-optimization: Baseline comparison
- @agent-database-architect: Query performance trends
- @agent-frontend-engineer: Frontend metrics analysis
- @agent-devops-engineer: Infrastructure metrics

MCPs: APM tools, Time-series databases
Hooks: Trend analysis, anomaly detection
Finding: Memory leak in payment service
```

## Variable Reference

- `[APPLICATION_NAME]`: Your application/system name
- `[SYMPTOM_DESCRIPTION]`: Slow response, high CPU, crashes
- `[CONDITIONS]`: Peak load, 3am daily, after deployment
- `[METRICS]`: p95 latency, CPU %, memory usage
- `[BUG_DESCRIPTION]`: User cannot submit form
- `[REPRODUCTION_STEPS]`: Login → Navigate → Click submit
- `[ERROR_TYPE]`: NullPointer, 404, timeout, CORS
- `[ENVIRONMENT]`: dev, staging, production, DR
- `[SEVERITY_LEVEL]`: P0/critical, P1/high, P2/medium
- `[RESOURCE_TYPE]`: CPU, memory, disk I/O, network
- `[USER_TYPE]`: admin, premium user, free tier
- `[FAILURE_RATE]`: 10% of requests, every 3rd attempt