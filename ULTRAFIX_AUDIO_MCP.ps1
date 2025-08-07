# ULTRAFIX Script - Definitively fixes Audio and MCP issues
Write-Host "ULTRAFIX - Audio and MCP Repair Tool" -ForegroundColor Magenta
Write-Host "=====================================" -ForegroundColor Magenta
Write-Host ""

# Fix 1: Update audio player hook with better debugging
Write-Host "1. Updating audio player hook..." -ForegroundColor Yellow
$sourceHook = "C:\Users\Zach\Desktop\Master Code\Claude_Code_Agents\Claude_Code_Dev_Stack\.claude-example\hooks\audio_player.py"
$destHook = "C:\Users\Zach\.claude\hooks\audio_player.py"

if (Test-Path $sourceHook) {
    Copy-Item $sourceHook -Destination $destHook -Force
    Write-Host "   OK - Audio hook updated with enhanced debugging" -ForegroundColor Green
} else {
    Write-Host "   ERROR - Source hook not found!" -ForegroundColor Red
}

# Fix 2: Verify WAV files exist
Write-Host ""
Write-Host "2. Checking audio files..." -ForegroundColor Yellow
$audioDir = "C:\Users\Zach\.claude\audio"

if (!(Test-Path $audioDir)) {
    New-Item -ItemType Directory -Path $audioDir -Force | Out-Null
    Write-Host "   Created audio directory" -ForegroundColor Green
}

# Copy WAV files from source
$sourceAudio = "C:\Users\Zach\Desktop\Master Code\Claude_Code_Agents\Claude_Code_Dev_Stack\.claude-example\audio"
$wavFiles = @("ready.wav", "task_complete.wav", "build_complete.wav", "error_fixed.wav", "awaiting_instructions.wav")

foreach ($wav in $wavFiles) {
    $source = "$sourceAudio\$wav"
    $dest = "$audioDir\$wav"
    if (Test-Path $source) {
        Copy-Item $source -Destination $dest -Force
        Write-Host "   OK - Copied $wav" -ForegroundColor Green
    } else {
        Write-Host "   WARNING - $wav not found in source" -ForegroundColor Yellow
    }
}

# Fix 3: Test audio directly with Python
Write-Host ""
Write-Host "3. Testing audio playback..." -ForegroundColor Yellow
$testScript = @'
import winsound
import os
from pathlib import Path

audio_file = Path.home() / ".claude" / "audio" / "ready.wav"
print(f"Testing audio file: {audio_file}")

if audio_file.exists():
    print(f"File exists: YES")
    print(f"File size: {audio_file.stat().st_size} bytes")
    try:
        # Test synchronous playback
        winsound.PlaySound(str(audio_file), winsound.SND_FILENAME)
        print("SUCCESS - Audio played!")
    except Exception as e:
        print(f"ERROR - Could not play audio: {e}")
else:
    print(f"ERROR - File not found at: {audio_file}")
'@

python -c $testScript

# Fix 4: Reinstall Obsidian MCP with correct command
Write-Host ""
Write-Host "4. Fixing Obsidian MCP..." -ForegroundColor Yellow

# First ensure package is installed
Write-Host "   Installing mcp-obsidian package..." -ForegroundColor Gray
pip install mcp-obsidian --upgrade --quiet 2>$null

# Remove old registration
claude mcp remove obsidian 2>$null | Out-Null

# Get API key
Write-Host ""
Write-Host "   Obsidian Local REST API required!" -ForegroundColor Yellow
Write-Host "   1. Open Obsidian -> Settings -> Community Plugins" -ForegroundColor Gray
Write-Host "   2. Search for 'Local REST API'" -ForegroundColor Gray
Write-Host "   3. Install and enable the plugin" -ForegroundColor Gray
Write-Host "   4. Copy the API key from plugin settings" -ForegroundColor Gray
Write-Host ""
$apiKey = Read-Host "   Enter your Obsidian API key (or press Enter to skip)"

if ($apiKey) {
    # CRITICAL: Use underscore not hyphen for Python module name
    claude mcp add obsidian --env OBSIDIAN_API_KEY=$apiKey --env OBSIDIAN_HOST=127.0.0.1 --env OBSIDIAN_PORT=27124 -- python -m mcp_obsidian
    Write-Host "   OK - Obsidian MCP registered with correct command" -ForegroundColor Green
} else {
    Write-Host "   SKIPPED - No API key provided" -ForegroundColor Yellow
}

# Fix 5: Verify all MCP servers
Write-Host ""
Write-Host "5. Current MCP status..." -ForegroundColor Yellow
claude mcp list

# Fix 6: Test hook execution directly
Write-Host ""
Write-Host "6. Testing hook execution..." -ForegroundColor Yellow
$testData = '{"hook_event_name": "SessionStart", "source": "test"}'
$hookPath = "C:\Users\Zach\.claude\hooks\audio_player.py"

if (Test-Path $hookPath) {
    Write-Host "   Running audio hook test..." -ForegroundColor Gray
    $testData | python $hookPath 2>&1
} else {
    Write-Host "   ERROR - Hook not found at: $hookPath" -ForegroundColor Red
}

# Summary
Write-Host ""
Write-Host "=====================================" -ForegroundColor Magenta
Write-Host "ULTRAFIX COMPLETE" -ForegroundColor Magenta
Write-Host "=====================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "What was fixed:" -ForegroundColor Cyan
Write-Host "  - Audio hook updated with better error handling" -ForegroundColor White
Write-Host "  - WAV files copied to correct location" -ForegroundColor White
Write-Host "  - Obsidian MCP uses correct Python module name (mcp_obsidian)" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Exit Claude Code completely (Ctrl+C)" -ForegroundColor White
Write-Host "  2. Restart Claude Code" -ForegroundColor White
Write-Host "  3. Run: claude --debug" -ForegroundColor White
Write-Host "  4. Watch for [AUDIO SUCCESS] messages" -ForegroundColor White
Write-Host "  5. Obsidian MCP should connect if API key was provided" -ForegroundColor White
Write-Host ""
Write-Host "Test commands:" -ForegroundColor Cyan
Write-Host '  claude "Create a file called TEST.txt"   # Should play audio' -ForegroundColor Gray
Write-Host '  claude "Use obsidian to list files"      # Should use Obsidian MCP' -ForegroundColor Gray
Write-Host ""