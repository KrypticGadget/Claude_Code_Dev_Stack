#!/usr/bin/env powershell
#Requires -Version 5.1
<#
.SYNOPSIS
    Claude Code Dev Stack v3.0 Quick Start Demo
    
.DESCRIPTION
    Demonstrates the master launch system with guided examples
    Shows different launch modes and explains what each does
#>

# Color functions
function Write-ColorText {
    param([string]$Text, [ConsoleColor]$Color = "White")
    Write-Host $Text -ForegroundColor $Color
}

function Show-Banner {
    param([string]$Title)
    Write-Host ""
    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host $Title.PadLeft([math]::Floor((60 + $Title.Length) / 2)) -ForegroundColor Yellow
    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host ""
}

Show-Banner "CLAUDE CODE DEV STACK V3.0 QUICK START DEMO"

Write-ColorText "🚀 Welcome to the Claude Code Dev Stack v3.0 Master Launch System!" "Green"
Write-Host ""
Write-ColorText "This demo will show you how to use the master launch commands" "Cyan"
Write-ColorText "to start all Claude Code services with proper orchestration." "Cyan"
Write-Host ""

# Check if launch scripts exist
$psScript = "claude-start.ps1"
$bashScript = "claude-start.sh"

if (-not (Test-Path $psScript)) {
    Write-ColorText "❌ $psScript not found in current directory" "Red"
    exit 1
}

if (-not (Test-Path $bashScript)) {
    Write-ColorText "❌ $bashScript not found in current directory" "Red"
    exit 1
}

Write-ColorText "✅ Master launch scripts found!" "Green"
Write-Host ""

# Show available launch modes
Write-ColorText "📋 Available Launch Modes:" "Yellow"
Write-Host ""

$modes = @(
    @{Name="full"; Desc="Complete system: Dashboard + Web App + Mobile + Terminal"; Services="All services"},
    @{Name="core"; Desc="Essential services: Dashboard + MCP servers"; Services="Core only"},
    @{Name="web"; Desc="Web application: React PWA development server"; Services="Web app"},
    @{Name="mobile"; Desc="Mobile interface: Dashboard + QR codes + tunnels"; Services="Mobile"},
    @{Name="debug"; Desc="Debug mode: Core services + enhanced logging"; Services="Debug"}
)

foreach ($mode in $modes) {
    Write-ColorText "  📌 $($mode.Name):" "Cyan"
    Write-ColorText "     $($mode.Desc)" "White"
    Write-ColorText "     Services: $($mode.Services)" "Gray"
    Write-Host ""
}

# Interactive demo
Write-ColorText "🎯 Interactive Demo Options:" "Yellow"
Write-Host ""
Write-ColorText "1. Quick Test (Core services only)" "White"
Write-ColorText "2. Full System Launch" "White"
Write-ColorText "3. Web Development Mode" "White"
Write-ColorText "4. Mobile Access Setup" "White"
Write-ColorText "5. Debug Mode" "White"
Write-ColorText "6. Show Help" "White"
Write-ColorText "7. Exit" "White"
Write-Host ""

