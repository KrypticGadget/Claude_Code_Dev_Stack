# Ultimate Claude Code Dev Stack Installer v3.0
# Downloads all components + Ultimate Audio System from GitHub to ~/.claude
# Now with automatic Playwright browser lock fixes!

# Pre-installation Edge cleanup (preserves Chrome for user browsing)
Write-Host "Preparing environment (Edge only)..." -ForegroundColor Yellow
Stop-Process -Name msedge,msedgewebview2 -Force -ErrorAction SilentlyContinue 2>$null
Remove-Item "$env:LOCALAPPDATA\ms-playwright\mcp-edge" -Recurse -Force -ErrorAction SilentlyContinue 2>$null
Remove-Item "$env:LOCALAPPDATA\ms-playwright\msedge-*" -Recurse -Force -ErrorAction SilentlyContinue 2>$null
[Environment]::SetEnvironmentVariable('PLAYWRIGHT_HEADLESS', 'false', 'User')
[Environment]::SetEnvironmentVariable('PLAYWRIGHT_BROWSER', 'msedge', 'User')
$env:PLAYWRIGHT_HEADLESS = "false"
$env:PLAYWRIGHT_BROWSER = "msedge"

# Setup logging
$logFile = "$env:USERPROFILE\claude_installer.log"
function Write-Log {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Out-File -FilePath $logFile -Append
    Write-Host $Message
}

Write-Log "========================================="
Write-Log "Ultimate Claude Code Dev Stack Installer v3.0"
Write-Log "==========================================="
Write-Log "Log file: $logFile"

# Base URLs
$baseUrl = "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers"

Write-Log "Installing 4 V3.0+ components:"
Write-Log "1. V3+ Agents (28 enhanced files with smart orchestration)"
Write-Log "2. V3+ Commands (20+ files with /orchestrate-demo)" 
Write-Log "3. V3+ Hooks & Audio (28 hooks + 102 audio files with mobile sync)"
Write-Log "4. V3+ MCPs (Playwright, Web Search, GitHub, Obsidian)"

# Component installers
$components = @(
    @{Name="V3+ Agents"; Script="install-agents.ps1"},
    @{Name="V3+ Commands"; Script="install-commands.ps1"},
    @{Name="V3+ Hooks & Audio"; Script="install-hooks.ps1"},
    @{Name="V3+ MCPs"; Script="install-mcps.ps1"}
)

foreach ($component in $components) {
    Write-Log "----------------------------------------"
    Write-Log "Installing $($component.Name)..."
    
    $scriptUrl = "$baseUrl/$($component.Script)"
    Write-Log "Downloading from: $scriptUrl"
    
    try {
        # Download and run the component installer
        Write-Log "Fetching script content..."
        $scriptContent = Invoke-WebRequest -Uri $scriptUrl -UseBasicParsing -TimeoutSec 30 -ErrorAction Stop
        
        if ($scriptContent -and $scriptContent.Content) {
            Write-Log "Script downloaded, size: $($scriptContent.Content.Length) bytes"
            Write-Log "Executing $($component.Name) installer..."
            
            # Save script to temp file and execute it separately to prevent crashes
            $tempScript = "$env:TEMP\claude_$($component.Script)"
            Write-Log "Saving to temp: $tempScript"
            $scriptContent.Content | Out-File -FilePath $tempScript -Encoding UTF8
            
            Write-Log "Running script..."
            & powershell.exe -ExecutionPolicy Bypass -File $tempScript
            Write-Log "Script completed with exit code: $LASTEXITCODE"
            
            Remove-Item $tempScript -Force -ErrorAction SilentlyContinue
        } else {
            Write-Log "ERROR: Empty response for $($component.Name)"
        }
    } catch {
        Write-Log "ERROR installing $($component.Name): $($_.Exception.Message)"
        Write-Log "Stack trace: $($_.ScriptStackTrace)"
    }
    
    Write-Log ""
}

# Create quick fix script for future browser locks
$quickFix = @'
# Quick Playwright Edge Browser Lock Fix (Preserves Chrome)
Write-Host "Fixing Playwright Edge browser locks..." -ForegroundColor Yellow
Stop-Process -Name msedge,msedgewebview2 -Force -ErrorAction SilentlyContinue
Remove-Item "$env:LOCALAPPDATA\ms-playwright\mcp-edge" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$env:LOCALAPPDATA\ms-playwright\msedge-*" -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "✓ Browser locks cleared!" -ForegroundColor Green
Write-Host "You can now use Playwright MCP again." -ForegroundColor Cyan
'@
$quickFix | Out-File -FilePath "$env:USERPROFILE\fix-playwright.ps1" -Encoding UTF8

Write-Host "========================================" -ForegroundColor Green
Write-Host "  🎉 ULTIMATE Installation Complete!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "Files installed to: $env:USERPROFILE\.claude" -ForegroundColor White
Write-Host ""
Write-Host "✨ V3.0 FEATURES:" -ForegroundColor Cyan
Write-Host "  • Real-time status line (100ms updates)" -ForegroundColor White
Write-Host "  • Context manager with token tracking" -ForegroundColor White
Write-Host "  • Smart orchestrator with context-aware agent selection" -ForegroundColor White
Write-Host "  • Parallel execution engine for concurrent agents" -ForegroundColor White
Write-Host "  • Chat handoff documentation system" -ForegroundColor White
Write-Host "  • 28 V3-enhanced agents with orchestration patterns" -ForegroundColor White
Write-Host "  • 50 phase-aware audio notifications" -ForegroundColor White
Write-Host "  • ✅ Playwright HEADED MODE (Edge browser visible!)" -ForegroundColor Green
Write-Host "  • 🔒 Chrome preserved for your browsing!" -ForegroundColor Cyan
Write-Host ""
Write-Host "To use:" -ForegroundColor Yellow
Write-Host "1. Restart Claude Code" -ForegroundColor White
Write-Host "2. Type @ to see agents" -ForegroundColor White
Write-Host "3. Type / to see commands" -ForegroundColor White
Write-Host "4. Vague prompts auto-transform!" -ForegroundColor Cyan
Write-Host "5. Audio alerts for all phases!" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎵 Test audio: powershell ~/.claude/audio/test_audio.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "🔧 Browser lock fix: powershell ~/fix-playwright.ps1" -ForegroundColor Yellow
Write-Host "   (Run if you get 'Browser already in use' errors)" -ForegroundColor Gray
Write-Host ""

# Don't use exit when running via iwr | iex as it kills the terminal
# Just return instead
return