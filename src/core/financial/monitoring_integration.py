#!/usr/bin/env python3
"""
Claude Token Calculator - Monitoring Integration
Integrates token cost tracking with existing Claude Code monitoring infrastructure
"""

import json
import time
import threading
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Dict, List, Optional, Any
import sqlite3
import sys
import os

# Add monitoring path to system path
monitoring_path = Path(__file__).parent.parent.parent / 'monitoring'
sys.path.append(str(monitoring_path))

try:
    from metrics.claude_metrics_collector import MetricsCollector
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False
    print("Warning: Monitoring system not available")

from token_cost_calculator import TokenCostCalculator

class TokenMonitoringIntegration:
    """Integration between token calculator and monitoring system"""
    
    def __init__(self, calculator: TokenCostCalculator, metrics_collector: Optional['MetricsCollector'] = None):
        self.calculator = calculator
        self.metrics_collector = metrics_collector
        self.claude_dir = Path.home() / '.claude'
        self.state_dir = self.claude_dir / 'state'
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # Integration state
        self.running = True
        self.sync_thread = None
        self.last_sync = datetime.now()
        
        # Start sync thread
        self.start_sync_thread()
    
    def start_sync_thread(self):
        """Start background synchronization thread"""
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
    
    def _sync_loop(self):
        """Background sync loop"""
        while self.running:
            try:
                self.sync_token_metrics()
                self.export_cost_metrics()
                self.update_performance_metrics()
                time.sleep(60)  # Sync every minute
            except Exception as e:
                print(f"Sync error: {e}")
                time.sleep(30)
    
    def sync_token_metrics(self):
        """Sync token usage data with monitoring system"""
        try:
            # Get recent token usage (last hour)
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=1)
            
            with sqlite3.connect(self.calculator.db_path) as conn:
                cursor = conn.execute('''
                    SELECT 
                        agent_name,
                        model_name,
                        SUM(total_tokens) as tokens,
                        SUM(total_cost) as cost,
                        COUNT(*) as requests,
                        AVG(duration_seconds) as avg_duration
                    FROM token_usage 
                    WHERE timestamp BETWEEN ? AND ?
                    GROUP BY agent_name, model_name
                ''', (start_time, end_time))
                
                metrics_data = {}
                for row in cursor:
                    agent_name, model_name, tokens, cost, requests, avg_duration = row
                    
                    if agent_name not in metrics_data:
                        metrics_data[agent_name] = {
                            'total_tokens': 0,
                            'total_cost': 0.0,
                            'total_requests': 0,
                            'models': {},
                            'avg_duration': 0.0
                        }
                    
                    metrics_data[agent_name]['total_tokens'] += tokens or 0
                    metrics_data[agent_name]['total_cost'] += cost or 0.0
                    metrics_data[agent_name]['total_requests'] += requests or 0
                    metrics_data[agent_name]['avg_duration'] = avg_duration or 0.0
                    metrics_data[agent_name]['models'][model_name] = {
                        'tokens': tokens or 0,
                        'cost': cost or 0.0,
                        'requests': requests or 0
                    }
                
                # Save to state file for monitoring system
                token_metrics_file = self.state_dir / 'token_metrics.json'
                with open(token_metrics_file, 'w') as f:
                    json.dump({
                        'timestamp': end_time.isoformat(),
                        'period_start': start_time.isoformat(),
                        'period_end': end_time.isoformat(),
                        'agents': metrics_data,
                        'summary': {
                            'total_tokens': sum(agent['total_tokens'] for agent in metrics_data.values()),
                            'total_cost': sum(agent['total_cost'] for agent in metrics_data.values()),
                            'total_requests': sum(agent['total_requests'] for agent in metrics_data.values()),
                            'unique_agents': len(metrics_data),
                            'unique_models': len(set(
                                model for agent in metrics_data.values() 
                                for model in agent['models'].keys()
                            ))
                        }
                    }, f, indent=2, default=str)
                
        except Exception as e:
            print(f"Error syncing token metrics: {e}")
    
    def export_cost_metrics(self):
        """Export cost metrics in Prometheus format"""
        try:
            # Get today's summary
            today_summary = self.calculator.get_usage_summary(
                start_date=date.today(),
                end_date=date.today()
            )
            
            # Get monthly summary
            month_start = date.today().replace(day=1)
            monthly_summary = self.calculator.get_usage_summary(
                start_date=month_start,
                end_date=date.today()
            )
            
            # Create Prometheus metrics
            prometheus_metrics = {
                'claude_token_cost_daily_total': {
                    'type': 'gauge',
                    'help': 'Daily token cost total in USD',
                    'value': today_summary['totals']['cost']
                },
                'claude_token_cost_monthly_total': {
                    'type': 'gauge',
                    'help': 'Monthly token cost total in USD',
                    'value': monthly_summary['totals']['cost']
                },
                'claude_tokens_daily_total': {
                    'type': 'gauge',
                    'help': 'Daily token usage total',
                    'value': today_summary['totals']['tokens']
                },
                'claude_tokens_monthly_total': {
                    'type': 'gauge',
                    'help': 'Monthly token usage total',
                    'value': monthly_summary['totals']['tokens']
                },
                'claude_api_requests_daily_total': {
                    'type': 'gauge',
                    'help': 'Daily API requests total',
                    'value': today_summary['totals']['requests']
                },
                'claude_cost_per_request_avg': {
                    'type': 'gauge',
                    'help': 'Average cost per API request',
                    'value': today_summary['totals']['avg_cost_per_request']
                },
                'claude_tokens_per_request_avg': {
                    'type': 'gauge',
                    'help': 'Average tokens per API request',
                    'value': today_summary['totals']['avg_tokens_per_request']
                }
            }
            
            # Add agent-specific metrics
            for agent in today_summary['by_agent'][:10]:  # Top 10 agents
                prometheus_metrics[f'claude_agent_cost_daily_{agent["agent_name"].replace("-", "_")}'] = {
                    'type': 'gauge',
                    'help': f'Daily cost for {agent["agent_name"]} agent',
                    'value': agent['cost'],
                    'labels': {'agent': agent['agent_name']}
                }
                
                prometheus_metrics[f'claude_agent_tokens_daily_{agent["agent_name"].replace("-", "_")}'] = {
                    'type': 'gauge',
                    'help': f'Daily tokens for {agent["agent_name"]} agent',
                    'value': agent['tokens'],
                    'labels': {'agent': agent['agent_name']}
                }
            
            # Add model-specific metrics
            for model in today_summary['by_model']:
                model_key = model['model_name'].replace('-', '_').replace('.', '_')
                prometheus_metrics[f'claude_model_cost_daily_{model_key}'] = {
                    'type': 'gauge',
                    'help': f'Daily cost for {model["model_name"]} model',
                    'value': model['cost'],
                    'labels': {'model': model['model_name']}
                }
            
            # Save metrics for Prometheus scraping
            prometheus_file = self.state_dir / 'token_prometheus_metrics.json'
            with open(prometheus_file, 'w') as f:
                json.dump(prometheus_metrics, f, indent=2, default=str)
            
            # Also create .prom file format
            prom_file = self.state_dir / 'token_metrics.prom'
            with open(prom_file, 'w') as f:
                for metric_name, metric_data in prometheus_metrics.items():
                    f.write(f"# HELP {metric_name} {metric_data['help']}\n")
                    f.write(f"# TYPE {metric_name} {metric_data['type']}\n")
                    
                    if 'labels' in metric_data:
                        label_str = ','.join(f'{k}="{v}"' for k, v in metric_data['labels'].items())
                        f.write(f"{metric_name}{{{label_str}}} {metric_data['value']}\n")
                    else:
                        f.write(f"{metric_name} {metric_data['value']}\n")
                    f.write("\n")
                
        except Exception as e:
            print(f"Error exporting cost metrics: {e}")
    
    def update_performance_metrics(self):
        """Update performance metrics with cost analysis"""
        try:
            # Get recommendations for performance insights
            recommendations = self.calculator.generate_cost_optimization_recommendations()
            
            # Analyze trends
            trends = self.calculator.get_cost_trends(7)
            
            # Create performance analysis
            performance_data = {
                'timestamp': datetime.now().isoformat(),
                'cost_optimization': {
                    'total_recommendations': len(recommendations),
                    'high_priority_count': len([r for r in recommendations if r.priority == "high"]),
                    'potential_savings': sum(float(r.potential_savings) for r in recommendations),
                    'categories': list(set(r.category for r in recommendations))
                },
                'cost_trends': {
                    'direction': trends['trend_analysis']['direction'],
                    'percentage_change': trends['trend_analysis']['percentage_change'],
                    'period_days': trends['trend_analysis']['period_days']
                },
                'efficiency_metrics': self._calculate_efficiency_metrics(),
                'alerts': {
                    'active_count': len([a for a in self.calculator.alerts if a.enabled]),
                    'recently_triggered': len([
                        a for a in self.calculator.alerts 
                        if a.last_triggered and a.last_triggered > datetime.now() - timedelta(hours=24)
                    ])
                }
            }
            
            # Save performance data
            performance_file = self.state_dir / 'token_performance_analysis.json'
            with open(performance_file, 'w') as f:
                json.dump(performance_data, f, indent=2, default=str)
            
            # Integrate with existing performance metrics if available
            if MONITORING_AVAILABLE and self.metrics_collector:
                self._update_monitoring_metrics(performance_data)
                
        except Exception as e:
            print(f"Error updating performance metrics: {e}")
    
    def _calculate_efficiency_metrics(self) -> Dict[str, Any]:
        """Calculate efficiency metrics"""
        try:
            # Get weekly summary
            week_summary = self.calculator.get_usage_summary(
                start_date=date.today() - timedelta(days=7),
                end_date=date.today()
            )
            
            # Calculate efficiency scores
            efficiency_metrics = {
                'cost_per_token': week_summary['totals']['cost'] / max(week_summary['totals']['tokens'], 1),
                'requests_per_day': week_summary['totals']['requests'] / 7,
                'tokens_per_request_efficiency': week_summary['totals']['avg_tokens_per_request'],
                'cost_efficiency_score': self._calculate_cost_efficiency_score(week_summary),
                'model_distribution_score': self._calculate_model_distribution_score(week_summary)
            }
            
            return efficiency_metrics
            
        except Exception as e:
            print(f"Error calculating efficiency metrics: {e}")
            return {}
    
    def _calculate_cost_efficiency_score(self, summary: Dict[str, Any]) -> float:
        """Calculate cost efficiency score (0-100)"""
        try:
            # Base score starts at 100
            score = 100.0
            
            # Penalty for high average cost per request
            avg_cost = summary['totals']['avg_cost_per_request']
            if avg_cost > 0.05:  # > $0.05 per request
                score -= min(30, (avg_cost - 0.05) * 1000)
            
            # Penalty for high token usage
            avg_tokens = summary['totals']['avg_tokens_per_request']
            if avg_tokens > 5000:  # > 5K tokens per request
                score -= min(20, (avg_tokens - 5000) / 100)
            
            # Bonus for using cheaper models
            total_cost = summary['totals']['cost']
            haiku_cost = sum(m['cost'] for m in summary['by_model'] if 'haiku' in m['model_name'].lower())
            if total_cost > 0:
                haiku_ratio = haiku_cost / total_cost
                score += haiku_ratio * 10  # Up to 10 points for using Haiku
            
            return max(0, min(100, score))
            
        except Exception:
            return 50.0  # Default neutral score
    
    def _calculate_model_distribution_score(self, summary: Dict[str, Any]) -> float:
        """Calculate model distribution efficiency score"""
        try:
            models = summary['by_model']
            if not models:
                return 50.0
            
            # Count model types
            model_counts = {'haiku': 0, 'sonnet': 0, 'opus': 0}
            total_cost = sum(m['cost'] for m in models)
            
            for model in models:
                name = model['model_name'].lower()
                cost_ratio = model['cost'] / max(total_cost, 0.001)
                
                if 'haiku' in name:
                    model_counts['haiku'] += cost_ratio
                elif 'sonnet' in name:
                    model_counts['sonnet'] += cost_ratio
                elif 'opus' in name:
                    model_counts['opus'] += cost_ratio
            
            # Ideal distribution: 60% Haiku, 35% Sonnet, 5% Opus
            ideal = {'haiku': 0.6, 'sonnet': 0.35, 'opus': 0.05}
            
            # Calculate distance from ideal
            distance = sum(abs(model_counts[model] - ideal[model]) for model in ideal)
            score = max(0, 100 - (distance * 100))
            
            return score
            
        except Exception:
            return 50.0
    
    def _update_monitoring_metrics(self, performance_data: Dict[str, Any]):
        """Update existing monitoring system with token metrics"""
        try:
            if not self.metrics_collector:
                return
            
            # Update token-related metrics in the monitoring system
            cost_data = performance_data['cost_optimization']
            
            # Record high-priority cost issues as performance issues
            if cost_data['high_priority_count'] > 0:
                self.metrics_collector.update_metric(
                    'claude_performance_issues_total',
                    cost_data['high_priority_count'],
                    {'issue_type': 'high_cost_usage'}
                )
            
            # Record potential savings
            if cost_data['potential_savings'] > 0:
                self.metrics_collector.update_metric(
                    'claude_cost_optimization_savings_potential',
                    cost_data['potential_savings']
                )
            
            # Record trend direction
            trend_direction = performance_data['cost_trends']['direction']
            trend_value = 1 if trend_direction == 'increasing' else 0
            self.metrics_collector.update_metric(
                'claude_cost_trend_increasing',
                trend_value
            )
            
        except Exception as e:
            print(f"Error updating monitoring metrics: {e}")
    
    def generate_monitoring_dashboard_config(self) -> Dict[str, Any]:
        """Generate Grafana dashboard configuration for token metrics"""
        
        dashboard_config = {
            "dashboard": {
                "id": None,
                "title": "Claude Token Usage & Cost Analysis",
                "tags": ["claude", "tokens", "cost", "ai"],
                "timezone": "browser",
                "panels": [
                    {
                        "id": 1,
                        "title": "Daily Cost Trend",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "claude_token_cost_daily_total",
                                "legendFormat": "Daily Cost ($)"
                            }
                        ],
                        "yAxes": [
                            {
                                "label": "Cost (USD)",
                                "min": 0
                            }
                        ]
                    },
                    {
                        "id": 2,
                        "title": "Token Usage by Agent",
                        "type": "piechart",
                        "targets": [
                            {
                                "expr": "claude_agent_tokens_daily_*",
                                "legendFormat": "{{agent}}"
                            }
                        ]
                    },
                    {
                        "id": 3,
                        "title": "Cost Efficiency Metrics",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "claude_cost_per_request_avg",
                                "legendFormat": "Avg Cost/Request"
                            },
                            {
                                "expr": "claude_tokens_per_request_avg",
                                "legendFormat": "Avg Tokens/Request"
                            }
                        ]
                    },
                    {
                        "id": 4,
                        "title": "Model Cost Distribution",
                        "type": "bargauge",
                        "targets": [
                            {
                                "expr": "claude_model_cost_daily_*",
                                "legendFormat": "{{model}}"
                            }
                        ]
                    },
                    {
                        "id": 5,
                        "title": "Optimization Opportunities",
                        "type": "table",
                        "targets": [
                            {
                                "expr": "claude_cost_optimization_savings_potential",
                                "legendFormat": "Potential Savings"
                            }
                        ]
                    }
                ],
                "time": {
                    "from": "now-30d",
                    "to": "now"
                },
                "refresh": "1m"
            }
        }
        
        # Save dashboard config
        dashboard_file = self.state_dir / 'token_grafana_dashboard.json'
        with open(dashboard_file, 'w') as f:
            json.dump(dashboard_config, f, indent=2)
        
        return dashboard_config
    
    def export_for_prometheus(self, output_file: Optional[str] = None) -> str:
        """Export current metrics in Prometheus format"""
        
        if not output_file:
            output_file = str(self.state_dir / 'token_metrics_export.prom')
        
        # Get current metrics
        today_summary = self.calculator.get_usage_summary(
            start_date=date.today(),
            end_date=date.today()
        )
        
        # Generate Prometheus metrics
        lines = []
        timestamp = int(time.time() * 1000)
        
        # Summary metrics
        lines.extend([
            f"# HELP claude_token_cost_total Total token cost in USD",
            f"# TYPE claude_token_cost_total counter",
            f"claude_token_cost_total {today_summary['totals']['cost']} {timestamp}",
            "",
            f"# HELP claude_token_usage_total Total tokens used",
            f"# TYPE claude_token_usage_total counter", 
            f"claude_token_usage_total {today_summary['totals']['tokens']} {timestamp}",
            "",
            f"# HELP claude_api_requests_total Total API requests",
            f"# TYPE claude_api_requests_total counter",
            f"claude_api_requests_total {today_summary['totals']['requests']} {timestamp}",
            ""
        ])
        
        # Agent metrics
        for agent in today_summary['by_agent']:
            agent_name = agent['agent_name'].replace('-', '_')
            lines.extend([
                f"claude_agent_cost{{agent=\"{agent['agent_name']}\"}} {agent['cost']} {timestamp}",
                f"claude_agent_tokens{{agent=\"{agent['agent_name']}\"}} {agent['tokens']} {timestamp}",
                f"claude_agent_requests{{agent=\"{agent['agent_name']}\"}} {agent['requests']} {timestamp}",
            ])
        
        # Model metrics
        for model in today_summary['by_model']:
            lines.extend([
                f"claude_model_cost{{model=\"{model['model_name']}\"}} {model['cost']} {timestamp}",
                f"claude_model_tokens{{model=\"{model['model_name']}\"}} {model['tokens']} {timestamp}",
                f"claude_model_requests{{model=\"{model['model_name']}\"}} {model['requests']} {timestamp}",
            ])
        
        # Write to file
        with open(output_file, 'w') as f:
            f.write('\n'.join(lines))
        
        return output_file
    
    def stop(self):
        """Stop integration services"""
        self.running = False
        if self.sync_thread and self.sync_thread.is_alive():
            self.sync_thread.join(timeout=5)