do {
    $choice = Read-Host "Enter your choice (1-7)"
    
    switch ($choice) {
        "1" {
            Write-ColorText "`n🔧 Starting Core Services Demo..." "Green"
            Write-ColorText "This will start:" "Cyan"
            Write-ColorText "  • Real-time dashboard (port 8080)" "White"
            Write-ColorText "  • MCP servers" "White"
            Write-ColorText "  • Health monitoring" "White"
            Write-Host ""
            
            $confirm = Read-Host "Continue? (y/N)"
            if ($confirm -eq "y" -or $confirm -eq "Y") {
                Write-ColorText "Launching core services..." "Yellow"
                & ".\$psScript" -Mode core -LogLevel info
            }
            break
        }
        
        "2" {
            Write-ColorText "`n🚀 Starting Full System Demo..." "Green"
            Write-ColorText "This will start ALL services:" "Cyan"
            Write-ColorText "  • Real-time dashboard (port 8080)" "White"
            Write-ColorText "  • Web application (port 3000)" "White"
            Write-ColorText "  • Mobile interface with QR codes" "White"
            Write-ColorText "  • Terminal server (port 7681)" "White"
            Write-ColorText "  • MCP servers" "White"
            Write-ColorText "  • Health monitoring" "White"
            Write-Host ""
            
            $confirm = Read-Host "Continue? (y/N)"
            if ($confirm -eq "y" -or $confirm -eq "Y") {
                Write-ColorText "Launching full system..." "Yellow"
                & ".\$psScript" -Mode full -AutoBrowser
            }
            break
        }
        
        "3" {
            Write-ColorText "`n🌐 Starting Web Development Mode..." "Green"
            Write-ColorText "This will start:" "Cyan"
            Write-ColorText "  • React PWA development server" "White"
            Write-ColorText "  • Vite build system with HMR" "White"
            Write-ColorText "  • Auto-browser opening" "White"
            Write-Host ""
            
            $confirm = Read-Host "Continue? (y/N)"
            if ($confirm -eq "y" -or $confirm -eq "Y") {
                Write-ColorText "Launching web development server..." "Yellow"
                & ".\$psScript" -Mode web -AutoBrowser -LogLevel debug
            }
            break
        }
        
        "4" {
            Write-ColorText "`n📱 Starting Mobile Access Setup..." "Green"
            Write-ColorText "This will start:" "Cyan"
            Write-ColorText "  • Mobile dashboard" "White"
            Write-ColorText "  • QR code generation" "White"
            Write-ColorText "  • Tunnel setup (requires ngrok token)" "White"
            Write-ColorText "  • Authentication system" "White"
            Write-Host ""
            
            $tunnelChoice = Read-Host "Enable tunnel for remote access? (y/N)"
            $localOnly = $tunnelChoice -ne "y" -and $tunnelChoice -ne "Y"
            
            $confirm = Read-Host "Continue? (y/N)"
            if ($confirm -eq "y" -or $confirm -eq "Y") {
                Write-ColorText "Launching mobile interface..." "Yellow"
                if ($localOnly) {
                    & ".\$psScript" -Mode mobile -LocalOnly
                } else {
                    & ".\$psScript" -Mode mobile
                }
            }
            break
        }
        
        "5" {
            Write-ColorText "`n🔍 Starting Debug Mode..." "Green"
            Write-ColorText "This will start:" "Cyan"
            Write-ColorText "  • Core services with debug logging" "White"
            Write-ColorText "  • Terminal tools" "White"
            Write-ColorText "  • Enhanced monitoring" "White"
            Write-ColorText "  • Detailed process information" "White"
            Write-Host ""
            
            $confirm = Read-Host "Continue? (y/N)"
            if ($confirm -eq "y" -or $confirm -eq "Y") {
                Write-ColorText "Launching debug mode..." "Yellow"
                & ".\$psScript" -Mode debug -LogLevel debug
            }
            break
        }
        
        "6" {
            Write-ColorText "`n📖 Command Reference:" "Green"
            Write-Host ""
            Write-ColorText "PowerShell Commands:" "Cyan"
            Write-ColorText "  .\claude-start.ps1                     # Full system" "White"
            Write-ColorText "  .\claude-start.ps1 -Mode core          # Core only" "White"
            Write-ColorText "  .\claude-start.ps1 -Mode web -AutoBrowser # Web + browser" "White"
            Write-ColorText "  .\claude-start.ps1 -Mode mobile -LocalOnly # Mobile local" "White"
            Write-ColorText "  .\claude-start.ps1 -Mode debug -LogLevel debug # Debug" "White"
            Write-Host ""
            Write-ColorText "Bash Commands (Linux/macOS):" "Cyan"
            Write-ColorText "  ./claude-start.sh                      # Full system" "White"
            Write-ColorText "  ./claude-start.sh --mode core          # Core only" "White"
            Write-ColorText "  ./claude-start.sh --mode web --auto-browser # Web + browser" "White"
            Write-ColorText "  ./claude-start.sh --mode mobile --local-only # Mobile local" "White"
            Write-ColorText "  ./claude-start.sh --mode debug --log-level debug # Debug" "White"
            Write-Host ""
            Write-ColorText "Options:" "Cyan"
            Write-ColorText "  -Mode / --mode          Launch mode (full|core|web|mobile|debug)" "White"
            Write-ColorText "  -SkipHealthCheck        Skip health checks" "White"
            Write-ColorText "  -LogLevel / --log-level Logging level (debug|info|warn|error)" "White"
            Write-ColorText "  -AutoBrowser / --auto-browser  Open browser automatically" "White"
            Write-ColorText "  -CustomPort / --port    Custom port for dashboard" "White"
            Write-ColorText "  -LocalOnly / --local-only  No tunnels, local access only" "White"
            Write-Host ""
            continue
        }
        
        "7" {
            Write-ColorText "`n👋 Thanks for trying Claude Code Dev Stack v3.0!" "Green"
            Write-Host ""
            Write-ColorText "📚 Additional Resources:" "Cyan"
            Write-ColorText "  • LAUNCH_SYSTEM_README.md - Complete documentation" "White"
            Write-ColorText "  • CLAUDE_CODE_V3_MASTER_PLAN.md - Architecture overview" "White"
            Write-ColorText "  • .claude-example/mobile/README.md - Mobile setup guide" "White"
            Write-Host ""
            Write-ColorText "🚀 To start the full system anytime:" "Yellow"
            Write-ColorText "  .\claude-start.ps1" "White"
            Write-Host ""
            exit 0
        }
        
        default {
            Write-ColorText "❌ Invalid choice. Please enter 1-7." "Red"
            continue
        }
    }
    
    Write-Host ""
    Write-ColorText "🔄 Demo completed! Press Enter to return to menu..." "Green"
    Read-Host
    
} while ($true)