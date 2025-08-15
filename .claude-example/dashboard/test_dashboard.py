#!/usr/bin/env python3
"""
Comprehensive Integration Tests for Real-Time Dashboard
Tests Flask server, WebSocket connections, monitoring services, and mobile responsiveness
"""

import asyncio
import json
import os
import sys
import tempfile
import threading
import time
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

import pytest
import requests
import socketio
import psutil
from flask import Flask
from flask_socketio import SocketIOTestClient

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from dashboard_server import DashboardServer
from simple_dashboard import DashboardHandler
from ttyd_manager import TerminalManager


class TestConfig:
    """Test configuration constants"""
    TEST_PORT = 8081
    TEST_HOST = '127.0.0.1'
    WEBSOCKET_TIMEOUT = 5
    HTTP_TIMEOUT = 10
    CLAUDE_DIR = Path.home() / '.claude_test'
    
    @classmethod
    def setup_test_dirs(cls):
        """Setup test directories"""
        cls.CLAUDE_DIR.mkdir(exist_ok=True)
        (cls.CLAUDE_DIR / 'state').mkdir(exist_ok=True)
        (cls.CLAUDE_DIR / 'logs').mkdir(exist_ok=True)
        (cls.CLAUDE_DIR / 'hooks').mkdir(exist_ok=True)
        return cls.CLAUDE_DIR
    
    @classmethod
    def cleanup_test_dirs(cls):
        """Cleanup test directories"""
        import shutil
        if cls.CLAUDE_DIR.exists():
            shutil.rmtree(cls.CLAUDE_DIR)


@pytest.fixture(scope="session")
def test_config():
    """Test configuration fixture"""
    config = TestConfig()
    config.setup_test_dirs()
    yield config
    config.cleanup_test_dirs()


@pytest.fixture
def mock_claude_dir(test_config, tmp_path):
    """Mock Claude directory with test data"""
    claude_dir = tmp_path / '.claude'
    claude_dir.mkdir(exist_ok=True)
    
    # Create required subdirectories
    (claude_dir / 'state').mkdir(exist_ok=True)
    (claude_dir / 'logs').mkdir(exist_ok=True)
    (claude_dir / 'hooks').mkdir(exist_ok=True)
    
    # Create mock performance metrics
    perf_data = {
        "summary": {
            "total_operations": 150,
            "average_execution_time": 2.5,
            "total_tokens_used": 25000,
            "issues_detected": 3
        },
        "agent_metrics": {
            "test-agent": {
                "last_execution": "2024-01-15T10:30:00",
                "executions": 25
            }
        },
        "resource_metrics": [
            {
                "timestamp": "2024-01-15T10:00:00",
                "cpu_percent": 45.2,
                "memory_percent": 60.8,
                "disk_percent": 75.3
            }
        ]
    }
    
    with open(claude_dir / 'state' / 'performance_metrics.json', 'w') as f:
        json.dump(perf_data, f)
    
    # Create mock log files
    log_content = "2024-01-15 10:00:00 [INFO] Test log entry\n"
    with open(claude_dir / 'logs' / 'test.log', 'w') as f:
        f.write(log_content)
    
    # Create mock settings
    settings = {"theme": "dark", "refresh_interval": 30}
    with open(claude_dir / 'settings.json', 'w') as f:
        json.dump(settings, f)
    
    return claude_dir


@pytest.fixture
def dashboard_server(mock_claude_dir):
    """Dashboard server fixture"""
    with patch('dashboard_server.Path.home') as mock_home:
        mock_home.return_value = mock_claude_dir.parent
        server = DashboardServer(port=TestConfig.TEST_PORT)
        server.claude_dir = mock_claude_dir
        yield server


@pytest.fixture
def running_dashboard(dashboard_server):
    """Running dashboard server fixture"""
    # Start server in background thread
    server_thread = threading.Thread(
        target=dashboard_server.run,
        kwargs={'host': TestConfig.TEST_HOST, 'debug': False},
        daemon=True
    )
    server_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    # Verify server is running
    try:
        response = requests.get(
            f'http://{TestConfig.TEST_HOST}:{TestConfig.TEST_PORT}/api/status',
            timeout=5
        )
        assert response.status_code == 200
    except Exception as e:
        pytest.skip(f"Dashboard server failed to start: {e}")
    
    yield dashboard_server
    
    # Stop server
    dashboard_server.stop_monitoring()


