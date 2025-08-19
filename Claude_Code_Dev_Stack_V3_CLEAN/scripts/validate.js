#!/usr/bin/env node

/**
 * Validation script for Claude Code Dev Stack V3
 */

import chalk from 'chalk';
import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function validatePackage() {
  console.log(chalk.blue('🔍 Validating Claude Code Dev Stack V3 Package'));
  console.log(chalk.blue('═'.repeat(50)));
  
  let validationPassed = true;
  const issues = [];
  
  try {
    const packageRoot = path.dirname(__dirname);
    
    // Validate package.json
    console.log(chalk.yellow('📦 Validating package.json...'));
    const packageJsonPath = path.join(packageRoot, 'package.json');
    
    if (await fs.pathExists(packageJsonPath)) {
      const packageJson = await fs.readJSON(packageJsonPath);
      
      // Required fields
      const requiredFields = ['name', 'version', 'description', 'main', 'bin', 'scripts'];
      for (const field of requiredFields) {
        if (!packageJson[field]) {
          issues.push(`Missing required field: ${field}`);
          validationPassed = false;
        }
      }
      
      // Validate name
      if (packageJson.name !== '@claude-code/dev-stack') {
        issues.push(`Invalid package name: ${packageJson.name}`);
        validationPassed = false;
      }
      
      // Validate version
      if (!packageJson.version || !packageJson.version.match(/^\d+\.\d+\.\d+$/)) {
        issues.push(`Invalid version format: ${packageJson.version}`);
        validationPassed = false;
      }
      
      console.log(chalk.green('  ✅ package.json validation passed'));
    } else {
      issues.push('package.json not found');
      validationPassed = false;
    }
    
    // Validate main entry point
    console.log(chalk.yellow('🎯 Validating entry point...'));
    const indexPath = path.join(packageRoot, 'index.js');
    
    if (await fs.pathExists(indexPath)) {
      console.log(chalk.green('  ✅ index.js found'));
    } else {
      issues.push('index.js not found');
      validationPassed = false;
    }
    
    // Validate bin scripts
    console.log(chalk.yellow('🔧 Validating CLI scripts...'));
    const binDir = path.join(packageRoot, 'bin');
    
    if (await fs.pathExists(binDir)) {
      const expectedBinFiles = [
        'claude-code-setup.js',
        'claude-code-agents.js', 
        'claude-code-hooks.js'
      ];
      
      for (const binFile of expectedBinFiles) {
        const binPath = path.join(binDir, binFile);
        if (await fs.pathExists(binPath)) {
          console.log(chalk.green(`  ✅ ${binFile} found`));
        } else {
          issues.push(`Missing bin script: ${binFile}`);
          validationPassed = false;
        }
      }
    } else {
      issues.push('bin directory not found');
      validationPassed = false;
    }
    
    // Validate lib directory
    console.log(chalk.yellow('📚 Validating lib directory...'));
    const libDir = path.join(packageRoot, 'lib');
    
    if (await fs.pathExists(libDir)) {
      const expectedLibDirs = [
        'agents',
        'hooks',
        'audio',
        'config',
        'orchestration',
        'ui'
      ];
      
      for (const libSubDir of expectedLibDirs) {
        const libPath = path.join(libDir, libSubDir);
        if (await fs.pathExists(libPath)) {
          console.log(chalk.green(`  ✅ lib/${libSubDir} found`));
        } else {
          issues.push(`Missing lib directory: ${libSubDir}`);
          validationPassed = false;
        }
      }
    } else {
      issues.push('lib directory not found');
      validationPassed = false;
    }
    
    // Validate core directories
    console.log(chalk.yellow('🏗️  Validating core directories...'));
    const coreDir = path.join(packageRoot, 'core');
    
    if (await fs.pathExists(coreDir)) {
      const expectedCoreDirs = [
        'agents/agents',
        'hooks/hooks',
        'audio/audio'
      ];
      
      for (const coreSubDir of expectedCoreDirs) {
        const corePath = path.join(coreDir, coreSubDir);
        if (await fs.pathExists(corePath)) {
          // Count files
          const files = await fs.readdir(corePath);
          console.log(chalk.green(`  ✅ core/${coreSubDir} found (${files.length} files)`));
        } else {
          issues.push(`Missing core directory: ${coreSubDir}`);
          validationPassed = false;
        }
      }
    } else {
      issues.push('core directory not found');
      validationPassed = false;
    }
    
    // Validate agents
    console.log(chalk.yellow('🤖 Validating agents...'));
    const agentsDir = path.join(packageRoot, 'core', 'agents', 'agents');
    
    if (await fs.pathExists(agentsDir)) {
      const agentFiles = await fs.readdir(agentsDir);
      const mdFiles = agentFiles.filter(f => f.endsWith('.md'));
      
      if (mdFiles.length >= 25) { // Allow some variance
        console.log(chalk.green(`  ✅ ${mdFiles.length} agent files found`));
      } else {
        issues.push(`Insufficient agent files: ${mdFiles.length} (expected ~28)`);
        validationPassed = false;
      }
    }
    
    // Validate hooks
    console.log(chalk.yellow('🪝 Validating hooks...'));
    const hooksDir = path.join(packageRoot, 'core', 'hooks', 'hooks');
    
    if (await fs.pathExists(hooksDir)) {
      const hookFiles = await fs.readdir(hooksDir);
      const pyFiles = hookFiles.filter(f => f.endsWith('.py') && !f.startsWith('__'));
      
      if (pyFiles.length >= 30) { // Allow some variance
        console.log(chalk.green(`  ✅ ${pyFiles.length} hook files found`));
      } else {
        issues.push(`Insufficient hook files: ${pyFiles.length} (expected ~37)`);
        validationPassed = false;
      }
    }
    
    // Validate audio files
    console.log(chalk.yellow('🔊 Validating audio files...'));
    const audioDir = path.join(packageRoot, 'core', 'audio', 'audio');
    
    if (await fs.pathExists(audioDir)) {
      const audioFiles = await fs.readdir(audioDir);
      const wavFiles = audioFiles.filter(f => f.endsWith('.wav'));
      
      if (wavFiles.length >= 80) { // Allow some variance
        console.log(chalk.green(`  ✅ ${wavFiles.length} audio files found`));
      } else {
        issues.push(`Insufficient audio files: ${wavFiles.length} (expected ~90)`);
        validationPassed = false;
      }
    }
    
    // Validate UI
    console.log(chalk.yellow('🎨 Validating UI...'));
    const uiDir = path.join(packageRoot, 'ui', 'react-pwa');
    
    if (await fs.pathExists(uiDir)) {
      const uiPackageJson = path.join(uiDir, 'package.json');
      if (await fs.pathExists(uiPackageJson)) {
        console.log(chalk.green('  ✅ React PWA found'));
      } else {
        issues.push('React PWA package.json not found');
        validationPassed = false;
      }
    } else {
      console.log(chalk.yellow('  ⚠️  React PWA not found (optional)'));
    }
    
  } catch (error) {
    issues.push(`Validation error: ${error.message}`);
    validationPassed = false;
  }
  
  // Summary
  console.log(chalk.blue('\n📊 Validation Results:'));
  
  if (validationPassed) {
    console.log(chalk.green('🎉 Package validation passed!'));
    console.log(chalk.blue('\n✨ Claude Code Dev Stack V3 is ready for publication'));
  } else {
    console.log(chalk.red('❌ Package validation failed'));
    console.log(chalk.red('\n🐛 Issues found:'));
    issues.forEach(issue => {
      console.log(chalk.red(`  • ${issue}`));
    });
  }
  
  process.exit(validationPassed ? 0 : 1);
}

validatePackage().catch(error => {
  console.error(chalk.red('Validation failed:'), error);
  process.exit(1);
});