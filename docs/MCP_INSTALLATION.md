# MCP (Model Context Protocol) Installation Guide

MCPs enable Claude Code to connect with external tools and services. The Claude Code Dev Stack uses 3 essential MCPs.

## Prerequisites
- Claude Code CLI installed and in PATH
- Node.js and npm installed
- For Brave Search: API key from https://brave.com/search/api/
- For Obsidian: Desktop app installed and running

## Quick Installation

Run these commands in your terminal after installing Claude Code:

```bash
# 1. Playwright - Browser automation and testing
claude mcp add playwright npx '@playwright/mcp@latest'

# 2. Brave Search - Web research (requires API key)
claude mcp add brave-search --env BRAVE_API_KEY=YOUR_KEY \
  -- npx -y @modelcontextprotocol/server-brave-search

# 3. Obsidian - Knowledge management (requires Obsidian desktop app running)
# For Claude Code, it auto-discovers running vaults:
claude
> /ide
> Select "Obsidian" from the list
```

## Verify Installation

```bash
# List all configured MCP servers
claude mcp list

# Check status within Claude Code
/mcp
```

## Individual MCP Details

### Playwright MCP 🎭
**Purpose**: Browser automation, web scraping, UI testing
**Documentation**: https://github.com/microsoft/playwright-mcp
**No authentication required**

**Available Tools** (25 total):
- `browser_navigate` - Navigate to URLs
- `browser_click` - Click elements
- `browser_type` - Type text
- `browser_take_screenshot` - Capture screenshots
- `browser_wait_for` - Wait for elements
- `browser_file_upload` - Upload files
- `browser_console_messages` - Read console
- And 18 more...

**Usage Examples**:
```
"Use playwright mcp to open example.com and take a screenshot"
"Test the login flow on our staging site"
"Fill out the contact form and verify success"
```

**Tips**:
- Browser window is visible, allowing manual authentication
- Cookies persist for the session duration
- Explicitly say "playwright mcp" the first time

### Brave Search MCP 🔍
**Purpose**: Web search and research
**Documentation**: https://docs.brave.com/search-api/mcp
**Requires**: Brave API key

**Setup**:
1. Get API key from https://brave.com/search/api/
2. Free tier: 2,000 queries/month
3. Data for AI plans available for more queries

**Usage Examples**:
```
"Search for recent React best practices using brave search"
"Find the latest security vulnerabilities for package X"
"What's the current recommended OAuth2 implementation?"
```

### Obsidian MCP 📝
**Purpose**: Access and manage your knowledge base
**Documentation**: https://github.com/iansinnott/obsidian-claude-code-mcp
**Requires**: Obsidian desktop app running with plugin enabled

**Setup**:
1. Install Obsidian plugin from Community Plugins
2. Enable HTTP server (default port: 22360)
3. Plugin serves both WebSocket (Claude Code) and HTTP/SSE (Claude Desktop)

**Configuration**:
- Default port: 22360
- Custom ports for multiple vaults
- Auto-discovery via WebSocket

**Usage Examples**:
```
"Find my notes about API architecture in Obsidian"
"Update the project roadmap in my vault"
"What did I document about authentication?"
```

## Windows-Specific Notes

Windows users must use cmd wrapper for npx commands:
```bash
# Example for Brave Search on Windows
claude mcp add brave-search --env BRAVE_API_KEY=YOUR_KEY \
  -- cmd /c npx -y @modelcontextprotocol/server-brave-search

# Playwright on Windows
claude mcp add playwright -- cmd /c npx '@playwright/mcp@latest'
```

**Common Windows Issues**:
- Use cmd /c wrapper for all npx commands
- Consider using WSL for better compatibility
- Use nvm instead of node installer for MCP compatibility

## Claude Desktop Configuration

Claude Desktop requires `mcp-remote` bridge for HTTP connections:

### Config Location:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### Example Configuration:
```json
{
  "mcpServers": {
    "obsidian": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:22360/sse"],
      "env": {}
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "YOUR_API_KEY_HERE"
      }
    },
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"],
      "env": {}
    }
  }
}
```

## Configuration Management

### Scopes:
- **Local** (default): Project-specific, private to you
- **Project**: Shared via `.mcp.json` in repo
- **User**: Available across all projects

```bash
# Add with specific scope
claude mcp add playwright --scope user npx '@playwright/mcp@latest'

# Remove and reinstall
claude mcp remove playwright
claude mcp add playwright npx '@playwright/mcp@latest'
```

## Troubleshooting

### Connection Issues
- Ensure Claude Code is in PATH: `where claude` (Windows) or `which claude` (Mac/Linux)
- For Obsidian: Make sure desktop app is running
- For Brave: Verify API key is valid
- Check firewall settings for local connections

### Playwright Issues
- **Browser not opening**: Check if running in headless mode
- **Timeouts**: Increase timeout in operations
- **Can't find elements**: Ensure page fully loaded

### Obsidian Connection Failed
- Check Obsidian is running
- Verify HTTP server enabled
- Check port availability (default 22360)
- Multiple vaults need unique ports

### Brave Search No Results
- Verify API key and quota
- Check rate limits
- Use more specific search terms

## Important Notes

- MCPs are managed through Claude Code CLI, not manual file installation
- Configuration stored in `~/.claude.json` (global) or `.mcp.json` (project)
- MCPs are available across all projects once installed globally
- You only need to install them once per machine
- Session persists until Claude Code is restarted