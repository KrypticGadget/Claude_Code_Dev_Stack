#!/usr/bin/env node
/**
 * NGROK Manager - Complete tunnel management for Claude Code Dev Stack
 * Handles automatic tunnel creation, persistence, health monitoring, and webhook testing
 */

const { spawn, exec } = require('child_process');
const fs = require('fs').promises;
const path = require('path');
const os = require('os');
const axios = require('axios');
const EventEmitter = require('events');

class NgrokManager extends EventEmitter {
  constructor(options = {}) {
    super();
    this.config = {
      configPath: options.configPath || path.join(__dirname, '../config/ngrok/ngrok-advanced.yml'),
      logPath: options.logPath || path.join(__dirname, '../logs/ngrok.log'),
      pidPath: options.pidPath || path.join(__dirname, '../tmp/ngrok.pid'),
      statusPath: options.statusPath || path.join(__dirname, '../tmp/ngrok-status.json'),
      healthCheckInterval: options.healthCheckInterval || 30000,
      restartDelay: options.restartDelay || 5000,
      maxRestartAttempts: options.maxRestartAttempts || 5,
      tunnels: options.tunnels || ['webapp', 'api', 'websocket', 'terminal', 'backend', 'webhooks'],
      environment: process.env.NODE_ENV || 'development'
    };
    
    this.process = null;
    this.tunnels = new Map();
    this.healthCheckTimer = null;
    this.restartAttempts = 0;
    this.isRunning = false;
    this.startTime = null;
  }

  /**
   * Initialize NGROK manager and start tunnels
   */
  async initialize() {
    try {
      console.log('🚀 Initializing NGROK Manager...');
      
      // Ensure directories exist
      await this.ensureDirectories();
      
      // Load environment variables
      await this.loadEnvironment();
      
      // Validate NGROK installation
      await this.validateNgrokInstallation();
      
      // Start tunnels
      await this.startTunnels();
      
      // Start health monitoring
      this.startHealthMonitoring();
      
      console.log('✅ NGROK Manager initialized successfully');
      this.emit('initialized');
      
    } catch (error) {
      console.error('❌ Failed to initialize NGROK Manager:', error.message);
      this.emit('error', error);
      throw error;
    }
  }

  /**
   * Start NGROK tunnels with advanced configuration
   */
  async startTunnels() {
    try {
      // Stop existing tunnels
      await this.stopTunnels();
      
      console.log('🔄 Starting NGROK tunnels...');
      
      // Build command with configuration
      const cmd = [
        'ngrok',
        'start',
        '--config', this.config.configPath,
        '--log', this.config.logPath,
        '--log-level', process.env.NGROK_LOG_LEVEL || 'info',
        '--log-format', 'json'
      ];
      
      // Add specific tunnels or all
      if (this.config.tunnels.length > 0) {
        cmd.push(...this.config.tunnels);
      } else {
        cmd.push('--all');
      }
      
      // Spawn NGROK process
      this.process = spawn(cmd[0], cmd.slice(1), {
        detached: true,
        stdio: ['ignore', 'pipe', 'pipe'],
        env: { ...process.env }
      });
      
      // Save PID
      await fs.writeFile(this.config.pidPath, this.process.pid.toString());
      
      // Handle process events
      this.process.stdout.on('data', (data) => {
        this.handleLogOutput(data.toString());
      });
      
      this.process.stderr.on('data', (data) => {
        console.error('NGROK Error:', data.toString());
        this.emit('error', new Error(data.toString()));
      });
      
      this.process.on('close', (code) => {
        console.log(`NGROK process exited with code ${code}`);
        this.isRunning = false;
        
        if (code !== 0 && this.restartAttempts < this.config.maxRestartAttempts) {
          console.log(`🔄 Restarting NGROK (attempt ${this.restartAttempts + 1}/${this.config.maxRestartAttempts})...`);
          setTimeout(() => this.restart(), this.config.restartDelay);
        }
        
        this.emit('stopped', code);
      });
      
      this.process.on('error', (error) => {
        console.error('NGROK Process Error:', error);
        this.emit('error', error);
      });
      
      // Wait for tunnels to be ready
      await this.waitForTunnelsReady();
      
      this.isRunning = true;
      this.startTime = new Date();
      this.restartAttempts = 0;
      
      // Fetch and save tunnel information
      await this.fetchTunnelInfo();
      
      console.log('✅ NGROK tunnels started successfully');
      this.emit('started');
      
    } catch (error) {
      console.error('❌ Failed to start NGROK tunnels:', error.message);
      this.emit('error', error);
      throw error;
    }
  }

