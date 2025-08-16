# MCP Manager PowerShell Wrapper System

**Enhanced Windows PowerShell integration for MCP Manager**

Original concept by @qdhenry (MIT License)  
Enhanced for Claude Code Dev Stack by DevOps Agent

## Overview

Complete PowerShell wrapper system for Windows that provides enterprise-grade MCP (Model Context Protocol) service management with Windows service integration, advanced health monitoring, configuration management, and automatic restart capabilities.

## Architecture

```
powershell/
├── MCPManager.psm1           # Core PowerShell module
├── MCPServiceManager.ps1     # Windows service management
├── MCPHealthMonitor.ps1      # Health monitoring & auto-restart
├── MCPConfigManager.ps1      # Configuration management
├── MCPOrchestrator.ps1       # Master orchestration system
└── README.md                 # This documentation
```

## Core Components

### 1. MCPManager.psm1 - Core PowerShell Module

The foundation module providing core MCP service management functions.

**Key Features:**
- Service discovery and registration
- Load balancing and health monitoring
- Real-time dashboard
- Configuration management
- Windows process integration
- System requirements validation

**Example Usage:**
```powershell
# Import the module
Import-Module .\MCPManager.psm1

# Initialize MCP Manager
Initialize-MCPManager

# Start the manager
Start-MCPManager

# View real-time dashboard
Show-MCPDashboard

# Check system information
Show-MCPSystemInfo
```

### 2. MCPServiceManager.ps1 - Windows Service Management

Advanced Windows service integration with full lifecycle management.

**Features:**
- Install/uninstall as Windows service
- Service recovery configuration
- Background operation
- Service monitoring
- Configuration backup/restore
- Process tracking

**Example Usage:**
```powershell
# Install as Windows service
.\MCPServiceManager.ps1 -Action Install -Force

# Start the service
.\MCPServiceManager.ps1 -Action Start

# Monitor service status
.\MCPServiceManager.ps1 -Action Monitor

# Backup configuration
.\MCPServiceManager.ps1 -Action Backup

# Service dashboard
.\MCPServiceManager.ps1 -Action Status
```

### 3. MCPHealthMonitor.ps1 - Health Monitoring & Auto-Restart

Comprehensive health monitoring with intelligent auto-restart capabilities.

**Features:**
- Real-time health checking
- Performance metrics collection
- Automatic service restart
- Email and webhook alerts
- Detailed logging
- Configurable thresholds

**Example Usage:**
```powershell
# Start health monitoring with auto-restart
.\MCPHealthMonitor.ps1 -AutoRestart -DetailedLogging

# Email alerts enabled
.\MCPHealthMonitor.ps1 -EmailAlerts -CheckInterval 15

# Single health check
.\MCPHealthMonitor.ps1 -RunOnce

# Background monitoring
.\MCPHealthMonitor.ps1 -Background -MonitorInterval 30
```

### 4. MCPConfigManager.ps1 - Configuration Management

Advanced configuration management with templates, validation, and versioning.

**Features:**
- Configuration templates (development, production, minimal)
- YAML validation and parsing
- Configuration backup/restore
- Environment-specific settings
- Configuration comparison
- Template-based generation

**Example Usage:**
```powershell
# Create configuration from template
.\MCPConfigManager.ps1 -Action Create -TemplateName production -Environment production

# Validate configuration
.\MCPConfigManager.ps1 -Action Validate

# Backup configuration
.\MCPConfigManager.ps1 -Action Backup

# Compare configurations
.\MCPConfigManager.ps1 -Action Compare -SourceConfig config1.yml -TargetConfig config2.yml

# Show available templates
.\MCPConfigManager.ps1 -Action Template
```

### 5. MCPOrchestrator.ps1 - Master Orchestration

Complete orchestration system that coordinates all components for seamless operation.

**Features:**
- Full deployment workflows
- Operation locking
- Statistics tracking
- Error handling and recovery
- Comprehensive dashboard
- Multi-environment support

