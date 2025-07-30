#!/bin/bash

# Claude Code Agent System - Update Script
# Updates all agents to the latest version

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/yourusername/claude-code-agent-system"
TEMP_DIR="/tmp/claude-agent-update-$$"

# Detect Claude Code agent directory
if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
    AGENT_DIR="$HOME/.config/claude/agents"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    AGENT_DIR="$APPDATA/claude/agents"
else
    echo -e "${RED}❌ Unsupported operating system${NC}"
    exit 1
fi

echo -e "${BLUE}🔄 Claude Code Agent System Updater${NC}"
echo -e "${BLUE}====================================${NC}"
echo

# Check if agent directory exists
if [ ! -d "$AGENT_DIR" ]; then
    echo -e "${RED}❌ Agent directory not found at: $AGENT_DIR${NC}"
    echo -e "${YELLOW}Please install Claude Code first: https://claude.ai/code${NC}"
    exit 1
fi

# Create backup
echo -e "${BLUE}📦 Creating backup of current agents...${NC}"
BACKUP_DIR="$HOME/.claude-agents-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r "$AGENT_DIR"/* "$BACKUP_DIR" 2>/dev/null || true
echo -e "${GREEN}✓ Backup created at: $BACKUP_DIR${NC}"

# Clone latest version
echo -e "${BLUE}📥 Downloading latest agent configurations...${NC}"
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"

# Clone or download the repository
if command -v git &> /dev/null; then
    git clone --depth 1 "$REPO_URL" . 2>/dev/null || {
        echo -e "${RED}❌ Failed to clone repository${NC}"
        echo -e "${YELLOW}Trying alternative download method...${NC}"
        curl -L "${REPO_URL}/archive/main.zip" -o agents.zip
        unzip -q agents.zip
        mv claude-code-agent-system-main/* .
    }
else
    # Fallback to curl/wget
    curl -L "${REPO_URL}/archive/main.zip" -o agents.zip || wget "${REPO_URL}/archive/main.zip" -O agents.zip
    unzip -q agents.zip
    mv claude-code-agent-system-main/* .
fi

# Check if agents directory exists in download
if [ ! -d "agents" ]; then
    echo -e "${RED}❌ Agents directory not found in repository${NC}"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Count agents
AGENT_COUNT=$(ls -1 agents/*.md 2>/dev/null | wc -l)
echo -e "${GREEN}✓ Found $AGENT_COUNT agents to update${NC}"

# Show changes
echo -e "${BLUE}📋 Checking for updates...${NC}"
UPDATED=0
NEW=0

for agent in agents/*.md; do
    agent_name=$(basename "$agent")
    if [ -f "$AGENT_DIR/$agent_name" ]; then
        if ! cmp -s "$agent" "$AGENT_DIR/$agent_name"; then
            echo -e "${YELLOW}  ↻ Updated: $agent_name${NC}"
            ((UPDATED++))
        fi
    else
        echo -e "${GREEN}  + New: $agent_name${NC}"
        ((NEW++))
    fi
done

UNCHANGED=$((AGENT_COUNT - UPDATED - NEW))
echo
echo -e "${BLUE}Summary: ${GREEN}$NEW new${NC}, ${YELLOW}$UPDATED updated${NC}, ${BLUE}$UNCHANGED unchanged${NC}"

# Confirm update
echo
read -p "$(echo -e "${YELLOW}Proceed with update? (y/N): ${NC}")" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Update cancelled${NC}"
    rm -rf "$TEMP_DIR"
    exit 0
fi

# Copy new agents
echo -e "${BLUE}📥 Installing updated agents...${NC}"
cp agents/*.md "$AGENT_DIR/"

# Update scripts if they exist
if [ -d "scripts" ] && [ -d "$HOME/.claude/scripts" ]; then
    echo -e "${BLUE}📥 Updating helper scripts...${NC}"
    cp scripts/*.sh "$HOME/.claude/scripts/" 2>/dev/null || true
    chmod +x "$HOME/.claude/scripts"/*.sh 2>/dev/null || true
fi

# Update documentation if exists
if [ -d "docs" ] && [ -d "$HOME/.claude/docs" ]; then
    echo -e "${BLUE}📥 Updating documentation...${NC}"
    cp -r docs/* "$HOME/.claude/docs/" 2>/dev/null || true
fi

# Cleanup
rm -rf "$TEMP_DIR"

# Verify update
echo -e "${BLUE}🔍 Verifying update...${NC}"
INSTALLED_COUNT=$(ls -1 "$AGENT_DIR"/*.md 2>/dev/null | wc -l)

if [ "$INSTALLED_COUNT" -ge "$AGENT_COUNT" ]; then
    echo -e "${GREEN}✅ Update successful! $INSTALLED_COUNT agents installed.${NC}"
    echo
    echo -e "${BLUE}What's next:${NC}"
    echo -e "  1. Test the updated agents in Claude Code"
    echo -e "  2. Check the changelog for new features"
    echo -e "  3. Review any breaking changes"
    echo
    echo -e "${YELLOW}Backup location: $BACKUP_DIR${NC}"
    echo -e "${YELLOW}To restore: cp $BACKUP_DIR/* $AGENT_DIR/${NC}"
else
    echo -e "${RED}❌ Update may have failed. Expected $AGENT_COUNT agents, found $INSTALLED_COUNT${NC}"
    echo -e "${YELLOW}You can restore from backup: cp $BACKUP_DIR/* $AGENT_DIR/${NC}"
    exit 1
fi

echo
echo -e "${GREEN}✨ Happy coding with your updated agents!${NC}"