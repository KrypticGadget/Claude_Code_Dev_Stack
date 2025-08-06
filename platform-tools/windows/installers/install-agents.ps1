# Simple Claude Code Agents Installer
# Just downloads agent files from GitHub to ~/.claude/agents

# Logging
$logFile = "$env:USERPROFILE\claude_agents.log"
function Write-Log {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Out-File -FilePath $logFile -Append
    Write-Host $Message
}

Write-Log "Claude Code Agents Installer"
Write-Log "============================="
Write-Log "Log file: $logFile"

# Setup paths
$claudeDir = "$env:USERPROFILE\.claude"
$agentsDir = "$claudeDir\agents"
Write-Log "Target directory: $agentsDir"

# Create directories (Force creates even if exists)
Write-Log "Setting up directories..."
try {
    if (-not (Test-Path $claudeDir)) {
        Write-Log "Creating $claudeDir"
        New-Item -ItemType Directory -Path $claudeDir -Force | Out-Null
    }
    if (-not (Test-Path $agentsDir)) {
        Write-Log "Creating $agentsDir"
        New-Item -ItemType Directory -Path $agentsDir -Force | Out-Null
    }
    Write-Log "Directory ready: $agentsDir"
} catch {
    Write-Log "ERROR creating directories: $_"
    exit 1
}

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

Write-Log "Downloading $($agents.Count) agents..."
$success = 0
$failed = 0
$count = 0

foreach ($agent in $agents) {
    $count++
    Write-Log "[$count/$($agents.Count)] Downloading: $agent"
    $url = "$baseUrl/$agent"
    $dest = "$agentsDir\$agent"
    
    try {
        Write-Log "  URL: $url"
        Write-Log "  Dest: $dest"
        
        # Download file using .NET WebClient for proper byte handling
        $webClient = New-Object System.Net.WebClient
        $bytes = $webClient.DownloadData($url)
        Write-Log "  Response size: $($bytes.Length) bytes"
        
        [System.IO.File]::WriteAllBytes($dest, $bytes)
        $webClient.Dispose()
        Write-Log "  SUCCESS"
        $success++
    } catch {
        Write-Log "  ERROR: $_"
        $failed++
    }
    
    Start-Sleep -Milliseconds 200
}

Write-Log "Complete!"
Write-Log "Success: $success"
if ($failed -gt 0) {
    Write-Log "Failed: $failed"
}
Write-Log "Location: $agentsDir"
Write-Log "Agents installer finished"

exit 0