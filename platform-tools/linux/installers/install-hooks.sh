#!/bin/bash
# Hooks Installer for Linux/WSL
# Installs 13 Python hook files to ~/.claude/hooks

install_hooks() {
    echo "Installing Claude Code Hooks..."
    
    # Check for Python (but don't fail if missing)
    if command -v python3 &> /dev/null; then
        echo "  Python3 found: $(python3 --version)"
    else
        echo "  Warning: Python3 not found. Hooks may not function properly."
    fi
    
    # Create hooks directory
    HOOKS_DIR="$HOME/.claude/hooks"
    mkdir -p "$HOOKS_DIR"
    
    # Base URL for hook files
    BASE_URL="https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example/hooks"
    
    # List of hook files
    HOOKS=(
        "agent_mention_parser.py"
        "agent_orchestrator.py"
        "base_hook.py"
        "mcp_gateway.py"
        "model_tracker.py"
        "planning_trigger.py"
        "post_command.py"
        "post_project.py"
        "pre_command.py"
        "pre_project.py"
        "quality_gate.py"
        "session_loader.py"
        "session_saver.py"
    )
    
    # Download each hook
    SUCCESS_COUNT=0
    for hook in "${HOOKS[@]}"; do
        echo -n "  Downloading $hook... "
        if curl -sS -f -o "$HOOKS_DIR/$hook" "$BASE_URL/$hook" 2>/dev/null; then
            chmod +x "$HOOKS_DIR/$hook"
            echo "✓"
            ((SUCCESS_COUNT++))
        else
            echo "✗"
        fi
    done
    
    echo "Hooks installed: $SUCCESS_COUNT/${#HOOKS[@]}"
    echo "Location: $HOOKS_DIR"
    
    if [ $SUCCESS_COUNT -eq ${#HOOKS[@]} ]; then
        return 0
    else
        return 1
    fi
}

# Main execution
install_hooks