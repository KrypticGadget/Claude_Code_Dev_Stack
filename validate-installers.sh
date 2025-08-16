#!/bin/bash
# Quick validation script for Claude Code Dev Stack v3.0 installers
# Tests core functionality without full execution

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0

test_result() {
    local test_name="$1"
    local success="$2"
    local message="$3"
    
    if [[ "$success" == "true" ]]; then
        echo -e "${GREEN}✅ PASS${NC}: $test_name"
        [[ -n "$message" ]] && echo -e "   ${BLUE}$message${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC}: $test_name"
        [[ -n "$message" ]] && echo -e "   ${YELLOW}$message${NC}"
        ((FAILED++))
    fi
}

echo "🧪 Validating Claude Code Dev Stack v3.0 Installers"
echo "=================================================="
echo ""

# Test 1: File existence
echo "📁 Testing file existence..."
test_result "PowerShell installer" "$(test -f install.ps1 && echo true || echo false)" "install.ps1 found"
test_result "Bash installer" "$(test -f install.sh && echo true || echo false)" "install.sh found"  
test_result "Documentation" "$(test -f INSTALLER_README.md && echo true || echo false)" "INSTALLER_README.md found"
test_result "Test suite" "$(test -f test-installer.ps1 && echo true || echo false)" "test-installer.ps1 found"

echo ""

# Test 2: File permissions
echo "🔒 Testing file permissions..."
test_result "Bash installer executable" "$(test -x install.sh && echo true || echo false)" "install.sh is executable"
test_result "PowerShell installer readable" "$(test -r install.ps1 && echo true || echo false)" "install.ps1 is readable"

echo ""

# Test 3: Syntax validation
echo "📝 Testing syntax..."
if command -v bash >/dev/null 2>&1; then
    if bash -n install.sh >/dev/null 2>&1; then
        test_result "Bash syntax check" "true" "No syntax errors in install.sh"
    else
        test_result "Bash syntax check" "false" "Syntax errors found in install.sh"
    fi
else
    test_result "Bash syntax check" "false" "Bash not available for testing"
fi

echo ""

# Test 4: Required functions
echo "🔧 Testing function definitions..."

# Check Bash functions
BASH_FUNCTIONS=(
    "detect_os"
    "install_dependencies" 
    "clone_repository"
    "setup_python_environment"
    "setup_nodejs_environment"
    "configure_services"
    "validate_installation"
    "create_launcher_scripts"
)

for func in "${BASH_FUNCTIONS[@]}"; do
    if grep -q "${func}()" install.sh; then
        test_result "Bash function: $func" "true" "Function defined"
    else
        test_result "Bash function: $func" "false" "Function missing"
    fi
done

# Check PowerShell functions  
PS_FUNCTIONS=(
    "Test-Dependencies"
    "Install-ClaudeStack"
    "Invoke-ValidationTests"
    "Create-LauncherScripts"
    "Show-InstallationSummary"
)

for func in "${PS_FUNCTIONS[@]}"; do
    if grep -q "function $func" install.ps1; then
        test_result "PowerShell function: $func" "true" "Function defined"
    else
        test_result "PowerShell function: $func" "false" "Function missing"
    fi
done

echo ""

# Test 5: Security features
echo "🔒 Testing security features..."

# Check for HTTPS-only URLs
if grep -q "http://" install.sh install.ps1; then
    test_result "HTTPS-only URLs" "false" "Found insecure HTTP URLs"
else
    test_result "HTTPS-only URLs" "true" "All URLs use HTTPS"
fi

# Check for error handling
if grep -q "set -euo pipefail" install.sh; then
    test_result "Bash error handling" "true" "Strict error handling enabled"
else
    test_result "Bash error handling" "false" "Missing strict error handling"
fi

if grep -q "trap.*ERR" install.sh; then
    test_result "Bash error trapping" "true" "Error trapping implemented"
else
    test_result "Bash error trapping" "false" "No error trapping found"
fi

# Check for secure random generation
if grep -q "openssl rand\|/dev/urandom" install.sh; then
    test_result "Secure random (Bash)" "true" "Using system secure random"
else
    test_result "Secure random (Bash)" "false" "No secure random generation"
fi

if grep -q "New-Guid\|Get-Random" install.ps1; then
    test_result "Secure random (PowerShell)" "true" "Using PowerShell secure random"
