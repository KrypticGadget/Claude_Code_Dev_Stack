#!/bin/bash
# Claude Code Dev Stack v2.1 - Master Uninstaller (Linux/WSL)
# Removes agents, commands, MCPs, and hooks with granular control

set -e

# Default values
AGENTS=false
COMMANDS=false
MCPS=false
HOOKS=false
ALL=false
FORCE=false
WHATIF=false
BACKUP=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --agents) AGENTS=true; shift ;;
        --commands) COMMANDS=true; shift ;;
        --mcps) MCPS=true; shift ;;
        --hooks) HOOKS=true; shift ;;
        --all) ALL=true; shift ;;
        --force) FORCE=true; shift ;;
        --whatif) WHATIF=true; shift ;;
        --backup) BACKUP=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Functions
print_header() { echo -e "\n${CYAN}=== $1 ===${NC}"; }
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; }

# ASCII Art Banner
echo -e "${RED}"
cat << "EOF"
╔═══════════════════════════════════════════════════════╗
║      Claude Code Dev Stack v2.1 - Uninstaller         ║
╚═══════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Exit code tracker
EXIT_CODE=0

# Define paths
PROJECT_CLAUDE_DIR="$(pwd)/.claude"
USER_CLAUDE_DIR="$HOME/.claude"
BACKUP_DIR="$HOME/claude-backup-$(date +%Y%m%d-%H%M%S)"

# Component arrays
declare -a AGENT_FILES=(
    "agents/frontend-architect.md"
    "agents/backend-architect.md"
    "agents/database-architect.md"
    "agents/devops-architect.md"
    "agents/api-architect.md"
    "agents/security-architect.md"
    "agents/testing-architect.md"
    "agents/documentation-architect.md"
    "agents/ui-ux-designer.md"
    "agents/business-analyst.md"
    "agents/project-manager.md"
    "agents/quality-assurance.md"
    "agents/performance-engineer.md"
    "agents/data-scientist.md"
    "agents/mobile-developer.md"
    "agents/blockchain-developer.md"
    "agents/game-developer.md"
    "agents/embedded-systems.md"
    "agents/machine-learning.md"
    "agents/cloud-architect.md"
    "agents/solution-architect.md"
    "agents/integration-specialist.md"
    "agents/automation-engineer.md"
    "agents/compliance-officer.md"
    "agents/accessibility-specialist.md"
    "agents/localization-engineer.md"
    "agents/support-engineer.md"
    "agents/master-orchestrator.md"
)

declare -a COMMAND_FILES=(
    "commands/build-frontend.md"
    "commands/build-backend.md"
    "commands/setup-database.md"
    "commands/deploy-app.md"
    "commands/run-tests.md"
    "commands/generate-docs.md"
    "commands/analyze-security.md"
    "commands/optimize-performance.md"
    "commands/create-api.md"
    "commands/design-ui.md"
)

declare -a HOOK_FILES=(
    "hooks/pre-response.md"
    "hooks/post-response.md"
    "hooks/error-handler.md"
    "hooks/context-enhancer.md"
    "hooks/quality-checker.md"
)

declare -a MCP_NAMES=(
    "playwright-mcp"
    "obsidian-mcp"
    "brave-search-mcp"
)

# Check if no parameters provided
if ! $AGENTS && ! $COMMANDS && ! $MCPS && ! $HOOKS && ! $ALL; then
    print_header "Uninstall Menu"
    echo -e "${YELLOW}What would you like to uninstall?${NC}"
    echo "[1] All components"
    echo "[2] Agents only"
    echo "[3] Commands only"
    echo "[4] MCPs only"
    echo "[5] Hooks only"
    echo "[6] Custom selection"
    echo "[0] Cancel"
    
    read -p $'\nSelect option (0-6): ' choice
    
    case $choice in
        0) print_info "Uninstall cancelled"; exit 0 ;;
        1) ALL=true ;;
        2) AGENTS=true ;;
        3) COMMANDS=true ;;
        4) MCPS=true ;;
        5) HOOKS=true ;;
        6)
            echo -e "\n${YELLOW}Select components to uninstall:${NC}"
            read -p "Remove Agents? (y/n): " ans
            [[ "$ans" == "y" ]] && AGENTS=true
            read -p "Remove Commands? (y/n): " ans
            [[ "$ans" == "y" ]] && COMMANDS=true
            read -p "Remove MCPs? (y/n): " ans
            [[ "$ans" == "y" ]] && MCPS=true
            read -p "Remove Hooks? (y/n): " ans
            [[ "$ans" == "y" ]] && HOOKS=true
            ;;
        *) print_error "Invalid option"; exit 2 ;;
    esac
fi

# If -All is specified, enable all components
if $ALL; then
    AGENTS=true
    COMMANDS=true
    MCPS=true
    HOOKS=true
fi

# Confirmation
if ! $FORCE; then
    print_header "Components to Uninstall"
    $AGENTS && echo -e "${YELLOW}• Agents (28 files)${NC}"
    $COMMANDS && echo -e "${YELLOW}• Commands (10 files)${NC}"
    $MCPS && echo -e "${YELLOW}• MCPs (3 packages)${NC}"
    $HOOKS && echo -e "${YELLOW}• Hooks (5 files)${NC}"
    
    $BACKUP && print_info "Backup will be created at: $BACKUP_DIR"
    
    read -p $'\nProceed with uninstall? (y/n): ' confirm
    if [[ "$confirm" != "y" ]]; then
        print_info "Uninstall cancelled"
        exit 0
    fi
fi

