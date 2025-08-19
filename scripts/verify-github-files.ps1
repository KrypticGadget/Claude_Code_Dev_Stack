Write-Host "Verifying all files exist on GitHub..." -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor DarkGray

$baseUrl = "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example"

# Test agents
Write-Host "`nChecking Agents..." -ForegroundColor Yellow
$agents = @(
    "api-integration-specialist.md",
    "backend-services.md",
    "business-analyst.md"
)

$agentErrors = 0
foreach ($agent in $agents) {
    $url = "$baseUrl/agents/$agent"
    try {
        $response = Invoke-WebRequest -Uri $url -Method Head -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        Write-Host "  ✓ $agent" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ $agent - 404" -ForegroundColor Red
        $agentErrors++
    }
}

# Test commands
Write-Host "`nChecking Commands..." -ForegroundColor Yellow
$commands = @(
    "new-project.md",
    "backend-service.md",
    "frontend-mockup.md"
)

$commandErrors = 0
foreach ($command in $commands) {
    $url = "$baseUrl/commands/$command"
    try {
        $response = Invoke-WebRequest -Uri $url -Method Head -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        Write-Host "  ✓ $command" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ $command - 404" -ForegroundColor Red
        $commandErrors++
    }
}

# Test hooks
Write-Host "`nChecking Hooks..." -ForegroundColor Yellow
$hooks = @(
    "session_loader.py",
    "agent_mention_parser.py",
    "base_hook.py"
)

$hookErrors = 0
foreach ($hook in $hooks) {
    $url = "$baseUrl/hooks/$hook"
    try {
        $response = Invoke-WebRequest -Uri $url -Method Head -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        Write-Host "  ✓ $hook" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ $hook - 404" -ForegroundColor Red
        $hookErrors++
    }
}

Write-Host "`n" + "=" * 50 -ForegroundColor Cyan
if (($agentErrors + $commandErrors + $hookErrors) -eq 0) {
    Write-Host "✅ All files accessible on GitHub!" -ForegroundColor Green
    Write-Host "Safe to run installer." -ForegroundColor Green
} else {
    Write-Host "⚠️ Some files missing on GitHub!" -ForegroundColor Red
    Write-Host "Agents missing: $agentErrors" -ForegroundColor Yellow
    Write-Host "Commands missing: $commandErrors" -ForegroundColor Yellow
    Write-Host "Hooks missing: $hookErrors" -ForegroundColor Yellow
    Write-Host "`nPush your changes to GitHub first!" -ForegroundColor Yellow
}