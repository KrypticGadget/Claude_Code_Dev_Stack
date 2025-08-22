// Color Picker - Advanced Color Selection with Accessibility Features
// Supports hex, RGB, HSL, and color blind friendly palettes

import React, { useState, useRef, useEffect, useCallback } from 'react'

interface ColorPickerProps {
  value: string
  onChange: (value: string) => void
  onGenerateVariations?: (value: string) => void
  label?: string
  disabled?: boolean
  showVariationButton?: boolean
  showAccessibilityInfo?: boolean
}

export const ColorPicker: React.FC<ColorPickerProps> = ({
  value,
  onChange,
  onGenerateVariations,
  label,
  disabled = false,
  showVariationButton = true,
  showAccessibilityInfo = true
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const [inputValue, setInputValue] = useState(value)
  const [colorFormat, setColorFormat] = useState<'hex' | 'rgb' | 'hsl'>('hex')
  const pickerRef = useRef<HTMLDivElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const hueCanvasRef = useRef<HTMLCanvasElement>(null)

  // Color palette presets
  const colorPresets = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
    '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
    '#F8C471', '#82E0AA', '#F1948A', '#85C1E9', '#D7BDE2',
    '#A3E4D7', '#F9E79F', '#FADBD8', '#D6EAF8', '#E8DAEF'
  ]

  // Accessibility safe color pairs
  const accessiblePairs = [
    { bg: '#000000', fg: '#FFFFFF', name: 'High Contrast' },
    { bg: '#FFFFFF', fg: '#000000', name: 'Inverted' },
    { bg: '#1A1B26', fg: '#C0CAF5', name: 'Tokyo Night' },
    { bg: '#282C34', fg: '#ABB2BF', name: 'One Dark' },
    { bg: '#FFFFFF', fg: '#24292E', name: 'GitHub Light' }
  ]

  useEffect(() => {
    setInputValue(value)
  }, [value])

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (pickerRef.current && !pickerRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
      drawColorPicker()
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  const drawColorPicker = useCallback(() => {
    const canvas = canvasRef.current
    const hueCanvas = hueCanvasRef.current
    if (!canvas || !hueCanvas) return

    const ctx = canvas.getContext('2d')
    const hueCtx = hueCanvas.getContext('2d')
    if (!ctx || !hueCtx) return

    // Draw main color picker
    const width = canvas.width
    const height = canvas.height

    // Create gradient from white to transparent
    const whiteGrad = ctx.createLinearGradient(0, 0, width, 0)
    whiteGrad.addColorStop(0, 'rgba(255, 255, 255, 1)')
    whiteGrad.addColorStop(1, 'rgba(255, 255, 255, 0)')

    // Create gradient from transparent to black
    const blackGrad = ctx.createLinearGradient(0, 0, 0, height)
    blackGrad.addColorStop(0, 'rgba(0, 0, 0, 0)')
    blackGrad.addColorStop(1, 'rgba(0, 0, 0, 1)')

    // Fill with current hue
    const hsl = hexToHsl(value)
    ctx.fillStyle = `hsl(${hsl.h}, 100%, 50%)`
    ctx.fillRect(0, 0, width, height)

    // Apply white gradient
    ctx.fillStyle = whiteGrad
    ctx.fillRect(0, 0, width, height)

    // Apply black gradient
    ctx.fillStyle = blackGrad
    ctx.fillRect(0, 0, width, height)

    // Draw hue bar
    const hueWidth = hueCanvas.width
    const hueHeight = hueCanvas.height
    const hueGrad = hueCtx.createLinearGradient(0, 0, 0, hueHeight)
    
    for (let i = 0; i <= 360; i += 60) {
      hueGrad.addColorStop(i / 360, `hsl(${i}, 100%, 50%)`)
    }
    
    hueCtx.fillStyle = hueGrad
    hueCtx.fillRect(0, 0, hueWidth, hueHeight)
  }, [value])

  const handleCanvasClick = useCallback((event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const rect = canvas.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top

    const saturation = (x / canvas.width) * 100
    const lightness = 100 - (y / canvas.height) * 100
    
    const hsl = hexToHsl(value)
    const newColor = hslToHex(hsl.h, saturation, lightness)
    
    onChange(newColor)
    setInputValue(newColor)
  }, [value, onChange])

  const handleHueClick = useCallback((event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = hueCanvasRef.current
    if (!canvas) return

    const rect = canvas.getBoundingClientRect()
    const y = event.clientY - rect.top
    const hue = (y / canvas.height) * 360

    const hsl = hexToHsl(value)
    const newColor = hslToHex(hue, hsl.s, hsl.l)
    
    onChange(newColor)
    setInputValue(newColor)
  }, [value, onChange])

  const handleInputChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = event.target.value
    setInputValue(newValue)
    
    if (isValidColor(newValue)) {
      onChange(newValue)
    }
  }, [onChange])

  const handleInputBlur = useCallback(() => {
    if (!isValidColor(inputValue)) {
      setInputValue(value) // Reset to valid value
    }
  }, [inputValue, value])

  const handleFormatChange = useCallback((format: 'hex' | 'rgb' | 'hsl') => {
    setColorFormat(format)
    let convertedValue = value
    
    if (format === 'rgb') {
      convertedValue = hexToRgb(value)
    } else if (format === 'hsl') {
      convertedValue = hexToHslString(value)
    }
    
    setInputValue(convertedValue)
  }, [value])

  const getAccessibilityInfo = useCallback(() => {
    const luminance = getLuminance(value)
    const contrastWithWhite = (1.05) / (luminance + 0.05)
    const contrastWithBlack = (luminance + 0.05) / (0.05)
    
    return {
      luminance: luminance.toFixed(3),
      contrastWithWhite: contrastWithWhite.toFixed(2),
      contrastWithBlack: contrastWithBlack.toFixed(2),
      wcagAA: Math.max(contrastWithWhite, contrastWithBlack) >= 4.5,
      wcagAAA: Math.max(contrastWithWhite, contrastWithBlack) >= 7
    }
  }, [value])

  const accessibilityInfo = showAccessibilityInfo ? getAccessibilityInfo() : null

  return (
    <div className="color-picker-container" ref={pickerRef}>
      <div className="color-picker-input">
        <div 
          className="color-swatch"
          style={{ backgroundColor: value }}
          onClick={() => !disabled && setIsOpen(!isOpen)}
          role="button"
          tabIndex={disabled ? -1 : 0}
          aria-label={`Color: ${value}`}
          aria-expanded={isOpen}
        />
        
        <input
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onBlur={handleInputBlur}
          disabled={disabled}
          className={`color-input ${!isValidColor(inputValue) ? 'invalid' : ''}`}
          aria-label={label || 'Color value'}
        />
        
        {showVariationButton && onGenerateVariations && (
          <button
            type="button"
            className="btn btn-sm btn-secondary"
            onClick={() => onGenerateVariations(value)}
            disabled={disabled}
            title="Generate color variations"
          >
            ✨
          </button>
        )}
      </div>

      {isOpen && (
        <div className="color-picker-dropdown">
          <div className="color-picker-header">
            <div className="format-tabs">
              <button
                className={`format-tab ${colorFormat === 'hex' ? 'active' : ''}`}
                onClick={() => handleFormatChange('hex')}
              >
                HEX
              </button>
              <button
                className={`format-tab ${colorFormat === 'rgb' ? 'active' : ''}`}
                onClick={() => handleFormatChange('rgb')}
              >
                RGB
              </button>
              <button
                className={`format-tab ${colorFormat === 'hsl' ? 'active' : ''}`}
                onClick={() => handleFormatChange('hsl')}
              >
                HSL
              </button>
            </div>
          </div>

          <div className="color-picker-main">
            <div className="color-picker-area">
              <canvas
                ref={canvasRef}
                width={200}
                height={150}
                onClick={handleCanvasClick}
                className="color-canvas"
              />
              
              <canvas
                ref={hueCanvasRef}
                width={20}
                height={150}
                onClick={handleHueClick}
                className="hue-canvas"
              />
            </div>

            <div className="color-presets">
              <h4>Presets</h4>
              <div className="preset-grid">
                {colorPresets.map((preset, index) => (
                  <button
                    key={index}
                    className="preset-color"
                    style={{ backgroundColor: preset }}
                    onClick={() => {
                      onChange(preset)
                      setInputValue(preset)
                    }}
                    title={preset}
                    aria-label={`Preset color ${preset}`}
                  />
                ))}
              </div>
            </div>

            {showAccessibilityInfo && accessibilityInfo && (
              <div className="accessibility-info">
                <h4>Accessibility</h4>
                <div className="accessibility-stats">
                  <div className="stat">
                    <span>Luminance:</span>
                    <span>{accessibilityInfo.luminance}</span>
                  </div>
                  <div className="stat">
                    <span>Contrast (White):</span>
                    <span className={parseFloat(accessibilityInfo.contrastWithWhite) >= 4.5 ? 'good' : 'poor'}>
                      {accessibilityInfo.contrastWithWhite}:1
                    </span>
                  </div>
                  <div className="stat">
                    <span>Contrast (Black):</span>
                    <span className={parseFloat(accessibilityInfo.contrastWithBlack) >= 4.5 ? 'good' : 'poor'}>
                      {accessibilityInfo.contrastWithBlack}:1
                    </span>
                  </div>
                  <div className="stat">
                    <span>WCAG AA:</span>
                    <span className={accessibilityInfo.wcagAA ? 'pass' : 'fail'}>
                      {accessibilityInfo.wcagAA ? 'Pass' : 'Fail'}
                    </span>
                  </div>
                </div>
              </div>
            )}

            <div className="accessible-pairs">
              <h4>Accessible Combinations</h4>
              <div className="pairs-grid">
                {accessiblePairs.map((pair, index) => (
                  <button
                    key={index}
                    className="accessible-pair"
                    style={{ 
                      backgroundColor: pair.bg, 
                      color: pair.fg,
                      border: `1px solid ${pair.fg}`
                    }}
                    onClick={() => {
                      onChange(pair.bg)
                      setInputValue(pair.bg)
                    }}
                    title={`${pair.name}: ${pair.bg} on ${pair.fg}`}
                  >
                    Aa
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .color-picker-container {
          position: relative;
          display: inline-block;
        }

        .color-picker-input {
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
        }

        .color-swatch {
          width: 32px;
          height: 32px;
          border-radius: var(--radius-md);
          border: 2px solid var(--color-border);
          cursor: pointer;
          transition: transform var(--transition-fast);
          position: relative;
        }

        .color-swatch:hover {
          transform: scale(1.05);
        }

        .color-swatch::before {
          content: '';
          position: absolute;
          inset: 0;
          background: linear-gradient(45deg, #ccc 25%, transparent 25%),
                      linear-gradient(-45deg, #ccc 25%, transparent 25%),
                      linear-gradient(45deg, transparent 75%, #ccc 75%),
                      linear-gradient(-45deg, transparent 75%, #ccc 75%);
          background-size: 8px 8px;
          background-position: 0 0, 0 4px, 4px -4px, -4px 0px;
          border-radius: inherit;
          z-index: -1;
        }

        .color-input {
          flex: 1;
          padding: var(--spacing-sm);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-md);
          background: var(--color-background);
          color: var(--color-text-primary);
          font-family: var(--font-family-mono);
          font-size: var(--font-size-sm);
          min-width: 100px;
        }

        .color-input.invalid {
          border-color: var(--color-error);
          background: var(--color-error-light);
        }

        .color-picker-dropdown {
          position: absolute;
          top: 100%;
          left: 0;
          z-index: var(--z-dropdown);
          background: var(--color-background);
          border: 1px solid var(--color-border);
          border-radius: var(--radius-lg);
          box-shadow: var(--shadow-lg);
          padding: var(--spacing-md);
          width: 280px;
          margin-top: var(--spacing-sm);
        }

        .color-picker-header {
          margin-bottom: var(--spacing-md);
        }

        .format-tabs {
          display: flex;
          background: var(--color-background-secondary);
          border-radius: var(--radius-md);
          padding: 2px;
        }

        .format-tab {
          flex: 1;
          padding: var(--spacing-xs) var(--spacing-sm);
          border: none;
          background: none;
          color: var(--color-text-secondary);
          font-size: var(--font-size-xs);
          border-radius: var(--radius-sm);
          cursor: pointer;
          transition: all var(--transition-fast);
        }

        .format-tab.active {
          background: var(--color-primary);
          color: white;
        }

        .color-picker-main {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-md);
        }

        .color-picker-area {
          display: flex;
          gap: var(--spacing-sm);
        }

        .color-canvas {
          border-radius: var(--radius-md);
          cursor: crosshair;
          border: 1px solid var(--color-border);
        }

        .hue-canvas {
          border-radius: var(--radius-md);
          cursor: crosshair;
          border: 1px solid var(--color-border);
        }

        .color-presets h4,
        .accessibility-info h4,
        .accessible-pairs h4 {
          margin: 0 0 var(--spacing-sm) 0;
          font-size: var(--font-size-sm);
          color: var(--color-text-secondary);
        }

        .preset-grid {
          display: grid;
          grid-template-columns: repeat(5, 1fr);
          gap: var(--spacing-xs);
        }

        .preset-color {
          width: 24px;
          height: 24px;
          border: 1px solid var(--color-border);
          border-radius: var(--radius-sm);
          cursor: pointer;
          transition: transform var(--transition-fast);
        }

        .preset-color:hover {
          transform: scale(1.1);
        }

        .accessibility-stats {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-xs);
        }

        .stat {
          display: flex;
          justify-content: space-between;
          font-size: var(--font-size-xs);
        }

        .stat .good {
          color: var(--color-success);
        }

        .stat .poor {
          color: var(--color-error);
        }

        .stat .pass {
          color: var(--color-success);
          font-weight: var(--font-weight-medium);
        }

        .stat .fail {
          color: var(--color-error);
          font-weight: var(--font-weight-medium);
        }

        .pairs-grid {
          display: grid;
          grid-template-columns: repeat(5, 1fr);
          gap: var(--spacing-xs);
        }

        .accessible-pair {
          width: 32px;
          height: 24px;
          border-radius: var(--radius-sm);
          cursor: pointer;
          font-size: var(--font-size-xs);
          font-weight: var(--font-weight-bold);
          transition: transform var(--transition-fast);
        }

        .accessible-pair:hover {
          transform: scale(1.05);
        }
      `}</style>
    </div>
  )
}

// Helper functions
function isValidColor(color: string): boolean {
  // Hex colors
  if (/^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6}|[A-Fa-f0-9]{8})$/.test(color)) {
    return true
  }
  
  // RGB/RGBA
  if (/^rgba?\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*(,\s*[\d.]+)?\s*\)$/i.test(color)) {
    return true
  }
  
  // HSL/HSLA
  if (/^hsla?\(\s*\d+\s*,\s*\d+%\s*,\s*\d+%\s*(,\s*[\d.]+)?\s*\)$/i.test(color)) {
    return true
  }
  
  return false
}

function hexToHsl(hex: string): { h: number; s: number; l: number } {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  if (!result) return { h: 0, s: 0, l: 0 }
  
  let r = parseInt(result[1], 16) / 255
  let g = parseInt(result[2], 16) / 255
  let b = parseInt(result[3], 16) / 255
  
  const max = Math.max(r, g, b)
  const min = Math.min(r, g, b)
  const diff = max - min
  const sum = max + min
  const l = sum / 2
  
  let h = 0
  let s = 0
  
  if (diff !== 0) {
    s = l > 0.5 ? diff / (2 - sum) : diff / sum
    
    switch (max) {
      case r:
        h = ((g - b) / diff) + (g < b ? 6 : 0)
        break
      case g:
        h = (b - r) / diff + 2
        break
      case b:
        h = (r - g) / diff + 4
        break
    }
    h /= 6
  }
  
  return {
    h: Math.round(h * 360),
    s: Math.round(s * 100),
    l: Math.round(l * 100)
  }
}

function hslToHex(h: number, s: number, l: number): string {
  h = h / 360
  s = s / 100
  l = l / 100
  
  const hue2rgb = (p: number, q: number, t: number): number => {
    if (t < 0) t += 1
    if (t > 1) t -= 1
    if (t < 1/6) return p + (q - p) * 6 * t
    if (t < 1/2) return q
    if (t < 2/3) return p + (q - p) * (2/3 - t) * 6
    return p
  }
  
  let r, g, b
  
  if (s === 0) {
    r = g = b = l
  } else {
    const q = l < 0.5 ? l * (1 + s) : l + s - l * s
    const p = 2 * l - q
    r = hue2rgb(p, q, h + 1/3)
    g = hue2rgb(p, q, h)
    b = hue2rgb(p, q, h - 1/3)
  }
  
  const toHex = (c: number): string => {
    const hex = Math.round(c * 255).toString(16)
    return hex.length === 1 ? '0' + hex : hex
  }
  
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`
}

function hexToRgb(hex: string): string {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  if (!result) return hex
  
  const r = parseInt(result[1], 16)
  const g = parseInt(result[2], 16)
  const b = parseInt(result[3], 16)
  
  return `rgb(${r}, ${g}, ${b})`
}

function hexToHslString(hex: string): string {
  const hsl = hexToHsl(hex)
  return `hsl(${hsl.h}, ${hsl.s}%, ${hsl.l}%)`
}

function getLuminance(hex: string): number {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  if (!result) return 0
  
  const [r, g, b] = [
    parseInt(result[1], 16) / 255,
    parseInt(result[2], 16) / 255,
    parseInt(result[3], 16) / 255
  ].map(c => c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4))
  
  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}