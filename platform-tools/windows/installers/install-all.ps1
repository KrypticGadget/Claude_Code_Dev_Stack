# Simple Claude Code Dev Stack Installer
# Downloads all components from GitHub to ~/.claude

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Claude Code Dev Stack Installer v2.1" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Base URLs
$baseUrl = "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers"

Write-Host "Installing 4 components:" -ForegroundColor Yellow
Write-Host "1. Agents (28 files)" -ForegroundColor White
Write-Host "2. Commands (18 files)" -ForegroundColor White
Write-Host "3. Hooks (13 files)" -ForegroundColor White
Write-Host "4. MCP configs" -ForegroundColor White
Write-Host ""

# Component installers
$components = @(
    @{Name="Agents"; Script="install-agents.ps1"},
    @{Name="Commands"; Script="install-commands.ps1"},
    @{Name="Hooks"; Script="install-hooks.ps1"},
    @{Name="MCPs"; Script="install-mcps.ps1"}
)

foreach ($component in $components) {
    Write-Host "----------------------------------------" -ForegroundColor DarkGray
    Write-Host "Installing $($component.Name)..." -ForegroundColor Cyan
    Write-Host "----------------------------------------" -ForegroundColor DarkGray
    
    $scriptUrl = "$baseUrl/$($component.Script)"
    
    try {
        # Download and run the component installer
        $scriptContent = Invoke-WebRequest -Uri $scriptUrl -UseBasicParsing -TimeoutSec 30
        Invoke-Expression $scriptContent.Content
    } catch {
        Write-Host "Failed to install $($component.Name): $_" -ForegroundColor Red
    }
    
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Green
Write-Host "  Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Files installed to: $env:USERPROFILE\.claude" -ForegroundColor White
Write-Host ""
Write-Host "To use:" -ForegroundColor Yellow
Write-Host "1. Open Claude Code" -ForegroundColor White
Write-Host "2. Type @ to see agents" -ForegroundColor White
Write-Host "3. Type / to see commands" -ForegroundColor White
Write-Host ""

exit 0