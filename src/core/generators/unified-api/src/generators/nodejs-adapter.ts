/**
 * Node.js generator adapter for the Unified MCP Generator
 */

import { spawn } from 'child_process';
import { join, resolve } from 'path';
import { promises as fs } from 'fs';
import { UnifiedGeneratorConfig, GenerationResult, GeneratorStatus, TransportType } from '../types.js';

/**
 * Adapter for the Node.js MCP generator
 */
export class NodeJSGeneratorAdapter {
  private config: UnifiedGeneratorConfig;
  private nodeGeneratorPath: string;

  constructor(config: UnifiedGeneratorConfig, nodeGeneratorPath?: string) {
    this.config = config;
    this.nodeGeneratorPath = nodeGeneratorPath || this.findNodeGenerator();
  }

  /**
   * Generates MCP project using Node.js generator
   */
  async generate(
    specPath: string,
    outputDir: string,
    onProgress?: (status: GeneratorStatus) => void
  ): Promise<GenerationResult> {
    const startTime = new Date();
    const files: GenerationResult['files'] = [];
    const errors: GenerationResult['errors'] = [];
    const warnings: GenerationResult['warnings'] = [];

    try {
      onProgress?.({
        phase: 'setup',
        progress: 10,
        operation: 'Preparing Node.js generator',
        filesProcessed: 0,
        totalFiles: 0,
        startTime
      });

      // Build Node.js generator command
      const command = this.buildCommand(specPath, outputDir);

      onProgress?.({
        phase: 'generation',
        progress: 20,
        operation: 'Running Node.js generator',
        filesProcessed: 0,
        totalFiles: 0,
        startTime
      });

      // Execute Node.js generator
      const result = await this.executeNodeGenerator(command, onProgress, startTime);

      onProgress?.({
        phase: 'post-processing',
        progress: 70,
        operation: 'Post-processing generated files',
        filesProcessed: 0,
        totalFiles: 0,
        startTime
      });

      // Post-process generated files based on configuration
      await this.postProcessFiles(outputDir);

      onProgress?.({
        phase: 'validation',
        progress: 90,
        operation: 'Validating generated files',
        filesProcessed: 0,
        totalFiles: 0,
        startTime
      });

      // Collect generated files
      const generatedFiles = await this.collectGeneratedFiles(outputDir);
      files.push(...generatedFiles);

      // Parse Node.js generator output for errors/warnings
      if (result.stderr) {
        const stderrLines = result.stderr.split('\n').filter(line => line.trim());
        for (const line of stderrLines) {
          if (line.toLowerCase().includes('error')) {
            errors.push({
              message: line,
              code: 'nodejs_generator_error'
            });
          } else if (line.toLowerCase().includes('warning')) {
            warnings.push({
              message: line,
              code: 'nodejs_generator_warning'
            });
          }
        }
      }

      onProgress?.({
        phase: 'complete',
        progress: 100,
        operation: 'Generation complete',
        filesProcessed: files.length,
        totalFiles: files.length,
        startTime
      });

      return {
        success: errors.length === 0,
        files,
        errors,
        warnings,
        metadata: {
          generator: 'nodejs',
          projectType: this.config.projectType,
          duration: Date.now() - startTime.getTime(),
          outputDir,
          configUsed: this.config
        }
      };

    } catch (error) {
      errors.push({
        message: error instanceof Error ? error.message : 'Unknown error',
        code: 'nodejs_adapter_error'
      });

      return {
        success: false,
        files,
        errors,
        warnings,
        metadata: {
          generator: 'nodejs',
          projectType: this.config.projectType,
          duration: Date.now() - startTime.getTime(),
          outputDir,
          configUsed: this.config
        }
      };
    }
  }

