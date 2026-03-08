import React from 'react'
import { motion } from 'framer-motion'
import { BarChart3 } from 'lucide-react'

export const AnalyticsPage: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8"
    >
      <div className="space-y-2">
        <h1 className="text-3xl font-bold gradient-text">Analytics</h1>
        <p className="text-muted-foreground">
          Advanced analytics and data visualization
        </p>
      </div>

      <div className="card p-8 text-center">
        <BarChart3 className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
        <h3 className="text-xl font-semibold mb-2">Analytics Coming Soon</h3>
        <p className="text-muted-foreground">
          Real-time analytics with 3D visualizations and predictive insights
        </p>
      </div>
    </motion.div>
  )
}
