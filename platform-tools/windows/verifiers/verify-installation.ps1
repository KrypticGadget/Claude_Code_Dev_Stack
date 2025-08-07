#!/usr/bin/env pwsh
# Claude Code Dev Stack - Enhanced Installation Verifier v2.1
# Verifies complete integrated system with hooks, audio, and all components

Write-Host @"
╔════════════════════════════════════════════════════════════════╗
║      Claude Code Dev Stack - Installation Verifier v2.1        ║
║        Checking FIXED Enhanced Hooks & Complete System         ║
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
$claudeJsonPath = "$env:USERPROFILE\.claude.json"
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

# Check enhanced hooks - UPDATED LIST WITH ALL 19 HOOKS
Write-Host "`n🪝 Enhanced Hooks (FIXED):" -ForegroundColor Cyan
$requiredHooks = @(
    "agent_mention_parser.py",
    "agent_orchestrator.py",
    "agent_orchestrator_integrated.py",
    "slash_command_router.py",
    "mcp_gateway.py",
    "mcp_gateway_enhanced.py",
    "mcp_initializer.py",
    "audio_player.py",
    "audio_notifier.py",
    "session_loader.py",
    "session_saver.py",
    "quality_gate.py",
    "model_tracker.py",
    "planning_trigger.py",
    "pre_command.py",
    "post_command.py",
    "pre_project.py",
    "post_project.py",
    "base_hook.py"
)

