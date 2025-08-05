# 🌐 MCP Integration Guide - Claude Code Dev Stack v2.1

## Core Principle: Agents Design, MCPs Execute

Your 28 agents handle all intellectual work. MCPs only handle what agents cannot: **interaction with external systems**.

---

## 🎯 The 3-5 MCP Rule

**Maximum MCPs**: 5 total (3 universal + 2 project-specific)

### Tier 1: Universal MCPs (Install These Today)
```bash
# 1. Browser Testing
claude mcp add playwright npx @playwright/mcp@latest

# 2. Knowledge Management  
claude mcp add obsidian

# 3. Research
claude mcp add brave-search
```

### Tier 2: Project-Specific (Choose ONE per category)

**Database (Pick ONE)**:
```bash
claude mcp add mongodb      # For document stores
claude mcp add postgresql   # For relational data
claude mcp add supabase    # For full-stack apps
```

**Deployment (Pick ONE)**:
```bash
claude mcp add gcp         # For enterprise scale
claude mcp add vercel      # For Next.js apps
claude mcp add netlify     # For static sites
```

---

## 📋 Agent-MCP Integration Patterns

### Pattern 1: Design → Execute → Verify
```yaml
Step 1: Agent designs (e.g., database schema)
Step 2: MCP executes (e.g., create tables)
Step 3: Agent verifies (e.g., validate schema)
```

### Pattern 2: Test-Driven Development
```yaml
Step 1: @agent-testing-automation[haiku] creates test specs
Step 2: Playwright MCP runs browser tests
Step 3: @agent-frontend-architecture fixes issues
Step 4: Repeat until passing
```

### Pattern 3: Knowledge Capture
```yaml
Continuous: All decisions → Obsidian MCP
Benefits: Searchable history, decision rationale, team knowledge
```

---

## 🔧 Configuration Files

### MCP Registry
**File**: `/mcp-configs/active-mcps.json`

```json
{
  "universal": {
    "playwright": {
      "purpose": "Browser testing",
      "installed": true,
      "primary_agents": ["@agent-testing-automation[haiku]", "@agent-quality-assurance[haiku]"]
    },
    "obsidian": {
      "purpose": "Knowledge management",
      "installed": true,
      "primary_agents": ["@agent-technical-documentation[haiku]", "@agent-master-orchestrator[opus]"]
    },
    "brave-search": {
      "purpose": "Research",
      "installed": true,
      "primary_agents": ["@agent-business-analyst[opus]", "@agent-ceo-strategy[opus]"]
    }
  },
  "project_specific": {
    "database": {
      "current": "mongodb",
      "purpose": "Data persistence",
      "primary_agents": ["@agent-database-architecture[opus]", "@agent-backend-services"]
    },
    "deployment": {
      "current": "vercel",
      "purpose": "Production hosting",
      "primary_agents": ["@agent-devops-engineering", "@agent-script-automation"]
    }
  },
  "mcp_count": 5,
  "limit": 5
}
```

### Agent MCP Bindings
**File**: `/mcp-configs/agent-bindings.json`

```json
{
  "@agent-testing-automation": {
    "primary_mcp": "playwright",
    "usage": "Run browser tests for all UI components"
  },
  "@agent-technical-documentation": {
    "primary_mcp": "obsidian",
    "usage": "Capture all technical decisions and rationale"
  },
  "@agent-database-architecture": {
    "primary_mcp": "mongodb",
    "usage": "Execute and validate schema designs"
  },
  "@agent-devops-engineering": {
    "primary_mcp": "vercel",
    "usage": "Deploy to staging and production"
  },
  "@agent-business-analyst": {
    "primary_mcp": "brave-search",
    "usage": "Research market trends and competitors"
  }
}
```

---

## 🚀 Quick Start Workflows

### New Project Setup
```bash
# 1. Agents design the system
/new-project "E-commerce platform" @agent-master-orchestrator[opus] @agent-business-analyst[opus]

# 2. Install project-specific MCPs
claude mcp add mongodb     # For product catalog
claude mcp add vercel      # For deployment

# 3. Agents + MCPs collaborate
"@agent-database-architecture[opus] create the product schema in MongoDB"
"Test the checkout flow with Playwright"
"Deploy staging environment to Vercel"
```

### Adding Authentication
```bash
# 1. Security Architect designs auth system
/security-audit "authentication requirements" @agent-security-architecture[opus]

# 2. Database Architect creates user schema
/database-design "user authentication tables" @agent-database-architecture[opus]

# 3. MongoDB MCP executes
"Create the user authentication schema in MongoDB"

# 4. Playwright MCP tests
"Test the login flow in Chrome and Safari"
```

### Performance Optimization
```bash
# 1. Performance Specialist analyzes
/optimize "page load performance" @agent-performance-optimization

# 2. Playwright MCP measures
"Run performance tests on key pages"

# 3. Obsidian MCP documents
"Document performance improvements and metrics"
```

---

## 📊 Integration Examples

### Example 1: Database Schema Execution
```typescript
// Agent generates this schema
const productSchema = {
  name: String,
  price: Number,
  inventory: Number,
  categories: [String]
}

// Then you say:
"@agent-database-architecture[opus] create this product schema in MongoDB with proper indexes"

// MCP executes in actual database
```

