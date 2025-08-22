// Theme Storage - Persistent Theme Management
// Handles localStorage, IndexedDB, and cloud sync for themes

import { ThemeConfig, UserThemePreferences, ThemeExport } from '../types/theme'

export class ThemeStorage {
  private storageKey: string
  private customThemesKey: string
  private preferencesKey: string

  constructor(baseKey: string = 'claude-code-theme') {
    this.storageKey = baseKey
    this.customThemesKey = `${baseKey}-custom-themes`
    this.preferencesKey = `${baseKey}-preferences`
  }

  // User Preferences Storage
  async saveUserPreferences(preferences: UserThemePreferences): Promise<void> {
    try {
      const data = JSON.stringify(preferences)
      localStorage.setItem(this.preferencesKey, data)
      
      // Also save to IndexedDB for larger storage and offline sync
      await this.saveToIndexedDB('user-preferences', preferences)
    } catch (error) {
      console.error('Failed to save user preferences:', error)
      throw new Error('Failed to save user preferences')
    }
  }

  async loadUserPreferences(): Promise<UserThemePreferences | null> {
    try {
      // Try localStorage first (faster)
      const localData = localStorage.getItem(this.preferencesKey)
      if (localData) {
        return JSON.parse(localData)
      }

      // Fallback to IndexedDB
      const idbData = await this.loadFromIndexedDB<UserThemePreferences>('user-preferences')
      if (idbData) {
        // Sync back to localStorage
        localStorage.setItem(this.preferencesKey, JSON.stringify(idbData))
        return idbData
      }

      return null
    } catch (error) {
      console.error('Failed to load user preferences:', error)
      return null
    }
  }

  // Custom Themes Storage
  async saveCustomThemes(themes: ThemeConfig[]): Promise<void> {
    try {
      const data = JSON.stringify(themes)
      localStorage.setItem(this.customThemesKey, data)
      
      // Save each theme individually to IndexedDB for better management
      for (const theme of themes) {
        await this.saveToIndexedDB(`custom-theme-${theme.id}`, theme)
      }
    } catch (error) {
      console.error('Failed to save custom themes:', error)
      throw new Error('Failed to save custom themes')
    }
  }

  async loadCustomThemes(): Promise<ThemeConfig[]> {
    try {
      // Try localStorage first
      const localData = localStorage.getItem(this.customThemesKey)
      if (localData) {
        const themes = JSON.parse(localData)
        return Array.isArray(themes) ? themes : []
      }

      // Fallback to IndexedDB - load all custom themes
      const themes = await this.loadAllCustomThemesFromIndexedDB()
      if (themes.length > 0) {
        // Sync back to localStorage
        localStorage.setItem(this.customThemesKey, JSON.stringify(themes))
      }

      return themes
    } catch (error) {
      console.error('Failed to load custom themes:', error)
      return []
    }
  }

  async saveCustomTheme(theme: ThemeConfig): Promise<void> {
    try {
      const existingThemes = await this.loadCustomThemes()
      const index = existingThemes.findIndex(t => t.id === theme.id)
      
      if (index >= 0) {
        existingThemes[index] = theme
      } else {
        existingThemes.push(theme)
      }

      await this.saveCustomThemes(existingThemes)
    } catch (error) {
      console.error('Failed to save custom theme:', error)
      throw new Error('Failed to save custom theme')
    }
  }

  async deleteCustomTheme(themeId: string): Promise<void> {
    try {
      const existingThemes = await this.loadCustomThemes()
      const filteredThemes = existingThemes.filter(t => t.id !== themeId)
      
      await this.saveCustomThemes(filteredThemes)
      
      // Remove from IndexedDB
      await this.deleteFromIndexedDB(`custom-theme-${themeId}`)
    } catch (error) {
      console.error('Failed to delete custom theme:', error)
      throw new Error('Failed to delete custom theme')
    }
  }

  // Theme Import/Export
  async exportTheme(theme: ThemeConfig): Promise<string> {
    const exportData: ThemeExport = {
      version: '1.0.0',
      theme,
      exportedAt: new Date().toISOString(),
      exportedBy: 'Claude Code Theme System'
    }

    return JSON.stringify(exportData, null, 2)
  }

  async exportAllCustomThemes(): Promise<string> {
    const themes = await this.loadCustomThemes()
    const exportData = {
      version: '1.0.0',
      themes,
      exportedAt: new Date().toISOString(),
      exportedBy: 'Claude Code Theme System'
    }

    return JSON.stringify(exportData, null, 2)
  }

