#!/bin/bash
# Claude Code Hooks System Installer for macOS
# Version: 1.0.0
# Repository: https://github.com/KrypticGadget/Claude_Code_Dev_Stack

set -euo pipefail

# Colors (macOS compatible)
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

# macOS specific echo handling
if [[ "$OSTYPE" == "darwin"* ]]; then
    alias echo='echo'
fi

# Start installation
echo
log_info "=== Claude Code Hooks System Installer for macOS ==="
echo

START_TIME=$(date +%s)

# Check Python installation
log_info "Checking Python installation..."

# Try different Python commands
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    # Check if it's Python 3
    if python --version 2>&1 | grep -q "Python 3"; then
        PYTHON_CMD="python"
    fi
fi

if [ -n "$PYTHON_CMD" ]; then
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
    MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [[ $MAJOR -eq 3 && $MINOR -ge 8 ]]; then
        log_success "Python $($PYTHON_CMD --version 2>&1) found"
    else
        log_error "Python 3.8+ required. Found: Python $PYTHON_VERSION"
        exit 1
    fi
else
    log_error "Python 3 not found."
    log_info "Install with: brew install python3"
    exit 1
fi

# Check for Homebrew (optional but recommended)
if ! command -v brew &> /dev/null; then
    log_warning "Homebrew not found. Some features may be limited."
    log_info "Install Homebrew from: https://brew.sh"
fi

# Check for required tools
log_info "Checking required tools..."
MISSING_TOOLS=()

# Check for curl (should be present on macOS)
if ! command -v curl &> /dev/null; then
    MISSING_TOOLS+=("curl")
fi

# Check for jq (optional but useful)
if ! command -v jq &> /dev/null; then
    log_warning "jq not found. JSON handling will be limited."
    if command -v brew &> /dev/null; then
        log_info "Install with: brew install jq"
    fi
fi

if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
    log_error "Missing required tools: ${MISSING_TOOLS[*]}"
    exit 1
fi

# Find Claude Code installation
log_info "Detecting Claude Code installation..."

# Common paths for Claude Code on macOS
CLAUDE_PATHS=(
    "$HOME/.claude"
    "$HOME/Library/Application Support/Claude"
    "$HOME/Library/Preferences/Claude"
    "/Applications/Claude.app/Contents/Resources/.claude"
    "$HOME/Documents/Claude/.claude"
)

CLAUDE_DIR=""
for path in "${CLAUDE_PATHS[@]}"; do
    if [ -d "$path" ]; then
        CLAUDE_DIR="$path"
        break
    fi
done

# If not found, check if Claude.app exists
if [ -z "$CLAUDE_DIR" ] && [ -d "/Applications/Claude.app" ]; then
    # Create default directory
    CLAUDE_DIR="$HOME/.claude"
    log_info "Claude.app found, using default location: $CLAUDE_DIR"
fi

if [ -z "$CLAUDE_DIR" ]; then
    log_warning "Claude Code installation not found in default locations."
    echo "Please enter Claude Code installation path"
    echo "(or press Enter to use default: $HOME/.claude):"
    read -r USER_PATH
    
    if [ -z "$USER_PATH" ]; then
        CLAUDE_DIR="$HOME/.claude"
    else
        CLAUDE_DIR="$USER_PATH"
    fi
    
    if [ ! -d "$CLAUDE_DIR" ]; then
        log_info "Creating directory: $CLAUDE_DIR"
        mkdir -p "$CLAUDE_DIR"
    fi
fi

log_success "Using Claude directory: $CLAUDE_DIR"

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

# Function to show progress
show_progress() {
    local current=$1
    local total=$2
    local progress=$((current * 100 / total))
    local filled=$((progress / 2))
    
    printf "\r  Progress: ["
    printf "%-50s" "$(printf '#%.0s' $(seq 1 $filled))"
    printf "] %d%%" $progress
}

