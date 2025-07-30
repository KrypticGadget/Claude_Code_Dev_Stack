# Master Prompts Directory

This directory contains universal, project-agnostic prompt templates for the Claude Code Agent System. These prompts are designed to work with any type of project - simply replace the bracketed variables with your specific values.

## 📋 Available Master Prompts

### 1. PROJECT-INITIALIZATION.md
Complete prompts for starting new projects:
- Full project initialization with business analysis
- Technical feasibility assessment
- Project planning and resource allocation
- Financial projections and ROI analysis
- Strategic positioning and go-to-market
- Requirements gathering and documentation

### 2. DEVELOPMENT-WORKFLOWS.md
Universal development task prompts:
- Frontend development (UI/UX, architecture, components)
- Backend development (APIs, services, databases)
- DevOps & infrastructure (CI/CD, monitoring, scaling)
- Testing implementation (strategy, automation, performance)
- Security implementation (audits, authentication, protection)
- Documentation (technical, API, user guides)

### 3. OPTIMIZATION-TASKS.md
Comprehensive optimization prompts:
- Performance optimization (application, database, frontend)
- Code quality improvements (refactoring, standards, debt)
- Architecture optimization (microservices, scalability)
- Security hardening (vulnerabilities, compliance)
- Testing improvements (coverage, performance, reliability)
- Process and cost optimization

### 4. TROUBLESHOOTING.md
Diagnostic and debugging prompts:
- Performance issue diagnosis
- Bug investigation and root cause analysis
- Integration and API troubleshooting
- Database issue resolution
- Deployment and environment debugging
- Security incident investigation

## 🚀 How to Use These Prompts

### Quick Option: Use Slash Commands
Many common operations have pre-built slash commands that are faster than templates:

```bash
# Install slash commands (one-time)
curl -sL https://raw.githubusercontent.com/yourusername/claude-code-agent-system/main/slash-commands/install-commands.sh | bash

# Then use instantly:
/new-project "Your project description"
/frontend-mockup "landing page"
/database-design "e-commerce schema"
```

### Full Control Option: Use Master Prompts

#### Step 1: Choose Your Prompt Category
Select the appropriate file based on what you need:
- Starting a new project? → PROJECT-INITIALIZATION.md
- Building features? → DEVELOPMENT-WORKFLOWS.md
- Improving existing code? → OPTIMIZATION-TASKS.md
- Fixing problems? → TROUBLESHOOTING.md

#### Step 2: Find the Right Prompt
Each file contains prompts organized by specific use cases. Browse to find the one that matches your needs.

#### Step 3: Copy and Customize
1. Copy the entire prompt including the agent invocation
2. Replace ALL bracketed variables [LIKE_THIS] with your specific values
3. Remove any optional parameters you don't need
4. Ensure all variables are replaced before using

#### Step 4: Execute in Claude Code
Paste the customized prompt into Claude Code to invoke the appropriate agent.

## 📝 Variable Guidelines

### Required vs Optional
- Required variables must be replaced for the prompt to work
- Optional variables can be removed if not needed
- Some prompts have minimal and full versions

### Variable Types
- `[PROJECT_NAME]`: Specific names and identifiers
- `[NUMERIC_VALUE]`: Numbers, percentages, counts
- `[TECHNOLOGY]`: Specific technologies, frameworks, tools
- `[DESCRIPTION]`: Detailed descriptions of issues or requirements
- `[LIST_ITEMS]`: Comma-separated lists of items

### Best Practices
1. Be specific with your variable values
2. Include measurable targets where applicable
3. Provide context for complex requirements
4. Use consistent naming across related prompts

## 🔧 Example Usage

### Using Master Prompt Template:

**Before (Template):**
```
> Use the backend-services agent to create [API_TYPE] API for [DOMAIN] supporting [OPERATIONS] with [AUTH_METHOD] authentication
```

**After (Filled):**
```
> Use the backend-services agent to create REST API for e-commerce platform supporting CRUD operations for products, orders, and users with JWT authentication
```

### Using Slash Command (Equivalent):
```
/backend-service "REST API for e-commerce" requirements:"CRUD operations, JWT auth"
```

## 📊 When to Use What

| Use Slash Commands When | Use Master Prompts When |
|------------------------|------------------------|
| Speed is priority | Need full customization |
| Common operations | Complex requirements |
| Standard parameters | Unique scenarios |
| Quick iterations | Learning the system |
| Known workflows | Exploring possibilities |

## 📚 Complete Variable Reference

Each prompt file includes a complete variable reference at the bottom explaining:
- What each variable represents
- Example values you might use
- Common options for each variable type
- Related variables that work together

## 💡 Tips for Success

1. **Start Simple**: Use minimal versions for quick tasks
2. **Add Detail**: Use full versions for complex projects
3. **Chain Prompts**: Combine multiple prompts for complete workflows
4. **Save Customizations**: Keep your filled prompts for reuse
5. **Iterate**: Refine your prompts based on results

## 🔗 Integration with Agent System

These prompts are designed to work seamlessly with all 28 agents in the Claude Code Agent System:
- Each prompt specifies the correct agent to use
- Variables align with agent capabilities
- Prompts can be chained for complex workflows
- Results from one prompt can inform the next

## 📖 Additional Resources

- See `/agents/` directory for individual agent capabilities
- Check `/prompts/` directory for example-based prompts
- Review `/docs/` for detailed documentation
- Refer to top-level README for installation and setup

Remember: These are templates. The power comes from how you customize them for your specific needs!