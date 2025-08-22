# V3.6.9 Complete Directory Structure

## Overview
Complete directory hierarchy for Claude Code Agents V3.6.9 with tier-based organization, specialized components, and comprehensive categorization.

## Tier-Based Agent Organization

### Tier 0 - Strategic Level
```
tier0/
├── master-orchestrator/
│   ├── configs/
│   ├── templates/
│   └── workflows/
└── system-architecture/
    ├── blueprints/
    ├── schemas/
    └── patterns/
```

### Tier 1 - Leadership Level
```
tier1/
├── technical-lead/
│   ├── specifications/
│   ├── reviews/
│   └── standards/
├── security-architect/
│   ├── policies/
│   ├── audits/
│   └── compliance/
└── devops-engineer/
    ├── infrastructure/
    ├── pipelines/
    └── monitoring/
```

### Tier 2 - Specialist Level
```
tier2/
├── backend-specialist/
│   ├── apis/
│   ├── services/
│   └── middleware/
├── frontend-specialist/
│   ├── components/
│   ├── pages/
│   └── styles/
├── database-specialist/
│   ├── schemas/
│   ├── migrations/
│   └── queries/
├── testing-specialist/
│   ├── unit-tests/
│   ├── integration-tests/
│   └── e2e-tests/
├── integration-setup/
│   ├── environments/
│   ├── dependencies/
│   └── configurations/
├── middleware-specialist/
│   ├── auth/
│   ├── logging/
│   └── validation/
└── bmad-specialists/
    ├── browser-automation-specialist/
    │   ├── scripts/
    │   ├── configs/
    │   └── tests/
    ├── marketing-automation-specialist/
    │   ├── campaigns/
    │   ├── analytics/
    │   └── templates/
    ├── analytics-data-specialist/
    │   ├── dashboards/
    │   ├── reports/
    │   └── pipelines/
    └── deployment-specialist/
        ├── strategies/
        ├── rollback/
        └── monitoring/
```

### Tier 3 - Implementation Level
```
tier3/
├── script-automation/
│   ├── generators/
│   ├── validators/
│   └── executors/
├── frontend-mockup/
│   ├── wireframes/
│   ├── prototypes/
│   └── assets/
├── production-frontend/
│   ├── builds/
│   ├── optimizations/
│   └── deployments/
├── ui-ux-design/
│   ├── designs/
│   ├── user-flows/
│   └── style-guides/
├── content-creation/
│   ├── documentation/
│   ├── tutorials/
│   └── guides/
└── performance-optimization/
    ├── benchmarks/
    ├── profiling/
    └── optimizations/
```

## Hook System Organization (12 Categories)

```
hooks/
├── pre-commit/           # Pre-commit validation hooks
├── post-commit/          # Post-commit processing hooks
├── pre-push/             # Pre-push validation hooks
├── post-push/            # Post-push processing hooks
├── pre-receive/          # Pre-receive server hooks
├── post-receive/         # Post-receive server hooks
├── pre-merge/            # Pre-merge validation hooks
├── post-merge/           # Post-merge processing hooks
├── deployment/           # Deployment-specific hooks
├── testing/              # Testing automation hooks
├── security/             # Security validation hooks
└── monitoring/           # Monitoring and alerting hooks
```

## PWA Component Structure

```
pwa/
├── components/           # Reusable PWA components
├── service-workers/      # Service worker implementations
├── manifest/             # PWA manifest configurations
├── icons/                # PWA icon assets
├── offline-cache/        # Offline caching strategies
├── push-notifications/   # Push notification handlers
├── background-sync/      # Background sync implementations
└── installation/         # PWA installation prompts
```

## Docker Services Architecture

```
docker-services/
├── web/                  # Web server services
├── api/                  # API gateway services
├── database/             # Database services
├── cache/                # Caching services
├── message-queue/        # Message queue services
├── monitoring/           # Monitoring services
├── reverse-proxy/        # Reverse proxy services
└── storage/              # Storage services
```

## Shared Resources Organization

```
shared/
├── constants/            # Shared constants
├── interfaces/           # TypeScript interfaces
├── types/                # Type definitions
└── validators/           # Validation schemas

templates/
├── agents/               # Agent templates
├── components/           # Component templates
├── services/             # Service templates
└── workflows/            # Workflow templates

utilities/
├── build-tools/          # Build utilities
├── deployment-scripts/   # Deployment utilities
├── monitoring-tools/     # Monitoring utilities
└── testing-helpers/      # Testing utilities

workflows/
├── ci-cd/                # CI/CD workflows
├── deployment/           # Deployment workflows
├── testing/              # Testing workflows
└── security/             # Security workflows
```

## Directory Usage Guidelines

### Naming Conventions
- Use kebab-case for directory names
- Use descriptive, meaningful names
- Keep names concise but clear
- Follow consistent patterns across tiers

### Organization Principles
- **Tier 0**: Strategic oversight and architecture
- **Tier 1**: Leadership and cross-cutting concerns
- **Tier 2**: Domain specialists and BMAD components
- **Tier 3**: Implementation and execution

### Access Patterns
- Each tier can delegate to lower tiers
- Shared resources accessible by all tiers
- Templates provide consistent starting points
- Utilities support cross-cutting functionality

### Integration Points
- Hooks provide event-driven integration
- PWA components enable progressive web app features
- Docker services support containerized deployment
- Workflows orchestrate complex processes

## Maintenance Notes
- Keep directory structure aligned with agent hierarchy
- Update organization as new specialists are added
- Maintain clear separation of concerns
- Document any structural changes

## Version History
- V3.6.9: Complete directory hierarchy established
- Tier-based organization implemented
- BMAD specialists categorized
- Hook system structured
- PWA components organized
- Docker services architected