  /**
   * Finds the Node.js generator path
   */
  private findNodeGenerator(): string {
    // Try to find the Node.js generator relative to this file
    const possiblePaths = [
      join(__dirname, '../../nodejs/dist/index.js'),
      join(__dirname, '../../../nodejs/dist/index.js'),
      join(process.cwd(), 'core/generators/nodejs/dist/index.js'),
      join(process.cwd(), '../nodejs/dist/index.js')
    ];

    for (const path of possiblePaths) {
      try {
        const resolvedPath = resolve(path);
        return resolvedPath;
      } catch {
        continue;
      }
    }

    // Fallback to using the npm package if installed globally
    return 'openapi-mcp-generator';
  }

  /**
   * Builds the command to execute the Node.js generator
   */
  private buildCommand(specPath: string, outputDir: string): string[] {
    const command = ['node', this.nodeGeneratorPath];
    
    // Add basic arguments
    command.push('-i', specPath);
    command.push('-o', outputDir);

    // Add server name if specified
    if (this.config.common.name) {
      command.push('-n', this.config.common.name);
    }

    // Add server version if specified
    if (this.config.common.version) {
      command.push('-v', this.config.common.version);
    }

    // Add base URL if specified
    if (this.config.common.baseUrl) {
      command.push('-b', this.config.common.baseUrl);
    }

    // Add transport type
    const transport = this.mapTransportType(this.config.common.transport || 'stdio');
    command.push('-t', transport);

    // Add port if specified for web transports
    if (this.config.common.port && ['web', 'streamable-http'].includes(transport)) {
      command.push('-p', this.config.common.port.toString());
    }

    // Force overwrite
    command.push('--force');

    return command;
  }

  /**
   * Maps unified transport types to Node.js generator transport types
   */
  private mapTransportType(transport: TransportType): string {
    const transportMap: Record<TransportType, string> = {
      'stdio': 'stdio',
      'web': 'web',
      'streamable-http': 'streamable-http',
      'websocket': 'web' // Fallback to web for websocket
    };

    return transportMap[transport] || 'stdio';
  }

  /**
   * Executes the Node.js generator
   */
  private async executeNodeGenerator(
    command: string[],
    onProgress?: (status: GeneratorStatus) => void,
    startTime?: Date
  ): Promise<{ stdout: string; stderr: string }> {
    return new Promise((resolve, reject) => {
      const [nodeCmd, ...args] = command;
      const child = spawn(nodeCmd, args, {
        stdio: ['pipe', 'pipe', 'pipe'],
        shell: process.platform === 'win32'
      });

      let stdout = '';
      let stderr = '';

      child.stdout?.on('data', (data) => {
        const output = data.toString();
        stdout += output;

        // Parse progress information from Node.js generator output
        if (onProgress && startTime) {
          const lines = output.split('\n');
          for (const line of lines) {
            if (line.includes('Generating') || line.includes('Creating')) {
              onProgress({
                phase: 'generation',
                progress: Math.min(90, 20 + Math.random() * 50), // Estimate progress
                operation: line.trim(),
                filesProcessed: 0,
                totalFiles: 0,
                startTime
              });
            }
          }
        }
      });

      child.stderr?.on('data', (data) => {
        stderr += data.toString();
      });

      child.on('close', (code) => {
        if (code === 0) {
          resolve({ stdout, stderr });
        } else {
          reject(new Error(`Node.js generator failed with code ${code}: ${stderr}`));
        }
      });

      child.on('error', (error) => {
        reject(new Error(`Failed to start Node.js generator: ${error.message}`));
      });
    });
  }

  /**
   * Post-processes generated files based on configuration
   */
  private async postProcessFiles(outputDir: string): Promise<void> {
    try {
      // Update package.json with additional dependencies and configuration
      await this.updatePackageJson(outputDir);

      // Update TypeScript configuration if enabled
      if (this.config.nodejs?.typescript) {
        await this.updateTsConfig(outputDir);
      }

      // Update ESLint configuration if enabled
      if (this.config.nodejs?.eslint) {
        await this.updateEslintConfig(outputDir);
      }

      // Update Jest configuration if enabled
      if (this.config.nodejs?.jest) {
        await this.updateJestConfig(outputDir);
      }

      // Add additional environment variables
      if (this.config.common.environment) {
        await this.updateEnvFile(outputDir);
      }

    } catch (error) {
      // Non-fatal errors in post-processing
      console.warn('Warning: Post-processing failed:', error);
    }
  }

