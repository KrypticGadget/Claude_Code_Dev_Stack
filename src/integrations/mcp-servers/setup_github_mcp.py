#!/usr/bin/env python3
"""
GitHub MCP Setup Script
Automated setup and installation for GitHub MCP server

Features:
- Dependency installation
- Configuration generation
- Environment setup
- Docker preparation
- Validation and testing
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any

def print_header(title: str):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_step(step: str):
    """Print step information"""
    print(f"\n🔧 {step}")

def print_success(message: str):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message: str):
    """Print error message"""
    print(f"❌ {message}")

def print_warning(message: str):
    """Print warning message"""
    print(f"⚠️  {message}")

def run_command(command: List[str], description: str = "") -> bool:
    """Run command and return success status"""
    try:
        if description:
            print(f"   Running: {description}")
        
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {' '.join(command)}")
        print(f"   Error: {e.stderr}")
        return False
    except FileNotFoundError:
        print_error(f"Command not found: {command[0]}")
        return False

def check_python_version() -> bool:
    """Check Python version"""
    print_step("Checking Python version")
    
    if sys.version_info >= (3, 8):
        print_success(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        return True
    else:
        print_error(f"Python 3.8+ required, found {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        return False

def install_dependencies() -> bool:
    """Install Python dependencies"""
    print_step("Installing Python dependencies")
    
    if not Path("requirements.txt").exists():
        print_error("requirements.txt not found")
        return False
    
    # Upgrade pip first
    if not run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], "Upgrading pip"):
        print_warning("Failed to upgrade pip, continuing anyway")
    
    # Install requirements
    return run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], "Installing requirements")

def setup_directories() -> bool:
    """Setup required directories"""
    print_step("Setting up directories")
    
    directories = [
        "logs",
        "data",
        "config",
        "ssl"
    ]
    
    for directory in directories:
        try:
            Path(directory).mkdir(exist_ok=True)
            print(f"   Created: {directory}/")
        except Exception as e:
            print_error(f"Failed to create directory {directory}: {e}")
            return False
    
    print_success("Directories created")
    return True

def generate_config() -> bool:
    """Generate configuration file if it doesn't exist"""
    print_step("Setting up configuration")
    
    config_file = Path("github_mcp_config.yml")
    
    if config_file.exists():
        print_success("Configuration file already exists")
        return True
    
    # Basic configuration template
    config_content = """# GitHub MCP Configuration
github_mcp:
  # Server Configuration
  host: "localhost"
  port: 8081
  log_level: "info"
  
  # GitHub Authentication (set via environment variables)
  github_token: null  # Set GITHUB_TOKEN environment variable
  
  # Optional: Redis Cache
  redis_host: "localhost"
  redis_port: 6379
  
  # Rate Limiting
  rate_limit_requests_per_hour: 5000
  rate_limit_search_per_minute: 30
  
  # Cache TTL (seconds)
  cache_ttl_default: 300
  cache_ttl_repository: 600
  cache_ttl_file_content: 1800
  
  # Health Monitoring
  health_check_interval: 30
  restart_on_failure: true
  max_restart_attempts: 3
  
  # Docker Configuration
  docker_enabled: false
"""
    
    try:
        with open(config_file, 'w') as f:
            f.write(config_content)
        print_success("Configuration file created")
        return True
    except Exception as e:
        print_error(f"Failed to create configuration file: {e}")
        return False

