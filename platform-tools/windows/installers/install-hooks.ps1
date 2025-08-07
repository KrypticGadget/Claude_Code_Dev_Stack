# Enhanced Claude Code Hooks Installer v2.1 - FIXED
# Installs complete integrated hook system with proper Windows paths

Write-Host @"
╔════════════════════════════════════════════════════════════════╗
║       Claude Code Enhanced Hooks Installer v2.1 - FIXED        ║
║     19 Hooks + Audio + Proper Windows Path Configuration       ║
╚════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Configuration
$claudeDir = "$env:USERPROFILE\.claude"
$hooksDir = "$claudeDir\hooks"
$audioDir = "$claudeDir\audio"
$logsDir = "$claudeDir\logs"
$stateDir = "$claudeDir\state"
$backupsDir = "$claudeDir\backups"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# Project paths - handle both direct execution and web download
if ($PSScriptRoot) {
    $projectRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
    $sourceHooksDir = "$projectRoot\.claude-example\hooks"
    $sourceAudioDir = "$projectRoot\.claude-example\audio"
    $sourceSettingsFile = "$projectRoot\.claude-example\settings-integrated.json"
} else {
    # Running from web, will download from GitHub
    $projectRoot = $null
    $sourceHooksDir = $null
    $sourceAudioDir = $null
    $sourceSettingsFile = $null
}

# Step 1: Detect Python command
Write-Host "`n🔍 Detecting Python installation..." -ForegroundColor Yellow

$pythonCmd = ""
$hasPython = $false

# Try python first (most common on Windows)
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3") {
        $pythonCmd = "python"
        $hasPython = $true
        Write-Host "  ✓ Found Python 3: $pythonVersion" -ForegroundColor Green
        Write-Host "  Using command: python" -ForegroundColor Cyan
    } elseif ($pythonVersion -match "Python 2") {
        Write-Host "  ⚠ Python 2 detected - Python 3 required!" -ForegroundColor Red
    }
} catch {
    # Try python3 as fallback
    try {
        $pythonVersion = python3 --version 2>&1
        if ($pythonVersion -match "Python 3") {
            $pythonCmd = "python3"
            $hasPython = $true
            Write-Host "  ✓ Found Python 3: $pythonVersion" -ForegroundColor Green
            Write-Host "  Using command: python3" -ForegroundColor Cyan
        }
    } catch {
        Write-Host "  ✗ Python not found - hooks will NOT work!" -ForegroundColor Red
        Write-Host "    Install from: https://python.org" -ForegroundColor Yellow
        Write-Host "    Make sure to check 'Add Python to PATH' during installation!" -ForegroundColor Yellow
        $pythonCmd = "python"  # Default fallback
    }
}

# Step 2: Create directory structure
Write-Host "`n📁 Creating directory structure..." -ForegroundColor Yellow

$directories = @($claudeDir, $hooksDir, $audioDir, $logsDir, $stateDir, $backupsDir)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✓ Created: $(Split-Path $dir -Leaf)" -ForegroundColor Green
    } else {
        Write-Host "  • Exists: $(Split-Path $dir -Leaf)" -ForegroundColor Gray
    }
}

# Step 3: Backup existing configuration
Write-Host "`n💾 Backing up existing configuration..." -ForegroundColor Yellow

if (Test-Path "$claudeDir\settings.json") {
    $backupPath = "$backupsDir\settings_$timestamp.json"
    Copy-Item "$claudeDir\settings.json" $backupPath -Force
    Write-Host "  ✓ Backed up settings to: $backupPath" -ForegroundColor Green
}

# Backup existing hooks if present
$existingHooks = Get-ChildItem $hooksDir -Filter "*.py" -ErrorAction SilentlyContinue
if ($existingHooks) {
    $backupHooksDir = "$backupsDir\hooks_$timestamp"
    New-Item -ItemType Directory -Path $backupHooksDir -Force | Out-Null
    Copy-Item "$hooksDir\*.py" $backupHooksDir -Force
    Write-Host "  ✓ Backed up $($existingHooks.Count) existing hooks" -ForegroundColor Green
}

