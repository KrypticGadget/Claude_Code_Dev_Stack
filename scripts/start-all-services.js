#!/usr/bin/env node
/**
 * Start All Services Script for Claude Code Dev Stack
 * Orchestrates startup of all services with NGROK integration
 */

const { spawn, exec } = require('child_process');
const path = require('path');
const fs = require('fs').promises;
const axios = require('axios');

const NgrokManager = require('./ngrok-manager');
const WebhookServer = require('./webhook-server');

class ServiceOrchestrator {
  constructor() {
    this.services = new Map();
    this.ngrokManager = null;
    this.webhookServer = null;
    this.isShuttingDown = false;
    
    this.serviceConfigs = [
      {
        name: 'webapp',
        description: 'React PWA Frontend',
        command: 'npm',
        args: ['run', 'dev'],
        cwd: path.join(__dirname, '../ui/react-pwa'),
        port: 3000,
        healthCheck: 'http://localhost:3000',
        autoRestart: true,
        essential: true
      },
      {
        name: 'api',
        description: 'API Server',
        command: 'node',
        args: [path.join(__dirname, '../server/unified-server.js')],
        cwd: __dirname,
        port: 8000,
        healthCheck: 'http://localhost:8000/health',
        autoRestart: true,
        essential: true
      },
      {
        name: 'websocket',
        description: 'WebSocket Server',
        command: 'node',
        args: [path.join(__dirname, '../server/websocket-server.js')],
        cwd: __dirname,
        port: 3002,
        healthCheck: 'ws://localhost:3002',
        autoRestart: true,
        essential: false
      },
      {
        name: 'terminal',
        description: 'Terminal Server',
        command: 'node',
        args: [path.join(__dirname, '../server/terminal-server.js')],
        cwd: __dirname,
        port: 3003,
        healthCheck: 'http://localhost:3003/health',
        autoRestart: true,
        essential: false
      },
      {
        name: 'webhooks',
        description: 'Webhook Testing Server',
        command: 'node',
        args: [path.join(__dirname, './webhook-server.js')],
        cwd: __dirname,
        port: 4000,
        healthCheck: 'http://localhost:4000/health',
        autoRestart: true,
        essential: false
      }
    ];
  }

  /**
   * Start all services in the correct order
   */
  async startAll() {
    try {
      console.log('🚀 Starting Claude Code Dev Stack v3.6.9...');
      console.log('════════════════════════════════════════════════');
      
      // 1. Start core services first
      await this.startCoreServices();
      
      // 2. Wait for services to be ready
      await this.waitForServicesReady();
      
      // 3. Start webhook server
      await this.startWebhookServer();
      
      // 4. Start NGROK tunnels
      await this.startNgrokTunnels();
      
      // 5. Display status
      await this.displayStatus();
      
      // 6. Start health monitoring
      this.startHealthMonitoring();
      
      console.log('✅ All services started successfully!');
      console.log('════════════════════════════════════════════════');
      
    } catch (error) {
      console.error('❌ Failed to start services:', error.message);
      await this.stopAll();
      process.exit(1);
    }
  }

