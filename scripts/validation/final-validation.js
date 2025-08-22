#!/usr/bin/env node
/**
 * Final Validation Script - V3.0 Complete System Check
 * Validates the complete Claude Code Dev Stack V3 installation
 */

import fs from 'fs-extra';
import path from 'path';
import os from 'os';
import { exec } from 'child_process';
import { promisify } from 'util';
import chalk from 'chalk';

const execAsync = promisify(exec);

class FinalValidator {
    constructor() {
        this.claudeDir = path.join(os.homedir(), '.claude');
        this.projectRoot = path.resolve(__dirname, '..');
        
        this.validationChecks = [
            {
                name: 'Directory Structure',
                check: 'validateDirectoryStructure',
                critical: true
            },
            {
                name: 'Claude Configuration',
                check: 'validateClaudeConfig',
                critical: true
            },
            {
                name: 'Hook Registration',
                check: 'validateHookRegistration', 
                critical: true
            },
            {
                name: 'Script Permissions',
                check: 'validateScriptPermissions',
                critical: false
            },
            {
                name: 'Agent Router',
                check: 'validateAgentRouter',
                critical: true
            },
            {
                name: 'Smart Orchestrator',
                check: 'validateSmartOrchestrator',
                critical: true
            },
            {
                name: 'Status Line Manager',
                check: 'validateStatusLineManager',
                critical: false
            },
            {
                name: 'MCP Integration',
                check: 'validateMCPIntegration',
                critical: false
            },
            {
                name: 'End-to-End Workflow',
                check: 'validateWorkflow',
                critical: true
            }
        ];
        
        this.results = {
            total: 0,
            passed: 0,
            failed: 0,
            warnings: 0,
            critical_failures: 0,
            details: []
        };
    }
    
    async runValidation() {
        console.log(chalk.blue('🔍 Claude Code Dev Stack V3 - Final Validation\n'));
        
        this.results.total = this.validationChecks.length;
        
        for (const check of this.validationChecks) {
            const result = await this.runCheck(check);
            this.results.details.push(result);
            
            if (result.status === 'pass') {
                this.results.passed++;
                console.log(chalk.green(`✓ ${check.name}: ${result.message}`));
            } else if (result.status === 'warn') {
                this.results.warnings++;
                console.log(chalk.yellow(`⚠ ${check.name}: ${result.message}`));
            } else {
                this.results.failed++;
                if (check.critical) {
                    this.results.critical_failures++;
                }
                console.log(chalk.red(`✗ ${check.name}: ${result.message}`));
            }
            
            if (result.details) {
                console.log(chalk.gray(`  ${result.details}`));
            }
        }
        
        await this.displaySummary();
        return this.results.critical_failures === 0;
    }
    
    async runCheck(checkConfig) {
        try {
            return await this[checkConfig.check]();
        } catch (error) {
            return {
                status: 'fail',
                message: `Check threw exception: ${error.message}`,
                error: error
            };
        }
    }
    
    async validateDirectoryStructure() {
        const requiredPaths = [
            path.join(this.claudeDir),
            path.join(this.claudeDir, 'state'),
            path.join(this.projectRoot, 'bin', 'agent-router.js'),
            path.join(this.projectRoot, 'bin', 'hook-integrator.js'),
            path.join(this.projectRoot, 'bin', 'test-integration.js'),
            path.join(this.projectRoot, 'core', 'hooks', 'hooks', 'smart_orchestrator.py'),
            path.join(this.projectRoot, 'core', 'hooks', 'hooks', 'status_line_manager.py'),
            path.join(this.projectRoot, 'core', 'hooks', 'hooks', 'agent_mention_parser.py')
        ];
        
        const missing = requiredPaths.filter(p => !fs.existsSync(p));
        
        if (missing.length === 0) {
            return {
                status: 'pass',
                message: `All ${requiredPaths.length} required paths exist`
            };
        } else {
            return {
                status: 'fail',
                message: `${missing.length} required paths missing`,
                details: missing.map(p => path.relative(this.projectRoot, p)).join(', ')
            };
        }
    }
    
