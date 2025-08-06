# Simple Claude Code Hooks Installer
# Just downloads Python hook files from GitHub to ~/.claude/hooks

Write-Host "Claude Code Hooks Installer" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan

# Check for Python (optional)
$hasPython = $false
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python") {
        $hasPython = $true
        Write-Host "Python found: $pythonVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "Python not found - hooks require Python to run" -ForegroundColor Yellow
}

# Setup paths
$claudeDir = "$env:USERPROFILE\.claude"
$hooksDir = "$claudeDir\hooks"

# Create directories
Write-Host "Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $hooksDir | Out-Null

# List of hook files
$hooks = @(
    "agent_mention_parser.py",
    "agent_orchestrator.py",
    "base_hook.py",
    "mcp_gateway.py",
    "model_tracker.py",
    "planning_trigger.py",
    "post_command.py",
    "post_project.py",
    "pre_command.py",
    "pre_project.py",
    "quality_gate.py",
    "session_loader.py",
    "session_saver.py"
)

$baseUrl = "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example/hooks"

Write-Host "Downloading $($hooks.Count) hooks..." -ForegroundColor Yellow
$success = 0
$failed = 0

foreach ($hook in $hooks) {
    Write-Host "Downloading: $hook... " -NoNewline
    $url = "$baseUrl/$hook"
    $dest = "$hooksDir\$hook"
    
    try {
        Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing -TimeoutSec 10
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
Write-Host "Location: $hooksDir" -ForegroundColor White

if (-not $hasPython) {
    Write-Host "`nNote: Python is required to run hooks" -ForegroundColor Yellow
    Write-Host "Install Python from: https://python.org" -ForegroundColor Yellow
}

exit 0