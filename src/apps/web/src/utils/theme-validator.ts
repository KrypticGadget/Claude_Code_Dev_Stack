// Theme Validator - Ensures Theme Integrity and Accessibility
// Validates theme configurations and provides accessibility checks

import { ThemeConfig, ColorPalette, MonacoTheme, TerminalTheme, AccessibilityOptions } from '../types/theme'

export interface ValidationResult {
  isValid: boolean
  errors: string[]
  warnings: string[]
  accessibilityIssues: string[]
}

export class ThemeValidator {
  private requiredColorKeys: (keyof ColorPalette)[] = [
    'primary', 'secondary', 'accent', 'background', 'backgroundSecondary',
    'textPrimary', 'textSecondary', 'success', 'warning', 'error', 'info'
  ]

  private requiredMonacoKeys: (keyof MonacoTheme['colors'])[] = [
    'editor.background', 'editor.foreground', 'editorCursor.foreground',
    'editorLineNumber.foreground', 'terminal.background', 'terminal.foreground'
  ]

  private requiredTerminalKeys: (keyof TerminalTheme)[] = [
    'background', 'foreground', 'cursor', 'black', 'red', 'green',
    'yellow', 'blue', 'magenta', 'cyan', 'white'
  ]

  validateTheme(theme: ThemeConfig): ValidationResult {
    const errors: string[] = []
    const warnings: string[] = []
    const accessibilityIssues: string[] = []

    // Basic structure validation
    this.validateBasicStructure(theme, errors)
    
    // Color validation
    this.validateColors(theme.colors, errors, warnings, accessibilityIssues)
    
    // Monaco theme validation
    this.validateMonacoTheme(theme.monaco, errors, warnings)
    
    // Terminal theme validation
    this.validateTerminalTheme(theme.terminal, errors, warnings)
    
    // Typography validation
    this.validateTypography(theme.typography, errors, warnings)
    
    // Accessibility validation
    this.validateAccessibility(theme, accessibilityIssues)

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      accessibilityIssues
    }
  }

  private validateBasicStructure(theme: ThemeConfig, errors: string[]): void {
    if (!theme.id || typeof theme.id !== 'string' || theme.id.trim() === '') {
      errors.push('Theme must have a valid ID')
    }

    if (!theme.name || typeof theme.name !== 'string' || theme.name.trim() === '') {
      errors.push('Theme must have a valid name')
    }

    if (!theme.displayName || typeof theme.displayName !== 'string' || theme.displayName.trim() === '') {
      errors.push('Theme must have a valid display name')
    }

    if (!theme.type || (theme.type !== 'light' && theme.type !== 'dark')) {
      errors.push('Theme type must be either "light" or "dark"')
    }

    if (!theme.colors || typeof theme.colors !== 'object') {
      errors.push('Theme must have a colors object')
    }

    if (!theme.monaco || typeof theme.monaco !== 'object') {
      errors.push('Theme must have a monaco object')
    }

    if (!theme.terminal || typeof theme.terminal !== 'object') {
      errors.push('Theme must have a terminal object')
    }

    if (!theme.typography || typeof theme.typography !== 'object') {
      errors.push('Theme must have a typography object')
    }
  }

  private validateColors(colors: ColorPalette, errors: string[], warnings: string[], accessibilityIssues: string[]): void {
    // Check required color keys
    for (const key of this.requiredColorKeys) {
      if (!colors[key]) {
        errors.push(`Missing required color: ${key}`)
      } else if (!this.isValidColor(colors[key])) {
        errors.push(`Invalid color format for ${key}: ${colors[key]}`)
      }
    }

    // Contrast validation
    this.validateColorContrasts(colors, accessibilityIssues)
    
    // Color harmony validation
    this.validateColorHarmony(colors, warnings)
  }

  private validateMonacoTheme(monaco: MonacoTheme, errors: string[], warnings: string[]): void {
    if (!monaco.base || !['vs', 'vs-dark', 'hc-black', 'hc-light'].includes(monaco.base)) {
      errors.push('Monaco theme must have a valid base theme')
    }

    if (!monaco.colors || typeof monaco.colors !== 'object') {
      errors.push('Monaco theme must have colors object')
      return
    }

    // Check required Monaco color keys
    for (const key of this.requiredMonacoKeys) {
      if (!monaco.colors[key]) {
        errors.push(`Missing required Monaco color: ${key}`)
      } else if (!this.isValidColor(monaco.colors[key])) {
        errors.push(`Invalid Monaco color format for ${key}: ${monaco.colors[key]}`)
      }
    }

    if (!Array.isArray(monaco.rules)) {
      warnings.push('Monaco theme should have syntax highlighting rules')
    } else {
      this.validateMonacoRules(monaco.rules, warnings)
    }
  }

  private validateTerminalTheme(terminal: TerminalTheme, errors: string[], warnings: string[]): void {
    // Check required terminal color keys
    for (const key of this.requiredTerminalKeys) {
      if (!terminal[key]) {
        errors.push(`Missing required terminal color: ${key}`)
      } else if (!this.isValidColor(terminal[key])) {
        errors.push(`Invalid terminal color format for ${key}: ${terminal[key]}`)
      }
    }

    // Validate terminal contrast
    if (terminal.background && terminal.foreground) {
      const contrast = this.calculateContrast(terminal.background, terminal.foreground)
      if (contrast < 4.5) {
        warnings.push(`Terminal background/foreground contrast ratio (${contrast.toFixed(2)}) is below WCAG AA standard (4.5:1)`)
      }
    }
  }

  private validateTypography(typography: any, errors: string[], warnings: string[]): void {
    if (!typography.fontFamily) {
      errors.push('Typography must have fontFamily')
    }

    if (!typography.fontFamilyMono) {
      errors.push('Typography must have fontFamilyMono')
    }

    if (!typography.fontSize || typeof typography.fontSize !== 'object') {
      errors.push('Typography must have fontSize object')
    }

    if (!typography.fontWeight || typeof typography.fontWeight !== 'object') {
      errors.push('Typography must have fontWeight object')
    }

    // Validate font size scale
    if (typography.fontSize) {
      const sizes = Object.values(typography.fontSize) as string[]
      for (const size of sizes) {
        if (!this.isValidCSSUnit(size)) {
          warnings.push(`Invalid font size format: ${size}`)
        }
      }
    }
  }

  private validateAccessibility(theme: ThemeConfig, accessibilityIssues: string[]): void {
    // Text contrast validation
    this.validateTextContrasts(theme, accessibilityIssues)
    
    // Color blindness validation
    this.validateColorBlindness(theme, accessibilityIssues)
    
    // Focus indicators
    this.validateFocusIndicators(theme, accessibilityIssues)
  }

  private validateColorContrasts(colors: ColorPalette, accessibilityIssues: string[]): void {
    const textColors = [colors.textPrimary, colors.textSecondary]
    const backgrounds = [colors.background, colors.backgroundSecondary, colors.backgroundTertiary]

    for (const textColor of textColors) {
      for (const backgroundColor of backgrounds) {
        if (textColor && backgroundColor) {
          const contrast = this.calculateContrast(backgroundColor, textColor)
          if (contrast < 4.5) {
            accessibilityIssues.push(
              `Low contrast ratio (${contrast.toFixed(2)}) between text and background. WCAG AA requires 4.5:1 minimum.`
            )
          }
        }
      }
    }

    // Check state colors against backgrounds
    const stateColors = [colors.success, colors.warning, colors.error, colors.info]
    for (const stateColor of stateColors) {
      if (stateColor && colors.background) {
        const contrast = this.calculateContrast(colors.background, stateColor)
        if (contrast < 3.0) {
          accessibilityIssues.push(
            `Low contrast ratio (${contrast.toFixed(2)}) for state color. Consider increasing contrast.`
          )
        }
      }
    }
  }

  private validateTextContrasts(theme: ThemeConfig, accessibilityIssues: string[]): void {
    const { colors } = theme
    
    // Primary text on backgrounds
    const primaryContrast = this.calculateContrast(colors.background, colors.textPrimary)
    if (primaryContrast < 4.5) {
      accessibilityIssues.push(`Primary text contrast (${primaryContrast.toFixed(2)}) is below WCAG AA standard`)
    }

    // Secondary text on backgrounds
    const secondaryContrast = this.calculateContrast(colors.background, colors.textSecondary)
    if (secondaryContrast < 4.5) {
      accessibilityIssues.push(`Secondary text contrast (${secondaryContrast.toFixed(2)}) is below WCAG AA standard`)
    }

    // Links and interactive elements
    const linkContrast = this.calculateContrast(colors.background, colors.primary)
    if (linkContrast < 4.5) {
      accessibilityIssues.push(`Link/interactive element contrast (${linkContrast.toFixed(2)}) is below WCAG AA standard`)
    }
  }

  private validateColorBlindness(theme: ThemeConfig, accessibilityIssues: string[]): void {
    const { colors } = theme
    
    // Check if success/error colors are distinguishable for color blind users
    if (colors.success && colors.error) {
      const successHue = this.getHue(colors.success)
      const errorHue = this.getHue(colors.error)
      
      if (successHue !== null && errorHue !== null) {
        const hueDifference = Math.abs(successHue - errorHue)
        if (hueDifference < 60 && hueDifference > 300) { // Too similar hues
          accessibilityIssues.push('Success and error colors may be difficult to distinguish for color blind users')
        }
      }
    }

    // Check if information is conveyed through color alone
    if (colors.warning && colors.error) {
      const warningLuminance = this.getLuminance(colors.warning)
      const errorLuminance = this.getLuminance(colors.error)
      
      if (Math.abs(warningLuminance - errorLuminance) < 0.2) {
        accessibilityIssues.push('Warning and error colors have similar brightness - consider using additional visual indicators')
      }
    }
  }

  private validateFocusIndicators(theme: ThemeConfig, accessibilityIssues: string[]): void {
    const { colors } = theme
    
    // Ensure focus indicators have sufficient contrast
    if (colors.primary && colors.background) {
      const focusContrast = this.calculateContrast(colors.background, colors.primary)
      if (focusContrast < 3.0) {
        accessibilityIssues.push('Focus indicator color should have at least 3:1 contrast ratio with background')
      }
    }
  }

  private validateColorHarmony(colors: ColorPalette, warnings: string[]): void {
    // Check if primary and secondary colors work well together
    if (colors.primary && colors.secondary) {
      const primaryHue = this.getHue(colors.primary)
      const secondaryHue = this.getHue(colors.secondary)
      
      if (primaryHue !== null && secondaryHue !== null) {
        const hueDifference = Math.abs(primaryHue - secondaryHue)
        if (hueDifference < 30 && hueDifference > 0) {
          warnings.push('Primary and secondary colors are very similar - consider increasing color difference')
        }
      }
    }
  }

  private validateMonacoRules(rules: any[], warnings: string[]): void {
    const requiredTokens = ['keyword', 'string', 'comment', 'number', 'function']
    const definedTokens = rules.map(rule => rule.token)
    
    for (const token of requiredTokens) {
      if (!definedTokens.includes(token)) {
        warnings.push(`Missing syntax highlighting for ${token} tokens`)
      }
    }
  }

  private isValidColor(color: string): boolean {
    if (typeof color !== 'string') return false
    
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
    
    // Named colors (basic check)
    const namedColors = [
      'black', 'white', 'red', 'green', 'blue', 'yellow', 'cyan', 'magenta',
      'transparent', 'currentColor'
    ]
    
    return namedColors.includes(color.toLowerCase())
  }

  private isValidCSSUnit(value: string): boolean {
    return /^\d+(\.\d+)?(px|em|rem|%|vh|vw|vmin|vmax|ex|ch|cm|mm|in|pt|pc)$/.test(value)
  }

  private calculateContrast(background: string, foreground: string): number {
    const bgLuminance = this.getLuminance(background)
    const fgLuminance = this.getLuminance(foreground)
    
    const lighter = Math.max(bgLuminance, fgLuminance)
    const darker = Math.min(bgLuminance, fgLuminance)
    
    return (lighter + 0.05) / (darker + 0.05)
  }

  private getLuminance(color: string): number {
    const rgb = this.hexToRgb(color)
    if (!rgb) return 0

    const [r, g, b] = rgb.map(c => {
      const normalized = c / 255
      return normalized <= 0.03928
        ? normalized / 12.92
        : Math.pow((normalized + 0.055) / 1.055, 2.4)
    })

    return 0.2126 * r + 0.7152 * g + 0.0722 * b
  }

  private getHue(color: string): number | null {
    const rgb = this.hexToRgb(color)
    if (!rgb) return null

    const [r, g, b] = rgb.map(c => c / 255)
    const max = Math.max(r, g, b)
    const min = Math.min(r, g, b)
    const delta = max - min

    if (delta === 0) return 0

    let hue = 0
    if (max === r) {
      hue = ((g - b) / delta) % 6
    } else if (max === g) {
      hue = (b - r) / delta + 2
    } else {
      hue = (r - g) / delta + 4
    }

    return Math.round(hue * 60)
  }

  private hexToRgb(hex: string): [number, number, number] | null {
    // Remove # if present
    hex = hex.replace('#', '')
    
    // Handle 3-character hex
    if (hex.length === 3) {
      hex = hex.split('').map(char => char + char).join('')
    }
    
    if (hex.length !== 6) return null
    
    const r = parseInt(hex.substr(0, 2), 16)
    const g = parseInt(hex.substr(2, 2), 16)
    const b = parseInt(hex.substr(4, 2), 16)
    
    return [r, g, b]
  }
}