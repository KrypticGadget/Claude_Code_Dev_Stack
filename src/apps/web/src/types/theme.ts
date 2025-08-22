// Theme System Types - Comprehensive Runtime Theme Switching
// Supports custom themes, accessibility, and cross-component integration

export interface ColorPalette {
  // Primary Colors
  primary: string
  primaryLight: string
  primaryDark: string
  secondary: string
  secondaryLight: string
  secondaryDark: string
  
  // Accent Colors
  accent: string
  accentLight: string
  accentDark: string
  
  // Background Colors
  background: string
  backgroundSecondary: string
  backgroundTertiary: string
  backgroundElevated: string
  
  // Text Colors
  textPrimary: string
  textSecondary: string
  textMuted: string
  textInverse: string
  
  // State Colors
  success: string
  successLight: string
  successDark: string
  warning: string
  warningLight: string
  warningDark: string
  error: string
  errorLight: string
  errorDark: string
  info: string
  infoLight: string
  infoDark: string
  
  // Border Colors
  border: string
  borderLight: string
  borderStrong: string
  
  // Surface Colors
  surface: string
  surfaceSecondary: string
  surfaceTertiary: string
  
  // Shadow Colors
  shadow: string
  shadowLight: string
  shadowStrong: string
}

export interface Typography {
  // Font Families
  fontFamily: string
  fontFamilyMono: string
  fontFamilySerif: string
  
  // Font Sizes
  fontSize: {
    xs: string
    sm: string
    base: string
    lg: string
    xl: string
    '2xl': string
    '3xl': string
    '4xl': string
    '5xl': string
    '6xl': string
  }
  
  // Font Weights
  fontWeight: {
    thin: number
    light: number
    normal: number
    medium: number
    semibold: number
    bold: number
    extrabold: number
    black: number
  }
  
  // Line Heights
  lineHeight: {
    none: number
    tight: number
    snug: number
    normal: number
    relaxed: number
    loose: number
  }
  
  // Letter Spacing
  letterSpacing: {
    tighter: string
    tight: string
    normal: string
    wide: string
    wider: string
    widest: string
  }
}

export interface Spacing {
  xs: string
  sm: string
  md: string
  lg: string
  xl: string
  '2xl': string
  '3xl': string
  '4xl': string
  '5xl': string
  '6xl': string
}

export interface BorderRadius {
  none: string
  sm: string
  md: string
  lg: string
  xl: string
  '2xl': string
  '3xl': string
  full: string
}

export interface Shadows {
  none: string
  sm: string
  md: string
  lg: string
  xl: string
  '2xl': string
  inner: string
}

export interface Transitions {
  none: string
  fast: string
  normal: string
  slow: string
  slower: string
}

export interface Breakpoints {
  sm: string
  md: string
  lg: string
  xl: string
  '2xl': string
}

export interface ZIndex {
  auto: string
  behind: number
  normal: number
  tooltip: number
  modal: number
  dropdown: number
  sticky: number
  fixed: number
  overlay: number
  max: number
}

export interface MonacoTheme {
  base: 'vs' | 'vs-dark' | 'hc-black' | 'hc-light'
  inherit: boolean
  rules: Array<{
    token: string
    foreground?: string
    background?: string
    fontStyle?: 'italic' | 'bold' | 'underline' | ''
  }>
  colors: {
    'editor.background': string
    'editor.foreground': string
    'editor.lineHighlightBackground': string
    'editor.selectionBackground': string
    'editor.selectionHighlightBackground': string
    'editor.inactiveSelectionBackground': string
    'editor.findMatchBackground': string
    'editor.findMatchHighlightBackground': string
    'editor.hoverHighlightBackground': string
    'editor.wordHighlightBackground': string
    'editor.wordHighlightStrongBackground': string
    'editorCursor.foreground': string
    'editorLineNumber.foreground': string
    'editorLineNumber.activeForeground': string
    'editorIndentGuide.background': string
    'editorIndentGuide.activeBackground': string
    'editorWhitespace.foreground': string
    'editorGutter.background': string
    'editorGutter.modifiedBackground': string
    'editorGutter.addedBackground': string
    'editorGutter.deletedBackground': string
    'editorError.foreground': string
    'editorWarning.foreground': string
    'editorInfo.foreground': string
    'editorHint.foreground': string
    'scrollbar.shadow': string
    'scrollbarSlider.background': string
    'scrollbarSlider.hoverBackground': string
    'scrollbarSlider.activeBackground': string
    'minimap.background': string
    'minimapGutter.addedBackground': string
    'minimapGutter.modifiedBackground': string
    'minimapGutter.deletedBackground': string
    'panel.background': string
    'panel.border': string
    'panelTitle.activeForeground': string
    'panelTitle.inactiveForeground': string
    'terminal.background': string
    'terminal.foreground': string
    'terminal.ansiBlack': string
    'terminal.ansiRed': string
    'terminal.ansiGreen': string
    'terminal.ansiYellow': string
    'terminal.ansiBlue': string
    'terminal.ansiMagenta': string
    'terminal.ansiCyan': string
    'terminal.ansiWhite': string
    'terminal.ansiBrightBlack': string
    'terminal.ansiBrightRed': string
    'terminal.ansiBrightGreen': string
    'terminal.ansiBrightYellow': string
    'terminal.ansiBrightBlue': string
    'terminal.ansiBrightMagenta': string
    'terminal.ansiBrightCyan': string
    'terminal.ansiBrightWhite': string
  }
}