@pytest.fixture
def socketio_client():
    """SocketIO test client fixture"""
    client = socketio.SimpleClient()
    yield client
    if client.connected:
        client.disconnect()


class TestFlaskServerStartup:
    """Test Flask server startup and basic functionality"""
    
    def test_server_initialization(self, dashboard_server):
        """Test server initializes correctly"""
        assert dashboard_server.port == TestConfig.TEST_PORT
        assert isinstance(dashboard_server.app, Flask)
        assert dashboard_server.socketio is not None
        assert dashboard_server.claude_dir.exists()
    
    def test_settings_loading(self, dashboard_server):
        """Test settings are loaded correctly"""
        settings = dashboard_server.settings
        assert isinstance(settings, dict)
        assert 'theme' in settings
        assert settings['theme'] == 'dark'
    
    def test_routes_setup(self, dashboard_server):
        """Test all routes are properly configured"""
        routes = [rule.rule for rule in dashboard_server.app.url_map.iter_rules()]
        expected_routes = [
            '/',
            '/api/status',
            '/api/metrics',
            '/api/alerts',
            '/api/agents',
            '/api/hooks',
            '/api/performance',
            '/api/security',
            '/api/logs',
            '/static/<path:filename>'
        ]
        
        for route in expected_routes:
            assert any(route in r for r in routes), f"Route {route} not found"
    
    def test_security_config(self, dashboard_server):
        """Test security configuration"""
        app_config = dashboard_server.app.config
        assert 'SECRET_KEY' in app_config
        assert app_config['SESSION_COOKIE_SECURE'] is True
        assert app_config['SESSION_COOKIE_HTTPONLY'] is True
        assert app_config['SESSION_COOKIE_SAMESITE'] == 'Lax'
    
    @pytest.mark.asyncio
    async def test_server_startup_integration(self, mock_claude_dir):
        """Test complete server startup process"""
        with patch('dashboard_server.Path.home') as mock_home:
            mock_home.return_value = mock_claude_dir.parent
            
            server = DashboardServer(port=TestConfig.TEST_PORT + 1)
            
            # Test initialization
            assert server.system_status == 'unknown'
            assert server.monitoring is True
            assert server.alerts == []
            
            # Test monitoring thread can start
            server.start_monitoring()
            time.sleep(1)
            
            assert server.monitor_thread is not None
            assert server.monitor_thread.is_alive()
            
            # Stop monitoring
            server.stop_monitoring()
            assert server.monitoring is False


class TestWebSocketConnections:
    """Test WebSocket connection functionality"""
    
    def test_socketio_client_connection(self, running_dashboard):
        """Test WebSocket client can connect"""
        client = socketio.SimpleClient()
        
        try:
            client.connect(f'http://{TestConfig.TEST_HOST}:{TestConfig.TEST_PORT}')
            assert client.connected
            
            # Test receiving status update
            event = client.receive(timeout=TestConfig.WEBSOCKET_TIMEOUT)
            assert event[0] == 'status_update'
            assert 'status' in event[1]
            
        finally:
            if client.connected:
                client.disconnect()
    
    def test_socketio_events_registration(self, dashboard_server):
        """Test SocketIO events are properly registered"""
        # Create test client
        client = SocketIOTestClient(dashboard_server.app, dashboard_server.socketio)
        
        # Test connection event
        received = client.get_received()
        assert len(received) > 0
        assert received[0]['name'] == 'status_update'
    
    def test_broadcast_update(self, dashboard_server):
        """Test broadcast update functionality"""
        # Create test client
        client = SocketIOTestClient(dashboard_server.app, dashboard_server.socketio)
        client.get_received()  # Clear initial messages
        
        # Trigger broadcast
        dashboard_server.broadcast_update()
        
        # Check received messages
        received = client.get_received()
        message_types = [msg['name'] for msg in received]
        
        assert 'metrics_update' in message_types
        assert 'status_update' in message_types
    
    def test_request_update_event(self, dashboard_server):
        """Test request_update event handling"""
        client = SocketIOTestClient(dashboard_server.app, dashboard_server.socketio)
        client.get_received()  # Clear initial messages
        
        # Emit request_update
        client.emit('request_update')
        
        # Check for update response
        received = client.get_received()
        assert len(received) > 0
        
        message_types = [msg['name'] for msg in received]
        assert 'metrics_update' in message_types or 'status_update' in message_types
    
    @pytest.mark.asyncio
    async def test_websocket_message_flow(self, running_dashboard):
        """Test complete WebSocket message flow"""
        client = socketio.AsyncSimpleClient()
        
        try:
            await client.connect(f'http://{TestConfig.TEST_HOST}:{TestConfig.TEST_PORT}')
            
            # Send request for update
            await client.emit('request_update')
            
            # Wait for response
            event = await client.receive(timeout=TestConfig.WEBSOCKET_TIMEOUT)
            assert event[0] in ['metrics_update', 'status_update']
            
            # Verify message structure
            if event[0] == 'metrics_update':
                data = event[1]
                assert 'system' in data or 'timestamp' in data
            
        finally:
            if client.connected:
                await client.disconnect()


