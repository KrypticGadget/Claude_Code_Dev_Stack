#!/usr/bin/env python3
"""
Dependency Installation Script for Real-Time Dashboard
Handles cross-platform installation with error handling and progress feedback.
"""

import sys
import subprocess
import platform
import os
from pathlib import Path


# Required packages with specific versions
REQUIRED_PACKAGES = [
    "flask==3.0.0",
    "flask-socketio==5.3.5",
    "flask-cors==4.0.0",
    "python-socketio==5.10.0",
    "gitpython==3.1.40",
    "watchdog==4.0.0",
    "psutil==5.9.6",
    "requests==2.31.0"
]

MINIMUM_PYTHON_VERSION = (3, 8)


def print_banner():
    """Print installation banner."""
    print("=" * 60)
    print("Real-Time Dashboard - Dependency Installation")
    print("=" * 60)
    print()


def check_python_version():
    """Check if Python version meets minimum requirements."""
    current_version = sys.version_info[:2]
    
    print(f"Checking Python version... {sys.version}")
    
    if current_version < MINIMUM_PYTHON_VERSION:
        print(f"ERROR: Python {MINIMUM_PYTHON_VERSION[0]}.{MINIMUM_PYTHON_VERSION[1]}+ is required.")
        print(f"Current version: {current_version[0]}.{current_version[1]}")
        return False
    
    print(f"✓ Python version {current_version[0]}.{current_version[1]} meets requirements")
    return True


def detect_pip_command():
    """Detect the appropriate pip command to use."""
    pip_commands = ["pip3", "pip"]
    
    for cmd in pip_commands:
        try:
            # Check if command exists and points to Python 3
            result = subprocess.run([cmd, "--version"], 
                                  capture_output=True, text=True, check=True)
            
            if "python 3" in result.stdout.lower() or "python3" in result.stdout.lower():
                print(f"✓ Using pip command: {cmd}")
                return cmd
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    # Fallback to python -m pip
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      capture_output=True, text=True, check=True)
        pip_cmd = [sys.executable, "-m", "pip"]
        print(f"✓ Using pip command: {' '.join(pip_cmd)}")
        return pip_cmd
    except subprocess.CalledProcessError:
        pass
    
    print("ERROR: Could not find a suitable pip command")
    return None


def check_existing_packages(pip_cmd):
    """Check which packages are already installed."""
    print("Checking existing packages...")
    
    try:
        if isinstance(pip_cmd, list):
            result = subprocess.run(pip_cmd + ["list", "--format=freeze"], 
                                  capture_output=True, text=True, check=True)
        else:
            result = subprocess.run([pip_cmd, "list", "--format=freeze"], 
                                  capture_output=True, text=True, check=True)
        
        installed_packages = {}
        for line in result.stdout.strip().split('\n'):
            if '==' in line:
                name, version = line.split('==', 1)
                installed_packages[name.lower()] = version
        
        return installed_packages
    except subprocess.CalledProcessError:
        print("Warning: Could not check existing packages")
        return {}


