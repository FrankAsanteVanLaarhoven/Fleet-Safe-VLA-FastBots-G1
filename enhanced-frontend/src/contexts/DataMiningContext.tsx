import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { useToast } from './ToastContext'

export interface MiningTask {
  id: string
  name: string
  type: 'web_crawl' | 'document_process' | 'data_analysis' | 'report_generation'
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  progress: number
  startTime: Date
  endTime?: Date
  data?: any
  error?: string
}

export interface MiningResult {
  id: string
  taskId: string
  type: string
  data: any
  metadata: {
    source: string
    timestamp: Date
    processingTime: number
    dataSize: number
  }
}

export interface RealTimeData {
  activeTasks: number
  completedTasks: number
  failedTasks: number
  dataProcessed: number
  systemPerformance: {
    cpu: number
    memory: number
    network: number
  }
}

interface DataMiningContextType {
  // Tasks
  tasks: MiningTask[]
  activeTask: MiningTask | null
  addTask: (task: Omit<MiningTask, 'id' | 'startTime' | 'status' | 'progress'>) => void
  updateTask: (id: string, updates: Partial<MiningTask>) => void
  cancelTask: (id: string) => void
  clearCompletedTasks: () => void
  
  // Results
  results: MiningResult[]
  addResult: (result: Omit<MiningResult, 'id'>) => void
  clearResults: () => void
  
  // Real-time data
  realTimeData: RealTimeData
  updateRealTimeData: (data: Partial<RealTimeData>) => void
  
  // Operations
  startMining: (config: any) => Promise<void>
  stopMining: () => Promise<void>
  isMining: boolean
  
  // Analytics
  getAnalytics: () => Promise<any>
  exportData: (format: 'json' | 'csv' | 'excel') => Promise<void>
}

const DataMiningContext = createContext<DataMiningContextType | undefined>(undefined)

export const useDataMining = () => {
  const context = useContext(DataMiningContext)
  if (context === undefined) {
    throw new Error('useDataMining must be used within a DataMiningProvider')
  }
  return context
}

interface DataMiningProviderProps {
  children: React.ReactNode
}

