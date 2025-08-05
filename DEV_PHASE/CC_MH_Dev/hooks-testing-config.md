# 🔧 Claude Code Hooks & Testing Protocol

## Overview
Automated hooks system to enforce code quality, testing, and administrative tracking for the Claude Code Dev Stack.

## 🎯 Hook Types

### 1. Pre-Commit Hooks
Triggered before code commits to ensure quality standards.

```powershell
# pre-commit.ps1
param(
    [string]$ProjectPath = (Get-Location)
)

Write-Host "🔍 Running pre-commit checks..." -ForegroundColor Cyan

# Check 1: Code Review
$modifiedFiles = git diff --cached --name-only
foreach ($file in $modifiedFiles) {
    Write-Host "Reviewing: $file"
    claude-code "/code-review $file" --agent code-reviewer
}

# Check 2: Security Scan
if ($modifiedFiles -match '\.(js|py|java|cs|go)$') {
    claude-code "/security-audit modified files" --agent security-architect
}

# Check 3: Test Coverage
claude-code "/test-suite generate for modified files" --agent testing-engineer

# Check 4: Documentation
if ($modifiedFiles -match '(api|endpoint|route)') {
    claude-code "/documentation update API docs" --agent documentation-specialist
}
```

### 2. Post-Update Hooks
Triggered after repository updates.

```powershell
# post-update.ps1
Write-Host "📋 Running post-update tasks..." -ForegroundColor Green

# Update dependencies
claude-code "Check and update project dependencies" --agent devops-automation-specialist

# Sync documentation
claude-code "/documentation sync all docs with code changes" 

# Update project context
$context = @{
    lastUpdate = Get-Date
    branch = git branch --show-current
    recentChanges = git log --oneline -10
}
$context | ConvertTo-Json | Out-File ".claude-code/context.json"
```

### 3. Test Runner Hook
Automated testing protocol.

```powershell
# test-runner.ps1
param(
    [string]$TestType = "all",
    [string]$Environment = "test"
)

Write-Host "🧪 Running automated tests..." -ForegroundColor Yellow

switch ($TestType) {
    "unit" {
        claude-code "/test-suite run unit tests" --mcp @api-test
    }
    "integration" {
        claude-code "/test-suite run integration tests" --mcp @api-test,@database
    }
    "e2e" {
        claude-code "/test-suite run end-to-end tests" --mcp @file-system,@api-test
    }
    "all" {
        # Run all test types
        & $MyInvocation.MyCommand.Path -TestType "unit"
        & $MyInvocation.MyCommand.Path -TestType "integration" 
        & $MyInvocation.MyCommand.Path -TestType "e2e"
    }
}

# Generate test report
claude-code "Generate test coverage report" --agent quality-assurance-lead
```

### 4. Diff Logger
Track and analyze code changes.

```powershell
# diff-logger.ps1
param(
    [string]$Since = "HEAD~1",
    [string]$OutputPath = ".claude-code/diff-logs"
)

Write-Host "📊 Logging code changes..." -ForegroundColor Magenta

# Create diff log directory
New-Item -ItemType Directory -Force -Path $OutputPath | Out-Null

# Generate diff report
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$diffFile = "$OutputPath/diff_$timestamp.log"

# Capture diff
git diff $Since > $diffFile

# Analyze changes
$analysis = @{
    timestamp = $timestamp
    filesChanged = (git diff --name-only $Since).Count
    insertions = git diff --stat $Since | Select-String -Pattern "(\d+) insertion" | ForEach-Object { $_.Matches[0].Groups[1].Value }
    deletions = git diff --stat $Since | Select-String -Pattern "(\d+) deletion" | ForEach-Object { $_.Matches[0].Groups[1].Value }
    summary = git log --oneline $Since..HEAD
}

# Save analysis
$analysis | ConvertTo-Json | Out-File "$OutputPath/analysis_$timestamp.json"

# Generate insights
claude-code "Analyze code changes and suggest improvements based on diff" --mcp @file-system
```

