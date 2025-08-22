#!/bin/bash
# Claude Code Dev Stack - Enhanced Installation Verifier v2.1 for Linux
# Verifies complete integrated system with hooks, audio, and all components

cat << 'EOF'
╔════════════════════════════════════════════════════════════════╗
║      Claude Code Dev Stack - Installation Verifier v2.1        ║
║        Checking Enhanced Hooks & Complete Integration          ║
╚════════════════════════════════════════════════════════════════╝
EOF

# Define paths
CLAUDE_DIR="$HOME/.claude"
AGENTS_PATH="$CLAUDE_DIR/agents"
COMMANDS_PATH="$CLAUDE_DIR/commands"
HOOKS_PATH="$CLAUDE_DIR/hooks"
AUDIO_PATH="$CLAUDE_DIR/audio"
LOGS_PATH="$CLAUDE_DIR/logs"
STATE_PATH="$CLAUDE_DIR/state"
SETTINGS_PATH="$CLAUDE_DIR/settings.json"
MCP_PATH="$CLAUDE_DIR/.mcp.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# Initialize counters
TESTS_TOTAL=0
TESTS_PASSED=0
declare -A COMPONENTS

echo -e "\n${YELLOW}🔍 Checking installation...${NC}"

# Check agents
echo -e "\n${CYAN}📚 Agents:${NC}"
((TESTS_TOTAL++))
if [ -d "$AGENTS_PATH" ]; then
    AGENT_COUNT=$(find "$AGENTS_PATH" -name "*.md" -type f 2>/dev/null | wc -l)
    if [ "$AGENT_COUNT" -ge 28 ]; then
        echo -e "  ${GREEN}✓ All 28 agents found${NC}"
        ((TESTS_PASSED++))
        COMPONENTS["Agents"]="true"
    elif [ "$AGENT_COUNT" -gt 0 ]; then
        echo -e "  ${YELLOW}⚠ Found $AGENT_COUNT agents (expected 28)${NC}"
        COMPONENTS["Agents"]="partial"
    else
        echo -e "  ${RED}✗ No agents found${NC}"
        COMPONENTS["Agents"]="false"
    fi
else
    echo -e "  ${RED}✗ Agents directory missing${NC}"
    COMPONENTS["Agents"]="false"
fi

# Check commands
echo -e "\n${CYAN}⚡ Slash Commands:${NC}"
((TESTS_TOTAL++))
if [ -d "$COMMANDS_PATH" ]; then
    CMD_COUNT=$(find "$COMMANDS_PATH" -name "*.md" -type f 2>/dev/null | wc -l)
    if [ "$CMD_COUNT" -ge 18 ]; then
        echo -e "  ${GREEN}✓ All 18 commands found${NC}"
        ((TESTS_PASSED++))
        COMPONENTS["Commands"]="true"
    elif [ "$CMD_COUNT" -gt 0 ]; then
        echo -e "  ${YELLOW}⚠ Found $CMD_COUNT commands (expected 18)${NC}"
        COMPONENTS["Commands"]="partial"
    else
        echo -e "  ${RED}✗ No commands found${NC}"
        COMPONENTS["Commands"]="false"
    fi
else
    echo -e "  ${RED}✗ Commands directory missing${NC}"
    COMPONENTS["Commands"]="false"
fi

# Check enhanced hooks
echo -e "\n${CYAN}🪝 Enhanced Hooks:${NC}"
REQUIRED_HOOKS=(
    "agent_orchestrator_integrated.py"
    "slash_command_router.py"
    "mcp_gateway_enhanced.py"
    "mcp_initializer.py"
    "audio_player.py"
    "session_loader.py"
    "session_saver.py"
    "model_tracker.py"
    "quality_gate.py"
)

FOUND_HOOKS=0
MISSING_HOOKS=()

for HOOK in "${REQUIRED_HOOKS[@]}"; do
    ((TESTS_TOTAL++))
    if [ -f "$HOOKS_PATH/$HOOK" ]; then
        ((FOUND_HOOKS++))
        ((TESTS_PASSED++))
    else
        MISSING_HOOKS+=("$HOOK")
    fi
