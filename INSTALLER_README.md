# Claude Code Dev Stack v3.0 - One-Line Installer

Complete automation scripts for cross-platform installation of Claude Code Dev Stack v3.0. These installers clone from GitHub, install all dependencies, setup virtual environments, configure services, and validate the installation.

## ⚡ Quick Installation

### Windows (PowerShell)
```powershell
# Run from PowerShell as Administrator (recommended)
irm https://raw.githubusercontent.com/yourusername/Claude_Code_Dev_Stack_v3/main/install.ps1 | iex
```

### Linux/macOS (Bash)
```bash
# One-line installation
curl -fsSL https://raw.githubusercontent.com/yourusername/Claude_Code_Dev_Stack_v3/main/install.sh | bash

# Alternative with wget
wget -qO- https://raw.githubusercontent.com/yourusername/Claude_Code_Dev_Stack_v3/main/install.sh | bash
```

## 🚀 What Gets Installed

### Core Components
- **28 AI Agents** - Specialized development agents
- **28 Hook System** - Automated development workflows  
- **18 Slash Commands** - Quick development commands
- **Audio System** - 102 phase-aware notification sounds
- **Real-time Dashboard** - Live monitoring interface
- **Mobile Interface** - Flutter-based mobile app
- **Web Application** - Progressive Web App interface

### Integrated Third-Party Tools
- **Claude Code Browser** (@zainhoda) - Session monitoring
- **Mobile App** (@9cat) - Flutter mobile interface  
- **MCP Manager** (@qdhenry) - MCP server configuration
- **OpenAPI Generators** (@cnoe-io, @harsha-iiiv) - API generation
- **Claude Powerline** (@Owloops) - Advanced statusline
- **CC-Statusline** (@chongdashu) - Setup patterns

### Technical Stack
- **Python 3.8+** with virtual environment
- **Node.js 18+** with npm dependencies
- **Flask** web framework for API
- **React** frontend with Vite
- **Docker** support (optional)
- **Git** for version control

## 📋 Installation Process

### Automated Steps
1. **Dependency Detection** - Checks for required tools
2. **System Dependencies** - Auto-installs missing packages
3. **Repository Cloning** - Downloads latest code from GitHub
4. **Python Environment** - Creates isolated virtual environment
5. **Python Dependencies** - Installs all required packages
6. **Node.js Environment** - Sets up web application dependencies
7. **Service Configuration** - Creates .env and config files
8. **Directory Structure** - Creates necessary folders
9. **Installation Validation** - Comprehensive health checks
10. **Launcher Scripts** - Creates convenient startup scripts

### Installation Locations
- **Default**: `$HOME/Claude_Code_Dev_Stack_v3`
- **Windows**: `C:\Users\{Username}\Claude_Code_Dev_Stack_v3`
- **Linux/macOS**: `/home/{username}/Claude_Code_Dev_Stack_v3`

## ⚙️ Advanced Installation Options

### Windows PowerShell Parameters
```powershell
# Custom installation path
irm install.ps1 | iex -InstallPath "C:\Custom\Path"

# Different GitHub repository
irm install.ps1 | iex -GitHubRepo "yourfork/Claude_Code_Dev_Stack_v3"

# Skip validation tests
irm install.ps1 | iex -SkipValidation

# Verbose logging
irm install.ps1 | iex -Verbose
```

### Linux/macOS Environment Variables
```bash
# Custom installation path
INSTALL_DIR="$HOME/custom/path" bash install.sh

# Different GitHub repository  
GITHUB_REPO="yourfork/Claude_Code_Dev_Stack_v3" bash install.sh

# Different branch
BRANCH="development" bash install.sh

# Combine multiple options
INSTALL_DIR="/opt/claude-stack" GITHUB_REPO="yourfork/repo" bash install.sh
```

## 🔧 Manual Installation

If the one-liner fails, you can run the installation manually:

### Windows
```powershell
# Download installer
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/yourusername/Claude_Code_Dev_Stack_v3/main/install.ps1" -OutFile "install.ps1"

# Run with parameters
.\install.ps1 -InstallPath "C:\Claude\Stack" -Verbose
```

### Linux/macOS
```bash
# Download installer
curl -fsSL -o install.sh https://raw.githubusercontent.com/yourusername/Claude_Code_Dev_Stack_v3/main/install.sh
chmod +x install.sh

# Run with environment variables
INSTALL_DIR="$HOME/claude-stack" ./install.sh
```

## 📊 System Requirements

### Minimum Requirements
- **OS**: Windows 10+, Ubuntu 18.04+, macOS 10.15+, or any modern Linux distro
- **RAM**: 4GB (8GB recommended)
- **Storage**: 2GB free space
- **Network**: Internet connection for downloads

### Required Software (Auto-installed)
- **Git** - Version control
- **Python 3.8+** - Runtime environment
- **Node.js 18+** - Web application runtime
- **pip** - Python package manager
- **npm** - Node.js package manager

### Optional Software
- **Docker** - For containerized deployment
- **curl/wget** - For downloads (one usually available)

## 🎯 Post-Installation

### Quick Start
```bash
# Navigate to installation
cd ~/Claude_Code_Dev_Stack_v3

# Start all services
./start.sh        # Linux/macOS
start.ps1         # Windows PowerShell
start.bat         # Windows Command Prompt
```

