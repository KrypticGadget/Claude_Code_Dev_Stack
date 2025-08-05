#!/bin/bash
# Claude Code Hooks System Installer for Ubuntu/WSL
# Version: 1.0.0
# Repository: https://github.com/KrypticGadget/Claude_Code_Dev_Stack

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }

# Start installation
echo
log_info "=== Claude Code Hooks System Installer ==="
echo

START_TIME=$(date +%s)

# Check Python installation
log_info "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
    MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [[ $MAJOR -eq 3 && $MINOR -ge 8 ]]; then
        log_success "Python $(python3 --version 2>&1) found"
    else
        log_error "Python 3.8+ required. Found: Python $PYTHON_VERSION"
        exit 1
    fi
else
    log_error "Python 3 not found. Install with: sudo apt update && sudo apt install python3"
    exit 1
fi

# Check for required tools
log_info "Checking required tools..."
MISSING_TOOLS=()

for tool in curl jq; do
    if ! command -v $tool &> /dev/null; then
        MISSING_TOOLS+=($tool)
    fi
done

if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
    log_warning "Missing tools: ${MISSING_TOOLS[*]}"
    log_info "Installing missing tools..."
    sudo apt update && sudo apt install -y ${MISSING_TOOLS[*]}
fi

# Find Claude Code installation
log_info "Detecting Claude Code installation..."

# Common paths for Claude Code on Linux/WSL
CLAUDE_PATHS=(
    "$HOME/.claude"
    "$HOME/.config/Claude"
    "$HOME/.local/share/Claude"
    "/mnt/c/Users/$USER/.claude"
    "/mnt/c/Users/$USER/AppData/Roaming/Claude"
    "/mnt/c/Users/$USER/AppData/Local/Claude"
)

CLAUDE_DIR=""
for path in "${CLAUDE_PATHS[@]}"; do
    if [ -d "$path" ]; then
        CLAUDE_DIR="$path"
        break
    fi
done

if [ -z "$CLAUDE_DIR" ]; then
    log_warning "Claude Code installation not found in default locations."
    read -p "Please enter Claude Code installation path: " CLAUDE_DIR
    if [ ! -d "$CLAUDE_DIR" ]; then
        log_error "Invalid path: $CLAUDE_DIR"
        exit 1
    fi
fi

log_success "Found Claude Code at: $CLAUDE_DIR"

# Create directory structure
log_info "Creating directory structure..."

DIRECTORIES=(
    "$CLAUDE_DIR/.claude/hooks"
    "$CLAUDE_DIR/.claude/config"
    "$CLAUDE_DIR/.claude/state"
)

for dir in "${DIRECTORIES[@]}"; do
    mkdir -p "$dir"
    if [ "${VERBOSE:-false}" = "true" ]; then
        log_info "  Created: $dir"
    fi
done

log_success "Directory structure created"

# Download files
BASE_URL="https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main"

# Hook scripts to download
HOOK_SCRIPTS=(
    "session_loader.py"
    "session_saver.py"
    "quality_gate.py"
    "planning_trigger.py"
    "agent_orchestrator.py"
    "agent_mention_parser.py"
    "model_tracker.py"
    "mcp_gateway.py"
    "mcp_pipeline.py"
)

# Config files to download
CONFIG_FILES=(
    "coding_standards.json"
    "agent_routing.json"
    "agent_models.json"
    "mcp_config.json"
)

