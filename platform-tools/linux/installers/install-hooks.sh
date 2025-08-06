#!/bin/bash
# Claude Code Hooks System Global Installer for Ubuntu/WSL
# Version: 2.0.0
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
log_info "=== Claude Code Hooks System Global Installer ==="
echo

START_TIME=$(date +%s)

# Check Python installation
log_info "Checking Python installation..."
PYTHON_CMD=""
PYTHON_PATH=""

# Try different Python commands
for cmd in python3 python; do
    if command -v $cmd &> /dev/null; then
        PYTHON_VERSION=$($cmd --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
        MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [[ $MAJOR -eq 3 && $MINOR -ge 8 ]]; then
            PYTHON_CMD="$cmd"
            PYTHON_PATH=$(which $cmd)
            log_success "Python $($cmd --version 2>&1) found at: $PYTHON_PATH"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    log_error "Python 3.8+ not found. Install with: sudo apt update && sudo apt install python3"
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

# Check if running in WSL
IS_WSL=false
if grep -qi microsoft /proc/version 2>/dev/null; then
    IS_WSL=true
    log_info "WSL detected"
fi

# Try to find Claude executable first
CLAUDE_EXE=""
CLAUDE_ROOT=""

# Check for Claude in PATH
if command -v claude &> /dev/null; then
    CLAUDE_EXE=$(which claude)
    CLAUDE_ROOT=$(dirname $(dirname "$CLAUDE_EXE"))
    log_success "Found Claude executable in PATH: $CLAUDE_EXE"
fi

# If not found and in WSL, check Windows paths
if [ -z "$CLAUDE_EXE" ] && [ "$IS_WSL" = true ]; then
    # Get Windows username
    WIN_USER=$(cmd.exe /c "echo %USERNAME%" 2>/dev/null | tr -d '\r\n')
    
    WINDOWS_PATHS=(
        "/mnt/c/Users/$WIN_USER/AppData/Local/Programs/Claude/Claude.exe"
        "/mnt/c/Program Files/Claude/Claude.exe"
        "/mnt/c/Program Files (x86)/Claude/Claude.exe"
    )
    
    for path in "${WINDOWS_PATHS[@]}"; do
        if [ -f "$path" ]; then
            CLAUDE_EXE="$path"
            CLAUDE_ROOT=$(dirname $(dirname "$path"))
            log_success "Found Claude executable at: $CLAUDE_EXE"
            break
        fi
    done
fi

# Fall back to config directory detection
if [ -z "$CLAUDE_ROOT" ]; then
    CLAUDE_PATHS=(
        "$HOME/.claude"
        "$HOME/.config/Claude"
        "$HOME/.local/share/Claude"
    )
    
    if [ "$IS_WSL" = true ]; then
        WIN_USER=$(cmd.exe /c "echo %USERNAME%" 2>/dev/null | tr -d '\r\n')
        CLAUDE_PATHS+=(
            "/mnt/c/Users/$WIN_USER/.claude"
            "/mnt/c/Users/$WIN_USER/AppData/Roaming/Claude"
            "/mnt/c/Users/$WIN_USER/AppData/Local/Claude"
        )
    fi
    
    for path in "${CLAUDE_PATHS[@]}"; do
        if [ -d "$path" ]; then
            CLAUDE_ROOT="$path"
            break
        fi
    done
fi

if [ -z "$CLAUDE_ROOT" ]; then
    log_warning "Claude Code installation not found automatically."
    echo "Please enter Claude Code root directory path:"
    read -r CLAUDE_ROOT
    if [ ! -d "$CLAUDE_ROOT" ]; then
        log_error "Invalid path: $CLAUDE_ROOT"
        exit 1
    fi
fi

log_success "Using Claude Code root: $CLAUDE_ROOT"

# Create global hooks directory
GLOBAL_HOOKS_DIR="$CLAUDE_ROOT/.claude-global"
log_info "Creating global hooks directory at: $GLOBAL_HOOKS_DIR"

DIRECTORIES=(
    "$GLOBAL_HOOKS_DIR/hooks"
    "$GLOBAL_HOOKS_DIR/config"
    "$GLOBAL_HOOKS_DIR/state"
)

for dir in "${DIRECTORIES[@]}"; do
    mkdir -p "$dir"
    if [ "${VERBOSE:-false}" = "true" ]; then
        log_info "  Created: $dir"
    fi
done

log_success "Directory structure created"

# Set up environment variables
log_info "Setting up environment variables..."

# Add to user's shell profile
SHELL_PROFILE=""
if [ -f "$HOME/.bashrc" ]; then
    SHELL_PROFILE="$HOME/.bashrc"
elif [ -f "$HOME/.bash_profile" ]; then
    SHELL_PROFILE="$HOME/.bash_profile"
elif [ -f "$HOME/.profile" ]; then
    SHELL_PROFILE="$HOME/.profile"
fi

if [ -n "$SHELL_PROFILE" ]; then
    # Check if already added
    if ! grep -q "CLAUDE_HOME" "$SHELL_PROFILE"; then
        cat >> "$SHELL_PROFILE" << EOF

# Claude Code Hooks System
export CLAUDE_HOME="$CLAUDE_ROOT"
export CLAUDE_PYTHON="$PYTHON_PATH"
export CLAUDE_HOOKS_DIR="\$CLAUDE_HOME/.claude-global/hooks"
EOF
        log_success "Environment variables added to $SHELL_PROFILE"
    else
        log_info "Environment variables already configured"
    fi
    
    # Export for current session
    export CLAUDE_HOME="$CLAUDE_ROOT"
    export CLAUDE_PYTHON="$PYTHON_PATH"
    export CLAUDE_HOOKS_DIR="$CLAUDE_HOME/.claude-global/hooks"
else
    log_warning "Could not find shell profile to update"
    log_info "Please add these to your shell profile:"
    echo "export CLAUDE_HOME=\"$CLAUDE_ROOT\""
    echo "export CLAUDE_PYTHON=\"$PYTHON_PATH\""
    echo "export CLAUDE_HOOKS_DIR=\"\$CLAUDE_HOME/.claude-global/hooks\""
fi

# Download files
BASE_URL="https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main"

# Hook scripts to download
HOOK_SCRIPTS=(
    "base_hook.py"
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
    URL="$BASE_URL/.claude-example/hooks/$script"
    DEST="$GLOBAL_HOOKS_DIR/hooks/$script"
    
    if curl -sS -f -o "$DEST" "$URL" 2>/dev/null; then
        chmod +x "$DEST"
        ((DOWNLOADED++))
        PROGRESS=$((DOWNLOADED * 100 / TOTAL))
        printf "\r  Progress: [%-50s] %d%%" $(printf '#%.0s' $(seq 1 $((PROGRESS / 2)))) $PROGRESS
    else
        echo # New line
        log_warning "Failed to download $script, creating default..."
        
        # Special handling for base_hook.py
        if [ "$script" = "base_hook.py" ]; then
            cat > "$DEST" << 'EOF'
#!/usr/bin/env python3
"""
Base Hook - Foundation for all Claude Code hooks
"""

import json
import sys
import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseHook(ABC):
    def __init__(self, hook_name: str):
        self.hook_name = hook_name
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format=f'[{self.hook_name}] %(levelname)s: %(message)s'
        )
        return logging.getLogger(self.hook_name)
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> int:
        pass
    
    def run(self) -> int:
        try:
            context = json.loads(os.environ.get('CLAUDE_HOOK_CONTEXT', '{}'))
            return self.execute(context)
        except Exception as e:
            self.logger.error(f"Hook execution failed: {e}")
            return 1
EOF
        else
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
        fi
        chmod +x "$DEST"
        ((DOWNLOADED++))
    fi
done

echo # New line after progress bar

log_info "Downloading config files..."

for config in "${CONFIG_FILES[@]}"; do
    URL="$BASE_URL/.claude-example/config/$config"
    DEST="$GLOBAL_HOOKS_DIR/config/$config"
    
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

# Find and update Claude Code settings
log_info "Updating Claude Code settings..."

# Look for settings.json in various locations
SETTINGS_PATHS=(
    "$CLAUDE_ROOT/settings.json"
    "$CLAUDE_ROOT/.claude/settings.json"
    "$HOME/.config/Claude/settings.json"
    "$HOME/.claude/settings.json"
)

if [ "$IS_WSL" = true ]; then
    WIN_USER=$(cmd.exe /c "echo %USERNAME%" 2>/dev/null | tr -d '\r\n')
    SETTINGS_PATHS+=(
        "/mnt/c/Users/$WIN_USER/AppData/Roaming/Claude/settings.json"
        "/mnt/c/Users/$WIN_USER/AppData/Local/Claude/settings.json"
    )
fi

SETTINGS_PATH=""
for path in "${SETTINGS_PATHS[@]}"; do
    if [ -f "$path" ]; then
        SETTINGS_PATH="$path"
        break
    fi
done

# Create default settings path if none found
if [ -z "$SETTINGS_PATH" ]; then
    SETTINGS_PATH="$CLAUDE_ROOT/settings.json"
fi

# Backup existing settings
if [ -f "$SETTINGS_PATH" ]; then
    cp "$SETTINGS_PATH" "$SETTINGS_PATH.backup"
fi

# Update settings with jq if available, otherwise use Python
if command -v jq &> /dev/null; then
    # Create temporary file with new settings
    if [ -f "$SETTINGS_PATH" ]; then
        jq '.hooks = {
            "enabled": true,
            "global_path": env.CLAUDE_HOME + "/.claude-global",
            "hooks_command": "\"" + env.CLAUDE_PYTHON + "\" \"" + env.CLAUDE_HOME + "/.claude-global/hooks/{hook_name}.py\"",
            "config_path": env.CLAUDE_HOME + "/.claude-global/config",
            "state_path": env.CLAUDE_HOME + "/.claude-global/state",
            "environment": {
                "CLAUDE_HOME": "$CLAUDE_HOME",
                "CLAUDE_PYTHON": "$CLAUDE_PYTHON",
                "CLAUDE_HOOKS_DIR": "$CLAUDE_HOME/.claude-global/hooks"
            }
        }' "$SETTINGS_PATH" > "$SETTINGS_PATH.tmp" && mv "$SETTINGS_PATH.tmp" "$SETTINGS_PATH"
    else
        # Create new settings file
        jq -n '{
            "hooks": {
                "enabled": true,
                "global_path": env.CLAUDE_HOME + "/.claude-global",
                "hooks_command": "\"" + env.CLAUDE_PYTHON + "\" \"" + env.CLAUDE_HOME + "/.claude-global/hooks/{hook_name}.py\"",
                "config_path": env.CLAUDE_HOME + "/.claude-global/config",
                "state_path": env.CLAUDE_HOME + "/.claude-global/state",
                "environment": {
                    "CLAUDE_HOME": "$CLAUDE_HOME",
                    "CLAUDE_PYTHON": "$CLAUDE_PYTHON",
                    "CLAUDE_HOOKS_DIR": "$CLAUDE_HOME/.claude-global/hooks"
                }
            }
        }' > "$SETTINGS_PATH"
    fi
    log_success "Settings updated with jq"
