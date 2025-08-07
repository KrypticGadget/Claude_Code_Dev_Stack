#!/bin/bash
# Uninstall Claude Code Hooks
# Removes hooks from ~/.claude/hooks

echo "Uninstalling Claude Code Hooks..."

HOOKS_DIR="$HOME/.claude/hooks"

if [ -d "$HOOKS_DIR" ]; then
    echo "Removing hooks directory..."
    rm -rf "$HOOKS_DIR"
    echo "✓ Hooks uninstalled"
else
    echo "No hooks directory found"
fi

echo "Uninstall complete"