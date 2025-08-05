#!/bin/bash
# Tier 1 MCP Installer for Ubuntu/WSL
# Installs: Playwright MCP, Obsidian MCP, and Brave Search MCP

set -e

echo -e "\033[36m=== Tier 1 MCP Installer for Claude Code ===\033[0m"
echo -e "\033[33mInstalling: Playwright, Obsidian, and Brave Search MCPs\033[0m"
echo ""

# Check for Node.js and npm
echo -e "\033[32m[1/5] Checking Node.js/npm installation...\033[0m"
if command -v node >/dev/null 2>&1 && command -v npm >/dev/null 2>&1; then
    NODE_VERSION=$(node --version)
    NPM_VERSION=$(npm --version)
    echo -e "  \033[90m✓ Node.js $NODE_VERSION detected\033[0m"
    echo -e "  \033[90m✓ npm v$NPM_VERSION detected\033[0m"
else
    echo -e "  \033[31m✗ Node.js/npm not found. Please install Node.js first.\033[0m"
    echo -e "  \033[33mInstall with: sudo apt-get update && sudo apt-get install nodejs npm\033[0m"
    exit 1
fi

# Detect Claude Code installation path
echo ""
echo -e "\033[32m[2/5] Detecting Claude Code installation...\033[0m"

# Common paths for Claude Code on Linux/WSL
CLAUDE_CODE_PATHS=(
    "$HOME/.config/Claude"
    "$HOME/.local/share/Claude"
    "$HOME/AppData/Roaming/Claude"  # WSL accessing Windows
    "$HOME/AppData/Local/Claude"     # WSL accessing Windows
    "/mnt/c/Users/$USER/AppData/Roaming/Claude"  # WSL
    "/mnt/c/Users/$USER/AppData/Local/Claude"    # WSL
)

CLAUDE_CODE_PATH=""
SETTINGS_PATH=""

for path in "${CLAUDE_CODE_PATHS[@]}"; do
    if [ -f "$path/claude_desktop_config.json" ]; then
        CLAUDE_CODE_PATH="$path"
        SETTINGS_PATH="$path/claude_desktop_config.json"
        break
    fi
done

if [ -z "$CLAUDE_CODE_PATH" ]; then
    echo -e "  \033[31m✗ Claude Code installation not found\033[0m"
    echo -e "  \033[33mPlease ensure Claude Code is installed\033[0m"
    exit 1
fi

echo -e "  \033[90m✓ Found Claude Code at: $CLAUDE_CODE_PATH\033[0m"

# Create MCP directory
MCP_DIR="$CLAUDE_CODE_PATH/mcp"
mkdir -p "$MCP_DIR"

# Install Tier 1 MCPs
echo ""
echo -e "\033[32m[3/5] Installing Tier 1 MCPs...\033[0m"

declare -A MCPS=(
    ["@modelcontextprotocol/server-playwright"]="Playwright MCP"
    ["@kreateworld/mcp-obsidian"]="Obsidian MCP"
    ["@modelcontextprotocol/server-brave-search"]="Brave Search MCP"
)

for package in "${!MCPS[@]}"; do
    display_name="${MCPS[$package]}"
    echo -e "  \033[33mInstalling $display_name...\033[0m"
    if npm install -g "$package" >/dev/null 2>&1; then
        echo -e "  \033[90m✓ $display_name installed successfully\033[0m"
    else
        echo -e "  \033[31m✗ Failed to install $display_name\033[0m"
        # Continue with other installations
    fi
done

# Download tier1-universal.json configuration
echo ""
echo -e "\033[32m[4/5] Downloading MCP configuration...\033[0m"
CONFIG_URL="https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/mcp-configs/tier1-universal.json"
CONFIG_PATH="$MCP_DIR/tier1-universal.json"

if curl -s -o "$CONFIG_PATH" "$CONFIG_URL"; then
    echo -e "  \033[90m✓ Configuration downloaded successfully\033[0m"
else
    echo -e "  \033[31m✗ Failed to download configuration\033[0m"
    exit 1
fi

# Update Claude Code settings
echo ""
echo -e "\033[32m[5/5] Updating Claude Code settings...\033[0m"

# Create temporary file for JSON processing
TEMP_SETTINGS=$(mktemp)
TEMP_CONFIG=$(mktemp)

# Ensure settings file exists with valid JSON
if [ -f "$SETTINGS_PATH" ]; then
    cp "$SETTINGS_PATH" "$TEMP_SETTINGS"
else
    echo '{}' > "$TEMP_SETTINGS"
fi

# Merge configurations using Python (more reliable JSON handling)
python3 - <<EOF
import json
import sys

try:
    # Read existing settings
    with open('$TEMP_SETTINGS', 'r') as f:
        content = f.read().strip()
        settings = json.loads(content) if content else {}
    
    # Read tier1 configuration
    with open('$CONFIG_PATH', 'r') as f:
        tier1_config = json.load(f)
    
    # Ensure mcpServers section exists
    if 'mcpServers' not in settings:
        settings['mcpServers'] = {}
    
    # Merge MCP configurations
    if 'mcpServers' in tier1_config:
        settings['mcpServers'].update(tier1_config['mcpServers'])
    
    # Write updated settings
    with open('$SETTINGS_PATH', 'w') as f:
        json.dump(settings, f, indent=2)
    
    print("success")
except Exception as e:
    print(f"error: {e}")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo -e "  \033[90m✓ Claude Code settings updated successfully\033[0m"
else
    echo -e "  \033[31m✗ Failed to update settings\033[0m"
    exit 1
fi

# Cleanup
rm -f "$TEMP_SETTINGS" "$TEMP_CONFIG"

echo ""
echo -e "\033[32m✅ Tier 1 MCPs installation complete!\033[0m"
echo ""
echo -e "\033[36mInstalled MCPs:\033[0m"
echo -e "  • Playwright MCP - Web automation and testing"
echo -e "  • Obsidian MCP - Note-taking integration"
echo -e "  • Brave Search MCP - Web search capabilities"
echo ""
echo -e "\033[33mPlease restart Claude Code to activate the MCPs.\033[0m"