    async validateClaudeConfig() {
        const configFile = path.join(this.claudeDir, 'claude.json');
        
        if (!fs.existsSync(configFile)) {
            return {
                status: 'fail',
                message: 'Claude configuration file not found'
            };
        }
        
        try {
            const config = await fs.readJson(configFile);
            
            if (!config.hooks || !Array.isArray(config.hooks)) {
                return {
                    status: 'fail',
                    message: 'No hooks array in configuration'
                };
            }
            
            if (config.hooks.length === 0) {
                return {
                    status: 'fail', 
                    message: 'No hooks registered in configuration'
                };
            }
            
            return {
                status: 'pass',
                message: `Configuration valid with ${config.hooks.length} hooks`
            };
        } catch (error) {
            return {
                status: 'fail',
                message: `Configuration parse error: ${error.message}`
            };
        }
    }
    
    async validateHookRegistration() {
        try {
            const integratorPath = path.join(this.projectRoot, 'bin', 'hook-integrator.js');
            const { stdout } = await execAsync(`node "${integratorPath}" validate`, { timeout: 10000 });
            
            if (stdout.includes('All hooks validated successfully')) {
                const hookCount = stdout.match(/(\d+) hooks?/)?.[1] || 'unknown';
                return {
                    status: 'pass',
                    message: `All hooks registered and validated (${hookCount} hooks)`
                };
            } else {
                return {
                    status: 'warn',
                    message: 'Hook validation returned warnings',
                    details: stdout.replace(/\n/g, ' ')
                };
            }
        } catch (error) {
            return {
                status: 'fail',
                message: `Hook validation failed: ${error.message}`
            };
        }
    }
    
    async validateScriptPermissions() {
        if (process.platform === 'win32') {
            return {
                status: 'pass',
                message: 'Windows platform - permissions not applicable'
            };
        }
        
        const scripts = [
            path.join(this.projectRoot, 'core', 'hooks', 'hooks', 'smart_orchestrator.py'),
            path.join(this.projectRoot, 'core', 'hooks', 'hooks', 'status_line_manager.py'),
            path.join(this.projectRoot, 'core', 'hooks', 'hooks', 'agent_mention_parser.py')
        ];
        
        const issues = [];
        
        for (const script of scripts) {
            if (!fs.existsSync(script)) continue;
            
            try {
                const stats = await fs.stat(script);
                const mode = stats.mode & parseInt('777', 8);
                if (mode < parseInt('644', 8)) {
                    issues.push(path.basename(script));
                }
            } catch (error) {
                issues.push(`${path.basename(script)} (check failed)`);
            }
        }
        
        if (issues.length === 0) {
            return {
                status: 'pass',
                message: 'All scripts have appropriate permissions'
            };
        } else {
            return {
                status: 'warn',
                message: `${issues.length} scripts may have permission issues`,
                details: issues.join(', ')
            };
        }
    }
    
    async validateAgentRouter() {
        try {
            const routerPath = path.join(this.projectRoot, 'bin', 'agent-router.js');
            const { stdout } = await execAsync(`node "${routerPath}" --list-agents`, { timeout: 5000 });
            
            if (stdout.includes('Available Agents:')) {
                const agentCount = (stdout.match(/@agent-/g) || []).length;
                return {
                    status: 'pass',
                    message: `Agent router working with ${agentCount} registered agents`
                };
            } else {
                return {
                    status: 'fail',
                    message: 'Agent router not returning expected output'
                };
            }
        } catch (error) {
            return {
                status: 'fail',
                message: `Agent router validation failed: ${error.message}`
            };
        }
    }
    
