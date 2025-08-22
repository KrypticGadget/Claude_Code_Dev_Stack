#!/usr/bin/env node

import { spawn, exec } from 'child_process';
import { promises as fs } from 'fs';
import path from 'path';
import os from 'os';
import axios from 'axios';
import chalk from 'chalk';
import QRCode from 'qrcode';
import { EventEmitter } from 'events';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class TunnelManager extends EventEmitter {
  constructor(configPath = null) {
    super();
    this.configPath = configPath || path.resolve(__dirname, '../../config/tunnel/tunnel-config.json');
    this.config = null;
    this.tunnels = new Map();
    this.processes = new Map();
    this.healthChecks = new Map();
    this.metrics = {
      startTime: Date.now(),
      tunnelsStarted: 0,
      tunnelsActive: 0,
      healthChecksFailed: 0,
      restarts: 0
    };
    this.isRunning = false;
    this.ngrokWebInterface = null;
  }

  async loadConfig() {
    try {
      const configData = await fs.readFile(this.configPath, 'utf8');
      this.config = JSON.parse(configData);
      
      // Validate required fields
      if (!this.config.providers || !this.config.services) {
        throw new Error('Invalid configuration: missing providers or services');
      }
      
      this.log('info', 'Configuration loaded successfully');
      return this.config;
    } catch (error) {
      this.log('error', `Failed to load configuration: ${error.message}`);
      throw error;
    }
  }

  async saveConfig() {
    try {
      await fs.writeFile(this.configPath, JSON.stringify(this.config, null, 2));
      this.log('info', 'Configuration saved successfully');
    } catch (error) {
      this.log('error', `Failed to save configuration: ${error.message}`);
      throw error;
    }
  }

  log(level, message, data = null) {
    const timestamp = new Date().toISOString();
    const prefix = `[${timestamp}] [${level.toUpperCase()}]`;
    
    const colors = {
      error: chalk.red,
      warn: chalk.yellow,
      info: chalk.blue,
      success: chalk.green,
      debug: chalk.gray
    };
    
    const colorFn = colors[level] || chalk.white;
    console.log(colorFn(`${prefix} ${message}`));
    
    if (data) {
      console.log(chalk.gray(JSON.stringify(data, null, 2)));
    }

    this.emit('log', { level, message, data, timestamp });
  }

  async findNgrokBinary() {
    const platform = os.platform();
    const paths = this.config.providers.ngrok.binary_paths[platform] || [];
    
    for (const binaryPath of paths) {
      try {
        const expandedPath = binaryPath.replace('%USERNAME%', os.userInfo().username);
        await fs.access(expandedPath);
        return expandedPath;
      } catch {
        continue;
      }
    }
    
    // Try PATH
    return new Promise((resolve, reject) => {
      exec('which ngrok || where ngrok', (error, stdout) => {
        if (error) {
          reject(new Error('ngrok binary not found'));
        } else {
          resolve(stdout.trim().split('\\n')[0]);
        }
      });
    });
  }

  async installNgrok() {
    const platform = os.platform();
    const installUrl = this.config.providers.ngrok.install_urls[platform];
    
    if (!installUrl) {
      throw new Error(`No installation URL for platform: ${platform}`);
    }
    
    this.log('info', `Installing ngrok for ${platform}...`);
    this.log('info', `Download URL: ${installUrl}`);
    
    // For now, just provide instructions
    this.log('warn', 'Please install ngrok manually:');
    this.log('info', `1. Download from: ${installUrl}`);
    this.log('info', '2. Extract to a directory in your PATH');
    this.log('info', '3. Run: ngrok config add-authtoken YOUR_TOKEN');
    
    throw new Error('Manual ngrok installation required');
  }

  async validateNgrokToken() {
    const token = process.env.NGROK_AUTHTOKEN || process.env.NGROK_AUTH_TOKEN;
    
    if (!token) {
      throw new Error('NGROK_AUTHTOKEN environment variable not set');
    }
    
    if (token.length < 20) {
      throw new Error('Invalid ngrok token format');
    }
    
    this.log('success', 'ngrok token validation passed');
    return token;
  }

  async startNgrokTunnels() {
    try {
      const ngrokBinary = await this.findNgrokBinary();
      await this.validateNgrokToken();
      
      const configPath = path.resolve(__dirname, '../../config/ngrok/ngrok.yml');
      
      // Ensure log directory exists
      const logDir = path.dirname(this.config.settings.logging.file);
      await fs.mkdir(logDir, { recursive: true });
      
      // Set environment variables for config
      const env = {
        ...process.env,
        NGROK_AUTHTOKEN: process.env.NGROK_AUTHTOKEN || process.env.NGROK_AUTH_TOKEN,
        NGROK_LOG_PATH: this.config.settings.logging.file,
        ...this.getServiceEnvironmentVars()
      };
      
      this.log('info', 'Starting ngrok with all tunnels...');
      
      const ngrokProcess = spawn(ngrokBinary, [
        'start',
        '--all',
        '--config', configPath
      ], {
        env,
        stdio: ['pipe', 'pipe', 'pipe']
      });
      
      this.processes.set('ngrok', ngrokProcess);
      
      ngrokProcess.stdout.on('data', (data) => {
        this.log('debug', `ngrok stdout: ${data.toString().trim()}`);
      });
      
      ngrokProcess.stderr.on('data', (data) => {
        this.log('warn', `ngrok stderr: ${data.toString().trim()}`);
      });
      
      ngrokProcess.on('close', (code) => {
        this.log('warn', `ngrok process exited with code ${code}`);
        this.processes.delete('ngrok');
        
        if (this.isRunning && this.config.settings.auto_restart) {
          this.log('info', 'Attempting to restart ngrok...');
          setTimeout(() => this.startNgrokTunnels(), this.config.settings.retry_delay);
          this.metrics.restarts++;
        }
      });
      
      ngrokProcess.on('error', (error) => {
        this.log('error', `ngrok process error: ${error.message}`);
        this.emit('error', error);
      });
      
      // Wait for ngrok to start and get tunnel URLs
      await this.waitForNgrokStartup();
      
      this.metrics.tunnelsStarted++;
      this.log('success', 'ngrok tunnels started successfully');
      
      return ngrokProcess;
    } catch (error) {
      this.log('error', `Failed to start ngrok tunnels: ${error.message}`);
      throw error;
    }
  }

  getServiceEnvironmentVars() {
    const vars = {};
    
    for (const [serviceName, serviceConfig] of Object.entries(this.config.services)) {
      const envName = serviceName.toUpperCase().replace('-', '_') + '_PORT';
      vars[envName] = serviceConfig.port.toString();
    }
    
    return vars;
  }

  async waitForNgrokStartup(maxWait = 30000) {
    const startTime = Date.now();
    const checkInterval = 1000;
    
    while (Date.now() - startTime < maxWait) {
      try {
        const response = await axios.get('http://localhost:4040/api/tunnels', {
          timeout: 2000
        });
        
        if (response.data && response.data.tunnels) {
          this.ngrokWebInterface = 'http://localhost:4040';
          return response.data.tunnels;
        }
      } catch (error) {
        // Still starting up
      }
      
      await new Promise(resolve => setTimeout(resolve, checkInterval));
    }
    
    throw new Error('ngrok startup timeout');
  }

  async getTunnelStatus() {
    try {
      const response = await axios.get('http://localhost:4040/api/tunnels');
      const tunnels = response.data.tunnels || [];
      
      const status = {
        active: true,
        count: tunnels.length,
        webInterface: this.ngrokWebInterface,
        tunnels: {}
      };
      
      for (const tunnel of tunnels) {
        const serviceName = tunnel.name;
        status.tunnels[serviceName] = {
          name: tunnel.name,
          url: tunnel.public_url,
          proto: tunnel.proto,
          config: tunnel.config,
          metrics: tunnel.metrics
        };
      }
      
      this.tunnels = new Map(Object.entries(status.tunnels));
      this.metrics.tunnelsActive = status.count;
      
      return status;
    } catch (error) {
      return {
        active: false,
        error: error.message,
        count: 0,
        tunnels: {}
      };
    }
  }

  async startHealthChecks() {
    if (!this.config.settings.health_check_enabled) {
      return;
    }
    
    this.log('info', 'Starting health checks...');
    
    for (const [serviceName, serviceConfig] of Object.entries(this.config.services)) {
      if (serviceConfig.health_check && serviceConfig.health_check.enabled) {
        this.startHealthCheckForService(serviceName, serviceConfig);
      }
    }
  }

  startHealthCheckForService(serviceName, serviceConfig) {
    const healthCheck = setInterval(async () => {
      try {
        const tunnel = this.tunnels.get(serviceName);
        if (!tunnel) {
          return; // Tunnel not active
        }
        
        const healthUrl = `${tunnel.url}${serviceConfig.health_check.path}`;
        
        await axios.get(healthUrl, {
          timeout: serviceConfig.health_check.timeout
        });
        
        this.emit('healthCheck', {
          service: serviceName,
          status: 'healthy',
          url: healthUrl
        });
      } catch (error) {
        this.metrics.healthChecksFailed++;
        this.log('warn', `Health check failed for ${serviceName}: ${error.message}`);
        
        this.emit('healthCheck', {
          service: serviceName,
          status: 'unhealthy',
          error: error.message
        });
      }
    }, serviceConfig.health_check.interval);
    
    this.healthChecks.set(serviceName, healthCheck);
  }

  async generateQRCodes() {
    if (!this.config.settings.qr_code_enabled) {
      return {};
    }
    
    const qrCodes = {};
    const status = await this.getTunnelStatus();
    
    for (const [serviceName, tunnel] of Object.entries(status.tunnels)) {
      try {
        const qrCode = await QRCode.toDataURL(tunnel.url, {
          errorCorrectionLevel: 'M',
          type: 'image/png',
          quality: 0.92,
          margin: 1,
          color: {
            dark: '#000000',
            light: '#FFFFFF'
          }
        });
        
        qrCodes[serviceName] = {
          url: tunnel.url,
          qr: qrCode
        };
      } catch (error) {
        this.log('warn', `Failed to generate QR code for ${serviceName}: ${error.message}`);
      }
    }
    
    return qrCodes;
  }

  async copyToClipboard(text) {
    if (!this.config.settings.clipboard_enabled) {
      return false;
    }
    
    try {
      const { clipboard } = await import('clipboardy');
      await clipboard.write(text);
      return true;
    } catch (error) {
      this.log('warn', `Failed to copy to clipboard: ${error.message}`);
      return false;
    }
  }

  async sendNotification(title, message, data = null) {
    if (!this.config.settings.notifications_enabled) {
      return;
    }
    
    this.emit('notification', { title, message, data });
    
    // TODO: Implement webhook notifications
    if (this.config.notifications.webhook_url) {
      try {
        await axios.post(this.config.notifications.webhook_url, {
          title,
          message,
          data,
          timestamp: new Date().toISOString()
        });
      } catch (error) {
        this.log('warn', `Failed to send webhook notification: ${error.message}`);
      }
    }
  }

  async start() {
    try {
      this.log('info', 'Starting Claude Code Tunnel Manager...');
      
      if (!this.config) {
        await this.loadConfig();
      }
      
      this.isRunning = true;
      
      // Start tunnels
      await this.startNgrokTunnels();
      
      // Start health checks
      await this.startHealthChecks();
      
      // Send startup notification
      await this.sendNotification(
        'Tunnel Manager Started',
        'All tunnels are now active and ready for remote access'
      );
      
      this.log('success', 'Tunnel Manager started successfully');
      this.emit('started');
      
      return true;
    } catch (error) {
      this.log('error', `Failed to start Tunnel Manager: ${error.message}`);
      this.emit('error', error);
      throw error;
    }
  }

  async stop() {
    try {
      this.log('info', 'Stopping Claude Code Tunnel Manager...');
      
      this.isRunning = false;
      
      // Stop health checks
      for (const healthCheck of this.healthChecks.values()) {
        clearInterval(healthCheck);
      }
      this.healthChecks.clear();
      
      // Stop processes
      for (const [name, process] of this.processes.entries()) {
        this.log('info', `Stopping ${name} process...`);
        process.kill('SIGTERM');
        
        // Force kill after timeout
        setTimeout(() => {
          if (!process.killed) {
            process.kill('SIGKILL');
          }
        }, 5000);
      }
      
      this.processes.clear();
      this.tunnels.clear();
      
      // Send shutdown notification
      await this.sendNotification(
        'Tunnel Manager Stopped',
        'All tunnels have been stopped and cleaned up'
      );
      
      this.log('success', 'Tunnel Manager stopped successfully');
      this.emit('stopped');
      
      return true;
    } catch (error) {
      this.log('error', `Failed to stop Tunnel Manager: ${error.message}`);
      throw error;
    }
  }

  async restart() {
    this.log('info', 'Restarting Tunnel Manager...');
    await this.stop();
    await new Promise(resolve => setTimeout(resolve, 2000));
    await this.start();
    this.metrics.restarts++;
  }

  async getMetrics() {
    const status = await this.getTunnelStatus();
    
    return {
      ...this.metrics,
      uptime: Date.now() - this.metrics.startTime,
      tunnelsActive: status.count,
      isRunning: this.isRunning,
      webInterface: this.ngrokWebInterface,
      timestamp: new Date().toISOString()
    };
  }

  async updateConfig(updates) {
    this.config = { ...this.config, ...updates };
    await this.saveConfig();
    this.log('info', 'Configuration updated');
    this.emit('configUpdated', updates);
  }
}

export default TunnelManager;