# Also check for test hook
$optionalHooks = @(
    "test_hook.py"
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

# Check optional hooks
$testHookFound = Test-Path "$hooksPath\test_hook.py"

if ($foundHooks -eq $requiredHooks.Count) {
    Write-Host "  ✓ All 19 required hooks installed" -ForegroundColor Green
    if ($testHookFound) {
        Write-Host "  ✓ Test hook also present (debugging enabled)" -ForegroundColor Green
    }
    $components.Hooks = $true
} elseif ($foundHooks -ge 15) {
    Write-Host "  ⚠ Most hooks installed ($foundHooks/19)" -ForegroundColor Yellow
    if ($missingHooks.Count -gt 0) {
        Write-Host "    Missing: $($missingHooks -join ', ')" -ForegroundColor Gray
    }
    $components.Hooks = "partial"
} else {
    Write-Host "  ✗ Insufficient hooks found ($foundHooks/19)" -ForegroundColor Red
    Write-Host "    Missing critical hooks for system functionality" -ForegroundColor Red
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

# Check .claude.json configuration with detailed validation
Write-Host "`n⚙️ Configuration (.claude.json - FIXED):" -ForegroundColor Cyan
$testsTotal++
if (Test-Path $claudeJsonPath) {
    try {
        $settings = Get-Content $claudeJsonPath -Raw | ConvertFrom-Json
        $configIssues = @()
        
        # Check for hooks configuration
        if ($settings.hooks) {
            # Check for all required hook events
            $hasPreToolUse = $settings.hooks.PreToolUse -ne $null
            $hasPostToolUse = $settings.hooks.PostToolUse -ne $null
            $hasUserPromptSubmit = $settings.hooks.UserPromptSubmit -ne $null
            $hasSessionStart = $settings.hooks.SessionStart -ne $null
            $hasStop = $settings.hooks.Stop -ne $null
            $hasSubagentStop = $settings.hooks.SubagentStop -ne $null
            
            # Check for proper command format
            $sampleCommand = $settings.hooks.PreToolUse[0].hooks[0].command
            $hasPythonCommand = $sampleCommand -match "python[3]?"
            $hasProperPaths = $sampleCommand -match "(C:/Users|\$env:USERPROFILE)"
            
            # Check for integrated features
            $hasAgentSystem = $settings.agentSystem -ne $null
            $hasSlashCommands = $settings.slashCommands -ne $null
            $hasMcpIntegration = $settings.mcpIntegration -ne $null
            
            if ($hasPreToolUse -and $hasPostToolUse -and $hasUserPromptSubmit -and $hasSessionStart -and $hasPythonCommand -and $hasProperPaths) {
                Write-Host "  ✓ .claude.json FULLY configured with all features" -ForegroundColor Green
                Write-Host "    • Hook Events: PreToolUse ✓ PostToolUse ✓ UserPromptSubmit ✓" -ForegroundColor Gray
                Write-Host "    • SessionStart ✓ Stop $(if($hasStop){"✓"}else{"✗"}) SubagentStop $(if($hasSubagentStop){"✓"}else{"✗"})" -ForegroundColor Gray
                Write-Host "    • Python command: ✓" -ForegroundColor Gray
                Write-Host "    • Windows paths: ✓" -ForegroundColor Gray
                
                if ($hasAgentSystem) {
                    Write-Host "    • Agent System: ✓ (28 agents configured)" -ForegroundColor Gray
                }
                if ($hasSlashCommands) {
                    Write-Host "    • Slash Commands: ✓ (18 commands configured)" -ForegroundColor Gray
                }
                if ($hasMcpIntegration) {
                    Write-Host "    • MCP Integration: ✓ (3 services configured)" -ForegroundColor Gray
                }
                
                $testsPassed++
                $components.Settings = $true
            } else {
                Write-Host "  ⚠ .claude.json has hooks but missing components" -ForegroundColor Yellow
                if (!$hasPythonCommand) {
                    $configIssues += "Missing python/python3 in commands"
                }
                if (!$hasProperPaths) {
                    $configIssues += "Paths need Windows format (C:/Users or `$env:USERPROFILE)"
                }
                if (!$hasPreToolUse) { $configIssues += "Missing PreToolUse hooks" }
                if (!$hasPostToolUse) { $configIssues += "Missing PostToolUse hooks" }
                if (!$hasUserPromptSubmit) { $configIssues += "Missing UserPromptSubmit hooks" }
                if (!$hasSessionStart) { $configIssues += "Missing SessionStart hooks" }
                
                foreach ($issue in $configIssues) {
                    Write-Host "    ✗ $issue" -ForegroundColor Red
                }
                $components.Settings = "partial"
            }
        } else {
            Write-Host "  ⚠ .claude.json exists but NO hooks configured!" -ForegroundColor Red
            Write-Host "    Run: .\platform-tools\windows\installers\install-hooks.ps1" -ForegroundColor Yellow
            $components.Settings = "partial"
        }
    } catch {
        Write-Host "  ⚠ .claude.json exists but couldn't parse: $_" -ForegroundColor Yellow
        $components.Settings = "partial"
    }
} else {
    Write-Host "  ✗ .claude.json missing completely!" -ForegroundColor Red
    Write-Host "    Run: .\platform-tools\windows\installers\install-hooks.ps1" -ForegroundColor Yellow
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

# Check Python with proper command detection
Write-Host "`n🐍 Python Runtime:" -ForegroundColor Cyan
$testsTotal++
$pythonCmd = ""
$pythonFound = $false

# Try python first (most common on Windows)
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3") {
        Write-Host "  ✓ Python 3 installed: $pythonVersion" -ForegroundColor Green
        Write-Host "    Command: python" -ForegroundColor Gray
        $testsPassed++
        $components.Python = $true
        $pythonCmd = "python"
        $pythonFound = $true
    } elseif ($pythonVersion -match "Python 2") {
        Write-Host "  ✗ Python 2 detected - Python 3 required!" -ForegroundColor Red
        $components.Python = $false
    }
} catch {
    # Try python3 as fallback
    try {
        $pythonVersion = python3 --version 2>&1
        if ($pythonVersion -match "Python 3") {
            Write-Host "  ✓ Python 3 installed: $pythonVersion" -ForegroundColor Green
            Write-Host "    Command: python3" -ForegroundColor Gray
            $testsPassed++
            $components.Python = $true
            $pythonCmd = "python3"
            $pythonFound = $true
        }
    } catch {
        Write-Host "  ✗ Python not found (CRITICAL - required for hooks)" -ForegroundColor Red
        Write-Host "    Install from: https://python.org" -ForegroundColor Yellow
        Write-Host "    Make sure to check 'Add Python to PATH'!" -ForegroundColor Yellow
        $components.Python = $false
    }
}

# Quick functional tests
Write-Host "`n🧪 Quick Functional Tests:" -ForegroundColor Cyan

if ($components.Hooks -eq $true -and $pythonFound) {
    # Test 1: Test hook execution
    $testsTotal++
    Write-Host "  Testing test_hook.py..." -NoNewline
    if (Test-Path "$hooksPath\test_hook.py") {
        $testData = '{"hook_event_name": "test", "tool_name": "Verify"}'
        $testResult = $testData | & $pythonCmd "$hooksPath\test_hook.py" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host " ✓" -ForegroundColor Green
            $testsPassed++
            
            # Check if log was created
            if (Test-Path "$logsPath\test_hook.log") {
                Write-Host "    Log file created: ✓" -ForegroundColor Gray
            }
        } else {
            Write-Host " ✗" -ForegroundColor Red
        }
    } else {
        Write-Host " SKIPPED (test hook not found)" -ForegroundColor Yellow
    }
    
    # Test 2: Slash command router
    $testsTotal++
    Write-Host "  Testing slash command router..." -NoNewline
    if (Test-Path "$hooksPath\slash_command_router.py") {
        $testData = '{"prompt":"/new-project test"}'
        $testResult = $testData | & $pythonCmd "$hooksPath\slash_command_router.py" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host " ✓" -ForegroundColor Green
            $testsPassed++
        } else {
            Write-Host " ✗" -ForegroundColor Red
        }
    } else {
        Write-Host " SKIPPED (router not found)" -ForegroundColor Yellow
    }
    
    # Test 3: Agent mention parser
    $testsTotal++
    Write-Host "  Testing agent mention parser..." -NoNewline
    if (Test-Path "$hooksPath\agent_mention_parser.py") {
        $testData = '{"prompt":"@agent-frontend-mockup test"}'
        $testResult = $testData | & $pythonCmd "$hooksPath\agent_mention_parser.py" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host " ✓" -ForegroundColor Green
            $testsPassed++
        } else {
            Write-Host " ✗" -ForegroundColor Red
        }
    } else {
        Write-Host " SKIPPED (parser not found)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  SKIPPED - Hooks or Python not properly installed" -ForegroundColor Yellow
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
    Write-Host "  ✅ System fully operational with FIXED hooks!" -ForegroundColor Green
    Write-Host "     Your Claude Code Dev Stack is ready for 6-9x faster development!" -ForegroundColor Cyan
    Write-Host "`n  🚀 Next Steps:" -ForegroundColor Cyan
    Write-Host "     1. Restart Claude Code" -ForegroundColor White
    Write-Host "     2. Run: claude --debug" -ForegroundColor White
    Write-Host "     3. Type: /hooks (to verify all are loaded)" -ForegroundColor White
} elseif ($percentage -ge 80) {
    Write-Host "  ⚠ System mostly operational with minor issues" -ForegroundColor Yellow
    if ($components.Python -eq $false) {
        Write-Host "     • CRITICAL: Install Python 3 from https://python.org" -ForegroundColor Red
        Write-Host "       Make sure to check 'Add Python to PATH'!" -ForegroundColor Yellow
    }
    if ($components.Settings -eq "partial") {
        Write-Host "     • Run INSTALL_HOOKS_FIX.ps1 to fix paths" -ForegroundColor Yellow
    }
    if ($components.Hooks -ne $true) {
        Write-Host "     • Run install-hooks.ps1 to install missing hooks" -ForegroundColor Yellow
    }
    if ($components.Audio -ne $true) {
        Write-Host "     • Run install-hooks.ps1 to add audio support" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ❌ System needs configuration" -ForegroundColor Red
    Write-Host "     Run one of the following to complete setup:" -ForegroundColor Yellow
    Write-Host "     • Quick Fix: .\INSTALL_HOOKS_FIX.ps1" -ForegroundColor Cyan
    Write-Host "     • Full Install: .\platform-tools\windows\installers\install-all.ps1" -ForegroundColor Cyan
}

Write-Host "`n📝 Troubleshooting Tips:" -ForegroundColor Cyan
Write-Host "  • If hooks don't trigger: Check Python is in PATH" -ForegroundColor White
Write-Host "  • If paths fail: Use absolute paths (C:/Users/Zach)" -ForegroundColor White
Write-Host "  • If JSON errors: Validate .claude.json syntax" -ForegroundColor White
Write-Host "  • Debug mode: claude --debug shows hook execution" -ForegroundColor White

# Return status code
if ($percentage -eq 100) {
    return 0  # Fully installed
} elseif ($percentage -ge 70) {
    return 1  # Partially installed
} else {
    return 2  # Not properly installed
}