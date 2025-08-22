#!/usr/bin/env node
/**
 * NGROK Setup Validator for Claude Code Dev Stack
 * Validates configuration, dependencies, and environment setup
 */

const fs = require('fs').promises;
const path = require('path');
const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);

class NgrokSetupValidator {
  constructor() {
    this.checks = [];
    this.warnings = [];
    this.errors = [];
    this.info = [];
  }

  /**
   * Run all validation checks
   */
  async validate() {
    console.log('🔍 Validating NGROK setup for Claude Code Dev Stack v3.6.9...');
    console.log('═'.repeat(60));

    try {
      // Core checks
      await this.checkNgrokInstallation();
      await this.checkAuthToken();
      await this.checkConfigurationFiles();
      await this.checkEnvironmentVariables();
      await this.checkPortAvailability();
      await this.checkDependencies();
      await this.checkPermissions();
      await this.checkLogDirectories();
      
      // Advanced checks
      await this.validateNgrokConfig();
      await this.checkNetworkConnectivity();
      await this.checkServiceCompatibility();
      
      // Display results
      this.displayResults();
      
      return this.errors.length === 0;
      
    } catch (error) {
      console.error('❌ Validation failed:', error.message);
      return false;
    }
  }

  /**
   * Check NGROK installation
   */
  async checkNgrokInstallation() {
    try {
      const { stdout } = await execAsync('ngrok version');
      const version = stdout.trim();
      
      this.info.push(`✅ NGROK installed: ${version}`);
      
      // Check if it's a recent version
      const versionMatch = version.match(/ngrok\\s+version\\s+([\\d\\.]+)/);
      if (versionMatch) {
        const versionNumber = versionMatch[1];
        const major = parseInt(versionNumber.split('.')[0]);
        
        if (major < 3) {
          this.warnings.push(`⚠️  NGROK version ${versionNumber} is older, consider upgrading to v3+`);
        }
      }
      
    } catch (error) {
      this.errors.push('❌ NGROK is not installed or not in PATH');
      this.errors.push('   Install from: https://ngrok.com/download');
    }
  }

  /**
   * Check auth token configuration
   */
  async checkAuthToken() {
    const tokenSources = [
      process.env.NGROK_AUTHTOKEN,
      await this.getEnvFileToken(),
      await this.getNgrokConfigToken()
    ];

    const hasToken = tokenSources.some(token => token && token.length > 10);

    if (hasToken) {
      this.info.push('✅ NGROK auth token configured');
    } else {
      this.errors.push('❌ NGROK auth token not found');
      this.errors.push('   Set NGROK_AUTHTOKEN environment variable');
      this.errors.push('   Or add to config/ngrok/.env file');
      this.errors.push('   Get token from: https://dashboard.ngrok.com/get-started/your-authtoken');
    }
  }

  /**
   * Get token from .env file
   */
  async getEnvFileToken() {
    try {
      const envPath = path.join(__dirname, '../config/ngrok/.env');
      const envContent = await fs.readFile(envPath, 'utf8');
      
      const tokenMatch = envContent.match(/NGROK_AUTHTOKEN\\s*=\\s*(.+)/);
      return tokenMatch ? tokenMatch[1].trim() : null;
    } catch (error) {
      return null;
    }
  }

  /**
   * Get token from NGROK config
   */
  async getNgrokConfigToken() {
    try {
      const { stdout } = await execAsync('ngrok config check');
      return stdout.includes('authtoken') ? 'configured' : null;
    } catch (error) {
      return null;
    }
  }

  /**
   * Check configuration files
   */
  async checkConfigurationFiles() {
    const configFiles = [
      'config/ngrok/ngrok-advanced.yml',
      'config/ngrok/ngrok.yml'
    ];

    for (const configFile of configFiles) {
      const fullPath = path.join(__dirname, '..', configFile);
      
      try {
        await fs.access(fullPath);
        this.info.push(`✅ Configuration file exists: ${configFile}`);
        
        // Validate YAML syntax
        const content = await fs.readFile(fullPath, 'utf8');
        if (content.includes('tunnels:')) {
          this.info.push(`✅ ${configFile} contains tunnel definitions`);
        } else {
          this.warnings.push(`⚠️  ${configFile} missing tunnel definitions`);
        }
        
      } catch (error) {
        this.warnings.push(`⚠️  Configuration file missing: ${configFile}`);
      }
    }
  }

  /**
   * Check environment variables
   */
  async checkEnvironmentVariables() {
    const requiredVars = [
      'NGROK_AUTHTOKEN'
    ];

    const optionalVars = [
      'NGROK_REGION',
      'NGROK_SUBDOMAIN_WEBAPP',
      'NGROK_SUBDOMAIN_API',
      'CLAUDE_WEBAPP_PORT',
      'CLAUDE_API_PORT',
      'CLAUDE_WS_PORT'
    ];

    // Check required variables
    for (const varName of requiredVars) {
      if (process.env[varName]) {
        this.info.push(`✅ Required env var set: ${varName}`);
      } else {
        this.errors.push(`❌ Required env var missing: ${varName}`);
      }
    }

    // Check optional variables
    let optionalCount = 0;
    for (const varName of optionalVars) {
      if (process.env[varName]) {
        optionalCount++;
      }
    }

    if (optionalCount > 0) {
      this.info.push(`✅ Optional env vars configured: ${optionalCount}/${optionalVars.length}`);
    } else {
      this.warnings.push('⚠️  No optional environment variables configured');
      this.warnings.push('   Consider setting NGROK_REGION, port overrides, etc.');
    }
  }

