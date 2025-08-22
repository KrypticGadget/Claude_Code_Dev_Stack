#!/usr/bin/env python3
"""
Claude Token Calculator CLI - Command Line Interface
Interactive command-line tool for token usage analysis and cost optimization
"""

import argparse
import json
import sys
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
import subprocess
import os

from token_cost_calculator import TokenCostCalculator, OptimizationRecommendation
from token_dashboard import TokenDashboard

class TokenCLI:
    """Command-line interface for token cost management"""
    
    def __init__(self):
        self.calculator = TokenCostCalculator()
        self.colors = {
            'reset': '\033[0m',
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'purple': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bold': '\033[1m'
        }
    
    def colorize(self, text: str, color: str) -> str:
        """Add color to text if terminal supports it"""
        if os.name == 'nt':  # Windows
            return text
        return f"{self.colors.get(color, '')}{text}{self.colors['reset']}"
    
    def print_header(self, title: str):
        """Print a formatted header"""
        print(f"\n{self.colorize('='*60, 'blue')}")
        print(f"{self.colorize(title.center(60), 'bold')}")
        print(f"{self.colorize('='*60, 'blue')}\n")
    
    def print_success(self, message: str):
        """Print success message"""
        print(f"{self.colorize('✓', 'green')} {message}")
    
    def print_error(self, message: str):
        """Print error message"""
        print(f"{self.colorize('✗', 'red')} {message}")
    
    def print_warning(self, message: str):
        """Print warning message"""
        print(f"{self.colorize('⚠', 'yellow')} {message}")
    
    def print_info(self, message: str):
        """Print info message"""
        print(f"{self.colorize('ℹ', 'blue')} {message}")
    
    def format_currency(self, amount: float) -> str:
        """Format currency with color based on amount"""
        formatted = f"${amount:.4f}" if amount < 1 else f"${amount:.2f}"
        if amount > 50:
            return self.colorize(formatted, 'red')
        elif amount > 10:
            return self.colorize(formatted, 'yellow')
        else:
            return self.colorize(formatted, 'green')
    
    def format_number(self, number: int) -> str:
        """Format large numbers with commas"""
        return f"{number:,}"
    
    def cmd_record(self, args):
        """Record token usage"""
        try:
            usage = self.calculator.record_usage(
                session_id=args.session_id,
                agent_name=args.agent,
                model_name=args.model,
                input_tokens=args.input_tokens,
                output_tokens=args.output_tokens,
                operation_type=args.operation or "completion",
                duration_seconds=args.duration or 0.0,
                context_length=args.context_length or 0,
                temperature=args.temperature or 0.7,
                max_tokens=args.max_tokens or 4096
            )
            
            self.print_success("Usage recorded successfully!")
            print(f"  Session: {usage.session_id}")
            print(f"  Agent: {usage.agent_name}")
            print(f"  Model: {usage.model_name}")
            print(f"  Tokens: {self.format_number(usage.total_tokens)} ({usage.input_tokens} in, {usage.output_tokens} out)")
            print(f"  Cost: {self.format_currency(float(usage.total_cost))}")
            print(f"  Timestamp: {usage.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            self.print_error(f"Failed to record usage: {e}")
    
    def cmd_summary(self, args):
        """Show usage summary"""
        try:
            start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date() if args.start_date else None
            end_date = datetime.strptime(args.end_date, '%Y-%m-%d').date() if args.end_date else None
            
            summary = self.calculator.get_usage_summary(start_date=start_date, end_date=end_date)
            
            self.print_header("TOKEN USAGE SUMMARY")
            
            # Period info
            period = summary['period']
            print(f"Period: {period['start_date']} to {period['end_date']} ({period['days']} days)")
            print()
            
            # Totals
            totals = summary['totals']
            print(f"{self.colorize('Total Cost:', 'bold')} {self.format_currency(totals['cost'])}")
            print(f"{self.colorize('Total Tokens:', 'bold')} {self.format_number(totals['tokens'])}")
            print(f"{self.colorize('API Requests:', 'bold')} {self.format_number(totals['requests'])}")
            print(f"{self.colorize('Sessions:', 'bold')} {totals['sessions']}")
            print(f"{self.colorize('Agents Used:', 'bold')} {totals['agents']}")
            print(f"{self.colorize('Avg Cost/Request:', 'bold')} {self.format_currency(totals['avg_cost_per_request'])}")
            print(f"{self.colorize('Avg Tokens/Request:', 'bold')} {self.format_number(int(totals['avg_tokens_per_request']))}")
            
            # Top agents by cost
            if summary['by_agent']:
                print(f"\n{self.colorize('Top Agents by Cost:', 'bold')}")
                for i, agent in enumerate(summary['by_agent'][:5]):
                    print(f"  {i+1}. {agent['agent_name']}: {self.format_currency(agent['cost'])} ({self.format_number(agent['tokens'])} tokens)")
            
            # Top models by cost
            if summary['by_model']:
                print(f"\n{self.colorize('Models Used:', 'bold')}")
                for model in summary['by_model']:
                    print(f"  • {model['model_name']}: {self.format_currency(model['cost'])} ({self.format_number(model['tokens'])} tokens)")
            
            # JSON output if requested
            if args.json:
                print(f"\n{self.colorize('JSON Output:', 'bold')}")
                print(json.dumps(summary, indent=2, default=str))
                
        except Exception as e:
            self.print_error(f"Failed to get summary: {e}")
    
    def cmd_trends(self, args):
        """Show cost trends"""
        try:
            trends = self.calculator.get_cost_trends(args.days)
            
            self.print_header(f"COST TRENDS ({args.days} DAYS)")
            
            # Trend analysis
            analysis = trends['trend_analysis']
            direction_symbol = "📈" if analysis['direction'] == "increasing" else "📉"
            direction_color = "red" if analysis['direction'] == "increasing" else "green"
            
            print(f"Trend Direction: {direction_symbol} {self.colorize(analysis['direction'].upper(), direction_color)}")
            if analysis['percentage_change'] != 0:
                print(f"Change: {analysis['percentage_change']:.1f}%")
            print()
            
            # Daily trends (last 7 days)
            if trends['daily_trends']:
                print(f"{self.colorize('Recent Daily Costs:', 'bold')}")
                recent_days = trends['daily_trends'][-7:]
                for day in recent_days:
                    cost_str = self.format_currency(day['cost'])
                    tokens_str = self.format_number(day['tokens'])
                    print(f"  {day['date']}: {cost_str} ({tokens_str} tokens, {day['requests']} requests)")
            
            # Hourly patterns
            if trends['hourly_patterns'] and not args.no_hourly:
                print(f"\n{self.colorize('Peak Usage Hours:', 'bold')}")
                sorted_hours = sorted(trends['hourly_patterns'], key=lambda x: x['requests'], reverse=True)
                for hour_data in sorted_hours[:5]:
                    hour = hour_data['hour']
                    time_str = f"{hour:02d}:00"
                    avg_cost = self.format_currency(hour_data['avg_cost'])
                    requests = hour_data['requests']
                    print(f"  {time_str}: {avg_cost} avg cost ({requests} requests)")
            
            # JSON output if requested
            if args.json:
                print(f"\n{self.colorize('JSON Output:', 'bold')}")
                print(json.dumps(trends, indent=2, default=str))
                
        except Exception as e:
            self.print_error(f"Failed to get trends: {e}")
    
    def cmd_optimize(self, args):
        """Show optimization recommendations"""
        try:
            recommendations = self.calculator.generate_cost_optimization_recommendations()
            
            self.print_header("COST OPTIMIZATION RECOMMENDATIONS")
            
            if not recommendations:
                self.print_success("Great! No optimization recommendations. Your usage appears efficient.")
                return
            
            # Group by priority
            high_priority = [r for r in recommendations if r.priority == "high"]
            medium_priority = [r for r in recommendations if r.priority == "medium"]
            low_priority = [r for r in recommendations if r.priority == "low"]
            
            for priority_group, title, emoji in [
                (high_priority, "HIGH PRIORITY", "🚨"),
                (medium_priority, "MEDIUM PRIORITY", "⚠️"),
                (low_priority, "LOW PRIORITY", "💡")
            ]:
                if priority_group:
                    print(f"\n{emoji} {self.colorize(title, 'bold')}")
                    print("-" * 40)
                    
                    for rec in priority_group:
                        print(f"\n{self.colorize(rec.category.replace('_', ' ').title(), 'bold')}")
                        print(f"Issue: {rec.description}")
                        print(f"Potential Savings: {self.format_currency(float(rec.potential_savings))}")
                        print(f"Implementation: {rec.implementation_effort} | Impact: {rec.estimated_impact}")
                        
                        if rec.specific_actions and not args.no_actions:
                            print("Actions:")
                            for action in rec.specific_actions[:3]:
                                print(f"  • {action}")
            
            # Summary
            total_savings = sum(float(r.potential_savings) for r in recommendations)
            print(f"\n{self.colorize('Total Potential Savings:', 'bold')} {self.format_currency(total_savings)}")
            
            # JSON output if requested
            if args.json:
                recommendations_dict = [
                    {
                        'category': r.category,
                        'priority': r.priority,
                        'description': r.description,
                        'potential_savings': float(r.potential_savings),
                        'implementation_effort': r.implementation_effort,
                        'estimated_impact': r.estimated_impact,
                        'specific_actions': r.specific_actions
                    }
                    for r in recommendations
                ]
                print(f"\n{self.colorize('JSON Output:', 'bold')}")
                print(json.dumps(recommendations_dict, indent=2))
                
        except Exception as e:
            self.print_error(f"Failed to get recommendations: {e}")
    
    def cmd_alerts(self, args):
        """Manage cost alerts"""
        try:
            if args.action == 'create':
                if not args.threshold:
                    self.print_error("Threshold amount required for creating alerts")
                    return
                
                alert_id = self.calculator.create_cost_alert(
                    alert_type=args.type,
                    threshold_amount=args.threshold,
                    notification_method=args.method or "console"
                )
                
                self.print_success(f"Alert created: {alert_id}")
                print(f"  Type: {args.type}")
                print(f"  Threshold: {self.format_currency(args.threshold)}")
                print(f"  Method: {args.method or 'console'}")
            
            elif args.action == 'list':
                if not self.calculator.alerts:
                    self.print_info("No active alerts configured")
                    return
                
                self.print_header("ACTIVE COST ALERTS")
                
                for alert in self.calculator.alerts:
                    status_icon = "🟢" if alert.enabled else "🔴"
                    print(f"{status_icon} {alert.alert_id}")
                    print(f"  Type: {alert.alert_type}")
                    print(f"  Threshold: {self.format_currency(float(alert.threshold_amount))}")
                    print(f"  Method: {alert.notification_method}")
                    print(f"  Created: {alert.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    if alert.last_triggered:
                        print(f"  Last Triggered: {alert.last_triggered.strftime('%Y-%m-%d %H:%M:%S')}")
                    print()
            
            elif args.action == 'test':
                self.print_info("Testing alert system...")
                self.calculator.check_cost_alerts()
                self.print_success("Alert check completed")
                
        except Exception as e:
            self.print_error(f"Failed to manage alerts: {e}")
    
    def cmd_export(self, args):
        """Export usage data"""
        try:
            start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date() if args.start_date else None
            end_date = datetime.strptime(args.end_date, '%Y-%m-%d').date() if args.end_date else None
            
            output_path = args.output or f"token_usage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{args.format}"
            
            self.calculator.export_usage_data(
                filepath=output_path,
                format=args.format,
                start_date=start_date,
                end_date=end_date
            )
            
            self.print_success(f"Data exported to: {output_path}")
            
            # Show file size
            file_size = os.path.getsize(output_path)
            print(f"File size: {file_size:,} bytes")
            
        except Exception as e:
            self.print_error(f"Failed to export data: {e}")
    
    def cmd_report(self, args):
        """Generate comprehensive report"""
        try:
            output_path = args.output or f"cost_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            
            self.print_info("Generating comprehensive cost report...")
            
            self.calculator.generate_cost_report(
                output_path=output_path,
                include_charts=not args.no_charts
            )
            
            self.print_success(f"Report generated: {output_path}")
            
            # Try to open in browser
            if args.open:
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(output_path)
                    else:  # macOS and Linux
                        subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', output_path])
                    self.print_info("Report opened in browser")
                except Exception:
                    self.print_warning("Could not open report in browser automatically")
                    
        except Exception as e:
            self.print_error(f"Failed to generate report: {e}")
    
    def cmd_compare(self, args):
        """Compare model costs"""
        try:
            comparison = self.calculator.get_model_comparison()
            
            self.print_header("MODEL COST COMPARISON")
            
            # Create comparison table
            print(f"{'Model':<30} {'Input ($/1M)':<12} {'Output ($/1M)':<13} {'Chat Avg':<10}")
            print("-" * 70)
            
            for model_name, data in comparison.items():
                pricing = data['pricing']
                chat_avg = data['scenario_costs']['chat_medium']
                
                input_cost = f"${pricing['input_cost_per_million']:.2f}"
                output_cost = f"${pricing['output_cost_per_million']:.2f}"
                chat_cost = self.format_currency(chat_avg)
                
                # Truncate long model names
                display_name = model_name[:28] + "..." if len(model_name) > 30 else model_name
                
                print(f"{display_name:<30} {input_cost:<12} {output_cost:<13} {chat_cost}")
            
            print()
            
            # Scenario comparison
            if not args.no_scenarios:
                print(f"{self.colorize('Scenario Cost Comparison:', 'bold')}")
                print("(Input tokens → Output tokens)")
                print()
                
                scenarios = {
                    'chat_small': '1K → 200',
                    'chat_medium': '2K → 500', 
                    'chat_large': '5K → 1K',
                    'document_analysis': '10K → 2K',
                    'code_generation': '3K → 1.5K'
                }
                
                for scenario, description in scenarios.items():
                    print(f"{scenario.replace('_', ' ').title()} ({description}):")
                    
                    # Sort models by cost for this scenario
                    model_costs = [(name, data['scenario_costs'][scenario]) 
                                 for name, data in comparison.items()]
                    model_costs.sort(key=lambda x: x[1])
                    
                    for name, cost in model_costs:
                        display_name = name.split('-')[-1] if '-' in name else name
                        print(f"  {display_name:<15} {self.format_currency(cost)}")
                    print()
            
            # JSON output if requested
            if args.json:
                print(f"\n{self.colorize('JSON Output:', 'bold')}")
                print(json.dumps(comparison, indent=2, default=str))
                
        except Exception as e:
            self.print_error(f"Failed to compare models: {e}")
    
    def cmd_predict(self, args):
        """Predict monthly costs"""
        try:
            prediction = self.calculator.predict_monthly_cost(args.days)
            
            self.print_header(f"MONTHLY COST PREDICTION (based on {args.days} days)")
            
            print(f"Daily Average: {self.format_currency(prediction['daily_average'])}")
            print(f"Monthly Projection: {self.format_currency(prediction['monthly_projection'])}")
            print()
            
            # Confidence interval
            confidence = prediction['confidence_95']
            print(f"{self.colorize('95% Confidence Interval:', 'bold')}")
            print(f"  Lower bound: {self.format_currency(confidence['lower'])}")
            print(f"  Upper bound: {self.format_currency(confidence['upper'])}")
            print()
            
            # Agent breakdown
            if prediction['breakdown_projection']['by_agent']:
                print(f"{self.colorize('Projected Monthly Cost by Agent:', 'bold')}")
                for agent in prediction['breakdown_projection']['by_agent'][:5]:
                    name = agent['agent_name']
                    cost = self.format_currency(agent['monthly_cost'])
                    print(f"  {name}: {cost}")
                print()
            
            # Model breakdown
            if prediction['breakdown_projection']['by_model']:
                print(f"{self.colorize('Projected Monthly Cost by Model:', 'bold')}")
                for model in prediction['breakdown_projection']['by_model']:
                    name = model['model_name'].split('-')[-1] if '-' in model['model_name'] else model['model_name']
                    cost = self.format_currency(model['monthly_cost'])
                    print(f"  {name}: {cost}")
            
            # JSON output if requested
            if args.json:
                print(f"\n{self.colorize('JSON Output:', 'bold')}")
                print(json.dumps(prediction, indent=2, default=str))
                
        except Exception as e:
            self.print_error(f"Failed to predict costs: {e}")
    
    def cmd_dashboard(self, args):
        """Launch web dashboard"""
        try:
            self.print_info(f"Starting dashboard on http://{args.host}:{args.port}")
            dashboard = TokenDashboard(self.calculator)
            dashboard.run(host=args.host, port=args.port, debug=args.debug)
            
        except KeyboardInterrupt:
            self.print_info("Dashboard stopped")
        except Exception as e:
            self.print_error(f"Failed to start dashboard: {e}")
    
    def cmd_status(self, args):
        """Show system status"""
        try:
            self.print_header("SYSTEM STATUS")
            
            # Database info
            db_path = Path(self.calculator.db_path)
            if db_path.exists():
                db_size = db_path.stat().st_size
                self.print_success(f"Database: Connected ({db_size:,} bytes)")
            else:
                self.print_error("Database: Not found")
            
            # Recent activity
            today_summary = self.calculator.get_usage_summary(
                start_date=date.today(),
                end_date=date.today()
            )
            
            print(f"Today's Usage:")
            print(f"  Requests: {today_summary['totals']['requests']}")
            print(f"  Tokens: {self.format_number(today_summary['totals']['tokens'])}")
            print(f"  Cost: {self.format_currency(today_summary['totals']['cost'])}")
            print()
            
            # Alerts status
            active_alerts = len([a for a in self.calculator.alerts if a.enabled])
            if active_alerts > 0:
                self.print_success(f"Alerts: {active_alerts} active")
            else:
                self.print_warning("Alerts: None configured")
            
            # Model pricing info
            print(f"\nAvailable Models: {len(self.calculator.model_pricing)}")
            for model_name in list(self.calculator.model_pricing.keys())[:3]:
                display_name = model_name.split('-')[-1] if '-' in model_name else model_name
                print(f"  • {display_name}")
            
            if len(self.calculator.model_pricing) > 3:
                print(f"  ... and {len(self.calculator.model_pricing) - 3} more")
                
        except Exception as e:
            self.print_error(f"Failed to get status: {e}")

def main():
    """Main CLI entry point"""
    
    parser = argparse.ArgumentParser(
        description='Claude Token Cost Calculator - Advanced financial analysis for Claude API usage',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s record --session-id="sess_123" --agent="business-analyst" --model="claude-3-5-sonnet-20241022" --input-tokens=1500 --output-tokens=300
  %(prog)s summary --start-date="2024-01-01" --end-date="2024-01-31"
  %(prog)s trends --days=14
  %(prog)s optimize
  %(prog)s alerts create --type=daily --threshold=25.00
  %(prog)s export --format=csv --output="usage_data.csv"
  %(prog)s dashboard --port=8080
  %(prog)s compare --no-scenarios
  %(prog)s predict --days=7
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Record command
    record_parser = subparsers.add_parser('record', help='Record token usage')
    record_parser.add_argument('--session-id', required=True, help='Session ID')
    record_parser.add_argument('--agent', required=True, help='Agent name')
    record_parser.add_argument('--model', required=True, help='Model name')
    record_parser.add_argument('--input-tokens', type=int, required=True, help='Input tokens')
    record_parser.add_argument('--output-tokens', type=int, required=True, help='Output tokens')
    record_parser.add_argument('--operation', help='Operation type (default: completion)')
    record_parser.add_argument('--duration', type=float, help='Duration in seconds')
    record_parser.add_argument('--context-length', type=int, help='Context length')
    record_parser.add_argument('--temperature', type=float, help='Temperature setting')
    record_parser.add_argument('--max-tokens', type=int, help='Max tokens setting')
    
    # Summary command
    summary_parser = subparsers.add_parser('summary', help='Show usage summary')
    summary_parser.add_argument('--start-date', help='Start date (YYYY-MM-DD)')
    summary_parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')
    summary_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Trends command
    trends_parser = subparsers.add_parser('trends', help='Show cost trends')
    trends_parser.add_argument('--days', type=int, default=30, help='Number of days (default: 30)')
    trends_parser.add_argument('--no-hourly', action='store_true', help='Skip hourly patterns')
    trends_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Optimize command
    optimize_parser = subparsers.add_parser('optimize', help='Show optimization recommendations')
    optimize_parser.add_argument('--no-actions', action='store_true', help='Skip specific actions')
    optimize_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Alerts command
    alerts_parser = subparsers.add_parser('alerts', help='Manage cost alerts')
    alerts_parser.add_argument('action', choices=['create', 'list', 'test'], help='Alert action')
    alerts_parser.add_argument('--type', choices=['daily', 'weekly', 'monthly'], help='Alert type')
    alerts_parser.add_argument('--threshold', type=float, help='Threshold amount')
    alerts_parser.add_argument('--method', choices=['console', 'email', 'webhook'], help='Notification method')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export usage data')
    export_parser.add_argument('--format', choices=['csv', 'json', 'excel'], default='csv', help='Export format')
    export_parser.add_argument('--output', help='Output file path')
    export_parser.add_argument('--start-date', help='Start date (YYYY-MM-DD)')
    export_parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate comprehensive report')
    report_parser.add_argument('--output', help='Output file path')
    report_parser.add_argument('--no-charts', action='store_true', help='Skip chart generation')
    report_parser.add_argument('--open', action='store_true', help='Open report in browser')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare model costs')
    compare_parser.add_argument('--no-scenarios', action='store_true', help='Skip scenario comparison')
    compare_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Predict command
    predict_parser = subparsers.add_parser('predict', help='Predict monthly costs')
    predict_parser.add_argument('--days', type=int, default=7, help='Days to base prediction on')
    predict_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Launch web dashboard')
    dashboard_parser.add_argument('--host', default='localhost', help='Host to bind to')
    dashboard_parser.add_argument('--port', type=int, default=8080, help='Port to bind to')
    dashboard_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize CLI
    cli = TokenCLI()
    
    # Execute command
    command_method = getattr(cli, f'cmd_{args.command}', None)
    if command_method:
        try:
            command_method(args)
        except KeyboardInterrupt:
            cli.print_info("Operation cancelled")
        except Exception as e:
            cli.print_error(f"Unexpected error: {e}")
            if args.command == 'dashboard' and 'debug' in args and args.debug:
                raise
    else:
        cli.print_error(f"Unknown command: {args.command}")

if __name__ == '__main__':
    main()