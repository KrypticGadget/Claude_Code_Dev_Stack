#!/usr/bin/env node

/**
 * Claude Code Dev Stack V3 - Stop Command
 * Stops all running services and tunnels
 */

import { execSync } from 'child_process';
import chalk from 'chalk';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log(chalk.red.bold(`
╔═══════════════════════════════════════════════════════════════╗
║  ·  ∘  ·  *  ·  ∘  ·  *  ·  ∘  ·  *  ·  ∘  ·  *  ·  ∘  ·    ║
║                                                               ║
║              🛑 CCDS - STOPPING SERVICES                      ║
║            CLAUDE CODE DEV STACK V3.6.9                      ║
║                                                               ║
║  ·  ∘  ·  *  ·  ∘  ·  *  ·  ∘  ·  *  ·  ∘  ·  *  ·  ∘  ·    ║
╚═══════════════════════════════════════════════════════════════╝
`));

console.log(chalk.yellow('🔍 Looking for running services...\n'));

let stoppedAny = false;

// Stop Node.js processes
try {
  console.log(chalk.cyan('📦 Stopping Node.js services...'));
  
  // Kill processes on common ports
  const ports = [3000, 3001, 5000, 5173, 8080, 8081, 4040];
  
  for (const port of ports) {
    try {
      if (process.platform === 'win32') {
        // Windows
        execSync(`netstat -ano | findstr :${port} | findstr LISTENING`, { stdio: 'pipe' });
        execSync(`for /f "tokens=5" %a in ('netstat -ano ^| findstr :${port} ^| findstr LISTENING') do taskkill /PID %a /F`, { stdio: 'pipe' });
        console.log(chalk.green(`   ✓ Stopped service on port ${port}`));
        stoppedAny = true;
      } else {
        // Unix/Linux/Mac
        execSync(`lsof -ti:${port} | xargs kill -9`, { stdio: 'pipe' });
        console.log(chalk.green(`   ✓ Stopped service on port ${port}`));
        stoppedAny = true;
      }
    } catch (e) {
      // Port not in use, continue
    }
  }
} catch (error) {
  // No services found
}

// Stop tunnels
try {
  console.log(chalk.cyan('🌐 Stopping ngrok tunnels...'));
  
  // Try to stop via our tunnel stop command
  const tunnelStopPath = path.join(__dirname, 'claude-code-tunnel-stop.js');
  execSync(`node ${tunnelStopPath}`, { stdio: 'pipe' });
  console.log(chalk.green('   ✓ Tunnels stopped'));
  stoppedAny = true;
} catch (error) {
  // Try direct ngrok kill
  try {
    if (process.platform === 'win32') {
      execSync('taskkill /IM ngrok.exe /F', { stdio: 'pipe' });
    } else {
      execSync('pkill ngrok', { stdio: 'pipe' });
    }
    console.log(chalk.green('   ✓ Ngrok stopped'));
    stoppedAny = true;
  } catch (e) {
    // No tunnels running
  }
}

// Stop pm2 processes if any
try {
  execSync('pm2 stop all', { stdio: 'pipe' });
  execSync('pm2 delete all', { stdio: 'pipe' });
  console.log(chalk.green('   ✓ PM2 processes stopped'));
  stoppedAny = true;
} catch (error) {
  // PM2 not running or not installed
}

console.log('');

if (stoppedAny) {
  console.log(chalk.green.bold('✅ All Claude Code services stopped successfully!'));
} else {
  console.log(chalk.yellow('⚠️  No running services found'));
}

console.log(chalk.gray('\n💡 Use "claude-code-start" to start services again'));

process.exit(0);