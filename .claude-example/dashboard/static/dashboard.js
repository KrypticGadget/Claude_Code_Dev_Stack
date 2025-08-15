/**
 * Claude Code Dashboard V3+ - Enhanced JavaScript Module
 * Comprehensive WebSocket client utilities and real-time dashboard management
 * 
 * Features:
 * - WebSocket connection management with auto-reconnect
 * - Real-time event handling for all socket events
 * - Dynamic DOM updates and data visualization
 * - Command execution interface
 * - Browser and in-page notifications
 * - Mobile touch events and optimizations
 * - Error handling and connection status management
 */

class ClaudeDashboard {
    constructor() {
        // Core properties
        this.socket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnectDelay = 1000; // Start with 1 second
        this.maxReconnectDelay = 30000; // Max 30 seconds
        
        // Charts and visualizations
        this.charts = {};
        this.chartData = {
            resources: { timestamps: [], cpu: [], memory: [], disk: [] },
            performance: { timestamps: [], responseTime: [], operations: [] }
        };
        
        // Data stores
        this.systemMetrics = {};
        this.agentStatus = {};
        this.hookStatus = {};
        this.alerts = [];
        this.logs = [];
        
        // UI state
        this.activeTab = 'overview';
        this.lastUpdate = null;
        this.updateTimer = null;
        
        // Mobile optimization
        this.isMobile = this.detectMobile();
        this.touchStartY = 0;
        this.touchEndY = 0;
        this.pullThreshold = 100;
        
        // Notification support
        this.notificationPermission = 'default';
        this.soundEnabled = true;
        
        // Initialize
        this.init();
    }

