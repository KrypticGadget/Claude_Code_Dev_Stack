#!/usr/bin/env node

/**
 * API Generator Service Test Script
 * Tests validation, generation, and deployment functionality
 */

const fetch = require('node-fetch').default || require('node-fetch')
const fs = require('fs').promises

const API_BASE = 'http://localhost:8082'

// Sample OpenAPI specification for testing
const sampleOpenAPISpec = {
  openapi: '3.0.0',
  info: {
    title: 'Test API',
    description: 'A simple test API for demonstrating MCP generation',
    version: '1.0.0'
  },
  servers: [
    {
      url: 'https://api.example.com/v1',
      description: 'Production server'
    }
  ],
  paths: {
    '/users': {
      get: {
        summary: 'List users',
        description: 'Retrieve a list of users',
        responses: {
          '200': {
            description: 'Successful response',
            content: {
              'application/json': {
                schema: {
                  type: 'array',
                  items: {
                    $ref: '#/components/schemas/User'
                  }
                }
              }
            }
          }
        }
      },
      post: {
        summary: 'Create user',
        description: 'Create a new user',
        requestBody: {
          required: true,
          content: {
            'application/json': {
              schema: {
                $ref: '#/components/schemas/CreateUser'
              }
            }
          }
        },
        responses: {
          '201': {
            description: 'User created',
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/User'
                }
              }
            }
          }
        }
      }
    },
    '/users/{id}': {
      get: {
        summary: 'Get user by ID',
        parameters: [
          {
            name: 'id',
            in: 'path',
            required: true,
            schema: {
              type: 'string'
            }
          }
        ],
        responses: {
          '200': {
            description: 'User found',
            content: {
              'application/json': {
                schema: {
                  $ref: '#/components/schemas/User'
                }
              }
            }
          },
          '404': {
            description: 'User not found'
          }
        }
      }
    }
  },
  components: {
    schemas: {
      User: {
        type: 'object',
        properties: {
          id: {
            type: 'string',
            description: 'Unique user identifier'
          },
          name: {
            type: 'string',
            description: 'User full name'
          },
          email: {
            type: 'string',
            format: 'email',
            description: 'User email address'
          },
          createdAt: {
            type: 'string',
            format: 'date-time',
            description: 'User creation timestamp'
          }
        },
        required: ['id', 'name', 'email']
      },
      CreateUser: {
        type: 'object',
        properties: {
          name: {
            type: 'string',
            description: 'User full name'
          },
          email: {
            type: 'string',
            format: 'email',
            description: 'User email address'
          }
        },
        required: ['name', 'email']
      }
    }
  }
}

async function checkServiceHealth() {
  console.log('🏥 Checking API Generator service health...')
  
  try {
    const response = await fetch(`${API_BASE}/health`)
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`)
    }
    
    const health = await response.json()
    console.log('✅ Service is healthy')
    console.log(`   Version: ${health.version}`)
    console.log(`   Uptime: ${Math.floor(health.uptime)}s`)
    console.log(`   Generators: ${Object.keys(health.generators).join(', ')}`)
    return true
  } catch (error) {
    console.error('❌ Service health check failed:', error.message)
    return false
  }
}

async function testValidation() {
  console.log('\n🔍 Testing OpenAPI validation...')
  
  try {
    const response = await fetch(`${API_BASE}/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ spec: sampleOpenAPISpec })
    })
    
    if (!response.ok) {
      throw new Error(`Validation request failed: ${response.status}`)
    }
    
    const result = await response.json()
    
    if (result.valid) {
      console.log('✅ OpenAPI specification is valid')
      console.log(`   Paths: ${result.info.paths}`)
      console.log(`   Operations: ${result.info.operations}`)
      console.log(`   Schemas: ${result.info.schemas}`)
      
      if (result.warnings.length > 0) {
        console.log(`   Warnings: ${result.warnings.length}`)
        result.warnings.forEach(warning => console.log(`     - ${warning}`))
      }
    } else {
      console.log('❌ OpenAPI specification is invalid')
      result.errors.forEach(error => console.log(`   Error: ${error}`))
    }
    
    return result.valid
  } catch (error) {
    console.error('❌ Validation test failed:', error.message)
    return false
  }
}

