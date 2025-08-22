// Accessibility Manager - Enhanced Accessibility Features
// Manages accessibility settings, color blindness support, and motion preferences

import { AccessibilityOptions } from '../types/theme'

export class AccessibilityManager {
  private mediaQueries: Map<string, MediaQueryList> = new Map()
  private listeners: Map<string, (e: MediaQueryListEvent) => void> = new Map()

  constructor() {
    this.initializeMediaQueries()
  }

  private initializeMediaQueries(): void {
    // Prefers reduced motion
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)')
    this.mediaQueries.set('reducedMotion', reducedMotion)

    // Prefers high contrast
    const highContrast = window.matchMedia('(prefers-contrast: high)')
    this.mediaQueries.set('highContrast', highContrast)

    // Prefers color scheme
    const darkMode = window.matchMedia('(prefers-color-scheme: dark)')
    this.mediaQueries.set('colorScheme', darkMode)

    // Display mode (for detecting large text/zoom)
    const coarsePointer = window.matchMedia('(pointer: coarse)')
    this.mediaQueries.set('coarsePointer', coarsePointer)
  }

  applySettings(options: AccessibilityOptions): void {
    this.applyHighContrast(options.highContrast)
    this.applyReducedMotion(options.reducedMotion)
    this.applyLargeText(options.largeText)
    this.applyColorBlindMode(options.colorBlindMode)
    this.applyFocusVisible(options.focusVisible)
    this.applyScreenReaderOptimizations(options.screenReaderOptimized)
  }

  private applyHighContrast(enabled: boolean): void {
    const root = document.documentElement
    
    if (enabled) {
      root.classList.add('accessibility-high-contrast')
      root.style.setProperty('--accessibility-high-contrast', '1')
      
      // Force high contrast colors
      root.style.setProperty('--color-background', '#000000')
      root.style.setProperty('--color-background-secondary', '#1a1a1a')
      root.style.setProperty('--color-text-primary', '#ffffff')
      root.style.setProperty('--color-text-secondary', '#e6e6e6')
      root.style.setProperty('--color-border', '#ffffff')
      root.style.setProperty('--color-primary', '#00d4ff')
      root.style.setProperty('--color-success', '#00ff00')
      root.style.setProperty('--color-warning', '#ffaa00')
      root.style.setProperty('--color-error', '#ff0000')
    } else {
      root.classList.remove('accessibility-high-contrast')
      root.style.removeProperty('--accessibility-high-contrast')
    }
  }

  private applyReducedMotion(enabled: boolean): void {
    const root = document.documentElement
    
    if (enabled) {
      root.classList.add('accessibility-reduced-motion')
      root.style.setProperty('--accessibility-reduced-motion', '1')
      
      // Override all animations and transitions
      const style = document.createElement('style')
      style.id = 'accessibility-reduced-motion-styles'
      style.textContent = `
        .accessibility-reduced-motion *,
        .accessibility-reduced-motion *::before,
        .accessibility-reduced-motion *::after {
          animation-duration: 0.01ms !important;
          animation-iteration-count: 1 !important;
          transition-duration: 0.01ms !important;
          scroll-behavior: auto !important;
        }
        
        .accessibility-reduced-motion .loading::after {
          animation: none !important;
        }
        
        .accessibility-reduced-motion [data-animate] {
          animation: none !important;
          transition: none !important;
        }
      `
      
      const existingStyle = document.getElementById('accessibility-reduced-motion-styles')
      if (existingStyle) {
        existingStyle.remove()
      }
      document.head.appendChild(style)
    } else {
      root.classList.remove('accessibility-reduced-motion')
      root.style.removeProperty('--accessibility-reduced-motion')
      
      const existingStyle = document.getElementById('accessibility-reduced-motion-styles')
      if (existingStyle) {
        existingStyle.remove()
      }
    }
  }

  private applyLargeText(enabled: boolean): void {
    const root = document.documentElement
    
    if (enabled) {
      root.classList.add('accessibility-large-text')
      root.style.setProperty('--accessibility-large-text', '1')
      
      // Increase font sizes
      root.style.setProperty('--font-size-scale', '1.25')
      root.style.setProperty('--line-height-scale', '1.2')
      root.style.setProperty('--spacing-scale', '1.15')
      
      // Ensure minimum touch targets
      const style = document.createElement('style')
      style.id = 'accessibility-large-text-styles'
      style.textContent = `
        .accessibility-large-text button,
        .accessibility-large-text .btn,
        .accessibility-large-text input,
        .accessibility-large-text select,
        .accessibility-large-text textarea,
        .accessibility-large-text [role="button"],
        .accessibility-large-text [tabindex] {
          min-height: 44px !important;
          min-width: 44px !important;
          font-size: calc(var(--font-size-base) * var(--font-size-scale, 1.25)) !important;
          line-height: calc(var(--line-height-normal) * var(--line-height-scale, 1.2)) !important;
        }
        
        .accessibility-large-text p,
        .accessibility-large-text span,
        .accessibility-large-text div {
          font-size: calc(var(--font-size-base) * var(--font-size-scale, 1.25)) !important;
          line-height: calc(var(--line-height-normal) * var(--line-height-scale, 1.2)) !important;
        }
      `
      
      const existingStyle = document.getElementById('accessibility-large-text-styles')
      if (existingStyle) {
        existingStyle.remove()
      }
      document.head.appendChild(style)
    } else {
      root.classList.remove('accessibility-large-text')
      root.style.removeProperty('--accessibility-large-text')
      root.style.removeProperty('--font-size-scale')
      root.style.removeProperty('--line-height-scale')
      root.style.removeProperty('--spacing-scale')
      
      const existingStyle = document.getElementById('accessibility-large-text-styles')
      if (existingStyle) {
        existingStyle.remove()
      }
    }
  }

  private applyColorBlindMode(mode: AccessibilityOptions['colorBlindMode']): void {
    const root = document.documentElement
    
    // Remove existing color blind classes
    root.classList.remove(
      'accessibility-protanopia',
      'accessibility-deuteranopia',
      'accessibility-tritanopia'
    )
    
    if (mode !== 'none') {
      root.classList.add(`accessibility-${mode}`)
      root.style.setProperty('--accessibility-color-blind-mode', mode)
      
      // Apply color blind friendly palette
      this.applyColorBlindPalette(mode)
    } else {
      root.style.removeProperty('--accessibility-color-blind-mode')
    }
  }

  private applyColorBlindPalette(mode: AccessibilityOptions['colorBlindMode']): void {
    if (mode === 'none') return
    
    const root = document.documentElement
    
    // Color blind friendly palettes
    const palettes = {
      protanopia: {
        // Red-blind friendly colors
        '--color-success': '#0173b2', // Blue instead of green
        '--color-error': '#de8f05',   // Orange instead of red
        '--color-warning': '#029e73', // Teal
        '--color-info': '#cc78bc',    // Pink
        '--color-primary': '#0173b2',
        '--color-secondary': '#029e73'
      },
      deuteranopia: {
        // Green-blind friendly colors
        '--color-success': '#0173b2', // Blue
        '--color-error': '#d55e00',   // Vermillion
        '--color-warning': '#f0e442', // Yellow
        '--color-info': '#cc78bc',    // Pink
        '--color-primary': '#0173b2',
        '--color-secondary': '#d55e00'
      },
      tritanopia: {
        // Blue-blind friendly colors
        '--color-success': '#009e73', // Green
        '--color-error': '#d55e00',   // Vermillion
        '--color-warning': '#f0e442', // Yellow
        '--color-info': '#cc78bc',    // Pink
        '--color-primary': '#009e73',
        '--color-secondary': '#d55e00'
      }
    }
    
    const palette = palettes[mode]
    if (palette) {
      Object.entries(palette).forEach(([property, value]) => {
        root.style.setProperty(property, value)
      })
    }
  }

  private applyFocusVisible(enabled: boolean): void {
    const root = document.documentElement
    
    if (enabled) {
      root.classList.add('accessibility-focus-visible')
      
      const style = document.createElement('style')
      style.id = 'accessibility-focus-visible-styles'
      style.textContent = `
        .accessibility-focus-visible *:focus {
          outline: 3px solid var(--color-primary) !important;
          outline-offset: 2px !important;
          border-radius: var(--radius-sm) !important;
        }
        
        .accessibility-focus-visible button:focus,
        .accessibility-focus-visible .btn:focus {
          box-shadow: 0 0 0 3px var(--color-primary) !important;
        }
        
        .accessibility-focus-visible input:focus,
        .accessibility-focus-visible textarea:focus,
        .accessibility-focus-visible select:focus {
          border-color: var(--color-primary) !important;
          box-shadow: 0 0 0 2px var(--color-primary) !important;
        }
      `
      
      const existingStyle = document.getElementById('accessibility-focus-visible-styles')
      if (existingStyle) {
        existingStyle.remove()
      }
      document.head.appendChild(style)
    } else {
      root.classList.remove('accessibility-focus-visible')
      
      const existingStyle = document.getElementById('accessibility-focus-visible-styles')
      if (existingStyle) {
        existingStyle.remove()
      }
    }
  }

  private applyScreenReaderOptimizations(enabled: boolean): void {
    const root = document.documentElement
    
    if (enabled) {
      root.classList.add('accessibility-screen-reader')
      root.style.setProperty('--accessibility-screen-reader', '1')
      
      // Add screen reader specific styles
      const style = document.createElement('style')
      style.id = 'accessibility-screen-reader-styles'
      style.textContent = `
        .accessibility-screen-reader .sr-only {
          position: absolute !important;
          width: 1px !important;
          height: 1px !important;
          padding: 0 !important;
          margin: -1px !important;
          overflow: hidden !important;
          clip: rect(0, 0, 0, 0) !important;
          white-space: nowrap !important;
          border: 0 !important;
        }
        
        .accessibility-screen-reader .sr-only:focus {
          position: static !important;
          width: auto !important;
          height: auto !important;
          padding: var(--spacing-sm) !important;
          margin: 0 !important;
          overflow: visible !important;
          clip: auto !important;
          white-space: normal !important;
          background: var(--color-background) !important;
          color: var(--color-text-primary) !important;
          border: 2px solid var(--color-primary) !important;
          border-radius: var(--radius-md) !important;
        }
        
        /* Ensure all interactive elements have proper ARIA labels */
        .accessibility-screen-reader button:not([aria-label]):not([aria-labelledby]):empty::before {
          content: "Unlabeled button";
          speak: always;
        }
      `
      
      const existingStyle = document.getElementById('accessibility-screen-reader-styles')
      if (existingStyle) {
        existingStyle.remove()
      }
      document.head.appendChild(style)
      
      // Add skip links if they don't exist
      this.addSkipLinks()
    } else {
      root.classList.remove('accessibility-screen-reader')
      root.style.removeProperty('--accessibility-screen-reader')
      
      const existingStyle = document.getElementById('accessibility-screen-reader-styles')
      if (existingStyle) {
        existingStyle.remove()
      }
    }
  }

  private addSkipLinks(): void {
    const existingSkipLinks = document.getElementById('accessibility-skip-links')
    if (existingSkipLinks) return
    
    const skipLinks = document.createElement('div')
    skipLinks.id = 'accessibility-skip-links'
    skipLinks.innerHTML = `
      <a href="#main-content" class="sr-only">Skip to main content</a>
      <a href="#navigation" class="sr-only">Skip to navigation</a>
      <a href="#footer" class="sr-only">Skip to footer</a>
    `
    
    document.body.insertBefore(skipLinks, document.body.firstChild)
  }

  // System preference detection
  getSystemPreferences(): Partial<AccessibilityOptions> {
    const preferences: Partial<AccessibilityOptions> = {}
    
    if (this.mediaQueries.get('reducedMotion')?.matches) {
      preferences.reducedMotion = true
    }
    
    if (this.mediaQueries.get('highContrast')?.matches) {
      preferences.highContrast = true
    }
    
    return preferences
  }

  // Listen for system preference changes
  onSystemPreferenceChange(callback: (preferences: Partial<AccessibilityOptions>) => void): () => void {
    const listeners: (() => void)[] = []
    
    // Reduced motion listener
    const reducedMotionListener = () => {
      callback({ reducedMotion: this.mediaQueries.get('reducedMotion')?.matches })
    }
    this.mediaQueries.get('reducedMotion')?.addEventListener('change', reducedMotionListener)
    listeners.push(() => 
      this.mediaQueries.get('reducedMotion')?.removeEventListener('change', reducedMotionListener)
    )
    
    // High contrast listener
    const highContrastListener = () => {
      callback({ highContrast: this.mediaQueries.get('highContrast')?.matches })
    }
    this.mediaQueries.get('highContrast')?.addEventListener('change', highContrastListener)
    listeners.push(() => 
      this.mediaQueries.get('highContrast')?.removeEventListener('change', highContrastListener)
    )
    
    // Return cleanup function
    return () => {
      listeners.forEach(cleanup => cleanup())
    }
  }

  // Announce to screen readers
  announce(message: string, priority: 'polite' | 'assertive' = 'polite'): void {
    const announcer = document.createElement('div')
    announcer.setAttribute('aria-live', priority)
    announcer.setAttribute('aria-atomic', 'true')
    announcer.classList.add('sr-only')
    announcer.textContent = message
    
    document.body.appendChild(announcer)
    
    // Remove after announcement
    setTimeout(() => {
      document.body.removeChild(announcer)
    }, 1000)
  }

  // Check if user is using assistive technology
  isUsingAssistiveTechnology(): boolean {
    // Detection heuristics
    return (
      'speechSynthesis' in window ||
      navigator.userAgent.includes('NVDA') ||
      navigator.userAgent.includes('JAWS') ||
      navigator.userAgent.includes('VoiceOver') ||
      window.navigator.maxTouchPoints > 0 && window.matchMedia('(pointer: coarse)').matches
    )
  }

  // Cleanup
  destroy(): void {
    // Remove all event listeners
    this.listeners.forEach((listener, key) => {
      const mediaQuery = this.mediaQueries.get(key)
      if (mediaQuery && listener) {
        mediaQuery.removeEventListener('change', listener)
      }
    })
    
    this.listeners.clear()
    this.mediaQueries.clear()
    
    // Remove accessibility styles
    const styleIds = [
      'accessibility-reduced-motion-styles',
      'accessibility-large-text-styles',
      'accessibility-focus-visible-styles',
      'accessibility-screen-reader-styles'
    ]
    
    styleIds.forEach(id => {
      const style = document.getElementById(id)
      if (style) {
        style.remove()
      }
    })
  }
}