# 🧠 Universal Meta-Prompting Guide v2.1 - Claude Code Dev Stack

> **Transform ANY AI Assistant into a Claude Code Expert in Minutes**
> 
> Version: 2.1 Enhanced | Last Updated: January 2025 | Status: Production Ready

---

## 🎯 What This Guide Does

In 30 seconds, you'll understand how to:
- ✅ Generate perfect Claude Code prompts using ANY AI assistant
- ✅ Save 40-60% on AI costs with strategic model selection
- ✅ Build complete applications from idea to deployment
- ✅ Coordinate 28 specialized AI agents like a pro

---

## 📚 Table of Contents

### 🚀 Getting Started (Start Here!)
- [How to Use This Guide](#-how-to-use-this-guide)
- [30-Second Quick Start](#-30-second-quick-start)
- [Universal LLM Instructions](#-universal-llm-instructions)
- [What's New in v2.1](#-whats-new-in-v21)

### 🏗️ Core Concepts
- [AIMS Framework Explained](#-aims-framework-explained)
- [The 28 Specialized Agents](#-the-28-specialized-agents)
- [18 Power Commands](#-the-18-power-commands)
- [Smart Cost Optimization](#-smart-cost-optimization)

### 🛠️ Tools & Features
- [MCP Tools Guide](#-mcp-tools-guide)
- [Automatic Features](#-automatic-features)
- [PDF Integration](#-pdf-integration)
- [Extended Sessions](#-extended-sessions)

### 📋 Templates & Examples
- [Copy-Paste Templates](#-copy-paste-templates)
- [Real Project Examples](#-real-project-examples)
- [Common Patterns](#-common-patterns)
- [Troubleshooting](#-troubleshooting)

### 🎓 Advanced Topics
- [Training Other AIs](#-training-other-ais)
- [Complex Projects](#-complex-projects)
- [Ultrathink Mode](#-ultrathink-mode)
- [Cross-Session Work](#-cross-session-work)

### 🔄 Integration Patterns (NEW!)
- [Cross-Agent Communication Patterns](#-cross-agent-communication-patterns)
- [MCP Integration Workflows](#-mcp-integration-workflows)
- [External LLM Integration](#-external-llm-integration)
- [Hook System Integration](#-hook-system-integration)
- [Session Management Patterns](#-session-management-patterns)
- [API and Webhook Patterns](#-api-and-webhook-patterns)

### 📚 Reference
- [Complete Agent List](#-complete-agent-reference)
- [Command Reference](#-command-reference)
- [Cost Calculator](#-cost-calculator)
- [One-Page Cheat Sheet](#-one-page-cheat-sheet)

---

## 🎯 How to Use This Guide

This guide has three reading paths:

### Path 1: "I need to start NOW" (2 minutes)
1. Jump to [30-Second Quick Start](#-30-second-quick-start)
2. Copy a template from [Copy-Paste Templates](#-copy-paste-templates)
3. Start building!

### Path 2: "I want to understand the basics" (10 minutes)
1. Read [AIMS Framework Explained](#-aims-framework-explained)
2. Scan [The 28 Specialized Agents](#-the-28-specialized-agents)
3. Try examples in [Real Project Examples](#-real-project-examples)

### Path 3: "I want to master Claude Code" (30 minutes)
1. Read the guide sequentially
2. Practice with different agent combinations
3. Optimize costs using [Smart Cost Optimization](#-smart-cost-optimization)

> 💡 **Pro Tip**: Keep the [One-Page Cheat Sheet](#-one-page-cheat-sheet) open while working!

---

## ⚡ 30-Second Quick Start

### The Fastest Way to Start

```prompt
/new-project "My Awesome App"
@agent-master-orchestrator @agent-business-analyst
Tell me what you want to build, and I'll handle the rest!
```

That's it! The agents will:
- Ask clarifying questions
- Plan your architecture
- Start building immediately
- Guide you through each step

### Quick Examples That Just Work

**Example 1: Build a SaaS MVP**
```prompt
/new-project "Task Management SaaS"
@agent-master-orchestrator @agent-business-analyst
Industry: B2B Software
Users: Small teams (5-20 people)
Core features: Tasks, projects, team collaboration
Tech preference: React + Node.js
```

**Example 2: Add Stripe Payments**
```prompt
/resume-project
@agent-api-integration-specialist integrate Stripe payments
@agent-backend-services create subscription management
Requirements: Monthly/yearly plans, team billing
```

**Example 3: Fix Performance**
```prompt
Issue: API responses taking >2 seconds
@agent-backend-services investigate slow queries
@agent-performance-optimization implement caching
Target: <200ms response time
```

---

## 🎯 Universal LLM Instructions

> ⚠️ **IMPORTANT**: Give these instructions to ANY AI assistant (ChatGPT, Claude.ai, Gemini, etc.)

### Copy This Box to Any AI Assistant:

```
I need you to generate Claude Code prompts using this guide. Please:

1. ALWAYS use @agent- prefix for agents (no brackets or model names)
2. Select agents based on task complexity to optimize costs
3. Include relevant slash commands from the 18 available
4. Remember: Opus costs 7x more than Haiku - use wisely
5. Follow the AIMS methodology (Agent, Integration, Method, Structure)

The guide explains everything. Help me build efficiently!
```

### Why This Works Everywhere

- **Universal Format**: Every AI understands these patterns
- **Self-Contained**: No external knowledge needed
- **Cost-Aware**: Built-in optimization strategies
- **Proven**: Tested across all major AI platforms

---

## 📊 What's New in v2.1

### 🔄 Major Changes (Action Required!)

| Old Way (❌) | New Way (✅) | Why It Changed |
|-------------|-------------|----------------|
| `@agent-backend[opus]` | `@agent-backend-services` | Models set in config files |
| Manual session management | Automatic hooks | Simplifies workflow |
| Unlimited MCP tools | Maximum 3 tools | Improves stability |
| Complex routing | Deterministic @agent- prefix | 100% reliable |

> 🚨 **Quick Fix**: Just remove `[model]` from all your existing prompts!

### ✨ New Features

- **Automatic Session Management**: No more manual `/session` commands
- **PDF Reading**: Every agent can now read PDF files directly
- **Cost Optimization**: 40-60% savings with smart model selection
- **Unlimited Project Size**: Microcompact enables endless sessions

---

## 🏗️ AIMS Framework Explained

Think of AIMS as your **prompt recipe** - follow it for perfect results every time!

### The AIMS Recipe

```
A - Agent Selection    → WHO will do the work (the chef)
I - Integration       → WHAT tools they need (the kitchen tools)
M - Method           → HOW they'll do it (the recipe steps)
S - Structure        → WHY in this order (the cooking sequence)
```

### 🅰️ **A - Agent Selection** (WHO)

Think of agents as **specialized experts** you'd hire for a project:

- **Need business strategy?** → `@agent-business-analyst`
- **Need to build an API?** → `@agent-backend-services`
- **Need to fix bugs?** → `@agent-testing-automation`

**The Golden Rule**: Always use `@agent-` prefix, never add model names!

```prompt
✅ CORRECT: @agent-backend-services
❌ WRONG:   @agent-backend-services[opus]
❌ WRONG:   @backend-services
```

### 🔗 **I - Integration** (WHAT)

Your agents have access to powerful tools:

| Tool Type | What It Does | Example Use |
|-----------|--------------|-------------|
| **MCP Tools** | Extend capabilities | Browser testing, web search |
| **Hooks** | Automate workflows | Session management (automatic!) |
| **PDFs** | Provide context | "Read requirements.pdf" |

> 💡 **Quick Win**: PDFs are the fastest way to give agents context!

### 🎯 **M - Method** (HOW)

Commands set the stage for your agents:

- **Starting fresh?** → `/new-project`
- **Continuing work?** → `/resume-project`
- **Need analysis?** → `/business-analysis`
- **Building features?** → `/backend-service`

**Pro Pattern**: Command + Agents + Details = Success

### 📋 **S - Structure** (WHY)

The right structure ensures clarity:

```prompt
1. Set context with a command
2. Call the right agents
3. Provide specific requirements
4. Reference resources (PDFs)
5. State constraints (budget, time)
6. Define success criteria
```

**Real Example Following AIMS**:
```prompt
/new-project "E-commerce Platform"              # Method (command)
@agent-master-orchestrator @agent-business-analyst  # Agents (who)
Requirements: Multi-vendor, 100k users          # Structure (details)
Read: "market-analysis.pdf"                     # Integration (resources)
Timeline: 8 weeks, cost-conscious               # Structure (constraints)
Success: MVP with payments working              # Structure (criteria)
```

---

## 👥 The 28 Specialized Agents

Think of these agents as your **dream team** - each expert in their domain!

### 🎯 Quick Selection Guide

| I Need To... | Use These Agents | Why Them? |
|--------------|------------------|-----------|
| Start a new project | `@agent-master-orchestrator` + `@agent-business-analyst` | Planning experts |
| Build an API | `@agent-backend-services` | Backend specialist |
| Create UI | `@agent-frontend-mockup` → `@agent-production-frontend` | UI progression |
| Add payments | `@agent-api-integration-specialist` | Integration expert |
| Fix performance | `@agent-performance-optimization` | Speed specialist |
| Write tests | `@agent-testing-automation` | Testing expert |

### 💰 Cost-Aware Agent Selection

Agents use three AI models with different costs:

| Model | Cost | Best For | # of Agents |
|-------|------|----------|-------------|
| **Opus** 🧠 | $$$ (7x) | Complex thinking, architecture | 11 agents |
| **Default** ⚙️ | $$ (4x) | Standard development | 13 agents |
| **Haiku** 🏃 | $ (1x) | Routine tasks, documentation | 4 agents |

> 💡 **Quick Win**: Using the right mix saves 40-60% on costs!

### 🏢 Agent Categories Explained

#### Business Strategy (Opus 🧠 - Use for Critical Decisions)
- `@agent-business-analyst` - Market research, requirements
- `@agent-ceo-strategy` - Business model, go-to-market
- `@agent-financial-analyst` - ROI, financial projections
- `@agent-technical-cto` - Technical feasibility

#### Development Team (Default ⚙️ - Your Workhorses)
- `@agent-backend-services` - APIs and server logic
- `@agent-frontend-mockup` - Quick UI prototypes
- `@agent-production-frontend` - Production React/Vue/Angular
- `@agent-api-integration-specialist` - Third-party integrations

#### Quality & Testing (Haiku 🏃 - Efficient for Routine Tasks)
- `@agent-testing-automation` - Automated tests
- `@agent-technical-documentation` - Documentation
- `@agent-quality-assurance` - Code reviews

#### Specialists (Mixed - As Needed)
- `@agent-database-architecture` - Database design (Opus)
- `@agent-security-architecture` - Security planning (Opus)
- `@agent-performance-optimization` - Speed improvements (Default)
- `@agent-devops-engineering` - CI/CD and deployment (Default)

> 📖 **Need Details?** See [Complete Agent Reference](#-complete-agent-reference) for full capabilities

---

## 🎮 The 18 Power Commands

Commands are like **keyboard shortcuts** for common tasks!

### 🚀 Essential Commands (Use These 80% of the Time)

| Command | What It Does | When to Use |
|---------|--------------|-------------|
| `/new-project` | Start from scratch | Beginning any project |
| `/resume-project` | Continue existing work | Returning to work |
| `/backend-service` | Build server features | Creating APIs |
| `/frontend-mockup` | Create UI prototypes | Designing interfaces |

### 📊 Full Command Categories

#### Project Management
- `/new-project` - Initialize complete project
- `/resume-project` - Continue existing work  
- `/project-plan` - Create timelines and milestones

#### Business & Strategy
- `/business-analysis` - Market research and validation
- `/financial-model` - Financial projections
- `/go-to-market` - Launch strategy
- `/tech-alignment` - Align tech with business

#### Development
- `/backend-service` - API development
- `/frontend-mockup` - UI prototypes
- `/production-frontend` - Production UI
- `/api-integration` - External integrations
- `/database-design` - Schema creation

#### Architecture & Planning
- `/technical-feasibility` - Assess technical approach
- `/requirements` - Gather detailed requirements
- `/site-architecture` - Information architecture
- `/middleware-setup` - Queues and caching

#### Documentation & Quality
- `/documentation` - Technical documentation
- `/prompt-enhance` - Optimize prompts

> 💡 **Pro Tip**: Commands + Agents = Magic! Always pair them for best results.

---

## 💰 Smart Cost Optimization

Save 40-60% on AI costs with these strategies!

### The Cost Reality

| Model | Relative Cost | When to Use | Example Tasks |
|-------|--------------|-------------|---------------|
| Opus 🧠 | 7x | Critical thinking | Architecture, security |
| Default ⚙️ | 4x | Standard work | Building features |
| Haiku 🏃 | 1x | Routine tasks | Tests, documentation |

### 💡 Money-Saving Patterns

#### Pattern 1: The 60/30/10 Rule
```
60% Haiku (routine) + 30% Default (building) + 10% Opus (critical) = 60% savings
```

#### Pattern 2: Phase-Based Optimization
```prompt
Phase 1 - Planning (Opus for 2 agents): $0.030
Phase 2 - Building (Default for 4 agents): $0.032  
Phase 3 - Testing (Haiku for 3 agents): $0.006
Total: $0.068 (vs $0.135 all-Opus = 50% savings!)
```

#### Pattern 3: Task-Specific Selection
- **Architecture Decision?** → Use Opus (worth the cost)
- **Building CRUD API?** → Use Default (standard work)
- **Writing tests?** → Use Haiku (routine task)

### 📊 Real Cost Examples

| Project Type | All-Opus Cost | Optimized Cost | Savings |
|--------------|---------------|----------------|---------|
| Simple CRUD App | $0.090 | $0.028 | 69% |
| SaaS Platform | $0.315 | $0.126 | 60% |
| Enterprise Integration | $0.450 | $0.270 | 40% |

> ⚠️ **Remember**: Agents automatically use the right model - just pick the right agents!

---

## 🛠️ MCP Tools Guide

MCP tools are like **power-ups** for your agents - use up to 3 per project!

### 🎯 The Three Power Tools

#### 🎭 Playwright - Browser Automation
**What**: Automates browsers for testing and scraping
**When**: E2E testing, UI validation, competitor research
**Install**: `claude mcp add playwright npx @playwright/mcp@latest`

**Example Use**:
```prompt
@agent-testing-automation use Playwright to:
- Test the complete checkout flow
- Verify responsive design on mobile
- Capture screenshots of each step
```

#### 📝 Obsidian - Knowledge Management  
**What**: Creates interconnected documentation
**When**: Architecture docs, decision tracking, wikis
**Install**: `claude mcp add obsidian`

**Example Use**:
```prompt
@agent-technical-documentation use Obsidian to:
- Create architecture decision records
- Build API documentation wiki
- Link all related documents
```

#### 🔍 Brave Search - Web Research
**What**: Searches the web for current information
**When**: Market research, tech evaluation, trends
**Install**: `claude mcp add brave-search`

**Example Use**:
```prompt
@agent-business-analyst use Brave Search to:
- Research competitor pricing models
- Find latest industry trends
- Analyze technology adoption rates
```

### 🎯 Tool Selection Strategy

| Project Type | Recommended Tools | Why This Combo |
|--------------|------------------|----------------|
| Web App | Playwright + Obsidian | Testing + Docs |
| Research Project | Brave + Obsidian | Research + Knowledge |
| API Only | Obsidian | Documentation focus |
| Mobile App | Obsidian + Brave | Docs + Market research |

> ⚠️ **Important**: Maximum 3 tools per project for stability!

---

## 🤖 Automatic Features

These features work **automatically** - no setup needed!

### ✨ What's Automatic

1. **Session Management**
   - Saves progress automatically
   - Resumes where you left off
   - No manual commands needed

2. **Quality Checks**
   - Code review on commits
   - Test coverage monitoring
   - Security scanning

3. **Planning Hooks**
   - Dependency tracking
   - Timeline updates
   - Resource optimization

### 🎯 What This Means for You

**Old Way** (Manual):
```prompt
/session save
/session microcompact
/quality-check enable
```

**New Way** (Automatic):
```prompt
Just start working - everything handles itself!
```

> 💡 **Quick Win**: Focus on building, not managing!

---

## 📄 PDF Integration

PDFs are your **secret weapon** for giving agents context!

### How to Use PDFs

Simply reference them in your prompts:

```prompt
@agent-business-analyst analyze the market
Read: "competitor-analysis.pdf"
Focus on pricing models and feature gaps
```

### 📚 Best PDF Practices

| PDF Type | Best Used For | Example |
|----------|---------------|---------|
| Requirements | Project specs | "Read requirements.pdf for feature list" |
| Research | Market analysis | "Read market-research.pdf for trends" |
| Designs | UI mockups | "Read wireframes.pdf for layout" |
| Reports | Data analysis | "Read analytics-report.pdf for metrics" |

### Power Moves with PDFs

1. **Multi-PDF Analysis**:
   ```prompt
   @agent-business-analyst compare:
   - "our-features.pdf"
   - "competitor-features.pdf"
   - "market-gaps.pdf"
   ```

2. **PDF-Driven Development**:
   ```prompt
   @agent-backend-services implement API from "api-spec.pdf"
   @agent-database-architecture use schema from "data-model.pdf"
   ```

> 💡 **Pro Tip**: PDFs eliminate long explanations - just reference and go!

---

## ♾️ Extended Sessions

Build projects of **any size** without limits!

### What Are Extended Sessions?

- **Unlimited Context**: Never lose your place
- **Automatic Management**: No manual intervention
- **Seamless Continuity**: Pick up exactly where you left off

### How It Works

1. Start your project normally
2. Work as long as needed
3. Come back anytime with `/resume-project`
4. Everything is preserved!

### 🎯 Best Practices

**For Long Projects**:
```prompt
/new-project "Enterprise Platform"
@agent-master-orchestrator 
Note: This is a 3-month project, we'll work in phases
```

**For Continuous Development**:
```prompt
/resume-project
What did we accomplish last session?
What's next on our roadmap?
```

> 💡 **No Limits**: Build for days, weeks, or months - Claude Code keeps up!

---

## 📋 Copy-Paste Templates

**Ready-to-use templates** - just fill in the blanks!

### 🚀 Template 1: Start Any Project

```prompt
/new-project "[YOUR PROJECT NAME]"
@agent-master-orchestrator @agent-business-analyst

What I'm Building:
- Type: [Web app/Mobile app/API/etc]
- Users: [Who will use this]
- Core Features: [Main 3-5 features]

Preferences:
- Timeline: [Weeks/Months]
- Tech Stack: [Your preferences or "recommend"]
- Budget: [Cost-conscious/Normal/Premium]

Start with market analysis and technical planning
```

### 💰 Template 2: Cost-Optimized Development

```prompt
/resume-project
Building: [FEATURE NAME]

Phase 1 - Planning (Using Opus for complex thinking):
@agent-technical-specifications design the architecture
@agent-database-architecture plan data model

Phase 2 - Implementation (Using Default for building):
@agent-backend-services build the API
@agent-frontend-mockup create the UI

Phase 3 - Quality (Using Haiku for routine tasks):
@agent-testing-automation write tests
@agent-technical-documentation update docs

Note: This approach saves 60% vs using premium models throughout
```

### ⚡ Template 3: Quick Feature Addition

```prompt
@agent-backend-services add [FEATURE] to existing API
@agent-production-frontend update UI for new feature
@agent-testing-automation create tests for changes

Requirements:
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

Reference: "feature-spec.pdf" for details
```

### 🐛 Template 4: Smart Debugging

```prompt
Issue: [DESCRIBE THE PROBLEM]

Step 1 - Investigate:
@agent-backend-services check logs and identify issue
@agent-database-architecture verify data integrity

Step 2 - Fix:
@agent-backend-services implement solution
@agent-testing-automation add regression tests

Step 3 - Verify:
@agent-quality-assurance review the fix
@agent-performance-optimization ensure no performance impact
```

### 🏗️ Template 5: Architecture Deep Dive

```prompt
"Let's ultrathink about [ARCHITECTURE CHALLENGE]"

@agent-master-orchestrator coordinate analysis
@agent-technical-cto evaluate options
@agent-database-architecture design data layer
@agent-security-architecture ensure security
@agent-frontend-architecture plan UI architecture

Consider:
- Scale: [EXPECTED LOAD]
- Constraints: [LIMITATIONS]
- Future: [GROWTH PLANS]

Document decisions in Architecture Decision Records
```

> 💡 **Pro Tip**: These templates are starting points - customize them!

---

## 🌟 Real Project Examples

Learn from **complete project walkthroughs**!

### Example 1: E-Commerce Platform (Full Walkthrough)

**Project**: Multi-vendor marketplace
**Timeline**: 12 weeks
**Budget**: Cost-conscious

#### Week 1-2: Planning Phase
```prompt
/new-project "Multi-vendor E-commerce Platform"
@agent-master-orchestrator @agent-business-analyst

Industry: E-commerce marketplace
Users: Vendors and buyers (B2C)
Scale: 100k concurrent users
Features: Products, orders, payments, reviews

First, analyze the market and create technical plan
```

**Cost**: $0.045 (3 Opus calls for critical thinking)

#### Week 3-4: Architecture
```prompt
@agent-database-architecture design schema for:
- Multi-vendor products with variants
- Order management with status tracking
- User roles (buyer, seller, admin)

@agent-security-architecture plan:
- Authentication (JWT + refresh tokens)
- Payment security (PCI compliance)
- Data protection
```

**Cost**: $0.030 (2 Opus calls for architecture)

#### Week 5-8: Building
```prompt
@agent-backend-services build:
- User authentication API
- Product management endpoints
- Order processing system
- Stripe Connect integration

@agent-production-frontend create:
- Product catalog with search
- Shopping cart
- Checkout flow
- Vendor dashboard
```

**Cost**: $0.056 (7 Default calls for implementation)

#### Week 9-10: Integration
```prompt
@agent-api-integration-specialist integrate:
- Stripe Connect for payments
- SendGrid for emails
- AWS S3 for images
- Redis for caching

@agent-middleware-specialist setup:
- Redis caching layer
- Background job processing
- Real-time notifications
```

**Cost**: $0.024 (3 Default calls)

#### Week 11-12: Launch Prep
```prompt
@agent-testing-automation create:
- Unit tests (80% coverage)
- Integration tests
- E2E tests with Playwright

@agent-technical-documentation write:
- API documentation
- Deployment guide
- User manuals

@agent-devops-engineering setup:
- CI/CD pipeline
- Monitoring
- Auto-scaling
```

**Cost**: $0.018 (6 Haiku calls for routine tasks)

**Total Project Cost**: $0.173 (vs $0.405 all-Opus = 57% savings!)

### Example 2: Real-Time Analytics Dashboard

**Project**: Business intelligence dashboard
**Timeline**: 6 weeks
**Focus**: Performance critical

```prompt
/new-project "Real-time Analytics Dashboard"
@agent-master-orchestrator @agent-performance-optimization

Requirements:
- Process 1M events/minute
- Sub-second query response
- Real-time visualizations
- Historical data analysis

Critical: Performance is top priority
Use Opus models for architecture decisions
```

[Detailed implementation steps follow similar pattern...]

### 💡 Lessons from Real Projects

1. **Start with Planning** - Opus agents for critical decisions
2. **Build with Default** - Standard development work
3. **Finish with Haiku** - Testing and documentation
4. **Always Consider Scale** - Architecture decisions impact everything
5. **Document Everything** - Future you will thank present you

---

## 🎓 Training Other AIs

Turn **any AI** into a Claude Code expert!

### The Universal Training Prompt

Give this to ChatGPT, Gemini, Perplexity, or any AI:

```
You are now a Claude Code prompt expert. Here's what you need to know:

1. Claude Code uses 28 specialized agents prefixed with @agent-
2. Never add [model] brackets - models are preconfigured
3. Use slash commands to set context (/new-project, /resume-project, etc.)
4. Follow AIMS: Agent, Integration, Method, Structure
5. Optimize costs: Opus (complex) > Default (standard) > Haiku (routine)

When users ask for help, generate prompts that:
- Select appropriate agents for the task
- Include relevant commands
- Reference PDFs when provided
- Consider cost optimization
- Follow the AIMS structure

Example prompt you might generate:
"/new-project 'SaaS Platform'
@agent-master-orchestrator @agent-business-analyst
Industry: B2B, Users: Small teams
Features: Projects, tasks, collaboration
Analyze market and plan architecture"

Help users build efficiently with Claude Code!
```

### Making Other AIs Even Smarter

**For ChatGPT**:
```
Also remember: Claude Code responses are interactive. 
Agents will ask clarifying questions. Guide users to:
- Answer questions thoughtfully
- Provide context via PDFs
- Trust agent recommendations
```

**For Gemini**:
```
Focus on cost optimization. Help users understand:
- Opus = $0.015/call (complex reasoning)
- Default = $0.008/call (standard tasks)
- Haiku = $0.002/call (routine work)
Guide them to mix models wisely.
```

---

## 🧠 Ultrathink Mode

For **complex problems** that need deep analysis!

### What is Ultrathink?

A special mode where agents:
- Think deeply about problems
- Consider multiple solutions
- Debate trade-offs
- Reach optimal conclusions

### When to Use Ultrathink

- Architecture decisions
- Technology selection
- Complex integrations
- Performance optimization
- Security planning

### How to Activate

Simply start with: **"Let's ultrathink about..."**

```prompt
"Let's ultrathink about our microservices architecture"

Current: Monolithic Node.js app with 50k users
Goal: Scale to 500k users
Concerns: Data consistency, service communication, deployment

@agent-master-orchestrator coordinate analysis
@agent-technical-cto evaluate approaches
@agent-database-architecture plan data strategy
@agent-devops-engineering consider deployment
```

### Ultrathink Best Practices

1. **Provide Context**: Current state and desired outcome
2. **List Concerns**: What worries you
3. **Include Constraints**: Budget, time, team size
4. **Multiple Agents**: Different perspectives
5. **Document Results**: Capture decisions

> 💡 **Power Move**: Ultrathink + Obsidian MCP = Documented decision history!

---

## 🔄 Cross-Session Work

Seamlessly continue projects **across multiple sessions**!

### The Magic Command

```prompt
/resume-project
```

That's it! Claude Code remembers everything.

### What Gets Preserved

- ✅ All code and files
- ✅ Project structure  
- ✅ Decisions made
- ✅ Architecture choices
- ✅ Work progress
- ✅ Agent context

### Best Practices for Long Projects

1. **Start with Clear Vision**:
   ```prompt
   /new-project "6-Month Enterprise Platform"
   This is a long-term project. Let's establish:
   - Clear architecture
   - Coding standards  
   - Documentation practices
   ```

2. **Regular Check-ins**:
   ```prompt
   /resume-project
   @agent-master-orchestrator summarize:
   - What we've built
   - What's remaining
   - Any blockers
   ```

3. **Phase Management**:
   ```prompt
   /resume-project
   Starting Phase 2: User Management
   Previous phase: Core API (complete)
   Next phase: Payment Integration
   ```

---

## 🔄 Cross-Agent Communication Patterns

Master the art of coordinating multiple agents for complex workflows!

### Agent Handoff Patterns

#### Sequential Handoff Pattern
Agents work in sequence, each building on the previous work:

```prompt
# Pattern: Planning → Architecture → Implementation → Testing

/new-project "Payment Processing System"

Step 1 - Business Analysis:
@agent-business-analyst analyze payment requirements
Output: requirements.md, user-stories.json

Step 2 - Architecture Design:
@agent-database-architecture design payment data model
@agent-security-architecture plan PCI compliance
Input: Use requirements.md from Step 1

Step 3 - Implementation:
@agent-backend-services implement payment API
@agent-api-integration-specialist integrate Stripe
Input: Use architecture from Step 2

Step 4 - Quality Assurance:
@agent-testing-automation write payment tests
@agent-security-architecture audit implementation
Input: Validate against original requirements
```

#### Parallel Coordination Pattern
Multiple agents work simultaneously on different aspects:

```prompt
# Pattern: Parallel development with synchronization points

"Building user authentication system - parallel approach"

Phase 1 - Parallel Planning (All agents work simultaneously):
@agent-database-architecture design user schema
@agent-security-architecture plan auth security
@agent-frontend-mockup design login UI
@agent-api-integration-specialist plan OAuth providers

Synchronization Point: All designs ready

Phase 2 - Parallel Implementation:
@agent-backend-services build auth API (uses all Phase 1 outputs)
@agent-production-frontend create login components
@agent-middleware-specialist setup Redis sessions

Final Sync: Integration testing with all components
```

#### Hub-and-Spoke Pattern
Master orchestrator coordinates specialist agents:

```prompt
# Pattern: Central coordinator managing specialists

@agent-master-orchestrator coordinate marketplace development

You'll manage:
- @agent-business-analyst for requirements
- @agent-database-architecture for data model  
- @agent-backend-services for APIs
- @agent-production-frontend for UI
- @agent-devops-engineering for deployment

Workflow:
1. Gather requirements from all specialists
2. Identify dependencies and conflicts
3. Create integrated development plan
4. Assign tasks with clear interfaces
5. Monitor progress and handle handoffs
```

### Data Flow Between Agents

#### Structured Data Handoff
```prompt
@agent-business-analyst create feature specification
Output format:
{
  "features": [...],
  "user_roles": [...],
  "acceptance_criteria": {...}
}

@agent-backend-services implement based on specification
Read the JSON output from business analyst
Generate API endpoints matching each feature
```

#### Context Preservation Pattern
```prompt
# Preserving context across agent transitions

@agent-master-orchestrator establish project context:
- Architecture decisions made
- Technology stack chosen
- Coding standards defined
- Security requirements

All subsequent agents: Reference this context
@agent-backend-services follow established patterns
@agent-production-frontend use approved component library
@agent-testing-automation validate against standards
```

#### Feedback Loop Pattern
```prompt
# Continuous improvement through agent feedback

@agent-quality-assurance review implementation
→ Feedback to @agent-backend-services
→ Improvements made
→ @agent-testing-automation validates changes
→ @agent-technical-documentation updates docs
→ Loop until quality standards met
```

### Synchronization Patterns

#### Checkpoint Synchronization
```prompt
# Regular sync points for complex projects

Checkpoint 1 - Requirements Complete:
@agent-business-analyst confirms all requirements gathered
@agent-technical-cto validates technical feasibility
All agents align on scope

Checkpoint 2 - Architecture Approved:
@agent-database-architecture presents data model
@agent-security-architecture confirms security design
@agent-master-orchestrator approves to proceed

Checkpoint 3 - MVP Ready:
@agent-backend-services completes core API
@agent-production-frontend finishes essential UI
@agent-testing-automation confirms 80% coverage
```

#### State Management Pattern
```prompt
# Maintaining consistent state across agents

Project State Document (maintained by master orchestrator):
- Current Phase: Implementation
- Completed: Requirements, Architecture
- In Progress: API development (60%), UI (40%)
- Blocked: Payment integration (awaiting credentials)
- Next: Testing phase

All agents reference and update this state
```

---

## 🔌 MCP Integration Workflows

Advanced patterns for combining MCPs with agents for powerful workflows!

### Playwright + Agent Combinations

#### E2E Testing Workflow
```prompt
# Complete E2E testing with visual validation

@agent-testing-automation coordinate E2E testing with Playwright

Test Workflow:
1. Use Playwright to navigate user flows
2. Capture screenshots at each step
3. Validate against design mockups
4. Test responsive breakpoints
5. Generate visual regression reports

Example Test Suite:
- Login flow with 2FA
- Product purchase journey  
- Admin dashboard interactions
- Mobile responsiveness
```

#### Competitor Analysis Workflow
```prompt
# Automated competitor research

@agent-business-analyst use Playwright for competitor analysis

Research Tasks:
1. Navigate to competitor sites
2. Capture pricing pages
3. Document feature lists
4. Screenshot UI patterns
5. Analyze user flows
6. Generate comparison matrix

Sites to analyze: [competitor1.com, competitor2.com]
Focus areas: Pricing, features, UX patterns
```

#### Automated UI Testing Pipeline
```prompt
@agent-devops-engineering create Playwright CI/CD pipeline

Pipeline Steps:
1. Trigger on PR
2. Run Playwright tests in parallel
3. Generate screenshots for failed tests
4. Create visual diff reports
5. Block merge if tests fail
6. Archive test artifacts

Browsers: Chrome, Firefox, Safari, Mobile
```

### Obsidian Knowledge Management Workflows

#### Architecture Decision Records (ADR)
```prompt
# Systematic architecture documentation

@agent-technical-cto use Obsidian for ADR management

Create linked documents for:
- Decision: Choosing React over Vue
- Context: Team expertise, ecosystem
- Consequences: Training needs, hiring
- Alternatives considered: Vue, Angular
- Links: [[Tech Stack]], [[Team Skills]]

Build knowledge graph showing all architectural decisions
```

#### Project Knowledge Base
```prompt
@agent-technical-documentation create Obsidian knowledge base

Structure:
/Architecture
  - System Overview
  - Component Diagrams
  - Data Flow
/APIs
  - Endpoint Documentation
  - Integration Guides
  - Error Codes
/Decisions
  - Technical ADRs
  - Business Decisions
/Procedures
  - Deployment Guide
  - Troubleshooting

Create bidirectional links between related documents
```

#### Living Documentation System
```prompt
# Self-updating documentation

@agent-master-orchestrator maintain Obsidian project wiki

Daily Updates:
1. New decisions → Create ADR
2. Code changes → Update API docs
3. Bug fixes → Update troubleshooting
4. New features → Update user guides

Use Obsidian tags: #decided #in-progress #deprecated
Link related issues, PRs, and discussions
```

### Brave Search Research Integration

#### Market Research Workflow
```prompt
# Comprehensive market analysis

@agent-business-analyst conduct market research with Brave

Research Plan:
1. Search: "[industry] market size 2025"
2. Find: Top 10 competitors
3. Analyze: Pricing models
4. Identify: Technology trends
5. Discover: Customer pain points
6. Track: Recent funding rounds

Compile into market analysis report
Cross-reference with internal data
```

#### Technology Evaluation Workflow
```prompt
@agent-technical-cto evaluate technology options using Brave

Research Framework:
1. Search: "[tech] vs [alternative] comparison"
2. Find: Recent benchmarks
3. Check: Security vulnerabilities
4. Review: Community sentiment
5. Analyze: Adoption trends
6. Assess: Long-term viability

Create decision matrix with findings
```

#### Real-time Monitoring Workflow
```prompt
# Stay updated on important changes

@agent-project-manager setup monitoring with Brave

Monitor:
- Competitor feature launches
- Technology security alerts
- Framework updates
- Industry news
- Regulatory changes

Weekly summary of relevant findings
Alert on critical updates
```

### Multi-MCP Orchestration Examples

#### Complete Feature Development
```prompt
# Combining all MCPs for feature development

Feature: Social Login Implementation

Phase 1 - Research (Brave):
@agent-business-analyst research OAuth providers
- Market share of social platforms
- Implementation complexity
- User preferences by demographic

Phase 2 - Documentation (Obsidian):
@agent-technical-documentation create implementation plan
- Architecture decisions
- Security considerations
- Integration steps

Phase 3 - Testing (Playwright):
@agent-testing-automation test social login flows
- Test each provider
- Capture success/error states
- Validate on mobile devices

Coordinate all outputs into cohesive feature
```

#### Automated Competitive Intelligence
```prompt
# Multi-tool competitive analysis

@agent-business-analyst coordinate competitive intelligence

Workflow:
1. Brave Search: Find new competitors
2. Playwright: Capture competitor UIs
3. Obsidian: Document findings
   - Features matrix
   - Pricing comparison
   - UX patterns
   - Technology stack

Monthly automated report generation
Track changes over time
```

---

## 🌐 External LLM Integration

Leverage multiple AI platforms for specialized tasks!

### ChatGPT 4.0 Integration

#### Specialized Prompts for ChatGPT
```prompt
# When to use ChatGPT 4.0 with Claude Code

Use ChatGPT for:
1. Generating Claude Code prompts
2. Brainstorming before implementation
3. Code review and optimization ideas
4. Alternative solution exploration

ChatGPT Prompt Template:
"I'm using Claude Code Dev Stack to build [project].
Current agents: [list agents being used]
Challenge: [specific problem]
Generate alternative approaches and optimal agent combinations"
```

#### ChatGPT + Claude Code Workflow
```prompt
Step 1 - ChatGPT Planning:
"Design a microservices architecture for an e-commerce platform.
Consider: scalability, security, performance.
Output: service boundaries and communication patterns"

Step 2 - Claude Code Implementation:
@agent-master-orchestrator implement the architecture from ChatGPT
@agent-database-architecture design data models per service
@agent-backend-services create service APIs
[Paste ChatGPT's architecture design]
```

### Claude.ai Integration Patterns

#### Complementary Analysis
```prompt
# Using Claude.ai for deep analysis before Claude Code

Claude.ai Task:
"Analyze this business model for potential risks and opportunities.
Consider: market dynamics, competition, technical challenges"

Then in Claude Code:
@agent-business-analyst refine business model based on analysis
@agent-financial-analyst create projections addressing identified risks
[Reference Claude.ai analysis results]
```

#### Cross-Validation Pattern
```prompt
# Validate Claude Code outputs with Claude.ai

Claude Code: Generate architecture
Claude.ai: Review and critique architecture
Claude Code: Implement improvements
Claude.ai: Final validation

This iterative process ensures optimal solutions
```

### Gemini Pro Usage Guidelines

#### Gemini for Visual Analysis
```prompt
# Leverage Gemini's multimodal capabilities

Workflow:
1. Gemini Pro: Analyze UI mockups and suggest improvements
2. Claude Code: @agent-production-frontend implement Gemini's suggestions
3. Gemini Pro: Review implementation screenshots
4. Claude Code: @agent-frontend-architecture refine based on feedback
```

#### Large-Context Processing
```prompt
# Use Gemini's large context window

Gemini Task:
"Analyze this 100-page requirements document.
Extract: key features, user stories, technical constraints"

Claude Code:
@agent-master-orchestrator create project plan from Gemini's analysis
@agent-business-analyst validate extracted requirements
@agent-backend-services prioritize features for implementation
```

### Perplexity Integration for Research

#### Real-Time Research Integration
```prompt
# Perplexity for current information

Research Flow:
1. Perplexity: "Latest best practices for [technology] in 2025"
2. Perplexity: "Recent security vulnerabilities in [framework]"
3. Perplexity: "Performance benchmarks for [database options]"

Claude Code:
@agent-technical-cto incorporate research findings
@agent-security-architecture address identified vulnerabilities
@agent-performance-optimization apply performance best practices
```

#### Fact-Checking Workflow
```prompt
# Validate technical decisions

@agent-master-orchestrator for each major decision:
1. Document the decision and rationale
2. Perplexity: Fact-check claims and assumptions
3. Find counter-arguments or alternatives
4. Update decision based on findings
5. Create ADR in Obsidian with references
```

### Cross-Platform Prompt Compatibility

#### Universal Prompt Structure
```prompt
# Prompts that work across all platforms

Structure:
1. Context: Clear project description
2. Constraints: Technical and business limitations
3. Objectives: Specific desired outcomes
4. Format: Required output structure

Example Universal Prompt:
"Project: B2B SaaS for team collaboration
Constraints: 6-week timeline, $50k budget, 3 developers
Objectives: MVP with core features, scalable architecture
Output: Technical specification and implementation plan"
```

#### Platform-Specific Adaptations
```prompt
# Adapt prompts for each platform's strengths

Base Prompt: "Design authentication system"

ChatGPT Version:
"Design a modern authentication system.
Compare JWT vs session-based approaches.
Consider security, scalability, and user experience."

Claude.ai Version:
"Analyze authentication requirements for enterprise B2B.
Address: SSO, MFA, compliance, audit trails.
Provide implementation recommendations."

Gemini Version:
"Review these authentication flow diagrams [images].
Suggest improvements for UX and security.
Consider mobile and desktop experiences."

Perplexity Version:
"Research current authentication best practices 2025.
Focus on: passwordless, biometric, blockchain auth.
Include recent breaches and lessons learned."
```

---

## 🪝 Hook System Integration

Advanced patterns for hook automation and custom workflows!

### Advanced Hook Chaining Patterns

#### Multi-Stage Hook Chain
```prompt
# Complex workflow automation with hooks

Hook Chain: Feature Development Pipeline

Trigger: New feature request
↓
Hook 1: Requirements Analysis
- @agent-business-analyst extracts requirements
- Validates against business goals
- Output: requirements.json
↓
Hook 2: Technical Planning  
- @agent-technical-cto assesses feasibility
- @agent-database-architecture designs schema
- Output: technical-plan.md
↓
Hook 3: Implementation
- @agent-backend-services builds API
- @agent-production-frontend creates UI
- Parallel execution
↓
Hook 4: Quality Assurance
- @agent-testing-automation runs tests
- @agent-security-architecture security scan
- Output: quality-report.md
↓
Hook 5: Deployment
- @agent-devops-engineering deploys
- Monitors initial performance
- Alerts on issues
```

#### Conditional Hook Execution
```prompt
# Hooks with branching logic

Conditional Deployment Hook:

IF (test_coverage > 80% AND security_scan == "passed") {
  Execute: Production deployment hook
  @agent-devops-engineering deploy to production
  @agent-project-manager notify stakeholders
} ELSE IF (test_coverage < 80%) {
  Execute: Test improvement hook
  @agent-testing-automation increase coverage
  @agent-quality-assurance review missing tests
} ELSE {
  Execute: Security fix hook
  @agent-security-architecture address vulnerabilities
  @agent-backend-services implement fixes
}
```

#### Event-Driven Hook Patterns
```prompt
# Hooks responding to system events

Event: API Response Time > 2 seconds

Triggered Hooks:
1. Performance Analysis Hook
   - @agent-performance-optimization analyze bottleneck
   - @agent-database-architecture check query performance
   
2. Caching Implementation Hook
   - @agent-middleware-specialist implement caching
   - @agent-backend-services add cache headers
   
3. Monitoring Enhancement Hook
   - @agent-devops-engineering add performance metrics
   - @agent-project-manager update SLA dashboard
```

### Custom Hook Development Guidelines

#### Hook Template Structure
```prompt
# Standard hook template

Hook Name: automated-code-review
Trigger: Pre-commit
Agents: @agent-quality-assurance, @agent-security-architecture

Hook Logic:
1. Scan changed files
2. Check coding standards
3. Run security analysis
4. Generate review report
5. Block commit if critical issues
6. Suggest improvements

Configuration:
- Severity levels: critical, major, minor
- Auto-fix: enabled for minor issues
- Report format: markdown
- Integration: Git hooks
```

#### Parameterized Hooks
```prompt
# Hooks with configuration options

Custom Hook: dynamic-scaling-monitor

Parameters:
- threshold_cpu: 70%
- threshold_memory: 80%
- scale_increment: 2 instances
- cooldown_period: 5 minutes
- max_instances: 10

Hook Behavior:
@agent-devops-engineering monitors resources
IF (cpu > threshold_cpu OR memory > threshold_memory):
  @agent-performance-optimization analyzes load
  @agent-devops-engineering scales up by scale_increment
  Wait for cooldown_period
  Re-evaluate
```

#### Hook Testing Framework
```prompt
# Test your custom hooks

@agent-testing-automation create hook test suite

Test Scenarios:
1. Normal execution path
2. Error conditions
3. Edge cases
4. Performance under load
5. Concurrent execution

Test Implementation:
- Mock agent responses
- Simulate triggers
- Verify outputs
- Measure execution time
- Check idempotency
```

### Hook + Agent + MCP Integration Flows

#### Complete Integration Example
```prompt
# Combining hooks, agents, and MCPs

Workflow: Automated Documentation System

Hook: documentation-update
Trigger: Code merge to main

Flow:
1. Hook activated on merge
2. @agent-technical-documentation analyzes changes
3. Brave Search: Find relevant documentation patterns
4. Generate updated docs
5. Obsidian: Create/update documentation pages
6. @agent-quality-assurance reviews documentation
7. Playwright: Screenshot new features
8. Obsidian: Embed screenshots in docs
9. Publish to documentation site
```

#### Intelligent Monitoring System
```prompt
# Self-improving monitoring with hooks and MCPs

System: Adaptive Performance Monitoring

Base Hook: performance-anomaly-detector
Agents: @agent-performance-optimization, @agent-devops-engineering
MCPs: Brave Search, Obsidian

Workflow:
1. Hook detects performance anomaly
2. @agent-performance-optimization investigates
3. Brave Search: Find similar issues and solutions
4. Implement suggested optimizations
5. Obsidian: Document issue and resolution
6. Hook learns from resolution
7. Updates detection parameters
8. Better anomaly detection next time
```

### Error Handling and Recovery Patterns

#### Graceful Degradation
```prompt
# Hooks with fallback mechanisms

Hook: payment-processing
Primary Flow: Stripe integration
Fallback Flow: PayPal integration
Emergency Flow: Queue for manual processing

Error Handling:
TRY {
  @agent-api-integration-specialist process with Stripe
} CATCH (StripeError) {
  Log error details
  @agent-api-integration-specialist try PayPal
} CATCH (AllPaymentErrors) {
  @agent-middleware-specialist queue transaction
  @agent-project-manager alert finance team
  Return "Payment queued" to user
}
```

#### Self-Healing Patterns
```prompt
# Hooks that fix themselves

Self-Healing Database Hook:

Monitors: Query performance
Threshold: >500ms average

Healing Actions:
1. @agent-database-architecture analyzes slow queries
2. Automatically adds missing indexes
3. Updates query execution plans
4. Monitors improvement
5. Rolls back if performance degrades
6. Learns from successful optimizations
```

#### Circuit Breaker Pattern
```prompt
# Prevent cascade failures

Circuit Breaker Hook: external-api-protection

States:
- Closed: Normal operation
- Open: Failing, reject requests
- Half-Open: Testing recovery

Implementation:
@agent-api-integration-specialist monitors API calls
Failure threshold: 5 errors in 1 minute
Open circuit: 30 seconds
Half-open test: 1 request
Full recovery: 3 successful requests

Fallback during open circuit:
- Return cached data
- Use alternative service
- Queue for later processing
```

---

## 📅 Session Management Patterns

Master multi-day projects and team collaboration!

### Multi-Day Project Continuity

#### Project State Management
```prompt
# Maintaining context across days/weeks

Project: Enterprise CRM System
Duration: 12 weeks

Daily Startup Routine:
/resume-project
@agent-master-orchestrator provide:
1. Current sprint status
2. Yesterday's accomplishments  
3. Today's priorities
4. Blockers and dependencies
5. Team member assignments

Weekly Checkpoint:
- Architecture decisions made
- Code completed and tested
- Documentation updated
- Technical debt identified
- Next week's plan
```

#### Milestone-Based Sessions
```prompt
# Organize long projects into clear phases

Project Phases:

Phase 1 (Weeks 1-2): Foundation
/new-project "Enterprise SaaS Platform"
@agent-master-orchestrator create phase plan
@agent-business-analyst complete requirements
@agent-database-architecture design core schema

Save Point: requirements-complete.md

Phase 2 (Weeks 3-5): Core Development
/resume-project
Load context: requirements-complete.md
@agent-backend-services build user management
@agent-production-frontend create admin panel

Save Point: core-features-complete.md

Phase 3 (Weeks 6-8): Integrations
/resume-project
Load context: core-features-complete.md
@agent-api-integration-specialist add payment processing
@agent-middleware-specialist implement job queues

[Continue pattern for all phases]
```

#### Context Preservation Strategy
```prompt
# Never lose important decisions

Automatic Context Capture:

1. Architecture Decisions
   - Stored in: /decisions/architecture/
   - Format: ADR (Architecture Decision Records)
   - Indexed by: Date, Impact, Technology

2. Code Patterns
   - Stored in: /patterns/
   - Examples of: API structure, component design
   - Referenced by: All agents

3. Project Evolution
   - Daily snapshots
   - Key decision points
   - Performance metrics
   - Test coverage trends

All agents reference this context automatically
```

### Team Collaboration Workflows

#### Distributed Team Pattern
```prompt
# Multiple team members working together

Team Setup:
- Frontend Developer: Uses @agent-production-frontend
- Backend Developer: Uses @agent-backend-services  
- DevOps Engineer: Uses @agent-devops-engineering
- QA Engineer: Uses @agent-testing-automation

Daily Sync Workflow:
Morning:
@agent-project-manager summarize overnight changes
Assign tasks based on dependencies

During Day:
Each member works with their agents
Commits include: [FRONTEND], [BACKEND], [DEVOPS] tags

End of Day:
@agent-master-orchestrator integration check
Identify conflicts or missing pieces
Plan next day's priorities
```

#### Handoff Protocols
```prompt
# Smooth transitions between team members

Handoff Template:

From: Backend Developer
To: Frontend Developer
Date: [Date]

Completed:
- User authentication API
- Endpoints: /login, /logout, /refresh
- Documentation: api-docs/auth.md

Ready for Frontend:
- Implement login form
- Handle JWT tokens
- Add refresh token logic

Notes:
- Rate limiting: 5 requests/minute
- Token expiry: 1 hour
- Refresh token: 7 days

Next Backend Tasks:
- User profile endpoints
- Permission system
```

#### Code Review Workflow
```prompt
# Collaborative code review process

Review Trigger: Pull request created

Step 1: Automated Review
@agent-quality-assurance initial code scan
@agent-security-architecture security check
@agent-testing-automation verify test coverage

Step 2: Peer Review Assignment
@agent-project-manager assign reviewers based on:
- Code ownership
- Expertise area
- Availability

Step 3: Review Process
Reviewers use agents for deep analysis:
@agent-performance-optimization check efficiency
@agent-database-architecture review queries
@agent-frontend-architecture assess UI patterns

Step 4: Feedback Integration
Author addresses feedback with agent help
Re-review if significant changes
Approval requires 2 reviewers + automated checks
```

### Version Control Integration

#### Git Workflow Automation
```prompt
# Integrated version control patterns

Branch Strategy with Agents:

Feature Development:
git checkout -b feature/user-authentication
@agent-backend-services implement auth logic
@agent-testing-automation write auth tests
@agent-quality-assurance review before commit

Commit Message Generation:
@agent-project-manager generate commit message based on:
- Changed files
- Feature description
- Issue reference
- Breaking changes

Example: "feat(auth): implement JWT authentication (#123)
- Add login/logout endpoints
- Implement refresh token logic
- Add rate limiting
- BREAKING: Changed token format"
```

#### Merge Conflict Resolution
```prompt
# Smart conflict resolution

Conflict Detection Hook:
@agent-master-orchestrator analyze conflicts
Categorize: Simple (formatting) vs Complex (logic)

Simple Conflicts:
@agent-quality-assurance auto-resolve formatting
Apply project coding standards
Verify no logic changes

Complex Conflicts:
@agent-backend-services understand both changes
Propose resolution options
Highlight business impact
Require human decision
@agent-testing-automation verify merged code
```

### State Synchronization Across Sessions

#### Distributed State Management
```prompt
# Keep everyone in sync

Central State Store:
Location: project-state.json
Updated: Every significant action
Accessed: Start of each session

Structure:
{
  "current_phase": "implementation",
  "active_features": ["auth", "user-profile"],
  "blocked_items": [{
    "feature": "payments",
    "blocker": "awaiting API keys",
    "assigned": "john"
  }],
  "recent_decisions": [...],
  "test_coverage": "82%",
  "deploy_status": "staging",
  "team_assignments": {...}
}

All agents read and update this state
```

#### Checkpoint and Restore
```prompt
# Save and restore complex states

Create Checkpoint:
@agent-master-orchestrator create checkpoint "pre-refactor"
Saves:
- All code state
- Database schema
- Configuration
- Documentation
- Test suites

Restore from Checkpoint:
/resume-project --from-checkpoint "pre-refactor"
@agent-master-orchestrator restore all state
Verify integrity
Continue from exact point
```

---

## 🌐 API and Webhook Patterns

Enterprise-grade integration patterns!

### External Service Integration via Agents

#### RESTful API Integration
```prompt
# Complete REST API integration

@agent-api-integration-specialist integrate external CRM API

Integration Requirements:
- Base URL: https://api.crm.com/v2
- Authentication: OAuth 2.0
- Rate limit: 1000 requests/hour
- Endpoints: Contacts, Deals, Activities

Implementation Plan:
1. OAuth flow implementation
2. Token management and refresh
3. Rate limiting with exponential backoff
4. Error handling and retries
5. Data transformation layer
6. Caching strategy

Deliverables:
- API client library
- Integration tests
- Error handling guide
- Performance benchmarks
```

#### GraphQL Integration Pattern
```prompt
# GraphQL API integration

@agent-api-integration-specialist implement GraphQL client

Configuration:
- Endpoint: https://api.service.com/graphql
- Authentication: API Key in header
- Subscriptions: WebSocket support
- Schema introspection: Enabled

Features to implement:
1. Query builder with type safety
2. Mutation handling
3. Subscription management
4. Fragment reuse
5. Cache normalization
6. Optimistic updates

Include error boundary for:
- Network failures
- Schema mismatches
- Rate limiting
```

#### Multi-Service Orchestration
```prompt
# Coordinating multiple external services

@agent-api-integration-specialist orchestrate services:

Services:
1. Payment: Stripe
2. Email: SendGrid  
3. SMS: Twilio
4. Storage: AWS S3
5. Analytics: Mixpanel

Orchestration Flow:
User Registration →
  ↓
Create Stripe customer →
  ↓
Send welcome email (SendGrid) →
  ↓
Send SMS verification (Twilio) →
  ↓
Upload profile image (S3) →
  ↓
Track event (Mixpanel)

Handle partial failures gracefully
Implement compensation transactions
```

### Webhook Handling with Appropriate Agents

#### Incoming Webhook Architecture
```prompt
# Robust webhook receiver implementation

@agent-backend-services create webhook receiver
@agent-security-architecture implement webhook security

Webhook Endpoints:
POST /webhooks/stripe/payment
POST /webhooks/github/push
POST /webhooks/slack/command

Security Measures:
1. Signature verification (HMAC-SHA256)
2. IP whitelist validation
3. Timestamp verification (5-min window)
4. Idempotency handling
5. Rate limiting per source
6. Request size limits

Processing Pipeline:
Receive → Validate → Queue → Process → Respond
```

#### Webhook Event Processing
```prompt
# Async webhook processing pattern

@agent-middleware-specialist design webhook processor

Queue Architecture:
- Incoming: Redis queue
- Processing: Bull job queue
- Failed: Dead letter queue
- Retry: Exponential backoff

Processing Flow:
@agent-backend-services webhook handler:
1. Quick validation and queue
2. Return 200 immediately
3. Process async:
   - Parse payload
   - Transform data
   - Execute business logic
   - Update database
   - Trigger notifications
4. Handle failures:
   - Retry 3 times
   - Move to DLQ
   - Alert on repeated failures
```

#### Outgoing Webhook System
```prompt
# Reliable webhook delivery system

@agent-backend-services build webhook dispatcher
@agent-middleware-specialist implement delivery queue

Features:
1. Event detection and filtering
2. Subscriber management
3. Payload construction
4. Signature generation
5. Delivery with retries
6. Failure handling

Delivery Strategy:
- Timeout: 30 seconds
- Retries: 5 times
- Backoff: 1, 2, 4, 8, 16 minutes
- Circuit breaker per endpoint
- Fallback to email notification
```

### CI/CD Pipeline Integration

#### GitHub Actions Integration
```prompt
# Automated deployment pipeline

@agent-devops-engineering create GitHub Actions workflow

Workflow Stages:
1. Code Check
   - Linting
   - Type checking
   - Security scan

2. Test Suite
   - Unit tests
   - Integration tests
   - E2E tests with Playwright

3. Build
   - Multi-stage Docker build
   - Optimize layers
   - Security scanning

4. Deploy
   - Staging first
   - Smoke tests
   - Production deployment
   - Health checks

5. Post-Deploy
   - Performance monitoring
   - Error rate tracking
   - Rollback if needed
```

#### GitLab CI Integration
```prompt
# GitLab CI/CD pipeline

@agent-devops-engineering implement .gitlab-ci.yml

Pipeline Structure:
stages:
  - validate
  - test
  - build
  - deploy
  - monitor

Include:
- Parallel job execution
- Docker-in-Docker for builds
- Kubernetes deployment
- Environment-specific variables
- Manual approval gates
- Artifact management
```

#### Jenkins Pipeline
```prompt
# Jenkins declarative pipeline

@agent-devops-engineering create Jenkinsfile

Pipeline Features:
- Multi-branch pipeline
- Docker agents
- Parallel stages
- Post-build actions
- Slack notifications
- Quality gates
- Artifact archiving
- Deployment to multiple environments
```

### Monitoring and Alerting Patterns

#### Comprehensive Monitoring Setup
```prompt
# Full monitoring implementation

@agent-devops-engineering implement monitoring stack
@agent-performance-optimization define metrics

Monitoring Layers:
1. Infrastructure
   - CPU, Memory, Disk
   - Network latency
   - Container health

2. Application
   - Request rate
   - Error rate
   - Response time
   - Active users

3. Business
   - Conversion rate
   - Revenue metrics
   - User engagement
   - Feature adoption

Tools Integration:
- Prometheus for metrics
- Grafana for visualization
- AlertManager for alerting
- ELK stack for logs
```

#### Alert Configuration
```prompt
# Smart alerting rules

@agent-devops-engineering configure alerts

Alert Categories:
1. Critical (Page immediately)
   - Service down
   - Data loss risk
   - Security breach
   - Payment failures

2. Warning (Notify team)
   - High error rate
   - Slow response time
   - Low disk space
   - Unusual traffic

3. Info (Log for review)
   - Deployment complete
   - Backup successful
   - Certificate renewal

Alert Routing:
- Critical → PagerDuty → On-call engineer
- Warning → Slack → Team channel
- Info → Email → Daily digest
```

#### Incident Response Automation
```prompt
# Automated incident response

@agent-devops-engineering create incident runbooks
@agent-master-orchestrator coordinate response

Incident Flow:
1. Alert triggered
2. Automatic diagnostics:
   - Collect logs
   - Capture metrics
   - Run health checks
3. Attempt auto-remediation:
   - Restart service
   - Scale resources
   - Clear cache
4. If not resolved:
   - Page on-call
   - Create incident channel
   - Start recording
5. Post-incident:
   - Generate report
   - Update runbooks
   - Schedule retrospective
```

---

## 🎯 Troubleshooting

Common issues and instant solutions!

### Issue: "Agent not responding"
**Solution**: Check exact spelling with `@agent-` prefix
```
❌ @backend-services
❌ @agent-backend
✅ @agent-backend-services
```

### Issue: "Costs too high"
**Solution**: Review agent selection
- Replace Opus agents with Default where possible
- Use Haiku for all testing and documentation
- Batch similar tasks together

### Issue: "Lost my progress"
**Solution**: Use `/resume-project`
```prompt
/resume-project
Show me the current state of the project
What was I working on last?
```

### Issue: "Agents giving generic responses"
**Solution**: Provide more context
- Add PDF references
- Include specific requirements
- Give examples of desired output

### Issue: "MCP tools not working"
**Solution**: Check installation
```bash
claude mcp list  # See installed tools
claude mcp add [tool]  # Add if missing
```

Remember: Maximum 3 MCPs per project!

---

## 📊 Complete Agent Reference

Detailed profiles of all 28 specialized agents.

### 🏢 Business Strategy Layer (4 Agents)

#### `@agent-business-analyst` 
**Model**: Opus 🧠 (Complex analysis)
**Expertise**: Market research, requirements, ROI
**When to Use**: Starting projects, feature validation
**Outputs**: Market analysis, user stories, business cases

#### `@agent-ceo-strategy`
**Model**: Opus 🧠 (Strategic thinking)
**Expertise**: Business models, go-to-market, positioning
**When to Use**: Product strategy, launch planning
**Outputs**: GTM strategies, positioning docs, roadmaps

#### `@agent-financial-analyst`
**Model**: Opus 🧠 (Financial modeling)
**Expertise**: Financial projections, pricing, unit economics
**When to Use**: Business case, pricing strategy
**Outputs**: Financial models, ROI calculations, pricing

#### `@agent-technical-cto`
**Model**: Opus 🧠 (Technical strategy)
**Expertise**: Tech feasibility, stack selection, architecture
**When to Use**: Technical decisions, risk assessment
**Outputs**: Feasibility reports, tech recommendations

### 💻 Development Layer (8 Agents)

#### `@agent-backend-services`
**Model**: Default ⚙️ (Standard development)
**Expertise**: APIs, business logic, database operations
**When to Use**: Building server-side features
**Outputs**: REST/GraphQL APIs, services, integrations

#### `@agent-frontend-mockup`
**Model**: Default ⚙️ (Rapid prototyping)
**Expertise**: HTML/CSS prototypes, UI concepts
**When to Use**: Quick UI validation, demos
**Outputs**: Interactive prototypes, mockups

#### `@agent-production-frontend`
**Model**: Default ⚙️ (Production UI)
**Expertise**: React, Vue, Angular, state management
**When to Use**: Building production UIs
**Outputs**: Component libraries, full applications

#### `@agent-api-integration-specialist`
**Model**: Default ⚙️ (Integration expert)
**Expertise**: Third-party APIs, webhooks, OAuth
**When to Use**: External service integration
**Outputs**: Integration code, webhook handlers

#### `@agent-database-architecture`
**Model**: Opus 🧠 (Data modeling)
**Expertise**: Schema design, optimization, migrations
**When to Use**: Database planning, performance
**Outputs**: ERDs, migration scripts, indexes

#### `@agent-middleware-specialist`
**Model**: Default ⚙️ (Infrastructure)
**Expertise**: Queues, caching, event systems
**When to Use**: Scalability, async processing
**Outputs**: Queue configs, cache strategies

#### `@agent-security-architecture`
**Model**: Opus 🧠 (Security critical)
**Expertise**: Security design, compliance, threats
**When to Use**: Security planning, audits
**Outputs**: Security docs, threat models

#### `@agent-performance-optimization`
**Model**: Default ⚙️ (Speed expert)
**Expertise**: Profiling, caching, optimization
**When to Use**: Performance issues, scaling
**Outputs**: Performance reports, optimizations

### 🧪 Quality Layer (6 Agents)

#### `@agent-testing-automation`
**Model**: Haiku 🏃 (Efficient testing)
**Expertise**: Unit, integration, E2E tests
**When to Use**: Test coverage, automation
**Outputs**: Test suites, coverage reports

#### `@agent-technical-documentation`
**Model**: Haiku 🏃 (Documentation)
**Expertise**: API docs, guides, tutorials
**When to Use**: Documentation needs
**Outputs**: Comprehensive documentation

#### `@agent-quality-assurance`
**Model**: Haiku 🏃 (Code quality)
**Expertise**: Code review, standards, best practices
**When to Use**: Quality checks, reviews
**Outputs**: Quality reports, recommendations

#### `@agent-devops-engineering`
**Model**: Default ⚙️ (Infrastructure)
**Expertise**: CI/CD, containers, deployment
**When to Use**: Deployment, automation
**Outputs**: Pipelines, configurations

#### `@agent-project-manager`
**Model**: Default ⚙️ (Coordination)
**Expertise**: Planning, timelines, resources
**When to Use**: Project planning, tracking
**Outputs**: Project plans, timelines

#### `@agent-prompt-engineer`
**Model**: Default ⚙️ (Optimization)
**Expertise**: Prompt optimization, efficiency
**When to Use**: Improving prompts
**Outputs**: Optimized prompts, workflows

### 🎯 Coordination Layer (2 Agents)

#### `@agent-master-orchestrator`
**Model**: Opus 🧠 (Master coordinator)
**Expertise**: Multi-agent coordination, complex projects
**When to Use**: Starting projects, complex coordination
**Outputs**: Project plans, coordination strategies

#### `@agent-usage-guide`
**Model**: Opus 🧠 (Meta-guidance)
**Expertise**: Claude Code workflows, best practices
**When to Use**: Learning, optimization
**Outputs**: Guides, recommendations

---

## 💰 Cost Calculator

Quick reference for budgeting your projects!

### Cost Per Call

| Model | Cost per Call | Relative Cost |
|-------|--------------|---------------|
| Opus 🧠 | $0.015 | 7.5x |
| Default ⚙️ | $0.008 | 4x |
| Haiku 🏃 | $0.002 | 1x |

### Project Cost Estimates

| Project Type | Complexity | Estimated Cost | Agent Calls |
|--------------|------------|----------------|-------------|
| Simple CRUD | Low | $0.02-0.04 | 10-20 calls |
| SaaS MVP | Medium | $0.10-0.20 | 50-100 calls |
| Enterprise | High | $0.30-0.50 | 150-250 calls |

### Cost Optimization Strategies

1. **The 60/30/10 Rule**
   - 60% Haiku (routine)
   - 30% Default (building)
   - 10% Opus (critical)

2. **Phase-Based Budgeting**
   - Planning: 20% Opus
   - Building: 60% Default
   - Testing: 20% Haiku

3. **Smart Selection**
   - Critical decisions → Opus
   - Implementation → Default
   - Documentation → Haiku

### ROI Calculator

```
Investment: $0.20 (100 optimized calls)
Time Saved: 40 hours development
Value: $4,000 (@ $100/hour)
ROI: 20,000% 🚀
```

---

## 📋 One-Page Cheat Sheet

**Print this page and keep it handy!**

### 🚀 Quick Start
```prompt
/new-project "Your Project Name"
@agent-master-orchestrator @agent-business-analyst
Describe what you want to build...
```

### 🎯 Essential Commands
```
/new-project      → Start fresh
/resume-project   → Continue work
@agent-           → Call specialist
"Let's ultrathink"→ Deep analysis
```

### 👥 Top Agents by Use Case
```
Planning     → @agent-master-orchestrator
Business     → @agent-business-analyst  
Backend API  → @agent-backend-services
Frontend UI  → @agent-production-frontend
Database     → @agent-database-architecture
Testing      → @agent-testing-automation
Deployment   → @agent-devops-engineering
```

### 💰 Model Strategy
```
Opus 🧠 ($$$$) → Critical thinking only
Default ⚙️ ($$) → Most development work
Haiku 🏃 ($)   → Tests & documentation
```

### 🛠️ MCP Tools (Max 3)
```
Playwright → Browser automation
Obsidian   → Knowledge management
Brave      → Web research
```

### 📋 AIMS Framework
```
A → Agent (who does the work)
I → Integration (what tools)
M → Method (which command)
S → Structure (organized prompt)
```

### 💡 Pro Tips
1. PDFs provide instant context
2. Sessions save automatically
3. Mix models to save 40-60%
4. Trust agent recommendations
5. Start simple, iterate fast

### 🆘 Quick Fixes
- Wrong agent? Check `@agent-` prefix
- High cost? Use more Haiku agents
- Lost work? Use `/resume-project`
- Need help? Ask `@agent-usage-guide`

---

## 🎉 You're Ready!

You now have everything needed to:
- ✅ Generate perfect Claude Code prompts
- ✅ Build complete applications efficiently  
- ✅ Save 40-60% on AI costs
- ✅ Coordinate 28 specialized agents like a pro

### Your First Step

1. Copy the [30-Second Quick Start](#-30-second-quick-start)
2. Paste into Claude Code
3. Describe your project
4. Let the agents guide you!

### Remember

- **Start Simple**: Use templates to begin
- **Trust the Process**: Agents know what they're doing
- **Optimize Later**: Get working first, optimize costs second
- **Have Fun**: You're building with AI superpowers!

---

<div align="center">

**Universal Meta-Prompting Guide v2.1 Enhanced**

*From Idea to Implementation in Record Time*

**Build Smarter. Build Faster. Build Better.**

[Back to Top](#-universal-meta-prompting-guide-v21---claude-code-dev-stack)

</div>