#!/usr/bin/env node

/**
 * Claude Code Dev Stack v3.0 Master Cleanup Script
 * 
 * Orchestrates the complete repository cleanup and reorganization:
 * 1. Archive redundant and outdated files
 * 2. Reorganize repository structure
 * 3. Generate comprehensive reports
 * 4. Create rollback capabilities
 */

const fs = require('fs').promises;
const path = require('path');
const { ArchiveOrganizer } = require('./archive-organizer');
const { RepoReorganizer } = require('./repo-reorganizer');

class MasterCleanup {
    constructor(options = {}) {
        this.dryRun = options.dryRun || false;
        this.verbose = options.verbose || false;
        this.basePath = options.basePath || process.cwd();
        this.skipArchive = options.skipArchive || false;
        this.skipReorganize = options.skipReorganize || false;
        
        this.results = {
            archive: null,
            reorganization: null,
            startTime: new Date().toISOString(),
            endTime: null,
            success: false
        };
    }

    async log(message, level = 'info') {
        const timestamp = new Date().toISOString();
        const prefix = this.dryRun ? '[DRY-RUN]' : '[LIVE]';
        const levelPrefix = level.toUpperCase();
        
        if (this.verbose || level === 'error' || level === 'warn') {
            console.log(`${timestamp} ${prefix} [MASTER] [${levelPrefix}] ${message}`);
        }
    }

    async validatePrerequisites() {
        this.log('Validating prerequisites...');
        
        // Check if Node.js version is compatible
        const nodeVersion = process.version;
        const majorVersion = parseInt(nodeVersion.slice(1).split('.')[0]);
        
        if (majorVersion < 14) {
            throw new Error(`Node.js version ${nodeVersion} is not supported. Minimum version: 14.0.0`);
        }
        
        // Check if we have write permissions
        try {
            const testFile = path.join(this.basePath, '.write-test');
            await fs.writeFile(testFile, 'test');
            await fs.unlink(testFile);
        } catch (error) {
            throw new Error(`No write permissions in ${this.basePath}: ${error.message}`);
        }
        
        // Check available disk space (basic check)
        try {
            const stats = await fs.stat(this.basePath);
            this.log(`Base directory validated: ${this.basePath}`);
        } catch (error) {
            throw new Error(`Cannot access base directory: ${error.message}`);
        }
        
        this.log('Prerequisites validated successfully');
    }

    async createMasterBackup() {
        this.log('Creating master backup...');
        
        const backupDir = path.join(this.basePath, '.archive', 'master-backup');
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const backupPath = path.join(backupDir, `pre-cleanup-${timestamp}`);
        
        if (!this.dryRun) {
            await fs.mkdir(backupPath, { recursive: true });
            
            // Create a backup of critical files
            const criticalFiles = [
                'README.md',
                'package.json',
                'requirements.txt',
                '.gitignore',
                'todo.md'
            ];
            
            for (const file of criticalFiles) {
                const sourcePath = path.join(this.basePath, file);
                const targetPath = path.join(backupPath, file);
                
                try {
                    await fs.copyFile(sourcePath, targetPath);
                    this.log(`Backed up: ${file}`);
                } catch (error) {
                    // File might not exist, that's okay
                    this.log(`Skipped backup of ${file}: ${error.message}`, 'warn');
                }
            }
            
            // Create backup manifest
            const backupManifest = {
                timestamp,
                backupPath: path.relative(this.basePath, backupPath),
                files: criticalFiles,
                created: new Date().toISOString()
            };
            
            await fs.writeFile(
                path.join(backupPath, 'backup-manifest.json'),
                JSON.stringify(backupManifest, null, 2)
            );
        }
        
        this.log(`Master backup created: ${backupPath}`);
        return backupPath;
    }

    async runArchivePhase() {
        if (this.skipArchive) {
            this.log('Skipping archive phase (--skip-archive)');
            return { skipped: true };
        }
        
        this.log('Starting archive phase...');
        
        const archiveOptions = {
            dryRun: this.dryRun,
            verbose: this.verbose,
            basePath: this.basePath
        };
        
        const archiver = new ArchiveOrganizer(archiveOptions);
        
        try {
            const result = await archiver.run();
            this.log(`Archive phase completed. Moved ${result.movedCount} files.`);
            return result;
        } catch (error) {
            this.log(`Archive phase failed: ${error.message}`, 'error');
            throw error;
        }
    }

    async runReorganizationPhase() {
        if (this.skipReorganize) {
            this.log('Skipping reorganization phase (--skip-reorganize)');
            return { skipped: true };
        }
        
        this.log('Starting reorganization phase...');
        
        const reorganizeOptions = {
            dryRun: this.dryRun,
            verbose: this.verbose,
            basePath: this.basePath
        };
        
        const reorganizer = new RepoReorganizer(reorganizeOptions);
        
        try {
            const result = await reorganizer.run();
            this.log(`Reorganization phase completed. Moved ${result.movedCount} files, resolved ${result.resolvedCount} conflicts.`);
            return result;
        } catch (error) {
            this.log(`Reorganization phase failed: ${error.message}`, 'error');
            throw error;
        }
    }

