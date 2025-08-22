// Linting Worker for Monaco Editor
// Performs syntax checking and linting for various languages

import { editor } from 'monaco-editor'

interface LintMessage {
  type: 'linting-result'
  markers: editor.IMarkerData[]
  uri: string
}

interface LintRequest {
  code: string
  language: string
  uri: string
}

// Language-specific linting functions
const linters: Record<string, (code: string) => editor.IMarkerData[]> = {
  typescript: lintTypeScript,
  javascript: lintJavaScript,
  python: lintPython,
  json: lintJSON,
  css: lintCSS,
  html: lintHTML
}

self.onmessage = (event: MessageEvent<LintRequest>) => {
  const { code, language, uri } = event.data
  
  try {
    const linter = linters[language]
    const markers = linter ? linter(code) : []
    
    const response: LintMessage = {
      type: 'linting-result',
      markers,
      uri
    }
    
    self.postMessage(response)
  } catch (error) {
    console.error('Linting error:', error)
    self.postMessage({
      type: 'linting-result',
      markers: [],
      uri
    })
  }
}

function lintTypeScript(code: string): editor.IMarkerData[] {
  const markers: editor.IMarkerData[] = []
  const lines = code.split('\n')
  
  lines.forEach((line, index) => {
    const lineNumber = index + 1
    
    // Check for common TypeScript issues
    
    // Missing semicolons (simplified check)
    if (line.trim() && 
        !line.trim().endsWith(';') && 
        !line.trim().endsWith('{') && 
        !line.trim().endsWith('}') &&
        !line.trim().startsWith('//') &&
        !line.trim().startsWith('*') &&
        !line.includes('if ') &&
        !line.includes('else') &&
        !line.includes('for ') &&
        !line.includes('while ') &&
        !line.includes('function ') &&
        !line.includes('class ') &&
        !line.includes('interface ') &&
        !line.includes('type ') &&
        !line.includes('import ') &&
        !line.includes('export ')) {
      markers.push({
        severity: 4, // Warning
        startLineNumber: lineNumber,
        startColumn: line.length,
        endLineNumber: lineNumber,
        endColumn: line.length + 1,
        message: 'Missing semicolon',
        code: 'missing-semicolon'
      })
    }
    
    // Unused variables (simplified check)
    const varMatches = line.match(/\b(let|const|var)\s+(\w+)/g)
    if (varMatches) {
      varMatches.forEach(match => {
        const varName = match.split(/\s+/)[1]
        const restOfCode = lines.slice(index + 1).join('\n')
        if (!restOfCode.includes(varName)) {
          const startColumn = line.indexOf(varName) + 1
          markers.push({
            severity: 2, // Info
            startLineNumber: lineNumber,
            startColumn,
            endLineNumber: lineNumber,
            endColumn: startColumn + varName.length,
            message: `'${varName}' is declared but never used`,
            code: 'unused-variable'
          })
        }
      })
    }
    
    // Console.log statements (code quality check)
    if (line.includes('console.log')) {
      const startColumn = line.indexOf('console.log') + 1
      markers.push({
        severity: 2, // Info
        startLineNumber: lineNumber,
        startColumn,
        endLineNumber: lineNumber,
        endColumn: startColumn + 11,
        message: 'Avoid using console.log in production code',
        code: 'no-console'
      })
    }
    
    // Type annotation suggestions
    const functionMatch = line.match(/function\s+(\w+)\s*\([^)]*\)\s*{/)
    if (functionMatch && !line.includes(': ')) {
      markers.push({
        severity: 2, // Info
        startLineNumber: lineNumber,
        startColumn: 1,
        endLineNumber: lineNumber,
        endColumn: line.length + 1,
        message: 'Consider adding return type annotation',
        code: 'missing-return-type'
      })
    }
  })
  
  return markers
}

function lintJavaScript(code: string): editor.IMarkerData[] {
  const markers: editor.IMarkerData[] = []
  const lines = code.split('\n')
  
  lines.forEach((line, index) => {
    const lineNumber = index + 1
    
    // Use strict mode check
    if (index === 0 && !line.includes("'use strict'") && !line.includes('"use strict"')) {
      markers.push({
        severity: 2, // Info
        startLineNumber: 1,
        startColumn: 1,
        endLineNumber: 1,
        endColumn: 1,
        message: "Consider adding 'use strict' directive",
        code: 'missing-strict-mode'
      })
    }
    
    // Equality operator suggestions
    if (line.includes('==') && !line.includes('===')) {
      const startColumn = line.indexOf('==') + 1
      markers.push({
        severity: 4, // Warning
        startLineNumber: lineNumber,
        startColumn,
        endLineNumber: lineNumber,
        endColumn: startColumn + 2,
        message: 'Use === instead of ==',
        code: 'eqeqeq'
      })
    }
    
    // Variable declaration suggestions
    if (line.includes('var ')) {
      const startColumn = line.indexOf('var ') + 1
      markers.push({
        severity: 2, // Info
        startLineNumber: lineNumber,
        startColumn,
        endLineNumber: lineNumber,
        endColumn: startColumn + 3,
        message: 'Consider using let or const instead of var',
        code: 'no-var'
      })
    }
  })
  
  return markers
}