def main():
    """Main integration setup"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Claude Token Monitoring Integration')
    parser.add_argument('command', choices=['start', 'sync', 'export', 'dashboard'], 
                       help='Integration command')
    parser.add_argument('--output', help='Output file path for exports')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    
    args = parser.parse_args()
    
    # Initialize components
    calculator = TokenCostCalculator()
    
    # Try to connect to monitoring system
    metrics_collector = None
    if MONITORING_AVAILABLE:
        try:
            metrics_collector = MetricsCollector()
            print("Connected to monitoring system")
        except Exception as e:
            print(f"Could not connect to monitoring system: {e}")
    
    integration = TokenMonitoringIntegration(calculator, metrics_collector)
    
    try:
        if args.command == 'start':
            print("Starting token monitoring integration...")
            if args.daemon:
                print("Running in daemon mode (Ctrl+C to stop)")
                while True:
                    time.sleep(60)
            else:
                print("Running sync once...")
                integration.sync_token_metrics()
                integration.export_cost_metrics()
                integration.update_performance_metrics()
                print("Sync completed")
        
        elif args.command == 'sync':
            print("Syncing token metrics...")
            integration.sync_token_metrics()
            integration.export_cost_metrics()
            integration.update_performance_metrics()
            print("Sync completed")
        
        elif args.command == 'export':
            output_file = integration.export_for_prometheus(args.output)
            print(f"Metrics exported to: {output_file}")
        
        elif args.command == 'dashboard':
            config = integration.generate_monitoring_dashboard_config()
            print("Grafana dashboard config generated")
            print(f"Config saved to: {integration.state_dir / 'token_grafana_dashboard.json'}")
    
    except KeyboardInterrupt:
        print("Stopping integration...")
    finally:
        integration.stop()

if __name__ == '__main__':
    main()