**Example Usage:**
```powershell
# Full deployment
.\MCPOrchestrator.ps1 -Action Deploy -Environment production

# Start monitoring
.\MCPOrchestrator.ps1 -Action Monitor -MonitorDuration 3600

# System reset and redeploy
.\MCPOrchestrator.ps1 -Action Reset -Force

# View dashboard
.\MCPOrchestrator.ps1 -Action Dashboard

# Cleanup system
.\MCPOrchestrator.ps1 -Action Clean
```

## Installation & Setup

### Prerequisites

- **PowerShell 5.1+** (Windows PowerShell or PowerShell Core)
- **Python 3.8+** with pip
- **Administrator privileges** (for Windows service installation)
- **2GB+ RAM** and **1GB+ disk space**
- **Network ports 8080-8092** available

### Quick Start

1. **Clone and navigate to the PowerShell directory:**
   ```powershell
   cd "path\to\Claude_Code_Dev_Stack_v3\integrations\mcp-manager\powershell"
   ```

2. **Check system requirements:**
   ```powershell
   Import-Module .\MCPManager.psm1
   Get-MCPSystemRequirements
   ```

3. **Deploy with orchestrator:**
   ```powershell
   .\MCPOrchestrator.ps1 -Action Deploy -Environment development
   ```

4. **Start monitoring:**
   ```powershell
   .\MCPOrchestrator.ps1 -Action Monitor
   ```

### Manual Installation

1. **Install Python dependencies:**
   ```powershell
   .\scripts\Start-MCPManager.ps1 -InstallDependencies -SetupEnvironment
   ```

2. **Create configuration:**
   ```powershell
   .\MCPConfigManager.ps1 -Action Create -TemplateName default
   ```

3. **Install Windows service:**
   ```powershell
   .\MCPServiceManager.ps1 -Action Install
   ```

4. **Start services:**
   ```powershell
   .\MCPServiceManager.ps1 -Action Start
   ```

## Configuration

### Environment Templates

The system includes pre-configured templates for different environments:

**Development Template:**
- Minimal services for testing
- Debug logging enabled
- Relaxed health check intervals
- Manual service startup

**Production Template:**
- Full service stack
- Security features enabled
- Prometheus monitoring
- Resource limits configured
- Automatic service startup

**Minimal Template:**
- Single core service
- Basic configuration
- Testing and development focused

### Configuration Structure

```yaml
# Global settings
health_check_interval: 30
service_discovery_interval: 300
max_retry_attempts: 3

# Services
services:
  - id: "playwright-mcp-8080"
    name: "Playwright MCP Service"
    type: "playwright"
    host: "localhost"
    port: 8080
    auto_start: true
    restart_policy: "always"

# Load balancing
load_balancing:
  default_algorithm: "round_robin"
  health_check_timeout: 10

# Security settings
security:
  enable_authentication: false
  api_key_required: false
  rate_limiting:
    requests_per_minute: 1000
```

## Health Monitoring

### Health Check Types

1. **Connectivity Check** - TCP port availability
2. **HTTP Response Check** - Service endpoint health
3. **Performance Metrics** - CPU, memory, response time
4. **Process Health** - Windows service status

### Alert Configuration

Create `config/alert-config.json`:

```json
{
  "email": {
    "enabled": true,
    "smtp_server": "smtp.example.com",
    "smtp_port": 587,
    "username": "alerts@example.com",
    "password": "password",
    "from": "mcp-monitor@example.com",
    "to": ["admin@example.com"]
  },
  "webhook": {
    "enabled": true,
    "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  }
}
```

### Auto-Restart Logic

- **Health Check Failures** trigger restart attempts
- **Maximum Restart Attempts** prevent infinite loops
- **Exponential Backoff** between restart attempts
- **Success Reset** clears failure counters
- **Manual Intervention** required after max attempts

## Windows Service Integration

### Service Installation

The system can run as a native Windows service with:

- **Automatic startup** on system boot
- **Service recovery** on failure
- **Process isolation** for security
- **Event log integration** for monitoring
- **Service control** via Services.msc

### Service Configuration

- **Service Name:** MCPManager
- **Display Name:** MCP Manager Service
- **Startup Type:** Automatic
- **Recovery Actions:** Restart service (3 attempts)
- **Log On:** Local System Account

## Advanced Features

### Performance Monitoring

