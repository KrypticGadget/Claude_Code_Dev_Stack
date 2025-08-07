#!/bin/bash
# Uninstall Claude Code Commands
# Removes commands from ~/.claude/commands

echo "Uninstalling Claude Code Commands..."

COMMANDS_DIR="$HOME/.claude/commands"

if [ -d "$COMMANDS_DIR" ]; then
    echo "Removing commands directory..."
    rm -rf "$COMMANDS_DIR"
    echo "✓ Commands uninstalled"
else
    echo "No commands directory found"
fi

echo "Uninstall complete"