else
    # Use Python to update settings
    $PYTHON_CMD << EOF
import json
import os

settings_path = "$SETTINGS_PATH"
claude_home = "$CLAUDE_ROOT"
claude_python = "$PYTHON_PATH"

try:
    with open(settings_path, 'r') as f:
        settings = json.load(f)
except:
    settings = {}

settings['hooks'] = {
    "enabled": True,
    "global_path": f"\$CLAUDE_HOME/.claude-global",
    "hooks_command": f'"\$CLAUDE_PYTHON" "\$CLAUDE_HOME/.claude-global/hooks/{{hook_name}}.py"',
    "config_path": f"\$CLAUDE_HOME/.claude-global/config",
    "state_path": f"\$CLAUDE_HOME/.claude-global/state",
    "environment": {
        "CLAUDE_HOME": "\$CLAUDE_HOME",
        "CLAUDE_PYTHON": "\$CLAUDE_PYTHON",
        "CLAUDE_HOOKS_DIR": "\$CLAUDE_HOME/.claude-global/hooks"
    }
}

with open(settings_path, 'w') as f:
    json.dump(settings, f, indent=4)

print("Settings updated with Python")
EOF
    log_success "Settings updated"
fi

log_info "Settings file location: $SETTINGS_PATH"

# Create test script
TEST_SCRIPT="$GLOBAL_HOOKS_DIR/test-hooks.py"
cat > "$TEST_SCRIPT" << 'EOF'
#!/usr/bin/env python3
import os
import sys
import json

