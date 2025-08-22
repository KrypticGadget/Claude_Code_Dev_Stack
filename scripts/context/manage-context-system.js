#!/usr/bin/env node
/**
 * Context Preservation System Management Script
 * Comprehensive management tool for the context preservation system
 */

const fs = require('fs').promises;
const path = require('path');
const { spawn } = require('child_process');
const axios = require('axios');

class ContextSystemManager {
  constructor() {
    this.config = {
      contextApiUrl: process.env.CONTEXT_API_URL || 'http://localhost:3100',
      dockerComposeFile: path.join(__dirname, '../../docker-services/context-preservation.yml'),
      mainDockerCompose: path.join(__dirname, '../../docker-compose.yml'),
      schemaFile: path.join(__dirname, '../../config/context/schema.sql'),
      configFile: path.join(__dirname, '../../config/context/context-config.yml'),
    };

    this.services = [
      'context-api',
      'context-analytics',
      'context-backup',
      'context-monitor',
      'context-search',
      'context-replication',
      'context-cache-warmer'
    ];
  }

  /**
   * Main command handler
   */
  async run(command, options = {}) {
    try {
      switch (command) {
        case 'setup':
          await this.setupSystem();
          break;
        case 'start':
          await this.startServices(options.services);
          break;
        case 'stop':
          await this.stopServices(options.services);
          break;
        case 'restart':
          await this.restartServices(options.services);
          break;
        case 'status':
          await this.checkStatus();
          break;
        case 'logs':
          await this.showLogs(options.service, options.follow);
          break;
        case 'migrate':
          await this.runMigrations();
          break;
        case 'backup':
          await this.createBackup();
          break;
        case 'restore':
          await this.restoreBackup(options.backupFile);
          break;
        case 'test':
          await this.runTests(options.type);
          break;
        case 'benchmark':
          await this.runBenchmarks();
          break;
        case 'monitor':
          await this.startMonitoring();
          break;
        case 'health':
          await this.healthCheck();
          break;
        case 'stats':
          await this.showStats();
          break;
        case 'cleanup':
          await this.cleanupExpired();
          break;
        case 'export':
          await this.exportContexts(options.outputFile, options.filter);
          break;
        case 'import':
          await this.importContexts(options.inputFile, options.overwrite);
          break;
        default:
          this.showHelp();
      }
    } catch (error) {
      console.error('❌ Error:', error.message);
      process.exit(1);
    }
  }

  /**
   * Setup the entire context preservation system
   */
  async setupSystem() {
    console.log('🚀 Setting up Context Preservation System...\n');

    // Step 1: Install dependencies
    console.log('📦 Installing dependencies...');
    await this.runCommand('npm', ['install'], {
      cwd: path.join(__dirname, '../../core/context'),
    });

    // Step 2: Setup database schema
    console.log('🗄️  Setting up database schema...');
    await this.setupDatabase();

    // Step 3: Validate configuration
    console.log('⚙️  Validating configuration...');
    await this.validateConfig();

    // Step 4: Build Docker images
    console.log('🐳 Building Docker images...');
    await this.buildDockerImages();

    // Step 5: Start core services
    console.log('🔄 Starting core services...');
    await this.startServices(['context-api']);

    // Step 6: Run health check
    console.log('🏥 Running health check...');
    await this.waitForHealthy();

    // Step 7: Run initial tests
    console.log('🧪 Running system tests...');
    await this.runTests('unit');

    console.log('\n✅ Context Preservation System setup complete!');
    console.log('📊 Access the system at:', this.config.contextApiUrl);
    console.log('📚 API Documentation: ' + this.config.contextApiUrl + '/api/context/docs');
  }

  /**
   * Setup database schema
   */
  async setupDatabase() {
    try {
      const schemaExists = await this.fileExists(this.config.schemaFile);
      if (!schemaExists) {
        throw new Error(`Schema file not found: ${this.config.schemaFile}`);
      }

      // Run schema setup via Docker
      await this.runCommand('docker', [
        'exec',
        'claude-code-agents-v369_postgres_1',
        'psql',
        '-U', 'claude',
        '-d', 'claude_dev_stack',
        '-f', '/config/context/schema.sql'
      ]);

      console.log('✅ Database schema setup complete');
    } catch (error) {
      console.error('❌ Database setup failed:', error.message);
      throw error;
    }
  }

