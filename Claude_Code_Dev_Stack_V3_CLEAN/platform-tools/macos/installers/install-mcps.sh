#!/bin/bash
# MCP Configuration Installer for macOS
# Installs settings.json and .mcp.json to ~/.claude

install_mcps() {
    echo "Installing Claude Code MCP Configuration..."
    
    # Create claude directory
    CLAUDE_DIR="$HOME/.claude"
    mkdir -p "$CLAUDE_DIR"
    
    # Base URL for config files
    BASE_URL="https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example"
    
    # Download settings.json if it doesn't exist
    if [ ! -f "$CLAUDE_DIR/settings.json" ]; then
        echo -n "  Downloading settings.json... "
        if curl -sS -f -o "$CLAUDE_DIR/settings.json" "$BASE_URL/settings.json" 2>/dev/null; then
            echo "✓"
        else
            echo "✗"
        fi
    else
        echo "  settings.json already exists, skipping"
    fi
    
    # Download .mcp.json if it doesn't exist
    if [ ! -f "$CLAUDE_DIR/.mcp.json" ]; then
        echo -n "  Downloading .mcp.json... "
        if curl -sS -f -o "$CLAUDE_DIR/.mcp.json" "$BASE_URL/.mcp.json" 2>/dev/null; then
            echo "✓"
        else
            echo "✗"
        fi
    else
        echo "  .mcp.json already exists, skipping"
    fi
    
    echo "MCP configuration installed"
    echo "Location: $CLAUDE_DIR"
    
    # Check if both files exist
    if [ -f "$CLAUDE_DIR/settings.json" ] && [ -f "$CLAUDE_DIR/.mcp.json" ]; then
        return 0
    else
        return 1
    fi
}

# Main execution
install_mcps