# 🧠 Master Prompting Guide - Claude Code Dev Stack v2.1

## Overview
This guide enables any LLM to generate perfectly integrated prompts for the Claude Code Agent System with deterministic @agent- mention subagents, Hooks execution layer, and MCP integration. Use this in any AI chat or trigger advanced planning with "ultrathink" in Claude Code.

---

## 🎯 AIMS Meta-Prompting Methodology (Enhanced)

Every prompt must follow the **AIMS** structure:
- **A**gent: Use @agent- mentions for deterministic agent invocation
- **I**ntegration: Include MCP tools (3-5 max) and hooks
- **M**ethod: Choose slash command(s) from the 18 available  
- **S**tructure: Format for optimal execution with context preservation

### Core Formula (Updated)
```
[Slash Command] + [Context] + [@agent- mentions] + [Model Selection] + [MCP Tools] + [Hook Triggers]
```

### 🆕 Deterministic Agent Invocation
Use @agent- mentions to ensure specific subagents are called:
- `@agent-system-architect` - Forces System Architect involvement
- `@agent-backend-services` - Ensures Backend Services participation
- `@agent-testing-automation[haiku]` - Uses Haiku 3.5 for cost-effective testing

### 🆕 Model Selection Strategy
- **Opus 4**: Complex planning, architecture decisions, critical analysis
- **Haiku 3.5**: Code formatting, simple tests, documentation updates
```
@agent-business-analyst[opus] - Complex ROI analysis
@agent-quality-assurance[haiku] - Quick code style checks
```

---

## 📊 Complete Reference System

### The 28 Agents (With @agent- mentions and Model Recommendations)

#### Orchestration Layer (2)
| Agent | @agent- mention | Model | Specialty | Key Triggers | MCP Partners |
|-------|-----------|-------|-----------|--------------|--------------|
| Master Orchestrator | `@agent-master-orchestrator[opus]` | Opus 4 | Project orchestration | Complex projects, multi-agent coordination | Obsidian (documentation) |
| Usage Guide | `@agent-usage-guide[opus]` | Opus 4 | Meta-configuration | Project setup, workflow optimization | Brave Search (research) |

#### Business & Strategy (5)
| Agent | @agent- mention | Model | Specialty | Key Triggers | MCP Partners |
|-------|-----------|-------|-----------|--------------|--------------|
| Business Analyst | `@agent-business-analyst[opus]` | Opus 4 | ROI, market analysis | Business cases, feasibility | Brave Search |
| Business Tech Alignment | `@agent-business-tech-alignment[opus]` | Opus 4 | Tech-business alignment | Strategic decisions | Obsidian |
| CEO Strategy | `@agent-ceo-strategy[opus]` | Opus 4 | Strategic vision | Market positioning | Brave Search |
| Financial Analyst | `@agent-financial-analyst[opus]` | Opus 4 | Financial modeling | Unit economics, projections | None |
| Technical CTO | `@agent-technical-cto[opus]` | Opus 4 | Technical feasibility | Architecture decisions | Brave Search |

#### Development & Implementation (10)
| Agent | @agent- mention | Model | Specialty | Key Triggers | MCP Partners |
|-------|-----------|-------|-----------|--------------|--------------|
| Backend Services | `@agent-backend-services` | Default | Server-side logic | API development | Database MCPs |
| Frontend Architecture | `@agent-frontend-architecture[opus]` | Opus 4 | UI/UX architecture | Frontend design | Playwright |
| Frontend Mockup | `@agent-frontend-mockup` | Default | UI prototypes | Design implementation | Playwright |
| Production Frontend | `@agent-production-frontend` | Default | Production UI | Final implementation | Playwright |
| API Integration | `@agent-api-integration-specialist` | Default | External integrations | Third-party APIs | Various |
| Middleware Specialist | `@agent-middleware-specialist` | Default | Message queues, caching | System integration | Redis, RabbitMQ |
| Database Architecture | `@agent-database-architecture[opus]` | Opus 4 | Data modeling | Schema design | MongoDB/PostgreSQL |
| Security Architecture | `@agent-security-architecture[opus]` | Opus 4 | Security design | Compliance needs | None |
| Performance Optimization | `@agent-performance-optimization` | Default | Speed optimization | Performance issues | Playwright |
| Integration Setup | `@agent-integration-setup` | Default | Environment setup | Dependency management | Various |

