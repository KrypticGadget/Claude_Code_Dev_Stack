# Meta Prompting with Claude Code Dev Stack

## What is Meta Prompting?

Meta prompting is using AI to generate perfect prompts for Claude Code. It's like having an expert prompt engineer create your development instructions.

## When to Use Meta Prompting

### Perfect for:
- Complex multi-component systems
- Projects requiring 5+ agents
- Intricate business logic
- Cross-functional requirements

### Examples:
- Multi-tenant SaaS platforms
- E-commerce with complex integrations
- Enterprise applications
- Real-time collaborative tools

## How to Use

### Step 1: Choose Your AI
Works with any LLM:
- ChatGPT
- Claude.ai
- Gemini
- Local LLMs

### Step 2: Load the Guide
Copy and paste the entire content of:
```
UNIVERSAL_META_PROMPTING_GUIDE.md
```

### Step 3: Describe Your Project
Be specific about:
- Business requirements
- Technical constraints
- Integration needs
- Performance requirements
- Security concerns

### Step 4: Receive Your Prompt
The AI will generate a complete Claude Code prompt with:
- Appropriate slash command
- Optimal agent selection
- Correct execution order
- Specific instructions

### Example Meta Prompt Input
```
I need a B2B SaaS platform with:
- Multi-tenant architecture
- Usage-based billing with Stripe
- Real-time collaboration features
- Enterprise SSO support
- Audit logging
- Role-based permissions
```

### Example Generated Output
```bash
/new-project "B2B SaaS Platform with multi-tenancy and real-time collaboration"

@agent-system-architect Design microservices architecture with tenant isolation
@agent-database-architect Create PostgreSQL schema with row-level security for multi-tenancy
@agent-backend-engineer Implement WebSocket architecture for collaboration
@agent-api-integration-specialist Set up Stripe with usage-based billing and webhook handling
@agent-security-architect Implement SAML SSO and comprehensive audit logging
@agent-frontend-architect Design RBAC system with tenant-aware permissions
@agent-devops-engineer Create Kubernetes deployment with tenant isolation
@agent-performance-optimization Set up per-tenant metrics and alerting
```

## Best Practices

1. **Be specific** about requirements
2. **Include constraints** (budget, timeline, tech stack)
3. **Mention integrations** explicitly
4. **Describe the end user** clearly
5. **Note compliance needs** (GDPR, HIPAA, etc.)

## Power Tips

- Use meta prompting for initial architecture
- Regular prompts for incremental features
- Combine both approaches for best results