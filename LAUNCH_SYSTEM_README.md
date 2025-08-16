# Claude Code Dev Stack v3.0 Master Launch System

## Overview

The Claude Code Dev Stack v3.0 Master Launch System provides a single command to orchestrate all services with proper dependency management, health checking, and graceful shutdown.

## 🚀 Quick Start

### Windows (PowerShell)
```powershell
# Full system launch
.\claude-start.ps1

# Core services only
.\claude-start.ps1 -Mode core

# Web application with auto-browser
.\claude-start.ps1 -Mode web -AutoBrowser

# Mobile interface, local only
.\claude-start.ps1 -Mode mobile -LocalOnly

# Debug mode with verbose logging
.\claude-start.ps1 -Mode debug -LogLevel debug
```

### Linux/macOS (Bash)
```bash
# Full system launch
./claude-start.sh

# Core services only
./claude-start.sh --mode core

# Web application with auto-browser
./claude-start.sh --mode web --auto-browser

# Mobile interface, local only
./claude-start.sh --mode mobile --local-only

# Debug mode with verbose logging
./claude-start.sh --mode debug --log-level debug
```

## 📋 Launch Modes

### Full Mode (Default)
- ✅ Environment validation
- ✅ Virtual environment setup
- ✅ Core services (Dashboard, MCP servers)
- ✅ Web application (React PWA)
- ✅ Mobile interfaces with QR codes
- ✅ Terminal tools (ttyd server)
- ✅ Health monitoring

### Core Mode
- ✅ Environment validation
- ✅ Virtual environment setup
- ✅ Real-time dashboard
- ✅ MCP servers
- ✅ Health monitoring

### Web Mode
- ✅ Environment validation
- ✅ Node.js dependencies
- ✅ React PWA development server
- ✅ Auto-browser (optional)

### Mobile Mode
- ✅ Environment validation
- ✅ Python virtual environment
- ✅ Mobile dashboard
- ✅ QR code generation
- ✅ Tunnel setup (optional)

### Debug Mode
- ✅ Core services
- ✅ Terminal tools
- ✅ Enhanced logging
- ✅ Development utilities

## 🔧 Command Options

### PowerShell (`claude-start.ps1`)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `-Mode` | String | `full` | Launch mode: `full`, `core`, `web`, `mobile`, `debug` |
| `-SkipHealthCheck` | Switch | `false` | Skip health checks for faster startup |
| `-LogLevel` | String | `info` | Logging level: `debug`, `info`, `warn`, `error` |
| `-AutoBrowser` | Switch | `false` | Automatically open browser |
| `-CustomPort` | String | `""` | Custom port for main dashboard |
| `-LocalOnly` | Switch | `false` | Run in local-only mode (no tunnels) |

### Bash (`claude-start.sh`)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-m, --mode` | String | `full` | Launch mode: `full`, `core`, `web`, `mobile`, `debug` |
| `-s, --skip-health` | Flag | `false` | Skip health checks for faster startup |
| `-l, --log-level` | String | `info` | Logging level: `debug`, `info`, `warn`, `error` |
| `-b, --auto-browser` | Flag | `false` | Automatically open browser |
| `-p, --port` | String | `""` | Custom port for main dashboard |
| `--local-only` | Flag | `false` | Run in local-only mode (no tunnels) |
| `-h, --help` | Flag | - | Show help message |

## 🏗️ System Architecture

### Service Startup Order

1. **Environment Validation**
   - Check Python 3.8+
   - Check Node.js 16+
   - Check Git
   - Check Claude CLI (optional)
   - Verify project structure

2. **Virtual Environment Setup**
   - Create Python virtual environment
   - Install Python dependencies
   - Install Node.js dependencies
   - Verify package integrity

3. **Core Services**
   - Real-time dashboard (Flask-SocketIO)
   - System monitoring
   - Git activity tracking
   - File change watching

4. **MCP Servers**
   - Playwright MCP server
   - Brave Search MCP server
   - Custom MCP servers

5. **Web Application**
   - React PWA development server
   - Vite build system
   - Hot module replacement

6. **Mobile Interface**
   - Mobile dashboard
   - QR code generation
   - Tunnel management (ngrok)
   - Authentication system

7. **Terminal Tools**
   - ttyd web terminal
   - Command execution
   - Process monitoring

8. **Health Monitoring**
   - Service health checks
   - Automatic restart (planned)
   - Status reporting

### Port Management

| Service | Default Port | Auto-Discovery |
|---------|--------------|----------------|
| Dashboard | 8080 | ✅ |
| Web App | 3000 | ✅ |
| Mobile Interface | 8080 | ✅ |
| Terminal Server | 7681 | ✅ |
| QR Code Server | 5555 | ✅ |

## 🔍 Health Checking

### Automatic Health Checks

- **HTTP Health Checks**: Services expose health endpoints
- **Process Monitoring**: Monitor process status
- **Port Availability**: Ensure ports are accessible
- **Dependency Validation**: Check service dependencies

### Health Check Timeouts

- **Default Timeout**: 30 seconds
- **Web Services**: HTTP GET to health endpoint
- **Background Services**: Process status check
- **Skip Option**: Use `-SkipHealthCheck` for faster startup

## 📊 Monitoring and Logging

### Log Levels

- **DEBUG**: Detailed execution information
- **INFO**: General operational messages
- **WARN**: Warning conditions
- **ERROR**: Error conditions
- **SUCCESS**: Successful operations

### Log Files

```
logs/
├── real-time_dashboard.log
├── web_application.log
├── mobile_interface.log
├── terminal_server.log
└── *.pid files
```

### Status Reporting

