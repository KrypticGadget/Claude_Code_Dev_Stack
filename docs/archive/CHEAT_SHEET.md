# 🚀 Claude Code Agent System - Quick Reference

## 🎯 START ANY PROJECT IN SECONDS

### With Agents
```bash
> Use the master-orchestrator agent to begin new project: "Your project description"
```

### With Slash Commands (Even Faster!)
```bash
/new-project "Your project description"
```

## ⚡ MOST COMMON COMMANDS

### 🚀 Project Initialization
```bash
# Full project with business analysis
> Use the master-orchestrator agent to begin new project: "E-commerce platform"
# OR
/new-project "E-commerce platform"

# Quick business analysis only
/business-analysis

# Technical feasibility check
/technical-feasibility "your concept" scale:"10000 users"
```

### 💼 Business & Strategy
```bash
# ROI and market analysis
> Use the business-analyst agent to analyze market opportunity
# OR
/business-analysis

# Financial projections
/financial-model "SaaS" pricing:"$99/month" market:"B2B"

# Go-to-market strategy
/go-to-market "product name" market:"target market"
```

### 🏗️ Development
```bash
# Frontend mockup
/frontend-mockup "landing page for SaaS"

# Production frontend
/production-frontend "React dashboard" features:"charts, auth, API"

# Backend API
/backend-service "REST API for user management"

# Database design
/database-design "multi-tenant SaaS schema"
```

### 🔌 Integration & Infrastructure
```bash
# External API integration
/api-integration "Stripe" requirements:"payments and subscriptions"

# Message queue setup
/middleware-setup "RabbitMQ" usecase:"async processing"

# Documentation
/documentation "my project" type:"API reference"
```

## 🎪 THE 28 AGENTS - QUICK REFERENCE

### Orchestration (2)
- `master-orchestrator` - Manages entire projects
- `prompt-engineer` - Enhances your prompts

### Business & Strategy (4)
- `business-analyst` - ROI, market analysis
- `technical-cto` - Tech feasibility
- `ceo-strategy` - Go-to-market
- `financial-analyst` - Financial models

### Project Management (3)
- `project-manager` - Timelines, resources
- `technical-specifications` - Requirements
- `business-tech-alignment` - Align tech/business

### Architecture & Design (8)
- `technical-documentation` - System docs
- `api-integration-specialist` - External APIs
- `frontend-architecture` - UI/UX structure
- `frontend-mockup` - Prototypes
- `production-frontend` - React/Vue/Angular
- `backend-services` - APIs, services
- `database-architecture` - Data modeling
- `middleware-specialist` - Queues, caching

### Development Support (6)
- `testing-automation` - Test creation
- `development-prompt` - Dev workflows
- `script-automation` - Build scripts
- `integration-setup` - Environment
- `security-architecture` - Security
- `performance-optimization` - Speed

### Specialized (5)
- `devops-engineering` - CI/CD
- `quality-assurance` - Code quality
- `mobile-development` - iOS/Android
- `ui-ux-design` - User experience
- `usage-guide` - Documentation

## 📋 COMMON WORKFLOWS

### 1. Full Stack Application
```bash
/new-project "Task management app with team collaboration"
# Orchestrator handles: business analysis → tech planning → development
```

### 2. Quick MVP (6 weeks)
```bash
> Use the master-orchestrator agent to begin new project: "MVP for meal planning app, 6 week deadline, essential features only"
```

### 3. Enterprise System
```bash
> Use the master-orchestrator agent to begin new project: "Enterprise CRM for 5000 users, SSO, compliance required, 6 month timeline"
```

### 4. API Service
```bash
/backend-service "REST API" requirements:"authentication, rate limiting"
/database-design "API data model"
/documentation "API" type:"OpenAPI spec"
```

### 5. Quick Frontend
```bash
/frontend-mockup "dashboard for analytics"
/production-frontend "React" features:"from mockup"
```

## 🔥 POWER USER TIPS

### Parallel Development
```bash
# Agents work in parallel automatically
/new-project "Full platform"
# Frontend team starts mockups while backend designs APIs
```

### Quick Iterations
```bash
# Start with mockup
/frontend-mockup "idea visualization"

# Get feedback, then build
/production-frontend "approved mockup"
```

### Enhance Any Request
```bash
/prompt-enhance "vague development request"
# Returns optimized prompt for better results
```

## 📊 BY PROJECT TYPE

### SaaS Platform
```bash
/new-project "Multi-tenant SaaS with subscription billing"
```

### Mobile App
```bash
> Use the master-orchestrator agent to begin new project: "Cross-platform mobile app for fitness tracking"
```

### E-commerce
```bash
/new-project "E-commerce with inventory and payment processing"
```

### API Platform
```bash
> Use the backend-services agent to design API platform with microservices
```

## 🚨 QUICK FIXES

### Debug Issue
```bash
> Use the quality-assurance agent to debug login authentication problem
```

### Performance
```bash
> Use the performance-optimization agent to improve page load from 3s to under 1s
```

### Security Audit
```bash
> Use the security-architecture agent to audit authentication system
```

### Add Feature
```bash
> Use the backend-services agent to add email notification system
```

## 💡 SLASH COMMAND VARIABLES

Commands support dynamic variables:
```bash
/project-plan "Mobile App" team:3 budget:50k deadline:"2 months"
/financial-model "SaaS" pricing:"tiered" horizon:"5 years"
/technical-feasibility "blockchain app" scale:"1M users" constraints:"AWS only"
```

## 🎯 DECISION POINTS

The orchestrator pauses for your input at:
1. **Business Approval** - After ROI/feasibility analysis
2. **Architecture Review** - After technical design
3. **Development Milestones** - At key checkpoints

## ⏱️ TYPICAL TIMELINES

- **MVP**: 4-6 weeks
- **Full App**: 3-4 months  
- **Platform**: 6-9 months
- **Enterprise**: 9-12 months

## 🔧 INSTALLATION

### Agents (Required)
```bash
curl -sL https://raw.githubusercontent.com/yourusername/claude-code-agent-system/main/install.sh | bash
```

### Slash Commands (Recommended)
```bash
curl -sL https://raw.githubusercontent.com/yourusername/claude-code-agent-system/main/slash-commands/install-commands.sh | bash
```

## 📚 MORE INFO

- **Full Docs**: See `/docs/` directory
- **Examples**: Check `/examples/` for real projects
- **Prompts**: Browse `/master-prompts/` for templates
- **Custom Commands**: Create your own in `~/.claude/commands/`

---

**Remember**: Start with `/new-project` or the master-orchestrator for complete projects, or use specific agents/commands for targeted tasks!