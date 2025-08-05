# 🧠 Universal Meta-Prompting Guide v2.1 - Claude Code Dev Stack

## The Definitive Guide for Generating Perfect Claude Code Prompts in Any LLM

---

## 🎯 Universal LLM Instructions

**Give this guide to any AI assistant (ChatGPT, Claude.ai, Gemini, Perplexity, etc.) with these instructions:**

```
I need you to generate Claude Code prompts using this guide. Please:
1. Always use @agent- prefix for deterministic agent routing
2. Select agents based on their model recommendations for cost optimization
3. Include relevant slash commands from the 18 available
4. Consider that Opus costs ~7x more than Haiku
5. Generate prompts that will work in Claude Code's interactive environment
6. Follow the AIMS methodology exactly as specified
```

---

## 📋 Quick Reference - What Changed in v2.1

### ❌ OLD Syntax (Pre-v2.1)
```
@agent-backend-services[opus]    # Model specified inline
@agent-testing-engineer[haiku]   # Model in brackets
```

### ✅ NEW Syntax (v2.1)
```
@agent-backend-services          # Model set in agent config
@agent-testing-automation        # Automatic model selection
```

**Key Change**: Models are now configured in each agent's YAML file, not specified inline. This ensures consistent cost optimization across all uses of an agent.

---

## 🏗️ AIMS Meta-Prompting Methodology v2.1

Every Claude Code prompt must follow the **AIMS** structure:

### A - Agent Selection (Deterministic with @agent-)
- Use exact agent names from configuration
- Pattern: `@agent-[exact-name-from-config]`
- NO square brackets or model specifications
- Let agent config determine optimal model

### I - Integration
- Maximum 3 MCP tools: Playwright, Obsidian, Brave Search
- Hooks execute automatically (no manual configuration needed)
- PDF reading available to all agents

### M - Method
- Choose from 18 slash commands
- Commands set context and workflow
- Can combine with @agent- mentions for precision

### S - Structure
- Clear, actionable instructions
- Cost-aware agent selection
- Session-aware (microcompact handles long sessions)

---

## 📊 Complete Agent Reference Table v2.1

### All 28 Agents with Model Assignments

| Agent Name | @agent- Invocation | Model | Use For | Cost |
|------------|-------------------|-------|---------|------|
| **Master Orchestrator** | `@agent-master-orchestrator` | Opus | Complex project coordination | $$$ |
| **Usage Guide** | `@agent-usage-guide` | Opus | Meta-configuration, workflow optimization | $$$ |
| **API Integration Specialist** | `@agent-api-integration-specialist` | Default | External API integration | $$ |
| **Backend Services** | `@agent-backend-services` | Default | Server-side development | $$ |
| **Business Analyst** | `@agent-business-analyst` | Opus | Market analysis, ROI calculations | $$$ |
| **Business Tech Alignment** | `@agent-business-tech-alignment` | Opus | Align tech with business goals | $$$ |
| **CEO Strategy** | `@agent-ceo-strategy` | Opus | Strategic planning, go-to-market | $$$ |
| **Database Architecture** | `@agent-database-architecture` | Opus | Schema design, optimization | $$$ |
| **Development Prompt** | `@agent-development-prompt` | Default | Development workflows | $$ |
| **DevOps Engineering** | `@agent-devops-engineering` | Default | CI/CD, deployment | $$ |
| **Financial Analyst** | `@agent-financial-analyst` | Opus | Financial modeling, projections | $$$ |
| **Frontend Architecture** | `@agent-frontend-architecture` | Opus | UI/UX architecture | $$$ |
| **Frontend Mockup** | `@agent-frontend-mockup` | Default | HTML/CSS prototypes | $$ |
| **Integration Setup** | `@agent-integration-setup` | Default | Environment configuration | $$ |
| **Middleware Specialist** | `@agent-middleware-specialist` | Default | Message queues, caching | $$ |
| **Performance Optimization** | `@agent-performance-optimization` | Default | Speed optimization | $$ |
| **Production Frontend** | `@agent-production-frontend` | Default | React/Vue/Angular | $$ |
| **Project Manager** | `@agent-project-manager` | Default | Timeline, resource management | $$ |
| **Prompt Engineer** | `@agent-prompt-engineer` | Default | Prompt optimization | $$ |
| **Quality Assurance** | `@agent-quality-assurance` | Haiku | Code quality checks | $ |
| **Script Automation** | `@agent-script-automation` | Default | Build/deploy scripts | $$ |
| **Security Architecture** | `@agent-security-architecture` | Opus | Security design, compliance | $$$ |
| **Technical CTO** | `@agent-technical-cto` | Opus | Technical feasibility | $$$ |
| **Technical Documentation** | `@agent-technical-documentation` | Haiku | Documentation writing | $ |
| **Technical Specifications** | `@agent-technical-specifications` | Opus | Requirements analysis | $$$ |
| **Testing Automation** | `@agent-testing-automation` | Haiku | Test creation | $ |
| **Mobile Development** | `@agent-mobile-development` | Default | iOS/Android apps | $$ |
| **UI/UX Design** | `@agent-ui-ux-design` | Default | User experience | $$ |

