# Quick Start - 60 Seconds to Productivity

## 1. Install (30 seconds)

### Windows
```powershell
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/installers/windows/install-all.ps1 | iex
```

### Linux/macOS
```bash
curl -sL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/installers/linux/install-all.sh | bash
```

## 2. Start Building (30 seconds)

```bash
# Open Claude Code
claude-code .

# Create your first project
/new-project "Todo app with authentication"

# Watch the magic:
# - @agent-system-architect designs the system
# - @agent-database-architect creates the schema
# - @agent-backend-engineer builds the API
# - @agent-frontend-architect creates the UI
# - @agent-security-architect adds authentication
```

## 3. What Just Happened?

You used:
- **Slash command** to start workflow
- **AI agents** automatically engaged
- **MCPs** activated as needed (Playwright for testing)
- **Hooks** saved your session

## Next Steps
- Try: `/backend-service "REST API for users"`
- Read: [Agent Reference](AGENT_REFERENCE.md)
- Explore: [Examples](../examples/)