/**
 * Unified MCP Generator - Main Entry Point
 * 
 * This module provides a unified API for generating Model Context Protocol (MCP)
 * servers from OpenAPI specifications using either Python or Node.js generators.
 */

// Core exports
export { UnifiedMCPGenerator } from './core/unified-generator.js';

// Type exports
export type {
  GeneratorType,
  ProjectType,
  TransportType,
  UnifiedGeneratorConfig,
  UnifiedCliOptions,
  CommonConfig,
  PythonGeneratorConfig,
  NodeJSGeneratorConfig,
  ValidationResult,
  GenerationResult,
  GeneratorStatus,
  GeneratorCapabilities,
  EnvironmentInfo,
  McpToolDefinition
} from './types.js';

// Validation exports
export { 
  validateConfiguration, 
  defaultConfig 
} from './validation/schema.js';

export { validateOpenAPISpec } from './validation/openapi.js';

// Generator exports
export { selectGenerator, getGeneratorCapabilities, listGenerators } from './generators/selector.js';
export { PythonGeneratorAdapter } from './generators/python-adapter.js';
export { NodeJSGeneratorAdapter } from './generators/nodejs-adapter.js';

// Utility exports
export { 
  detectEnvironment, 
  checkGeneratorRequirements,
  detectProjectType,
  validateEnvironmentRequirements
} from './utils/environment.js';

// CLI exports
export { InteractiveWizard, QuickSetupWizard } from './cli/interactive.js';
export { setupCommands } from './cli/commands.js';

/**
 * Quick generation function for programmatic use
 */
export async function generateMCPProject(options: {
  /** OpenAPI specification path or URL */
  specPath: string;
  /** Output directory */
  outputDir: string;
  /** Generator configuration */
  config?: Partial<UnifiedGeneratorConfig>;
  /** Progress callback */
  onProgress?: (status: GeneratorStatus) => void;
}): Promise<GenerationResult> {
  const { UnifiedMCPGenerator } = await import('./core/unified-generator.js');
  const { defaultConfig } = await import('./validation/schema.js');

  const fullConfig: UnifiedGeneratorConfig = {
    ...defaultConfig,
    ...options.config,
    common: {
      ...defaultConfig.common,
      ...options.config?.common
    }
  };

  const cliOptions: UnifiedCliOptions = {
    input: options.specPath,
    output: options.outputDir
  };

  const generator = new UnifiedMCPGenerator(fullConfig, cliOptions);
  return await generator.generate(options.onProgress);
}

/**
 * Validation helper function
 */
export async function validateMCPProject(options: {
  /** OpenAPI specification path or URL */
  specPath: string;
  /** Configuration to validate */
  config?: UnifiedGeneratorConfig;
  /** Strict validation mode */
  strict?: boolean;
}): Promise<{
  configValidation: ValidationResult;
  specValidation: ValidationResult;
  overall: {
    valid: boolean;
    errors: number;
    warnings: number;
  };
}> {
  const { UnifiedMCPGenerator } = await import('./core/unified-generator.js');
  const { validateConfiguration, defaultConfig } = await import('./validation/schema.js');
  const { validateOpenAPISpec } = await import('./validation/openapi.js');

  const config = options.config || defaultConfig;
  
  // Validate configuration
  const configValidation = validateConfiguration(config);
  
  // Validate OpenAPI spec
  const specResult = await validateOpenAPISpec(options.specPath, {
    strict: options.strict || false,
    dereference: true
  });

  return {
    configValidation,
    specValidation: specResult.validation,
    overall: {
      valid: configValidation.valid && specResult.validation.valid,
      errors: configValidation.errors.length + specResult.validation.errors.length,
      warnings: configValidation.warnings.length + specResult.validation.warnings.length
    }
  };
}

/**
 * Environment analysis helper
 */