export const DataMiningProvider: React.FC<DataMiningProviderProps> = ({ children }) => {
  const [tasks, setTasks] = useState<MiningTask[]>([])
  const [results, setResults] = useState<MiningResult[]>([])
  const [isMining, setIsMining] = useState(false)
  const [realTimeData, setRealTimeData] = useState<RealTimeData>({
    activeTasks: 0,
    completedTasks: 0,
    failedTasks: 0,
    dataProcessed: 0,
    systemPerformance: {
      cpu: 0,
      memory: 0,
      network: 0,
    },
  })

  const { addToast } = useToast()

  // Get active task
  const activeTask = tasks.find(task => task.status === 'running') || null

  // Add new task
  const addTask = useCallback((taskData: Omit<MiningTask, 'id' | 'startTime' | 'status' | 'progress'>) => {
    const newTask: MiningTask = {
      ...taskData,
      id: Math.random().toString(36).substr(2, 9),
      startTime: new Date(),
      status: 'pending',
      progress: 0,
    }
    
    setTasks(prev => [...prev, newTask])
    addToast({
      type: 'info',
      title: 'Task Added',
      message: `New ${taskData.type} task "${taskData.name}" has been queued.`,
    })
  }, [addToast])

  // Update task
  const updateTask = useCallback((id: string, updates: Partial<MiningTask>) => {
    setTasks(prev => prev.map(task => 
      task.id === id ? { ...task, ...updates } : task
    ))
  }, [])

  // Cancel task
  const cancelTask = useCallback((id: string) => {
    setTasks(prev => prev.map(task => 
      task.id === id ? { ...task, status: 'cancelled', endTime: new Date() } : task
    ))
    addToast({
      type: 'warning',
      title: 'Task Cancelled',
      message: 'The task has been cancelled successfully.',
    })
  }, [addToast])

  // Clear completed tasks
  const clearCompletedTasks = useCallback(() => {
    setTasks(prev => prev.filter(task => task.status === 'running' || task.status === 'pending'))
    addToast({
      type: 'success',
      title: 'Tasks Cleared',
      message: 'Completed tasks have been cleared.',
    })
  }, [addToast])

  // Add result
  const addResult = useCallback((resultData: Omit<MiningResult, 'id'>) => {
    const newResult: MiningResult = {
      ...resultData,
      id: Math.random().toString(36).substr(2, 9),
    }
    
    setResults(prev => [...prev, newResult])
  }, [])

  // Clear results
  const clearResults = useCallback(() => {
    setResults([])
    addToast({
      type: 'success',
      title: 'Results Cleared',
      message: 'All results have been cleared.',
    })
  }, [addToast])

  // Update real-time data
  const updateRealTimeData = useCallback((data: Partial<RealTimeData>) => {
    setRealTimeData(prev => ({ ...prev, ...data }))
  }, [])

  // Start mining operation
  const startMining = useCallback(async (_config: any) => {
    try {
      setIsMining(true)
      addToast({
        type: 'info',
        title: 'Mining Started',
        message: 'Data mining operation has been initiated.',
      })
      
      // Simulate mining operation
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      addToast({
        type: 'success',
        title: 'Mining Complete',
        message: 'Data mining operation completed successfully.',
      })
    } catch (error) {
      addToast({
        type: 'error',
        title: 'Mining Failed',
        message: 'Data mining operation failed. Please try again.',
      })
    } finally {
      setIsMining(false)
    }
  }, [addToast])

  // Stop mining operation
  const stopMining = useCallback(async () => {
    setIsMining(false)
    addToast({
      type: 'warning',
      title: 'Mining Stopped',
      message: 'Data mining operation has been stopped.',
    })
  }, [addToast])

  // Get analytics
  const getAnalytics = useCallback(async () => {
    // Simulate analytics data
    return {
      totalTasks: tasks.length,
      successRate: tasks.filter(t => t.status === 'completed').length / tasks.length,
      averageProcessingTime: 1500,
      dataVolume: results.reduce((sum, r) => sum + r.metadata.dataSize, 0),
    }
  }, [tasks, results])

  // Export data
  const exportData = useCallback(async (format: 'json' | 'csv' | 'excel') => {
    try {
      // Simulate export
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      addToast({
        type: 'success',
        title: 'Export Complete',
        message: `Data exported successfully in ${format.toUpperCase()} format.`,
      })
    } catch (error) {
      addToast({
        type: 'error',
        title: 'Export Failed',
        message: 'Failed to export data. Please try again.',
      })
    }
  }, [addToast])

  // Update real-time data periodically
  useEffect(() => {
    const interval = setInterval(() => {
      updateRealTimeData({
        activeTasks: tasks.filter(t => t.status === 'running').length,
        completedTasks: tasks.filter(t => t.status === 'completed').length,
        failedTasks: tasks.filter(t => t.status === 'failed').length,
        dataProcessed: results.reduce((sum, r) => sum + r.metadata.dataSize, 0),
        systemPerformance: {
          cpu: Math.random() * 100,
          memory: Math.random() * 100,
          network: Math.random() * 100,
        },
      })
    }, 5000)

    return () => clearInterval(interval)
  }, [tasks, results, updateRealTimeData])

  const value: DataMiningContextType = {
    tasks,
    activeTask,
    addTask,
    updateTask,
    cancelTask,
    clearCompletedTasks,
    results,
    addResult,
    clearResults,
    realTimeData,
    updateRealTimeData,
    startMining,
    stopMining,
    isMining,
    getAnalytics,
    exportData,
  }

  return (
    <DataMiningContext.Provider value={value}>
      {children}
    </DataMiningContext.Provider>
  )
}
