#!/usr/bin/env python3
"""
Model Tracker Hook - Track model usage, costs, and performance metrics
Monitors token usage, response times, and provides cost optimization insights
"""

import sys
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict
from base_hook import BaseHook, format_size


class ModelTracker(BaseHook):
    """Track model usage and costs"""
    
    # Model pricing (example rates - adjust to actual pricing)
    MODEL_PRICING = {
        'claude-3-opus': {'input': 0.015, 'output': 0.075},  # per 1K tokens
        'claude-3-sonnet': {'input': 0.003, 'output': 0.015},
        'claude-3-haiku': {'input': 0.00025, 'output': 0.00125},
        'claude-2.1': {'input': 0.008, 'output': 0.024},
        'claude-instant': {'input': 0.0008, 'output': 0.0024}
    }
    
    # Token estimation factors
    CHARS_PER_TOKEN = 4  # Rough estimate
    
    def __init__(self):
        super().__init__('model_tracker')
        self.metrics_file = self.env.cache_dir / 'model_metrics.json'
        self.daily_metrics_dir = self.env.cache_dir / 'daily_metrics'
        self.daily_metrics_dir.mkdir(exist_ok=True)
    
    def run(self) -> int:
        """Track model usage from request"""
        # Read usage data from stdin
        usage_data = self._read_usage_data()
        
        if not usage_data:
            self.logger.debug("No usage data provided")
            return 0
        
        # Load current metrics
        metrics = self._load_metrics()
        
        # Update metrics with new usage
        self._update_metrics(metrics, usage_data)
        
        # Calculate costs
        costs = self._calculate_costs(usage_data)
        
        # Analyze usage patterns
        analysis = self._analyze_usage(metrics)
        
        # Generate optimization suggestions
        suggestions = self._generate_suggestions(metrics, analysis)
        
        # Save updated metrics
        self._save_metrics(metrics)
        
        # Archive daily metrics
        self._archive_daily_metrics(usage_data)
        
        # Prepare output report
        report = self._generate_report(metrics, costs, analysis, suggestions)
        
        # Output report
        self.write_stdout(json.dumps(report, indent=2))
        
        self.logger.info("Model usage tracked", 
                        model=usage_data.get('model', 'unknown'),
                        tokens=usage_data.get('total_tokens', 0),
                        cost=costs.get('total_cost', 0))
        
        return 0
    
    def _read_usage_data(self) -> Dict[str, Any]:
        """Read usage data from stdin"""
        input_text = self.read_stdin()
        
        if not input_text:
            return {}
        
        try:
            data = json.loads(input_text)
            
            # Ensure required fields
            if 'model' not in data:
                data['model'] = 'claude-3-sonnet'  # Default model
            
            # Estimate tokens if not provided
            if 'input_tokens' not in data and 'input_text' in data:
                data['input_tokens'] = len(data['input_text']) // self.CHARS_PER_TOKEN
            
            if 'output_tokens' not in data and 'output_text' in data:
                data['output_tokens'] = len(data['output_text']) // self.CHARS_PER_TOKEN
            
            data['total_tokens'] = data.get('input_tokens', 0) + data.get('output_tokens', 0)
            data['timestamp'] = datetime.now().isoformat()
            
            return data
            
        except json.JSONDecodeError:
            # Treat as raw text input
            return {
                'model': 'claude-3-sonnet',
                'input_text': input_text,
                'input_tokens': len(input_text) // self.CHARS_PER_TOKEN,
                'output_tokens': 0,
                'total_tokens': len(input_text) // self.CHARS_PER_TOKEN,
                'timestamp': datetime.now().isoformat()
            }
    
    def _load_metrics(self) -> Dict[str, Any]:
        """Load existing metrics"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load metrics: {e}")
        
        # Initialize metrics structure
        return {
            'total_requests': 0,
            'total_tokens': 0,
            'total_cost': 0.0,
            'by_model': defaultdict(lambda: {
                'requests': 0,
                'input_tokens': 0,
                'output_tokens': 0,
                'total_tokens': 0,
                'cost': 0.0,
                'avg_response_time': 0.0
            }),
            'by_agent': defaultdict(lambda: {
                'requests': 0,
                'tokens': 0,
                'cost': 0.0
            }),
            'by_day': defaultdict(lambda: {
                'requests': 0,
                'tokens': 0,
                'cost': 0.0
            }),
            'hourly_distribution': defaultdict(int),
            'response_times': [],
            'error_count': 0,
            'last_reset': datetime.now().isoformat()
        }
    
    def _update_metrics(self, metrics: Dict[str, Any], usage_data: Dict[str, Any]):
        """Update metrics with new usage data"""
        model = usage_data.get('model', 'unknown')
        agent = usage_data.get('agent', 'unknown')
        date_key = datetime.now().strftime('%Y-%m-%d')
        hour_key = datetime.now().hour
        
        # Update totals
        metrics['total_requests'] += 1
        metrics['total_tokens'] += usage_data.get('total_tokens', 0)
        
        # Update by model
        model_metrics = metrics['by_model'][model]
        model_metrics['requests'] += 1
        model_metrics['input_tokens'] += usage_data.get('input_tokens', 0)
        model_metrics['output_tokens'] += usage_data.get('output_tokens', 0)
        model_metrics['total_tokens'] += usage_data.get('total_tokens', 0)
        
        # Update response time
        if 'response_time' in usage_data:
            response_times = metrics.get('response_times', [])
            response_times.append(usage_data['response_time'])
            # Keep only last 1000 response times
            metrics['response_times'] = response_times[-1000:]
            
            # Update average
            model_metrics['avg_response_time'] = sum(response_times) / len(response_times)
        
        # Update by agent
        if agent != 'unknown':
            agent_metrics = metrics['by_agent'][agent]
            agent_metrics['requests'] += 1
            agent_metrics['tokens'] += usage_data.get('total_tokens', 0)
        
        # Update by day
        day_metrics = metrics['by_day'][date_key]
        day_metrics['requests'] += 1
        day_metrics['tokens'] += usage_data.get('total_tokens', 0)
        
        # Update hourly distribution
        metrics['hourly_distribution'][str(hour_key)] += 1
        
        # Update error count
        if usage_data.get('error'):
            metrics['error_count'] += 1
    
    def _calculate_costs(self, usage_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate costs for the usage"""
        model = usage_data.get('model', 'claude-3-sonnet')
        input_tokens = usage_data.get('input_tokens', 0)
        output_tokens = usage_data.get('output_tokens', 0)
        
        # Get pricing for model
        pricing = self.MODEL_PRICING.get(model, self.MODEL_PRICING['claude-3-sonnet'])
        
        # Calculate costs (pricing is per 1K tokens)
        input_cost = (input_tokens / 1000) * pricing['input']
        output_cost = (output_tokens / 1000) * pricing['output']
        total_cost = input_cost + output_cost
        
        return {
            'input_cost': round(input_cost, 6),
            'output_cost': round(output_cost, 6),
            'total_cost': round(total_cost, 6),
            'cost_per_token': round(total_cost / max(usage_data.get('total_tokens', 1), 1), 8)
        }
    
    def _analyze_usage(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze usage patterns"""
        analysis = {
            'peak_hours': [],
            'most_used_model': None,
            'most_active_agent': None,
            'daily_average': 0,
            'cost_trend': 'stable',
            'token_efficiency': 0,
            'error_rate': 0
        }
        
        # Find peak usage hours
        if metrics['hourly_distribution']:
            sorted_hours = sorted(metrics['hourly_distribution'].items(), 
                                key=lambda x: x[1], reverse=True)
            analysis['peak_hours'] = [int(h[0]) for h in sorted_hours[:3]]
        
        # Find most used model
        if metrics['by_model']:
            most_used = max(metrics['by_model'].items(), 
                          key=lambda x: x[1]['requests'])
            analysis['most_used_model'] = most_used[0]
        
        # Find most active agent
        if metrics['by_agent']:
            most_active = max(metrics['by_agent'].items(), 
                            key=lambda x: x[1]['requests'])
            analysis['most_active_agent'] = most_active[0]
        
        # Calculate daily average
        if metrics['by_day']:
            total_days = len(metrics['by_day'])
            analysis['daily_average'] = metrics['total_requests'] / max(total_days, 1)
        
        # Analyze cost trend
        if metrics['by_day'] and len(metrics['by_day']) > 7:
            recent_costs = []
            for date in sorted(metrics['by_day'].keys())[-7:]:
                recent_costs.append(metrics['by_day'][date].get('cost', 0))
            
            if recent_costs:
                avg_recent = sum(recent_costs[-3:]) / 3
                avg_previous = sum(recent_costs[:3]) / 3
                
                if avg_recent > avg_previous * 1.2:
                    analysis['cost_trend'] = 'increasing'
                elif avg_recent < avg_previous * 0.8:
                    analysis['cost_trend'] = 'decreasing'
        
        # Calculate token efficiency
        if metrics['total_tokens'] > 0:
            analysis['token_efficiency'] = metrics['total_requests'] / (metrics['total_tokens'] / 1000)
        
        # Calculate error rate
        if metrics['total_requests'] > 0:
            analysis['error_rate'] = metrics['error_count'] / metrics['total_requests']
        
        return analysis
    
    def _generate_suggestions(self, metrics: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate cost optimization suggestions"""
        suggestions = []
        
        # Model optimization
        model_costs = {}
        for model, data in metrics['by_model'].items():
            if data['total_tokens'] > 0:
                avg_cost_per_token = data.get('cost', 0) / data['total_tokens']
                model_costs[model] = avg_cost_per_token
        
        if model_costs:
            cheapest_model = min(model_costs.items(), key=lambda x: x[1])[0]
            most_expensive = max(model_costs.items(), key=lambda x: x[1])[0]
            
            if most_expensive != cheapest_model:
                potential_savings = (model_costs[most_expensive] - model_costs[cheapest_model]) * \
                                  metrics['by_model'][most_expensive]['total_tokens']
                
                suggestions.append({
                    'type': 'model_optimization',
                    'priority': 'high',
                    'suggestion': f"Consider using {cheapest_model} instead of {most_expensive}",
                    'potential_savings': f"${potential_savings:.2f}",
                    'impact': 'Reduce costs without significant quality loss for routine tasks'
                })
        
        # Token optimization
        if analysis['token_efficiency'] < 0.5:
            suggestions.append({
                'type': 'token_optimization',
                'priority': 'medium',
                'suggestion': "Optimize prompts to reduce token usage",
                'potential_savings': "Up to 30% cost reduction",
                'impact': 'More concise prompts can maintain quality with fewer tokens'
            })
        
        # Time-based optimization
        if analysis['peak_hours']:
            suggestions.append({
                'type': 'usage_pattern',
                'priority': 'low',
                'suggestion': f"Peak usage at hours: {analysis['peak_hours']}",
                'potential_savings': "Better resource planning",
                'impact': 'Consider batch processing during off-peak hours'
            })
        
        # Error reduction
        if analysis['error_rate'] > 0.05:
            suggestions.append({
                'type': 'error_reduction',
                'priority': 'high',
                'suggestion': f"High error rate: {analysis['error_rate']:.1%}",
                'potential_savings': "Reduce wasted API calls",
                'impact': 'Fix errors to avoid costly retries'
            })
        
        # Agent-specific suggestions
        high_cost_agents = []
        for agent, data in metrics['by_agent'].items():
            if data['requests'] > 10 and data.get('cost', 0) / data['requests'] > 0.1:
                high_cost_agents.append(agent)
        
        if high_cost_agents:
            suggestions.append({
                'type': 'agent_optimization',
                'priority': 'medium',
                'suggestion': f"High-cost agents: {', '.join(high_cost_agents)}",
                'potential_savings': "Agent-specific optimizations",
                'impact': 'Review if these agents need expensive models'
            })
        
        return suggestions
    
    def _save_metrics(self, metrics: Dict[str, Any]):
        """Save updated metrics"""
        try:
            # Update total cost
            total_cost = 0
            for model_data in metrics['by_model'].values():
                total_cost += model_data.get('cost', 0)
            metrics['total_cost'] = round(total_cost, 2)
            
            # Update agent costs
            for agent in metrics['by_agent']:
                agent_tokens = metrics['by_agent'][agent]['tokens']
                # Estimate cost based on average
                if metrics['total_tokens'] > 0:
                    agent_cost = (agent_tokens / metrics['total_tokens']) * metrics['total_cost']
                    metrics['by_agent'][agent]['cost'] = round(agent_cost, 2)
            
            # Update daily costs
            for date in metrics['by_day']:
                day_tokens = metrics['by_day'][date]['tokens']
                if metrics['total_tokens'] > 0:
                    day_cost = (day_tokens / metrics['total_tokens']) * metrics['total_cost']
                    metrics['by_day'][date]['cost'] = round(day_cost, 2)
            
            # Save to file
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Failed to save metrics: {e}")
    
    def _archive_daily_metrics(self, usage_data: Dict[str, Any]):
        """Archive detailed daily metrics"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        daily_file = self.daily_metrics_dir / f'metrics_{date_str}.json'
        
        try:
            # Load existing daily data
            daily_data = []
            if daily_file.exists():
                with open(daily_file, 'r', encoding='utf-8') as f:
                    daily_data = json.load(f)
            
            # Add new entry
            daily_data.append({
                'timestamp': usage_data.get('timestamp', datetime.now().isoformat()),
                'model': usage_data.get('model'),
                'agent': usage_data.get('agent'),
                'tokens': usage_data.get('total_tokens'),
                'cost': self._calculate_costs(usage_data)['total_cost'],
                'response_time': usage_data.get('response_time'),
                'error': usage_data.get('error')
            })
            
            # Save updated daily data
            with open(daily_file, 'w', encoding='utf-8') as f:
                json.dump(daily_data, f, indent=2)
                
        except Exception as e:
            self.logger.warning(f"Failed to archive daily metrics: {e}")
    
    def _generate_report(self, metrics: Dict[str, Any], costs: Dict[str, float], 
                        analysis: Dict[str, Any], suggestions: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate comprehensive usage report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'session_cost': costs,
            'totals': {
                'requests': metrics['total_requests'],
                'tokens': metrics['total_tokens'],
                'cost': f"${metrics['total_cost']:.2f}",
                'avg_cost_per_request': f"${metrics['total_cost'] / max(metrics['total_requests'], 1):.4f}"
            },
            'model_breakdown': {},
            'agent_breakdown': {},
            'analysis': analysis,
            'suggestions': suggestions,
            'daily_limit_status': self._check_daily_limits(metrics),
            'cost_projection': self._project_costs(metrics)
        }
        
        # Add model breakdown
        for model, data in metrics['by_model'].items():
            if isinstance(data, dict) and data.get('requests', 0) > 0:
                report['model_breakdown'][model] = {
                    'requests': data['requests'],
                    'tokens': data['total_tokens'],
                    'cost': f"${data.get('cost', 0):.2f}",
                    'avg_response_time': f"{data.get('avg_response_time', 0):.2f}s"
                }
        
        # Add agent breakdown
        for agent, data in metrics['by_agent'].items():
            if isinstance(data, dict) and data.get('requests', 0) > 0:
                report['agent_breakdown'][agent] = {
                    'requests': data['requests'],
                    'tokens': data['tokens'],
                    'cost': f"${data.get('cost', 0):.2f}"
                }
        
        return report
    
    def _check_daily_limits(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Check against daily usage limits"""
        today = datetime.now().strftime('%Y-%m-%d')
        today_metrics = metrics['by_day'].get(today, {})
        
        # Define limits (configurable)
        limits = self.config.get('daily_limits', {
            'tokens': 1000000,  # 1M tokens
            'cost': 50.0,  # $50
            'requests': 1000
        })
        
        status = {
            'tokens': {
                'used': today_metrics.get('tokens', 0),
                'limit': limits['tokens'],
                'percentage': (today_metrics.get('tokens', 0) / limits['tokens']) * 100
            },
            'cost': {
                'used': today_metrics.get('cost', 0),
                'limit': limits['cost'],
                'percentage': (today_metrics.get('cost', 0) / limits['cost']) * 100
            },
            'requests': {
                'used': today_metrics.get('requests', 0),
                'limit': limits['requests'],
                'percentage': (today_metrics.get('requests', 0) / limits['requests']) * 100
            }
        }
        
        # Add warnings if approaching limits
        for metric, data in status.items():
            if data['percentage'] > 80:
                data['warning'] = f"Approaching daily {metric} limit"
            elif data['percentage'] > 100:
                data['warning'] = f"Exceeded daily {metric} limit"
        
        return status
    
    def _project_costs(self, metrics: Dict[str, Any]) -> Dict[str, str]:
        """Project costs based on current usage"""
        # Get recent daily average
        recent_days = sorted(metrics['by_day'].keys())[-7:]
        if not recent_days:
            return {
                'daily': '$0.00',
                'weekly': '$0.00',
                'monthly': '$0.00'
            }
        
        recent_costs = [metrics['by_day'][day].get('cost', 0) for day in recent_days]
        avg_daily_cost = sum(recent_costs) / len(recent_costs)
        
        return {
            'daily': f"${avg_daily_cost:.2f}",
            'weekly': f"${avg_daily_cost * 7:.2f}",
            'monthly': f"${avg_daily_cost * 30:.2f}",
            'trend': 'Based on last 7 days average'
        }


def main():
    """Main entry point"""
    tracker = ModelTracker()
    return tracker.safe_run()


if __name__ == "__main__":
    sys.exit(main())