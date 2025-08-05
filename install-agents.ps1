# Claude Code Agents Installer for Windows - GLOBAL Installation
# Downloads and installs 28 AI agents to Claude Code ROOT directory
# Enables @agent- mentions from ANY project

$ErrorActionPreference = "Continue"  # Don't stop on errors
$ProgressPreference = "SilentlyContinue"  # Disable built-in progress bars that slow down downloads

# Start timer
$startTime = Get-Date

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

Write-Host "`nClaude Code Agents Installer v3.0 - FAST Edition" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Installing agents GLOBALLY for use in ANY project" -ForegroundColor Yellow
Write-Host "Total agents to download: $($AGENTS.Count)" -ForegroundColor White

# Detect Claude Code ROOT installation path (not project-specific)
function Find-ClaudeCodeRootPath {
    # Check environment variable first
    if ($env:CLAUDE_CODE_ROOT) {
        Write-Host "Using CLAUDE_CODE_ROOT environment variable: $env:CLAUDE_CODE_ROOT" -ForegroundColor Green
        return $env:CLAUDE_CODE_ROOT
    }
    
    # Common Claude Code root paths (NOT project-specific)
    $possiblePaths = @(
        "$env:USERPROFILE\.claude",
        "$env:USERPROFILE\AppData\Roaming\Claude",
        "$env:APPDATA\Claude",
        "$env:LOCALAPPDATA\Claude",
        "$env:USERPROFILE\.claude-code",
        "$env:APPDATA\claude-code"
    )
    
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            # Verify this is the root by checking for config files
            $configFiles = @("settings.json", "config.json", ".claude")
            foreach ($config in $configFiles) {
                if (Test-Path (Join-Path $path $config)) {
                    Write-Host "Found Claude Code root directory with $config" -ForegroundColor Green
                    return $path
                }
            }
        }
    }
    
    # Create default if not found
    $defaultPath = "$env:USERPROFILE\.claude"
    Write-Host "Claude Code root not found. Creating at: $defaultPath" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $defaultPath -Force | Out-Null
    return $defaultPath
}

$claudeRootPath = Find-ClaudeCodeRootPath
$agentsDir = Join-Path $claudeRootPath "agents"

Write-Host "Installing to: $agentsDir" -ForegroundColor Green

# Create agents directory if it doesn't exist
if (!(Test-Path $agentsDir)) {
    Write-Host "Creating agents directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $agentsDir -Force | Out-Null
}

# Download function with timeout and progress
function Download-Agent {
    param (
        [string]$AgentName,
        [string]$Url,
        [string]$Destination,
        [int]$Index,
        [int]$Total
    )
    
    $agentShortName = $AgentName -replace '-agent\.md$', ''
    
    try {
        # Show progress
        Write-Host "[$Index/$Total] Downloading: $agentShortName... " -NoNewline
        
        # Download with timeout
        $response = Invoke-WebRequest -Uri $Url -TimeoutSec 30 -UseBasicParsing
        
        # Save to file
        [System.IO.File]::WriteAllBytes($Destination, $response.Content)
        
        Write-Host "✓" -ForegroundColor Green
        return $true
    }
    catch {
        $errorMsg = $_.Exception.Message
        if ($errorMsg -like "*timeout*") {
            Write-Host "✗ (timeout)" -ForegroundColor Red
        }
        elseif ($errorMsg -like "*404*") {
            Write-Host "✗ (not found)" -ForegroundColor Red
        }
        else {
            Write-Host "✗ (failed)" -ForegroundColor Red
        }
        return $false
    }
}

