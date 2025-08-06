# Claude Code Slash Commands Installer for Windows
# Version: 2.1 - Fixed Edition
# Installs 18 slash commands globally to Claude Code root directory

$ErrorActionPreference = "Continue"  # Continue on errors
$ProgressPreference = 'SilentlyContinue'  # Suppress built-in progress bars for speed

Write-Host "`nClaude Code Slash Commands Installer v2.1" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Installing slash commands globally for all projects" -ForegroundColor Yellow

# Start timer
$startTime = Get-Date

# Function to find Claude Code root installation
function Find-ClaudeCodeRoot {
    # Check environment variable first
    if ($env:CLAUDE_CODE_ROOT) {
        Write-Host "Using CLAUDE_CODE_ROOT environment variable: $env:CLAUDE_CODE_ROOT" -ForegroundColor Green
        return $env:CLAUDE_CODE_ROOT
    }
    
    # Common Claude Code root paths
    $possiblePaths = @(
        "$env:USERPROFILE\.claude",
        "$env:APPDATA\Claude",
        "$env:LOCALAPPDATA\Claude",
        "$env:USERPROFILE\AppData\Roaming\Claude",
        "$env:USERPROFILE\AppData\Local\Claude",
        "$env:USERPROFILE\.claude-code",
        "$env:APPDATA\claude-code"
    )
    
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            # Verify this is the root by checking for config files
            $configFiles = @("settings.json", "agent-config.yaml", ".claude")
            foreach ($config in $configFiles) {
                if (Test-Path (Join-Path $path $config)) {
                    Write-Host "Found Claude Code root directory with $config" -ForegroundColor Green
                    return $path
                }
            }
        }
    }
    
    # If not found, create in the default location
    $defaultPath = "$env:USERPROFILE\.claude"
    Write-Host "Claude Code root not found. Creating at: $defaultPath" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $defaultPath -Force | Out-Null
    return $defaultPath
}

# Find Claude Code root directory
$claudeRoot = Find-ClaudeCodeRoot
$commandsPath = Join-Path $claudeRoot "commands"
$registryPath = Join-Path $claudeRoot "commands-registry.json"
$settingsPath = Join-Path $claudeRoot "settings.json"

Write-Host "Installing to: $commandsPath" -ForegroundColor Green

# Create directory if it doesn't exist
if (!(Test-Path $commandsPath)) {
    Write-Host "Creating commands directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path $commandsPath | Out-Null
}

# List of all 18 command files
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

$baseUrl = "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example/commands/"
$totalCommands = $commands.Count
$completed = 0
$failed = 0
$failedCommands = @()

Write-Host "`nStarting command installation..." -ForegroundColor Yellow
Write-Host "=" * 50 -ForegroundColor DarkGray

# Initialize command registry
$commandRegistry = @{
    version = "2.1"
    commands = @()
    installed = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
}

