import React from 'react'
import { motion } from 'framer-motion'
import { FolderOpen } from 'lucide-react'

export const ProjectsPage: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8"
    >
      <div className="space-y-2">
        <h1 className="text-3xl font-bold gradient-text">Projects</h1>
        <p className="text-muted-foreground">
          Manage your data mining projects and workflows
        </p>
      </div>

      <div className="card p-8 text-center">
        <FolderOpen className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
        <h3 className="text-xl font-semibold mb-2">Projects Coming Soon</h3>
        <p className="text-muted-foreground">
          Advanced project management with AI-assisted task creation and workflow automation
        </p>
      </div>
    </motion.div>
  )
}
