#!/usr/bin/env node

import { Command } from 'commander';
import chalk from 'chalk';
import { promises as fs } from 'fs';
import path from 'path';
import inquirer from 'inquirer';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const program = new Command();

program
  .name('claude-code-tunnel-config')
  .description('Configure tunnel settings and manage service definitions')
  .version('1.0.0')
  .option('-s, --show', 'Show current configuration')
  .option('-e, --edit', 'Interactive configuration editor')
  .option('-v, --validate', 'Validate configuration')
  .option('-r, --reset', 'Reset to default configuration')
  .option('--set <key=value>', 'Set specific configuration value')
  .option('--service <name>', 'Configure specific service')
  .option('--export <file>', 'Export configuration to file')
  .option('--import <file>', 'Import configuration from file')
  .action(async (options) => {
    try {
      const configPath = path.resolve(__dirname, '../config/tunnel/tunnel-config.json');
      const defaultConfigPath = path.resolve(__dirname, '../config/tunnel/tunnel-config.default.json');
      
      // Load current configuration
      let config;
      try {
        const configData = await fs.readFile(configPath, 'utf8');
        config = JSON.parse(configData);
      } catch (error) {
        console.log(chalk.yellow('⚠️ Configuration file not found, creating default...'));
        config = await createDefaultConfig();
        await saveConfig(config, configPath);
      }
      
      // Handle show option
      if (options.show) {
        console.log(chalk.blue.bold('🔧 Current Tunnel Configuration'));
        console.log(chalk.gray('=' + '='.repeat(60)));
        
        console.log(chalk.cyan('📋 General Settings:'));
        console.log(chalk.gray(`   Version: ${config.version}`));
        console.log(chalk.gray(`   Auto Start: ${config.settings.auto_start ? '✅' : '❌'}`));
        console.log(chalk.gray(`   Auto Restart: ${config.settings.auto_restart ? '✅' : '❌'}`));
        console.log(chalk.gray(`   Health Checks: ${config.settings.health_check_enabled ? '✅' : '❌'}`));
        console.log(chalk.gray(`   QR Codes: ${config.settings.qr_code_enabled ? '✅' : '❌'}`));
        console.log(chalk.gray(`   Notifications: ${config.settings.notifications_enabled ? '✅' : '❌'}`));
        
        console.log(chalk.cyan('\\n🌐 Configured Services:'));
        for (const [serviceName, serviceConfig] of Object.entries(config.services)) {
          console.log(chalk.yellow(`   📡 ${serviceName}`));
          console.log(chalk.gray(`      Name: ${serviceConfig.name}`));
          console.log(chalk.gray(`      Port: ${serviceConfig.port}`));
          console.log(chalk.gray(`      Subdomain: ${serviceConfig.subdomain}`));
          console.log(chalk.gray(`      Auth: ${serviceConfig.auth || 'None'}`));
          console.log(chalk.gray(`      Health Check: ${serviceConfig.health_check?.enabled ? '✅' : '❌'}`));
        }
        
        console.log(chalk.cyan('\\n🔌 Providers:'));
        for (const [providerName, providerConfig] of Object.entries(config.providers)) {
          const status = providerConfig.enabled ? '✅' : '❌';
          console.log(chalk.gray(`   ${providerName}: ${status} (Priority: ${providerConfig.priority})`));
        }
        
        return;
      }
      
      // Handle validation
      if (options.validate) {
        console.log(chalk.blue('🔍 Validating tunnel configuration...'));
        
        const validation = validateConfig(config);
        
        if (validation.valid) {
          console.log(chalk.green('✅ Configuration is valid'));
        } else {
          console.log(chalk.red('❌ Configuration has errors:'));
          validation.errors.forEach(error => {
            console.log(chalk.red(`   • ${error}`));
          });
        }
        
        console.log(chalk.blue(`\\n📊 Configuration Summary:`));
        console.log(chalk.gray(`   Services: ${Object.keys(config.services).length}`));
        console.log(chalk.gray(`   Providers: ${Object.keys(config.providers).length}`));
        console.log(chalk.gray(`   Health Checks: ${Object.values(config.services).filter(s => s.health_check?.enabled).length}`));
        
        return;
      }
      
      // Handle reset
      if (options.reset) {
        const { confirm } = await inquirer.prompt([{
          type: 'confirm',
          name: 'confirm',
          message: 'Are you sure you want to reset configuration to defaults?',
          default: false
        }]);
        
        if (confirm) {
          config = await createDefaultConfig();
          await saveConfig(config, configPath);
          console.log(chalk.green('✅ Configuration reset to defaults'));
        } else {
          console.log(chalk.blue('Operation cancelled'));
        }
        return;
      }
      
      // Handle export
      if (options.export) {
        const exportPath = path.resolve(options.export);
        await fs.writeFile(exportPath, JSON.stringify(config, null, 2));
        console.log(chalk.green(`✅ Configuration exported to: ${exportPath}`));
        return;
      }
      
      // Handle import
      if (options.import) {
        const importPath = path.resolve(options.import);
        try {
          const importData = await fs.readFile(importPath, 'utf8');
          const importConfig = JSON.parse(importData);
          
          const validation = validateConfig(importConfig);
          if (!validation.valid) {
            console.log(chalk.red('❌ Invalid configuration file:'));
            validation.errors.forEach(error => {
              console.log(chalk.red(`   • ${error}`));
            });
            return;
          }
          
          const { confirm } = await inquirer.prompt([{
            type: 'confirm',
            name: 'confirm',
            message: 'Import this configuration? (will overwrite current settings)',
            default: false
          }]);
          
          if (confirm) {
            await saveConfig(importConfig, configPath);
            console.log(chalk.green('✅ Configuration imported successfully'));
          }
        } catch (error) {
          console.log(chalk.red(`❌ Failed to import configuration: ${error.message}`));
        }
        return;
      }
      
      // Handle set option
      if (options.set) {
        const [key, value] = options.set.split('=');
        if (!key || value === undefined) {
          console.log(chalk.red('❌ Invalid format. Use --set key=value'));
          return;
        }
        
        // Parse value
        let parsedValue = value;
        if (value === 'true') parsedValue = true;
        else if (value === 'false') parsedValue = false;
        else if (!isNaN(value)) parsedValue = Number(value);
        
        // Set nested property
        const keys = key.split('.');
        let current = config;
        
        for (let i = 0; i < keys.length - 1; i++) {
          if (!(keys[i] in current)) {
            current[keys[i]] = {};
          }
          current = current[keys[i]];
        }
        
        current[keys[keys.length - 1]] = parsedValue;
        
        await saveConfig(config, configPath);
        console.log(chalk.green(`✅ Set ${key} = ${parsedValue}`));
        return;
      }
      
      // Handle service configuration
      if (options.service) {
        await configureService(config, options.service, configPath);
        return;
      }
      
      // Handle interactive editor
      if (options.edit) {
        await interactiveEditor(config, configPath);
        return;
      }
      
      // Default: show help
      console.log(chalk.blue.bold('🔧 Tunnel Configuration Manager'));
      console.log(chalk.gray('=' + '='.repeat(60)));
      console.log(chalk.yellow('Available commands:'));
      console.log(chalk.gray('  --show              Show current configuration'));
      console.log(chalk.gray('  --edit              Interactive configuration editor'));
      console.log(chalk.gray('  --validate          Validate configuration'));
      console.log(chalk.gray('  --reset             Reset to defaults'));
      console.log(chalk.gray('  --set key=value     Set specific value'));
      console.log(chalk.gray('  --service <name>    Configure service'));
      console.log(chalk.gray('  --export <file>     Export configuration'));
      console.log(chalk.gray('  --import <file>     Import configuration'));
      
    } catch (error) {
      console.log(chalk.red(`❌ Configuration error: ${error.message}`));
      process.exit(1);
    }
  });

