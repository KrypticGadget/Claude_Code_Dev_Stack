# Claude Code Mobile Launcher - V3.0 Enhanced

This directory contains bulletproof launchers for the Claude Code mobile access system with proper virtual environment management and Windows compatibility.

## 🚀 Quick Start

Choose any launcher method below - they all do the same thing:

### Option 1: Windows Batch File (Recommended)
```cmd
launch_mobile.bat
```

### Option 2: PowerShell Script  
```powershell
.\launch_mobile.ps1
```

### Option 3: Direct Python (if venv is already set up)
```cmd
python launch_mobile.py
```

## 📁 File Overview

| File | Purpose | Platform |
|------|---------|----------|
| `launch_mobile.py` | Main Python launcher with enhanced virtual environment management | Cross-platform |
| `launch_mobile.bat` | Windows batch launcher with bulletproof setup | Windows |
| `launch_mobile.ps1` | PowerShell launcher with advanced error handling | Windows |
| `requirements.txt` | Python dependencies for the mobile system | All |

## 🔧 What The Launchers Do

All launchers follow the same bulletproof workflow:

### 1. **Virtual Environment Management**
- ✅ Check if `.venv` directory exists
- ✅ Create virtual environment if missing
- ✅ Verify virtual environment Python executable
- ✅ Automatically switch to virtual environment if not already active
- ✅ Upgrade pip to latest version

### 2. **Dependency Installation** 
- ✅ Install from `requirements.txt` if available
- ✅ Fallback to individual package installation if needed
- ✅ Handle installation timeouts and errors gracefully
- ✅ Continue with essential packages if some fail

### 3. **Service Startup** (in correct order)
- ✅ **QR Server** on port 5555 (for displaying access info)
- ✅ **ttyd Terminal** on port 7681 (web-based terminal access)  
- ✅ **Dashboard** on port 8080 (main mobile interface)
- ✅ **Secure Tunnel** via ngrok (public access URL)

### 4. **Error Handling**
- ✅ Comprehensive error checking at every step
- ✅ Fallback mechanisms for failed operations
- ✅ Clear error messages and troubleshooting hints
- ✅ Proper cleanup on exit/interruption

## 🎯 Features

### Enhanced Virtual Environment Support
- **Automatic Creation**: Creates `.venv` if missing
- **Path Validation**: Ensures Python executable exists
- **Dependency Management**: Installs all required packages
- **Windows Compatibility**: Handles Windows paths correctly

### Bulletproof Service Management
- **Sequential Startup**: Services start in correct dependency order
- **Health Checks**: Verifies each service starts successfully  
- **Process Monitoring**: Monitors running services
- **Graceful Shutdown**: Clean process termination

### Advanced Error Recovery
- **Fallback Dashboards**: Simple → Complex → Enhanced dashboards
- **Package Installation**: requirements.txt → individual → essential only
- **Connection Handling**: Multiple tunnel providers supported
- **Timeout Management**: Prevents hanging operations

## 📱 Mobile Access Flow

1. **Launch**: Run any launcher script
2. **Setup**: Virtual environment and dependencies installed automatically
3. **Services**: All services start in correct order
4. **Access Portal**: Visit `http://localhost:5555` for:
   - QR code for mobile scanning
   - Tunnel URL for remote access  
   - Auth token for secure connection
   - Direct mobile links

5. **Mobile Dashboard**: Access via tunnel URL for:
   - Real-time system monitoring
   - File system access
   - Terminal interface (ttyd)
   - Git integration

## 🔒 Security Features

- **Token Authentication**: Secure auth tokens for all connections
- **Session Management**: Time-limited access tokens
- **Tunnel Encryption**: All traffic encrypted via ngrok/CloudFlare
- **Local Isolation**: Services bound to localhost by default

## 🛠 Troubleshooting

### Common Issues

**Virtual Environment Issues:**
```cmd
# Delete and recreate if corrupted
rmdir /s .venv
launch_mobile.bat
```

**Dependency Installation Failures:**
```cmd
# Manual installation in virtual environment
.venv\Scripts\python.exe -m pip install -r requirements.txt --upgrade
```

**Port Conflicts:**
```cmd
# Use different ports
launch_mobile.py --port 9090
```

**ngrok Authentication:**
```cmd
# Set auth token environment variable
set NGROK_AUTH_TOKEN=your_token_here
launch_mobile.bat
```

### Advanced Options

**Python Launcher Options:**
```cmd
python launch_mobile.py --help
python launch_mobile.py --no-phone --no-qr --port 9090
```

**PowerShell Options:**
```powershell
.\launch_mobile.ps1 -NoPhone -NoQr -Port 9090
```

## 📊 System Requirements

- **Python**: 3.8+ (3.9+ recommended)
- **OS**: Windows 10/11 (Linux/macOS compatible with Python launcher)  
- **Memory**: 256MB+ available RAM
- **Network**: Internet connection for ngrok tunnel
- **Storage**: 100MB+ for virtual environment and dependencies

## 🔄 Updates

The launchers automatically:
- ✅ Download latest components from GitHub  
- ✅ Update dependencies to compatible versions
- ✅ Maintain backward compatibility with existing setups
- ✅ Preserve user configurations and auth tokens

## 📞 Support

For issues:
1. Check the console output for specific error messages
2. Try deleting `.venv` directory and relaunching  
3. Ensure Python 3.8+ is installed and in PATH
4. Verify ngrok auth token is valid
5. Check Windows firewall/antivirus settings

---

**DevOps Engineering Agent V3.0** - Bulletproof infrastructure automation for seamless mobile development workflows.