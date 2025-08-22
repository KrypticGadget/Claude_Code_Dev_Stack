#!/usr/bin/env python3
"""
Real-time Agent Performance Monitoring System
Comprehensive monitoring and analytics for agent performance and system health
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics
import time
from concurrent.futures import ThreadPoolExecutor

from .agent_metadata_db import (
    AsyncAgentMetadataDB, DatabaseConfig, create_database_manager,
    ExecutionStatus, AgentStatus
)


# ========== MONITORING DATA STRUCTURES ==========

@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    category: str
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    
    @property
    def status(self) -> str:
        """Get metric status based on thresholds"""
        if self.threshold_critical and self.value >= self.threshold_critical:
            return "critical"
        elif self.threshold_warning and self.value >= self.threshold_warning:
            return "warning"
        else:
            return "ok"


@dataclass
class AgentHealthStatus:
    """Health status for a single agent"""
    agent_id: str
    agent_name: str
    status: str
    last_execution: Optional[datetime]
    success_rate_24h: float
    avg_response_time_24h: float
    total_executions_24h: int
    current_load: int
    error_count_24h: int
    health_score: float
    issues: List[str]


@dataclass
class SystemHealthReport:
    """Overall system health report"""
    timestamp: datetime
    overall_health_score: float
    total_agents: int
    active_agents: int
    total_executions_24h: int
    avg_success_rate: float
    avg_response_time: float
    system_load: float
    agent_health: List[AgentHealthStatus]
    performance_metrics: List[PerformanceMetric]
    alerts: List[Dict[str, Any]]


@dataclass
class PerformanceTrend:
    """Performance trend data"""
    metric_name: str
    time_series: List[Tuple[datetime, float]]
    trend_direction: str  # "up", "down", "stable"
    trend_percentage: float
    forecast_24h: Optional[float]


# ========== REAL-TIME METRICS COLLECTOR ==========

class MetricsCollector:
    """Collects and aggregates real-time metrics"""
    
    def __init__(self, db: AsyncAgentMetadataDB):
        self.db = db
        self.logger = logging.getLogger(__name__)
        
        # In-memory metric storage (sliding window)
        self.metrics_buffer = defaultdict(lambda: deque(maxlen=1000))
        self.alert_thresholds = self._load_alert_thresholds()
        
        # Performance tracking
        self.collection_intervals = {
            'system_health': 30,  # seconds
            'agent_performance': 60,
            'resource_usage': 15,
            'error_rates': 30
        }
        
        self._collection_tasks = {}
        self._is_running = False
    
    def _load_alert_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Load alert thresholds configuration"""
        return {
            'response_time_ms': {'warning': 5000, 'critical': 10000},
            'error_rate_percent': {'warning': 10, 'critical': 25},
            'success_rate_percent': {'warning': 85, 'critical': 70},
            'queue_length': {'warning': 50, 'critical': 100},
            'memory_usage_mb': {'warning': 512, 'critical': 1024},
            'cpu_usage_percent': {'warning': 80, 'critical': 95}
        }
    
    async def start_collection(self):
        """Start real-time metrics collection"""
        if self._is_running:
            return
        
        self._is_running = True
        self.logger.info("Starting metrics collection")
        
        # Start collection tasks
        self._collection_tasks = {
            'system_health': asyncio.create_task(self._collect_system_health()),
            'agent_performance': asyncio.create_task(self._collect_agent_performance()),
            'resource_usage': asyncio.create_task(self._collect_resource_usage()),
            'error_tracking': asyncio.create_task(self._collect_error_metrics())
        }
    
    async def stop_collection(self):
        """Stop metrics collection"""
        self._is_running = False
        
        # Cancel all collection tasks
        for task_name, task in self._collection_tasks.items():
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        self._collection_tasks.clear()
        self.logger.info("Stopped metrics collection")
    
    async def _collect_system_health(self):
        """Collect system-wide health metrics"""
        while self._is_running:
            try:
                # Get system health from database
                health_data = await self.db.get_system_health()
                
                for metric_name, metric_info in health_data.items():
                    metric = PerformanceMetric(
                        name=metric_name,
                        value=metric_info['value'],
                        unit='count',
                        timestamp=datetime.now(),
                        category='system_health',
                        threshold_warning=self.alert_thresholds.get(metric_name, {}).get('warning'),
                        threshold_critical=self.alert_thresholds.get(metric_name, {}).get('critical')
                    )
                    self.metrics_buffer[metric_name].append(metric)
                
                await asyncio.sleep(self.collection_intervals['system_health'])
                
            except Exception as e:
                self.logger.error(f"Error collecting system health: {e}")
                await asyncio.sleep(5)
    
    async def _collect_agent_performance(self):
        """Collect individual agent performance metrics"""
        while self._is_running:
            try:
                # Get all active agents
                agents = await self.db.search_agents(limit=100)
                
                for agent in agents:
                    # Get performance for last 24h
                    performance = await self.db.get_agent_performance(agent.id, days=1)
                    
                    # Create metrics
                    metrics = [
                        PerformanceMetric(
                            name=f"agent_{agent.name}_success_rate",
                            value=performance['success_rate'],
                            unit='percent',
                            timestamp=datetime.now(),
                            category='agent_performance',
                            threshold_warning=85,
                            threshold_critical=70
                        ),
                        PerformanceMetric(
                            name=f"agent_{agent.name}_avg_duration",
                            value=performance['avg_duration_ms'],
                            unit='milliseconds',
                            timestamp=datetime.now(),
                            category='agent_performance',
                            threshold_warning=5000,
                            threshold_critical=10000
                        ),
                        PerformanceMetric(
                            name=f"agent_{agent.name}_executions",
                            value=performance['total_executions'],
                            unit='count',
                            timestamp=datetime.now(),
                            category='agent_performance'
                        )
                    ]
                    
                    for metric in metrics:
                        self.metrics_buffer[metric.name].append(metric)
                
                await asyncio.sleep(self.collection_intervals['agent_performance'])
                
            except Exception as e:
                self.logger.error(f"Error collecting agent performance: {e}")
                await asyncio.sleep(10)
    
    async def _collect_resource_usage(self):
        """Collect resource usage metrics"""
        while self._is_running:
            try:
                # Get database connection pool status
                pool_info = self.db.pool
                if pool_info:
                    pool_metric = PerformanceMetric(
                        name="db_connection_pool_usage",
                        value=pool_info.get_size() - pool_info.get_idle_size(),
                        unit='connections',
                        timestamp=datetime.now(),
                        category='resource_usage',
                        threshold_warning=15,
                        threshold_critical=18
                    )
                    self.metrics_buffer['db_connection_pool_usage'].append(pool_metric)
                
                # System resource metrics would go here
                # (CPU, memory, disk, network)
                
                await asyncio.sleep(self.collection_intervals['resource_usage'])
                
            except Exception as e:
                self.logger.error(f"Error collecting resource usage: {e}")
                await asyncio.sleep(5)
    
    async def _collect_error_metrics(self):
        """Collect error and failure metrics"""
        while self._is_running:
            try:
                # Query recent errors from execution_history
                query = """
                SELECT 
                    COUNT(*) as total_errors,
                    COUNT(DISTINCT agent_id) as agents_with_errors,
                    AVG(EXTRACT(EPOCH FROM (NOW() - started_at))) as avg_time_to_error
                FROM execution_history 
                WHERE status = 'failed' 
                AND started_at >= NOW() - INTERVAL '1 hour'
                """
                
                async with self.db.get_connection() as conn:
                    result = await conn.fetchrow(query)
                
                if result:
                    error_metrics = [
                        PerformanceMetric(
                            name="error_count_1h",
                            value=result['total_errors'],
                            unit='count',
                            timestamp=datetime.now(),
                            category='error_tracking',
                            threshold_warning=10,
                            threshold_critical=25
                        ),
                        PerformanceMetric(
                            name="agents_with_errors_1h",
                            value=result['agents_with_errors'],
                            unit='count',
                            timestamp=datetime.now(),
                            category='error_tracking',
                            threshold_warning=5,
                            threshold_critical=10
                        )
                    ]
                    
                    for metric in error_metrics:
                        self.metrics_buffer[metric.name].append(metric)
                
                await asyncio.sleep(self.collection_intervals['error_rates'])
                
            except Exception as e:
                self.logger.error(f"Error collecting error metrics: {e}")
                await asyncio.sleep(10)
    
    def get_current_metrics(self, category: str = None) -> List[PerformanceMetric]:
        """Get current metrics, optionally filtered by category"""
        current_metrics = []
        
        for metric_name, metric_deque in self.metrics_buffer.items():
            if metric_deque:
                latest_metric = metric_deque[-1]
                if category is None or latest_metric.category == category:
                    current_metrics.append(latest_metric)
        
        return current_metrics
    
    def get_metric_history(self, metric_name: str, hours: int = 24) -> List[PerformanceMetric]:
        """Get historical data for a specific metric"""
        if metric_name not in self.metrics_buffer:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            metric for metric in self.metrics_buffer[metric_name]
            if metric.timestamp >= cutoff_time
        ]