async function createDefaultConfig() {
  return {
    "version": "1.0.0",
    "name": "Claude Code Tunnel Manager",
    "description": "Centralized tunnel management for Claude Code remote access",
    
    "providers": {
      "ngrok": {
        "enabled": true,
        "priority": 1,
        "config_path": "./config/ngrok/ngrok.yml",
        "binary_paths": {
          "win32": ["C:\\\\Program Files\\\\ngrok\\\\ngrok.exe", "C:\\\\Users\\\\%USERNAME%\\\\ngrok.exe", "ngrok.exe"],
          "darwin": ["/usr/local/bin/ngrok", "/opt/homebrew/bin/ngrok", "ngrok"],
          "linux": ["/usr/local/bin/ngrok", "/usr/bin/ngrok", "ngrok"]
        },
        "web_interface": "http://localhost:4040"
      }
    },
    
    "services": {
      "claude-app": {
        "name": "Claude Code Main Application",
        "port": 3000,
        "subdomain": "claude-dev",
        "auth": false,
        "health_check": {
          "enabled": true,
          "path": "/health",
          "interval": 30000,
          "timeout": 5000
        }
      },
      "claude-api": {
        "name": "Claude Code API Server",
        "port": 3001,
        "subdomain": "claude-api",
        "auth": false,
        "health_check": {
          "enabled": true,
          "path": "/api/health",
          "interval": 30000,
          "timeout": 5000
        }
      },
      "claude-ui": {
        "name": "Claude Code UI/Frontend",
        "port": 5173,
        "subdomain": "claude-ui",
        "auth": false,
        "health_check": {
          "enabled": true,
          "path": "/",
          "interval": 30000,
          "timeout": 5000
        }
      }
    },
    
    "settings": {
      "auto_start": true,
      "auto_restart": true,
      "max_retries": 3,
      "retry_delay": 5000,
      "health_check_enabled": true,
      "qr_code_enabled": true,
      "clipboard_enabled": true,
      "notifications_enabled": true,
      "logging": {
        "level": "info",
        "file": "./logs/tunnel-manager.log",
        "max_size": "10MB",
        "max_files": 5
      }
    }
  };
}