export async function analyzeMCPEnvironment(): Promise<{
  environment: EnvironmentInfo;
  generators: Array<{
    name: GeneratorType;
    available: boolean;
    capabilities: GeneratorCapabilities;
  }>;
  recommendations: {
    generator: GeneratorType;
    reasoning: string[];
    warnings: string[];
  };
}> {
  const { detectEnvironment } = await import('./utils/environment.js');
  const { listGenerators, selectGenerator } = await import('./generators/selector.js');
  const { defaultConfig } = await import('./validation/schema.js');

  const environment = await detectEnvironment();
  const generators = await listGenerators();
  
  // Get recommendation using default config
  const selection = await selectGenerator(defaultConfig, { interactive: false });

  return {
    environment,
    generators: generators.map(g => ({
      name: g.name,
      available: g.available,
      capabilities: g.capabilities
    })),
    recommendations: {
      generator: selection.generator,
      reasoning: selection.reasoning,
      warnings: selection.warnings
    }
  };
}

/**
 * Configuration helper functions
 */
export const configHelpers = {
  /**
   * Creates a minimal configuration for quick starts
   */
  createMinimalConfig(generator: GeneratorType = 'auto', projectType: ProjectType = 'mcp-server'): UnifiedGeneratorConfig {
    return {
      generator,
      projectType,
      common: {
        version: '1.0.0',
        license: 'MIT',
        transport: 'stdio'
      }
    };
  },

  /**
   * Creates a full-featured configuration with all options
   */
  createFullConfig(): UnifiedGeneratorConfig {
    const { defaultConfig } = require('./validation/schema.js');
    return {
      ...defaultConfig,
      python: {
        pythonVersion: '>=3.11',
        enhanceDocstrings: true,
        enhanceDocstringsOpenAPI: true,
        generateAgent: true,
        generateEval: true,
        generateSystemPrompt: true,
        withA2AProxy: false,
        fileHeaders: {
          copyright: 'Copyright 2024',
          license: 'MIT',
          message: 'Generated by Unified MCP Generator'
        }
      },
      nodejs: {
        nodeVersion: '>=18.0.0',
        packageManager: 'npm',
        typescript: true,
        eslint: true,
        prettier: true,
        jest: true
      },
      validation: {
        validateSpec: true,
        validateOutput: true,
        strict: true
      }
    };
  },

  /**
   * Merges multiple configuration objects
   */
  mergeConfigs(...configs: Partial<UnifiedGeneratorConfig>[]): UnifiedGeneratorConfig {
    const { defaultConfig } = require('./validation/schema.js');
    let result = { ...defaultConfig };

    for (const config of configs) {
      result = {
        ...result,
        ...config,
        common: {
          ...result.common,
          ...config.common
        },
        python: {
          ...result.python,
          ...config.python
        },
        nodejs: {
          ...result.nodejs,
          ...config.nodejs
        },
        validation: {
          ...result.validation,
          ...config.validation
        },
        hooks: {
          ...result.hooks,
          ...config.hooks
        }
      };
    }

    return result;
  }
};

/**
 * Template helpers
 */
export const templateHelpers = {
  /**
   * Gets a predefined project template
   */
  async getTemplate(name: string): Promise<UnifiedGeneratorConfig | null> {
    const { UnifiedMCPGenerator } = await import('./core/unified-generator.js');
    const templates = await UnifiedMCPGenerator.listProjectTemplates();
    const template = templates.find(t => t.name === name);
    
    if (!template) {
      return null;
    }

    return UnifiedMCPGenerator.generateSampleConfig(
      template.generator as GeneratorType,
      template.projectType
    );
  },

  /**
   * Lists all available templates
   */
  async listTemplates() {
    const { UnifiedMCPGenerator } = await import('./core/unified-generator.js');
    return await UnifiedMCPGenerator.listProjectTemplates();
  }
};

// Default export for convenience
export default {
  UnifiedMCPGenerator,
  generateMCPProject,
  validateMCPProject,
  analyzeMCPEnvironment,
  configHelpers,
  templateHelpers
};