  /**
   * Stop NGROK tunnels
   */
  async stopTunnels() {
    try {
      console.log('🛑 Stopping NGROK tunnels...');
      
      // Stop health monitoring
      if (this.healthCheckTimer) {
        clearInterval(this.healthCheckTimer);
        this.healthCheckTimer = null;
      }
      
      // Kill existing process
      if (this.process) {
        this.process.kill('SIGTERM');
        this.process = null;
      }
      
      // Try to find and kill existing NGROK processes
      try {
        const pidFile = await fs.readFile(this.config.pidPath, 'utf8');
        const pid = parseInt(pidFile.trim());
        
        if (pid && !isNaN(pid)) {
          process.kill(pid, 'SIGTERM');
        }
      } catch (error) {
        // PID file doesn't exist or process already dead
      }
      
      // Clean up files
      try {
        await fs.unlink(this.config.pidPath);
        await fs.unlink(this.config.statusPath);
      } catch (error) {
        // Files don't exist
      }
      
      this.isRunning = false;
      this.tunnels.clear();
      
      console.log('✅ NGROK tunnels stopped');
      this.emit('stopped');
      
    } catch (error) {
      console.error('❌ Failed to stop NGROK tunnels:', error.message);
      this.emit('error', error);
    }
  }

  /**
   * Restart NGROK tunnels
   */
  async restart() {
    this.restartAttempts++;
    
    try {
      await this.stopTunnels();
      await new Promise(resolve => setTimeout(resolve, 2000));
      await this.startTunnels();
    } catch (error) {
      console.error('❌ Failed to restart NGROK:', error.message);
      this.emit('error', error);
    }
  }

  /**
   * Start health monitoring for tunnels
   */
  startHealthMonitoring() {
    if (this.healthCheckTimer) {
      clearInterval(this.healthCheckTimer);
    }
    
    this.healthCheckTimer = setInterval(async () => {
      try {
        await this.performHealthCheck();
      } catch (error) {
        console.error('Health check failed:', error.message);
        this.emit('health-check-failed', error);
      }
    }, this.config.healthCheckInterval);
    
    console.log('💓 Health monitoring started');
  }

  /**
   * Perform health check on all tunnels
   */
  async performHealthCheck() {
    try {
      // Check NGROK API
      const apiResponse = await axios.get('http://127.0.0.1:4040/api/tunnels', {
        timeout: 5000
      });
      
      const activeTunnels = apiResponse.data.tunnels || [];
      const tunnelStatus = new Map();
      
      // Check each tunnel
      for (const tunnel of activeTunnels) {
        const status = {
          name: tunnel.name,
          url: tunnel.public_url,
          proto: tunnel.proto,
          addr: tunnel.config.addr,
          status: 'healthy',
          lastCheck: new Date().toISOString(),
          metrics: tunnel.metrics || {}
        };
        
        // Test tunnel connectivity
        try {
          const testUrl = tunnel.public_url + '/health';
          const response = await axios.get(testUrl, {
            timeout: 3000,
            validateStatus: () => true // Accept any status
          });
          
          status.httpStatus = response.status;
          status.responseTime = response.headers['x-response-time'] || 'unknown';
          
        } catch (error) {
          status.status = 'unhealthy';
          status.error = error.message;
        }
        
        tunnelStatus.set(tunnel.name, status);
      }
      
      // Update tunnel information
      this.tunnels = tunnelStatus;
      
      // Save status to file
      await this.saveStatus();
      
      // Emit health check event
      this.emit('health-check', {
        timestamp: new Date().toISOString(),
        tunnels: Array.from(tunnelStatus.values()),
        healthy: Array.from(tunnelStatus.values()).filter(t => t.status === 'healthy').length,
        total: tunnelStatus.size
      });
      
    } catch (error) {
      console.error('Health check error:', error.message);
      
      // If NGROK API is not responding, try to restart
      if (error.code === 'ECONNREFUSED') {
        console.log('🔄 NGROK API not responding, attempting restart...');
        await this.restart();
      }
      
      throw error;
    }
  }