    /**
     * Initialize the dashboard
     */
    init() {
        console.log('🚀 Initializing Claude Code Dashboard V3+');
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupDashboard());
        } else {
            this.setupDashboard();
        }
    }

    /**
     * Setup dashboard components
     */
    setupDashboard() {
        this.setupWebSocket();
        this.setupEventListeners();
        this.setupNotifications();
        this.setupMobileOptimizations();
        this.initializeCharts();
        this.loadInitialData();
        this.startUpdateTimer();
        
        console.log('✅ Dashboard initialized successfully');
    }

    /**
     * WebSocket Connection Management
     */
    setupWebSocket() {
        try {
            // Initialize Socket.IO connection
            this.socket = io({
                transports: ['websocket', 'polling'],
                upgrade: true,
                rememberUpgrade: true,
                timeout: 10000,
                forceNew: false,
                reconnection: true,
                reconnectionAttempts: this.maxReconnectAttempts,
                reconnectionDelay: this.reconnectDelay,
                reconnectionDelayMax: this.maxReconnectDelay,
                maxReconnectionAttempts: this.maxReconnectAttempts
            });

            // Connection event handlers
            this.socket.on('connect', () => this.handleConnect());
            this.socket.on('disconnect', (reason) => this.handleDisconnect(reason));
            this.socket.on('connect_error', (error) => this.handleConnectionError(error));
            this.socket.on('reconnect', (attemptNumber) => this.handleReconnect(attemptNumber));
            this.socket.on('reconnect_attempt', (attemptNumber) => this.handleReconnectAttempt(attemptNumber));
            this.socket.on('reconnect_failed', () => this.handleReconnectFailed());

            // Data event handlers
            this.socket.on('claude_sessions', (data) => this.handleClaudeSessions(data));
            this.socket.on('git_activity', (data) => this.handleGitActivity(data));
            this.socket.on('file_change', (data) => this.handleFileChange(data));
            this.socket.on('system_metrics', (data) => this.handleSystemMetrics(data));
            this.socket.on('command_result', (data) => this.handleCommandResult(data));
            this.socket.on('status_update', (data) => this.handleStatusUpdate(data));
            this.socket.on('metrics_update', (data) => this.handleMetricsUpdate(data));
            this.socket.on('new_alert', (data) => this.handleNewAlert(data));

        } catch (error) {
            console.error('❌ Failed to initialize WebSocket:', error);
            this.updateConnectionStatus('error', 'WebSocket initialization failed');
        }
    }

    /**
     * Connection Event Handlers
     */
    handleConnect() {
        console.log('🔗 WebSocket connected');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;
        this.updateConnectionStatus('connected', 'Connected');
        
        // Request initial data
        this.requestUpdate();
        
        // Show notification
        this.showNotification('Dashboard Connected', 'Successfully connected to Claude Code Dashboard', 'success');
        this.playSound('connect');
    }

    handleDisconnect(reason) {
        console.log('🔌 WebSocket disconnected:', reason);
        this.isConnected = false;
        this.updateConnectionStatus('disconnected', `Disconnected: ${reason}`);
        
        // Show notification
        this.showNotification('Dashboard Disconnected', `Connection lost: ${reason}`, 'warning');
        this.playSound('disconnect');
        
        // Attempt manual reconnection for certain reasons
        if (reason === 'io server disconnect' || reason === 'transport close') {
            setTimeout(() => this.attemptReconnect(), 2000);
        }
    }

    handleConnectionError(error) {
        console.error('🚨 WebSocket connection error:', error);
        this.updateConnectionStatus('error', 'Connection error');
    }

    handleReconnect(attemptNumber) {
        console.log(`🔄 WebSocket reconnected after ${attemptNumber} attempts`);
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.updateConnectionStatus('connected', 'Reconnected');
        
        this.showNotification('Dashboard Reconnected', 'Connection restored successfully', 'success');
        this.playSound('reconnect');
    }

    handleReconnectAttempt(attemptNumber) {
        console.log(`🔄 Reconnection attempt ${attemptNumber}`);
        this.reconnectAttempts = attemptNumber;
        this.updateConnectionStatus('reconnecting', `Reconnecting... (${attemptNumber}/${this.maxReconnectAttempts})`);
    }

    handleReconnectFailed() {
        console.error('💥 WebSocket reconnection failed');
        this.updateConnectionStatus('failed', 'Reconnection failed');
        
        this.showNotification('Connection Failed', 'Unable to reconnect to dashboard', 'error');
        this.playSound('error');
    }

    /**
     * Manual reconnection attempt
     */
    attemptReconnect() {
        if (!this.isConnected && this.socket) {
            console.log('🔄 Attempting manual reconnection...');
            this.socket.connect();
        }
    }

    /**
     * Data Event Handlers
     */
    handleClaudeSessions(data) {
        console.log('👤 Claude sessions update:', data);
        this.updateSessionsDisplay(data);
        this.logEvent('Claude Sessions', `${data.active_sessions} active sessions`, 'info');
    }

    handleGitActivity(data) {
        console.log('📝 Git activity:', data);
        this.updateGitActivity(data);
        this.logEvent('Git Activity', data.message || 'Git operation completed', 'info');
        
        // Show notification for important git events
        if (data.type === 'push' || data.type === 'pull' || data.type === 'commit') {
            this.showNotification('Git Activity', data.message || `Git ${data.type} operation`, 'info');
        }
    }

    handleFileChange(data) {
        console.log('📁 File change:', data);
        this.updateFileChanges(data);
        this.logEvent('File Change', `${data.file} ${data.action}`, 'info');
    }

    handleSystemMetrics(data) {
        console.log('📊 System metrics:', data);
        this.systemMetrics = data;
        this.updateSystemMetricsDisplay(data);
        this.updateChartsWithMetrics(data);
    }

    handleCommandResult(data) {
        console.log('⚡ Command result:', data);
        this.displayCommandResult(data);
        this.logEvent('Command Executed', data.command || 'Command completed', data.success ? 'success' : 'error');
        
        // Show notification for command completion
        const status = data.success ? 'success' : 'error';
        const message = data.success ? 'Command executed successfully' : 'Command execution failed';
        this.showNotification('Command Result', message, status);
    }

    handleStatusUpdate(data) {
        console.log('🔄 Status update:', data);
        this.updateSystemStatus(data);
        this.lastUpdate = new Date();
        this.updateLastUpdateDisplay();
    }

    handleMetricsUpdate(data) {
        console.log('📈 Metrics update:', data);
        this.systemMetrics = { ...this.systemMetrics, ...data };
        this.updateMetricsDisplay(data);
        this.updateChartsWithMetrics(data);
    }

    handleNewAlert(data) {
        console.log('🚨 New alert:', data);
        this.alerts.unshift(data);
        this.updateAlertsDisplay();
        
        // Show notification for alerts
        const level = data.level || 'info';
        this.showNotification('System Alert', data.message, level);
        this.playSound('alert');
    }

    /**
     * UI Update Methods
     */
    updateConnectionStatus(status, text) {
        const statusIndicator = document.getElementById('connection-status');
        const statusText = document.getElementById('connection-text');
        
        if (statusIndicator && statusText) {
            // Remove existing status classes
            statusIndicator.className = 'status-indicator';
            
            // Add appropriate status class
            switch (status) {
                case 'connected':
                    statusIndicator.classList.add('status-healthy');
                    break;
                case 'disconnected':
                case 'reconnecting':
                    statusIndicator.classList.add('status-warning');
                    break;
                case 'error':
                case 'failed':
                    statusIndicator.classList.add('status-critical');
                    break;
                default:
                    statusIndicator.classList.add('status-unknown');
            }
            
            statusText.textContent = text;
        }
    }

    updateSystemStatus(data) {
        const statusElement = document.getElementById('system-status');
        if (statusElement && data.status) {
            const status = data.status;
            const statusText = status.charAt(0).toUpperCase() + status.slice(1);
            
            statusElement.innerHTML = `
                <span class="status-indicator status-${status}"></span>
                ${statusText}
            `;
        }

        // Update uptime
        const uptimeElement = document.getElementById('uptime');
        if (uptimeElement && data.uptime) {
            uptimeElement.textContent = data.uptime;
        }
    }

    updateMetricsDisplay(data) {
        if (data.system) {
            this.updateProgressBar('cpu', data.system.cpu_percent);
            this.updateProgressBar('memory', data.system.memory_percent);
            this.updateProgressBar('disk', data.system.disk_percent);
        }

        if (data.claude_code) {
            this.updateElement('total-operations', data.claude_code.total_operations);
            this.updateElement('total-tokens', data.claude_code.total_tokens_used?.toLocaleString());
        }
    }

    updateProgressBar(type, value) {
        const progressBar = document.getElementById(`${type}-progress`);
        const text = document.getElementById(`${type}-text`);
        
        if (progressBar && text) {
            progressBar.style.width = `${value}%`;
            text.textContent = `${value.toFixed(1)}%`;
            
            // Update color based on value
            progressBar.className = 'progress-bar';
            if (value > 90) {
                progressBar.classList.add('bg-danger');
            } else if (value > 70) {
                progressBar.classList.add('bg-warning');
            } else {
                progressBar.classList.add('bg-success');
            }
        }
    }

    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element && value !== undefined) {
            element.textContent = value;
        }
    }

    updateAlertsDisplay() {
        const alertsContainer = document.getElementById('recent-alerts');
        const alertsCount = document.getElementById('active-alerts');
        
        if (alertsCount) {
            alertsCount.textContent = this.alerts.length;
        }
        
        if (alertsContainer) {
            alertsContainer.innerHTML = '';
            
            // Show last 5 alerts
            const recentAlerts = this.alerts.slice(0, 5);
            
            if (recentAlerts.length === 0) {
                alertsContainer.innerHTML = '<p class="text-muted">No recent alerts</p>';
                return;
            }
            
            recentAlerts.forEach(alert => {
                const alertClass = this.getAlertClass(alert.level);
                const alertElement = document.createElement('div');
                alertElement.className = `alert ${alertClass} alert-sm mb-2`;
                
                const timestamp = new Date(alert.timestamp).toLocaleTimeString();
                alertElement.innerHTML = `
                    <small class="text-muted">${timestamp}</small><br>
                    <strong>${alert.message}</strong>
                    ${alert.details ? `<br><small>${alert.details}</small>` : ''}
                `;
                
                alertsContainer.appendChild(alertElement);
            });
        }
    }

    getAlertClass(level) {
        switch (level) {
            case 'error': return 'alert-danger';
            case 'warning': return 'alert-warning';
            case 'success': return 'alert-success';
            case 'info':
            default: return 'alert-info';
        }
    }

    updateLastUpdateDisplay() {
        const lastUpdateElement = document.getElementById('last-update');
        if (lastUpdateElement && this.lastUpdate) {
            lastUpdateElement.textContent = this.lastUpdate.toLocaleTimeString();
        }
    }

    /**
     * Chart and Data Visualization
     */
    initializeCharts() {
        try {
            this.initResourceChart();
            this.initPerformanceChart();
            this.initTimelineChart();
            console.log('📊 Charts initialized');
        } catch (error) {
            console.error('❌ Chart initialization failed:', error);
        }
    }

    initResourceChart() {
        const canvas = document.getElementById('resource-chart');
        if (canvas) {
            const ctx = canvas.getContext('2d');
            this.charts.resource = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['CPU', 'Memory', 'Disk'],
                    datasets: [{
                        data: [0, 0, 0],
                        backgroundColor: ['#da3633', '#d29922', '#238636'],
                        borderColor: '#161b22',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { 
                                color: '#c9d1d9',
                                font: { size: this.isMobile ? 12 : 14 }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `${context.label}: ${context.parsed.toFixed(1)}%`;
                                }
                            }
                        }
                    }
                }
            });
        }
    }

    initPerformanceChart() {
        const canvas = document.getElementById('performance-chart');
        if (canvas) {
            const ctx = canvas.getContext('2d');
            this.charts.performance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Response Time (ms)',
                        data: [],
                        borderColor: '#0969da',
                        backgroundColor: 'rgba(9, 105, 218, 0.1)',
                        tension: 0.4,
                        fill: true
                    }, {
                        label: 'Operations/min',
                        data: [],
                        borderColor: '#238636',
                        backgroundColor: 'rgba(35, 134, 54, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y1'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    plugins: {
                        legend: {
                            labels: { 
                                color: '#c9d1d9',
                                font: { size: this.isMobile ? 12 : 14 }
                            }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { 
                                color: '#c9d1d9',
                                font: { size: this.isMobile ? 10 : 12 }
                            },
                            grid: { color: '#30363d' }
                        },
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            ticks: { 
                                color: '#c9d1d9',
                                font: { size: this.isMobile ? 10 : 12 }
                            },
                            grid: { color: '#30363d' }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            ticks: { 
                                color: '#c9d1d9',
                                font: { size: this.isMobile ? 10 : 12 }
                            },
                            grid: { drawOnChartArea: false }
                        }
                    }
                }
            });
        }
    }

    initTimelineChart() {
        const canvas = document.getElementById('performance-timeline-chart');
        if (canvas) {
            const ctx = canvas.getContext('2d');
            this.charts.timeline = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'CPU %',
                        data: [],
                        borderColor: '#da3633',
                        backgroundColor: 'rgba(218, 54, 51, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Memory %',
                        data: [],
                        borderColor: '#d29922',
                        backgroundColor: 'rgba(210, 153, 34, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Disk %',
                        data: [],
                        borderColor: '#238636',
                        backgroundColor: 'rgba(35, 134, 54, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    plugins: {
                        legend: {
                            labels: { 
                                color: '#c9d1d9',
                                font: { size: this.isMobile ? 12 : 14 }
                            }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { 
                                color: '#c9d1d9',
                                font: { size: this.isMobile ? 10 : 12 }
                            },
                            grid: { color: '#30363d' }
                        },
                        y: {
                            ticks: { 
                                color: '#c9d1d9',
                                font: { size: this.isMobile ? 10 : 12 }
                            },
                            grid: { color: '#30363d' },
                            min: 0,
                            max: 100
                        }
                    }
                }
            });
        }
    }

    updateChartsWithMetrics(data) {
        // Update resource chart
        if (this.charts.resource && data.system) {
            const resourceData = [
                data.system.cpu_percent || 0,
                data.system.memory_percent || 0,
                data.system.disk_percent || 0
            ];
            this.charts.resource.data.datasets[0].data = resourceData;
            this.charts.resource.update('none');
        }

        // Update timeline chart
        if (this.charts.timeline && data.system) {
            const now = new Date().toLocaleTimeString();
            
            // Add new data point
            this.chartData.resources.timestamps.push(now);
            this.chartData.resources.cpu.push(data.system.cpu_percent || 0);
            this.chartData.resources.memory.push(data.system.memory_percent || 0);
            this.chartData.resources.disk.push(data.system.disk_percent || 0);
            
            // Keep only last 20 data points
            if (this.chartData.resources.timestamps.length > 20) {
                this.chartData.resources.timestamps.shift();
                this.chartData.resources.cpu.shift();
                this.chartData.resources.memory.shift();
                this.chartData.resources.disk.shift();
            }
            
            // Update chart
            this.charts.timeline.data.labels = this.chartData.resources.timestamps;
            this.charts.timeline.data.datasets[0].data = this.chartData.resources.cpu;
            this.charts.timeline.data.datasets[1].data = this.chartData.resources.memory;
            this.charts.timeline.data.datasets[2].data = this.chartData.resources.disk;
            this.charts.timeline.update('none');
        }
    }

    /**
     * Command Execution Interface
     */
    executeCommand(command, params = {}) {
        if (!this.isConnected) {
            this.showNotification('Command Failed', 'Not connected to dashboard', 'error');
            return;
        }

        console.log(`⚡ Executing command: ${command}`, params);
        
        // Show command execution feedback
        this.showCommandExecuting(command);
        
        // Send command via WebSocket
        this.socket.emit('execute_command', {
            command: command,
            params: params,
            timestamp: new Date().toISOString()
        });
    }

    showCommandExecuting(command) {
        // You can implement a loading state UI here
        const commandButton = document.querySelector(`[data-command="${command}"]`);
        if (commandButton) {
            commandButton.classList.add('executing');
            commandButton.disabled = true;
            
            // Reset after 5 seconds
            setTimeout(() => {
                commandButton.classList.remove('executing');
                commandButton.disabled = false;
            }, 5000);
        }
    }

    displayCommandResult(data) {
        // Display command result in a modal or dedicated area
        const resultContainer = document.getElementById('command-results');
        if (resultContainer) {
            const resultElement = document.createElement('div');
            resultElement.className = `command-result ${data.success ? 'success' : 'error'}`;
            
            const timestamp = new Date(data.timestamp).toLocaleTimeString();
            resultElement.innerHTML = `
                <div class="result-header">
                    <strong>${data.command || 'Command'}</strong>
                    <span class="timestamp">${timestamp}</span>
                </div>
                <div class="result-body">
                    <pre>${data.output || data.error || 'No output'}</pre>
                </div>
            `;
            
            resultContainer.insertBefore(resultElement, resultContainer.firstChild);
            
            // Keep only last 10 results
            while (resultContainer.children.length > 10) {
                resultContainer.removeChild(resultContainer.lastChild);
            }
        }
    }

    /**
     * Notification System
     */
    setupNotifications() {
        // Request notification permission
        if ('Notification' in window) {
            Notification.requestPermission().then(permission => {
                this.notificationPermission = permission;
                console.log(`🔔 Notification permission: ${permission}`);
            });
        }
    }

    showNotification(title, message, type = 'info', duration = 5000) {
        // Browser notification
        if (this.notificationPermission === 'granted') {
            const notification = new Notification(title, {
                body: message,
                icon: this.getNotificationIcon(type),
                tag: 'claude-dashboard',
                requireInteraction: type === 'error'
            });
            
            notification.onclick = () => {
                window.focus();
                notification.close();
            };
            
            // Auto close
            if (type !== 'error') {
                setTimeout(() => notification.close(), duration);
            }
        }
        
        // In-page notification
        this.showInPageNotification(title, message, type, duration);
    }

    showInPageNotification(title, message, type, duration) {
        const container = this.getNotificationContainer();
        
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-header">
                <strong>${title}</strong>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">&times;</button>
            </div>
            <div class="notification-body">${message}</div>
        `;
        
        container.appendChild(notification);
        
        // Animate in
        setTimeout(() => notification.classList.add('show'), 10);
        
        // Auto remove
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, duration);
    }

    getNotificationContainer() {
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container';
            document.body.appendChild(container);
        }
        return container;
    }

    getNotificationIcon(type) {
        const icons = {
            'success': '✅',
            'warning': '⚠️',
            'error': '❌',
            'info': 'ℹ️'
        };
        return icons[type] || icons.info;
    }

    /**
     * Mobile Optimization
     */
    setupMobileOptimizations() {
        if (this.isMobile) {
            console.log('📱 Setting up mobile optimizations');
            
            // Add mobile-specific classes
            document.body.classList.add('mobile-device');
            
            // Setup touch events
            this.setupTouchEvents();
            
            // Setup pull-to-refresh
            this.setupPullToRefresh();
            
            // Optimize charts for mobile
            this.optimizeChartsForMobile();
        }
    }

    detectMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
               (window.innerWidth <= 768);
    }

    setupTouchEvents() {
        // Add touch event listeners for better mobile interaction
        document.addEventListener('touchstart', (e) => {
            this.touchStartY = e.touches[0].clientY;
        }, { passive: true });
        
        document.addEventListener('touchend', (e) => {
            this.touchEndY = e.changedTouches[0].clientY;
            this.handleTouchGesture();
        }, { passive: true });
        
        // Prevent zoom on double tap for dashboard elements
        document.addEventListener('touchend', (e) => {
            if (e.target.closest('.dashboard-content')) {
                e.preventDefault();
            }
        });
    }

    setupPullToRefresh() {
        const container = document.querySelector('.container-fluid');
        if (container) {
            container.addEventListener('touchstart', (e) => {
                if (window.scrollY === 0) {
                    this.touchStartY = e.touches[0].clientY;
                }
            }, { passive: true });
            
            container.addEventListener('touchmove', (e) => {
                if (window.scrollY === 0) {
                    const touchY = e.touches[0].clientY;
                    const pullDistance = touchY - this.touchStartY;
                    
                    if (pullDistance > this.pullThreshold) {
                        this.showPullToRefreshIndicator();
                    }
                }
            }, { passive: true });
            
            container.addEventListener('touchend', (e) => {
                if (window.scrollY === 0) {
                    const touchY = e.changedTouches[0].clientY;
                    const pullDistance = touchY - this.touchStartY;
                    
                    if (pullDistance > this.pullThreshold) {
                        this.refreshDashboard();
                    }
                    this.hidePullToRefreshIndicator();
                }
            }, { passive: true });
        }
    }

    handleTouchGesture() {
        const distance = this.touchEndY - this.touchStartY;
        
        // Swipe down to refresh (when at top)
        if (distance > 50 && window.scrollY === 0) {
            this.refreshDashboard();
        }
        
        // Swipe up for quick access menu (when at bottom)
        if (distance < -50 && (window.innerHeight + window.scrollY) >= document.body.offsetHeight) {
            this.showQuickActions();
        }
    }

    showPullToRefreshIndicator() {
        // Implement pull-to-refresh visual indicator
        let indicator = document.getElementById('pull-refresh-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'pull-refresh-indicator';
            indicator.className = 'pull-refresh-indicator';
            indicator.innerHTML = '↓ Pull to refresh';
            document.body.insertBefore(indicator, document.body.firstChild);
        }
        indicator.classList.add('visible');
    }

    hidePullToRefreshIndicator() {
        const indicator = document.getElementById('pull-refresh-indicator');
        if (indicator) {
            indicator.classList.remove('visible');
        }
    }

    optimizeChartsForMobile() {
        // Adjust chart options for mobile devices
        const mobileOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { 
                        boxWidth: 12,
                        padding: 10,
                        font: { size: 10 }
                    }
                }
            },
            elements: {
                point: {
                    radius: 2,
                    hoverRadius: 4
                }
            }
        };
        
        // Apply to all charts when they're created
        this.mobileChartOptions = mobileOptions;
    }

    showQuickActions() {
        // Show a quick action menu for mobile users
        const quickActions = document.getElementById('quick-actions-modal');
        if (quickActions) {
            quickActions.classList.add('show');
        }
    }

    /**
     * Audio System
     */
    playSound(type) {
        if (!this.soundEnabled) return;
        
        try {
            // Create audio context if needed
            if (!this.audioContext) {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            }
            
            // Play appropriate sound for event type
            const sounds = {
                'connect': [800, 1000], // Rising tone
                'disconnect': [600, 400], // Falling tone
                'reconnect': [600, 800, 1000], // Rising sequence
                'alert': [1200, 1200, 1200], // Alert beeps
                'error': [300, 300, 300], // Error beeps
                'success': [800, 1200] // Success tone
            };
            
            const tones = sounds[type] || sounds.info;
            this.playToneSequence(tones);
            
        } catch (error) {
            console.warn('🔇 Audio not available:', error);
        }
    }

    playToneSequence(frequencies) {
        frequencies.forEach((freq, index) => {
            setTimeout(() => {
                this.playTone(freq, 0.1, 0.1);
            }, index * 150);
        });
    }

    playTone(frequency, duration, volume = 0.1) {
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.value = frequency;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(volume, this.audioContext.currentTime + 0.01);
        gainNode.gain.exponentialRampToValueAtTime(0.001, this.audioContext.currentTime + duration);
        
        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + duration);
    }

    /**
     * Data Management
     */
    loadInitialData() {
        console.log('📊 Loading initial dashboard data...');
        
        const endpoints = [
            '/api/status',
            '/api/metrics',
            '/api/agents',
            '/api/hooks',
            '/api/performance',
            '/api/security',
            '/api/logs',
            '/api/alerts'
        ];
        
        endpoints.forEach(endpoint => {
            fetch(endpoint)
                .then(response => response.json())
                .then(data => this.handleApiResponse(endpoint, data))
                .catch(error => console.error(`Error loading ${endpoint}:`, error));
        });
    }

    handleApiResponse(endpoint, data) {
        switch (endpoint) {
            case '/api/status':
                this.updateSystemStatus(data);
                break;
            case '/api/metrics':
                this.updateMetricsDisplay(data);
                break;
            case '/api/agents':
                this.updateAgentsTable(data);
                break;
            case '/api/hooks':
                this.updateHooksTable(data);
                break;
            case '/api/performance':
                this.updatePerformanceTab(data);
                break;
            case '/api/security':
                this.updateSecurityTab(data);
                break;
            case '/api/logs':
                this.updateLogsTab(data);
                break;
            case '/api/alerts':
                this.alerts = data.alerts || [];
                this.updateAlertsDisplay();
                break;
        }
    }

    updateAgentsTable(data) {
        const tbody = document.getElementById('agents-table');
        const totalAgents = document.getElementById('total-agents');
        const activeAgents = document.getElementById('active-agents');
        
        if (totalAgents) totalAgents.textContent = data.total_agents || 0;
        if (activeAgents) activeAgents.textContent = data.active_agents || 0;
        
        if (tbody) {
            tbody.innerHTML = '';
            
            if (!data.agents || data.agents.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No agents found</td></tr>';
                return;
            }
            
            data.agents.forEach(agent => {
                const row = document.createElement('tr');
                const status = agent.last_used ? 'Active' : 'Inactive';
                const statusClass = agent.last_used ? 'text-success' : 'text-muted';
                const lastUsed = agent.last_used ? new Date(agent.last_used).toLocaleString() : 'Never';
                const fileSize = (agent.file_size / 1024).toFixed(1) + ' KB';
                
                row.innerHTML = `
                    <td>${agent.name}</td>
                    <td><span class="${statusClass}">${status}</span></td>
                    <td>${agent.executions || 0}</td>
                    <td>${lastUsed}</td>
                    <td>${fileSize}</td>
                `;
                tbody.appendChild(row);
            });
        }
    }

    updateHooksTable(data) {
        const tbody = document.getElementById('hooks-table');
        const totalHooks = document.getElementById('total-hooks');
        const enabledHooks = document.getElementById('enabled-hooks');
        
        if (totalHooks) totalHooks.textContent = data.total_hooks || 0;
        if (enabledHooks) enabledHooks.textContent = data.enabled_hooks || 0;
        
        if (tbody) {
            tbody.innerHTML = '';
            
            if (!data.hooks || data.hooks.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No hooks found</td></tr>';
                return;
            }
            
            data.hooks.forEach(hook => {
                const row = document.createElement('tr');
                const status = hook.enabled ? 'Enabled' : 'Disabled';
                const statusClass = hook.enabled ? 'text-success' : 'text-warning';
                const fileSize = (hook.file_size / 1024).toFixed(1) + ' KB';
                const modified = new Date(hook.modified * 1000).toLocaleString();
                
                row.innerHTML = `
                    <td>${hook.name}</td>
                    <td><span class="${statusClass}">${status}</span></td>
                    <td>${fileSize}</td>
                    <td>${modified}</td>
                `;
                tbody.appendChild(row);
            });
        }
    }

    updatePerformanceTab(data) {
        if (data.summary) {
            this.updateElement('avg-execution-time', `${data.summary.average_execution_time || 0}s`);
            this.updateElement('peak-memory', `${data.summary.peak_memory_usage || 0}%`);
            this.updateElement('performance-issues', data.summary.issues_detected || 0);
            this.updateElement('operations-count', data.summary.total_operations || 0);
        }
        
        // Update timeline chart if data available
        if (data.resource_timeline && this.charts.timeline) {
            const timeline = data.resource_timeline;
            this.charts.timeline.data.labels = timeline.timestamps.map(t => new Date(t).toLocaleTimeString());
            this.charts.timeline.data.datasets[0].data = timeline.cpu_usage;
            this.charts.timeline.data.datasets[1].data = timeline.memory_usage;
            this.charts.timeline.data.datasets[2].data = timeline.disk_usage;
            this.charts.timeline.update();
        }
    }

    updateSecurityTab(data) {
        const statusBadge = document.getElementById('security-status-badge');
        
        if (statusBadge) {
            let badgeClass = 'bg-secondary';
            let statusText = 'Unknown';
            
            if (data.status) {
                switch (data.status) {
                    case 'secure':
                        badgeClass = 'bg-success';
                        statusText = 'Secure';
                        break;
                    case 'warning':
                        badgeClass = 'bg-warning';
                        statusText = 'Warning';
                        break;
                    case 'critical':
                        badgeClass = 'bg-danger';
                        statusText = 'Critical';
                        break;
                    case 'attention':
                        badgeClass = 'bg-info';
                        statusText = 'Attention';
                        break;
                }
            }
            
            statusBadge.innerHTML = `<span class="badge ${badgeClass}">${statusText}</span>`;
        }
        
        this.updateElement('total-security-issues', data.total_issues || 0);
        this.updateElement('files-scanned', data.files_scanned || 0);
        
        if (data.last_scan) {
            this.updateElement('last-scan', new Date(data.last_scan).toLocaleString());
        }
        
        // Show recent issues
        const issuesContainer = document.getElementById('security-issues');
        if (issuesContainer) {
            if (data.recent_issues && data.recent_issues.length > 0) {
                issuesContainer.innerHTML = '<h6>Recent Issues:</h6>';
                data.recent_issues.forEach(issue => {
                    const alertClass = this.getSecurityAlertClass(issue.severity);
                    
                    const issueElement = document.createElement('div');
                    issueElement.className = `alert ${alertClass} alert-dismissible fade show`;
                    issueElement.innerHTML = `
                        <strong>${issue.file}:${issue.line}</strong> - ${issue.description}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    `;
                    
                    issuesContainer.appendChild(issueElement);
                });
            } else {
                issuesContainer.innerHTML = '<p class="text-muted">No recent security issues</p>';
            }
        }
    }

    getSecurityAlertClass(severity) {
        switch (severity) {
            case 'HIGH': return 'alert-danger';
            case 'MEDIUM': return 'alert-warning';
            case 'LOW':
            default: return 'alert-info';
        }
    }

    updateLogsTab(data) {
        const container = document.getElementById('logs-container');
        const count = document.getElementById('logs-count');
        
        if (count) {
            count.textContent = `${data.logs ? data.logs.length : 0} log entries`;
        }
        
        if (container) {
            if (data.logs && data.logs.length > 0) {
                container.innerHTML = '';
                data.logs.forEach(log => {
                    const logEntry = document.createElement('div');
                    logEntry.className = 'log-entry';
                    logEntry.innerHTML = `
                        <small class="text-muted">[${log.file}]</small> ${log.content}
                    `;
                    container.appendChild(logEntry);
                });
            } else {
                container.innerHTML = '<p class="text-muted">No log entries found</p>';
            }
        }
    }

    /**
     * Event System
     */
    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', (e) => {
                this.activeTab = e.target.getAttribute('data-bs-target').substring(1);
                this.onTabChange(this.activeTab);
            });
        });
        
        // Refresh buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="refresh"]') || e.target.closest('[data-action="refresh"]')) {
                e.preventDefault();
                this.refreshDashboard();
            }
        });
        
        // Command buttons
        document.addEventListener('click', (e) => {
            const commandButton = e.target.closest('[data-command]');
            if (commandButton) {
                e.preventDefault();
                const command = commandButton.getAttribute('data-command');
                const params = JSON.parse(commandButton.getAttribute('data-params') || '{}');
                this.executeCommand(command, params);
            }
        });
        
        // Settings toggle
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="toggle-sound"]')) {
                this.soundEnabled = !this.soundEnabled;
                e.target.textContent = this.soundEnabled ? '🔊' : '🔇';
                this.showNotification('Settings', `Sound ${this.soundEnabled ? 'enabled' : 'disabled'}`, 'info', 2000);
            }
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'r':
                        e.preventDefault();
                        this.refreshDashboard();
                        break;
                    case '1':
                    case '2':
                    case '3':
                    case '4':
                    case '5':
                    case '6':
                        e.preventDefault();
                        this.switchToTab(parseInt(e.key) - 1);
                        break;
                }
            }
        });
        
        // Window events
        window.addEventListener('online', () => {
            this.showNotification('Connection Restored', 'Internet connection restored', 'success');
            if (!this.isConnected) {
                this.attemptReconnect();
            }
        });
        
        window.addEventListener('offline', () => {
            this.showNotification('Connection Lost', 'Internet connection lost', 'warning');
        });
        
        // Visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                // Page is hidden, reduce update frequency
                this.pauseUpdates();
            } else {
                // Page is visible, resume normal updates
                this.resumeUpdates();
            }
        });
    }

    onTabChange(tabName) {
        console.log(`📋 Switched to ${tabName} tab`);
        
        // Load tab-specific data if needed
        switch (tabName) {
            case 'agents':
                fetch('/api/agents').then(r => r.json()).then(data => this.updateAgentsTable(data));
                break;
            case 'hooks':
                fetch('/api/hooks').then(r => r.json()).then(data => this.updateHooksTable(data));
                break;
            case 'performance':
                fetch('/api/performance').then(r => r.json()).then(data => this.updatePerformanceTab(data));
                break;
            case 'security':
                fetch('/api/security').then(r => r.json()).then(data => this.updateSecurityTab(data));
                break;
            case 'logs':
                fetch('/api/logs').then(r => r.json()).then(data => this.updateLogsTab(data));
                break;
        }
    }

    switchToTab(index) {
        const tabs = document.querySelectorAll('[data-bs-toggle="tab"]');
        if (tabs[index]) {
            tabs[index].click();
        }
    }

    /**
     * Update Management
     */
    startUpdateTimer() {
        // Start periodic updates
        this.updateTimer = setInterval(() => {
            if (!document.hidden && this.isConnected) {
                this.requestUpdate();
            }
        }, 30000); // Update every 30 seconds
        
        console.log('⏰ Update timer started');
    }

    requestUpdate() {
        if (this.socket && this.isConnected) {
            this.socket.emit('request_update');
        }
    }

    refreshDashboard() {
        console.log('🔄 Refreshing dashboard...');
        
        // Show refresh indicator
        this.showRefreshIndicator();
        
        // Load fresh data
        this.loadInitialData();
        
        // Request WebSocket update
        this.requestUpdate();
        
        // Hide refresh indicator after delay
        setTimeout(() => this.hideRefreshIndicator(), 1000);
        
        this.showNotification('Dashboard Refreshed', 'All data has been refreshed', 'success', 2000);
    }

    showRefreshIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'refresh-indicator';
        indicator.className = 'refresh-indicator';
        indicator.innerHTML = '🔄 Refreshing...';
        document.body.appendChild(indicator);
    }

    hideRefreshIndicator() {
        const indicator = document.getElementById('refresh-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    pauseUpdates() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
        }
    }

    resumeUpdates() {
        if (!this.updateTimer) {
            this.startUpdateTimer();
        }
    }

    /**
     * Utility Methods
     */
    logEvent(category, message, level = 'info') {
        const timestamp = new Date().toISOString();
        console.log(`[${timestamp}] ${category}: ${message}`);
        
        // Add to internal log
        this.logs.unshift({
            timestamp,
            category,
            message,
            level
        });
        
        // Keep only last 100 log entries
        if (this.logs.length > 100) {
            this.logs = this.logs.slice(0, 100);
        }
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    formatDuration(seconds) {
        if (seconds < 60) {
            return `${seconds}s`;
        } else if (seconds < 3600) {
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = seconds % 60;
            return `${minutes}m ${remainingSeconds}s`;
        } else {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            return `${hours}h ${minutes}m`;
        }
    }

    /**
     * Cleanup
     */
    destroy() {
        console.log('🧹 Cleaning up dashboard...');
        
        // Stop monitoring
        this.pauseUpdates();
        
        // Disconnect WebSocket
        if (this.socket) {
            this.socket.disconnect();
        }
        
        // Destroy charts
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        
        // Remove event listeners
        document.removeEventListener('visibilitychange', this.handleVisibilityChange);
        window.removeEventListener('online', this.handleOnline);
        window.removeEventListener('offline', this.handleOffline);
    }
}

// Global dashboard instance
let dashboard;

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new ClaudeDashboard();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (dashboard) {
        dashboard.destroy();
    }
});

// Export for external access
window.ClaudeDashboard = ClaudeDashboard;
window.dashboard = dashboard;

// CSS Styles for dashboard enhancements
const dashboardStyles = `
/* Notification system styles */
.notification-container {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 10000;
    max-width: 400px;
}

.notification {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    margin-bottom: 10px;
    opacity: 0;
    transform: translateX(100%);
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.notification.show {
    opacity: 1;
    transform: translateX(0);
}

.notification-info { border-left: 4px solid #0969da; }
.notification-success { border-left: 4px solid #238636; }
.notification-warning { border-left: 4px solid #d29922; }
.notification-error { border-left: 4px solid #da3633; }

.notification-header {
    padding: 10px 15px 5px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.notification-body {
    padding: 0 15px 10px;
    color: #c9d1d9;
    font-size: 0.9em;
}

.notification-close {
    background: none;
    border: none;
    color: #8b949e;
    font-size: 1.5em;
    line-height: 1;
    cursor: pointer;
}

.notification-close:hover {
    color: #c9d1d9;
}

/* Pull to refresh indicator */
.pull-refresh-indicator {
    position: fixed;
    top: -50px;
    left: 50%;
    transform: translateX(-50%);
    background: #161b22;
    color: #c9d1d9;
    padding: 10px 20px;
    border-radius: 0 0 8px 8px;
    border: 1px solid #30363d;
    border-top: none;
    transition: top 0.3s ease;
    z-index: 1000;
}

.pull-refresh-indicator.visible {
    top: 0;
}

/* Refresh indicator */
.refresh-indicator {
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: #161b22;
    color: #c9d1d9;
    padding: 10px 20px;
    border-radius: 8px;
    border: 1px solid #30363d;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    z-index: 10001;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.7; }
    100% { opacity: 1; }
}

/* Mobile optimizations */
@media (max-width: 768px) {
    .notification-container {
        left: 10px;
        right: 10px;
        max-width: none;
    }
    
    .notification {
        font-size: 0.9em;
    }
    
    .card-body {
        padding: 15px;
    }
    
    .table-responsive {
        font-size: 0.85em;
    }
    
    .metric-card {
        margin-bottom: 15px;
    }
}

/* Command execution styles */
.command-result {
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 10px;
    margin-bottom: 10px;
    font-family: monospace;
}

.command-result.success {
    border-left: 4px solid #238636;
}

.command-result.error {
    border-left: 4px solid #da3633;
}

.result-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
    font-weight: bold;
}

.result-body pre {
    background: transparent;
    border: none;
    padding: 0;
    margin: 0;
    white-space: pre-wrap;
    word-wrap: break-word;
}

/* Button states */
.btn.executing {
    position: relative;
    pointer-events: none;
}

.btn.executing::after {
    content: '';
    position: absolute;
    width: 16px;
    height: 16px;
    margin: auto;
    border: 2px solid transparent;
    border-top-color: #ffffff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Chart container improvements */
.chart-container {
    position: relative;
    min-height: 300px;
}

.chart-container canvas {
    max-height: 300px;
}

/* Log entry improvements */
.log-entry {
    transition: background-color 0.2s ease;
}

.log-entry:hover {
    background-color: #262c36;
}

/* Status indicator improvements */
.status-indicator {
    animation: pulse-glow 2s infinite;
}

@keyframes pulse-glow {
    0% { box-shadow: 0 0 0 0 rgba(35, 134, 54, 0.4); }
    70% { box-shadow: 0 0 0 4px rgba(35, 134, 54, 0); }
    100% { box-shadow: 0 0 0 0 rgba(35, 134, 54, 0); }
}

.status-warning {
    animation: pulse-glow-warning 2s infinite;
}

@keyframes pulse-glow-warning {
    0% { box-shadow: 0 0 0 0 rgba(210, 153, 34, 0.4); }
    70% { box-shadow: 0 0 0 4px rgba(210, 153, 34, 0); }
    100% { box-shadow: 0 0 0 0 rgba(210, 153, 34, 0); }
}

.status-critical {
    animation: pulse-glow-critical 1s infinite;
}

@keyframes pulse-glow-critical {
    0% { box-shadow: 0 0 0 0 rgba(218, 54, 51, 0.4); }
    70% { box-shadow: 0 0 0 4px rgba(218, 54, 51, 0); }
    100% { box-shadow: 0 0 0 0 rgba(218, 54, 51, 0); }
}
`;

// Inject CSS styles
const styleSheet = document.createElement('style');
styleSheet.textContent = dashboardStyles;
document.head.appendChild(styleSheet);