- **Service Summary**: Total, running, failed services
- **Detailed Status**: Individual service status
- **Uptime Tracking**: System uptime display
- **Access URLs**: Available service endpoints

## 🛠️ Troubleshooting

### Common Issues

#### Environment Validation Fails
```bash
# Check Python version
python --version
python3 --version

# Check Node.js version
node --version
npm --version

# Check Git
git --version

# Check Claude CLI
claude --version
```

#### Port Conflicts
```bash
# Check port usage (Linux/macOS)
lsof -i :8080
netstat -tulpn | grep 8080

# Check port usage (Windows)
netstat -ano | findstr :8080
```

#### Virtual Environment Issues
```bash
# Remove and recreate Python venv
rm -rf .claude-example/mobile/.venv
python3 -m venv .claude-example/mobile/.venv

# Reinstall Node.js dependencies
cd Claude_Code_Dev_Stack_v3/apps/web
rm -rf node_modules package-lock.json
npm install
```

#### Service Startup Failures
```bash
# Check service logs
tail -f logs/real-time_dashboard.log
tail -f logs/web_application.log

# Debug mode startup
./claude-start.sh --mode debug --log-level debug
```

### Debug Commands

```bash
# Test environment manually
python3 -c "import flask, psutil, git; print('Python deps OK')"
node -e "console.log('Node.js OK')"

# Check service status
curl http://localhost:8080/api/status
curl http://localhost:3000

# Process monitoring
ps aux | grep python
ps aux | grep node
```

## 🔐 Security Considerations

### Authentication

- **Dashboard**: Token-based authentication
- **Mobile Access**: Secure token generation
- **Tunnel Access**: ngrok authentication required
- **Command Execution**: Whitelist-based command filtering

### Network Security

- **Local Binding**: Services bind to localhost by default
- **Tunnel Encryption**: All tunnel traffic encrypted
- **Token Expiry**: Authentication tokens expire after 24 hours
- **CORS Configuration**: Proper CORS headers for web services

### Process Security

- **User Permissions**: Runs with user permissions
- **Process Isolation**: Each service runs in separate process
- **Resource Limits**: Memory and CPU usage monitoring
- **Clean Shutdown**: Graceful service termination

## 🔄 Service Management

### Starting Services

```bash
# Start all services
./claude-start.sh

# Start specific mode
./claude-start.sh --mode core
```

### Stopping Services

- **Ctrl+C**: Graceful shutdown of all services
- **SIGTERM**: Handled by cleanup function
- **Force Stop**: Kill remaining processes

### Restarting Services

```bash
# Stop current instance (Ctrl+C)
# Then restart
./claude-start.sh --mode full
```

### Service Status

The launcher provides real-time status updates:

- **Green ✅**: Service running successfully
- **Red ❌**: Service failed to start
- **Yellow ⏰**: Service health check timeout
- **Gray ❓**: Unknown service status

## 📱 Mobile Access

### QR Code Generation

- **Automatic**: QR codes generated for mobile access
- **Local Network**: Works on same WiFi network
- **Tunnel Support**: ngrok tunnel for remote access
- **Samsung Galaxy S25 Edge**: Optimized for mobile browsers

### Mobile Dashboard Features

- **Real-time Monitoring**: Live system metrics
- **Git Activity**: Recent commits and status
- **File Changes**: Modified files tracking
- **Command Execution**: Remote command execution
- **Terminal Access**: Web-based terminal

## 🌐 Web Application

### React PWA Features

- **Progressive Web App**: Install as native app
- **Offline Support**: Service worker caching
- **Responsive Design**: Works on all screen sizes
- **Hot Reload**: Development server with HMR
- **TypeScript**: Full TypeScript support

### Development Features

- **Vite Build**: Fast development server
- **ESLint**: Code quality checking
- **Testing**: Vitest test runner
- **Component Library**: Lucide React icons

## 🔌 Integration Points

### Claude CLI Integration

- **MCP Servers**: Automatic MCP server management
- **Configuration**: Uses Claude CLI configuration
- **Authentication**: Claude CLI authentication

### System Integration

- **Git Integration**: Real-time git activity monitoring
- **File System**: File change watching
- **Process Monitoring**: System resource tracking
- **Network Monitoring**: Port and connectivity checking

## 📈 Performance Optimization

### Startup Optimization

- **Parallel Startup**: Services start concurrently
- **Health Check Optimization**: Configurable timeouts
- **Dependency Caching**: Virtual environment reuse
- **Process Pooling**: Efficient process management

### Runtime Optimization

- **Resource Monitoring**: CPU and memory tracking
- **Log Rotation**: Automatic log file management
- **Connection Pooling**: Efficient database connections
- **Caching**: In-memory caching for frequent operations

## 🤝 Contributing

### Adding New Services

1. Add service definition to startup functions
2. Implement health check endpoint
3. Add service to cleanup function
4. Update documentation

### Modifying Launch Modes

1. Edit mode selection in `parse_arguments()`
2. Add mode-specific logic in `main()`
3. Update help documentation
4. Test all combinations

### Platform Support

- **Windows**: PowerShell 5.1+ required
- **Linux**: Bash 4.0+ required
- **macOS**: Bash 3.2+ supported
- **WSL**: Full support in Windows Subsystem for Linux

## 📚 Additional Resources

- [Claude Code Dev Stack v3.0 Documentation](./CLAUDE_CODE_V3_MASTER_PLAN.md)
- [Technical Specifications](./CLAUDE_CODE_V3_TECHNICAL_SPECS.md)
- [Mobile Access Guide](./.claude-example/mobile/README.md)
- [Web Application Guide](./Claude_Code_Dev_Stack_v3/apps/web/README.md)

---

**Claude Code Dev Stack v3.0** - *Engineered for Developer Excellence*