print("Testing Claude Code Global Hooks System...")
base_dir = os.path.dirname(__file__)
hooks_dir = os.path.join(base_dir, 'hooks')
config_dir = os.path.join(base_dir, 'config')

# Test environment variables
print("\nEnvironment Variables:")
claude_home = os.environ.get('CLAUDE_HOME', 'NOT SET')
claude_python = os.environ.get('CLAUDE_PYTHON', 'NOT SET')
print(f"  CLAUDE_HOME: {claude_home}")
print(f"  CLAUDE_PYTHON: {claude_python}")

# Test hook scripts
print("\nHook Scripts:")
if os.path.exists(hooks_dir):
    for script in sorted(os.listdir(hooks_dir)):
        if script.endswith('.py'):
            print(f"  ✓ {script}")
else:
    print(f"  ✗ Hooks directory not found: {hooks_dir}")

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
    print(f"  ✗ Config directory not found: {config_dir}")

print("\nGlobal hooks system ready!")
print(f"Installation path: {base_dir}")
EOF

chmod +x "$TEST_SCRIPT"

# Run test
log_info "Testing installation..."
if $PYTHON_CMD "$TEST_SCRIPT"; then
    log_success "Installation test passed"
else
    log_warning "Installation test failed"
fi

# Test hook execution with spaces in path
log_info "Testing hook execution with spaces in path..."
TEST_PROJECT_PATH="/tmp/Test Project With Spaces"
mkdir -p "$TEST_PROJECT_PATH"
TEST_HOOK_CMD="\"$PYTHON_PATH\" \"$GLOBAL_HOOKS_DIR/hooks/session_loader.py\""
log_info "Test command: $TEST_HOOK_CMD"
rm -rf "$TEST_PROJECT_PATH"

