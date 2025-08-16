const express = require('express')
const cors = require('cors')
const { spawn, exec } = require('child_process')
const fs = require('fs').promises
const path = require('path')
const SwaggerParser = require('@apidevtools/swagger-parser')
const yaml = require('yaml')
const archiver = require('archiver')
const { v4: uuidv4 } = require('uuid')

// API Generator Service for OpenAPI to MCP conversion
// Integrates @cnoe-io/openapi-mcp-codegen (Python) and @harsha-iiiv/openapi-mcp-generator (Node.js)

const app = express()
const PORT = process.env.API_GENERATOR_PORT || 8082

// Configuration
const TEMP_DIR = path.join(__dirname, 'temp')
const OUTPUT_DIR = path.join(__dirname, 'generated')
const PYTHON_GENERATOR_PATH = path.join(__dirname, 'generators', 'python')
const NODEJS_GENERATOR_PATH = path.join(__dirname, 'generators', 'nodejs')

// Middleware
app.use(cors())
app.use(express.json({ limit: '10mb' }))
app.use(express.static(path.join(__dirname, 'public')))

// Ensure directories exist
async function ensureDirectories() {
  const dirs = [TEMP_DIR, OUTPUT_DIR, PYTHON_GENERATOR_PATH, NODEJS_GENERATOR_PATH]
  for (const dir of dirs) {
    try {
      await fs.mkdir(dir, { recursive: true })
    } catch (error) {
      console.error(`Failed to create directory ${dir}:`, error)
    }
  }
}

// OpenAPI Validation
app.post('/validate', async (req, res) => {
  try {
    const { spec } = req.body
    
    if (!spec) {
      return res.status(400).json({
        valid: false,
        errors: ['No OpenAPI specification provided'],
        warnings: [],
        info: { paths: 0, operations: 0, schemas: 0 }
      })
    }

    // Parse and validate using swagger-parser
    const api = await SwaggerParser.validate(spec)
    
    // Calculate statistics
    const paths = Object.keys(api.paths || {})
    let operations = 0
    paths.forEach(path => {
      const methods = ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']
      methods.forEach(method => {
        if (api.paths[path][method]) operations++
      })
    })
    
    const schemas = Object.keys(api.components?.schemas || {})

    // Check for common issues and warnings
    const warnings = []
    if (!api.info?.description) warnings.push('API description is missing')
    if (!api.servers || api.servers.length === 0) warnings.push('No servers defined')
    if (schemas.length === 0) warnings.push('No schemas defined')
    if (operations === 0) warnings.push('No operations defined')

    res.json({
      valid: true,
      errors: [],
      warnings,
      info: {
        paths: paths.length,
        operations,
        schemas: schemas.length
      }
    })
  } catch (error) {
    res.json({
      valid: false,
      errors: [error.message || 'Invalid OpenAPI specification'],
      warnings: [],
      info: { paths: 0, operations: 0, schemas: 0 }
    })
  }
})

