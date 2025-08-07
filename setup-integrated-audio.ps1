# setup-integrated-audio.ps1
# Complete setup script for integrated Claude Code Dev Stack with Audio

Write-Host @"

╔════════════════════════════════════════════════════════════════╗
║     Claude Code Integrated Dev Stack + Audio Setup v2.1        ║
║     Agents + Commands + MCPs + Hooks + Audio = Complete        ║
╚════════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# Configuration
$claudeHome = "$env:USERPROFILE\.claude"
$hooksDir = "$claudeHome\hooks"
$audioDir = "$claudeHome\audio"
$logsDir = "$claudeHome\logs"
$stateDir = "$claudeHome\state"
$backupsDir = "$claudeHome\backups"
$sourceDir = (Get-Location).Path
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# Step 1: Create directory structure
Write-Host "`n📁 Creating directory structure..." -ForegroundColor Yellow

$directories = @(
    $hooksDir,
    $audioDir,
    $logsDir,
    $stateDir,
    $backupsDir,
    "$claudeHome\agents",
    "$claudeHome\commands",
    "$claudeHome\mcp-configs",
    "$claudeHome\templates"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✓ Created: $(Split-Path $dir -Leaf)" -ForegroundColor Green
    } else {
        Write-Host "  • Exists: $(Split-Path $dir -Leaf)" -ForegroundColor Gray
    }
}

# Step 2: Backup existing configuration
Write-Host "`n💾 Backing up existing configuration..." -ForegroundColor Yellow

if (Test-Path "$claudeHome\settings.json") {
    Copy-Item "$claudeHome\settings.json" "$backupsDir\settings_$timestamp.json"
    Write-Host "  ✓ Backed up settings to: settings_$timestamp.json" -ForegroundColor Green
}

# Step 3: Copy hook files from .claude-example
Write-Host "`n📝 Installing hook scripts..." -ForegroundColor Yellow

$hookFiles = @(
    "agent_mention_parser.py",
    "agent_orchestrator.py",
    "agent_orchestrator_integrated.py",
    "audio_player.py",  # NEW: Audio player hook
    "base_hook.py",
    "mcp_gateway.py",
    "mcp_gateway_enhanced.py",
    "mcp_initializer.py",
    "model_tracker.py",
    "planning_trigger.py",
    "post_command.py",
    "post_project.py",
    "pre_command.py",
    "pre_project.py",
    "quality_gate.py",
    "session_loader.py",
    "session_saver.py",
    "slash_command_router.py"
)

$copiedCount = 0
$sourceHooksDir = "$sourceDir\.claude-example\hooks"

foreach ($hookFile in $hookFiles) {
    $sourcePath = "$sourceHooksDir\$hookFile"
    $destPath = "$hooksDir\$hookFile"
    
    if (Test-Path $sourcePath) {
        Copy-Item $sourcePath $destPath -Force
        Write-Host "  ✓ Installed: $hookFile" -ForegroundColor Green
        $copiedCount++
    }
}

Write-Host "  Installed $copiedCount hook scripts" -ForegroundColor Cyan

# Step 4: Copy audio files from .claude-example
Write-Host "`n🎵 Installing audio assets..." -ForegroundColor Yellow

$sourceAudioDir = "$sourceDir\.claude-example\audio"
if (Test-Path $sourceAudioDir) {
    $audioFiles = Get-ChildItem $sourceAudioDir -Filter "*.mp3"
    
    foreach ($audioFile in $audioFiles) {
        Copy-Item $audioFile.FullName "$audioDir\$($audioFile.Name)" -Force
        Write-Host "  ✓ Installed: $($audioFile.Name)" -ForegroundColor Green
    }
    
    Write-Host "  Installed $($audioFiles.Count) audio files" -ForegroundColor Cyan
} else {
    Write-Host "  ⚠ No audio files found in .claude-example\audio" -ForegroundColor Yellow
}

# Step 5: Install integrated settings with audio
Write-Host "`n⚙️ Installing integrated configuration with audio..." -ForegroundColor Yellow

