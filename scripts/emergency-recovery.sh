#!/bin/bash
# Emergency Recovery Script for Claude Code Dev Stack (Unix/Linux/macOS)
# This script provides emergency recovery from the safety backup branch

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default parameters
FORCE=false
VALIDATE=false
RESTORE_POINT="safety/pre-reorganization-backup"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            FORCE=true
            shift
            ;;
        --validate)
            VALIDATE=true
            shift
            ;;
        --restore-point)
            RESTORE_POINT="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--force] [--validate] [--restore-point <branch>]"
            exit 1
            ;;
    esac
done

echo -e "${RED}🚨 CLAUDE CODE DEV STACK - EMERGENCY RECOVERY${NC}"
echo -e "${YELLOW}=============================================${NC}"

# Function to check Git status
check_git_repository() {
    if [ ! -d ".git" ]; then
        echo -e "${RED}❌ Not in a Git repository. Please run from repository root.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Git repository detected${NC}"
}

# Function to validate backup branch
check_backup_branch() {
    local branch_name="$1"
    
    if ! git show-ref --verify --quiet "refs/heads/$branch_name"; then
        echo -e "${RED}❌ Safety branch '$branch_name' not found!${NC}"
        echo -e "${YELLOW}Available branches:${NC}"
        git branch -a
        exit 1
    fi
    
    echo -e "${GREEN}✅ Safety branch '$branch_name' verified${NC}"
}

# Function to validate key files in backup
validate_backup_integrity() {
    local branch_name="$1"
    
    echo -e "${CYAN}🔍 Validating backup integrity...${NC}"
    
    local key_files=(
        "Claude_Code_Dev_Stack_v3/apps/web/package.json"
        ".claude-example/settings.json"
        "install.sh"
        "docs/README_V3.md"
        "Claude_Code_Dev_Stack_v3/core/hooks/hooks/__init__.py"
    )
    
    local missing_files=()
    
    for file in "${key_files[@]}"; do
        if git cat-file -e "${branch_name}:$file" 2>/dev/null; then
            echo -e "  ${GREEN}✅ $file${NC}"
        else
            echo -e "  ${RED}❌ $file${NC}"
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -gt 0 ]; then
        echo -e "${RED}❌ Critical files missing from backup:${NC}"
        for file in "${missing_files[@]}"; do
            echo -e "    ${RED}- $file${NC}"
        done
        exit 1
    fi
    
    echo -e "${GREEN}✅ Backup integrity verified${NC}"
}

# Function to create recovery branch
create_recovery_branch() {
    local restore_point="$1"
    
    local timestamp=$(date +"%Y%m%d-%H%M%S")
    local recovery_branch="emergency-recovery-$timestamp"
    
    echo -e "${CYAN}🔄 Creating recovery branch: $recovery_branch${NC}"
    
    # Switch to restore point
    if ! git checkout "$restore_point"; then
        echo -e "${RED}❌ Failed to checkout $restore_point${NC}"
        exit 1
    fi
    
    # Create new recovery branch
    if ! git checkout -b "$recovery_branch"; then
        echo -e "${RED}❌ Failed to create recovery branch${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Recovery branch created: $recovery_branch${NC}"
    echo "$recovery_branch"
}

# Function to show recovery status
show_recovery_status() {
    echo -e "${YELLOW}📊 RECOVERY STATUS${NC}"
    echo -e "${YELLOW}==================${NC}"
    
    echo -n "Current branch: "
    git branch --show-current
    
    echo -e "${CYAN}Last 5 commits:${NC}"
    git log --oneline -5
    
    echo -e "\n${CYAN}📁 Key directories status:${NC}"
    local key_dirs=(
        "Claude_Code_Dev_Stack_v3"
        ".claude-example"
        ".github/workflows"
        "docs"
    )
    
    for dir in "${key_dirs[@]}"; do
        if [ -d "$dir" ]; then
            local file_count=$(find "$dir" -type f | wc -l)
            echo -e "  ${GREEN}✅ $dir ($file_count files)${NC}"
        else
            echo -e "  ${RED}❌ $dir (missing)${NC}"
        fi
    done
}

# Main execution
main() {
    check_git_repository
    
    if [ "$VALIDATE" = true ]; then
        echo -e "${CYAN}🔍 VALIDATION MODE - Testing backup without recovery${NC}"
        check_backup_branch "$RESTORE_POINT"
        validate_backup_integrity "$RESTORE_POINT"
        echo -e "${GREEN}✅ Validation complete - backup is ready for emergency recovery${NC}"
        exit 0
    fi
    
    # Check for uncommitted changes
    if [ -n "$(git status --porcelain)" ] && [ "$FORCE" != true ]; then
        echo -e "${YELLOW}⚠️  Uncommitted changes detected:${NC}"
        git status --short
        echo -e "\n${YELLOW}Use --force to proceed anyway, or commit/stash changes first.${NC}"
        exit 1
    fi
    
    echo -e "${RED}🚨 EMERGENCY RECOVERY INITIATED${NC}"
    echo -e "${YELLOW}This will restore repository to: $RESTORE_POINT${NC}"
    
    if [ "$FORCE" != true ]; then
        echo -n "Continue? (type 'RECOVER' to confirm): "
        read -r confirm
        if [ "$confirm" != "RECOVER" ]; then
            echo -e "${YELLOW}❌ Recovery cancelled${NC}"
            exit 0
        fi
    fi
    
    check_backup_branch "$RESTORE_POINT"
    validate_backup_integrity "$RESTORE_POINT"
    
    local recovery_branch
    recovery_branch=$(create_recovery_branch "$RESTORE_POINT")
    
    show_recovery_status
    
    echo -e "\n${GREEN}🎉 EMERGENCY RECOVERY COMPLETE!${NC}"
    echo -e "${GREEN}You are now on branch: $recovery_branch${NC}"
    echo -e "\n${CYAN}Next steps:${NC}"
    echo "1. Verify system functionality"
    echo "2. Run validation scripts"
    echo "3. If recovery is successful, merge to main branch"
    echo "4. If issues persist, check REPOSITORY_SAFETY_BACKUP_STRATEGY.md"
}

# Error handling
trap 'echo -e "\n${RED}❌ Recovery failed${NC}"; echo -e "${YELLOW}📖 Check REPOSITORY_SAFETY_BACKUP_STRATEGY.md for manual recovery procedures${NC}"; exit 1' ERR

# Run main function
main "$@"