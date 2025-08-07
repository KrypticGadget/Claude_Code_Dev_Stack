# Audio Fix and Test Script
Write-Host "Audio Hook Fix Script" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan
Write-Host ""

# Copy fixed audio hooks
Write-Host "1. Updating audio hooks..." -ForegroundColor Yellow
$sourceDir = "C:\Users\Zach\Desktop\Master Code\Claude_Code_Agents\Claude_Code_Dev_Stack\.claude-example\hooks"
$destDir = "C:\Users\Zach\.claude\hooks"

Copy-Item "$sourceDir\audio_player.py" -Destination "$destDir\" -Force
Copy-Item "$sourceDir\audio_notifier.py" -Destination "$destDir\" -Force
Write-Host "   OK - Audio hooks updated" -ForegroundColor Green

# Test audio with Python
Write-Host ""
Write-Host "2. Testing audio playback..." -ForegroundColor Yellow
$testScript = @'
import winsound
import os
from pathlib import Path

audio_file = Path.home() / ".claude" / "audio" / "ready.wav"
if audio_file.exists():
    print(f"   Playing: {audio_file}")
    try:
        winsound.PlaySound(str(audio_file), winsound.SND_FILENAME)
        print("   OK - Audio test successful!")
    except Exception as e:
        print(f"   ERROR - Audio error: {e}")
else:
    print(f"   ERROR - Audio file not found: {audio_file}")
    print("   Make sure you have .wav files in C:\\Users\\Zach\\.claude\\audio\\")
'@

python -c $testScript

Write-Host ""
Write-Host "3. Checking audio files..." -ForegroundColor Yellow
$audioDir = "$env:USERPROFILE\.claude\audio"
if (Test-Path $audioDir) {
    $wavFiles = Get-ChildItem "$audioDir\*.wav" -ErrorAction SilentlyContinue
    if ($wavFiles) {
        Write-Host "   Found WAV files:" -ForegroundColor Green
        $wavFiles | ForEach-Object { Write-Host "     - $($_.Name)" -ForegroundColor Gray }
    } else {
        Write-Host "   WARNING - No WAV files found!" -ForegroundColor Yellow
        Write-Host "   You need these files in $audioDir :" -ForegroundColor Yellow
        @("ready.wav", "task_complete.wav", "build_complete.wav", "error_fixed.wav", "awaiting_instructions.wav") | ForEach-Object {
            Write-Host "     - $_" -ForegroundColor Gray
        }
    }
}

Write-Host ""
Write-Host "Done! The audio hooks now use winsound which:" -ForegroundColor Green
Write-Host "  - Works with WAV files" -ForegroundColor Gray
Write-Host "  - Will not minimize your PowerShell window" -ForegroundColor Gray
Write-Host "  - Plays silently in background" -ForegroundColor Gray
Write-Host ""
Write-Host "Test in Claude Code with:" -ForegroundColor Yellow
Write-Host '  Create a file called TEST.txt' -ForegroundColor Gray