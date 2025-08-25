#!/bin/bash
#
# VM Testing Script for Claude Code Dev Stack
# Tests all components in Linux/Docker environments
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}    Claude Code Dev Stack - VM Environment Test Suite${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"

# Function to print test results
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        FAILED_TESTS+=("$2")
    fi
}

# Array to track failed tests
FAILED_TESTS=()

# 1. Platform Detection
echo -e "${YELLOW}🔍 Platform Detection...${NC}"
echo "Platform: $(uname -s)"
echo "Kernel: $(uname -r)"
echo "Architecture: $(uname -m)"
if [ -f /.dockerenv ]; then
    echo "Environment: Docker Container"
elif grep -q microsoft /proc/version 2>/dev/null; then
    echo "Environment: WSL"
else
    echo "Environment: Native Linux/VM"
fi
echo ""

# 2. Python Installation Check
echo -e "${YELLOW}🐍 Python Installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    print_result 0 "Python3 found: $(python3 --version)"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    print_result 0 "Python found: $(python --version)"
else
    print_result 1 "Python not found"
    PYTHON_CMD="python3"
fi

# Check Python packages
echo -e "\nPython packages:"
for package in requests pyyaml psutil colorama click; do
    if $PYTHON_CMD -c "import $package" 2>/dev/null; then
        print_result 0 "$package installed"
    else
        print_result 1 "$package not installed"
    fi
done
echo ""

# 3. Claude Directory Structure
echo -e "${YELLOW}📁 Claude Directory Structure...${NC}"
CLAUDE_DIR="$HOME/.claude"

if [ -d "$CLAUDE_DIR" ]; then
    print_result 0 "Claude directory exists: $CLAUDE_DIR"
    
    # Check subdirectories
    for dir in hooks state todos shell-snapshots; do
        if [ -d "$CLAUDE_DIR/$dir" ]; then
            count=$(find "$CLAUDE_DIR/$dir" -type f 2>/dev/null | wc -l)
            print_result 0 "$dir/ exists ($count files)"
        else
            print_result 1 "$dir/ missing"
        fi
    done
else
    print_result 1 "Claude directory missing"
    mkdir -p "$CLAUDE_DIR"
fi
echo ""

# 4. Settings.json Analysis
echo -e "${YELLOW}⚙️ Settings.json Configuration...${NC}"
SETTINGS_FILE="$CLAUDE_DIR/settings.json"

if [ -f "$SETTINGS_FILE" ]; then
    print_result 0 "settings.json exists"
    
    # Check for Windows paths
    if grep -q "C:" "$SETTINGS_FILE" || grep -q "C\\\\" "$SETTINGS_FILE"; then
        print_result 1 "Windows paths detected in settings.json!"
        echo -e "${RED}   This will cause hooks to fail in Linux/VM${NC}"
    else
        print_result 0 "No Windows paths detected"
    fi
    
    # Check statusLine configuration
    if grep -q "statusLine" "$SETTINGS_FILE"; then
        statusline_cmd=$(grep -A 2 "statusLine" "$SETTINGS_FILE" | grep "command" | head -1)
        echo "   Statusline command: $statusline_cmd"
    else
        print_result 1 "No statusLine configuration found"
    fi
    
    # Count configured hooks
    hook_count=$(grep -o "\"hooks\":" "$SETTINGS_FILE" | wc -l)
    if [ $hook_count -gt 0 ]; then
        print_result 0 "Hooks configured in settings"
    else
        print_result 1 "No hooks configured"
    fi
else
    print_result 1 "settings.json not found"
fi
echo ""

# 5. Hook Files Check
echo -e "${YELLOW}🪝 Hook Files...${NC}"
HOOKS_DIR="$CLAUDE_DIR/hooks"

if [ -d "$HOOKS_DIR" ]; then
    # List all Python hooks
    hook_files=$(find "$HOOKS_DIR" -name "*.py" -type f 2>/dev/null)
    hook_count=$(echo "$hook_files" | grep -c "\.py" || echo 0)
    
    if [ $hook_count -gt 0 ]; then
        print_result 0 "Found $hook_count hook files"
        
        # Test critical hooks
        for hook in claude_statusline.py master_orchestrator.py smart_orchestrator.py; do
            if [ -f "$HOOKS_DIR/$hook" ]; then
                # Test if hook is executable
                if echo '{"test": true}' | $PYTHON_CMD "$HOOKS_DIR/$hook" &>/dev/null; then
                    print_result 0 "$hook is working"
                else
                    print_result 1 "$hook failed to execute"
                fi
            else
                print_result 1 "$hook not found"
            fi
        done
    else
        print_result 1 "No hook files found"
    fi
else
    print_result 1 "Hooks directory not found"
fi
echo ""

# 6. Statusline Test
echo -e "${YELLOW}📊 Statusline Test...${NC}"
STATUSLINE_SCRIPT="$HOOKS_DIR/claude_statusline.py"

if [ -f "$STATUSLINE_SCRIPT" ]; then
    # Test statusline with sample input
    test_input='{"model":{"display_name":"Test Model"},"conversation":{"uuid":"test-123"}}'
    
    echo "Testing statusline with: $test_input"
    if output=$(echo "$test_input" | $PYTHON_CMD "$STATUSLINE_SCRIPT" 2>&1); then
        print_result 0 "Statusline executed successfully"
        echo "   Output: $output"
    else
        print_result 1 "Statusline execution failed"
        echo "   Error: $output"
    fi
else
    print_result 1 "Statusline script not found"
fi
echo ""

# 7. NPM Package Check
echo -e "${YELLOW}📦 NPM Package Installation...${NC}"
if command -v npm &> /dev/null; then
    print_result 0 "npm found: $(npm --version)"
    
    # Check if claude-code-dev-stack is installed
    if npm list -g claude-code-dev-stack &>/dev/null; then
        version=$(npm list -g claude-code-dev-stack | grep claude-code-dev-stack | head -1)
        print_result 0 "claude-code-dev-stack installed: $version"
    else
        print_result 1 "claude-code-dev-stack not installed globally"
    fi
else
    print_result 1 "npm not found"
fi
echo ""

# 8. Fix Attempt
if [ ${#FAILED_TESTS[@]} -gt 0 ]; then
    echo -e "${YELLOW}🔧 Attempting to fix issues...${NC}"
    
    # Try to run platform detection with fix
    if [ -f "$(npm root -g)/claude-code-dev-stack/bin/detect-platform.js" ]; then
        echo "Running platform detection fix..."
        node "$(npm root -g)/claude-code-dev-stack/bin/detect-platform.js" --fix
    fi
    
    # Try to run hook installer
    if [ -f "$(npm root -g)/claude-code-dev-stack/bin/install-hooks.js" ]; then
        echo "Running hook installer..."
        node "$(npm root -g)/claude-code-dev-stack/bin/install-hooks.js"
    fi
fi

# 9. Summary
echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}                          TEST SUMMARY${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

if [ ${#FAILED_TESTS[@]} -eq 0 ]; then
    echo -e "${GREEN}✨ All tests passed! Your VM environment is properly configured.${NC}"
else
    echo -e "${RED}⚠️  ${#FAILED_TESTS[@]} test(s) failed:${NC}"
    for test in "${FAILED_TESTS[@]}"; do
        echo -e "${RED}   - $test${NC}"
    done
    echo -e "\n${YELLOW}To fix these issues, run:${NC}"
    echo "  npm install -g claude-code-dev-stack@latest"
    echo "  ccds-setup"
    echo "  node $(npm root -g)/claude-code-dev-stack/bin/detect-platform.js --fix"
fi

echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"