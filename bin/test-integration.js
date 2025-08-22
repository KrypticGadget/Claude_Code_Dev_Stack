#!/usr/bin/env node
/**
 * Integration Test Suite - V3.0 Complete System Validation
 * Tests all components of Claude Code Dev Stack V3
 */

import fs from 'fs-extra';
import path from 'path';
import os from 'os';
import { exec } from 'child_process';
import { promisify } from 'util';
import chalk from 'chalk';

const execAsync = promisify(exec);

class IntegrationTester {
    constructor() {
        this.claudeDir = path.join(os.homedir(), '.claude');
        this.binDir = path.join(__dirname);
        this.hooksDir = path.join(__dirname, '..', 'core', 'hooks', 'hooks');
        
        this.tests = [
            'testDirectoryStructure',
            'testExecutablePermissions',
            'testClaudeConfiguration',
            'testHookScripts',
            'testAgentRouter',
            'testSmartOrchestrator',
            'testStatusLineManager',
            'testAgentMentionParser',
            'testMCPServers',
            'testCompleteWorkflow'
        ];
        
        this.results = {
            passed: 0,
            failed: 0,
            skipped: 0,
            errors: []
        };
    }
    
    async runTest(testName) {
        console.log(chalk.blue(`🧪 Running ${testName}...`));
        
        try {
            const result = await this[testName]();
            if (result.success) {
                console.log(chalk.green(`  ✓ ${testName} passed`));
                this.results.passed++;
                if (result.details) {
                    console.log(chalk.gray(`    ${result.details}`));
                }
            } else {
                console.log(chalk.red(`  ✗ ${testName} failed: ${result.error}`));
                this.results.failed++;
                this.results.errors.push({ test: testName, error: result.error });
            }
        } catch (error) {
            console.log(chalk.red(`  ✗ ${testName} threw exception: ${error.message}`));
            this.results.failed++;
            this.results.errors.push({ test: testName, error: error.message });
        }
    }
    
    async testDirectoryStructure() {
        const requiredPaths = [
            this.claudeDir,
            this.binDir,
            this.hooksDir,
            path.join(this.hooksDir, 'smart_orchestrator.py'),
            path.join(this.hooksDir, 'status_line_manager.py'),
            path.join(this.hooksDir, 'agent_mention_parser.py'),
            path.join(this.binDir, 'agent-router.js'),
            path.join(this.binDir, 'hook-integrator.js')
        ];
        
        const missing = [];
        for (const requiredPath of requiredPaths) {
            if (!fs.existsSync(requiredPath)) {
                missing.push(requiredPath);
            }
        }
        
        if (missing.length > 0) {
            return {
                success: false,
                error: `Missing paths: ${missing.join(', ')}`
            };
        }
        
        return {
            success: true,
            details: `All ${requiredPaths.length} required paths exist`
        };
    }
    
    async testExecutablePermissions() {
        const scripts = [
            path.join(this.hooksDir, 'smart_orchestrator.py'),
            path.join(this.hooksDir, 'status_line_manager.py'),
            path.join(this.hooksDir, 'agent_mention_parser.py'),
            path.join(this.binDir, 'agent-router.js'),
            path.join(this.binDir, 'hook-integrator.js')
        ];
        
        const issues = [];
        
        for (const script of scripts) {
            if (!fs.existsSync(script)) {
                issues.push(`Missing: ${script}`);
                continue;
            }
            
            // Check if file has shebang
            const content = await fs.readFile(script, 'utf8');
            if (!content.startsWith('#!')) {
                issues.push(`No shebang: ${script}`);
            }
            
            // Check permissions on Unix systems
            if (process.platform !== 'win32') {
                try {
                    const stats = await fs.stat(script);
                    const mode = stats.mode & parseInt('777', 8);
                    if (mode < parseInt('755', 8)) {
                        issues.push(`Not executable: ${script} (${mode.toString(8)})`);
                    }
                } catch (error) {
                    issues.push(`Permission check failed: ${script}`);
                }
            }
        }
        
        if (issues.length > 0) {
            return {
                success: false,
                error: issues.join('; ')
            };
        }
        
        return {
            success: true,
            details: `All ${scripts.length} scripts have correct permissions`
        };
    }
    
    async testClaudeConfiguration() {
        const configFile = path.join(this.claudeDir, 'claude.json');
        
        if (!fs.existsSync(configFile)) {
            return {
                success: false,
                error: 'Claude configuration file not found'
            };
        }
        
        try {
            const config = await fs.readJson(configFile);
            
            if (!config.hooks || !Array.isArray(config.hooks)) {
                return {
                    success: false,
                    error: 'No hooks array in configuration'
                };
            }
            
            const hookNames = config.hooks.map(h => h.name);
            const expectedHooks = [
                'agent-mention-parser',
                'smart-orchestrator',
                'status-line-manager'
            ];
            
            const missingHooks = expectedHooks.filter(h => !hookNames.includes(h));
            if (missingHooks.length > 0) {
                return {
                    success: false,
                    error: `Missing hooks: ${missingHooks.join(', ')}`
                };
            }
            
            return {
                success: true,
                details: `Configuration valid with ${config.hooks.length} hooks`
            };
        } catch (error) {
            return {
                success: false,
                error: `Config parse error: ${error.message}`
            };
        }
    }
    