  /**
   * Validate system configuration
   */
  async validateConfig() {
    const configExists = await this.fileExists(this.config.configFile);
    if (!configExists) {
      throw new Error(`Configuration file not found: ${this.config.configFile}`);
    }

    // Validate required environment variables
    const required = [
      'POSTGRES_PASSWORD',
      'REDIS_PASSWORD',
    ];

    const missing = required.filter(env => !process.env[env]);
    if (missing.length > 0) {
      throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
    }

    console.log('✅ Configuration validation complete');
  }

  /**
   * Build Docker images
   */
  async buildDockerImages() {
    await this.runCommand('docker-compose', [
      '-f', this.config.dockerComposeFile,
      'build'
    ]);
    console.log('✅ Docker images built successfully');
  }

  /**
   * Start services
   */
  async startServices(serviceList = null) {
    const services = serviceList || this.services;
    console.log(`🔄 Starting services: ${services.join(', ')}`);

    await this.runCommand('docker-compose', [
      '-f', this.config.dockerComposeFile,
      'up', '-d',
      ...services
    ]);

    console.log('✅ Services started successfully');
  }

  /**
   * Stop services
   */
  async stopServices(serviceList = null) {
    const services = serviceList || this.services;
    console.log(`⏹️  Stopping services: ${services.join(', ')}`);

    await this.runCommand('docker-compose', [
      '-f', this.config.dockerComposeFile,
      'stop',
      ...services
    ]);

    console.log('✅ Services stopped successfully');
  }

  /**
   * Restart services
   */
  async restartServices(serviceList = null) {
    await this.stopServices(serviceList);
    await this.startServices(serviceList);
  }

  /**
   * Check system status
   */
  async checkStatus() {
    console.log('📊 Context Preservation System Status\n');

    // Check Docker services
    console.log('🐳 Docker Services:');
    try {
      const result = await this.runCommand('docker-compose', [
        '-f', this.config.dockerComposeFile,
        'ps'
      ], { capture: true });
      console.log(result.stdout);
    } catch (error) {
      console.error('❌ Docker status check failed:', error.message);
    }

    // Check API health
    console.log('\n🏥 API Health Check:');
    try {
      const response = await axios.get(`${this.config.contextApiUrl}/api/context/health`);
      console.log('✅ Context API:', response.data.status);
      console.log('   Uptime:', Math.round(response.data.uptime), 'seconds');
      console.log('   Connections:', response.data.connections);
    } catch (error) {
      console.error('❌ Context API health check failed:', error.message);
    }

    // Check database connection
    console.log('\n🗄️  Database Status:');
    try {
      const result = await this.runCommand('docker', [
        'exec',
        'claude-code-agents-v369_postgres_1',
        'pg_isready',
        '-U', 'claude',
        '-d', 'claude_dev_stack'
      ], { capture: true });
      console.log('✅ PostgreSQL:', result.stdout.trim());
    } catch (error) {
      console.error('❌ PostgreSQL check failed:', error.message);
    }

    // Check Redis connection
    console.log('\n🔴 Redis Status:');
    try {
      const result = await this.runCommand('docker', [
        'exec',
        'claude-code-agents-v369_redis_1',
        'redis-cli',
        'ping'
      ], { capture: true });
      console.log('✅ Redis:', result.stdout.trim());
    } catch (error) {
      console.error('❌ Redis check failed:', error.message);
    }
  }

  /**
   * Show service logs
   */
  async showLogs(service = null, follow = false) {
    const args = ['-f', this.config.dockerComposeFile, 'logs'];
    
    if (follow) {
      args.push('-f');
    }
    
    if (service) {
      args.push(service);
    }

    await this.runCommand('docker-compose', args, { inherit: true });
  }

  /**
   * Run database migrations
   */
  async runMigrations() {
    console.log('🔄 Running database migrations...');
    
    await this.runCommand('node', ['scripts/migrate.js'], {
      cwd: path.join(__dirname, '../../core/context'),
    });

    console.log('✅ Migrations completed successfully');
  }

  /**
   * Create system backup
   */
  async createBackup() {
    console.log('💾 Creating system backup...');
    
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const backupDir = path.join(__dirname, '../../backups', timestamp);
    
    await fs.mkdir(backupDir, { recursive: true });

    // Backup database
    await this.runCommand('docker', [
      'exec',
      'claude-code-agents-v369_postgres_1',
      'pg_dump',
      '-U', 'claude',
      '-d', 'claude_dev_stack',
      '--schema=context_system',
      '-f', `/backups/${timestamp}/context_db_backup.sql`
    ]);

    // Backup configuration
    await fs.copyFile(this.config.configFile, path.join(backupDir, 'context-config.yml'));

    console.log(`✅ Backup created: ${backupDir}`);
  }