async function testGeneration(generator) {
  console.log(`\n🔄 Testing ${generator} generator...`)
  
  try {
    const response = await fetch(`${API_BASE}/generate/${generator}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        spec: sampleOpenAPISpec,
        options: {
          serverName: 'test-api',
          generateTests: true,
          includeDocumentation: true
        }
      })
    })
    
    if (!response.ok) {
      throw new Error(`Generation request failed: ${response.status}`)
    }
    
    const result = await response.json()
    
    if (result.success) {
      console.log(`✅ ${generator} generation successful`)
      console.log(`   Server: ${result.mcpServer.name}`)
      console.log(`   Port: ${result.mcpServer.port}`)
      console.log(`   Endpoints: ${result.mcpServer.endpoints.length}`)
      console.log(`   Package size: ${(result.output.length / 1024 / 1024 * 0.75).toFixed(2)} MB`)
      return result
    } else {
      console.log(`❌ ${generator} generation failed: ${result.error}`)
      return null
    }
  } catch (error) {
    console.error(`❌ ${generator} generation test failed:`, error.message)
    return null
  }
}

async function testDeployment(generationResult) {
  if (!generationResult) {
    console.log('⏭️  Skipping deployment test (no generation result)')
    return false
  }
  
  console.log(`\n🚀 Testing deployment for ${generationResult.mcpServer.name}...`)
  
  try {
    const response = await fetch(`${API_BASE}/deploy`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        generator: generationResult.mcpServer.type,
        mcpServer: generationResult.mcpServer,
        autoStart: true
      })
    })
    
    if (!response.ok) {
      throw new Error(`Deployment request failed: ${response.status}`)
    }
    
    const result = await response.json()
    
    if (result.success) {
      console.log('✅ Deployment successful')
      console.log(`   Deployment ID: ${result.deploymentId}`)
      console.log(`   Status: ${result.status}`)
      return true
    } else {
      console.log(`❌ Deployment failed: ${result.error}`)
      return false
    }
  } catch (error) {
    console.error('❌ Deployment test failed:', error.message)
    return false
  }
}

async function testListDeployments() {
  console.log('\n📋 Testing deployment listing...')
  
  try {
    const response = await fetch(`${API_BASE}/deployments`)
    
    if (!response.ok) {
      throw new Error(`Deployments request failed: ${response.status}`)
    }
    
    const result = await response.json()
    
    console.log(`✅ Found ${result.deployments.length} deployments`)
    result.deployments.forEach((deployment, index) => {
      console.log(`   ${index + 1}. ${deployment.mcpServer.name} (${deployment.generator})`)
      console.log(`      Status: ${deployment.status}`)
      console.log(`      Deployed: ${new Date(deployment.deployedAt).toLocaleString()}`)
    })
    
    return true
  } catch (error) {
    console.error('❌ Deployment listing test failed:', error.message)
    return false
  }
}

async function runTests() {
  console.log('🧪 API Generator Service Test Suite')
  console.log('=' .repeat(50))
  
  const results = {}
  
  // Health check
  results.health = await checkServiceHealth()
  if (!results.health) {
    console.log('\n💥 Service is not running. Start it first:')
    console.log('   node start-api-generator.js')
    process.exit(1)
  }
  
  // Validation test
  results.validation = await testValidation()
  
  // Generation tests
  const pythonResult = await testGeneration('python')
  const nodejsResult = await testGeneration('nodejs')
  
  results.pythonGeneration = pythonResult !== null
  results.nodejsGeneration = nodejsResult !== null
  
  // Deployment tests
  if (pythonResult) {
    results.pythonDeployment = await testDeployment(pythonResult)
  }
  
  if (nodejsResult) {
    results.nodejsDeployment = await testDeployment(nodejsResult)
  }
  
  // List deployments
  results.listDeployments = await testListDeployments()
  
  // Summary
  console.log('\n📊 Test Results Summary')
  console.log('=' .repeat(30))
  
  const passed = Object.values(results).filter(Boolean).length
  const total = Object.keys(results).length
  
  Object.entries(results).forEach(([test, passed]) => {
    const status = passed ? '✅' : '❌'
    const name = test.replace(/([A-Z])/g, ' $1').toLowerCase()
    console.log(`${status} ${name}`)
  })
  
  console.log(`\n🎯 ${passed}/${total} tests passed`)
  
  if (passed === total) {
    console.log('🎉 All tests passed! API Generator is working correctly.')
  } else {
    console.log('⚠️  Some tests failed. Check the output above for details.')
  }
  
  return passed === total
}

// Handle command line arguments
const args = process.argv.slice(2)
if (args.includes('--help') || args.includes('-h')) {
  console.log('API Generator Test Script')
  console.log('')
  console.log('Usage: node test-api-generator.js')
  console.log('')
  console.log('Tests the API Generator service by:')
  console.log('  - Checking service health')
  console.log('  - Validating OpenAPI specification')
  console.log('  - Testing Python and Node.js generators')
  console.log('  - Testing deployment functionality')
  console.log('')
  console.log('Make sure the API Generator service is running first:')
  console.log('  node start-api-generator.js')
  process.exit(0)
}

// Run tests
if (require.main === module) {
  runTests().then(success => {
    process.exit(success ? 0 : 1)
  }).catch(error => {
    console.error('💥 Test suite failed:', error.message)
    process.exit(1)
  })
}

module.exports = { runTests, sampleOpenAPISpec }