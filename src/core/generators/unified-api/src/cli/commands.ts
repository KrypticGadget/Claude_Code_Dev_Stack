/**
 * CLI commands for the Unified MCP Generator
 */

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import { promises as fs } from 'fs';
import { join } from 'path';
import { 
  UnifiedCliOptions, 
  GeneratorType, 
  ProjectType,
  GeneratorStatus 
} from '../types.js';
import { UnifiedMCPGenerator } from '../core/unified-generator.js';
import { InteractiveWizard, QuickSetupWizard } from './interactive.js';
import { validateEnvironmentRequirements } from '../utils/environment.js';
import { listGenerators } from '../generators/selector.js';

/**
 * Sets up all CLI commands
 */
export function setupCommands(): Command {
  const program = new Command();

  program
    .name('unified-mcp-generator')
    .description('Unified API for Python and Node.js MCP generators')
    .version('1.0.0');

  // Main generate command
  program
    .command('generate')
    .alias('gen')
    .description('Generate MCP project from OpenAPI specification')
    .requiredOption('-i, --input <path>', 'OpenAPI specification file or URL')
    .requiredOption('-o, --output <dir>', 'Output directory')
    .option('-g, --generator <type>', 'Generator type (python|nodejs|auto)', 'auto')
    .option('-p, --project-type <type>', 'Project type (mcp-server|mcp-agent|mcp-client|full-stack)', 'mcp-server')
    .option('-c, --config <path>', 'Configuration file path')
    .option('-f, --force', 'Force overwrite existing files', false)
    .option('-d, --dry-run', 'Show what would be generated without creating files', false)
    .option('-v, --verbose', 'Verbose output', false)
    .option('--skip-install', 'Skip dependency installation', false)
    .option('--template-dir <path>', 'Custom template directory')
    .action(async (options: UnifiedCliOptions) => {
      await handleGenerateCommand(options);
    });

  // Interactive wizard
  program
    .command('wizard')
    .alias('w')
    .description('Interactive project setup wizard')
    .option('-q, --quick', 'Quick setup with templates', false)
    .action(async (options: { quick?: boolean }) => {
      await handleWizardCommand(options);
    });

  // Initialize command
  program
    .command('init')
    .description('Initialize a new project with configuration file')
    .option('-g, --generator <type>', 'Generator type (python|nodejs|auto)', 'auto')
    .option('-p, --project-type <type>', 'Project type', 'mcp-server')
    .option('-o, --output <path>', 'Configuration file output path', './unified-mcp.config.yaml')
    .action(async (options: { generator?: GeneratorType; projectType?: ProjectType; output: string }) => {
      await handleInitCommand(options);
    });

  // Validate command
  program
    .command('validate')
    .description('Validate OpenAPI specification and configuration')
    .requiredOption('-i, --input <path>', 'OpenAPI specification file or URL')
    .option('-c, --config <path>', 'Configuration file path')
    .option('--strict', 'Strict validation mode', false)
    .action(async (options: { input: string; config?: string; strict: boolean }) => {
      await handleValidateCommand(options);
    });

  // List generators
  program
    .command('list')
    .alias('ls')
    .description('List available generators and their capabilities')
    .action(async () => {
      await handleListCommand();
    });

  // Environment info
  program
    .command('env')
    .description('Show environment information and recommendations')
    .action(async () => {
      await handleEnvCommand();
    });

  // Config commands
  const configCmd = program
    .command('config')
    .description('Configuration management');

  configCmd
    .command('show')
    .description('Show current configuration')
    .option('-c, --config <path>', 'Configuration file path')
    .action(async (options: { config?: string }) => {
      await handleConfigShowCommand(options);
    });

  configCmd
    .command('validate')
    .description('Validate configuration file')
    .requiredOption('-c, --config <path>', 'Configuration file path')
    .action(async (options: { config: string }) => {
      await handleConfigValidateCommand(options);
    });

  configCmd
    .command('sample')
    .description('Generate sample configuration file')
    .option('-g, --generator <type>', 'Generator type', 'auto')
    .option('-p, --project-type <type>', 'Project type', 'mcp-server')
    .option('-o, --output <path>', 'Output file path', './unified-mcp.config.yaml')
    .action(async (options: { generator: GeneratorType; projectType: ProjectType; output: string }) => {
      await handleConfigSampleCommand(options);
    });

  return program;
}