### Model Cost Strategy
- **Opus (11 agents)**: $0.015/call - Use for complex reasoning, architecture, critical decisions
- **Default (13 agents)**: $0.008/call - Use for standard development tasks
- **Haiku (4 agents)**: $0.002/call - Use for routine tasks, documentation, simple tests

**Cost Optimization**: Using this distribution typically saves 40-60% vs using Opus for everything.

---

## 🎯 All 18 Slash Commands

| Command | Purpose | Example with @agent- | Typical Agents |
|---------|---------|---------------------|----------------|
| `/new-project` | Initialize complete project | `/new-project "SaaS platform" @agent-master-orchestrator @agent-business-analyst` | Orchestrator, Business |
| `/resume-project` | Continue existing work | `/resume-project @agent-master-orchestrator` | Orchestrator |
| `/business-analysis` | Market & ROI analysis | `/business-analysis @agent-business-analyst @agent-financial-analyst` | Business, Financial |
| `/technical-feasibility` | Tech assessment | `/technical-feasibility "microservices" @agent-technical-cto` | CTO, Architecture |
| `/project-plan` | Timeline & resources | `/project-plan @agent-project-manager` | Project Manager |
| `/frontend-mockup` | UI prototypes | `/frontend-mockup "dashboard" @agent-frontend-mockup` | Frontend Mockup |
| `/backend-service` | API development | `/backend-service "auth API" @agent-backend-services` | Backend Services |
| `/database-design` | Schema creation | `/database-design @agent-database-architecture` | Database Architecture |
| `/api-integration` | External APIs | `/api-integration "Stripe" @agent-api-integration-specialist` | API Integration |
| `/middleware-setup` | Queue/cache setup | `/middleware-setup @agent-middleware-specialist` | Middleware |
| `/production-frontend` | Production UI | `/production-frontend @agent-production-frontend` | Production Frontend |
| `/documentation` | Technical docs | `/documentation @agent-technical-documentation` | Documentation |
| `/financial-model` | Financial projections | `/financial-model @agent-financial-analyst` | Financial Analyst |
| `/go-to-market` | GTM strategy | `/go-to-market @agent-ceo-strategy` | CEO Strategy |
| `/requirements` | Requirements gathering | `/requirements @agent-technical-specifications` | Specifications |
| `/site-architecture` | Information architecture | `/site-architecture @agent-frontend-architecture` | Frontend Architecture |
| `/tech-alignment` | Business-tech alignment | `/tech-alignment @agent-business-tech-alignment` | Business-Tech |
| `/prompt-enhance` | Prompt optimization | `/prompt-enhance @agent-prompt-engineer` | Prompt Engineer |

---

## 🌐 MCP Tools (Maximum 3)

| Tool | Purpose | Install Command | Primary Agents |
|------|---------|----------------|----------------|
| **Playwright** | Browser testing | `claude mcp add playwright npx @playwright/mcp@latest` | Testing, QA, Frontend |
| **Obsidian** | Knowledge management | `claude mcp add obsidian` | Documentation, Orchestrator |
| **Brave Search** | Web research | `claude mcp add brave-search` | Business, Requirements |

**Rule**: Never exceed 3 MCPs. These cover 90% of external integration needs.

---

## 🔧 Hook System (Automatic)

Hooks execute automatically when configured. No manual triggering needed.

| Hook | Trigger | Effect | Benefit |
|------|---------|--------|---------|
| Session Loader | Claude Code starts | Restores context | Never lose work |
| Session Saver | Claude Code stops | Persists state | Resume seamlessly |
| Quality Gate | Before file save | Checks standards | Consistent code |
| Planning Trigger | Requirements change | Alerts agents | Proactive planning |
| Agent Parser | @agent- mentions | Routes to agents | Deterministic control |
| Model Tracker | Agent calls | Tracks costs | Cost visibility |
| Microcompact | Context grows | Clears old data | Extended sessions |

