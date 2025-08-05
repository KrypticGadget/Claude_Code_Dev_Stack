# 🧠 Master Prompting Guide - Claude Code Dev Stack v2.1

## Overview
This guide enables any LLM to generate perfectly integrated prompts for the Claude Code Agent System with deterministic @-mention subagents, Hooks execution layer, and MCP integration. Use this in any AI chat or trigger advanced planning with "ultrathink" in Claude Code.

---

## 🎯 AIMS Meta-Prompting Methodology (Enhanced)

Every prompt must follow the **AIMS** structure:
- **A**gent: Use @-mentions for deterministic agent invocation
- **I**ntegration: Include MCP tools (3-5 max) and hooks
- **M**ethod: Choose slash command(s) from the 18 available  
- **S**tructure: Format for optimal execution with context preservation

### Core Formula (Updated)
```
[Slash Command] + [Context] + [@agent mentions] + [Model Selection] + [MCP Tools] + [Hook Triggers]
```

### 🆕 Deterministic Agent Invocation
Use @-mentions to ensure specific subagents are called:
- `@system-architect` - Forces System Architect involvement
- `@backend-engineer` - Ensures Backend Engineer participation
- `@testing-engineer[haiku]` - Uses Haiku 3.5 for cost-effective testing

### 🆕 Model Selection Strategy
- **Opus 4**: Complex planning, architecture decisions, critical analysis
- **Haiku 3.5**: Code formatting, simple tests, documentation updates
```
@business-analyst[opus] - Complex ROI analysis
@code-reviewer[haiku] - Quick code style checks
```

---

## 📊 Complete Reference System

### The 28 Agents (With @-mentions and Model Recommendations)

#### Orchestration Layer (2)
| Agent | @-mention | Model | Specialty | Key Triggers | MCP Partners |
|-------|-----------|-------|-----------|--------------|--------------|
| AI Architect | `@ai-architect[opus]` | Opus 4 | System design & coordination | Complex projects, architecture decisions | Obsidian (documentation) |
| Project Init Specialist | `@project-init[opus]` | Opus 4 | Project bootstrapping | New projects, major pivots | Brave Search (research) |

#### Business & Strategy (4)
| Agent | @-mention | Model | Specialty | Key Triggers | MCP Partners |
|-------|-----------|-------|-----------|--------------|--------------|
| Business Analyst | `@business-analyst[opus]` | Opus 4 | ROI, market analysis | Business cases, feasibility | Brave Search |
| Strategic Advisor | `@strategic-advisor[opus]` | Opus 4 | Long-term planning | Strategic decisions | Obsidian |
| Product Manager | `@product-manager` | Either | Feature prioritization | Product roadmap | Obsidian |
| Technical Feasibility | `@tech-feasibility[opus]` | Opus 4 | Technical assessment | New technologies | Brave Search |

#### Project Management (3)
| Agent | @-mention | Model | Specialty | Key Triggers | MCP Partners |
|-------|-----------|-------|-----------|--------------|--------------|
| Scrum Master | `@scrum-master[haiku]` | Haiku 3.5 | Agile processes | Sprint planning | None |
| PMO Coordinator | `@pmo-coordinator` | Either | Project coordination | Multi-team projects | Obsidian |
| Iteration Specialist | `@iteration-specialist` | Either | Refinement cycles | Feature iterations | None |

#### Architecture & Design (8)
| Agent | @-mention | Model | Specialty | Key Triggers | MCP Partners |
|-------|-----------|-------|-----------|--------------|--------------|
| System Architect | `@system-architect[opus]` | Opus 4 | High-level design | System architecture | Obsidian |
| Solution Architect | `@solution-architect[opus]` | Opus 4 | Technical solutions | Integration challenges | Database MCPs |
| Frontend Architect | `@frontend-architect` | Either | UI/UX architecture | Frontend design | Playwright, Figma |
| Backend Engineer | `@backend-engineer` | Either | Server-side logic | API development | Database MCPs |
| Database Architect | `@database-architect[opus]` | Opus 4 | Data modeling | Schema design | MongoDB/PostgreSQL |
| API Gateway Specialist | `@api-gateway` | Either | API design | Microservices | None |
| Cloud Infrastructure | `@cloud-infrastructure` | Either | Cloud architecture | Deployment | GCP/AWS/Vercel |
| Security Architect | `@security-architect[opus]` | Opus 4 | Security design | Compliance needs | None |

#### Development Support (6)
| Agent | @-mention | Model | Specialty | Key Triggers | MCP Partners |
|-------|-----------|-------|-----------|--------------|--------------|
| DevOps Automation | `@devops-automation` | Either | CI/CD pipelines | Deployment setup | Docker, Cloud MCPs |
| Integration Specialist | `@integration-specialist` | Either | System integration | Third-party APIs | Various |
| Performance Specialist | `@performance-specialist[opus]` | Opus 4 | Optimization | Performance issues | Playwright |
| Code Reviewer | `@code-reviewer[haiku]` | Haiku 3.5 | Code quality | PR reviews | None |
| Documentation Specialist | `@documentation[haiku]` | Haiku 3.5 | Technical writing | Documentation needs | Obsidian |
| Technical Writer | `@technical-writer[haiku]` | Haiku 3.5 | User guides | External docs | Obsidian |