  /**
   * Check port availability
   */
  async checkPortAvailability() {
    const ports = [
      { port: 3000, service: 'Web App' },
      { port: 3001, service: 'API Alt' },
      { port: 3002, service: 'WebSocket' },
      { port: 3003, service: 'Terminal' },
      { port: 4000, service: 'Webhook Server' },
      { port: 4040, service: 'NGROK Dashboard' },
      { port: 8000, service: 'API Server' }
    ];

    const results = await Promise.all(
      ports.map(({ port, service }) => this.checkPort(port, service))
    );

    const available = results.filter(r => r.available).length;
    const total = results.length;

    if (available === total) {
      this.info.push(`✅ All ${total} required ports are available`);
    } else {
      this.warnings.push(`⚠️  ${total - available}/${total} ports are in use`);
      
      results.filter(r => !r.available).forEach(r => {
        this.warnings.push(`   Port ${r.port} (${r.service}) is in use`);
      });
    }
  }

  /**
   * Check if a port is available
   */
  async checkPort(port, service) {
    return new Promise((resolve) => {
      const server = require('net').createServer();
      
      server.listen(port, () => {
        server.close(() => {
          resolve({ port, service, available: true });
        });
      });
      
      server.on('error', () => {
        resolve({ port, service, available: false });
      });
    });
  }

  /**
   * Check Node.js dependencies
   */
  async checkDependencies() {
    const requiredDeps = [
      'express',
      'axios',
      'cors',
      'ws',
      'chalk',
      'commander'
    ];

    try {
      const packageJsonPath = path.join(__dirname, '../package.json');
      const packageJson = JSON.parse(await fs.readFile(packageJsonPath, 'utf8'));
      const deps = { ...packageJson.dependencies, ...packageJson.devDependencies };

      const missing = requiredDeps.filter(dep => !deps[dep]);

      if (missing.length === 0) {
        this.info.push('✅ All required Node.js dependencies available');
      } else {
        this.errors.push(`❌ Missing dependencies: ${missing.join(', ')}`);
        this.errors.push('   Run: npm install');
      }

    } catch (error) {
      this.errors.push('❌ Cannot read package.json');
    }
  }

  /**
   * Check file permissions
   */
  async checkPermissions() {
    const scriptsToCheck = [
      'scripts/ngrok-manager.js',
      'scripts/webhook-server.js',
      'scripts/ngrok-health-monitor.js',
      'scripts/start-all-services.js',
      'bin/ngrok-cli.js'
    ];

    let executableCount = 0;

    for (const script of scriptsToCheck) {
      const fullPath = path.join(__dirname, '..', script);
      
      try {
        await fs.access(fullPath);
        
        // Check if file is executable (Unix-like systems)
        if (process.platform !== 'win32') {
          try {
            await fs.access(fullPath, fs.constants.X_OK);
            executableCount++;
          } catch (error) {
            this.warnings.push(`⚠️  Script not executable: ${script}`);
            this.warnings.push(`   Run: chmod +x ${script}`);
          }
        }
        
      } catch (error) {
        this.errors.push(`❌ Script file missing: ${script}`);
      }
    }

    if (process.platform !== 'win32' && executableCount > 0) {
      this.info.push(`✅ Script files are executable: ${executableCount}/${scriptsToCheck.length}`);
    }
  }

  /**
   * Check log directories
   */
  async checkLogDirectories() {
    const logDirs = [
      'logs',
      'tmp'
    ];

    for (const dir of logDirs) {
      const fullPath = path.join(__dirname, '..', dir);
      
      try {
        await fs.mkdir(fullPath, { recursive: true });
        this.info.push(`✅ Log directory exists: ${dir}/`);
      } catch (error) {
        this.warnings.push(`⚠️  Cannot create log directory: ${dir}/`);
      }
    }
  }

  /**
   * Validate NGROK configuration syntax
   */
  async validateNgrokConfig() {
    try {
      const configPath = path.join(__dirname, '../config/ngrok/ngrok-advanced.yml');
      const { stdout, stderr } = await execAsync(`ngrok config check --config="${configPath}"`);
      
      if (stderr && stderr.includes('error')) {
        this.errors.push('❌ NGROK configuration has errors');
        this.errors.push(`   ${stderr.trim()}`);
      } else {
        this.info.push('✅ NGROK configuration syntax is valid');
      }
      
    } catch (error) {
      this.warnings.push('⚠️  Could not validate NGROK configuration');
      this.warnings.push('   NGROK config check failed');
    }
  }

