# Claude Code Tunnel Management System

## Overview

The Claude Code Tunnel Management System provides comprehensive remote access capabilities for your development environment. It manages secure tunnels using ngrok and other providers, enabling remote access to your local services with health monitoring, QR code generation, and automatic recovery.

## Features

- **Multi-Service Tunneling**: Support for all Claude Code services
- **Health Monitoring**: Automatic health checks with recovery
- **QR Code Generation**: Mobile-friendly access codes
- **Cross-Platform Support**: Windows, macOS, and Linux
- **Configuration Management**: Interactive configuration editor
- **Real-time Status**: Live tunnel monitoring with metrics
- **Automatic Recovery**: Auto-restart failed tunnels
- **Security**: Authentication and rate limiting support

## Quick Start

### 1. Setup

```bash
# Run the setup script
node scripts/setup-tunnel-management.js

# Or install dependencies manually
npm install qrcode qrcode-terminal clipboardy
```

### 2. Get ngrok Token

1. Visit [ngrok dashboard](https://dashboard.ngrok.com/signup)
2. Sign up for a free account
3. Copy your auth token from the dashboard

### 3. Configure Environment

Edit `.env.tunnel` or set environment variables:

```bash
# Required
NGROK_AUTHTOKEN=your_token_here

# Optional - Service Ports
CLAUDE_APP_PORT=3000
CLAUDE_API_PORT=3001
CLAUDE_UI_PORT=5173
```

### 4. Start Tunnels

```bash
# Using CLI commands
claude-code-tunnel-start

# Using npm scripts
npm run tunnel:start

# With custom token
claude-code-tunnel-start --token YOUR_TOKEN
```

## Commands

### claude-code-tunnel-start

Start all NGROK tunnels with health checks.

```bash
claude-code-tunnel-start [options]

Options:
  -c, --config <path>     Custom configuration file path
  -s, --services <list>   Comma-separated list of services to start
  -w, --wait             Wait for user input before exiting
  -q, --quiet            Suppress non-essential output
  --no-health-checks     Disable health checks
  --no-qr               Disable QR code generation
  --no-clipboard        Disable clipboard functionality
  --token <token>       Set ngrok auth token
```

**Examples:**
```bash
# Start all tunnels
claude-code-tunnel-start

# Start specific services only
claude-code-tunnel-start --services claude-app,claude-api

# Start with custom token
claude-code-tunnel-start --token 2fN9S1K8VxH3n7wP1mQ4567890_1AbCdEfGhIjKlMnOpQrStUv

# Start in quiet mode
claude-code-tunnel-start --quiet --no-qr
```

### claude-code-tunnel-stop

Gracefully stop all tunnels and cleanup processes.

```bash
claude-code-tunnel-stop [options]

Options:
  -f, --force      Force kill all tunnel processes
  -q, --quiet      Suppress non-essential output
  --keep-logs      Keep log files after stopping
```

**Examples:**
```bash
# Graceful stop
claude-code-tunnel-stop

# Force stop
claude-code-tunnel-stop --force

# Stop and keep logs
claude-code-tunnel-stop --keep-logs
```

### claude-code-tunnel-status

Check tunnel status and display URLs with health information.

```bash
claude-code-tunnel-status [options]

Options:
  -j, --json           Output status in JSON format
  -q, --quiet          Show minimal output
  -w, --watch          Watch mode - refresh every 5 seconds
  --qr <service>       Show QR code for specific service
  --qr-all            Show QR codes for all services
  --health            Show detailed health check information
  --metrics           Show tunnel metrics and statistics
  --copy <service>    Copy URL for specific service to clipboard
```

**Examples:**
```bash
# Basic status
claude-code-tunnel-status

# Watch mode (auto-refresh)
claude-code-tunnel-status --watch

# Show QR codes
claude-code-tunnel-status --qr-all

# Health details
claude-code-tunnel-status --health --metrics

# Copy URL to clipboard
claude-code-tunnel-status --copy claude-app

# JSON output
claude-code-tunnel-status --json
```

### claude-code-tunnel-restart

Restart failed tunnels or perform a complete restart.

```bash
claude-code-tunnel-restart [options]

Options:
  -a, --all              Restart all tunnels (complete restart)
  -s, --service <name>   Restart specific service tunnel
  -f, --force           Force restart without graceful shutdown
  -q, --quiet           Suppress non-essential output
  -w, --wait <seconds>  Wait time between stop and start (default: 3)
  --check-health        Check service health before restarting
```

**Examples:**
```bash
# Restart failed tunnels only
claude-code-tunnel-restart

# Complete restart
claude-code-tunnel-restart --all

# Restart specific service
claude-code-tunnel-restart --service claude-app

# Force restart with health check
claude-code-tunnel-restart --force --check-health
```

### claude-code-tunnel-config

Configure tunnel settings and manage service definitions.

```bash
claude-code-tunnel-config [options]

Options:
  -s, --show           Show current configuration
  -e, --edit           Interactive configuration editor
  -v, --validate       Validate configuration
  -r, --reset          Reset to default configuration
  --set <key=value>    Set specific configuration value
  --service <name>     Configure specific service
  --export <file>      Export configuration to file
  --import <file>      Import configuration from file
```

**Examples:**
```bash
# Show current config
claude-code-tunnel-config --show

# Interactive editor
claude-code-tunnel-config --edit

# Set specific value
claude-code-tunnel-config --set settings.auto_restart=true

# Configure service
claude-code-tunnel-config --service claude-app

# Export/Import
claude-code-tunnel-config --export backup.json
claude-code-tunnel-config --import backup.json
```

## Configuration

### Main Configuration File

Located at `config/tunnel/tunnel-config.json`:

```json
{
  "version": "1.0.0",
  "providers": {
    "ngrok": {
      "enabled": true,
      "priority": 1,
      "config_path": "./config/ngrok/ngrok.yml"
    }
  },
  "services": {
    "claude-app": {
      "name": "Claude Code Main Application",
      "port": 3000,
      "subdomain": "claude-dev",
      "health_check": {
        "enabled": true,
        "path": "/health",
        "interval": 30000,
        "timeout": 5000
      }
    }
  },
  "settings": {
    "auto_start": true,
    "auto_restart": true,
    "health_check_enabled": true,
    "qr_code_enabled": true,
    "notifications_enabled": true
  }
}
```

### ngrok Configuration

Located at `config/ngrok/ngrok.yml`:

```yaml
version: "2"
authtoken: ${NGROK_AUTHTOKEN}
region: us
web_addr: 0.0.0.0:4040

tunnels:
  claude-app:
    proto: http
    addr: ${CLAUDE_APP_PORT:-3000}
    subdomain: ${NGROK_SUBDOMAIN:-claude-dev}
    bind_tls: true
```

### Environment Variables

```bash
# Required
NGROK_AUTHTOKEN=your_token_here

# Optional - Custom subdomains (requires ngrok pro)
NGROK_SUBDOMAIN=claude-dev
NGROK_API_SUBDOMAIN=claude-api

# Optional - Service ports
CLAUDE_APP_PORT=3000
CLAUDE_API_PORT=3001

# Optional - Authentication
NGROK_MONITORING_AUTH=admin:admin
```

## Service Definitions

### Default Services

| Service | Port | Subdomain | Description |
|---------|------|-----------|-------------|
| claude-app | 3000 | claude-dev | Main application |
| claude-api | 3001 | claude-api | API server |
| claude-ui | 5173 | claude-ui | Frontend/UI |
| claude-monitoring | 3000 | claude-monitoring | Monitoring dashboard |
| claude-terminal | 3002 | claude-terminal | Terminal server |
| claude-mobile | 5555 | claude-mobile | Mobile access |

### Adding Custom Services

```bash
# Interactive service configuration
claude-code-tunnel-config --service my-service

# Or edit config file directly
claude-code-tunnel-config --edit
```

## Health Monitoring

### Health Check Configuration

```json
{
  "health_check": {
    "enabled": true,
    "path": "/health",
    "interval": 30000,
    "timeout": 5000
  }
}
```

### Health Check Endpoints

Services should implement health check endpoints:

```javascript
// Express.js example
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'claude-app',
    version: '1.0.0'
  });
});
```

## QR Code Generation

QR codes are automatically generated for mobile access:

```bash
# Generate QR codes for all services
claude-code-tunnel-status --qr-all

# Generate QR code for specific service
claude-code-tunnel-status --qr claude-app
```

QR codes are saved to `logs/qr-codes/` directory.

## Monitoring and Metrics

### ngrok Web Interface

Access the ngrok web interface at `http://localhost:4040` for:
- Real-time request inspection
- Traffic metrics
- Connection details
- Error logs

### Custom Metrics

```bash
# View detailed metrics
claude-code-tunnel-status --metrics

# JSON output for integration
claude-code-tunnel-status --json --metrics
```

## Troubleshooting

### Common Issues

1. **ngrok not found**
   ```bash
   # Install ngrok
   # Windows: choco install ngrok
   # macOS: brew install ngrok
   # Linux: snap install ngrok
   ```

2. **Authentication failed**
   ```bash
   # Set auth token
   export NGROK_AUTHTOKEN=your_token_here
   # Or configure ngrok directly
   ngrok config add-authtoken your_token_here
   ```

3. **Port conflicts**
   ```bash
   # Check what's using the port
   netstat -tulpn | grep :4040
   # Kill process or use different port
   ```

4. **Health checks failing**
   ```bash
   # Check service health manually
   curl http://localhost:3000/health
   # Disable health checks temporarily
   claude-code-tunnel-start --no-health-checks
   ```

### Debug Mode

```bash
# Enable verbose logging
TUNNEL_LOG_LEVEL=debug claude-code-tunnel-start

# Check logs
tail -f logs/tunnel-manager.log
tail -f logs/ngrok.log
```

### Reset Configuration

```bash
# Reset to defaults
claude-code-tunnel-config --reset

# Validate configuration
claude-code-tunnel-config --validate
```

## Security Considerations

1. **Authentication**: Enable auth for sensitive services
2. **Token Security**: Keep ngrok tokens secure
3. **Network Access**: Tunnels expose services to internet
4. **Rate Limiting**: Configure rate limits in production
5. **Monitoring**: Monitor tunnel access logs

## Integration

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Start Tunnels for Testing
  run: |
    export NGROK_AUTHTOKEN=${{ secrets.NGROK_TOKEN }}
    claude-code-tunnel-start --quiet
    
- name: Run E2E Tests
  run: |
    TUNNEL_URL=$(claude-code-tunnel-status --json | jq -r '.tunnels["claude-app"].url')
    npm run test:e2e -- --base-url=$TUNNEL_URL
    
- name: Stop Tunnels
  run: claude-code-tunnel-stop --quiet
```

### Programmatic Usage

```javascript
import TunnelManager from './lib/tunnel/tunnel-manager.js';

const manager = new TunnelManager();

// Start tunnels
await manager.start();

// Get status
const status = await manager.getTunnelStatus();

// Stop tunnels
await manager.stop();
```

## NPM Scripts

Add to your `package.json`:

```json
{
  "scripts": {
    "tunnel:start": "claude-code-tunnel-start",
    "tunnel:stop": "claude-code-tunnel-stop",
    "tunnel:status": "claude-code-tunnel-status",
    "tunnel:restart": "claude-code-tunnel-restart",
    "dev:remote": "concurrently \"npm run dev\" \"npm run tunnel:start\""
  }
}
```

## Support

For issues and questions:
1. Check logs in `logs/tunnel-manager.log`
2. Validate configuration with `--validate`
3. Try `--force` restart for stuck processes
4. Reset configuration if corrupted

## License

Part of Claude Code Dev Stack - MIT License