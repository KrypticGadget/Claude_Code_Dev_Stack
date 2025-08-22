#!/usr/bin/env node

/**
 * Simple Hook Registry Path Updater for V3.6.9 Categorized Structure
 * Uses built-in Node.js modules only
 */

const fs = require('fs');
const path = require('path');

class SimpleHookPathUpdater {
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
        console.log('🔧 Hook Registry Path Updater V3.6.9');
        console.log('==================================================');

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
            console.error('❌ Update failed:', error.message);
            process.exit(1);
        }
    }

    async createBackup() {
        console.log('📦 Creating backup...');
        try {
            const data = await fs.promises.readFile(this.registryPath);
            await fs.promises.writeFile(this.backupPath, data);
            console.log(`✅ Backup created: ${this.backupPath}`);
        } catch (error) {
            throw new Error(`Failed to create backup: ${error.message}`);
        }
    }

    async loadRegistry() {
        console.log('📖 Loading hook registry...');
        try {
            const data = await fs.promises.readFile(this.registryPath, 'utf8');
            const registry = JSON.parse(data);
            console.log(`✅ Loaded ${Object.keys(registry.hooks).length} hooks`);
            return registry;
        } catch (error) {
            throw new Error(`Failed to load registry: ${error.message}`);
        }
    }

    async updatePaths(registry) {
        console.log('🔄 Updating hook paths...');
        
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
            
            console.log(`  ${hookName}: ${oldSource} → ${newDir}/${oldSource}`);
            this.results.updated++;
        }
        
        // Update version to reflect changes
        updatedRegistry.version = "3.6.9";
        updatedRegistry.last_updated = new Date().toISOString().split('T')[0];
        
        return updatedRegistry;
    }

    async verifyPaths(registry) {
        console.log('🔍 Verifying updated paths...');
        
        for (const [hookName, hookData] of Object.entries(registry.hooks)) {
            const fullPath = `src/core/hooks/${hookData.source}`;
            
            try {
                await fs.promises.access(fullPath);
                console.log(`✅ ${hookName}: ${fullPath}`);
                this.results.verified++;
            } catch (error) {
                console.log(`❌ ${hookName}: ${fullPath} (MISSING)`);
                this.results.errors++;
                this.results.warnings.push(`File not found: ${fullPath}`);
            }
        }
    }

    async saveRegistry(registry) {
        console.log('💾 Saving updated registry...');
        try {
            const data = JSON.stringify(registry, null, 2);
            await fs.promises.writeFile(this.registryPath, data);
            console.log('✅ Registry saved with updated paths');
        } catch (error) {
            throw new Error(`Failed to save registry: ${error.message}`);
        }
    }

    printResults() {
        console.log('\n📊 UPDATE RESULTS');
        console.log('========================================');
        
        console.log(`Hooks Updated: ${this.results.updated}`);
        console.log(`Paths Verified: ${this.results.verified}`);
        console.log(`Errors: ${this.results.errors}`);
        console.log(`Warnings: ${this.results.warnings.length}`);
        
        if (this.results.warnings.length > 0) {
            console.log('\n⚠️  WARNINGS:');
            this.results.warnings.forEach(warning => {
                console.log(`  • ${warning}`);
            });
        }
        
        if (this.results.errors === 0) {
            console.log('\n🎉 All paths updated and verified successfully!');
        } else {
            console.log(`\n❌ ${this.results.errors} paths could not be verified`);
        }
        
        console.log('\n🔄 Hook registry updated for V3.6.9 categorized structure');
    }
}

// Run updater
const updater = new SimpleHookPathUpdater();
updater.run().catch(console.error);