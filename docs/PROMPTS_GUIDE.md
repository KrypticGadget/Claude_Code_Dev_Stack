# Complete Prompts Guide - Claude Code Agent System

This guide explains the three types of prompts available in the Claude Code Agent System and how to use them effectively.

## 📋 Prompt Types Overview

The system provides three complementary prompt systems:

1. **Master Prompts** (`/master-prompts/`) - Universal, fill-in-the-blank templates
2. **Example Prompts** (`/prompts/`) - Scenario-specific examples with context
3. **Direct Agent Invocation** - Using agents directly with custom prompts

## 🎯 Master Prompts

Located in `/master-prompts/`, these are the most versatile prompts for any project.

### What Are Master Prompts?

Master prompts are universal templates with `[VARIABLES]` that you replace with your specific values. They're designed to work with any type of project, technology stack, or business domain.

### Available Master Prompts

#### 1. PROJECT-INITIALIZATION.md
For starting new projects from scratch:
```
> Use the master-orchestrator agent to begin new project: "[PROJECT_TYPE] for [TARGET_AUDIENCE] that [CORE_FUNCTIONALITY]"
```

#### 2. DEVELOPMENT-WORKFLOWS.md
For specific development tasks:
```
> Use the backend-services agent to create [API_TYPE] API for [DOMAIN] supporting [OPERATIONS]
```

#### 3. OPTIMIZATION-TASKS.md
For improving existing systems:
```
> Use the performance-optimization agent to optimize [APPLICATION_NAME] improving [METRIC_TYPE] from [CURRENT_VALUE] to [TARGET_VALUE]
```

#### 4. TROUBLESHOOTING.md
For debugging and fixing issues:
```
> Use the quality-assurance agent to investigate bug where [BUG_DESCRIPTION] occurs in [FEATURE/MODULE]
```

### How to Use Master Prompts

1. **Open the relevant file** in `/master-prompts/`
2. **Find the appropriate template** for your task
3. **Copy the entire prompt**
4. **Replace ALL bracketed variables** with your values
5. **Paste into Claude Code**

### Example: Using a Master Prompt

**Before (Template):**
```
> Use the master-orchestrator agent to begin new project: "[PROJECT_TYPE] for [TARGET_AUDIENCE] that [CORE_FUNCTIONALITY]. Key requirements: [REQUIREMENT_1], [REQUIREMENT_2], [REQUIREMENT_3]"
```

**After (Filled):**
```
> Use the master-orchestrator agent to begin new project: "E-commerce platform for small businesses that manages inventory and processes payments. Key requirements: multi-vendor support, mobile responsive, Stripe integration"
```

## 📝 Example Prompts

Located in `/prompts/`, these provide scenario-specific examples with more context.

### What Are Example Prompts?

Example prompts are pre-written scenarios for common use cases. They include industry context, typical requirements, and best practices. You can use them as-is or modify them for your needs.

### Directory Structure

```
prompts/
├── project-initialization/    # Starting new projects
├── development-workflows/     # Building features
├── industry-templates/        # Industry-specific apps
├── optimization/             # Improving performance
├── troubleshooting/          # Fixing issues
└── specific-tasks/           # Quick implementations
```

### When to Use Example Prompts

- When building industry-specific applications
- When you want to see best practices included
- When you need inspiration for your prompt
- When working on common scenarios

### Example: FinTech Application

From `/prompts/industry-templates/fintech-applications.md`:
```
> Use the master-orchestrator agent to begin new project: "Digital banking platform for millennials with mobile-first design, peer-to-peer payments, budgeting tools, and investment options. Must be PCI-DSS compliant with bank-grade security."
```

## 🚀 Direct Agent Invocation

The most flexible approach - invoke any agent directly with your custom prompt.

### Basic Pattern

```
> Use the [agent-name] agent to [your specific task]
```

### Examples

#### Business Analysis
```
> Use the business-analyst agent to evaluate the market opportunity for a subscription-based meal planning service targeting busy professionals in urban areas
```

