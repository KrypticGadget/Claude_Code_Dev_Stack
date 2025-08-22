#!/usr/bin/env node

/**
 * Claude Code Dev Stack v3.0 Repository Reorganizer
 * 
 * Prepares the repository for clean V3 structure by:
 * 1. Moving files from nested Claude_Code_Dev_Stack_v3 to root
 * 2. Avoiding conflicts with existing files
 * 3. Creating backup copies of important files
 * 4. Generating detailed reorganization plan
 */

const fs = require('fs').promises;
const path = require('path');
const { existsSync } = require('fs');

class RepoReorganizer {
    constructor(options = {}) {
        this.dryRun = options.dryRun || false;
        this.verbose = options.verbose || false;
        this.basePath = options.basePath || process.cwd();
        this.sourceDir = path.join(this.basePath, 'Claude_Code_Dev_Stack_v3');
        
        this.manifest = {
            operations: [],
            conflicts: [],
            timestamp: new Date().toISOString(),
            version: '1.0.0',
            dryRun: this.dryRun
        };

        // Files to merge/update rather than replace
        this.mergeableFiles = [
            'README.md',
            'requirements.txt',
            'package.json',
            '.gitignore',
            'setup.sh',
            'setup.bat'
        ];

        // Directories to handle specially
        this.specialDirectories = {
            'apps': 'Move to root level',
            'core': 'Move to root level', 
            'integrations': 'Move to root level',
            'server': 'Move to root level',
            'scripts': 'Merge with existing scripts directory',
            'venv': 'Skip - virtual environment',
            'clones': 'Skip - temporary directory'
        };

        this.skipPatterns = [
            /node_modules/,
            /\.git/,
            /venv/,
            /\.venv/,
            /__pycache__/,
            /\.DS_Store/,
            /Thumbs\.db/,
            /\.pyc$/,
            /clones/
        ];
    }

    async log(message, level = 'info') {
        const timestamp = new Date().toISOString();
        const prefix = this.dryRun ? '[DRY-RUN]' : '[LIVE]';
        const levelPrefix = level.toUpperCase();
        
        if (this.verbose || level === 'error' || level === 'warn') {
            console.log(`${timestamp} ${prefix} [${levelPrefix}] ${message}`);
        }
        
        this.manifest.operations.push({
            timestamp,
            level,
            message,
            dryRun: this.dryRun
        });
    }

    async validateEnvironment() {
        this.log('Validating environment...');
        
        if (!existsSync(this.sourceDir)) {
            throw new Error(`Source directory not found: ${this.sourceDir}`);
        }

        const sourceStat = await fs.stat(this.sourceDir);
        if (!sourceStat.isDirectory()) {
            throw new Error(`Source is not a directory: ${this.sourceDir}`);
        }

        this.log(`Source directory validated: ${this.sourceDir}`);
        return true;
    }

    async analyzeStructure() {
        this.log('Analyzing repository structure...');
        
        const analysis = {
            sourceFiles: await this.scanDirectory(this.sourceDir),
            targetFiles: await this.scanDirectory(this.basePath, ['Claude_Code_Dev_Stack_v3']),
            conflicts: [],
            mergeable: [],
            moveable: []
        };

        // Identify conflicts and categorize operations
        for (const sourceFile of analysis.sourceFiles) {
            const relativePath = path.relative(this.sourceDir, sourceFile);
            const targetPath = path.join(this.basePath, relativePath);
            
            if (existsSync(targetPath)) {
                const fileName = path.basename(relativePath);
                
                if (this.mergeableFiles.includes(fileName)) {
                    analysis.mergeable.push({
                        source: sourceFile,
                        target: targetPath,
                        relativePath,
                        type: 'merge'
                    });
                } else {
                    analysis.conflicts.push({
                        source: sourceFile,
                        target: targetPath,
                        relativePath,
                        type: 'conflict'
                    });
                }
            } else {
                analysis.moveable.push({
                    source: sourceFile,
                    target: targetPath,
                    relativePath,
                    type: 'move'
                });
            }
        }

        this.log(`Analysis complete:`);
        this.log(`  - Files to move: ${analysis.moveable.length}`);
        this.log(`  - Files to merge: ${analysis.mergeable.length}`);
        this.log(`  - Conflicts found: ${analysis.conflicts.length}`);

        return analysis;
    }