- **System CPU/Memory** tracking
- **Process-specific** metrics
- **Network connection** monitoring
- **Windows Performance Counters** integration
- **Historical data** collection

### Security Features

- **Process isolation** via Windows services
- **Configuration encryption** for sensitive data
- **Network security** with port monitoring
- **Access control** via Windows permissions
- **Audit logging** for compliance

### Disaster Recovery

- **Automated backups** of configuration
- **Point-in-time recovery** capabilities
- **Configuration versioning** and rollback
- **Service state persistence** across reboots
- **Emergency reset** procedures

## Troubleshooting

### Common Issues

**Service Won't Start:**
```powershell
# Check system requirements
Get-MCPSystemRequirements

# Verify configuration
.\MCPConfigManager.ps1 -Action Validate

# Check port availability
Test-MCPPortAvailability

# View service logs
.\MCPOrchestrator.ps1 -Action Logs
```

**Health Checks Failing:**
```powershell
# Manual health check
.\MCPHealthMonitor.ps1 -RunOnce -DetailedLogging

# Check process status
Get-MCPProcessInfo

# Verify network connectivity
Test-NetConnection localhost -Port 8080
```

**Configuration Issues:**
```powershell
# Validate configuration
.\MCPConfigManager.ps1 -Action Validate

# Compare with working configuration
.\MCPConfigManager.ps1 -Action Compare -SourceConfig backup.yml -TargetConfig current.yml

# Reset to default
.\MCPConfigManager.ps1 -Action Create -TemplateName default -Force
```

### Log Locations

- **Orchestrator Logs:** `logs/orchestrator.log`
- **Health Monitor Logs:** `logs/health-monitor.log`
- **Service Logs:** `logs/mcp-service.log`
- **Configuration Logs:** `logs/config-manager.log`
- **Windows Event Logs:** Application Log > MCP Health Monitor

### Recovery Procedures

**Complete System Reset:**
```powershell
# Stop everything
.\MCPOrchestrator.ps1 -Action Stop

# Clean up
.\MCPOrchestrator.ps1 -Action Clean

# Reset and redeploy
.\MCPOrchestrator.ps1 -Action Reset -Environment production
```

**Service Recovery:**
```powershell
# Uninstall and reinstall service
.\MCPServiceManager.ps1 -Action Uninstall
.\MCPServiceManager.ps1 -Action Install -Force

# Restore from backup
.\MCPServiceManager.ps1 -Action Restore -BackupPath "path\to\backup"
```

## API Reference

### Core Functions

**MCPManager.psm1:**
- `Initialize-MCPManager` - Initialize the MCP Manager
- `Start-MCPManager` - Start MCP services
- `Stop-MCPManager` - Stop MCP services
- `Get-MCPServices` - List all services
- `Get-MCPServiceStatus` - Get service status
- `Show-MCPDashboard` - Display dashboard
- `Get-MCPProcessInfo` - Get process information
- `Test-MCPPortAvailability` - Check port status
- `Get-MCPSystemRequirements` - Validate system requirements
- `Show-MCPSystemInfo` - Display system information

**Service Management:**
- `Install` - Install Windows service
- `Uninstall` - Remove Windows service
- `Start` - Start service
- `Stop` - Stop service
- `Restart` - Restart service
- `Status` - Show service status
- `Monitor` - Start monitoring
- `Backup` - Backup configuration

**Configuration Management:**
- `Create` - Create from template
- `Validate` - Validate configuration
- `Backup` - Backup configuration
- `Restore` - Restore from backup
- `Compare` - Compare configurations
- `Template` - Show templates

**Health Monitoring:**
- Auto-restart monitoring
- Alert configuration
- Performance tracking
- Health validation

## Contributing

This enhanced PowerShell wrapper system builds upon the original MCP Manager by @qdhenry. Contributions should:

1. Maintain compatibility with the original MIT license
2. Follow PowerShell best practices
3. Include comprehensive error handling
4. Provide detailed logging
5. Include help documentation

## License

MIT License - Building upon original work by @qdhenry

## Support

For issues and support:
1. Check troubleshooting section
2. Review log files
3. Verify system requirements
4. Test with minimal configuration
5. Create GitHub issue with logs and configuration