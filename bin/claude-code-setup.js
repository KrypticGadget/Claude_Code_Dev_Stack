#!/usr/bin/env node

/**
 * Claude Code Setup - Main Installation Script
 * 
 * Installs and configures the complete Claude Code Dev Stack V3
 * including agents, hooks, audio, and unified PWA.
 */

import { program } from 'commander';
import chalk from 'chalk';
import inquirer from 'inquirer';
import fs from 'fs-extra';
import path from 'path';
import os from 'os';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

import { ClaudeCodeDevStack } from '../index.js';

// ASCII Art Banner
const banner = `
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ████████  ██          █████   ██    ██ ██████   ███████     ║
║   ██        ██         ██   ██  ██    ██ ██   ██  ██          ║
║   ██        ██         ███████  ██    ██ ██   ██  █████       ║
║   ██        ██         ██   ██  ██    ██ ██   ██  ██          ║
║   ████████  ███████    ██   ██   ██████   ██████   ███████     ║
║                                                               ║
║                    CODE DEV STACK V3                         ║
║              AI-Powered Development Environment               ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
`;

program
  .name('claude-code-setup')
  .description('Setup and configure Claude Code Dev Stack V3')
  .version('3.0.0');

program
  .option('-i, --interactive', 'Run interactive setup wizard')
  .option('-a, --agents-only', 'Install only agents')
  .option('-h, --hooks-only', 'Install only hooks')
  .option('-u, --audio-only', 'Setup only audio system')
  .option('-p, --path <path>', 'Custom installation path')
  .option('-y, --yes', 'Skip confirmations (use defaults)')
  .option('--skip-validation', 'Skip system validation')
  .option('--dev-mode', 'Enable development mode features')
  .action(async (options) => {
    console.log(chalk.cyan(banner));
    console.log(chalk.blue('🚀 Welcome to Claude Code Dev Stack V3 Setup!'));
    console.log();

    try {
      await runSetup(options);
    } catch (error) {
      console.error(chalk.red('❌ Setup failed:'), error.message);
      process.exit(1);
    }
  });