def install_package(pip_cmd, package, progress, total):
    """Install a single package with progress feedback."""
    package_name = package.split('==')[0]
    
    print(f"[{progress}/{total}] Installing {package}...", end=' ', flush=True)
    
    try:
        if isinstance(pip_cmd, list):
            cmd = pip_cmd + ["install", package]
        else:
            cmd = [pip_cmd, "install", package]
        
        # Add platform-specific flags
        if platform.system() == "Windows":
            # On Windows, sometimes we need to handle path issues
            cmd.append("--user")
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✓ Success")
        return True
        
    except subprocess.CalledProcessError as e:
        print("✗ Failed")
        print(f"Error installing {package}: {e.stderr}")
        
        # Try alternative installation methods
        print(f"Attempting alternative installation for {package}...")
        
        try:
            # Try without --user flag
            if isinstance(pip_cmd, list):
                cmd = pip_cmd + ["install", package, "--no-cache-dir"]
            else:
                cmd = [pip_cmd, "install", package, "--no-cache-dir"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✓ Alternative installation succeeded for {package}")
            return True
            
        except subprocess.CalledProcessError as e2:
            print(f"✗ Alternative installation also failed: {e2.stderr}")
            return False


def upgrade_pip(pip_cmd):
    """Upgrade pip to latest version."""
    print("Upgrading pip to latest version...")
    
    try:
        if isinstance(pip_cmd, list):
            cmd = pip_cmd + ["install", "--upgrade", "pip"]
        else:
            cmd = [pip_cmd, "install", "--upgrade", "pip"]
        
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✓ pip upgraded successfully")
    except subprocess.CalledProcessError:
        print("Warning: Could not upgrade pip (this may be okay)")


def create_requirements_file():
    """Create requirements.txt file."""
    script_dir = Path(__file__).parent
    requirements_file = script_dir / "requirements.txt"
    
    print(f"Creating requirements.txt at {requirements_file}")
    
    try:
        with open(requirements_file, 'w') as f:
            for package in REQUIRED_PACKAGES:
                f.write(f"{package}\n")
        
        print("✓ requirements.txt created successfully")
        return str(requirements_file)
    except Exception as e:
        print(f"Error creating requirements.txt: {e}")
        return None


def verify_installation(pip_cmd):
    """Verify all packages are installed correctly."""
    print("\nVerifying installation...")
    
    try:
        if isinstance(pip_cmd, list):
            result = subprocess.run(pip_cmd + ["list", "--format=freeze"], 
                                  capture_output=True, text=True, check=True)
        else:
            result = subprocess.run([pip_cmd, "list", "--format=freeze"], 
                                  capture_output=True, text=True, check=True)
        
        installed_packages = {}
        for line in result.stdout.strip().split('\n'):
            if '==' in line:
                name, version = line.split('==', 1)
                installed_packages[name.lower()] = version
        
        all_installed = True
        for required_package in REQUIRED_PACKAGES:
            package_name, required_version = required_package.split('==')
            package_name_lower = package_name.lower()
            
            if package_name_lower in installed_packages:
                installed_version = installed_packages[package_name_lower]
                if installed_version == required_version:
                    print(f"✓ {package_name} {installed_version}")
                else:
                    print(f"⚠ {package_name} {installed_version} (expected {required_version})")
            else:
                print(f"✗ {package_name} not found")
                all_installed = False
        
        return all_installed
    except subprocess.CalledProcessError:
        print("Could not verify installation")
        return False


def test_imports():
    """Test importing key packages."""
    print("\nTesting package imports...")
    
    test_imports = [
        ("flask", "Flask"),
        ("flask_socketio", "SocketIO"),
        ("flask_cors", "CORS"),
        ("socketio", "python-socketio"),
        ("git", "GitPython"),
        ("watchdog.observers", "watchdog"),
        ("psutil", "psutil"),
        ("requests", "requests")
    ]
    
    all_imports_successful = True
    
    for module_name, display_name in test_imports:
        try:
            __import__(module_name)
            print(f"✓ {display_name} import successful")
        except ImportError as e:
            print(f"✗ {display_name} import failed: {e}")
            all_imports_successful = False
    
    return all_imports_successful


def main():
    """Main installation function."""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Detect pip command
    pip_cmd = detect_pip_command()
    if not pip_cmd:
        print("ERROR: No suitable pip installation found")
        sys.exit(1)
    
    # Create requirements.txt
    requirements_file = create_requirements_file()
    
    # Upgrade pip
    upgrade_pip(pip_cmd)
    
    # Check existing packages
    existing_packages = check_existing_packages(pip_cmd)
    
    print(f"\nInstalling {len(REQUIRED_PACKAGES)} required packages...")
    print("-" * 40)
    
    # Install packages
    failed_packages = []
    for i, package in enumerate(REQUIRED_PACKAGES, 1):
        package_name = package.split('==')[0].lower()
        
        # Check if already installed with correct version
        if package_name in existing_packages:
            required_version = package.split('==')[1]
            if existing_packages[package_name] == required_version:
                print(f"[{i}/{len(REQUIRED_PACKAGES)}] {package} already installed ✓")
                continue
        
        if not install_package(pip_cmd, package, i, len(REQUIRED_PACKAGES)):
            failed_packages.append(package)
    
    print("-" * 40)
    
    # Summary
    if failed_packages:
        print(f"\n⚠ Installation completed with {len(failed_packages)} failures:")
        for package in failed_packages:
            print(f"  - {package}")
        print("\nYou may need to install these packages manually.")
    else:
        print("\n✓ All packages installed successfully!")
    
    # Verify installation
    if verify_installation(pip_cmd):
        print("\n✓ Installation verification passed")
    else:
        print("\n⚠ Installation verification found issues")
    
    # Test imports
    if test_imports():
        print("\n✓ All package imports successful")
    else:
        print("\n⚠ Some package imports failed")
    
    # Final instructions
    print("\n" + "=" * 60)
    print("Installation Summary:")
    print(f"- Python version: {sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}")
    print(f"- Platform: {platform.system()} {platform.release()}")
    print(f"- Pip command: {pip_cmd if isinstance(pip_cmd, str) else ' '.join(pip_cmd)}")
    
    if requirements_file:
        print(f"- Requirements file: {requirements_file}")
    
    if not failed_packages:
        print("\n✓ Ready to run the real-time dashboard!")
        print("You can now start the dashboard with: python dashboard.py")
    else:
        print(f"\n⚠ Please resolve {len(failed_packages)} failed package installations before running the dashboard.")
    
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("Please check your Python and pip installation.")
        sys.exit(1)