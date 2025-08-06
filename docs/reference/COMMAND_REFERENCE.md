# Slash Command Reference Guide

Complete reference for all 18 slash commands in the Claude Code Dev Stack system.

## Overview

Slash commands provide rapid access to common agent workflows. All commands start with `/` and support parameters.

### Command Syntax
```
/command-name "main parameter" option:value flag:true
```

## Complete Command List

### 🚀 Project Management Commands

#### `/new-project`
**Purpose:** Start a new project with full orchestration
**Syntax:** `/new-project "project description"`
**Example:**
```
/new-project "B2B SaaS platform for team collaboration"
```
**Triggers:** master-orchestrator → business-analyst → technical-cto → full project setup

#### `/resume-project`
**Purpose:** Continue work on an existing project
**Syntax:** `/resume-project "project name or context"`
**Example:**
```
/resume-project "team collaboration platform"
```
**Features:** Loads project context, resumes from last checkpoint

### 💼 Business & Analysis Commands

#### `/business-analysis`
**Purpose:** Comprehensive business analysis for ideas or markets
**Syntax:** `/business-analysis`
**Interactive:** Prompts for business idea, market, and goals
**Outputs:** Market analysis, competitive landscape, ROI projections, business model

#### `/technical-feasibility`
**Purpose:** Assess technical viability and requirements
**Syntax:** `/technical-feasibility "project description"`
**Example:**
```
/technical-feasibility "real-time collaborative editing platform"
```
**Outputs:** Tech stack recommendations, scalability analysis, risk assessment

### 🏗️ Architecture & Design Commands

#### `/architecture-design`
**Purpose:** Create comprehensive system architecture
**Syntax:** `/architecture-design "system requirements"`
**Example:**
```
/architecture-design "microservices-based e-commerce platform"
```
**Outputs:** Architecture diagrams, component design, data flow, deployment strategy

#### `/database-design`
**Purpose:** Design database schema and data models
**Syntax:** `/database-design "system type"`
**Example:**
```
/database-design "multi-tenant SaaS application"
```
**Outputs:** Schema design, relationships, indexes, migration strategy

#### `/api-design`
**Purpose:** Design RESTful or GraphQL APIs
**Syntax:** `/api-design "api requirements"`
**Example:**
```
/api-design "payment processing API with webhooks"
```
**Outputs:** Endpoint design, authentication, documentation, SDK templates

### 💻 Development Commands

#### `/frontend-mockup`
**Purpose:** Create interactive HTML/CSS mockups
**Syntax:** `/frontend-mockup "ui description"`
**Example:**
```
/frontend-mockup "dashboard with analytics charts and user management"
```
**Outputs:** HTML/CSS files, responsive design, interactive elements

#### `/backend-implementation`
**Purpose:** Implement backend services and APIs
**Syntax:** `/backend-implementation "service requirements"`
**Example:**
```
/backend-implementation "user authentication service with JWT"
```
**Outputs:** Service code, API endpoints, middleware, database integration

#### `/full-stack-app`
**Purpose:** Build complete full-stack applications
**Syntax:** `/full-stack-app "application description"`
**Example:**
```
/full-stack-app "task management app with real-time updates"
```
**Outputs:** Frontend + backend code, database setup, deployment config

### 🧪 Testing & Quality Commands

#### `/test-suite`
**Purpose:** Generate comprehensive test suites
**Syntax:** `/test-suite "component or system"`
**Example:**
```
/test-suite "user authentication module"
```
**Outputs:** Unit tests, integration tests, E2E tests, test documentation

#### `/code-review`
**Purpose:** Perform thorough code review and quality analysis
**Syntax:** `/code-review`
**Interactive:** Analyzes current codebase or specified files
**Outputs:** Code quality report, suggestions, refactoring recommendations

### 🔧 DevOps & Deployment Commands

