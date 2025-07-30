# Agent Usage Guide

Learn how to effectively use the 28 specialized agents in the Claude Code Agent System.

## Understanding Agent Activation

### Method 1: Direct Agent Invocation
Agents are invoked using this pattern:
```
> Use the [agent-name] agent to [specific task]
```

### Method 2: Slash Commands (Faster!)
Pre-built shortcuts for common agent tasks:
```
/command-name "parameters" variable:value
```

### Automatic Activation
Some agents activate automatically based on keywords:
- "MUST BE USED" agents trigger on specific terms
- "Use proactively" agents activate when appropriate
- Master orchestrator activates for new projects

## Quick Comparison: Agents vs Slash Commands

| Task | Agent Method | Slash Command |
|------|--------------|---------------|
| Start project | `> Use the master-orchestrator agent to begin new project: "desc"` | `/new-project "desc"` |
| Business analysis | `> Use the business-analyst agent to analyze market` | `/business-analysis` |
| Create mockup | `> Use the frontend-mockup agent to create prototype` | `/frontend-mockup "desc"` |
| Design database | `> Use the database-architecture agent to design schema` | `/database-design "system"` |

## Agent Categories and When to Use Them

### 🎯 Orchestration Agents

#### Master Orchestrator
**When to use:**
- Starting any new project
- Coordinating multiple agents
- Managing complex workflows
- Need end-to-end project management

**Examples:**
```
# Agent method
> Use the master-orchestrator agent to begin new project: "SaaS platform for team collaboration"

# Slash command (faster)
/new-project "SaaS platform for team collaboration"
```

#### Prompt Engineer
**When to use:**
- Have a vague or incomplete request
- Need to optimize prompts for better results
- Want to add context to requests

**Examples:**
```
# Agent method
> Use the prompt-engineer agent to improve my request: "make a website"

# Slash command
/prompt-enhance "make a website"
```

### 💼 Business & Strategy Agents

#### Business Analyst
**When to use:**
- Need market analysis
- ROI calculations
- Competitive analysis
- Business viability assessment

**Examples:**
```
# Agent method
> Use the business-analyst agent to analyze market opportunity for meal delivery app

# Slash command
/business-analysis
```
- Calculating ROI
- Validating business ideas
- Competitive research

**Example:**
```
> Use the business-analyst agent to analyze market opportunity for a B2B analytics platform
```

#### Technical CTO
**When to use:**
- Technology stack decisions
- Scalability planning
- Technical feasibility studies
- Architecture reviews

#### CEO Strategy
**When to use:**
- Pricing strategy
- Go-to-market planning
- Product positioning
- Strategic partnerships

#### Financial Analyst
**When to use:**
- Financial projections
- Unit economics
- Budget planning
- Investment analysis

### 📋 Planning & Management Agents

#### Project Manager
**When to use:**
- Creating timelines
- Resource allocation
- Sprint planning
- Risk management

#### Technical Specifications
**When to use:**
- Documenting requirements
- API specifications
- System design documents
- Integration planning

#### Business-Tech Alignment
**When to use:**
- Ensuring tech serves business goals
- ROI-driven decisions
- Cost-benefit analysis
- Trade-off evaluation

### 🏗️ Architecture & Design Agents

#### Frontend Architecture
**When to use:**
- Information architecture
- Site mapping
- Navigation design
- Component hierarchy planning

#### Frontend Mockup
**When to use:**
- Creating prototypes
- HTML/CSS mockups
- Design validation
- Quick UI demonstrations

#### UI/UX Design
**When to use:**
- User experience design
- Accessibility compliance
- Design systems
- Usability improvements

#### Database Architecture
**When to use:**
- Schema design
- Query optimization
- Data modeling
- Migration planning

#### API Integration Specialist
**When to use:**
- Third-party integrations
- Webhook implementation
- API gateway design
- External service connections

### 💻 Development Agents

#### Production Frontend
**When to use:**
- Building React/Vue/Angular apps
- Frontend implementation
- Component development
- Performance optimization

#### Backend Services
**When to use:**
- API development
- Business logic implementation
- Service architecture
- Microservices design

#### Mobile Development
**When to use:**
- iOS/Android apps
- React Native development
- Mobile-specific features
- App store deployment

#### Middleware Specialist
**When to use:**
- Message queues
- Event streaming
- Service mesh
- Caching layers

### 🔧 DevOps & Operations Agents

#### DevOps Engineering
**When to use:**
- CI/CD pipelines
- Infrastructure as Code
- Container orchestration
- Cloud deployment

#### Integration Setup
**When to use:**
- Environment configuration
- Dependency management
- Development setup
- Troubleshooting setup issues

#### Script Automation
**When to use:**
- Build scripts
- Deployment automation
- Task automation
- Workflow scripts

#### Development Prompt
**When to use:**
- Generating command sequences
- Complex workflow automation
- Multi-step processes

### 🛡️ Quality & Security Agents

#### Security Architecture
**When to use:**
- Security audits
- Compliance implementation
- Threat modeling
- Vulnerability assessment

#### Performance Optimization
**When to use:**
- Performance issues
- Load testing
- Optimization strategies
- Scalability improvements

#### Quality Assurance
**When to use:**
- Code reviews
- Best practices enforcement
- Technical debt assessment
- Code quality metrics

#### Testing Automation
**When to use:**
- Test strategy design
- Test implementation
- Coverage improvement
- Test maintenance

### 📚 Documentation Agents

#### Technical Documentation
**When to use:**
- Architecture documentation
- API documentation
- Developer guides
- System documentation

#### Usage Guide
**When to use:**
- User manuals
- Getting started guides
- Feature documentation
- Best practices guides

## Effective Agent Combinations

