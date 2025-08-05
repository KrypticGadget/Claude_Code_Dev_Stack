#!/bin/bash
# Claude Code Slash Commands Installer for macOS
# Version: 1.0
# Installs 18 slash commands from the Claude_Code_Dev_Stack repository

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}Claude Code Slash Commands Installer for macOS${NC}"
echo -e "${CYAN}=============================================${NC}"
echo ""

# Function to find Claude Code installation
find_claude_code_path() {
    local possible_paths=(
        "$HOME/Library/Application Support/Claude/slash-commands/commands"
        "$HOME/.claude/slash-commands/commands"
        "$HOME/.config/Claude/slash-commands/commands"
        "$HOME/Documents/Claude/slash-commands/commands"
        "/Applications/Claude.app/Contents/Resources/slash-commands/commands"
    )
    
    for path in "${possible_paths[@]}"; do
        if [[ -d "$(dirname "$(dirname "$path")")" ]]; then
            echo "$path"
            return 0
        fi
    done
    
    # Default macOS path
    local default_path="$HOME/Library/Application Support/Claude/slash-commands/commands"
    echo -e "${YELLOW}Claude Code installation not found. Creating directory at: $default_path${NC}"
    echo "$default_path"
}

# Find or create the installation path
INSTALL_PATH=$(find_claude_code_path)
echo -e "${GREEN}Installation path: $INSTALL_PATH${NC}"

# Create directory if it doesn't exist
if [[ ! -d "$INSTALL_PATH" ]]; then
    echo -e "${YELLOW}Creating directory structure...${NC}"
    mkdir -p "$INSTALL_PATH"
fi

# List of all 18 command files
commands=(
    "api-integration.md"
    "backend-service.md"
    "business-analysis.md"
    "database-design.md"
    "documentation.md"
    "financial-model.md"
    "frontend-mockup.md"
    "go-to-market.md"
    "middleware-setup.md"
    "new-project.md"
    "production-frontend.md"
    "project-plan.md"
    "prompt-enhance.md"
    "requirements.md"
    "resume-project.md"
    "site-architecture.md"
    "tech-alignment.md"
    "technical-feasibility.md"
)

BASE_URL="https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/slash-commands/commands/"
TOTAL_COMMANDS=${#commands[@]}
COMPLETED=0
FAILED=0

echo ""
echo -e "${CYAN}Downloading $TOTAL_COMMANDS slash commands...${NC}"

# macOS comes with curl by default
DOWNLOAD_CMD="curl -fsSL"

# Function to show progress bar
show_progress() {
    local current=$1
    local total=$2
    local percent=$((current * 100 / total))
    local filled=$((percent / 2))
    
    printf "\r["
    printf "%-50s" "$(printf '#%.0s' $(seq 1 $filled))"
    printf "] %d%%" $percent
}

# Download each command
for command in "${commands[@]}"; do
    ((COMPLETED++))
    
    show_progress $COMPLETED $TOTAL_COMMANDS
    
    URL="${BASE_URL}${command}"
    DESTINATION="${INSTALL_PATH}/${command}"
    
    if $DOWNLOAD_CMD "$URL" -o "$DESTINATION" 2>/dev/null; then
        printf "\r[$COMPLETED/$TOTAL_COMMANDS] ${GREEN}✓${NC} %-40s\n" "$command"
    else
        ((FAILED++))
        printf "\r[$COMPLETED/$TOTAL_COMMANDS] ${RED}✗${NC} %-40s - Download failed\n" "$command"
        rm -f "$DESTINATION" 2>/dev/null
    fi
done

# Clear progress bar line
printf "\r%-70s\r" ""

echo ""
echo -e "${CYAN}Installation Complete!${NC}"
echo -e "${CYAN}=====================${NC}"
echo -e "${GREEN}Successfully installed: $((TOTAL_COMMANDS - FAILED)) commands${NC}"
if [[ $FAILED -gt 0 ]]; then
    echo -e "${RED}Failed: $FAILED commands${NC}"
fi
echo ""
echo -e "${YELLOW}Commands installed to:${NC}"
echo "$INSTALL_PATH"
echo ""
echo -e "${CYAN}You can now use these commands in Claude Code by typing '/' in the chat.${NC}"
echo ""

# Check if Claude Code is running
if pgrep -x "Claude" > /dev/null; then
    echo -e "${YELLOW}Note: You may need to restart Claude Code for the commands to appear.${NC}"
    echo ""
fi