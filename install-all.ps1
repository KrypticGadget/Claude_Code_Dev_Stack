# Claude Code Dev Stack v2.1 - Complete Installation Script
# This script installs the 28 AI agents, hooks system, and v2.1 features

Write-Host "🚀 Claude Code Dev Stack v2.1 - Complete Installation" -ForegroundColor Cyan
Write-Host "Installing 28 AI agents with @agent- routing, hooks, and MCP support..." -ForegroundColor Yellow

# Set installation directory
$CLAUDE_DIR = "$env:USERPROFILE\.claude-code"
$AGENTS_DIR = "$CLAUDE_DIR\agents"
$COMMANDS_DIR = "$CLAUDE_DIR\commands"
$HOOKS_DIR = "$CLAUDE_DIR\.claude\hooks"
$CONFIG_DIR = "$CLAUDE_DIR\.claude\config"
$STATE_DIR = "$CLAUDE_DIR\.claude\state"
$MCP_DIR = "$CLAUDE_DIR\mcp-configs"

# GitHub repository URL
$REPO_URL = "https://github.com/KrypticGadget/Claude_Code_Dev_Stack"
$RAW_URL = "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main"

try {
    # Create all directories
    Write-Host "`n📁 Creating v2.1 directory structure..." -ForegroundColor Green
    $directories = @(
        $CLAUDE_DIR, $AGENTS_DIR, $COMMANDS_DIR, $HOOKS_DIR, 
        $CONFIG_DIR, $STATE_DIR, $MCP_DIR
    )
    foreach ($dir in $directories) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }

    # Download agent configurations with @agent- support
    Write-Host "`n📥 Downloading 28 agent configurations with v2.1 features..." -ForegroundColor Green
    
    $agentFiles = @(
        "master-orchestrator-agent.md",
        "usage-guide-agent.md",
        "api-integration-specialist-agent.md",
        "backend-services-agent.md",
        "business-analyst-agent.md",
        "business-tech-alignment-agent.md",
        "ceo-strategy-agent.md",
        "database-architecture-agent.md",
        "development-prompt-agent.md",
        "devops-engineering-agent.md",
        "financial-analyst-agent.md",
        "frontend-architecture-agent.md",
        "frontend-mockup-agent.md",
        "integration-setup-agent.md",
        "middleware-specialist-agent.md",
        "performance-optimization-agent.md",
        "production-frontend-agent.md",
        "project-manager-agent.md",
        "prompt-engineer-agent.md",
        "quality-assurance-agent.md",
        "script-automation-agent.md",
        "security-architecture-agent.md",
        "technical-cto-agent.md",
        "technical-documentation-agent.md",
        "technical-specifications-agent.md",
        "testing-automation-agent.md"
    )
    
    $totalFiles = $agentFiles.Count
    $currentFile = 0
    
    foreach ($file in $agentFiles) {
        $currentFile++
        $progress = [math]::Round(($currentFile / $totalFiles) * 100)
        Write-Progress -Activity "Downloading agents" -Status "$file" -PercentComplete $progress
        
        $url = "$RAW_URL/Config_Files/$file"
        $destination = Join-Path $AGENTS_DIR $file
        
        try {
            Invoke-WebRequest -Uri $url -OutFile $destination -UseBasicParsing -ErrorAction Stop
        } catch {
            Write-Host "⚠️  Failed to download $file - $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
    
    Write-Progress -Activity "Downloading agents" -Completed

    # Download and install hooks
    Write-Host "`n🔧 Installing v2.1 Hooks System..." -ForegroundColor Green
    
    $hookFiles = @{
        "session_loader.py" = "$HOOKS_DIR\session_loader.py"
        "session_saver.py" = "$HOOKS_DIR\session_saver.py"
        "quality_gate.py" = "$HOOKS_DIR\quality_gate.py"
        "planning_trigger.py" = "$HOOKS_DIR\planning_trigger.py"
        "agent_orchestrator.py" = "$HOOKS_DIR\agent_orchestrator.py"
        "agent_mention_parser.py" = "$HOOKS_DIR\agent_mention_parser.py"
        "model_tracker.py" = "$HOOKS_DIR\model_tracker.py"
        "mcp_gateway.py" = "$HOOKS_DIR\mcp_gateway.py"
    }
    
    foreach ($file in $hookFiles.GetEnumerator()) {
        $url = "$RAW_URL/.claude/hooks/$($file.Key)"
        Write-Host "  Downloading $($file.Key)..." -ForegroundColor Yellow
        try {
            Invoke-WebRequest -Uri $url -OutFile $file.Value -UseBasicParsing -ErrorAction Stop
            Write-Host "  ✓ Installed $($file.Key)" -ForegroundColor Green
        } catch {
            Write-Host "  ⚠️  Failed to download $($file.Key)" -ForegroundColor Yellow
        }
    }

    # Download configuration files
    Write-Host "`n⚙️  Installing v2.1 configuration files..." -ForegroundColor Green
    
    $configFiles = @{
        "coding_standards.json" = "$CONFIG_DIR\coding_standards.json"
        "agent_models.json" = "$CONFIG_DIR\agent_models.json"
        "settings.json" = "$CLAUDE_DIR\.claude\settings.json"
    }
    
    foreach ($file in $configFiles.GetEnumerator()) {
        $url = "$RAW_URL/.claude/config/$($file.Key)"
        try {
            Invoke-WebRequest -Uri $url -OutFile $file.Value -UseBasicParsing -ErrorAction Stop
            Write-Host "  ✓ Installed $($file.Key)" -ForegroundColor Green
        } catch {
            Write-Host "  ⚠️  Failed to download $($file.Key)" -ForegroundColor Yellow
        }
    }

    # Download MCP configurations
    Write-Host "`n🌐 Installing MCP configuration files..." -ForegroundColor Green
    
    $mcpFiles = @{
        "tier1-universal.json" = "$MCP_DIR\tier1-universal.json"
        "active-mcps.json" = "$MCP_DIR\active-mcps.json"
        "agent-bindings.json" = "$MCP_DIR\agent-bindings.json"
    }
    
    foreach ($file in $mcpFiles.GetEnumerator()) {
        $url = "$RAW_URL/mcp-configs/$($file.Key)"
        try {
            Invoke-WebRequest -Uri $url -OutFile $file.Value -UseBasicParsing -ErrorAction Stop
            Write-Host "  ✓ Installed $($file.Key)" -ForegroundColor Green
        } catch {
            Write-Host "  ⚠️  Failed to download $($file.Key)" -ForegroundColor Yellow
        }
    }

    # Download slash commands
    Write-Host "`n📋 Installing 18 slash commands..." -ForegroundColor Green
    
    $slashCommands = @(
        "new-project.md", "resume-project.md", "business-analysis.md",
        "technical-feasibility.md", "project-plan.md", "frontend-mockup.md",
        "backend-service.md", "database-design.md", "api-integration.md",
        "middleware-setup.md", "production-frontend.md", "documentation.md",
        "financial-model.md", "go-to-market.md", "requirements.md",
        "site-architecture.md", "tech-alignment.md", "prompt-enhance.md"
    )
    
    foreach ($cmd in $slashCommands) {
        $url = "$RAW_URL/slash-commands/commands/$cmd"
        $destination = Join-Path $COMMANDS_DIR $cmd
        try {
            Invoke-WebRequest -Uri $url -OutFile $destination -UseBasicParsing -ErrorAction SilentlyContinue
        } catch {
            # Silently continue if file doesn't exist
        }
    }

    # Download master documentation
    Write-Host "`n📚 Downloading v2.1 documentation..." -ForegroundColor Green
    
    $docs = @{
        "MASTER_PROMPTING_GUIDE.md" = "$CLAUDE_DIR\MASTER_PROMPTING_GUIDE.md"
        "HOOKS_IMPLEMENTATION.md" = "$CLAUDE_DIR\HOOKS_IMPLEMENTATION.md"
        "MCP_INTEGRATION_GUIDE.md" = "$CLAUDE_DIR\MCP_INTEGRATION_GUIDE.md"
    }
    
    foreach ($doc in $docs.GetEnumerator()) {
        $url = "$RAW_URL/docs/$($doc.Key)"
        try {
            Invoke-WebRequest -Uri $url -OutFile $doc.Value -UseBasicParsing -ErrorAction SilentlyContinue
            Write-Host "  ✓ Downloaded $($doc.Key)" -ForegroundColor Green
        } catch {
            # Create if doesn't exist
        }
    }

    # Create v2.1 quick reference
    Write-Host "`n📋 Creating v2.1 Quick Reference..." -ForegroundColor Green
    $quickRef = @"
🚀 Claude Code Dev Stack v2.1 - Quick Reference

📁 Installation Locations:
- Agents: $AGENTS_DIR
- Commands: $COMMANDS_DIR
- Hooks: $HOOKS_DIR
- MCP Configs: $MCP_DIR

✨ New v2.1 Features:
- @agent- deterministic routing (e.g., @agent-backend-services)
- Model selection: [opus] for complex, [haiku] for simple
- Automatic microcompact for extended sessions
- PDF reading capability
- Hooks execution layer
- MCP integration (Playwright, Obsidian, Brave Search)

🎯 Quick Start:
1. Use @agent- mentions: @agent-system-architect[opus] design a system
2. Cost optimization: @agent-testing-automation[haiku] for simple tests
3. Install MCPs: claude mcp add playwright npx @playwright/mcp@latest
4. PDF analysis: "Read requirements from spec.pdf"

📋 Available Agents (28 total):
- Orchestration: @agent-master-orchestrator[opus], @agent-usage-guide[opus]
- Business: @agent-business-analyst[opus], @agent-ceo-strategy[opus]
- Architecture: @agent-system-architect[opus], @agent-database-architecture[opus]
- Development: @agent-backend-services, @agent-frontend-architecture
- Testing: @agent-testing-automation[haiku], @agent-quality-assurance[haiku]
- Documentation: @agent-technical-documentation[haiku]

💰 Cost Optimization:
- Use [opus] only for complex reasoning (20% of tasks)
- Use [haiku] for routine tasks (30% of tasks)
- Default model for standard development (50% of tasks)
- Result: 40-60% cost reduction

🔧 Hooks Active:
- Session continuity (automatic state restoration)
- Quality gates (code standards enforcement)
- Planning triggers (requirements change detection)
- Agent routing (@agent- mention parsing)
- Model tracking (cost optimization monitoring)

📚 Documentation:
- Master Guide: $CLAUDE_DIR\MASTER_PROMPTING_GUIDE.md
- Hooks Guide: $CLAUDE_DIR\HOOKS_IMPLEMENTATION.md
- MCP Guide: $CLAUDE_DIR\MCP_INTEGRATION_GUIDE.md
- Repository: https://github.com/KrypticGadget/Claude_Code_Dev_Stack
"@
    
    $quickRef | Out-File -FilePath "$CLAUDE_DIR\QUICK_REFERENCE_V2.1.txt" -Encoding UTF8

    # Create example usage file
    $examples = @"
# Claude Code Dev Stack v2.1 - Example Usage

## Basic @agent- Routing
@agent-backend-services create a REST API for user management
@agent-frontend-architecture[opus] design a complex dashboard
@agent-testing-automation[haiku] write unit tests

## Project Initialization with Model Optimization
/new-project "E-commerce Platform" @agent-master-orchestrator[opus] @agent-business-analyst[opus]

## Cost-Optimized Workflow
# Complex planning (Opus)
@agent-system-architect[opus] @agent-database-architecture[opus] design the system

# Implementation (Default)
@agent-backend-services @agent-frontend-architecture implement features

# Testing & Docs (Haiku)
@agent-testing-automation[haiku] @agent-technical-documentation[haiku] finish up

## PDF Integration
@agent-business-analyst[opus] analyze requirements from business-plan.pdf
@agent-technical-specifications review the API spec in api-docs.pdf

## MCP Usage
"Run browser tests with Playwright for the checkout flow"
"Document architectural decisions in Obsidian"
"Research competitor features using Brave Search"

## Extended Sessions
# Work all day without context issues - microcompact handles it automatically
# Hooks preserve your state between sessions
"@

    $examples | Out-File -FilePath "$CLAUDE_DIR\EXAMPLES_V2.1.md" -Encoding UTF8

    Write-Host "`n✅ Claude Code Dev Stack v2.1 installation complete!" -ForegroundColor Green
    Write-Host "`n📍 Installed to: $CLAUDE_DIR" -ForegroundColor Cyan
    Write-Host "📄 Quick reference: $CLAUDE_DIR\QUICK_REFERENCE_V2.1.txt" -ForegroundColor Cyan
    Write-Host "📘 Examples: $CLAUDE_DIR\EXAMPLES_V2.1.md" -ForegroundColor Cyan
    
    Write-Host "`n🎯 Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Install Tier 1 MCPs:" -ForegroundColor White
    Write-Host "   claude mcp add playwright npx @playwright/mcp@latest" -ForegroundColor Gray
    Write-Host "   claude mcp add obsidian" -ForegroundColor Gray
    Write-Host "   claude mcp add brave-search" -ForegroundColor Gray
    Write-Host "2. Copy .claude\settings.json to your Claude Code settings" -ForegroundColor White
    Write-Host "3. Restart Claude Code to activate v2.1 features" -ForegroundColor White
    Write-Host "4. Try: @agent-master-orchestrator[opus] plan a new project" -ForegroundColor White
    
} catch {
    Write-Host "`n❌ Installation failed: $_" -ForegroundColor Red
    Write-Host "Error details: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please check your internet connection and try again." -ForegroundColor Yellow
}

Write-Host "`n🎉 Ready to use Claude Code Dev Stack v2.1!" -ForegroundColor Green
Write-Host "Try: @agent-backend-services create a user authentication API" -ForegroundColor White