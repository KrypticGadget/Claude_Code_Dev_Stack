#!/usr/bin/env node
/**
 * NGROK Health Monitor - Advanced monitoring and alerting for NGROK tunnels
 * Provides comprehensive health checking, performance monitoring, and automated recovery
 */

const axios = require('axios');
const fs = require('fs').promises;
const path = require('path');
const EventEmitter = require('events');

class NgrokHealthMonitor extends EventEmitter {
  constructor(options = {}) {
    super();
    
    this.config = {
      ngrokApiUrl: options.ngrokApiUrl || 'http://127.0.0.1:4040/api',
      checkInterval: options.checkInterval || 30000, // 30 seconds
      alertThreshold: options.alertThreshold || 3, // Consecutive failures
      responseTimeThreshold: options.responseTimeThreshold || 5000, // 5 seconds
      statusFile: options.statusFile || path.join(__dirname, '../tmp/ngrok-health.json'),
      alertsFile: options.alertsFile || path.join(__dirname, '../logs/ngrok-alerts.log'),
      performanceFile: options.performanceFile || path.join(__dirname, '../logs/ngrok-performance.jsonl'),
      enableSlackAlerts: options.enableSlackAlerts || false,
      slackWebhookUrl: options.slackWebhookUrl || process.env.SLACK_WEBHOOK_URL,
      enableEmailAlerts: options.enableEmailAlerts || false,
      maxRetries: options.maxRetries || 3,
      retryDelay: options.retryDelay || 5000
    };
    
    this.tunnels = new Map();
    this.alerts = new Map();
    this.performanceData = [];
    this.monitoringActive = false;
    this.checkTimer = null;
  }

  /**
   * Start health monitoring
   */
  async start() {
    try {
      console.log('💓 Starting NGROK Health Monitor...');
      
      // Ensure directories exist
      await this.ensureDirectories();
      
      // Load previous state if exists
      await this.loadPreviousState();
      
      // Start monitoring loop
      this.startMonitoringLoop();
      
      console.log('✅ NGROK Health Monitor started');
      this.emit('started');
      
    } catch (error) {
      console.error('❌ Failed to start health monitor:', error.message);
      this.emit('error', error);
      throw error;
    }
  }

  /**
   * Stop health monitoring
   */
  async stop() {
    console.log('🛑 Stopping NGROK Health Monitor...');
    
    this.monitoringActive = false;
    
    if (this.checkTimer) {
      clearInterval(this.checkTimer);
      this.checkTimer = null;
    }
    
    // Save final state
    await this.saveState();
    
    console.log('✅ NGROK Health Monitor stopped');
    this.emit('stopped');
  }

  /**
   * Start the monitoring loop
   */
  startMonitoringLoop() {
    this.monitoringActive = true;
    
    // Run initial check
    this.performHealthCheck();
    
    // Set up periodic checks
    this.checkTimer = setInterval(() => {
      if (this.monitoringActive) {
        this.performHealthCheck();
      }
    }, this.config.checkInterval);
    
    console.log(`🔄 Health checks scheduled every ${this.config.checkInterval / 1000} seconds`);
  }

  /**
   * Perform comprehensive health check
   */
  async performHealthCheck() {
    const checkStartTime = Date.now();
    
    try {
      console.log('🔍 Performing health check...');
      
      // 1. Check NGROK API availability
      const apiHealth = await this.checkNgrokApi();
      
      if (!apiHealth.healthy) {
        await this.handleApiFailure(apiHealth);
        return;
      }
      
      // 2. Get tunnel information
      const tunnelsInfo = await this.getTunnelsInfo();
      
      // 3. Check each tunnel
      const tunnelResults = await this.checkAllTunnels(tunnelsInfo);
      
      // 4. Analyze results
      await this.analyzeResults(tunnelResults);
      
      // 5. Update performance metrics
      await this.updatePerformanceMetrics(checkStartTime, tunnelResults);
      
      // 6. Save state
      await this.saveState();
      
      console.log(`✅ Health check completed in ${Date.now() - checkStartTime}ms`);
      
    } catch (error) {
      console.error('❌ Health check failed:', error.message);
      await this.handleHealthCheckFailure(error);
    }
  }

  /**
   * Check NGROK API availability
   */
  async checkNgrokApi() {
    try {
      const startTime = Date.now();
      const response = await axios.get(`${this.config.ngrokApiUrl}/tunnels`, {
        timeout: 10000
      });
      
      const responseTime = Date.now() - startTime;
      
      return {
        healthy: response.status === 200,
        responseTime,
        status: response.status,
        data: response.data
      };
      
    } catch (error) {
      return {
        healthy: false,
        error: error.message,
        code: error.code
      };
    }
  }

