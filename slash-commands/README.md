# Claude Code Slash Commands

Pre-built slash commands for the Claude Code Agent System that enable rapid development workflows.

## 🚀 One-Line Installation

```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/slash-commands/install-commands.sh | bash
```

## 📦 Included Commands

### Project Management
- `/new-project` - Start a new project with comprehensive analysis
- `/resume-project` - Resume existing project by analyzing current state
- `/project-plan` - Create project timeline and resource plan
- `/go-to-market` - Develop go-to-market strategy

### Business Strategy
- `/business-analysis` - Analyze business viability and ROI
- `/financial-model` - Create financial projections
- `/tech-alignment` - Align technical decisions with business goals

### Technical Planning
- `/technical-feasibility` - Assess technical feasibility
- `/requirements` - Document technical requirements
- `/site-architecture` - Design information architecture

### Development
- `/frontend-mockup` - Create HTML/CSS mockup
- `/production-frontend` - Build production React/Vue app
- `/backend-service` - Design backend services and APIs
- `/database-design` - Design database schema
- `/api-integration` - Integrate external APIs
- `/middleware-setup` - Configure message queues and caching

### Documentation & Utilities
- `/documentation` - Create technical documentation
- `/prompt-enhance` - Enhance development prompts

## 💡 Usage Examples

### Basic Usage
```bash
/new-project "E-commerce platform with inventory management"
```

### With Variables
```bash
/project-plan "Mobile App" team:3 budget:50k deadline:"2 months"
```

### Interactive Prompts
```bash
/frontend-mockup "landing page for SaaS product"
/database-design "multi-tenant user system"
```

## 🔧 Command Structure

Each command supports:
- **Aliases**: Alternative names (e.g., `/roi` for `/business-analysis`)
- **Variables**: Dynamic inputs with defaults
- **Categories**: Organized by function
- **Tags**: For discovery and grouping

## 📝 Variable Syntax

Commands use double curly braces for variables:
- `{{variable}}` - Required variable
- `{{variable:default}}` - Variable with default value
- `{{variable:default value with spaces}}` - Multi-word defaults

Example:
```
/financial-model "SaaS" pricing:"$99/month" market:"B2B SMEs"
```

## 🎯 Common Workflows

### Start a New Project
```bash
# 1. Begin with comprehensive planning
/new-project "Your project description"

# 2. Or start with business analysis
/business-analysis

# 3. Then assess technical feasibility
/technical-feasibility "your concept" scale:"expected users"
```

### Quick Prototyping
```bash
# 1. Create a mockup
/frontend-mockup "dashboard for analytics app"

# 2. Design the database
/database-design "analytics data model"

# 3. Plan the backend
/backend-service "REST API for analytics"
```

### Documentation
```bash
/documentation "my project" type:"API reference"
```

## 📂 Installation Location

Commands are installed to:
```
~/.claude/commands/
```

## 🔄 Updating Commands

Re-run the installation command to get the latest versions:
```bash
curl -sL https://raw.githubusercontent.com/yourusername/claude-code-agent-system/main/slash-commands/install-commands.sh | bash
```

Your existing commands will be backed up automatically.

## ✏️ Creating Custom Commands

### Command Format
```markdown
---
description: Brief description of what the command does
aliases: ["alt1", "alt2"]
category: category-name
tags: ["tag1", "tag2"]
---

Your prompt template with {{variables}}
```

### Adding to Claude Code
1. Create a `.md` file in `~/.claude/commands/`
2. Add YAML frontmatter
3. Write your prompt template
4. Use the command with `/filename`

## 🤝 Contributing

To contribute new commands:
1. Fork the repository
2. Add commands to `slash-commands/commands/`
3. Follow the existing format
4. Submit a pull request

## 📚 Related Documentation

- [Agent System Documentation](../docs/)
- [Master Prompts](../master-prompts/)
- [Quick Start Guide](../QUICK_START.md)
- [Examples](../examples/)

## 🆘 Troubleshooting

### Commands Not Found
```bash
# Check installation
ls ~/.claude/commands/

# Reinstall if needed
./install-commands.sh
```

### Variable Not Working
Ensure you're using the correct syntax:
- Correct: `/command "value" var:value`
- Incorrect: `/command value var=value`

### Getting Help
Each command shows its template when called without arguments.