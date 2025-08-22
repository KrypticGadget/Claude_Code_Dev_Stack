#!/usr/bin/env node

/**
 * MCP Server Verification Script
 * Tests connectivity and functionality of configured MCP servers
 */

const { execSync, spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

console.log('\x1b[36m╔══════════════════════════════════════════════════════════╗');
console.log('║              MCP Server Verification                    ║');
console.log('╚══════════════════════════════════════════════════════════╝\x1b[0m\n');

const claudeConfigPath = path.join(os.homedir(), '.claude.json');

function testMcpServer(serverName, config, timeout = 30000) {
  return new Promise((resolve) => {
    console.log(`\x1b[33m🔍 Testing ${serverName} MCP server...\x1b[0m`);
    
    try {
      // Create a simple test process
      const child = spawn(config.command, config.args, {
        stdio: ['pipe', 'pipe', 'pipe'],
        env: { ...process.env, ...config.env }
      });

      let output = '';
      let errorOutput = '';
      let resolved = false;

      const cleanup = () => {
        if (!resolved) {
          resolved = true;
          try {
            child.kill('SIGTERM');
          } catch (e) {
            // Ignore cleanup errors
          }
        }
      };

      const timeoutId = setTimeout(() => {
        cleanup();
        resolve({
          name: serverName,
          status: 'timeout',
          message: `Server did not respond within ${timeout}ms`
        });
      }, timeout);

      child.stdout.on('data', (data) => {
        output += data.toString();
        // Look for MCP initialization patterns
        if (output.includes('{"jsonrpc"') || output.includes('"method"') || output.includes('"result"')) {
          clearTimeout(timeoutId);
          cleanup();
          if (!resolved) {
            resolved = true;
            resolve({
              name: serverName,
              status: 'success',
              message: 'Server responded with JSON-RPC messages',
              output: output.substring(0, 200) + (output.length > 200 ? '...' : '')
            });
          }
        }
      });

      child.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });

      child.on('error', (error) => {
        clearTimeout(timeoutId);
        cleanup();
        if (!resolved) {
          resolved = true;
          resolve({
            name: serverName,
            status: 'error',
            message: `Failed to start: ${error.message}`,
            error: errorOutput
          });
        }
      });

      child.on('close', (code) => {
        clearTimeout(timeoutId);
        cleanup();
        if (!resolved) {
          resolved = true;
          if (code === 0) {
            resolve({
              name: serverName,
              status: 'closed_cleanly',
              message: 'Server started and closed cleanly',
              output: output.substring(0, 200) + (output.length > 200 ? '...' : '')
            });
          } else {
            resolve({
              name: serverName,
              status: 'error',
              message: `Server exited with code ${code}`,
              error: errorOutput
            });
          }
        }
      });

      // Send a simple initialize request
      setTimeout(() => {
        try {
          const initRequest = JSON.stringify({
            jsonrpc: "2.0",
            id: 1,
            method: "initialize",
            params: {
              protocolVersion: "2024-11-05",
              capabilities: {},
              clientInfo: {
                name: "verification-test",
                version: "1.0.0"
              }
            }
          }) + '\n';
          
          child.stdin.write(initRequest);
        } catch (e) {
          // Ignore write errors
        }
      }, 1000);

    } catch (error) {
      resolve({
        name: serverName,
        status: 'error',
        message: `Failed to create process: ${error.message}`
      });
    }
  });
}

async function verifyMcpServers() {
  // Check if Claude config exists
  if (!fs.existsSync(claudeConfigPath)) {
    console.log('\x1b[31m❌ Claude configuration not found at ~/.claude.json\x1b[0m');
    console.log('\x1b[33m💡 Run claude-code-setup to create the configuration\x1b[0m');
    return;
  }

  let config;
  try {
    const configContent = fs.readFileSync(claudeConfigPath, 'utf8');
    config = JSON.parse(configContent);
  } catch (error) {
    console.log('\x1b[31m❌ Failed to parse Claude configuration\x1b[0m');
    console.log(`\x1b[31m   ${error.message}\x1b[0m`);
    return;
  }

  // Check if MCP servers are configured
  if (!config.mcpServers || Object.keys(config.mcpServers).length === 0) {
    console.log('\x1b[33m⚠️  No MCP servers configured in ~/.claude.json\x1b[0m');
    console.log('\x1b[33m💡 Run claude-code-setup to configure MCP servers\x1b[0m');
    return;
  }

  console.log(`\x1b[32mFound ${Object.keys(config.mcpServers).length} MCP server(s) configured:\x1b[0m`);
  Object.keys(config.mcpServers).forEach(name => {
    const server = config.mcpServers[name];
    console.log(`  • ${name}: ${server.command} ${server.args ? server.args.join(' ') : ''}`);
  });
  
  console.log('\n\x1b[36m🧪 Testing MCP servers...\x1b[0m\n');

  // Test each server
  const results = [];
  for (const [serverName, serverConfig] of Object.entries(config.mcpServers)) {
    const result = await testMcpServer(serverName, serverConfig, 15000);
    results.push(result);
    
    // Display result
    switch (result.status) {
      case 'success':
        console.log(`\x1b[32m✅ ${result.name}: ${result.message}\x1b[0m`);
        if (result.output) {
          console.log(`\x1b[90m   Output: ${result.output}\x1b[0m`);
        }
        break;
      case 'closed_cleanly':
        console.log(`\x1b[32m✅ ${result.name}: ${result.message}\x1b[0m`);
        break;
      case 'timeout':
        console.log(`\x1b[33m⏰ ${result.name}: ${result.message}\x1b[0m`);
        break;
      case 'error':
        console.log(`\x1b[31m❌ ${result.name}: ${result.message}\x1b[0m`);
        if (result.error) {
          console.log(`\x1b[90m   Error: ${result.error.substring(0, 200)}${result.error.length > 200 ? '...' : ''}\x1b[0m`);
        }
        break;
    }
    console.log('');
  }

  // Summary
  console.log('\x1b[36m📊 Verification Summary:\x1b[0m');
  const successful = results.filter(r => r.status === 'success' || r.status === 'closed_cleanly');
  const failed = results.filter(r => r.status === 'error');
  const timeouts = results.filter(r => r.status === 'timeout');

  console.log(`\x1b[32m✅ Successful: ${successful.length}\x1b[0m`);
  console.log(`\x1b[31m❌ Failed: ${failed.length}\x1b[0m`);
  console.log(`\x1b[33m⏰ Timeouts: ${timeouts.length}\x1b[0m`);

  if (failed.length > 0) {
    console.log('\n\x1b[33m💡 Troubleshooting tips:\x1b[0m');
    console.log('  • For GitHub MCP: Ensure GITHUB_PERSONAL_ACCESS_TOKEN is set');
    console.log('  • For Code Sandbox: Ensure Docker is installed and running');
    console.log('  • Check that all required dependencies are installed');
    console.log('  • Try running: claude-code-setup to reconfigure');
  }
}

// Run verification
verifyMcpServers().catch(error => {
  console.log(`\x1b[31m❌ Verification failed: ${error.message}\x1b[0m`);
  process.exit(1);
});