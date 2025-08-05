#!/bin/bash

# Claude Code Dev Stack v2.1 - macOS Installation Script
# This script installs the 28 AI agents, hooks system, and v2.1 features

set -e

echo -e "\033[36m🚀 Claude Code Dev Stack v2.1 - macOS Installation\033[0m"
echo -e "\033[33mInstalling 28 AI agents with @agent- routing, hooks, and MCP support...\033[0m"

# Check for required tools
if ! command -v curl &> /dev/null; then
    echo "Error: curl is required but not installed."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "Warning: python3 is required for hooks. Please install it via: brew install python3"
fi

# Set installation directory
CLAUDE_DIR="$HOME/.claude-code"
AGENTS_DIR="$CLAUDE_DIR/agents"
COMMANDS_DIR="$CLAUDE_DIR/commands"
HOOKS_DIR="$CLAUDE_DIR/.claude/hooks"
CONFIG_DIR="$CLAUDE_DIR/.claude/config"
STATE_DIR="$CLAUDE_DIR/.claude/state"
MCP_DIR="$CLAUDE_DIR/mcp-configs"

# GitHub repository URL
REPO_URL="https://github.com/KrypticGadget/Claude_Code_Dev_Stack"
RAW_URL="https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main"

# Create all directories
echo -e "\n\033[32m📁 Creating v2.1 directory structure...\033[0m"
mkdir -p "$CLAUDE_DIR" "$AGENTS_DIR" "$COMMANDS_DIR" "$HOOKS_DIR" "$CONFIG_DIR" "$STATE_DIR" "$MCP_DIR"

# Function to download with retry
download_with_retry() {
    local url=$1
    local output=$2
    local retries=3
    
    for i in $(seq 1 $retries); do
        if curl -sL "$url" -o "$output"; then
            return 0
        fi
        sleep 1
    done
    return 1
}

# Download agent configurations with @agent- support
echo -e "\n\033[32m📥 Downloading 28 agent configurations with v2.1 features...\033[0m"

agent_files=(
    "master-orchestrator-agent.md"
    "usage-guide-agent.md"
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
    "middleware-specialist-agent.md"
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
)

