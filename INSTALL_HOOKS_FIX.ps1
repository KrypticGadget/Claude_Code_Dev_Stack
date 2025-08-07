# PowerShell Script to Fix Hook Installation
# Run this from PowerShell to properly install all hooks

Write-Host @"

╔════════════════════════════════════════════════════════════════╗
║           Claude Code Hook System Fix v2.1                     ║
║           Installing and Configuring All 19 Hooks              ║
╚════════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# Step 1: Create directories
Write-Host "`n📁 Creating directories..." -ForegroundColor Yellow
$directories = @(
    "$env:USERPROFILE\.claude",
    "$env:USERPROFILE\.claude\hooks",
    "$env:USERPROFILE\.claude\audio",
    "$env:USERPROFILE\.claude\logs",
    "$env:USERPROFILE\.claude\state",
    "$env:USERPROFILE\.claude\backups"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✓ Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "  • Exists: $dir" -ForegroundColor Gray
    }
}

# Step 2: Backup existing settings
Write-Host "`n💾 Backing up existing settings..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
if (Test-Path "$env:USERPROFILE\.claude\settings.json") {
    Copy-Item "$env:USERPROFILE\.claude\settings.json" "$env:USERPROFILE\.claude\backups\settings_backup_$timestamp.json"
    Write-Host "  ✓ Backed up to: settings_backup_$timestamp.json" -ForegroundColor Green
}

# Step 3: Copy all hooks from .claude-example to .claude
Write-Host "`n📝 Installing hooks..." -ForegroundColor Yellow
$sourceHooks = Get-Location | Join-Path -ChildPath ".claude-example\hooks"
$destHooks = "$env:USERPROFILE\.claude\hooks"

$hookFiles = @(
    "agent_mention_parser.py",
    "agent_orchestrator.py",
    "agent_orchestrator_integrated.py",
    "slash_command_router.py",
    "mcp_gateway.py",
    "mcp_gateway_enhanced.py",
    "mcp_initializer.py",
    "audio_player.py",
    "audio_notifier.py",
    "session_loader.py",
    "session_saver.py",
    "quality_gate.py",
    "model_tracker.py",
    "planning_trigger.py",
    "pre_command.py",
    "post_command.py",
    "pre_project.py",
    "post_project.py",
    "base_hook.py",
    "test_hook.py"
)

$copiedCount = 0
foreach ($hook in $hookFiles) {
    $source = Join-Path $sourceHooks $hook
    $dest = Join-Path $destHooks $hook
    
    if (Test-Path $source) {
        Copy-Item $source $dest -Force
        Write-Host "  ✓ Installed: $hook" -ForegroundColor Green
        $copiedCount++
    } else {
        Write-Host "  ✗ Not found: $hook" -ForegroundColor Red
    }
}

Write-Host "  Installed $copiedCount hooks" -ForegroundColor Cyan

# Step 4: Copy audio files
Write-Host "`n🎵 Installing audio files..." -ForegroundColor Yellow
$sourceAudio = Get-Location | Join-Path -ChildPath ".claude-example\audio"
$destAudio = "$env:USERPROFILE\.claude\audio"

if (Test-Path $sourceAudio) {
    $audioFiles = Get-ChildItem $sourceAudio -Filter "*.mp3"
    foreach ($audio in $audioFiles) {
        Copy-Item $audio.FullName "$destAudio\$($audio.Name)" -Force
        Write-Host "  ✓ Installed: $($audio.Name)" -ForegroundColor Green
    }
} else {
    Write-Host "  ⚠ Audio directory not found, creating placeholders..." -ForegroundColor Yellow
    $placeholders = @("ready.mp3", "task_complete.mp3", "build_complete.mp3", "error_fixed.mp3", "awaiting_instructions.mp3")
    foreach ($placeholder in $placeholders) {
        New-Item -ItemType File -Path "$destAudio\$placeholder" -Force | Out-Null
        Write-Host "  • Created placeholder: $placeholder" -ForegroundColor Gray
    }
}

# Step 5: Install corrected settings.json
Write-Host "`n⚙️ Installing corrected settings.json..." -ForegroundColor Yellow

