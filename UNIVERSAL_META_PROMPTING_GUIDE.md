# Universal Meta Prompting Guide for Claude Code Development Stack

## Overview
This guide serves as the single source of truth for generating Claude Code prompts in any LLM environment. It contains all 28 AI agents and 18 slash commands that comprise the complete Claude Code Development Stack.

## Quick Start
```bash
# One-line installer for ALL components (Windows)
powershell -ExecutionPolicy Bypass -Command "& {iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/installers/windows/install-all.ps1 | iex}"

# One-line installer for ALL components (Mac/Linux)
curl -fsSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/scripts/install-all.sh | bash
```

## Table of Contents
1. [AI Agents (28 Total)](#ai-agents)
2. [Slash Commands (18 Total)](#slash-commands)
3. [Usage Instructions](#usage-instructions)
4. [Integration Guidelines](#integration-guidelines)

---

## AI Agents

### 1. Master Orchestrator Agent (@master-orchestrator)
**Purpose**: Central coordination hub for all AI agents
**Trigger**: `@master-orchestrator`
**Key Responsibilities**:
- Analyzes user requests and routes to appropriate specialist agents
- Manages multi-agent workflows and task dependencies
- Ensures comprehensive project coverage
- Monitors progress and quality across all agents

### 2. CEO Strategy Agent (@ceo-strategy)
**Purpose**: High-level business strategy and vision alignment
**Trigger**: `@ceo-strategy`
**Key Responsibilities**:
- Business model validation
- Market opportunity assessment
- Strategic roadmap development
- Stakeholder alignment

### 3. Technical CTO Agent (@technical-cto)
**Purpose**: Technical architecture and infrastructure decisions
**Trigger**: `@technical-cto`
**Key Responsibilities**:
- Technology stack selection
- Scalability planning
- Technical risk assessment
- Infrastructure design

### 4. Business Analyst Agent (@business-analyst)
**Purpose**: Requirements gathering and business process analysis
**Trigger**: `@business-analyst`
**Key Responsibilities**:
- User story creation
- Process flow mapping
- Requirements documentation
- Acceptance criteria definition

### 5. Technical Specifications Agent (@technical-specifications)
**Purpose**: Detailed technical documentation and specifications
**Trigger**: `@technical-specifications`
**Key Responsibilities**:
- API specifications
- Data model design
- System architecture diagrams
- Technical requirements documentation

### 6. Frontend Architecture Agent (@frontend-architecture)
**Purpose**: Frontend system design and architecture
**Trigger**: `@frontend-architecture`
**Key Responsibilities**:
- Component architecture design
- State management strategy
- Performance optimization planning
- Frontend technology selection

### 7. Backend Services Agent (@backend-services)
**Purpose**: Backend service development and API design
**Trigger**: `@backend-services`
**Key Responsibilities**:
- RESTful/GraphQL API development
- Microservices architecture
- Business logic implementation
- Service integration

### 8. Database Architecture Agent (@database-architecture)
**Purpose**: Database design and optimization
**Trigger**: `@database-architecture`
**Key Responsibilities**:
- Schema design
- Query optimization
- Data migration strategies
- Database technology selection

### 9. DevOps Engineering Agent (@devops-engineering)
**Purpose**: CI/CD and infrastructure automation
**Trigger**: `@devops-engineering`
**Key Responsibilities**:
- Pipeline configuration
- Container orchestration
- Infrastructure as Code
- Monitoring setup

### 10. Security Architecture Agent (@security-architecture)
**Purpose**: Security implementation and best practices
**Trigger**: `@security-architecture`
**Key Responsibilities**:
- Security audit and assessment
- Authentication/authorization design
- Encryption implementation
- Compliance requirements

### 11. Quality Assurance Agent (@quality-assurance)
**Purpose**: Testing strategy and quality control
**Trigger**: `@quality-assurance`
**Key Responsibilities**:
- Test plan creation
- Test case design
- Quality metrics definition
- Bug tracking processes

### 12. Testing Automation Agent (@testing-automation)
**Purpose**: Automated testing implementation
**Trigger**: `@testing-automation`
**Key Responsibilities**:
- Unit test development
- Integration testing
- E2E test automation
- Performance testing

### 13. Performance Optimization Agent (@performance-optimization)
**Purpose**: System performance enhancement
**Trigger**: `@performance-optimization`
**Key Responsibilities**:
- Performance profiling
- Optimization strategies
- Caching implementation
- Load balancing design

### 14. UI/UX Design Agent (@ui-ux-design)
**Purpose**: User interface and experience design
**Trigger**: `@ui-ux-design`
**Key Responsibilities**:
- Design system creation
- User flow mapping
- Wireframe development
- Accessibility compliance

### 15. Frontend Mockup Agent (@frontend-mockup)
**Purpose**: Rapid UI prototyping and mockups
**Trigger**: `@frontend-mockup`
**Key Responsibilities**:
- HTML/CSS mockups
- Interactive prototypes
- Component demonstrations
- Style guide creation

### 16. Production Frontend Agent (@production-frontend)
**Purpose**: Production-ready frontend implementation
**Trigger**: `@production-frontend`
**Key Responsibilities**:
- React/Vue/Angular development
- State management implementation
- API integration
- Performance optimization

### 17. Mobile Development Agent (@mobile-development)
**Purpose**: Mobile application development
**Trigger**: `@mobile-development`
**Key Responsibilities**:
- Native/React Native development
- Mobile UI/UX optimization
- Platform-specific features
- App store deployment

### 18. API Integration Specialist Agent (@api-integration-specialist)
**Purpose**: Third-party API integration
**Trigger**: `@api-integration-specialist`
**Key Responsibilities**:
- API client development
- Authentication handling
- Rate limiting implementation
- Error handling strategies

### 19. Middleware Specialist Agent (@middleware-specialist)
**Purpose**: Middleware and service layer development
**Trigger**: `@middleware-specialist`
**Key Responsibilities**:
- Message queue implementation
- Service bus design
- Caching strategies
- Request/response handling

### 20. Integration Setup Agent (@integration-setup)
**Purpose**: System integration configuration
**Trigger**: `@integration-setup`
**Key Responsibilities**:
- Webhook configuration
- Event-driven architecture
- Service mesh setup
- API gateway configuration

### 21. Project Manager Agent (@project-manager)
**Purpose**: Project planning and execution
**Trigger**: `@project-manager`
**Key Responsibilities**:
- Sprint planning
- Resource allocation
- Timeline management
- Risk mitigation

### 22. Financial Analyst Agent (@financial-analyst)
**Purpose**: Financial modeling and analysis
**Trigger**: `@financial-analyst`
**Key Responsibilities**:
- Cost estimation
- ROI analysis
- Budget planning
- Financial reporting

### 23. Business Tech Alignment Agent (@business-tech-alignment)
**Purpose**: Business and technology alignment
**Trigger**: `@business-tech-alignment`
**Key Responsibilities**:
- Technology roadmap alignment
- Business value assessment
- Stakeholder communication
- Change management

### 24. Technical Documentation Agent (@technical-documentation)
**Purpose**: Comprehensive documentation creation
**Trigger**: `@technical-documentation`
**Key Responsibilities**:
- API documentation
- Developer guides
- Architecture documentation
- Deployment guides

### 25. Development Prompt Agent (@development-prompt)
**Purpose**: AI prompt engineering and optimization
**Trigger**: `@development-prompt`
**Key Responsibilities**:
- Prompt template creation
- Context optimization
- Response formatting
- Prompt testing

### 26. Prompt Engineer Agent (@prompt-engineer)
**Purpose**: Advanced prompt engineering
**Trigger**: `@prompt-engineer`
**Key Responsibilities**:
- Complex prompt design
- Multi-step workflows
- Prompt chaining
- Performance optimization

### 27. Script Automation Agent (@script-automation)
**Purpose**: Automation script development
**Trigger**: `@script-automation`
**Key Responsibilities**:
- Build automation
- Deployment scripts
- Data processing automation
- System maintenance scripts

### 28. Usage Guide Agent (@usage-guide)
**Purpose**: User guide and help documentation
**Trigger**: `@usage-guide`
**Key Responsibilities**:
- User manual creation
- FAQ documentation
- Video script writing
- Training material development

---

## Slash Commands

### 1. /new-project
**Purpose**: Initialize a new project with complete setup
**Usage**: `/new-project [project-name]`
**Creates**:
- Project structure
- Configuration files
- Initial documentation
- Development environment

### 2. /resume-project
**Purpose**: Resume work on an existing project
**Usage**: `/resume-project [project-path]`
**Actions**:
- Load project context
- Restore session state
- Display project status
- Suggest next steps

### 3. /requirements
**Purpose**: Gather and document project requirements
**Usage**: `/requirements`
**Generates**:
- Functional requirements
- Non-functional requirements
- User stories
- Acceptance criteria

### 4. /technical-feasibility
**Purpose**: Assess technical feasibility of project
**Usage**: `/technical-feasibility`
**Analyzes**:
- Technology constraints
- Resource requirements
- Risk assessment
- Implementation timeline

### 5. /project-plan
**Purpose**: Create comprehensive project plan
**Usage**: `/project-plan`
**Includes**:
- Milestone definition
- Task breakdown
- Resource allocation
- Timeline estimation

### 6. /site-architecture
**Purpose**: Design overall site architecture
**Usage**: `/site-architecture`
**Produces**:
- System architecture diagram
- Component relationships
- Data flow diagrams
- Infrastructure layout

### 7. /database-design
**Purpose**: Design database schema and structure
**Usage**: `/database-design`
**Creates**:
- Entity relationship diagrams
- Table schemas
- Index strategies
- Migration plans

### 8. /api-integration
**Purpose**: Plan and implement API integrations
**Usage**: `/api-integration [service-name]`
**Handles**:
- API endpoint mapping
- Authentication setup
- Data transformation
- Error handling

### 9. /backend-service
**Purpose**: Develop backend services
**Usage**: `/backend-service [service-name]`
**Implements**:
- Service architecture
- Business logic
- Data access layer
- API endpoints

### 10. /frontend-mockup
**Purpose**: Create frontend mockups and prototypes
**Usage**: `/frontend-mockup [page-name]`
**Generates**:
- HTML/CSS mockups
- Interactive elements
- Responsive layouts
- Component examples

### 11. /production-frontend
**Purpose**: Build production-ready frontend
**Usage**: `/production-frontend [component-name]`
**Develops**:
- React/Vue/Angular components
- State management
- API integration
- Performance optimization

### 12. /middleware-setup
**Purpose**: Configure middleware services
**Usage**: `/middleware-setup [middleware-type]`
**Configures**:
- Authentication middleware
- Logging systems
- Caching layers
- Message queues

### 13. /documentation
**Purpose**: Generate project documentation
**Usage**: `/documentation [doc-type]`
**Creates**:
- API documentation
- User guides
- Developer documentation
- Deployment guides

### 14. /financial-model
**Purpose**: Create financial models and projections
**Usage**: `/financial-model`
**Calculates**:
- Cost projections
- Revenue models
- ROI analysis
- Budget planning

### 15. /go-to-market
**Purpose**: Develop go-to-market strategy
**Usage**: `/go-to-market`
**Plans**:
- Market analysis
- Launch strategy
- Marketing channels
- Success metrics

### 16. /business-analysis
**Purpose**: Perform business analysis
**Usage**: `/business-analysis`
**Analyzes**:
- Market opportunity
- Competitive landscape
- Business processes
- Value proposition

### 17. /tech-alignment
**Purpose**: Align technology with business goals
**Usage**: `/tech-alignment`
**Ensures**:
- Technology strategy alignment
- Business objective mapping
- ROI justification
- Risk mitigation

### 18. /prompt-enhance
**Purpose**: Enhance and optimize AI prompts
**Usage**: `/prompt-enhance [prompt]`
**Improves**:
- Prompt clarity
- Context optimization
- Response quality
- Token efficiency

---

## Usage Instructions

### Agent Invocation
1. **Direct Mention**: Type `@` followed by the agent name
   - Example: `@backend-services create a user authentication API`
   
2. **Multiple Agents**: Mention multiple agents in one request
   - Example: `@frontend-architecture @backend-services design a real-time chat application`

3. **Master Orchestration**: Let the master orchestrator coordinate
   - Example: `@master-orchestrator build a complete e-commerce platform`

### Command Execution
1. **Basic Usage**: Type `/` followed by the command
   - Example: `/new-project my-awesome-app`

2. **Command Chaining**: Execute multiple commands in sequence
   - Example: `/new-project myapp` then `/requirements` then `/technical-feasibility`

3. **Context Awareness**: Commands understand project context
   - Example: `/resume-project` automatically loads previous session

---

## Integration Guidelines

### For LLM Developers
1. **Agent Loading**: Load agent prompts as system messages
2. **Context Management**: Maintain conversation context between agents
3. **Response Formatting**: Preserve code blocks and formatting
4. **Error Handling**: Gracefully handle missing agents or commands

### For Platform Integration
1. **File Structure**: Place agents in `.claude/agents/` directory
2. **Command Registration**: Register commands in `.claude/commands/` directory
3. **Configuration**: Update `settings.json` with agent paths
4. **Hook System**: Implement pre/post execution hooks

### Best Practices
1. **Start with Master Orchestrator** for complex projects
2. **Use specific agents** for targeted tasks
3. **Combine agents** for comprehensive solutions
4. **Document decisions** using appropriate agents
5. **Test incrementally** with QA and testing agents

---

## Quick Reference Card

### Most Used Agents
- `@master-orchestrator` - Project coordination
- `@backend-services` - API development
- `@frontend-architecture` - UI architecture
- `@database-architecture` - Data design
- `@devops-engineering` - Deployment setup

### Essential Commands
- `/new-project` - Start new project
- `/requirements` - Gather requirements
- `/project-plan` - Create timeline
- `/documentation` - Generate docs
- `/resume-project` - Continue work

### Workflow Example
```
1. /new-project ecommerce-platform
2. @business-analyst gather requirements for online store
3. @technical-specifications create detailed specs
4. @database-architecture design product catalog schema
5. @backend-services implement product API
6. @frontend-architecture design component structure
7. @production-frontend build product listing page
8. @testing-automation create test suite
9. @devops-engineering setup CI/CD pipeline
10. /documentation generate API docs
```

---

## Support and Updates
- **Repository**: https://github.com/KrypticGadget/Claude_Code_Dev_Stack
- **Issues**: Report bugs or request features on GitHub
- **Updates**: Pull latest changes for new agents and commands
- **Community**: Join discussions in GitHub Discussions

---

*This guide is maintained as part of the Claude Code Development Stack project. Version 2.1*