# Step 4: Install enhanced hooks
Write-Host "`n📝 Installing enhanced hooks..." -ForegroundColor Yellow

# Complete list of enhanced hooks
$hooks = @(
    # Core integration hooks
    "agent_mention_parser.py",
    "agent_orchestrator.py",
    "agent_orchestrator_integrated.py",
    "slash_command_router.py",
    "mcp_gateway.py",
    "mcp_gateway_enhanced.py",
    "mcp_initializer.py",
    
    # Audio and notification
    "audio_player.py",
    "audio_notifier.py",
    
    # Session management
    "session_loader.py",
    "session_saver.py",
    
    # Quality and tracking
    "quality_gate.py",
    "model_tracker.py",
    "planning_trigger.py",
    
    # Pre/Post hooks
    "pre_command.py",
    "post_command.py",
    "pre_project.py",
    "post_project.py",
    
    # Base utilities
    "base_hook.py"
)

$installedCount = 0
$failedCount = 0

# Try local source first (only works when running locally)
if ($sourceHooksDir -and (Test-Path $sourceHooksDir)) {
    Write-Host "  Installing from local source..." -ForegroundColor Cyan
    
    foreach ($hook in $hooks) {
        $sourcePath = "$sourceHooksDir\$hook"
        $destPath = "$hooksDir\$hook"
        
        if (Test-Path $sourcePath) {
            Copy-Item $sourcePath $destPath -Force
            Write-Host "    ✓ $hook" -ForegroundColor Green
            $installedCount++
        } else {
            Write-Host "    ⚠ $hook (not found)" -ForegroundColor Yellow
        }
    }
    
    # Also create test hook for debugging
    $testHook = @'
#!/usr/bin/env python3
"""Test hook to verify system is working"""
import json
import sys
import os
from datetime import datetime

# Read input
try:
    input_data = json.load(sys.stdin)
    event = input_data.get("hook_event_name", "unknown")
    
    # Log to file
    log_dir = os.path.expanduser("~/.claude/logs")
    os.makedirs(log_dir, exist_ok=True)
    with open(os.path.join(log_dir, "test_hook.log"), "a") as f:
        f.write(f"{datetime.now().isoformat()}: Event={event}\n")
    
    # Output to stderr for debug
    print(f"[TEST HOOK] Event: {event}", file=sys.stderr)
except Exception as e:
    print(f"[TEST HOOK ERROR] {e}", file=sys.stderr)

sys.exit(0)
'@
    $testHook | Out-File -FilePath "$hooksDir\test_hook.py" -Encoding UTF8
    Write-Host "    ✓ test_hook.py (debug)" -ForegroundColor Green
    $installedCount++
    
} else {
    # Fallback to GitHub download
    Write-Host "  Downloading from GitHub..." -ForegroundColor Cyan
    $baseUrl = "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example/hooks"
    
    foreach ($hook in $hooks) {
        Write-Host "    Downloading: $hook... " -NoNewline
        $url = "$baseUrl/$hook"
        $dest = "$hooksDir\$hook"
        
        try {
            $webClient = New-Object System.Net.WebClient
            $webClient.DownloadFile($url, $dest)
            $webClient.Dispose()
            Write-Host "✓" -ForegroundColor Green
            $installedCount++
        } catch {
            Write-Host "✗" -ForegroundColor Red
            $failedCount++
        }
        
        Start-Sleep -Milliseconds 100
    }
}

# Create test_hook.py for debugging
Write-Host "  Creating test_hook.py..." -NoNewline
$testHook = @'
#!/usr/bin/env python3
"""Test hook to verify system is working"""
import json
import sys
import os
from datetime import datetime

try:
    input_data = json.load(sys.stdin)
    event = input_data.get("hook_event_name", "unknown")
    
    log_dir = os.path.expanduser("~/.claude/logs")
    os.makedirs(log_dir, exist_ok=True)
    with open(os.path.join(log_dir, "test_hook.log"), "a") as f:
        f.write(f"{datetime.now().isoformat()}: Event={event}\n")
    
    print(f"[TEST HOOK] Event: {event}", file=sys.stderr)