    async scanDirectory(dirPath, excludeDirs = []) {
        const files = [];
        
        try {
            const entries = await fs.readdir(dirPath, { withFileTypes: true });
            
            for (const entry of entries) {
                const fullPath = path.join(dirPath, entry.name);
                
                // Skip excluded directories
                if (excludeDirs.includes(entry.name)) {
                    continue;
                }
                
                // Skip patterns
                if (this.shouldSkip(entry.name)) {
                    continue;
                }
                
                if (entry.isDirectory()) {
                    const subFiles = await this.scanDirectory(fullPath);
                    files.push(...subFiles);
                } else if (entry.isFile()) {
                    files.push(fullPath);
                }
            }
        } catch (error) {
            this.log(`Error scanning directory ${dirPath}: ${error.message}`, 'error');
        }
        
        return files;
    }

    shouldSkip(fileName) {
        return this.skipPatterns.some(pattern => pattern.test(fileName));
    }

    async createBackups(analysis) {
        this.log('Creating backups of conflicting files...');
        
        const backupDir = path.join(this.basePath, '.archive', 'pre-reorganization-backup');
        
        if (!this.dryRun) {
            await fs.mkdir(backupDir, { recursive: true });
        }

        for (const conflict of analysis.conflicts) {
            const backupPath = path.join(backupDir, conflict.relativePath);
            
            if (!this.dryRun) {
                await fs.mkdir(path.dirname(backupPath), { recursive: true });
                await fs.copyFile(conflict.target, backupPath);
            }
            
            this.log(`Backed up: ${conflict.relativePath}`);
        }

        // Also backup mergeable files
        for (const mergeable of analysis.mergeable) {
            const backupPath = path.join(backupDir, 'original-' + mergeable.relativePath);
            
            if (!this.dryRun) {
                await fs.mkdir(path.dirname(backupPath), { recursive: true });
                await fs.copyFile(mergeable.target, backupPath);
            }
            
            this.log(`Backed up for merge: ${mergeable.relativePath}`);
        }
    }

    async moveFiles(analysis) {
        this.log('Moving files to root level...');
        
        let movedCount = 0;
        
        for (const item of analysis.moveable) {
            try {
                if (!this.dryRun) {
                    await fs.mkdir(path.dirname(item.target), { recursive: true });
                    await fs.rename(item.source, item.target);
                }
                
                this.log(`Moved: ${item.relativePath}`);
                movedCount++;
                
                this.manifest.operations.push({
                    type: 'move',
                    source: path.relative(this.basePath, item.source),
                    target: path.relative(this.basePath, item.target),
                    timestamp: new Date().toISOString()
                });
                
            } catch (error) {
                this.log(`Failed to move ${item.relativePath}: ${error.message}`, 'error');
            }
        }
        
        return movedCount;
    }

    async handleConflicts(analysis) {
        this.log('Handling file conflicts...');
        
        let resolvedCount = 0;
        
        for (const conflict of analysis.conflicts) {
            try {
                // Create conflict resolution by renaming new file
                const parsedPath = path.parse(conflict.target);
                const newName = `${parsedPath.name}_v3${parsedPath.ext}`;
                const newTarget = path.join(parsedPath.dir, newName);
                
                if (!this.dryRun) {
                    await fs.mkdir(path.dirname(newTarget), { recursive: true });
                    await fs.rename(conflict.source, newTarget);
                }
                
                this.log(`Resolved conflict: ${conflict.relativePath} -> ${path.basename(newTarget)}`);
                resolvedCount++;
                
                this.manifest.conflicts.push({
                    originalPath: conflict.relativePath,
                    conflictResolution: path.relative(this.basePath, newTarget),
                    timestamp: new Date().toISOString()
                });
                
            } catch (error) {
                this.log(`Failed to resolve conflict for ${conflict.relativePath}: ${error.message}`, 'error');
            }
        }
        
        return resolvedCount;
    }

