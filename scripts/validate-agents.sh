#!/bin/bash
# Validate Claude Code Agents Installation

set -e

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
AGENTS_DIR="$HOME/.claude/agents"
EXPECTED_AGENTS=28

echo "Claude Code Agent System Validator"
echo "================================="
echo

# Check if agents directory exists
if [ ! -d "$AGENTS_DIR" ]; then
    echo -e "${RED}[✗]${NC} Agents directory not found at $AGENTS_DIR"
    echo "    Please run install.sh first"
    exit 1
fi

# Count agent files
AGENT_COUNT=$(ls -1 "$AGENTS_DIR"/*.md 2>/dev/null | wc -l)

echo "Checking agent installations..."
echo

# List all expected agents
EXPECTED_AGENT_NAMES=(
    "api-integration-specialist-agent"
    "backend-services-agent"
    "business-analyst-agent"
    "business-tech-alignment-agent"
    "ceo-strategy-agent"
    "database-architecture-agent"
    "development-prompt-agent"
    "devops-engineering-agent"
    "financial-analyst-agent"
    "frontend-architecture-agent"
    "frontend-mockup-agent"
    "integration-setup-agent"
    "master-orchestrator-agent"
    "middleware-specialist-agent"
    "mobile-development-agent"
    "performance-optimization-agent"
    "production-frontend-agent"
    "project-manager-agent"
    "prompt-engineer-agent"
    "quality-assurance-agent"
    "script-automation-agent"
    "security-architecture-agent"
    "technical-cto-agent"
    "technical-documentation-agent"
    "technical-specifications-agent"
    "testing-automation-agent"
    "ui-ux-design-agent"
    "usage-guide-agent"
)

# Check each expected agent
MISSING_COUNT=0
VALID_COUNT=0

for agent_name in "${EXPECTED_AGENT_NAMES[@]}"; do
    agent_file="$AGENTS_DIR/${agent_name}.md"
    
    if [ -f "$agent_file" ]; then
        # Validate agent file has required frontmatter
        if grep -q "^name:" "$agent_file" && grep -q "^description:" "$agent_file"; then
            echo -e "${GREEN}[✓]${NC} $agent_name"
            ((VALID_COUNT++))
        else
            echo -e "${YELLOW}[!]${NC} $agent_name (invalid format)"
        fi
    else
        echo -e "${RED}[✗]${NC} $agent_name (missing)"
        ((MISSING_COUNT++))
    fi
done

echo
echo "Validation Summary"
echo "=================="
echo "Expected agents: $EXPECTED_AGENTS"
echo "Valid agents:    $VALID_COUNT"
echo "Missing agents:  $MISSING_COUNT"
echo

# Check for extra agents
EXTRA_AGENTS=$(ls -1 "$AGENTS_DIR"/*.md 2>/dev/null | grep -v -F "$(printf '%s\n' "${EXPECTED_AGENT_NAMES[@]}" | sed 's/$/.md/')" | wc -l)
if [ "$EXTRA_AGENTS" -gt 0 ]; then
    echo -e "${YELLOW}[!]${NC} Found $EXTRA_AGENTS unexpected agent files"
fi

# Final status
if [ "$VALID_COUNT" -eq "$EXPECTED_AGENTS" ] && [ "$MISSING_COUNT" -eq 0 ]; then
    echo -e "${GREEN}[✓]${NC} All agents are properly installed!"
    exit 0
else
    echo -e "${RED}[✗]${NC} Agent validation failed"
    echo "    Run ./install.sh to fix missing agents"
    exit 1
fi