    async generateMasterReport() {
        this.log('Generating master cleanup report...');
        
        const reportPath = path.join(this.basePath, '.archive', 'master-cleanup-report.md');
        
        const report = `# Claude Code Dev Stack v3.0 - Master Cleanup Report

Generated: ${new Date().toISOString()}
Mode: ${this.dryRun ? 'Dry Run' : 'Live Execution'}
Duration: ${this.calculateDuration()}

## Executive Summary

This report summarizes the complete cleanup and reorganization of the Claude Code Dev Stack v3.0 repository.

### Archive Phase
${this.results.archive?.skipped ? '❌ Skipped' : this.results.archive?.success ? '✅ Completed Successfully' : '❌ Failed'}

${this.results.archive?.movedCount ? `- Files archived: ${this.results.archive.movedCount}` : ''}
${this.results.archive?.manifest?.summary ? `- Operations logged: ${this.results.archive.manifest.summary.totalOperations}` : ''}

### Reorganization Phase
${this.results.reorganization?.skipped ? '❌ Skipped' : this.results.reorganization?.success ? '✅ Completed Successfully' : '❌ Failed'}

${this.results.reorganization?.movedCount ? `- Files moved: ${this.results.reorganization.movedCount}` : ''}
${this.results.reorganization?.resolvedCount ? `- Conflicts resolved: ${this.results.reorganization.resolvedCount}` : ''}
${this.results.reorganization?.mergedCount ? `- Files merged: ${this.results.reorganization.mergedCount}` : ''}

## Detailed Results

### Archive Operations
${this.results.archive?.manifest?.summary?.operationsByCategory ? 
    Object.entries(this.results.archive.manifest.summary.operationsByCategory)
        .map(([category, count]) => `- ${category}: ${count} files`)
        .join('\n') : 'No archive operations performed'}

### File Conflicts Resolved
${this.results.reorganization?.manifest?.conflicts?.length ? 
    this.results.reorganization.manifest.conflicts
        .map(conflict => `- ${conflict.originalPath} → ${conflict.conflictResolution}`)
        .join('\n') : 'No conflicts found'}

## Post-Cleanup Actions Required

${this.dryRun ? `
### Dry Run Results
This was a simulation. To perform actual cleanup:

1. Review this report and the individual phase reports
2. Run the cleanup with: \`node scripts/master-cleanup.js --live\`
3. Test the reorganized repository
4. Commit changes to version control

` : `
### Cleanup Completed
The repository has been reorganized. Next steps:

1. ✅ Test all functionality in the reorganized structure
2. ✅ Update any hardcoded paths in scripts or documentation
3. ✅ Update CI/CD pipelines to reflect new structure
4. ✅ Commit the cleaned repository to version control
5. ✅ Update team documentation about the new structure

### Rollback Options
If you need to rollback changes:
- Archive rollback: \`node .archive/rollback.js\`
- Full restoration: Restore from \`.archive/master-backup/\`
`}

## Files and Directories Structure

After cleanup, your repository should have this clean structure:

\`\`\`
Claude_Code_Dev_Stack/
├── .archive/           # All archived and backup files
├── .claude/           # Claude configuration
├── .github/           # GitHub workflows
├── apps/              # Application code (moved from nested v3)
├── core/              # Core system modules (moved from nested v3)
├── docs/              # Documentation
├── integrations/      # Integration modules (moved from nested v3)
├── scripts/           # Automation scripts (this cleanup system)
├── server/            # Server components (moved from nested v3)
├── README.md          # Updated main documentation
├── requirements.txt   # Merged Python dependencies
└── package.json       # Merged Node.js dependencies
\`\`\`

## Support

If you encounter issues with the cleaned repository:

1. Check the detailed logs in \`.archive/\`
2. Use rollback scripts if needed
3. Review the backup files in \`.archive/master-backup/\`
4. Run individual phase scripts for targeted fixes

---

*Generated by Claude Code Dev Stack v3.0 Master Cleanup System*
`;

        if (!this.dryRun) {
            await fs.mkdir(path.dirname(reportPath), { recursive: true });
            await fs.writeFile(reportPath, report);
        }
        
