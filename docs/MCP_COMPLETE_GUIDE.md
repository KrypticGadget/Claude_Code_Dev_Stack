# Claude Code Complete MCP Integration Guide

## Overview
This comprehensive guide covers the installation and configuration of three essential MCP (Model Context Protocol) servers for Claude Code:

1. **Playwright MCP** - Browser automation and web scraping
2. **Obsidian MCP** - Note-taking and knowledge management integration  
3. **Web-search MCP** - Free web searching without API keys

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Individual Server Setup](#individual-server-setup)
  - [Playwright MCP](#playwright-mcp)
  - [Obsidian MCP](#obsidian-mcp)
  - [Web-search MCP](#web-search-mcp)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Usage Examples](#usage-examples)

## Prerequisites

### Required for All Servers
- **Node.js 18+** - [Download](https://nodejs.org)
- **Claude Code CLI** - [Installation Guide](https://docs.anthropic.com/claude-code)

### Additional Requirements

| Server | Requirements |
|--------|-------------|
| Playwright | None (uses npx) |
| Obsidian | Python 3.8+, UV package manager, Obsidian with REST API plugin |
| Web-search | Git (optional), npm |

## Quick Start

### Automated Installation (All Three Servers)

```powershell
# One-line installer
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/mcp/master-mcp-setup.ps1 | iex

# Or download and run with options
curl -O https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/mcp/master-mcp-setup.ps1
.\master-mcp-setup.ps1 -ObsidianApiKey "your_api_key_here"
```

### Manual Quick Commands

```powershell
# Install all three servers quickly
claude mcp add playwright -- cmd /c npx '@playwright/mcp@latest' --headless
claude mcp add obsidian --env OBSIDIAN_API_KEY=YOUR_KEY -- cmd /c uvx mcp-obsidian
claude mcp add web-search -- cmd /c node "%USERPROFILE%\mcp-servers\web-search\build\index.js"
```

## Individual Server Setup

### Playwright MCP

**Purpose**: Browser automation, web scraping, visual testing, form filling

#### Installation Commands

```powershell
# Basic headless installation (recommended for automation)
claude mcp add playwright -- cmd /c npx '@playwright/mcp@latest' --headless

# Headed mode (see browser window)
claude mcp add playwright-headed -- cmd /c npx '@playwright/mcp@latest'

# Mobile emulation
claude mcp add playwright-mobile -- cmd /c npx '@playwright/mcp@latest' --device='iPhone 15'

# Custom viewport with Chrome
claude mcp add playwright-chrome -- cmd /c npx '@playwright/mcp@latest' --browser=chrome --viewport-size=1920,1080

# Full featured with vision and PDF
claude mcp add playwright-full -- cmd /c npx '@playwright/mcp@latest' --caps=vision,pdf --save-session --save-trace
```

#### Configuration Options

```powershell
# All available options
--browser <browser>          # chrome, firefox, webkit, msedge
--headless                   # Run without UI
--device <device>           # Device emulation: "iPhone 15", "Pixel 5", etc.
--viewport-size <size>      # Custom viewport: "1920,1080"
--caps <caps>              # Additional capabilities: vision,pdf
--proxy-server <proxy>     # Proxy server: "http://proxy:8080"
--ignore-https-errors      # Ignore SSL certificate errors
--user-agent <string>      # Custom user agent
--isolated                 # Isolated browser sessions
--save-session            # Save session logs
--save-trace             # Save Playwright traces
--output-dir <path>      # Output directory for files
```

#### Test Command

```powershell
claude "Use playwright to navigate to https://example.com and extract the main heading"
```

### Obsidian MCP

**Purpose**: Read/write notes, search vault, manage knowledge base

#### Prerequisites

1. **Install Obsidian REST API Plugin**:
   - Open Obsidian → Settings → Community Plugins
   - Search for "Local REST API"
   - Install and enable the plugin
   - Copy the API key from plugin settings

2. **Install Python and UV**:
```powershell
# Install UV (if Python is installed)
pip install uv

# Or use standalone installer
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### Installation Commands

```powershell
# With environment variables
claude mcp add obsidian --env OBSIDIAN_API_KEY=your_api_key_here --env OBSIDIAN_HOST=127.0.0.1 --env OBSIDIAN_PORT=27124 -- cmd /c uvx mcp-obsidian

# If uvx is not in PATH, use full path
$uvxPath = (Get-Command uvx).Source
claude mcp add obsidian --env OBSIDIAN_API_KEY=your_api_key --env OBSIDIAN_HOST=127.0.0.1 --env OBSIDIAN_PORT=27124 -- cmd /c "`"$uvxPath`"" mcp-obsidian
```

#### Available Tools

| Tool | Description |
|------|-------------|
| `list_files_in_vault` | List all files in vault root |
| `list_files_in_dir` | List files in specific directory |
| `get_file_contents` | Read file content |
| `search` | Search across all files |
| `patch_content` | Insert content relative to headings/blocks |
| `append_content` | Append to new or existing file |
| `delete_file` | Delete file or directory |

#### Test Command

```powershell
claude "Use obsidian to list all files in the vault and count how many notes I have"
```

### Web-search MCP

**Purpose**: Free web searching without API keys, Google search results

#### Installation Commands

```powershell
# Clone and build (recommended)
git clone https://github.com/pskill9/web-search.git "$env:USERPROFILE\mcp-servers\web-search"
cd "$env:USERPROFILE\mcp-servers\web-search"
npm install
npm run build

# Add to Claude Code
claude mcp add web-search -- cmd /c node "%USERPROFILE%\mcp-servers\web-search\build\index.js"
```

#### Alternative Installation (without Git)

```powershell
# Download as ZIP
$zipUrl = "https://github.com/pskill9/web-search/archive/refs/heads/main.zip"
$zipPath = "$env:TEMP\web-search.zip"
Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath

# Extract
Expand-Archive -Path $zipPath -DestinationPath "$env:USERPROFILE\mcp-servers" -Force
Move-Item "$env:USERPROFILE\mcp-servers\web-search-main" "$env:USERPROFILE\mcp-servers\web-search" -Force

# Build
cd "$env:USERPROFILE\mcp-servers\web-search"
npm install
npm run build

# Add to Claude Code
claude mcp add web-search -- cmd /c node "%USERPROFILE%\mcp-servers\web-search\build\index.js"
```

#### Search Parameters

```json
{
  "query": "your search query",
  "limit": 5  // Number of results (max 10)
}
```

#### Test Command

```powershell
claude "Use web-search to find the latest news about artificial intelligence"
```

## Testing

### Individual Server Tests

```powershell
# Test Playwright
claude "Use playwright to go to https://www.google.com and tell me what's in the search box placeholder"

# Test Obsidian (ensure Obsidian is running)
claude "Use obsidian to search for notes containing the word 'meeting'"

# Test Web-search
claude "Use web-search to find information about Model Context Protocol MCP"
```

### Combined Usage Tests

```powershell
# Web research workflow
claude "Use web-search to find articles about 'prompt engineering best practices', then use playwright to visit the first result and extract the main content, finally use obsidian to save a summary in a new note called 'Prompt Engineering Research.md'"

# Data extraction and storage
claude "Use playwright to go to https://news.ycombinator.com, extract the top 5 stories with their points and comments, then save this data to my Obsidian vault in a note called 'HN Top Stories - [today's date].md'"
```

## Troubleshooting

### Common Issues and Solutions

#### All Servers

**Issue**: "claude" command not recognized
```powershell
# Verify Claude Code is installed
claude --version

# If not found, check PATH or reinstall Claude Code
```

**Issue**: MCP server already exists
```powershell
# Remove and reinstall
claude mcp remove [server-name]
claude mcp add [server-name] -- [command]
```

#### Playwright Specific

**Issue**: Browser doesn't launch
```powershell
# Install browsers
npx playwright install

# Use system Chrome
claude mcp add playwright -- cmd /c npx '@playwright/mcp@latest' --browser=chrome --executable-path="C:\Program Files\Google\Chrome\Application\chrome.exe"
```

**Issue**: Timeout errors
```powershell
# Use headless mode for better performance
claude mcp add playwright -- cmd /c npx '@playwright/mcp@latest' --headless
```

#### Obsidian Specific

**Issue**: Connection refused
- Ensure Obsidian is running
- Check REST API plugin is enabled
- Verify API key is correct
- Check firewall settings for port 27124

**Issue**: UV/UVX not found
```powershell
# Install UV globally
pip install --user uv

# Or specify full path
where uvx  # Find the path
claude mcp add obsidian --env OBSIDIAN_API_KEY=key -- cmd /c "C:\full\path\to\uvx.exe" mcp-obsidian
```

#### Web-search Specific

**Issue**: Build fails
```powershell
# Clean install
cd "$env:USERPROFILE\mcp-servers\web-search"
Remove-Item node_modules -Recurse -Force
npm cache clean --force
npm install
npm run build
```

**Issue**: Rate limiting from Google
- Add delays between searches
- Reduce search frequency
- Use specific, targeted queries

### Verification Commands

```powershell
# List all installed MCP servers
claude mcp list

# Check specific server status
claude mcp status playwright
claude mcp status obsidian
claude mcp status web-search

# View server logs (if available)
Get-Content "$env:LOCALAPPDATA\Claude\logs\mcp-*.log" -Tail 20
```

## Usage Examples

### Web Scraping and Analysis

```powershell
# Extract structured data
claude "Use playwright to go to a real estate website and extract the first 10 property listings with prices, locations, and descriptions into a table format"

# Monitor prices
claude "Use playwright to check the price of a specific product on Amazon and tell me if it's on sale"
```

### Knowledge Management

```powershell
# Daily notes workflow
claude "Use obsidian to create a new daily note with today's date, add a template with sections for Tasks, Notes, and Reflections"

# Research organization
claude "Use obsidian to search for all notes tagged with #project and create a summary document linking to each one"
```

### Research Automation

```powershell
# Comprehensive research
claude "I need to research 'quantum computing applications'. Use web-search to find 5 recent articles, use playwright to visit each and extract key points, then compile everything into an Obsidian note with proper citations"

# Competitive analysis
claude "Use web-search to find my competitor's website, then use playwright to analyze their pricing page and save the information to Obsidian"
```

### Development Workflows

```powershell
# API documentation extraction
claude "Use playwright to go to an API documentation page, extract all endpoints with their methods and descriptions, format as markdown"

# Testing form validation
claude "Use playwright to test the contact form on my website - try submitting with invalid email, empty fields, and valid data, report what happens"
```

## Advanced Configuration

### Environment Variables

Create a `.env` file for persistent configuration:

```env
# Obsidian Configuration
OBSIDIAN_API_KEY=your_api_key_here
OBSIDIAN_HOST=127.0.0.1
OBSIDIAN_PORT=27124

# Playwright Configuration
PLAYWRIGHT_BROWSER=chrome
PLAYWRIGHT_HEADLESS=true
```

### Custom Scripts

Create specialized configurations for different use cases:

```powershell
# development.ps1 - Development environment
claude mcp add playwright-dev -- cmd /c npx '@playwright/mcp@latest' --browser=chrome
claude mcp add obsidian-dev --env OBSIDIAN_API_KEY=$env:OBSIDIAN_API_KEY -- cmd /c uvx mcp-obsidian

# production.ps1 - Production environment
claude mcp add playwright-prod -- cmd /c npx '@playwright/mcp@latest' --headless --caps=vision,pdf
```

## Performance Optimization

### Best Practices

1. **Playwright**
   - Use headless mode for automation
   - Enable browser caching
   - Reuse browser contexts when possible

2. **Obsidian**
   - Keep vault size manageable
   - Use specific search queries
   - Organize notes in folders

3. **Web-search**
   - Cache search results
   - Use specific keywords
   - Implement rate limiting

### Resource Management

```powershell
# Monitor MCP server resources
Get-Process | Where-Object {$_.ProcessName -match "node|chrome|firefox"} | Select-Object ProcessName, CPU, WS

# Clean up orphaned processes
Get-Process chrome | Where-Object {$_.MainWindowTitle -eq ""} | Stop-Process
```

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Web Scraping**: Respect robots.txt and terms of service
3. **Rate Limiting**: Implement delays to avoid being blocked
4. **Data Privacy**: Be cautious with sensitive information in notes
5. **Firewall**: Obsidian REST API opens port 27124 - configure firewall accordingly

## Support and Resources

- **Playwright MCP**: [GitHub Repository](https://github.com/microsoft/playwright-mcp)
- **Obsidian MCP**: [GitHub Repository](https://github.com/MarkusPfundstein/mcp-obsidian)
- **Web-search MCP**: [GitHub Repository](https://github.com/pskill9/web-search)
- **Claude Code Docs**: [Official Documentation](https://docs.anthropic.com/claude-code)
- **MCP Specification**: [modelcontextprotocol.io](https://modelcontextprotocol.io)

## Contributing

To contribute improvements to this guide:

1. Fork the repository
2. Create a feature branch
3. Test all commands thoroughly
4. Submit a pull request with:
   - Clear description of changes
   - Test results
   - Any new dependencies

---

*Last Updated: January 2025*  
*Tested with: Claude Code 1.x, Playwright MCP 0.0.32, Obsidian MCP latest, Web-search MCP latest*