function validateConfig(config) {
  const errors = [];
  
  // Required fields
  if (!config.version) errors.push('Missing version field');
  if (!config.providers) errors.push('Missing providers configuration');
  if (!config.services) errors.push('Missing services configuration');
  if (!config.settings) errors.push('Missing settings configuration');
  
  // Validate providers
  if (config.providers) {
    const enabledProviders = Object.values(config.providers).filter(p => p.enabled);
    if (enabledProviders.length === 0) {
      errors.push('No providers enabled');
    }
  }
  
  // Validate services
  if (config.services) {
    for (const [name, service] of Object.entries(config.services)) {
      if (!service.port) errors.push(`Service ${name}: missing port`);
      if (!service.subdomain) errors.push(`Service ${name}: missing subdomain`);
      if (service.port < 1 || service.port > 65535) {
        errors.push(`Service ${name}: invalid port ${service.port}`);
      }
    }
  }
  
  return {
    valid: errors.length === 0,
    errors
  };
}

async function saveConfig(config, configPath) {
  await fs.writeFile(configPath, JSON.stringify(config, null, 2));
}

async function configureService(config, serviceName, configPath) {
  console.log(chalk.blue(`🔧 Configuring service: ${serviceName}`));
  
  const existingService = config.services[serviceName];
  
  const answers = await inquirer.prompt([
    {
      type: 'input',
      name: 'name',
      message: 'Service display name:',
      default: existingService?.name || serviceName
    },
    {
      type: 'number',
      name: 'port',
      message: 'Local port:',
      default: existingService?.port || 3000,
      validate: (value) => {
        if (value < 1 || value > 65535) {
          return 'Port must be between 1 and 65535';
        }
        return true;
      }
    },
    {
      type: 'input',
      name: 'subdomain',
      message: 'Subdomain:',
      default: existingService?.subdomain || serviceName
    },
    {
      type: 'confirm',
      name: 'auth',
      message: 'Enable authentication?',
      default: existingService?.auth || false
    },
    {
      type: 'confirm',
      name: 'health_check_enabled',
      message: 'Enable health checks?',
      default: existingService?.health_check?.enabled || true
    }
  ]);
  
  // Health check configuration
  let healthCheck = existingService?.health_check || {};
  
  if (answers.health_check_enabled) {
    const healthAnswers = await inquirer.prompt([
      {
        type: 'input',
        name: 'path',
        message: 'Health check path:',
        default: healthCheck.path || '/health'
      },
      {
        type: 'number',
        name: 'interval',
        message: 'Check interval (ms):',
        default: healthCheck.interval || 30000
      },
      {
        type: 'number',
        name: 'timeout',
        message: 'Request timeout (ms):',
        default: healthCheck.timeout || 5000
      }
    ]);
    
    healthCheck = {
      enabled: true,
      ...healthAnswers
    };
  } else {
    healthCheck = { enabled: false };
  }
  
  // Update configuration
  config.services[serviceName] = {
    name: answers.name,
    port: answers.port,
    subdomain: answers.subdomain,
    auth: answers.auth,
    health_check: healthCheck
  };
  
  await saveConfig(config, configPath);
  console.log(chalk.green(`✅ Service ${serviceName} configured successfully`));
}

