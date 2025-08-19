/**
 * Interactive CLI for the Unified MCP Generator
 */

import inquirer from 'inquirer';
import chalk from 'chalk';
import { 
  UnifiedGeneratorConfig, 
  GeneratorType, 
  ProjectType, 
  TransportType,
  UnifiedCliOptions
} from '../types.js';
import { defaultConfig } from '../validation/schema.js';
import { detectEnvironment, checkGeneratorRequirements } from '../utils/environment.js';
import { listGenerators } from '../generators/selector.js';
import { UnifiedMCPGenerator } from '../core/unified-generator.js';

/**
 * Interactive configuration wizard
 */
export class InteractiveWizard {
  private config: UnifiedGeneratorConfig = { ...defaultConfig };

  /**
   * Runs the interactive configuration wizard
   */
  async run(): Promise<UnifiedCliOptions & { config: UnifiedGeneratorConfig }> {
    console.log(chalk.blue.bold('\n🚀 Unified MCP Generator - Interactive Setup\n'));

    // Step 1: Basic project information
    await this.collectBasicInfo();

    // Step 2: Generator selection
    await this.selectGenerator();

    // Step 3: Project type selection
    await this.selectProjectType();

    // Step 4: Transport configuration
    await this.configureTransport();

    // Step 5: Generator-specific configuration
    await this.configureGeneratorSpecific();

    // Step 6: Advanced options
    if (await this.askForAdvancedOptions()) {
      await this.configureAdvancedOptions();
    }

    // Step 7: Summary and confirmation
    await this.showSummary();

    return {
      input: await this.getOpenAPISpecPath(),
      output: await this.getOutputPath(),
      config: this.config
    };
  }

  /**
   * Collects basic project information
   */
  private async collectBasicInfo(): Promise<void> {
    console.log(chalk.yellow('📋 Basic Project Information\n'));

    const answers = await inquirer.prompt([
      {
        type: 'input',
        name: 'name',
        message: 'Project name:',
        default: 'my-mcp-project',
        validate: (input: string) => {
          if (!/^[a-z0-9-_]+$/.test(input)) {
            return 'Project name must contain only lowercase letters, numbers, hyphens, and underscores';
          }
          return true;
        }
      },
      {
        type: 'input',
        name: 'description',
        message: 'Project description:',
        default: 'A generated MCP server from OpenAPI specification'
      },
      {
        type: 'input',
        name: 'version',
        message: 'Initial version:',
        default: '1.0.0',
        validate: (input: string) => {
          if (!/^\d+\.\d+\.\d+/.test(input)) {
            return 'Version must follow semantic versioning (e.g., 1.0.0)';
          }
          return true;
        }
      },
      {
        type: 'input',
        name: 'authorName',
        message: 'Author name:',
        default: 'Your Name'
      },
      {
        type: 'input',
        name: 'authorEmail',
        message: 'Author email:',
        default: 'your.email@example.com',
        validate: (input: string) => {
          if (input && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input)) {
            return 'Please enter a valid email address';
          }
          return true;
        }
      },
      {
        type: 'list',
        name: 'license',
        message: 'License:',
        choices: ['MIT', 'Apache-2.0', 'GPL-3.0', 'BSD-3-Clause', 'ISC', 'Other'],
        default: 'MIT'
      }
    ]);

