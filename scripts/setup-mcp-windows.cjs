#!/usr/bin/env node

/**
 * Windows-specific MCP Server Setup
 * Handles Windows path issues and ensures MCP servers work correctly
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

console.log('\x1b[36m╔══════════════════════════════════════════════════════════╗');
console.log('║           Windows MCP Server Setup                      ║');
console.log('╚══════════════════════════════════════════════════════════╝\x1b[0m\n');

const claudeConfigPath = path.join(os.homedir(), '.claude.json');

function updateClaudeConfig() {
  console.log('\x1b[33m🔧 Updating Claude configuration for Windows...\x1b[0m');

  let config = {};
  if (fs.existsSync(claudeConfigPath)) {
    try {
      config = JSON.parse(fs.readFileSync(claudeConfigPath, 'utf8'));
    } catch (error) {
      console.log('\x1b[33m⚠️  Could not parse existing config, creating new one\x1b[0m');
    }
  }

  // Initialize MCP servers object
  config.mcpServers = config.mcpServers || {};

  // Configure GitHub MCP with proper Windows paths
  const dockerAvailable = checkDockerAvailable();
  if (dockerAvailable) {
    console.log('\x1b[32m✅ Docker detected, configuring GitHub MCP with Docker\x1b[0m');
    config.mcpServers.github = {
      type: "stdio",
      command: "docker",
      args: [
        "run", "-i", "--rm", 
        "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
        "ghcr.io/github/github-mcp-server"
      ],
      env: {
        GITHUB_PERSONAL_ACCESS_TOKEN: process.env.GITHUB_PERSONAL_ACCESS_TOKEN || 
                                     process.env.GITHUB_TOKEN || ""
      }
    };
  } else {
    console.log('\x1b[33m⚠️  Docker not available, using npx for GitHub MCP\x1b[0m');
    config.mcpServers.github = {
      type: "stdio", 
      command: "npx",
      args: ["@modelcontextprotocol/server-github"],
      env: {
        GITHUB_PERSONAL_ACCESS_TOKEN: process.env.GITHUB_PERSONAL_ACCESS_TOKEN || 
                                     process.env.GITHUB_TOKEN || ""
      }
    };
  }

  // Configure Code Sandbox MCP
  const codeSandboxBinaryPath = path.join(
    os.homedir(), 
    'AppData', 'Local', 'code-sandbox-mcp', 'code-sandbox-mcp.exe'
  );

  if (fs.existsSync(codeSandboxBinaryPath)) {
    console.log('\x1b[32m✅ Code Sandbox binary found, using direct path\x1b[0m');
    config.mcpServers["code-sandbox"] = {
      type: "stdio",
      command: codeSandboxBinaryPath,
      args: [],
      env: {}
    };
  } else {
    console.log('\x1b[33m⚠️  Code Sandbox binary not found, using npx fallback\x1b[0m');
    config.mcpServers["code-sandbox"] = {
      type: "stdio",
      command: "cmd",
      args: ["/c", "npx", "@modelcontextprotocol/code-sandbox-mcp"],
      env: {}
    };
  }

  // Save updated configuration
  try {
    fs.writeFileSync(claudeConfigPath, JSON.stringify(config, null, 2));
    console.log('\x1b[32m✅ Claude configuration updated successfully\x1b[0m');
    return true;
  } catch (error) {
    console.log(`\x1b[31m❌ Failed to save configuration: ${error.message}\x1b[0m`);
    return false;
  }
}

function checkDockerAvailable() {
  try {
    execSync('docker --version', { stdio: 'pipe' });
    execSync('docker ps', { stdio: 'pipe' });
    return true;
  } catch (error) {
    return false;
  }
}

function installMissingMcpServers() {
  console.log('\x1b[33m📦 Checking for missing MCP servers...\x1b[0m');

  // Try to install GitHub MCP server if not using Docker
  if (!checkDockerAvailable()) {
    try {
      console.log('\x1b[33m⬇️  Installing GitHub MCP server...\x1b[0m');
      execSync('npm install -g @modelcontextprotocol/server-github', { 
        stdio: 'inherit',
        timeout: 60000 
      });
      console.log('\x1b[32m✅ GitHub MCP server installed\x1b[0m');
    } catch (error) {
      console.log('\x1b[33m⚠️  GitHub MCP server installation failed, Docker will be used instead\x1b[0m');
    }
  }

  // Try to install Code Sandbox MCP
  const codeSandboxBinaryPath = path.join(
    os.homedir(), 
    'AppData', 'Local', 'code-sandbox-mcp', 'code-sandbox-mcp.exe'
  );

  if (!fs.existsSync(codeSandboxBinaryPath)) {
    console.log('\x1b[33m⬇️  Installing Code Sandbox MCP...\x1b[0m');
    try {
      // Try npm first
      try {
        execSync('npm install -g @modelcontextprotocol/code-sandbox-mcp', {
          stdio: 'inherit',
          timeout: 60000
        });
        console.log('\x1b[32m✅ Code Sandbox MCP installed via npm\x1b[0m');
      } catch (npmError) {
        // Try the PowerShell installer
        console.log('\x1b[33m⚠️  npm install failed, trying binary installer...\x1b[0m');
        
        const tempFile = path.join(os.tmpdir(), 'code-sandbox-installer.ps1');
        const installerUrl = 'https://raw.githubusercontent.com/Automata-Labs-team/code-sandbox-mcp/main/install.ps1';
        
        // Download installer
        execSync(`powershell -Command "Invoke-WebRequest -Uri '${installerUrl}' -OutFile '${tempFile}'"`, {
          stdio: 'pipe'
        });
        
        // Run installer
        execSync(`powershell -ExecutionPolicy Bypass -File "${tempFile}"`, {
          stdio: 'inherit',
          timeout: 120000
        });
        
        console.log('\x1b[32m✅ Code Sandbox MCP installed via binary installer\x1b[0m');
      }
    } catch (error) {
      console.log(`\x1b[31m❌ Code Sandbox MCP installation failed: ${error.message}\x1b[0m`);
      console.log('\x1b[33m💡 Visit https://github.com/Automata-Labs-team/code-sandbox-mcp for manual installation\x1b[0m');
    }
  } else {
    console.log('\x1b[32m✅ Code Sandbox MCP binary already installed\x1b[0m');
  }
}

function validateEnvironmentVariables() {
  console.log('\x1b[33m🔐 Checking environment variables...\x1b[0m');

  const githubToken = process.env.GITHUB_PERSONAL_ACCESS_TOKEN || process.env.GITHUB_TOKEN;
  if (!githubToken) {
    console.log('\x1b[33m⚠️  GITHUB_PERSONAL_ACCESS_TOKEN not set\x1b[0m');
    console.log('\x1b[33m💡 Set it with: set GITHUB_PERSONAL_ACCESS_TOKEN=your_token_here\x1b[0m');
    console.log('\x1b[33m   Or add it to your system environment variables\x1b[0m');
  } else {
    console.log('\x1b[32m✅ GitHub token configured\x1b[0m');
  }
}

function runDiagnostics() {
  console.log('\x1b[36m\n🔍 Running MCP diagnostics...\x1b[0m');

  // Check Node.js and npm
  try {
    const nodeVersion = execSync('node --version', { encoding: 'utf8' }).trim();
    const npmVersion = execSync('npm --version', { encoding: 'utf8' }).trim();
    console.log(`\x1b[32m✅ Node.js: ${nodeVersion}\x1b[0m`);
    console.log(`\x1b[32m✅ npm: ${npmVersion}\x1b[0m`);
  } catch (error) {
    console.log('\x1b[31m❌ Node.js/npm not available\x1b[0m');
  }

  // Check npx
  try {
    execSync('npx --version', { stdio: 'pipe' });
    console.log('\x1b[32m✅ npx available\x1b[0m');
  } catch (error) {
    console.log('\x1b[31m❌ npx not available\x1b[0m');
  }

  // Check Docker
  if (checkDockerAvailable()) {
    console.log('\x1b[32m✅ Docker available and running\x1b[0m');
  } else {
    console.log('\x1b[33m⚠️  Docker not available or not running\x1b[0m');
  }

  // Check Claude config
  if (fs.existsSync(claudeConfigPath)) {
    console.log('\x1b[32m✅ Claude config exists\x1b[0m');
  } else {
    console.log('\x1b[31m❌ Claude config not found\x1b[0m');
  }
}

async function main() {
  try {
    // Run initial diagnostics
    runDiagnostics();
    
    console.log('\n\x1b[36m🚀 Setting up MCP servers...\x1b[0m');
    
    // Install missing servers
    installMissingMcpServers();
    
    // Update Claude configuration
    updateClaudeConfig();
    
    // Validate environment variables
    validateEnvironmentVariables();
    
    console.log('\n\x1b[32m✅ Windows MCP setup complete!\x1b[0m');
    console.log('\n\x1b[36m🧪 Next steps:\x1b[0m');
    console.log('  1. Test MCP servers: node bin/verify-mcp-servers.js');
    console.log('  2. Restart Claude Code if it\'s running');
    console.log('  3. Try using MCP commands: /mcp in Claude Code');
    
  } catch (error) {
    console.log(`\x1b[31m❌ Setup failed: ${error.message}\x1b[0m`);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}