### Full Stack Web Application
```
1. master-orchestrator → Initial planning
2. business-analyst → Market validation  
3. technical-cto → Tech stack selection
4. frontend-architecture + backend-services → Parallel development
5. testing-automation → Test implementation
6. devops-engineering → Deployment
```

### API Service
```
1. technical-specifications → API design
2. backend-services → Implementation
3. api-integration-specialist → External integrations
4. security-architecture → Security review
5. technical-documentation → API docs
```

### Mobile Application
```
1. business-analyst → Market research
2. ui-ux-design → User experience
3. mobile-development → App development
4. backend-services → API backend
5. testing-automation → Mobile testing
```

## Advanced Usage Patterns

### Parallel Agent Execution
Some agents can work simultaneously:
```
> Use the frontend-architecture agent to design the user interface while the database-architecture agent designs the data model
```

### Sequential Workflows
Chain agents for complex tasks:
```
> Use the business-analyst agent to validate the idea, then use the technical-cto agent to assess feasibility, then use the project-manager agent to create a timeline
```

### Iterative Refinement
Use agents multiple times:
```
> Use the performance-optimization agent to identify bottlenecks
[Review results]
> Use the performance-optimization agent to implement the recommended optimizations
```

## Best Practices

### 1. Start with the Right Agent
- For new projects: Always start with master-orchestrator
- For specific tasks: Use the specialized agent directly
- When unsure: Check the agent catalog

### 2. Provide Context
- Include relevant background information
- Specify constraints and requirements
- Mention existing systems or technologies

### 3. Be Specific
- Clear, measurable objectives
- Defined success criteria
- Specific technologies when relevant

### 4. Use Templates
- Leverage master-prompts for consistency
- Customize variables appropriately
- Save successful prompts for reuse

### 5. Monitor Output Quality
- Review agent recommendations
- Validate technical decisions
- Ensure business alignment

## Using Slash Commands

### Installation
```bash
# Install slash commands (one-time setup)
curl -sL https://raw.githubusercontent.com/yourusername/claude-code-agent-system/main/slash-commands/install-commands.sh | bash
```

### Available Commands

#### Project & Planning
- `/new-project` - Start comprehensive project
- `/business-analysis` - Analyze ROI and market
- `/technical-feasibility` - Assess tech options
- `/project-plan` - Create timeline and resources
- `/requirements` - Document specifications

#### Development
- `/frontend-mockup` - Create HTML/CSS prototype
- `/production-frontend` - Build React/Vue/Angular
- `/backend-service` - Design APIs and services
- `/database-design` - Create database schema
- `/api-integration` - Integrate external APIs

#### Strategy & Operations
- `/financial-model` - Financial projections
- `/go-to-market` - Market strategy
- `/tech-alignment` - Align tech with business
- `/documentation` - Create technical docs
- `/middleware-setup` - Configure queues/caching
- `/site-architecture` - Design information architecture
- `/prompt-enhance` - Improve unclear requests

### Slash Command Features

#### Variable Support
```bash
# Basic usage
/frontend-mockup "landing page"

# With variables
/project-plan "Mobile App" team:5 budget:100k deadline:"3 months"

# Multiple variables
/technical-feasibility "blockchain app" scale:"1M users" constraints:"AWS only" budget:"limited"
```

#### Default Values
Commands include sensible defaults:
```bash
/technical-feasibility "app"  # Uses default scale of 10,000 users
/financial-model "SaaS"       # Uses default 5-year projection
```

#### Command Aliases
```bash
/roi              # Same as /business-analysis
/specs            # Same as /requirements
/gtm              # Same as /go-to-market
```

### When to Use Slash Commands vs Direct Agents

| Use Slash Commands When | Use Direct Agents When |
|------------------------|------------------------|
| Speed is priority | Need custom parameters |
| Common operations | Complex requirements |
| Known parameters | First-time exploration |
| Repeated tasks | Unique scenarios |

## Common Mistakes to Avoid

### ❌ Using the Wrong Agent
**Problem:** Using backend-services for database design
**Solution:** Use database-architecture for schema design

### ❌ Vague Instructions
**Problem:** "Make it better"
**Solution:** "Optimize API response time from 500ms to under 200ms"

### ❌ Skipping Planning Agents
**Problem:** Jumping straight to development
**Solution:** Use planning agents first for better outcomes

### ❌ Ignoring Dependencies
**Problem:** Using agents out of sequence
**Solution:** Follow recommended workflows

### ❌ Not Providing Context
**Problem:** "Build a login system"
**Solution:** "Build JWT-based login for React SPA with 2FA support"

## Troubleshooting Agent Issues

### Agent Not Responding As Expected
1. Check you're using the correct agent name
2. Verify the task matches agent capabilities
3. Provide more specific instructions
4. Review agent description for activation triggers

### Conflicting Recommendations
1. Use business-tech-alignment agent to resolve
2. Consider business priorities
3. Evaluate technical trade-offs
4. Document decision rationale

### Incomplete Results
1. Break down complex tasks
2. Use multiple agents in sequence
3. Provide more context
4. Specify expected deliverables

## Tips for Power Users

### 1. Create Custom Workflows
Document your successful agent combinations for reuse

### 2. Use CLAUDE.md Files
Store project-specific context for agents to reference

### 3. Chain Agents Effectively
Output from one agent can be input for another

### 4. Leverage Parallel Processing
Run independent agents simultaneously

### 5. Build Prompt Libraries
Save effective prompts for your common tasks

## Getting Started Checklist

- [ ] Install all 28 agents
- [ ] Read agent descriptions
- [ ] Try master-orchestrator for a test project
- [ ] Explore master-prompts templates
- [ ] Create your first multi-agent workflow
- [ ] Document successful patterns

Remember: The agents are tools. Your expertise in using them effectively will improve with practice!