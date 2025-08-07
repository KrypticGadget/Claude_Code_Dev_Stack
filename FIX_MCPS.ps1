# Quick MCP Fix Script
Write-Host "MCP Quick Fix Script" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan
Write-Host ""

# Fix Playwright MCP
Write-Host "1. Fixing Playwright MCP..." -ForegroundColor Yellow
claude mcp remove playwright 2>$null | Out-Null
claude mcp add playwright -- cmd /c npx "@playwright/mcp@latest" --headless
Write-Host "   ✓ Playwright MCP fixed" -ForegroundColor Green

# Fix Obsidian MCP
Write-Host ""
Write-Host "2. Fixing Obsidian MCP..." -ForegroundColor Yellow
Write-Host "   Installing mcp-obsidian package..." -ForegroundColor Gray
pip install mcp-obsidian --upgrade --quiet
claude mcp remove obsidian 2>$null | Out-Null

$apiKey = Read-Host "   Enter your Obsidian API key (or press Enter to skip)"
if ($apiKey) {
    claude mcp add obsidian --env OBSIDIAN_API_KEY=$apiKey -- python -m mcp_obsidian
    Write-Host "   ✓ Obsidian MCP fixed" -ForegroundColor Green
} else {
    Write-Host "   ⚠ Skipped Obsidian (no API key)" -ForegroundColor Yellow
}

# Fix Web-search MCP
Write-Host ""
Write-Host "3. Fixing Web-search MCP..." -ForegroundColor Yellow
$webSearchDir = "$env:USERPROFILE\mcp-servers\web-search"
if (Test-Path "$webSearchDir\build\index.js") {
    claude mcp remove web-search 2>$null | Out-Null
    claude mcp add web-search -- cmd /c node "$webSearchDir\build\index.js"
    Write-Host "   ✓ Web-search MCP fixed" -ForegroundColor Green
} else {
    Write-Host "   ⚠ Web-search not installed, run install-mcps.ps1 first" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Current MCP Status:" -ForegroundColor Cyan
claude mcp list

Write-Host ""
Write-Host "Done! Test with:" -ForegroundColor Green
Write-Host '  claude "Use playwright to navigate to example.com"' -ForegroundColor Gray
Write-Host '  claude "Use web-search to find news about AI"' -ForegroundColor Gray
if ($apiKey) {
    Write-Host '  claude "Use obsidian to list files in vault"' -ForegroundColor Gray
}