done

if [ "$FOUND_HOOKS" -eq "${#REQUIRED_HOOKS[@]}" ]; then
    echo -e "  ${GREEN}✓ All critical hooks installed ($FOUND_HOOKS/${#REQUIRED_HOOKS[@]})${NC}"
    COMPONENTS["Hooks"]="true"
elif [ "$FOUND_HOOKS" -gt 0 ]; then
    echo -e "  ${YELLOW}⚠ Partial hooks ($FOUND_HOOKS/${#REQUIRED_HOOKS[@]})${NC}"
    if [ "${#MISSING_HOOKS[@]}" -gt 0 ]; then
        echo -e "    ${GRAY}Missing: ${MISSING_HOOKS[*]}${NC}"
    fi
    COMPONENTS["Hooks"]="partial"
else
    echo -e "  ${RED}✗ No enhanced hooks found${NC}"
    COMPONENTS["Hooks"]="false"
fi

# Check audio
echo -e "\n${CYAN}🎵 Audio System:${NC}"
((TESTS_TOTAL++))
if [ -d "$AUDIO_PATH" ]; then
    AUDIO_COUNT=$(find "$AUDIO_PATH" -name "*.mp3" -type f 2>/dev/null | wc -l)
    if [ "$AUDIO_COUNT" -ge 5 ]; then
        echo -e "  ${GREEN}✓ All audio files present ($AUDIO_COUNT files)${NC}"
        ((TESTS_PASSED++))
        COMPONENTS["Audio"]="true"
    elif [ "$AUDIO_COUNT" -gt 0 ]; then
        echo -e "  ${YELLOW}⚠ Found $AUDIO_COUNT audio files (expected 5)${NC}"
        COMPONENTS["Audio"]="partial"
    else
        echo -e "  ${RED}✗ No audio files found${NC}"
        COMPONENTS["Audio"]="false"
    fi
else
    echo -e "  ${RED}✗ Audio directory missing${NC}"
    COMPONENTS["Audio"]="false"
fi

# Check settings
echo -e "\n${CYAN}⚙️ Configuration:${NC}"
((TESTS_TOTAL++))
if [ -f "$SETTINGS_PATH" ]; then
    if command -v jq &> /dev/null; then
        if jq -e '.hooks' "$SETTINGS_PATH" &> /dev/null; then
            echo -e "  ${GREEN}✓ Integrated settings.json with hooks${NC}"
            ((TESTS_PASSED++))
            COMPONENTS["Settings"]="true"
        else
            echo -e "  ${YELLOW}⚠ settings.json exists but no hooks configured${NC}"
            COMPONENTS["Settings"]="partial"
        fi
    else
        # Fallback: check if file contains "hooks" string
        if grep -q '"hooks"' "$SETTINGS_PATH"; then
            echo -e "  ${GREEN}✓ Integrated settings.json with hooks${NC}"
            ((TESTS_PASSED++))
            COMPONENTS["Settings"]="true"
        else
            echo -e "  ${YELLOW}⚠ settings.json exists but no hooks configured${NC}"
            COMPONENTS["Settings"]="partial"
        fi
    fi
else
    echo -e "  ${RED}✗ settings.json missing${NC}"
    COMPONENTS["Settings"]="false"
fi

# Check MCP configuration
echo -e "\n${CYAN}🔌 MCP Services:${NC}"
((TESTS_TOTAL++))
if [ -f "$MCP_PATH" ]; then
    echo -e "  ${GREEN}✓ MCP configuration found${NC}"
    ((TESTS_PASSED++))
    COMPONENTS["MCP"]="true"
else
    echo -e "  ${YELLOW}⚠ MCP not configured (optional)${NC}"
    COMPONENTS["MCP"]="optional"
fi

