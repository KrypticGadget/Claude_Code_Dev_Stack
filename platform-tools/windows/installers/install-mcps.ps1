# Simple Claude Code MCPs Installer
# Downloads MCP configuration files

Write-Host "Claude Code MCPs Installer" -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan

# Setup paths
$claudeDir = "$env:USERPROFILE\.claude"

# Create directory (Force creates even if exists)
Write-Host "Setting up directories..." -ForegroundColor Yellow
if (-not (Test-Path $claudeDir)) {
    New-Item -ItemType Directory -Path $claudeDir -Force | Out-Null
}
Write-Host "Directory ready: $claudeDir" -ForegroundColor Green

# Download MCP config files
$configs = @(
    @{Name="settings.json"; Url="https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example/settings.json"},
    @{Name=".mcp.json"; Url="https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example/.mcp.json"}
)

Write-Host "Downloading MCP configurations..." -ForegroundColor Yellow

foreach ($config in $configs) {
    Write-Host "Downloading: $($config.Name)... " -NoNewline
    $dest = "$claudeDir\$($config.Name)"
    
    # Skip if file already exists
    if (Test-Path $dest) {
        Write-Host "EXISTS (skipped)" -ForegroundColor Yellow
        continue
    }
    
    try {
        # Download file using .NET WebClient for proper byte handling  
        $webClient = New-Object System.Net.WebClient
        $bytes = $webClient.DownloadData($config.Url)
        [System.IO.File]::WriteAllBytes($dest, $bytes)
        $webClient.Dispose()
        Write-Host "OK" -ForegroundColor Green
    } catch {
        Write-Host "FAILED" -ForegroundColor Red
    }
}

Write-Host "`nComplete!" -ForegroundColor Cyan
Write-Host "MCPs configured in: $claudeDir" -ForegroundColor White
Write-Host "`nNote: MCPs (Playwright, Obsidian, Brave Search) need to be installed separately" -ForegroundColor Yellow

# Return instead of exit to avoid killing terminal
return 0