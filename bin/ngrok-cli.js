#!/usr/bin/env node
/**
 * NGROK CLI Tool for Claude Code Dev Stack
 * Unified command-line interface for NGROK tunnel management
 */

const { Command } = require('commander');
const chalk = require('chalk');
const path = require('path');
const fs = require('fs').promises;

const NgrokManager = require('../scripts/ngrok-manager');
const NgrokHealthMonitor = require('../scripts/ngrok-health-monitor');
const WebhookServer = require('../scripts/webhook-server');

const program = new Command();

// Global instances
let ngrokManager = null;
let healthMonitor = null;
let webhookServer = null;

program
  .name('ngrok-cli')
  .description('NGROK CLI for Claude Code Dev Stack v3.6.9')
  .version('3.6.9');

// Start command
program
  .command('start')
  .description('Start NGROK tunnels and services')
  .option('-c, --config <path>', 'Configuration file path', '../config/ngrok/ngrok-advanced.yml')
  .option('-t, --tunnels <tunnels>', 'Comma-separated list of tunnels to start', 'webapp,api,websocket,terminal,backend,webhooks')
  .option('-m, --monitor', 'Start health monitoring', false)
  .option('-w, --webhooks', 'Start webhook server', false)
  .option('-a, --all', 'Start all services (tunnels, monitoring, webhooks)', false)
  .action(async (options) => {
    try {
      console.log(chalk.blue('🚀 Starting NGROK services...'));
      
      if (options.all) {
        options.monitor = true;
        options.webhooks = true;
      }
      
      // Start NGROK tunnels
      const configPath = path.resolve(__dirname, options.config);
      const tunnels = options.tunnels.split(',').map(t => t.trim());
      
      ngrokManager = new NgrokManager({
        configPath,
        tunnels
      });
      
      await ngrokManager.initialize();
      console.log(chalk.green('✅ NGROK tunnels started'));
      
      // Start webhook server if requested
      if (options.webhooks) {
        webhookServer = new WebhookServer();
        await webhookServer.start();
        console.log(chalk.green('✅ Webhook server started'));
      }
      
      // Start health monitoring if requested
      if (options.monitor) {
        healthMonitor = new NgrokHealthMonitor();
        await healthMonitor.start();
        console.log(chalk.green('✅ Health monitoring started'));
      }
      
      // Display tunnel URLs
      const urls = ngrokManager.getTunnelUrls();
      console.log(chalk.cyan('\\n🔗 Active Tunnels:'));
      for (const [name, url] of Object.entries(urls)) {
        console.log(chalk.cyan(`   ${name}: ${url}`));
      }
      
      console.log(chalk.green('\\n🎉 All services started successfully!'));
      console.log(chalk.yellow('Press Ctrl+C to stop all services'));
      
      // Keep process alive
      process.stdin.resume();
      
    } catch (error) {
      console.error(chalk.red('❌ Failed to start services:'), error.message);
      process.exit(1);
    }
  });

// Stop command
program
  .command('stop')
  .description('Stop NGROK tunnels and services')
  .option('-a, --all', 'Stop all services', false)
  .action(async (options) => {
    try {
      console.log(chalk.blue('🛑 Stopping NGROK services...'));
      
      if (healthMonitor) {
        await healthMonitor.stop();
        console.log(chalk.green('✅ Health monitoring stopped'));
      }
      
      if (webhookServer) {
        await webhookServer.stop();
        console.log(chalk.green('✅ Webhook server stopped'));
      }
      
      if (ngrokManager) {
        await ngrokManager.stopTunnels();
        console.log(chalk.green('✅ NGROK tunnels stopped'));
      }
      
      console.log(chalk.green('🎉 All services stopped successfully!'));
      
    } catch (error) {
      console.error(chalk.red('❌ Failed to stop services:'), error.message);
      process.exit(1);
    }
  });

