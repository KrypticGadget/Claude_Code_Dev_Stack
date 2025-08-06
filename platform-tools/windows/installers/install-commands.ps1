# Simple Claude Code Commands Installer
# Just downloads command files from GitHub to ~/.claude/commands

Write-Host "Claude Code Commands Installer" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan

# Setup paths
$claudeDir = "$env:USERPROFILE\.claude"
$commandsDir = "$claudeDir\commands"

# Create directories (Force creates even if exists)
Write-Host "Setting up directories..." -ForegroundColor Yellow
if (-not (Test-Path $claudeDir)) {
    New-Item -ItemType Directory -Path $claudeDir -Force | Out-Null
}
if (-not (Test-Path $commandsDir)) {
    New-Item -ItemType Directory -Path $commandsDir -Force | Out-Null
}
Write-Host "Directory ready: $commandsDir" -ForegroundColor Green

# List of command files
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

$baseUrl = "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example/commands"

Write-Host "Downloading $($commands.Count) commands..." -ForegroundColor Yellow
$success = 0
$failed = 0

foreach ($command in $commands) {
    Write-Host "Downloading: $command... " -NoNewline
    $url = "$baseUrl/$command"
    $dest = "$commandsDir\$command"
    
    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 10 -ErrorAction Stop
        [System.IO.File]::WriteAllBytes($dest, $response.Content)
        Write-Host "OK" -ForegroundColor Green
        $success++
    } catch {
        Write-Host "FAILED" -ForegroundColor Red
        $failed++
    }
    
    Start-Sleep -Milliseconds 200
}

Write-Host "`nComplete!" -ForegroundColor Cyan
Write-Host "Success: $success" -ForegroundColor Green
if ($failed -gt 0) {
    Write-Host "Failed: $failed" -ForegroundColor Red
}
Write-Host "Location: $commandsDir" -ForegroundColor White

exit 0