#### Quality & Testing (5)
| Agent | @-mention | Model | Specialty | Key Triggers | MCP Partners |
|-------|-----------|-------|-----------|--------------|--------------|
| QA Lead | `@qa-lead` | Either | Test strategy | Quality planning | Playwright |
| Testing Engineer | `@testing-engineer[haiku]` | Haiku 3.5 | Test implementation | Test creation | Playwright |
| Requirements Analyst | `@requirements-analyst` | Either | Requirements gathering | Spec definition | Brave Search |
| Quality Assurance | `@quality-assurance` | Either | Quality processes | Standards enforcement | None |
| UI/UX Designer | `@ui-ux-designer` | Either | Design systems | Interface design | Figma |

### The 18 Slash Commands (With @-mention Integration)

| Command | Purpose | Example with @-mentions | Hook Triggers |
|---------|---------|------------------------|---------------|
| `/new-project` | Complete project initialization | `/new-project "SaaS platform" @ai-architect[opus] @business-analyst[opus]` | Session state, planning |
| `/resume-project` | Continue existing project | `/resume-project @project-init` | Session loader |
| `/business-analysis` | Business viability analysis | `/business-analysis @business-analyst[opus] @strategic-advisor[opus]` | Documentation |
| `/technical-feasibility` | Technical assessment | `/technical-feasibility "microservices" @tech-feasibility[opus] @system-architect[opus]` | Planning trigger |
| `/project-plan` | Project planning | `/project-plan @pmo-coordinator @scrum-master[haiku]` | Planning phase |
| `/frontend-mockup` | UI prototypes | `/frontend-mockup "dashboard" @frontend-architect @ui-ux-designer` | Quality gate |
| `/backend-service` | API development | `/backend-service "auth API" @backend-engineer @security-architect[opus]` | Quality gate |
| `/database-design` | Schema design | `/database-design @database-architect[opus]` | Quality gate |
| `/cloud-setup` | Infrastructure | `/cloud-setup "AWS" @cloud-infrastructure @devops-automation` | MCP gateway |
| `/deploy` | Deployment | `/deploy "production" @devops-automation` | MCP gateway |
| `/code-review` | Code review | `/code-review @code-reviewer[haiku]` | Quality gate |
| `/security-audit` | Security check | `/security-audit @security-architect[opus]` | Quality gate |
| `/optimize` | Performance | `/optimize @performance-specialist[opus]` | Testing |
| `/test-suite` | Test creation | `/test-suite @testing-engineer[haiku] @qa-lead` | Test runner |
| `/refactor` | Code refactoring | `/refactor "payment module" @backend-engineer @code-reviewer[haiku]` | Quality gate |
| `/integration` | System integration | `/integration "Stripe" @integration-specialist` | MCP gateway |
| `/documentation` | Documentation | `/documentation @documentation[haiku] @technical-writer[haiku]` | Session saver |
| `/ui-design` | Interface design | `/ui-design @ui-ux-designer @frontend-architect` | Quality gate |

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
  - `@requirements-analyst` reading specification documents
  - `@business-analyst[opus]` analyzing market reports
  - `@technical-writer[haiku]` extracting documentation

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
| Database | MongoDB, PostgreSQL, Supabase | Based on data structure | Database Architect |
| Deploy | GCP, Vercel, Netlify, AWS | Based on scale/stack | DevOps, Cloud |

#### Tier 3: Specialized (As Needed)
| MCP | Trigger Condition | Agent Partners |
|-----|-------------------|----------------|
| Docker | Container issues | DevOps |
| Figma Dev | Design handoff | UI/UX Designer |
| Slack | Team communication | PMO Coordinator |

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
Activates: System Architect + Cloud Infrastructure + Database Architect + DevOps
MCPs: Database analysis tools + Deployment planning
Hooks: Architecture documentation, migration planning triggers
```

#### Performance Crisis
```
"Let's ultrathink about our 10-second page load times"
Activates: Performance Specialist + Frontend Architect + Backend Engineer
MCPs: Playwright for testing + Database for query analysis
Hooks: Performance benchmarking, optimization workflows
```

#### Security Audit
```
"Let's ultrathink about GDPR compliance for our user data"
Activates: Security Architect + Database Architect + Business Analyst
MCPs: Database inspection + Documentation
Hooks: Compliance checklist, audit trail generation
```

---

## 📋 Master Prompt Templates (Updated with @-mentions)

### Template 1: New Project with Full Stack
```
/new-project "[PROJECT_NAME]: [DESCRIPTION]"
@ai-architect[opus] @business-analyst[opus] @system-architect[opus]
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
@backend-engineer @frontend-architect @testing-engineer[haiku]
Context: Adding [FEATURE] to existing [PROJECT_NAME]
Feature Requirements:
- Functionality: [DETAILED_SPECS]
- Integration points: [EXISTING_SYSTEMS]
- Performance targets: [METRICS]
Cost Optimization: Use Haiku for testing and documentation
Quality Gates: @code-reviewer[haiku] for all changes
Documentation: @documentation[haiku] to update guides
```

### Template 3: Complex Architecture Planning
```
"Let's ultrathink about [ARCHITECTURAL_CHALLENGE]"
@system-architect[opus] @solution-architect[opus] @database-architect[opus] @security-architect[opus]