  async importTheme(data: string): Promise<ThemeConfig> {
    try {
      const parsed = JSON.parse(data)
      
      // Handle different export formats
      let theme: ThemeConfig
      if (parsed.theme) {
        // Single theme export
        theme = parsed.theme
      } else if (parsed.themes && Array.isArray(parsed.themes)) {
        // Multiple themes export - take first one
        if (parsed.themes.length === 0) {
          throw new Error('No themes found in import data')
        }
        theme = parsed.themes[0]
      } else {
        // Direct theme object
        theme = parsed
      }

      // Validate theme structure
      if (!theme.id || !theme.name || !theme.colors || !theme.type) {
        throw new Error('Invalid theme format')
      }

      // Ensure unique ID
      const existingThemes = await this.loadCustomThemes()
      let uniqueId = theme.id
      let counter = 1
      while (existingThemes.some(t => t.id === uniqueId)) {
        uniqueId = `${theme.id}-${counter}`
        counter++
      }

      if (uniqueId !== theme.id) {
        theme.id = uniqueId
        theme.name = `${theme.name}-${counter - 1}`
        theme.displayName = `${theme.displayName} (${counter - 1})`
      }

      // Update timestamps
      theme.createdAt = new Date().toISOString()
      theme.updatedAt = new Date().toISOString()

      await this.saveCustomTheme(theme)
      return theme
    } catch (error) {
      console.error('Failed to import theme:', error)
      throw new Error(`Failed to import theme: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  // IndexedDB Operations
  private async saveToIndexedDB(key: string, data: any): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('ClaudeCodeThemes', 1)
      
      request.onerror = () => reject(request.error)
      
      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result
        if (!db.objectStoreNames.contains('themes')) {
          db.createObjectStore('themes', { keyPath: 'key' })
        }
      }
      
      request.onsuccess = () => {
        const db = request.result
        const transaction = db.transaction(['themes'], 'readwrite')
        const store = transaction.objectStore('themes')
        
        store.put({ key, data, timestamp: Date.now() })
        
        transaction.oncomplete = () => {
          db.close()
          resolve()
        }
        
        transaction.onerror = () => {
          db.close()
          reject(transaction.error)
        }
      }
    })
  }

  private async loadFromIndexedDB<T>(key: string): Promise<T | null> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('ClaudeCodeThemes', 1)
      
      request.onerror = () => resolve(null) // Don't reject on error, just return null
      
      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result
        if (!db.objectStoreNames.contains('themes')) {
          db.createObjectStore('themes', { keyPath: 'key' })
        }
      }
      
      request.onsuccess = () => {
        const db = request.result
        const transaction = db.transaction(['themes'], 'readonly')
        const store = transaction.objectStore('themes')
        const getRequest = store.get(key)
        
        getRequest.onsuccess = () => {
          db.close()
          resolve(getRequest.result?.data || null)
        }
        
        getRequest.onerror = () => {
          db.close()
          resolve(null)
        }
      }
    })
  }

  private async loadAllCustomThemesFromIndexedDB(): Promise<ThemeConfig[]> {
    return new Promise((resolve) => {
      const request = indexedDB.open('ClaudeCodeThemes', 1)
      
      request.onerror = () => resolve([])
      
      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result
        if (!db.objectStoreNames.contains('themes')) {
          db.createObjectStore('themes', { keyPath: 'key' })
        }
      }
      
      request.onsuccess = () => {
        const db = request.result
        const transaction = db.transaction(['themes'], 'readonly')
        const store = transaction.objectStore('themes')
        const getAllRequest = store.getAll()
        
        getAllRequest.onsuccess = () => {
          db.close()
          const allData = getAllRequest.result || []
          const customThemes = allData
            .filter(item => item.key.startsWith('custom-theme-'))
            .map(item => item.data)
            .filter(theme => theme && typeof theme === 'object')
          
          resolve(customThemes)
        }
        
        getAllRequest.onerror = () => {
          db.close()
          resolve([])
        }
      }
    })
  }

  private async deleteFromIndexedDB(key: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('ClaudeCodeThemes', 1)
      
      request.onerror = () => resolve() // Don't reject on error
      
      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result
        if (!db.objectStoreNames.contains('themes')) {
          db.createObjectStore('themes', { keyPath: 'key' })
        }
      }
      
      request.onsuccess = () => {
        const db = request.result
        const transaction = db.transaction(['themes'], 'readwrite')
        const store = transaction.objectStore('themes')
        
        store.delete(key)
        
        transaction.oncomplete = () => {
          db.close()
          resolve()
        }
        
        transaction.onerror = () => {
          db.close()
          resolve()
        }
      }
    })
  }

  // Cloud Sync (placeholder for future implementation)
  async syncToCloud(): Promise<void> {
    // TODO: Implement cloud sync functionality
    console.log('Cloud sync not yet implemented')
  }

  async syncFromCloud(): Promise<void> {
    // TODO: Implement cloud sync functionality
    console.log('Cloud sync not yet implemented')
  }

  // Cleanup and maintenance
  async clearAllData(): Promise<void> {
    try {
      localStorage.removeItem(this.preferencesKey)
      localStorage.removeItem(this.customThemesKey)
      
      // Clear IndexedDB
      const deleteRequest = indexedDB.deleteDatabase('ClaudeCodeThemes')
      await new Promise<void>((resolve, reject) => {
        deleteRequest.onsuccess = () => resolve()
        deleteRequest.onerror = () => reject(deleteRequest.error)
      })
    } catch (error) {
      console.error('Failed to clear theme data:', error)
      throw new Error('Failed to clear theme data')
    }
  }

  async getStorageInfo(): Promise<{
    preferences: boolean
    customThemes: number
    totalSize: number
  }> {
    const preferences = await this.loadUserPreferences()
    const customThemes = await this.loadCustomThemes()
    
    const preferencesData = localStorage.getItem(this.preferencesKey) || ''
    const themesData = localStorage.getItem(this.customThemesKey) || ''
    const totalSize = new Blob([preferencesData + themesData]).size

    return {
      preferences: !!preferences,
      customThemes: customThemes.length,
      totalSize
    }
  }
}