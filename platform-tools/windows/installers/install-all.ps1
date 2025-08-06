# Claude Code Dev Stack - Master Installer for Windows
# Version: 2.1
# Installs all components: Agents, Commands, Hooks, and MCPs

param(
    [switch]$SkipAgents,
    [switch]$SkipCommands,
    [switch]$SkipHooks,
    [switch]$SkipMCPs,
    [switch]$Force
)

$ErrorActionPreference = "Continue"
$ProgressPreference = 'SilentlyContinue'

# ASCII Art Banner
$banner = @"

╔═══════════════════════════════════════════════════════════════╗
║     Claude Code Dev Stack - Master Installer v2.1             ║
║     Complete AI Development Environment Setup                  ║
╚═══════════════════════════════════════════════════════════════╝

"@

Write-Host $banner -ForegroundColor Cyan
Write-Host "Starting complete installation..." -ForegroundColor Yellow
Write-Host ""

$startTime = Get-Date

# Track overall progress
$components = @{
    "Agents" = @{ Enabled = !$SkipAgents; Status = "Pending"; Script = "install-agents.ps1" }
    "Commands" = @{ Enabled = !$SkipCommands; Status = "Pending"; Script = "install-commands.ps1" }
    "Hooks" = @{ Enabled = !$SkipHooks; Status = "Pending"; Script = "install-hooks.ps1" }
    "MCPs" = @{ Enabled = !$SkipMCPs; Status = "Pending"; Script = "install-mcps.ps1" }
}

# When running from iwr | iex, we need to use GitHub URLs directly
$baseUrl = "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main"
$installersUrl = "$baseUrl/platform-tools/windows/installers"

# Function to run component installer
function Install-Component {
    param(
        [string]$Name,
        [string]$ScriptName,
        [string]$Description
    )
    
    Write-Host "`n══════════════════════════════════════════════════" -ForegroundColor DarkGray
    Write-Host "Installing $Name..." -ForegroundColor Cyan
    Write-Host "══════════════════════════════════════════════════" -ForegroundColor DarkGray
    
    # Download and execute script from GitHub
    $scriptUrl = "$installersUrl/$ScriptName"
    
    try {
        Write-Host "Downloading from: $scriptUrl" -ForegroundColor DarkGray
        $scriptContent = Invoke-WebRequest -Uri $scriptUrl -UseBasicParsing -TimeoutSec 30
        
        # Execute the downloaded script
        Invoke-Expression $scriptContent.Content
        
        Write-Host "✓ $Name installed successfully!" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "✗ Error installing $Name`: $_" -ForegroundColor Red
        return $false
    }
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check for admin rights (recommended but not required)
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "⚠ Running without administrator privileges" -ForegroundColor Yellow
    Write-Host "  Some features may require manual configuration" -ForegroundColor DarkGray
}

# Check for required tools
$requiredTools = @{
    "git" = @{ Description = "Git version control"; Required = $false }
    "node" = @{ Description = "Node.js runtime"; Required = $false }
    "npm" = @{ Description = "Node package manager"; Required = $false }
}

$optionalTools = @{
    "python" = @{ Description = "Python 3.8+ (needed for hooks)"; Required = $false }
}

$missingCritical = @()
foreach ($tool in $requiredTools.Keys) {
    try {
        $null = Get-Command $tool -ErrorAction Stop
        Write-Host "✓ Found $tool" -ForegroundColor Green
    } catch {
        if ($requiredTools[$tool].Required) {
            $missingCritical += $tool
        }
        Write-Host "⚠ Missing $tool - $($requiredTools[$tool].Description)" -ForegroundColor Yellow
    }
}

foreach ($tool in $optionalTools.Keys) {
    try {
        $null = Get-Command $tool -ErrorAction Stop
        Write-Host "✓ Found $tool" -ForegroundColor Green
    } catch {
        Write-Host "⚠ Optional: $tool - $($optionalTools[$tool].Description)" -ForegroundColor DarkYellow
        if ($tool -eq "python" -and -not $SkipHooks) {
            Write-Host "  Note: Hooks will not be installed without Python" -ForegroundColor DarkGray
            $SkipHooks = $true
        }
    }
}

if ($missingCritical.Count -gt 0 -and -not $Force) {
    Write-Host "`n✗ Missing critical tools: $($missingCritical -join ', ')" -ForegroundColor Red
    Write-Host "Please install missing tools or use -Force to continue anyway" -ForegroundColor Yellow
    exit 1
}

# Install components
$results = @{}

# 1. Install Agents (28 specialized AI agents)
if ($components["Agents"].Enabled) {
    $results["Agents"] = Install-Component -Name "AI Agents (28 agents)" -ScriptName $components["Agents"].Script -Description "Specialized AI agents for every development task"
    $components["Agents"].Status = if ($results["Agents"]) { "Success" } else { "Failed" }
}

