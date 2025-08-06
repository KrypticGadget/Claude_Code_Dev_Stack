#!/bin/bash

# Claude Code Agents Installer for Ubuntu/WSL - GLOBAL Installation
# Downloads and installs 28 AI agents to Claude Code ROOT directory
# Enables @agent- mentions from ANY project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_BASE="https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example/agents"
AGENTS=(
    "api-integration-specialist-agent.md"
    "backend-services-agent.md"
    "business-analyst-agent.md"
    "business-tech-alignment-agent.md"
    "ceo-strategy-agent.md"
    "database-architecture-agent.md"
    "development-prompt-agent.md"
    "devops-engineering-agent.md"
    "financial-analyst-agent.md"
    "frontend-architecture-agent.md"
    "frontend-mockup-agent.md"
    "integration-setup-agent.md"
    "master-orchestrator-agent.md"
    "middleware-specialist-agent.md"
    "mobile-development-agent.md"
    "performance-optimization-agent.md"
    "production-frontend-agent.md"
    "project-manager-agent.md"
    "prompt-engineer-agent.md"
    "quality-assurance-agent.md"
    "script-automation-agent.md"
    "security-architecture-agent.md"
    "technical-cto-agent.md"
    "technical-documentation-agent.md"
    "technical-specifications-agent.md"
    "testing-automation-agent.md"
    "ui-ux-design-agent.md"
    "usage-guide-agent.md"
)

echo -e "${CYAN}Claude Code Agents Installer v2.0 - GLOBAL Installation${NC}"
echo -e "${CYAN}======================================================${NC}"
echo -e "${YELLOW}This will install agents GLOBALLY for use in ANY project${NC}"

# Function to detect Claude Code ROOT installation path (not project-specific)
find_claude_code_root_path() {
    # Check environment variable first
    if [ -n "$CLAUDE_CODE_ROOT" ]; then
        echo -e "${GREEN}Using CLAUDE_CODE_ROOT environment variable: $CLAUDE_CODE_ROOT${NC}"
        echo "$CLAUDE_CODE_ROOT"
        return 0
    fi
    
    # Common Claude Code root paths (NOT project-specific)
    local possible_paths=(
        "$HOME/.claude"
        "$HOME/.config/Claude"
        "$HOME/.claude-code"
        "$HOME/.config/claude-code"
        "/mnt/c/Users/$USER/.claude"  # WSL path for Windows Claude root
        "/mnt/c/Users/$USER/AppData/Roaming/Claude"  # WSL Windows AppData path
    )
    
    for path in "${possible_paths[@]}"; do
        if [ -d "$path" ]; then
            # Verify this is the root by checking for config files
            if [ -f "$path/settings.json" ] || [ -f "$path/config.json" ] || [ -f "$path/.claude" ]; then
                echo -e "${GREEN}Found Claude Code root directory at: $path${NC}"
                echo "$path"
                return 0
            fi
        fi
    done
    
    # Create default if not found
    local default_path="$HOME/.claude"
    echo -e "${YELLOW}Claude Code root not found. Creating at: $default_path${NC}"
    mkdir -p "$default_path"
    echo "$default_path"
}

# Check for required commands
check_requirements() {
    local missing_tools=()
    
    if ! command -v curl &> /dev/null; then
        missing_tools+=("curl")
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        echo -e "${RED}Error: Missing required tools: ${missing_tools[*]}${NC}"
        echo -e "${YELLOW}Please install with: sudo apt-get install ${missing_tools[*]}${NC}"
        exit 1
    fi
}

# Show progress bar
show_progress() {
    local current=$1
    local total=$2
    local width=50
    local percent=$((current * 100 / total))
    local filled=$((width * current / total))
    
    printf "\rProgress: ["
    printf "%${filled}s" | tr ' ' '='
    printf "%$((width - filled))s" | tr ' ' ' '
    printf "] %d%% (%d/%d)" $percent $current $total
}