#### DevOps & Automation (3)
| Agent | @agent- mention | Model | Specialty | Key Triggers | MCP Partners |
|-------|-----------|-------|-----------|--------------|--------------|
| DevOps Engineering | `@agent-devops-engineering` | Default | CI/CD pipelines | Deployment setup | Docker, Cloud MCPs |
| Script Automation | `@agent-script-automation` | Default | Automation scripts | Build/deploy scripts | Various |
| Development Prompt | `@agent-development-prompt` | Default | Prompt engineering | Workflow optimization | None |

#### Quality & Documentation (4)
| Agent | @agent- mention | Model | Specialty | Key Triggers | MCP Partners |
|-------|-----------|-------|-----------|--------------|--------------|
| Testing Automation | `@agent-testing-automation[haiku]` | Haiku 3.5 | Test implementation | Test creation | Playwright |
| Quality Assurance | `@agent-quality-assurance[haiku]` | Haiku 3.5 | Quality processes | Standards enforcement | Playwright |
| Technical Documentation | `@agent-technical-documentation[haiku]` | Haiku 3.5 | Documentation | Technical writing | Obsidian |
| Technical Specifications | `@agent-technical-specifications[opus]` | Opus 4 | Requirements specs | Architecture docs | Obsidian |

#### Project Management (2)
| Agent | @agent- mention | Model | Specialty | Key Triggers | MCP Partners |
|-------|-----------|-------|-----------|--------------|--------------|
| Project Manager | `@agent-project-manager` | Default | Project coordination | Sprint planning | Obsidian |
| Prompt Engineer | `@agent-prompt-engineer` | Default | Prompt optimization | User experience | None |

### The 18 Slash Commands (With @agent- mention Integration)

| Command | Purpose | Example with @agent- mentions | Hook Triggers |
|---------|---------|------------------------|---------------|
| `/new-project` | Complete project initialization | `/new-project "SaaS platform" @agent-master-orchestrator[opus] @agent-business-analyst[opus]` | Session state, planning |
| `/resume-project` | Continue existing project | `/resume-project @agent-master-orchestrator` | Session loader |
| `/business-analysis` | Business viability analysis | `/business-analysis @agent-business-analyst[opus] @agent-ceo-strategy[opus]` | Documentation |
| `/technical-feasibility` | Technical assessment | `/technical-feasibility "microservices" @agent-technical-cto[opus] @agent-frontend-architecture[opus]` | Planning trigger |
| `/project-plan` | Project planning | `/project-plan @agent-project-manager` | Planning phase |
| `/frontend-mockup` | UI prototypes | `/frontend-mockup "dashboard" @agent-frontend-mockup @agent-frontend-architecture` | Quality gate |
| `/backend-service` | API development | `/backend-service "auth API" @agent-backend-services @agent-security-architecture[opus]` | Quality gate |
| `/database-design` | Schema design | `/database-design @agent-database-architecture[opus]` | Quality gate |
| `/api-integration` | External API integration | `/api-integration "Stripe" @agent-api-integration-specialist` | MCP gateway |
| `/middleware-setup` | Middleware configuration | `/middleware-setup @agent-middleware-specialist` | MCP gateway |
| `/production-frontend` | Production UI | `/production-frontend @agent-production-frontend` | Quality gate |
| `/documentation` | Documentation | `/documentation @agent-technical-documentation[haiku]` | Session saver |
| `/financial-model` | Financial projections | `/financial-model @agent-financial-analyst[opus]` | Documentation |
| `/go-to-market` | GTM strategy | `/go-to-market @agent-ceo-strategy[opus] @agent-business-analyst[opus]` | Planning |
| `/requirements` | Requirements gathering | `/requirements @agent-technical-specifications[opus]` | Planning trigger |
| `/site-architecture` | Information architecture | `/site-architecture @agent-frontend-architecture[opus]` | Documentation |
| `/tech-alignment` | Technology alignment | `/tech-alignment @agent-business-tech-alignment[opus]` | Planning |
| `/prompt-enhance` | Enhance user prompts | `/prompt-enhance @agent-prompt-engineer` | User experience |

### 🆕 Context Management Features

#### Microcompact (Automatic)
- **What**: Automatically clears old tool calls when context grows long
- **When**: Triggers automatically, no action needed
- **Benefit**: Work longer without losing important project context
- **Hook Integration**: Session saver captures state before microcompact

#### PDF Reading Capability
- **Usage**: `"Read the requirements from specs.pdf"`
- **Agents**: Any agent can request PDF reading
- **Common Uses**:
  - `@agent-business-analyst[opus]` reading market reports
  - `@agent-technical-specifications[opus]` analyzing specification documents
  - `@agent-technical-documentation[haiku]` extracting documentation

