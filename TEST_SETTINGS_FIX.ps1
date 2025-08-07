# Test script to verify settings.json fix

$pythonCmd = "python"
$settingsUrl = "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example/settings-integrated.json"

Write-Host "Downloading and fixing settings.json..." -ForegroundColor Cyan

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
    
    # Save to test file
    $settingsContent | Out-File "TEST_SETTINGS.json" -Encoding UTF8
    Write-Host "✓ Saved to TEST_SETTINGS.json" -ForegroundColor Green
    
    # Try to parse it
    Write-Host "`nValidating JSON..." -ForegroundColor Yellow
    $test = Get-Content "TEST_SETTINGS.json" -Raw | ConvertFrom-Json
    Write-Host "✓ JSON is valid!" -ForegroundColor Green
    
    # Show a sample command
    Write-Host "`nSample command:" -ForegroundColor Cyan
    Write-Host $test.hooks.PreToolUse[0].hooks[0].command -ForegroundColor White
    
} catch {
    Write-Host "✗ Error: $_" -ForegroundColor Red
}