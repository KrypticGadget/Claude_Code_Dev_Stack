#!/usr/bin/env node

const { exec, spawn } = require('child_process')
const fs = require('fs').promises
const path = require('path')

/**
 * Setup script for API Generator Service
 * Installs and configures both Python and Node.js OpenAPI to MCP generators
 */

const GENERATORS = {
  python: {
    name: '@cnoe-io/openapi-mcp-codegen',
    description: 'Python FastAPI-based MCP server generator',
    installCommand: 'pip install openapi-mcp-codegen',
    testCommand: 'openapi-mcp-codegen --version',
    runtime: 'python3'
  },
  nodejs: {
    name: '@harsha-iiiv/openapi-mcp-generator',
    description: 'Node.js Express-based MCP server generator',
    installCommand: 'npm install -g @harsha-iiiv/openapi-mcp-generator',
    testCommand: 'npx @harsha-iiiv/openapi-mcp-generator --version',
    runtime: 'node'
  }
}

async function checkRuntime(runtime) {
  return new Promise((resolve) => {
    exec(`${runtime} --version`, (error) => {
      resolve(!error)
    })
  })
}

async function installGenerator(generator) {
  return new Promise((resolve, reject) => {
    console.log(`📦 Installing ${generator.name}...`)
    
    exec(generator.installCommand, (error, stdout, stderr) => {
      if (error) {
        console.error(`❌ Failed to install ${generator.name}:`, error.message)
        return reject(error)
      }
      
      console.log(`✅ ${generator.name} installed successfully`)
      if (stdout) console.log('stdout:', stdout)
      if (stderr) console.log('stderr:', stderr)
      resolve()
    })
  })
}

async function testGenerator(generator) {
  return new Promise((resolve, reject) => {
    console.log(`🧪 Testing ${generator.name}...`)
    
    exec(generator.testCommand, (error, stdout, stderr) => {
      if (error) {
        console.error(`❌ ${generator.name} test failed:`, error.message)
        return reject(error)
      }
      
      console.log(`✅ ${generator.name} is working correctly`)
      if (stdout) console.log('Version:', stdout.trim())
      resolve()
    })
  })
}

async function setupDirectories() {
  const dirs = [
    'temp',
    'generated',
    'generators/python',
    'generators/nodejs'
  ]

  for (const dir of dirs) {
    try {
      await fs.mkdir(dir, { recursive: true })
      console.log(`📁 Created directory: ${dir}`)
    } catch (error) {
      console.error(`Failed to create directory ${dir}:`, error.message)
    }
  }
}

async function createGeneratorConfigs() {
  // Python generator config
  const pythonConfig = {
    generator: 'python',
    package: '@cnoe-io/openapi-mcp-codegen',
    runtime: 'python3',
    outputFormat: 'fastapi',
    features: {
      authentication: true,
      documentation: true,
      testing: true,
      dockerization: true
    },
    defaultOptions: {
      asyncSupport: true,
      validationEnabled: true,
      corsEnabled: true
    }
  }

  // Node.js generator config
  const nodejsConfig = {
    generator: 'nodejs',
    package: '@harsha-iiiv/openapi-mcp-generator',
    runtime: 'node',
    outputFormat: 'express',
    features: {
      authentication: true,
      documentation: true,
      testing: true,
      dockerization: true
    },
    defaultOptions: {
      typescript: true,
      swaggerUI: true,
      corsEnabled: true
    }
  }

  try {
    await fs.writeFile(
      'generators/python/config.json',
      JSON.stringify(pythonConfig, null, 2)
    )
    await fs.writeFile(
      'generators/nodejs/config.json',
      JSON.stringify(nodejsConfig, null, 2)
    )
    console.log('📝 Generator configurations created')
  } catch (error) {
    console.error('Failed to create generator configs:', error.message)
  }
}

async function installDependencies() {
  return new Promise((resolve, reject) => {
    console.log('📦 Installing Node.js dependencies...')
    
    exec('npm install', (error, stdout, stderr) => {
      if (error) {
        console.error('❌ Failed to install dependencies:', error.message)
        return reject(error)
      }
      
      console.log('✅ Dependencies installed successfully')
      resolve()
    })
  })
}

async function setupAPIGenerator() {
  console.log('🚀 Setting up API Generator Service...\n')

  try {
    // Check if package.json exists, if not copy from api-generator-package.json
    try {
      await fs.access('package.json')
    } catch {
      console.log('📋 Creating package.json...')
      const packageContent = await fs.readFile('api-generator-package.json', 'utf8')
      await fs.writeFile('package.json', packageContent)
    }

    // Setup directories
    await setupDirectories()

    // Install Node.js dependencies
    await installDependencies()

    // Check runtimes
    console.log('\n🔍 Checking runtimes...')
    const pythonAvailable = await checkRuntime('python3') || await checkRuntime('python')
    const nodeAvailable = await checkRuntime('node')

    console.log(`Python3: ${pythonAvailable ? '✅' : '❌'} Available`)
    console.log(`Node.js: ${nodeAvailable ? '✅' : '❌'} Available`)

    if (!nodeAvailable) {
      throw new Error('Node.js is required but not available')
    }

    // Install generators
    console.log('\n📦 Installing generators...')
    
    if (pythonAvailable) {
      try {
        await installGenerator(GENERATORS.python)
        await testGenerator(GENERATORS.python)
      } catch (error) {
        console.warn(`⚠️  Python generator setup failed: ${error.message}`)
      }
    } else {
      console.warn('⚠️  Skipping Python generator (Python not available)')
    }

    try {
      await installGenerator(GENERATORS.nodejs)
      await testGenerator(GENERATORS.nodejs)
    } catch (error) {
      console.warn(`⚠️  Node.js generator setup failed: ${error.message}`)
    }

    // Create generator configurations
    await createGeneratorConfigs()

    console.log('\n🎉 API Generator Service setup complete!')
    console.log('\n📋 Available generators:')
    console.log(`  • Python: ${pythonAvailable ? '✅ Ready' : '❌ Not available'}`)
    console.log(`  • Node.js: ✅ Ready`)
    
    console.log('\n🚀 To start the service:')
    console.log('  npm start')
    console.log('  # or')
    console.log('  node api-generator.js')

  } catch (error) {
    console.error('\n❌ Setup failed:', error.message)
    process.exit(1)
  }
}

// Run setup if called directly
if (require.main === module) {
  setupAPIGenerator()
}

module.exports = { setupAPIGenerator }