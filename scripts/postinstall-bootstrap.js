#!/usr/bin/env node

/**
 * Bootstrap script for postinstall
 * This script has NO dependencies and ensures required packages are installed
 * before running the fancy complete-install.js
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('\n🚀 Claude Code Dev Stack V3 - Installation Starting...\n');

// Check if we're in a global install context
const isGlobalInstall = process.env.npm_config_global === 'true';

// List of required dependencies for the installer
const requiredDeps = ['chalk', 'fs-extra'];
const missingDeps = [];

// Check which dependencies are missing
for (const dep of requiredDeps) {
  try {
    require.resolve(dep);
  } catch {
    missingDeps.push(dep);
  }
}

// If dependencies are missing, install them
if (missingDeps.length > 0) {
  console.log('📦 Installing required dependencies for setup...');
  console.log(`   Missing: ${missingDeps.join(', ')}\n`);
  
  try {
    // Install missing dependencies locally in the package directory
    const installCmd = `npm install ${missingDeps.join(' ')} --no-save --silent`;
    execSync(installCmd, { 
      stdio: 'inherit',
      cwd: path.join(__dirname, '..')
    });
    console.log('✅ Dependencies installed\n');
  } catch (error) {
    console.error('⚠️  Could not install dependencies automatically');
    console.error('   Please run the setup manually: claude-code-setup\n');
    process.exit(0); // Exit gracefully, don't fail the install
  }
}

// Now run the complete installer
try {
  console.log('🎨 Starting fancy installation...\n');
  
  // Use child_process to run the ES module script
  const scriptPath = path.join(__dirname, 'complete-install.js');
  const result = execSync(`node ${scriptPath}`, {
    stdio: 'inherit',
    cwd: path.join(__dirname, '..'),
    env: { ...process.env }
  });
} catch (error) {
  console.error('⚠️  Complete installation failed:', error.message);
  console.log('\n💡 You can complete setup manually by running:');
  console.log('   claude-code-setup\n');
  
  // Don't fail the npm install
  process.exit(0);
}