#!/usr/bin/env node

import { Command } from 'commander';
import chalk from 'chalk';
import TunnelManager from '../src/lib/tunnel/tunnel-manager.js';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const program = new Command();

program
  .name('claude-code-tunnel-start')
  .description('Start all NGROK tunnels with health checks for Claude Code remote access')
  .version('1.0.0')
  .option('-c, --config <path>', 'Custom configuration file path')
  .option('-s, --services <services>', 'Comma-separated list of services to start (default: all)')
  .option('-w, --wait', 'Wait for user input before exiting')
  .option('-q, --quiet', 'Suppress non-essential output')
  .option('--no-health-checks', 'Disable health checks')
  .option('--no-qr', 'Disable QR code generation')
  .option('--no-clipboard', 'Disable clipboard functionality')
  .option('--token <token>', 'Set ngrok auth token')
  .action(async (options) => {
    try {
      console.log(chalk.blue.bold('🚀 Claude Code Tunnel Manager - Starting Tunnels'));
      console.log(chalk.gray('=' + '='.repeat(60)));
      
      // Set ngrok token if provided
      if (options.token) {
        process.env.NGROK_AUTHTOKEN = options.token;
        process.env.NGROK_AUTH_TOKEN = options.token;
        if (!options.quiet) {
          console.log(chalk.green('✅ ngrok auth token set from command line'));
        }
      }
      
      // Check for auth token
      const token = process.env.NGROK_AUTHTOKEN || process.env.NGROK_AUTH_TOKEN;
      if (!token) {
        console.log(chalk.red('❌ Error: ngrok auth token not found'));
        console.log(chalk.yellow('📋 To get your token:'));
        console.log(chalk.gray('   1. Go to: https://dashboard.ngrok.com/signup'));
        console.log(chalk.gray('   2. Sign up for a free account'));
        console.log(chalk.gray('   3. Copy your auth token from the dashboard'));
        console.log(chalk.yellow('💡 Set token with: --token YOUR_TOKEN'));
        console.log(chalk.yellow('💡 Or set environment variable: NGROK_AUTHTOKEN=YOUR_TOKEN'));
        process.exit(1);
      }
      
      // Initialize tunnel manager
      const tunnelManager = new TunnelManager(options.config);
      
      // Set up event listeners
      tunnelManager.on('log', ({ level, message }) => {
        if (options.quiet && level === 'debug') return;
        // Log messages are already formatted and colored in tunnel manager
      });
      
      tunnelManager.on('error', (error) => {
        console.log(chalk.red(`❌ Error: ${error.message}`));
      });
      
      tunnelManager.on('started', async () => {
        console.log(chalk.green.bold('✅ All tunnels started successfully!'));
        
        try {
          // Get tunnel status
          const status = await tunnelManager.getTunnelStatus();
          
          if (status.active && Object.keys(status.tunnels).length > 0) {
            console.log(chalk.blue('\\n🌐 Active Tunnels:'));
            console.log(chalk.gray('-'.repeat(80)));
            
            for (const [name, tunnel] of Object.entries(status.tunnels)) {
              const serviceName = tunnelManager.config.services[name]?.name || name;
              console.log(chalk.cyan(`📡 ${serviceName}`));
              console.log(chalk.gray(`   URL: ${tunnel.url}`));
              console.log(chalk.gray(`   Local: http://localhost:${tunnelManager.config.services[name]?.port || 'unknown'}`));
              console.log('');
            }
            
            // Generate QR codes if enabled
            if (!options.noQr) {
              try {
                const qrCodes = await tunnelManager.generateQRCodes();
                if (Object.keys(qrCodes).length > 0) {
                  console.log(chalk.blue('📱 QR Codes generated for mobile access'));
                  
                  // Save QR codes to files
                  const qrDir = path.resolve(__dirname, '../logs/qr-codes');
                  await fs.mkdir(qrDir, { recursive: true });
                  
                  for (const [service, qrData] of Object.entries(qrCodes)) {
                    const qrFile = path.join(qrDir, `${service}-qr.txt`);
                    await fs.writeFile(qrFile, `Service: ${service}\\nURL: ${qrData.url}\\nQR Code: ${qrData.qr}`);
                  }
                  
                  console.log(chalk.gray(`   QR codes saved to: ${qrDir}`));
                }
              } catch (error) {
                console.log(chalk.yellow(`⚠️ QR code generation failed: ${error.message}`));
              }
            }
            
            // Copy main URL to clipboard if enabled
            if (!options.noClipboard) {
              const mainTunnel = status.tunnels['claude-app'] || Object.values(status.tunnels)[0];
              if (mainTunnel) {
                const copied = await tunnelManager.copyToClipboard(mainTunnel.url);
                if (copied) {
                  console.log(chalk.green(`📋 Main URL copied to clipboard: ${mainTunnel.url}`));
                }
              }
            }
            
            // Show web interface
            if (status.webInterface) {
              console.log(chalk.blue(`🔍 ngrok Web Interface: ${status.webInterface}`));
            }
            
            console.log(chalk.gray('-'.repeat(80)));
            console.log(chalk.green('🎉 Remote access is now available!'));
            console.log(chalk.yellow('💡 Use claude-code-tunnel-status to check tunnel health'));
            console.log(chalk.yellow('💡 Use claude-code-tunnel-stop to stop all tunnels'));
            
          } else {
            console.log(chalk.yellow('⚠️ Tunnels started but no active connections found'));
          }
          
        } catch (error) {
          console.log(chalk.yellow(`⚠️ Could not retrieve tunnel status: ${error.message}`));
        }
      });
      
      // Load configuration and start tunnels
      await tunnelManager.loadConfig();
      
      // Update configuration based on options
      if (options.noHealthChecks) {
        tunnelManager.config.settings.health_check_enabled = false;
      }
      if (options.noQr) {
        tunnelManager.config.settings.qr_code_enabled = false;
      }
      if (options.noClipboard) {
        tunnelManager.config.settings.clipboard_enabled = false;
      }
      
      // Start tunnel manager
      await tunnelManager.start();
      
      // Wait for user input if requested
      if (options.wait) {
        console.log(chalk.blue('\\nPress any key to exit...'));
        process.stdin.setRawMode(true);
        process.stdin.resume();
        process.stdin.on('data', () => {
          process.exit(0);
        });
      }
      
    } catch (error) {
      console.log(chalk.red('❌ Failed to start tunnels:'));
      console.log(chalk.red(`   ${error.message}`));
      
      if (error.message.includes('ngrok binary not found')) {
        console.log(chalk.yellow('\\n💡 Install ngrok:'));
        console.log(chalk.gray('   Visit: https://ngrok.com/download'));
        console.log(chalk.gray('   Or use package manager:'));
        console.log(chalk.gray('     - Windows: choco install ngrok'));
        console.log(chalk.gray('     - macOS: brew install ngrok'));
        console.log(chalk.gray('     - Linux: snap install ngrok'));
      }
      
      if (error.message.includes('token')) {
        console.log(chalk.yellow('\\n💡 Get ngrok token:'));
        console.log(chalk.gray('   1. Sign up at: https://dashboard.ngrok.com/signup'));
        console.log(chalk.gray('   2. Copy your auth token'));
        console.log(chalk.gray('   3. Run: ngrok config add-authtoken YOUR_TOKEN'));
        console.log(chalk.gray('   4. Or set: NGROK_AUTHTOKEN=YOUR_TOKEN'));
      }
      
      process.exit(1);
    }
  });

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log(chalk.yellow('\\n🛑 Received interrupt signal. Tunnels will continue running.'));
  console.log(chalk.blue('💡 Use claude-code-tunnel-stop to stop all tunnels'));
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log(chalk.yellow('\\n🛑 Received termination signal. Tunnels will continue running.'));
  process.exit(0);
});

program.parse(process.argv);