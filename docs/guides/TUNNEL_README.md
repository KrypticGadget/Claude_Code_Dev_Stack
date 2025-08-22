# Claude Code Tunnel Management System

## Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Get ngrok Token
1. Sign up at [ngrok dashboard](https://dashboard.ngrok.com/signup)
2. Copy your auth token

### 3. Configure Environment
```bash
# Copy example file
cp .env.tunnel.example .env.tunnel

# Edit with your token
# Set NGROK_AUTHTOKEN=your_token_here
```

### 4. Start Tunnels
```bash
# Using CLI commands
claude-code-tunnel-start

# Using npm scripts  
npm run tunnel:start
```

## Available Commands

| Command | Description |
|---------|-------------|
| `claude-code-tunnel-start` | Start all tunnels |
| `claude-code-tunnel-stop` | Stop all tunnels |
| `claude-code-tunnel-status` | Check tunnel status |
| `claude-code-tunnel-restart` | Restart failed tunnels |
| `claude-code-tunnel-config` | Configure settings |

## NPM Scripts

| Script | Description |
|--------|-------------|
| `npm run tunnel:start` | Start tunnels |
| `npm run tunnel:stop` | Stop tunnels |
| `npm run tunnel:status` | Check status |
| `npm run tunnel:restart` | Restart tunnels |
| `npm run tunnel:config` | Configure |

## Quick Examples

```bash
# Start with token
claude-code-tunnel-start --token YOUR_TOKEN

# Check status with QR codes
claude-code-tunnel-status --qr-all

# Watch status (auto-refresh)
claude-code-tunnel-status --watch

# Copy URL to clipboard
claude-code-tunnel-status --copy claude-app

# Force restart all
claude-code-tunnel-restart --all

# Configure interactively
claude-code-tunnel-config --edit
```

## Default Services

| Service | Port | URL Pattern |
|---------|------|-------------|
| claude-app | 3000 | https://claude-dev.ngrok.io |
| claude-api | 3001 | https://claude-api.ngrok.io |
| claude-ui | 5173 | https://claude-ui.ngrok.io |
| claude-monitoring | 3000 | https://claude-monitoring.ngrok.io |
| claude-terminal | 3002 | https://claude-terminal.ngrok.io |
| claude-mobile | 5555 | https://claude-mobile.ngrok.io |

## Features

- ✅ **Multi-Service Tunneling**: Support for all Claude Code services
- ✅ **Health Monitoring**: Automatic health checks with recovery
- ✅ **QR Code Generation**: Mobile-friendly access codes
- ✅ **Cross-Platform**: Windows, macOS, and Linux support
- ✅ **Configuration Management**: Interactive configuration editor
- ✅ **Real-time Status**: Live tunnel monitoring with metrics
- ✅ **Automatic Recovery**: Auto-restart failed tunnels
- ✅ **Security**: Authentication and rate limiting support

## Troubleshooting

### ngrok not found
```bash
# Windows
choco install ngrok

# macOS
brew install ngrok

# Linux
snap install ngrok
```

### Authentication failed
```bash
# Set token environment variable
export NGROK_AUTHTOKEN=your_token_here

# Or configure ngrok directly
ngrok config add-authtoken your_token_here
```

### Check logs
```bash
# View tunnel manager logs
tail -f logs/tunnel-manager.log

# View ngrok logs
tail -f logs/ngrok.log
```

### Reset configuration
```bash
claude-code-tunnel-config --reset
```

## Documentation

Full documentation available in `docs/TUNNEL_MANAGEMENT.md`

## Validation

Run setup validation:
```bash
node scripts/validate-tunnel-setup.js
```

## Support

For issues:
1. Check validation: `node scripts/validate-tunnel-setup.js`
2. Check logs in `logs/` directory
3. Try force restart: `claude-code-tunnel-restart --force`
4. Reset config: `claude-code-tunnel-config --reset`

---

🎉 **Remote access made easy with Claude Code!**