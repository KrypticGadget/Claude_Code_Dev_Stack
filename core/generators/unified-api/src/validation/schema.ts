/**
 * Configuration schema validation for the Unified MCP Generator
 */

import Ajv, { JSONSchemaType } from 'ajv';
import { UnifiedGeneratorConfig, ValidationResult } from '../types.js';

const ajv = new Ajv({ allErrors: true, verbose: true });

/**
 * JSON Schema for the unified generator configuration
 */
const configSchema: JSONSchemaType<UnifiedGeneratorConfig> = {
  type: 'object',
  properties: {
    generator: {
      type: 'string',
      enum: ['python', 'nodejs', 'auto']
    },
    projectType: {
      type: 'string',
      enum: ['mcp-server', 'mcp-agent', 'mcp-client', 'full-stack']
    },
    common: {
      type: 'object',
      properties: {
        name: { type: 'string', nullable: true },
        version: { type: 'string', nullable: true },
        description: { type: 'string', nullable: true },
        author: {
          type: 'object',
          properties: {
            name: { type: 'string' },
            email: { type: 'string', nullable: true },
            url: { type: 'string', nullable: true }
          },
          required: ['name'],
          nullable: true
        },
        license: { type: 'string', nullable: true },
        baseUrl: { type: 'string', nullable: true },
        port: { type: 'number', nullable: true },
        transport: {
          type: 'string',
          enum: ['stdio', 'web', 'streamable-http', 'websocket'],
          nullable: true
        },
        securitySchemes: {
          type: 'array',
          items: { type: 'string' },
          nullable: true
        },
        excludeOperations: {
          type: 'array',
          items: { type: 'string' },
          nullable: true
        },
        headers: {
          type: 'object',
          additionalProperties: { type: 'string' },
          nullable: true
        },
        environment: {
          type: 'object',
          additionalProperties: { type: 'string' },
          nullable: true
        },
        outputStructure: {
          type: 'object',
          properties: {
            srcDir: { type: 'string', nullable: true },
            testsDir: { type: 'string', nullable: true },
            docsDir: { type: 'string', nullable: true },
            configDir: { type: 'string', nullable: true }
          },
          nullable: true
        }
      },
      required: []
    },
    python: {
      type: 'object',
      properties: {
        pythonVersion: { type: 'string', nullable: true },
        enhanceDocstrings: { type: 'boolean', nullable: true },
        enhanceDocstringsOpenAPI: { type: 'boolean', nullable: true },
        generateAgent: { type: 'boolean', nullable: true },
        generateEval: { type: 'boolean', nullable: true },
        generateSystemPrompt: { type: 'boolean', nullable: true },
        withA2AProxy: { type: 'boolean', nullable: true },
        dependencies: {
          type: 'array',
          items: { type: 'string' },
          nullable: true
        },
        fileHeaders: {
          type: 'object',
          properties: {
            copyright: { type: 'string', nullable: true },
            license: { type: 'string', nullable: true },
            message: { type: 'string', nullable: true }
          },
          nullable: true
        }
      },
      nullable: true
    },
    nodejs: {
      type: 'object',
      properties: {
        nodeVersion: { type: 'string', nullable: true },
        packageManager: {
          type: 'string',
          enum: ['npm', 'yarn', 'pnpm'],
          nullable: true
        },
        typescript: { type: 'boolean', nullable: true },
        eslint: { type: 'boolean', nullable: true },
        prettier: { type: 'boolean', nullable: true },
        jest: { type: 'boolean', nullable: true },
        dependencies: {
          type: 'object',
          additionalProperties: { type: 'string' },
          nullable: true
        },
        devDependencies: {
          type: 'object',
          additionalProperties: { type: 'string' },
          nullable: true
        }
      },
      nullable: true
    },
    validation: {
      type: 'object',
      properties: {
        validateSpec: { type: 'boolean', nullable: true },
        validateOutput: { type: 'boolean', nullable: true },
        strict: { type: 'boolean', nullable: true }
      },
      nullable: true
    },
    hooks: {
      type: 'object',
      properties: {
        preGenerate: {
          type: 'array',
          items: { type: 'string' },
          nullable: true
        },
        postGenerate: {
          type: 'array',
          items: { type: 'string' },
          nullable: true
        },
        postInstall: {
          type: 'array',
          items: { type: 'string' },
          nullable: true
        }
      },
      nullable: true
    }
  },
  required: ['generator', 'projectType', 'common']
};