    this.config.common = {
      ...this.config.common,
      name: answers.name,
      description: answers.description,
      version: answers.version,
      author: {
        name: answers.authorName,
        email: answers.authorEmail
      },
      license: answers.license
    };
  }

  /**
   * Generator selection with environment analysis
   */
  private async selectGenerator(): Promise<void> {
    console.log(chalk.yellow('\n🔧 Generator Selection\n'));

    // Analyze environment
    const environment = await detectEnvironment();
    const generators = await listGenerators();

    console.log(chalk.cyan('Environment Analysis:'));
    if (environment.nodeVersion) {
      console.log(chalk.green(`  ✓ Node.js ${environment.nodeVersion}`));
    } else {
      console.log(chalk.red('  ✗ Node.js not detected'));
    }

    if (environment.pythonVersion) {
      console.log(chalk.green(`  ✓ Python ${environment.pythonVersion}`));
    } else {
      console.log(chalk.red('  ✗ Python not detected'));
    }

    console.log('');

    // Show generator availability
    const generatorChoices = generators.map(gen => {
      const status = gen.available ? '✓' : '✗';
      const color = gen.available ? chalk.green : chalk.red;
      const requirements = gen.available ? '' : ` (${gen.requirements.missing.join(', ')})`;
      
      return {
        name: color(`${status} ${gen.name}${requirements}`),
        value: gen.name,
        disabled: !gen.available
      };
    });

    // Add auto option
    generatorChoices.unshift({
      name: chalk.blue('🤖 auto - Let the system choose the best generator'),
      value: 'auto',
      disabled: false
    });

    const { generator } = await inquirer.prompt([
      {
        type: 'list',
        name: 'generator',
        message: 'Select generator:',
        choices: generatorChoices,
        default: environment.recommendedGenerator
      }
    ]);

    this.config.generator = generator as GeneratorType;

    // Show generator-specific information
    if (generator !== 'auto') {
      const selectedGen = generators.find(g => g.name === generator);
      if (selectedGen) {
        console.log(chalk.cyan(`\nGenerator capabilities:`));
        console.log(`  Project types: ${selectedGen.capabilities.projectTypes.join(', ')}`);
        console.log(`  Transports: ${selectedGen.capabilities.transports.join(', ')}`);
        console.log(`  Features: ${selectedGen.capabilities.features.codeGeneration.join(', ')}`);
      }
    }
  }

  /**
   * Project type selection
   */
  private async selectProjectType(): Promise<void> {
    console.log(chalk.yellow('\n📦 Project Type\n'));

    const projectTypeChoices = [
      {
        name: '🔌 MCP Server - Basic server implementation',
        value: 'mcp-server',
        description: 'Standard MCP server with tools for API integration'
      },
      {
        name: '🤖 MCP Agent - AI agent with MCP tools',
        value: 'mcp-agent',
        description: 'LangGraph-based agent that uses MCP tools (Python only)'
      },
      {
        name: '📱 MCP Client - Client library for MCP servers',
        value: 'mcp-client',
        description: 'Client library to connect to MCP servers'
      },
      {
        name: '🏗️ Full Stack - Complete project with server, client, and examples',
        value: 'full-stack',
        description: 'Complete project setup with multiple components'
      }
    ];

    const { projectType } = await inquirer.prompt([
      {
        type: 'list',
        name: 'projectType',
        message: 'Select project type:',
        choices: projectTypeChoices,
        default: 'mcp-server'
      }
    ]);

    this.config.projectType = projectType as ProjectType;

    // Show additional information based on selection
    if (projectType === 'mcp-agent' && this.config.generator === 'nodejs') {
      console.log(chalk.yellow('\n⚠️  Note: MCP Agent is best supported by the Python generator.'));
      const { confirm } = await inquirer.prompt([
        {
          type: 'confirm',
          name: 'confirm',
          message: 'Continue with Node.js generator?',
          default: false
        }
      ]);

      if (!confirm) {
        this.config.generator = 'python';
        console.log(chalk.green('Switched to Python generator for better agent support.'));
      }
    }
  }

  /**
   * Transport configuration
   */
  private async configureTransport(): Promise<void> {
    console.log(chalk.yellow('\n🚇 Transport Configuration\n'));

    const transportChoices = [
      {
        name: '📡 stdio - Standard input/output (recommended for most use cases)',
        value: 'stdio'
      },
      {
        name: '🌐 web - HTTP web server with browser interface',
        value: 'web'
      },
      {
        name: '📊 streamable-http - HTTP with streaming support',
        value: 'streamable-http'
      },
      {
        name: '🔌 websocket - WebSocket transport (Python only)',
        value: 'websocket'
      }
    ];

    const { transport } = await inquirer.prompt([
      {
        type: 'list',
        name: 'transport',
        message: 'Select transport type:',
        choices: transportChoices,
        default: 'stdio'
      }
    ]);

    this.config.common.transport = transport as TransportType;

    // Configure port for web transports
    if (['web', 'streamable-http', 'websocket'].includes(transport)) {
      const { port } = await inquirer.prompt([
        {
          type: 'number',
          name: 'port',
          message: 'Server port:',
          default: 3000,
          validate: (input: number) => {
            if (input < 1 || input > 65535) {
              return 'Port must be between 1 and 65535';
            }
            return true;
          }
        }
      ]);

      this.config.common.port = port;
    }
  }

  /**
   * Generator-specific configuration
   */
  private async configureGeneratorSpecific(): Promise<void> {
    if (this.config.generator === 'auto') {
      return; // Skip generator-specific config for auto
    }

    console.log(chalk.yellow(`\n⚙️  ${this.config.generator.toUpperCase()} Generator Configuration\n`));

    if (this.config.generator === 'python') {
      await this.configurePythonGenerator();
    } else if (this.config.generator === 'nodejs') {
      await this.configureNodeJSGenerator();
    }
  }

  /**
   * Python generator specific configuration
   */
  private async configurePythonGenerator(): Promise<void> {
    const answers = await inquirer.prompt([
      {
        type: 'confirm',
        name: 'enhanceDocstrings',
        message: 'Enhance docstrings with LLM?',
        default: false
      },
      {
        type: 'confirm',
        name: 'enhanceDocstringsOpenAPI',
        message: 'Include OpenAPI documentation in docstrings?',
        default: false,
        when: (answers) => answers.enhanceDocstrings
      },
      {
        type: 'confirm',
        name: 'generateAgent',
        message: 'Generate agent wrapper?',
        default: this.config.projectType === 'mcp-agent'
      },
      {
        type: 'confirm',
        name: 'generateEval',
        message: 'Generate evaluation code?',
        default: false,
        when: (answers) => answers.generateAgent
      },
      {
        type: 'confirm',
        name: 'generateSystemPrompt',
        message: 'Generate system prompt with LLM?',
        default: false,
        when: (answers) => answers.generateAgent
      },
      {
        type: 'confirm',
        name: 'withA2AProxy',
        message: 'Include A2A (Agent-to-Agent) proxy?',
        default: false,
        when: (answers) => answers.generateAgent
      }
    ]);

    this.config.python = {
      ...this.config.python,
      ...answers
    };
  }

  /**
   * Node.js generator specific configuration
   */
  private async configureNodeJSGenerator(): Promise<void> {
    const answers = await inquirer.prompt([
      {
        type: 'confirm',
        name: 'typescript',
        message: 'Use TypeScript?',
        default: true
      },
      {
        type: 'confirm',
        name: 'eslint',
        message: 'Include ESLint configuration?',
        default: true
      },
      {
        type: 'confirm',
        name: 'prettier',
        message: 'Include Prettier configuration?',
        default: true
      },
      {
        type: 'confirm',
        name: 'jest',
        message: 'Include Jest testing framework?',
        default: true
      },
      {
        type: 'list',
        name: 'packageManager',
        message: 'Package manager:',
        choices: ['npm', 'yarn', 'pnpm'],
        default: 'npm'
      }
    ]);

    this.config.nodejs = {
      ...this.config.nodejs,
      ...answers
    };
  }

  /**
   * Ask if user wants to configure advanced options
   */
  private async askForAdvancedOptions(): Promise<boolean> {
    const { advanced } = await inquirer.prompt([
      {
        type: 'confirm',
        name: 'advanced',
        message: 'Configure advanced options?',
        default: false
      }
    ]);

    return advanced;
  }

  /**
   * Advanced configuration options
   */
  private async configureAdvancedOptions(): Promise<void> {
    console.log(chalk.yellow('\n🔧 Advanced Configuration\n'));

    const answers = await inquirer.prompt([
      {
        type: 'input',
        name: 'baseUrl',
        message: 'API base URL (leave empty to use OpenAPI servers):',
        validate: (input: string) => {
          if (input && !input.startsWith('http')) {
            return 'Base URL must start with http:// or https://';
          }
          return true;
        }
      },
      {
        type: 'confirm',
        name: 'validateSpec',
        message: 'Validate OpenAPI specification?',
        default: true
      },
      {
        type: 'confirm',
        name: 'strict',
        message: 'Enable strict validation mode?',
        default: false,
        when: (answers) => answers.validateSpec
      },
      {
        type: 'input',
        name: 'excludeOperations',
        message: 'Operations to exclude (comma-separated):',
        filter: (input: string) => input ? input.split(',').map(s => s.trim()) : []
      }
    ]);

    if (answers.baseUrl) {
      this.config.common.baseUrl = answers.baseUrl;
    }

    if (answers.excludeOperations && answers.excludeOperations.length > 0) {
      this.config.common.excludeOperations = answers.excludeOperations;
    }

    this.config.validation = {
      ...this.config.validation,
      validateSpec: answers.validateSpec,
      strict: answers.strict
    };
  }

  /**
   * Show configuration summary and get confirmation
   */
  private async showSummary(): Promise<void> {
    console.log(chalk.yellow('\n📋 Configuration Summary\n'));

    console.log(chalk.cyan('Project:'));
    console.log(`  Name: ${this.config.common.name}`);
    console.log(`  Description: ${this.config.common.description}`);
    console.log(`  Version: ${this.config.common.version}`);
    console.log(`  Author: ${this.config.common.author?.name}`);
    console.log(`  License: ${this.config.common.license}`);

    console.log(chalk.cyan('\nGeneration:'));
    console.log(`  Generator: ${this.config.generator}`);
    console.log(`  Project type: ${this.config.projectType}`);
    console.log(`  Transport: ${this.config.common.transport}`);

    if (this.config.common.port) {
      console.log(`  Port: ${this.config.common.port}`);
    }

    if (this.config.python && this.config.generator === 'python') {
      console.log(chalk.cyan('\nPython Options:'));
      Object.entries(this.config.python).forEach(([key, value]) => {
        if (value) {
          console.log(`  ${key}: ${value}`);
        }
      });
    }

    if (this.config.nodejs && this.config.generator === 'nodejs') {
      console.log(chalk.cyan('\nNode.js Options:'));
      Object.entries(this.config.nodejs).forEach(([key, value]) => {
        if (value) {
          console.log(`  ${key}: ${value}`);
        }
      });
    }

    const { confirm } = await inquirer.prompt([
      {
        type: 'confirm',
        name: 'confirm',
        message: 'Proceed with this configuration?',
        default: true
      }
    ]);

    if (!confirm) {
      console.log(chalk.red('Configuration cancelled.'));
      process.exit(0);
    }
  }

  /**
   * Get OpenAPI specification path
   */
  private async getOpenAPISpecPath(): Promise<string> {
    const { specPath } = await inquirer.prompt([
      {
        type: 'input',
        name: 'specPath',
        message: 'OpenAPI specification path or URL:',
        validate: (input: string) => {
          if (!input.trim()) {
            return 'OpenAPI specification path is required';
          }
          return true;
        }
      }
    ]);

    return specPath;
  }

  /**
   * Get output directory path
   */
  private async getOutputPath(): Promise<string> {
    const defaultOutput = `./${this.config.common.name}`;

    const { outputPath } = await inquirer.prompt([
      {
        type: 'input',
        name: 'outputPath',
        message: 'Output directory:',
        default: defaultOutput
      }
    ]);

    return outputPath;
  }
}