  /**
   * Get tunnels information from NGROK API
   */
  async getTunnelsInfo() {
    try {
      const response = await axios.get(`${this.config.ngrokApiUrl}/tunnels`, {
        timeout: 5000
      });
      
      return response.data.tunnels || [];
      
    } catch (error) {
      console.error('Failed to get tunnels info:', error.message);
      return [];
    }
  }

  /**
   * Check all tunnels health
   */
  async checkAllTunnels(tunnelsInfo) {
    const results = [];
    
    for (const tunnel of tunnelsInfo) {
      try {
        const result = await this.checkTunnelHealth(tunnel);
        results.push(result);
      } catch (error) {
        results.push({
          name: tunnel.name,
          url: tunnel.public_url,
          healthy: false,
          error: error.message
        });
      }
    }
    
    return results;
  }

  /**
   * Check individual tunnel health
   */
  async checkTunnelHealth(tunnel) {
    const startTime = Date.now();
    
    try {
      // Try to access the tunnel URL with a health check endpoint
      const healthUrl = `${tunnel.public_url}/health`;
      
      const response = await axios.get(healthUrl, {
        timeout: this.config.responseTimeThreshold,
        validateStatus: (status) => status < 500 // Accept 4xx but not 5xx
      });
      
      const responseTime = Date.now() - startTime;
      
      const result = {
        name: tunnel.name,
        url: tunnel.public_url,
        proto: tunnel.proto,
        addr: tunnel.config.addr,
        healthy: response.status < 400,
        statusCode: response.status,
        responseTime,
        timestamp: new Date().toISOString(),
        metrics: tunnel.metrics || {}
      };
      
      // Update tunnel state
      this.updateTunnelState(tunnel.name, result);
      
      return result;
      
    } catch (error) {
      const responseTime = Date.now() - startTime;
      
      const result = {
        name: tunnel.name,
        url: tunnel.public_url,
        proto: tunnel.proto,
        addr: tunnel.config.addr,
        healthy: false,
        error: error.message,
        errorCode: error.code,
        responseTime,
        timestamp: new Date().toISOString()
      };
      
      this.updateTunnelState(tunnel.name, result);
      
      return result;
    }
  }

  /**
   * Update tunnel state and track failures
   */
  updateTunnelState(tunnelName, result) {
    const existing = this.tunnels.get(tunnelName) || {
      consecutiveFailures: 0,
      totalChecks: 0,
      totalFailures: 0,
      lastSuccess: null,
      lastFailure: null,
      averageResponseTime: 0
    };
    
    existing.totalChecks++;
    existing.lastCheck = result.timestamp;
    existing.lastResult = result;
    
    if (result.healthy) {
      existing.consecutiveFailures = 0;
      existing.lastSuccess = result.timestamp;
      
      // Update average response time
      if (existing.averageResponseTime === 0) {
        existing.averageResponseTime = result.responseTime;
      } else {
        existing.averageResponseTime = (existing.averageResponseTime + result.responseTime) / 2;
      }
    } else {
      existing.consecutiveFailures++;
      existing.totalFailures++;
      existing.lastFailure = result.timestamp;
      existing.lastError = result.error || 'Unknown error';
    }
    
    this.tunnels.set(tunnelName, existing);
  }

  /**
   * Analyze health check results and trigger alerts
   */
  async analyzeResults(results) {
    for (const result of results) {
      const tunnelState = this.tunnels.get(result.name);
      
      if (!tunnelState) continue;
      
      // Check for alert conditions
      if (tunnelState.consecutiveFailures >= this.config.alertThreshold) {
        await this.triggerAlert('tunnel_down', {
          tunnel: result.name,
          url: result.url,
          consecutiveFailures: tunnelState.consecutiveFailures,
          lastError: tunnelState.lastError,
          timestamp: result.timestamp
        });
      }
      
      // Check for performance issues
      if (result.healthy && result.responseTime > this.config.responseTimeThreshold) {
        await this.triggerAlert('slow_response', {
          tunnel: result.name,
          url: result.url,
          responseTime: result.responseTime,
          threshold: this.config.responseTimeThreshold,
          timestamp: result.timestamp
        });
      }
      
      // Check for recovery
      if (result.healthy && tunnelState.consecutiveFailures === 0 && tunnelState.lastFailure) {
        const lastFailure = new Date(tunnelState.lastFailure);
        const now = new Date();
        
        if (now - lastFailure < this.config.checkInterval * 2) {
          await this.triggerAlert('tunnel_recovered', {
            tunnel: result.name,
            url: result.url,
            downtime: now - lastFailure,
            timestamp: result.timestamp
          });
        }
      }
    }
  }