  /**
   * Start core services
   */
  async startCoreServices() {
    console.log('📦 Starting core services...');
    
    for (const config of this.serviceConfigs) {
      if (config.essential) {
        await this.startService(config);
        
        // Wait a bit between essential services
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    }
    
    // Start non-essential services
    for (const config of this.serviceConfigs) {
      if (!config.essential && config.name !== 'webhooks') {
        await this.startService(config);
      }
    }
  }

  /**
   * Start a single service
   */
  async startService(config) {
    try {
      console.log(`  🔄 Starting ${config.name} (${config.description})...`);
      
      // Check if port is already in use
      const isPortFree = await this.checkPort(config.port);
      if (!isPortFree) {
        console.log(`  ⚠️  Port ${config.port} already in use for ${config.name}`);
        return;
      }
      
      const process = spawn(config.command, config.args, {
        cwd: config.cwd,
        stdio: ['ignore', 'pipe', 'pipe'],
        env: {
          ...process.env,
          PORT: config.port,
          NODE_ENV: process.env.NODE_ENV || 'development'
        }
      });
      
      const serviceInfo = {
        ...config,
        process,
        startTime: new Date(),
        status: 'starting',
        restarts: 0
      };
      
      // Handle process output
      process.stdout.on('data', (data) => {
        const output = data.toString().trim();
        if (output) {
          console.log(`  [${config.name}] ${output}`);
        }
      });
      
      process.stderr.on('data', (data) => {
        const output = data.toString().trim();
        if (output && !output.includes('warning')) {
          console.error(`  [${config.name}] ERROR: ${output}`);
        }
      });
      
      process.on('close', (code) => {
        console.log(`  [${config.name}] Process exited with code ${code}`);
        serviceInfo.status = 'stopped';
        
        if (code !== 0 && config.autoRestart && !this.isShuttingDown) {
          this.restartService(config.name);
        }
      });
      
      process.on('error', (error) => {
        console.error(`  [${config.name}] Process error:`, error.message);
        serviceInfo.status = 'error';
      });
      
      this.services.set(config.name, serviceInfo);
      serviceInfo.status = 'running';
      
      console.log(`  ✅ ${config.name} started on port ${config.port}`);
      
    } catch (error) {
      console.error(`  ❌ Failed to start ${config.name}:`, error.message);
      throw error;
    }
  }

  /**
   * Start webhook server using the class
   */
  async startWebhookServer() {
    try {
      console.log('🪝 Starting webhook server...');
      
      this.webhookServer = new WebhookServer({
        port: 4000
      });
      
      await this.webhookServer.start();
      console.log('  ✅ Webhook server started on port 4000');
      
    } catch (error) {
      console.error('  ❌ Failed to start webhook server:', error.message);
      throw error;
    }
  }

  /**
   * Start NGROK tunnels
   */
  async startNgrokTunnels() {
    try {
      console.log('🌐 Starting NGROK tunnels...');
      
      this.ngrokManager = new NgrokManager({
        configPath: path.join(__dirname, '../config/ngrok/ngrok-advanced.yml'),
        tunnels: ['webapp', 'api', 'websocket', 'terminal', 'backend', 'webhooks']
      });
      
      // Listen for events
      this.ngrokManager.on('started', () => {
        console.log('  ✅ NGROK tunnels started successfully');
      });
      
      this.ngrokManager.on('error', (error) => {
        console.error('  ❌ NGROK error:', error.message);
      });
      
      this.ngrokManager.on('tunnel-started', (tunnel) => {
        console.log(`  🔗 Tunnel started: ${tunnel.url || 'unknown'}`);
      });
      
      await this.ngrokManager.initialize();
      
    } catch (error) {
      console.error('  ❌ Failed to start NGROK tunnels:', error.message);
      // Don't throw error here - NGROK is optional
      console.log('  ⚠️  Continuing without NGROK tunnels');
    }
  }

  /**
   * Wait for services to be ready
   */
  async waitForServicesReady(timeout = 60000) {
    console.log('⏳ Waiting for services to be ready...');
    
    const startTime = Date.now();
    const readyServices = new Set();
    
    while (Date.now() - startTime < timeout) {
      for (const [name, service] of this.services) {
        if (readyServices.has(name)) continue;
        
        try {
          if (service.healthCheck.startsWith('http')) {
            await axios.get(service.healthCheck, { timeout: 2000 });
          }
          
          readyServices.add(name);
          console.log(`  ✅ ${name} is ready`);
          
        } catch (error) {
          // Service not ready yet
        }
      }
      
      if (readyServices.size === this.services.size) {
        console.log('  🎉 All services are ready!');
        return;
      }
      
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    const notReady = Array.from(this.services.keys()).filter(name => !readyServices.has(name));
    if (notReady.length > 0) {
      console.log(`  ⚠️  Services not ready: ${notReady.join(', ')}`);
    }
  }

  /**
   * Display current status
   */
  async displayStatus() {
    console.log('\\n📊 Service Status:');
    console.log('══════════════════');
    
    for (const [name, service] of this.services) {
      const uptime = Math.floor((Date.now() - service.startTime.getTime()) / 1000);
      const status = service.status === 'running' ? '🟢' : 
                   service.status === 'starting' ? '🟡' : '🔴';
      
      console.log(`${status} ${name.padEnd(12)} | Port: ${service.port} | Uptime: ${uptime}s | PID: ${service.process.pid}`);
    }
    
    // Display NGROK URLs if available
    if (this.ngrokManager && this.ngrokManager.isRunning) {
      console.log('\\n🌐 NGROK Tunnels:');
      console.log('═════════════════');
      
      const urls = this.ngrokManager.getTunnelUrls();
      for (const [name, url] of Object.entries(urls)) {
        console.log(`🔗 ${name.padEnd(12)} | ${url}`);
      }
    }
    
    console.log('\\n💡 Quick Access:');
    console.log('════════════════');
    console.log('  Web App:       http://localhost:3000');
    console.log('  API:           http://localhost:8000');
    console.log('  WebSocket:     ws://localhost:3002');
    console.log('  Terminal:      http://localhost:3003');
    console.log('  Webhooks:      http://localhost:4000');
    console.log('  NGROK Status:  http://localhost:4040');
    console.log('');
  }

  /**
   * Start health monitoring
   */
  startHealthMonitoring() {
    console.log('💓 Starting health monitoring...');
    
    setInterval(async () => {
      await this.performHealthCheck();
    }, 30000); // Check every 30 seconds
  }

  /**
   * Perform health check on all services
   */
  async performHealthCheck() {
    for (const [name, service] of this.services) {
      try {
        if (service.healthCheck.startsWith('http')) {
          await axios.get(service.healthCheck, { timeout: 5000 });
          service.status = 'running';
        }
      } catch (error) {
        console.error(`⚠️  Health check failed for ${name}: ${error.message}`);
        service.status = 'unhealthy';
        
        if (service.autoRestart && !this.isShuttingDown) {
          console.log(`🔄 Restarting unhealthy service: ${name}`);
          await this.restartService(name);
        }
      }
    }
  }

  /**
   * Restart a service
   */
  async restartService(serviceName) {
    const service = this.services.get(serviceName);
    if (!service) return;
    
    try {
      console.log(`🔄 Restarting ${serviceName}...`);
      
      // Kill the process
      if (service.process && !service.process.killed) {
        service.process.kill('SIGTERM');
      }
      
      // Wait a bit
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Start again
      const config = this.serviceConfigs.find(c => c.name === serviceName);
      if (config) {
        service.restarts++;
        await this.startService(config);
        console.log(`✅ ${serviceName} restarted (restart #${service.restarts})`);
      }
      
    } catch (error) {
      console.error(`❌ Failed to restart ${serviceName}:`, error.message);
    }
  }

  /**
   * Check if port is free
   */
  async checkPort(port) {
    return new Promise((resolve) => {
      const server = require('net').createServer();
      
      server.listen(port, () => {
        server.close(() => resolve(true));
      });
      
      server.on('error', () => resolve(false));
    });
  }

  /**
   * Stop all services
   */
  async stopAll() {
    this.isShuttingDown = true;
    
    console.log('\\n🛑 Stopping all services...');
    console.log('══════════════════════════');
    
    // Stop NGROK first
    if (this.ngrokManager) {
      try {
        await this.ngrokManager.stopTunnels();
        console.log('  ✅ NGROK tunnels stopped');
      } catch (error) {
        console.error('  ❌ Failed to stop NGROK:', error.message);
      }
    }
    
    // Stop webhook server
    if (this.webhookServer) {
      try {
        await this.webhookServer.stop();
        console.log('  ✅ Webhook server stopped');
      } catch (error) {
        console.error('  ❌ Failed to stop webhook server:', error.message);
      }
    }
    
    // Stop all other services
    for (const [name, service] of this.services) {
      try {
        if (service.process && !service.process.killed) {
          service.process.kill('SIGTERM');
          console.log(`  ✅ ${name} stopped`);
        }
      } catch (error) {
        console.error(`  ❌ Failed to stop ${name}:`, error.message);
      }
    }
    
    console.log('✅ All services stopped');
  }

  /**
   * Get service status
   */
  getStatus() {
    const status = {
      timestamp: new Date().toISOString(),
      services: {},
      ngrok: null,
      webhook: null
    };
    
    for (const [name, service] of this.services) {
      status.services[name] = {
        status: service.status,
        port: service.port,
        uptime: Math.floor((Date.now() - service.startTime.getTime()) / 1000),
        restarts: service.restarts,
        pid: service.process ? service.process.pid : null
      };
    }
    
    if (this.ngrokManager) {
      status.ngrok = {
        running: this.ngrokManager.isRunning,
        tunnels: this.ngrokManager.getTunnelUrls()
      };
    }
    
    if (this.webhookServer) {
      status.webhook = {
        running: true,
        port: this.webhookServer.config.port
      };
    }
    
    return status;
  }
}

// CLI interface
if (require.main === module) {
  const orchestrator = new ServiceOrchestrator();
  
  const command = process.argv[2];
  
  switch (command) {
    case 'start':
      orchestrator.startAll().catch(console.error);
      break;
      
    case 'stop':
      orchestrator.stopAll().then(() => process.exit(0)).catch(console.error);
      break;
      
    case 'status':
      console.log(JSON.stringify(orchestrator.getStatus(), null, 2));
      break;
      
    case 'restart':
      const serviceName = process.argv[3];
      if (serviceName) {
        orchestrator.restartService(serviceName).catch(console.error);
      } else {
        orchestrator.stopAll().then(() => {
          setTimeout(() => orchestrator.startAll(), 3000);
        }).catch(console.error);
      }
      break;
      
    default:
      orchestrator.startAll().catch(console.error);
  }
  
  // Handle graceful shutdown
  process.on('SIGINT', async () => {
    console.log('\\n🛑 Received SIGINT, shutting down...');
    await orchestrator.stopAll();
    process.exit(0);
  });
  
  process.on('SIGTERM', async () => {
    console.log('\\n🛑 Received SIGTERM, shutting down...');
    await orchestrator.stopAll();
    process.exit(0);
  });
}

module.exports = ServiceOrchestrator;