  /**
   * Restore from backup
   */
  async restoreBackup(backupFile) {
    if (!backupFile) {
      throw new Error('Backup file path is required');
    }

    console.log(`🔄 Restoring from backup: ${backupFile}`);

    await this.runCommand('docker', [
      'exec', '-i',
      'claude-code-agents-v369_postgres_1',
      'psql',
      '-U', 'claude',
      '-d', 'claude_dev_stack'
    ], { stdin: backupFile });

    console.log('✅ Restore completed successfully');
  }

  /**
   * Run tests
   */
  async runTests(type = 'all') {
    console.log(`🧪 Running ${type} tests...`);

    const contextDir = path.join(__dirname, '../../core/context');
    
    switch (type) {
      case 'unit':
        await this.runCommand('npm', ['test'], { cwd: contextDir });
        break;
      case 'integration':
        await this.runCommand('npm', ['run', 'test:integration'], { cwd: contextDir });
        break;
      case 'all':
        await this.runCommand('npm', ['test'], { cwd: contextDir });
        await this.runCommand('npm', ['run', 'test:integration'], { cwd: contextDir });
        break;
      default:
        throw new Error(`Unknown test type: ${type}`);
    }

    console.log('✅ Tests completed successfully');
  }

  /**
   * Run performance benchmarks
   */
  async runBenchmarks() {
    console.log('⚡ Running performance benchmarks...');

    await this.runCommand('node', ['scripts/benchmark.js'], {
      cwd: path.join(__dirname, '../../core/context'),
    });

    console.log('✅ Benchmarks completed');
  }

  /**
   * Start monitoring dashboard
   */
  async startMonitoring() {
    console.log('📊 Starting monitoring dashboard...');
    
    await this.startServices(['context-monitor']);
    
    console.log('✅ Monitoring dashboard available at: http://localhost:3102');
  }

  /**
   * Perform health check
   */
  async healthCheck() {
    try {
      const response = await axios.get(`${this.config.contextApiUrl}/api/context/health`, {
        timeout: 5000
      });

      console.log('✅ System Health Check Passed');
      console.log('   Status:', response.data.status);
      console.log('   Uptime:', Math.round(response.data.uptime), 'seconds');
      console.log('   Memory Usage:', JSON.stringify(response.data.memory, null, 2));
      console.log('   Active Connections:', response.data.connections);

      return true;
    } catch (error) {
      console.error('❌ Health check failed:', error.message);
      return false;
    }
  }

  /**
   * Show system statistics
   */
  async showStats() {
    try {
      const response = await axios.get(`${this.config.contextApiUrl}/api/context/analytics`);
      const stats = response.data.analytics;

      console.log('📊 Context Preservation System Statistics\n');
      console.log(`📝 Total Contexts: ${stats.total_contexts}`);
      console.log(`🔄 Active Contexts: ${stats.total_contexts - (stats.expired_contexts || 0)}`);
      console.log(`👥 Unique Sessions: ${stats.unique_sessions}`);
      console.log(`🤖 Unique Agents: ${stats.unique_agents}`);
      console.log(`📈 Total Accesses: ${stats.total_accesses}`);
      console.log(`⚡ Avg Accesses per Context: ${parseFloat(stats.avg_accesses_per_context).toFixed(2)}`);
      console.log(`💾 Cache Hit Ratio: ${stats.cache_hit_ratio}%`);

    } catch (error) {
      console.error('❌ Failed to retrieve stats:', error.message);
    }
  }

  /**
   * Cleanup expired contexts
   */
  async cleanupExpired() {
    try {
      console.log('🧹 Cleaning up expired contexts...');

      // Call cleanup endpoint
      const response = await axios.post(`${this.config.contextApiUrl}/api/context/cleanup`);
      
      console.log(`✅ Cleanup completed: ${response.data.deleted} contexts removed`);
    } catch (error) {
      console.error('❌ Cleanup failed:', error.message);
    }
  }