    async validateSmartOrchestrator() {
        try {
            const orchestratorPath = path.join(this.projectRoot, 'core', 'hooks', 'hooks', 'smart_orchestrator.py');
            const { stdout } = await execAsync(`python3 "${orchestratorPath}" "create a simple test application"`, { timeout: 10000 });
            
            const result = JSON.parse(stdout);
            
            if (result.agents && Array.isArray(result.agents) && result.agents.length > 0) {
                return {
                    status: 'pass',
                    message: `Smart orchestrator working - selected ${result.agents.length} agents`,
                    details: `Agents: ${result.agents.join(', ')}`
                };
            } else {
                return {
                    status: 'fail',
                    message: 'Smart orchestrator not selecting agents correctly'
                };
            }
        } catch (error) {
            if (error.message.includes('python3')) {
                return {
                    status: 'warn',
                    message: 'Python3 not available - orchestrator cannot be tested'
                };
            }
            return {
                status: 'fail',
                message: `Smart orchestrator validation failed: ${error.message}`
            };
        }
    }
    
    async validateStatusLineManager() {
        try {
            const statusPath = path.join(this.projectRoot, 'core', 'hooks', 'hooks', 'status_line_manager.py');
            const { stdout } = await execAsync(`python3 "${statusPath}"`, { timeout: 5000 });
            
            if (stdout.trim().length > 0) {
                // Check for expected status line format elements
                const hasExpectedFormat = stdout.includes('git:') && stdout.includes('|');
                
                if (hasExpectedFormat) {
                    return {
                        status: 'pass',
                        message: 'Status line manager working correctly',
                        details: stdout.trim()
                    };
                } else {
                    return {
                        status: 'warn',
                        message: 'Status line format may be incorrect',
                        details: stdout.trim()
                    };
                }
            } else {
                return {
                    status: 'fail',
                    message: 'Status line manager not producing output'
                };
            }
        } catch (error) {
            if (error.message.includes('python3')) {
                return {
                    status: 'warn',
                    message: 'Python3 not available - status line cannot be tested'
                };
            }
            return {
                status: 'warn',
                message: `Status line validation skipped: ${error.message}`
            };
        }
    }
    
    async validateMCPIntegration() {
        const mcpServers = [
            '@modelcontextprotocol/server-github',
            '@automata-labs/playwright-mcp'
        ];
        
        const results = [];
        
        for (const server of mcpServers) {
            try {
                await execAsync(`npm list -g ${server}`, { timeout: 3000 });
                results.push(`${server}: installed`);
            } catch (error) {
                results.push(`${server}: not found`);
            }
        }
        
        const installed = results.filter(r => r.includes('installed')).length;
        
        if (installed === mcpServers.length) {
            return {
                status: 'pass',
                message: 'All MCP servers installed and available'
            };
        } else if (installed > 0) {
            return {
                status: 'warn',
                message: `${installed}/${mcpServers.length} MCP servers available`,
                details: results.join(', ')
            };
        } else {
            return {
                status: 'warn',
                message: 'No MCP servers found - external integrations unavailable'
            };
        }
    }
    
    async validateWorkflow() {
        try {
            // Test @mention parsing
            const testInput = JSON.stringify({
                prompt: "Test @agent-master-orchestrator workflow"
            });
            
            const parserPath = path.join(this.projectRoot, 'core', 'hooks', 'hooks', 'agent_mention_parser.py');
            const { stdout: parserOutput } = await execAsync(`echo '${testInput}' | python3 "${parserPath}"`, { timeout: 5000 });
            
            if (!parserOutput.includes('master-orchestrator')) {
                return {
                    status: 'fail',
                    message: 'End-to-end workflow: agent mention parsing failed'
                };
            }
            
            // Test orchestration
            const orchestratorPath = path.join(this.projectRoot, 'core', 'hooks', 'hooks', 'smart_orchestrator.py');
            const { stdout: orchestratorOutput } = await execAsync(`python3 "${orchestratorPath}" "Test @agent-master-orchestrator workflow"`, { timeout: 10000 });
            
            const result = JSON.parse(orchestratorOutput);
            
            if (!result.agents || !result.agents.includes('master-orchestrator')) {
                return {
                    status: 'fail',
                    message: 'End-to-end workflow: orchestration not handling mentions'
                };
            }
            
            return {
                status: 'pass',
                message: 'End-to-end workflow functioning correctly',
                details: `Workflow: mention parsing → orchestration → agent selection`
            };
        } catch (error) {
            if (error.message.includes('python3')) {
                return {
                    status: 'warn',
                    message: 'Workflow test skipped - Python3 not available'
                };
            }
            return {
                status: 'fail',
                message: `End-to-end workflow validation failed: ${error.message}`
            };
        }
    }
    
