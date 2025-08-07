#!/bin/bash
# Claude Code Dev Stack - Uninstall All Components
# Simple script to remove all Claude Code components

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Simple logging
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Main uninstall function
uninstall_all() {
    log_warning "This will remove all Claude Code Dev Stack components:"
    echo "  - ~/.claude/agents"
    echo "  - ~/.claude/commands"
    echo "  - ~/.claude/hooks"
    echo "  - ~/.claude/mcps"
    echo "  - MCP configuration files"
    echo ""
    
    # Confirmation prompt
    read -p "Are you sure you want to uninstall everything? (yes/no): " confirmation
    
    if [[ "$confirmation" != "yes" ]]; then
        log_info "Uninstallation cancelled"
        return 0
    fi
    
    log_info "Starting uninstallation..."
    
    # Remove agents directory
    if [[ -d "$HOME/.claude/agents" ]]; then
        rm -rf "$HOME/.claude/agents"
        log_info "Removed agents directory"
    fi
    
    # Remove commands directory
    if [[ -d "$HOME/.claude/commands" ]]; then
        rm -rf "$HOME/.claude/commands"
        log_info "Removed commands directory"
    fi
    
    # Remove hooks directory
    if [[ -d "$HOME/.claude/hooks" ]]; then
        rm -rf "$HOME/.claude/hooks"
        log_info "Removed hooks directory"
    fi
    
    # Remove mcps directory
    if [[ -d "$HOME/.claude/mcps" ]]; then
        rm -rf "$HOME/.claude/mcps"
        log_info "Removed mcps directory"
    fi
    
    # Remove MCP config files
    if [[ -f "$HOME/.config/mcp/mcp.json" ]]; then
        rm -f "$HOME/.config/mcp/mcp.json"
        log_info "Removed MCP configuration"
    fi
    
    # Remove empty directories
    if [[ -d "$HOME/.claude" ]] && [[ -z "$(ls -A "$HOME/.claude")" ]]; then
        rmdir "$HOME/.claude"
        log_info "Removed empty .claude directory"
    fi
    
    if [[ -d "$HOME/.config/mcp" ]] && [[ -z "$(ls -A "$HOME/.config/mcp")" ]]; then
        rmdir "$HOME/.config/mcp"
        log_info "Removed empty MCP config directory"
    fi
    
    log_info "Uninstallation completed successfully"
    return 0
}

# Run uninstall
uninstall_all