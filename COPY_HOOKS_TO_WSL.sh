#!/bin/bash
# Script to copy hooks from Windows .claude to WSL .claude

echo "📁 Copying hooks from Windows to WSL..."

# Create hooks directory in WSL
mkdir -p /home/krypticgadget/.claude/hooks
mkdir -p /home/krypticgadget/.claude/audio
mkdir -p /home/krypticgadget/.claude/logs
mkdir -p /home/krypticgadget/.claude/state

# Copy all hook files from Windows location to WSL
echo "📝 Copying hook files..."

# Source directory (Windows path accessed from WSL)
SOURCE_HOOKS="/mnt/c/Users/Zach/.claude/hooks"
DEST_HOOKS="/home/krypticgadget/.claude/hooks"

# List of all hooks
HOOKS=(
    "agent_mention_parser.py"
    "agent_orchestrator.py"
    "agent_orchestrator_integrated.py"
    "slash_command_router.py"
    "mcp_gateway.py"
    "mcp_gateway_enhanced.py"
    "mcp_initializer.py"
    "audio_player.py"
    "audio_notifier.py"
    "session_loader.py"
    "session_saver.py"
    "quality_gate.py"
    "model_tracker.py"
    "planning_trigger.py"
    "pre_command.py"
    "post_command.py"
    "pre_project.py"
    "post_project.py"
    "base_hook.py"
    "test_hook.py"
)

# Copy each hook
for hook in "${HOOKS[@]}"; do
    if [ -f "$SOURCE_HOOKS/$hook" ]; then
        cp "$SOURCE_HOOKS/$hook" "$DEST_HOOKS/$hook"
        chmod +x "$DEST_HOOKS/$hook"
        echo "  ✓ Copied: $hook"
    else
        echo "  ⚠ Not found: $SOURCE_HOOKS/$hook"
    fi
done

# Copy audio files
echo "🎵 Copying audio files..."
SOURCE_AUDIO="/mnt/c/Users/Zach/.claude/audio"
DEST_AUDIO="/home/krypticgadget/.claude/audio"

if [ -d "$SOURCE_AUDIO" ]; then
    cp -r "$SOURCE_AUDIO"/* "$DEST_AUDIO/" 2>/dev/null || echo "  ⚠ No audio files to copy"
fi

echo ""
echo "✅ Hooks copied to WSL location!"
echo ""
echo "📍 Hooks are now at: /home/krypticgadget/.claude/hooks/"
echo "⚙️ Settings already updated at: /home/krypticgadget/.claude/settings.json"
echo ""
echo "🚀 Next steps:"
echo "  1. Exit Claude Code completely"
echo "  2. Restart Claude Code: claude --debug"
echo "  3. Test with: ls"
echo "  4. Check: /hooks"
echo ""
echo "Your hooks should now be working!"