import React from 'react'
import { motion } from 'framer-motion'
import { Rocket } from 'lucide-react'

export const OnboardingPage: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8"
    >
      <div className="space-y-2">
        <h1 className="text-3xl font-bold gradient-text">Welcome to DataMinerAI</h1>
        <p className="text-muted-foreground">
          Let's get you started with your AI-powered data mining journey
        </p>
      </div>

      <div className="card p-8 text-center">
        <Rocket className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
        <h3 className="text-xl font-semibold mb-2">Onboarding Coming Soon</h3>
        <p className="text-muted-foreground">
          Interactive setup wizard to configure your data mining environment
        </p>
      </div>
    </motion.div>
  )
}
