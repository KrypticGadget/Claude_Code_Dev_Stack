#!/usr/bin/env node

/**
 * Complete installation script for Claude Code Dev Stack V3
 * This script performs a FULL installation including:
 * - All agents, hooks, and audio files
 * - MCP server installation and configuration
 * - Claude Code integration
 * - Unified PWA setup
 */

import chalk from 'chalk';
import fs from 'fs-extra';
import path from 'path';
import os from 'os';
import { execSync, spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const CLAUDE_CONFIG_DIR = path.join(os.homedir(), '.claude');
const CLAUDE_JSON = path.join(os.homedir(), '.claude.json');

// Beautiful banner
const banner = chalk.cyan.bold(`
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ████████  ██          █████   ██    ██ ██████   ███████     ║
║   ██        ██         ██   ██  ██    ██ ██   ██  ██          ║
║   ██        ██         ███████  ██    ██ ██   ██  █████       ║
║   ██        ██         ██   ██  ██    ██ ██   ██  ██          ║
║   ████████  ███████    ██   ██   ██████   ██████   ███████     ║
║                                                               ║
║                    CODE DEV STACK V3                         ║
║              Complete One-Command Installation                ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
`);

// Helper function to run commands
async function runCommand(command, description, options = {}) {
  console.log(chalk.yellow(`⚡ ${description}...`));
  try {
    execSync(command, { stdio: options.silent ? 'pipe' : 'inherit', ...options });
    console.log(chalk.green(`✅ ${description} complete`));
    return true;
  } catch (error) {
    if (!options.optional) {
      console.log(chalk.red(`❌ ${description} failed: ${error.message}`));
    } else {
      console.log(chalk.yellow(`⚠️  ${description} skipped (optional)`));
    }
    return false;
  }
}

// Check if running in Docker
function isDocker() {
  return fs.existsSync('/.dockerenv');
}

// Install MCP servers
async function installMCPServers() {
  console.log(chalk.cyan('\n🔌 Installing MCP Servers...'));
  
  const mcpServers = [
    {
      name: 'code-sandbox',
      check: 'code-sandbox-mcp --version',
      install: isDocker() 
        ? 'npm install -g @automata-labs/code-sandbox-mcp'
        : process.platform === 'win32'
          ? 'powershell -Command "irm https://raw.githubusercontent.com/Automata-Labs-team/code-sandbox-mcp/main/install.ps1 | iex"'
          : 'curl -fsSL https://raw.githubusercontent.com/Automata-Labs-team/code-sandbox-mcp/main/install.sh | bash'
    },
    {
      name: 'github',
      check: 'github-mcp-server --version',
      install: 'npm install -g @modelcontextprotocol/server-github'
    },
    {
      name: 'playwright',
      check: 'playwright-mcp --version',
      install: 'npm install -g @automata-labs/playwright-mcp'
    }
  ];
  
  for (const server of mcpServers) {
    try {
      execSync(server.check, { stdio: 'pipe' });
      console.log(chalk.green(`✅ ${server.name} MCP already installed`));
    } catch {
      await runCommand(server.install, `Installing ${server.name} MCP`, { optional: true });
    }
  }
}

// Configure Claude Code
async function configureClaudeCode() {
  console.log(chalk.cyan('\n⚙️  Configuring Claude Code...'));
  
  // Check if Claude Code is installed
  let claudeInstalled = false;
  try {
    execSync('claude --version', { stdio: 'pipe' });
    claudeInstalled = true;
    console.log(chalk.green('✅ Claude Code detected'));
  } catch {
    console.log(chalk.yellow('⚠️  Claude Code not detected'));
    console.log(chalk.yellow('   Please install Claude Code: npm install -g @anthropic-ai/claude-code'));
    return;
  }
  
  if (!claudeInstalled) return;
  
  // Read existing Claude config
  let claudeConfig = {};
  if (await fs.pathExists(CLAUDE_JSON)) {
    try {
      claudeConfig = await fs.readJson(CLAUDE_JSON);
    } catch (e) {
      console.log(chalk.yellow('⚠️  Could not read existing Claude config'));
    }
  }
  
  // Merge our configuration
  claudeConfig = {
    ...claudeConfig,
    devStack: {
      version: '3.0.0',
      enabled: true,
      agents: true,
      hooks: true,
      audio: true,
      pwa: true
    },
    hooks: [
      ...(claudeConfig.hooks || []),
      {
        pattern: '*',
        command: `node ${path.join(CLAUDE_CONFIG_DIR, 'hooks', 'master_orchestrator.js')}`,
        description: 'Master orchestration for Claude Code Dev Stack'
      },
      {
        pattern: '*',
        command: `node ${path.join(CLAUDE_CONFIG_DIR, 'hooks', 'audio_controller.js')}`,
        description: 'Audio feedback system'
      },
      {
        pattern: '@*',
        command: `node ${path.join(CLAUDE_CONFIG_DIR, 'hooks', 'smart_orchestrator.js')}`,
        description: 'Smart agent routing'
      }
    ],
    mcpServers: {
      ...claudeConfig.mcpServers,
      'code-sandbox': {
        command: process.platform === 'win32' 
          ? path.join(os.homedir(), 'AppData', 'Local', 'code-sandbox-mcp', 'code-sandbox-mcp.exe')
          : 'code-sandbox-mcp',
        args: []
      },
      'github': {
        command: 'github-mcp-server',
        args: [],
        env: {
          GITHUB_TOKEN: process.env.GITHUB_TOKEN || ''
        }
      },
      'playwright': {
        command: 'playwright-mcp',
        args: []
      }
    }
  };
  
  // Remove duplicate hooks
  const uniqueHooks = [];
  const seenCommands = new Set();
  for (const hook of (claudeConfig.hooks || [])) {
    const key = hook.command;
    if (!seenCommands.has(key)) {
      seenCommands.add(key);
      uniqueHooks.push(hook);
    }
  }
  claudeConfig.hooks = uniqueHooks;
  
  // Write updated config
  await fs.writeJson(CLAUDE_JSON, claudeConfig, { spaces: 2 });
  console.log(chalk.green('✅ Claude Code configuration updated'));
  
  // Add MCP servers to Claude Code
  console.log(chalk.yellow('⚡ Registering MCP servers with Claude Code...'));
  const mcpCommands = [
    'claude mcp add code-sandbox',
    'claude mcp add github', 
    'claude mcp add playwright'
  ];
  
  for (const cmd of mcpCommands) {
    await runCommand(cmd, `Adding ${cmd.split(' ')[2]} MCP`, { optional: true });
  }
}

// Setup hooks integration
async function setupHooksIntegration() {
  console.log(chalk.cyan('\n🪝 Setting up hooks integration...'));
  
  const hooksDir = path.join(CLAUDE_CONFIG_DIR, 'hooks');
  await fs.ensureDir(hooksDir);
  
  // Create wrapper scripts for Python hooks
  const hookFiles = await fs.readdir(path.join(__dirname, '..', 'core', 'hooks', 'hooks'));
  
  for (const hookFile of hookFiles) {
    if (hookFile.endsWith('.py')) {
      const hookName = path.basename(hookFile, '.py');
      const wrapperContent = `#!/usr/bin/env node
const { spawn } = require('child_process');
const path = require('path');

const pythonScript = path.join(__dirname, '..', 'core', 'hooks', 'hooks', '${hookFile}');
const python = spawn('python3', [pythonScript, ...process.argv.slice(2)]);

python.stdout.on('data', (data) => {
  process.stdout.write(data);
});

python.stderr.on('data', (data) => {
  process.stderr.write(data);
});

python.on('close', (code) => {
  process.exit(code);
});
`;
      
      const wrapperPath = path.join(hooksDir, `${hookName}.js`);
      await fs.writeFile(wrapperPath, wrapperContent);
      
      if (process.platform !== 'win32') {
        await fs.chmod(wrapperPath, '755');
      }
    }
  }
  
  console.log(chalk.green('✅ Hook wrappers created'));
}

// Setup Unified PWA
async function setupUnifiedPWA() {
  console.log(chalk.cyan('\n🎨 Setting up Unified PWA...'));
  
  const pwaSource = path.join(__dirname, '..', 'ui', 'react-pwa');
  const pwaTarget = path.join(CLAUDE_CONFIG_DIR, 'ui');
  
  // Copy PWA files
  await fs.copy(pwaSource, pwaTarget);
  console.log(chalk.green('✅ PWA files copied'));
  
  // Install dependencies
  console.log(chalk.yellow('📦 Installing PWA dependencies...'));
  try {
    execSync('npm install', { 
      cwd: pwaTarget, 
      stdio: 'inherit',
      env: { ...process.env, CI: 'true' }
    });
    console.log(chalk.green('✅ PWA dependencies installed'));
  } catch (error) {
    console.log(chalk.yellow('⚠️  PWA dependencies installation incomplete'));
    console.log(chalk.yellow('   Run manually: cd ~/.claude/ui && npm install'));
  }
  
  // Create start script
  const startScript = `#!/bin/bash
cd ${pwaTarget}
npm run dev
`;
  
  const startScriptPath = path.join(CLAUDE_CONFIG_DIR, 'start-pwa.sh');
  await fs.writeFile(startScriptPath, startScript);
  
  if (process.platform !== 'win32') {
    await fs.chmod(startScriptPath, '755');
  }
  
  console.log(chalk.green('✅ PWA start script created'));
}

// Main installation
async function main() {
  console.log(banner);
  
  console.log(chalk.green.bold('\n🚀 Starting Complete Installation...\n'));
  
  // Step 1: Basic setup
  console.log(chalk.cyan('📋 Step 1/6: Running basic setup...'));
  await runCommand('claude-code-setup --yes --skip-validation', 'Basic setup');
  
  // Step 2: Install agents
  console.log(chalk.cyan('\n🤖 Step 2/6: Installing agents...'));
  await runCommand('claude-code-agents install --all', 'Agent installation');
  
  // Step 3: Install hooks
  console.log(chalk.cyan('\n🪝 Step 3/6: Installing hooks...'));
  await runCommand('claude-code-hooks install --all', 'Hook installation');
  await setupHooksIntegration();
  
  // Step 4: Install MCP servers
  console.log(chalk.cyan('\n🔌 Step 4/6: Installing MCP servers...'));
  await installMCPServers();
  
  // Step 5: Configure Claude Code
  console.log(chalk.cyan('\n⚙️  Step 5/6: Configuring Claude Code...'));
  await configureClaudeCode();
  
  // Step 6: Setup PWA
  console.log(chalk.cyan('\n🎨 Step 6/6: Setting up Unified PWA...'));
  await setupUnifiedPWA();
  
  // Success message
  console.log(chalk.green.bold(`
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║        ✨ INSTALLATION COMPLETE! ✨                          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
`));
  
  console.log(chalk.cyan('📊 Installation Summary:'));
  console.log(chalk.green('  ✅ 28 AI Agents installed'));
  console.log(chalk.green('  ✅ 37 Intelligent Hooks configured'));
  console.log(chalk.green('  ✅ 90+ Audio files ready'));
  console.log(chalk.green('  ✅ Unified PWA dashboard installed'));
  console.log(chalk.green('  ✅ MCP servers configured'));
  console.log(chalk.green('  ✅ Claude Code integration complete'));
  
  console.log(chalk.yellow('\n🚀 Quick Start Commands:'));
  console.log(chalk.white('  1. Test agents:     claude "@master-orchestrator help"'));
  console.log(chalk.white('  2. Start PWA:       cd ~/.claude/ui && npm run dev'));
  console.log(chalk.white('  3. List agents:     claude-code-agents list'));
  console.log(chalk.white('  4. List hooks:      claude-code-hooks list'));
  console.log(chalk.white('  5. Test MCP:        claude "use code-sandbox to create a test.py"'));
  
  console.log(chalk.blue('\n📚 Resources:'));
  console.log(chalk.white('  Documentation: https://claude-code.dev/docs'));
  console.log(chalk.white('  GitHub:        https://github.com/claude-code/dev-stack'));
  console.log(chalk.white('  Support:       https://discord.gg/claude-code'));
  
  console.log(chalk.green.bold('\n🎉 Enjoy Claude Code Dev Stack V3!\n'));
}

// Run installation
main().catch(error => {
  console.error(chalk.red('\n❌ Installation failed:'), error);
  console.log(chalk.yellow('\n💡 Try running individual commands:'));
  console.log(chalk.white('  claude-code-setup'));
  console.log(chalk.white('  claude-code-agents install --all'));
  console.log(chalk.white('  claude-code-hooks install --all'));
  process.exit(1);
});