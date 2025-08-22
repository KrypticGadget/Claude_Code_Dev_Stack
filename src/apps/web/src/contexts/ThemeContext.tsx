// Theme Context - Comprehensive Theme Management System
// Provides runtime theme switching, user preferences, and accessibility support

import React, { createContext, useContext, useEffect, useState, useCallback, useRef } from 'react'
import { ThemeContext as IThemeContext, ThemeConfig, UserThemePreferences, AccessibilityOptions, BUILT_IN_THEMES } from '../types/theme'
import { builtInThemes } from '../themes/built-in'
import { ThemeStorage } from '../utils/theme-storage'
import { ThemeValidator } from '../utils/theme-validator'
import { AccessibilityManager } from '../utils/accessibility-manager'

interface ThemeProviderProps {
  children: React.ReactNode
  defaultTheme?: string
  storageKey?: string
  enableSystemPreference?: boolean
  enableAutoSwitch?: boolean
}

const ThemeContext = createContext<IThemeContext | undefined>(undefined)

const DEFAULT_USER_PREFERENCES: UserThemePreferences = {
  currentTheme: BUILT_IN_THEMES.TOKYO_NIGHT,
  autoSwitchMode: 'system',
  lightTheme: BUILT_IN_THEMES.GITHUB_LIGHT,
  darkTheme: BUILT_IN_THEMES.TOKYO_NIGHT,
  customThemes: [],
  accessibility: {
    highContrast: false,
    reducedMotion: false,
    largeText: false,
    colorBlindMode: 'none',
    focusVisible: true,
    screenReaderOptimized: false
  },
  syncAcrossDevices: false
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({
  children,
  defaultTheme = BUILT_IN_THEMES.TOKYO_NIGHT,
  storageKey = 'claude-code-theme',
  enableSystemPreference = true,
  enableAutoSwitch = true
}) => {
  const [availableThemes, setAvailableThemes] = useState<ThemeConfig[]>(builtInThemes)
  const [userPreferences, setUserPreferences] = useState<UserThemePreferences>(DEFAULT_USER_PREFERENCES)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string>()
  
  const themeStorage = useRef(new ThemeStorage(storageKey))
  const themeValidator = useRef(new ThemeValidator())
  const accessibilityManager = useRef(new AccessibilityManager())
  
  // Current theme computed from preferences
  const currentTheme = availableThemes.find(theme => theme.id === userPreferences.currentTheme) || builtInThemes[0]

  // Load themes and preferences on mount
  useEffect(() => {
    loadThemes()
  }, [])

  // System theme preference listener
  useEffect(() => {
    if (!enableSystemPreference || userPreferences.autoSwitchMode !== 'system') return

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handleSystemThemeChange = (e: MediaQueryListEvent) => {
      const newTheme = e.matches ? userPreferences.darkTheme : userPreferences.lightTheme
      setUserPreferences(prev => ({ ...prev, currentTheme: newTheme }))
    }

    mediaQuery.addEventListener('change', handleSystemThemeChange)
    
    // Set initial theme based on system preference
    const isDark = mediaQuery.matches
    const initialTheme = isDark ? userPreferences.darkTheme : userPreferences.lightTheme
    if (initialTheme !== userPreferences.currentTheme) {
      setUserPreferences(prev => ({ ...prev, currentTheme: initialTheme }))
    }

    return () => mediaQuery.removeEventListener('change', handleSystemThemeChange)
  }, [enableSystemPreference, userPreferences.autoSwitchMode, userPreferences.lightTheme, userPreferences.darkTheme])

  // Time-based theme switching
  useEffect(() => {
    if (!enableAutoSwitch || userPreferences.autoSwitchMode !== 'time') return
    if (!userPreferences.scheduleStart || !userPreferences.scheduleEnd) return

    const checkTimeBasedTheme = () => {
      const now = new Date()
      const currentTime = now.getHours() * 60 + now.getMinutes()
      
      const [startHour, startMin] = userPreferences.scheduleStart!.split(':').map(Number)
      const [endHour, endMin] = userPreferences.scheduleEnd!.split(':').map(Number)
      
      const startTime = startHour * 60 + startMin
      const endTime = endHour * 60 + endMin
      
      let isDarkTime = false
      if (startTime < endTime) {
        // Same day schedule (e.g., 22:00 to 06:00 next day)
        isDarkTime = currentTime >= startTime || currentTime < endTime
      } else {
        // Cross-day schedule (e.g., 22:00 to 06:00)
        isDarkTime = currentTime >= startTime && currentTime < endTime
      }
      
      const newTheme = isDarkTime ? userPreferences.darkTheme : userPreferences.lightTheme
      if (newTheme !== userPreferences.currentTheme) {
        setUserPreferences(prev => ({ ...prev, currentTheme: newTheme }))
      }
    }

    // Check immediately and then every minute
    checkTimeBasedTheme()
    const interval = setInterval(checkTimeBasedTheme, 60000)

    return () => clearInterval(interval)
  }, [enableAutoSwitch, userPreferences.autoSwitchMode, userPreferences.scheduleStart, userPreferences.scheduleEnd, userPreferences.lightTheme, userPreferences.darkTheme])

  // Apply theme to document
  useEffect(() => {
    applyThemeToDocument(currentTheme)
    applyAccessibilitySettings(userPreferences.accessibility)
  }, [currentTheme, userPreferences.accessibility])

  // Auto-save preferences
  useEffect(() => {
    if (!isLoading) {
      saveThemes()
    }
  }, [userPreferences, availableThemes, isLoading])

  const loadThemes = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(undefined)

      // Load user preferences
      const savedPreferences = await themeStorage.current.loadUserPreferences()
      if (savedPreferences) {
        setUserPreferences(savedPreferences)
      }

      // Load custom themes
      const customThemes = await themeStorage.current.loadCustomThemes()
      const validCustomThemes = customThemes.filter(theme => 
        themeValidator.current.validateTheme(theme).isValid
      )

      setAvailableThemes([...builtInThemes, ...validCustomThemes])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load themes')
      console.error('Theme loading error:', err)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const saveThemes = useCallback(async () => {
    try {
      await themeStorage.current.saveUserPreferences(userPreferences)
      
      const customThemes = availableThemes.filter(theme => 
        !builtInThemes.some(builtIn => builtIn.id === theme.id)
      )
      await themeStorage.current.saveCustomThemes(customThemes)
    } catch (err) {
      console.error('Theme saving error:', err)
    }
  }, [userPreferences, availableThemes])

  const setTheme = useCallback((themeId: string) => {
    const theme = availableThemes.find(t => t.id === themeId)
    if (!theme) {
      console.warn(`Theme with id "${themeId}" not found`)
      return
    }

    setUserPreferences(prev => ({
      ...prev,
      currentTheme: themeId,
      autoSwitchMode: 'manual' // Switch to manual mode when user explicitly changes theme
    }))
  }, [availableThemes])

  const toggleTheme = useCallback(() => {
    const currentType = currentTheme.type
    const oppositeType = currentType === 'dark' ? 'light' : 'dark'
    const themesOfOppositeType = availableThemes.filter(theme => theme.type === oppositeType)
    
    if (themesOfOppositeType.length > 0) {
      // Use preferred theme for the opposite type
      const preferredTheme = oppositeType === 'dark' ? userPreferences.darkTheme : userPreferences.lightTheme
      const themeToUse = availableThemes.find(t => t.id === preferredTheme) || themesOfOppositeType[0]
      setTheme(themeToUse.id)
    }
  }, [currentTheme, availableThemes, userPreferences.darkTheme, userPreferences.lightTheme, setTheme])

  const createCustomTheme = useCallback(async (themeData: Partial<ThemeConfig>): Promise<ThemeConfig> => {
    try {
      const baseTheme = currentTheme
      const newTheme: ThemeConfig = {
        ...baseTheme,
        ...themeData,
        id: themeData.id || `custom-${Date.now()}`,
        name: themeData.name || `custom-${Date.now()}`,
        displayName: themeData.displayName || 'Custom Theme',
        author: 'User',
        version: '1.0.0',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }

      const validation = themeValidator.current.validateTheme(newTheme)
      if (!validation.isValid) {
        throw new Error(`Invalid theme: ${validation.errors.join(', ')}`)
      }

      setAvailableThemes(prev => [...prev, newTheme])
      setUserPreferences(prev => ({
        ...prev,
        customThemes: [...prev.customThemes, newTheme.id]
      }))

      return newTheme
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create custom theme'
      setError(message)
      throw err
    }
  }, [currentTheme])

  const updateCustomTheme = useCallback(async (themeId: string, updates: Partial<ThemeConfig>): Promise<ThemeConfig> => {
    try {
      const themeIndex = availableThemes.findIndex(t => t.id === themeId)
      if (themeIndex === -1) {
        throw new Error(`Theme with id "${themeId}" not found`)
      }

      const theme = availableThemes[themeIndex]
      if (builtInThemes.some(builtIn => builtIn.id === themeId)) {
        throw new Error('Cannot modify built-in themes')
      }

      const updatedTheme: ThemeConfig = {
        ...theme,
        ...updates,
        id: themeId, // Prevent ID changes
        updatedAt: new Date().toISOString()
      }

      const validation = themeValidator.current.validateTheme(updatedTheme)
      if (!validation.isValid) {
        throw new Error(`Invalid theme: ${validation.errors.join(', ')}`)
      }

      const newThemes = [...availableThemes]
      newThemes[themeIndex] = updatedTheme
      setAvailableThemes(newThemes)

      return updatedTheme
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to update custom theme'
      setError(message)
      throw err
    }
  }, [availableThemes])

  const deleteCustomTheme = useCallback(async (themeId: string): Promise<void> => {
    try {
      if (builtInThemes.some(builtIn => builtIn.id === themeId)) {
        throw new Error('Cannot delete built-in themes')
      }

      setAvailableThemes(prev => prev.filter(t => t.id !== themeId))
      setUserPreferences(prev => ({
        ...prev,
        customThemes: prev.customThemes.filter(id => id !== themeId),
        currentTheme: prev.currentTheme === themeId ? BUILT_IN_THEMES.TOKYO_NIGHT : prev.currentTheme
      }))
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete custom theme'
      setError(message)
      throw err
    }
  }, [])

  const importTheme = useCallback(async (themeData: string | ThemeConfig): Promise<ThemeConfig> => {
    try {
      let theme: ThemeConfig
      
      if (typeof themeData === 'string') {
        const parsed = JSON.parse(themeData)
        theme = parsed.theme || parsed // Handle both exported format and direct theme
      } else {
        theme = themeData
      }

      // Ensure unique ID
      const existingIds = availableThemes.map(t => t.id)
      if (existingIds.includes(theme.id)) {
        theme.id = `${theme.id}-imported-${Date.now()}`
        theme.name = `${theme.name}-imported`
        theme.displayName = `${theme.displayName} (Imported)`
      }

      theme.createdAt = new Date().toISOString()
      theme.updatedAt = new Date().toISOString()

      const validation = themeValidator.current.validateTheme(theme)
      if (!validation.isValid) {
        throw new Error(`Invalid theme: ${validation.errors.join(', ')}`)
      }

      setAvailableThemes(prev => [...prev, theme])
      setUserPreferences(prev => ({
        ...prev,
        customThemes: [...prev.customThemes, theme.id]
      }))

      return theme
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to import theme'
      setError(message)
      throw err
    }
  }, [availableThemes])

  const exportTheme = useCallback(async (themeId: string): Promise<string> => {
    try {
      const theme = availableThemes.find(t => t.id === themeId)
      if (!theme) {
        throw new Error(`Theme with id "${themeId}" not found`)
      }

      const exportData = {
        version: '1.0.0',
        theme,
        exportedAt: new Date().toISOString(),
        exportedBy: 'Claude Code Theme System'
      }

      return JSON.stringify(exportData, null, 2)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to export theme'
      setError(message)
      throw err
    }
  }, [availableThemes])

  const updateUserPreferences = useCallback((preferences: Partial<UserThemePreferences>) => {
    setUserPreferences(prev => ({ ...prev, ...preferences }))
  }, [])

  const resetToDefaults = useCallback(() => {
    setUserPreferences(DEFAULT_USER_PREFERENCES)
    setAvailableThemes(builtInThemes)
  }, [])

  const applyAccessibilityMode = useCallback((mode: Partial<AccessibilityOptions>) => {
    const newAccessibility = { ...userPreferences.accessibility, ...mode }
    setUserPreferences(prev => ({ ...prev, accessibility: newAccessibility }))
  }, [userPreferences.accessibility])

  // Apply theme to document root
  const applyThemeToDocument = useCallback((theme: ThemeConfig) => {
    const root = document.documentElement
    
    // Apply color palette
    Object.entries(theme.colors).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`, value)
    })

    // Apply typography
    Object.entries(theme.typography.fontSize).forEach(([key, value]) => {
      root.style.setProperty(`--font-size-${key}`, value)
    })
    
    Object.entries(theme.typography.fontWeight).forEach(([key, value]) => {
      root.style.setProperty(`--font-weight-${key}`, value.toString())
    })
    
    Object.entries(theme.typography.lineHeight).forEach(([key, value]) => {
      root.style.setProperty(`--line-height-${key}`, value.toString())
    })

    root.style.setProperty('--font-family-primary', theme.typography.fontFamily)
    root.style.setProperty('--font-family-mono', theme.typography.fontFamilyMono)
    root.style.setProperty('--font-family-serif', theme.typography.fontFamilySerif)

    // Apply spacing
    Object.entries(theme.spacing).forEach(([key, value]) => {
      root.style.setProperty(`--spacing-${key}`, value)
    })

    // Apply border radius
    Object.entries(theme.borderRadius).forEach(([key, value]) => {
      root.style.setProperty(`--radius-${key}`, value)
    })

    // Apply shadows
    Object.entries(theme.shadows).forEach(([key, value]) => {
      root.style.setProperty(`--shadow-${key}`, value)
    })

    // Apply transitions
    Object.entries(theme.transitions).forEach(([key, value]) => {
      root.style.setProperty(`--transition-${key}`, value)
    })

    // Apply custom properties
    if (theme.custom) {
      Object.entries(theme.custom).forEach(([key, value]) => {
        root.style.setProperty(`--custom-${key}`, value)
      })
    }

    // Set theme type
    root.setAttribute('data-theme', theme.type)
    root.setAttribute('data-theme-id', theme.id)

    // Update meta theme-color for PWA
    const metaThemeColor = document.querySelector('meta[name="theme-color"]')
    if (metaThemeColor) {
      metaThemeColor.setAttribute('content', theme.colors.primary)
    }
  }, [])

  // Apply accessibility settings
  const applyAccessibilitySettings = useCallback((accessibility: AccessibilityOptions) => {
    accessibilityManager.current.applySettings(accessibility)
  }, [])

  const contextValue: IThemeContext = {
    currentTheme,
    availableThemes,
    userPreferences,
    isLoading,
    error,
    setTheme,
    toggleTheme,
    createCustomTheme,
    updateCustomTheme,
    deleteCustomTheme,
    importTheme,
    exportTheme,
    updateUserPreferences,
    resetToDefaults,
    loadThemes,
    saveThemes,
    applyAccessibilityMode
  }

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = (): IThemeContext => {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

export { ThemeContext }