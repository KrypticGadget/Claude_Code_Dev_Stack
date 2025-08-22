import React, { useEffect, useRef } from 'react'
import { editor } from 'monaco-editor'
import { GitStatus } from '../hooks/useGitIntegration'
import { Breakpoint } from '../hooks/useDebugger'

export interface MonacoEditorMinimapProps {
  editor: editor.IStandaloneCodeEditor | null
  gitStatus?: GitStatus
  breakpoints?: Map<string, Breakpoint[]>
  onLineClick?: (line: number) => void
}

export const MonacoEditorMinimap: React.FC<MonacoEditorMinimapProps> = ({
  editor,
  gitStatus,
  breakpoints,
  onLineClick
}) => {
  const minimapRef = useRef<HTMLCanvasElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!editor || !minimapRef.current) return

    const canvas = minimapRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const model = editor.getModel()
    if (!model) return

    // Setup canvas
    const container = containerRef.current!
    const rect = container.getBoundingClientRect()
    
    canvas.width = rect.width * devicePixelRatio
    canvas.height = rect.height * devicePixelRatio
    canvas.style.width = `${rect.width}px`
    canvas.style.height = `${rect.height}px`
    ctx.scale(devicePixelRatio, devicePixelRatio)

    // Draw minimap
    drawMinimap(ctx, editor, model, rect.width, rect.height)

    // Add Git indicators if available
    if (gitStatus) {
      drawGitIndicators(ctx, editor, model, gitStatus, rect.width, rect.height)
    }

    // Add breakpoint indicators if available
    if (breakpoints) {
      drawBreakpointIndicators(ctx, editor, model, breakpoints, rect.width, rect.height)
    }

    // Update on content changes
    const contentListener = model.onDidChangeContent(() => {
      requestAnimationFrame(() => {
        drawMinimap(ctx, editor, model, rect.width, rect.height)
      })
    })

    // Update on scroll
    const scrollListener = editor.onDidScrollChange(() => {
      requestAnimationFrame(() => {
        drawViewport(ctx, editor, model, rect.width, rect.height)
      })
    })

    return () => {
      contentListener.dispose()
      scrollListener.dispose()
    }
  }, [editor, gitStatus, breakpoints])

  const drawMinimap = (
    ctx: CanvasRenderingContext2D,
    editor: editor.IStandaloneCodeEditor,
    model: editor.ITextModel,
    width: number,
    height: number
  ) => {
    ctx.clearRect(0, 0, width, height)

    const lineCount = model.getLineCount()
    const lineHeight = height / lineCount
    const charWidth = 1 // Simplified character width

    // Draw background
    ctx.fillStyle = '#1e1e1e'
    ctx.fillRect(0, 0, width, height)

    // Draw code content
    for (let lineNumber = 1; lineNumber <= lineCount; lineNumber++) {
      const line = model.getLineContent(lineNumber)
      const y = (lineNumber - 1) * lineHeight

      // Analyze line content for syntax highlighting
      const tokens = getLineTokens(line)
      let x = 0

      tokens.forEach(token => {
        ctx.fillStyle = getTokenColor(token.type)
        const tokenWidth = Math.min(token.text.length * charWidth, width - x)
        ctx.fillRect(x, y, tokenWidth, Math.max(lineHeight, 1))
        x += tokenWidth
      })
    }

    // Draw viewport indicator
    drawViewport(ctx, editor, model, width, height)
  }

  const drawViewport = (
    ctx: CanvasRenderingContext2D,
    editor: editor.IStandaloneCodeEditor,
    model: editor.ITextModel,
    width: number,
    height: number
  ) => {
    const visibleRange = editor.getVisibleRanges()[0]
    if (!visibleRange) return

    const lineCount = model.getLineCount()
    const lineHeight = height / lineCount

    const startY = (visibleRange.startLineNumber - 1) * lineHeight
    const endY = visibleRange.endLineNumber * lineHeight
    const viewportHeight = endY - startY

    // Draw viewport outline
    ctx.strokeStyle = '#007acc'
    ctx.lineWidth = 1
    ctx.setLineDash([])
    ctx.strokeRect(0, startY, width, viewportHeight)

    // Draw semi-transparent overlay
    ctx.fillStyle = 'rgba(0, 122, 204, 0.1)'
    ctx.fillRect(0, startY, width, viewportHeight)
  }

  const drawGitIndicators = (
    ctx: CanvasRenderingContext2D,
    editor: editor.IStandaloneCodeEditor,
    model: editor.ITextModel,
    gitStatus: GitStatus,
    width: number,
    height: number
  ) => {
    const lineCount = model.getLineCount()
    const lineHeight = height / lineCount
    const indicatorWidth = 3

    // Get current file path (simplified)
    const uri = model.uri.toString()
    
    // Draw modified lines indicator
    if (gitStatus.modified.some(file => uri.includes(file))) {
      ctx.fillStyle = '#f39c12'
      for (let lineNumber = 1; lineNumber <= lineCount; lineNumber++) {
        // This would typically come from diff information
        if (Math.random() < 0.1) { // Simulated modified lines
          const y = (lineNumber - 1) * lineHeight
          ctx.fillRect(width - indicatorWidth, y, indicatorWidth, Math.max(lineHeight, 1))
        }
      }
    }

    // Draw added lines indicator
    if (gitStatus.added.some(file => uri.includes(file))) {
      ctx.fillStyle = '#27ae60'
      for (let lineNumber = 1; lineNumber <= lineCount; lineNumber++) {
        if (Math.random() < 0.05) { // Simulated added lines
          const y = (lineNumber - 1) * lineHeight
          ctx.fillRect(width - indicatorWidth, y, indicatorWidth, Math.max(lineHeight, 1))
        }
      }
    }
  }

  const drawBreakpointIndicators = (
    ctx: CanvasRenderingContext2D,
    editor: editor.IStandaloneCodeEditor,
    model: editor.ITextModel,
    breakpoints: Map<string, Breakpoint[]>,
    width: number,
    height: number
  ) => {
    const uri = model.uri.toString()
    const fileBreakpoints = breakpoints.get(uri) || []
    
    if (fileBreakpoints.length === 0) return

    const lineCount = model.getLineCount()
    const lineHeight = height / lineCount
    const indicatorSize = 4

    fileBreakpoints.forEach(bp => {
      const y = (bp.line - 1) * lineHeight
      const x = 2

      // Draw breakpoint circle
      ctx.beginPath()
      ctx.arc(x + indicatorSize / 2, y + lineHeight / 2, indicatorSize / 2, 0, 2 * Math.PI)
      
      if (bp.enabled) {
        ctx.fillStyle = bp.verified ? '#e74c3c' : '#f39c12'
      } else {
        ctx.fillStyle = '#95a5a6'
      }
      
      ctx.fill()

      // Draw condition indicator for conditional breakpoints
      if (bp.condition || bp.logMessage) {
        ctx.strokeStyle = '#ffffff'
        ctx.lineWidth = 1
        ctx.stroke()
      }
    })
  }

  const getLineTokens = (line: string) => {
    // Simplified tokenization - in a real implementation, this would use Monaco's tokenizer
    const tokens = []
    const keywords = ['function', 'const', 'let', 'var', 'if', 'else', 'for', 'while', 'return']
    const strings = line.match(/"[^"]*"|'[^']*'|`[^`]*`/g) || []
    const comments = line.match(/\/\/.*|\/\*[\s\S]*?\*\//g) || []

    let remaining = line
    let offset = 0

    // Extract strings
    strings.forEach(str => {
      const index = remaining.indexOf(str)
      if (index !== -1) {
        if (index > 0) {
          tokens.push({ type: 'default', text: remaining.substring(0, index) })
        }
        tokens.push({ type: 'string', text: str })
        remaining = remaining.substring(index + str.length)
        offset += index + str.length
      }
    })

    // Extract comments
    comments.forEach(comment => {
      const index = remaining.indexOf(comment)
      if (index !== -1) {
        if (index > 0) {
          tokens.push({ type: 'default', text: remaining.substring(0, index) })
        }
        tokens.push({ type: 'comment', text: comment })
        remaining = remaining.substring(index + comment.length)
        offset += index + comment.length
      }
    })

    // Check for keywords in remaining text
    keywords.forEach(keyword => {
      const regex = new RegExp(`\\b${keyword}\\b`, 'g')
      remaining = remaining.replace(regex, (match) => {
        tokens.push({ type: 'keyword', text: match })
        return ''
      })
    })

    if (remaining.trim()) {
      tokens.push({ type: 'default', text: remaining })
    }

    return tokens.length > 0 ? tokens : [{ type: 'default', text: line }]
  }

  const getTokenColor = (tokenType: string): string => {
    const colors: Record<string, string> = {
      keyword: '#569cd6',
      string: '#ce9178',
      comment: '#6a9955',
      number: '#b5cea8',
      default: '#d4d4d4'
    }
    return colors[tokenType] || colors.default
  }

  const handleCanvasClick = (event: React.MouseEvent<HTMLCanvasElement>) => {
    if (!editor || !onLineClick) return

    const canvas = minimapRef.current!
    const rect = canvas.getBoundingClientRect()
    const y = event.clientY - rect.top

    const model = editor.getModel()
    if (!model) return

    const lineCount = model.getLineCount()
    const lineHeight = rect.height / lineCount
    const lineNumber = Math.ceil(y / lineHeight)

    onLineClick(lineNumber)
    
    // Scroll to line
    editor.revealLineInCenter(lineNumber)
  }

  return (
    <div 
      ref={containerRef}
      className="monaco-minimap-container"
      style={{
        position: 'absolute',
        right: 0,
        top: 0,
        width: '120px',
        height: '100%',
        backgroundColor: '#1e1e1e',
        borderLeft: '1px solid #3c3c3c',
        overflow: 'hidden'
      }}
    >
      <canvas
        ref={minimapRef}
        className="monaco-minimap-canvas"
        onClick={handleCanvasClick}
        style={{
          cursor: 'pointer',
          width: '100%',
          height: '100%'
        }}
      />
    </div>
  )
}

export default MonacoEditorMinimap