# ========== PERFORMANCE MONITOR ==========

class PerformanceMonitor:
    """Main performance monitoring system"""
    
    def __init__(self, db: AsyncAgentMetadataDB):
        self.db = db
        self.metrics_collector = MetricsCollector(db)
        self.logger = logging.getLogger(__name__)
        
        # Alert management
        self.active_alerts = {}
        self.alert_cooldowns = {}
        self.alert_callbacks = []
    
    async def start_monitoring(self):
        """Start the performance monitoring system"""
        await self.metrics_collector.start_collection()
        self.logger.info("Performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop the performance monitoring system"""
        await self.metrics_collector.stop_collection()
        self.logger.info("Performance monitoring stopped")
    
    async def get_system_health_report(self) -> SystemHealthReport:
        """Generate comprehensive system health report"""
        
        # Get current metrics
        metrics = self.metrics_collector.get_current_metrics()
        
        # Get agent health statuses
        agent_health = await self._get_agent_health_statuses()
        
        # Calculate overall health score
        overall_health = self._calculate_overall_health_score(metrics, agent_health)
        
        # Get system statistics
        system_stats = await self._get_system_statistics()
        
        # Generate alerts
        alerts = self._generate_alerts(metrics, agent_health)
        
        return SystemHealthReport(
            timestamp=datetime.now(),
            overall_health_score=overall_health,
            total_agents=system_stats['total_agents'],
            active_agents=system_stats['active_agents'],
            total_executions_24h=system_stats['executions_24h'],
            avg_success_rate=system_stats['avg_success_rate'],
            avg_response_time=system_stats['avg_response_time'],
            system_load=system_stats['system_load'],
            agent_health=agent_health,
            performance_metrics=metrics,
            alerts=alerts
        )
    
    async def _get_agent_health_statuses(self) -> List[AgentHealthStatus]:
        """Get health status for all agents"""
        
        query = """
        SELECT 
            a.id,
            a.name,
            a.status,
            a.last_active_at,
            
            -- 24h performance metrics
            COUNT(eh.id) as executions_24h,
            COUNT(CASE WHEN eh.status = 'completed' THEN 1 END) as success_24h,
            COUNT(CASE WHEN eh.status = 'failed' THEN 1 END) as error_24h,
            AVG(CASE WHEN eh.duration_ms IS NOT NULL THEN eh.duration_ms END) as avg_duration_24h,
            
            -- Current load (running executions)
            COUNT(CASE WHEN eh.status = 'running' THEN 1 END) as current_load
            
        FROM agents a
        LEFT JOIN execution_history eh ON a.id = eh.agent_id 
            AND eh.started_at >= NOW() - INTERVAL '24 hours'
        WHERE a.status != 'deprecated'
        GROUP BY a.id, a.name, a.status, a.last_active_at
        ORDER BY a.name
        """
        
        agent_statuses = []
        
        async with self.db.get_connection() as conn:
            rows = await conn.fetch(query)
        
        for row in rows:
            # Calculate metrics
            executions_24h = row['executions_24h'] or 0
            success_24h = row['success_24h'] or 0
            error_24h = row['error_24h'] or 0
            
            success_rate = (success_24h / executions_24h * 100) if executions_24h > 0 else 100
            avg_response_time = row['avg_duration_24h'] or 0
            
            # Calculate health score
            health_score = self._calculate_agent_health_score(
                success_rate, avg_response_time, executions_24h, error_24h
            )
            
            # Identify issues
            issues = []
            if success_rate < 80:
                issues.append(f"Low success rate: {success_rate:.1f}%")
            if avg_response_time > 5000:
                issues.append(f"High response time: {avg_response_time:.0f}ms")
            if error_24h > 5:
                issues.append(f"High error count: {error_24h}")
            if row['current_load'] > 5:
                issues.append(f"High current load: {row['current_load']}")
            
            agent_status = AgentHealthStatus(
                agent_id=str(row['id']),
                agent_name=row['name'],
                status=row['status'],
                last_execution=row['last_active_at'],
                success_rate_24h=success_rate,
                avg_response_time_24h=avg_response_time,
                total_executions_24h=executions_24h,
                current_load=row['current_load'] or 0,
                error_count_24h=error_24h,
                health_score=health_score,
                issues=issues
            )
            
            agent_statuses.append(agent_status)
        
        return agent_statuses
    
    def _calculate_agent_health_score(self, 
                                    success_rate: float,
                                    avg_response_time: float,
                                    executions: int,
                                    errors: int) -> float:
        """Calculate health score for an agent (0-100)"""
        
        # Success rate component (40%)
        success_score = min(100, success_rate)
        
        # Response time component (30%)
        # Score decreases as response time increases
        if avg_response_time <= 1000:
            response_score = 100
        elif avg_response_time <= 5000:
            response_score = 100 - ((avg_response_time - 1000) / 4000) * 50
        else:
            response_score = max(0, 50 - ((avg_response_time - 5000) / 10000) * 50)
        
        # Activity component (20%)
        if executions == 0:
            activity_score = 50  # Neutral for inactive agents
        elif executions < 5:
            activity_score = 70
        else:
            activity_score = 100
        
        # Error rate component (10%)
        if errors == 0:
            error_score = 100
        elif errors <= 2:
            error_score = 80
        elif errors <= 5:
            error_score = 60
        else:
            error_score = max(0, 60 - (errors - 5) * 10)
        
        # Weighted average
        total_score = (
            success_score * 0.4 +
            response_score * 0.3 +
            activity_score * 0.2 +
            error_score * 0.1
        )
        
        return round(total_score, 1)
    
    def _calculate_overall_health_score(self, 
                                      metrics: List[PerformanceMetric],
                                      agent_health: List[AgentHealthStatus]) -> float:
        """Calculate overall system health score"""
        
        if not agent_health:
            return 0.0
        
        # Average agent health scores
        agent_scores = [agent.health_score for agent in agent_health if agent.status == 'active']
        avg_agent_health = statistics.mean(agent_scores) if agent_scores else 50
        
        # System metric scores
        system_score = 100
        for metric in metrics:
            if metric.category == 'system_health' and metric.status != 'ok':
                if metric.status == 'warning':
                    system_score -= 10
                elif metric.status == 'critical':
                    system_score -= 25
        
        # Weighted combination
        overall_score = (avg_agent_health * 0.7 + max(0, system_score) * 0.3)
        
        return round(overall_score, 1)
    
    async def _get_system_statistics(self) -> Dict[str, Any]:
        """Get system-wide statistics"""
        
        query = """
        SELECT 
            (SELECT COUNT(*) FROM agents WHERE status != 'deprecated') as total_agents,
            (SELECT COUNT(*) FROM agents WHERE status = 'active') as active_agents,
            (SELECT COUNT(*) FROM execution_history WHERE started_at >= NOW() - INTERVAL '24 hours') as executions_24h,
            (SELECT AVG(success_count::float / GREATEST(total_executions, 1) * 100) 
             FROM agents WHERE status = 'active' AND total_executions > 0) as avg_success_rate,
            (SELECT AVG(avg_execution_time_ms) 
             FROM agents WHERE status = 'active' AND avg_execution_time_ms > 0) as avg_response_time,
            (SELECT COUNT(*) FROM execution_history WHERE status = 'running') as current_load
        """
        
        async with self.db.get_connection() as conn:
            result = await conn.fetchrow(query)
        
        return {
            'total_agents': result['total_agents'] or 0,
            'active_agents': result['active_agents'] or 0,
            'executions_24h': result['executions_24h'] or 0,
            'avg_success_rate': float(result['avg_success_rate'] or 0),
            'avg_response_time': float(result['avg_response_time'] or 0),
            'system_load': result['current_load'] or 0
        }
    
    def _generate_alerts(self, 
                        metrics: List[PerformanceMetric],
                        agent_health: List[AgentHealthStatus]) -> List[Dict[str, Any]]:
        """Generate alerts based on current metrics and agent health"""
        
        alerts = []
        
        # Metric-based alerts
        for metric in metrics:
            if metric.status in ['warning', 'critical']:
                alert = {
                    'type': 'metric_threshold',
                    'severity': metric.status,
                    'title': f"{metric.name} {metric.status}",
                    'description': f"{metric.name} is {metric.value} {metric.unit}",
                    'metric_name': metric.name,
                    'current_value': metric.value,
                    'threshold': metric.threshold_warning if metric.status == 'warning' else metric.threshold_critical,
                    'timestamp': metric.timestamp
                }
                alerts.append(alert)
        
        # Agent health alerts
        for agent in agent_health:
            if agent.health_score < 70:
                severity = 'critical' if agent.health_score < 50 else 'warning'
                alert = {
                    'type': 'agent_health',
                    'severity': severity,
                    'title': f"Agent {agent.agent_name} health issues",
                    'description': f"Health score: {agent.health_score:.1f}. Issues: {', '.join(agent.issues)}",
                    'agent_id': agent.agent_id,
                    'agent_name': agent.agent_name,
                    'health_score': agent.health_score,
                    'issues': agent.issues,
                    'timestamp': datetime.now()
                }
                alerts.append(alert)
        
        return alerts
    
    async def get_performance_trends(self, hours: int = 24) -> List[PerformanceTrend]:
        """Get performance trends over time"""
        
        trends = []
        key_metrics = [
            'total_agents', 'avg_success_rate', 'error_count_1h',
            'db_connection_pool_usage'
        ]
        
        for metric_name in key_metrics:
            history = self.metrics_collector.get_metric_history(metric_name, hours)
            
            if len(history) >= 2:
                # Calculate trend
                values = [m.value for m in history]
                timestamps = [m.timestamp for m in history]
                
                # Simple linear trend calculation
                first_half = values[:len(values)//2]
                second_half = values[len(values)//2:]
                
                if first_half and second_half:
                    trend_percentage = ((statistics.mean(second_half) - statistics.mean(first_half)) / 
                                      statistics.mean(first_half)) * 100
                    
                    if abs(trend_percentage) < 5:
                        direction = "stable"
                    elif trend_percentage > 0:
                        direction = "up"
                    else:
                        direction = "down"
                    
                    trend = PerformanceTrend(
                        metric_name=metric_name,
                        time_series=list(zip(timestamps, values)),
                        trend_direction=direction,
                        trend_percentage=trend_percentage,
                        forecast_24h=None  # Could implement forecasting
                    )
                    
                    trends.append(trend)
        
        return trends
    
    def add_alert_callback(self, callback):
        """Add callback function for alert notifications"""
        self.alert_callbacks.append(callback)
    
    async def _trigger_alert_callbacks(self, alert: Dict[str, Any]):
        """Trigger all registered alert callbacks"""
        for callback in self.alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(alert)
                else:
                    callback(alert)
            except Exception as e:
                self.logger.error(f"Error in alert callback: {e}")


# ========== DASHBOARD QUERY INTERFACE ==========

class DashboardQueries:
    """Optimized queries for dashboard displays"""
    
    def __init__(self, db: AsyncAgentMetadataDB):
        self.db = db
    
    async def get_top_performing_agents(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing agents by success rate and activity"""
        
        query = """
        SELECT 
            a.name,
            a.display_name,
            a.specializations,
            a.total_executions,
            a.success_count,
            CASE 
                WHEN a.total_executions > 0 THEN (a.success_count::float / a.total_executions * 100)
                ELSE 0 
            END as success_rate,
            a.avg_execution_time_ms,
            a.last_active_at,
            COUNT(eh.id) as executions_24h
        FROM agents a
        LEFT JOIN execution_history eh ON a.id = eh.agent_id 
            AND eh.started_at >= NOW() - INTERVAL '24 hours'
        WHERE a.status = 'active' AND a.total_executions > 0
        GROUP BY a.id, a.name, a.display_name, a.specializations, 
                 a.total_executions, a.success_count, a.avg_execution_time_ms, a.last_active_at
        ORDER BY success_rate DESC, a.total_executions DESC
        LIMIT $1
        """
        
        async with self.db.get_connection() as conn:
            rows = await conn.fetch(query, limit)
        
        return [dict(row) for row in rows]
    
    async def get_execution_timeline(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get execution timeline for the last N hours"""
        
        query = """
        SELECT 
            DATE_TRUNC('hour', started_at) as hour,
            COUNT(*) as total_executions,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful,
            COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
            AVG(duration_ms) as avg_duration
        FROM execution_history 
        WHERE started_at >= NOW() - INTERVAL '%s hours'
        GROUP BY DATE_TRUNC('hour', started_at)
        ORDER BY hour
        """ % hours
        
        async with self.db.get_connection() as conn:
            rows = await conn.fetch(query)
        
        return [dict(row) for row in rows]
    
    async def get_error_summary(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get error summary by agent and error type"""
        
        query = """
        SELECT 
            a.name as agent_name,
            COUNT(*) as error_count,
            array_agg(DISTINCT COALESCE(eh.error_details, 'Unknown error')) as error_types,
            MAX(eh.started_at) as last_error_time
        FROM execution_history eh
        JOIN agents a ON eh.agent_id = a.id
        WHERE eh.status = 'failed' 
        AND eh.started_at >= NOW() - INTERVAL '%s hours'
        GROUP BY a.name
        ORDER BY error_count DESC
        """ % hours
        
        async with self.db.get_connection() as conn:
            rows = await conn.fetch(query)
        
        return [dict(row) for row in rows]
    
    async def get_collaboration_network(self) -> List[Dict[str, Any]]:
        """Get agent collaboration network data"""
        
        query = """
        SELECT 
            af.name as from_agent,
            at.name as to_agent,
            cp.total_handoffs,
            cp.successful_handoffs,
            cp.collaboration_score,
            cp.last_collaboration
        FROM collaboration_patterns cp
        JOIN agents af ON cp.from_agent_id = af.id
        JOIN agents at ON cp.to_agent_id = at.id
        WHERE cp.total_handoffs > 0
        ORDER BY cp.total_handoffs DESC
        """
        
        async with self.db.get_connection() as conn:
            rows = await conn.fetch(query)
        
        return [dict(row) for row in rows]


# ========== FACTORY FUNCTION ==========

async def create_performance_monitor() -> PerformanceMonitor:
    """Create and initialize performance monitor"""
    db = create_database_manager(async_mode=True)
    await db.initialize()
    return PerformanceMonitor(db)


# ========== EXAMPLE USAGE ==========

async def example_monitoring():
    """Example usage of performance monitoring"""
    
    # Create monitor
    monitor = await create_performance_monitor()
    
    try:
        # Start monitoring
        await monitor.start_monitoring()
        
        # Wait a bit for metrics to collect
        await asyncio.sleep(5)
        
        # Get health report
        health_report = await monitor.get_system_health_report()
        
        print(f"System Health Score: {health_report.overall_health_score:.1f}")
        print(f"Active Agents: {health_report.active_agents}/{health_report.total_agents}")
        print(f"24h Executions: {health_report.total_executions_24h}")
        print(f"Average Success Rate: {health_report.avg_success_rate:.1f}%")
        
        # Show agent health
        print("\nAgent Health:")
        for agent in health_report.agent_health[:5]:
            print(f"- {agent.agent_name}: {agent.health_score:.1f} "
                  f"({agent.success_rate_24h:.1f}% success, {agent.total_executions_24h} executions)")
        
        # Show alerts
        if health_report.alerts:
            print(f"\nAlerts ({len(health_report.alerts)}):")
            for alert in health_report.alerts[:3]:
                print(f"- {alert['severity'].upper()}: {alert['title']}")
        
        # Get trends
        trends = await monitor.get_performance_trends(hours=24)
        print(f"\nTrends ({len(trends)}):")
        for trend in trends:
            print(f"- {trend.metric_name}: {trend.trend_direction} "
                  f"({trend.trend_percentage:+.1f}%)")
        
    finally:
        await monitor.stop_monitoring()
        await monitor.db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(example_monitoring())