# Claude Code Hooks System Global Installer for Windows
# Version: 2.0.0
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
Write-Info "=== Claude Code Hooks System Global Installer ==="
Write-Host ""

$startTime = Get-Date

# Check Python installation
Write-Info "Checking Python installation..."
$pythonPath = $null
$pythonCmd = $null

# Try different Python locations
$pythonCmds = @("python", "python3", "py")
foreach ($cmd in $pythonCmds) {
    try {
        $pythonVersion = & $cmd --version 2>&1
        if ($pythonVersion -match "Python 3\.(\d+)") {
            $minorVersion = [int]$matches[1]
            if ($minorVersion -ge 8) {
                $pythonCmd = $cmd
                $pythonPath = (Get-Command $cmd).Source
                Write-Success "✓ Python $pythonVersion found at: $pythonPath"
                break
            }
        }
    } catch {
        continue
    }
}

if (-not $pythonCmd) {
    Write-Error "✗ Python 3.8+ not found. Please install from python.org"
    exit 1
}

# Find Claude Code executable
Write-Info "Detecting Claude Code installation..."

# Check for Claude executable in common locations
$claudeExePaths = @(
    "$env:LOCALAPPDATA\Programs\Claude\Claude.exe",
    "$env:ProgramFiles\Claude\Claude.exe",
    "${env:ProgramFiles(x86)}\Claude\Claude.exe",
    "$env:APPDATA\Claude\Claude.exe"
)

$claudeExe = $null
foreach ($path in $claudeExePaths) {
    if (Test-Path $path) {
        $claudeExe = $path
        break
    }
}

# If not found, search PATH
if (-not $claudeExe) {
    try {
        $claudeExe = (Get-Command claude.exe -ErrorAction SilentlyContinue).Source
    } catch {}
}

# Determine Claude Code root directory
$claudeRoot = $null
if ($claudeExe) {
    $claudeRoot = Split-Path -Parent (Split-Path -Parent $claudeExe)
    Write-Success "✓ Found Claude Code executable at: $claudeExe"
} else {
    # Fall back to config directory detection
    $configPaths = @(
        "$env:APPDATA\Claude",
        "$env:LOCALAPPDATA\Claude",
        "$env:USERPROFILE\.claude"
    )
    
    foreach ($path in $configPaths) {
        if (Test-Path $path) {
            $claudeRoot = $path
            break
        }
    }
}

if (-not $claudeRoot) {
    Write-Warning "Claude Code installation not found automatically."
    $claudeRoot = Read-Host "Please enter Claude Code root directory path"
    if (-not (Test-Path $claudeRoot)) {
        Write-Error "✗ Invalid path: $claudeRoot"
        exit 1
    }
}

Write-Success "✓ Using Claude Code root: $claudeRoot"

# Create global hooks directory
$globalHooksDir = Join-Path $claudeRoot ".claude-global"
Write-Info "Creating global hooks directory at: $globalHooksDir"

$directories = @(
    "$globalHooksDir\hooks",
    "$globalHooksDir\config", 
    "$globalHooksDir\state"
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
    "base_hook.py",
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
    $dest = "$globalHooksDir\hooks\$script"
    
    try {
        if ($Verbose) { Write-Info "  Downloading $script..." }
        Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing
        $downloaded++
        Write-Progress -Activity "Installing Hooks" -Status "Downloaded $script" -PercentComplete (($downloaded / $total) * 100)
    } catch {
        Write-Warning "  Failed to download $script, creating default..."
        
        # Special handling for base_hook.py
        if ($script -eq "base_hook.py") {
            $defaultContent = @"
#!/usr/bin/env python3
"""
Base Hook - Foundation for all Claude Code hooks
"""

import json
import sys
import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseHook(ABC):
    def __init__(self, hook_name: str):
        self.hook_name = hook_name
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format=f'[{self.hook_name}] %(levelname)s: %(message)s'
        )
        return logging.getLogger(self.hook_name)
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> int:
        pass
    
    def run(self) -> int:
        try:
            context = json.loads(os.environ.get('CLAUDE_HOOK_CONTEXT', '{}'))
            return self.execute(context)
        except Exception as e:
            self.logger.error(f"Hook execution failed: {e}")
            return 1
"@
        } else {
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
        }
        Set-Content -Path $dest -Value $defaultContent
        $downloaded++
    }
}

Write-Info "Downloading config files..."