function lintPython(code: string): editor.IMarkerData[] {
  const markers: editor.IMarkerData[] = []
  const lines = code.split('\n')
  
  lines.forEach((line, index) => {
    const lineNumber = index + 1
    
    // Indentation check (simplified)
    if (line.trim() && !line.startsWith(' ') && !line.startsWith('\t') && index > 0) {
      const prevLine = lines[index - 1]
      if (prevLine.trim().endsWith(':')) {
        markers.push({
          severity: 8, // Error
          startLineNumber: lineNumber,
          startColumn: 1,
          endLineNumber: lineNumber,
          endColumn: 5,
          message: 'Expected indented block',
          code: 'indentation-error'
        })
      }
    }
    
    // Import organization
    if (line.includes('import ') && index > 0) {
      const prevLines = lines.slice(0, index)
      const hasNonImport = prevLines.some(l => 
        l.trim() && 
        !l.startsWith('import ') && 
        !l.startsWith('from ') && 
        !l.startsWith('#') &&
        !l.startsWith('"""') &&
        !l.startsWith("'''")
      )
      
      if (hasNonImport) {
        markers.push({
          severity: 2, // Info
          startLineNumber: lineNumber,
          startColumn: 1,
          endLineNumber: lineNumber,
          endColumn: line.length + 1,
          message: 'Imports should be at the top of the file',
          code: 'import-order'
        })
      }
    }
    
    // Line length check
    if (line.length > 88) {
      markers.push({
        severity: 2, // Info
        startLineNumber: lineNumber,
        startColumn: 89,
        endLineNumber: lineNumber,
        endColumn: line.length + 1,
        message: 'Line too long (>88 characters)',
        code: 'line-too-long'
      })
    }
  })
  
  return markers
}

function lintJSON(code: string): editor.IMarkerData[] {
  const markers: editor.IMarkerData[] = []
  
  try {
    JSON.parse(code)
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Invalid JSON'
    
    // Try to extract line number from error message
    const lineMatch = errorMessage.match(/line (\d+)/i)
    const line = lineMatch ? parseInt(lineMatch[1]) : 1
    
    markers.push({
      severity: 8, // Error
      startLineNumber: line,
      startColumn: 1,
      endLineNumber: line,
      endColumn: 100,
      message: errorMessage,
      code: 'json-parse-error'
    })
  }
  
  return markers
}

function lintCSS(code: string): editor.IMarkerData[] {
  const markers: editor.IMarkerData[] = []
  const lines = code.split('\n')
  
  lines.forEach((line, index) => {
    const lineNumber = index + 1
    
    // Missing semicolons in CSS
    if (line.includes(':') && line.trim() && !line.includes('{') && !line.includes('}') && !line.trim().endsWith(';')) {
      markers.push({
        severity: 4, // Warning
        startLineNumber: lineNumber,
        startColumn: line.length,
        endLineNumber: lineNumber,
        endColumn: line.length + 1,
        message: 'Missing semicolon',
        code: 'missing-semicolon'
      })
    }
    
    // Unknown CSS properties (simplified check)
    const propertyMatch = line.match(/^\s*([a-z-]+)\s*:/)
    if (propertyMatch) {
      const property = propertyMatch[1]
      const knownProperties = [
        'color', 'background', 'margin', 'padding', 'border', 'width', 'height',
        'display', 'position', 'top', 'left', 'right', 'bottom', 'font-size',
        'font-family', 'text-align', 'line-height', 'opacity', 'z-index'
      ]
      
      if (!knownProperties.includes(property)) {
        const startColumn = line.indexOf(property) + 1
        markers.push({
          severity: 2, // Info
          startLineNumber: lineNumber,
          startColumn,
          endLineNumber: lineNumber,
          endColumn: startColumn + property.length,
          message: `Unknown property '${property}'`,
          code: 'unknown-property'
        })
      }
    }
  })
  
  return markers
}

function lintHTML(code: string): editor.IMarkerData[] {
  const markers: editor.IMarkerData[] = []
  const lines = code.split('\n')
  
  lines.forEach((line, index) => {
    const lineNumber = index + 1
    
    // Unclosed tags (simplified check)
    const openTags = line.match(/<(\w+)[^>]*>/g) || []
    const closeTags = line.match(/<\/(\w+)>/g) || []
    
    openTags.forEach(tag => {
      const tagName = tag.match(/<(\w+)/)?.[1]
      if (tagName && !['img', 'br', 'hr', 'input', 'meta', 'link'].includes(tagName)) {
        const hasClosing = closeTags.some(closeTag => 
          closeTag.includes(tagName)
        )
        
        if (!hasClosing) {
          const startColumn = line.indexOf(tag) + 1
          markers.push({
            severity: 4, // Warning
            startLineNumber: lineNumber,
            startColumn,
            endLineNumber: lineNumber,
            endColumn: startColumn + tag.length,
            message: `Unclosed tag '${tagName}'`,
            code: 'unclosed-tag'
          })
        }
      }
    })
    
    // Missing alt attributes for images
    if (line.includes('<img') && !line.includes('alt=')) {
      const startColumn = line.indexOf('<img') + 1
      markers.push({
        severity: 4, // Warning
        startLineNumber: lineNumber,
        startColumn,
        endLineNumber: lineNumber,
        endColumn: startColumn + 4,
        message: 'Image missing alt attribute',
        code: 'missing-alt'
      })
    }
  })
  
  return markers
}

export {}