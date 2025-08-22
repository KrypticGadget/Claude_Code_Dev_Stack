#!/usr/bin/env node

import { Command } from 'commander';
import chalk from 'chalk';
import { spawn, exec } from 'child_process';
import { promises as fs } from 'fs';
import axios from 'axios';
import path from 'path';
import os from 'os';

const program = new Command();

program
  .name('claude-code-tunnel-stop')
  .description('Gracefully stop all tunnels and cleanup processes')
  .version('1.0.0')
  .option('-f, --force', 'Force kill all tunnel processes')
  .option('-q, --quiet', 'Suppress non-essential output')
  .option('--keep-logs', 'Keep log files after stopping')
  .action(async (options) => {
    try {
      if (!options.quiet) {
        console.log(chalk.red.bold('🛑 Claude Code Tunnel Manager - Stopping Tunnels'));
        console.log(chalk.gray('=' + '='.repeat(60)));
      }
      
      let stoppedCount = 0;
      let errors = [];
      
      // Try to get tunnel status before stopping
      let tunnelInfo = null;
      try {
        const response = await axios.get('http://localhost:4040/api/tunnels', { timeout: 3000 });
        tunnelInfo = response.data;
        if (!options.quiet && tunnelInfo.tunnels) {
          console.log(chalk.blue(`📊 Found ${tunnelInfo.tunnels.length} active tunnels`));
        }
      } catch (error) {
        if (!options.quiet) {
          console.log(chalk.yellow('⚠️ Could not connect to ngrok API (may already be stopped)'));
        }
      }
      
      // Stop ngrok gracefully first
      if (!options.force) {
        if (!options.quiet) {
          console.log(chalk.blue('🔄 Attempting graceful shutdown...'));
        }
        
        try {
          // Try to stop via API
          await axios.delete('http://localhost:4040/api/tunnels', { timeout: 5000 });
          stoppedCount++;
          if (!options.quiet) {
            console.log(chalk.green('✅ Tunnels stopped via API'));
          }
          
          // Wait a moment for cleanup
          await new Promise(resolve => setTimeout(resolve, 2000));
          
        } catch (error) {
          if (!options.quiet) {
            console.log(chalk.yellow('⚠️ API shutdown failed, trying process termination...'));
          }
        }
      }
      
      // Find and kill ngrok processes
      const platform = os.platform();
      let killCommand;
      
      if (platform === 'win32') {
        killCommand = options.force ? 
          'taskkill /F /IM ngrok.exe' : 
          'taskkill /IM ngrok.exe';
      } else {
        killCommand = options.force ?
          'pkill -9 ngrok' :
          'pkill -TERM ngrok';
      }
      
      try {
        await new Promise((resolve, reject) => {
          exec(killCommand, (error, stdout, stderr) => {
            if (error) {
              // Process might not be running
              if (error.message.includes('not found') || error.message.includes('No such process')) {
                resolve();
              } else {
                reject(error);
              }
            } else {
              resolve();
            }
          });
        });
        
        stoppedCount++;
        if (!options.quiet) {
          console.log(chalk.green('✅ ngrok processes terminated'));
        }
        
      } catch (error) {
        errors.push(`Process termination failed: ${error.message}`);
        if (!options.quiet) {
          console.log(chalk.yellow(`⚠️ ${error.message}`));
        }
      }
      
      // Kill any remaining tunnel-related processes
      const processNames = ['ngrok', 'cloudflared', 'tunnel'];
      
      for (const procName of processNames) {
        try {
          let cmd;
          if (platform === 'win32') {
            cmd = `tasklist /FI "IMAGENAME eq ${procName}.exe" /FO CSV | find /C "${procName}.exe"`;
          } else {
            cmd = `pgrep ${procName} | wc -l`;
          }
          
          const count = await new Promise((resolve) => {
            exec(cmd, (error, stdout) => {
              if (error) {
                resolve(0);
              } else {
                const num = parseInt(stdout.trim()) || 0;
                resolve(num);
              }
            });
          });
          
          if (count > 0) {
            const killCmd = platform === 'win32' ?
              `taskkill ${options.force ? '/F' : ''} /IM ${procName}.exe` :
              `pkill ${options.force ? '-9' : '-TERM'} ${procName}`;
            
            await new Promise((resolve) => {
              exec(killCmd, () => resolve()); // Always resolve to continue
            });
            
            if (!options.quiet) {
              console.log(chalk.green(`✅ Stopped ${count} ${procName} process(es)`));
            }
          }
          
        } catch (error) {
          errors.push(`Failed to stop ${procName}: ${error.message}`);
        }
      }
      
      // Clean up port bindings
      const portsToCheck = [4040, 4041, 4042]; // Common ngrok ports
      
      for (const port of portsToCheck) {
        try {
          if (platform === 'win32') {
            await new Promise((resolve) => {
              exec(`netstat -ano | findstr :${port}`, (error, stdout) => {
                if (stdout) {
                  const lines = stdout.split('\\n');
                  for (const line of lines) {
                    const match = line.match(/\\s+(\\d+)$/);
                    if (match) {
                      const pid = match[1];
                      exec(`taskkill /F /PID ${pid}`, () => {});
                    }
                  }
                }
                resolve();
              });
            });
          } else {
            await new Promise((resolve) => {
              exec(`lsof -ti:${port} | xargs kill ${options.force ? '-9' : '-TERM'}`, () => resolve());
            });
          }
        } catch (error) {
          // Ignore port cleanup errors
        }
      }
      
      // Clean up log files if requested
      if (!options.keepLogs) {
        try {
          const logDir = path.resolve(process.cwd(), 'logs');
          const ngrokLogPattern = path.join(logDir, '*ngrok*.log');
          const tunnelLogPattern = path.join(logDir, 'tunnel-manager.log');
          
          if (platform === 'win32') {
            exec(`del /Q "${ngrokLogPattern}" 2>nul`, () => {});
            exec(`del /Q "${tunnelLogPattern}" 2>nul`, () => {});
          } else {
            exec(`rm -f ${ngrokLogPattern} ${tunnelLogPattern}`, () => {});
          }
          
          if (!options.quiet) {
            console.log(chalk.blue('🧹 Log files cleaned up'));
          }
        } catch (error) {
          if (!options.quiet) {
            console.log(chalk.yellow('⚠️ Could not clean up log files'));
          }
        }
      }
      
      // Verify tunnels are stopped
      try {
        await axios.get('http://localhost:4040/api/tunnels', { timeout: 2000 });
        if (!options.quiet) {
          console.log(chalk.yellow('⚠️ ngrok API still responding - may need force stop'));
        }
      } catch (error) {
        // Good - API is not responding
        if (!options.quiet) {
          console.log(chalk.green('✅ Verified tunnels are stopped'));
        }
      }
      
      // Final status
      if (!options.quiet) {
        console.log(chalk.gray('-'.repeat(60)));
        
        if (stoppedCount > 0) {
          console.log(chalk.green.bold(`✅ Successfully stopped ${stoppedCount} tunnel service(s)`));
        } else {
          console.log(chalk.yellow('ℹ️ No active tunnels found to stop'));
        }
        
        if (errors.length > 0) {
          console.log(chalk.yellow('\\n⚠️ Some cleanup operations had issues:'));
          errors.forEach(error => {
            console.log(chalk.gray(`   • ${error}`));
          });
        }
        
        console.log(chalk.blue('\\n💡 Remote access has been disabled'));
        console.log(chalk.blue('💡 Use claude-code-tunnel-start to restart tunnels'));
      }
      
    } catch (error) {
      console.log(chalk.red('❌ Failed to stop tunnels:'));
      console.log(chalk.red(`   ${error.message}`));
      
      if (!options.quiet) {
        console.log(chalk.yellow('\\n💡 Try using --force flag for forceful shutdown'));
        console.log(chalk.gray('   claude-code-tunnel-stop --force'));
      }
      
      process.exit(1);
    }
  });

program.parse(process.argv);