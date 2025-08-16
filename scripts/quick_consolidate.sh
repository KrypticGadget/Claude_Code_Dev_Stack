#!/bin/bash
# Quick Consolidation Script for Unix/Linux/macOS
# ==============================================
# Executes the v3 consolidation process with safety checks

set -e  # Exit on error

echo
echo "============================================================"
echo " Claude Code Dev Stack v3 Consolidation"
echo "============================================================"
echo

# Change to the script directory and then to root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Check if v3 directory exists
if [ ! -d "Claude_Code_Dev_Stack_v3" ]; then
    echo "ERROR: Claude_Code_Dev_Stack_v3 directory not found"
    echo "Make sure you're running this from the correct location"
    exit 1
fi

# Safety prompt
echo "This will consolidate the v3 structure into the root level."
echo "A full backup will be created before making any changes."
echo
read -p "Do you want to continue? (y/N): " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "Consolidation cancelled."
    exit 0
fi

echo
echo "Starting consolidation process..."
echo

# Check for Python
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "ERROR: Python not found"
    echo "Please install Python 3.x"
    exit 1
fi

# Run consolidation
echo "Using Python consolidation script..."
if $PYTHON_CMD scripts/consolidate_v3_structure.py; then
    echo
    echo "============================================================"
    echo " CONSOLIDATION COMPLETED SUCCESSFULLY"
    echo "============================================================"
    echo
    echo "Next steps:"
    echo "1. Run validation: $PYTHON_CMD scripts/validate_consolidation.py"
    echo "2. Test functionality"
    echo "3. Review CONSOLIDATION_REPORT.md"
    echo
else
    echo
    echo "============================================================"
    echo " CONSOLIDATION FAILED"
    echo "============================================================"
    echo
    echo "Check the logs and restore from backup if needed."
    echo "Backup location will be shown in the error output above."
    echo
    exit 1
fi