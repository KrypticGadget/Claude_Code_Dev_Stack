#!/bin/bash
# Claude Code Dev Stack v2.1 - Uninstaller Scripts Installer (macOS)
# Downloads and installs the uninstaller scripts

set -e

# Colors (macOS compatible)
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    CYAN='\033[0;36m'
    NC='\033[0m'
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    CYAN=''
    NC=''
fi

# Functions
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }

echo -e "\n${CYAN}📦 Installing Claude Code Uninstaller Scripts...${NC}"

# GitHub repository details
REPO_OWNER="Codewordium"
REPO_NAME="Claude_Code_Agents"
BRANCH="main"
BASE_PATH="Claude_Code_Dev_Stack"

# Uninstaller scripts to download
declare -a scripts=(
    "uninstall-all-mac.sh"
    "uninstall-agents-mac.sh"
    "uninstall-commands-mac.sh"
    "uninstall-mcps-mac.sh"
    "uninstall-hooks-mac.sh"
)

# Create uninstallers directory
UNINSTALLERS_DIR="./uninstallers"
mkdir -p "$UNINSTALLERS_DIR"
print_success "Created uninstallers directory"

# Download each script
downloaded_count=0
for script in "${scripts[@]}"; do
    echo -n "Downloading $script..."
    url="https://raw.githubusercontent.com/$REPO_OWNER/$REPO_NAME/$BRANCH/$BASE_PATH/$script"
    
    if curl -sL "$url" -o "$UNINSTALLERS_DIR/$script" 2>/dev/null; then
        chmod +x "$UNINSTALLERS_DIR/$script"
        echo -e " ${GREEN}Done${NC}"
        ((downloaded_count++))
    else
        echo -e " ${RED}Failed${NC}"
        print_error "Failed to download $script"
    fi
done

# Create a convenient run-uninstaller.sh in current directory
cat > ./run-uninstaller.sh << 'EOF'
#!/bin/bash
# Claude Code Dev Stack - Run Uninstaller (macOS)
# Convenient wrapper to run the uninstaller scripts

set -e

# Colors (macOS compatible)
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
fi

# Parse arguments
COMPONENT="${1:-all}"
FORCE=false
WHATIF=false
BACKUP=false

shift || true
while [[ $# -gt 0 ]]; do
    case $1 in
        --force) FORCE=true; shift ;;
        --whatif) WHATIF=true; shift ;;
        --backup) BACKUP=true; shift ;;
        *) echo -e "${RED}Unknown option: $1${NC}"; exit 1 ;;
    esac
done

# Validate component
case $COMPONENT in
    all|agents|commands|mcps|hooks) ;;
    *) echo -e "${RED}Invalid component: $COMPONENT${NC}"; exit 1 ;;
esac

UNINSTALLERS_DIR="$(dirname "$0")/uninstallers"
SCRIPT_NAME="uninstall-$COMPONENT-mac.sh"
SCRIPT_PATH="$UNINSTALLERS_DIR/$SCRIPT_NAME"

if [ ! -f "$SCRIPT_PATH" ]; then
    echo -e "${RED}Error: Uninstaller script not found: $SCRIPT_PATH${NC}"
    echo -e "${YELLOW}Run the install-uninstallers-mac.sh script first.${NC}"
    exit 1
fi

# Build arguments
ARGS=()
[ "$FORCE" = true ] && ARGS+=("--force")
[ "$WHATIF" = true ] && ARGS+=("--whatif")
[ "$BACKUP" = true ] && [ "$COMPONENT" = "all" ] && ARGS+=("--backup")

# Execute the uninstaller
exec "$SCRIPT_PATH" "${ARGS[@]}"
EOF

chmod +x ./run-uninstaller.sh
print_success "Created run-uninstaller.sh"

# Summary
echo -e "\n${GREEN}✅ Installation Complete!${NC}"
echo -e "${CYAN}Downloaded $downloaded_count/${#scripts[@]} uninstaller scripts${NC}"

echo -e "\n${YELLOW}📋 Usage Examples:${NC}"
echo "  ./run-uninstaller.sh              # Interactive menu"
echo "  ./run-uninstaller.sh all --force  # Remove everything without confirmation"
echo "  ./run-uninstaller.sh agents       # Remove agents only"
echo "  ./run-uninstaller.sh all --whatif # Dry run to see what would be removed"
echo "  ./run-uninstaller.sh all --backup # Create backup before removal"

echo -e "\n${YELLOW}💡 Direct script usage:${NC}"
echo "  ./uninstallers/uninstall-all-mac.sh --agents --commands --force"
echo "  ./uninstallers/uninstall-mcps-mac.sh --whatif"

print_info "Uninstaller scripts saved in: $UNINSTALLERS_DIR"