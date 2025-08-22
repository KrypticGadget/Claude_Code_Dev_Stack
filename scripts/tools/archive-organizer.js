#!/usr/bin/env node

/**
 * Claude Code Dev Stack v3.0 Archive Organizer
 * 
 * Cross-platform Node.js script to organize and archive repository files
 * Features:
 * - Dry-run capability
 * - Rollback functionality
 * - File manifest generation
 * - Safe file operations with validation
 * - Cross-platform path handling
 */

const fs = require('fs').promises;
const path = require('path');
const { existsSync, createReadStream, createWriteStream } = require('fs');
const crypto = require('crypto');

class ArchiveOrganizer {
    constructor(options = {}) {
        this.dryRun = options.dryRun || false;
        this.verbose = options.verbose || false;
        this.basePath = options.basePath || process.cwd();
        this.manifest = {
            operations: [],
            timestamp: new Date().toISOString(),
            version: '1.0.0',
            dryRun: this.dryRun
        };
        
        // Archive structure configuration
        this.archiveStructure = {
            '.archive': {
                'old-tests': 'Move duplicate test files',
                'legacy-docs': 'Move outdated documentation',
                'deprecated-configs': 'Move old config files',
                'duplicate-components': 'Move duplicate UI components',
                'backup-scripts': 'Move redundant scripts'
            }
        };

        // File patterns to identify for archiving
        this.archivePatterns = {
            'old-tests': [
                /.*test.*\.py$/i,
                /.*Test.*\.js$/i,
                /.*\.test\.(js|ts|py)$/i,
                /test_.*\.py$/i,
                /.*_test\.py$/i
            ],
            'legacy-docs': [
                /README.*\.md$/i,
                /CHANGELOG.*\.md$/i,
                /HISTORY.*\.md$/i,
                /.*\.docs\.md$/i,
                /doc.*\.md$/i
            ],
            'deprecated-configs': [
                /.*\.config\.(old|bak|backup)$/i,
                /.*\.(old|bak|backup)\.(json|yaml|yml|ini)$/i,
                /config.*\.old$/i
            ],
            'duplicate-components': [
                /.*\.component\.(old|bak|backup)\.(js|ts|tsx|jsx)$/i,
                /.*\.(old|bak|backup)\.(vue|svelte)$/i
            ],
            'backup-scripts': [
                /.*\.(old|bak|backup)\.(sh|bat|ps1|py)$/i,
                /backup.*\.(sh|bat|ps1|py)$/i,
                /.*backup.*\.(sh|bat|ps1|py)$/i
            ]
        };

        // Files to exclude from archiving (keep in main repo)
        this.excludePatterns = [
            /node_modules/,
            /\.git/,
            /\.archive/,
            /venv/,
            /\.venv/,
            /__pycache__/,
            /\.DS_Store/,
            /Thumbs\.db/
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

    async createArchiveStructure() {
        this.log('Creating archive directory structure...');
        
        for (const [baseDir, subDirs] of Object.entries(this.archiveStructure)) {
            const baseDirPath = path.join(this.basePath, baseDir);
            
            if (!this.dryRun) {
                await fs.mkdir(baseDirPath, { recursive: true });
            }
            this.log(`Created directory: ${baseDirPath}`);
            
            if (typeof subDirs === 'object') {
                for (const [subDir, description] of Object.entries(subDirs)) {
                    const subDirPath = path.join(baseDirPath, subDir);
                    
                    if (!this.dryRun) {
                        await fs.mkdir(subDirPath, { recursive: true });
                        
                        // Create README in each archive subdirectory
                        const readmePath = path.join(subDirPath, 'README.md');
                        const readmeContent = `# ${subDir}\n\n${description}\n\nArchived on: ${new Date().toISOString()}\n`;
                        await fs.writeFile(readmePath, readmeContent);
                    }
                    
                    this.log(`Created archive subdirectory: ${subDirPath}`);
                }
            }
        }
    }

    async scanForArchivableFiles() {
        this.log('Scanning for archivable files...');
        const archivableFiles = {
            'old-tests': [],
            'legacy-docs': [],
            'deprecated-configs': [],
            'duplicate-components': [],
            'backup-scripts': []
        };

        await this.scanDirectory(this.basePath, archivableFiles);
        
        // Log findings
        for (const [category, files] of Object.entries(archivableFiles)) {
            this.log(`Found ${files.length} files for ${category}`);
            if (this.verbose) {
                files.forEach(file => this.log(`  - ${file}`, 'debug'));
            }
        }

        return archivableFiles;
    }

    async scanDirectory(dirPath, archivableFiles, depth = 0) {
        if (depth > 10) return; // Prevent infinite recursion
        
        try {
            const entries = await fs.readdir(dirPath, { withFileTypes: true });
            
            for (const entry of entries) {
                const fullPath = path.join(dirPath, entry.name);
                const relativePath = path.relative(this.basePath, fullPath);
                
                // Skip excluded paths
                if (this.shouldExclude(relativePath)) {
                    continue;
                }
                
                if (entry.isDirectory()) {
                    await this.scanDirectory(fullPath, archivableFiles, depth + 1);
                } else if (entry.isFile()) {
                    this.categorizeFile(relativePath, fullPath, archivableFiles);
                }
            }
        } catch (error) {
            this.log(`Error scanning directory ${dirPath}: ${error.message}`, 'error');
        }
    }

    shouldExclude(relativePath) {
        return this.excludePatterns.some(pattern => pattern.test(relativePath));
    }

    categorizeFile(relativePath, fullPath, archivableFiles) {
        for (const [category, patterns] of Object.entries(this.archivePatterns)) {
            if (patterns.some(pattern => pattern.test(relativePath))) {
                archivableFiles[category].push({
                    relativePath,
                    fullPath,
                    category
                });
                break; // File can only belong to one category
            }
        }
    }

    async moveFilesToArchive(archivableFiles) {
        this.log('Moving files to archive...');
        let movedCount = 0;

        for (const [category, files] of Object.entries(archivableFiles)) {
            if (files.length === 0) continue;

            this.log(`Moving ${files.length} files to ${category}...`);

            for (const fileInfo of files) {
                try {
                    const targetDir = path.join(this.basePath, '.archive', category);
                    const targetPath = path.join(targetDir, path.basename(fileInfo.relativePath));
                    
                    // Handle filename conflicts
                    const finalTargetPath = await this.getUniqueFilePath(targetPath);
                    
                    if (!this.dryRun) {
                        await this.moveFile(fileInfo.fullPath, finalTargetPath);
                    }
                    
                    this.log(`Moved: ${fileInfo.relativePath} -> ${path.relative(this.basePath, finalTargetPath)}`);
                    movedCount++;
                    
                    // Add to manifest
                    this.manifest.operations.push({
                        type: 'move',
                        source: fileInfo.relativePath,
                        target: path.relative(this.basePath, finalTargetPath),
                        category,
                        timestamp: new Date().toISOString()
                    });
                    
                } catch (error) {
                    this.log(`Failed to move ${fileInfo.relativePath}: ${error.message}`, 'error');
                }
            }
        }

        this.log(`Successfully moved ${movedCount} files to archive`);
        return movedCount;
    }

    async getUniqueFilePath(targetPath) {
        let counter = 1;
        let uniquePath = targetPath;
        
        while (existsSync(uniquePath)) {
            const parsedPath = path.parse(targetPath);
            uniquePath = path.join(
                parsedPath.dir,
                `${parsedPath.name}_${counter}${parsedPath.ext}`
            );
            counter++;
        }
        
        return uniquePath;
    }

    async moveFile(sourcePath, targetPath) {
        // Ensure target directory exists
        await fs.mkdir(path.dirname(targetPath), { recursive: true });
        
        // Move file
        await fs.rename(sourcePath, targetPath);
    }

    async generateManifest() {
        const manifestPath = path.join(this.basePath, '.archive', 'manifest.json');
        
        // Add summary statistics
        this.manifest.summary = {
            totalOperations: this.manifest.operations.length,
            operationsByType: {},
            operationsByCategory: {}
        };

        // Calculate statistics
        this.manifest.operations.forEach(op => {
            if (op.type) {
                this.manifest.summary.operationsByType[op.type] = 
                    (this.manifest.summary.operationsByType[op.type] || 0) + 1;
            }
            if (op.category) {
                this.manifest.summary.operationsByCategory[op.category] = 
                    (this.manifest.summary.operationsByCategory[op.category] || 0) + 1;
            }
        });

        if (!this.dryRun) {
            await fs.writeFile(manifestPath, JSON.stringify(this.manifest, null, 2));
        }
        
        this.log(`Generated manifest: ${manifestPath}`);
        return manifestPath;
    }

    async generateRollbackScript() {
        const rollbackScriptPath = path.join(this.basePath, '.archive', 'rollback.js');
        
        const rollbackScript = `#!/usr/bin/env node
/**
 * Rollback script for archive operations
 * Generated on: ${new Date().toISOString()}
 */

const fs = require('fs').promises;
const path = require('path');

async function rollback() {
    const manifestPath = path.join(__dirname, 'manifest.json');
    const manifest = JSON.parse(await fs.readFile(manifestPath, 'utf8'));
    
    console.log('Rolling back archive operations...');
    
    let rolledBack = 0;
    const moveOps = manifest.operations.filter(op => op.type === 'move');
    
    for (const op of moveOps.reverse()) {
        try {
            const sourcePath = path.resolve(__dirname, '..', '..', op.target);
            const targetPath = path.resolve(__dirname, '..', '..', op.source);
            
            // Ensure target directory exists
            await fs.mkdir(path.dirname(targetPath), { recursive: true });
            
            // Move file back
            await fs.rename(sourcePath, targetPath);
            console.log(\`Restored: \${op.target} -> \${op.source}\`);
            rolledBack++;
        } catch (error) {
            console.error(\`Failed to restore \${op.source}: \${error.message}\`);
        }
    }
    
    console.log(\`Rollback complete. Restored \${rolledBack} files.\`);
}

if (require.main === module) {
    rollback().catch(console.error);
}

module.exports = { rollback };
`;

        if (!this.dryRun) {
            await fs.writeFile(rollbackScriptPath, rollbackScript);
            
            // Make executable on Unix systems
            if (process.platform !== 'win32') {
                await fs.chmod(rollbackScriptPath, '755');
            }
        }
        
        this.log(`Generated rollback script: ${rollbackScriptPath}`);
        return rollbackScriptPath;
    }

    async run() {
        try {
            this.log('Starting Claude Code Dev Stack v3.0 Archive Organization...');
            this.log(`Base path: ${this.basePath}`);
            this.log(`Dry run mode: ${this.dryRun}`);
            
            // Step 1: Create archive structure
            await this.createArchiveStructure();
            
            // Step 2: Scan for archivable files
            const archivableFiles = await this.scanForArchivableFiles();
            
            // Step 3: Move files to archive
            const movedCount = await this.moveFilesToArchive(archivableFiles);
            
            // Step 4: Generate manifest and rollback script
            await this.generateManifest();
            await this.generateRollbackScript();
            
            this.log('Archive organization complete!');
            this.log(`Files processed: ${movedCount}`);
            
            if (this.dryRun) {
                this.log('This was a dry run. No files were actually moved.');
                this.log('Run with --live to perform actual file operations.');
            }
            
            return {
                success: true,
                movedCount,
                manifest: this.manifest
            };
            
        } catch (error) {
            this.log(`Archive organization failed: ${error.message}`, 'error');
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

    // Override base path if provided
    const basePathIndex = args.findIndex(arg => arg === '--path');
    if (basePathIndex !== -1 && args[basePathIndex + 1]) {
        options.basePath = path.resolve(args[basePathIndex + 1]);
    }

    console.log('Claude Code Dev Stack v3.0 Archive Organizer');
    console.log('=============================================');
    
    const organizer = new ArchiveOrganizer(options);
    
    try {
        const result = await organizer.run();
        console.log('\nOperation completed successfully!');
        
        if (options.dryRun) {
            console.log('\nTo perform actual file operations, run:');
            console.log('node archive-organizer.js --live');
        } else {
            console.log('\nTo rollback these changes, run:');
            console.log('node .archive/rollback.js');
        }
        
        process.exit(0);
    } catch (error) {
        console.error('\nOperation failed:', error.message);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = { ArchiveOrganizer };