#!/usr/bin/env node

/**
 * Post-install script for Claude Code Dev Stack V3
 * Runs automatically after npm install
 * Fixes executable permissions and file paths
 */

import chalk from 'chalk';
import fs from 'fs-extra';
import path from 'path';
import os from 'os';
import { execSync } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

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
    
    // Fix executable permissions on Unix systems
    await fixExecutablePermissions();
    
    // Validate Python scripts have proper shebangs
    await validatePythonScripts();
    
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

async function fixExecutablePermissions() {
  // Only fix permissions on Unix-like systems
  if (os.platform() === 'win32') {
    console.log(chalk.yellow('⚠️  Windows detected - skipping chmod operations'));
    return;
  }
  
  console.log(chalk.blue('🔧 Fixing executable permissions on Unix system...'));
  
  const packageRoot = path.resolve(__dirname, '..');
  
  try {
    // Fix bin directory scripts
    const binDir = path.join(packageRoot, 'bin');
    if (await fs.pathExists(binDir)) {
      const binFiles = await fs.readdir(binDir);
      for (const file of binFiles) {
        if (file.endsWith('.js')) {
          const filePath = path.join(binDir, file);
          try {
            execSync(`chmod +x "${filePath}"`, { stdio: 'pipe' });
            console.log(chalk.green(`  ✅ Made executable: ${file}`));
          } catch (error) {
            console.log(chalk.yellow(`  ⚠️  Could not chmod ${file}: ${error.message}`));
          }
        }
      }
    }
    
    // Fix Python hook scripts
    const hooksDir = path.join(packageRoot, 'core', 'hooks', 'hooks');
    if (await fs.pathExists(hooksDir)) {
      const hookFiles = await fs.readdir(hooksDir);
      for (const file of hookFiles) {
        if (file.endsWith('.py')) {
          const filePath = path.join(hooksDir, file);
          try {
            execSync(`chmod +x "${filePath}"`, { stdio: 'pipe' });
            console.log(chalk.green(`  ✅ Made executable: ${file}`));
          } catch (error) {
            console.log(chalk.yellow(`  ⚠️  Could not chmod ${file}: ${error.message}`));
          }
        }
      }
    }
    
    // Fix any shell scripts
    const scriptsDirs = [
      path.join(packageRoot, 'scripts'),
      path.join(packageRoot, 'integrations')
    ];
    
    for (const scriptsDir of scriptsDirs) {
      if (await fs.pathExists(scriptsDir)) {
        const allFiles = await walkDirectory(scriptsDir);
        for (const filePath of allFiles) {
          if (filePath.endsWith('.sh') || filePath.endsWith('.py')) {
            try {
              execSync(`chmod +x "${filePath}"`, { stdio: 'pipe' });
              console.log(chalk.green(`  ✅ Made executable: ${path.basename(filePath)}`));
            } catch (error) {
              // Silently skip files we can't chmod
            }
          }
        }
      }
    }
    
    console.log(chalk.green('✅ Executable permissions fixed'));
    
  } catch (error) {
    console.log(chalk.yellow(`⚠️  Permission fixing had issues: ${error.message}`));
  }
}

async function validatePythonScripts() {
  console.log(chalk.blue('🐍 Validating Python script shebangs...'));
  
  const packageRoot = path.resolve(__dirname, '..');
  const hooksDir = path.join(packageRoot, 'core', 'hooks', 'hooks');
  
  if (!(await fs.pathExists(hooksDir))) {
    console.log(chalk.yellow('⚠️  Hooks directory not found, skipping validation'));
    return;
  }
  
  const hookFiles = await fs.readdir(hooksDir);
  const pythonFiles = hookFiles.filter(file => file.endsWith('.py'));
  
  let fixedCount = 0;
  
  for (const file of pythonFiles) {
    const filePath = path.join(hooksDir, file);
    try {
      const content = await fs.readFile(filePath, 'utf8');
      const lines = content.split('\n');
      
      // Check if first line is a proper shebang
      if (!lines[0] || !lines[0].startsWith('#!/usr/bin/env python')) {
        // Add proper shebang
        const newContent = '#!/usr/bin/env python3\n' + content;
        await fs.writeFile(filePath, newContent);
        console.log(chalk.green(`  ✅ Added shebang to: ${file}`));
        fixedCount++;
      } else {
        console.log(chalk.gray(`  ✓ ${file} already has shebang`));
      }
    } catch (error) {
      console.log(chalk.yellow(`  ⚠️  Could not validate ${file}: ${error.message}`));
    }
  }
  
  if (fixedCount > 0) {
    console.log(chalk.green(`✅ Fixed shebangs in ${fixedCount} Python scripts`));
  } else {
    console.log(chalk.green('✅ All Python scripts have proper shebangs'));
  }
}

async function walkDirectory(dir) {
  const files = [];
  const entries = await fs.readdir(dir, { withFileTypes: true });
  
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      const subFiles = await walkDirectory(fullPath);
      files.push(...subFiles);
    } else {
      files.push(fullPath);
    }
  }
  
  return files;
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