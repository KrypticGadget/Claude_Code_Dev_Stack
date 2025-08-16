#!/usr/bin/env python3
"""
Claude Code Browser Integration Installer
=========================================

Installs and configures the Claude Code Browser integration with Dev Stack v3.0.
Ensures proper dependencies, setup, and AGPL-3.0 compliance.

Attribution:
- Original Claude Code Browser by @zainhoda (AGPL-3.0)
- Integration by Claude Code Dev Stack v3.0 (AGPL-3.0)
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

def print_banner():
    """Print installation banner"""
    print("\n" + "="*80)
    print("🚀 Claude Code Browser Integration Installer")
    print("="*80)
    print("📦 Original Claude Code Browser by @zainhoda (AGPL-3.0)")
    print("🔧 Integration by Claude Code Dev Stack v3.0 (AGPL-3.0)")
    print("📄 License: AGPL-3.0 (Source Available)")
    print("="*80 + "\n")

def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """Install required Python dependencies"""
    print("📦 Installing dependencies...")
    
    dependencies = [
        "websockets>=12.0",
        "aiohttp>=3.9.0", 
        "aiofiles>=23.0.0",
        "psutil>=5.9.0"
    ]
    
    try:
        for dep in dependencies:
            print(f"   Installing {dep}...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", dep
            ], check=True, capture_output=True)
        
        print("✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_browser_data_directory():
    """Setup Claude Code Browser data directory"""
    browser_data_path = Path.home() / ".claude" / "projects"
    
    try:
        browser_data_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Browser data directory: {browser_data_path}")
        
        # Create sample project if none exists
        if not any(browser_data_path.iterdir()):
            sample_project = browser_data_path / "sample_project"
            sample_project.mkdir(exist_ok=True)
            
            # Create sample session
            sample_session = {
                "content": "@agent-api-integration analyze current project structure\n\nThis is a sample Claude Code session with Dev Stack commands.",
                "timestamp": datetime.now().isoformat(),
                "todos": {
                    "todos": [
                        {"text": "Analyze project structure", "completed": False},
                        {"text": "Set up API integration", "completed": False}
                    ]
                }
            }
            
            session_file = sample_project / f"sample_{int(datetime.now().timestamp())}.json"
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(sample_session, f, indent=2)
            
            print(f"✅ Created sample project at {sample_project}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to setup browser data directory: {e}")
        return False

def verify_integration_files():
    """Verify integration files are present"""
    base_path = Path(__file__).parent
    required_files = [
        "core/integrations/browser_adapter.py",
        "core/hooks/hooks/browser_integration_hook.py", 
        "core/integrations/start_browser_integration.py",
        "core/integrations/ATTRIBUTION_AND_COMPLIANCE.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = base_path / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"❌ Missing integration files: {missing_files}")
        return False
    
    print("✅ All integration files present")
    return True

def test_integration():
    """Test the integration setup"""
    print("🧪 Testing integration...")
    
    try:
        # Test imports
        sys.path.insert(0, str(Path(__file__).parent))
        
        from core.integrations.browser_adapter import get_browser_adapter
        from core.hooks.hooks.browser_integration_hook import get_browser_integration_hook
        
        # Test adapter creation
        adapter = get_browser_adapter()
        print("✅ Browser adapter created successfully")
        
        # Test hook creation
        hook = get_browser_integration_hook()
        print("✅ Browser integration hook created successfully")
        
        # Test status
        adapter_status = adapter.get_integration_status()
        hook_status = hook.get_hook_status()
        
        print(f"✅ Adapter status: {adapter_status['adapter_status']}")
        print(f"✅ Hook status: {'active' if hook_status['is_active'] else 'inactive'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def create_startup_script():
    """Create convenient startup script"""
    script_content = '''#!/usr/bin/env python3
"""
Start Claude Code Browser Integration
===================================
"""

import sys
from pathlib import Path

# Add integration path
sys.path.insert(0, str(Path(__file__).parent))

from core.integrations.start_browser_integration import main

if __name__ == "__main__":
    main()
'''
    
    script_path = Path(__file__).parent / "start_browser_integration.py"
    
    try:
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # Make executable on Unix systems
        if sys.platform != 'win32':
            os.chmod(script_path, 0o755)
        
        print(f"✅ Startup script created: {script_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create startup script: {e}")
        return False

def show_completion_message():
    """Show installation completion message"""
    print("\n" + "="*80)
    print("🎉 Claude Code Browser Integration Installation Complete!")
    print("="*80)
    print("📋 Next Steps:")
    print("   1. Start the integration:")
    print("      python start_browser_integration.py")
    print("   2. Or with custom ports:")
    print("      python start_browser_integration.py --websocket-port 8081 --http-port 8082")
    print("   3. Access PWA at: http://localhost:5173 (if dev server running)")
    print("   4. WebSocket API: ws://localhost:8081")
    print("   5. HTTP API: http://localhost:8082")
    print("\n📚 Documentation:")
    print("   - Integration guide: core/integrations/ATTRIBUTION_AND_COMPLIANCE.md")
    print("   - Original project: https://github.com/zainhoda/claude-code-browser")
    print("\n⚖️  License Compliance:")
    print("   - AGPL-3.0 license maintained")
    print("   - Original author @zainhoda properly attributed")
    print("   - Source code available and modifiable")
    print("="*80 + "\n")

def main():
    """Main installation process"""
    print_banner()
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup directories
    if not setup_browser_data_directory():
        sys.exit(1)
    
    # Verify files
    if not verify_integration_files():
        sys.exit(1)
    
    # Test integration
    if not test_integration():
        print("⚠️  Integration test failed, but installation may still work")
    
    # Create startup script
    if not create_startup_script():
        print("⚠️  Failed to create startup script, but integration should work")
    
    # Show completion
    show_completion_message()

if __name__ == "__main__":
    main()