else
    test_result "Secure random (PowerShell)" "false" "No secure random generation"
fi

echo ""

# Test 6: Documentation quality
echo "📚 Testing documentation..."

# Check README completeness
REQUIRED_SECTIONS=(
    "Quick Installation"
    "System Requirements"
    "Troubleshooting"
    "Security Considerations"
)

for section in "${REQUIRED_SECTIONS[@]}"; do
    if grep -q "$section" INSTALLER_README.md; then
        test_result "README section: $section" "true" "Section found"
    else
        test_result "README section: $section" "false" "Section missing"
    fi
done

# Check for usage examples
if grep -q "curl.*install.sh.*bash\|irm.*install.ps1.*iex" INSTALLER_README.md; then
    test_result "Usage examples" "true" "One-liner examples provided"
else
    test_result "Usage examples" "false" "Missing usage examples"
fi

echo ""

# Test 7: File sizes (reasonable checks)
echo "📊 Testing file sizes..."

INSTALL_SH_SIZE=$(stat -c%s install.sh 2>/dev/null || stat -f%z install.sh 2>/dev/null || echo 0)
INSTALL_PS1_SIZE=$(stat -c%s install.ps1 2>/dev/null || stat -f%z install.ps1 2>/dev/null || echo 0)
README_SIZE=$(stat -c%s INSTALLER_README.md 2>/dev/null || stat -f%z INSTALLER_README.md 2>/dev/null || echo 0)

test_result "Bash installer size" "$([[ $INSTALL_SH_SIZE -gt 10000 && $INSTALL_SH_SIZE -lt 100000 ]] && echo true || echo false)" "${INSTALL_SH_SIZE} bytes"
test_result "PowerShell installer size" "$([[ $INSTALL_PS1_SIZE -gt 10000 && $INSTALL_PS1_SIZE -lt 100000 ]] && echo true || echo false)" "${INSTALL_PS1_SIZE} bytes"
test_result "README size" "$([[ $README_SIZE -gt 5000 ]] && echo true || echo false)" "${README_SIZE} bytes"

echo ""

# Test 8: Platform detection
echo "🌐 Testing platform detection..."

# Check if installers detect common platforms
PLATFORMS=("linux" "macos" "windows")
for platform in "${PLATFORMS[@]}"; do
    if grep -q "$platform" install.sh install.ps1; then
        test_result "Platform detection: $platform" "true" "Platform handling found"
    else
        test_result "Platform detection: $platform" "false" "No platform handling"
    fi
done

echo ""

# Summary
echo "=================================================="
echo "🎯 VALIDATION SUMMARY"
echo "=================================================="
echo ""
echo "Results:"
echo "  ✅ Passed: $PASSED"
echo "  ❌ Failed: $FAILED"
echo "  📊 Total:  $((PASSED + FAILED))"

TOTAL=$((PASSED + FAILED))
if [[ $TOTAL -gt 0 ]]; then
    SUCCESS_RATE=$(( (PASSED * 100) / TOTAL ))
    echo "  🎯 Success Rate: ${SUCCESS_RATE}%"
else
    SUCCESS_RATE=0
fi

echo ""

if [[ $FAILED -eq 0 ]]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo "Installers are ready for deployment."
elif [[ $SUCCESS_RATE -ge 85 ]]; then
    echo -e "${YELLOW}⚠️  MINOR ISSUES DETECTED${NC}"
    echo "Installers are mostly ready, but review failed tests."
else
    echo -e "${RED}❌ SIGNIFICANT ISSUES DETECTED${NC}"
    echo "Please fix issues before deployment."
fi

echo ""
echo "Next steps:"
if [[ $FAILED -eq 0 ]]; then
    echo "1. Upload installers to GitHub repository"
    echo "2. Test one-liner commands on clean systems"
    echo "3. Update main README with installer links"
else
    echo "1. Review and fix failed tests"
    echo "2. Re-run validation: ./validate-installers.sh"
    echo "3. Test on target platforms"
fi

echo ""
echo "Files validated:"
echo "  📄 install.ps1 (Windows PowerShell installer)"
echo "  📄 install.sh (Linux/macOS Bash installer)"  
echo "  📄 INSTALLER_README.md (Comprehensive documentation)"
echo "  📄 test-installer.ps1 (Comprehensive test suite)"
echo ""

exit $([[ $FAILED -eq 0 ]] && echo 0 || echo 1)