// Status command
program
  .command('status')
  .description('Show status of NGROK services')
  .option('-j, --json', 'Output in JSON format', false)
  .option('-w, --watch', 'Watch mode (refresh every 5 seconds)', false)
  .action(async (options) => {
    try {
      const showStatus = async () => {
        const status = {
          timestamp: new Date().toISOString(),
          ngrok: null,
          webhook: null,
          monitor: null
        };
        
        // Check NGROK status
        try {
          const axios = require('axios');
          const response = await axios.get('http://127.0.0.1:4040/api/tunnels', { timeout: 2000 });
          status.ngrok = {
            running: true,
            tunnels: response.data.tunnels.map(t => ({
              name: t.name,
              url: t.public_url,
              proto: t.proto,
              addr: t.config.addr
            }))
          };
        } catch (error) {
          status.ngrok = {
            running: false,
            error: error.message
          };
        }
        
        // Check webhook server status
        try {
          const axios = require('axios');
          const response = await axios.get('http://localhost:4000/health', { timeout: 2000 });
          status.webhook = {
            running: true,
            health: response.data
          };
        } catch (error) {
          status.webhook = {
            running: false,
            error: error.message
          };
        }
        
        // Check health monitor status
        try {
          const statusFile = path.join(__dirname, '../tmp/ngrok-health.json');
          const monitorData = await fs.readFile(statusFile, 'utf8');
          status.monitor = JSON.parse(monitorData);
        } catch (error) {
          status.monitor = {
            running: false,
            error: 'No status file found'
          };
        }
        
        if (options.json) {
          console.log(JSON.stringify(status, null, 2));
        } else {
          displayFormattedStatus(status);
        }
      };
      
      if (options.watch) {
        console.log(chalk.blue('👀 Watching NGROK status (Press Ctrl+C to exit)...'));
        
        const interval = setInterval(async () => {
          console.clear();
          await showStatus();
        }, 5000);
        
        // Initial display
        await showStatus();
        
        // Handle Ctrl+C
        process.on('SIGINT', () => {
          clearInterval(interval);
          console.log(chalk.yellow('\\n👋 Stopped watching'));
          process.exit(0);
        });
        
        // Keep process alive
        process.stdin.resume();
        
      } else {
        await showStatus();
      }
      
    } catch (error) {
      console.error(chalk.red('❌ Failed to get status:'), error.message);
      process.exit(1);
    }
  });

// Logs command
program
  .command('logs')
  .description('View NGROK and webhook logs')
  .option('-t, --type <type>', 'Log type: ngrok, webhook, health, all', 'all')
  .option('-f, --follow', 'Follow log output', false)
  .option('-n, --lines <number>', 'Number of lines to show', '50')
  .action(async (options) => {
    try {
      const logPaths = {
        ngrok: path.join(__dirname, '../logs/ngrok.log'),
        webhook: path.join(__dirname, '../logs/webhooks.log'),
        health: path.join(__dirname, '../logs/ngrok-alerts.log')
      };
      
      if (options.follow) {
        console.log(chalk.blue(`📄 Following ${options.type} logs (Press Ctrl+C to exit)...`));
        
        const { spawn } = require('child_process');
        
        if (options.type === 'all') {
          // Follow all logs
          for (const [type, logPath] of Object.entries(logPaths)) {
            try {
              const tail = spawn('tail', ['-f', logPath]);
              tail.stdout.on('data', (data) => {
                console.log(chalk.cyan(`[${type}]`), data.toString().trim());
              });
            } catch (error) {
              console.log(chalk.yellow(`No ${type} log file found`));
            }
          }
        } else {
          const logPath = logPaths[options.type];
          if (logPath) {
            const tail = spawn('tail', ['-f', logPath]);
            tail.stdout.on('data', (data) => {
              console.log(data.toString());
            });
          } else {
            console.error(chalk.red(`Unknown log type: ${options.type}`));
            process.exit(1);
          }
        }
        
        // Keep process alive
        process.stdin.resume();
        
      } else {
        // Show recent logs
        if (options.type === 'all') {
          for (const [type, logPath] of Object.entries(logPaths)) {
            try {
              console.log(chalk.cyan(`\\n📄 ${type.toUpperCase()} Logs (last ${options.lines} lines):`));
              console.log('═'.repeat(50));
              
              const { exec } = require('child_process');
              exec(`tail -n ${options.lines} "${logPath}"`, (error, stdout) => {
                if (error) {
                  console.log(chalk.yellow(`No ${type} log file found`));
                } else {
                  console.log(stdout);
                }
              });
            } catch (error) {
              console.log(chalk.yellow(`No ${type} log file found`));
            }
          }
        } else {
          const logPath = logPaths[options.type];
          if (logPath) {
            try {
              const { exec } = require('child_process');
              exec(`tail -n ${options.lines} "${logPath}"`, (error, stdout) => {
                if (error) {
                  console.log(chalk.yellow(`No ${options.type} log file found`));
                } else {
                  console.log(stdout);
                }
              });
            } catch (error) {
              console.log(chalk.yellow(`No ${options.type} log file found`));
            }
          } else {
            console.error(chalk.red(`Unknown log type: ${options.type}`));
            process.exit(1);
          }
        }
      }
      
    } catch (error) {
      console.error(chalk.red('❌ Failed to view logs:'), error.message);
      process.exit(1);
    }
  });