### Service URLs
- **📱 Mobile Interface**: http://localhost:8080
- **🌐 Web Application**: http://localhost:3000  
- **📊 Dashboard**: http://localhost:8081
- **🔌 API Server**: http://localhost:8000

### Configuration
1. **Edit `.env` file** - Add your CLAUDE_API_KEY
2. **Configure services** - Adjust ports and settings
3. **Customize agents** - Modify agent configurations
4. **Setup hooks** - Configure automation workflows

## 🛠️ Troubleshooting

### Common Issues

#### Permission Errors (Windows)
```powershell
# Run PowerShell as Administrator
# Or enable script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Missing Dependencies (Linux)
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y git python3 python3-pip nodejs npm

# CentOS/RHEL
sudo yum install -y git python3 python3-pip nodejs npm

# Arch Linux
sudo pacman -S git python nodejs npm
```

#### Python Virtual Environment Issues
```bash
# Ensure python3-venv is installed (Linux)
sudo apt-get install python3-venv

# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Node.js Issues
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf apps/web/node_modules
cd apps/web && npm install
```

#### Port Conflicts
```bash
# Check what's using ports
netstat -tulpn | grep -E "(3000|8000|8080|8081)"

# Kill processes on specific ports
sudo lsof -ti:3000 | xargs kill -9
```

### Validation Failures

If validation tests fail, check:
1. **Log files** - Located in `/tmp/claude-stack-install-*.log`
2. **Missing dependencies** - Rerun dependency installation
3. **Network connectivity** - Ensure GitHub access
4. **Permissions** - Check file/directory permissions
5. **Disk space** - Ensure sufficient storage

### Manual Recovery
```bash
# Navigate to installation directory
cd ~/Claude_Code_Dev_Stack_v3

# Rerun Python setup
python3 setup_environment.py

# Reinstall Node.js dependencies
cd apps/web && npm install && cd ../..

# Recreate configuration
cp .env.example .env  # Edit with your settings

# Test individual components
source venv/bin/activate
python -c "import flask, requests; print('Python OK')"
cd apps/web && npm run build && cd ../..
```

## 📈 Installation Validation

The installer runs comprehensive validation tests:

### Python Environment Tests
- ✅ Virtual environment creation
- ✅ Core package imports (flask, requests, yaml)
- ✅ Requirements installation
- ✅ Script execution permissions

### Node.js Environment Tests  
- ✅ Package.json presence
- ✅ Node modules installation
- ✅ Build process execution
- ✅ Development server startup

### Service Configuration Tests
- ✅ Environment file creation
- ✅ Directory structure setup
- ✅ Status file initialization
- ✅ Permission validation

### Integration Tests
- ✅ Cross-service communication
- ✅ Port availability
- ✅ API endpoint responses
- ✅ Dashboard accessibility

## 🔒 Security Considerations

### Safe Installation Practices
- **Review scripts** before running (especially one-liners)
- **Use HTTPS** for all downloads
- **Verify checksums** when available
- **Run with minimal privileges** when possible

### What the Installer Does
- ✅ Downloads from official GitHub repository
- ✅ Uses package managers for dependencies
- ✅ Creates isolated virtual environments
- ✅ Generates secure random secrets
- ✅ Sets appropriate file permissions

### What the Installer Doesn't Do
- ❌ Modify system-wide configurations
- ❌ Install global packages (unless explicitly needed)
- ❌ Change system security settings
- ❌ Access external networks beyond GitHub/package repos
- ❌ Store or transmit sensitive information

## 🚨 Emergency Uninstall

### Complete Removal
```bash
# Stop all services
cd ~/Claude_Code_Dev_Stack_v3
./stop.sh 2>/dev/null || true

# Remove installation directory
rm -rf ~/Claude_Code_Dev_Stack_v3

# Remove logs (optional)
rm -f /tmp/claude-stack-install-*.log

# Remove system packages (optional, use with caution)
# This will remove packages that might be used by other applications
# sudo apt-get remove --purge nodejs npm python3-pip
```

### Partial Cleanup
```bash
# Keep source code, remove virtual environments
cd ~/Claude_Code_Dev_Stack_v3
rm -rf venv apps/web/node_modules

# Keep installation, remove logs only
rm -f /tmp/claude-stack-install-*.log logs/*.log
```

## 📚 Additional Resources

### Documentation
- **README.md** - Project overview and quick start
- **docs/** - Comprehensive documentation
- **CHANGELOG.md** - Version history and updates
- **CONTRIBUTING.md** - Development guidelines

### Community
- **GitHub Issues** - Bug reports and feature requests
- **Discussions** - Community support and ideas
- **Wiki** - Additional documentation and tutorials

### Development
- **Code Style** - Black (Python), Prettier (TypeScript)
- **Testing** - pytest (Python), Vitest (TypeScript)
- **Linting** - flake8 (Python), ESLint (TypeScript)

---

## 💝 Attribution

This installer integrates and sets up these excellent open-source projects:

- **Claude Code Browser** by @zainhoda
- **Claude Code Mobile App** by @9cat  
- **MCP Manager** by @qdhenry
- **OpenAPI MCP Codegen** by @cnoe-io
- **OpenAPI MCP Generator** by @harsha-iiiv
- **Claude Powerline** by @Owloops
- **CC-Statusline** by @chongdashu

All original licenses and attributions are preserved. See [CREDITS.md](CREDITS.md) for detailed attribution.

---

**Support**: For installation issues, check GitHub issues or create a new issue with your system details and error logs.