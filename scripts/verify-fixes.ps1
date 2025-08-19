Write-Host ""
Write-Host "Verifying Agent, Hooks and MCP Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check agents
Write-Host ""
Write-Host "Checking Agents:" -ForegroundColor Yellow
$agentFiles = @(
    ".claude-example\agents\api-integration-specialist.md",
    ".claude-example\agents\backend-services.md",
    ".claude-example\agents\business-analyst.md",
    ".claude-example\agents\business-tech-alignment.md",
    ".claude-example\agents\ceo-strategy.md",
    ".claude-example\agents\database-architecture.md",
    ".claude-example\agents\development-prompt.md",
    ".claude-example\agents\devops-engineering.md",
    ".claude-example\agents\financial-analyst.md",
    ".claude-example\agents\frontend-architecture.md",
    ".claude-example\agents\frontend-mockup.md",
    ".claude-example\agents\integration-setup.md",
    ".claude-example\agents\master-orchestrator.md",
    ".claude-example\agents\middleware-specialist.md",
    ".claude-example\agents\mobile-development.md",
    ".claude-example\agents\performance-optimization.md",
    ".claude-example\agents\production-frontend.md",
    ".claude-example\agents\project-manager.md",
    ".claude-example\agents\prompt-engineer.md",
    ".claude-example\agents\quality-assurance.md",
    ".claude-example\agents\script-automation.md",
    ".claude-example\agents\security-architecture.md",
    ".claude-example\agents\technical-cto.md",
    ".claude-example\agents\technical-documentation.md",
    ".claude-example\agents\technical-specifications.md",
    ".claude-example\agents\testing-automation.md",
    ".claude-example\agents\ui-ux-design.md",
    ".claude-example\agents\usage-guide.md"
)

$validAgents = 0
$problemAgents = @()

foreach ($file in $agentFiles) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        if ($content -match '(?s)^---.*?name:\s*\S+.*?---') {
            $validAgents++
            Write-Host "  OK: $(Split-Path $file -Leaf) - Valid YAML" -ForegroundColor Green
        } else {
            Write-Host "  FAIL: $(Split-Path $file -Leaf) - Missing/Invalid YAML" -ForegroundColor Red
            $problemAgents += Split-Path $file -Leaf
        }
    } else {
        Write-Host "  WARN: $(Split-Path $file -Leaf) - File not found" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Total: $validAgents/28 agents properly configured" -ForegroundColor $(if ($validAgents -eq 28) {'Green'} else {'Yellow'})

if ($problemAgents.Count -gt 0) {
    Write-Host ""
    Write-Host "Problem agents:" -ForegroundColor Red
    $problemAgents | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
}

# Check hooks configuration
Write-Host ""
Write-Host "Checking Hooks Configuration:" -ForegroundColor Yellow
if (Test-Path ".claude-example\settings.json") {
    $settings = Get-Content ".claude-example\settings.json" -Raw | ConvertFrom-Json -ErrorAction SilentlyContinue
    if ($settings -and $settings.hooks) {
        Write-Host "  OK: Hooks configuration found" -ForegroundColor Green
        $hookEvents = $settings.hooks.PSObject.Properties.Name
        Write-Host "  Events configured: $($hookEvents -join ', ')" -ForegroundColor Gray
        
        # Check for all expected events
        $expectedEvents = @("SessionStart", "UserPromptSubmit", "PreToolUse", "PostToolUse", "Stop", "SubagentStop")
        $missingEvents = $expectedEvents | Where-Object { $_ -notin $hookEvents }
        if ($missingEvents.Count -eq 0) {
            Write-Host "  OK: All expected hook events configured" -ForegroundColor Green
        } else {
            Write-Host "  WARN: Missing events: $($missingEvents -join ', ')" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  FAIL: Invalid or missing hooks configuration" -ForegroundColor Red
    }
} else {
    Write-Host "  FAIL: Missing settings.json" -ForegroundColor Red
}

# Check hook files
Write-Host ""
Write-Host "Checking Hook Scripts:" -ForegroundColor Yellow
$hookFiles = @(
    ".claude-example\hooks\session_loader.py",
    ".claude-example\hooks\agent_mention_parser.py",
    ".claude-example\hooks\quality_gate.py",
    ".claude-example\hooks\post_command.py",
    ".claude-example\hooks\session_saver.py",
    ".claude-example\hooks\model_tracker.py"
)

foreach ($hookFile in $hookFiles) {
    if (Test-Path $hookFile) {
        Write-Host "  OK: $(Split-Path $hookFile -Leaf) exists" -ForegroundColor Green
    } else {
        Write-Host "  WARN: $(Split-Path $hookFile -Leaf) missing" -ForegroundColor Yellow
    }
}

# Check MCP documentation
Write-Host ""
Write-Host "Checking MCP Documentation:" -ForegroundColor Yellow
$mcpDocs = @(
    "docs\MCP_INSTALLATION.md",
    "docs\reference\MCP_GUIDE.md",
    ".claude-example\.mcp.json"
)

foreach ($doc in $mcpDocs) {
    if (Test-Path $doc) {
        Write-Host "  OK: $(Split-Path $doc -Leaf) exists" -ForegroundColor Green
    } else {
        Write-Host "  FAIL: $(Split-Path $doc -Leaf) missing" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Remember:" -ForegroundColor Yellow
Write-Host "  1. Copy .claude-example to .claude in your user directory" -ForegroundColor White
Write-Host "  2. MCPs must be installed manually with 'claude mcp add' commands" -ForegroundColor White
Write-Host "  3. Restart Claude Code after changes" -ForegroundColor White
Write-Host ""
Write-Host "Run this verification after applying fixes!" -ForegroundColor Cyan