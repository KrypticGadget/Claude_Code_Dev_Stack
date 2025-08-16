#!/usr/bin/env powershell
# Comprehensive Testing Suite for Claude Code Dev Stack v3.0
# Tests all integrated components with proper attribution

Write-Host @"
╔════════════════════════════════════════════════════════════════╗
║               Claude Code Dev Stack v3.0                       ║
║                 Comprehensive Test Suite                       ║
║                                                                ║
║  Testing integrated components:                                ║
║  • 28 Agents + 28 Hooks + 18 Commands                         ║
║  • Claude Powerline (@Owloops)                                 ║
║  • Claude Code Browser (@zainhoda)                             ║
║  • Mobile App (@9cat)                                          ║
║  • MCP Manager (@qdhenry)                                      ║
║  • OpenAPI Generators (@cnoe-io, @harsha-iiiv)                ║
╚════════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

$testResults = @{}
$startTime = Get-Date

# Test 1: Core System Components
Write-Host "`n🧪 Testing Core System Components..." -ForegroundColor Yellow

# Test agents
Write-Host "Testing agents..." -ForegroundColor Blue
$agentCount = (Get-ChildItem "core/agents" -Filter "*.py" -ErrorAction SilentlyContinue).Count
$testResults["agents"] = @{
    "expected" = 28
    "found" = $agentCount
    "status" = if ($agentCount -eq 28) { "✅ PASS" } else { "❌ FAIL" }
}

# Test hooks
Write-Host "Testing hooks..." -ForegroundColor Blue
$hookCount = (Get-ChildItem "core/hooks" -Recurse -Filter "*.py" -ErrorAction SilentlyContinue).Count
$testResults["hooks"] = @{
    "expected" = 28
    "found" = $hookCount
    "status" = if ($hookCount -ge 28) { "✅ PASS" } else { "❌ FAIL" }
}

# Test commands
Write-Host "Testing commands..." -ForegroundColor Blue
$commandCount = (Get-ChildItem "core/commands" -Filter "*.py" -ErrorAction SilentlyContinue).Count
$testResults["commands"] = @{
    "expected" = 18
    "found" = $commandCount
    "status" = if ($commandCount -ge 18) { "✅ PASS" } else { "❌ FAIL" }
}

# Test audio files
Write-Host "Testing audio system..." -ForegroundColor Blue
$audioCount = (Get-ChildItem "core/audio" -Recurse -Filter "*.wav" -ErrorAction SilentlyContinue).Count
$testResults["audio"] = @{
    "expected" = 102
    "found" = $audioCount
    "status" = if ($audioCount -ge 100) { "✅ PASS" } else { "❌ FAIL" }
}

# Test 2: Statusline Integration
Write-Host "`n🎨 Testing Statusline Integration..." -ForegroundColor Yellow

# Test Claude Powerline installation
Write-Host "Testing Claude Powerline (@Owloops)..." -ForegroundColor Blue
try {
    $powerlineTest = npm list -g @owloops/claude-powerline 2>$null
    $testResults["powerline"] = @{
        "component" = "@Owloops/claude-powerline"
        "status" = if ($powerlineTest) { "✅ INSTALLED" } else { "⚠️ NOT INSTALLED" }
    }
} catch {
    $testResults["powerline"] = @{
        "component" = "@Owloops/claude-powerline"
        "status" = "❌ ERROR"
    }
}

# Test statusline service
Write-Host "Testing statusline service..." -ForegroundColor Blue
$statuslineService = Test-Path "integrations/statusline/ultimate-statusline.ts"
$testResults["statusline_service"] = @{
    "component" = "Ultimate Statusline Service"
    "status" = if ($statuslineService) { "✅ READY" } else { "❌ MISSING" }
}

# Test 3: Web Application
Write-Host "`n🌐 Testing Web Application..." -ForegroundColor Yellow

# Test React PWA
Write-Host "Testing React PWA..." -ForegroundColor Blue
$webAppRunning = try {
    $response = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 3 -ErrorAction Stop
    $response.StatusCode -eq 200
} catch {
    $false
}

$testResults["react_pwa"] = @{
    "component" = "React PWA"
    "status" = if ($webAppRunning) { "✅ RUNNING" } else { "⚠️ NOT RUNNING" }
    "url" = "http://localhost:5173"
}

# Test 4: Mobile Application
Write-Host "`n📱 Testing Mobile Application..." -ForegroundColor Yellow

