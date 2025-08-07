#!/bin/bash
# Master MCP Setup Script for Claude Code Dev Stack (Linux/WSL)
# Installs and configures Playwright, Obsidian, and Web-search MCP servers

cat << 'EOF'
==================================
 Claude Code MCP Server Setup v2.1
==================================
EOF

# Configuration
CLAUDE_DIR="$HOME/.claude"
MCP_CONFIG="$CLAUDE_DIR/.mcp.json"
NODE_MIN_VERSION="18.0.0"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# Parse command-line arguments
OBSIDIAN_API_KEY=""
SKIP_PLAYWRIGHT=false
SKIP_OBSIDIAN=false
SKIP_WEBSEARCH=false
UNINSTALL=false
TEST=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --obsidian-api-key)
            OBSIDIAN_API_KEY="$2"
            shift 2
            ;;
        --skip-playwright)
            SKIP_PLAYWRIGHT=true
            shift
            ;;
        --skip-obsidian)
            SKIP_OBSIDIAN=true
            shift
            ;;
        --skip-websearch)
            SKIP_WEBSEARCH=true
            shift
            ;;
        --uninstall)
            UNINSTALL=true
            shift
            ;;
        --test)
            TEST=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --obsidian-api-key KEY    Set Obsidian API key"
            echo "  --skip-playwright         Skip Playwright installation"
            echo "  --skip-obsidian          Skip Obsidian installation"
            echo "  --skip-websearch         Skip Web-search installation"
            echo "  --uninstall              Remove all MCP servers"
            echo "  --test                   Test MCP server connectivity"
            echo "  --help                   Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Function to check Node.js version
check_node_version() {
    if ! command -v node &> /dev/null; then
        echo -e "${RED}✗ Node.js not found${NC}"
        echo -e "${YELLOW}  Please install Node.js ${NODE_MIN_VERSION} or higher${NC}"
        echo -e "${GRAY}  Install with: curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt-get install -y nodejs${NC}"
        return 1
    fi
    
    NODE_VERSION=$(node -v | cut -d'v' -f2)
    if [ "$(printf '%s\n' "$NODE_MIN_VERSION" "$NODE_VERSION" | sort -V | head -n1)" = "$NODE_MIN_VERSION" ]; then
        echo -e "${GREEN}✓ Node.js $NODE_VERSION found${NC}"
        return 0
    else
        echo -e "${RED}✗ Node.js version $NODE_VERSION is too old${NC}"
        echo -e "${YELLOW}  Please upgrade to Node.js ${NODE_MIN_VERSION} or higher${NC}"
        return 1
    fi
}

# Function to install MCP server
install_mcp_server() {
    local SERVER_NAME=$1
    local NPM_PACKAGE=$2
    local CONFIG_JSON=$3
    
    echo -e "\n${CYAN}Installing $SERVER_NAME MCP server...${NC}"
    
    # Check if already installed
    if npm list -g "$NPM_PACKAGE" &> /dev/null; then
        echo -e "${YELLOW}  $SERVER_NAME already installed, updating...${NC}"
    fi
    
    # Install/update the package
    if npm install -g "$NPM_PACKAGE" &> /dev/null; then
        echo -e "${GREEN}  ✓ $SERVER_NAME installed successfully${NC}"
    else
        echo -e "${RED}  ✗ Failed to install $SERVER_NAME${NC}"
        return 1
    fi
    
    return 0
}

# Function to uninstall MCP servers
uninstall_mcp_servers() {
    echo -e "\n${YELLOW}Uninstalling MCP servers...${NC}"
    
    # Uninstall Playwright
    if npm list -g @modelcontextprotocol/server-playwright &> /dev/null; then
        npm uninstall -g @modelcontextprotocol/server-playwright &> /dev/null
        echo -e "${GREEN}  ✓ Playwright MCP server removed${NC}"
    fi
    
    # Uninstall Obsidian
    if npm list -g mcp-obsidian &> /dev/null; then
        npm uninstall -g mcp-obsidian &> /dev/null
        echo -e "${GREEN}  ✓ Obsidian MCP server removed${NC}"
    fi
    
    # Uninstall Web-search
    if npm list -g mcp-websearch &> /dev/null; then
        npm uninstall -g mcp-websearch &> /dev/null
        echo -e "${GREEN}  ✓ Web-search MCP server removed${NC}"
    fi
    
    # Remove MCP configuration
    if [ -f "$MCP_CONFIG" ]; then
        rm "$MCP_CONFIG"
        echo -e "${GREEN}  ✓ MCP configuration removed${NC}"
    fi
    
    echo -e "${GREEN}✓ All MCP servers have been uninstalled${NC}"
    exit 0
}

