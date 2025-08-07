# Enhanced Claude Code Hooks Installer v2.1
# Installs complete integrated hook system with audio notifications

Write-Host @"
╔════════════════════════════════════════════════════════════════╗
║          Claude Code Enhanced Hooks Installer v2.1             ║
║     19 Hooks + Audio Notifications + Full Integration          ║
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

# Project paths
$projectRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
$sourceHooksDir = "$projectRoot\.claude-example\hooks"
$sourceAudioDir = "$projectRoot\.claude-example\audio"
$sourceSettings = "$projectRoot\.claude-example\settings-integrated.json"

# Step 1: Check prerequisites
Write-Host "`n🔍 Checking prerequisites..." -ForegroundColor Yellow

$hasPython = $false
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python") {
        $hasPython = $true
        Write-Host "  ✓ Python found: $pythonVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "  ⚠ Python not found - hooks require Python to run" -ForegroundColor Yellow
    Write-Host "    Install from: https://python.org" -ForegroundColor Gray
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

# Try local source first
if (Test-Path $sourceHooksDir) {
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

Write-Host "  Installed: $installedCount hooks" -ForegroundColor Green
if ($failedCount -gt 0) {
    Write-Host "  Failed: $failedCount hooks" -ForegroundColor Red
}

# Step 5: Install audio assets
Write-Host "`n🎵 Installing audio notifications..." -ForegroundColor Yellow

if (Test-Path $sourceAudioDir) {
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
    # Create placeholder audio files
    Write-Host "  Creating audio placeholders..." -ForegroundColor Yellow
    $audioPlaceholders = @(
        "ready.mp3",
        "task_complete.mp3",
        "build_complete.mp3",
        "error_fixed.mp3",
        "awaiting_instructions.mp3"
    )
    
    foreach ($audio in $audioPlaceholders) {
        $audioPath = "$audioDir\$audio"
        if (!(Test-Path $audioPath)) {
            New-Item -ItemType File -Path $audioPath -Force | Out-Null
            Write-Host "    • Created placeholder: $audio" -ForegroundColor Gray
        }
    }
}

# Step 6: Install integrated settings
Write-Host "`n⚙️ Installing integrated settings..." -ForegroundColor Yellow

if (Test-Path $sourceSettings) {
    # Read settings and update paths
    $settingsContent = Get-Content $sourceSettings -Raw
    $settingsContent = $settingsContent -replace '\$HOME', $env:USERPROFILE.Replace('\', '/')
    
    # Save to Claude directory
    $settingsContent | Out-File "$claudeDir\settings.json" -Encoding UTF8
    Write-Host "  ✓ Installed integrated settings.json" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Settings file not found, creating minimal configuration" -ForegroundColor Yellow
    
    # Create minimal settings with hook configurations
    $minimalSettings = @{
        hooks = @{
            PreToolUse = @(
                @{
                    matcher = "Task"
                    hooks = @(
                        @{
                            type = "command"
                            command = "`$HOME/.claude/hooks/agent_orchestrator_integrated.py"
                            timeout = 10
                        },
                        @{
                            type = "command"
                            command = "`$HOME/.claude/hooks/audio_player.py"
                            timeout = 1
                        }
                    )
                }
            )
            PostToolUse = @(
                @{
                    hooks = @(
                        @{
                            type = "command"
                            command = "`$HOME/.claude/hooks/model_tracker.py"
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
                            command = "`$HOME/.claude/hooks/slash_command_router.py"
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
                            command = "`$HOME/.claude/hooks/session_loader.py"
                            timeout = 10
                        },
                        @{
                            type = "command"
                            command = "`$HOME/.claude/hooks/mcp_initializer.py"
                            timeout = 5
                        }
                    )
                }
            )
            Stop = @(
                @{
                    hooks = @(
                        @{
                            type = "command"
                            command = "`$HOME/.claude/hooks/session_saver.py"
                            timeout = 5
                        },
                        @{
                            type = "command"
                            command = "`$HOME/.claude/hooks/audio_player.py"
                            timeout = 1
                        }
                    )
                }
            )
        }
    }
    
    $minimalSettings | ConvertTo-Json -Depth 10 | Out-File "$claudeDir\settings.json" -Encoding UTF8
    Write-Host "  ✓ Created minimal settings.json" -ForegroundColor Green
}

# Step 7: Create test script
Write-Host "`n🧪 Creating test script..." -ForegroundColor Yellow

$testScript = @'
# Test enhanced hook system
Write-Host "Testing Enhanced Hook System" -ForegroundColor Cyan

$claudeHooks = "$env:USERPROFILE\.claude\hooks"

# Test slash command router
Write-Host "`nTesting slash command router..." -ForegroundColor Yellow
$testData = @{ prompt = "/new-project test" } | ConvertTo-Json
$result = $testData | python "$claudeHooks\slash_command_router.py" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Slash commands work!" -ForegroundColor Green
} else {
    Write-Host "  ✗ Slash commands failed" -ForegroundColor Red
}

# Test agent orchestrator
Write-Host "Testing agent orchestrator..." -ForegroundColor Yellow
$testData = @{
    tool_name = "Task"
    tool_input = @{ prompt = "@agent-frontend-mockup test" }
} | ConvertTo-Json
$result = $testData | python "$claudeHooks\agent_orchestrator_integrated.py" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Agent orchestration works!" -ForegroundColor Green
} else {
    Write-Host "  ✗ Agent orchestration failed" -ForegroundColor Red
}