  /**
   * Trigger an alert
   */
  async triggerAlert(type, data) {
    const alert = {
      id: `${type}_${data.tunnel}_${Date.now()}`,
      type,
      data,
      timestamp: new Date().toISOString(),
      notified: false
    };
    
    // Check if we already have a recent alert of this type for this tunnel
    const recentAlert = Array.from(this.alerts.values()).find(a => 
      a.type === type && 
      a.data.tunnel === data.tunnel && 
      (Date.now() - new Date(a.timestamp).getTime()) < 300000 // 5 minutes
    );
    
    if (recentAlert && type !== 'tunnel_recovered') {
      return; // Don't spam alerts
    }
    
    this.alerts.set(alert.id, alert);
    
    // Log alert
    await this.logAlert(alert);
    
    // Send notifications
    await this.sendNotifications(alert);
    
    console.log(`🚨 Alert triggered: ${type} for ${data.tunnel}`);
    this.emit('alert', alert);
  }

  /**
   * Log alert to file
   */
  async logAlert(alert) {
    try {
      const logLine = JSON.stringify(alert) + '\\n';
      await fs.appendFile(this.config.alertsFile, logLine);
    } catch (error) {
      console.error('Failed to log alert:', error);
    }
  }

  /**
   * Send notifications for alerts
   */
  async sendNotifications(alert) {
    try {
      // Slack notification
      if (this.config.enableSlackAlerts && this.config.slackWebhookUrl) {
        await this.sendSlackNotification(alert);
      }
      
      // Email notification (if configured)
      if (this.config.enableEmailAlerts) {
        await this.sendEmailNotification(alert);
      }
      
      alert.notified = true;
      
    } catch (error) {
      console.error('Failed to send notifications:', error);
    }
  }

  /**
   * Send Slack notification
   */
  async sendSlackNotification(alert) {
    try {
      const message = this.formatSlackMessage(alert);
      
      await axios.post(this.config.slackWebhookUrl, {
        text: message.text,
        attachments: message.attachments
      }, {
        timeout: 10000
      });
      
      console.log('📱 Slack notification sent');
      
    } catch (error) {
      console.error('Failed to send Slack notification:', error);
    }
  }

  /**
   * Format Slack message
   */
  formatSlackMessage(alert) {
    const { type, data } = alert;
    
    let color = 'warning';
    let emoji = '⚠️';
    let title = 'NGROK Alert';
    
    switch (type) {
      case 'tunnel_down':
        color = 'danger';
        emoji = '🔴';
        title = 'Tunnel Down';
        break;
      case 'slow_response':
        color = 'warning';
        emoji = '🐌';
        title = 'Slow Response';
        break;
      case 'tunnel_recovered':
        color = 'good';
        emoji = '✅';
        title = 'Tunnel Recovered';
        break;
    }
    
    return {
      text: `${emoji} ${title}: ${data.tunnel}`,
      attachments: [{
        color,
        fields: [
          {
            title: 'Tunnel',
            value: data.tunnel,
            short: true
          },
          {
            title: 'URL',
            value: data.url || 'N/A',
            short: true
          },
          {
            title: 'Details',
            value: this.getAlertDetails(alert),
            short: false
          },
          {
            title: 'Timestamp',
            value: new Date(alert.timestamp).toLocaleString(),
            short: true
          }
        ]
      }]
    };
  }

  /**
   * Get alert details based on type
   */
  getAlertDetails(alert) {
    const { type, data } = alert;
    
    switch (type) {
      case 'tunnel_down':
        return `Consecutive failures: ${data.consecutiveFailures}\\nLast error: ${data.lastError}`;
      case 'slow_response':
        return `Response time: ${data.responseTime}ms (threshold: ${data.threshold}ms)`;
      case 'tunnel_recovered':
        return `Downtime: ${Math.round(data.downtime / 1000)}s`;
      default:
        return 'No additional details';
    }
  }

  /**
   * Update performance metrics
   */
  async updatePerformanceMetrics(checkStartTime, results) {
    const metrics = {
      timestamp: new Date().toISOString(),
      checkDuration: Date.now() - checkStartTime,
      totalTunnels: results.length,
      healthyTunnels: results.filter(r => r.healthy).length,
      unhealthyTunnels: results.filter(r => !r.healthy).length,
      averageResponseTime: results.reduce((sum, r) => sum + (r.responseTime || 0), 0) / results.length,
      tunnels: results.map(r => ({
        name: r.name,
        healthy: r.healthy,
        responseTime: r.responseTime,
        statusCode: r.statusCode
      }))
    };
    
    this.performanceData.push(metrics);
    
    // Keep only last 1000 entries
    if (this.performanceData.length > 1000) {
      this.performanceData = this.performanceData.slice(-1000);
    }
    
    // Save to file
    try {
      const logLine = JSON.stringify(metrics) + '\\n';
      await fs.appendFile(this.config.performanceFile, logLine);
    } catch (error) {
      console.error('Failed to save performance metrics:', error);
    }
  }

