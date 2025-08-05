#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Verifies Claude Code Dev Stack v2.1 installation
.DESCRIPTION
    Comprehensive verification script that checks all components of Claude Code Dev Stack:
    - 28 AI Agents
    - 18 Commands
    - 3 Tier 1 MCPs
    - Hook configuration
.PARAMETER Detailed
    Shows detailed information including component names
.PARAMETER Quiet
    Shows only summary information
.EXAMPLE
    ./verify-installation.ps1
    Basic verification with standard output
.EXAMPLE
    ./verify-installation.ps1 -Detailed
    Detailed verification showing all component names
.EXAMPLE
    ./verify-installation.ps1 -Quiet
    Minimal output, suitable for scripts
#>

param(
    [switch]$Detailed,
    [switch]$Quiet
)

# Script configuration
$script:Version = "2.1"
$script:ExpectedAgents = 28
$script:ExpectedCommands = 18
$script:ExpectedMCPs = 3
$script:ExitCode = 0

# Color functions for cross-platform compatibility
function Write-Success {
    param([string]$Message)
    if (-not $Quiet) {
        Write-Host $Message -ForegroundColor Green
    }
}

function Write-Warning {
    param([string]$Message)
    if (-not $Quiet) {
        Write-Host $Message -ForegroundColor Yellow
    }
}

function Write-Error {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    if (-not $Quiet) {
        Write-Host $Message -ForegroundColor Cyan
    }
}

function Write-Header {
    param([string]$Message)
    if (-not $Quiet) {
        Write-Host "`n$Message" -ForegroundColor Magenta
        Write-Host ("-" * $Message.Length) -ForegroundColor Magenta
    }
}

# Detect platform
function Get-Platform {
    if ($IsWindows -or $PSVersionTable.PSVersion.Major -lt 6) {
        if (Test-Path "/proc/version") {
            $versionInfo = Get-Content "/proc/version" -ErrorAction SilentlyContinue
            if ($versionInfo -match "microsoft") {
                return "WSL"
            }
        }
        return "Windows"
    } elseif ($IsMacOS) {
        return "macOS"
    } elseif ($IsLinux) {
        return "Linux"
    }
    return "Unknown"
}

# Get Claude directories
function Get-ClaudeDirectories {
    $dirs = @{
        Project = $null
        User = $null
    }
    
    # Project directory (.claude in current or parent directories)
    $currentDir = Get-Location
    $testDir = $currentDir
    
    while ($testDir) {
        $claudeDir = Join-Path $testDir ".claude"
        if (Test-Path $claudeDir) {
            $dirs.Project = $claudeDir
            break
        }
        $parent = Split-Path $testDir -Parent
        if ($parent -eq $testDir) { break }
        $testDir = $parent
    }
    
    # User directory (~/.claude)
    $homeDir = if ($env:HOME) { $env:HOME } else { $env:USERPROFILE }
    $userClaudeDir = Join-Path $homeDir ".claude"
    if (Test-Path $userClaudeDir) {
        $dirs.User = $userClaudeDir
    }
    
    return $dirs
}