# Cleanup
rm -f "$TEST_SCRIPT"

# Set proper permissions
chmod -R 755 "$GLOBAL_HOOKS_DIR/hooks"
chmod -R 644 "$GLOBAL_HOOKS_DIR/config"
chmod -R 755 "$GLOBAL_HOOKS_DIR/state"

# Summary
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo
log_success "=== Global Installation Complete ==="
echo
log_info "Installed to: $GLOBAL_HOOKS_DIR"
log_info "Settings file: $SETTINGS_PATH"
log_info "Time taken: ${DURATION}s"
echo
log_info "Environment variables configured:"
log_info "  CLAUDE_HOME=$CLAUDE_ROOT"
log_info "  CLAUDE_PYTHON=$PYTHON_PATH"
log_info "  CLAUDE_HOOKS_DIR=$GLOBAL_HOOKS_DIR/hooks"
echo
log_info "Next steps:"
log_info "1. Restart your terminal or run: source $SHELL_PROFILE"
log_info "2. Restart Claude Code"
log_info "3. Create or open any project - hooks will work globally"
log_info "4. Customize configs in $GLOBAL_HOOKS_DIR/config"
echo

# If running in WSL, provide Windows-specific info
if [ "$IS_WSL" = true ]; then
    log_info "WSL Notes:"
    log_info "- Hooks installed for WSL environment"
    log_info "- For native Windows support, run install-hooks.ps1 in PowerShell"
    log_info "- Settings may be shared between WSL and Windows"
fi