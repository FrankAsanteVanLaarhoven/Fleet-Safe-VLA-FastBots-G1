import React from 'react'
import { motion } from 'framer-motion'
import { 
  Brain, 
  Database, 
  Activity, 
  Zap, 
  Target,
  BarChart3,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react'
import { useDataMining } from '../contexts/DataMiningContext'
import { useStaggeredEntrance } from '../hooks/useStaggeredEntrance'

export const DashboardPage: React.FC = () => {
  const { realTimeData, tasks } = useDataMining()
  const { isVisible, containerVariants, itemVariants, titleVariants } = useStaggeredEntrance([1, 2, 3, 4], 0.1)

  const stats = [
    {
      icon: Database,
      label: 'Active Tasks',
      value: realTimeData.activeTasks,
      change: '+12%',
      color: 'text-primary-500',
      bgColor: 'bg-primary-50 dark:bg-primary-950',
    },
    {
      icon: CheckCircle,
      label: 'Completed',
      value: realTimeData.completedTasks,
      change: '+8%',
      color: 'text-success-500',
      bgColor: 'bg-success-50 dark:bg-success-950',
    },
    {
      icon: AlertCircle,
      label: 'Failed',
      value: realTimeData.failedTasks,
      change: '-3%',
      color: 'text-error-500',
      bgColor: 'bg-error-50 dark:bg-error-950',
    },
    {
      icon: BarChart3,
      label: 'Data Processed',
      value: `${(realTimeData.dataProcessed / 1024 / 1024).toFixed(1)} MB`,
      change: '+15%',
      color: 'text-accent-500',
      bgColor: 'bg-accent-50 dark:bg-accent-950',
    },
  ]

  const recentTasks = tasks.slice(-5).reverse()

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate={isVisible ? "visible" : "hidden"}
      className="space-y-8"
    >
      {/* Header */}
      <motion.div variants={titleVariants} className="space-y-2">
        <h1 className="text-3xl font-bold gradient-text">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome to your AI-powered data mining command center
        </p>
      </motion.div>

      {/* Stats Grid */}
      <motion.div 
        variants={itemVariants}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        {stats.map((stat) => (
          <motion.div
            key={stat.label}
            variants={itemVariants}
            className={`${stat.bgColor} p-6 rounded-xl border border-border/50 hover:shadow-medium transition-all duration-300 hover:-translate-y-1`}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">{stat.label}</p>
                <p className="text-2xl font-bold mt-1">{stat.value}</p>
                <p className={`text-xs font-medium mt-1 ${stat.change.startsWith('+') ? 'text-success-500' : 'text-error-500'}`}>
                  {stat.change} from last month
                </p>
              </div>
              <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                <stat.icon className={`w-6 h-6 ${stat.color}`} />
              </div>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* System Performance */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Chart */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">System Performance</h3>
            <Activity className="w-5 h-5 text-muted-foreground" />
          </div>
          
          <div className="space-y-4">
            {[
              { label: 'CPU', value: realTimeData.systemPerformance.cpu, color: 'bg-primary-500' },
              { label: 'Memory', value: realTimeData.systemPerformance.memory, color: 'bg-secondary-500' },
              { label: 'Network', value: realTimeData.systemPerformance.network, color: 'bg-accent-500' },
            ].map((metric) => (
              <div key={metric.label} className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">{metric.label}</span>
                  <span className="font-medium">{metric.value.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-muted rounded-full h-2">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${metric.value}%` }}
                    transition={{ duration: 1, ease: "easeOut" }}
                    className={`h-2 rounded-full ${metric.color}`}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Recent Activity</h3>
            <Clock className="w-5 h-5 text-muted-foreground" />
          </div>
          
          <div className="space-y-3">
            {recentTasks.length > 0 ? (
              recentTasks.map((task) => (
                <div key={task.id} className="flex items-center space-x-3 p-3 rounded-lg hover:bg-muted/50 transition-colors">
                  <div className={`w-2 h-2 rounded-full ${
                    task.status === 'completed' ? 'bg-success-500' :
                    task.status === 'running' ? 'bg-primary-500' :
                    task.status === 'failed' ? 'bg-error-500' :
                    'bg-muted-foreground'
                  }`} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{task.name}</p>
                    <p className="text-xs text-muted-foreground capitalize">{task.type.replace('_', ' ')}</p>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    task.status === 'completed' ? 'bg-success-100 text-success-700 dark:bg-success-900 dark:text-success-300' :
                    task.status === 'running' ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300' :
                    task.status === 'failed' ? 'bg-error-100 text-error-700 dark:bg-error-900 dark:text-error-300' :
                    'bg-muted text-muted-foreground'
                  }`}>
                    {task.status}
                  </span>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Database className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No recent activity</p>
                <p className="text-sm">Start a new data mining task to see activity here</p>
              </div>
            )}
          </div>
        </div>
      </motion.div>

      {/* Quick Actions */}
      <motion.div variants={itemVariants} className="card p-6">
        <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { icon: Brain, label: 'Start AI Analysis', description: 'Begin intelligent data processing', color: 'bg-primary-500' },
            { icon: Database, label: 'Crawl Website', description: 'Extract data from web sources', color: 'bg-secondary-500' },
            { icon: Target, label: 'Generate Report', description: 'Create comprehensive analytics report', color: 'bg-accent-500' },
          ].map((action) => (
            <motion.button
              key={action.label}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="p-4 rounded-lg border border-border hover:shadow-medium transition-all duration-200 text-left group"
            >
              <div className="flex items-center space-x-3">
                <div className={`p-2 rounded-lg ${action.color} text-white`}>
                  <action.icon className="w-5 h-5" />
                </div>
                <div>
                  <p className="font-medium group-hover:text-primary-600 transition-colors">{action.label}</p>
                  <p className="text-sm text-muted-foreground">{action.description}</p>
                </div>
              </div>
            </motion.button>
          ))}
        </div>
      </motion.div>

      {/* AI Insights */}
      <motion.div variants={itemVariants} className="card p-6 bg-gradient-to-r from-primary-50 to-accent-50 dark:from-primary-950 dark:to-accent-950 border-primary-200 dark:border-primary-800">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2 bg-primary-500 rounded-lg">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold">AI Insights</h3>
            <p className="text-sm text-muted-foreground">Powered by advanced machine learning</p>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <p className="text-sm font-medium">Data Quality Score</p>
            <div className="flex items-center space-x-2">
              <div className="flex-1 bg-white dark:bg-black rounded-full h-2">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: '87%' }}
                  transition={{ duration: 1, delay: 0.5 }}
                  className="h-2 bg-gradient-to-r from-success-500 to-primary-500 rounded-full"
                />
              </div>
              <span className="text-sm font-bold">87%</span>
            </div>
          </div>
          
          <div className="space-y-2">
            <p className="text-sm font-medium">Processing Efficiency</p>
            <div className="flex items-center space-x-2">
              <div className="flex-1 bg-white dark:bg-black rounded-full h-2">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: '94%' }}
                  transition={{ duration: 1, delay: 0.7 }}
                  className="h-2 bg-gradient-to-r from-accent-500 to-secondary-500 rounded-full"
                />
              </div>
              <span className="text-sm font-bold">94%</span>
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}
