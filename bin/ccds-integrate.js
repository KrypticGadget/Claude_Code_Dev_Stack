#!/usr/bin/env node
/**
 * Hook Integrator - V3.0 Claude Code Hook Registration
 * Registers all V3 hooks with Claude Code for seamless integration
 */

import fs from 'fs-extra';
import path from 'path';
import os from 'os';
import chalk from 'chalk';

class HookIntegrator {
    constructor() {
        this.claudeDir = path.join(os.homedir(), '.claude');
        this.configFile = path.join(this.claudeDir, 'claude.json');
        this.hooksDir = path.join(__dirname, '..', 'core', 'hooks', 'hooks');
        
        // Hook definitions
        this.hooks = [
            {
                name: 'agent-mention-parser',
                script: 'agent_mention_parser.py',
                events: ['UserPromptSubmit'],
                description: 'Parse @agent- mentions for routing',
                enabled: true
            },
            {
                name: 'smart-orchestrator',
                script: 'smart_orchestrator.py',
                events: ['UserPromptSubmit'],
                description: 'Intelligent agent selection and orchestration',
                enabled: true
            },
            {
                name: 'status-line-manager',
                script: 'status_line_manager.py',
                events: ['SessionStart', 'UserPromptSubmit', 'AssistantMessage'],
                description: 'Real-time context and status tracking',
                enabled: true
            },
            {
                name: 'agent-enhancer',
                script: 'agent_enhancer_v3.py',
                events: ['UserPromptSubmit'],
                description: 'Prompt enhancement and optimization',
                enabled: true
            },
            {
                name: 'orchestration-enhancer',
                script: 'orchestration_enhancer.py',
                events: ['UserPromptSubmit'],
                description: 'Multi-agent workflow coordination',
                enabled: true
            }
        ];
    }
    
    async loadClaudeConfig() {
        try {
            if (fs.existsSync(this.configFile)) {
                return await fs.readJson(this.configFile);
            }
        } catch (error) {
            console.warn(chalk.yellow('Warning: Could not load Claude config, creating new one'));
        }
        
        // Default minimal config
        return {
            hooks: []
        };
    }
    
    async saveClaudeConfig(config) {
        await fs.ensureDir(this.claudeDir);
        await fs.writeJson(this.configFile, config, { spaces: 2 });
    }
    
    prepareHookCommand(hook) {
        const scriptPath = path.join(this.hooksDir, hook.script);
        
        // Ensure script exists and is executable
        if (!fs.existsSync(scriptPath)) {
            console.warn(chalk.yellow(`Warning: Hook script not found: ${scriptPath}`));
            return null;
        }
        
        // Make script executable on Unix systems
        if (process.platform !== 'win32') {
            try {
                fs.chmodSync(scriptPath, '755');
            } catch (error) {
                console.warn(chalk.yellow(`Warning: Could not make script executable: ${scriptPath}`));
            }
        }
        
        // Determine command based on script type
        let command;
        if (hook.script.endsWith('.py')) {
            command = `python3 "${scriptPath}"`;
        } else if (hook.script.endsWith('.js')) {
            command = `node "${scriptPath}"`;
        } else {
            command = `"${scriptPath}"`;
        }
        
        return {
            name: hook.name,
            description: hook.description,
            command: command,
            events: hook.events,
            enabled: hook.enabled,
            timeout: 5000,  // 5 second timeout
            priority: this.getHookPriority(hook.name)
        };
    }
    
    getHookPriority(hookName) {
        const priorities = {
            'agent-mention-parser': 1,
            'smart-orchestrator': 2,
            'agent-enhancer': 3,
            'orchestration-enhancer': 4,
            'status-line-manager': 5
        };
        
        return priorities[hookName] || 10;
    }
    
    async integrateHooks() {
        console.log(chalk.blue('🔌 Integrating Claude Code Dev Stack V3 hooks...'));
        
        const config = await this.loadClaudeConfig();
        
        // Initialize hooks array if it doesn't exist
        if (!config.hooks) {
            config.hooks = [];
        }
        
        let added = 0;
        let updated = 0;
        let skipped = 0;
        
        for (const hook of this.hooks) {
            const hookCommand = this.prepareHookCommand(hook);
            
            if (!hookCommand) {
                skipped++;
                continue;
            }
            
            // Check if hook already exists
            const existingIndex = config.hooks.findIndex(h => h.name === hook.name);
            
            if (existingIndex >= 0) {
                // Update existing hook
                config.hooks[existingIndex] = hookCommand;
                updated++;
                console.log(chalk.green(`  ✓ Updated hook: ${hook.name}`));
            } else {
                // Add new hook
                config.hooks.push(hookCommand);
                added++;
                console.log(chalk.green(`  + Added hook: ${hook.name}`));
            }
        }
        
        // Sort hooks by priority
        config.hooks.sort((a, b) => (a.priority || 10) - (b.priority || 10));
        
        // Save updated config
        await this.saveClaudeConfig(config);
        
        // Display summary
        console.log(chalk.blue('\n📊 Integration Summary:'));
        console.log(chalk.green(`  ✓ Added: ${added} hooks`));
        console.log(chalk.cyan(`  ⟳ Updated: ${updated} hooks`));
        if (skipped > 0) {
            console.log(chalk.yellow(`  ⚠ Skipped: ${skipped} hooks`));
        }
        
        console.log(chalk.blue(`\n🔗 Total hooks registered: ${config.hooks.length}`));
        
        return {
            success: true,
            added,
            updated,
            skipped,
            total: config.hooks.length
        };
    }
    