# Check agents
function Test-Agents {
    param($Directories)
    
    Write-Header "Checking AI Agents"
    
    $expectedAgentNames = @(
        "master-orchestrator", "technical-specification-analyst", "database-architect",
        "backend-services-engineer", "frontend-ui-developer", "api-integration-specialist",
        "security-compliance-auditor", "devops-automation-engineer", "quality-assurance-tester",
        "claude-code-expert", "code-reviewer", "performance-optimizer",
        "documentation-writer", "project-manager", "ux-designer",
        "accessibility-specialist", "mobile-developer", "cloud-architect",
        "data-scientist", "ml-engineer", "blockchain-developer",
        "game-developer", "embedded-systems-engineer", "test-automation-engineer",
        "release-manager", "support-engineer", "business-analyst",
        "scrum-master"
    )
    
    $foundAgents = @()
    $agentDirs = @()
    
    # Check both project and user directories
    foreach ($dirType in @("Project", "User")) {
        $baseDir = $Directories[$dirType]
        if ($baseDir) {
            $agentDir = Join-Path $baseDir "agents"
            if (Test-Path $agentDir) {
                $agentDirs += @{Type = $dirType; Path = $agentDir}
                $agents = Get-ChildItem -Path $agentDir -Filter "*.md" -ErrorAction SilentlyContinue
                foreach ($agent in $agents) {
                    $agentName = [System.IO.Path]::GetFileNameWithoutExtension($agent.Name)
                    if ($agentName -notin $foundAgents) {
                        $foundAgents += $agentName
                    }
                }
            }
        }
    }
    
    $agentCount = $foundAgents.Count
    
    if ($agentCount -eq 0) {
        Write-Error "❌ No agents found"
        $script:ExitCode = 2
        return @{
            Status = "Failed"
            Count = 0
            Expected = $script:ExpectedAgents
            Agents = @()
        }
    }
    elseif ($agentCount -lt $script:ExpectedAgents) {
        Write-Warning "⚠️  Found $agentCount/$script:ExpectedAgents agents"
        if ($script:ExitCode -lt 1) { $script:ExitCode = 1 }
        
        if ($Detailed) {
            Write-Info "`nFound agents:"
            foreach ($agent in $foundAgents | Sort-Object) {
                Write-Host "  • $agent" -ForegroundColor Gray
            }
            
            Write-Info "`nMissing agents:"
            foreach ($expected in $expectedAgentNames) {
                if ($expected -notin $foundAgents) {
                    Write-Host "  • $expected" -ForegroundColor Yellow
                }
            }
        }
        
        return @{
            Status = "Partial"
            Count = $agentCount
            Expected = $script:ExpectedAgents
            Agents = $foundAgents
        }
    }
    else {
        Write-Success "✅ All $script:ExpectedAgents agents found"
        
        if ($Detailed) {
            Write-Info "`nAgent locations:"
            foreach ($dir in $agentDirs) {
                Write-Host "  • $($dir.Type): $($dir.Path)" -ForegroundColor Gray
            }
            Write-Info "`nAvailable agents:"
            foreach ($agent in $foundAgents | Sort-Object) {
                Write-Host "  • $agent" -ForegroundColor Gray
            }
        }
        
        return @{
            Status = "Success"
            Count = $agentCount
            Expected = $script:ExpectedAgents
            Agents = $foundAgents
        }
    }
}

# Check commands
function Test-Commands {
    param($Directories)
    
    Write-Header "Checking Commands"
    
    $expectedCommandNames = @(
        "analyze-project", "auto-commit", "create-test-suite", "debug-issue",
        "explain-code", "fix-errors", "generate-docs", "implement-feature",
        "optimize-performance", "refactor-code", "review-code", "search-codebase",
        "setup-cicd", "setup-project", "suggest-improvements", "update-dependencies",
        "validate-security", "resume-project"
    )
    
    $foundCommands = @()
    $commandDirs = @()
    
    # Check both project and user directories
    foreach ($dirType in @("Project", "User")) {
        $baseDir = $Directories[$dirType]
        if ($baseDir) {
            $commandDir = Join-Path $baseDir "commands"
            if (Test-Path $commandDir) {
                $commandDirs += @{Type = $dirType; Path = $commandDir}
                $commands = Get-ChildItem -Path $commandDir -Filter "*.md" -ErrorAction SilentlyContinue
                foreach ($command in $commands) {
                    $commandName = [System.IO.Path]::GetFileNameWithoutExtension($command.Name)
                    if ($commandName -notin $foundCommands) {
                        $foundCommands += $commandName
                    }
                }
            }
        }
    }
    
    $commandCount = $foundCommands.Count
    
    if ($commandCount -eq 0) {
        Write-Error "❌ No commands found"
        $script:ExitCode = 2
        return @{
            Status = "Failed"
            Count = 0
            Expected = $script:ExpectedCommands
            Commands = @()
        }
    }
    elseif ($commandCount -lt $script:ExpectedCommands) {
        Write-Warning "⚠️  Found $commandCount/$script:ExpectedCommands commands"
        if ($script:ExitCode -lt 1) { $script:ExitCode = 1 }
        
        if ($Detailed) {
            Write-Info "`nFound commands:"
            foreach ($command in $foundCommands | Sort-Object) {
                Write-Host "  • /$command" -ForegroundColor Gray
            }
            
            Write-Info "`nMissing commands:"
            foreach ($expected in $expectedCommandNames) {
                if ($expected -notin $foundCommands) {
                    Write-Host "  • /$expected" -ForegroundColor Yellow
                }
            }
        }
        
        return @{
            Status = "Partial"
            Count = $commandCount
            Expected = $script:ExpectedCommands
            Commands = $foundCommands
        }
    }
    else {
        Write-Success "✅ All $script:ExpectedCommands commands found"
        
        if ($Detailed) {
            Write-Info "`nCommand locations:"
            foreach ($dir in $commandDirs) {
                Write-Host "  • $($dir.Type): $($dir.Path)" -ForegroundColor Gray
            }
            Write-Info "`nAvailable commands:"
            foreach ($command in $foundCommands | Sort-Object) {
                Write-Host "  • /$command" -ForegroundColor Gray
            }
        }
        
        return @{
            Status = "Success"
            Count = $commandCount
            Expected = $script:ExpectedCommands
            Commands = $foundCommands
        }
    }
}