# Test mobile app structure
Write-Host "Testing mobile app (9cat)..." -ForegroundColor Blue
$mobileApp = Test-Path "apps/mobile/package.json"
$mobileComponents = Test-Path "apps/mobile/src/components/UltimateStatuslineView.tsx"
$testResults["mobile_app"] = @{
    "component" = "@9cat mobile app integration"
    "structure" = if ($mobileApp) { "✅ READY" } else { "❌ MISSING" }
    "statusline_component" = if ($mobileComponents) { "✅ INTEGRATED" } else { "❌ MISSING" }
}

# Test 5: Browser Integration
Write-Host "`n🌐 Testing Browser Integration..." -ForegroundColor Yellow

# Test Claude Code Browser integration
Write-Host "Testing Claude Code Browser (zainhoda)..." -ForegroundColor Blue
$browserIntegration = Test-Path "integrations/browser/statusline_bridge.py"
$browserClone = Test-Path "clones/claude-code-browser"
$testResults["browser_integration"] = @{
    "component" = "@zainhoda/claude-code-browser"
    "clone" = if ($browserClone) { "✅ CLONED" } else { "❌ MISSING" }
    "statusline_bridge" = if ($browserIntegration) { "✅ INTEGRATED" } else { "❌ MISSING" }
}

# Test 6: MCP Integration
Write-Host "`n🔌 Testing MCP Integration..." -ForegroundColor Yellow

# Test MCP Manager
Write-Host "Testing MCP Manager (qdhenry)..." -ForegroundColor Blue
$mcpManager = Test-Path "clones/mcp-manager"
$mcpWrapper = Test-Path "integrations/mcp-manager/mcp-wrapper.js"
$mcpOrchestrator = Test-Path "core/agents/mcp_orchestrator.py"
$testResults["mcp_integration"] = @{
    "component" = "@qdhenry/MCP-Manager"
    "clone" = if ($mcpManager) { "✅ CLONED" } else { "❌ MISSING" }
    "wrapper" = if ($mcpWrapper) { "✅ READY" } else { "❌ MISSING" }
    "orchestrator" = if ($mcpOrchestrator) { "✅ READY" } else { "❌ MISSING" }
}

# Test OpenAPI generators
Write-Host "Testing OpenAPI generators..." -ForegroundColor Blue
$pythonGenerator = Test-Path "clones/openapi-mcp-codegen"
$nodeGenerator = Test-Path "clones/openapi-mcp-generator"
$testResults["openapi_generators"] = @{
    "python_generator" = if ($pythonGenerator) { "✅ @cnoe-io READY" } else { "❌ MISSING" }
    "node_generator" = if ($nodeGenerator) { "✅ @harsha-iiiv READY" } else { "❌ MISSING" }
}

# Test 7: Installation Scripts
Write-Host "`n🚀 Testing Installation Scripts..." -ForegroundColor Yellow

$installScripts = @{
    "install-v3.ps1" = "scripts/install-v3.ps1"
    "setup-mcp-orchestration.ps1" = "scripts/setup-mcp-orchestration.ps1"
    "test-v3-system.ps1" = "scripts/test-v3-system.ps1"
}

foreach ($script in $installScripts.Keys) {
    $scriptExists = Test-Path $installScripts[$script]
    $testResults["script_$script"] = @{
        "component" = $script
        "status" = if ($scriptExists) { "✅ READY" } else { "❌ MISSING" }
    }
}

# Test 8: Attribution and Legal Compliance
Write-Host "`n📜 Testing Attribution and Legal Compliance..." -ForegroundColor Yellow

$attributionFiles = @{
    "CREDITS.md" = "CREDITS.md"
    "README.md" = "README.md"
    "LICENSE-THIRD-PARTY" = "LICENSE-THIRD-PARTY"
}

foreach ($file in $attributionFiles.Keys) {
    $fileExists = Test-Path $attributionFiles[$file]
    $testResults["attribution_$file"] = @{
        "component" = $file
        "status" = if ($fileExists) { "✅ PRESENT" } else { "❌ MISSING" }
    }
}

# Test 9: Performance and Resource Usage
Write-Host "`n⚡ Testing Performance and Resource Usage..." -ForegroundColor Yellow

