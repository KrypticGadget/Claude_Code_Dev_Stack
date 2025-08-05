#!/bin/bash
# Claude Code Dev Stack - Master Installer (macOS)
# Installs all 4 components: agents, commands, MCPs, and hooks
# Features: progress tracking, error handling, health checks, rollback, retry logic

set -euo pipefail

# Script configuration
SCRIPT_VERSION="2.1.0"
GITHUB_BASE="https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main"
INSTALL_DIR="$HOME/.claude-code"
LOG_DIR="$INSTALL_DIR/.claude/logs"
BACKUP_DIR="$INSTALL_DIR/.claude/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/install_$TIMESTAMP.log"

# Color codes (macOS compatible)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# Component definitions
declare -A COMPONENTS
COMPONENTS[agents]="install-agents.sh|28 AI agents with @agent- routing|$INSTALL_DIR/agents/master-orchestrator-agent.md"
COMPONENTS[commands]="install-commands.sh|18 slash commands|$INSTALL_DIR/commands/new-project.md"
COMPONENTS[mcps]="install-mcps.sh|Tier 1 MCP configurations|$INSTALL_DIR/mcp-configs/tier1-universal.json"
COMPONENTS[hooks]="install-hooks.sh|Hooks execution system|$INSTALL_DIR/.claude/hooks/session_loader.py"

# Component order
COMPONENT_ORDER=("agents" "commands" "mcps" "hooks")

# macOS specific checks
check_macos_requirements() {
    # Check for Homebrew
    if ! command -v brew &> /dev/null; then
        echo -e "${YELLOW}Warning: Homebrew not found. Some features may require it.${NC}"
        echo -e "${GRAY}Install from: https://brew.sh${NC}"
    fi
    
    # Check for Python 3
    if ! command -v python3 &> /dev/null; then
        echo -e "${YELLOW}Warning: Python 3 not found. Required for hooks.${NC}"
        echo -e "${GRAY}Install with: brew install python3${NC}"
    fi
    
    # Check terminal color support
    if [[ ! "${TERM:-}" =~ "256color" ]]; then
        echo -e "${GRAY}Tip: For better colors, add to ~/.zshrc: export TERM=xterm-256color${NC}"
    fi
}

# Initialize directories
initialize_dirs() {
    mkdir -p "$LOG_DIR" "$BACKUP_DIR"
}

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    local log_entry="[$timestamp] [$level] $message"
    
    case $level in
        ERROR)   echo -e "${RED}$log_entry${NC}" ;;
        WARNING) echo -e "${YELLOW}$log_entry${NC}" ;;
        SUCCESS) echo -e "${GREEN}$log_entry${NC}" ;;
        INFO)    echo -e "${CYAN}$log_entry${NC}" ;;
        *)       echo "$log_entry" ;;
    esac
    
    echo "$log_entry" >> "$LOG_FILE" 2>/dev/null || true
}

# Check for updates
check_updates() {
    log INFO "Checking for updates..."
    
    if command -v curl &> /dev/null; then
        local latest_version=$(curl -sL "$GITHUB_BASE/VERSION" 2>/dev/null || echo "$SCRIPT_VERSION")
        
        if [[ "$latest_version" != "$SCRIPT_VERSION" ]]; then
            log WARNING "New version available: $latest_version (current: $SCRIPT_VERSION)"
            log INFO "Visit: https://github.com/KrypticGadget/Claude_Code_Dev_Stack"
        else
            log SUCCESS "You have the latest version"
        fi
    else
        log WARNING "curl not found, skipping update check"
    fi
}

# Create backup
create_backup() {
    if [[ -d "$INSTALL_DIR" ]]; then
        log INFO "Creating backup of existing installation..."
        
        local backup_path="$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"
        
        # macOS tar syntax
        if tar -czf "$backup_path" -C "$HOME" ".claude-code" 2>/dev/null; then
            log SUCCESS "Backup created: $backup_path"
            echo "$backup_path"
        else
            log WARNING "Failed to create backup"
            echo ""
        fi
    else
        echo ""
    fi
}

# Restore from backup
restore_backup() {
    local backup_path=$1
    
    if [[ -f "$backup_path" ]]; then
        log INFO "Restoring from backup: $backup_path"
        
        # Remove current installation
        rm -rf "$INSTALL_DIR"
        
        # Extract backup
        if tar -xzf "$backup_path" -C "$HOME" 2>/dev/null; then
            log SUCCESS "Restore completed successfully"
            return 0
        else
            log ERROR "Failed to restore backup"
            return 1
        fi
    fi
    return 1
}

