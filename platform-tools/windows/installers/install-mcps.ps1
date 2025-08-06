# Simple Claude Code MCPs Installer
# Downloads MCP configuration files

Write-Host "Claude Code MCPs Installer" -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan

# Setup paths
$claudeDir = "$env:USERPROFILE\.claude"

# Create directory
Write-Host "Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $claudeDir | Out-Null

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
        Invoke-WebRequest -Uri $config.Url -OutFile $dest -UseBasicParsing -TimeoutSec 10
        Write-Host "OK" -ForegroundColor Green
    } catch {
        Write-Host "FAILED" -ForegroundColor Red
    }
}

Write-Host "`nComplete!" -ForegroundColor Cyan
Write-Host "MCPs configured in: $claudeDir" -ForegroundColor White
Write-Host "`nNote: MCPs (Playwright, Obsidian, Brave Search) need to be installed separately" -ForegroundColor Yellow

exit 0