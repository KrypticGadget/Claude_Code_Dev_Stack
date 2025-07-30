#!/bin/bash
# Update Claude Code Agents to latest version

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
REPO_URL="https://github.com/yourusername/claude-code-agent-system.git"
TEMP_DIR="/tmp/claude-agent-update-$$"
AGENTS_DIR="$HOME/.claude/agents"
BACKUP_DIR="$HOME/.claude/backups/update-$(date +%Y%m%d_%H%M%S)"

echo "Claude Code Agent System Updater"
echo "================================"
echo

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

# Check if agents are installed
if [ ! -d "$AGENTS_DIR" ]; then
    print_error "Agents directory not found at $AGENTS_DIR"
    echo "Please run install.sh first"
    exit 1
fi

# Create backup
print_status "Creating backup of current agents..."
mkdir -p "$BACKUP_DIR"
cp -r "$AGENTS_DIR" "$BACKUP_DIR/"
print_success "Backup created at $BACKUP_DIR"

# Download latest version
print_status "Downloading latest agent configurations..."
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"

if ! git clone --depth 1 "$REPO_URL" . &> /dev/null; then
    print_error "Failed to download latest agents"
    
    # Try alternative download methods
    if command -v wget &> /dev/null; then
        wget -q -O agents.zip "${REPO_URL%.git}/archive/main.zip"
        unzip -q agents.zip
        mv claude-code-agent-system-main/* .
    elif command -v curl &> /dev/null; then
        curl -sL -o agents.zip "${REPO_URL%.git}/archive/main.zip"
        unzip -q agents.zip
        mv claude-code-agent-system-main/* .
    else
        print_error "Cannot download updates. No git, wget, or curl available."
        exit 1
    fi
fi

print_success "Latest version downloaded"

# Check for changes
print_status "Checking for updates..."
UPDATES=0
NEW_AGENTS=0

if [ -d "$TEMP_DIR/Config_Files" ]; then
    for agent_file in "$TEMP_DIR/Config_Files/"*.md; do
        agent_name=$(basename "$agent_file")
        existing_file="$AGENTS_DIR/$agent_name"
        
        if [ -f "$existing_file" ]; then
            # Check if files are different
            if ! cmp -s "$agent_file" "$existing_file"; then
                cp "$agent_file" "$existing_file"
                print_success "Updated: $agent_name"
                ((UPDATES++))
            fi
        else
            # New agent
            cp "$agent_file" "$AGENTS_DIR/"
            print_success "New agent: $agent_name"
            ((NEW_AGENTS++))
        fi
    done
else
    print_error "Config_Files directory not found in download"
    exit 1
fi

# Update scripts
if [ -d "$TEMP_DIR/scripts" ]; then
    print_status "Updating helper scripts..."
    SCRIPTS_DIR="$HOME/.claude/scripts"
    mkdir -p "$SCRIPTS_DIR"
    cp -r "$TEMP_DIR/scripts/"*.sh "$SCRIPTS_DIR/" 2>/dev/null || true
    chmod +x "$SCRIPTS_DIR/"*.sh 2>/dev/null || true
    print_success "Scripts updated"
fi

# Update documentation
if [ -d "$TEMP_DIR/docs" ] || [ -f "$TEMP_DIR/README.md" ]; then
    print_status "Updating documentation..."
    DOCS_DIR="$HOME/.claude/docs"
    mkdir -p "$DOCS_DIR"
    
    [ -f "$TEMP_DIR/README.md" ] && cp "$TEMP_DIR/README.md" "$DOCS_DIR/"
    [ -f "$TEMP_DIR/QUICK_START.md" ] && cp "$TEMP_DIR/QUICK_START.md" "$DOCS_DIR/"
    [ -f "$TEMP_DIR/CHEAT_SHEET.md" ] && cp "$TEMP_DIR/CHEAT_SHEET.md" "$DOCS_DIR/"
    
    print_success "Documentation updated"
fi

# Cleanup
print_status "Cleaning up..."
rm -rf "$TEMP_DIR"
print_success "Cleanup complete"

# Summary
echo
echo "Update Summary"
echo "=============="
echo "Updated agents:  $UPDATES"
echo "New agents:      $NEW_AGENTS"
echo "Backup location: $BACKUP_DIR"
echo

# Verify installation
"$HOME/.claude/scripts/validate-agents.sh" 2>/dev/null || true

echo
print_success "Update complete!"
echo
echo "To restore previous version:"
echo "  cp -r $BACKUP_DIR/agents/* $AGENTS_DIR/"