    async mergeFiles(analysis) {
        this.log('Merging compatible files...');
        
        let mergedCount = 0;
        
        for (const mergeable of analysis.mergeable) {
            try {
                const fileName = path.basename(mergeable.relativePath);
                
                switch (fileName) {
                    case 'README.md':
                        await this.mergeReadmeFiles(mergeable);
                        break;
                    case 'requirements.txt':
                        await this.mergeRequirementsFiles(mergeable);
                        break;
                    case 'package.json':
                        await this.mergePackageJsonFiles(mergeable);
                        break;
                    case '.gitignore':
                        await this.mergeGitignoreFiles(mergeable);
                        break;
                    default:
                        // For other files, just rename the new version
                        const parsedPath = path.parse(mergeable.target);
                        const newName = `${parsedPath.name}_v3${parsedPath.ext}`;
                        const newTarget = path.join(parsedPath.dir, newName);
                        
                        if (!this.dryRun) {
                            await fs.rename(mergeable.source, newTarget);
                        }
                        break;
                }
                
                this.log(`Merged: ${mergeable.relativePath}`);
                mergedCount++;
                
            } catch (error) {
                this.log(`Failed to merge ${mergeable.relativePath}: ${error.message}`, 'error');
            }
        }
        
        return mergedCount;
    }

    async mergeReadmeFiles(mergeable) {
        const originalContent = await fs.readFile(mergeable.target, 'utf8');
        const newContent = await fs.readFile(mergeable.source, 'utf8');
        
        const mergedContent = `# Claude Code Dev Stack v3.0

${newContent}

---

## Legacy Documentation

${originalContent}
`;
        
        if (!this.dryRun) {
            await fs.writeFile(mergeable.target, mergedContent);
        }
    }

    async mergeRequirementsFiles(mergeable) {
        const originalLines = (await fs.readFile(mergeable.target, 'utf8')).split('\n');
        const newLines = (await fs.readFile(mergeable.source, 'utf8')).split('\n');
        
        const combined = [...new Set([...originalLines, ...newLines])];
        const mergedContent = combined.filter(line => line.trim()).sort().join('\n');
        
        if (!this.dryRun) {
            await fs.writeFile(mergeable.target, mergedContent);
        }
    }

    async mergePackageJsonFiles(mergeable) {
        const originalPackage = JSON.parse(await fs.readFile(mergeable.target, 'utf8'));
        const newPackage = JSON.parse(await fs.readFile(mergeable.source, 'utf8'));
        
        const merged = {
            ...originalPackage,
            ...newPackage,
            dependencies: { ...originalPackage.dependencies, ...newPackage.dependencies },
            devDependencies: { ...originalPackage.devDependencies, ...newPackage.devDependencies },
            scripts: { ...originalPackage.scripts, ...newPackage.scripts }
        };
        
        if (!this.dryRun) {
            await fs.writeFile(mergeable.target, JSON.stringify(merged, null, 2));
        }
    }

    async mergeGitignoreFiles(mergeable) {
        const originalLines = (await fs.readFile(mergeable.target, 'utf8')).split('\n');
        const newLines = (await fs.readFile(mergeable.source, 'utf8')).split('\n');
        
        const combined = [...new Set([...originalLines, ...newLines])];
        const mergedContent = combined.filter(line => line.trim()).join('\n');
        
        if (!this.dryRun) {
            await fs.writeFile(mergeable.target, mergedContent);
        }
    }

    async cleanupEmptyDirectories() {
        this.log('Cleaning up empty directories...');
        
        try {
            // Check if source directory is empty after move
            const sourceContents = await fs.readdir(this.sourceDir);
            const nonEmptyContents = sourceContents.filter(item => !this.shouldSkip(item));
            
            if (nonEmptyContents.length === 0) {
                if (!this.dryRun) {
                    await fs.rmdir(this.sourceDir, { recursive: true });
                }
                this.log(`Removed empty source directory: ${this.sourceDir}`);
            } else {
                this.log(`Source directory not empty, keeping: ${nonEmptyContents.join(', ')}`);
            }
        } catch (error) {
            this.log(`Error cleaning up directories: ${error.message}`, 'warn');
        }
    }

