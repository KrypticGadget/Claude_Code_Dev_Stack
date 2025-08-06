# Claude Code Hooks System Global Installer for Windows
# Version: 2.1 - Fixed Edition
# Installs Python hooks for Claude Code automation

param(
    [switch]$Force,
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"  # Continue on errors
$ProgressPreference = 'SilentlyContinue'

Write-Host "`nClaude Code Hooks Installer v2.1" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "Installing global hooks for automation" -ForegroundColor Yellow

$startTime = Get-Date

# Check Python installation
Write-Host "`nChecking Python installation..." -ForegroundColor Yellow
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
                $pythonPath = (Get-Command $cmd -ErrorAction SilentlyContinue).Source
                Write-Host "✓ Found $pythonVersion at: $pythonPath" -ForegroundColor Green
                break
            }
        }
    } catch {
        continue
    }
}

if (-not $pythonCmd) {
    Write-Host "⚠ Python 3.8+ not found" -ForegroundColor Yellow
    Write-Host "  Hooks require Python. Please install from python.org" -ForegroundColor DarkGray
    Write-Host "  Skipping hooks installation (agents and commands will still work)" -ForegroundColor DarkGray
    exit 0
}

# Find Claude Code root directory
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
    
    # Create default if not found
    $defaultPath = "$env:USERPROFILE\.claude"
    Write-Host "Claude Code root not found. Creating at: $defaultPath" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $defaultPath -Force | Out-Null
    return $defaultPath
}

$claudeRoot = Find-ClaudeCodeRoot
Write-Host "Installing to: $claudeRoot" -ForegroundColor Green

# Create hooks directory structure
$hooksDir = Join-Path $claudeRoot "hooks"
$directories = @(
    $hooksDir,
    (Join-Path $claudeRoot "config"),
    (Join-Path $claudeRoot "state"),
    (Join-Path $claudeRoot "logs")
)

Write-Host "`nCreating directory structure..." -ForegroundColor Yellow
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✓ Created: $dir" -ForegroundColor Green
    }
}

# Create hook Python files from .claude-example
Write-Host "`nCreating hook scripts..." -ForegroundColor Yellow

