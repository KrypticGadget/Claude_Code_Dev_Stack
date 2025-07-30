#!/bin/bash
# Claude Code Agent System - One Line Installer
# https://github.com/yourusername/claude-code-agent-system

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/yourusername/claude-code-agent-system.git"
TEMP_DIR="/tmp/claude-agent-install-$$"
CLAUDE_DIR="$HOME/.claude"
AGENTS_DIR="$CLAUDE_DIR/agents"
BACKUP_DIR="$CLAUDE_DIR/backups/$(date +%Y%m%d_%H%M%S)"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Function to check if Claude Code is installed
check_claude_code() {
    if ! command -v claude &> /dev/null; then
        print_error "Claude Code CLI not found!"
        echo "Please install Claude Code first: https://docs.anthropic.com/en/docs/claude-code"
        exit 1
    fi
    print_success "Claude Code CLI detected"
}

# Function to create necessary directories
setup_directories() {
    print_status "Setting up Claude directories..."
    
    # Create Claude directory if it doesn't exist
    if [ ! -d "$CLAUDE_DIR" ]; then
        mkdir -p "$CLAUDE_DIR"
        print_success "Created $CLAUDE_DIR"
    fi
    
    # Backup existing agents if they exist
    if [ -d "$AGENTS_DIR" ] && [ "$(ls -A $AGENTS_DIR 2>/dev/null)" ]; then
        print_warning "Existing agents found. Creating backup..."
        mkdir -p "$BACKUP_DIR"
        cp -r "$AGENTS_DIR" "$BACKUP_DIR/"
        print_success "Backup created at $BACKUP_DIR"
    fi
    
    # Create agents directory
    mkdir -p "$AGENTS_DIR"
    print_success "Agents directory ready at $AGENTS_DIR"
}

# Function to download agent configurations
download_agents() {
    print_status "Downloading Claude Code Agent System..."
    
    # Create temporary directory
    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR"
    
    # Clone repository
    if ! git clone --depth 1 "$REPO_URL" . &> /dev/null; then
        print_error "Failed to download agent system"
        echo "Attempting direct download..."
        
        # Fallback to wget/curl
        if command -v wget &> /dev/null; then
            wget -q -O agents.zip "${REPO_URL%.git}/archive/main.zip"
            unzip -q agents.zip
            mv claude-code-agent-system-main/* .
        elif command -v curl &> /dev/null; then
            curl -sL -o agents.zip "${REPO_URL%.git}/archive/main.zip"
            unzip -q agents.zip
            mv claude-code-agent-system-main/* .
        else
            print_error "Neither git, wget, nor curl found. Cannot download agents."
            exit 1
        fi
    fi
    
    print_success "Agent system downloaded"
}

# Function to install agents
install_agents() {
    print_status "Installing 28 specialized agents..."
    
    # Copy all agent configurations
    if [ -d "$TEMP_DIR/Config_Files" ]; then
        cp -r "$TEMP_DIR/Config_Files/"*.md "$AGENTS_DIR/" 2>/dev/null || true
        
        # Count installed agents
        AGENT_COUNT=$(ls -1 "$AGENTS_DIR"/*.md 2>/dev/null | wc -l)
        
        if [ "$AGENT_COUNT" -eq 28 ]; then
            print_success "All 28 agents installed successfully!"
        else
            print_warning "Installed $AGENT_COUNT agents (expected 28)"
        fi
    else
        print_error "Config_Files directory not found in download"
        exit 1
    fi
}

# Function to install helper scripts
install_scripts() {
    print_status "Installing helper scripts..."
    
    # Create scripts directory
    SCRIPTS_DIR="$CLAUDE_DIR/scripts"
    mkdir -p "$SCRIPTS_DIR"
    
    # Copy scripts if they exist
    if [ -d "$TEMP_DIR/scripts" ]; then
        cp -r "$TEMP_DIR/scripts/"*.sh "$SCRIPTS_DIR/" 2>/dev/null || true
        chmod +x "$SCRIPTS_DIR/"*.sh 2>/dev/null || true
        print_success "Helper scripts installed to $SCRIPTS_DIR"
    else
        print_warning "No helper scripts found in repository"
    fi
}

# Function to setup documentation
setup_documentation() {
    print_status "Setting up documentation..."
    
    # Create docs directory
    DOCS_DIR="$CLAUDE_DIR/docs"
    mkdir -p "$DOCS_DIR"
    
    # Copy documentation
    if [ -f "$TEMP_DIR/README.md" ]; then
        cp "$TEMP_DIR/README.md" "$DOCS_DIR/"
    fi
    
    if [ -f "$TEMP_DIR/QUICK_START.md" ]; then
        cp "$TEMP_DIR/QUICK_START.md" "$DOCS_DIR/"
    fi
    
    if [ -f "$TEMP_DIR/CHEAT_SHEET.md" ]; then
        cp "$TEMP_DIR/CHEAT_SHEET.md" "$DOCS_DIR/"
    fi
    
    print_success "Documentation installed to $DOCS_DIR"
}

# Function to verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    # List installed agents
    echo
    echo "Installed agents:"
    echo "================"
    
    # Show agent list with descriptions
    for agent in "$AGENTS_DIR"/*.md; do
        if [ -f "$agent" ]; then
            agent_name=$(basename "$agent" .md)
            # Extract description from agent file
            description=$(grep -A1 "^description:" "$agent" 2>/dev/null | tail -1 | sed 's/^[[:space:]]*//' || echo "No description")
            printf "  %-35s %s\n" "$agent_name" "${description:0:40}..."
        fi
    done
    
    echo
    print_success "Installation verified"
}

# Function to show next steps
show_next_steps() {
    echo
    echo "=========================================="
    echo "  Claude Code Agent System Installed!"
    echo "=========================================="
    echo
    echo "Quick Start Commands:"
    echo "--------------------"
    echo
    echo "1. Start a new project with the Master Orchestrator:"
    echo "   ${GREEN}> Use the master-orchestrator agent to begin new project: \"Your Project Description\"${NC}"
    echo
    echo "2. List available agents:"
    echo "   ${GREEN}ls ~/.claude/agents/${NC}"
    echo
    echo "3. Use a specific agent:"
    echo "   ${GREEN}> Use the [agent-name] agent to [task description]${NC}"
    echo
    echo "4. View documentation:"
    echo "   ${GREEN}cat ~/.claude/docs/QUICK_START.md${NC}"
    echo
    echo "5. View cheat sheet:"
    echo "   ${GREEN}cat ~/.claude/docs/CHEAT_SHEET.md${NC}"
    echo
    echo "For more information, visit: https://github.com/yourusername/claude-code-agent-system"
    echo
}

# Function to cleanup
cleanup() {
    print_status "Cleaning up temporary files..."
    rm -rf "$TEMP_DIR"
    print_success "Cleanup complete"
}

# Main installation flow
main() {
    echo
    echo "======================================"
    echo "  Claude Code Agent System Installer"
    echo "======================================"
    echo
    
    # Check prerequisites
    check_claude_code
    
    # Setup directories
    setup_directories
    
    # Download agents
    download_agents
    
    # Install components
    install_agents
    install_scripts
    setup_documentation
    
    # Verify installation
    verify_installation
    
    # Cleanup
    cleanup
    
    # Show next steps
    show_next_steps
}

# Run main installation
main

# Exit successfully
exit 0