# Claude Code Agents Installer for Windows - GLOBAL Installation
# Downloads and installs 28 AI agents to Claude Code ROOT directory
# Enables @agent- mentions from ANY project

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

Write-Host "Claude Code Agents Installer v2.0 - GLOBAL Installation" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "This will install agents GLOBALLY for use in ANY project" -ForegroundColor Yellow

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

Write-Host "Installing to Claude Code ROOT: $claudeRootPath" -ForegroundColor Green

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
        Write-Host "Please add the following to your settings.json:" -ForegroundColor Yellow
        Write-Host @"
{
  "agents": {
    "enabled": true,
    "globalPath": "$($agentsDir -replace '\\', '/')",
    "configFile": "$($configFile -replace '\\', '/')",
    "autoComplete": true,
    "showInMenu": true
  }
}
"@ -ForegroundColor Cyan
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

Write-Host "`nInstallation complete!" -ForegroundColor Green
Write-Host "Agents are now available GLOBALLY in ANY project!" -ForegroundColor Green
Write-Host "Use @agent-[name] to mention an agent (e.g., @agent-backend-services)" -ForegroundColor Cyan

# Test agent availability
Write-Host "`nTesting agent availability..." -ForegroundColor Yellow
$testAgent = Join-Path $agentsDir "backend-services-agent.md"
if (Test-Path $testAgent) {
    Write-Host "✓ Agent files accessible" -ForegroundColor Green
    Write-Host "✓ Ready to use in any project!" -ForegroundColor Green
}
else {
    Write-Host "⚠ Warning: Could not verify agent files" -ForegroundColor Yellow
}

# Pause to show results
Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")