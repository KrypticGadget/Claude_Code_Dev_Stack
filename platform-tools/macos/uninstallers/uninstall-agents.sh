#!/bin/bash
# Uninstall Claude Code Agents
# Removes agents from ~/.claude/agents

echo "Uninstalling Claude Code Agents..."

AGENTS_DIR="$HOME/.claude/agents"

if [ -d "$AGENTS_DIR" ]; then
    echo "Removing agents directory..."
    rm -rf "$AGENTS_DIR"
    echo "✓ Agents uninstalled"
else
    echo "No agents directory found"
fi

echo "Uninstall complete"