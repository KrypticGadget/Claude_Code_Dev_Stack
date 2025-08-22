#!/usr/bin/env node

/**
 * Test runner for Claude Code Dev Stack V3
 */

import chalk from 'chalk';
import { ClaudeCodeDevStack } from '../index.js';

async function runTests() {
  console.log(chalk.blue('🧪 Running Claude Code Dev Stack V3 Tests'));
  console.log(chalk.blue('═'.repeat(50)));
  
  let passedTests = 0;
  let failedTests = 0;
  
  try {
    // Test 1: Initialization
    console.log(chalk.yellow('🔄 Testing initialization...'));
    const stack = new ClaudeCodeDevStack();
    const initResult = await stack.initialize();
    
    if (initResult.success) {
      console.log(chalk.green('  ✅ Initialization test passed'));
      passedTests++;
    } else {
      console.log(chalk.red('  ❌ Initialization test failed'));
      failedTests++;
    }
    
    // Test 2: Agent Manager
    console.log(chalk.yellow('🔄 Testing agent manager...'));
    const agentStatus = stack.agentManager.getStatus();
    
    if (agentStatus.available > 0) {
      console.log(chalk.green(`  ✅ Agent manager test passed (${agentStatus.available} agents available)`));
      passedTests++;
    } else {
      console.log(chalk.red('  ❌ Agent manager test failed'));
      failedTests++;
    }
    
    // Test 3: Hook Manager
    console.log(chalk.yellow('🔄 Testing hook manager...'));
    const hookStatus = stack.hookManager.getStatus();
    
    if (hookStatus.available > 0) {
      console.log(chalk.green(`  ✅ Hook manager test passed (${hookStatus.available} hooks available)`));
      passedTests++;
    } else {
      console.log(chalk.red('  ❌ Hook manager test failed'));
      failedTests++;
    }
    
    // Test 4: Audio Manager
    console.log(chalk.yellow('🔄 Testing audio manager...'));
    const audioStatus = stack.audioManager.getStatus();
    
    if (audioStatus.files > 0) {
      console.log(chalk.green(`  ✅ Audio manager test passed (${audioStatus.files} audio files available)`));
      passedTests++;
    } else {
      console.log(chalk.red('  ❌ Audio manager test failed'));
      failedTests++;
    }
    
    // Test 5: Configuration Manager
    console.log(chalk.yellow('🔄 Testing configuration manager...'));
    const configStatus = stack.configManager.initialized;
    
    if (configStatus) {
      console.log(chalk.green('  ✅ Configuration manager test passed'));
      passedTests++;
    } else {
      console.log(chalk.red('  ❌ Configuration manager test failed'));
      failedTests++;
    }
    
    // Test 6: Orchestration Engine
    console.log(chalk.yellow('🔄 Testing orchestration engine...'));
    const orchestrationStatus = stack.orchestrationEngine.getStatus();
    
    if (orchestrationStatus.initialized) {
      console.log(chalk.green('  ✅ Orchestration engine test passed'));
      passedTests++;
    } else {
      console.log(chalk.red('  ❌ Orchestration engine test failed'));
      failedTests++;
    }
    
    // Test 7: UI Manager
    console.log(chalk.yellow('🔄 Testing UI manager...'));
    const uiStatus = stack.uiManager.getStatus();
    
    if (uiStatus.initialized) {
      console.log(chalk.green('  ✅ UI manager test passed'));
      passedTests++;
    } else {
      console.log(chalk.red('  ❌ UI manager test failed'));
      failedTests++;
    }
    
    // Test 8: System Status
    console.log(chalk.yellow('🔄 Testing system status...'));
    const systemStatus = stack.getStatus();
    
    if (systemStatus.initialized) {
      console.log(chalk.green('  ✅ System status test passed'));
      passedTests++;
    } else {
      console.log(chalk.red('  ❌ System status test failed'));
      failedTests++;
    }
    
  } catch (error) {
    console.log(chalk.red(`  ❌ Test suite error: ${error.message}`));
    failedTests++;
  }
  
  // Summary
  console.log(chalk.blue('\n📊 Test Results:'));
  console.log(`  • Passed: ${chalk.green(passedTests)}`);
  console.log(`  • Failed: ${chalk.red(failedTests)}`);
  console.log(`  • Total: ${passedTests + failedTests}`);
  
  if (failedTests === 0) {
    console.log(chalk.green('\n🎉 All tests passed!'));
    process.exit(0);
  } else {
    console.log(chalk.red('\n❌ Some tests failed'));
    process.exit(1);
  }
}

runTests().catch(error => {
  console.error(chalk.red('Test runner failed:'), error);
  process.exit(1);
});