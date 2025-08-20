#!/usr/bin/env node

/**
 * Simple postinstall script for npm GitHub installations
 * This script is completely self-contained with no dependencies
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

console.log('\n🚀 Claude Code Dev Stack V3 - Installation Starting...\n');

// Helper to check if we're in the right directory
function findPackageRoot() {
  let currentDir = __dirname;
  // Go up until we find package.json with our name
  while (currentDir !== path.dirname(currentDir)) {
    const packagePath = path.join(currentDir, 'package.json');
    if (fs.existsSync(packagePath)) {
      try {
        const pkg = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
        if (pkg.name === '@claude-code/dev-stack') {
          return currentDir;
        }
      } catch (e) {
        // Continue searching
      }
    }
    currentDir = path.dirname(currentDir);
  }
  return path.join(__dirname, '..');
}

const rootDir = findPackageRoot();
console.log('📍 Installation root:', rootDir);

// Check if complete-install.js exists
const completeInstallPath = path.join(rootDir, 'scripts', 'complete-install.js');
const completeInstallExists = fs.existsSync(completeInstallPath);

if (!completeInstallExists) {
  console.log('⚠️  Complete installer not found at expected location');
  console.log('   This is normal for npm GitHub installations');
  console.log('');
  console.log('📦 Installing minimal required dependencies...');
  
  try {
    // Install only the most essential dependencies
    execSync('npm install chalk fs-extra --no-save --silent', { 
      stdio: 'inherit',
      cwd: rootDir
    });
  } catch (e) {
    console.log('⚠️  Could not install dependencies automatically');
  }
  
  // Create bin commands if they don't exist
  const binDir = path.join(rootDir, 'bin');
  if (!fs.existsSync(binDir)) {
    fs.mkdirSync(binDir, { recursive: true });
  }
  
  // Create minimal setup command
  const setupScript = `#!/usr/bin/env node
console.log('Claude Code Dev Stack V3 - Manual Setup');
console.log('');
console.log('To complete installation, run:');
console.log('  1. npm install -g @anthropic-ai/claude-code');
console.log('  2. npm install -g @modelcontextprotocol/server-github');
console.log('  3. npm install -g @automata-labs/playwright-mcp');
console.log('');
console.log('For full installation with all features:');
console.log('  git clone https://github.com/KrypticGadget/Claude_Code_Dev_Stack');
console.log('  cd Claude_Code_Dev_Stack');
console.log('  npm install');
console.log('  npm run complete-install');
`;

  const setupPath = path.join(binDir, 'claude-code-setup.js');
  if (!fs.existsSync(setupPath)) {
    fs.writeFileSync(setupPath, setupScript);
    if (process.platform !== 'win32') {
      fs.chmodSync(setupPath, '755');
    }
  }
  
  console.log('');
  console.log('✅ Basic installation complete!');
  console.log('');
  console.log('📋 Next Steps:');
  console.log('   1. Run: claude-code-setup');
  console.log('   2. Or clone the full repository for all features');
  console.log('');
  console.log('📚 Full documentation: https://github.com/KrypticGadget/Claude_Code_Dev_Stack');
  
} else {
  // We have the complete installer, so run it
  console.log('✅ Complete installer found');
  console.log('📦 Installing dependencies for full installation...');
  
  try {
    execSync('npm install chalk fs-extra commander inquirer --no-save --silent', { 
      stdio: 'inherit',
      cwd: rootDir
    });
    console.log('✅ Dependencies installed\n');
    
    console.log('🎨 Starting complete installation...\n');
    
    // Run the complete installer
    try {
      execSync(`node ${completeInstallPath}`, {
        stdio: 'inherit',
        cwd: rootDir,
        env: { ...process.env }
      });
    } catch (error) {
      console.error('⚠️  Complete installation had warnings');
      console.log('   You can run claude-code-setup manually to complete setup\n');
    }
  } catch (error) {
    console.error('⚠️  Could not run complete installation');
    console.log('   Run manually: npm run complete-install\n');
  }
}

// Always exit successfully to not break npm install
process.exit(0);