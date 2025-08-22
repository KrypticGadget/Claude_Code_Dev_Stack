#!/usr/bin/env node

/**
 * Setup Verification Script for Claude Code Dev Stack V3
 * Verifies the complete installation and hook configuration
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync } = require('child_process');

const CLAUDE_JSON = path.join(os.homedir(), '.claude.json');

function checkClaudeCodeInstalled() {
  try {
    const result = execSync('claude --version', { encoding: 'utf8', stdio: 'pipe' });
    console.log('✅ Claude Code installed:', result.trim());
    return true;
  } catch (error) {
    console.log('❌ Claude Code not found');
    console.log('   Install with: npm install -g @anthropic-ai/claude-code');
    return false;
  }
}

function checkPythonAvailable() {
  const commands = process.platform === 'win32' ? ['python', 'py'] : ['python3', 'python'];
  
  for (const cmd of commands) {
    try {
      const result = execSync(`${cmd} --version`, { encoding: 'utf8', stdio: 'pipe' });
      console.log(`✅ Python available: ${cmd} (${result.trim()})`);
      return cmd;
    } catch (error) {
      // Continue to next command
    }
  }
  
  console.log('❌ Python not found');
  return null;
}

function verifyClaudeConfig() {
  console.log('\n🔍 Verifying Claude configuration...');
  
  if (!fs.existsSync(CLAUDE_JSON)) {
    console.log('❌ .claude.json not found');
    console.log(`   Expected location: ${CLAUDE_JSON}`);
    return false;
  }
  
  try {
    const config = JSON.parse(fs.readFileSync(CLAUDE_JSON, 'utf8'));
    
    // Check dev stack configuration
    if (!config.devStack) {
      console.log('❌ No devStack configuration found');
      return false;
    }
    
    console.log(`✅ Dev Stack v${config.devStack.version} configured`);
    
    // Check hooks
    const hooks = config.hooks || [];
    console.log(`✅ ${hooks.length} hooks configured`);
    
    // Verify critical hooks
    const criticalHooks = ['status_line_manager.py', 'smart_orchestrator.py'];
    let foundCritical = 0;
    
    for (const criticalHook of criticalHooks) {
      const found = hooks.some(hook => hook.command.includes(criticalHook));
      if (found) {
        foundCritical++;
        console.log(`✅ Critical hook found: ${criticalHook}`);
      } else {
        console.log(`❌ Critical hook missing: ${criticalHook}`);
      }
    }
    
    // Check MCP servers
    const mcpServers = Object.keys(config.mcpServers || {});
    console.log(`✅ ${mcpServers.length} MCP servers configured: ${mcpServers.join(', ')}`);
    
    return foundCritical === criticalHooks.length;
    
  } catch (error) {
    console.log('❌ Could not parse .claude.json:', error.message);
    return false;
  }
}

function verifyHookFiles() {
  console.log('\n📁 Verifying hook files...');
  
  const scriptDir = __dirname;
  const packageRoot = path.dirname(scriptDir);
  const hooksDir = path.join(packageRoot, 'core', 'hooks', 'hooks');
  
  if (!fs.existsSync(hooksDir)) {
    console.log(`❌ Hooks directory not found: ${hooksDir}`);
    return false;
  }
  
  console.log(`✅ Hooks directory found: ${hooksDir}`);
  
  const requiredHooks = [
    'status_line_manager.py',
    'smart_orchestrator.py',
    'audio_controller.py'
  ];
  
  let foundHooks = 0;
  for (const hook of requiredHooks) {
    const hookPath = path.join(hooksDir, hook);
    if (fs.existsSync(hookPath)) {
      foundHooks++;
      console.log(`✅ Found: ${hook}`);
    } else {
      console.log(`❌ Missing: ${hook}`);
    }
  }
  
  return foundHooks === requiredHooks.length;
}

function runQuickTest() {
  console.log('\n🧪 Running quick functionality test...');
  
  try {
    // Test basic Claude command
    execSync('claude --help', { stdio: 'pipe' });
    console.log('✅ Claude Code basic functionality works');
    
    return true;
  } catch (error) {
    console.log('❌ Claude Code test failed');
    return false;
  }
}

function main() {
  console.log('🔧 Claude Code Dev Stack V3 - Setup Verification\n');
  
  let allPassed = true;
  
  // Check 1: Claude Code installation
  console.log('1️⃣ Checking Claude Code installation...');
  if (!checkClaudeCodeInstalled()) {
    allPassed = false;
  }
  
  // Check 2: Python availability
  console.log('\n2️⃣ Checking Python availability...');
  const pythonCmd = checkPythonAvailable();
  if (!pythonCmd) {
    allPassed = false;
  }
  
  // Check 3: Claude configuration
  console.log('\n3️⃣ Checking Claude configuration...');
  if (!verifyClaudeConfig()) {
    allPassed = false;
  }
  
  // Check 4: Hook files
  console.log('\n4️⃣ Checking hook files...');
  if (!verifyHookFiles()) {
    allPassed = false;
  }
  
  // Check 5: Basic functionality
  console.log('\n5️⃣ Testing basic functionality...');
  if (!runQuickTest()) {
    allPassed = false;
  }
  
  // Final result
  console.log('\n' + '='.repeat(60));
  
  if (allPassed) {
    console.log('🎉 VERIFICATION PASSED!');
    console.log('\n✅ Your Claude Code Dev Stack V3 is ready to use!');
    console.log('\n🚀 Try these commands:');
    console.log('   claude "help"');
    console.log('   claude "@master-orchestrator list agents"');
    console.log('   claude "status"');
    
  } else {
    console.log('❌ VERIFICATION FAILED!');
    console.log('\n🔧 Please run the setup again:');
    console.log('   npm run validate-hooks');
    console.log('   node bin/claude-code-setup-simple.js');
  }
  
  console.log('\n📚 Documentation: https://claude-code.dev/docs');
  console.log('🐛 Issues: https://github.com/claude-code/dev-stack/issues');
}

main();