# Check MCPs
function Test-MCPs {
    Write-Header "Checking Model Context Protocol (MCPs)"
    
    $expectedMCPs = @("postgres", "git", "web")
    
    # Check if claude command exists
    $claudeCmd = Get-Command claude -ErrorAction SilentlyContinue
    if (-not $claudeCmd) {
        Write-Error "❌ Claude command not found"
        Write-Info "  Install Claude from: https://claude.ai/download"
        $script:ExitCode = 2
        return @{
            Status = "Failed"
            Count = 0
            Expected = $script:ExpectedMCPs
            MCPs = @()
        }
    }
    
    # Get MCP list
    try {
        $mcpOutput = & claude mcp list 2>&1
        $foundMCPs = @()
        
        foreach ($line in $mcpOutput -split "`n") {
            foreach ($mcp in $expectedMCPs) {
                if ($line -match $mcp) {
                    if ($mcp -notin $foundMCPs) {
                        $foundMCPs += $mcp
                    }
                }
            }
        }
        
        $mcpCount = $foundMCPs.Count
        
        if ($mcpCount -eq 0) {
            Write-Error "❌ No Tier 1 MCPs found"
            $script:ExitCode = 2
            return @{
                Status = "Failed"
                Count = 0
                Expected = $script:ExpectedMCPs
                MCPs = @()
            }
        }
        elseif ($mcpCount -lt $script:ExpectedMCPs) {
            Write-Warning "⚠️  Found $mcpCount/$script:ExpectedMCPs Tier 1 MCPs"
            if ($script:ExitCode -lt 1) { $script:ExitCode = 1 }
            
            if ($Detailed) {
                Write-Info "`nFound MCPs:"
                foreach ($mcp in $foundMCPs) {
                    Write-Host "  • $mcp" -ForegroundColor Gray
                }
                
                Write-Info "`nMissing MCPs:"
                foreach ($expected in $expectedMCPs) {
                    if ($expected -notin $foundMCPs) {
                        Write-Host "  • $expected" -ForegroundColor Yellow
                    }
                }
            }
            
            return @{
                Status = "Partial"
                Count = $mcpCount
                Expected = $script:ExpectedMCPs
                MCPs = $foundMCPs
            }
        }
        else {
            Write-Success "✅ All $script:ExpectedMCPs Tier 1 MCPs found"
            
            if ($Detailed) {
                Write-Info "`nTier 1 MCPs:"
                foreach ($mcp in $foundMCPs) {
                    Write-Host "  • $mcp" -ForegroundColor Gray
                }
            }
            
            return @{
                Status = "Success"
                Count = $mcpCount
                Expected = $script:ExpectedMCPs
                MCPs = $foundMCPs
            }
        }
    }
    catch {
        Write-Error "❌ Failed to check MCPs: $_"
        $script:ExitCode = 2
        return @{
            Status = "Failed"
            Count = 0
            Expected = $script:ExpectedMCPs
            MCPs = @()
        }
    }
}

