#!/usr/bin/env node

import { promises as fs } from 'fs';
import path from 'path';
import chalk from 'chalk';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function setupTunnelManagement() {
  console.log(chalk.blue.bold('🔧 Setting up Claude Code Tunnel Management'));
  console.log(chalk.gray('=' + '='.repeat(60)));
  
  try {
    // Create necessary directories
    const dirs = [
      path.resolve(__dirname, '../logs'),
      path.resolve(__dirname, '../logs/qr-codes'),
      path.resolve(__dirname, '../config/tunnel'),
      path.resolve(__dirname, '../config/ngrok'),
      path.resolve(__dirname, '../lib/tunnel')
    ];
    
    for (const dir of dirs) {
      try {
        await fs.mkdir(dir, { recursive: true });
        console.log(chalk.green(`✅ Created directory: ${path.relative(process.cwd(), dir)}`));
      } catch (error) {
        if (error.code !== 'EEXIST') {
          console.log(chalk.yellow(`⚠️ Could not create ${dir}: ${error.message}`));
        }
      }
    }
    
    // Create .gitkeep files for empty directories
    const gitkeepDirs = [
      path.resolve(__dirname, '../logs'),
      path.resolve(__dirname, '../logs/qr-codes')
    ];
    
    for (const dir of gitkeepDirs) {
      const gitkeepPath = path.join(dir, '.gitkeep');
      try {
        await fs.writeFile(gitkeepPath, '# Keep this directory in git\n');
      } catch (error) {
        // Ignore errors
      }
    }
    
    // Create default environment file
    const envPath = path.resolve(__dirname, '../.env.tunnel');
    const envContent = `# Claude Code Tunnel Management Environment Variables
# Get your ngrok token from: https://dashboard.ngrok.com/auth/your-authtoken

# Required: ngrok authentication token
NGROK_AUTHTOKEN=

# Optional: Custom subdomains (requires ngrok pro)
NGROK_SUBDOMAIN=claude-dev
NGROK_API_SUBDOMAIN=claude-api
NGROK_UI_SUBDOMAIN=claude-ui
NGROK_MONITORING_SUBDOMAIN=claude-monitoring
NGROK_DEV_SUBDOMAIN=claude-dev-tools
NGROK_WS_SUBDOMAIN=claude-ws
NGROK_TERMINAL_SUBDOMAIN=claude-terminal
NGROK_MOBILE_SUBDOMAIN=claude-mobile

# Optional: Authentication for protected services
NGROK_MONITORING_AUTH=admin:admin

# Optional: Service ports (defaults defined in config)
CLAUDE_APP_PORT=3000
CLAUDE_API_PORT=3001
CLAUDE_UI_PORT=5173
CLAUDE_MONITORING_PORT=3000
CLAUDE_DEV_PORT=8080
CLAUDE_WS_PORT=3000
CLAUDE_TERMINAL_PORT=3002
CLAUDE_MOBILE_PORT=5555

# Optional: Logging
NGROK_LOG_PATH=./logs/ngrok.log
TUNNEL_LOG_LEVEL=info
`;
    
    try {
      await fs.access(envPath);
      console.log(chalk.blue(`ℹ️ Environment file already exists: ${path.relative(process.cwd(), envPath)}`));
    } catch {
      await fs.writeFile(envPath, envContent);
      console.log(chalk.green(`✅ Created environment file: ${path.relative(process.cwd(), envPath)}`));
    }
    
    // Verify tunnel commands exist
    const binDir = path.resolve(__dirname, '../bin');
    const tunnelCommands = [
      'claude-code-tunnel-start.js',
      'claude-code-tunnel-stop.js',
      'claude-code-tunnel-status.js',
      'claude-code-tunnel-restart.js',
      'claude-code-tunnel-config.js'
    ];
    
    let allCommandsExist = true;
    for (const command of tunnelCommands) {
      const commandPath = path.join(binDir, command);
      try {
        await fs.access(commandPath);
        console.log(chalk.green(`✅ Tunnel command: ${command}`));
      } catch {
        console.log(chalk.red(`❌ Missing command: ${command}`));
        allCommandsExist = false;
      }
    }
    
    // Verify configuration files exist
    const configFiles = [
      '../config/tunnel/tunnel-config.json',
      '../config/ngrok/ngrok.yml',
      '../lib/tunnel/tunnel-manager.js'
    ];
    
    for (const configFile of configFiles) {
      const configPath = path.resolve(__dirname, configFile);
      try {
        await fs.access(configPath);
        console.log(chalk.green(`✅ Config file: ${path.relative(process.cwd(), configPath)}`));
      } catch {
        console.log(chalk.red(`❌ Missing config: ${path.relative(process.cwd(), configPath)}`));
      }
    }
    
    // Check if ngrok is installed
    console.log(chalk.blue('\\n🔍 Checking ngrok installation...'));
    
    const { exec } = await import('child_process');
    const checkNgrok = () => new Promise((resolve) => {
      exec('ngrok version', (error, stdout, stderr) => {
        if (error) {
          resolve({ installed: false, error: error.message });
        } else {
          resolve({ installed: true, version: stdout.trim() });
        }
      });
    });
    
    const ngrokCheck = await checkNgrok();
    
    if (ngrokCheck.installed) {
      console.log(chalk.green(`✅ ngrok installed: ${ngrokCheck.version}`));
    } else {
      console.log(chalk.yellow('⚠️ ngrok not found in PATH'));
      console.log(chalk.blue('💡 Install ngrok:'));
      console.log(chalk.gray('   Windows: choco install ngrok'));
      console.log(chalk.gray('   macOS: brew install ngrok'));
      console.log(chalk.gray('   Linux: snap install ngrok'));
      console.log(chalk.gray('   Manual: https://ngrok.com/download'));
    }
    
    // Final setup instructions
    console.log(chalk.blue.bold('\\n🎯 Setup Complete!'));
    console.log(chalk.gray('=' + '='.repeat(60)));
    
    if (allCommandsExist) {
      console.log(chalk.green('✅ All tunnel management commands are available'));
      console.log(chalk.blue('\\n📋 Available commands:'));
      console.log(chalk.gray('   claude-code-tunnel-start     - Start all tunnels'));
      console.log(chalk.gray('   claude-code-tunnel-stop      - Stop all tunnels'));
      console.log(chalk.gray('   claude-code-tunnel-status    - Check tunnel status'));
      console.log(chalk.gray('   claude-code-tunnel-restart   - Restart failed tunnels'));
      console.log(chalk.gray('   claude-code-tunnel-config    - Configure settings'));
      
      console.log(chalk.blue('\\n📋 NPM scripts:'));
      console.log(chalk.gray('   npm run tunnel:start         - Start tunnels'));
      console.log(chalk.gray('   npm run tunnel:stop          - Stop tunnels'));
      console.log(chalk.gray('   npm run tunnel:status        - Check status'));
      console.log(chalk.gray('   npm run tunnel:restart       - Restart tunnels'));
      console.log(chalk.gray('   npm run tunnel:config        - Configure'));
    }
    
    console.log(chalk.blue('\\n🔑 Next steps:'));
    console.log(chalk.gray('   1. Get ngrok token: https://dashboard.ngrok.com/auth/your-authtoken'));
    console.log(chalk.gray(`   2. Edit: ${path.relative(process.cwd(), envPath)}`));
    console.log(chalk.gray('   3. Set NGROK_AUTHTOKEN in environment or .env.tunnel'));
    console.log(chalk.gray('   4. Run: claude-code-tunnel-start'));
    
    console.log(chalk.green('\\n🎉 Tunnel management system is ready!'));
    
  } catch (error) {
    console.log(chalk.red(`❌ Setup failed: ${error.message}`));
    process.exit(1);
  }
}

// Run setup if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  setupTunnelManagement();
}

export default setupTunnelManagement;