async function interactiveEditor(config, configPath) {
  console.log(chalk.blue.bold('🔧 Interactive Configuration Editor'));
  
  const { section } = await inquirer.prompt([{
    type: 'list',
    name: 'section',
    message: 'What would you like to configure?',
    choices: [
      { name: '⚙️ General Settings', value: 'settings' },
      { name: '🌐 Services', value: 'services' },
      { name: '🔌 Providers', value: 'providers' },
      { name: '🔒 Security', value: 'security' },
      { name: '📋 View Full Config', value: 'view' },
      { name: '💾 Save & Exit', value: 'exit' }
    ]
  }]);
  
  switch (section) {
    case 'settings':
      await configureSettings(config);
      break;
    case 'services':
      await configureServices(config);
      break;
    case 'providers':
      await configureProviders(config);
      break;
    case 'view':
      console.log(JSON.stringify(config, null, 2));
      break;
    case 'exit':
      await saveConfig(config, configPath);
      console.log(chalk.green('✅ Configuration saved'));
      return;
  }
  
  // Continue editing
  await interactiveEditor(config, configPath);
}

async function configureSettings(config) {
  const answers = await inquirer.prompt([
    {
      type: 'confirm',
      name: 'auto_start',
      message: 'Auto-start tunnels?',
      default: config.settings.auto_start
    },
    {
      type: 'confirm',
      name: 'auto_restart',
      message: 'Auto-restart failed tunnels?',
      default: config.settings.auto_restart
    },
    {
      type: 'confirm',
      name: 'health_check_enabled',
      message: 'Enable health checks?',
      default: config.settings.health_check_enabled
    },
    {
      type: 'confirm',
      name: 'qr_code_enabled',
      message: 'Generate QR codes?',
      default: config.settings.qr_code_enabled
    },
    {
      type: 'confirm',
      name: 'notifications_enabled',
      message: 'Enable notifications?',
      default: config.settings.notifications_enabled
    }
  ]);
  
  config.settings = { ...config.settings, ...answers };
  console.log(chalk.green('✅ Settings updated'));
}

async function configureServices(config) {
  const { action } = await inquirer.prompt([{
    type: 'list',
    name: 'action',
    message: 'Service management:',
    choices: [
      { name: '➕ Add Service', value: 'add' },
      { name: '✏️ Edit Service', value: 'edit' },
      { name: '🗑️ Remove Service', value: 'remove' },
      { name: '📋 List Services', value: 'list' }
    ]
  }]);
  
  switch (action) {
    case 'add':
      const { newServiceName } = await inquirer.prompt([{
        type: 'input',
        name: 'newServiceName',
        message: 'New service name:',
        validate: (value) => {
          if (!value) return 'Service name is required';
          if (config.services[value]) return 'Service already exists';
          return true;
        }
      }]);
      await configureService(config, newServiceName, '');
      break;
      
    case 'edit':
      const { editService } = await inquirer.prompt([{
        type: 'list',
        name: 'editService',
        message: 'Select service to edit:',
        choices: Object.keys(config.services)
      }]);
      await configureService(config, editService, '');
      break;
      
    case 'remove':
      const { removeService } = await inquirer.prompt([{
        type: 'list',
        name: 'removeService',
        message: 'Select service to remove:',
        choices: Object.keys(config.services)
      }]);
      delete config.services[removeService];
      console.log(chalk.green(`✅ Service ${removeService} removed`));
      break;
      
    case 'list':
      console.log(chalk.cyan('\\n📋 Configured Services:'));
      for (const [name, service] of Object.entries(config.services)) {
        console.log(chalk.yellow(`   ${name}: ${service.name} (Port ${service.port})`));
      }
      break;
  }
}

async function configureProviders(config) {
  console.log(chalk.blue('🔌 Provider Configuration'));
  console.log(chalk.gray('Currently only ngrok is supported'));
  
  const { enabled } = await inquirer.prompt([{
    type: 'confirm',
    name: 'enabled',
    message: 'Enable ngrok provider?',
    default: config.providers.ngrok.enabled
  }]);
  
  config.providers.ngrok.enabled = enabled;
  console.log(chalk.green('✅ Provider settings updated'));
}

program.parse(process.argv);