#!/usr/bin/env python3
"""
Quick Start Script for Claude Code V3.6.9 Monitoring
One-command setup and validation of the complete monitoring infrastructure
"""

import os
import sys
import time
import json
import subprocess
import requests
from pathlib import Path
from datetime import datetime
import logging

class QuickStart:
    """Quick start monitoring infrastructure"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.claude_dir = Path.home() / '.claude'
        
        # Setup logging
        self.setup_logging()
        
        # Services configuration
        self.services = {
            'prometheus': {'port': 9090, 'path': '/api/v1/status/config'},
            'grafana': {'port': 3000, 'path': '/api/health'},
            'alertmanager': {'port': 9093, 'path': '/-/ready'},
            'loki': {'port': 3100, 'path': '/ready'},
            'metrics_collector': {'port': 8001, 'path': '/metrics'}
        }
        
        self.setup_complete = False
    
    def setup_logging(self):
        """Setup logging"""
        log_dir = self.claude_dir / 'logs' / 'setup'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] QuickStart: %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'quick_start.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def print_banner(self):
        """Print startup banner"""
        banner = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                   Claude Code V3.6.9 Monitoring Quick Start                  ║
║                                                                               ║
║  🎯 Agent Performance Tracking     📊 Session Management Monitoring          ║
║  🖥️  System Health Visualization   🔧 Hook Execution Metrics                ║
║  🚨 Intelligent Alerting          📈 Performance Baselines                  ║
║                                                                               ║
║  Setting up complete monitoring infrastructure...                            ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
        print(banner)
    
    def check_prerequisites(self) -> bool:
        """Check prerequisites quickly"""
        self.logger.info("Checking prerequisites...")
        
        required = {
            'docker': 'Docker is required for monitoring stack',
            'docker-compose': 'Docker Compose is required',
            'python': 'Python 3.8+ is required'
        }
        
        missing = []
        for tool, description in required.items():
            if not self.check_command(tool):
                missing.append(f"❌ {tool}: {description}")
            else:
                print(f"✅ {tool}: Found")
        
        if missing:
            print("\nMissing prerequisites:")
            for item in missing:
                print(f"  {item}")
            return False
        
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8 or higher required")
            return False
        
        print("✅ All prerequisites satisfied")
        return True
    
    def check_command(self, command: str) -> bool:
        """Check if command exists"""
        try:
            subprocess.run([command, '--version'], 
                         capture_output=True, check=True, timeout=5)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def run_setup(self) -> bool:
        """Run the monitoring setup"""
        self.logger.info("Running monitoring setup...")
        
        setup_script = self.base_dir / 'setup_monitoring.py'
        if not setup_script.exists():
            self.logger.error("Setup script not found")
            return False
        
        try:
            print("🔧 Setting up monitoring infrastructure...")
            result = subprocess.run([
                sys.executable, str(setup_script), 'full'
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✅ Monitoring infrastructure setup completed")
                self.setup_complete = True
                return True
            else:
                print(f"❌ Setup failed: {result.stderr}")
                self.logger.error(f"Setup failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Setup timed out after 5 minutes")
            return False
        except Exception as e:
            print(f"❌ Setup error: {e}")
            return False
    
    def start_services(self) -> bool:
        """Start monitoring services"""
        self.logger.info("Starting monitoring services...")
        
        compose_file = self.base_dir / 'docker-compose.yml'
        if not compose_file.exists():
            self.logger.error("Docker Compose file not found")
            return False
        
        try:
            print("🚀 Starting monitoring services...")
            os.chdir(self.base_dir)
            
            # Pull images first
            print("  📦 Pulling Docker images...")
            subprocess.run(['docker-compose', 'pull'], 
                         capture_output=True, check=True, timeout=180)
            
            # Start services
            print("  ⚡ Starting services...")
            subprocess.run(['docker-compose', 'up', '-d'], 
                         capture_output=True, check=True, timeout=120)
            
            print("✅ Services started successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start services: {e}")
            return False
        except subprocess.TimeoutExpired:
            print("❌ Service startup timed out")
            return False
    
    def wait_for_services(self) -> bool:
        """Wait for all services to be ready"""
        self.logger.info("Waiting for services to be ready...")
        print("🔍 Waiting for services to be ready...")
        
        max_wait = 300  # 5 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            all_ready = True
            status_line = "  "
            
            for service_name, config in self.services.items():
                if self.check_service_health(service_name, config):
                    status_line += f"✅ {service_name} "
                else:
                    status_line += f"⏳ {service_name} "
                    all_ready = False
            
            print(f"\r{status_line}", end="", flush=True)
            
            if all_ready:
                print("\n✅ All services are ready!")
                return True
            
            time.sleep(5)
        
        print("\n❌ Services did not start within 5 minutes")
        return False
    
    def check_service_health(self, service_name: str, config: dict) -> bool:
        """Check if service is healthy"""
        try:
            url = f"http://localhost:{config['port']}{config['path']}"
            response = requests.get(url, timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def start_metrics_collector(self) -> bool:
        """Start the metrics collector"""
        self.logger.info("Starting metrics collector...")
        
        collector_script = self.base_dir / 'enhanced_performance_monitor.py'
        if not collector_script.exists():
            self.logger.error("Metrics collector not found")
            return False
        
        try:
            print("📊 Starting metrics collector...")
            
            # Start collector in background
            subprocess.Popen([
                sys.executable, str(collector_script), 'start'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Wait a moment and check if it's responding
            time.sleep(5)
            if self.check_service_health('metrics_collector', self.services['metrics_collector']):
                print("✅ Metrics collector started")
                return True
            else:
                print("❌ Metrics collector failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start metrics collector: {e}")
            return False
    
    def run_validation_tests(self) -> bool:
        """Run validation tests"""
        self.logger.info("Running validation tests...")
        print("🧪 Running validation tests...")
        
        tests = [
            ("Service Health Check", self.validate_services),
            ("Metrics Collection", self.validate_metrics),
            ("Dashboard Access", self.validate_dashboards),
            ("Log Aggregation", self.validate_logs),
            ("Alert Configuration", self.validate_alerts)
        ]
        
        passed = 0
        for test_name, test_func in tests:
            print(f"  Testing {test_name}...", end=" ")
            try:
                if test_func():
                    print("✅ PASS")
                    passed += 1
                else:
                    print("❌ FAIL")
            except Exception as e:
                print(f"❌ ERROR: {e}")
        
        success_rate = passed / len(tests)
        if success_rate >= 0.8:
            print(f"✅ Validation passed ({passed}/{len(tests)} tests)")
            return True
        else:
            print(f"❌ Validation failed ({passed}/{len(tests)} tests)")
            return False
    
    def validate_services(self) -> bool:
        """Validate all services are running"""
        for service_name, config in self.services.items():
            if not self.check_service_health(service_name, config):
                return False
        return True
    
    def validate_metrics(self) -> bool:
        """Validate metrics are being collected"""
        try:
            response = requests.get('http://localhost:8001/metrics', timeout=5)
            return response.status_code == 200 and len(response.text) > 100
        except:
            return False
    
    def validate_dashboards(self) -> bool:
        """Validate Grafana dashboards are accessible"""
        try:
            # Check Grafana API
            response = requests.get('http://localhost:3000/api/health', timeout=5)
            if response.status_code != 200:
                return False
            
            # Check if we can access the dashboard list
            response = requests.get('http://localhost:3000/api/search', 
                                  auth=('admin', 'admin'), timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def validate_logs(self) -> bool:
        """Validate log aggregation is working"""
        try:
            response = requests.get('http://localhost:3100/ready', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def validate_alerts(self) -> bool:
        """Validate alert configuration"""
        try:
            response = requests.get('http://localhost:9093/-/ready', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate_access_info(self) -> dict:
        """Generate access information for user"""
        return {
            'services': {
                'Grafana Dashboards': 'http://localhost:3000 (admin/admin)',
                'Prometheus Metrics': 'http://localhost:9090',
                'Alert Manager': 'http://localhost:9093',
                'Log Viewer (Loki)': 'http://localhost:3000/explore (select Loki datasource)',
                'Metrics Endpoint': 'http://localhost:8001/metrics'
            },
            'dashboards': [
                'Agent Performance - Monitor agent execution and success rates',
                'Session Monitoring - Track session operations and sizes',
                'System Health - CPU, memory, disk usage',
                'Resource Usage - Token usage and component memory',
                'Hook Execution - Hook performance and failures'
            ],
            'next_steps': [
                'Open Grafana at http://localhost:3000',
                'Login with admin/admin (change password)',
                'Explore the Claude Code folder in dashboards',
                'Set up alert notification channels',
                'Configure custom alerts if needed'
            ]
        }
    
    def print_success_summary(self):
        """Print success summary with access information"""
        access_info = self.generate_access_info()
        
        print("\n" + "═" * 80)
        print("🎉 MONITORING INFRASTRUCTURE SETUP COMPLETE! 🎉")
        print("═" * 80)
        
        print("\n📊 AVAILABLE SERVICES:")
        for service, url in access_info['services'].items():
            print(f"  • {service}: {url}")
        
        print("\n📈 AVAILABLE DASHBOARDS:")
        for dashboard in access_info['dashboards']:
            print(f"  • {dashboard}")
        
        print("\n🚀 NEXT STEPS:")
        for step in access_info['next_steps']:
            print(f"  {step}")
        
        print("\n💡 QUICK TIPS:")
        print("  • Use Ctrl+C to stop this script, services will continue running")
        print("  • To stop monitoring: docker-compose down")
        print("  • To restart monitoring: docker-compose up -d")
        print("  • Logs are stored in ~/.claude/logs/")
        print("  • Metrics data is persisted in Docker volumes")
        
        print("\n" + "═" * 80)
        
        # Save access info
        access_file = self.base_dir / 'access_info.json'
        with open(access_file, 'w') as f:
            json.dump(access_info, f, indent=2)
        print(f"📄 Access information saved to: {access_file}")
    
    def run_complete_quick_start(self) -> bool:
        """Run complete quick start process"""
        self.print_banner()
        
        steps = [
            ("Prerequisites Check", self.check_prerequisites),
            ("Setup Infrastructure", self.run_setup),
            ("Start Services", self.start_services),
            ("Wait for Services", self.wait_for_services),
            ("Start Metrics Collector", self.start_metrics_collector),
            ("Validation Tests", self.run_validation_tests)
        ]
        
        for step_name, step_func in steps:
            print(f"\n🔄 {step_name}...")
            try:
                if not step_func():
                    print(f"❌ {step_name} failed")
                    return False
            except KeyboardInterrupt:
                print(f"\n⚠️  Setup interrupted during {step_name}")
                return False
            except Exception as e:
                print(f"❌ {step_name} error: {e}")
                return False
        
        self.print_success_summary()
        return True

def main():
    """Main entry point"""
    quick_start = QuickStart()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'check':
            success = quick_start.check_prerequisites()
            sys.exit(0 if success else 1)
        
        elif command == 'services':
            success = quick_start.start_services() and quick_start.wait_for_services()
            sys.exit(0 if success else 1)
        
        elif command == 'validate':
            success = quick_start.run_validation_tests()
            sys.exit(0 if success else 1)
        
        elif command == 'full':
            success = quick_start.run_complete_quick_start()
            sys.exit(0 if success else 1)
        
        else:
            print("Usage: quick_start.py [check|services|validate|full]")
            print("  check    - Check prerequisites only")
            print("  services - Start services and wait for ready")
            print("  validate - Run validation tests")
            print("  full     - Complete quick start (default)")
            sys.exit(1)
    else:
        # Default: run full quick start
        try:
            success = quick_start.run_complete_quick_start()
            if success:
                print("\n🎯 Monitoring is now active! Press Ctrl+C to exit (services will continue)")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n👋 Goodbye! Monitoring services are still running.")
            sys.exit(0 if success else 1)
        except KeyboardInterrupt:
            print("\n⚠️  Quick start interrupted")
            sys.exit(1)

if __name__ == '__main__':
    main()