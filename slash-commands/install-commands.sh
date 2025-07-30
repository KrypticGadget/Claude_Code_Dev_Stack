#!/bin/bash
# Claude Code Slash Commands - One Line Installer
# Install custom slash commands for Claude Code Agent System

set -e

# Configuration
CLAUDE_COMMANDS_DIR="$HOME/.claude/commands"
REPO_OWNER="KrypticGadget"
REPO_NAME="Claude_Code_Dev_Stack"
REPO_URL="https://github.com/${REPO_OWNER}/${REPO_NAME}"
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

# Check dependencies
check_dependencies() {
    local missing_deps=()
    
    # Check for unzip
    if ! command -v unzip &> /dev/null; then
        missing_deps+=("unzip")
    fi
    
    # Check for curl or wget
    if ! command -v curl &> /dev/null && ! command -v wget &> /dev/null; then
        missing_deps+=("curl or wget")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing required dependencies: ${missing_deps[*]}"
        echo "Please install missing dependencies:"
        echo "  Ubuntu/Debian: sudo apt-get install -y unzip curl"
        echo "  RHEL/CentOS: sudo yum install -y unzip curl"
        echo "  macOS: brew install curl (unzip is pre-installed)"
        echo "  WSL/Windows: sudo apt-get install -y unzip curl"
        exit 1
    fi
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
    
    # Check dependencies first
    check_dependencies
    
    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR"
    
    # Download the entire repository as a zip file (no authentication needed for public repos)
    if command -v curl &> /dev/null; then
        print_status "Using curl to download..."
        if curl -sL -o repo.zip "${REPO_URL}/archive/refs/heads/main.zip"; then
            unzip -q repo.zip
            if [ -d "${REPO_NAME}-main/slash-commands/commands" ]; then
                mkdir -p slash-commands
                cp -r "${REPO_NAME}-main/slash-commands/commands" slash-commands/
                print_success "Commands downloaded"
            else
                # Fallback to downloading individual files
                print_warning "Commands directory not found in archive, downloading individual files..."
                mkdir -p slash-commands/commands
                
                # Download individual command files
                for cmd in new-project business-analysis technical-feasibility frontend-mockup \
                          database-design api-integration project-plan financial-model \
                          backend-service documentation production-frontend middleware-setup \
                          site-architecture go-to-market tech-alignment requirements prompt-enhance \
                          resume-project; do
                    curl -sL "${REPO_URL}/raw/main/slash-commands/commands/$cmd.md" \
                         -o "slash-commands/commands/$cmd.md" 2>/dev/null || true
                done
                print_success "Commands downloaded individually"
            fi
        else
            print_error "Failed to download repository"
            exit 1
        fi
    elif command -v wget &> /dev/null; then
        print_status "Using wget to download..."
        if wget -q -O repo.zip "${REPO_URL}/archive/refs/heads/main.zip"; then
            unzip -q repo.zip
            if [ -d "${REPO_NAME}-main/slash-commands/commands" ]; then
                mkdir -p slash-commands
                cp -r "${REPO_NAME}-main/slash-commands/commands" slash-commands/
                print_success "Commands downloaded"
            else
                print_error "Commands directory not found in download"
                exit 1
            fi
        else
            print_error "Failed to download repository"
            exit 1
        fi
    else
        print_error "Neither curl nor wget found. Please install curl or wget."
        exit 1
    fi
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