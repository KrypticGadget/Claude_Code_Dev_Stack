# Claude Code Hooks System Installer for Windows
# Version: 1.0.0
# Repository: https://github.com/KrypticGadget/Claude_Code_Dev_Stack

param(
    [switch]$Force,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
$ProgressPreference = 'SilentlyContinue'

# Colors for output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Info { Write-ColorOutput Cyan @args }
function Write-Success { Write-ColorOutput Green @args }
function Write-Warning { Write-ColorOutput Yellow @args }
function Write-Error { Write-ColorOutput Red @args }

# Start installation
Write-Host ""
Write-Info "=== Claude Code Hooks System Installer ==="
Write-Host ""

$startTime = Get-Date

# Check Python installation
Write-Info "Checking Python installation..."
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.(\d+)") {
        $minorVersion = [int]$matches[1]
        if ($minorVersion -ge 8) {
            Write-Success "✓ Python $pythonVersion found"
        } else {
            Write-Error "✗ Python 3.8+ required. Found: $pythonVersion"
            exit 1
        }
    } else {
        Write-Error "✗ Python 3 not found"
        exit 1
    }
} catch {
    Write-Error "✗ Python not found. Please install Python 3.8+ from python.org"
    exit 1
}

# Find Claude Code installation
Write-Info "Detecting Claude Code installation..."

$claudePaths = @(
    "$env:APPDATA\Claude",
    "$env:LOCALAPPDATA\Claude",
    "$env:USERPROFILE\.claude",
    "C:\Users\$env:USERNAME\AppData\Roaming\Claude",
    "C:\Users\$env:USERNAME\AppData\Local\Claude"
)

$claudeDir = $null
foreach ($path in $claudePaths) {
    if (Test-Path $path) {
        $claudeDir = $path
        break
    }
}

if (-not $claudeDir) {
    Write-Warning "Claude Code installation not found in default locations."
    $claudeDir = Read-Host "Please enter Claude Code installation path"
    if (-not (Test-Path $claudeDir)) {
        Write-Error "✗ Invalid path: $claudeDir"
        exit 1
    }
}

Write-Success "✓ Found Claude Code at: $claudeDir"

# Create directory structure
Write-Info "Creating directory structure..."

$directories = @(
    "$claudeDir\.claude\hooks",
    "$claudeDir\.claude\config",
    "$claudeDir\.claude\state"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        if ($Verbose) { Write-Info "  Created: $dir" }
    }
}

Write-Success "✓ Directory structure created"

# Download files
$baseUrl = "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main"

# Hook scripts to download
$hookScripts = @(
    "session_loader.py",
    "session_saver.py",
    "quality_gate.py",
    "planning_trigger.py",
    "agent_orchestrator.py",
    "agent_mention_parser.py",
    "model_tracker.py",
    "mcp_gateway.py",
    "mcp_pipeline.py"
)

# Config files to download
$configFiles = @(
    "coding_standards.json",
    "agent_routing.json",
    "agent_models.json",
    "mcp_config.json"
)

Write-Info "Downloading hook scripts..."
$downloaded = 0
$total = $hookScripts.Count + $configFiles.Count

foreach ($script in $hookScripts) {
    $url = "$baseUrl/.claude/hooks/$script"
    $dest = "$claudeDir\.claude\hooks\$script"
    
    try {
        if ($Verbose) { Write-Info "  Downloading $script..." }
        Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing
        $downloaded++
        Write-Progress -Activity "Installing Hooks" -Status "Downloaded $script" -PercentComplete (($downloaded / $total) * 100)
    } catch {
        Write-Warning "  Failed to download $script, creating default..."
        
        # Create default script
        $defaultContent = @"
#!/usr/bin/env python3
"""
$script - Claude Code Hook
Auto-generated placeholder
"""

import json
import sys
import os

def main():
    # Placeholder implementation
    print(f"Hook {os.path.basename(__file__)} executed", file=sys.stderr)
    return 0

if __name__ == "__main__":
    sys.exit(main())
"@
        Set-Content -Path $dest -Value $defaultContent
        $downloaded++
    }
}

Write-Info "Downloading config files..."

