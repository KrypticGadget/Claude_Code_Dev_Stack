# Claude Code Dev Stack - GLOBAL Master Installer (Windows PowerShell)
# ONE-TIME GLOBAL installation at Claude Code ROOT directory
# After installation, ALL components work in ANY project directory
# Features: progress tracking, error handling, health checks, rollback, retry logic

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Script configuration
$SCRIPT_VERSION = "2.1.0"
$GITHUB_BASE = "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main"
$INSTALL_DIR = "$env:USERPROFILE\.claude-code"  # GLOBAL Claude Code ROOT directory
$LOG_DIR = "$INSTALL_DIR\.claude\logs"
$BACKUP_DIR = "$INSTALL_DIR\.claude\backups"
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"
$LOG_FILE = "$LOG_DIR\install_$TIMESTAMP.log"

# Component installers
$COMPONENTS = @(
    @{
        Name = "agents"
        Installer = "install-agents.ps1"
        Description = "28 AI agents with @agent- routing"
        HealthCheck = { Test-Path "$INSTALL_DIR\agents\master-orchestrator-agent.md" }
    },
    @{
        Name = "commands"
        Installer = "install-commands.ps1"
        Description = "18 slash commands"
        HealthCheck = { Test-Path "$INSTALL_DIR\commands\new-project.md" }
    },
    @{
        Name = "mcps"
        Installer = "install-mcps.ps1"
        Description = "Tier 1 MCP configurations"
        HealthCheck = { Test-Path "$INSTALL_DIR\mcp-configs\tier1-universal.json" }
    },
    @{
        Name = "hooks"
        Installer = "install-hooks.ps1"
        Description = "Hooks execution system"
        HealthCheck = { Test-Path "$INSTALL_DIR\.claude\hooks\session_loader.py" }
    }
)

# Initialize logging
function Initialize-Logging {
    New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null
    
    # Start transcript
    Start-Transcript -Path $LOG_FILE -Force
    
    Write-Log "Claude Code Dev Stack GLOBAL Master Installer v$SCRIPT_VERSION" "INFO"
    Write-Log "ONE-TIME GLOBAL installation started at $(Get-Date)" "INFO"
    Write-Log "GLOBAL install directory (Claude Code ROOT): $INSTALL_DIR" "INFO"
    Write-Log "After installation, ALL features work in ANY project directory!" "SUCCESS"
}

# Logging function
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    # Color output based on level
    switch ($Level) {
        "ERROR" { Write-Host $logEntry -ForegroundColor Red }
        "WARNING" { Write-Host $logEntry -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $logEntry -ForegroundColor Green }
        "INFO" { Write-Host $logEntry -ForegroundColor Cyan }
        default { Write-Host $logEntry }
    }
    
    # Also write to log file
    Add-Content -Path $LOG_FILE -Value $logEntry -ErrorAction SilentlyContinue
}

# Check for updates
function Check-Updates {
    Write-Log "Checking for updates..." "INFO"
    
    try {
        $versionUrl = "$GITHUB_BASE/VERSION"
        $latestVersion = (Invoke-WebRequest -Uri $versionUrl -UseBasicParsing).Content.Trim()
        
        if ($latestVersion -ne $SCRIPT_VERSION) {
            Write-Log "New version available: $latestVersion (current: $SCRIPT_VERSION)" "WARNING"
            Write-Log "Visit: https://github.com/KrypticGadget/Claude_Code_Dev_Stack" "INFO"
        } else {
            Write-Log "You have the latest version" "SUCCESS"
        }
    } catch {
        Write-Log "Failed to check for updates: $_" "WARNING"
    }
}

# Create backup
function Create-Backup {
    if (Test-Path $INSTALL_DIR) {
        Write-Log "Creating backup of existing installation..." "INFO"
        
        New-Item -ItemType Directory -Force -Path $BACKUP_DIR | Out-Null
        $backupPath = "$BACKUP_DIR\backup_$TIMESTAMP.zip"
        
        try {
            # Create zip backup (excluding logs and backups)
            Add-Type -AssemblyName System.IO.Compression.FileSystem
            [System.IO.Compression.ZipFile]::CreateFromDirectory($INSTALL_DIR, $backupPath)
            
            Write-Log "Backup created: $backupPath" "SUCCESS"
            return $backupPath
        } catch {
            Write-Log "Failed to create backup: $_" "WARNING"
            return $null
        }
    }
    return $null
}

# Restore from backup
function Restore-Backup {
    param([string]$BackupPath)
    
    if ($BackupPath -and (Test-Path $BackupPath)) {
        Write-Log "Restoring from backup: $BackupPath" "INFO"
        
        try {
            # Remove current installation
            Remove-Item -Path $INSTALL_DIR -Recurse -Force -ErrorAction SilentlyContinue
            
            # Extract backup
            Add-Type -AssemblyName System.IO.Compression.FileSystem
            [System.IO.Compression.ZipFile]::ExtractToDirectory($BackupPath, $INSTALL_DIR)
            
            Write-Log "Restore completed successfully" "SUCCESS"
            return $true
        } catch {
            Write-Log "Failed to restore backup: $_" "ERROR"
            return $false
        }
    }
    return $false
}

