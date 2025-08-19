/**
 * Generator selection logic for the Unified MCP Generator
 */

import { GeneratorType, ProjectType, UnifiedGeneratorConfig, GeneratorCapabilities } from '../types.js';
import { detectEnvironment, checkGeneratorRequirements } from '../utils/environment.js';

/**
 * Generator capabilities definition
 */
const GENERATOR_CAPABILITIES: Record<GeneratorType, GeneratorCapabilities> = {
  python: {
    projectTypes: ['mcp-server', 'mcp-agent', 'mcp-client'],
    transports: ['stdio', 'web', 'websocket'],
    openApiVersions: ['3.0.x', '3.1.x'],
    features: {
      authentication: ['oauth2', 'api-key', 'bearer', 'basic', 'custom'],
      codeGeneration: ['templates', 'llm-enhancement', 'documentation', 'validation'],
      validation: ['openapi', 'schema', 'runtime'],
      documentation: ['auto-generation', 'llm-enhancement', 'openapi-docs']
    }
  },
  nodejs: {
    projectTypes: ['mcp-server', 'mcp-client'],
    transports: ['stdio', 'web', 'streamable-http'],
    openApiVersions: ['3.0.x', '3.1.x'],
    features: {
      authentication: ['oauth2', 'api-key', 'bearer', 'basic'],
      codeGeneration: ['templates', 'typescript', 'validation'],
      validation: ['openapi', 'schema', 'zod'],
      documentation: ['auto-generation', 'typescript-docs']
    }
  },
  auto: {
    projectTypes: ['mcp-server', 'mcp-agent', 'mcp-client', 'full-stack'],
    transports: ['stdio', 'web', 'streamable-http', 'websocket'],
    openApiVersions: ['3.0.x', '3.1.x'],
    features: {
      authentication: ['oauth2', 'api-key', 'bearer', 'basic', 'custom'],
      codeGeneration: ['templates', 'llm-enhancement', 'documentation', 'validation', 'typescript'],
      validation: ['openapi', 'schema', 'runtime', 'zod'],
      documentation: ['auto-generation', 'llm-enhancement', 'openapi-docs', 'typescript-docs']
    }
  }
};

/**
 * Selects the optimal generator based on configuration and environment
 */
export async function selectGenerator(
  config: UnifiedGeneratorConfig,
  options: {
    interactive?: boolean;
    forceGenerator?: GeneratorType;
  } = {}
): Promise<{
  generator: GeneratorType;
  reasoning: string[];
  warnings: string[];
  fallbacks: GeneratorType[];
}> {
  const reasoning: string[] = [];
  const warnings: string[] = [];
  const fallbacks: GeneratorType[] = [];

  // If force override is provided
  if (options.forceGenerator) {
    reasoning.push(`Generator forced to: ${options.forceGenerator}`);
    return {
      generator: options.forceGenerator,
      reasoning,
      warnings,
      fallbacks: options.forceGenerator === 'auto' ? ['python', 'nodejs'] : []
    };
  }

  // If specific generator is requested in config
  if (config.generator !== 'auto') {
    const isSupported = await validateGeneratorSupport(config.generator, config);
    if (isSupported.supported) {
      reasoning.push(`Using configured generator: ${config.generator}`);
      return {
        generator: config.generator,
        reasoning,
        warnings: isSupported.warnings,
        fallbacks: []
      };
    } else {
      warnings.push(`Requested generator ${config.generator} is not suitable: ${isSupported.reason}`);
      reasoning.push(`Falling back to auto-selection due to: ${isSupported.reason}`);
    }
  }

  // Auto-selection logic
  const environment = await detectEnvironment();
  reasoning.push(`Environment detected: ${environment.platform}`);

  if (environment.nodeVersion) {
    reasoning.push(`Node.js ${environment.nodeVersion} available`);
  }
  if (environment.pythonVersion) {
    reasoning.push(`Python ${environment.pythonVersion} available`);
  }

  // Score generators based on multiple criteria
  const scores = await scoreGenerators(config, environment);
  reasoning.push('Generator scoring completed');

  // Sort by score (highest first)
  const sortedGenerators = Object.entries(scores)
    .filter(([gen]) => gen !== 'auto')
    .sort(([, a], [, b]) => b.total - a.total);

  if (sortedGenerators.length === 0) {
    warnings.push('No suitable generators found');
    return {
      generator: 'python', // Default fallback
      reasoning: [...reasoning, 'Using default Python generator as fallback'],
      warnings,
      fallbacks: ['nodejs']
    };
  }

  const [selectedGenerator, selectedScore] = sortedGenerators[0];
  const secondBest = sortedGenerators[1];

  reasoning.push(`Selected ${selectedGenerator} with score ${selectedScore.total}`);
  reasoning.push(`Score breakdown: ${Object.entries(selectedScore.breakdown).map(([k, v]) => `${k}=${v}`).join(', ')}`);

  if (secondBest) {
    reasoning.push(`Second choice: ${secondBest[0]} with score ${secondBest[1].total}`);
    fallbacks.push(secondBest[0] as GeneratorType);
  }

  return {
    generator: selectedGenerator as GeneratorType,
    reasoning,
    warnings,
    fallbacks
  };
}

/**
 * Scores generators based on various criteria
 */
