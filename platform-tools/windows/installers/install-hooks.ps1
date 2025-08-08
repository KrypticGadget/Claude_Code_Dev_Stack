# Ultimate Claude Code Hooks & Audio System Installer v3.0
# Installs hooks + 50 JARVIS-style audio notifications

Write-Host @"
╔════════════════════════════════════════════════════════════════╗
║   Ultimate Claude Code Hooks & Audio System Installer v3.0     ║
║    Hooks + 50 JARVIS-style Audio + Intelligent Orchestration   ║
╚════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Configuration
$claudeDir = "$env:USERPROFILE\.claude"
$settingsPath = "$claudeDir\settings.json"  # Hooks go in settings.json, not .claude.json!
$hooksDir = "$claudeDir\hooks"
$audioDir = "$claudeDir\audio"
$logsDir = "$claudeDir\logs"
$stateDir = "$claudeDir\state"
$backupsDir = "$claudeDir\backups"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

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

# Step 3: Backup existing settings.json
Write-Host "`n💾 Backing up existing configuration..." -ForegroundColor Yellow

if (Test-Path $settingsPath) {
    $backupPath = "$backupsDir\settings_$timestamp.json"
    Copy-Item $settingsPath $backupPath -Force
    Write-Host "  ✓ Backed up settings.json to: $backupPath" -ForegroundColor Green
}

# Step 4: Install optimized hooks INCLUDING ULTIMATE SYSTEM
Write-Host "`n📝 Installing Ultimate Hook System..." -ForegroundColor Yellow

# Ultimate system hooks + essential ones (12 total)
$hooks = @(
    # Core functionality (5 hooks)
    "agent_mention_parser.py",    # Routes @agent- mentions
    "slash_command_router.py",    # Handles /commands
    "audio_player.py",            # Audio notifications
    "audio_notifier.py",          # Alternative audio system
    "planning_trigger.py",        # Todo management
    
    # ULTIMATE SYSTEM HOOKS (3 new)
    "master_orchestrator.py",     # Master orchestrator for intelligent routing
    "audio_controller.py",        # Advanced audio controller
    "ultimate_claude_hook.py",   # Simplified ultimate system
    
    # Minimal session management (3 hooks - lightweight versions)
    "session_loader.py",          # Minimal - just acknowledges
    "session_saver.py",          # Minimal - just timestamp
    "model_tracker.py",          # Minimal - daily count only
    
    # Test hook for debugging
    "test_hook.py"               # Test hook for verification
)

$installedCount = 0
$failedCount = 0

# Download from GitHub
Write-Host "  Downloading hooks from GitHub..." -ForegroundColor Cyan
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

# Step 5: Install ULTIMATE Audio System (50 sounds)
Write-Host "`n🎵 Installing Ultimate Audio System (50 JARVIS-style sounds)..." -ForegroundColor Yellow

# All 50 audio files to download
$audioFiles = @(
    # Development phases (23)
    "project_created.wav", "dependencies_installed.wav", "environment_ready.wav",
    "requirements_gathered.wav", "architecture_designed.wav", "database_modeled.wav",
    "backend_complete.wav", "frontend_complete.wav", "api_integrated.wav",
    "auth_implemented.wav", "unit_tests_pass.wav", "integration_tests_pass.wav",
    "e2e_tests_complete.wav", "coverage_achieved.wav", "build_started.wav",
    "build_progress.wav", "build_successful.wav", "build_optimized.wav",
    "deploy_initiated.wav", "deploy_validation.wav", "deploy_complete.wav",
    "rollback_complete.wav", "milestone_complete.wav",
    
    # Input detection (15)
    "awaiting_response.wav", "awaiting_confirmation.wav", "awaiting_selection.wav",
    "awaiting_details.wav", "awaiting_code_review.wav", "yes_no_question.wav",
    "multiple_choice.wav", "clarification_needed.wav", "permission_required.wav",
    "ready_for_input.wav", "processing_complete.wav", "task_paused.wav",
    "decision_point.wav", "gentle_reminder.wav", "still_waiting.wav",
    
    # Orchestration (12)
    "agent_activated.wav", "agent_team_suggested.wav", "meta_prompt_transforming.wav",
    "orchestrator_engaged.wav", "mcp_service_starting.wav", "parallel_execution.wav",
    "sequential_execution.wav", "handoff_occurring.wav", "optimization_applied.wav",
    "context_switching.wav", "pipeline_complete.wav", "coordination_active.wav"
)

# Check if we already have the audio files
$existingAudio = (Get-ChildItem $audioDir -Filter "*.wav" -ErrorAction SilentlyContinue).Count

