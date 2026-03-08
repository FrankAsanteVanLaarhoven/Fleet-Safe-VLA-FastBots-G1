import React from 'react'
import { motion } from 'framer-motion'
import { Database, Search, Upload, Link } from 'lucide-react'

export const KnowledgeBasePage: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8"
    >
      <div className="space-y-2">
        <h1 className="text-3xl font-bold gradient-text">Knowledge Base</h1>
        <p className="text-muted-foreground">
          Manage your data sources and knowledge repositories
        </p>
      </div>

      <div className="card p-8 text-center">
        <Database className="w-16 h-16 mx-auto mb-4 text-muted-foreground" />
        <h3 className="text-xl font-semibold mb-2">Knowledge Base Coming Soon</h3>
        <p className="text-muted-foreground mb-6">
          Advanced document processing, web crawling, and intelligent search capabilities
        </p>
        
        <div className="flex justify-center space-x-4">
          <div className="flex items-center space-x-2 text-sm text-muted-foreground">
            <Search className="w-4 h-4" />
            <span>Smart Search</span>
          </div>
          <div className="flex items-center space-x-2 text-sm text-muted-foreground">
            <Upload className="w-4 h-4" />
            <span>Document Upload</span>
          </div>
          <div className="flex items-center space-x-2 text-sm text-muted-foreground">
            <Link className="w-4 h-4" />
            <span>Web Crawling</span>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