async function scoreGenerators(config: UnifiedGeneratorConfig, environment: any): Promise<Record<string, {
  total: number;
  breakdown: Record<string, number>;
}>> {
  const scores: Record<string, { total: number; breakdown: Record<string, number> }> = {
    python: { total: 0, breakdown: {} },
    nodejs: { total: 0, breakdown: {} }
  };

  // Environment availability (0-30 points)
  const pythonReqs = await checkGeneratorRequirements('python', environment);
  const nodeReqs = await checkGeneratorRequirements('nodejs', environment);

  scores.python.breakdown.environment = pythonReqs.available ? 30 : 0;
  scores.nodejs.breakdown.environment = nodeReqs.available ? 30 : 0;

  // Project type compatibility (0-25 points)
  const pythonSupportsProject = GENERATOR_CAPABILITIES.python.projectTypes.includes(config.projectType);
  const nodeSupportsProject = GENERATOR_CAPABILITIES.nodejs.projectTypes.includes(config.projectType);

  scores.python.breakdown.projectType = pythonSupportsProject ? 25 : 0;
  scores.nodejs.breakdown.projectType = nodeSupportsProject ? 25 : 0;

  // Special bonuses for specific project types
  if (config.projectType === 'mcp-agent') {
    scores.python.breakdown.projectType += 10; // Python is better for agents
  }

  // Transport compatibility (0-15 points)
  const transport = config.common.transport || 'stdio';
  const pythonSupportsTransport = GENERATOR_CAPABILITIES.python.transports.includes(transport);
  const nodeSupportsTransport = GENERATOR_CAPABILITIES.nodejs.transports.includes(transport);

  scores.python.breakdown.transport = pythonSupportsTransport ? 15 : 0;
  scores.nodejs.breakdown.transport = nodeSupportsTransport ? 15 : 0;

  // Feature requirements (0-20 points)
  let pythonFeatureScore = 0;
  let nodeFeatureScore = 0;

  // Check for advanced features that favor Python
  if (config.python?.enhanceDocstrings || config.python?.generateAgent) {
    pythonFeatureScore += 10;
  }

  // Check for TypeScript preference (favors Node.js)
  if (config.nodejs?.typescript) {
    nodeFeatureScore += 10;
  }

  scores.python.breakdown.features = pythonFeatureScore;
  scores.nodejs.breakdown.features = nodeFeatureScore;

  // Version compatibility (0-10 points)
  if (environment.pythonVersion) {
    const pythonVersion = parseVersion(environment.pythonVersion);
    if (pythonVersion.major >= 3 && pythonVersion.minor >= 11) {
      scores.python.breakdown.version = 10;
    } else if (pythonVersion.major >= 3 && pythonVersion.minor >= 9) {
      scores.python.breakdown.version = 5;
    }
  }

  if (environment.nodeVersion) {
    const nodeVersion = parseVersion(environment.nodeVersion);
    if (nodeVersion.major >= 18) {
      scores.nodejs.breakdown.version = 10;
    } else if (nodeVersion.major >= 16) {
      scores.nodejs.breakdown.version = 5;
    }
  }

  // Calculate totals
  for (const generator of ['python', 'nodejs']) {
    scores[generator].total = Object.values(scores[generator].breakdown).reduce((sum, score) => sum + score, 0);
  }

  return scores;
}

/**
 * Validates if a generator supports the given configuration
 */
async function validateGeneratorSupport(
  generator: GeneratorType,
  config: UnifiedGeneratorConfig
): Promise<{
  supported: boolean;
  reason?: string;
  warnings: string[];
}> {
  const warnings: string[] = [];
  
  if (generator === 'auto') {
    return { supported: true, warnings };
  }

  const capabilities = GENERATOR_CAPABILITIES[generator];

  // Check project type support
  if (!capabilities.projectTypes.includes(config.projectType)) {
    return {
      supported: false,
      reason: `${generator} generator does not support ${config.projectType} projects`,
      warnings
    };
  }

  // Check transport support
  const transport = config.common.transport || 'stdio';
  if (!capabilities.transports.includes(transport)) {
    return {
      supported: false,
      reason: `${generator} generator does not support ${transport} transport`,
      warnings
    };
  }

  // Check environment requirements
  const requirements = await checkGeneratorRequirements(generator);
  if (!requirements.available) {
    return {
      supported: false,
      reason: `Missing requirements: ${requirements.missing.join(', ')}`,
      warnings
    };
  }

  warnings.push(...requirements.warnings);

  return { supported: true, warnings };
}

/**
 * Gets generator capabilities
 */
export function getGeneratorCapabilities(generator: GeneratorType): GeneratorCapabilities {
  return GENERATOR_CAPABILITIES[generator];
}

/**
 * Lists all available generators with their status
 */
export async function listGenerators(): Promise<Array<{
  name: GeneratorType;
  available: boolean;
  capabilities: GeneratorCapabilities;
  requirements: {
    available: boolean;
    missing: string[];
    warnings: string[];
  };
}>> {
  const generators: GeneratorType[] = ['python', 'nodejs'];
  const result = [];

  for (const generator of generators) {
    const requirements = await checkGeneratorRequirements(generator);
    const capabilities = getGeneratorCapabilities(generator);

    result.push({
      name: generator,
      available: requirements.available,
      capabilities,
      requirements
    });
  }

  return result;
}

/**
 * Parses a semantic version string
 */
function parseVersion(version: string): { major: number; minor: number; patch: number } {
  const parts = version.split('.').map(p => parseInt(p.replace(/[^\d]/g, ''), 10) || 0);
  return {
    major: parts[0] || 0,
    minor: parts[1] || 0,
    patch: parts[2] || 0
  };
}