### MCP Tool Tiers

#### Tier 1: Universal (Always Available)
| MCP | Purpose | Agent Partners | Install Command |
|-----|---------|----------------|-----------------|
| Playwright | Browser testing | QA, Frontend, Testing | `claude mcp add playwright npx @playwright/mcp@latest` |
| Obsidian | Knowledge base | All documentation agents | `claude mcp add obsidian` |
| Brave Search | Research | Business, Requirements | `claude mcp add brave-search` |

#### Tier 2: Project-Specific (Choose ONE per category)
| Category | Options | When to Use | Agent Partners |
|----------|---------|-------------|----------------|
| Database | MongoDB, PostgreSQL, Supabase | Based on data structure | Database Architecture |
| Deploy | GCP, Vercel, Netlify, AWS | Based on scale/stack | DevOps, Cloud |

#### Tier 3: Specialized (As Needed)
| MCP | Trigger Condition | Agent Partners |
|-----|-------------------|----------------|
| Docker | Container issues | DevOps |
| Figma Dev | Design handoff | Frontend Architecture |
| Slack | Team communication | Project Manager |

### Hook Integration Points

| Hook Type | Trigger | Purpose | Agents Affected |
|-----------|---------|---------|-----------------|
| Session Start | Claude Code launch | Load context | All agents |
| Session Stop | Claude Code exit | Save state | All agents |
| Pre-Tool Use | Before file edits | Quality checks | Development agents |
| Post-Tool Use | After file writes | Trigger workflows | Planning agents |
| User Submit | New prompts | Route to agents | Orchestration agents |

---

## 🚀 Ultrathink Planning Mode

### Activation
In Claude Code, type: `"Let's ultrathink about [complex problem]"`

### What Happens
1. **Context Loading**: All session state, agent assignments, and planning context loaded
2. **Multi-Agent Activation**: Relevant agents assembled based on problem domain
3. **MCP Tool Availability**: Appropriate MCPs ready for execution
4. **Hook Orchestration**: Automated workflows triggered
5. **Persistent Planning**: All decisions saved for future sessions

### Example Ultrathink Scenarios

#### System Architecture
```
"Let's ultrathink about migrating from monolith to microservices"
Activates: @agent-system-architect[opus] + @agent-middleware-specialist + @agent-database-architecture[opus] + @agent-devops-engineering
MCPs: Database analysis tools + Deployment planning
Hooks: Architecture documentation, migration planning triggers
```

#### Performance Crisis
```
"Let's ultrathink about our 10-second page load times"
Activates: @agent-performance-optimization + @agent-frontend-architecture[opus] + @agent-backend-services
MCPs: Playwright for testing + Database for query analysis
Hooks: Performance benchmarking, optimization workflows
```

#### Security Audit
```
"Let's ultrathink about GDPR compliance for our user data"
Activates: @agent-security-architecture[opus] + @agent-database-architecture[opus] + @agent-business-analyst[opus]
MCPs: Database inspection + Documentation
Hooks: Compliance checklist, audit trail generation
```

---

## 📋 Master Prompt Templates (Updated with @agent- mentions)

### Template 1: New Project with Full Stack
```
/new-project "[PROJECT_NAME]: [DESCRIPTION]"
@agent-master-orchestrator[opus] @agent-business-analyst[opus] @agent-frontend-architecture[opus]
Context: 
- Domain: [INDUSTRY/SECTOR]
- Users: [TARGET_AUDIENCE] 
- Scale: [EXPECTED_LOAD]
- Requirements PDF: [filename.pdf] (if available)
Requirements:
- Core features: [LIST]
- Integrations: [THIRD_PARTY_SERVICES]
- Compliance: [REGULATIONS]
Constraints:
- Timeline: [WEEKS/MONTHS]
- Budget: [AMOUNT]
- Team: [SIZE]
Tech Preferences: [STACK] or "recommend optimal stack"
MCP Setup: Tier 1 (Playwright, Obsidian, Brave) + [DATABASE_MCP] + [DEPLOY_MCP]
Hook Configuration: Full suite (session, quality, planning, orchestration)

Note: Microcompact will handle long sessions automatically
```

### Template 2: Feature Addition with Optimized Models
```
/resume-project
@agent-backend-services @agent-frontend-architecture @agent-testing-automation[haiku]
Context: Adding [FEATURE] to existing [PROJECT_NAME]
Feature Requirements:
- Functionality: [DETAILED_SPECS]
- Integration points: [EXISTING_SYSTEMS]
- Performance targets: [METRICS]
Cost Optimization: Use Haiku for testing and documentation
Quality Gates: @agent-quality-assurance[haiku] for all changes
Documentation: @agent-technical-documentation[haiku] to update guides
```

