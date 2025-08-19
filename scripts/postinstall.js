#!/usr/bin/env node

/**
 * Post-install script for Claude Code Dev Stack V3
 * Runs automatically after npm install
 */

import chalk from 'chalk';
import fs from 'fs-extra';
import path from 'path';
import os from 'os';

const banner = `
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     🎉 Claude Code Dev Stack V3 Installed Successfully! 🎉      ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
`;

async function postInstall() {
  console.log(chalk.cyan(banner));
  
  console.log(chalk.blue('📋 Post-installation setup...'));
  
  try {
    // Create global directories if needed
    await ensureDirectories();
    
    // Show welcome message
    showWelcomeMessage();
    
    // Show next steps
    showNextSteps();
    
  } catch (error) {
    console.error(chalk.red('❌ Post-install setup failed:'), error.message);
    console.log(chalk.yellow('⚠️  You can still run claude-code-setup manually'));
  }
}

async function ensureDirectories() {
  const claudeDir = path.join(os.homedir(), '.claude');
  
  if (!(await fs.pathExists(claudeDir))) {
    await fs.ensureDir(claudeDir);
    console.log(chalk.green(`📁 Created Claude directory: ${claudeDir}`));
  }
  
  // Create subdirectories
  const subdirs = ['agents', 'hooks', 'audio', 'ui', 'logs', 'cache'];
  
  for (const subdir of subdirs) {
    const fullPath = path.join(claudeDir, subdir);
    await fs.ensureDir(fullPath);
  }
  
  console.log(chalk.green('📁 Directory structure created'));
}

function showWelcomeMessage() {
  console.log(chalk.blue('\n🚀 Claude Code Dev Stack V3 Features:'));
  console.log(chalk.green('  ✅ 28 Specialized AI Agents'));
  console.log(chalk.green('  ✅ 37 Intelligent Hooks'));
  console.log(chalk.green('  ✅ 90+ Audio Feedback Files'));
  console.log(chalk.green('  ✅ Unified React PWA Dashboard'));
  console.log(chalk.green('  ✅ Smart Orchestration Engine'));
  console.log(chalk.green('  ✅ Performance Monitoring'));
  console.log(chalk.green('  ✅ Security Scanning'));
  console.log(chalk.green('  ✅ Auto-Documentation'));
}

function showNextSteps() {
  console.log(chalk.yellow('\n🎯 Next Steps:'));
  console.log(chalk.cyan('  1. Run setup:'));
  console.log(chalk.white('     claude-code-setup'));
  console.log();
  console.log(chalk.cyan('  2. Or run interactive setup:'));
  console.log(chalk.white('     claude-code-setup --interactive'));
  console.log();
  console.log(chalk.cyan('  3. Manage agents:'));
  console.log(chalk.white('     claude-code-agents list'));
  console.log(chalk.white('     claude-code-agents install --all'));
  console.log();
  console.log(chalk.cyan('  4. Manage hooks:'));
  console.log(chalk.white('     claude-code-hooks list'));
  console.log(chalk.white('     claude-code-hooks install --all'));
  console.log();
  console.log(chalk.cyan('  5. Get help:'));
  console.log(chalk.white('     claude-code-setup --help'));
  console.log(chalk.white('     claude-code-agents help-examples'));
  console.log(chalk.white('     claude-code-hooks help-examples'));
  console.log();
  console.log(chalk.blue('📚 Documentation: https://claude-code.dev/docs'));
  console.log(chalk.blue('🐛 Issues: https://github.com/claude-code/dev-stack/issues'));
  console.log(chalk.blue('💬 Community: https://discord.gg/claude-code'));
  console.log();
  console.log(chalk.green('🎉 Happy coding with Claude!'));
}

// Run post-install
postInstall().catch(console.error);