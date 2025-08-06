# Claude Code Agents Installer for Windows - GLOBAL Installation
# Downloads and installs 28 AI agents to Claude Code ROOT directory
# Enables @agent- mentions from ANY project

$ErrorActionPreference = "Continue"  # Don't stop on errors
$ProgressPreference = "SilentlyContinue"  # Disable built-in progress bars that slow down downloads

# Start timer
$startTime = Get-Date

# Configuration
$REPO_BASE = "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example/agents"
$AGENTS = @(
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

Write-Host "`nClaude Code Agents Installer v3.1 - Fixed Edition" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
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

# Download function with better progress and error handling
function Download-Agent {
    param (
        [string]$AgentName,
        [string]$Url,
        [string]$Destination,
        [int]$Index,
        [int]$Total
    )
    
    # Extract clean agent name (remove -agent.md suffix)
    $agentShortName = $AgentName -replace '-agent\.md$', ''
    
    try {
        # Show detailed progress
        Write-Host "Installing agent $Index/$Total`: $agentShortName" -ForegroundColor Cyan
        Write-Host "  Downloading from: $Url" -ForegroundColor DarkGray
        
        # Download with proper error handling
        $response = Invoke-WebRequest -Uri $Url -TimeoutSec 30 -UseBasicParsing -ErrorAction Stop
        
        # Verify content was downloaded
        if ($response.Content.Length -eq 0) {
            throw "Downloaded file is empty"
        }
        
        # Save to file with proper encoding
        $content = [System.Text.Encoding]::UTF8.GetString($response.Content)
        [System.IO.File]::WriteAllText($Destination, $content, [System.Text.Encoding]::UTF8)
        
        # Verify file was created and has content
        if (Test-Path $Destination) {
            $fileSize = (Get-Item $Destination).Length
            if ($fileSize -gt 0) {
                Write-Host "  ✓ Downloaded successfully ($fileSize bytes)" -ForegroundColor Green
                
                # Also save with shortened name (without -agent suffix)
                $shortDestination = Join-Path (Split-Path $Destination -Parent) "$agentShortName.md"
                Copy-Item $Destination $shortDestination -Force
                Write-Host "  ✓ Created shorthand reference: $agentShortName.md" -ForegroundColor Green
                
                return $true
            } else {
                throw "File created but is empty"
            }
        } else {
            throw "File was not created"
        }
    }
    catch {
        $errorMsg = $_.Exception.Message
        Write-Host "  ✗ Failed: $errorMsg" -ForegroundColor Red
        
        # Log detailed error for debugging
        $errorLog = Join-Path $claudeRootPath "agent-install-errors.log"
        $errorEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Failed to download ${AgentName}: ${errorMsg}`n"
        Add-Content -Path $errorLog -Value $errorEntry -Force
        
        return $false
    }
}

# Sequential download with detailed progress
Write-Host "`nStarting agent installation..." -ForegroundColor Yellow
Write-Host "=" * 50 -ForegroundColor DarkGray

$successCount = 0
$failedAgents = @()

for ($i = 0; $i -lt $AGENTS.Count; $i++) {
    $agent = $AGENTS[$i]
    $url = "$REPO_BASE/$agent"
    $destination = Join-Path $agentsDir $agent
    
    # Show elapsed time
    $elapsed = [int](New-TimeSpan -Start $startTime -End (Get-Date)).TotalSeconds
    Write-Host "`nElapsed time: ${elapsed}s" -ForegroundColor DarkGray
    
    if (Download-Agent -AgentName $agent -Url $url -Destination $destination -Index ($i + 1) -Total $AGENTS.Count) {
        $successCount++
    } else {
        $failedAgents += $agent
    }
    
    # Longer delay to prevent overwhelming the system
    Start-Sleep -Milliseconds 1000
    
    # Clear variables to prevent memory buildup
    [System.GC]::Collect()
}

# Calculate total time
$totalTime = [int](New-TimeSpan -Start $startTime -End (Get-Date)).TotalSeconds

# Summary
Write-Host "`n" + "=" * 50 -ForegroundColor Cyan
Write-Host "Installation Complete! (Total time: ${totalTime}s)" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "Total agents: $($AGENTS.Count)" -ForegroundColor White
Write-Host "Successfully installed: $successCount" -ForegroundColor Green

if ($failedAgents.Count -gt 0) {
    Write-Host "Failed: $($failedAgents.Count)" -ForegroundColor Red
    Write-Host "`nFailed agents:" -ForegroundColor Red
    $failedAgents | ForEach-Object { 
        Write-Host "  - $($_ -replace '-agent\.md$', '')" -ForegroundColor Red 
    }
    
    # Offer to view error log
    $errorLog = Join-Path $claudeRootPath "agent-install-errors.log"
    if (Test-Path $errorLog) {
        Write-Host "`nError details saved to: $errorLog" -ForegroundColor Yellow
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

version: 2.1
global_agents_path: $($agentsDir -replace '\\', '/')
enabled: true

agents:
"@

foreach ($agent in $AGENTS) {
    $agentName = $agent -replace '\.md$', '' -replace '-agent$', ''
    $yamlContent += @"

  - name: $agentName
    file: $agent
    shorthand: $agentName.md
    trigger: "@$agentName"
    legacy_trigger: "@agent-$agentName"
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
            "prefix" = "@"
        }
        
        $settings | ConvertTo-Json -Depth 10 | Out-File -FilePath $settingsFile -Encoding UTF8
        Write-Host "Updated settings.json with agent configuration" -ForegroundColor Green
    }
    catch {
        Write-Host "Warning: Could not update settings.json automatically" -ForegroundColor Yellow
    }
} else {
    # Create minimal settings.json
    Write-Host "Creating new settings.json..." -ForegroundColor Yellow
    @{
        "version" = "1.0.0"
        "agents" = @{
            "enabled" = $true
            "globalPath" = $agentsDir -replace '\\', '/'
            "configFile" = $configFile -replace '\\', '/'
            "autoComplete" = $true
            "showInMenu" = $true
            "prefix" = "@"
        }
    } | ConvertTo-Json -Depth 10 | Out-File -FilePath $settingsFile -Encoding UTF8
    Write-Host "Created settings.json with agent configuration" -ForegroundColor Green
}

# Quick verification
Write-Host "`nVerifying installation..." -ForegroundColor Yellow
$verificationPassed = $true

# Check if files exist and have content
$sampleAgents = @("backend-services-agent.md", "frontend-architecture-agent.md", "database-architecture-agent.md")
foreach ($sampleAgent in $sampleAgents) {
    $agentPath = Join-Path $agentsDir $sampleAgent
    if (Test-Path $agentPath) {
        $fileSize = (Get-Item $agentPath).Length
        if ($fileSize -gt 1000) {  # Agent files should be at least 1KB
            Write-Host "✓ Verified: $($sampleAgent -replace '-agent\.md$', '') ($fileSize bytes)" -ForegroundColor Green
        } else {
            Write-Host "✗ File too small: $sampleAgent ($fileSize bytes)" -ForegroundColor Red
            $verificationPassed = $false
        }
    } else {
        Write-Host "✗ Missing: $sampleAgent" -ForegroundColor Red
        $verificationPassed = $false
    }
}

if ($verificationPassed) {
    Write-Host "`n✓ All verification checks passed!" -ForegroundColor Green
} else {
    Write-Host "`n⚠ Some verification checks failed. Try running the installer again." -ForegroundColor Yellow
}

Write-Host "`n" + "=" * 50 -ForegroundColor Cyan
Write-Host "Usage Instructions:" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "1. Type @ followed by agent name in any project" -ForegroundColor White
Write-Host "   Example: @backend-services" -ForegroundColor Green
Write-Host "   Example: @frontend-architecture" -ForegroundColor Green
Write-Host "`n2. Legacy format also supported:" -ForegroundColor White
Write-Host "   Example: @agent-backend-services" -ForegroundColor DarkGray
Write-Host "`n3. View all agents: $agentsDir" -ForegroundColor White
Write-Host "=" * 50 -ForegroundColor Cyan

# Clean up and exit
if ($failedAgents.Count -eq 0 -and $verificationPassed) {
    Write-Host "`n✅ Installation completed successfully!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n⚠ Installation completed with warnings" -ForegroundColor Yellow
    exit 0
}