/**
 * Handles the generate command
 */
async function handleGenerateCommand(options: UnifiedCliOptions): Promise<void> {
  const spinner = ora('Initializing generation...').start();

  try {
    // Validate environment
    const envValidation = await validateEnvironmentRequirements();
    if (!envValidation.valid) {
      spinner.fail('Environment validation failed');
      console.error(chalk.red('Environment errors:'));
      envValidation.errors.forEach(error => console.error(chalk.red(`  - ${error}`)));
      process.exit(1);
    }

    if (envValidation.warnings.length > 0) {
      spinner.warn('Environment warnings detected');
      envValidation.warnings.forEach(warning => console.warn(chalk.yellow(`  - ${warning}`)));
    }

    // Create generator instance
    spinner.text = 'Loading configuration...';
    const generator = await UnifiedMCPGenerator.fromOptions(options);

    // Validate configuration
    spinner.text = 'Validating configuration...';
    const configValidation = generator.validateConfiguration();
    if (!configValidation.valid) {
      spinner.fail('Configuration validation failed');
      console.error(chalk.red('Configuration errors:'));
      configValidation.errors.forEach(error => console.error(chalk.red(`  - ${error.message}`)));
      process.exit(1);
    }

    if (configValidation.warnings.length > 0) {
      configValidation.warnings.forEach(warning => console.warn(chalk.yellow(`  - ${warning.message}`)));
    }

    // Validate OpenAPI spec
    spinner.text = 'Validating OpenAPI specification...';
    const specValidation = await generator.validateSpec();
    if (!specValidation.validation.valid) {
      spinner.fail('OpenAPI validation failed');
      console.error(chalk.red('OpenAPI errors:'));
      specValidation.validation.errors.forEach(error => console.error(chalk.red(`  - ${error.message}`)));
      process.exit(1);
    }

    if (specValidation.validation.warnings.length > 0) {
      specValidation.validation.warnings.forEach(warning => console.warn(chalk.yellow(`  - ${warning.message}`)));
    }

    // Show generator selection
    const selection = await generator.selectGenerator();
    spinner.succeed(`Selected generator: ${chalk.blue(selection.generator)}`);
    
    if (options.verbose) {
      console.log(chalk.cyan('Selection reasoning:'));
      selection.reasoning.forEach(reason => console.log(chalk.gray(`  - ${reason}`)));
    }

    // Generate project
    if (options.dryRun) {
      spinner.info('Dry run mode - no files will be created');
      return;
    }

    let currentSpinner = ora('Starting generation...').start();
    
    const result = await generator.generate((status: GeneratorStatus) => {
      const progressBar = '█'.repeat(Math.floor(status.progress / 5)) + '░'.repeat(20 - Math.floor(status.progress / 5));
      currentSpinner.text = `[${progressBar}] ${status.progress}% - ${status.operation}`;
    });

    if (result.success) {
      currentSpinner.succeed(chalk.green('Generation completed successfully!'));
      
      console.log(chalk.cyan('\nGenerated files:'));
      const fileCounts = result.files.reduce((acc, file) => {
        acc[file.type] = (acc[file.type] || 0) + 1;
        return acc;
      }, {} as Record<string, number>);

      Object.entries(fileCounts).forEach(([type, count]) => {
        console.log(chalk.gray(`  ${type}: ${count} files`));
      });

      console.log(chalk.cyan(`\nTotal: ${result.files.length} files generated`));
      console.log(chalk.cyan(`Duration: ${(result.metadata.duration / 1000).toFixed(2)}s`));
      console.log(chalk.cyan(`Output: ${result.metadata.outputDir}`));

      if (result.warnings.length > 0) {
        console.log(chalk.yellow('\nWarnings:'));
        result.warnings.forEach(warning => console.log(chalk.yellow(`  - ${warning.message}`)));
      }

      // Show next steps
      console.log(chalk.green('\n🎉 Next steps:'));
      console.log(chalk.white(`  1. cd ${options.output}`));
      
      if (selection.generator === 'nodejs') {
        console.log(chalk.white('  2. npm install'));
        console.log(chalk.white('  3. npm run build'));
        console.log(chalk.white('  4. npm start'));
      } else if (selection.generator === 'python') {
        console.log(chalk.white('  2. pip install -e .'));
        console.log(chalk.white('  3. python -m your_mcp_server'));
      }

    } else {
      currentSpinner.fail(chalk.red('Generation failed!'));
      
      console.error(chalk.red('\nErrors:'));
      result.errors.forEach(error => console.error(chalk.red(`  - ${error.message}`)));
      
      process.exit(1);
    }

  } catch (error) {
    spinner.fail(chalk.red('Generation failed with error'));
    console.error(chalk.red(error instanceof Error ? error.message : 'Unknown error'));
    process.exit(1);
  }
}

