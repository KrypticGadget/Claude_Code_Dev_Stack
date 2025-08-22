#!/bin/bash
# Uninstall MCP Configuration
# Removes MCP config files from ~/.claude

echo "Uninstalling Claude Code MCP Configuration..."

# Remove settings.json if it exists
if [ -f "$HOME/.claude/settings.json" ]; then
    echo "Removing settings.json..."
    rm -f "$HOME/.claude/settings.json"
fi

# Remove .mcp.json if it exists
if [ -f "$HOME/.claude/.mcp.json" ]; then
    echo "Removing .mcp.json..."
    rm -f "$HOME/.claude/.mcp.json"
fi

echo "✓ MCP configuration uninstalled"
echo "Uninstall complete"