// Config command
program
  .command('config')
  .description('Manage NGROK configuration')
  .option('-s, --show', 'Show current configuration', false)
  .option('-e, --edit', 'Edit configuration file', false)
  .option('-v, --validate', 'Validate configuration', false)
  .option('-t, --test', 'Test configuration', false)
  .action(async (options) => {
    try {
      const configPath = path.join(__dirname, '../config/ngrok/ngrok-advanced.yml');
      
      if (options.show) {
        console.log(chalk.blue('📋 Current NGROK Configuration:'));
        console.log('═'.repeat(50));
        
        const config = await fs.readFile(configPath, 'utf8');
        console.log(config);
      }
      
      if (options.edit) {
        const editor = process.env.EDITOR || 'nano';
        const { spawn } = require('child_process');
        
        console.log(chalk.blue(`📝 Opening configuration in ${editor}...`));
        
        const child = spawn(editor, [configPath], {
          stdio: 'inherit'
        });
        
        child.on('close', (code) => {
          if (code === 0) {
            console.log(chalk.green('✅ Configuration saved'));
          } else {
            console.log(chalk.yellow('⚠️  Editor exited with code'), code);
          }
        });
      }
      
      if (options.validate) {
        console.log(chalk.blue('🔍 Validating configuration...'));
        
        try {
          const yaml = require('yaml');
          const config = await fs.readFile(configPath, 'utf8');
          const parsed = yaml.parse(config);
          
          // Basic validation
          if (!parsed.authtoken) {
            console.log(chalk.red('❌ Missing authtoken'));
          }
          
          if (!parsed.tunnels || Object.keys(parsed.tunnels).length === 0) {
            console.log(chalk.red('❌ No tunnels configured'));
          }
          
          console.log(chalk.green('✅ Configuration is valid'));
          
        } catch (error) {
          console.error(chalk.red('❌ Configuration validation failed:'), error.message);
        }
      }
      
      if (options.test) {
        console.log(chalk.blue('🧪 Testing NGROK configuration...'));
        
        try {
          const { exec } = require('child_process');
          exec(`ngrok config check --config="${configPath}"`, (error, stdout, stderr) => {
            if (error) {
              console.error(chalk.red('❌ Configuration test failed:'), error.message);
            } else {
              console.log(chalk.green('✅ Configuration test passed'));
              if (stdout) console.log(stdout);
            }
          });
        } catch (error) {
          console.error(chalk.red('❌ Failed to test configuration:'), error.message);
        }
      }
      
    } catch (error) {
      console.error(chalk.red('❌ Configuration command failed:'), error.message);
      process.exit(1);
    }
  });

