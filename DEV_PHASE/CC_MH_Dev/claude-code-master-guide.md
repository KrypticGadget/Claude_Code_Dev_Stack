# 🚀 Claude Code Stack Master Prompting Guide

## Overview
This guide enables any Claude instance to generate perfectly integrated prompts for the Claude Code Agent System, incorporating 28 specialized agents, 18 slash commands, and MCP (Model Context Protocol) tools.

## 🎯 Meta-Prompting Methodology

### Core Principle
Every prompt should follow the **AIMS** structure:
- **A**gent: Select the right agent(s) for the task
- **I**ntegration: Include relevant MCP tools
- **M**ethod: Choose appropriate slash commands
- **S**tructure: Format for optimal Claude Code execution

### Prompt Generation Formula
```
[Slash Command] + [Context] + [Constraints] + [MCP Tools] + [Agent Routing]
```

## 📋 Quick Reference Tables

### Slash Commands by Purpose
| Purpose | Command | Best For |
|---------|---------|----------|
| **Start Project** | `/new-project` | Complete project initialization with all analysis |
| **Resume Work** | `/resume-project` | Continue existing projects |
| **Frontend** | `/frontend-mockup` | UI prototypes and components |
| **Backend** | `/backend-service` | API design and services |
| **Database** | `/database-design` | Schema and data modeling |
| **Infrastructure** | `/cloud-setup` | AWS, Azure, GCP configuration |
| **Testing** | `/test-suite` | Comprehensive test generation |
| **Documentation** | `/documentation` | Technical docs and guides |
| **Security** | `/security-audit` | Vulnerability assessment |
| **Optimization** | `/optimize` | Performance improvements |

### Agent Specializations
| Category | Agents | Primary Use |
|----------|--------|-------------|
| **Orchestration** | AI Architect, Project Init | High-level coordination |
| **Business** | Business Analyst, Strategic Advisor | ROI, market analysis |
| **Architecture** | System/Solution Architect | Technical design |
| **Development** | Backend/Frontend Engineer | Implementation |
| **Quality** | QA Lead, Testing Engineer | Testing & validation |
| **DevOps** | DevOps Specialist, Cloud Specialist | Deployment & scaling |
| **Security** | Security Architect | Compliance & protection |

### MCP Tool Categories (Tier 1 Priority)
| Tool Type | Integration | Use Case |
|-----------|-------------|----------|
| **File System** | `@file-system` | Read/write project files |
| **Git** | `@git` | Version control operations |
| **Database** | `@database` | Direct DB queries |
| **API Testing** | `@api-test` | Endpoint validation |
| **Environment** | `@env-config` | Variable management |

## 🔥 Master Prompt Templates

### 1. Full Project Initialization
```
/new-project "[PROJECT_DESCRIPTION]"
Context: [BUSINESS_DOMAIN], [TARGET_USERS], [SCALE]
Constraints: Timeline: [WEEKS], Budget: [AMOUNT], Team: [SIZE]
Tech Stack: [PREFERRED_TECHNOLOGIES]
Integrations: [THIRD_PARTY_SERVICES]
MCP Tools: @file-system for structure, @git for initialization, @env-config for setup
Routing: Start with Strategic Advisor → Business Analyst → System Architect → [Specialized Agents]
```

### 2. Feature Development
```
/backend-service "[FEATURE_DESCRIPTION]"
Context: Existing project at [PROJECT_PATH]
Requirements: [FUNCTIONAL_REQUIREMENTS]
Constraints: [PERFORMANCE_NEEDS], [SECURITY_REQUIREMENTS]
MCP Tools: @file-system for code generation, @database for schema updates, @api-test for validation
Routing: Backend Engineer → Database Architect → API Gateway Specialist → Testing Engineer
```

### 3. Infrastructure & Deployment
```
/cloud-setup "[INFRASTRUCTURE_NEEDS]"
Environment: [DEV/STAGING/PROD]
Scale: [EXPECTED_LOAD]
Services: [REQUIRED_SERVICES]
MCP Tools: @env-config for secrets, @git for IaC, @file-system for configs
Routing: Cloud Infrastructure Specialist → DevOps Automation → Security Architect
```

## 🎨 Prompt Engineering Patterns

### Pattern 1: Progressive Enhancement
```
Step 1: /technical-feasibility "[IDEA]" constraints:[TECHNICAL_LIMITS]
Step 2: /project-plan based on feasibility results
Step 3: /new-project with refined scope
Step 4: Iterate with specific agents
```

### Pattern 2: Parallel Development
```
Concurrent Execution:
- /frontend-mockup "[UI_REQUIREMENTS]" → Frontend Architect
- /backend-service "[API_REQUIREMENTS]" → Backend Engineer  
- /database-design "[DATA_MODEL]" → Database Architect
Integration: API Gateway Specialist to connect all components
```

### Pattern 3: Security-First Approach
```
1. /security-audit requirements:[COMPLIANCE_NEEDS]
2. Apply security constraints to all subsequent commands
3. Route through Security Architect for all major decisions
4. Use @env-config MCP for secrets management
```

## 🔧 Advanced Integration Techniques

