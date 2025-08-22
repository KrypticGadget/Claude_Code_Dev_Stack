#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function checkDependencies() {
  const packageJsonPath = path.join(__dirname, '..', 'package.json');
  
  if (!fs.existsSync(packageJsonPath)) {
    log('Error: package.json not found', 'red');
    process.exit(1);
  }

  const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
  const requiredDeps = ['express', 'ws', 'node-pty', 'cors'];
  const missingDeps = [];

  for (const dep of requiredDeps) {
    if (!packageJson.dependencies || !packageJson.dependencies[dep]) {
      missingDeps.push(dep);
    }
  }

  if (missingDeps.length > 0) {
    log('Missing dependencies detected:', 'yellow');
    missingDeps.forEach(dep => log(`  - ${dep}`, 'yellow'));
    log('Installing missing dependencies...', 'cyan');
    
    const npmInstall = spawn('npm', ['install', ...missingDeps], {
      stdio: 'inherit',
      cwd: path.join(__dirname, '..')
    });

    npmInstall.on('close', (code) => {
      if (code === 0) {
        log('Dependencies installed successfully', 'green');
        startServer();
      } else {
        log('Failed to install dependencies', 'red');
        process.exit(1);
      }
    });
  } else {
    startServer();
  }
}

function startServer() {
  const serverPath = path.join(__dirname, '..', 'server', 'terminal-server.js');
  
  if (!fs.existsSync(serverPath)) {
    log('Error: Terminal server not found at ' + serverPath, 'red');
    process.exit(1);
  }

  log('Starting Claude Code Terminal Server...', 'cyan');
  log('Server path: ' + serverPath, 'blue');

  const server = spawn('node', [serverPath], {
    stdio: 'inherit',
    env: {
      ...process.env,
      TERMINAL_PORT: process.env.TERMINAL_PORT || '3001',
      NODE_ENV: process.env.NODE_ENV || 'development'
    }
  });

  server.on('error', (error) => {
    log('Failed to start terminal server:', 'red');
    log(error.message, 'red');
    process.exit(1);
  });

  server.on('close', (code) => {
    if (code === 0) {
      log('Terminal server stopped', 'yellow');
    } else {
      log(`Terminal server exited with code ${code}`, 'red');
    }
  });

  // Handle process signals
  process.on('SIGINT', () => {
    log('\nReceived SIGINT, stopping terminal server...', 'yellow');
    server.kill('SIGINT');
  });

  process.on('SIGTERM', () => {
    log('\nReceived SIGTERM, stopping terminal server...', 'yellow');
    server.kill('SIGTERM');
  });
}

// Start the process
log('Claude Code Terminal Server Manager', 'bright');
log('=====================================', 'bright');

checkDependencies();