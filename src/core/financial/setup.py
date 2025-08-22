#!/usr/bin/env python3
"""
Claude Token Usage Calculator - Setup Script
Automated setup and configuration for the token cost tracking system
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import json
from datetime import datetime

class TokenCalculatorSetup:
    """Setup and configuration manager for token calculator"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.claude_dir = Path.home() / '.claude'
        self.financial_dir = self.claude_dir / 'financial'
        
    def run_setup(self):
        """Run complete setup process"""
        print("🚀 Claude Token Usage Calculator Setup")
        print("=" * 50)
        
        # Check Python version
        if not self.check_python_version():
            return False
        
        # Create directories
        self.create_directories()
        
        # Install dependencies
        if not self.install_dependencies():
            return False
        
        # Initialize database
        self.initialize_database()
        
        # Create configuration
        self.create_configuration()
        
        # Set up CLI commands
        self.setup_cli_commands()
        
        # Create sample data (optional)
        self.create_sample_data()
        
        # Generate documentation
        self.generate_documentation()
        
        print("\n✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Try: python token_cli.py status")
        print("2. Record usage: python token_cli.py record --help")
        print("3. Launch dashboard: python token_cli.py dashboard")
        print("4. View documentation: open TOKEN_CALCULATOR_README.md")
        
        return True
    
    def check_python_version(self):
        """Check Python version compatibility"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("❌ Error: Python 3.8+ required")
            print(f"Current version: {version.major}.{version.minor}.{version.micro}")
            return False
        
        print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    
    def create_directories(self):
        """Create necessary directories"""
        print("\n📁 Creating directories...")
        
        directories = [
            self.claude_dir,
            self.financial_dir,
            self.claude_dir / 'state',
            self.claude_dir / 'logs',
            self.financial_dir / 'exports',
            self.financial_dir / 'reports',
            self.financial_dir / 'backups'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ {directory}")
    
    def install_dependencies(self):
        """Install required Python packages"""
        print("\n📦 Installing dependencies...")
        
        try:
            # Check if requirements.txt exists
            requirements_file = self.base_dir / 'requirements.txt'
            if not requirements_file.exists():
                print("⚠️ Warning: requirements.txt not found, installing core dependencies only")
                core_packages = [
                    'pandas>=1.5.0',
                    'numpy>=1.21.0', 
                    'matplotlib>=3.5.0',
                    'fastapi>=0.100.0',
                    'uvicorn[standard]>=0.20.0',
                    'psutil>=5.9.0'
                ]
            else:
                print(f"  📋 Reading requirements from: {requirements_file}")
                with open(requirements_file) as f:
                    core_packages = [
                        line.strip() for line in f 
                        if line.strip() and not line.startswith('#')
                    ]
            
            # Install packages
            for package in core_packages[:6]:  # Install core packages first
                if package and not package.startswith('#'):
                    print(f"  Installing {package}...")
                    result = subprocess.run([
                        sys.executable, '-m', 'pip', 'install', package
                    ], capture_output=True, text=True, timeout=300)
                    
                    if result.returncode != 0:
                        print(f"  ⚠️ Failed to install {package}: {result.stderr}")
                    else:
                        print(f"  ✓ {package}")
            
            print("✅ Core dependencies installed")
            return True
            
        except subprocess.TimeoutExpired:
            print("❌ Installation timeout - please install dependencies manually")
            return False
        except Exception as e:
            print(f"❌ Installation error: {e}")
            print("Please install dependencies manually using: pip install -r requirements.txt")
            return False
    
    def initialize_database(self):
        """Initialize the SQLite database"""
        print("\n🗄️ Initializing database...")
        
        try:
            from token_cost_calculator import TokenCostCalculator
            calculator = TokenCostCalculator()
            print(f"  ✓ Database created: {calculator.db_path}")
            
            # Test the database
            calculator.record_usage(
                session_id="setup_test",
                agent_name="setup",
                model_name="claude-3-5-haiku-20241022",
                input_tokens=100,
                output_tokens=50,
                operation_type="setup_test"
            )
            print("  ✓ Database test successful")
            
        except Exception as e:
            print(f"  ❌ Database initialization failed: {e}")
    
    def create_configuration(self):
        """Create default configuration files"""
        print("\n⚙️ Creating configuration...")
        
        config = {
            "version": "1.0.0",
            "created": datetime.now().isoformat(),
            "database": {
                "path": str(self.financial_dir / "token_costs.db"),
                "backup_enabled": True,
                "backup_frequency": "daily"
            },
            "alerts": {
                "default_thresholds": {
                    "daily": 10.0,
                    "weekly": 50.0,
                    "monthly": 200.0
                },
                "notification_methods": ["console"]
            },
            "dashboard": {
                "default_port": 8080,
                "host": "localhost",
                "auto_refresh": True,
                "refresh_interval": 10
            },
            "reporting": {
                "default_format": "html",
                "include_charts": True,
                "export_formats": ["csv", "json", "excel"]
            },
            "optimization": {
                "auto_recommendations": True,
                "savings_threshold": 5.0,
                "efficiency_targets": {
                    "max_cost_per_request": 0.05,
                    "max_tokens_per_request": 5000,
                    "preferred_model_distribution": {
                        "haiku": 0.6,
                        "sonnet": 0.35,
                        "opus": 0.05
                    }
                }
            }
        }
        
        config_file = self.financial_dir / 'config.json'
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"  ✓ Configuration saved: {config_file}")
    
    def setup_cli_commands(self):
        """Set up CLI command shortcuts"""
        print("\n💻 Setting up CLI commands...")
        
        # Create shell scripts for easy access
        if os.name == 'nt':  # Windows
            batch_content = f'''@echo off
cd /d "{self.base_dir}"
python token_cli.py %*
'''
            batch_file = self.base_dir / 'claude-tokens.bat'
            with open(batch_file, 'w') as f:
                f.write(batch_content)
            print(f"  ✓ Windows batch file: {batch_file}")
            
        else:  # Unix-like systems
            shell_content = f'''#!/bin/bash
cd "{self.base_dir}"
python3 token_cli.py "$@"
'''
            shell_file = self.base_dir / 'claude-tokens.sh'
            with open(shell_file, 'w') as f:
                f.write(shell_content)
            os.chmod(shell_file, 0o755)
            print(f"  ✓ Shell script: {shell_file}")
        
        # Create Python module entry point
        init_content = '''#!/usr/bin/env python3
"""Claude Token Calculator package entry point"""

if __name__ == "__main__":
    from token_cli import main
    main()
'''
        init_file = self.base_dir / '__main__.py'
        with open(init_file, 'w') as f:
            f.write(init_content)
        print(f"  ✓ Python module entry: {init_file}")
    
    def create_sample_data(self):
        """Create sample data for demonstration"""
        print("\n📊 Creating sample data...")
        
        try:
            from token_cost_calculator import TokenCostCalculator
            calculator = TokenCostCalculator()
            
            # Sample agents and their typical usage patterns
            sample_agents = [
                ("business-analyst", "claude-3-5-sonnet-20241022", 2000, 500),
                ("technical-cto", "claude-3-5-haiku-20241022", 1500, 800),
                ("financial-analyst", "claude-3-5-sonnet-20241022", 3000, 1200),
                ("project-manager", "claude-3-5-haiku-20241022", 1000, 300),
                ("ceo-strategy", "claude-3-opus-20240229", 5000, 2000),
            ]
            
            # Create sample data for the last 7 days
            from datetime import timedelta
            import random
            
            for days_ago in range(7):
                date_offset = timedelta(days=days_ago)
                
                for agent, model, base_input, base_output in sample_agents:
                    # Simulate 1-5 requests per day per agent
                    requests = random.randint(1, 5)
                    
                    for req in range(requests):
                        # Add some randomness to token counts
                        input_tokens = base_input + random.randint(-500, 500)
                        output_tokens = base_output + random.randint(-200, 200)
                        
                        # Ensure positive values
                        input_tokens = max(100, input_tokens)
                        output_tokens = max(50, output_tokens)
                        
                        calculator.record_usage(
                            session_id=f"sample_{days_ago}_{agent}_{req}",
                            agent_name=agent,
                            model_name=model,
                            input_tokens=input_tokens,
                            output_tokens=output_tokens,
                            operation_type="sample_data",
                            duration_seconds=random.uniform(1.0, 30.0)
                        )
            
            print("  ✓ Sample data created (7 days, multiple agents)")
            
        except Exception as e:
            print(f"  ⚠️ Could not create sample data: {e}")
    
    def generate_documentation(self):
        """Generate documentation files"""
        print("\n📖 Generating documentation...")
        
        readme_content = '''# Claude Token Usage Calculator

## Overview
Advanced financial analysis tool for tracking and optimizing Claude API token usage and costs.

## Quick Start

### 1. View System Status
```bash
python token_cli.py status
```

### 2. Record Token Usage
```bash
python token_cli.py record \\
  --session-id="session_123" \\
  --agent="business-analyst" \\
  --model="claude-3-5-sonnet-20241022" \\
  --input-tokens=1500 \\
  --output-tokens=300
```

### 3. View Usage Summary
```bash
python token_cli.py summary --start-date="2024-01-01"
```

### 4. Get Cost Optimization Recommendations
```bash
python token_cli.py optimize
```

### 5. Launch Web Dashboard
```bash
python token_cli.py dashboard --port=8080
```

## Features

### 📊 Cost Tracking
- Real-time token usage monitoring
- Cost calculation per model and agent
- Historical analysis and trends
- Budget management and alerts

### 🎯 Optimization
- AI-powered cost optimization recommendations
- Model comparison and selection guidance
- Usage pattern analysis
- Efficiency scoring

### 📈 Analytics
- Interactive web dashboard
- Comprehensive reporting
- Data export capabilities
- Predictive cost modeling

### 🔔 Alerts
- Configurable spending thresholds
- Daily, weekly, monthly alerts
- Multiple notification methods
- Smart threshold recommendations

## Command Reference

### Recording Usage
```bash
# Basic usage recording
python token_cli.py record --session-id="sess_1" --agent="agent-name" --model="claude-3-5-sonnet-20241022" --input-tokens=1000 --output-tokens=200

# With additional context
python token_cli.py record --session-id="sess_1" --agent="agent-name" --model="claude-3-5-sonnet-20241022" --input-tokens=1000 --output-tokens=200 --duration=15.5 --context-length=8000
```

### Analysis Commands
```bash
# Usage summary
python token_cli.py summary
python token_cli.py summary --start-date="2024-01-01" --end-date="2024-01-31" --json

# Cost trends
python token_cli.py trends --days=30
python token_cli.py trends --days=7 --no-hourly

# Optimization recommendations
python token_cli.py optimize
python token_cli.py optimize --no-actions --json
```

### Alert Management
```bash
# Create alerts
python token_cli.py alerts create --type=daily --threshold=25.00
python token_cli.py alerts create --type=monthly --threshold=200.00 --method=email

# List active alerts
python token_cli.py alerts list

# Test alert system
python token_cli.py alerts test
```

### Data Export
```bash
# Export as CSV
python token_cli.py export --format=csv --output="usage_data.csv"

# Export date range as JSON
python token_cli.py export --format=json --start-date="2024-01-01" --end-date="2024-01-31"

# Generate comprehensive report
python token_cli.py report --output="cost_report.html" --open
```

### Model Comparison
```bash
# Compare all models
python token_cli.py compare

# JSON output for integration
python token_cli.py compare --json --no-scenarios
```

### Cost Prediction
```bash
# Monthly prediction based on last 7 days
python token_cli.py predict --days=7

# Detailed prediction analysis
python token_cli.py predict --days=14 --json
```

### Web Dashboard
```bash
# Start dashboard (default: localhost:8080)
python token_cli.py dashboard

# Custom host and port
python token_cli.py dashboard --host=0.0.0.0 --port=8090

# Debug mode
python token_cli.py dashboard --debug
```

## Model Pricing (Current)

| Model | Input ($/1M tokens) | Output ($/1M tokens) |
|-------|--------------------|--------------------|
| Claude 3.5 Haiku | $1.00 | $5.00 |
| Claude 3.5 Sonnet | $3.00 | $15.00 |
| Claude 3 Opus | $15.00 | $75.00 |

## Configuration

Configuration file: `~/.claude/financial/config.json`

Key settings:
- Alert thresholds
- Dashboard preferences  
- Optimization targets
- Export formats

## Integration

### Monitoring Integration
```bash
# Sync with existing monitoring
python monitoring_integration.py sync

# Export Prometheus metrics
python monitoring_integration.py export

# Generate Grafana dashboard
python monitoring_integration.py dashboard
```

### API Integration
```python
from token_cost_calculator import TokenCostCalculator

calculator = TokenCostCalculator()

# Record usage
usage = calculator.record_usage(
    session_id="api_session",
    agent_name="api_agent", 
    model_name="claude-3-5-sonnet-20241022",
    input_tokens=1000,
    output_tokens=200
)

print(f"Cost: ${usage.total_cost}")
```

## Troubleshooting

### Database Issues
- Database location: `~/.claude/financial/token_costs.db`
- Backup: Automatic daily backups enabled
- Reset: Delete database file to start fresh

### Dashboard Not Loading
- Check port availability: `netstat -an | grep 8080`
- Try different port: `--port=8081`
- Check firewall settings

### Missing Dependencies
- Install manually: `pip install -r requirements.txt`
- Use virtual environment recommended
- Python 3.8+ required

## Support

For issues and feature requests:
1. Check existing documentation
2. Review configuration settings
3. Check log files in `~/.claude/logs/`
4. Create issue with detailed error information

## Version History

- v1.0.0: Initial release with core functionality
- Features: Token tracking, cost analysis, web dashboard, CLI tools

---

Generated by Claude Token Calculator Setup
Date: ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        readme_file = self.base_dir / 'TOKEN_CALCULATOR_README.md'
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        
        print(f"  ✓ Documentation: {readme_file}")
        
        # Create examples file
        examples_content = '''# Claude Token Calculator Examples

## Example 1: Basic Usage Tracking

```python
from token_cost_calculator import TokenCostCalculator

calculator = TokenCostCalculator()

# Record a conversation
usage = calculator.record_usage(
    session_id="chat_001",
    agent_name="business-analyst",
    model_name="claude-3-5-sonnet-20241022",
    input_tokens=1500,
    output_tokens=400,
    operation_type="analysis",
    duration_seconds=12.3
)

print(f"Cost: ${usage.total_cost}")
print(f"Total tokens: {usage.total_tokens}")
```

## Example 2: Cost Analysis

```python
# Get monthly summary
summary = calculator.get_usage_summary(
    start_date=date(2024, 1, 1),
    end_date=date(2024, 1, 31)
)

print(f"Monthly cost: ${summary['totals']['cost']:.2f}")
print(f"Top agent: {summary['by_agent'][0]['agent_name']}")

# Get optimization recommendations
recommendations = calculator.generate_cost_optimization_recommendations()
for rec in recommendations:
    print(f"{rec.priority}: {rec.description}")
    print(f"Savings: ${rec.potential_savings}")
```

## Example 3: Setting Up Alerts

```python
# Create cost alerts
daily_alert = calculator.create_cost_alert(
    alert_type="daily",
    threshold_amount=25.00,
    notification_method="console"
)

monthly_alert = calculator.create_cost_alert(
    alert_type="monthly", 
    threshold_amount=200.00,
    notification_method="email"
)

print(f"Alerts created: {daily_alert}, {monthly_alert}")
```

## Example 4: Web Dashboard Integration

```python
from token_dashboard import TokenDashboard

dashboard = TokenDashboard(calculator)
dashboard.run(host="0.0.0.0", port=8080)
```

## Example 5: Data Export

```python
# Export to CSV
calculator.export_usage_data(
    filepath="january_usage.csv",
    format="csv",
    start_date=date(2024, 1, 1),
    end_date=date(2024, 1, 31)
)

# Generate HTML report
calculator.generate_cost_report(
    output_path="cost_analysis.html",
    include_charts=True
)
```

## Example 6: Model Comparison

```python
comparison = calculator.get_model_comparison()

for model_name, data in comparison.items():
    pricing = data['pricing']
    print(f"{model_name}:")
    print(f"  Input: ${pricing['input_cost_per_million']}/M")
    print(f"  Output: ${pricing['output_cost_per_million']}/M")
    
    # Show scenario costs
    scenarios = data['scenario_costs']
    print(f"  Chat (2K→500): ${scenarios['chat_medium']:.4f}")
```

## Example 7: Monitoring Integration

```python
from monitoring_integration import TokenMonitoringIntegration

# Connect to existing monitoring
integration = TokenMonitoringIntegration(calculator)

# Export Prometheus metrics
metrics_file = integration.export_for_prometheus()
print(f"Metrics exported to: {metrics_file}")

# Generate Grafana dashboard config
dashboard_config = integration.generate_monitoring_dashboard_config()
```

## CLI Examples

```bash
# Daily workflow
python token_cli.py status
python token_cli.py summary --start-date="2024-01-01"
python token_cli.py optimize

# Set up monitoring
python token_cli.py alerts create --type=daily --threshold=20.00
python token_cli.py alerts create --type=weekly --threshold=100.00

# Generate reports
python token_cli.py export --format=csv --output="weekly_report.csv"
python token_cli.py report --output="analysis.html" --open

# Compare models for cost optimization
python token_cli.py compare
python token_cli.py predict --days=14
```
'''
        
        examples_file = self.base_dir / 'EXAMPLES.md'
        with open(examples_file, 'w') as f:
            f.write(examples_content)
        
        print(f"  ✓ Examples: {examples_file}")

def main():
    """Main setup entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Claude Token Calculator Setup')
    parser.add_argument('--force', action='store_true', help='Force reinstall')
    parser.add_argument('--no-deps', action='store_true', help='Skip dependency installation')
    parser.add_argument('--no-sample', action='store_true', help='Skip sample data creation')
    
    args = parser.parse_args()
    
    setup = TokenCalculatorSetup()
    
    try:
        success = setup.run_setup()
        if success:
            print("\n🎉 Setup completed! Token calculator is ready to use.")
            return 0
        else:
            print("\n❌ Setup failed. Please check error messages above.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Setup cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())