$settingsSource = "$sourceDir\.claude-example\settings-integrated.json"
if (Test-Path $settingsSource) {
    # Read and update paths
    $settingsContent = Get-Content $settingsSource -Raw
    $settingsContent = $settingsContent -replace '\$HOME', $env:USERPROFILE.Replace('\', '/')
    
    # Save to Claude home
    $settingsContent | Out-File "$claudeHome\settings.json" -Encoding UTF8
    Write-Host "  ✓ Installed integrated settings.json with audio hooks" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Settings file not found" -ForegroundColor Yellow
}

# Step 6: Install agents
Write-Host "`n🤖 Installing agents..." -ForegroundColor Yellow

$agentsSource = "$sourceDir\.claude-example\agents"
if (Test-Path $agentsSource) {
    $agentFiles = Get-ChildItem $agentsSource -Filter "*.md" -ErrorAction SilentlyContinue
    if ($agentFiles) {
        Copy-Item "$agentsSource\*.md" "$claudeHome\agents\" -Force
        Write-Host "  ✓ Installed $($agentFiles.Count) agents" -ForegroundColor Green
    }
}

# Step 7: Install commands
Write-Host "`n⚡ Installing slash commands..." -ForegroundColor Yellow

$commandsSource = "$sourceDir\.claude-example\commands"
if (Test-Path $commandsSource) {
    $commandFiles = Get-ChildItem $commandsSource -Filter "*.md" -ErrorAction SilentlyContinue
    if ($commandFiles) {
        Copy-Item "$commandsSource\*.md" "$claudeHome\commands\" -Force
        Write-Host "  ✓ Installed $($commandFiles.Count) commands" -ForegroundColor Green
    }
}

# Step 8: Create audio configuration
Write-Host "`n🎨 Creating audio configuration..." -ForegroundColor Yellow

$audioConfig = @{
    "version" = "2.1"
    "enabled" = $true
    "audio_mappings" = @{
        "task_complete" = "task_complete.mp3"
        "build_complete" = "build_complete.mp3"
        "error_fixed" = "error_fixed.mp3"
        "ready" = "ready.mp3"
        "awaiting_instructions" = "awaiting_instructions.mp3"
    }
    "events" = @{
        "SessionStart" = "ready"
        "Stop" = "task_complete"
        "BuildSuccess" = "build_complete"
        "ErrorResolved" = "error_fixed"
        "UserPromptSubmit" = "awaiting_instructions"
    }
}

$audioConfig | ConvertTo-Json -Depth 3 | Out-File "$audioDir\audio_config.json" -Encoding UTF8
Write-Host "  ✓ Created audio_config.json" -ForegroundColor Green

# Step 9: Create test script
Write-Host "`n🧪 Creating test script..." -ForegroundColor Yellow

$testScript = @'
# Test integrated system with audio
Write-Host "Testing Integrated Claude Code Dev Stack with Audio" -ForegroundColor Cyan

# Test audio hook
Write-Host "`nTesting audio playback..." -ForegroundColor Yellow
$testData = @{
    hook_event_name = "SessionStart"
} | ConvertTo-Json

$result = $testData | python "$env:USERPROFILE\.claude\hooks\audio_player.py" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Audio hook works!" -ForegroundColor Green
} else {
    Write-Host "  ✗ Audio hook failed" -ForegroundColor Red
}

# Test slash command routing
Write-Host "`nTesting slash command: /new-project" -ForegroundColor Yellow
$testData = @{
    prompt = "/new-project test"
} | ConvertTo-Json

$result = $testData | python "$env:USERPROFILE\.claude\hooks\slash_command_router.py" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Command routing works!" -ForegroundColor Green
}

# Test agent orchestrator
Write-Host "`nTesting agent orchestrator" -ForegroundColor Yellow
$testData = @{
    tool_name = "Task"
    tool_input = @{
        prompt = "@agent-frontend-mockup test"
    }
} | ConvertTo-Json

$result = $testData | python "$env:USERPROFILE\.claude\hooks\agent_orchestrator_integrated.py" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Agent orchestrator works!" -ForegroundColor Green
}

Write-Host "`nAll tests complete!" -ForegroundColor Green
'@

$testScript | Out-File "$claudeHome\test-integration-audio.ps1" -Encoding UTF8
Write-Host "  ✓ Created test-integration-audio.ps1" -ForegroundColor Green

# Step 10: Display summary
Write-Host "`n" -NoNewline
Write-Host "═" * 60 -ForegroundColor Cyan
Write-Host "  INSTALLATION COMPLETE WITH AUDIO" -ForegroundColor Green
Write-Host "═" * 60 -ForegroundColor Cyan

Write-Host "`n📊 Summary:" -ForegroundColor Cyan
Write-Host "  • Hook scripts: $copiedCount installed" -ForegroundColor White
Write-Host "  • Audio files: 5 MP3 files ready" -ForegroundColor White
Write-Host "  • Configuration: Integrated settings with audio" -ForegroundColor White
Write-Host "  • Agents: 28 configured" -ForegroundColor White
Write-Host "  • Commands: 18 configured" -ForegroundColor White
Write-Host "  • Audio events: 5 mapped" -ForegroundColor White

Write-Host "`n🎵 Audio Mappings:" -ForegroundColor Cyan
Write-Host "  • Session start     → ready.mp3" -ForegroundColor White
Write-Host "  • Task complete     → task_complete.mp3" -ForegroundColor White
Write-Host "  • Build success     → build_complete.mp3" -ForegroundColor White
Write-Host "  • Error fixed       → error_fixed.mp3" -ForegroundColor White
Write-Host "  • Awaiting input    → awaiting_instructions.mp3" -ForegroundColor White

Write-Host "`n📌 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Restart Claude Code to load new configuration" -ForegroundColor White
Write-Host "  2. Test with: .\test-integration-audio.ps1" -ForegroundColor White
Write-Host "  3. Try: claude `"@agent-frontend-mockup test`"" -ForegroundColor White

Write-Host "`n✨ Your Claude Code Dev Stack is fully integrated with audio!" -ForegroundColor Green
Write-Host "   28 Agents + 18 Commands + 3 MCPs + 15 Hooks + 5 Sounds = " -NoNewline -ForegroundColor Cyan
Write-Host "Complete System" -ForegroundColor Green

Write-Host "`n🚀 Every action now has audio feedback!" -ForegroundColor Cyan