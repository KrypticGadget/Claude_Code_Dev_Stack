#!/usr/bin/env pwsh
# Claude Code Dev Stack - Enhanced Installation Verifier v2.1
# Verifies complete integrated system with hooks, audio, and all components

Write-Host @"
╔════════════════════════════════════════════════════════════════╗
║      Claude Code Dev Stack - Installation Verifier v2.1        ║
║        Checking Enhanced Hooks & Complete Integration          ║
╚════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Define paths
$claudeDir = "$env:USERPROFILE\.claude"
$agentsPath = "$claudeDir\agents"
$commandsPath = "$claudeDir\commands"
$hooksPath = "$claudeDir\hooks"
$audioPath = "$claudeDir\audio"
$logsPath = "$claudeDir\logs"
$statePath = "$claudeDir\state"
$settingsPath = "$claudeDir\settings.json"
$mcpPath = "$claudeDir\.mcp.json"

# Initialize counters
$testsTotal = 0
$testsPassed = 0
$components = @{}

Write-Host "`n🔍 Checking installation..." -ForegroundColor Yellow

# Check agents
Write-Host "`n📚 Agents:" -ForegroundColor Cyan
$testsTotal++
if (Test-Path $agentsPath) {
    $agentCount = (Get-ChildItem $agentsPath -Filter "*.md" -File -ErrorAction SilentlyContinue).Count
    if ($agentCount -ge 28) {
        Write-Host "  ✓ All 28 agents found" -ForegroundColor Green
        $testsPassed++
        $components.Agents = $true
    } elseif ($agentCount -gt 0) {
        Write-Host "  ⚠ Found $agentCount agents (expected 28)" -ForegroundColor Yellow
        $components.Agents = "partial"
    } else {
        Write-Host "  ✗ No agents found" -ForegroundColor Red
        $components.Agents = $false
    }
} else {
    Write-Host "  ✗ Agents directory missing" -ForegroundColor Red
    $components.Agents = $false
}

# Check commands
Write-Host "`n⚡ Slash Commands:" -ForegroundColor Cyan
$testsTotal++
if (Test-Path $commandsPath) {
    $cmdCount = (Get-ChildItem $commandsPath -Filter "*.md" -File -ErrorAction SilentlyContinue).Count
    if ($cmdCount -ge 18) {
        Write-Host "  ✓ All 18 commands found" -ForegroundColor Green
        $testsPassed++
        $components.Commands = $true
    } elseif ($cmdCount -gt 0) {
        Write-Host "  ⚠ Found $cmdCount commands (expected 18)" -ForegroundColor Yellow
        $components.Commands = "partial"
    } else {
        Write-Host "  ✗ No commands found" -ForegroundColor Red
        $components.Commands = $false
    }
} else {
    Write-Host "  ✗ Commands directory missing" -ForegroundColor Red
    $components.Commands = $false
}

# Check enhanced hooks
Write-Host "`n🪝 Enhanced Hooks:" -ForegroundColor Cyan
$requiredHooks = @(
    "agent_orchestrator_integrated.py",
    "slash_command_router.py",
    "mcp_gateway_enhanced.py",
    "mcp_initializer.py",
    "audio_player.py",
    "session_loader.py",
    "session_saver.py",
    "model_tracker.py",
    "quality_gate.py"
)

$foundHooks = 0
$missingHooks = @()

foreach ($hook in $requiredHooks) {
    $testsTotal++
    if (Test-Path "$hooksPath\$hook") {
        $foundHooks++
        $testsPassed++
    } else {
        $missingHooks += $hook
    }
}

if ($foundHooks -eq $requiredHooks.Count) {
    Write-Host "  ✓ All critical hooks installed ($foundHooks/$($requiredHooks.Count))" -ForegroundColor Green
    $components.Hooks = $true
} elseif ($foundHooks -gt 0) {
    Write-Host "  ⚠ Partial hooks ($foundHooks/$($requiredHooks.Count))" -ForegroundColor Yellow
    if ($missingHooks.Count -gt 0) {
        Write-Host "    Missing: $($missingHooks -join ', ')" -ForegroundColor Gray
    }
    $components.Hooks = "partial"
} else {
    Write-Host "  ✗ No enhanced hooks found" -ForegroundColor Red
    $components.Hooks = $false
}

# Check audio
Write-Host "`n🎵 Audio System:" -ForegroundColor Cyan
$testsTotal++
if (Test-Path $audioPath) {
    $audioCount = (Get-ChildItem $audioPath -Filter "*.mp3" -ErrorAction SilentlyContinue).Count
    if ($audioCount -ge 5) {
        Write-Host "  ✓ All audio files present ($audioCount files)" -ForegroundColor Green
        $testsPassed++
        $components.Audio = $true
    } elseif ($audioCount -gt 0) {
        Write-Host "  ⚠ Found $audioCount audio files (expected 5)" -ForegroundColor Yellow
        $components.Audio = "partial"
    } else {
        Write-Host "  ✗ No audio files found" -ForegroundColor Red
        $components.Audio = $false
    }
} else {
    Write-Host "  ✗ Audio directory missing" -ForegroundColor Red
    $components.Audio = $false
}