/**
 * Handles the wizard command
 */
async function handleWizardCommand(options: { quick?: boolean }): Promise<void> {
  try {
    const result = options.quick 
      ? await QuickSetupWizard.quickSetup()
      : await new InteractiveWizard().run();

    // Save configuration
    const configPath = join(result.output, 'unified-mcp.config.yaml');
    await UnifiedMCPGenerator.saveConfigToFile(result.config, configPath);

    console.log(chalk.green(`\n✅ Configuration saved to: ${configPath}`));
    console.log(chalk.blue('🚀 Run the following command to generate your project:'));
    console.log(chalk.white(`unified-mcp-generator generate -i "${result.input}" -o "${result.output}" -c "${configPath}"`));

  } catch (error) {
    console.error(chalk.red('Wizard failed:'), error instanceof Error ? error.message : 'Unknown error');
    process.exit(1);
  }
}

/**
 * Handles the init command
 */
async function handleInitCommand(options: { generator?: GeneratorType; projectType?: ProjectType; output: string }): Promise<void> {
  const spinner = ora('Generating configuration...').start();

  try {
    const config = UnifiedMCPGenerator.generateSampleConfig(options.generator, options.projectType);
    await UnifiedMCPGenerator.saveConfigToFile(config, options.output);

    spinner.succeed(chalk.green(`Configuration file created: ${options.output}`));
    console.log(chalk.blue('Edit the configuration file and then run:'));
    console.log(chalk.white(`unified-mcp-generator generate -i <spec-path> -o <output-dir> -c ${options.output}`));

  } catch (error) {
    spinner.fail(chalk.red('Failed to create configuration'));
    console.error(chalk.red(error instanceof Error ? error.message : 'Unknown error'));
    process.exit(1);
  }
}

/**
 * Handles the validate command
 */