export interface TerminalTheme {
  background: string
  foreground: string
  cursor: string
  cursorAccent: string
  selection: string
  black: string
  red: string
  green: string
  yellow: string
  blue: string
  magenta: string
  cyan: string
  white: string
  brightBlack: string
  brightRed: string
  brightGreen: string
  brightYellow: string
  brightBlue: string
  brightMagenta: string
  brightCyan: string
  brightWhite: string
}

export interface AccessibilityOptions {
  highContrast: boolean
  reducedMotion: boolean
  largeText: boolean
  colorBlindMode: 'none' | 'protanopia' | 'deuteranopia' | 'tritanopia'
  focusVisible: boolean
  screenReaderOptimized: boolean
}

export interface ThemeConfig {
  id: string
  name: string
  displayName: string
  description?: string
  author?: string
  version?: string
  type: 'light' | 'dark'
  
  // Core Theme Properties
  colors: ColorPalette
  typography: Typography
  spacing: Spacing
  borderRadius: BorderRadius
  shadows: Shadows
  transitions: Transitions
  breakpoints: Breakpoints
  zIndex: ZIndex
  
  // Editor & Terminal Themes
  monaco: MonacoTheme
  terminal: TerminalTheme
  
  // Accessibility
  accessibility: AccessibilityOptions
  
  // Custom Properties
  custom?: Record<string, string>
  
  // Preview Image
  preview?: string
  
  // Theme Metadata
  tags?: string[]
  createdAt?: string
  updatedAt?: string
}

export interface UserThemePreferences {
  currentTheme: string
  autoSwitchMode: 'system' | 'time' | 'manual'
  lightTheme: string
  darkTheme: string
  scheduleStart?: string // Time for dark mode
  scheduleEnd?: string   // Time for light mode
  customThemes: string[] // IDs of user-created themes
  accessibility: AccessibilityOptions
  syncAcrossDevices: boolean
}

export interface ThemeContextState {
  currentTheme: ThemeConfig
  availableThemes: ThemeConfig[]
  userPreferences: UserThemePreferences
  isLoading: boolean
  error?: string
}

export interface ThemeContextActions {
  setTheme: (themeId: string) => void
  toggleTheme: () => void
  createCustomTheme: (theme: Partial<ThemeConfig>) => Promise<ThemeConfig>
  updateCustomTheme: (themeId: string, updates: Partial<ThemeConfig>) => Promise<ThemeConfig>
  deleteCustomTheme: (themeId: string) => Promise<void>
  importTheme: (themeData: string | ThemeConfig) => Promise<ThemeConfig>
  exportTheme: (themeId: string) => Promise<string>
  updateUserPreferences: (preferences: Partial<UserThemePreferences>) => void
  resetToDefaults: () => void
  loadThemes: () => Promise<void>
  saveThemes: () => Promise<void>
  applyAccessibilityMode: (mode: Partial<AccessibilityOptions>) => void
}

export type ThemeContext = ThemeContextState & ThemeContextActions

// Theme Builder Types
export interface ThemeBuilderState {
  baseTheme: ThemeConfig
  modifiedTheme: ThemeConfig
  previewMode: boolean
  activeSection: 'colors' | 'typography' | 'spacing' | 'monaco' | 'terminal' | 'accessibility'
  unsavedChanges: boolean
}

export interface ColorGroup {
  name: string
  colors: Array<{
    key: keyof ColorPalette
    label: string
    value: string
  }>
}

// Export/Import Types
export interface ThemeExport {
  version: string
  theme: ThemeConfig
  exportedAt: string
  exportedBy?: string
}

export interface ThemeImportResult {
  success: boolean
  theme?: ThemeConfig
  error?: string
  warnings?: string[]
}

// Built-in Theme IDs
export const BUILT_IN_THEMES = {
  // Dark Themes
  TOKYO_NIGHT: 'tokyo-night',
  ONE_DARK: 'one-dark',
  DRACULA: 'dracula',
  MONOKAI: 'monokai',
  CLAUDE_DARK: 'claude-dark',
  
  // Light Themes
  GITHUB_LIGHT: 'github-light',
  ONE_LIGHT: 'one-light',
  SOLARIZED_LIGHT: 'solarized-light',
  CLAUDE_LIGHT: 'claude-light',
  
  // High Contrast
  HIGH_CONTRAST_DARK: 'high-contrast-dark',
  HIGH_CONTRAST_LIGHT: 'high-contrast-light'
} as const

export type BuiltInThemeId = typeof BUILT_IN_THEMES[keyof typeof BUILT_IN_THEMES]