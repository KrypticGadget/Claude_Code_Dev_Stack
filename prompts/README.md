# Claude Code Agent System - Prompt Templates

This directory contains ready-to-use prompt templates for various scenarios. Simply copy, customize the variables in brackets, and use with the Claude Code Agent System.

## Directory Structure

### 📁 project-initialization/
Templates for starting new projects from scratch.

- **[new-web-application.md](./project-initialization/new-web-application.md)** - Web apps, SaaS platforms, PWAs
- **[new-mobile-application.md](./project-initialization/new-mobile-application.md)** - iOS, Android, cross-platform apps
- **[new-api-service.md](./project-initialization/new-api-service.md)** - REST APIs, GraphQL, microservices
- **[new-enterprise-system.md](./project-initialization/new-enterprise-system.md)** - ERP, CRM, enterprise software

### 📁 development-workflows/
Templates for specific development tasks.

- **[frontend-development.md](./development-workflows/frontend-development.md)** - React, Vue, Angular workflows
- **[backend-development.md](./development-workflows/backend-development.md)** - APIs, services, integrations
- **[database-operations.md](./development-workflows/database-operations.md)** - Schema design, migrations, optimization
- **[devops-deployment.md](./development-workflows/devops-deployment.md)** - CI/CD, containerization, cloud

### 📁 industry-templates/
Industry-specific application templates.

- **[fintech-applications.md](./industry-templates/fintech-applications.md)** - Banking, payments, trading
- **[healthcare-applications.md](./industry-templates/healthcare-applications.md)** - EHR, telemedicine, HIPAA
- **[ecommerce-retail.md](./industry-templates/ecommerce-retail.md)** - Marketplaces, D2C, inventory
- **[education-edtech.md](./industry-templates/education-edtech.md)** - LMS, courses, virtual classroom

### 📁 specific-tasks/
Templates for quick, focused implementations.

- **[quick-implementations.md](./specific-tasks/quick-implementations.md)** - Auth, search, payments, etc.

### 📁 troubleshooting/
Templates for debugging and fixing issues.

- **[common-issues.md](./troubleshooting/common-issues.md)** - Performance, security, deployment

### 📁 optimization/
Templates for improving existing systems.

- **[performance-optimization.md](./optimization/performance-optimization.md)** - Speed, scaling, efficiency
- **[security-hardening.md](./optimization/security-hardening.md)** - Security improvements
- **[code-refactoring.md](./optimization/code-refactoring.md)** - Clean code, maintainability

## How to Use These Templates

### Method 1: Direct Agent Usage

#### 1. Choose Your Template
Browse the directories to find the template that matches your need.

#### 2. Copy the Prompt
Copy the relevant prompt from the template file.

#### 3. Replace Variables
Replace all `[BRACKETED VARIABLES]` with your specific values:
- `[APPLICATION TYPE]` → "task management"
- `[USER COUNT]` → "10,000"
- `[TECHNOLOGY]` → "React Native"

#### 4. Use in Claude Code
Paste the customized prompt into Claude Code:
```
> [Your customized prompt here]
```

### Method 2: Using Slash Commands (Recommended)

Many common operations have pre-built slash commands that are faster:

```bash
# Instead of copying and customizing a template:
/new-project "task management app for 10,000 users using React Native"

# Other quick commands:
/frontend-mockup "dashboard for analytics"
/backend-service "REST API with authentication"
/database-design "multi-tenant schema"
```

Install slash commands for instant access:
```bash
curl -sL https://raw.githubusercontent.com/yourusername/claude-code-agent-system/main/slash-commands/install-commands.sh | bash
```

## Quick Start Examples

### Starting a New SaaS Project

**Using Agent:**
```
> Use the master-orchestrator agent to begin new project: "Multi-tenant SaaS platform for project management with subscription billing, team collaboration, admin dashboard, and API access. Target market is small businesses with freemium pricing model."
```

**Using Slash Command:**
```
/new-project "Multi-tenant SaaS platform for project management with subscription billing"
```

### Adding Authentication

**Using Agent:**
```
> Use the security-architecture agent to implement JWT authentication for my application with refresh tokens and secure storage
```

**Using Slash Command:**
```
/api-integration "JWT auth" requirements:"refresh tokens, secure storage"
```

### Fixing Performance Issues

**Using Agent:**
```
> Use the performance-optimization agent to analyze slow API endpoint /api/products currently taking 2 seconds and optimize to under 200ms
```

**Note:** Performance optimization doesn't have a dedicated slash command yet - use the agent directly.

## Best Practices

### 1. Be Specific
The more specific your prompt, the better the results:
- ❌ "Build an e-commerce site"
- ✅ "E-commerce platform for handmade crafts with multi-vendor support, Etsy integration, and $50 average order value"

### 2. Include Constraints
Mention important constraints upfront:
- Timeline: "to be developed in 3 months"
- Budget: "with a $50K budget"
- Team: "by 2 developers"
- Compliance: "HIPAA compliant"

### 3. Specify Integrations
List any required third-party services:
- Payment: "integrated with Stripe and PayPal"
- Email: "using SendGrid for transactional emails"
- Analytics: "with Google Analytics and Mixpanel"

### 4. Define Success Metrics
Include performance requirements:
- Scale: "supporting 100K daily active users"
- Speed: "with sub-second page loads"
- Uptime: "99.9% availability SLA"

## Common Variable Reference

### Scale Variables
- `[USER COUNT]` - 1K, 10K, 100K, 1M users
- `[TRANSACTION VOLUME]` - 100, 10K, 1M per day
- `[DATA SIZE]` - GB, TB, PB

### Time Variables
- `[TIMELINE]` - 1 month, 3 months, 6 months
- `[RESPONSE TIME]` - 100ms, 1s, 5s
- `[FREQUENCY]` - hourly, daily, weekly

### Technology Variables
- `[FRAMEWORK]` - React, Vue, Angular, Next.js
- `[DATABASE]` - PostgreSQL, MongoDB, MySQL
- `[CLOUD PROVIDER]` - AWS, Azure, GCP

### Business Variables
- `[INDUSTRY]` - finance, healthcare, retail
- `[BUSINESS MODEL]` - B2B, B2C, marketplace
- `[PRICING MODEL]` - subscription, one-time, usage-based

## Getting Help

If you need help with:
- **Choosing a template**: Start with project initialization templates
- **Customizing prompts**: See the variables section in each template
- **Complex projects**: Use the master-orchestrator for guidance
- **Troubleshooting**: Check the troubleshooting directory

## Contributing

To add new prompt templates:
1. Create a new .md file in the appropriate directory
2. Follow the existing format with clear sections
3. Include variable placeholders with `[BRACKET NOTATION]`
4. Add examples and use cases
5. Submit a pull request

---

Remember: These templates are starting points. Feel free to combine multiple templates or customize them for your specific needs!