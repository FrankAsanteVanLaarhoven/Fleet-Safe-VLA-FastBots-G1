import React, { createContext, useContext, useState, useEffect } from 'react'

interface Settings {
  // General settings
  language: string
  timezone: string
  dateFormat: string
  
  // UI settings
  sidebarCollapsed: boolean
  compactMode: boolean
  showAnimations: boolean
  autoSave: boolean
  
  // Data mining settings
  maxConcurrentTasks: number
  dataRetentionDays: number
  enableRealTimeUpdates: boolean
  enablePredictiveAnalytics: boolean
  
  // AI settings
  defaultModel: string
  enableAutoSuggestions: boolean
  enableSmartFiltering: boolean
  
  // Performance settings
  enableCaching: boolean
  cacheExpirationMinutes: number
  enableBackgroundSync: boolean
}

interface SettingsContextType {
  settings: Settings
  updateSettings: (updates: Partial<Settings>) => void
  resetSettings: () => void
  isLoading: boolean
}

const defaultSettings: Settings = {
  // General settings
  language: 'en',
  timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
  dateFormat: 'MMM dd, yyyy',
  
  // UI settings
  sidebarCollapsed: false,
  compactMode: false,
  showAnimations: true,
  autoSave: true,
  
  // Data mining settings
  maxConcurrentTasks: 5,
  dataRetentionDays: 30,
  enableRealTimeUpdates: true,
  enablePredictiveAnalytics: true,
  
  // AI settings
  defaultModel: 'gpt-4',
  enableAutoSuggestions: true,
  enableSmartFiltering: true,
  
  // Performance settings
  enableCaching: true,
  cacheExpirationMinutes: 60,
  enableBackgroundSync: true,
}

const SettingsContext = createContext<SettingsContextType | undefined>(undefined)

export const useSettings = () => {
  const context = useContext(SettingsContext)
  if (context === undefined) {
    throw new Error('useSettings must be used within a SettingsProvider')
  }
  return context
}

interface SettingsProviderProps {
  children: React.ReactNode
}

export const SettingsProvider: React.FC<SettingsProviderProps> = ({ children }) => {
  const [settings, setSettings] = useState<Settings>(defaultSettings)
  const [isLoading, setIsLoading] = useState(true)

  // Load settings from localStorage on mount
  useEffect(() => {
    const loadSettings = () => {
      try {
        const savedSettings = localStorage.getItem('dataminer-settings')
        if (savedSettings) {
          const parsedSettings = JSON.parse(savedSettings)
          setSettings(prev => ({ ...prev, ...parsedSettings }))
        }
      } catch (error) {
        console.error('Failed to load settings:', error)
      } finally {
        setIsLoading(false)
      }
    }

    loadSettings()
  }, [])

  // Save settings to localStorage whenever they change
  useEffect(() => {
    if (!isLoading) {
      try {
        localStorage.setItem('dataminer-settings', JSON.stringify(settings))
      } catch (error) {
        console.error('Failed to save settings:', error)
      }
    }
  }, [settings, isLoading])

  const updateSettings = (updates: Partial<Settings>) => {
    setSettings(prev => ({ ...prev, ...updates }))
  }

  const resetSettings = () => {
    setSettings(defaultSettings)
  }

  const value = {
    settings,
    updateSettings,
    resetSettings,
    isLoading,
  }

  return (
    <SettingsContext.Provider value={value}>
      {children}
    </SettingsContext.Provider>
  )
}
