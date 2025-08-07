# Claude Code Hook Manager - Control which hooks are active
# Usage: .\manage_hooks.ps1 -Action [status|minimal|disable-all|enable-all]

param(
    [string]$Action = "status"
)

Write-Host ""
Write-Host "Claude Code Hook Manager" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host ""

$hooksDir = "$env:USERPROFILE\.claude\hooks"

# Essential hooks that provide core functionality
$essentialHooks = @(
    "audio_player.py",        # Audio notifications
    "audio_notifier.py",      # Audio notifications
    "agent_mention_parser.py", # Agent routing
    "slash_command_router.py", # Slash commands
    "planning_trigger.py"      # Todo management
)

# Problematic hooks that can cause bloat
$problematicHooks = @(
    "session_saver.py",       # Can cause .claude.json bloat if not minimal
    "session_loader.py",      # Can load too much context
    "model_tracker.py"        # Can accumulate too much data
)

# Optional hooks
$optionalHooks = @(
    "pre_project.py",
    "post_project.py",
    "pre_command.py",
    "post_command.py",
    "quality_gate.py",
    "mcp_gateway.py",
    "mcp_gateway_enhanced.py",
    "mcp_initializer.py",
    "agent_orchestrator.py",
    "agent_orchestrator_integrated.py"
)

switch ($Action) {
    "status" {
        Write-Host "Hook Status Report:" -ForegroundColor Yellow
        Write-Host ""
        
        # Check active hooks
        $activeHooks = Get-ChildItem $hooksDir -Filter "*.py" -ErrorAction SilentlyContinue
        $disabledHooks = Get-ChildItem $hooksDir -Filter "*.DISABLED" -ErrorAction SilentlyContinue
        
        Write-Host "Active Hooks ($($activeHooks.Count)):" -ForegroundColor Green
        foreach ($hook in $activeHooks) {
            $category = "Optional"
            if ($hook.Name -in $essentialHooks) {
                $category = "Essential"
                Write-Host "  ✓ $($hook.Name) [$category]" -ForegroundColor Green
            } elseif ($hook.Name -in $problematicHooks) {
                $category = "Problematic"
                Write-Host "  ⚠ $($hook.Name) [$category]" -ForegroundColor Yellow
            } else {
                Write-Host "  • $($hook.Name) [$category]" -ForegroundColor Gray
            }
        }
        
        if ($disabledHooks.Count -gt 0) {
            Write-Host ""
            Write-Host "Disabled Hooks ($($disabledHooks.Count)):" -ForegroundColor Red
            foreach ($hook in $disabledHooks) {
                Write-Host "  ✗ $($hook.Name)" -ForegroundColor Red
            }
        }
        
        # Check .claude.json size
        Write-Host ""
        $jsonPath = "$env:USERPROFILE\.claude.json"
        if (Test-Path $jsonPath) {
            $jsonSize = (Get-Item $jsonPath).Length / 1MB
            if ($jsonSize -gt 10) {
                Write-Host "WARNING: .claude.json is $([Math]::Round($jsonSize, 2))MB!" -ForegroundColor Red
                Write-Host "  Run: .\manage_hooks.ps1 -Action minimal" -ForegroundColor Yellow
            } else {
                Write-Host ".claude.json size: $([Math]::Round($jsonSize, 2))MB" -ForegroundColor Green
            }
        }
    }
    
    "minimal" {
        Write-Host "Switching to MINIMAL mode..." -ForegroundColor Yellow
        Write-Host "  Keeping only essential hooks for stability" -ForegroundColor Gray
        Write-Host ""
        
        $disabled = 0
        Get-ChildItem $hooksDir -Filter "*.py" -ErrorAction SilentlyContinue | 
            Where-Object { $_.Name -notin $essentialHooks } |
            ForEach-Object { 
                $newName = "$($_.FullName).DISABLED"
                Rename-Item $_.FullName $newName -Force
                Write-Host "  Disabled: $($_.Name)" -ForegroundColor Red
                $disabled++
            }
        
        Write-Host ""
        Write-Host "✓ Disabled $disabled non-essential hooks" -ForegroundColor Green
        Write-Host "  Your Claude Code should run much faster now!" -ForegroundColor Cyan
    }
    
    "disable-all" {
        Write-Host "Disabling ALL hooks..." -ForegroundColor Red
        
        $disabled = 0
        Get-ChildItem $hooksDir -Filter "*.py" -ErrorAction SilentlyContinue |
            ForEach-Object {
                $newName = "$($_.FullName).DISABLED"
                Rename-Item $_.FullName $newName -Force
                Write-Host "  Disabled: $($_.Name)" -ForegroundColor Red
                $disabled++
            }
        
        Write-Host ""
        Write-Host "✓ Disabled $disabled hooks" -ForegroundColor Green
        Write-Host "  Claude Code running without any hooks" -ForegroundColor Yellow
    }
    
    "enable-all" {
        Write-Host "Re-enabling ALL hooks..." -ForegroundColor Green
        Write-Host "  WARNING: This may cause performance issues!" -ForegroundColor Yellow
        Write-Host ""
        
        $enabled = 0
        Get-ChildItem $hooksDir -Filter "*.DISABLED" -ErrorAction SilentlyContinue |
            ForEach-Object {
                $newName = $_.FullName.Replace('.DISABLED', '')
                Rename-Item $_.FullName $newName -Force
                Write-Host "  Enabled: $($_.Name.Replace('.DISABLED',''))" -ForegroundColor Green
                $enabled++
            }
        
        Write-Host ""
        Write-Host "✓ Enabled $enabled hooks" -ForegroundColor Green
    }
    
    default {
        Write-Host "Usage: .\manage_hooks.ps1 -Action [status|minimal|disable-all|enable-all]" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Actions:" -ForegroundColor Cyan
        Write-Host "  status      - Show current hook status" -ForegroundColor White
        Write-Host "  minimal     - Keep only essential hooks (RECOMMENDED)" -ForegroundColor White
        Write-Host "  disable-all - Disable all hooks" -ForegroundColor White
        Write-Host "  enable-all  - Enable all hooks (may cause slowdown)" -ForegroundColor White
    }
}

Write-Host ""