# Check Python
echo -e "\n${CYAN}🐍 Python Runtime:${NC}"
((TESTS_TOTAL++))
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "  ${GREEN}✓ Python installed: $PYTHON_VERSION${NC}"
    ((TESTS_PASSED++))
    COMPONENTS["Python"]="true"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1)
    if [[ $PYTHON_VERSION == *"Python 3"* ]]; then
        echo -e "  ${GREEN}✓ Python installed: $PYTHON_VERSION${NC}"
        ((TESTS_PASSED++))
        COMPONENTS["Python"]="true"
        PYTHON_CMD="python"
    else
        echo -e "  ${RED}✗ Python 2 found - Python 3 required${NC}"
        COMPONENTS["Python"]="false"
    fi
else
    echo -e "  ${RED}✗ Python not found (required for hooks)${NC}"
    COMPONENTS["Python"]="false"
fi

# Quick functional test
echo -e "\n${CYAN}🧪 Quick Functional Test:${NC}"
if [ "${COMPONENTS[Hooks]}" = "true" ] && [ "${COMPONENTS[Python]}" = "true" ]; then
    ((TESTS_TOTAL++))
    echo -n "  Testing slash command router..."
    TEST_DATA='{"prompt":"/new-project test"}'
    if echo "$TEST_DATA" | $PYTHON_CMD "$HOOKS_PATH/slash_command_router.py" &> /dev/null; then
        echo -e " ${GREEN}✓${NC}"
        ((TESTS_PASSED++))
    else
        echo -e " ${RED}✗${NC}"
    fi
fi

# Summary
echo -e "\n${CYAN}════════════════════════════════════════════════════════════${NC}"
echo -e "  ${WHITE}INSTALLATION SUMMARY${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"

# Calculate percentage
if [ "$TESTS_TOTAL" -gt 0 ]; then
    PERCENTAGE=$(( (TESTS_PASSED * 100) / TESTS_TOTAL ))
else
    PERCENTAGE=0
fi

echo -e "\n${CYAN}📊 Test Results:${NC}"
if [ "$PERCENTAGE" -ge 90 ]; then
    COLOR=$GREEN
elif [ "$PERCENTAGE" -ge 70 ]; then
    COLOR=$YELLOW
else
    COLOR=$RED
fi
echo -e "  ${COLOR}Tests Passed: $TESTS_PASSED/$TESTS_TOTAL ($PERCENTAGE%)${NC}"

echo -e "\n${CYAN}📦 Component Status:${NC}"
for COMP in "${!COMPONENTS[@]}"; do
    STATUS="${COMPONENTS[$COMP]}"
    case "$STATUS" in
        "true")
            echo -e "  ${GREEN}✓ $COMP${NC}"
            ;;
        "partial")
            echo -e "  ${YELLOW}⚠ $COMP${NC}"
            ;;
        "optional")
            echo -e "  ${GRAY}• $COMP${NC}"
            ;;
        *)
            echo -e "  ${RED}✗ $COMP${NC}"
            ;;
    esac
done

# Recommendations
echo -e "\n${CYAN}💡 Recommendations:${NC}"
if [ "$PERCENTAGE" -eq 100 ]; then
    echo -e "  ${GREEN}✅ System fully operational!${NC}"
    echo -e "     ${CYAN}Your Claude Code Dev Stack is ready for 6-9x faster development!${NC}"
elif [ "$PERCENTAGE" -ge 80 ]; then
    echo -e "  ${YELLOW}⚠ System mostly operational with minor issues${NC}"
    if [ "${COMPONENTS[Python]}" = "false" ]; then
        echo -e "     ${YELLOW}• Install Python 3 from your package manager${NC}"
    fi
    if [ "${COMPONENTS[Audio]}" != "true" ]; then
        echo -e "     ${YELLOW}• Run install-hooks.sh to add audio support${NC}"
    fi
else
    echo -e "  ${RED}❌ System needs configuration${NC}"
    echo -e "     ${YELLOW}Run the following to complete setup:${NC}"
    echo -e "     ${CYAN}./platform-tools/linux/installers/install-all.sh${NC}"
fi

# Return status code
if [ "$PERCENTAGE" -eq 100 ]; then
    exit 0  # Fully installed
elif [ "$PERCENTAGE" -ge 70 ]; then
    exit 1  # Partially installed
else
    exit 2  # Not properly installed
fi