async function runSetup(options) {
  const stack = new ClaudeCodeDevStack();
  
  // System validation
  if (!options.skipValidation) {
    console.log(chalk.yellow('🔍 Validating system requirements...'));
    await validateSystem();
  }

  // Interactive mode
  if (options.interactive) {
    const answers = await inquirer.prompt([
      {
        type: 'checkbox',
        name: 'components',
        message: 'Which components would you like to install?',
        choices: [
          { name: '🤖 All 28 Specialized Agents', value: 'agents', checked: true },
          { name: '🪝 All 37 Intelligent Hooks', value: 'hooks', checked: true },
          { name: '🔊 Audio Feedback System (90+ sounds)', value: 'audio', checked: true },
          { name: '🎨 Unified PWA Dashboard', value: 'ui', checked: true },
          { name: '⚙️ Configuration Templates', value: 'config', checked: true }
        ]
      },
      {
        type: 'input',
        name: 'installPath',
        message: 'Installation path (leave empty for auto-detect):',
        default: ''
      },
      {
        type: 'confirm',
        name: 'createBackup',
        message: 'Create backup of existing configuration?',
        default: true
      },
      {
        type: 'confirm',
        name: 'enableDevMode',
        message: 'Enable development mode features?',
        default: false
      }
    ]);

    options = { ...options, ...answers };
  }

  // Determine installation path
  const installPath = options.path || options.installPath || await detectClaudeCodePath();
  
  console.log(chalk.blue(`📁 Installation path: ${installPath}`));
  console.log();

  // Create backup if requested
  if (options.createBackup !== false && !options.yes) {
    await createBackup(installPath);
  }

  // Initialize stack
  console.log(chalk.yellow('⚡ Initializing Claude Code Dev Stack...'));
  await stack.initialize();

  // Install components based on options
  const installPromises = [];

  if (shouldInstall('agents', options)) {
    console.log(chalk.blue('🤖 Installing agents...'));
    installPromises.push(stack.installAgents(installPath));
  }

  if (shouldInstall('hooks', options)) {
    console.log(chalk.blue('🪝 Installing hooks...'));
    installPromises.push(stack.installHooks(installPath));
  }

  if (shouldInstall('audio', options)) {
    console.log(chalk.blue('🔊 Setting up audio system...'));
    installPromises.push(stack.setupAudio(installPath));
  }

  if (shouldInstall('ui', options)) {
    console.log(chalk.blue('🎨 Installing unified PWA...'));
    installPromises.push(stack.startUI({ install: true, path: installPath }));
  }

  if (shouldInstall('config', options)) {
    console.log(chalk.blue('⚙️ Generating configuration...'));
    installPromises.push(stack.configManager.generate({ path: installPath, devMode: options.enableDevMode }));
  }

  // Execute all installations
  const results = await Promise.allSettled(installPromises);
  
  // Report results
  console.log();
  console.log(chalk.green('📊 Installation Results:'));
  
  results.forEach((result, index) => {
    const component = ['agents', 'hooks', 'audio', 'ui', 'config'][index];
    if (result.status === 'fulfilled') {
      console.log(chalk.green(`  ✅ ${component}: Success`));
    } else {
      console.log(chalk.red(`  ❌ ${component}: ${result.reason.message}`));
    }
  });

  // Final status
  const status = stack.getStatus();
  console.log();
  console.log(chalk.green('🎉 Claude Code Dev Stack V3 Setup Complete!'));
  console.log();
  console.log(chalk.blue('📈 System Status:'));
  console.log(`  • Version: ${status.version}`);
  console.log(`  • Agents: ${status.agents.installed}/${status.agents.available}`);
  console.log(`  • Hooks: ${status.hooks.installed}/${status.hooks.available}`);
  console.log(`  • Audio Files: ${status.audio.files}`);
  console.log(`  • UI: ${status.ui.status}`);
  console.log();
  console.log(chalk.yellow('🚀 Next Steps:'));
  console.log('  1. Restart Claude Code to load new components');
  console.log('  2. Run "claude-code-agents list" to see available agents');
  console.log('  3. Run "claude-code-hooks list" to see available hooks');
  console.log('  4. Visit the PWA dashboard for visual management');
  console.log();
  console.log(chalk.cyan('📚 Documentation: https://claude-code.dev/docs'));
}

function shouldInstall(component, options) {
  if (options.agentsOnly) return component === 'agents';
  if (options.hooksOnly) return component === 'hooks';
  if (options.audioOnly) return component === 'audio';
  if (options.components) return options.components.includes(component);
  return true; // Default: install everything
}

async function validateSystem() {
  const requirements = [
    { name: 'Node.js', command: 'node --version', minVersion: '18.0.0' },
    { name: 'npm', command: 'npm --version', minVersion: '8.0.0' },
    { name: 'Git', command: 'git --version', minVersion: '2.20.0' },
    { name: 'Python', command: 'python --version || python3 --version', minVersion: '3.8.0' }
  ];

  for (const req of requirements) {
    try {
      const { execSync } = await import('child_process');
      const version = execSync(req.command, { encoding: 'utf8', stdio: 'pipe' });
      console.log(chalk.green(`  ✅ ${req.name}: ${version.trim()}`));
    } catch (error) {
      console.log(chalk.yellow(`  ⚠️  ${req.name}: Not found or version check failed`));
    }
  }
}

async function detectClaudeCodePath() {
  const possiblePaths = [
    path.join(os.homedir(), '.claude'),
    path.join(os.homedir(), '.config', 'claude'),
    path.join(process.cwd(), '.claude'),
    '/usr/local/share/claude',
    'C:\\ProgramData\\Claude'
  ];

  for (const testPath of possiblePaths) {
    if (await fs.pathExists(testPath)) {
      return testPath;
    }
  }

  // Default to home directory
  return path.join(os.homedir(), '.claude');
}

async function createBackup(installPath) {
  const backupPath = `${installPath}.backup.${Date.now()}`;
  
  try {
    if (await fs.pathExists(installPath)) {
      await fs.copy(installPath, backupPath);
      console.log(chalk.green(`📋 Backup created: ${backupPath}`));
    }
  } catch (error) {
    console.log(chalk.yellow(`⚠️  Backup failed: ${error.message}`));
  }
}

program.parse();