  /**
   * Updates package.json with additional configuration
   */
  private async updatePackageJson(outputDir: string): Promise<void> {
    const packageJsonPath = join(outputDir, 'package.json');
    
    try {
      const packageJsonContent = await fs.readFile(packageJsonPath, 'utf-8');
      const packageJson = JSON.parse(packageJsonContent);

      // Update metadata
      if (this.config.common.description) {
        packageJson.description = this.config.common.description;
      }

      if (this.config.common.author) {
        packageJson.author = this.config.common.author.name;
        if (this.config.common.author.email) {
          packageJson.author += ` <${this.config.common.author.email}>`;
        }
      }

      if (this.config.common.license) {
        packageJson.license = this.config.common.license;
      }

      // Add additional dependencies
      if (this.config.nodejs?.dependencies) {
        packageJson.dependencies = {
          ...packageJson.dependencies,
          ...this.config.nodejs.dependencies
        };
      }

      // Add additional dev dependencies
      if (this.config.nodejs?.devDependencies) {
        packageJson.devDependencies = {
          ...packageJson.devDependencies,
          ...this.config.nodejs.devDependencies
        };
      }

      // Update scripts based on package manager preference
      if (this.config.nodejs?.packageManager && this.config.nodejs.packageManager !== 'npm') {
        const pm = this.config.nodejs.packageManager;
        for (const [key, script] of Object.entries(packageJson.scripts || {})) {
          if (typeof script === 'string' && script.includes('npm ')) {
            packageJson.scripts[key] = script.replace('npm ', `${pm} `);
          }
        }
      }

      await fs.writeFile(packageJsonPath, JSON.stringify(packageJson, null, 2));
    } catch (error) {
      // If package.json doesn't exist or can't be updated, skip
    }
  }

  /**
   * Updates TypeScript configuration
   */
  private async updateTsConfig(outputDir: string): Promise<void> {
    const tsconfigPath = join(outputDir, 'tsconfig.json');
    
    try {
      const tsconfigContent = await fs.readFile(tsconfigPath, 'utf-8');
      const tsconfig = JSON.parse(tsconfigContent);

      // Add strict mode if not already enabled
      if (!tsconfig.compilerOptions) {
        tsconfig.compilerOptions = {};
      }

      tsconfig.compilerOptions.strict = true;
      tsconfig.compilerOptions.noImplicitAny = true;
      tsconfig.compilerOptions.noImplicitReturns = true;

      await fs.writeFile(tsconfigPath, JSON.stringify(tsconfig, null, 2));
    } catch (error) {
      // If tsconfig.json doesn't exist or can't be updated, skip
    }
  }

  /**
   * Updates ESLint configuration
   */
  private async updateEslintConfig(outputDir: string): Promise<void> {
    const eslintPath = join(outputDir, '.eslintrc.json');
    
    try {
      const eslintContent = await fs.readFile(eslintPath, 'utf-8');
      const eslintConfig = JSON.parse(eslintContent);

      // Add additional rules
      if (!eslintConfig.rules) {
        eslintConfig.rules = {};
      }

      eslintConfig.rules['@typescript-eslint/no-unused-vars'] = 'error';
      eslintConfig.rules['@typescript-eslint/explicit-function-return-type'] = 'warn';

      await fs.writeFile(eslintPath, JSON.stringify(eslintConfig, null, 2));
    } catch (error) {
      // If .eslintrc.json doesn't exist or can't be updated, skip
    }
  }

