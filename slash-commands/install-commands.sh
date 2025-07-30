#!/bin/bash
# Claude Code Slash Commands - One Line Installer
# Install custom slash commands for Claude Code Agent System

set -e

# Configuration
CLAUDE_COMMANDS_DIR="$HOME/.claude/commands"
REPO_URL="https://github.com/yourusername/claude-code-agent-system"
TEMP_DIR="/tmp/claude-commands-install-$$"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Functions
print_status() { echo -e "${BLUE}[*]${NC} $1"; }
print_success() { echo -e "${GREEN}[✓]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
print_error() { echo -e "${RED}[✗]${NC} $1"; }

# Check if Claude Code is installed
check_claude() {
    if ! command -v claude &> /dev/null; then
        print_error "Claude Code CLI not found!"
        echo "Please install Claude Code first: https://docs.anthropic.com/en/docs/claude-code"
        exit 1
    fi
    print_success "Claude Code CLI detected"
}

# Create commands directory
setup_directory() {
    print_status "Setting up commands directory..."
    
    # Backup existing commands if present
    if [ -d "$CLAUDE_COMMANDS_DIR" ] && [ "$(ls -A $CLAUDE_COMMANDS_DIR 2>/dev/null)" ]; then
        BACKUP_DIR="$HOME/.claude/backups/commands-$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        cp -r "$CLAUDE_COMMANDS_DIR"/* "$BACKUP_DIR/" 2>/dev/null || true
        print_warning "Existing commands backed up to $BACKUP_DIR"
    fi
    
    mkdir -p "$CLAUDE_COMMANDS_DIR"
    print_success "Commands directory ready at $CLAUDE_COMMANDS_DIR"
}

# Download commands
download_commands() {
    print_status "Downloading slash commands..."
    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR"
    
    # Try git first
    if command -v git &> /dev/null; then
        if ! git clone --depth 1 --sparse "$REPO_URL.git" . &> /dev/null; then
            print_warning "Git clone failed, trying direct download..."
            USE_CURL=true
        else
            git sparse-checkout init --cone &> /dev/null
            git sparse-checkout set slash-commands/commands &> /dev/null
            USE_CURL=false
        fi
    else
        USE_CURL=true
    fi
    
    # Fallback to curl
    if [ "$USE_CURL" = true ]; then
        if command -v curl &> /dev/null; then
            mkdir -p slash-commands/commands
            COMMANDS_URL="${REPO_URL%.git}/tree/main/slash-commands/commands"
            
            # Download individual command files
            for cmd in new-project business-analysis technical-feasibility frontend-mockup \
                      database-design api-integration project-plan financial-model \
                      backend-service documentation production-frontend middleware-setup \
                      site-architecture go-to-market tech-alignment requirements prompt-enhance; do
                curl -sL "$REPO_URL/raw/main/slash-commands/commands/$cmd.md" \
                     -o "slash-commands/commands/$cmd.md" 2>/dev/null || true
            done
        else
            print_error "Neither git nor curl found. Cannot download commands."
            exit 1
        fi
    fi
    
    print_success "Commands downloaded"
}

# Install commands
install_commands() {
    print_status "Installing slash commands..."
    
    if [ -d "$TEMP_DIR/slash-commands/commands" ]; then
        INSTALLED=0
        for cmd_file in "$TEMP_DIR/slash-commands/commands"/*.md; do
            if [ -f "$cmd_file" ]; then
                cp "$cmd_file" "$CLAUDE_COMMANDS_DIR/"
                INSTALLED=$((INSTALLED + 1))
            fi
        done
        
        print_success "Installed $INSTALLED slash commands"
    else
        print_error "Commands directory not found in download"
        exit 1
    fi
}

# Show installed commands
show_commands() {
    echo
    echo "Installed Commands:"
    echo "=================="
    
    for cmd in "$CLAUDE_COMMANDS_DIR"/*.md; do
        if [ -f "$cmd" ]; then
            cmd_name=$(basename "$cmd" .md)
            # Extract description from YAML frontmatter
            description=$(sed -n '/^description:/s/description: *//p' "$cmd" 2>/dev/null | head -1)
            printf "  ${GREEN}/%-20s${NC} %s\n" "$cmd_name" "${description:-No description}"
        fi
    done
}

# Show usage
show_usage() {
    echo
    echo "========================================="
    echo "  Slash Commands Installed Successfully!"
    echo "========================================="
    echo
    echo "Usage Examples:"
    echo "--------------"
    echo
    echo "1. Start a new project:"
    echo "   ${GREEN}/new-project \"E-commerce platform with inventory management\"${NC}"
    echo
    echo "2. Analyze business viability:"
    echo "   ${GREEN}/business-analysis${NC}"
    echo
    echo "3. Create a frontend mockup:"
    echo "   ${GREEN}/frontend-mockup \"landing page for my startup\"${NC}"
    echo
    echo "4. Design a database schema:"
    echo "   ${GREEN}/database-design \"user management system\"${NC}"
    echo
    echo "5. List all commands:"
    echo "   ${GREEN}ls ~/.claude/commands/${NC}"
    echo
    echo "Pro tip: Commands support variables! Example:"
    echo "   ${GREEN}/project-plan \"Mobile App\" team:3 budget:50k deadline:\"2 months\"${NC}"
    echo
}

# Cleanup
cleanup() {
    rm -rf "$TEMP_DIR"
    print_success "Cleanup complete"
}

# Main installation
main() {
    echo
    echo "======================================"
    echo "  Claude Code Slash Commands Installer"
    echo "======================================"
    echo
    
    check_claude
    setup_directory
    download_commands
    install_commands
    show_commands
    cleanup
    show_usage
}

# Run installation
main

exit 0