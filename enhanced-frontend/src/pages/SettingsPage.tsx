import React from 'react'
import { motion } from 'framer-motion'
import { Settings } from 'lucide-react'

export const SettingsPage: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8"
    >
      <div className="space-y-2">
        <h1 className="text-3xl font-bold gradient-text">Settings</h1>
        <p className="text-muted-foreground">
          Configure your DataMinerAI platform
        </p>
      </div>

      <div className="card p-8 text-center">
        <Settings className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
        <h3 className="text-xl font-semibold mb-2">Settings Coming Soon</h3>
        <p className="text-muted-foreground">
          Advanced configuration options for AI models, data processing, and system preferences
        </p>
      </div>
    </motion.div>
  )
}
