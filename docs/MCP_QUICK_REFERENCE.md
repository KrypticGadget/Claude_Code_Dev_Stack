# MCP Quick Reference Card

## 🚀 One-Line Installation

```powershell
# Install all three MCP servers
iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/mcp/master-mcp-setup.ps1 | iex
```

## 📦 Individual Installations

### Playwright (Browser Automation)
```powershell
# Headless (recommended)
claude mcp add playwright -- cmd /c npx '@playwright/mcp@latest' --headless

# With browser window
claude mcp add playwright -- cmd /c npx '@playwright/mcp@latest'
```

### Obsidian (Note Management)
```powershell
# First: Install REST API plugin in Obsidian, get API key
# Then:
claude mcp add obsidian --env OBSIDIAN_API_KEY=YOUR_KEY -- cmd /c uvx mcp-obsidian
```

### Web-search (Free Google Search)
```powershell
# Quick install (requires Git)
git clone https://github.com/pskill9/web-search.git "$env:USERPROFILE\mcp-servers\web-search"
cd "$env:USERPROFILE\mcp-servers\web-search" && npm install && npm run build
claude mcp add web-search -- cmd /c node "%USERPROFILE%\mcp-servers\web-search\build\index.js"
```

## 🧪 Test Commands

```powershell
# Test Playwright
claude "Use playwright to go to example.com and get the page title"

# Test Obsidian (Obsidian must be running)
claude "Use obsidian to list all files in the vault"

# Test Web-search
claude "Use web-search to find information about Claude AI"

# Combined test
claude "Use web-search to find news about AI, then use playwright to visit the first link"
```

## 🛠️ Management Commands

```powershell
# List all MCP servers
claude mcp list

# Remove a server
claude mcp remove playwright

# Check status
claude mcp status web-search

# Uninstall all
.\master-mcp-setup.ps1 -Uninstall
```

## 🔧 Quick Fixes

### Playwright Issues
```powershell
# Browser not launching? Install browsers:
npx playwright install

# Timeouts? Use headless:
claude mcp remove playwright
claude mcp add playwright -- cmd /c npx '@playwright/mcp@latest' --headless
```

### Obsidian Issues
```powershell
# Connection refused?
# 1. Check Obsidian is running
# 2. Verify REST API plugin enabled
# 3. Check API key is correct

# UV not found? Install it:
pip install --user uv
```

### Web-search Issues
```powershell
# Build failed? Clean reinstall:
cd "$env:USERPROFILE\mcp-servers\web-search"
Remove-Item node_modules -Recurse -Force
npm cache clean --force
npm install && npm run build
```

## 💡 Pro Tips

### Playwright Options
```powershell
--headless              # No browser window (faster)
--browser=chrome        # Use specific browser
--device='iPhone 15'    # Mobile emulation
--viewport-size=1920,1080  # Custom size
--caps=vision,pdf       # Extra capabilities
```

### Obsidian Tools
- `list_files_in_vault` - List all files
- `search` - Search content
- `append_content` - Add to files
- `get_file_contents` - Read files
- `patch_content` - Insert at specific locations

### Web-search Limits
- Max 10 results per search
- Use specific keywords
- Add delays between searches to avoid rate limiting

## 📚 Common Workflows

### Research & Save
```powershell
claude "Search for 'quantum computing', visit top 3 results with playwright, save summaries to Obsidian"
```

### Web Monitoring
```powershell
claude "Use playwright to check if a product price changed on Amazon, log changes to Obsidian"
```

### Documentation Extraction
```powershell
claude "Use playwright to extract all API endpoints from a docs page, format as markdown"
```

## 🔗 Resources

- [Complete Guide](./MCP_COMPLETE_GUIDE.md)
- [Master Setup Script](../platform-tools/windows/mcp/master-mcp-setup.ps1)
- [Claude Code Docs](https://docs.anthropic.com/claude-code)

---

*Quick Reference v2.1 - January 2025*