### Multi-Agent Collaboration Format
```
Task: [COMPLEX_REQUIREMENT]
Primary Agent: [LEAD_AGENT]
Supporting Agents: [AGENT_LIST]
Handoff Protocol:
  1. Lead agent creates initial design
  2. Supporting agents review and enhance
  3. Integration specialist merges outputs
MCP Coordination: @file-system for shared artifacts
```

### MCP Tool Chaining
```
Operation: [WORKFLOW_NAME]
Tool Chain:
  1. @git pull latest changes
  2. @file-system read current structure
  3. @database analyze schema
  4. Generate updates
  5. @api-test validate changes
  6. @git commit with descriptive message
```

### Conditional Routing
```
IF [CONDITION]:
  Route to [AGENT_A] with /[COMMAND_A]
  Use MCP tools: [TOOL_SET_A]
ELSE:
  Route to [AGENT_B] with /[COMMAND_B]
  Use MCP tools: [TOOL_SET_B]
```

## 📊 Optimization Strategies

### 1. Context Preservation
```
Project Context File: .claude-code/context.json
Contents:
- Project overview
- Current sprint goals
- Technical decisions log
- Active feature branches
MCP: @file-system to read/update context between sessions
```

### 2. Incremental Development
```
Iteration Pattern:
1. /resume-project with context
2. Small, focused prompts to specific agents
3. Frequent @git commits
4. Regular /code-review cycles
5. Continuous /test-suite updates
```

### 3. Quality Gates
```
Before Major Changes:
- /code-review by Code Reviewer agent
- /security-audit for sensitive features
- /test-suite for regression prevention
- Performance benchmarks via @api-test
```

## 🎯 Example: E-commerce Platform

### Initial Prompt
```
/new-project "E-commerce platform with multi-vendor support"
Context: B2B2C marketplace, expecting 10K vendors, 1M products
Constraints: 6-month timeline, $500K budget, team of 8
Tech Stack: React, Node.js, PostgreSQL, AWS
Key Features: 
- Multi-tenant architecture
- Real-time inventory
- Payment processing (Stripe)
- Advanced search with filters
MCP Tools: @file-system, @git, @database, @env-config
Initial Routing: Business Analyst → System Architect → parallel(Frontend Architect, Backend Engineer, Database Architect)
```

### Feature Development
```
/backend-service "Product search API with Elasticsearch"
Context: Existing e-commerce project
Requirements: 
- Full-text search across 1M products
- Faceted filtering
- Real-time inventory status
- Sub-100ms response time
MCP Tools: @database for PostgreSQL, @api-test for performance
Routing: Backend Engineer → Performance Optimization Specialist → API Gateway Specialist
```

## 🔄 Workflow Automation Hooks

### Pre-commit Hooks
```
Trigger: Before @git commit
Actions:
1. Run /code-review on changed files
2. Execute /test-suite for affected modules
3. Check /security-audit if security files modified
4. Update documentation if API changes
```

### Post-deployment Hooks
```
Trigger: After deployment
Actions:
1. /optimize performance metrics
2. Monitor via integrated MCP tools
3. Generate deployment report
4. Update project context
```

## 📝 Usage Instructions for Claude

When receiving this guide, Claude should:

1. **Analyze the user's request** to identify:
   - Project phase (new/existing)
   - Technical requirements
   - Constraints and context

2. **Select appropriate components**:
   - Primary slash command
   - Required agents (in order)
   - Necessary MCP tools

3. **Generate integrated prompt** following the AIMS structure

4. **Provide the prompt** with clear explanation of:
   - Why each component was selected
   - Expected execution flow
   - Integration points between agents

5. **Suggest follow-up actions** based on typical workflows

## 🚀 Quick Start Examples

### "I want to build a SaaS application"
```
/new-project "SaaS platform for [SPECIFIC_PURPOSE]"
Context: B2B, subscription-based, multi-tenant
Constraints: MVP in 3 months, scalable to 1000 customers
Tech Stack: [SPECIFY_OR_ASK_FOR_RECOMMENDATIONS]
MCP Tools: @file-system, @git, @database, @env-config
Routing: Business Analyst → Technical Feasibility → System Architect → specialized development agents
```

### "Add user authentication to my app"
```
/backend-service "JWT-based authentication system"
Context: Existing [FRAMEWORK] application
Requirements: Email/password, OAuth, 2FA support
Security: OWASP compliance, rate limiting
MCP Tools: @database for user schema, @env-config for secrets, @api-test for validation
Routing: Security Architect → Backend Engineer → Testing Engineer
```

### "Deploy my application"
```
/deploy "Production deployment pipeline"
Environment: AWS with auto-scaling
Requirements: Zero-downtime deployment, rollback capability
Monitoring: CloudWatch integration
MCP Tools: @env-config for production secrets, @git for tags
Routing: DevOps Automation Specialist → Cloud Infrastructure Specialist → Security Architect (final review)
```

---

## Meta-Prompt for Claude

When a user provides project requirements, generate prompts using this guide that:
1. Select the most appropriate slash command
2. Include all relevant context and constraints
3. Specify MCP tool integrations
4. Define agent routing order
5. Anticipate follow-up needs

Always format prompts for direct use in Claude Code, ensuring seamless integration between agents, commands, and tools.