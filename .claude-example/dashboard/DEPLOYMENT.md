# Claude Code V3+ Dashboard - Deployment & Usage Guide

**Comprehensive deployment and usage documentation for the Claude Code Dev Stack V3+ Dashboard system with mobile access, terminal integration, and security features.**

---

## 📋 Table of Contents

1. [System Architecture Overview](#-system-architecture-overview)
2. [Installation Steps](#-installation-steps)
3. [Configuration Options](#-configuration-options)
4. [Usage Guide](#-usage-guide)
5. [Troubleshooting](#-troubleshooting)
6. [API Documentation](#-api-documentation)
7. [Security Considerations](#-security-considerations)
8. [Performance Tuning](#-performance-tuning)

---

## 🏗️ System Architecture Overview

The Claude Code V3+ Dashboard is a multi-component system designed for comprehensive monitoring and management:

### Architecture Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                             │
│  📱 Mobile (Galaxy S25 Edge) │ 💻 Desktop Browser │ 🖥️ Terminal │
└─────────────────┬───────────────────────────────────────────────┘
                  │ HTTPS/WSS (TLS 1.3)
┌─────────────────▼───────────────────────────────────────────────┐
│                    Security Layer                               │
│  🔐 Token Auth │ 🛡️ Rate Limiting │ 🔒 Session Management    │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│                  Application Layer                              │
│  🎯 Dashboard Server │ 📊 Real-time APIs │ 🔄 WebSocket Engine │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│                   Service Layer                                 │
│  🤖 Agent Monitor │ 🔧 Hook Monitor │ 🖥️ Terminal (ttyd)      │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│                     Data Layer                                  │
│  📈 Metrics DB │ 📝 Logs │ 🔒 Auth Store │ ⚙️ Configuration    │
└─────────────────────────────────────────────────────────────────┘
```

### Component Overview

| Component | Purpose | Technology | Port |
|-----------|---------|------------|------|
| **Dashboard Server** | Main web interface with real-time monitoring | Flask + SocketIO | 8080 |
| **Simple Dashboard** | Lightweight fallback dashboard | Built-in HTTP server | 8080 |
| **Terminal Manager** | Browser-based terminal access | ttyd binary | 7681 |
| **Mobile Auth** | Secure token-based authentication | Python + JSON storage | - |
| **WebSocket Engine** | Real-time data streaming | Socket.IO | 8080 |

---

## 🚀 Installation Steps

### 1. One-Liner Installation

#### Windows (PowerShell)
```powershell
iwr -Uri "https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/windows/dashboard/install-dashboard.ps1" -UseBasicParsing | iex
```

#### Linux/macOS
```bash
curl -fsSL https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/platform-tools/unix/dashboard/install-dashboard.sh | bash
```

### 2. Manual Installation

#### Prerequisites Check
```bash
# Check Python version (3.8+ required)
python --version

# Check pip availability
pip --version

# Check available disk space (minimum 500MB)
df -h
```

#### Step 1: Install Dependencies
```bash
# Core dependencies
pip install flask>=2.3.0 flask-socketio>=5.3.0 psutil>=5.9.0

# Optional dependencies for enhanced features
pip install requests qrcode[pil] pyngrok

# Development dependencies (optional)
pip install pytest pytest-cov black flake8
```

#### Step 2: Directory Setup
```bash
# Create dashboard directory structure
mkdir -p ~/.claude/dashboard/{templates,static,logs}
mkdir -p ~/.claude/mobile
mkdir -p ~/.claude/bin

# Set proper permissions (Unix systems)
chmod 755 ~/.claude/dashboard
chmod 700 ~/.claude/mobile  # Secure auth directory
```

#### Step 3: Download Dashboard Files
```bash
# Clone or download dashboard files
cd ~/.claude/dashboard

# Download main server
curl -O https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example/dashboard/dashboard_server.py

# Download simple fallback
curl -O https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example/dashboard/simple_dashboard.py

# Download terminal manager
curl -O https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example/dashboard/ttyd_manager.py

# Download HTML template
mkdir -p templates
curl -o templates/dashboard.html https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example/dashboard/templates/dashboard.html

# Download mobile auth
curl -o ../mobile/mobile_auth.py https://raw.githubusercontent.com/KrypticGadget/Claude_Code_Dev_Stack/main/.claude-example/mobile/mobile_auth.py
```

#### Step 4: Install Terminal Binary (ttyd)
```bash
# The terminal manager will auto-download ttyd on first run
# Or manually download for your platform:

# Windows
curl -L -o ~/.claude/bin/ttyd.exe https://github.com/tsl0922/ttyd/releases/download/1.7.4/ttyd.win32.exe

# Linux x86_64
curl -L -o ~/.claude/bin/ttyd https://github.com/tsl0922/ttyd/releases/download/1.7.4/ttyd.x86_64
chmod +x ~/.claude/bin/ttyd

# macOS x86_64
curl -L -o ~/.claude/bin/ttyd https://github.com/tsl0922/ttyd/releases/download/1.7.4/ttyd.x86_64.darwin
chmod +x ~/.claude/bin/ttyd
```

### 3. Dependency Requirements

#### Core Requirements (requirements.txt)
```txt
flask>=2.3.0
flask-socketio>=5.3.0
python-socketio>=5.8.0
python-engineio>=4.7.0
psutil>=5.9.0
```

#### Optional Requirements
```txt
# Remote access
requests>=2.28.0
pyngrok>=5.1.0

# QR code generation
qrcode[pil]>=7.3.1

# Enhanced security
cryptography>=3.4.8
bcrypt>=3.2.0

# Performance monitoring
py-cpuinfo>=8.0.0
GPUtil>=1.4.0
```

#### System Dependencies

**Windows:**
- Windows 10/11 (1909+)
- PowerShell 5.1+
- Windows Terminal (recommended)

**Linux:**
- glibc 2.17+ (most modern distributions)
- systemd (for service management)
- curl/wget

**macOS:**
- macOS 10.14+
- Xcode Command Line Tools

---

## ⚙️ Configuration Options

### 1. Port Settings

#### Dashboard Server Ports
```python
# dashboard_server.py configuration
SERVER_CONFIG = {
    'dashboard_port': 8080,      # Main dashboard interface
    'terminal_port': 7681,       # ttyd terminal access
    'debug_port': 8081,          # Debug interface (dev only)
    'websocket_port': 8080,      # WebSocket same as dashboard
}
```

#### Environment Variables
```bash
# Port configuration
export CLAUDE_DASHBOARD_PORT=8080
export CLAUDE_TERMINAL_PORT=7681
export CLAUDE_DEBUG_MODE=false

# Network binding
export CLAUDE_DASHBOARD_HOST=0.0.0.0  # All interfaces
export CLAUDE_DASHBOARD_HOST=127.0.0.1  # Local only
```

#### Command Line Options
```bash
# Start with custom port
python dashboard_server.py --port 9090

# Bind to specific host
python dashboard_server.py --host 127.0.0.1

# Enable debug mode
python dashboard_server.py --debug

# Custom terminal port
python ttyd_manager.py --port 7682
```

### 2. Authentication Configuration

#### Token-Based Authentication
```python
# Mobile authentication setup
auth_config = {
    'token_expiry': 24 * 60 * 60,    # 24 hours
    'max_sessions': 5,               # Concurrent sessions
    'rate_limit_window': 60,         # 1 minute
    'max_attempts': 10,              # Per IP per window
    'session_timeout': 86400,        # 24 hours
}
```

#### Generate Authentication Token
```bash
# Generate new auth token
python ~/.claude/mobile/mobile_auth.py generate

# Example output:
# Generated token: ABCxyz123-SecureToken-789DEF
# Expires: 2024-01-16T10:30:00
```

#### Authentication Environment Variables
```bash
# Security configuration
export CLAUDE_DASHBOARD_SECRET=your_secret_key_here
export CLAUDE_MOBILE_AUTH_TOKEN=your_mobile_token
export CLAUDE_SESSION_SECURE=true

# Optional: External auth providers
export CLAUDE_OAUTH_CLIENT_ID=your_oauth_client
export CLAUDE_OAUTH_SECRET=your_oauth_secret
```

### 3. Monitoring Intervals

#### Real-Time Update Configuration
```python
# Update intervals in seconds
MONITORING_CONFIG = {
    'system_metrics': 1,          # CPU, Memory, Disk every 1s
    'agent_status': 5,            # Agent monitoring every 5s
    'hook_status': 10,            # Hook system every 10s
    'performance_data': 30,       # Performance metrics every 30s
    'security_scan': 3600,        # Security checks hourly
    'log_rotation': 86400,        # Daily log rotation
}
```

#### WebSocket Update Rates
```javascript
// Client-side update configuration
const UPDATE_INTERVALS = {
    realtime: 100,      // 100ms - system metrics
    standard: 5000,     // 5s - standard updates
    background: 30000,  // 30s - background tasks
    slow: 300000,       // 5min - slow-changing data
};
```

#### Configuring Update Frequency
```bash
# High-frequency monitoring (development)
export CLAUDE_UPDATE_RATE=fast      # 100ms updates

# Standard monitoring (production)
export CLAUDE_UPDATE_RATE=standard  # 1s updates

# Low-frequency monitoring (battery saving)
export CLAUDE_UPDATE_RATE=slow      # 10s updates
```

---

## 💻 Usage Guide

### 1. Accessing Dashboard

#### Local Access
```bash
# Start the dashboard server
cd ~/.claude/dashboard
python dashboard_server.py

# Access in browser
open http://localhost:8080

# Alternative: Simple dashboard (no dependencies)
python simple_dashboard.py
```

#### Remote Access Setup
```bash
# Install tunnel provider
pip install pyngrok

# Start with remote access
python dashboard_server.py --mobile-auth your_token

# The system will automatically:
# 1. Start dashboard on localhost:8080
# 2. Create secure tunnel (ngrok/cloudflare)
# 3. Generate QR code for mobile access
# 4. Display secure URL with authentication
```

### 2. Using Terminal Interface

#### Browser-Based Terminal
```bash
# Start terminal server
python ttyd_manager.py

# Access terminal in browser
open http://localhost:7681

# Login with generated credentials:
# Username: admin
# Password: [auto-generated secure password]
```

#### Terminal Features
- **Full shell access** - Complete command line environment
- **File editing** - Built-in editor with syntax highlighting
- **Session persistence** - Reconnect to running sessions
- **Multi-tab support** - Multiple terminal sessions
- **Copy/paste** - Seamless clipboard integration
- **Responsive design** - Works on mobile devices

#### Terminal Configuration
```bash
# Custom shell
python ttyd_manager.py --shell /bin/zsh

# Custom theme
python ttyd_manager.py --theme dark

# Read-only mode
python ttyd_manager.py --readonly

# Custom welcome message
python ttyd_manager.py --title "Claude Code Terminal"
```

### 3. Mobile Access via QR Code

#### QR Code Generation
```bash
# Generate mobile access QR code
python ~/.claude/mobile/mobile_auth.py generate --qr

# The QR code contains:
# - Secure dashboard URL (tunnel)
# - Authentication token
# - Session expiry information
```

#### Mobile Browser Setup
```bash
# Samsung Internet (recommended for Galaxy S25 Edge)
# 1. Scan QR code or enter URL
# 2. Authenticate with token (auto-filled)
# 3. Enable "Add to Home Screen"
# 4. Grant notification permissions

# Features enabled:
# - Touch-optimized interface
# - S Pen support
# - Edge panel integration
# - Samsung DeX compatibility
```

#### Mobile-Specific Features

**Touch Controls:**
- **Swipe left/right** - Switch dashboard tabs
- **Pinch to zoom** - Zoom charts and metrics
- **Long press** - Context menus and options
- **Pull to refresh** - Update dashboard data

**Samsung Galaxy S25 Edge Optimizations:**
- **Edge display curves** - Content safely within curved area
- **S Pen integration** - Precision controls and annotations
- **Dark mode** - OLED-optimized for battery life
- **DeX mode** - Desktop experience when docked

### 4. Command Execution

#### Dashboard Command Interface
```javascript
// Execute commands via WebSocket
socket.emit('execute_command', {
    command: 'system_status',
    parameters: {},
    authentication: 'session_token'
});

// Receive command results
socket.on('command_result', (data) => {
    console.log('Command output:', data.result);
});
```

#### Supported Commands
```python
# System commands
SUPPORTED_COMMANDS = {
    'system_status': 'Get overall system health',
    'restart_agent': 'Restart specific agent',
    'clear_logs': 'Clear system logs',
    'update_config': 'Update configuration',
    'export_metrics': 'Export performance data',
    'security_scan': 'Run security audit',
    'backup_data': 'Create system backup',
}
```

#### Command Whitelist
```json
{
  "allowed_commands": [
    "system_status",
    "agent_status",
    "performance_metrics",
    "log_tail",
    "config_get",
    "health_check"
  ],
  "restricted_commands": [
    "system_shutdown",
    "delete_logs",
    "modify_config",
    "user_management"
  ],
  "admin_only": [
    "security_audit",
    "backup_restore",
    "service_restart"
  ]
}
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Dashboard Not Loading

**Symptom:** Browser shows "Connection refused" or "Site can't be reached"

**Diagnosis:**
```bash
# Check if dashboard is running
ps aux | grep dashboard_server

# Check port availability
netstat -an | grep 8080
# OR
ss -tuln | grep 8080

# Test local connection
curl http://localhost:8080/api/status
```

**Solutions:**
```bash
# Solution 1: Restart dashboard
pkill -f dashboard_server
python ~/.claude/dashboard/dashboard_server.py

# Solution 2: Check firewall
# Windows
netsh advfirewall firewall add rule name="Claude Dashboard" dir=in action=allow protocol=TCP localport=8080

# Linux (ufw)
sudo ufw allow 8080/tcp

# Linux (firewalld)
sudo firewall-cmd --add-port=8080/tcp --permanent
sudo firewall-cmd --reload

# Solution 3: Use alternative port
python dashboard_server.py --port 8081
```

#### 2. WebSocket Connection Issues

**Symptom:** Dashboard loads but shows "Disconnected" status, no real-time updates

**Diagnosis:**
```bash
# Check WebSocket endpoint
curl -I http://localhost:8080/socket.io/

# Check for proxy/reverse proxy issues
curl -H "Upgrade: websocket" -H "Connection: upgrade" http://localhost:8080
```

**Solutions:**
```bash
# Solution 1: Disable proxy/VPN
# Temporarily disable any proxy software

# Solution 2: Browser-specific fixes
# Chrome: chrome://settings/content/javascriptExceptions
# Firefox: about:config -> network.websocket.enabled -> true

# Solution 3: Alternative transport
# Edit dashboard.html, find socket.io connection:
socket = io({
    transports: ['polling', 'websocket']  # Fallback to polling
});
```

#### 3. Mobile Access Problems

**Symptom:** QR code doesn't work, mobile browser can't connect

**Diagnosis:**
```bash
# Check tunnel status
python -c "import requests; print(requests.get('http://your-tunnel-url/api/status').status_code)"

# Verify authentication
python ~/.claude/mobile/mobile_auth.py validate your_token

# Test mobile network
ping your-tunnel-domain.ngrok.io
```

**Solutions:**
```bash
# Solution 1: Regenerate tunnel
pkill -f ngrok
python dashboard_server.py --mobile-auth new_token

# Solution 2: Alternative tunnel provider
# Install cloudflared
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb
cloudflared tunnel --url http://localhost:8080

# Solution 3: Direct IP access (local network only)
# Find your local IP
ip addr show | grep inet
# Access via http://192.168.1.100:8080 (replace with your IP)
```

#### 4. Performance Issues

**Symptom:** Dashboard is slow, high CPU usage, delayed updates

**Diagnosis:**
```bash
# Monitor dashboard resource usage
top -p $(pgrep -f dashboard_server)

# Check system resources
free -h
df -h
iostat 1 5

# Profile Python performance
python -m cProfile -o dashboard.prof dashboard_server.py
```

**Solutions:**
```bash
# Solution 1: Reduce update frequency
export CLAUDE_UPDATE_RATE=slow
python dashboard_server.py

# Solution 2: Disable heavy features
# Edit dashboard_server.py
MONITORING_CONFIG = {
    'detailed_metrics': False,
    'chart_animations': False,
    'background_tasks': False,
}

# Solution 3: Use simple dashboard
python simple_dashboard.py  # Lightweight alternative
```

### Debug Mode

#### Enable Debug Mode
```bash
# Start with debug enabled
python dashboard_server.py --debug

# Set debug environment
export CLAUDE_DEBUG=true
export FLASK_DEBUG=1

# Enable verbose logging
export CLAUDE_LOG_LEVEL=DEBUG
```

#### Debug Information Available
```python
# Debug endpoints (only in debug mode)
debug_endpoints = {
    '/debug/status': 'System status details',
    '/debug/config': 'Configuration dump',
    '/debug/metrics': 'Raw metrics data',
    '/debug/logs': 'Debug logs',
    '/debug/sessions': 'Active sessions',
    '/debug/performance': 'Performance profiling',
}
```

### Log Locations

#### Log File Structure
```
~/.claude/logs/
├── dashboard.log              # Main dashboard log
├── dashboard_error.log        # Error-only log
├── mobile_auth.log           # Authentication events
├── terminal.log              # Terminal access log
├── performance.log           # Performance metrics
├── security.log              # Security events
└── debug.log                 # Debug information (debug mode only)
```

#### Log Analysis Commands
```bash
# Monitor real-time dashboard logs
tail -f ~/.claude/logs/dashboard.log

# Search for errors
grep -i error ~/.claude/logs/*.log

# Monitor authentication attempts
grep -i "auth" ~/.claude/logs/mobile_auth.log

# Performance analysis
grep -i "slow\|timeout\|error" ~/.claude/logs/performance.log

# Security events
tail -f ~/.claude/logs/security.log
```

#### Log Rotation Configuration
```python
# Log rotation settings
LOG_CONFIG = {
    'max_size': '100MB',        # Maximum log file size
    'backup_count': 7,          # Keep 7 days of logs
    'rotate_when': 'midnight',  # Daily rotation
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}
```

---

## 📡 API Documentation

### 1. WebSocket Events

#### Client → Server Events
```javascript
// Request real-time updates
socket.emit('request_update');

// Execute command
socket.emit('execute_command', {
    command: 'system_status',
    parameters: {},
    auth_token: 'your_token'
});

// Subscribe to specific metrics
socket.emit('subscribe', {
    channels: ['system_metrics', 'agent_status'],
    update_rate: 'realtime'  // realtime, standard, slow
});
```

#### Server → Client Events
```javascript
// System status update
socket.on('status_update', (data) => {
    console.log('System status:', data.status);
    console.log('Last update:', data.timestamp);
});

// Real-time metrics
socket.on('metrics_update', (data) => {
    console.log('CPU:', data.system.cpu_percent);
    console.log('Memory:', data.system.memory_percent);
    console.log('Agents:', data.claude_code.total_operations);
});

// New alert notification
socket.on('new_alert', (alert) => {
    console.log('Alert level:', alert.level);
    console.log('Message:', alert.message);
    console.log('Timestamp:', alert.timestamp);
});

// Command execution result
socket.on('command_result', (result) => {
    console.log('Command:', result.command);
    console.log('Success:', result.success);
    console.log('Output:', result.output);
});
```

### 2. REST Endpoints

#### System Information
```http
GET /api/status
Authorization: Bearer your_session_token

Response:
{
    "status": "healthy|warning|critical|error",
    "last_update": "2024-01-15T10:30:00Z",
    "uptime": "5d 12h 30m",
    "version": "3.0+"
}
```

#### Metrics Data
```http
GET /api/metrics
Authorization: Bearer your_session_token

Response:
{
    "system": {
        "cpu_percent": 45.2,
        "memory_percent": 67.8,
        "memory_used_gb": 8.2,
        "memory_total_gb": 32.0,
        "disk_percent": 24.5,
        "disk_used_gb": 125.4,
        "disk_total_gb": 512.0
    },
    "claude_code": {
        "total_operations": 1247,
        "average_execution_time": 2.3,
        "total_tokens_used": 45230,
        "issues_detected": 3
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Agent Status
```http
GET /api/agents
Authorization: Bearer your_session_token

Response:
{
    "total_agents": 28,
    "active_agents": 5,
    "agents": [
        {
            "name": "master-orchestrator",
            "last_used": "2024-01-15T10:25:00Z",
            "executions": 15,
            "file_size": 45120
        }
    ]
}
```

#### Performance Metrics
```http
GET /api/performance
Authorization: Bearer your_session_token

Response:
{
    "summary": {
        "total_operations": 1247,
        "average_execution_time": 2.3,
        "peak_memory_usage": 78.5,
        "issues_detected": 3
    },
    "resource_timeline": {
        "timestamps": ["10:00", "10:01", "10:02"],
        "cpu_usage": [45.2, 47.1, 44.8],
        "memory_usage": [67.8, 68.2, 67.5],
        "disk_usage": [24.5, 24.5, 24.6]
    }
}
```

#### Security Status
```http
GET /api/security
Authorization: Bearer your_session_token

Response:
{
    "status": "secure|warning|critical|attention",
    "total_issues": 5,
    "severity_counts": {
        "HIGH": 1,
        "MEDIUM": 2,
        "LOW": 2
    },
    "files_scanned": 245,
    "last_scan": "2024-01-15T09:00:00Z",
    "recent_issues": [
        {
            "file": "config.py",
            "line": 42,
            "severity": "MEDIUM",
            "description": "Hardcoded password detected"
        }
    ]
}
```

### 3. Command Whitelist

#### System Commands
```json
{
  "system": {
    "system_status": {
      "description": "Get comprehensive system status",
      "parameters": [],
      "permission_level": "user",
      "example": "system_status"
    },
    "restart_service": {
      "description": "Restart specific service",
      "parameters": ["service_name"],
      "permission_level": "admin",
      "example": "restart_service dashboard"
    },
    "get_logs": {
      "description": "Retrieve recent log entries",
      "parameters": ["log_type", "lines"],
      "permission_level": "user",
      "example": "get_logs system 100"
    }
  }
}
```

#### Agent Commands
```json
{
  "agents": {
    "list_agents": {
      "description": "List all available agents",
      "parameters": [],
      "permission_level": "user"
    },
    "agent_status": {
      "description": "Get status of specific agent",
      "parameters": ["agent_name"],
      "permission_level": "user"
    },
    "restart_agent": {
      "description": "Restart specific agent",
      "parameters": ["agent_name"],
      "permission_level": "admin"
    }
  }
}
```

#### Security Commands
```json
{
  "security": {
    "security_scan": {
      "description": "Run comprehensive security scan",
      "parameters": ["scan_type"],
      "permission_level": "admin",
      "example": "security_scan full"
    },
    "list_sessions": {
      "description": "List active authentication sessions",
      "parameters": [],
      "permission_level": "admin"
    },
    "revoke_session": {
      "description": "Revoke specific session",
      "parameters": ["session_id"],
      "permission_level": "admin"
    }
  }
}
```

### 4. Authentication API

#### Generate Token
```http
POST /api/auth/generate
Content-Type: application/json

Request:
{
    "metadata": {
        "device": "Samsung Galaxy S25 Edge",
        "purpose": "Mobile dashboard access"
    }
}

Response:
{
    "token": "ABCxyz123-SecureToken-789DEF",
    "expires": "2024-01-16T10:30:00Z",
    "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
}
```

#### Validate Session
```http
GET /api/auth/status
Cookie: claude_session_id=session_token_here

Response:
{
    "authenticated": true,
    "auth_enabled": true,
    "session_info": {
        "session_id": "abc123...",
        "ip_address": "192.168.1.100",
        "created": "2024-01-15T10:00:00Z",
        "last_activity": "2024-01-15T10:30:00Z",
        "requests": 47
    }
}
```

---

## 🔒 Security Considerations

### 1. Authentication Security

#### Token Security
```python
# Token generation uses cryptographically secure random
token = secrets.token_urlsafe(32)  # 256-bit entropy

# Token validation includes:
token_validation = {
    'expiry_check': True,      # Time-based expiry
    'usage_tracking': True,    # Monitor usage patterns
    'ip_binding': True,        # Bind session to IP
    'rate_limiting': True,     # Prevent brute force
}
```

#### Session Management
```python
session_security = {
    'secure_cookies': True,           # HTTPS only cookies
    'httponly_cookies': True,         # No JavaScript access
    'samesite': 'Lax',               # CSRF protection
    'session_timeout': 86400,         # 24-hour timeout
    'session_regeneration': True,     # New ID on privilege change
}
```

### 2. Network Security

#### HTTPS Configuration
```python
# TLS Configuration
tls_config = {
    'min_version': 'TLSv1.3',        # Latest TLS only
    'cipher_suites': [               # Strong ciphers only
        'ECDHE-RSA-AES256-GCM-SHA384',
        'ECDHE-RSA-AES128-GCM-SHA256',
    ],
    'hsts_enabled': True,            # HTTP Strict Transport Security
    'hsts_max_age': 31536000,        # 1 year
}
```

#### Firewall Configuration
```bash
# Recommended firewall rules
# Allow only necessary ports
ufw allow 8080/tcp comment "Dashboard HTTP"
ufw allow 8443/tcp comment "Dashboard HTTPS"
ufw allow 7681/tcp comment "Terminal access"

# Deny all other incoming
ufw default deny incoming
ufw default allow outgoing
```

### 3. Input Validation

#### Command Sanitization
```python
# Command whitelist enforcement
ALLOWED_COMMANDS = {
    'system_status': {'params': [], 'dangerous': False},
    'get_logs': {'params': ['log_type', 'lines'], 'dangerous': False},
    'restart_service': {'params': ['service'], 'dangerous': True},
}

def validate_command(command, params, user_role):
    if command not in ALLOWED_COMMANDS:
        raise SecurityError("Command not allowed")
    
    if ALLOWED_COMMANDS[command]['dangerous'] and user_role != 'admin':
        raise SecurityError("Insufficient privileges")
    
    return sanitize_parameters(params)
```

#### Parameter Sanitization
```python
import re
import html

def sanitize_input(user_input):
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[;<>&|`$]', '', user_input)
    
    # HTML escape for display
    sanitized = html.escape(sanitized)
    
    # Limit length
    sanitized = sanitized[:1000]
    
    return sanitized
```

### 4. Rate Limiting

#### IP-Based Rate Limiting
```python
rate_limits = {
    'authentication': {
        'window': 60,           # 1 minute window
        'max_attempts': 10,     # 10 attempts per window
        'lockout_duration': 300, # 5 minute lockout
    },
    'api_calls': {
        'window': 60,           # 1 minute window
        'max_requests': 100,    # 100 requests per minute
        'burst_limit': 20,      # 20 requests in quick succession
    }
}
```

### 5. Security Monitoring

#### Security Event Logging
```python
# Security events that trigger alerts
security_events = {
    'failed_authentication': 'Multiple failed login attempts',
    'privilege_escalation': 'User attempting admin commands',
    'suspicious_commands': 'Potentially dangerous command execution',
    'unusual_access': 'Access from new IP or unusual hours',
    'session_hijacking': 'Session used from different IP',
}
```

#### Intrusion Detection
```python
# Basic intrusion detection patterns
intrusion_patterns = {
    'sql_injection': r'(union|select|insert|update|delete|drop)\s+',
    'command_injection': r'[;&|`$()]',
    'path_traversal': r'\.\./|\.\.\\\',
    'xss_attempt': r'<script|javascript:|on\w+\s*=',
}
```

---

## ⚡ Performance Tuning

### 1. Dashboard Performance

#### Resource Optimization
```python
# Performance tuning configuration
performance_config = {
    'update_batching': True,        # Batch multiple updates
    'compression': True,            # Compress WebSocket data
    'caching': {
        'static_data': 3600,        # Cache static data 1 hour
        'metrics_data': 30,         # Cache metrics 30 seconds
        'user_sessions': 1800,      # Cache sessions 30 minutes
    },
    'connection_pooling': {
        'max_connections': 100,     # Max concurrent connections
        'keepalive_timeout': 300,   # 5 minute keepalive
    }
}
```

#### Memory Management
```python
# Memory optimization settings
memory_config = {
    'max_history_points': 1000,     # Limit historical data
    'log_rotation_size': 100*1024*1024,  # 100MB log files
    'session_cleanup_interval': 3600,     # Cleanup hourly
    'metrics_retention': 7*24*3600,       # Keep 7 days
}
```

### 2. WebSocket Optimization

#### Connection Management
```javascript
// Client-side connection optimization
const socketConfig = {
    transports: ['websocket', 'polling'],
    upgrade: true,
    rememberUpgrade: true,
    timeout: 20000,
    forceNew: false,
    reconnection: true,
    reconnectionAttempts: 5,
    reconnectionDelay: 1000,
    maxReconnectionDelay: 5000,
};
```

#### Data Compression
```python
# Server-side compression
compression_config = {
    'enable_compression': True,
    'compression_level': 6,         # Balance speed vs size
    'compression_threshold': 1024,  # Compress data > 1KB
    'compression_method': 'gzip',
}
```

### 3. Mobile Performance

#### Battery Optimization
```javascript
// Battery-conscious update rates
const batteryConfig = {
    'high_battery': {
        'update_rate': 1000,        // 1 second updates
        'chart_animations': true,
        'background_updates': true,
    },
    'low_battery': {
        'update_rate': 10000,       // 10 second updates
        'chart_animations': false,
        'background_updates': false,
    }
};

// Detect battery status (if available)
if ('getBattery' in navigator) {
    navigator.getBattery().then(function(battery) {
        const config = battery.level > 0.2 ? 
            batteryConfig.high_battery : 
            batteryConfig.low_battery;
        applyConfig(config);
    });
}
```

#### Mobile Network Optimization
```javascript
// Adaptive quality based on connection
const connectionConfig = {
    '4g': {
        'chart_resolution': 'high',
        'update_frequency': 'realtime',
        'image_quality': 100,
    },
    '3g': {
        'chart_resolution': 'medium',
        'update_frequency': 'standard',
        'image_quality': 75,
    },
    'slow-2g': {
        'chart_resolution': 'low',
        'update_frequency': 'slow',
        'image_quality': 50,
    }
};
```

### 4. System Resource Tuning

#### CPU Optimization
```bash
# System-level performance tuning
# Set CPU governor to performance (when needed)
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Increase process priority (careful with this)
nice -n -10 python dashboard_server.py

# Use multiple worker processes
gunicorn --workers 4 --worker-class eventlet -w 1 --bind 0.0.0.0:8080 dashboard_server:app
```

#### Memory Optimization
```bash
# Increase system limits
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# Tune virtual memory
echo 'vm.swappiness=10' >> /etc/sysctl.conf
echo 'vm.vfs_cache_pressure=50' >> /etc/sysctl.conf
```

### 5. Database Performance

#### Metrics Database Tuning
```python
# SQLite optimization for metrics storage
sqlite_config = {
    'synchronous': 'NORMAL',        # Balance safety vs speed
    'cache_size': 10000,            # 10MB cache
    'temp_store': 'MEMORY',         # Use RAM for temp data
    'journal_mode': 'WAL',          # Write-ahead logging
    'auto_vacuum': 'INCREMENTAL',   # Gradual space reclamation
}
```

#### Log Management
```python
# Efficient log handling
log_config = {
    'buffer_size': 64*1024,         # 64KB write buffer
    'flush_interval': 5,            # Flush every 5 seconds
    'compression': 'gzip',          # Compress old logs
    'retention_days': 30,           # Keep 30 days
    'max_file_size': 100*1024*1024, # 100MB per file
}
```

### 6. Monitoring Performance Metrics

#### Performance Dashboard
```python
# Key performance indicators to monitor
performance_kpis = {
    'response_time': {
        'target': '<100ms',
        'warning': '>500ms',
        'critical': '>2000ms'
    },
    'memory_usage': {
        'target': '<256MB',
        'warning': '>512MB',
        'critical': '>1GB'
    },
    'cpu_usage': {
        'target': '<25%',
        'warning': '>50%',
        'critical': '>80%'
    },
    'concurrent_connections': {
        'target': '<50',
        'warning': '>100',
        'critical': '>200'
    }
}
```

#### Performance Alerts
```python
# Automated performance monitoring
def check_performance():
    metrics = get_current_metrics()
    
    if metrics['response_time'] > 2000:
        send_alert('CRITICAL', 'Dashboard response time > 2s')
    
    if metrics['memory_usage'] > 1024*1024*1024:  # 1GB
        send_alert('CRITICAL', 'Dashboard memory usage > 1GB')
    
    if metrics['cpu_usage'] > 80:
        send_alert('WARNING', 'Dashboard CPU usage > 80%')
```

---

## 📚 Appendix

### Example Configuration Files

#### dashboard_config.json
```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8080,
    "debug": false,
    "ssl_enabled": false,
    "ssl_cert": "cert.pem",
    "ssl_key": "key.pem"
  },
  "authentication": {
    "enabled": true,
    "token_expiry": 86400,
    "max_sessions": 10,
    "rate_limit": {
      "window": 60,
      "max_attempts": 10
    }
  },
  "monitoring": {
    "update_interval": 1,
    "history_retention": 604800,
    "metrics_compression": true
  },
  "mobile": {
    "qr_enabled": true,
    "push_notifications": false,
    "battery_optimization": true
  }
}
```

#### systemd Service File
```ini
[Unit]
Description=Claude Code V3+ Dashboard
After=network.target

[Service]
Type=simple
User=claude
WorkingDirectory=/home/claude/.claude/dashboard
Environment=PYTHONPATH=/home/claude/.claude
ExecStart=/usr/bin/python3 dashboard_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Quick Reference Commands

```bash
# Start dashboard
python ~/.claude/dashboard/dashboard_server.py

# Start with mobile access
python ~/.claude/dashboard/dashboard_server.py --mobile-auth $(python ~/.claude/mobile/mobile_auth.py generate | grep token | cut -d' ' -f3)

# Start simple dashboard (fallback)
python ~/.claude/dashboard/simple_dashboard.py

# Generate authentication token
python ~/.claude/mobile/mobile_auth.py generate

# Check dashboard status
curl http://localhost:8080/api/status

# Monitor logs
tail -f ~/.claude/logs/dashboard.log

# Stop dashboard
pkill -f dashboard_server
```

---

**The Claude Code V3+ Dashboard provides comprehensive monitoring, secure mobile access, and powerful management capabilities for your entire development environment. This deployment guide ensures you can set up, configure, and optimize the dashboard for maximum efficiency and security.**

🚀 **Ready to monitor everywhere, deploy securely!**