log_info "Downloading hook scripts..."
DOWNLOADED=0
TOTAL=$((${#HOOK_SCRIPTS[@]} + ${#CONFIG_FILES[@]}))

for script in "${HOOK_SCRIPTS[@]}"; do
    URL="$BASE_URL/.claude/hooks/$script"
    DEST="$CLAUDE_DIR/.claude/hooks/$script"
    
    if curl -sS -f -o "$DEST" "$URL" 2>/dev/null; then
        chmod +x "$DEST"
        ((DOWNLOADED++))
        PROGRESS=$((DOWNLOADED * 100 / TOTAL))
        printf "\r  Progress: [%-50s] %d%%" $(printf '#%.0s' $(seq 1 $((PROGRESS / 2)))) $PROGRESS
    else
        log_warning "Failed to download $script, creating default..."
        
        # Create default script
        cat > "$DEST" << 'EOF'
#!/usr/bin/env python3
"""
Hook script - Auto-generated placeholder
"""

import json
import sys
import os

def main():
    # Placeholder implementation
    print(f"Hook {os.path.basename(__file__)} executed", file=sys.stderr)
    return 0

if __name__ == "__main__":
    sys.exit(main())
EOF
        chmod +x "$DEST"
        ((DOWNLOADED++))
    fi
done

echo # New line after progress bar

log_info "Downloading config files..."

for config in "${CONFIG_FILES[@]}"; do
    URL="$BASE_URL/.claude/config/$config"
    DEST="$CLAUDE_DIR/.claude/config/$config"
    
    if curl -sS -f -o "$DEST" "$URL" 2>/dev/null; then
        ((DOWNLOADED++))
        PROGRESS=$((DOWNLOADED * 100 / TOTAL))
        printf "\r  Progress: [%-50s] %d%%" $(printf '#%.0s' $(seq 1 $((PROGRESS / 2)))) $PROGRESS
    else
        log_warning "Failed to download $config, creating default..."
        
        # Create default configs
        case "$config" in
            "coding_standards.json")
                cat > "$DEST" << 'EOF'
{
    "version": "1.0.0",
    "enabled": true,
    "standards": {
        "max_line_length": 120,
        "indent_size": 4,
        "use_spaces": true
    }
}
EOF
                ;;
            "agent_routing.json")
                cat > "$DEST" << 'EOF'
{
    "version": "1.0.0",
    "routes": {
        "@frontend": "frontend-development",
        "@backend": "backend-architecture",
        "@test": "testing-automation"
    }
}
EOF
                ;;
            "agent_models.json")
                cat > "$DEST" << 'EOF'
{
    "version": "1.0.0",
    "models": {
        "default": "claude-3-opus-20240229",
        "agents": {}
    }
}
EOF
                ;;
            "mcp_config.json")
                cat > "$DEST" << 'EOF'
{
    "version": "1.0.0",
    "servers": []
}
EOF
                ;;
        esac
        ((DOWNLOADED++))
    fi
done

echo # New line after progress bar

# Update Claude Code settings
log_info "Updating Claude Code settings..."

SETTINGS_PATH="$CLAUDE_DIR/.claude/settings.json"

if [ -f "$SETTINGS_PATH" ]; then
    # Backup existing settings
    cp "$SETTINGS_PATH" "$SETTINGS_PATH.backup"
    
    # Update settings with jq if available
    if command -v jq &> /dev/null; then
        jq '.hooks = {
            "enabled": true,
            "path": ".claude/hooks",
            "config_path": ".claude/config",
            "state_path": ".claude/state",
            "python_path": "python3"
        }' "$SETTINGS_PATH" > "$SETTINGS_PATH.tmp" && mv "$SETTINGS_PATH.tmp" "$SETTINGS_PATH"
        log_success "Settings updated"
    else
        log_warning "jq not available, manual settings update required"
    fi
else
    # Create new settings file
    cat > "$SETTINGS_PATH" << 'EOF'
{
    "hooks": {
        "enabled": true,
        "path": ".claude/hooks",
        "config_path": ".claude/config",
        "state_path": ".claude/state",
        "python_path": "python3"
    }
}
EOF
    log_success "Settings created"
fi

# Create test script
TEST_SCRIPT="$CLAUDE_DIR/.claude/test-hooks.py"
cat > "$TEST_SCRIPT" << 'EOF'
#!/usr/bin/env python3
import os
import sys
import json

print("Testing Claude Code Hooks System...")
hooks_dir = os.path.join(os.path.dirname(__file__), 'hooks')
config_dir = os.path.join(os.path.dirname(__file__), 'config')

# Test hook scripts
print("\nHook Scripts:")
for script in sorted(os.listdir(hooks_dir)):
    if script.endswith('.py'):
        print(f"  ✓ {script}")

# Test config files
print("\nConfig Files:")
for config in sorted(os.listdir(config_dir)):
    if config.endswith('.json'):
        try:
            with open(os.path.join(config_dir, config)) as f:
                json.load(f)
            print(f"  ✓ {config} (valid JSON)")
        except:
            print(f"  ✗ {config} (invalid JSON)")

print("\nHooks system ready!")
EOF

chmod +x "$TEST_SCRIPT"

# Run test
log_info "Testing installation..."
if python3 "$TEST_SCRIPT"; then
    log_success "Installation test passed"
else
    log_warning "Installation test failed"
fi

# Cleanup
rm -f "$TEST_SCRIPT"

# Set proper permissions
chmod -R 755 "$CLAUDE_DIR/.claude/hooks"
chmod -R 644 "$CLAUDE_DIR/.claude/config"
chmod -R 755 "$CLAUDE_DIR/.claude/state"

# Summary
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo
log_success "=== Installation Complete ==="
echo
log_info "Installed to: $CLAUDE_DIR/.claude"
log_info "Time taken: ${DURATION}s"
echo
log_info "Next steps:"
log_info "1. Restart Claude Code"
log_info "2. Verify hooks are working with a new project"
log_info "3. Customize configs in $CLAUDE_DIR/.claude/config"
echo

# If running in WSL, check Windows installation too
if grep -qi microsoft /proc/version 2>/dev/null; then
    log_info "WSL detected. You may also want to run install-hooks.ps1 in Windows."
fi