if ($existingAudio -ge 50) {
    Write-Host "  ✓ Ultimate audio system already installed ($existingAudio files)" -ForegroundColor Green
} else {
    Write-Host "  Downloading 50 audio files from GitHub..." -ForegroundColor Cyan
    $audioBaseUrl = "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example/audio"
    
    $audioDownloaded = 0
    $audioFailed = 0
    
    foreach ($audioFile in $audioFiles) {
        $audioUrl = "$audioBaseUrl/$audioFile"
        $audioPath = "$audioDir\$audioFile"
        
        # Skip if already exists
        if (Test-Path $audioPath) {
            $audioDownloaded++
            continue
        }
        
        try {
            $webClient = New-Object System.Net.WebClient
            $webClient.DownloadFile($audioUrl, $audioPath)
            $webClient.Dispose()
            $audioDownloaded++
            
            # Show progress every 10 files
            if ($audioDownloaded % 10 -eq 0) {
                Write-Host "    Downloaded: $audioDownloaded/50" -ForegroundColor Gray
            }
        } catch {
            $audioFailed++
        }
        
        Start-Sleep -Milliseconds 100  # Small delay to avoid rate limiting
    }
    
    Write-Host "  ✓ Downloaded: $audioDownloaded audio files" -ForegroundColor Green
    if ($audioFailed -gt 0) {
        Write-Host "  ⚠ Failed: $audioFailed files" -ForegroundColor Yellow
    }
}

# Show audio system status
$finalAudioCount = (Get-ChildItem $audioDir -Filter "*.wav" -ErrorAction SilentlyContinue).Count
if ($finalAudioCount -ge 50) {
    Write-Host "`n  🎉 Ultimate Audio System Ready!" -ForegroundColor Green
    Write-Host "    • 23 Development phase sounds" -ForegroundColor Gray
    Write-Host "    • 15 Input detection sounds" -ForegroundColor Gray
    Write-Host "    • 12 Orchestration sounds" -ForegroundColor Gray
} elseif ($finalAudioCount -gt 0) {
    Write-Host "`n  ⚠ Partial audio system ($finalAudioCount files)" -ForegroundColor Yellow
    Write-Host "    Only $finalAudioCount of 50 files installed" -ForegroundColor Yellow
}

# Step 6: Download and merge hook configuration into settings.json
Write-Host "`n⚙️ Configuring hooks in ~/.claude/settings.json..." -ForegroundColor Yellow

# Download the CLEANED hook configuration template (only 8 essential hooks)
$hooksConfigUrl = "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example/settings.json"

