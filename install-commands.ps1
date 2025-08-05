# Claude Code Slash Commands Installer for Windows
# Version: 2.0
# Installs 18 slash commands globally to Claude Code root directory

$ErrorActionPreference = "Stop"
$ProgressPreference = 'Continue'

Write-Host "Claude Code Global Slash Commands Installer" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

# Function to find Claude Code root installation
function Find-ClaudeCodeRoot {
    $possiblePaths = @(
        "$env:APPDATA\Claude",
        "$env:LOCALAPPDATA\Claude",
        "$env:USERPROFILE\AppData\Roaming\Claude",
        "$env:USERPROFILE\AppData\Local\Claude",
        "$env:PROGRAMDATA\Claude"
    )
    
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            return $path
        }
    }
    
    # If not found, create in the most common location
    $defaultPath = "$env:APPDATA\Claude"
    Write-Host "Claude Code installation not found. Creating directory at: $defaultPath" -ForegroundColor Yellow
    return $defaultPath
}

# Find Claude Code root directory
$claudeRoot = Find-ClaudeCodeRoot
$commandsPath = Join-Path $claudeRoot "commands"
$registryPath = Join-Path $claudeRoot "commands-registry.json"
$settingsPath = Join-Path $claudeRoot "settings.json"

Write-Host "Claude Code root: $claudeRoot" -ForegroundColor Green
Write-Host "Commands will be installed to: $commandsPath" -ForegroundColor Green

# Create directory if it doesn't exist
if (!(Test-Path $commandsPath)) {
    Write-Host "Creating global commands directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path $commandsPath | Out-Null
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

# Initialize command registry
$commandRegistry = @{
    version = "2.0"
    commands = @()
    installed = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
}

foreach ($command in $commands) {
    $completed++
    $percent = [int](($completed / $totalCommands) * 100)
    Write-Progress -Activity "Installing Claude Code Commands" -Status "Downloading $command" -PercentComplete $percent
    
    try {
        $url = $baseUrl + $command
        $destination = Join-Path $commandsPath $command
        
        # Download the file
        Invoke-WebRequest -Uri $url -OutFile $destination -UseBasicParsing
        
        Write-Host "[$completed/$totalCommands] ✓ $command" -ForegroundColor Green
        
        # Add to registry
        $commandName = [System.IO.Path]::GetFileNameWithoutExtension($command)
        $commandRegistry.commands += @{
            name = $commandName
            file = $command
            path = $destination
            description = "/$commandName - Claude Code development command"
        }
    }
    catch {
        $failed++
        Write-Host "[$completed/$totalCommands] ✗ $command - Error: $_" -ForegroundColor Red
    }
}

Write-Progress -Activity "Installing Claude Code Commands" -Completed

# Save command registry
try {
    $commandRegistry | ConvertTo-Json -Depth 4 | Set-Content -Path $registryPath -Force
    Write-Host ""
    Write-Host "✓ Command registry created at: $registryPath" -ForegroundColor Green
}
catch {
    Write-Host "✗ Failed to create command registry: $_" -ForegroundColor Red
}

# Update Claude Code settings if exists
if (Test-Path $settingsPath) {
    try {
        $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json
        $settings | Add-Member -NotePropertyName "commandsPath" -NotePropertyValue $commandsPath -Force
        $settings | Add-Member -NotePropertyName "commandRegistry" -NotePropertyValue $registryPath -Force
        $settings | ConvertTo-Json -Depth 4 | Set-Content -Path $settingsPath -Force
        Write-Host "✓ Updated Claude Code settings" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Failed to update settings: $_" -ForegroundColor Red
    }
}

# Summary
Write-Host ""
Write-Host "Global Installation Complete!" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan
Write-Host "Successfully installed: $($totalCommands - $failed) commands" -ForegroundColor Green
if ($failed -gt 0) {
    Write-Host "Failed: $failed commands" -ForegroundColor Red
}
Write-Host ""
Write-Host "Installation Details:" -ForegroundColor Yellow
Write-Host "  • Claude Code Root: $claudeRoot" -ForegroundColor Yellow
Write-Host "  • Commands Directory: $commandsPath" -ForegroundColor Yellow
Write-Host "  • Command Registry: $registryPath" -ForegroundColor Yellow
Write-Host ""
Write-Host "These commands are now globally available in ALL your Claude Code projects!" -ForegroundColor Cyan
Write-Host "You can use them by typing '/' in any chat, for example: /new-project" -ForegroundColor Cyan
Write-Host ""

# Test command availability
Write-Host "Testing command availability..." -ForegroundColor Yellow
$testCommand = Join-Path $commandsPath "new-project.md"
if (Test-Path $testCommand) {
    Write-Host "✓ /new-project command is ready to use!" -ForegroundColor Green
} else {
    Write-Host "✗ Command test failed - please check installation" -ForegroundColor Red
}
Write-Host ""

# Pause to show results
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")