---

## 📋 Master Prompt Templates v2.1

### Template 1: New Full-Stack Project
```
/new-project "[PROJECT_NAME]: [DESCRIPTION]"
@agent-master-orchestrator @agent-business-analyst
Context: 
- Industry: [SECTOR]
- Users: [TARGET_AUDIENCE]
- Scale: [EXPECTED_LOAD]
- Budget conscious: Yes (use model optimization)
Requirements:
- Core features: [LIST]
- Integrations: [THIRD_PARTY_SERVICES]
- Timeline: [WEEKS/MONTHS]
Tech Stack: [PREFERENCES] or "recommend optimal"

PDF Resources: 
"Read requirements from requirements.pdf"
"Analyze competitor analysis from market-research.pdf"

Note: Session will use microcompact for extended development
```

### Template 2: Cost-Optimized Feature Addition
```
/resume-project
Feature: [FEATURE_NAME]

Phase 1 - Planning (Opus agents for complex thinking):
@agent-technical-specifications analyze requirements
@agent-database-architecture design schema changes

Phase 2 - Implementation (Default agents for development):
@agent-backend-services implement API endpoints
@agent-frontend-mockup create UI components

Phase 3 - Quality (Haiku agents for routine tasks):
@agent-testing-automation write comprehensive tests
@agent-technical-documentation update all docs
@agent-quality-assurance review code quality

Expected cost reduction: 60% vs all-Opus approach
```

### Template 3: Rapid MVP (Maximum Speed + Cost Efficiency)
```
/new-project "MVP: [IDEA]"
@agent-master-orchestrator coordinate rapid development

Week 1 - Core Planning:
@agent-business-analyst validate idea (Opus - critical thinking)
@agent-technical-cto assess feasibility (Opus - architecture)

Week 2-3 - Build:
@agent-backend-services create minimal API (Default - standard dev)
@agent-frontend-mockup build UI (Default - standard dev)

Week 4 - Polish:
@agent-testing-automation basic tests (Haiku - routine)
@agent-technical-documentation user guide (Haiku - routine)

Total agents: 7 (3 Opus, 2 Default, 2 Haiku)
Estimated savings: 55% vs traditional approach
```

### Template 4: Architecture Planning (Opus-Heavy)
```
"Let's ultrathink about [ARCHITECTURAL_CHALLENGE]"

Critical Thinking Phase (Opus for all):
@agent-master-orchestrator coordinate analysis
@agent-frontend-architecture design system architecture
@agent-database-architecture plan data architecture
@agent-security-architecture ensure security compliance
@agent-technical-cto validate technical decisions

Research Support:
Use Brave Search MCP for market research
Use Obsidian MCP for decision documentation

Note: This template intentionally uses Opus-model agents due to 
architectural complexity. Cost is justified by decision criticality.
```

### Template 5: Bug Fix Workflow (Cost-Conscious)
```
Issue: [BUG_DESCRIPTION]

Step 1 - Triage (Default model):
@agent-backend-services investigate backend logs
@agent-frontend-mockup check UI issues

Step 2 - Fix (Default model):
@agent-backend-services implement fix
@agent-performance-optimization ensure no regression

Step 3 - Verify (Haiku for routine):
@agent-testing-automation write regression tests
@agent-quality-assurance verify fix

Total cost: ~70% less than using Opus agents
```

---

## 🎯 Project Development Patterns

### Pattern 1: New SaaS Project (Balanced Approach)
```
Phase 1 - Business Foundation (Opus - 20% of effort):
/business-analysis @agent-business-analyst
/technical-feasibility @agent-technical-cto
/financial-model @agent-financial-analyst

Phase 2 - Architecture (Opus - 20% of effort):
@agent-master-orchestrator create project structure
@agent-database-architecture design complete schema
@agent-security-architecture plan security layers

Phase 3 - Implementation (Default - 40% of effort):
@agent-backend-services build all APIs
@agent-frontend-mockup create all UIs
@agent-integration-setup configure environment

Phase 4 - Quality & Launch (Haiku - 20% of effort):
@agent-testing-automation comprehensive test suite
@agent-technical-documentation complete documentation
@agent-quality-assurance final review

Cost Profile: Balanced (40% Opus, 40% Default, 20% Haiku)
```

