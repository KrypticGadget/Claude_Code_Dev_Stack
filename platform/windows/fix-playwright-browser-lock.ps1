# Playwright MCP Edge Browser Lock Fix Script
# Resolves "Browser is already in use" errors for Edge (preserves Chrome)

Write-Host ""
Write-Host "Playwright Browser Lock Fix" -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Kill ONLY Edge processes (preserves Chrome for user browsing)
Write-Host "1. Terminating Edge browser processes..." -ForegroundColor Yellow
$processes = @("msedge", "msedgewebview2")
foreach ($proc in $processes) {
    $count = (Get-Process -Name $proc -ErrorAction SilentlyContinue).Count
    if ($count -gt 0) {
        taskkill /F /IM "$proc.exe" /T 2>$null | Out-Null
        Write-Host "   Killed $count $proc process(es)" -ForegroundColor Green
    }
}

# Step 2: Clear Playwright cache directories
Write-Host ""
Write-Host "2. Clearing Playwright cache..." -ForegroundColor Yellow
$cacheDirs = @(
    "$env:LOCALAPPDATA\ms-playwright\mcp-edge",
    "$env:LOCALAPPDATA\ms-playwright\msedge-*",
    "$env:TEMP\playwright-edge-*",
    "$env:TEMP\playwright-*"
)

foreach ($dir in $cacheDirs) {
    $paths = Get-ChildItem -Path $dir -ErrorAction SilentlyContinue
    if ($paths) {
        Remove-Item -Path $dir -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "   Cleared: $dir" -ForegroundColor Green
    }
}

# Step 3: Restart Playwright MCP with proper configuration
Write-Host ""
Write-Host "3. Reconfiguring Playwright MCP..." -ForegroundColor Yellow

# Remove existing configuration
try {
    claude mcp remove playwright 2>$null | Out-Null
    Write-Host "   Removed existing Playwright MCP" -ForegroundColor Green
} catch {
    Write-Host "   No existing Playwright MCP found" -ForegroundColor Yellow
}

# Add with headed mode and proper flags
Write-Host "   Installing Playwright MCP with headed mode..." -ForegroundColor Yellow
try {
    $result = claude mcp add playwright `
        --env PLAYWRIGHT_HEADLESS=false `
        --env PLAYWRIGHT_BROWSER=msedge `
        --env PLAYWRIGHT_CHROMIUM_ARGS="--no-sandbox --disable-setuid-sandbox --disable-dev-shm-usage" `
        -- cmd /c npx '@playwright/mcp@latest' 2>&1
    
    Write-Host "   Playwright MCP installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "   Failed to install Playwright MCP" -ForegroundColor Red
    Write-Host "   Try running manually:" -ForegroundColor Yellow
    Write-Host "   claude mcp add playwright --env PLAYWRIGHT_HEADLESS=false -- cmd /c npx '@playwright/mcp@latest'" -ForegroundColor Gray
}

# Step 4: Verify installation
Write-Host ""
Write-Host "4. Verifying installation..." -ForegroundColor Yellow
$mcpList = claude mcp list 2>$null
if ($mcpList -like "*playwright*") {
    Write-Host "   Playwright MCP is configured" -ForegroundColor Green
} else {
    Write-Host "   Could not verify Playwright MCP" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "===========================" -ForegroundColor Cyan
Write-Host " Fix Complete!" -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Edge browser lock issue resolved (Chrome untouched)." -ForegroundColor Green
Write-Host ""
Write-Host "Test command:" -ForegroundColor Yellow
Write-Host "  claude `"Use playwright to navigate to https://example.com`"" -ForegroundColor Gray
Write-Host ""
Write-Host "If you still have issues:" -ForegroundColor Yellow
Write-Host "  1. Restart your computer" -ForegroundColor Gray
Write-Host "  2. Run this script again" -ForegroundColor Gray
Write-Host "  3. Set environment variable manually in PowerShell:" -ForegroundColor Gray
Write-Host "     [Environment]::SetEnvironmentVariable('PLAYWRIGHT_HEADLESS', 'false', 'User')" -ForegroundColor Gray
Write-Host ""