#!/usr/bin/env node

/**
 * Validation Script for Claude Code Dev Stack V3
 * Validates that all permissions and paths are correctly set
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
║     ✅ Claude Code Dev Stack V3 - Permission Validator ✅       ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
`;

async function main() {
  console.log(chalk.cyan(banner));
  
  console.log(chalk.blue('🔍 Validating executable permissions and paths...'));
  
  const packageRoot = path.resolve(__dirname, '..');
  let issues = [];
  let successes = [];
  
  try {
    // Validate bin scripts
    const binValidation = await validateBinScripts(packageRoot);
    issues.push(...binValidation.issues);
    successes.push(...binValidation.successes);
    
    // Validate Python hooks
    const pythonValidation = await validatePythonHooks(packageRoot);
    issues.push(...pythonValidation.issues);
    successes.push(...pythonValidation.successes);
    
    // Validate path resolution
    const pathValidation = await validatePathResolution(packageRoot);
    issues.push(...pathValidation.issues);
    successes.push(...pathValidation.successes);
    
    // Validate Python detection
    const pythonDetection = await validatePythonDetection();
    issues.push(...pythonDetection.issues);
    successes.push(...pythonDetection.successes);
    
    // Report results
    console.log(chalk.blue('\n📋 Validation Results:'));
    
    if (successes.length > 0) {
      console.log(chalk.green(`\n✅ Successful checks (${successes.length}):`));
      successes.forEach(success => {
        console.log(chalk.green(`  ✅ ${success}`));
      });
    }
    
    if (issues.length > 0) {
      console.log(chalk.red(`\n❌ Issues found (${issues.length}):`));
      issues.forEach(issue => {
        console.log(chalk.red(`  ❌ ${issue}`));
      });
      
      console.log(chalk.yellow('\n💡 To fix issues, run:'));
      console.log(chalk.white('   npm run fix-permissions'));
      console.log(chalk.white('   # or on Unix systems:'));
      console.log(chalk.white('   bash scripts/fix-permissions.sh'));
      
      process.exit(1);
    } else {
      console.log(chalk.green('\n🎉 All validations passed! Everything looks good.'));
      console.log(chalk.blue('📦 Ready for global npm install:'));
      console.log(chalk.white('   npm install -g github:KrypticGadget/Claude_Code_Dev_Stack#feature/v3-dev'));
    }
    
  } catch (error) {
    console.error(chalk.red('❌ Validation failed:'), error.message);
    process.exit(1);
  }
}

async function validateBinScripts(packageRoot) {
  const issues = [];
  const successes = [];
  
  console.log(chalk.blue('🔧 Validating bin scripts...'));
  
  const binDir = path.join(packageRoot, 'bin');
  
  if (!(await fs.pathExists(binDir))) {
    issues.push('Bin directory does not exist');
    return { issues, successes };
  }
  
  const binFiles = await fs.readdir(binDir);
  const jsFiles = binFiles.filter(file => file.endsWith('.js'));
  
  for (const file of jsFiles) {
    const filePath = path.join(binDir, file);
    
    // Check if file has shebang
    const content = await fs.readFile(filePath, 'utf8');
    if (!content.startsWith('#!/usr/bin/env node')) {
      issues.push(`${file} missing proper shebang`);
    } else {
      successes.push(`${file} has proper shebang`);
    }
    
    // Check executable permissions on Unix
    if (os.platform() !== 'win32') {
      try {
        const stats = await fs.stat(filePath);
        if (!(stats.mode & parseInt('111', 8))) {
          issues.push(`${file} not executable`);
        } else {
          successes.push(`${file} is executable`);
        }
      } catch (error) {
        issues.push(`Could not check permissions for ${file}`);
      }
    } else {
      successes.push(`${file} permissions (Windows - OK)`);
    }
  }
  
  return { issues, successes };
}

async function validatePythonHooks(packageRoot) {
  const issues = [];
  const successes = [];
  
  console.log(chalk.blue('🐍 Validating Python hook scripts...'));
  
  const hooksDir = path.join(packageRoot, 'core', 'hooks', 'hooks');
  
  if (!(await fs.pathExists(hooksDir))) {
    issues.push('Hooks directory does not exist');
    return { issues, successes };
  }
  
  const hookFiles = await fs.readdir(hooksDir);
  const pythonFiles = hookFiles.filter(file => file.endsWith('.py'));
  
  for (const file of pythonFiles) {
    const filePath = path.join(hooksDir, file);
    
    // Check if file has proper shebang
    const content = await fs.readFile(filePath, 'utf8');
    const lines = content.split('\n');
    
    if (!lines[0] || !lines[0].startsWith('#!/usr/bin/env python')) {
      issues.push(`${file} missing proper shebang`);
    } else {
      successes.push(`${file} has proper shebang`);
    }
    
    // Check executable permissions on Unix
    if (os.platform() !== 'win32') {
      try {
        const stats = await fs.stat(filePath);
        if (!(stats.mode & parseInt('111', 8))) {
          issues.push(`${file} not executable`);
        } else {
          successes.push(`${file} is executable`);
        }
      } catch (error) {
        issues.push(`Could not check permissions for ${file}`);
      }
    } else {
      successes.push(`${file} permissions (Windows - OK)`);
    }
  }
  
  return { issues, successes };
}

async function validatePathResolution(packageRoot) {
  const issues = [];
  const successes = [];
  
  console.log(chalk.blue('🔗 Validating path resolution...'));
  
  const setupScript = path.join(packageRoot, 'bin', 'claude-code-setup-simple.js');
  
  if (!(await fs.pathExists(setupScript))) {
    issues.push('Setup script does not exist');
    return { issues, successes };
  }
  
  const content = await fs.readFile(setupScript, 'utf8');
  
  // Check for improved path resolution
  if (content.includes('Dynamic path resolution for global npm installs')) {
    successes.push('Setup script has improved path resolution');
  } else {
    issues.push('Setup script lacks improved path resolution');
  }
  
  // Check for improved Python detection
  if (content.includes('Cross-platform Python command detection')) {
    successes.push('Setup script has improved Python detection');
  } else {
    issues.push('Setup script lacks improved Python detection');
  }
  
  return { issues, successes };
}

async function validatePythonDetection() {
  const issues = [];
  const successes = [];
  
  console.log(chalk.blue('🐍 Validating Python detection...'));
  
  try {
    // Try python3 first
    execSync('python3 --version', { stdio: 'pipe' });
    successes.push('python3 is available');
  } catch {
    try {
      // Try python
      execSync('python --version', { stdio: 'pipe' });
      successes.push('python is available');
    } catch {
      issues.push('Neither python3 nor python found in PATH');
    }
  }
  
  return { issues, successes };
}

// Run validation
main().catch(console.error);