# Download with retry logic
function Download-WithRetry {
    param(
        [string]$Url,
        [string]$Description,
        [int]$MaxRetries = 3
    )
    
    for ($i = 1; $i -le $MaxRetries; $i++) {
        try {
            Write-Log "Downloading $Description (attempt $i/$MaxRetries)..." "INFO"
            $content = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 30
            return $content.Content
        } catch {
            if ($i -eq $MaxRetries) {
                Write-Log "Failed to download $Description after $MaxRetries attempts: $_" "ERROR"
                throw
            }
            Write-Log "Download failed, retrying in 2 seconds..." "WARNING"
            Start-Sleep -Seconds 2
        }
    }
}

# Execute component installer
function Install-Component {
    param(
        [hashtable]$Component,
        [int]$Index,
        [int]$Total
    )
    
    $componentName = $Component.Name
    $progress = "$Index/$Total"
    
    Write-Host ""
    Write-Log "[$progress] Installing $componentName - $($Component.Description)" "INFO"
    Write-Progress -Activity "Installing Claude Code Dev Stack" -Status "Installing $componentName" -PercentComplete (($Index / $Total) * 100)
    
    # Skip if already installed and healthy
    if (& $Component.HealthCheck) {
        $response = Read-Host "Component '$componentName' appears to be already installed. Skip? (Y/n)"
        if ($response -ne 'n') {
            Write-Log "Skipping $componentName (already installed)" "INFO"
            return @{ Success = $true; Skipped = $true }
        }
    }
    
    try {
        # Download installer script
        $installerContent = Download-WithRetry -Url "$GITHUB_BASE/$($Component.Installer)" -Description "$componentName installer"
        
        # Save to temp file
        $tempInstaller = "$env:TEMP\$($Component.Installer)"
        Set-Content -Path $tempInstaller -Value $installerContent -Encoding UTF8
        
        # Execute installer
        Write-Log "Executing $componentName installer..." "INFO"
        & powershell -ExecutionPolicy Bypass -File $tempInstaller
        
        # Verify installation with health check
        Start-Sleep -Seconds 2
        if (& $Component.HealthCheck) {
            Write-Log "$componentName installed successfully" "SUCCESS"
            Write-Log "GLOBALLY installed at: $INSTALL_DIR\$componentName" "INFO"
            return @{ Success = $true; Skipped = $false }
        } else {
            Write-Log "$componentName health check failed" "ERROR"
            return @{ Success = $false; Skipped = $false }
        }
        
    } catch {
        Write-Log "Failed to install $componentName`: $_" "ERROR"
        return @{ Success = $false; Skipped = $false; Error = $_.Exception.Message }
    } finally {
        # Clean up temp file
        if (Test-Path $tempInstaller -ErrorAction SilentlyContinue) {
            Remove-Item $tempInstaller -Force -ErrorAction SilentlyContinue
        }
    }
}

