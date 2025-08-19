#!/bin/bash
# Claude Code Dev Stack V3.0 - Quick Cleanup Script
# This is a simple wrapper for the Python cleanup script

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}🚀 Claude Code Dev Stack V3.0 - Quick Cleanup${NC}"
echo "=================================================="

# Check if Python script exists
PYTHON_SCRIPT="$SCRIPT_DIR/cleanup.py"
if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    echo -e "${RED}❌ Python cleanup script not found: $PYTHON_SCRIPT${NC}"
    exit 1
fi

# Make Python script executable
chmod +x "$PYTHON_SCRIPT"

# Check for Python
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo -e "${RED}❌ Python not found. Please install Python 3.6+${NC}"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo -e "${BLUE}🐍 Using Python: $(which $PYTHON_CMD)${NC}"
echo -e "${BLUE}📁 Project root: $PROJECT_ROOT${NC}"
echo ""

# Parse command line arguments
DRY_RUN=false
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run|--dry)
            DRY_RUN=true
            shift
            ;;
        --force|-f)
            FORCE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --dry-run, --dry    Run analysis without actual cleanup"
            echo "  --force, -f         Force cleanup without confirmation"
            echo "  --help, -h          Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                  # Interactive cleanup"
            echo "  $0 --dry-run        # Analyze without cleanup"
            echo "  $0 --force          # Cleanup without prompts"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Build Python command
PYTHON_ARGS=("--project-root" "$PROJECT_ROOT")

if [[ "$DRY_RUN" == true ]]; then
    PYTHON_ARGS+=("--dry-run")
    echo -e "${YELLOW}🔍 Running in dry-run mode (no actual cleanup)${NC}"
fi

if [[ "$FORCE" == true ]]; then
    PYTHON_ARGS+=("--force")
    echo -e "${YELLOW}⚡ Running in force mode (no confirmation prompts)${NC}"
fi

echo ""

# Execute Python cleanup script
echo -e "${GREEN}▶️  Executing cleanup script...${NC}"
echo ""

if "$PYTHON_CMD" "$PYTHON_SCRIPT" "${PYTHON_ARGS[@]}"; then
    echo ""
    echo -e "${GREEN}✅ Cleanup completed successfully!${NC}"
    
    # Show final status
    if [[ -f "$SCRIPT_DIR/cleanup_report.md" ]]; then
        echo -e "${BLUE}📄 Cleanup report available at: $SCRIPT_DIR/cleanup_report.md${NC}"
    fi
    
    if [[ -f "$SCRIPT_DIR/extraction_manifest.json" ]]; then
        echo -e "${BLUE}📋 Extraction manifest available at: $SCRIPT_DIR/extraction_manifest.json${NC}"
    fi
    
    # Check if clones directory still exists
    if [[ ! -d "$PROJECT_ROOT/clones" ]]; then
        echo -e "${GREEN}🗑️  Clones directory successfully removed${NC}"
    else
        echo -e "${YELLOW}⚠️  Clones directory still exists${NC}"
    fi
    
else
    echo ""
    echo -e "${RED}❌ Cleanup failed!${NC}"
    echo -e "${YELLOW}💡 Try running with --dry-run to analyze the issue${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}🎉 Claude Code Dev Stack V3.0 cleanup complete!${NC}"
echo "=================================================="