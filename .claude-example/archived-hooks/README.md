# Archived Hooks

These hooks have been archived because they cause performance issues or provide no real value.

## Why These Were Archived

### Performance Issues (caused .claude.json bloat):
- **pre_project.py** - Unnecessary filesystem scanning
- **post_project.py** - Accumulated unbounded data
- **agent_orchestrator.py** - Overly complex state management
- **agent_orchestrator_integrated.py** - Even more complex version
- **mcp_initializer.py** - Redundant MCP initialization

### No Real Value:
- **pre_command.py** - Added overhead with no benefit
- **post_command.py** - Added overhead with no benefit
- **quality_gate.py** - Never actually gated anything
- **mcp_gateway.py** - Redundant MCP handling
- **mcp_gateway_enhanced.py** - Double redundant
- **base_hook.py** - Just a base class, not used directly

## Problems They Caused

1. **.claude.json grew to 150MB+** causing PowerShell to freeze
2. **Filesystem scanning** on every operation
3. **Unbounded data accumulation** with no cleanup
4. **Hook execution overhead** with no tangible benefit
5. **Memory leaks** from storing entire conversation history

## Current Solution

We now use only 8 optimized hooks that provide real value:
- `agent_mention_parser.py` - Routes @agent- mentions
- `slash_command_router.py` - Handles /commands  
- `audio_player.py` - Audio notifications
- `audio_notifier.py` - Alternative audio
- `planning_trigger.py` - Todo management
- `session_loader.py` - Minimal version (just acknowledges)
- `session_saver.py` - Minimal version (just timestamp)
- `model_tracker.py` - Minimal version (daily count only)

## If You Want to Use These

**DON'T!** They will cause performance problems. If you absolutely must:

1. Copy the hook to `.claude/hooks/`
2. Be prepared for slowdowns
3. Run `claude_maintenance.ps1` frequently
4. Monitor `.claude.json` size

## Better Alternatives

Instead of these hooks, use:
- **Audio hooks** for notifications
- **Agent parser** for routing
- **Slash commands** for workflows
- **Planning trigger** for todos

These archived hooks are kept only for reference and should not be used in production.