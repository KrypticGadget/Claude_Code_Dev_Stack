/**
 * Type definitions for the Unified MCP Generator API
 */

import { OpenAPIV3 } from 'openapi-types';
import { JSONSchema7 } from 'json-schema';

/**
 * Generator types available in the unified API
 */
export type GeneratorType = 'python' | 'nodejs' | 'auto';

/**
 * Transport types supported by MCP servers
 */
export type TransportType = 'stdio' | 'web' | 'streamable-http' | 'websocket';

/**
 * Project types that can be generated
 */
export type ProjectType = 'mcp-server' | 'mcp-agent' | 'mcp-client' | 'full-stack';

/**
 * Configuration for Python generator
 */
export interface PythonGeneratorConfig {
  /** Python version requirement */
  pythonVersion?: string;
  /** Enable docstring enhancement with LLM */
  enhanceDocstrings?: boolean;
  /** Enable OpenAPI documentation in docstrings */
  enhanceDocstringsOpenAPI?: boolean;
  /** Generate agent wrapper */
  generateAgent?: boolean;
  /** Generate evaluation code */
  generateEval?: boolean;
  /** Generate system prompt with LLM */
  generateSystemPrompt?: boolean;
  /** Enable A2A proxy */
  withA2AProxy?: boolean;
  /** Package dependencies */
  dependencies?: string[];
  /** File header configuration */
  fileHeaders?: {
    copyright?: string;
    license?: string;
    message?: string;
  };
}

/**
 * Configuration for Node.js generator
 */
export interface NodeJSGeneratorConfig {
  /** Node.js version requirement */
  nodeVersion?: string;
  /** Package manager to use */
  packageManager?: 'npm' | 'yarn' | 'pnpm';
  /** TypeScript configuration */
  typescript?: boolean;
  /** ESLint configuration */
  eslint?: boolean;
  /** Prettier configuration */
  prettier?: boolean;
  /** Jest testing configuration */
  jest?: boolean;
  /** Additional dependencies */
  dependencies?: Record<string, string>;
  /** Development dependencies */
  devDependencies?: Record<string, string>;
}

/**
 * Common configuration for both generators
 */
export interface CommonConfig {
  /** Project name */
  name?: string;
  /** Project version */
  version?: string;
  /** Project description */
  description?: string;
  /** Author information */
  author?: {
    name: string;
    email?: string;
    url?: string;
  };
  /** License type */
  license?: string;
  /** Base URL for the API */
  baseUrl?: string;
  /** Server port for web transports */
  port?: number;
  /** Transport type */
  transport?: TransportType;
  /** Security schemes to include */
  securitySchemes?: string[];
  /** Operations to exclude */
  excludeOperations?: string[];
  /** Custom headers */
  headers?: Record<string, string>;
  /** Environment variables */
  environment?: Record<string, string>;
  /** Output directory structure */
  outputStructure?: {
    srcDir?: string;
    testsDir?: string;
    docsDir?: string;
    configDir?: string;
  };
}

/**
 * Unified generator configuration
 */
export interface UnifiedGeneratorConfig {
  /** Generator type to use */
  generator: GeneratorType;
  /** Project type to generate */
  projectType: ProjectType;
  /** Common configuration */
  common: CommonConfig;
  /** Python-specific configuration */
  python?: PythonGeneratorConfig;
  /** Node.js-specific configuration */
  nodejs?: NodeJSGeneratorConfig;
  /** Validation options */
  validation?: {
    /** Validate OpenAPI spec before generation */
    validateSpec?: boolean;
    /** Validate generated code */
    validateOutput?: boolean;
    /** Strict mode validation */
    strict?: boolean;
  };
  /** Post-generation hooks */
  hooks?: {
    /** Commands to run before generation */
    preGenerate?: string[];
    /** Commands to run after generation */
    postGenerate?: string[];
    /** Commands to run after dependencies installation */
    postInstall?: string[];
  };
}

/**
 * CLI options for the unified generator
 */