total_files=${#agent_files[@]}
current_file=0

for file in "${agent_files[@]}"; do
    ((current_file++))
    printf "\r  Downloading agents: %d/%d" "$current_file" "$total_files"
    download_with_retry "$RAW_URL/Config_Files/$file" "$AGENTS_DIR/$file" || echo "  ⚠️  Failed: $file"
done
echo -e "\n  ✓ Downloaded $total_files agent configurations"

# Download and install hooks
echo -e "\n\033[32m🔧 Installing v2.1 Hooks System...\033[0m"

hook_files=(
    "session_loader.py"
    "session_saver.py"
    "quality_gate.py"
    "planning_trigger.py"
    "agent_orchestrator.py"
    "agent_mention_parser.py"
    "model_tracker.py"
    "mcp_gateway.py"
)

for file in "${hook_files[@]}"; do
    echo "  Downloading $file..."
    if download_with_retry "$RAW_URL/.claude/hooks/$file" "$HOOKS_DIR/$file"; then
        chmod +x "$HOOKS_DIR/$file"
        echo -e "  \033[32m✓ Installed $file\033[0m"
    else
        echo -e "  \033[33m⚠️  Failed to download $file\033[0m"
    fi
done

# Download configuration files
echo -e "\n\033[32m⚙️  Installing v2.1 configuration files...\033[0m"

# Download coding standards
download_with_retry "$RAW_URL/.claude/config/coding_standards.json" "$CONFIG_DIR/coding_standards.json" && \
    echo -e "  \033[32m✓ Installed coding_standards.json\033[0m"

# Download agent models config
download_with_retry "$RAW_URL/.claude/config/agent_models.json" "$CONFIG_DIR/agent_models.json" && \
    echo -e "  \033[32m✓ Installed agent_models.json\033[0m"

# Download settings
download_with_retry "$RAW_URL/.claude/settings.json" "$CLAUDE_DIR/.claude/settings.json" && \
    echo -e "  \033[32m✓ Installed settings.json\033[0m"

# Download MCP configurations
echo -e "\n\033[32m🌐 Installing MCP configuration files...\033[0m"

mcp_files=(
    "tier1-universal.json"
    "active-mcps.json"
    "agent-bindings.json"
)

for file in "${mcp_files[@]}"; do
    if download_with_retry "$RAW_URL/mcp-configs/$file" "$MCP_DIR/$file"; then
        echo -e "  \033[32m✓ Installed $file\033[0m"
    else
        echo -e "  \033[33m⚠️  Failed to download $file\033[0m"
    fi
done

# Download slash commands
echo -e "\n\033[32m📋 Installing 18 slash commands...\033[0m"

slash_commands=(
    "new-project.md" "resume-project.md" "business-analysis.md"
    "technical-feasibility.md" "project-plan.md" "frontend-mockup.md"
    "backend-service.md" "database-design.md" "api-integration.md"
    "middleware-setup.md" "production-frontend.md" "documentation.md"
    "financial-model.md" "go-to-market.md" "requirements.md"
    "site-architecture.md" "tech-alignment.md" "prompt-enhance.md"
)

for cmd in "${slash_commands[@]}"; do
    download_with_retry "$RAW_URL/slash-commands/commands/$cmd" "$COMMANDS_DIR/$cmd" 2>/dev/null || true
done
echo "  ✓ Downloaded slash commands"

# Download master documentation
echo -e "\n\033[32m📚 Downloading v2.1 documentation...\033[0m"

docs=(
    "MASTER_PROMPTING_GUIDE.md"
    "HOOKS_IMPLEMENTATION.md"
    "MCP_INTEGRATION_GUIDE.md"
)

for doc in "${docs[@]}"; do
    if download_with_retry "$RAW_URL/docs/$doc" "$CLAUDE_DIR/$doc" 2>/dev/null; then
        echo -e "  \033[32m✓ Downloaded $doc\033[0m"
    fi
done

# Create v2.1 quick reference
echo -e "\n\033[32m📋 Creating v2.1 Quick Reference...\033[0m"
cat > "$CLAUDE_DIR/QUICK_REFERENCE_V2.1.txt" << 'EOF'
🚀 Claude Code Dev Stack v2.1 - Quick Reference (macOS)

✨ New v2.1 Features:
- @agent- deterministic routing (e.g., @agent-backend-services)
- Model selection: [opus] for complex, [haiku] for simple
- Automatic microcompact for extended sessions
- PDF reading capability
- Hooks execution layer
- MCP integration (Playwright, Obsidian, Brave Search)

🎯 Quick Start:
1. Use @agent- mentions: @agent-system-architect[opus] design a system
2. Cost optimization: @agent-testing-automation[haiku] for simple tests
3. Install MCPs: claude mcp add playwright npx @playwright/mcp@latest
4. PDF analysis: "Read requirements from spec.pdf"

📋 Available Agents (28 total):
- Orchestration: @agent-master-orchestrator[opus], @agent-usage-guide[opus]
- Business: @agent-business-analyst[opus], @agent-ceo-strategy[opus]
- Architecture: @agent-system-architect[opus], @agent-database-architecture[opus]
- Development: @agent-backend-services, @agent-frontend-architecture
- Testing: @agent-testing-automation[haiku], @agent-quality-assurance[haiku]
- Documentation: @agent-technical-documentation[haiku]

💰 Cost Optimization:
- Use [opus] only for complex reasoning (20% of tasks)
- Use [haiku] for routine tasks (30% of tasks)
- Default model for standard development (50% of tasks)
- Result: 40-60% cost reduction

🔧 Hooks Active:
- Session continuity (automatic state restoration)
- Quality gates (code standards enforcement)
- Planning triggers (requirements change detection)
- Agent routing (@agent- mention parsing)
- Model tracking (cost optimization monitoring)

🍎 macOS Specific:
- Ensure python3 is installed: brew install python3
- For better terminal colors: export TERM=xterm-256color
- Claude Code settings: ~/Library/Application Support/Claude/
EOF

# Create example usage file
cat > "$CLAUDE_DIR/EXAMPLES_V2.1.md" << 'EOF'
# Claude Code Dev Stack v2.1 - Example Usage (macOS)

## Basic @agent- Routing
@agent-backend-services create a REST API for user management
@agent-frontend-architecture[opus] design a complex dashboard
@agent-testing-automation[haiku] write unit tests

## Project Initialization with Model Optimization
/new-project "E-commerce Platform" @agent-master-orchestrator[opus] @agent-business-analyst[opus]

## Cost-Optimized Workflow
# Complex planning (Opus)
@agent-system-architect[opus] @agent-database-architecture[opus] design the system

# Implementation (Default)
@agent-backend-services @agent-frontend-architecture implement features

# Testing & Docs (Haiku)
@agent-testing-automation[haiku] @agent-technical-documentation[haiku] finish up

## PDF Integration
@agent-business-analyst[opus] analyze requirements from business-plan.pdf
@agent-technical-specifications review the API spec in api-docs.pdf

## MCP Usage
"Run browser tests with Playwright for the checkout flow"
"Document architectural decisions in Obsidian"
"Research competitor features using Brave Search"

## macOS Terminal Tips
# Add to ~/.zshrc for better experience:
alias ccds='cd ~/.claude-code'
alias cchelp='cat ~/.claude-code/QUICK_REFERENCE_V2.1.txt'
EOF

# Check for Claude Code installation
echo -e "\n\033[33m🔍 Checking Claude Code installation...\033[0m"
if command -v claude &> /dev/null; then
    echo -e "\033[32m✅ Claude Code is installed\033[0m"
else
    echo -e "\033[33m⚠️  Claude Code not found. Install it from: https://claude.ai/download\033[0m"
fi

echo -e "\n\033[32m✅ Claude Code Dev Stack v2.1 installation complete!\033[0m"
echo -e "\n\033[36m📍 Installed to: $CLAUDE_DIR\033[0m"
echo -e "\033[36m📄 Quick reference: $CLAUDE_DIR/QUICK_REFERENCE_V2.1.txt\033[0m"
echo -e "\033[36m📘 Examples: $CLAUDE_DIR/EXAMPLES_V2.1.md\033[0m"

echo -e "\n\033[33m🎯 Next Steps:\033[0m"
echo -e "\033[37m1. Install Tier 1 MCPs:\033[0m"
echo -e "\033[90m   claude mcp add playwright npx @playwright/mcp@latest\033[0m"
echo -e "\033[90m   claude mcp add obsidian\033[0m"
echo -e "\033[90m   claude mcp add brave-search\033[0m"
echo -e "\033[37m2. Copy .claude/settings.json to your Claude Code settings\033[0m"
echo -e "\033[37m3. Restart Claude Code to activate v2.1 features\033[0m"
echo -e "\033[37m4. Try: @agent-master-orchestrator[opus] plan a new project\033[0m"

# macOS specific tips
echo -e "\n\033[36m🍎 macOS Tips:\033[0m"
echo -e "\033[90m- Add alias to ~/.zshrc: alias cchelp='cat ~/.claude-code/QUICK_REFERENCE_V2.1.txt'\033[0m"
echo -e "\033[90m- For python3: brew install python3\033[0m"
echo -e "\033[90m- For better colors: export TERM=xterm-256color\033[0m"

echo -e "\n\033[32m🎉 Ready to use Claude Code Dev Stack v2.1!\033[0m"
echo -e "\033[37mTry: @agent-backend-services create a user authentication API\033[0m"