# Define hook templates
$hookTemplates = @{
    "pre_project.py" = @"
#!/usr/bin/env python3
"""
Pre-project hook - Runs before starting any new project.
Use this to set up project-specific configurations, validate requirements,
or prepare the development environment.
"""

import os
import sys
import json
from datetime import datetime


def main():
    """Main hook function called by Claude."""
    print("🚀 Running pre-project hook...")
    
    # Get project context from environment
    project_name = os.environ.get('CLAUDE_PROJECT_NAME', 'Unknown Project')
    project_path = os.environ.get('CLAUDE_PROJECT_PATH', os.getcwd())
    
    print(f"  Project: {project_name}")
    print(f"  Path: {project_path}")
    
    # Example: Create project metadata file
    metadata = {
        'project_name': project_name,
        'created_at': datetime.now().isoformat(),
        'claude_version': os.environ.get('CLAUDE_VERSION', 'Unknown'),
        'hook_version': '1.0.0'
    }
    
    metadata_path = os.path.join(project_path, '.claude-project.json')
    try:
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"  ✓ Created project metadata at {metadata_path}")
    except Exception as e:
        print(f"  ⚠ Warning: Could not create metadata file: {e}")
    
    # Example: Validate prerequisites
    required_tools = ['git', 'node', 'python']
    missing_tools = []
    
    for tool in required_tools:
        if os.system(f"which {tool} > /dev/null 2>&1") != 0:
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"  ⚠ Warning: Missing tools: {', '.join(missing_tools)}")
        print("    Some features may not work correctly.")
    else:
        print("  ✓ All required tools are installed")
    
    print("✨ Pre-project hook completed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
"@

    "post_project.py" = @"
#!/usr/bin/env python3
"""
Post-project hook - Runs after completing a project.
Use this to clean up resources, generate reports, or archive project data.
"""

import os
import sys
import json
from datetime import datetime


def main():
    """Main hook function called by Claude."""
    print("🏁 Running post-project hook...")
    
    project_name = os.environ.get('CLAUDE_PROJECT_NAME', 'Unknown Project')
    project_path = os.environ.get('CLAUDE_PROJECT_PATH', os.getcwd())
    
    # Example: Update project metadata with completion time
    metadata_path = os.path.join(project_path, '.claude-project.json')
    try:
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            metadata['completed_at'] = datetime.now().isoformat()
            metadata['status'] = 'completed'
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"  ✓ Updated project metadata")
    except Exception as e:
        print(f"  ⚠ Warning: Could not update metadata: {e}")
    
    # Example: Generate project summary
    print(f"\n📊 Project Summary:")
    print(f"  Name: {project_name}")
    print(f"  Path: {project_path}")
    
    # Count files created/modified
    file_count = sum(len(files) for _, _, files in os.walk(project_path))
    print(f"  Total files: {file_count}")
    
    print("\n✨ Post-project hook completed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
"@

    "pre_command.py" = @"
#!/usr/bin/env python3
"""
Pre-command hook - Runs before executing any slash command.
Use this to validate inputs, set up command-specific environment,
or log command usage.
"""

import os
import sys
import json
from datetime import datetime


def main():
    """Main hook function called by Claude."""
    command_name = os.environ.get('CLAUDE_COMMAND_NAME', 'unknown')
    command_args = os.environ.get('CLAUDE_COMMAND_ARGS', '')
    
    print(f"⚡ Running pre-command hook for /{command_name}")
    
    # Example: Log command usage
    log_dir = os.path.expanduser('~/.claude/logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'command': command_name,
        'args': command_args,
        'cwd': os.getcwd()
    }
    
    log_file = os.path.join(log_dir, 'command-usage.jsonl')
    try:
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        print(f"  ✓ Command logged to {log_file}")
    except Exception as e:
        print(f"  ⚠ Warning: Could not log command: {e}")
    
    # Example: Validate command prerequisites
    if command_name == 'new-project' and not os.environ.get('CLAUDE_API_KEY'):
        print("  ⚠ Warning: CLAUDE_API_KEY not set")
        print("    Some features may require API access")
    
    print(f"✅ Pre-command hook completed for /{command_name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
"@

    "post_command.py" = @"
#!/usr/bin/env python3
"""
Post-command hook - Runs after executing any slash command.
Use this to clean up after commands, process results, or trigger
follow-up actions.
"""

import os
import sys
import json
from datetime import datetime


def main():
    """Main hook function called by Claude."""
    command_name = os.environ.get('CLAUDE_COMMAND_NAME', 'unknown')
    command_result = os.environ.get('CLAUDE_COMMAND_RESULT', 'unknown')
    
    print(f"🎯 Running post-command hook for /{command_name}")
    print(f"  Result: {command_result}")
    
    # Example: Send notification for certain commands
    if command_name in ['production-frontend', 'backend-service'] and command_result == 'success':
        print(f"  🔔 Notification: {command_name} completed successfully!")
        # Here you could send actual notifications (email, Slack, etc.)
    
    # Example: Trigger follow-up actions
    if command_name == 'new-project' and command_result == 'success':
        print("  📋 Suggested next steps:")
        print("    1. Run /requirements to gather detailed requirements")
        print("    2. Run /technical-feasibility to assess the project")
        print("    3. Run /project-plan to create a development timeline")
    
    print(f"✨ Post-command hook completed for /{command_name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
"@

    "base_hook.py" = @"
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
        log_dir = os.path.expanduser('~/.claude/logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f'{self.hook_name}.log')
        
        logging.basicConfig(
            level=logging.INFO,
            format=f'[{self.hook_name}] %(asctime)s - %(levelname)s: %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(self.hook_name)
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> int:
        """Execute the hook logic. Return 0 for success, non-zero for failure."""
        pass
    
    def run(self) -> int:
        """Main entry point for the hook."""
        try:
            # Get context from environment or command line
            context_json = os.environ.get('CLAUDE_HOOK_CONTEXT', '{}')
            context = json.loads(context_json)
            
            self.logger.info(f"Starting {self.hook_name} hook")
            result = self.execute(context)
            
            if result == 0:
                self.logger.info(f"{self.hook_name} hook completed successfully")
            else:
                self.logger.error(f"{self.hook_name} hook failed with code {result}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Hook execution failed: {e}", exc_info=True)
            return 1


# Example hook implementation
class ExampleHook(BaseHook):
    def __init__(self):
        super().__init__('example')
    
    def execute(self, context: Dict[str, Any]) -> int:
        self.logger.info(f"Executing with context: {context}")
        # Your hook logic here
        return 0


if __name__ == "__main__":
    # This file can be imported by other hooks
    pass
"@
}

# Create each hook file
$successCount = 0
foreach ($hookName in $hookTemplates.Keys) {
    $hookPath = Join-Path $hooksDir $hookName
    try {
        $hookTemplates[$hookName] | Out-File -FilePath $hookPath -Encoding UTF8
        Write-Host "  ✓ Created: $hookName" -ForegroundColor Green
        $successCount++
    } catch {
        Write-Host "  ✗ Failed to create: $hookName - $_" -ForegroundColor Red
    }
}

Write-Host "Created $successCount hook scripts" -ForegroundColor Green

# Create settings.json with hooks configuration
$settingsPath = Join-Path $claudeRoot "settings.json"
Write-Host "`nUpdating Claude Code settings..." -ForegroundColor Yellow

$settings = @{}
if (Test-Path $settingsPath) {
    try {
        $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json -AsHashtable
    } catch {
        Write-Host "Warning: Could not parse existing settings.json" -ForegroundColor Yellow
        $settings = @{}
    }
}

# Add hooks configuration
if (-not $settings.ContainsKey("hooks")) {
    $settings["hooks"] = @{}
}

$settings.hooks = @{
    "enabled" = $true
    "path" = $hooksDir.Replace('\', '/')
    "pre_project" = @{
        "enabled" = $true
        "script" = "pre_project.py"
    }
    "post_project" = @{
        "enabled" = $true
        "script" = "post_project.py"
    }
    "pre_command" = @{
        "enabled" = $true
        "script" = "pre_command.py"
    }
    "post_command" = @{
        "enabled" = $true
        "script" = "post_command.py"
    }
}

# Also ensure other configurations are present
if (-not $settings.ContainsKey("version")) {
    $settings["version"] = "1.0.0"
}

# Save settings
try {
    $settings | ConvertTo-Json -Depth 10 | Out-File -FilePath $settingsPath -Encoding UTF8
    Write-Host "✓ Updated settings.json" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to update settings.json: $_" -ForegroundColor Red
}

# Create example configuration files
Write-Host "`nCreating configuration files..." -ForegroundColor Yellow

$configDir = Join-Path $claudeRoot "config"

# Create coding standards config
$codingStandards = @{
    "version" = "1.0.0"
    "enabled" = $true
    "standards" = @{
        "max_line_length" = 120
        "indent_size" = 4
        "use_spaces" = $true
        "trim_trailing_whitespace" = $true
        "insert_final_newline" = $true
        "file_encoding" = "utf-8"
    }
    "languages" = @{
        "python" = @{
            "style_guide" = "PEP 8"
            "max_line_length" = 88
        }
        "javascript" = @{
            "style_guide" = "StandardJS"
            "semicolons" = $false
        }
    }
} | ConvertTo-Json -Depth 10

$codingStandards | Out-File -FilePath (Join-Path $configDir "coding_standards.json") -Encoding UTF8

# Create hook configuration
$hookConfig = @{
    "version" = "1.0.0"
    "global" = @{
        "timeout" = 30
        "retry_count" = 3
        "log_level" = "INFO"
    }
    "hooks" = @{
        "pre_project" = @{
            "timeout" = 60
            "required_env" = @("CLAUDE_PROJECT_NAME", "CLAUDE_PROJECT_PATH")
        }
        "post_project" = @{
            "timeout" = 60
            "cleanup" = $true
        }
        "pre_command" = @{
            "timeout" = 15
            "log_commands" = $true
        }
        "post_command" = @{
            "timeout" = 15
            "notifications" = $true
        }
    }
} | ConvertTo-Json -Depth 10

$hookConfig | Out-File -FilePath (Join-Path $configDir "hook_config.json") -Encoding UTF8

Write-Host "✓ Created configuration files" -ForegroundColor Green

# Test hook execution
Write-Host "`nTesting hook installation..." -ForegroundColor Yellow

# Create a simple test
$testScript = @"
import sys
import os
sys.path.insert(0, r'$hooksDir')

try:
    # Test importing base_hook
    from base_hook import BaseHook
    print("✓ Successfully imported base_hook module")
    
    # Test hook files exist
    hook_files = ['pre_project.py', 'post_project.py', 'pre_command.py', 'post_command.py']
    for hook_file in hook_files:
        hook_path = os.path.join(r'$hooksDir', hook_file)
        if os.path.exists(hook_path):
            print(f"✓ Found hook: {hook_file}")
        else:
            print(f"✗ Missing hook: {hook_file}")
    
    print("\n✓ Hook system is properly installed!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
"@

$testPath = Join-Path $env:TEMP "test_hooks.py"
$testScript | Out-File -FilePath $testPath -Encoding UTF8

try {
    & $pythonCmd $testPath
    Remove-Item $testPath -Force
} catch {
    Write-Host "✗ Hook test failed: $_" -ForegroundColor Red
}

# Calculate elapsed time
$endTime = Get-Date
$elapsed = $endTime - $startTime
$elapsedSeconds = [math]::Round($elapsed.TotalSeconds, 1)

# Summary
Write-Host "`n" + "=" * 50 -ForegroundColor Cyan
Write-Host "Installation Complete! (Time: $elapsedSeconds seconds)" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "Hooks installed to: $hooksDir" -ForegroundColor Green
Write-Host "Settings updated: $settingsPath" -ForegroundColor Green
Write-Host "Python executable: $pythonPath" -ForegroundColor Green

Write-Host "`n" + "=" * 50 -ForegroundColor Cyan
Write-Host "Hook System Features:" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "✓ Pre-project hook  - Runs before starting new projects" -ForegroundColor White
Write-Host "✓ Post-project hook - Runs after completing projects" -ForegroundColor White
Write-Host "✓ Pre-command hook  - Runs before slash commands" -ForegroundColor White
Write-Host "✓ Post-command hook - Runs after slash commands" -ForegroundColor White
Write-Host "`nConfiguration files in: $(Join-Path $claudeRoot 'config')" -ForegroundColor White
Write-Host "Log files will be in: $(Join-Path $claudeRoot 'logs')" -ForegroundColor White
Write-Host "=" * 50 -ForegroundColor Cyan

Write-Host "`n✅ Hook system ready to use!" -ForegroundColor Green
Write-Host "Restart Claude Code to activate the hooks." -ForegroundColor Yellow

exit 0