  /**
   * Updates Jest configuration
   */
  private async updateJestConfig(outputDir: string): Promise<void> {
    const jestConfigPath = join(outputDir, 'jest.config.js');
    
    try {
      // For now, just check if the file exists
      await fs.access(jestConfigPath);
      // In a full implementation, you could modify the Jest config here
    } catch (error) {
      // If jest.config.js doesn't exist, skip
    }
  }

  /**
   * Updates environment file with additional variables
   */
  private async updateEnvFile(outputDir: string): Promise<void> {
    const envPath = join(outputDir, '.env.example');
    
    try {
      let envContent = '';
      
      try {
        envContent = await fs.readFile(envPath, 'utf-8');
      } catch {
        // File doesn't exist, start with empty content
      }

      // Add additional environment variables
      const additionalVars: string[] = [];
      for (const [key, value] of Object.entries(this.config.common.environment || {})) {
        if (!envContent.includes(key)) {
          additionalVars.push(`${key}=${value}`);
        }
      }

      if (additionalVars.length > 0) {
        const newContent = envContent + '\n' + additionalVars.join('\n') + '\n';
        await fs.writeFile(envPath, newContent);
      }
    } catch (error) {
      // If .env.example can't be updated, skip
    }
  }

  /**
   * Collects information about generated files
   */
  private async collectGeneratedFiles(outputDir: string): Promise<GenerationResult['files']> {
    const files: GenerationResult['files'] = [];

    try {
      await this.collectFilesRecursive(outputDir, files, outputDir);
    } catch (error) {
      // If we can't read the output directory, return empty array
    }

    return files;
  }

  /**
   * Recursively collects file information
   */
  private async collectFilesRecursive(
    dir: string,
    files: GenerationResult['files'],
    baseDir: string
  ): Promise<void> {
    try {
      const entries = await fs.readdir(dir, { withFileTypes: true });

      for (const entry of entries) {
        const fullPath = join(dir, entry.name);
        const relativePath = fullPath.replace(baseDir + '/', '').replace(baseDir + '\\', '');

        if (entry.isDirectory()) {
          // Skip node_modules and .git directories
          if (entry.name !== 'node_modules' && entry.name !== '.git') {
            await this.collectFilesRecursive(fullPath, files, baseDir);
          }
        } else {
          const stats = await fs.stat(fullPath);
          const fileType = this.categorizeFile(entry.name);

          files.push({
            path: relativePath,
            type: fileType,
            size: stats.size
          });
        }
      }
    } catch (error) {
      // Skip directories we can't read
    }
  }

  /**
   * Categorizes a file based on its name/extension
   */
  private categorizeFile(filename: string): 'source' | 'config' | 'docs' | 'test' {
    if (filename.includes('test') || filename.includes('spec')) {
      return 'test';
    }

    if (filename.endsWith('.md') || filename.endsWith('.txt') || filename.endsWith('.html')) {
      return 'docs';
    }

    if (filename.endsWith('.json') || filename.endsWith('.js') || 
        filename.endsWith('.yaml') || filename.endsWith('.yml') ||
        filename.startsWith('.env') || filename.startsWith('.') ||
        filename.endsWith('.config.js') || filename.endsWith('rc')) {
      return 'config';
    }

    return 'source';
  }

  /**
   * Validates that Node.js generator is available
   */
  static async validate(): Promise<{
    available: boolean;
    version?: string;
    error?: string;
  }> {
    try {
      // Check if Node.js is available
      const nodeVersion = await new Promise<string>((resolve, reject) => {
        const child = spawn('node', ['--version'], { stdio: 'pipe' });
        let output = '';

        child.stdout?.on('data', (data) => {
          output += data.toString();
        });

        child.on('close', (code) => {
          if (code === 0) {
            resolve(output.trim());
          } else {
            reject(new Error('Node.js not found'));
          }
        });

        child.on('error', reject);
      });

      return {
        available: true,
        version: nodeVersion
      };
    } catch (error) {
      return {
        available: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }
}