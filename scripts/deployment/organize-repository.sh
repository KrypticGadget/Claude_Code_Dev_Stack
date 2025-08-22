#!/bin/bash
# Repository Organization Script for Unix/Linux/macOS
# Cleans and organizes the V3.6.9 repository structure

set -e  # Exit on error

echo "================================================"
echo " Claude Code Agents V3.6.9 Repository Organizer"
echo "================================================"
echo

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Repository location: $REPO_ROOT"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7+ and try again"
    exit 1
fi

echo "Python found. Starting organization process..."
echo

# Parse command line arguments
DRY_RUN=false
FORCE=false

for arg in "$@"; do
    case $arg in
        --dry-run)
        DRY_RUN=true
        shift
        ;;
        --force)
        FORCE=true
        shift
        ;;
        -h|--help)
        echo "Usage: $0 [--dry-run] [--force] [--help]"
        echo "  --dry-run  Show what would be done without making changes"
        echo "  --force    Skip confirmation prompt"
        echo "  --help     Show this help message"
        exit 0
        ;;
    esac
done

# Ask for confirmation unless --force is passed
if [ "$FORCE" != true ] && [ "$DRY_RUN" != true ]; then
    echo "This will organize your repository structure and create backups."
    read -p "Continue? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Organization cancelled."
        exit 0
    fi
fi

# Run the organization
if [ "$DRY_RUN" = true ]; then
    echo "Running in DRY RUN mode (no changes will be made)..."
    python3 "$SCRIPT_DIR/automated-repository-organizer.py" "$REPO_ROOT" --dry-run
else
    echo "Starting repository organization..."
    python3 "$SCRIPT_DIR/automated-repository-organizer.py" "$REPO_ROOT"
fi

# Check result
if [ $? -eq 0 ]; then
    echo
    echo "✅ Repository organization completed successfully!"
    echo
    echo "Next steps:"
    echo "1. Review ORGANIZATION_GUIDE.md for usage instructions"
    echo "2. Run: python3 scripts/validate-organization.py to verify"
    echo "3. Set up scheduled maintenance with: bash scripts/setup-cron.sh"
else
    echo
    echo "❌ Repository organization encountered errors"
    echo "Check the organization report for details"
    exit 1
fi