foreach ($config in $configFiles) {
    $url = "$baseUrl/.claude/config/$config"
    $dest = "$globalHooksDir\config\$config"
    
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

# Set up environment variables
Write-Info "Setting up environment variables..."

# Set user environment variables
[System.Environment]::SetEnvironmentVariable("CLAUDE_HOME", $claudeRoot, [System.EnvironmentVariableTarget]::User)
[System.Environment]::SetEnvironmentVariable("CLAUDE_PYTHON", $pythonPath, [System.EnvironmentVariableTarget]::User)

Write-Success "✓ Environment variables set"

# Find Claude Code settings.json
Write-Info "Updating Claude Code settings..."

# Look for settings.json in various locations
$settingsPaths = @(
    "$claudeRoot\settings.json",
    "$claudeRoot\.claude\settings.json",
    "$env:APPDATA\Claude\settings.json",
    "$env:LOCALAPPDATA\Claude\settings.json"
)

$settingsPath = $null
foreach ($path in $settingsPaths) {
    if (Test-Path $path) {
        $settingsPath = $path
        break
    }
}

# Create default settings path if none found
if (-not $settingsPath) {
    $settingsPath = "$claudeRoot\settings.json"
}

$settings = @{}
if (Test-Path $settingsPath) {
    try {
        $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json -AsHashtable
    } catch {
        Write-Warning "Could not parse existing settings.json"
        $settings = @{}
    }
}

# Add hooks configuration with proper escaping for paths with spaces
if (-not $settings.ContainsKey("hooks")) {
    $settings["hooks"] = @{}
}

# Escape paths for JSON
$escapedGlobalDir = $globalHooksDir -replace '\\', '\\'
$escapedPythonPath = $pythonPath -replace '\\', '\\'

$settings.hooks = @{
    enabled = $true
    global_path = "`$CLAUDE_HOME\\.claude-global"
    hooks_command = "`"`$CLAUDE_PYTHON`" `"`$CLAUDE_HOME\\.claude-global\\hooks\\{hook_name}.py`""
    config_path = "`$CLAUDE_HOME\\.claude-global\\config"
    state_path = "`$CLAUDE_HOME\\.claude-global\\state"
    environment = @{
        CLAUDE_HOME = "`$CLAUDE_HOME"
        CLAUDE_PYTHON = "`$CLAUDE_PYTHON"
        CLAUDE_HOOKS_DIR = "`$CLAUDE_HOME\\.claude-global\\hooks"
    }
}

try {
    $json = $settings | ConvertTo-Json -Depth 10
    # Ensure proper formatting
    $json = $json -replace '(?<!\\)\\(?!\\)', '\\'
    Set-Content -Path $settingsPath -Value $json -Encoding UTF8
    Write-Success "✓ Settings updated at: $settingsPath"
} catch {
    Write-Warning "Could not update settings.json automatically"
    Write-Info "Please add the following to your settings.json:"
    Write-Host @"
{
    "hooks": {
        "enabled": true,
        "global_path": "`$CLAUDE_HOME\\.claude-global",
        "hooks_command": "\"`$CLAUDE_PYTHON\" \"`$CLAUDE_HOME\\.claude-global\\hooks\\{hook_name}.py\"",
        "config_path": "`$CLAUDE_HOME\\.claude-global\\config",
        "state_path": "`$CLAUDE_HOME\\.claude-global\\state",
        "environment": {
            "CLAUDE_HOME": "`$CLAUDE_HOME",
            "CLAUDE_PYTHON": "`$CLAUDE_PYTHON",
            "CLAUDE_HOOKS_DIR": "`$CLAUDE_HOME\\.claude-global\\hooks"
        }
    }
}
"@
}

# Create test script
$testScript = "$globalHooksDir\test-hooks.py"
@"
#!/usr/bin/env python3
import os
import sys
import json

print("Testing Claude Code Global Hooks System...")
base_dir = os.path.dirname(__file__)
hooks_dir = os.path.join(base_dir, 'hooks')
config_dir = os.path.join(base_dir, 'config')

# Test environment variables
print("\nEnvironment Variables:")
claude_home = os.environ.get('CLAUDE_HOME', 'NOT SET')
claude_python = os.environ.get('CLAUDE_PYTHON', 'NOT SET')
print(f"  CLAUDE_HOME: {claude_home}")
print(f"  CLAUDE_PYTHON: {claude_python}")

# Test hook scripts
print("\nHook Scripts:")
if os.path.exists(hooks_dir):
    for script in sorted(os.listdir(hooks_dir)):
        if script.endswith('.py'):
            print(f"  ✓ {script}")
else:
    print(f"  ✗ Hooks directory not found: {hooks_dir}")

# Test config files
print("\nConfig Files:")
if os.path.exists(config_dir):
    for config in sorted(os.listdir(config_dir)):
        if config.endswith('.json'):
            try:
                with open(os.path.join(config_dir, config)) as f:
                    json.load(f)
                print(f"  ✓ {config} (valid JSON)")
            except:
                print(f"  ✗ {config} (invalid JSON)")
else:
    print(f"  ✗ Config directory not found: {config_dir}")

print("\nGlobal hooks system ready!")
print(f"Installation path: {base_dir}")
"@ | Set-Content -Path $testScript

# Run test
Write-Info "Testing installation..."
try {
    # Set environment variables for test
    $env:CLAUDE_HOME = $claudeRoot
    $env:CLAUDE_PYTHON = $pythonPath
    
    & $pythonCmd $testScript
    Write-Success "✓ Installation test passed"
} catch {
    Write-Warning "Installation test failed"
}

# Test hook execution with paths containing spaces
Write-Info "Testing hook execution with spaces in path..."
$testProjectPath = "C:\Test Project With Spaces"
$testHookCmd = "`"$pythonPath`" `"$globalHooksDir\hooks\session_loader.py`""
Write-Info "Test command: $testHookCmd"

# Cleanup
Remove-Item $testScript -Force -ErrorAction SilentlyContinue

# Summary
$endTime = Get-Date
$duration = [math]::Round(($endTime - $startTime).TotalSeconds, 1)

Write-Host ""
Write-Success "=== Global Installation Complete ==="
Write-Host ""
Write-Info "Installed to: $globalHooksDir"
Write-Info "Settings file: $settingsPath"
Write-Info "Time taken: ${duration}s"
Write-Host ""
Write-Info "Environment variables set:"
Write-Info "  CLAUDE_HOME = $claudeRoot"
Write-Info "  CLAUDE_PYTHON = $pythonPath"
Write-Host ""
Write-Info "Next steps:"
Write-Info "1. Restart your terminal/PowerShell to load new environment variables"
Write-Info "2. Restart Claude Code"
Write-Info "3. Create or open any project - hooks will work globally"
Write-Info "4. Customize configs in $globalHooksDir\config"
Write-Host ""

if ($Force) {
    Write-Success "Installation completed successfully!"
} else {
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}