def setup_environment() -> bool:
    """Setup environment variables"""
    print_step("Setting up environment")
    
    env_file = Path(".env.example")
    
    env_content = """# GitHub MCP Environment Variables

# Required: GitHub Authentication
GITHUB_TOKEN=your_github_personal_access_token_here

# Optional: GitHub App Authentication
GITHUB_APP_ID=your_github_app_id
GITHUB_APP_PRIVATE_KEY=your_github_app_private_key

# Optional: Webhook Security
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# Optional: Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Optional: Security
JWT_SECRET=your_jwt_secret_key

# Optional: MCP Manager Integration
MCP_MANAGER_URL=http://localhost:8000

# Optional: Logging
LOG_LEVEL=info

# Optional: Performance
WEBSOCKET_MAX_CONNECTIONS=100
RATE_LIMIT_REQUESTS_PER_HOUR=5000
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print_success("Environment template created (.env.example)")
        print("   📝 Copy .env.example to .env and update with your values")
        return True
    except Exception as e:
        print_error(f"Failed to create environment template: {e}")
        return False

def check_optional_dependencies() -> Dict[str, bool]:
    """Check optional dependencies"""
    print_step("Checking optional dependencies")
    
    optional_deps = {
        "Docker": ["docker", "--version"],
        "Redis CLI": ["redis-cli", "--version"],
        "Git": ["git", "--version"]
    }
    
    results = {}
    
    for name, command in optional_deps.items():
        success = run_command(command, f"Checking {name}")
        results[name] = success
        
        if success:
            print_success(f"{name} is available")
        else:
            print_warning(f"{name} is not available (optional)")
    
    return results

def setup_docker() -> bool:
    """Setup Docker configuration"""
    print_step("Setting up Docker configuration")
    
    # Check if Docker is available
    if not run_command(["docker", "--version"], "Checking Docker"):
        print_warning("Docker not available, skipping Docker setup")
        return True
    
    # Create docker-compose override for local development
    override_content = """# Docker Compose Override for Local Development
version: '3.8'

services:
  github-mcp:
    environment:
      - LOG_LEVEL=debug
    volumes:
      - ./.env:/app/.env:ro
    ports:
      - "8081:8081"
  
  redis:
    ports:
      - "6379:6379"
"""
    
    try:
        with open("docker-compose.override.yml", 'w') as f:
            f.write(override_content)
        print_success("Docker Compose override created")
        return True
    except Exception as e:
        print_error(f"Failed to create Docker override: {e}")
        return False

def validate_setup() -> bool:
    """Validate the setup"""
    print_step("Validating setup")
    
    # Check if validation script exists
    if not Path("validate_github_mcp.py").exists():
        print_warning("Validation script not found, skipping validation")
        return True
    
    # Run validation with --validate-only flag (environment check only)
    return run_command([sys.executable, "validate_github_mcp.py", "--validate-only"], "Running validation")

def print_next_steps():
    """Print next steps for the user"""
    print_header("SETUP COMPLETE - NEXT STEPS")
    
    print("""
1. 📝 Configure Authentication:
   • Copy .env.example to .env
   • Set your GITHUB_TOKEN in .env
   • Or configure GitHub App credentials

2. 🔧 Optional Configuration:
   • Edit github_mcp_config.yml as needed
   • Configure Redis if desired
   • Set up webhook secrets

3. 🚀 Start the Server:
   
   Local Development:
   python start_github_mcp.py
   
   Docker:
   docker-compose -f docker-compose.github-mcp.yml up -d
   
   Validation:
   python validate_github_mcp.py

4. 🧪 Test the Setup:
   • Visit http://localhost:8081/health
   • Check http://localhost:8081/mcp/info
   • Test WebSocket at ws://localhost:8081/ws/test

5. 📚 Documentation:
   • See README.md for complete documentation
   • Check example configurations
   • Review API documentation

6. 🔗 Integration:
   • Register with MCP Manager if available
   • Configure webhooks in GitHub repositories
   • Set up monitoring and alerts
""")

def main():
    """Main setup function"""
    print_header("GitHub MCP Server Setup")
    print("Automated setup for GitHub MCP server with complete API integration")
    
    success = True
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install dependencies
    if not install_dependencies():
        print_error("Failed to install dependencies")
        success = False
    
    # Setup directories
    if not setup_directories():
        print_error("Failed to setup directories")
        success = False
    
    # Generate configuration
    if not generate_config():
        print_error("Failed to generate configuration")
        success = False
    
    # Setup environment
    if not setup_environment():
        print_error("Failed to setup environment")
        success = False
    
    # Check optional dependencies
    optional_results = check_optional_dependencies()
    
    # Setup Docker if available
    if optional_results.get("Docker", False):
        if not setup_docker():
            print_warning("Failed to setup Docker configuration")
    
    # Validate setup
    if not validate_setup():
        print_warning("Setup validation failed (may need configuration)")
    
    if success:
        print_success("Setup completed successfully!")
        print_next_steps()
        return 0
    else:
        print_error("Setup completed with errors")
        return 1

if __name__ == "__main__":
    sys.exit(main())