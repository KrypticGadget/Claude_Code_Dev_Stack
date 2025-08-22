#!/usr/bin/env python3
"""
Claude Token Usage Dashboard - Real-time Web Interface
Live monitoring and cost optimization dashboard for Claude API usage
"""

import json
import asyncio
import threading
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Dict, List, Optional, Any
import sqlite3
from decimal import Decimal

import uvicorn
from fastapi import FastAPI, WebSocket, Request, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import websockets
from contextlib import asynccontextmanager

from token_cost_calculator import TokenCostCalculator

class TokenDashboard:
    """Real-time token usage dashboard"""
    
    def __init__(self, calculator: TokenCostCalculator):
        self.calculator = calculator
        self.active_connections: List[WebSocket] = []
        self.app = self._create_app()
        
        # Background monitoring
        self.monitoring = True
        self.monitor_task = None
    
    def _create_app(self) -> FastAPI:
        """Create FastAPI application"""
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            self.monitor_task = asyncio.create_task(self._monitor_usage())
            yield
            # Shutdown
            self.monitoring = False
            if self.monitor_task:
                self.monitor_task.cancel()
        
        app = FastAPI(
            title="Claude Token Usage Dashboard",
            description="Real-time monitoring and cost optimization for Claude API usage",
            version="1.0.0",
            lifespan=lifespan
        )
        
        # Setup templates and static files
        templates_dir = Path(__file__).parent / "templates"
        static_dir = Path(__file__).parent / "static"
        templates_dir.mkdir(exist_ok=True)
        static_dir.mkdir(exist_ok=True)
        
        templates = Jinja2Templates(directory=str(templates_dir))
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        
        @app.get("/", response_class=HTMLResponse)
        async def dashboard_home(request: Request):
            """Main dashboard page"""
            return templates.TemplateResponse("dashboard.html", {"request": request})
        
        @app.get("/api/summary")
        async def get_summary():
            """Get current usage summary"""
            summary = self.calculator.get_usage_summary()
            return JSONResponse(summary)
        
        @app.get("/api/trends")
        async def get_trends(days: int = 30):
            """Get cost trends"""
            trends = self.calculator.get_cost_trends(days)
            return JSONResponse(trends)
        
        @app.get("/api/recommendations")
        async def get_recommendations():
            """Get optimization recommendations"""
            recommendations = self.calculator.generate_cost_optimization_recommendations()
            return JSONResponse([{
                'category': r.category,
                'priority': r.priority,
                'description': r.description,
                'potential_savings': float(r.potential_savings),
                'implementation_effort': r.implementation_effort,
                'estimated_impact': r.estimated_impact,
                'specific_actions': r.specific_actions
            } for r in recommendations])
        
        @app.get("/api/model-comparison")
        async def get_model_comparison():
            """Get model cost comparison"""
            comparison = self.calculator.get_model_comparison()
            return JSONResponse(comparison)
        
        @app.get("/api/prediction")
        async def get_monthly_prediction(days: int = 7):
            """Get monthly cost prediction"""
            prediction = self.calculator.predict_monthly_cost(days)
            return JSONResponse(prediction)
        
        @app.post("/api/alerts")
        async def create_alert(alert_data: dict):
            """Create cost alert"""
            alert_id = self.calculator.create_cost_alert(
                alert_type=alert_data['type'],
                threshold_amount=alert_data['threshold'],
                notification_method=alert_data.get('method', 'console')
            )
            return {"alert_id": alert_id, "status": "created"}
        
        @app.get("/api/alerts")
        async def get_alerts():
            """Get active alerts"""
            return JSONResponse([{
                'alert_id': alert.alert_id,
                'alert_type': alert.alert_type,
                'threshold_amount': float(alert.threshold_amount),
                'notification_method': alert.notification_method,
                'enabled': alert.enabled,
                'created_at': alert.created_at.isoformat(),
                'last_triggered': alert.last_triggered.isoformat() if alert.last_triggered else None
            } for alert in self.calculator.alerts])
        
        @app.delete("/api/alerts/{alert_id}")
        async def delete_alert(alert_id: str):
            """Delete cost alert"""
            # Remove from calculator alerts list
            self.calculator.alerts = [a for a in self.calculator.alerts if a.alert_id != alert_id]
            
            # Remove from database
            with sqlite3.connect(self.calculator.db_path) as conn:
                conn.execute('UPDATE cost_alerts SET enabled = 0 WHERE alert_id = ?', (alert_id,))
            
            return {"status": "deleted"}
        
        @app.get("/api/live-stats")
        async def get_live_stats():
            """Get current live statistics"""
            today_summary = self.calculator.get_usage_summary(
                start_date=date.today(),
                end_date=date.today()
            )
            
            # Get recent activity (last hour)
            with sqlite3.connect(self.calculator.db_path) as conn:
                cursor = conn.execute('''
                    SELECT COUNT(*) as recent_requests,
                           SUM(total_cost) as recent_cost,
                           AVG(total_tokens) as avg_tokens
                    FROM token_usage 
                    WHERE timestamp > datetime('now', '-1 hour')
                ''')
                recent_stats = cursor.fetchone()
            
            return JSONResponse({
                'today': today_summary['totals'],
                'recent_hour': {
                    'requests': recent_stats[0] or 0,
                    'cost': float(recent_stats[1] or 0),
                    'avg_tokens': recent_stats[2] or 0
                },
                'timestamp': datetime.now().isoformat()
            })
        
        @app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates"""
            await websocket.accept()
            self.active_connections.append(websocket)
            
            try:
                while True:
                    # Keep connection alive
                    await asyncio.sleep(10)
            except Exception:
                pass
            finally:
                if websocket in self.active_connections:
                    self.active_connections.remove(websocket)
        
        @app.get("/api/export")
        async def export_data(
            format: str = "csv",
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
            background_tasks: BackgroundTasks = None
        ):
            """Export usage data"""
            
            start = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
            end = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
            
            filename = f"token_usage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
            filepath = self.calculator.financial_dir / filename
            
            try:
                self.calculator.export_usage_data(str(filepath), format, start, end)
                return {"status": "success", "filename": filename, "path": str(filepath)}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        return app
    
    async def _monitor_usage(self):
        """Background task to monitor usage and send real-time updates"""
        
        while self.monitoring:
            try:
                if self.active_connections:
                    # Get live stats
                    live_stats = await self._get_live_update()
                    
                    # Send to all connected clients
                    disconnected = []
                    for connection in self.active_connections:
                        try:
                            await connection.send_json(live_stats)
                        except Exception:
                            disconnected.append(connection)
                    
                    # Remove disconnected clients
                    for conn in disconnected:
                        if conn in self.active_connections:
                            self.active_connections.remove(conn)
                
                await asyncio.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                print(f"Monitor error: {e}")
                await asyncio.sleep(30)
    
    async def _get_live_update(self) -> Dict[str, Any]:
        """Get data for live updates"""
        
        # Today's stats
        today_summary = self.calculator.get_usage_summary(
            start_date=date.today(),
            end_date=date.today()
        )
        
        # Recent activity (last 10 minutes)
        with sqlite3.connect(self.calculator.db_path) as conn:
            cursor = conn.execute('''
                SELECT 
                    COUNT(*) as requests,
                    SUM(total_cost) as cost,
                    SUM(total_tokens) as tokens,
                    agent_name,
                    COUNT(*) as agent_requests
                FROM token_usage 
                WHERE timestamp > datetime('now', '-10 minutes')
                GROUP BY agent_name
                ORDER BY agent_requests DESC
            ''')
            
            recent_activity = []
            total_recent_requests = 0
            total_recent_cost = 0.0
            total_recent_tokens = 0
            
            for row in cursor:
                if row[0] > 0:  # If there are requests
                    total_recent_requests = row[0]
                    total_recent_cost = float(row[1] or 0)
                    total_recent_tokens = row[2] or 0
                    
                    if row[3]:  # If agent name exists
                        recent_activity.append({
                            'agent': row[3],
                            'requests': row[4]
                        })
        
        return {
            'type': 'live_update',
            'timestamp': datetime.now().isoformat(),
            'today_total': today_summary['totals'],
            'recent_10min': {
                'requests': total_recent_requests,
                'cost': total_recent_cost,
                'tokens': total_recent_tokens,
                'active_agents': recent_activity
            }
        }
    
    def run(self, host: str = "localhost", port: int = 8080, debug: bool = False):
        """Run the dashboard server"""
        
        # Create dashboard template if it doesn't exist
        self._create_dashboard_template()
        self._create_dashboard_assets()
        
        print(f"Starting Claude Token Dashboard on http://{host}:{port}")
        uvicorn.run(self.app, host=host, port=port, log_level="info" if debug else "warning")
    
    def _create_dashboard_template(self):
        """Create the main dashboard HTML template"""
        
        template_path = Path(__file__).parent / "templates" / "dashboard.html"
        template_path.parent.mkdir(exist_ok=True)
        
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claude Token Usage Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/date-fns@2.29.3/index.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            color: #333;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            margin: 0;
            font-size: 1.8rem;
            font-weight: 600;
        }
        
        .header .subtitle {
            opacity: 0.9;
            margin-top: 0.5rem;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border-left: 4px solid #667eea;
            transition: transform 0.2s;
        }
        
        .stat-card:hover {
            transform: translateY(-2px);
        }
        
        .stat-card .icon {
            font-size: 2rem;
            color: #667eea;
            margin-bottom: 1rem;
        }
        
        .stat-card .value {
            font-size: 2rem;
            font-weight: bold;
            color: #2d3748;
            margin-bottom: 0.5rem;
        }
        
        .stat-card .label {
            color: #718096;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .chart-container {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin-bottom: 2rem;
        }
        
        .chart-container h3 {
            margin-bottom: 1rem;
            color: #2d3748;
        }
        
        .tabs {
            display: flex;
            border-bottom: 1px solid #e2e8f0;
            margin-bottom: 1rem;
        }
        
        .tab {
            padding: 0.75rem 1.5rem;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
        }
        
        .tab.active {
            border-bottom-color: #667eea;
            color: #667eea;
            font-weight: 500;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .recommendations {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin-bottom: 2rem;
        }
        
        .recommendation {
            padding: 1rem;
            margin-bottom: 1rem;
            border-radius: 8px;
            border-left: 4px solid;
        }
        
        .recommendation.high { 
            border-left-color: #e53e3e;
            background: #fed7d7;
        }
        
        .recommendation.medium { 
            border-left-color: #dd6b20;
            background: #feebc8;
        }
        
        .recommendation.low { 
            border-left-color: #38a169;
            background: #c6f6d5;
        }
        
        .recommendation h4 {
            margin-bottom: 0.5rem;
            text-transform: capitalize;
        }
        
        .live-indicator {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: #38a169;
            font-size: 0.9rem;
        }
        
        .live-dot {
            width: 8px;
            height: 8px;
            background: #38a169;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .alert-section {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        .alert-form {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr auto;
            gap: 1rem;
            align-items: end;
            margin-bottom: 1rem;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 0.25rem;
            font-weight: 500;
            color: #4a5568;
        }
        
        .form-group input, .form-group select {
            width: 100%;
            padding: 0.5rem;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            font-size: 0.9rem;
        }
        
        .btn {
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5a6fd8;
        }
        
        .btn-danger {
            background: #e53e3e;
            color: white;
            font-size: 0.8rem;
            padding: 0.25rem 0.5rem;
        }
        
        .alert-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem;
            background: #f7fafc;
            border-radius: 6px;
            margin-bottom: 0.5rem;
        }
        
        .model-comparison {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
        }
        
        .model-card {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid #e9ecef;
        }
        
        .model-card h4 {
            margin-bottom: 0.5rem;
            color: #495057;
        }
        
        .scenario-costs {
            margin-top: 0.5rem;
        }
        
        .scenario-costs div {
            display: flex;
            justify-content: space-between;
            padding: 0.25rem 0;
            font-size: 0.9rem;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .alert-form {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1><i class="fas fa-chart-line"></i> Claude Token Usage Dashboard</h1>
        <div class="subtitle">
            <span class="live-indicator">
                <span class="live-dot"></span>
                Live Monitoring
            </span>
            | Real-time cost tracking and optimization
        </div>
    </div>

    <div class="container">
        <!-- Stats Overview -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="icon"><i class="fas fa-dollar-sign"></i></div>
                <div class="value" id="total-cost">$0.00</div>
                <div class="label">Total Cost (30 days)</div>
            </div>
            <div class="stat-card">
                <div class="icon"><i class="fas fa-coins"></i></div>
                <div class="value" id="total-tokens">0</div>
                <div class="label">Total Tokens</div>
            </div>
            <div class="stat-card">
                <div class="icon"><i class="fas fa-robot"></i></div>
                <div class="value" id="total-requests">0</div>
                <div class="label">API Requests</div>
            </div>
            <div class="stat-card">
                <div class="icon"><i class="fas fa-clock"></i></div>
                <div class="value" id="avg-cost">$0.0000</div>
                <div class="label">Avg Cost/Request</div>
            </div>
            <div class="stat-card">
                <div class="icon"><i class="fas fa-calendar-day"></i></div>
                <div class="value" id="today-cost">$0.00</div>
                <div class="label">Today's Cost</div>
            </div>
            <div class="stat-card">
                <div class="icon"><i class="fas fa-trending-up"></i></div>
                <div class="value" id="monthly-projection">$0.00</div>
                <div class="label">Monthly Projection</div>
            </div>
        </div>

        <!-- Charts Section -->
        <div class="chart-container">
            <div class="tabs">
                <div class="tab active" onclick="showTab('trends')">Cost Trends</div>
                <div class="tab" onclick="showTab('agents')">Agent Breakdown</div>
                <div class="tab" onclick="showTab('models')">Model Comparison</div>
            </div>
            
            <div id="trends" class="tab-content active">
                <h3>Daily Cost Trends</h3>
                <canvas id="trendsChart" width="400" height="200"></canvas>
            </div>
            
            <div id="agents" class="tab-content">
                <h3>Cost by Agent</h3>
                <canvas id="agentsChart" width="400" height="200"></canvas>
            </div>
            
            <div id="models" class="tab-content">
                <h3>Model Cost Comparison</h3>
                <div class="model-comparison" id="model-comparison"></div>
            </div>
        </div>

        <!-- Recommendations -->
        <div class="recommendations">
            <h3><i class="fas fa-lightbulb"></i> Cost Optimization Recommendations</h3>
            <div id="recommendations-list">
                Loading recommendations...
            </div>
        </div>

        <!-- Alerts Management -->
        <div class="alert-section">
            <h3><i class="fas fa-bell"></i> Cost Alerts</h3>
            
            <div class="alert-form">
                <div class="form-group">
                    <label for="alert-type">Alert Type</label>
                    <select id="alert-type">
                        <option value="daily">Daily</option>
                        <option value="weekly">Weekly</option>
                        <option value="monthly">Monthly</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="alert-threshold">Threshold ($)</label>
                    <input type="number" id="alert-threshold" step="0.01" placeholder="10.00">
                </div>
                <div class="form-group">
                    <label for="alert-method">Notification</label>
                    <select id="alert-method">
                        <option value="console">Console</option>
                        <option value="email">Email</option>
                        <option value="webhook">Webhook</option>
                    </select>
                </div>
                <div>
                    <button class="btn btn-primary" onclick="createAlert()">
                        <i class="fas fa-plus"></i> Add Alert
                    </button>
                </div>
            </div>
            
            <div id="alerts-list">
                Loading alerts...
            </div>
        </div>
    </div>

    <script>
        let socket = null;
        let trendsChart = null;
        let agentsChart = null;

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            initializeWebSocket();
            loadInitialData();
            setInterval(loadLiveStats, 10000); // Update every 10 seconds
        });

        function initializeWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            socket = new WebSocket(wsUrl);
            
            socket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                if (data.type === 'live_update') {
                    updateLiveStats(data);
                }
            };
            
            socket.onclose = function() {
                console.log('WebSocket disconnected, reconnecting...');
                setTimeout(initializeWebSocket, 5000);
            };
        }

        async function loadInitialData() {
            try {
                // Load summary
                const summary = await fetch('/api/summary').then(r => r.json());
                updateSummaryStats(summary);
                
                // Load trends
                const trends = await fetch('/api/trends').then(r => r.json());
                updateTrendsChart(trends);
                
                // Load recommendations
                const recommendations = await fetch('/api/recommendations').then(r => r.json());
                updateRecommendations(recommendations);
                
                // Load alerts
                const alerts = await fetch('/api/alerts').then(r => r.json());
                updateAlertsList(alerts);
                
                // Load model comparison
                const comparison = await fetch('/api/model-comparison').then(r => r.json());
                updateModelComparison(comparison);
                
                // Load prediction
                const prediction = await fetch('/api/prediction').then(r => r.json());
                document.getElementById('monthly-projection').textContent = `$${prediction.monthly_projection.toFixed(2)}`;
                
            } catch (error) {
                console.error('Error loading initial data:', error);
            }
        }

        async function loadLiveStats() {
            try {
                const stats = await fetch('/api/live-stats').then(r => r.json());
                document.getElementById('today-cost').textContent = `$${stats.today.cost.toFixed(2)}`;
            } catch (error) {
                console.error('Error loading live stats:', error);
            }
        }

        function updateSummaryStats(summary) {
            document.getElementById('total-cost').textContent = `$${summary.totals.cost.toFixed(2)}`;
            document.getElementById('total-tokens').textContent = summary.totals.tokens.toLocaleString();
            document.getElementById('total-requests').textContent = summary.totals.requests.toLocaleString();
            document.getElementById('avg-cost').textContent = `$${summary.totals.avg_cost_per_request.toFixed(4)}`;
        }

        function updateLiveStats(data) {
            if (data.recent_10min) {
                // Update with recent activity data
                console.log('Recent activity:', data.recent_10min);
            }
        }

        function updateTrendsChart(trends) {
            const ctx = document.getElementById('trendsChart').getContext('2d');
            
            if (trendsChart) {
                trendsChart.destroy();
            }
            
            trendsChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: trends.daily_trends.map(d => d.date),
                    datasets: [{
                        label: 'Daily Cost ($)',
                        data: trends.daily_trends.map(d => d.cost),
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return '$' + value.toFixed(2);
                                }
                            }
                        }
                    }
                }
            });
        }

        function updateRecommendations(recommendations) {
            const container = document.getElementById('recommendations-list');
            
            if (recommendations.length === 0) {
                container.innerHTML = '<p>No recommendations available. Your usage appears optimized!</p>';
                return;
            }
            
            container.innerHTML = recommendations.map(rec => `
                <div class="recommendation ${rec.priority}">
                    <h4>${rec.category.replace('_', ' ')} - ${rec.priority.toUpperCase()} Priority</h4>
                    <p><strong>Issue:</strong> ${rec.description}</p>
                    <p><strong>Potential Savings:</strong> $${rec.potential_savings.toFixed(2)}</p>
                    <p><strong>Implementation:</strong> ${rec.implementation_effort} | <strong>Impact:</strong> ${rec.estimated_impact}</p>
                    <ul>
                        ${rec.specific_actions.slice(0, 3).map(action => `<li>${action}</li>`).join('')}
                    </ul>
                </div>
            `).join('');
        }

        function updateAlertsList(alerts) {
            const container = document.getElementById('alerts-list');
            
            if (alerts.length === 0) {
                container.innerHTML = '<p>No active alerts configured.</p>';
                return;
            }
            
            container.innerHTML = alerts.map(alert => `
                <div class="alert-item">
                    <div>
                        <strong>${alert.alert_type.toUpperCase()}</strong> - $${alert.threshold_amount} 
                        (${alert.notification_method})
                        ${alert.last_triggered ? `<br><small>Last triggered: ${new Date(alert.last_triggered).toLocaleString()}</small>` : ''}
                    </div>
                    <button class="btn btn-danger" onclick="deleteAlert('${alert.alert_id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `).join('');
        }

        function updateModelComparison(comparison) {
            const container = document.getElementById('model-comparison');
            
            container.innerHTML = Object.entries(comparison).map(([modelName, data]) => `
                <div class="model-card">
                    <h4>${data.pricing.description}</h4>
                    <div><strong>Input:</strong> $${data.pricing.input_cost_per_million}/M tokens</div>
                    <div><strong>Output:</strong> $${data.pricing.output_cost_per_million}/M tokens</div>
                    <div class="scenario-costs">
                        <strong>Scenario Costs:</strong>
                        ${Object.entries(data.scenario_costs).map(([scenario, cost]) => 
                            `<div><span>${scenario.replace('_', ' ')}:</span><span>$${cost.toFixed(4)}</span></div>`
                        ).join('')}
                    </div>
                </div>
            `).join('');
        }

        async function createAlert() {
            const alertType = document.getElementById('alert-type').value;
            const threshold = parseFloat(document.getElementById('alert-threshold').value);
            const method = document.getElementById('alert-method').value;
            
            if (!threshold || threshold <= 0) {
                alert('Please enter a valid threshold amount');
                return;
            }
            
            try {
                const response = await fetch('/api/alerts', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        type: alertType,
                        threshold: threshold,
                        method: method
                    })
                });
                
                if (response.ok) {
                    document.getElementById('alert-threshold').value = '';
                    const alerts = await fetch('/api/alerts').then(r => r.json());
                    updateAlertsList(alerts);
                }
            } catch (error) {
                console.error('Error creating alert:', error);
                alert('Failed to create alert');
            }
        }

        async function deleteAlert(alertId) {
            if (!confirm('Are you sure you want to delete this alert?')) {
                return;
            }
            
            try {
                const response = await fetch(`/api/alerts/${alertId}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    const alerts = await fetch('/api/alerts').then(r => r.json());
                    updateAlertsList(alerts);
                }
            } catch (error) {
                console.error('Error deleting alert:', error);
                alert('Failed to delete alert');
            }
        }

        function showTab(tabName) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Remove active class from all tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab content
            document.getElementById(tabName).classList.add('active');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
            
            // Load specific data for the tab
            if (tabName === 'agents') {
                loadAgentsChart();
            }
        }

        async function loadAgentsChart() {
            try {
                const summary = await fetch('/api/summary').then(r => r.json());
                const ctx = document.getElementById('agentsChart').getContext('2d');
                
                if (agentsChart) {
                    agentsChart.destroy();
                }
                
                const topAgents = summary.by_agent.slice(0, 10);
                
                agentsChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: topAgents.map(a => a.agent_name),
                        datasets: [{
                            data: topAgents.map(a => a.cost),
                            backgroundColor: [
                                '#667eea', '#764ba2', '#f093fb', '#f5576c',
                                '#4facfe', '#43e97b', '#fa709a', '#fee140',
                                '#a8edea', '#fed6e3'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'bottom'
                            }
                        }
                    }
                });
            } catch (error) {
                console.error('Error loading agents chart:', error);
            }
        }
    </script>
</body>
</html>'''
        
        with open(template_path, 'w') as f:
            f.write(html_content)
    
    def _create_dashboard_assets(self):
        """Create additional dashboard assets if needed"""
        
        static_dir = Path(__file__).parent / "static"
        static_dir.mkdir(exist_ok=True)
        
        # Create a simple CSS file for additional styles
        css_content = """
        /* Additional dashboard styles */
        .loading {
            text-align: center;
            padding: 2rem;
            color: #718096;
        }
        
        .error {
            background: #fed7d7;
            color: #c53030;
            padding: 1rem;
            border-radius: 6px;
            margin: 1rem 0;
        }
        
        .success {
            background: #c6f6d5;
            color: #22543d;
            padding: 1rem;
            border-radius: 6px;
            margin: 1rem 0;
        }
        """
        
        with open(static_dir / "dashboard.css", 'w') as f:
            f.write(css_content)

def main():
    """Main entry point for dashboard"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Claude Token Usage Dashboard')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Initialize calculator
    calculator = TokenCostCalculator()
    
    # Create and run dashboard
    dashboard = TokenDashboard(calculator)
    dashboard.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == '__main__':
    main()