# Create backup if requested
if $BACKUP && ! $WHATIF; then
    print_header "Creating Backup"
    mkdir -p "$BACKUP_DIR"
    
    # Backup project .claude directory
    if [ -d "$PROJECT_CLAUDE_DIR" ]; then
        cp -r "$PROJECT_CLAUDE_DIR" "$BACKUP_DIR/project-claude"
        print_success "Backed up project .claude directory"
    fi
    
    # Backup user .claude directory
    if [ -d "$USER_CLAUDE_DIR" ]; then
        cp -r "$USER_CLAUDE_DIR" "$BACKUP_DIR/user-claude"
        print_success "Backed up user .claude directory"
    fi
    
    print_info "Backup location: $BACKUP_DIR"
fi

# Function to remove files
remove_component_files() {
    local component_type=$1
    shift
    local files=("$@")
    
    print_header "Removing $component_type"
    local removed_count=0
    local failed_count=0
    
    for file in "${files[@]}"; do
        # Check project directory
        local project_path="$PROJECT_CLAUDE_DIR/$file"
        if [ -f "$project_path" ]; then
            if $WHATIF; then
                echo -e "${GRAY}Would remove: $project_path${NC}"
            else
                if rm -f "$project_path" 2>/dev/null; then
                    print_success "Removed: $file (project)"
                    ((removed_count++))
                else
                    print_error "Failed to remove: $file (project)"
                    ((failed_count++))
                    EXIT_CODE=1
                fi
            fi
        fi
        
        # Check user directory
        local user_path="$USER_CLAUDE_DIR/$file"
        if [ -f "$user_path" ]; then
            if $WHATIF; then
                echo -e "${GRAY}Would remove: $user_path${NC}"
            else
                if rm -f "$user_path" 2>/dev/null; then
                    print_success "Removed: $file (user)"
                    ((removed_count++))
                else
                    print_error "Failed to remove: $file (user)"
                    ((failed_count++))
                    EXIT_CODE=1
                fi
            fi
        fi
    done
    
    print_info "Summary: $removed_count removed, $failed_count failed"
    echo "$removed_count $failed_count"
}

# Track overall results
declare -A RESULTS

# Remove Agents
if $AGENTS; then
    result=$(remove_component_files "Agents" "${AGENT_FILES[@]}")
    RESULTS[agents]="$result"
fi

# Remove Commands
if $COMMANDS; then
    result=$(remove_component_files "Commands" "${COMMAND_FILES[@]}")
    RESULTS[commands]="$result"
fi

# Remove Hooks
if $HOOKS; then
    result=$(remove_component_files "Hooks" "${HOOK_FILES[@]}")
    RESULTS[hooks]="$result"
fi

# Remove MCPs
if $MCPS; then
    print_header "Removing MCPs"
    mcp_removed=0
    mcp_failed=0
    
    # Check if claude CLI is available
    if command -v claude &> /dev/null; then
        # Get list of installed MCPs
        installed_mcps=$(claude mcp list 2>/dev/null || true)
        
        for mcp in "${MCP_NAMES[@]}"; do
            if echo "$installed_mcps" | grep -q "$mcp"; then
                if $WHATIF; then
                    echo -e "${GRAY}Would remove MCP: $mcp${NC}"
                else
                    if claude mcp remove "$mcp" 2>/dev/null; then
                        print_success "Removed MCP: $mcp"
                        ((mcp_removed++))
                    else
                        print_error "Failed to remove MCP: $mcp"
                        ((mcp_failed++))
                        EXIT_CODE=1
                    fi
                fi
            fi
        done
    else
        print_warning "Claude CLI not found. MCPs must be removed manually."
        EXIT_CODE=1
    fi
    
    RESULTS[mcps]="$mcp_removed $mcp_failed"
    print_info "Summary: $mcp_removed removed, $mcp_failed failed"
fi

# Clean up empty directories
if ! $WHATIF; then
    print_header "Cleaning Up Empty Directories"
    
    declare -a dirs_to_check=(
        "$PROJECT_CLAUDE_DIR/agents"
        "$PROJECT_CLAUDE_DIR/commands"
        "$PROJECT_CLAUDE_DIR/hooks"
        "$USER_CLAUDE_DIR/agents"
        "$USER_CLAUDE_DIR/commands"
        "$USER_CLAUDE_DIR/hooks"
    )
    
    for dir in "${dirs_to_check[@]}"; do
        if [ -d "$dir" ] && [ -z "$(ls -A "$dir")" ]; then
            if rmdir "$dir" 2>/dev/null; then
                print_success "Removed empty directory: $dir"
            else
                print_warning "Could not remove directory: $dir"
            fi
        fi
    done
fi

# Final Summary
print_header "Uninstall Summary"
total_removed=0
total_failed=0

for component in "${!RESULTS[@]}"; do
    read removed failed <<< "${RESULTS[$component]}"
    total_removed=$((total_removed + removed))
    total_failed=$((total_failed + failed))
    
    if [ $failed -eq 0 ]; then
        echo -e "${GREEN}✓ $component: $removed removed, $failed failed${NC}"
    else
        echo -e "${YELLOW}⚠ $component: $removed removed, $failed failed${NC}"
    fi
done

echo -e "\n${CYAN}Total: $total_removed components removed, $total_failed failed${NC}"

$WHATIF && print_info "This was a dry run. No changes were made."
$BACKUP && ! $WHATIF && print_info "Backup saved to: $BACKUP_DIR"

# Set exit code
if [ $total_failed -gt 0 ]; then
    EXIT_CODE=1  # Partial success
elif [ $total_removed -eq 0 ]; then
    EXIT_CODE=2  # Nothing to remove
fi

exit $EXIT_CODE