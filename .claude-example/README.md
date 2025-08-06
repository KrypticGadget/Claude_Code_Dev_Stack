# .claude-example Directory

This is the source of truth for all Claude Code Dev Stack components.

## 📁 Contents

```
.claude-example/
├── agents/       # 28 AI agent definitions (.md files)
├── commands/     # 18 slash command definitions (.md files)
├── hooks/        # 13 Python automation hooks
├── settings.json # Default settings template
└── .mcp.json     # MCP configuration
```

## 🎯 Purpose

This directory contains all the ready-to-use components that installers copy to your local `.claude` directories. It's organized to match Claude Code's expected structure.

## 📦 Components

### Agents (28 total)
Expert AI agents for every development task:
- Architecture & Design
- Frontend & Backend Development
- Database & Infrastructure
- Testing & Security
- Business & Strategy
- And more...

### Commands (18 total)
Instant workflows for common tasks:
- `/new-project` - Start any project
- `/backend-service` - Create APIs
- `/frontend-mockup` - Design UIs
- `/database-design` - Model data
- And more...

### Hooks (13 total)
Automation that runs behind the scenes:
- Session persistence
- Agent routing
- Cost optimization
- Quality gates
- And more...

## 🚀 Usage

These files are automatically installed by the installers. You don't need to manually copy them.

To install everything:
```bash
# Windows
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/installers/windows/install-all.ps1 | iex

# Linux/macOS
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/installers/[platform]/install-all.sh | bash
```

## 🔧 Customization

To customize these components:
1. Fork the repository
2. Modify the files in this directory
3. Update installer URLs to point to your fork
4. Run your custom installers

## 📝 File Format

- **Agents & Commands**: Markdown files with YAML frontmatter
- **Hooks**: Python scripts following the base_hook.py pattern
- **Settings**: JSON configuration files

See the [documentation](../docs/) for detailed specifications.