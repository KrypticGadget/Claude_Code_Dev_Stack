#!/usr/bin/env node
/**
 * Complete Integration Script - V3.0 Final Setup
 * Integrates all V3 components and validates complete installation
 */

import fs from 'fs-extra';
import path from 'path';
import os from 'os';
import { exec } from 'child_process';
import { promisify } from 'util';
import chalk from 'chalk';

const execAsync = promisify(exec);

class CompleteIntegrator {
    constructor() {
        this.projectRoot = path.resolve(__dirname, '..');
        this.claudeDir = path.join(os.homedir(), '.claude');
        this.binDir = path.join(this.projectRoot, 'bin');
        this.hooksDir = path.join(this.projectRoot, 'core', 'hooks', 'hooks');
        
        this.installSteps = [
            'validateEnvironment',
            'setupDirectories',
            'fixPermissions', 
            'registerHooks',
            'validateIntegration',
            'testSystem',
            'displaySummary'
        ];
        
        this.results = {
            completed: [],
            failed: [],
            warnings: []
        };
    }
    
    log(message, type = 'info') {
        const prefix = {
            info: chalk.blue('ℹ'),
            success: chalk.green('✓'),
            warning: chalk.yellow('⚠'),
            error: chalk.red('✗')
        }[type] || chalk.blue('ℹ');
        
        console.log(`${prefix} ${message}`);
    }
    
    async validateEnvironment() {
        this.log('Validating environment...', 'info');
        
        // Check Node.js version
        const nodeVersion = process.version;
        const majorVersion = parseInt(nodeVersion.split('.')[0].substring(1));
        
        if (majorVersion < 18) {
            throw new Error(`Node.js 18+ required, found ${nodeVersion}`);
        }
        
        // Check Python availability
        try {
            await execAsync('python3 --version');
        } catch (error) {
            this.results.warnings.push('Python3 not found - some hooks may not work');
        }
        
        // Check Git availability
        try {
            await execAsync('git --version');
        } catch (error) {
            this.results.warnings.push('Git not found - version control features disabled');
        }
        
        this.log('Environment validation complete', 'success');
        return { success: true };
    }
    
    async setupDirectories() {
        this.log('Setting up directories...', 'info');
        
        const directories = [
            this.claudeDir,
            path.join(this.claudeDir, 'state'),
            path.join(this.claudeDir, 'agents'),
            path.join(this.claudeDir, 'hooks'),
            path.join(this.claudeDir, 'audio'),
            path.join(this.claudeDir, 'logs')
        ];
        
        for (const dir of directories) {
            await fs.ensureDir(dir);
            this.log(`Created directory: ${path.relative(os.homedir(), dir)}`, 'info');
        }
        
        this.log('Directory setup complete', 'success');
        return { success: true };
    }
    
    async fixPermissions() {
        this.log('Fixing script permissions...', 'info');
        
        if (process.platform === 'win32') {
            this.log('Windows detected - skipping Unix permissions', 'info');
            return { success: true };
        }
        
        const scripts = [
            path.join(this.hooksDir, 'smart_orchestrator.py'),
            path.join(this.hooksDir, 'status_line_manager.py'), 
            path.join(this.hooksDir, 'agent_mention_parser.py'),
            path.join(this.binDir, 'agent-router.js'),
            path.join(this.binDir, 'hook-integrator.js'),
            path.join(this.binDir, 'test-integration.js')
        ];
        
        let fixed = 0;
        
        for (const script of scripts) {
            if (fs.existsSync(script)) {
                try {
                    await fs.chmod(script, '755');
                    fixed++;
                } catch (error) {
                    this.results.warnings.push(`Could not fix permissions for ${script}: ${error.message}`);
                }
            }
        }
        
        this.log(`Fixed permissions for ${fixed} scripts`, 'success');
        return { success: true };
    }
    
    async registerHooks() {
        this.log('Registering hooks with Claude Code...', 'info');
        
        try {
            const integratorPath = path.join(this.binDir, 'hook-integrator.js');
            const { stdout } = await execAsync(`node "${integratorPath}" integrate`);
            
            // Parse output to determine success
            if (stdout.includes('Integration Summary:')) {
                this.log('Hooks registered successfully', 'success');
                return { success: true, details: stdout };
            } else {
                throw new Error('Hook integration returned unexpected output');
            }
        } catch (error) {
            this.results.warnings.push(`Hook registration partially failed: ${error.message}`);
            return { success: false, error: error.message };
        }
    }
    
    async validateIntegration() {
        this.log('Validating integration...', 'info');
        
        try {
            const integratorPath = path.join(this.binDir, 'hook-integrator.js');
            const { stdout } = await execAsync(`node "${integratorPath}" validate`);
            
            if (stdout.includes('All hooks validated successfully')) {
                this.log('Integration validation passed', 'success');
                return { success: true };
            } else {
                this.results.warnings.push('Some validation issues found');
                return { success: false, details: stdout };
            }
        } catch (error) {
            this.results.warnings.push(`Validation failed: ${error.message}`);
            return { success: false, error: error.message };
        }
    }
    