# Function to test MCP servers
test_mcp_servers() {
    echo -e "\n${CYAN}Testing MCP server connectivity...${NC}"
    
    # Test Playwright
    if command -v mcp-playwright &> /dev/null; then
        echo -e "${GREEN}  ✓ Playwright MCP server found${NC}"
    else
        echo -e "${YELLOW}  ⚠ Playwright MCP server not found${NC}"
    fi
    
    # Test Obsidian
    if command -v mcp-obsidian &> /dev/null; then
        echo -e "${GREEN}  ✓ Obsidian MCP server found${NC}"
    else
        echo -e "${YELLOW}  ⚠ Obsidian MCP server not found${NC}"
    fi
    
    # Test Web-search
    if command -v mcp-websearch &> /dev/null; then
        echo -e "${GREEN}  ✓ Web-search MCP server found${NC}"
    else
        echo -e "${YELLOW}  ⚠ Web-search MCP server not found${NC}"
    fi
    
    # Check configuration
    if [ -f "$MCP_CONFIG" ]; then
        echo -e "${GREEN}  ✓ MCP configuration file exists${NC}"
        echo -e "${GRAY}    Location: $MCP_CONFIG${NC}"
    else
        echo -e "${YELLOW}  ⚠ MCP configuration file not found${NC}"
    fi
    
    exit 0
}

# Main execution
echo -e "\n${YELLOW}🔍 Checking prerequisites...${NC}"

# Handle uninstall flag
if [ "$UNINSTALL" = true ]; then
    uninstall_mcp_servers
fi

# Handle test flag
if [ "$TEST" = true ]; then
    test_mcp_servers
fi

# Check Node.js
if ! check_node_version; then
    exit 1
fi

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}✗ npm not found${NC}"
    echo -e "${YELLOW}  npm should come with Node.js installation${NC}"
    exit 1
fi
echo -e "${GREEN}✓ npm $(npm -v) found${NC}"

# Create Claude directory if it doesn't exist
mkdir -p "$CLAUDE_DIR"

# Install MCP servers
INSTALLED_COUNT=0
FAILED_COUNT=0

# Install Playwright MCP
if [ "$SKIP_PLAYWRIGHT" = false ]; then
    if install_mcp_server "Playwright" "@modelcontextprotocol/server-playwright" ""; then
        ((INSTALLED_COUNT++))
    else
        ((FAILED_COUNT++))
    fi
else
    echo -e "${GRAY}Skipping Playwright installation${NC}"
fi

# Install Obsidian MCP
if [ "$SKIP_OBSIDIAN" = false ]; then
    if [ -z "$OBSIDIAN_API_KEY" ]; then
        echo -e "\n${YELLOW}⚠ Obsidian API key not provided${NC}"
        echo -e "${GRAY}  Use --obsidian-api-key to set it later${NC}"
    fi
    
    if install_mcp_server "Obsidian" "mcp-obsidian" ""; then
        ((INSTALLED_COUNT++))
    else
        ((FAILED_COUNT++))
    fi
else
    echo -e "${GRAY}Skipping Obsidian installation${NC}"
fi

# Install Web-search MCP
if [ "$SKIP_WEBSEARCH" = false ]; then
    if install_mcp_server "Web-search" "mcp-websearch" ""; then
        ((INSTALLED_COUNT++))
    else
        ((FAILED_COUNT++))
    fi
else
    echo -e "${GRAY}Skipping Web-search installation${NC}"
