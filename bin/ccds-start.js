#!/usr/bin/env node

/**
 * Claude Code Dev Stack V3 - Start Command
 * Starts the development server and web UI
 */

import { spawn } from 'child_process';
import chalk from 'chalk';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const packageRoot = path.resolve(__dirname, '..');

console.log(chalk.cyan.bold(`
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   🚀 CLAUDE CODE DEV STACK - STARTING                       ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
`));

console.log(chalk.green('🎯 Starting development server...'));
console.log(chalk.gray('   Press Ctrl+C to stop\n'));

// Start the dev server
const devProcess = spawn('npm', ['run', 'dev'], {
  cwd: packageRoot,
  stdio: 'inherit',
  shell: true,
  env: { ...process.env }
});

devProcess.on('error', (error) => {
  console.error(chalk.red(`❌ Failed to start: ${error.message}`));
  process.exit(1);
});

devProcess.on('exit', (code) => {
  if (code !== 0 && code !== null) {
    console.log(chalk.yellow(`⚠️  Process exited with code ${code}`));
  } else {
    console.log(chalk.green('✅ Stopped successfully'));
  }
});

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log(chalk.yellow('\n🛑 Stopping Claude Code Dev Stack...'));
  devProcess.kill('SIGTERM');
  setTimeout(() => {
    process.exit(0);
  }, 1000);
});

process.on('SIGTERM', () => {
  devProcess.kill('SIGTERM');
  process.exit(0);
});