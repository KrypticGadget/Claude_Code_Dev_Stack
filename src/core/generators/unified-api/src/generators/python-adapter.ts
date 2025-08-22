/**
 * Python generator adapter for the Unified MCP Generator
 */

import { spawn } from 'child_process';
import { join, resolve } from 'path';
import { promises as fs } from 'fs';
import { UnifiedGeneratorConfig, GenerationResult, GeneratorStatus } from '../types.js';
import * as yaml from 'yaml';

/**
 * Adapter for the Python MCP generator
 */
export class PythonGeneratorAdapter {
  private config: UnifiedGeneratorConfig;
  private pythonGeneratorPath: string;
  private tempConfigPath?: string;

  constructor(config: UnifiedGeneratorConfig, pythonGeneratorPath?: string) {
    this.config = config;
    this.pythonGeneratorPath = pythonGeneratorPath || this.findPythonGenerator();
  }

  /**
   * Generates MCP project using Python generator
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
      // Create temporary config file for Python generator
      await this.createPythonConfig();

      onProgress?.({
        phase: 'setup',
        progress: 10,
        operation: 'Preparing Python generator',
        filesProcessed: 0,
        totalFiles: 0,
        startTime
      });

      // Build Python generator command
      const command = await this.buildCommand(specPath, outputDir);

      onProgress?.({
        phase: 'generation',
        progress: 20,
        operation: 'Running Python generator',
        filesProcessed: 0,
        totalFiles: 0,
        startTime
      });

      // Execute Python generator
      const result = await this.executePythonGenerator(command, onProgress, startTime);

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

      // Add any errors/warnings from Python generator
      if (result.stderr) {
        const stderrLines = result.stderr.split('\n').filter(line => line.trim());
        for (const line of stderrLines) {
          if (line.toLowerCase().includes('error')) {
            errors.push({
              message: line,
              code: 'python_generator_error'
            });
          } else if (line.toLowerCase().includes('warning')) {
            warnings.push({
              message: line,
              code: 'python_generator_warning'
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
          generator: 'python',
          projectType: this.config.projectType,
          duration: Date.now() - startTime.getTime(),
          outputDir,
          configUsed: this.config
        }
      };

    } catch (error) {
      errors.push({
        message: error instanceof Error ? error.message : 'Unknown error',
        code: 'python_adapter_error'
      });

      return {
        success: false,
        files,
        errors,
        warnings,
        metadata: {
          generator: 'python',
          projectType: this.config.projectType,
          duration: Date.now() - startTime.getTime(),
          outputDir,
          configUsed: this.config
        }
      };
    } finally {
      // Cleanup temporary config file
      if (this.tempConfigPath) {
        try {
          await fs.unlink(this.tempConfigPath);
        } catch {
          // Ignore cleanup errors
        }
      }
    }
  }

  /**
   * Finds the Python generator path
   */
  private findPythonGenerator(): string {
    // Try to find the Python generator relative to this file
    const possiblePaths = [
      join(__dirname, '../../python/openapi_mcp_codegen/__main__.py'),
      join(__dirname, '../../../python/openapi_mcp_codegen/__main__.py'),
      join(process.cwd(), 'core/generators/python/openapi_mcp_codegen/__main__.py'),
      join(process.cwd(), '../python/openapi_mcp_codegen/__main__.py')
    ];

    for (const path of possiblePaths) {
      try {
        const resolvedPath = resolve(path);
        // Note: We can't use fs.existsSync here as it's synchronous
        // In a real implementation, you'd want to check this asynchronously
        return resolvedPath;
      } catch {
        continue;
      }
    }

    throw new Error('Python generator not found. Please specify the path explicitly.');
  }

  /**
   * Creates a temporary configuration file for the Python generator
   */
  private async createPythonConfig(): Promise<void> {
    const pythonConfig = this.convertToPythonConfig();
    const configContent = yaml.stringify(pythonConfig);
    
    this.tempConfigPath = join(process.cwd(), `unified-mcp-config-${Date.now()}.yaml`);
    await fs.writeFile(this.tempConfigPath, configContent, 'utf-8');
  }