  /**
   * Fetch tunnel information from NGROK API
   */
  async fetchTunnelInfo() {
    try {
      const response = await axios.get('http://127.0.0.1:4040/api/tunnels', {
        timeout: 5000
      });
      
      const tunnels = response.data.tunnels || [];
      
      for (const tunnel of tunnels) {
        this.tunnels.set(tunnel.name, {
          name: tunnel.name,
          url: tunnel.public_url,
          proto: tunnel.proto,
          addr: tunnel.config.addr,
          status: 'active',
          started: new Date().toISOString()
        });
      }
      
      await this.saveStatus();
      
      // Display tunnel URLs
      console.log('\\n🔗 Active Tunnels:');
      for (const [name, info] of this.tunnels) {
        console.log(`   ${name}: ${info.url} -> ${info.addr}`);
      }
      console.log('');
      
    } catch (error) {
      console.error('Failed to fetch tunnel info:', error.message);
    }
  }

  /**
   * Wait for tunnels to be ready
   */
  async waitForTunnelsReady(timeout = 30000) {
    const startTime = Date.now();
    
    while (Date.now() - startTime < timeout) {
      try {
        await axios.get('http://127.0.0.1:4040/api/tunnels', { timeout: 2000 });
        return; // API is responding
      } catch (error) {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
    
    throw new Error('Timeout waiting for NGROK tunnels to be ready');
  }

  /**
   * Handle log output from NGROK process
   */
  handleLogOutput(data) {
    const lines = data.split('\\n').filter(line => line.trim());
    
    for (const line of lines) {
      try {
        const logEntry = JSON.parse(line);
        
        if (logEntry.msg && logEntry.msg.includes('started tunnel')) {
          console.log(`✅ Tunnel started: ${logEntry.url || 'unknown'}`);
          this.emit('tunnel-started', logEntry);
        }
        
        if (logEntry.lvl === 'eror' || logEntry.level === 'error') {
          console.error('NGROK Error:', logEntry.msg || logEntry.message);
          this.emit('tunnel-error', logEntry);
        }
        
      } catch (error) {
        // Not JSON log, just output as is
        if (data.includes('http://') || data.includes('https://')) {
          console.log('NGROK:', data.trim());
        }
      }
    }
  }

  /**
   * Save current status to file
   */
  async saveStatus() {
    const status = {
      timestamp: new Date().toISOString(),
      uptime: this.startTime ? Date.now() - this.startTime.getTime() : 0,
      isRunning: this.isRunning,
      pid: this.process ? this.process.pid : null,
      restartAttempts: this.restartAttempts,
      tunnels: Array.from(this.tunnels.values()),
      config: {
        environment: this.config.environment,
        healthCheckInterval: this.config.healthCheckInterval,
        configPath: this.config.configPath
      }
    };
    
    try {
      await fs.writeFile(this.config.statusPath, JSON.stringify(status, null, 2));
    } catch (error) {
      console.error('Failed to save status:', error.message);
    }
  }

  /**
   * Get current status
   */
  async getStatus() {
    try {
      const statusFile = await fs.readFile(this.config.statusPath, 'utf8');
      return JSON.parse(statusFile);
    } catch (error) {
      return {
        timestamp: new Date().toISOString(),
        isRunning: this.isRunning,
        tunnels: Array.from(this.tunnels.values()),
        error: 'No status file found'
      };
    }
  }

  /**
   * Get tunnel URLs
   */
  getTunnelUrls() {
    const urls = {};
    for (const [name, info] of this.tunnels) {
      urls[name] = info.url;
    }
    return urls;
  }

  /**
   * Ensure required directories exist
   */
  async ensureDirectories() {
    const dirs = [
      path.dirname(this.config.logPath),
      path.dirname(this.config.pidPath),
      path.dirname(this.config.statusPath),
      path.dirname(this.config.configPath)
    ];
    
    for (const dir of dirs) {
      try {
        await fs.mkdir(dir, { recursive: true });
      } catch (error) {
        // Directory already exists
      }
    }
  }

  /**
   * Load environment variables
   */
  async loadEnvironment() {
    // Load .env file if it exists
    const envPath = path.join(__dirname, '../.env');
    
    try {
      const envContent = await fs.readFile(envPath, 'utf8');
      const envVars = envContent.split('\\n').filter(line => line.includes('='));
      
      for (const line of envVars) {
        const [key, ...values] = line.split('=');
        if (key && values.length > 0) {
          process.env[key.trim()] = values.join('=').trim();
        }
      }
    } catch (error) {
      // .env file doesn't exist, use defaults
    }
    
    // Set default environment variables
    const defaults = {
      NGROK_AUTHTOKEN: process.env.NGROK_AUTHTOKEN || '',
      NGROK_REGION: process.env.NGROK_REGION || 'us',
      CLAUDE_WEBAPP_PORT: process.env.CLAUDE_WEBAPP_PORT || '3000',
      CLAUDE_API_PORT: process.env.CLAUDE_API_PORT || '3001',
      CLAUDE_WS_PORT: process.env.CLAUDE_WS_PORT || '3002',
      CLAUDE_TERMINAL_PORT: process.env.CLAUDE_TERMINAL_PORT || '3003',
      CLAUDE_BACKEND_PORT: process.env.CLAUDE_BACKEND_PORT || '8000',
      CLAUDE_WEBHOOK_PORT: process.env.CLAUDE_WEBHOOK_PORT || '4000'
    };
    
    for (const [key, value] of Object.entries(defaults)) {
      if (!process.env[key]) {
        process.env[key] = value;
      }
    }
  }

  /**
   * Validate NGROK installation
   */
  async validateNgrokInstallation() {
    return new Promise((resolve, reject) => {
      exec('ngrok version', (error, stdout, stderr) => {
        if (error) {
          reject(new Error('NGROK is not installed or not in PATH. Please install NGROK first.'));
        } else {
          console.log('✅ NGROK version:', stdout.trim());
          resolve(stdout.trim());
        }
      });
    });
  }

  /**
   * Cleanup on exit
   */
  async cleanup() {
    console.log('🧹 Cleaning up NGROK Manager...');
    await this.stopTunnels();
  }
}

// CLI interface
if (require.main === module) {
  const manager = new NgrokManager();
  
  // Handle command line arguments
  const command = process.argv[2];
  
  switch (command) {
    case 'start':
      manager.initialize().catch(console.error);
      break;
      
    case 'stop':
      manager.stopTunnels().catch(console.error);
      break;
      
    case 'restart':
      manager.restart().catch(console.error);
      break;
      
    case 'status':
      manager.getStatus().then(status => {
        console.log(JSON.stringify(status, null, 2));
      }).catch(console.error);
      break;
      
    case 'urls':
      manager.initialize().then(() => {
        console.log(JSON.stringify(manager.getTunnelUrls(), null, 2));
      }).catch(console.error);
      break;
      
    default:
      console.log(`
Usage: node ngrok-manager.js <command>

Commands:
  start    - Start NGROK tunnels
  stop     - Stop NGROK tunnels  
  restart  - Restart NGROK tunnels
  status   - Show current status
  urls     - Show tunnel URLs

Environment Variables:
  NGROK_AUTHTOKEN - Your NGROK auth token
  NGROK_REGION    - NGROK region (default: us)
  NODE_ENV        - Environment (development/production)
      `);
  }
  
  // Handle graceful shutdown
  process.on('SIGINT', async () => {
    console.log('\\n🛑 Received SIGINT, shutting down...');
    await manager.cleanup();
    process.exit(0);
  });
  
  process.on('SIGTERM', async () => {
    console.log('\\n🛑 Received SIGTERM, shutting down...');
    await manager.cleanup();
    process.exit(0);
  });
}

module.exports = NgrokManager;