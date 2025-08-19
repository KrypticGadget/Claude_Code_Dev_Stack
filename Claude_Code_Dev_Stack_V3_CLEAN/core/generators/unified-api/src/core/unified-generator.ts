/**
 * Main Unified MCP Generator implementation
 */

import { promises as fs } from 'fs';
import { join, resolve } from 'path';
import * as yaml from 'yaml';
import { 
  UnifiedGeneratorConfig, 
  UnifiedCliOptions, 
  GenerationResult, 
  ValidationResult,
  GeneratorStatus,
  GeneratorType
} from '../types.js';
import { validateConfiguration, defaultConfig } from '../validation/schema.js';
import { validateOpenAPISpec } from '../validation/openapi.js';
import { selectGenerator } from '../generators/selector.js';
import { PythonGeneratorAdapter } from '../generators/python-adapter.js';
import { NodeJSGeneratorAdapter } from '../generators/nodejs-adapter.js';
import { detectEnvironment } from '../utils/environment.js';

/**
 * Main Unified MCP Generator class
 */
export class UnifiedMCPGenerator {
  private config: UnifiedGeneratorConfig;
  private options: UnifiedCliOptions;

  constructor(config: UnifiedGeneratorConfig, options: UnifiedCliOptions) {
    this.config = config;
    this.options = options;
  }

  /**
   * Creates a new generator instance from CLI options
   */
  static async fromOptions(options: UnifiedCliOptions): Promise<UnifiedMCPGenerator> {
    let config: UnifiedGeneratorConfig;

    // Load configuration from file if specified
    if (options.config) {
      config = await UnifiedMCPGenerator.loadConfigFromFile(options.config);
    } else {
      config = { ...defaultConfig };
    }

    // Override config with CLI options
    if (options.generator) {
      config.generator = options.generator;
    }

    if (options.projectType) {
      config.projectType = options.projectType;
    }

    // Set up common configuration from CLI options
    if (options.verbose) {
      config.validation = { ...config.validation, strict: true };
    }

    return new UnifiedMCPGenerator(config, options);
  }