  /**
   * Check network connectivity
   */
  async checkNetworkConnectivity() {
    const testUrls = [
      'https://api.ngrok.com',
      'https://tunnel.ngrok.com'
    ];

    const axios = require('axios');
    let successCount = 0;

    for (const url of testUrls) {
      try {
        await axios.get(url, { timeout: 5000 });
        successCount++;
      } catch (error) {
        // Network check failed
      }
    }

    if (successCount === testUrls.length) {
      this.info.push('✅ Network connectivity to NGROK services OK');
    } else {
      this.warnings.push('⚠️  Network connectivity issues detected');
      this.warnings.push('   Check firewall and proxy settings');
    }
  }

  /**
   * Check service compatibility
   */
  async checkServiceCompatibility() {
    // Check Node.js version
    const nodeVersion = process.version;
    const majorVersion = parseInt(nodeVersion.replace('v', '').split('.')[0]);

    if (majorVersion >= 18) {
      this.info.push(`✅ Node.js version compatible: ${nodeVersion}`);
    } else {
      this.errors.push(`❌ Node.js version too old: ${nodeVersion}`);
      this.errors.push('   Requires Node.js v18 or higher');
    }

    // Check platform compatibility
    const platform = process.platform;
    const supportedPlatforms = ['win32', 'darwin', 'linux'];

    if (supportedPlatforms.includes(platform)) {
      this.info.push(`✅ Platform supported: ${platform}`);
    } else {
      this.warnings.push(`⚠️  Platform may not be fully supported: ${platform}`);
    }
  }

  /**
   * Display validation results
   */
  displayResults() {
    console.log('\\n📊 Validation Results:');
    console.log('═'.repeat(30));

    // Display info messages
    if (this.info.length > 0) {
      console.log('\\n✅ Information:');
      this.info.forEach(msg => console.log(`   ${msg}`));
    }

    // Display warnings
    if (this.warnings.length > 0) {
      console.log('\\n⚠️  Warnings:');
      this.warnings.forEach(msg => console.log(`   ${msg}`));
    }

    // Display errors
    if (this.errors.length > 0) {
      console.log('\\n❌ Errors:');
      this.errors.forEach(msg => console.log(`   ${msg}`));
    }

    // Summary
    console.log('\\n📈 Summary:');
    console.log(`   ✅ Info: ${this.info.length}`);
    console.log(`   ⚠️  Warnings: ${this.warnings.length}`);
    console.log(`   ❌ Errors: ${this.errors.length}`);

    if (this.errors.length === 0) {
      console.log('\\n🎉 NGROK setup validation passed!');
      console.log('\\n💡 Next steps:');
      console.log('   1. npm run services:start      - Start all services');
      console.log('   2. claude-code-ngrok status     - Check tunnel status');
      console.log('   3. claude-code-ngrok urls       - Get tunnel URLs');
    } else {
      console.log('\\n🔧 Please fix the errors above before proceeding.');
    }

    console.log('\\n📚 Documentation: docs/NGROK_INTEGRATION_GUIDE.md');
  }

  /**
   * Auto-fix common issues
   */
  async autoFix() {
    console.log('\\n🔧 Attempting to auto-fix common issues...');

    try {
      // Create missing directories
      const dirs = ['logs', 'tmp', 'config/ngrok'];
      for (const dir of dirs) {
        const fullPath = path.join(__dirname, '..', dir);
        await fs.mkdir(fullPath, { recursive: true });
      }
      console.log('✅ Created missing directories');

      // Create .env.example if it doesn't exist
      const envExamplePath = path.join(__dirname, '../config/ngrok/.env.example');
      try {
        await fs.access(envExamplePath);
      } catch (error) {
        // File doesn't exist, create it
        const envContent = `# NGROK Configuration
NGROK_AUTHTOKEN=your_token_here
NGROK_REGION=us
CLAUDE_WEBAPP_PORT=3000
CLAUDE_API_PORT=8000
`;
        await fs.writeFile(envExamplePath, envContent);
        console.log('✅ Created .env.example file');
      }

      // Make scripts executable (Unix-like systems)
      if (process.platform !== 'win32') {
        const scripts = [
          'scripts/ngrok-manager.js',
          'scripts/webhook-server.js',
          'scripts/start-all-services.js',
          'bin/ngrok-cli.js'
        ];

        for (const script of scripts) {
          const fullPath = path.join(__dirname, '..', script);
          try {
            await execAsync(`chmod +x "${fullPath}"`);
          } catch (error) {
            // Ignore permission errors
          }
        }
        console.log('✅ Made scripts executable');
      }

      console.log('\\n🎉 Auto-fix completed!');
      console.log('Run validation again to check remaining issues.');

    } catch (error) {
      console.error('❌ Auto-fix failed:', error.message);
    }
  }
}

// CLI interface
if (require.main === module) {
  const validator = new NgrokSetupValidator();
  
  const command = process.argv[2];
  
  if (command === 'fix') {
    validator.autoFix().catch(console.error);
  } else {
    validator.validate().then(success => {
      process.exit(success ? 0 : 1);
    }).catch(error => {
      console.error('Validation failed:', error);
      process.exit(1);
    });
  }
}

module.exports = NgrokSetupValidator;