# Hooks System Guide

## Overview
13 automation hooks work behind the scenes to enhance Claude Code's capabilities. No manual intervention required - they just work.

## Hook Categories

### Session Management
- **session_loader.py** - Restores context on startup
- **session_saver.py** - Saves state between sessions

### Agent Orchestration  
- **agent_mention_parser.py** - Routes @agent mentions
- **agent_orchestrator.py** - Coordinates agent responses

### Quality Control
- **quality_gate.py** - Enforces coding standards
- **pre_command.py** - Validates before execution
- **post_command.py** - Cleanup after execution

### Project Lifecycle
- **pre_project.py** - Project initialization
- **post_project.py** - Project finalization
- **planning_trigger.py** - Activates planning mode

### Integration
- **mcp_gateway.py** - Manages MCP connections
- **model_tracker.py** - Optimizes model usage
- **base_hook.py** - Shared hook utilities

## Configuration

Hooks are configured in `settings.json`:
```json
{
  "hooks": {
    "SessionStart": ["session_loader.py"],
    "SessionEnd": ["session_saver.py"],
    "UserPromptSubmit": ["agent_mention_parser.py"],
    "AgentResponse": ["model_tracker.py"]
  }
}
```

## Benefits

1. **Never lose work** - Session persistence
2. **Right expert** - Smart agent routing
3. **Consistent quality** - Automated standards
4. **Cost savings** - Model optimization (60% cheaper)
5. **Zero config** - Works automatically

## How Hooks Work

### Session Persistence
When you start Claude Code, `session_loader.py` automatically:
- Loads previous conversation context
- Restores project state
- Reconnects to active services
- Resumes where you left off

When you close Claude Code, `session_saver.py`:
- Saves conversation history
- Preserves project progress
- Stores configuration state
- Ensures nothing is lost

### Agent Routing
The `agent_mention_parser.py` hook:
- Detects @agent- mentions
- Routes to appropriate specialists
- Manages agent collaboration
- Optimizes response order

### Quality Gates
Before and after every operation:
- Code style checking
- Security validation
- Performance analysis
- Best practices enforcement

### Model Optimization
The `model_tracker.py` hook automatically:
- Analyzes task complexity
- Selects optimal model (Opus for complex, Haiku for simple)
- Tracks token usage
- Reduces costs by 60%

## Advanced Features

### Custom Hook Development
Developers can create custom hooks following the base_hook.py pattern:
```python
from base_hook import BaseHook

class CustomHook(BaseHook):
    def execute(self, context):
        # Your automation logic here
        pass
```

### Hook Chaining
Hooks can trigger other hooks for complex workflows:
- Pre-command → Validation → Execution → Post-command
- Session start → Load state → Route agents → Begin work

### Error Recovery
Hooks include automatic error handling:
- Graceful degradation
- Fallback mechanisms
- Error logging
- User notification

## Best Practices

1. **Let hooks work** - Don't try to manually control automated processes
2. **Trust the routing** - Agent selection is optimized
3. **Review logs** - Check ~/.claude/logs/ for hook activity
4. **Report issues** - Help improve hook reliability

## Troubleshooting

### Hooks not firing?
1. Check settings.json configuration
2. Verify hook files exist in ~/.claude/hooks/
3. Check logs for errors
4. Restart Claude Code

### Session not persisting?
1. Ensure write permissions on ~/.claude/
2. Check disk space
3. Verify session files aren't corrupted
4. Clear cache if needed

### Cost optimization not working?
1. Model tracker needs usage history
2. Allow 2-3 sessions to build profile
3. Check model availability
4. Review token usage logs