interface HealthStatus {
  status: 'healthy' | 'unhealthy' | 'degraded'
  message: string
  timestamp: Date
  services: {
    server: boolean
    mcp: boolean
    agents: boolean
    database: boolean
  }
  performance: {
    responseTime: number
    uptime: number
    memoryUsage: number
  }
}

class ServerHealthService {
  private baseUrl: string
  private healthCheckInterval: ReturnType<typeof setInterval> | null = null
  private isMonitoring = false

  constructor() {
    this.baseUrl = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8181'
  }

  async checkHealth(): Promise<HealthStatus> {
    try {
      const startTime = Date.now()
      
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: AbortSignal.timeout(5000), // 5 second timeout
      })

      const responseTime = Date.now() - startTime

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      
      return {
        status: data.status || 'healthy',
        message: data.message || 'All services operational',
        timestamp: new Date(),
        services: {
          server: data.services?.server || true,
          mcp: data.services?.mcp || true,
          agents: data.services?.agents || true,
          database: data.services?.database || true,
        },
        performance: {
          responseTime,
          uptime: data.uptime || 0,
          memoryUsage: data.memory_usage || 0,
        },
      }
    } catch (error) {
      console.error('Health check failed:', error)
      
      return {
        status: 'unhealthy',
        message: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date(),
        services: {
          server: false,
          mcp: false,
          agents: false,
          database: false,
        },
        performance: {
          responseTime: 0,
          uptime: 0,
          memoryUsage: 0,
        },
      }
    }
  }

  startMonitoring(callback?: (status: HealthStatus) => void, interval: number = 30000) {
    if (this.isMonitoring) {
      this.stopMonitoring()
    }

    this.isMonitoring = true

    const performHealthCheck = async () => {
      try {
        const status = await this.checkHealth()
        callback?.(status)
      } catch (error) {
        console.error('Health monitoring error:', error)
      }
    }

    // Perform initial check
    performHealthCheck()

    // Set up interval
    this.healthCheckInterval = setInterval(performHealthCheck, interval)
  }

  stopMonitoring() {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval)
      this.healthCheckInterval = null
    }
    this.isMonitoring = false
  }

  async getServerInfo() {
    try {
      const response = await fetch(`${this.baseUrl}/info`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to get server info:', error)
      throw error
    }
  }

  async ping(): Promise<number> {
    const startTime = Date.now()
    
    try {
      await fetch(`${this.baseUrl}/ping`, {
        method: 'GET',
        signal: AbortSignal.timeout(3000),
      })
      
      return Date.now() - startTime
    } catch (error) {
      throw new Error('Server unreachable')
    }
  }

  isConnected(): boolean {
    return this.isMonitoring
  }
}

export const serverHealthService = new ServerHealthService()
