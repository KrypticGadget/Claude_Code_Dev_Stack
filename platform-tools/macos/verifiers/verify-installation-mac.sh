#!/bin/bash
# Claude Code Dev Stack v2.1 - Installation Verification (macOS)

echo -e "\n🔍 CLAUDE CODE DEV STACK VERIFICATION"
echo "====================================="

echo -e "\n📦 Agents (Subagents):"
project_agents=$(find .claude/agents -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
user_agents=$(find ~/.claude/agents -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
echo "   Project agents: $project_agents"
echo "   User agents: $user_agents"
total_agents=$((project_agents + user_agents))
if [ $total_agents -ge 28 ]; then
    echo -e "   Total: \033[0;32m$total_agents/28 expected\033[0m ✓"
else
    echo -e "   Total: \033[0;33m$total_agents/28 expected\033[0m"
fi

echo -e "\n💬 Slash Commands:"
project_commands=$(find .claude/commands -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
user_commands=$(find ~/.claude/commands -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
echo "   Project commands: $project_commands"
echo "   User commands: $user_commands"
total_commands=$((project_commands + user_commands))
if [ $total_commands -ge 18 ]; then
    echo -e "   Total: \033[0;32m$total_commands/18 expected\033[0m ✓"
else
    echo -e "   Total: \033[0;33m$total_commands/18 expected\033[0m"
fi

echo -e "\n🔌 MCPs:"
if command -v claude &> /dev/null; then
    mcp_count=$(claude mcp list 2>/dev/null | grep -E "playwright|obsidian|brave" | wc -l | tr -d ' ')
    if [ $mcp_count -eq 3 ]; then
        echo -e "   Found \033[0;32m$mcp_count/3 Tier 1 MCPs\033[0m ✓"
    else
        echo -e "   Found \033[0;31m$mcp_count/3 Tier 1 MCPs\033[0m"
    fi
else
    echo -e "   \033[0;31mClaude CLI not found\033[0m"
fi

echo -e "\n🪝 Hooks:"
if [[ -f ~/.claude/settings.json ]] || [[ -f .claude/settings.json ]]; then
    echo -e "   \033[0;32m✓ Settings files found\033[0m"
    if [[ -f ~/.claude/settings.json ]]; then
        echo "     • User settings: ~/.claude/settings.json"
    fi
    if [[ -f .claude/settings.json ]]; then
        echo "     • Project settings: .claude/settings.json"
    fi
else
    echo -e "   \033[0;33m✗ No settings files found - hooks not configured\033[0m"
fi

# macOS specific - check for Claude.app
if [[ -d "/Applications/Claude.app" ]]; then
    echo -e "\n🖥️  macOS Installation:"
    echo -e "   \033[0;32m✓ Claude.app found in Applications\033[0m"
fi

echo -e "\n✅ Installation Summary:"
if [ $total_agents -ge 28 ] && [ $total_commands -ge 18 ]; then
    echo -e "   \033[0;32mCore components installed successfully!\033[0m"
else
    echo -e "   \033[0;33mSome components may be missing\033[0m"
fi

echo -e "\n📍 To see everything in Claude Code:"
echo "   /agents  - View all subagents"
echo "   /help    - View all slash commands"
echo "   /mcp     - View MCP connections"
echo "   /hooks   - View hook configurations"
echo ""