# Download each command with detailed progress
foreach ($command in $commands) {
    $completed++
    $commandName = [System.IO.Path]::GetFileNameWithoutExtension($command)
    
    # Show detailed progress
    Write-Host "`nInstalling command $completed/$totalCommands`: /$commandName" -ForegroundColor Cyan
    Write-Host "  Downloading from: $baseUrl$command" -ForegroundColor DarkGray
    
    try {
        $url = $baseUrl + $command
        $destination = Join-Path $commandsPath $command
        
        # Download with proper error handling
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 30 -ErrorAction Stop
        
        # Verify content was downloaded
        if ($response.Content.Length -eq 0) {
            throw "Downloaded file is empty"
        }
        
        # Save with proper encoding
        $content = [System.Text.Encoding]::UTF8.GetString($response.Content)
        [System.IO.File]::WriteAllText($destination, $content, [System.Text.Encoding]::UTF8)
        
        # Verify file was created
        if (Test-Path $destination) {
            $fileSize = (Get-Item $destination).Length
            if ($fileSize -gt 0) {
                Write-Host "  ✓ Downloaded successfully ($fileSize bytes)" -ForegroundColor Green
                Write-Host "  ✓ Command ready: /$commandName" -ForegroundColor Green
                
                # Add to registry
                $commandRegistry.commands += @{
                    name = $commandName
                    file = $command
                    path = $destination.Replace('\', '/')
                    description = "/$commandName - Claude Code development command"
                    trigger = "/$commandName"
                }
            } else {
                throw "File created but is empty"
            }
        } else {
            throw "File was not created"
        }
    }
    catch {
        $failed++
        $failedCommands += $commandName
        $errorMsg = $_.Exception.Message
        Write-Host "  ✗ Failed: $errorMsg" -ForegroundColor Red
        
        # Log error
        $errorLog = Join-Path $claudeRoot "command-install-errors.log"
        $errorEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Failed to download $command: $errorMsg`n"
        Add-Content -Path $errorLog -Value $errorEntry -Force
    }
    
    # Small delay to avoid rate limiting
    Start-Sleep -Milliseconds 300
}

# Save command registry
Write-Host "`nCreating command registry..." -ForegroundColor Yellow
try {
    $commandRegistry | ConvertTo-Json -Depth 4 | Out-File -FilePath $registryPath -Encoding UTF8
    Write-Host "✓ Command registry created at: $registryPath" -ForegroundColor Green
}
catch {
    Write-Host "✗ Failed to create command registry: $_" -ForegroundColor Red
}

# Update Claude Code settings
if (Test-Path $settingsPath) {
    Write-Host "`nUpdating Claude Code settings..." -ForegroundColor Yellow
    try {
        $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json
        
        # Add or update commands configuration
        if (-not $settings.PSObject.Properties["commands"]) {
            $settings | Add-Member -NotePropertyName "commands" -NotePropertyValue @{}
        }
        
        $settings.commands = @{
            "enabled" = $true
            "globalPath" = $commandsPath.Replace('\', '/')
            "registryFile" = $registryPath.Replace('\', '/')
            "prefix" = "/"
            "autoComplete" = $true
        }
        
        $settings | ConvertTo-Json -Depth 4 | Out-File -FilePath $settingsPath -Encoding UTF8
        Write-Host "✓ Updated settings.json with command configuration" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ Failed to update settings: $_" -ForegroundColor Red
    }
} else {
    # Create new settings.json
    Write-Host "`nCreating new settings.json..." -ForegroundColor Yellow
    @{
        "version" = "1.0.0"
        "commands" = @{
            "enabled" = $true
            "globalPath" = $commandsPath.Replace('\', '/')
            "registryFile" = $registryPath.Replace('\', '/')
            "prefix" = "/"
            "autoComplete" = $true
        }
    } | ConvertTo-Json -Depth 4 | Out-File -FilePath $settingsPath -Encoding UTF8
    Write-Host "✓ Created settings.json with command configuration" -ForegroundColor Green
}

# Calculate elapsed time
$endTime = Get-Date
$elapsed = $endTime - $startTime
$elapsedSeconds = [math]::Round($elapsed.TotalSeconds, 1)

# Summary
Write-Host "`n" + "=" * 50 -ForegroundColor Cyan
Write-Host "Installation Complete! (Time: $elapsedSeconds seconds)" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "Total commands: $totalCommands" -ForegroundColor White
Write-Host "Successfully installed: $($totalCommands - $failed)" -ForegroundColor Green

if ($failed -gt 0) {
    Write-Host "Failed: $failed" -ForegroundColor Red
    Write-Host "`nFailed commands:" -ForegroundColor Red
    $failedCommands | ForEach-Object { 
        Write-Host "  - /$_" -ForegroundColor Red 
    }
    
    $errorLog = Join-Path $claudeRoot "command-install-errors.log"
    if (Test-Path $errorLog) {
        Write-Host "`nError details saved to: $errorLog" -ForegroundColor Yellow
    }
}

Write-Host "`nCommands installed to: $commandsPath" -ForegroundColor Green

# Test command availability
Write-Host "`nVerifying installation..." -ForegroundColor Yellow
$verificationPassed = $true

$testCommands = @("new-project.md", "backend-service.md", "frontend-mockup.md")
foreach ($testCommand in $testCommands) {
    $testPath = Join-Path $commandsPath $testCommand
    if (Test-Path $testPath) {
        $fileSize = (Get-Item $testPath).Length
        $cmdName = [System.IO.Path]::GetFileNameWithoutExtension($testCommand)
        if ($fileSize -gt 100) {  # Commands should be at least 100 bytes
            Write-Host "✓ Verified: /$cmdName ($fileSize bytes)" -ForegroundColor Green
        } else {
            Write-Host "✗ File too small: /$cmdName ($fileSize bytes)" -ForegroundColor Red
            $verificationPassed = $false
        }
    } else {
        $cmdName = [System.IO.Path]::GetFileNameWithoutExtension($testCommand)
        Write-Host "✗ Missing: /$cmdName" -ForegroundColor Red
        $verificationPassed = $false
    }
}

if ($verificationPassed) {
    Write-Host "`n✓ All verification checks passed!" -ForegroundColor Green
} else {
    Write-Host "`n⚠ Some verification checks failed." -ForegroundColor Yellow
}

Write-Host "`n" + "=" * 50 -ForegroundColor Cyan
Write-Host "Usage Instructions:" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "These commands are now globally available in ALL projects!" -ForegroundColor White
Write-Host "`nType '/' followed by command name in any chat:" -ForegroundColor White
Write-Host "  /new-project       - Start a new project" -ForegroundColor Green
Write-Host "  /backend-service   - Build backend services" -ForegroundColor Green
Write-Host "  /frontend-mockup   - Create frontend mockup" -ForegroundColor Green
Write-Host "  /database-design   - Design database schema" -ForegroundColor Green
Write-Host "  /requirements      - Gather requirements" -ForegroundColor Green
Write-Host "`nView all commands: $commandsPath" -ForegroundColor White
Write-Host "=" * 50 -ForegroundColor Cyan

# Clean up and exit
if ($failed -eq 0 -and $verificationPassed) {
    Write-Host "`n✅ Installation completed successfully!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n⚠ Installation completed with warnings" -ForegroundColor Yellow
    exit 0
}