    async displaySummary() {
        console.log(chalk.blue('\n' + '='.repeat(60)));
        console.log(chalk.blue('📊 VALIDATION SUMMARY'));
        console.log(chalk.blue('='.repeat(60)));
        
        // Overall status
        const overallStatus = this.results.critical_failures === 0 ? 'READY' : 'ISSUES DETECTED';
        const statusColor = this.results.critical_failures === 0 ? 'green' : 'red';
        
        console.log(chalk[statusColor](`\n🎯 System Status: ${overallStatus}`));
        
        // Statistics
        console.log(chalk.blue('\n📈 Validation Results:'));
        console.log(chalk.green(`  ✓ Passed: ${this.results.passed}/${this.results.total}`));
        
        if (this.results.warnings > 0) {
            console.log(chalk.yellow(`  ⚠ Warnings: ${this.results.warnings}`));
        }
        
        if (this.results.failed > 0) {
            console.log(chalk.red(`  ✗ Failed: ${this.results.failed}`));
            
            if (this.results.critical_failures > 0) {
                console.log(chalk.red(`  🚨 Critical Failures: ${this.results.critical_failures}`));
            }
        }
        
        // Recommendations
        if (this.results.critical_failures === 0) {
            console.log(chalk.green('\n🚀 System Ready for Use!'));
            console.log(chalk.blue('\n💡 Next Steps:'));
            console.log(chalk.cyan('  1. Test with: claude "@agent-master-orchestrator help"'));
            console.log(chalk.cyan('  2. List agents: claude-code-router --list-agents'));
            console.log(chalk.cyan('  3. Monitor status: python3 status_line_manager.py --monitor'));
        } else {
            console.log(chalk.red('\n⚠️ Critical Issues Detected'));
            console.log(chalk.yellow('\n🔧 Recommended Actions:'));
            
            const criticalFailures = this.results.details.filter(d => d.status === 'fail');
            criticalFailures.forEach(failure => {
                console.log(chalk.yellow(`  • Fix: ${failure.message}`));
            });
            
            console.log(chalk.blue('\n🔄 After fixing issues, re-run:'));
            console.log(chalk.cyan('  node scripts/final-validation.js'));
        }
        
        console.log(chalk.blue('\n' + '='.repeat(60)));
    }
}

// CLI interface
async function main() {
    if (process.argv.includes('--help')) {
        console.log(chalk.blue('Final Validation Script V3.0'));
        console.log('Performs comprehensive validation of Claude Code Dev Stack V3 installation');
        console.log('\nThis validates:');
        console.log('• Directory structure and file permissions');
        console.log('• Claude Code hook registration');
        console.log('• Agent routing and orchestration');
        console.log('• Status line and context management');
        console.log('• End-to-end workflow functionality');
        return;
    }
    
    const validator = new FinalValidator();
    
    try {
        const success = await validator.runValidation();
        process.exit(success ? 0 : 1);
    } catch (error) {
        console.error(chalk.red('Validation failed:'), error);
        process.exit(1);
    }
}

if (import.meta.url === `file://${process.argv[1]}`) {
    main();
}

export default FinalValidator;