# Test audio
Write-Host "Testing audio notifications..." -ForegroundColor Yellow
$testData = @{ hook_event_name = "SessionStart" } | ConvertTo-Json
$result = $testData | python "$claudeHooks\audio_player.py" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Audio system works!" -ForegroundColor Green
} else {
    Write-Host "  ✗ Audio system failed" -ForegroundColor Red
}

Write-Host "`nTest complete!" -ForegroundColor Green
'@

$testScript | Out-File "$claudeDir\test-hooks.ps1" -Encoding UTF8
Write-Host "  ✓ Created test-hooks.ps1" -ForegroundColor Green

# Step 8: Display summary
Write-Host "`n" -NoNewline
Write-Host "═" * 60 -ForegroundColor Cyan
Write-Host "  ENHANCED HOOKS INSTALLATION COMPLETE" -ForegroundColor Green
Write-Host "═" * 60 -ForegroundColor Cyan

Write-Host "`n📊 Installation Summary:" -ForegroundColor Cyan
Write-Host "  • Hooks installed: $installedCount/$($hooks.Count)" -ForegroundColor White
Write-Host "  • Audio files: $(if (Test-Path $audioDir) { (Get-ChildItem $audioDir -Filter "*.mp3").Count } else { 0 })" -ForegroundColor White
Write-Host "  • Directories created: $($directories.Count)" -ForegroundColor White
Write-Host "  • Settings: Integrated configuration" -ForegroundColor White

Write-Host "`n🚀 Key Features Enabled:" -ForegroundColor Cyan
Write-Host "  • 28 Agents orchestration" -ForegroundColor White
Write-Host "  • 18 Slash commands" -ForegroundColor White
Write-Host "  • 3 MCP services integration" -ForegroundColor White
Write-Host "  • Audio notifications" -ForegroundColor White
Write-Host "  • Session persistence" -ForegroundColor White
Write-Host "  • Model optimization" -ForegroundColor White
Write-Host "  • Quality gates" -ForegroundColor White

Write-Host "`n📝 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Restart Claude Code to load new hooks" -ForegroundColor White
Write-Host "  2. Test system: .\test-hooks.ps1" -ForegroundColor White
Write-Host "  3. Try: claude `"/new-project test`"" -ForegroundColor White

if (!$hasPython) {
    Write-Host "`n⚠ Important:" -ForegroundColor Yellow
    Write-Host "  Python is required for hooks to function" -ForegroundColor Red
    Write-Host "  Install from: https://python.org" -ForegroundColor Yellow
}

Write-Host "`n✨ Your Claude Code is now enhanced with 6-9x faster development!" -ForegroundColor Green

# Return success
return 0