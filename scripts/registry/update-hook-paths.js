#!/usr/bin/env node

/**
 * Update Hook Registry Paths for V3.6.9 Categorized Structure
 * Maps flat paths to new categorized directory structure
 */

import fs from 'fs-extra';
import path from 'path';
import chalk from 'chalk';

class HookPathUpdater {
    constructor() {
        this.registryPath = 'src/core/hooks/hook-registry.json';
        this.backupPath = 'src/core/hooks/hook-registry.json.backup';
        
        // Group to directory mapping
        this.groupMapping = {
            'orchestration': 'orchestration',
            'routing': 'agent',
            'feedback': 'audio',
            'ui': 'system',
            'automation': 'quality', 
            'quality': 'quality',
            'monitoring': 'monitoring',
            'state': 'session',
            'config': 'config',
            'workflow': 'orchestration',
            'execution': 'system',
            'special': 'system',
            'migration': 'system'
        };

        this.results = {
            updated: 0,
            verified: 0,
            errors: 0,
            warnings: []
        };
    }

    async run() {
        console.log(chalk.blue('🔧 Hook Registry Path Updater V3.6.9'));
        console.log(chalk.gray('=' * 50));

        try {
            // Backup original
            await this.createBackup();
            
            // Load registry
            const registry = await this.loadRegistry();
            
            // Update paths
            const updatedRegistry = await this.updatePaths(registry);
            
            // Verify paths exist
            await this.verifyPaths(updatedRegistry);
            
            // Save updated registry
            await this.saveRegistry(updatedRegistry);
            
            this.printResults();
            
        } catch (error) {
            console.error(chalk.red('❌ Update failed:'), error.message);
            process.exit(1);
        }
    }

    async createBackup() {
        console.log(chalk.yellow('📦 Creating backup...'));
        try {
            await fs.copy(this.registryPath, this.backupPath);
            console.log(chalk.green(`✅ Backup created: ${this.backupPath}`));
        } catch (error) {
            throw new Error(`Failed to create backup: ${error.message}`);
        }
    }

    async loadRegistry() {
        console.log(chalk.yellow('📖 Loading hook registry...'));
        try {
            const registry = await fs.readJson(this.registryPath);
            console.log(chalk.green(`✅ Loaded ${Object.keys(registry.hooks).length} hooks`));
            return registry;
        } catch (error) {
            throw new Error(`Failed to load registry: ${error.message}`);
        }
    }

    async updatePaths(registry) {
        console.log(chalk.yellow('🔄 Updating hook paths...'));
        
        const updatedRegistry = { ...registry };
        
        for (const [hookName, hookData] of Object.entries(registry.hooks)) {
            const oldSource = hookData.source;
            const group = hookData.group;
            
            // Determine new directory
            const newDir = this.groupMapping[group];
            if (!newDir) {
                this.results.warnings.push(`Unknown group '${group}' for hook '${hookName}'`);
                continue;
            }
            
            // Update source path
            updatedRegistry.hooks[hookName].source = `${newDir}/${oldSource}`;
            
            console.log(chalk.blue(`  ${hookName}: ${oldSource} → ${newDir}/${oldSource}`));
            this.results.updated++;
        }
        
        // Update version to reflect changes
        updatedRegistry.version = "3.6.9";
        updatedRegistry.last_updated = new Date().toISOString().split('T')[0];
        
        return updatedRegistry;
    }

    async verifyPaths(registry) {
        console.log(chalk.yellow('🔍 Verifying updated paths...'));
        
        for (const [hookName, hookData] of Object.entries(registry.hooks)) {
            const fullPath = `src/core/hooks/${hookData.source}`;
            
            try {
                await fs.access(fullPath);
                console.log(chalk.green(`✅ ${hookName}: ${fullPath}`));
                this.results.verified++;
            } catch (error) {
                console.log(chalk.red(`❌ ${hookName}: ${fullPath} (MISSING)`));
                this.results.errors++;
                this.results.warnings.push(`File not found: ${fullPath}`);
            }
        }
    }

    async saveRegistry(registry) {
        console.log(chalk.yellow('💾 Saving updated registry...'));
        try {
            await fs.writeJson(this.registryPath, registry, { spaces: 2 });
            console.log(chalk.green(`✅ Registry saved with updated paths`));
        } catch (error) {
            throw new Error(`Failed to save registry: ${error.message}`);
        }
    }

    printResults() {
        console.log(chalk.blue('\n📊 UPDATE RESULTS'));
        console.log(chalk.gray('=' * 40));
        
        console.log(`Hooks Updated: ${chalk.cyan(this.results.updated)}`);
        console.log(`Paths Verified: ${chalk.green(this.results.verified)}`);
        console.log(`Errors: ${chalk.red(this.results.errors)}`);
        console.log(`Warnings: ${chalk.yellow(this.results.warnings.length)}`);
        
        if (this.results.warnings.length > 0) {
            console.log(chalk.yellow('\n⚠️  WARNINGS:'));
            this.results.warnings.forEach(warning => {
                console.log(chalk.yellow(`  • ${warning}`));
            });
        }
        
        if (this.results.errors === 0) {
            console.log(chalk.green('\n🎉 All paths updated and verified successfully!'));
        } else {
            console.log(chalk.red(`\n❌ ${this.results.errors} paths could not be verified`));
        }
        
        console.log(chalk.blue('\n🔄 Hook registry updated for V3.6.9 categorized structure'));
    }
}

// Run updater
const updater = new HookPathUpdater();
updater.run().catch(console.error);