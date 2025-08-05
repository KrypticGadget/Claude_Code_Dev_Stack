#!/bin/bash
# Claude Code Dev Stack v2.1 - MCPs Uninstaller (macOS)
# Removes Tier 1 Model Context Protocol packages

set -e

# Default values
FORCE=false
WHATIF=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --force) FORCE=true; shift ;;
        --whatif) WHATIF=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Colors (macOS compatible)
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    CYAN='\033[0;36m'
    NC='\033[0m'
else
    RED=''; GREEN=''; YELLOW=''; BLUE=''; CYAN=''; NC=''
fi

# Functions
print_header() { echo -e "\n${CYAN}=== $1 ===${NC}"; }
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; }

echo -e "\n${RED}🔌 Claude Code MCPs Uninstaller${NC}"

# Tier 1 MCPs to remove
declare -a MCP_NAMES=(
    "playwright-mcp"
    "obsidian-mcp"
    "brave-search-mcp"
)

# Check if claude CLI is available
if ! command -v claude &> /dev/null; then
    print_error "Claude CLI not found. Please install Claude Desktop first."
    print_info "MCPs can only be managed through the Claude CLI."
    exit 2
fi

# Get list of installed MCPs
print_header "Checking Installed MCPs"
installed_mcps=$(claude mcp list 2>/dev/null || true)
found_mcps=()

for mcp in "${MCP_NAMES[@]}"; do
    if echo "$installed_mcps" | grep -q "$mcp"; then
        found_mcps+=("$mcp")
        print_info "Found: $mcp"
    fi
done

if [ ${#found_mcps[@]} -eq 0 ]; then
    print_warning "No Tier 1 MCPs found to uninstall"
    exit 0
fi

# Confirmation
if ! $FORCE; then
    print_warning "This will remove the following MCPs:"
    for mcp in "${found_mcps[@]}"; do
        echo -e "  ${YELLOW}• $mcp${NC}"
    done
    
    read -p $'\nProceed? (y/n): ' confirm
    if [[ "$confirm" != "y" ]]; then
        print_info "Uninstall cancelled"
        exit 0
    fi
fi

print_header "Removing MCPs"
removed_count=0
failed_count=0

for mcp in "${found_mcps[@]}"; do
    if $WHATIF; then
        echo "Would remove MCP: $mcp"
        ((removed_count++))
    else
        echo -n "Removing $mcp..."
        if claude mcp remove "$mcp" &>/dev/null; then
            echo -e " ${GREEN}Done${NC}"
            print_success "Removed: $mcp"
            ((removed_count++))
        else
            echo -e " ${RED}Failed${NC}"
            print_error "Failed to remove: $mcp"
            ((failed_count++))
        fi
    fi
done

# Additional cleanup for MCP configurations (macOS paths)
if ! $WHATIF && [ $removed_count -gt 0 ]; then
    print_header "Cleaning MCP Configurations"
    
    config_paths=(
        "$HOME/Library/Application Support/Claude/mcp-configs"
        "$HOME/.config/claude/mcp-configs"
    )
    
    for path in "${config_paths[@]}"; do
        if [ -d "$path" ]; then
            for mcp in "${found_mcps[@]}"; do
                mcp_config="$path/$mcp"
                if [ -d "$mcp_config" ]; then
                    if rm -rf "$mcp_config" 2>/dev/null; then
                        print_success "Cleaned config: $mcp"
                    else
                        print_warning "Could not clean config for: $mcp"
                    fi
                fi
            done
        fi
    done
fi

# Summary
print_header "Summary"
echo -e "${GREEN}MCPs removed: $removed_count${NC}"
if [ $failed_count -gt 0 ]; then
    echo -e "${RED}Failed: $failed_count${NC}"
    exit 1
fi

$WHATIF && print_info "This was a dry run. No changes were made."

# Restart recommendation
if [ $removed_count -gt 0 ] && ! $WHATIF; then
    print_info "Please restart Claude Desktop to complete the uninstall."
fi

exit 0