# Check hooks configuration
function Test-Hooks {
    param($Directories)
    
    Write-Header "Checking Hook Configuration"
    
    $settingsFound = $false
    $settingsLocation = $null
    
    # Check both project and user directories for settings.json
    foreach ($dirType in @("Project", "User")) {
        $baseDir = $Directories[$dirType]
        if ($baseDir) {
            $settingsPath = Join-Path $baseDir "settings.json"
            if (Test-Path $settingsPath) {
                $settingsFound = $true
                $settingsLocation = @{Type = $dirType; Path = $settingsPath}
                
                try {
                    $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json
                    
                    # Check for autoexecute configuration
                    if ($settings.autoexecute -and $settings.autoexecute.afterResponse) {
                        Write-Success "✅ Hook configuration found and valid"
                        
                        if ($Detailed) {
                            Write-Info "`nSettings location:"
                            Write-Host "  • $($settingsLocation.Type): $($settingsLocation.Path)" -ForegroundColor Gray
                            Write-Info "`nConfigured hooks:"
                            foreach ($hook in $settings.autoexecute.afterResponse) {
                                Write-Host "  • $hook" -ForegroundColor Gray
                            }
                        }
                        
                        return @{
                            Status = "Success"
                            Location = $settingsLocation
                            Hooks = $settings.autoexecute.afterResponse
                        }
                    }
                    else {
                        Write-Warning "⚠️  settings.json found but hooks not configured"
                        if ($script:ExitCode -lt 1) { $script:ExitCode = 1 }
                        return @{
                            Status = "Partial"
                            Location = $settingsLocation
                            Hooks = @()
                        }
                    }
                }
                catch {
                    Write-Error "❌ Failed to parse settings.json: $_"
                    $script:ExitCode = 2
                    return @{
                        Status = "Failed"
                        Location = $settingsLocation
                        Hooks = @()
                    }
                }
            }
        }
    }
    
    if (-not $settingsFound) {
        Write-Error "❌ No settings.json found"
        $script:ExitCode = 2
        return @{
            Status = "Failed"
            Location = $null
            Hooks = @()
        }
    }
}

# Show fix suggestions
function Show-FixSuggestions {
    param($Results)
    
    if ($Quiet) { return }
    
    $hasIssues = $false
    foreach ($component in $Results.Keys) {
        if ($Results[$component].Status -ne "Success") {
            $hasIssues = $true
            break
        }
    }
    
    if (-not $hasIssues) { return }
    
    Write-Header "Fix Suggestions"
    
    # Agents fixes
    if ($Results.Agents.Status -ne "Success") {
        Write-Info "To install missing agents:"
        Write-Host "  1. Run the installer script:" -ForegroundColor White
        Write-Host "     ./install-claude-dev-stack.ps1" -ForegroundColor Yellow
        Write-Host "  2. Or download from GitHub:" -ForegroundColor White
        Write-Host "     https://github.com/Zap3515/Claude_Code_Agents" -ForegroundColor Yellow
    }
    
    # Commands fixes
    if ($Results.Commands.Status -ne "Success") {
        Write-Info "`nTo install missing commands:"
        Write-Host "  1. Run the installer script:" -ForegroundColor White
        Write-Host "     ./install-claude-dev-stack.ps1" -ForegroundColor Yellow
        Write-Host "  2. Commands are included with agents installation" -ForegroundColor White
    }
    
    # MCP fixes
    if ($Results.MCPs.Status -ne "Success") {
        Write-Info "`nTo install missing MCPs:"
        Write-Host "  1. Install Claude Desktop from:" -ForegroundColor White
        Write-Host "     https://claude.ai/download" -ForegroundColor Yellow
        Write-Host "  2. Run MCP installer:" -ForegroundColor White
        Write-Host "     ./install-mcps.ps1" -ForegroundColor Yellow
        Write-Host "  3. Restart Claude Desktop" -ForegroundColor White
    }
    
    # Hooks fixes
    if ($Results.Hooks.Status -ne "Success") {
        Write-Info "`nTo configure hooks:"
        Write-Host "  1. Create settings.json in .claude directory" -ForegroundColor White
        Write-Host "  2. Add this configuration:" -ForegroundColor White
        Write-Host @"
{
  "autoexecute": {
    "afterResponse": [
      "npm run lint:fix",
      "npm test -- --passWithNoTests"
    ]
  }
}
"@ -ForegroundColor Yellow
    }
}

