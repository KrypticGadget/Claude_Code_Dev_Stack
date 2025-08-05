# Claude Code Dev Stack v2.1 - Uninstaller Scripts Installer
# Downloads and installs the uninstaller scripts

$ErrorActionPreference = "Stop"

# Colors
function Write-Success { param($Text) Write-Host "✓ $Text" -ForegroundColor Green }
function Write-Error { param($Text) Write-Host "✗ $Text" -ForegroundColor Red }
function Write-Info { param($Text) Write-Host "ℹ $Text" -ForegroundColor Blue }

Write-Host "`n📦 Installing Claude Code Uninstaller Scripts..." -ForegroundColor Cyan

# GitHub repository details
$repoOwner = "Codewordium"
$repoName = "Claude_Code_Agents"
$branch = "main"
$basePath = "Claude_Code_Dev_Stack"

# Uninstaller scripts to download
$scripts = @(
    "uninstall-all.ps1",
    "uninstall-agents.ps1",
    "uninstall-commands.ps1",
    "uninstall-mcps.ps1",
    "uninstall-hooks.ps1"
)

# Create uninstallers directory
$uninstallersDir = Join-Path $PWD "uninstallers"
if (-not (Test-Path $uninstallersDir)) {
    New-Item -ItemType Directory -Path $uninstallersDir -Force | Out-Null
    Write-Success "Created uninstallers directory"
}

# Download each script
$downloadedCount = 0
foreach ($script in $scripts) {
    try {
        $url = "https://raw.githubusercontent.com/$repoOwner/$repoName/$branch/$basePath/$script"
        $destination = Join-Path $uninstallersDir $script
        
        Write-Host "Downloading $script..." -NoNewline
        Invoke-WebRequest -Uri $url -OutFile $destination -UseBasicParsing
        Write-Host " Done" -ForegroundColor Green
        
        $downloadedCount++
    }
    catch {
        Write-Host " Failed" -ForegroundColor Red
        Write-Error "Failed to download $script`: $_"
    }
}

# Create a convenient run-uninstaller.ps1 in current directory
$runUninstallerContent = @'
# Claude Code Dev Stack - Run Uninstaller
# Convenient wrapper to run the uninstaller scripts

param(
    [Parameter(Position=0)]
    [ValidateSet("all", "agents", "commands", "mcps", "hooks")]
    [string]$Component = "all",
    
    [switch]$Force,
    [switch]$WhatIf,
    [switch]$Backup
)

$uninstallersDir = Join-Path $PSScriptRoot "uninstallers"
$scriptName = "uninstall-$Component.ps1"
$scriptPath = Join-Path $uninstallersDir $scriptName

if (-not (Test-Path $scriptPath)) {
    Write-Host "Error: Uninstaller script not found: $scriptPath" -ForegroundColor Red
    Write-Host "Run the install-uninstallers.ps1 script first." -ForegroundColor Yellow
    exit 1
}

# Build arguments
$args = @()
if ($Force) { $args += "-Force" }
if ($WhatIf) { $args += "-WhatIf" }
if ($Backup -and $Component -eq "all") { $args += "-Backup" }

# Execute the uninstaller
& $scriptPath @args
'@

$runUninstallerPath = Join-Path $PWD "run-uninstaller.ps1"
Set-Content -Path $runUninstallerPath -Value $runUninstallerContent
Write-Success "Created run-uninstaller.ps1"

# Summary
Write-Host "`n✅ Installation Complete!" -ForegroundColor Green
Write-Host "Downloaded $downloadedCount/$($scripts.Count) uninstaller scripts" -ForegroundColor Cyan

Write-Host "`n📋 Usage Examples:" -ForegroundColor Yellow
Write-Host "  .\run-uninstaller.ps1              # Interactive menu"
Write-Host "  .\run-uninstaller.ps1 all -Force   # Remove everything without confirmation"
Write-Host "  .\run-uninstaller.ps1 agents       # Remove agents only"
Write-Host "  .\run-uninstaller.ps1 all -WhatIf  # Dry run to see what would be removed"
Write-Host "  .\run-uninstaller.ps1 all -Backup  # Create backup before removal"

Write-Host "`n💡 Direct script usage:" -ForegroundColor Yellow
Write-Host "  .\uninstallers\uninstall-all.ps1 -Agents -Commands -Force"
Write-Host "  .\uninstallers\uninstall-mcps.ps1 -WhatIf"

Write-Info "Uninstaller scripts saved in: $uninstallersDir"