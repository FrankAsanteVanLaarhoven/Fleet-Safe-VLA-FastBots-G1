import React, { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'

// Contexts
import { ThemeProvider } from './contexts/ThemeContext'
import { ToastProvider } from './contexts/ToastContext'
import { SettingsProvider } from './contexts/SettingsContext'
import { DataMiningProvider } from './contexts/DataMiningContext'

// Layout Components
import { MainLayout } from './components/layouts/MainLayout'
import { LoadingScreen } from './components/ui/LoadingScreen'

// Pages
import { DashboardPage } from './pages/DashboardPage'
import { KnowledgeBasePage } from './pages/KnowledgeBasePage'
import { ProjectsPage } from './pages/ProjectsPage'
import { AnalyticsPage } from './pages/AnalyticsPage'
import { MCPPage } from './pages/MCPPage'
import { SettingsPage } from './pages/SettingsPage'
import { OnboardingPage } from './pages/OnboardingPage'

// Services
import { serverHealthService } from './services/serverHealthService'

// Hooks
import { useStaggeredEntrance } from './hooks/useStaggeredEntrance'

const AppRoutes = () => {
  const { isVisible, containerVariants } = useStaggeredEntrance([1], 0.1)

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key="app-routes"
        variants={containerVariants}
        initial="hidden"
        animate={isVisible ? "visible" : "hidden"}
        exit="exit"
        className="min-h-screen"
      >
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/knowledge" element={<KnowledgeBasePage />} />
          <Route path="/projects" element={<ProjectsPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/mcp" element={<MCPPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/onboarding" element={<OnboardingPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </motion.div>
    </AnimatePresence>
  )
}

const AppContent = () => {
  const [isLoading, setIsLoading] = React.useState(true)

  useEffect(() => {
    const initializeApp = async () => {
      try {
        // Check server health
        await serverHealthService.checkHealth()
        
        // Simulate loading time for smooth UX
        await new Promise(resolve => setTimeout(resolve, 1500))
        
        setIsLoading(false)
      } catch (error) {
        console.error('Failed to initialize app:', error)
        setIsLoading(false)
      }
    }

    initializeApp()
  }, [])

  if (isLoading) {
    return <LoadingScreen />
  }

  return (
    <MainLayout>
      <AppRoutes />
    </MainLayout>
  )
}

export function App() {
  return (
    <ThemeProvider>
      <ToastProvider>
        <SettingsProvider>
          <DataMiningProvider>
            <AppContent />
          </DataMiningProvider>
        </SettingsProvider>
      </ToastProvider>
    </ThemeProvider>
  )
}