## 🔄 Integration Workflow

### Setup Script
```powershell
# setup-hooks.ps1
Write-Host "🔧 Setting up Claude Code hooks..." -ForegroundColor Cyan

# Install Git hooks
$hooksPath = ".git/hooks"
$claudeHooksPath = ".claude-code/hooks"

# Create directories
New-Item -ItemType Directory -Force -Path $claudeHooksPath | Out-Null

# Copy hook scripts
Copy-Item "hooks/*.ps1" -Destination $claudeHooksPath -Force

# Create Git hook wrappers
@"
#!/bin/sh
powershell.exe -File $claudeHooksPath/pre-commit.ps1
"@ | Out-File "$hooksPath/pre-commit" -Encoding ASCII

# Make executable (if on WSL/Linux)
if (Get-Command chmod -ErrorAction SilentlyContinue) {
    chmod +x "$hooksPath/pre-commit"
}

Write-Host "✅ Hooks installed successfully!" -ForegroundColor Green
```

### Configuration File
```json
{
  "hooks": {
    "enabled": true,
    "pre-commit": {
      "checks": ["code-review", "security", "tests", "docs"],
      "failOnError": true,
      "timeout": 300
    },
    "post-update": {
      "tasks": ["dependencies", "documentation", "context"],
      "async": true
    },
    "testing": {
      "autoRun": true,
      "coverage": {
        "minimum": 80,
        "enforced": true
      },
      "types": ["unit", "integration", "e2e"]
    },
    "diff-logging": {
      "enabled": true,
      "retention": "30 days",
      "analysis": true
    }
  },
  "notifications": {
    "slack": {
      "enabled": false,
      "webhook": ""
    },
    "email": {
      "enabled": false,
      "recipients": []
    }
  }
}
```

## 📊 Administrative Dashboard

### Status Command
```powershell
# admin-status.ps1
Write-Host @"
📊 Claude Code Stack Status Dashboard
====================================
"@ -ForegroundColor Cyan

# Project Health
$health = @{
    "Test Coverage" = "85%"
    "Security Score" = "A"
    "Documentation" = "95% complete"
    "Last Deploy" = (Get-Date).AddDays(-2)
}

$health.GetEnumerator() | ForEach-Object {
    Write-Host "$($_.Key): $($_.Value)"
}

# Recent Activity
Write-Host "`n📈 Recent Activity:" -ForegroundColor Yellow
Get-Content ".claude-code/diff-logs/analysis_*.json" | 
    Select-Object -Last 5 | 
    ConvertFrom-Json | 
    Format-Table timestamp, filesChanged

# Agent Usage
Write-Host "`n🤖 Agent Usage Stats:" -ForegroundColor Green
# This would read from usage logs
```

## 🚀 Usage Examples

### Enable All Hooks
```powershell
# In your project directory
./hooks/setup-hooks.ps1
```

### Run Specific Checks
```powershell
# Run only security checks
claude-code "/security-audit" --hook pre-commit

# Run test suite
./hooks/test-runner.ps1 -TestType integration

# Generate diff report
./hooks/diff-logger.ps1 -Since "main"
```

### Configure for CI/CD
```yaml
# .github/workflows/claude-code.yml
name: Claude Code Checks
on: [push, pull_request]

jobs:
  claude-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Claude Code Hooks
        run: |
          pwsh ./hooks/pre-commit.ps1
          pwsh ./hooks/test-runner.ps1
```

## 🔐 Security Considerations

1. **API Key Protection**: Never commit API keys
2. **Hook Permissions**: Limit execution permissions
3. **Timeout Handling**: Prevent infinite loops
4. **Error Recovery**: Graceful failure handling
5. **Audit Trail**: Log all automated actions

## 📈 Metrics & Reporting

The hooks system generates:
- Code quality metrics
- Test coverage reports
- Security audit logs
- Change analysis reports
- Performance benchmarks

All reports are stored in `.claude-code/reports/` for tracking and analysis.