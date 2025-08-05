#!/bin/bash
# Tier 1 MCP Installer for Ubuntu/WSL
# Installs: Playwright MCP, Obsidian MCP, and Brave Search MCP
# Global installation at Claude Code root level

set -e

echo -e "\033[36m=== Tier 1 MCP Global Installer for Claude Code ===\033[0m"
echo -e "\033[33mInstalling: Playwright, Obsidian, and Brave Search MCPs\033[0m"
echo -e "\033[32mInstallation Type: GLOBAL (Available in all projects)\033[0m"
echo ""

# Check for Claude CLI
echo -e "\033[32m[1/6] Checking Claude CLI installation...\033[0m"
if command -v claude >/dev/null 2>&1; then
    CLAUDE_VERSION=$(claude --version 2>&1 || echo "version unknown")
    echo -e "  \033[90m✓ Claude CLI detected: $CLAUDE_VERSION\033[0m"
else
    echo -e "  \033[31m✗ Claude CLI not found. Please install Claude Code first.\033[0m"
    echo -e "  \033[33mDownload from: https://claude.ai/download\033[0m"
    exit 1
fi

# Check for Node.js and npm
echo ""
echo -e "\033[32m[2/6] Checking Node.js/npm installation...\033[0m"
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
echo -e "\033[32m[3/6] Detecting Claude Code installation...\033[0m"

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

# Create global MCP directory at Claude Code root
MCP_DIR="$CLAUDE_CODE_PATH/mcp"
mkdir -p "$MCP_DIR"
echo -e "  \033[90m✓ Created global MCP directory: $MCP_DIR\033[0m"

# Install Tier 1 MCPs using Claude CLI
echo ""
echo -e "\033[32m[4/6] Installing Tier 1 MCPs globally...\033[0m"

# Define MCPs with their commands
declare -A MCP_COMMANDS=(
    ["playwright"]="claude mcp add playwright npx @playwright/mcp@latest"
    ["obsidian"]="claude mcp add obsidian npx @kreateworld/mcp-obsidian@latest"
    ["brave-search"]="claude mcp add brave-search npx @modelcontextprotocol/server-brave-search@latest"
)

declare -A MCP_NAMES=(
    ["playwright"]="Playwright MCP"
    ["obsidian"]="Obsidian MCP"
    ["brave-search"]="Brave Search MCP"
)

declare -A MCP_DESCRIPTIONS=(
    ["playwright"]="Browser testing and UI automation"
    ["obsidian"]="Knowledge management and documentation"
    ["brave-search"]="Web research and market analysis"
)

INSTALLED_COUNT=0
for mcp_id in "playwright" "obsidian" "brave-search"; do
    echo ""
    echo -e "  \033[33mInstalling ${MCP_NAMES[$mcp_id]}...\033[0m"
    echo -e "  \033[90mPurpose: ${MCP_DESCRIPTIONS[$mcp_id]}\033[0m"
    
    # Execute Claude MCP add command
    if ${MCP_COMMANDS[$mcp_id]} >/dev/null 2>&1; then
        echo -e "  \033[32m✓ ${MCP_NAMES[$mcp_id]} installed globally\033[0m"
        ((INSTALLED_COUNT++))
        
        # Create subdirectory for this MCP
        mkdir -p "$MCP_DIR/$mcp_id"
    else
        echo -e "  \033[31m✗ Failed to install ${MCP_NAMES[$mcp_id]}\033[0m"
        echo -e "  \033[33mYou can manually install with: ${MCP_COMMANDS[$mcp_id]}\033[0m"
    fi
done

# Create global MCP configuration
echo ""
echo -e "\033[32m[5/6] Creating global MCP configuration...\033[0m"

# Create mcp-config.json
MCP_CONFIG_PATH="$CLAUDE_CODE_PATH/mcp-config.json"
cat > "$MCP_CONFIG_PATH" <<EOF
{
  "version": "1.0",
  "global": true,
  "mcps": {
    "playwright": {
      "name": "playwright",
      "command": "npx",
      "args": ["@playwright/mcp@latest"],
      "description": "Browser testing and UI automation",
      "enabled": true
    },
    "obsidian": {
      "name": "obsidian",
      "command": "npx",
      "args": ["@kreateworld/mcp-obsidian@latest"],
      "description": "Knowledge management and documentation",
      "enabled": true
    },
    "brave-search": {
      "name": "brave-search",
      "command": "npx",
      "args": ["@modelcontextprotocol/server-brave-search@latest"],
      "description": "Web research and market analysis",
      "enabled": true
    }
  },
  "installation_date": "$(date +'%Y-%m-%d %H:%M:%S')",
  "installed_count": $INSTALLED_COUNT
}
EOF

echo -e "  \033[90m✓ Created global MCP configuration: $MCP_CONFIG_PATH\033[0m"

# Update Claude Code settings
echo ""
echo -e "\033[32m[6/6] Updating Claude Code global settings...\033[0m"

# Create temporary file for JSON processing
TEMP_SETTINGS=$(mktemp)

# Ensure settings file exists with valid JSON
if [ -f "$SETTINGS_PATH" ]; then
    cp "$SETTINGS_PATH" "$TEMP_SETTINGS"
else
    echo '{}' > "$TEMP_SETTINGS"
fi

# Update settings using Python (more reliable JSON handling)
python3 - <<EOF
import json
import sys

try:
    # Read existing settings
    with open('$TEMP_SETTINGS', 'r') as f:
        content = f.read().strip()
        settings = json.loads(content) if content else {}
    
    # Update global MCP settings
    if 'globalSettings' not in settings:
        settings['globalSettings'] = {}
    
    settings['globalSettings']['mcpEnabled'] = True
    settings['globalSettings']['mcpDirectory'] = '$MCP_DIR'
    settings['globalSettings']['mcpConfigPath'] = '$MCP_CONFIG_PATH'
    settings['globalSettings']['mcpToolLimit'] = 5
    
    # Note: MCPs are now managed globally by Claude CLI
    if 'mcpServers' not in settings:
        settings['mcpServers'] = {
            "_comment": "MCPs are now managed globally via 'claude mcp' commands"
        }
    
    # Write updated settings
    with open('$SETTINGS_PATH', 'w') as f:
        json.dump(settings, f, indent=2)
    
    print("success")
except Exception as e:
    print(f"error: {e}")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo -e "  \033[90m✓ Claude Code global settings updated successfully\033[0m"
else
    echo -e "  \033[31m✗ Failed to update settings\033[0m"
fi

# Cleanup
rm -f "$TEMP_SETTINGS"

echo ""
echo -e "\033[32m✅ Tier 1 MCPs global installation complete!\033[0m"
echo ""
echo -e "\033[36mInstalled $INSTALLED_COUNT/3 MCPs globally:\033[0m"
echo -e "  • Playwright MCP - Browser testing and UI automation"
echo -e "  • Obsidian MCP - Knowledge management and documentation"
echo -e "  • Brave Search MCP - Web research and market analysis"
echo ""
echo -e "\033[33mGlobal MCP Directory: $MCP_DIR\033[0m"
echo -e "\033[33mGlobal Configuration: $MCP_CONFIG_PATH\033[0m"
echo ""
echo -e "\033[32m⚡ MCPs are now available in ALL projects!\033[0m"
echo -e "\033[33mPlease restart Claude Code to activate the MCPs.\033[0m"