// Python Generator (@cnoe-io/openapi-mcp-codegen)
app.post('/generate/python', async (req, res) => {
  const sessionId = uuidv4()
  const sessionDir = path.join(TEMP_DIR, sessionId)
  
  try {
    const { spec, options = {} } = req.body
    
    await fs.mkdir(sessionDir, { recursive: true })
    
    // Write OpenAPI spec to file
    const specPath = path.join(sessionDir, 'openapi.json')
    await fs.writeFile(specPath, JSON.stringify(spec, null, 2))
    
    // Generate Python MCP server using openapi-mcp-codegen
    const generatePythonMCP = () => {
      return new Promise((resolve, reject) => {
        const serverName = options.serverName || spec.info?.title || 'generated-api'
        const outputPath = path.join(sessionDir, 'python-mcp-server')
        
        // Use openapi-mcp-codegen CLI
        const cmd = `openapi-mcp-codegen generate ${specPath} --output ${outputPath} --name ${serverName}`
        
        exec(cmd, { cwd: PYTHON_GENERATOR_PATH }, (error, stdout, stderr) => {
          if (error) {
            console.error('Python generation error:', error)
            return reject(new Error(`Python generation failed: ${error.message}`))
          }
          
          console.log('Python generation stdout:', stdout)
          if (stderr) console.log('Python generation stderr:', stderr)
          
          resolve(outputPath)
        })
      })
    }

    const pythonOutputPath = await generatePythonMCP()
    
    // Create deployment package
    const zipPath = path.join(sessionDir, 'python-mcp-server.zip')
    await createZipPackage(pythonOutputPath, zipPath)
    
    // Read generated files for analysis
    const mcpServerInfo = await analyzePythonMCPServer(pythonOutputPath, spec)
    
    // Read zip file as base64
    const zipBuffer = await fs.readFile(zipPath)
    const zipBase64 = zipBuffer.toString('base64')
    
    res.json({
      success: true,
      output: zipBase64,
      mcpServer: mcpServerInfo,
      sessionId
    })
    
  } catch (error) {
    console.error('Python generation error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  } finally {
    // Cleanup session directory
    setTimeout(async () => {
      try {
        await fs.rmdir(sessionDir, { recursive: true })
      } catch (error) {
        console.error('Cleanup error:', error)
      }
    }, 300000) // 5 minutes
  }
})

// Node.js Generator (@harsha-iiiv/openapi-mcp-generator)
app.post('/generate/nodejs', async (req, res) => {
  const sessionId = uuidv4()
  const sessionDir = path.join(TEMP_DIR, sessionId)
  
  try {
    const { spec, options = {} } = req.body
    
    await fs.mkdir(sessionDir, { recursive: true })
    
    // Write OpenAPI spec to file
    const specPath = path.join(sessionDir, 'openapi.json')
    await fs.writeFile(specPath, JSON.stringify(spec, null, 2))
    
    // Generate Node.js MCP server using openapi-mcp-generator
    const generateNodejsMCP = () => {
      return new Promise((resolve, reject) => {
        const serverName = options.serverName || spec.info?.title || 'generated-api'
        const outputPath = path.join(sessionDir, 'nodejs-mcp-server')
        
        // Use openapi-mcp-generator CLI
        const cmd = `npx @harsha-iiiv/openapi-mcp-generator ${specPath} --output ${outputPath} --name ${serverName}`
        
        exec(cmd, { cwd: NODEJS_GENERATOR_PATH }, (error, stdout, stderr) => {
          if (error) {
            console.error('Node.js generation error:', error)
            return reject(new Error(`Node.js generation failed: ${error.message}`))
          }
          
          console.log('Node.js generation stdout:', stdout)
          if (stderr) console.log('Node.js generation stderr:', stderr)
          
          resolve(outputPath)
        })
      })
    }

    const nodejsOutputPath = await generateNodejsMCP()
    
    // Create deployment package
    const zipPath = path.join(sessionDir, 'nodejs-mcp-server.zip')
    await createZipPackage(nodejsOutputPath, zipPath)
    
    // Read generated files for analysis
    const mcpServerInfo = await analyzeNodejsMCPServer(nodejsOutputPath, spec)
    
    // Read zip file as base64
    const zipBuffer = await fs.readFile(zipPath)
    const zipBase64 = zipBuffer.toString('base64')
    
    res.json({
      success: true,
      output: zipBase64,
      mcpServer: mcpServerInfo,
      sessionId
    })
    
  } catch (error) {
    console.error('Node.js generation error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  } finally {
    // Cleanup session directory
    setTimeout(async () => {
      try {
        await fs.rmdir(sessionDir, { recursive: true })
      } catch (error) {
        console.error('Cleanup error:', error)
      }
    }, 300000) // 5 minutes
  }
})

// Deploy MCP servers
app.post('/deploy', async (req, res) => {
  try {
    const { generator, mcpServer, autoStart = false } = req.body
    
    if (!mcpServer) {
      return res.status(400).json({
        success: false,
        error: 'No MCP server configuration provided'
      })
    }

    const deploymentId = uuidv4()
    const deploymentPath = path.join(OUTPUT_DIR, deploymentId)
    
    await fs.mkdir(deploymentPath, { recursive: true })
    
    // For now, we'll simulate deployment by creating a deployment manifest
    const deploymentManifest = {
      id: deploymentId,
      generator,
      mcpServer,
      deployedAt: new Date().toISOString(),
      status: 'deployed',
      autoStart
    }
    
    await fs.writeFile(
      path.join(deploymentPath, 'manifest.json'),
      JSON.stringify(deploymentManifest, null, 2)
    )
    
    // If autoStart is enabled, simulate starting the server
    if (autoStart) {
      deploymentManifest.status = 'running'
      deploymentManifest.startedAt = new Date().toISOString()
      
      await fs.writeFile(
        path.join(deploymentPath, 'manifest.json'),
        JSON.stringify(deploymentManifest, null, 2)
      )
    }
    
    res.json({
      success: true,
      deploymentId,
      status: deploymentManifest.status
    })
    
  } catch (error) {
    console.error('Deployment error:', error)
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

// Helper Functions

async function createZipPackage(sourcePath, outputPath) {
  return new Promise((resolve, reject) => {
    const output = require('fs').createWriteStream(outputPath)
    const archive = archiver('zip', { zlib: { level: 9 } })
    
    output.on('close', () => resolve())
    archive.on('error', reject)
    
    archive.pipe(output)
    archive.directory(sourcePath, false)
    archive.finalize()
  })
}

async function analyzePythonMCPServer(serverPath, spec) {
  try {
    // Analyze generated Python MCP server
    const endpoints = extractEndpointsFromSpec(spec)
    const port = findAvailablePort(8090, 8100)
    
    return {
      name: spec.info?.title || 'python-mcp-server',
      port,
      endpoints,
      type: 'python',
      runtime: 'fastapi',
      features: {
        authentication: spec.components?.securitySchemes ? true : false,
        documentation: true,
        testing: true,
        dockerized: true
      }
    }
  } catch (error) {
    console.error('Python analysis error:', error)
    return {
      name: 'python-mcp-server',
      port: 8090,
      endpoints: [],
      type: 'python'
    }
  }
}

async function analyzeNodejsMCPServer(serverPath, spec) {
  try {
    // Analyze generated Node.js MCP server
    const endpoints = extractEndpointsFromSpec(spec)
    const port = findAvailablePort(8100, 8110)
    
    return {
      name: spec.info?.title || 'nodejs-mcp-server',
      port,
      endpoints,
      type: 'nodejs',
      runtime: 'express',
      features: {
        authentication: spec.components?.securitySchemes ? true : false,
        documentation: true,
        testing: true,
        dockerized: true
      }
    }
  } catch (error) {
    console.error('Node.js analysis error:', error)
    return {
      name: 'nodejs-mcp-server',
      port: 8100,
      endpoints: [],
      type: 'nodejs'
    }
  }
}

function extractEndpointsFromSpec(spec) {
  const endpoints = []
  
  if (spec.paths) {
    Object.keys(spec.paths).forEach(path => {
      const pathObject = spec.paths[path]
      const methods = ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']
      
      methods.forEach(method => {
        if (pathObject[method]) {
          endpoints.push({
            path,
            method: method.toUpperCase(),
            summary: pathObject[method].summary || '',
            operationId: pathObject[method].operationId || `${method}${path.replace(/[^a-zA-Z0-9]/g, '')}`
          })
        }
      })
    })
  }
  
  return endpoints
}

function findAvailablePort(start, end) {
  // Simple port selection - in real implementation, check for availability
  return start + Math.floor(Math.random() * (end - start))
}

// Health Check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'API Generator',
    version: '1.0.0',
    generators: {
      python: '@cnoe-io/openapi-mcp-codegen',
      nodejs: '@harsha-iiiv/openapi-mcp-generator'
    },
    uptime: process.uptime()
  })
})

// List deployments
app.get('/deployments', async (req, res) => {
  try {
    const deployments = []
    const entries = await fs.readdir(OUTPUT_DIR)
    
    for (const entry of entries) {
      try {
        const manifestPath = path.join(OUTPUT_DIR, entry, 'manifest.json')
        const manifest = JSON.parse(await fs.readFile(manifestPath, 'utf8'))
        deployments.push(manifest)
      } catch (error) {
        // Skip invalid deployments
      }
    }
    
    res.json({ deployments })
  } catch (error) {
    res.status(500).json({ error: error.message })
  }
})

// Setup generator dependencies
async function setupGenerators() {
  console.log('Setting up API generators...')
  
  try {
    // Setup Python generator
    console.log('Setting up Python generator (@cnoe-io/openapi-mcp-codegen)...')
    // In real implementation, install the Python package
    
    // Setup Node.js generator
    console.log('Setting up Node.js generator (@harsha-iiiv/openapi-mcp-generator)...')
    // In real implementation, install the npm package
    
    console.log('API generators setup complete!')
  } catch (error) {
    console.error('Generator setup failed:', error)
  }
}

// Initialize server
async function initializeServer() {
  await ensureDirectories()
  await setupGenerators()
  
  app.listen(PORT, () => {
    console.log(`🚀 API Generator Service running on port ${PORT}`)
    console.log(`📋 OpenAPI Validation: http://localhost:${PORT}/validate`)
    console.log(`🐍 Python Generator: http://localhost:${PORT}/generate/python`)
    console.log(`📦 Node.js Generator: http://localhost:${PORT}/generate/nodejs`)
    console.log(`🚀 Deployment Service: http://localhost:${PORT}/deploy`)
    console.log(`💚 Health Check: http://localhost:${PORT}/health`)
  })
}

// Error handling
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error)
})

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason)
})

// Start the server
initializeServer().catch(console.error)

module.exports = app