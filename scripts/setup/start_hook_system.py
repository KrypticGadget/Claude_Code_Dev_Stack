#!/usr/bin/env python3
"""
Hook System Startup Script - V3.6.9
Comprehensive startup script for the Claude Code Hook Registry System
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
import subprocess
import logging
from datetime import datetime

# Add the hooks directory to the Python path
CURRENT_DIR = Path(__file__).parent
HOOKS_DIR = CURRENT_DIR / "core" / "hooks"
sys.path.insert(0, str(HOOKS_DIR))

# Import the hook management system
try:
    from hook_manager import get_hook_manager, HookManager
    from hook_config import get_hook_config_manager
    from hook_registry import get_hook_registry
    from hook_registry_api import start_api_server
except ImportError as e:
    print(f"❌ Failed to import hook system components: {e}")
    print("Make sure you're running from the correct directory and all dependencies are installed.")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(CURRENT_DIR / 'hook_system.log')
    ]
)
logger = logging.getLogger(__name__)


class HookSystemStarter:
    """Comprehensive hook system startup manager"""
    
    def __init__(self):
        self.hooks_dir = HOOKS_DIR
        self.config_file = self.hooks_dir / "hooks_config.yaml"
        self.startup_config = self._load_startup_config()
        
        # System components
        self.hook_manager = None
        self.api_server = None
        
        # Status tracking
        self.startup_time = datetime.now()
        self.components_status = {
            'dependencies': False,
            'configuration': False,
            'registry': False,
            'api_server': False,
            'hook_discovery': False,
            'system_ready': False
        }
    
    def _load_startup_config(self):
        """Load startup configuration"""
        config_file = CURRENT_DIR / "startup_config.json"
        
        default_config = {
            "api_host": "localhost",
            "api_port": 8888,
            "enable_api": True,
            "enable_hot_reload": True,
            "enable_performance_monitoring": True,
            "enable_lsp_bridge": True,
            "auto_discover_hooks": True,
            "auto_activate_hooks": True,
            "startup_delay": 2,
            "health_check_interval": 30,
            "log_level": "INFO",
            "max_workers": 4,
            "default_timeout": 30.0
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                logger.warning(f"Failed to load startup config: {e}, using defaults")
        else:
            # Create default config file
            try:
                with open(config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                logger.info(f"Created default startup config: {config_file}")
            except Exception as e:
                logger.warning(f"Failed to create startup config: {e}")
        
        return default_config
    
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        logger.info("🔍 Checking dependencies...")
        
        required_packages = [
            'flask', 'flask_cors', 'yaml', 'psutil', 'watchdog'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logger.error(f"❌ Missing required packages: {missing_packages}")
            logger.error("Install them with: pip install -r core/hooks/requirements.txt")
            return False
        
        logger.info("✅ All required dependencies are installed")
        self.components_status['dependencies'] = True
        return True
    
    def setup_configuration(self):
        """Setup and validate configuration"""
        logger.info("⚙️ Setting up configuration...")
        
        try:
            # Create config manager
            config_manager = get_hook_config_manager(
                str(self.hooks_dir), 
                str(self.config_file)
            )
            
            # Validate configurations
            issues = config_manager.validate_configurations()
            
            if issues:
                logger.warning(f"Configuration issues found: {len(issues)}")
                for issue in issues[:5]:  # Show first 5 issues
                    logger.warning(f"  ⚠️  {issue}")
                if len(issues) > 5:
                    logger.warning(f"  ... and {len(issues) - 5} more issues")
            else:
                logger.info("✅ Configuration validation passed")
            
            # Show configuration statistics
            stats = config_manager.get_statistics()
            logger.info(f"📊 Configuration stats: {stats['total_hooks']} hooks, "
                       f"{stats['enabled_hooks']} enabled, {stats['lsp_enabled_hooks']} LSP-compatible")
            
            self.components_status['configuration'] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Configuration setup failed: {e}")
            return False
    
    def initialize_registry(self):
        """Initialize the hook registry"""
        logger.info("📚 Initializing hook registry...")
        
        try:
            # Create hook registry
            registry = get_hook_registry(str(self.hooks_dir))
            
            logger.info(f"✅ Hook registry initialized with {len(registry.hooks)} hooks")
            
            # Show registry statistics
            active_hooks = len([h for h in registry.hooks.values() 
                               if h.state.name == 'ACTIVE'])
            logger.info(f"📈 Registry stats: {active_hooks} active hooks, "
                       f"{len(registry.trigger_mappings)} trigger mappings")
            
            self.components_status['registry'] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Hook registry initialization failed: {e}")
            return False
    
    def start_api_server(self):
        """Start the REST API server"""
        if not self.startup_config.get('enable_api', True):
            logger.info("🚫 API server disabled in configuration")
            self.components_status['api_server'] = True
            return True
        
        logger.info(f"🌐 Starting API server on {self.startup_config['api_host']}:{self.startup_config['api_port']}...")
        
        try:
            # Start API server in background thread
            self.api_server = start_api_server(
                host=self.startup_config['api_host'],
                port=self.startup_config['api_port'],
                threaded=True
            )
            
            # Give the server a moment to start
            time.sleep(2)
            
            logger.info(f"✅ API server started at http://{self.startup_config['api_host']}:{self.startup_config['api_port']}")
            logger.info("🔗 Available endpoints:")
            logger.info("   • /health - Health check")
            logger.info("   • /status - System status")
            logger.info("   • /api/hooks - Hook management")
            logger.info("   • /api/performance - Performance monitoring")
            logger.info("   • /api/triggers - Trigger management")
            
            self.components_status['api_server'] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ API server startup failed: {e}")
            return False
    
    def initialize_hook_manager(self):
        """Initialize the comprehensive hook manager"""
        logger.info("🎛️ Initializing hook management system...")
        
        try:
            # Create hook manager with configuration
            self.hook_manager = get_hook_manager(
                hooks_directory=str(self.hooks_dir),
                config_file=str(self.config_file),
                api_host=self.startup_config['api_host'],
                api_port=self.startup_config['api_port'],
                auto_start=True
            )
            
            logger.info("✅ Hook management system initialized")
            
            # Auto-activate hooks if configured
            if self.startup_config.get('auto_activate_hooks', True):
                self._auto_activate_hooks()
            
            self.components_status['hook_discovery'] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Hook manager initialization failed: {e}")
            return False
    
    def _auto_activate_hooks(self):
        """Auto-activate hooks based on configuration"""
        if not self.hook_manager:
            return
        
        logger.info("🔄 Auto-activating configured hooks...")
        
        try:
            # Get enabled hooks from configuration
            if self.hook_manager.config_manager:
                enabled_hooks = self.hook_manager.config_manager.get_enabled_hooks()
                
                activated_count = 0
                for hook_name in enabled_hooks:
                    if self.hook_manager.activate_hook(hook_name):
                        activated_count += 1
                
                logger.info(f"✅ Auto-activated {activated_count}/{len(enabled_hooks)} hooks")
            
        except Exception as e:
            logger.error(f"❌ Auto-activation failed: {e}")
    
    def run_system_checks(self):
        """Run comprehensive system checks"""
        logger.info("🔍 Running system health checks...")
        
        try:
            if self.hook_manager:
                # Run validation
                validation = self.hook_manager.validate_system()
                
                if validation['overall_status'] == 'healthy':
                    logger.info("✅ System health check passed")
                else:
                    logger.warning(f"⚠️  System health: {validation['overall_status']}")
                    
                    if validation['issues']:
                        for issue in validation['issues'][:3]:
                            logger.warning(f"   • {issue}")
                    
                    if validation['warnings']:
                        for warning in validation['warnings'][:3]:
                            logger.warning(f"   • {warning}")
                
                # Show performance summary
                perf_summary = self.hook_manager.get_performance_summary()
                system_perf = perf_summary.get('system_performance', {})
                
                if system_perf:
                    logger.info(f"📊 Performance: {system_perf.get('active_hooks', 0)} active hooks, "
                               f"{system_perf.get('total_executions', 0)} total executions")
            
            self.components_status['system_ready'] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ System health checks failed: {e}")
            return False
    
    def start_system(self):
        """Start the complete hook system"""
        logger.info("🚀 Starting Claude Code Hook Registry System V3.6.9")
        logger.info(f"📁 Working directory: {CURRENT_DIR}")
        logger.info(f"🔧 Hooks directory: {self.hooks_dir}")
        
        startup_steps = [
            ("Dependencies", self.check_dependencies),
            ("Configuration", self.setup_configuration),
            ("Registry", self.initialize_registry),
            ("API Server", self.start_api_server),
            ("Hook Manager", self.initialize_hook_manager),
            ("System Checks", self.run_system_checks)
        ]
        
        for step_name, step_function in startup_steps:
            logger.info(f"▶️  Starting {step_name}...")
            
            if not step_function():
                logger.error(f"❌ {step_name} failed - stopping startup")
                return False
            
            # Brief delay between steps
            if self.startup_config.get('startup_delay', 0) > 0:
                time.sleep(self.startup_config['startup_delay'])
        
        # System is now ready
        startup_duration = (datetime.now() - self.startup_time).total_seconds()
        logger.info(f"🎉 Hook Registry System fully operational! (startup time: {startup_duration:.1f}s)")
        
        # Show system summary
        self._show_system_summary()
        
        return True
    
    def _show_system_summary(self):
        """Show system summary after startup"""
        logger.info("📋 System Summary:")
        
        if self.hook_manager:
            status = self.hook_manager.get_system_status()
            
            logger.info(f"   • Total hooks: {status.get('stats', {}).get('total_hooks', 0)}")
            logger.info(f"   • Active hooks: {status.get('stats', {}).get('active_hooks', 0)}")
            logger.info(f"   • Uptime: {status.get('uptime_seconds', 0):.1f}s")
            
            if self.startup_config.get('enable_api', True):
                logger.info(f"   • API endpoint: http://{self.startup_config['api_host']}:{self.startup_config['api_port']}")
        
        logger.info(f"   • Hot reload: {'✅' if self.startup_config.get('enable_hot_reload', True) else '❌'}")
        logger.info(f"   • Performance monitoring: {'✅' if self.startup_config.get('enable_performance_monitoring', True) else '❌'}")
        logger.info(f"   • LSP bridge: {'✅' if self.startup_config.get('enable_lsp_bridge', True) else '❌'}")
    
    def run_daemon(self):
        """Run the system as a daemon"""
        logger.info("🔄 Running as daemon - press Ctrl+C to stop")
        
        try:
            health_check_interval = self.startup_config.get('health_check_interval', 30)
            
            while True:
                time.sleep(health_check_interval)
                
                # Periodic health check
                if self.hook_manager:
                    try:
                        status = self.hook_manager.get_system_status()
                        if status.get('running', False):
                            logger.debug(f"🏥 Health check: System running normally "
                                       f"({status.get('stats', {}).get('active_hooks', 0)} active hooks)")
                        else:
                            logger.warning("⚠️  Health check: System not running properly")
                    except Exception as e:
                        logger.error(f"❌ Health check failed: {e}")
                
        except KeyboardInterrupt:
            logger.info("🛑 Received interrupt signal, shutting down...")
            self.stop_system()
        except Exception as e:
            logger.error(f"❌ Daemon error: {e}")
            self.stop_system()
    
    def stop_system(self):
        """Stop the hook system gracefully"""
        logger.info("🛑 Stopping Hook Registry System...")
        
        try:
            if self.hook_manager:
                self.hook_manager.stop()
                logger.info("✅ Hook manager stopped")
            
            if self.api_server:
                self.api_server.stop()
                logger.info("✅ API server stopped")
            
            logger.info("🔚 Hook Registry System stopped gracefully")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")
    
    def get_system_status(self):
        """Get current system status"""
        if self.hook_manager:
            return self.hook_manager.get_system_status()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'initialized': False,
            'running': False,
            'components_status': self.components_status
        }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Claude Code Hook Registry System V3.6.9 Startup Script"
    )
    
    parser.add_argument('--daemon', action='store_true', 
                       help='Run as daemon (keeps running until stopped)')
    parser.add_argument('--status-only', action='store_true', 
                       help='Show status and exit')
    parser.add_argument('--validate-only', action='store_true', 
                       help='Run validation and exit')
    parser.add_argument('--config-file', 
                       help='Custom configuration file path')
    parser.add_argument('--api-host', default='localhost', 
                       help='API server host')
    parser.add_argument('--api-port', type=int, default=8888, 
                       help='API server port')
    parser.add_argument('--no-api', action='store_true', 
                       help='Disable API server')
    parser.add_argument('--debug', action='store_true', 
                       help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create startup manager
    starter = HookSystemStarter()
    
    # Override configuration with command line arguments
    if args.config_file:
        starter.config_file = Path(args.config_file)
    if args.no_api:
        starter.startup_config['enable_api'] = False
    if args.api_host:
        starter.startup_config['api_host'] = args.api_host
    if args.api_port:
        starter.startup_config['api_port'] = args.api_port
    
    try:
        if args.status_only:
            # Show status and exit
            status = starter.get_system_status()
            print(json.dumps(status, indent=2, default=str))
            return
        
        elif args.validate_only:
            # Run validation only
            if starter.check_dependencies() and starter.setup_configuration():
                print("✅ Validation passed")
                return
            else:
                print("❌ Validation failed")
                sys.exit(1)
        
        else:
            # Full system startup
            if starter.start_system():
                if args.daemon:
                    starter.run_daemon()
                else:
                    print("✅ System started successfully")
                    print(f"🌐 API available at: http://{starter.startup_config['api_host']}:{starter.startup_config['api_port']}")
                    print("💡 Use --daemon flag to run continuously")
            else:
                print("❌ System startup failed")
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        starter.stop_system()
    except Exception as e:
        logger.error(f"❌ Startup script failed: {e}")
        sys.exit(1)
    finally:
        starter.stop_system()


if __name__ == '__main__':
    main()