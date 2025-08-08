# Ultimate Claude Code Dev Stack Installer v3.0
# Downloads all components + Ultimate Audio System from GitHub to ~/.claude

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
Write-Log "========================================="
Write-Log "Log file: $logFile"

# Base URLs
$baseUrl = "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers"

Write-Log "Installing 5 components:"
Write-Log "1. Agents (28 files)"
Write-Log "2. Commands (18 files)" 
Write-Log "3. Hooks (13 files)"
Write-Log "4. MCP configs"
Write-Log "5. Ultimate Audio System (50 sounds + orchestrator)"

# Component installers
$components = @(
    @{Name="Agents"; Script="install-agents.ps1"},
    @{Name="Commands"; Script="install-commands.ps1"},
    @{Name="Hooks"; Script="install-hooks.ps1"},
    @{Name="MCPs"; Script="install-mcps.ps1"},
    @{Name="Ultimate Audio"; Script="install-ultimate-audio.ps1"}
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

Write-Host "========================================" -ForegroundColor Green
Write-Host "  🎉 ULTIMATE Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Files installed to: $env:USERPROFILE\.claude" -ForegroundColor White
Write-Host ""
Write-Host "✨ NEW ULTIMATE FEATURES:" -ForegroundColor Cyan
Write-Host "  • 50 JARVIS-style audio notifications" -ForegroundColor White
Write-Host "  • Master orchestrator for smart routing" -ForegroundColor White
Write-Host "  • Meta-prompt transformation" -ForegroundColor White
Write-Host "  • Development phase detection" -ForegroundColor White
Write-Host "  • Input detection with audio alerts" -ForegroundColor White
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

# Don't use exit when running via iwr | iex as it kills the terminal
# Just return instead
return