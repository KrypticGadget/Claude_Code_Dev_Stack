#!/bin/bash
# Simple Claude Code Installation Verifier for Linux
# Checks that all components are properly installed

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Claude Code Installation Verifier"
echo "================================="
echo ""

# Track results
TOTAL=0
PASSED=0
FAILED=0

# Check function
check() {
    local description="$1"
    local path="$2"
    local expected_count="$3"
    
    TOTAL=$((TOTAL + 1))
    
    if [ -d "$path" ]; then
        if [ -n "$expected_count" ]; then
            actual_count=$(find "$path" -type f -name "*.md" 2>/dev/null | wc -l)
            if [ "$actual_count" -eq "$expected_count" ]; then
                echo -e "${GREEN}✓${NC} $description ($actual_count files)"
                PASSED=$((PASSED + 1))
            else
                echo -e "${YELLOW}⚠${NC} $description (found $actual_count, expected $expected_count)"
                FAILED=$((FAILED + 1))
            fi
        else
            echo -e "${GREEN}✓${NC} $description"
            PASSED=$((PASSED + 1))
        fi
    elif [ -f "$path" ]; then
        echo -e "${GREEN}✓${NC} $description"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗${NC} $description (not found)"
        FAILED=$((FAILED + 1))
    fi
}

# Check components
echo "Checking installation..."
echo ""

check "Agents directory" "$HOME/.claude/agents" 28
check "Commands directory" "$HOME/.claude/commands" 18
check "Hooks directory" "$HOME/.claude/hooks" 0  # Python files, not .md
check "Settings file" "$HOME/.claude/settings.json" ""
check "MCP config" "$HOME/.claude/.mcp.json" ""

# Check Python for hooks
echo ""
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓${NC} Python3 installed (hooks will work)"
else
    echo -e "${YELLOW}⚠${NC} Python3 not found (hooks won't work)"
fi

# Summary
echo ""
echo "================================="
echo "Verification Results:"
echo "  Passed: $PASSED/$TOTAL"
if [ $FAILED -gt 0 ]; then
    echo -e "  ${YELLOW}Some components may need reinstallation${NC}"
else
    echo -e "  ${GREEN}All components installed successfully!${NC}"
fi
echo ""

# Return status
if [ $FAILED -eq 0 ]; then
    return 0 2>/dev/null || true
else
    return 1 2>/dev/null || true
fi