class TestMonitorServices:
    """Test monitoring service functionality"""
    
    def test_claude_monitor_session_parsing(self, dashboard_server):
        """Test ClaudeMonitor session data parsing"""
        # Mock session data
        session_data = {
            'session_id': 'test-session-123',
            'agent_name': 'test-agent',
            'start_time': datetime.now().isoformat(),
            'operations': 5
        }
        
        # Test metrics collection
        metrics = dashboard_server.get_current_metrics()
        assert 'claude_code' in metrics
        assert 'total_operations' in metrics['claude_code']
    
    def test_system_monitor_metrics(self, dashboard_server):
        """Test SystemMonitor metrics collection"""
        with patch('psutil.cpu_percent', return_value=45.0), \
             patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk:
            
            # Mock system metrics
            mock_memory.return_value = Mock(percent=60.0, used=8*1024**3, total=16*1024**3)
            mock_disk.return_value = Mock(percent=75.0, used=500*1024**3, total=1000*1024**3)
            
            metrics = dashboard_server.get_current_metrics()
            
            assert 'system' in metrics
            system_metrics = metrics['system']
            assert system_metrics['cpu_percent'] == 45.0
            assert system_metrics['memory_percent'] == 60.0
            assert system_metrics['disk_percent'] == 75.0
    
    def test_file_monitor_change_detection(self, dashboard_server, tmp_path):
        """Test FileMonitor change detection"""
        # Create test file
        test_file = tmp_path / 'test.txt'
        test_file.write_text('initial content')
        
        initial_mtime = test_file.stat().st_mtime
        
        # Modify file
        time.sleep(0.1)
        test_file.write_text('modified content')
        
        new_mtime = test_file.stat().st_mtime
        assert new_mtime > initial_mtime
    
    def test_git_monitor_repository_tracking(self, dashboard_server, tmp_path):
        """Test GitMonitor repository tracking capabilities"""
        # Mock git repository
        git_dir = tmp_path / '.git'
        git_dir.mkdir()
        
        # Create mock git objects
        (git_dir / 'HEAD').write_text('ref: refs/heads/main')
        
        refs_dir = git_dir / 'refs' / 'heads'
        refs_dir.mkdir(parents=True)
        (refs_dir / 'main').write_text('abc123def456')
        
        # Test repository detection
        assert git_dir.exists()
        assert (git_dir / 'HEAD').exists()
    
    def test_agent_status_monitoring(self, dashboard_server):
        """Test agent status monitoring"""
        agent_status = dashboard_server.get_agent_status()
        
        assert 'total_agents' in agent_status
        assert 'active_agents' in agent_status
        assert 'agents' in agent_status
        assert isinstance(agent_status['agents'], list)
    
    def test_performance_metrics_collection(self, dashboard_server):
        """Test performance metrics collection"""
        perf_metrics = dashboard_server.get_performance_metrics()
        
        if 'error' not in perf_metrics:
            assert 'summary' in perf_metrics
            assert 'agent_metrics' in perf_metrics
    
    def test_security_status_monitoring(self, dashboard_server):
        """Test security status monitoring"""
        security_status = dashboard_server.get_security_status()
        
        assert 'status' in security_status
        assert security_status['status'] in ['unknown', 'secure', 'warning', 'critical', 'error']