# Download with retry (macOS optimized)
download_with_retry() {
    local url=$1
    local description=$2
    local max_retries=${3:-3}
    local output_file=${4:-}
    
    for ((i=1; i<=max_retries; i++)); do
        log INFO "Downloading $description (attempt $i/$max_retries)..."
        
        if [[ -n "$output_file" ]]; then
            # Use -L flag for redirects, common on GitHub
            if curl -sL "$url" -o "$output_file" --connect-timeout 30 --max-time 60; then
                return 0
            fi
        else
            local content=$(curl -sL "$url" --connect-timeout 30 --max-time 60 2>/dev/null)
            if [[ -n "$content" ]]; then
                echo "$content"
                return 0
            fi
        fi
        
        if [[ $i -lt $max_retries ]]; then
            log WARNING "Download failed, retrying in 2 seconds..."
            sleep 2
        fi
    done
    
    log ERROR "Failed to download $description after $max_retries attempts"
    return 1
}

# Health check function
health_check() {
    local check_file=$1
    [[ -f "$check_file" ]]
}

# Install component
install_component() {
    local component=$1
    local index=$2
    local total=$3
    
    local IFS='|'
    read -r installer description health_file <<< "${COMPONENTS[$component]}"
    
    local progress="$index/$total"
    
    echo
    log INFO "[$progress] Installing $component - $description"
    
    # Show progress bar
    local percent=$((index * 100 / total))
    printf "\rProgress: ["
    
    # macOS compatible progress bar
    for ((j=0; j<$((percent/2)); j++)); do printf "="; done
    for ((j=$((percent/2)); j<50; j++)); do printf " "; done
    
    printf "] %d%%" "$percent"
    echo
    
    # Check if already installed
    if health_check "$health_file"; then
        read -p "Component '$component' appears to be already installed. Skip? (Y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            log INFO "Skipping $component (already installed)"
            return 0
        fi
    fi
    
    # Download and execute installer
    local temp_installer="/tmp/claude_${component}_installer.sh"
    
    if download_with_retry "$GITHUB_BASE/$installer" "$component installer" 3 "$temp_installer"; then
        chmod +x "$temp_installer"
        
        log INFO "Executing $component installer..."
        
        # Execute installer and capture output
        if /bin/bash "$temp_installer" 2>&1 | tee -a "$LOG_FILE"; then
            # Verify installation with health check
            sleep 2
            if health_check "$health_file"; then
                log SUCCESS "$component installed successfully"
                rm -f "$temp_installer"
                return 0
            else
                log ERROR "$component health check failed"
                rm -f "$temp_installer"
                return 1
            fi
        else
            log ERROR "Failed to execute $component installer"
            rm -f "$temp_installer"
            return 1
        fi
    else
        log ERROR "Failed to download $component installer"
        return 1
    fi
}

# Clean up old backups
cleanup_backups() {
    if [[ -d "$BACKUP_DIR" ]]; then
        # macOS find syntax
        local backup_count=$(find "$BACKUP_DIR" -name "backup_*.tar.gz" -type f | wc -l | tr -d ' ')
        
        if [[ $backup_count -gt 5 ]]; then
            log INFO "Cleaning up old backups..."
            # macOS compatible find and sort
            find "$BACKUP_DIR" -name "backup_*.tar.gz" -type f -exec stat -f "%m %N" {} \; | \
                sort -n | head -n $((backup_count - 5)) | cut -d' ' -f2- | \
                xargs rm -f
            log SUCCESS "Old backups cleaned up"
        fi
    fi
}