# Main installation
main() {
    check_requirements
    
    local claude_root_path=$(find_claude_code_root_path)
    local agents_dir="$claude_root_path/agents"
    
    echo -e "${GREEN}Installing to Claude Code ROOT: $claude_root_path${NC}"
    
    # Create agents directory if it doesn't exist
    if [ ! -d "$agents_dir" ]; then
        echo -e "${YELLOW}Creating agents directory...${NC}"
        mkdir -p "$agents_dir"
    fi
    
    # Download agents
    local total_agents=${#AGENTS[@]}
    local downloaded=0
    local failed_agents=()
    
    echo -e "\n${YELLOW}Downloading $total_agents agents...${NC}"
    
    for agent in "${AGENTS[@]}"; do
        ((downloaded++))
        show_progress $downloaded $total_agents
        
        local url="$REPO_BASE/$agent"
        local destination="$agents_dir/$agent"
        
        # Download with retry logic
        local retry_count=0
        local max_retries=3
        local success=false
        
        while [ $retry_count -lt $max_retries ] && [ "$success" = false ]; do
            if curl -sL --fail --connect-timeout 10 --max-time 30 "$url" -o "$destination" 2>/dev/null; then
                success=true
            else
                ((retry_count++))
                if [ $retry_count -lt $max_retries ]; then
                    sleep 1
                fi
            fi
        done
        
        if [ "$success" = false ]; then
            failed_agents+=("$agent")
            echo -e "\n${RED}Failed to download: $agent${NC}"
        fi
    done
    
    echo -e "\n\n${CYAN}Installation Summary${NC}"
    echo -e "${CYAN}===================${NC}"
    echo -e "Total agents: $total_agents"
    echo -e "${GREEN}Successfully installed: $((total_agents - ${#failed_agents[@]}))${NC}"
    
    if [ ${#failed_agents[@]} -gt 0 ]; then
        echo -e "${RED}Failed: ${#failed_agents[@]}${NC}"
        echo -e "${RED}Failed agents:${NC}"
        for agent in "${failed_agents[@]}"; do
            echo -e "${RED}  - $agent${NC}"
        done
    fi
    
    echo -e "\n${GREEN}Agents installed to: $agents_dir${NC}"
    
    # Create agent-config.yaml for global agent registry
    local config_file="$claude_root_path/agent-config.yaml"
    echo -e "\n${YELLOW}Creating global agent registry...${NC}"
    
    cat > "$config_file" << EOF
# Claude Code Global Agent Registry
# Auto-generated by install-agents.sh
# This file enables @agent- mentions from ANY project

version: 2.0
global_agents_path: $agents_dir
enabled: true

agents:
EOF
    
    for agent in "${AGENTS[@]}"; do
        local agent_name=$(echo "$agent" | sed 's/\.md$//' | sed 's/-agent$//')
        cat >> "$config_file" << EOF
  - name: $agent_name
    file: $agent
    trigger: "@agent-$agent_name"
EOF
    done
    
    echo -e "${GREEN}Created agent registry: $config_file${NC}"
    
    # Update Claude Code settings.json to include agent configuration
    local settings_file="$claude_root_path/settings.json"
    if [ -f "$settings_file" ]; then
        echo -e "${YELLOW}Updating Claude Code settings...${NC}"
        
        # Backup original settings
        cp "$settings_file" "$settings_file.bak"
        
        # Update settings using jq if available, otherwise use python
        if command -v jq &> /dev/null; then
            jq '.agents = {
                "enabled": true,
                "globalPath": "'"$agents_dir"'",
                "configFile": "'"$config_file"'",
                "autoComplete": true,
                "showInMenu": true
            }' "$settings_file" > "$settings_file.tmp" && mv "$settings_file.tmp" "$settings_file"
            echo -e "${GREEN}Updated settings.json with agent configuration${NC}"
        elif command -v python3 &> /dev/null; then
            python3 -c "
import json
with open('$settings_file', 'r') as f:
    settings = json.load(f)
settings['agents'] = {
    'enabled': True,
    'globalPath': '$agents_dir',
    'configFile': '$config_file',
    'autoComplete': True,
    'showInMenu': True
}
with open('$settings_file', 'w') as f:
    json.dump(settings, f, indent=2)
"
            echo -e "${GREEN}Updated settings.json with agent configuration${NC}"
        else
            echo -e "${YELLOW}Warning: Could not update settings.json automatically${NC}"
            echo -e "${YELLOW}Please add the following to your settings.json:${NC}"
            echo -e "${CYAN}{
  \"agents\": {
    \"enabled\": true,
    \"globalPath\": \"$agents_dir\",
    \"configFile\": \"$config_file\",
    \"autoComplete\": true,
    \"showInMenu\": true
  }
}${NC}"
        fi
    else
        # Create minimal settings.json
        echo -e "${YELLOW}Creating new settings.json...${NC}"
        cat > "$settings_file" << EOF
{
  "agents": {
    "enabled": true,
    "globalPath": "$agents_dir",
    "configFile": "$config_file",
    "autoComplete": true,
    "showInMenu": true
  }
}
EOF
        echo -e "${GREEN}Created settings.json with agent configuration${NC}"
    fi
    
    echo -e "\n${GREEN}Installation complete!${NC}"
    echo -e "${GREEN}Agents are now available GLOBALLY in ANY project!${NC}"
    echo -e "${CYAN}Use @agent-[name] to mention an agent (e.g., @agent-backend-services)${NC}"
    
    # Test agent availability
    echo -e "\n${YELLOW}Testing agent availability...${NC}"
    local test_agent="$agents_dir/backend-services-agent.md"
    if [ -f "$test_agent" ]; then
        echo -e "${GREEN}✓ Agent files accessible${NC}"
        echo -e "${GREEN}✓ Ready to use in any project!${NC}"
    else
        echo -e "${YELLOW}⚠ Warning: Could not verify agent files${NC}"
    fi
    
    # Set environment variable suggestion
    echo -e "\n${BLUE}Tip: To make this installation permanent, add to your ~/.bashrc:${NC}"
    echo -e "${CYAN}export CLAUDE_CODE_ROOT=\"$claude_root_path\"${NC}"
}

# Run main function
main

# Make script executable
chmod +x "$0" 2>/dev/null || true