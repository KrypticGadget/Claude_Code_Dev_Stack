#!/usr/bin/env python3
"""
Claude Token Usage Calculator & Cost Optimization Engine
Advanced financial analysis tool for Claude API token tracking and cost management
"""

import json
import sqlite3
import time
import threading
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_HALF_UP
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

@dataclass
class ModelPricing:
    """Claude model pricing structure"""
    model_name: str
    input_cost_per_million: Decimal  # USD per million input tokens
    output_cost_per_million: Decimal  # USD per million output tokens
    context_window: int
    max_output: int
    description: str

@dataclass
class TokenUsage:
    """Token usage record"""
    session_id: str
    agent_name: str
    model_name: str
    timestamp: datetime
    input_tokens: int
    output_tokens: int
    total_tokens: int
    input_cost: Decimal
    output_cost: Decimal
    total_cost: Decimal
    operation_type: str
    duration_seconds: float
    context_length: int
    temperature: float
    max_tokens: int

@dataclass
class CostAlert:
    """Cost alert configuration"""
    alert_id: str
    alert_type: str  # daily, weekly, monthly, threshold
    threshold_amount: Decimal
    notification_method: str  # email, console, webhook
    enabled: bool
    created_at: datetime
    last_triggered: Optional[datetime] = None

@dataclass
class OptimizationRecommendation:
    """Cost optimization recommendation"""
    category: str
    priority: str  # high, medium, low
    description: str
    potential_savings: Decimal
    implementation_effort: str  # easy, medium, hard
    estimated_impact: str
    specific_actions: List[str]

