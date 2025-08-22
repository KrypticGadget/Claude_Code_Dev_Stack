#!/usr/bin/env node

import { Command } from 'commander';
import chalk from 'chalk';
import axios from 'axios';
import { spawn, exec } from 'child_process';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const program = new Command();

program
  .name('claude-code-tunnel-restart')
  .description('Restart failed tunnels or perform a complete restart')
  .version('1.0.0')
  .option('-a, --all', 'Restart all tunnels (complete restart)')
  .option('-s, --service <service>', 'Restart specific service tunnel')
  .option('-f, --force', 'Force restart without graceful shutdown')
  .option('-q, --quiet', 'Suppress non-essential output')
  .option('-w, --wait <seconds>', 'Wait time between stop and start (default: 3)', '3')
  .option('--check-health', 'Check service health before restarting')
  .action(async (options) => {
    try {
      if (!options.quiet) {
        console.log(chalk.blue.bold('🔄 Claude Code Tunnel Manager - Restart'));
        console.log(chalk.gray('=' + '='.repeat(60)));
      }
      
      const waitTime = parseInt(options.wait) * 1000;
      let restartRequired = false;
      
      // Check current tunnel status
      let currentStatus;
      try {
        const response = await axios.get('http://localhost:4040/api/tunnels', { timeout: 5000 });
        currentStatus = {
          active: true,
          tunnels: response.data.tunnels || [],
          webInterface: 'http://localhost:4040'
        };
        
        if (!options.quiet) {
          console.log(chalk.blue(`📊 Found ${currentStatus.tunnels.length} active tunnels`));
        }
      } catch (error) {
        currentStatus = {
          active: false,
          error: error.message,
          tunnels: []
        };
        
        if (!options.quiet) {
          console.log(chalk.yellow('⚠️ No active tunnels detected'));
        }
      }
      
      // Load service configuration
      let config;
      try {
        const configPath = path.resolve(__dirname, '../config/tunnel/tunnel-config.json');
        const configData = await fs.readFile(configPath, 'utf8');
        config = JSON.parse(configData);
      } catch (error) {
        console.log(chalk.red(`❌ Failed to load configuration: ${error.message}`));
        process.exit(1);
      }
      
      // Health check function
      const checkServiceHealth = async (url, healthPath = '/health', timeout = 5000) => {
        try {
          const healthUrl = `${url}${healthPath}`;
          await axios.get(healthUrl, { timeout });
          return { healthy: true };
        } catch (error) {
          return { 
            healthy: false, 
            error: error.message,
            statusCode: error.response?.status
          };
        }
      };
      
      // Determine what needs to be restarted
      let servicesToRestart = [];
      
      if (options.all) {
        // Restart everything
        restartRequired = true;
        servicesToRestart = Object.keys(config.services);
        if (!options.quiet) {
          console.log(chalk.yellow('🔄 Complete restart requested'));
        }
        
      } else if (options.service) {
        // Restart specific service
        if (!config.services[options.service]) {
          console.log(chalk.red(`❌ Service '${options.service}' not found in configuration`));
          process.exit(1);
        }
        
        servicesToRestart = [options.service];
        restartRequired = true;
        
        if (!options.quiet) {
          console.log(chalk.yellow(`🔄 Restarting service: ${options.service}`));
        }
        
      } else {
        // Check for failed tunnels
        if (!currentStatus.active) {
          restartRequired = true;
          servicesToRestart = Object.keys(config.services);
          if (!options.quiet) {
            console.log(chalk.yellow('🔄 No active tunnels - full restart required'));
          }
        } else {
          // Check each configured service
          for (const [serviceName, serviceConfig] of Object.entries(config.services)) {
            const tunnel = currentStatus.tunnels.find(t => t.name === serviceName);
            
            if (!tunnel) {
              servicesToRestart.push(serviceName);
              restartRequired = true;
              if (!options.quiet) {
                console.log(chalk.yellow(`⚠️ Service '${serviceName}' tunnel not found`));
              }
              continue;
            }
            
            // Health check if requested
            if (options.checkHealth && serviceConfig.health_check?.enabled) {
              const health = await checkServiceHealth(
                tunnel.public_url,
                serviceConfig.health_check.path,
                serviceConfig.health_check.timeout
              );
              
              if (!health.healthy) {
                servicesToRestart.push(serviceName);
                restartRequired = true;
                if (!options.quiet) {
                  console.log(chalk.yellow(`⚠️ Service '${serviceName}' failed health check: ${health.error}`));
                }
              } else if (!options.quiet) {
                console.log(chalk.green(`✅ Service '${serviceName}' is healthy`));
              }
            }
          }
        }
      }
      
      if (!restartRequired) {
        if (!options.quiet) {
          console.log(chalk.green('✅ All tunnels are running and healthy'));
          console.log(chalk.blue('💡 Use --all flag to force a complete restart'));
        }
        return;
      }
      
      if (!options.quiet) {
        console.log(chalk.blue(`🔄 Restarting ${servicesToRestart.length} service(s): ${servicesToRestart.join(', ')}`));
      }
      
      // Step 1: Stop tunnels
      if (!options.quiet) {
        console.log(chalk.yellow('🛑 Stopping tunnels...'));
      }
      
      try {
        // Use the tunnel stop script
        const stopScript = path.resolve(__dirname, 'claude-code-tunnel-stop.js');
        const stopArgs = ['node', stopScript];
        
        if (options.force) {
          stopArgs.push('--force');
        }
        if (options.quiet) {
          stopArgs.push('--quiet');
        }
        
        await new Promise((resolve, reject) => {
          const stopProcess = spawn('node', [stopScript, ...(options.force ? ['--force'] : []), ...(options.quiet ? ['--quiet'] : [])], {
            stdio: options.quiet ? 'pipe' : 'inherit'
          });
          
          stopProcess.on('close', (code) => {
            if (code === 0) {
              resolve();
            } else {
              reject(new Error(`Stop script exited with code ${code}`));
            }
          });
          
          stopProcess.on('error', reject);
        });
        
        if (!options.quiet) {
          console.log(chalk.green('✅ Tunnels stopped successfully'));
        }
        
      } catch (error) {
        if (!options.quiet) {
          console.log(chalk.yellow(`⚠️ Stop process had issues: ${error.message}`));
          console.log(chalk.blue('Continuing with restart...'));
        }
      }
      
      // Step 2: Wait
      if (!options.quiet) {
        console.log(chalk.blue(`⏳ Waiting ${options.wait} seconds for cleanup...`));
      }
      
      await new Promise(resolve => setTimeout(resolve, waitTime));
      
      // Step 3: Start tunnels
      if (!options.quiet) {
        console.log(chalk.blue('🚀 Starting tunnels...'));
      }
      
      try {
        // Check for auth token
        const token = process.env.NGROK_AUTHTOKEN || process.env.NGROK_AUTH_TOKEN;
        if (!token) {
          console.log(chalk.red('❌ Error: ngrok auth token not found'));
          console.log(chalk.yellow('💡 Set environment variable: NGROK_AUTHTOKEN=YOUR_TOKEN'));
          process.exit(1);
        }
        
        // Use the tunnel start script
        const startScript = path.resolve(__dirname, 'claude-code-tunnel-start.js');
        const startArgs = ['node', startScript];
        
        if (options.quiet) {
          startArgs.push('--quiet');
        }
        
        await new Promise((resolve, reject) => {
          const startProcess = spawn('node', [startScript, ...(options.quiet ? ['--quiet'] : [])], {
            stdio: options.quiet ? 'pipe' : 'inherit',
            env: process.env
          });
          
          startProcess.on('close', (code) => {
            if (code === 0) {
              resolve();
            } else {
              reject(new Error(`Start script exited with code ${code}`));
            }
          });
          
          startProcess.on('error', reject);
        });
        
        if (!options.quiet) {
          console.log(chalk.green('✅ Tunnels started successfully'));
        }
        
      } catch (error) {
        console.log(chalk.red(`❌ Failed to start tunnels: ${error.message}`));
        process.exit(1);
      }
      
      // Step 4: Verify restart
      if (!options.quiet) {
        console.log(chalk.blue('🔍 Verifying restart...'));
      }
      
      // Wait a moment for tunnels to initialize
      await new Promise(resolve => setTimeout(resolve, 5000));
      
      try {
        const response = await axios.get('http://localhost:4040/api/tunnels', { timeout: 10000 });
        const newTunnels = response.data.tunnels || [];
        
        if (!options.quiet) {
          console.log(chalk.green(`✅ Restart verification: ${newTunnels.length} tunnels active`));
          
          // Show restarted services
          console.log(chalk.blue('\\n🌐 Active Tunnels After Restart:'));
          console.log(chalk.gray('-'.repeat(60)));
          
          for (const tunnel of newTunnels) {
            const serviceName = tunnel.name;
            const serviceConfig = config.services[serviceName];
            
            console.log(chalk.cyan(`📡 ${serviceConfig?.name || serviceName}`));
            console.log(chalk.gray(`   URL: ${tunnel.public_url}`));
          }
          
          console.log(chalk.gray('-'.repeat(60)));
          console.log(chalk.green.bold('🎉 Restart completed successfully!'));
          console.log(chalk.blue('💡 Use claude-code-tunnel-status to monitor tunnel health'));
        }
        
      } catch (error) {
        console.log(chalk.yellow(`⚠️ Could not verify restart: ${error.message}`));
        console.log(chalk.blue('💡 Check status manually with: claude-code-tunnel-status'));
      }
      
    } catch (error) {
      console.log(chalk.red('❌ Restart failed:'));
      console.log(chalk.red(`   ${error.message}`));
      
      if (!options.quiet) {
        console.log(chalk.yellow('\\n💡 Troubleshooting:'));
        console.log(chalk.gray('   1. Check if ngrok is installed'));
        console.log(chalk.gray('   2. Verify NGROK_AUTHTOKEN is set'));
        console.log(chalk.gray('   3. Try manual stop/start:'));
        console.log(chalk.gray('      claude-code-tunnel-stop --force'));
        console.log(chalk.gray('      claude-code-tunnel-start'));
      }
      
      process.exit(1);
    }
  });

program.parse(process.argv);