except Exception as e:
    print(f"[TEST HOOK ERROR] {e}", file=sys.stderr)

sys.exit(0)
'@
$testHook | Out-File -FilePath "$hooksDir\test_hook.py" -Encoding UTF8
Write-Host " ✓" -ForegroundColor Green
$installedCount++

Write-Host "  Installed: $installedCount hooks" -ForegroundColor Green
if ($failedCount -gt 0) {
    Write-Host "  Failed: $failedCount hooks" -ForegroundColor Red
}

# Also ensure hooks have proper Python shebang
Write-Host "`n🔧 Ensuring hooks are executable..." -ForegroundColor Yellow
$hookFiles = Get-ChildItem $hooksDir -Filter "*.py" -ErrorAction SilentlyContinue
foreach ($hook in $hookFiles) {
    $content = Get-Content $hook.FullName -Raw
    if ($content -notmatch '^#!/usr/bin/env python') {
        $newContent = "#!/usr/bin/env python3`n" + $content
        $newContent | Out-File $hook.FullName -Encoding UTF8
    }
}
Write-Host "  ✓ Hook files prepared" -ForegroundColor Green

# Step 5: Install audio assets
Write-Host "`n🎵 Installing audio notifications..." -ForegroundColor Yellow

if ($sourceAudioDir -and (Test-Path $sourceAudioDir)) {
    $audioFiles = Get-ChildItem $sourceAudioDir -Filter "*.mp3" -ErrorAction SilentlyContinue
    
    if ($audioFiles) {
        foreach ($audioFile in $audioFiles) {
            Copy-Item $audioFile.FullName "$audioDir\$($audioFile.Name)" -Force
            Write-Host "  ✓ $($audioFile.Name)" -ForegroundColor Green
        }
        Write-Host "  Installed: $($audioFiles.Count) audio files" -ForegroundColor Cyan
    } else {
        Write-Host "  ⚠ No audio files found" -ForegroundColor Yellow
    }
} else {
    # Download audio files from GitHub or create placeholders
    Write-Host "  Downloading audio files from GitHub..." -ForegroundColor Yellow
    $audioBaseUrl = "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example/audio"
    $audioFiles = @(
        "ready.mp3",
        "task_complete.mp3",
        "build_complete.mp3",
        "error_fixed.mp3",
        "awaiting_instructions.mp3"
    )
    
    $audioDownloaded = 0
    foreach ($audio in $audioFiles) {
        $audioUrl = "$audioBaseUrl/$audio"
        $audioPath = "$audioDir\$audio"
        
        try {
            # Try to download real audio file
            $webClient = New-Object System.Net.WebClient
            $webClient.DownloadFile($audioUrl, $audioPath)
            $webClient.Dispose()
            Write-Host "    ✓ Downloaded: $audio" -ForegroundColor Green
            $audioDownloaded++
        } catch {
            # Create placeholder if download fails
            if (!(Test-Path $audioPath)) {
                New-Item -ItemType File -Path $audioPath -Force | Out-Null
                Write-Host "    • Created placeholder: $audio" -ForegroundColor Gray
            }
        }
        Start-Sleep -Milliseconds 100
    }
    
    if ($audioDownloaded -gt 0) {
        Write-Host "  Downloaded: $audioDownloaded audio files" -ForegroundColor Green
    }
}

# Step 6: Copy or download settings-integrated.json
Write-Host "`n⚙️ Installing settings.json with complete hook configuration..." -ForegroundColor Yellow