### Example 2: Browser Testing
```typescript
// Agent creates test specs
describe('Checkout Flow', () => {
  it('should process payment', async () => {
    // test implementation
  })
})

// Then you say:
"Run these checkout tests in Playwright across all browsers"

// MCP runs actual browser tests
```

### Example 3: Deployment
```yaml
# Agent creates deployment config
production:
  environment: production
  regions: [us-east-1, eu-west-1]
  scaling: auto

# Then you say:
"@agent-devops-engineering deploy to Vercel production with this configuration"

# MCP handles actual deployment
```

---

## ❌ What NOT to Use MCPs For

1. **Code Generation** - Agents handle this perfectly
2. **Architecture Design** - Pure intellectual work
3. **Documentation Writing** - Agents excel at this
4. **Planning** - Agent orchestration covers this
5. **Code Review** - Built into your agent system

**Remember**: If an agent can do it, don't add an MCP for it.

---

## 📈 Success Metrics

You're using MCPs correctly when:
- ✅ You have 5 or fewer MCPs total
- ✅ Each MCP has a clear, unique purpose
- ✅ Agents do the thinking, MCPs do the doing
- ✅ No duplication with agent capabilities
- ✅ Development is faster, not more complex

---

## 🔄 Migration Path for Existing Projects

### Week 1: Universal MCPs
```bash
# Monday: Install and test Playwright
claude mcp add playwright npx @playwright/mcp@latest
# Test with: "Run a simple browser test"

# Wednesday: Add Obsidian
claude mcp add obsidian
# Test with: "Document today's architectural decisions"

# Friday: Add Brave Search
claude mcp add brave-search
# Test with: "Research best practices for user authentication"
```

### Week 2: Project-Specific MCPs
```bash
# Evaluate your needs:
- What database are you using? → Add that MCP
- Where do you deploy? → Add that MCP
- Stop there! (5 MCP limit)
```

### Week 3: Optimize Workflows
- Create agent+MCP combination workflows
- Document patterns that work well
- Remove any redundant MCPs

---

## 🎯 Quick Reference Card

```
Universal MCPs (Always):
├── playwright    → Browser testing
├── obsidian      → Knowledge base
└── brave-search  → Research

Project Database (Choose 1):
├── mongodb       → NoSQL/Documents
├── postgresql    → Relational/SQL
└── supabase      → Full-stack DB

Project Deploy (Choose 1):
├── gcp           → Enterprise scale
├── vercel        → Next.js/React
└── netlify       → Static sites

Total: 5 MCPs maximum
```

---

## 🚀 Common Workflows

### Frontend Development Flow
```bash
# Design with agent
@agent-frontend-architecture[opus] design the user dashboard

# Build with agent
@agent-frontend-mockup create the dashboard components

# Test with MCP
"Run Playwright tests on the dashboard in all browsers"

# Document with MCP
"Save dashboard architecture decisions in Obsidian"
```

### Backend API Flow
```bash
# Design with agent
@agent-backend-services design REST API for users

# Implement with agent
@agent-backend-services implement the user endpoints

# Database with MCP
"Create user collection in MongoDB with indexes"

# Deploy with MCP
"Deploy API to Vercel staging environment"
```

### Research & Planning Flow
```bash
# Research with MCP
"Use Brave Search to find competitor pricing models"

# Analyze with agent
@agent-business-analyst[opus] analyze the research findings

# Document with MCP
"Save competitive analysis in Obsidian"

# Plan with agent
@agent-ceo-strategy[opus] create pricing strategy
```

---

## 🛠️ Troubleshooting

### MCP Not Working
1. Check installation: `claude mcp list`
2. Verify MCP is in approved list
3. Check mcp_gateway.py hook is active
4. Look for error messages

### Too Many MCPs Error
1. Review active MCPs: check `/mcp-configs/active-mcps.json`
2. Remove unused MCPs: `claude mcp remove [name]`
3. Consolidate functionality
4. Stay under 5 total

### Agent-MCP Coordination Issues
1. Check agent bindings in `/mcp-configs/agent-bindings.json`
2. Verify agent is using correct MCP
3. Review workflow patterns
4. Ensure clear separation of concerns

---

## 💡 Best Practices

### DO:
- ✅ Use MCPs for external system interaction only
- ✅ Let agents handle all intellectual work
- ✅ Document MCP decisions in Obsidian
- ✅ Test with Playwright for all UI changes
- ✅ Research with Brave for market insights

### DON'T:
- ❌ Add MCPs for tasks agents can do
- ❌ Exceed 5 MCPs total
- ❌ Use MCPs for code generation
- ❌ Duplicate functionality
- ❌ Complicate simple workflows

---

## 🚀 Next Steps

1. **Right Now**: Install the 3 universal MCPs (5 minutes)
2. **This Week**: Add 1 database + 1 deployment MCP for your project
3. **Ongoing**: Resist the urge to add more MCPs
4. **Remember**: Agents think, MCPs do, Hooks ensure

Your agents are brilliant. MCPs just give them hands to interact with the outside world. Keep it simple, keep it focused, keep it under 5 MCPs total.

---

*MCP Integration Guide v2.1 | Part of Claude Code Dev Stack*