# Check repository size
$repoSize = (Get-ChildItem -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB
$testResults["repo_size"] = @{
    "component" = "Repository Size"
    "size_mb" = [math]::Round($repoSize, 2)
    "status" = if ($repoSize -lt 200) { "✅ UNDER 200MB" } else { "⚠️ OVER 200MB" }
}

# Check node_modules size (exclude from repo)
$nodeModulesSize = 0
if (Test-Path "apps/web/node_modules") {
    $nodeModulesSize = (Get-ChildItem "apps/web/node_modules" -Recurse -File -ErrorAction SilentlyContinue | 
                       Measure-Object -Property Length -Sum).Sum / 1MB
}
$testResults["node_modules"] = @{
    "component" = "Node Modules (excluded)"
    "size_mb" = [math]::Round($nodeModulesSize, 2)
    "status" = "ℹ️ EXCLUDED FROM REPO"
}

# Generate Test Report
Write-Host "`n📊 Generating Test Report..." -ForegroundColor Yellow

$endTime = Get-Date
$testDuration = ($endTime - $startTime).TotalSeconds

$report = @"

╔════════════════════════════════════════════════════════════════╗
║                    TEST REPORT SUMMARY                         ║
╚════════════════════════════════════════════════════════════════╝

Test Duration: $([math]::Round($testDuration, 2)) seconds
Test Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

CORE COMPONENTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Agents:    $($testResults.agents.found)/$($testResults.agents.expected) $($testResults.agents.status)
• Hooks:     $($testResults.hooks.found)/$($testResults.hooks.expected) $($testResults.hooks.status)
• Commands:  $($testResults.commands.found)/$($testResults.commands.expected) $($testResults.commands.status)
• Audio:     $($testResults.audio.found)/$($testResults.audio.expected) $($testResults.audio.status)

STATUSLINE INTEGRATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Powerline: $($testResults.powerline.status) (@Owloops)
• Service:   $($testResults.statusline_service.status)

APPLICATIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• React PWA: $($testResults.react_pwa.status) ($($testResults.react_pwa.url))
• Mobile:    $($testResults.mobile_app.structure) $($testResults.mobile_app.statusline_component)

INTEGRATIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Browser:   $($testResults.browser_integration.clone) $($testResults.browser_integration.statusline_bridge) (@zainhoda)
• MCP:       $($testResults.mcp_integration.clone) $($testResults.mcp_integration.wrapper) (@qdhenry)
• OpenAPI:   $($testResults.openapi_generators.python_generator) $($testResults.openapi_generators.node_generator)

PERFORMANCE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Repo Size: $($testResults.repo_size.size_mb) MB $($testResults.repo_size.status)
• Node Deps: $($testResults.node_modules.size_mb) MB $($testResults.node_modules.status)

ATTRIBUTION COMPLIANCE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Credits:   $($testResults.attribution_"CREDITS.md".status)
• README:    $($testResults.attribution_"README.md".status)
• Licenses:  $($testResults.attribution_"LICENSE-THIRD-PARTY".status)

OVERALL STATUS: $(
    $passCount = ($testResults.Values | Where-Object { $_.status -like "*✅*" }).Count
    $totalTests = $testResults.Count
    if ($passCount -ge ($totalTests * 0.8)) { "🟢 EXCELLENT" }
    elseif ($passCount -ge ($totalTests * 0.6)) { "🟡 GOOD" }
    else { "🔴 NEEDS ATTENTION" }
)

Total Tests: $($testResults.Count)
Passed: $(($testResults.Values | Where-Object { $_.status -like "*✅*" }).Count)
Warnings: $(($testResults.Values | Where-Object { $_.status -like "*⚠️*" }).Count)
Failed: $(($testResults.Values | Where-Object { $_.status -like "*❌*" }).Count)

"@

Write-Host $report -ForegroundColor Green

# Save report to file
$report | Out-File "test-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').txt" -Encoding UTF8

Write-Host "`n💾 Test report saved to: test-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').txt" -ForegroundColor Blue

# Return summary for CI/CD
$overallStatus = if (($testResults.Values | Where-Object { $_.status -like "*✅*" }).Count -ge ($testResults.Count * 0.8)) {
    "SUCCESS"
} else {
    "ATTENTION_NEEDED"
}

Write-Host "`n🎯 Overall Test Status: $overallStatus" -ForegroundColor $(if ($overallStatus -eq "SUCCESS") { "Green" } else { "Yellow" })

if ($overallStatus -ne "SUCCESS") {
    Write-Host "`n⚠️ Review failed tests above and run:" -ForegroundColor Yellow
    Write-Host "   • .\scripts\install-v3.ps1 (for missing components)" -ForegroundColor Gray
    Write-Host "   • .\scripts\setup-mcp-orchestration.ps1 (for MCP issues)" -ForegroundColor Gray
}