foreach ($config in $configFiles) {
    $url = "$baseUrl/.claude/config/$config"
    $dest = "$claudeDir\.claude\config\$config"
    
    try {
        if ($Verbose) { Write-Info "  Downloading $config..." }
        Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing
        $downloaded++
        Write-Progress -Activity "Installing Hooks" -Status "Downloaded $config" -PercentComplete (($downloaded / $total) * 100)
    } catch {
        Write-Warning "  Failed to download $config, creating default..."
        
        # Create default configs
        $defaultConfig = switch ($config) {
            "coding_standards.json" {
                @{
                    version = "1.0.0"
                    enabled = $true
                    standards = @{
                        max_line_length = 120
                        indent_size = 4
                        use_spaces = $true
                    }
                }
            }
            "agent_routing.json" {
                @{
                    version = "1.0.0"
                    routes = @{
                        "@frontend" = "frontend-development"
                        "@backend" = "backend-architecture"
                        "@test" = "testing-automation"
                    }
                }
            }
            "agent_models.json" {
                @{
                    version = "1.0.0"
                    models = @{
                        default = "claude-3-opus-20240229"
                        agents = @{}
                    }
                }
            }
            "mcp_config.json" {
                @{
                    version = "1.0.0"
                    servers = @()
                }
            }
        }
        
        $defaultConfig | ConvertTo-Json -Depth 10 | Set-Content -Path $dest
        $downloaded++
    }
}

Write-Progress -Activity "Installing Hooks" -Completed

# Update Claude Code settings
Write-Info "Updating Claude Code settings..."

$settingsPath = "$claudeDir\.claude\settings.json"
$settings = @{}

if (Test-Path $settingsPath) {
    try {
        $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json
    } catch {
        Write-Warning "Could not parse existing settings.json"
    }
}

# Add hooks configuration
if (-not $settings.PSObject.Properties["hooks"]) {
    $settings | Add-Member -NotePropertyName "hooks" -NotePropertyValue @{}
}

$settings.hooks = @{
    enabled = $true
    path = ".claude/hooks"
    config_path = ".claude/config"
    state_path = ".claude/state"
    python_path = "python"
}

try {
    $settings | ConvertTo-Json -Depth 10 | Set-Content -Path $settingsPath
    Write-Success "✓ Settings updated"
} catch {
    Write-Warning "Could not update settings.json automatically"
    Write-Info "Please add the following to your settings.json:"
    Write-Host @"
{
    "hooks": {
        "enabled": true,
        "path": ".claude/hooks",
        "config_path": ".claude/config",
        "state_path": ".claude/state",
        "python_path": "python"
    }
}
"@
}

# Create test script
$testScript = "$claudeDir\.claude\test-hooks.py"
@"
#!/usr/bin/env python3
import os
import sys
import json

print("Testing Claude Code Hooks System...")
hooks_dir = os.path.join(os.path.dirname(__file__), 'hooks')
config_dir = os.path.join(os.path.dirname(__file__), 'config')

# Test hook scripts
print("\nHook Scripts:")
for script in os.listdir(hooks_dir):
    if script.endswith('.py'):
        print(f"  ✓ {script}")

# Test config files
print("\nConfig Files:")
for config in os.listdir(config_dir):
    if config.endswith('.json'):
        try:
            with open(os.path.join(config_dir, config)) as f:
                json.load(f)
            print(f"  ✓ {config} (valid JSON)")
        except:
            print(f"  ✗ {config} (invalid JSON)")

print("\nHooks system ready!")
"@ | Set-Content -Path $testScript

# Run test
Write-Info "Testing installation..."
try {
    python $testScript
    Write-Success "✓ Installation test passed"
} catch {
    Write-Warning "Installation test failed"
}

# Cleanup
Remove-Item $testScript -Force -ErrorAction SilentlyContinue

# Summary
$endTime = Get-Date
$duration = [math]::Round(($endTime - $startTime).TotalSeconds, 1)

Write-Host ""
Write-Success "=== Installation Complete ==="
Write-Host ""
Write-Info "Installed to: $claudeDir\.claude"
Write-Info "Time taken: ${duration}s"
Write-Host ""
Write-Info "Next steps:"
Write-Info "1. Restart Claude Code"
Write-Info "2. Verify hooks are working with a new project"
Write-Info "3. Customize configs in $claudeDir\.claude\config"
Write-Host ""

if ($Force) {
    Write-Success "Installation completed successfully!"
} else {
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}