import React, { useState, useCallback } from 'react'
import { Code, Upload, Download, Settings, Play, CheckCircle, XCircle, AlertTriangle, Loader2, FileText, Server, Zap } from 'lucide-react'

interface OpenAPISpec {
  name: string
  content: string
  version: string
  servers: Array<{ url: string; description?: string }>
  info: {
    title: string
    description?: string
    version: string
  }
}

interface GenerationResult {
  generator: 'python' | 'nodejs'
  success: boolean
  output?: string
  error?: string
  timestamp: Date
  mcpServer?: {
    name: string
    port: number
    endpoints: string[]
  }
}

interface ValidationResult {
  valid: boolean
  errors: string[]
  warnings: string[]
  info: {
    paths: number
    operations: number
    schemas: number
  }
}

const API_GENERATOR_BASE = process.env.NEXT_PUBLIC_API_GENERATOR_URL || 'http://localhost:8082'

export const APIGenerator: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'upload' | 'generate' | 'deploy'>('upload')
  const [openApiSpec, setOpenApiSpec] = useState<OpenAPISpec | null>(null)
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null)
  const [selectedGenerator, setSelectedGenerator] = useState<'python' | 'nodejs' | 'both'>('both')
  const [generationResults, setGenerationResults] = useState<GenerationResult[]>([])
  const [isValidating, setIsValidating] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [isDeploying, setIsDeploying] = useState(false)
  const [deploymentStatus, setDeploymentStatus] = useState<string>('')

  // File upload handler
  const handleFileUpload = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    try {
      const content = await file.text()
      const spec = JSON.parse(content)
      
      const openApiSpec: OpenAPISpec = {
        name: file.name.replace('.json', ''),
        content,
        version: spec.openapi || spec.swagger || '3.0.0',
        servers: spec.servers || [],
        info: spec.info || { title: 'API', version: '1.0.0' }
      }

      setOpenApiSpec(openApiSpec)
      validateOpenApiSpec(openApiSpec)
    } catch (error) {
      console.error('Failed to parse OpenAPI spec:', error)
      alert('Invalid OpenAPI specification file')
    }
  }, [])

  // Manual spec input handler
  const handleSpecInput = useCallback((content: string) => {
    try {
      const spec = JSON.parse(content)
      
      const openApiSpec: OpenAPISpec = {
        name: spec.info?.title || 'API',
        content,
        version: spec.openapi || spec.swagger || '3.0.0',
        servers: spec.servers || [],
        info: spec.info || { title: 'API', version: '1.0.0' }
      }

      setOpenApiSpec(openApiSpec)
      validateOpenApiSpec(openApiSpec)
    } catch (error) {
      console.error('Failed to parse OpenAPI spec:', error)
    }
  }, [])

  // OpenAPI validation
  const validateOpenApiSpec = async (spec: OpenAPISpec) => {
    setIsValidating(true)
    try {
      const response = await fetch(`${API_GENERATOR_BASE}/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ spec: JSON.parse(spec.content) })
      })

      if (!response.ok) throw new Error('Validation failed')

      const result = await response.json()
      setValidationResult(result)
    } catch (error) {
      setValidationResult({
        valid: false,
        errors: [error instanceof Error ? error.message : 'Validation failed'],
        warnings: [],
        info: { paths: 0, operations: 0, schemas: 0 }
      })
    } finally {
      setIsValidating(false)
    }
  }

  // Generate MCP servers
  const generateMCPServers = async () => {
    if (!openApiSpec || !validationResult?.valid) return

    setIsGenerating(true)
    setGenerationResults([])

    const generators = selectedGenerator === 'both' ? ['python', 'nodejs'] : [selectedGenerator]

    try {
      const results = await Promise.allSettled(
        generators.map(async (generator) => {
          const response = await fetch(`${API_GENERATOR_BASE}/generate/${generator}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              spec: JSON.parse(openApiSpec.content),
              options: {
                serverName: openApiSpec.name,
                generateTests: true,
                includeDocumentation: true
              }
            })
          })

          if (!response.ok) throw new Error(`${generator} generation failed`)

          const result = await response.json()
          return {
            generator: generator as 'python' | 'nodejs',
            success: true,
            output: result.output,
            timestamp: new Date(),
            mcpServer: result.mcpServer
          }
        })
      )

      const processedResults = results.map((result, index) => {
        if (result.status === 'fulfilled') {
          return result.value
        } else {
          return {
            generator: generators[index] as 'python' | 'nodejs',
            success: false,
            error: result.reason.message,
            timestamp: new Date()
          }
        }
      })

      setGenerationResults(processedResults)
    } catch (error) {
      console.error('Generation failed:', error)
    } finally {
      setIsGenerating(false)
    }
  }

  // Deploy MCP servers
  const deployMCPServers = async () => {
    const successfulResults = generationResults.filter(r => r.success && r.mcpServer)
    if (successfulResults.length === 0) return

    setIsDeploying(true)
    setDeploymentStatus('Preparing deployment...')

    try {
      for (const result of successfulResults) {
        setDeploymentStatus(`Deploying ${result.generator} MCP server...`)
        
        const response = await fetch(`${API_GENERATOR_BASE}/deploy`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            generator: result.generator,
            mcpServer: result.mcpServer,
            autoStart: true
          })
        })

        if (!response.ok) throw new Error(`Failed to deploy ${result.generator} server`)
      }

      setDeploymentStatus('All MCP servers deployed successfully!')
      setTimeout(() => setDeploymentStatus(''), 3000)
    } catch (error) {
      setDeploymentStatus(`Deployment failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
      setTimeout(() => setDeploymentStatus(''), 5000)
    } finally {
      setIsDeploying(false)
    }
  }

  // Download generated code
  const downloadGeneratedCode = (result: GenerationResult) => {
    if (!result.output) return

    const blob = new Blob([result.output], { type: 'application/zip' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${openApiSpec?.name}-${result.generator}-mcp-server.zip`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="api-generator">
      {/* Header */}
      <div className="card" style={{ gridColumn: '1 / -1' }}>
        <div className="card-header">
          <h2 className="card-title">
            <Code size={20} />
            API Generator - OpenAPI to MCP
          </h2>
          <div className="flex items-center gap-2">
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
              @cnoe-io/openapi-mcp-codegen
            </span>
            <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
              @harsha-iiiv/openapi-mcp-generator
            </span>
          </div>
        </div>
        <div className="card-content">
          <p>Convert OpenAPI specifications to Model Context Protocol (MCP) servers with Python and Node.js generators</p>
          
          {/* Tab Navigation */}
          <div className="mt-4 border-b">
            <nav className="flex space-x-8">
              {[
                { id: 'upload' as const, label: 'Upload & Validate', icon: Upload },
                { id: 'generate' as const, label: 'Generate MCP', icon: Zap },
                { id: 'deploy' as const, label: 'Deploy Servers', icon: Server }
              ].map(({ id, label, icon: Icon }) => (
                <button
                  key={id}
                  onClick={() => setActiveTab(id)}
                  className={`flex items-center gap-2 py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <Icon size={16} />
                  {label}
                </button>
              ))}
            </nav>
          </div>
        </div>
      </div>

      {/* Upload & Validate Tab */}
      {activeTab === 'upload' && (
        <>
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">
                <Upload size={18} />
                Upload OpenAPI Specification
              </h3>
            </div>
            <div className="card-content">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Upload JSON File</label>
                  <input
                    type="file"
                    accept=".json,.yaml,.yml"
                    onChange={handleFileUpload}
                    className="w-full"
                  />
                </div>
                
                <div className="text-center text-gray-500">— OR —</div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">Paste OpenAPI JSON</label>
                  <textarea
                    rows={10}
                    className="w-full font-mono text-sm"
                    placeholder="Paste your OpenAPI 3.x JSON specification here..."
                    onChange={(e) => handleSpecInput(e.target.value)}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Validation Results */}
          {openApiSpec && (
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">
                  <FileText size={18} />
                  Specification Details
                </h3>
              </div>
              <div className="card-content">
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium">Name</label>
                      <p className="text-sm text-gray-600">{openApiSpec.name}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium">Version</label>
                      <p className="text-sm text-gray-600">{openApiSpec.info.version}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium">OpenAPI Version</label>
                      <p className="text-sm text-gray-600">{openApiSpec.version}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium">Servers</label>
                      <p className="text-sm text-gray-600">{openApiSpec.servers.length} defined</p>
                    </div>
                  </div>
                  
                  {openApiSpec.info.description && (
                    <div>
                      <label className="text-sm font-medium">Description</label>
                      <p className="text-sm text-gray-600">{openApiSpec.info.description}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Validation Status */}
          {isValidating && (
            <div className="card">
              <div className="card-content">
                <div className="flex items-center justify-center py-4">
                  <Loader2 size={20} className="animate-spin text-blue-500 mr-2" />
                  <span>Validating OpenAPI specification...</span>
                </div>
              </div>
            </div>
          )}

          {validationResult && (
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">
                  {validationResult.valid ? (
                    <CheckCircle size={18} className="text-green-500" />
                  ) : (
                    <XCircle size={18} className="text-red-500" />
                  )}
                  Validation Results
                </h3>
              </div>
              <div className="card-content">
                <div className="space-y-4">
                  {/* Status */}
                  <div className={`p-3 rounded ${
                    validationResult.valid 
                      ? 'bg-green-50 border border-green-200 text-green-700'
                      : 'bg-red-50 border border-red-200 text-red-700'
                  }`}>
                    <div className="flex items-center">
                      {validationResult.valid ? (
                        <CheckCircle size={16} className="mr-2" />
                      ) : (
                        <XCircle size={16} className="mr-2" />
                      )}
                      <span className="font-medium">
                        {validationResult.valid ? 'Valid OpenAPI Specification' : 'Invalid OpenAPI Specification'}
                      </span>
                    </div>
                  </div>

                  {/* Statistics */}
                  <div className="grid grid-cols-3 gap-4">
                    <div className="metric">
                      <div className="metric-value text-blue-500">{validationResult.info.paths}</div>
                      <div className="metric-label">Paths</div>
                    </div>
                    <div className="metric">
                      <div className="metric-value text-green-500">{validationResult.info.operations}</div>
                      <div className="metric-label">Operations</div>
                    </div>
                    <div className="metric">
                      <div className="metric-value text-purple-500">{validationResult.info.schemas}</div>
                      <div className="metric-label">Schemas</div>
                    </div>
                  </div>

                  {/* Errors */}
                  {validationResult.errors.length > 0 && (
                    <div>
                      <h4 className="font-medium text-red-700 mb-2">Errors:</h4>
                      <ul className="space-y-1">
                        {validationResult.errors.map((error, index) => (
                          <li key={index} className="text-sm text-red-600 flex items-start">
                            <XCircle size={14} className="mr-2 mt-0.5 flex-shrink-0" />
                            {error}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Warnings */}
                  {validationResult.warnings.length > 0 && (
                    <div>
                      <h4 className="font-medium text-yellow-700 mb-2">Warnings:</h4>
                      <ul className="space-y-1">
                        {validationResult.warnings.map((warning, index) => (
                          <li key={index} className="text-sm text-yellow-600 flex items-start">
                            <AlertTriangle size={14} className="mr-2 mt-0.5 flex-shrink-0" />
                            {warning}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {/* Generate Tab */}
      {activeTab === 'generate' && (
        <>
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">
                <Settings size={18} />
                Generator Configuration
              </h3>
            </div>
            <div className="card-content">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Select Generator</label>
                  <div className="space-y-2">
                    {[
                      { value: 'python', label: 'Python (@cnoe-io/openapi-mcp-codegen)', description: 'FastAPI-based MCP server with Python' },
                      { value: 'nodejs', label: 'Node.js (@harsha-iiiv/openapi-mcp-generator)', description: 'Express-based MCP server with TypeScript' },
                      { value: 'both', label: 'Both Generators', description: 'Generate both Python and Node.js implementations' }
                    ].map((option) => (
                      <label key={option.value} className="flex items-start space-x-3 cursor-pointer">
                        <input
                          type="radio"
                          name="generator"
                          value={option.value}
                          checked={selectedGenerator === option.value}
                          onChange={(e) => setSelectedGenerator(e.target.value as 'python' | 'nodejs' | 'both')}
                          className="mt-1"
                        />
                        <div>
                          <div className="font-medium">{option.label}</div>
                          <div className="text-sm text-gray-600">{option.description}</div>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t">
                  <div>
                    <p className="text-sm text-gray-600">
                      {openApiSpec ? `Ready to generate MCP server for "${openApiSpec.name}"` : 'No OpenAPI specification loaded'}
                    </p>
                    {validationResult && !validationResult.valid && (
                      <p className="text-sm text-red-600 mt-1">
                        Please fix validation errors before generating
                      </p>
                    )}
                  </div>
                  <button
                    onClick={generateMCPServers}
                    disabled={!openApiSpec || !validationResult?.valid || isGenerating}
                    className="btn btn-primary"
                  >
                    {isGenerating ? (
                      <>
                        <Loader2 size={16} className="animate-spin mr-2" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Play size={16} className="mr-2" />
                        Generate MCP Servers
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Generation Results */}
          {generationResults.length > 0 && (
            <div className="card" style={{ gridColumn: '1 / -1' }}>
              <div className="card-header">
                <h3 className="card-title">
                  <Code size={18} />
                  Generation Results
                </h3>
              </div>
              <div className="card-content">
                <div className="space-y-4">
                  {generationResults.map((result, index) => (
                    <div key={index} className={`p-4 border rounded ${
                      result.success ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
                    }`}>
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center">
                          {result.success ? (
                            <CheckCircle size={20} className="text-green-500 mr-2" />
                          ) : (
                            <XCircle size={20} className="text-red-500 mr-2" />
                          )}
                          <div>
                            <h4 className="font-medium capitalize">{result.generator} Generator</h4>
                            <p className="text-sm text-gray-600">
                              {result.timestamp.toLocaleString()}
                            </p>
                          </div>
                        </div>
                        {result.success && result.output && (
                          <button
                            onClick={() => downloadGeneratedCode(result)}
                            className="btn btn-secondary text-xs"
                          >
                            <Download size={12} className="mr-1" />
                            Download
                          </button>
                        )}
                      </div>

                      {result.success && result.mcpServer && (
                        <div className="grid grid-cols-3 gap-4 mb-3">
                          <div>
                            <label className="text-sm font-medium">Server Name</label>
                            <p className="text-sm text-gray-600">{result.mcpServer.name}</p>
                          </div>
                          <div>
                            <label className="text-sm font-medium">Port</label>
                            <p className="text-sm text-gray-600">{result.mcpServer.port}</p>
                          </div>
                          <div>
                            <label className="text-sm font-medium">Endpoints</label>
                            <p className="text-sm text-gray-600">{result.mcpServer.endpoints.length} endpoints</p>
                          </div>
                        </div>
                      )}

                      {result.error && (
                        <div className="text-sm text-red-600 font-mono bg-red-100 p-2 rounded">
                          {result.error}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {/* Deploy Tab */}
      {activeTab === 'deploy' && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">
              <Server size={18} />
              Deploy MCP Servers
            </h3>
          </div>
          <div className="card-content">
            <div className="space-y-4">
              {generationResults.filter(r => r.success).length > 0 ? (
                <>
                  <div>
                    <p className="text-sm text-gray-600 mb-4">
                      Deploy the generated MCP servers to the local environment for immediate use.
                    </p>
                    
                    <div className="space-y-3">
                      {generationResults.filter(r => r.success).map((result, index) => (
                        <div key={index} className="flex items-center justify-between p-3 border rounded">
                          <div>
                            <h4 className="font-medium capitalize">{result.generator} MCP Server</h4>
                            <p className="text-sm text-gray-600">
                              {result.mcpServer?.name} on port {result.mcpServer?.port}
                            </p>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                              Ready
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-4 border-t">
                    <div>
                      {deploymentStatus && (
                        <p className="text-sm text-blue-600">{deploymentStatus}</p>
                      )}
                    </div>
                    <button
                      onClick={deployMCPServers}
                      disabled={isDeploying}
                      className="btn btn-primary"
                    >
                      {isDeploying ? (
                        <>
                          <Loader2 size={16} className="animate-spin mr-2" />
                          Deploying...
                        </>
                      ) : (
                        <>
                          <Server size={16} className="mr-2" />
                          Deploy All Servers
                        </>
                      )}
                    </button>
                  </div>
                </>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Server size={48} className="mx-auto mb-4 opacity-50" />
                  <p className="text-lg font-medium mb-2">No Servers Ready for Deployment</p>
                  <p className="text-sm mb-4">
                    Generate MCP servers first before deploying them.
                  </p>
                  <button
                    onClick={() => setActiveTab('generate')}
                    className="btn btn-primary"
                  >
                    Go to Generator
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}