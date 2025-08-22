#!/usr/bin/env python3
"""
Monitoring Infrastructure Setup Script for Claude Code V3.6.9
Automated setup and configuration of complete monitoring stack
"""

import os
import sys
import json
import subprocess
import shutil
import time
from pathlib import Path
from typing import List, Dict, Any
import logging

class MonitoringSetup:
    """Setup and configure monitoring infrastructure"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.claude_dir = Path.home() / '.claude'
        self.monitoring_dir = self.claude_dir / 'monitoring'
        
        # Setup logging
        self.setup_logging()
        
        # Configuration
        self.config = {
            'prometheus_port': 9090,
            'grafana_port': 3000,
            'alertmanager_port': 9093,
            'loki_port': 3100,
            'metrics_collector_port': 8001,
            'node_exporter_port': 9100
        }
    
    def setup_logging(self):
        """Setup logging for setup process"""
        log_dir = self.claude_dir / 'logs' / 'setup'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] Setup: %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'monitoring_setup.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are installed"""
        self.logger.info("Checking prerequisites...")
        
        required_tools = ['docker', 'docker-compose', 'python']
        missing_tools = []
        
        for tool in required_tools:
            if not shutil.which(tool):
                missing_tools.append(tool)
        
        if missing_tools:
            self.logger.error(f"Missing required tools: {', '.join(missing_tools)}")
            return False
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or python_version.minor < 8:
            self.logger.error("Python 3.8 or higher required")
            return False
        
        self.logger.info("All prerequisites satisfied")
        return True
    
    def create_directory_structure(self):
        """Create monitoring directory structure"""
        self.logger.info("Creating directory structure...")
        
        directories = [
            self.monitoring_dir,
            self.monitoring_dir / 'prometheus',
            self.monitoring_dir / 'grafana' / 'dashboards',
            self.monitoring_dir / 'grafana' / 'provisioning' / 'dashboards',
            self.monitoring_dir / 'grafana' / 'provisioning' / 'datasources',
            self.monitoring_dir / 'loki',
            self.monitoring_dir / 'alerting',
            self.monitoring_dir / 'logs',
            self.monitoring_dir / 'metrics',
            self.monitoring_dir / 'scripts',
            self.claude_dir / 'logs' / 'performance',
            self.claude_dir / 'logs' / 'agents',
            self.claude_dir / 'logs' / 'hooks',
            self.claude_dir / 'logs' / 'sessions',
            self.claude_dir / 'logs' / 'integrations',
            self.claude_dir / 'logs' / 'errors',
            self.claude_dir / 'logs' / 'orchestration',
            self.claude_dir / 'logs' / 'system',
            self.claude_dir / 'logs' / 'api'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("Directory structure created")
    
    def copy_configuration_files(self):
        """Copy configuration files to monitoring directory"""
        self.logger.info("Copying configuration files...")
        
        config_files = [
            ('prometheus/prometheus.yml', self.monitoring_dir / 'prometheus' / 'prometheus.yml'),
            ('prometheus/alert_rules.yml', self.monitoring_dir / 'prometheus' / 'alert_rules.yml'),
            ('alerting/alertmanager.yml', self.monitoring_dir / 'alerting' / 'alertmanager.yml'),
            ('logging/promtail_config.yml', self.monitoring_dir / 'logging' / 'promtail_config.yml'),
            ('docker-compose.yml', self.monitoring_dir / 'docker-compose.yml'),
            ('Dockerfile.metrics', self.monitoring_dir / 'Dockerfile.metrics'),
            ('requirements-monitoring.txt', self.monitoring_dir / 'requirements-monitoring.txt')
        ]
        
        for src, dst in config_files:
            src_path = self.base_dir / src
            if src_path.exists():
                shutil.copy2(src_path, dst)
                self.logger.info(f"Copied {src} to {dst}")
            else:
                self.logger.warning(f"Source file not found: {src}")
        
        # Copy dashboard files
        dashboard_files = [
            'agent_performance.json',
            'session_monitoring.json',
            'system_health.json',
            'resource_usage.json',
            'hook_execution.json'
        ]
        
        grafana_dashboards_dir = self.monitoring_dir / 'grafana' / 'dashboards'
        for dashboard in dashboard_files:
            src_path = self.base_dir / 'grafana' / 'dashboards' / dashboard
            if src_path.exists():
                shutil.copy2(src_path, grafana_dashboards_dir / dashboard)
                self.logger.info(f"Copied dashboard: {dashboard}")
    
    def create_grafana_provisioning(self):
        """Create Grafana provisioning configuration"""
        self.logger.info("Creating Grafana provisioning configuration...")
        
        # Datasources configuration
        datasources_config = {
            'apiVersion': 1,
            'datasources': [
                {
                    'name': 'Prometheus',
                    'type': 'prometheus',
                    'access': 'proxy',
                    'url': f'http://prometheus:{self.config["prometheus_port"]}',
                    'isDefault': True
                },
                {
                    'name': 'Loki',
                    'type': 'loki',
                    'access': 'proxy',
                    'url': f'http://loki:{self.config["loki_port"]}'
                }
            ]
        }
        
        datasources_file = self.monitoring_dir / 'grafana' / 'provisioning' / 'datasources' / 'datasources.yml'
        with open(datasources_file, 'w') as f:
            import yaml
            yaml.dump(datasources_config, f, default_flow_style=False)
        
        # Dashboards configuration
        dashboards_config = {
            'apiVersion': 1,
            'providers': [
                {
                    'name': 'claude-code-dashboards',
                    'type': 'file',
                    'disableDeletion': False,
                    'editable': True,
                    'options': {
                        'path': '/var/lib/grafana/dashboards'
                    }
                }
            ]
        }
        
        dashboards_file = self.monitoring_dir / 'grafana' / 'provisioning' / 'dashboards' / 'dashboards.yml'
        with open(dashboards_file, 'w') as f:
            import yaml
            yaml.dump(dashboards_config, f, default_flow_style=False)
    
    def create_loki_config(self):
        """Create Loki configuration"""
        self.logger.info("Creating Loki configuration...")
        
        loki_config = {
            'auth_enabled': False,
            'server': {
                'http_listen_port': 3100,
                'grpc_listen_port': 9096
            },
            'common': {
                'path_prefix': '/loki',
                'storage': {
                    'filesystem': {
                        'chunks_directory': '/loki/chunks',
                        'rules_directory': '/loki/rules'
                    }
                },
                'replication_factor': 1,
                'ring': {
                    'instance_addr': '127.0.0.1',
                    'kvstore': {
                        'store': 'inmemory'
                    }
                }
            },
            'query_range': {
                'results_cache': {
                    'cache': {
                        'embedded_cache': {
                            'enabled': True,
                            'max_size_mb': 100
                        }
                    }
                }
            },
            'schema_config': {
                'configs': [
                    {
                        'from': '2020-10-24',
                        'store': 'boltdb-shipper',
                        'object_store': 'filesystem',
                        'schema': 'v11',
                        'index': {
                            'prefix': 'index_',
                            'period': '24h'
                        }
                    }
                ]
            },
            'ruler': {
                'alertmanager_url': f'http://alertmanager:{self.config["alertmanager_port"]}'
            }
        }
        
        loki_config_file = self.monitoring_dir / 'loki' / 'local-config.yaml'
        with open(loki_config_file, 'w') as f:
            import yaml
            yaml.dump(loki_config, f, default_flow_style=False)
    
    def install_python_dependencies(self):
        """Install Python monitoring dependencies"""
        self.logger.info("Installing Python dependencies...")
        
        requirements_file = self.monitoring_dir / 'requirements-monitoring.txt'
        if requirements_file.exists():
            try:
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
                ], check=True, capture_output=True)
                self.logger.info("Python dependencies installed successfully")
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to install Python dependencies: {e}")
                return False
        
        return True
    
    def setup_metrics_collector(self):
        """Setup Claude Code metrics collector"""
        self.logger.info("Setting up metrics collector...")
        
        # Copy metrics collector
        collector_src = self.base_dir / 'enhanced_performance_monitor.py'
        collector_dst = self.monitoring_dir / 'enhanced_performance_monitor.py'
        
        if collector_src.exists():
            shutil.copy2(collector_src, collector_dst)
        
        # Copy additional metrics files
        metrics_src_dir = self.base_dir / 'metrics'
        metrics_dst_dir = self.monitoring_dir / 'metrics'
        
        if metrics_src_dir.exists():
            shutil.copytree(metrics_src_dir, metrics_dst_dir, dirs_exist_ok=True)
        
        # Create startup script
        startup_script = self.monitoring_dir / 'scripts' / 'start_metrics_collector.py'
        startup_script.parent.mkdir(exist_ok=True)
        
        startup_content = f'''#!/usr/bin/env python3
"""
Claude Code Metrics Collector Startup Script
"""

import os
import sys
from pathlib import Path

# Add monitoring directory to path
monitoring_dir = Path(__file__).parent.parent
sys.path.insert(0, str(monitoring_dir))

# Start the enhanced performance monitor
from enhanced_performance_monitor import main

if __name__ == '__main__':
    main()
'''
        
        with open(startup_script, 'w') as f:
            f.write(startup_content)
        
        startup_script.chmod(0o755)
    
    def start_monitoring_stack(self):
        """Start the monitoring stack using Docker Compose"""
        self.logger.info("Starting monitoring stack...")
        
        compose_file = self.monitoring_dir / 'docker-compose.yml'
        if not compose_file.exists():
            self.logger.error("Docker Compose file not found")
            return False
        
        try:
            # Change to monitoring directory
            os.chdir(self.monitoring_dir)
            
            # Pull images
            subprocess.run(['docker-compose', 'pull'], check=True)
            
            # Start services
            subprocess.run(['docker-compose', 'up', '-d'], check=True)
            
            self.logger.info("Monitoring stack started successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to start monitoring stack: {e}")
            return False
    
    def wait_for_services(self):
        """Wait for services to be ready"""
        self.logger.info("Waiting for services to be ready...")
        
        services = [
            ('Prometheus', f'http://localhost:{self.config["prometheus_port"]}/api/v1/status/config'),
            ('Grafana', f'http://localhost:{self.config["grafana_port"]}/api/health'),
            ('Alertmanager', f'http://localhost:{self.config["alertmanager_port"]}/-/ready')
        ]
        
        import requests
        import time
        
        for service_name, url in services:
            for attempt in range(30):  # Wait up to 5 minutes
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        self.logger.info(f"{service_name} is ready")
                        break
                except requests.exceptions.RequestException:
                    pass
                
                if attempt == 29:
                    self.logger.warning(f"{service_name} may not be ready")
                
                time.sleep(10)
    
    def create_monitoring_scripts(self):
        """Create utility scripts for monitoring management"""
        self.logger.info("Creating monitoring scripts...")
        
        scripts_dir = self.monitoring_dir / 'scripts'
        
        # Status check script
        status_script = scripts_dir / 'check_status.py'
        status_content = '''#!/usr/bin/env python3
"""Check monitoring stack status"""

import requests
import json
import sys
from pathlib import Path

def check_service(name, url):
    try:
        response = requests.get(url, timeout=5)
        status = "UP" if response.status_code == 200 else "DOWN"
        print(f"{name}: {status}")
        return response.status_code == 200
    except:
        print(f"{name}: DOWN")
        return False

def main():
    services = [
        ("Prometheus", "http://localhost:9090/api/v1/status/config"),
        ("Grafana", "http://localhost:3000/api/health"),
        ("Alertmanager", "http://localhost:9093/-/ready"),
        ("Loki", "http://localhost:3100/ready"),
        ("Metrics Collector", "http://localhost:8001/metrics")
    ]
    
    all_up = True
    for name, url in services:
        if not check_service(name, url):
            all_up = False
    
    sys.exit(0 if all_up else 1)

if __name__ == '__main__':
    main()
'''
        
        with open(status_script, 'w') as f:
            f.write(status_content)
        status_script.chmod(0o755)
        
        # Restart script
        restart_script = scripts_dir / 'restart_monitoring.sh'
        restart_content = '''#!/bin/bash
"""Restart monitoring stack"""

cd "$(dirname "$0")/.."
echo "Stopping monitoring stack..."
docker-compose down

echo "Starting monitoring stack..."
docker-compose up -d

echo "Monitoring stack restarted"
'''
        
        with open(restart_script, 'w') as f:
            f.write(restart_content)
        restart_script.chmod(0o755)
    
    def setup_integration_with_existing_hooks(self):
        """Setup integration with existing Claude Code hooks"""
        self.logger.info("Setting up integration with existing hooks...")
        
        # Create hook integration script
        integration_script = self.claude_dir / 'hooks' / 'monitoring_integration.py'
        integration_content = f'''#!/usr/bin/env python3
"""
Monitoring Integration Hook for Claude Code V3.6.9
Integrates existing hooks with monitoring infrastructure
"""

import json
import time
import requests
from pathlib import Path
from datetime import datetime

class MonitoringIntegration:
    """Integration with monitoring infrastructure"""
    
    def __init__(self):
        self.metrics_endpoint = "http://localhost:{self.config['metrics_collector_port']}/metrics"
        self.claude_dir = Path.home() / '.claude'
        self.enabled = True
    
    def record_agent_execution(self, agent_name, duration, tokens_used, success=True):
        """Record agent execution metrics"""
        if not self.enabled:
            return
        
        try:
            # This would send metrics to the collector
            # Implementation depends on the metrics collector API
            pass
        except Exception as e:
            print(f"Failed to record agent metrics: {{e}}")
    
    def record_hook_execution(self, hook_name, duration, success=True):
        """Record hook execution metrics"""
        if not self.enabled:
            return
        
        try:
            # This would send metrics to the collector
            pass
        except Exception as e:
            print(f"Failed to record hook metrics: {{e}}")
    
    def record_session_operation(self, operation_type, duration, session_size=0):
        """Record session operation metrics"""
        if not self.enabled:
            return
        
        try:
            # This would send metrics to the collector
            pass
        except Exception as e:
            print(f"Failed to record session metrics: {{e}}")

# Global integration instance
_integration = MonitoringIntegration()

def get_integration():
    """Get monitoring integration instance"""
    return _integration
'''
        
        with open(integration_script, 'w') as f:
            f.write(integration_content)
    
    def generate_setup_report(self) -> Dict[str, Any]:
        """Generate setup completion report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'setup_status': 'completed',
            'services': {
                'prometheus': f'http://localhost:{self.config["prometheus_port"]}',
                'grafana': f'http://localhost:{self.config["grafana_port"]}',
                'alertmanager': f'http://localhost:{self.config["alertmanager_port"]}',
                'loki': f'http://localhost:{self.config["loki_port"]}',
                'metrics_collector': f'http://localhost:{self.config["metrics_collector_port"]}'
            },
            'dashboards': [
                'Agent Performance',
                'Session Monitoring',
                'System Health',
                'Resource Usage',
                'Hook Execution'
            ],
            'configuration': {
                'monitoring_directory': str(self.monitoring_dir),
                'logs_directory': str(self.claude_dir / 'logs'),
                'metrics_directory': str(self.claude_dir / 'metrics')
            },
            'next_steps': [
                'Access Grafana at http://localhost:3000 (admin/admin)',
                'Check Prometheus at http://localhost:9090',
                'View logs in Loki via Grafana',
                'Configure alerts in Alertmanager',
                'Start metrics collector: python enhanced_performance_monitor.py start'
            ]
        }
        
        return report
    
    def run_complete_setup(self):
        """Run complete monitoring setup"""
        self.logger.info("Starting complete monitoring infrastructure setup...")
        
        steps = [
            ("Checking prerequisites", self.check_prerequisites),
            ("Creating directory structure", self.create_directory_structure),
            ("Copying configuration files", self.copy_configuration_files),
            ("Creating Grafana provisioning", self.create_grafana_provisioning),
            ("Creating Loki configuration", self.create_loki_config),
            ("Installing Python dependencies", self.install_python_dependencies),
            ("Setting up metrics collector", self.setup_metrics_collector),
            ("Creating monitoring scripts", self.create_monitoring_scripts),
            ("Setting up hook integration", self.setup_integration_with_existing_hooks),
        ]
        
        for step_name, step_func in steps:
            self.logger.info(f"Executing: {step_name}")
            try:
                result = step_func()
                if result is False:
                    self.logger.error(f"Failed: {step_name}")
                    return False
            except Exception as e:
                self.logger.error(f"Error in {step_name}: {e}")
                return False
        
        # Generate and save setup report
        report = self.generate_setup_report()
        report_file = self.monitoring_dir / 'setup_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info("Monitoring infrastructure setup completed successfully!")
        
        # Print summary
        print("\n" + "="*60)
        print("Claude Code V3.6.9 Monitoring Infrastructure Setup Complete!")
        print("="*60)
        print(f"Monitoring Directory: {self.monitoring_dir}")
        print(f"Setup Report: {report_file}")
        print("\nNext Steps:")
        for step in report['next_steps']:
            print(f"  • {step}")
        print("="*60)
        
        return True

def main():
    """Main setup function"""
    setup = MonitoringSetup()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'full':
            success = setup.run_complete_setup()
            sys.exit(0 if success else 1)
        
        elif command == 'start-stack':
            success = setup.start_monitoring_stack()
            if success:
                setup.wait_for_services()
            sys.exit(0 if success else 1)
        
        elif command == 'check':
            # Quick prerequisite check
            success = setup.check_prerequisites()
            sys.exit(0 if success else 1)
        
        else:
            print("Usage: setup_monitoring.py [full|start-stack|check]")
            sys.exit(1)
    else:
        # Default: run full setup
        success = setup.run_complete_setup()
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()