  /**
   * Handle NGROK API failure
   */
  async handleApiFailure(apiHealth) {
    console.error('❌ NGROK API is not responding');
    
    await this.triggerAlert('api_failure', {
      error: apiHealth.error,
      code: apiHealth.code,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Handle health check failure
   */
  async handleHealthCheckFailure(error) {
    console.error('❌ Health check system failure:', error.message);
    
    await this.triggerAlert('monitor_failure', {
      error: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Get current status
   */
  getStatus() {
    const tunnelStats = Array.from(this.tunnels.entries()).map(([name, state]) => ({
      name,
      healthy: state.consecutiveFailures === 0,
      consecutiveFailures: state.consecutiveFailures,
      totalChecks: state.totalChecks,
      totalFailures: state.totalFailures,
      successRate: ((state.totalChecks - state.totalFailures) / state.totalChecks * 100).toFixed(2),
      averageResponseTime: Math.round(state.averageResponseTime),
      lastCheck: state.lastCheck,
      lastSuccess: state.lastSuccess,
      lastFailure: state.lastFailure
    }));
    
    const recentAlerts = Array.from(this.alerts.values())
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
      .slice(0, 10);
    
    return {
      timestamp: new Date().toISOString(),
      monitoring: this.monitoringActive,
      tunnels: tunnelStats,
      alerts: {
        total: this.alerts.size,
        recent: recentAlerts
      },
      performance: {
        totalChecks: this.performanceData.length,
        lastCheck: this.performanceData.length > 0 ? this.performanceData[this.performanceData.length - 1] : null
      }
    };
  }

  /**
   * Save current state to file
   */
  async saveState() {
    try {
      const state = this.getStatus();
      await fs.writeFile(this.config.statusFile, JSON.stringify(state, null, 2));
    } catch (error) {
      console.error('Failed to save state:', error);
    }
  }

  /**
   * Load previous state from file
   */
  async loadPreviousState() {
    try {
      const stateData = await fs.readFile(this.config.statusFile, 'utf8');
      const state = JSON.parse(stateData);
      
      // Restore tunnel states
      if (state.tunnels) {
        for (const tunnel of state.tunnels) {
          this.tunnels.set(tunnel.name, {
            consecutiveFailures: tunnel.consecutiveFailures,
            totalChecks: tunnel.totalChecks,
            totalFailures: tunnel.totalFailures,
            averageResponseTime: tunnel.averageResponseTime,
            lastCheck: tunnel.lastCheck,
            lastSuccess: tunnel.lastSuccess,
            lastFailure: tunnel.lastFailure
          });
        }
      }
      
      console.log(`📊 Loaded previous state: ${this.tunnels.size} tunnels`);
      
    } catch (error) {
      console.log('📝 No previous state found, starting fresh');
    }
  }

  /**
   * Ensure required directories exist
   */
  async ensureDirectories() {
    const dirs = [
      path.dirname(this.config.statusFile),
      path.dirname(this.config.alertsFile),
      path.dirname(this.config.performanceFile)
    ];
    
    for (const dir of dirs) {
      try {
        await fs.mkdir(dir, { recursive: true });
      } catch (error) {
        // Directory already exists
      }
    }
  }
}

// CLI interface
if (require.main === module) {
  const monitor = new NgrokHealthMonitor();
  
  const command = process.argv[2];
  
  switch (command) {
    case 'start':
      monitor.start().catch(console.error);
      break;
      
    case 'stop':
      monitor.stop().then(() => process.exit(0)).catch(console.error);
      break;
      
    case 'status':
      monitor.loadPreviousState().then(() => {
        console.log(JSON.stringify(monitor.getStatus(), null, 2));
      }).catch(console.error);
      break;
      
    default:
      console.log(`
Usage: node ngrok-health-monitor.js <command>

Commands:
  start    - Start health monitoring
  stop     - Stop health monitoring
  status   - Show current status

Environment Variables:
  SLACK_WEBHOOK_URL  - Slack webhook for alerts
      `);
  }
  
  // Handle graceful shutdown
  process.on('SIGINT', async () => {
    console.log('\\n🛑 Received SIGINT, shutting down...');
    await monitor.stop();
    process.exit(0);
  });
  
  process.on('SIGTERM', async () => {
    console.log('\\n🛑 Received SIGTERM, shutting down...');
    await monitor.stop();
    process.exit(0);
  });
}

module.exports = NgrokHealthMonitor;