#!/bin/bash

# Fix Permissions Script for Claude Code Dev Stack V3
# Standalone shell script to fix executable permissions and shebangs

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║     🔧 Claude Code Dev Stack V3 - Permission Fixer 🔧           ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${BLUE}🔧 Fixing executable permissions and shebangs...${NC}"

# Function to fix executable permissions
fix_executable_permissions() {
    echo -e "${BLUE}🔧 Fixing executable permissions on Unix system...${NC}"
    
    local fixed_count=0
    
    # Fix bin directory scripts
    if [ -d "$PACKAGE_ROOT/bin" ]; then
        echo -e "${YELLOW}📁 Processing bin directory...${NC}"
        for file in "$PACKAGE_ROOT/bin"/*.js; do
            if [ -f "$file" ]; then
                chmod +x "$file"
                echo -e "${GREEN}  ✅ Made executable: $(basename "$file")${NC}"
                ((fixed_count++))
            fi
        done
    fi
    
    # Fix Python hook scripts
    if [ -d "$PACKAGE_ROOT/core/hooks/hooks" ]; then
        echo -e "${YELLOW}📁 Processing Python hook scripts...${NC}"
        for file in "$PACKAGE_ROOT/core/hooks/hooks"/*.py; do
            if [ -f "$file" ]; then
                chmod +x "$file"
                echo -e "${GREEN}  ✅ Made executable: $(basename "$file")${NC}"
                ((fixed_count++))
            fi
        done
    fi
    
    # Fix shell scripts
    echo -e "${YELLOW}📁 Processing shell scripts...${NC}"
    find "$PACKAGE_ROOT" -name "*.sh" -type f -exec chmod +x {} \; -exec echo -e "${GREEN}  ✅ Made executable: $(basename "{}")${NC}" \;
    
    # Count shell scripts
    local sh_count=$(find "$PACKAGE_ROOT" -name "*.sh" -type f | wc -l)
    ((fixed_count += sh_count))
    
    echo -e "${GREEN}✅ Fixed permissions on $fixed_count files${NC}"
}

# Function to validate and fix Python script shebangs
validate_python_scripts() {
    echo -e "${BLUE}🐍 Validating and fixing Python script shebangs...${NC}"
    
    local fixed_count=0
    local validated_count=0
    
    # Find all Python files
    while IFS= read -r -d '' file; do
        ((validated_count++))
        
        # Read first line
        first_line=$(head -n 1 "$file")
        
        # Check if shebang exists and is correct
        if [[ ! "$first_line" =~ ^#!/usr/bin/env\ python ]]; then
            # Add proper shebang
            temp_file=$(mktemp)
            echo "#!/usr/bin/env python3" > "$temp_file"
            cat "$file" >> "$temp_file"
            mv "$temp_file" "$file"
            echo -e "${GREEN}  ✅ Added shebang to: $(basename "$file")${NC}"
            ((fixed_count++))
        else
            echo -e "  ✓ $(basename "$file") already has shebang"
        fi
    done < <(find "$PACKAGE_ROOT" -name "*.py" -type f -print0)
    
    if [ $fixed_count -gt 0 ]; then
        echo -e "${GREEN}✅ Fixed shebangs in $fixed_count/$validated_count Python scripts${NC}"
    else
        echo -e "${GREEN}✅ All $validated_count Python scripts have proper shebangs${NC}"
    fi
}

# Function to create a post-install hook script
create_post_install_hook() {
    echo -e "${BLUE}🔗 Creating post-install hook for npm...${NC}"
    
    # Create a simple post-install script that runs this fixer
    cat > "$PACKAGE_ROOT/scripts/post-install-hook.sh" << 'EOF'
#!/bin/bash
# Auto-run permission fixer after npm install

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Only run on Unix systems
if [[ "$OSTYPE" != "msys" && "$OSTYPE" != "win32" ]]; then
    echo "🔧 Auto-fixing permissions after npm install..."
    if [ -f "$SCRIPT_DIR/fix-permissions.sh" ]; then
        bash "$SCRIPT_DIR/fix-permissions.sh"
    fi
fi
EOF
    
    chmod +x "$PACKAGE_ROOT/scripts/post-install-hook.sh"
    echo -e "${GREEN}  ✅ Created post-install hook${NC}"
}

# Function to update package.json if needed
update_package_json() {
    echo -e "${BLUE}📦 Checking package.json configuration...${NC}"
    
    local package_json="$PACKAGE_ROOT/package.json"
    
    if [ -f "$package_json" ]; then
        # Check if postinstall script exists
        if grep -q '"postinstall"' "$package_json"; then
            echo -e "${GREEN}  ✓ postinstall script already configured${NC}"
        else
            echo -e "${YELLOW}  ⚠️  Consider adding postinstall script to package.json${NC}"
            echo -e "${YELLOW}     Add: \"postinstall\": \"node scripts/postinstall.js\"${NC}"
        fi
    fi
}

# Main execution
main() {
    # Check if we're on a Unix-like system
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        echo -e "${YELLOW}⚠️  Windows detected - use PowerShell script or Node.js version instead${NC}"
        echo -e "${YELLOW}   Run: npm run fix-permissions${NC}"
        exit 0
    fi
    
    # Verify we can write to the files
    if [ ! -w "$PACKAGE_ROOT" ]; then
        echo -e "${RED}❌ No write permission to package directory${NC}"
        echo -e "${YELLOW}💡 Try running with sudo or check file permissions${NC}"
        exit 1
    fi
    
    # Run all fixes
    fix_executable_permissions
    validate_python_scripts
    create_post_install_hook
    update_package_json
    
    echo ""
    echo -e "${GREEN}✅ All permissions and paths have been fixed!${NC}"
    echo -e "${BLUE}📋 Summary:${NC}"
    echo -e "${GREEN}  ✅ Executable permissions set${NC}"
    echo -e "${GREEN}  ✅ Python shebangs validated${NC}"
    echo -e "${GREEN}  ✅ Post-install hook created${NC}"
    echo -e "${YELLOW}💡 You can now install globally with:${NC}"
    echo -e "   npm install -g github:KrypticGadget/Claude_Code_Dev_Stack#feature/v3-dev"
    echo ""
}

# Trap errors
trap 'echo -e "${RED}❌ Script failed at line $LINENO${NC}"' ERR

# Run main function
main "$@"