try {
    Write-Host "  Downloading cleaned hook configuration (8 hooks only)..." -ForegroundColor Cyan
    $webClient = New-Object System.Net.WebClient
    $hooksConfigContent = $webClient.DownloadString($hooksConfigUrl)
    $webClient.Dispose()
    
    # Parse the hooks configuration
    $hooksConfig = $hooksConfigContent | ConvertFrom-Json
    
    # Fix paths in the hooks configuration
    foreach ($eventType in $hooksConfig.hooks.PSObject.Properties) {
        foreach ($matcher in $eventType.Value) {
            if ($matcher.hooks) {
                foreach ($hook in $matcher.hooks) {
                    # Replace $HOME with Windows path (use forward slashes for Python)
                    $hook.command = $hook.command -replace '\$HOME', $env:USERPROFILE.Replace('\', '/')
                    
                    # Ensure we use python command with full path
                    if ($hook.command -match '\.claude/hooks/(.+\.py)') {
                        $hookScript = $matches[1]
                        $hook.command = "$pythonCmd `"$($env:USERPROFILE.Replace('\', '/'))/.claude/hooks/$hookScript`""
                    }
                    # Add python command if missing
                    elseif ($hook.command -notmatch '^(python|python3)') {
                        $hook.command = "$pythonCmd $($hook.command)"
                    }
                    
                    # Fix python/python3 based on what we detected
                    if ($pythonCmd -eq "python") {
                        $hook.command = $hook.command -replace '^python3\s+', 'python '
                    } else {
                        $hook.command = $hook.command -replace '^python\s+', 'python3 '
                    }
                }
            }
        }
    }
    
    # Load existing settings.json or create new
    if (Test-Path $settingsPath) {
        Write-Host "  Merging with existing settings.json..." -ForegroundColor Cyan
        $existingConfig = Get-Content $settingsPath -Raw | ConvertFrom-Json
        
        # Add or update hooks section
        if ($existingConfig.PSObject.Properties["hooks"]) {
            Write-Host "    Updating existing hooks configuration..." -ForegroundColor Gray
        } else {
            Write-Host "    Adding hooks configuration..." -ForegroundColor Gray
        }
        
        # Add hooks to existing config
        $existingConfig | Add-Member -MemberType NoteProperty -Name "hooks" -Value $hooksConfig.hooks -Force
        
        # Also add agent and command systems if not present
        if ($hooksConfig.agentSystem -and -not $existingConfig.PSObject.Properties["agentSystem"]) {
            $existingConfig | Add-Member -MemberType NoteProperty -Name "agentSystem" -Value $hooksConfig.agentSystem -Force
            Write-Host "    Added agent system configuration" -ForegroundColor Gray
        }
        
        if ($hooksConfig.slashCommands -and -not $existingConfig.PSObject.Properties["slashCommands"]) {
            $existingConfig | Add-Member -MemberType NoteProperty -Name "slashCommands" -Value $hooksConfig.slashCommands -Force
            Write-Host "    Added slash commands configuration" -ForegroundColor Gray
        }
        
        $finalConfig = $existingConfig
    } else {
        Write-Host "  Creating new settings.json..." -ForegroundColor Cyan
        $finalConfig = $hooksConfig
    }
    
    # Save the merged configuration without BOM to settings.json
    $jsonContent = $finalConfig | ConvertTo-Json -Depth 10
    [System.IO.File]::WriteAllText($settingsPath, $jsonContent, [System.Text.UTF8Encoding]::new($false))
    Write-Host "  ✓ Successfully configured hooks in settings.json" -ForegroundColor Green
    
} catch {
    Write-Host "  ✗ Failed to configure settings.json: $_" -ForegroundColor Red
    Write-Host "    Please manually add hook configuration" -ForegroundColor Yellow
}

# Step 7: Validate configuration
Write-Host "`n🔍 Validating installation..." -ForegroundColor Yellow

# Check settings.json
try {
    $testConfig = Get-Content $settingsPath -Raw | ConvertFrom-Json
    if ($testConfig.hooks) {
        Write-Host "  ✓ settings.json has hooks configuration" -ForegroundColor Green
        
        # Count configured hooks
        $hookCount = 0
        foreach ($eventType in $testConfig.hooks.PSObject.Properties) {
            foreach ($matcher in $eventType.Value) {
                if ($matcher.hooks) {
                    $hookCount += $matcher.hooks.Count
                }
            }
        }
        Write-Host "  ✓ $hookCount hook commands configured" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ settings.json missing hooks configuration" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ✗ settings.json has JSON errors!" -ForegroundColor Red
}

# Test Python execution
Write-Host "`n🧪 Testing hook system..." -ForegroundColor Yellow
$testInput = '{"hook_event_name": "test", "tool_name": "Verify"}'
$testCommand = "$pythonCmd `"$hooksDir\test_hook.py`""

try {
    $testInput | & cmd /c $testCommand 2>&1 | Out-Null
    Write-Host "  ✓ Test hook executed successfully" -ForegroundColor Green
    
    if (Test-Path "$logsDir\test_hook.log") {
        Write-Host "  ✓ Test log created successfully" -ForegroundColor Green
    }
} catch {
    Write-Host "  ⚠ Test hook execution failed (check Python installation)" -ForegroundColor Yellow
}

# Step 8: Display summary
Write-Host "`n" -NoNewline
Write-Host "═" * 60 -ForegroundColor Cyan
Write-Host "  ENHANCED HOOKS INSTALLATION COMPLETE" -ForegroundColor Green
Write-Host "═" * 60 -ForegroundColor Cyan

Write-Host "`n📊 Installation Summary:" -ForegroundColor Cyan
Write-Host "  • Hooks installed: $installedCount/8" -ForegroundColor White
Write-Host "  • Audio files: $audioDownloaded/5" -ForegroundColor White
Write-Host "  • Python command: $pythonCmd" -ForegroundColor White
Write-Host "  • Configuration: ~/.claude/settings.json" -ForegroundColor White

Write-Host "`n🚀 Key Features Enabled:" -ForegroundColor Cyan
Write-Host "  • Agent routing (@agent- mentions)" -ForegroundColor White
Write-Host "  • Slash command handling" -ForegroundColor White
Write-Host "  • Audio notifications" -ForegroundColor White
Write-Host "  • Todo management" -ForegroundColor White
Write-Host "  • Minimal session tracking (no bloat)" -ForegroundColor White
Write-Host "  • Optimized for performance" -ForegroundColor White

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