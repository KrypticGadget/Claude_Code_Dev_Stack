# Agent Quick Reference - Claude Code Agent System

Quick reference for all 28 agents with invocation patterns and common use cases.

## 🎯 Orchestration & Coordination

### master-orchestrator
**Invocation:** `> Use the master-orchestrator agent to begin new project: "[description]"`
**Common Uses:**
- Starting new projects
- Coordinating multi-agent workflows
- Managing project lifecycle
- Handling complex requirements

### prompt-engineer
**Invocation:** `> Use the prompt-engineer agent to enhance: "[your prompt]"`
**Common Uses:**
- Improving vague requests
- Adding technical context
- Optimizing for specific agents
- Clarifying requirements

## 💼 Business & Strategy

### business-analyst
**Invocation:** `> Use the business-analyst agent to analyze [market/opportunity/ROI]`
**Common Uses:**
- Market opportunity assessment
- Competitive analysis
- ROI calculations
- Business case development

### technical-cto
**Invocation:** `> Use the technical-cto agent to assess [technical feasibility/architecture]`
**Common Uses:**
- Technology evaluation
- Scalability assessment
- Architecture decisions
- Tech stack selection

### ceo-strategy
**Invocation:** `> Use the ceo-strategy agent to develop [strategy/positioning/pricing]`
**Common Uses:**
- Go-to-market strategy
- Product positioning
- Pricing models
- Partnership strategy

### financial-analyst
**Invocation:** `> Use the financial-analyst agent to calculate [projections/metrics/analysis]`
**Common Uses:**
- Financial modeling
- Unit economics
- Budget planning
- Investment analysis

## 📋 Project Management

### project-manager
**Invocation:** `> Use the project-manager agent to create [timeline/plan/schedule]`
**Common Uses:**
- Project planning
- Resource allocation
- Sprint management
- Risk assessment

### technical-specifications
**Invocation:** `> Use the technical-specifications agent to document [requirements/specs]`
**Common Uses:**
- Requirements gathering
- API specifications
- System design docs
- Technical proposals

### business-tech-alignment
**Invocation:** `> Use the business-tech-alignment agent to align [tech decisions with business goals]`
**Common Uses:**
- Technology ROI analysis
- Cost-benefit evaluation
- Strategic alignment
- Trade-off decisions

## 🏗️ Architecture & Design

### technical-documentation
**Invocation:** `> Use the technical-documentation agent to create [docs/guides/references]`
**Common Uses:**
- Architecture documentation
- API documentation
- Developer guides
- System manuals

### api-integration-specialist
**Invocation:** `> Use the api-integration-specialist agent to integrate [service/API/webhook]`
**Common Uses:**
- Third-party integrations
- Webhook implementation
- API gateway design
- Service connections

### frontend-architecture
**Invocation:** `> Use the frontend-architecture agent to design [UI structure/user flows]`
**Common Uses:**
- Information architecture
- Site mapping
- Navigation design
- Component hierarchy

### frontend-mockup
**Invocation:** `> Use the frontend-mockup agent to create [prototype/wireframe/mockup]`
**Common Uses:**
- HTML/CSS prototypes
- Design mockups
- Interactive demos
- UI concepts

### production-frontend
**Invocation:** `> Use the production-frontend agent to build [React/Vue/Angular app]`
**Common Uses:**
- Frontend implementation
- Component development
- State management
- Performance optimization

### backend-services
**Invocation:** `> Use the backend-services agent to develop [API/service/backend]`
**Common Uses:**
- API development
- Business logic
- Microservices
- Server architecture

### database-architecture
**Invocation:** `> Use the database-architecture agent to design [schema/database/queries]`
**Common Uses:**
- Schema design
- Query optimization
- Data modeling
- Migration planning

### middleware-specialist
**Invocation:** `> Use the middleware-specialist agent to implement [queues/cache/integration]`
**Common Uses:**
- Message queues
- Caching layers
- Event streaming
- Service mesh

## 💻 Development Support

### testing-automation
**Invocation:** `> Use the testing-automation agent to create [tests/coverage/strategies]`
**Common Uses:**
- Test strategy
- Unit tests
- Integration tests
- E2E tests

### development-prompt
**Invocation:** `> Use the development-prompt agent to generate [commands/workflows]`
**Common Uses:**
- Development workflows
- Command sequences
- Automation scripts
- Process documentation

### script-automation
**Invocation:** `> Use the script-automation agent to create [scripts/automation/tools]`
**Common Uses:**
- Build scripts
- Deployment scripts
- Setup automation
- CI/CD scripts

### integration-setup
**Invocation:** `> Use the integration-setup agent to setup [environment/dependencies]`
**Common Uses:**
- Environment setup
- Dependency management
- Configuration
- Troubleshooting

### security-architecture
**Invocation:** `> Use the security-architecture agent to implement [security/audit/compliance]`
**Common Uses:**
- Security audits
- Threat modeling
- Compliance checks
- Authentication

### performance-optimization
**Invocation:** `> Use the performance-optimization agent to optimize [speed/efficiency/scale]`
**Common Uses:**
- Performance profiling
- Speed optimization
- Resource usage
- Scalability

## 🔧 Specialized Expertise

### devops-engineering
**Invocation:** `> Use the devops-engineering agent to setup [CI/CD/infrastructure]`
**Common Uses:**
- Pipeline creation
- Infrastructure setup
- Container orchestration
- Monitoring

### quality-assurance
**Invocation:** `> Use the quality-assurance agent to review [code/quality/standards]`
**Common Uses:**
- Code reviews
- Quality metrics
- Best practices
- Technical debt

### mobile-development
**Invocation:** `> Use the mobile-development agent to build [iOS/Android/cross-platform]`
**Common Uses:**
- Mobile apps
- Native features
- App store prep
- Cross-platform

### ui-ux-design
**Invocation:** `> Use the ui-ux-design agent to design [interface/experience/flow]`
**Common Uses:**
- User research
- Design systems
- Accessibility
- Usability testing

### usage-guide
**Invocation:** `> Use the usage-guide agent to create [user docs/tutorials/guides]`
**Common Uses:**
- User manuals
- Getting started
- Feature guides
- Best practices

## 🚀 Common Workflows

### New Project
```
1. master-orchestrator → Start project
2. business-analyst → Market analysis
3. technical-cto → Tech feasibility
4. project-manager → Planning
5. [Development agents] → Implementation
```

### Add Feature
```
1. technical-specifications → Requirements
2. frontend/backend agents → Implementation
3. testing-automation → Tests
4. usage-guide → Documentation
```

### Fix Issue
```
1. quality-assurance → Investigate
2. Relevant dev agent → Fix
3. testing-automation → Verify
4. devops-engineering → Deploy
```

### Optimize Performance
```
1. performance-optimization → Analysis
2. database-architecture → DB optimization
3. backend-services → Code optimization
4. devops-engineering → Infrastructure
```

## 💡 Pro Tips

1. **Start with master-orchestrator** for new projects
2. **Use prompt-engineer** when unsure how to phrase requests
3. **Combine agents** for complex tasks
4. **Be specific** about requirements and constraints
5. **Include context** about existing systems

---

Quick reminder: Replace `[bracketed items]` with your specific requirements when using these patterns!