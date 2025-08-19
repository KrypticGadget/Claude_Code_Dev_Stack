/**
 * UI Manager - Manages the unified React PWA dashboard
 */

import fs from 'fs-extra';
import path from 'path';
import chalk from 'chalk';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export class UIManager {
  constructor(options = {}) {
    this.options = options;
    this.uiPath = path.join(__dirname, '../../ui/react-pwa');
    this.initialized = false;
    this.server = null;
  }

  async initialize() {
    if (this.initialized) return;
    
    console.log(chalk.blue('🎨 Initializing UI Manager...'));
    
    // Check if React PWA exists
    const packageJsonPath = path.join(this.uiPath, 'package.json');
    if (await fs.pathExists(packageJsonPath)) {
      console.log(chalk.blue('📦 React PWA found'));
    } else {
      console.log(chalk.yellow('⚠️  React PWA not found, UI features will be limited'));
    }
    
    this.initialized = true;
    console.log(chalk.green('✅ UI Manager initialized'));
  }

  async start(options = {}) {
    if (options.install) {
      return await this.install(options.path);
    }

    console.log(chalk.blue('🚀 Starting unified PWA...'));
    
    const packageJsonPath = path.join(this.uiPath, 'package.json');
    if (!(await fs.pathExists(packageJsonPath))) {
      throw new Error('React PWA not found. Run installation first.');
    }

    // Install dependencies if needed
    const nodeModulesPath = path.join(this.uiPath, 'node_modules');
    if (!(await fs.pathExists(nodeModulesPath))) {
      console.log(chalk.blue('📦 Installing UI dependencies...'));
      await this.runCommand('npm', ['install'], this.uiPath);
    }

    // Start development server
    console.log(chalk.blue('🌐 Starting development server...'));
    this.server = spawn('npm', ['run', 'dev'], {
      cwd: this.uiPath,
      stdio: 'inherit',
      shell: true
    });

    return {
      success: true,
      url: 'http://localhost:3000',
      pid: this.server.pid
    };
  }

  async install(targetPath = null) {
    console.log(chalk.blue('📦 Installing unified PWA...'));
    
    const claudeConfigPath = targetPath || await this.detectClaudeConfigPath();
    const uiTargetPath = path.join(claudeConfigPath, 'ui');
    
    // Copy React PWA to target location
    if (await fs.pathExists(this.uiPath)) {
      await fs.copy(this.uiPath, uiTargetPath);
      console.log(chalk.green(`✅ PWA installed to: ${uiTargetPath}`));
      
      return {
        success: true,
        path: uiTargetPath,
        url: 'http://localhost:3000'
      };
    } else {
      console.log(chalk.yellow('⚠️  React PWA source not found, skipping UI installation'));
      return {
        success: false,
        error: 'PWA source not found'
      };
    }
  }

  async runCommand(command, args, cwd) {
    return new Promise((resolve, reject) => {
      const child = spawn(command, args, {
        cwd,
        stdio: 'inherit',
        shell: true
      });

      child.on('close', (code) => {
        if (code === 0) {
          resolve();
        } else {
          reject(new Error(`Command failed with code ${code}`));
        }
      });

      child.on('error', reject);
    });
  }

  async detectClaudeConfigPath() {
    const possiblePaths = [
      path.join(process.env.HOME || process.env.USERPROFILE, '.claude'),
      path.join(process.env.HOME || process.env.USERPROFILE, '.config', 'claude'),
      path.join(process.cwd(), '.claude')
    ];

    for (const testPath of possiblePaths) {
      if (await fs.pathExists(testPath)) {
        return testPath;
      }
    }

    // Default to home directory
    const defaultPath = path.join(process.env.HOME || process.env.USERPROFILE, '.claude');
    await fs.ensureDir(defaultPath);
    return defaultPath;
  }

  getStatus() {
    return {
      initialized: this.initialized,
      serverRunning: this.server !== null,
      uiPath: this.uiPath
    };
  }

  async stop() {
    if (this.server) {
      this.server.kill();
      this.server = null;
      console.log(chalk.yellow('⏹️  UI server stopped'));
    }
  }
}