async function handleValidateCommand(options: { input: string; config?: string; strict: boolean }): Promise<void> {
  const spinner = ora('Validating...').start();

  try {
    // Create temporary generator for validation
    const cliOptions: UnifiedCliOptions = {
      input: options.input,
      output: './temp',
      config: options.config,
      verbose: options.strict
    };

    const generator = await UnifiedMCPGenerator.fromOptions(cliOptions);

    // Validate configuration
    spinner.text = 'Validating configuration...';
    const configValidation = generator.validateConfiguration();
    
    // Validate OpenAPI spec
    spinner.text = 'Validating OpenAPI specification...';
    const specValidation = await generator.validateSpec();

    const totalErrors = configValidation.errors.length + specValidation.validation.errors.length;
    const totalWarnings = configValidation.warnings.length + specValidation.validation.warnings.length;

    if (totalErrors === 0) {
      spinner.succeed(chalk.green('Validation passed!'));
    } else {
      spinner.fail(chalk.red(`Validation failed with ${totalErrors} error(s)`));
    }

    if (configValidation.errors.length > 0) {
      console.log(chalk.red('\nConfiguration errors:'));
      configValidation.errors.forEach(error => console.log(chalk.red(`  - ${error.message}`)));
    }

    if (specValidation.validation.errors.length > 0) {
      console.log(chalk.red('\nOpenAPI errors:'));
      specValidation.validation.errors.forEach(error => console.log(chalk.red(`  - ${error.message}`)));
    }

    if (totalWarnings > 0) {
      console.log(chalk.yellow(`\nWarnings (${totalWarnings}):`));
      [...configValidation.warnings, ...specValidation.validation.warnings].forEach(warning => {
        console.log(chalk.yellow(`  - ${warning.message}`));
      });
    }

    if (totalErrors > 0) {
      process.exit(1);
    }

  } catch (error) {
    spinner.fail(chalk.red('Validation failed'));
    console.error(chalk.red(error instanceof Error ? error.message : 'Unknown error'));
    process.exit(1);
  }
}

/**
 * Handles the list command
 */
async function handleListCommand(): Promise<void> {
  const spinner = ora('Loading generator information...').start();

  try {
    const generators = await listGenerators();
    
    spinner.succeed('Available generators:');
    
    for (const gen of generators) {
      const status = gen.available ? chalk.green('✓ Available') : chalk.red('✗ Unavailable');
      console.log(chalk.cyan(`\n${gen.name.toUpperCase()}: ${status}`));
      
      if (!gen.available) {
        console.log(chalk.red(`  Missing: ${gen.requirements.missing.join(', ')}`));
      }
      
      console.log(chalk.gray(`  Project types: ${gen.capabilities.projectTypes.join(', ')}`));
      console.log(chalk.gray(`  Transports: ${gen.capabilities.transports.join(', ')}`));
      console.log(chalk.gray(`  Features: ${gen.capabilities.features.codeGeneration.join(', ')}`));
      
      if (gen.requirements.warnings.length > 0) {
        console.log(chalk.yellow(`  Warnings: ${gen.requirements.warnings.join(', ')}`));
      }
    }

    // Show templates
    console.log(chalk.cyan('\nProject templates:'));
    const templates = await UnifiedMCPGenerator.listProjectTemplates();
    templates.forEach(template => {
      console.log(chalk.gray(`  - ${template.name}: ${template.description}`));
    });

  } catch (error) {
    spinner.fail('Failed to load generator information');
    console.error(chalk.red(error instanceof Error ? error.message : 'Unknown error'));
    process.exit(1);
  }
}

/**
 * Handles the env command
 */
