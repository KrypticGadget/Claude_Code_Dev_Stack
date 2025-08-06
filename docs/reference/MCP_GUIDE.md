# MCP (Model Context Protocol) Guide - Claude Code Dev Stack

## Overview

The Claude Code Dev Stack uses a minimal set of 3 essential MCPs that cover 95% of development needs:
- **Playwright** - Browser automation and testing
- **Obsidian** - Knowledge management
- **Brave Search** - Web research

## Why Only 3 MCPs?

### The 3-5 MCP Rule
Based on real-world usage patterns:
- **90% of tasks** need only these 3 MCPs
- **More MCPs = More complexity** without proportional benefit
- **Agents handle the logic**, MCPs handle external connections

### What These 3 Cover
- **Testing**: Playwright handles all browser-based testing
- **Knowledge**: Obsidian manages your documentation and notes
- **Research**: Brave Search provides current information

### What You DON'T Need
❌ File system MCP - Claude Code already has file access
❌ Git MCP - Use Claude Code's built-in git integration
❌ Multiple database MCPs - Your agents handle SQL generation
❌ Dozens of API MCPs - Most APIs work better through agents

## Installation

### Quick Start (All Platforms)
```bash
# 1. Playwright
claude mcp add playwright npx '@playwright/mcp@latest'

# 2. Brave Search (requires API key)
claude mcp add brave-search --env BRAVE_API_KEY=YOUR_KEY \
  -- npx -y @modelcontextprotocol/server-brave-search

# 3. Obsidian (requires desktop app)
# In Claude Code:
/ide
# Select "Obsidian" from the list
```

### Windows-Specific Commands
```bash
# Windows users must use cmd wrapper:
claude mcp add playwright -- cmd /c npx '@playwright/mcp@latest'

claude mcp add brave-search --env BRAVE_API_KEY=YOUR_KEY \
  -- cmd /c npx -y @modelcontextprotocol/server-brave-search
```

## The 3 Essential MCPs

### 1. Playwright 🎭
**Purpose**: Browser automation, web scraping, UI testing
**When it activates**: Testing web apps, scraping data, automating browser tasks
**Documentation**: https://github.com/microsoft/playwright-mcp

**Example usage**:
```
"Use playwright mcp to test the login flow on our staging site"
"Open example.com and take a screenshot of the homepage"
"Fill out the contact form and verify the success message"
```

**Key features**:
- Visible browser mode for manual authentication
- Cross-browser testing (Chrome, Firefox, Safari)
- Network interception and console access
- Screenshot and video recording
- Mobile device emulation
- 25 available tools for complete browser control

**Authentication tip**: Since the browser is visible, you can manually log in when needed:
```
"Open the admin panel"
# Manually enter credentials in the browser
"Now test the dashboard features"
```

### 2. Obsidian 📝
**Purpose**: Access your knowledge base, project documentation, notes
**When it activates**: Retrieving project context, updating documentation
**Documentation**: https://github.com/iansinnott/obsidian-claude-code-mcp

**Example usage**:
```
"Find my notes about the API architecture in Obsidian"
"Update the project roadmap in my Obsidian vault"
"What did I document about the authentication flow?"
```

**Requirements**:
- Obsidian desktop app must be running
- Install plugin from Community Plugins
- HTTP API server enabled (default port: 22360)
- Vault must be open

**Multiple vaults**: Configure unique ports for each vault in Obsidian settings

### 3. Brave Search 🔍
**Purpose**: Real-time web research, finding current information
**When it activates**: Researching solutions, checking documentation, finding packages
**Documentation**: https://docs.brave.com/search-api/mcp

**Example usage**:
```
"Search for the latest React best practices using brave search"
"Find recent security vulnerabilities for package X"
"What's the current recommended way to implement OAuth2?"
```

**Setup**:
1. Get API key from https://brave.com/search/api/
2. Free tier includes 2,000 queries/month
3. Data for AI plans available for higher usage

**Search operators**:
- `site:` - Search specific sites
- `filetype:` - Find specific file types
- `"exact phrase"` - Exact match
- `-exclude` - Exclude terms

## Integration with the 4-Stack System

### How MCPs Work with Agents
```
User: "Test our checkout flow"
↓
@agent-testing-automation: "I'll test the checkout"
↓
Playwright MCP: Opens browser, runs tests
↓
@agent-quality-assurance: "3 issues found"
```

### Automatic Activation
You don't invoke MCPs directly. They activate when needed:
- Mention "test the website" → Playwright activates
- Ask about "my notes" → Obsidian activates  
- Request "search for" → Brave activates

### With Hooks
Hooks can monitor MCP usage:
```json
{
  "PreToolUse": [{
    "matcher": "mcp__playwright__.*",
    "hooks": [{
      "command": "echo 'Browser test started' >> test.log"
    }]
  }]
}
```

## Configuration Management

### Check Status
```bash
# List all MCPs
claude mcp list

# Within Claude Code
/mcp

# Get details
claude mcp get playwright
```

### Remove and Reinstall
```bash
# Remove
claude mcp remove playwright

# Reinstall
claude mcp add playwright npx '@playwright/mcp@latest'
```

### Scopes
- **Local** (default): Project-specific, private
- **Project**: Shared via `.mcp.json`
- **User**: Available across all projects

```bash
# Add globally
claude mcp add --scope user playwright npx '@playwright/mcp@latest'
```

## Best Practices

### 1. Let Context Guide MCP Usage
Don't force MCP mentions. Natural language works:
- ✅ "Test the login page"
- ❌ "Use playwright mcp to test login"

### 2. Combine with Agents
MCPs work best with agent expertise:
```
@agent-testing-automation @agent-security-architect
"Run security tests on our web app"
# Playwright MCP will activate automatically
```

### 3. Use for External Tasks Only
- ✅ Browser automation (Playwright)
- ✅ Searching the web (Brave)
- ✅ Accessing notes (Obsidian)
- ❌ File operations (use Claude Code)
- ❌ Code analysis (use agents)

## Troubleshooting

### Common Issues

**MCP not found**:
- Ensure Claude Code CLI is in PATH
- Restart terminal after installation
- Check `claude mcp list`

**Playwright Issues**:
- Browser not opening: Check headless mode setting
- Timeouts: Increase timeout values
- Elements not found: Add wait conditions

**Obsidian Connection Failed**:
- Is Obsidian desktop running?
- HTTP server enabled in plugin?
- Port 22360 available?
- Firewall blocking local connections?

**Brave Search No Results**:
- API key valid and has quota?
- Rate limits exceeded?
- Try more specific search terms

**Windows Specific**:
- Always use `cmd /c` wrapper for npx
- Consider WSL for better compatibility
- Use nvm instead of node installer

## Summary

The Claude Code Dev Stack's 3-MCP approach:
- **Playwright** - All browser automation needs
- **Obsidian** - Your knowledge management
- **Brave Search** - Current information lookup

This minimal set integrates perfectly with your 28 agents, 18 commands, and 13 hooks to create a powerful yet simple development environment.

Remember: **Agents think, MCPs connect, Hooks automate, Commands accelerate.**