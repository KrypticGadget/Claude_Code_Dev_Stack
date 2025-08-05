# Claude Code Agents Installer for Windows
# Downloads and installs 28 AI agents from the Config_Files directory

$ErrorActionPreference = "Stop"
$ProgressPreference = "Continue"

# Configuration
$REPO_BASE = "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/Config_Files"
$AGENTS = @(
    "api-integration-specialist-agent.md",
    "backend-services-agent.md",
    "business-analyst-agent.md",
    "business-tech-alignment-agent.md",
    "ceo-strategy-agent.md",
    "database-architecture-agent.md",
    "development-prompt-agent.md",
    "devops-engineering-agent.md",
    "financial-analyst-agent.md",
    "frontend-architecture-agent.md",
    "frontend-mockup-agent.md",
    "integration-setup-agent.md",
    "master-orchestrator-agent.md",
    "middleware-specialist-agent.md",
    "mobile-development-agent.md",
    "performance-optimization-agent.md",
    "production-frontend-agent.md",
    "project-manager-agent.md",
    "prompt-engineer-agent.md",
    "quality-assurance-agent.md",
    "script-automation-agent.md",
    "security-architecture-agent.md",
    "technical-cto-agent.md",
    "technical-documentation-agent.md",
    "technical-specifications-agent.md",
    "testing-automation-agent.md",
    "ui-ux-design-agent.md",
    "usage-guide-agent.md"
)

Write-Host "Claude Code Agents Installer v1.0" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Detect Claude Code installation path
function Find-ClaudeCodePath {
    $possiblePaths = @(
        "$env:USERPROFILE\.claude-code",
        "$env:APPDATA\claude-code",
        "$env:LOCALAPPDATA\claude-code",
        "$env:USERPROFILE\AppData\Roaming\Claude",
        "$env:USERPROFILE\.claude"
    )
    
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            return $path
        }
    }
    
    # If not found, use default
    return "$env:USERPROFILE\.claude-code"
}

$claudePath = Find-ClaudeCodePath
$agentsDir = Join-Path $claudePath "agents"

Write-Host "Detected Claude Code path: $claudePath" -ForegroundColor Green

# Create agents directory if it doesn't exist
if (!(Test-Path $agentsDir)) {
    Write-Host "Creating agents directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $agentsDir -Force | Out-Null
}

# Download agents with progress
$totalAgents = $AGENTS.Count
$downloaded = 0
$failed = @()

Write-Host "`nDownloading $totalAgents agents..." -ForegroundColor Yellow

foreach ($agent in $AGENTS) {
    $downloaded++
    $percent = [math]::Round(($downloaded / $totalAgents) * 100)
    Write-Progress -Activity "Installing Claude Code Agents" -Status "Downloading $agent" -PercentComplete $percent
    
    $url = "$REPO_BASE/$agent"
    $destination = Join-Path $agentsDir $agent
    
    try {
        # Download with retry logic
        $retryCount = 0
        $maxRetries = 3
        $success = $false
        
        while (!$success -and $retryCount -lt $maxRetries) {
            try {
                Invoke-WebRequest -Uri $url -OutFile $destination -UseBasicParsing
                $success = $true
                Write-Host "[$downloaded/$totalAgents] Downloaded: $agent" -ForegroundColor Green
            }
            catch {
                $retryCount++
                if ($retryCount -lt $maxRetries) {
                    Write-Host "Retry $retryCount/$maxRetries for $agent..." -ForegroundColor Yellow
                    Start-Sleep -Seconds 1
                }
            }
        }
        
        if (!$success) {
            throw "Failed after $maxRetries retries"
        }
    }
    catch {
        Write-Host "[$downloaded/$totalAgents] Failed: $agent - $_" -ForegroundColor Red
        $failed += $agent
    }
}

Write-Progress -Activity "Installing Claude Code Agents" -Completed

# Summary
Write-Host "`nInstallation Summary" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan
Write-Host "Total agents: $totalAgents" -ForegroundColor White
Write-Host "Successfully installed: $($totalAgents - $failed.Count)" -ForegroundColor Green
if ($failed.Count -gt 0) {
    Write-Host "Failed: $($failed.Count)" -ForegroundColor Red
    Write-Host "Failed agents:" -ForegroundColor Red
    $failed | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
}

Write-Host "`nAgents installed to: $agentsDir" -ForegroundColor Green
Write-Host "Installation complete!" -ForegroundColor Green

# Pause to show results
Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")