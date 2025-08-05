# 🌐 MCP Integration Guide - Claude Code Dev Stack

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
Step 1: Testing Engineer creates test specs
Step 2: Playwright MCP runs browser tests
Step 3: Frontend Architect fixes issues
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
      "primary_agents": ["testing-engineer", "qa-lead"]
    },
    "obsidian": {
      "purpose": "Knowledge management",
      "installed": true,
      "primary_agents": ["documentation-specialist", "architect"]
    },
    "brave-search": {
      "purpose": "Research",
      "installed": true,
      "primary_agents": ["requirements-analyst", "business-analyst"]
    }
  },
  "project_specific": {
    "database": {
      "current": "mongodb",
      "purpose": "Data persistence",
      "primary_agents": ["database-architect", "backend-engineer"]
    },
    "deployment": {
      "current": "vercel",
      "purpose": "Production hosting",
      "primary_agents": ["devops-specialist", "cloud-architect"]
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
  "testing-engineer": {
    "primary_mcp": "playwright",
    "usage": "Run browser tests for all UI components"
  },
  "documentation-specialist": {
    "primary_mcp": "obsidian",
    "usage": "Capture all technical decisions and rationale"
  },
  "database-architect": {
    "primary_mcp": "mongodb",
    "usage": "Execute and validate schema designs"
  },
  "devops-specialist": {
    "primary_mcp": "vercel",
    "usage": "Deploy to staging and production"
  },
  "requirements-analyst": {
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
/new-project "E-commerce platform"

# 2. Install project-specific MCPs
claude mcp add mongodb     # For product catalog
claude mcp add vercel      # For deployment

# 3. Agents + MCPs collaborate
"Create the product schema in MongoDB"
"Test the checkout flow with Playwright"
"Deploy staging environment to Vercel"
```

### Adding Authentication
```bash
# 1. Security Architect designs auth system
/security-audit "authentication requirements"

# 2. Database Architect creates user schema
/database-design "user authentication tables"

# 3. MongoDB MCP executes
"Create the user authentication schema in MongoDB"

# 4. Playwright MCP tests
"Test the login flow in Chrome and Safari"
```

### Performance Optimization
```bash
# 1. Performance Specialist analyzes
/optimize "page load performance"

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
"Create this product schema in MongoDB with proper indexes"

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
"Deploy to Vercel production with this configuration"

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

## 🚀 Next Steps

1. **Right Now**: Install the 3 universal MCPs (5 minutes)
2. **This Week**: Add 1 database + 1 deployment MCP for your project
3. **Ongoing**: Resist the urge to add more MCPs
4. **Remember**: Agents think, MCPs do, Hooks ensure

Your agents are brilliant. MCPs just give them hands to interact with the outside world. Keep it simple, keep it focused, keep it under 5 MCPs total.