# Simple Claude Code Agents Installer
# Just downloads agent files from GitHub to ~/.claude/agents

Write-Host "Claude Code Agents Installer" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan

# Setup paths
$claudeDir = "$env:USERPROFILE\.claude"
$agentsDir = "$claudeDir\agents"

# Create directories (Force creates even if exists)
Write-Host "Setting up directories..." -ForegroundColor Yellow
if (-not (Test-Path $claudeDir)) {
    New-Item -ItemType Directory -Path $claudeDir -Force | Out-Null
}
if (-not (Test-Path $agentsDir)) {
    New-Item -ItemType Directory -Path $agentsDir -Force | Out-Null
}
Write-Host "Directory ready: $agentsDir" -ForegroundColor Green

# List of agent files
$agents = @(
    "api-integration-specialist.md",
    "backend-services.md",
    "business-analyst.md",
    "business-tech-alignment.md",
    "ceo-strategy.md",
    "database-architecture.md",
    "development-prompt.md",
    "devops-engineering.md",
    "financial-analyst.md",
    "frontend-architecture.md",
    "frontend-mockup.md",
    "integration-setup.md",
    "master-orchestrator.md",
    "middleware-specialist.md",
    "mobile-development.md",
    "performance-optimization.md",
    "production-frontend.md",
    "project-manager.md",
    "prompt-engineer.md",
    "quality-assurance.md",
    "script-automation.md",
    "security-architecture.md",
    "technical-cto.md",
    "technical-documentation.md",
    "technical-specifications.md",
    "testing-automation.md",
    "ui-ux-design.md",
    "usage-guide.md"
)

$baseUrl = "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example/agents"

Write-Host "Downloading $($agents.Count) agents..." -ForegroundColor Yellow
$success = 0
$failed = 0

foreach ($agent in $agents) {
    Write-Host "Downloading: $agent... " -NoNewline
    $url = "$baseUrl/$agent"
    $dest = "$agentsDir\$agent"
    
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
Write-Host "Location: $agentsDir" -ForegroundColor White

exit 0