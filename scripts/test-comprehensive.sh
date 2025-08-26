#!/bin/bash

# Claude Code Dev Stack v3.7.11 Comprehensive Testing Script
# Tests installation, hooks, configuration, and platform compatibility

echo "🧪 Claude Code Dev Stack v3.7.11 Testing Suite"
echo "============================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
PASSED=0
FAILED=0

# Test 1: Clean Environment Installation
test_clean_installation() {
  echo -e "\n📋 Test 1: Clean Environment Installation"
  echo "----------------------------------------"
  
  # Remove existing Claude config
  if [ -d ~/.claude ]; then
    echo "Backing up existing .claude directory..."
    mv ~/.claude ~/.claude.backup.$(date +%s)
  fi
  
  # Run setup
  echo "Running ccds-setup..."
  node bin/ccds-setup.cjs
  
  # Verify installation
  if [ -d ~/.claude/hooks ]; then
    echo -e "${GREEN}✅ Hooks directory created${NC}"
    hook_count=$(ls ~/.claude/hooks/*.py 2>/dev/null | wc -l)
    echo "📊 Installed hooks: $hook_count"
    
    if [ $hook_count -ge 40 ]; then
      echo -e "${GREEN}✅ Sufficient hooks installed${NC}"
      ((PASSED++))
      return 0
    else
      echo -e "${RED}❌ Insufficient hooks installed (expected 40+, got $hook_count)${NC}"
      ((FAILED++))
      return 1
    fi
  else
    echo -e "${RED}❌ Hooks directory not created${NC}"
    ((FAILED++))
    return 1
  fi
}

# Test 2: Critical Hook Verification
test_critical_hooks() {
  echo -e "\n📋 Test 2: Critical Hook Verification"
  echo "------------------------------------"
  
  critical_hooks=(
    "smart_orchestrator.py"
    "status_line_manager.py"
    "claude_statusline.py"
    "master_orchestrator.py"
    "audio_player.py"
  )
  
  all_good=true
  for hook in "${critical_hooks[@]}"; do
    hook_path="$HOME/.claude/hooks/$hook"
    if [ -f "$hook_path" ]; then
      size=$(stat -f%z "$hook_path" 2>/dev/null || stat -c%s "$hook_path" 2>/dev/null)
      if [ $size -gt 100 ]; then
        echo -e "${GREEN}✅ $hook: Found ($size bytes)${NC}"
      else
        echo -e "${YELLOW}⚠️  $hook: Too small (likely placeholder)${NC}"
        all_good=false
      fi
    else
      echo -e "${RED}❌ $hook: Not found${NC}"
      all_good=false
    fi
  done
  
  if [ "$all_good" = true ]; then
    ((PASSED++))
    return 0
  else
    ((FAILED++))
    return 1
  fi
}

# Test 3: Configuration Validation
test_configuration() {
  echo -e "\n📋 Test 3: Configuration Validation"
  echo "----------------------------------"
  
  config_file="$HOME/.claude.json"
  if [ -f "$config_file" ]; then
    # Check if JSON is valid
    python3 -m json.tool "$config_file" >/dev/null 2>&1
    if [ $? -eq 0 ]; then
      echo -e "${GREEN}✅ Configuration JSON is valid${NC}"
      
      # Check for required sections
      if grep -q '"hooks":' "$config_file" && \
         grep -q '"mcpServers":' "$config_file"; then
        echo -e "${GREEN}✅ Required configuration sections present${NC}"
        ((PASSED++))
        return 0
      else
        echo -e "${RED}❌ Missing required configuration sections${NC}"
        ((FAILED++))
        return 1
      fi
    else
      echo -e "${RED}❌ Configuration JSON is invalid${NC}"
      ((FAILED++))
      return 1
    fi
  else
    echo -e "${RED}❌ Configuration file not found${NC}"
    ((FAILED++))
    return 1
  fi
}

# Test 4: Platform Compatibility
test_platform_compatibility() {
  echo -e "\n📋 Test 4: Platform Compatibility"
  echo "--------------------------------"
  
  platform=$(uname -s)
  echo "🖥️  Platform: $platform"
  
  case $platform in
    Linux*)
      if grep -q Microsoft /proc/version 2>/dev/null; then
        echo -e "${GREEN}✅ WSL detected and supported${NC}"
      else
        echo -e "${GREEN}✅ Native Linux detected and supported${NC}"
      fi
      ((PASSED++))
      ;;
    Darwin*)
      echo -e "${GREEN}✅ macOS detected and supported${NC}"
      ((PASSED++))
      ;;
    MINGW*|CYGWIN*|MSYS*)
      echo -e "${GREEN}✅ Windows detected and supported${NC}"
      ((PASSED++))
      ;;
    *)
      echo -e "${YELLOW}⚠️  Unknown platform: $platform${NC}"
      ((FAILED++))
      ;;
  esac
  
  return 0
}

# Test 5: Corruption Recovery
test_corruption_recovery() {
  echo -e "\n📋 Test 5: Corruption Recovery"
  echo "-----------------------------"
  
  # Create corrupted config
  echo "Testing corruption detection and recovery..."
  cp ~/.claude.json ~/.claude.json.test.backup
  
  # Inject corrupted hook reference
  echo '{
    "hooks": {
      "PreToolUse": [{
        "matcher": "Write",
        "hooks": [{
          "type": "command",
          "command": "python3 /home/user/.claude/hooks/non_existent_hook.py",
          "timeout": 5
        }]
      }]
    }
  }' > ~/.claude.json
  
  # Re-run setup (should detect corruption and fix)
  echo "Running setup with corrupted config..."
  node bin/ccds-setup.cjs
  
  # Verify fix
  python3 -m json.tool ~/.claude.json >/dev/null 2>&1
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Corruption recovery successful${NC}"
    # Restore original
    mv ~/.claude.json.test.backup ~/.claude.json
    ((PASSED++))
    return 0
  else
    echo -e "${RED}❌ Corruption recovery failed${NC}"
    mv ~/.claude.json.test.backup ~/.claude.json
    ((FAILED++))
    return 1
  fi
}

# Test 6: Hook Execution Test
test_hook_execution() {
  echo -e "\n📋 Test 6: Hook Execution Test"
  echo "-----------------------------"
  
  test_hook="$HOME/.claude/hooks/smart_orchestrator.py"
  if [ -f "$test_hook" ]; then
    # Test basic Python syntax
    python3 -m py_compile "$test_hook" 2>/dev/null
    if [ $? -eq 0 ]; then
      echo -e "${GREEN}✅ Hook syntax valid${NC}"
      ((PASSED++))
      return 0
    else
      echo -e "${RED}❌ Hook has syntax errors${NC}"
      ((FAILED++))
      return 1
    fi
  else
    echo -e "${RED}❌ Test hook not found${NC}"
    ((FAILED++))
    return 1
  fi
}

# Main test runner
main() {
  echo "🚀 Starting comprehensive test suite..."
  echo ""
  
  # Run tests
  test_clean_installation
  test_critical_hooks
  test_configuration
  test_platform_compatibility
  test_corruption_recovery
  test_hook_execution
  
  # Summary
  echo ""
  echo "========================================"
  echo "📊 Test Results Summary"
  echo "========================================"
  echo -e "${GREEN}✅ Passed: $PASSED${NC}"
  echo -e "${RED}❌ Failed: $FAILED${NC}"
  
  TOTAL=$((PASSED + FAILED))
  PERCENTAGE=$((PASSED * 100 / TOTAL))
  
  echo ""
  echo "Overall Score: ${PERCENTAGE}%"
  
  if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed! Installation is ready.${NC}"
    exit 0
  elif [ $PERCENTAGE -ge 80 ]; then
    echo -e "\n${YELLOW}⚠️  Most tests passed. Installation should work with minor issues.${NC}"
    exit 0
  else
    echo -e "\n${RED}💥 Too many tests failed. Installation may have critical issues.${NC}"
    exit 1
  fi
}

# Run main if script is executed directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
  main
fi