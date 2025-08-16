# MCP Configuration Manager - Advanced configuration management system
# Enhanced PowerShell configuration management for MCP Manager
# 
# Original concept by @qdhenry (MIT License)
# Enhanced for Claude Code Dev Stack by DevOps Agent

#Requires -Version 5.1

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("Create", "Validate", "Backup", "Restore", "Merge", "Export", "Import", "Template", "Encrypt", "Decrypt", "Update", "Compare", "Status")]
    [string]$Action = "Status",
    
    [string]$ConfigPath = "",
    [string]$TemplateName = "default",
    [string]$BackupPath = "",
    [string]$SourceConfig = "",
    [string]$TargetConfig = "",
    [string]$OutputFormat = "yaml",
    [string]$Environment = "development",
    [switch]$Force,
    [switch]$Interactive,
    [switch]$Secure,
    [switch]$Verbose,
    [hashtable]$Properties = @{}
)

# Module configuration
$ScriptRoot = Split-Path -Parent $PSScriptRoot
$IntegrationRoot = Split-Path -Parent $ScriptRoot
$DefaultConfigPath = Join-Path $IntegrationRoot "config\mcp-services.yml"
$TemplatesDir = Join-Path $IntegrationRoot "config\templates"
$BackupDir = Join-Path $IntegrationRoot "backups\config"
$SecretsDir = Join-Path $IntegrationRoot "config\secrets"
$LogPath = Join-Path $IntegrationRoot "logs\config-manager.log"

# Use provided paths or defaults
$ConfigPath = if ($ConfigPath) { $ConfigPath } else { $DefaultConfigPath }
$BackupPath = if ($BackupPath) { $BackupPath } else { $BackupDir }