    async validateIntegration() {
        console.log(chalk.blue('🔍 Validating hook integration...'));
        
        const config = await this.loadClaudeConfig();
        const issues = [];
        
        if (!config.hooks || config.hooks.length === 0) {
            issues.push('No hooks found in configuration');
            return { valid: false, issues };
        }
        
        for (const hook of config.hooks) {
            // Check if script exists
            const scriptPath = hook.command.match(/"([^"]+)"/)?.[1];
            if (scriptPath && !fs.existsSync(scriptPath)) {
                issues.push(`Script not found: ${scriptPath} (${hook.name})`);
            }
            
            // Check required fields
            if (!hook.events || hook.events.length === 0) {
                issues.push(`No events defined for hook: ${hook.name}`);
            }
        }
        
        if (issues.length === 0) {
            console.log(chalk.green('✓ All hooks validated successfully'));
            return { valid: true, issues: [] };
        } else {
            console.log(chalk.red(`✗ Found ${issues.length} issue(s):`));
            issues.forEach(issue => console.log(chalk.yellow(`  • ${issue}`)));
            return { valid: false, issues };
        }
    }
    
    async listIntegratedHooks() {
        const config = await this.loadClaudeConfig();
        
        console.log(chalk.blue('🎯 Integrated Claude Code Hooks:'));
        
        if (!config.hooks || config.hooks.length === 0) {
            console.log(chalk.yellow('  No hooks registered'));
            return;
        }
        
        config.hooks.forEach((hook, index) => {
            const status = hook.enabled ? chalk.green('✓') : chalk.red('✗');
            const events = hook.events ? hook.events.join(', ') : 'none';
            console.log(`  ${status} ${chalk.cyan(hook.name)} - ${hook.description || 'No description'}`);
            console.log(`    Events: ${chalk.gray(events)}`);
            console.log(`    Priority: ${chalk.gray(hook.priority || 10)}`);
        });
    }
    
    async removeHook(hookName) {
        const config = await this.loadClaudeConfig();
        
        if (!config.hooks) {
            console.log(chalk.yellow('No hooks to remove'));
            return false;
        }
        
        const initialCount = config.hooks.length;
        config.hooks = config.hooks.filter(h => h.name !== hookName);
        
        if (config.hooks.length < initialCount) {
            await this.saveClaudeConfig(config);
            console.log(chalk.green(`✓ Removed hook: ${hookName}`));
            return true;
        } else {
            console.log(chalk.yellow(`Hook not found: ${hookName}`));
            return false;
        }
    }
}

// CLI interface
async function main() {
    const integrator = new HookIntegrator();
    const command = process.argv[2] || 'integrate';
    
    try {
        switch (command) {
            case 'integrate':
                await integrator.integrateHooks();
                break;
                
            case 'validate':
                await integrator.validateIntegration();
                break;
                
            case 'list':
                await integrator.listIntegratedHooks();
                break;
                
            case 'remove':
                if (process.argv[3]) {
                    await integrator.removeHook(process.argv[3]);
                } else {
                    console.log(chalk.red('Usage: hook-integrator.js remove <hook-name>'));
                }
                break;
                
            case 'help':
            case '--help':
                console.log(chalk.blue('Hook Integrator V3.0 - Commands:'));
                console.log('  integrate  - Register all V3 hooks with Claude Code');
                console.log('  validate   - Validate hook integration');
                console.log('  list       - List all integrated hooks');
                console.log('  remove     - Remove a specific hook');
                console.log('  help       - Show this help message');
                break;
                
            default:
                console.log(chalk.red(`Unknown command: ${command}`));
                console.log(chalk.gray('Use "help" for available commands'));
                process.exit(1);
        }
    } catch (error) {
        console.error(chalk.red('Integration failed:'), error);
        process.exit(1);
    }
}

if (import.meta.url === `file://${process.argv[1]}`) {
    main();
}

export default HookIntegrator;