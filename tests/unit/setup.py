#!/usr/bin/env python3
"""
Setup script for Agent Test Framework
Initializes the test environment and validates system readiness
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestEnvironmentSetup:
    """Setup and validate test environment"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.tests_path = self.base_path / "tests"
        
    def run_setup(self) -> bool:
        """Run complete setup process"""
        logger.info("Starting Agent Test Framework Setup")
        
        setup_steps = [
            ("Validate Python version", self.validate_python_version),
            ("Create directory structure", self.create_directories),
            ("Install dependencies", self.install_dependencies),
            ("Validate agent discovery", self.validate_agent_discovery),
            ("Setup configuration", self.setup_configuration),
            ("Initialize baselines", self.initialize_baselines),
            ("Validate permissions", self.validate_permissions),
            ("Run smoke tests", self.run_smoke_tests)
        ]
        
        for step_name, step_function in setup_steps:
            logger.info(f"Executing: {step_name}")
            try:
                if not step_function():
                    logger.error(f"Setup step failed: {step_name}")
                    return False
                logger.info(f"✅ Completed: {step_name}")
            except Exception as e:
                logger.error(f"❌ Error in {step_name}: {e}")
                return False
        
        logger.info("🎉 Agent Test Framework setup completed successfully!")
        return True
    
    def validate_python_version(self) -> bool:
        """Validate Python version"""
        version = sys.version_info
        
        if version.major != 3 or version.minor < 9:
            logger.error(f"Python 3.9+ required, found {version.major}.{version.minor}")
            return False
        
        logger.info(f"Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    
    def create_directories(self) -> bool:
        """Create necessary directory structure"""
        directories = [
            self.tests_path,
            self.tests_path / "config",
            self.tests_path / "logs", 
            self.tests_path / "reports",
            self.tests_path / "data",
            self.tests_path / "baselines",
            self.tests_path / "temp"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")
        
        return True
    
    def install_dependencies(self) -> bool:
        """Install required Python packages"""
        requirements_file = self.tests_path / "requirements.txt"
        
        if not requirements_file.exists():
            logger.error(f"Requirements file not found: {requirements_file}")
            return False
        
        try:
            # Install requirements
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], capture_output=True, text=True, check=True)
            
            logger.info("Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e.stderr}")
            return False
    
    def validate_agent_discovery(self) -> bool:
        """Validate that all agents can be discovered"""
        try:
            # Import and test agent discovery
            sys.path.insert(0, str(self.tests_path))
            from agent_test_framework import AgentTestFramework
            
            framework = AgentTestFramework()
            discovered_agents = len(framework.agents)
            
            logger.info(f"Discovered {discovered_agents} agents")
            
            # Validate expected agent count
            expected_agents = 37  # 27 core + 10 BMAD
            if discovered_agents < expected_agents:
                logger.warning(f"Expected {expected_agents} agents, found {discovered_agents}")
                # Don't fail setup, but warn user
            
            # Validate agent categories
            categories = set(agent.category for agent in framework.agents)
            tiers = set(agent.tier for agent in framework.agents)
            
            logger.info(f"Agent categories: {sorted(categories)}")
            logger.info(f"Agent tiers: {sorted(tiers)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Agent discovery validation failed: {e}")
            return False
    
    def setup_configuration(self) -> bool:
        """Setup test configuration"""
        config_file = self.tests_path / "config" / "test-config.yaml"
        
        if config_file.exists():
            logger.info("Configuration file already exists")
            return True
        
        # Configuration should already be created by previous steps
        if not config_file.exists():
            logger.error("Test configuration file not found")
            return False
        
        logger.info(f"Configuration validated: {config_file}")
        return True
    
    def initialize_baselines(self) -> bool:
        """Initialize performance baselines"""
        baselines_dir = self.tests_path / "baselines"
        baseline_file = baselines_dir / "performance-baselines.json"
        
        if baseline_file.exists():
            logger.info("Performance baselines already exist")
            return True
        
        # Create empty baseline file
        import json
        initial_baselines = {
            "version": "3.6.9",
            "created": "initial_setup",
            "baselines": {}
        }
        
        with open(baseline_file, 'w') as f:
            json.dump(initial_baselines, f, indent=2)
        
        logger.info(f"Initialized baselines: {baseline_file}")
        return True
    
    def validate_permissions(self) -> bool:
        """Validate file and directory permissions"""
        # Check write permissions
        test_dirs = [
            self.tests_path / "logs",
            self.tests_path / "reports", 
            self.tests_path / "temp"
        ]
        
        for directory in test_dirs:
            try:
                # Test write permission
                test_file = directory / "test_write_permission.tmp"
                test_file.write_text("permission test")
                test_file.unlink()
                logger.info(f"Write permission validated: {directory}")
            except Exception as e:
                logger.error(f"No write permission for {directory}: {e}")
                return False
        
        # Check execute permissions on scripts
        scripts = [
            self.tests_path / "test-runner.py",
            self.tests_path / "validate-quality-gates.py"
        ]
        
        for script in scripts:
            if script.exists():
                # Make executable on Unix-like systems
                if os.name != 'nt':  # Not Windows
                    os.chmod(script, 0o755)
                logger.info(f"Execute permission set: {script}")
        
        return True
    
    def run_smoke_tests(self) -> bool:
        """Run basic smoke tests to validate setup"""
        try:
            sys.path.insert(0, str(self.tests_path))
            
            # Test 1: Framework initialization
            from agent_test_framework import AgentTestFramework
            framework = AgentTestFramework()
            
            if len(framework.agents) == 0:
                logger.error("No agents discovered in smoke test")
                return False
            
            # Test 2: Configuration loading
            config = framework.config
            if not config:
                logger.error("Configuration not loaded in smoke test")
                return False
            
            # Test 3: Mock environment
            mock_env = framework.mock_environment
            if not mock_env:
                logger.error("Mock environment not initialized in smoke test")
                return False
            
            logger.info("All smoke tests passed")
            return True
            
        except Exception as e:
            logger.error(f"Smoke tests failed: {e}")
            return False
    
    def generate_quickstart_script(self):
        """Generate a quickstart script"""
        quickstart_content = """#!/bin/bash
# Agent Test Framework Quickstart

echo "🚀 Agent Test Framework Quick Start"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "test-runner.py" ]; then
    echo "❌ Please run this script from the tests/ directory"
    exit 1
fi

echo "📊 Running quick validation..."
python test-runner.py --suites individual_operations --timeout 60

echo ""
echo "✅ Quick start completed!"
echo "📖 For full documentation, see README.md"
echo "🔧 To run all tests: python test-runner.py"
echo "📈 To run performance tests: python test-runner.py --suites performance_benchmarks"
"""
        
        quickstart_file = self.tests_path / "quickstart.sh"
        with open(quickstart_file, 'w') as f:
            f.write(quickstart_content)
        
        # Make executable
        if os.name != 'nt':
            os.chmod(quickstart_file, 0o755)
        
        logger.info(f"Quickstart script created: {quickstart_file}")
    
    def print_setup_summary(self):
        """Print setup summary and next steps"""
        print("\n" + "="*60)
        print("🎉 AGENT TEST FRAMEWORK SETUP COMPLETE")
        print("="*60)
        print("\n📁 Directory Structure:")
        print(f"  Tests:      {self.tests_path}")
        print(f"  Config:     {self.tests_path / 'config'}")
        print(f"  Reports:    {self.tests_path / 'reports'}")
        print(f"  Logs:       {self.tests_path / 'logs'}")
        
        print("\n🚀 Quick Start Commands:")
        print("  # Run all tests")
        print("  python test-runner.py")
        print("")
        print("  # Run specific test suite")
        print("  python test-runner.py --suites individual_operations")
        print("")
        print("  # Run with verbose output")
        print("  python test-runner.py --verbose")
        print("")
        print("  # Validate quality gates")
        print("  python validate-quality-gates.py")
        
        print("\n📖 Documentation:")
        print(f"  README:     {self.tests_path / 'README.md'}")
        print(f"  Config:     {self.tests_path / 'config' / 'test-config.yaml'}")
        
        print("\n✅ Next Steps:")
        print("  1. Review test configuration in config/test-config.yaml")
        print("  2. Run initial test suite: python test-runner.py --suites individual_operations")
        print("  3. Check test reports in reports/ directory")
        print("  4. Set up CI/CD integration if needed")
        print("="*60)


def main():
    """Main setup function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup Agent Test Framework')
    parser.add_argument('--path', help='Base path for setup (default: current directory)')
    parser.add_argument('--skip-deps', action='store_true', help='Skip dependency installation')
    parser.add_argument('--quiet', action='store_true', help='Suppress detailed output')
    
    args = parser.parse_args()
    
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    # Initialize setup
    setup = TestEnvironmentSetup(args.path)
    
    try:
        # Run setup
        success = setup.run_setup()
        
        if success:
            # Generate additional files
            setup.generate_quickstart_script()
            
            if not args.quiet:
                setup.print_setup_summary()
            
            print("✅ Setup completed successfully!")
            sys.exit(0)
        else:
            print("❌ Setup failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏸️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Setup failed with error: {e}")
        print(f"❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()