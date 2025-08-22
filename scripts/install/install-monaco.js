#!/usr/bin/env node

/**
 * Monaco Editor Installation Script
 * Installs and configures Monaco Editor with all dependencies
 */

const { execSync } = require('child_process')
const fs = require('fs')
const path = require('path')

console.log('🚀 Installing Monaco Editor Integration...\n')

// Check if we're in the correct directory
const webAppPath = path.join(process.cwd(), 'apps', 'web')
if (!fs.existsSync(webAppPath)) {
  console.error('❌ Error: Please run this script from the project root directory')
  process.exit(1)
}

const dependencies = [
  '@monaco-editor/react@^4.6.0',
  'monaco-editor@^0.45.0',
  'monaco-languageclient@^8.0.0',
  'vscode-languageserver-protocol@^3.17.5',
  'vscode-languageserver@^9.0.1',
  'prettier@^3.1.1',
  'y-monaco@^0.1.5',
  'y-websocket@^1.5.0',
  'yjs@^13.6.10',
  'monaco-vim@^0.4.0',
  'monaco-emacs@^0.3.0'
]

const devDependencies = [
  '@types/prettier@^3.0.0'
]

try {
  // Change to web app directory
  process.chdir(webAppPath)
  
  console.log('📦 Installing Monaco Editor dependencies...')
  execSync(`npm install ${dependencies.join(' ')}`, { stdio: 'inherit' })
  
  console.log('\n📦 Installing development dependencies...')
  execSync(`npm install --save-dev ${devDependencies.join(' ')}`, { stdio: 'inherit' })
  
  console.log('\n⚙️ Setting up Vite configuration for Monaco...')
  
  // Read existing vite.config.ts
  const viteConfigPath = path.join(process.cwd(), 'vite.config.ts')
  let viteConfig = ''
  
  if (fs.existsSync(viteConfigPath)) {
    viteConfig = fs.readFileSync(viteConfigPath, 'utf8')
  } else {
    viteConfig = `import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})`
  }
  
  // Check if Monaco configuration already exists
  if (!viteConfig.includes('monaco-editor')) {
    // Add Monaco Editor configuration
    const monacoConfig = `
  // Monaco Editor configuration
  optimizeDeps: {
    include: [
      'monaco-editor',
      'monaco-editor/esm/vs/language/typescript/ts.worker',
      'monaco-editor/esm/vs/language/json/json.worker',
      'monaco-editor/esm/vs/language/css/css.worker',
      'monaco-editor/esm/vs/language/html/html.worker',
      'monaco-editor/esm/vs/editor/editor.worker'
    ],
  },
  define: {
    global: 'globalThis',
  },
  worker: {
    format: 'es'
  }`
    
    // Insert Monaco config before the closing brace
    viteConfig = viteConfig.replace(
      /export default defineConfig\(\{([^}]+)\}\)/,
      `export default defineConfig({$1,${monacoConfig}
})`
    )
    
    fs.writeFileSync(viteConfigPath, viteConfig)
    console.log('✅ Updated Vite configuration')
  } else {
    console.log('✅ Vite configuration already includes Monaco settings')
  }
  
  console.log('\n🎨 Setting up CSS imports...')
  
  // Check if CSS is already imported in main CSS file
  const mainCssPath = path.join(process.cwd(), 'src', 'index.css')
  if (fs.existsSync(mainCssPath)) {
    let mainCss = fs.readFileSync(mainCssPath, 'utf8')
    
    if (!mainCss.includes('monaco-editor.css')) {
      mainCss += '\n\n/* Monaco Editor Styles */\n@import "./styles/monaco-editor.css";\n'
      fs.writeFileSync(mainCssPath, mainCss)
      console.log('✅ Added Monaco Editor CSS import')
    } else {
      console.log('✅ Monaco Editor CSS already imported')
    }
  }
  
  console.log('\n🔧 Creating language server configuration...')
  
  // Create language server config file
  const configDir = path.join(process.cwd(), 'src', 'config')
  if (!fs.existsSync(configDir)) {
    fs.mkdirSync(configDir, { recursive: true })
  }
  
  const languageServerConfig = `// Language Server Configuration
export const LANGUAGE_SERVERS = {
  typescript: {
    url: process.env.REACT_APP_TS_LANGUAGE_SERVER || 'ws://localhost:3001/typescript',
    enabled: true
  },
  python: {
    url: process.env.REACT_APP_PYTHON_LANGUAGE_SERVER || 'ws://localhost:3001/python',
    enabled: true
  },
  go: {
    url: process.env.REACT_APP_GO_LANGUAGE_SERVER || 'ws://localhost:3001/go',
    enabled: true
  },
  rust: {
    url: process.env.REACT_APP_RUST_LANGUAGE_SERVER || 'ws://localhost:3001/rust',
    enabled: true
  }
}

export const COLLABORATION_CONFIG = {
  enabled: process.env.REACT_APP_COLLABORATION_ENABLED === 'true',
  websocketUrl: process.env.REACT_APP_COLLABORATION_URL || 'ws://localhost:1234'
}

export const GIT_CONFIG = {
  enabled: process.env.REACT_APP_GIT_INTEGRATION_ENABLED !== 'false',
  serviceUrl: process.env.REACT_APP_GIT_SERVICE_URL || 'ws://localhost:3002'
}`
  
  const configPath = path.join(configDir, 'monaco.ts')
  if (!fs.existsSync(configPath)) {
    fs.writeFileSync(configPath, languageServerConfig)
    console.log('✅ Created language server configuration')
  } else {
    console.log('✅ Language server configuration already exists')
  }
  
  console.log('\n📄 Creating environment template...')
  
  // Create .env.example file
  const envExample = `# Monaco Editor Configuration
REACT_APP_TS_LANGUAGE_SERVER=ws://localhost:3001/typescript
REACT_APP_PYTHON_LANGUAGE_SERVER=ws://localhost:3001/python
REACT_APP_GO_LANGUAGE_SERVER=ws://localhost:3001/go
REACT_APP_RUST_LANGUAGE_SERVER=ws://localhost:3001/rust
REACT_APP_COLLABORATION_ENABLED=true
REACT_APP_COLLABORATION_URL=ws://localhost:1234
REACT_APP_GIT_INTEGRATION_ENABLED=true
REACT_APP_GIT_SERVICE_URL=ws://localhost:3002

# Editor Features
REACT_APP_ENABLE_VIM_MODE=false
REACT_APP_ENABLE_EMACS_MODE=false
REACT_APP_DEFAULT_THEME=auto
REACT_APP_DEFAULT_FONT_SIZE=14
REACT_APP_DEFAULT_FONT_FAMILY='JetBrains Mono', 'Fira Code', Consolas, monospace`
  
  const envExamplePath = path.join(process.cwd(), '.env.example')
  if (!fs.existsSync(envExamplePath)) {
    fs.writeFileSync(envExamplePath, envExample)
    console.log('✅ Created environment template')
  } else {
    console.log('✅ Environment template already exists')
  }
  
  console.log('\n🧪 Setting up test configuration...')
  
  // Create test utilities
  const testUtilsDir = path.join(process.cwd(), 'src', 'test-utils')
  if (!fs.existsSync(testUtilsDir)) {
    fs.mkdirSync(testUtilsDir, { recursive: true })
  }
  
  const monacoTestUtils = `// Monaco Editor Test Utilities
import { render, RenderOptions } from '@testing-library/react'
import { ReactElement } from 'react'

// Mock Monaco Editor for tests
export const mockMonacoEditor = {
  editor: {
    create: jest.fn(),
    defineTheme: jest.fn(),
    setModelLanguage: jest.fn(),
    getModel: jest.fn(),
    getValue: jest.fn(),
    setValue: jest.fn(),
    onDidChangeContent: jest.fn(),
    dispose: jest.fn()
  },
  languages: {
    registerCompletionItemProvider: jest.fn(),
    registerHoverProvider: jest.fn(),
    registerDefinitionProvider: jest.fn()
  }
}

// Mock module
jest.mock('@monaco-editor/react', () => ({
  Editor: ({ onChange, onMount }: any) => {
    // Simulate editor mount
    if (onMount) {
      onMount(mockMonacoEditor.editor, mockMonacoEditor)
    }
    return <div data-testid="monaco-editor" />
  }
}))

export const renderWithProviders = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => {
  return render(ui, options)
}

export * from '@testing-library/react'`
  
  const testUtilsPath = path.join(testUtilsDir, 'monaco.tsx')
  if (!fs.existsSync(testUtilsPath)) {
    fs.writeFileSync(testUtilsPath, monacoTestUtils)
    console.log('✅ Created Monaco test utilities')
  } else {
    console.log('✅ Monaco test utilities already exist')
  }
  
  console.log('\n🚀 Installation completed successfully!')
  console.log('\n📝 Next steps:')
  console.log('1. Copy .env.example to .env and configure as needed')
  console.log('2. Start language servers (optional)')
  console.log('3. Run npm start to see the Monaco Editor in action')
  console.log('4. Visit /editor route to see the demo')
  console.log('\n📚 Documentation: See MONACO_EDITOR_README.md for details')
  
} catch (error) {
  console.error('❌ Installation failed:', error.message)
  process.exit(1)
}