#!/usr/bin/env node

/**
 * API Generator Service Launcher
 * Starts the unified OpenAPI to MCP conversion service
 */

const { spawn } = require('child_process')
const path = require('path')
const fs = require('fs')

const API_GENERATOR_PORT = process.env.API_GENERATOR_PORT || 8082
const API_GENERATOR_SCRIPT = path.join(__dirname, 'api-generator.js')

async function checkSetup() {
  console.log('🔍 Checking API Generator setup...')
  
  // Check if api-generator.js exists
  if (!fs.existsSync(API_GENERATOR_SCRIPT)) {
    console.error('❌ API Generator script not found:', API_GENERATOR_SCRIPT)
    process.exit(1)
  }

  // Check if package.json exists
  const packagePath = path.join(__dirname, 'package.json')
  if (!fs.existsSync(packagePath)) {
    const fallbackPackagePath = path.join(__dirname, 'api-generator-package.json')
    if (fs.existsSync(fallbackPackagePath)) {
      console.log('📋 Copying package.json from template...')
      fs.copyFileSync(fallbackPackagePath, packagePath)
    } else {
      console.error('❌ No package.json found')
      process.exit(1)
    }
  }

  console.log('✅ Setup check complete')
}

async function startAPIGenerator() {
  await checkSetup()
  
  console.log('🚀 Starting API Generator Service...')
  console.log(`📡 Port: ${API_GENERATOR_PORT}`)
  console.log(`📁 Script: ${API_GENERATOR_SCRIPT}`)
  console.log('─'.repeat(50))

  const child = spawn('node', [API_GENERATOR_SCRIPT], {
    stdio: 'inherit',
    env: {
      ...process.env,
      API_GENERATOR_PORT
    }
  })

  child.on('error', (error) => {
    console.error('❌ Failed to start API Generator:', error.message)
    process.exit(1)
  })

  child.on('exit', (code, signal) => {
    if (signal) {
      console.log(`\n🛑 API Generator terminated by signal: ${signal}`)
    } else if (code !== 0) {
      console.log(`\n❌ API Generator exited with code: ${code}`)
    } else {
      console.log('\n✅ API Generator shutdown gracefully')
    }
  })

  // Handle graceful shutdown
  process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down API Generator...')
    child.kill('SIGINT')
  })

  process.on('SIGTERM', () => {
    console.log('\n🛑 Terminating API Generator...')
    child.kill('SIGTERM')
  })
}

// Start if called directly
if (require.main === module) {
  startAPIGenerator().catch((error) => {
    console.error('💥 Startup failed:', error.message)
    process.exit(1)
  })
}

module.exports = { startAPIGenerator }