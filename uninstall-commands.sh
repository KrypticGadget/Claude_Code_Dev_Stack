#!/bin/bash
# Claude Code Dev Stack v2.1 - Commands Uninstaller (Linux/WSL)
# Removes only command files from project and user directories

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

echo -e "\n${RED}⚡ Claude Code Commands Uninstaller${NC}"

# Define paths
PROJECT_CLAUDE_DIR="$(pwd)/.claude"
USER_CLAUDE_DIR="$HOME/.claude"

# Command files to remove
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

# Confirmation
if ! $FORCE; then
    print_warning "This will remove 10 command files from:"
    [ -d "$PROJECT_CLAUDE_DIR" ] && echo "  • $PROJECT_CLAUDE_DIR"
    [ -d "$USER_CLAUDE_DIR" ] && echo "  • $USER_CLAUDE_DIR"
    
    read -p $'\nProceed? (y/n): ' confirm
    if [[ "$confirm" != "y" ]]; then
        print_info "Uninstall cancelled"
        exit 0
    fi
fi

print_header "Removing Commands"
removed_count=0
failed_count=0

for file in "${COMMAND_FILES[@]}"; do
    # Check project directory
    project_path="$PROJECT_CLAUDE_DIR/$file"
    if [ -f "$project_path" ]; then
        if $WHATIF; then
            echo -e "Would remove: $project_path"
        else
            if rm -f "$project_path" 2>/dev/null; then
                print_success "Removed: $file (project)"
                ((removed_count++))
            else
                print_error "Failed to remove: $file (project)"
                ((failed_count++))
            fi
        fi
    fi
    
    # Check user directory
    user_path="$USER_CLAUDE_DIR/$file"
    if [ -f "$user_path" ]; then
        if $WHATIF; then
            echo -e "Would remove: $user_path"
        else
            if rm -f "$user_path" 2>/dev/null; then
                print_success "Removed: $file (user)"
                ((removed_count++))
            else
                print_error "Failed to remove: $file (user)"
                ((failed_count++))
            fi
        fi
    fi
done

# Clean up empty commands directories
if ! $WHATIF; then
    for dir in "$PROJECT_CLAUDE_DIR/commands" "$USER_CLAUDE_DIR/commands"; do
        if [ -d "$dir" ] && [ -z "$(ls -A "$dir")" ]; then
            if rmdir "$dir" 2>/dev/null; then
                print_success "Removed empty directory: $dir"
            else
                print_warning "Could not remove directory: $dir"
            fi
        fi
    done
fi

# Summary
print_header "Summary"
echo -e "${GREEN}Commands removed: $removed_count${NC}"
if [ $failed_count -gt 0 ]; then
    echo -e "${RED}Failed: $failed_count${NC}"
    exit 1
fi

$WHATIF && print_info "This was a dry run. No changes were made."

exit 0