### Pattern 2: Enterprise Integration (Complex, Opus-Heavy)
```
Complexity warrants higher Opus usage:

/new-project "Enterprise CRM Integration"
@agent-master-orchestrator (Opus - orchestration)
@agent-business-tech-alignment (Opus - alignment)
@agent-api-integration-specialist (Default - implementation)
@agent-security-architecture (Opus - compliance critical)
@agent-database-architecture (Opus - data critical)

Justification: Enterprise = higher stakes = worth Opus investment
```

### Pattern 3: Simple CRUD App (Haiku-Optimized)
```
Simple requirements allow maximum cost savings:

/new-project "Basic task manager"
@agent-backend-services create CRUD API (Default)
@agent-frontend-mockup simple UI (Default)
@agent-testing-automation basic tests (Haiku)
@agent-technical-documentation API docs (Haiku)

Cost Profile: Minimal (0% Opus, 50% Default, 50% Haiku)
Savings: ~80% vs traditional approach
```

---

## 🚀 Special Modes & Features

### Ultrathink Mode (Complex Problem Solving)
```
Activation: "Let's ultrathink about [COMPLEX_PROBLEM]"

What happens:
1. Automatically assembles relevant Opus-model agents
2. Loads all session context via hooks
3. Enables extended reasoning chains
4. Documents decisions in Obsidian MCP
5. Preserves state for future sessions

Example:
"Let's ultrathink about scaling to 1 million users"
Auto-activates:
- @agent-master-orchestrator (coordination)
- @agent-performance-optimization (performance)
- @agent-database-architecture (data scaling)
- @agent-devops-engineering (infrastructure)
- @agent-security-architecture (security at scale)
```

### PDF-Driven Development
```
Any agent can read PDFs directly:

"@agent-business-analyst analyze the market research in competitor-analysis.pdf"
"@agent-technical-specifications extract requirements from client-rfp.pdf"
"@agent-database-architecture implement the schema from legacy-database.pdf"

Best practice: Reference PDFs early in prompts for context loading
```

### Extended Session Best Practices
```
Microcompact handles automatically, but optimize by:

1. Start with context load:
   "Continue yesterday's e-commerce project"
   
2. Let hooks restore state:
   - Previous agent assignments
   - Decision history
   - Work progress
   
3. Work naturally:
   - No manual /compact needed
   - Context preserved automatically
   - Critical state saved before clearing
   
4. End with summary:
   @agent-technical-documentation summarize today's progress
```

### Cross-Session Continuity Pattern
```
Session 1 (Monday):
/new-project "SaaS Platform" @agent-master-orchestrator
[Work progresses, hooks save state]

Session 2 (Wednesday):
/resume-project
"Continue SaaS platform development"
[Hooks restore: agents, decisions, progress]

Session 3 (Friday):
"Complete the remaining SaaS platform tasks"
[Full context available, work continues seamlessly]

Key: Trust the hooks - they maintain perfect continuity
```

---

## 💰 Cost Optimization Strategies

### Strategy 1: Task-Based Agent Selection
```
Complex Tasks (Use Opus):
- System architecture design
- Business strategy planning  
- Database schema design
- Security architecture
- Financial modeling

Standard Tasks (Use Default):
- API implementation
- Frontend development
- Integration work
- DevOps setup

Routine Tasks (Use Haiku):
- Test writing
- Documentation
- Code formatting
- Basic QA checks
```

### Strategy 2: Project Phase Optimization
```
Early Phase (Invest in Opus):
- Critical decisions need best reasoning
- Architecture mistakes are expensive
- 40% Opus usage acceptable

Mid Phase (Balance Default):
- Implementation is straightforward
- 70% Default usage typical

Late Phase (Maximize Haiku):
- Documentation and tests are routine
- 60% Haiku usage achievable
```

### Strategy 3: Intelligent Pairing
```
Pair Opus + Haiku for balance:
@agent-database-architecture design schema (Opus)
@agent-testing-automation test the schema (Haiku)

Result: Critical thinking + cost-efficient execution
```

---

## 📝 Converting Old Prompts to v2.1

### Example 1: Old Multi-Model Prompt
```
OLD:
/new-project "E-commerce"
@agent-master-orchestrator[opus] @agent-backend-services[sonnet] @agent-testing-engineer[haiku]

NEW:
/new-project "E-commerce"
@agent-master-orchestrator @agent-backend-services @agent-testing-automation

(Models now in agent configs: Orchestrator=Opus, Backend=Default, Testing=Haiku)
```