# Check settings
Write-Host "`n⚙️ Configuration:" -ForegroundColor Cyan
$testsTotal++
if (Test-Path $settingsPath) {
    try {
        $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json
        if ($settings.hooks) {
            Write-Host "  ✓ Integrated settings.json with hooks" -ForegroundColor Green
            $testsPassed++
            $components.Settings = $true
        } else {
            Write-Host "  ⚠ settings.json exists but no hooks configured" -ForegroundColor Yellow
            $components.Settings = "partial"
        }
    } catch {
        Write-Host "  ⚠ settings.json exists but couldn't parse" -ForegroundColor Yellow
        $components.Settings = "partial"
    }
} else {
    Write-Host "  ✗ settings.json missing" -ForegroundColor Red
    $components.Settings = $false
}

# Check MCP configuration
Write-Host "`n🔌 MCP Services:" -ForegroundColor Cyan
$testsTotal++
if (Test-Path $mcpPath) {
    Write-Host "  ✓ MCP configuration found" -ForegroundColor Green
    $testsPassed++
    $components.MCP = $true
} else {
    Write-Host "  ⚠ MCP not configured (optional)" -ForegroundColor Yellow
    $components.MCP = "optional"
}

# Check Python
Write-Host "`n🐍 Python Runtime:" -ForegroundColor Cyan
$testsTotal++
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python") {
        Write-Host "  ✓ Python installed: $pythonVersion" -ForegroundColor Green
        $testsPassed++
        $components.Python = $true
    }
} catch {
    Write-Host "  ✗ Python not found (required for hooks)" -ForegroundColor Red
    $components.Python = $false
}

# Quick functional test
Write-Host "`n🧪 Quick Functional Test:" -ForegroundColor Cyan
if ($components.Hooks -eq $true -and $components.Python -eq $true) {
    $testsTotal++
    Write-Host "  Testing slash command router..." -NoNewline
    $testData = '{"prompt":"/new-project test"}'
    $testResult = $testData | python "$hooksPath\slash_command_router.py" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✓" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host " ✗" -ForegroundColor Red
    }
}

# Summary
Write-Host "`n" -NoNewline
Write-Host "═" * 60 -ForegroundColor Cyan
Write-Host "  INSTALLATION SUMMARY" -ForegroundColor White
Write-Host "═" * 60 -ForegroundColor Cyan

$percentage = if ($testsTotal -gt 0) { [math]::Round(($testsPassed / $testsTotal) * 100, 1) } else { 0 }

Write-Host "`n📊 Test Results:" -ForegroundColor Cyan
Write-Host "  Tests Passed: $testsPassed/$testsTotal ($percentage%)" -ForegroundColor $(
    if ($percentage -ge 90) { "Green" }
    elseif ($percentage -ge 70) { "Yellow" }
    else { "Red" }
)

Write-Host "`n📦 Component Status:" -ForegroundColor Cyan
foreach ($comp in $components.GetEnumerator()) {
    $status = $comp.Value
    $color = switch ($status) {
        $true { "Green" }
        "partial" { "Yellow" }
        "optional" { "Gray" }
        default { "Red" }
    }
    $symbol = switch ($status) {
        $true { "✓" }
        "partial" { "⚠" }
        "optional" { "•" }
        default { "✗" }
    }
    Write-Host "  $symbol $($comp.Key)" -ForegroundColor $color
}

# Recommendations
Write-Host "`n💡 Recommendations:" -ForegroundColor Cyan
if ($percentage -eq 100) {
    Write-Host "  ✅ System fully operational!" -ForegroundColor Green
    Write-Host "     Your Claude Code Dev Stack is ready for 6-9x faster development!" -ForegroundColor Cyan
} elseif ($percentage -ge 80) {
    Write-Host "  ⚠ System mostly operational with minor issues" -ForegroundColor Yellow
    if ($components.Python -eq $false) {
        Write-Host "     • Install Python from https://python.org" -ForegroundColor Yellow
    }
    if ($components.Audio -ne $true) {
        Write-Host "     • Run install-hooks.ps1 to add audio support" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ❌ System needs configuration" -ForegroundColor Red
    Write-Host "     Run the following to complete setup:" -ForegroundColor Yellow
    Write-Host "     .\platform-tools\windows\installers\install-all.ps1" -ForegroundColor Cyan
}

# Return status code
if ($percentage -eq 100) {
    return 0  # Fully installed
} elseif ($percentage -ge 70) {
    return 1  # Partially installed
} else {
    return 2  # Not properly installed
}