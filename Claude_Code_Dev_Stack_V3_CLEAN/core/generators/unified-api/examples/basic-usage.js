#!/usr/bin/env node
/**
 * Basic usage examples for the Unified MCP Generator
 */

import { 
  generateMCPProject, 
  validateMCPProject,
  analyzeMCPEnvironment,
  configHelpers
} from '@claude-code/unified-mcp-generator';

async function basicExample() {
  console.log('🚀 Basic MCP Generation Example\n');
  
  try {
    // Simple generation with auto-selection
    const result = await generateMCPProject({
      specPath: 'https://petstore.swagger.io/v2/swagger.json',
      outputDir: './petstore-mcp',
      config: {
        generator: 'auto',
        projectType: 'mcp-server',
        common: {
          name: 'petstore-mcp',
          description: 'Petstore MCP Server',
          transport: 'stdio'
        }
      },
      onProgress: (status) => {
        console.log(`[${status.progress}%] ${status.operation}`);
      }
    });

    if (result.success) {
      console.log('\n✅ Generation completed successfully!');
      console.log(`📁 Generated ${result.files.length} files`);
      console.log(`⏱️  Duration: ${result.metadata.duration}ms`);
      console.log(`🔧 Used generator: ${result.metadata.generator}`);
    } else {
      console.error('\n❌ Generation failed:');
      result.errors.forEach(error => {
        console.error(`  - ${error.message}`);
      });
    }

  } catch (error) {
    console.error('Fatal error:', error.message);
  }
}

async function validationExample() {
  console.log('\n🔍 Validation Example\n');

  try {
    const validation = await validateMCPProject({
      specPath: 'https://petstore.swagger.io/v2/swagger.json',
      config: configHelpers.createMinimalConfig('python', 'mcp-server'),
      strict: true
    });

    console.log(`Overall validation: ${validation.overall.valid ? '✅ PASS' : '❌ FAIL'}`);
    console.log(`Errors: ${validation.overall.errors}`);
    console.log(`Warnings: ${validation.overall.warnings}`);

    if (validation.configValidation.errors.length > 0) {
      console.log('\nConfiguration errors:');
      validation.configValidation.errors.forEach(error => {
        console.log(`  - ${error.message}`);
      });
    }

    if (validation.specValidation.errors.length > 0) {
      console.log('\nOpenAPI errors:');
      validation.specValidation.errors.forEach(error => {
        console.log(`  - ${error.message}`);
      });
    }

  } catch (error) {
    console.error('Validation error:', error.message);
  }
}

async function environmentExample() {
  console.log('\n🌍 Environment Analysis Example\n');

  try {
    const analysis = await analyzeMCPEnvironment();

    console.log('Environment:');
    console.log(`  Platform: ${analysis.environment.platform}`);
    console.log(`  Node.js: ${analysis.environment.nodeVersion || 'Not detected'}`);
    console.log(`  Python: ${analysis.environment.pythonVersion || 'Not detected'}`);

    console.log('\nAvailable generators:');
    analysis.generators.forEach(gen => {
      const status = gen.available ? '✅' : '❌';
      console.log(`  ${status} ${gen.name}`);
    });

    console.log(`\nRecommended generator: ${analysis.recommendations.generator}`);
    console.log('Reasoning:');
    analysis.recommendations.reasoning.forEach(reason => {
      console.log(`  - ${reason}`);
    });

    if (analysis.recommendations.warnings.length > 0) {
      console.log('\nWarnings:');
      analysis.recommendations.warnings.forEach(warning => {
        console.log(`  ! ${warning}`);
      });
    }

  } catch (error) {
    console.error('Environment analysis error:', error.message);
  }
}

async function advancedConfigExample() {
  console.log('\n⚙️ Advanced Configuration Example\n');

  // Create a complex configuration
  const config = configHelpers.mergeConfigs(
    configHelpers.createMinimalConfig('python', 'mcp-agent'),
    {
      common: {
        name: 'advanced-mcp-agent',
        description: 'Advanced MCP Agent with all features',
        transport: 'web',
        port: 8080,
        author: {
          name: 'Developer',
          email: 'dev@example.com'
        }
      },
      python: {
        enhanceDocstrings: true,
        enhanceDocstringsOpenAPI: true,
        generateAgent: true,
        generateEval: true,
        generateSystemPrompt: true,
        fileHeaders: {
          copyright: 'Copyright 2024',
          license: 'MIT'
        }
      },
      validation: {
        validateSpec: true,
        strict: true
      },
      hooks: {
        postGenerate: [
          'pip install -e .',
          'python -m pytest tests/ -v'
        ]
      }
    }
  );

  console.log('Generated configuration:');
  console.log(JSON.stringify(config, null, 2));
}

// Run examples
async function runExamples() {
  console.log('🎯 Unified MCP Generator Examples\n');
  
  // Comment out examples you don't want to run
  await basicExample();
  await validationExample();
  await environmentExample();
  await advancedConfigExample();
  
  console.log('\n🎉 Examples completed!');
}

// Run if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  runExamples().catch(console.error);
}

export {
  basicExample,
  validationExample,
  environmentExample,
  advancedConfigExample
};