export interface UnifiedCliOptions {
  /** Path to OpenAPI specification */
  input: string;
  /** Output directory */
  output: string;
  /** Generator type */
  generator?: GeneratorType;
  /** Project type */
  projectType?: ProjectType;
  /** Configuration file path */
  config?: string;
  /** Force overwrite existing files */
  force?: boolean;
  /** Dry run mode (don't write files) */
  dryRun?: boolean;
  /** Verbose output */
  verbose?: boolean;
  /** Skip dependency installation */
  skipInstall?: boolean;
  /** Interactive mode */
  interactive?: boolean;
  /** Template directory */
  templateDir?: string;
}

/**
 * Validation result interface
 */
export interface ValidationResult {
  /** Whether validation passed */
  valid: boolean;
  /** Validation errors */
  errors: Array<{
    path: string;
    message: string;
    code?: string;
    severity: 'error' | 'warning' | 'info';
  }>;
  /** Validation warnings */
  warnings: Array<{
    path: string;
    message: string;
    code?: string;
  }>;
}

/**
 * Generation result interface
 */
export interface GenerationResult {
  /** Whether generation was successful */
  success: boolean;
  /** Generated files */
  files: Array<{
    path: string;
    type: 'source' | 'config' | 'docs' | 'test';
    size: number;
  }>;
  /** Generation errors */
  errors: Array<{
    message: string;
    file?: string;
    line?: number;
    code?: string;
  }>;
  /** Generation warnings */
  warnings: Array<{
    message: string;
    file?: string;
    line?: number;
    code?: string;
  }>;
  /** Generation metadata */
  metadata: {
    generator: GeneratorType;
    projectType: ProjectType;
    duration: number;
    outputDir: string;
    configUsed: UnifiedGeneratorConfig;
  };
}

/**
 * Tool definition extracted from OpenAPI
 */
export interface McpToolDefinition {
  /** Tool name */
  name: string;
  /** Tool description */
  description: string;
  /** Input schema */
  inputSchema: JSONSchema7;
  /** HTTP method */
  method: string;
  /** Path template */
  pathTemplate: string;
  /** Parameters */
  parameters: OpenAPIV3.ParameterObject[];
  /** Execution parameters */
  executionParameters: Array<{ name: string; in: string }>;
  /** Request body content type */
  requestBodyContentType?: string;
  /** Security requirements */
  securityRequirements: OpenAPIV3.SecurityRequirementObject[];
  /** Operation ID */
  operationId: string;
  /** Base URL */
  baseUrl?: string;
}

/**
 * Generator status information
 */
export interface GeneratorStatus {
  /** Current phase */
  phase: string;
  /** Progress percentage (0-100) */
  progress: number;
  /** Current operation */
  operation: string;
  /** Files processed */
  filesProcessed: number;
  /** Total files to process */
  totalFiles: number;
  /** Start time */
  startTime: Date;
  /** Estimated completion time */
  estimatedCompletion?: Date;
}

/**
 * Generator capabilities
 */
export interface GeneratorCapabilities {
  /** Supported project types */
  projectTypes: ProjectType[];
  /** Supported transport types */
  transports: TransportType[];
  /** Supported OpenAPI versions */
  openApiVersions: string[];
  /** Supported features */
  features: {
    /** Authentication support */
    authentication: string[];
    /** Code generation features */
    codeGeneration: string[];
    /** Validation features */
    validation: string[];
    /** Documentation features */
    documentation: string[];
  };
}

/**
 * Environment detection result
 */
export interface EnvironmentInfo {
  /** Operating system */
  platform: string;
  /** Node.js version */
  nodeVersion?: string;
  /** Python version */
  pythonVersion?: string;
  /** Available package managers */
  packageManagers: Array<{
    name: string;
    version?: string;
    available: boolean;
  }>;
  /** Git information */
  git?: {
    available: boolean;
    version?: string;
    repository?: string;
    branch?: string;
  };
  /** Recommended generator type */
  recommendedGenerator: GeneratorType;
}

/**
 * Template metadata
 */
export interface TemplateMetadata {
  /** Template name */
  name: string;
  /** Template version */
  version: string;
  /** Description */
  description: string;
  /** Generator type */
  generator: GeneratorType;
  /** Project type */
  projectType: ProjectType;
  /** Required variables */
  requiredVariables: string[];
  /** Optional variables */
  optionalVariables: string[];
  /** Dependencies */
  dependencies: string[];
}