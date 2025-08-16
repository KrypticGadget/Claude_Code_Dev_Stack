# Claude Code Dev Stack v3.0 - Complete Troubleshooting FAQ

**Comprehensive Solutions for All Common Issues**

---

## 📋 Table of Contents

1. [Installation Issues](#installation-issues)
2. [Agent Problems](#agent-problems)
3. [Hook Execution Issues](#hook-execution-issues)
4. [Command Failures](#command-failures)
5. [MCP Server Problems](#mcp-server-problems)
6. [Audio System Issues](#audio-system-issues)
7. [Mobile Interface Problems](#mobile-interface-problems)
8. [Performance Issues](#performance-issues)
9. [Integration Problems](#integration-problems)
10. [Emergency Recovery](#emergency-recovery)

---

## Installation Issues

### ❌ Problem: "claude" command not recognized

**Symptoms:**
- Command prompt shows: `'claude' is not recognized as an internal or external command`
- PowerShell shows: `The term 'claude' is not recognized`

**Solution:**
```powershell
# 1. Verify Claude Code installation
# Download from: https://claude.ai/code

# 2. Check if Claude Code is in PATH
$env:PATH -split ';' | Select-String "Claude"

# 3. If not found, add to PATH
$claudePath = "C:\Program Files\Claude Code"  # Adjust path as needed
$env:PATH += ";$claudePath"

# 4. Restart PowerShell and test
claude --version
```

**Additional Checks:**
```powershell
# Check if executable exists
Get-ChildItem "C:\Program Files\Claude Code\claude.exe" -ErrorAction SilentlyContinue

# Check Windows app installation
Get-AppxPackage | Where-Object {$_.Name -like "*Claude*"}
```

### ❌ Problem: Permission denied during installation

**Symptoms:**
- `Access denied` errors during file copying
- `Permission denied` when running installation scripts

**Solution:**
```powershell
# 1. Run PowerShell as Administrator
# Right-click PowerShell → "Run as Administrator"

# 2. Set execution policy temporarily
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# 3. Run installation with elevated privileges
.\platform-tools\windows\installers\install-all.ps1

# 4. Reset execution policy
Set-ExecutionPolicy -ExecutionPolicy Restricted -Scope Process
```

### ❌ Problem: Missing dependencies (Node.js, Python, Git)

**Symptoms:**
- `'node' is not recognized`
- `'python' is not recognized`
- `'git' is not recognized`

**Solution:**
```powershell
# Option 1: Install via Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
choco install nodejs python git -y

# Option 2: Manual installation
# Node.js: https://nodejs.org/
# Python: https://python.org/
# Git: https://git-scm.com/

# Verify installations
node --version    # Should show v18+
python --version  # Should show 3.8+
git --version     # Should show 2.0+
```

### ❌ Problem: Firewall blocking installation

**Symptoms:**
- Download timeouts
- Connection refused errors
- Antivirus warnings

**Solution:**
```powershell
# 1. Temporarily disable Windows Defender real-time protection
# Windows Security → Virus & threat protection → Real-time protection: OFF

# 2. Add firewall exception for Claude Code
New-NetFirewallRule -DisplayName "Claude Code Dev Stack" -Direction Inbound -Port 8080,8081 -Protocol TCP -Action Allow

# 3. Add folder exclusion in Windows Defender
# Windows Security → Virus & threat protection → Exclusions
# Add: C:\Users\%USERNAME%\.claude\

# 4. Re-enable protection after installation
```

---

## Agent Problems

### ❌ Problem: Agents not appearing after installation

**Symptoms:**
- `@agent-` mentions not recognized
- Agent list shows fewer than 28 agents
- "Agent not found" errors

**Diagnosis:**
```powershell
# Check agent count
Get-ChildItem ~/.claude/agents/*.md | Measure-Object
# Expected: Count = 28

# Check agent file contents
Get-ChildItem ~/.claude/agents/*.md | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    if ($content -notmatch "^---") {
        Write-Host "Invalid frontmatter in: $($_.Name)" -ForegroundColor Red
    }
}
```

**Solution:**
```powershell
# 1. Remove existing agents
Remove-Item ~/.claude/agents/*.md -Force

# 2. Reinstall agents
.\platform-tools\windows\installers\install-agents.ps1 -Force

# 3. Verify installation
Get-ChildItem ~/.claude/agents/*.md | Measure-Object

# 4. Test agent recognition
claude "List all available agents"
```

### ❌ Problem: Agent execution timeout

**Symptoms:**
- Agents take too long to respond
- "Agent timeout" errors
- Incomplete agent responses

**Solution:**
```powershell
# 1. Check system resources
Get-Process | Where-Object {$_.ProcessName -match "claude|node|python"} | 
    Select-Object ProcessName, CPU, WS | Sort-Object WS -Descending

# 2. Increase timeout in settings
$settings = Get-Content ~/.claude/settings.json | ConvertFrom-Json
$settings.agents.timeout = 600  # 10 minutes
$settings | ConvertTo-Json -Depth 10 | Set-Content ~/.claude/settings.json

# 3. Reduce parallel agent limit
$settings.agents.max_parallel = 3
$settings | ConvertTo-Json -Depth 10 | Set-Content ~/.claude/settings.json

# 4. Restart Claude Code
```

### ❌ Problem: Agent routing not working

**Symptoms:**
- `@agent-` mentions ignored
- Wrong agent responding to mentions
- Agent collaboration failures

**Solution:**
```powershell
# 1. Check agent mention parser hook
python ~/.claude/hooks/agent_mention_parser.py --test

# 2. Verify settings.json hook configuration
Get-Content ~/.claude/settings.json | ConvertFrom-Json | Select-Object -ExpandProperty hooks

# 3. Test agent routing manually
claude "Use the @agent-master-orchestrator to test routing functionality"

# 4. Reinstall hooks if routing fails
.\platform-tools\windows\installers\install-hooks.ps1 -Force
```

### ❌ Problem: Agent performance degradation

**Symptoms:**
- Agents responding slowly
- Quality of responses decreased
- Memory usage increasing

**Solution:**
```powershell
# 1. Clear agent cache
Remove-Item ~/.claude/cache/agents/* -Recurse -Force

# 2. Monitor memory usage
Get-Process | Where-Object {$_.ProcessName -match "claude"} | 
    Select-Object ProcessName, WS | Sort-Object WS -Descending

# 3. Restart Claude Code session
# Close and reopen Claude Code

# 4. Check for memory leaks
# Monitor process memory over time
```

---

## Hook Execution Issues

### ❌ Problem: Hooks not triggering

**Symptoms:**
- Expected hooks don't execute
- No hook output in logs
- Audio notifications not playing

**Diagnosis:**
```powershell
# Check hook configuration
Get-Content ~/.claude/settings.json | ConvertFrom-Json | Select-Object -ExpandProperty hooks

# Check hook files exist
Get-ChildItem ~/.claude/hooks/*.py | Measure-Object
# Expected: Count = 28

# Test individual hook
echo '{"hook_event_name": "SessionStart"}' | python ~/.claude/hooks/session_loader.py
```

**Solution:**
```powershell
# 1. Verify hook permissions
Get-ChildItem ~/.claude/hooks/*.py | ForEach-Object {
    if (!(python $_.FullName --test 2>$null)) {
        Write-Host "Hook error: $($_.Name)" -ForegroundColor Red
    }
}

# 2. Reinstall hooks
.\platform-tools\windows\installers\install-hooks.ps1 -Force

# 3. Check Python environment
python --version
pip list | Select-String "requests|json|pathlib"

# 4. Manually trigger test hook
echo '{"hook_event_name": "Test"}' | python ~/.claude/hooks/base_hook.py
```

### ❌ Problem: Hook execution errors

**Symptoms:**
- Hooks fail with errors
- "Hook execution failed" messages
- Partial hook chain execution

**Solution:**
```powershell
# 1. Check Python dependencies
pip install --upgrade requests pathlib json5

# 2. View hook error logs
Get-Content ~/.claude/logs/hooks.log -Tail 20

# 3. Test problematic hook individually
echo '{"hook_event_name": "SessionStart", "debug": true}' | python ~/.claude/hooks/session_loader.py

# 4. Fix hook permissions
icacls ~/.claude/hooks/*.py /grant Everyone:F
```

### ❌ Problem: Hook chain breaking

**Symptoms:**
- First few hooks execute, then chain stops
- Inconsistent hook execution
- Some events trigger hooks, others don't

**Solution:**
```powershell
# 1. Check hook dependency chain
Get-Content ~/.claude/hooks/base_hook.py | Select-String "chain|dependency"

# 2. Monitor hook execution in real-time
# Open new PowerShell window
Get-Content ~/.claude/logs/hooks.log -Wait -Tail 5

# 3. Reduce hook timeout
$settings = Get-Content ~/.claude/settings.json | ConvertFrom-Json
$settings.hooks.execution_timeout = 60  # Increase timeout
$settings | ConvertTo-Json -Depth 10 | Set-Content ~/.claude/settings.json

# 4. Test hook chain manually
.\test-hooks-chain.ps1  # If available
```

---

## Command Failures

### ❌ Problem: Slash commands not recognized

**Symptoms:**
- `/command` treated as regular text
- "Command not found" errors
- Commands execute as agent requests instead

**Solution:**
```powershell
# 1. Check command installation
Get-ChildItem ~/.claude/commands/*.md | Measure-Object
# Expected: Count = 18

# 2. Verify command format
Get-ChildItem ~/.claude/commands/*.md | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    if ($content -notmatch "^---") {
        Write-Host "Invalid command format: $($_.Name)" -ForegroundColor Red
    }
}

# 3. Reinstall commands
.\platform-tools\windows\installers\install-commands.ps1 -Force

# 4. Test command recognition
claude "List all available slash commands"
```

### ❌ Problem: Command execution hangs

**Symptoms:**
- Commands start but never complete
- No progress updates
- Claude Code becomes unresponsive

**Solution:**
```powershell
# 1. Check for hanging processes
Get-Process | Where-Object {$_.ProcessName -match "claude|node|python"} | 
    Where-Object {$_.CPU -gt 90}

# 2. Kill hanging processes if necessary
# Get-Process "problematic_process" | Stop-Process -Force

# 3. Reduce command complexity
# Use simpler parameters or break into smaller commands

# 4. Increase system resources
# Close other applications to free memory
```

### ❌ Problem: Command parameters not working

**Symptoms:**
- Commands ignore parameters
- Unexpected command behavior
- "Invalid parameter" errors

**Solution:**
```powershell
# 1. Check parameter syntax
# Correct: /new-project "My Project Name"
# Incorrect: /new-project My Project Name

# 2. Escape special characters
# Use quotes around parameters with spaces or special chars

# 3. Test with simple parameters first
claude '/project-status'

# 4. Check command documentation
Get-Content ~/.claude/commands/new-project.md | Select-String "parameter|usage"
```

---

## MCP Server Problems

### ❌ Problem: MCP servers not connecting

**Symptoms:**
- `claude mcp list` shows disconnected servers
- "MCP server unavailable" errors
- Tools not accessible

**Diagnosis:**
```powershell
# Check MCP server status
claude mcp list

# Check server logs
Get-Content "$env:LOCALAPPDATA\Claude\logs\mcp-*.log" -Tail 20

# Test individual server
claude mcp status playwright
claude mcp status obsidian
claude mcp status web-search
```

**Solution:**
```powershell
# 1. Restart MCP servers
claude mcp restart playwright
claude mcp restart obsidian
claude mcp restart web-search

# 2. If restart fails, remove and reinstall
claude mcp remove playwright
claude mcp add playwright -- cmd /c npx '@playwright/mcp@latest' --headless

# 3. Check server dependencies
# For Playwright: npx playwright install
# For Obsidian: Verify API key and Obsidian running
# For Web-search: Check Node.js installation
```

### ❌ Problem: Playwright MCP issues

**Symptoms:**
- Browser automation fails
- "Browser not found" errors
- Timeout errors during web navigation

**Solution:**
```powershell
# 1. Install Playwright browsers
npx playwright install

# 2. Use system Chrome if available
claude mcp remove playwright
claude mcp add playwright -- cmd /c npx '@playwright/mcp@latest' --browser=chrome --executable-path="C:\Program Files\Google\Chrome\Application\chrome.exe"

# 3. Use headless mode for better performance
claude mcp remove playwright
claude mcp add playwright -- cmd /c npx '@playwright/mcp@latest' --headless

# 4. Check for conflicting browser processes
Get-Process chrome,firefox,msedge | Stop-Process -Force
```

### ❌ Problem: Obsidian MCP connection failed

**Symptoms:**
- "Connection refused" errors
- "API key invalid" messages
- Obsidian tools not available

**Solution:**
```powershell
# 1. Verify Obsidian is running
Get-Process obsidian -ErrorAction SilentlyContinue

# 2. Check REST API plugin is enabled
# Open Obsidian → Settings → Community Plugins → Local REST API

# 3. Verify API key
# Copy API key from Obsidian plugin settings
$apiKey = "your_api_key_here"
$env:OBSIDIAN_API_KEY = $apiKey

# 4. Reinstall with correct API key
claude mcp remove obsidian
claude mcp add obsidian --env OBSIDIAN_API_KEY=$apiKey --env OBSIDIAN_HOST=127.0.0.1 --env OBSIDIAN_PORT=27124 -- cmd /c uvx mcp-obsidian

# 5. Test connection
Test-NetConnection -ComputerName 127.0.0.1 -Port 27124
```

### ❌ Problem: Web-search MCP build failures

**Symptoms:**
- `npm install` fails
- `npm run build` errors
- "Module not found" errors

**Solution:**
```powershell
# 1. Clean Node.js cache
npm cache clean --force

# 2. Remove node_modules and reinstall
cd "$env:USERPROFILE\mcp-servers\web-search"
Remove-Item node_modules -Recurse -Force -ErrorAction SilentlyContinue
npm install

# 3. Use different Node.js version if needed
# Install nvm-windows: https://github.com/coreybutler/nvm-windows
# nvm install 18.17.0
# nvm use 18.17.0

# 4. Manual build steps
npm run clean  # If available
npm run build

# 5. Alternative installation method
Remove-Item "$env:USERPROFILE\mcp-servers\web-search" -Recurse -Force
$zipUrl = "https://github.com/pskill9/web-search/archive/refs/heads/main.zip"
Invoke-WebRequest -Uri $zipUrl -OutFile "$env:TEMP\web-search.zip"
Expand-Archive -Path "$env:TEMP\web-search.zip" -DestinationPath "$env:USERPROFILE\mcp-servers" -Force
```

---

## Audio System Issues

### ❌ Problem: No audio notifications

**Symptoms:**
- Silent system - no sounds play
- Audio hook executes but no sound
- Missing audio files

**Diagnosis:**
```powershell
# Check audio files exist
Get-ChildItem ~/.claude/audio/*.mp3 | Measure-Object
# Expected: Multiple MP3 files

# Test audio hook
echo '{"hook_event_name": "SessionStart"}' | python ~/.claude/hooks/audio_player.py

# Check Windows audio system
Get-WmiObject -Class Win32_SoundDevice | Select-Object Name, Status
```

**Solution:**
```powershell
# 1. Install audio files
.\platform-tools\windows\installers\install-audio.ps1 -Force

# 2. Test Windows audio system
Add-Type -AssemblyName System.Media
$player = New-Object System.Media.SoundPlayer
$player.SoundLocation = "$env:USERPROFILE\.claude\audio\ready.mp3"
$player.Play()

# 3. Check audio configuration
Get-Content ~/.claude/audio/audio_config.json | ConvertFrom-Json

# 4. Verify Python audio dependencies
pip install playsound pygame --upgrade
```

### ❌ Problem: Wrong audio playing

**Symptoms:**
- Incorrect sounds for events
- Audio not matching context
- Random audio notifications

**Solution:**
```powershell
# 1. Check audio mapping configuration
Get-Content ~/.claude/hooks/audio_player.py | Select-String "audio_mapping|determine_audio"

# 2. Test specific audio events
echo '{"hook_event_name": "Stop", "context": {"model": "claude-3-opus"}}' | python ~/.claude/hooks/audio_player.py

# 3. Update audio configuration
$config = Get-Content ~/.claude/audio/audio_config.json | ConvertFrom-Json
$config.model_specific_sounds = @{
    "claude-3-opus" = @{
        "activation" = "complex_chord.wav"
        "completion" = "sophisticated_chime.wav"
    }
}
$config | ConvertTo-Json -Depth 10 | Set-Content ~/.claude/audio/audio_config.json

# 4. Restart audio system
# Close and reopen Claude Code
```

### ❌ Problem: Audio playback errors

**Symptoms:**
- "Audio device not found" errors
- Crackling or distorted audio
- Audio hook fails with errors

**Solution:**
```powershell
# 1. Check audio device availability
Get-WmiObject -Class Win32_SoundDevice | Where-Object {$_.Status -eq "OK"}

# 2. Use alternative audio method
# Edit ~/.claude/hooks/audio_player.py
# Change audio playback method from pygame to windows media player

# 3. Check audio file integrity
Get-ChildItem ~/.claude/audio/*.mp3 | ForEach-Object {
    try {
        $player = New-Object System.Media.SoundPlayer
        $player.SoundLocation = $_.FullName
        $player.LoadSync()
        Write-Host "OK: $($_.Name)" -ForegroundColor Green
    } catch {
        Write-Host "Corrupted: $($_.Name)" -ForegroundColor Red
    }
}

# 4. Reinstall audio files
Remove-Item ~/.claude/audio/*.mp3 -Force
.\platform-tools\windows\installers\install-audio.ps1 -Force
```

---

## Mobile Interface Problems

### ❌ Problem: Mobile interface not accessible

**Symptoms:**
- Browser shows "This site can't be reached"
- Connection refused on port 8080
- Mobile app won't connect

**Diagnosis:**
```powershell
# Check if mobile server is running
Test-NetConnection -ComputerName localhost -Port 8080

# Check for process listening on port
netstat -ano | Select-String ":8080"

# Check firewall rules
Get-NetFirewallRule -DisplayName "*8080*" | Select-Object DisplayName, Enabled
```

**Solution:**
```powershell
# 1. Launch mobile interface
.\platform-tools\windows\mobile\launch-mobile-remote.ps1

# 2. Add firewall exception
New-NetFirewallRule -DisplayName "Claude Code Mobile" -Direction Inbound -Port 8080 -Protocol TCP -Action Allow

# 3. Check for port conflicts
$portProcess = netstat -ano | Select-String ":8080" | ForEach-Object { ($_ -split '\s+')[-1] }
if ($portProcess) {
    Get-Process -Id $portProcess | Select-Object ProcessName, Id
    # Kill conflicting process if safe
    # Stop-Process -Id $portProcess -Force
}

# 4. Use alternative port
.\platform-tools\windows\mobile\launch-mobile-remote.ps1 -Port 8081
```

### ❌ Problem: Mobile commands not executing

**Symptoms:**
- Commands sent from mobile don't execute
- Mobile shows "queued" status indefinitely
- Desktop doesn't receive mobile commands

**Solution:**
```powershell
# 1. Check mobile sync hook
python ~/.claude/hooks/mobile_sync.py --test

# 2. Verify WebSocket connection
# In browser dev tools (F12):
# const ws = new WebSocket('ws://localhost:8080/api/v3/status/stream');
# ws.onopen = () => console.log('Connected');

# 3. Check command queue
Get-Content ~/.claude/logs/mobile.log -Tail 20

# 4. Restart mobile interface
# Kill current mobile process
Get-Process python | Where-Object {$_.ProcessName -match "launch_mobile"} | Stop-Process -Force
# Restart mobile interface
.\platform-tools\windows\mobile\launch-mobile-remote.ps1
```

### ❌ Problem: Mobile sync issues

**Symptoms:**
- Status updates not appearing on mobile
- Delayed synchronization
- Mobile shows stale information

**Solution:**
```powershell
# 1. Check status line updater
python ~/.claude/hooks/status_line_updater.py --test

# 2. Monitor real-time updates
# Open browser to http://localhost:8080
# Check if status updates every 100ms

# 3. Check WebSocket health
# Browser dev tools → Network → WS (WebSocket connections)
# Should show active connection to ws://localhost:8080/status

# 4. Restart status system
# Restart Claude Code to reinitialize status line
```

---

## Performance Issues

### ❌ Problem: System running slowly

**Symptoms:**
- High CPU usage
- Slow response times
- System lag during operations

**Diagnosis:**
```powershell
# Monitor system resources
Get-Process | Where-Object {$_.ProcessName -match "claude|node|python"} | 
    Select-Object ProcessName, CPU, WS | Sort-Object WS -Descending

# Check memory usage
Get-WmiObject -Class Win32_OperatingSystem | 
    Select-Object @{Name="MemoryUsage";Expression={[math]::Round(($_.TotalVisibleMemorySize - $_.FreePhysicalMemory) / $_.TotalVisibleMemorySize * 100, 2)}}

# Monitor disk usage
Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, FreeSpace, Size
```

**Solution:**
```powershell
# 1. Reduce parallel agent limit
$settings = Get-Content ~/.claude/settings.json | ConvertFrom-Json
$settings.agents.max_parallel = 3  # Reduce from default 5
$settings | ConvertTo-Json -Depth 10 | Set-Content ~/.claude/settings.json

# 2. Clear cache and temporary files
Remove-Item ~/.claude/cache/* -Recurse -Force
Remove-Item ~/.claude/tmp/* -Recurse -Force

# 3. Optimize hook execution
$settings.hooks.execution_timeout = 30  # Reduce timeout
$settings | ConvertTo-Json -Depth 10 | Set-Content ~/.claude/settings.json

# 4. Restart Claude Code with fresh session
```

### ❌ Problem: Memory usage growing

**Symptoms:**
- Increasing memory consumption over time
- Out of memory errors
- System becomes unresponsive

**Solution:**
```powershell
# 1. Monitor memory leaks
$before = (Get-Process claude).WS
Start-Sleep 300  # Wait 5 minutes
$after = (Get-Process claude).WS
$growth = $after - $before
Write-Host "Memory growth: $([math]::Round($growth/1MB, 2)) MB"

# 2. Enable memory optimization
$settings = Get-Content ~/.claude/settings.json | ConvertFrom-Json
$settings.performance = @{
    memory_optimization = $true
    garbage_collection = $true
    cache_limit = "1GB"
}
$settings | ConvertTo-Json -Depth 10 | Set-Content ~/.claude/settings.json

# 3. Restart session periodically
# Close and reopen Claude Code every few hours for long sessions

# 4. Reduce context window size
$settings.agents.context_limit = 50000  # Reduce if needed
```

### ❌ Problem: Network timeouts

**Symptoms:**
- "Request timeout" errors
- Slow API responses
- Connection dropped errors

**Solution:**
```powershell
# 1. Test network connectivity
Test-NetConnection -ComputerName api.anthropic.com -Port 443

# 2. Increase timeout values
$settings = Get-Content ~/.claude/settings.json | ConvertFrom-Json
$settings.network = @{
    timeout = 60000  # 60 seconds
    retry_count = 3
    connection_pool_size = 10
}
$settings | ConvertTo-Json -Depth 10 | Set-Content ~/.claude/settings.json

# 3. Check proxy settings (if using proxy)
netsh winhttp show proxy

# 4. Flush DNS cache
ipconfig /flushdns
```

---

## Integration Problems

### ❌ Problem: Third-party integration failures

**Symptoms:**
- Claude Code Browser not loading
- Mobile app connection issues
- MCP Manager not working

**Solution:**
```powershell
# 1. Verify all integrations are properly attributed
Get-Content ./CREDITS.md | Select-String "Original Author"

# 2. Check integration directories
Get-ChildItem ~/.claude/integrations/ -Recurse | Select-Object Name, LastWriteTime

# 3. Update integration components
# For Claude Code Browser (@zainhoda)
cd ~/.claude/integrations/browser
git pull origin main
npm install

# For Mobile App (@9cat)
cd ~/.claude/integrations/mobile
flutter pub get

# 4. Verify integration configuration
Get-Content ~/.claude/integrations/config.json | ConvertFrom-Json
```

### ❌ Problem: GitHub integration not working

**Symptoms:**
- Auto-commits not happening
- PR creation failures
- Git operations failing

**Solution:**
```powershell
# 1. Check Git configuration
git config --list | Select-String "user.name|user.email"

# 2. Verify GitHub credentials
git credential-manager-core get

# 3. Test git operations manually
git status
git add .
git commit -m "Test commit"

# 4. Check GitHub hook configuration
python ~/.claude/hooks/github_integrator.py --test
```

### ❌ Problem: License compliance issues

**Symptoms:**
- Missing attribution
- License conflicts
- Redistribution concerns

**Solution:**
```powershell
# 1. Verify all licenses are present
Get-ChildItem ./LICENSE-THIRD-PARTY/ | Select-Object Name

# Expected files:
# LICENSE-claude-code-browser (AGPL-3.0)
# LICENSE-9cat-mobile (MIT)
# LICENSE-mcp-manager (MIT)
# LICENSE-openapi-codegen (Apache-2.0)
# LICENSE-openapi-generator (MIT)
# LICENSE-claude-powerline (MIT)
# LICENSE-cc-statusline (MIT)

# 2. Check source code attribution
Get-ChildItem -Recurse -Include "*.py","*.js","*.md" | 
    Select-String "Original.*Author|@zainhoda|@9cat|@qdhenry|@Owloops|@chongdashu"

# 3. Verify CREDITS.md is complete and accurate
Get-Content ./CREDITS.md

# 4. Update attribution if needed
# Add missing attributions to source files
```

---

## Emergency Recovery

### 🆘 Complete System Reset

**When to use:** System completely broken, nothing works

```powershell
# 1. Create backup of current state
$backupDir = "~/.claude-backup-$(Get-Date -Format 'yyyyMMdd-HHmm')"
Copy-Item ~/.claude $backupDir -Recurse -Force

# 2. Complete uninstallation
.\platform-tools\windows\uninstallers\uninstall-all.ps1 -Force

# 3. Clean installation directories
Remove-Item ~/.claude -Recurse -Force -ErrorAction SilentlyContinue

# 4. Fresh installation
.\platform-tools\windows\installers\install-all.ps1

# 5. Verify installation
.\platform-tools\windows\verifiers\verify-installation.ps1

# 6. Restore custom settings (if needed)
# Copy-Item "$backupDir/custom-settings.json" ~/.claude/
```

### 🔧 Selective Component Recovery

**For specific component failures:**

```powershell
# Reset agents only
.\platform-tools\windows\uninstallers\uninstall-agents.ps1
.\platform-tools\windows\installers\install-agents.ps1

# Reset hooks only
.\platform-tools\windows\uninstallers\uninstall-hooks.ps1
.\platform-tools\windows\installers\install-hooks.ps1

# Reset MCP servers only
claude mcp remove --all
.\platform-tools\windows\installers\install-mcps.ps1

# Reset audio system only
Remove-Item ~/.claude/audio/* -Recurse -Force
.\platform-tools\windows\installers\install-audio.ps1
```

### 📊 Diagnostic Data Collection

**For reporting issues:**

```powershell
# Create diagnostic package
$diagDir = "claude-code-diagnostics-$(Get-Date -Format 'yyyyMMdd-HHmm')"
New-Item $diagDir -ItemType Directory

# System information
Get-ComputerInfo > "$diagDir/system-info.txt"
claude --version > "$diagDir/claude-version.txt"

# Component status
Get-ChildItem ~/.claude/agents/*.md | Measure-Object > "$diagDir/agent-count.txt"
Get-ChildItem ~/.claude/hooks/*.py | Measure-Object > "$diagDir/hook-count.txt"
claude mcp list > "$diagDir/mcp-status.txt"

# Configuration files
Copy-Item ~/.claude/settings.json "$diagDir/"
Copy-Item ~/.claude/audio/audio_config.json "$diagDir/" -ErrorAction SilentlyContinue

# Recent logs
Get-Content ~/.claude/logs/*.log -Tail 100 > "$diagDir/recent-logs.txt"

# Process information
Get-Process | Where-Object {$_.ProcessName -match "claude|node|python"} | 
    Select-Object ProcessName, CPU, WS, StartTime > "$diagDir/processes.txt"

# Compress diagnostic package
Compress-Archive -Path $diagDir -DestinationPath "$diagDir.zip"
Write-Host "Diagnostic package created: $diagDir.zip" -ForegroundColor Green
```

### 🔄 Factory Reset (Last Resort)

**Nuclear option - complete clean slate:**

```powershell
# WARNING: This removes ALL Claude Code configuration

# 1. Stop all Claude Code processes
Get-Process | Where-Object {$_.ProcessName -match "claude"} | Stop-Process -Force

# 2. Remove all Claude Code directories
Remove-Item ~/.claude -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$env:LOCALAPPDATA\Claude" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$env:APPDATA\Claude" -Recurse -Force -ErrorAction SilentlyContinue

# 3. Clear registry entries (if any)
# Remove-Item "HKCU:\Software\Claude*" -Recurse -Force -ErrorAction SilentlyContinue

# 4. Reinstall Claude Code from scratch
# Download fresh installer from claude.ai/code

# 5. Install Dev Stack
.\platform-tools\windows\installers\install-all.ps1

# 6. Verify everything works
.\platform-tools\windows\verifiers\verify-installation.ps1
```

---

## 🆘 Emergency Contacts & Resources

### Getting Help
- **GitHub Issues**: https://github.com/KrypticGadget/Claude_Code_Dev_Stack/issues
- **Documentation**: `./docs/` directory
- **Community**: GitHub Discussions

### Quick Reference Commands
```powershell
# Status check
.\platform-tools\windows\verifiers\verify-installation.ps1

# Component reinstall
.\platform-tools\windows\installers\install-[component].ps1 -Force

# Complete reset
.\platform-tools\windows\uninstallers\uninstall-all.ps1
.\platform-tools\windows\installers\install-all.ps1

# Diagnostic collection
# See "Diagnostic Data Collection" section above
```

### Log Locations
- **Main logs**: `~/.claude/logs/`
- **MCP logs**: `$env:LOCALAPPDATA\Claude\logs\mcp-*.log`
- **Hook logs**: `~/.claude/logs/hooks.log`
- **Audio logs**: `~/.claude/logs/audio.log`
- **Mobile logs**: `~/.claude/logs/mobile.log`

---

*Claude Code Dev Stack v3.0 Troubleshooting FAQ - Complete Solutions Guide*

**Remember: When in doubt, try the component-specific reinstall before full system reset**

Last Updated: January 16, 2025