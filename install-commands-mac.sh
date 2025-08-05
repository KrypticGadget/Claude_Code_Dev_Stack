#!/bin/bash
# Claude Code Slash Commands Installer for macOS
# Version: 2.0
# Installs 18 slash commands globally to Claude Code root directory

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}Claude Code Global Slash Commands Installer for macOS${NC}"
echo -e "${CYAN}=====================================================${NC}"
echo ""

# Function to find Claude Code root installation
find_claude_code_root() {
    local possible_paths=(
        "$HOME/Library/Application Support/Claude"
        "$HOME/.claude"
        "$HOME/.config/Claude"
        "$HOME/Documents/Claude"
        "/Applications/Claude.app/Contents/Resources"
        "/Library/Application Support/Claude"
    )
    
    for path in "${possible_paths[@]}"; do
        if [[ -d "$path" ]]; then
            echo "$path"
            return 0
        fi
    done
    
    # Default macOS path
    local default_path="$HOME/Library/Application Support/Claude"
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

# Initialize command registry
cat > "$REGISTRY_PATH.tmp" << EOF
{
  "version": "2.0",
  "installed": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "commands": [
EOF

# Download each command
FIRST_COMMAND=true
for command in "${commands[@]}"; do
    ((COMPLETED++))
    
    show_progress $COMPLETED $TOTAL_COMMANDS
    
    URL="${BASE_URL}${command}"
    DESTINATION="${COMMANDS_PATH}/${command}"
    
    if $DOWNLOAD_CMD "$URL" -o "$DESTINATION" 2>/dev/null; then
        printf "\r[$COMPLETED/$TOTAL_COMMANDS] ${GREEN}✓${NC} %-40s\n" "$command"
        
        # Add to registry
        COMMAND_NAME="${command%.md}"
        if [[ "$FIRST_COMMAND" != "true" ]]; then
            echo "," >> "$REGISTRY_PATH.tmp"
        fi
        cat >> "$REGISTRY_PATH.tmp" << EOF
    {
      "name": "$COMMAND_NAME",
      "file": "$command",
      "path": "$DESTINATION",
      "description": "/$COMMAND_NAME - Claude Code development command"
    }
EOF
        FIRST_COMMAND=false
    else
        ((FAILED++))
        printf "\r[$COMPLETED/$TOTAL_COMMANDS] ${RED}✗${NC} %-40s - Download failed\n" "$command"
        rm -f "$DESTINATION" 2>/dev/null
    fi
done

# Complete registry JSON
cat >> "$REGISTRY_PATH.tmp" << EOF

  ]
}
EOF

# Move registry to final location
if mv "$REGISTRY_PATH.tmp" "$REGISTRY_PATH"; then
    echo -e "${GREEN}✓ Command registry created at: $REGISTRY_PATH${NC}"
else
    echo -e "${RED}✗ Failed to create command registry${NC}"
fi

# Clear progress bar line
printf "\r%-70s\r" ""

# Update Claude Code settings if exists
if [[ -f "$SETTINGS_PATH" ]]; then
    echo -e "${YELLOW}Updating Claude Code settings...${NC}"
    # macOS has Python by default, use it for JSON manipulation
    if command -v python3 &> /dev/null; then
        python3 -c "
import json
with open('$SETTINGS_PATH', 'r') as f:
    settings = json.load(f)
settings['commandsPath'] = '$COMMANDS_PATH'
settings['commandRegistry'] = '$REGISTRY_PATH'
with open('$SETTINGS_PATH', 'w') as f:
    json.dump(settings, f, indent=2)
"
        echo -e "${GREEN}✓ Updated Claude Code settings${NC}"
    else
        echo -e "${YELLOW}Note: Could not update settings automatically${NC}"
    fi
fi

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

# Check if Claude Code is running
if pgrep -x "Claude" > /dev/null; then
    echo -e "${YELLOW}Note: You may need to restart Claude Code for the commands to appear.${NC}"
    echo ""
fi