### Template 3: Complex Architecture Planning
```
"Let's ultrathink about [ARCHITECTURAL_CHALLENGE]"
@agent-frontend-architecture[opus] @agent-database-architecture[opus] @agent-security-architecture[opus]

Context: [CURRENT_ARCHITECTURE]
Challenge: [DETAILED_PROBLEM]
Constraints: [TECHNICAL/BUSINESS_CONSTRAINTS]

Read architecture docs: [architecture.pdf]
Research needed: @agent-business-analyst[opus] with Brave Search MCP

Expected Deliverables:
1. Architecture decision record (Obsidian MCP)
2. Migration plan
3. Risk assessment
4. Cost analysis (use @agent-financial-analyst[opus])
```

### Template 4: Rapid MVP Development
```
/new-project "MVP: [PROJECT_IDEA]"
@agent-master-orchestrator @agent-project-manager
Fast Track Setup:
- Use @agent-frontend-mockup for quick UI
- Use @agent-backend-services for minimal API
- Use @agent-testing-automation[haiku] for basic tests
- Use @agent-technical-documentation[haiku] for simple docs

Timeline: 2 weeks
Focus: Core functionality only
Deploy: @agent-devops-engineering with Vercel MCP
```

### Template 5: Performance Crisis Response
```
/optimize "URGENT: [PERFORMANCE_ISSUE]"
@agent-performance-optimization @agent-backend-services @agent-devops-engineering

Immediate Actions:
1. @agent-performance-optimization - Root cause analysis
2. Playwright MCP - Run performance tests
3. @agent-backend-services - Implement fixes
4. @agent-testing-automation[haiku] - Verify improvements
5. @agent-technical-documentation[haiku] - Update runbooks

Microcompact will maintain context during long debugging session
```

### 🆕 Cost-Optimized Workflow Example
```
# Complex planning with Opus
@agent-master-orchestrator[opus] @agent-frontend-architecture[opus]
"Design the overall system architecture"

# Implementation with default model
@agent-backend-services @agent-frontend-mockup
"Implement the core features"

# Lightweight tasks with Haiku
@agent-quality-assurance[haiku] @agent-testing-automation[haiku] @agent-technical-documentation[haiku]
"Review code, create tests, and document"

Result: 60% cost reduction while maintaining quality
```

---

## 🔄 Integration Patterns

### Pattern 1: Design → Build → Test → Deploy
```
Step 1: /frontend-mockup → @agent-frontend-mockup creates mockups
Step 2: /production-frontend → @agent-production-frontend implements
Step 3: MCP: Playwright tests in real browsers
Step 4: /backend-service → @agent-backend-services creates APIs
Step 5: MCP: Database setup and migration
Step 6: /test-suite → @agent-testing-automation[haiku] creates tests
Step 7: /deploy → @agent-devops-engineering handles deployment
Step 8: MCP: Deploy to chosen platform
Hooks: Quality gates at each step, session persistence throughout
```

### Pattern 2: Problem → Analysis → Solution → Implementation
```
Step 1: Identify issue → Route to appropriate analyst
Step 2: /business-analysis or /technical-feasibility
Step 3: MCP: Research with Brave Search
Step 4: Solution design with architect agents
Step 5: MCP: Document in Obsidian
Step 6: Implementation with engineering agents
Step 7: Validation with QA agents
Hooks: Planning triggers, state management
```

### Pattern 3: Continuous Improvement Cycle
```
Ongoing: Hook-driven monitoring
Trigger: Performance degradation detected
Step 1: /optimize → @agent-performance-optimization analyzes
Step 2: MCP: Playwright runs performance tests
Step 3: Recommendations generated
Step 4: /refactor → Engineers implement
Step 5: /test-suite → Validate improvements
Step 6: /documentation → Update docs
Hooks: Automated cycle based on metrics
```

---

## 💡 Advanced Techniques

### Multi-Session Orchestration
```
Session 1: Planning and architecture
- Agents establish design
- Hooks save all decisions
- MCP documents in Obsidian

Session 2: Implementation begins
- Hooks restore full context
- Agents continue from exact state
- Work proceeds seamlessly

Session N: Deployment ready
- Complete context preserved
- All decisions traceable
- Full audit trail available
```

