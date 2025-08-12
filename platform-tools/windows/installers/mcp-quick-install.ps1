# MCP Quick Install - One-liner installer
# Run from anywhere: iwr -useb https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers/mcp-quick-install.ps1 | iex

# Download and run the full installer
$installerUrl = "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/installers/install-mcps.ps1"
$tempInstaller = "$env:TEMP\install-mcps-temp.ps1"

Write-Host "Downloading MCP installer..." -ForegroundColor Cyan
Invoke-WebRequest -Uri $installerUrl -OutFile $tempInstaller -UseBasicParsing

Write-Host "Running installer..." -ForegroundColor Cyan
powershell -ExecutionPolicy Bypass -File $tempInstaller

# Clean up
Remove-Item $tempInstaller -Force -ErrorAction SilentlyContinue

Write-Host "Installation complete!" -ForegroundColor Green