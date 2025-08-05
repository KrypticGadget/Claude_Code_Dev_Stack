# Claude Code Slash Commands Installer for Windows
# Version: 1.0
# Installs 18 slash commands from the Claude_Code_Dev_Stack repository

$ErrorActionPreference = "Stop"
$ProgressPreference = 'Continue'

Write-Host "Claude Code Slash Commands Installer" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Function to find Claude Code installation
function Find-ClaudeCodePath {
    $possiblePaths = @(
        "$env:APPDATA\Claude\slash-commands\commands",
        "$env:LOCALAPPDATA\Claude\slash-commands\commands",
        "$env:USERPROFILE\AppData\Roaming\Claude\slash-commands\commands",
        "$env:USERPROFILE\AppData\Local\Claude\slash-commands\commands"
    )
    
    foreach ($path in $possiblePaths) {
        if (Test-Path (Split-Path -Parent (Split-Path -Parent $path))) {
            return $path
        }
    }
    
    # If not found, create in the most common location
    $defaultPath = "$env:APPDATA\Claude\slash-commands\commands"
    Write-Host "Claude Code installation not found. Creating directory at: $defaultPath" -ForegroundColor Yellow
    return $defaultPath
}

# Find or create the installation path
$installPath = Find-ClaudeCodePath
Write-Host "Installation path: $installPath" -ForegroundColor Green

# Create directory if it doesn't exist
if (!(Test-Path $installPath)) {
    Write-Host "Creating directory structure..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path $installPath | Out-Null
}

# List of all 18 command files
$commands = @(
    "api-integration.md",
    "backend-service.md",
    "business-analysis.md",
    "database-design.md",
    "documentation.md",
    "financial-model.md",
    "frontend-mockup.md",
    "go-to-market.md",
    "middleware-setup.md",
    "new-project.md",
    "production-frontend.md",
    "project-plan.md",
    "prompt-enhance.md",
    "requirements.md",
    "resume-project.md",
    "site-architecture.md",
    "tech-alignment.md",
    "technical-feasibility.md"
)

$baseUrl = "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/slash-commands/commands/"
$totalCommands = $commands.Count
$completed = 0
$failed = 0

Write-Host ""
Write-Host "Downloading $totalCommands slash commands..." -ForegroundColor Cyan

foreach ($command in $commands) {
    $completed++
    $percent = [int](($completed / $totalCommands) * 100)
    Write-Progress -Activity "Installing Claude Code Commands" -Status "Downloading $command" -PercentComplete $percent
    
    try {
        $url = $baseUrl + $command
        $destination = Join-Path $installPath $command
        
        # Download the file
        Invoke-WebRequest -Uri $url -OutFile $destination -UseBasicParsing
        
        Write-Host "[$completed/$totalCommands] ✓ $command" -ForegroundColor Green
    }
    catch {
        $failed++
        Write-Host "[$completed/$totalCommands] ✗ $command - Error: $_" -ForegroundColor Red
    }
}

Write-Progress -Activity "Installing Claude Code Commands" -Completed

# Summary
Write-Host ""
Write-Host "Installation Complete!" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan
Write-Host "Successfully installed: $($totalCommands - $failed) commands" -ForegroundColor Green
if ($failed -gt 0) {
    Write-Host "Failed: $failed commands" -ForegroundColor Red
}
Write-Host ""
Write-Host "Commands installed to: $installPath" -ForegroundColor Yellow
Write-Host ""
Write-Host "You can now use these commands in Claude Code by typing '/' in the chat." -ForegroundColor Cyan
Write-Host ""

# Pause to show results
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")