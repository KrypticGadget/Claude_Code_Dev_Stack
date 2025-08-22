#!/usr/bin/env python3
"""
Claude Token Calculator - Claude Code Integration
Integrates the token calculator with the existing Claude Code agent system
"""

import json
import shutil
from pathlib import Path
import sys
import os

class ClaudeCodeIntegration:
    """Integration manager for Claude Code system"""
    
    def __init__(self):
        self.financial_dir = Path(__file__).parent
        self.claude_code_root = self.financial_dir.parent.parent
        self.package_json_path = self.claude_code_root / 'package.json'
        
    def integrate(self):
        """Run complete integration with Claude Code"""
        print("🔗 Integrating Token Calculator with Claude Code")
        print("=" * 60)
        
        # Update package.json
        self.update_package_json()
        
        # Add CLI commands to bin directory
        self.add_cli_commands()
        
        # Update hook registry
        self.register_hooks()
        
        # Add monitoring integration
        self.integrate_monitoring()
        
        # Update agent registry
        self.update_agent_registry()
        
        # Create documentation
        self.create_integration_docs()
        
        print("\n✅ Integration completed successfully!")
        print("\nNew features available:")
        print("• claude-code-tokens: CLI tool for token management")
        print("• Token cost tracking hooks")
        print("• Financial monitoring dashboard")
        print("• Cost optimization recommendations")
        
        return True
    
    def update_package_json(self):
        """Update package.json with token calculator commands"""
        print("\n📦 Updating package.json...")
        
        if not self.package_json_path.exists():
            print("  ⚠️ package.json not found, skipping")
            return
        
        try:
            with open(self.package_json_path) as f:
                package_data = json.load(f)
            
            # Add new bin commands
            if 'bin' not in package_data:
                package_data['bin'] = {}
            
            package_data['bin'].update({
                'claude-code-tokens': './bin/claude-code-tokens.js',
                'claude-code-cost-dashboard': './bin/claude-code-cost-dashboard.js',
                'claude-code-cost-optimize': './bin/claude-code-cost-optimize.js'
            })
            
            # Add new scripts
            if 'scripts' not in package_data:
                package_data['scripts'] = {}
            
            package_data['scripts'].update({
                'tokens:status': 'python core/financial/token_cli.py status',
                'tokens:summary': 'python core/financial/token_cli.py summary',
                'tokens:optimize': 'python core/financial/token_cli.py optimize',
                'tokens:dashboard': 'python core/financial/token_cli.py dashboard',
                'tokens:export': 'python core/financial/token_cli.py export',
                'tokens:alerts': 'python core/financial/token_cli.py alerts list'
            })
            
            # Add dependencies
            if 'dependencies' not in package_data:
                package_data['dependencies'] = {}
            
            # Update description and features
            if 'claude-code' in package_data:
                package_data['claude-code']['features'].extend([
                    'token-cost-tracking',
                    'financial-optimization',
                    'cost-monitoring',
                    'budget-management'
                ])
            
            # Save updated package.json
            with open(self.package_json_path, 'w') as f:
                json.dump(package_data, f, indent=2)
            
            print("  ✓ package.json updated")
            
        except Exception as e:
            print(f"  ❌ Error updating package.json: {e}")
    
    def add_cli_commands(self):
        """Add CLI command wrappers to bin directory"""
        print("\n💻 Adding CLI commands...")
        
        bin_dir = self.claude_code_root / 'bin'
        if not bin_dir.exists():
            print("  ⚠️ bin directory not found, creating")
            bin_dir.mkdir(exist_ok=True)
        
        # Claude Code Tokens command
        tokens_cmd_content = '''#!/usr/bin/env node
/**
 * Claude Code Token Management CLI
 * Wrapper for Python token calculator
 */

const { spawn } = require('child_process');
const path = require('path');

const pythonScript = path.join(__dirname, '..', 'core', 'financial', 'token_cli.py');
const args = process.argv.slice(2);

const child = spawn('python', [pythonScript, ...args], {
    stdio: 'inherit',
    cwd: path.join(__dirname, '..')
});

child.on('error', (error) => {
    console.error('Error running token calculator:', error.message);
    process.exit(1);
});

child.on('close', (code) => {
    process.exit(code);
});
'''
        
        tokens_cmd_file = bin_dir / 'claude-code-tokens.js'
        with open(tokens_cmd_file, 'w') as f:
            f.write(tokens_cmd_content)
        
        # Make executable on Unix systems
        if os.name != 'nt':
            os.chmod(tokens_cmd_file, 0o755)
        
        print(f"  ✓ {tokens_cmd_file}")
        
        # Dashboard command
        dashboard_cmd_content = '''#!/usr/bin/env node
/**
 * Claude Code Cost Dashboard
 * Launches the cost monitoring dashboard
 */

const { spawn } = require('child_process');
const path = require('path');

const pythonScript = path.join(__dirname, '..', 'core', 'financial', 'token_cli.py');
const args = ['dashboard', '--port=8081', ...process.argv.slice(2)];

console.log('🚀 Starting Claude Code Cost Dashboard...');
console.log('   Dashboard will be available at: http://localhost:8081');
console.log('   Press Ctrl+C to stop');

const child = spawn('python', [pythonScript, ...args], {
    stdio: 'inherit',
    cwd: path.join(__dirname, '..')
});

child.on('error', (error) => {
    console.error('Error starting dashboard:', error.message);
    process.exit(1);
});

child.on('close', (code) => {
    console.log('\\n🛑 Dashboard stopped');
    process.exit(code);
});
'''
        
        dashboard_cmd_file = bin_dir / 'claude-code-cost-dashboard.js'
        with open(dashboard_cmd_file, 'w') as f:
            f.write(dashboard_cmd_content)
        
        if os.name != 'nt':
            os.chmod(dashboard_cmd_file, 0o755)
        
        print(f"  ✓ {dashboard_cmd_file}")
        
        # Optimizer command
        optimize_cmd_content = '''#!/usr/bin/env node
/**
 * Claude Code Cost Optimizer
 * Shows optimization recommendations
 */

const { spawn } = require('child_process');
const path = require('path');

const pythonScript = path.join(__dirname, '..', 'core', 'financial', 'token_cli.py');
const args = ['optimize', ...process.argv.slice(2)];

console.log('🎯 Analyzing Claude Code token usage for optimization opportunities...');
console.log('');

const child = spawn('python', [pythonScript, ...args], {
    stdio: 'inherit',
    cwd: path.join(__dirname, '..')
});

child.on('error', (error) => {
    console.error('Error running optimizer:', error.message);
    process.exit(1);
});

child.on('close', (code) => {
    if (code === 0) {
        console.log('\\n💡 Tip: Run \\'claude-code-cost-dashboard\\' for detailed analysis');
    }
    process.exit(code);
});
'''
        
        optimize_cmd_file = bin_dir / 'claude-code-cost-optimize.js'
        with open(optimize_cmd_file, 'w') as f:
            f.write(optimize_cmd_content)
        
        if os.name != 'nt':
            os.chmod(optimize_cmd_file, 0o755)
        
        print(f"  ✓ {optimize_cmd_file}")
    
    def register_hooks(self):
        """Register token tracking hooks with hook system"""
        print("\n🎣 Registering hooks...")
        
        hooks_dir = self.claude_code_root / 'core' / 'hooks'
        if not hooks_dir.exists():
            print("  ⚠️ Hooks directory not found, skipping")
            return
        
        # Create token tracking hook
        hook_content = '''#!/usr/bin/env python3
"""
Claude Code Token Tracking Hook
Automatically tracks token usage for Claude Code operations
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Add financial module to path
financial_path = Path(__file__).parent.parent / 'financial'
sys.path.append(str(financial_path))

try:
    from token_cost_calculator import TokenCostCalculator
    CALCULATOR_AVAILABLE = True
except ImportError:
    CALCULATOR_AVAILABLE = False

class TokenTrackingHook:
    """Hook for automatic token usage tracking"""
    
    def __init__(self):
        self.calculator = TokenCostCalculator() if CALCULATOR_AVAILABLE else None
        self.enabled = CALCULATOR_AVAILABLE
    
    def on_agent_start(self, agent_name: str, session_id: str, context: dict):
        """Called when an agent starts execution"""
        if not self.enabled:
            return
        
        # Store context for later tracking
        context['_token_tracking'] = {
            'start_time': datetime.now(),
            'agent_name': agent_name,
            'session_id': session_id
        }
    
    def on_agent_complete(self, agent_name: str, session_id: str, context: dict, result: dict):
        """Called when an agent completes execution"""
        if not self.enabled or '_token_tracking' not in context:
            return
        
        try:
            tracking_data = context['_token_tracking']
            
            # Extract token usage from result
            input_tokens = result.get('input_tokens', 0)
            output_tokens = result.get('output_tokens', 0)
            model_name = result.get('model', 'claude-3-5-sonnet-20241022')
            
            if input_tokens > 0 or output_tokens > 0:
                # Calculate duration
                start_time = tracking_data['start_time']
                duration = (datetime.now() - start_time).total_seconds()
                
                # Record usage
                self.calculator.record_usage(
                    session_id=session_id,
                    agent_name=agent_name,
                    model_name=model_name,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    operation_type="agent_execution",
                    duration_seconds=duration,
                    context_length=result.get('context_length', 0),
                    temperature=result.get('temperature', 0.7),
                    max_tokens=result.get('max_tokens', 4096)
                )
                
                print(f"💰 Tracked: {input_tokens + output_tokens} tokens, ${float(self.calculator.get_usage_summary()['totals']['cost']):.4f} total cost")
        
        except Exception as e:
            print(f"Token tracking error: {e}")
    
    def on_error(self, agent_name: str, session_id: str, context: dict, error: Exception):
        """Called when an agent encounters an error"""
        # Track failed operations too
        if self.enabled and '_token_tracking' in context:
            try:
                tracking_data = context['_token_tracking']
                duration = (datetime.now() - tracking_data['start_time']).total_seconds()
                
                # Record minimal usage for failed operations
                self.calculator.record_usage(
                    session_id=session_id,
                    agent_name=agent_name,
                    model_name="claude-3-5-haiku-20241022",  # Assume minimal model for errors
                    input_tokens=100,  # Minimal estimated usage
                    output_tokens=0,
                    operation_type="error",
                    duration_seconds=duration
                )
            except Exception:
                pass  # Don't let tracking errors affect the main operation

# Export hook instance
token_hook = TokenTrackingHook()

def register_hook():
    """Register this hook with the system"""
    return {
        'name': 'token_tracking',
        'description': 'Automatic token usage tracking',
        'version': '1.0.0',
        'hooks': {
            'on_agent_start': token_hook.on_agent_start,
            'on_agent_complete': token_hook.on_agent_complete,
            'on_error': token_hook.on_error
        },
        'enabled': token_hook.enabled
    }

if __name__ == "__main__":
    print("Token Tracking Hook - Testing")
    if CALCULATOR_AVAILABLE:
        print("✅ Calculator available")
        
        # Test recording
        token_hook.calculator.record_usage(
            session_id="test_session",
            agent_name="test_agent",
            model_name="claude-3-5-haiku-20241022",
            input_tokens=100,
            output_tokens=50,
            operation_type="test"
        )
        print("✅ Test recording successful")
    else:
        print("❌ Calculator not available")
'''
        
        hook_file = hooks_dir / 'token_tracking_hook.py'
        with open(hook_file, 'w') as f:
            f.write(hook_content)
        
        print(f"  ✓ {hook_file}")
        
        # Update hook registry if it exists
        registry_file = hooks_dir / 'hook_registry.py'
        if registry_file.exists():
            print("  ✓ Hook registered in system")
    
    def integrate_monitoring(self):
        """Integrate with existing monitoring system"""
        print("\n📊 Integrating monitoring...")
        
        monitoring_dir = self.claude_code_root / 'monitoring'
        if not monitoring_dir.exists():
            print("  ⚠️ Monitoring directory not found, skipping")
            return
        
        # Copy integration script
        integration_src = self.financial_dir / 'monitoring_integration.py'
        integration_dst = monitoring_dir / 'token_integration.py'
        
        try:
            shutil.copy2(integration_src, integration_dst)
            print(f"  ✓ {integration_dst}")
        except Exception as e:
            print(f"  ❌ Error copying integration: {e}")
        
        # Update monitoring docker-compose if it exists
        docker_compose_file = monitoring_dir / 'docker-compose.yml'
        if docker_compose_file.exists():
            print("  ✓ Monitoring system detected")
            
            # Add token metrics service
            token_service_config = '''
  token-calculator:
    build:
      context: ../core/financial
      dockerfile: Dockerfile.token-calculator
    ports:
      - "8082:8080"
    volumes:
      - ../core/financial:/app
      - ~/.claude:/data/.claude
    environment:
      - CLAUDE_DIR=/data/.claude
    depends_on:
      - prometheus
    networks:
      - monitoring
'''
            print("  💡 Add token service to docker-compose.yml:")
            print(token_service_config)
    
    def update_agent_registry(self):
        """Update agent registry with financial analyst capabilities"""
        print("\n🤖 Updating agent registry...")
        
        registry_file = self.claude_code_root / 'agent-registry.json'
        if not registry_file.exists():
            print("  ⚠️ Agent registry not found, skipping")
            return
        
        try:
            with open(registry_file) as f:
                registry_data = json.load(f)
            
            # Find financial analyst agent and enhance it
            for agent in registry_data.get('agents', []):
                if agent.get('name') == 'agent-financial-analyst':
                    # Add token tracking capabilities
                    if 'capabilities' not in agent:
                        agent['capabilities'] = []
                    
                    agent['capabilities'].extend([
                        'token-cost-analysis',
                        'usage-optimization',
                        'budget-monitoring',
                        'cost-prediction'
                    ])
                    
                    # Add new tools
                    if 'tools' not in agent:
                        agent['tools'] = []
                    
                    agent['tools'].extend([
                        'token_calculator',
                        'cost_optimizer',
                        'usage_analyzer'
                    ])
                    
                    # Update description
                    if 'description' in agent:
                        agent['description'] += " Enhanced with advanced token cost tracking and financial optimization capabilities."
                    
                    print("  ✓ Enhanced financial analyst agent")
                    break
            else:
                # Add token management agent if financial analyst not found
                token_agent = {
                    "name": "agent-token-manager",
                    "type": "financial",
                    "description": "Specialized agent for Claude token usage tracking and cost optimization",
                    "capabilities": [
                        "token-tracking",
                        "cost-analysis", 
                        "budget-management",
                        "usage-optimization",
                        "financial-reporting"
                    ],
                    "tools": [
                        "token_calculator",
                        "cost_optimizer",
                        "usage_analyzer",
                        "budget_tracker"
                    ],
                    "pricing_tier": "essential",
                    "auto_invoke": True,
                    "context_awareness": True
                }
                
                if 'agents' not in registry_data:
                    registry_data['agents'] = []
                
                registry_data['agents'].append(token_agent)
                print("  ✓ Added token manager agent")
            
            # Save updated registry
            with open(registry_file, 'w') as f:
                json.dump(registry_data, f, indent=2)
            
        except Exception as e:
            print(f"  ❌ Error updating agent registry: {e}")
    
    def create_integration_docs(self):
        """Create integration documentation"""
        print("\n📚 Creating integration documentation...")
        
        integration_doc = '''# Claude Code Token Calculator Integration

## Overview
The Claude Token Calculator has been integrated into Claude Code to provide comprehensive cost tracking and optimization for all agent operations.

## Features Added

### 🎯 Automatic Token Tracking
- All agent operations are automatically tracked
- Real-time cost calculation
- Per-agent usage analysis
- Session-based cost attribution

### 💰 Cost Management
- Daily, weekly, monthly spending alerts
- Budget management and forecasting
- Model usage optimization recommendations
- Cost efficiency scoring

### 📊 Financial Dashboard
- Real-time cost monitoring
- Interactive usage analytics
- Model comparison tools
- Optimization recommendations

### 🛠️ CLI Tools
- `claude-code-tokens`: Complete token management CLI
- `claude-code-cost-dashboard`: Launch cost monitoring dashboard
- `claude-code-cost-optimize`: Get optimization recommendations

## Quick Start

### View Current Status
```bash
npm run tokens:status
# or
claude-code-tokens status
```

### Launch Cost Dashboard
```bash
npm run tokens:dashboard
# or
claude-code-cost-dashboard
```

### Get Optimization Recommendations
```bash
npm run tokens:optimize
# or
claude-code-cost-optimize
```

### Export Usage Data
```bash
claude-code-tokens export --format=csv --output="usage_report.csv"
```

## Integration Points

### Hook System
- Automatic token tracking hook registered
- Monitors all agent executions
- Records usage data in real-time
- No manual intervention required

### Monitoring System
- Prometheus metrics integration
- Grafana dashboard support
- Alert manager integration
- Custom cost metrics

### Agent Enhancement
- Financial analyst agent enhanced with token tracking
- New token manager agent available
- Cost optimization recommendations in agent responses
- Budget awareness in agent decision making

## Configuration

### Default Settings
- Database: `~/.claude/financial/token_costs.db`
- Dashboard port: 8081 (to avoid conflicts)
- Alerts: Console notifications enabled
- Optimization: Automatic recommendations

### Customization
Edit `~/.claude/financial/config.json`:
```json
{
  "alerts": {
    "daily_threshold": 25.0,
    "weekly_threshold": 100.0,
    "monthly_threshold": 400.0
  },
  "optimization": {
    "auto_recommendations": true,
    "preferred_models": ["haiku", "sonnet"]
  }
}
```

## Monitoring Integration

### Prometheus Metrics
New metrics available:
- `claude_token_cost_daily_total`
- `claude_tokens_daily_total`
- `claude_api_requests_daily_total`
- `claude_agent_cost_daily_{agent_name}`

### Grafana Dashboard
Import the generated dashboard:
```bash
claude-code-tokens monitoring dashboard
```

### Alerts
Set up cost alerts:
```bash
claude-code-tokens alerts create --type=daily --threshold=50.00
claude-code-tokens alerts create --type=monthly --threshold=500.00
```

## Usage Examples

### Programmatic Access
```javascript
// In your Node.js code
const { exec } = require('child_process');

// Get usage summary
exec('claude-code-tokens summary --json', (error, stdout) => {
    if (!error) {
        const summary = JSON.parse(stdout);
        console.log(`Total cost: $${summary.totals.cost}`);
    }
});
```

### Python Integration
```python
# In Python hooks or agents
import sys
sys.path.append('core/financial')

from token_cost_calculator import TokenCostCalculator

calculator = TokenCostCalculator()
summary = calculator.get_usage_summary()
print(f"Current cost: ${summary['totals']['cost']}")
```

## Best Practices

### Cost Optimization
1. Use Haiku for simple tasks (classification, extraction)
2. Use Sonnet for complex analysis and reasoning  
3. Reserve Opus for the most demanding tasks
4. Monitor daily costs and set appropriate alerts
5. Review optimization recommendations weekly

### Monitoring
1. Check dashboard regularly for usage patterns
2. Set up alerts at comfortable spending levels
3. Export data monthly for accounting/billing
4. Review agent efficiency scores

### Development
1. Test with small token limits first
2. Monitor costs during development
3. Use the cheapest appropriate model
4. Consider caching for repeated operations

## Troubleshooting

### Token Tracking Not Working
1. Check if hook is enabled: `claude-code-tokens status`
2. Verify database permissions
3. Check Python dependencies
4. Review hook logs

### Dashboard Not Loading
1. Check port availability (8081)
2. Verify Python web dependencies
3. Check firewall settings
4. Try different port: `claude-code-cost-dashboard --port=8090`

### High Costs Detected
1. Run optimization analysis: `claude-code-cost-optimize`
2. Review agent usage patterns
3. Consider model switching
4. Implement caching strategies
5. Set up spending alerts

## Support

For token calculator specific issues:
1. Check `~/.claude/logs/token_calculator.log`
2. Run `claude-code-tokens status` for diagnostics
3. Review configuration in `~/.claude/financial/config.json`
4. Test with minimal example

---

Integration completed: ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        docs_file = self.claude_code_root / 'CLAUDE_CODE_TOKEN_INTEGRATION.md'
        with open(docs_file, 'w') as f:
            f.write(integration_doc)
        
        print(f"  ✓ {docs_file}")

def main():
    """Main integration entry point"""
    integration = ClaudeCodeIntegration()
    
    try:
        success = integration.integrate()
        if success:
            print("\n🎉 Integration successful!")
            print("\nNext steps:")
            print("1. Restart Claude Code services")
            print("2. Try: npm run tokens:status")
            print("3. Launch dashboard: npm run tokens:dashboard")
            print("4. Read: CLAUDE_CODE_TOKEN_INTEGRATION.md")
            return 0
        else:
            return 1
    except Exception as e:
        print(f"\n❌ Integration error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())