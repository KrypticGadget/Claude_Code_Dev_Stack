#!/bin/bash
# Commands Installer for macOS
# Installs 18 slash command files to ~/.claude/commands

install_commands() {
    echo "Installing Claude Code Commands..."
    
    # Create commands directory
    COMMANDS_DIR="$HOME/.claude/commands"
    mkdir -p "$COMMANDS_DIR"
    
    # Base URL for command files
    BASE_URL="https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example/commands"
    
    # List of command files (without .md extension in the names)
    COMMANDS=(
        "api-integration"
        "backend-service"
        "business-analysis"
        "database-design"
        "documentation"
        "financial-model"
        "frontend-mockup"
        "go-to-market"
        "middleware-setup"
        "new-project"
        "production-frontend"
        "project-plan"
        "prompt-enhance"
        "requirements"
        "resume-project"
        "site-architecture"
        "tech-alignment"
        "technical-feasibility"
    )
    
    # Download each command
    SUCCESS_COUNT=0
    for cmd in "${COMMANDS[@]}"; do
        echo -n "  Downloading $cmd... "
        if curl -sS -f -o "$COMMANDS_DIR/$cmd.md" "$BASE_URL/$cmd.md" 2>/dev/null; then
            echo "✓"
            ((SUCCESS_COUNT++))
        else
            echo "✗"
        fi
    done
    
    echo "Commands installed: $SUCCESS_COUNT/${#COMMANDS[@]}"
    echo "Location: $COMMANDS_DIR"
    
    if [ $SUCCESS_COUNT -eq ${#COMMANDS[@]} ]; then
        return 0
    else
        return 1
    fi
}

# Main execution
install_commands