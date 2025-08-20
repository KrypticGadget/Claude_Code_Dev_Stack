#!/usr/bin/env node

/**
 * Bootstrap script for postinstall
 * This script has NO dependencies and ensures required packages are installed
 * before running the fancy complete-install.js
 */

const { execSync } = require('child_process');
const path = require('path');

console.log('\n🚀 Claude Code Dev Stack V3 - Installation Starting...\n');

// Always install dependencies first (don't check, just install)
console.log('📦 Installing required dependencies...');

try {
  // Install dependencies silently
  execSync('npm install chalk fs-extra commander inquirer --no-save --silent', { 
    stdio: 'inherit',
    cwd: path.join(__dirname, '..')
  });
  console.log('✅ Dependencies installed\n');
} catch (error) {
  console.log('⚠️  Could not install dependencies automatically');
  console.log('   Continuing with basic setup...\n');
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