# Check which Python command to use
$pythonCmd = "python"
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3") {
        $pythonCmd = "python"
        Write-Host "  ✓ Found Python 3: $pythonVersion" -ForegroundColor Green
    }
} catch {
    try {
        $pythonVersion = python3 --version 2>&1
        if ($pythonVersion -match "Python 3") {
            $pythonCmd = "python3"
            Write-Host "  ✓ Found Python 3: $pythonVersion" -ForegroundColor Green
        }
    } catch {
        Write-Host "  ⚠ Python not found - hooks will not work!" -ForegroundColor Red
    }
}

# Create the corrected settings.json with proper Windows paths
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
                        command = "$pythonCmd `"$env:USERPROFILE\.claude\hooks\audio_player.py`""
                        timeout = 1
                    }
                )
            }
        )
    }
}

# Save the settings.json
$settingsPath = "$env:USERPROFILE\.claude\settings.json"
$settings | ConvertTo-Json -Depth 10 | Out-File $settingsPath -Encoding UTF8
Write-Host "  ✓ Installed corrected settings.json" -ForegroundColor Green

# Step 6: Validate installation
Write-Host "`n🔍 Validating installation..." -ForegroundColor Yellow

# Check if settings.json is valid JSON
try {
    $testSettings = Get-Content $settingsPath -Raw | ConvertFrom-Json
    Write-Host "  ✓ settings.json is valid JSON" -ForegroundColor Green
} catch {
    Write-Host "  ✗ settings.json has JSON errors!" -ForegroundColor Red
}

# Count installed hooks
$installedHooks = (Get-ChildItem "$env:USERPROFILE\.claude\hooks" -Filter "*.py").Count
Write-Host "  ✓ $installedHooks Python hooks installed" -ForegroundColor Green

# Test a hook
Write-Host "`n🧪 Testing hook execution..." -ForegroundColor Yellow
$testInput = '{"hook_event_name": "test", "tool_name": "Bash"}' 
$testCommand = "$pythonCmd `"$env:USERPROFILE\.claude\hooks\test_hook.py`""

try {
    $testInput | & cmd /c $testCommand 2>&1
    Write-Host "  ✓ Test hook executed successfully" -ForegroundColor Green
    
    # Check if log was created
    if (Test-Path "$env:USERPROFILE\.claude\logs\test_hook.log") {
        Write-Host "  ✓ Test hook log created" -ForegroundColor Green
    }
} catch {
    Write-Host "  ⚠ Test hook execution failed (this is okay if Python is not in PATH)" -ForegroundColor Yellow
}

# Final instructions
Write-Host "`n" -NoNewline
Write-Host "═" * 60 -ForegroundColor Cyan
Write-Host "  INSTALLATION COMPLETE" -ForegroundColor Green
Write-Host "═" * 60 -ForegroundColor Cyan

Write-Host "`n📋 Summary:" -ForegroundColor Cyan
Write-Host "  • Hooks installed: $installedHooks" -ForegroundColor White
Write-Host "  • Settings.json: Configured with Windows paths" -ForegroundColor White
Write-Host "  • Python command: $pythonCmd" -ForegroundColor White
Write-Host "  • Test hook: Installed for debugging" -ForegroundColor White

Write-Host "`n⚠️ CRITICAL NEXT STEPS:" -ForegroundColor Yellow
Write-Host "  1. EXIT Claude Code completely (close all windows)" -ForegroundColor White
Write-Host "  2. Restart Claude Code" -ForegroundColor White
Write-Host "  3. Run in debug mode to verify: claude --debug" -ForegroundColor White
Write-Host "  4. Type: /hooks" -ForegroundColor White
Write-Host "  5. You should see all hooks listed" -ForegroundColor White

Write-Host "`n🧪 To verify hooks are working:" -ForegroundColor Cyan
Write-Host "  1. Run: ls" -ForegroundColor White
Write-Host "  2. Check: $env:USERPROFILE\.claude\logs\test_hook.log" -ForegroundColor White
Write-Host "  3. Try: @agent-frontend-mockup test" -ForegroundColor White
Write-Host "  4. Try: /new-project test" -ForegroundColor White

Write-Host "`n💡 If hooks don't appear:" -ForegroundColor Yellow
Write-Host "  • Make sure Python is in your PATH" -ForegroundColor White
Write-Host "  • Try using python instead of python3" -ForegroundColor White
Write-Host "  • Check Windows Defender hasn't blocked scripts" -ForegroundColor White
Write-Host "  • Run Claude Code as Administrator once" -ForegroundColor White

Write-Host "`n✨ Your hook system should now be working!" -ForegroundColor Green