# Main installation process
function Start-Installation {
    $results = @()
    $backupPath = $null
    
    try {
        # Initialize
        Initialize-Logging
        Write-Host ""
        Write-Host "🚀 Claude Code Dev Stack - GLOBAL Master Installer v$SCRIPT_VERSION" -ForegroundColor Cyan
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
        Write-Host ""
        Write-Host "🌍 ONE-TIME GLOBAL INSTALLATION" -ForegroundColor Yellow
        Write-Host "   Installing to Claude Code ROOT: $INSTALL_DIR" -ForegroundColor White
        Write-Host "   After installation, ALL components work in ANY project!" -ForegroundColor Green
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
        
        # Check for updates
        Check-Updates
        
        # Create backup
        $backupPath = Create-Backup
        
        # Install components
        Write-Host ""
        Write-Log "Installing $($COMPONENTS.Count) components..." "INFO"
        
        for ($i = 0; $i -lt $COMPONENTS.Count; $i++) {
            $result = Install-Component -Component $COMPONENTS[$i] -Index ($i + 1) -Total $COMPONENTS.Count
            $result.Component = $COMPONENTS[$i].Name
            $results += $result
        }
        
        # Summary
        Write-Host ""
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
        Write-Log "Installation Summary:" "INFO"
        
        $successCount = ($results | Where-Object { $_.Success }).Count
        $failedCount = ($results | Where-Object { -not $_.Success }).Count
        $skippedCount = ($results | Where-Object { $_.Skipped }).Count
        
        foreach ($result in $results) {
            if ($result.Success) {
                if ($result.Skipped) {
                    Write-Host "  ⏭️  $($result.Component): Skipped (already installed)" -ForegroundColor Yellow
                } else {
                    Write-Host "  ✅ $($result.Component): Success" -ForegroundColor Green
                }
            } else {
                Write-Host "  ❌ $($result.Component): Failed" -ForegroundColor Red
                if ($result.Error) {
                    Write-Host "     Error: $($result.Error)" -ForegroundColor DarkRed
                }
            }
        }
        
        Write-Host ""
        Write-Log "Total: $successCount successful, $failedCount failed, $skippedCount skipped" "INFO"
        
        # Handle failures
        if ($failedCount -gt 0) {
            Write-Log "Some components failed to install" "WARNING"
            
            if ($backupPath) {
                $response = Read-Host "Would you like to rollback to the previous installation? (y/N)"
                if ($response -eq 'y') {
                    if (Restore-Backup -BackupPath $backupPath) {
                        Write-Log "Rollback completed successfully" "SUCCESS"
                    } else {
                        Write-Log "Rollback failed" "ERROR"
                    }
                }
            }
        } else {
            Write-Log "All components installed successfully!" "SUCCESS"
            
            # Run verification script
            Write-Host ""
            Write-Log "Running installation verification..." "INFO"
            try {
                $verifyScript = "$INSTALL_DIR\verification\verify-installation.ps1"
                if (Test-Path $verifyScript) {
                    & powershell -ExecutionPolicy Bypass -File $verifyScript
                } else {
                    # Download and run verification script
                    $verifyContent = Download-WithRetry -Url "$GITHUB_BASE/verification/verify-installation.ps1" -Description "verification script"
                    $tempVerify = "$env:TEMP\verify-installation.ps1"
                    Set-Content -Path $tempVerify -Value $verifyContent -Encoding UTF8
                    & powershell -ExecutionPolicy Bypass -File $tempVerify
                    Remove-Item $tempVerify -Force -ErrorAction SilentlyContinue
                }
            } catch {
                Write-Log "Verification script not available" "WARNING"
            }
            
            # Show global directory structure
            Write-Host ""
            Write-Host "📁 GLOBAL Installation Directory Structure:" -ForegroundColor Cyan
            Write-Host "   $INSTALL_DIR\" -ForegroundColor White
            Write-Host "   ├── agents\           # 28 AI agents (@agent- commands)" -ForegroundColor Gray
            Write-Host "   ├── commands\         # 18 slash commands" -ForegroundColor Gray
            Write-Host "   ├── mcp-configs\      # MCP configurations" -ForegroundColor Gray
            Write-Host "   └── .claude\          # Hooks and settings" -ForegroundColor Gray
            Write-Host "       └── hooks\        # Execution hooks" -ForegroundColor Gray
            
            # Post-installation steps
            Write-Host ""
            Write-Host "✅ GLOBAL INSTALLATION COMPLETE!" -ForegroundColor Green
            Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
            Write-Host ""
            Write-Host "🎯 Next Steps:" -ForegroundColor Yellow
            Write-Host "1. Install MCPs manually:" -ForegroundColor White
            Write-Host "   claude mcp add playwright npx @playwright/mcp@latest" -ForegroundColor Gray
            Write-Host "   claude mcp add obsidian" -ForegroundColor Gray
            Write-Host "   claude mcp add brave-search" -ForegroundColor Gray
            Write-Host ""
            Write-Host "2. Restart Claude Code to activate all features" -ForegroundColor White
            Write-Host ""
            Write-Host "3. Test from ANY directory:" -ForegroundColor White
            Write-Host "   cd C:\MyProject" -ForegroundColor Gray
            Write-Host "   # Then use any command:" -ForegroundColor DarkGray
            Write-Host "   @agent-master-orchestrator[opus] plan a new project" -ForegroundColor Gray
            Write-Host "   /new-project MyApp" -ForegroundColor Gray
            Write-Host ""
            Write-Host "🌍 All components are GLOBALLY available - work from ANY project!" -ForegroundColor Green
            Write-Host ""
        }
        
    } catch {
        Write-Log "Installation failed with critical error: $_" "ERROR"
        
        # Attempt rollback on critical failure
        if ($backupPath -and (Test-Path $backupPath)) {
            Write-Log "Attempting automatic rollback..." "WARNING"
            Restore-Backup -BackupPath $backupPath
        }
    } finally {
        # Clean up old backups (keep last 5)
        if (Test-Path $BACKUP_DIR) {
            $backups = Get-ChildItem $BACKUP_DIR -Filter "backup_*.zip" | Sort-Object CreationTime -Descending
            if ($backups.Count -gt 5) {
                $backups | Select-Object -Skip 5 | Remove-Item -Force
                Write-Log "Cleaned up old backups" "INFO"
            }
        }
        
        # Stop transcript
        Stop-Transcript
        
        Write-Host ""
        Write-Log "Installation log saved to: $LOG_FILE" "INFO"
        Write-Host "Press any key to exit..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
}

# Run installation
Start-Installation