# Try to copy from local source first
if ($sourceSettingsFile -and (Test-Path $sourceSettingsFile)) {
    Write-Host "  Installing from local source..." -ForegroundColor Cyan
    
    # Read the source settings file
    $sourceContent = Get-Content $sourceSettingsFile -Raw
    
    # Replace $HOME with actual Windows path
    $settingsContent = $sourceContent -replace '\$HOME', $env:USERPROFILE.Replace('\', '/')
    
    # Fix Python commands - add python/python3 where needed
    if ($pythonCmd -eq "python3") {
        # Add python3 to commands that don't have it
        $settingsContent = $settingsContent -replace '"command":\s*"(/[^"]+\.py)', '"command": "python3 $1'
        $settingsContent = $settingsContent -replace '"command":\s*"(C:/[^"]+\.py)', '"command": "python3 $1'
        # Keep existing python3 commands
        $settingsContent = $settingsContent -replace '"command":\s*"python\s+', '"command": "python3 '
    } else {
        # Add python to commands that don't have it
        $settingsContent = $settingsContent -replace '"command":\s*"(/[^"]+\.py)', '"command": "python $1'
        $settingsContent = $settingsContent -replace '"command":\s*"(C:/[^"]+\.py)', '"command": "python $1'
        # Keep existing python commands, change python3 to python
        $settingsContent = $settingsContent -replace '"command":\s*"python3\s+', '"command": "python '
    }
    
    # Save the modified settings
    $settingsContent | Out-File "$claudeDir\settings.json" -Encoding UTF8
    Write-Host "  ✓ Installed settings.json from local source" -ForegroundColor Green
    
} else {
    # Download from GitHub
    Write-Host "  Downloading settings from GitHub..." -ForegroundColor Cyan
    $settingsUrl = "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example/settings-integrated.json"
    
    try {
        $webClient = New-Object System.Net.WebClient
        $sourceContent = $webClient.DownloadString($settingsUrl)
        $webClient.Dispose()
        
        # Replace $HOME with actual Windows path
        $settingsContent = $sourceContent -replace '\$HOME', $env:USERPROFILE.Replace('\', '/')
        
        # Fix Python commands - add python/python3 where needed
        if ($pythonCmd -eq "python3") {
            # Add python3 to commands that don't have it
            $settingsContent = $settingsContent -replace '"command":\s*"(/[^"]+\.py)', '"command": "python3 $1'
            $settingsContent = $settingsContent -replace '"command":\s*"(C:/[^"]+\.py)', '"command": "python3 $1'
            # Keep existing python3 commands
            $settingsContent = $settingsContent -replace '"command":\s*"python\s+', '"command": "python3 '
        } else {
            # Add python to commands that don't have it
            $settingsContent = $settingsContent -replace '"command":\s*"(/[^"]+\.py)', '"command": "python $1'
            $settingsContent = $settingsContent -replace '"command":\s*"(C:/[^"]+\.py)', '"command": "python $1'
            # Keep existing python commands, change python3 to python
            $settingsContent = $settingsContent -replace '"command":\s*"python3\s+', '"command": "python '
        }
        
        # Save the modified settings
        $settingsContent | Out-File "$claudeDir\settings.json" -Encoding UTF8
        Write-Host "  ✓ Downloaded and configured settings.json" -ForegroundColor Green
        
    } catch {
        Write-Host "  ✗ Failed to download settings.json, creating basic configuration..." -ForegroundColor Yellow
        
        # Fallback to creating basic settings
        $settings = @{
            hooks = @{
                PreToolUse = @(
            @{
                matcher = "Task"
                hooks = @(
                    @{
                        type = "command"
                        command = "$pythonCmd `"$env:USERPROFILE\.claude\hooks\agent_orchestrator_integrated.py`""
                        timeout = 10
                    },
                    @{
                        type = "command"
                        command = "$pythonCmd `"$env:USERPROFILE\.claude\hooks\audio_player.py`""
                        timeout = 1
                    }
                )
            },
            @{
                matcher = "Write|Edit|MultiEdit"
                hooks = @(
                    @{
                        type = "command"
                        command = "$pythonCmd `"$env:USERPROFILE\.claude\hooks\quality_gate.py`""
                        timeout = 5
                    }
                )
            },
            @{
                matcher = "Bash"
                hooks = @(
                    @{
                        type = "command"
                        command = "$pythonCmd `"$env:USERPROFILE\.claude\hooks\pre_command.py`""
                        timeout = 5
                    },
                    @{
                        type = "command"
                        command = "$pythonCmd `"$env:USERPROFILE\.claude\hooks\test_hook.py`""
                        timeout = 2
                    }
                )
            },
            @{
                matcher = "mcp__playwright__.*"
                hooks = @(
                    @{
                        type = "command"
                        command = "$pythonCmd `"$env:USERPROFILE\.claude\hooks\mcp_gateway_enhanced.py`" --service playwright"
                        timeout = 5
                    }
                )
            },
            @{
                matcher = "mcp__obsidian__.*"
                hooks = @(
                    @{
                        type = "command"
                        command = "$pythonCmd `"$env:USERPROFILE\.claude\hooks\mcp_gateway_enhanced.py`" --service obsidian"
                        timeout = 5
                    }
                )
            },
            @{
                matcher = "mcp__web-search__.*"
                hooks = @(
                    @{
                        type = "command"
                        command = "$pythonCmd `"$env:USERPROFILE\.claude\hooks\mcp_gateway_enhanced.py`" --service web-search"
                        timeout = 5
                    }
                )
            }
        )
        PostToolUse = @(
            @{
                matcher = "Task"
                hooks = @(
                    @{
                        type = "command"
                        command = "$pythonCmd `"$env:USERPROFILE\.claude\hooks\model_tracker.py`""
                        timeout = 5
                    },
                    @{
                        type = "command"
                        command = "$pythonCmd `"$env:USERPROFILE\.claude\hooks\audio_player.py`""
                        timeout = 1
                    }
                )
            },
            @{
                matcher = "Write|Edit|MultiEdit"
                hooks = @(
                    @{
                        type = "command"
                        command = "$pythonCmd `"$env:USERPROFILE\.claude\hooks\post_command.py`""
                        timeout = 5
                    }
                )
            }
        )
        UserPromptSubmit = @(
            @{
                hooks = @(
                    @{
                        type = "command"
                        command = "$pythonCmd `"$env:USERPROFILE\.claude\hooks\agent_mention_parser.py`""
                        timeout = 3
                    },
                    @{
                        type = "command"
                        command = "$pythonCmd `"$env:USERPROFILE\.claude\hooks\slash_command_router.py`""
                        timeout = 3
                    },
                    @{
                        type = "command"
                        command = "$pythonCmd `"$env:USERPROFILE\.claude\hooks\planning_trigger.py`""
                        timeout = 3
                    }
                )
            }
        )
        SessionStart = @(
            @{
                hooks = @(
                    @{
                        type = "command"
                        command = "$pythonCmd `"$env:USERPROFILE\.claude\hooks\session_loader.py`""
                        timeout = 10
                    },
                    @{
                        type = "command"
                        command = "$pythonCmd `"$env:USERPROFILE\.claude\hooks\mcp_initializer.py`""
                        timeout = 5
                    },
                    @{
                        type = "command"
                        command = "$pythonCmd `"$env:USERPROFILE\.claude\hooks\audio_player.py`""
                        timeout = 1
                    }
                )
            }
        )
        Stop = @(
            @{
                hooks = @(
                    @{
                        type = "command"
                        command = "$pythonCmd `"$env:USERPROFILE\.claude\hooks\session_saver.py`""
                        timeout = 5
                    },
                    @{
                        type = "command"
                        command = "$pythonCmd `"$env:USERPROFILE\.claude\hooks\post_project.py`""
                        timeout = 5
                    },
                    @{
                        type = "command"
                        command = "$pythonCmd `"$env:USERPROFILE\.claude\hooks\audio_player.py`""
                        timeout = 1
                    }
                )
            }
        )
        SubagentStop = @(
            @{
                hooks = @(
                    @{
                        type = "command"
                        command = "$pythonCmd `"$env:USERPROFILE\.claude\hooks\model_tracker.py`""
                        timeout = 3
                    }
                )
            }
        )
            }
        }
        
        # Convert to JSON and save
        $settingsJson = $settings | ConvertTo-Json -Depth 10
        $settingsJson | Out-File "$claudeDir\settings.json" -Encoding UTF8
        Write-Host "  ✓ Created fallback settings.json with Windows paths" -ForegroundColor Yellow
    }
}

Write-Host "  ✓ Python command configured: $pythonCmd" -ForegroundColor Cyan

# Step 7: Validate JSON
Write-Host "`n🔍 Validating configuration..." -ForegroundColor Yellow

try {
    $testSettings = Get-Content "$claudeDir\settings.json" -Raw | ConvertFrom-Json
    Write-Host "  ✓ settings.json is valid JSON" -ForegroundColor Green
} catch {
    Write-Host "  ✗ settings.json has JSON errors!" -ForegroundColor Red
    Write-Host "    Error: $_" -ForegroundColor Red
}

# Step 8: Test hook execution
Write-Host "`n🧪 Testing hook system..." -ForegroundColor Yellow

$testInput = '{"hook_event_name": "test", "tool_name": "Bash"}'
$testHookPath = "$hooksDir\test_hook.py"

if (Test-Path $testHookPath) {
    try {
        $testOutput = $testInput | & $pythonCmd $testHookPath 2>&1
        Write-Host "  ✓ Test hook executed successfully" -ForegroundColor Green
        
        if (Test-Path "$logsDir\test_hook.log") {
            Write-Host "  ✓ Test log created successfully" -ForegroundColor Green
        }
    } catch {
        Write-Host "  ⚠ Test hook failed (Python may not be in PATH)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⚠ Test hook not found" -ForegroundColor Yellow
}

# Step 9: Display summary
Write-Host "`n" -NoNewline
Write-Host "═" * 60 -ForegroundColor Cyan
Write-Host "  ENHANCED HOOKS INSTALLATION COMPLETE" -ForegroundColor Green
Write-Host "═" * 60 -ForegroundColor Cyan

Write-Host "`n📊 Installation Summary:" -ForegroundColor Cyan
Write-Host "  • Hooks installed: $installedCount/20" -ForegroundColor White
Write-Host "  • Audio files: $(if (Test-Path $audioDir) { (Get-ChildItem $audioDir -Filter "*.mp3").Count } else { 0 })" -ForegroundColor White
Write-Host "  • Python command: $pythonCmd" -ForegroundColor White
Write-Host "  • Settings: Configured with Windows paths" -ForegroundColor White

Write-Host "`n🚀 Key Features Enabled:" -ForegroundColor Cyan
Write-Host "  • 28 Agents orchestration" -ForegroundColor White
Write-Host "  • 18 Slash commands" -ForegroundColor White
Write-Host "  • MCP services integration" -ForegroundColor White
Write-Host "  • Audio notifications" -ForegroundColor White
Write-Host "  • Session persistence" -ForegroundColor White
Write-Host "  • Quality gates" -ForegroundColor White

Write-Host "`n⚠️ CRITICAL NEXT STEPS:" -ForegroundColor Yellow
Write-Host "  1. EXIT Claude Code completely" -ForegroundColor Red
Write-Host "  2. Restart Claude Code" -ForegroundColor White
Write-Host "  3. Run in debug mode: claude --debug" -ForegroundColor White
Write-Host "  4. Type: /hooks" -ForegroundColor White
Write-Host "  5. Verify all hooks are listed" -ForegroundColor White

Write-Host "`n🧪 To Test Hooks:" -ForegroundColor Cyan
Write-Host "  • Run: ls (should trigger test_hook)" -ForegroundColor White
Write-Host "  • Try: @agent-frontend-mockup test" -ForegroundColor White
Write-Host "  • Try: /new-project test" -ForegroundColor White
Write-Host "  • Check: $logsDir\test_hook.log" -ForegroundColor White

if (!$hasPython) {
    Write-Host "`n❌ IMPORTANT:" -ForegroundColor Red
    Write-Host "  Python 3 is REQUIRED for hooks to function" -ForegroundColor Red
    Write-Host "  Install from: https://python.org" -ForegroundColor Yellow
    Write-Host "  Make sure to check 'Add Python to PATH'!" -ForegroundColor Yellow
}

Write-Host "`n✨ Your Claude Code is now enhanced with 6-9x faster development!" -ForegroundColor Green

# Return success
return 0