# Ensure required directories exist
$RequiredDirs = @($TemplatesDir, $BackupDir, $SecretsDir, (Split-Path $LogPath -Parent))
foreach ($dir in $RequiredDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# Configuration templates
$script:ConfigTemplates = @{
    default = @{
        Name = "Default MCP Configuration"
        Description = "Standard configuration for MCP services"
        Services = @(
            @{
                id = "playwright-mcp-8080"
                name = "Playwright MCP Service"
                type = "playwright"
                host = "localhost"
                port = 8080
                auto_start = $true
                restart_policy = "always"
            },
            @{
                id = "github-mcp-8081"
                name = "GitHub MCP Service"
                type = "github"
                host = "localhost"
                port = 8081
                auto_start = $true
                restart_policy = "always"
            },
            @{
                id = "websearch-mcp-8082"
                name = "WebSearch MCP Service"
                type = "websearch"
                host = "localhost"
                port = 8082
                auto_start = $true
                restart_policy = "always"
            }
        )
        Settings = @{
            health_check_interval = 30
            service_discovery_interval = 300
            max_retry_attempts = 3
        }
    }
    
    production = @{
        Name = "Production MCP Configuration"
        Description = "Production-ready configuration with monitoring and security"
        Services = @(
            @{
                id = "playwright-mcp-8080"
                name = "Playwright MCP Service"
                type = "playwright"
                host = "localhost"
                port = 8080
                auto_start = $true
                restart_policy = "always"
                resource_limits = @{
                    memory = "512MB"
                    cpu = "0.5"
                }
            },
            @{
                id = "github-mcp-8081"
                name = "GitHub MCP Service"
                type = "github"
                host = "localhost"
                port = 8081
                auto_start = $true
                restart_policy = "always"
                resource_limits = @{
                    memory = "256MB"
                    cpu = "0.3"
                }
            }
        )
        Settings = @{
            health_check_interval = 15
            service_discovery_interval = 180
            max_retry_attempts = 5
            security = @{
                enable_authentication = $true
                api_key_required = $true
                rate_limiting = @{
                    requests_per_minute = 500
                }
            }
            monitoring = @{
                enable_prometheus = $true
                prometheus_port = 9090
                metrics_interval = 15
            }
        }
    }
    
    development = @{
        Name = "Development MCP Configuration"
        Description = "Development configuration with debugging and testing features"
        Services = @(
            @{
                id = "playwright-mcp-8080"
                name = "Playwright MCP Service"
                type = "playwright"
                host = "localhost"
                port = 8080
                auto_start = $false
                restart_policy = "on-failure"
                debug_mode = $true
            }
        )
        Settings = @{
            health_check_interval = 60
            max_retry_attempts = 1
            development = @{
                debug_mode = $true
                test_mode = $true
                mock_services = $false
                log_level = "DEBUG"
            }
        }
    }
    
    minimal = @{
        Name = "Minimal MCP Configuration"
        Description = "Minimal configuration for testing and development"
        Services = @(
            @{
                id = "core-mcp-8080"
                name = "Core MCP Service"
                type = "core"
                host = "localhost"
                port = 8080
                auto_start = $true
                restart_policy = "always"
            }
        )
        Settings = @{
            health_check_interval = 30
            max_retry_attempts = 3
        }
    }
}

# Logging functions
function Write-ConfigLog {
    param(
        [string]$Message,
        [ValidateSet("INFO", "WARN", "ERROR", "DEBUG", "SUCCESS")]
        [string]$Level = "INFO"
    )
    
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [CONFIG] [$Level] $Message"
    
    # Write to console with appropriate color
    $Color = switch ($Level) {
        "INFO" { "White" }
        "WARN" { "Yellow" }
        "ERROR" { "Red" }
        "DEBUG" { "Gray" }
        "SUCCESS" { "Green" }
    }
    
    if ($Verbose -or $Level -ne "DEBUG") {
        Write-Host $LogEntry -ForegroundColor $Color
    }
    
    # Write to log file
    try {
        Add-Content -Path $LogPath -Value $LogEntry -ErrorAction SilentlyContinue
    }
    catch {
        # Ignore log file errors
    }
}

# Configuration validation
function Test-ConfigurationValidity {
    param([hashtable]$Config)
    
    $ValidationResults = @{
        IsValid = $true
        Errors = @()
        Warnings = @()
        Info = @()
    }
    
    try {
        Write-ConfigLog "Validating configuration structure..." -Level "DEBUG"
        
        # Check required top-level sections
        $RequiredSections = @("services")
        foreach ($Section in $RequiredSections) {
            if (-not $Config.ContainsKey($Section)) {
                $ValidationResults.Errors += "Missing required section: $Section"
                $ValidationResults.IsValid = $false
            }
        }
        
        # Validate services section
        if ($Config.ContainsKey("services") -and $Config.services) {
            $ServiceIds = @()
            $ServicePorts = @()
            
            foreach ($Service in $Config.services) {
                # Check required service properties
                $RequiredServiceProps = @("id", "name", "type", "port")
                foreach ($Prop in $RequiredServiceProps) {
                    if (-not $Service.ContainsKey($Prop) -or -not $Service[$Prop]) {
                        $ValidationResults.Errors += "Service missing required property: $Prop"
                        $ValidationResults.IsValid = $false
                    }
                }
                
                # Check for duplicate service IDs
                if ($Service.id -and $ServiceIds -contains $Service.id) {
                    $ValidationResults.Errors += "Duplicate service ID: $($Service.id)"
                    $ValidationResults.IsValid = $false
                }
                else {
                    $ServiceIds += $Service.id
                }
                
                # Check for port conflicts
                if ($Service.port) {
                    if ($ServicePorts -contains $Service.port) {
                        $ValidationResults.Errors += "Port conflict: $($Service.port) used by multiple services"
                        $ValidationResults.IsValid = $false
                    }
                    else {
                        $ServicePorts += $Service.port
                    }
                    
                    # Validate port range
                    if ($Service.port -lt 1024 -or $Service.port -gt 65535) {
                        $ValidationResults.Warnings += "Service $($Service.name) uses non-standard port: $($Service.port)"
                    }
                }
                
                # Validate service type
                $ValidServiceTypes = @("core", "playwright", "github", "websearch", "custom", "proxy", "gateway")
                if ($Service.type -and $ValidServiceTypes -notcontains $Service.type) {
                    $ValidationResults.Warnings += "Unknown service type: $($Service.type)"
                }
                
                # Check host validity
                if ($Service.host -and $Service.host -ne "localhost" -and $Service.host -notmatch "^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$") {
                    # Basic hostname validation
                    if ($Service.host -notmatch "^[a-zA-Z0-9\-\.]+$") {
                        $ValidationResults.Warnings += "Service $($Service.name) has potentially invalid hostname: $($Service.host)"
                    }
                }
                
                # Validate restart policy
                if ($Service.restart_policy) {
                    $ValidRestartPolicies = @("always", "on-failure", "never")
                    if ($ValidRestartPolicies -notcontains $Service.restart_policy) {
                        $ValidationResults.Warnings += "Service $($Service.name) has invalid restart policy: $($Service.restart_policy)"
                    }
                }
            }
            
            $ValidationResults.Info += "Validated $($Config.services.Count) services"
        }
        else {
            $ValidationResults.Warnings += "No services defined in configuration"
        }
        
        # Validate settings section
        if ($Config.ContainsKey("settings")) {
            $Settings = $Config.settings
            
            # Validate numeric settings
            $NumericSettings = @{
                "health_check_interval" = @{ Min = 5; Max = 3600 }
                "service_discovery_interval" = @{ Min = 60; Max = 86400 }
                "max_retry_attempts" = @{ Min = 1; Max = 10 }
            }
            
            foreach ($Setting in $NumericSettings.Keys) {
                if ($Settings.ContainsKey($Setting)) {
                    $Value = $Settings[$Setting]
                    $Range = $NumericSettings[$Setting]
                    
                    if ($Value -lt $Range.Min -or $Value -gt $Range.Max) {
                        $ValidationResults.Warnings += "Setting $Setting value $Value is outside recommended range ($($Range.Min)-$($Range.Max))"
                    }
                }
            }
        }
        
        # Summary
        $ErrorCount = $ValidationResults.Errors.Count
        $WarningCount = $ValidationResults.Warnings.Count
        
        if ($ErrorCount -eq 0 -and $WarningCount -eq 0) {
            $ValidationResults.Info += "Configuration validation passed with no issues"
        }
        elseif ($ErrorCount -eq 0) {
            $ValidationResults.Info += "Configuration validation passed with $WarningCount warnings"
        }
        else {
            $ValidationResults.Info += "Configuration validation failed with $ErrorCount errors and $WarningCount warnings"
        }
        
        Write-ConfigLog "Configuration validation completed" -Level "DEBUG"
        
    }
    catch {
        $ValidationResults.Errors += "Validation error: $($_.Exception.Message)"
        $ValidationResults.IsValid = $false
        Write-ConfigLog "Configuration validation error: $($_.Exception.Message)" -Level "ERROR"
    }
    
    return $ValidationResults
}

# Configuration creation and management
function New-ConfigurationFromTemplate {
    param(
        [string]$TemplateName,
        [string]$OutputPath,
        [hashtable]$CustomProperties = @{}
    )
    
    Write-ConfigLog "Creating configuration from template: $TemplateName" -Level "INFO"
    
    try {
        if (-not $script:ConfigTemplates.ContainsKey($TemplateName)) {
            Write-ConfigLog "Template '$TemplateName' not found" -Level "ERROR"
            return $false
        }
        
        $Template = $script:ConfigTemplates[$TemplateName]
        
        # Build configuration from template
        $Config = @{
            "# MCP Manager Configuration" = ""
            "# Generated from template: $($Template.Name)" = ""
            "# Description: $($Template.Description)" = ""
            "# Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" = ""
            "" = ""
        }
        
        # Add settings
        if ($Template.Settings) {
            foreach ($Key in $Template.Settings.Keys) {
                $Config[$Key] = $Template.Settings[$Key]
            }
        }
        
        # Add services
        $Config["services"] = $Template.Services
        
        # Apply custom properties
        foreach ($Property in $CustomProperties.Keys) {
            $Config[$Property] = $CustomProperties[$Property]
        }
        
        # Apply environment-specific overrides
        if ($Environment -and $Environment -ne "development") {
            Write-ConfigLog "Applying environment-specific settings for: $Environment" -Level "DEBUG"
            
            switch ($Environment) {
                "production" {
                    $Config["health_check_interval"] = 15
                    $Config["max_retry_attempts"] = 5
                    if (-not $Config.ContainsKey("security")) {
                        $Config["security"] = @{}
                    }
                    $Config["security"]["enable_authentication"] = $true
                }
                "staging" {
                    $Config["health_check_interval"] = 20
                    $Config["max_retry_attempts"] = 3
                }
                "testing" {
                    $Config["health_check_interval"] = 60
                    $Config["max_retry_attempts"] = 1
                    if (-not $Config.ContainsKey("development")) {
                        $Config["development"] = @{}
                    }
                    $Config["development"]["test_mode"] = $true
                }
            }
        }
        
        # Convert to YAML
        $YamlContent = ConvertTo-Yaml -InputObject $Config
        
        # Write to file
        $OutputDir = Split-Path $OutputPath -Parent
        if (-not (Test-Path $OutputDir)) {
            New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
        }
        
        $YamlContent | Out-File -FilePath $OutputPath -Encoding UTF8 -Force
        
        Write-ConfigLog "Configuration created successfully: $OutputPath" -Level "SUCCESS"
        return $true
        
    }
    catch {
        Write-ConfigLog "Failed to create configuration: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function ConvertTo-Yaml {
    param([hashtable]$InputObject, [int]$IndentLevel = 0)
    
    $Indent = "  " * $IndentLevel
    $Yaml = ""
    
    foreach ($Key in $InputObject.Keys) {
        $Value = $InputObject[$Key]
        
        if ($Key.StartsWith("#") -or $Key -eq "") {
            # Comment or empty line
            if ($Key -eq "") {
                $Yaml += "`n"
            }
            else {
                $Yaml += "$Key`n"
            }
            continue
        }
        
        if ($Value -is [hashtable]) {
            $Yaml += "$Indent${Key}:`n"
            $Yaml += ConvertTo-Yaml -InputObject $Value -IndentLevel ($IndentLevel + 1)
        }
        elseif ($Value -is [array]) {
            $Yaml += "$Indent${Key}:`n"
            foreach ($Item in $Value) {
                if ($Item -is [hashtable]) {
                    $Yaml += "$Indent  -`n"
                    foreach ($SubKey in $Item.Keys) {
                        $SubValue = $Item[$SubKey]
                        if ($SubValue -is [hashtable]) {
                            $Yaml += "$Indent    ${SubKey}:`n"
                            foreach ($SubSubKey in $SubValue.Keys) {
                                $Yaml += "$Indent      ${SubSubKey}: $($SubValue[$SubSubKey])`n"
                            }
                        }
                        else {
                            $ValueStr = if ($SubValue -is [string]) { "`"$SubValue`"" } else { $SubValue.ToString().ToLower() }
                            $Yaml += "$Indent    ${SubKey}: $ValueStr`n"
                        }
                    }
                }
                else {
                    $ValueStr = if ($Item -is [string]) { "`"$Item`"" } else { $Item.ToString().ToLower() }
                    $Yaml += "$Indent  - $ValueStr`n"
                }
            }
        }
        elseif ($Value -is [boolean]) {
            $Yaml += "$Indent${Key}: $($Value.ToString().ToLower())`n"
        }
        elseif ($Value -is [string]) {
            $Yaml += "$Indent${Key}: `"$Value`"`n"
        }
        else {
            $Yaml += "$Indent${Key}: $Value`n"
        }
    }
    
    return $Yaml
}

function Backup-Configuration {
    param(
        [string]$SourcePath,
        [string]$BackupLocation = $BackupPath
    )
    
    Write-ConfigLog "Creating configuration backup..." -Level "INFO"
    
    try {
        if (-not (Test-Path $SourcePath)) {
            Write-ConfigLog "Source configuration not found: $SourcePath" -Level "ERROR"
            return $false
        }
        
        $BackupTimestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $BackupFileName = "mcp-config-backup-$BackupTimestamp.yml"
        $BackupFullPath = Join-Path $BackupLocation $BackupFileName
        
        # Create backup directory
        if (-not (Test-Path $BackupLocation)) {
            New-Item -ItemType Directory -Path $BackupLocation -Force | Out-Null
        }
        
        # Copy configuration file
        Copy-Item -Path $SourcePath -Destination $BackupFullPath -Force
        
        # Create backup metadata
        $BackupInfo = @{
            BackupDate = Get-Date
            SourcePath = $SourcePath
            BackupPath = $BackupFullPath
            FileSize = (Get-Item $SourcePath).Length
            MD5Hash = (Get-FileHash $SourcePath -Algorithm MD5).Hash
        }
        
        $MetadataPath = Join-Path $BackupLocation "backup-metadata-$BackupTimestamp.json"
        $BackupInfo | ConvertTo-Json -Depth 5 | Out-File -FilePath $MetadataPath -Encoding UTF8
        
        Write-ConfigLog "Configuration backup created: $BackupFullPath" -Level "SUCCESS"
        return $BackupFullPath
        
    }
    catch {
        Write-ConfigLog "Failed to create backup: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Restore-Configuration {
    param(
        [string]$BackupPath,
        [string]$TargetPath
    )
    
    Write-ConfigLog "Restoring configuration from backup..." -Level "INFO"
    
    try {
        if (-not (Test-Path $BackupPath)) {
            Write-ConfigLog "Backup file not found: $BackupPath" -Level "ERROR"
            return $false
        }
        
        # Create backup of current config before restore
        if (Test-Path $TargetPath) {
            $PreRestoreBackup = Backup-Configuration -SourcePath $TargetPath
            Write-ConfigLog "Created pre-restore backup: $PreRestoreBackup" -Level "INFO"
        }
        
        # Restore configuration
        Copy-Item -Path $BackupPath -Destination $TargetPath -Force
        
        # Validate restored configuration
        $RestoredConfig = Import-Configuration -ConfigPath $TargetPath
        if ($RestoredConfig) {
            $ValidationResult = Test-ConfigurationValidity -Config $RestoredConfig
            
            if ($ValidationResult.IsValid) {
                Write-ConfigLog "Configuration restored and validated successfully" -Level "SUCCESS"
                return $true
            }
            else {
                Write-ConfigLog "Restored configuration failed validation" -Level "ERROR"
                foreach ($Error in $ValidationResult.Errors) {
                    Write-ConfigLog "  Validation error: $Error" -Level "ERROR"
                }
                return $false
            }
        }
        else {
            Write-ConfigLog "Failed to import restored configuration" -Level "ERROR"
            return $false
        }
        
    }
    catch {
        Write-ConfigLog "Failed to restore configuration: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Import-Configuration {
    param([string]$ConfigPath)
    
    try {
        if (-not (Test-Path $ConfigPath)) {
            Write-ConfigLog "Configuration file not found: $ConfigPath" -Level "ERROR"
            return $null
        }
        
        $ConfigContent = Get-Content $ConfigPath -Raw
        
        # Simple YAML to hashtable conversion
        $Config = @{}
        $CurrentSection = $null
        $InServicesList = $false
        $CurrentService = $null
        $Services = @()
        
        $Lines = $ConfigContent -split "`n"
        foreach ($Line in $Lines) {
            $Line = $Line.Trim()
            
            # Skip comments and empty lines
            if ($Line.StartsWith("#") -or -not $Line) {
                continue
            }
            
            if ($Line -eq "services:") {
                $InServicesList = $true
                continue
            }
            elseif ($Line.StartsWith("- ") -and $InServicesList) {
                # New service in list
                if ($CurrentService) {
                    $Services += $CurrentService
                }
                $CurrentService = @{}
            }
            elseif ($Line.Contains(":") -and -not $Line.StartsWith("  ")) {
                # Top-level setting
                $InServicesList = $false
                if ($CurrentService -and $Services) {
                    $Services += $CurrentService
                    $Config["services"] = $Services
                    $CurrentService = $null
                }
                
                $Parts = $Line -split ":", 2
                $Key = $Parts[0].Trim()
                $Value = $Parts[1].Trim().Trim('"').Trim("'")
                
                # Convert value types
                if ($Value -eq "true" -or $Value -eq "false") {
                    $Value = [bool]::Parse($Value)
                }
                elseif ($Value -match "^\d+$") {
                    $Value = [int]$Value
                }
                
                $Config[$Key] = $Value
            }
            elseif ($InServicesList -and $CurrentService -ne $null -and $Line.Contains(":")) {
                # Service property
                $Parts = $Line -split ":", 2
                $Key = $Parts[0].Trim()
                $Value = $Parts[1].Trim().Trim('"').Trim("'")
                
                # Convert value types
                if ($Value -eq "true" -or $Value -eq "false") {
                    $Value = [bool]::Parse($Value)
                }
                elseif ($Value -match "^\d+$") {
                    $Value = [int]$Value
                }
                
                $CurrentService[$Key] = $Value
            }
        }
        
        # Add last service if exists
        if ($CurrentService) {
            $Services += $CurrentService
            $Config["services"] = $Services
        }
        
        return $Config
        
    }
    catch {
        Write-ConfigLog "Failed to import configuration: $($_.Exception.Message)" -Level "ERROR"
        return $null
    }
}

function Compare-Configurations {
    param(
        [string]$SourcePath,
        [string]$TargetPath
    )
    
    Write-ConfigLog "Comparing configurations..." -Level "INFO"
    
    try {
        $SourceConfig = Import-Configuration -ConfigPath $SourcePath
        $TargetConfig = Import-Configuration -ConfigPath $TargetPath
        
        if (-not $SourceConfig -or -not $TargetConfig) {
            Write-ConfigLog "Failed to load one or both configurations for comparison" -Level "ERROR"
            return $false
        }
        
        $Differences = @{
            Added = @()
            Removed = @()
            Modified = @()
            Summary = ""
        }
        
        # Compare services
        $SourceServices = if ($SourceConfig.services) { $SourceConfig.services } else { @() }
        $TargetServices = if ($TargetConfig.services) { $TargetConfig.services } else { @() }
        
        $SourceServiceIds = $SourceServices | ForEach-Object { $_.id }
        $TargetServiceIds = $TargetServices | ForEach-Object { $_.id }
        
        # Find added services
        foreach ($ServiceId in $TargetServiceIds) {
            if ($SourceServiceIds -notcontains $ServiceId) {
                $Service = $TargetServices | Where-Object { $_.id -eq $ServiceId }
                $Differences.Added += "Service: $($Service.name) ($ServiceId)"
            }
        }
        
        # Find removed services
        foreach ($ServiceId in $SourceServiceIds) {
            if ($TargetServiceIds -notcontains $ServiceId) {
                $Service = $SourceServices | Where-Object { $_.id -eq $ServiceId }
                $Differences.Removed += "Service: $($Service.name) ($ServiceId)"
            }
        }
        
        # Find modified services
        foreach ($ServiceId in $SourceServiceIds) {
            if ($TargetServiceIds -contains $ServiceId) {
                $SourceService = $SourceServices | Where-Object { $_.id -eq $ServiceId }
                $TargetService = $TargetServices | Where-Object { $_.id -eq $ServiceId }
                
                foreach ($Property in $SourceService.Keys) {
                    if ($TargetService.ContainsKey($Property)) {
                        if ($SourceService[$Property] -ne $TargetService[$Property]) {
                            $Differences.Modified += "Service $ServiceId.$Property`: $($SourceService[$Property]) -> $($TargetService[$Property])"
                        }
                    }
                    else {
                        $Differences.Removed += "Service $ServiceId.$Property`: $($SourceService[$Property])"
                    }
                }
                
                foreach ($Property in $TargetService.Keys) {
                    if (-not $SourceService.ContainsKey($Property)) {
                        $Differences.Added += "Service $ServiceId.$Property`: $($TargetService[$Property])"
                    }
                }
            }
        }
        
        # Compare settings
        $AllKeys = @()
        $AllKeys += $SourceConfig.Keys | Where-Object { $_ -ne "services" }
        $AllKeys += $TargetConfig.Keys | Where-Object { $_ -ne "services" }
        $AllKeys = $AllKeys | Select-Object -Unique
        
        foreach ($Key in $AllKeys) {
            if ($SourceConfig.ContainsKey($Key) -and $TargetConfig.ContainsKey($Key)) {
                if ($SourceConfig[$Key] -ne $TargetConfig[$Key]) {
                    $Differences.Modified += "Setting $Key`: $($SourceConfig[$Key]) -> $($TargetConfig[$Key])"
                }
            }
            elseif ($TargetConfig.ContainsKey($Key)) {
                $Differences.Added += "Setting $Key`: $($TargetConfig[$Key])"
            }
            else {
                $Differences.Removed += "Setting $Key`: $($SourceConfig[$Key])"
            }
        }
        
        # Generate summary
        $AddedCount = $Differences.Added.Count
        $RemovedCount = $Differences.Removed.Count
        $ModifiedCount = $Differences.Modified.Count
        
        $Differences.Summary = "Added: $AddedCount, Removed: $RemovedCount, Modified: $ModifiedCount"
        
        # Display results
        Write-Host ""
        Write-Host "Configuration Comparison Results" -ForegroundColor Cyan
        Write-Host "=" * 50 -ForegroundColor Cyan
        Write-Host "Source: $SourcePath" -ForegroundColor Gray
        Write-Host "Target: $TargetPath" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Summary: $($Differences.Summary)" -ForegroundColor Yellow
        Write-Host ""
        
        if ($Differences.Added.Count -gt 0) {
            Write-Host "Added ($($Differences.Added.Count)):" -ForegroundColor Green
            foreach ($Item in $Differences.Added) {
                Write-Host "  + $Item" -ForegroundColor Green
            }
            Write-Host ""
        }
        
        if ($Differences.Removed.Count -gt 0) {
            Write-Host "Removed ($($Differences.Removed.Count)):" -ForegroundColor Red
            foreach ($Item in $Differences.Removed) {
                Write-Host "  - $Item" -ForegroundColor Red
            }
            Write-Host ""
        }
        
        if ($Differences.Modified.Count -gt 0) {
            Write-Host "Modified ($($Differences.Modified.Count)):" -ForegroundColor Yellow
            foreach ($Item in $Differences.Modified) {
                Write-Host "  ~ $Item" -ForegroundColor Yellow
            }
            Write-Host ""
        }
        
        if ($AddedCount -eq 0 -and $RemovedCount -eq 0 -and $ModifiedCount -eq 0) {
            Write-Host "No differences found" -ForegroundColor Green
        }
        
        return $Differences
        
    }
    catch {
        Write-ConfigLog "Failed to compare configurations: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Show-ConfigurationStatus {
    param([string]$ConfigPath)
    
    Write-Host ""
    Write-Host "MCP Configuration Manager Status" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Configuration File: $ConfigPath" -ForegroundColor Yellow
    
    if (Test-Path $ConfigPath) {
        Write-Host "Status: Found" -ForegroundColor Green
        
        $FileInfo = Get-Item $ConfigPath
        Write-Host "Size: $($FileInfo.Length) bytes" -ForegroundColor White
        Write-Host "Modified: $($FileInfo.LastWriteTime)" -ForegroundColor White
        
        # Import and validate configuration
        $Config = Import-Configuration -ConfigPath $ConfigPath
        if ($Config) {
            Write-Host ""
            Write-Host "Configuration Summary:" -ForegroundColor Yellow
            
            if ($Config.services) {
                Write-Host "  Services: $($Config.services.Count)" -ForegroundColor White
                foreach ($Service in $Config.services) {
                    $Status = if ($Service.auto_start) { "Auto-start" } else { "Manual" }
                    Write-Host "    $($Service.name) ($($Service.type)) - Port $($Service.port) - $Status" -ForegroundColor Gray
                }
            }
            else {
                Write-Host "  Services: 0" -ForegroundColor Red
            }
            
            # Show key settings
            $KeySettings = @("health_check_interval", "max_retry_attempts", "service_discovery_interval")
            foreach ($Setting in $KeySettings) {
                if ($Config.ContainsKey($Setting)) {
                    Write-Host "  $Setting`: $($Config[$Setting])" -ForegroundColor White
                }
            }
            
            # Validate configuration
            Write-Host ""
            Write-Host "Validation Results:" -ForegroundColor Yellow
            $ValidationResult = Test-ConfigurationValidity -Config $Config
            
            if ($ValidationResult.IsValid) {
                Write-Host "  Status: Valid" -ForegroundColor Green
            }
            else {
                Write-Host "  Status: Invalid" -ForegroundColor Red
            }
            
            if ($ValidationResult.Errors.Count -gt 0) {
                Write-Host "  Errors:" -ForegroundColor Red
                foreach ($Error in $ValidationResult.Errors) {
                    Write-Host "    - $Error" -ForegroundColor Red
                }
            }
            
            if ($ValidationResult.Warnings.Count -gt 0) {
                Write-Host "  Warnings:" -ForegroundColor Yellow
                foreach ($Warning in $ValidationResult.Warnings) {
                    Write-Host "    - $Warning" -ForegroundColor Yellow
                }
            }
        }
        else {
            Write-Host "Status: Invalid (failed to parse)" -ForegroundColor Red
        }
    }
    else {
        Write-Host "Status: Not Found" -ForegroundColor Red
    }
    
    # Show available templates
    Write-Host ""
    Write-Host "Available Templates:" -ForegroundColor Yellow
    foreach ($TemplateName in $script:ConfigTemplates.Keys) {
        $Template = $script:ConfigTemplates[$TemplateName]
        Write-Host "  $TemplateName - $($Template.Description)" -ForegroundColor Gray
    }
    
    # Show recent backups
    if (Test-Path $BackupPath) {
        $BackupFiles = Get-ChildItem -Path $BackupPath -Filter "mcp-config-backup-*.yml" | Sort-Object LastWriteTime -Descending | Select-Object -First 5
        
        if ($BackupFiles.Count -gt 0) {
            Write-Host ""
            Write-Host "Recent Backups:" -ForegroundColor Yellow
            foreach ($Backup in $BackupFiles) {
                Write-Host "  $($Backup.Name) - $($Backup.LastWriteTime)" -ForegroundColor Gray
            }
        }
    }
    
    Write-Host ""
}

# Main execution
try {
    Write-Host "MCP Configuration Manager - Advanced Configuration Management" -ForegroundColor Cyan
    Write-Host "=" * 70 -ForegroundColor Cyan
    Write-Host ""
    
    switch ($Action.ToLower()) {
        "create" {
            if (-not $TemplateName) {
                Write-ConfigLog "Template name required for create action" -Level "ERROR"
                exit 1
            }
            
            $OutputPath = if ($ConfigPath -ne $DefaultConfigPath) { $ConfigPath } else { $DefaultConfigPath }
            
            if ((Test-Path $OutputPath) -and -not $Force) {
                Write-ConfigLog "Configuration already exists. Use -Force to overwrite." -Level "WARN"
                exit 1
            }
            
            $Success = New-ConfigurationFromTemplate -TemplateName $TemplateName -OutputPath $OutputPath -CustomProperties $Properties
            exit $(if ($Success) { 0 } else { 1 })
        }
        
        "validate" {
            $Config = Import-Configuration -ConfigPath $ConfigPath
            if ($Config) {
                $ValidationResult = Test-ConfigurationValidity -Config $Config
                
                Write-Host "Validation Results:" -ForegroundColor Yellow
                Write-Host "Status: $(if ($ValidationResult.IsValid) { "VALID" } else { "INVALID" })" -ForegroundColor $(if ($ValidationResult.IsValid) { "Green" } else { "Red" })
                
                if ($ValidationResult.Errors.Count -gt 0) {
                    Write-Host "Errors:" -ForegroundColor Red
                    foreach ($Error in $ValidationResult.Errors) {
                        Write-Host "  - $Error" -ForegroundColor Red
                    }
                }
                
                if ($ValidationResult.Warnings.Count -gt 0) {
                    Write-Host "Warnings:" -ForegroundColor Yellow
                    foreach ($Warning in $ValidationResult.Warnings) {
                        Write-Host "  - $Warning" -ForegroundColor Yellow
                    }
                }
                
                foreach ($Info in $ValidationResult.Info) {
                    Write-Host $Info -ForegroundColor White
                }
                
                exit $(if ($ValidationResult.IsValid) { 0 } else { 1 })
            }
            else {
                Write-ConfigLog "Failed to load configuration for validation" -Level "ERROR"
                exit 1
            }
        }
        
        "backup" {
            $BackupResult = Backup-Configuration -SourcePath $ConfigPath
            if ($BackupResult) {
                Write-Host "Backup created: $BackupResult" -ForegroundColor Green
                exit 0
            }
            else {
                exit 1
            }
        }
        
        "restore" {
            if (-not $SourceConfig) {
                Write-ConfigLog "Source backup path required for restore action" -Level "ERROR"
                exit 1
            }
            
            $TargetPath = if ($TargetConfig) { $TargetConfig } else { $ConfigPath }
            $Success = Restore-Configuration -BackupPath $SourceConfig -TargetPath $TargetPath
            exit $(if ($Success) { 0 } else { 1 })
        }
        
        "compare" {
            if (-not $SourceConfig -or -not $TargetConfig) {
                Write-ConfigLog "Both source and target configuration paths required for compare action" -Level "ERROR"
                exit 1
            }
            
            $ComparisonResult = Compare-Configurations -SourcePath $SourceConfig -TargetPath $TargetConfig
            exit $(if ($ComparisonResult) { 0 } else { 1 })
        }
        
        "template" {
            Write-Host "Available Configuration Templates:" -ForegroundColor Yellow
            Write-Host ""
            
            foreach ($TemplateName in $script:ConfigTemplates.Keys) {
                $Template = $script:ConfigTemplates[$TemplateName]
                Write-Host "$TemplateName" -ForegroundColor Cyan
                Write-Host "  Description: $($Template.Description)" -ForegroundColor White
                Write-Host "  Services: $($Template.Services.Count)" -ForegroundColor Gray
                foreach ($Service in $Template.Services) {
                    Write-Host "    - $($Service.name) ($($Service.type)) on port $($Service.port)" -ForegroundColor Gray
                }
                Write-Host ""
            }
        }
        
        "status" {
            Show-ConfigurationStatus -ConfigPath $ConfigPath
        }
        
        default {
            Write-ConfigLog "Unknown action: $Action" -Level "ERROR"
            Write-Host "Valid actions: Create, Validate, Backup, Restore, Compare, Template, Status" -ForegroundColor Yellow
            exit 1
        }
    }
    
}
catch {
    Write-ConfigLog "Configuration manager error: $($_.Exception.Message)" -Level "ERROR"
    Write-Host "Stack trace:" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Red
    exit 1
}