  /**
   * Loads configuration from a YAML or JSON file
   */
  static async loadConfigFromFile(configPath: string): Promise<UnifiedGeneratorConfig> {
    try {
      const configContent = await fs.readFile(configPath, 'utf-8');
      
      if (configPath.endsWith('.yaml') || configPath.endsWith('.yml')) {
        return yaml.parse(configContent) as UnifiedGeneratorConfig;
      } else if (configPath.endsWith('.json')) {
        return JSON.parse(configContent) as UnifiedGeneratorConfig;
      } else {
        throw new Error('Configuration file must be YAML (.yaml/.yml) or JSON (.json)');
      }
    } catch (error) {
      throw new Error(`Failed to load configuration from ${configPath}: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Saves configuration to a file
   */
  static async saveConfigToFile(config: UnifiedGeneratorConfig, configPath: string): Promise<void> {
    const configContent = configPath.endsWith('.json') 
      ? JSON.stringify(config, null, 2)
      : yaml.stringify(config);

    await fs.writeFile(configPath, configContent, 'utf-8');
  }

  /**
   * Validates the current configuration
   */
  validateConfiguration(): ValidationResult {
    return validateConfiguration(this.config);
  }

  /**
   * Validates the OpenAPI specification
   */
  async validateSpec(): Promise<{
    validation: ValidationResult;
    spec?: any;
  }> {
    const options = {
      strict: this.config.validation?.strict || false,
      dereference: true
    };

    return await validateOpenAPISpec(this.options.input, options);
  }

  /**
   * Selects the optimal generator for the current configuration
   */
  async selectGenerator(): Promise<{
    generator: GeneratorType;
    reasoning: string[];
    warnings: string[];
    fallbacks: GeneratorType[];
  }> {
    return await selectGenerator(this.config, {
      interactive: this.options.interactive,
      forceGenerator: this.options.generator
    });
  }

  /**
   * Generates the MCP project
   */
  async generate(onProgress?: (status: GeneratorStatus) => void): Promise<GenerationResult> {
    const startTime = new Date();

    try {
      // Phase 1: Validation
      onProgress?.({
        phase: 'validation',
        progress: 5,
        operation: 'Validating configuration',
        filesProcessed: 0,
        totalFiles: 0,
        startTime
      });

      const configValidation = this.validateConfiguration();
      if (!configValidation.valid) {
        throw new Error(`Configuration validation failed: ${configValidation.errors.map(e => e.message).join(', ')}`);
      }

      // Phase 2: OpenAPI Validation
      onProgress?.({
        phase: 'validation',
        progress: 10,
        operation: 'Validating OpenAPI specification',
        filesProcessed: 0,
        totalFiles: 0,
        startTime
      });

      const specValidation = await this.validateSpec();
      if (!specValidation.validation.valid) {
        throw new Error(`OpenAPI validation failed: ${specValidation.validation.errors.map(e => e.message).join(', ')}`);
      }

      // Phase 3: Generator Selection
      onProgress?.({
        phase: 'selection',
        progress: 15,
        operation: 'Selecting optimal generator',
        filesProcessed: 0,
        totalFiles: 0,
        startTime
      });

      const selection = await this.selectGenerator();
      const selectedGenerator = selection.generator;

      if (this.options.verbose) {
        console.log('Generator selection reasoning:');
        selection.reasoning.forEach(reason => console.log(`  - ${reason}`));
        if (selection.warnings.length > 0) {
          console.log('Warnings:');
          selection.warnings.forEach(warning => console.log(`  ! ${warning}`));
        }
      }

      // Phase 4: Environment Setup
      onProgress?.({
        phase: 'setup',
        progress: 20,
        operation: 'Setting up generator environment',
        filesProcessed: 0,
        totalFiles: 0,
        startTime
      });

      await this.prepareOutputDirectory();

      // Phase 5: Generation
      onProgress?.({
        phase: 'generation',
        progress: 25,
        operation: `Starting ${selectedGenerator} generator`,
        filesProcessed: 0,
        totalFiles: 0,
        startTime
      });

      const result = await this.executeGenerator(selectedGenerator, onProgress);

      // Phase 6: Post-processing
      if (result.success && this.config.hooks?.postGenerate) {
        onProgress?.({
          phase: 'post-processing',
          progress: 95,
          operation: 'Running post-generation hooks',
          filesProcessed: result.files.length,
          totalFiles: result.files.length,
          startTime
        });

        await this.runHooks(this.config.hooks.postGenerate, this.options.output);
      }

      // Update metadata with selection info
      result.metadata.configUsed = this.config;
      result.metadata.generator = selectedGenerator;

      return result;

    } catch (error) {
      return {
        success: false,
        files: [],
        errors: [{
          message: error instanceof Error ? error.message : 'Unknown generation error',
          code: 'generation_error'
        }],
        warnings: [],
        metadata: {
          generator: this.config.generator,
          projectType: this.config.projectType,
          duration: Date.now() - startTime.getTime(),
          outputDir: this.options.output,
          configUsed: this.config
        }
      };
    }
  }

  /**
   * Prepares the output directory
   */
  private async prepareOutputDirectory(): Promise<void> {
    const outputDir = resolve(this.options.output);

    // Check if directory exists
    try {
      const stats = await fs.stat(outputDir);
      if (stats.isDirectory()) {
        // Check if directory is empty
        const files = await fs.readdir(outputDir);
        if (files.length > 0 && !this.options.force) {
          throw new Error(`Output directory ${outputDir} is not empty. Use --force to overwrite.`);
        }
      }
    } catch (error) {
      if ((error as any).code === 'ENOENT') {
        // Directory doesn't exist, create it
        await fs.mkdir(outputDir, { recursive: true });
      } else {
        throw error;
      }
    }

    // Run pre-generation hooks
    if (this.config.hooks?.preGenerate) {
      await this.runHooks(this.config.hooks.preGenerate, outputDir);
    }
  }

  /**
   * Executes the selected generator
   */
  private async executeGenerator(
    generator: GeneratorType,
    onProgress?: (status: GeneratorStatus) => void
  ): Promise<GenerationResult> {
    const specPath = resolve(this.options.input);
    const outputDir = resolve(this.options.output);

    if (generator === 'auto') {
      // Auto generator should have been resolved by now
      throw new Error('Auto generator type should have been resolved to a specific generator');
    }

    if (generator === 'python') {
      const adapter = new PythonGeneratorAdapter(this.config);
      return await adapter.generate(specPath, outputDir, onProgress);
    } else if (generator === 'nodejs') {
      const adapter = new NodeJSGeneratorAdapter(this.config);
      return await adapter.generate(specPath, outputDir, onProgress);
    } else {
      throw new Error(`Unsupported generator type: ${generator}`);
    }
  }

  /**
   * Runs a list of shell commands as hooks
   */
  private async runHooks(commands: string[], workingDir: string): Promise<void> {
    const { spawn } = await import('child_process');
    const { promisify } = await import('util');

    for (const command of commands) {
      if (this.options.verbose) {
        console.log(`Running hook: ${command}`);
      }

      try {
        await new Promise<void>((resolve, reject) => {
          const child = spawn(command, {
            cwd: workingDir,
            stdio: this.options.verbose ? 'inherit' : 'pipe',
            shell: true
          });

          child.on('close', (code) => {
            if (code === 0) {
              resolve();
            } else {
              reject(new Error(`Hook command failed with code ${code}: ${command}`));
            }
          });

          child.on('error', reject);
        });
      } catch (error) {
        console.warn(`Hook failed: ${command} - ${error instanceof Error ? error.message : 'Unknown error'}`);
        // Continue with other hooks even if one fails
      }
    }
  }

  /**
   * Gets the current configuration
   */
  getConfig(): UnifiedGeneratorConfig {
    return { ...this.config };
  }

  /**
   * Updates the configuration
   */
  updateConfig(newConfig: Partial<UnifiedGeneratorConfig>): void {
    this.config = {
      ...this.config,
      ...newConfig,
      common: {
        ...this.config.common,
        ...newConfig.common
      }
    };
  }

  /**
   * Generates a sample configuration file
   */
  static generateSampleConfig(generator?: GeneratorType, projectType?: string): UnifiedGeneratorConfig {
    const config = { ...defaultConfig };

    if (generator) {
      config.generator = generator;
    }

    if (projectType) {
      config.projectType = projectType as any;
    }

    // Add sample values
    config.common = {
      ...config.common,
      name: 'my-mcp-server',
      description: 'A generated MCP server from OpenAPI specification',
      author: {
        name: 'Your Name',
        email: 'your.email@example.com'
      },
      version: '1.0.0',
      license: 'MIT'
    };

    return config;
  }

  /**
   * Lists available project templates
   */
  static async listProjectTemplates(): Promise<Array<{
    name: string;
    description: string;
    generator: GeneratorType;
    projectType: string;
  }>> {
    return [
      {
        name: 'python-mcp-server',
        description: 'Python-based MCP server with stdio transport',
        generator: 'python',
        projectType: 'mcp-server'
      },
      {
        name: 'python-mcp-agent',
        description: 'Python-based MCP agent with LangGraph integration',
        generator: 'python',
        projectType: 'mcp-agent'
      },
      {
        name: 'nodejs-mcp-server',
        description: 'Node.js/TypeScript MCP server with web transport',
        generator: 'nodejs',
        projectType: 'mcp-server'
      },
      {
        name: 'nodejs-streamable-http',
        description: 'Node.js MCP server with StreamableHTTP transport',
        generator: 'nodejs',
        projectType: 'mcp-server'
      }
    ];
  }

  /**
   * Detects the current environment and provides recommendations
   */
  static async analyzeEnvironment(): Promise<{
    environment: any;
    recommendations: string[];
    warnings: string[];
  }> {
    const environment = await detectEnvironment();
    const recommendations: string[] = [];
    const warnings: string[] = [];

    // Analyze and provide recommendations
    if (!environment.nodeVersion && !environment.pythonVersion) {
      warnings.push('Neither Node.js nor Python detected. Please install at least one runtime.');
      recommendations.push('Install Node.js 18+ or Python 3.11+ to use the generators');
    } else {
      if (environment.nodeVersion) {
        const nodeVersion = parseVersion(environment.nodeVersion);
        if (nodeVersion.major >= 18) {
          recommendations.push('Node.js environment looks good for TypeScript/JavaScript projects');
        } else {
          warnings.push(`Node.js ${environment.nodeVersion} detected. Consider upgrading to 18+`);
        }
      }

      if (environment.pythonVersion) {
        const pythonVersion = parseVersion(environment.pythonVersion);
        if (pythonVersion.major >= 3 && pythonVersion.minor >= 11) {
          recommendations.push('Python environment looks good for Python projects');
        } else {
          warnings.push(`Python ${environment.pythonVersion} detected. Consider upgrading to 3.11+`);
        }
      }
    }

    // Check package managers
    const hasNpm = environment.packageManagers.some(pm => pm.name === 'npm' && pm.available);
    const hasPip = environment.packageManagers.some(pm => pm.name === 'pip' && pm.available);

    if (!hasNpm && environment.nodeVersion) {
      warnings.push('Node.js detected but npm is not available');
    }

    if (!hasPip && environment.pythonVersion) {
      warnings.push('Python detected but pip is not available');
    }

    // Git recommendations
    if (!environment.git?.available) {
      recommendations.push('Install Git for version control features');
    }

    return {
      environment,
      recommendations,
      warnings
    };
  }
}

/**
 * Utility function to parse version strings
 */
function parseVersion(version: string): { major: number; minor: number; patch: number } {
  const parts = version.replace(/^v/, '').split('.').map(p => parseInt(p, 10) || 0);
  return {
    major: parts[0] || 0,
    minor: parts[1] || 0,
    patch: parts[2] || 0
  };
}