Context: [CURRENT_ARCHITECTURE]
Challenge: [DETAILED_PROBLEM]
Constraints: [TECHNICAL/BUSINESS_CONSTRAINTS]

Read architecture docs: [architecture.pdf]
Research needed: @requirements-analyst with Brave Search MCP

Expected Deliverables:
1. Architecture decision record (Obsidian MCP)
2. Migration plan
3. Risk assessment
4. Cost analysis (use @business-analyst[opus])
```

### Template 4: Rapid MVP Development
```
/new-project "MVP: [PROJECT_IDEA]"
@project-init @product-manager
Fast Track Setup:
- Use @frontend-architect for quick UI
- Use @backend-engineer for minimal API
- Use @testing-engineer[haiku] for basic tests
- Use @documentation[haiku] for simple docs

Timeline: 2 weeks
Focus: Core functionality only
Deploy: @devops-automation with Vercel MCP
```

### Template 5: Performance Crisis Response
```
/optimize "URGENT: [PERFORMANCE_ISSUE]"
@performance-specialist[opus] @backend-engineer @devops-automation

Immediate Actions:
1. @performance-specialist[opus] - Root cause analysis
2. Playwright MCP - Run performance tests
3. @backend-engineer - Implement fixes
4. @testing-engineer[haiku] - Verify improvements
5. @documentation[haiku] - Update runbooks

Microcompact will maintain context during long debugging session
```

### 🆕 Cost-Optimized Workflow Example
```
# Complex planning with Opus
@ai-architect[opus] @system-architect[opus]
"Design the overall system architecture"

# Implementation with default model
@backend-engineer @frontend-architect
"Implement the core features"

# Lightweight tasks with Haiku
@code-reviewer[haiku] @testing-engineer[haiku] @documentation[haiku]
"Review code, create tests, and document"

Result: 60% cost reduction while maintaining quality
```

---

## 🔄 Integration Patterns

### Pattern 1: Design → Build → Test → Deploy
```
Step 1: /ui-design → UI/UX Designer creates mockups
Step 2: /frontend-mockup → Frontend Architect implements
Step 3: MCP: Playwright tests in real browsers
Step 4: /backend-service → Backend Engineer creates APIs
Step 5: MCP: Database setup and migration
Step 6: /test-suite → Testing Engineer creates tests
Step 7: /deploy → DevOps handles deployment
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
Step 1: /optimize → Performance Specialist analyzes
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
Database Architect completes schema → 
Hook notifies Backend Engineer → 
API development begins with schema context →
Hook notifies Testing Engineer →
Test cases generated for new APIs
```

### Intelligent Routing with Context
```
User: "The app is slow"
Hook: Loads performance history
Router: Checks previous optimization attempts
Decision: Route to Performance Specialist with full context
MCP: Playwright runs targeted tests
Result: Specific bottleneck identified and addressed
```

---

## 🎯 Usage in External LLMs

When using this guide in ChatGPT, Claude.ai, or other LLMs:

1. **Provide Context**:
   ```
   I'm using Claude Code Dev Stack v2.1 with:
   - 28 agents (invoked with @-mentions)
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
   - Use @-mentions for deterministic agent routing
   - Select appropriate models (Opus for complex, Haiku for simple)
   - Include relevant slash commands
   - Specify MCP tools needed
   - Consider PDF documents: [list any PDFs]
   ```

3. **The LLM Should Generate**:
   - Properly formatted slash commands with @-mentions
   - Model selections based on task complexity
   - Appropriate MCP tool selection (≤5 total)
   - Hook configuration requirements
   - Complete execution flow

### Example External LLM Request
```
Create a Claude Code prompt for building an e-commerce platform that:
- Uses @ai-architect[opus] for system design
- Uses @testing-engineer[haiku] for cost-effective testing
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

### Deterministic @-mentions
- **What**: Use `@agent-name` to ensure specific agents are called
- **Why**: Guarantees the right expert handles each task
- **Example**: `@system-architect[opus]` for complex architecture

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
Planning Phase: @ai-architect[opus] @system-architect[opus]
Implementation: @backend-engineer @frontend-architect (default model)
Quality/Docs: @code-reviewer[haiku] @documentation[haiku]
Result: Premium quality at 40% lower cost
```

---

*This guide version: 2.1 | Compatible with Claude Code + @-mentions + Hooks + MCP | Last updated with Anthropic's latest features*