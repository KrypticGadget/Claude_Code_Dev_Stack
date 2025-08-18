#!/bin/bash
# Claude Code Dev Stack V3.0+ - Uninstall All Components
# Simple script to remove all Claude Code V3+ components

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
    log_warning "This will remove all Claude Code Dev Stack V3.0+ components:"
    echo "  - ~/.claude/agents (28 V3+ agent files)"
    echo "  - ~/.claude/commands (20+ command files)"
    echo "  - ~/.claude/hooks (19 hook files)"
    echo "  - ~/.claude/audio (96 audio files)"
    echo "  - ~/.claude/logs (system logs)"
    echo "  - ~/.claude/state (state management)"
    echo "  - ~/.claude/backups (backup files)"
    echo "  - ~/.claude/mobile (mobile configs)"
    echo "  - ~/.claude/tunnels (tunnel configs)"
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
    
    # Remove audio directory
    if [[ -d "$HOME/.claude/audio" ]]; then
        rm -rf "$HOME/.claude/audio"
        log_info "Removed audio directory (96 files)"
    fi
    
    # Remove logs directory
    if [[ -d "$HOME/.claude/logs" ]]; then
        rm -rf "$HOME/.claude/logs"
        log_info "Removed logs directory"
    fi
    
    # Remove state directory
    if [[ -d "$HOME/.claude/state" ]]; then
        rm -rf "$HOME/.claude/state"
        log_info "Removed state directory"
    fi
    
    # Remove backups directory
    if [[ -d "$HOME/.claude/backups" ]]; then
        rm -rf "$HOME/.claude/backups"
        log_info "Removed backups directory"
    fi
    
    # Remove mobile directory
    if [[ -d "$HOME/.claude/mobile" ]]; then
        rm -rf "$HOME/.claude/mobile"
        log_info "Removed mobile directory"
    fi
    
    # Remove tunnels directory
    if [[ -d "$HOME/.claude/tunnels" ]]; then
        rm -rf "$HOME/.claude/tunnels"
        log_info "Removed tunnels directory"
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
    
    log_info "V3.0+ uninstallation completed successfully"
    log_info "All mobile launchers and tunnel configs removed"
    return 0
}

# Run uninstall
uninstall_all