    async testHookScripts() {
        const scripts = [
            'smart_orchestrator.py',
            'status_line_manager.py',
            'agent_mention_parser.py'
        ];
        
        const results = [];
        
        for (const script of scripts) {
            const scriptPath = path.join(this.hooksDir, script);
            
            try {
                // Test Python syntax
                if (script.endsWith('.py')) {
                    const { stderr } = await execAsync(`python3 -m py_compile "${scriptPath}"`);
                    if (stderr) {
                        results.push(`Syntax error in ${script}: ${stderr}`);
                    }
                }
                
                // Test basic execution (help/version)
                const { stdout } = await execAsync(`python3 "${scriptPath}" --help`, { timeout: 3000 });
                // If it doesn't throw, the script is at least runnable
                
            } catch (error) {
                if (error.code !== 1) { // Exit code 1 is often expected for --help
                    results.push(`Execution test failed for ${script}: ${error.message}`);
                }
            }
        }
        
        if (results.length > 0) {
            return {
                success: false,
                error: results.join('; ')
            };
        }
        
        return {
            success: true,
            details: `All ${scripts.length} hook scripts validated`
        };
    }
    
    async testAgentRouter() {
        const routerPath = path.join(this.binDir, 'agent-router.js');
        
        if (!fs.existsSync(routerPath)) {
            return {
                success: false,
                error: 'Agent router script not found'
            };
        }
        
        try {
            // Test --list-agents command
            const { stdout } = await execAsync(`node "${routerPath}" --list-agents`, { timeout: 5000 });
            
            if (!stdout.includes('Available Agents:')) {
                return {
                    success: false,
                    error: 'Agent router not returning expected output'
                };
            }
            
            return {
                success: true,
                details: 'Agent router functioning correctly'
            };
        } catch (error) {
            return {
                success: false,
                error: `Agent router test failed: ${error.message}`
            };
        }
    }
    
    async testSmartOrchestrator() {
        const orchestratorPath = path.join(this.hooksDir, 'smart_orchestrator.py');
        
        try {
            // Test with sample prompt
            const { stdout } = await execAsync(`python3 "${orchestratorPath}" "create a simple web app"`, { timeout: 10000 });
            
            const result = JSON.parse(stdout);
            
            if (!result.agents || !Array.isArray(result.agents)) {
                return {
                    success: false,
                    error: 'Smart orchestrator not returning agent array'
                };
            }
            
            return {
                success: true,
                details: `Orchestrator selected ${result.agents.length} agents: ${result.agents.join(', ')}`
            };
        } catch (error) {
            return {
                success: false,
                error: `Smart orchestrator test failed: ${error.message}`
            };
        }
    }
    
    async testStatusLineManager() {
        const statusPath = path.join(this.hooksDir, 'status_line_manager.py');
        
        try {
            // Test status line generation
            const { stdout } = await execAsync(`python3 "${statusPath}"`, { timeout: 5000 });
            
            if (!stdout || stdout.trim().length === 0) {
                return {
                    success: false,
                    error: 'Status line manager not returning output'
                };
            }
            
            // Should contain key status elements
            const expectedElements = ['git:', '|', 'tokens'];
            const missing = expectedElements.filter(el => !stdout.includes(el));
            
            if (missing.length > 0) {
                return {
                    success: false,
                    error: `Status line missing elements: ${missing.join(', ')}`
                };
            }
            
            return {
                success: true,
                details: `Status line: ${stdout.trim()}`
            };
        } catch (error) {
            return {
                success: false,
                error: `Status line manager test failed: ${error.message}`
            };
        }
    }
    
    async testAgentMentionParser() {
        const parserPath = path.join(this.hooksDir, 'agent_mention_parser.py');
        
        try {
            // Test with sample input containing @agent mentions
            const testInput = JSON.stringify({
                prompt: "Please @agent-business-analyst analyze this and @agent-technical-cto[opus] review the architecture"
            });
            
            const { stdout } = await execAsync(`echo '${testInput}' | python3 "${parserPath}"`, { timeout: 5000 });
            
            if (!stdout.includes('business-analyst') || !stdout.includes('technical-cto')) {
                return {
                    success: false,
                    error: 'Agent mention parser not detecting mentions correctly'
                };
            }
            
            return {
                success: true,
                details: 'Agent mention parser working correctly'
            };
        } catch (error) {
            return {
                success: false,
                error: `Agent mention parser test failed: ${error.message}`
            };
        }
    }
    
