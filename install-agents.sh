#!/bin/bash

# Claude Code Agents Installer for Ubuntu/WSL
# Downloads and installs 28 AI agents from the Config_Files directory

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
REPO_BASE="https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/Config_Files"
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

echo -e "${CYAN}Claude Code Agents Installer v1.0${NC}"
echo -e "${CYAN}=================================${NC}"

# Function to detect Claude Code installation path
find_claude_code_path() {
    local possible_paths=(
        "$HOME/.claude-code"
        "$HOME/.config/claude-code"
        "$HOME/.claude"
        "$HOME/.config/Claude"
        "/mnt/c/Users/$USER/.claude-code"  # WSL path
        "/mnt/c/Users/$USER/AppData/Roaming/Claude"  # WSL Windows path
    )
    
    for path in "${possible_paths[@]}"; do
        if [ -d "$path" ]; then
            echo "$path"
            return 0
        fi
    done
    
    # Default path if not found
    echo "$HOME/.claude-code"
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
    
    local claude_path=$(find_claude_code_path)
    local agents_dir="$claude_path/agents"
    
    echo -e "${GREEN}Detected Claude Code path: $claude_path${NC}"
    
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
    echo -e "${GREEN}Installation complete!${NC}"
}

# Run main function
main

# Make script executable
chmod +x "$0" 2>/dev/null || true