#!/bin/bash
# Claude Code Dev Stack - Uninstall Hooks
# Simple script to remove ~/.claude/hooks directory

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
uninstall_hooks() {
    log_warning "This will remove the hooks directory:"
    echo "  - ~/.claude/hooks"
    echo ""
    
    # Confirmation prompt
    read -p "Are you sure you want to remove hooks? (yes/no): " confirmation
    
    if [[ "$confirmation" != "yes" ]]; then
        log_info "Uninstallation cancelled"
        return 0
    fi
    
    log_info "Removing hooks..."
    
    # Remove hooks directory
    if [[ -d "$HOME/.claude/hooks" ]]; then
        rm -rf "$HOME/.claude/hooks"
        log_info "Removed hooks directory"
    else
        log_info "Hooks directory not found"
    fi
    
    # Remove empty parent directory if exists
    if [[ -d "$HOME/.claude" ]] && [[ -z "$(ls -A "$HOME/.claude")" ]]; then
        rmdir "$HOME/.claude"
        log_info "Removed empty .claude directory"
    fi
    
    log_info "Hooks uninstallation completed"
    return 0
}

# Run uninstall
uninstall_hooks