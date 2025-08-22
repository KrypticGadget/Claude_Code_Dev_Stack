#!/bin/bash
# Shell integration script for Claude Code Terminal Statusline
# Supports bash, zsh, and fish shells on Unix-like systems

set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
STATUSLINE_CMD="$PROJECT_ROOT/bin/statusline.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        log_error "Python is not installed or not in PATH"
        exit 1
    fi
    
    # Check statusline script
    if [[ ! -f "$STATUSLINE_CMD" ]]; then
        log_error "Statusline script not found at $STATUSLINE_CMD"
        exit 1
    fi
    
    # Make statusline script executable
    chmod +x "$STATUSLINE_CMD"
    
    log_info "Prerequisites check passed"
}

# Detect current shell
detect_shell() {
    local shell_name
    
    if [[ -n "${ZSH_VERSION:-}" ]]; then
        echo "zsh"
    elif [[ -n "${BASH_VERSION:-}" ]]; then
        echo "bash"
    elif [[ -n "${FISH_VERSION:-}" ]]; then
        echo "fish"
    else
        # Fallback to checking SHELL environment variable
        shell_name="$(basename "${SHELL:-}")"
        case "$shell_name" in
            zsh|bash|fish)
                echo "$shell_name"
                ;;
            *)
                echo "bash"  # Default fallback
                ;;
        esac
    fi
}

# Generate shell-specific integration
generate_bash_integration() {
    cat << 'EOF'
# Claude Code Statusline Integration for Bash

# Function to update statusline
function _claude_statusline_update() {
    if [[ "$TERM" != "dumb" ]] && [[ -t 1 ]]; then
        local statusline_output
        statusline_output=$(STATUSLINE_CMD render 2>/dev/null)
        if [[ $? -eq 0 ]] && [[ -n "$statusline_output" ]]; then
            # Save cursor position, move to top, write statusline, restore cursor
            printf '\033[s\033[1;1H%s\033[K\033[u' "$statusline_output"
        fi
    fi
}

# Update statusline before each prompt
if [[ -z "$PROMPT_COMMAND" ]]; then
    PROMPT_COMMAND="_claude_statusline_update"
else
    PROMPT_COMMAND="$PROMPT_COMMAND; _claude_statusline_update"
fi
EOF
}

generate_zsh_integration() {
    cat << 'EOF'
# Claude Code Statusline Integration for Zsh

# Function to update statusline
function _claude_statusline_update() {
    if [[ "$TERM" != "dumb" ]] && [[ -t 1 ]]; then
        local statusline_output
        statusline_output=$(STATUSLINE_CMD render 2>/dev/null)
        if [[ $? -eq 0 ]] && [[ -n "$statusline_output" ]]; then
            # Save cursor position, move to top, write statusline, restore cursor
            printf '\033[s\033[1;1H%s\033[K\033[u' "$statusline_output"
        fi
    fi
}

# Add to precmd hooks
autoload -Uz add-zsh-hook
add-zsh-hook precmd _claude_statusline_update
EOF
}

generate_fish_integration() {
    cat << 'EOF'
# Claude Code Statusline Integration for Fish

# Function to update statusline
function _claude_statusline_update --on-event fish_prompt
    if test "$TERM" != "dumb"; and isatty stdout
        set statusline_output (STATUSLINE_CMD render 2>/dev/null)
        if test $status -eq 0; and test -n "$statusline_output"
            # Save cursor position, move to top, write statusline, restore cursor
            printf '\033[s\033[1;1H%s\033[K\033[u' "$statusline_output"
        end
    end
end
EOF
}

# Install integration for specific shell
install_shell_integration() {
    local shell="$1"
    local config_file=""
    local integration_code=""
    
    log_info "Installing $shell integration..."
    
    # Determine config file
    case "$shell" in
        bash)
            config_file="$HOME/.bashrc"
            if [[ ! -f "$config_file" ]]; then
                config_file="$HOME/.bash_profile"
            fi
            integration_code="$(generate_bash_integration)"
            ;;
        zsh)
            config_file="$HOME/.zshrc"
            integration_code="$(generate_zsh_integration)"
            ;;
        fish)
            config_file="$HOME/.config/fish/config.fish"
            mkdir -p "$(dirname "$config_file")"
            integration_code="$(generate_fish_integration)"
            ;;
        *)
            log_error "Unsupported shell: $shell"
            return 1
            ;;
    esac
    
    # Check if already installed
    if [[ -f "$config_file" ]] && grep -q "Claude Code Statusline" "$config_file"; then
        log_warn "$shell integration already installed in $config_file"
        return 0
    fi
    
    # Add integration
    {
        echo ""
        echo "# Claude Code Statusline Integration"
        echo "$integration_code" | sed "s|STATUSLINE_CMD|$STATUSLINE_CMD|g"
        echo ""
    } >> "$config_file"
    
    log_info "$shell integration installed in $config_file"
}