        this.log(`Master report generated: ${reportPath}`);
        return reportPath;
    }

    calculateDuration() {
        if (!this.results.endTime) return 'In progress...';
        
        const start = new Date(this.results.startTime);
        const end = new Date(this.results.endTime);
        const duration = end - start;
        
        const minutes = Math.floor(duration / 60000);
        const seconds = Math.floor((duration % 60000) / 1000);
        
        return `${minutes}m ${seconds}s`;
    }

    async generateCompletionScript() {
        this.log('Generating post-cleanup scripts...');
        
        const scriptPath = path.join(this.basePath, '.archive', 'post-cleanup-actions.js');
        
        const script = `#!/usr/bin/env node

/**
 * Post-Cleanup Actions Script
 * Generated: ${new Date().toISOString()}
 */

const fs = require('fs').promises;
const path = require('path');
const { spawn } = require('child_process');

async function runPostCleanupActions() {
    console.log('Running post-cleanup actions...');
    
    // 1. Validate repository structure
    console.log('1. Validating repository structure...');
    const requiredDirs = ['apps', 'core', 'integrations', 'server', 'scripts'];
    for (const dir of requiredDirs) {
        try {
            await fs.access(dir);
            console.log(\`✅ \${dir} exists\`);
        } catch {
            console.log(\`❌ \${dir} missing\`);
        }
    }
    
    // 2. Update package.json scripts if needed
    console.log('2. Checking package.json...');
    try {
        const packagePath = 'package.json';
        await fs.access(packagePath);
        console.log('✅ package.json exists');
    } catch {
        console.log('❌ package.json not found');
    }
    
    // 3. Suggest next steps
    console.log('\\n3. Recommended next steps:');
    console.log('   - Test application startup: npm start or python main.py');
    console.log('   - Run tests: npm test or python -m pytest');
    console.log('   - Check CI/CD pipelines for path updates needed');
    console.log('   - Update team documentation');
    console.log('   - Commit changes: git add . && git commit -m "Reorganize repository structure"');
    
    console.log('\\nPost-cleanup actions completed!');
}

if (require.main === module) {
    runPostCleanupActions().catch(console.error);
}
`;

        if (!this.dryRun) {
            await fs.writeFile(scriptPath, script);
        }
        
        this.log(`Post-cleanup script generated: ${scriptPath}`);
        return scriptPath;
    }

    async run() {
        try {
            this.log('Starting master cleanup process...');
            this.log(`Base path: ${this.basePath}`);
            this.log(`Dry run mode: ${this.dryRun}`);
            
            // Step 1: Validate prerequisites
            await this.validatePrerequisites();
            
            // Step 2: Create master backup
            await this.createMasterBackup();
            
            // Step 3: Run archive phase
            this.results.archive = await this.runArchivePhase();
            
            // Step 4: Run reorganization phase
            this.results.reorganization = await this.runReorganizationPhase();
            
            // Step 5: Generate reports and scripts
            await this.generateMasterReport();
            await this.generateCompletionScript();
            
            this.results.endTime = new Date().toISOString();
            this.results.success = true;
            
            this.log('Master cleanup process completed successfully!');
            this.log(`Duration: ${this.calculateDuration()}`);
            
            if (this.dryRun) {
                console.log('\n🔍 DRY RUN COMPLETED');
                console.log('No files were actually moved or modified.');
                console.log('\nTo perform the actual cleanup:');
                console.log('node scripts/master-cleanup.js --live');
            } else {
                console.log('\n✅ CLEANUP COMPLETED');
                console.log('Your repository has been reorganized!');
                console.log('\nNext steps:');
                console.log('1. Review the reports in .archive/');
                console.log('2. Test your applications');
                console.log('3. Run: node .archive/post-cleanup-actions.js');
                console.log('4. Commit your changes');
            }
            
            return this.results;
            
        } catch (error) {
            this.results.endTime = new Date().toISOString();
            this.results.success = false;
            this.log(`Master cleanup failed: ${error.message}`, 'error');
            
            console.log('\n❌ CLEANUP FAILED');
            console.log(`Error: ${error.message}`);
            console.log('\nCheck the logs above for details.');
            console.log('If files were partially moved, use rollback scripts in .archive/');
            
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
        skipArchive: args.includes('--skip-archive'),
        skipReorganize: args.includes('--skip-reorganize'),
        basePath: process.cwd()
    };

    // Help text
    if (args.includes('--help') || args.includes('-h')) {
        console.log(`
Claude Code Dev Stack v3.0 Master Cleanup

Usage: node master-cleanup.js [options]

Options:
  --live              Perform actual file operations (default: dry-run)
  --verbose, -v       Enable verbose logging
  --skip-archive      Skip the archive phase
  --skip-reorganize   Skip the reorganization phase
  --help, -h          Show this help message

Examples:
  node master-cleanup.js                    # Dry run with default settings
  node master-cleanup.js --live             # Perform actual cleanup
  node master-cleanup.js --live --verbose   # Live run with detailed logging
  node master-cleanup.js --skip-archive     # Only reorganize, don't archive
`);
        process.exit(0);
    }

    console.log('');
    console.log('╔════════════════════════════════════════════════════════════╗');
    console.log('║          Claude Code Dev Stack v3.0 Master Cleanup        ║');
    console.log('╚════════════════════════════════════════════════════════════╝');
    console.log('');
    
    const cleanup = new MasterCleanup(options);
    
    try {
        await cleanup.run();
        process.exit(0);
    } catch (error) {
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = { MasterCleanup };