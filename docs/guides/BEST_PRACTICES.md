# Best Practices - Peak Performance with Claude Code Dev Stack

## 🎯 Core Principles

### 1. Start with Slash Commands
```bash
# Good
/new-project "E-commerce site"

# Better - add specificity
/new-project "E-commerce site with Stripe and inventory management"

# Best - add key agents
/new-project "E-commerce site with Stripe" @agent-system-architect @agent-payment-integration
```

### 2. Use Agent Teams, Not Individuals
```bash
# Solo agent (limited perspective)
@agent-backend-engineer "Build API"

# Agent team (comprehensive solution)
@agent-backend-engineer @agent-security-architect @agent-api-integration-specialist "Build secure API with third-party integrations"
```

### 3. Trust the Automation
- Let hooks handle session management
- Don't specify models (hooks optimize)
- Don't repeat context (agents remember)

## 🚀 Power Patterns

### Progressive Enhancement
```bash
# Start simple
/backend-service "Basic CRUD"

# Layer in complexity
@agent-security-architect "Add authentication"
@agent-performance-optimization "Optimize queries"
@agent-api-integration-specialist "Add Stripe"
```

### Domain-Specific Teams
```bash
# E-commerce Team
@agent-system-architect @agent-payment-integration @agent-database-architect

# SaaS Team  
@agent-system-architect @agent-security-architect @agent-business-analyst

# Mobile Team
@agent-frontend-architect @agent-api-integration-specialist @agent-performance-optimization
```

## 💡 Meta Prompting Strategy

Use for complex, multi-faceted projects:

1. Open any LLM
2. Load UNIVERSAL_META_PROMPTING_GUIDE.md
3. Describe complete requirements
4. Get orchestrated prompt
5. Execute in Claude Code

## ⚡ Performance Tips

### Speed
- Slash commands: 10x faster than explaining
- Agent teams: Complete solutions first try
- Meta prompting: Complex projects simplified

### Cost
- Let hooks choose models (60% savings)
- Use specific agents (focused = cheaper)
- Batch related tasks (context reuse)

### Quality
- Always include @agent-security-architect
- Add @agent-testing-automation for critical features
- Use @agent-documentation-specialist for docs

## 🚫 Anti-Patterns to Avoid

1. **Over-specifying**
   ```bash
   # Bad - too much detail
   @agent-backend-engineer "Create a REST API with Express.js using..."
   
   # Good - let agent decide implementation
   @agent-backend-engineer "Create user management API"
   ```

2. **Using too many MCPs**
   - Stick to the 3 essentials
   - Don't add MCPs "just in case"

3. **Ignoring slash commands**
   - They trigger optimized workflows
   - Always start with a command when possible

## 📊 Success Metrics

You're using the stack optimally when:
- Projects complete 10x faster
- API costs drop 60%
- Code quality improves consistently
- Less back-and-forth clarification
- Agents work together seamlessly