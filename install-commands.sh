#!/bin/bash
# Claude Code Slash Commands Installer for Ubuntu/WSL
# Version: 2.0
# Installs 18 slash commands globally to Claude Code root directory

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}Claude Code Global Slash Commands Installer${NC}"
echo -e "${CYAN}===========================================${NC}"
echo ""

# Function to find Claude Code root installation
find_claude_code_root() {
    local possible_paths=(
        "$HOME/.config/Claude"
        "$HOME/.local/share/Claude"
        "$HOME/Claude"
        "/opt/Claude"
        "/usr/local/Claude"
    )
    
    # WSL specific: Check Windows directories
    if [[ -f /proc/sys/fs/binfmt_misc/WSLInterop ]]; then
        # Detect Windows username
        local win_user
        if [[ -n "$USERPROFILE" ]]; then
            win_user=$(basename "$USERPROFILE")
        else
            win_user="$USER"
        fi
        
        possible_paths+=(
            "/mnt/c/Users/$win_user/AppData/Roaming/Claude"
            "/mnt/c/Users/$win_user/AppData/Local/Claude"
            "/mnt/c/ProgramData/Claude"
        )
    fi
    
    for path in "${possible_paths[@]}"; do
        if [[ -d "$path" ]]; then
            echo "$path"
            return 0
        fi
    done
    
    # Default path
    local default_path="$HOME/.config/Claude"
    echo -e "${YELLOW}Claude Code installation not found. Creating directory at: $default_path${NC}" >&2
    echo "$default_path"
}

# Find Claude Code root directory
CLAUDE_ROOT=$(find_claude_code_root)
COMMANDS_PATH="$CLAUDE_ROOT/commands"
REGISTRY_PATH="$CLAUDE_ROOT/commands-registry.json"
SETTINGS_PATH="$CLAUDE_ROOT/settings.json"

echo -e "${GREEN}Claude Code root: $CLAUDE_ROOT${NC}"
echo -e "${GREEN}Commands will be installed to: $COMMANDS_PATH${NC}"

# Create directory if it doesn't exist
if [[ ! -d "$COMMANDS_PATH" ]]; then
    echo -e "${YELLOW}Creating global commands directory...${NC}"
    mkdir -p "$COMMANDS_PATH"
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

# Initialize command registry
echo "{" > "$REGISTRY_PATH.tmp"
echo '  "version": "2.0",' >> "$REGISTRY_PATH.tmp"
echo "  \"installed\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"," >> "$REGISTRY_PATH.tmp"
echo '  "commands": [' >> "$REGISTRY_PATH.tmp"

# Download each command
FIRST_COMMAND=true
for command in "${commands[@]}"; do
    ((COMPLETED++))
    PERCENT=$((COMPLETED * 100 / TOTAL_COMMANDS))
    
    # Progress bar
    printf "\r[%-50s] %d%%" $(printf '#%.0s' $(seq 1 $((PERCENT / 2)))) $PERCENT
    
    URL="${BASE_URL}${command}"
    DESTINATION="${COMMANDS_PATH}/${command}"
    
    if $DOWNLOAD_CMD "$URL" > "$DESTINATION" 2>/dev/null; then
        echo -e "\r[$COMPLETED/$TOTAL_COMMANDS] ${GREEN}✓${NC} $command                                        "
        
        # Add to registry
        COMMAND_NAME="${command%.md}"
        if [[ "$FIRST_COMMAND" != "true" ]]; then
            echo "," >> "$REGISTRY_PATH.tmp"
        fi
        printf '    {\n      "name": "%s",\n      "file": "%s",\n      "path": "%s",\n      "description": "/%s - Claude Code development command"\n    }' \
            "$COMMAND_NAME" "$command" "$DESTINATION" "$COMMAND_NAME" >> "$REGISTRY_PATH.tmp"
        FIRST_COMMAND=false
    else
        ((FAILED++))
        echo -e "\r[$COMPLETED/$TOTAL_COMMANDS] ${RED}✗${NC} $command - Download failed                     "
        rm -f "$DESTINATION" 2>/dev/null
    fi
done

# Complete registry JSON
echo "" >> "$REGISTRY_PATH.tmp"
echo "  ]" >> "$REGISTRY_PATH.tmp"
echo "}" >> "$REGISTRY_PATH.tmp"

# Move registry to final location
if mv "$REGISTRY_PATH.tmp" "$REGISTRY_PATH"; then
    echo -e "${GREEN}✓ Command registry created at: $REGISTRY_PATH${NC}"
else
    echo -e "${RED}✗ Failed to create command registry${NC}"
fi

# Update Claude Code settings if exists
if [[ -f "$SETTINGS_PATH" ]]; then
    echo -e "${YELLOW}Updating Claude Code settings...${NC}"
    if command -v jq &> /dev/null; then
        # Use jq if available
        jq --arg cp "$COMMANDS_PATH" --arg cr "$REGISTRY_PATH" \
            '. + {commandsPath: $cp, commandRegistry: $cr}' \
            "$SETTINGS_PATH" > "$SETTINGS_PATH.tmp" && mv "$SETTINGS_PATH.tmp" "$SETTINGS_PATH"
        echo -e "${GREEN}✓ Updated Claude Code settings${NC}"
    else
        echo -e "${YELLOW}Note: Install jq for automatic settings update${NC}"
    fi
fi

echo ""
echo ""
echo -e "${CYAN}Global Installation Complete!${NC}"
echo -e "${CYAN}============================${NC}"
echo -e "${GREEN}Successfully installed: $((TOTAL_COMMANDS - FAILED)) commands${NC}"
if [[ $FAILED -gt 0 ]]; then
    echo -e "${RED}Failed: $FAILED commands${NC}"
fi
echo ""
echo -e "${YELLOW}Installation Details:${NC}"
echo -e "${YELLOW}  • Claude Code Root: $CLAUDE_ROOT${NC}"
echo -e "${YELLOW}  • Commands Directory: $COMMANDS_PATH${NC}"
echo -e "${YELLOW}  • Command Registry: $REGISTRY_PATH${NC}"
echo ""
echo -e "${CYAN}These commands are now globally available in ALL your Claude Code projects!${NC}"
echo -e "${CYAN}You can use them by typing '/' in any chat, for example: /new-project${NC}"
echo ""

# Test command availability
echo -e "${YELLOW}Testing command availability...${NC}"
TEST_COMMAND="$COMMANDS_PATH/new-project.md"
if [[ -f "$TEST_COMMAND" ]]; then
    echo -e "${GREEN}✓ /new-project command is ready to use!${NC}"
else
    echo -e "${RED}✗ Command test failed - please check installation${NC}"
fi
echo ""