    async testSystem() {
        this.log('Testing system functionality...', 'info');
        
        const tests = [
            this.testAgentRouter(),
            this.testSmartOrchestrator(),
            this.testStatusLine()
        ];
        
        const results = await Promise.allSettled(tests);
        
        let passed = 0;
        let failed = 0;
        
        results.forEach((result, index) => {
            if (result.status === 'fulfilled' && result.value.success) {
                passed++;
            } else {
                failed++;
                const testName = ['Agent Router', 'Smart Orchestrator', 'Status Line'][index];
                this.results.warnings.push(`${testName} test failed`);
            }
        });
        
        this.log(`System tests: ${passed} passed, ${failed} failed`, passed === results.length ? 'success' : 'warning');
        return { success: passed > 0 };
    }
    
    async testAgentRouter() {
        try {
            const routerPath = path.join(this.binDir, 'agent-router.js');
            const { stdout } = await execAsync(`node "${routerPath}" --status`, { timeout: 5000 });
            return { success: true, output: stdout };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
    
    async testSmartOrchestrator() {
        try {
            const orchestratorPath = path.join(this.hooksDir, 'smart_orchestrator.py');
            const { stdout } = await execAsync(`python3 "${orchestratorPath}" "test prompt"`, { timeout: 10000 });
            const result = JSON.parse(stdout);
            return { success: !!result.agents };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
    
    async testStatusLine() {
        try {
            const statusPath = path.join(this.hooksDir, 'status_line_manager.py');
            const { stdout } = await execAsync(`python3 "${statusPath}"`, { timeout: 5000 });
            return { success: stdout.trim().length > 0 };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
    
    async displaySummary() {
        console.log(chalk.blue('\n' + '='.repeat(60)));
        console.log(chalk.blue('🎉 CLAUDE CODE DEV STACK V3 INTEGRATION COMPLETE'));
        console.log(chalk.blue('='.repeat(60)));
        
        // Display what was completed
        if (this.results.completed.length > 0) {
            console.log(chalk.green('\n✅ Completed Steps:'));
            this.results.completed.forEach(step => {
                console.log(chalk.green(`  ✓ ${step}`));
            });
        }
        
        // Display warnings
        if (this.results.warnings.length > 0) {
            console.log(chalk.yellow('\n⚠️  Warnings:'));
            this.results.warnings.forEach(warning => {
                console.log(chalk.yellow(`  • ${warning}`));
            });
        }
        
        // Display failed steps
        if (this.results.failed.length > 0) {
            console.log(chalk.red('\n❌ Failed Steps:'));
            this.results.failed.forEach(step => {
                console.log(chalk.red(`  ✗ ${step}`));
            });
        }
        
        // Display available commands
        console.log(chalk.blue('\n🚀 Available Commands:'));
        console.log(chalk.cyan('  claude-code-router --list-agents      ') + chalk.gray('- List all available agents'));
        console.log(chalk.cyan('  claude-code-integrate list            ') + chalk.gray('- Show registered hooks'));
        console.log(chalk.cyan('  claude-code-test                      ') + chalk.gray('- Run integration tests'));
        console.log(chalk.cyan('  python3 status_line_manager.py --monitor') + chalk.gray('- Monitor status line'));
        
        // Display example usage
        console.log(chalk.blue('\n💡 Example Usage:'));
        console.log(chalk.green('  claude "@agent-master-orchestrator create a new project"'));
        console.log(chalk.green('  claude "@agent-business-analyst[opus] analyze market opportunity"'));
        console.log(chalk.green('  claude "@agent-technical-cto review this architecture"'));
        
        console.log(chalk.blue('\n' + '='.repeat(60)));
        
        return { success: true };
    }
    
    async runIntegration() {
        const startTime = Date.now();
        
        console.log(chalk.blue('🚀 Starting Claude Code Dev Stack V3 Complete Integration\n'));
        
        for (const step of this.installSteps) {
            try {
                const result = await this[step]();
                if (result.success) {
                    this.results.completed.push(step);
                } else {
                    this.results.failed.push(step);
                }
            } catch (error) {
                this.log(`Step ${step} failed: ${error.message}`, 'error');
                this.results.failed.push(step);
            }
        }
        
        const duration = Date.now() - startTime;
        const success = this.results.failed.length === 0;
        
        console.log(chalk.blue(`\n⏱ Integration completed in ${duration}ms`));
        
        if (success) {
            this.log('🎉 Complete integration successful!', 'success');
        } else {
            this.log('⚠ Integration completed with some issues', 'warning');
        }
        
        return success;
    }
}

// CLI interface
async function main() {
    const integrator = new CompleteIntegrator();
    
    if (process.argv.includes('--help')) {
        console.log(chalk.blue('Complete Integration Script V3.0'));
        console.log('Performs final setup and validation of Claude Code Dev Stack V3');
        console.log('\nThis script will:');
        console.log('• Validate environment requirements');
        console.log('• Setup directory structure');
        console.log('• Fix script permissions');
        console.log('• Register hooks with Claude Code');
        console.log('• Validate complete integration');
        console.log('• Test system functionality');
        return;
    }
    
    try {
        const success = await integrator.runIntegration();
        process.exit(success ? 0 : 1);
    } catch (error) {
        console.error(chalk.red('Integration failed:'), error);
        process.exit(1);
    }
}

if (import.meta.url === `file://${process.argv[1]}`) {
    main();
}

export default CompleteIntegrator;