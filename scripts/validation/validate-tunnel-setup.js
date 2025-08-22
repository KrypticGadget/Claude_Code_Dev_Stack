#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🔧 Claude Code Tunnel Management - Setup Validation');
console.log('=' + '='.repeat(60));

let errors = [];
let warnings = [];
let success = [];

// Check package.json bin commands
try {
  const packagePath = path.resolve(__dirname, '../package.json');
  const packageData = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
  
  const tunnelCommands = [
    'claude-code-tunnel-start',
    'claude-code-tunnel-stop', 
    'claude-code-tunnel-status',
    'claude-code-tunnel-restart',
    'claude-code-tunnel-config'
  ];
  
  for (const cmd of tunnelCommands) {
    if (packageData.bin && packageData.bin[cmd]) {
      success.push(`✅ Command registered: ${cmd}`);
    } else {
      errors.push(`❌ Missing bin command: ${cmd}`);
    }
  }
  
  // Check dependencies
  const requiredDeps = ['qrcode', 'qrcode-terminal', 'clipboardy'];
  for (const dep of requiredDeps) {
    if (packageData.dependencies && packageData.dependencies[dep]) {
      success.push(`✅ Dependency: ${dep}`);
    } else {
      errors.push(`❌ Missing dependency: ${dep}`);
    }
  }
  
} catch (error) {
  errors.push(`❌ Cannot read package.json: ${error.message}`);
}

// Check CLI files
const binDir = path.resolve(__dirname, '../bin');
const cliFiles = [
  'claude-code-tunnel-start.js',
  'claude-code-tunnel-stop.js',
  'claude-code-tunnel-status.js',
  'claude-code-tunnel-restart.js',
  'claude-code-tunnel-config.js'
];

for (const file of cliFiles) {
  const filePath = path.join(binDir, file);
  try {
    fs.accessSync(filePath);
    success.push(`✅ CLI file: ${file}`);
  } catch {
    errors.push(`❌ Missing CLI file: ${file}`);
  }
}

// Check config files
const configFiles = [
  '../config/tunnel/tunnel-config.json',
  '../config/ngrok/ngrok.yml',
  '../lib/tunnel/tunnel-manager.js'
];

for (const file of configFiles) {
  const filePath = path.resolve(__dirname, file);
  try {
    fs.accessSync(filePath);
    success.push(`✅ Config file: ${path.relative(process.cwd(), filePath)}`);
  } catch {
    errors.push(`❌ Missing config file: ${path.relative(process.cwd(), filePath)}`);
  }
}

// Check directories
const requiredDirs = [
  '../logs',
  '../config/tunnel',
  '../config/ngrok',
  '../lib/tunnel'
];

for (const dir of requiredDirs) {
  const dirPath = path.resolve(__dirname, dir);
  try {
    const stat = fs.statSync(dirPath);
    if (stat.isDirectory()) {
      success.push(`✅ Directory: ${path.relative(process.cwd(), dirPath)}`);
    } else {
      warnings.push(`⚠️ Not a directory: ${path.relative(process.cwd(), dirPath)}`);
    }
  } catch {
    warnings.push(`⚠️ Missing directory: ${path.relative(process.cwd(), dirPath)}`);
  }
}

// Print results
console.log('\\n📋 Validation Results:');
console.log('-'.repeat(60));

if (success.length > 0) {
  console.log('\\n✅ Success:');
  success.forEach(msg => console.log(`   ${msg}`));
}

if (warnings.length > 0) {
  console.log('\\n⚠️ Warnings:');
  warnings.forEach(msg => console.log(`   ${msg}`));
}

if (errors.length > 0) {
  console.log('\\n❌ Errors:');
  errors.forEach(msg => console.log(`   ${msg}`));
}

console.log('\\n📊 Summary:');
console.log(`   Success: ${success.length}`);
console.log(`   Warnings: ${warnings.length}`);
console.log(`   Errors: ${errors.length}`);

if (errors.length === 0) {
  console.log('\\n🎉 Tunnel management system is properly configured!');
  console.log('\\n💡 Next steps:');
  console.log('   1. Install dependencies: npm install');
  console.log('   2. Get ngrok token: https://dashboard.ngrok.com/auth');
  console.log('   3. Set NGROK_AUTHTOKEN environment variable');
  console.log('   4. Run: claude-code-tunnel-start');
} else {
  console.log('\\n⚠️ Please fix the errors above before using tunnel management.');
  process.exit(1);
}