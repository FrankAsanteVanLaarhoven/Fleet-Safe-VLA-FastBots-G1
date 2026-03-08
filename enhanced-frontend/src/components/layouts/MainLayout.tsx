import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Menu, 
  X, 
  Home, 
  Database, 
  FolderOpen, 
  BarChart3, 
  Settings, 
  Brain
} from 'lucide-react'
import { useTheme } from '../../contexts/ThemeContext'
import { useSettings } from '../../contexts/SettingsContext'

interface MainLayoutProps {
  children: React.ReactNode
}

const navigationItems = [
  { icon: Home, label: 'Dashboard', path: '/' },
  { icon: Database, label: 'Knowledge Base', path: '/knowledge' },
  { icon: FolderOpen, label: 'Projects', path: '/projects' },
  { icon: BarChart3, label: 'Analytics', path: '/analytics' },
  { icon: Brain, label: 'MCP Server', path: '/mcp' },
  { icon: Settings, label: 'Settings', path: '/settings' },
]

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { setTheme, isDark } = useTheme()
  const { settings } = useSettings()

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen)

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Mobile sidebar overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-40 lg:hidden"
            onClick={toggleSidebar}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.aside
        initial={{ x: -300 }}
        animate={{ x: sidebarOpen ? 0 : -300 }}
        className={`
          fixed top-0 left-0 z-50 h-full w-80 bg-card border-r border-border
          transform transition-transform duration-300 ease-in-out
          lg:translate-x-0 lg:static lg:z-auto
          ${settings.sidebarCollapsed ? 'lg:w-16' : 'lg:w-80'}
        `}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-border">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center space-x-3"
            >
              <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-accent-500 rounded-lg flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              {!settings.sidebarCollapsed && (
                <span className="text-lg font-bold gradient-text">DataMinerAI</span>
              )}
            </motion.div>
            
            <button
              onClick={toggleSidebar}
              className="lg:hidden p-2 rounded-md hover:bg-accent"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2">
            {navigationItems.map((item, index) => (
              <motion.a
                key={item.path}
                href={item.path}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center space-x-3 p-3 rounded-lg hover:bg-accent transition-colors group"
              >
                <item.icon className="w-5 h-5 text-muted-foreground group-hover:text-foreground" />
                {!settings.sidebarCollapsed && (
                  <span className="text-sm font-medium">{item.label}</span>
                )}
              </motion.a>
            ))}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-border">
            <div className="flex items-center justify-between">
              {!settings.sidebarCollapsed && (
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse" />
                  <span className="text-xs text-muted-foreground">System Online</span>
                </div>
              )}
              
              <button
                onClick={() => setTheme(isDark ? 'light' : 'dark')}
                className="p-2 rounded-md hover:bg-accent"
              >
                {isDark ? '🌞' : '🌙'}
              </button>
            </div>
          </div>
        </div>
      </motion.aside>

      {/* Main content */}
      <div className={`
        transition-all duration-300 ease-in-out
        ${settings.sidebarCollapsed ? 'lg:ml-16' : 'lg:ml-80'}
      `}>
        {/* Top bar */}
        <header className="sticky top-0 z-30 bg-background/80 backdrop-blur-md border-b border-border">
          <div className="flex items-center justify-between p-4">
            <div className="flex items-center space-x-4">
              <button
                onClick={toggleSidebar}
                className="p-2 rounded-md hover:bg-accent lg:hidden"
              >
                <Menu className="w-5 h-5" />
              </button>
              
              <motion.h1
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-xl font-semibold"
              >
                DataMinerAI Platform
              </motion.h1>
            </div>

            <div className="flex items-center space-x-4">
              {/* Real-time status indicator */}
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse" />
                <span>Live</span>
              </div>

              {/* Theme toggle */}
              <button
                onClick={() => setTheme(isDark ? 'light' : 'dark')}
                className="p-2 rounded-md hover:bg-accent transition-colors"
              >
                {isDark ? '🌞' : '🌙'}
              </button>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-6">
          <AnimatePresence mode="wait">
            <motion.div
              key={window.location.pathname}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {children}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  )
}
