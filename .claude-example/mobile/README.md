# Claude Code V3+ Mobile Access 📱

Secure one-liner mobile access to your Claude Code Dev Stack V3+ from any Android/iOS device.

## 🚀 **One-Line Setup for Samsung Galaxy S25 Edge**

### **Windows:**
```cmd
launch_mobile.bat
```

### **Linux/macOS:**
```bash
./launch_mobile.sh
```

### **Python Direct:**
```bash
python .claude-example/mobile/launch_mobile.py
```

## 🔒 **Security Features**

- ✅ **HTTPS Tunnel Encryption** (TLS 1.3)
- ✅ **Session-Based Authentication** (24-hour tokens)
- ✅ **Rate Limiting** (10 attempts/minute per IP)
- ✅ **Auto-Expiring Sessions** (24 hours)
- ✅ **Secure Token Generation** (32-byte cryptographic tokens)
- ✅ **IP Validation** (prevents session hijacking)
- ✅ **QR Code Access** (no typing URLs)

## 📱 **What You Get**

When you run the one-liner, it:

1. **🔐 Generates secure auth token** (cryptographically strong)
2. **🌐 Starts dashboard** with authentication protection
3. **🚇 Creates tunnel** (ngrok/Cloudflare with auto-fallback)
4. **📱 Sends to your phone** via Pushover/Telegram
5. **📊 Displays QR code** for instant access
6. **🔄 Monitors system** until you stop it

## 🎯 **Access From Samsung Galaxy S25 Edge**

### **Method 1: QR Code (Recommended)**
1. Run the one-liner command
2. Scan QR code with camera app
3. Opens Samsung Internet with full dashboard access

### **Method 2: Push Notification**
1. Notification appears on your phone
2. Tap to open secure URL
3. Full V3+ dashboard access

### **Method 3: Manual URL**
1. Copy URL + auth token from terminal
2. Open Samsung Internet Browser
3. Navigate to: `https://xyz.ngrok.io?auth=token`

## 🎛️ **Dashboard Features on Mobile**

- **📊 Real-time System Metrics** - CPU, Memory, Disk usage
- **🤖 Agent Monitoring** - All 28 agents status and activity
- **🔧 Hook Status** - 28 hooks real-time monitoring
- **🎭 MCP Playwright Sessions** - Browser automation viewing
- **🔒 Security Scans** - Vulnerability detection results
- **📈 Performance Charts** - Agent execution and token usage
- **📋 Live Logs** - Real-time system logs
- **🔔 Alert Center** - System notifications and warnings

## ⚙️ **Configuration**

### **Required Environment Variables:**
```bash
# For phone notifications (optional but recommended)
set PUSHOVER_TOKEN=your_pushover_token
set PUSHOVER_USER=your_pushover_user

# Or Telegram (alternative)
set TELEGRAM_BOT_TOKEN=your_bot_token
set TELEGRAM_CHAT_ID=your_chat_id

# For ngrok tunnels (get from ngrok.com)
set NGROK_TOKEN=your_ngrok_token
```

### **Command Options:**
```bash
python launch_mobile.py --help

Options:
  --no-phone      Don't send to phone
  --no-qr         Don't generate QR code
  --port 8080     Custom dashboard port
```

## 🛡️ **Security Best Practices**

### **Token Management:**
- Tokens expire automatically after 24 hours
- Maximum 5 concurrent sessions per device
- Rate limiting prevents brute force attacks
- Sessions tied to IP addresses

### **Network Security:**
- All traffic encrypted via HTTPS (TLS 1.3)
- ngrok/Cloudflare provide secure tunnels
- No credentials stored in browser
- Session cookies are HTTP-only and secure

### **Mobile Security:**
- Use Samsung Internet (recommended) or Chrome
- Enable biometric app locks
- Use secure WiFi networks
- Log out when finished

## 🔧 **Troubleshooting**

### **"Command not found" errors:**
```bash
# Install dependencies
pip install flask flask-socketio qrcode[pil] requests psutil
```

### **Tunnel fails to start:**
```bash
# Set ngrok token
set NGROK_TOKEN=your_token_from_ngrok.com
```

### **No phone notifications:**
```bash
# Setup Pushover (recommended - $5 one-time)
# 1. Install Pushover app on phone
# 2. Get API token from pushover.net
# 3. Set environment variables

set PUSHOVER_TOKEN=your_token
set PUSHOVER_USER=your_user_key
```

### **Authentication errors:**
```bash
# Check auth status
python .claude-example/mobile/mobile_auth.py stats

# Clean expired sessions
python .claude-example/mobile/mobile_auth.py cleanup
```

### **Dashboard not loading:**
```bash
# Check if dashboard is running
curl http://localhost:8080/api/auth/status

# Check tunnel status
python .claude-example/tunnels/tunnel_manager.py status
```

## 📊 **Usage Examples**

### **Quick Start:**
```bash
# Basic launch (Windows)
launch_mobile.bat

# Basic launch (Linux/macOS)
./launch_mobile.sh
```

### **Custom Configuration:**
```bash
# Custom port, no phone notification
python launch_mobile.py --port 9090 --no-phone

# Generate QR only, no tunnel
python launch_mobile.py --no-phone
```

### **Authentication Management:**
```bash
# Generate manual token
python mobile_auth.py generate

# List active sessions
python mobile_auth.py sessions

# Revoke specific token
python mobile_auth.py revoke <token>
```

## 🔗 **Integration with V3+ Features**

The mobile access integrates seamlessly with all V3+ features:

- **🎵 Audio Notifications** → **📱 Push Notifications**
- **🤖 Agent Orchestration** → **📊 Real-time Monitoring**
- **🔧 Quality Tools** → **📈 Performance Dashboards**
- **🛡️ Security Scanning** → **🔒 Security Status**
- **🌐 MCP Integrations** → **📱 Browser Session Viewing**

## 🎯 **Perfect for Samsung Galaxy S25 Edge**

This system is optimized for the Samsung Galaxy S25 Edge:

- **📱 Responsive design** for Edge display
- **✋ Touch-friendly controls** 
- **🖊️ S Pen support** for precise interaction
- **📱 Edge panel integration** (planned)
- **🖥️ Samsung DeX support** for desktop mode
- **🔄 Multi-window support** for multitasking

## 🚀 **What This Enables**

With secure mobile access, you can:

- **☕ Monitor projects** from coffee shops
- **✈️ Check progress** while traveling  
- **🚗 Get notifications** during commutes
- **🏠 Quick fixes** from anywhere in house
- **🌙 Late night checks** without disturbing setup
- **📱 Demo capabilities** to colleagues/clients

Your Samsung Galaxy S25 Edge becomes a **powerful remote development monitoring and control center** for your entire Claude Code V3+ stack!

---

## 🔐 **Security Note**

This mobile access system provides **enterprise-grade security** while maintaining **ease of use**. All communications are encrypted, sessions are time-limited, and access is properly authenticated. Perfect for professional development environments requiring both security and convenience.

**Built for developers who code everywhere** 🌍