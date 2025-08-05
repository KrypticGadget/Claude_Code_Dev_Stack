#!/bin/bash
# Claude Code Slash Commands Installer for Ubuntu/WSL
# Version: 1.0
# Installs 18 slash commands from the Claude_Code_Dev_Stack repository

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}Claude Code Slash Commands Installer${NC}"
echo -e "${CYAN}====================================${NC}"
echo ""

# Function to find Claude Code installation
find_claude_code_path() {
    local possible_paths=(
        "$HOME/.config/Claude/slash-commands/commands"
        "$HOME/.local/share/Claude/slash-commands/commands"
        "$HOME/Claude/slash-commands/commands"
        "/mnt/c/Users/$USER/AppData/Roaming/Claude/slash-commands/commands"
        "/mnt/c/Users/$USER/AppData/Local/Claude/slash-commands/commands"
    )
    
    for path in "${possible_paths[@]}"; do
        if [[ -d "$(dirname "$(dirname "$path")")" ]]; then
            echo "$path"
            return 0
        fi
    done
    
    # WSL specific: Check Windows user directories
    if [[ -n "$USERPROFILE" ]]; then
        local win_path="/mnt/c${USERPROFILE//\\//}/AppData/Roaming/Claude/slash-commands/commands"
        win_path="${win_path//C://c}"
        if [[ -d "$(dirname "$(dirname "$win_path")")" ]]; then
            echo "$win_path"
            return 0
        fi
    fi
    
    # Default path
    local default_path="$HOME/.config/Claude/slash-commands/commands"
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

# Check for required tools
if ! command -v curl &> /dev/null && ! command -v wget &> /dev/null; then
    echo -e "${RED}Error: Neither curl nor wget found. Please install one of them.${NC}"
    exit 1
fi

# Determine download tool
if command -v curl &> /dev/null; then
    DOWNLOAD_CMD="curl -fsSL"
else
    DOWNLOAD_CMD="wget -qO-"
fi

# Download each command
for command in "${commands[@]}"; do
    ((COMPLETED++))
    PERCENT=$((COMPLETED * 100 / TOTAL_COMMANDS))
    
    # Progress bar
    printf "\r[%-50s] %d%%" $(printf '#%.0s' $(seq 1 $((PERCENT / 2)))) $PERCENT
    
    URL="${BASE_URL}${command}"
    DESTINATION="${INSTALL_PATH}/${command}"
    
    if $DOWNLOAD_CMD "$URL" > "$DESTINATION" 2>/dev/null; then
        echo -e "\r[$COMPLETED/$TOTAL_COMMANDS] ${GREEN}✓${NC} $command                                        "
    else
        ((FAILED++))
        echo -e "\r[$COMPLETED/$TOTAL_COMMANDS] ${RED}✗${NC} $command - Download failed                     "
        rm -f "$DESTINATION" 2>/dev/null
    fi
done

echo ""
echo ""
echo -e "${CYAN}Installation Complete!${NC}"
echo -e "${CYAN}=====================${NC}"
echo -e "${GREEN}Successfully installed: $((TOTAL_COMMANDS - FAILED)) commands${NC}"
if [[ $FAILED -gt 0 ]]; then
    echo -e "${RED}Failed: $FAILED commands${NC}"
fi
echo ""
echo -e "${YELLOW}Commands installed to: $INSTALL_PATH${NC}"
echo ""
echo -e "${CYAN}You can now use these commands in Claude Code by typing '/' in the chat.${NC}"
echo ""