// URLs command
program
  .command('urls')
  .description('Show active tunnel URLs')
  .option('-j, --json', 'Output in JSON format', false)
  .option('-c, --copy', 'Copy URLs to clipboard', false)
  .action(async (options) => {
    try {
      const axios = require('axios');
      const response = await axios.get('http://127.0.0.1:4040/api/tunnels', { timeout: 5000 });
      
      const tunnels = response.data.tunnels || [];
      const urls = {};
      
      tunnels.forEach(tunnel => {
        urls[tunnel.name] = tunnel.public_url;
      });
      
      if (options.json) {
        console.log(JSON.stringify(urls, null, 2));
      } else {
        console.log(chalk.cyan('🔗 Active Tunnel URLs:'));
        console.log('═'.repeat(30));
        
        for (const [name, url] of Object.entries(urls)) {
          console.log(chalk.cyan(`${name.padEnd(15)}: ${url}`));
        }
      }
      
      if (options.copy && Object.keys(urls).length > 0) {
        const urlList = Object.values(urls).join('\\n');
        
        try {
          const { exec } = require('child_process');
          
          // Try different clipboard commands based on platform
          const platform = require('os').platform();
          let clipboardCmd;
          
          if (platform === 'darwin') {
            clipboardCmd = 'pbcopy';
          } else if (platform === 'win32') {
            clipboardCmd = 'clip';
          } else {
            clipboardCmd = 'xclip -selection clipboard';
          }
          
          exec(`echo "${urlList}" | ${clipboardCmd}`, (error) => {
            if (error) {
              console.log(chalk.yellow('⚠️  Could not copy to clipboard'));
            } else {
              console.log(chalk.green('📋 URLs copied to clipboard'));
            }
          });
        } catch (error) {
          console.log(chalk.yellow('⚠️  Clipboard not available'));
        }
      }
      
    } catch (error) {
      console.error(chalk.red('❌ Failed to get tunnel URLs:'), error.message);
      console.log(chalk.yellow('💡 Make sure NGROK is running'));
      process.exit(1);
    }
  });

// Display formatted status
function displayFormattedStatus(status) {
  console.log(chalk.blue('📊 NGROK Service Status'));
  console.log('═'.repeat(50));
  console.log(chalk.gray(`Last updated: ${new Date(status.timestamp).toLocaleString()}`));
  console.log('');
  
  // NGROK Status
  const ngrokStatus = status.ngrok.running ? 
    chalk.green('🟢 Running') : chalk.red('🔴 Stopped');
  console.log(`NGROK Tunnels: ${ngrokStatus}`);
  
  if (status.ngrok.running && status.ngrok.tunnels) {
    console.log(chalk.cyan('  Active tunnels:'));
    status.ngrok.tunnels.forEach(tunnel => {
      console.log(chalk.cyan(`    ${tunnel.name}: ${tunnel.url} -> ${tunnel.addr}`));
    });
  } else if (status.ngrok.error) {
    console.log(chalk.red(`  Error: ${status.ngrok.error}`));
  }
  
  console.log('');
  
  // Webhook Status
  const webhookStatus = status.webhook.running ? 
    chalk.green('🟢 Running') : chalk.red('🔴 Stopped');
  console.log(`Webhook Server: ${webhookStatus}`);
  
  if (status.webhook.running && status.webhook.health) {
    console.log(chalk.cyan(`  Port: 4000`));
    console.log(chalk.cyan(`  Webhooks received: ${status.webhook.health.webhooks?.received || 0}`));
  } else if (status.webhook.error) {
    console.log(chalk.red(`  Error: ${status.webhook.error}`));
  }
  
  console.log('');
  
  // Health Monitor Status
  const monitorStatus = status.monitor.running ? 
    chalk.green('🟢 Running') : chalk.red('🔴 Stopped');
  console.log(`Health Monitor: ${monitorStatus}`);
  
  if (status.monitor.running && status.monitor.tunnels) {
    const healthyCount = status.monitor.tunnels.filter(t => t.healthy).length;
    const totalCount = status.monitor.tunnels.length;
    
    console.log(chalk.cyan(`  Healthy tunnels: ${healthyCount}/${totalCount}`));
    
    if (status.monitor.alerts && status.monitor.alerts.total > 0) {
      console.log(chalk.yellow(`  Total alerts: ${status.monitor.alerts.total}`));
    }
  } else if (status.monitor.error) {
    console.log(chalk.red(`  Error: ${status.monitor.error}`));
  }
}

// Handle graceful shutdown
process.on('SIGINT', async () => {
  console.log(chalk.yellow('\\n🛑 Received SIGINT, shutting down...'));
  
  if (healthMonitor) {
    await healthMonitor.stop();
  }
  
  if (webhookServer) {
    await webhookServer.stop();
  }
  
  if (ngrokManager) {
    await ngrokManager.stopTunnels();
  }
  
  process.exit(0);
});

program.parse();