class TokenCostCalculator:
    """Comprehensive token cost tracking and optimization engine"""
    
    def __init__(self, database_path: Optional[str] = None):
        self.claude_dir = Path.home() / '.claude'
        self.financial_dir = self.claude_dir / 'financial'
        self.financial_dir.mkdir(parents=True, exist_ok=True)
        
        # Database setup
        self.db_path = database_path or str(self.financial_dir / 'token_costs.db')
        self.init_database()
        
        # Model pricing (as of 2024 - update as needed)
        self.model_pricing = {
            'claude-3-5-sonnet-20241022': ModelPricing(
                model_name='claude-3-5-sonnet-20241022',
                input_cost_per_million=Decimal('3.00'),
                output_cost_per_million=Decimal('15.00'),
                context_window=200000,
                max_output=8192,
                description='Claude 3.5 Sonnet (Latest)'
            ),
            'claude-3-5-haiku-20241022': ModelPricing(
                model_name='claude-3-5-haiku-20241022',
                input_cost_per_million=Decimal('1.00'),
                output_cost_per_million=Decimal('5.00'),
                context_window=200000,
                max_output=8192,
                description='Claude 3.5 Haiku (Latest)'
            ),
            'claude-3-opus-20240229': ModelPricing(
                model_name='claude-3-opus-20240229',
                input_cost_per_million=Decimal('15.00'),
                output_cost_per_million=Decimal('75.00'),
                context_window=200000,
                max_output=4096,
                description='Claude 3 Opus'
            ),
            'claude-3-sonnet-20240229': ModelPricing(
                model_name='claude-3-sonnet-20240229',
                input_cost_per_million=Decimal('3.00'),
                output_cost_per_million=Decimal('15.00'),
                context_window=200000,
                max_output=4096,
                description='Claude 3 Sonnet'
            ),
            'claude-3-haiku-20240307': ModelPricing(
                model_name='claude-3-haiku-20240307',
                input_cost_per_million=Decimal('0.25'),
                output_cost_per_million=Decimal('1.25'),
                context_window=200000,
                max_output=4096,
                description='Claude 3 Haiku'
            )
        }
        
        # Alert configurations
        self.alerts: List[CostAlert] = []
        self.load_alerts()
        
        # Background monitoring
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_costs, daemon=True)
        self.monitor_thread.start()
    
    def init_database(self):
        """Initialize SQLite database for token tracking"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS token_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    input_tokens INTEGER NOT NULL,
                    output_tokens INTEGER NOT NULL,
                    total_tokens INTEGER NOT NULL,
                    input_cost DECIMAL(10,6) NOT NULL,
                    output_cost DECIMAL(10,6) NOT NULL,
                    total_cost DECIMAL(10,6) NOT NULL,
                    operation_type TEXT NOT NULL,
                    duration_seconds REAL,
                    context_length INTEGER,
                    temperature REAL,
                    max_tokens INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS cost_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id TEXT UNIQUE NOT NULL,
                    alert_type TEXT NOT NULL,
                    threshold_amount DECIMAL(10,2) NOT NULL,
                    notification_method TEXT NOT NULL,
                    enabled BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_triggered DATETIME
                );
                
                CREATE TABLE IF NOT EXISTS daily_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE UNIQUE NOT NULL,
                    total_tokens INTEGER NOT NULL,
                    total_cost DECIMAL(10,6) NOT NULL,
                    session_count INTEGER NOT NULL,
                    agent_breakdown TEXT,  -- JSON
                    model_breakdown TEXT,  -- JSON
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS optimization_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    recommendation_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    potential_savings DECIMAL(10,6),
                    implemented BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_usage_timestamp ON token_usage(timestamp);
                CREATE INDEX IF NOT EXISTS idx_usage_agent ON token_usage(agent_name);
                CREATE INDEX IF NOT EXISTS idx_usage_model ON token_usage(model_name);
                CREATE INDEX IF NOT EXISTS idx_usage_session ON token_usage(session_id);
                CREATE INDEX IF NOT EXISTS idx_daily_date ON daily_summaries(date);
            ''')
    
    def record_usage(self, session_id: str, agent_name: str, model_name: str,
                    input_tokens: int, output_tokens: int, operation_type: str = "completion",
                    duration_seconds: float = 0.0, context_length: int = 0,
                    temperature: float = 0.7, max_tokens: int = 4096) -> TokenUsage:
        """Record token usage and calculate costs"""
        
        timestamp = datetime.now()
        total_tokens = input_tokens + output_tokens
        
        # Calculate costs
        if model_name in self.model_pricing:
            pricing = self.model_pricing[model_name]
            input_cost = (Decimal(input_tokens) / Decimal(1_000_000)) * pricing.input_cost_per_million
            output_cost = (Decimal(output_tokens) / Decimal(1_000_000)) * pricing.output_cost_per_million
        else:
            # Default to Sonnet pricing if model not found
            pricing = self.model_pricing['claude-3-5-sonnet-20241022']
            input_cost = (Decimal(input_tokens) / Decimal(1_000_000)) * pricing.input_cost_per_million
            output_cost = (Decimal(output_tokens) / Decimal(1_000_000)) * pricing.output_cost_per_million
        
        total_cost = input_cost + output_cost
        
        # Round to 6 decimal places
        input_cost = input_cost.quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)
        output_cost = output_cost.quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)
        total_cost = total_cost.quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)
        
        usage = TokenUsage(
            session_id=session_id,
            agent_name=agent_name,
            model_name=model_name,
            timestamp=timestamp,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost,
            operation_type=operation_type,
            duration_seconds=duration_seconds,
            context_length=context_length,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO token_usage (
                    session_id, agent_name, model_name, timestamp,
                    input_tokens, output_tokens, total_tokens,
                    input_cost, output_cost, total_cost,
                    operation_type, duration_seconds, context_length,
                    temperature, max_tokens
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                usage.session_id, usage.agent_name, usage.model_name, usage.timestamp,
                usage.input_tokens, usage.output_tokens, usage.total_tokens,
                float(usage.input_cost), float(usage.output_cost), float(usage.total_cost),
                usage.operation_type, usage.duration_seconds, usage.context_length,
                usage.temperature, usage.max_tokens
            ))
        
        # Update daily summary
        self.update_daily_summary(timestamp.date())
        
        # Check alerts
        self.check_cost_alerts()
        
        return usage
    
    def get_usage_summary(self, start_date: Optional[date] = None, 
                         end_date: Optional[date] = None) -> Dict[str, Any]:
        """Get comprehensive usage summary"""
        
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()
        
        with sqlite3.connect(self.db_path) as conn:
            # Total costs and tokens
            total_query = '''
                SELECT 
                    SUM(total_tokens) as total_tokens,
                    SUM(total_cost) as total_cost,
                    COUNT(*) as total_requests,
                    COUNT(DISTINCT session_id) as unique_sessions,
                    COUNT(DISTINCT agent_name) as unique_agents,
                    AVG(total_cost) as avg_cost_per_request,
                    AVG(total_tokens) as avg_tokens_per_request
                FROM token_usage 
                WHERE DATE(timestamp) BETWEEN ? AND ?
            '''
            
            cursor = conn.execute(total_query, (start_date, end_date))
            total_stats = dict(zip([d[0] for d in cursor.description], cursor.fetchone()))
            
            # Cost by agent
            agent_query = '''
                SELECT 
                    agent_name,
                    SUM(total_tokens) as tokens,
                    SUM(total_cost) as cost,
                    COUNT(*) as requests,
                    AVG(total_cost) as avg_cost,
                    AVG(duration_seconds) as avg_duration
                FROM token_usage 
                WHERE DATE(timestamp) BETWEEN ? AND ?
                GROUP BY agent_name
                ORDER BY cost DESC
            '''
            
            agent_stats = []
            for row in conn.execute(agent_query, (start_date, end_date)):
                agent_stats.append({
                    'agent_name': row[0],
                    'tokens': row[1] or 0,
                    'cost': float(row[2] or 0),
                    'requests': row[3] or 0,
                    'avg_cost': float(row[4] or 0),
                    'avg_duration': row[5] or 0
                })
            
            # Cost by model
            model_query = '''
                SELECT 
                    model_name,
                    SUM(total_tokens) as tokens,
                    SUM(total_cost) as cost,
                    COUNT(*) as requests,
                    AVG(total_cost) as avg_cost
                FROM token_usage 
                WHERE DATE(timestamp) BETWEEN ? AND ?
                GROUP BY model_name
                ORDER BY cost DESC
            '''
            
            model_stats = []
            for row in conn.execute(model_query, (start_date, end_date)):
                model_stats.append({
                    'model_name': row[0],
                    'tokens': row[1] or 0,
                    'cost': float(row[2] or 0),
                    'requests': row[3] or 0,
                    'avg_cost': float(row[4] or 0)
                })
            
            # Daily breakdown
            daily_query = '''
                SELECT 
                    DATE(timestamp) as date,
                    SUM(total_tokens) as tokens,
                    SUM(total_cost) as cost,
                    COUNT(*) as requests
                FROM token_usage 
                WHERE DATE(timestamp) BETWEEN ? AND ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            '''
            
            daily_stats = []
            for row in conn.execute(daily_query, (start_date, end_date)):
                daily_stats.append({
                    'date': row[0],
                    'tokens': row[1] or 0,
                    'cost': float(row[2] or 0),
                    'requests': row[3] or 0
                })
        
        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': (end_date - start_date).days + 1
            },
            'totals': {
                'tokens': total_stats['total_tokens'] or 0,
                'cost': float(total_stats['total_cost'] or 0),
                'requests': total_stats['total_requests'] or 0,
                'sessions': total_stats['unique_sessions'] or 0,
                'agents': total_stats['unique_agents'] or 0,
                'avg_cost_per_request': float(total_stats['avg_cost_per_request'] or 0),
                'avg_tokens_per_request': total_stats['avg_tokens_per_request'] or 0
            },
            'by_agent': agent_stats,
            'by_model': model_stats,
            'daily_breakdown': daily_stats
        }
    
    def get_cost_trends(self, days: int = 30) -> Dict[str, Any]:
        """Analyze cost trends and patterns"""
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            # Daily trends
            trend_query = '''
                SELECT 
                    DATE(timestamp) as date,
                    SUM(total_cost) as daily_cost,
                    SUM(total_tokens) as daily_tokens,
                    COUNT(*) as daily_requests,
                    AVG(total_cost) as avg_request_cost
                FROM token_usage 
                WHERE DATE(timestamp) BETWEEN ? AND ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            '''
            
            trends = []
            for row in conn.execute(trend_query, (start_date, end_date)):
                trends.append({
                    'date': row[0],
                    'cost': float(row[1] or 0),
                    'tokens': row[2] or 0,
                    'requests': row[3] or 0,
                    'avg_cost': float(row[4] or 0)
                })
            
            # Hour-of-day analysis
            hourly_query = '''
                SELECT 
                    strftime('%H', timestamp) as hour,
                    AVG(total_cost) as avg_cost,
                    COUNT(*) as request_count
                FROM token_usage 
                WHERE DATE(timestamp) BETWEEN ? AND ?
                GROUP BY strftime('%H', timestamp)
                ORDER BY hour
            '''
            
            hourly_stats = []
            for row in conn.execute(hourly_query, (start_date, end_date)):
                hourly_stats.append({
                    'hour': int(row[0]),
                    'avg_cost': float(row[1] or 0),
                    'requests': row[2] or 0
                })
            
            # Calculate trend metrics
            if len(trends) >= 7:
                recent_week = trends[-7:]
                previous_week = trends[-14:-7] if len(trends) >= 14 else []
                
                recent_avg = sum(t['cost'] for t in recent_week) / len(recent_week)
                previous_avg = sum(t['cost'] for t in previous_week) / len(previous_week) if previous_week else recent_avg
                
                trend_direction = "increasing" if recent_avg > previous_avg else "decreasing"
                trend_percentage = ((recent_avg - previous_avg) / previous_avg * 100) if previous_avg > 0 else 0
            else:
                trend_direction = "insufficient_data"
                trend_percentage = 0
        
        return {
            'daily_trends': trends,
            'hourly_patterns': hourly_stats,
            'trend_analysis': {
                'direction': trend_direction,
                'percentage_change': trend_percentage,
                'period_days': days
            }
        }
    
    def generate_cost_optimization_recommendations(self) -> List[OptimizationRecommendation]:
        """Generate intelligent cost optimization recommendations"""
        
        recommendations = []
        summary = self.get_usage_summary(start_date=date.today() - timedelta(days=30))
        trends = self.get_cost_trends(30)
        
        # High-cost agent analysis
        high_cost_agents = [agent for agent in summary['by_agent'] if agent['cost'] > 10.0]
        if high_cost_agents:
            total_high_cost = sum(agent['cost'] for agent in high_cost_agents)
            recommendations.append(OptimizationRecommendation(
                category="agent_optimization",
                priority="high",
                description=f"High-cost agents consuming ${total_high_cost:.2f} in 30 days",
                potential_savings=Decimal(str(total_high_cost * 0.3)),
                implementation_effort="medium",
                estimated_impact="20-40% cost reduction",
                specific_actions=[
                    f"Review {agent['agent_name']} usage patterns" for agent in high_cost_agents[:3]
                ] + [
                    "Consider using Haiku model for simple tasks",
                    "Implement context length optimization",
                    "Add response caching for repetitive queries"
                ]
            ))
        
        # Model optimization
        expensive_models = [model for model in summary['by_model'] 
                           if model['model_name'].endswith('opus') and model['cost'] > 5.0]
        if expensive_models:
            opus_cost = sum(model['cost'] for model in expensive_models)
            recommendations.append(OptimizationRecommendation(
                category="model_optimization",
                priority="high",
                description=f"Opus model usage costing ${opus_cost:.2f} in 30 days",
                potential_savings=Decimal(str(opus_cost * 0.7)),
                implementation_effort="easy",
                estimated_impact="60-80% cost reduction",
                specific_actions=[
                    "Replace Opus with Sonnet for most tasks",
                    "Use Haiku for simple classification/extraction",
                    "Reserve Opus only for complex reasoning tasks",
                    "Implement model routing based on complexity"
                ]
            ))
        
        # Token efficiency
        avg_tokens = summary['totals']['avg_tokens_per_request']
        if avg_tokens > 8000:
            recommendations.append(OptimizationRecommendation(
                category="token_efficiency",
                priority="medium",
                description=f"High average token usage: {avg_tokens:.0f} tokens per request",
                potential_savings=Decimal(str(summary['totals']['cost'] * 0.25)),
                implementation_effort="medium",
                estimated_impact="15-30% cost reduction",
                specific_actions=[
                    "Implement prompt compression techniques",
                    "Use shorter system prompts",
                    "Reduce context window when possible",
                    "Implement response length limits",
                    "Add context pruning for long conversations"
                ]
            ))
        
        # Usage pattern optimization
        if trends['trend_analysis']['direction'] == "increasing" and trends['trend_analysis']['percentage_change'] > 20:
            recommendations.append(OptimizationRecommendation(
                category="usage_patterns",
                priority="medium",
                description=f"Cost increasing by {trends['trend_analysis']['percentage_change']:.1f}% recently",
                potential_savings=Decimal(str(summary['totals']['cost'] * 0.2)),
                implementation_effort="easy",
                estimated_impact="10-25% cost reduction",
                specific_actions=[
                    "Implement usage quotas per agent",
                    "Add cost alerts at $50, $100, $200 thresholds",
                    "Review and optimize high-frequency operations",
                    "Consider batch processing for similar requests"
                ]
            ))
        
        # Caching opportunities
        repeat_requests = self._analyze_repeat_patterns()
        if repeat_requests > 20:
            recommendations.append(OptimizationRecommendation(
                category="caching",
                priority="low",
                description=f"~{repeat_requests}% of requests could benefit from caching",
                potential_savings=Decimal(str(summary['totals']['cost'] * (repeat_requests / 100))),
                implementation_effort="hard",
                estimated_impact="10-30% cost reduction",
                specific_actions=[
                    "Implement response caching for common queries",
                    "Add semantic similarity detection",
                    "Cache model responses with TTL",
                    "Implement prompt deduplication"
                ]
            ))
        
        return recommendations
    
    def _analyze_repeat_patterns(self) -> float:
        """Analyze potential for caching based on repeat patterns"""
        # Simplified analysis - in production, would use semantic similarity
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT COUNT(*) as total_requests,
                       COUNT(DISTINCT agent_name || operation_type) as unique_patterns
                FROM token_usage 
                WHERE timestamp > datetime('now', '-7 days')
            ''')
            
            result = cursor.fetchone()
            if result and result[0] > 0:
                return max(0, (1 - result[1] / result[0]) * 100)
        
        return 0
    
    def create_cost_alert(self, alert_type: str, threshold_amount: float,
                         notification_method: str = "console") -> str:
        """Create a cost alert"""
        
        alert_id = f"{alert_type}_{int(time.time())}"
        alert = CostAlert(
            alert_id=alert_id,
            alert_type=alert_type,
            threshold_amount=Decimal(str(threshold_amount)),
            notification_method=notification_method,
            enabled=True,
            created_at=datetime.now()
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO cost_alerts (
                    alert_id, alert_type, threshold_amount,
                    notification_method, enabled
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                alert.alert_id, alert.alert_type, float(alert.threshold_amount),
                alert.notification_method, alert.enabled
            ))
        
        self.alerts.append(alert)
        return alert_id
    
    def check_cost_alerts(self):
        """Check if any cost alerts should be triggered"""
        
        current_time = datetime.now()
        
        for alert in self.alerts:
            if not alert.enabled:
                continue
            
            # Check if enough time has passed since last trigger
            if (alert.last_triggered and 
                current_time - alert.last_triggered < timedelta(hours=1)):
                continue
            
            should_trigger = False
            current_amount = Decimal('0')
            
            if alert.alert_type == "daily":
                today_summary = self.get_usage_summary(start_date=date.today(), end_date=date.today())
                current_amount = Decimal(str(today_summary['totals']['cost']))
                should_trigger = current_amount >= alert.threshold_amount
            
            elif alert.alert_type == "weekly":
                week_start = date.today() - timedelta(days=7)
                week_summary = self.get_usage_summary(start_date=week_start, end_date=date.today())
                current_amount = Decimal(str(week_summary['totals']['cost']))
                should_trigger = current_amount >= alert.threshold_amount
            
            elif alert.alert_type == "monthly":
                month_start = date.today().replace(day=1)
                month_summary = self.get_usage_summary(start_date=month_start, end_date=date.today())
                current_amount = Decimal(str(month_summary['totals']['cost']))
                should_trigger = current_amount >= alert.threshold_amount
            
            if should_trigger:
                self._trigger_alert(alert, current_amount)
    
    def _trigger_alert(self, alert: CostAlert, current_amount: Decimal):
        """Trigger a cost alert"""
        
        message = f"COST ALERT: {alert.alert_type} spending of ${current_amount:.2f} exceeds threshold of ${alert.threshold_amount:.2f}"
        
        if alert.notification_method == "console":
            print(f"\n{'='*60}")
            print(f"⚠️  {message}")
            print(f"Alert ID: {alert.alert_id}")
            print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}\n")
        
        # Update last triggered time
        alert.last_triggered = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE cost_alerts 
                SET last_triggered = ? 
                WHERE alert_id = ?
            ''', (alert.last_triggered, alert.alert_id))
    
    def update_daily_summary(self, target_date: date):
        """Update daily summary for given date"""
        
        with sqlite3.connect(self.db_path) as conn:
            # Get daily stats
            cursor = conn.execute('''
                SELECT 
                    SUM(total_tokens) as total_tokens,
                    SUM(total_cost) as total_cost,
                    COUNT(DISTINCT session_id) as session_count,
                    agent_name,
                    SUM(total_cost) as agent_cost,
                    model_name,
                    SUM(total_cost) as model_cost
                FROM token_usage 
                WHERE DATE(timestamp) = ?
                GROUP BY agent_name, model_name
            ''', (target_date,))
            
            # Aggregate by agent and model
            agent_breakdown = defaultdict(float)
            model_breakdown = defaultdict(float)
            total_tokens = 0
            total_cost = 0.0
            session_count = 0
            
            for row in cursor:
                if row[0]:  # If we have data
                    total_tokens = row[0]
                    total_cost = float(row[1])
                    session_count = row[2]
                    agent_breakdown[row[3]] += float(row[4])
                    model_breakdown[row[5]] += float(row[6])
            
            # Insert or update daily summary
            conn.execute('''
                INSERT OR REPLACE INTO daily_summaries 
                (date, total_tokens, total_cost, session_count, agent_breakdown, model_breakdown)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                target_date,
                total_tokens,
                total_cost,
                session_count,
                json.dumps(dict(agent_breakdown)),
                json.dumps(dict(model_breakdown))
            ))
    
    def load_alerts(self):
        """Load existing alerts from database"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT * FROM cost_alerts WHERE enabled = 1')
                
                for row in cursor:
                    alert = CostAlert(
                        alert_id=row[1],
                        alert_type=row[2],
                        threshold_amount=Decimal(str(row[3])),
                        notification_method=row[4],
                        enabled=bool(row[5]),
                        created_at=datetime.fromisoformat(row[6]),
                        last_triggered=datetime.fromisoformat(row[7]) if row[7] else None
                    )
                    self.alerts.append(alert)
        except Exception as e:
            print(f"Error loading alerts: {e}")
    
    def _monitor_costs(self):
        """Background cost monitoring thread"""
        
        while self.monitoring:
            try:
                self.check_cost_alerts()
                time.sleep(300)  # Check every 5 minutes
            except Exception as e:
                print(f"Cost monitoring error: {e}")
                time.sleep(60)
    
    def export_usage_data(self, filepath: str, format: str = "csv",
                         start_date: Optional[date] = None,
                         end_date: Optional[date] = None):
        """Export usage data for external analysis"""
        
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()
        
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT * FROM token_usage 
                WHERE DATE(timestamp) BETWEEN ? AND ?
                ORDER BY timestamp
            '''
            
            df = pd.read_sql_query(query, conn, params=(start_date, end_date))
        
        if format.lower() == "csv":
            df.to_csv(filepath, index=False)
        elif format.lower() == "json":
            df.to_json(filepath, orient='records', date_format='iso')
        elif format.lower() == "excel":
            df.to_excel(filepath, index=False)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def generate_cost_report(self, output_path: str, include_charts: bool = True):
        """Generate comprehensive cost analysis report"""
        
        summary = self.get_usage_summary()
        trends = self.get_cost_trends()
        recommendations = self.generate_cost_optimization_recommendations()
        
        # Create HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Claude Token Cost Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background: #f0f0f0; padding: 20px; border-radius: 8px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #e9f5ff; border-radius: 5px; }}
                .high-priority {{ background: #ffe6e6; }}
                .medium-priority {{ background: #fff3e0; }}
                .low-priority {{ background: #e8f5e8; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Claude Token Cost Analysis Report</h1>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Period: {summary['period']['start_date']} to {summary['period']['end_date']}</p>
            </div>
            
            <div class="section">
                <h2>Executive Summary</h2>
                <div class="metric">Total Cost: ${summary['totals']['cost']:.2f}</div>
                <div class="metric">Total Tokens: {summary['totals']['tokens']:,}</div>
                <div class="metric">Requests: {summary['totals']['requests']:,}</div>
                <div class="metric">Avg Cost/Request: ${summary['totals']['avg_cost_per_request']:.4f}</div>
            </div>
            
            <div class="section">
                <h2>Top Agents by Cost</h2>
                <table>
                    <tr><th>Agent</th><th>Cost</th><th>Tokens</th><th>Requests</th><th>Avg Cost</th></tr>
        """
        
        for agent in summary['by_agent'][:10]:
            html_content += f"""
                    <tr>
                        <td>{agent['agent_name']}</td>
                        <td>${agent['cost']:.2f}</td>
                        <td>{agent['tokens']:,}</td>
                        <td>{agent['requests']}</td>
                        <td>${agent['avg_cost']:.4f}</td>
                    </tr>
            """
        
        html_content += """
                </table>
            </div>
            
            <div class="section">
                <h2>Cost Optimization Recommendations</h2>
        """
        
        for rec in recommendations:
            priority_class = f"{rec.priority}-priority"
            html_content += f"""
                <div class="section {priority_class}">
                    <h3>{rec.category.replace('_', ' ').title()} - {rec.priority.upper()} Priority</h3>
                    <p><strong>Issue:</strong> {rec.description}</p>
                    <p><strong>Potential Savings:</strong> ${rec.potential_savings:.2f}</p>
                    <p><strong>Estimated Impact:</strong> {rec.estimated_impact}</p>
                    <p><strong>Implementation:</strong> {rec.implementation_effort}</p>
                    <ul>
            """
            
            for action in rec.specific_actions:
                html_content += f"<li>{action}</li>"
            
            html_content += """
                    </ul>
                </div>
            """
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        if include_charts:
            self._generate_cost_charts(str(Path(output_path).parent))
    
    def _generate_cost_charts(self, output_dir: str):
        """Generate cost visualization charts"""
        
        try:
            summary = self.get_usage_summary()
            trends = self.get_cost_trends()
            
            # Daily cost trend chart
            dates = [datetime.strptime(d['date'], '%Y-%m-%d').date() for d in trends['daily_trends']]
            costs = [d['cost'] for d in trends['daily_trends']]
            
            plt.figure(figsize=(12, 6))
            plt.plot(dates, costs, marker='o', linewidth=2, markersize=4)
            plt.title('Daily Cost Trends', fontsize=16, fontweight='bold')
            plt.xlabel('Date')
            plt.ylabel('Cost (USD)')
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(f"{output_dir}/daily_costs.png", dpi=300, bbox_inches='tight')
            plt.close()
            
            # Agent cost breakdown pie chart
            agent_names = [a['agent_name'] for a in summary['by_agent'][:8]]
            agent_costs = [a['cost'] for a in summary['by_agent'][:8]]
            
            plt.figure(figsize=(10, 8))
            plt.pie(agent_costs, labels=agent_names, autopct='%1.1f%%', startangle=90)
            plt.title('Cost Distribution by Agent', fontsize=16, fontweight='bold')
            plt.axis('equal')
            plt.tight_layout()
            plt.savefig(f"{output_dir}/agent_cost_distribution.png", dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"Charts saved to {output_dir}/")
            
        except Exception as e:
            print(f"Error generating charts: {e}")
    
    def get_model_comparison(self) -> Dict[str, Any]:
        """Compare costs across different Claude models"""
        
        comparison = {}
        
        for model_name, pricing in self.model_pricing.items():
            # Calculate cost per 1K tokens for different scenarios
            scenarios = {
                'chat_small': (1000, 200),      # 1K input, 200 output
                'chat_medium': (2000, 500),     # 2K input, 500 output
                'chat_large': (5000, 1000),     # 5K input, 1K output
                'document_analysis': (10000, 2000),  # 10K input, 2K output
                'code_generation': (3000, 1500),     # 3K input, 1.5K output
            }
            
            model_costs = {}
            for scenario, (input_tokens, output_tokens) in scenarios.items():
                input_cost = (Decimal(input_tokens) / Decimal(1_000_000)) * pricing.input_cost_per_million
                output_cost = (Decimal(output_tokens) / Decimal(1_000_000)) * pricing.output_cost_per_million
                total_cost = float(input_cost + output_cost)
                model_costs[scenario] = total_cost
            
            comparison[model_name] = {
                'pricing': asdict(pricing),
                'scenario_costs': model_costs,
                'cost_per_1k_tokens': {
                    'input_only': float(pricing.input_cost_per_million / 1000),
                    'output_only': float(pricing.output_cost_per_million / 1000),
                    'mixed_avg': float((pricing.input_cost_per_million + pricing.output_cost_per_million) / 2000)
                }
            }
        
        return comparison
    
    def predict_monthly_cost(self, based_on_days: int = 7) -> Dict[str, Any]:
        """Predict monthly costs based on recent usage"""
        
        end_date = date.today()
        start_date = end_date - timedelta(days=based_on_days)
        
        recent_summary = self.get_usage_summary(start_date=start_date, end_date=end_date)
        daily_avg_cost = recent_summary['totals']['cost'] / based_on_days
        
        # Project to full month (30 days)
        monthly_projection = daily_avg_cost * 30
        
        # Calculate confidence intervals based on daily variance
        trends = self.get_cost_trends(based_on_days)
        daily_costs = [d['cost'] for d in trends['daily_trends']]
        
        if len(daily_costs) > 1:
            std_dev = np.std(daily_costs)
            confidence_95 = {
                'lower': max(0, monthly_projection - (1.96 * std_dev * np.sqrt(30))),
                'upper': monthly_projection + (1.96 * std_dev * np.sqrt(30))
            }
        else:
            confidence_95 = {'lower': monthly_projection * 0.7, 'upper': monthly_projection * 1.3}
        
        return {
            'based_on_days': based_on_days,
            'daily_average': daily_avg_cost,
            'monthly_projection': monthly_projection,
            'confidence_95': confidence_95,
            'breakdown_projection': {
                'by_agent': [
                    {
                        'agent_name': agent['agent_name'],
                        'monthly_cost': (agent['cost'] / based_on_days) * 30
                    }
                    for agent in recent_summary['by_agent']
                ],
                'by_model': [
                    {
                        'model_name': model['model_name'],
                        'monthly_cost': (model['cost'] / based_on_days) * 30
                    }
                    for model in recent_summary['by_model']
                ]
            }
        }
    
    def cleanup(self):
        """Cleanup resources"""
        self.monitoring = False

def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Claude Token Cost Calculator')
    parser.add_argument('command', choices=[
        'record', 'summary', 'trends', 'optimize', 'alerts', 'export', 'report', 'compare', 'predict'
    ], help='Command to execute')
    
    # Record usage arguments
    parser.add_argument('--session-id', help='Session ID for recording')
    parser.add_argument('--agent', help='Agent name for recording')
    parser.add_argument('--model', help='Model name for recording')
    parser.add_argument('--input-tokens', type=int, help='Input tokens')
    parser.add_argument('--output-tokens', type=int, help='Output tokens')
    parser.add_argument('--operation', default='completion', help='Operation type')
    
    # Alert arguments
    parser.add_argument('--alert-type', choices=['daily', 'weekly', 'monthly'], help='Alert type')
    parser.add_argument('--threshold', type=float, help='Alert threshold amount')
    
    # Export arguments
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--format', choices=['csv', 'json', 'excel'], default='csv', help='Export format')
    
    # Date range arguments
    parser.add_argument('--start-date', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')
    parser.add_argument('--days', type=int, default=30, help='Number of days for analysis')
    
    args = parser.parse_args()
    
    calculator = TokenCostCalculator()
    
    try:
        if args.command == 'record':
            if not all([args.session_id, args.agent, args.model, args.input_tokens, args.output_tokens]):
                print("Error: Missing required arguments for record command")
                return
            
            usage = calculator.record_usage(
                session_id=args.session_id,
                agent_name=args.agent,
                model_name=args.model,
                input_tokens=args.input_tokens,
                output_tokens=args.output_tokens,
                operation_type=args.operation
            )
            
            print(f"Recorded: {usage.total_tokens} tokens, ${usage.total_cost:.6f}")
        
        elif args.command == 'summary':
            start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date() if args.start_date else None
            end_date = datetime.strptime(args.end_date, '%Y-%m-%d').date() if args.end_date else None
            
            summary = calculator.get_usage_summary(start_date=start_date, end_date=end_date)
            print(json.dumps(summary, indent=2, default=str))
        
        elif args.command == 'trends':
            trends = calculator.get_cost_trends(args.days)
            print(json.dumps(trends, indent=2, default=str))
        
        elif args.command == 'optimize':
            recommendations = calculator.generate_cost_optimization_recommendations()
            for rec in recommendations:
                print(f"\n{rec.priority.upper()} PRIORITY: {rec.category}")
                print(f"Description: {rec.description}")
                print(f"Potential Savings: ${rec.potential_savings:.2f}")
                print(f"Actions: {', '.join(rec.specific_actions[:3])}")
        
        elif args.command == 'alerts':
            if args.alert_type and args.threshold:
                alert_id = calculator.create_cost_alert(args.alert_type, args.threshold)
                print(f"Created alert: {alert_id}")
            else:
                print("Active alerts:")
                for alert in calculator.alerts:
                    print(f"- {alert.alert_id}: {alert.alert_type} ${alert.threshold_amount}")
        
        elif args.command == 'export':
            if not args.output:
                print("Error: Output file path required for export")
                return
            
            start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date() if args.start_date else None
            end_date = datetime.strptime(args.end_date, '%Y-%m-%d').date() if args.end_date else None
            
            calculator.export_usage_data(args.output, args.format, start_date, end_date)
            print(f"Data exported to {args.output}")
        
        elif args.command == 'report':
            output_path = args.output or f"cost_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            calculator.generate_cost_report(output_path)
            print(f"Report generated: {output_path}")
        
        elif args.command == 'compare':
            comparison = calculator.get_model_comparison()
            print(json.dumps(comparison, indent=2, default=str))
        
        elif args.command == 'predict':
            prediction = calculator.predict_monthly_cost(args.days)
            print(json.dumps(prediction, indent=2, default=str))
    
    finally:
        calculator.cleanup()

if __name__ == '__main__':
    main()