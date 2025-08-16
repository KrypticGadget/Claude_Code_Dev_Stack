#!/usr/bin/env node
/**
 * Ultimate Statusline CLI Launcher
 * 
 * Quick launcher for the Ultimate Statusline Manager
 * Integrates @Owloops/claude-powerline with Dev Stack monitoring
 * 
 * Usage:
 *   node ultimate-statusline-cli.js
 *   npm run statusline
 * 
 * Attribution:
 * - Powerline by @Owloops: https://github.com/owloops/claude-powerline
 * - Dev Stack orchestration by Zach
 * - Ultimate integration for Claude Code v3.0
 */

const { startStatuslineCLI } = require('./ultimate-statusline');

console.log('🚀 Ultimate Statusline CLI Launcher');
console.log('====================================');
console.log('');
console.log('🎯 Starting Ultimate Statusline Manager...');
console.log('📊 Combining @Owloops/claude-powerline with Dev Stack monitoring');
console.log('⚡ Real-time updates every 100ms');
console.log('');

// Parse command line arguments
const args = process.argv.slice(2);
const config = {};

for (let i = 0; i < args.length; i++) {
  const arg = args[i];
  
  if (arg === '--interval' && i + 1 < args.length) {
    config.updateInterval = parseInt(args[i + 1], 10);
    i++; // Skip next argument
  } else if (arg === '--port' && i + 1 < args.length) {
    config.integrations = {
      ...config.integrations,
      browser: { port: parseInt(args[i + 1], 10) }
    };
    i++; // Skip next argument
  } else if (arg === '--no-websocket') {
    config.enableWebSocket = false;
  } else if (arg === '--no-performance') {
    config.enablePerformanceMetrics = false;
  } else if (arg === '--help' || arg === '-h') {
    console.log('Usage: node ultimate-statusline-cli.js [options]');
    console.log('');
    console.log('Options:');
    console.log('  --interval <ms>      Update interval in milliseconds (default: 100)');
    console.log('  --port <port>        WebSocket server port (default: 8087)');
    console.log('  --no-websocket       Disable WebSocket server');
    console.log('  --no-performance     Disable performance metrics');
    console.log('  --help, -h           Show this help message');
    console.log('');
    console.log('Attribution:');
    console.log('  Powerline: @Owloops/claude-powerline');
    console.log('  Dev Stack: Monitoring by Zach');
    console.log('  Integration: Ultimate Statusline v3.0');
    process.exit(0);
  }
}

// Start the statusline with config
startStatuslineCLI(config).catch((error) => {
  console.error('❌ Failed to start Ultimate Statusline:', error);
  process.exit(1);
});