#### Technical Architecture
```
> Use the technical-cto agent to design a microservices architecture for our e-learning platform that needs to support 50,000 concurrent users with live video streaming
```

#### Database Design
```
> Use the database-architecture agent to design a multi-tenant schema for our SaaS CRM that isolates customer data while allowing efficient queries across tenants
```

## 🔄 Combining Prompt Types

You can combine different prompt types for maximum effectiveness:

### 1. Start with Master Prompt
Use a master prompt to initialize your project with all requirements.

### 2. Add Example Context
Look at example prompts for industry-specific best practices.

### 3. Direct Agent Tasks
Use direct invocation for specific features or issues.

## 💡 Best Practices

### 1. Be Specific
The more detail you provide, the better the results:
- ❌ "Build a website"
- ✅ "Build a responsive e-commerce website for handmade jewelry with Shopify integration, supporting 1000 products"

### 2. Include Constraints
Always mention important limitations:
- Budget: "with a $25K budget"
- Timeline: "to launch in 2 months"
- Team: "for a team of 3 developers"
- Technology: "using React and Node.js"

### 3. Define Success Criteria
Include measurable goals:
- Performance: "page load under 2 seconds"
- Scale: "supporting 10,000 daily users"
- Quality: "with 90% test coverage"

### 4. Specify Integrations
List required third-party services:
- Payments: "Stripe for payments"
- Email: "SendGrid for emails"
- Storage: "AWS S3 for file storage"

## 📊 Variable Quick Reference

### Common Variables Used in Templates

#### Project Variables
- `[PROJECT_TYPE]` - web app, mobile app, API, platform
- `[PROJECT_NAME]` - your project's name
- `[TARGET_AUDIENCE]` - who will use it
- `[CORE_FUNCTIONALITY]` - main features

#### Technical Variables
- `[TECH_STACK]` - React, Vue, Python, etc.
- `[DATABASE]` - PostgreSQL, MongoDB, etc.
- `[CLOUD_PROVIDER]` - AWS, Azure, GCP
- `[API_TYPE]` - REST, GraphQL, gRPC

#### Business Variables
- `[BUSINESS_MODEL]` - B2B, B2C, marketplace
- `[PRICING_MODEL]` - subscription, one-time
- `[MARKET_SEGMENT]` - industry or niche
- `[REVENUE_TARGET]` - financial goals

#### Performance Variables
- `[USER_COUNT]` - expected users
- `[RESPONSE_TIME]` - performance targets
- `[UPTIME_REQUIREMENT]` - availability needs
- `[DATA_VOLUME]` - storage requirements

## 🎯 Which Prompt Type to Use?

### Use Master Prompts When:
- Starting any new project
- You want maximum customization
- Working on unique requirements
- Need a structured approach

### Use Example Prompts When:
- Building industry-specific apps
- Want to see best practices
- Need inspiration
- Working on common scenarios

### Use Direct Invocation When:
- Working on specific features
- Need quick answers
- Debugging issues
- Want maximum flexibility

## 📚 Learning Path

### Beginner
1. Start with example prompts to see patterns
2. Try master prompts with simple projects
3. Practice direct agent invocation

### Intermediate
1. Customize master prompts for complex projects
2. Combine multiple agents in workflows
3. Create your own prompt patterns

### Advanced
1. Chain multiple prompts for workflows
2. Create industry-specific templates
3. Optimize prompts for efficiency

## 🔗 Related Resources

- [Master Prompts README](/master-prompts/README.md) - Detailed master prompt guide
- [Example Prompts README](/prompts/README.md) - Example prompt catalog
- [Agent Catalog](/docs/architecture/agent-catalog.md) - All 28 agents reference
- [Agent Usage Guide](/docs/AGENT_USAGE.md) - How to use agents effectively

---

Remember: The best prompt is one that clearly communicates your needs. Start simple, then add detail as needed!