#### `/deployment-setup`
**Purpose:** Create deployment configurations and CI/CD pipelines
**Syntax:** `/deployment-setup "platform"`
**Options:** `platform:aws|gcp|azure|vercel|netlify`
**Example:**
```
/deployment-setup "aws" monitoring:true auto-scale:true
```
**Outputs:** Deployment scripts, CI/CD config, monitoring setup

#### `/docker-setup`
**Purpose:** Create Docker configurations for containerization
**Syntax:** `/docker-setup`
**Outputs:** Dockerfile, docker-compose.yml, build scripts, orchestration config

### 📚 Documentation Commands

#### `/documentation`
**Purpose:** Generate comprehensive project documentation
**Syntax:** `/documentation "type"`
**Options:** `type:api|user|technical|all`
**Example:**
```
/documentation "api" format:openapi examples:true
```
**Outputs:** Formatted documentation, API specs, user guides, README files

#### `/prompt-enhance`
**Purpose:** Improve and clarify prompts for better results
**Syntax:** `/prompt-enhance "your prompt"`
**Example:**
```
/prompt-enhance "make a website for selling things"
```
**Outputs:** Enhanced prompt with context, specifications, and agent recommendations

### 🔒 Security & Performance Commands

#### `/security-audit`
**Purpose:** Perform comprehensive security analysis
**Syntax:** `/security-audit`
**Outputs:** Security report, vulnerability assessment, recommendations, fixes

#### `/performance-optimization`
**Purpose:** Analyze and optimize application performance
**Syntax:** `/performance-optimization "focus area"`
**Options:** `focus:frontend|backend|database|all`
**Example:**
```
/performance-optimization "database" analyze:queries cache:true
```
**Outputs:** Performance report, optimization recommendations, implementation guide

## Command Options & Flags

### Common Options
- `language:` - Programming language preference (js, python, java, etc.)
- `framework:` - Framework selection (react, django, spring, etc.)
- `style:` - Code style (functional, oop, minimal, etc.)
- `complexity:` - Project complexity (simple, moderate, complex)

### Common Flags
- `interactive:true` - Enable interactive mode
- `verbose:true` - Detailed output
- `test:true` - Include test generation
- `docs:true` - Include documentation

## Workflow Examples

### Complete Project Setup
```bash
# 1. Start new project
/new-project "E-commerce marketplace"

# 2. Design architecture
/architecture-design "microservices with event-driven architecture"

# 3. Design database
/database-design "multi-vendor marketplace"

# 4. Create API
/api-design "REST API with GraphQL gateway"

# 5. Build frontend
/frontend-mockup "marketplace with vendor dashboards"

# 6. Implement backend
/backend-implementation "order processing and payment system"

# 7. Add tests
/test-suite "complete application"

# 8. Setup deployment
/deployment-setup "aws" auto-scale:true monitoring:true
```

### Quick Prototype
```bash
# 1. Quick mockup
/frontend-mockup "landing page with signup"

# 2. Simple backend
/backend-implementation "user registration API"

# 3. Deploy
/deployment-setup "vercel"
```

## Best Practices

1. **Use Commands for Speed:** Slash commands are 3-5x faster than agent invocation
2. **Combine Commands:** Chain commands for complete workflows
3. **Specify Options:** Use options to get exactly what you need
4. **Interactive Mode:** Use `interactive:true` for guided experiences
5. **Context Matters:** Commands remember context within a session

## Command Aliases (Coming Soon)

Future update will include short aliases:
- `/np` → `/new-project`
- `/ba` → `/business-analysis`
- `/fm` → `/frontend-mockup`
- `/ds` → `/deployment-setup`

## Troubleshooting

### Command Not Working?
1. Ensure correct syntax with quotes around parameters
2. Check if required agents are available
3. Use `/prompt-enhance` to clarify your request

### Need Help?
- Use `/help` for command list
- Use `/help command-name` for specific command help
- Check agent documentation for underlying functionality

Remember: Slash commands are productivity shortcuts. For complex custom workflows, use direct agent invocation.