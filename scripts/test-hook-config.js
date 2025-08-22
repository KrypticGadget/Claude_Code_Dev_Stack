#!/usr/bin/env node

/**
 * Test script to verify hook configuration works correctly
 * This script simulates what Claude Code will do when loading hooks
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const { spawn } = require('child_process');

const CLAUDE_JSON = path.join(os.homedir(), '.claude.json');

function testHookExecution(hookCommand) {
  return new Promise((resolve) => {
    console.log(`\n🧪 Testing hook: ${hookCommand}`);
    
    // Parse the command to extract the Python script and arguments
    const parts = hookCommand.match(/"([^"]+)"/g);
    if (!parts || parts.length === 0) {
      console.log('❌ Could not parse hook command');
      resolve(false);
      return;
    }
    
    const scriptPath = parts[0].replace(/"/g, '');
    const pythonCmd = hookCommand.split(' ')[0];
    
    // Check if script exists
    if (!fs.existsSync(scriptPath)) {
      console.log(`❌ Script not found: ${scriptPath}`);
      resolve(false);
      return;
    }
    
    console.log(`✅ Script exists: ${scriptPath}`);
    
    // Test Python execution with --help flag
    const testProcess = spawn(pythonCmd, [scriptPath, '--help'], {
      stdio: 'pipe',
      timeout: 5000
    });
    
    let output = '';
    let errorOutput = '';
    
    testProcess.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    testProcess.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });
    
    testProcess.on('close', (code) => {
      if (code === 0 || output.includes('usage') || output.includes('help')) {
        console.log('✅ Hook executes successfully');
        resolve(true);
      } else {
        console.log(`❌ Hook execution failed (code: ${code})`);
        if (errorOutput) {
          console.log(`   Error: ${errorOutput.trim()}`);
        }
        resolve(false);
      }
    });
    
    testProcess.on('error', (error) => {
      console.log(`❌ Process error: ${error.message}`);
      resolve(false);
    });
  });
}

async function main() {
  console.log('🔍 Testing Claude Code Hook Configuration\n');
  
  // Check if .claude.json exists
  if (!fs.existsSync(CLAUDE_JSON)) {
    console.log('❌ .claude.json not found. Run setup first.');
    process.exit(1);
  }
  
  // Read and parse config
  let config;
  try {
    config = JSON.parse(fs.readFileSync(CLAUDE_JSON, 'utf8'));
  } catch (error) {
    console.log('❌ Could not parse .claude.json:', error.message);
    process.exit(1);
  }
  
  console.log('✅ .claude.json found and parsed');
  console.log(`📊 Found ${(config.hooks || []).length} hooks configured\n`);
  
  // Test each hook
  const hooks = config.hooks || [];
  let passedTests = 0;
  
  for (const hook of hooks) {
    const success = await testHookExecution(hook.command);
    if (success) passedTests++;
  }
  
  console.log(`\n📊 Test Results: ${passedTests}/${hooks.length} hooks passed`);
  
  if (passedTests === hooks.length) {
    console.log('🎉 All hooks configured correctly!');
    process.exit(0);
  } else {
    console.log('⚠️  Some hooks failed. Check Python installation and script paths.');
    process.exit(1);
  }
}

main().catch(error => {
  console.error('❌ Test failed:', error);
  process.exit(1);
});