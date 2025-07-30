# Code Refactoring Prompts

Use these prompts to improve code quality, maintainability, and structure.

## Code Quality Improvements

### Technical Debt Assessment
```
> Use the quality-assurance agent to analyze technical debt in [CODEBASE/MODULE] and create prioritized remediation plan
```

### Code Complexity Reduction
```
> Use the quality-assurance agent to refactor complex code in [FILE/MODULE] reducing cyclomatic complexity below [THRESHOLD]
```

### Code Duplication Removal
```
> Use the quality-assurance agent to identify and eliminate code duplication in [CODEBASE] using DRY principles
```

### Code Standards Enforcement
```
> Use the quality-assurance agent to refactor [CODEBASE] to comply with [STANDARD/STYLE GUIDE] conventions
```

## Architecture Refactoring

### Monolith to Microservices
```
> Use the backend-services agent to create plan for breaking [MONOLITH APPLICATION] into microservices starting with [MODULE]
```

### Service Extraction
```
> Use the backend-services agent to extract [FUNCTIONALITY] from [APPLICATION] into separate service
```

### API Redesign
```
> Use the backend-services agent to refactor [API] from [CURRENT STYLE] to [TARGET STYLE] maintaining compatibility
```

### Database Schema Refactoring
```
> Use the database-architecture agent to refactor database schema for [APPLICATION] improving normalization and performance
```

## Frontend Refactoring

### Component Refactoring
```
> Use the production-frontend agent to refactor [COMPONENT/PAGE] into reusable components following [PATTERN]
```

### State Management
```
> Use the frontend-architecture agent to refactor state management from [CURRENT] to [TARGET] pattern
```

### Legacy Code Modernization
```
> Use the production-frontend agent to modernize [LEGACY FRONTEND] from [OLD FRAMEWORK] to [NEW FRAMEWORK]
```

### Accessibility Improvements
```
> Use the ui-ux-design agent to refactor [APPLICATION] UI components for WCAG 2.1 AA compliance
```

## Backend Refactoring

### Design Pattern Implementation
```
> Use the backend-services agent to refactor [MODULE] implementing [PATTERN NAME] design pattern
```

### Async/Await Migration
```
> Use the backend-services agent to refactor callback-based code in [MODULE] to use async/await
```

### ORM Implementation
```
> Use the backend-services agent to refactor raw SQL queries in [APPLICATION] to use [ORM NAME]
```

### Service Layer Creation
```
> Use the backend-services agent to refactor [APPLICATION] creating proper service layer separation
```

## Testing Improvements

### Test Coverage Increase
```
> Use the testing-automation agent to refactor tests for [MODULE] increasing coverage from [CURRENT]% to [TARGET]%
```

### Test Structure Improvement
```
> Use the testing-automation agent to refactor test suite for [APPLICATION] improving organization and maintainability
```

### Integration Test Refactoring
```
> Use the testing-automation agent to refactor integration tests to use [PATTERN/FRAMEWORK] reducing flakiness
```

### Mock Implementation
```
> Use the testing-automation agent to refactor tests in [MODULE] to use proper mocking instead of real dependencies
```

## Performance Refactoring

### Algorithm Optimization
```
> Use the performance-optimization agent to refactor [ALGORITHM/FUNCTION] from O([CURRENT]) to O([TARGET]) complexity
```

### Memory Optimization
```
> Use the performance-optimization agent to refactor [MODULE] reducing memory usage by implementing [TECHNIQUE]
```

### Query Optimization
```
> Use the database-architecture agent to refactor database queries in [MODULE] eliminating N+1 problems
```

### Caching Implementation
```
> Use the performance-optimization agent to refactor [MODULE] adding caching layer for expensive operations
```

## Clean Code Practices

### Function Extraction
```
> Use the quality-assurance agent to refactor large functions in [FILE] into smaller, single-responsibility functions
```

### Variable Naming
```
> Use the quality-assurance agent to refactor variable and function names in [MODULE] for clarity and consistency
```

### Comments to Documentation
```
> Use the technical-documentation agent to refactor inline comments into proper documentation for [MODULE]
```

### Error Handling
```
> Use the quality-assurance agent to refactor error handling in [APPLICATION] implementing consistent patterns
```

## Dependency Management

### Dependency Updates
```
> Use the integration-setup agent to refactor [APPLICATION] updating dependencies and fixing breaking changes
```

### Dependency Injection
```
> Use the backend-services agent to refactor [MODULE] implementing dependency injection pattern
```

### Package Structure
```
> Use the backend-services agent to refactor package/module structure of [APPLICATION] improving organization
```

### Circular Dependency Resolution
```
> Use the quality-assurance agent to identify and refactor circular dependencies in [CODEBASE]
```

## Security Refactoring

### Security Vulnerability Fixes
```
> Use the security-architecture agent to refactor [MODULE] fixing identified security vulnerabilities
```

### Authentication Refactoring
```
> Use the security-architecture agent to refactor authentication system from [CURRENT] to [TARGET] method
```

### Input Sanitization
```
> Use the security-architecture agent to refactor input handling in [APPLICATION] adding proper sanitization
```

### Secrets Management
```
> Use the security-architecture agent to refactor [APPLICATION] removing hardcoded secrets using [SECRET MANAGER]
```

## Specific Refactoring Tasks

### Legacy API Migration
```
> Use the api-integration-specialist agent to refactor [APPLICATION] migrating from [OLD API] to [NEW API]
```

### Database Migration
```
> Use the database-architecture agent to refactor [APPLICATION] migrating from [OLD DB] to [NEW DB]
```

### Framework Upgrade
```
> Use the backend-services agent to refactor [APPLICATION] upgrading from [OLD VERSION] to [NEW VERSION]
```

### Build System Modernization
```
> Use the devops-engineering agent to refactor build system from [OLD TOOL] to [NEW TOOL] improving speed
```

## Variables to Replace:
- `[CODEBASE/MODULE]` - Specific code area
- `[THRESHOLD]` - Complexity number (e.g., 10)
- `[STANDARD/STYLE GUIDE]` - PEP8, ESLint, etc.
- `[CURRENT]` → `[TARGET]` - Migration path
- `[PATTERN]` - Design pattern name
- `[OLD FRAMEWORK]` → `[NEW FRAMEWORK]` - jQuery → React
- `[CURRENT]%` → `[TARGET]%` - 40% → 80%
- `[TECHNIQUE]` - Object pooling, lazy loading