# Parallel download function using jobs
function Download-AgentsParallel {
    param (
        [array]$AgentList,
        [string]$BaseUrl,
        [string]$DestinationDir
    )
    
    Write-Host "`nStarting parallel downloads..." -ForegroundColor Yellow
    
    $jobs = @()
    $successful = 0
    $failed = @()
    
    # Start all download jobs
    for ($i = 0; $i -lt $AgentList.Count; $i++) {
        $agent = $AgentList[$i]
        $url = "$BaseUrl/$agent"
        $destination = Join-Path $DestinationDir $agent
        
        $job = Start-Job -ScriptBlock {
            param($url, $dest, $agent)
            try {
                $response = Invoke-WebRequest -Uri $url -TimeoutSec 30 -UseBasicParsing
                [System.IO.File]::WriteAllBytes($dest, $response.Content)
                return @{ Success = $true; Agent = $agent }
            }
            catch {
                return @{ Success = $false; Agent = $agent; Error = $_.Exception.Message }
            }
        } -ArgumentList $url, $destination, $agent
        
        $jobs += $job
    }
    
    # Monitor jobs and show progress
    $completed = 0
    while ($jobs | Where-Object { $_.State -eq 'Running' }) {
        $running = ($jobs | Where-Object { $_.State -eq 'Running' }).Count
        $done = ($jobs | Where-Object { $_.State -eq 'Completed' }).Count
        
        # Update progress line
        $elapsed = [int](New-TimeSpan -Start $startTime -End (Get-Date)).TotalSeconds
        Write-Host "`rProgress: $done/$($AgentList.Count) completed, $running downloading... (${elapsed}s elapsed)" -NoNewline
        
        Start-Sleep -Milliseconds 500
    }
    
    # Collect results
    Write-Host "`n"
    foreach ($job in $jobs) {
        $result = Receive-Job -Job $job
        Remove-Job -Job $job
        
        if ($result.Success) {
            $successful++
            Write-Host "✓ $($result.Agent -replace '-agent\.md$', '')" -ForegroundColor Green
        }
        else {
            $failed += $result.Agent
            Write-Host "✗ $($result.Agent -replace '-agent\.md$', '')" -ForegroundColor Red
        }
    }
    
    return @{
        Successful = $successful
        Failed = $failed
    }
}

# Ask user for download method
Write-Host "`nDownload method:" -ForegroundColor Cyan
Write-Host "1. Fast (parallel downloads)" -ForegroundColor White
Write-Host "2. Sequential (one at a time)" -ForegroundColor White
Write-Host -NoNewline "Choose [1 or 2] (default: 1): " -ForegroundColor Yellow

$choice = Read-Host
if ($choice -eq "" -or $choice -eq "1") {
    # Parallel download
    $results = Download-AgentsParallel -AgentList $AGENTS -BaseUrl $REPO_BASE -DestinationDir $agentsDir
    $successCount = $results.Successful
    $failedAgents = $results.Failed
}
else {
    # Sequential download with progress
    Write-Host "`nDownloading agents sequentially..." -ForegroundColor Yellow
    
    $successCount = 0
    $failedAgents = @()
    
    for ($i = 0; $i -lt $AGENTS.Count; $i++) {
        $agent = $AGENTS[$i]
        $url = "$REPO_BASE/$agent"
        $destination = Join-Path $agentsDir $agent
        
        # Show elapsed time
        $elapsed = [int](New-TimeSpan -Start $startTime -End (Get-Date)).TotalSeconds
        Write-Host -NoNewline "(${elapsed}s) "
        
        if (Download-Agent -AgentName $agent -Url $url -Destination $destination -Index ($i + 1) -Total $AGENTS.Count) {
            $successCount++
        }
        else {
            $failedAgents += $agent
        }
    }
}

# Calculate total time
$totalTime = [int](New-TimeSpan -Start $startTime -End (Get-Date)).TotalSeconds

# Summary
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "Installation Complete! (Total time: ${totalTime}s)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Total agents: $($AGENTS.Count)" -ForegroundColor White
Write-Host "Successfully installed: $successCount" -ForegroundColor Green

if ($failedAgents.Count -gt 0) {
    Write-Host "Failed: $($failedAgents.Count)" -ForegroundColor Red
    Write-Host "`nFailed agents:" -ForegroundColor Red
    $failedAgents | ForEach-Object { 
        Write-Host "  - $($_ -replace '-agent\.md$', '')" -ForegroundColor Red 
    }
    
    Write-Host "`nRetry failed downloads? [Y/n]: " -NoNewline -ForegroundColor Yellow
    $retry = Read-Host
    if ($retry -eq "" -or $retry -eq "Y" -or $retry -eq "y") {
        Write-Host "`nRetrying failed downloads..." -ForegroundColor Yellow
        
        $retrySuccess = 0
        foreach ($agent in $failedAgents) {
            $url = "$REPO_BASE/$agent"
            $destination = Join-Path $agentsDir $agent
            
            if (Download-Agent -AgentName $agent -Url $url -Destination $destination -Index 1 -Total $failedAgents.Count) {
                $retrySuccess++
            }
        }
        
        Write-Host "Retry complete: $retrySuccess/$($failedAgents.Count) successful" -ForegroundColor Cyan
        $successCount += $retrySuccess
    }
}

