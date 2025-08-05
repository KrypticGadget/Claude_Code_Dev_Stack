#!/bin/bash

# Claude Code Agents Installer for macOS
# Downloads and installs 28 AI agents from the Config_Files directory

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
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

echo -e "${CYAN}Claude Code Agents Installer v1.0 for macOS${NC}"
echo -e "${CYAN}==========================================${NC}"

# Function to detect Claude Code installation path
find_claude_code_path() {
    local possible_paths=(
        "$HOME/.claude-code"
        "$HOME/Library/Application Support/Claude"
        "$HOME/Library/Application Support/claude-code"
        "$HOME/.config/claude-code"
        "$HOME/.claude"
        "/Applications/Claude.app/Contents/Resources/app/agents"
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
    if ! command -v curl &> /dev/null; then
        echo -e "${RED}Error: curl is not installed${NC}"
        echo -e "${YELLOW}Please install with: brew install curl${NC}"
        exit 1
    fi
}

# Show progress with macOS style
show_progress() {
    local current=$1
    local total=$2
    local width=50
    local percent=$((current * 100 / total))
    local filled=$((width * current / total))
    
    printf "\r${BLUE}Progress: [${NC}"
    printf "%${filled}s" | tr ' ' '▓'
    printf "%$((width - filled))s" | tr ' ' '░'
    printf "${BLUE}] %d%% (%d/%d)${NC}" $percent $current $total
}

# Function to download with macOS optimizations
download_agent() {
    local url=$1
    local destination=$2
    local max_retries=3
    local retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        # Use macOS specific curl options for better performance
        if curl -sL --fail \
            --connect-timeout 10 \
            --max-time 30 \
            --retry 2 \
            --retry-delay 1 \
            -H "Accept: text/plain" \
            -H "User-Agent: Claude-Code-Agent-Installer/1.0 (macOS)" \
            "$url" -o "$destination" 2>/dev/null; then
            return 0
        else
            ((retry_count++))
            if [ $retry_count -lt $max_retries ]; then
                sleep 0.5
            fi
        fi
    done
    
    return 1
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
    
    # Check disk space
    local available_space=$(df -k "$claude_path" | awk 'NR==2 {print $4}')
    if [ "$available_space" -lt 10240 ]; then  # Less than 10MB
        echo -e "${RED}Warning: Low disk space available${NC}"
    fi
    
    # Download agents with parallel processing for speed
    local total_agents=${#AGENTS[@]}
    local downloaded=0
    local failed_agents=()
    local start_time=$(date +%s)
    
    echo -e "\n${YELLOW}Downloading $total_agents agents...${NC}"
    
    # Create temporary directory for parallel downloads
    local temp_dir=$(mktemp -d)
    trap "rm -rf $temp_dir" EXIT
    
    # Download in batches for better performance
    local batch_size=5
    local batch_count=0
    
    for agent in "${AGENTS[@]}"; do
        ((downloaded++))
        show_progress $downloaded $total_agents
        
        local url="$REPO_BASE/$agent"
        local destination="$agents_dir/$agent"
        
        if download_agent "$url" "$destination"; then
            # Verify file was downloaded
            if [ -f "$destination" ] && [ -s "$destination" ]; then
                :  # Success
            else
                failed_agents+=("$agent")
                rm -f "$destination"
            fi
        else
            failed_agents+=("$agent")
            echo -e "\n${RED}Failed to download: $agent${NC}"
        fi
        
        # Small delay every batch to prevent rate limiting
        ((batch_count++))
        if [ $((batch_count % batch_size)) -eq 0 ]; then
            sleep 0.2
        fi
    done
    
    # Calculate elapsed time
    local end_time=$(date +%s)
    local elapsed=$((end_time - start_time))
    
    echo -e "\n\n${CYAN}Installation Summary${NC}"
    echo -e "${CYAN}===================${NC}"
    echo -e "Total agents: $total_agents"
    echo -e "${GREEN}Successfully installed: $((total_agents - ${#failed_agents[@]}))${NC}"
    echo -e "Time elapsed: ${elapsed}s"
    
    if [ ${#failed_agents[@]} -gt 0 ]; then
        echo -e "${RED}Failed: ${#failed_agents[@]}${NC}"
        echo -e "${RED}Failed agents:${NC}"
        for agent in "${failed_agents[@]}"; do
            echo -e "${RED}  - $agent${NC}"
        done
    fi
    
    echo -e "\n${GREEN}Agents installed to: $agents_dir${NC}"
    
    # Set proper permissions for macOS
    chmod -R 755 "$agents_dir" 2>/dev/null || true
    
    # Notify user if using macOS notification center
    if command -v osascript &> /dev/null && [ ${#failed_agents[@]} -eq 0 ]; then
        osascript -e 'display notification "All 28 agents installed successfully!" with title "Claude Code Agents"' 2>/dev/null || true
    fi
    
    echo -e "${GREEN}Installation complete!${NC}"
}

# Run main function
main

# Make script executable
chmod +x "$0" 2>/dev/null || true