# Remove integration from config file
remove_shell_integration() {
    local shell="$1"
    local config_file=""
    
    log_info "Removing $shell integration..."
    
    # Determine config file
    case "$shell" in
        bash)
            config_file="$HOME/.bashrc"
            if [[ ! -f "$config_file" ]]; then
                config_file="$HOME/.bash_profile"
            fi
            ;;
        zsh)
            config_file="$HOME/.zshrc"
            ;;
        fish)
            config_file="$HOME/.config/fish/config.fish"
            ;;
        *)
            log_error "Unsupported shell: $shell"
            return 1
            ;;
    esac
    
    if [[ ! -f "$config_file" ]]; then
        log_warn "Config file not found: $config_file"
        return 0
    fi
    
    # Create temporary file without statusline integration
    local temp_file
    temp_file="$(mktemp)"
    
    # Process file, removing statusline-related sections
    local skip_block=false
    while IFS= read -r line; do
        if [[ "$line" == *"Claude Code Statusline"* ]]; then
            skip_block=true
            continue
        elif [[ "$skip_block" == true ]] && [[ -z "$line" ]]; then
            skip_block=false
            continue
        elif [[ "$skip_block" == false ]]; then
            echo "$line" >> "$temp_file"
        fi
    done < "$config_file"
    
    # Replace original file
    mv "$temp_file" "$config_file"
    
    log_info "$shell integration removed from $config_file"
}

# Test statusline rendering
test_statusline() {
    log_info "Testing statusline rendering..."
    
    if "$STATUSLINE_CMD" render; then
        log_info "Statusline test passed"
    else
        log_error "Statusline test failed"
        return 1
    fi
}

# Show usage information
show_usage() {
    cat << EOF
Claude Code Terminal Statusline - Shell Integration

Usage: $0 [COMMAND] [OPTIONS]

Commands:
    install [SHELL]     Install integration for specified shell (default: auto-detect)
    uninstall [SHELL]   Remove integration for specified shell (default: auto-detect)
    test               Test statusline rendering
    render             Render statusline once
    help               Show this help message

Supported shells: bash, zsh, fish

Examples:
    $0 install          # Install for current shell
    $0 install bash     # Install for bash specifically
    $0 uninstall        # Remove from current shell
    $0 test            # Test the statusline
    $0 render          # Render statusline once

After installation, restart your shell or source your shell configuration file.
EOF
}

# Install for multiple shells
install_multiple_shells() {
    local shells=("$@")
    
    if [[ ${#shells[@]} -eq 0 ]]; then
        shells=("$(detect_shell)")
    fi
    
    for shell in "${shells[@]}"; do
        install_shell_integration "$shell"
    done
    
    log_info "Installation completed for: ${shells[*]}"
    log_info "Please restart your shell or source your configuration file"
}

# Remove from multiple shells
uninstall_multiple_shells() {
    local shells=("$@")
    
    if [[ ${#shells[@]} -eq 0 ]]; then
        shells=("bash" "zsh" "fish")  # Try all supported shells
    fi
    
    for shell in "${shells[@]}"; do
        remove_shell_integration "$shell"
    done
    
    log_info "Removal completed for: ${shells[*]}"
}

# Main function
main() {
    local command="${1:-help}"
    shift || true
    
    case "$command" in
        install)
            check_prerequisites
            install_multiple_shells "$@"
            ;;
        uninstall)
            uninstall_multiple_shells "$@"
            ;;
        test)
            check_prerequisites
            test_statusline
            ;;
        render)
            check_prerequisites
            "$STATUSLINE_CMD" render
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            log_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"