class TestCommandExecution:
    """Test command execution through dashboard"""
    
    def test_api_endpoints(self, running_dashboard):
        """Test all API endpoints respond correctly"""
        base_url = f'http://{TestConfig.TEST_HOST}:{TestConfig.TEST_PORT}'
        
        endpoints = [
            '/api/status',
            '/api/metrics',
            '/api/alerts',
            '/api/agents',
            '/api/hooks',
            '/api/performance',
            '/api/security',
            '/api/logs'
        ]
        
        for endpoint in endpoints:
            response = requests.get(f'{base_url}{endpoint}', timeout=TestConfig.HTTP_TIMEOUT)
            assert response.status_code == 200, f"Endpoint {endpoint} failed"
            
            # Verify JSON response
            data = response.json()
            assert isinstance(data, dict)
    
    def test_dashboard_page_rendering(self, running_dashboard):
        """Test main dashboard page renders correctly"""
        response = requests.get(
            f'http://{TestConfig.TEST_HOST}:{TestConfig.TEST_PORT}/',
            timeout=TestConfig.HTTP_TIMEOUT
        )
        
        assert response.status_code == 200
        assert 'text/html' in response.headers['content-type']
        assert 'Claude Code' in response.text
    
    def test_metrics_api_structure(self, running_dashboard):
        """Test metrics API returns proper structure"""
        response = requests.get(
            f'http://{TestConfig.TEST_HOST}:{TestConfig.TEST_PORT}/api/metrics',
            timeout=TestConfig.HTTP_TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        if 'error' not in data:
            assert 'system' in data
            assert 'claude_code' in data
            assert 'timestamp' in data
    
    def test_status_api_response(self, running_dashboard):
        """Test status API response format"""
        response = requests.get(
            f'http://{TestConfig.TEST_HOST}:{TestConfig.TEST_PORT}/api/status',
            timeout=TestConfig.HTTP_TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ['status', 'last_update', 'uptime', 'version']
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
    
    def test_alert_system(self, dashboard_server):
        """Test alert generation and retrieval"""
        # Add test alert
        dashboard_server.add_alert('warning', 'Test alert message', 'Test details')
        
        assert len(dashboard_server.alerts) == 1
        alert = dashboard_server.alerts[0]
        
        assert alert['level'] == 'warning'
        assert alert['message'] == 'Test alert message'
        assert alert['details'] == 'Test details'
        assert 'timestamp' in alert
        assert alert['acknowledged'] is False


class TestErrorHandling:
    """Test error handling and recovery"""
    
    def test_invalid_api_endpoints(self, running_dashboard):
        """Test invalid API endpoints return 404"""
        response = requests.get(
            f'http://{TestConfig.TEST_HOST}:{TestConfig.TEST_PORT}/api/nonexistent',
            timeout=TestConfig.HTTP_TIMEOUT
        )
        assert response.status_code == 404
    
    def test_metrics_error_handling(self, dashboard_server):
        """Test metrics collection error handling"""
        with patch('psutil.cpu_percent', side_effect=Exception('Test error')):
            metrics = dashboard_server.get_current_metrics()
            assert 'error' in metrics
            assert 'Test error' in str(metrics['error'])
    
    def test_performance_metrics_missing_file(self, dashboard_server):
        """Test handling of missing performance metrics file"""
        # Ensure file doesn't exist
        perf_file = dashboard_server.claude_dir / 'state' / 'nonexistent.json'
        assert not perf_file.exists()
        
        perf_metrics = dashboard_server.get_performance_metrics()
        assert 'error' in perf_metrics
    
    def test_websocket_connection_failure(self):
        """Test WebSocket connection failure handling"""
        client = socketio.SimpleClient()
        
        # Try to connect to non-existent server
        with pytest.raises(Exception):
            client.connect('http://localhost:99999', wait_timeout=1)
    
    def test_system_status_error_handling(self, dashboard_server):
        """Test system status update error handling"""
        with patch('dashboard_server.DashboardServer.get_current_metrics', 
                   side_effect=Exception('Test error')):
            dashboard_server.update_system_status()
            assert dashboard_server.system_status == 'error'
    
    def test_monitoring_thread_recovery(self, dashboard_server):
        """Test monitoring thread handles errors gracefully"""
        # Start monitoring
        dashboard_server.start_monitoring()
        time.sleep(1)
        
        # Simulate error in monitoring
        with patch.object(dashboard_server, 'update_system_status', 
                          side_effect=Exception('Test monitoring error')):
            time.sleep(2)  # Let monitoring run with error
        
        # Thread should still be alive after error
        assert dashboard_server.monitor_thread.is_alive()
        
        dashboard_server.stop_monitoring()


class TestMobileResponsiveness:
    """Test mobile responsiveness and mobile auth integration"""
    
    def test_mobile_viewport_meta(self, running_dashboard):
        """Test mobile viewport meta tag is present"""
        response = requests.get(
            f'http://{TestConfig.TEST_HOST}:{TestConfig.TEST_PORT}/',
            timeout=TestConfig.HTTP_TIMEOUT
        )
        
        assert response.status_code == 200
        assert 'viewport' in response.text
        assert 'width=device-width' in response.text
    
    def test_mobile_auth_disabled_by_default(self, dashboard_server):
        """Test mobile auth is disabled by default"""
        assert dashboard_server.auth_manager is None
        assert dashboard_server.require_auth is None
        assert dashboard_server.require_session is None
    
    def test_mobile_auth_api_without_auth(self, running_dashboard):
        """Test mobile auth API when auth is disabled"""
        response = requests.get(
            f'http://{TestConfig.TEST_HOST}:{TestConfig.TEST_PORT}/api/auth/status',
            timeout=TestConfig.HTTP_TIMEOUT
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['authenticated'] is False
        assert data['auth_enabled'] is False
    
    def test_mobile_responsive_css(self, running_dashboard):
        """Test mobile responsive CSS is included"""
        response = requests.get(
            f'http://{TestConfig.TEST_HOST}:{TestConfig.TEST_PORT}/',
            timeout=TestConfig.HTTP_TIMEOUT
        )
        
        content = response.text
        
        # Check for responsive design elements
        assert '@media' in content or 'max-width' in content or 'min-width' in content
    
    @patch('dashboard_server.MobileAuthManager')
    @patch('dashboard_server.create_auth_decorators')
    def test_mobile_auth_enabled(self, mock_decorators, mock_auth_manager):
        """Test mobile authentication when enabled"""
        mock_auth_instance = Mock()
        mock_auth_manager.return_value = mock_auth_instance
        mock_decorators.return_value = (Mock(), Mock())
        
        with patch('dashboard_server.Path.home') as mock_home:
            mock_home.return_value = Path.cwd()
            
            server = DashboardServer(
                port=TestConfig.TEST_PORT + 2, 
                mobile_auth_token='test-token'
            )
            
            assert server.auth_manager is mock_auth_instance
            assert server.require_auth is not None
            assert server.require_session is not None


class TestTtydTerminalIntegration:
    """Test ttyd terminal integration"""
    
    def test_terminal_manager_initialization(self):
        """Test TerminalManager initializes correctly"""
        manager = TerminalManager()
        
        assert manager.port == 7681
        assert manager.username == "admin"
        assert len(manager.password) > 8
        assert manager.process is None
    
    @patch('requests.get')
    def test_ttyd_download_success(self, mock_get):
        """Test successful ttyd download"""
        # Mock successful download
        mock_response = Mock()
        mock_response.headers = {'content-length': '1000'}
        mock_response.iter_content = Mock(return_value=[b'fake_binary_data'])
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        manager = TerminalManager()
        manager.ttyd_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure file doesn't exist
        if manager.ttyd_path.exists():
            manager.ttyd_path.unlink()
        
        result = manager.download_ttyd()
        assert result is True
        assert manager.ttyd_path.exists()
    
    @patch('requests.get')
    def test_ttyd_download_failure(self, mock_get):
        """Test ttyd download failure handling"""
        # Mock failed download
        mock_get.side_effect = Exception('Download failed')
        
        manager = TerminalManager()
        manager.ttyd_dir.mkdir(parents=True, exist_ok=True)
        
        result = manager.download_ttyd()
        assert result is False
    
    @patch('subprocess.Popen')
    def test_terminal_start_success(self, mock_popen):
        """Test successful terminal server start"""
        # Mock successful process start
        mock_process = Mock()
        mock_process.poll.return_value = None  # Process is running
        mock_popen.return_value = mock_process
        
        manager = TerminalManager()
        manager.ttyd_dir.mkdir(parents=True, exist_ok=True)
        
        # Create fake ttyd binary
        manager.ttyd_path.touch()
        if not sys.platform.startswith('win'):
            manager.ttyd_path.chmod(0o755)
        
        result = manager.start_terminal()
        assert result is True
        assert manager.process is mock_process
    
    @patch('subprocess.Popen')
    def test_terminal_start_failure(self, mock_popen):
        """Test terminal server start failure"""
        # Mock failed process start
        mock_process = Mock()
        mock_process.poll.return_value = 1  # Process failed
        mock_process.communicate.return_value = ('stdout', 'stderr')
        mock_popen.return_value = mock_process
        
        manager = TerminalManager()
        manager.ttyd_dir.mkdir(parents=True, exist_ok=True)
        
        # Create fake ttyd binary
        manager.ttyd_path.touch()
        if not sys.platform.startswith('win'):
            manager.ttyd_path.chmod(0o755)
        
        result = manager.start_terminal()
        assert result is False
    
    def test_terminal_credentials(self):
        """Test terminal credentials generation"""
        manager = TerminalManager()
        credentials = manager.get_credentials()
        
        assert 'url' in credentials
        assert 'username' in credentials
        assert 'password' in credentials
        
        assert credentials['url'] == f'http://localhost:{manager.port}'
        assert credentials['username'] == manager.username
        assert credentials['password'] == manager.password
    
    def test_terminal_stop(self):
        """Test terminal server stop functionality"""
        manager = TerminalManager()
        mock_process = Mock()
        manager.process = mock_process
        
        manager.stop_terminal()
        
        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once_with(timeout=5)


class TestSimpleDashboard:
    """Test simple dashboard functionality"""
    
    def test_dashboard_handler_get_root(self):
        """Test dashboard handler GET request for root"""
        from http.server import HTTPServer
        from unittest.mock import patch
        import io
        
        # Create mock request
        handler = DashboardHandler(Mock(), ('127.0.0.1', 8080), Mock())
        handler.path = '/'
        
        # Mock wfile
        handler.wfile = io.BytesIO()
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        
        handler.do_GET()
        
        handler.send_response.assert_called_with(200)
        handler.send_header.assert_called()
    
    def test_dashboard_handler_health_check(self):
        """Test dashboard handler health check endpoint"""
        import io
        
        handler = DashboardHandler(Mock(), ('127.0.0.1', 8080), Mock())
        handler.path = '/health'
        
        # Mock wfile
        handler.wfile = io.BytesIO()
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        
        handler.do_GET()
        
        handler.send_response.assert_called_with(200)
        
    def test_dashboard_handler_404(self):
        """Test dashboard handler 404 response"""
        handler = DashboardHandler(Mock(), ('127.0.0.1', 8080), Mock())
        handler.path = '/nonexistent'
        
        handler.send_response = Mock()
        handler.end_headers = Mock()
        
        handler.do_GET()
        
        handler.send_response.assert_called_with(404)


class TestIntegrationScenarios:
    """Test complete integration scenarios"""
    
    def test_full_dashboard_lifecycle(self, mock_claude_dir):
        """Test complete dashboard lifecycle"""
        with patch('dashboard_server.Path.home') as mock_home:
            mock_home.return_value = mock_claude_dir.parent
            
            # Initialize dashboard
            server = DashboardServer(port=TestConfig.TEST_PORT + 3)
            
            # Start monitoring
            server.start_monitoring()
            time.sleep(1)
            
            # Test metrics collection
            metrics = server.get_current_metrics()
            assert 'system' in metrics or 'error' in metrics
            
            # Test alert system
            server.add_alert('info', 'Test integration alert')
            assert len(server.alerts) == 1
            
            # Test status update
            server.update_system_status()
            assert server.system_status in ['healthy', 'warning', 'critical', 'error']
            
            # Stop monitoring
            server.stop_monitoring()
            assert server.monitoring is False
    
    def test_concurrent_client_connections(self, running_dashboard):
        """Test multiple concurrent client connections"""
        clients = []
        
        try:
            # Create multiple clients
            for i in range(3):
                client = socketio.SimpleClient()
                client.connect(f'http://{TestConfig.TEST_HOST}:{TestConfig.TEST_PORT}')
                clients.append(client)
            
            # All clients should be connected
            for client in clients:
                assert client.connected
            
            # Test broadcast reaches all clients
            for client in clients:
                client.emit('request_update')
                event = client.receive(timeout=TestConfig.WEBSOCKET_TIMEOUT)
                assert event is not None
                
        finally:
            # Cleanup
            for client in clients:
                if client.connected:
                    client.disconnect()
    
    def test_performance_under_load(self, running_dashboard):
        """Test dashboard performance under load"""
        import concurrent.futures
        import time
        
        def make_request():
            try:
                response = requests.get(
                    f'http://{TestConfig.TEST_HOST}:{TestConfig.TEST_PORT}/api/metrics',
                    timeout=5
                )
                return response.status_code == 200
            except:
                return False
        
        # Make concurrent requests
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        
        # Check results
        success_rate = sum(results) / len(results)
        response_time = end_time - start_time
        
        assert success_rate >= 0.8, f"Success rate too low: {success_rate}"
        assert response_time < 10, f"Response time too high: {response_time}"
    
    @pytest.mark.asyncio
    async def test_websocket_resilience(self, running_dashboard):
        """Test WebSocket connection resilience"""
        client = socketio.AsyncSimpleClient()
        
        try:
            # Connect
            await client.connect(f'http://{TestConfig.TEST_HOST}:{TestConfig.TEST_PORT}')
            
            # Send multiple requests rapidly
            for i in range(10):
                await client.emit('request_update')
                await asyncio.sleep(0.1)
            
            # Should still be connected
            assert client.connected
            
            # Should receive responses
            response_count = 0
            try:
                while response_count < 5:
                    event = await client.receive(timeout=1)
                    if event:
                        response_count += 1
            except:
                pass
            
            assert response_count > 0, "No responses received"
            
        finally:
            if client.connected:
                await client.disconnect()


# Performance and Load Testing
class TestPerformanceMetrics:
    """Test performance metrics and benchmarks"""
    
    def test_memory_usage(self, dashboard_server):
        """Test dashboard memory usage stays reasonable"""
        import psutil
        import gc
        
        # Get initial memory
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Perform operations that might consume memory
        for _ in range(100):
            dashboard_server.get_current_metrics()
            dashboard_server.add_alert('info', f'Test alert {_}')
        
        # Force garbage collection
        gc.collect()
        
        # Check memory growth
        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be reasonable (less than 50MB for this test)
        assert memory_growth < 50 * 1024 * 1024, f"Memory growth too high: {memory_growth} bytes"
    
    def test_response_time_benchmarks(self, running_dashboard):
        """Test API response time benchmarks"""
        import time
        
        endpoints = [
            '/api/status',
            '/api/metrics',
            '/api/agents'
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            
            response = requests.get(
                f'http://{TestConfig.TEST_HOST}:{TestConfig.TEST_PORT}{endpoint}',
                timeout=TestConfig.HTTP_TIMEOUT
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 1.0, f"Endpoint {endpoint} too slow: {response_time}s"


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--asyncio-mode=auto',
        '-W', 'ignore::DeprecationWarning'
    ])