# Main installation
main() {
    # Initialize
    initialize_dirs
    
    # Redirect output to log file while still showing on screen
    exec > >(tee -a "$LOG_FILE")
    exec 2>&1
    
    echo
    echo -e "${CYAN}🚀 Claude Code Dev Stack - Master Installer v$SCRIPT_VERSION (macOS)${NC}"
    echo -e "${GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    log INFO "Installation started at $(date)"
    log INFO "Install directory: $INSTALL_DIR"
    log INFO "Platform: macOS $(sw_vers -productVersion)"
    
    # macOS specific checks
    check_macos_requirements
    
    # Check for updates
    check_updates
    
    # Create backup
    local backup_path=$(create_backup)
    
    # Install components
    echo
    log INFO "Installing ${#COMPONENT_ORDER[@]} components..."
    
    local results=()
    local success_count=0
    local failed_count=0
    
    for i in "${!COMPONENT_ORDER[@]}"; do
        local component="${COMPONENT_ORDER[$i]}"
        local index=$((i + 1))
        
        if install_component "$component" "$index" "${#COMPONENT_ORDER[@]}"; then
            results+=("$component:success")
            ((success_count++))
        else
            results+=("$component:failed")
            ((failed_count++))
        fi
    done
    
    # Summary
    echo
    echo -e "${GRAY}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    log INFO "Installation Summary:"
    
    for result in "${results[@]}"; do
        local component="${result%%:*}"
        local status="${result##*:}"
        
        case $status in
            success) echo -e "  ${GREEN}✅ $component: Success${NC}" ;;
            failed)  echo -e "  ${RED}❌ $component: Failed${NC}" ;;
        esac
    done
    
    echo
    log INFO "Total: $success_count successful, $failed_count failed"
    
    # Handle failures
    if [[ $failed_count -gt 0 ]]; then
        log WARNING "Some components failed to install"
        
        if [[ -n "$backup_path" ]]; then
            read -p "Would you like to rollback to the previous installation? (y/N) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                if restore_backup "$backup_path"; then
                    log SUCCESS "Rollback completed successfully"
                else
                    log ERROR "Rollback failed"
                fi
            fi
        fi
    else
        log SUCCESS "All components installed successfully!"
        
        # Post-installation steps
        echo
        echo -e "${YELLOW}🎯 Next Steps:${NC}"
        echo -e "${NC}1. Install MCPs manually:${NC}"
        echo -e "${GRAY}   claude mcp add playwright npx @playwright/mcp@latest${NC}"
        echo -e "${GRAY}   claude mcp add obsidian${NC}"
        echo -e "${GRAY}   claude mcp add brave-search${NC}"
        echo -e "${NC}2. Restart Claude Code to activate all features${NC}"
        echo -e "${NC}3. Try: @agent-master-orchestrator[opus] plan a new project${NC}"
        echo
        
        # macOS specific tips
        echo -e "${CYAN}🍎 macOS Tips:${NC}"
        echo -e "${GRAY}- Add to ~/.zshrc: alias cchelp='cat ~/.claude-code/QUICK_REFERENCE_V2.1.txt'${NC}"
        echo -e "${GRAY}- For Python 3: brew install python3${NC}"
        echo -e "${GRAY}- For better colors: export TERM=xterm-256color${NC}"
        echo -e "${GRAY}- Claude settings: ~/Library/Application Support/Claude/${NC}"
        echo
        
        # Create quick access alias for zsh (default macOS shell)
        if [[ -f "$HOME/.zshrc" ]]; then
            if ! grep -q "alias cchelp" "$HOME/.zshrc"; then
                echo "alias cchelp='cat $INSTALL_DIR/QUICK_REFERENCE_V2.1.txt'" >> "$HOME/.zshrc"
                echo "alias ccds='cd $INSTALL_DIR'" >> "$HOME/.zshrc"
                log SUCCESS "Added aliases to .zshrc (reload with: source ~/.zshrc)"
            fi
        fi
    fi
    
    # Cleanup
    cleanup_backups
    
    echo
    log INFO "Installation log saved to: $LOG_FILE"
    echo -e "${GREEN}🎉 Installation complete!${NC}"
    
    # Check if Claude Code is installed
    if command -v claude &> /dev/null; then
        echo -e "${GREEN}✅ Claude Code CLI detected${NC}"
    else
        echo -e "${YELLOW}⚠️  Claude Code CLI not found. Install from: https://claude.ai/download${NC}"
    fi
}

# Error handler
error_handler() {
    local line_no=$1
    local exit_code=$2
    
    # Skip benign errors
    if [[ $exit_code -eq 141 ]]; then
        # SIGPIPE - common when piping to head/tail
        return
    fi
    
    log ERROR "Installation failed at line $line_no (exit code: $exit_code)"
    
    # Attempt rollback if backup exists
    if [[ -n "${backup_path:-}" ]] && [[ -f "$backup_path" ]]; then
        log WARNING "Attempting automatic rollback..."
        restore_backup "$backup_path"
    fi
    
    exit $exit_code
}

# Set error trap
trap 'error_handler $LINENO $?' ERR

# Run main installation
main "$@"