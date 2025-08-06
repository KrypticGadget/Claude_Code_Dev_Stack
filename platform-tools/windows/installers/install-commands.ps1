# Simple Claude Code Commands Installer
# Just downloads command files from GitHub to ~/.claude/commands

# Logging
$logFile = "$env:USERPROFILE\claude_commands.log"
function Write-Log {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Out-File -FilePath $logFile -Append
    Write-Host $Message
}

Write-Log "Claude Code Commands Installer"
Write-Log "==============================="
Write-Log "Log file: $logFile"

# Setup paths
$claudeDir = "$env:USERPROFILE\.claude"
$commandsDir = "$claudeDir\commands"
Write-Log "Target directory: $commandsDir"

# Create directories (Force creates even if exists)
Write-Log "Setting up directories..."
try {
    if (-not (Test-Path $claudeDir)) {
        Write-Log "Creating $claudeDir"
        New-Item -ItemType Directory -Path $claudeDir -Force | Out-Null
    }
    if (-not (Test-Path $commandsDir)) {
        Write-Log "Creating $commandsDir"
        New-Item -ItemType Directory -Path $commandsDir -Force | Out-Null
    }
    Write-Log "Directory ready: $commandsDir"
} catch {
    Write-Log "ERROR creating directories: $_"
    return 1
}

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

Write-Log "Downloading $($commands.Count) commands..."
$success = 0
$failed = 0
$count = 0

foreach ($command in $commands) {
    $count++
    Write-Log "[$count/$($commands.Count)] Downloading: $command"
    $url = "$baseUrl/$command"
    $dest = "$commandsDir\$command"
    
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
Write-Log "Location: $commandsDir"
Write-Log "Commands installer finished"

# Return instead of exit to avoid killing terminal
return 0