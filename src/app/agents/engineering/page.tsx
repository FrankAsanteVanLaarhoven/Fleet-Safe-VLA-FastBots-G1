'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Code, 
  Bug, 
  TestTube, 
  FileText, 
  Zap, 
  Monitor,
  Play,
  Settings,
  BarChart3,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

const engineeringAgents = [
  {
    id: 'code-review',
    name: 'Code Review Assistant',
    icon: Code,
    description: 'Automated PR reviews and code quality analysis',
    color: 'from-blue-500 to-cyan-500',
    features: [
      'Automated code review suggestions',
      'Security vulnerability detection',
      'Performance optimization recommendations',
      'Best practices enforcement',
      'Code style consistency checks'
    ],
    status: 'active',
    usage: 85,
    responseTime: '2.3s'
  },
  {
    id: 'qa-engineer',
    name: 'QA Engineer',
    icon: TestTube,
    description: 'Automated testing and debugging',
    color: 'from-green-500 to-emerald-500',
    features: [
      'Automated test case generation',
      'Regression testing automation',
      'Bug detection and reporting',
      'Test coverage analysis',
      'Performance testing'
    ],
    status: 'active',
    usage: 92,
    responseTime: '1.8s'
  },
  {
    id: 'devops-monitor',
    name: 'DevOps Monitor',
    icon: Monitor,
    description: 'Infrastructure monitoring and alerts',
    color: 'from-purple-500 to-pink-500',
    features: [
      'Real-time infrastructure monitoring',
      'Automated alerting system',
      'Performance metrics tracking',
      'Resource optimization',
      'Deployment automation'
    ],
    status: 'active',
    usage: 78,
    responseTime: '0.5s'
  },
  {
    id: 'documentation-generator',
    name: 'Documentation Generator',
    icon: FileText,
    description: 'Auto-generate technical documentation',
    color: 'from-orange-500 to-red-500',
    features: [
      'API documentation generation',
      'Code comment analysis',
      'README file creation',
      'Technical specification docs',
      'Change log automation'
    ],
    status: 'active',
    usage: 65,
    responseTime: '3.1s'
  },
  {
    id: 'bug-tracker',
    name: 'Bug Tracker',
    icon: Bug,
    description: 'Intelligent bug detection and resolution',
    color: 'from-red-500 to-pink-500',
    features: [
      'Automated bug detection',
      'Issue classification and prioritization',
      'Root cause analysis',
      'Fix suggestion generation',
      'Bug trend analysis'
    ],
    status: 'active',
    usage: 88,
    responseTime: '1.2s'
  },
  {
    id: 'performance-optimizer',
    name: 'Performance Optimizer',
    icon: Zap,
    description: 'Code and system performance analysis',
    color: 'from-yellow-500 to-orange-500',
    features: [
      'Performance bottleneck detection',
      'Optimization recommendations',
      'Memory usage analysis',
      'CPU profiling',
      'Database query optimization'
    ],
    status: 'active',
    usage: 71,
    responseTime: '4.2s'
  }
];