### Cross-Agent Handoffs
```
Agent A completes task → Hook triggers handoff → Agent B notified with context → Work continues

Example:
@agent-database-architecture[opus] completes schema → 
Hook notifies @agent-backend-services → 
API development begins with schema context →
Hook notifies @agent-testing-automation[haiku] →
Test cases generated for new APIs
```

### Intelligent Routing with Context
```
User: "The app is slow"
Hook: Loads performance history
Router: Checks previous optimization attempts
Decision: Route to @agent-performance-optimization with full context
MCP: Playwright runs targeted tests
Result: Specific bottleneck identified and addressed
```

---

## 🎯 Usage in External LLMs

When using this guide in ChatGPT, Claude.ai, or other LLMs:

1. **Provide Context**:
   ```
   I'm using Claude Code Dev Stack v2.1 with:
   - 28 agents (invoked with @agent- mentions)
   - 18 slash commands
   - Model selection (Opus 4 / Haiku 3.5)
   - Hooks execution layer
   - MCP integration (3-5 tools max)
   - Automatic microcompact for long sessions
   - PDF reading capability
   
   Here's my project: [DESCRIPTION]
   ```

2. **Request Specific Prompts**:
   ```
   Using the Master Prompting Guide, create prompts that:
   - Use @agent- mentions for deterministic agent routing
   - Select appropriate models (Opus for complex, Haiku for simple)
   - Include relevant slash commands
   - Specify MCP tools needed
   - Consider PDF documents: [list any PDFs]
   ```

3. **The LLM Should Generate**:
   - Properly formatted slash commands with @agent- mentions
   - Model selections based on task complexity
   - Appropriate MCP tool selection (≤5 total)
   - Hook configuration requirements
   - Complete execution flow

### Example External LLM Request
```
Create a Claude Code prompt for building an e-commerce platform that:
- Uses @agent-master-orchestrator[opus] for system design
- Uses @agent-testing-automation[haiku] for cost-effective testing
- Reads requirements from requirements.pdf
- Integrates MongoDB and Vercel MCPs
- Sets up hooks for session continuity
```

---

## 📈 Success Patterns

### Indicators of Proper Usage
1. **Agent Utilization**: Multiple agents collaborate naturally
2. **MCP Minimalism**: Only 3-5 MCPs in use
3. **Hook Effectiveness**: Zero context loss between sessions
4. **Quality Metrics**: Automated standards enforcement working
5. **Development Velocity**: 70% faster than traditional methods

### Common Anti-Patterns to Avoid
1. ❌ Too many MCPs (>5)
2. ❌ Skipping hook setup
3. ❌ Single agent doing everything
4. ❌ Ignoring session persistence
5. ❌ Manual quality checks

---

## 🚀 Quick Start Checklist

For any new project:
1. [ ] Install Tier 1 MCPs (Playwright, Obsidian, Brave)
2. [ ] Run `/new-project` with full context
3. [ ] Let hooks establish session continuity
4. [ ] Follow agent recommendations for additional MCPs
5. [ ] Use ultrathink for complex decisions
6. [ ] Trust the orchestration

Remember: **Agents think, Hooks execute, MCPs interact with external systems**

---

## 🆕 Version 2.1 Features

### Deterministic @agent- mentions
- **What**: Use `@agent-[name]` to ensure specific agents are called
- **Why**: Guarantees the right expert handles each task
- **Example**: `@agent-frontend-architecture[opus]` for complex architecture

### Model Selection
- **Opus 4**: Complex planning, architecture, critical analysis (~$$)
- **Haiku 3.5**: Simple tasks, formatting, basic tests (~$)
- **Strategy**: Use Haiku for 60% cost reduction on routine tasks

### Microcompact
- **What**: Automatic context clearing for extended sessions
- **When**: Triggers automatically when context grows
- **Benefit**: Work for hours without manual /compact
- **Hooks**: Session state preserved before clearing

### PDF Reading
- **Usage**: `"Read requirements from spec.pdf"`
- **Agents**: All agents can request PDF analysis
- **Common**: Requirements docs, architecture diagrams, reports

### Cost Optimization Pattern
```
Planning Phase: @agent-master-orchestrator[opus] @agent-frontend-architecture[opus]
Implementation: @agent-backend-services @agent-frontend-mockup (default model)
Quality/Docs: @agent-quality-assurance[haiku] @agent-technical-documentation[haiku]
Result: Premium quality at 40% lower cost
```

---

*This guide version: 2.1 | Compatible with Claude Code + @agent- mentions + Hooks + MCP | Last updated with Anthropic's latest features*