  /**
   * Export contexts
   */
  async exportContexts(outputFile, filter = {}) {
    try {
      console.log('📤 Exporting contexts...');

      const response = await axios.post(`${this.config.contextApiUrl}/api/context/export`, {
        keys: filter.keys,
        format: 'json'
      });

      const exportData = response.data.export;
      await fs.writeFile(outputFile, JSON.stringify(exportData, null, 2));

      console.log(`✅ Export completed: ${exportData.count} contexts exported to ${outputFile}`);
    } catch (error) {
      console.error('❌ Export failed:', error.message);
    }
  }

  /**
   * Import contexts
   */
  async importContexts(inputFile, overwrite = false) {
    try {
      console.log('📥 Importing contexts...');

      const importData = JSON.parse(await fs.readFile(inputFile, 'utf8'));
      
      const response = await axios.post(`${this.config.contextApiUrl}/api/context/import`, {
        contexts: importData.contexts,
        overwrite
      });

      console.log(`✅ Import completed: ${response.data.imported} contexts imported`);
      if (response.data.failed > 0) {
        console.warn(`⚠️  ${response.data.failed} contexts failed to import`);
      }
    } catch (error) {
      console.error('❌ Import failed:', error.message);
    }
  }

  /**
   * Wait for services to be healthy
   */
  async waitForHealthy(timeout = 60000) {
    const start = Date.now();
    
    while (Date.now() - start < timeout) {
      try {
        const healthy = await this.healthCheck();
        if (healthy) {
          return true;
        }
      } catch (error) {
        // Continue waiting
      }
      
      await this.sleep(2000);
    }
    
    throw new Error('Health check timeout');
  }

  /**
   * Run shell command
   */
  async runCommand(command, args = [], options = {}) {
    return new Promise((resolve, reject) => {
      const child = spawn(command, args, {
        stdio: options.inherit ? 'inherit' : options.capture ? 'pipe' : 'inherit',
        cwd: options.cwd,
        env: { ...process.env, ...options.env }
      });

      let stdout = '';
      let stderr = '';

      if (options.capture) {
        child.stdout?.on('data', (data) => {
          stdout += data.toString();
        });

        child.stderr?.on('data', (data) => {
          stderr += data.toString();
        });
      }

      child.on('close', (code) => {
        if (code === 0) {
          resolve({ stdout, stderr, code });
        } else {
          reject(new Error(`Command failed with code ${code}: ${stderr}`));
        }
      });

      child.on('error', reject);
    });
  }

  /**
   * Check if file exists
   */
  async fileExists(filePath) {
    try {
      await fs.access(filePath);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Sleep for specified milliseconds
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Show help message
   */
  showHelp() {
    console.log(`
Context Preservation System Management

Usage: node manage-context-system.js <command> [options]

Commands:
  setup              Complete system setup
  start [services]   Start services (default: all)
  stop [services]    Stop services (default: all)
  restart [services] Restart services (default: all)
  status             Show system status
  logs [service]     Show logs (add -f to follow)
  migrate            Run database migrations
  backup             Create system backup
  restore <file>     Restore from backup
  test [type]        Run tests (unit|integration|all)
  benchmark          Run performance benchmarks
  monitor            Start monitoring dashboard
  health             Perform health check
  stats              Show system statistics
  cleanup            Cleanup expired contexts
  export <file>      Export contexts to file
  import <file>      Import contexts from file

Options:
  --services         Comma-separated list of services
  --follow, -f       Follow logs
  --type             Test type (unit|integration|all)
  --overwrite        Overwrite existing contexts on import

Examples:
  node manage-context-system.js setup
  node manage-context-system.js start --services context-api,context-analytics
  node manage-context-system.js logs context-api --follow
  node manage-context-system.js test --type integration
  node manage-context-system.js export contexts-backup.json
`);
  }
}

// CLI support
if (require.main === module) {
  const manager = new ContextSystemManager();
  const command = process.argv[2];
  
  // Parse options
  const options = {};
  for (let i = 3; i < process.argv.length; i++) {
    const arg = process.argv[i];
    if (arg.startsWith('--')) {
      const [key, value] = arg.substring(2).split('=');
      options[key] = value || process.argv[++i] || true;
    } else if (arg.startsWith('-')) {
      options[arg.substring(1)] = true;
    } else if (!options._args) {
      options._args = [arg];
    } else {
      options._args.push(arg);
    }
  }

  // Map common flags
  if (options.services) {
    options.services = options.services.split(',').map(s => s.trim());
  }
  if (options.f) {
    options.follow = true;
  }

  manager.run(command, options).catch(error => {
    console.error('❌ Error:', error.message);
    process.exit(1);
  });
}

module.exports = ContextSystemManager;