    async generateManifest() {
        const manifestPath = path.join(this.basePath, '.archive', 'reorganization-manifest.json');
        
        this.manifest.summary = {
            totalOperations: this.manifest.operations.length,
            conflictsResolved: this.manifest.conflicts.length,
            completedAt: new Date().toISOString()
        };
        
        if (!this.dryRun) {
            await fs.mkdir(path.dirname(manifestPath), { recursive: true });
            await fs.writeFile(manifestPath, JSON.stringify(this.manifest, null, 2));
        }
        
        this.log(`Generated reorganization manifest: ${manifestPath}`);
        return manifestPath;
    }

    async generateReorganizationReport() {
        const reportPath = path.join(this.basePath, '.archive', 'reorganization-report.md');
        
        const report = `# Repository Reorganization Report

Generated: ${new Date().toISOString()}
Mode: ${this.dryRun ? 'Dry Run' : 'Live'}

## Summary

- Total operations: ${this.manifest.operations.length}
- Conflicts resolved: ${this.manifest.conflicts.length}
- Reorganization ${this.dryRun ? 'simulated' : 'completed'} successfully

## Operations Performed

${this.manifest.operations.map(op => `- [${op.level}] ${op.message}`).join('\n')}

## Conflicts Resolved

${this.manifest.conflicts.map(conflict => 
    `- ${conflict.originalPath} -> ${conflict.conflictResolution}`
).join('\n') || 'No conflicts found'}

## Next Steps

${this.dryRun ? `
1. Review this report carefully
2. Run with --live flag to perform actual reorganization
3. Test the reorganized structure
4. Commit changes to version control
` : `
1. Test the reorganized repository structure
2. Update any scripts or documentation that reference old paths
3. Commit the reorganized structure to version control
4. Update CI/CD pipelines if necessary
`}
`;

        if (!this.dryRun) {
            await fs.writeFile(reportPath, report);
        }
        
        this.log(`Generated reorganization report: ${reportPath}`);
        return reportPath;
    }

    async run() {
        try {
            this.log('Starting repository reorganization...');
            
            // Step 1: Validate environment
            await this.validateEnvironment();
            
            // Step 2: Analyze structure
            const analysis = await this.analyzeStructure();
            
            // Step 3: Create backups
            await this.createBackups(analysis);
            
            // Step 4: Move files
            const movedCount = await this.moveFiles(analysis);
            
            // Step 5: Handle conflicts
            const resolvedCount = await this.handleConflicts(analysis);
            
            // Step 6: Merge compatible files
            const mergedCount = await this.mergeFiles(analysis);
            
            // Step 7: Cleanup
            await this.cleanupEmptyDirectories();
            
            // Step 8: Generate documentation
            await this.generateManifest();
            await this.generateReorganizationReport();
            
            this.log('Repository reorganization complete!');
            this.log(`Files moved: ${movedCount}`);
            this.log(`Conflicts resolved: ${resolvedCount}`);
            this.log(`Files merged: ${mergedCount}`);
            
            return {
                success: true,
                movedCount,
                resolvedCount,
                mergedCount,
                manifest: this.manifest
            };
            
        } catch (error) {
            this.log(`Repository reorganization failed: ${error.message}`, 'error');
            throw error;
        }
    }
}

// CLI interface
async function main() {
    const args = process.argv.slice(2);
    const options = {
        dryRun: !args.includes('--live'),
        verbose: args.includes('--verbose') || args.includes('-v'),
        basePath: process.cwd()
    };

    console.log('Claude Code Dev Stack v3.0 Repository Reorganizer');
    console.log('================================================');
    
    const reorganizer = new RepoReorganizer(options);
    
    try {
        const result = await reorganizer.run();
        console.log('\nReorganization completed successfully!');
        
        if (options.dryRun) {
            console.log('\nTo perform actual reorganization, run:');
            console.log('node repo-reorganizer.js --live');
        }
        
        process.exit(0);
    } catch (error) {
        console.error('\nReorganization failed:', error.message);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = { RepoReorganizer };