### Example 2: Old Feature Addition
```
OLD:
@agent-frontend-developer[sonnet] build dashboard
@agent-qa-engineer[haiku] test it

NEW:
@agent-frontend-mockup build dashboard
@agent-quality-assurance test it

(Agents renamed for clarity, models in configs)
```

---

## 🎓 Training Other LLMs

### For ChatGPT/Claude.ai/Gemini:
```
"I'm going to give you a guide for generating Claude Code prompts. Please:
1. Read the entire UNIVERSAL_META_PROMPTING_GUIDE_V21.md
2. Note that models are configured in agent files, not specified inline
3. Always use @agent- prefix exactly as shown in the tables
4. Generate prompts that optimize for cost (Haiku for routine tasks)
5. Include relevant slash commands and MCP references
6. Assume hooks handle session management automatically"
```

### Example Meta-Prompt for Other LLMs:
```
"Using the Universal Meta-Prompting Guide v2.1, create a Claude Code prompt for 
building a B2B SaaS platform with subscription management. Optimize for cost by 
using Opus agents only for critical architecture decisions, and Haiku agents 
for all testing and documentation. Include PDF reading for existing requirements."
```

### Expected Output Format:
```
/new-project "B2B SaaS with Subscription Management"
@agent-master-orchestrator @agent-business-analyst

Context:
- Read requirements: "Analyze requirements from saas-requirements.pdf"
- Industry: B2B Software
- Key feature: Subscription management
- Cost conscious: Yes

Phase 1 - Architecture (Opus agents):
@agent-database-architecture design subscription schema
@agent-security-architecture plan authentication

Phase 2 - Build (Default agents):
@agent-backend-services implement subscription API
@agent-frontend-mockup create billing dashboard

Phase 3 - Quality (Haiku agents):
@agent-testing-automation comprehensive test suite
@agent-technical-documentation API documentation

MCP Usage: Obsidian for architecture decisions
```

---

## 🚨 Common Mistakes to Avoid

### ❌ DON'T: Specify Models Inline
```
WRONG: @agent-backend-services[opus]
WRONG: @agent-testing-engineer[haiku]
```

### ✅ DO: Use Agent Names Only
```
RIGHT: @agent-backend-services
RIGHT: @agent-testing-automation
```

### ❌ DON'T: Use Old Agent Names
```
WRONG: @agent-frontend-developer
WRONG: @agent-qa-engineer
```

### ✅ DO: Use Exact Config Names
```
RIGHT: @agent-frontend-mockup
RIGHT: @agent-quality-assurance
```

### ❌ DON'T: Exceed 3 MCPs
```
WRONG: Add Playwright, Obsidian, Brave, MongoDB, Slack
```

### ✅ DO: Stick to Universal MCPs
```
RIGHT: Playwright, Obsidian, Brave Search only
```

### ❌ DON'T: Manage Sessions Manually
```
WRONG: /save-context, /restore-context, /compact
```

### ✅ DO: Let Hooks Handle Everything
```
RIGHT: Hooks manage session state automatically
```

---

## 🎯 Quick Decision Matrix

| If You Need... | Use These Agents | Model Type | Cost |
|----------------|------------------|------------|------|
| Project planning | Master Orchestrator, Business Analyst | Opus | $$$ |
| Architecture design | System/Database/Security Architects | Opus | $$$ |
| API development | Backend Services, API Integration | Default | $$ |
| UI development | Frontend Mockup, Production Frontend | Default | $$ |
| Testing | Testing Automation, Quality Assurance | Haiku | $ |
| Documentation | Technical Documentation | Haiku | $ |
| Deployment | DevOps Engineering | Default | $$ |
| Optimization | Performance Optimization | Default | $$ |

---

## 📚 Final Notes

1. **This guide is version 2.1** - Always check for updates
2. **Models are preset** - Don't specify them inline
3. **Hooks are automatic** - Configure once, run forever
4. **MCPs are limited** - 3 maximum for simplicity
5. **Cost matters** - 40-60% savings are achievable
6. **Sessions are unlimited** - Microcompact handles length
7. **PDFs work everywhere** - Any agent can read them
8. **Cross-LLM compatible** - This guide works in any AI

---

*Universal Meta-Prompting Guide v2.1 - The single source of truth for Claude Code prompt generation*