Write-Host "`nAgents installed to: $agentsDir" -ForegroundColor Green

# Create agent-config.yaml for global agent registry
$configFile = Join-Path $claudeRootPath "agent-config.yaml"
Write-Host "`nCreating global agent registry..." -ForegroundColor Yellow

$yamlContent = @"
# Claude Code Global Agent Registry
# Auto-generated by install-agents.ps1
# This file enables @agent- mentions from ANY project

version: 2.0
global_agents_path: $($agentsDir -replace '\\', '/')
enabled: true

agents:
"@

foreach ($agent in $AGENTS) {
    $agentName = $agent -replace '\.md$', '' -replace '-agent$', ''
    $yamlContent += @"

  - name: $agentName
    file: $agent
    trigger: "@agent-$agentName"
"@
}

$yamlContent | Out-File -FilePath $configFile -Encoding UTF8
Write-Host "Created agent registry: $configFile" -ForegroundColor Green

# Update Claude Code settings.json to include agent configuration
$settingsFile = Join-Path $claudeRootPath "settings.json"
if (Test-Path $settingsFile) {
    Write-Host "Updating Claude Code settings..." -ForegroundColor Yellow
    try {
        $settings = Get-Content $settingsFile -Raw | ConvertFrom-Json
        
        # Add or update agent configuration
        if (-not $settings.PSObject.Properties["agents"]) {
            $settings | Add-Member -NotePropertyName "agents" -NotePropertyValue @{}
        }
        
        $settings.agents = @{
            "enabled" = $true
            "globalPath" = $agentsDir -replace '\\', '/'
            "configFile" = $configFile -replace '\\', '/'
            "autoComplete" = $true
            "showInMenu" = $true
        }
        
        $settings | ConvertTo-Json -Depth 10 | Out-File -FilePath $settingsFile -Encoding UTF8
        Write-Host "Updated settings.json with agent configuration" -ForegroundColor Green
    }
    catch {
        Write-Host "Warning: Could not update settings.json automatically" -ForegroundColor Yellow
    }
}
else {
    # Create minimal settings.json
    Write-Host "Creating new settings.json..." -ForegroundColor Yellow
    @{
        "agents" = @{
            "enabled" = $true
            "globalPath" = $agentsDir -replace '\\', '/'
            "configFile" = $configFile -replace '\\', '/'
            "autoComplete" = $true
            "showInMenu" = $true
        }
    } | ConvertTo-Json -Depth 10 | Out-File -FilePath $settingsFile -Encoding UTF8
    Write-Host "Created settings.json with agent configuration" -ForegroundColor Green
}

# Quick test
Write-Host "`nQuick test:" -ForegroundColor Yellow
$testAgent = Join-Path $agentsDir "backend-services-agent.md"
if (Test-Path $testAgent) {
    Write-Host "✓ Agent files accessible" -ForegroundColor Green
    Write-Host "✓ Ready to use @agent- mentions in any project!" -ForegroundColor Green
}
else {
    Write-Host "⚠ Warning: Could not verify agent files" -ForegroundColor Yellow
}

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "Usage: Type @agent-[name] in any project" -ForegroundColor Cyan
Write-Host "Example: @agent-backend-services" -ForegroundColor White
Write-Host "================================================" -ForegroundColor Cyan

# Clean up and exit
try {
    # Close any progress indicators
    Write-Progress -Activity "Installing Agents" -Completed
    
    # Clean up memory
    [System.GC]::Collect()
    
    # Only pause if there were errors
    if ($failedAgents.Count -gt 0 -and $successCount -lt $AGENTS.Count) {
        Write-Host "`nPress any key to exit..." -ForegroundColor Red
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 1
    }
    else {
        Write-Host "`n✅ Installation complete!" -ForegroundColor Green
        Start-Sleep -Seconds 1  # Brief pause to see message
        exit 0
    }
} catch {
    Write-Host "`n❌ Installation failed: $_" -ForegroundColor Red
    Write-Host "Press any key to exit..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}