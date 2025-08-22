#!/bin/bash
# Claude Code Dev Stack - Uninstall MCPs
# Simple script to remove MCP config files

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
uninstall_mcps() {
    log_warning "This will remove MCP configuration files:"
    echo "  - ~/.claude/mcps"
    echo "  - ~/.config/mcp/mcp.json"
    echo ""
    
    # Confirmation prompt
    read -p "Are you sure you want to remove MCP configs? (yes/no): " confirmation
    
    if [[ "$confirmation" != "yes" ]]; then
        log_info "Uninstallation cancelled"
        return 0
    fi
    
    log_info "Removing MCP configurations..."
    
    # Remove mcps directory
    if [[ -d "$HOME/.claude/mcps" ]]; then
        rm -rf "$HOME/.claude/mcps"
        log_info "Removed mcps directory"
    else
        log_info "MCPs directory not found"
    fi
    
    # Remove MCP config file
    if [[ -f "$HOME/.config/mcp/mcp.json" ]]; then
        rm -f "$HOME/.config/mcp/mcp.json"
        log_info "Removed MCP config file"
    else
        log_info "MCP config file not found"
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
    
    log_info "MCP uninstallation completed"
    return 0
}

# Run uninstall
uninstall_mcps