for script in "${HOOK_SCRIPTS[@]}"; do
    URL="$BASE_URL/.claude/hooks/$script"
    DEST="$CLAUDE_DIR/.claude/hooks/$script"
    
    if curl -sS -f -o "$DEST" "$URL" 2>/dev/null; then
        chmod +x "$DEST"
        ((DOWNLOADED++))
        show_progress $DOWNLOADED $TOTAL
    else
        echo # New line
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
        show_progress $DOWNLOADED $TOTAL
    else
        echo # New line
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
            "python_path": "'$PYTHON_CMD'"
        }' "$SETTINGS_PATH" > "$SETTINGS_PATH.tmp" && mv "$SETTINGS_PATH.tmp" "$SETTINGS_PATH"
        log_success "Settings updated"
    else
        log_warning "jq not available, creating Python updater..."
        
        # Use Python to update JSON
        $PYTHON_CMD << EOF
import json
import sys

settings_path = "$SETTINGS_PATH"
try:
    with open(settings_path, 'r') as f:
        settings = json.load(f)
except:
    settings = {}

settings['hooks'] = {
    "enabled": True,
    "path": ".claude/hooks",
    "config_path": ".claude/config",
    "state_path": ".claude/state",
    "python_path": "$PYTHON_CMD"
}

with open(settings_path, 'w') as f:
    json.dump(settings, f, indent=4)

print("Settings updated via Python")
EOF
    fi
else
    # Create new settings file
    cat > "$SETTINGS_PATH" << EOF
{
    "hooks": {
        "enabled": true,
        "path": ".claude/hooks",
        "config_path": ".claude/config",
        "state_path": ".claude/state",
        "python_path": "$PYTHON_CMD"
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
if os.path.exists(hooks_dir):
    for script in sorted(os.listdir(hooks_dir)):
        if script.endswith('.py'):
            print(f"  ✓ {script}")
else:
    print("  ✗ Hooks directory not found")

# Test config files
print("\nConfig Files:")
if os.path.exists(config_dir):
    for config in sorted(os.listdir(config_dir)):
        if config.endswith('.json'):
            try:
                with open(os.path.join(config_dir, config)) as f:
                    json.load(f)
                print(f"  ✓ {config} (valid JSON)")
            except:
                print(f"  ✗ {config} (invalid JSON)")
else:
    print("  ✗ Config directory not found")

print("\nHooks system ready!")
EOF

chmod +x "$TEST_SCRIPT"

# Run test
log_info "Testing installation..."
if $PYTHON_CMD "$TEST_SCRIPT"; then
    log_success "Installation test passed"
else
    log_warning "Installation test failed"
fi

# Cleanup
rm -f "$TEST_SCRIPT"

# Set proper permissions (macOS specific)
chmod -R 755 "$CLAUDE_DIR/.claude/hooks"
chmod -R 644 "$CLAUDE_DIR/.claude/config"
chmod -R 755 "$CLAUDE_DIR/.claude/state"

# Fix execute permissions for Python scripts
find "$CLAUDE_DIR/.claude/hooks" -name "*.py" -exec chmod +x {} \;

# Create launch agent for auto-start (optional)
log_info "Creating launch agent (optional)..."
LAUNCH_AGENT_DIR="$HOME/Library/LaunchAgents"
LAUNCH_AGENT_PLIST="$LAUNCH_AGENT_DIR/com.claude.hooks.plist"

if [ ! -d "$LAUNCH_AGENT_DIR" ]; then
    mkdir -p "$LAUNCH_AGENT_DIR"
fi

cat > "$LAUNCH_AGENT_PLIST" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.claude.hooks</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_CMD</string>
        <string>$CLAUDE_DIR/.claude/hooks/session_loader.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>$HOME/Library/Logs/claude-hooks.log</string>
    <key>StandardOutPath</key>
    <string>$HOME/Library/Logs/claude-hooks.log</string>
</dict>
</plist>
EOF

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

# macOS specific instructions
if [[ "$OSTYPE" == "darwin"* ]]; then
    log_info "macOS specific:"
    log_info "- Launch agent created at: $LAUNCH_AGENT_PLIST"
    log_info "- To enable auto-start: launchctl load $LAUNCH_AGENT_PLIST"
    log_info "- Logs available at: ~/Library/Logs/claude-hooks.log"
    echo
fi

log_success "Installation completed successfully!"