/**
 * Quick setup wizard for common scenarios
 */
export class QuickSetupWizard {
  /**
   * Quick setup for common project types
   */
  static async quickSetup(): Promise<UnifiedCliOptions & { config: UnifiedGeneratorConfig }> {
    console.log(chalk.blue.bold('\n⚡ Quick Setup - Unified MCP Generator\n'));

    const templates = await UnifiedMCPGenerator.listProjectTemplates();

    const { template } = await inquirer.prompt([
      {
        type: 'list',
        name: 'template',
        message: 'Choose a project template:',
        choices: templates.map(t => ({
          name: `${t.name} - ${t.description}`,
          value: t
        }))
      }
    ]);

    const { name, specPath, outputPath } = await inquirer.prompt([
      {
        type: 'input',
        name: 'name',
        message: 'Project name:',
        default: 'my-mcp-project'
      },
      {
        type: 'input',
        name: 'specPath',
        message: 'OpenAPI specification path or URL:',
        validate: (input: string) => input.trim() ? true : 'Path is required'
      },
      {
        type: 'input',
        name: 'outputPath',
        message: 'Output directory:',
        default: (answers: any) => `./${answers.name}`
      }
    ]);

    const config = UnifiedMCPGenerator.generateSampleConfig(
      template.generator as GeneratorType,
      template.projectType
    );

    config.common.name = name;

    return {
      input: specPath,
      output: outputPath,
      config
    };
  }
}