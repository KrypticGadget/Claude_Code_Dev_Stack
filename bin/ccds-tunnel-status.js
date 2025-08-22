#!/usr/bin/env node

import { Command } from 'commander';
import chalk from 'chalk';
import axios from 'axios';
import { promises as fs } from 'fs';
import path from 'path';
import QRCode from 'qrcode-terminal';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const program = new Command();

program
  .name('claude-code-tunnel-status')
  .description('Check tunnel status and display URLs with health information')
  .version('1.0.0')
  .option('-j, --json', 'Output status in JSON format')
  .option('-q, --quiet', 'Show minimal output')
  .option('-w, --watch', 'Watch mode - refresh every 5 seconds')
  .option('--qr <service>', 'Show QR code for specific service')
  .option('--qr-all', 'Show QR codes for all services')
  .option('--health', 'Show detailed health check information')
  .option('--metrics', 'Show tunnel metrics and statistics')
  .option('--copy <service>', 'Copy URL for specific service to clipboard')
  .action(async (options) => {
    
    const getTunnelStatus = async () => {
      try {
        const response = await axios.get('http://localhost:4040/api/tunnels', { timeout: 5000 });
        return {
          active: true,
          tunnels: response.data.tunnels || [],
          webInterface: 'http://localhost:4040'
        };
      } catch (error) {
        return {
          active: false,
          error: error.message,
          tunnels: []
        };
      }
    };
    
    const getServiceConfig = async () => {
      try {
        const configPath = path.resolve(__dirname, '../config/tunnel/tunnel-config.json');
        const configData = await fs.readFile(configPath, 'utf8');
        return JSON.parse(configData);
      } catch (error) {
        return null;
      }
    };
    
    const checkServiceHealth = async (url, healthPath = '/health', timeout = 5000) => {
      try {
        const healthUrl = `${url}${healthPath}`;
        const response = await axios.get(healthUrl, { timeout });
        return {
          status: 'healthy',
          responseTime: response.headers['x-response-time'] || 'unknown',
          statusCode: response.status
        };
      } catch (error) {
        return {
          status: 'unhealthy',
          error: error.message,
          statusCode: error.response?.status || 'timeout'
        };
      }
    };
    
    const formatBytes = (bytes) => {
      if (bytes === 0) return '0 B';
      const k = 1024;
      const sizes = ['B', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };
    
    const formatUptime = (seconds) => {
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      const secs = seconds % 60;
      
      if (hours > 0) {
        return `${hours}h ${minutes}m ${secs}s`;
      } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
      } else {
        return `${secs}s`;
      }
    };
    
    const showQRCode = (url, serviceName) => {
      console.log(chalk.blue(`\\n📱 QR Code for ${serviceName}:`));
      console.log(chalk.gray(`URL: ${url}`));
      console.log('');
      QRCode.generate(url, { small: true });
      console.log('');
    };
    
    const copyToClipboard = async (text) => {
      try {
        const { default: clipboardy } = await import('clipboardy');
        await clipboardy.write(text);
        return true;
      } catch (error) {
        return false;
      }
    };
    
    const displayStatus = async () => {
      const status = await getTunnelStatus();
      const config = await getServiceConfig();
      
      if (options.json) {
        const jsonOutput = {
          active: status.active,
          timestamp: new Date().toISOString(),
          tunnels: status.tunnels.map(tunnel => ({
            name: tunnel.name,
            url: tunnel.public_url,
            proto: tunnel.proto,
            config: tunnel.config,
            metrics: tunnel.metrics
          })),
          webInterface: status.webInterface,
          error: status.error
        };
        
        console.log(JSON.stringify(jsonOutput, null, 2));
        return;
      }
      
      if (!options.quiet) {
        console.clear();
        console.log(chalk.blue.bold('🌐 Claude Code Tunnel Status'));
        console.log(chalk.gray('=' + '='.repeat(60)));
        console.log(chalk.gray(`Updated: ${new Date().toLocaleString()}`));
        console.log('');
      }
      
      if (!status.active) {
        console.log(chalk.red('❌ Tunnels are not active'));
        console.log(chalk.gray(`Error: ${status.error}`));
        console.log(chalk.yellow('💡 Run claude-code-tunnel-start to start tunnels'));
        return;
      }
      
      if (status.tunnels.length === 0) {
        console.log(chalk.yellow('⚠️ No tunnels found'));
        console.log(chalk.blue(`🔍 Web Interface: ${status.webInterface}`));
        return;
      }
      
      // Show tunnel information
      if (!options.quiet) {
        console.log(chalk.green(`✅ ${status.tunnels.length} tunnel(s) active`));
        console.log(chalk.blue(`🔍 Web Interface: ${status.webInterface}`));
        console.log('');
      }
      
      // Process each tunnel
      for (const tunnel of status.tunnels) {
        const serviceName = tunnel.name;
        const serviceConfig = config?.services?.[serviceName];
        
        if (!options.quiet) {
          console.log(chalk.cyan.bold(`📡 ${serviceConfig?.name || serviceName}`));
        } else {
          console.log(`${serviceName}: ${tunnel.public_url}`);
          continue;
        }
        
        console.log(chalk.gray(`   Public URL:  ${tunnel.public_url}`));
        console.log(chalk.gray(`   Local Port:  ${tunnel.config.addr}`));
        console.log(chalk.gray(`   Protocol:    ${tunnel.proto}`));
        
        // Show health status if requested
        if (options.health && serviceConfig?.health_check?.enabled) {
          const health = await checkServiceHealth(
            tunnel.public_url, 
            serviceConfig.health_check.path,
            serviceConfig.health_check.timeout
          );
          
          const healthIcon = health.status === 'healthy' ? '🟢' : '🔴';
          const healthColor = health.status === 'healthy' ? chalk.green : chalk.red;
          
          console.log(chalk.gray(`   Health:      ${healthIcon} ${healthColor(health.status)}`));
          
          if (health.responseTime && health.status === 'healthy') {
            console.log(chalk.gray(`   Response:    ${health.responseTime}`));
          }
          
          if (health.error) {
            console.log(chalk.gray(`   Error:       ${health.error}`));
          }
        }
        
        // Show metrics if requested
        if (options.metrics && tunnel.metrics) {
          console.log(chalk.gray(`   Connections: ${tunnel.metrics.conns?.count || 0}`));
          console.log(chalk.gray(`   Data In:     ${formatBytes(tunnel.metrics.http?.count || 0)}`));
          console.log(chalk.gray(`   Data Out:    ${formatBytes(tunnel.metrics.http?.bytes || 0)}`));
        }
        
        console.log('');
      }
      
      // Handle QR code display
      if (options.qrAll) {
        for (const tunnel of status.tunnels) {
          showQRCode(tunnel.public_url, tunnel.name);
        }
      } else if (options.qr) {
        const tunnel = status.tunnels.find(t => t.name === options.qr);
        if (tunnel) {
          showQRCode(tunnel.public_url, tunnel.name);
        } else {
          console.log(chalk.red(`❌ Service '${options.qr}' not found`));
        }
      }
      
      // Handle clipboard copy
      if (options.copy) {
        const tunnel = status.tunnels.find(t => t.name === options.copy);
        if (tunnel) {
          const copied = await copyToClipboard(tunnel.public_url);
          if (copied) {
            console.log(chalk.green(`📋 Copied ${tunnel.name} URL to clipboard: ${tunnel.public_url}`));
          } else {
            console.log(chalk.yellow(`⚠️ Could not copy to clipboard`));
            console.log(chalk.gray(`URL: ${tunnel.public_url}`));
          }
        } else {
          console.log(chalk.red(`❌ Service '${options.copy}' not found`));
        }
      }
      
      if (!options.quiet && !options.json) {
        console.log(chalk.gray('-'.repeat(60)));
        console.log(chalk.blue('💡 Commands:'));
        console.log(chalk.gray('   claude-code-tunnel-stop    - Stop all tunnels'));
        console.log(chalk.gray('   claude-code-tunnel-restart - Restart failed tunnels'));
        console.log(chalk.gray('   --qr <service>            - Show QR code'));
        console.log(chalk.gray('   --copy <service>          - Copy URL to clipboard'));
        console.log(chalk.gray('   --watch                   - Auto-refresh status'));
      }
    };
    
    // Handle watch mode
    if (options.watch) {
      console.log(chalk.blue('👀 Watch mode enabled - Press Ctrl+C to exit'));
      
      const interval = setInterval(displayStatus, 5000);
      
      process.on('SIGINT', () => {
        clearInterval(interval);
        console.log(chalk.yellow('\\n🛑 Watch mode stopped'));
        process.exit(0);
      });
      
      // Initial display
      await displayStatus();
      
    } else {
      // Single status check
      await displayStatus();
    }
  });

program.parse(process.argv);