# 2. Install Commands (18 slash commands)
if ($components["Commands"].Enabled) {
    $results["Commands"] = Install-Component -Name "Slash Commands (18 commands)" -ScriptName $components["Commands"].Script -Description "Power commands for rapid development"
    $components["Commands"].Status = if ($results["Commands"]) { "Success" } else { "Failed" }
}

# 3. Install Hooks (Python automation)
if ($components["Hooks"].Enabled) {
    $results["Hooks"] = Install-Component -Name "Hook System" -ScriptName $components["Hooks"].Script -Description "Automated workflows and quality checks"
    $components["Hooks"].Status = if ($results["Hooks"]) { "Success" } else { "Failed" }
}

# 4. Install MCPs (Model Context Protocol servers)
if ($components["MCPs"].Enabled) {
    $results["MCPs"] = Install-Component -Name "MCP Servers" -ScriptName $components["MCPs"].Script -Description "Enhanced capabilities through MCP tools"
    $components["MCPs"].Status = if ($results["MCPs"]) { "Success" } else { "Failed" }
}

# Calculate results
$totalComponents = ($components.Values | Where-Object { $_.Enabled }).Count
$successCount = ($results.Values | Where-Object { $_ -eq $true }).Count
$failCount = $totalComponents - $successCount

# Calculate elapsed time
$endTime = Get-Date
$elapsed = $endTime - $startTime
$elapsedMinutes = [math]::Round($elapsed.TotalMinutes, 1)

# Display summary
Write-Host "`n" + "═" * 60 -ForegroundColor Cyan
Write-Host "INSTALLATION COMPLETE" -ForegroundColor Cyan
Write-Host "═" * 60 -ForegroundColor Cyan

Write-Host "`nComponent Status:" -ForegroundColor Yellow
foreach ($component in $components.Keys) {
    if ($components[$component].Enabled) {
        $status = $components[$component].Status
        $color = if ($status -eq "Success") { "Green" } else { "Red" }
        $icon = if ($status -eq "Success") { "✓" } else { "✗" }
        Write-Host "  $icon $component`: $status" -ForegroundColor $color
    } else {
        Write-Host "  - $component`: Skipped" -ForegroundColor DarkGray
    }
}

Write-Host "`nSummary:" -ForegroundColor Yellow
Write-Host "  Total components: $totalComponents" -ForegroundColor White
Write-Host "  Successful: $successCount" -ForegroundColor Green
if ($failCount -gt 0) {
    Write-Host "  Failed: $failCount" -ForegroundColor Red
}
Write-Host "  Time elapsed: $elapsedMinutes minutes" -ForegroundColor White

# Provide next steps
Write-Host "`n" + "═" * 60 -ForegroundColor Cyan
Write-Host "NEXT STEPS" -ForegroundColor Cyan
Write-Host "═" * 60 -ForegroundColor Cyan

$nextSteps = @"
1. Restart Claude Desktop to activate all features

2. Test your installation:
   - Type @ to see available agents
   - Type / to see available commands
   - MCP tools will appear in the tools menu

3. Start building:
   /new-project "My Awesome App"
   @backend-services @frontend-architecture

4. Documentation:
   - Guide: $rootDir\docs\MASTER_PROMPTING_GUIDE_V2.md
   - Examples: $rootDir\.claude-example\

5. Get help:
   - GitHub: https://github.com/KrypticGadget/Claude_Code_Dev_Stack
   - Discord: https://discord.gg/claude-code
"@

Write-Host $nextSteps -ForegroundColor White

# Check if any components failed
if ($failCount -gt 0) {
    Write-Host "`n⚠ Some components failed to install" -ForegroundColor Yellow
    Write-Host "You can retry individual components:" -ForegroundColor Yellow
    
    if ($components["Agents"].Status -eq "Failed") {
        Write-Host "  .\install-agents.ps1" -ForegroundColor DarkGray
    }
    if ($components["Commands"].Status -eq "Failed") {
        Write-Host "  .\install-commands.ps1" -ForegroundColor DarkGray
    }
    if ($components["Hooks"].Status -eq "Failed") {
        Write-Host "  .\install-hooks.ps1" -ForegroundColor DarkGray
    }
    if ($components["MCPs"].Status -eq "Failed") {
        Write-Host "  .\install-mcps.ps1" -ForegroundColor DarkGray
    }
}

Write-Host "`n✨ Happy coding with Claude Code Dev Stack!" -ForegroundColor Green

# Exit with appropriate code
if ($failCount -eq 0) {
    exit 0
} else {
    exit 1
}