const validateConfig = ajv.compile(configSchema);

/**
 * Validates a unified generator configuration
 */
export function validateConfiguration(config: unknown): ValidationResult {
  const isValid = validateConfig(config);
  
  const errors: ValidationResult['errors'] = [];
  const warnings: ValidationResult['warnings'] = [];

  if (!isValid && validateConfig.errors) {
    for (const error of validateConfig.errors) {
      const path = error.instancePath || error.schemaPath || 'root';
      const message = error.message || 'Validation error';
      
      errors.push({
        path,
        message: `${path}: ${message}`,
        code: error.keyword || 'validation_error',
        severity: 'error'
      });
    }
  }

  // Additional custom validations
  if (isValid && config) {
    const typedConfig = config as UnifiedGeneratorConfig;
    
    // Check generator-specific configuration
    if (typedConfig.generator === 'python' && !typedConfig.python) {
      warnings.push({
        path: 'python',
        message: 'Python generator selected but no Python-specific configuration provided',
        code: 'missing_generator_config'
      });
    }
    
    if (typedConfig.generator === 'nodejs' && !typedConfig.nodejs) {
      warnings.push({
        path: 'nodejs',
        message: 'Node.js generator selected but no Node.js-specific configuration provided',
        code: 'missing_generator_config'
      });
    }

    // Check project type compatibility
    if (typedConfig.projectType === 'mcp-agent' && typedConfig.generator === 'nodejs') {
      warnings.push({
        path: 'projectType',
        message: 'MCP Agent generation is primarily supported by Python generator',
        code: 'suboptimal_generator'
      });
    }

    // Check transport compatibility
    if (typedConfig.common.transport === 'websocket' && typedConfig.generator === 'nodejs') {
      warnings.push({
        path: 'common.transport',
        message: 'WebSocket transport has better support in Python generator',
        code: 'transport_compatibility'
      });
    }

    // Validate version strings
    if (typedConfig.python?.pythonVersion) {
      const pythonVersionRegex = /^>=?\d+\.\d+(\.\d+)?/;
      if (!pythonVersionRegex.test(typedConfig.python.pythonVersion)) {
        errors.push({
          path: 'python.pythonVersion',
          message: 'Invalid Python version format. Use format like ">=3.11" or "3.11.0"',
          code: 'invalid_version_format',
          severity: 'error'
        });
      }
    }

    if (typedConfig.nodejs?.nodeVersion) {
      const nodeVersionRegex = /^>=?\d+\.\d+(\.\d+)?/;
      if (!nodeVersionRegex.test(typedConfig.nodejs.nodeVersion)) {
        errors.push({
          path: 'nodejs.nodeVersion',
          message: 'Invalid Node.js version format. Use format like ">=18.0.0" or "18.0.0"',
          code: 'invalid_version_format',
          severity: 'error'
        });
      }
    }

    // Validate port number
    if (typedConfig.common.port !== undefined) {
      if (typedConfig.common.port < 1 || typedConfig.common.port > 65535) {
        errors.push({
          path: 'common.port',
          message: 'Port number must be between 1 and 65535',
          code: 'invalid_port_range',
          severity: 'error'
        });
      }
    }

    // Check for required transport port
    const webTransports = ['web', 'streamable-http', 'websocket'];
    if (typedConfig.common.transport && webTransports.includes(typedConfig.common.transport)) {
      if (!typedConfig.common.port) {
        warnings.push({
          path: 'common.port',
          message: `Port number is recommended for ${typedConfig.common.transport} transport`,
          code: 'missing_port'
        });
      }
    }
  }

  return {
    valid: isValid && errors.length === 0,
    errors,
    warnings
  };
}

/**
 * Default configuration template
 */
export const defaultConfig: UnifiedGeneratorConfig = {
  generator: 'auto',
  projectType: 'mcp-server',
  common: {
    version: '0.1.0',
    license: 'MIT',
    transport: 'stdio',
    outputStructure: {
      srcDir: 'src',
      testsDir: 'tests',
      docsDir: 'docs',
      configDir: 'config'
    }
  },
  python: {
    pythonVersion: '>=3.11',
    enhanceDocstrings: false,
    enhanceDocstringsOpenAPI: false,
    generateAgent: false,
    generateEval: false,
    generateSystemPrompt: false,
    withA2AProxy: false
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
    validateOutput: false,
    strict: false
  }
};