fi

# Create MCP configuration
echo -e "\n${CYAN}Creating MCP configuration...${NC}"

cat > "$MCP_CONFIG" << 'CONFIG_EOF'
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-playwright"],
      "description": "Browser automation and testing"
    },
    "obsidian": {
      "command": "npx",
      "args": ["mcp-obsidian"],
      "env": {
        "OBSIDIAN_API_KEY": "PLACEHOLDER_API_KEY"
      },
      "description": "Note-taking and knowledge management"
    },
    "websearch": {
      "command": "npx",
      "args": ["mcp-websearch"],
      "description": "Web search capabilities"
    }
  }
}
CONFIG_EOF

# Update Obsidian API key if provided
if [ -n "$OBSIDIAN_API_KEY" ]; then
    if command -v jq &> /dev/null; then
        jq ".mcpServers.obsidian.env.OBSIDIAN_API_KEY = \"$OBSIDIAN_API_KEY\"" "$MCP_CONFIG" > "$MCP_CONFIG.tmp" && mv "$MCP_CONFIG.tmp" "$MCP_CONFIG"
        echo -e "${GREEN}  ✓ Obsidian API key configured${NC}"
    else
        # Fallback without jq
        sed -i "s/PLACEHOLDER_API_KEY/$OBSIDIAN_API_KEY/g" "$MCP_CONFIG"
        echo -e "${GREEN}  ✓ Obsidian API key configured${NC}"
    fi
fi

echo -e "${GREEN}  ✓ MCP configuration created at: $MCP_CONFIG${NC}"

# Installation summary
echo -e "\n${CYAN}════════════════════════════════════════════════════════════${NC}"
echo -e "  ${WHITE}MCP SERVER INSTALLATION COMPLETE${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"

echo -e "\n${CYAN}📊 Installation Summary:${NC}"
echo -e "  ${WHITE}• Servers installed: $INSTALLED_COUNT${NC}"
if [ $FAILED_COUNT -gt 0 ]; then
    echo -e "  ${RED}• Failed installations: $FAILED_COUNT${NC}"
fi

echo -e "\n${CYAN}🔌 Available MCP Servers:${NC}"
if [ "$SKIP_PLAYWRIGHT" = false ] && [ $INSTALLED_COUNT -gt 0 ]; then
    echo -e "  ${WHITE}• Playwright - Browser automation${NC}"
fi
if [ "$SKIP_OBSIDIAN" = false ] && [ $INSTALLED_COUNT -gt 0 ]; then
    echo -e "  ${WHITE}• Obsidian - Note management${NC}"
    if [ -z "$OBSIDIAN_API_KEY" ]; then
        echo -e "    ${YELLOW}⚠ API key needed for full functionality${NC}"
    fi
fi
if [ "$SKIP_WEBSEARCH" = false ] && [ $INSTALLED_COUNT -gt 0 ]; then
    echo -e "  ${WHITE}• Web-search - Internet search${NC}"
fi

echo -e "\n${YELLOW}📝 Next Steps:${NC}"
echo -e "  ${WHITE}1. Restart Claude Code to load MCP servers${NC}"
if [ -z "$OBSIDIAN_API_KEY" ]; then
    echo -e "  ${WHITE}2. Set Obsidian API key in: $MCP_CONFIG${NC}"
fi
echo -e "  ${WHITE}3. Test with: $0 --test${NC}"

echo -e "\n${CYAN}💡 Usage Examples:${NC}"
echo -e "  ${GRAY}# Test MCP servers${NC}"
echo -e "  ${WHITE}$0 --test${NC}"
echo -e ""
echo -e "  ${GRAY}# Update Obsidian API key${NC}"
echo -e "  ${WHITE}$0 --obsidian-api-key \"your-key-here\"${NC}"
echo -e ""
echo -e "  ${GRAY}# Uninstall all MCP servers${NC}"
echo -e "  ${WHITE}$0 --uninstall${NC}"

echo -e "\n${GREEN}✨ MCP servers are ready to enhance Claude Code!${NC}"

exit 0