# Show usage instructions
function Show-UsageInstructions {
    if ($Quiet) { return }
    
    Write-Header "Using Claude Code Dev Stack"
    
    Write-Info "Agent Usage:"
    Write-Host "  Type @ in Claude to see all available agents" -ForegroundColor White
    Write-Host "  Examples:" -ForegroundColor Gray
    Write-Host "    @backend-services-engineer - Design backend architecture" -ForegroundColor Gray
    Write-Host "    @frontend-ui-developer - Build UI components" -ForegroundColor Gray
    Write-Host "    @security-compliance-auditor - Review security" -ForegroundColor Gray
    
    Write-Info "`nCommand Usage:"
    Write-Host "  Type / in Claude to see all available commands" -ForegroundColor White
    Write-Host "  Examples:" -ForegroundColor Gray
    Write-Host "    /setup-project - Initialize new project" -ForegroundColor Gray
    Write-Host "    /implement-feature - Build new features" -ForegroundColor Gray
    Write-Host "    /review-code - Get code review" -ForegroundColor Gray
    
    Write-Info "`nMCP Usage:"
    Write-Host "  MCPs provide Claude with additional capabilities:" -ForegroundColor White
    Write-Host "    • postgres - Direct database access" -ForegroundColor Gray
    Write-Host "    • git - Repository management" -ForegroundColor Gray
    Write-Host "    • web - Web browsing and search" -ForegroundColor Gray
    
    Write-Info "`nPro Tips:"
    Write-Host "  • Use @master-orchestrator for complex multi-agent tasks" -ForegroundColor Cyan
    Write-Host "  • Combine agents: '@backend @frontend build login system'" -ForegroundColor Cyan
    Write-Host "  • Use /resume-project to continue previous work" -ForegroundColor Cyan
}

# Main execution
function Main {
    if (-not $Quiet) {
        Clear-Host
        Write-Host "Claude Code Dev Stack v$script:Version - Installation Verification" -ForegroundColor Cyan
        Write-Host "================================================================" -ForegroundColor Cyan
        Write-Host "Platform: $(Get-Platform)" -ForegroundColor Gray
        Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    }
    
    # Get Claude directories
    $directories = Get-ClaudeDirectories()
    
    if (-not $Quiet) {
        Write-Info "`nDetected directories:"
        if ($directories.Project) {
            Write-Host "  • Project: $($directories.Project)" -ForegroundColor Gray
        }
        if ($directories.User) {
            Write-Host "  • User: $($directories.User)" -ForegroundColor Gray
        }
        if (-not $directories.Project -and -not $directories.User) {
            Write-Warning "  • No .claude directories found"
        }
    }
    
    # Run all checks
    $results = @{
        Agents = Test-Agents -Directories $directories
        Commands = Test-Commands -Directories $directories
        MCPs = Test-MCPs
        Hooks = Test-Hooks -Directories $directories
    }
    
    # Summary
    if (-not $Quiet) {
        Write-Header "Installation Summary"
        
        $totalComponents = 0
        $successComponents = 0
        
        foreach ($component in @("Agents", "Commands", "MCPs", "Hooks")) {
            $totalComponents++
            if ($results[$component].Status -eq "Success") {
                $successComponents++
                Write-Success "✅ $component - OK"
            }
            elseif ($results[$component].Status -eq "Partial") {
                Write-Warning "⚠️  $component - Partial"
            }
            else {
                Write-Error "❌ $component - Failed"
            }
        }
        
        Write-Host "`nOverall Status: " -NoNewline
        if ($successComponents -eq $totalComponents) {
            Write-Success "FULLY INSTALLED ($successComponents/$totalComponents components)"
        }
        elseif ($successComponents -gt 0) {
            Write-Warning "PARTIALLY INSTALLED ($successComponents/$totalComponents components)"
        }
        else {
            Write-Error "NOT INSTALLED"
        }
        
        # Show suggestions and instructions
        Show-FixSuggestions -Results $results
        Show-UsageInstructions
    }
    else {
        # Quiet mode output
        Write-Host "$successComponents/$totalComponents"
    }
    
    # Exit with appropriate code
    exit $script:ExitCode
}

# Run main function
Main