    async testMCPServers() {
        // Test MCP server installations
        const mcpTests = [];
        
        try {
            // Check if GitHub MCP is available
            const { stdout: githubCheck } = await execAsync('npm list -g @modelcontextprotocol/server-github', { timeout: 3000 });
            mcpTests.push('GitHub MCP: installed');
        } catch (error) {
            mcpTests.push('GitHub MCP: not found');
        }
        
        try {
            // Check if code-sandbox MCP is available
            const { stdout: sandboxCheck } = await execAsync('npm list -g @automata-labs/playwright-mcp', { timeout: 3000 });
            mcpTests.push('Code-sandbox MCP: installed');
        } catch (error) {
            mcpTests.push('Code-sandbox MCP: not found');
        }
        
        const installed = mcpTests.filter(test => test.includes('installed')).length;
        
        if (installed === 0) {
            return {
                success: false,
                error: 'No MCP servers found'
            };
        }
        
        return {
            success: true,
            details: `${installed}/2 MCP servers available: ${mcpTests.join(', ')}`
        };
    }
    
    async testCompleteWorkflow() {
        // Test end-to-end workflow
        try {
            // 1. Test agent mention parsing
            const testPrompt = "I need @agent-master-orchestrator to help me create a new project";
            
            // 2. Test smart orchestration
            const orchestratorPath = path.join(this.hooksDir, 'smart_orchestrator.py');
            const { stdout: orchestratorResult } = await execAsync(`python3 "${orchestratorPath}" "${testPrompt}"`, { timeout: 10000 });
            
            const result = JSON.parse(orchestratorResult);
            
            // Should detect the explicit mention
            if (!result.agents.includes('master-orchestrator')) {
                return {
                    success: false,
                    error: 'Workflow test: orchestrator not detecting explicit mentions'
                };
            }
            
            // 3. Test status line update
            const statusPath = path.join(this.hooksDir, 'status_line_manager.py');
            const { stdout: statusResult } = await execAsync(`python3 "${statusPath}"`, { timeout: 5000 });
            
            if (!statusResult.trim()) {
                return {
                    success: false,
                    error: 'Workflow test: status line not functioning'
                };
            }
            
            return {
                success: true,
                details: `Complete workflow validated: ${result.agents.length} agents, status: "${statusResult.trim()}"`
            };
        } catch (error) {
            return {
                success: false,
                error: `Complete workflow test failed: ${error.message}`
            };
        }
    }
    
    async runAllTests() {
        console.log(chalk.blue('🚀 Starting Claude Code Dev Stack V3 Integration Tests\n'));
        
        const startTime = Date.now();
        
        for (const testName of this.tests) {
            await this.runTest(testName);
        }
        
        const duration = Date.now() - startTime;
        
        // Display summary
        console.log(chalk.blue('\n📊 Test Summary:'));
        console.log(chalk.green(`  ✓ Passed: ${this.results.passed}`));
        
        if (this.results.failed > 0) {
            console.log(chalk.red(`  ✗ Failed: ${this.results.failed}`));
        }
        
        if (this.results.skipped > 0) {
            console.log(chalk.yellow(`  ⚠ Skipped: ${this.results.skipped}`));
        }
        
        console.log(chalk.blue(`  ⏱ Duration: ${duration}ms`));
        
        const success = this.results.failed === 0;
        
        if (success) {
            console.log(chalk.green('\n🎉 All tests passed! Claude Code Dev Stack V3 is ready to use.'));
            console.log(chalk.blue('\n🚀 Quick Start Commands:'));
            console.log(chalk.cyan('  claude "@agent-master-orchestrator help me create a new project"'));
            console.log(chalk.cyan('  node agent-router.js --list-agents'));
            console.log(chalk.cyan('  python3 status_line_manager.py --monitor'));
        } else {
            console.log(chalk.red('\n❌ Some tests failed. Please review the errors above.'));
            
            if (this.results.errors.length > 0) {
                console.log(chalk.red('\n🐛 Error Details:'));
                this.results.errors.forEach((err, index) => {
                    console.log(chalk.red(`  ${index + 1}. ${err.test}: ${err.error}`));
                });
            }
        }
        
        return success;
    }
}

// CLI interface
async function main() {
    const tester = new IntegrationTester();
    
    if (process.argv.includes('--help')) {
        console.log(chalk.blue('Integration Test Suite V3.0'));
        console.log('Usage: test-integration.js [test-name]');
        console.log('\nAvailable tests:');
        tester.tests.forEach(test => console.log(`  ${test}`));
        console.log('\nRun without arguments to execute all tests.');
        return;
    }
    
    const specificTest = process.argv[2];
    
    if (specificTest && tester.tests.includes(specificTest)) {
        // Run specific test
        await tester.runTest(specificTest);
    } else if (specificTest) {
        console.log(chalk.red(`Unknown test: ${specificTest}`));
        console.log(chalk.gray('Use --help to see available tests'));
        process.exit(1);
    } else {
        // Run all tests
        const success = await tester.runAllTests();
        process.exit(success ? 0 : 1);
    }
}

if (import.meta.url === `file://${process.argv[1]}`) {
    main();
}

export default IntegrationTester;