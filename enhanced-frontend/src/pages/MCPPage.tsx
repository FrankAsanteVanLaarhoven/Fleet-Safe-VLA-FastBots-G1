import React from 'react'
import { motion } from 'framer-motion'
import { Brain } from 'lucide-react'

export const MCPPage: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8"
    >
      <div className="space-y-2">
        <h1 className="text-3xl font-bold gradient-text">MCP Server</h1>
        <p className="text-muted-foreground">
          Model Context Protocol server management
        </p>
      </div>

      <div className="card p-8 text-center">
        <Brain className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
        <h3 className="text-xl font-semibold mb-2">MCP Server Coming Soon</h3>
        <p className="text-muted-foreground">
          Advanced MCP server with custom tools for data mining operations
        </p>
      </div>
    </motion.div>
  )
}