async function handleEnvCommand(): Promise<void> {
  const spinner = ora('Analyzing environment...').start();

  try {
    const analysis = await UnifiedMCPGenerator.analyzeEnvironment();
    
    spinner.succeed('Environment analysis complete');
    
    console.log(chalk.cyan('\nEnvironment:'));
    console.log(chalk.gray(`  Platform: ${analysis.environment.platform}`));
    
    if (analysis.environment.nodeVersion) {
      console.log(chalk.green(`  Node.js: ${analysis.environment.nodeVersion}`));
    } else {
      console.log(chalk.red('  Node.js: Not detected'));
    }
    
    if (analysis.environment.pythonVersion) {
      console.log(chalk.green(`  Python: ${analysis.environment.pythonVersion}`));
    } else {
      console.log(chalk.red('  Python: Not detected'));
    }

    console.log(chalk.cyan('\nPackage managers:'));
    analysis.environment.packageManagers.forEach((pm: any) => {
      const status = pm.available ? chalk.green('✓') : chalk.red('✗');
      const version = pm.version ? ` (${pm.version})` : '';
      console.log(chalk.gray(`  ${status} ${pm.name}${version}`));
    });

    if (analysis.environment.git) {
      const gitStatus = analysis.environment.git.available ? chalk.green('✓') : chalk.red('✗');
      console.log(chalk.cyan('\nVersion Control:'));
      console.log(chalk.gray(`  ${gitStatus} Git ${analysis.environment.git.version || ''}`));
      
      if (analysis.environment.git.repository) {
        console.log(chalk.gray(`  Repository: ${analysis.environment.git.repository}`));
        console.log(chalk.gray(`  Branch: ${analysis.environment.git.branch}`));
      }
    }

    console.log(chalk.cyan(`\nRecommended generator: ${chalk.blue(analysis.environment.recommendedGenerator)}`));

    if (analysis.recommendations.length > 0) {
      console.log(chalk.green('\nRecommendations:'));
      analysis.recommendations.forEach(rec => console.log(chalk.green(`  + ${rec}`)));
    }

    if (analysis.warnings.length > 0) {
      console.log(chalk.yellow('\nWarnings:'));
      analysis.warnings.forEach(warning => console.log(chalk.yellow(`  ! ${warning}`)));
    }

  } catch (error) {
    spinner.fail('Environment analysis failed');
    console.error(chalk.red(error instanceof Error ? error.message : 'Unknown error'));
    process.exit(1);
  }
}

/**
 * Handles the config show command
 */
async function handleConfigShowCommand(options: { config?: string }): Promise<void> {
  try {
    if (!options.config) {
      console.error(chalk.red('Configuration file path is required'));
      process.exit(1);
    }

    const config = await UnifiedMCPGenerator.loadConfigFromFile(options.config);
    console.log(chalk.cyan('Configuration:'));
    console.log(JSON.stringify(config, null, 2));

  } catch (error) {
    console.error(chalk.red('Failed to load configuration:'), error instanceof Error ? error.message : 'Unknown error');
    process.exit(1);
  }
}

/**
 * Handles the config validate command
 */
async function handleConfigValidateCommand(options: { config: string }): Promise<void> {
  const spinner = ora('Validating configuration...').start();

  try {
    const config = await UnifiedMCPGenerator.loadConfigFromFile(options.config);
    const validation = await import('../validation/schema.js').then(m => m.validateConfiguration(config));

    if (validation.valid) {
      spinner.succeed(chalk.green('Configuration is valid!'));
    } else {
      spinner.fail(chalk.red(`Configuration validation failed with ${validation.errors.length} error(s)`));
      
      validation.errors.forEach(error => {
        console.error(chalk.red(`  - ${error.message}`));
      });
    }

    if (validation.warnings.length > 0) {
      console.log(chalk.yellow('\nWarnings:'));
      validation.warnings.forEach(warning => {
        console.log(chalk.yellow(`  - ${warning.message}`));
      });
    }

    if (!validation.valid) {
      process.exit(1);
    }

  } catch (error) {
    spinner.fail('Validation failed');
    console.error(chalk.red(error instanceof Error ? error.message : 'Unknown error'));
    process.exit(1);
  }
}

/**
 * Handles the config sample command
 */
async function handleConfigSampleCommand(options: { generator: GeneratorType; projectType: ProjectType; output: string }): Promise<void> {
  const spinner = ora('Generating sample configuration...').start();

  try {
    const config = UnifiedMCPGenerator.generateSampleConfig(options.generator, options.projectType);
    await UnifiedMCPGenerator.saveConfigToFile(config, options.output);

    spinner.succeed(chalk.green(`Sample configuration saved to: ${options.output}`));
    console.log(chalk.blue('Edit the configuration file to customize your project settings.'));

  } catch (error) {
    spinner.fail('Failed to generate sample configuration');
    console.error(chalk.red(error instanceof Error ? error.message : 'Unknown error'));
    process.exit(1);
  }
}