#!/bin/bash
# List all available Claude Code agents with descriptions

set -e

# Color codes
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
AGENTS_DIR="$HOME/.claude/agents"

echo "Claude Code Agent System - Available Agents"
echo "=========================================="
echo

# Check if agents directory exists
if [ ! -d "$AGENTS_DIR" ]; then
    echo "Agents not found. Run install.sh first."
    exit 1
fi

# Categories and their agents
declare -A CATEGORIES
CATEGORIES["Business Strategy & Analysis"]="business-analyst-agent technical-cto-agent ceo-strategy-agent financial-analyst-agent"
CATEGORIES["Project Management & Planning"]="project-manager-agent technical-specifications-agent business-tech-alignment-agent"
CATEGORIES["Architecture & Documentation"]="technical-documentation-agent api-integration-specialist-agent frontend-architecture-agent database-architecture-agent middleware-specialist-agent"
CATEGORIES["Frontend Development"]="frontend-mockup-agent production-frontend-agent ui-ux-design-agent"
CATEGORIES["Backend Development"]="backend-services-agent"
CATEGORIES["Mobile Development"]="mobile-development-agent"
CATEGORIES["DevOps & Infrastructure"]="devops-engineering-agent integration-setup-agent script-automation-agent"
CATEGORIES["Quality & Security"]="quality-assurance-agent testing-automation-agent security-architecture-agent performance-optimization-agent"
CATEGORIES["Orchestration & Support"]="master-orchestrator-agent development-prompt-agent prompt-engineer-agent usage-guide-agent"

# Function to extract description from agent file
get_description() {
    local agent_file="$1"
    if [ -f "$agent_file" ]; then
        # Extract description, handling multi-line descriptions
        awk '/^description:/ {
            sub(/^description: */, "");
            desc = $0;
            while (getline > 0 && match($0, /^[[:space:]]+/)) {
                sub(/^[[:space:]]+/, " ");
                desc = desc $0;
            }
            print desc;
            exit;
        }' "$agent_file" | head -c 80
    else
        echo "Agent file not found"
    fi
}

# Display agents by category
for category in "Business Strategy & Analysis" "Project Management & Planning" "Architecture & Documentation" "Frontend Development" "Backend Development" "Mobile Development" "DevOps & Infrastructure" "Quality & Security" "Orchestration & Support"; do
    echo -e "${BLUE}$category${NC}"
    echo "$(echo "$category" | sed 's/./─/g')"
    
    # Get agents for this category
    agents="${CATEGORIES[$category]}"
    
    # Display each agent
    for agent in $agents; do
        agent_file="$AGENTS_DIR/${agent}.md"
        if [ -f "$agent_file" ]; then
            description=$(get_description "$agent_file")
            printf "  ${GREEN}%-35s${NC} %s\n" "$agent" "$description..."
        fi
    done
    echo
done

# Show usage instructions
echo "Usage Instructions"
echo "=================="
echo
echo "To use any agent, type in Claude Code:"
echo -e "${YELLOW}> Use the [agent-name] agent to [your task]${NC}"
echo
echo "Examples:"
echo "  > Use the master-orchestrator agent to begin new project: \"E-commerce platform\""
echo "  > Use the business-analyst agent to evaluate ROI for my SaaS idea"
echo "  > Use the frontend-mockup agent to create a landing page prototype"
echo
echo "For detailed help, see: ~/.claude/docs/QUICK_START.md"