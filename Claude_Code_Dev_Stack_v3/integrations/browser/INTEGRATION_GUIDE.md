# Claude Code Browser Integration Guide

## Overview

This integration seamlessly combines the Claude Code Browser by @zainhoda (AGPL-3.0) with the Claude Code Dev Stack v3.0 using an adapter pattern that maintains license compliance while extending functionality.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Dev Stack v3.0 PWA                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Agent Dash    │  │ Browser Monitor │  │ Task Monitor │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│               │                │                │            │
│               └────────────────┼────────────────┘            │
│                                │                             │
└────────────────────────────────┼─────────────────────────────┘
                                 │ WebSocket (ws://localhost:8081/ws)
┌────────────────────────────────┼─────────────────────────────┐
│            Dev Stack API Server (Port 8081)                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ /api/devstack/* │  │ WebSocket Hub   │  │ Attribution  │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│               │                │                │            │
│               └────────────────┼────────────────┘            │
│                                │                             │
└────────────────────────────────┼─────────────────────────────┘
                                 │ HTTP Proxy
┌────────────────────────────────┼─────────────────────────────┐
│        Original Claude Code Browser (Port 8080)             │
│                    by @zainhoda (AGPL-3.0)                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Project List  │  │ Session Viewer  │  │ Todo Tracker │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## License Compliance

### Original Work Attribution
- **Author**: @zainhoda
- **Project**: Claude Code Browser
- **License**: AGPL-3.0
- **Source**: https://github.com/zainhoda/claude-code-browser

### Integration Compliance
- **Adapter Pattern**: Maintains separation between original and extended code
- **License Compatibility**: AGPL-3.0 maintained throughout
- **Attribution Preservation**: Original author credited in all interfaces
- **Source Availability**: Original source remains unchanged and accessible

## Installation & Setup

### Prerequisites

1. **Go** (latest version)
   ```bash
   # Check if Go is installed
   go version
   ```

2. **Python 3.8+** with pip
   ```bash
   # Check Python version
   python --version
   ```

3. **Claude Code Browser Source** (already included in clones/)

### Quick Setup

1. **Install Python Dependencies**
   ```bash
   cd integrations/browser/
   pip install -r requirements.txt
   ```

2. **Check Dependencies**
   ```bash
   python start_integration.py --check-deps
   ```

3. **Create Configuration**
   ```bash
   python start_integration.py --create-config
   ```

4. **Start Integration**
   ```bash
   python start_integration.py
   ```

## Usage

### Starting the Integration

#### Basic Start
```bash
cd integrations/browser/
python start_integration.py
```

#### Custom Ports
```bash
python start_integration.py --browser-port 9000 --api-port 9001
```

#### Disable Streaming
```bash
python start_integration.py --no-streaming
```

#### With Configuration File
```bash
python start_integration.py --config my_config.json
```

### Available Services

Once started, the following services are available:

| Service | URL | Description |
|---------|-----|-------------|
| **Original Browser** | http://localhost:8080 | Full Claude Code Browser by @zainhoda |
| **Dev Stack API** | http://localhost:8081 | Extended API with Dev Stack features |
| **WebSocket** | ws://localhost:8081/ws | Real-time updates |
| **Health Check** | http://localhost:8081/health | Service health monitoring |
| **Attribution** | http://localhost:8081/api/attribution | License and attribution info |

### PWA Integration

The browser monitor is integrated into the Dev Stack PWA:

1. **Access via PWA**: Navigate to `/browser` in the Dev Stack PWA
2. **Real-time Updates**: WebSocket connection provides live metrics
3. **Project Browsing**: View and access Claude Code projects
4. **Session Analysis**: Deep dive into conversation sessions

## API Endpoints

### Dev Stack Extensions

#### Agent Management
```http
GET /api/devstack/agents
POST /api/devstack/agents/{name}/activate
POST /api/devstack/agents/{name}/deactivate
```

#### Task Monitoring
```http
GET /api/devstack/tasks
POST /api/devstack/tasks
PUT /api/devstack/tasks/{id}
```

#### Hook System
```http
GET /api/devstack/hooks
POST /api/devstack/hooks/trigger
```

#### Audio Events
```http
GET /api/devstack/audio
POST /api/devstack/audio/event
```

### Browser Proxy Endpoints

All original browser endpoints are available through the proxy:

```http
GET /api/browser/projects      # Proxied to original browser
GET /api/browser/project/{name}
GET /api/browser/session/{project}/{uuid}
```

## Configuration

### Default Configuration

The system creates a `browser_config.json` file with default settings:

```json
{
  "browser": {
    "browser_port": 8080,
    "devstack_port": 8081,
    "go_binary_path": "clones/claude-code-browser/main",
    "claude_projects_path": "~/.claude/projects",
    "streaming_enabled": true,
    "websocket_enabled": true
  },
  "streaming": {
    "webrtc_enabled": true,
    "novnc_enabled": false,
    "screen_capture_fps": 30,
    "max_resolution": [1920, 1080],
    "compression_quality": 80,
    "webrtc_port": 8082,
    "novnc_port": 8083
  }
}
```

### Customizing Configuration

Edit the configuration file to adjust settings:

```json
{
  "browser": {
    "browser_port": 9000,
    "devstack_port": 9001
  }
}
```

Then start with the custom config:
```bash
python start_integration.py --config my_config.json
```

## Streaming Capabilities

### WebRTC Streaming (Optional)

Real-time screen sharing of the browser interface:

- **Endpoint**: ws://localhost:8082
- **Features**: Live video stream, remote interaction
- **Use Case**: Remote collaboration, presentation

### noVNC Access (Optional)

Web-based VNC access to the browser:

- **Endpoint**: http://localhost:8083
- **Features**: Full remote desktop in browser
- **Use Case**: Remote access, screen sharing

## Troubleshooting

### Common Issues

#### 1. Go Binary Not Found
```
❌ Failed to start browser server: Go binary not found
```
**Solution**: Build the Go binary manually:
```bash
cd clones/claude-code-browser/
go build -o main .
```

#### 2. Port Already in Use
```
❌ Failed to start API server: Port 8081 already in use
```
**Solution**: Use different ports:
```bash
python start_integration.py --api-port 8082
```

#### 3. Claude Projects Not Found
```
⚠️ Claude projects directory not found
```
**Solution**: This is normal if Claude Code hasn't been used yet. The directory will be created when you first use Claude Code.

#### 4. WebSocket Connection Failed
```
🔌 WebSocket error: Connection refused
```
**Solution**: Ensure the integration server is running and check firewall settings.

### Debug Mode

Run with verbose logging for detailed information:
```bash
python start_integration.py --verbose
```

### Dependency Check

Verify all dependencies are installed:
```bash
python start_integration.py --check-deps
```

### Manual Dependency Installation

If automatic installation fails:
```bash
pip install aiohttp aiofiles websockets requests Pillow numpy opencv-python
```

## Development

### Project Structure

```
integrations/browser/
├── README.md                 # Overview and setup
├── INTEGRATION_GUIDE.md      # This guide
├── requirements.txt          # Python dependencies
├── start_integration.py      # Main launcher
├── attribution.py            # License compliance
├── adapter.py               # Browser adapter
├── api_endpoints.py         # Dev Stack API
├── streaming.py             # WebRTC/noVNC support
└── server_wrapper.py        # Extended server
```

### Extending the Integration

To add new Dev Stack features:

1. **Add API Endpoint** in `api_endpoints.py`:
   ```python
   async def my_new_endpoint(self, request):
       return web.json_response({"status": "success"})
   ```

2. **Register Route**:
   ```python
   self.app.router.add_get('/api/devstack/my-feature', self.my_new_endpoint)
   ```

3. **Update WebSocket** for real-time updates:
   ```python
   await self._broadcast_update('my-feature-update', data)
   ```

### Contributing

1. Maintain AGPL-3.0 license compatibility
2. Preserve original attribution to @zainhoda
3. Use adapter pattern to separate extensions
4. Document all changes and additions
5. Test with original browser functionality

## License & Attribution

This integration maintains full compliance with the AGPL-3.0 license:

- **Original Work**: Claude Code Browser by @zainhoda
- **Integration**: Claude Code Dev Stack v3.0 adapter
- **License**: AGPL-3.0 for all components
- **Source**: Available and documented
- **Attribution**: Preserved and displayed in all interfaces

The integration uses an adapter pattern to extend functionality while keeping the original codebase unchanged and properly attributed.

## Support

### Getting Help

1. **Check Dependencies**: `python start_integration.py --check-deps`
2. **View Logs**: Use `--verbose` flag for detailed logging
3. **Health Check**: Visit http://localhost:8081/health
4. **Attribution**: View license info at http://localhost:8081/api/attribution

### Reporting Issues

When reporting issues, include:

1. Operating system and Python version
2. Full error message with `--verbose` flag
3. Configuration file contents
4. Dependency check output

### Original Project

For issues with the core browser functionality, refer to the original project:
- **Repository**: https://github.com/zainhoda/claude-code-browser
- **Author**: @zainhoda
- **License**: AGPL-3.0