  /**
   * Converts unified config to Python generator format
   */
  private convertToPythonConfig(): any {
    const pythonConfig: any = {
      version: this.config.common.version || '0.1.0',
      description: this.config.common.description || 'Generated MCP server',
      author: this.config.common.author?.name || 'Unspecified',
      email: this.config.common.author?.email || 'auto@example.com',
      license: this.config.common.license || 'MIT'
    };

    // Add Python-specific configuration
    if (this.config.python) {
      const pyConfig = this.config.python;
      
      if (pyConfig.pythonVersion) {
        pythonConfig.python_version = pyConfig.pythonVersion;
      }

      if (pyConfig.dependencies) {
        pythonConfig.poetry_dependencies = pyConfig.dependencies.join('\n    ');
      }

      if (pyConfig.fileHeaders) {
        pythonConfig.file_headers = pyConfig.fileHeaders;
      }
    }

    // Add common headers if specified
    if (this.config.common.headers) {
      pythonConfig.headers = this.config.common.headers;
    }

    // Add base package if needed
    pythonConfig.mcp_server_base_package = 'mcp';

    return pythonConfig;
  }

  /**
   * Builds the command to execute the Python generator
   */
  private async buildCommand(specPath: string, outputDir: string): Promise<string[]> {
    const command = ['python', this.pythonGeneratorPath];
    
    // Add basic arguments
    command.push('--spec-path', specPath);
    command.push('--output-dir', outputDir);
    command.push('--config-path', this.tempConfigPath!);

    // Add Python-specific flags
    if (this.config.python) {
      const pyConfig = this.config.python;

      if (pyConfig.enhanceDocstrings) {
        command.push('--enhance-docstring-with-llm');
      }

      if (pyConfig.enhanceDocstringsOpenAPI) {
        command.push('--enhance-docstring-with-llm-openapi');
      }

      if (pyConfig.generateAgent) {
        command.push('--generate-agent');
      }

      if (pyConfig.generateEval) {
        command.push('--generate-eval');
      }

      if (pyConfig.generateSystemPrompt) {
        command.push('--generate-system-prompt');
      }

      if (pyConfig.withA2AProxy) {
        command.push('--with-a2a-proxy');
      }
    }

    return command;
  }

  /**
   * Executes the Python generator
   */
  private async executePythonGenerator(
    command: string[],
    onProgress?: (status: GeneratorStatus) => void,
    startTime?: Date
  ): Promise<{ stdout: string; stderr: string }> {
    return new Promise((resolve, reject) => {
      const [pythonCmd, ...args] = command;
      const child = spawn(pythonCmd, args, {
        stdio: ['pipe', 'pipe', 'pipe'],
        shell: process.platform === 'win32'
      });

      let stdout = '';
      let stderr = '';

      child.stdout?.on('data', (data) => {
        const output = data.toString();
        stdout += output;

        // Parse progress information from Python generator output
        if (onProgress && startTime) {
          const lines = output.split('\n');
          for (const line of lines) {
            if (line.includes('Generating') || line.includes('Processing')) {
              onProgress({
                phase: 'generation',
                progress: Math.min(90, 20 + Math.random() * 60), // Estimate progress
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
          reject(new Error(`Python generator failed with code ${code}: ${stderr}`));
        }
      });

      child.on('error', (error) => {
        reject(new Error(`Failed to start Python generator: ${error.message}`));
      });
    });
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
      // The error will be handled elsewhere
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
          await this.collectFilesRecursive(fullPath, files, baseDir);
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

    if (filename.endsWith('.md') || filename.endsWith('.rst') || filename.endsWith('.txt')) {
      return 'docs';
    }

    if (filename.endsWith('.toml') || filename.endsWith('.json') || 
        filename.endsWith('.yaml') || filename.endsWith('.yml') ||
        filename.startsWith('.env') || filename.endsWith('.ini')) {
      return 'config';
    }

    return 'source';
  }

  /**
   * Validates that Python generator is available
   */
  static async validate(): Promise<{
    available: boolean;
    version?: string;
    error?: string;
  }> {
    try {
      // Check if Python is available
      const pythonVersion = await new Promise<string>((resolve, reject) => {
        const child = spawn('python', ['--version'], { stdio: 'pipe' });
        let output = '';

        child.stdout?.on('data', (data) => {
          output += data.toString();
        });

        child.stderr?.on('data', (data) => {
          output += data.toString();
        });

        child.on('close', (code) => {
          if (code === 0) {
            resolve(output.trim());
          } else {
            reject(new Error('Python not found'));
          }
        });

        child.on('error', reject);
      });

      return {
        available: true,
        version: pythonVersion
      };
    } catch (error) {
      return {
        available: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }
}