export default function EngineeringAgents() {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState<string | null>(null);

  const handleRunAgent = async (agentId: string) => {
    setIsRunning(agentId);
    // Simulate agent execution
    setTimeout(() => {
      setIsRunning(null);
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
          <div className="text-center">
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center justify-center mb-4"
            >
              <div className="w-16 h-16 rounded-xl bg-gradient-to-r from-blue-500 to-cyan-500 flex items-center justify-center mr-4">
                <Code className="w-8 h-8 text-white" />
              </div>
              <h1 className="text-4xl md:text-6xl font-bold text-white">
                Engineering Agents
              </h1>
            </motion.div>
            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="text-xl text-zinc-300/90 mb-8 max-w-2xl mx-auto"
            >
              Automate code review, testing, documentation, and performance optimization with our intelligent engineering agents
            </motion.p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
          
          {/* Stats Overview */}
          <section className="mb-12">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="grid grid-cols-2 md:grid-cols-4 gap-6"
            >
              <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
                <div className="text-3xl font-bold text-white mb-2">6</div>
                <div className="text-zinc-400 text-sm">Active Agents</div>
              </div>
              <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
                <div className="text-3xl font-bold text-white mb-2">79.8%</div>
                <div className="text-zinc-400 text-sm">Avg Usage</div>
              </div>
              <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
                <div className="text-3xl font-bold text-white mb-2">2.2s</div>
                <div className="text-zinc-400 text-sm">Avg Response</div>
              </div>
              <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
                <div className="text-3xl font-bold text-white mb-2">100%</div>
                <div className="text-zinc-400 text-sm">Uptime</div>
              </div>
            </motion.div>
          </section>

          {/* Agents Grid */}
          <section>
            <motion.h2 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="text-3xl font-bold text-white mb-8 text-center"
            >
              Available Agents
            </motion.h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {engineeringAgents.map((agent, index) => (
                <motion.div
                  key={agent.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 * index }}
                  className="group"
                >
                  <div className="relative overflow-hidden rounded-2xl bg-white/5 backdrop-blur-sm border border-white/10 p-6 hover:bg-white/10 transition-all duration-300">
                    {/* Glow Effect */}
                    <div className={`absolute inset-0 bg-gradient-to-r ${agent.color} opacity-0 group-hover:opacity-10 transition-opacity duration-300`} />
                    
                    {/* Header */}
                    <div className="relative z-10 flex items-start justify-between mb-4">
                      <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${agent.color} flex items-center justify-center`}>
                        <agent.icon className="w-6 h-6 text-white" />
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className={`w-2 h-2 rounded-full ${agent.status === 'active' ? 'bg-green-400' : 'bg-red-400'}`} />
                        <span className="text-xs text-zinc-400 capitalize">{agent.status}</span>
                      </div>
                    </div>
                    
                    {/* Content */}
                    <div className="relative z-10">
                      <h3 className="text-xl font-bold text-white mb-2">{agent.name}</h3>
                      <p className="text-zinc-400 text-sm mb-4">{agent.description}</p>
                      
                      {/* Features */}
                      <div className="mb-4">
                        <h4 className="text-sm font-semibold text-white mb-2">Features:</h4>
                        <ul className="space-y-1">
                          {agent.features.slice(0, 3).map((feature, idx) => (
                            <li key={idx} className="text-xs text-zinc-400 flex items-center">
                              <CheckCircle className="w-3 h-3 text-green-400 mr-2 flex-shrink-0" />
                              {feature}
                            </li>
                          ))}
                          {agent.features.length > 3 && (
                            <li className="text-xs text-zinc-500">
                              +{agent.features.length - 3} more features
                            </li>
                          )}
                        </ul>
                      </div>
                      
                      {/* Metrics */}
                      <div className="grid grid-cols-2 gap-4 mb-4">
                        <div>
                          <div className="text-sm text-zinc-400">Usage</div>
                          <div className="text-lg font-bold text-white">{agent.usage}%</div>
                        </div>
                        <div>
                          <div className="text-sm text-zinc-400">Response</div>
                          <div className="text-lg font-bold text-white">{agent.responseTime}</div>
                        </div>
                      </div>
                      
                      {/* Actions */}
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleRunAgent(agent.id)}
                          disabled={isRunning === agent.id}
                          className="flex-1 bg-gradient-to-r from-blue-500 to-purple-500 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:from-blue-600 hover:to-purple-600 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {isRunning === agent.id ? (
                            <div className="flex items-center justify-center">
                              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                              Running...
                            </div>
                          ) : (
                            <div className="flex items-center justify-center">
                              <Play className="w-4 h-4 mr-2" />
                              Run Agent
                            </div>
                          )}
                        </button>
                        <button
                          onClick={() => setSelectedAgent(selectedAgent === agent.id ? null : agent.id)}
                          className="px-4 py-2 bg-white/10 text-white rounded-lg text-sm font-semibold hover:bg-white/20 transition-all duration-300"
                        >
                          <Settings className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </section>

          {/* Quick Actions */}
          <section className="mt-16">
            <motion.h2 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6 }}
              className="text-3xl font-bold text-white mb-8 text-center"
            >
              Quick Actions
            </motion.h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.7 }}
              >
                <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-blue-500/20 to-purple-500/20 backdrop-blur-sm border border-blue-500/30 p-6">
                  <h3 className="text-xl font-bold text-white mb-2">Run All Tests</h3>
                  <p className="text-zinc-300 mb-4">Execute comprehensive testing across all agents</p>
                  <button className="bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-blue-600 transition-all duration-300">
                    Execute Tests
                  </button>
                </div>
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 }}
              >
                <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-green-500/20 to-emerald-500/20 backdrop-blur-sm border border-green-500/30 p-6">
                  <h3 className="text-xl font-bold text-white mb-2">Performance Review</h3>
                  <p className="text-zinc-300 mb-4">Analyze performance metrics and optimization opportunities</p>
                  <button className="bg-green-500 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-green-600 transition-all duration-300">
                    Analyze Performance
                  </button>
                </div>
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.9 }}
              >
                <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-orange-500/20 to-red-500/20 backdrop-blur-sm border border-orange-500/30 p-6">
                  <h3 className="text-xl font-bold text-white mb-2">Generate Reports</h3>
                  <p className="text-zinc-300 mb-4">Create comprehensive engineering reports and documentation</p>
                  <button className="bg-orange-500 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-orange-600 transition-all duration-300">
                    Generate Reports
                  </button>
                </div>
              </motion.div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
